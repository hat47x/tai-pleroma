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