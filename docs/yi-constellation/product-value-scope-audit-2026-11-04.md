# YI Constellation：主要価値からの要件適正化と独立レビュー計画

- **作成日**：2026-11-04
- **状態**：横断レビュー計画案／主要Issue・価値文書の一次照合済み。各製品の全Issue・全ADR・全コードの網羅監査、複数モデルの実比較、利用者価値の実測、Ownerによる製品要件の受理は **NOT RUN**。
- **統括Issue・現時点の作業ルール**：[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)
- **位置づけ**：本書は各ProductのRequirement、意味、実行権限、受理の第二正本ではない。Product Ownerによる正式な採用までは「レビュー提案」に限る。
- **関連する横断計画**：[価値・要望・要件](value-needs-requirements-2026-11-01.md)、[価値の実現と検証](value-realization-research-protocol-2026-11-01.md)、[Harness能力増幅・縮退](../harness-capability-lifecycle-2026-10.md)、[TAI #233](https://github.com/hat47x/tai-pleroma/issues/233)。

## 1. 今回の問い

YIのProduct数・Issue数・研究領域を機械的に減らすのが目的ではない。**各製品を選ぶ理由となる主要価値に照らし、どの要求が中核で、どれが用途条件付きで、どれが実証前の拡張候補にとどまるか**を見極める。

「将来の多用途を妨げない」ことと「すべての多用途を標準構成で実装する」ことは違う。「意味の精密さ」と「人が毎回入力・確認する情報量」も違う。さらに、生成AIの低い実行費用は探索を拡張する理由になるが、統合・検証・保守・Owner審査の費用をゼロにしない。

**適正化の対象**は「実装先行」「初期受入への過大な組込み」「他製品/外部Harnessとの重複」「不要な起動・読込み・通知・追加確認」「条件のない汎用化」。**安易に削らないもの**は意味・同一性・不確実性、Source/Revision、業務認可、OS/Hostの実際の機密境界、実処理結果・回復、必要な独立Oracleである。安全な挙動自体を削減せず、必要な用途に必要な方式で実現する。

検討の前提は、TAI/SEI/SUI/TEI/SHO/EKIの役割を分け、外部のAI Harnessが既に持つ会話・計画・定期実行・汎用Tool操作を原則として重複開発しないこと。YIはブランド、TAIは活動をつなぐ製品・シリーズ構成拠点であり、新しい中央Runtime/Hostではない。MMI、TEI Studio、CSWなどの製品分類は[TAI #73](https://github.com/hat47x/tai-pleroma/issues/73)で未決を保持する。

## 2. 一次照合：価値、最低限の体験、過剰化リスク

下記は確認した価値文書・主要Issueから作成した**監査仮説**であり、各Product要件の採否ではない。

| Product | 主要価値と最小の体験 | 初期成立条件へ混ぜない高度化候補 | 必ず保全する区別／関連Source |
| --- | --- | --- | --- |
| **TAI** | 目的→必要な能力の利用→成果・未決→別回での再開。外部Harness＋既存CLI/ファイルに対する増分を確認 | 常時Agent、全Product必須起動、巨大な製品Registry、全製品一括ビルド、汎用Handoff Engine | 活動の連結≠第二の判断/実行正本。[#168](https://github.com/hat47x/tai-pleroma/issues/168)・[#73](https://github.com/hat47x/tai-pleroma/issues/73)・[#74](https://github.com/hat47x/tai-pleroma/issues/74)・[#271](https://github.com/hat47x/tai-pleroma/issues/271) |
| **TEI** | 専門家が読めるData/Rule/Function→最小の実機能→変更・再生成時の意味保全 | 全分野の特殊構造を初期Coreで実装、全Target同時実装、常時Plugin hot-swap、全機能の高度UIを前提 | 意味の受理≠Source byte一致≠Runtime許可。単一Go binaryを基本に、Target/Hostの必要に応じ拡張。[Value](https://github.com/hat47x/tei-platform/blob/main/product/value/TEI_PRODUCT_VALUE.md)・[#2619](https://github.com/hat47x/tei-platform/issues/2619)・[#1223](https://github.com/hat47x/tei-platform/issues/1223)・[#1127](https://github.com/hat47x/tei-platform/issues/1127) |
| **SEI** | 小さい入力で判断・根拠・未決を残し、時点が変わっても正しく再開 | 多領域Method、全面的な認識ルーティング、初回から全意味要素の入力強制 | Observation/Interpretation/Decision/Authority/ResultとUnknownを混同しない。[First Slice](https://github.com/hat47x/sei-cognition/blob/main/product/interaction/SEI_FIRST_USABLE_PRODUCT_SLICE.md)・[#660](https://github.com/hat47x/sei-cognition/issues/660)・[#767](https://github.com/hat47x/sei-cognition/issues/767) |
| **SUI** | 保留・異論・違和感を保持して構造化し、元資料と過去の見立てに戻る | すべての文化的認知法を標準機能化、最速要約競争、全探索へ単一の評価軸・確定Gateを適用 | 早い合意に潰さず、人の採否と生成的探索を分ける。[ADR-0089](https://github.com/hat47x/sui-sensemaking/blob/main/01_Plans/adr/ADR-0089-product-value-canon.md)・[ROADMAP](https://github.com/hat47x/sui-sensemaking/blob/main/ROADMAP.md) |
| **SHO** | 独立して文書を編集・保存・再開し、必要な引用を再解決して説明・納品する | 論文の自動理解からコード実装までをSHOの内蔵機能にする、全形式/組版を初回必須、専用Document Graph DB | 文書作業成立・出典解決・説明レビュー・納品承認を分ける。[#1](https://github.com/hat47x/sho-composer/issues/1)・[#4](https://github.com/hat47x/sho-composer/issues/4)・[#7](https://github.com/hat47x/sho-composer/issues/7)・[#8](https://github.com/hat47x/sho-composer/issues/8) |
| **EKI** | 制約付きTaskを依頼→Worker実行→同一Attemptの結果を独立確認→故障時の収束 | 学習型Scheduler、複数管理クラスタ、全組織の高度公平性・市場・連邦型を初回必須 | Task≠Attempt、Claim≠AcceptedResult≠業務Effect、端末所有者の停止権。[Value](https://github.com/hat47x/eki-fabric/blob/main/product/value.md)・[#58](https://github.com/hat47x/eki-fabric/issues/58)・[#381](https://github.com/hat47x/eki-fabric/issues/381) |

**補足：**
- TEI #1223は「目標アーキテクチャ」と「実際の移行」の区別が既にある。無停止を必要とする配備に必要な実証まで否定しない。
- TEI #2386は単純な組織から必要に応じ履歴・代理へ拡張する方針を持つ。複雑さの**条件付き導入の良例**であり、一律の削減候補ではない。
- SUIの認知支援計画とEKI #19の学習型Schedulerには、既に実務比較・Shadow評価・非昇格が書かれている。研究を廃止するのでなく、初回必須への混入を防ぐ。
- SHO #7の「リンク一覧だけでも完成体験」、SEIのresume-first、TEI #1127、EKIの委任MVPは、価値から実装を逆算できる起点。
- TAI #233にある安価なモデルによる大量並列探索と、本書の**実装義務の選別**は対立しない。

## 3. 判定単位：構想・Requirement・Realization・Evidenceを混ぜない

各候補に対して、少なくとも次の独立した問いを置く。

1. **Value / User Job**：誰が何を成し遂げるために必要か。本人が望まない・何もしない選択も、TAIなどでは正当なOutcomeか。
2. **Minimum experience**：既存Harness、通常のテキスト、CLI、既存Host/Providerと比較し、最小の成立体験は何か。
3. **Invariant / Obligation**：意味・業務権限・副作用・機密・結果を守るため省略できない条件は何か。何らかの実現方式を唯一の手段と誤認していないか。
4. **Candidate realization**：どの技術がその要求を満たすか。独立Plugin/Adapter/Providerへの移譲や、必要時だけ起動・詳細読込みする選択は可能か。
5. **Incremental effect**：導入による誤判断減少、引継ぎ改善、再作業削減、所要時間、確認回数、維持費、失効対応をどう観測するか。
6. **Counterexample / Reversal**：機構を外しても目的を達成できる例と、外すと守るべき条件が破れる例は何か。後者が成立する用途・条件を限定できるか。

分類ラベル（正式Product Schemaではない）：`core`、`conditional`、`research-only`、`delegate`、`overlap`、`simplify-or-phase`、`retirement-candidate`、`unknown`。

- `core`：主要価値に不可欠であると明確に示せる。
- `conditional`：特定の可用性・機密性・対象領域・規模・期限等の条件で不可欠。条件と代替を記す。
- `research-only`：価値仮説はあるが実利用へ要件化する証拠が不足。
- `delegate`：既存Harness/Host/Provider/他Productに保有者がいる。呼出しと資格だけを扱う。
- `overlap`：二重実装・第二正本になり得る。既存Ownerへ集約する案を出す。
- `simplify-or-phase`：簡単な実現・遅延読込み・段階的導入で価値を満たす可能性。
- `retirement-candidate`：比較の結果、追加価値がなく、移行・復旧の条件が定まれば撤去候補。
- `unknown`：Sourceや現在の実装・対象母集団が不足し判定不能。未調査を不要としない。

**分類は絶対的な優先度・点数ではない。** 同じ要件でも低リスクのローカル利用では条件付き、高機密の業務では中核になる。技術的な複雑さだけを責めず、必要な安全保証は正しく維持する。

## 4. 複数エージェント・モデルの分担と責務

統括Issue [#422](https://github.com/hat47x/tai-pleroma/issues/422)を**coordination board**として用いるが、新しいTask DBやAgent Runnerは作らない。作業状態はIssue/PR/既存Gitだけで足りる範囲から開始する。

### 作業Lane
- **VA-00**：Coordinator。Source取得可否、対象母集団、重複Issue、割当、mainの変更、共通ファイル競合を確認。作業者の実モデル・利用可能なツールを報告。
- **VA-TAI / VA-TEI / VA-SEI / VA-SUI / VA-SHO / VA-EKI**：製品別一次評価。必ずProduct Value/非目標と現行Requirements/Issueを照合し、事実・推測・提案を別欄にする。
- **VA-X**：独立反証者。一次評価を作ったAgentとは別Context・別モデル（可能なら別提供元）で「過剰ではない場合」「既存手段で足りる場合」の双方を示す。単なる同意・要約は禁止。
- **VA-E**：Evidence/安全性レビュアー。exact revision、実試験、holdoutと独立Expected、対象全件性・開示制約・現行Authority・Business Outcomeへの誤昇格を確認。
- **VA-I**：Integrator。矛盾表、残余論点、対象Issueへの最小差分を統合。正式な意味/設計受理はProduct Ownerの仕事。

モデルが利用できない場合は`not-available`、外部HarnessやAgentを実起動していない場合は`NOT RUN`と書く。同一モデルでも別コンテキストなら独立した推論経路は作れるが、それだけでモデル多様性・根拠独立性が成立するわけではない。同じ資料から学習したモデル複数の合意を「独立した実証」と数えない。

### 完了票（IssueコメントかDraft PRの一表。独自の必須DBは設けない）

```text
Lane / Issue / Role / Agent-model (known or unknown)
Repository / exact source commit / file-section / observed_at / coverage limits
Value / concrete user job / minimum viable experience / alternatives
Requirement or design claim / proposed classification / applicable conditions
Invariants that must survive / negative example if removed
Actual evidence (static, synthetic run, integrated, real use, human accepted)
Ablation baseline vs candidate / added setup, context, review and maintenance cost
Opposing assessment / unresolved / recommended disposition / Owner to decide
Changed files and PR / tests actually run / NOT RUN / disclosure scope
```

各Laneの出力は**再利用できる短い表と必要な原典リンク**を優先する。最初から全製品のIssue全文や大きなモデル定義を外部Harnessへ一括投入しない。必要な製品Skill/CLI/詳細資料だけ発見・起動・読込み、通常のファイル・CLI・手作業で足りる場合はTAI統合機能を追加しない。

## 5. 実作業の基本ルール

1. **一つの変更を一つのOwnerに**：Product固有要件・意味の正本は各repo。横断担当が別repoを勝手に更新しない。同じIssue/ADR/PR/作業パスを複数Agentで同時編集しない。異なるBranch・Worktree・ドラフトで独立作業。
2. **固定したSourceと閲覧の限界**：full SHA、原典URL/範囲、取得日時、検索母集団、Access/partial/unknownを記録。別時点のIssueとmainを一つのsnapshotと呼ばない。新しいHeadで必要な部分を再確認。
3. **自由探索と後段評価を分離**：候補・反例・Issueの固定上限は設けない。探索の各段階へ包括的な採否Gateを置かず、正式要件・実装・配布へ昇格するときだけ必要な反証とOwner判断を求める。
4. **批判の責任**：VA-Xは「削ると壊れる最小例」「残すと不必要に重い最小例」「実在代替」を提案。VA-Eはソースを再読し、実行できるものだけ実行、未確認を記録。モデル多数決や自己テストだけで採否を確定しない。
5. **公平な比較**：同じ利用仕事・入力Source・Revision・Tool/Host・Authority・評価基準。独立Expectedを候補作成前に固定する。B案だけ多い資料・Toolを使った結果を増分価値と呼ばない。
6. **損失をゼロにしない**：単純化によってSource/Meaning/NULL/Unknown/Scope/Order/Identity/Disclosure/Actual Effectが落ちたら、必要なら不適合。情報を省くのは「用途が不要」「許容されたLoss」「安全な代替あり」の場合だけ。
7. **Toolと権限**：Agentが読めること≠外部LLMへ送ってよいこと。read-only API≠Raw開示許可。OS/Hostでアクセスとegressが本当に制限されていない機密Profileは未実証。[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)に委ね、原文/秘密/内部Oracleを公開Issueへ転載しない。
8. **変更と実行は別資格**：静的レビュー、合成PASS、製品E2E、ユーザー成果、Owner受理、本番作用を区別。新中央Host、第二Meaning/Authority、独自Runner/大きな共通Schemaを適正化のために導入しない。
9. **異論を消さない**：製品担当・反証担当・Evidence担当の判断が割れた場合、適用範囲と根拠の違いを明記してOwnerへ提出。レビュー票には強い代替案・拒否理由を残す。
10. **後からの失効**：世界・Source・生成器・Consumer・契約・Host/Grantが変わったとき、歴史的な正しい試験を消さず、現在用途へ適用できるかを分離。全再実行も無検証再利用も唯一の正解としない。

## 6. 段階・評価票・受入（新しい技術Gateではない）

| 段階 | 最小の成果 | まだ主張しないこと |
| --- | --- | --- |
| **G0 Inventory** | 六製品＋周辺候補の価値定義／現行main／代表Issue／Scope未調査の一覧。分類が未確定のものは未確定のまま | 全リポジトリの完全棚卸し・全Issue判断 |
| **G1 Map** | 価値→成立仕事→要件→実現→証拠→Unknownを結び、製品ごとに重要2〜3件の適用条件を比較 | 概念分類だけで廃止/正式要件化 |
| **G2 Compare** | 少なくとも高優先2例でbaselineと候補の正負対。可能なら別モデルで独立再現 | 同じモデル・入力の複数回実行を独立ユーザー成果とすること |
| **G3 Review** | VA-X/VA-E反証と、Ownerの既存Issue/ADRへの変更差分をDraftとして提示 | Product Ownerの採用・merge・本番適用 |
| **G4 Requalify** | 版更新後に必要な差分のみ再比較、古い受入の流用可否と未確認を表示 | 古いPASSが更新版の意味・効果も保証 |

最初の対照候補：
- **SEI**：一判断の再開（普通のメモ、外部AI会話履歴、SEI Resume Brief）。時間・誤再構成・旧判断の誤復活・確認負担。
- **TEI**：小さなCRUD/Rule変更（通常コード、TEI最小DSL、TEIの高度なPlugin合成）。意味保全・簡潔さ・生成/更新後の修正・実DB結果。
- **SHO**：Markdown原文＋通常リンクと、文書参照の固定版・再解決。編集/再開と誤出典・追加入力・レビュー負担。
- **EKI**：ローカル実行・既存ジョブ・EKI Native Worker。転送・再試行・端末復帰・Ownerの停止・結果確認。比較不能な保証水準を同等扱いしない。
- **SUI / TAI**：SUIの保留つき再検討を通常図解と比較し、TAIはHarnessだけと製品を追加した場合の目的達成・通知/質問/起動/引継ぎ負担を測る。

必要な安全条件が異なる案どうしの速さだけを比較して「簡単な方がよい」とは判定しない。結果は**不変条件の合否／利用者成果／保守コスト／実現範囲／Unknown**を別軸で記録し、単一scoreにしない。

## 7. 既存Issueへ還流する差分（新Issueの乱立を避ける）

| Owner | 既存の受け皿 | 追記すべき成熟した判断・追加検証 |
| --- | --- | --- |
| TAI | [#233](https://github.com/hat47x/tai-pleroma/issues/233)、[#168](https://github.com/hat47x/tai-pleroma/issues/168)、[#73](https://github.com/hat47x/tai-pleroma/issues/73)、[#74](https://github.com/hat47x/tai-pleroma/issues/74) | 探索量の拡大と標準要求の増加を区別。最初の横断Skillは必要時起動・遅延読込・既存Harnessのみとの比較を行う。製品台帳・配布は小さい用途から |
| TEI | [#2619](https://github.com/hat47x/tei-platform/issues/2619)、[#1223](https://github.com/hat47x/tei-platform/issues/1223)、[#1127](https://github.com/hat47x/tei-platform/issues/1127)、[#2018](https://github.com/hat47x/tei-platform/issues/2018) | 専門家の認知順・ノイズ最小のDSLと、汎用データ/Plugin/Targetの内部実現を分ける。Go単一バイナリの基本形で価値を確認し、他Target/無停止は用途相対 |
| SEI | [#660](https://github.com/hat47x/sei-cognition/issues/660)、[#767](https://github.com/hat47x/sei-cognition/issues/767)、[#711](https://github.com/hat47x/sei-cognition/issues/711) | 高度Methodより判断の再開、過少・過大確認、現在適用性を先行。認識状態の細分化をすべて手入力にしない |
| SUI | [ADR-0089](https://github.com/hat47x/sui-sensemaking/blob/main/01_Plans/adr/ADR-0089-product-value-canon.md)、[ROADMAP](https://github.com/hat47x/sui-sensemaking/blob/main/ROADMAP.md) | 根拠・異論・保留の実務上の増分をT2で確認し、文化的手法は必要時の選択可能Methodにとどめる |
| SHO | [#1](https://github.com/hat47x/sho-composer/issues/1)、[#4](https://github.com/hat47x/sho-composer/issues/4)、[#7](https://github.com/hat47x/sho-composer/issues/7)、[#9](https://github.com/hat47x/sho-composer/issues/9) | 単独文書編集・保存・出典を第一の成立条件とする。論文→コード実装はTEI/外部Harnessと連携する上位シナリオ |
| EKI | [#58](https://github.com/hat47x/eki-fabric/issues/58)、[#19](https://github.com/hat47x/eki-fabric/issues/19)、[#155](https://github.com/hat47x/eki-fabric/issues/155)、[#381](https://github.com/hat47x/eki-fabric/issues/381) | 実委任/結果/回復・Suitability Gateを優先し、学習型・公平性・クラスタ接続は適用条件を確認して採用 |

各製品で既に同じ方針が採用済みなら、重ねてIssueを作らず**既存決定を引用し、それが初期受入に実際に反映されているか**を確認する。過剰要件に見えるものも、実際はすでに`research-only`・`conditional`かもしれない。反証前に削除候補へ昇格しない。

## 8. 次の判断・既知の未確認

- **Owner判断待ち**：初回の評価対象、標準機能と任意拡張の境界、改訂提案の優先順位、モデル間の反証で決着しない価値判断、各Productの正式要求変更。
- **未確認**：各repoの全Issueとコードの網羅、実モデル2系統での照合、独立ホールドアウト、利用者が感じる価値、実Host/OSでの機密拒否、正式なProduct Ownerの採用。
- **作業を始められる範囲**：公開された価値文書/IssueのSource-static棚卸し、製品別の負例候補生成、別モデルの反証票、合成・read-only比較、既存Ownerへの小さな差分提案。

本計画の成果は**削ったIssue数や生成コード量ではなく、主要価値を失わずに減らした必須の複雑さ、反対に守るべき条件を正しく残せたこと、利用者の利益、未解決の明瞭さ**で評価する。


## 9. 他Workstreamとの具体的な照合（2026-11-04追補）

初回の評価を実際のAgentへ渡せる比較票に落とした：[VA-01：主要価値レビュー・初回反証パケット](../../evaluations/VA-01-product-value-necessity.md)。ここにある分類は**Source-staticの監査仮説**であって、OwnerによるRequirement変更・実テストPASSではない。

### 9.1 TEI：価値への最短経路と拡張機構を別レーンにする

- **専門家可読DSLを先に判定**する。Go単一バイナリは実行/配布の基準であり、日常DSLに`func`/`struct`等のGo構文を強制する根拠ではない。Go式AST、独自構文、Hybrid、DSL→Goコード生成を同じ意味、診断、Source位置、NULL、金額精度、演算順、負例で比較する。構文方式は未採用。
- **Function / Invocation / Trigger / Buildを別概念とし、単一実行バイナリで足りる間は分割しない**。[TEI #1130](https://github.com/hat47x/tei-platform/issues/1130)、[#1097](https://github.com/hat47x/tei-platform/issues/1097)、[#1182](https://github.com/hat47x/tei-platform/issues/1182)を参照。cron/Webから同じ業務Functionを呼べても、TargetのAPI・Credential・Commit権限が同一とは推定しない。異配備・異隔離・ライフサイクルが必要なときだけMulti-Buildを検証する。
- **生成AIに自由にテストを拡張させる足場**は、[TEI #1180](https://github.com/hat47x/tei-platform/issues/1180)が所有するDriver ScenarioのSSOTからCLI/Web/Target別Assertionを派生させる案を再利用する。UI画像差・Host認可・Runtime/Provider差は同一Scenarioの**Target固有試験**として保持し、CLI PASSでWeb PASSとしない。生成AI専用の第二Scenario DB/DSLや、全GUIの即時自動化を初期必須にしない。
- **高速ビルド**は入力・Artifact・Evidence・現在の実行資格の再利用を別判定する（[TEI #2600](https://github.com/hat47x/tei-platform/issues/2600)）。同一Sourceのbyte一致は別ToolchainやGrant更新時の現在資格を保証しない。高速化のため新Cache/Registryを先に増やさず、既存Referenceへ差分試験を追加する。
- **TEI/EKI境界**は、TEIが業務Function・条件・結果の意味を所有し、EKIは選択された委任Taskの資源配置・Attempt・回復を扱い、実Host/Providerが外部Effectとその証拠を所有する。EKI未接続でもTEIの単独業務Functionとread-only検証を止めない。

### 9.2 EKI：高度な資源割当は「リードタイム・復旧可能性・総費用」から段階化

[EKI #58](https://github.com/hat47x/eki-fabric/issues/58)のSuitabilityによる**分散しない判断**は最小製品価値。割当ての候補は、明示された締切、転送、計算、復旧余裕、予算、許可された資源群、過去の実績（あるときのみ）に基づき比較する。相関故障や予定以上の遅延により、廉価なAttemptを繰り返しても締切に間に合わない負例を先に固定する。

- **中核**：合法な配置候補のフィルタリング、利用者のreclaim/opt-out、期限内に完了できない場合の誠実な拒否、Task/Attempt/Result/業務Effectの区別、結果不明時の無条件再実行禁止。
- **条件付き**：Recovery Reserve、複数資源群の予約、公平性、期限接近時の切替。これらが必要なワークロードとローカル実行の対照を示して導入する。
- **研究のみ**：[EKI #19](https://github.com/hat47x/eki-fabric/issues/19)の学習型予測は既存deterministic scoreに対するresidual/shadow比較から開始。MLが配置・業務許可・組織横断の権限を得る仕様にはしない。
- **状態ドリフト修正**：[EKI #381](https://github.com/hat47x/eki-fabric/issues/381)は2026-11-04取得時点でClosed。旧文書の「未配線」を現在の未解決事実とせず、実TaskのE2E・費用最適化・期限内回復の証拠とは別に確認する。

### 9.3 TAI/SEI/SUI/SHO：ユーザーに義務を負わせず、本当に必要な詳細だけを起動

- **TAI**：外部Harnessを活動の入口にし、必要なProduct/Skill/Toolだけ選択・遅延読込する。[TAI Draft #270](https://github.com/hat47x/tai-pleroma/pull/270)のSkill軽量化は設計・配布改善の局所証拠であり、外部Harnessでの利用者価値は別実測。Product単体で足りるならTAI統合フローを起動しない。
- **SEI**：小さな判断のresume-first体験を基準とし、全Methodの記録や認識論的な詳細入力を本人に初回から義務付けない。ただし、Sourceの現在性・Unknown・Claimの対象集合・開示資格が必要な場面は省かない。[SEI #767](https://github.com/hat47x/sei-cognition/issues/767)を研究と実際のユーザー操作の負担で別評価する。
- **SUI**：異論・保留・未解決を保つことで意味形成を支援する。発散時に一律の受理/合意Gateを強制しない。高度な文化的Methodや順位付けは選択できる機能候補であり、実利用で保留/再検討の質が改善するかを対照する。開示範囲を越える投影は禁ずる。
- **SHO**：単独の文書編集・保存・出典照合を成立させる。[SHO #7](https://github.com/hat47x/sho-composer/issues/7)のL0 Markdown文献リンク一覧はPDF・DOI・研究用Graph DBなしで完結する。L1書誌情報→L2本文→L3人の確認した関係→L4開発受渡しは条件付き拡張。原資料を未取得なのに内容を理解したと推定しない。

### 9.4 過剰要件レビューに特有の誤判定

**誤った削減**：危険な業務Effectの直前認可、未知のSource依存、情報非開示、Task/Attempt/結果不明の回復判定を「複雑だから削除」とする。

**誤った高度化**：データ取得・テスト・Agent分担・文書引用・スケジューリングの各境界に、既存Ownerが既に保持する資格・正本を複製する共通Controller/DB/Pluginを追加する。

**判定手順**：同じUser JobでB0既存手段／B1必要な1製品／B2高度化を比較し、不変条件が破れるケースでは設計方式を見直す。利用者の確認負担・起動時間・再開時間・編集しやすさ・失敗復旧・維持費を別に観測。差が確認できない場合は価値がないと断定せず、未確認の適用条件と次の反証を残す。

## 10. 実施順（既存Phase・各Product Ownerを変更しない）

- **VA-G0**：TAI #422をCoordinator、[VA-01](../../evaluations/VA-01-product-value-necessity.md)を初回の作業票として、対象Source・版・Issue状態のドリフトを記録。代表Issueの一次レビューを、全Issue/全コードの網羅と表現しない。
- **VA-G1**：TEI Driver Scenario（VA-T2）、EKI Suitability/期限内回復（VA-E1）について、作成担当とは別のVA-Xが「省くと壊れる」と「増やさなくてもよい」の両方を事前登録。SHO L0/SEI resume-firstは独立に進める。
- **VA-G2**：実Fixture・実Targetと独立Expectedを確認し、各Product既存Issue内の試験へ接合。実行できない場合はNOT RUN。Source-staticから推定した結果を実験PASSと呼ばない。
- **VA-G3**：VA-EでScope・環境・事実を点検し、VA-Iが製品の既存Issue/ADRへの最小差分を提案。Owner未受理なら確定しない。複数モデルの一致だけで製品要件を変更しない。

**計画上のExit**：少なくとも2件の独立反証とSource/Evidence点検を、Owner判断可能な形で記録し、「標準で残す／用途で選ぶ／研究で続ける／他Ownerへ移す／撤回候補／未確認」を理由付きで提案する。プロセスのための新Harness・検証エンジン・中央評価DBを製品要件化しない。


## 11. 初回実証手順：VA-02への受け渡し

[VA-02：製品独立性を保った初回実証・証拠引継ぎ手順](../../evaluations/VA-02-cross-product-first-run-protocol.md)を、既存[VA-01](../../evaluations/VA-01-product-value-necessity.md)の**試験実行側の入口**として追加する。VA-01は価値と過剰要件の判定票、VA-02は実行ラダー・停止条件・Expectedと観測の取り違えを防ぐRunbookであり、Product固有のテスト/Meaning/Authorizationの正本ではない。

- **依存を不必要に直列化しない**：TEIのtest-local Go Scenario→保存Scenario→CLI→Webは段階的検証。SHO Markdown L0保存やEKIの「分散しない」判断はTEI/TAIの全面完成を待たず並走可。TAI外部Harnessや製品横断Handoffは、それぞれの単独製品証拠を利用する任意の後続検証とする。
- **7段階の資格連鎖**：Declared/Available/Resolved/Eligible/Observed effect/Received/Qualifiedを個別記録。説明上の能力、実CLIの存在、実行資格、Commit後観測、同一AttemptのConsumer実Read、Owner品質受理を混ぜない。
- **独立Expected先行**：VA-02 V02-01〜09に、未実装CLI、Web 403、1,000件上限、POST後503、A→B→A、Claim ACKのみ、期限内復旧不能、SHO出典未解決、Grant失効を置く。全Caseは現段階では**NOT RUN**。
- **Exit条件**：VA-T2とVA-E1の双方について実測正負例、VA-X反証、VA-E Source/Evidence照合、比較可能なBaseline、Consumer/Reader観測を揃える。未実施・未受理を合格へ昇格させない。

既存[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)、[TEI #1180](https://github.com/hat47x/tei-platform/issues/1180)、[EKI #58](https://github.com/hat47x/eki-fabric/issues/58)へ実証のOwnerを返す。横断#422と本計画へ第二のRegistry、別Scenario DB、Runnerや実認可を実装しない。


## 12. AI-first実証入口の再判定（2026-11-04）

既存[VA-02](../../evaluations/VA-02-cross-product-first-run-protocol.md) §6を参照。TEI mainには **6-Step保存済みDriver Scenarioと限定CLI verify/generate/run/checkの実ファイルが存在する**。#1180の初期説明を根拠に「保存Scenario全体が未実装」とは扱わない。これらのSource確認と、実Goテスト・実Web E2E・実Provider Writeの成功は別の証拠階層。

横断G0/G1で、(a)言語/Operatorテスト候補（[TEI Draft #2813](https://github.com/hat47x/tei-platform/pull/2813)）、(b)シナリオテスト正本（既存保存Driver Scenario）、(c)Target/Host実行結果を分離。Candidate JSON追加を正式な業務Scenario、独立Expected、実Web Coverageへ自動昇格しない。[TEI Draft #2811](https://github.com/hat47x/tei-platform/pull/2811)と[TEI #1180](https://github.com/hat47x/tei-platform/issues/1180)の既存Owner・Issueを再利用し、第二Scenario DB/AI専用Runnerは作らない。

**初回実証の順序**：AI-EXT-01（独立Anchorを維持したJSON候補拡張）、AI-EXT-02（既存6 Stepの版固定CLI実行とfail-closed）、AI-EXT-03（Code/Rule/データ/Scenario/Target/Providerの分母を別管理）。その後、Web Host/実Provider/Consumer実受領に進む。対応なし・未取得・分母不明は未検証。AI生成Case数の増加をCoverage率や製品価値の向上と同一視しない。

**現状**：計画とSource-static照合のみ。各AI-EXTの実行、独立Oracle受理、実Web/OS/ProviderのE2E、横断価値測定はNOT RUN。

## 13. VA-COND-01：用途相対の価値と文書ドリフトを同じレビューに束縛（2026-11-04）

[VA-COND-01：用途条件付き能力・Source状態ドリフト](../../evaluations/VA-COND-01-conditional-capabilities-and-source-drift.md)を、VA-01（要件の必要性）・VA-02（実証資格連鎖）に追加する**独立した用途適合性の判定軸**とする。既存の[TAI #424](https://github.com/hat47x/tai-pleroma/issues/424)（9 Lane整合性監査、S4は同一モデルの別Context）と[TAI #425](https://github.com/hat47x/tai-pleroma/issues/425)（TAIのF1/F2/F3所見）を再利用し、第二のIssue/ADR台帳・監査Runtimeは設けない。

### 実際のUser Jobを先に固定する
- [EKI Product Value](https://github.com/hat47x/eki-fabric/blob/main/product/value.md)の委任の核は、長時間バッチだけでなく、AI推論・ツール実行、隔離実行、軽量常駐認知の外面へ広がる。**高速通信・マルチモーダルを一律に「過剰」としない**。ただし必須化は用途別：有限Job→従来型Task/Artifact、低遅延イベント→期限・jitter・再送/順序/Backpressure、Media→受信・同期、常駐→有限Grantの更新とLocal Governor、を個別の負例で評価する。
- TEI/TAI/SHO/SEI/SUIの拡張要件も同様に、B0既存Harness/ファイル/CLI、B1単体製品の最小能力、B2高度構成という**同じUser Job・権限の下でのみ**比較する。要求を満たすB0/B1を退役・置換するためにB2を導入しない。
- **省略できない保証と選べる実装**を分ける。Source/Meaning/Scope・Host/Provider認可・実Effect・独立Consumer Read・期限内回復は必要な用途で保全するが、それらを守るために一律の中央Host/Registry/Process・同じ通信方式が必要とは推論しない。

### 既存監査で明らかになったドリフトへの対応
- TAIロードマップのPR #169の古い未統合表示を、2026-11-02 mergedの状態へ改める。ただしmergeはOwner受理・ユーザー価値・実Host接続の証拠ではない。
- TEI #2488 ClosedとPR #2489 mergedを、現行のrecord/string全Consumer成功と同義にしない。
- 2026-10-29のSCN-001 Owner判断に従い、現段階の開発評価者を生成AIとして記述し、実物の人間レビュー・公開・Authority資格は別の後続工程とする。
- **同一モデルの別Contextによる文書整合性チェック**と、異なるモデルを使った独立反証、実Provider/OS/Consumerの実証はそれぞれ別のEvidence tier。TAI #424の監査完了を本Issue #422の価値比較完了へ転用しない。

### G0〜G4への最小差分
G0では監査所見・最新Source状態・各Productの実Valueを再取得。G1ではVA-COND-01の用途条件とB0/B1/B2の候補を登録。G2では必要になったデータ様式と時間制約だけを測り、独立Expectedを確保。G3では各Product Ownerへの**差分のみ**返す。G4では経路/Provider/Grant/Target/Source変更に対する必要な再確認だけ行う。新Quality/Transport共通Engineをこの監査から作らない。

**成熟度**：Source-static／設計提案。実EKI low-latency benchmark、Media Data Plane、異モデル反証、正式なTransport選択、Owner受理は **NOT RUN**。

## 14. VA-00実監査をVA-04の入力閉包検証へ接続（2026-11-04）

[VA-00調整台帳・実監査記録 TAI #424](https://github.com/hat47x/tai-pleroma/issues/424)では、9 Lane（TAI/TEI-A/TEI-B/SEI/SUI/SHO/EKI/MMI/CSW）のS1〜S3、別担当S4照合、#422への集約が完了。意味的Owner判断事項F2は59件（高20/中28/低11）に整理済み。これは**文書/Issue/ADRのSource-static監査**であり、コード全域・実Target・実ユーザーの製品価値受入ではない。別contextによる再点検は行われたが異モデル実証ではない。TAI #424の機械的F1修正PRもOwner判断前に無断mergeしない。

この結果を[VA-04：入力閉包と契約発見の事前確認](../../evaluations/VA-04-evidence-readiness-preflight.md)へ接合し、[VA-02](../../evaluations/VA-02-cross-product-first-run-protocol.md)のP0/P1に次を追加する。

1. **Declared / Discovered / Consumed / Asserted / Eligible+Received**：manifestの宣言、ファイル発見、Parser/Providerの実読込、Assertionの対象、現在実行許可と実Consumer受領を区別。fingerprintや終了コード0のみで完全性を保証しない。
2. **TEIの局所事実を条件付きで取り込む**：[TEI #2822](https://github.com/hat47x/tei-platform/issues/2822)（宣言0件でもvalidate成功）、[#2823](https://github.com/hat47x/tei-platform/issues/2823)（未読込Sourceが黙って無視される）、[#2824](https://github.com/hat47x/tei-platform/issues/2824)（19 command/文書13件、discoveryのschema契約不明）からPF-01〜04を作成。製品Issueにある実再現とVA-04の未実行を別記。
3. **EKIの結果値の衝突を未決として扱う**：[EKI #698](https://github.com/hat47x/eki-fabric/issues/698) EKI-CA-02にあるSuitability ADR 4値と実装3値の差を、EKI #58のVA-E1へ反映。NOT_SUPPORTEDを実Suitability戻り値として固定しない。Admission/Policy拒否と実装による非分散判定は別証拠。
4. **独立レビューと研究の責務**：F2 Owner判断はVA-00各検査Issue、価値必要性はVA-01、実証はVA-02、Claim上限/入力閉包はVA-04。議論の横断連携により第二Validator/Runner/Host/Authorityを作らない。

**G0更新**：製品別 full SHA、実CLI/Plugin/Provider版、検査対象Scope、取得済み/未読込、独立Expected、実行された環境を確認。Sourceが不完全なら全体PASSを禁止しつつ、許容された公開合成テスト候補の探索は継続可能とする。


### 監査由来の未決を実験依存へ絞る（整合性監査を再実施しない）

[TAI #424 のS6判断項目59件](https://github.com/hat47x/tai-pleroma/issues/422#issuecomment-6623059604)を実験ごとに次のように扱う。**Blocking**＝対象・安全・独立Expectedが決まらず当該実験が成立しない、**Conditional**＝明記した範囲だけ進行可能、**Nonblocking**＝実験自体を止めない、**Unknown**＝現在のSourceでは判定不能。分類はIssueの優先度や正式Requirementではなく、指定した実験の開始条件に相対的。

| 対象実験 | S6で判明した不一致／既存Owner | 最小の実験条件と判定 |
| --- | --- | --- |
| **VA-T2：TEI Scenario→CLI/Web** | [TEI #2823](https://github.com/hat47x/tei-platform/issues/2823) 未知Source rootが未読込、[TEI #2825](https://github.com/hat47x/tei-platform/issues/2825) 認証Ownerの記述差 | **Conditional**：限定Source/Stepを固定したCLIの静的/合成検査は継続。完全なSource CoverageやWeb Host AuthのPASSはSource closure/実Hostが未確認なら**Blocking** |
| **VA-E1：EKI Suitability** | [EKI #698 EKI-CA-02](https://github.com/hat47x/eki-fabric/issues/698)：提案ADRの4状態と実APIの3状態が不一致 | **Conditional**：実API 3値とAdmission/Policy拒否を別結果として限定比較。NOT_SUPPORTEDを実戻り値と主張する試験、正式Contract採用はOwner決着まで**Blocking** |
| **VA-H1：SHO単独Markdown保存・Reader** | [SHO #15](https://github.com/hat47x/sho-composer/issues/15)：G1b/G1c/G1-SHOの意味に衝突 | **Nonblocking**：L0の保存・再開は実験可能。実MMI RunnerをSHOの実Reader/根拠再解決済みと呼ぶ資格はOwnerの定義が確定するまで**Blocking** |
| **VA-C1：SEI再開** | [SEI #792](https://github.com/hat47x/sei-cognition/issues/792)：Method根拠十分性と製品Requirementsの参照関係に未決 | **Conditional**：小さいResume/Unknown維持は限定比較。全Method・全域のSource十分性を要求/実証済みとするのは**Blocking** |
| **VA-SUI-01：SUI異論・保留** | [SUI #3384](https://github.com/hat47x/sui-sensemaking/issues/3384)：SafeMode下の本文読取に関する説明が現挙動と相違 | **Conditional**：非機密の公開合成データで保留維持を確認。実Private Rawの安全なTool/Agent読取はコード・Host/egressが未検証なら**Blocking** |
| **VA-A1：TAI製品分類・外部Harness** | [TAI #73](https://github.com/hat47x/tai-pleroma/issues/73) 分類・公開境界がOwner未決 | **Nonblocking**：既存Product CLI/Skill単独の比較は可能。正式なYIシリーズ全体の公開分類・製品同一性・一括配布はOwner判断が必要 |

**判断の節約**：各Laneの既存Issueに「実験ID／差分の未決／試験で固定する代替条件／Owner／再確認条件」をコメントで返す。別F2台帳やProduct共通のGate Engineは作らず、59件全体をG2ブロッカーにしない。VA-Xの反証は、まずBlockingか否かの具体的負例に集中させ、モデル多数決や文書の引用数だけで完了としない。

**ケースID訂正**：[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)の重複したVA-S1を、SUIはVA-SUI-01、SHOはVA-H1に統一した。過去の固定済み監査コメントは書き換えず、最新の試験票で誤読しないための編集上の修正である。

**後続研究**：EKIの軽量認知・低レイテンシ・マルチモーダル通信では、Workload/データ様式に応じたTransport Profile選択を比較候補とする（[VA-COND-01：用途相対と通信条件](../../evaluations/VA-COND-01-conditional-capabilities-and-source-drift.md) §2/§5）。現行実装・採用プロトコル・低遅延の保証は未確認であり、初期EKI Suitability/結果受理の合格条件へ無条件追加しない。

本追加は計画反映。VA-04の再現試験、AI-EXT/CLI実行、Web/実Provider、独立Oracle受理、Ownerの要求採用は**NOT RUN**。

## 15. 既存の試験資産で検証する「必要最小限」と独立判別力（2026-11-04）

製品価値の検証は**新しい構成要素の数**でなく、現行の最小手段からの増分と、守るべき条件を満たす証拠で判断する。[VA-02 §8](../../evaluations/VA-02-cross-product-first-run-protocol.md)と[VA-04 §6](../../evaluations/VA-04-evidence-readiness-preflight.md)に実験手順を集約し、横断側で新しいScenario SSOT／Build Registry／Runnerを設けない。

- **TEI：AI-firstテストは最小増築を優先**。[TEI #2828](https://github.com/hat47x/tei-platform/pull/2828)の既存6-Stepと限定CLIを使ったtest-only JSON候補追加を最小案とする。生成Case数ではなく、独立Expected、既知Mutantの検出、固定Anchor/Plan失効、Source/TargetのCoverage分母で評価する。[#2811](https://github.com/hat47x/tei-platform/pull/2811)の設計と[#2813](https://github.com/hat47x/tei-platform/pull/2813)のPipeline JSON候補は**異なるConsumer**であり、一つの万能Test DSLへ性急に統合しない。
- **TEI：安全性を削らず実装機構を減らす**。[TEI #2819](https://github.com/hat47x/tei-platform/pull/2819)で、宣言Source D1と実Go builder入力D2の相違が現行Selectorで拒否されない局所ケースが確認された。DigestやReceiptを追加で重複保存するのでなく、**実際にビルドで消費した入力集合との一致**を必要なClaimの不変条件にする。修正/実証Ownerは[TEI #2595](https://github.com/hat47x/tei-platform/issues/2595)。この局所負例を全Target E2Eの失敗や完了と推定しない。
- **TAI：Skillの説明削減と能力の削減を混同しない**。[TAI Draft #270](https://github.com/hat47x/tai-pleroma/pull/270)と[SK-02の既存対照](https://github.com/hat47x/tai-pleroma/blob/docs/yi-harness-skills-20261102/evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)を用い、Harness＋Product CLIだけのH2と、必要なProduct Skillを実ロードするH3を同一条件・四独立Sessionで比較する。既に報告のあるTEI Product Skillの限定read-only CIと、TAI Harness上でのTool呼出し・文書負担・利用者成果は別資格。Skill実Loader/Token/人手費用を観測せずに「Skillが不要」「軽量化で価値向上」と断定しない。
- **共通の停止・進行規則**：未読込Source・不明Grant・Builder入力差は、その証拠を必要とする**実行・納品Claimだけ**を止める。許可済みの静的調査、AI候補生成、SHO L0編集、SEIの限定再開、SUIの公開合成での保留検討まで一括停止しない。新しい万能Gateを導入せず、TAI #424のF2と各Product IssueにOwner判断を残す。

**証拠の現在地**：#2828は実テスト候補PR、#2819はProduct側の限定的な再現報告、TAI #270はSK-02実験を定義済み。しかし本横断PRでの二Case実走、異モデル反証、TAI H2/H3実Harness、User Job増分、各Product正式受理は **NOT RUN**。

## 16. 11月5日の成熟成果：主要価値と内部成熟度を別々に検証する

[TAI #422への11月5日VA-TEI受渡し](https://github.com/hat47x/tai-pleroma/issues/422#issuecomment-6655780152)と[TEI #1119](https://github.com/hat47x/tei-platform/issues/1119)を、**価値実証の着手順**に具体化する。新しい共通Gateや第二の正本を作らず、各Productが持つMeaning・Provider・テストのOwnerに戻す。本節は2026-11-06時点のSource/Issue静的照合による計画案であり、下記実験の実行・正式受理ではない。

### 16.1 TEIの4経路：価値への必要条件を局所化

| 経路・比較 | 同じUser Jobで比較するB0/B1/B2 | 必須の負例と資格 | 他経路を止めない条件 |
| --- | --- | --- | --- |
| **A：VA-T2-R／Source→Model→CLI Read** | B0＝通常のコード・資料調査、B1＝TEI固定Sourceの実CLI読取、B2＝AIテスト拡張やStudio/Skill | Source宣言・発見・実読込・解析・対象Scope・Warning/Unknown・独立Expectedを別観測。TEI #2822〜24の空/未解析Source、#1180の限定Scenarioを使用 | 読取だけなら実DB Commit、EKI分散、Self-buildの完成を要しない。TEIの単なるCatalog件数やvalidate okで完全性を主張しない |
| **B：VA-T2-W／Function→Command→実DB Effect** | B0＝明示SQL/既存Provider、B1＝TEI Function/Commandと実PGを一件接続、B2＝複数DB/移行・無人Workflow | [#2853](https://github.com/hat47x/tei-platform/pull/2853)は実PG CAS＋Invokerの局所進捗。[#2854](https://github.com/hat47x/tei-platform/pull/2854)はABA後の別Key再適用を示す負例。元OperationID／Current Grant／実Commit結果／Receipt／別Connection再読取／Consumerを分離 | Bの実書込み資格はAやSHO単独編集の完成条件ではない。Commit応答喪失は「未作用」でなくunknown、無条件の新Key再試行はしない |
| **C：VA-H1・TEI Studio／SHO Authoring** | B0＝通常のMarkdown等、B1＝SHO単独の保存・再開／TEIモデルの最小編集、B2＝UI Kit・複数Target・高度論文連携 | Sourceの版・引用位置・権限、表示成功と編集保存／実Effectを分離。[TEI #997](https://github.com/hat47x/tei-platform/issues/997)は案件UIの入替可能性、SHO #7はL0からの段階化を評価 | GUI価値を測るときは実編集体験が必要だが、CLI/Read、実PG縦切りを待たせない。SHO L0にTEI Studioや高度PDF解析を義務化しない |
| **D：TEI全体Self-build** | B0＝現在のGo Buildと既存Plugin SB-3、B1＝代表TEI Artifactの標準Graph→実入力→出力の一対一対応、B2＝全Stage/複数Targetの再現 | [#2831](https://github.com/hat47x/tei-platform/issues/2831)／[Draft #2877](https://github.com/hat47x/tei-platform/pull/2877)のSB-A/B/C。nested moduleの依存欠落・実Builder入力の不一致を検出 | G4内部成熟度の並行評価であり、A/B/Cの最初のユーザー価値比較へ新たなHard dependencyを追加しない |

**初回二試行**：VA-T2-Rは「既存資料／実TEI read-only CLI」を、VA-T2-Wは「同じ業務Functionを既存SQL/Provider／TEI Command＋実PG」で比較する。両者に独立Expectedと同じPurpose/Source/必要権限を指定し、結果の正確性・偽成功・保留の正確さ・作業手数・時間・再確認の費用を別列とする。現在のGitHub上の局所CIや実PG証拠を横断試験実施済みとは数えない。

### 16.2 「必要な複雑さ」と「初期に義務化しない複雑さ」

| テーマ | そのUser Jobでは省けないもの | 条件が成立するまで初期の全体前提にしないもの・既存Owner |
| --- | --- | --- |
| **DB移行・旧新並走** | Expand→Backfill→Validate→Cutover→Contractの各段階で、旧/新Client共存、業務キー/物理PKと履歴、再開/rollback、独立観測、Ownerの正本切替判断を別確認。Migration成功ログだけで完了としない | 通常のread-only・一件PG Commandを実証する前に全汎用CDC/ETL・異種DB移行を要求しない。[TEI #2555](https://github.com/hat47x/tei-platform/issues/2555)の同一機械PG3インスタンス限定実測と異種DB/本番未実施を分け、DB/正本切替Ownerへ |
| **Plugin・Build形態** | Contractの意味と版、選択したProvider/Targetの実依存閉包、Host権限とProviderの外部Effect、未選択Plugin非干渉、selected nested moduleの実Build成立 | 一つのPluginを小Interfaceごとに分割したり、動的Hot-swap/全Target常時Buildを初期義務にしない。[TEI #1251](https://github.com/hat47x/tei-platform/issues/1251)、[#951](https://github.com/hat47x/tei-platform/issues/951)、[#2831](https://github.com/hat47x/tei-platform/issues/2831)へ。凝集度の高いBundleの配布と実選択/Artifact組込を別に検証 |
| **生成AIの提案と実行** | AI候補のSource/引用/Revision、未確定のまま保持する曖昧さ、独立検査、Owner意味受理、現在のHost/Provider認可、Execution Receipt／独立Read | AI候補を直接Providerへ作用させる汎用Autonomous Runtime、第二Meaning Registryは採用しない。[TEI #267](https://github.com/hat47x/tei-platform/issues/267)、[#988](https://github.com/hat47x/tei-platform/issues/988)、[#1174](https://github.com/hat47x/tei-platform/issues/1174)の責務を維持 |
| **Tool/Skill・EKI** | Product単独の利用価値と、実Skill Loaded/必要Tool実Invoke/実Consumer受領/Grantの現在資格を区別。EKIは委任・Human-first・Task/Attempt/Resultを保持 | 外部Harness全件常時Load、全Jobでの低遅延マルチモーダル、全件分散/学習Schedulerを義務化しない。[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)、[Draft #270](https://github.com/hat47x/tai-pleroma/pull/270)、[EKI #58](https://github.com/hat47x/eki-fabric/issues/58)の比較に委譲 |

**過剰削減の反証**：Read側で未解析Sourceを「0件」、実PG側でCommit不明を「失敗だから新Keyで再送」、移行側でBackfill件数一致を「正本切替済み」、Plugin側でroot go test PASSを「選択Studioの実Binaryも適合」、AI側で提案が妥当を「実行許可」と扱う構成は、より簡単でもB1の合格にはしない。

**過剰拡張の反証**：一件のread-only調査に全DB Migration、全GUI、self-build G4、複数Harness、複数Provider、全Plugin方式選定を必須にする構成は、同じJobで必要性・増分価値を示さない限りB2の条件付き候補に置く。

### 16.3 既存Issueと証拠の更新・停止線

- [VA-00 #424](https://github.com/hat47x/tai-pleroma/issues/424)は2026-11-05時点で**Closed**。9 LaneのSource-static整合性監査と機械的修正は成果として利用するが、Owner未決のADR・製品分類・実価値の受理までCloseされたとは扱わない。
- [TEI #1180](https://github.com/hat47x/tei-platform/issues/1180)と[#2514](https://github.com/hat47x/tei-platform/issues/2514)のScenario SSOT／独立Oracleを再利用する。各評価票には、必要なSource/Scenario/Contract/Build/Runtime/Grant/Consumerのうち**Required／Observed／Undischarged**を示し、合成試験・実PG局所試験・同一Revision全経路試験のClaim ceilingを別記する。
- [TEI #1163](https://github.com/hat47x/tei-platform/issues/1163)の一改訂証拠票、[#1174](https://github.com/hat47x/tei-platform/issues/1174)のEffect Fence、[#2555](https://github.com/hat47x/tei-platform/issues/2555)のMigration正本切替、[#1251](https://github.com/hat47x/tei-platform/issues/1251)のPlugin Buildは**各Ownerが実実装・受入**を担う。横断計画が新しいDB移行器・Tx Coordinator・Plugin Host・AI実行権限を所有しない。
- 既存GitHubの局所PASSは正しく対象範囲に帰属させる。2026-11-06時点、TAIのこの比較（VA-T2-R/W、実GUI UX、異モデルVA-X、横断同一改訂E2E、Owner正式受理）は**NOT RUN**。mainとDraft PR #423の乖離は、別の統合時差分レビュー対象とし、この追補をmainの機能完了宣言に使わない。

## 17. 11月5日夜の横断反証：候補・実選択・実消費・現在資格を分ける

**統合する成熟成果**：Plugin、DB移行、SHO Parser、TEI Effect Recovery、TAI Skillに共通するのは「候補がある」「実際に選ばれた」「その版で消費された」「今もこの用途に使える」が異なること。標準化するのは**評価時に確認すべき問い**であり、製品を横断するSelector／Registry／Operation Ledgerを実装することではない。[TEI #1251](https://github.com/hat47x/tei-platform/issues/1251)、[#2555](https://github.com/hat47x/tei-platform/issues/2555)、[SHO #7](https://github.com/hat47x/sho-composer/issues/7)、[TEI #2870](https://github.com/hat47x/tei-platform/pull/2870)、[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の各Ownerの既存受入票を再利用する。

| 何を選ぶか | B1の最小経路と、変化したときの資格 | 複雑さを減らすが、絶対に削れない反例 |
| --- | --- | --- |
| **業務Command／実Provider** | まず一つのFunction/OperationIDと実PG CAS/Receipt/独立Readを固定。[#2853](https://github.com/hat47x/tei-platform/pull/2853)の局所実PG成功、[#2870](https://github.com/hat47x/tei-platform/pull/2870)の再起動でin-memory unknownが失われる観測、[#2854](https://github.com/hat47x/tei-platform/pull/2854)の別Key/ABA再適用を分ける | **同じKey**なら実PG側の冪等記録が再適用を止め得るが、再起動後のLifecycle自体が永続安全という意味ではない。新Keyでの自動Retry、ACK消失＝無作用、外側Rollback＝内側Commit取消はいずれも拒否/unknownとして扱う |
| **旧新DBの読取・書込正本** | [#2555](https://github.com/hat47x/tei-platform/issues/2555)のMIG-H01〜07。Expand/Backfill/Validate/Cutover/Contractのうち、実User Jobに必要な段階だけ旧新Client/Authority/Read Cohort/履歴を照合。TAI [#271](https://github.com/hat47x/tai-pleroma/issues/271) SC-13へHandoffを委譲 | Backfill件数・Rollback後差分0・同じ値/Schema名でも、**現在のread/write owner・CDC水位・参照時点・権限**は証明できない。Cutoverを越えてUnknown Commitを新Providerへ別Keyで盲再送しない |
| **Plugin／Target Builder** | 最初はGo単一Binaryと凝集Bundleの選択的Build。[#1251](https://github.com/hat47x/tei-platform/issues/1251) PB-01/02/07（未選択の非干渉）とPB-10（選択したnested moduleの依存閉包）を**別のA/B**で実測 | 未使用PluginがCatalogにあるだけで実Binaryに混入する問題と、root Go Test成功なのにStudioの依存sum不足でBuild不能な問題は異なる。後者はmainで修正PR統合済みだが検出条件は維持。Pluginの小分割や動的Hostは未採用 |
| **SHO Research Index Parser** | [SHO #7](https://github.com/hat47x/sho-composer/issues/7) G1bは明示固定Parser/Grammar/option/Source byteで最初のMarkdown L0索引を試す。Parser候補追加と実選択変更、実入力とIndex再利用を区別 | 選択Parserの欠落を無音で別Parserへ切替えない。古い索引や同じURLを、同一Occurrence/引用原文/Reader現在資格と扱わない。全文再解析をBaseline、Cacheは後測定。L0単独編集に外部論文取得や全Plugin探索を義務化しない |
| **TAI外部HarnessとProduct Skill** | [#168](https://github.com/hat47x/tai-pleroma/issues/168)の実TEI CLI S1とSK-02 H2/H3四独立Sessionの対照を再利用。実Loaded Subject・Source span/byteと警告を同じScopeで観測 | Skillの存在、静的CI、Tool広告、人工60/60は、H3での実Skill load/Tool呼出し/独立Expected達成ではない。Skill不要という結論も認める。二Harness/実PG/SHO/EKIは最初のread-only対照の先行条件にしない |

### 最小の変更注入と採点（新しい実行Engineではない）

選択対象について、**N0＝対象外候補だけ変更**、**N1＝選択した実装／実消費byte変更**、**N2＝現在のGrant/Authority/Reader/受理版変更**、**N3＝途中停止・再起動／別Attempt／移行境界**の4種類を既存Fixtureへ適用する。N0が非干渉なら必要な局所Evidenceだけ再利用可能。N1では該当Artifact/結果、N2では現在資格、N3では同一OperationID/Receipt/実Readを別々に照合する。依存閉包・観測権限・必要な正本が不明ならunknownに留め、古いPASSの消去・無条件全面再実行・無検証再利用の三択に閉じない。

**一行Claim**：User Job／Sourceと実消費版／選択根拠／実行Target・Attempt／独立Expected／Observed／未充足Required／失効要因／現在Authority／必要な再試験／追加費用。元のTAI #422・TEI #2514/#2600・各ProductのIssueコメントへの参照列とし、第二のClaim DB・新共通Schemaを定義しない。

**記録上の訂正**：[TAI #424](https://github.com/hat47x/tai-pleroma/issues/424)のS7〜S11で機械的/推奨一意な文書修正Draftの一部は11月5日にmain統合され、台帳はClosed。59件すべてがOwner受理された意味ではなく、残るADR/分類/ライセンス等は各OwnerのS9最終状態を正とする。[SHO #7の三系列対応表](https://github.com/hat47x/sho-composer/issues/7#issuecomment-6652422013)はOwner受理済みであり、以前の「提案のみ」という説明を現在の状態としない。ただし未確認セルは受理によって自動確定しない。

**実施段階**：まずTEI読取／同Harness H2/H3の最小比較、次にWrite RecoveryとPlugin選択の反例、必要時にCutoverやSHO実Reader/別Harnessへ拡張。上記の新たな横断実行・独立Oracle採点・異モデルVA-X・Owner意味受理は**NOT RUN**。既存Productでの限定実Go/実PGやCIの実績は当該Source/Environmentでのみ認める。

## 18. 11月6日：TEI文書形式の方向転換と、実価値Trialの観測分母を再定義する

### 18.1 Authoring形式のOwner方針：`*.tei.md`へ寄せる（実装済みとはしない）

2026-11-06の別議論で、**`*.tei`は原則廃止し、TEI向け文書は`*.tei.md`へ寄せる**方向が利用者から明示された。この**Authoring配置の方向**を製品価値比較の前提として扱う。ただし、現行[TEI #2621](https://github.com/hat47x/tei-platform/issues/2621)の末尾にある「`.md`+OKFタグ／別`.tei`の比較、`.tei.md`を標準化しない」は、旧提案としてこの新方針と**未整合**。同Issueおよび[#988](https://github.com/hat47x/tei-platform/issues/988)のGrammar、[#1440](https://github.com/hat47x/tei-platform/issues/1440)の文章→候補、[#2620](https://github.com/hat47x/tei-platform/issues/2620)のRole/Meaning、SHO [#18](https://github.com/hat47x/sho-composer/issues/18)/[#19](https://github.com/hat47x/sho-composer/issues/19)で**移行・互換性・実装範囲**を決める。TAIがTEIのFilename Selector／Language Plugin／Workspaceを無断変更しない。

- **B0**：通常の`.md`をそのまま保存・再開。OKF `type/tags`や任意の`tei`メタデータは意図・候補発見に利用し得るが、**意味受理／Parser適合／実行許可ではない**。
- **B1**：`*.tei.md`という認識可能なMarkdownを、元の文章・表・式・図・コードフェンス・シンタックスシュガーを保ったまま編集する。正式意味が未受理でも保存可。**ファイル名がTEI向けであることと、選択した部分が実Parserで解決されAccepted Meaningに束縛されたことを別資格**にする。
- **B2**：AIが選択箇所をData/Function/Business/Rule・Diagram/Expectedの候補へ展開。原文・曖昧さ・NULL/unknown・業務時点・候補出典を保持して差分Review→既存Acceptanceに接続する。AI自身の生成Expectedを独立Oracleとしない。AI無しでも手動で構造化できることを前提とする。

**互換・拒否条件（TEI Ownerへの照合候補）**：旧`*.tei`参照を含むWorkspaceからの移行は、対象の実Read/Parse/SourceIndex・選択/引用・Build入力・Source Revisionの差を見える化し、RenameだけをMeaning同一や旧Receiptの現在適格にしない。未移行Sourceが黙って飛ばされたら局所`validate ok`でも「移行済み」としない。`*.tei.md`の未受理表・普通の引用・コード例を実行可能定義へ誤昇格しない。No-op Saveで元Markdown byteを維持し、Role付き編集は明示対象への局所Patch→再Read/Parse→Diffで確認。**旧`*.tei`の読取互換・書込可否・自動変換、`*.tei.md`の厳密Grammar／OKF併用規則は未決**であり、この節で実装完了も既存Sourceの一括変換も主張しない。

### 18.2 最初のSkill価値試験は「割付」と「実提供」を分ける

[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の2026-11-06版では、公開TEI利用者定義Subject `sales.order`について[実S1 CLI CI](https://github.com/hat47x/tai-pleroma/actions/runs/42101157330)が限定成功。さらに[no-Go PATHでのPrebuilt Binary CI](https://github.com/hat47x/tai-pleroma/actions/runs/42182253212)が固定実行ファイルの直接起動を検証した。**前者はSource/CLIのread-only基線、後者は配布実行経路の肯定対照**であり、外部HarnessのTool request、H3 Skill loader、Skillによる改善は未観測。実Goビルド資格と配布済みBinaryの起動資格も別。

既存SK-02の**一つのParticipant Task原byte**と固定Source/CLI/Model/Tool/Grantを使い、H2 Tool-only→H3 Skillあり→H3→H2の4独立Sessionを比較する。試行時は **R＝事前割付**、**D＝実Loader＋実Tool/CLIの提供が実ログで成立**を分離。割付H3でLoaderに失敗してもH2へ再分類せず、失敗を含めたITT型の割付ベース結果と、実提供できた試行だけのPP型適格結果を別表示。Sample `n=4`を一般的な因果効果やp95へ外挿しない。T0/Product単独で目的が達成でき、TAI Skillで上積みが無ければ**TAIを常時介在させない**ことも正当な価値結論。Skill/TEI Plugin/Harness Plugin/Host Grantの責務を混合しない。[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488)と[Draft #489](https://github.com/hat47x/tai-pleroma/pull/489)が比較契約を既に所有し、本PRは第二Checker／Runnerを追加しない。

### 18.3 SHO Readerの到達点：候補コードの成功とGrammar完全性を分ける

[SHO Draft #17](https://github.com/hat47x/sho-composer/pull/17)の後続HEAD `113040fb66b72f62f5baaeaf88aedd961b4b6bc`について、[CI #42111682280](https://github.com/hat47x/sho-composer/actions/runs/42111682280)／[CI #42111693753](https://github.com/hat47x/sho-composer/actions/runs/42111693753)でUbuntu/Windowsの**16/16限定試験成功**がIssue #16に報告されている。実ReaderはBOM/UTF-8の明示と最大2MiB+1byte読取でのサイズ拒否を追加。ただし`coverage.unresolvedReferenceCandidatesEvaluated=false`で、未定義参照を実検出できたとはしない。Parserの正式版決定、資源隔離、全OS Egress、独立Reader/Writer保存・UI、Owner受理とmain統合は別。古い14/14は過去HEADの実績として保持する。

**VA-H1の次の判断**はSHO Product L0の独立価値（保存・再開・引用Scope／未知保持）と、このG1b実Reader候補のGrammar被覆・実Consumer資格を分けること。TAIのSkillやTEI Host統合をSHO単独の最初の価値試験の先行条件にしない。[SHO #16](https://github.com/hat47x/sho-composer/issues/16)の既存負例・Owner判断を採用し、横断の別Parser/Indexerは作らない。

**現在の証拠上限**：TEI S1/no-Go BinaryとSHO #17は各固定HEADの製品/限定CI証拠。新`*.tei.md`規約に基づく実Parser/Writer/全Repository移行、外部AI Harness H2/H3、ITT/PP価値採点、SHO正式G1b、Owner横断採否は**NOT RUN／NOT ACCEPTED**。本節は既存Ownerの実装を置換しない計画への接続である。

## 19. 11月6日後半の深化：移行の実読込と、利用者Activityの価値

- **TEI Authoringの実装上の段差**：[Draft #3030](https://github.com/hat47x/tei-platform/pull/3030)にM0〜M6/TM-01〜14が設計され、現Loaderの`*.tei`固定名・検索規則、`filepath.Ext`の`.md`判定、DSL Parserの非Markdown対応を既存の制約として特定した。新`*.tei.md`標準はOwner方針だが、Reader/Parser/Workspaceにおける実移行の資格ではない。[#988](https://github.com/hat47x/tei-platform/issues/988)は、初期SeedとLanguage選択が新Source自身に依存する循環を別に検討。まず実Source一覧と現Parserの受入集合を確定し、旧形式の除去・固定Gateの変更は独立検証とOwner判断の後とする。
- **TAIが本当に増やす価値**：[TAI #271 SC-14/15](https://github.com/hat47x/tai-pleroma/issues/271)のSCN-001では、O-01〜05の矛盾・未決・DraftをO-06で再開する。B0（手動/通常Harness）、B1（必要な単独Product）、B2（TAIの条件付き選択・根拠引渡し）で再開の正しさ・保存後読取・再確認負担と費用を比較する。これはH2/H3 Tool/Skillの**呼出し能力**とは別。J0全面/J1限定/J2未確認再利用も別の比較軸。[VA-01 §6](../../evaluations/VA-01-product-value-necessity.md)で独立Expected・非開示反証・誤資格化を具体化した。
- **隠れた反証は「存在しない」とも「外部にある」とも断言しない**：[Draft #490](https://github.com/hat47x/tai-pleroma/pull/490)のSUI Context合成stubは、選択された候補と参考のみのEvidence/Relationを分ける局所確認。実User Context全件や外部許可を保証しない。Audienceによっては未選択反証の存在・件数さえ開示できない。[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)のHost/Policy条件を保持する。
- **SHO Readerの安全性はGrammar被覆と別のClaim**：[Draft #17](https://github.com/hat47x/sho-composer/pull/17)には固定HEADの両OS16件の成功証拠がある一方、[SHO #16](https://github.com/hat47x/sho-composer/issues/16)には特殊ファイルの読取処理で停止し得る未修正の懸念が追加された。通常ファイルの入力サイズ制限が成立しても、あらゆる入力・OSで非停止を保証しない。実Readerの拒否・隔離・ファイル種類の方針はSHO Ownerが保持し、TAIは新Reader/Sandboxを作らない。

**優先順位**：最初の実験は引き続き[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の外部Harness H2実Tool呼出し1 Session。以降H3の実Load、同一Task四Session、別にSCN-001の活動成果B0/B1/B2を検証する。`*.tei.md`移行やSHO実Readerの追加安全性試験は各Productの並行Owner課題であり、初回TEI S1/H2を一律に停止しない。

**状態**：本節はProduct Issue/PRの静的確認とVA-01評価票への計画反映。新`*.tei.md` Loader・Parser実装、外部Harness H2/H3、SHO特殊ファイル拒否の製品実証、SUIの実非公開Data引渡し、SCN-001利用者試行、異モデルVA-X/VA-E、Owner正式受理は**NOT RUN**。

### 19.1 実装進展に合わせて移行試験の合格範囲を更新

旧`*.tei`を`*.tei.md`へ単純改名すると、従来Loaderが対象Semantic Sourceを読まず、`validate.ok=true`のままSubjectが消え得るという反例に対し、[TEI Draft #3031](https://github.com/hat47x/tei-platform/pull/3031)は`TEI_MD_PARSER_UNBOUND`の明示診断を追加。固定HEAD `63953ccb`の[限定CI #42217379093](https://github.com/hat47x/tei-platform/actions/runs/42217379093)は成功。これは**黙って成功する不具合を防ぐ局所進展**であり、`*.tei.md`を解析・生成できるようになったことでも、mainへ統合済みであることでもない。[VA-04 §7](../../evaluations/VA-04-evidence-readiness-preflight.md)では、旧形式の正常読取・改名後の未読込・明示診断・将来の新形式正常読取を四つの状態として区別する。

**移行Ownerの2026-11-07訂正**：[TEI Draft #3030](https://github.com/hat47x/tei-platform/pull/3030)の最新追補により、旧新形式の移行仕様・検収M0〜M6/TM-01〜14の**主担当は#3030**。[Draft #2667](https://github.com/hat47x/tei-platform/pull/2667)のTMDケースは歴史的な横断経緯・引渡しであり、競合する第二Gateではない。専門家向けのMarkdown表層/原文保持AU-01〜08も#3030内の別の評価目的とする。[#3031](https://github.com/hat47x/tei-platform/pull/3031)の管理Root内の新形式を明示拒否するCI成功は、旧Source＋通常Markdown/非管理Raw Draftの継続、選択した必須Sourceの正常Parse、Writer/Meaning受理まで証明しない。正負対照を既存#3030で比較し、全自動Renameや新Parserを前提にしたB1/B2は保留。旧固定公開TEI基線のH2は継続できる。

### 19.2 活動再開の証拠：正常HTTP応答だけでは再開点・本文・利用資格を証明しない

[TAI #271 SC-17](https://github.com/hat47x/tai-pleroma/issues/271)の根拠には、[TAI merged #491](https://github.com/hat47x/tai-pleroma/pull/491)でSUI管理監査APIが不正CursorへHTTP 200で先頭ページを返した限定観測、[merged #492](https://github.com/hat47x/tai-pleroma/pull/492)でETagは連続Readに安定・保存後に変化する一方、If-None-Matchを与えても**304ではなく本文付き200**が返る限定観測がある。これは仕様の全体受入ではなく、再開するConsumerにとっての負例である。

SCN-001のB0/B1/B2比較でそのSource経路が必要な時だけ、**継続Cursor/観測したページ範囲、実BodyとVariant、ETag/現在のGrant・Audience、必要なConsumer受領**を分離する。不正Cursorの先頭回帰を「新イベント0件」や「監査完了」と解釈せず、ETag一致を「HTTP 304」「ネットワーク費用削減」「現在公開してよい」と推定しない。選択外反証と非公開情報の扱いはSC-15、Readerの形式はSC-16、利用者目的の変更は[VA-01 §6.3](../../evaluations/VA-01-product-value-necessity.md)へ責務を返す。

**投資判断**：これらは用途依存の有効な負例であり、初回H2 Tool-onlyには管理監査API・ETag・全てのCloud Syncを要求しない。後続のActivity再開試行でのみ、誤完了・再取得量・Token/Review/時間・正しく保留した件数を比較する。新共有Cache/Result Storeは作らない。SC-17とSC-18の**実利用者試行・外部Harness・Owner価値採用はNOT RUN**。

## 20. 11月7日朝：外部Tool実観測を価値試験の資格へ接続し直す

### 20.1 先行していた「初回H2 Tool未実施」は歴史状態

[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)と[TEI Evidence Draft #3113](https://github.com/hat47x/tei-platform/pull/3113)が報告するDSH `0.2.2-rc.1`→固定公開TEI実Binaryの実呼出しは、Tool Request/CLI Exit/Reply、SourceIndex Fingerprintを含む技術的縦切りの**限定実測**。9探索試行のうち完了3（Participant Taskは1件）、エラー6（MALFORMED_RESPONSE 5、INVALID_CONFIG 1）、完了Session内のTool call 56／TEI起動32。以前の本計画§18/§19やVA票の「外部Harness H2 Tool呼出しはNOT RUN」「次は最初のH2実Call」は**記載時点の歴史**であり、現状の実施状況を示さない。

**新たな停止線**：DSH read-only Profileから想定するParticipant作業場所外のWorktree Readが実際に可能だった。旧Session・Skill本文・Reviewer Expected・関連Sourceを物理的に隔離した証拠がなく、元DSH JSONLの全byte、独立Answer採点、OS/Network Egress、費用も不十分。従って正式H2/H3比較に必要な**参加者条件の非露出**は未達。探索9件を事後に四Session試験へ流用せず、失敗6件も探索歴として残す。[VA-02 §13](../../evaluations/VA-02-cross-product-first-run-protocol.md)／[VA-04 §8](../../evaluations/VA-04-evidence-readiness-preflight.md)を実験資格の詳細とする。

**最小の次の出口**：既存Harness上で実OS/HostによるSkill/Expected/旧Logの到達拒否を試し、固定Participant Task・Source/CLI binary・Tool schema・Model/Profile・採点基準・費用観測を先にPin。その後に**比較適格なH2の1Session**をTool実呼出し→回答受信→独立採点まで確認し、H3実Loaderと残りのH2/H3試行を同じ事前割付へ接続する。Model/Adapterが不正なTool JSONを生成する現象は実Failureとし、Trial中にModel切替で修復しない。固定Task/Skill本文を事後改変しない。

### 20.2 OKFのAttested Computationは「計算の裏付け」の条件付き拡張

[TAI #514](https://github.com/hat47x/tai-pleroma/issues/514)と[TEI #2605](https://github.com/hat47x/tei-platform/issues/2605)へ、OKF v0.2の`type: Attested Computation`を、Product Skillが計算定義を発見・型付きParameterをBindし、実Executor/Receipt・独立Attester・再読取を分ける契約候補として引き渡した。**OKF v0.2は共通Attester ABI、実Sandbox、正本/実業務認可を規定しない**。SEIは[SEI #820](https://github.com/hat47x/sei-cognition/issues/820)でSource/verified/stale_after等の交換・鮮度の候補として検討するが、SEIのKnowledge/Accepted DecisionをOKF文字列へ置換しない。

**導入の必要性は用途相対**：最初の公開TEI read-only CLI調査/H2/H3比較をOKF Reader/Attesterで止めない。比較後に、既存TEI/OKF機構を使って*実計算1件*の定義・Result・Receiptと独立Attesterを正負試験し、通常のSource→CLI/Resultへの増分価値を評価する。独立ReadやOwner Accepted Meaning、Host Grantが無い場合はUnsupported/Unknownを保持。OKFを全Product必須Runtime、第二知識正本、全更新Actionの実行資格にしない。提案段階でありOKF Attesterの**実施はNOT RUN**。

### 20.3 Product価値として昇格したもの・していないもの

| Claim | 現時点 | 次に必要な証拠 |
| --- | --- | --- |
| TEI公開1 SubjectのCLI読取 | 固定Source／Product S1／DSH外部Tool実呼出しまで限定Observed | 新たな比較Trialの隔離、実Participant Answer／Reviewer独立Expected |
| Product Skillの追加価値 | **NOT RUN** | H3実root/refs LoadedとH2非露出、事前割付4 Session、正答・Warning/Unknown・費用比較 |
| TAIのActivity価値 | **NOT RUN** | SCN-001の同一User JobでB0手動/B1必要Product/B2条件付きTAI、正確さと誤停止/費用を測る |
| OKF計算検証の付加価値 | **NOT RUN** | 既存Ownerによる1件の実Executor/Attester/Result独立再読取 |
| TEI `*.tei.md`通常解析／実Provider Write・SHO正式Reader | **未成立／用途別並行課題** | 各Product Ownerの別Scope/Artifact・実Effect・独立Consumer |

**投資判断**：DSHの実接続という一段階は確認できた。次は新Kernel/新Harness Bridge/第二Plugin Registryではなく、**実隔離と比較可能な少数試行**へ資源を集中する。実H3、正式4Session、外部送出ゼロ、Owner価値受理は未確認。

### 20.4 初回Harness実証から追加された価値判断：Toolの到達と結果の完全性を分ける

[TEI #3113のEvidenceはmainへ収録](https://github.com/hat47x/tei-platform/tree/main/plan/evidence/DSH_H2_TOOL_ONLY_READ_ONLY_2026-11-07)。[TAI #270 Runbook §24.3](https://github.com/hat47x/tai-pleroma/blob/docs/yi-harness-skills-20261102/docs/yi-constellation/first-real-skill-qualification-runbook-2026-11-02.md)はその保存Byteを再読し、外部Toolの呼出し成功と受領の不完全性を別に確認した。Catalog Resultの2ファイルが各8,192 bytesで切れてJSON全体を解析できない一方、inspectやvalidateはstdout先頭JSONとShell stderrを分ければ実値を照合できる。56 Tool Callと55 Resultの差は残り、Session completedは全Result受領を意味しない。

**利用者価値の限定**：初回User Jobは明示済みsales.orderの属性・Source・Warningを調べることである。全Catalog・全Indexを完備する新Toolや全Product共通Adapterより、**必要な対象Subjectの限定inspect/validate stdoutが欠落なくModelへ届いたか**を先に判定する。全Catalogが不完全なら全Source確認済みとは言わない。必要な対象の実情報が不十分なら許可された追加ReadまたはUnknownで停止する。

**増やさない要求**：DSH専用の新TEI Tool Proxy、共通Result Store、第二JSON Parser、MCP全面移行、新Harness/中央Validatorを初期価値試験の先行条件にしない。既存のTool request→実CLI stdout/stderr→Tool reply→Harness/Model受信→Participant回答を固定Task/Source/Permissionに束縛すればよい。出力断絶は[TEI #2509](https://github.com/hat47x/tei-platform/issues/2509)、実隔離は[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)、H2/H3比較資格は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)へ戻す。

**独立Expected**：[VA-02 §13.1](../../evaluations/VA-02-cross-product-first-run-protocol.md)のDSH-C01〜05に、Catalog一部受領を全件確認と誤認する、stdout/stderr混在の返信を単一JSONとして扱う、Result欠落でも完了扱い、探索時だけのsource-indexを正式Whitelistへ事後追加、指定Model Aliasを実Weights同一と断言する負例を集約する。

**優先順**：①許可外Source/Skill/Reviewer資料の実到達拒否、②開始前Profile/Tool whitelist/Task/Model/Expected固定、③必要なSubject限定Resultの完全受領、④比較適格H2の1 Session、⑤H3実Loaderと固定4 Sessionの独立採点。OKF Attester・新TEI Markdown Parserなどを最初のHard dependencyへ加えない。受領不足原因・外部Egress・Cost・正式比較・Owner価値受理はNOT RUN。

### 20.5 H3実Skill受信とDSH副次送出の反証に基づく投資順位

前節の「H3実ロードは未実施」は[TEI mainに収録された4実Session](https://github.com/hat47x/tei-platform/blob/main/plan/evidence/DSH_H2_H3_FOUR_SESSION_2026-11-07/README.md)以後、**当時の歴史記録**となった。H3-A/H3-Bは固定Product Skill root 5,482 bytes／同digestと参照文書1件を実受信。H2-A/H2-BにSkill Toolの実呼出しは無い。技術的な「実Loader・実Tool起動」を永久に未達と記載しない。ただしH2-Aの探索Session再利用、参加者TaskのWorkspace pathと実Rootの不一致、Skill/Reviewer資料の物理的非露出未証明、Tool whitelist逸脱、独立Expected/費用評価未実施のため、**有効なH2/H3比較＝0/4**。4 completedを4合格と読み替えない。

さらに[TEI mainのH6-E1合成Read](https://github.com/hat47x/tei-platform/tree/main/plan/evidence/DSH_H6E1_READ_BOUNDARY_2026-11-07)では、DSH read-onlyで許可Projection・合成Raw・合成.env・cwd外Peerの4件がすべてRead成功し、OS拒否0。この合成ファイル本文はモデル入力だけでなくSession Logにも載った。[H6-E2 Local Mock](https://github.com/hat47x/tei-platform/tree/main/plan/evidence/DSH_SESSION_LOG_RETRY_AND_DEFAULT_2026-11-07)では`dsh_session_log`が既定で約45.5KB付随し、503・空streamでは受理水位が進まず同一範囲が再送される。**実Providerへの秘密漏えい・全Networkの不在は未測定**だが、`read-only`表示／Session Log offという説明だけで機密境界を認定できないことは実測に基づく。実Egressに加え、監査Evidence自体を公開Issue等へ出す際のSinkも[TEI #2515](https://github.com/hat47x/tei-platform/issues/2515)／[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)の開示Scopeで確認する。

**G0/G1/G2の最小投資順**：G0＝許可済みRead成功＋許可外Skill/Reviewer/親Sourceの同一実Profileでの強制拒否。G1＝Model MessagesとSession Log等の送出先・再開後の再送を区別し、Scope外送出をOS/Hostで止める。G2＝許可Toolのcommand/flag・実Workspace identity・完全Tool reply/Consumer受領。次に**新規4 Sessionを開始前割付**し、H3の実Loadと回答品質/費用を独立Expectedで比較する。前回探索9件と技術Witness4件は比較分母に遡及編入しない。[VA-02 §13.2](../../evaluations/VA-02-cross-product-first-run-protocol.md)・[VA-04 §8.2](../../evaluations/VA-04-evidence-readiness-preflight.md)が受入票。

**隣接する新しいProduct局所発見**：[TEI #3181](https://github.com/hat47x/tei-platform/issues/3181)でCLI WorldFPはWorkspace manifest identityの完全な代用ではない。[TEI #3182](https://github.com/hat47x/tei-platform/issues/3182)では`view`のread-only広告にもかかわらず指定flagでFSファイル出力が発生した。これらをG2の引数・実効果束縛へ吸収し、新CLI Toolや一律の隠れたWrite許可にしない。許可済み`inspect`のread-only調査は継続する。

**本当に必要な製品価値**：Skill Packageが読めること、Tool Callが成功すること、正確な判断・適切な保留、独立Consumerへの到達、実業務Outcomeの順に別Claimで評価する。[TAI #531](https://github.com/hat47x/tai-pleroma/issues/531)／[Draft #532](https://github.com/hat47x/tai-pleroma/pull/532)のOutcome/Skill/Authority分解は[VA-01 §6.6](../../evaluations/VA-01-product-value-necessity.md)へ価値軸だけ取り入れ、Fusion Claw型の統合Runtimeや第二Receipt Storeは導入しない。

**現在の資格**：H3 root+1 referenceの実Load、H6-E1の拒否失敗、H6-E2のLocal Mock送出は局所Observed。隔離済み正式比較0/4、独立採点/費用、実OS/Network強制拒否、本番外部送出範囲、実利用者Outcome・Owner受理は未達。初回固定Skill/Source/Taskを変えず、次の最小出口はG0/G1/G2を満たした新Trial Group。


## 21. 2026-11-07：主要価値に対する「義務化の伝播」を断つ横断照合

> **状態**：2026-11-07に既存の各Product Value/README、代表Issueと本Draftを照合した**Source-staticの判定提案**。全Issue・全ADRの網羅、別モデルのVA-X、実ProductのB0/B1/B2比較、Ownerの正式な要求改定は未実施。IssueがOpenであることは実装必須を意味しない。この節は[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)と[VA-01 §7](../../evaluations/VA-01-product-value-necessity.md)の判断材料であり、Product側の正本を置換しない。

### 21.1 論点は「機能が多いか」でなく「他の利用場面へ義務が伝播するか」

各要件・設計を **価値要件（何が成立すべきか）／安全・意味の不変条件／具体的実現方式／採用する配備・用途条件／試験の証拠資格** に分ける。必要な不変条件が重いことと、どの用途でも特定のRuntime・Schema・GUI・Methodを必須とすることは別である。

過剰化を疑うのは、(a) その機構を使わない小さなUser Jobでも事前の設定・ロード・全件取得・Owner承認を強制する、(b) 本来のOwnerでないProductが同じDecision/Meaning/Authority/Executionを再実装する、(c) 完成を証明するための試験環境が利用者の初回体験より先に必須化される、(d) 候補が実消費・結果・利用者価値と無関係に「全製品必須」へ昇格する場合。逆に、条件付き機能に対応する明確な反例が存在すれば「無駄」と断定しない。

| 対象・既存Owner | 価値が最初に成立する断面 | **初回の必須**に伝播させないもの／用途条件 | 省くと壊れる不変条件・局所判断 |
| --- | --- | --- | --- |
| **TAI** [#168](https://github.com/hat47x/tai-pleroma/issues/168) / [#271](https://github.com/hat47x/tai-pleroma/issues/271) / [#74](https://github.com/hat47x/tai-pleroma/issues/74) | 既存Harnessで必要なProductを選び、正しい対象・未決・次の作業を再開できる。B1単独Productで十分ならTAI不介在も正しい結果 | 常駐TAI Agent、全製品Bundle/サイト公開、全Skillの一括Load、全Handoffの常時再資格化は用途条件付き。配布と利用者のActivityを別成果にする | 誤った権限継承・秘匿データ外送・旧Attempt成果を現在のOutcomeへ転用しない。H2/H3の技術Witness4件は正式比較**適格0/4**、新TrialのG0/G1/G2を優先 |
| **TEI** [#1127](https://github.com/hat47x/tei-platform/issues/1127) / [#1180](https://github.com/hat47x/tei-platform/issues/1180) / [#2619](https://github.com/hat47x/tei-platform/issues/2619) / [#1223](https://github.com/hat47x/tei-platform/issues/1223) | 専門家に読みやすいData/Relation/Function/Ruleから一つの保守・保存・再読取と変更後の検証。CLI/Go単一バイナリが基本形、既存Scenarioを再利用 | 全Domain/数学型/組織履歴、全Target/Studioの**同時完成**、常時Hot Swap、無停止の二世代更新は初期受入の条件にしない。ただしPlugin-firstは正式な製品要求RQ-008であり、無条件の任意機能には格下げしない。D0→D1の単一Inspector縦切りから段階実現し、別Core/Runner/Resolverは追加しない | NULL/欠損、関係の粒度、業務ID、現在Grant、Effect、独立Readbackを保存。 `*.tei.md` は方向性と実Parser/Loader対応を区別し、旧Source一括改名を先行しない |
| **SEI** [#711](https://github.com/hat47x/sei-cognition/issues/711) / [#758](https://github.com/hat47x/sei-cognition/issues/758) / [#660](https://github.com/hat47x/sei-cognition/issues/660) / [#767](https://github.com/hat47x/sei-cognition/issues/767) | 1件のObservation/Decisionと根拠・Unknownを保持し、別回で根拠・Scope・適用性を再構成する | 毎回全Method・全認知Signalを手入力させること、万能なTruth/Method Engine、全領域連携は条件付き。取得不能な根拠をUI都合で補完しない | `verify`が未検証recordを含んでもexit 0になるとの[#758](https://github.com/hat47x/sei-cognition/issues/758)の報告は簡略化対象でなく**最初の真偽判定を壊す製品Gap**。Unknown・ExactBinding・根拠の欠落を隠さない |
| **SUI** [ADR-0089](https://github.com/hat47x/sui-sensemaking/blob/main/01_Plans/adr/ADR-0089-product-value-canon.md) / [#3371](https://github.com/hat47x/sui-sensemaking/issues/3371) | 未整理の観測・異論・保留を、レビュー前後の由来を失わず編集・再開・共有できる | 最速自動要約、全文化Method、TEI/TAI向け全Projection経路の常時有効化を初回成立条件にしない。DocumentV1変換が未使用・未接続なら利用範囲を限定してよい | 非レビュー構造の非開示と、Island/Relation等の意味損失を隠さない。Projection一致を原文同一・復元可能・全件確認へ昇格しない。認知増分は実務T2で判定 |
| **SHO** [#4](https://github.com/hat47x/sho-composer/issues/4) / [#7](https://github.com/hat47x/sho-composer/issues/7) / [#8](https://github.com/hat47x/sho-composer/issues/8) / [#9](https://github.com/hat47x/sho-composer/issues/9) | TEI・論文本文・DOIを取得せずとも一文書とMarkdownリンク階層を編集・保存・再開する。必要時に出典の現在資格を確認 | L1〜L4学術メタ情報、PDF組版、多Target、論文→コード自動化、独立Document Graph DBは初回不要。MMI C-01/T2が未成立でもSHO単独L0を止めない | 著者本文、意図したSource、実読取bytes、表示、Review、固定納品を分ける。同名異内容/未取得/未定義参照/非可逆変換を「引用確認済み」としない |
| **EKI** [#58](https://github.com/hat47x/eki-fabric/issues/58) / [#19](https://github.com/hat47x/eki-fabric/issues/19) / [#155](https://github.com/hat47x/eki-fabric/issues/155) / [#67](https://github.com/hat47x/eki-fabric/issues/67) | 分散が適するTaskだけを受理し、許されたWorkerへ委任、同一Task/Attemptの実結果・故障回復を確認する。分散**しない**のも正しい成果 | 学習型Scheduler、全組織の公平性、2系統クラスタProvider、Federation/多媒体Stream等は実Workloadと失敗条件が出てから | Client/Worker不信、Local Governor停止、Resource予算、AttemptとClaim/AcceptedResult/Artifactの区別を削らない。Suitabilityを省いて高価な分散を強制しない |

**系列外を不当に製品化しない**：[CSW](https://github.com/hat47x/cultural-substrate-weaving/blob/main/README.md)は2026-11-07取得のREADMEで、本文の三つの執筆Skillを独立に利用でき、CI・ビルド・配布の義務を縮小した例。TAIの全体RegistryやSHOの文書保存義務をCSWへ移植する根拠にはしない。SHO/MMI、TEI Studio、CSWのProduct分類は[#73](https://github.com/hat47x/tai-pleroma/issues/73)の未決に従う。

### 21.2 省略可能性を判別する三種類の反証

- **最小価値の反証（V）**：B0＝既存Harness/テキスト/既存ジョブ、B1＝当該Product単独、B2＝高度な関連機構。入力・Audience・目的・Source版・権限・Independent Expectedを揃え、正答・未決保持・安全性・手戻り・費用を別列で比較。B1が成立しB2の純増価値が無ければ、B2を既定・必須へ昇格しない。
- **削り過ぎの反証（I）**：SEIの未検証recordを検証成功にする、SUIの非公開カードを漏らす、TEIのCommit不明を成功にする、SHOの未取得論文を読了にする、EKIのClaim ACKを成果物到達とする、TAIの古いGrantを現在のAction許可にする、の各負例。安全・意味の不変条件に必要な小さな修正は、巨大な汎用化を待たず優先する。
- **依存伝播の反証（D）**：単独TEI read-only調査にTAI/Handoffの全起動、SHO L0にMMI C-01/PDF、SEI resumeにTEIの現在モデル全件、SUIの保留にTEI DocumentV1逆保存、EKI有限TaskにML/Federationを要求する構成は、いずれも「なぜその依存が今のUser Jobに必要か」を反例で説明できるまで任意のまま。価値比較用に新しい中央GateやDBを作らない。

### 21.3 実施順と停止線

1. **先行**：現行Product内の、価値を誤表示する局所Gap（SEI #758、SUI #3371、SHOの原文/参照の誤昇格、TEI/外部HarnessのTool Result欠落、EKI同Attemptの結果未達）はそれぞれのOwner Issueへ戻す。研究候補は保留でも危険な偽成功は保留しない。
2. **単独利用から**：TAI #168のH2/H3は既存Task/Source/Skillを変えず、G0の許可外Read実拒否→G1のModel/Session Log送出→G2のWorkspace/Tool Reply完全性を通した新Trial Groupで評価。SUI実務T2、SHO L0、SEI一件resume、TEI単一Function、EKI有限Taskは**他製品の一括完成を待たない独立レーン**で並行に実証できる。
3. **条件付き拡張**：B1の反証が実際に出た用途だけ、TEIの全Capability一括Plugin化・無停止Hot Swap・全Target同時実装、EKI高可用性/高速Data Plane、SEI高度Method、SHO Research Index L1以降、TAI配布/多Product統合を局所導入する。選定理由と撤回条件をOwnerへ返す。全Product共通の採用義務を作らない。
4. **観測**：各段階で `提案→実選択→実読込/実呼出し→Host/Provider実効果→Consumer実受領→利用者のOutcome→Owner受理` の証拠を別資格にする。単なるCI成功・数の多いIssue・モデル間一致は価値の確証ではない。

**この更新で実施したこと**：既存のValue/README、関連IssueをSource-staticで横断照合し、計画上の依存伝播・優先順・反証ケースを具体化した。各製品のRequirement/ADR/コード、既存PRのmerge、実B0/B1/B2、異モデルレビュー、外部Harness隔離の修正と新Group実行、実Provider/実利用者・Owner受理は**NOT RUN**。


## 22. 2026-11-07：実証に応じて義務を縮退する――単独価値の次の最小一歩

本節は[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)の**価値適正化**のみを扱う。すでに実測があるProductの「まだ動いていない」扱いを修正すると同時に、CI成功を本来のUser Job完了へ広げない。各Ownerの実装計画・受理を上書きせず、[VA-01 §8](../../evaluations/VA-01-product-value-necessity.md)を次の反証入力とする。

### 22.1 設計方針の採用と、初回に必要な実装量は別

- **TEIのPlugin-firstは任意ではない。** [TEI RQ-008](https://github.com/hat47x/tei-platform/blob/main/requirements/TEI_PRODUCT_REQUIREMENTS.md)に、Coreを除くCLI/StudioのPlugin化・生成RuntimeとのContract/Resolver/Build/Test共用が明文化され、[PR #3277](https://github.com/hat47x/tei-platform/pull/3277)は**merged**。これは**製品要求と設計文書の採用**であって、実CLI/StudioがPlugin経由で動作した証拠ではない。実装の最小経路は同PRのD0（現在の静的CLI・Studio差分）→D1（read-only Inspector一機能の実Plugin/Consumer）で、全機能の同時移管や別Host/Resolverの新設を初回条件にしない。
- **Verified Composition BOMは、組合せを利用する場合の基本的な適合証拠であって、一律に全組合せを実行する義務ではない。** [TEI Draft #3269](https://github.com/hat47x/tei-platform/pull/3269)のGo Referenceは合成2×2等の限定テストを実行したが、宣言候補12組とLock供給候補9組は一致せず、実Resolver/Target/Host/独立Expectedへの適合は未実証。候補列挙、選択Lock、実Build/Load、独立試験、利用資格を分ける。Pairwise合格を全候補の保証にしない。
- **TEI Design Context Queryは、AIが新たにScenario/Ruleを作るときの必要SourceのScope閉包である。** [#3262](https://github.com/hat47x/tei-platform/issues/3262)のP-1aは現CLIのread-only照合、P-1bは限定Query、MCPは後続Adapter。あらゆるTEI起動・一件の手動CRUDに、全Workspace/全Sourceの完了Queryを強制しない。取得不能・未解析・Reply切詰めを「complete」にはしない。

### 22.2 実測から選ぶ「次の最小実験」

| 対象 | 既存の限定達成（参照証拠） | まだ言えないこと | 次の**1辺**だけを実証する／避ける過剰化 |
| --- | --- | --- | --- |
| TEI test dogfood | [main #3304](https://github.com/hat47x/tei-platform/pull/3304)の専用[CI #42378033965](https://github.com/hat47x/tei-platform/actions/runs/42378033965)は、既知Ruleの行番号0をPinned実CLIで検出し、偽Expected・偽Fixture・旧Pinを限定判別（**T1-A**）。従来の局所C0相当10.1%、C1未計測は別資格 | **AIが未知の未カバーRuleを盲検発見するT1-B**、全設計Closure/実Provider/Target E2Eではない。TT-56は正常JSONでもRequired Rule/Relation欠落を検出する必要がある | [#3262](https://github.com/hat47x/tei-platform/issues/3262)の既存Context GateのRequired照合を一本化し、固定HoldoutのT1-Bへ進む。新Runner/第二Scenario SSOTを建てない |
| SUI→SHO | [SUI #3397](https://github.com/hat47x/sui-sensemaking/pull/3397)の354-byte固定原文と[SHO Draft #21](https://github.com/hat47x/sho-composer/pull/21)の別Repo限定互換。SHOのCheckout同一性・偽Producer起動前拒否は[CI #42377986797](https://github.com/hat47x/sho-composer/actions/runs/42377986797)でUbuntu/Windows各**20 PASS・1 SKIP** | SKIP一件こそ**実同一File H1**。既存GuardのPASSは実SUI Checkout→SHO CLIの同一Attempt受領・Source真正性・Writerを証明しない | 既存Runnerで真正SUI固定HEADとSHO実CLIの一Attemptを検証。SHA/実Path/Reader Scopeを独立観測。新Handoff Serviceは不要 |
| SHO独立L0 | [#16](https://github.com/hat47x/sho-composer/issues/16)／旧[Draft #17](https://github.com/hat47x/sho-composer/pull/17)はread-only Readerの実ディスク/2 OS CIを限定実証。[Fixture #12](https://github.com/hat47x/sho-composer/pull/12)はmerged、#17は**closed・unmerged** | 正式製品Reader採用、未定義参照完全検出、特殊FileのOpen前拒否、Writer G2/保存再開 | Readerの未解決候補を正確に「未評価」と表示しつつ、[#4](https://github.com/hat47x/sho-composer/issues/4)の一文書保存→再開へ繋ぐ。PDF/DOI/MMI完成は待たない |
| TEI Plugin/BOM横断 | [RQ-008 #3277](https://github.com/hat47x/tei-platform/pull/3277)はmerged。[main #3337](https://github.com/hat47x/tei-platform/pull/3337)は2環境・宣言12能力のうち未選択6を列挙（うちdatabase-provider 2はBinding型の照合限界）。[main #3336](https://github.com/hat47x/tei-platform/pull/3336)はBuildの起動主体と子Process・実Disk Artifact digestを別観測 | **未選択は故障とは限らず、選択≠実利用**。Stage Driverはself-build L3や実Runtime資格を証明しない。Studio実Plugin/Verified BOM未達 | Inspector一能力のKind+ID→Environment選択→実Link→実Consumer→必要Grantを別検査。未選択の全能力やself-buildを通常inspect/Buildの先行Gateにしない |

**順序の判断**：局所的に既存CIが通っている経路は、同じ試験の再包装よりも「欠けている一辺」（TEI T1、SUI→SHO同一File、SHO Writer、Plugin実Consumer）を優先する。安全・出典・Scope・現行Grantの不変条件は省略しない。未実施の価値比較を「B2は不要と証明された」と読み替えない。

### 22.3 証拠と要求IDの伝播事故を、既存手順で防ぐ

[TEI #3223](https://github.com/hat47x/tei-platform/issues/3223)に記録された**RQ-035のBranch間意味衝突**（main＝Data Source Workbench、旧BOM Draft＝Verified BOM）は、Issueや設計が増えただけで同一IDの意味が変わりうる具体例。新しい横断Requirement Registryを作るのでなく、**採用前のOwner Issue番号／Source ref＋blob SHA／Requirement ID→Meaning／PR状態**を照合し、不一致なら未受理に止める。閉鎖されたDraftを現行標準の根拠として扱わない。

**今回の資格**：他Productで報告されたCI/実験と現行GitHub Issue・PR・要求本文をSourceとして照合し、**このDraftの要件境界・試験優先順位のみ更新**した。ここでの新CLI/Plugin/SHO writer/同一File転送/新T1/実B0-B2/複数モデル反証/Owner受理は **NOT RUN**。

### 22.4 必須条件を削るべき場所と、削ってはいけない証拠の境界（11月7日夜）

**過剰要件には二種類ある**。①正当なProduct状態を受け付けない、Consumer側で上乗せされた**余計な必須性**。②まだ取得できていないTarget/Source/意味を、見かけのPASSで補完する**必要な証拠の欠落**。前者は最小の契約変更で緩和し、後者は正規のSource/Context/Independent Expectedを確認する。いずれも「常に全機能を実装する」「常に拒否する」の二択にしない。

| 既存Product実観測とOwner | 必要な判断／最小の次試験 | 現時点の上限 |
| --- | --- | --- |
| [TAI #533](https://github.com/hat47x/tai-pleroma/issues/533)→[#535](https://github.com/hat47x/tai-pleroma/issues/535)：SUI Edge `fromKind/toKind`は任意なのに現行投影契約は必須。旧契約では両方ありのみ`present`、項目欠落は`missing`、JSON `null`は`unresolved`、Edgeが失われる。任意契約の試作では欠落/片側nullでもEdgeが`present` | Productで任意な種別は**Edge全体の存在条件にしない**。ただしNode Identity・端点の実在・向き・多重辺・種別未確定は別。SUI→TAI生成器→合成層で「未指定」「明示null」「実種別」を区別して投影Loss・曖昧参照を検査。現行パイロット契約はOwner判断まで勝手に置換しない | #535の報告では試作と全体Suite 88段PASS。ただし合成層の意味・本番Profile・正式契約採用は未実証 |
| [TEI #3284](https://github.com/hat47x/tei-platform/pull/3284)→[main #3299](https://github.com/hat47x/tei-platform/pull/3299)／[main #3304](https://github.com/hat47x/tei-platform/pull/3304)：T0.5/T0.6の実CLI Context/Source/Lock拒否から、**既知Ruleの行番号0を実走するT1-A**まで前進 | 既知Caseの実走と**未知の未カバーRuleをAIが発見するT1-B**は別。正常JSON/同一FPでもRuleが欠けるTT-56は独立Required→Catalog/全件Source Indexの実返却へ照合し、partial/unknownなら不足診断を先行。新しいContext Reader/Runnerを増やさない | [#3304の専用CI #42378033965](https://github.com/hat47x/tei-platform/actions/runs/42378033965)はT1-Aを実CLIで判別。[#3326](https://github.com/hat47x/tei-platform/pull/3326)の初回CIは**subject Indexを全件Indexと誤認して失敗**、既存indexモード追加後の[専用CI #42385726717](https://github.com/hat47x/tei-platform/actions/runs/42385726717)は成功（Context Consumer限定）。別[#3324](https://github.com/hat47x/tei-platform/pull/3324)と同一ファイルの並行DraftなのでOwnerがRequired 3 Rule/1 Rule+Relationを一本化。`qualifiedTestGeneration=false`、C1・盲検T1-B・全Required/Provider E2E未達 |
| [TEI #3267](https://github.com/hat47x/tei-platform/issues/3267)／[Draft #3297](https://github.com/hat47x/tei-platform/pull/3297)：Verified Composition BOM（現行要求番号候補RQ-036）、mainのRQ-035はWorkbench | Matrix選択・`candidate lock`・`observed-pass`・`qualified-in-scope`を分け、**実Source/Artifact/Target/Consumer/独立Expected/Checks/Attemptの同一性が揃った行だけ**推奨。候補からの派生Pairwiseは供給された組合せのCoverageであって、未列挙Universeの完全性ではない | Draftはsynthetic/read-only・`qualified:false`。新PRのCI/Resolver×Consumer×実Target×Host Grantは別。旧[#3269](https://github.com/hat47x/tei-platform/pull/3269)はclosed/unmergedであり採用根拠にしない |

**価値判定の共通規則**：構造同一性や型の欠落を理由に利用者の正しい閲覧/操作を止めるならB1の費用として計測する。一方、Loader未読・Rule未取得・候補Lockだけの行から「全件検証済み」と提示するなら誤完了として失敗。最小修正の後に**本当に利用可能な正例**と、意味・Identity・Scope・現在Grantが不明な負例を同じ必要範囲で確認する。Edge種別の任意化は全Graphの自動合成/書戻し許可と異なり、Context診断は所有者受理なしの業務意味認定ではない。

**優先順位**：初回[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の外部Harness比較G0実拒否→G1送出→G2完全受信→事前割付H2/H3は変更しない。TAI/SUI契約試作、TEI Design Context／T1、BOM Exact Tupleは**それぞれ既存Product Ownerの並行レーン**として進め、全Productへ先行必須化しない。今回本計画が所有するのは価値・過剰必須性の比較であり、**既知T1-Aは局所Observed／盲検T1-BはNOT RUN**。実BOM/Plugin Target・TAI端点種別の正式契約更新・外部Skillの価値比較/Owner受理もNOT RUN。



### 22.5 未選択Capabilityと編集可能性を「全体失格」にしない

[TEI Plugin Capability Coverage #3337](https://github.com/hat47x/tei-platform/pull/3337)は、宣言能力12のうち6がどのEnvironmentからも選ばれない参照Workspaceを実観測した。しかし、別環境向けの未選択候補を含むのは正常であり、database-provider 2件はBinding種別の照合限界もある。**宣言・Plugin選択・Capability Binding・Buildへの採用・実Provider呼出し・現在許可**を分ける。「選ばれない」を全Pluginの修理義務とせず、**要求された操作に必要な能力だけ**を実BindingとConsumerで確認する。最初のInspector一機能は[#1251](https://github.com/hat47x/tei-platform/issues/1251)で証明し、全Provider選択/実利用を強制する別Resolverを建てない。

[TEI Build Stage Driver #3336](https://github.com/hat47x/tei-platform/pull/3336)は子Processの実起動主体・起動先・disk Artifact digestを区別して記録した。ただしStage1自身の生成物による次段Build（L3）ではない。通常のGo buildや単一Inspectorの価値を、self-build L3完了まで停止しない。自称の子Build結果を実Artifact検査なしで信用しない、という不変条件は維持する。

**SHOの独立した文書価値**：[SHO #19](https://github.com/hat47x/sho-composer/issues/19)／[#20](https://github.com/hat47x/sho-composer/issues/20)に従い、普通のMarkdownと管理外の未完成Source Draftを、AI・OKF・TEIの新Parser・Cloud同期なしでRaw編集・no-op保存・再読取できることを第一段に置く。[TEI #3031](https://github.com/hat47x/tei-platform/pull/3031)が示す宣言済Source Root内の新形式未束縛エラーは**TEI意味解釈の拒否**であり、SHOテキスト保存の全面拒否理由ではない。OKFは[SHO #18](https://github.com/hat47x/sho-composer/issues/18)の任意交換契約であり、通常Markdownに出典やAccepted Meaningを自動付与しない。Writer/外部Editor競合/ABA/Byte保持は[SHO #4](https://github.com/hat47x/sho-composer/issues/4)で実証する。

**共通の反証対**：(a) 不要Capabilityは未選択でも指定されたread-only操作は成功、必要Capabilityが未Bindingなら**その操作のみ**不可・理由付き。(b) 未対応TEI Markdownの実Parser処理は拒否するが、SHOで原文をno-op保存・再開できる。(c) 子Process Buildが成功してもself-build資格は主張しないが、通常Buildは止めない。利用可能な部分を不必要に止めた回数と、未資格の結果を誤って成功扱いした回数を別々に測る。統一Status Schemaや中央Gateを増やさない。

**実施状態**：他Productの限定CI/参照実験と現行Issueを確認し、本Draftの優先順位のみ更新。Inspector実Provider呼出し、SHO Writer・通常Editor/TEI Loader E2E、self-build L3、SUI→SHOの実同一File、B0/B1/B2独立比較とOwner受理は**NOT RUN**。


### 22.6 11月8日：統合済みContext Gateから、限定された次の実証へ

[VA-04 §10](../../evaluations/VA-04-evidence-readiness-preflight.md)に、**局所正証人は保持／全件不存在の主張には閉包が必要**という、テスト・Plugin・Handoffで共通するClaim判定を接続した。これは全Productで共有する新しい状態機械ではなく、各Productの証拠から何を主張できるかを照合する読取り規則である。

**Source現在地の重要な訂正**：§22.4にあるTEI #3324/#3326の「二つのDraftを一本化待ち」は当時の状態。現在は[#3354 merged](https://github.com/hat47x/tei-platform/pull/3354)（2026-11-07 16:35Z）に統合され、旧二PRはclosed/unmerged。#3354 exact PR HEADの[専用CI #42391707962](https://github.com/hat47x/tei-platform/actions/runs/42391707962)に11実CLI Reply、3 Required Rule、32合成Consumer判別、既存6 pinned＋既知T1-A第7 Stepの限定成功が記録された。これがProductの全Required Rule、AIが未知Ruleを発見するT1-B、C1、実Provider/Studio/外部Harnessを保証するわけではない。

さらに[Draft #3365](https://github.com/hat47x/tei-platform/pull/3365)では6 Stepの局所検証と不完全目録に起因する全体Coverage unknownを同時保持する検証が進み、[TEI #3223 §29](https://github.com/hat47x/tei-platform/issues/3223)にexact HEAD限定CI記録がある。**部分目録から対象不存在や未テスト確定を推論することも、局所Receiptを消去することも誤り**。[Draft #3370](https://github.com/hat47x/tei-platform/pull/3370)の合法な空result配列とTool失敗の区別も、同じ「誤拒否を避ける」側の課題。これらは未マージの機能をmain実装済みとして採点しない。

**用途別の追加確認先**：
- [Draft #3371](https://github.com/hat47x/tei-platform/pull/3371)：Studio Hostが選んだInspectorと実呼出しProviderを一致させる。Factoryのモック呼出し成功≠CLI/Studio両Consumerの実Plugin資格。
- [Draft #3372](https://github.com/hat47x/tei-platform/pull/3372)：物理FK/UNIQUE/IndexのSource付き観測→構造候補→人が受理したData/Function/Business→図面/CRUD/SHOの**非可逆な境界**を守る。合成Metadata投影成功≠実PG read/DDL/業務Relation受理。
- [TEI #3353 merged](https://github.com/hat47x/tei-platform/pull/3353)：空集合のHandoffでも確認なしのHoldsを許さない。ただしCaller申告を実相手方Receiptへ昇格しない。

**実施順序（既存Ownerの最小一辺ずつ）**：D（#3262の独立Required/Loader/Parser）・T（TAI #168の実Tool受領/実隔離）・G（#3273の独立Blind T1-B）を分けて進める。TEI Inspector実消費、Workbench実Source→Meaning、SHO普通のRaw Writerと同一File H1は並走可。これらの完成をTAIの初回H2/H3に一律先行必須化しない。不要なRequiredによる**誤停止**と、欠けたSource/Effectの**誤成功**を同じUser Job、B0/B1/B2、独立Expectedで計数する。新共通Engine/Registry/Hostなし。

**今回の証拠**：既存ProductのIssue/PR/CI報告の再照合と本計画追補まで。main統合後の別実CI、盲検T1-B、実Provider/Studio/Workbench/SHO Writer、比較適格H2/H3、Ownerの正式意味受理・利用者B0/B1/B2は本更新では**NOT RUN**。


## 23. 2026-11-08：SUIの二つの製品価値を、初回価値と段階拡張として照合する

[現行SUI価値正本 ADR-0089](https://github.com/hat47x/sui-sensemaking/blob/main/01_Plans/adr/ADR-0089-product-value-canon.md)と、新しい[意味形成価値の原点照合 #3400](https://github.com/hat47x/sui-sensemaking/issues/3400)／[異種データ統合Workspace構想 #3401](https://github.com/hat47x/sui-sensemaking/issues/3401)を区別して取り込む。**#3400/#3401は提案であり、ADR改訂・製品価値受理は未実施**。従来の「SUI=カード保存だけ」「統合は常に余計」という二分法は採らない。

### 23.1 主要価値を二軸で検討し、実装入口を二重に必須化しない

| 価値の軸と利用者の仕事 | 最初の独立した仕事／評価 | この軸を正しく守る条件 | 先に製品全体へ強制しないもの |
| --- | --- | --- | --- |
| **SUI-V（意味形成）**：「理由は不明だが気になる」という資料を、元の意味の一体性のまま置き、別の見立て・異論・変化を残して再開する | AI OFF/従来の紙・MarkdownをB0、既存SUIで材料→配置→候補比較→保留→翌日再開をB1として比較。[#3400](https://github.com/hat47x/sui-sensemaking/issues/3400)のSV-01〜05/08から**初回10分と再開**に絞る。T2はSUI開発以外の実務資料で検証 | 任意の理由入力を義務にしない。Cardは文単位の機械分割でなく意味が生きる単位。原資料と新解釈のGain/Loss、理由を後付けした時点、異論・保留・人の判断履歴を別に追跡。AI提示前の自力の気付きを先に記録 | 全資料の自動カード化、標準クラスタリング、AI生成要約/表札、巨大Canvas自動分割、全操作Event Sourcing、全Method常時実行 |
| **SUI-I（異種情報からの状況理解）**：RDB/文書/時系列から対象・関係・時点を仮同定し、別Viewで比較して新しい関係を検討する | [#3401](https://github.com/hat47x/sui-sensemaking/issues/3401)のI1で**少数対象、3系統、必要な2 View以下**のread-only Candidate。既存DB/表計算/文書B0、カード手動取込B1、限定外部参照B2を同一問いで比較。II-01〜08の誤同定・権限・部分取得を先に圧力試験 | Source版/Scope/時点と「同じ対象かもしれない」を区別し、同名/同値を自動Identity受理しない。Graph多重辺・未公開Scope・遅延Index・Partialを可視性と別に扱う。外部更新はAction提案とEffect/Receiptを分ける | 全RDB/Graph/Vector/Media Source、常時全件Cache、万能Join/Query Engine、統一業務Ontology、全Viewの同時実装、Scenarioから自動業務実行 |

**二軸は競争関係ではない**。SUI-Vの正しい「理由のない保留」を、SUI-IのEntity/Relation正式Schema不足として拒否しない。SUI-Iの一つの意味あるSource付き関係発見を、AIクラスタリングの見栄えやカード枚数で代替しない。#3401は戦略的な追加主要価値**候補**として研究を保ち、初回SUI-VやTAI #168の必須依存へ変更しない。人の認知増分と操作・計算費用、誤誘導/誤結合は同じ総合スコアに畳まず別計測する。

### 23.2 Itemの低摩擦収容から外部Actionまで、意味・作用を飛び越えない

- **取込/探索**：未整理Item・長文・異種資料は、最初からTask/Action/Event型や細粒度Cardへの分解を要求せずRaw/Sourceを保つ。Tree/Canvasの配置と関係は別投影であり、同じCardが複数Canvasに現れても同一の位置・所属・解釈とは限らない。[#3400](https://github.com/hat47x/sui-sensemaking/issues/3400)のSV-06/09に既存Ownerを維持。
- **理解/判断**：AIの提案と人が採用した判断、仮説の関係と正式な業務Relation、古い理由と後で説明された理由を分ける。View/Canvasの結線を実ActionやEventに直結しない。統一されたAction/Event型を全Itemの必須属性としない。
- **操作/受領**：外部Actionが必要な場合にのみ型付きIntent→Hostの現Grant/Operation Identity→実Effect/Receipt→新しいObservationへ接続。[#3401](https://github.com/hat47x/sui-sensemaking/issues/3401)はread-only/Proposal-onlyを初期境界とし、Event発生やCommitをCanvasの変更から作らない。
- **共同編集**：[SUI #3399](https://github.com/hat47x/sui-sensemaking/issues/3399)ではローカルUndo、保存Revision/CAS、意味判断履歴を別に扱う。二クライアントの409／dirty buffer保全を先に実証し、全操作永続Event/CRDT/独立共同編集Hostを導入前提にしない。

### 23.3 採用・実装への判定

1. SUI-Vは**実務T2での意味形成の増分**（気付きの変化/元資料へ戻る/異論と保留/再開）を実測する。単一のSUI内部dogfood、T3模擬参加者、AIの整った説明はT2/T1の代替としない。
2. SUI-IはSource付き候補の実Read・二つのViewだけでB1手動取込にない価値を示す。II-01〜08のidentity/開示/partial違反があれば、その用途のB2を不適格に戻す。SUI-Vの正例を取り消さない。
3. 両軸に影響する共同編集は[#3399](https://github.com/hat47x/sui-sensemaking/issues/3399)の二Client保存→409→独立再Readの範囲から。実需が出るまでCRDT等の配備方式を選ばない。
4. 現在のTAI H2/H3 G0/G1/G2と適格試験を変更せず、SUI側のSource/Meaning/Save/外部EffectはそれぞれのProduct Ownerで検証する。新中央Host/DB/Oracle/Action Engineを設けず、AIのTool/Readerや将来のProvider機構は既存境界を再利用する。

**資格と限界**：SUI #3400/#3401/#3399の提案・受入設計、現行ADRと既存実証の区分をSource-static照合したのみ。本更新でSUIの10分実User Job、T2/T1、異種Source実Provider、複数Client E2E、外部Action、別モデル独立評価、OwnerによるADR改訂/受理は**NOT RUN**。
