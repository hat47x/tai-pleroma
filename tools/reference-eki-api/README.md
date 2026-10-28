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

## 境界

- Taskの送信は合成的な1件だけで、実行・結果・委任の完了は未検証です。
- EKIの実運用Control Planeではありません。検証用の一時config/DBで起動したM0 Control Planeです。
- 405は認証通過の観測であり、Task機能の実装・受入を証明しません。
