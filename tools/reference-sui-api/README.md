# TAI → SUI API read-only probe

SUI APIの`/healthz`と`/openapi.json`だけを読む、到達性確認の参照です。

**SUIのDocument内容・テナント・認可・SCN-001データは検証しません。** SUI APIが起動し、公開契約を返すことだけを確認します。

## 実行

SUI APIが起動している環境で実行します。このリポジトリの検証では、WSL Ubuntu-22.04上でSUIバックエンドを起動し、`127.0.0.1:8765`へ接続しました。

```text
python -m unittest -v probe_test.py
python probe.py --base-url http://127.0.0.1:8765 --out ../../evaluations/records/SUI-api-2026-10-26.json
```

## 確認すること

- `/healthz`が`{"status":"ok"}`を返す。
- `/openapi.json`が`paths`を持つ。
- `openapi` version、`pathCount`、path一覧をreceiptへ記録。
- `readOnly=true`、`realProductConnected=true`、`passed=true`。

## 境界

- SUI Documentの読み取り・作成・更新は行わない。
- テナント、認可、監査、本人確認は未検証。
- SCN-001の観測・仮説・DraftとSUIの意味形成は接続していない。
- `realProductConnected=true`はAPIプロセスの到達性だけを示す。
