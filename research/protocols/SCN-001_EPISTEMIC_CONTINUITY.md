# SCN-001 製品横断「証拠に制約された意味の継続性」予備実験プロトコル

- 状態: **Draft / Pre-registration candidate / NOT RUN**（2026-10-29）
- 研究: [TAI横断研究アジェンダ](../README.md) の **H1 / RQ1**（H5への予備データも含む）
- シナリオ: [SCN-001](../../scenarios/SCN-001-shared-space-guidance.md)
- 主な製品側Owner: [#28 原資料と成果物の整合](https://github.com/hat47x/tai-pleroma/issues/28)、[#33 旧判断の誤復活](https://github.com/hat47x/tai-pleroma/issues/33)
- 比較対象の状態: **予定のみ**。過去の製品試験結果をこの研究の結果とみなさない。

## 1. 研究問いと成功ではない状態

**RQ1**: 同じ観測、仮説、判断、成果物を複数の製品へ渡すとき、現在の出典版と意味上の状態を照合することが、古い根拠や不当な確定の検出にどれだけ寄与するか。

対象は構造・版・受渡しの適合を機械検証できる範囲に限る。例えば`artifactBytesVerified=true`は保存したファイルとreceiptのbyte一致を示すだけであり、意味の正しさや実物の真正性を示さない。`-sui-receipt`の内容照合も、SUIのDocument本文からdigestを独立再計算したことにはならない。

過去のDecisionが新しい出典版でも有効か、権限者が正当に承認したか、施設の規程が実際に正しいかは、人間の受理と実物証拠がない限り**未評価**とする。

## 2. 対象の固定と実行前の記録

対象を「mainの最新」ではなく、runごとに固定する。初回の文書調査基準はTAI main `26b6a644ae52d0e6ac500865f5c7fe9af754a5f4`（2026-10-29参照）である。これは**実験の実行SHAではない**。

各run開始前に記録するもの:

- TAIと使用したSUI/SEI/TEI/MMI/EKIの各commit、dirty状態、依存lockfile digest。接続しなかった製品は「未使用」。
- OS、ランタイム、CPU等、時刻基準、実験者・評価者、使用したAIのモデル/設定（未使用ならN/A）。
- 入力fixtureとMMIの合成コピーworkspace、元のSUI receipt、SEI bundle、D-04のdigest。コピーの元ファイルを上書きしない。
- 試験前に決めた期待結果、失敗時に残してよい成果物、公開してよい記録の範囲。
- 開始状態が同等か、失敗するまでの経路が同等か。既存の検査器自体を変更する試行は別run/別方式とする。

過去の参考資料:
- [TAI統合実行](../../tools/reference-scn001-run/README.md)、[SCN合成評価](../../tools/reference-scn001/README.md)
- [SUI card照合](../../tools/reference-sui-link/README.md)、[SCN受入条件](../../evaluations/SCN-001-acceptance.md)
- [保存済み証拠と未検証](../../docs/status.md)、[実物再レビュー](../../evaluations/SCN-001-real-object-review.md)

## 3. 比較する方式

| Arm | 構成・範囲 | 判定上の注意 |
| --- | --- | --- |
| B0 | Markdown、Issue、ファイル参照で人が同じ課題を追う。実験者と確認記録を残す | 独立Gold判定と異なる評価者を用意できなければ人的正答率はNOT RUN |
| B1 | 現行TAIの保存済みSUI要約（`-sui-link`）＋MMI/SEI/SCN/D-04の参照経路 | 要約の構造は確認できるが、今回の観測本文の再照合と混同しない |
| B2 | 現行TAIの元SUI receiptと今回のMMI反映済みfixtureの照合（`-sui-receipt`）を使用 | SUI内容の時点間不一致に対する増分を評価。意味判断の実証ではない |
| B3 | B2から研究対象の一検査を除いた実験用コピー（ablation） | 未実装・未承認。実製品に検査無効化を適用しない。必要性が確かめられた場合だけ隔離環境で試行 |

B1とB2は**すでに存在するモードの比較**。B2を今回新規の機能として計上しない。B3は設計提案にすぎず、初期プロトコルではNOT RUN。比較時には、動作差以外の環境・入力・成果物検査を揃える。

## 4. 正常・負例の事前試験集合（候補）

「Expected」は研究の事前期待であり、**実行観測ではない**。`machine`は対象範囲内の構造・参照を検査、`human-required`は意味/権限の人間判定を要する。

| 研究case | 入力・変化 | 期待される判定 | 既存SCN対応・水準 |
| --- | --- | --- | --- |
| E1-P01 | O-02/O-03が異なる資料であることを保持、公開は保留 | 読出し・参照は成立、双方の出典へ戻れる | P-01/P-02、machine |
| E1-P02 | O-02/O-03/O-07の選択順だけを変更する | 内容とdigestを保持して通過 | #28、machine |
| E1-P03 | 同一のSUI receiptと同一時点MMI観測を照合する | B2で照合成立、受理・公開はfalse | #28、machine |
| E1-P04 | 成果物bytesが記録digestと一致する | byte一致のみ成立、意味・Authorityは未評価 | #28、machine |
| E1-P05 | 参照資料が取得不能であることを記録する | `unavailable`を保持、規程不存在とはしない | N-03、machine |
| E1-P06 | 開発レビュー用Draftだけを作る | レビュー可能。公開・外部作用には進まない | P-03/P-04/N-07、machine |
| E1-N01 | MMI側のO-02/O-07の文言をコピーworkspaceだけで変更し、SUI receiptは旧版 | B1の既存範囲では通り得る。B2はcard digest不一致として拒否することを期待 | #28の既存再現系、machine |
| E1-N02 | SUI cardのID集合は同じ、本文digestのみ古い | 単なる件数・ID一致だけで同一と確定しない | #28、machine |
| E1-N03 | D-04の保存後bytesを差し替える | `-verify -artifact`で不一致を検出、元の記録は変更しない | #28、machine |
| E1-N04 | A→B→Aの同じ文言を持つ新しいSource versionに、旧Decisionを流用しようとする | 同文言だけで「旧判断有効」としない。実Decisionの有効性判定は未実施 | #33/N-01、machine（一部）＋human-required |
| E1-N05 | AIの推奨を、採用者・対象版の証拠なしに決定済みと呼ぶ | 受理済みを主張しない。実際の採用判断は人間へ保留 | N-04、human-required |
| E1-N06 | EKIが`queued`を返しただけでTask完了・業務効果と報告する | 結果・Outcomeへ昇格しない。実Worker検証はNOT RUN | N-05、machine（状態区別）＋未実行 |

初期12件はベンチマークの設計集合であり、統計上の推論に十分な標本数を意味しない。人間判断と未実装の比較armは実行可能な機械caseの分母から**除外した理由と件数**を別掲する。実験中に見つかった新ケースは別版に追加し、評価前固定済みケースの結果と混ぜない。

## 5. 手順（計画、実行済みではない）

1. 評価者がcaseごとの期待結果と検査対象範囲を実施前に固定する。実装担当者が正解を改変しない。
2. コピーした合成fixtureについて、入力bytes・元のreceipt・作業ツリーのdigestを記録する。
3. B1で現行の`-sui-link`経路を評価する。使用したreceiptが古い可能性を既知の失敗条件として記録する。
4. **別の新規出力パス**でB2の`-sui-receipt`経路を評価する。同一のMMI反映済みfixtureをSUI照合とD-04生成へ渡す。元のreceipt・CSVは変更しない。
5. 正常例／失敗例ともstdout、終了コード、保存記録の有無、原入力hashの不変性、公開gateの状態を記録する。
6. 保存された成果物は`-verify <record> -artifact <file>`でbyte照合する。保存後の`-verify`だけではSUI内容照合を再実行しないことを明記する。
7. B0の手動条件とB3の要素除去は、それぞれの実行準備が整った場合のみ実施し、構造試験と人的意味判断の結果を混合しない。
8. 実行後、入力・判定・所要時間と不確かさ、欠測、否定的結果を独立して保存する。

上記は既存ツールの利用方針であり、再現コマンドの実行記録ではない。既存ツールの現行CLI引数は[参照実行README](../../tools/reference-scn001-run/README.md)を正とする。新CLI・新receipt形式・契約変更を要求しない。

## 6. 指標の定義と集計

研究の観測対象を「case × arm × 独立run」とする。同一入力を繰り返した実行は独立した異なる課題とは数えない。

- **不当通過率（false-accept）** = Goldで拒否/保留すべきcaseのうち、成功・確定として通した件数 / 判定できた拒否対象case数。
- **過剰拒否率（false-reject）** = Goldで通過可能なcaseのうち、拒否した件数 / 判定できた通過対象case数。
- **根拠再構成率** = Goldで定義した必須の原文・出典・版・判断主体・適用範囲をすべて再構成できたcase数 / 適格case数。抽出対象が元から存在しないものはN/A。
- **意味の誤昇格件数** = 観測→仮説→判断→権限→実行→Outcomeの境界で、明示的な追加証拠・受理がないのに次状態と扱った件数。
- **費用・負担** = 総所要時間（設計・入力・比較・再確認・修正を含む）、人的介入回数、AI token/cost、試験維持費用を別々に記録する。
- **未測定・未実施** = `NOT RUN`、`BLOCKED`、`N/A`、`FAIL`を区別。分母が0なら率はN/Aとする。実装が不可能なarmを推測で埋めない。

正しい停止と作業完了は別指標にする。`runDigest`の一致、`artifactBytesVerified`、`validation=ok`、`queued`はその範囲以上の成功と数えない。少数データからの有意性・一般化は主張しない。比較件数が増えた場合も独立run数とシナリオ数を別掲する。

## 7. 成果物・実施記録の最低項目

試験ごとに以下を持つMarkdownまたは既存のrecordを参照する研究用記録を用意する。**製品の既存receiptを置換せず、研究記録から参照する。**

- `study_id` / `case_id` / `arm` / `run_id` / `run_status`（`PASS`、`FAIL`、`NOT RUN`、`BLOCKED`）。
- Gold判定の担当者・固定日時・根拠。人間の判断が必要な場合は未受理を明示。
- 基準・対象commit、実際の入力digest、fixture種別（`synthetic`、`real-object`等）、成果物とそのdigest、参照した元receipt。
- 実行環境・コマンド・開始/終了、観測終了コード、出力ファイルの有無、期待/実結果。
- どの保証まで確認したか（`structural` / `byte-match` / `source-authenticity` / `semantic-acceptance` / `execution` / `business-outcome`）。確認しなかった項目を明示。
- false accept / false reject候補、利用者の介入、コスト、失敗要因、保留事項、再現方法。
- 実験結果を製品改善へ戻す先のIssue。未採用の研究仮説で製品契約を変更しない。

### 研究結果の記録場所

研究計画と比較結果の**索引**は本ディレクトリ。個別の既存fixture、component receipt、評価記録の正本は元の`evaluations/`、`tools/`、各製品に残す。新しい実験の結果を保存する場合は`research/results/`へ参照・要約を追加する。未実施の「結果」ファイルを作らない。

## 8. 実施・論文化を止める条件

- 実物の原本・権限者・独立レビューが未確認ならR-01〜R-07を`accepted`にしない。公開gateは`blocked`。
- B2の構造検査が通っても、SUIの実テナント認可やDocument本文からのdigest再計算を検証したとは書かない。
- #33のA→B→Aに対して、本文digestの一致だけで旧Decisionの有効性を判定しない。ExactBindingと人間の再確認条件は元Ownerへ戻す。
- EKIのResultClaimやTask状態を業務Outcomeへ昇格しない。実Worker・独立検証はEKIのMVPと別途受入を要する。
- 合成PASS、研究測定、実使用の有用性、論文の一般的主張を別に扱う。
- B0でも同等の結果が得られる、B2/B3の価値が小さい、過剰拒否や保守費用が大きい場合は、TAI固有の追加機構を撤回する選択を残す。

本プロトコルは**比較試験の設計**であり、製品要求の採用、実行検証の完了、研究仮説の支持、論文の新規性を意味しない。
