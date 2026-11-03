# TEI投影からSUI DocumentV1への接続 — 到達点と残課題

2026-11-03時点の整理。実装と検証の正本は各リポジトリのGit履歴とreceipt。

## 目的

TEIの投影を、SUIのDocumentV1再構築へ接続する。読み取り専用artifactから始め、保存経路まで段階的に検証する。

## 現在の経路

```text
TEI契約（record投影）
  → 生成・適合選抜（5契約、21ケース）
  → 合成（Card/Island/Edge/Affiliation）
  → artifact（tai.reference.tei-documentv1-projection/v0）
  → SUI consumer（型付きrecord）
  → DocumentV1 payload
  → 保存計画（契約検証・非破壊マージ）
  → uvicorn実サーバ（APIキーあり）
  → 作成・読戻し・往復整合
```

## 検証済み

| 項目 | 状態 | 根拠 |
| --- | --- | --- |
| TEI契約からの生成・選抜 | 21ケースPASS | `SUI-TEI-artifact-2026-11-02.json` |
| artifact構造検証 | PASS | `SUI-TEI-artifact-validation-2026-11-02.json` |
| SUI transport読み取り（tenant/管理） | PASS | `SUI-TEI-sui-reader-2026-11-02.json` |
| 管理経路HTTP（認可override） | 200/404 | `SUI-TEI-http-route-2026-11-02.json` |
| 管理経路HTTP（実認可） | 200/401 | `SUI-TEI-auth-2026-11-02.json` |
| tenant面HTTP（認可差し替え） | 200/403/503 | `SUI-TEI-tenant-route-2026-11-03.json` |
| DocumentV1モデル検証 | PASS | `SUI-TEI-documentv1-validation-2026-11-03.json` |
| 保存計画・非破壊マージ | 6件PASS | `SUI-TEI-save-plan-merge-2026-11-03.json` |
| 既存文書の事前検証 | 7件PASS | SUI #3381 |
| 保存の実行（一時SQLite） | 200/200/200 | `SUI-TEI-save-e2e-2026-11-03.json` |
| 認証ありの保存 | 401/200 | `SUI-TEI-save-auth-2026-11-03.json` |
| 保存後の往復整合 | 6項目一致 | `SUI-TEI-save-roundtrip-2026-11-03.json` |
| uvicorn実サーバ経由 | 200/401 | `SUI-TEI-server-2026-11-03.json` |
| 投影の決定性 | 2回で同一digest | `SUI-TEI-determinism-2026-11-03.json` |
| 複数文書の保存（10件） | 200/全件独立 | `SUI-TEI-multi-doc-2026-11-03.json` |
| ETag前提条件 | 409/200 | `SUI-TEI-etag-2026-11-03.json` |
| 大量カード（300枚、合成） | 200/200 | `SUI-TEI-large-doc-2026-11-03.json` |

receiptは`evaluations/records/`にあり、合成61件・実実行96件がcheckerを通る。

## 未検証

- 本番DB（Postgres）。この環境に`psql`・`docker`・5432の待受がない
- TLS・リバースプロキシ・実配備
- 本番認証構成（現在は`local-dev`と静的APIキー）
- SaaSプロファイル。trusted SaaS runtime policyの設定が不足して起動できない
- 実際の大量カード（300枚は合成fixtureで確認）
- 同時書き込み
- 意味の正しさ、人の受理

## 暫定決定

- 投影はrecord形式（`identity|normalize|record`のうちrecord）
- Affiliationは`Island.cardIds`の包含と重複させない
- Document/Islandの`title`はoptional
- 構造体配列・`transform`・時刻・履歴は投影せず、SUI側を正本とする
- `transform`・時刻は呼び出し側が供給する
- 保存は非破壊マージを既定の選択肢とする
- 利用面はAPIの読み取り専用消費に限定し、フロントエンドconsumerは作らない

## リスク

- 非破壊マージは既存文書の不正フィールドを保持する。マージ前の検証が必要（実装済み、呼び出し側の適用が前提）
- `transform`・時刻の供給元が未確定
- 本番DB・配備の挙動は未確認
- 保存は作成・更新のみで、削除や競合解決は未検証

## 次の候補

1. Postgres環境を用意して保存を確認する
2. TLS・リバースプロキシを含む配備構成を確認する
3. 複数文書・大規模文書で保存と往復整合を確認する
4. 保存計画を運用ツールとして定着させる

公開gateは`blocked`のまま。外部作用・公開は未承認。

## 付録: DocumentV1とTEI primitiveの対応

| 要素 | フィールド | TEI primitive | 契約フィールド |
| --- | --- | --- | --- |
| Document | `id` | `std.identifier` | `sui.document.document_id` |
| Document | `title`（optional） | `std.text` | `sui.document.title` |
| Card | `id` | `std.identifier` | `sui.card.card_id` |
| Card | `text` | `std.text` | `sui.card.text` |
| Card | `x`,`y` | `std.decimal` | `sui.card.x` / `sui.card.y` |
| Card | `claimType`（optional） | `std.text` | `sui.card.claim_type` |
| Card | `holdState`（optional） | `std.text` | `sui.card.hold_state` |
| Card | `textReviewed`（optional） | `std.boolean` | `sui.card.text_reviewed` |
| Island | `id` | `std.identifier` | `sui.island.island_id` |
| Island | `title`（optional） | `std.text` | `sui.island.title` |
| Island | `cardIds`（配列） | `std.identifier` × many | `sui.island.card_ids` |
| Edge | `id` | `std.identifier` | `sui.edge.edge_id` |
| Edge | `fromId`,`toId` | `std.identifier` | `sui.edge.from_id` / `to_id` |
| Edge | `type` | `std.text` | `sui.edge.relation` |
| Edge | `fromKind`,`toKind` | `std.text` | `sui.edge.from_kind` / `to_kind` |
| Affiliation | `id` | `std.identifier` | `sui.affiliation.affiliation_id` |
| Affiliation | `cardId`,`islandId` | `std.identifier` | `sui.affiliation.card_id` / `island_id` |

投影しないもの: `critique`・`critiqueTags`・`meta`・`ka`・`geometry`・`summaryText`・`transform`・`createdAt`/`updatedAt`・`critiqueInputs`などの構造体配列。
## 構造体配列の扱い（暫定決定）

`narratives`・`evidenceLinks`・`critiqueInputs`・`relationSummaries`のような構造体配列は、投影しないままにする。

検討した選択肢:

| 案 | 内容 | 判断 |
| --- | --- | --- |
| A | 投影しない。既存値を保存時にマージで保持する | 採用 |
| B | 要素ごとに別契約・別artifactを作る | 保留 |
| C | JSON文字列として1フィールドへ通す | 不採用 |

理由:

- 現在の投影は平坦なrecordで、要素の意味と必須項目が固まっていない
- 保存は非破壊マージなので、投影しない値は保持される
- Cは契約上は通るが、型の検証を失い、TEIのprimitiveの意味から外れる

見直し条件:

- SUIが投影だけからこれらの要素を復元する必要が出たとき
- 要素の契約（必須項目・参照関係）が確定したとき
## Postgresでの保存試行（2026-11-03）

埋め込みPostgreSQL 16.2（`pgserver`）を起動し、SUIを`local-dev`で接続するところまでは到達した。テーブルは`Base.metadata.create_all`で作成した。

- 結果: `PUT /docs/doc-1`が**409 "Document changed concurrently"**
- 読み戻しは404、`documents`と`canvas_revisions`は0行
- 例外はルート側で409へ変換されるため、DB側の原因は未特定
- 仮説: Alembicのmigrationで作られる制約・トリガーが不足している

SQLiteの一時DBでは同じ手順が200で通る。Postgres経路は未検証のまま。[attempt](../evaluations/postgres-attempt-2026-11-03.json)
### 追記（解決）

409の原因は、`local-default`テナント行が`tenants`になく、`documents`の外部キー制約に違反していたことだった（`ForeignKeyViolation`）。`Base.metadata.create_all`だけではテナントが投入されない。

テナント行を投入して再実行したところ、保存は成功した。

```text
createStatus: 200
readStatus: 200
documentRows: 1
revisionRows: 1
roundTrip: true
```

[save receipt](../evaluations/records/SUI-TEI-postgres-2026-11-03.json)
### 追記（migration経路）

`alembic upgrade head`でスキーマを作る経路でも保存を確認した。

```text
migration: alembic upgrade head
createStatus: 200
readStatus: 200
documentRows: 1
revisionRows: 1
roundTrip: true
```

テナント行の投入は migration 後も必要だった（migrationはテナントを投入しない）。[receipt](../evaluations/records/SUI-TEI-postgres-migrate-2026-11-03.json)
## SaaSプロファイルの前提（2026-11-03再確認）

埋め込みPostgresをAlembicで初期化したうえで`SUI_RUNTIME_PROFILE=saas-multitenant`を起動すると、`trusted SaaS runtime policy is incomplete`で停止する。現在の不足項目は6つ。

1. external access control
2. deny fail-safe mode
3. external document policy binding
4. external tenant capability resolution
5. SaaS OAuth broker authorize endpoint configured
6. SaaS auth-session hash key configured

APIキーと管理者キーを設定しても、この6項目は自動では満たされない。[probe](../evaluations/saas-startup-probe-2026-11-03.json)
## TEI本体の更新に対する再確認（2026-11-03）

検証時のTEIは`2e16b2af9`だった。その後TEIの`main`は`e0e813915`まで進んでいる。同じSUIパイロットを新しいTEIで実行し、21ケース・スキーマ・DocumentV1・契約digestがすべて通ることを確認した。[receipt](../evaluations/records/SUI-TEI-compat-2026-11-03.json)
## 競合時の503（2026-11-03）

Postgresで条件付きPUTを競争させると、通常は1勝2敗（200と409）に収束する。しかし再実行の一部で、409ではなく**503**が1件返る場合があった（4回中1回、5ラウンド中1ラウンド）。

- 200は各ラウンド1件のまま
- 503は書き込み競合として409へ変換されない経路があると推測
- 発生は断続的で、頻度は未測定
- クライアント側の再試行余地がある

[receipt](../evaluations/records/SUI-TEI-postgres-contention-2026-11-03.json)