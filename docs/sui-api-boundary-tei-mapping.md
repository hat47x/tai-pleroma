# SUIのAPI境界とTEI投影の接続案

SUIのDocument APIとTEIの投影・合成をどこで接続するかを整理します。ここに書くのは設計案であり、SUI側の変更ではありません。

## 参照した版

- SUI: `0a19ec56`
- `03_Implement/backend/src/sui_sensemaking_api/routes/docs.py`（`GET/PUT /docs/{doc_id}`、`DocumentPayload = DocumentV1`）
- `03_Implement/backend/src/sui_sensemaking_api/routes/tei_epistemic.py`（`GET /docs/{doc_id}/epistemic/projection`）
- `03_Implement/backend/src/sui_sensemaking_api/tei_reference_transport.py`（binding registry、artifact kind、tenant別ディレクトリ）

## 既にある接続面

SUIは、TEI Referenceの成果物を読む専用の面をすでに持っています。

```text
GET /docs/{doc_id}/epistemic/projection
  -> 200 {"ok": true, "artifact": <JSON object>}
  -> 404/503 は fail-closed（内容を返さない）
```

- 対象はテナントとdocumentの組で、`tenants/<tenantId>/<docId>/<kind>.json`から読む
- どの成果物を読むかは`epistemic-bindings.json`の運用者バインディングで決まる
- artifact kindは`epistemic-assessment`・`epistemic-context`・`epistemic-detail`の3つ
- 読み取り専用で、DocumentV1や確認状態への書き込みはしない
- agent credentialでは403

## パイロットの成果物との差

パイロットが作るのは、Document/Card/Island/Edge/Affiliationのflat recordと、その合成結果です。上の3つのartifact kindとは意味が違います。

## 接続の候補

### 案A: 読み取り専用のartifactとして足す

- `documentv1-projection`のようなartifact kindを追加し、合成結果を`tenants/<tenantId>/<docId>/`へ置く
- `epistemic-bindings.json`でバインディングを記録
- SUI側の変更はartifact kindの許可リスト追加と、必要ならレスポンスの型付けだけ
- 書き込み権限を持たないので、既存のfail-closed経路を再利用できる

### 案B: DocumentV1の書き込み経路へ入れる

- 合成結果を`PUT /docs/{doc_id}`の`DocumentV1`へ変換して保存する
- 座標、時刻、`transform`、レビュー状態など、現在のパイロットが持たないフィールドが必要
- 認証・改訂・監査の権限を持つため、影響が大きい

## 暫定意思決定（AI）

- 最初の接続は案Aにする。読み取り専用で、既存のテナント分離とfail-closedの規則をそのまま使える。
- 案Bは、座標・レビュー状態・`transform`を含む完全なDocumentV1の写像ができてから扱う。
- artifactのpayloadには、どの契約と版から作ったかを示す`contract`と`schema`を含める。
- SUI側の変更（artifact kindの追加）は、この設計を前提に別の変更として行う。

## 未確認

- 認証・テナント解決・監査の実装詳細は、この整理では追っていない。
- フロントエンドの`epistemic_projection_adapter`が新しいartifact kindを受け取れるかは未確認。
- `GET /docs/{doc_id}`と`PUT /docs/{doc_id}`の改訂・競合の扱いは未確認。
- 案Aに必要なSUI側の変更量は未見積もり。

## 実装状況（2026-11-02）

SUIの許可リストへ`documentv1-projection`を追加しました（[sui-sensemaking #3364](https://github.com/hat47x/sui-sensemaking/pull/3364)、`963adb0`）。TAIのartifactを`tenants/<tenantId>/<docId>/documentv1-projection.json`へ置き、SUIのtransport moduleでpayloadが一致して読めること、別tenantでは
ot-a-file`になることを確認しました（[receipt](../evaluations/records/SUI-TEI-sui-reader-2026-11-02.json)）。HTTPサーバ・認証・配備は未検証です。

なお、2026-11-02に`install_artifact.py`と`verify_sui_reader.py`で、バインディングの解決とtenant分離を確認しました（[receipt](../evaluations/records/SUI-TEI-binding-2026-11-02.json)）。
管理経路（`/admin/tei-epistemic/artifacts/{artifact_kind}`）でも同じkindを読めることを確認しました（[receipt](../evaluations/records/SUI-TEI-admin-path-2026-11-02.json)）。