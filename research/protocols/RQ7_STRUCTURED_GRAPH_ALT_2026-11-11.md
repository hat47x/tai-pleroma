# RQ7 G-Cal1b-Nav — 構造化テキストによるGraph関係への到達

- **対象**: 公開合成RQ7の小規模DAGのみ（2026-11-11）。[RQ7研究計画](RQ7_BOUNDED_GRAPH_OBSERVABILITY_2026-11-06.md)、[SVG/Chromium AX等価性](RQ7_CHROMIUM_AX_TOPOLOGY_2026-11-11.md)を補完する。
- **実装**: [Native HTML詳細表示](../tools/rq7_structured_alt.py)、[Chromium DOM/キーボード試験](../tools/rq7_browser_smoke.py)、[変異回帰](../tools/test_rq7_structured_alt.py)、[限定CI](../../.github/workflows/rq7-public-prepilot.yml)。
- **実証していないもの**: 実スクリーンリーダー操作・読解効率、WebView2/Studio、TEI実Source/Policy/Owner、実ETL/Build、独立Holdout、Human/AI認知効果。

## 1. なぜ画像のAX説明だけでは十分でないか

前回[TAI #622](https://github.com/hat47x/tai-pleroma/pull/622)で、SVGの短い画像名と長い関係説明を分離し、実ChromiumのAX Treeに全Node/直接Edgeが現れることを確認した。しかし**一段落の説明を正しく伝える**ことと、利用者が**特定Node・特定Edgeへ構造的に移動・照合する**ことは違う。

[W3C WAI Complex Images](https://www.w3.org/WAI/tutorials/images/complex/)は、複雑な画像に短い説明と十分な長い説明を組み合わせ、必要なら見出し・表を備えた構造化説明を提供する方法を示している。特に`aria-describedby`で結び付けた長い説明は連続したテキストとなり、見出し・表の構造的なナビゲーションが失われる点に注意している。これは**「画像の説明文字列が完全ならa11yも完全」という主張の反例**である。

## 2. 今回の最小構成

公開合成fixtureのDeclared Graphだけから、ネイティブHTMLの開閉部`<details id="graph-data">`と`<summary>`、意味を明示した2つの表を作る。これは**RQ7研究用ブラウザーハーネス**内の実験表示であり、TEI共通UIや新Pluginではない。

| 表 | 内容 | 誤昇格させないこと |
| --- | --- | --- |
| **Declared nodes** | `<th scope=row>`にID、`<td>`に元のLabel | Source上の全Role・Nodeの閉包とは限らない |
| **Declared directed edges, not transitive paths** | 元Graphの各直接`from→to`。推移的Reachabilityを勝手に加えない | Build/ETL実行順や実Effectを意味しない |

実装では文字列をHTMLエスケープし、Gold/実Observed/Policy/Source路径を付加しない。テーブルをまとめるだけでなく、**Graph本体と行のID/ラベル/向きまで完全一致**することを検査する。

## 3. 受入の独立検査

1. Python標準ライブラリで、v0/v1合計22ケースのNode・直接Edgeを、2表のセル内容として再読取・照合する。
2. **同じ件数でもEdgeを別の向き・相手に差替えた変異**を拒否。これは[TAI #619](https://github.com/hat47x/tai-pleroma/pull/619)で確認した「同一件数と同一意味は別」の一般化である。
3. Chromiumのキーボード操作で、`summary`へTabで到達し、Enterで開閉できることを検査する。プログラムによるfocus注入だけで「キーボードから届いた」としない。
4. 開いた状態で、Chromium DOMから直接行データを再取得し、元GraphのID/ラベル/直接Edgeと比較する。Accessibility Treeに`table`2件と`columnheader`があることを検査する。
5. SVG/AX Tree幾何の既存試験を温存し、公開3種DAG×PC/モバイルの6条件で併存を確認。長いLabelのSVGは未対応のままなので、構造化表を追加しただけで視覚面の修復が済んだとは扱わない。

## 4. 検証資格と次の停止線

- **G-Cal1b-Nav**: ネイティブHTMLの表を実Chromiumから構造とキーボード操作を含めて検査する。正式なScreen Readerの音声やユーザー操作の満足度は含まない。
- **G-Cal1c**: 同じGraphに対するSVG+AX説明と、構造化表の**検索負担・誤確定・過剰保留**を、人間・画像対応AIで別々に比較する（NOT RUN）。同じ参加者が公開Goldを見た条件を独立Holdoutと呼ばない。
- **E-trace/E-pipeline**: TEI [#4382](https://github.com/hat47x/tei-platform/pull/4382)の多Projection漏れ、[#4392](https://github.com/hat47x/tei-platform/pull/4392)のValidation/Map/Source資格、[#3321](https://github.com/hat47x/tei-platform/pull/3321)のRoot/Read Attempt不明、[#4240](https://github.com/hat47x/tei-platform/pull/4240)のABA、[#4299](https://github.com/hat47x/tei-platform/pull/4299)の実State不一致は各Ownerの実装・検証領域である。今回の表は**Synthetic Declared Projectionだけ**に由来するので、実Source/実Readを受理したふりをしない。
- 最小Self-build/ETL研究でも、**Declared Graphがある／表示できた／Stateを実際に分離した／Consumerが独立に読んだ／Ownerが受理した**を異なるClaimとして扱う。閉包できない場合はUnknownを保持する。

**今回のコードが成功しても、複雑Graphの一般的な探索UI、スクリーンリーダー利用上の適格性やユーザー満足度は保証しない。** RQ7の根本要件は、図と表のどちらかを唯一の正本にすることではなく、同じ宣言データの複数Projectionが、欠落や過剰解釈をせずに到達可能であることを検証する点にある。

## 5. exact-headの結果

GitHub上の本PRの限定CI、Chromiumの表・キーボード/AX結果、TAI Referenceの実行を確認後、固定SHAと合否を記録する。旧#622の57/57 PASSを本変更のPASSとして流用しない。
