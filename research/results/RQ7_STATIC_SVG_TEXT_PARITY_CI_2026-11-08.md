# RQ7 G-Cal1a：公開合成Graphの静的SVG/Text照合のCI実測

- **記録日**: 2026-11-08（JST）
- **固定コードHEAD**: `4a10c1cd950c158a5f6d407700370153da67a727`（[TAI研究Draft #473](https://github.com/hat47x/tai-pleroma/pull/473)の通過済み版）
- **GitHub Actions**: [RQ7限定run #42434940638](https://github.com/hat47x/tai-pleroma/actions/runs/42434940638)（completed/success）、job `128591660090`
- **実行結果**: Python 3.13、`Ran 52 tests in 0.227s / OK`。上記はGitHub Actionsの**当該headの実job log**で確認。
- **非該当**: TAI通常Reference全体の最新版検査、TEIのGo/CLI/Studio/ETL/Build、実権限・Source closure、実ブラウザーとA11y、外部AI/Humanの認知比較、独立holdout。これらに対するPASSではない。

## 1. 固定した実行対象

| File | Git blob |
| --- | --- |
| [SVGレンダラー](../tools/rq7_svg.py) | `6e9591a1d1e3268e14a3ac8fca61542c89e99b9e` |
| [SVG負例・構造テスト](../tools/test_rq7_svg.py) | `7a323e47b542648e47e040a8d7916ab729d22e2e` |
| [研究限定Actions](../../.github/workflows/rq7-public-prepilot.yml) | `243a3cdf4bf661946a823ecbf2fda566b4734c74` |
| [公開v0刺激](../fixtures/RQ7_BOUNDED_COMPLETENESS_PILOT.synthetic.json) | `fdf5fa882e6a1234942835713d00be2c3bc7bac6` |
| [公開v1刺激](../fixtures/RQ7_BALANCED_PUBLIC_PREPILOT_V1.synthetic.json) | `c50fbfa0e857415dec9bc895edfeb747628a31e7` |

`rq7-public-prepilot`はv0/v1のFixture検査・公開Gold校正・SVG/Text静的構造比較・Python unittestを実行。新しい製品CI Gateではない。既存公開v0/v1 Goldは変更していない。

## 2. 今回検査した内容

- 公開22ケースの`Declared.nodes/edges`をPython標準ライブラリだけで静的SVGへ生成し、元`declared_text`のNode/Edge/Labelと一致させる。
- SVGをXMLとして読み戻し、描画する`text`の2行（ID/Label）と`data-id/data-label`が対応することを検査する。
- Edgeの`data-from/data-to`だけでなく、**矢印の実際のXML座標・結線先とNode配置**が固定DAGレイアウトと一致することを検査する。
- わざとEdgeの座標だけを変え、データ上は同じGraphに見えるが**矢印が違う**変異を拒否する（test_tampered_arrow_geometry...）。Nodeを別位置へ移しても拒否。
- SVGが静的XMLであり外部`script`や`https`参照を出さないこと、危険文字がXMLエスケープされることを検査。
- Cycle、Dangling Edge、重複Edgeの拒否も試験。一般の循環Graphを描けるわけではない。

公開22ケースは**3種類のDistinct Declared Graph**（Build 11件／File Relay 9件／Cross-boundary 2件）の繰返しである。52のtest countは**互いに独立した52種類のGraphを検証した**という意味ではない。

## 3. 完了していない研究Gate

| Gate | 状態 | 必要な観測 |
| --- | --- | --- |
| **G-Cal1a** 公開DAGの静的SVG/Text Node・Edge・位置対応 | **限定PASS** | 上記exact HEADと52テストに固定 |
| **G-Cal1b** 実ブラウザーの描画/テキスト視認/キー・A11y/日本語・画面幅・フォント | **NOT RUN** | ブラウザー版・スクリーンショット・独立レビュー |
| **G-Cal1c** Graph vs Textの人間/AI認知効果 | **NOT RUN** | 独立holdout・事前Gold・情報量統制・分層評価 |
| **G-Cal2** TEI #3321の許可済みPublic Source Slice→E-trace表示 | **NOT RUN** | 実Policy開示資格と同一Packet/Caller-scopeを維持 |
| **G-Cal3** #2831 Self-build/#2542 ETLの独立宣言と実消費を同Attemptで比較 | **NOT RUN** | 別OwnerのSource/Resolved/Observed/Consumed・受理済み意味 |

**保証境界**: 本ツールは静的SVGを作るが、フォント/ブラウザーのピクセル配置やスクリーンリーダー解釈を実行していない。`data-*`とNode位置が一致していても、実図として理解可能か、人/AIの工数が減るかは未確認。G-Cal1aがPASSでも、許可されないSourceや非公開Relationの完全性を言ってはならない。

詳しい実験設計・反証条件は[静的SVG/Text比較プロトコル](../protocols/RQ7_STATIC_SVG_TEXT_PARITY_2026-11-08.md)に置き、製品側のOwner判断は[TEI #3321](https://github.com/hat47x/tei-platform/pull/3321)/[#2831](https://github.com/hat47x/tei-platform/issues/2831)/[#2542](https://github.com/hat47x/tei-platform/issues/2542)に残す。
