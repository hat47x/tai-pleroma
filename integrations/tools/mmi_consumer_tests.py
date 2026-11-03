"""Run MMI's consumer test against the projected artifact."""

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "evaluations/artifacts/mmi-format-profile-projection.json"


def main():
    mmi_repo = Path(os.environ.get("MMI_REPO", r"D:\GIT\hat47x\markdown-matrix-injector")) / "03_Implement"
    env = {**os.environ, "TEI_MMI_PROJECTION_ARTIFACT": str(ARTIFACT)}
    completed = subprocess.run(
        ["node", "--import", "tsx", "--test", "test/teiProjection.test.ts"],
        cwd=mmi_repo,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = completed.stdout + completed.stderr
    passed_match = re.search(r"pass (\d+)", output)
    failed_match = re.search(r"fail (\d+)", output)
    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 1
    ok = completed.returncode == 0 and failed == 0 and passed > 0
    print(json.dumps({"passed": passed, "failed": failed, "returncode": completed.returncode}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
