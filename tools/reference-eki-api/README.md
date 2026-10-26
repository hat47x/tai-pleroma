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

## 境界

- Taskの送信、委任、Worker、結果検証、Authorityは未検証です。
- EKIの実運用Control Planeではありません。検証用の一時config/DBで起動したM0 Control Planeです。
- 405は認証通過の観測であり、Task機能の実装・受入を証明しません。
