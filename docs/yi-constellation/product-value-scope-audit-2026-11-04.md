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

[VA-03：用途条件付き能力・Source状態ドリフト](../../evaluations/VA-COND-01-conditional-capabilities-and-source-drift.md)を、VA-01（要件の必要性）・VA-02（実証資格連鎖）に追加する**独立した用途適合性の判定軸**とする。既存の[TAI #424](https://github.com/hat47x/tai-pleroma/issues/424)（9 Lane整合性監査、S4は同一モデルの別Context）と[TAI #425](https://github.com/hat47x/tai-pleroma/issues/425)（TAIのF1/F2/F3所見）を再利用し、第二のIssue/ADR台帳・監査Runtimeは設けない。

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

**後続研究**：EKIの軽量認知・低レイテンシ・マルチモーダル通信では、Workload/データ様式に応じたTransport Profile選択を比較候補とする（[VA-COND-01：用途相対と通信条件](../../evaluations/VA-COND-01-conditional-capabilities-and-source-drift.md) §2/§5）。現行実装・採用プロトコル・低遅延の保証は未確認であり、初期EKI Suitability/結果受理の合格条件へ無条件追加しない。

本追加は計画反映。VA-04の再現試験、AI-EXT/CLI実行、Web/実Provider、独立Oracle受理、Ownerの要求採用は**NOT RUN**。
