# TAI Pleromaの現在状態

更新日: 2026-10-28。状態: **参照実装と仮承認の記録**。製品受入・公開承認ではない。

## 要約

SCN-001の合成walkthrough、MMI読み取り専用MCP、SEI decision-memory、SUIのcard/island/edge、TEIの型検証、EKIのTask admission/cancel、統合参照実行、D-04レビュー成果物、Owner判断packetまでを参照実装として接続した。

Owner指示（2026-10-26）とOwner判断（2026-10-29）により、`development-review-only`の仮承認でCP-3まで進めている。R-01〜R-05は合成文書でdevelopment review accepted。**公開・外部作用は未承認**であり、公開用の実物レビューを合成後の工程として残す。

## 実装と証拠

| 対象 | 状態 | 証拠 | 限界 |
| --- | --- | --- | --- |
| SCN-001合成walkthrough | 実装済み | [reference-scn001](../tools/reference-scn001/README.md) | 合成fixture。P-06/N-05はnot-run |
| MMI読み取り専用MCP | ローカル参照接続済み | [reference-mmi-readonly](../tools/reference-mmi-readonly/README.md) | ローカル開発チェックアウト限定。実運用の認可・版固定は未確認 |
| SEI decision-memory | 一時storeで3 recordsを参照済み（synthetic） | [reference-sei-decision](../tools/reference-sei-decision/README.md)、[record](../evaluations/records/SEI-decision-2026-10-26.json) | 合成fixture。実store・権限・署名は未確認 |
| 統合参照実行 | 実装済み（SUI linkを含む） | [reference-scn001-run](../tools/reference-scn001-run/README.md)、[record](../evaluations/records/SCN-001-run-2026-10-26.json) | `runDigest`は内部整合のみ。署名・Authorityは未検証 |
| D-04レビュー成果物 | 生成済み | [artifact](../evaluations/artifacts/SCN-001-D-04-provisional.md) | 公開用ではない。実在の規程ではない |
| Owner判断packet | 生成可能 | `-owner-packet` | 承認ではない。実物レビュー待ち |
| 合成後レビュー | 合成でR-01〜R-05をdevelopment accepted。実物は未実施 | [判断](../evaluations/SCN-001-owner-decision-2026-10-29.md)、[計画](../evaluations/SCN-001-real-object-review.md) | R-06/R-07はPending。公開用real-objectは未取得 |
| 生成AI development review | D-04を観点に照らして`quality=sufficient-for-development` | [rubric](../evaluations/SCN-001-ai-development-review-rubric.md)、[receipt](../evaluations/records/SCN-001-ai-review-2026-10-29.json) | 人間レビュー・公開承認ではない |
| 合成フロー接続 | 文書→MMI→SEI→TEI→SUI→D-04→AI review→gateが接続済み | [receipt](../evaluations/records/SCN-001-synthetic-flow-2026-10-29.json) | 実在の規程・権限ではない |
| 公開gate | blocked | [gate](../tools/reference-publication-gate/README.md) | syntheticはdevelopmentAccepted。公開にはreal-objectが必要 |
| TEIモデル検証 | 型宣言をvalidate済み（synthetic） | [reference-tei-model](../tools/reference-tei-model/README.md)、[record](../evaluations/records/TEI-model-2026-10-29.json) | 実データ・意味・Authorityは未検証 |
| SUI API到達性 | `/healthz`・`/openapi.json`・`/docs`・5 card/3 island/1 `contradicts` edgeのDocumentV1 GETを確認済み（synthetic） | [probe](../tools/reference-sui-api/README.md)、[record](../evaluations/records/SUI-api-2026-10-26.json) | 実在のSCN-001資料・テナント・認可は未検証 |
| SUI→SCN-001対応 | card digestとisland構成を照合済み | [link](../tools/reference-sui-link/README.md) | 意味形成の正しさ・実資料は未検証 |
| SUI→D-04対応 | D-04の観測行と公開境界を照合済み | [link](../tools/reference-sui-draft/README.md) | 意味の受理・公開承認は未検証 |
| 合成施設文書の工程検査 | 4種類の工程欠陥を検出済み（synthetic） | [receipt](../evaluations/records/SCN-001-synthetic-facility-2026-10-28.json) | 実物レビューの証拠ではない |
| 合成workspaceのMMI参照 | O-02/O-03/O-06/O-07/O-08の5行を読み取り専用で確認（synthetic） | [receipt](../evaluations/records/SCN-001-synthetic-mmi-2026-10-29.json) | 実資料・実認可ではない |
| 合成receiptの横断検査 | SUI/TEI/SEI/MMI/施設/EKI-envの`synthetic`ラベルをCIで確認 | [checker](../tools/check-synthetic-receipts/README.md) | 実物証拠ではない |
| EKI CLI起動 | `eki-control`/`eki-agent`のversionを確認済み | [probe](../tools/reference-eki-cli/README.md)、[record](../evaluations/records/EKI-cli-2026-10-26.json) | 実Task・委任・Authorityは未検証 |
| EKI Control API認証 | `GET /v1/tasks`の405で認証通過を確認済み | [probe](../tools/reference-eki-api/README.md)、[record](../evaluations/records/EKI-api-2026-10-26.json) | Task送信・委任・Worker・結果検証は未実施 |
| EKI Task admission | 合成Task 1件を`queued`で受理し、同一keyの再送が同じtask_idを返すことを確認済み | [submit](../tools/reference-eki-api/README.md)、[record](../evaluations/records/EKI-task-2026-10-26.json) | Worker未起動。実行・結果・委任完了は未検証 |
| EKI Task cancel | 合成Task 1件を`cancelled`/`CANCELLED`まで確認済み。result APIは501 | [cancel](../tools/reference-eki-api/README.md)、[record](../evaluations/records/EKI-cancel-2026-10-26.json) | Worker未起動。実行・結果は未検証 |
| EKI Worker test環境 | WSL/DockerでAgent/Control test profile、claim wire、Control Planeを確認済み | [worker env](../tools/reference-eki-worker/README.md)、[record](../evaluations/records/EKI-worker-env-2026-10-28.json) | Task実行主体ではなく、結果・委任完了は未検証 |
| EKI Task lifecycle on WSL | `queued`→`cancelled`/`CANCELLED`を確認済み | [worker env](../tools/reference-eki-worker/README.md) | Worker実行・結果は未検証 |
| EKI Native Runner spike | 終了コード・出力上限・期限/取消し・Supervisor接続・Windows/Linuxのプロセスツリー停止を確認。未対応sandbox/資源上限/GPU/digest/引数を拒否 | [eki-fabric #275](https://github.com/hat47x/eki-fabric/pull/275) | sandbox・CPU/メモリ制限なし。未信頼Task不可 |

## 検証

- GitHub Actions `tai-reference`のmatrixで10ツール（SCN-001、MMI、SEI、統合実行、D-04 render、TEI、公開gate、SUI link、SUI→D-04、EKI CLI）を`gofmt`・`go vet`・`go test`。
- 別jobでSUI API/EKI API/EKI Task/公開境界のPython testを実行する。
- MMI/SEIの実接続試験は、sibling checkoutがないCIではskip。
- 保存済みの統合実行recordは常に`runDigest`とcomponent invariantsを検証。
- 2026-10-28時点のmain CIはsuccess。

## 公開状態

- TAI、EKI、SEI、MMIは公開リポジトリ。MITライセンス。
- README先頭に、生成AIを用いた初期開発中のソースコード公開であることを明記。
- 4リポジトリでsecret scanning・push protection・Private vulnerability reportingを有効化。
- TEI Platformの非公開作業資料は非公開を維持し、非公開理由と公開条件を別の非公開リポジトリのREADMEに記録。
- 公開境界の回帰検査をCIで実行。

## 仮承認の境界

- `provisionalApproved=true`、`publicationApproved=false`、`authorityVerified=false`。
- 仮承認の根拠は`owner-instruction-2026-10-26`と`owner-decision-2026-10-29`。
- R-01〜R-05は合成文書でdevelopment accepted。公開用real-objectレビューは合成後の工程へ移す。
- 合成後の実物レビューで前提が崩れた場合は`provisionalApproved=false`へ戻し、D-04を未決へ戻す。
- 公開・外部作用・予約実行は行わない。

## 未確認

- 実在の施設規程・掲示・案内文とD-04の適合。
- 公開権限者の本人・役割・承認範囲。
- MMI/SEIの実運用環境、監査、版固定、複数利用者。
- P-06（主体規模比較）、N-05（EKI委任）。
- 利用者にとっての有用性。

## 次の判断

実物ベース再レビューの担当・日程・証拠の入手方法を決める。実装を先行させる場合は、R-01〜R-05の証拠が揃うまで仮承認の範囲を超えない。
