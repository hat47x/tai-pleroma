# TAI → SUI API read-only probe

SUI APIの`/healthz`、`/openapi.json`、`/docs`のメタデータ一覧、任意の`/docs/{doc_id}`を読む参照です。

**SUIのテナント・認可・SCN-001データは検証しません。** 検証では一時DBに空のDocumentV1をPUTしてからGETしています。

Document本文の読み取りは、明示的に`--doc-id`を指定した場合だけ行います。

## 実行

SUI APIが起動している環境で実行します。このリポジトリの検証では、WSL Ubuntu-22.04上でSUIバックエンドを起動し、`127.0.0.1:8765`へ接続しました。

```text
python -m unittest -v probe_test.py
python probe.py --base-url http://127.0.0.1:8765 --out ../../evaluations/records/SUI-api-2026-10-26.json
python probe.py --base-url http://127.0.0.1:8765 --doc-id scn001-demo --timeout 30 --out ../../evaluations/records/SUI-api-2026-10-26.json
```

`--doc-id`指定時は`/docs/{doc_id}`を読み、`documentTitle`、`documentCardCount`、`documentDigest`、各cardの`id`・`claimType`・`textDigest`、`documentIslandCount`、`documentEdgeCount`をreceiptへ追加します。生のcard本文は記録しません。

検証時の入力fixtureは[fixtures/scn001-document.json](fixtures/scn001-document.json)で、O-02/O-03/O-06/O-07の4 cardと、予約不要/必要の2 island、`contradicts` edgeを持ちます。検証では一時DBへPUTしてからGETしました。

## 確認すること

- `/healthz`が`{"status":"ok"}`を返す。
- `/openapi.json`が`paths`を持つ。
- `/docs`がDocumentメタデータの配列を返す。
- `openapi` version、`pathCount`、`documentCount`、`documentIds`をreceiptへ記録。
- `readOnly=true`、`realProductConnected=true`、`passed=true`。

## 境界

- SUI Document本文の作成・更新はprobeでは行わない。検証用の一時DBへ空のDocumentV1を別途PUTした。
- `--doc-id`の本文読み取りは、合成fixtureの4 cardだけを対象にした。実在のSCN-001資料・実カードは未接続。
- テナント、認可、監査、本人確認は未検証。
- SCN-001の観測・仮説・DraftとSUIの意味形成は接続していない。
- `realProductConnected=true`はAPIプロセスの到達性だけを示す。
