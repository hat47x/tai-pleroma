# 設計・判断資料

プロダクトの目的、用語、要件、機能設計、重要な判断と未決事項を扱います。

## YI ConstellationとTAIの統合・配布構想（Draft）

- [シリーズ統合・配布アーキテクチャ](product-family-delivery.md) — ファミリーブランド、TAI製品、TAIリポジトリ、個別製品の責務境界。
- [シリーズ統合ビルド・リリース要求／受入条件](product-family-release-requirements.md) — 固定版、構成別配布、負例と段階的Gate。
- [YI Constellationウェブサイトの情報設計](yi-constellation-website.md) — TAIリポジトリ内で制作するブランドサイトの情報構造と公開境界。
- [Issue #74](https://github.com/hat47x/tai-pleroma/issues/74) — 構想のOwner判断と受入追跡。

**いずれも提案段階**であり、現行のSCN-001参照実装・公開判断や[横断的Product分類のDraft PR #72](https://github.com/hat47x/tai-pleroma/pull/72)（2026-11-02 merged）を置き換えません。

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
- [TAI全体像の横断読解ガイド v0（Draft）](tai-crossview-reader-guide-2026-11-09.md) — 利用目的から役割・Product選択・実証・配布・結果の各資料を混同せず辿るための読者用ガイド。

G1の正式な対象・分類・公開の採否は[TAI Issue #73](https://github.com/hat47x/tai-pleroma/issues/73)で追跡する。Issueと文書はいずれも現在**Draft・未受入**。

## 製品シリーズの概要

[YI Constellation 構想と設計（PowerPoint）](YI_Constellation.pptx)は、製品群の役割と境界、利用例、構想、2026年10月時点の確認範囲をまとめた資料です。各製品の最新の要件・設計・検証結果は、それぞれのリポジトリを参照してください。資料内の構想や過去の確認結果は、現在の実装や受入を示すものではありません。

## YI Constellation：価値観・要望・要件の研究（Draft）

- [価値観・要望・要件の往復設計](yi-constellation/value-needs-requirements-2026-11-01.md) — 構想・10価値領域・9要望・18要件候補。**研究提案であり正式な採用済み要件ではありません**。
- [価値の実現と検証の研究計画](yi-constellation/value-realization-research-protocol-2026-11-01.md) — 実質的な選択可能性、価値の緊張、個人/組織/社会の対照研究、既存シナリオへの対応。
- 既存の[PowerPoint構想資料](YI_Constellation.pptx)とは版と状態が異なります。Draft #72/#75/#81/#128/#169（いずれも2026-11-02 merged）、TAI #73/#74/#127/#165〜168等のレビューと合わせて読み、Owner未受理の具体案を製品の正式契約として扱わないでください。

## 製品シリーズの分析

[YI Constellation 64卦システム分析](yi-constellation/README.md)は、TAIを中心とする製品シリーズを、易の64卦をシステム全体として読む分析です。要件候補、課題探索領域、計画、レビューを含みます。分析草稿であり、要件の受理や設計の採用を示しません。

- [YI ConstellationのTEI移行適合性と初回検証計画](../analysis/yi-constellation-tei-fit-gap-2026-11.md) — 7製品のFit/Gap、依存関係、移行方式の比較、独立Expected、初回の小規模検証計画。実装置換は行わない。

## 横断的な証拠・引渡し境界（Draft）

- [ハーネス横断の認知・作用・証拠の境界](harness-evidence-boundary.md) — 外部ハーネスに引き継いでよい主張と、その裏付け・Owner・未観測を区別する非規範的設計。受入試験は[負例マトリクス](../evaluations/harness-boundary-negative-cases.md)を参照。

## 上流の整合

- [SCN-001「実行→検証→受理」の三視点整合](scn001-three-view-alignment.md)
- [TEIによるプロダクト構築への移行 — フィージビリティ検証計画](tei-construction-migration-plan.md)

<!-- doc-index:begin -->

以下は各文書の先頭見出しから生成した。**手で保たない。**
対象: `docs` 直下の `*.md`（READMEを除く27件）。

| 文書 | 題 | 状態 |
| --- | --- | --- |
| [ai-human-cogovernance-development-plan.md](ai-human-cogovernance-development-plan.md) | 人と生成AIの協働統治に向けた開発の焦点（Draft） | **Proposed / Owner受入待ち / 利用者評価NOT RUN** |
| [architecture-slice-001.md](architecture-slice-001.md) | 最初の知的機能スライス：責務境界 | **Draft（設計案・未採用／未実証）** |
| [critical-path-2026-10.md](critical-path-2026-10.md) | TAI中心のクリティカルパス（2026-10） | **Draft（計画・参照実装の記録）**。5基盤への参照接続は追加済みですが、実製品間の通し接続、人間の承認、利用者価 |
| [harness-capability-lifecycle-2026-10.md](harness-capability-lifecycle-2026-10.md) | TAIシリーズの能力増幅・縮退適性と横断実証計画（2026-10-30） | **Draft / Proposed**。SW-01 S1に限定合成実測あり（OpenCode Aは同一モデル計3回、既 |
| [harness-evidence-boundary.md](harness-evidence-boundary.md) | ハーネス横断の認知・作用・証拠の境界（設計案） | **Draft / 非規範 / 提案、実際のハーネス間統合は未受入** |
| [meaning-change-runbook.md](meaning-change-runbook.md) | 意味変更の進め方（2026-11-06） | — |
| [product-family-delivery.md](product-family-delivery.md) | YI ConstellationとTAIの製品群統合・配布アーキテクチャ（Draft v0） | **Proposed / Ownerレビュー待ち / 実装・統合リリースNOT RUN** |
| [product-family-release-requirements.md](product-family-release-requirements.md) | シリーズ統合ビルド・リリース要求／受入条件（Draft v0） | **すべて提案／NOT RUN**。製品間の統合ビルドや公開Releaseが成立したという報告ではない。 |
| [product-inventory-candidates.md](product-inventory-candidates.md) | 公開リポジトリの棚卸しとプロダクト候補（v0） | **Draft / 調査記録。製品としての分類・TAIの管理対象範囲・相互接続は未採用／未実証を含む。** |
| [product-knowledge-model.md](product-knowledge-model.md) | プロダクト横断知識モデルと管理境界 v0 | **Draft / 提案**。横断情報をTAIへ集約するという方向性と、以下の具体的なスキーマ・運用・検査規則の採用判断 |
| [product-landscape-acceptance.md](product-landscape-acceptance.md) | 横断プロダクト情報の受入・更新プロトコル（提案 v0） | **Draft / NOT RUN**。本書はTAIの製品群カタログと図が満たすべき条件の**提案**であり、現行実装や |
| [product-landscape-requirements.md](product-landscape-requirements.md) | Product Landscape 横断要求 v0（提案・未採用） | **Draft / Proposed / acceptance NOT RUN**。この文書は製品群の位置づけをTAIへ |
| [product-landscape-view-contract.md](product-landscape-view-contract.md) | Product Landscape View Contract v0 — 三つの図を混同しないための設計 | **Draft / 提案 / renderer・validator未実装**。 |
| [product-landscape.md](product-landscape.md) | プロダクト横断の全体像と関係図（Product Landscape v0） | **Draft — 横断情報をTAIに集約する方針の設計提案。製品分類・関係型・接続方式は未採用／未実証を含む。** |
| [re-observation-plan.md](re-observation-plan.md) | 再観測の準備（2026-11-06） | — |
| [reproduction-runbook.md](reproduction-runbook.md) | 再現手順（2026-11-06） | — |
| [roadmap.md](roadmap.md) | 初期PoCの作業順序 | **Proposed（Owner受理待ち）**。直近の計画案であり、導入済み機能やコミット済みの実行結果を示さない。 |
| [SCN-001-owner-review-packet.md](SCN-001-owner-review-packet.md) | SCN-001 Owner review packet（development review） | **development review accepted / publication blocked**。 |
| [scn001-three-view-alignment.md](scn001-three-view-alignment.md) | SCN-001「実行→検証→受理」の三視点整合 | **Draft（上流の整理）**。方法の定義は[EKI ADR-0033](https://github.com/hat |
| [status.md](status.md) | TAI Pleromaの現在状態 | — |
| [sui-api-boundary-tei-mapping.md](sui-api-boundary-tei-mapping.md) | SUIのAPI境界とTEI投影の接続案 | — |
| [sui-documentv1-tei-gap.md](sui-documentv1-tei-gap.md) | SUI DocumentV1 とTEIパイロット投影の差分 | — |
| [synthetic-validation.md](synthetic-validation.md) | 合成入力による工程検証の現在地 | **合成検証のみ**。実物レビュー・公開承認・Authority検証ではない。 |
| [tai-crossview-reader-guide-2026-11-09.md](tai-crossview-reader-guide-2026-11-09.md) | TAI全体像の横断読解ガイド v0 — 課題から製品選択・証拠・結果まで | **Draft / 読者向けの解釈・検査案 / Owner未受理 / 本書固有の検証NOT RUN**（2026-11- |
| [tei-construction-migration-plan.md](tei-construction-migration-plan.md) | TEIによるプロダクト構築への移行 — フィージビリティ検証計画 | **Draft（提案）**。Owner指示（2026-11-01）を前提にした検証計画であり、製品要求・採用済み設計では |
| [tei-pilot-status-brief.md](tei-pilot-status-brief.md) | TEIパイロットの現況（2026-11-06） | — |
| [yi-constellation-website.md](yi-constellation-website.md) | YI Constellation ウェブサイトの情報設計（Draft v0） | **Proposed / 公開サイト未実装**。YI Constellation専用リポジトリを作らず、**既存のTAI |
<!-- doc-index:end -->
