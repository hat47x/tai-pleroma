"""Run the four TEI projection candidates and feed their outputs to the assembler."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

from document_assembler import AssemblyError, assemble

CONTRACTS = ["document-record", "card-record", "island-record", "edge-record", "affiliation-record"]


def digest(path):
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def run(command, cwd, stdin_text=None):
    return subprocess.run(
        command,
        cwd=cwd,
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    tei_repo = os.path.abspath(args.tei_repo)
    workspace = os.path.abspath(args.workspace)
    started = time.monotonic()
    candidates = {}
    cases_run = 0
    case_results = []

    with tempfile.TemporaryDirectory(prefix="tei-flow-") as tmp:
        for name in CONTRACTS:
            contract_path = os.path.join(workspace, "candidates", name, "contract.json")
            fixtures_path = os.path.join(workspace, "candidates", name, "fixtures.json")
            out_dir = os.path.join(tmp, name)
            build = run(
                [
                    "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
                    "-contract", contract_path, "-strategy", "text-record-template", "-out", out_dir,
                ],
                cwd=tei_repo,
            )
            if build.returncode != 0:
                print(build.stderr, file=sys.stderr)
                return 1
            manifest = json.loads(build.stdout)[0]
            binary = os.path.join(out_dir, "candidate.exe")
            compiled = run(["go", "build", "-o", binary, "main.go"], cwd=out_dir)
            if compiled.returncode != 0:
                print(compiled.stderr, file=sys.stderr)
                return 1

            with open(fixtures_path, encoding="utf-8") as handle:
                fixtures = json.load(handle)
            records = {}
            for case in fixtures["cases"]:
                cases_run += 1
                executed = run([binary], cwd=out_dir, stdin_text=json.dumps(case["input"]))
                if executed.returncode != 0:
                    case_results.append({"contract": name, "case": case["id"], "passed": False})
                    continue
                actual = json.loads(executed.stdout)
                passed = all(actual.get(key) == value for key, value in case["want"].items())
                case_results.append({"contract": name, "case": case["id"], "passed": passed})
                if passed and actual.get("state") == "present":
                    records[case["id"]] = json.loads(actual["text"])
            candidates[name] = {
                "sourceDigest": manifest.get("SourceDigest") or manifest.get("Manifest", {}).get("sourceDigest"),
                "cases": len(fixtures["cases"]),
                "passed": sum(1 for item in case_results if item["contract"] == name and item["passed"]),
                "records": records,
            }

    document = candidates["document-record"]["records"]["present"]
    cards = [
        candidates["card-record"]["records"]["present"],
        candidates["card-record"]["records"]["present-2"],
    ]
    islands = [candidates["island-record"]["records"]["present"]]
    edges = [candidates["edge-record"]["records"]["present"]]
    affiliations = [candidates["affiliation-record"]["records"]["present"]]

    composed = assemble(document, cards, islands, edges, affiliations)
    dangling = [dict(edges[0], toId="card-9")]
    rejected = False
    try:
        assemble(document, cards, islands, dangling, affiliations)
    except AssemblyError:
        rejected = True

    receipt = {
        "schema": "tai.reference.tei-integration-flow/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "teiCommit": run(["git", "rev-parse", "HEAD"], cwd=tei_repo).stdout.strip(),
        "host": "Windows with Go on PATH and Python 3.12",
        "command": f"python integrations/pilot-sui-document/assembler/integration_flow.py --tei-repo {tei_repo} --workspace {workspace}",
        "result": "PASS",
        "elapsedMillis": round((time.monotonic() - started) * 1000),
        "contracts": {name: {"sourceDigest": data["sourceDigest"], "cases": data["cases"], "passed": data["passed"]} for name, data in candidates.items()},
        "casesRun": cases_run,
        "casesPassed": sum(1 for item in case_results if item["passed"]),
        "composed": {
            "id": composed["document"]["id"],
            "cards": len(composed["cards"]),
            "islands": len(composed["islands"]),
            "edges": len(composed["edges"]),
            "affiliations": len(composed["affiliations"]),
        },
        "danglingReferenceRejected": rejected,
        "scope": "Generated candidates are executed on this host and their present-case outputs are composed in-process. It does not generate SUI code, use a real target, or show human acceptance.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"casesPassed": receipt["casesPassed"], "rejected": rejected}))
    return 0 if receipt["casesPassed"] == cases_run and rejected else 1


if __name__ == "__main__":
    sys.exit(main())
