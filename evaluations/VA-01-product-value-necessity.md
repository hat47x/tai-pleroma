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

### 6.4 成果の誤認と過剰停止を同じ価値比較で測る

[TAI #271 SC-19〜21](https://github.com/hat47x/tai-pleroma/issues/271)の成熟分は既存OwnerのAT-01〜09／RQ-01〜07に試験定義があるため、ここでは**B0手動／B1単独製品／B2 TAI条件付き連携**の差分価値に必要な採点軸だけを追加する。

| 軸 | 具体的な限定実測／後続反証 | 利用者価値に対する判定 |
| --- | --- | --- |
| **誤った完了主張** | [TAI merged #493〜#496](https://github.com/hat47x/tai-pleroma/pull/496)のSUI局所TestClient：Archived Read 200でもWrite 423、必要Event欠落は409、HTTP 200で本文`rollback_required`。TEI [merged #3042](https://github.com/hat47x/tei-platform/pull/3042)のExecutor後`EffectUnknown` | HTTP受付・本文のVerdict・現在Grant・実Provider Effect/Receipt・Consumer再読取を別採点。Cancel ACK・rejected・Export監査記録から作用なし／外部到着を推定しない |
| **過剰停止・過剰利用** | [TAI #271 SC-21](https://github.com/hat47x/tai-pleroma/issues/271)で、SUI Agent Profileが未配線ならAgent Route 503でも、他の許可済みread-only Productは使える場合がある。healthz 200はDB/Reader Readyではない | 不適格なActionだけ止め、正当な履歴閲覧・未完成Draft保存・独立Readを継続できるか。TAI追加の不要Tool呼出し、Token/時間、人間の再確認を費用として数える |
| **目的と結果の取り違え** | SC-18/19の目的変更後、旧AttemptのBody遅着や作用不明が存在し得る。SUI候補類似、Export監査重複防止、Local Action成功は業務意味受理や外部受領と異なる | 旧Attempt/Source/Scope/Recipientの帰属を維持し、新しい公開依頼へ実行資格を移さない。同時に履歴自体は消さず、必要な局所再確認で仕事を再開できるか |

**優先順は変更しない**。まず[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の固定公開TEI H2実Tool 1 Session→H3 Skill実Load→4独立Sessionを評価し、その後SCN-001 Activity B0/B1/B2へ。本表のEffect/Export/Hostの負例はSCN-001の公開・実書込みを捏造せず、用途が必要になった段階で隔離した別Caseにする。B1で同等の正確さ・費用ならTAIは任意と判断してよい。

**試験状態**：#493〜#496/#3042の各局所結果は既存Productに帰属する。AT/RQの**横断実Task**、実Host Grant、外部Recipient受領、SCN-001利用者価値比較、異モデル独立評価、Owner正式受理はNOT RUN。

### 6.5 実Tool接続の成立と、Skill／TAI増分価値を分ける

[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)／[TEI Draft #3113](https://github.com/hat47x/tei-platform/pull/3113)により、外部DSH経由の**実Tool起動・TEI結果受信**は有限の技術実証を得た。ただし当該9探索試行は参加者の非露出隔離が守られず、Model/Adapter障害が混在し、独立採点も未実施。このため**「製品へ接続できる」価値の一部はObserved、「Product Skillを追加すると正答・費用・確認負荷が改善する」はNOT RUN、「TAIが利用者の活動を改善する」もNOT RUN**と別表示する。

最初の対照は固定した公開TEI一SubjectをTool-only H2で扱い、参加者が見えてよいSource/Tool/Reviewer Expectedの境界を実OS/Harnessで拒否対照化したのちH3へ進む。H2/H3の差がゼロまたは負であればSkillを常時使わない。さらに[TAI #514](https://github.com/hat47x/tai-pleroma/issues/514)のOKF Attested Computationは、計算定義の説明/検証情報が通常のCLI+既存Receiptに対して追加価値を持つかを**後続1件のRead-only計算**で判定する。OKF文書のverified/Attester PASSはOwnerの業務意味受理・現在Grant・結果の新鮮さと別。OKF用新共通Attester/Skillを初回H2/H3のHard dependencyにしない。

**現状**：実DSH→TEI CLI接続は限定Observed、正式な隔離済みH2 Trial・Skill実ロード・H2/H3増分価値・TAI Activity B0/B1/B2・OKF実Attester/価値採点・Owner受理はNOT RUN。

### 6.6 H3実読込成立後の価値判定：不必要な実行を避ける成果も測る

[TEI mainの四Session Witness](https://github.com/hat47x/tei-platform/blob/main/plan/evidence/DSH_H2_H3_FOUR_SESSION_2026-11-07/README.md)で、H3-A/Bは各Skill root 5,482 bytesと参照文書1件を実受信した。これは**Product Skillの実動作能力の到達**であり、比較用に事前登録した独立H2/H3の4腕は**適格0/4**である。旧H2-AのSession再利用・Worktree越境Read・Task path差・Tool受領欠落を残したまま、H3のTokenやcompletedを改善・悪化の因果結論に使わない。次の価値ClaimはG0/G1/G2を通過した新規Groupだけで問う。

[TAI #531](https://github.com/hat47x/tai-pleroma/issues/531)／[価値実現Draft #532](https://github.com/hat47x/tai-pleroma/pull/532)の外部Pressure Caseは、**Goal→実Source/Meaningの消費→Action Intent→現在のHost権限→実Provider効果→実Consumer受領→利用者/組織のOutcome**を分離する必要性を示す。Oracleの一体型Runtimeや50%削減主張をTAIへコピーせず、既存VA-TAI B0/B1/B2の**価値採点条件**にだけ必要な差を取り込む。

| 結果 | 採点する増分価値 | 誤って完了としない条件 |
| --- | --- | --- |
| **正しいread-only継続** | 単独ProductやTool-onlyでも必要な出典・不確実性を残し、最小の手間で再開できた | Skill実LoadやToken減少だけで利用者Outcomeへ昇格しない |
| **適切な不実行・保留** | 未受理の公開・権限不足・旧Research版・作用不明を示し、禁止Actionを行わず正当なReadを継続 | 何もしなかった結果を自動PASSにしない。必要なActionの誤拒否・副作用未観測・部分失敗を区別 |
| **実Action後の成果** | 現在Purpose/Audience/Grantの下で、Receiptと実Resource readback、Consumer受領、業務の受入を個別に確認 | 旧Receipt、`completed`、HTTP 200、保存ACK、合成AttesterのPASSだけでは成果ではない |
| **TAI追加介在の費用** | B1単独Productと比べ、説明の質・誤完了・過剰停止・再確認時間・Tool/Token/費用が改善するか | B1で十分ならB2は採用しない。実験していない機能を将来価値として得点化しない |

**初期Trialは変更しない**。まずH2/H3固定公開TEI read-only Jobと実隔離/送出/Tool Result完全性を確認。その後SCN-001のB0/B1/B2でPurpose変更や中断再開の正負対照を行う。Result-first/Outcome-firstの新共有Runbook、Outcome DB、独立Oracle（独立Expectedの別正本）を追加しない。[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)は現在の用途適格、[#168](https://github.com/hat47x/tai-pleroma/issues/168)はTool/Skill試行、各ProductはEffect/意味、[#422](https://github.com/hat47x/tai-pleroma/issues/422)は価値比較を担当する。

**状態**：Tool技術到達とH3実Loadは限定Observed、H2/H3正式比較適格0/4。利用者Outcome、現実の業務Action、Effect/Consumerの一Attempt E2E、異モデル独立採点・Owner意味/価値受理は**NOT RUN**。


## 7. 2026-11-07：Issue単位の義務化判定票と独立反証の最小入力

本節は[横断計画§21](../docs/yi-constellation/product-value-scope-audit-2026-11-04.md)からの評価用抜粋。**静的な提案であり、各IssueのClose/要求変更の提案ではない**。不変条件（I）と導入方式（R）を別欄に持ち、`conditional`は「用途条件が成立したとき必要」、`research-only`は「検証を止める」の意味ではない。

| Case | 代表Issue・仮の処遇 | B1だけで満たすべき対象／守るI | B2を義務化できる反証条件・独立Expected |
| --- | --- | --- | --- |
| **VA-TAI-01** | [TAI #74](https://github.com/hat47x/tai-pleroma/issues/74)は配布`conditional`、[#168](https://github.com/hat47x/tai-pleroma/issues/168)は外部Harness接続`core`の受入実験、[#271](https://github.com/hat47x/tai-pleroma/issues/271)は用途相対の再開 | 必要な一製品のSource/Unknownを正しい範囲で読める。許可外Sourceは物理的に拒否、遅着Receipt/旧Grantは結果にしない | 複数Productの改版・別Harness引継ぎでB1が失敗し、TAI追加で誤継承/再確認負担が独立に改善。初回H2/H3は**現在0/4適格**であり、新しいG0/G1/G2を省かない |
| **VA-TEI-01** | [#1127](https://github.com/hat47x/tei-platform/issues/1127)／[#1180](https://github.com/hat47x/tei-platform/issues/1180)は最小機能の`core`候補。[#2619](https://github.com/hat47x/tei-platform/issues/2619)は抽象化`conditional`、[#1223](https://github.com/hat47x/tei-platform/issues/1223)の無停止更新は配備条件付き | 1 FunctionのData/Relation/Rule→操作→保存→再読込と独立Expected。NULL/粒度/同時更新/現行Grantを保持。別CLI/Web入口の違いを観測 | Target交代・複数配備・業務無停止を必要とする具体的SLOで、B1にない欠陥を示す。最初の一件に全Plugin/全Domain/全Targetを必須化しない |
| **VA-SEI-01** | [#711](https://github.com/hat47x/sei-cognition/issues/711)の根拠入力と[#758](https://github.com/hat47x/sei-cognition/issues/758)のverify判定は`core gap`候補。[#660](https://github.com/hat47x/sei-cognition/issues/660)/[#767](https://github.com/hat47x/sei-cognition/issues/767)の全面Method化は用途条件付き | 一件のDecisionをResumeし、根拠/Scope/Unknown/ExactBinding/未検証件数を消さない。未検証recordを含む`verify exit=0`を偽成功と採点する | 実務再開で汎用Methodなしでは誤再構成が残る時のみ、必要なCognitive Methodを導入。全項目必須フォームと第二Truth Engineは比較しないまま採用しない |
| **VA-SUI-01** | [ADR-0089](https://github.com/hat47x/sui-sensemaking/blob/main/01_Plans/adr/ADR-0089-product-value-canon.md)の保留/根拠復帰は`core`、[#3371](https://github.com/hat47x/sui-sensemaking/issues/3371)のDocumentV1投影は接続条件付き | 実務T2の一Documentで異論/保留を保存→再表示し、非公開Card/Relationの存在や件数を漏らさない | 外部Consumerが必要とする内容・loss予算を示してProjection採用を判定。型検証だけでSUI原本へ逆保存したとしない。文化MethodはT2比較後 |
| **VA-SHO-01** | [#4](https://github.com/hat47x/sho-composer/issues/4)/[#7](https://github.com/hat47x/sho-composer/issues/7)のS0/L0は`core`、[#8](https://github.com/hat47x/sho-composer/issues/8)の論文→実装は`conditional`、[#9](https://github.com/hat47x/sho-composer/issues/9)が価値比較 | 取得していない3つの架空URLでもリンク階層とメモを保存・再開し、未取得と出典未確認を明示。MMIを利用しない構成で成立する | DOI/PDF/複数論文関係・実装/数式の用途で通常Markdownに比べて意味誤読・手戻りが減ることを示す。出典確認をしないまま論文主張へ昇格しない |
| **VA-EKI-01** | [#58](https://github.com/hat47x/eki-fabric/issues/58) Suitability＋MVP結果経路は`core`、[#19](https://github.com/hat47x/eki-fabric/issues/19) MLは`research-only`、[#155](https://github.com/hat47x/eki-fabric/issues/155) Fairness・[#67](https://github.com/hat47x/eki-fabric/issues/67)複数管理Providerは`conditional` | 小CPU Taskを分散しない、分散適合Taskは許可Workerへ配置・同一AttemptのBody/Resultを確認、途中停止/期限切れ・回復予算を守る | 飢餓や高負荷/多組織、可用性・通信の実条件でB1が不足する場合にだけFairness/ML/複数Providerを比較。到達ACKや平均遅延の改善だけでは採用しない |

**二方向の独立Expected（最小6対）**：各行で「高度化なしでも正しく完了・保留できる」正例と、「意味・安全を削ると誤成功または過剰停止する」負例を一つずつ、提案Agentと独立に固定する。B2優位を示せない場合は`not-justified-for-this-job`、測定不能なら`unknown`と明記し、研究自体の停止やCoreからの一律削除にはしない。手戻り、人の確認回数、Tool/Token/CPU/通信、外部送出と導入・運用コストは分離して記録する。

**優先度の扱い**：初回の正式H2/H3に新たなBlocking Conditionを追加しない。既知の隔離・送出・Tool Reply完全性（G0/G1/G2）を最優先し、並行してSEI #758の誤成功、SHO L0の単独保存、SUI T2、TEI #1127/1180とEKI #58の一往復を各Ownerの現行試験へ接続する。TEI Studio全画面、全Target、EKI高度Data Plane、SHO Paper-to-Program、SEI全Methodの完成は同一の前提にしない。

**今回の証拠の資格**：Source-staticの要件・Issue照合と比較票の追加のみ。6対の独立Expected確定／別モデルVA-X／VA-E実行／B0/B1/B2実測／人の利用価値／各Owner受理は**NOT RUN**。


## 8. 2026-11-07：既存実証に接続した最小差分の独立Expected

[横断計画 §22](../docs/yi-constellation/product-value-scope-audit-2026-11-04.md)からの**実行可能な反証指定**。当表は現行Productの新しいAcceptance Gateを発行しない。「機能が存在する」「設計が製品要求に載った」「利用者価値が証明された」は別判定である。実行者はSource/Tool/HEAD/Scopeを固定し、Expectedを生成候補の出力に合わせて後修正しない。

| Case（既存Owner） | 事前固定する二世界・独立Expected | 通過時に言えること／次の縮退判断 |
| --- | --- | --- |
| **VA-TEI-T1** [TEI main #3304](https://github.com/hat47x/tei-platform/pull/3304)、[#1180](https://github.com/hat47x/tei-platform/issues/1180) | **T1-Aは限定Observed**：既知の行番号正数Ruleに対して0を与え、既存CLIで拒否を判別。[CI #42378033965](https://github.com/hat47x/tei-platform/actions/runs/42378033965)は偽Expected/Fixture/旧Pin負例も検査。次は独立Required Rule/Relationの部分欠落（TT-56）を既存Context Gateで拒否した後、未知RuleをAIが発見する**盲検T1-B**を別Expectedで採点 | 既知Caseの第7Stepを実行できてもAI新規発見・C1・全製品Coverageとはしない。旧T1-Aを未実施と再掲せず、新Runnerや第二Scenario正本は作らない |
| **VA-TEI-PLUGIN** [RQ-008](https://github.com/hat47x/tei-platform/blob/main/requirements/TEI_PRODUCT_REQUIREMENTS.md)、[main #3337](https://github.com/hat47x/tei-platform/pull/3337)、[#1251](https://github.com/hat47x/tei-platform/issues/1251) | A＝一つのInspectorに必要なKind+IDのCapabilityがEnvironmentから選ばれ、実Build→CLI Consumer呼出しを観測。B＝別Environment用Capabilityが未選択でも、このInspectorの実操作は成功。C＝Inspector自体のBinding/Link/Invocationが欠ければ当該操作だけ unavailable/unknown とする。plugin selected と capability bound は違う | #3337の「宣言12・全環境未選択6（DB Provider種別差を含む）」を欠陥件数にしない。全Providerの選択義務も、選択を実利用資格へ昇格させることも禁止。業務Grantは別証拠 |
| **VA-TEI-BOM** [#3267](https://github.com/hat47x/tei-platform/issues/3267)、[Draft #3269](https://github.com/hat47x/tei-platform/pull/3269) | A＝宣言された候補Pair12、B＝実Lock供給Pair9の差を欠落3として保持。BのReference synthetic PASSだけではqualified=false。実Consumer/Independent Expectedがある選択Pairのみ検証し、同じProviderとConsumerでも別版は未試験として残す | Verified BOMの**組合せ別資格**を最小採用。9/9を12/12へ昇格せず、組合せを利用しない単独読取の前に全Version Matrixを要求しない |
| **VA-SUI-SHO-FILE** [SUI #3397](https://github.com/hat47x/sui-sensemaking/pull/3397)、[SHO #21](https://github.com/hat47x/sho-composer/pull/21)、[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271) | A＝両Repoの別々の354-byte Fixture CI（固定Raw PASS）。B＝SUI実Producerが新規絶対Pathへ1回書き、SHO実CLIが**同じPath・同じBytes**を読む（現CIは1 SKIP）。両者のPath、SHA、mtime、Source/Scope、CLI結果を比較。非公開カードや失われたIsland/Edgeを出典付きとして復元しない | B実行後でも「read-only一File受領」のみ。SHO Writer/公開Scope/Source認可・意味受理は別。新Handoff Serviceを作る根拠にしない |
| **VA-SHO-L0** [#4](https://github.com/hat47x/sho-composer/issues/4)、[#19](https://github.com/hat47x/sho-composer/issues/19)、[#20](https://github.com/hat47x/sho-composer/issues/20)、[TEI #3031](https://github.com/hat47x/tei-platform/pull/3031) | A＝通常notes.mdと管理外の下書きorder.tei.mdを、AI/OKF/TEI Language Plugin/CloudなしでRaw no-op保存・再開。B＝管理済みSource Rootの未対応tei.mdはTEI解釈を拒否するが、SHO Raw Draftの保存まで拒否しない。C＝外部Editor競合・BOM/CRLF/未定義Referenceは原文を勝手に正規化/上書き/網羅断言しない | G1b Readerの限定CIはSHO Writer受入ではない。新DB/Parser/全Vault同期を第一価値の前提にせず、原文Byte/Writer readbackとMeaning/出典資格を分ける |
| **VA-RQ-IDENTITY** [TEI #3223](https://github.com/hat47x/tei-platform/issues/3223) | A＝同じRQ-035表記でも、main WorkbenchとBOM Draftの意味・Source ref/Blobを別に提示。B＝IDだけでMergeする旧処理なら意味衝突を見逃す。実Ref単位の採用前照合で誤上書きを拒否 | 中央Requirement Registryなしの差分検査で十分か判定。旧Draft #3269 closed/unmergedをRequirement acceptedとして扱わない |

**優先順位**：既存実証の欠落一辺は TEI T0→T1、SUI/SHO 別Fixture→同一File、SHO Reader→Writer readback、TEI Plugin要求→単一実Consumer の4系統。互いに独立に実施でき、TAI #168の現行H2/H3 G0/G1/G2を追加でブロックしない。SEI #758のverify偽成功とEKI #58の「分散しない」選択は§7の独立レーンで保持する。

**判定状態**：Product側に既存の限定CI・Go Reference・Fixture実測はあるが、**本VA-01としての6ケース独立ExpectedのOwner固定、今回の新CLI/同一File/Writer/Target比較、別モデルVA-X/VA-E、人間のUser Job比較はNOT RUN**。これは実証の引用範囲を精密化する更新であり、検査を実施した報告ではない。

## 9. 2026-11-07：余分な必須属性と不完全な根拠を、同じ利用者価値票で対照する

[TAI #535](https://github.com/hat47x/tai-pleroma/issues/535)で、SUIの任意`Edge.fromKind/toKind`をTAIの必須契約として投影するとEdge自体が欠落し、**契約の任意化だけで投影は可能**という局所試作が示された。反対に[TEI #3262](https://github.com/hat47x/tei-platform/issues/3262)のDesign Context/Source Gateと[#3267](https://github.com/hat47x/tei-platform/issues/3267)のVerified BOMは、証拠が不完全なのに採用/実行可とするのを拒む**必要な必須条件**である。どちらも常時拒否/常時受理で解決しない。

| 価値対照の独立Expected（提案） | B0既存方式／B1最小Product／B2追加TAIの評価 | 判別すべき反例 |
| --- | --- | --- |
| **VA-MIN-E1 正当な任意Edge** | 同一公開SUI Graph（明示種別、種別省略、片側null、複数有向辺）を表示/選択/関連参照し、*消えた正当Edge・不要な手動補完・誤った結線*を測る。B1で任意契約が足りる場合、TAI追加Resolverを価値として計上しない | 種別が未定だからEdgeが存在しないと消す／欠けた種別を勝手に復元／non-publicなEdgeのID・件数を開示する |
| **VA-MIN-T1 Context／新Testの資格** | [#3304](https://github.com/hat47x/tei-platform/pull/3304)で既知Ruleの行番号0を**実CLIで判別したT1-A**を基線とする。同じ公開Subjectに対し（a）Rule/Relationが正常JSONのまま欠落するTT-56、（b）Required外のSubjectだけ省略する正例を区別し、**必要情報不足の診断精度・誤拒否・修復手数**を測る。Required閉包後に未知Obligationを見つける盲検T1-Bを独立Expectedで採点する | 実CLI T1-AからAIの自律発見へ昇格／subjectモードのIndexで全件定義済みと誤判定／正常FPでもRequired Rule欠落を見逃す／非必須欠落まで全部拒否／C0相当10.1%をC1や全要件網羅と宣言 |
| **VA-MIN-B1 候補BOMと適格BOM** | 同一Provider×Consumerの版・Target/Artifactを指定し、実Checker/独立Expectedが到達した組合せだけ薦める。候補を誤って除外した件数、検証不足を根拠に薦めた件数、手動ロック指定の手間を別採点 | `observed-pass`合成Reference／未提供UniverseのPairwise／別Scopeの旧Receiptを`qualified-in-scope`とする |
| **VA-MIN-S1 移行・再開時の部分継続** | 任意Edgeの合成意味やText/G1b Readerの未対応を理由に、独立したread-only検索・未完成Draftの保存まで止めないか。必要な実Actionだけ現Grant/Owner確定を待つ | 部分的なSource不足を全Activity停止へ拡大／逆にReader未読を完全な編集・公開資格とする |

**最低限の観測票**：同一User Task・Source/版/意味/現在Audience、Tool/Builder経路、Required Input、実Provider/Result、判定`success/partial/unknown/denied`、追加手動操作、誤停止・誤完了・正しく保留した件数をB0/B1/B2の**各々で独立に**記録する。非開示対象の件数や暗黙のGraph意味を外へ露出する採点器を作らず、既存[#422](https://github.com/hat47x/tai-pleroma/issues/422)と[#271](https://github.com/hat47x/tai-pleroma/issues/271)、TEI #1180/#2514とSUIの独立Expectedを参照する。

**最新の証拠境界（11月7日夜）**：[TEI #3304 CI #42378033965](https://github.com/hat47x/tei-platform/actions/runs/42378033965)は一時Scenario第7Stepと偽Expected/Fixture/旧Pinの限定実CLI判別。TT-56用[Draft #3326](https://github.com/hat47x/tei-platform/pull/3326)はsubjectモードのSource Indexで全Definitionを期待した初回CIが失敗し、**試験Consumerのモード誤り**を特定。既存の全件indexモードを追加した後の[専用CI #42385726717](https://github.com/hat47x/tei-platform/actions/runs/42385726717)は`bounded-design-context`ジョブ成功。一方、並行[Draft #3324](https://github.com/hat47x/tei-platform/pull/3324)は同じContext Gateへの1 Rule＋Relation/Canonical照合案であり、**両DraftのCIを合成実装のPASSとしない**。#3262/#3223のOwnerが実Requirement集合・関係の追加必要性を決め、一本化した正確なHEADと実CLI→Context Consumerで再確認する。`qualifiedTestGeneration=false`、独立Holdoutを隠したT1-B、C1、正式User価値は未達。

**停止線／優先**：TEIの初回H2/H3固定Trialはそのまま。Edgeの現行パイロット契約を本Draftから変更しない。#535の局所試作/88段Suiteの結果、TEI限定CI、BOM合成参照を横断ActivityのPASSへ昇格しない。**VA-MIN-E1/T1/B1/S1のB0/B1/B2実User試行、未知GapをAIが盲検発見するT1-B、Source/Host/Role受理、Plugin/BOM実Target、Owner意味判断・VA-X/VA-E独立実証はNOT RUN。既知T1-Aのみ局所Observed。**



## 10. 2026-11-07：用途に無関係な前提による過剰停止を実測する

[横断監査 §22.5](../docs/yi-constellation/product-value-scope-audit-2026-11-04.md)を、**過剰停止と誤成功の対称な試験**に落とす。新しい共通データモデルや採点エンジンは作らない。評価者は各Productの独立Expectedを採用前に固定し、Target/Source/Grantの必要Scopeだけ指定する。

| ID | 利用者Job／同一条件の対照 | 正しく通す／正しく止める | 過剰設計の判別 |
| --- | --- | --- | --- |
| **VA-NC-01 Plugin未選択は正常** | TEI一つのread-only Inspector。別Environment向けProvider・未使用のmigration能力を残したBundle／それらを全選択させる構成の比較 | 指定Inspectorが実選択・実Consumer利用可能なら通す。Inspector自身のBindingが無い場合だけ当該操作を不可とし、他のModel参照は妨げない。plugin lock名とCapability Kind+IDを混同しない | 追加手動選択数、不要Plugin実Build混入、誤拒否数、選択したが未使用の誤PASS数 |
| **VA-NC-02 文書保存と意味解釈** | SHO通常Markdown／管理外のtei.md DraftをRawで保存する場合と、TEI管理SourceとしてParserへ渡す場合 | SHOはBOM/CRLF/未知Fenceをno-op保持して保存再開。TEI Loaderの未束縛はTEI解釈だけ拒否。OKF未導入・AI OFF・Cloud OFFを正常正例とする | 保存できない誤拒否、原文Byte破壊、未解析をAccepted Meaningにした誤成功、操作回数 |
| **VA-NC-03 Build段階を偽装しない** | 通常Go Build／子Process Stage Driver／Stage1生成物が次のBuildを駆動するself-buildを区別 | 子Buildのinvoker/invoked/実Disk SHAが一致してもL3として採点しない。一方L3未達を理由に通常Buildと検証済み単体inspectを拒否しない | L3誤成功、通常Buildへの不要な追加手順、Artifact照合漏れ |

H1 SUI→SHOは[SHO #21](https://github.com/hat47x/sho-composer/pull/21)のRunner構文・偽Checkout起動前拒否が限定CI成功（Ubuntu/Windows **20 PASS・1 SKIP**）。実同一File受領はSKIPのままなので、本表のNC-02やSUI→SHO横断のPASSへ合算しない。

**既知のProduct証拠**：[TEI #3337](https://github.com/hat47x/tei-platform/pull/3337)はread-only列挙・Go Reference限定PASS、[#3336](https://github.com/hat47x/tei-platform/pull/3336)は別Process BuildとArtifact digestの限定Observed。[SHO #4](https://github.com/hat47x/sho-composer/issues/4)のWriterと[TEI #3031](https://github.com/hat47x/tei-platform/pull/3031)の実Parser対応は未完成。VA-NC-01〜03の**同条件B0/B1/B2実比較／独立レビューVA-X／VA-E／Owner受理はNOT RUN**。


## 11. 2026-11-08：価値の誤停止と、証拠の誤昇格を同じ母数で比較

[VA-04 §10](VA-04-evidence-readiness-preflight.md)の限定正証人・不存在主張の閉包を、§9〜10で定義済みの**同一User Job・B0/B1/B2**に接続する。新しいテストCase正本・共通採点Engineは作らない。既存Expectedを固定し、各構成で「正しく継続」「正しく拒否」「誤って拒否」「誤って成功表示」「証拠不足で保留」を別件数と手動操作数・待ち時間で測る。保留を無根拠の成功/失敗へ繰り入れない。

- **TEI**：[#3354 merged](https://github.com/hat47x/tei-platform/pull/3354)でTT-56の二Draftを一本化。11実CLI/32合成Consumer対照は限定Source資格であり、独立Required全件・未知RuleのAI盲検T1-BのPASSではない。[#3365 Draft](https://github.com/hat47x/tei-platform/pull/3365)の局所Step Receiptは残しつつ、未受領目録から全体未テスト確定を推論しない。空配列・別モード・必要外未読込の不当拒否も数える。
- **Plugin/Workbench**：未選択の別環境用Capabilityを含んでいても必要Inspectorは実選択→実Provider Invokeで評価。物理FKが観測されたことだけでBusiness Relation/CRUD生成を業務受理せず、逆にFKが無いだけで手動Relation定義の正当性を否定しない（TEI #3270、Draft #3371/#3372）。
- **SHO/TAI/EKI**：未解釈Markdownの安全な保存、実同一File受領未達の明示、空対象集合でもHandoff確認が必要な区別（TEI #3353）を各Productの独立試験に委譲。SHO WriterやSUI→SHO実H1はTAI H2/H3比較の先行必須にしない。

**更新時の境界**：§9に記した#3324/#3326並行Draftは当時の記録。現在はclosed/unmerged、統合#3354がmerged。今回のVA-01自体での新しいB0/B1/B2利用者比較・未知T1-B・実Provider/Studio・SHO Writer/H1・適格H2/H3、Owner採否は**NOT RUN**。既存局所CIを総合価値PASSへ足し合わせない。


## 12. 2026-11-08：独自Harnessの投資条件を、製品能力の増分で判定する

[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)・[#488](https://github.com/hat47x/tai-pleroma/issues/488)のH2/H3固定比較を変更せず、**YI Constellation独自の汎用Harnessを最初から構築する必要があるか**を、別の後続価値試験として明示する。既存外部HarnessはTool/Skill/PluginやSession機構を備える場合があり、TAIの増分は製品固有のDesign Context・SEI根拠十分性・安全な意思決定・再開・開示といった**成果に帰着する差**で示す。Everything is Plugins型の汎用化を理由に、TEI/SEIのMethodやOwner Meaningの正本をHarnessへ移転しない。

### 12.1 実装しないことも判別できる逐次比較（既存H2/H3のArm名を上書きしない）

| 後続比較Arm | 同じUser Jobで実行する構成 | 価値がなければ採らない追加要素 |
| --- | --- | --- |
| **HV-0** | Product自身のCLI/既存UIによる同一Sourceのread-only作業 | Harnessを使うこと自体 |
| **HV-1** | 既存外部Harness＋Productの実Tool。Skill説明なし | YI独自Harness、TAI常時介在 |
| **HV-2** | 同じ外部Harness＋必要なProduct Skill（固定rootと実Reference Load） | 複数Product横断Skillの自動必須化 |
| **HV-3** | 既存Harnessの既存Plugin/Tool適合層を通じ、TEIのRequired Context、SEIの限定Inquiry等を**実呼出** | 独自実行ループ、第二Resolver/Permission Engine |
| **HV-4** | HV-3では達成不能な一つのProduct固有不変条件を先に独立Expectedで固定し、その不足だけを補う専用ループ候補 | 一律の自前Harness移行・全製品共通常駐 |

**比較の開始条件**：既存SK-02のG0物理隔離／G1副次送出／G2全Tool Reply受領を満たす実Harness環境と、同一公開Source・Task・Model版・予算・Expectedがあること。現時点では既存H2/H3比較適格は0/4。**HV-0/1/2の実比較もまだNOT RUN**であり、H3実Skill Loadの歴史的Observedのみを増分価値PASSとしない。HV-3/4はH2/H3の完了を妨げず、Product側単独MethodやPlugin試験を先行してよい。

### 12.2 費用対効果の独立Expected
- **成果**：根拠付き正答、重大な誤完了/誤拒否、Domain Obligation欠落の診断、未決として保持できた比率、後続Consumer実受領、再開後の同一Purpose/Scope/Revision、Ownerが必要な確認手数。
- **安全・適格**：Source開示の物理拒否、Skill/Reviewer Holdout非露出、Session Log/Network別Sinkの実送出、現Grant、実Effect／未知Commit、Agentに許す判断と人が受理する判断を分ける。安全の重大違反を低Token費用で相殺しない。
- **費用**：初回接続/Skill作成/Plugin適合作業、Runner更新負担、Prompt/Token/計算・通信費、人の介入・復旧・監査時間、既存Toolchain移行量、p50/p95作業完了時間。少数試行を一般的な統計優位と宣言しない。
- **独立性**：各Armの割付、実際のTool/Skill/Plugin提供とConsumer受領を分離。モデルに盲検Expectedや隠れたSourceを渡さない。同一モデルの別Context・多数決は独立Expectedや別モデル実反証ではない。

### 12.3 TEI/SEIの高付加価値を先に比較する（新しいProduct Method実装を作らない）
[SEI Draft #824](https://github.com/hat47x/sei-cognition/pull/824) §9.2はD0（通常Tool）/D1（根拠・不足診断）/M1（SEI Method）を**同条件**で比較するH3-X01〜08を計画化し、正常な空result/Source Index mode/Plugin selected≠invoked等の不足を識別する。最初の比較はH3-X02（独立Required Ruleと実取得Mode）。**M1がD1より成果・費用・誤判定で優越しなければMethod常時必須化はしない**。TEI [#3262](https://github.com/hat47x/tei-platform/issues/3262)の実Contextと[#3482 merged](https://github.com/hat47x/tei-platform/pull/3482)のFunction declaration sliceを入力候補にするが、Functionの実Provider ReadやSEI実Tool連結の成立は別証拠。

**新しい独立Negative案**：HV-N1=Skillに手順があるだけで実Tool未実装、HV-N2=Plugin selectedだがactual invokedは別Provider、HV-N3=正常な空Resultから全業務Source不存在を断定、HV-N4=H2/Skill独立Expectedや非公開Rawへ越境Read、HV-N5=SEI Method回答は良いが現在のGrant/受領なし、HV-N6=独自ループの費用が継続的に増えるのに独立ExpectedでHV-3を超えない。全て**新規実行NOT RUN**。

**採否の停止線**：初回外部Harness H2/H3の資格確認を最優先、既存TEI/SEIのMethod/Pluginを接続して成果を測る。HV-4は、既存HarnessとPluginでは再現・隔離・再開・意思決定の必要条件を満たせない**具体的反例**と、専用実装で改善できる見込みが独立評価で示された場合だけ設計レビューする。独自Harnessの新Runtime/Plugin Manager/Memory/Tool Routerの先行製品化を承認しない。


## 13. 2026-11-08：SUIの認知価値と情報統合価値を混同しない対照実験

[監査 §23](../docs/yi-constellation/product-value-scope-audit-2026-11-04.md)の具体的比較票。現行一次価値は[SUI ADR-0089](https://github.com/hat47x/sui-sensemaking/blob/main/01_Plans/adr/ADR-0089-product-value-canon.md)。[#3400](https://github.com/hat47x/sui-sensemaking/issues/3400)のSensemaking体験と[#3401](https://github.com/hat47x/sui-sensemaking/issues/3401)の異種Source統合は**両方重要な検証仮説**であるが、後者のProvider/DB/統合Viewを前者の成功条件にしない。以下は各ProductのSV/II/CUケースの第二正本ではなく、**何に投資するかを判断するための比較設計**。

| YIC比較Case | 同じ利用者課題に与えるB0/B1/B2 | 観測する独立Expectedと失敗 | 次の投資判断 |
| --- | --- | --- | --- |
| **VA-SUI-V01 理由にならない違和感** | B0＝紙/Markdownで原資料を読む、B1＝AIなしSUIのRaw/配置/保留/翌日再開、B2＝同じSourceをAI候補・別配置を見た後に再開 | 初回の自力の見立てをAI提示前に記録。理由を説明できない保留・異論を保持、後付け理由を元の日時へ偽装しない。AIによる気付きと誘導/混乱を別列。カード枚数・整理速度のみで成功にしない。[SV-03/05/08](https://github.com/hat47x/sui-sensemaking/issues/3400) | B1で最初の価値を測り、B2は認知上の純増・損失・介入費用を評価。録音・全資料OCR/LLM必須化はしない |
| **VA-SUI-V02 意味の単位と複数の見方** | 同じ原文1件と2 Canvasの複数Occurrence。B0＝原文/手動マップ、B1＝単一CanvasでCard/Island/Tree別投影、B2＝必要時だけ複数Canvas/別Viewer | 意味として一体の経験を文単位に強制分割しない。Node同一・Canvas座標差・Tree親子/Island所属を合一しない。読み返せる原文・非公開Scopeを保つ。[SV-01/06/09](https://github.com/hat47x/sui-sensemaking/issues/3400) | 全Graph Schemaや複数Canvas Editorの**同時実装は不要**。一Canvasの意味保持不足・実務分割需要が出た機能だけ評価 |
| **VA-SUI-I01 3異種Sourceと同定の仮説** | B0＝既存DB/表計算/文書の手動参照、B1＝SUI Cardへ手動投入、B2＝RDBまたはCSV・文書・時系列Eventの限定SourceRefを読取って2 Viewで照合 | Source/Revision/有効時刻/粒度が別でも同一人物/案件と自動確定しない。転載2件を独立証拠2件に数えない。非公開SubjectのID/件数を出さない。[II-01/02/03/07](https://github.com/hat47x/sui-sensemaking/issues/3401) | B2で**新しい重要な関係が発見できたか**と誤同定/コストを測る。高価な万能Query/中央DB/全ViewやVector/RAGはB2入口にしない |
| **VA-SUI-I02 Partialと誤結論** | 一つのSourceだけ最新、もう一つは遅延・一部未取得。B1/B2の同じ問いの説明を比較 | 一件の観測は限定存在証人、見つからなかった対象は全件不在と断言しない。古いIndexに「現在」と付けない。Scenarioは実Effectでない。[II-04/08/10/11](https://github.com/hat47x/sui-sensemaking/issues/3401) | B2の速度/回答数改善を完全性/業務成果として合算しない。実ProviderやAuthority不足は対象Claimだけunknown |
| **VA-SUI-C01 二人の保存と判断** | 同じ文書Revision r0からA/Bが別Cardと保留を編集。単独Browser Undoと2 Client CAS保存を対照 | Bが先着保存した後、Aの古い保存は409でdirty buffer維持。AのローカルUndoはBの確定値・意味判断履歴を巻戻さない。保存ACK喪失時はEffect unknown。[CU-01〜04/09](https://github.com/hat47x/sui-sensemaking/issues/3399) | まずDocument CAS/保存時同期。CRDT/常時同期/Event Sourcingは2 Client実証の不足が出たときだけ |

**測定欄**：Sourceの出典と現Audience、資料への復帰、理解の変化・新発見・残る異論、誤同定・誤要約・秘密露出、正しい部分継続/過剰停止、次に必要な外部Source・人の判断、介入操作数/時間・Tool/Token費用を別列。異質な認知成果を単一Total Scoreへ合算しない。SUI製品自身の内部dogfoodは実務T2に数えず、SUI外の実務資料でAI OFF→必要時AI ONの順を記録する。実第三者T1は得られた場合の別証拠であり、T3模擬試験の多数決で代替しない。

**採否の順序**：まず[#3400](https://github.com/hat47x/sui-sensemaking/issues/3400)のV0/V1で一仕事の理解変化と再開を確認する。別レーンで[#3401](https://github.com/hat47x/sui-sensemaking/issues/3401)のI0→I1→I2をread-onlyで実証。共同編集は[#3399](https://github.com/hat47x/sui-sensemaking/issues/3399)の最小2 Clientだけ。SUIのActionIntentは外部Effect/Hostの承認と別資格であり、YIC新Runtime/中央Data Serviceを作らない。TAI #168のH2/H3比較Blockingへ新しい要件を加えない。

**証拠の状態**：上記5ケースの比較は設計提案・Product Source-staticの対照まで。実B0/B1/B2、独立ExpectedのProduct Owner固定、SUI実務T2／第三者T1、異種Source 3系統のProvider実Read、2 Client保存E2E、AI効果測定、Owner正式受理は**NOT RUN**。


## 14. 2026-11-08：不明な実行結果を「成功／失敗」に押し込めない価値試験

[横断監査 §24](../docs/yi-constellation/product-value-scope-audit-2026-11-04.md)の **VA-RC-01** を既存VA-01の対照実験へ接続する。追加の共通Runtime/Receipt/再試行機構ではなく、既存Productが現に所有する確定境界・独立Readで検証する。新たな製品要件の採否はOwnerへ返す。

| 比較 | B0 既存手段／B1 Product／必要時B2追加連携 | 独立Expected・価値に数える成果 |
| --- | --- | --- |
| **RC-01 確定直前失効** | 同じ旧版の保存/DDL/Lease/Tool操作を、Source・Grant・ETag・Attempt変更後に要求 | 誤った確定0、stale拒否の理由が説明できる、無関係なread-only継続は阻害しない |
| **RC-02 確定直後ACK喪失** | OwnerへCommitされたか不明な状態を意図的に作り、権限ある別Readで現状態を確認 | `confirmed-done / confirmed-not-done / unknown`を分離。独立観測不能なら自動非冪等再試行0 |
| **RC-03 Partial delivery** | 一部Tool Reply、文書、固定イベントだけを受領 | 全件/有効0件/部分/permission-deniedを区別し、指定Consumerの仕事の達成を偽装しない |
| **RC-04 Optional不在** | Optional Cloud/AI/高度Targetなしで基本User Jobを行う | 根拠のない全体停止0。操作回数・時間・誤停止を測る |
| **RC-05 同bytesの復帰** | 版A→B→A、同digest別所在/主体に置換 | Source/Identity/Review/現在Grant/業務結果をdigest一致だけで復権しない |

**実施単位**：TEI [#2892](https://github.com/hat47x/tei-platform/issues/2892)のMigration、SUI [#3399](https://github.com/hat47x/sui-sensemaking/issues/3399)の2 Client、SHO [#20](https://github.com/hat47x/sho-composer/issues/20)のVault、EKI [#77](https://github.com/hat47x/eki-fabric/issues/77)のLease、TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)のTool Replyのうち、実入口が存在するものから選ぶ。各Caseの実Expectedと原Observedは別担当で記録。旧PR局所CI・模擬結果を本CaseのPASSに算入しない。全Caseの同時実装も求めない。

**状態**：試験計画のみ。RC-01〜05の実注入、B0/B1/B2の費用・品質計測、実Provider/OS/外部Harness再実行、Owner受理は **NOT RUN**。


## 15. 2026-11-08：KON独立化の必要性を二Consumerで反証する

[横断監査 §25](../docs/yi-constellation/product-value-scope-audit-2026-11-04.md)の **VA-KON-01** を既存B0/B1/B2評価へ接続。B0＝SUI既存Store＋手動SHO参照、B1＝薄いSource/Revision Adapter、B2＝KON独立Store/Service候補。**B2は現行実装・配備を意味しない**。

同一Raw一件のCanvas A/Bで異なる仮説と位置を許し、SHO Readerが原Sourceを引用できるかを試す。独立ExpectedはRaw identityとView identityの非同一、同名別Source／同byte別所在／A→B→A、現在Audienceによる存在非開示、SUI仮説とTEI Accepted Meaningの非同一、ACK喪失・Partialの正しい判定（§14 RC-02/03を再利用）。測定は共有Identity/Revisionの不一致、誤同定・秘密露出、Consumer復帰、手作業・運用コストを別列にする。

**採用停止線**：B0/B1の実User Jobで満たせない複数Consumer需要とB2の測定可能な改善が示されるまで、KON独立Service/中央DB/独自認可Engineを初回必須にしない。KONの長期汎用マルチテナント構想は維持する。SUI #3399/#3400/#3401、SHO #20、TEI #2586/#3419のOwnerと正本を変更しない。実SUI→SHO連携、B0/B1/B2比較、KON Store/Service、Owner受理は **NOT RUN**。
