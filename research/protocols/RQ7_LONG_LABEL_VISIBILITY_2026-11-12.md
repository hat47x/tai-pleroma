# RQ7 G-Cal1b-Label：長い宣言ラベルを黙って欠落させない

**状態**：公開合成RQ7の小規模DAGに限定した視覚表示の改善（2026-11-12）。人間・AIの認知効果、実TEI Source/Policy/Owner、ブラウザーやスクリーンリーダー全般への適合は **NOT PROVEN**。

基礎となる研究：[RQ7本体](RQ7_BOUNDED_GRAPH_OBSERVABILITY_2026-11-06.md)、[Chromium幾何・遮蔽検査](RQ7_CHROMIUM_GEOMETRY_GATE_2026-11-09.md)、[SVG→Chromium AX Tree](RQ7_CHROMIUM_AX_TOPOLOGY_2026-11-11.md)、[キーボードで開ける関係表](RQ7_STRUCTURED_GRAPH_ALT_2026-11-11.md)。実装対象は [SVG生成器](../tools/rq7_svg.py)、[実Chromium検査](../tools/rq7_browser_smoke.py)、[回帰テスト](../tools/test_rq7_svg.py)。製品Studio、Graphエンジン、Source Reader、Host、Authorityは変更しない。

## 1. 修正する認知・証拠上の穴

これまでの公開SVGは、各Nodeの矩形幅を180px、ラベル1行を13pxに固定していた。ラベルが長くなると、元Graph・SVG内の`data-label`・Chromium AX説明・構造化Node表は完全一致していても、**可視矩形からラベル文字がはみ出す**。したがって「Source→SVGのメタデータ一致」と「人間が画面上で全ラベルを読める」は別の命題である。

**変更**：宣言Labelから標準ライブラリで保守的な必要幅を見積もり、1つのGraphのNode幅を一様に拡張する。各Rankの横位置・SVG viewBox・矢印の出発点と到達点・遮蔽検査の矩形も同じ幅を参照する。ラベルの文字列・大小文字・ID・直接Edge・方向・Gold・Observationは変えない。

- 最小幅 **180px**、単一行の最大対応幅 **2048px**。英語・日本語・全角文字などに対して余裕を持つ幅推定を行う。
- 上限超過は `ValueError: label exceeds supported single-line SVG width` で**明示的に拒否**し、切り詰め／フォント縮小／秘密の追加表示を行わない。
- 英語の長いラベル、日本語の長いラベル、それぞれのオリジナルGraphと、ラベル以外のNode/Edgeが同一であることを、Pythonと実Chromiumで検査する。
- Chromiumでは実ラベルの`getBBox`をNode矩形の**実幅**と比較する。Nodeをわざと180pxへ戻す変異で「ラベル欠落を検出できる」ことを検証する。
- 横スクロールを実際に移動できることと、SVG/AXの全ラベルが等しいことを検査する。構造化表は別のRead-only投影として維持する。

## 2. 既存のTEI/TAI研究との接続

| 別の既存研究 | 反映する設計上の区分 |
| --- | --- |
| [TEI Draft #4464](https://github.com/hat47x/tei-platform/pull/4464) | 4構造×8表現系の投影Loss/拒否という限定Referenceを研究。図の可視ラベルの一部欠落も**可視Projectionの損失**として判定し、意味保持の採用済み契約と混同しない。#4464は現時点でOpenであり、実編集/保存/再投影の受理ではない。 |
| [TEI Draft #4487](https://github.com/hat47x/tei-platform/pull/4487) | 存在・不存在・全称・実行・業務受理の量化別資格は提案段階。ラベルを描けた／描けないことからSourceの関係不存在・Writer不存在を推論しない。 |
| [TAI研究計画](RQ7_REAL_CLI_EVIDENCE_TRANSFER_2026-11-08.md) | Subject/Scope/Revision・表示Projection・実Reader/Owner/Authorityを別々に固定。公開SVGの表示改善を実TEIのSource Closureや完全Graphへ昇格しない。 |

またW3C [WCAG Reflow](https://www.w3.org/WAI/WCAG21/Understanding/reflow)は、図などの二次元レイアウトを必要とする内容と、その内部にある文字のリフローを区別している。今回のNode横幅拡張は**狭い画面では横方向スクロールが増える**というトレードオフを持つ。長文・混在言語・ズーム・全環境・実スクリーンリーダー・長いラベルの認知効率を満たす適合表明はしない。

## 3. 反例と成功条件

| 層 | 正の例 | 負の例・停止条件 |
| --- | --- | --- |
| 宣言Graph | 既存v0/v1 22ケースのNode ID/Label・Edge不変 | 未宣言Edge・別Scope/Sourceを推測しない |
| 英語長文 | 元文を1字も省かずNode矩形内に表示 | 従来180px矩形へ戻せばChromiumがoverflowを検出 |
| 日本語長文 | 全角文字で幅が増えた矩形と全文を一致 | 別端末・別フォントで欠落するならその環境はFail/Unknown |
| 2048px超過 | 非対応を明示し**生成を中断** | 欠けた文字があるのに「可視Graph完全」と記録しない |
| 結線 | Rank/Edge/遮蔽計算も拡張幅に追従 | 迂回線が別Node矩形を貫く場合はReject |
| アクセシビリティ | SVG全文、AX説明、構造化表から元Labelへ到達 | 実Screen Reader・キーボードの利用者評価は別Gate |

成功を主張できるのは、**固定headでPythonの全RQ7回帰、ChromiumのPC・モバイル（公開DAG 3種×2画面＋英日長文変異）、通常TAI Referenceが成功した場合だけ**。元の3種以外の実TEI Graphや循環／多項Relation／巨大Pipelineへの一般化はしない。

## 4. 次Gate

長文のNode横幅が画面の認知負荷を増やす可能性があるため、次は複数行折返し・読み方向・文字拡大と図表の再レイアウトを、実ブラウザーと構造化代替表の双方で比較する必要がある。さらに、各Projectionでの**可視性/到達可能性**を確かめてから独立Holdoutで人間/AIの誤確定・過剰保留・検索時間を評価する。これらは **NOT RUN**。
