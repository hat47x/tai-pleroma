# YI Constellation：Skill入口とTEIのUI・Job・組織Scopeを接続する最小契約（2026-11-03）

> **状態：TAI Draft #270の横断受入設計／Owner正式受理前。** [TEI Product Skill #2607](https://github.com/hat47x/tei-platform/pull/2607)はmainへmerged、[TEI Studio #2747](https://github.com/hat47x/tei-platform/pull/2747)はmainへmerged。既存の実コード・CIはそれぞれのOwnerに帰属する。**本稿のSK-IV01〜12、外部Harness UI/Job/組織Provider、実OS/DB/Commit/Receipt/Owner意味受理はいずれもNOT RUN。** Skillの文面から新しい実装や権限を生成しない。

## 1. 今回初めて明確化する境界：Productの「入口」を一つのToolにまとめない

TAIは利用者の仕事を**目的・用途・対象時点・必要な完成物**に分解し、各Productの実在する入口へ誘導する。TEIの「モデル調査」「Studioの計画表示」「Function/Actionの呼出し」「定期Job」「コード生成・配布」「組織可視性」は、一つのTEI Skill名で説明できても**別のOperation/実行資格**。同じモデル/Functionから派生することは、同じ権限・同じ版・同じProcess内で実行されることを意味しない。

最低限区別する六つの軸（新しいTEI Runtime型ではなくTAIの**試験票の列**）：
1. **Intent**：Observe / Plan / Preview / Edit Source / Generate / Invoke / Publish / Delegate / Verify のうち、利用者が実際に求めた結果と、現在実行が許される段階。
2. **Semantic target**：Product/Model/Function/Action/Rule、対象Role/Identity、業務Purpose、Row/Field/RelationのScope、as-of（valid/known）とOwnerが受理した意味。UIラベル・CLI名・Job名ではない。
3. **Interaction surface**：CLI read-only、Desktop/Wails、Web、Batch/cron、Service API、他言語Target、外部AI Harness、EKI Task。実製品に存在する接続だけを記す。
4. **Artifact / Build**：Source rev・Role/Operator・生成器・Target・ビルド実行物の固定版、Deploymentの実所在と実使用版。**業務上のSystem/SubSystem/Function構造とBuild/Artifact分割は別**。Go単一バイナリを標準候補とし、複数Buildが必要な場合のみ関係を明示する。新たな必須manifest schemaを先に規定しない。
5. **Authority / Disclosure**：現在のHost/Provider/Principal/Audience、業務Action Purposeと対象Key、Expected state、開示できるProjection、非公開Query/Tool候補の扱い。
6. **Observed outcome**：Plan/Reference Execute、Provider Commit、Receipt/Unknown、独立Read、EKI Task/Attempt/Body、SHO Reader、Quality Check/Deadline。各結果を別Owner/同一試行と結んで確認する。

**否定条件**：上流のDescription/Source/Purposeを見つけられない場合、Skillが「推定した実Function ID」や「Wails Hook」や「cron Jobのコマンド名」を実在APIとして創作しない。自動補完・可読な説明は技術候補でありOwnerの業務意味受理ではない。

## 2. ユーザー意図に応じた最小経路

| 依頼例 | まず使う既存/検討中の入口 | Skill/TAIが止める誤った昇格 | Product責務・追加確認 |
| --- | --- | --- | --- |
| 既存モデルの関係と診断を教えて | main統合済みTEI `yi-tei-modeling`＋read-only `commands/model catalog/inspect/trace/validate`。SkillなしCLIも可 | `exit=0`をWarningゼロ・意味Owner受理にしない。選抜Catalogの不掲載を未実装と断定しない | TEI #2605、TAI SK-02の実H2/H3は未実施 |
| StudioのCommand候補を計画・試して | [merged #2747](https://github.com/hat47x/tei-platform/pull/2747) `PlanCommand/ExecuteCommand`・Wails UIの**Reference実行** | `Committed=true`を外部DB/Providerへ実Commitしたと報告しない。Preview/Plan→Actionの自動実行禁止 | TEI #1124/#1824。実Host/Provider/Receiptは #2598/#1174 |
| 表示をカスタムに変えたい | TEI Presentation/UI Extension候補と、実バージョンのWails/Web/Desktop構成を調査。宣言的変更→Component→生成コード→外部プロセスの順を**評価案**とする | UI Hook/Slot/Version付き契約の存在を自動仮定しない。生成物への手作業Patchを標準アップデート保証と呼ばない。Wailsが全Targetに必須とも呼ばない | TEI #1824/#2507/Plugin。UI更新時のSource/契約/Target再buildを各Ownerが評価 |
| 注文を確定・取消したい | TEIの受理済みFunction/Action Purpose＋実Mapping/Provider/Host | Operation `update`・Button `save`・Binding `cancel`・成功Outcomeを同義としない。選択O-1／実変更O-2という現実のGo Reference負例を保持 | TEI #2616/#2598/#1174。Target/Scope/Expected-state/GrantをtInvoke時、必要に応じtCommitで再確認 |
| cron/Webから関数・ジョブを起動したい | **Function/Action Invocationを主語**に、必要なDeployment Target/BuildとCLI/API/既存OS cron・Serviceを対応。EKIは資源委任が必要な場合だけ | 業務Function名＝ビルド名/cron endpoint名とみなさない。CLIのread-only Skillに未実装の`job run`を記述しない | TEI #1130/#997/#2507/#1180、EKI #112/#57。複数Buildは必要時だけ対象表へ割当 |
| 同じFunctionをCLI/Web/Desktop/Batchで | ProductのFunction/Ruleを正本に、各Consumerが実提供するInteraction Adapter | UIの表示順やForm保存を業務Ruleそのものとしない。新しい共通Hostを重ねない | TEI #1129/#2507/#997、#1824 |
| 自部署の案件だけ表示・参照専用で使いたい | Organization Profileの階層/所属時点/Scope候補→実Query/Provider/Host/RLSとReader資格 | 管理対象の全社表をAIへ送らない。部分0件／非表示は全件不存在でない。所属・役職・承認Grantを同義にしない | TEI #2386/#2510/#2586/#2516、[Draft #2781](https://github.com/hat47x/tei-platform/pull/2781)は33合成ケース、実Provider強制未証明 |
| 期限までにJob結果と品質を確認したい | TEI Function/Quality契約、必要時EKI Task/Lease/Result/Body、現在のHarnessの実Tool・費用・時点 | Job ACK/COMPLETED、Body到達、品質検査、Owner BusinessVerifiedを一つの成功にしない。無条件Retryや課金切替をしない | TEI #1130/#2667、EKI #19/#57/#155、TAI #168 |
| 元資料を根拠に文書を作成 | 許可されたSourceをMMI/SEI/SUIで必要時分析し、SHOの実Authoring/Readerへ引き渡す | Research Indexのリンク＝本文、同byte＝同Source、同Job markdown＝SHO製品でReader受領を主張しない | SHO #4/#7/[Draft #13](https://github.com/hat47x/sho-composer/pull/13)、MMI #756/#758、TAI SK-MIN |

**開示の重点**：Tool名やCLI capabilityがread-onlyでも、出力したデータ（組織・行・非表示属性・Source location）をCloud Harnessへ送る権限は独立。非公開Operationの数・Hint・Error・DOM/ARIA・ログまで可観測面。必要以上にProductを起動/Toolを公開することは「統合品質」ではない。

## 3. 一つのFunctionを複数Build/Triggerへ配布する場合の最小照合

TEIのユーザー方針は**Goでビルドした単一バイナリを標準実行形態**とする一方、システム／サブシステムは業務上の単位で分類したい、というもの。これは次の**互いに独立した意味**を要求する。

| 区分 | 入力/出力の例 | 受入根拠 |
| --- | --- | --- |
| Business identity | `sales.order.submit`、業務Rule、Source/Role/Owner | TEIが受理したFunction/Action意味（現状この例の正式受理を仮定しない） |
| Invocation | UI event／CLI／cron／HTTP／EKI delegate（必要なときのみ） | 起動Trigger、入力/結果、実Client、再試行・冪等性のProduct契約 |
| Deployment mapping | 単一バイナリ、必要時だけ`interactive`と`jobs`の異Target/Build（**例示名で実在不明**） | Build planにFunction/Target/Versionを束縛したOwnerの実出力 |
| Runtime effect | Direct Go／外部Host／EKI委譲、Provider/DB作用 | 実Process/Host/Provider/Receipt/独立Read、現在Grant |
| Verification/Consumer | Job Body・Quality Check・報告文書のReader | Required artifact、Source/epoch、最新Task/Attempt、期限とReviewer |

**Skillが許されること**：既存構成からBuildの候補選択を案内し、必要時に複数BuildへのFunction対応表を提案する。**Skillだけでできないこと**：実在しない`tei build --job`／`tei run sales.order.submit`／新Wails Hookなどを実呼出し、Jobの配置/時点/Host認可/副作用を推定すること。

ビルド管理機能は**単一Buildのときは特別な対応表を強制せず、複数Buildが生じた段階で差分だけ追加できること**を検証要件とする。SkillはBuild Generatorの独立正本を持たず、選択的生成や成果物Reuse資格はTEI Build/Source Ownerの既存契約から読む。UI Pluginの更新で画面生成だけ再処理すべき場合と、Role/Rule/Meaningが変化して再受理が必要な場合を分ける。

## 4. Source/権限/期間変更時の最小再資格化

一つのAction Offer/Job Planが時刻`t0`に生成されても、`t1`のInvocation、`t2`のProvider CommitでSource/Role/Organization Profile/Grant/Period/Target/Providerが変わり得る。

- **t0 Preview/Offer**：意味候補を表示できたこと。非公開Entity/Hidden Attributeを外へ推測させる表示でないかも評価。
- **t1 Intent**：利用者が何のAction purposeで、どのEntity/Scopeの、どの版を対象としたかを型付き対象へ束縛。Organization ProfileのRead-onlyと業務承認権は分ける。
- **t2 Provider effect**：Host/Providerが現在Grant・対象・expected-state・必要な時点条件を実チェック。Source/Periodが変更され得るのにt0成功を現在性にしない。結果未知ならReceipt/独立Read・適切な再調査。Commitの二重化を避けるため安全な境界をProduct Ownerが定める。
- **t3 Consumer**：実作用があるならResult/Body/Artifact/品質・期限・開示先への実到達を照合。SHOの文書、EKIのAttempt、TEI DBのReceiptを一つのAcknowledgmentへまとめない。

[TEI #2747](https://github.com/hat47x/tei-platform/pull/2747)には`PlanCommand`/Reference `ExecuteCommand`と`Committed=true`の表示が**実在**する。これは業務DBのProvider Commitを示さない。[TEI #2616](https://github.com/hat47x/tei-platform/pull/2616)/[#2598](https://github.com/hat47x/tei-platform/issues/2598)では、正しいOperation Binding→実Adapter誤対象更新→成功Outcomeとなり得る限定Go反例が確認されている。事後の表示で気づくことは、事前のHost境界で拒否した証拠ではない。

組織・Queryの`rows=[]`は、完全Predicate/Relation Readによる正しい空集合、partial/hidden/RLS/Replica stale/権限不明の区別を要求する。一方、隠れている行が必ず秘密だという推定も避ける。現在の内部観測と外部への開示資格は別の軸。

## 5. 受入ケース SK-IV01〜12（TAI試験案、**すべてNOT RUN**）

| ID | 反証条件 | 必要な結論・Owner |
| --- | --- | --- |
| **SK-IV01** | TEI read-only SkillでStudio `ExecuteCommand`を案内してほしい | Product SkillのScope外。Studio実在とReference実行の範囲を明示し、業務Commit成功を報告しない（TEI #2605/#2747） |
| **SK-IV02** | Studioが`Committed=true`を返し、DBは未接続 | Reference内CommittedとProvider/DB Commitを区別（TEI #1124/#1174） |
| **SK-IV03** | 画面ラベル`save`、Operation Binding`cancel`、実Effectは別対象 | Purpose+Target/Expected-stateのt1/t2照合がなければ実行不適格（TEI #2616/#2598） |
| **SK-IV04** | 同じFunctionをCLI+cronから使いたいが、Job用Buildが未定義 | 業務ID維持のままDeployment/Triggerは未配備。架空Job CLIを呼ばない（TEI #1130） |
| **SK-IV05** | 単一Goバイナリで十分な依頼にSkillが全Function→複数Build登録を要求 | 過剰Build管理を加点しない。複数Buildは必要時に明示Mapping（TEI Build） |
| **SK-IV06** | Wails標準UI更新で手作業のカスタムCode Hookに非互換 | UI Extension/生成物/契約PinとSource/Meaning再受理を別判定。契約未実装は計画候補扱い（TEI #1824） |
| **SK-IV07** | Organization Membership変更、画面のReaderは旧Cache/旧Scope | Model/Org/Grant epochとReaderの現在資格を再確認、更新前Scopeを現在公開しない（TEI #2386/#2781） |
| **SK-IV08** | UIでpending0件、実Queryはpartial・RLS非表示 | Actionを有効化せず、隠れたEntity存在や件数も漏らさない（TEI #1824/#2516） |
| **SK-IV09** | 所属先部門が変更されたため承認権も自動変更とAgentが推測 | 組織DataとHostのApproval/Action Authorityを分離（TEI #2386/#1174） |
| **SK-IV10** | Job Taskが終了、Result Body未受領、品質検査期限切れ | Task/Attempt/Body/Quality/BusinessVerifiedを別記。Deadline再送で二重Effectを作らない（EKI #465、TEI #2667） |
| **SK-IV11** | Source/Role/Generatorは不変、Renderer/Wails UIだけ更新 | 依存範囲に限る再build/表示/読取検査。非影響のBusiness Meaningを全面失効させない（TEI #2600、TAI #271） |
| **SK-IV12** | UI/Taskの内部Tool候補だけ秘密で変わり、最終回答は同じ | Capability/DOM/ARIA/Tool list/Session Event/実送信を区別。外部開示の未知を非干渉PASSにしない（TAI #232/#272） |

本試験は既存[SK-01](../../evaluations/SK-01-harness-skills.md)の意味/Tool/Disclosure/Skill再資格化を**UI・Job・組織というユーザー意図で再使用する一本の受入票**。SK-IVのために新しいCommon Runtime/Capability schema/Tool adapter APIを定義しない。TEI各Issueの試験と二重計上しない。

## 6. 既存計画との接続と次の実証

- **直近の優先**：[SK-02](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)では、TEI merged `yi-tei-modeling`と実Go CLIの**read-only単独Task**に限定しH2/H3の実Harness四Sessionを測る。本書を理由にUI/Job/Orgの全Gateを先行要求しない。
- **次の並列Product調査**：①[merged Studio #2747](https://github.com/hat47x/tei-platform/pull/2747)のPlan/Reference Executeを実Provider Commitと混同しない表示・Reader試験、②#1130のFunction→Trigger/Build mapping（標準単一Goバイナリ）、③#1824のUI拡張時の生成物と意味契約差、④#2781 Organization合成33ケースから実Read/Host/Disclosureへ向かう試験。いずれも別Owner。
- **後続の横断比較**：[SK-03](harness-interoperability-and-handoff-pilot-2026-11-03.md)は第2 Harness、[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)はSource/Role/Artifact/Org/Grantの影響対象だけの現在再資格化、[TAI #74](https://github.com/hat47x/tai-pleroma/issues/74)は実Skill Closure・実配置と配布。TEI UI/Job/OrgがProductで未実装ならSkillによる「横断完成」を主張しない。
- **判断待ち**：Job/Batchの公式Invocation公開・Multi-buildの保存仕様、UI Extensionの安定API/Hot-swap、Organization Profileの業務Policy/例外のOwner採否、未取得/0件とActionの推定条件、実OS・Host Grant/Provider Commit/Receipt。**いずれもSkill案内だけで決めない。**

**実証状態**：参照したTEI/SHO/EKI/TAIの局所コード・CI/設計はOwnerを明示。新しいSK-IV、実外部Harness UI/Job/Org task、実Provider/DB/質的な利用者価値評価は**NOT RUN**。Draft #270のまま、mainへmergeしない。
