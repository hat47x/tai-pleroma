"""Check that the projected MMI format profile is accepted by MMI's own validator."""

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "evaluations/artifacts/mmi-format-profile-projection.json"
RECEIPT = ROOT / "evaluations/records/MMI-TEI-profile-2026-11-03.json"

SCRIPT = """
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
const modulePath = process.env.MMI_FORMAT_PROFILE_MODULE;
const artifactPath = process.env.MMI_ARTIFACT_PATH;
const mod = await import(pathToFileURL(modulePath).href);
const artifact = JSON.parse(readFileSync(artifactPath, "utf8"));
try {
  mod.assertFormatProfile(artifact.profile);
  console.log(JSON.stringify({ accepted: true }));
} catch (error) {
  console.log(JSON.stringify({ accepted: false, message: String(error && error.message) }));
}
"""


def main():
    mmi_repo = Path(os.environ.get("MMI_REPO", r"D:\GIT\hat47x\markdown-matrix-injector")) / "03_Implement"
    module = mmi_repo / "src/experimental/formatProfile.ts"
    workdir = Path(tempfile.mkdtemp(prefix="tei-mmi-assert-", dir=os.environ.get("GOTMPDIR") or None))
    script = workdir / "assert.mjs"
    script.write_text(SCRIPT, encoding="utf-8")
    env = {**os.environ, "MMI_FORMAT_PROFILE_MODULE": str(module), "MMI_ARTIFACT_PATH": str(ARTIFACT)}
    completed = subprocess.run(
        ["node", "--import", "tsx", str(script)],
        cwd=mmi_repo,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = completed.stdout.strip().splitlines()
    parsed = {}
    for line in output:
        if line.startswith("{"):
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
    accepted = parsed.get("accepted") is True
    receipt = {
        "schema": "tai.reference.tei-mmi-profile-assert/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Node 24 and MMI's tsx toolchain",
        "command": "python integrations/tools/mmi_profile_assert.py",
        "result": "PASS" if accepted else "FAIL",
        "artifact": {"path": str(ARTIFACT.relative_to(ROOT)).replace("\\", "/")},
        "observed": {
            "accepted": accepted,
            "message": parsed.get("message"),
            "returncode": completed.returncode,
            "stderrTail": completed.stderr.strip().splitlines()[-2:],
        },
        "scope": "Calls MMI's assertFormatProfile on the projected profile. It does not build an approved profile, run a worksheet prototype, or exercise MMI's review workflow.",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": accepted, "returncode": completed.returncode}))


if __name__ == "__main__":
    raise SystemExit(main())
