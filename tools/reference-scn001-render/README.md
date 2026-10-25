# TAI SCN-001 review artifact

SCN-001のD-04を、`development-review-only`の仮承認に基づく内部レビュー用Markdownとして生成します。

**公開用の案内ではありません。** 実在の規程・権限・利用者による承認ではなく、公開承認もありません。

## 実行

```text
go test ./...
go run . -fixture ../reference-scn001/testdata/scn001.json -out ../../evaluations/artifacts/SCN-001-D-04-provisional.md
```

生成物: [SCN-001-D-04-provisional.md](../../evaluations/artifacts/SCN-001-D-04-provisional.md)

## 検査

- `provisionalApproval`と`DEC-02`が`development-review-only`である。
- `publicationApproved=false`、`reviewRequired=true`、`reviewTrigger=real-object`。
- D-04が未公開で、実在するobservationだけを参照する。
- `authority.status=unconfirmed`。
- 生成Markdownのdigestを`artifactDigest`へ記録する。

## 境界

- 合成fixtureから生成した参照成果物で、実在の規程を示さない。
- 実物ベースの再レビュー（R-01〜R-07）が完了するまで公開しない。
- 生成物の存在は、内容の正しさ・公開承認・Authorityを証明しない。
