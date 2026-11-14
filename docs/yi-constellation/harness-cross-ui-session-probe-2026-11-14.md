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
