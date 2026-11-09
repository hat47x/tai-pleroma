# RQ7 G-Cal1b：実ブラウザーの表示経路・Node遮蔽負例

- **状態**: 実Chromium幾何検証の限定作業（2026-11-09）。公開合成3種のDAG限定。独立Human/AI比較、TEI Product、Source/Policy/Authority/Owner受理、実Screen Readerは **NOT RUN**。
- **基準**: [RQ7研究プロトコル](../protocols/RQ7_BOUNDED_GRAPH_OBSERVABILITY_2026-11-06.md)、[G-Cal1a静的SVG/Text比較](../protocols/RQ7_STATIC_SVG_TEXT_PARITY_2026-11-08.md)、[main済み公開合成機材](../protocols/RQ7_PUBLIC_TOOLING_MAINLINE_2026-11-09.md)。
- **変更**: [固定DAG SVG renderer](../tools/rq7_svg.py)、[構造・変異回帰](../tools/test_rq7_svg.py)、[Chromium DOM幾何smoke](../tools/rq7_browser_smoke.py)、[限定CI](../../.github/workflows/rq7-public-prepilot.yml)。
- **参照PR**: [TAI #556](https://github.com/hat47x/tai-pleroma/pull/556)。この文書は新しいProduct Layout Engine、TEI StudioのUI Acceptanceを提案しない。

## 1. 実際に発見した欠落：Edge同一性だけでは「図を正しく描いた」と言えない

公開合成Build DAGの `src→compile`、`compile→test`、`test→package`、`compile→package` は4つのEdgeである。旧静的SVGは`compile→package`を一本の直線で描いていたため、中間の`test`ノードの中を横切る。

旧固定DAG配置を独立計算すると、`compile→package`の直線は`(440,60)→(711,60)`、中間`test`は`x=490..670,y=30..90`の長方形であり、交差は幾何学的に真。前回のXML構造・座標一致テスト（52/52 PASS）は「**指定どおりに誤配置した**」ことを許していた。これは実TEIのRuntime Sourceや業務Relationの反例ではなく、公開合成Stimulusの**図としての意味の可視性**に対する反例である。

## 2. 採用した最小修正と停止条件

既存の公開3種DAGに限り、複数Rankを跨ぐEdgeを、上側に確保した経路へ`M/L`の折線で迂回させる。元のEdge集合・方向・Node識別子、Gold、Text表示、観測境界は変更しない。

追加した検査は、以下を混同せず実施する。

| 層 | 検査 | 意味しないこと |
| --- | --- | --- |
| 宣言の意味 | 元Graph・Text・SVGでNode/Edge/Labelが一致、Gold不変 | 実SourceのRelation閉包、Owner受理 |
| SVGメタデータと座標 | 指定Edgeの経路・方向・矢印が新しい配置と一致 | 描画エンジンでのピクセル・フォント視認性 |
| **Node遮蔽** | 矢印を構成する各区間が、両端**以外の**Node矩形内部を横切らない | 多数Edge同士の交差、図全体の最適性 |
| **Chromium描画** | 実ブラウザーの`getBBox`、`getScreenCTM`、`getPointAtLength`でラベル・経路の表示座標を検査 | 人間による見やすさ評価、スクリーンリーダー |
| 狭い画面 | Mobile width=390pxでもGraph全幅が横スクロールで到達可能 | 一画面に全Graphが収まること |

この方式は**一般GraphのEdge Routingではない**。長いラベルや日本語・巨大なGraph、循環、多項Role、複数の長距離Edgeの経路衝突には別の設計・実ブラウザー検証が必要。一般論としてノードとの交差を回避するGraph edge routing自体は先行研究があり、[Binucci et al., *Placing Arrows in Directed Graph Layouts: Algorithms and Experiments* (2022)](https://doi.org/10.1111/cgf.14440)等がある。本件を学術的な新規アルゴリズムと主張しない。

## 3. 実ブラウザー検査の再現

GitHub ActionsはPublic Syntheticに限定した別JobでPlaywright + Chromiumを明示導入し、固定CIで以下を行う。

`python research/tools/rq7_browser_smoke.py --screenshots "$RUNNER_TEMP/rq7-browser"`

- 元の公開22ケースを列挙し、**3種の異なるGraph**から各1件を代表にする。Desktop `1280×900` とMobile `390×780` の**最大6組**。
- 本当に描画されたSVGのラベル領域を`getBBox`で測り、ID/Labelが矩形外へはみ出すなら失敗とする。
- 矢印を`getPointAtLength`（Path）/座標線形補間（Line）でサンプリングし、`getScreenCTM`で画面座標に変換し、両端以外のNodeを横切らないことを確認する。
- 狭い画面ではGraphが横スクロールでき、実移動量を得られることを検査する。外部HTTP(S)要求は許可しない。
- **長いLabelを人工的に追加した負例**では、単一行ラベルのはみ出し検出に成功することを要求する。これは「長いLabelが正しく表示できた」の合格ではなく、**現在の固定幅レイアウトが長いLabelに非対応であることの確認**。
- 公開合成のみのスクリーンショットを7日保持する。Node内部の一行ラベル以外に業務機密、Raw TEI CLI Source、ユーザー情報を扱わない。

### 試験成功後に主張できる範囲

- **G-Cal1b-geometry**: 「3種の公開合成GraphをChromium上で実描画し、定義した要素・経路・短いラベル・Mobile横スクロールの機械検査に合格」。
- **G-Cal1b-a11y**: **NOT RUN**。`svg[role=img]`と`title/desc`の存在だけでは、Node/Edgeを実スクリーンリーダーで辿れる保証にならない。
- **G-Cal1b-perception**: **NOT RUN**。Node/Edgeが幾何的に正しくても、視覚的に紛らわしくないことや認知負担の低下は未証明。
- **G-Cal2/3**: TEI #3321実CLIのDisclosure Qualified Public Slice、#2831 Build、#2542 ETLの独立閉包と実消費、Human/AIの独立Goldはそれぞれ未実証。

**停止条件**：実ブラウザーの幾何検査がFail、長いLabelで欠落が起きる、公開ルール外のSourceやDisclosureが必要になる場合は、製品の「完全な図表」へ昇格せず、明示的な不確実さとText表示を保持する。実ブラウザーが動かない環境ではステータスをNOT RUNとし、合成XMLのPASSで代替しない。

## 4. 実行結果（exact HEADで確認して追記）

GitHub Actionsの実行結果、変更head、Chromium version、成功ジョブ数、スクリーンショットの存在、残るFailを確認した後に**初めて**「G-Cal1b-geometry限定PASS」と記録する。設計プロトコルに記載しただけで実施済み扱いにはしない。
