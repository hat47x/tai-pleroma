# RQ7 公開合成の構造・Gold・静的図表校正ツール — mainline移管

- **状態**: 既存[研究Draft #473](https://github.com/hat47x/tai-pleroma/pull/473)から**検証済みの公開合成ツールに限って**現行mainを基点に移管（2026-11-09）。これは**研究機材**であり、Human/AI認知改善、TEI実CLI/Graphの完全性・実施承認を意味しない。
- **分割の目的**: #473が長期研究・E-trace/E-pipelineと合成fixture/CIを同一Draftに保持し、mainと大きく乖離したため、独立して実行可能な「公開データと検査」の部分だけを取り出す。変更元の各ファイルは、固定head `cbe3a4aa11302ad2efb2813a6f78ab297d951dd4`の**Git blobを完全一致で複製**した。元Draftに残る同内容のファイルはmain統合後のPR差分から相殺されるべきであり、別機構として二重導入しない。
- **機材の対象**: [v0/v1公開fixture](../fixtures/)を使用したNode/Edge/Label・Direct edge/Directed path・Gold verdictの構造検査、固定DAGへの静的SVG描画とText投影、正答分布および単純Baselineの校正。
- **範囲外**: 新TEI Source Reader、Pipeline/Build/ETL Runner、Graph/Relation資格を与えるProvider、Studio UI、Policy/Authority、独立holdout、実AI/Human、ブラウザー画面/a11y、プロダクト受理。

## 1. 資産と入力/出力

| 資産 | 目的 | 完了していないこと |
| --- | --- | --- |
| [`rq7_pilot.py`](../tools/rq7_pilot.py) | 公開v0（10件）/v1（12件）切替、V0/V1/V2/V3のText/Mermaidソース、公開Gold漏出/構造検査 | 実画面描画・実CLI観測ではない |
| [`rq7_calibrate.py`](../tools/rq7_calibrate.py) | 常時S/R/Uと特権的Typed Selectorだけを読むBaselineのGold照合 | 被験者・実AIモデルの成績ではない |
| [`rq7_svg.py`](../tools/rq7_svg.py) | 公開DAGのみ静的SVG化し、TextとNode/Edge/ラベル/矢印座標を照合 | 実ブラウザー画像のクリッピング/人間の読解は未確認 |
| [`test_rq7_*.py`](../tools/) | Gold非漏出、構造・変異、矢印位置改変、公開2データセットの回帰 | 正解の独立学術/業務評価ではない |
| [研究限定CI](../../.github/workflows/rq7-public-prepilot.yml) | Public synthetic testだけをPR/対象Pathの変更に対して実行 | Product本体の資格を与えるCI Gateではない |

`v0/v1`のGoldは**公開開発用**で、独立した sealed holdout ではない。v0の宣言だけのGold（S/R/U）は2/0/8、v1は4/4/4。v1の追加合成Evidence付きは5/5/2であるが、同じGraphの質問を多数含むため、被験者の認知向上を意味しない。22公開ケースは**Distinct Declared Graphが3種**（Build 11/ETL 9/Cross-boundary 2）。テストが多いことを独立した図表数へ読み替えない。

## 2. 実行・検証コマンド

Python 3.13・標準ライブラリのみ。以下は**公開合成研究機材だけ**を動かす。

`python research/tools/rq7_pilot.py --dataset v0 --check`

`python research/tools/rq7_pilot.py --dataset v1 --check`

`python research/tools/rq7_calibrate.py --dataset v1`

`python research/tools/rq7_svg.py --dataset v0 --check`

`python research/tools/rq7_svg.py --dataset v1 --check`

`python research/tools/rq7_svg.py --dataset v1 --case B-DR01 > /tmp/rq7-B-DR01.svg`

`python -m unittest discover -s research/tools -p 'test_rq7_*.py' -v`

GitHubで元Draft #473のコードhead `4a10c1cd950c158a5f6d407700370153da67a727`に対して、[限定Actions #42434940638](https://github.com/hat47x/tai-pleroma/actions/runs/42434940638)は**52/52 PASS**（試験が対象とするのは公開合成DAGの構造/配置）。**この新branch自身のGitHub Actions・mainへの統合は、PR作成後に別々に検証し記録する**。旧headのPASSを新branchのPASSとして転用しない。

## 3. 証拠資格の停止線

[TEI現行main起点の実Trace Draft #3321](https://github.com/hat47x/tei-platform/pull/3321)は、Go実CLI→Node Consumerの限定照合についてhead `6dba996ee07af5ddd9b8c705fdf654e092171d59`で[専用Actions #42575521655](https://github.com/hat47x/tei-platform/actions/runs/42575521655)を実行し、**Node 18/18 PASS、Go CLI 4観測PASS**と記録している。ただし、同じManifest・Source・World・SourceIndex/Snapshot tokenのままで別の**物理Root/Read Attemptを識別できない**反例を発見し、`same-observed-load-context-only`に主張を限定した。観測フィンガープリント一致と実体・Attempt同一性は別。

この研究機材は上記TEI実CLIのraw JSONやSource pathを持たない。TEIのScope/Root/Reader/Authority/Ownerを生成するものではなく、実CLIの成功をRQ7公開DAGのClosed-world証拠へ転用しない。実データを使う前に**現在の開示Policyが許すSlice**と独立Qualified Subjectを固定する。

[TEI Studio Draft #3543](https://github.com/hat47x/tei-platform/pull/3543)の実CLI→同一Workbenchイベントも別Owner/別実証。RQ7のSynthetic 52テストがStudio M0/M1を満たすものではない。ユーザー指示のHost原則廃止を覆さない。

## 4. 次の研究（この分割PRには追加しない）

- **G-Cal1b**：実SVG画像のブラウザー描画・文字はみ出し・キーボード/スクリーンリーダー・Textとの提示情報同一性（NOT RUN）。
- **E-trace**：TEI #3321の現行Policyで開示可能な限定ObservationのText/図への投影と過大解釈防止（NOT RUN）。
- **E-pipeline**：#2831 Self-build/#2542 ETL/MFTが固定した独立宣言とResolved/Observed/Consumedを同一Attemptで得られるか（NOT RUN）。
- **G-Cal3**：Gold秘匿・独立評価者・人間/AIの2×2認知研究。公開v0/v1はholdoutとして使わない（NOT RUN）。

本分割PRの成功後も、TEIの設計意図・実装・検証・受理の責務は各Ownerへ残す。#473の研究計画・将来実験は別レビューとし、現在の公開合成機材のPASSでまとめて採用しない。
