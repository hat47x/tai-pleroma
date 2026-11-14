# 製品横断Handoff `yi.handoff.context/v1`：最小の二製品経路と段階的検証計画

2026-11-11。YI Constellation の複数製品が**外部AIハーネスのSession**を共有し、TEI・SHO・SUI・SEI の専門機能を協調利用するための、最小の製品横断 Handoff 機構。

本書は設計と実装の記録である。**全新規の共通実行基盤・中央Host・第二Registry・権限Engineは作らない。** 既存の Product Skill・Activity・Context Projection・Source Provenance・Evidence・Handoff 契約の延長として成立する範囲だけを実装する。

## 1. 調査した契約（2026-11-11 時点の最新main）

### 1.1 製品別の正本とSkill

| 製品 | Product Skill（個別に利用可能） | read-only入口 | Handoff関連の既存契約 |
| --- | --- | --- | --- |
| TAI | `examples/skills/yi-tai-activity/SKILL.md`（横断。**必須前提にしない**） | 製品Coreを持たない | Handoff票の最小要素（[SK-03 §4](harness-interoperability-and-handoff-pilot-2026-11-03.md)）、選択的再資格化（TAI #271） |
| TEI | `skills/yi-tei-modeling/SKILL.md`（main統合済み） | `go run ./cmd/tei commands/model catalog/inspect/trace/validate` | `worldFingerprint`／`sourceIndexFingerprint`、`reference/composition-evidence-handoff`（E9〜E11 の証拠参照照合） |
| SHO | `skills/yi-sho-compose/SKILL.md`（main） | `node bin/sho-inspect.cjs inspect <md>` | `source.sha256`／`revision=unknown`／`coverage`、SUI→SHO P0同一ファイル試験 |
| SUI | `skills/ponytail/SKILL.md`、MCP `get_context_projection`（main） | `GET /docs/{id}/tei/sui-reference`（PR #3428 でmain統合） | `context-projection.v1`、`tai.reference.tei-documentv1-projection/v0`、ADR-0101 transport、ADR-0114 handoff JSON |
| SEI | `skills/ponytail/SKILL.md` | Go runtime・contracts | `sei.semantic-reference/v1alpha1` ほか5家族、`sei.semantic-interchange/v1alpha1` |

**各Product Skillは単独で利用可能な構成を維持する。** TAI の横断Skillは追加群であり、必須の前提にしない。TEI単独・TAI無し・MCP無しで read-only 利用できる。

### 1.2 既存の製品間経路と、その限界

| 経路 | 状態 | 限界 |
| --- | --- | --- |
| SUI → SHO | 両側がmainに実装済み。P0同一ファイル試験（test-only Runner） | byte一致のみ。元製品・Revision・開示Scope・未解決・用途制限が運ばれない |
| TEI → SUI | SUI consumer側がmain（PR #3428）。producer契約（`source.status`・文書単位開示）はOwner判断待ち | SUIは第二のデータ正本を作らない |
| SHO → TEI／SEI → 各製品 | 経路なし | 実装しない |

## 2. 何をHandoffと呼び、何を呼ばないか

**Handoffとは**、一つの製品の**用途に相対的なread-only Projection**を、別の製品が**独立に再読取**して業務上の次の作業へ接続する操作である。

**Handoffではないもの**：

- 会話履歴の移行。履歴はSessionの内部状態であり、資格・根拠・未完了義務の証明にならない。
- Tool成功・Agentの`done`文字列・CI成功。これらは意味受理・権限・実Effectの証拠にならない。
- Harness Sessionを中央正本にすること。Sessionは運搬経路である。

したがって票は **Task・根拠（evidence）・未完了の義務（obligations）・確認が必要な依存関係（dependenciesToConfirm）** を別欄で運ぶ。会話履歴は `conversationHistory.included=false` を**宣言**して運ばない。

## 3. Harness Sessionの位置づけ

- Harness Session は**運搬経路**。製品間の対話・作業継続に使う。
- Harness Session は**中央正本ではない**。各製品のデータ正本・意味受理・権限・実行結果は各Product/Hostが保持する。
- 票の `transport` は**運搬観測のみ**。`transport.authority` は常に `none`。Harness名・Sessionラベルは記録であり、資格・再送保証・継続許可を与えない。
- Sessionを切り替えても、別Harnessへ移行しても、票が運ぶ情報は不変。増幅するのは観測ラベルだけ。

## 4. 選んだ経路：SUI → SHO（最小の二製品Handoff）

### 4.1 選定理由

- **両側がmainに実装済みの実入口**がある。合成のみで成立させる経路を作らなくて済む。
- TEI→SHO・SHO→SUI・SEI連携は、producer/consumer契約が未確定（ADR-0116は`source.status`と文書単位開示をOwner判断待ち）であり、契約変更を要する。**最小の経路として既存契約で成立するものを選ぶ。**

### 4.2 単一の操作

一つのHandoff操作は、**一つのread-only Context**を運ぶ。payload 1ファイルと票 1ファイルの組だけを書出す。

```
SUI 実Producer（handoff_context_emit.test.ts / handoff_context_envelope.ts）
   → payload（read-only Markdown草稿、P0固定354 bytes契約を維持）
   → 票（yi.handoff.context/v1）
SHO 実Consumer（bin/sho-inspect.cjs handoff <票>）
   → 票の厳格検証 → payload の独立再読取 → byte/digest 照合 → 受領Receipt
```

Producer側はI/Oを行わない純関数モジュールとする。書き出しは呼び出し側の**明示的操作**だけ。自動送信・バックグラウンド送信・直接POSTの経路は存在しない。

### 4.3 票が運ぶ欄（要求された全項目を含む）

| 要求 | 票の欄 |
| --- | --- |
| 元製品 | `producer.product`／`producer.entrypoint`／`producer.version`／`producer.productSkill` |
| 対象ID | `target.product`／`target.kind`／`target.id` |
| Revision | `revision.kind`／`revision.value`／`revision.digest`（`sha256:<64小文字hex>`）／`revision.observedAt` |
| 開示Scope | `disclosure.scope`（閉集合）／`disclosure.audience`／`disclosure.purpose`／`disclosure.rawSource="not-exportable"` |
| 参照先 | `references[]`（`kind`・`locator`・`digest`・`note`） |
| 未解決情報 | `unresolved[]`（`id`・`kind`・`description`） |
| 用途上の制限 | `usageRestrictions[]` |
| Task | `task.statement`／`task.completionDefinition` |
| 根拠 | `evidence[]`（`claim`・`basis`・`observedAt`・`limitation`） |
| 未完の義務 | `obligations[]`（`id`・`description`・`owner`） |
| 確認が必要な依存関係 | `dependenciesToConfirm[]`（`id`・`description`・`confirmWith`） |
| 再確認要求 | `consumerRecheck[]` |
| 残作業 | `residualWork[]` |
| 運搬観測 | `transport.harness`／`transport.sessionLabel`／`transport.authority="none"` |
| 会話履歴でないこと | `conversationHistory.included=false` |

**運ばないもの**：Card本文の生データ・Island題名・Document題名・Narrative・要約・review attribution・原本Source・権限・Grant・資格・Credential。権限系keyと資格マーカーはProducer/Consumerの双方で実行時に拒否する。

### 4.4 fail-closed の規則

| 条件 | 動作 |
| --- | --- |
| `disclosure.scope` が閉集合外 | 拒否。`active`・`public` へ読み替えない |
| `disclosure.audience` が空 | 拒否 |
| `disclosure.rawSource !== "not-exportable"` | 拒否 |
| digest が `sha256:<64小文字hex>` 以外 | 拒否（欄名をエラーに含める） |
| `payload.relPath` がbare filename以外 | 拒否（パス区切り・`..`・先頭ドット） |
| payload のbyte数・digestが不一致 | **解釈より先に**拒否。部分受領を部分成功にしない |
| `conversationHistory.included !== false` | 拒否 |
| `transport.authority !== "none"` | 拒否 |
| 権限系keyがどこかに出現 | 拒否（出現路をエラーに含める） |
| serializeされた資格素材の形が現れる | 拒否（`-----begin`・`bearer `・`authorization:`・`api_key`・`access_token` 等） |
| `schema` が未知 | 拒否。opaque payloadとして推定解釈しない |

**資格の混入は二つの検査で防ぐ。** key名の完全一致（`grant`・`token`・`credential`・`secret`・`password`・`authorization`・`permission`・`role`・`lease` 等を、大文字小文字を無視してanywhereで拒否）と、serializeされた資格素材の形。`credential` や `secret` を**単語として**禁じると、他製品の読み取り専用観測を引用したときに偽陽性になる。TEIの参照Workspaceには `security.credential`・`security.authorization_grant` というsubject IDが実在し、read-only CLIのcatalog出力に現れる。したがって業務語はkey名側でのみ扱う。

## 5. 実装と検証の結果

> **本書は G1（二製品Handoff）時点の設計・契約の記録である。** その後の G2〜G6 の実装と実測結果は [後続実行票 G2〜G6](cross-product-handoff-execution-tickets-2026-11-11.md) の「実行状況」表にまとめてあり、**数値と状態はそちらが現在の正**。本書の §5・§6 は初期スナップショットとして残す。

| リポジトリ | 変更 | 検証 |
| --- | --- | --- |
| sui-sensemaking | `src/export/handoff_context_envelope.ts`（Producer、純関数）、`handoff_context_envelope.test.ts`、`handoff_context_emit.test.ts`（単一操作の書出）、`handoff_receipt_review.ts`、`handoff_tei_observation_emit.test.ts`、`01_Plans/adr/ADR-0117` | `vitest run src/export` 238 passed/4 skip、`tsc --noEmit` exit 0 |
| sho-composer | `src/handoff_envelope.cjs`（Consumer、独立実装）、`bin/sho-inspect.cjs handoff`、`test/handoff-envelope.test.cjs`、`scripts/handoff-cross-product.cjs`、`scripts/handoff-harness-switch.cjs`、`.github/workflows/sho-handoff-consumer.yml`、試験記録 | `node --test test/handoff-envelope.test.cjs` 29 passed、`test/g1b-reader.test.cjs` 20 passed/2 skip、Runner 実exit 0 |

### 5.1 二製品実受領で確認したこと（実製品E2E）

Runner は**SUIの実Producerテスト**と**SHOの実CLI**を呼ぶ。2製品モードで10観測、3製品モード（`--tei-root`）で12観測すべてok。

1. `producer-emit`：354 bytes、独立期待SHA一致。
2. `consumer-receive`：実CLI exit 0、parser 14.3.3、`revision=unknown`、coverage全false、未解決3件・義務2件・依存2件が運ばれる。
3. `source-updated-after`：受領後にpayloadを書き換えると、次の受領は `handoff-payload-size-mismatch`。
4. `second-session`：別Sessionで再受領。payload・claimsは同一、`sessionInheritedAuthority=false`。
5. `harness-switch`：別Harnessで再受領。claimsは完全一致、`authorityCarried=false`・`externalDisclosure=false`。
6. `partial-receipt`：payloadを100 bytesに切り詰めると `handoff-payload-size-mismatch`、stdoutにReceiptなし。
7. `tampered-authority`：`producer.grant` を足すと `handoff-authority-field`。
8. `conversation-replay`：`conversationHistory.included=true` は `handoff-conversation-history`。
9. `disclosure-scope-widened`：`disclosure.scope=public` は `handoff-disclosure-scope-unknown`。
10. `receipt-returned-and-reviewed`：受領Receiptを書出し、Producerが票digestで独立照合（G2）。
11. `tei-readonly-observation-cited`：実TEI read-only CLIの観測を票へ引用し受領（G3）。
12. `new-process-rereceive`：別プロセス・別ラベルで再受領。payload・checks・carriedForwardが完全一致（G4）。

**資格の上限**：合成データ・ローカル一時ファイル・実製品の入口による限定試験。実SUIランタイムUI、実ネットワーク、実SHO Writer、原本Source、OKF/SEI意味受理は含まない。RunnerのCI（`--sui-frontend` を与えない）ではProducerを実行しない。**通常CIのPASSをlive handoffのPASSに数えない。**

**来歴ゲート**：Runner はrepo全体のHEAD一致ではなく、**Producer入力3ファイルのgit blob SHA**をピン留めする。無関係な開発中のcommitで試験が不成立にならない一方、Producerコードが変わると崩れる。ピンは独立にProducer差分を確認したときだけ更新する。

**削除確認の順序**：`fileDeletedAfterTrial` は Receipt の組み立て・出力**より前**に、実際の `rmSync` と存在確認から確定させる。確認できなければ Receipt を出さず失敗する（未実行の確認を合格として記録しない）。

## 6. 段階的検証計画（二製品成立後）

| 段階 | 内容 | 現在 |
| --- | --- | --- |
| **G1（完了）** | 二製品の単一read-only Handoff。実受領・独立再読取 | 実証済み（§5.1） |
| **G2** | 受領ReceiptのProducerへの返送経路。現在はConsumer側に留まる | 未実装 |
| **G3** | 三製品以上の協調。第二のHandoff（例：SHOの索引ReceiptをTEIへ）。**producer/consumer契約が未確定** | NOT RUN |
| **G4** | Session再開。Goal Round跨ぎ・Host再起動後の再受領と現在資格の再確認 | 部分的（別Session再受領は実証）。Session永続・再開自体は未実装 |
| **G5** | 別Harnessへの移行。実Harness（DSH/Codex/Claude Code等）での実呼出し | NOT RUN。票はHarness非依存であることを構造で示したのみ |
| **G6** | Source Provenance・Evidenceの Product Oracle。TEI #2586/#2516、SEI contracts への接続 | 各Owner |

> 上の表は**本書執筆時点（G1直後）のスナップショット**。G2〜G6 はその後すべて実装・実測され、状態は [後続実行票](cross-product-handoff-execution-tickets-2026-11-11.md) の「実行状況」表が現在の正。

G2〜G6 の**実行票**（目的・非目的・前提・変更ファイル・契約差分・機械確認可能な受入条件・必須負例・撤退条件・Ownerゲート）は [後続実行票 G2〜G6](cross-product-handoff-execution-tickets-2026-11-11.md) に具体化済み。G3は**新しい契約を一つも作らず**、TEIのread-only CLI観測を票の `evidence[]`/`references[]` として引用する形で実装できる。

G3以降は**新しい契約を増やさず**、既存Ownerの試験へ接続する。第二のDispatcher・共通Context JSON正本・自動Schedulerは、実不足が示された場合にのみ具体案として検討する。

## 7. Owner判断

**2026-11-11 に OG-1〜OG-8 を代行決定済み。** 一覧と理由は [後続実行票 §7](cross-product-handoff-execution-tickets-2026-11-11.md) に記載。実 Owner は各決定を覆せる（覆す場合は Issue/PR に理由を残す）。

代行決定の要点：

1. **開示Scope語彙**：v1 の閉集合（`synthetic-only`／`reviewed-projection-only`）のまま。新增しない。
2. **`source.status` と文書単位の開示宣言**：TEI側契約に追加しない。無いまま `unknown` として動かす。
3. **本文・題名の公開**：しない。既定は SafeMode ON、構造のみ（SUI #3369 は据え置き）。
4. **共通実行基盤の新設・権限境界の変更**：却下。作らない・変えない。
5. **受領Receiptの返送と監査**：Receipt は一時作業物。保持義務を課さず、監査・コンプライアンス用途に使わない。

## 8. 安全不変条件（緩和しない）

- SafeMode・未レビュー非公開・`human_reviewed`・proposal-onlyの境界を緩和しない。
- Card本文・Island題名・Document題名・Narrative・要約・review attributionを票やpayloadへ載せない。
- 第二のデータ正本・意味Registry・第二のProvider・共通Agent Runtimeを作らない。
- 各Product Skillは個別に利用可能な構成を維持する。TAI横断Skillを必須の前提にしない。
- Harness Sessionを中央正本にしない。Sessionは運搬経路である。
- 会話履歴の移行をHandoffと呼ばない。
- 合成試験の成功を実製品E2Eの成功として扱わない。未実行の検証を合格と記録しない。

## 関連

- TAI：[SK-03](harness-interoperability-and-handoff-pilot-2026-11-03.md) §4 Handoff票の最小要素、TAI #271（再資格化）、#232（機密と実Egress）、#168（Harness互換）
- SUI：[ADR-0117](../../../sui-sensemaking/01_Plans/adr/ADR-0117-cross-product-handoff-context-envelope.md)、ADR-0054（外部接続のread-only投影）、ADR-0114（handoff）、ADR-0116（TEI参照のSource状態と開示制限）
- SHO：[二製品実受領の限定試験](../../../sho-composer/docs/handoff-cross-product-trial-2026-11-11.md) と [実実行Receipt](../../../sho-composer/docs/handoff-cross-product-trial-receipt-2026-11-11.json)
- TEI：#2515（実効隔離/全送出Conformance）、#2516（用途別Projection）、#2586（Query→Context→Claim）、#2605（Product Skill）
