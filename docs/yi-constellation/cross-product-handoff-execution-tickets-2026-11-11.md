# 製品横断Handoff：後続実行票 G2〜G6（具体化・実行結果）

2026-11-11。[設計・契約文書](cross-product-handoff-context-v1-2026-11-11.md) の G1（二製品Handoff）は実証済み。本書は **G2〜G6 を後続の実装者が迷わず最後まで実行できる形**に具体化する。

**本書が守る制約**：共通実行基盤の新設、中央Host、第二Registry、権限Engine、権限境界の変更は行わない。それらが必要とされる段になった場合は、§7 のOwner判断ゲートへ戻す。

## 実行状況（2026-11-11 更新）

| 票 | 状態 | 実測 | 残り（NOT RUN） |
| --- | --- | --- | --- |
| G2 | **observed-pass** | Receipt返送＋Producer側照合を実製品E2Eで確認（`receipt-returned-and-reviewed`） | Receiptの保持期間・監査利用（OG-5） |
| G3 | **observed-pass** | 実TEI read-only CLI観測を票へ引用し、実SHO CLIが受領（3製品・負例5件） | 第二のHop（`chain`v2）、`source.status`契約（OG-2） |
| G4 | **observed-pass（新プロセスでの受領に限定）** | 別プロセス・別Sessionラベルでの再受領（歴史観測ID=`session-resumed`）、Audience拡大票の再読取もSHO #42で回帰 | 実Harness Session永続、現在Host Recipient Grant・Audience拡大拒否、縮小試験 |
| G5 | **observed-pass（Receipt一致の限定範囲）** | A=ローカルNodeからSHO Consumer CLIを直接実行（`deepseek-harness`はラベル）、B=外部ARGV指定でClaude Codeを起動しSHO CLIのJSON Receiptを回収（7観測）。Aの実DSH Agent経由起動はこのRunner/Receipt単独では未証明 | 両Harnessの実Agent経由Invoke・Skill実ロード・MCP経路・現在Host Grant/外部egress |
| G6 | **observed-pass（限定）** | 票のreferencesをSEI exact_binding形と照合（`reference-linked-unverified`に留める・self-test 8件） | 受入2（TEI #2586 Claim closure）、負例N1〜N3（正式に閉じた）、別Source検出 |

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

# 4. G5 ローカルCLI(A)と外部Harness CLI(B)の比較（票を先に用意してから）
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

SHOが受領内容を**別の製品へ再emit**する連鎖は、いまの票には`chain`欄がない。`evidence[]` が「このProductが自分で読んだ観測」なのか「前の票から継承した観測」なのかを欄としては区別できない。

**OG-4（2026-11-11 代行決定）により `yi.handoff.context/v2` と `chain` は作らない。** 具体スキーマ（`hop`・`priorHandoffId`・`inheritedEvidence`）の案は、決定に反する将来経路を文書が提示することになるため**本書に載せない**。来歴は v1 の範囲で次で運ぶ。

| 来歴を運ぶ方法（v1） | 内容 |
| --- | --- |
| 新しい票として発行 | 連鎖の各段は独立の `handoffId` を持つ票を作る。前の票を「拡張」しない |
| `evidence[].basis` に継承元を書く | `basis` は観測面（例: `tei.cli.model/v0`）。継承した観測なら `from:<priorHandoffId>` を basis に含める |
| `evidence[].limitation` に継承であることを書く | 前の票の `limitation` を**変更せず**そのまま運び、「これは `<priorHandoffId>` から継承した観測である」と付ける |
| `references[].note` に継承元の locator を書く | 継承元の参照を `note` に含め、後から辿れるようにする |

**判別の仕方**：Consumerは `basis` に `from:<handoffId>` が含まれるかを見て、第一手の観測か継承かを判別できる。新しい欄は増えない。

**変更する条件**：実 Owner が連鎖の実需要を確認し、v1 の方法では来歴を運べないことを実測した場合。その場合は**新規の判断**として v2 を設計する（本書の決定を自動的に覆さない）。

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

**実行結果（2026-11-11）**：1〜4は**別プロセスのSHO CLI受領として**限定`observed-pass`。Runnerの歴史観測ID `session-resumed`は実Harness Sessionの継続・復元を意味しない。
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
| G4-N2 | 既存 `['sho-composer']` を `['sho-composer','other-consumer']` へ**拡大**した票を別プロセスで受領 | **現在票に記載されたAudienceを再読取**する。追加RecipientへのHost許可・送出拒否は別結果 | [SHO merged #42](https://github.com/hat47x/sho-composer/pull/42)で実Consumerのreadbackと非継承をNode回帰し、Ubuntu/Windows Handoff CI成功。`g4-n2-current-audience`の`hostRecipientAuthorization`／`audienceExpansionDenied`は**`not-run`**。外部Harnessによる追加送出・Host拒否は未実証 |
| G4-N2R | 再開前にAudienceを本当に**縮小**する | 現在票を再読取し、旧Recipientを許可済みとして復元しない | **`not-run`**（元のG4-N2の意図した縮小反例は新しい拡大試験では実証されない） |
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

**実行結果（2026-11-11、2026-11-12資格監査）**：1はAローカル/B外部ARGVのConsumer Receipt一致、2はReceiptの宣言値がすべて`false`、4は票内`transport.authority=none`と実Tool可用性の**非継承（宣言面のみ）**として限定`observed-pass`。3のB側実Tool/権限/Source現在再確認は`not-run`。

実際の構成：
- Harness A = **このRunnerが直接起動したローカルNode/SHO Consumer CLI**（`--harness-a deepseek-harness`はReceipt用ラベル。外側の実DSH Agent起動・Sessionは別の一次ログがない限り未資格）
- Harness B = Claude Code 2.1.302（`--harness-b-argv` で **ARGV 起動**。`-p` のプロンプトで実Consumerを実行させ、標準出力のJSONを回収）
- 票 `sha256:d0c3c588…`／payload `sha256:7fd6fde2…`（354 bytes）

**再実行の可否（2026-11-11 追記）**：異なるHarness間の実測は、Claude Code のセッション上限に達したため**当日は再実行できない**（`unrecognized_model`／`session limit`）。これは外部クォータの制約であり、機構の故障ではない。異なるHarnessが使えない環境では、**異なるHarness/Session風のラベルを付けて同じSHO Consumer受領を比較する対照**を実行できる（`docs/handoff-harness-switch-control-receipt-2026-11-11.json`）。ただしそのReceiptの`sessionLabels.a/b`はともに`g5-switch`であり、**二つの実DSH SessionのID・再開を示さない**。対照が通っても「異なるHarness間で増幅しない」ことや「別Sessionを実装した」ことの証拠にはならない。対照が通らなければ機構側のbugである。

| 受入条件 | 実測 |
| --- | --- |
| 1 | `payload`・`checks`・`carriedForward`・`claims`・票本文（`transport` 除く）が**完全一致**。差分は `consumer.harness` と `consumer.sessionLabel` のみ（`identical-beyond-transport`） |
| 2 | `authorityCarried`・`externalDisclosure`・`writerInvoked`・`sessionInheritedAuthority`・`meaningAccepted` すべて `false`（`no-amplification`） |
| 3 | **`not-run`**。Harness B のTool・権限・Sourceの独立再確認は記録していない。Runbookの手順として残す |
| 4 | 票の `transport.authority="none"` を両Harnessが読む（`ticket-transport-authority-none`）。Skill実ロード・MCP経路は `not-run` |

追加で確認：A/Bの実SHO Consumerが同じpayload bytesを観測（暗黙の差し替えなし）。`disclosure.scope` を広げた票への拒否は**A側ローカルCLIでのみ実注入**されており、B側Claude Code経由は未注入。

RunbookとReceipt: `sho-composer:docs/handoff-harness-switch-trial-2026-11-11.md` と `handoff-harness-switch-trial-receipt-2026-11-11.json`。

### 2026-11-12 Source/Receipt照合：G5観測の資格上限と次の実行条件

SHO [`scripts/handoff-harness-switch.cjs`](https://github.com/hat47x/sho-composer/blob/main/scripts/handoff-harness-switch.cjs)の現mainは、**Aで`spawnSync(process.execPath, [...sho-inspect, '--harness', harnessA])`、Bで`spawnSync(program, argv)`**を実行する。Aの`--harness-a`は**記録ラベル**でありDSH CLIの起動コマンドではない。Bは2026-11-11の一次記録でClaude Codeを外部ARGV起動したとされるが、受領JSON内の`consumer.harness`文字列だけではBのAgent版・外部Provider送信・Skill Loaderを検証できない。外側DSH SessionからNode Runnerを起動した別の一次ログが存在するなら、その観測を別列で連結し、**現RunnerのA側がDSH経由だったと推定で補完しない**。

| 項目 | 今回のコード/Receiptで確認できる範囲 | まだ必要な独立観測 |
| --- | --- | --- |
| G5-A local | 実SHO CLIのexit 0とReceipt readback、`--harness-a`文字列の記録 | **実DSH Agent→Tool→このRunner**のSession/Invocation/実引数・Tool全応答、実OS Read/egress |
| G5-B external | B指定実プログラムからJSON Receiptを得て、Aのpayload/checks/claimsと比較 | Bの現Grant・Tool/Skill実LoadとProvider全送出、後着/部分結果・CLI外副作用 |
| G5 N3 expanded scope | 現Runnerで`widenedA = runConsumer(widenedPath, harnessA)`を一度実行 | **Bにも変更票を入力して実拒否させる**。現状の`widened-scope-rejected`はAのPASSに限る |
| `no-amplification`・`noUnapprovedSourceAutoSend` | 両Consumer Receipt内の`claims.*===false`と`transport.authority='none'`、JSON比較 | Host Grant/OS効果/Network egress/全Sinkの非発生は**NOT RUN**。Receiptの宣言だけで外部漏えい・副作用ゼロを証明しない |
| Harness/Activity/Skill | G5は同じ票・payloadの再受領 | 同一Live Session継続、H3 Skill実Load、Activity再開・対象のSource/Scope再資格はそれぞれ別試験（TAI #168/#271/#488、QH §10） |

**扱い**：既存7観測の履歴ReceiptやB側の実CLI起動を取り消さない。G5の`observed-pass`は**ローカルCLI Aと外部ARGV BにおけるConsumer結果一致**に限って維持する。既存Runner/Schema/歴史Receiptをこの文書で改変せず、次の独立G5-A/B Trialで本当に二つの外部Harnessを明示的に起動し、それぞれの入口とCurrent Grant/Tool/Skill/外部送出を実観測したときに限って、主張を上げる。TAI #168の初回H2/H3（適格0/4）のBlockingは変更しない。

### 2026-11-12 Machine ReceiptのClaim Ceilingを実Runnerへ固定する（後続実験の資格）

[SHO G5実Runner修正 merged PR #45](https://github.com/hat47x/sho-composer/pull/45)は、[TAI #635](https://github.com/hat47x/tai-pleroma/pull/635)／[SHO #43](https://github.com/hat47x/sho-composer/pull/43)の**記述上の訂正を実際のMachine Receiptへ反映してmainに統合済み**。2026-11-11の固定Receiptは履歴のまま変更しない。現行の受領一致の範囲を超えて`noAuthorityAmplification=true`／`noUnapprovedSourceAutoSend=true`を新しいReceiptへ出さないようにする。

| Receiptの軸 | 新Runnerが表す範囲 | まだ実証していないこと |
| --- | --- | --- |
| `executionPaths` | A=`local-node-direct-consumer`、B=`external-argv-program`を明記。表示ラベルをAgent証拠にしない | Aの実DSH Session Tool呼出、Bの現在Tool Profile/Grant |
| `claims.receiptDeclaresAuthorityAndWriterFalse` | **両SHO Consumerの宣言値**がfalseであることだけをtrueにできる | 実Host Authority、OS write、Provider/Network送出の0 |
| `claims.noAuthorityAmplification`／`noUnapprovedSourceAutoSend` | `not-proven`、外側実送出は`not-run` | 実OS/Network Egress全Sink・業務Effect |
| `claims.widenedScopeRejected`／`externalBWidenedScopeRejected` | `local-a-only`／`not-run`。旧観測ID`widened-scope-rejected`は新Receiptでは`local-a-widened-scope-rejected` | B側Agent経由で同じ改変票を投入して拒否させること |
| `claims.realProductConsumerInBothHarnesses` | `not-proven`。実Consumer 2経路のJSON一致とは別 | A/B二つの実Agent Sessionが対等に同じTaskを実行 |

**反例の再利用**：G5-N2/N3、[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488) X04/X05/X06、同実行票§10のQH（I/R/P/T/C/H）を用い、**旧`observations[].id`と新Runnerの同名風IDを同じ資格へ自動集計しない**。新回帰`test/handoff-harness-switch-claims.test.cjs`は**SHO main統合済み**で、Ubuntu/Windows双方のHandoff CIで実行・成功。ただし検証したのは**新Receiptの宣言範囲とCLI入力拒否**であり、実二Agent・Host/OS/egressをこのCIで試したわけではない。これはTest-only Receiptの厳格化であり、`yi.handoff.context/v1`、正式Authority/Skill Loader、全製品共通のEvidence Registryや第二Verifierは変更しない。TAI #168のH2/H3比較適格0/4・G0→G2を優先し、二Agentの実ログ/外部送信/B不正票は独立した**NOT RUN**の次段階。

### 2026-11-12 実CLI Runner出力とProduct Skill宣言の独立回帰（SHO main #46）

[SHO merged PR #46](https://github.com/hat47x/sho-composer/pull/46)は、前節の**純粋なClaim Ceiling関数のテスト**に加え、実`scripts/handoff-harness-switch.cjs`を起動するNode回帰を追加。合成・公開可能な`yi.handoff.context/v1`票を使い、A=ローカルNode→実SHO Consumer、B=別Nodeを`--harness-b-argv`で起動→同じ実SHO Consumerの**二経路を明示的に通す**。最終Machine Receiptの7観測ID・payload byteLength/SHA・`scope/claim/executionPaths`・`not-proven/not-run/local-a-only`を独立Expectedと照合し、Ubuntu/Windows Handoff CIで成功。これは**実外部Harness二Agentや同一Live Sessionの実証ではない**。当該Bは外部ARGVのNodeプロセスであり、DSH/Claude等のAgent Loader・Tool Permission/OS・Provider送出を実行していない。

さらに、SHO Consumerで未知の`producer.productSkill`を`ticket.producerSkill`へ表示する仕様について、**Productが宣言した値を落とさず運ぶことと、Harnessが本当にSkillをロードしたことを区別**した。Skill宣言あり／なしで`receipt.claims`が変わらず、`authorityCarried`・`writerInvoked`がfalseである合成回帰を追加した。元Sourceや現在Permission、実Tool Replyの証明はProducerのmetadata欄から復元しない。旧2026-11-11固定Receiptは変更しない。

**資格の段階**：値を返す関数の単体試験→実CLI/Consumer同士の一往復（今回到達）→実AgentのLoader/Tool呼出と完全Reply→実OS/Host Grant/全Sink/業務Effect（後二者NOT RUN）を異なる結果列とする。既存QHのI/R/P/T/C/Hと[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)/[#488](https://github.com/hat47x/tai-pleroma/issues/488)を利用し、新しい共通Runner・第二Evidence Store/Verifier・Handoff v2を導入しない。初回H2/H3比較適格0/4を変更しない。

### 2026-11-12 B側Receiptの再利用反例を実Runnerで確認（SHO merged #47）

[SHO main PR #47](https://github.com/hat47x/sho-composer/pull/47)で、G5-Bが**現在のAttemptで実Consumerを起動しなくても**、過去に作ったBラベル付き受領JSONを外部ARGVから再出力するだけで、現Runnerの内容一致を満たす反例を追加した。事前Receiptの作成は実Consumer、G5のB argvは**保存済みJSONの出力のみ**。これは実Harness二Agent試験でなく、実Node/CLIによる**Runnerの観測限界の回帰**。Ubuntu/WindowsのSHO Handoff CIで正常経路と当該再利用負例がともに成功した。

| 判定 | 実Runner出力の修正範囲 | 証明できないこと |
| --- | --- | --- |
| `scope/claim` | `synthetic-local-consumer-external-json-receipt`／`local-consumer-vs-external-json-consistency-only` | Bが実Consumerを呼んだこと |
| `observations[].id` | `external-b-receipt-json-observed`・`receipt-declared-bytes-match`。返却JSONの一致だけを観測 | Bが今回のPayload bytesを自ら再Readしたこと |
| `claims.localAConsumerAndExternalBReceiptJsonObserved` | Aで実Consumerを直接起動／Bで外部JSONを受領したことに限って`true` | BのHost/Tool、Skillの実ロード、他Sinkの送出 |
| `claims/executionPaths.externalBConsumerInvocationVerified`、`externalBPayloadRereadVerified`、`externalBReceiptReplayExcluded` | いずれも`not-proven`。保存済みB Receiptが通る負例を回帰 | Bの実Tool起動、現在Source/Revision・Disclosure/Grantの再評価 |

**以前のG5 #34/#43/#45/#46の固定Receipt・観測IDは歴史記録として変更しない。** 当時のB実Claude Code argv起動記録は保持するが、B側の実Consumer起動・Payloadの新鮮な再Read・外部送出を実ToolログやHost evidenceなしに証明済みへ上げない。「実行時刻欄だけ追加」「票を再署名した」といった宣言系の改変は、任意BプログラムがJSONを返せる限り実行証明の代わりにはならない。

**実施順**：既定[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)のG0読取隔離／G1外部送出／G2全Tool Reply→固定独立4Session H2/H3を優先。その後、実Host/AgentのTool呼出開始・終了、入力Ticket/Source bytes、Consumer Process/結果と現在Grantの独立ログを既存実行環境で採取する。TAIは新しいReceipt Attester・Agent Runtime・共通Verifierを作らず、Consumer/Host/Harness各Ownerの記録を照合するだけ。G5-N5はこの`NOT PROVEN`を実行中に勝手に`PASS`へ上げないための負例。

### 必須負例

| ID | 注入 | 期待 | 実測 |
| --- | --- | --- | --- |
| G5-N1 | Harness A のSession Logに票の内容が残っている状態でHarness Bを起動 | Harness B は票を**ファイルから独立に再読取**する | `observed-pass`（Harness B は `bin/sho-inspect.cjs handoff <票>` を実行し、ファイルから読む。Session履歴の復元経路は無い） |
| G5-N2 | Harness B に広いshell権限がある環境で実行 | 書込み・送出が実際に起きない | **Receiptの宣言値だけ一致**。Claude Codeに `--allowedTools Bash` を与え、返ったReceiptの `writerInvoked=false`・`externalDisclosure=false` は確認したが、OS/Network実副作用・送出全Sinkは**not-run** |
| G5-N3 | Harness A で開示Scopeを広げた履歴がある | Harness B は**現在の** `disclosure.scope` だけを見る | **AローカルCLIでのみ `observed-pass`**（`widened-scope-rejected`）。Bの外部Harness経由では不正拡大票を実行しておらず**not-run** |
| G5-N4 | Harness B がMCP経由で接続する | CLI-only経路のPASSをMCPのPASSに読み替えない | `not-run`（MCP経路は実行していない。`otherHarnessMcpPath: not-run`） |
| G5-N5 | Bに**保存済みRecipient受領JSON**を再出力させる（B実Consumerは実行しない） | 内容一致の成功とB実Consumer/Source再読取/Replay排除の成功を別資格とする | [SHO #47](https://github.com/hat47x/sho-composer/pull/47)の実Runner回帰で**再利用成立を観測**。三つの実行資格はいずれも`not-proven`。実二Agent/Host egressは`not-run` |

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
| tai-pleroma | `evaluations/tools/check-handoff-sei-binding.cjs` | 照合ツール（test-only）。診断名は TEI E9 の語彙を再利用 |
| tai-pleroma | `evaluations/records/G6-handoff-sei-binding-observation-2026-11-11.json` | 実票での照合結果と self-test の記録 |
| tei-platform | `plan/` | TEI #2586（Query→Context→Claim）・#2516（用途別Projection）の既存Laneに接続。**本票では未着手** |
| sei-cognition | `contracts/` | `sei.semantic-reference` の Exact Binding の形を照合の基準として読む。**変更しない** |

ツールの出力に `yi.handoff.sei-binding-review/v1` と `yi.handoff.sei-binding-self-test/v1` という識別子が現れるが、**これらは本ツールの出力形式であり、新しい交換契約ではない**。Handoff 票の契約は `yi.handoff.context/v1` のまま。

### 受入条件（機械確認可能）

1. `references[].digest` をSEIの Exact Binding 形式と照合し、一致・不一致・未知を区別して返せる。
2. TEI #2586の実Read closureが実証された範囲**だけ**、否定Claimを適合判定する。未実装の範囲は `insufficient-evidence`。
3. 照合結果は `reference-linked-unverified` にとどめる。`verified` へ自動昇格させない（TEI E9の既存診断名を再利用）。

**実行結果（2026-11-11）**：1・3 は `observed-pass`、2 は `not-run`。

| 受入条件 | 実測 |
| --- | --- |
| 1 | 実票（TEI観測引用）で3参照の状態を区別して返した。`tei:…:application:order_entry` と payload が `reference-linked-unverified`、`producer-source` が `reference-incomplete`（digest 欠落）。`--schema` 指定時は SEI schema の `exactBinding` 必須欄が期待どおりかも確認 |
| 2 | **`not-run`**。TEI #2586 の Claim closure は未接続。否定Claimの適合判定はしていない |
| 3 | `reference-linked-unverified` に留めている。`profile.matched=false`・`declaredByTicket=null` を明示して返す |

**fail-closed（追加）**：票でないJSON・`schema` が `yi.handoff.context/v1` でないもの・`references` が配列でないもの・`references` が**空配列**のものは exit 2。空配列や references 欠落を「照合して何も見つからなかった」として exit 0 で返さない。

### 必須負例

| ID | 注入 | 期待 | 実測 |
| --- | --- | --- | --- |
| G6-N1 | 空配列 `[]` を「global不存在」と結論づけるConsumer | `insufficient-evidence`。母集団・Predicate・coverageの確認を要求 | **`not-run`（正式に閉じた）**。このツールは母集団・Predicate・coverageを持たないため断定できない。出力の `notDeterminable['insufficient-evidence']` に理由と責任者（TEI #2586 closure）を明示する |
| G6-N2 | 部分取得を「全件」として報告 | `evidence-mismatch` | **`not-run`（正式に閉じた）**。このツールは参照の形だけを照合し、参照先の内容を読まない。`notDeterminable['evidence-mismatch']` に理由を明示 |
| G6-N3 | Source-only移動後にWorldFPのみ一致、引用locatorは旧版 | `stale-or-different-binding` | **`not-run`（正式に閉じた）**。同bytes別path・旧版locatorの検出手段がない。`notDeterminable['stale-or-different-binding']` に理由を明示 |
| G6-N4 | 同じdigestの別Source | 同一視しない。所在とdigestを別列で確認 | **`observed-pass`**（一部）。同一 `locator` の複数参照は `reference-ambiguous`。ただし「同digestの別Source」の検出は `locator` でしか区別できないため、**別Sourceの検出そのものは未実装** |
| G6-N5（追加） | 票でないJSON／`schema` 不一致／`references` が配列でない／**`references` が空配列** | exit 2（fail-closed） | **`observed-pass`** |
| G6-N6（追加） | `representation_profile` を票が宣言しない | `matched=false`・`declaredByTicket=null` を明示 | **`observed-pass`** |

**ID の使い回しに関する注意（解消済み）**：self-test の ID は `ST-N1`〜`ST-N4`・`ST-linked-*`・`ST-exact-binding-*` に改名し、票の負例 ID（`G6-N1`〜`G6-N6`）と**完全に分離した**。かつては self-test が `G6-N1`〜`G6-N4` を別シナリオに使っており、票の G6-N1〜N3 が通ったように読める状態だった。いまは名前が違うので混同しない。


**「正式に閉じた」の意味**：G6-N1〜N3 は**実装しない**と決め、その理由と責任者をツールの出力（`notDeterminable`）に載せた。黙って通す（「確認済み」と読ませる）のではない。断定には Product 自身の read closure が必要で、それを持たないツールが判定すると read closure を持たない断定になる。

---

## 7. Owner判断ゲート一覧

> **代行決定（2026-11-11）**：Owner から委任を受けて、安全側の既定で決定した。**実 Owner は各決定を覆せる。** 覆す場合は Issue/PR に理由を残すこと。代行決定の原則は「(a) 露出面を広げない、(b) 新しい共通基盤を作らない、(c) 既存の安全不変条件を緩めない、(d) 必要性が実測されるまで機能を増やさない」の4つ。

| ID | 判断事項 | 影響する票 | 代行決定 | 理由 |
| --- | --- | --- | --- | --- |
| OG-1 | 開示Scope語彙 | 全票 | **v1 の閉集合（`synthetic-only`／`reviewed-projection-only`）のまま。新增しない。** | 語彙を増やすと露出面が広がる。新しいScopeは、それ自体の監査と試験を持つ要求が実測されてから。`reviewed-projection-only` の意味は「人間がレビュー済みと判定した内容の投影」に限定する |
| OG-2 | `source.status` と文書単位の開示宣言をTEI側契約にするか | G3 | **追加しない。** 無いまま `unknown` として動かす | TEI の artifact 生成契約を広げる必要が実測されていない。Consumer は欠落を `unknown` として扱い fail-closed なので、安全側で足りている |
| OG-3 | 本文・題名の業務面への公開（SUI #3369） | G3・G6 | **公開しない。** 既定は SafeMode ON、構造のみ | 未レビュー情報の意図しない共有は安全不変条件。用途ごとの明示許可があるまで緩めない |
| OG-4 | 連鎖Handoffの `chain`（v2）を採るか | G3.5 | **v2 は作らない。** 連鎖が必要になったら**新しい票として発行**し、`evidence[].basis` に継承元の handoffId を、`limitation` に「継承した観測である」ことを書く | v1 の型を広げずに来歴を運べる。未知欄を増やすと Consumer の解釈がぶれる |
| OG-5 | 返送Receiptの保持期間・閲覧者・監査利用 | G2 | **一時的な作業物。保持義務を課さない。試験後は消す。** 監査・コンプライアンス用途には使わない | Receipt は Consumer の観測であって証明書ではない。監査に使う要求が実測されたら別判断 |
| OG-6 | **共通実行基盤の新設・権限境界の変更** | 全票 | **行わない（却下）。** 共通Runtime・中央Host・第二Registry・権限Engine・自動Scheduler は作らない。権限境界も変えない | 元の制約どおり。不足が実測されたら具体案を別途出す |
| OG-7 | Harness別Adapterの配布・版固定（TAI #74） | G5 | **配布しない。** CLI-only 経路を参照経路として維持する | 配布物は版固定・依存閉包・許可の説明を要する。現状は観測の記録で足りている |
| OG-8 | MCP Tool一覧への read-only 追加（SUI MCP の allowlist） | G5 | **追加しない。** 既存の2 read-only Tool のまま | allowlist を広げると MCP 面が広がる。CLI 経路で足りており、CLI を参照経路とする |

### 7.1 代行決定で「実装しない」が確定したもの

OG-2・OG-3・OG-4・OG-6・OG-7・OG-8 は**実装しない**。したがって以下は作らない。

- TEI 側の `source.status`・文書単位開示宣言の生成
- 本文・題名を Handoff 票やpayloadへ載せる経路
- `yi.handoff.context/v2` と `chain`
- 共通Runtime・中央Host・第二Registry・権限Engine・自動Scheduler
- Harness別Adapter の配布パッケージ
- MCP Tool の追加

### 7.2 代行決定で「維持」が確定したもの

OG-1・OG-5 は現状維持。既存の実装を変えない。

- 開示Scopeは `synthetic-only`／`reviewed-projection-only` の2値
- Receipt は一時作業物。保持・監査の義務なし

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
| 受入条件の機械確認 | **一部**。G2・G3・G4・G5の主要条件は達成。G6-受入2、G5-受入3、G4-N2/N3、G5-N4、G6-N1〜N3 は `not-run` |
| 必須負例の実注入 | **一部**。G2・G3は実注入済み。G4は1件、G5は3件、G6は3件が `not-run`（理由を各表に明記） |
| 合成試験と実製品E2Eの区別 | **達成**。Receiptの `scope` と `claims` で区別。CIのPASSをlive handoffのPASSに数えない |
| 未実行の `not-run` 保持 | **達成**（§実行状況・各負例表） |

**Owner判断**：§7 の OG-1〜OG-8 は **2026-11-11 に代行決定済み**。実 Owner は覆せる。

**まだ完了ではない理由**：上の「一部」「not-run」が残る。ただし OG-2・OG-3・OG-4・OG-6・OG-7・OG-8 は「実装しない」が確定したため、これらの `not-run` は**努力不足ではなく決定の結果**である。残る `not-run` は外部条件（実Host Grant/egress、意味受理、SEI runtime、TEI Claim closure）に依存する。

### 8.4 独立監査の結果

**第1回（2026-11-11、3エージェント）**：blocking 0・non-blocking 16・question 8。
主なもの：票への本文除外 assert 欠落、TEI modelRevision の `revision.digest` 誤帰属、`readBoundedRegularFile` の check-then-use、`fileDeletedAfterTrial` の事前記録、G6 負例 ID の使い回し、2文書の数値不整合。→ **全件対応済み**。

- **票への本文除外 assert**：payload と同じ除外を票側にも置いた。原本の生データ（Document/Island/Card の原本・card meta の原本Source）が自由文欄に注入されると CI が失敗する。あわせて OG-3 の「本文」の適用範囲を ADR-0117 に明記した。
- **未知のトップレベルフィールドの黙って落とす挙動**：Consumer・Producer とも `unknownFields` として逐語運ぶ。落とすと後から語彙を増やしたときに過去の票・Receiptから拡張欄が無警告で失われる。reject すると前方互換が壊れ、解釈すると「未知の値は unknown のまま」不変条件に反するため、逐語運ぶだけが両方を満たす。
- **G6 self-test ID の使い回し**：`G6-N1`〜`G6-N4` を `ST-N1`〜`ST-N4`・`ST-linked-*`・`ST-exact-binding-*` に改名し、票の負例 ID と完全に分離した。
- **未使用の `HANDOFF_READBACK_SCHEMA`**：削除。write-back 契約は OG-5 により未実装で、未使用の定数は契約が存在するように読める。

**第2回（2026-11-12、マージ前レビュー、3エージェント）**：blocking 2・non-blocking 8・question 1。

| blocking | 内容 | 対応 |
| --- | --- | --- |
| B-1 | SHO の試験記録が「12観測・`sessionResumeRechecks=true`」と記載。リンクする receipt は14観測・`harnessSessionResume="not-run"`。実 Harness Session 再開を合格として記録していた | **修正**。14観測に更新し `newProcessRereceive=true`・`harnessSessionResume="not-run"` に修正。HEAD値も現在値に合わせ、「三製品は observed-pass、Session再開の実製品確認と別Harness移行は NOT RUN」と分けて記載 |
| B-2 | TAI §3.5 が `yi.handoff.context/v2` と `chain` の具体スキーマを「次の段階で検討する」案として残していた。OG-4（v2/chain は作らない）と矛盾 | **修正**。具体スキーマを削除し、v1 で来歴を運ぶ方法（新しい票として発行・`evidence[].basis` に `from:<handoffId>`・`limitation` に継承であることを書く）に置換 |

| non-blocking | 内容 | 対応 |
| --- | --- | --- |
| NB-1 | SUI の契約コメントが実挙動と不一致 | **修正**。生産ModuleはI/Oを持たないこと、書き出しは各テストが明示的に渡すdirectoryだけだと実挙動に合わせた |
| NB-2 | `handoff_receipt_review.test.ts` に describe 外の `it` が2件 | **修正**。describe ブロック内へ移動 |
| NB-3 | G6 記録 JSON の selfTest.cases が陈旧した ID（`G6-N*`） | **修正**。実出力の `ST-*` に更新し、票の負例とは別シナリオであることを note に明記 |
| NB-4 | G6 ツールが `references: []` を exit 0 で通す（fail-open） | **修正**。空配列も拒否する |
| NB-5 | `ticketSha256` が BOM 除去前の生バイトから計算 | **修正**。BOM 除去後の文字列から計算 |
| NB-6 | SHO の unknownFields がトップレベルだけ。`producer.productSkill`・`consumer.entrypoint` が正規化で消えていた | **修正**。既知コンテナ内の未知キーも `unknownFields.<container>.<key>` に集録。fixture から未知キーを外し baseline を0に保つ |
| NB-7 | `conversationHistory` が note ごと落ちる | **修正**。そのまま運ぶ |
| NB-8 | `payloadRaw.length` の比較が byte/char で混線し得る | **修正**。`Buffer.byteLength` を明示的に使用 |
| NB-9 | SHO 試験記録のHEAD・観測数が receipt と不一致 | **修正**（B-1 と同時） |

| question | 内容 | 対応 |
| --- | --- | --- |
| Q-1 | `ReceiptReview.unknownClaims` は照合が claims 検証へ到達した経路でだけ設定される | **対応しない**。拒否される経路では claims の検証自体が到達しないため、早期 fail-closed の帰結。コメントで明記するだけで足りると判断 |

**第2回で「対応しない」と判断したもの**：Q-1 のほか、「好み」や「別の設計の方がよい」という指摘は含めなかった（マージ前レビューの依頼条件）。

### OG-3 の厳格読取への切替手順（別決定・未実施）

緩和を採ったが、実 Owner が「レビュー済み投影文本字も不可」と判断する場合は次で切り替える。**起票は外部効果なので Owner 判断とする。**

| 手順 | 内容 |
| --- | --- |
| 1 | `handoff_context_emit.test.ts`・`handoff_tei_observation_emit.test.ts` の `buildContextProjection` を `safeMode: true` に変更 |
| 2 | payload の354 bytes／独立期待SHA `7fd6fde2…71cd` が**変わる**。P0 byte 契約の更新が必要 |
| 3 | SHO 側 `test/fixtures/sui-to-sho-p0.md` と SUI の `context_projection_markdown_handoff.test.ts` の独立期待も追随 |
| 4 | SHO の Runner の `EXPECTED_PAYLOAD_BYTES`／`EXPECTED_PAYLOAD_SHA256` を更新 |
| 5 | SUI の `CHANGE_DETECTION_PIN`（票digestの変化検出）を更新 |
| 6 | `EXPECTED_PRODUCER_BLOBS` の3blob を更新（独立に差分を確認してから） |

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

---

## 10. 後続の最小実証：Qualified Target→Handoff→Consumerを「同じ対象」と言えるか（2026-11-12／新試験NOT RUN）

### 10.1 なぜ追加するか、既存G1〜G6で保証できていないこと

実[SUI Producer](https://github.com/hat47x/sui-sensemaking/blob/main/03_Implement/frontend/src/export/handoff_context_envelope.ts)の`yi.handoff.context/v1`には`target.{product,kind,id}`、`revision`、`references[]`、`evidence[]`等がある。[SHO Consumer](https://github.com/hat47x/sho-composer/blob/main/src/handoff_envelope.cjs)はHandoff票を非信頼入力として検査し、**Markdown payloadの実byteを独立に再Read**する。G3ではTEI read-onlyの観測を**引用**した。しかし**SHO側がTEIの対象IDを同じSource/Workspace/Scopeで独立解決した証拠はない**。この差を、単なる`target.id`一致や全体`worldFingerprint`一致で埋めない。

TEIの[#4475](https://github.com/hat47x/tei-platform/issues/4475)のうち、**Fingerprint計算が元モデルのAuthorityLimitsを書き換える／自分自身のFingerprintをハッシュする問題は[merged #4507](https://github.com/hat47x/tei-platform/pull/4507)で実コード・正負テストを追加して修正**された。一方、同Kind・同IDの後勝ち衝突とConsumerでの曖昧対象判定は残る。[#4472](https://github.com/hat47x/tei-platform/issues/4472)のCRUD Data索引修正は[Draft #4513](https://github.com/hat47x/tei-platform/pull/4513)が未統合であり、明示定義のみの脱落・矛盾OKは別問題。[Draft #4514](https://github.com/hat47x/tei-platform/pull/4514)は図面Source-only driftを既存`sourceFingerprint`で再評価する候補で未統合。**構造Fingerprintが同じでも、元Sourceの移動・原文改版・現在Grant・Owner受理の資格は別**。Derived CRUD Cellや同名RelationをID/構造Digest一致だけで編集対象とみなさない。さらに[TEI #2586](https://github.com/hat47x/tei-platform/issues/2586)のProvider実Rowsetは未接続であり、Model WorldFPが変わらなくてもDB Rowset/RLS/Grantの現在資格は変わり得る。

**追加するのは後段Trialの独立Expectedと判定票のみ**であり、既存P0の354 byte/SHA、G2〜G6の受入・Receipt、`yi.handoff.context/v1`のSchemaやDisclosure閉集合、TAI #168のH2/H3初回4Slot、旧G5の実CLI切替の証拠を変更しない。TAI #629/#633はUI選択・Pin/製品別再解決設計の並行Draftであり、本書ではその第二の状態機械を実装しない。

### 10.2 同じ対象・同じ根拠・同じ現在資格の判定を分割する

| 評価列 | 実観測のOwner | 成功とみなす最小証拠／成功でないもの |
| --- | --- | --- |
| **I：Intent/Pin** | 将来のTEI Studio/CUI Product UI（#1124） | 利用者が指定したQualified Kind+ID/Workspace/Source/Occurrence/Scopeと意図を固定した観測。試験Driver内の明示選択は*合成Pin*でありGUI Pinの実証でない |
| **R：Resolve/Uniqueness** | TEI実Catalog/Inspect/Source Readerと別Expected（#1124/#4475） | 当該Source/Scope/版で対象を再発見し、候補複数・失効/部分取得を別判定。`target.product/kind/id`・ラベル・Fingerprintの一致**だけ**では不十分 |
| **P：Projection/Disclosure** | Product/Host（TEI #2516／TAI #232） | 今回のAudience/目的/Current Grantに許可された範囲だけを生成した証拠。Driverが公開合成資料だけを使った場合、実OS外部送出禁止をPASSとしない |
| **T：Transport/Receipt** | SUI Producer→SHO実CLI、既存G1〜G5 | 票・payload exact byte/Source・Receiptの実受領。これ単独でTEI対象の独立解決や現行Source/Meaning受理を示さない |
| **C：Consumer meaning/use** | SHO/TEI/SEI各Consumer（TAI #271） | 当該Consumerが用途相対の根拠・未決を再照合した範囲でのみ限定説明。未知のReference/Source未Readなら`unknown`を保持 |
| **H：Harness/Skill/Effect** | TAI #168/#488、実Host/Provider | 実Tool/Skill Loader/Session/Effectを各実証で区別。G5でAローカルNode・B外部ARGV受領が一致したこと≠二Agent実呼出・同一Live Session再開、Handoffの`productSkill`文字列≠実Load |

### 10.3 最初の実行カード（Ownerの既存Runnerを再利用する）

**QH-P0（read-only / Headless）**：①公開可能なTEI `reference/workspace`を固定し、現行`go run ./cmd/tei model catalog -workspace reference/workspace`の実Source/HEAD/CLI argv/Tool profile、選択候補1件のkind/id/取得Scopeを実観測する。②`I`はGUIを使わない**明示テストDriverの合成選択**と記録し、対象に対する独立Expectedを先に固定。③既存SUI Handoff v1の`target/revision/references/evidence/limitations`に適合する公開内容だけを通し、現行SHO `bin/sho-inspect.cjs handoff`の実受領/別Process再Readを[既存Runner](https://github.com/hat47x/sho-composer/blob/main/scripts/handoff-cross-product.cjs)で観測。④**TEI対象の再解決が実行されていないなら**`T=observed-pass`と`R/C=not-run/insufficient-evidence`を並記。v1票に入らないQualified Scopeを空想のFieldで補完せず、既存Productの公開Referenceで束縛を表せない場合は適合性GapとしてOwnerへ返す。テスト用のTEI CLIが実Consumerに代わって再Readしたなら「DriverによるR」と明示し「SHO ConsumerがR」としない。

**QH-P1（GUI/CUI比較、後段）**：TEI Studioで同じ対象を固定→無関係な画面/Canvas/AI入力へ移動→再度同じ対象へ戻り、CUIでの指定とIdentity/Scope/時点が一致するかを確認。まだPin操作が実装されていない場合は`unsupported/not-run`。実外部Harness受領・現在Policy・書込み/Effectは別Gateにする。

**評価する利用者価値（今は測定計画）**：同じ許可済みTaskでAIなしのProduct/CUIと、固定対象→Handoff→復帰する経路を対照。対象へ戻る操作数/再説明文量、誤対象の回答・誤付替え件数、元根拠と未決の保持率、訂正・Undo/不適格時停止の成否、実Tool/転送/人手費用を別々に記録する。誤対象・秘密開示・黙ったSource再束縛は合格させず、**従来経路と比べて改善が観測されなければ既存Product単独UIを維持**する。生成AIによる評価しかない場合は利用者実測を偽装せず、独立Expected付きシナリオと操作イベント観測に限定する。

**並列・接合順**：S＝各Product内の対象選択・再解決（#1124/#4475）、H＝外部HarnessのG0/G1/G2・Tool実証（TAI #168）は独立に進めてよい。J＝実Productで固定した同一対象を**実Harness Sessionを介して**戻す接合TrialはS/H双方の必要資格後。C＝CSW×SUIの方法寄与・KJ型補正はJとは別Armで評価し、初回を遅らせない。これは追加の共有Runtimeや全製品共通Gateを設けることではない。

| Case | 独立Expected（QH-P0全体はNOT RUN。QH-07の局所Consumer負例のみ実行済み） |
| --- | --- |
| **QH-01** 正常な一意対象 | kind/idだけでなくSource/Scope/実Read revision/当該Consumerの再Readを列別記録。実Consumerが未実装なら列は未実施 |
| **QH-02** 同Kind同ID重複・別Scope同名 | TEI #4475の問題を静的負例として固定し、自動的に後勝ちの1件を選ばない。実修正済みと主張しない |
| **QH-03** 構造FingerprintとSource/Authority変化・A→B→A | [merged #4507](https://github.com/hat47x/tei-platform/pull/4507)の**計算純粋性・自己参照排除は修正済み**として別記録。一方、Authorityのみ変更・Source-only変更・A→B→Aで構造Digestが同じでもSource/current Grant/意味資格を復元しない（#4514はDraft、別実試行NOT RUN） |
| **QH-04** CRUD明示のみ・矛盾/誤索引 | [#4513 Draft](https://github.com/hat47x/tei-platform/pull/4513)のData索引修正がまだmain未統合。仮に索引修正済みでも、#4472の明示CRUD-only／矛盾後勝ち／`ok=true`の整合判定は別の独立Expectedが必要 |
| **QH-05** 非公開Peerあり/なし、許可Projection同じ二世界 | Handoff票/Body/Receipt/diagnosticsに未許可ID/件数/Location/Roleが漏れない。Host外部egressは別実観測 |
| **QH-06** 部分取得・0件・Resolver不在 | complete emptyとpartial/not-found/unknown/unsupportedを区別し、無取得を「存在しない」と断定しない |
| **QH-07** Handoff受領は成功だがTEI Source再解決なし | [SHO merged #48](https://github.com/hat47x/sho-composer/pull/48)で**局所合成負例を実Consumer/CLI・Ubuntu/Windows CIで実行済み**：同一PayloadでもSource/Revision/対象IDが異なる3票を受領し、`independentReread=true`でも`originalSourcesRead=false`・`sourceRevisionCurrent=false`。**実TEI Source再解決とQH-P0製品横断試験はNOT RUN**。`T`の局所観測と`R/C`現在資格を合算しない |
| **QH-08** Skill名付き票/G5別Harness CLI/B事前Receipt再利用/後着GUI結果 | Skill文字列≠実Loader、B JSON一致≠実Consumerの再Read（[SHO #47](https://github.com/hat47x/sho-composer/pull/47) G5-N5）、旧結果≠新Pinの資格。実Session継続、対象再束縛、業務Effectはそれぞれ独立観測が必要 |

### 10.4 最初の実Consumer反例：同じPayloadと異なるSource／対象ID（2026-11-12、局所試験のみ）

[SHO main PR #48](https://github.com/hat47x/sho-composer/pull/48)で、既存`yi.handoff.context/v1`の合成・read-only票に`target.product=tei-platform`／`kind=data`を宣言し、**同じ実Markdown bytes**について次の3ケースを独立Expected付きNode試験に追加した。

- **A**：`target.id=sales.order`、`source-a`、そのSource Revision digest／Source locator。
- **B**：同じ`target.id=sales.order`、しかし`source-b`と異なるRevision digest／Source locator。
- **C**：同じ`source-b`と同じPayload、しかし`target.id=sales.order.other`。

3票とも実SHO Consumerが`status=received`でPayloadを独立に再Readし、Payload SHA/長さは一致。Bでは票SHA・Source locator・宣言Revision digestがAと異なり、Cではtarget IDだけがBと異なる。**それでも`claims.independentReread=true`と`payloadMatchesTicket=true`になり得る**ため、これらは元のTEI Source/Kind/IDの再束縛成功を示さない。実際のConsumerは`originalSourcesRead=false`、`sourceRevisionCurrent=false`、`meaningAccepted=false`を保持する。最終ケースを実`bin/sho-inspect.cjs handoff` CLIでも検査。Ubuntu/Windows Handoff CI成功。

**局所成功の上限**：本試験のSource locatorは合成文字列で、TEI実`reference/workspace`へ接続していない。SUI実Producerとの一往復、TEI Source位置/改版/Grantの現在再照合、TEI同Kind同IDの衝突解消、GUIで固定したSelectionの再資格は引き続き`not-run`。新しいTEI ResolverやHandoff v2をSHOのReaderへ組み込むのではなく、次のQH-P0で**TEI Product Readerが当該Qualified Subjectを実Readしたか**を別列で確認する。SHOによるMarkdown独立再Readの証拠をTEI Sourceへ流用しない。

**終了/撤退条件**：P0の成功は`I`合成・`T`既存限定・`R/C`当該実Consumerが本当に行った範囲でのみ宣言。Kind/ID一意性、対象の元Source Binding、Disclosure Producer、Consumer Resolverのいずれかを実証できなければ、特定の列を`not-run/unsupported/insufficient-evidence`として残す。新UI/第二Resolver/Authorizer/Session Store・新`yi.handoff.context/v2`を要する設計なら実装を停止して各OwnerへFit/Gapを返す。初回TAI #168 H2/H3の新Blockingにしない。

**責務**：対象解決と#4472/#4475修正＝TEI #1124/#4472/#4475、用途別開示＝TEI #2516/TAI #232、Handoff/実Consumer＝SUI/SHO既存Owner、Activity現在資格＝TAI #271、Skill有効性＝TAI #488、実Harness比較＝TAI #168。既存のG1〜G6の歴史実測をこの未実施のQHで上書きしない。
