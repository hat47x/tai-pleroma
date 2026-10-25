# SCN-001 publication gate

実物ベース再レビュー（R-01〜R-07）の状態を読み、公開へ進める条件を満たすかだけを判定します。

**公開を実行しません。** 現在のreview statusはPendingのため、gateは必ずblockedになります。

## 実行

```text
go test ./...
go run . -status ../../evaluations/SCN-001-review-status.json
```

許可される条件:

- R-01〜R-05が`accepted`で、空でないevidenceを持つ。
- R-06/R-07が`accepted`（evidenceあり）または`not-applicable`。
- 上記以外は`allowed=false`、blockerを返す。

## 境界

- review statusの内容が真実であることを検証しない。署名・実在確認は別途必要。
- gateの`allowed=true`は公開承認ではなく、入力条件の充足だけを示す。
- 公開・外部作用は実装しない。
- 現在のstatusは[evaluations/SCN-001-review-status.json](../../evaluations/SCN-001-review-status.json)。
