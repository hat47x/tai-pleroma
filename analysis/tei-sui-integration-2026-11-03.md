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

receiptは`evaluations/records/`にあり、合成61件・実実行65件がcheckerを通る。

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