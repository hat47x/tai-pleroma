# TAI → EKI CLI build probe

EKIの`eki-control`と`eki-agent`のversion表示だけを確認する参照です。

**Taskの委任・Worker・Authority・結果検証は行いません。** EKIのビルドとCLI起動が成立することだけを確認します。

## 実行

EKIの開発チェックアウトとGoが必要です。

```text
go test ./...
go run . -eki-root ../../../eki-fabric
```

`EKI_ROOT`でも指定できます。

## 確認すること

- `eki-control --version`と`eki-agent --version`が起動する。
- `ekiCommit`、`goVersion`、各version文字列をreceiptへ記録。
- `readOnly=true`、`taskDelegated=false`、`authorityVerified=false`。

## 境界

- EKIのTask、Worker、委任、結果検証、Authorityは未検証。
- `eki-control`はM0 skeletonで、実運用のControl Planeではない。
- version表示は機能の実装・受入を証明しない。
