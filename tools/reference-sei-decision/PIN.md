# SEIの版を固定して実行する（任意）

既定の実行は、これまでどおりSEIの`go run ./cmd/sei`を使い、版とcheckoutの状態を**記録するだけ**です。期待するcommitを渡したときだけ、SEIのコードをビルド・起動する前に、checkoutの状態を照合します。外れていれば`passed=false`で止まります。

固定の一致が示すのは、checkoutの**HEAD・追跡内容・Go toolchainが期待と合ったこと**だけです。SEIの正しさ、決定の意味、Authority、公開の承認は示しません。

## 指定の方法

| フラグ | 環境変数 | 意味 |
| --- | --- | --- |
| `-expect-commit <40桁または64桁のhex>` | `TAI_SEI_EXPECT_COMMIT` | SEI checkoutのHEADがこのcommitと一致しなければ失敗する。大文字は小文字にする |
| `-expect-go-version <goX.Y[.Z]>` | `TAI_SEI_EXPECT_GO_VERSION` | `go version`のversionトークンが一致しなければ失敗する（OS・archは含めない）。単独では指定できない |
| `-build-out <dir>` | なし | 固定実行でビルドした`sei`をこのディレクトリに残す。checkoutの外でなければ拒否する。相対パスは呼び出し元のcwd基準の絶対パスにして判定とビルドに使う。期待値なしでは使えない |

フラグが環境変数より優先します。フラグの空値は「期待なし」です。どれかを指定すると固定実行になり、固定実行には`-expect-commit`が要ります（Goのversionだけでは、どのcheckoutを動かしたか分からないため）。形が不正な指定は`invalid-expectation`で失敗します。

```text
go run . -sei-root <sei-checkout> -expect-commit <HEADのhash> -expect-go-version <goのversion>
```

`TAI_SEI_EXPECT_*`を環境に設定したまま`go test`を動かすと、SEI_ROOTのある環境の既存の実SEI試験も固定実行になります。

通常の実行（既定の`Run`）、`-variant`、`-basis-bundle`、`-decision-validity`のすべてが同じ仕組みを通ります。

## 固定実行が起動前に確認すること

1. `runtime/go/cmd/sei`、`go`、`git`があること。
2. SEI rootがgit worktreeの最上位であること（別repoの下位ディレクトリの外側のcommitを借りない）。
3. HEADが期待と一致すること。
4. checkout全体の追跡内容が、HEADと同じであること（ステージ済み・未ステージ・削除・同じサイズの編集を含む。`git diff --binary HEAD`のsha256を使う）。
5. `assume-unchanged`または`skip-worktree`の追跡ファイルが0件であること（編集を隠せるため、あれば`unavailable`）。
6. `runtime/go`以下に、`go build`が取り込み得る未追跡またはgitignore済みのファイル（`.go`、`.s`、`.c`、`.h`など、任意の深さの`go.mod`/`go.sum`/`go.work*`、`vendor/`以下）が無いこと。`runtime/go`の外の未追跡ファイルは件数の記録だけで、失敗にしない。
7. `go version`のトークンが期待と一致すること（`-expect-go-version`を渡したとき）。
8. `GOTOOLDIR`と`GOCACHEPROG`が未設定であり、`GOROOT`が設定されている場合はgo自身のGOROOTと同じであること。違えば`unavailable`。

gitの照会は、`GIT_DIR`・`GIT_WORK_TREE`・`GIT_INDEX_FILE`・`GIT_COMMON_DIR`・`GIT_OBJECT_DIRECTORY`・`GIT_ALTERNATE_OBJECT_DIRECTORIES`を取り除き、`--no-replace-objects`で実行します。`git diff`はindexを書き換えるため、実checkoutの`.git/index`を一時ディレクトリへ複製し、**元のmtimeを保ったまま**`GIT_INDEX_FILE`で読みます（mtimeを失うと、indexと同じ秒に行った同じサイズの編集を見逃す）。実checkoutの`.git`には書きません。

## 固定実行のビルドと実行

- `GOTOOLCHAIN=local`、`GOWORK=off`、`GOFLAGS=-mod=readonly`を、起動する全てのgoコマンドに設定します。継承した`GOFLAGS`は**置き換えられる**ため、ビルドには効きません（`-tags`、`-ldflags`、`-modfile`、`-overlay`など）。receiptにはそのフラグの名前だけを残し、値（パスを含み得る）は残しません。
- `go build -mod=readonly -buildvcs=false -trimpath`で`./cmd/sei`をcheckoutの**外**へビルドし、`go run`は使いません。
- ビルドした`sei`は、空の一時ディレクトリを作業ディレクトリとして動かします。実行後にそこが空でなければ（`--data-root`の渡し忘れの`.sei`など）失敗します。
- 実行前後でcheckoutを比べます（HEAD、追跡内容、未追跡、ビルド入力、隠しフラグ）。変わっていれば`passed=false`です。
- 標準出力だけをJSONとして読みます。標準エラーは捨てます。
- 固定実行のエラーは定型文です。ツールのエラー文、絶対パス、一時ディレクトリ名、`GOFLAGS`の値は、receiptにも失敗理由にも入れません。ビルドが失敗したときは、`runtime/go/go.mod`のgoディレクティブ（数値のみ）とローカルGoのversionを理由に添えます。
- 固定実行の文脈では、`go run ./cmd/sei ...`の形に合わない呼び出しは、`go run`へ戻らずに失敗します。

## 追加のreceiptフィールド

既存の項目の名前・意味、`schema`文字列は変えません。次の4つのキーを足します。

- `pin`: `checked`、`result`（`not-checked`/`match`/`mismatch`/`unavailable`/`invalid-expectation`）、`commit`、`goVersion`、`sourceTree`（`status`と、追跡変更・未追跡・ビルド入力・隠しフラグの件数）。
- `checkout`: `status`（`not-checked`/`unchanged`/`changed`/`unavailable`）と、実行前後の事実（commit、件数、digest）。
- `toolchain`: `goVersionToken`、`goToolchainEnv`、`goFlagNames`、`goWork`（`""`/`off`/`present`。パスは入れない）、`goDirective`、`inheritedSettings`（拘束しない設定のうち、設定されているものの名前だけ）、`enforced`、`build`、`buildFlags`。
- `binary`: `status`、`sha256`（記録のみで照合しない）、`versionLine`（`sei version`の`version`/`commit`/`target`）、`reportedCommit`、`keptAt`（`build-out`のときだけ`"build-out"`。パスは入れない）。

既定（期待値なし）では、`pin.checked=false`で、factsとtoolchainを記録します。checkoutが実行中に変わっても`checkout.status=changed`と記録するだけで、`passed`は変えません。gitが無い、別repoの下位ディレクトリ、といった場合も失敗にせず、`unavailable`と記録して従来どおり実行します。`-basis-bundle`と`-decision-validity`の出力にも、同じ4つのキーが付きます。

## 境界

- `sei version`は`commit: unknown`を返します（ビルド時に埋め込まれない）。よって`binary.reportedCommit`は通常`not-reported`です。ツールが`-ldflags`でcommitを注入することはしません（自己申告になるため）。`sei version`が将来commitを報告し始め、HEADと違えば、固定実行は失敗します。7〜39桁の短縮hashは、HEADの接頭辞かどうかで照合します（`commit`欄だけ。40桁・64桁は欄を問わず全文照合）。
- `//go:embed`と`cgo`は、確認した版の`runtime/go`に無かったことだけを確認しました。他の版では未確認です。埋め込まれたファイルは、名前によらず検出できません。
- `runtime/go`以下にある別のgitリポジトリ（未追跡で`.git`を持つディレクトリ）は、gitが中のファイルを列挙しません。そのためディレクトリ単位でビルド入力として数え、固定実行を`mismatch`にします（中身は見ません）。
- `GOEXPERIMENT`、`CGO_ENABLED`、`GOOS`/`GOARCH`、`CC`、`GOENV`（`go env -w`の設定）は拘束しません。設定されていれば名前を`toolchain.inheritedSettings`に残すだけです。`GOPROXY`なども拘束しません。モジュールの取得は、追跡対象の`go.sum`が検証します。
- storeの中身（実行後に削除される）は比較しません。保証は「checkoutと作業ディレクトリが変わらない」までです。
- このツールにはHTTP/MCPの機能が無いため、プロキシによる迂回や、応答者の識別の対策はありません。何が答えたかの束縛は、`binary.sha256`と`sei version`の出力に限ります。
- 保存済みのreceipt（`evaluations/records/`）には固定情報がありません。同じ合成主張に、別々のSEI commitが引用されています（表の確認したmain、実行ピン、保存済みSEI record、保存済みrun record）。どれを正とするかは決めておらず、固定実行を実SEIで行った後に、Ownerが実物で再審査します。
- 実SEIでの固定実行は、SEIのclone（commit `234c3f91`）をGo 1.26.9（`GOTOOLCHAIN=local`）で1回実施した。`pin.result=match`、`passed=true`、`checkout.status=unchanged`、`recordCount=3`、`sei version`は`commit: unknown`で`reportedCommit=not-reported`だった。誤ったcommitの指定は、ビルドも起動もせずに約1秒で失敗した。SEIの`go.mod`は`go 1.25`で、新しいGoは要らなかった。別の版・別のホストでは未確認。
- `go 1.25`ちょうどのGoでのビルドは未確認です。SEIの`go.mod`が将来、CIのGo（1.26.x）より新しいversionを要求すると、固定実行と実SEIの統合試験は`SEI build failed`で止まります。
- 固定なしの経路は、`resume`と`verify`の標準出力だけをJSONとして読みます（標準エラーの`go: downloading ...`は混ざりません）。`init`/`add`の出力は解析しません。固定実行は`sei`を直接起動し、標準出力だけを返します。
- 偽のSEI（試験用の小さなプログラム）での成功は、ビルドと検査の経路が動くことだけを示します。実SEIの正しさは示しません。

## Owner判断（仮承認）

利用者から仮承認を得て、推奨案で進めました。実物で再審査します。

1. 強制は期待値を渡したときだけとし、既定は記録のみ。
2. 固定なしの実行は`go run`のまま。checkout外ビルドと`sei version`の確認は固定実行だけ（EKIは固定なしもビルドに揃えた。揃えると診断本文が定型化し、実行時間が縮む）。
3. 実行前後のcheckoutの変化は、固定なしでは記録のみで`passed`を変えない（EKIは固定なしでも失敗にした）。共有checkoutを他のセッションが同時に動かすと偶発的に`changed`になり得る点が論点。
4. 固定の主軸はHEAD・追跡内容・Go toolchain。バイナリのsha256は記録のみ。
5. 未追跡・ignoredのビルド入力は`runtime/go`以下に限る（モジュールの根がcheckout直下でないため）。追跡変更はcheckout全体で見る。
6. receiptには継承`GOFLAGS`のフラグ名だけを残す（EKI/MMIは生の値を残していて、絶対パスを含み得る。そちらの修正は別PRで提案）。
7. 固定実行のタイムアウトは既存の120秒のまま。コールドキャッシュのビルドが収まらなければ`SEI build failed`で止まる。延長はOwner判断。
8. どのSEI commitを既定値にするかは決めない。
