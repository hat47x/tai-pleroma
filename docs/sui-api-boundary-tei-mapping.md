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
## 利用面の決定（2026-11-02、暫定）

`documentv1-projection`は、当面APIの読み取り専用消費に限定します。フロントエンドのconsumerは作りません。

- 理由: 既存のフロントエンドはepistemic系のスキーマだけを扱っており、DocumentV1の投影を表示する画面は再構築の対象そのもの。
- 読み取り経路は、tenant面と管理面の既存の認可・fail-closed規則に従う。
- 見直し: SUI再構築でDocumentV1の表示・編集が必要になったとき。
## consumerの実装状況（2026-11-02）

SUI側へ読み取り専用のconsumerを追加しました（[sui-sensemaking #3365](https://github.com/hat47x/sui-sensemaking/pull/3365)、`a1128a1`）。

- `sui_sensemaking_api.documentv1_projection.from_artifact`が、envelopeと参照整合性を検証して型付きrecordを返す
- 6件のunittestがPASS
- DocumentV1の保存・API・UIには接続していない

TAI側の記録: [receipt](../evaluations/records/SUI-TEI-consumer-2026-11-02.json)
### DocumentV1型への組み立て（2026-11-02）

`to_documentv1_payload`を追加しました（[sui-sensemaking #3366](https://github.com/hat47x/sui-sensemaking/pull/3366)、`ba660d7`）。

- 投影から`DocumentV1`相当のmappingを組み立てる
- `transform`・`createdAt`・`updatedAt`は投影に含まれないため、呼び出し側が渡す
- 保存・Pydantic検証・API呼び出しは行わない
- unittest 9件がPASS

TAI側の記録: [receipt](../evaluations/records/SUI-TEI-adapter-2026-11-02.json)
### HTTP経路の確認（2026-11-02）

管理経路`/admin/tei-epistemic/artifacts/documentv1-projection`をFastAPIのTestClientで確認しました（[sui-sensemaking #3367](https://github.com/hat47x/sui-sensemaking/pull/3367)、`42ec002`）。

- 200でartifactをverbatim返す（`Cache-Control: no-store`）
- 未知kindは404 `unknown_tei_artifact`
- control-plane認可はdependency overrideで外しており、認可そのものは未検証
- 実サーバ・実配備・tenant面のHTTP経路は未検証

TAI側の記録: [receipt](../evaluations/records/SUI-TEI-http-route-2026-11-02.json)
#### 実認可の確認（2026-11-02）

`SUI_ADMIN_API_KEY`を設定した状態で、管理経路をTestClientで確認しました（[sui-sensemaking #3372](https://github.com/hat47x/sui-sensemaking/pull/3372)、`b56d78f`）。

- 正しい`X-Admin-Api-Key`で200、artifactをverbatim返す
- 無認証は401
- DB依存はoverrideで外しており、実DB・実サーバは未検証

TAI側の記録: [receipt](../evaluations/records/SUI-TEI-auth-2026-11-02.json)
### tenant面のHTTP確認（2026-11-03）

tenant面の`/docs/{doc_id}/epistemic/projection`をTestClientで確認しました（[sui-sensemaking #3375](https://github.com/hat47x/sui-sensemaking/pull/3375)、`bee69d0`）。

- binding経由で200、artifactをverbatim返す
- agent credentialは403 `agent_route_not_enabled`
- bindingなしは503 `tei_reference_unavailable`
- 認可関数はテスト用に差し替えており、実セッション・実DBは未検証

TAI側の記録: [receipt](../evaluations/records/SUI-TEI-tenant-route-2026-11-03.json)
### 保存計画（2026-11-03）

`plan_save`を追加しました（[sui-sensemaking #3376](https://github.com/hat47x/sui-sensemaking/pull/3376)、`47c6479`）。

- 投影と既存DocumentV1を比較し、追加・削除・変更を返す
- 投影が持たない既存フィールド（`critiqueInputs`、`transform`、`narratives`など）は失われるため警告する
- 書き込みは行わない
- unittest 4件がPASS

TAI側の記録: [receipt](../evaluations/records/SUI-TEI-save-plan-2026-11-03.json)
### 非破壊マージ（2026-11-03）

`merge_preserving_existing`を追加しました（[sui-sensemaking #3377](https://github.com/hat47x/sui-sensemaking/pull/3377)、`de50696`）。

- 投影が持たないdocument/card/islandのフィールドを保持
- 投影にない既存Card/Islandも保持
- `createdAt`は既存値を維持
- 書き込みは行わない
- unittest 5件がPASS

TAI側の記録: [receipt](../evaluations/records/SUI-TEI-save-merge-2026-11-03.json)
### 保存計画への非破壊マージ統合（2026-11-03）

`plan_save`へ`preserve_existing`を追加しました（[sui-sensemaking #3378](https://github.com/hat47x/sui-sensemaking/pull/3378)、`56133c7`）。

- 既存Card/Islandと投影外フィールドを保持した計画を作る
- 保持時は削除警告を出さず、`preserved_cards`/`preserved_islands`で示す
- 書き込みは行わない
- unittest 6件がPASS

TAI側の記録: [receipt](../evaluations/records/SUI-TEI-save-plan-merge-2026-11-03.json)
### 保存契約（A1）の通過確認（2026-11-03）

保存planのpayloadを、保存経路と同じ`_validate_document_payload_with_a1_contract`で検証しました。

- payloadに`schemaVersion`は不要（[sui-sensemaking #3380](https://github.com/hat47x/sui-sensemaking/pull/3380)で追加を取り消し）
- 非破壊マージ後のpayloadが契約を通る（`contractValid: true`）`n- 当初の422は、既存文書の`critiqueInputs`が不正だったことが原因`n- 対策として、マージ前に既存文書を`DocumentV1`で検証する（[sui-sensemaking #3381](https://github.com/hat47x/sui-sensemaking/pull/3381)、`fb22b65`）
- 保存・API呼び出しは未実施

TAI側の記録: [receipt](../evaluations/records/SUI-TEI-save-contract-2026-11-03.json)
### 保存の実行（2026-11-03）

`save_to_sui.py`で、投影から作成・読み戻し・非破壊マージによる更新までを通しました。

- `PUT /docs/doc-1` 作成: 200
- `GET` 読み戻し: 200
- 既存検証 + マージ + `PUT`: 200
- 最終`GET`: 200
- 一時SQLite、`local-dev`、APIキーなし

本番DB・認証・実配備は未検証です。

TAI側の記録: [receipt](../evaluations/records/SUI-TEI-save-e2e-2026-11-03.json)
### 認証ありの保存（2026-11-03）

業務APIキーを設定した状態で、同じ保存経路を確認しました。

- APIキーなし: 401
- `X-API-Key`あり: 作成・読み戻し・更新・最終GETがすべて200
- 一時SQLite、`local-dev`

本番認証・本番DB・実配備は未検証です。

TAI側の記録: [receipt](../evaluations/records/SUI-TEI-save-auth-2026-11-03.json)