# TAI Pleromaの現在状態

更新日: 2026-10-26。状態: **参照実装と仮承認の記録**。製品受入・公開承認ではない。

## 要約

SCN-001の合成walkthrough、MMI読み取り専用MCP、SEI decision-memory、統合参照実行、D-04レビュー成果物、Owner判断packetまでを参照実装として接続した。

Owner指示（2026-10-26）により、`development-review-only`の仮承認でCP-3まで進めている。**公開・外部作用は未承認**であり、`reviewTrigger=real-object`で実物ベースの再レビューを要する。

## 実装と証拠

| 対象 | 状態 | 証拠 | 限界 |
| --- | --- | --- | --- |
| SCN-001合成walkthrough | 実装済み | [reference-scn001](../tools/reference-scn001/README.md) | 合成fixture。P-06/N-05はnot-run |
| MMI読み取り専用MCP | ローカル参照接続済み | [reference-mmi-readonly](../tools/reference-mmi-readonly/README.md) | ローカル開発チェックアウト限定。実運用の認可・版固定は未確認 |
| SEI decision-memory | 一時storeで参照済み | [reference-sei-decision](../tools/reference-sei-decision/README.md) | 合成fixture。実store・権限・署名は未確認 |
| 統合参照実行 | 実装済み（SUI linkを含む） | [reference-scn001-run](../tools/reference-scn001-run/README.md)、[record](../evaluations/records/SCN-001-run-2026-10-26.json) | `runDigest`は内部整合のみ。署名・Authorityは未検証 |
| D-04レビュー成果物 | 生成済み | [artifact](../evaluations/artifacts/SCN-001-D-04-provisional.md) | 公開用ではない。実在の規程ではない |
| Owner判断packet | 生成可能 | `-owner-packet` | 承認ではない。実物レビュー待ち |
| 実物ベース再レビュー | 未実施 | [計画](../evaluations/SCN-001-real-object-review.md) | R-01〜R-07はPending |
| 公開gate | blocked | [gate](../tools/reference-publication-gate/README.md) | R-01〜R-05のaccepted証拠がない |
| TEIモデル検証 | 型宣言をvalidate済み | [reference-tei-model](../tools/reference-tei-model/README.md) | 実データ・意味・Authorityは未検証 |
| SUI API到達性 | `/healthz`・`/openapi.json`・`/docs`・3 card/2 island/1 edgeのDocumentV1 GETを確認済み | [probe](../tools/reference-sui-api/README.md)、[record](../evaluations/records/SUI-api-2026-10-26.json) | 実在のSCN-001資料・テナント・認可は未検証 |
| SUI→SCN-001対応 | card digestとisland構成を照合済み | [link](../tools/reference-sui-link/README.md) | 意味形成の正しさ・実資料は未検証 |
| SUI→D-04対応 | D-04の観測行と公開境界を照合済み | [link](../tools/reference-sui-draft/README.md) | 意味の受理・公開承認は未検証 |
| EKI CLI起動 | `eki-control`/`eki-agent`のversionを確認済み | [probe](../tools/reference-eki-cli/README.md)、[record](../evaluations/records/EKI-cli-2026-10-26.json) | 実Task・委任・Authorityは未検証 |
| EKI Control API認証 | `GET /v1/tasks`の405で認証通過を確認済み | [probe](../tools/reference-eki-api/README.md)、[record](../evaluations/records/EKI-api-2026-10-26.json) | Task送信・委任・Worker・結果検証は未実施 |
| EKI Task admission | 合成Task 1件を`queued`で受理済み | [submit](../tools/reference-eki-api/README.md)、[record](../evaluations/records/EKI-task-2026-10-26.json) | Worker未起動。実行・結果・委任完了は未検証 |
| EKI Task cancel | 合成Task 1件を`cancelled`/`CANCELLED`まで確認済み | [cancel](../tools/reference-eki-api/README.md)、[record](../evaluations/records/EKI-cancel-2026-10-26.json) | Worker未起動。実行・結果は未検証 |

## 検証

- GitHub Actions `tai-reference`のmatrixで9ツール（SCN-001、MMI、SEI、統合実行、D-04 render、TEI、公開gate、SUI link、EKI CLI）を`gofmt`・`go vet`・`go test`。
- 別jobでSUI API probeとEKI API probeのPython testを実行する。
- MMI/SEIの実接続試験は、sibling checkoutがないCIではskip。
- 保存済みの統合実行recordは常に`runDigest`とcomponent invariantsを検証。
- 2026-10-26時点のmain CIはsuccess。

## 仮承認の境界

- `provisionalApproved=true`、`publicationApproved=false`、`authorityVerified=false`。
- 仮承認の根拠は`owner-instruction-2026-10-26`。
- 実物レビューR-01〜R-05が揃わない場合は、`provisionalApproved=false`へ戻し、D-04を未決へ戻す。
- 公開・外部作用・予約実行は行わない。

## 未確認

- 実在の施設規程・掲示・案内文とD-04の適合。
- 公開権限者の本人・役割・承認範囲。
- MMI/SEIの実運用環境、監査、版固定、複数利用者。
- P-06（主体規模比較）、N-05（EKI委任）。
- 利用者にとっての有用性。

## 次の判断

実物ベース再レビューの担当・日程・証拠の入手方法を決める。実装を先行させる場合は、R-01〜R-05の証拠が揃うまで仮承認の範囲を超えない。
