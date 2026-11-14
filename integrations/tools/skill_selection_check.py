"""Check Skill text against a real TEI CLI, and score capability selections.

Two small read-only checks for TAI #488 (YIC-ROUTE). Neither is a dispatcher,
registry or agent runtime, and neither selects anything.

  drift   Compare what a Skill document claims (commands, `go run` form, JSON
          paths) with what the real CLI discovers and prints. Only read-only
          commands that need nothing but -workspace are run.
  score   Score recorded selection trials against an evaluator-held expected
          file. Each metric is reported on its own; there is no total.
  --self-test   Synthetic cases only. Not a Product, Harness or model test.

The expected file must not live inside this repository, so it cannot reach a
participant model. `score` refuses an in-repository path.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOLD_OUTCOMES = {"need-clarification", "unsupported", "withhold"}
METRICS = (
    "missed", "extra", "nonexistent", "wrongExecution", "unneededHold",
    "disclosure", "unsupportedEvidenceClaim", "jobNotEstablished",
)


def run_tei(tei, args, timeout=60):
    """Run the CLI. Return (exit, stdout) or (None, reason) when it cannot start."""
    cmd = list(tei) if isinstance(tei, (list, tuple)) else [str(tei)]
    try:
        p = subprocess.run(cmd + list(args), capture_output=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, type(exc).__name__
    return p.returncode, p.stdout.decode("utf-8", "replace")


def parse_json(text):
    try:
        return json.loads(text)
    except ValueError:
        return None


def resolve(doc, dotted):
    cur = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    return True


def list_has_leaves(doc, list_path, prefix, leaves):
    """True when doc[list_path] is a non-empty list whose items carry every leaf."""
    cur = doc
    for part in list_path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    if not isinstance(cur, list) or not cur:
        return False
    for item in cur:
        node = item
        for part in prefix:
            node = node.get(part) if isinstance(node, dict) else None
        if not isinstance(node, dict) or any(leaf not in node for leaf in leaves):
            return False
    return True


def discover(tei):
    code, out = run_tei(tei, ["commands"])
    doc = parse_json(out) if code == 0 else None
    if not doc or "commands" not in doc:
        return None
    return {
        "sha256": hashlib.sha256(out.encode("utf-8")).hexdigest(),
        "scope": doc.get("scope"),
        "commands": {c["name"]: c for c in doc["commands"]},
    }


def usage_count(tei):
    cmd = list(tei) if isinstance(tei, (list, tuple)) else [str(tei)]
    try:
        q = subprocess.run(cmd + ["__no_such_command__"], capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    out = (q.stdout + q.stderr).decode("utf-8", "replace")
    m = re.search(r"<([^>]+)>", out or "")
    return len(m.group(1).split("|")) if m else None


CMD_RE = re.compile(r"(?:go run \./cmd/tei|\btei)\s+([a-z][a-z-]*(?:\s+[a-z][a-z-]*)?)")
PATH_RE = re.compile(r"`([A-Za-z_][\w.]*)\[\]\.([\w.]+(?:/\w+)*)`")


def match_command(words, names):
    two = " ".join(words.split()[:2])
    one = words.split()[0]
    if two in names:
        return two
    if one in names:
        return one
    return None


def check_skill(tei, workspace, skill_texts):
    findings = []
    disc = discover(tei)
    if disc is None:
        return {"status": "tool-unavailable", "findings": [],
                "note": "discovery did not return; no claim was judged"}
    names = set(disc["commands"])
    mentioned = set()
    outputs = {}
    for label, text in skill_texts:
        if "go run ./cmd/tei" in text:
            findings.append({"class": "GAP", "code": "SKILL_USES_GO_RUN", "doc": label,
                             "detail": "documents `go run`; a real Tool Profile calls a built binary"})
        for line in text.splitlines():
            line_cmd = None
            for m in CMD_RE.finditer(line):
                cmd = match_command(m.group(1), names)
                if cmd:
                    mentioned.add(cmd)
                    line_cmd = cmd
                elif m.group(1).split()[0] == "commands":
                    continue  # the discovery entry point itself
                elif not m.group(1).startswith(("-", "<")):
                    findings.append({"class": "DRIFT", "code": "SKILL_COMMAND_NOT_DISCOVERED",
                                     "doc": label, "detail": m.group(1).split()[0]})
            for pm in PATH_RE.finditer(line):
                list_path = pm.group(1)
                parts = pm.group(2).split(".")
                prefix, leaves = parts[:-1], parts[-1].split("/")
                claim = f"{list_path}[].{pm.group(2)}"
                meta = disc["commands"].get(line_cmd or "")
                if not meta or set(meta.get("requiredFlags", [])) - {"workspace", "world"}:
                    findings.append({"class": "UNJUDGED", "code": "PATH_CLAIM_NEEDS_ARGUMENTS",
                                     "doc": label, "detail": claim})
                    continue
                if line_cmd not in outputs:
                    args = line_cmd.split() + ["-workspace", str(workspace)]
                    code, out = run_tei(tei, args)
                    outputs[line_cmd] = (code, parse_json(out))
                code, doc = outputs[line_cmd]
                if doc is None:
                    findings.append({"class": "UNJUDGED", "code": "COMMAND_OUTPUT_NOT_JSON",
                                     "doc": label, "detail": f"{line_cmd} exit={code}"})
                    continue
                literal = list_has_leaves(doc, list_path, prefix, leaves)
                actual = list_has_leaves(doc, "result." + list_path, prefix, leaves)
                if literal:
                    continue
                findings.append({
                    "class": "DRIFT" if actual else "UNJUDGED",
                    "code": "SKILL_PATH_ABSENT_AT_DOCUMENTED_LOCATION" if actual
                            else "SKILL_PATH_NOT_FOUND_ANYWHERE_CHECKED",
                    "doc": label, "command": line_cmd, "claim": claim,
                    "foundAt": ("result." + list_path + "[]") if actual else None})
    uncovered = sorted(names - mentioned)
    return {
        "status": "checked",
        "discovery": {"sha256": disc["sha256"], "scope": disc["scope"],
                      "discoveredCommands": len(names), "usageCommands": usage_count(tei)},
        "skillMentionsDiscovered": sorted(mentioned),
        "discoveredNotCoveredBySkill": len(uncovered),
        "findings": findings,
        "limits": ["Only explicit command spans and `list[].a.b/c` path claims are parsed.",
                   "A PASS here is not a Harness, Loader, Grant or model result."],
    }


def in_repo(path):
    try:
        Path(path).resolve().relative_to(REPO)
        return True
    except ValueError:
        return False


def score_trial(trial, exp):
    sel = trial.get("selected", {})
    chosen = set(sel.get("products", [])) | set(sel.get("skills", []))
    tools = set(sel.get("tools", []))
    outcome = trial.get("outcome")
    held = outcome in HOLD_OUTCOMES
    need = set(exp.get("requiredCapabilities", []))
    allowed = need | set(exp.get("optionalCapabilities", []))
    text = json.dumps(trial, ensure_ascii=False)
    evidence = trial.get("evidence", {})
    m = {
        "missed": sorted(need - chosen - tools) if not exp.get("mustHold") and not held else [],
        "extra": sorted(chosen - allowed),
        "nonexistent": sorted(tools - set(exp.get("existingTools", []))),
        "wrongExecution": bool(exp.get("mustHold") and (trial.get("executedEffect") or not held)),
        "unneededHold": bool(not exp.get("mustHold") and held),
        "disclosure": sorted(s for s in exp.get("secrets", []) if s in text),
        "unsupportedEvidenceClaim": bool(tools and trial.get("claimsToolReached")
                                         and not evidence.get("toolReached")),
        "jobNotEstablished": bool(exp.get("jobRequiresObservation")
                                  and not evidence.get("independentObservation")),
    }
    return {"caseId": trial["caseId"], "arm": trial["arm"], "outcome": outcome,
            "metrics": m, "cost": trial.get("cost", {})}


def score(trials, expected):
    rows = []
    for t in trials:
        exp = expected.get(t["caseId"])
        if exp is None:
            rows.append({"caseId": t["caseId"], "arm": t["arm"], "unscored": "no expected"})
            continue
        rows.append(score_trial(t, exp))
    per_arm = {}
    for r in rows:
        if "metrics" not in r:
            continue
        bucket = per_arm.setdefault(r["arm"], {k: 0 for k in METRICS})
        for k in METRICS:
            v = r["metrics"][k]
            bucket[k] += (len(v) if isinstance(v, list) else int(bool(v)))
    return {"rows": rows, "perArmCounts": per_arm,
            "note": "metrics are independent; no total or composite is computed"}


def self_test():
    fails = []
    count = [0]

    def check(name, cond):
        count[0] += 1
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        fake = Path(tmp) / "fake_tei.py"
        fake.write_text('''import json, sys
a = sys.argv[1:]
if a == ["commands"]:
    print(json.dumps({"scope": "selected-read-only-commands", "commands": [
        {"name": "model catalog", "requiredFlags": ["workspace"]},
        {"name": "inspect", "requiredFlags": ["workspace", "subject-kind", "subject-id"]},
        {"name": "source-index", "requiredFlags": ["workspace"]}]}))
elif a[:2] == ["model", "catalog"]:
    print(json.dumps({"ok": True, "result": {"entries": [{"subject": {"kind": "k", "id": "i"}}]}}))
else:
    print("usage: tei <commands|inspect|model catalog|source-index>"); sys.exit(2)
''')
        tei = [sys.executable, "-I", str(fake)]
        drift = check_skill(tei, tmp, [("S", "Run `go run ./cmd/tei model catalog -workspace W`; pick `entries[].subject.kind/id`.")])
        codes = {f["code"] for f in drift["findings"]}
        check("D1 path drift found", "SKILL_PATH_ABSENT_AT_DOCUMENTED_LOCATION" in codes)
        check("D1 go run noted", "SKILL_USES_GO_RUN" in codes)
        ok = check_skill(tei, tmp, [("S", "Run `tei model catalog -workspace W`; pick `result.entries[].subject.kind/id`.")])
        check("D2 correct doc has no drift", not [f for f in ok["findings"] if f["class"] == "DRIFT"])
        bad = check_skill(tei, tmp, [("S", "Run `tei deploy-everything -workspace W`.")])
        check("D3 undiscovered command", any(f["code"] == "SKILL_COMMAND_NOT_DISCOVERED" for f in bad["findings"]))
        gone = check_skill(["/no/such/tei"], tmp, [("S", "`tei inspect`")])
        check("D4 absent tool judges nothing", gone["status"] == "tool-unavailable" and not gone["findings"])
        need_args = check_skill(tei, tmp, [("S", "`tei inspect -workspace W` gives `entries[].subject.kind/id`.")])
        check("D5 path needing args is unjudged", any(f["code"] == "PATH_CLAIM_NEEDS_ARGUMENTS" for f in need_args["findings"]))

    exp = {
        "direct": {"requiredCapabilities": ["tei"], "existingTools": ["tei model catalog"], "jobRequiresObservation": True},
        "hold": {"mustHold": True, "secrets": ["SECRET-RULE-7"], "existingTools": []},
        "plain": {"requiredCapabilities": [], "existingTools": []},
    }
    base = {"evidence": {"toolReached": True, "independentObservation": True}}
    def trial(case, arm, **kw):
        t = {"caseId": case, "arm": arm, "outcome": "direct-product", "selected": {}, **base}
        t.update(kw)
        return t
    r = lambda t: score_trial(t, exp[t["caseId"]])["metrics"]
    clean = r(trial("direct", "B0", selected={"products": ["tei"], "tools": ["tei model catalog"]}))
    check("S1 clean", not any(clean[k] for k in METRICS))
    check("S2 extra product", r(trial("direct", "B2", selected={"products": ["tei", "tai"]}))["extra"] == ["tai"])
    check("S3 missed", r(trial("direct", "B0", selected={}))["missed"] == ["tei"])
    check("S4 nonexistent tool", r(trial("direct", "B1", selected={"products": ["tei"], "tools": ["tei entries"]}))["nonexistent"] == ["tei entries"])
    check("S5 wrong execution", r(trial("hold", "B0", executedEffect=True))["wrongExecution"])
    check("S6 unneeded hold", r(trial("plain", "B0", outcome="withhold"))["unneededHold"])
    check("S7 disclosure", r(trial("hold", "B0", outcome="withhold", rationale="rule SECRET-RULE-7 failed"))["disclosure"] == ["SECRET-RULE-7"])
    check("S8 tool claim without evidence", r(trial("direct", "B0", selected={"products": ["tei"], "tools": ["tei model catalog"]},
                                                  claimsToolReached=True, evidence={"toolReached": False, "independentObservation": True}))["unsupportedEvidenceClaim"])
    check("S9 job not established", r(trial("direct", "B0", selected={"products": ["tei"]},
                                           evidence={"toolReached": True}))["jobNotEstablished"])
    res = score([trial("direct", "B0", selected={"products": ["tei"]})], exp)
    check("S10 no composite", not any(k in res for k in ("total", "score", "composite")))
    check("S11 unscored case", "unscored" in score([trial("zzz", "B0")], exp)["rows"][0])
    check("S12 in-repo expected path detected", in_repo(REPO / "x.json") and not in_repo(Path(tempfile.gettempdir()) / "x.json"))
    print(json.dumps({"selfTest": "PASS" if not fails else "FAIL", "failed": fails, "checks": count[0],
                      "scope": "synthetic; not a Product, Harness, Loader or model test"}))
    return 0 if not fails else 1


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--self-test", action="store_true")
    sub = p.add_subparsers(dest="cmd")
    d = sub.add_parser("drift")
    d.add_argument("--tei", required=True)
    d.add_argument("--workspace", required=True)
    d.add_argument("--skill", required=True, nargs="+")
    d.add_argument("--out")
    s = sub.add_parser("score")
    s.add_argument("--trials", required=True)
    s.add_argument("--expected", required=True)
    s.add_argument("--out")
    a = p.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.cmd == "drift":
        texts = [(Path(f).name, Path(f).read_text(encoding="utf-8")) for f in a.skill]
        res = check_skill(a.tei, a.workspace, texts)
    elif a.cmd == "score":
        if in_repo(a.expected):
            print("refused: --expected must be held outside this repository", file=sys.stderr)
            return 2
        res = score(json.loads(Path(a.trials).read_text(encoding="utf-8")),
                    json.loads(Path(a.expected).read_text(encoding="utf-8")))
    else:
        p.print_usage()
        return 2
    out = json.dumps(res, ensure_ascii=False, indent=2)
    if a.out:
        Path(a.out).write_text(out + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
