# 応答を失ったあとの回復判断：実EKIでの1件

状態: **観測記録**。EKIの仕様変更の提案ではなく、TAIが外部Effectの「不明」をどう読み、何を再試行してよいかの根拠である。
対象: [TAI #531](https://github.com/hat47x/tai-pleroma/issues/531) OX-04（Commit後の応答喪失）、OR-04、OR-11。[SCN-001 成果の観測](SCN-001-outcome-observation-2026-11-11.md)で自己試験にとどまっていた O7 の実プロセス版。
記録: [EKI-lost-acknowledgement-2026-11-12.json](records/EKI-lost-acknowledgement-2026-11-12.json)。実験の原文: [lost_ack_process_test.go.txt](tools/eki-lost-ack/lost_ack_process_test.go.txt)。

## 1. 何をしたか

- EKI main `72f4a1842fa60380b8c0ae3eb91e8914de224676` から `eki-control` と `eki-agent` をビルドした（`modified=false`）。WSL2 Ubuntu、Go 1.27.0。
- EKI既存のプロセス試験の補助関数を使い、実プロセス2本をmTLSでつないだ。Client APIからTaskを投入し、Agentが固定コマンドを実行する。
- AgentとControl Planeの間に、TCPをそのまま通す中継を置いた。中継は通信の中身を読めない。切替後は、**要求はControl Planeへ届け、TLSハンドシェイク後の応答だけを捨てて**Agent側を切断する。
- EKI本体のコードは変更していない。実験ファイルはスクラッチのcloneに置いただけで、EKIへはcommitしていない。

コマンドの実行回数は、コマンド自身がファイルへ1行追記することで数えた。

## 2. 観測

3回実行し、3回とも同じ結果だった。障害を入れない既存試験2件（`TestAgentSendsTheBodyItsRunnerProduced`、`TestHTTPTaskSubmissionIsExecutedByTheAgent`）は同じバイナリでPASSした。

応答を失っている間：

| 観測者 | 見えたもの |
| --- | --- |
| Agent | `result_claim_delivery_failed` が1件。受理確認は受け取っていない |
| Control Planeの記録（SQLiteを直接読取） | ResultClaimは**記録済み** |
| Client API `GET /v1/tasks/{id}` | `status: verifying` |
| Client API `GET /v1/tasks/{id}/result` | 409 |
| 成果物の保管先 | 出力本体は無い |

経路を戻したあと：

| | 同じAgentが再送 | Agentを再起動してから再送 |
| --- | --- | --- |
| 再送したclaimへの判定 | `duplicate` | `duplicate` |
| コマンドの実行回数 | 1 | 1 |
| TaskのAttempt数 | 1 | 1 |
| 出力本体 | **保管された** | **失われた** |
| 本体に関するAgentのevent | `claim_body_sent` | **何も出ない** |
| Client APIのstatus／result | `verifying`／409 | `verifying`／409 |

Clientが同じTaskを投入し直した場合：同じ `Idempotency-Key` は 202・`replayed:true`・同じ `task_id`。新しいkeyは 202 で**別のTask**を作る。

## 3. 分かったこと

1. **「不明」は観測者ごとに違う。** 同じ時点で、Agentにとっては不明、Control Planeにとっては既知だった。Effectの不明は「誰にとって」を付けて記録する。
2. **不明を既知に変えるのは、同じ識別子でProvider側を読むことである。** `task_id` で読めば `verifying` と `attempt_count=1` が返り、claimが届いたことは外から分かる。
3. **同じ識別子での再試行は安全だった。** 同じclaimの再送も、同じ `Idempotency-Key` の再投入も重複排除され、実行は1回のままだった。Control Planeを強制終了して再起動しても、記録済みのclaimは残り、再送は `duplicate` だった。
4. **新しい識別子での再試行は安全ではない。** 新しいkeyは別のTaskを作る。応答が無かったことを理由に識別子を作り直すと、作業が重複する。
5. **Client APIが区別できるのは、claimの記録の有無までである。** 要求がControl Planeへ届かなかった場合は `running`、claimが記録された場合は `verifying` で、読むだけで区別できた。一方、「claimも本体もある」と「claimはあるが本体は失われた」は、どちらも `verifying`／409 で同じに見える。本体の有無が分かったのは、成果物の保管先とSQLiteを直接読んだときだけである。Agentを再起動した場合、本体が失われたことを示すeventも出ない。
6. **要求が飲み込まれている間、Agentは何も報告しない。** 10秒の観測中、`result_claim_delivery_failed` は0件だった。「失敗」がeventとして現れるのは、Agent側の要求が失敗してからである。
7. **20秒遅れた受理確認は、Agentが再送せずにそのまま受理した。** 遅延が長い場合のAgent側の待ち時間（要求のtimeout）は読んでおらず、20秒より長い遅延は試していない。

### 補足：Control Plane再起動の変種で2回止まった

`control-restart` の変種は23回実行して21回完了し、2回は、claimの記録とAgentの失敗eventを待つ最初の待機で進まなかった。1回は待機の位置を確認できた。もう1回は位置を確認していない。その後14回連続で再現しなかった。原因は特定しておらず、中継の側にあるのか、EKIの側にあるのかは分からない。完了した21回の結果は同じである。

## 3b. 自己申告の承認は、実EKIの受付でどう扱われたか（2026-11-13追加）

[SCN-001 成果の観測](SCN-001-outcome-observation-2026-11-11.md)の反例O4（承認の自己申告）が、自己試験にとどまっていた。EKIの受付（Client API）に、承認を装う要求を12通送った。Agentは動かしておらず、何も実行していない。記録: [EKI-self-declared-approval-2026-11-13.json](records/EKI-self-declared-approval-2026-11-13.json)。

| 要求 | 応答 |
| --- | --- |
| 正しい要求 | 202 |
| トークンなし、誤ったトークン、Workerのトークン | 401 `AUTHENTICATION_REQUIRED` |
| 方針で承認されていないexecutor | 422 `executor-not-approved` |
| `effect_mode` が `external`、`write` | 400（`none` のみ許可） |
| 項目 `approved`、`approval` を付けた要求 | 400（未知の項目） |
| **自由形式の `parameters` の中に `approved_by: owner` を書いた要求** | **202（受理）** |
| 方針を超える資源、不正な優先度 | 400 |

分かったこと：
- 承認を**構造として**主張する要求（未知の項目）は拒否され、権限は**主体（トークン）とoperatorの方針**で決まった。
- 自由形式の欄に承認の文言を書いた要求は受理された。EKIはそれを権限として扱わない不活性なデータだが、**受理されたことは承認の証拠ではない**。TAIは、自由形式の欄にある承認の文言を権限として読まない。
- EKIの受付に**人間の承認という概念は無い**。SCN-001の「公開の承認」に相当する実Productの観測は、EKIからは得られない。O4の実試験は、Ownerの承認を持つProductがあって初めて成り立つ。

未確認：自由形式の欄を下流のexecutorが読んだ場合の挙動。

## 4. TAIが守る読み方

新しい機構は足さない。識別子はProviderが持ち、TAIは参照だけを持つ。

| 状況 | TAIの記録 | してよいこと | してはいけないこと |
| --- | --- | --- | --- |
| 応答が無い | Effect＝unknown（観測者を明記） | 同じ識別子でProviderを読む | 失敗と記録する。成功と記録する |
| 読取で「claimの記録なし」（`running`） | 受領側にとってはnone。Agent側は実行済みの可能性が残る（unknown） | 同じ識別子で再送する。実行の有無はAgentに尋ねる | 実行されていないと推定する |
| 読取で記録を確認 | Effect＝known。ただし成果物の受領は別 | 同じ識別子で再送する | 新しい識別子で投入し直す |
| 読取で「無い」を確認 | Effect＝none | 同じ識別子で再送する | 「無い」をProvider以外の情報から推定する |
| 読取ができない | unknown のまま保持 | 待つ。権限のある人へ渡す | 再実行する |
| 記録はあるが成果物を確認できない | Effect＝partial | 成果物を所定の受取先から読み直す | claimの記録を成果物の受領と読む |

識別子の持ち主：

| 識別子 | 持ち主 | TAIの扱い |
| --- | --- | --- |
| `Idempotency-Key`（Taskの投入） | 投入したClient | 再投入に同じ値を使う。値を作り直さない |
| `task_id` | EKI | 読取の鍵として参照する |
| Attemptとclaimの同一性 | EKI（AgentとControl Plane） | 関与しない |
| 出力本体のdigest | EKI | 受領の照合に使う。本体の所在はEKIに尋ねる |

## 5. 範囲と未実施

- 観測したEffectは、EKI自身の記録（ResultClaim）である。EKIが受け付けるのは `effect_mode: none` だけなので、**業務上の外部作用は試していない**。
- Taskは終端状態に達していない。結果受理の実行系は起動経路に配線されておらず（[EKI #242](https://github.com/hat47x/eki-fabric/issues/242)）、受理済み結果の読取は確認できない。
- 両プロセスは同一ホスト・同一操作者。独立したVerifier、本番の権限、実Providerは無い。
- 中継の障害は四種類（応答の廃棄、要求の廃棄、20秒の応答遅延、廃棄後のControl Plane強制終了と再起動）。それ以外の障害、20秒を超える遅延、Agent側のtimeoutの値は未確認。
- 本体が失われたあとの回復（同じAttemptでの本体再送、新しいAttempt）は、EKIに経路が無いので試していない。採否はEKI Ownerの判断である（[EKI #465](https://github.com/hat47x/eki-fabric/issues/465)のClose時に未決として残された項目）。
- SCN-001のD-04の生成をEKIが担ったわけではない。SCN-001の公開（P-Publish）は従来どおり未達である。

## 6. 再現

```text
# EKIを 72f4a184 でcloneし、Go 1.27 で実行する（Linux）
cp evaluations/tools/eki-lost-ack/lost_ack_process_test.go.txt \
   <EKI>/conformance/process/zz_effect_unknown_test.go
cd <EKI> && go test ./conformance/process -run TestLostAcknowledgement -count=3 -v
```

出力の `TASK6_OBS` 行が観測値である。実験ファイルはEKIへcommitしない。
