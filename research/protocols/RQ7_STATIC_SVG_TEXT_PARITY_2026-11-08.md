# RQ7 G-Cal1a：宣言Graphの静的SVGとTextの構造等価性

- 状態: **公開合成研究用の機材検査**（2026-11-08）。**G-Cal1bの実ブラウザー描画、人間/AIの認知比較、独立holdout、実TEI/EKI/Source/Policyは NOT RUN**
- 研究正本: [RQ7プロトコル](RQ7_BOUNDED_GRAPH_OBSERVABILITY_2026-11-06.md)、[v0/v1比較とGold](RQ7_PILOT_STIMULUS_AND_SCORING_2026-11-06.md)、[実CLI証拠の比較資格](RQ7_REAL_CLI_EVIDENCE_TRANSFER_2026-11-08.md)
- 実装: [静的SVG生成・照合ツール](../tools/rq7_svg.py)、[専用変異テスト](../tools/test_rq7_svg.py)、[限定CI](../../.github/workflows/rq7-public-prepilot.yml)
- v0=10ケース・v1=12ケースの既存公開合成Stimulus/Goldは変更しない。評価被験者にGoldや`question_selector`の特権情報を渡さない。

## 1. なぜMermaid文字列だけでは比較研究が完了しないか

これまでの研究用V1/V3の`declared_graph`は**Mermaidのソース表記**だった。人間に視認される図（ノードの見た目・エッジ・矢印・レイアウト・文字のはみ出し）でも、AIが画像として受け取る図でもない。Mermaid構文をテキストとして読めた参加者を、実際に図を読めた参加者と同じ条件へ集計すると、表示形式の効果を分離できない。

今回の`rq7_svg.py`は、公開合成Fixtureの宣言`nodes/edges`から、標準ライブラリのみで**外部通信・JavaScript・外部フォントを要求しない静的SVG 1ファイル**を出力する。テキスト条件は既存`rq7_pilot.declared_text`を使用。これは、**V1-svg/V3-svgという将来の表示実験の候補**を作るもの。Mermaid版V1/V3と表示形式を変えたことを、比較時に黙って混合しない。

## 2. 自動で確認できる同等性（G-Cal1a）

| 独立した検査対象 | 自動チェック | このチェックだけでは分からないこと |
| --- | --- | --- |
| **論理Nodes** | SVG側`data-id/data-label`・可視`text`が、公開Graphの`id/label`と一致し、Text側`Node id: label`も一致 | 実レンダラーで文字が視認・読み上げ可能か |
| **論理Edges** | SVG内`data-from/data-to`、Text側`Edge src→dst`が、元Graphの有向集合に一致 | 実Productの全Relation/Roleが元Graphに含まれていたか |
| **SVG矢印の幾何** | 矢印の始終点が、静的DAGレイアウト内の該当Nodeの位置に結ばれている。座標を変える負例を拒否 | 実ブラウザーで線が隠れない・交差が読める・認知的に明瞭か |
| **SVGの可視ラベルと配置** | Nodeごとの可視`text` ID/Label、`transform`、枠と基本コントラスト値を静的検査。ラベル差替え・Node移動を拒否 | フォント幅、言語、ズーム、横スクロール、色弱・スクリーンリーダー評価 |
| **入力制限と安全境界** | Public fixtureのみ。DAG以外・dangling/duplicate Edge・無効IDを拒否。XMLエスケープと外部リソース不使用を検査 | 任意のProduct Graph（循環・Hyperedge・Role・大型データ）への適用可能性 |
| **正解隔離** | `render_svg`は宣言Graphだけを読む。Goldを読み込まないので、出力XMLにGold判定を描かない | 実験者がGoldを知ったことによる被験者選択・評価バイアス |

**重要**: SVG内のメタデータだけを検査すると、`data-from=src`と書きながら別Nodeへ矢印を向けても「一致」と誤判定する。そのため**座標だけを誤らせた負例**を加えている。ただし正しいブラウザー描画・UI/ARIA/画像理解までは証明しない。

## 3. 再現可能な入力と操作

研究Branchでの最小実行コマンド：

`python research/tools/rq7_svg.py --dataset v0 --check`

`python research/tools/rq7_svg.py --dataset v1 --check`

`python research/tools/rq7_svg.py --dataset v1 --case B-DR01 > /tmp/rq7-B-DR01.svg`

`python -m unittest discover -s research/tools -p 'test_rq7_*.py' -v`

`--check`は公開22ケースを対象に同一Graphの静的XML/Textを比較する。**Graphの存在・実Sourceの完全性・実Provider/Owner資格を検査するコマンドではない**。SVG生成ツールは`dag`の最小固定構成だけを対象とし、複合Relation、Loop、分岐の実行時状態、Plugin最適化の論理物理対応を描く汎用TEI Graph Viewerではない。

### 実表示の独立確認（G-Cal1b：未実施）

ブラウザー・描画エンジンの具体版を固定し、同じ`scope/revision/claim`の文脈に配置したSVGとTextを、以下の負例も含めて比較する。

1. 長いLabel・日本語・狭い画面幅・拡大表示で、Node/Edgeが欠ける、重なる、別方向に見える。
2. 色や線だけに意味を任せず、Tab操作・キーボードとスクリーンリーダーから全Node/Edgeへ到達できるか。
3. Text側にあって図側にないEdge、図側で別Rootへ結線されたEdge、SVG内の`data-*`は正しいが画面では異なる矢印を**独立した人間が見つけられるか**。
4. 参加者がMermaid文字列を読むか、実画像を読むか、テキストNode/Edge表を読むかを**別条件**として記録し、モデルの画像対応能力を固定する。
5. 片方だけにScope、Observer coverage、Consumer Read、Policy資格を描画していないことを確認する。今回のSVGは`Declared`のみであり、V2/V3へ追加の合成Evidenceを載せるUIは**未実装**。

これが完了するまでは「同じ情報を含むSVG/XMLとTextの構造一致」は言えても、「図とテキストを**実際に同等に理解できる条件**」や「図が認知負担を改善した」とは言わない。

## 4. E-traceとE-pipelineの次段接続

[TEI #3321](https://github.com/hat47x/tei-platform/pull/3321)の実`tei trace`が提供するのは**直接参照候補の観測Projection**であり、独立した宣言`Pipeline DAG`ではない。今回の公開DAGのSVGを、そのまま#3321の実CLI GraphのSource完全性／Relation権限と読み替えない。

次の実証は二つに分ける。

- **E-trace（限定説明能力）**: #3321のOwnerが公開を認めた`subject/scope-origin/manifest/edge-candidate/unknown-claims`の最小Sliceを、同一情報のText/Graphへ投影したとき、認知的な誤昇格を防ぐか。現在はraw CLIデータをTAIへ取得・転記していない。
- **E-pipeline（後続の意味/実行）**: #2831 Build/#2542 ETL側が、独立に承認された宣言Graphと同じAttemptの`Resolved/Observed/Consumed`を提供できた場合だけ、RQ7本体の2×2実験を行う。現段階は**BLOCKED/NOT RUN**。

**採用・撤回条件**: 元Graphの不明なSource/Role/Boundaryを隠したまま見栄えだけを改善してはならない。表示効果がなく、非開示への影響やレンダリング負担が増すなら、Read-only Text表示と未解決の明示を優先し、不要な汎用Graph/Pluginを追加しない。TEI Studioの最優先[直接ブロッカー #1124](https://github.com/hat47x/tei-platform/issues/1124)は本研究で置換しない。
