# SCN-001 予備比較：固定入力・Gold判定・結果採取票

- 状態: **Protocol freeze candidate / 実験未実行**（2026-10-29）
- Owner: [研究アジェンダ](../README.md) H1 / [SCN-001研究プロトコル](SCN-001_EPISTEMIC_CONTINUITY.md)
- 参照main: TAI `c388e47c708c6f35b6c6f8f42a546a1b31710f3d`（調査時点）。本文記載の資料版は固定だが、**実験実行版は未固定**。実行時にmainではなくコミットSHAで固定する。
- 主な既存実装・記録: [統合run](../../tools/reference-scn001-run/README.md)、[旧照合の不一致再現](../../evaluations/SCN-001-sui-current-observation-gap.md)、[既存の再現スクリプト](../../evaluations/reproduce-sui-observation-gap.py)
- 実装Owner: [TAI #28](https://github.com/hat47x/tai-pleroma/issues/28) および [Draft PR #142](https://github.com/hat47x/tai-pleroma/pull/142)（別変更／未採用）。研究のために機能を重複実装しない。

## 1. 予備比較の問いと固定条件

**RQ1-P1**: 同じIDでMMI観測本文だけを変更し、元SUI receiptを変えないとき、保存済みSUI要約（B1）を採用する経路と、今回の観測を元SUI receiptへ照合する経路（B2）では、不一致検出に差があるか。

- 固定入力: `tools/reference-scn001/testdata/scn001.json`（Git blob `6de80588e14d8b091448dbfe7d6b1cc3d9c14f3d`）と `evaluations/records/SUI-api-2026-10-26.json`（Git blob `3e84d786cc022d01c02907907e8803f05db99f4a`）。
- B1への既存要約: `evaluations/records/SUI-SCN-link-2026-10-26.json`（Git blob `a3f099ee58288b89981af3213780878c091378b9`）。
- 操作する対象: 合成MMI workspaceの**コピーだけ**。O-02/O-07を同じIDのまま、`施設の利用は予約不要` → `施設の利用は予約不要（SUI照合の比較試験）`へ変更する。原ファイル、SEI bundle、SUI元receiptは変更禁止。
- Gold: 元SUI receiptのO-02/O-07の`textDigest`が**今回MMI観測本文**のSHA-256と等しい場合にのみ、内容照合の正例とする。異なる場合は**内容照合を拒否**する。文書の真正性、業務意味、判断の現在有効性とは別。
- 同じ入力・環境・実行対象を各armで用い、失敗後の出力パスを再利用しない。正常系と差替え系はそれぞれ新規の独立した隔離コピーを用意する。

## 2. 研究用Gold matrix（実測ではない）

| Case | 操作 | B1: 保存済み要約の期待 | B2: 現在観測との照合の期待 | Gold / 評価境界 |
| --- | --- | --- | --- | --- |
| CTRL-01 | 元のO-02/O-07本文、元SUI receipt | 通過 | 通過 | 内容digest一致。承認は未確認 |
| MUT-01 | O-02/O-07本文だけ変更、元SUI receipt維持 | **誤通過が起こり得る** | 不一致として拒否 | 内容整合の失敗を正しく検出 |
| BYTE-01 | 正例で生成後、保存したD-04のbytesを変更 | `-verify -artifact`で拒否 | 同左 | byte照合であり意味受理ではない |
| BIND-01 | MMI選択・SCN評価・D-04でIDは同じ、本文だけずれる | 現行mainの保証を別途確認 | 現行mainの保証を別途確認 | [PR #142](https://github.com/hat47x/tai-pleroma/pull/142)の`inputBindingVerified`を将来の別armとする。PR未採用のままGold合格にしない |

CTRL-01/MUT-01の差は既存[合成反例の記録](../../evaluations/SCN-001-sui-current-observation-gap.md)にある。**本研究で同条件の新規比較を行った結果ではない**。BIND-01はPR #142の統合・採用後の独立試験へ回し、現行のB1/B2比較の分母へ混ぜない。

## 3. 実行準備・コマンドと期待する停止境界

以下は**予定コマンド例**。現時点で当該研究のために実行していない。既存のスクリプトが行う旧要約との対照と、B2の統合経路は別に記録する。

1. 対象のTAI本体とMMI・SEIのコミット・依存を固定する。`MMI_ROOT`、`SEI_ROOT`は隔離した開発checkoutを指す。パスには公開不可の原資料を含めない。
2. baseline B1の既存反例再現は、[既存Pythonスクリプト](../../evaluations/reproduce-sui-observation-gap.py)を**新しい絶対パス**で実行する。実行成功は`gapObserved=true`であり、統合機能の合格ではない。
3. B2は同条件のコピーworkspaceを使い、`reference-scn001-run`へ`-sui-receipt`を渡す。正常系は`passed=true`かつ公開・Human/Authority false、変更系は観測内容の不一致で失敗し、成功したrun記録・D-04を生成しないことを期待する。
4. B2の正常系では新規ファイルへ保存した`run.json`と`review.md`に対し`-verify -artifact`を行う。保存済みreceiptの構造・D-04 byte一致と、SUIの元receiptとの再照合を混同しない。
5. 両方式の元CSV、SUI receipt、要約、出力ファイルを実行前後にdigestで照合する。例外、終了コード、stdout/stderr、出力の有無、失敗理由、使用時間と再試行回数を保存する。
6. 実験者が入力を見た後でGoldを変更しない。結果に異論が出た場合はプロトコル版を増やし、旧結果を書き換えない。

**実行時の注意**: `-sui-receipt`と`-sui-link`は同時指定しない。`-out`と`-artifact-out`には未存在の新しいファイルを指定する。`-sui-receipt`の失敗を成功へ読み替えて再試行しない。B0の人間による意味判断・B3のablationはこの実験とは別で、両方NOT RUN。

## 4. runごとの結果記録テンプレート

実際のrunを開始したとき、以下の欄を**1 arm × 1 case × 1 run**で埋める。記録の正本は元の`evaluations/`と製品側に置き、研究側からは参照する。

| 項目 | 記録すべき内容 |
| --- | --- |
| 研究識別子 | `TAI-H1-PILOT-01` / case / arm / run番号 |
| 状態 | **NOT RUN**（初期値）→ PASS / FAIL / BLOCKED（終了後に限定） |
| 固定版 | TAI/MMI/SEI/SUIなど各repoのcommit、依存lockfile、dirty状態、環境 |
| 入力 | fixture digest、変更対象と前後bytes hash、元SUI receipt digest、Gold固定日時 |
| 観測 | exit code、`passed`、`reason`、stdout/stderr参照、出力の有無、研究対象の内容照合 |
| 安全境界 | 公開gate blocked、`humanReviewed=false`、`authorityVerified=false`、`publicationApproved=false` |
| 結果の解釈 | Goldとの一致・不一致、false accept/false reject、正しい拒否とタスク完了の区別 |
| 費用・欠測 | 実測時間、介入回数、実験者・評価者、外部依存の未取得、NOT RUN、再試行理由 |
| 再現性 | SHA固定の手順、参照ログ、異なる順序・別環境での再現可否 |

## 5. 研究結果へ進むGate

- Gate A: 正常系と差替え系のGoldが事前に固定され、比較対象の製品版・実行環境が揃う。
- Gate B: B1とB2の同一条件の実行を完了し、結果・ログ・入力不変性が残る（成功/失敗の両方を保持）。
- Gate C: 独立した評価で結果を確認し、当初の開発用fixture以外の**保留ケース**を使用する。
- Gate D: 他のシナリオで同様の問題が起こり得るかを評価する。[SCN-002](../../scenarios/SCN-002-synthetic-maintenance/README.md)は分野転用の候補だが、同等のdigest/判断境界のケースをまだ固定していないため、結果の一般化には用いない。

**現在**: プロトコル候補と過去の開発証拠があるのみ。Gate A〜Dはこの研究として未完了。R-01〜R-07とP-06/N-05は既存の未受理・NOT RUNのまま。Ownerによる意味受理・公開・外部作用は行わない。
