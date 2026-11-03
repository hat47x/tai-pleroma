---
name: yi-tai-activity
description: >-
  YI Constellationで、利用者の一つの課題をSEI/SUI/TEI/SHO/EKIなどの製品へ
  必要に応じて分担し、出典・未決・権限・結果を保って活動を続けるときに使う。
  単独製品で十分な場合はその製品のSkill/CLIを直接使い、横断処理を増やさない。
---

# TAI Activity：必要な製品を組み合わせる（配布前試作）

> **実Harness未検証／NOT RUN**。YI Constellationはブランドであり、TAI Skillは製品のCore・権限・認知Method・CLI・Scheduler・Hostではない。現在のCLI/Skill/MCP実接続、Source/Role/権限、成果物の受領は毎回必要に応じて実確認する。

## 起動判断：単独製品を優先

**一製品のCLI・API・既存Skillだけで依頼が完了するなら、このTAI Skillを使わない。** 複数の製品を一つの目的・出典・成果に沿って選択・引継ぎ・再確認する必要がある場合のみ使う。例：資料観測→問い相対の分析→モデル候補→文書化→必要な委任。

製品OwnerはそれぞれSEI（根拠・認知Method）、SUI（探索・意味候補）、TEI（意味モデル・CLI・生成）、SHO（執筆・Reader）、EKI（明示的な実Task委任）。MMIは既存 `skills/mmi` があるが、実Harnessと実Tool可用性は別に調べる。開発一般向け `skills/ponytail` を製品操作Skillと呼ばない。

## 実行手順

1. **目的と停止条件**：利用者が求める成果、対象・時点・Audience、許容Source、期限/予算/品質、Owner判断が必要な条件を特定。不要な製品・Tool・秘密は探索・送信しない。
2. **実在する経路だけを選ぶ**：現在のProduct CLI/API/MCP、Skillの実ロード/依存物、Build/Provider/Hostを照合。名前・説明・UI・CLI Catalogから存在、権限、効果を推測しない。足りない能力は `unknown/unavailable/unsupported/not-run` とする。
3. **根拠を用途へ結ぶ**：Source版・Occurrence・Scope/Grain・Role/Rule・時点・診断と未知をProductの実Observationに結ぶ。資料のURLは本文ではなく、0件は必ずしも不存在ではない。検証されたMeaningと候補を分ける。
4. **必要最小の連携**：Ownerが許可したProjectionと既存成果物参照だけを別Product/Harnessへ渡す。Tool名・非公開Capability件数・Plan/DOM/Log・外部送信も公開対象として考える。Raw・Grant・秘密・独立Oracleを自動転送しない。
5. **作用前の現在資格**：Action Purpose、対象Identity/Scope、Source/時点、Target版、現在のHost/Provider Grantを実作用の前に照合。Studio Reference ExecuteやCommand候補、EKI ACKはDB Commit/Body受領/BusinessVerifiedではない。結果不明時の無条件Retryをしない。
6. **期限・Quality・回復を別々に判断**：必要な完了期限、復旧余裕、課金経路、品質CheckSet/有効期限を区別。価格の安さは権限や期限を上書きしない。EKIを明示委任した場合だけEKIのLease/Attempt/Recovery契約へ引き継ぐ。
7. **実証可能な範囲を返す**：実際に読んだSource・呼んだTool/版、受け取ったResult/Artifact、診断・Owner未受理・開示/Effectの未知、残作業、次の必要なProduct確認を用途に必要な量だけ記録。別Harness再開時は履歴と現在資格を再確認。

## 必要なときだけ読む詳細

- **Product/入口・意味の選択**：TEIのCLI/Studio/UI/cron・組織Scope、SHO Research Index、Action Purpose、型付きConnectionを扱うときは[用途別の詳細](references/product-entrypoints.md)。
- **Source/Tool/Disclosure**：Tool/Skillの実ロード根拠、RLS/部分取得、Source改版、成果物公開、Planner/外部送出が問題になるときは[Sourceと開示の詳細](references/source-disclosure-evidence.md)。
- **変更後の再利用・期限**：Role/Provider/Source変更、Activityの別Session引継ぎ、Quality期限・EKI Recoveryが必要なときは[再資格化・期限の詳細](references/requalification-deadline-recovery.md)。

これらの詳細は**初回から全量をロードする必要はない**。必要な参照ファイルだけを使い、参照の実消費版を記録する。Harnessが参照を実ロードした証拠を、このMarkdownのリンクだけで代用しない。

## 回答の最小形

`目的/対象/時点`、`実使用Product・Tool・版`、`Sourceと確認した範囲`、`意味候補/採否`、`実Tool/Provider/Consumer結果`、`未知/未実施`、`次に必要な判断`を必要に応じて書く。歴史的PASSを現時点のGrantやBusiness Effectへ昇格しない。

## 関連・状態

- [YIC構成計画](../../../docs/yi-constellation/harness-skill-plugin-plan-2026-11-02.md)／[実評価SK-01](../../../evaluations/SK-01-harness-skills.md)／[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)
- [最小選択SK-MIN](../../../docs/yi-constellation/skill-composition-minimal-routing-scenarios-2026-11-02.md)／[SK-02 H2/H3](../../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)／[入口別SK-IV](../../../docs/yi-constellation/skill-entrypoint-ui-job-organization-boundaries-2026-11-03.md)

**配布前のTAI例示Skill**。新しい公開Tool/API/共通Host/Policy Engine/中央Registryは導入しない。実Harness install/load/invoke、二Harness比較・OS Egress・Owner受理は**NOT RUN**。
