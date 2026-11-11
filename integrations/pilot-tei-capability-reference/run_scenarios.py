"""同じActivityで4つの状態を実CLIで確かめるシナリオ実行。

R1 参照成功 / R2 対象なし / R3 Source更新 / R4 古いRevisionを受領したConsumer。
加えて、Tool不在とHandoffの最小性を負例として確認する。

期待値はTEIの型付き診断（SUBJECT_NOT_FOUND / STALE_SNAPSHOT）と
TAI側の次元分離だけを検査する。意味の正しさ・実行権限・業務効果は判定しない。
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOL = Path(__file__).with_name("tei_capability_reference.py")
DEFAULT_SUBJECT = "semantic-capability:sales.order.submit"
DEFAULT_SCOPE = "definition,source,dependencies"
MUTATION = "\ndata OrderNote {\n    attribute noteId type std.text\n}\n"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_tool(args: list[str], expected: int = 0) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        [sys.executable, str(TOOL), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != expected:
        raise AssertionError(
            f"command failed ({proc.returncode} != {expected}): {args}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def observe(
    tei: str,
    workspace: Path,
    out: Path,
    subject: str = DEFAULT_SUBJECT,
    scope: str = DEFAULT_SCOPE,
    limit: int = 5,
    fmt: str = "json",
) -> dict[str, Any]:
    run_tool(
        [
            "observe",
            "--tei",
            tei,
            "--workspace",
            str(workspace),
            "--subject",
            subject,
            "--disclosure",
            scope,
            "--limit",
            str(limit),
            "--format",
            fmt,
            "--out",
            str(out),
        ]
    )
    if fmt == "json":
        return load(out)
    return {"markdown": out.read_text(encoding="utf-8")}


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def promotion_is_neutral(value: dict[str, Any]) -> bool:
    promotion = value.get("promotion") or {}
    return (
        promotion.get("teiCandidateToTaiDecision") == "not-performed"
        and promotion.get("teiDiagnosticToOperationPermission") == "not-performed"
        and promotion.get("activityDecision") == "not-made"
        and promotion.get("operationPermission") == "not-granted"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tei", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    workspace = Path(args.workspace).resolve()
    work = Path(tempfile.mkdtemp(prefix="tai-tei-capref-"))
    scenarios: list[dict[str, Any]] = []

    def record(scenario_id: str, title: str, observations: dict[str, Any]) -> None:
        scenarios.append({"id": scenario_id, "title": title, "result": "PASS", "observed": observations})

    try:
        # R1: 参照成功
        view1 = observe(args.tei, workspace, work / "view1.json")
        check(view1["schemaVersion"] == "tai.tei-capability-reference/view/v0", "view schema")
        check(view1["dimensions"]["toolAvailability"]["state"] == "available", "tool must be available")
        check(view1["dimensions"]["productCapability"]["state"] == "declared", "capability must be declared")
        check(view1["dimensions"]["skillLoad"]["state"] == "not-observed", "skill load must not be inferred")
        check(view1["dimensions"]["executionAuthority"]["state"] == "not-evaluated", "authority must not be inferred")
        check(view1["dimensions"]["consumerReceipt"]["state"] == "not-delivered", "receipt must not be inferred")
        check(promotion_is_neutral(view1), "view must not promote TEI candidates")
        capability = view1["capabilities"][0]
        check(capability["productCapability"]["canonical"]["id"] == "sales.order.submit", "canonical id")
        check(
            sorted(capability["disclosure"]["selected"]) == ["definition", "dependencies", "source"],
            "disclosure scope",
        )
        check(bool(capability["activityContinuation"]["reviewPlan"]["fingerprint"]), "review plan fingerprint")
        check(bool(capability["activityContinuation"]["trace"]["snapshotFingerprint"]), "trace snapshot")
        check(view1["capabilityCandidates"]["total"] >= 3, "limited capability list")
        check(view1["productComposition"]["state"] == "observed", "composition observed")
        markdown = observe(args.tei, workspace, work / "view1.md", fmt="markdown")["markdown"]
        check("Product Capability" in markdown and "Consumer receipt" in markdown, "markdown presentation")
        record(
            "R1",
            "TEI参照が成功する",
            {
                "productCapability": "declared",
                "canonical": capability["productCapability"]["canonical"],
                "capabilityListTotal": view1["capabilityCandidates"]["total"],
                "compositionSections": len(view1["productComposition"]["sections"]),
                "revision": view1["source"]["revision"],
            },
        )

        # Handoff（選択・Source・Revision・Disclosure Scopeだけを運ぶ）
        run_tool(
            [
                "handoff",
                "--view",
                str(work / "view1.json"),
                "--consumer",
                "tai-activity-session-1",
                "--disclosure",
                "definition,source",
                "--out",
                str(work / "handoff.json"),
            ]
        )
        envelope = load(work / "handoff.json")
        unexpected = set(envelope) - {
            "schemaVersion",
            "createdAt",
            "activity",
            "consumer",
            "selection",
            "source",
            "capabilities",
            "authority",
            "limits",
            "envelopeDigest",
        }
        check(not unexpected, f"handoff leaked keys: {unexpected}")
        for leaked in ("conversation", "transcript", "messages", "workspaceFiles"):
            check(leaked not in envelope, f"handoff must not carry {leaked}")
        check(envelope["selection"]["subjects"] == view1["request"]["selection"]["subjects"], "handoff selection")
        check(envelope["selection"]["disclosureScope"] == ["definition", "source"], "handoff scope")
        check(envelope["source"]["revision"] == view1["source"]["revision"], "handoff revision")
        run_tool(
            [
                "receipt",
                "--envelope",
                str(work / "handoff.json"),
                "--consumer",
                "tai-activity-session-1",
                "--out",
                str(work / "receipt.json"),
            ]
        )
        receipt = load(work / "receipt.json")
        check(receipt["state"] == "received", "receipt state")
        check(receipt["revision"] == view1["source"]["revision"], "receipt binds revision")
        # 負例: Disclosure Scopeを空にしたHandoffは受け付けない
        run_tool(
            [
                "handoff",
                "--view",
                str(work / "view1.json"),
                "--consumer",
                "tai-activity-session-1",
                "--disclosure",
                "",
                "--out",
                str(work / "handoff-empty.json"),
            ],
            expected=2,
        )
        record(
            "H1",
            "Handoffは選択・Source・Revision・Disclosure Scopeだけを運ぶ",
            {
                "keys": sorted(envelope),
                "selection": envelope["selection"],
                "revision": envelope["source"]["revision"],
                "emptyScopeRejected": True,
            },
        )

        # R2: 対象なし
        view_missing = observe(
            args.tei, workspace, work / "view-missing.json", subject="semantic-capability:sales.order.missing"
        )
        missing = view_missing["capabilities"][0]["productCapability"]
        check(view_missing["dimensions"]["toolAvailability"]["state"] == "available", "tool available on not-found")
        check(missing["state"] == "not-found", "missing subject state")
        check((missing.get("error") or {}).get("code") == "SUBJECT_NOT_FOUND", "typed not-found")
        check(view_missing["productComposition"]["state"] == "observed", "composition still observed")
        check(view_missing["dimensions"]["productCapability"]["state"] == "not-found", "not-found is dimension")
        check(promotion_is_neutral(view_missing), "not-found must not promote")
        record(
            "R2",
            "対象が見つからない",
            {
                "productCapability": "not-found",
                "diagnostic": missing.get("error"),
                "compositionStillObserved": True,
                "capabilityListTotal": view_missing["capabilityCandidates"]["total"],
            },
        )

        # R3: Source更新（同じActivityで別Revisionを観測）
        updated_workspace = work / "workspace-updated"
        shutil.copytree(workspace, updated_workspace)
        source_file = updated_workspace / "semantic" / "sales" / "order.tei"
        check(source_file.exists(), f"mutation target not found: {source_file}")
        source_file.write_text(source_file.read_text(encoding="utf-8") + MUTATION, encoding="utf-8")
        view2 = observe(args.tei, updated_workspace, work / "view2.json")
        check(view2["dimensions"]["productCapability"]["state"] == "declared", "updated capability still declared")
        run_tool(
            [
                "compare",
                "--before",
                str(work / "view1.json"),
                "--after",
                str(work / "view2.json"),
                "--out",
                str(work / "delta.json"),
            ]
        )
        delta = load(work / "delta.json")
        check(delta["state"] == "source-updated", f"delta state: {delta['state']}")
        check(delta["requalificationRequired"] is True, "requalification required")
        check("worldFingerprint" in delta["changed"], "world changed")
        check("sourceIndexFingerprint" in delta["changed"], "source index changed")
        check(bool(delta["artifactChanges"]), "artifact fingerprint changed")
        check(promotion_is_neutral(delta), "delta must not promote")
        record(
            "R3",
            "Sourceが更新された",
            {
                "state": delta["state"],
                "changed": delta["changed"],
                "requalificationRequired": True,
                "before": delta["before"]["revision"],
                "after": delta["after"]["revision"],
            },
        )

        # R4: Consumerが古いRevisionを受領
        run_tool(
            [
                "verify-consumer",
                "--receipt",
                str(work / "receipt.json"),
                "--tei",
                args.tei,
                "--workspace",
                str(updated_workspace),
                "--out",
                str(work / "check-stale.json"),
            ]
        )
        stale = load(work / "check-stale.json")
        check(stale["state"] == "stale", f"stale state: {stale['state']}")
        check(stale["consumerAction"] == "requalification-required", "stale action")
        check(
            any(item.get("error") == "STALE_SNAPSHOT" for item in stale["teiDiagnostics"]),
            "TEI typed stale diagnostic",
        )
        check(promotion_is_neutral(stale), "stale must not promote")
        run_tool(
            [
                "verify-consumer",
                "--receipt",
                str(work / "receipt.json"),
                "--tei",
                args.tei,
                "--workspace",
                str(workspace),
                "--out",
                str(work / "check-fresh.json"),
            ]
        )
        fresh = load(work / "check-fresh.json")
        check(fresh["state"] == "fresh", f"fresh state: {fresh['state']}")
        check(fresh["consumerAction"] == "none", "fresh action")
        record(
            "R4",
            "Consumerが古い結果を受け取る",
            {
                "state": stale["state"],
                "teiDiagnostics": stale["teiDiagnostics"],
                "consumerAction": stale["consumerAction"],
                "freshControl": fresh["state"],
            },
        )

        # 負例: Tool不在をProduct Capabilityの不在と混同しない
        view_no_tool = observe(str(work / "no-such-tei"), workspace, work / "view-no-tool.json")
        check(view_no_tool["dimensions"]["toolAvailability"]["state"] == "unavailable", "tool unavailable")
        check(view_no_tool["dimensions"]["productCapability"]["state"] == "unknown", "capability unknown")
        check(
            view_no_tool["capabilities"][0]["productCapability"]["state"] == "unknown",
            "subject unknown when tool missing",
        )
        check(promotion_is_neutral(view_no_tool), "tool unavailable must not promote")
        record(
            "N1",
            "Tool不在はProduct Capability不在ではない",
            {
                "toolAvailability": "unavailable",
                "productCapability": "unknown",
                "diagnostic": view_no_tool["dimensions"]["toolAvailability"].get("diagnostic"),
            },
        )

        record_data = {
            "schemaVersion": "tai.tei-capability-reference/scenario-record/v0",
            "date": utc_now(),
            "activity": view1["activity"],
            "command": (
                "python integrations/pilot-tei-capability-reference/run_scenarios.py "
                "--tei <tei> --workspace <workspace> "
                "--out evaluations/records/TAI-TEI-capability-reference-2026-11-11.json"
            ),
            "target": {
                "tei": {
                    "path": "<tei>",
                    "identity": view1["dimensions"]["toolAvailability"]["cli"],
                },
                "workspace": {
                    "path": "<workspace>",
                    "name": view1["source"]["workspace"].get("name"),
                    "manifestSha256": view1["source"]["workspace"].get("manifestSha256"),
                },
                "subject": DEFAULT_SUBJECT,
                "disclosureScope": view1["request"]["disclosureScope"],
                "mutation": "semantic/sales/order.tei に data OrderNote { attribute noteId type std.text } を追記（コピー上）",
            },
            "scenarios": scenarios,
            "result": "PASS" if all(item["result"] == "PASS" for item in scenarios) else "FAIL",
            "notRun": [
                "外部Harness SessionでのProduct Skill実Load",
                "実Tool実行・意味受理・実行権限",
                "実Consumer（別製品）への配送と受領",
                "実Workspace以外のSource、権限、OS隔離",
            ],
            "limits": [
                "PASSは読み取り参照と次元分離の範囲だけを示す。",
                "TEIのinspect/model overviewは派生物であり、活動判断や操作許可ではない。",
                "この記録は単一の公開Reference Workspaceと1つのActivityに対する観測である。",
            ],
        }
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"result": record_data["result"], "scenarios": [s["id"] for s in scenarios]}))
        return 0 if record_data["result"] == "PASS" else 1
    except AssertionError as exc:
        scenarios.append({"id": "FAIL", "title": str(exc), "result": "FAIL"})
        print(json.dumps({"result": "FAIL", "error": str(exc)}, ensure_ascii=False))
        return 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
