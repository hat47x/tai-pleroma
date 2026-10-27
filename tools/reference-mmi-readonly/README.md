# TAI → MMI read-only MCP reference

TAIのSCN-001から、SHO前身MMI（Markdown Matrix Injector）の読み取り専用MCP `inspect`と`select`を呼ぶ参照接続です。

**実製品接続の最初の1件**として、次を確認します。

- MMI MCPの`initialize`と`notifications/initialized`。
- `tools/list`を取得し、書込み可能と思われる名前（`commit`・`write`・`import`などの語を含む名前）の有無を記録する。MMIはMCPのannotationsを返さないため、判定はツール名によります。
- `inspect`でCSVの候補を取得し、`candidates[].locator.sourceDigest`が、TAIが呼出し前に計算したCSVのSHA-256と一致する。`candidateCount`は、返されたJSONの`candidates`配列の長さです。
- `select`でO-02/O-03/O-07の行を取得し、O-02とO-03の文言が異なるまま保持される。`rows`の`shown`と`ofTotal`が等しく、`exact`が`true`で、プレビューの行数とも一致する。
- `select`の表fingerprintが、`inspect`の同じ表の候補fingerprintと一致する。
- ワークスペース外の`../outside.csv`と存在しない`missing.csv`を拒否し、拒否理由の種別（`outside-workspace`／`not-found`）を区別する。
- 呼出し前後で、ワークスペース全体（ファイルの内容・相対パス・空ディレクトリ・symlinkの指す先）のdigestと、原本・guideのSHA-256が変わらない。
- receiptにMMIのcommit、`package-lock.json`のdigest、Nodeのversionを記録する。期待値を指定したときだけ、これらを照合する。
- `selected`にO-02/O-03/O-07のID・原文・出典・版・availabilityを保存し、SCN-001評価へ渡せる。

意味の受理、公開権限、実運用の認可、MMIの書込み操作は扱いません。

## 実行

MMIの開発チェックアウト（`03_Implement/node_modules`を含む）が必要です。MMIまたは`node`がない環境では、MMIの実接続試験だけがskipされます。偽のMCPサーバーを使う負例は実行され、偽のGit repositoryを使う試験は`git`がなければskipされます。

```text
go test ./...
go run . -workspace testdata/workspace
```

MMIの場所は`-mmi-root`または`MMI_ROOT`で指定できます。省略時は`../../../markdown-matrix-injector`を使います。

偽サーバーの試験は、実測した応答の形に合わせた合成です。通っても、実際のMMIが同じ形で応答することの確認にはなりません。MMIでの確認は、上の実接続試験で行います。

## 版を固定して実行する（任意）

既定では、MMIのcommit・`package-lock.json`のdigest・Nodeのversionを**記録するだけ**です（receiptの`pin.checked=false`）。この実行は、接続したMMIが文書に書かれた版と同じかを示しません。

期待値を指定すると、次を満たさない実行は`passed=false`になり、MMIのコードを起動する前に止まります。

- `-expect-commit`（必須）: MMIチェックアウトの`HEAD`（40桁の16進）。MMIのディレクトリがGit repositoryのルートでない場合は取得できず、失敗します。
- `-expect-lock-digest`: `03_Implement/package-lock.json`の、CRLFをLFに直した後の`sha256:<64桁>`。
- `-expect-node-major`: `node --version`のmajor（10進）。
- 他の期待値だけを指定した場合は、`-expect-commit`がないため失敗します。lockのdigestはMMIの複数のcommitで同じ値になり、Nodeのmajorはチェックアウトの内容を示さないためです。
- 追跡対象ファイルに変更（ステージ済み・未ステージ・削除）があると失敗します。`assume-unchanged`または`skip-worktree`の印が付いた追跡ファイルがある場合も、その編集を見分けられないため失敗します。比較では`refs/replace`（`git replace`）を無視します。MMIの`.git/index`は書き換えず、複製した写しに対してgitを実行します（`git diff`は`--no-optional-locks`を付けても渡されたindexを更新するため）。Nodeのversionは、MMIを起動するのと同じ`03_Implement`ディレクトリで`node --version`を実行して取ります。
- 取得できない値（gitがない、lockがない、`node`がない）を期待した場合も失敗です。
- `tools/list`に書込み可能と思われる名前や、測定していない名前のツールがあると失敗します。
- `sourceDigest`・`select`のfingerprint・`rows`のいずれかが、照合できない（`unavailable`）場合も失敗します。版を固定しない実行では、これらは記録のみです。

```text
go run . -mmi-root <MMIのcloneのパス> -workspace testdata/workspace \
  -expect-commit a8addd1560bd02131b29ade4d9d1cfa7ca5f9b21 \
  -expect-lock-digest sha256:bef54626c357b34267bd6647fc8fbeb86a816aab6fd9d9a42751ec24ebef2875 \
  -expect-node-major <使うNodeのmajor>
```

環境変数`TAI_MMI_EXPECT_COMMIT`・`TAI_MMI_EXPECT_PACKAGE_LOCK_DIGEST`・`TAI_MMI_EXPECT_NODE_MAJOR`でも指定できます（フラグが優先）。`go test`と、この接続を子プロセスとして起動する統合参照実行にも環境変数は引き継がれます。環境変数名を誤ると、記録のみの実行になります。

統合参照実行（`reference-scn001-run`）のrecordは、このツールの`pin`の結果を取り込みません。統合参照実行が子プロセスとして起動するこのツールに環境変数を引き継いでも、期待値を指定して実行したことはrecordに残りません。固定版での実行記録にするには、期待値を指定して実行したこのツール自身のreceipt（`pin.checked=true`、`pin.result=match`）を別に保存する必要があります。統合参照実行のrecordへ`pin`を取り込むかどうかは、消費側（このツールの範囲外）の変更を伴うため、**未決（Owner判断）**です。

実行後は、receiptの次を確認してください。

- `pin.checked`が`true`で、`pin.result`が`match`。
- `pin.commit.status`が`match`（指定した期待値のそれぞれの`status`が`match`）。
- `pin.sourceTree.status`が`clean`。
- `binding.sourceDigest`と`binding.fingerprintCrossCheck`が`match`、`binding.rows.status`が`complete`。

### 固定する版はOwner判断です

上のcommit `a8addd1`は、`integrations/capability-inventory.md`が「確認したmain」に挙げる版です。固定版の正本を`a8addd1`にするか、MMIの現在のmainへ更新するかは**未決（Owner判断）**で、この例は決定ではありません。保存済みの評価record（`evaluations/records/SCN-001-run-2026-10-26.json`）の`mmiCommit`は`1989b827…`で、`a8addd1`ではありません。版を固定せずに生成されたもので、文書の固定版での実行記録ではありません。

### 測定した値

次は、`a8addd1`のMMI（Linux、Node v20.18.0、`npm ci`済み）で、期待値を指定して実行した結果です。

- `pin.result`は`match`、`pin.sourceTree.status`は`clean`。`inspect`の`sourceDigest`と`select`のfingerprintは一致し、境界外は`outside-workspace`、存在しないsourceは`not-found`で拒否された。
- 同じ期待値で`06f5b341`のMMIを使うと、commitが一致せず`passed=false`で止まる（MMIは起動しない）。`package-lock.json`のdigestは`a8addd1`と同じ値だった。lockのdigestだけではこれらのcommitを区別できないため、commitの照合が必要です。
- Node majorは、測定した環境（Linux）では20でした。過去の記録のNodeは22系とされていますが、保存済みのrecordにはNode versionの欄がなく、出典は確認できていません。ここでは再現していません（未確認）。

次は上の実行とは別の観測で、`a8addd1`での実行結果ではありません。

- Windowsで`core.autocrlf=true`のチェックアウト（共有の開発用チェックアウト、`1989b827`の作業ツリー）で`package-lock.json`を読み取りだけで確認すると、receiptの`packageLockDigest`（生のバイト列）は`sha256:f6810ef0…`になります。Linuxやコミット済みのblobは`sha256:bef54626…`です。照合には後者（CRLF→LF）を使います。

## 境界

- MCPはstdioだけを使い、ネットワークへ接続しません。
- 呼ぶツールは`inspect`と`select`だけです。他のツール名の呼出しは、TAI側で送信前に拒否します。
- `tools/list`の確認は名前による判定です。MMIが書込めないことの証明ではなく、MMIのプロセスはsandboxされていません。ワークスペースの外（キャッシュなど）への書込みは見ていません。版を固定しない実行では、書込み可能と思われる名前を記録して注記するだけで、失敗にしません。
- `candidateCount`は返されたJSONの`candidates`配列の長さで、表の意味や内容の正しさではありません。
- `sourceDigest`の一致は、呼出し時点でMMIとTAIが同じバイト列を読んだことを示します。資料の真正性や内容の正しさではありません。CRLFとLFでは別のdigestになります。
- `select`の表fingerprint（`table-display-cells-v1`）は表の表示内容の指紋で、CSVのバイト列のdigestとは比べられません。改行コードが違っても同じ値になります。記録して`inspect`と突き合わせるだけです。
- MMIが返さない値、または形式が異なる値は`unavailable`として記録し、版を固定しない実行では失敗にしません。
- 拒否理由の種別はエラーメッセージの文言で判定します（MMIは機械可読な符号を返しません）。文言が測定済みの版と異なる場合、版を固定しない実行では記録して注記し、固定した実行では失敗にします。メッセージ本文はローカルの絶対パスを含み得るためreceiptに保存しません。ただし、失敗時の`reason`には、子プロセスが標準エラーに出した文字列が入ることがあります。失敗したreceiptはコミットしないでください。
- `selectedRows`と`conflictPreserved`は、MMIがO-02/O-03/O-07の3行を返し、O-02とO-03の文言差を保持したことだけを示します。
- `realProductConnected=true`は、この環境でMMI MCPとの読み取り往復が成立し、このツールが実行する照合（`inspect`の`sourceDigest`・`select`の`rows`・fingerprintのうちMMIが返した値、拒否理由、ワークスペースの不変）を通ったことだけを示します。版を固定しない実行では、MMIの版（commit・lock digest・Node version）の照合と、MMIが返さなかった値の結び付けは行っていません。
- 版を固定しない実行でも、MMIが別のcommitで挙動を変えれば（`sourceDigest`の不一致、`rows`の不整合、ワークスペースの変更など）失敗します。これらはMMIの版の違いではなく、その実行で観測した事実の不一致だからです。

### 版の一致が示さないこと

`pin.result=match`が示すのは、MMIチェックアウトの`HEAD`、追跡対象ファイルの内容（`assume-unchanged`・`skip-worktree`の印がないもの）、`package-lock.json`のdigest、Nodeのmajorが期待値と一致したことだけです。次は示しません。

- MMIの実装が正しいこと、配布物と同じであること、MMIの所有者がレビューしたこと。
- `pin.sourceTree.status=clean`は追跡対象ファイルの内容だけを指します。追跡されていないファイル（件数は`untrackedFiles`に記録するだけです）、`.gitignore`の対象（`node_modules`を含む）、チェックアウトの外のファイルは見ていません。追跡されていないファイルが実行時に読み込まれても検出できません。
- `node_modules`の中身が`package-lock.json`どおりであること。Nodeのminor・patch。
- 確認から起動までの間にチェックアウトが書き換えられないこと。
- 固定版での実行記録が保存されていること。この確認は、期待値を指定して実行したときだけ得られます。

実運用の権限、監査、複数利用者は未検証です。
