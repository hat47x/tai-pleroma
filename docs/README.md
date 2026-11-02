# 設計・判断資料

プロダクトの目的、用語、要件、機能設計、重要な判断と未決事項を扱います。

## YI ConstellationとTAIの統合・配布構想（Draft）

- [シリーズ統合・配布アーキテクチャ](product-family-delivery.md) — ファミリーブランド、TAI製品、TAIリポジトリ、個別製品の責務境界。
- [シリーズ統合ビルド・リリース要求／受入条件](product-family-release-requirements.md) — 固定版、構成別配布、負例と段階的Gate。
- [YI Constellationウェブサイトの情報設計](yi-constellation-website.md) — TAIリポジトリ内で制作するブランドサイトの情報構造と公開境界。
- [Issue #74](https://github.com/hat47x/tai-pleroma/issues/74) — 構想のOwner判断と受入追跡。

**いずれも提案段階**であり、現行のSCN-001参照実装・公開判断や[横断的Product分類のDraft PR #72](https://github.com/hat47x/tai-pleroma/pull/72)を置き換えません。

仮説・提案・受理済み・実装済み・検証済みを区別し、Issue・PRや関連基盤の根拠へリンクしてください。初期段階では採用済みのアーキテクチャを仮定しません。

- [人とAIの協働統治に向けた開発の焦点（Draft）](ai-human-cogovernance-development-plan.md) — 個人・組織・社会の価値検証を先行させる優先順位と責務境界。実施条件は[P-06評価](../evaluations/P-06-cogovernance-protocol.md)で定める。

## プロダクト横断の俯瞰と棚卸し（Draft）

- [プロダクト横断の全体像と関係図（Draft）](product-landscape.md) — 既存の五基盤とTAIの役割、横断俯瞰、調査範囲の限界。
- [プロダクト横断知識モデルと管理境界（Draft）](product-knowledge-model.md) — 型付き関係・根拠・状態・Revision・Owner境界と受入条件。

両文書はTAIへの横断情報集約の具体化案です。既存のSCN-001責務境界・接続実証の正本を置き換えません。

- [公開リポジトリの棚卸しとプロダクト候補（Draft）](product-inventory-candidates.md) — 固定main版に基づく公開対象の候補、SHO/MMIやCSWの分類保留、網羅性・公開境界。
- [横断プロダクト情報の受入・更新プロトコル（Draft）](product-landscape-acceptance.md) — scope、Evidence、Revision、公開境界、誤った確定を避ける負例。

- [Product Landscape 横断要求 v0（Draft）](product-landscape-requirements.md) — PL-REQ-01〜16、G1〜G3、要件・受入・Ownerのトレース。
- [Product Landscape View Contract v0（Draft）](product-landscape-view-contract.md) — Portfolio/Capability/Integrationの図の意味、版と公開の条件。

G1の正式な対象・分類・公開の採否は[TAI Issue #73](https://github.com/hat47x/tai-pleroma/issues/73)で追跡する。Issueと文書はいずれも現在**Draft・未受入**。

## 製品シリーズの概要

[YI Constellation 構想と設計（PowerPoint）](YI_Constellation.pptx)は、製品群の役割と境界、利用例、構想、2026年10月時点の確認範囲をまとめた資料です。各製品の最新の要件・設計・検証結果は、それぞれのリポジトリを参照してください。資料内の構想や過去の確認結果は、現在の実装や受入を示すものではありません。

## YI Constellation：価値観・要望・要件の研究（Draft）

- [価値観・要望・要件の往復設計](yi-constellation/value-needs-requirements-2026-11-01.md) — 構想・10価値領域・9要望・18要件候補。**研究提案であり正式な採用済み要件ではありません**。
- [価値の実現と検証の研究計画](yi-constellation/value-realization-research-protocol-2026-11-01.md) — 実質的な選択可能性、価値の緊張、個人/組織/社会の対照研究、既存シナリオへの対応。
- 既存の[PowerPoint構想資料](YI_Constellation.pptx)とは版と状態が異なります。Draft #72/#75/#81/#128/#169、TAI #73/#74/#127/#165〜168等のレビューと合わせて読み、Owner未受理の具体案を製品の正式契約として扱わないでください。

## 製品シリーズの分析

[YI Constellation 64卦システム分析](yi-constellation/README.md)は、TAIを中心とする製品シリーズを、易の64卦をシステム全体として読む分析です。要件候補、課題探索領域、計画、レビューを含みます。分析草稿であり、要件の受理や設計の採用を示しません。

## 横断的な証拠・引渡し境界（Draft）

- [ハーネス横断の認知・作用・証拠の境界](harness-evidence-boundary.md) — 外部ハーネスに引き継いでよい主張と、その裏付け・Owner・未観測を区別する非規範的設計。受入試験は[負例マトリクス](../evaluations/harness-boundary-negative-cases.md)を参照。

## 上流の整合

- [SCN-001「実行→検証→受理」の三視点整合](scn001-three-view-alignment.md)
- [TEIによるプロダクト構築への移行 — フィージビリティ検証計画](tei-construction-migration-plan.md)
