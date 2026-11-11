"""TAI側の最小能力参照経路。TEIの既存read-only CLIだけを呼ぶ。

このツールは製品の正本でも、第二のRegistryでも、共通Agent Hostでもない。
TAIが一つのActivityで「製品構成・能力参照・継続に必要な情報」を提示する
ための、選択したSubjectとDisclosure Scopeに限定した読み取り専用の写像である。

区別して保持する状態:

- Product Capability: TEIが宣言した意味要素として存在するか（declared/not-found/unknown）
- Tool availability: 実CLIが起動し、JSON契約を返したか（available/unavailable）
- Skill load: TEI Product Skillを実際にロードした観測があるか（not-observed）
- Execution authority: 操作・実行の許可があるか（not-evaluated / not-granted）
- Consumer receipt: 消費者がどのRevisionを受け取ったか（not-delivered / received）

TEIの候補・診断はTAIの活動判断や操作許可へ自動昇格しない。`promotion`は常に
`not-performed` / `not-made` / `not-granted`を返す。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VIEW_SCHEMA = "tai.tei-capability-reference/view/v0"
HANDOFF_SCHEMA = "tai.tei-capability-reference/handoff/v0"
RECEIPT_SCHEMA = "tai.tei-capability-reference/consumer-receipt/v0"
CHECK_SCHEMA = "tai.tei-capability-reference/consumer-check/v0"
DELTA_SCHEMA = "tai.tei-capability-reference/revision-delta/v0"

SELECTABLE_SECTIONS = ("definition", "dependencies", "source")
CAPABILITY_KIND = "semantic-capability"

# 消費者へ渡してよい鍵だけを列挙する。会話、Workspace全体、Raw bytes は含めない。
HANDOFF_KEYS = {
    "schemaVersion",
    "handoffId",
    "createdAt",
    "activity",
    "consumer",
    "selection",
    "source",
    "capabilities",
    "authority",
    "limits",
}

PROMOTION = {
    "teiCandidateToTaiDecision": "not-performed",
    "teiDiagnosticToOperationPermission": "not-performed",
    "activityDecision": "not-made",
    "operationPermission": "not-granted",
}


class ToolError(RuntimeError):
    """入力またはCLI結果が、安全に解釈できない状態。"""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_digest(value: Any) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(data.encode("utf-8")).hexdigest()


def digest_without(value: dict, key: str) -> str:
    return canonical_digest({k: v for k, v in value.items() if k != key})


def sanitize_argv(args: list[str], tei: str, workspace: str | None) -> list[str]:
    out: list[str] = []
    for arg in args:
        if tei and arg == tei:
            out.append("<tei>")
        elif workspace and arg == workspace:
            out.append("<workspace>")
        else:
            out.append(arg)
    return out


class TeiRunner:
    def __init__(self, tei: str) -> None:
        self.tei = tei
        self.calls: list[dict[str, Any]] = []

    def run(self, args: list[str], workspace: str | None) -> dict[str, Any]:
        argv = [self.tei] + args
        record: dict[str, Any] = {
            "argv": sanitize_argv(args, self.tei, workspace),
        }
        try:
            proc = subprocess.run(argv, capture_output=True, check=False)
        except OSError as exc:
            record.update({"exitCode": None, "invocationError": str(exc), "payload": None})
            self.calls.append(record)
            return record

        stdout = proc.stdout.decode("utf-8", "replace")
        stderr = proc.stderr.decode("utf-8", "replace")
        payload: Any = None
        if stdout.strip():
            try:
                payload = json.loads(stdout)
            except json.JSONDecodeError:
                payload = None
        record.update(
            {
                "exitCode": proc.returncode,
                "payload": payload,
                "stdoutHead": stdout[:2000],
                "stderrHead": stderr[:2000],
            }
        )
        self.calls.append(record)
        return record

    def identity(self) -> dict[str, Any]:
        result = self.run(["version", "-json"], None)
        payload = result.get("payload")
        available = (
            result.get("exitCode") == 0
            and isinstance(payload, dict)
            and payload.get("schemaVersion") == "tei.cli.version/v0"
            and bool(payload.get("vcsRevision") or payload.get("goVersion"))
        )
        identity = {
            "state": "available" if available else "unavailable",
            "observedBy": "tei version -json",
            "exitCode": result.get("exitCode"),
            "cli": payload if isinstance(payload, dict) else None,
        }
        if not available:
            identity["diagnostic"] = (
                result.get("invocationError")
                or (payload or {}).get("error")
                or (result.get("stderrHead") or "").strip()
                or "the TEI CLI did not answer the version contract"
            )
        return identity


def error_code_of(payload: Any) -> str | None:
    if isinstance(payload, dict) and payload.get("ok") is False:
        error = payload.get("error")
        if isinstance(error, dict):
            return error.get("code")
    return None


def result_of(record: dict[str, Any]) -> dict[str, Any] | None:
    payload = record.get("payload")
    if isinstance(payload, dict) and payload.get("ok") is True:
        result = payload.get("result")
        if isinstance(result, dict):
            return result
    return None


def limited_entries(entries: list[dict[str, Any]], limit: int) -> tuple[list[dict[str, Any]], bool]:
    return entries[:limit], len(entries) > limit


def composition_view(overview: dict[str, Any] | None, catalog: dict[str, Any] | None, limit: int) -> dict[str, Any]:
    composition: dict[str, Any] = {
        "basis": "tei model overview",
        "limit": limit,
        "state": "unavailable",
        "sections": [],
        "declarationCounts": None,
        "coverage": None,
    }
    if catalog:
        composition["declarationCounts"] = catalog.get("declarationCounts")
    if overview:
        sections = []
        for section in overview.get("sections") or []:
            entry = section.get("entry") or {}
            subject = entry.get("subject") or {}
            attention = section.get("attention") or {}
            sections.append(
                {
                    "kind": subject.get("kind"),
                    "id": subject.get("id"),
                    "descendants": section.get("descendants"),
                    "needsAttention": attention.get("needsAttention"),
                }
            )
        limited, truncated = limited_entries(sections, limit)
        composition.update(
            {
                "state": "observed",
                "sectionTotal": overview.get("sectionTotal"),
                "sectionsOmitted": overview.get("sectionsOmitted"),
                "sections": limited,
                "sectionsTruncated": truncated,
                "coverage": overview.get("sectionScope"),
            }
        )
    return composition


def capability_list_view(catalog: dict[str, Any] | None, limit: int) -> dict[str, Any]:
    if not catalog:
        return {"state": "unavailable", "total": None, "truncated": None, "subjects": []}
    entries = [
        entry
        for entry in catalog.get("entries") or []
        if (entry.get("subject") or {}).get("kind") == CAPABILITY_KIND
    ]
    limited, truncated = limited_entries(entries, limit)
    return {
        "state": "observed",
        "total": len(entries),
        "truncated": truncated,
        "subjects": [entry.get("subject") for entry in limited],
    }


def trace_view(record: dict[str, Any]) -> dict[str, Any]:
    result = result_of(record)
    if result is None:
        return {"state": "unavailable", "diagnostic": error_code_of(record.get("payload"))}
    trace = result.get("trace") or {}
    return {
        "state": "observed",
        "snapshotFingerprint": result.get("snapshotFingerprint"),
        "projectionUnresolved": result.get("projectionUnresolved") or [],
        "total": trace.get("total"),
        "authority": trace.get("authority"),
    }


def inspect_view(record: dict[str, Any]) -> dict[str, Any]:
    result = result_of(record)
    if result is None:
        code = error_code_of(record.get("payload"))
        state = "not-found" if code == "SUBJECT_NOT_FOUND" else "unknown"
        return {
            "state": state,
            "error": (record.get("payload") or {}).get("error") if isinstance(record.get("payload"), dict) else None,
            "exitCode": record.get("exitCode"),
        }
    return {
        "state": "declared",
        "canonical": result.get("canonical"),
        "sources": result.get("sources"),
        "authorityLimits": result.get("authorityLimits") or [],
        "worldFingerprint": result.get("worldFingerprint"),
        "sourceIndexFingerprint": result.get("sourceIndexFingerprint"),
    }


def disclosure_view(record: dict[str, Any]) -> dict[str, Any]:
    result = result_of(record)
    if result is None:
        return {"state": "unavailable", "diagnostic": error_code_of(record.get("payload"))}
    return {
        "state": result.get("status") or "unknown",
        "fingerprint": result.get("fingerprint"),
        "selected": result.get("selectedSections") or [],
        "disclosed": result.get("disclosedSections") or [],
        "omitted": result.get("omittedAvailableSections") or [],
        "available": result.get("availableSections") or [],
        "semanticElement": result.get("semanticElement"),
    }


def context_view(record: dict[str, Any]) -> dict[str, Any]:
    result = result_of(record)
    if result is None:
        return {"state": "unavailable", "diagnostic": error_code_of(record.get("payload"))}
    return {
        "state": "observed",
        "outgoing": result.get("outgoing") or [],
        "incoming": result.get("incoming") or [],
    }


def review_plan_view(record: dict[str, Any]) -> dict[str, Any]:
    result = result_of(record)
    if result is None:
        return {"state": "unavailable", "diagnostic": error_code_of(record.get("payload"))}
    return {
        "state": "observed",
        "fingerprint": result.get("fingerprint"),
        "purpose": result.get("purpose"),
        "routingScope": result.get("routingScope"),
        "reviewSequence": result.get("reviewSequence") or [],
        "stopRules": result.get("stopRules") or [],
        "authorityLimits": result.get("authorityLimits") or [],
    }


def parse_scope(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def check_disclosure(scope: list[str]) -> list[str]:
    if not scope:
        raise ToolError("disclosure scope is required; the whole workspace or conversation is never sent")
    unknown = [item for item in scope if item not in SELECTABLE_SECTIONS]
    if unknown:
        raise ToolError(f"unknown disclosure section(s): {', '.join(unknown)}")
    return scope


def observe(args: argparse.Namespace) -> dict[str, Any]:
    if not args.subject:
        raise ToolError("at least one --subject <kind>:<id> is required")
    subjects = []
    for raw in args.subject:
        kind, _, subject_id = raw.partition(":")
        if not kind or not subject_id:
            raise ToolError(f"subject must be <kind>:<id>: {raw!r}")
        subjects.append({"kind": kind, "id": subject_id})
    if len(subjects) > args.max_subjects:
        raise ToolError(f"at most {args.max_subjects} subjects per observation")
    scope = check_disclosure(parse_scope(args.disclosure))

    runner = TeiRunner(args.tei)
    tool = runner.identity()

    overview_result = runner.run(
        ["model", "overview", "-workspace", args.workspace, "-limit", str(args.limit)], args.workspace
    )
    catalog_result = runner.run(["model", "catalog", "-workspace", args.workspace], args.workspace)
    overview = result_of(overview_result)
    catalog = result_of(catalog_result)

    request = {
        "from": "tai",
        "to": "tei",
        "transport": "cli",
        "selection": {"subjects": subjects},
        "disclosureScope": scope,
        "workspace": "<workspace>",
        "includesConversation": False,
        "includesWholeWorkspacePayload": False,
    }

    if tool["state"] != "available":
        return finish_view(
            args,
            tool,
            request,
            composition_view(None, None, args.limit),
            {"state": "unavailable", "total": None, "truncated": None, "subjects": []},
            [
                object_not_observed(subject, "unknown", "tool-unavailable: the TEI CLI did not answer")
                for subject in subjects
            ],
            runner,
        )

    capabilities = []
    for subject in subjects:
        base = ["-workspace", args.workspace, "-subject-kind", subject["kind"], "-subject-id", subject["id"]]
        inspect_record = runner.run(["inspect"] + base, args.workspace)
        inspect = inspect_view(inspect_record)
        item: dict[str, Any] = {
            "subject": subject,
            "productCapability": inspect,
            "activityContinuation": {"state": "not-available"},
        }
        if inspect["state"] == "declared":
            disclose_record = runner.run(
                ["knowledge-context"] + base + ["-disclose", ",".join(scope)], args.workspace
            )
            context_record = runner.run(["knowledge-context"] + base, args.workspace)
            plan_record = runner.run(["knowledge-review-plan"] + base, args.workspace)
            trace_record = runner.run(["trace"] + base + ["-scope", "current"], args.workspace)
            item["disclosure"] = disclosure_view(disclose_record)
            item["dependencies"] = context_view(context_record)
            item["activityContinuation"] = {
                "state": "observed",
                "reviewPlan": review_plan_view(plan_record),
                "trace": trace_view(trace_record),
            }
        capabilities.append(item)

    return finish_view(
        args,
        tool,
        request,
        composition_view(overview, catalog, args.limit),
        capability_list_view(catalog, args.limit),
        capabilities,
        runner,
    )


def object_not_observed(subject: dict[str, Any], state: str, reason: str) -> dict[str, Any]:
    return {
        "subject": subject,
        "productCapability": {"state": state, "reason": reason},
        "activityContinuation": {"state": "not-available"},
    }


def finish_view(
    args: argparse.Namespace,
    tool: dict[str, Any],
    request: dict[str, Any],
    composition: dict[str, Any],
    capability_list: dict[str, Any],
    capabilities: list[dict[str, Any]],
    runner: TeiRunner,
) -> dict[str, Any]:
    states = [item["productCapability"].get("state") for item in capabilities]
    if tool["state"] != "available":
        product_state = "unknown"
    elif all(state == "declared" for state in states):
        product_state = "declared"
    elif any(state == "declared" for state in states):
        product_state = "partially-declared"
    elif states and all(state == "not-found" for state in states):
        product_state = "not-found"
    else:
        product_state = "unknown"

    authority_limits: list[str] = []
    for item in capabilities:
        for limit in item.get("productCapability", {}).get("authorityLimits") or []:
            if limit not in authority_limits:
                authority_limits.append(limit)
        for limit in (item.get("activityContinuation", {}).get("reviewPlan") or {}).get("authorityLimits") or []:
            if limit not in authority_limits:
                authority_limits.append(limit)

    # 同じ実行内で返った版だけを採用する。後段のコマンドが同じ版を返す場合は
    # 最初に見つかった値（model overview / model catalog）を優先する。
    revision: dict[str, Any] = {}
    for call in runner.calls:
        result = result_of(call)
        if not result:
            continue
        for key in ("worldFingerprint", "sourceIndexFingerprint", "modelRevision"):
            if not revision.get(key) and result.get(key):
                revision[key] = result.get(key)

    workspace_view: dict[str, Any] = {"path": "<workspace>"}
    for call in runner.calls:
        result = result_of(call)
        if result and isinstance(result.get("workspace"), dict):
            workspace = result["workspace"]
            workspace_view = {
                "path": "<workspace>",
                "name": workspace.get("name"),
                "formatVersion": workspace.get("formatVersion"),
                "manifestPath": (workspace.get("manifest") or {}).get("path"),
                "manifestSha256": (workspace.get("manifest") or {}).get("sha256"),
            }
            break

    view = {
        "schemaVersion": VIEW_SCHEMA,
        "observedAt": args.observed_at or utc_now(),
        "activity": {"id": args.activity, "purpose": "activity-continuation-reference"},
        "request": request,
        "source": {
            "product": "tei",
            "workspace": workspace_view,
            "revision": revision,
        },
        "productComposition": composition,
        "capabilityCandidates": capability_list,
        "capabilities": capabilities,
        "dimensions": {
            "productCapability": {
                "state": product_state,
                "basis": "tei inspect -subject-kind -subject-id",
                "subjects": states,
            },
            "toolAvailability": tool,
            "skillLoad": {
                "state": "not-observed",
                "productSkill": {
                    "name": "yi-tei-modeling",
                    "reference": "tei-platform/skills/yi-tei-modeling/SKILL.md",
                },
                "note": "CLI実行の成功はProduct Skillのロード証跡ではない。実LoadはHarness Sessionの証跡で別に判定する。",
            },
            "executionAuthority": {
                "state": "not-evaluated",
                "grantsRequested": "none",
                "readOnlyCommandsOnly": True,
                "authorityLimits": authority_limits,
            },
            "consumerReceipt": {
                "state": "not-delivered",
                "delivery": "explicit handoff required",
            },
        },
        "promotion": dict(PROMOTION),
        "limitations": [
            "TEIのinspect/model overview/model catalogは派生物であり、意味受理・業務完了・書込み権限ではない。",
            "Product Capabilityのdeclaredは、そのActivityでの利用可否・実行権限・Consumer受領を意味しない。",
            "Product Skillのロード、実Tool実行、外部Harness接続はこのツールの観測範囲外である。",
            "model overviewが覆わない種別（plugin/database/release等）はsectionScope.notCoveredKindsのとおり製品構成の一部に過ぎない。",
            "not-foundは指定IDの不在であり、製品全体に能力が無いことの証明ではない。",
        ],
    }
    view["cli"] = {
        "calls": [call["argv"] for call in runner.calls],
    }
    return view


def load_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str | None, value: dict[str, Any]) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def render_markdown(view: dict[str, Any]) -> str:
    dimensions = view["dimensions"]
    lines = [
        "# TEI能力参照（TAI側の表示）",
        "",
        f"- 観測: {view['observedAt']}",
        f"- Activity: {view['activity']['id']}",
        f"- 選択: {', '.join(s['kind'] + ':' + s['id'] for s in view['request']['selection']['subjects'])}",
        f"- Disclosure Scope: {', '.join(view['request']['disclosureScope'])}",
        f"- Workspace: {view['source']['workspace'].get('name')} "
        f"({view['source']['workspace'].get('manifestSha256')})",
        f"- Revision: world={view['source']['revision'].get('worldFingerprint')}",
        "",
        "| 次元 | 状態 | 意味 |",
        "| --- | --- | --- |",
        f"| Product Capability | {dimensions['productCapability']['state']} | TEIが宣言した意味要素として存在するか |",
        f"| Tool availability | {dimensions['toolAvailability']['state']} | 実CLIがJSON契約を返したか |",
        f"| Skill load | {dimensions['skillLoad']['state']} | Product Skillの実ロードを観測したか |",
        f"| Execution authority | {dimensions['executionAuthority']['state']} | 操作・実行の許可があるか |",
        f"| Consumer receipt | {dimensions['consumerReceipt']['state']} | 消費者がRevisionを受け取ったか |",
        "",
        "## 能力一覧（限定）",
        "",
    ]
    candidates = view["capabilityCandidates"]
    if candidates["state"] != "observed":
        lines.append("- 一覧を取得できていない（ToolまたはWorkspaceの状態を確認する）。")
    else:
        for subject in candidates["subjects"]:
            lines.append(f"- `{subject['kind']}:{subject['id']}`")
        if candidates.get("truncated"):
            lines.append(f"- ほか {candidates['total'] - len(candidates['subjects'])} 件（表示上限）")
    lines.extend(["", "## 選択した能力", ""])
    for item in view["capabilities"]:
        capability = item["productCapability"]
        lines.append(f"### `{item['subject']['kind']}:{item['subject']['id']}`")
        lines.append("")
        lines.append(f"- Product Capability: {capability['state']}")
        if capability["state"] == "declared":
            canonical = capability.get("canonical") or {}
            lines.append(f"- 定義: 入力 {canonical.get('inputs')} / 出力 {canonical.get('output')}")
            sources = capability.get("sources") or {}
            for artifact in sources.get("artifacts") or []:
                lines.append(f"- Source: `{artifact['path']}` ({artifact['fingerprint']})")
            plan = (item.get("activityContinuation") or {}).get("reviewPlan") or {}
            if plan.get("fingerprint"):
                lines.append(f"- 継続用Review Plan: {plan['fingerprint']}")
            trace = (item.get("activityContinuation") or {}).get("trace") or {}
            if trace.get("snapshotFingerprint"):
                lines.append(f"- Trace snapshot: {trace['snapshotFingerprint']}")
        else:
            error = capability.get("error") or {}
            lines.append(f"- 診断: {error.get('code') or capability.get('reason')}")
        lines.append("")
    lines.extend(
        [
            "## 昇格しないもの",
            "",
            "- TEI候補 → TAI活動判断: しない",
            "- TEI診断 → 操作許可: しない",
            f"- Activity判断: {view['promotion']['activityDecision']}",
            f"- 操作許可: {view['promotion']['operationPermission']}",
            "",
        ]
    )
    return "\n".join(lines)


def build_handoff(args: argparse.Namespace) -> dict[str, Any]:
    view = load_json(args.view)
    if view.get("schemaVersion") != VIEW_SCHEMA:
        raise ToolError("view has an unexpected schemaVersion")
    scope = check_disclosure(parse_scope(args.disclosure))
    subjects = view["request"]["selection"]["subjects"]
    selected = {f"{s['kind']}:{s['id']}" for s in subjects}
    capabilities = [
        item
        for item in view.get("capabilities") or []
        if f"{item['subject']['kind']}:{item['subject']['id']}" in selected
    ]
    artifacts: list[dict[str, Any]] = []
    for item in capabilities:
        for artifact in (item.get("productCapability", {}).get("sources") or {}).get("artifacts") or []:
            artifacts.append({"path": artifact.get("path"), "fingerprint": artifact.get("fingerprint")})
    trace_snapshots = {}
    for item in capabilities:
        trace = (item.get("activityContinuation") or {}).get("trace") or {}
        if trace.get("snapshotFingerprint"):
            trace_snapshots[f"{item['subject']['kind']}:{item['subject']['id']}"] = trace["snapshotFingerprint"]

    envelope = {
        "schemaVersion": HANDOFF_SCHEMA,
        "handoffId": None,
        "createdAt": args.created_at or utc_now(),
        "activity": view.get("activity"),
        "consumer": {"id": args.consumer},
        "selection": {"subjects": subjects, "disclosureScope": scope},
        "source": {
            "product": "tei",
            "workspace": view["source"]["workspace"],
            "revision": view["source"]["revision"],
            "artifacts": artifacts,
            "traceSnapshots": trace_snapshots,
        },
        "capabilities": [
            {
                "subject": item["subject"],
                "productCapability": item["productCapability"].get("state"),
                "disclosure": item.get("disclosure"),
            }
            for item in capabilities
        ],
        "authority": {
            "readOnly": True,
            "operationPermission": "not-granted",
            "activityDecision": "not-made",
        },
        "limits": [
            "このHandoffは選択・Source・Revision・Disclosure Scopeだけを運ぶ。会話やWorkspace全体は含まない。",
            "受領は能力の現在資格・実行権限・活動判断を意味しない。",
            "Revisionが変わった場合は再資格化が必要で、古い結果を暗黙に再利用しない。",
        ],
    }
    envelope["handoffId"] = digest_without(envelope, "handoffId")
    envelope["envelopeDigest"] = digest_without(envelope, "envelopeDigest")
    unexpected = set(envelope) - HANDOFF_KEYS - {"envelopeDigest"}
    if unexpected:
        raise ToolError(f"handoff leaked unexpected keys: {sorted(unexpected)}")
    return envelope


def build_receipt(args: argparse.Namespace) -> dict[str, Any]:
    envelope = load_json(args.envelope)
    if envelope.get("schemaVersion") != HANDOFF_SCHEMA:
        raise ToolError("envelope has an unexpected schemaVersion")
    expected = digest_without(envelope, "envelopeDigest")
    if envelope.get("envelopeDigest") != expected:
        raise ToolError("envelope digest does not match its content")
    if envelope.get("consumer", {}).get("id") != args.consumer:
        raise ToolError("receipt consumer does not match the handoff consumer")
    return {
        "schemaVersion": RECEIPT_SCHEMA,
        "consumer": {"id": args.consumer},
        "receivedAt": args.received_at or utc_now(),
        "envelopeDigest": envelope["envelopeDigest"],
        "activity": envelope.get("activity"),
        "selection": envelope["selection"],
        "revision": envelope["source"]["revision"],
        "artifacts": envelope["source"]["artifacts"],
        "traceSnapshots": envelope["source"]["traceSnapshots"],
        "state": "received",
        "note": "受領は現在資格・実行権限・活動判断ではない。",
    }


def compare_views(args: argparse.Namespace) -> dict[str, Any]:
    before = load_json(args.before)
    after = load_json(args.after)
    if before.get("schemaVersion") != VIEW_SCHEMA or after.get("schemaVersion") != VIEW_SCHEMA:
        raise ToolError("both inputs must be capability-reference views")
    before_subjects = {f"{s['kind']}:{s['id']}" for s in before["request"]["selection"]["subjects"]}
    after_subjects = {f"{s['kind']}:{s['id']}" for s in after["request"]["selection"]["subjects"]}
    states_after = [item["productCapability"].get("state") for item in after.get("capabilities") or []]
    before_tool = (before.get("dimensions") or {}).get("toolAvailability", {}).get("state")
    after_tool = (after.get("dimensions") or {}).get("toolAvailability", {}).get("state")

    changed: list[str] = []
    before_revision = before["source"]["revision"]
    after_revision = after["source"]["revision"]
    for key in ("worldFingerprint", "sourceIndexFingerprint", "modelRevision"):
        if before_revision.get(key) != after_revision.get(key):
            changed.append(key)

    def artifact_map(view: dict[str, Any]) -> dict[tuple[str, str], str]:
        found = {}
        for item in view.get("capabilities") or []:
            subject = f"{item['subject']['kind']}:{item['subject']['id']}"
            for artifact in (item.get("productCapability", {}).get("sources") or {}).get("artifacts") or []:
                found[(subject, artifact.get("path"))] = artifact.get("fingerprint")
        return found

    before_artifacts = artifact_map(before)
    after_artifacts = artifact_map(after)
    artifact_changes = []
    for key in sorted(set(before_artifacts) | set(after_artifacts)):
        if before_artifacts.get(key) != after_artifacts.get(key):
            artifact_changes.append(
                {"subject": key[0], "path": key[1], "before": before_artifacts.get(key), "after": after_artifacts.get(key)}
            )
    if artifact_changes:
        changed.append("artifacts")

    if before_tool != "available" or after_tool != "available":
        state = "incomparable-tool-unavailable"
    elif before_subjects != after_subjects:
        state = "incomparable-selection-changed"
    elif any(value == "not-found" for value in states_after):
        state = "target-not-found"
    elif changed:
        state = "source-updated"
    else:
        state = "unchanged"

    return {
        "schemaVersion": DELTA_SCHEMA,
        "comparedAt": args.compared_at or utc_now(),
        "activity": after.get("activity"),
        "before": {"observedAt": before.get("observedAt"), "revision": before_revision},
        "after": {"observedAt": after.get("observedAt"), "revision": after_revision},
        "state": state,
        "changed": changed,
        "artifactChanges": artifact_changes,
        "requalificationRequired": state in ("source-updated", "target-not-found"),
        "promotion": dict(PROMOTION),
    }


def verify_consumer(args: argparse.Namespace) -> dict[str, Any]:
    receipt = load_json(args.receipt)
    if receipt.get("schemaVersion") != RECEIPT_SCHEMA:
        raise ToolError("receipt has an unexpected schemaVersion")
    subjects = receipt["selection"]["subjects"]
    runner = TeiRunner(args.tei)
    tool = runner.identity()
    if tool["state"] != "available":
        return finish_check(receipt, "tool-unavailable", tool, [], "stop-and-report-tool-unavailable")

    diagnostics: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    states = []
    for subject in subjects:
        base = ["-workspace", args.workspace, "-subject-kind", subject["kind"], "-subject-id", subject["id"]]
        inspect_record = runner.run(["inspect"] + base, args.workspace)
        inspect = inspect_view(inspect_record)
        states.append(inspect["state"])
        if inspect["state"] != "declared":
            diagnostics.append({"command": "inspect", "subject": subject, "error": inspect.get("error")})
            continue
        current[f"{subject['kind']}:{subject['id']}"] = {
            "worldFingerprint": inspect.get("worldFingerprint"),
            "sourceIndexFingerprint": inspect.get("sourceIndexFingerprint"),
            "artifacts": [
                {"path": a.get("path"), "fingerprint": a.get("fingerprint")}
                for a in (inspect.get("sources") or {}).get("artifacts") or []
            ],
        }
        # traceのexpected-fingerprintは外側result.snapshotFingerprintと比較する。
        expected = (receipt.get("traceSnapshots") or {}).get(f"{subject['kind']}:{subject['id']}")
        if expected:
            trace_record = runner.run(
                ["trace"] + base + ["-scope", "current", "-expected-fingerprint", expected], args.workspace
            )
            code = error_code_of(trace_record.get("payload"))
            if code:
                diagnostics.append({"command": "trace", "subject": subject, "error": code})

    if any(state == "not-found" for state in states):
        return finish_check(receipt, "target-not-found", tool, diagnostics, "stop-and-report-missing-target")

    revision_matches = True
    for subject in subjects:
        key = f"{subject['kind']}:{subject['id']}"
        observed = current.get(key)
        if not observed:
            revision_matches = False
            continue
        if observed["worldFingerprint"] != receipt["revision"].get("worldFingerprint"):
            revision_matches = False
        if observed["sourceIndexFingerprint"] != receipt["revision"].get("sourceIndexFingerprint"):
            revision_matches = False
    current_artifacts = {
        (artifact.get("path"), artifact.get("fingerprint"))
        for observed in current.values()
        for artifact in observed.get("artifacts") or []
    }
    received_artifacts = {
        (artifact.get("path"), artifact.get("fingerprint")) for artifact in receipt.get("artifacts") or []
    }
    if current_artifacts != received_artifacts:
        revision_matches = False
    stale_diagnostic = any(item.get("error") == "STALE_SNAPSHOT" for item in diagnostics)
    if revision_matches and not stale_diagnostic:
        return finish_check(receipt, "fresh", tool, diagnostics, "none")
    return finish_check(receipt, "stale", tool, diagnostics, "requalification-required")


def finish_check(
    receipt: dict[str, Any], state: str, tool: dict[str, Any], diagnostics: list[dict[str, Any]], action: str
) -> dict[str, Any]:
    return {
        "schemaVersion": CHECK_SCHEMA,
        "checkedAt": utc_now(),
        "activity": receipt.get("activity"),
        "consumer": receipt.get("consumer"),
        "state": state,
        "consumerAction": action,
        "requalificationRequired": state in ("stale", "target-not-found"),
        "teiDiagnostics": diagnostics,
        "toolAvailability": tool,
        "receivedRevision": receipt.get("revision"),
        "promotion": dict(PROMOTION),
        "limits": [
            "この判定は参照Revisionの一致だけを扱い、意味の現在資格・実行権限・活動判断を決めない。",
            "freshは能力の利用許可ではなく、staleは活動の停止判断そのものでもない。",
        ],
    }


def add_observe_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tei", required=True, help="TEI CLI executable")
    parser.add_argument("--workspace", required=True, help="TEI workspace path")
    parser.add_argument("--subject", action="append", default=[], help="<kind>:<id>; repeatable")
    parser.add_argument(
        "--disclosure",
        required=True,
        help="comma separated disclosure sections: definition,dependencies,source",
    )
    parser.add_argument("--limit", type=int, default=20, help="limit for composition/capability lists")
    parser.add_argument("--max-subjects", type=int, default=5)
    parser.add_argument("--activity", default="TAI-ACT-TEI-CAPABILITY-REFERENCE-01")
    parser.add_argument("--observed-at", default=None)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--out", default=None)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    observe_parser = sub.add_parser("observe", help="read a bounded capability reference from TEI")
    add_observe_arguments(observe_parser)

    handoff_parser = sub.add_parser("handoff", help="build a bounded TAI-to-consumer handoff")
    handoff_parser.add_argument("--view", required=True)
    handoff_parser.add_argument("--consumer", required=True)
    handoff_parser.add_argument("--disclosure", required=True)
    handoff_parser.add_argument("--created-at", default=None)
    handoff_parser.add_argument("--out", default=None)

    receipt_parser = sub.add_parser("receipt", help="record a consumer receipt for a handoff")
    receipt_parser.add_argument("--envelope", required=True)
    receipt_parser.add_argument("--consumer", required=True)
    receipt_parser.add_argument("--received-at", default=None)
    receipt_parser.add_argument("--out", default=None)

    compare_parser = sub.add_parser("compare", help="compare two observations of the same activity")
    compare_parser.add_argument("--before", required=True)
    compare_parser.add_argument("--after", required=True)
    compare_parser.add_argument("--compared-at", default=None)
    compare_parser.add_argument("--out", default=None)

    verify_parser = sub.add_parser("verify-consumer", help="check a received revision against the current TEI")
    verify_parser.add_argument("--receipt", required=True)
    verify_parser.add_argument("--tei", required=True)
    verify_parser.add_argument("--workspace", required=True)
    verify_parser.add_argument("--out", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "observe":
            view = observe(args)
            if args.format == "markdown":
                text = render_markdown(view) + "\n"
                if args.out:
                    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
                    Path(args.out).write_text(text, encoding="utf-8")
                else:
                    sys.stdout.write(text)
            else:
                write_json(args.out, view)
            return 0
        if args.command == "handoff":
            write_json(args.out, build_handoff(args))
            return 0
        if args.command == "receipt":
            write_json(args.out, build_receipt(args))
            return 0
        if args.command == "compare":
            write_json(args.out, compare_views(args))
            return 0
        if args.command == "verify-consumer":
            write_json(args.out, verify_consumer(args))
            return 0
    except ToolError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
