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
    if not isinstance(doc, dict) or doc.get("ok") is False:
        return None
    commands = doc.get("commands")
    if not isinstance(commands, list):
        return None
    if any(not isinstance(c, dict) or not isinstance(c.get("name"), str)
           or not c["name"].strip()
           or not isinstance(c.get("requiredFlags", []), list)
           or any(not isinstance(flag, str) for flag in c.get("requiredFlags", []))
           for c in commands):
        return None
    names = [c["name"] for c in commands]
    if len(names) != len(set(names)):
        # Conflicting entries cannot silently overwrite one another.
        return None
    return {
        "sha256": hashlib.sha256(out.encode("utf-8")).hexdigest(),
        "scope": doc.get("scope"),
        "commands": {c["name"]: c for c in commands},
    }


def usage_commands(tei):
    """Read command names from CLI usage; this is not a grant or complete discovery."""
    cmd = list(tei) if isinstance(tei, (list, tuple)) else [str(tei)]
    try:
        q = subprocess.run(cmd + ["__no_such_command__"], capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    out = (q.stdout + q.stderr).decode("utf-8", "replace")
    m = re.search(r"<([^>]+)>", out or "")
    return set(m.group(1).split("|")) if m else None


def usage_count(tei):
    names = usage_commands(tei)
    return len(names) if names is not None else None


CMD_RE = re.compile(r"(?:go run \./cmd/tei|\btei)\s+([a-z][a-z-]*(?:\s+[a-z][a-z-]*)?)")
PATH_RE = re.compile(r"`([A-Za-z_][\w.]*)\[\]\.([\w.]+(?:/\w+)*)`")


def match_command(words, names):
    """An advertised parent never proves a two-word command.

    CMD_RE captures up to two command words. If the Skill explicitly writes
    both words, the entire name must occur in scoped discovery; otherwise
    leave it unjudged. Flags (e.g. -workspace) are outside CMD_RE.
    """
    parts = words.split()
    if not parts:
        return None
    full_name = " ".join(parts)
    return full_name if full_name in names else None


def check_skill(tei, workspace, skill_texts):
    findings = []
    disc = discover(tei)
    if disc is None:
        return {"status": "tool-unavailable", "findings": [],
                "note": "discovery unavailable or unqualified; no claim was judged"}
    names = set(disc["commands"])
    usage_names = usage_commands(tei)
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
                    claimed = m.group(1).strip()
                    root = claimed.split()[0]
                    if usage_names is not None and claimed in usage_names:
                        # Only an exact usage entry demonstrates that the
                        # complete name was advertised outside this scope.
                        findings.append({"class": "UNJUDGED", "code": "SKILL_COMMAND_OUTSIDE_DISCOVERY_SCOPE",
                                         "doc": label, "detail": claimed, "scope": disc["scope"]})
                    elif " " in claimed and (root in names or
                                                 (usage_names is not None and root in usage_names)):
                        # A parent in scoped discovery OR usage does not
                        # establish its child. Never silently execute the
                        # parent when a Skill named an unconfirmed child.
                        findings.append({"class": "UNJUDGED", "code": "SKILL_SUBCOMMAND_NOT_ESTABLISHED",
                                         "doc": label, "detail": claimed, "scope": disc["scope"]})
                    else:
                        findings.append({"class": "DRIFT", "code": "SKILL_COMMAND_NOT_DISCOVERED",
                                         "doc": label, "detail": claimed, "scope": disc["scope"],
                                         "existence": "not-established"})
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
                if code != 0 or (isinstance(doc, dict) and doc.get("ok") is False):
                    # Error responses can retain a result-shaped payload. It
                    # must not validate a documented success path, even when
                    # the JSON structure happens to match.
                    findings.append({"class": "UNJUDGED", "code": "COMMAND_RESULT_NOT_ACCEPTED",
                                     "doc": label, "command": line_cmd, "claim": claim,
                                     "exit": code,
                                     "reason": "cli-nonzero" if code != 0 else "response-ok-false"})
                    continue
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
                      "discoveredCommands": len(names),
                      "usageCommands": len(usage_names) if usage_names is not None else None},
        "skillMentionsDiscovered": sorted(mentioned),
        "discoveredNotCoveredBySkill": len(uncovered),
        "findings": findings,
        "limits": ["Only explicit command spans and `list[].a.b/c` path claims are parsed.",
                   "A scoped commands response cannot prove that omitted commands do not exist.",
                    "Failed or malformed discovery cannot establish a command or success path.",
                   "Usage-only commands are not demonstrated callable or authorized.",
                   "A usage parent name alone does not establish its subcommands.",
                   "Nonzero CLI exits and explicit ok=false cannot prove a success-response path.",
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
if a == ["--discovery-failed", "commands"]:
    print(json.dumps({"ok": False, "scope": "selected-read-only-commands",
                      "commands": [{"name": "model catalog", "requiredFlags": ["workspace"]}]}))
elif a == ["--discovery-malformed", "commands"]:
    print(json.dumps({"ok": True, "scope": "selected-read-only-commands",
                      "commands": {"name": "model catalog"}}))
elif a == ["--discovery-duplicate", "commands"]:
    print(json.dumps({"ok": True, "scope": "selected-read-only-commands",
                      "commands": [{"name": "model catalog", "requiredFlags": ["workspace"]},
                                   {"name": "model catalog", "requiredFlags": []}]}))
elif a == ["commands"]:
    print(json.dumps({"scope": "selected-read-only-commands", "commands": [
        {"name": "model catalog", "requiredFlags": ["workspace"]},
        {"name": "model", "requiredFlags": ["workspace"]},
        {"name": "inspect", "requiredFlags": ["workspace", "subject-kind", "subject-id"]},
        {"name": "source-index", "requiredFlags": ["workspace"]},
        {"name": "read-failed", "requiredFlags": ["workspace"]},
        {"name": "read-softfail", "requiredFlags": ["workspace"]}]}))
elif a and a[0] == "read-failed":
    print(json.dumps({"ok": True, "result": {"entries": [{"subject": {"kind": "k", "id": "i"}}]}}))
    sys.exit(3)
elif a and a[0] == "read-softfail":
    print(json.dumps({"ok": False, "result": {"entries": [{"subject": {"kind": "k", "id": "i"}}]}}))
elif a[:2] == ["model", "catalog"]:
    print(json.dumps({"ok": True, "result": {"entries": [{"subject": {"kind": "k", "id": "i"}}]}}))
else:
    print("usage: tei <commands|inspect|model|model catalog|source-index|hidden-example|read-failed|read-softfail>"); sys.exit(2)
''')
        tei = [sys.executable, "-I", str(fake)]
        drift = check_skill(tei, tmp, [("S", "Run `go run ./cmd/tei model catalog -workspace W`; pick `entries[].subject.kind/id`.")])
        codes = {f["code"] for f in drift["findings"]}
        check("D1 path drift found", "SKILL_PATH_ABSENT_AT_DOCUMENTED_LOCATION" in codes)
        check("D1 go run noted", "SKILL_USES_GO_RUN" in codes)
        ok = check_skill(tei, tmp, [("S", "Run `tei model catalog -workspace W`; pick `result.entries[].subject.kind/id`.")])
        check("D2 correct doc has no drift", not [f for f in ok["findings"] if f["class"] == "DRIFT"])
        bad = check_skill(tei, tmp, [("S", "Run `tei deploy-everything -workspace W`.")])
        check("D3 undiscovered command", any(f["code"] == "SKILL_COMMAND_NOT_DISCOVERED"
                                             and f.get("existence") == "not-established"
                                             for f in bad["findings"]))
        usage_only = check_skill(tei, tmp, [("S", "Try `tei hidden-example`.")])
        check("D6 usage-only is not absent", any(f["code"] == "SKILL_COMMAND_OUTSIDE_DISCOVERY_SCOPE"
                                                and f["class"] == "UNJUDGED"
                                                for f in usage_only["findings"]))
        check("D7 scoped discovery is not exhaustive",
              usage_only["discovery"]["discoveredCommands"] == 6
              and usage_only["discovery"]["usageCommands"] == 8
              and not [f for f in usage_only["findings"] if f["class"] == "DRIFT"])
        unknown_subcommand = check_skill(tei, tmp, [("S", "Try `tei model imagined`.")])
        check("D8 usage parent does not prove a subcommand",
              any(f["code"] == "SKILL_SUBCOMMAND_NOT_ESTABLISHED"
                  and f["class"] == "UNJUDGED"
                  and f["detail"] == "model imagined"
                  for f in unknown_subcommand["findings"]))
        check("D9 parent-only usage does not prove an exact child",
              not any(f["code"] == "SKILL_COMMAND_OUTSIDE_DISCOVERY_SCOPE"
                      for f in unknown_subcommand["findings"])
              and "model" not in unknown_subcommand["skillMentionsDiscovered"])
        unknown_with_path = check_skill(tei, tmp, [
            ("S", "`tei model imagined -workspace W` returns `entries[].subject.kind/id`.")])
        check("D13 discovered parent does not validate a child's JSON path",
              any(f["code"] == "SKILL_SUBCOMMAND_NOT_ESTABLISHED"
                  for f in unknown_with_path["findings"])
              and any(f["code"] == "PATH_CLAIM_NEEDS_ARGUMENTS"
                      for f in unknown_with_path["findings"])
              and not any(f["code"].startswith("SKILL_PATH_")
                          or f["code"] == "COMMAND_RESULT_NOT_ACCEPTED"
                          for f in unknown_with_path["findings"]))
        parent_only = check_skill(tei, tmp, [("S", "`tei model -workspace W`.")])
        check("D14 explicitly named discovered parent remains available",
              parent_only["skillMentionsDiscovered"] == ["model"]
              and not [f for f in parent_only["findings"] if f["class"] == "DRIFT"])
        exact_usage_subcommand = check_skill(tei, tmp, [("S", "Try `tei model catalog`.")])
        check("D10 actual discovered child stays discovered",
              exact_usage_subcommand["skillMentionsDiscovered"] == ["model catalog"]
              and not [f for f in exact_usage_subcommand["findings"] if f["class"] == "DRIFT"])
        bad_exit = check_skill(tei, tmp, [("S", "`tei read-failed -workspace W` returns `entries[].subject.kind/id`.")])
        check("D11 nonzero result-shaped JSON cannot prove a success path",
              any(f["code"] == "COMMAND_RESULT_NOT_ACCEPTED"
                  and f["class"] == "UNJUDGED" and f["reason"] == "cli-nonzero"
                  and f["exit"] == 3 for f in bad_exit["findings"])
              and not any(f["code"] == "SKILL_PATH_ABSENT_AT_DOCUMENTED_LOCATION"
                          for f in bad_exit["findings"]))
        soft_failure = check_skill(tei, tmp, [("S", "`tei read-softfail -workspace W` returns `entries[].subject.kind/id`.")])
        check("D12 ok=false JSON with exit zero cannot prove a success path",
              any(f["code"] == "COMMAND_RESULT_NOT_ACCEPTED"
                  and f["class"] == "UNJUDGED" and f["reason"] == "response-ok-false"
                  and f["exit"] == 0 for f in soft_failure["findings"])
              and not any(f["code"] == "SKILL_PATH_ABSENT_AT_DOCUMENTED_LOCATION"
                          for f in soft_failure["findings"]))
        failed_discovery = check_skill(tei + ["--discovery-failed"], tmp,
                                       [("S", "`tei model catalog` gives `result.entries[].subject.kind/id`.")])
        check("D15 ok=false discovery cannot validate a Skill path",
              failed_discovery["status"] == "tool-unavailable" and not failed_discovery["findings"])
        malformed_discovery = check_skill(tei + ["--discovery-malformed"], tmp,
                                          [("S", "`tei model catalog`.")])
        check("D16 malformed discovery cannot establish a command",
              malformed_discovery["status"] == "tool-unavailable" and not malformed_discovery["findings"])
        duplicate_discovery = check_skill(tei + ["--discovery-duplicate"], tmp,
                                         [("S", "`tei model catalog`.")])
        check("D17 duplicate command names cannot overwrite one another",
              duplicate_discovery["status"] == "tool-unavailable" and not duplicate_discovery["findings"])
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
