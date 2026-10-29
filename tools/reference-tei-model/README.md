# TAI → TEI read-only model validation

SCN-001の`Observation`と`RuleCandidate`をTEIの型宣言として置き、TEIの`validate`だけを実行する読み取り専用接続です。

**実データ・意味・Authorityを検証しません。** TEIのモデル構造が成立することだけを確認します。

## 実行

TEIの開発チェックアウトとGoが必要です。

```text
go test ./...
go run . -tei-root ../../../tei-platform -workspace testdata/workspace
```

`TEI_ROOT`でも指定できます。

## 確認すること

- `tei.workspace.yaml`と`semantic/guidance.tei`が存在する。
- `tei validate`が`ok`を返す。
- workspaceの全ファイルdigestが呼出し前後で不変。
- `teiCommit`、`goVersion`、`workspaceDigest`をreceiptへ記録。
- `-synthetic`指定時は`synthetic=true`、`evidenceKind=synthetic`。実物レビューの証拠ではない。

## 境界

- `Observation`と`RuleCandidate`は型宣言だけで、SCN-001の実データではない。
- TEIの意味受理・規程確定・実Targetは未検証。
- validateの成功はモデル構造の成立だけを示し、内容の正しさを証明しない。
- 実運用の認可・監査・版固定は未確認。
