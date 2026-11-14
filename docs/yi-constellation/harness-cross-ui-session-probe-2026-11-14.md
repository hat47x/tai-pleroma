# YIC 複数UI・外部Harness Session接合の後続実証計画（2026-11-14）

> **Status: Proposed / Docs-only / 新しい実Harness・実Product E2Eは NOT RUN。** 本文は既存Ownerの受入票へ実行順と記録方法を接続する補助計画であり、Handoff v2、公開API/ABI、第二Expected/Authority、中央Runner/Session Store/Lock/Registryを定義しない。Ownerの正式採用・外部送出・業務実行を意味しない。

## 0. 関連Ownerと変えない先行条件

- [TAI #234](https://github.com/hat47x/tai-pleroma/issues/234)：B0〜B4投資比較、Goal/Schedule/並列、[HC-01〜14](https://github.com/hat47x/tai-pleroma/issues/234#issuecomment-6844475381)、[HC-15〜18](https://github.com/hat47x/tai-pleroma/issues/234#issuecomment-6856979920)の後続判断。B4独自Agent Loopは未採用。
- [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)：初回Blockingは**G0実OS identity/Read-deny正負→G1実Egress→G2実Tool Reply完全性→新規独立H2→H3→H3→H2の4 Slot（直近確認0/4適格）**。本計画を初回の新Blockingにしない。
- [TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)：Activityの目的・参照・未決・根拠と現在資格、別Sessionへの選択的Handoff。[TAI Draft #633](https://github.com/hat47x/tai-pleroma/pull/633)：元PinのProduct再解決、限定Projection、返却先、既存Handoff v1の後続R0〜R5。[TAI Draft #629](https://github.com/hat47x/tai-pleroma/pull/629)：選択集合Q/E/Aとidentity/partialの判定。[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)/[#562](https://github.com/hat47x/tai-pleroma/issues/562)：機密と回答前観測面。[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)：利用者価値比較。
- [TAI QH-P0 実行票§10](https://github.com/hat47x/tai-pleroma/blob/main/docs/yi-constellation/cross-product-handoff-execution-tickets-2026-11-11.md)：意図I、元Product再解決R、現在開示P、配送T、Consumer実用途C、Harness Hを独立記録。**QH-P0のI/R/P/T/Cと外部HarnessのHは別資格**。
- [TEI #4515](https://github.com/hat47x/tei-platform/issues/4515)：Workbench-local Subject Pin/UnpinとHost Inspectの再資格化。現時点のGUI Pinと意味Relation Pinは未実装。[TEI #3419〜3422](https://github.com/hat47x/tei-platform/issues/3419)：型付きApplication API、CLI/MCP/HTTP/IPC意味同値とProduct側Acceptance/Effect。
- **別レーンP0**：[TEI #4583](https://github.com/hat47x/tei-platform/issues/4583)：生成N0 Inspector→N1 Go/TS→N2 esbuild→N3 native Wails/実WebView2、BuildIntent/Builder/Stage1→Stage2実再入。Draft #4587の同HEADで生成WebView2限定実証あり。**B1-B/B2/B3の正規BuildIntent・Stage1 Desktop自己再入はNOT RUN**。YICはBuild Engine/Source authorityを所有しない。

## 1. 目的と不可逆な境界

**目的**：人がTEI StudioでSubjectをPinし、必要時だけ外部Harnessへ説明を依頼、SHOまたは別のTEI UIに移っても元の対象・証拠・未決を誤継承せずに回答を候補として受け取る。

三つの継続は別々に採点する。

| 継続対象 | 実体・Owner | 認めない推論 |
| --- | --- | --- |
| Activity continuation | TAI #271が保持するTask意図、必要な参照と未決、許可済みHandoff | 新Session再開を同一Live Session復帰と呼ぶ |
| Native Harness Session continuation | 実Harness/HostのSession・Turn・Tool Event、Profile/Provider実能力、Transcript | 保存Session IDから別UIの閲覧可・多Writer可・完全Log/過去承認の移転を推定 |
| Product Operation continuation | TEI/SHO/EKI等の現在のSource/Attempt/BuildIntent/Receipt/Consumer | AIの「完了」、Tool exit、Interrupt、過去Receipt再出力から実Effectやセルフビルドを推定 |

**既存Sessionの履歴は新しい開示先に対する潜在的な情報源**である。現在のUIへ新規送信してよいという判断だけでは、過去Transcript/Tool Result/Prompt/Session LogをそのUIから閲覧してよいとは限らない。既送のRawは事後の権限撤回で取り消したと扱わない。閲覧可能範囲を現Hostで確認できなければ、旧Sessionへattachせず用途を限定した新Sessionへ縮退する。

Source Revisionは単独の鮮度証明ではない。[TEI #4616](https://github.com/hat47x/tei-platform/pull/4616)の限定実試験ではWorld/SourceIndex/Model Revisionが同じでも実Root存在差でValidationがerror→warningへ変化。Root/Origin、Required/Consumed範囲、Validation現時点、Grant/Recipient、Plugin/Tool byte、Build選択/実消費を用途別に再確認する。0件や空referencesはSubject不存在・未使用・完全取得を証明しない（TEI #4577）。

## 2. 最小利用モード：機能一覧ではなく当該Hostでの実効資格

| モード | 操作 | 当該Attemptで必要な証拠 | 不成立時の縮退 |
| --- | --- | --- | --- |
| M0 Product-only | AIなしのStudio/CLI/SHO | Product単体の対象・Result・Acceptance | M0のまま利用可 |
| M1 Activity handoff | 許可済み目的・参照・unknownを**新Session**へ引継ぐ | Producer Projection、現在開示、既存Handoff v1のConsumer実Read | Product-only。秘密Rawの代替送出禁止 |
| M2 Live view | 同じNative Sessionの現在/過去Eventを**閲覧** | 実Session IDと実Host設定、履歴のAudience/Recipient適合、Tool/Transcript受領完全性 | M1へ。旧Live Session共有と表示しない |
| M3 Live control | 同じSessionへTurn送信/Interrupt/Tool呼出し | M2の資格に加え、Nativeの同時Turn/直列化/操作帰属の**実保証**、送信UIとTurnの結合 | 実証可能な単独操作元のみ。別UIはM2またはM1 |
| M4 Product apply | AI提案をPreview→受理→実変更へ | **元Pinを今再解決**、Product現在Grant、既存Acceptance/Operation ID、Effect/Receipt/独立Consumer観測 | read-only候補として保持。Effect unknownで自動再実行しない |

M0〜M4は実装レイヤーの強制的な一方向状態機械ではない。用途・Audience・Host実能力ごとに成立するモードを限定して表示する**評価上の区分**。M2/M3の追加がProductの正しいM0/M1やTEIセルフビルドの前提にならない。

**同一Sessionの同時操作**について、UI-local mutexを分散端末/別Processまで有効な排他とみなさない。既存Harness/Hostに実保証がなければM3で二Writerを公開せず、実証済み一つの操作元＋他View閲覧/新Session Handoffに縮退する。新中央Lock Serviceを解決策として先行採用しない。

## 3. 後続read-onlyの一往復：既存QH/Pin/HC票を使う

1. **R0 Product読取**：公開合成TEI Workspaceを固定し、実Inspect/Catalog/必要なsource-indexで存在するSubjectのkind/id/Root/Origin、Source/Validation、取得範囲・unknownを観測。SourceIndex空配列だけで存在確認しない。Productのtyped API/CLIで入口差を区別する。
2. **R1 Pin意図**：TEI #4515のWorkbench-local Subject Pinを一時Focusから分離。未実装なら既存CLI上の固定参照を用い**GUI Pin PASSと呼ばない**。同FP別Root、A→B→A、旧Reply遅着では意図保持と現在資格失効を別表示。Relation Graphの描画IDを意味IDとしない。
3. **R2 Disclosure/Consumer**：Productで現時点に再解決した許可ProjectionだけをPreview→明示送出し、既存`yi.handoff.context/v1`とTAI QH-P0で別Process Consumerの実受信/実Readを検証。必要ならSHO Readerを選ぶが、SHOがMarkdown本文を読んだことを元TEI Subjectの独立再解決と呼ばない。
4. **R3 外部Harness**：#168のG0/G1/G2が適格な固定Trialとは別の**後続**Taskで、まずTool-only、必要ならProduct Skillを実Load/Invoke、増分があるJobだけTAI Activity Skillを追加。Provider/Model/Host ProfileとRead/Write/Network Grantを実固定し、送出byte、Tool Replyの終端、実Consumer受信、Answer、unknownを分けて採点。
5. **R4 別UIへ復帰**：M1新SessionのActivity再開を先に対照として成立させる。M2 Native Live view、M3制御は各Harness実Capability Probeで許可された範囲だけ追加。各Reply/Turnを発信時のPin・Root/Scope・元Requestに帰属させ、現Focusへ自動反映しない。
6. **R5 候補→Product適用**：最初の一往復は**read-only結果候補まで**。将来のTEI/SHO Writer・EKI実作用では、現在のProduct Operation/Acceptance/Effect Receiptに引き渡し、interruptやAgent Exitを完了・rollbackとはしない。Stage1→Stage2 Build再入はTEI #4583の別Attemptで独立検証。

Source名、件数、digest、Tool候補一覧、Rendererの過去情報も現在開示がないなら送出しない。生TranscriptをEvidence共有の既定形式とせず、用途上許されたSource/Receipt**参照**と必要な限定Projectionを採用する。

## 4. 同一試験の記録列と独立Expected

**新しいログ正本/Schemaではなく既存Runbook・Product CI・Issue/PR Evidenceに記入する列**：

- Task/Activity目的、Product/Root/Origin/Subject kind+id、Pin意図と固定時点、宣言Source/現在Root・Validation/取得範囲、unknown/partial/permission-denied。
- Harness名/版/Provider/Model/Host Profile/OS identity/Tool・Skill実byte、Native Session/Turn/Tool ID、利用モードM0〜M4、実Grant/Recipient。
- 許可Projectionと実Egress、Tool request/argv/stdout/stderr/Reply終端・切断、Consumer実Readと現在資格、Return Location/独立レビュー。
- 実Operationがある場合のみProduct Attempt/Builder selected-vs-actual/Artifact/Receipt・実Consumer。Read-onlyにEffect必須の偽FAILを作らない。
- 事前固定の独立Expected、合格/不合格/unknown/unsupported/environment-ineligible/NOT RUN、Cost・時間・Tool回数・再説明・誤対象・Undo・人手レビューを**別列**。単一の`verified`や総合点に丸めない。

**既存負例を再利用（第二採点表を作らない）**：

| 試験 | 既存Expectedの参照 | 当該観測の差分 |
| --- | --- | --- |
| 過去機密を含むSessionに別Audience UIがattach | [HC-15](https://github.com/hat47x/tai-pleroma/issues/234#issuecomment-6856979920)・TAI #232/#562 | 現時点の新規Projectionと履歴Transcriptの閲覧資格を別検査 |
| 二UIから同一Sessionへ同時Turn/Interrupt | HC-16 | Nativeの実直列化/帰属に失敗したらM3を限定。UI-local queueの成功を多端末保証としない |
| 旧Reply遅着、Stream欠落、別Root同byte、ABA | HC-17・[PIN-S0](https://github.com/hat47x/tei-platform/issues/4515)・[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271) | 元Pinと現在資格を分け、誤対象への自動反映0。欠けたTool Replyはunknown |
| Agent Interrupt後に実Build/Effectが進む | HC-18・[TEI #4583](https://github.com/hat47x/tei-platform/issues/4583) | Native Turn停止とProduct Attempt/実Artifact/Effectを独立照会。旧Receiptによる成功補完・二重再実行0 |
| SUI/SHO等の同byte別Source/旧Receipt再出力 | [QH-P0](https://github.com/hat47x/tai-pleroma/blob/main/docs/yi-constellation/cross-product-handoff-execution-tickets-2026-11-11.md)・[HC-10〜14](https://github.com/hat47x/tai-pleroma/issues/234#issuecomment-6846699191) | 配送と受理/元Source実Readを区別。別Harnessラベルを実Session切替証拠にしない |
| 同一WorldFP/ModelRevisionだがRoot実在変更 | [TEI #4616](https://github.com/hat47x/tei-platform/pull/4616) | 旧現在Validation資格を再利用しない。構造Claimだけ保持できる場合は保全 |

## 5. 受入順・各Laneの終了条件（新Hard Gateなし）

| Lane | Owner | 最小出口 | 非主張 |
| --- | --- | --- | --- |
| A / 最優先 | TEI #4583/#1824 | N0〜N3を既存BuildIntent/Builderの実Attemptで接合しStage1実Process→Stage2 native Desktop→実WebView2 Consumer | YICがBuilderを代行しない。過去別HEADのCIを合算しない |
| B / 最優先 | TAI #168/#232 | 実OS Read-deny・Egress・Tool Reply完全性を確認して初回H2/H3独立4Slot比較適格へ | M2/M3を初回Gateに追加しない |
| C / 並走 | TEI #4515 + TAI Draft #629 | read-only Subject Pin、同FP別Root/ABA/partialの正負と現在資格 | Workbenchの成功をHost Disclosureへ昇格しない |
| D / 後続read-only | TAI QH §10 + #271 + Draft #633 | 同じProduct Targetを今再解決し、許可Projectionが実Consumerへ届き、Return候補が元対象に帰属 | Body受領だけで元Subjectの再解決・同一Live Sessionとしない |
| E / D後続 | TAI #234/#168/#232 | M1 Activity HandoffとM2閲覧/M3操作を別Harness・実Host能力で比較。HC-15〜18を個別記録 | 二UIが同時接続できると仮定しない |
| F / 価値・投資判断 | TAI #422/#234/#488 | B0 Product-only／B1 Tool+Skill／B2 Adapter／B3統合UIの用途別増分、費用/再説明/誤継承/現在資格を同Taskで比較 | B3が有用でもB4自作Loop必要の証明にならない |

**独自Loop（B4）の再審査**：複数の代表Harnessの適格実Trialで同じ必須Jobの失敗を確認し、Product API/Projection・Native Session/Activity Handoff・OS/Host適格性・薄いAdapterでは解決不能であることを独立Expectedで示し、運用/コスト/権限/移行/撤退とOwner受理が揃った時のみ着手する。

## 6. この計画自体の扱い

- 初回の外部Harness試験に追加のRunner、Session Server、Agent Team、Registry、Central Pin/Lock/Policyを持ち込まない。
- UI/Targetの契約をTAI側で固定せず、TEI/SHO/SUI/SEI/EKI各Ownerの既存CLI/typed APIに委譲する。Go単一バイナリ・外部HostというTEIの既定方針を変更しない。
- Evidenceの保存先は既存Issue/PR/CIや許可済みNAS/S3/KON参照を用途で選び、機密RawをGitHubへ一律投入しない。保存と現在の開示・意味受理を分離する。
- 本文のM0〜M4やR0〜R5は**評価時の呼称**で、公開Product API/共通Protocolのスキーマ番号ではない。各Ownerの既存票・Runbookを唯一の実行/判定資料とする。
- **2026-11-14時点の今回実施**：既存Issue/計画/限定CIの静的照合と、この後続実行カードの設計のみ。HC-15〜18、Product→外部Harness→複数UIの実一往復、実Session二画面接合、Owner受理、TEI Stage1→Stage2 Desktopの統合実行はNOT RUN。


## 7. 2026-11-14 横断更新：AIによる起動候補からProduct実行への停止線

他チャットのTEIスクリプト起動・Plugin/三視点・SUI Raw→Card・EKI実Result Delivery・Lifecycle Graphを照合。以下は**各Ownerの既存設計をYICの後続Jobに組み込む実行順の差分**であり、公開ABI/共通Agent Loop/中央Schemaの採用ではない。本節からTAI #168の初回H2/H3へ新Gateを追加しない。

### 7.1 AIの入力は「要求候補」であって権限・起動実績ではない

[TEI #4495](https://github.com/hat47x/tei-platform/issues/4495)のP0・[#4497](https://github.com/hat47x/tei-platform/issues/4497)のP1・[#4502](https://github.com/hat47x/tei-platform/issues/4502)、共通API [#3422](https://github.com/hat47x/tei-platform/issues/3422)に合わせて、以下の非同一性を維持する。

| 既存TEI Ownerの対象 | YICが依頼・表示・記録してよい範囲 | 禁止する自動昇格 |
| --- | --- | --- |
| Function / Script / Accepted Meaning | 意味とSource/契約への許可済み参照 | Functionの存在・parse成功→公開可能な起動Entry |
| Entry (公開起動契約) | 選択されたComposition/Targetで実DiscoverされたEntry/typed schemaを案内 | Entry表示→Product現在Grant/Artifact収録/実行可能 |
| TriggerDefinition / Occurrence | manual/UI/CLI/Harness/event/schedule/batch別の起動希望と発火事実を区別 | Session Goalや定時通知→実Invocation成功 |
| PreparedInvocation | Productのtyped APIへ対象・input・expected revision・Operation ID・deadlineを**候補**として提出 | AI記述のactor/role/scope/ApprovalをHost Authorityへ変換 |
| Admitted / Started Attempt | Host/Provider実Grant・実Artifact・選択／実Providerの一致・Invocation受理を観測 | 承認要求・ACK・Tool exit→実Run/業務成功 |
| Effect / Result Delivery / Verification | Receipt、結果本文byte、実Consumer読取、業務判定を各Ownerへ照会 | Agent停止/成功発話/Result claim→Commit/Effect/Owner受理 |

**最初の実行縦断はpure/read-only Entry 1件だけ**：TEI #4495の独立Expected EL-01〜12を再利用し、Product直接APIと実CLIの二入口から「公開Entry→型付き要求→実選択Provider→実Output byte」を一つのSource/Toolchain/Attemptで照合する。この試験が成立するまで、YICのHarnessがTEI業務Functionを書込み実行できるというUI表示をしない。Harnessは後段Consumerとして限定Provider Toolを使い、TEI実行正本を持たない。

次に検討する非同期実行は[TEI #4497](https://github.com/hat47x/tei-platform/issues/4497)のTR-01〜12を参照。Goal/Scheduleが追跡・配信するAI Activity、TEI Triggerが要求するEntry、EKI Task/Attemptが担う外部実行を**三つの別系統**として扱う。時差/DST、missed-run、Queue後Grant失効、post-commit時点、Eventの循環、Effect unknownは該当Ownerで検証する。YICにScheduler/Broker/Job Registryを増やさない。

### 7.2 複数View・Pluginの固定対象はProductの資格を引き継ぐ

- [TEI #4515](https://github.com/hat47x/tei-platform/issues/4515)はWorkbench-local **read-only Subject Pinの最小実装**。一時Focusから独立させ、Source/Rootが不明ならunknownとする。
- [TEI #4614](https://github.com/hat47x/tei-platform/issues/4614)はX-TEA三視点の**保存・複数画面でのPin**。Hostへ新しい共有状態を持たせず、呼出側がPin意図を保持する。ページ再起動後もSource変更で失効し、絶対PathやRaw本文を保存しない。**#4515の最小Pinと#4614の持続Pinを別Owner/別段階として実装**。
- [TEI #4611](https://github.com/hat47x/tei-platform/issues/4611)はInspector/Three-viewの「選択Registry→実在Inventory束縛→実Provider Invoke観測」を共通化するProduct課題。Harnessが第二Resolver/Registryを作らず、選択B/実Call A（結果同一）を拒否した**Product Witness**だけを受け取る。
- [TEI #4198](https://github.com/hat47x/tei-platform/issues/4198)ではGraph/AI Chatにおけるpartial tool args・提案Patch・実行承認を分ける研究を保持。YICのWeb Chat表示やStream途中のargsをProductの完全なCommand入力として自動実行しない。UI座標/Graph描画Edge IDをModel identityへ昇格しない。

従って、多View共有のYIC評価は「Product-local Pin Intent→対象の現在再解決→開示Projection→Hostの実Harness Session」で行い、全製品統一Pin保存庫、共通Operation Resolver、認可Coreを要件化しない。

### 7.3 SUI/SHOの原資料、Card、仮説、文章を別のものとして扱う

[SUI #3441](https://github.com/hat47x/sui-sensemaking/issues/3441)は、Raw原文の人間による任意UTF-8 byte range選択→KJ Card→Document Save→別Process再読→**同じ出典箇所への復帰**を既存R2-SRC-01〜08で実証するOwner。既存R0 DocumentV1 Draft #3439／R1 Reference Raw Reader Draft #3440の局所PASSは、実ProductのRoot/Scope/Grantを証明しない。**同文二箇所、同内容別Root、ABA、権限失効、Save 409**を無視しない。

[SUI #3401](https://github.com/hat47x/sui-sensemaking/issues/3401)は情報統合のSource Reference、状況対象/関係/時間、複数View、Scenarioと実作用の非同一性を扱う。Canvas上のCard/Island・AI提案のRelation・未受理の仮説は、TEI Accepted Meaningや実世界の同定結果ではない。YICがSUIから受け取るのは当該Recipientに開示可能な**限定Projectionと出典参照**だけで、Native Raw/Hidden Relation/Source ID/件数からの無断逆生成はしない。

SHOがHandoff Markdownを実Read・保存したことは、元SUI Rawまたは元TEI Subjectを独立再解決した証拠ではない。SHO文書のWriter/保存後ReOpen/OccurrenceはSHOの既存Ownerへ戻し、Product間の任意の同一性をYIC内で補完しない。AI OFFのKJ/文書編集を常に製品比較のB0として保持する。

### 7.4 EKIのTask/Lease/ResultをHarness Tool Eventへ吸収しない

[EKI #829](https://github.com/hat47x/eki-fabric/issues/829)のOwnerが担うTask/Attempt/Lease/Result Claim/Artifact Deliveryについて、YICが見るべき観測は少なくとも(1)Admission、(2)実Lease/Attempt、(3)Result Claim、(4)実Output body/digest、(5)Consumer独立Read、(6)適用対象である場合のみ外部Effectである。ACKだけではBody受領にならず、Agent interruptは実Task cancel/rollbackではない。

[EKI #753](https://github.com/hat47x/eki-fabric/issues/753)のLocal IPC/Connect測定はTransport能力の個別検証で、現時点の実Adapter/Lease/Consumer保証を含まない。M0/MVPでは既存の通信方式を維持し、追加Transportや中央SchedulerをHarness接合のために導入しない。実Egress/Consumer資格は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)と[QH §10](https://github.com/hat47x/tai-pleroma/blob/main/docs/yi-constellation/cross-product-handoff-execution-tickets-2026-11-11.md)へ接続。

## 8. 後続の「一仕事ずつ」の実装順と比較票

**既存Lane A/B（TEI DesktopセルフビルドとTAI #168 G0→G2→H2/H3）を独立P0に維持**したうえで、複合したE2E一発合格を要求せず、以下の小さな後続仕事に切る。各ケースのExpected/Checker/Fixtureは記載したProduct Ownerへ置き、本書に二重実装しない。

| 後続仕事 | 最初の正例・負例 | 既存Owner/終了条件 | 未達の場合 |
| --- | --- | --- | --- |
| J-R：read-only Contextの別View/別Consumer | TEI実SubjectとSUI Raw→Cardを各々独立にSourceから再読、別Root/同byteとPartialを注入 | TEI #4515、SUI #3441、TAI QH-P0（I/R/P/T/C列の実行済み範囲のみ） | Productだけ継続。元Sourceの現在資格が無ければ共有しない |
| J-P：公開pure Entryの起動 | Entry未公開・旧Artifact/Provider B選択A呼出し、missing/null/unfetchedを区別 | TEI #4495 EL-01〜12、#3422のAPI/CLI二入口・実Provider Output | YIC側で代替Launcherを作らず、Product修正へ差戻し |
| J-S：ActivityとNative Live Sessionの別資格 | 新Session Handoffを対照に同Session View/Turn、過去秘密Transcript、二UI同時送信、再接続遅着 | TAI #271/#234 HC-15〜18（Host実ID/受領/Recipientを独立観測） | M1限定Handoff、一操作元のみ。Live再接続/多Writerを成功表示しない |
| J-A：非同期TriggerとEffect unknown | Queue後Grant撤回、重複event、ACK loss、cancel後実作用、Result body欠落 | TEI #4497 TR-01〜12、EKI #829の選択適合Jobのみ | 未受理Operationを開始せず、既存Attempt照会。無条件再実行禁止 |
| J-V：製品価値／自作Loop投資判断 | Product-only、Harness Tool-only、＋Product Skill、必要な場合のみ＋TAI Skill、Adapter/UIのありなしを直交比較 | TAI #422/#234/#488、Task/Model/Source/Host/独立Expected固定 | 改善を示せない層は常時機能化しない。B4内製判断保留 |

### J-Pの検収時に必ず見分けるもの

- **Product API/CLIの結果が同じ**ことと、同一実Providerが選択・ロード・実呼出しされたことは異なる。Providerの実Identity/byteをWitnessで照合する。
- **Tool一覧/Skill説明**と実Loader/Invoke、実HostのGrant/公開Entry/実Provider実行は異なる。Unknown・unsupported・permission-deniedを成功やdefaultに置換しない。
- **実数値Output**と業務意味の受理、業務書込み/DB Effect、Owner受理は異なる。pure computationの成功をProtected Writeへ外挿しない。
- **Harnessから製品を起動できる**ことと、YICが独自Agent Loopを持つ必要があることは異なる。ProductのEntry/typed APIが不足する場合、その不足をB4の根拠に数えない。

### J-V評価で記録する実務指標

正しく確認されたTarget割合、誤対象への自動反映件数、独立根拠付きで完了した仕事数、正しく残したUnknown、実Handoff Consumer受領、Session再説明回数、失われた出典、Undo/人の再検証工数、Tool/Skill実Call、Input/Output Token、定額枠と実課金の区別、待ち時間、失敗・再試行、OS/Network隔離の失敗を**分離して記録**する。多数Agent/多Worktreeを比較する場合はSource/branch/変更path/独立ReviewのOwnerを固定し、異なるLaneのCI結果や同じExpectedを重複母数にしない。契約/API互換だけで他サービスのサブスクリプション枠を転用可能とみなさない。

## 9. 採否への帰結と今回の証拠上限

この横断照合が支持するのは、**「既存Harness + Product Tool/Skill + 必要最小のActivity Handoff/Adapter/統合UI」を優先し、Agent Loop自作は未受理のままにする**という実装順である。

独自Loopを再審査するには、TAI #234の既定条件どおり、互いに独立した代表Harnessの適格実試行、Product Entry/Projection/Host/Adapterでは埋まらない重大欠落、保守・運用・費用・移行・撤退の実負担、Owner正式判断が必要。Target/Raw/Grant・Evidenceの正本をYICに移さない。

**今回の新規実施範囲**：既存Issue/Sourceに記載された限定実績の静的照合と本計画の追補のみ。J-R/J-P/J-S/J-A/J-Vの新しいE2E試行、TAI #168の4比較適格（直近0/4）、TEI #4495の実pure Entry縦断、SUI #3441 Product R2、EKI #829 Task/Result実受領、複数UI Session共有、TEI #4583 Stage1→Stage2 Desktop完全再入、Owner受理は**NOT RUN**。局所CI/PASS・Issue起票・Draft PR作成を横断合格に読み替えない。


## 10. 2026-11-14追補：Skill起動判断を三つの依存閉包に分ける

[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488)と[Draft #633](https://github.com/hat47x/tai-pleroma/pull/633)、[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)の既存判断を受け、**J-R/J-P/J-Sを実際の「必要時Skill呼出し」に接合する前の検証順**を明確化する。新しいSkill Schema/Runner/Loader/共通許可エンジンではなく、**既存Runbookに記録すべき別々の依存**とする。宣言の一致・配送・実呼出し・現在の利用資格を同一のPASSと扱わない。

| 閉包（評価の観点） | Product/Hostの既存Ownerに確認する実体 | 不適格・不明ならどうするか |
| --- | --- | --- |
| **I：Instruction/Package** | Product Skillの選択されたentry、本文だけでなく参照ファイル/Script/必要Tool宣言、実Skill Loaderから見たbyte/digest・版・実Load、実Modelに提示された範囲 | Skillの名称/説明・ディレクトリ存在を実Loadと呼ばない。参照だけ古ければ当該Skill利用資格を止める。Tool-onlyが合法なら継続 |
| **S：Subject/Information** | Productが今再解決したRoot/Origin/Subject/Occurrence、必要なSource・Required/Consumed/取得範囲、時点・単位・粒度・unknown/partial/permission、否定Claimの集合閉包 | Index 0件・同byte別Root・同ModelRevision・未取得を「存在しない」「未使用」「同じ対象」と断言しない。意図は保持し、該当Claimを選択的に再Read |
| **C：Capability/Authority** | 当該Targetに実収録されたArtifact/Entry/Provider、実Tool schema/CLI、選択版と実Invoker/子exe、現在Host/OS/Network Grant、RecipientへのDisclosure、Tool Reply終端、独立Consumer read | 署名/登録/Capability宣言だけで現在利用を許さない。Hostが実Call拒否なら再発見または安全に縮退し、別Tool・広い権限へ黙って切替えない |

**適用順**：Jobの意図とProduct-local Pinの確認 → 必要なInformation/Sourceを今再解決 → Product-only/Tool-onlyで足りるか判断 → 不足する能力がある場合に限り選択SkillのInstruction closureを確認 → 現HostのCapability/Authorityで実Load/Invoke → Tool結果の完全受領とClaim別の現在資格を確認する。これは一律の起動フローを全Jobへ強制しない。純粋read-onlyではEffectは適用外でよい。

**Claimに相対的な再資格化**：歴史観測H、現在の用途に使える資格U、今回の実Attempt Aは別。Source A→B→A、同Tool名の参照Scriptだけ変更、実Root存在差、Audience撤回、Required集合の追加/削除、Providerの選択と実Callの不一致を、それぞれ影響するClaim/Read/Skill/Operationにだけ再検証する。履歴を消さず、古いGrantを回復したとみなさない。依存線の閉包が不明なら「無影響」ではなくunknownを残す。全てのProduct Skillを同時に読ませたり、1件の変更で全Activityを一律失効させたりしない。

**実装境界**：IはSkill Loader/配布元、SはTEI/SUI/SHO/SEI等のProduct Reader、CはTEI Plugin/Entry・Host/EKI・外部Harnessの実Tool受領に根拠を置く。TAI/YICはそれらを参照するだけで、ProductのSource/Policy/Authority/EffectやSkillの第二正本を作らない。TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)の初回H2/H3四SlotのSkill byte、Task、Tool profile、G0〜G2先行条件は変更しない。

### 10.1 独立試験の再利用先（新しいExpected票を起こさない）

| 最小反例 | 既存試験のOwner | 判別すべきClaim |
| --- | --- | --- |
| Skill本文は同じだが参照Script/Tool schemaが改版、Loaderが一部のみ読んだ | TAI #488 X01〜X03、TEI #2605、TAI #168 H3 | Packageの部分的Loadと実Provider利用を分ける。Skill紹介文から実Closureを捏造しない |
| Sourceは同じdigestだが別Root、あるいはSourceIndex 0件・Reader validationのみ変更 | TEI #4515/#4616/#4577、TAI #271 | Pin意図・Subject存在・現在Validation/対象集合のClosed Worldを区別 |
| Product Toolを発見したが実Provider未収録、Tool結果が8192Bで切れた | TEI #4495 EL-01〜12、TAI #168 G2、TAI QH §10 | Tool discover/selected/loaded/invoked/delivered/consumedを別々に観測 |
| 過去SessionのTool/ReceiptをB側へコピー、現在Grant/Recipientを撤回 | TAI #271/#234 HC-03/05/13、SHO #47、TAI #640 | 実Session、現在Disclosure、同一Attempt・独立Consumerを拒否点まで追う |
| AIの回答が正しいがEvidenceがない、または本当は根拠付きの局所Claimを全拒否 | TAI #621 §14.7 D0〜D3、Draft #585 | 誤昇格だけでなく過剰保留も計測する |

## 11. J-Vの比較を「Packetの価値」と「Skillの価値」に分離する

[TAI Draft #621 §14.5〜14.7](https://github.com/hat47x/tai-pleroma/pull/621)・[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488)を**唯一の評価Owner**とし、本書は後続J-Vに必要な前提条件・観測先の索引を示す。

- **M00**：新SessionにActivity Packetなし／TAI Skillなし。**M10**：同じ許可済みPacketあり／Skillなし。**M01**：Packetなし／Skillあり。**M11**：M10と同一byte Packetあり／Skillあり。
- **Packetだけの効果**はM10−M00、**Packet条件を固定したTAI Skillの増分**はM11−M10、Skill単独の効果はM01−M00として、同じ公開TEI/SEI Source・実CLI・モデル/Tool/Host条件・独立Expectedで比較する。初回のW0/W1×4セルは「8条件」であり8独立反復ではない。Trialの途中でSkill byte/World/Tool・別Root/Targetを変えない。
- 最初のSEI `rec-1`（TAI merged #647）は**版・SourceのBasisが無い**ため、Skillなしでも正しく「未確認」と回答できたn=1の観測。これ単独では**根拠が現在有効な場合に限定再利用できるか**を識別できない。既存[TAI Draft #585](https://github.com/hat47x/tai-pleroma/pull/585)を使い、D0＝Basis欠落、D1＝有効Basis/局所不変、D2＝意味/依存変更、D3＝非意味的変更/対象外Validation不備を**試験前に固定**し、過剰保留と偽再利用を両方採点する。
- Packetの生成/Redaction/送達/現在Source再確認/修復にかかる人手・Token・時間・失敗を**再開後の便益から隠さない**。Tool/Cost低減と秘密漏洩/誤対象/旧Grantの偽継承を一つの点数で相殺しない。全割当Attempt（ITT）と事前に資格を満たしたAttempt（PP）を別集計し、Skillの自己申告で実Load/利用を認定しない。
- **撤退条件**：M10で足り、M11の独立反復で用途上の改善がなければ、YICはTool-only＋限定Handoffを標準候補とする。改善が実証された特定JobだけProduct Skill/TAI Skillを追加する。モデル名/提供者の違いをSkill追加の効果と混同しない。

このJ-Vは外部DSH H2/H3の**Skill Load比較資格**そのものではなく、後続の活動継続・便益の実験である。TAI #168のG0 OS Read-deny→G1 Egress→G2 Tool Reply→新規独立H2→H3→H3→H2（現0/4）を先に進め、比較適格0/4を変更しない。YICの独自Agent Loop内製への投資判断はTAI #234の既定条件に残す。

## 12. 新しいProduct実証を計画へ接続する際のClaim上限

- **TEI Builder pin（2026-11-14最新）**：[Draft #4623](https://github.com/hat47x/tei-platform/pull/4623) HEAD f1e219a25976946bcc8a19ef57f5490333ec8a84で、Caller指定Digestの起動前検査に加え、opt-inのBuildIntent.Resolve／Catalog選択Builder Digestを実子exeの起動前照合へ渡す経路を追加。当該HEADのGitHub Actions **8/8 completed/success**（[Self-build #43539856841](https://github.com/hat47x/tei-platform/actions/runs/43539856841)、[Health #43539856799](https://github.com/hat47x/tei-platform/actions/runs/43539856799)等）を確認した。選択不一致による子起動前拒否は局所成果。ただしCatalogの意味・現在権限／N0～N3の非Plugin ArtifactSet・実工程／完全なRead時依存／OS Loader TOCTOU／**生成Stage1→Stage2 DesktopとStage2 WebView2**は未受入。別HEADの[Desktop Draft #4587](https://github.com/hat47x/tei-platform/pull/4587)の過去Windows Greenと合算しない。TEI #4583のOwnerへ返し、TAIにBuilderを作らない。
- **SUI段階実証**：[SUI Draft #3442](https://github.com/hat47x/sui-sensemaking/pull/3442)のIG0 AI OFF→IG1 Raw/人手範囲→Card保存・原文復帰→IG2二資料→IG3構造化Source/時間→IG4複数View→IG5 Loss付きSHO Consumer→IG6実務価値の順はSUI Owner。AI OFFのIG0/IG1を外部Harness必須にしない。Card occurrence/原文/現在Source資格は保持し、情報が投影で失われた場合の全件・同一性・意味受理を捏造しない。
- **Product Plugin Obligations**：[TEI Draft #4620](https://github.com/hat47x/tei-platform/pull/4620)はContract/Role、exact Selection、Build Inclusion、actual Invocation、Current Grant/Effect、Consumerの区別をStudio主線へ統合するDocs-only案。J-PのEntry/Provider実証に必要なProduct側の意味・ObligationはTEI #951/#1016/#1251/#1129/#1174/#4611で判定し、YICがGraph Compilerや新Hostを設けない。
- **現状**：本追補はDocs-only案。#4623 f1e219aの既存CI 8/8 successは限定確認済み。一方、SUI IG1〜IG6製品E2E、J-V 4セルの実比較、Skill三閉包の実Trial、Live二UI Session、TEIの正式Desktopセルフビルド、H2/H3四適格Slotは**NOT RUN/NOT OBSERVED**。各HEADと各Ownerの試験を合算しない。


## 13. Goal・Schedule・Sessionの再開を独立受入する

### 13.1 外部Harnessの公開仕様から確かめた差分

前章のNative Session/ViewとProduct Applyの区分を、代表Harnessの公開仕様へ接続する。ただし下表は**公開文書に記載されたCapability**であり、YICが実使用するHost/Version/Profileでの実動作保証ではない。

| 参照する公開実装 | 文書上の意味 | 混同を禁止するClaim |
| --- | --- | --- |
| [DSH Goal](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/goal/goal/README.md) | Objective、phase、revision、round countはSession Logへ保存。Session resume/fork/process restart後は、activeでも**継続許可のarmed状態は復元しない**。明示的なrearmが必要。 | 永続Goalのactive状態≠次Turn実開始≠実作業完了。Goalのround上限・blockedも別 |
| [DSH Schedule](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/schedule.md) | Hostが保存したTaskを期日にSession Inboxへ配送。Host停止中は実行できず、再起動時に期限超過を処理。配送記録は実Model受領・結果ではない。Crash時の重複・配送記録があっても未消費の可能性がある。 | Schedule due≠Inbox保存≠Model実受信≠Tool Invoke≠Product Effect。Exactly-onceを推定しない |
| [Codex App Server](https://learn.chatgpt.com/docs/app-server) | Thread/Turn/Item、履歴ページ読取、thread/start・resume・forkを提供。fork後のThread IDは異なってもrootのsessionIdを共有し得る。 | 同じsessionId≠同じLive Thread、同じWriter、同じAudience。forkを多UI同時制御と呼ばない |
| [Claude Agent SDK](https://platform.claude.com/cookbook/claude-agent-sdk-04-migrating-from-openai-agents-sdk) | resumeに使うSession記録はローカルディスクに保存。新Processで再開できても別Machineで自動共有されない。 | ローカル再開≠ネットワーク共有≠閲覧権限の移転。Managed Agentsの別Hosted APIと混同しない |

評価票にはHarness/実Version/Host/Process、Native Thread IDとfork関係、Goal phaseとarmed、Schedule Task/Delivery、Turn/Tool実Event、元Product Attemptを**観測できた範囲で別欄**に残す。この区分は評価のためのもので、共通Session ID/Schema/Storeは作らない。

### 13.2 後続に置く三つの実Probe（新しいExpected正本は作らない）

| ProbeとOwner | 最小操作・独立観測 | 認める結果と縮退 |
| --- | --- | --- |
| **Resume / Fork**：TAI #234 HC-06/10/17、#271 ASV-03 | 公開read-only Goalを設定→Pause/Host停止→実Resumeまたはfork。明示再許可の前後でGoal phase、実Turn/Toolを別観測。Codexならroot sessionIdと実Thread IDを別記。 | 状態復元だけで自動継続PASSとしない。現在Recipient/履歴範囲を再確認できなければActivity限定Handoffから新Sessionへ |
| **Scheduled Job**：TAI #234 HC-06/18、TEI #4497 TR-05/07、EKI #829 | 公開read-onlyの1 JobについてTask保存→期日→Inbox→Model受領→Tool実処理→Product Consumerを段階観測。Host停止/ACK喪失/再送も注入。 | 配送Receiptから完了を捏造しない。結果不明ならProductの元Operation/Attemptを照会し、勝手に新IDで再実行しない |
| **二つのUI**：TAI #234 HC-15/16/17、#271 ASV-02/04 | UI AでSource公開ContextのSessionを作成し、UI Bで閲覧/Turn候補。Audience差、履歴Tool Result、別Root、遅い旧Replyを注入。 | 新規Projection許可と過去Transcript開示資格を別判定。Native同時Writer保証がなければ閲覧限定または新Session。元Pin以外への自動反映0 |

**実施順と非採用**：本ProbeはTAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)のG0実OS Read-deny→G1実Egress→G2全Tool Reply→独立H2/H3四Slot（比較適格0/4）の**後続**。TEI #4583のセルフビルドも独立P0。既存HarnessのGoal/Session/Schedule＋Product Typed Application API＋許可Handoff v1で用途を満たす間は、YIC独自の常駐Agent Loop、中央Scheduler、Session DB、分散Lock、第二Authorityを導入しない。

**状態**：公開公式資料照合と既存Ownerへの受入手順の接続だけ。DSH再起動、Codex fork、Claude SDK再開、実二UI、Tool受領、Product実作用は本追補ではすべて**NOT RUN**。


## 14. Product Adapterの受渡し：Capability宣言と実行資格の間の具体的な二辺

本節は[TEI Draft #4624](https://github.com/hat47x/tei-platform/pull/4624)（BuildIntent宣言とResolver回答の一致）、[TEI Draft #4625](https://github.com/hat47x/tei-platform/pull/4625)（REA保存Evidenceの実CLI入口）、既存[TEI #3422](https://github.com/hat47x/tei-platform/issues/3422)（CLI/Web/Desktop/IPC共通Application操作境界）、[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)（機密開示）をJ-R/J-Pに**既存Product Ownerのまま**接続する。YIC用の第二Resolver/Reader/Host/CLI/Authorityは作らない。

### 14.1 宣言→選択→実到達のClaimを実装途中で混ぜない

- **宣言とResolver回答の整合**：TEI #4624のDraft HEAD `2d403f4996c205514dc57d5fc1237127c6bd994b`ではSource Kind/ID、Builder Contract/major・明示Provider/Implementation・Artifact pin/Pinned、Dependency Kind/ID/majorについて、宣言と異なるResolver応答を拒否する。**確認したGitHub Actions 5/5 completed/success**、PR本文にLinux focused/race・Windows GoとNode20件の局所結果。ただし**Resolver整合≠受理済み意味≠実Builder Invoke≠完全Read Closure/Stage2**。同HEADの実験範囲だけを証拠にする。
- **選択と実Invokerの整合**：TEI #4623 HEAD `f1e219a`の**8/8 CI success**は、opt-inのBuildIntent ResolveによるBuilder digest→実Child開始前SHA一致・不一致拒否までの局所証拠。#4624と#4623の別HEAD Greenを**統合End-to-End PASSに合算しない**。共通ResolverとLauncherを同じ実Build Attemptで接続し、非Plugin N0/N2/N3・ArtifactSetの実Consumed byteを別に確認するのは[TEI #4583](https://github.com/hat47x/tei-platform/issues/4583)のP0。
- **実CLI読取りの到達**：[TEI Draft #4625](https://github.com/hat47x/tei-platform/pull/4625) は既存`operations.ExternalCandidates`を呼ぶ `tei external-candidates` のローカルread-only入口。実CLIバイナリをGoでbuildし子Processで実行するテストを含む。`evidence-path`/producer Tool version/Observation ID/Directed Relation ID、および任意のEvidence ID・Received Digest・Source Revision pinを使う。正例では選択対象だけでなく**Unselected、Coverage unknown、AuthorityLimits**も落とさない。外部のREA実Processを再実行するのではなく、保存されたEvidenceを解釈する入口である。
- **実ローカルPathの禁止境界**：#4625は意図的なlocal-file CLI。ローカルPathをStudio Webや遠隔MCP/別Userの自由入力へそのまま渡さない。失敗時診断が内部Pathを含む可能性、`rea`の`Present`が実producer起動証拠でないこと、Digestが同じでもSource Scope/現在Grant/意味受理でないことを保持。[TEI #3394](https://github.com/hat47x/tei-platform/issues/3394) R3-Bでは**Product/Hostが許可済みbyteを取得**するReaderを、R3-Cでは別Consumer実Readを独立に検収する。

### 14.2 最初のYIC読取り協業の実行カード（既存Expected/Fixtureを利用）

| 手順 | 実行・記録の最小単位 | 合否を決める既存Owner |
| --- | --- | --- |
| **P-A Discovery** | Product `tei commands`で実存在を確認。実バイナリ/Tool version/CLI envelopeと`external-candidates`の実Responseを保持 | TEI #4625 R3-A／#3422。DiscoverだけでCLI Invocation PASSとしない |
| **P-B Product-local Reader** | Productが許可した一つの保存Evidenceを、実CLI子ProcessでObservation/Relation ID・pin一致・unknown/unselectedを含めRead | TEI #3394 R3-A。原REA観測時刻と現在Read時刻、byte/raw digestとScopeを区別 |
| **P-C Host boundary** | 外部Harnessへ生Path/原Evidence/内部Errorを直接与えず、Hostが選択済みProjectionだけを開示。秘密または許可不明では拒否・ローカル閲覧のみ | TEI #3394 R3-B／TAI #232 C0～C3・#168 G0～G2。新YIC Readerなし |
| **P-D Handoff consumer** | 現行`yi.handoff.context/v1`に許可済み参照・unknownを限定送出→別Productが**自身のReader**で現在資格を再確認 | TAI QH §10／TEI #3394 R3-C／SHO既存Owner。Receipt replay/見かけの一致では不可 |

**拒否の焦点**：Path traversal・別Root同内容・古いSourceRevision・同名異Evidence、Source存在不明、Relation ID/向き混同、`Coverage unknown`→全件肯定、内部Pathがエラーへ漏れるケース。P-Cは実OS Read-deny/egress資格がない環境では合格にしない。局所CLI成功を公開Remote Tool適格性へ昇格しない。

## 15. DesktopとWeb版の協業境界：同じUI構成でも同じ作業単位ではない

他チャットの[TEI Studio GUI/Web版の構想]を、既存[TEI #1824](https://github.com/hat47x/tei-platform/issues/1824)のWails共通UI/Go Service/接続分離と、[TEI #3422](https://github.com/hat47x/tei-platform/issues/3422)共通Application APIの**後続圧力ケース**として扱う。Webチーム開発の採用済み実装を主張するものではなく、最優先[TEI #4583](https://github.com/hat47x/tei-platform/issues/4583) DesktopセルフビルドのHard Gateに追加しない。

| 意味の単位 | Desktop（既定：独立ローカル開発→Git共有） | 将来Web（候補：単一またはHA開発Server上の共同開発） | YICの境界 |
| --- | --- | --- | --- |
| Workspace/Source | ローカルRoot/Worktree/Branchと実Binary、個人の保存・Commit | Server上の共同Workspaceと共有Revision、複数Userの同時保存・競合 | **同じRepoや同じ画面名≠同じSource Snapshot**。Workspace identity/Revisionの調停はTEI側 |
| Viewer/Audience | Desktop使用者＋選択した外部Harness Recipient | 利用者ごとにログインSession・Tenant/Team・Grant/Disclosureが異なる | 同じ共同Workspace≠同じTranscript閲覧資格。過去Prompt/Tool履歴は再開時に別審査 |
| AI Session/Turn | 外部Harness Native Sessionまたは限定Activity Handoff | 複数User/Browser Tabが同じActivityを見ても、同じLive Native Turnを書けるとは限らない | NativeのWriter/Turn起源が不確定なら一Writer・他は閲覧限定、または新Session |
| Product Operation | 個人がPreview/Pin/typed APIを操作し、保存/Build/Commitの実Attemptを観測 | 共有Sourceへ複数の編集意図、If-Match/CAS競合、他者更新・Grant撤回 | Agent Resultと本番保存/Build/Effectは別。Apply直前にProductが現在Version/Grant再検査 |
| Build/Artifact | ローカルGo/Wails実行とStage1→Stage2のNative証拠 | ServerのJob/Artifact/Host運用は別配備。結果の表示はClient | Web Server内のBuild成功をWindows Desktop Stage2セルフビルドへ流用しない |

**共通UIの実装方針**：Product意味/型付き操作・モデルのSource identityは共有し、表示・Projection・Interaction componentを可能な限り共通化。DesktopではWails IPC、WebではHostが許可したAdapterを選び、**Client UIが直接Host CredentialやRaw Pathを生成しない**。新しいYIC Webサーバ、Session Registry、Lock、共同編集Engine、常駐Agent Loopを先行設計しない。共同SourceのCAS/CRDT/Git運用方式は実際の同時編集要求と[TEI #1824](https://github.com/hat47x/tei-platform/issues/1824) Owner判断へ残す。

**後続最小の四反例**（既存TEI #3422 T08～T13、TAI #234 HC-15～18／TAI #271 ASV-02～07に割り当て、新Oracle/試験Harnessは作らない）：

1. 同一Web Workspaceを共有する2 Userの可視Projectionは一致、過去Harness Transcriptには非公開Tool結果を含む。**新AudienceのView権限だけでは過去Transcript全文を返さない**。
2. 旧Workspace/旧Source RevisionでAgentが変更案を生成中に他Userが保存。画面上は同じSubject IDでも、Apply前にTEI現在Version/必要Grantを照合し、staleなら**Draftは保持・Commit 0**。
3. 二つのBrowser Tabが同時Turnを送る。Nativeが実Turn ordering/actor帰属を証明できない場合は**View-only・新Session縮退**、UI-local mutexをCross-Host Lockと偽らない。
4. Browser切断・再接続と同時に非冪等Operationが進行する。Turn cancel、Session閉鎖、HTTP ACK lossを実Effect/rollbackへ変換しない。元Operation ID/AttemptをProductで照会し、unknownのまま無条件再送しない。

**設計採否**：TEI Studio Web共同作業は将来のProduct受入課題であり、初回YIC H2/H3（0/4）やStage1→Stage2 Desktopをブロックしない。YICが提供する価値は複数画面における限定選択・Activity継続・履歴開示と実操作の透明性であって、Git履歴／共有Workspaceの正本やAgent Loopの中央運用権限ではない。

## 16. 今回の統合変更・未成立の証拠

本節までの§14～15は**Product Owner実装PR・Issueおよび他チャット設計を照合した受入計画の追加**。#4624の既存Workflow 5/5 completed/successは確認したHEADだけの事実。#4625の確認時HEAD `aa86e15e7cf1978d505303151bb6d3b765006a2c`はGitHub Actions **9件中7件completed/success、2件in_progress**であり、本Draftはそれらの結果を追認する実試験ではない。

**NOT RUN/NOT ACCEPTED**：#4624と#4623を同一Desktop Attemptで接続した受入、#4625外部Harness公開利用・Host限定Byte取得・SHO第二Consumer、Webチーム同時編集/権限撤回/旧Reply、TAI #168 G0～G2およびH2/H3新4 Slot（現在比較適格0/4）、TEI #4583 B2/B3 Windows Stage2実行、業務書込み/Owner意味受理。

**次の着手は二つの既存P0を維持**：TEI #4583 Builder/非Plugin ArtifactSet→Stage2 WebView2、TAI #168実OS隔離→送出→完全Reply→独立4 Slot。P-A～P-DとWeb反例は後続のread-only横断実験であり、先行条件を無断で増やさない。新共通API、Egress代替、Session Server、Plugin/Skill Registry、第二受理正本、TEI独自Host、Native Agent Loopの開発判断を本Draftでは行わない。

<!-- yic-harness-web-wasm-substrate-and-port-20261114 -->
## 17. Web/Desktop共通Core・WASMの責務境界（2026-11-14設計候補／実装NOT RUN）

### Wailsの共有可能範囲
Wails v3はDesktopではGo native backend＋OS WebView＋Native Bridgeを用い、Web配信用Server Buildも提供する。したがって「Web版にもWails」を**Go ApplicationとUI資産の再利用**として検討するが、通常ブラウザーでDesktop WebView IPCをそのまま使えるとは扱わない。公式参照：[Technical Overview](https://v3.wails.io/contributing/overview/)／[Architecture](https://v3.wails.io/contributing/architecture/)／[FAQ](https://v3.wails.io/faq/)。

| 状態・処理 | Desktop | Web | Owner/共有範囲 |
| --- | --- | --- | --- |
| UI View/Focus/一時Draft | TypeScript in WebView | TypeScript in Browser | UI部品は共用。Focusを意味的Pinと混同しない |
| Product Action/Current Source/Grant | Wails Bridge→Go Application | AuthZ付きWeb transport→Go Application | TEI #3422の型付きApplication API。Goが正本、transportは別 |
| Activity/用途限定Handoff | Product UIの参照 | Product UIの参照 | TAI #271。Native Session IDと別 |
| Harness Session/Turn/Tool Event | Host側Native Adapter | 実到達可能なHost側Adapter | Native実ID、閲覧Audience、Writerを検証。新Session Storeなし |
| Build/Provider/Effect | 実OS Process/Artifact | 実Server Process/Artifact | Product/Host Ownerの実Attempt。Desktop Stage1→Stage2とWeb Jobは別証拠 |

**WASMは必須共通Runtimeではない。** 同一データから同一結果を得る純粋な検証・型変換・Graph/差分処理・表示補助についてのみ、TypeScript処理／Go native service／Go→WASM実装を比較する。Source/Grant/Disclosure、秘密のHost Credential、外部Harnessの実操作、Build/EffectはWASMの権威にしない。Client計算値は候補であり、Productの現在確認を置換しない。

採否は起動・download byte・Memory・編集直後の応答・Buildサイズ・実SourceとNULL/Bag/同名多重Relation/ABAの挙動一致・debug負担を**同一Fixture・独立Expected**で比べた後とする。初回のTEI Studio Desktop SelfBuild [#4583](https://github.com/hat47x/tei-platform/issues/4583)に新Hard Gateを追加しない。決定Ownerは[TEI #1824](https://github.com/hat47x/tei-platform/issues/1824)/[#3422](https://github.com/hat47x/tei-platform/issues/3422)。

### Stateとイベント帰属
一時Focus、Pinned Target intent、Product Source identity/current Revision、Activity、Native Session/Thread/Turn、Product Operation/Attemptは独立した概念。Web同一Workspace・同じSessionの表示・同一Model Revisionを、現在Grant/Transcript閲覧許可/Sourceの連続同一性の根拠としない。Streamの遅着・欠落・別UIでの受信時も、実Native IDと元Pin/Activity/Attemptを対応づけ、確定不能なら候補保留／unknownとする。Productへの自動Applyは行わない。

## 18. 薄いHarness Adapterを実装するための最小受渡し（計画／NOT RUN）

本節の名前は設計用の説明語彙であり、全Harnessに実装を要求する新共通ABI/Registry/Runnerではない。既存TAI #168/#234 HC-01〜18/#271、Draft #648 §§3–16の実証とOwnerを再利用する。

| Adapter操作候補 | 観測しなければならないこと | 縮退・禁止する推論 |
| --- | --- | --- |
| Capability Probe | Native仕様、実Host/Provider/Model/Profile、現在read/session/stream/interrupt可否 | 公開APIの存在から実資格を推定しない。unknown/unsupportedを残す |
| Open/Resume/Fork | 実Session/Thread ID、fork関係、Audience、履歴の開示範囲 | Live継続不可ならTAI Activityから新Sessionへ限定Handoff。過去Grant/Transcriptは移さない |
| Context Delivery | Product許可Projection、Prepared/Actual Delivered、実受領、送出範囲 | Modelが理解した証拠にはしない。Raw Path・秘密資料は送り込まない |
| Turn/Event/Interrupt | Native Turn/Tool ID、欠落/切断/順序、操作元、cancel受領 | UI局所queueは別端末のWriter排他ではない。InterruptはBuild/Effect取消の証拠ではない |
| Candidate Return | 元Pin、Source/Revision、Activity参照、AI候補の実到着 | Productが現在再資格化してPreviewへ渡す。回答=Apply/Owner受理ではない |

**実装・受入の順序（既存計画を置換しない）**
1. **独立P0-A** TEI #4583：Builder→実Child→Stage1→Stage2→WebView2の同一Attempt検証。別HEADの成功を合算しない。
2. **独立P0-B** TAI #168：G0物理Read-deny→G1実送出→G2完全Tool Reply→独立H2/H3 4 Slot（現適格0/4）。Session UI/WASMを追加Blockingにしない。
3. **後続J-R/J-P** TEI #4515のSubject Pin、#4625局所read-only CLI、#3394 Host許可Projectionから、各ProductのReaderと実Consumerを照合する。
4. **後続J-S** DSHでActivity→Native Sessionの限定閲覧/Resumeを実験し、HC-15〜18で履歴開示、別UI同時Turn、遅着、Interrupt後のOperationを検査する。Native未対応なら閲覧限定/新Sessionへ縮退。
5. **後続J-V** B0 Product-only、B1 Tool/Skill、B2 Adapter、B3統合UIを同じ公開Task/Source/Disclosure/独立Expectedで比較。別Harnessを追加してProduct Coreが変わるならAdapter境界の失敗として記録。B4独自LoopはB0〜B3で解消不能な実測欠落がある場合のみ再検討。

**反証と停止線**：同名別Workspace、Source A→B→A、Rev同一でもGrant変更、履歴への過剰開示、8KiBで切れたTool Reply、並行Turn/二重Writer、Interrupt後の実Build/Effect不明。合格不能な機能はunsupported/unknown/NOT RUNとして示す。Claim、Tool exit、実Consumer、Host Effect、Owner意味受理を分離し、実験を増やすための第二Authority/Agent Loop/Source Storeは作らない。

**今回の資格**：Wails公式資料と既存Product/TAI計画の照合を追加したDocs-only追補。Go/WASMベンチマーク、実Web共同開発、実二Harness互換、4 Slot新比較、Stage2 Desktop実合格、Owner正式受理はいずれもNOT RUN。


## 19. 並行Draftの収束：実装Owner・統合順序・レビュー条件（2026-11-14）

これまでの議論を新しい標準Schemaや第三の総合文書として統合せず、**既存Draftの責務・正本・採否順序**として再整理する。2026-11-14照合時のGitHub Compare `main...PR head` は、TAI #629がahead 13/behind 18（1ファイル）、#633がahead 29/behind 16（2ファイル）、#621がahead 26/behind 39（2ファイル）、本#648がahead 6/behind 0（新規1ファイル）。すべてOpen Draft／未マージ・当該確認時はmergeable。**異なるファイルであることと、Owner受理／意味整合／今後の無競合統合は別**。

| 統合対象の実Owner | 確定的に残す範囲・参照する唯一の編集先 | 他Draftから持ち込まずに参照すること |
| --- | --- | --- |
| [TAI #629](https://github.com/hat47x/tai-pleroma/pull/629) | Product-local Q/E/A集合、Subject Pin意図、Qualified Source/根拠・Selection再資格。[Interop計画](https://github.com/hat47x/tai-pleroma/blob/docs/shared-harness-selection-requalification-20261112/docs/yi-constellation/harness-skills-interoperability-and-evidence-2026-11-02.md)を正本候補とする | #648のSession接続やWeb Focusを第二Resolver・Global Pin Storeにしない |
| [TAI #633](https://github.com/hat47x/tai-pleroma/pull/633) | Tool-only→必要なProduct Skill→TAI Skill、Product実Handoff/Consumer、Skill三閉包、CLI/Desktop/Webへの適格性。既存[Skill計画 §48〜50](https://github.com/hat47x/tai-pleroma/blob/docs/yic-pinned-handoff-main-reconcile-20261112/docs/yi-constellation/harness-skill-plugin-plan-2026-11-02.md)を実装順の正本候補とする | #648 §17/18のAdapter候補をSkill必須Loaderや全環境共通Host ABIにしない |
| [TAI #621](https://github.com/hat47x/tai-pleroma/pull/621) | Activity引継ぎの価値、Packet×Skill 2×2、D0〜D3の肯定/否定、全Lifecycle工数とITT/PPの判別。[Crossview ReaderとRoadmap](https://github.com/hat47x/tai-pleroma/pull/621)を評価の正本候補とする | #648のM0〜M4 Adapter段階とM00/M10/M01/M11モデル試験を混同しない。初回H2/H3四Slotの母数にも加えない |
| **本[TAI #648](https://github.com/hat47x/tai-pleroma/pull/648)** | Activity≠Native Session≠Product Attempt、二UI接続の履歴開示・Turn帰属・縮退、TEI Studio Desktop/Web/WASMの**評価上の境界**、read-only Product→Host→Consumerの後続試験順。本書は**接合の読解・受入計画** | Pin/Skill/Source/実Build/現Grant/独立Expectedの実装正本を本書へ移さない |

### 19.1 マージ順ではなく、受入に必要な証拠の依存順を固定する

- **P0-A（TEI製品）**：[TEI #4583](https://github.com/hat47x/tei-platform/issues/4583) のBuilderの宣言→Resolver回答→選択実Invoker→非Plugin ArtifactSet実Read→生成Stage1→Stage2 Windows Desktop→そのStage2 WebView2。既存[TEI Draft #4624](https://github.com/hat47x/tei-platform/pull/4624)（Resolver整合、限定CI）、[#4623](https://github.com/hat47x/tei-platform/pull/4623)（pre-start child pin、別HEAD限定CI）、[#4587](https://github.com/hat47x/tei-platform/pull/4587)（過去Windows B0/primitive N0）は別Attempt。**三つのGreenを一つのL3成功に足さない**。TEI独自Host・YIC Build Engineは新設しない。
- **P0-B（TAI実Harness）**：[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) 実OS禁止Read／Egress／完全Tool Reply→事前割付の独立H2/H3四Slot（現0/4）。WASM・SUI Canvas・複数UI・Native forkを初回Hard Gateへ加えない。
- **後続read-only**：Product Source/Root/Subjectを実Read→Pinの現在性→Tool-only→必要時Skill→Host許可Projection→既存Handoff v1→実Consumer再Read。TEI [#4625](https://github.com/hat47x/tei-platform/pull/4625) のREA `external-candidates`は**local Pathを受けるCLI**の限定候補であり、Studio Webや外部Harnessに任意Pathを公開するToolにはしない。R3-B/Cは[TEI #3394](https://github.com/hat47x/tei-platform/issues/3394)／QH §10の別Consumer資格。
- **後続ユーザー価値**：Native SessionのView-only・一Writer・限定Packet新Session縮退の実測をTAI #234 HC-15〜18/#271 ASVへ委譲。その後TAI #621/#488の同Source・同HostでPacket単独とSkill増分の仕事単位比較を実行。再説明、誤対象、根拠喪失、過剰保留、開示違反、Undo・作成・再資格化・配送費用を別々に記録する。

### 19.2 Draft統合時のレビューチェック（共通の実行器ではない）

1. **差分再確認**：各PRのhead SHAとその時点の`main`を比較し、重複段落や並行追記、他Branchの成功を写し込んでいないか確認。#621/#629/#633にはbehindがあるので、古いmainの段落を復元せずOwnerが必要箇所だけ追従させる。並行Draftを機械的に全部結合しない。
2. **唯一のSource/Expected/Owner**：PinはProduct/TAI #629、SkillとHandoffは#633、Activityの実利は#621、Session Adapterの異質Consumer受入は#648。実Source・Grant・業務意味はTEI/SUI/SHO/SEI/EKI各ProductのOwner、Host/OS強制はTAI #168/#232。独立ExpectedとFixtureの複製禁止。
3. **実績の境界**：docs-onlyで確定できるのは非重複・依存順・停止条件まで。実Tool/Source/Skill Loader/Session/OS隔離/実Consumerの達成は各Jobのexact HEAD・Attempt・Receipt・独立Expectedで判断。現状態のunknown/partial/unsupported/NOT RUNを「計画反映済み」を理由にGreenへ変更しない。
4. **導入と撤退**：最初のUIはProduct-onlyと限定Handoffに縮退できる。採否を判定するのは各製品の業務成果であり、Wails Web/WASM化や外部HarnessのSession API数ではない。B4独自Agent Loopは外部Harness＋既存Adapterで解消できない重大欠落とOwnerの費用・撤退判断が実測で揃うまで保留。

**本節の実施事実**：TAI 4 Draftの現GitHub Compare（changed files/ahead/behind/mergeable）と既存TEI実装PR・他チャット設計の再照合、文書への受入順の反映のみ。Draft再base/merge、Windows Stage2、実OS H2/H3、二UI実Session、WASMの同一Fixture計測、実Handoff Consumer、Product Owner正式受理は**NOT RUN**。本節が承認済みの合意・追加Hard Gateであるとは主張しない。

<!-- yic-harness-activity-causality-qhp0-consumer-matrix-20261114 -->
## 20. Activity→Harness→Productの因果帰属を、一つのSession状態に畳まない（後続設計）

### 20.1 操作の順序でなく、出典と実Observationの辺を照合する

他チャットのTEI設計Build/Evidence、SUIのRaw/Item/Occurrence、SHOのSource/文書Consumer、SEIの判断Basis、EKIのTask/Attempt/Effectを照合すると、YICで本当に共有したいのは**任意のSession全履歴**でなく、当該仕事に必要な次の因果辺である。ただし新しい中央Event Graph/Schemaを設けるのではなく、既存QH-P0のI/R/P/T/C/H、TEI Pin/Operation、TAI Activity、Harness Native Log、EKI/SHO Receiptで実際に追える範囲だけを記録する。

| 辺／問い | Source-of-truthと観測場所 | 成立しても保証しないもの |
| --- | --- | --- |
| Activity intent → Product Pin | TAI #271の目的、TEI #4515のWorkbench/CLIで人が明示したWorkspace+Kind+ID/Scope | FocusやGraph描画IDだけから対象の一意性を推認しない |
| Pin → qualified current Product Read | TEI #1124/#3422、SUI/SHO各Readerの原Source/Root/Revision/Required/Consumed/Validationの実読取り | 同じWorld/Model FP、Digest、表示結果があっても現在Grant・完全閉包・原子的Snapshotではない |
| Product Read → disclosure projection | Source保持Product/Hostの現在Audience/目的/Grant、送信予定byteとRedaction | 取得できたSourceの全件開示可を意味しない。Meta/件数/Path/エラー自体が秘密となり得る |
| Projection → actual external delivery | TAI #168 G1、既存QH Transport Receipt、実Tool argv/egressの観測 | Prepared≠Delivered。Transport受付≠Model実利用 |
| Native Session/Turn → actual Tool Reply | Harness Native実Session/Thread/Turn/Tool ID・実Host Profile・G2 complete stdout/stderr/body | Session名、final answer、Tool exit 0だけで完全受領・意味正答・Product実Readを認めない |
| Tool Reply → Consumer claim | Product/SHO/SEIによる用途相対の実Readと現在Basis、unknown/partialの保持 | SHOが票のMarkdown payloadを再Readしても元TEI Sourceを独立再Readしたとは言えない（QH-07） |
| Candidate → Product Preview/Apply | 元Pin/現在Source/Grant・Acceptance/BuildIntent・Product Operation ID | Agent「完了」、Turn中断、古いReceiptで最新の保存・生成・業務Effectを保証しない |

**観測の接着単位**：実Harnessが発行したNative IDと、送信元のProductが生成/保持したRequest/Pin intent参照、実Tool Invocation/Response、およびProduct側の元Attemptを、同一試行の証拠票に対応付ける。「外部Harness sessionIdとProduct subjectIdが等しい」など別名前空間のID値一致で結合しない。Cross-UIの画面名・Git branch名・Session labelも、実対象のBindingではない。

**不完全取得の停止線**：TEI #3262のrequired/declared/discovered/loaded/parsed/bound/returned、page/continuation/end、Root/Validationの現在性を当該Claimに必要なところまで検査する。複数Readerが別時点でSourceを読んだとき、一致したModelRevisionをもってatomic snapshotとは扱わない。Scope/epochまたは当該必要集合が未確認なら、確認済みの局所Claimを残したまま、横断Claimをunknownにして必要辺だけ再確認する。

**権限の時間方向**：後からGrantを撤回できても、外部Harness/旧Sessionにすでに渡したRaw/Tool結果を取り戻せたとは言わない。新しいAudienceが同じSessionへattachする際には、**今後のProjection**と**すでにSessionに存在するTranscript/履歴Tool Result**を別々に判定。履歴資格が確認できなければM2/M3へ進まず、M1の新Session限定Handoffへ縮退する（TAI #234 HC-15）。

### 20.2 成立した辺だけ残す選択的再資格化

次の変化はすべて「過去のObservationは履歴として残し、現在用途の資格を再判定する」候補。新Watcherや強制Global Invalidationではなく、既存Productが実際に確認できるRead/Validation/Grantを用途ごとに参照する。

| 変化 | 維持可能なもの | 改めて確認するもの | 既存Expected |
| --- | --- | --- | --- |
| 同一Source byte/同じModelRevisionでRoot実在だけ変更 | Pinの意図、過去構造Observation | Current Root/Validation、今回のProduct Reader | TEI #4616、#4515 PIN-S0 |
| Source A→B→A、同名別Scope/別Root | 過去の選択履歴・候補 | 実Origin/Identity/必要Source、現在Grant | QH-02/03、PIN-S0、HC-10〜14 |
| Skill本文不変だが参照Script/Tool更新 | 影響しないTool-only用途、旧Skill使用履歴 | 当該Instruction packageのLoad、実Tool版と必要Skill範囲 | TAI #488、Draft #633 §49/50 |
| Harness転送中にReply切断、Stream後着 | 送出試行・取得済み局所Event | Reply終端/Consumer受領、元TurnとPinの帰属 | TAI #168 G2、HC-17、YH-04 |
| 旧Session/別UserへのAudience変化 | TAI Activity目的の許可可能な限定参照 | 過去Transcript閲覧、現在Projection、実Native Writer権利 | HC-15/16、TAI #271 |
| Interrupt/Host再起動中のProduct Operation | 起動済みOperation/Attemptのidentity | 現Hostでの実Result/Effect、再実行の冪等性・受理 | HC-18、EKI既存Owner |

確認できない属性を「変化なし」と埋めず、既存票のunknown/unsupported/insufficient-evidenceに残す。安全に続けられるProduct単独read-onlyまで一律停止しない。

## 21. 最初の一仕事の実行カード：QH-P0をHarness接続へ接合する前のProduct実縦切り

### 21.1 既存の実証を使う順序

**最初の適用対象は公開・read-onlyのTEI一Subject**。新しいHarness Runtime/中央Store/Schema/総合Oracleを先に実装せず、既存[QH-P0 §10.3](https://github.com/hat47x/tai-pleroma/blob/main/docs/yi-constellation/cross-product-handoff-execution-tickets-2026-11-11.md)および実Product CIと同じFixture/Expectedを再利用する。

1. **Product実存在の確認（I/R）**：公開TEI reference/workspace、実CLI binary/commitとworkspace contentを固定。現行QH票の例である go run ./cmd/tei model catalog -workspace reference/workspace を出発点にし、実Discovery・Inspect・必要Readから**今回存在する一意Subject**を決める。CLI/Workspaceの実構文が変われば現行ProductのUsage/Helpに従い、旧Commandを成功扱いしない。GUI未実装時の選択は「合成Pin」であり、実GUI Pin合格ではない。
2. **Current Product/Disclosure（R/P）**：Source/Root/Origin/Subject Kind+ID/Scope、Required-Consumed/partial/Validation、今回の受信先への開示可能なbyteをProduct/Hostで確認。公開Fixtureでの正例を実OSの秘密Raw拒否と混同しない。Root/Scopeが一意に表せない場合は送出せずFit/Gap票へ。
3. **既存Handoff v1の実Transport（T）**：実SUI Producerが供給した許可票、または実Driverが作った合成票であることを明示して区別。既存 yi.handoff.context/v1 の target/revision/references/evidence/limitations だけを使い、相手SHOの既存Consumer/Node CLIを**別Process**で呼んでpayload原byte/Receipt/exitを観測。Qualified Scopeがv1に表現できなければ、存在しないFieldを捏造せずOwnerへ非適合Gapを戻す。
4. **Consumerが実際に利用した根拠（C）**：SHOによるPayload再Readと、TEI Productが元Subjectを実再Readしたかは別の列。既存[SHO #48](https://github.com/hat47x/sho-composer/pull/48)の同Markdown byte/異Source・異対象3票を対照として再利用。TEI元Source未読ならR/Cの当該Claimはnot-run/insufficient-evidenceであり、Tの成功から補完しない。
5. **外部Harness試行（H、後続）**：ここまでのProduct基線を保存したうえで、TAI #168 G0実OS Read-deny→G1 actual Egress→G2 complete Tool Replyが成立した公開Profileのみ、独立H2/H3 4 Slotとは**別の後続Job**に接続する。まずTool-only。SkillはJob固有の改善が必要な場合だけ、I/S/C三閉包で実Loadを確認して追加する。生PathをRemote CLI/MCP引数として任意開放しない。
6. **結果を元対象へ戻す（J-P/後続）**：外部Answerは元Pin・Root・Source時点・Native Turnの候補として保持し、現在Productで再Read/Preview。AIが使った対象と今のFocus/Workspaceが変わっていれば自動Apply 0。read-onlyの完了判定ではBuild/Effectを要求せず、後日のWriteは既存TEI/SHO/EKI Operationに引き渡す。

### 21.2 一試行の採点欄を統合しない

| QH列 | 最小実Observation | 不成立時の限定結果 |
| --- | --- | --- |
| I / Intent | 誰がどのRoot/Kind+ID/用途を指定したか。合成か実GUI操作か | Synthesized selection / GUI NOT RUN |
| R / Resolution | 実TEI Product Readerが当該Qualified Subjectを実Sourceから読んだか、Coverage/unknown | Product Read不足ならnot-run/unknown |
| P / Projection | 現在Audienceへの許可と実Preview byte/非開示範囲 | Host承認・実Policy未観測なら限定公開Fixtureのみ |
| T / Transport | 既存Handoff v1 payload exact bytes、別Process受領、Receipt | 元Source再解決/現在性には昇格しない |
| C / Consumer | SHO等が実際に何をReadし、何をBasisとしたか | Payload Readのみなら元TEI Source claimはunknown |
| H / Harness | Native Session/Turn/Tool ID、実送出・完全Reply・実受領 | Product-only試験ならnot-run。Skill名はLoader証拠でない |

**受入の切り方**：実CLIでRが成立してもSHOでRが成立したとは表示しない。公開合成Pが成立しても、機密P・OS G0/G1をPASSにしない。Tの局所実証から今回のHをPASSにしない。実HarnessのHが成立しても同じActivityの別UI継続・Product ApplyをPASSへ加算しない。各結果のHEAD/Attempt/Owner/Expectedを記録する。

### 21.3 後続UI・Web・第二Harnessへの伸長条件

- **QH-P1**：実GUI Pinが実装されたら同じ公開SubjectをStudio/CUIで指定し、Focus移動・同Kind同ID別Root・同RevisionのValidation変更・後着Eventを検査。Wails WebViewの画面上の表示一致だけでCLIと同じApplication Operationを消費したと宣言しない（TEI #1824/#3422）。
- **Web/二User**：Browser Tabが共有Workspaceを見ていても、Dirty Buffer/CASとAI Candidate・旧Transcriptは異なる資格。Web Go ServerでCurrent Grantを再検査、Native実Writer保証が不明ならM3を公開せずM1/M2へ縮退（HC-15〜18）。
- **第二Harness**：同一Task・公開Source/Host Disclosure・独立Expectedを保存し、DSHと実接続可能なCodex/Claude Code/OpenCodeの一つでTool実到達/Resume/Reply完全性を比較。Native差はAdapterのCapabilityとして表し、失敗時の代替Harnessが勝手に広いGrantへ昇格しないことを評価。

**撤退／Fit-Gap判定**：Product Source Locator/Scopeを既存v1と既存Product APIだけで安全に結べない、OS Read-denyや実Egressが不適格、Consumerが元Sourceを再Readできない、Native履歴Audience/Writerを判別できない場合は、影響する列と現在の実モードだけを不適格とする。新 Handoff v2/第二Registry/Host/Agent Loop/分散Lockを応急作成せず、既存Product・TAI Ownerに不足する契約を戻す。

## 22. 開発・価値評価への統合：先行二P0を止めず、誤昇格と過剰停止を両方測る

**P0を変更しない**：A=TEI [#4583](https://github.com/hat47x/tei-platform/issues/4583)の実Stage1→Stage2 Desktop/同Attempt BuildIntent+Native WebView2、B=TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)のG0→G1→G2→独立H2/H3四Slot（比較適格0/4）。いずれも独立Owner/独立証拠で進め、C=Product-local Pin/R3-A、D=QH-P0、E=M1/M2/M3、F=J-Vを後続の必要な用途にのみ接続する。SUIのAI OFF Raw→Card→原文復帰、SHO単独Writer、SEIの局所判断、TEI Studio単独操作はHarness不適格でも維持する。

**SK-02 Native fork独立性の負例（既存Checkerの局所実装修正）**：[TAI Draft #649](https://github.com/hat47x/tai-pleroma/pull/649)では、従来の4件の`session_id`一意性だけでは見逃す**共通root、fork親、fork深度、resume**を、実Native記録がある場合に比較不適格として分類する。DSHの通常forkは親IDを残さず`isSeeded`や`inheritedEventCount`で継承履歴を表す場合があるため、親IDのみを資格判定にしない。新しいSK-02 Checker/Host/Runnerは追加せず、既存の合成E73〜E82とCIの必須ケース一覧を補強する。**観測されないNative lineageを自己申告の`independent_session_observed=true`から保証したとは言わず、実OS/Host隔離・G1/G2・独立Expectedは#168/#232のOwnerに残す**。初回H2/H3四SlotのTask/Tool/独立割付を変更しない。コードPRのCI成功は外部DSH実資格0/4を変更しない。

**UI/Go/WASMの検証方法**：前§17のWASM案は、Productに既存の現在Source/Grant・実Operation正本を残した状態で、UIに必要な**純粋な局所計算だけ**をTypeScript／Go Service／WASM三条件で比較。最初のQH-P0やH2/H3へWASMを必須にせず、実Studio Desktopの基線取得後に必要な処理だけ測る。再生成後に同じWebViewに表示できたことと、同じSource/Required/Consumed/AuthorityのConsumer資格を得たことは別。

**価値比較の評価者と母数**：B0 Product単独、B1 Tool-only/必要時Product Skill、B2薄いAdapter、B3統合UIの比較は[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)/[#488](https://github.com/hat47x/tai-pleroma/issues/488)・既存J-V/M00/M01/M10/M11を使用。追加すべき観測は「正しく確認済みの局所Claimを保持したか」「本当に変更・失効した必要辺だけを保留したか」の両方向であり、通知件数・Token節約だけで安全性を相殺しない。Packetの準備・配送・再Read・失効修復コストも増分価値へ算入。小標本の参考比較を一般的効果量とは呼ばない。

**採否**：Tool-only＋既存Handoff v1が足りるJobではTAI Skillを配布標準にしない。B0〜B3の実適格試験で必要なUser Jobが実現できる限り、B4独自Agent Loopを投資対象にしない。B4再検討には、複数代表Harnessの実適格比較、Product API/薄いAdapterで解消できない重大欠落、実運用費用・復旧・Owner受理をすべて要求する（TAI #234）。

**今回の証拠上限**：本§20〜22は既存[QH-P0](https://github.com/hat47x/tai-pleroma/blob/main/docs/yi-constellation/cross-product-handoff-execution-tickets-2026-11-11.md)、TEI #4616/#4625、SHO #48、TAI #168/#234/#271/#488の限定記録を照合した**Docs-only実装・検収計画**。新しいTEI実CLI→SUI→SHOの同一Job、同一SessionのDesktop/Web、二Harnessの対照、実WASMベンチマーク、Stage2 Native Desktop、OS/Network適格H2/H3四Slot、Product/Owner正式受理は**NOT RUN**。別HEAD・別AttemptのCI成功を一つのE2Eへ合算しない。

<!-- yic-harness-surface-web-exposure-typed-entry-gate-20261114 -->
## 23. Web/Native/CLI/Harnessの実行面を区別し、秘密Eventと操作Entryを明示審査する（設計案／実公開NOT RUN）

他チャット[TEI Plugin Contract Draft #4621](https://github.com/hat47x/tei-platform/pull/4621) §17、[Wails Server Surface Draft #4627](https://github.com/hat47x/tei-platform/pull/4627)、[TEI Script Launch Draft #4618](https://github.com/hat47x/tei-platform/pull/4618)の限定成果を、既存TAI #232/#168・HC-15〜18・Product #3421の**実行面資格**へ接続する。これはYIC用第二Gateway/共通HTTP/認証器/ランチャーを新設する提案ではない。

### 23.1 Productの型付き意味と、実行面への公開は独立

| 実行面 | 今できること／検証できている範囲 | 必ず別に確認すること・禁止する昇格 |
| --- | --- | --- |
| Product-local CLI | TEIの既存read-only/Local Evidence CLI等をそのOS Principalの実Processとして試験可能 | ローカルPath引数・内部ErrorをRemote Web/MCPへ転送しない。CLIのhelp/一覧≠Entry実選択≠実Invoker |
| Wails Desktop Native | Go Application/StudioBridgeと生成Workbenchを実WebView2で利用する限定H1/B0実証がある | Native UIの表示＝現在のSource/Owner意味/Build/Grant受理ではない。Web公開にそのまま流用しない |
| Wails Server / Web | Wails v3 Server BuildでGo ServiceがBrowserへBindingされ、標準Go→Browser Eventは接続Browserへbroadcastする | 実Trusted Principal・Workspace・Audienceでサービス/Tool/Transcript/WS payloadを制限。Origin/Host/Tab名≠AuthN/AuthZ/現在Grant |
| 外部Harness/MCP/Skill | 実Tool/Skill Loaderと現在Host Profileに合う用途限定Projectionだけを使う | Skill説明≠Provider実収録/CLI実動作。ローカル生Path/実Secret、未許可Raw/Metadataを渡さない |
| Go→WASM Client候補 | pure/read-only検証・表示補助の速度比較候補 | 権限確認、DB/Provider、秘密の現在Source、Build/Effect/Host実操作のAuthorityにしない |

Wails v3公式[Server Build](https://v3.wails.io/guides/server-build/)はServer Service Bindingの利用と、Goから接続全Browserへの標準Event broadcastを記載する。従って、**個別Audienceにだけ許されたSession/Tool/Raw/Rowset/TranscriptをGlobal Eventへ載せる実装はWebの採用条件を満たさない**。Browserで受信後に非表示とするだけでは遅い。秘密Eventの個別配信方式がProduct/Hostで適格化できない場合は、Server上の対象イベントを送らず、現在Grantで再取得するread-only Query/限定Viewに縮退する。必要なAudience別Deliveryの実装方式の採否はTEI #1824/#3421/Host Ownerに残す。

[TEI #4627](https://github.com/hat47x/tei-platform/pull/4627)はGo Server登録・反射Methodの15件をread・plan・reference command・external child等へ分類し、漏れた新公開面をレビュー要求にする限定テスト。HEAD 9491bf9 のWails Server Jobの成功は**static method inventory＋local loopback/2 browser contextsの表示分離**に限る。Web認証済み2 Principal×2 Workspace×2 Tabの実HTTP/WS拒否、Actorに対する現在Grant、Web実公開適格は未実証。既存Command/SHO external process entryを含むStudioBridgeをそのままPublic Webへ公開しない。

### 23.2 実行面への公開は明示Entry/Selection/Invocationを経由

[TEI #4495](https://github.com/hat47x/tei-platform/issues/4495)の既存区分をそのまま利用する。Function/Script Sourceが存在しても、CLI/Web/Harnessへ公開可能なEntryではない。Trigger（UI、Harness、Schedule等）は起動要求の契機にすぎず、選択済みProvider/Artifact、typed input、対象Revision、Operation identity、現在Host Principal/Grantと実Invocationを別に確認する。

**YICからの利用者操作の認知順**は「目的と固定対象 → 実Product/Tool発見 → 現在のSource・Required/Consumed・開示状態 → 明示Entry/型付き要求 → Preview → Host admit／Provider実invoke → Reply/Consumer/Effectの独立観測」。read-onlyの場合Effectはnot-applicableとする。Tool-onlyで充分なJobにProduct SkillやTAI Skillを常時ロードせず、必要な場合だけ[Draft #633 §49〜51](https://github.com/hat47x/tai-pleroma/pull/633)のInstruction / Subject / Capability閉包を照合する。

**Agentが作成した命令、旧Grant、UI Actor文字列、Role名、Tool descriptionは実Authorityではない**。Prepare段階で表示されたInvoke可能候補と、Admit/Invoke直前のProduct現在資格が異なったら自動切替や実行をしない。Script/Builder/Pluginの選択と実起動が同一Attemptで一致するかは各Product/Host Ownerが実観測する。YICのSession Resume・Goal Armed・Schedule ACKは入場許可でない。中断・timeoutは実Effectのrollbackを意味しない。

## 24. Web×Harness接合の小さな反証と製品ごとの停止線（既存Expected再利用）

**この章は新試験番号/第二Oracleではない**。既存[TAI #234 HC-15〜18](https://github.com/hat47x/tai-pleroma/issues/234)、[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)、[TEI #3421](https://github.com/hat47x/tei-platform/issues/3421)、[TEI #4495 EL-01〜12](https://github.com/hat47x/tei-platform/issues/4495)、[TEI #4621 WSP-02](https://github.com/hat47x/tei-platform/pull/4621)の独立Expectedを組み合わせる**受入観点の索引**。

| 観測する小試験 | 既存Owner／入力・実証ポイント | 守る停止線と正常な縮退 |
| --- | --- | --- |
| Serverの公開面と二利用者の閲覧 | TEI #4627の登録Method Inventoryを固定→#3421 WSP-02bの2 Workspace×2 Principal×2 Tabで実HTTP/WSを観測 | 許可外のCommand/SHO子Process、別Audience向けEvent/Rowset/Tool履歴は**実受領0**。Originのみで合格不可。失敗なら共有WebでM2/M3を提供しない |
| Transcriptを含む旧Sessionへのattach | HC-15とTAI #232。新User/Workspaceで現在Projectionは見えても、過去Raw/Tool結果を含むNative Sessionを購読 | 旧履歴が読めてはいけない場合はattachを拒否し、M1用途限定Handoffから新Sessionへ。外部に既送の平文撤回を保証しない |
| Product Functionの存在と実行可能性 | TEI #4495 EL-01/02/04/06、Draft #4618。FunctionはあるがEntry非公開、Provider未収録、選択B/実Call A、Actor偽装 | いずれも新Toolに自動fallback/権限拡張0。実Hostのtyped App/Entry検査に委譲。結果値が同じでも誤Invokerは不合格 |
| Web/CUI/Harness間での障害・再送 | TEI #4495 EL-09/10/12、TAI HC-17/18。Reply途中切断、同Operation ID異Input再送、Host効果中にAgent Interrupt | 欠けたReply/Effectはunknown。元Operation/Attemptの観測なしに新IDで二重実行0。AI Turn閉鎖はBuild/Effect取消でない |
| Skill宣言と実在Provider | TAI #488／Draft #633 §51、TEI #4625。SkillにはLocal CLIが記載されるが現Hostは未導入、またはLocal Evidence PathをRemote要求へ流用 | Tool-onlyの適格な安全機能だけ利用継続。現在Productの有効Entryと実Load/実Invocationが無いSkillは候補として表示しても利用可能と記さない |

### 24.1 提供面の縮退を一律停止にしない

M0 Product-onlyは常に独立評価する。Web Serverの現在のHost境界が不適格なら、**Web上の機密Session共有・遠隔Command実行のみ非提供**とし、ローカルDesktop/CLIの正当なread-only調査やSUIのAI OFF作業を止めない。外部HarnessがM3操作非対応でもM1新Session Handoffが安全に成立するなら、そのモードの利便性を比較する。できない場合はM0へ戻る。

初回固定H2/H3四Slot用の公開TEI実験を、Web共有Server/再開Event/新Skillの要求で汚染しない。Webの別Principal/Audience受入は**P1**、純粋Go/WASM比較は後続**P2**、共有Webの共同編集・HAはProductの必要性に応じる**P3**。独立P0はTEI #4583セルフビルドとTAI #168 G0→G2→比較資格4 Slotのまま維持。

## 25. 今回のレビューで反映する差分と未成立資格

- **設計上確定できる差分**：WebにおけるProduct/Host現在資格、Native Transcript旧情報、Global Event、Function Entry/Trigger/Invoker、Skill案内の非同一性と、用途ごとの縮退・既存Owner割付。実装採否／Public Webサービス許可には別実測が必要。
- **局所的な実測**：[TEI #4627](https://github.com/hat47x/tei-platform/pull/4627)のGo method inventoryとloopback/2 BrowserContexts試験は限定CI成功。[TEI #4587](https://github.com/hat47x/tei-platform/pull/4587)のH1 N2→N3生成物byte照合は別HEAD・別Attemptの限定成功。互いの証拠を一つの本番Web/Stage2 Build結果と合算しない。
- **未実施・保留**：認証済み2 Principal×2 Workspace実HTTP/WS・実Audience別Event拒否、Wails Public Webの安全なread-only facade、実外部Harness→Web Serviceの同一Attempt、実Script公開Entry→Product CLI実Invoke、A→B→A／現在Grant/Owner意味受理、二Writer Native保証、H2/H3の新4適格Slot、TEI生成Stage1→Stage2 WebView2、WASM性能比較はNOT RUN。
- **Ownerと重複排除**：実Web/API/Command適格はTEI #1824/#3421/#4495/#4627、Skill導入と実CapabilityはTAI #488/Draft #633、ActivityとTranscriptはTAI #271/#234、OS/LLM送出はTAI #232/#168、Handoff/ConsumerはQH §10。TAI #648は接合の判断/計画のみであり、Webの認証器、Builder、Registry、Session Server、Run Engine、Script Runtimeを実装しない。

本追補は既存Product PRとWails公式資料の仕様・限定CIの照合による**Docs-only設計**。新OS/Web/Browser/Service/Script/Harness/WASMの実験を本作業で実行・受理したわけではない。

<!-- yic-longrun-goal-schedule-operation-recovery-20261114 -->
## 26. 長時間作業の復旧をHarness Goal/DeliveryとProduct結果の独立照会に分ける（設計／新実Trial NOT RUN）

[TAI #234](https://github.com/hat47x/tai-pleroma/issues/234)のGoal/Schedule/多Session比較、前§13の公開実装調査、[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)のActivity継続、[TEI #4497](https://github.com/hat47x/tei-platform/issues/4497)のTrigger Binding、[EKI #57](https://github.com/hat47x/eki-fabric/issues/57)/[#829](https://github.com/hat47x/eki-fabric/issues/829)のTask/Attempt/Resultを、**YIC独自Schedulerを新設せず**実際の1 Jobの復旧判断へ結び付ける。

### 26.1 段階を一つのrunning/completedにしない

| 状態・識別子 | 実際のOwnerと観測点 | 何を保証しないか |
| --- | --- | --- |
| Goal phase、revision、armed/disarmed、round | 外部Harness/DSH等のGoal Host。実Host/Version/Profile別にProbe | active/completeがTool開始・Product Effect・Owner受理の証拠ではない。再起動・fork後の自律再開を自動推定しない |
| Schedule Definition／due Occurrence | 実Harness Schedule ProviderまたはTEI Trigger Provider | 予定時刻・Task保存はInbox配送でも実Model消費でもない。TZ/DST/missed-run規則は明示 |
| Schedule Delivery／Inbox ACK | 実Hostと実Session/Turn受領 | 配送ACKが実Product Operation入場・Effect・独立Consumerの証拠ではない |
| Native Session／Turn／Tool ID | 外部Harnessの実Native記録 | 同名Session、fork root ID、回答「完了」から同じLive Thread/Writer・Tool Reply終端は推論不可 |
| Activity intent／許可Packet | TAI #271の目的・根拠・未決と現在開示資格 | Session全履歴/過去Grantの継承、業務操作のAuthorityにはならない |
| PreparedInvocation／Entry／Operation identity | TEIなどProductの現在Source/Entry、実Host Admit／既存Operation | HarnessのTool要求・Schedule tickだけでは実行不可。再送前に元Operation確認 |
| EKI Task／Attempt／Lease／ResultClaim（選択時のみ） | EKI #57/#829がOwnerの実Execution/Lease/Verifier/Artifact | Task completed、Worker exit 0、Result metadataだけでは出力本文・Verifier・Product Consumer受理にならない |
| Effect／Consumer／Owner Acceptance | Product/外部Hostの実Commit/Receipt、SHO/TEI等の実Consumer | Native Tool exit、Cancel ACK、過去Receiptの再生から現在Effect/意味受理を推定不可 |

**時間・IDの最小持ち方（新Schemaではない）**：実Jobの既存票へ「Goal/Session/Turn/Occurrence/Operation/Task/Attemptの各Issuer名前空間とNative ID」、「UTCの発生/配送/受信/入場/完了の実観測時刻」、「業務as-of/TZ/DST」、「固定Product Source/Required/Consumed・現在Grant」、「Result body実受領/Verifier/Consumer」を記録。実Hostが発行していないIDをYICで生成したふりをせず、実観測できない列はunknown/not-runとする。単純な同値IDや同timestampだけで横断結合せず、元Product側のRequest・実受領Receipt・Native Tool/Attemptの因果参照を照合する。

### 26.2 再起動時の判断順（適格な既存Providerの利用のみ）

1. **停止時の事実を再取得**：Harnessが中断したときのGoal/Task/Inbox/Native Turnの現在状態と、Product/EKIの元Operation/Attemptを別照会。接続先、Host Principal、Workspace、Source/Artifact選択、Recipientの現在資格を再確認する。旧Transcriptを別UIへ無審査でattachしない。
2. **配送と作用を分ける**：予定発火なし／配送なし／配送済み未受信／受信済みTool不完全／Product開始済み結果不明／独立Result受理済み、を観測できるところまで分ける。最後のreplyが欠落している場合、成功・失敗を想像しない。
3. **結果の既存Owner照会**：元Operation/Task/Attempt/Leaseと出力bodyの所在・digest、Verifier/Consumer・Effect ReceiptをProduct/EKI/実Hostへ確認する。既存Result bodyが読めずMetadataだけならverified/completedにしない。
4. **再開の許可をやり直す**：外部Harness側でGoalのrearmが必要なら、実Host/利用者の明示手順で実施。Goal再開≠旧Operationの再発行。期限・missed-run・再試行予算・Principal/Grant・Source/Selected Providerをその時点で再評価する。
5. **再実行可否**：読み取り/純粋処理で再実行が明示許可され、旧Operationが二重作用しないことを実Ownerが照会できた場合だけ既存のretry契約へ進む。外部Effectがunknown、旧Attemptがin-flight、旧Leaseのfencingが不明、異Input/Artifactで同一OperationIDが再来した場合は**自動再実行しない**。Ownerへpending/unknownで戻す。
6. **UIへ投影**：Activity自体は保存・参照できても、Native Session復元／Agent自律再開／Product再開／成果物受理を別結果として表示。復旧不可なら許可済み限定Packetによる新SessionのActivity再開へ縮退し、同一Live Sessionの復帰とは呼ばない。

この順序は単一の横断状態機械や中央Coordinatorの導入ではない。**どのOwnerの現時点Observationを問い合わせるかの利用手順**。Productの既存Idempotency/Effect/Trigger契約とHarness Native APIをそのまま利用する。

## 27. Schedule・Lease・Resultの最小反証を後続J-Aへ接続（既存Expectedを再利用）

| 観測対象 | 固定する反例と既存Owner | 受入・縮退条件 |
| --- | --- | --- |
| Host停止中の予定3回欠落 | TAI #234 Schedule G2／HC-06・TEI #4497 TR-08/09。明示TZ/発火Window、missed-run=skip/catch-up候補を区別 | due／Host Inbox／Model受領／実Tool／Product結果を別記録。Providerが復旧配送を保証しなければ、未実施と表示。catch-up自動三重実行禁止 |
| Queue時許可、start前のGrant撤回・Script改版 | TEI #4497 TR-03/04、TEI #4495 EL-07 | Queueの古いGrantやProvider版を再利用せず、実Admit前に再資格化。拒否はそのEntryだけであり安全read-onlyを止めない |
| 重複Event、ACK loss、Deadline超過 | TEI #4497 TR-05/07/09、TAI #234 HC-18 | Occurrence、Operation、Attemptと業務as-ofを分離。遅延受信が期限内開始/完了を意味しない。元Operationを照会してblind retry 0 |
| 旧Workerから遅着Result、Lease失効、Control Plane再起動 | EKI #57 V2/V3/V6、#829 E1/E2 | 古いLease/AttemptからAcceptedResultを復活させない。Task/revision/Worker/Artifact/Lease/ResultClaim/Verifier一致までE2E資格を保留 |
| Output metadataだけあるが実bodyは取得不能 | EKI #829 E2、TEI #4497 TR-12、TEI #4194 | Task completed文字列やexit 0は業務結果に不十分。body実byte/readback＋digest＋独立Verifier/Consumerが必要 |
| AI Turn cancel後もBuild/DB Effectが進む | HC-18、TEI #4495 EL-09/10、EKI #829 | Turn InterruptとProduct Operation取消を分ける。Effect unknownのまま再実行・成功表示しない |
| External Tool Reply切断／履歴の別Audience表示 | TAI #168 G2・HC-15/17 | 完全なTool Reply/現在Audienceがなければ回答確定・旧Transcript共有を止めるが、許可済みM0/M1の作業は継続 |

**現実装の適用上限**：[EKI #829](https://github.com/hat47x/eki-fabric/issues/829)の現状評価にはArtifact ingestionの422、Result body retrievalの501、effect mode none限定などの未接続点が残る。これらはIssueの観測時点の報告であり、今この文書で現行バイナリを再実行した確認ではない。T1 EKI Nativeの実Attempt→body→Verifierに必要なものがない場合、**T0 Product/Host Directのpure Jobを先に成立させる計画へ戻す**。現状のT0実装・利用可能性まで保証するわけではない。T2 Managed Providerは実Delegation Profile/ExecutionRef/独立Resultが成立するまで保留。TEI [#4194](https://github.com/hat47x/tei-platform/issues/4194)のW-1/T0・T1・T2を比較先とし、成功件数を異なるルートで合算しない。

## 28. 複数Session／多モデル開発の最小運用単位と実価値を分ける

YICで一晩〜複数日にわたり複数Issueを進める場合も、**一つの中央Agent Loopが全作業を再実行・統合する構成を前提にしない**。[TAI #234](https://github.com/hat47x/tai-pleroma/issues/234)の3 Workstream以上の比較案に沿い、DSHをPlugin親和性により実証順で僅かに優先しながら、Codex/Claude Code/OpenCodeと同じ利用者Jobの適格な比較を設計する。

**最小の作業票（既存GitHub Issue/PR・Product/EKI Evidenceの参照を束ねるだけ）**：

| 何を固定するか | 誰が持つか | 統合時の反証 |
| --- | --- | --- |
| Task goal／対象Issue／Owner／完了の独立Expected | GitHub Issue/各Product Owner、TAI Activityはその参照 | Agentの自己申告Complete/PR作成はOwner Acceptでない |
| Repository/branch/worktree/対象path/Source＋Model revision | 実Git・Product Reader／Build Owner | 別BranchのGreen、Source移動/A→B→A、同じファイルの競合を一つのAttemptへ寄せない |
| 使用Harness/Provider/Model、実Tool/Skill/Host Profile／予算／権限 | 実Native Harness/Host、TAI #168/#488比較票 | Session名、同一Model名、サブスク画面表示を実Quota/Tool資格へ昇格しない |
| 実Invocation/Source Read/生成Artifact/テスト/出力/受理 | Product Build/Script Owner、EKIは選択時のみ | commit SHAやTool exitだけでは独立Test・元Source/Evidence・Consumer受理でない |
| 停止理由/期限/Lease/Result unknown/人による判定 | Native Host/Operation Owner/TAI Activity参照 | 結果不明を新Sessionから自動再実行・自動mergeしない |

**最初に実行する比較**：公開または許可済みread-onlyの独立3 Issue/3 Workstreamを用い、(a) Product-only＋手動Issue運用、(b) 代表Harness各独立Session＋Product CLI、(c) 必要な用途だけTAI Activity Packetによる再開、の順に比較。実Writer／PR merge／本番Effectを比較の初期必須条件にしない。Skill増分のM00/M10/M01/M11はTAI #621/#488のOwnerに残し、Workstream数×Skill条件を一度に増やして因果効果を不明にしない。

**測るべき増分価値**は、実Independent Expectedを満たした仕事数／利用者が再開時に必要とした説明量／重複実行・修復コスト／間違ったSource・Targetへの候補戻し／有効な根拠を失わず再利用できた割合／正しくunknownに留めた割合／修正・Review・Undoの人手／Token・料金・Quotas・失敗・待ち時間をそれぞれ記録する。高い並列度や低いToken数だけを製品価値の代理としない。ITT/PPの母数と独立ExpectedはTAI #621/#422の既存案に従い、新しい総合スコアを作らない。

## 29. ロードマップの接続先・採否・検証状態

| レーン | 今回の追加成果 | 接続先の実Owner | 次に要求する実証／非目標 |
| --- | --- | --- | --- |
| 独立P0-A | Build途中のHarness/Session停止でもTEI Stage1/Stage2実Attemptを正本とする | TEI #4583/#1824 | 同一Attempt BuildIntent→実Builder/Artifact→生成Stage2 WebView2。Harness rearmをセルフビルドの前提にしない |
| 独立P0-B | 外部HarnessのTool Reply/OS隔離資格なしに長時間自律運用を合格へ昇格させない | TAI #168/#232 | G0 real Read-deny→G1 egress→G2 complete Reply→独立H2/H3四Slot。最新Issue観測で比較適格0/4 |
| 後続J-A1 | Goal armed／Schedule配送／Product開始／結果の別Claim | TAI #234、TEI #4497 | 公開pure/read-only JobでHost再起動・予定3回欠落・ACK lossを段階観測 |
| 後続J-A2 | 外部効果・再送・Lease・Result body復旧を現Ownerへ委譲 | TEI #4495/#4194、EKI #57/#829 | T0 Direct基線の次にT1条件付き。T2はManaged Provider実Delegation Profile後。Effect unknownは自動再試行しない |
| 後続J-S/J-V | 再接続・限定Packet Handoff・並列3 Workstream・費用／再説明 | TAI #271/#234/#621/#422 | Native Session実復帰と新Session Activity再開を別採点。Goal/Schedule実運用能力は各Provider/Profileで評価 |
| 後続UI | Resume/Cancel/Retry/受理の別表示 | TEI Studio #1824/#3421、TAI #234 HC-15〜18 | UIで表示できてもHost/Effectが復旧したとは扱わない。Web機密Eventと二Writerは§23/24の別試験 |

**Owner受理の停止線**：本章で採用したのは設計上の区分・実証順・失敗時縮退であり、DSH/Codex/Claude Code実Resume、Scheduleの再配送、EKI Artifact/Result body、Control Plane failover、TEI Stage2 Self-build、実Product Commit/Owner承認、多Workstreamの実効果を新たに観測・採用したわけではない。DSHの公式機能表・各Issueの既存局所Evidenceはあっても、今の実Host/Principalでの利用資格は別。B4独自Agent Loopへの投資判断は[TAI #234](https://github.com/hat47x/tai-pleroma/issues/234)の既定条件（複数代表Harnessの適格比較、代替可能性、重大固有欠落、費用、Owner受理）が成立するまで保留する。

**実施内容**：TAI #234/#168/#271、TEI #4495/#4497/#4194、EKI #57/#829と前§13/§18/§20〜25の文書・Issueを照合し、既存Ownerへ次の1 Jobの復旧実験を割り当てたDocs-only計画追補。新しいTrigger schema、中央Scheduler、Agent Host、Session Store、Task Engine、Result Verifier、Cost Registry、Handoff v2、第二Expected正本は増やさない。
