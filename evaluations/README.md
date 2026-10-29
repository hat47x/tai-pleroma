# 評価・検証

統一的な知的機能が実際に成立するかを、再現可能な試験と観測で確かめます。

対象シナリオ・対象版、期待結果、負例、実行条件、結果と未実施項目を記録してください。合成fixture・モック・実環境観測を明確に区別します。機微情報の原本は格納せず、公開可能な証拠への参照を利用します。

## 参照実行の記録

- [SCN-001実物ベース再レビュー](SCN-001-real-object-review.md): 合成後に行う公開用実物レビューの計画。R-06/R-07は未実施。
- [SCN-001合成施設文書による工程欠陥検査](SCN-001-synthetic-facility-review.md): 創作文書で工程欠陥を検出する検証。実物レビューではない。
- [SCN-001実物レビュー要求の変更](SCN-001-owner-decision-2026-10-29.md): 合成文書によるdevelopment acceptedと、生成AI評価・人間レビュー後置のOwner判断。
- [SCN-001生成AI development reviewの観点](SCN-001-ai-development-review-rubric.md): D-04を確認する5観点。
- [SCN-001-ai-review-2026-10-29.json](records/SCN-001-ai-review-2026-10-29.json): 生成AIによるdevelopment review receipt。`quality=sufficient-for-development`、`humanReviewed=false`。
- [SCN-001-synthetic-facility-2026-10-28.json](records/SCN-001-synthetic-facility-2026-10-28.json): 合成文書の欠陥検査receipt。`synthetic=true`、`publicationAllowed=false`。
- [SCN-001-synthetic-mmi-2026-10-29.json](records/SCN-001-synthetic-mmi-2026-10-29.json): 合成workspaceのMMI読み取り専用receipt。`synthetic=true`、`selectedRows=5`。実認可は未検証。
- [SCN-001-review-status.json](SCN-001-review-status.json): R-01〜R-05は合成で`accepted`/`synthetic`。R-06/R-07は`pending`。公開gateはblocked。
- [SCN-001-D-04-provisional.md](artifacts/SCN-001-D-04-provisional.md): 仮承認に基づく内部レビュー用Draft。公開用ではない。
- [SEI-decision-2026-10-26.json](records/SEI-decision-2026-10-26.json): SEI decision-memoryの合成fixture receipt。`synthetic=true`、`recordCount=3`。
- [TEI-model-2026-10-29.json](records/TEI-model-2026-10-29.json): TEI型検証の合成fixture receipt。`synthetic=true`、`validation=ok`。
- [SUI-api-2026-10-26.json](records/SUI-api-2026-10-26.json): SUI APIの`/healthz`、`/openapi.json`、`/docs`、5 card/3 island/1 edgeのDocumentV1 GET record。`synthetic=true`。実資料・認可・SCN-001データは未検証。SUI→SCN-001対応は[reference-sui-link](../tools/reference-sui-link/README.md)で照合。
- [EKI-cli-2026-10-26.json](records/EKI-cli-2026-10-26.json): `eki-control`/`eki-agent`のversion起動record。Task・委任・Authorityは未検証。
- [EKI-api-2026-10-26.json](records/EKI-api-2026-10-26.json): EKI Control APIの`GET /v1/tasks`が405を返し、Client credentialの認証通過を確認したrecord。
- [EKI-task-2026-10-26.json](records/EKI-task-2026-10-26.json): 合成Task 1件を`queued`で受理し、同一Idempotency-Keyの再送が同じtask_idを返したrecord。Worker未起動のため、実行・結果・委任完了は未検証。
- [EKI-cancel-2026-10-26.json](records/EKI-cancel-2026-10-26.json): 合成Task 1件を`cancelled`/`CANCELLED`まで確認したrecord。Worker未起動のため、実行・結果は未検証。
- [SCN-001-run-2026-10-26.json](records/SCN-001-run-2026-10-26.json): MMI・SEI・SCN-001合成評価の統合receipt。`runDigest=sha256:53600dc...`、`humanReviewed=false`、`authorityVerified=false`、`published=false`。`reference-scn001-run`の`-verify`で内部整合を再確認できる。受入合格ではない。
