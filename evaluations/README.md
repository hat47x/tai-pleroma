# 評価・検証

統一的な知的機能が実際に成立するかを、再現可能な試験と観測で確かめます。

対象シナリオ・対象版、期待結果、負例、実行条件、結果と未実施項目を記録してください。合成fixture・モック・実環境観測を明確に区別します。機微情報の原本は格納せず、公開可能な証拠への参照を利用します。

## 参照実行の記録

- [SCN-001実物ベース再レビュー](SCN-001-real-object-review.md): `reviewTrigger=real-object`の再レビュー計画。R-01〜R-07は未実施。
- [SCN-001-review-status.json](SCN-001-review-status.json): R-01〜R-07の状態。現在はすべて`pending`で、公開gateはblocked。
- [SCN-001-D-04-provisional.md](artifacts/SCN-001-D-04-provisional.md): 仮承認に基づく内部レビュー用Draft。公開用ではない。
- [SCN-001-run-2026-10-26.json](records/SCN-001-run-2026-10-26.json): MMI・SEI・SCN-001合成評価の統合receipt。`runDigest=sha256:9f82586...`、`humanReviewed=false`、`authorityVerified=false`、`published=false`。`reference-scn001-run`の`-verify`で内部整合を再確認できる。受入合格ではない。
