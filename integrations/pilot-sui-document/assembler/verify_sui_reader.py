"""Verify that SUI reads the TAI projection artifact through its transport."""

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import time
from pathlib import Path


def digest(path):
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def load_transport(sui_repo):
    module_path = Path(sui_repo) / "03_Implement/backend/src/sui_sensemaking_api/tei_reference_transport.py"
    spec = importlib.util.spec_from_file_location("tei_reference_transport", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["tei_reference_transport"] = module
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    transport = load_transport(args.sui_repo)
    payload = json.loads(Path(args.artifact).read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="sui-tei-read-") as tmp:
        bound = Path(tmp) / "tenants" / "tenant-a" / "doc-1"
        bound.mkdir(parents=True)
        (bound / "documentv1-projection.json").write_text(
            Path(args.artifact).read_text(encoding="utf-8"), encoding="utf-8"
        )
        read = transport.read_bound_tei_reference_artifact(
            tmp, "tenant-a", "doc-1", "documentv1-projection"
        )
        other = transport.read_bound_tei_reference_artifact(
            tmp, "tenant-b", "doc-1", "documentv1-projection"
        )

    read_ok = isinstance(read, transport.TeiReferenceArtifact) and read.payload == payload
    isolated = (
        isinstance(other, transport.TeiReferenceReadFailure) and other.reason == "not-a-file"
    )

    receipt = {
        "schema": "tai.reference.tei-sui-reader/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "suiCommit": os.popen(f'git -C "{args.sui_repo}" rev-parse HEAD').read().strip(),
        "host": "Windows with Python 3.12",
        "command": f"python integrations/pilot-sui-document/assembler/verify_sui_reader.py --sui-repo {args.sui_repo} --artifact {args.artifact}",
        "result": "PASS" if read_ok and isolated else "FAIL",
        "artifact": {"path": os.path.relpath(args.artifact), "digest": digest(args.artifact)},
        "readOk": read_ok,
        "tenantIsolationRejected": isolated,
        "scope": "The SUI transport module is imported directly and reads the TAI artifact from a temporary tenant directory. It does not start the SUI server, exercise HTTP authorization, or prove deployment.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"readOk": read_ok, "isolated": isolated}))
    return 0 if read_ok and isolated else 1


if __name__ == "__main__":
    sys.exit(main())
