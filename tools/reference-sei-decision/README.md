# TAI → SEI decision-memory reference

SCN-001の`DEC-01`を、SEIの一時storeへ合成fixtureとして記録し、`sei resume --json`のprojectionだけを読む参照接続です。

確認するのは、決定がrecommendationに依拠し、`authority:unknown`を未解決として残し、公開・承認済みと扱わないことです。

**実運用のstore・権限・公開を検証しません。** 合成fixtureをSEIの一時storeへ記録するため、SEIの`init`/`add`を使ってから`resume`を読みます。

## 実行

SEIの開発チェックアウトとGoが必要です。

```text
go test ./...
go run . -sei-root ../../../sei-cognition
```

`SEI_ROOT`でも指定できます。

## 確認すること

- `sei init`で一時storeを作る。
- `rec-01`をrecommendationとして記録する。
- `dec-01`をdecisionとして記録し、`rec-01`へ依拠し、`authority:unknown`を未解決に残す。
- `dec-02`をdevelopment-review-onlyの仮承認として記録し、`publication:unapproved`も未解決に残す。
- `sei resume --json`で3 records、`dec-01`/`dec-02`、未解決`authority:unknown`/`publication:unapproved`を確認。
- receiptは`provisionalApproved=true`、`authorityVerified=false`、`humanReviewed=false`、`published=false`。

## 境界

- storeは一時ディレクトリで、終了時に削除する。実在の規程・権限・利用者ではない。
- `resume`はprojectionであり、決定の意味・正しさ・Authorityを証明しない。
- `readOnlyProjection=true`は`resume`の読み取りだけを示し、SEI全体の読取専用を意味しない。
- 実運用の監査、複数利用者、署名、公開は未検証。
