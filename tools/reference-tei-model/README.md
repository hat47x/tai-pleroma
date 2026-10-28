# TAI → TEI read-only model validation

SCN-001の`Observation`と`RuleCandidate`をTEIの型宣言として置き、TEIの読み取り専用コマンド`validate`（テキストと`-json`）と`model catalog`だけを実行する接続です。

**実データ・意味・Authorityを検証しません。** TEIのモデル構造が成立し、宣言した型がTEIに読み込まれたことだけを確認します。

## 実行

TEIの開発チェックアウトとGoが必要です。TEIの`go.mod`が求めるGoと依存moduleは、TEI側の定義に従います。TEIまたは`go`がない環境では、TEIの実接続試験だけがskipされます。偽のTEIを使う負例は実行され、偽のGit repositoryを使う試験は`git`がなければskipされます。

```text
go test ./...
go run . -tei-root <TEIのcloneのパス> -workspace testdata/workspace
```

TEIの場所は`-tei-root`または`TEI_ROOT`で指定できます。省略時は`../../../tei-platform`を使います。`go test`のTEI実接続試験は、`TEI_ROOT`を指定したときだけ実行します（兄弟ディレクトリへの既定は使いません）。他のセッションが編集中の共有チェックアウトではなく、専用のcloneを指してください。呼出し前後の比較は、他者による編集もTEIによる書込みと見分けられないためです。

この接続は、TEIの`cmd/tei`を`go build -mod=readonly -buildvcs=false`でTEIのチェックアウトの外の一時ディレクトリへ1回だけビルドし、同じバイナリで3つの呼出しを行います。`go run`は呼出しのたびにリンクし直すため使いません。`-buildvcs=false`がないと、`go build`は`git status`をTEIのチェックアウトで実行し、`.git/index`を書き換え得ます（測定済み）。TEIの初回ビルドは、ビルドキャッシュが空だと環境により25秒から4分以上かかります（下の「測定した値」）。

偽のTEIの試験は、実測した出力の形に合わせた合成です。通っても、実際のTEIが同じ形で応答することの確認にはなりません。TEIでの確認は、実接続試験で行います。

## 確認すること

- `tei.workspace.yaml`と`semantic/guidance.tei`が存在する。
- `tei validate -workspace`が`ok`だけを出力し、終了コード0で終わる（TEIのコードの読解では、警告があると`ok`の前に診断の行が出るため失敗します。警告を出すworkspaceでの実測は未確認です）。
- `tei validate -workspace -json`の`schemaVersion`が`tei.cli.validate/v0`で、`ok=true`、error診断なし、終了コード0であり、テキストの`ok`と矛盾しない。
- `tei model catalog -workspace`が、宣言した`Observation`と`RuleCandidate`の全attributeとその型を過不足なく返す（`validate`の`ok`は、型が1つもないworkspaceでも返るため、型が読み込まれたことは示しません）。
- workspaceの全ファイルdigest（`workspaceDigest`）と、空ディレクトリ・symlinkの指す先を含むtree digest（`workspaceTree`）が呼出し前後で不変。
- TEIのチェックアウトの`HEAD`、追跡対象の変更（件数と差分のdigest）、未追跡ファイル（件数と名前のdigest）、未追跡または`.gitignore`対象のGoビルド入力（件数と名前のdigest）、`assume-unchanged`／`skip-worktree`の印が付いた追跡ファイルの件数が、呼出し前後で不変（`checkout`）。
- receiptに`teiCommit`、`goVersion`（`go version`の出力）、`toolchain`、`workspaceDigest`、TEIチェックアウトの状態を記録する。期待値を指定したときだけ、commitなどを照合する。

`readOnly`は、呼出しの前後でworkspaceまたはTEIのチェックアウトの変化を観測したときだけ`false`になります（観測した書込みの記録であり、書込めないことの証明ではありません）。この変化は、版を固定しない実行でも`passed=false`です。TEIが`readOnly`と宣言するコマンドだけを呼んでいるため、観測した書込みはTEIの版の違いではなく、その実行の事実の不一致だからです。

## 版を固定して実行する（任意）

既定では、TEIのcommitとGo versionを**記録するだけ**です（receiptの`pin.checked=false`）。この実行は、接続したTEIが文書に書かれた版と同じかを示しません。TEIのチェックアウトが別のcommitでも、追跡対象の変更があっても、既定の実行は失敗しません（記録します）。

期待値を指定すると、次を満たさない実行は`passed=false`になり、TEIのコードをビルドする前に止まります。

- `-expect-commit`（必須）: TEIチェックアウトの`HEAD`（40桁の16進）。TEIのディレクトリがGit repositoryのルートでない場合は取得できず、失敗します（別のrepositoryの内側にあるときに、外側のcommitを使いません）。
- `-expect-go-version`: `go version`の版の語（例: `go1.26.9`。OSとarchは含めない）。TEIのcheckoutで`go version`を実行して取ります。
- `-expect-go-version`だけを指定した場合は、`-expect-commit`がないため失敗します。Go versionはTEIのどのcommitを実行するかを示さないためです。
- 追跡対象ファイルに変更（ステージ済み・未ステージ・削除）があると失敗します。`assume-unchanged`または`skip-worktree`の印が付いた追跡ファイルがある場合も、その編集を見分けられないため失敗します。比較では`refs/replace`（`git replace`）を無視します。TEIの`.git/index`は書き換えず、複製した写しに対してgitを実行します（`git diff`は`--no-optional-locks`を付けても渡されたindexを更新するため）。写しには元のindexの更新時刻を引き継ぎます。引き継がないと、indexを書いたのと同じ秒に行った同サイズの編集を、gitが見落とします（測定済み）。
- 追跡されていない、または`.gitignore`の対象になっているGoのビルド入力が1件でもあると失敗します（`pin.sourceTree.untrackedBuildInputs`）。`cmd/tei`に未追跡の`.go`ファイルがあると、`HEAD`も追跡対象ファイルも変わらないまま、別のプログラムがビルドされるためです。対象は、拡張子が`.go`・`.s`・`.S`・`.sx`・`.c`・`.h`・`.syso`など、`go build`が取り込むソースの種類のファイルと、深さを問わない`go.mod`・`go.sum`・`go.work*`、ルートの`vendor/`以下です。判定は名前によるため、Goに使われないファイル（例: `.gitignore`の対象のディレクトリにある`.c`や`.h`）も数え、失敗にします（誤検出は失敗側です）。それ以外の未追跡ファイルは、件数を記録するだけで失敗にしません。
- 取得できない値（gitがない、`go`がない）を期待した場合も失敗です。`GOFLAGS`に`-modfile`または`-overlay`があると、コンパイルされるものがcommitと一致しないため失敗します。
- `validate -json`がテキストの`ok`と一致する形で得られない場合、`model catalog`が宣言した型と結び付かない場合も失敗します。版を固定しない実行では、これらは記録のみです（ただしTEIの2つの出力が互いに矛盾する場合は、固定の有無にかかわらず失敗します）。
- 固定した実行は、`go version`と`go build`の環境に`GOTOOLCHAIN=local`、`GOWORK=off`、`GOFLAGS=-mod=readonly`を与え、呼出し元の値を置き換えます（`toolchain.enforced`に記録）。呼出し元の値の記録（`toolchain.goToolchainEnv`・`goFlags`・`goWork`）のために読む`go env`だけは、呼出し元の環境のまま実行します。
  - `GOTOOLCHAIN=local`: TEIの`go.mod`が求めるGoが入っていない環境で、別のtoolchainを自動取得せず、失敗します。
  - `GOWORK=off`: `go.work`がTEIのmodule版を変えることを防ぎます。
  - `GOFLAGS=-mod=readonly`: 環境変数やgo envファイルの`GOFLAGS`（`-tags`、`-ldflags`、`-gcflags`など）は、ファイルを1つも変えずに別のプログラムをビルドさせます。値は空にしません。環境変数の空の`GOFLAGS`は、go envファイルの`GOFLAGS`を打ち消さないためです（測定済み）。置き換える前の値は`toolchain.goFlags`に記録します。

```text
go run . -tei-root <TEIのcloneのパス> -workspace testdata/workspace \
  -expect-commit <TEIのcommit（40桁）> \
  -expect-go-version go1.26.9
```

期待するcommitは、使うTEIのcloneで`git rev-parse HEAD`を実行して得ます（その版が正しいかどうかの判断は、この接続の範囲外です）。Go versionの語は`go version`の出力の3つ目の語です。

環境変数`TAI_TEI_EXPECT_COMMIT`・`TAI_TEI_EXPECT_GO_VERSION`でも指定できます（フラグが優先）。実接続試験（`go test`）は、期待値を環境変数だけから取ります。環境変数名を誤ると、記録のみの実行になります。

```text
TEI_ROOT=<TEIのcloneのパス> TAI_TEI_EXPECT_COMMIT=<40桁> TAI_TEI_EXPECT_GO_VERSION=go1.26.9 \
  go test -run TestTEIWorkspaceValidation -v
```

実行後は、receiptの次を確認してください。

- `pin.checked`が`true`で、`pin.result`が`match`。
- `pin.commit.status`が`match`（指定した期待値のそれぞれの`status`が`match`）。
- `pin.sourceTree.status`が`clean`（`trackedChanges`・`untrackedBuildInputs`・`hiddenFlaggedFiles`が0）。
- `validateJson.status`が`consistent`、`modelBinding.status`が`bound`、`checkout.status`が`unchanged`。

固定に失敗した実行は、TEIをビルドする前に止まるため、`validateJson`・`modelBinding`・`checkout`は`not-run`／`not-checked`のまま、`workspaceTree.digestAfter`は空です。

統合参照実行（`reference-scn001-run`）は、このツールのreceiptを読みません。統合参照実行のrecordへ、このツールの`pin`や`teiCommit`を取り込むかどうかは、消費側（このツールの範囲外）の変更を伴うため、**未決（Owner判断）**です。固定版での実行記録にするには、期待値を指定して実行したこのツール自身のreceipt（`pin.checked=true`、`pin.result=match`）を別に保存する必要があります。

### 固定する版はOwner判断です

TEIの参照接続について、実行したTEIのcommitを記録した保存済みの評価recordはありません（未確認）。`integrations/capability-inventory.md`の表にあるTEIの`490dd20`は、READMEと設計文書を静的に確認した版であり、この接続を実行した版ではありません。固定版の正本を`490dd20`にするか、TEIの現在のmainへ更新するかは**未決（Owner判断）**で、この文書の例は決定ではありません。

次の2点も、Ownerが判断する範囲を広げています。

- `model catalog`の呼出し: 従来の説明は「`validate`だけ」でした。宣言した型がTEIに読み込まれたことは、`model catalog`（TEI自身が`commands`で読み取り専用と宣言）でしか結び付けられません。採用しない場合は`modelBinding`を外し、「型を検証」という表現を弱めます。
- `readOnly`の意味: 従来は常に`true`でした。上のとおり、観測した書込みがあるときだけ`false`にします。

### 測定した値

次は、Linux上のTEIの専用clone（Go 1.26.9、`GOPROXY`・`GOTOOLCHAIN`は既定の環境）に対して、この接続を実行した結果です。TEIのコードの正しさを示すものではありません。

環境: WSL2（Ubuntu 22.04）、Go 1.26.9 linux/amd64、`GOTOOLCHAIN=local`、モジュールキャッシュは取得済み。TEIの専用cloneを、それぞれ`git checkout --detach`で次の3つのcommitに置いて実行しました。

| TEIのcommit | 実行 | 観測 |
| --- | --- | --- |
| `aec98f37b`（実行時点で共有チェックアウトが指していたブランチ上のcommit。mainではありません） | 期待値なし | `passed=true`、`pin.checked=false`、`validateJson=consistent`、`modelBinding=bound`、`checkout=unchanged` |
| 同上 | `-expect-commit`と`-expect-go-version go1.26.9` | `pin.result=match`、`sourceTree=clean`、`passed=true` |
| 同上 | 別のcommit（`490dd205c`）を期待 | `pin.result=mismatch`、`passed=false`、`toolchain.build=not-run`（TEIをビルドせず約0.3秒で終了） |
| `490dd205c`（文書が静的に確認した版） | commit＋Go versionを指定 | `match`／`consistent`／`bound`／`unchanged`、`passed=true` |
| `57f09a7ec` | commitを指定 | 同上 |
| `aec98f37b`＋追跡ファイルを1行追記 | commitを指定 | `pin.sourceTree.status=tracked-changes`（1件）、`passed=false`、TEI未ビルド |
| 同上 | 期待値なし | `passed=true`。`pin.sourceTree`の`trackedChanges=1`を記録（既定の実行は止まりません） |
| `aec98f37b`＋`cmd/tei`に未追跡の`.go`ファイル | commitを指定 | `pin.sourceTree.status=untracked-build-inputs`（1件）、`passed=false`、TEI未ビルド |
| `aec98f37b`＋未追跡の`.txt`ファイルのみ | commitを指定 | `passed=true`、`untrackedFiles=1`を記録 |
| `aec98f37b`、環境に`GOFLAGS=-tags=server`・`GOTOOLCHAIN=auto` | commitを指定 | `passed=true`。`toolchain.goFlags`に`-tags=server`、`goToolchainEnv`に`auto`を記録し、ビルドは`GOFLAGS=-mod=readonly`・`GOTOOLCHAIN=local`で実行 |

いずれも、実行の前後でTEIのcloneの`.git/index`のsha256と`git status --porcelain`の件数（0）は不変で、一時ディレクトリの残りもありませんでした。receiptの`workspaceTree`は4エントリで、前後のdigestが一致しました。

- 1回の実行は、モジュールキャッシュとビルドキャッシュが温かい状態で約4〜12秒、冷たい`GOCACHE`でのビルドは約25秒でした（12コア、負荷平均5〜6）。別の負荷の高い環境では、冷たい`GOCACHE`で4分以上かかった測定もあります。
- `-buildvcs=false`なしの`go build`は、`git status`などを実行し、更新時刻だけが古いindexの`.git/index`を書き換えました（sha256が変化）。`-buildvcs=false`では書き換えませんでした。
- `GOFLAGS=`（空）を環境変数で与えても、go envファイルの`GOFLAGS`（例: `-tags=fromfile`）は打ち消されません。`GOFLAGS=-mod=readonly`を与えると置き換わります。

これはLinux・Go 1.26.9・上の3つのcommit・正常なworkspaceでの結果だけです。Windowsでの実行、警告を出すworkspace、他のcommitは未確認です。

## 境界

- TEIの呼出しは`tei validate -workspace`（テキストと`-json`）と`tei model catalog -workspace`だけです。ネットワーク接続はこの接続からは行いません。ただし`go build`は、TEIの依存moduleがmodule cacheにない場合、Goの設定に従って取得することがあります。
- `validate -json`は、`schemaVersion`・`ok`・`diagnostics`・`error`だけを返し、型の名前もTEIの版も含みません。診断の件数と`error.code`だけを記録し、メッセージ（ローカルの絶対パスを含み得る）は保存しません。
- `modelBinding`の`worldFingerprint`・`sourceIndexFingerprint`・`modelRevision`は、TEIが返した値の記録です。測定では、TEIの複数のcommitで同じ値でした。workspaceの内容に由来し、TEIの版の証拠にはなりません。
- `model catalog`の宣言との照合は、`semantic/guidance.tei`にあるdata型とattributeの名前・型参照の一致です。意味・Authorityの検証ではありません。
- TEIのプロセスはsandboxされていません。TEIのチェックアウトとworkspaceの外（Goのキャッシュ、一時ファイルなど）への書込みは見ていません。呼出し前後の比較は、`.gitignore`の対象のうちGoのビルド入力以外のファイルを見ません。
- 失敗したreceiptの`reason`には、TEIまたは`go build`が標準エラーに出した文字列（最大2000バイト）が入ることがあり、ローカルの絶対パスを含み得ます。失敗したreceiptはコミットしないでください。
- `passed=true`は、この接続が行う照合を通ったことだけを示します。版を固定しない実行では、TEIの版の照合と、`validate -json`・`model catalog`の結び付けは行っていません。

### 版の一致が示さないこと

`pin.result=match`が示すのは、TEIチェックアウトの`HEAD`、追跡対象ファイルの内容（`assume-unchanged`・`skip-worktree`の印がないもの）、Goのビルド入力に未追跡・無視されたファイルがないこと、`go version`の版の語が期待値と一致したことだけです。次は示しません。

- TEIの実装が正しいこと、配布物と同じであること、TEIの所有者がレビューしたこと。
- `pin.sourceTree.status=clean`は、追跡対象ファイルの内容と、名前で判定したGoのビルド入力だけを指します。それ以外の未追跡ファイル（件数は`untrackedFiles`に記録するだけです）、`.gitignore`の対象、`//go:embed`で取り込まれる任意の名前のファイル、チェックアウトの外のファイルは見ていません。これらがビルドや実行時に使われても検出できません。
- `GOFLAGS`以外のビルド環境（`GOEXPERIMENT`・`CGO_ENABLED`・`GOOS`・`GOARCH`・`CC`・`CGO_*FLAGS`など）。固定した実行でも制約せず、`toolchain`にも記録していません。
- 依存moduleの内容がTEIの`go.sum`どおりであること（`go build`の検証に委ねています）。Goのminor・patchより細かい差。
- 確認からビルドまでの間にチェックアウトが書き換えられないこと。`checkout`の前後比較は、実行の前後で変わったかを見るだけです。
- 固定版での実行記録が保存されていること。この確認は、期待値を指定して実行したときだけ得られます。

実運用の認可・監査は未確認です。
