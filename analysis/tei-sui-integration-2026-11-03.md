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

receiptは`evaluations/records/`にあり、合成61件・実実行100件がcheckerを通る。

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

検証時のTEIは`2e16b2af9`だった。その後TEIの`main`は`e0e813915`、`25a15110d`と進んでいる。最新でも同じパイロットが通ることを確認した。同じSUIパイロットを新しいTEIで実行し、21ケース・スキーマ・DocumentV1・契約digestがすべて通ることを確認した。[receipt](../evaluations/records/SUI-TEI-compat-2026-11-03.json)
## 競合時の503（2026-11-03）

Postgresで条件付きPUTを競争させると、通常は1勝2敗（200と409）に収束する。しかし再実行の一部で、409ではなく**503**が1件返る場合があった（4回中1回、5ラウンド中1ラウンド）。

- 200は各ラウンド1件のまま
- SUIは`DocumentRevisionDivergence`などを503へ変換する（fail-closed）。競合時にこの経路に入ると推測
- 発生は断続的で、頻度は未測定
- クライアント側の再試行余地がある

[receipt](../evaluations/records/SUI-TEI-postgres-contention-2026-11-03.json)
### 503を受けた再試行（2026-11-03）

503を受けた側が、現在のETagを取り直して再試行する実装を試した。

- 再試行1回で200/409のどちらかに収束した
- ただし、再試行が新しいETagで成功すると、同じラウンドに200が2件並ぶことがある（別バージョンへの条件付き更新になるため）
- したがって「1ラウンド1勝」は再試行なしの場合の性質で、再試行を含む場合は「最終的に200か409」を条件にする

[receipt](../evaluations/records/SUI-TEI-postgres-retry-evidence-2026-11-03.json)
## EKIの実行系は未配線（2026-11-03）

EKIへ投影TaskRequestを投入すると202で`queued`になるが、実行までは進まない。EKI自身の`docs/development.md`が、Placement・Lease・WorkOrderの発行が`eki-control`の起動経路に配線されていないこと、ResultClaimが受理結果へ繋がっていないことを記している（#242）。

- こちらで観測したのは`queued`まで
- Dispatch設定（署名鍵・trust domain・各種principal・ExecutorApproval）を用意すれば配置まで進む可能性はあるが、実行結果の受理は未配線
- したがって「Workerを繋いだ実行」は、現時点のEKIでは確かめられない
### Dispatchを有効にした場合（2026-11-03）

署名鍵（Ed25519、EdDSA）とDispatch設定を用意して`eki-control`を起動すると、配置ループ自体は動く。しかし投入したTaskは`queued`のまま進まず、ログには次が出る。

```text
dispatch tick considered=0 dispatched=0 deferred=1 reasons="...: policy is not available"
```

EKIの`internal/control/dispatch/dispatch.go`では、`admitted`のTaskを`ready`へ昇格させる前に`Policies.LoadCurrentPolicy`を要求し、取得できない場合は「policy is not available」で据え置く。今回の構成にはpolicy storeが無いため、ここで止まる。

- 署名鍵の`algorithm`は`EdDSA`（`Ed25519`は拒否される）
- policy storeの用意が、実行へ進むための次の前提
### policyを投入した後（2026-11-03）

`policy_history`（epoch 1、active）と`policy_current`へ行を入れて再起動すると、配置ループは止まらず、Taskを検討対象にする。

```text
dispatch tick considered=2 dispatched=0 deferred=2
reasons="...: no usable worker is registered"
```

つまり次の不足は**Workerの登録**である。Taskは依然`queued`で、実行はされない。

- policyはstate storeの行として投入できた
- 配置はWorker registryを見る段で止まる
- 次に必要なのはWorker plane（登録・セッション）の用意

[attempt](../evaluations/eki-dispatch-attempt-2026-11-03.json)・[log](../evaluations/eki-dispatch-attempt-2026-11-03.log)
### Workerを登録するとrunningへ進む（2026-11-03）

`workers`と`enrollment_credentials`へ行を入れ（Workerプロセスは起動せず）、policy投入済みの状態で再起動すると、配置ループはTaskを1件dispatchした。

```text
dispatch tick considered=2 dispatched=1 deferred=1
reasons="...: reserve lease: NOT_YET_VALID: approval is issued in the future"
```

タスクの公開状態は`queued`から**`running`**へ変わった。ただしWorkerは動いていないため、実行結果は無く、`taskExecuted=false`である。

- 投影したTaskRequestが、EKIの配置・lease予約の段まで進むことを確認
- 残るのはWorkerプロセスの実行と結果受理（未配線）
- Worker行の直接投入は登録手続きの代替ではない

[receipt](../evaluations/records/EKI-TEI-dispatch-running-2026-11-03.json)・[log](../evaluations/records/EKI-TEI-dispatch-running-2026-11-03.log)
## 更新後の一括検証（2026-11-03）

TEI `25a15110d`・EKI `8159af1`・SUI `21d07f01`の組み合わせで、一括検証16段を実行し、すべて通った。EKI投入には現在のEKIからビルドした`eki-control`を使った。[receipt](../evaluations/records/TEI-suite-2026-11-03.json)

## SUIの文書ルートのテスト（2026-11-03）

SUIの文書ルートに関するテスト7ファイルを実行し、122件すべて通った。[receipt](../evaluations/records/SUI-docs-tests-2026-11-03.json)

往復・境界・テナント分離・アクセス制御連携・監査連携・A1エラー契約を含む。`PYTHONPATH=03_Implement/backend/src`が必要で、実配備ではない。

## SUI全テストの1回実行（2026-11-03）

SUIのbackendテスト全体を1回実行した。[記録](../evaluations/SUI-full-tests-2026-11-03.json)

```text
passed 2082 / failed 14 / skipped 49 / deselected 8
所要 約23分
```

失敗14件の内訳は、実行環境に由来するものだった。

- `test_codegen_pipeline.py` 12件: 子プロセスの出力がcp932で表現できず失敗
- `test_external_content_store.py` 2件: `C:\Users\...\Temp`配下への書き込みが拒否される

製品の挙動に関する表明の失敗ではないが、再実行していないため件数は1回の観測である。

## SEIのCLIで判断を記録する（2026-11-03）

投影したSEI判断recordを、SEI自身のCLIで記録し、bundleの書き出しと検証まで通した。[receipt](../evaluations/records/SEI-TEI-cli-2026-11-03.json)

```text
sei init → sei add decision → sei resume → sei export → sei verify
checks 6/6
```

- storeは一時ディレクトリ
- `resume`のスナップショットdigestを記録
- policy gateは通していない

## SEIのgateで許可と拒否（2026-11-03）

投影した判断の文面で、SEIのpolicy gateの許可・拒否の両方を確認した。[receipt](../evaluations/records/SEI-TEI-gate-2026-11-03.json)

- 責任者とrecommendationを備えた判断: `verdict=allow`、終了コード0、`decision_digest`あり
- 責任者の無い判断: `verdict=deny`、終了コード3、理由は「責任者を挙げていない」
- gateはAuthority・行為との一致・Semantic Lineageを検証しないと明示している

## SEIのMCPでAIツールから読む（2026-11-03）

SEIのstdio MCPサーバを起動し、`initialize`・`tools/list`・`tools/call resume`を送った。[receipt](../evaluations/records/SEI-TEI-mcp-2026-11-03.json)

- 公開されるツール: `resume`・`add_recommendation`・`check_decision`
- `resume`は記録済みの判断を返す
- 実AIクライアント・write系ツール・セッション分離は未確認

## MCP経由のcheck_decision（2026-11-03）

SEIのMCPツール`check_decision`を、許可・拒否の両方で呼んだ。[receipt](../evaluations/records/SEI-TEI-mcp-check-2026-11-03.json)

- 責任者とrecommendationを備えた判断: `verdict=allow`、`decision_digest`あり
- 責任者の無い判断: `verdict=deny`、理由あり
- 応答は`content[].text`にJSON文字列として入る

## MMIのunitレーン1回実行（2026-11-03）

MMIの`test:unit`を1回実行した。[記録](../evaluations/MMI-unit-tests-2026-11-03.json)

```text
tests 1329 / fail 1
失敗: hashed sample and kit text assets contain no CR after checkout
```

失敗は、WindowsのCRLFチェックアウトで文書資産にCRが含まれるためだった。製品挙動の失敗ではないが、LFのチェックアウトでの再実行はしていない。CLIにformat profileを適用する経路は無く、形式プロファイルは拡張側の資産である。

## MMI形式プロファイルとの差分（2026-11-03）

MMIの`FormatProfileV1`は`provenance`（`sourceKind`・`sourceDigest`・`generationMethod`）と任意の`approval`を必須に含む。こちらの投影recordは`features`・`sourceEvidence`までで、`provenance`を持たない。

- 契約の`note`にも「provenanceは対象外」と書いてある
- そのため、MMIの`assertFormatProfile`にそのまま通すことはできない
- MMIのCLIにもformat profileを適用する経路が無い

form profileをMMI側の型として成立させるには、投影に`provenance`を足すか、MMIの受理境界を別に定める必要がある。

## MMI形式プロファイルにprovenanceを足す（2026-11-03）

投影の契約とTEIへ`sourceKind`・`sourceDigest`・`generationMethod`を足し、artifactの`profile.provenance`として組み立てるようにした。これでMMIの`assertFormatProfile`が投影を受け付ける。[receipt](../evaluations/records/MMI-TEI-profile-2026-11-03.json)

- 属性は3つ増え、契約は12項目になった
- `generationMethod`は`worksheet-prototype-v1`に固定
- `approval`は対象外のまま

## EKIの取り消し受理（2026-11-03）

実行中（`running`）のTaskへ`POST /v1/tasks/{id}/cancel`を送った。[attempt](../evaluations/EKI-cancel-attempt-2026-11-03.json)

```text
202 {"schema":"eki.task-cancel-accepted/v1","status":"cancellation-requested"}
4秒後の公開状態: running
```

取り消しは受理されるが、attemptが飛行中でWorkerが動いていないため、公開状態は`running`のままだった。Idempotency-Keyが必須で、無い場合は400になる。

## EKIの実行系の範囲（2026-11-03 修正）

EKI `8159af1`には`internal/agent/executor`・`internal/agent/nativerunner`・`internal/agent/assignment`があり、Agent側でWorkOrderのassignmentを受けてコマンドを実行する仕組みがある（sandbox・資源上限・停止を含む）。したがって「実行系が無い」は正確ではない。

これまで確認したのは次である。

- Client APIのTaskは`queued`→（policy・Worker行ありで）`running`まで進む
- Client APIのTaskがassignmentとしてAgentへ届き、実行され、結果がClient APIのTask状態へ戻る経路は未確認
- 結果受理（Result Acceptance）の部品はあるが、`eki-control`の起動経路との接続は未確認

次に確かめるべきは、Client APIのTaskからAgent実行までの縦断である。

## PostgresとTLSの同時構成（2026-11-03）

埋め込みPostgresと自己署名TLSを同時に有効にしてSUIを起動し、保存・取得を確認した。[receipt](../evaluations/records/SUI-TEI-postgres-tls-2026-11-03.json)

```text
httpsReady true / create 200 / fetch 200 / roundTrip true / anonymous 401
```

証明書は自己署名で、リバースプロキシは介していない。管理DB・実CA・配備は依然として未検証である。

## TLS終端プロキシ配下（2026-11-03）

SUIを平文で起動し、手前のローカルTLS終端プロキシ（`X-Forwarded-Proto`等を付与）経由で保存・取得した。[receipt](../evaluations/records/SUI-TEI-proxy-2026-11-03.json)

```text
proxyReady true / create 200 / fetch 200 / roundTrip true / anonymous 401
```

プロキシは検証用の小さな実装で、実運用のリバースプロキシ・HSTS・実証明書は未検証である。

## Worker登録（mTLS）と実行の範囲（2026-11-03）

`eki-control gen-worker-ca`でCAを作り、`enroll-token`を発行し、mTLSのWorker listenerへ`eki-agent enroll`で登録できた。[receipt](../evaluations/EKI-worker-enroll-2026-11-03.json)

```text
enrolled as wrk_5daff2b4de9773099aed44b43b5aa10b in trust domain tei.test
state: control-anchor.pem / worker-ca.pem / worker-identity.pem
```

ただし、Agentのassignment実行は**設定済みの固定コマンドを1つ実行する**ものであり、Taskの内容を実行するものではない（`internal/agent/service/assignments.go`の`ExecutionConfig`: "This is not a sandbox."、`events_file`が観測結果）。したがってClient APIのTaskからAgentへ仕事が渡って実行される縦断は、現時点のEKIでは成立しない。

## ローカルCAの証明書チェーン（2026-11-03）

ルートCAとサーバ証明書の二層構成でSUIを起動し、クライアントはルートCAだけを信頼して接続した。[receipt](../evaluations/records/SUI-TEI-ca-chain-2026-11-03.json)

```text
chainTrusted true / create 200 / fetch 200 / roundTrip true / untrustedRefused true
```

- サーバ証明書はローカルCAが署名（SANに`127.0.0.1`）
- システム信頼ストアのままのクライアントは接続を拒否される
- 公開CAではないため、実運用の証明書ではない

## 複数インスタンスと共有DB（2026-11-03）

1つのPostgresに2つのSUIプロセスを接続し、インスタンス間の読み書きとETagの扱いを確認した。[receipt](../evaluations/records/SUI-TEI-multi-instance-2026-11-03.json)

```text
instancesReady true / create(A) 200 / crossRead(B) 200 / crossUpdate(B) 200 / staleUpdate(A) 409
```

- Aで作成した文書をBで読める
- Bの更新後、Aの古いETagは409で拒否される
- 同一ホスト上の2プロセスであり、別ホスト配備ではない

## Worker実行を止めているもの（2026-11-03）

Agentのassignment実行には`assignment`設定が必要で、次の項目がすべて必須である（`internal/agent/service/assignments.go`）。

- `trust_anchor_file`: `internal/agent/trustanchor`の形式。`trust_domain`・`policy_revision`・`bundle_revision`・`validated_at`・各種上限・Authority公開鍵に加え、`control_public_key`と`trust_bundle_versions`（Control Planeが署名したTrust Bundleの履歴）を持つ
- `replay_db`・`events_file`
- `approved_executors`（`decision_id`・`payload_digest`・`executor_digest`）
- `machine`・`ceiling_percent`・任意の`execution`

`eki-control`/`eki-agent`のCLIにはTrust Bundleを署名・発行するサブコマンドが無く、`conformance/process`のテストが内部パッケージで組み立てている。したがって、TAI側から実プロセスでassignment実行まで進めるには、まずTrust Bundleの発行手順（#78・#478）が必要になる。

## MMIのinspect（実xlsx・2026-11-03）

MMIのCLIでリポジトリ内の実xlsxを読み取り専用でinspectした。[receipt](../evaluations/records/MMI-inspect-2026-11-03.json)

```text
candidates 3 / contract mmi.semantic-candidate/v1
checks 5/5（exit 0・contract・候補あり・sourceDigestあり・table-rangeあり）
```

- シートごとの領域とヘッダを候補として返す
- 各候補に`sourceDigest`（sha256）が付く
- 形式プロファイルの適用や書き込みは行わない

## 監査ログのHTTPエクスポート（2026-11-03）

SUIの監査エクスポートをHTTPトランスポートで有効にし、ローカルのシンクで受信した。[receipt](../evaluations/records/SUI-TEI-audit-2026-11-03.json)

```text
create 200 / view 200 / eventCount 1 / docId一致 / Bearerヘッダ一致
```

- 監査イベントは文書の閲覧（view）で発行される
- `SUI_AUDIT_ALLOW_IN_SAFE_MODE=true`が無いとsafe modeのイベントは送られない
- シンクはローカルの受信用プロセス

## 管理プレーンの認証分離（2026-11-03）

`GET /admin/provision/audit`で、管理キーと業務キーの分離を確認した。[receipt](../evaluations/records/SUI-TEI-admin-2026-11-03.json)

```text
anonymous 401 / business key 401 / admin key 200（events配列）
```

- 管理者キーは`X-Admin-Api-Key`ヘッダ
- 業務キー`X-Api-Key`では管理APIに到達できない
- 利用者provisionとIdP段階（stage B）は未確認

## 利用者provision（2026-11-03）

管理APIで合成利用者を1件provisionした。[receipt](../evaluations/records/SUI-TEI-provision-2026-11-03.json)

```text
POST 201 / provisioned true / reviewerRef・ownerRefはuser: / 同一リクエストで同一userId / 匿名401 / 監査3件
```

- 再実行しても同じ利用者に解決される（冪等）
- 管理操作は監査に残る
- IdP接続は未実施

## SUIがTEIアーティファクトを配信する（2026-11-03）

SUIの`SUI_TEI_REFERENCE_DIR`に、`epistemic-bindings.json`と`tenants/<tenant>/<doc>/<kind>.json`を置き、`GET /docs/{id}/epistemic/projection`で読んだ。[receipt](../evaluations/records/SUI-TEI-reference-2026-11-03.json)

```text
create 200 / projection 200 / artifactEchoed true / 未結合 doc 404（epistemic_binding_not_found）
```

- バインドは（tenant, doc, artifact種別）単位
- SUIはartifactをそのまま返し、スキーマ検証はconsumer側の責務
- 種別は`documentv1-projection`などを許可リストで制限

## 複数artifactの文書別配信（2026-11-03）

2つの文書に別種別のTEI artifactを結合し、それぞれ自分のartifactだけが返ることを確認した。[receipt](../evaluations/records/SUI-TEI-reference-multi-2026-11-03.json)

```text
doc-1 → documentv1-projection（SUI文書）
doc-2 → epistemic-context（SEI判断record）
未結合doc → 404
```

- 文書ごとにartifactが混ざらない
- SEIの判断recordも、TEI artifactとしてSUIから配信できる

## gateのポリシー変種（2026-11-03）

SEIのgateで`--deny-unresolved`と`--require-recommendation`を確認した。[receipt](../evaluations/records/SEI-TEI-gate-variants-2026-11-03.json)

- 未解決の問いを残す判断: 既定では`allow`、`--deny-unresolved`で`deny`
- recommendationを欠く判断: 既定では`allow`、`--require-recommendation`で`deny`
- 理由文にunresolved/recommendationが現れる

## MMIのsource inventory（2026-11-03）

MMIの`inventory`でディレクトリを読み取り専用で棚卸しした。[receipt](../evaluations/records/MMI-inventory-2026-11-03.json)

```text
contract mmi.source-inventory/v0 / status complete / entries 16
各entryにidentity.digest（sha256）とbyteLength
```

- 文書内容は返さず、識別子とダイジェストだけを返す
- 一貫性の表明は`per-file-observation`

## MMIのdelivery audit（2026-11-03）

サンプル文書に対して`delivery-audit`を実行した。[receipt](../evaluations/records/MMI-delivery-audit-2026-11-03.json)

```text
schema mmi.delivery-audit/v0 / scope file-only-excel-mmi-embeds
referentialCompleteness empty / references 0 / exit 1
```

- 対象は**ファイル全体参照**のみで、範囲参照（`#sheet|A1:F13`）は数えない
- そのため件数0・`empty`・終了コード1（差異または不確定）になる
- 納品の完全性を主張しない、という製品の境界どおりの挙動

## EKIの実行は製品テストで成立している（2026-11-03 再修正）

EKI自身のプロセス試験`TestHTTPTaskSubmissionIsExecutedByTheAgent`をWindowsで実行し、PASSした。[receipt](../evaluations/records/EKI-TEI-http-execution-2026-11-03.json)

```text
task=tsk_0392f98887715afb385a41e0020e9980
attempt=atm_b1d8db7f810e3bc11f2cb8ca88e2121c
claim/accepted result digest=cd2eca3535741f27a8ae40c31b0c41d4057a7a7b912b33b9aed86485d1c84676
```

- HTTPで投入したTaskがAgentに実行され、ResultClaimが受理される
- ただしEKIのTEST PROFILE（#198の決定ではない）と、試験自身のTaskによる
- TAIの投影TaskRequestを被験体にした実行は未実施

これまでの「実行系は成立しない」という記述は、TAI側の経路についてのみ当てはまる。製品の試験用経路では成立している。

## 投影TaskRequestをEKIで実行する（2026-11-03）

TAIの投影TaskRequest（平坦なrecord）から、Client APIの封筒（executor/inputs/parameters/resources/reliability/priority）を組み立てて投入した。[receipt](../evaluations/records/EKI-TEI-projection-execution-2026-11-03.json)

```text
投影値のまま: 422 RESOURCE_BUDGET_EXCEEDED（wall 300s・output 16MiB・network 128MiBが試験ポリシー超過）
ポリシー上限へ丸め: task=tsk_a5916e55... 実行・claim取得
```

- 平坦なrecordはそのままでは投入できない（封筒へ組み立てる必要がある）
- 投影値は試験ポリシーの予算（60s/1MiB/1MiB）を超えるため拒否される
- 丸めた場合、EKIのTEST PROFILEで実行とResultClaimまで到達する
- 本番のWorker Protocol互換や権限は未検証

## 予算を製品ポリシーに合わせた投影（2026-11-03）

`present-policy-aligned`ケース（wall 60s・output 1MiB・network 1MiB）を契約へ追加し、その投影をEKIへ投入した。[receipt](../evaluations/records/EKI-TEI-policy-execution-2026-11-03.json)

```text
投影値のまま受理（422なし）→ task=tsk_52632a0a... 実行・claim取得
cases 5→6
```

- 予算はTEIの契約側で表現でき、製品ポリシーに合わせた投影は丸めなしで通る
- 元の`present`ケース（300s/16MiB/128MiB）は製品ポリシーより大きい

## Trust Bundleは必須ではない（2026-11-03 修正）

`internal/agent/trustanchor`の`File`で`control_public_key`と`trust_bundle_versions`は`omitempty`／任意であり、`conformance/signedchain`の`TrustAnchor`は両方を省いてanchorを作っている（`signedchain.go`）。

```go
doc := trustanchor.File{TrustDomain: ..., PolicyRevision: ..., BundleRevision: ..., ValidatedAt: ...}
for _, k := range a.PublicKeys { doc.Keys = append(...) }
```

したがって、assignment実行に必要なのは、Trust Bundleの署名済み履歴ではなく、**Authority公開鍵・trust domain・policy revision・bundle revision・鮮度上限**を持つanchorである。以前の「Trust Bundleの発行手順が先に必要」という記述は誤りだった。発行手段が無いのは`control_public_key`を使う経路（ADR-0036）だけである。

## 自前構成でのEKI実行（2026-11-03）

製品テストに依存せず、Control Planeの設定・Trust Anchor・Agent設定を自前で組み立てて、投影TaskRequestを実行した。[receipt](../evaluations/records/EKI-TEI-manual-execution-2026-11-03.json)

```text
submit 202 / task=tsk_2ab3ccd1... / executed true / claimed true
```

分かったこと:

- 必要なTrust Anchorは`trust_domain`・`policy_revision`（**有効なpolicyのrevision**）・`bundle_revision`・`validated_at`・上限・Authority公開鍵。`control_public_key`と`trust_bundle_versions`は不要
- `policy_revision`を鍵ポリシー（`kp-*`）にすると`lease_policy_revision_mismatch`で拒否される
- native runnerはnetwork上限が非0だと実行を拒否する（`native runner does not enforce network limits`）。`NetworkBytesMax`は0にする
- sandbox profileは`native-fixed-spike`を使う。`NetworkProfile`を付けても`native runner does not implement network profile`になる
- 稀に`approval is issued in the future`でdispatchが延期されることがあるため、再試行を入れた（今回は1回目で成功）

## 実行結果の受入はControl Planeに配線されていない（2026-11-03）

自前構成で実行したTaskについて、ResultClaimは`result_claim_submitted`（`claim_decision: new`）まで進むが、`GET /v1/tasks/{id}/result`は`409 RESULT_NOT_READY`を返す。[receipt](../evaluations/records/EKI-TEI-manual-execution-2026-11-03.json)

```text
executed true / claimed true / result 409 RESULT_NOT_READY
```

- `internal/control`に`resultacceptance`の組み立てが無く、受入は`conformance/process`の試験が内部で構成している
- 2026-11-06時点のEKI上流（`origin/main` `f4451df`）でも`internal/control`配下に`resultacceptance`の参照は無く、`internal/control/service/config.go`にも受入の設定キーが無い。したがって旧版固有の欠落ではない
- 本リポジトリのreceiptは`8159af1`のバイナリで取得している
- したがって「実行して結果が受け入れられる」縦断は、製品プロセスとしては未配線

## Workerの失効（2026-11-03）

`eki-control worker-state`で登録済みWorkerを`revoked`にし、その後の状態を確認した。[receipt](../evaluations/records/EKI-TEI-worker-revoke-2026-11-03.json)

```text
revoked への遷移: 成功
registered へ戻す操作: 拒否（revoked is final）
```

- 失効は最終状態として扱われ、再登録で戻せない
- Agent側の拒否は未確認（assignmentを持たないAgentはWorker listenerを呼ばないため）

## 失効したWorkerのAgent拒否（2026-11-03）

Workerを失効させた後、assignment付きのAgentを起動した。[receipt](../evaluations/records/EKI-TEI-revoked-agent-2026-11-03.json)

```text
control: worker authentication refused reason=worker_not_usable
agent: assignment poll failed: control plane answered HTTP 401
executed false
```

- 失効はControl Planeの認証段で止まる（assignmentの取得すら通らない）
- Agent側は401を受けて実行に進まない

## 複数Workerの登録と割り当て（2026-11-03）

1つのControl PlaneへWorkerを2台登録し、Taskを4件投入した。[receipt](../evaluations/records/EKI-TEI-multi-worker-2026-11-03.json)

```text
workers 2 / submitted 4 / executed 2 / claimed 2 / distributed false
```

- 2台の登録自体は成功する
- この構成ではAttemptが1台に集中し、4件中2件だけが待ち時間内に実行された
- 割り当ての分散や並列度は、この観測だけでは保証できない（未検証）

### 分散しなかった理由の切り分け（2026-11-03）

複数Workerの観測で、Control Planeのログは次の順で動いていた。

```text
dispatch tick considered=2 dispatched=2 deferred=0
dispatch tick considered=2 dispatched=0 deferred=2
  reasons="...: reserve lease: NOT_YET_VALID: approval is issued in the future; ..."
tasks: 2件 verifying / 2件 active
```

- 同時に4件投入すると、dispatchは2件だけをdispatchedし、残り2件を`NOT_YET_VALID`で延期した
- 延期された2件は`active`へ進んだまま、待ち時間内に実行が完了しなかった
- したがって「2台に分散しなかった」のは、Worker選択の偏りではなく、Attemptが2件しか作られなかったため
- `approval is issued in the future`の原因（署名時刻とControl Planeの時計のずれ）は未特定

### `NOT_YET_VALID`の当たり（2026-11-03・仮説）

- 検証は`internal/core/placementverify/verify.go`の`Revalidate`で`now.Before(a.IssuedAt())`のとき`NOT_YET_VALID`を返す
- dispatchは`internal/control/dispatch/dispatch.go`で`l.now()`のスナップショットを取り、`place`で署名し、`Reserve`で再検証する
- 署名時刻がtick開始時のスナップショットより後になると、再検証の`now`が署名時刻より前になり、延期される

この順序に起因する可能性が高いが、Control Planeの時計の取得箇所を計測していないため**未確定**。観測上は次tickで解消し、同時投入時にだけ目立つ。

## SUIのcontext query契約（2026-11-03）

`POST /context/query`の受理と拒否を確認した。[receipt](../evaluations/records/SUI-TEI-context-2026-11-03.json)

```text
200 accepted + queryCanonicalHash
422 preview_required（previewConfirmed=false）
400 unknown_contract_key（未知キー）
400（depth=9）
```

- 契約キーは`extra=forbid`で閉じている
- プレビュー確認が無い問い合わせは受けない
- bundle構築は未実施

## SUIのcontext bundle（2026-11-03）

`POST /context/bundle`を同じ問い合わせで2回実行した。[receipt](../evaluations/records/SUI-TEI-context-bundle-2026-11-03.json)

```text
200 / bundleHash c2890a02... / 2回で同一 / queryCanonicalHashあり
422 preview_required（previewConfirmed=false）
```

- bundleのハッシュは同一入力で安定する
- 使用したstub datasetは`A2-minimal-v1`（合成）
- 実データや実テナントでの構築は未実施

## SUIのCE4 bundle resolve（2026-11-03）

`POST /context/bundles:resolve`をdry-runとapplyで実行した。[receipt](../evaluations/records/SUI-TEI-ce4-2026-11-03.json)

```text
dryRun=true → 200（bundleHash・equivalenceKey・auditChain・proposalLifecycle・sideEffect）
dryRun=false → 200
不正なsourceBundleHash → 400
未知キー → 400
```

- 応答は解決結果と監査連鎖の要約を含む
- 実コンテキスト提供者には接続していない（モック）

## SUIのモデル登録（2026-11-03）

管理APIでモデルレジストリを読み、プロバイダを1件登録した。[receipt](../evaluations/records/SUI-TEI-registry-2026-11-03.json)

```text
GET  /admin/provision/models → 200（providers/models）
POST /admin/provision/models/providers（providerKind=local）→ 201
匿名 → 401
未対応のproviderKind → 422
```

- 登録できるproviderKindは`local`・`large-scale`・`deepseek`
- 実モデル呼び出しは行っていない

## 上流最新版での再実行（2026-11-06）

EKI上流`66b0c04`で`eki-control`/`eki-agent`を再ビルドし、自前構成の実行を再度通した。[receipt](../evaluations/records/EKI-TEI-manual-execution-2026-11-03.json)

```text
binaries: eki-control-66b0c04.exe / eki-agent-66b0c04.exe
executed true / claimed true / result 409 RESULT_NOT_READY
```

- 実行系は旧版（8159af1）と同じ手順で通る
- 結果の受入は`66b0c04`でも未配線（409が継続）
- receiptの`binaries`欄に使用したバイナリを記録するようにした

## 更新後のSUI・EKIでの一括検証（2026-11-06）

SUIを`09c24046`、EKIを`66b0c04`へ更新して、一括検証53段を再実行した。[suite receipt](../evaluations/records/TEI-suite-2026-11-03.json)

```text
result PASS / steps 53 / TEI 2d0b09b13 / SUI 09c24046 / SEI e8d13e0 / MMI b07ed4a2 / EKI 66b0c04
```

- 更新後も保存・TLS・Postgres・監査・管理API・context系・EKI実行系の段が通る（TEI/SEI/MMIの更新も同時に確認）\n- 5リポジトリすべてを最新の`origin/main`へ揃えた組み合わせで53段PASS
- 端末固有のreceipt（ID・時刻）は再生成されるため、追跡するのはsuite receiptと本節のみ

公開gateは`allowed=false`のまま。

## Agent資格情報と監査出力の関係（2026-11-06）

`agent_audit_is_not_exported`を直接呼んで確認した。[receipt](../evaluations/records/SUI-TEI-agent-guard-2026-11-06.json)

```text
agent有効・監査出力なし → guard true
監査出力あり（SafeMode含む） → guard false
```

- 実装は起動を止めず、警告ログを出す（fail-openの警告）
- したがって「監査なしでは起動しない」という前提は誤り。統制は警告と運用に依存する
- 起動ログ自体の捕捉はしていない（規則の評価のみ）

## Agent資格情報の登録APIの拒否（2026-11-06）

`POST /tenant-admin/agent-credentials`を、tenant adminセッションなしで呼んだ。[receipt](../evaluations/records/SUI-TEI-agent-credential-admin-2026-11-06.json)

```text
匿名 → 401
業務キー（X-API-Key）のみ → 503
```

- 業務キーはtenant admin経路の代用にならない
- local-devでは信頼済みSaaSランタイムが未構成のため503（fail-closed）
- SaaSプロファイルで実際のtenant adminセッションを使った登録は未確認

## 管理監査のカーソルページング（2026-11-06）

`GET /admin/provision/audit`を`limit=1`で2回読み、カーソルで次ページを取得した。[receipt](../evaluations/records/SUI-TEI-audit-pagination-2026-11-06.json)

```text
1ページ目: 200 / events 1 / nextCursor あり
2ページ目: 200 / events 1 / 1ページ目と重複なし
```

- カーソルは単調に進み、ページ間で同じイベントを返さない
- 不正なカーソルは拒否されず、200で先頭ページを返す（実装は不明なカーソルを無視する）\n- カーソルの失効や大量の監査での挙動は未確認

## 文書ETagの安定性と条件付きGET（2026-11-06）

同じ文書を2回読み、`If-None-Match`付きで再読し、編集保存後に再度読んだ。[receipt](../evaluations/records/SUI-TEI-etag-stability-2026-11-06.json)

```text
保存 200 / ETag あり
2回読み: ETag が一致（安定）
If-None-Match 付き再読: 200（本文をそのまま返す）
編集保存 200 → ETag が変化
```

- ETag は内容のハッシュで、読みの間は安定する
- 条件付きGETは `304` を返さず、毎回本文を返す。読者は転送量を削減できない
- 編集保存でETagが変わるため、楽観ロックの前提は保たれる

## アーカイブの書き込み禁止（2026-11-06）

文書をアーカイブし、読み・書き・復帰を順に試した。[receipt](../evaluations/records/SUI-TEI-archive-lifecycle-2026-11-06.json)

```text
保存 200 → archive 204 → 読み 200（閲覧は可能）
アーカイブ中の書き込み → 423 document_archived
unarchive 204 → 書き込み 200
```

- アーカイブは閲覧を残したまま書き込みだけを止める
- 復帰後は同じ操作で書き込みが通る
- 並行書き込みやagent資格情報での挙動は未確認

## 統合判断ログの追記専用性（2026-11-06）

`POST /docs/{id}/merge-decision-logs`で同じ判断を2回送り、一覧を読んだ。[receipt](../evaluations/records/SUI-TEI-merge-decision-log-2026-11-06.json)

```text
初回追記 201 / 一覧 200（1件、decision-1）
同一decisionIdの再送 409
未登録グループの一覧 200（0件）
```

- 判断ログは追記専用で、同じ判断の上書き・重複は409で拒否する
- 未知のグループは空の一覧を返し、存在しない文書の404とは区別される
- スナップショット版での復元ビュー（restore/{snapshotVersion}）も200で、未登録の版は0件を返す\n- 並行追記や他tenantの認可は未確認

## CE4監査イベントの順序規則（2026-11-06）

`POST /docs/{id}/context-audit`で、イベント順と整合性の規則を順に試した。[receipt](../evaluations/records/SUI-TEI-ce4-audit-order-2026-11-06.json)

```text
他のイベント前のapply → 409 missing_event（不足: bundle, proposal, query）
query → 200 / bundle → 200 / proposal → 200
全イベント後のapply → 200
sourceBundleHashの不一致 → 409 equivalence_mismatch
operationとcommandの不一致 → 422 operation_command_mismatch
```

- applyは先行イベントが揃うまで拒否され、不足分を`missingEvents`で返す
- 提案と適用の`sourceBundleHash`連鎖は不一致を409で止める
- trackerの失効窓や別tenantとの干渉は未確認

## ポリゴン受け渡し契約の検証（2026-11-06）

`POST /docs/{id}/polygon-handoff/verify-contract`を、正常系と違反系で試した。[receipt](../evaluations/records/SUI-TEI-polygon-handoff-2026-11-06.json)

```text
違反なし → 200 ok / rollbackRequired=false / verificationKey 64桁
paddingViolationCount=2 → 200 rollback_required / ["paddingViolationCount>0"]
tieBreakOrderを逆順 → 200 rollback_required / ["tieBreakOrderChanged=true"]
既定順を明示 → 200 ok
存在しない文書 → 404
不正なinputHash → 422
```

- 判定は決定的で、違反の種類を`failureReasons`で区別する
- 成功・失敗いずれも200で返し、状態は本文で表す
- 実ポリゴン計算との接続は未確認（契約検証のみ）

## 類似候補グループの生成規則（2026-11-06）

`GET /docs/{id}/similar-candidate-groups`を、正規化一致・語の一致・無関係・空文字・統合済み・出典付き・正規ID付きのカードで試した。[receipt](../evaluations/records/SUI-TEI-similar-candidates-2026-11-06.json)

```text
正規化一致（"Same  Text" と "same text"） → normalized_text + token_signature
語の一致（"alpha beta" と "beta alpha"） → token_signature
無関係・空文字 → グループ化されない
統合済み・出典付き・正規ID付き → 対象外
snapshotVersion は12桁
存在しない文書 → 404
```

- 2つのヒューリスティックが一致した場合、1グループに両方の理由コードが付く
- 対象外カードの除外は、統合・出典・正規IDのいずれでも効く
- 実類似モデルとの接続は未確認（規則ベースのみ）

## 書き出し監査の重複抑止（2026-11-06）

`POST /docs/{id}/export-audit`で、同じ`exportId`の再送・別`exportId`・`exportId`なしを順に送り、ローカルのsinkに届いたイベントを数えた。[receipt](../evaluations/records/SUI-TEI-export-dedup-2026-11-06.json)

```text
同一exportIdの2回 → bundleのイベントは1件（再送は抑止）
別exportId → bundleが計2件（別の書き出しは残る）
exportIdなし → markdownが1件（抑止しない）
```

- 重複抑止の単位は`exportId`で、書き出しの種類や回数ではない
- `exportId`を省いた古いクライアントの記録は落とさない
- 抑止窓の境界と再起動をまたぐ挙動は未確認
- `safeMode=true`では`export`が403（fail-safe）になるため、本検証は`safeMode=false`で行った

## ネイティブAction受信の既定無効と多段の門（2026-11-06）

`POST /docs/{id}/action-commit`を、機能フラグを立てた状態で試した。[receipt](../evaluations/records/SUI-TEI-native-action-2026-11-06.json)

```text
フラグ無効 → 404 action_denied（通常配備では面を公開しない）
X-TEI-Actionなし → 403 / 別オリジン → 403 request_origin_denied
古いexpectedRevision → 409 revision_conflict / 未知のcardId → 400 invalid_payload
X-Read-Only: 1 → 403
正しい要求 → 200（新しいrevisionを返し、カード座標が x=100, y=50 に変わる）
同じ要求の再送 → 409 revision_conflict（リプレイを拒否）
アーカイブ中 → 423 action_denied
```

- 受信面は既定で無効で、TEI Host接続時に明示的に有効化する前提
- 認証・版・同一オリジン・読み取り専用・リプレイ・アーカイブの各門が個別に働く
- 実TEI Hostや認証済みセッションとの接続は未確認

## 文書一覧のカーソルページング（2026-11-06）

`GET /docs`を`limit=2`で読み、`X-Next-Cursor`を辿った。[receipt](../evaluations/records/SUI-TEI-list-pagination-2026-11-06.json)

```text
4件作成 → 1ページ目 200 / 2件 / カーソルあり
2ページ目 200 / 2件 / 重複なし
3ページ目なし（最終ページにカーソルなし）
4件すべてが一度ずつ出る
limit=501 → 422
```

- 一覧は本文を含まない行メタデータのみ
- カーソルは `updated_at:id` の組で、ページ間の重複も取りこぼしもない
- アーカイブ済みの文書も一覧に載り、`lifecycle_state`で区別できる（一覧からは消えない）\n- `createdBy`に無関係な主体を指定すると0件を返す（作成者での絞り込みが効く）\n- ページング中の並行書き込みは未確認

## agent資格情報の読み取り経路（2026-11-06）

資格情報を作り、許可した文書の読み・書き・一覧・派生ビュー・未付与文書・混在資格情報・不正トークン・監査を順に試した。[receipt](../evaluations/records/SUI-TEI-agent-read-path-2026-11-06.json)

```text
付与文書の読み → 200（ETagなし、カード2枚、確認済みのみ本文あり、題名は返さない）
書き → 403 agent_write_not_enabled
一覧 → 200（付与文書のみ、題名と作成者は伏せる）
派生ビュー（類似候補） → 403 agent_route_not_enabled
未付与文書 → 404 agent_document_not_granted
混在資格情報 → 400 agent_credential_conflict
不正トークン → 401
context-audit（channel=mcp） → 200 / channel=api → 403
```

- agentは文書の本文を「人が確認したカード」に限って読める。未確認カードは本文もidも返さない
- 派生データ（類似候補など）は経路ごとに閉じており、許可は明示リストで管理する
- **`SUI_AGENT_CREDENTIAL_HASH_KEY`を設定しても、local-devプロファイルではapp.stateへ配線されない**（配線は`settings.runtime_profile == "saas-multitenant"`の分岐内にある。ASTで確認済み）。本検証は検証内で鍵を配線して経路を評価した
- 本番相当プロファイルでの配線と、実外部agentとの接続は未確認

## SaaSの書き込み前提条件（2026-11-06）

`_require_saas_document_precondition`を9通りのヘッダーで直接呼び、返る状態とコードを記録した。[receipt](../evaluations/records/SUI-TEI-saas-precondition-2026-11-06.json)

```text
If-Match/If-None-Match なし（更新・作成） → 428 document_precondition_required
両方指定 → 400 document_precondition_conflict
If-Match: * → 428（ワイルドカードで版検査を迂回できない）
If-Match: "abc", * → 428
If-None-Match: "abc"（作成） → 400 document_precondition_invalid
If-None-Match: * で既存 → 409 document_already_exists
If-Match: "abc"（更新） / If-None-Match: * （新規） → 通過
```

- SaaSプロファイルは暗黙の上書きを許さず、更新は具体版、作成は`If-None-Match: *`を要求する
- ワイルドカードは一覧に混ぜても迂回にならない
- local-devではこの前提条件が有効でないため、HTTP経路ではなくヘルパーを直接呼んで評価した

## 監査重複抑止の窓（2026-11-06）

`AuditDispatcher`を直接動かし、抑止窓の境界を測った。[receipt](../evaluations/records/SUI-TEI-dedup-window-2026-11-06.json)

```text
窓=0 → 同じキーの3回がすべて送信（抑止なし）
窓=0.2秒 → 直後の再送は duplicate で抑止、0.35秒後は送信
キーなし → 2回とも送信（抑止しない）
送信失敗 → send_failed、再送は queued_pending（待ち行列の控えを送る）
```

- 抑止は「送信に成功したキー」だけを記録するため、失敗した初回は再試行できる
- 抑止の単位は呼び出し側が渡す論理キーで、イベント内容では判定しない
- HTTP輸送路や再起動をまたぐ挙動は未確認

## 実行プロファイルの政策表（2026-11-06）

`resolve_tenant_session_bootstrap_mode`を5つのプロファイル名で呼び、`main.py`/`access_control.py`のガードと突き合わせた。[receipt](../evaluations/records/SUI-TEI-profile-policy-2026-11-06.json)

```text
local-dev / evaluation / enterprise-production → single-tenant
saas-multitenant → tenant-session-required
未知のプロファイル → RuntimeError（fail-closed）
APIドキュメント公開: local-dev / evaluation のみ
agent系配線: saas-multitenant のみ
export/share のSafeMode拒否: access_control に存在
```

- どの機能がどのプロファイルで有効かは、プロファイル文字列を条件にした分散したifで決まる
- 未知のプロファイルは起動時点で拒否される
- 各プロファイルの実起動は未確認（saas-multitenantは実IdP等が必要）