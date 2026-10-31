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

既定の実行は記録だけです。期待値を渡さない限り、commitの不一致や未コミットの変更で失敗にはしません（例外は、実行中のcheckout書き換えの検出。Owner判断7）。

## 版を固定して実行する（任意）

期待値を1つでも渡すと固定実行になります。

```text
go run . -eki-root ../../../eki-fabric \
  -expect-commit <40桁または64桁のcommit> -expect-go-version go1.27.3 \
  -build-out ../../../eki-build
```

| 項目 | フラグ | 環境変数 |
| --- | --- | --- |
| 期待するEKIのcommit | `-expect-commit` | `TAI_EKI_EXPECT_COMMIT` |
| 期待する`go version`のtoken | `-expect-go-version` | `TAI_EKI_EXPECT_GO_VERSION` |
| ビルドしたバイナリを残すdir（checkout外） | `-build-out` | なし |

フラグが環境変数より優先され、空値は期待なしです。固定実行ではcommitが必須で、`-expect-go-version`だけでは`invalid-expectation`になります。小文字のhexに揃えます。

固定実行は、**EKIのコードをビルド・起動する前に**次を確認し、1つでも外れれば`passed=false`で止まります。

- checkoutの`HEAD`が期待commitと一致する。checkoutがgit toplevelでない（別repoの下位dir）ときは`unavailable`。
- 追跡ファイルの変更（staged・unstaged・削除・同サイズの編集）がない。内容は`git diff HEAD`で見るので、CRLFの作業コピーだけでは差にならない。
- `assume-unchanged`/`skip-worktree`の追跡ファイルがない（編集が見えないので`unavailable`）。
- 追跡外・無視された**Goのビルド入力**がない（`.go` `.s` `.c` `.h`等、`go.mod` `go.sum` `go.work*`、`vendor/`）。READMEなどの追跡外ファイルは件数を残すだけで失敗にしない。
- `go version`が期待と一致する。
- `GOFLAGS`に`-modfile`/`-overlay`がない。

gitの事実は、`--no-replace-objects`で、`GIT_DIR`等の環境変数を除いて取ります。indexは元のmtimeを保ったまま一時dirへ複製し、`GIT_INDEX_FILE`でその複製だけを読みます（racy-gitで同サイズの編集を見落とさないため。共有checkoutの`.git`は書き換えません）。

固定実行は、すべてのgoコマンドに`GOTOOLCHAIN=local` `GOWORK=off` `GOFLAGS=-mod=readonly`を付けます。固定でない実行は環境を引き継ぎ、`toolchain`に記録します。

ビルドは固定でも固定でなくても`go build -mod=readonly -buildvcs=false -trimpath`でcheckoutの**外**へ出力します（`go run`は使いません）。バイナリは空の一時dirで`--version`だけ実行します。`-build-out`がcheckout内（symlink経由を含む）を指すときは起動前に失敗します。実行の前後にcheckoutの状態を比べ、変化があれば固定の有無によらず`passed=false`、`readOnly=false`です（reasonは変化した項目名だけで、内容は入れません）。

ビルド後に判る版出力の確認だけは、起動前の規則の例外です。`eki-control <token>`と`eki-agent <token>`の形で、tokenが一致しなければ固定実行は失敗します。出力にcommitのhex（40/64桁）があればHEADと照合します。

## 確認すること

- `eki-control --version`と`eki-agent --version`が起動する。
- `ekiCommit`、`goVersion`、各version文字列をreceiptへ記録。
- `readOnly=true`、`taskDelegated=false`、`authorityVerified=false`。
- 追加フィールド（既存のschema `tai.reference.eki-cli/v0`と既存フィールドは変えない）:
  - `pin`: 期待値と実際（commit・go version・追跡内容）。既定は`checked=false`。
  - `checkout`: 実行前後の状態と`unchanged`/`changed`。
  - `toolchain`: Goのtoken、引き継いだ`GOTOOLCHAIN`/`GOFLAGS`/`GOWORK`、強制した値、ビルドの結果とフラグ。
  - `binaries`: 作ったバイナリのsha256、version出力の1行、一致の有無、`reportedCommit`。
- 失敗のreasonは定型文だけです。goやgitのエラー文、絶対パスは入れません。

## 境界

- EKIのTask、Worker、委任、結果検証、Authorityは未検証。
- `eki-control`はM0 skeletonで、実運用のControl Planeではない。
- version表示は機能の実装・受入を証明しない。
- **`--version`は`dev`だけを出し、commitを報告しない**（EKI `84f03d1`から`934069a`までの5つのcommitで確認）。`versionAgreement=agree`は同じcommitのバイナリであることを何も示さない。固定の中身は、checkoutのHEAD・追跡内容・Go toolchainだけである。バイナリのsha256は記録するだけで、このCLIは期待値と照合しない（`reference-eki-api`の`--expect-control-sha256`へ渡す値として使える）。`reportedCommit=not-reported`のまま`pin.result=match`になる。
- pinの一致は、HEAD・追跡内容・toolchainが期待と合ったことだけを示す。EKIの正しさ、実行結果、Authorityは示さない。
- 追跡外・無視された非Goのファイルや、`//go:embed`で取り込まれる任意名のファイルは見えない（未確認の限界）。cgo、環境変数、モジュールのダウンロード元も固定しない。
- EKIの`go.mod`は`go 1.27.0`で、Go 1.26ではビルドできない。固定実行はビルド失敗（reason `EKI build failed`）になる。実EKIの試験はGo 1.27以上があるときだけ走り、CIのGo 1.26.xでは必ずskipする。
- `reference-eki-api`が同じバイナリの応答を確認できるように`-build-out`を使う。別ホスト・別Goで同じsha256になるかは未確認（同一ホストで2回のビルドが一致したことだけ測定した）。
- 実EKIの試験は環境変数の期待値からだけ走る（`TAI_EKI_EXPECT_COMMIT`、`TAI_EKI_EXPECT_GO_VERSION`）。コードに実commitは書かない。

## Owner判断（仮承認。実物に当てて再審査する）

1. 既定は記録のみ。強制はフラグ・環境変数を渡したときだけ。
2. 非固定の実行も`go run`をやめ、`go build -buildvcs=false -trimpath`でcheckout外にビルドして実行する。reasonは定型文になり、エラー詳細は失われる（診断は減る）。
3. 版の主軸は、`--version`ではなく、checkoutのHEADと追跡内容（ビルドしたバイナリのsha256は記録のみ）。EKIがversionにcommitを出すようになれば、`reportedCommit`を必須に強められる。EKI側の変更は求めない。
4. 固定実行のtoolchainは`GOTOOLCHAIN=local`。Go 1.27未満では実EKIを固定できない。`GOTOOLCHAIN=auto`は版の保証が弱くなるので許さない。
5. どのEKIの版を固定するかは決めない（既定値なし）。記録は`84f03d1`（capability-inventoryの表）、`6daa15c`/`a578b05`（保存済みrecord）、`critical-path`の`6daa15c`で揃っておらず、呼び出し側が明示する。
6. untracked/ignoredで失敗にするのはGoのビルド入力だけ。全件を失敗にすると誤検出が増える。
7. 実行中のcheckout書き換えの検出は、期待値の有無によらず常に有効（`readOnly=true`という既存の主張を偽にしないため）。これは「既定は記録のみ」の例外で、従来の既定の失敗条件（version出力が空など）に加わる。期待commitの不一致や、実行前から存在する未コミットの変更では既定の実行は失敗にしない。共有checkoutを他の作業が同時に動かすと偶発的に`changed`になり得るので、その場合はreceiptの`checkout`を見て再実行する。
