# TAI → EKI Control API probe

EKI Control APIの`GET /v1/tasks`に対する認証結果だけを確認する参照です。

`GET /v1/tasks`は未対応メソッドなので、有効なClient credentialでは認証後に405、無効なcredentialでは401を返します。Taskの送信・委任・Worker・結果検証は行いません。

## 実行

```text
python -m unittest -v probe_test.py
python probe.py --base-url http://127.0.0.1:18080 --token "$EKI_TOKEN" \
  --out ../../evaluations/records/EKI-api-2026-10-26.json
```

`EKI_TOKEN`でもtokenを指定できます。

## 確認すること

- 有効なtokenで`GET /v1/tasks`が405を返す（認証通過）。
- 無効なtokenでは401。
- `readOnly=true`、`authenticated=true`、`taskDelegated=false`、`authorityVerified=false`。
- 追加フィールド`controlBinary`と`pin`（既定は`binding=not-provided`、`pin.checked=false`）。schema文字列と既存フィールドは変えない。

## 合成Taskの送信

`submit.py`は`fixtures/task-request.json`を`POST /v1/tasks`へ送り、`queued`状態を読みます。Workerを起動しないため、Taskは実行されません。

```text
python -m unittest -v submit_test.py
python submit.py --base-url http://127.0.0.1:18081 --token "$EKI_TOKEN" \
  --fixture fixtures/task-request.json --idempotency-key tai-scn001-0001 \
  --out ../../evaluations/records/EKI-task-2026-10-26.json
```

`taskExecuted=false`、`workerResult=false`、`authorityVerified=false`です。

同じIdempotency-Keyで2回送信し、同じ`task_id`が返ることを確認して`idempotent=true`を記録します。

## 合成Taskの取り消し

`cancel.py`はTaskを送信し、`POST /v1/tasks/{id}/cancel`の後、`cancelled`と`CANCELLED`を読みます。

```text
python -m unittest -v cancel_test.py
python cancel.py --base-url http://127.0.0.1:18082 --token "$EKI_TOKEN" \
  --fixture fixtures/task-request.json --idempotency-key tai-scn001-cancel-0001 \
  --out ../../evaluations/records/EKI-cancel-2026-10-26.json
```

`cancelled=true`、`taskExecuted=false`、`workerResult=false`です。

cancel後、`GET /v1/tasks/{id}/result`は**501 NOT_IMPLEMENTED**を返すことを確認し、`resultAvailable=false`を記録します。結果APIが未実装の段階で、結果を捏造しないための境界です。

## Control Planeの起動（推奨手順）

このツールはControl Planeを起動しません。`--base-url`へHTTPで話すだけです。起動と後始末は別の手順で、衝突しにくい次の形を勧めます。

1. 一時dirを`mktemp -d`で作る。configとDBはその中に置く。
2. configは`listen`を`127.0.0.1:0`、`database`を一時dir内にする。tokenは乱数を生成し、sha256だけをconfigへ書く。tokenは環境変数`EKI_TOKEN`で渡し、コマンドラインに出さない。
3. 起動ログの`control plane listening addr=…`から実ポートを読み、`--base-url`へ渡す。既定の18080/18081/18082は他のセッションと衝突し得る。
4. 停止は`SIGTERM`。その後、一時dirを丸ごと削除する。`SIGKILL`ではDBの`-wal`/`-shm`が残る（測定）。
5. バイナリはEKIのcheckoutの中ではなく外へビルドする（`reference-eki-cli`の`-build-out`）。

起動を自動化するかは未決です（Owner判断）。

## どのバイナリが応答したかを固定する（任意）

`--control-binary`、`--control-pid`、`--expect-control-sha256`（環境変数`TAI_EKI_EXPECT_CONTROL_SHA256`、`sha256:<64桁hex>`）を`probe.py` `submit.py` `cancel.py`が受け付けます。形式が不正なら終了コード2で、receiptは出しません。

```text
python probe.py --base-url http://127.0.0.1:<port> --token "$EKI_TOKEN" \
  --control-pid <pid> --expect-control-sha256 sha256:<hex>
```

- 期待値を渡さない実行は記録だけです。`controlBinary.binding`は`not-provided`、`process`（`--control-pid`あり）、`file`（`--control-binary`のみ）、`unavailable`（読めない）のいずれかで、失敗にはしません。`file`は**操作者の申告**で、応答したサーバプロセスの束縛ではありません。
- 期待値を渡す固定実行は、`--control-pid`が必須です。リクエストを1件も送る前に、(1) `/proc/<pid>/exe`のsha256が期待と一致し、(2) そのPIDが`--base-url`のポートをLISTENしている（`/proc/net/tcp`のinodeと`/proc/<pid>/fd`の突き合わせ）ことを確認します。外れれば何も送らず`passed=false`です。全リクエストの後にもう一度実行ファイルのsha256を見て、変わっていれば`passed=false`にします。`--control-binary`も渡したときは、そのファイルのsha256も一致が必要です。
- Linux（WSL含む）だけで動きます。`/proc`がない環境、他ユーザー・他名前空間のPID（`fd`が読めない）、IPv6だけのLISTEN、ループバック以外の`--base-url`は`unavailable`か不一致になり、固定実行は**閉じる側**（失敗）に倒れます。
- receiptの追加フィールド: `controlBinary`（`binding` `sha256` `processSha256` `listenerBound` `source`）と`pin`（`checked` `result` `controlBinary.status/expected/actual`）。パス、PID、token、OSのエラー文は入れません。

### commitとの関係と限界

EKIの`--version`は`dev`だけでcommitを出さないため、commitとの結びつきは次の鎖で間接的に得ます。

1. `reference-eki-cli`の固定実行で、期待commit・追跡内容・Go toolchainを確認し、`-build-out`へバイナリを作る（receiptにsha256）。
2. そのバイナリを起動し、PIDを`--control-pid`へ、sha256を`--expect-control-sha256`へ渡す。

この鎖が成り立つのは、**同一ホストで同じファイルを起動した場合**だけです。別ホスト・別Goで同じsha256になるかは未確認です。

- 一致が示すのは、応答したプロセスの実行ファイルが期待のsha256だったことだけです。EKIの正しさ、Taskの処理、結果、Authorityは示しません。同じ実行ファイルが他のポートもLISTENし得るので、そのプロセスが特定のTaskを処理したことも示しません。
- 実行前後の2回の確認の間に、別のバイナリへ`exec`で差し替わってすぐ戻る競合は防げません（TOCTOUは緩和のみ）。PIDの再利用も完全には閉じません。
- インタープリタ経由（シェルのラッパー、`go run`の一時バイナリ、`docker exec`）で起動したプロセスの`exe`は、ラッパー側のsha256になり、`-build-out`のバイナリとは一致しません。不一致として止まるだけで、通ることはありません。
- 保存済みのapi/task/cancelのrecordにはEKIのcommitもバイナリ情報もないため、どの版で得たかは**未確認**です。再生成はしません。
- 実Control Planeを起動する試験は作りません（EKIのバイナリ、Go 1.27以上、ネットワークが要る）。CIではfake HTTPと、Linuxでは実の子プロセスだけで走ります。

## 境界

- Taskの送信は合成的な1件だけで、実行・結果・委任の完了は未検証です。
- EKIの実運用Control Planeではありません。検証用の一時config/DBで起動したM0 Control Planeです。
- このツール自体はControl Planeを起動しません（`--base-url`へ送るだけ）。起動は別の手順です。`tools/reference-eki-worker`は固定ポート・`/tmp`固定のDB・EKIのcheckout内へのビルドを使うので、上の推奨手順とは異なります（そのdirはこの変更の対象外で、Owner判断として別に扱います）。
- 405は認証通過の観測であり、Task機能の実装・受入を証明しません。
