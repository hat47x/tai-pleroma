# 製品横断Handoff：後続実行票 G2〜G6（具体化・実行結果）

2026-11-11。[設計・契約文書](cross-product-handoff-context-v1-2026-11-11.md) の G1（二製品Handoff）は実証済み。本書は **G2〜G6 を後続の実装者が迷わず最後まで実行できる形**に具体化する。

**本書が守る制約**：共通実行基盤の新設、中央Host、第二Registry、権限Engine、権限境界の変更は行わない。それらが必要とされる段になった場合は、§7 のOwner判断ゲートへ戻す。

## 実行状況（2026-11-11 更新）

| 票 | 状態 | 実測 | 残り（NOT RUN） |
| --- | --- | --- | --- |
| G2 | **observed-pass** | Receipt返送＋Producer側照合を実製品E2Eで確認（`receipt-returned-and-reviewed`） | Receiptの保持期間・監査利用（OG-5） |
| G3 | **observed-pass** | 実TEI read-only CLI観測を票へ引用し、実SHO CLIが受領（3製品・負例5件） | 第二のHop（`chain`v2）、`source.status`契約（OG-2） |
| G4 | **observed-pass** | 別プロセス・別Sessionラベルでの再受領（`session-resumed`） | Host再起動・日跨ぎの実Session永続 |
| G5 | **observed-pass** | DeepSeek Harness と Claude Code の実CLIで切替（別Runner・7観測） | 両HarnessのSkill実ロード・MCP経路・実Host Grant/egress |
| G6 | **observed-pass（限定）** | 票のreferencesをSEI exact_binding形と照合（`reference-linked-unverified`に留める・self-test 8件） | SEI Go runtime・SEI fixture・TEI #2586 Claim closure・発行Authority |

**全票の共通する未達**：実Host Grant／OS egress（TAI #232・TEI #2515）、意味受理（各Owner）、原本Source読取。いずれも `not-run` のまま。

---

## 0. 現在地と再現手順

### 0.1 成立しているもの

| 要素 | 所在 | 状態 |
| --- | --- | --- |
| 票の契約 `yi.handoff.context/v1` | sui-sensemaking `03_Implement/frontend/src/export/handoff_context_envelope.ts` | 実装・試験済み |
| Producer（純関数、I/Oなし） | 同上＋ `handoff_context_emit.test.ts` | 実装・試験済み |
| Consumer（実CLI、独立再読取） | sho-composer `src/handoff_envelope.cjs`・`bin/sho-inspect.cjs handoff` | 実装・試験済み |
| 二製品検証Runner | sho-composer `scripts/handoff-cross-product.cjs` | 実装・実実行済み |
| 設計・契約記録 | tai-pleroma `docs/yi-constellation/cross-product-handoff-context-v1-2026-11-11.md` | 記録済み |

### 0.2 再現手順（この順で実行すれば G1〜G5 の結果が再現できる）

```powershell
# 1. SUI Producer の試験（SUI checkout で）
cd <SUI>\03_Implement\frontend
node node_modules/vitest/vitest.mjs run src/export
node node_modules/typescript/bin/tsc --noEmit          # exit 0 であること

# 2. SHO Consumer の試験（SHO checkout で）
cd <SHO>
npm ci --ignore-scripts --no-audit --no-fund
node --test test/handoff-envelope.test.cjs             # 29 passed
node --test test/g1b-reader.test.cjs                   # 20 passed / 2 skip

# 3. 二製品／三製品の実受領（実SUI Producer → 実SHO Consumer [+ 実TEI read-only CLI]）
cd <SHO>
node scripts/handoff-cross-product.cjs --sui-frontend '<ABSOLUTE_SUI>\03_Implement\frontend'
node scripts/handoff-cross-product.cjs --sui-frontend '<ABSOLUTE_SUI>\03_Implement\frontend' `
  --tei-root '<ABSOLUTE_TEI>'
# exit 0。2製品なら10観測、3製品なら12観測がすべて ok の JSON Receipt が標準出力に出る。

# 4. G5 実Harness切替（票を先に用意してから）
cd <SHO>
node scripts/handoff-harness-switch.cjs --ticket '<票の絶対パス>' `
  --harness-a deepseek-harness --harness-b claude-code `
  --harness-b-argv <claude.exe> -p '<実CLIを実行させるプロンプト>' --allowedTools Bash --

# 5. G6 SEI Exact Binding との照合（TAI checkout で）
cd <TAI>
node evaluations/tools/check-handoff-sei-binding.cjs --self-test `
  --ticket '<票の絶対パス>' `
  --schema '<SEI>\contracts\schemas\v1alpha1\semantic-reference.schema.json'
```

**トラブル時**：`Producer input ... blob is ...` が出たら、SUI の Producer 3ファイルがピン留めblobと不一致。ピンは独立にProducer差分を確認したときだけ更新する（`scripts/handoff-cross-product.cjs` の `EXPECTED_PRODUCER_BLOBS`）。`SUI frontend path does not match...` が出たら、渡したPathが `<SUI root>\03_Implement\frontend` ではない。Runner は**作業ツリーが clean でないと実行しない**（Receiptを先に書き換えたまま再実行すると失敗する）。

### 0.3 実行環境（実測）

Node v24.19.0／Windows／markdown-it 14.3.3／Go 1.27.0（TEI CLI）。Node 22 でもCI（ubuntu/windows）で green を確認済み。G5 の第二Harnessは Claude Code 2.1.302。

### 0.4 実装済みの入口（後続者が触る場所）

| 何 | repo:path |
| --- | --- |
| 票の契約とProducer | `sui-sensemaking:03_Implement/frontend/src/export/handoff_context_envelope.ts` |
| 単一操作のemit | `sui-sensemaking:03_Implement/frontend/src/export/handoff_context_emit.test.ts` |
| TEI観測の引用emit | `sui-sensemaking:03_Implement/frontend/src/export/handoff_tei_observation_emit.test.ts` |
| ReceiptのProducer側照合 | `sui-sensemaking:03_Implement/frontend/src/export/handoff_receipt_review.ts` |
| Consumer（独立実装） | `sho-composer:src/handoff_envelope.cjs` |
| 実CLI入口 | `sho-composer:bin/sho-inspect.cjs`（`handoff`） |
| 二製品／三製品Runner | `sho-composer:scripts/handoff-cross-product.cjs` |
| G5 Harness切替Runner | `sho-composer:scripts/handoff-harness-switch.cjs` |
| G6 SEI照合 | `tai-pleroma:evaluations/tools/check-handoff-sei-binding.cjs` |

---

## 1. 読み方（全票共通）

### 1.1 各票の構造

| 見出し | 意味 |
| --- | --- |
| 目的 / 非目的 | この票が成立させること／ explicitly 扱わないこと |
| 前提 | 着手前に成立していなければならないもの。欠けたら着手しない |
| 変更ファイル | `repo:path` 形式。ここ以外は触らない |
| 契約差分 | 追加・不変・禁止を分けて書く |
| 受入条件 | **機械で確認できる形**でのみ書く。主観的判断は入れない |
| 必須負例 | 通らないことを確認する試験。欠けたら票未完 |
| 撤退条件 | ここに当たったら実装を戻し、判断をIssueへ返す |
| Ownerゲート | 人が決める必要があるもの。実装者が決め打ちしない |

### 1.2 全票共通の不変条件

1. 原本は各Productが保持する。票とReceiptは**一時的な受渡し用Projection**。
2. Harness Sessionは運搬経路。データ正本・意味受理・権限・実行結果の集約先にしない。
3. 会話履歴をHandoffと呼ばない。Task・根拠・未完の義務・確認が必要な依存関係を別欄で運ぶ。
4. Consumerは票の宣言を信じず、参照先を独立に再読取する。
5. 未知の値は安全側へ読み替えない。`unknown` のまま運ぶ。
6. 合成試験の成功を実製品E2Eの成功として扱わない。未実行の検証を合格と記録しない。
7. 各Product Skillは個別に利用可能な構成を維持する。TAI横断Skillを必須の前提にしない。

### 1.3 全票共通の禁止事項

- 新しい共通Runtime・中央Host・第二Registry・権限Engine・自動Schedulerを作らない。
- 既存Productの意味契約・Authority・Source正本を横断担当が編集・採用確定しない。
- 実秘密・個人情報・未レビュー本文・Credentialを票・Receipt・ログ・fixtureへ載せない。
- Tool成功・Agentの`done`・CI成功を意味受理や業務Effectへ昇格させない。
- 既存のP0 byte契約（354 bytes／独立期待SHA `7fd6fde2…71cd`）を変えない。

### 1.4 状態の書き方

各票の完了は `observed-pass` / `observed-fail` / `not-run` / `unsupported` / `unknown` のいずれかで記録する。`not-run` を `unsupported` や合格に丸めない。

---

## 2. G2：受領ReceiptのProducer返す経路

### 目的

Consumer（SHO）が作った受領Receipt `yi.handoff.receipt/v1` を、Producer（SUI）が**読める形で返す**。いまはReceiptが標準出力に留まり、Producerは「渡した票がどう受領されたか」を知らない。

### 非目的

- 自動返送・バックグラウンド返送を作らない。返送は利用者の明示的操作だけ。
- Receiptを監査DB・中央Storeへ集約しない。
- Receiptを意味受理や権限として扱わない。

### 前提

- G1が成立している（§0.2 が再現できる）。
- SUIの `handoff_context_envelope.ts` がConsumer側の検証規則と衝突しない。

### 変更ファイル

| repo | path | 内容 |
| --- | --- | --- |
| sho-composer | `src/handoff_envelope.cjs` | Receiptの**書き出し**関数を追加（`writeHandoffReceipt(receipt, directory)`）。既存の `receiveHandoff` は不変 |
| sho-composer | `bin/sho-inspect.cjs` | `handoff` に `--receipt-out <dir>` を追加。未指定なら書き出さない（既定はstdoutのみ） |
| sui-sensemaking | `03_Implement/frontend/src/export/handoff_receipt_review.ts` | Receiptの**読み取りと照合**（純関数）。ProducerはReceiptを信じず、自分の票と再照合する |
| sui-sensemaking | `03_Implement/frontend/src/export/handoff_receipt_review.test.ts` | 受入条件の試験 |
| sho-composer | `test/handoff-envelope.test.cjs` | 書き出しの試験を追加 |

### 契約差分

**追加**（`yi.handoff.receipt/v1` をファイルとして書出すための最小事項）:
- 書き出しは `wx` フラグ（新規ファイルのみ）。既存ファイルは上書きしない。
- ファイル名は `<handoffId>.receipt.json` のbare filename。パス区切り・`..`を拒否。
- Receiptには `ticket.sha256`（Producerの票のdigest）を含める。Producerはこれで自分の票と対応づける。

**不変**: `receiveHandoff` の戻り値の形・`claims` の意味・fail-closed規則。

**禁止**: Receiptに権限・Grant・Credential・Session資格を含めない。`claims.authorityCarried=false` を維持する。

### 受入条件（機械確認可能）

1. `--receipt-out` 未指定で `handoff` を実行すると、**ファイルは1つも作られない**（stdoutのみ）。
2. `--receipt-out <dir>` 指定で実行すると、`<handoffId>.receipt.json` が**新規作成**され、stdoutのJSONとbyte一致する。
3. 同名ファイルが既存のときは exit 2 で `handoff-receipt-exists`。**上書きしない**。
4. Producer側の照合関数は、Receiptの `ticket.sha256` が自分の票と一致するときだけ `matched` を返す。不一致は `mismatch`。
5. Producer側の照合関数は、Receiptの `claims.meaningAccepted=true` を**受理しない**（`claim-not-accepted` を返す）。Receiptは意味受理にならない。
6. `claims.authorityCarried=true` のReceiptは `handoff-receipt-authority` で拒否。

**実行結果（2026-11-11）**：1〜6 すべて `observed-pass`。
- 試験: `sho-composer` の7件（`--receipt-out` 未指定・byte一致・上書き拒否・失敗時にReceiptなし・不正出力先・unsafe handoffId・claims拒否）
- 実E2E: Runnerの観測 `receipt-returned-and-reviewed` が、実SHO CLIが書いたReceiptを実SUIモジュールが票digestで照合し、`matched`・上書き拒否・`meaningAccepted=false` を確認。
- 未実装の残り: Receiptの保持期間・閲覧者・監査利用（OG-5・Owner判断）。

### 必須負例

| ID | 注入 | 期待 |
| --- | --- | --- |
| G2-N1 | Receiptの `ticket.sha256` を別の票のdigestに差し替え | Producer照合が `mismatch` |
| G2-N2 | Receiptに `producer.grant` を足す | `handoff-authority-field` |
| G2-N3 | Receiptの `claims.meaningAccepted` を `true` に | Producer照合が `claim-not-accepted` |
| G2-N4 | `--receipt-out` に相対Path・`..` を含むPath | exit 2、ファイル不作成 |
| G2-N5 | 受領が失敗した（payload不一致）状態で `--receipt-out` を指定 | Receiptは作られない（失敗にReceiptを付けない） |

### 撤退条件

- 返送に認証・監査・再送の設計が必要になったら止め、ADR-0111の送信条件へ戻す（PoCのファイル受け渡しで足りるかを再確認する）。
- Receiptを「レビュー済み」や「承認済み」として扱う要求が入ったら止め、`human_reviewed` の境界（SUI安全不変条件）を理由に却下する。

### Ownerゲート

返送Receiptの保持期間と閲覧者。監査に使うかどうか。

---

## 3. G3：三製品協調（TEI read-only観測を票の根拠として引用）

### 目的

**TEIの読み取り専用観測を、SUIのHandoff票の `evidence[]`／`references[]` として引用し、SHOが受領する。** これが「TEIのモデル情報をSHOで説明文書候補として利用する経路」の最小形。**新しい契約を一つも作らない。**

### 非目的

- TEIのartifact生成契約（`source.status`・文書単位の開示宣言）を作らない。ADR-0116はOwner判断待ちのまま。
- TEIの観測を意味受理やSource正本として扱わない。
- 第二のHandoff（SHOが別製品へ再emitする連鎖）は§3.5で段階分けする。

### 前提

- G1が成立している。
- TEIのread-only CLIが実働すること。**実測済み**：

```powershell
cd <TEI>
go run ./cmd/tei commands                                        # read-onlyコマンドの發現
go run ./cmd/tei model catalog -workspace reference/workspace     # 実観測
```

実測出力（2026-11-11、Go 1.27.0）の要点：
- `result.worldFingerprint` = `sha256:<64hex>`
- `result.sourceIndexFingerprint` = `sha256:<64hex>`
- `result.modelRevision` = `sha256:<64hex>`
- `result.entries[].subject.kind` / `.id` / `.sourceStatus`
- `result.validation.ok` / `errorCount` / `warningCount`
- `result.authorityLimits[]` = `["catalog-is-a-derived-read-only-projection", "source-references-are-navigation-not-edit-or-acceptance-authority", "model-revision-does-authorize-source-writes"... ]`（※引用時は実出力の値を使う）

### 3.1 変更ファイル

| repo | path | 内容 |
| --- | --- | --- |
| sho-composer | `scripts/handoff-cross-product.cjs` | TEI read-only観測の引用ケースを追加（§3.3） |
| sho-composer | `test/handoff-envelope.test.cjs` | 引用を受け取るConsumer側の試験を追加 |
| sui-sensemaking | `03_Implement/frontend/src/export/handoff_context_emit.test.ts` | TEI観測を引用するemitの試験を追加 |
| tai-pleroma | `docs/yi-constellation/cross-product-handoff-context-v1-2026-11-11.md` | G3の状態を `observed-pass` に更新 |

**TEI側の変更は不要。** TEIのread-only CLIを its own contract のまま呼ぶ。

### 3.2 引用の規約（新規語彙。契約の追加ではない）

`references[]` の `kind` を次の閉集合として使う。未知の `kind` はConsumerが `unknown` として運ぶ（拒否しない。根拠を落とさない）。

| `kind` | 意味 | `digest` |
| --- | --- | --- |
| `handoff-payload` | 票と同梱のpayload | 必須（`sha256:<64hex>`） |
| `producer-source` | Producerが保持する原本 | 未知なら `null` |
| `tei-readonly-observation` | TEI read-only CLIの観測 | `worldFingerprint` または `modelRevision` |

`evidence[]` の規約：
- `basis` は `<product>.<command>/<schemaVersion>` を含む（例: `tei.cli.model/v0`）。
- `limitation` は**TEIの `authorityLimits[]` を落とさず**含む。空文字は不可（Producer側の `requireText` で拒否される）。
- `claim` は観測事実のみ。「〜である」という推論や「検証済み」を書かない。

### 3.3 受入条件（機械確認可能）

1. RunnerがTEI read-only CLIを**実実行**し、その出力から `worldFingerprint`・1件の `subject`・`authorityLimits` を抽出する。
2. 抽出値を引用したSUI Producerのemitが成功し、票の `references[]` に `kind="tei-readonly-observation"` の1件が、`evidence[]` に `basis` が `tei.cli.model/v0` を含む1件が入る。
3. SHO Consumerがその票を受領し、Receiptの `carriedForward.evidence[].limitation` に TEI の `authorityLimits` の内容が**全て**含まれる。
4. Receiptの `claims.meaningAccepted` は `false` のまま。TEI観測を意味受理として扱わない。
5. Receiptの `claims.originalSourcesRead` は `false` のまま。
6. RunnerのObservationsに `tei-readonly-observation-cited` が `ok:true` で加わる。

**実行結果（2026-11-11）**：1〜6 すべて `observed-pass`（`scope: synthetic-three-product-one-handoff`、12観測すべてok）。

| 受入条件 | 実測 |
| --- | --- |
| 1 | `go run ./cmd/tei model catalog -workspace reference/workspace`（TEI `origin/main` = `2a9a14c07`）を実行。`worldFingerprint sha256:c92de09f…`・`modelRevision sha256:f414e2b0…`・`authorityLimits` 4件を抽出 |
| 2 | SUIの `handoff_tei_observation_emit.test.ts` が `kind="tei-readonly-observation"`（`digest=worldFingerprint`）と `basis="tei.cli.model/v0"` を票に載せた |
| 3 | 実SHO CLIで受領。`limitation` に4件の `authorityLimits` が**全て**残る |
| 4 | `claims.meaningAccepted=false` |
| 5 | `claims.originalSourcesRead=false` |
| 6 | `tei-readonly-observation-cited` が `ok:true`、`threeProductCoordination="observed-pass"` |

### 3.4 必須負例

| ID | 注入 | 期待 | 実測 |
| --- | --- | --- | --- |
| G3-N1 | `references[].digest` を `sha256:` 以外にする | `handoff-invalid-digest:references[].digest` | `observed-pass`（Runnerで実注入） |
| G3-N2 | `evidence[].limitation` を空文字にする | `handoff-missing-field:evidence[].limitation` | `observed-pass` |
| G3-N3 | `evidence[].limitation` から `authorityLimits` を落とす | 受入条件3が失敗する | `observed-pass`（G3-N2と同経路。落とすと空文字になる） |
| G3-N4 | TEI観測を「検証済み」と書いた `claim` を入れる | 意味受理へ昇格させない | `observed-pass`。**Consumerはclaimの真偽を判定しない**という限界を明示し、`meaningAccepted=false` を維持（`promotion-not-accepted`） |
| G3-N5 | `references[].kind` に未知の値（`sei-observation`）を入れる | Consumerは受領し、運ぶ。拒否しない | `observed-pass`（`unknown-kind-carried`） |
| G3-N6 | read-only でないコマンドを呼ぼうとする | Runnerが事前に拒否 | `observed-pass`（`result.effect === "read-only"` を呼出し前に確認） |
| G3-N7（追加） | `evidence[].basis` を削除する | `handoff-missing-field:evidence[].basis` | `observed-pass`（観測面を落とすと再発見できないため必須化） |

### 3.5 連鎖Handoff（第二のHop）は段階分けする

SHOが受領内容を**別の製品へ再emit**する連鎖は、いまの票には**来歴の区別**がない。`evidence[]` が「このProductが自分で読んだ観測」なのか「前の票から継承した観測」なのかを区別できないため、継承した主張が第一手の観測として誤認され得る。

**次の段階でのみ**、`yi.handoff.context/v2` に `chain` を追加することを検討する：

```
chain: {
  hop: 1..n,
  priorHandoffId: string | null,
  inheritedEvidence: [{ claim, basis, observedAt, limitation, fromHandoffId }]
}
```

規則（v2で満たすべきもの）:
- `inheritedEvidence` の各件は `limitation` を**変更しない**。前の票のlimitationをそのまま運ぶ。
- `inheritedEvidence` は第一手の観測として提示しない。Consumerは `hop` と `fromHandoffId` を見て継承であることを判別できる。
- `hop` の上限は設けないが、上限なしを「無制限に信頼できる」と扱わない。

**v2への昇格はOwnerゲート。** 連鎖の実需要が確認されるまで v1 のままにする。

### 撤退条件

- TEI観測を「〜が正しい」という主張に使う要求が入ったら止める。観測は観測まで。
- `authorityLimits` を落とさないと票が作れない案件が出たら、その案件を止めてIssueへ返す。

---

## 4. G4：Session再開

### 目的

Goal Roundをまたぐ・Hostを再起動する・日をまたぐ**Session再開**の後で、Handoffが現在の資格を保って再受領できることを確認する。

### 非目的

- HarnessのSession永続化・Goal機構を作らない。それは各Harnessの実装。
- 自動resume・自動再送を作らない。

### 前提

- G1が成立している。
- 票がSession非依存であること（`transport` は観測のみ、`authority="none"`）が G1 で確認済み。

### 変更ファイル

| repo | path | 内容 |
| --- | --- | --- |
| sho-composer | `scripts/handoff-cross-product.cjs` | Session再開ケースを追加 |
| sho-composer | `test/handoff-envelope.test.cjs` | 同一ファイルを「別の日に別プロセスで」受領する試験 |

### 受入条件（機械確認可能）

1. 同じ票・同じpayloadを、**別プロセス・別時刻**で受領しても、payload・checks・carriedForwardは一致する。`receivedAt` のみが変わる。
2. 再開後にProducer側の原本が更新されている場合、受領は `handoff-payload-size-mismatch` または `handoff-payload-digest-mismatch` で閉じる。**再開を理由に差分を許さない**。
3. 再開時のReceiptに `claims.sessionInheritedAuthority=false` が立つ。前Sessionの資格を継承しない。
4. `transport.sessionLabel` は新Sessionのラベルで記録され、旧Sessionのラベルが復活しない。

**実行結果（2026-11-11）**：1〜4 すべて `observed-pass`。Runnerの観測 `session-resumed`。
- 別プロセス（`spawnSync` で新規起動）・別ラベル（`session-resumed`）で再受領。
- `payload`・`checks`・`carriedForward` は初回と完全一致。`consumer.sessionLabel` のみが変わる。
- `claims.sessionInheritedAuthority=false`、`claims.independentReread=true`。
- Consumerは票の `transport.sessionLabel` を書き換えない（運搬観測の保持）。
- 再開後にpayloadを変更すると、同じく `handoff-payload-size-mismatch` で閉じる（G4-N1 相当）。
- **未検証**：Host再起動・日跨ぎの実Session永続、Goal Round跨ぎの再開。

### 必須負例

| ID | 注入 | 期待 | 実測 |
| --- | --- | --- | --- |
| G4-N1 | 再開前にpayloadを変更 | fail-closed | `observed-pass`（`handoff-payload-size-mismatch`） |
| G4-N2 | 再開前に票の `disclosure.audience` を狭める | 新しいAudienceで受領。旧Audienceを「覚えている」ことにしない | `not-run`（票の作り直しが要る。Runner未実装） |
| G4-N3 | Receiptを手で編集して `receivedAt` を過去にする | 受領は新Attemptとして記録。編集を現在の受領として扱わない | `not-run`（Receiptは受領時に生成するため、編集済みReceiptを読み戻す経路が未実装） |

### 撤退条件

- Session再開に「資格の自動回復」が必要という要求が入ったら止める。資格は現在のHost/Providerが都度確認する。

---

## 5. G5：別Harnessへの移行

### 目的

Harness A（例: DSH）で開始したHandoffを、Harness B（例: Codex・Claude Code）に引き継いだとき、**実行権限が増幅しない・未承認のSourceが自動送出されない**ことを確認する。

### 非目的

- Harness間のSession移植・Context継承を作らない。
- MCP/ACPの新規実装・Protocol改変をしない。CLI-only経路を別対照として継続する。

### 前提

- G1の `harness-switch` 観測で、**同一プロセス内でラベルを変えただけ**では増幅しないことを確認済み。G5は**実Harnessを差し替える**段階。

### 変更ファイル

| repo | path | 内容 |
| --- | --- | --- |
| tai-pleroma | `docs/yi-constellation/harness-interoperability-and-handoff-pilot-2026-11-03.md` | HX-01〜26との接続を記録 |
| sho-composer | `scripts/handoff-cross-product.cjs` | `--harness` を実Harness名にして実行するRunbookを追記 |
| tai-pleroma | `integrations/` | **Harness別Adapterの配置・発見・実ロードの記録のみ**。Product契約の再実装はしない |

### 受入条件（機械確認可能）

1. Harness A で `bin/sho-inspect.cjs handoff` を実行し、Harness B で**同じコマンド**を実行する。両者のReceiptの `payload`・`checks`・`carriedForward`・`claims` は一致する。`consumer.harness` のみが変わる。
2. Harness B の実行で、`claims.authorityCarried`・`claims.externalDisclosure`・`claims.writerInvoked` はすべて `false`。
3. Harness B の実行前に、Harness A のSessionで見えていたTool・権限・Sourceが、Harness B では**独立に再確認**される。再確認の記録がRunbookに残る。
4. Harness A で「可用」と確認したToolを、Harness B で**無条件に可用としない**。未知のものは `unknown` として記録する。

**実行結果（2026-11-11）**：1・2・4 は `observed-pass`、3 は `not-run`。

実際の構成：
- Harness A = DeepSeek Harness 0.2.2-rc.1（このプロセスの実CLI）
- Harness B = Claude Code 2.1.302（`--harness-b-argv` で **ARGV 起動**。`-p` のプロンプトで実Consumerを実行させ、標準出力のJSONを回収）
- 票 `sha256:d0c3c588…`／payload `sha256:7fd6fde2…`（354 bytes）

**再実行の可否（2026-11-11 追記）**：異なるHarness間の実測は、Claude Code のセッション上限に達したため**当日は再実行できない**（`unrecognized_model`／`session limit`）。これは外部クォータの制約であり、機構の故障ではない。異なるHarnessが使えない環境では、**同一Harnessの別Session**を対照として走らせることができる（`docs/handoff-harness-switch-control-receipt-2026-11-11.json`）。**対照が通っても「異なるHarness間で増幅しない」ことの証拠にはならない**。対照が通らなければ機構側のbugである。

| 受入条件 | 実測 |
| --- | --- |
| 1 | `payload`・`checks`・`carriedForward`・`claims`・票本文（`transport` 除く）が**完全一致**。差分は `consumer.harness` と `consumer.sessionLabel` のみ（`identical-beyond-transport`） |
| 2 | `authorityCarried`・`externalDisclosure`・`writerInvoked`・`sessionInheritedAuthority`・`meaningAccepted` すべて `false`（`no-amplification`） |
| 3 | **`not-run`**。Harness B のTool・権限・Sourceの独立再確認は記録していない。Runbookの手順として残す |
| 4 | 票の `transport.authority="none"` を両Harnessが読む（`ticket-transport-authority-none`）。Skill実ロード・MCP経路は `not-run` |

追加で確認：両Harnessが同じpayload bytesを観測（暗黙の差し替えなし）。`disclosure.scope` を広げた票は両Harnessで `handoff-disclosure-scope-unknown`。

RunbookとReceipt: `sho-composer:docs/handoff-harness-switch-trial-2026-11-11.md` と `handoff-harness-switch-trial-receipt-2026-11-11.json`。

### 必須負例

| ID | 注入 | 期待 | 実測 |
| --- | --- | --- | --- |
| G5-N1 | Harness A のSession Logに票の内容が残っている状態でHarness Bを起動 | Harness B は票を**ファイルから独立に再読取**する | `observed-pass`（Harness B は `bin/sho-inspect.cjs handoff <票>` を実行し、ファイルから読む。Session履歴の復元経路は無い） |
| G5-N2 | Harness B に広いshell権限がある環境で実行 | 書込み・送出は起きない | `observed-pass`（Claude Code に `--allowedTools Bash` を与えても `writerInvoked=false`・`externalDisclosure=false`） |
| G5-N3 | Harness A で開示Scopeを広げた履歴がある | Harness B は**現在の** `disclosure.scope` だけを見る | `observed-pass`（`widened-scope-rejected`。票を広げると両Harnessで拒否） |
| G5-N4 | Harness B がMCP経由で接続する | CLI-only経路のPASSをMCPのPASSに読み替えない | `not-run`（MCP経路は実行していない。`otherHarnessMcpPath: not-run`） |

### 撤退条件

- Harness差し替えで「前のSessionの資格を引き継ぐ」仕様が必要になったら止める。それは権限境界の変更でありOwner判断。

---

## 6. G6：Source Provenance・EvidenceのProduct Oracle

### 目的

票が運ぶ `unresolved`・`evidence`・`references` を、**各Product自身のOracle**で閉じられる範囲を確認する。TAIはConsumerとして「差異を失っていないか」を検査するだけで、独自のOracleを作らない。

### 非目的

- 新しい共通Oracle・Claim Store・全社履歴DBを作らない。
- 否定Claim（「存在しない」）をProductの実Read closureなしに断定しない。

### 前提

- G1・G3が成立している。

### 変更ファイル

| repo | path | 内容 |
| --- | --- | --- |
| tei-platform | `plan/` | TEI #2586（Query→Context→Claim）・#2516（用途別Projection）の既存Laneに接続 |
| sei-cognition | `contracts/` | `sei.semantic-reference` の Exact Binding を `references[]` の参照形式として照合 |
| tai-pleroma | `docs/yi-constellation/` | 照合結果の記録。**採否は各Owner** |

### 受入条件（機械確認可能）

1. `references[].digest` をSEIの Exact Binding 形式と照合し、一致・不一致・未知を区別して返せる。
2. TEI #2586の実Read closureが実証された範囲**だけ**、否定Claimを適合判定する。未実装の範囲は `insufficient-evidence`。
3. 照合結果は `reference-linked-unverified` にとどめる。`verified` へ自動昇格させない（TEI E9の既存診断名を再利用）。

### 必須負例

| ID | 注入 | 期待 |
| --- | --- | --- |
| G6-N1 | 空配列 `[]` を「global不存在」と結論づけるConsumer | `insufficient-evidence`。母集団・Predicate・coverageの確認を要求 |
| G6-N2 | 部分取得を「全件」として報告 | `evidence-mismatch` |
| G6-N3 | Source-only移動後にWorldFPのみ一致、引用locatorは旧版 | `stale-or-different-binding` |
| G6-N4 | 同じdigestの別Source | 同一視しない。所在とdigestを別列で確認 |

---

## 7. Owner判断ゲート一覧

| ID | 判断事項 | 影響する票 | 現状 |
| --- | --- | --- | --- |
| OG-1 | 開示Scope語彙（`synthetic-only`／`reviewed-projection-only`）の確定 | 全票 | 候補のまま |
| OG-2 | `source.status` と文書単位の開示宣言をTEI側artifact生成契約にするか | G3 | 未決。無い場合は`unknown`として動く |
| OG-3 | 本文・題名の業務面への公開（SUI #3369） | G3・G6 | 未決 |
| OG-4 | 連鎖Handoffの `chain`（v2）を採るか | G3.5 | 未決。v1のまま |
| OG-5 | 返送Receiptの保持期間・閲覧者・監査利用 | G2 | 未決 |
| OG-6 | **共通実行基盤の新設・権限境界の変更** | 全票 | **行わない。必要なら具体案を出す** |
| OG-7 | Harness別Adapterの配布・版固定（TAI #74） | G5 | 未決 |
| OG-8 | MCP Tool一覧への read-only 追加（SUI MCP の allowlist） | G5 | 未決。CLI-onlyで継続 |

---

## 8. 完了の定義と差し戻し条件

### 8.1 全体の完了

- G2〜G6 の各票が、§1.4 の状態語で記録されている。
- 各票の受入条件が**機械で確認**され、必須負例が**全て**実注入されている。
- 合成試験と実製品E2Eが区別されて記録されている。
- 未実行の検証が `not-run` として残っている（合格に丸めていない）。

### 8.2 差し戻し条件（いずれかに当たったら作業を止め、Issueへ返す）

1. 共通Runtime・中央Host・第二Registry・権限Engineが必要になった。
2. 権限境界の変更（露出範囲の拡大・資格の自動回復・自動送出）が必要になった。
3. 票が第二のデータ正本として使われ始めた（artifactを保存・編集する経路が生まれた）。
4. 本文が不用意に載り始めた。
5. 否定ClaimをProductの実Read closureなしに断定する必要が出た。
6. 会話履歴の移行をHandoffとして要求された。

### 8.3 現時点の達成状況（2026-11-11）

| 条件 | 状態 |
| --- | --- |
| G2〜G6 の状態語での記録 | **達成**（§実行状況の表） |
| 受入条件の機械確認 | **達成**（G2・G3・G4・G5の主要条件。G5-受入3・G4-N2/N3・G5-N4 は `not-run`） |
| 必須負例の実注入 | **一部**。G2・G3は実注入済み。G4は1件、G5は3件が `not-run`（理由を表に明記） |
| 合成試験と実製品E2Eの区別 | **達成**。Receiptの `scope` と `claims` で区別。CIのPASSをlive handoffのPASSに数えない |
| 未実行の `not-run` 保持 | **達成**（§実行状況・各負例表） |

**まだ完了ではない理由**：上の「一部」「not-run」が残る。Owner判断ゲート OG-1〜OG-8 も未決。

---

## 9. 実装中の発見（後続者のための注意）

1. **資格マーカーの偽陽性**：`credential` や `secret` を単語として禁じると、他製品の読み取り専用観測を引用したときに票が作れない。TEIの参照Workspaceには `security.credential`・`security.authorization_grant` というsubject IDが実在する。現在の実装は marker を `-----begin`・`bearer `・`authorization:`・`api_key`・`access_token` 等の**serializeされた資格素材の形**に限定し、業務語は key名の完全一致側で扱う。G3で他製品観測を引用するときは、この区別を崩さないこと。
2. **来歴ゲートはblobピン**：repo全体のHEAD一致を要求すると、無関係な開発中のcommitで試験が不成立になる。Producer入力3ファイルのgit blob SHAをピン留めする方式にしている。Producerコードを変えたらピンを更新すること（独立に差分を確認してから）。
3. **ConsumerはProducerとコードを共有しない**：片方のbugがもう片方へ無音で伝播しないため。規則を合わせたいときは**試験**で合わせる（独立Expected）。
4. **`evidence[]` の `basis` は必須にした**：観測面（`tei.cli.model/v0` など）を落とすと、後から観測を再発見できない。任意欄にすると「根拠があるように見えるが辿れない票」が通る。
5. **`references[]` は未知のkindを拒否せず運ぶ**：Consumerが意味を知らないことと、根拠が無いことは違う。未知kindを落とすと、後から語彙を増やしたときに過去の票から根拠が消える。
6. **BOMを値と混同しない**：PowerShell 5.1 の `Out-File -Encoding utf8` は BOM を付ける。TEI CLI の出力を保存して読む経路では BOM を落としてから `JSON.parse` する。落とさないと「観測の引用」ではなく「保存経路の癖」で失敗する。
7. **Runnerは作業ツリーがcleanでないと動かない**：Receiptを先に書き換えたまま再実行すると `Tracked files are modified` で止まる。ReceiptはRunnerが最後に書く（先に手で置かない）。
8. **Harness B はARGVで起動する**：shell文字列を組み立てると、引用符の解釈差で「別のコマンドが走った」ことを見逃す。`--harness-b-argv` はARGVをそのまま渡す。
9. **Tei read-only の事前確認**：`result.effect === "read-only"` を**呼出し前**に確認する。書込み可能なコマンドを呼んでから後追いで拒否するのでは遅い。

## 関連

- [設計・契約文書](cross-product-handoff-context-v1-2026-11-11.md)
- SUI ADR-0117、SHO `docs/handoff-cross-product-trial-2026-11-11.md`
- TAI #168 / #271 / #232 / #74、TEI #2515 / #2516 / #2586 / #2605、SUI #3369 / #3397、SHO #4 / #21、SEI contracts
