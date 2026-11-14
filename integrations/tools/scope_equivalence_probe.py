"""Which TEI read-only responses change when only content outside the asked scope changes?

Read-only probe for TAI #488 / YIC-ROUTE-05. It copies a public TEI Workspace
into three throw-away worlds and compares the same requests across them:

  A  the Workspace as given
  B  A plus an unrelated namespace (nothing references sales.order)
  C  A plus a declaration that references sales.order

A response that differs between A and B reports something wider than the asked
scope. This probe has no Principal or Grant model; it does not test hiding from
an unauthorized caller, only scope-relative stability. Public synthetic Source
only. `--self-test` uses a fake CLI and is not a TEI, Harness or model test.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

B_FILE = ("semantic/vault/vault.tei",
          "namespace vault\n\ntype PayoutId from std.identifier\n\ndata Payout {\n"
          "    attribute payoutId type vault.payout_id\n    attribute amount type std.money\n}\n\n"
          "capability vault.payout.approve {\n    input payout vault.payout\n    output vault.payout\n}\n")
C_FILE = ("semantic/vault/vault.tei",
          "namespace vault\n\ndata Hold {\n    attribute reason type std.text\n"
          "    relation order to sales.order one\n}\n\n"
          "capability vault.order.freeze {\n    input order sales.order\n    output sales.order\n}\n")
SUBJECT = ["-subject-kind", "semantic-data", "-subject-id", "sales.order"]


def queries(w):
    trace = ["trace", "-workspace", w, "-scope", "reference-observation", *SUBJECT, "-mode", "summary"]
    return {
        "inspect": ["inspect", "-workspace", w, *SUBJECT],
        "knowledge-context definition": ["knowledge-context", "-workspace", w, *SUBJECT, "-disclose", "definition"],
        "knowledge-context definition+dependencies": ["knowledge-context", "-workspace", w, *SUBJECT, "-disclose", "definition,dependencies"],
        "source-index subject": ["source-index", "-workspace", w, *SUBJECT],
        "knowledge-review-plan": ["knowledge-review-plan", "-workspace", w, *SUBJECT],
        "trace outgoing": trace + ["-direction", "outgoing"],
        "trace both": trace + ["-direction", "both"],
        "model locate": ["model", "locate", "-workspace", w, *SUBJECT],
        "model catalog -namespace sales": ["model", "catalog", "-workspace", w, "-namespace", "sales"],
        "validate": ["validate", "-workspace", w, "-json"],
    }


def leaves(x, path="", out=None):
    out = {} if out is None else out
    if isinstance(x, dict):
        for k, v in x.items():
            leaves(v, f"{path}.{k}", out)
    elif isinstance(x, list):
        out[path + "#len"] = len(x)
        for v in x:
            leaves(v, path + "[]", out)
    else:
        out[path] = x
    return out


def run(tei, args, root):
    cmd = list(tei) if isinstance(tei, (list, tuple)) else [str(tei)]
    p = subprocess.run(cmd + args, capture_output=True, timeout=120)
    text = p.stdout.decode("utf-8", "replace").replace(str(root), "<W>").replace(str(root).replace("\\", "/"), "<W>")
    try:
        return p.returncode, leaves(json.loads(text))
    except ValueError:
        return p.returncode, {"raw": text[:200]}


def world(src, dest, extra):
    shutil.copytree(src, dest)
    if extra:
        rel, text = extra
        target = Path(dest) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")


def probe(tei, src, qfn=queries):
    with tempfile.TemporaryDirectory(prefix="scope-eq-") as tmp:
        roots = {}
        for name, extra in (("A", None), ("B", B_FILE), ("C", C_FILE)):
            roots[name] = Path(tmp) / name
            world(src, roots[name], extra)
        rows = {}
        for label in qfn(str(roots["A"])):
            got = {n: run(tei, qfn(str(r))[label], r) for n, r in roots.items()}
            base = got["A"][1]
            row = {"exitA": got["A"][0]}
            for n in ("B", "C"):
                code, leaf = got[n]
                diff = sorted(k for k in set(base) | set(leaf) if base.get(k) != leaf.get(k))
                row[n] = {"exit": code, "changedLeaves": len(diff), "keys": diff[:10]}
            rows[label] = row
    return rows


def self_test():
    with tempfile.TemporaryDirectory() as tmp:
        fake = Path(tmp) / "fake.py"
        fake.write_text('import json, sys, pathlib\n'
                        'w = sys.argv[sys.argv.index("-workspace") + 1]\n'
                        'n = len(list(pathlib.Path(w).rglob("*.tei")))\n'
                        'scoped = {"result": {"definition": "same"}}\n'
                        'wide = {"result": {"definition": "same", "total": n}}\n'
                        'print(json.dumps(scoped if sys.argv[1] == "inspect" else wide))\n')
        src = Path(tmp) / "src"
        (src / "semantic").mkdir(parents=True)
        (src / "semantic" / "a.tei").write_text("namespace a\n")
        rows = probe([sys.executable, "-I", str(fake)], src, lambda w: {
            "scoped": ["inspect", "-workspace", w], "wide": ["validate", "-workspace", w]})
    ok = (rows["scoped"]["B"]["changedLeaves"] == 0 and rows["wide"]["B"]["changedLeaves"] == 1
          and rows["wide"]["C"]["changedLeaves"] == 1)
    print(json.dumps({"selfTest": "PASS" if ok else "FAIL", "checks": 3,
                      "scope": "synthetic fake CLI; not a TEI, Harness or model test"}))
    return 0 if ok else 1


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--tei")
    p.add_argument("--workspace", help="public TEI Workspace to copy (e.g. reference/workspace)")
    p.add_argument("--out")
    a = p.parse_args(argv)
    if a.self_test:
        return self_test()
    if not (a.tei and a.workspace):
        p.print_usage()
        return 2
    rows = probe(a.tei, a.workspace)
    out = json.dumps(rows, ensure_ascii=False, indent=2)
    if a.out:
        Path(a.out).write_text(out + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
