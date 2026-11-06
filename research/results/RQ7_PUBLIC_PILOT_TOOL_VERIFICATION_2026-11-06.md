# RQ7 公開予備実験ツールの実行検証（2026-11-06）

**状態**: LOCAL RUN / Python public synthetic fixture tooling **14/14 PASS**。**研究上の人・AI比較、TEI製品E2E、独立holdoutはNOT RUN**。

- 計画: [RQ7プロトコル](../protocols/RQ7_BOUNDED_GRAPH_OBSERVABILITY_2026-11-06.md)、[公開予備刺激・採点計画](../protocols/RQ7_PILOT_STIMULUS_AND_SCORING_2026-11-06.md)
- 実行対象: [fixture renderer](../tools/rq7_pilot.py)、[Python unittest](../tools/test_rq7_pilot.py)、[公開刺激](../fixtures/RQ7_BOUNDED_COMPLETENESS_PILOT.synthetic.json)、[公開Gold](../fixtures/RQ7_BOUNDED_COMPLETENESS_GOLD.public.json)
- 実行環境: Linuxコンテナ、Python `3.13.5`、Node `v22.16.0`（**JSONをローカルで再構成した準備工程のみ**）、Git `2.47.3`。ネットワークは使用できず、公開GitHub原稿はGitHub connectorから取得。
- 実行者: AIによるローカルスクリプト実行。外部の独立採点者ではない。
- 試験結果は2026-11-06に固定した公開fixture向け。main全体のCIやProductの動作の証拠ではない。

## 1. 実行byteの同一性

元GitHub branchに保存されたファイルを**同じ内容へ再構成**し、`git hash-object`で元blobと照合してから実行した（2026-11-06時点）。

| 実行・読取ファイル | 確認したGit blob SHA-1 |
| --- | --- |
| `research/fixtures/RQ7_BOUNDED_COMPLETENESS_PILOT.synthetic.json` | `fdf5fa882e6a1234942835713d00be2c3bc7bac6` |
| `research/fixtures/RQ7_BOUNDED_COMPLETENESS_GOLD.public.json` | `f31b21ba89e05df6914f10a364bb885c3a5a51ab` |
| `research/tools/rq7_pilot.py` | `5a5f9b055d560a9c36293850ce70271cf02c73a1` |
| `research/tools/test_rq7_pilot.py` | `9b2ae4c3b151b7cf498559109e8fed631b742613` |

Git SHA-1はGit blobの同一性検証であり、コンテンツ生成上の意味保証やセキュリティ上のAuthorityを与えるものではない。GitHubをクローンしてRepository全体の試験を行ったのではない。

## 2. 実行したコマンドと実測

`python --version` → `Python 3.13.5`

`python research/tools/rq7_pilot.py --check` → 正常終了。`status=PUBLIC_SYNTHETIC_FIXTURE_CHECK_ONLY`、`experiment_run_status=NOT_RUN`、`cases=10`、`gold_entries=10`、`independent_holdout=false`。

`python -m unittest discover -s research/tools -p 'test_rq7_pilot.py' -v` → **Ran 14 tests / OK**。`-q`でも **Ran 14 tests / OK**（後者の計測表示は約1.4秒、環境依存でベンチマーク値ではない）。

`python -m py_compile research/tools/rq7_pilot.py research/tools/test_rq7_pilot.py` → 正常終了。

`python research/tools/rq7_pilot.py --case B-N01 --arm V3` → 正常終了。Mermaidの宣言Node/Edge、`hook`を含む合成観測Event、scope、coverage、問いと回答形式を表示。

`python research/tools/rq7_pilot.py --case F-N01 --arm V2` → 正常終了。`detail@manifest-g2`と`control@manifest-g1`を別々に表示し、合成の`transfer-ack`をConsumer readと混同しない刺激になることを確認。

### 14テストが検証した範囲

- 10ケース×4条件（40通り）の`render()`が例外なくMarkdown/Mermaid**ソース**を生成。**実画像レンダラーの描画・スクリーンリーダー・AIの画像理解は未検査**。
- V0/V1・V2/V3のGold等値、Node/Edge内容の対応、V2/V3の追加根拠テキスト同一を検査。
- 合法skipと宣言だけで答えられる正例、観測不足の3種の`undetermined`を検査。
- case ID重複、dangling edge、required/skip矛盾、unsupported coverage、Gold漏出、holdout偽称、Goldの不正値・条件間不一致が`validate`で拒否されることをMutationで検査。
- `--check`と`--case/--arm`の実CLI subprocessが正常終了することを検査。

**このPASSの意味**: 公開の刺激生成・構造チェックの限定テストが動作した。Gold判定の意味的正しさ、合成Observerの実効性、Declared/Resolved/Observedの製品上の一致、図による理解の向上は証明していない。

## 3. 今回の知見と次のGate

**K0（今回達成）**: 公開予備fixtureの版・生成コード・正負系・Goldを独立ファイルとして再実行可能な状態にした。唯一の意味評価者が実験開発者でもあることは強い制約。外部独立レビュー・sealed holdoutは未実施。

**K1（未実施）**: 固定のGraph Renderer、実Markdownの描画と代替テキスト、画面幅・a11y・AIへの入力方式、同情報量の独立確認。Mermaidソースの存在を「視覚認知改善」と呼ばない。

**K2（未実施）**: 被験者・モデル・評価者とケースの割当、V0〜V3の試行、判定の正しさ・正しい保留・過剰拒否・工数、別のholdout。公開Goldを見たモデルの回答を独立一般化と扱わない。

**K3（未実施）**: [TEI self-build #2831](https://github.com/hat47x/tei-platform/issues/2831)のSB-0 module/source closure、SB-A0/A1、SB-B実CLI、SB-C0/C1 Stage2再入と、[ETL/MFT #2542](https://github.com/hat47x/tei-platform/issues/2542)のEF-01〜05をそれぞれの実証で取得して、合成イベントから実RunのEvidenceへ置換。Ownerの実資格を研究側が再発行しない。

**研究上の停止条件**: 生成テキストと実Graph UIが等価でない、Observationが必要な範囲で閉じない、独立Goldが用意できない、非公開Sourceや内部診断を不適切に開示する場合は、研究結果へ数えず`BLOCKED/NOT RUN`とする。

**契約/実行への影響**: この記録とユニットテストによって、TEI Graph/Self-build/ETL/Plugin Executor、外部Harness、現在のProvider Authority、Ownerによる意味受理、論文投稿・生産性の実証が変更されたことにはならない。
