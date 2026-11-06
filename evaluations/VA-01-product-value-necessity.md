# VA-01：YI Constellation主要価値レビュー・初回反証パケット

- **状態**：2026-11-04、Source-staticの初回対象選定／試験設計。全Issue監査・実製品比較・2モデル実行・Owner受理は **NOT RUN**。
- **統括**：[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)、[横断計画](../docs/yi-constellation/product-value-scope-audit-2026-11-04.md)。
- **方法**：Product担当（一次案）→ VA-X（別モデル・別コンテキスト優先の反証）→ VA-E（ソース・実測確認）→ VA-I（Ownerへの最小差分）。担当の割当て・実稼働は未実施。
- **Source版**：下記Issueは2026-11-04の個別取得による動的な状態確認であり、単一SHAの固定スナップショットではない。各実作業Laneは自らSource full SHA／Issue URL・更新時点・取得範囲を固定する。検索・転記だけでコード実装の合否としない。

## 1. 価値のための最小構成を判別する第一波

| Case / Lane | 現実のUser Job・初期ベースライン | 高度化案・判別する適用条件 | 省略すると壊れる負例・推奨する当初扱い |
| --- | --- | --- | --- |
| **VA-T1 / TEI** | 小さなData/RelationとRuleから保守・保存・再読込する。[#1127](https://github.com/hat47x/tei-platform/issues/1127)、[#2018](https://github.com/hat47x/tei-platform/issues/2018)。通常コード/既存低コードと同条件比較 | [#2619](https://github.com/hat47x/tei-platform/issues/2619)の万能データ構造／[#1223](https://github.com/hat47x/tei-platform/issues/1223)の汎用Kernel。単一Go binaryで利用可能な小部分と高度Target/Pluginを分ける | **負例**：NULLを未取得と誤認／Auth拒否をUI表示成功で上書き／Scope外行を保存。初期は最小業務縦切りを `core`、全Domain同時実装・無停止差替えは `conditional/research-only`仮説 |
| **VA-T2 / TEI** | 1つの受理済みDriver ScenarioからCLI/Web業務経路を検査。[#1180](https://github.com/hat47x/tei-platform/issues/1180)。AIはScenario/負例を追加し、既存Driverを利用 | 独立したGUIテスト専用DSL、全Target同時E2Eフレームワーク。まず現行Go testから小さな保存Scenarioと両経路生成を比較 | **負例**：CLI PASSなのにWeb認可拒否／未対応Stepの黙示skip／生成AIが自身のExpectedを自己採点。シナリオSSOTを既存Issueで再利用し、新Runner/第二Semantic正本を作らない |
| **VA-T3 / TEI** | Functionと起動・Triggerを分け、単一Go実行バイナリからCLI/Web/cronの必要入口を扱う。[#1130](https://github.com/hat47x/tei-platform/issues/1130) | 別配備・異信頼境界・保守周期・資源条件で複数Buildを必要とする場合だけ選択。[#1097](https://github.com/hat47x/tei-platform/issues/1097)、[#1182](https://github.com/hat47x/tei-platform/issues/1182)、[#2600](https://github.com/hat47x/tei-platform/issues/2600) | **負例**：Function同一性のないJob APIを生成／同一バイナリに同居した別PluginのAuthorityを一括昇格／Toolchain変更を入力Digestだけで再利用。マルチビルド常時必須は `conditional` |
| **VA-A1 / TAI** | 外部Harness単独＋必要なProduct CLI/Skillを1つだけ読み、再開できるか。[#168](https://github.com/hat47x/tai-pleroma/issues/168)、[Draft #270](https://github.com/hat47x/tai-pleroma/pull/270) | 全Product一括Load、TAI独自Agent Runtime、全件Handoff Schema。必要時だけ詳細Skill/資料を読む方法と比較 | **負例**：旧Skillの同名別byteを現在の実行権限とみなす／開示不可Sourceを横断Contextへ送る。最低限は `delegate/core`を分け、全件ロードを標準義務にしない |
| **VA-C1 / SEI** | 根拠と未決を残して1件の判断を中断・再開。[First Slice](https://github.com/hat47x/sei-cognition/blob/main/product/interaction/SEI_FIRST_USABLE_PRODUCT_SLICE.md) | 全Method・全領域のEpistemic Routingを初期入力に要求するか。[#660](https://github.com/hat47x/sei-cognition/issues/660)、[#767](https://github.com/hat47x/sei-cognition/issues/767) | **負例**：同一公開Projectionでも内部対象集合が違う／前回のUnknownを現在の不存在と誤認。正しいresumeは `core`、全入力項目の常時表示・全Method強制は `conditional/research-only` |
| **VA-SUI-01 / SUI** | 意見の違い・保留・未確認のSourceを保持して再検討。[ADR-0089](https://github.com/hat47x/sui-sensemaking/blob/main/01_Plans/adr/ADR-0089-product-value-canon.md) | 文化的Method・学習順位付け・統一評価を最初の意味形成に必須化するか。[Research #3157](https://github.com/hat47x/sui-sensemaking/issues/3157) | **負例**：未受理意見を多数決で消す／非公開の未レビュー構造を投影から推測させる／探索時点で無理に合意確定。任意Methodは `conditional/research-only` |
| **VA-H1 / SHO** | Markdown文書の編集・保存・再開、リンク一覧L0の成立。[#4](https://github.com/hat47x/sho-composer/issues/4)、[#7](https://github.com/hat47x/sho-composer/issues/7) | DOI/書誌・PDF抽出・関係Graph・論文→コードをL0の必須条件にするか。手作業Markdownとの増分を評価。[#9](https://github.com/hat47x/sho-composer/issues/9) | **負例**：字下げから学術的引用関係を推定／同一URLの別Source改版を同一と断定／資料未取得でも「読了」扱い。L0を `core`、L1〜L4を段階要件に |
| **VA-E1 / EKI** | 同じTaskをローカルと既存基盤とEKIで比較。そもそも分散しない選択。[#58](https://github.com/hat47x/eki-fabric/issues/58) | [#19](https://github.com/hat47x/eki-fabric/issues/19)のMLは現行deterministic spikeとのshadow比較、[#155](https://github.com/hat47x/eki-fabric/issues/155)の公平性は条件相対。費用・期限・回復余裕・相関失敗を見て判断 | **負例**：安価なWorkerへ2回割当てたが相関障害で期限超過／ACKだけでBody受領／Commit不明の業務Effectを無条件再実行。Suitability・Result/回復は `core`、MLを常時採用しない |

### 状態に関する注意
- [EKI #381](https://github.com/hat47x/eki-fabric/issues/381)（active→verifying/ready経路）は**2026-11-04取得時点でClosed**。旧資料の未完了表現を転記せず、終了した実装課題と「実TaskのE2E・期限内回復が独立に実証されたか」を分ける。
- [TEI #1180](https://github.com/hat47x/tei-platform/issues/1180)はOpenで、元Issue自体がScenario→CLI/Web再生成を求めている。ここに新しいテストSSOTや生成AI専用の業務DSLを追加するのは重複。
- TAI Draft #270やSHO #7の段階化は**既に主張された設計**。今回の仕事は同じIssueを増やすことではなく、実体験・費用・回帰試験で成否を判断すること。

## 2. 判定のための対照条件（まだ実験結果ではない）

各Caseは、以下を**個別の実験票**として固定する。研究発散を止めるGateではなく、公開・実装・要件昇格時に使う比較である。

| 比較軸 | B0：最小の既存手段 | B1：必要なProduct能力だけ | B2：高度化案 |
| --- | --- | --- | --- |
| 構成 | 外部Harness／通常ファイル／通常コード／ローカル実行等 | 1Product、1Job/Scenario、必要なCLI/Skillだけ | 多Product・多Target・高度Scheduler/Method、全件ロード等 |
| 成果 | 同じUser Job、同じ許可済みSource、同じ版・Scope・権限 | B0と同じゴール、追加価値と費用を測る | B1で不足する用途条件を具体的に固定 |
| 実行費用 | 作業・待ち・CPU/メモリ・転送・Prompt量・人の検証・失敗復旧 | 導入/保守/破棄と再確認を追加 | 設計/統合/移行・常時管理も含む |
| 安全・意味 | 既存Host/Providerが保証する範囲を明示 | Productの付加契約を別観測 | 守る条件を満たせず中止する場合も記録 |

実行回数、独立Expected、fixtureを事前記録する。実利用の配備条件・Worker/Tool可用性が異なる場合、時間・成功率だけを横並び比較しない。

**誤昇格の拒否**：静的Sourceの存在≠現行CLI能力／合成テストPASS≠Product E2E／Task完了≠業務効果／外部HarnessがToolを実行できる≠利用者がその用途で実行資格を持つ／モデル同士の一致≠独立根拠。

## 3. VA-X・VA-Eが先に用意する負例Oracle（提案）

初回は各Caseにつき正例1・削減側が壊れる負例1・高度化が不要な反例1を用意し、**一次評価を生成するAgentとExpected/判定根拠を作る担当を分ける**。

- **EX-1：単純化し過ぎるケース** — 古いGrantで更新処理を再実行してしまうなら、必要な実行直前のHost/Provider再資格化は省略不可。一方、静的なDSL型検査を毎Request全面繰返しすることが同じ保証に必要かは別に調べる。
- **EX-2：高度化し過ぎるケース** — Markdownの3リンクを保存・再開するだけなのに、PDF、DOI、独立Graph DB、全論文の意味抽出を要求する構成は、L0の完成条件と比較する。
- **EX-3：見かけ上の成功** — TEI Driver ScenarioのCLI PASSだけでWeb AuthorizationのPASS、EKIのClaim ACKだけで成果物受領、SUIの候補の多数決だけでOwner意味受理とするならReject。
- **EX-4：最適化の逆効果** — EKIで最安Workerの複数Attemptが同一障害ドメインに集中し、期限内復旧余力を失う。価格/速さだけでなく回復予算・相関失敗・無許可配置の拒否を確認。
- **EX-5：Sourceと現在資格の差** — TEI/SHO/SEIでSource内容がA→B→Aと戻る、同byte別Toolchain、表示名のみ変化、参照位置移動を独立に注入し、何が使い回せて何が再確認必要かを示す。すべてを無差別失効させない。

最初の実比較として**VA-T2（CLI/Web共通Scenario）とVA-E1（Suitability/期限回復）**を優先し、**VA-H1（Markdown L0）とVA-C1（resume-first）**を並行の低依存Caseとする。理由：Sourceとなる既存Issueが具体的で、過剰設計と省略による危険の両方向を一つのFixtureで判別できるため。優先順はOwner変更可能。

## 4. 各Laneの提出物と停止条件

1. **Product analyst**：価値・代替・対象Issue・既存実装確認・暫定分類・要件を外す危険・未確認を短い表へ記入。Sourceへのリンク、exact revision、取得時刻を残す。
2. **VA-X**：Product analystの結論を見ずに最初の反対仮説・負例を作成した上で、原案を読んで争点を記録する。モデル/提供元/Context条件と共有Sourceを明記。同一モデルの場合「別Context」、異モデルを確認できた場合のみ「別モデル」。
3. **VA-E**：既存試験が本当にその対象・版・入口・Host/Provider/権限を確認したか再取得し、`source-static / synthetic-executed / product-integrated / real-world-observed / owner-accepted`を分ける。実行環境がなければNOT RUN。高機密のSource/Oracleは公開Issueへ移さない。
4. **VA-I**：評価が割れた場合は**原案・反対案・反証不能な範囲**を三列で残す。各Product OwnerへIssue/ADRの差分案のみ返し、Draftの統合・閉鎖・合否確定を行わない。

**最初のレビュー終了条件**：6製品の一次判定と未調査母集団、VA-T2/VA-E1の各正負例の独立Expected、少なくとも2件のVA-X反証とVA-E裏付け、Ownerへの差分提案。作業者未配置・実験未実行・ホールドアウト未構成なら、その事実を完了と誤認しない。

**本票は試験定義であり、上表のケースを実行した記録ではない。**


## 5. 2026-11-04 実装状態の更新注記

VA-T2のG0に補足。[TEI mainの6-Step Scenario](https://github.com/hat47x/tei-platform/blob/main/reference/driver-scenarios/order-entry-pattern-smoke.json)、[Scenario parser](https://github.com/hat47x/tei-platform/blob/main/internal/scenariotest/scenario.go)、[CLI verify/generate/run/check](https://github.com/hat47x/tei-platform/blob/main/cmd/tei/scenario.go)の実在を2026-11-04にSource-static確認。旧Issueの「保存Scenario未実装」は限定Referenceが追加された現mainにそのまま適用しない。汎用Scenario compiler/Web E2E/実Provider Write/現行Owner受理は別の未実証領域。

生成AIの自由なCase追加は[Draft #2813](https://github.com/hat47x/tei-platform/pull/2813)のPipeline候補JSONと、[Draft #2811](https://github.com/hat47x/tei-platform/pull/2811)のAI-first Coverage設計を区別。テスト専用JSONとAccepted Driver Scenarioを混同しない。詳細な作業・Negative・資格連鎖は[VA-02 §6](VA-02-cross-product-first-run-protocol.md)に集約。独立ExpectedとCoverage分母の実証は **NOT RUN**。

## 6. 2026-11-06：能力の利用と活動の成果を別々に比較する

[TAI #271 SC-14/15](https://github.com/hat47x/tai-pleroma/issues/271) と[TAI #489](https://github.com/hat47x/tai-pleroma/pull/489)の成熟差分を、VA-01の**価値評価の分母**へ反映する。最初の[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) TEI公開1 Subject／H2実Tool→H3実Skill Loader→4独立Sessionの能力試験はそのまま先行する。ただし「実Toolを正しく呼べた」「SkillでTokenが減った」は利用者の仕事が進んだことの代用にならない。

### 6.1 SCN-001 Activity価値の独立したB0/B1/B2

[SCN-001](https://github.com/hat47x/tai-pleroma/blob/main/scenarios/SCN-001-shared-space-guidance.md)の予約案内の食い違い・未決事項・非公開Draftを中断後に再開する**同じ仕事**で、以下を比較する。

| 構成 | 比較する価値 | 出力で必ず区別するもの |
| --- | --- | --- |
| **B0 手動/通常Markdown・既存Harness** | 外部の追加調整なしで、過去のO-01〜05からO-06の作業を再構成できるか | 原文と版、矛盾・未決、Draft、D-04の実保存後再読取、再確認の手数・時間 |
| **B1 必要な単独Product** | 目的に必要なTEI/SEI/SUI/SHO等の現存機能だけで仕事を改善できるか | Productが実読込/実出力した範囲、未選択・未取得・非開示、現在資格、余分なTool/データ送出 |
| **B2 TAIの条件付き選択・Handoff** | B1を超えて、許可済み根拠の引継ぎ、未完了義務、適切な再開と選択的再確認を改善するか | Task/Attempt/Source/Owner/Grantの対応、反証や未決の保持、誤資格化、追加管理/Context/Token費用 |

**J0全面再確認／J1影響限定／J2無確認再利用**はB0/B1/B2と異なる**再資格化戦略の軸**。各B構成内で比較できるが、「B2=J1」等と等置しない。B2の増分効果が無ければ、TAI常時介在を初期構成に採用しない。逆に機密の不正開示や意味の偽確定を削減効果で相殺しない。

### 6.2 選択から漏れた反証と、開示してはならない存在

[TAI #271 SC-15](https://github.com/hat47x/tai-pleroma/issues/271)と[Draft #490](https://github.com/hat47x/tai-pleroma/pull/490)は、SUI Contextの`selected`と参照のみの`evidence/relations`を分ける固定stubの限定試験候補。**SUI実データの完全な引渡しや実Host開示は未証明**。以下の独立Expectedを既存VA-X/VA-Eへ引き渡す。

- **AC-01**：O-02「予約不要」だけがselectedでも、参照にO-03「会議室は予約必要」相当の未レビュー反証があるなら、非選択を反証不存在としない。ただし未レビュー情報を業務の確定答えへ昇格させない。
- **AC-02**：公開Projectionが同じでも、非公開側に別の反証があり得る。外部Audienceへ反証の存在や件数すら開示禁止なら、その存在を示唆しない。内部Ownerの判断と外部回答の開示範囲は別。判断の状態は現在Grant/Disclosureに従う。
- **AC-03/04**：件数一致でRelationやContext epochを保証しない。O-06後にA→B→Aで表面文言が戻っても古いReview/Authorityは復活しない。履歴Observationsは保ち、現在用途が必要とする分だけ再確認する。

**最小の結果票**：User Job/時点、割付構成、実利用Product、固定Source/権限、独立Expected、原文・異論・未決の保持、実保存/再読取/Consumer、誤回答・過剰保留・漏洩、操作数/Token/時間/人手Review、再開後の正しい到達点を同一Scopeで記録する。これを新Activity Store/Skill Dispatcher/中央Oracle Schemaとして実装しない。

**実行状態**：TEIの限定Product S1とTAIの固定stub/多Repo CIは既存の局所証拠である。**SCN-001 B0/B1/B2の実Activity試行、外部Harness H2/H3、SUI非公開Scopeの実Host確認、SHO D-04再読取の同一Attempt、異モデルVA-X/VA-Eの独立採点、Owner価値受理はNOT RUN**。初回H2をこれらの完成待ちでブロックしない。

### 6.3 再開時の目的・対象・Audienceが変わる場合は別の価値判定

[TAI #271 SC-18](https://github.com/hat47x/tai-pleroma/issues/271)にPD-01〜07の独立Expected案が追加された。**同じSourceと保存済みObservationが存在しても、利用者が今求める成果は変わり得る**。SCN-001のO-06再開時に、目的が「会議室予約案内の矛盾を整理する」から「利用者向け案内を公開する」へ変われば、過去の証拠は歴史的に残せても、公開の適用性、Review、現在のGrant、実送出の許可は別確認である。

**VA-TAI-PD最小対照**：PD-01同一目的でのread-only継続、PD-02整理→公開、PD-03対象の縮小、PD-04内部→外部Audience、PD-05目的取消、PD-06言い換え、PD-07複数目的の同時進行。元依頼/新依頼の原文、Purpose、対象、公開先、固定Source/Revision、独立Expectedを先に照合する。旧目的を無条件継承して未承認公開・Effectを行うことも、ただの言い換えなのに全面停止・再取得することも失敗候補とする。

B0手動／B1単独Product／B2 TAI条件付きHandoffの**利用者価値比較**にだけこの条件を加え、先行するTEI一SubjectのH2/H3 **能力比較**を停止しない。J0/J1/J2再資格化方式は別軸。再開に必要な過去Evidenceの保持と、新用途に対する現在資格を明示的に分ける。判定基準は[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)、開示は[#232](https://github.com/hat47x/tai-pleroma/issues/232)に委ね、中央のPurpose Resolverを増やさない。

**現状**：PD-01〜07は未実行の試験案であり、SCN-001 B0/B1/B2の実比較、実送出、実Host認可、異モデルVA-X/VA-E、Owner価値受理も**NOT RUN**。
