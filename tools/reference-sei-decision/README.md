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

合成バリエーションは`-variant b`または`-variant c`で記録できます。

```text
go run . -sei-root ../../../sei-cognition -variant b -synthetic -out variant-b.json
```

## 確認すること

- `sei init`で一時storeを作る。
- `rec-01`をrecommendationとして記録する。
- `dec-01`をdecisionとして記録し、`rec-01`へ依拠し、`authority:unknown`を未解決に残す。
- `dec-02`をdevelopment-review-onlyの仮承認として記録し、`publication:unapproved`も未解決に残す。
- `sei resume --json`で3 records、`dec-01`/`dec-02`、未解決`authority:unknown`/`publication:unapproved`を確認。
- receiptは`provisionalApproved=true`、`authorityVerified=false`、`humanReviewed=false`、`published=false`。
- `-synthetic`指定時は`synthetic=true`、`evidenceKind=synthetic`。実物レビューの証拠ではない。

## 境界

- storeは一時ディレクトリで、終了時に削除する。実在の規程・権限・利用者ではない。
- `resume`はprojectionであり、決定の意味・正しさ・Authorityを証明しない。
- `readOnlyProjection=true`は`resume`の読み取りだけを示し、SEI全体の読取専用を意味しない。
- 実運用の監査、複数利用者、署名、公開は未検証。

## 原記録の根拠参照を読む

`resume`は表示用の一覧であり、ExactBindingのscope・digest・表現profileを同じ形で返すものではありません。原記録を確認する場合は、SEIの既存`export`で取得したportable bundleを、次のモードで読みます。

```text
go run . -sei-root ../../../sei-cognition -basis-bundle review-bundle.json -out basis-inspection.json
```

このモードは`init`/`add`を呼びません。入力のbyte列を一時snapshotとして固定し、同じsnapshotについて既存の`sei verify --input`と参照抽出を行います。入力全体の`sourceDigest`、元record ID、元記録内の`jsonPointer`、Decisionの論理参照、`basis_refs`の各項目と値を返します。参照をkind:idだけに縮めず、論理参照とExactBindingの両方を保持します。出力JSONの空白・エスケープ等は再符号化されるため、断片の元byte列の保存を意味しません。

- 認識した`sei.decision-memory/v1alpha1`のDecisionだけを抽出します。未認識Contractは意味を解釈せず、`notVerifiedRecordCount`で残します。抽出0件を「元案件に判断がない」と読み替えません。
- 同じDecision論理IDが複数のrecordにあっても、record IDと元の位置で別々に返します。
- `recordStructureChecked=true`はSEIの構造検査が成功したことだけを示します。`exactTargetsVerified`・`humanReviewed`・`authorityVerified`・`publicationApproved`はすべてfalseです。
- `-out`は既存ファイルを上書きしません。入力と同じパスや、その別名を指定しても、既存ファイルのまま失敗します。
- 不正なUTF-8、同名JSON項目、末尾の追加データを拒否します。値を置換文字で補いません。case foldingで同名になる項目も拒否するため、この診断の受入範囲はSEI本体より狭く、拒否はSEI Contract違反の判定ではありません。

出力は原記録へ戻るための参照資料です。新しい製品間Contractや状態の正本ではありません。参照先の内容・現行性・署名・権限は検証せず、受理の継続・失効・再受理も決めません。既定のSCN-001一時storeによる実行と、そのreceiptは変更しません。
