"""Reproduce the saved SUI summary/current MMI observation gap using copies only.

Requires Go, Node, MMI_ROOT and SEI_ROOT as for reference-scn001-run.
Exit zero means the comparison completed, not that the integration is accepted.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="new output directory")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.out.resolve()
    for name in ("MMI_ROOT", "SEI_ROOT"):
        if not os.environ.get(name):
            parser.error(f"{name} must select an isolated development checkout")
    # Refuse reuse, including after an incomplete run; never retry unknown writes.
    output.mkdir(parents=True, exist_ok=False)
    alternate = output / "alternate"
    modules = ("reference-mmi-readonly", "reference-sei-decision", "reference-scn001",
               "reference-scn001-render", "reference-publication-gate", "reference-sui-link")
    for module in modules:
        shutil.copytree(root / "tools" / module, alternate / "tools" / module)
    (alternate / "evaluations").mkdir()
    shutil.copyfile(root / "evaluations/SCN-001-review-status.json",
                    alternate / "evaluations/SCN-001-review-status.json")
    source_csv = root / "tools/reference-mmi-readonly/testdata/workspace/observations.csv"
    csv = alternate / "tools/reference-mmi-readonly/testdata/workspace/observations.csv"
    original = csv.read_bytes()
    changed_text = "施設の利用は予約不要（SUI照合の比較試験）"
    old = "施設の利用は予約不要".encode()
    if original.count(old) != 2:
        raise RuntimeError("expected exactly O-02 and O-07 in the synthetic workspace")
    csv.write_bytes(original.replace(old, changed_text.encode()))
    link = root / "evaluations/records/SUI-SCN-link-2026-10-26.json"
    source = root / "evaluations/records/SUI-api-2026-10-26.json"
    tracked = (source_csv, csv, link, source)
    before = [digest(path) for path in tracked]

    def call(command, cwd, name, expected=0):
        result = subprocess.run(command, cwd=cwd, capture_output=True, timeout=240)
        (output / (name + ".stdout")).write_bytes(result.stdout)
        (output / (name + ".stderr")).write_bytes(result.stderr)
        if result.returncode != expected:
            raise RuntimeError(f"{name}: exit {result.returncode}, expected {expected}; see logs")
        return result.stdout

    binary = output / ("run.exe" if os.name == "nt" else "run")
    call(["go", "build", "-o", str(binary), "."],
         root / "tools/reference-scn001-run", "build")
    control = json.loads(call(["go", "run", ".", "-fixture",
                               str(alternate / "tools/reference-scn001/testdata/scn001.json"),
                               "-sui-receipt", str(source)],
                              alternate / "tools/reference-sui-link", "control"))
    if not control["passed"]:
        raise RuntimeError("unchanged synthetic fixture must match the saved SUI receipt")
    run_path, artifact = output / "run.json", output / "review.md"
    run = json.loads(call([str(binary), "-root", str(alternate), "-sui-link", str(link),
                           "-artifact-out", str(artifact), "-out", str(run_path)], root, "combined"))
    verified = json.loads(call([str(binary), "-verify", str(run_path), "-artifact", str(artifact)],
                               root, "verify"))
    mmi, resolved = output / "mmi.json", output / "resolved.json"
    call(["go", "run", ".", "-workspace", "testdata/workspace", "-out", str(mmi)],
         alternate / "tools/reference-mmi-readonly", "mmi")
    call(["go", "run", ".", "-fixture", "testdata/scn001.json", "-mmi-receipt", str(mmi),
          "-out-fixture", str(resolved)], alternate / "tools/reference-scn001", "scn")
    # go run propagates the checker's exit 1 as exit 1 on Linux and Windows.
    direct = json.loads(call(["go", "run", ".", "-fixture", str(resolved),
                              "-sui-receipt", str(source)],
                             alternate / "tools/reference-sui-link", "direct", expected=1))
    unchanged = before == [digest(path) for path in tracked]
    approvals = ("humanReviewed", "authorityVerified", "publicationApproved")
    gap = (run["passed"] and run["components"]["suiLink"]["passed"]
           and verified["passed"] and verified["artifactBytesVerified"]
           and not direct["passed"]
           and direct["reason"] == "card digest does not match the SCN observation: O-02"
           and changed_text in artifact.read_text(encoding="utf-8")
           and unchanged and all(run[key] is False for key in approvals))
    report = {"syntheticOnly": True, "gapObserved": gap, "unchangedFixtureLinkPassed": control["passed"],
              "combinedRunPassed": run["passed"], "artifactBytesVerified": verified["artifactBytesVerified"],
              "directLinkPassed": direct["passed"], "directLinkReason": direct.get("reason"),
              "runDigest": run["runDigest"],
              "artifactDigest": run["components"]["reviewArtifact"]["artifactDigest"],
              "sourcesUnchanged": unchanged, **{key: run[key] for key in approvals}}
    raw = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    (output / "report.json").write_text(raw, encoding="utf-8")
    print(raw, end="")
    if not gap:
        raise RuntimeError("the recorded gap was not reproduced; inspect this revision's behavior")


if __name__ == "__main__":
    main()
