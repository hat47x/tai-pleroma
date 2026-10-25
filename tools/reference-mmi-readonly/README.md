# TAI → MMI read-only MCP reference

TAIのSCN-001から、SHO前身MMI（Markdown Matrix Injector）の読み取り専用MCP `inspect`を呼ぶ参照接続です。

**実製品接続の最初の1件**として、次だけを確認します。

- MMI MCPの`initialize`と`notifications/initialized`。
- `inspect`でCSVの候補を取得する。
- `select`でO-02/O-03/O-07の行を取得し、O-02とO-03の文言が異なるまま保持される。
- ワークスペース外の`../outside.csv`を拒否する。
- 呼出し前後で原本とguideのSHA-256が変わらない。

意味の受理、公開権限、実運用の認可、MMIの書込み操作は扱いません。

## 実行

MMIの開発チェックアウト（`03_Implement/node_modules`を含む）が必要です。

```text
go test ./...
go run . -workspace testdata/workspace
```

MMIの場所は`-mmi-root`または`MMI_ROOT`で指定できます。省略時は`../../../markdown-matrix-injector`を使います。

## 境界

- MCPはstdioだけを使い、ネットワークへ接続しません。
- 呼ぶツールは`inspect`と`select`だけです。
- `candidateCount`はinspect結果に`candidates`が含まれることの確認であり、表の意味や内容の正しさではありません。
- `selectedRows`と`conflictPreserved`は、MMIがO-02/O-03/O-07の3行を返し、O-02とO-03の文言差を保持したことだけを示します。
- `realProductConnected=true`は、この環境でMMI MCPとの読み取り往復が成立したことだけを示します。
- 実運用の権限、監査、複数利用者、MMIの版固定、書込み・保存は未検証です。
