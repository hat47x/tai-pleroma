# SCN-001 publication gate

実物ベース再レビュー（R-01〜R-07）の状態を読み、公開へ進める条件を満たすかだけを判定します。

**公開を実行しません。** R-01〜R-05は合成文書によるdevelopment review acceptedですが、公開用の実物証拠ではないため、gateはblockedになります。

## 実行

```text
go test ./...
go run . -status ../../evaluations/SCN-001-review-status.json
```

許可される条件:

- R-01〜R-05が`accepted`で、空でないevidenceと`evidenceKind=real-object`を持つ。
- R-06/R-07が`accepted`（evidenceありかつ`evidenceKind=real-object`）または`not-applicable`。
- `evidenceKind=synthetic`のaccepted項目は`developmentAccepted`へ記録し、公開用の`real-object`が必要なためblockedにする。
- `evidenceKind`が`fixture`・`none`などのaccepted項目はblockedにする。
- R-01〜R-07のIDはそれぞれ一度だけ指定する。重複・未知のIDがあれば、行順や値が同じかどうかにかかわらず`allowed=false`とする。
- JSONの同名項目、未知の項目、末尾の追加データを拒否する。大文字小文字やUnicodeのcase foldingで同じ名前になる項目も、重複として扱う。
- schemaまたはscenarioが対象外なら、判定を通さない。
- 上記以外は`allowed=false`、blockerを返す。

## 境界

- review statusの内容が真実であることを検証しない。署名・実在確認は別途必要。重複を拒否しても、証拠の真正性や承認者の権限は確認できない。
- gateの`allowed=true`は公開承認ではなく、入力条件の充足だけを示す。
- 公開・外部作用は実装しない。
- 現在のstatusは[evaluations/SCN-001-review-status.json](../../evaluations/SCN-001-review-status.json)。
