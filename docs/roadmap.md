# 初期PoCの作業順序

状態: **Proposed（Owner受理待ち）**。直近の計画案であり、導入済み機能やコミット済みの実行結果を示さない。

## Phase 0 — 利用者の課題と検証条件を定める

- 対象を[SCN-001](../scenarios/SCN-001-shared-space-guidance.md)に限定する。
- [評価条件](../evaluations/SCN-001-acceptance.md)を先に定め、既存の基盤の[現在地](../integrations/capability-inventory.md)と照合する。
- **出口**: 入力の矛盾、成果物、反例、判断権限が記述できていること。実用・実装済みとは評価しない。

## Phase 1 — 手動の一巡（次の最小実証）

- 合成walkthroughの参照実装を追加した。T0/T1/T2の参照関係とP/Nの機械検査可能部分を確認するが、**人間の手動一巡や受入合格ではない**。
- 架空の観測O-01〜O-05から、仮説、暫定文書案、更新候補までを作る。
- 元の観測、仮説、未決、文書版の対応をMarkdownと手動記録で再構成する。
- O-06を追加し、A→B→Aや取得失敗時に何が保持されるか試す。
- **出口**: P-01〜P-05およびN-01〜N-04/N-06の結果が対象版とともに記録されること。

## Phase 2 — 既存の実機能を一つ接続

- 読み取り専用の実接続を一つ選び、既存コマンド／MCPの入力・出力、版・権限を確認する。
- MMI MCPの`inspect`を呼ぶ参照接続を追加した。stdin/stdout、`initialize`、ワークスペース外の拒否、原本digest不変を確認するが、実運用の認可・版固定は未確認。
- 手動一巡に対して何が改善したか、反例はどう変わるかを測定する。
- **出口**: 実接続の再現手順と負例が残ること。各基盤の契約を無断で拡張しない。

## Phase 3 — 主体の規模と実行形態を比較

**次の評価対象**: [人とAIの協働統治に向けた開発の焦点](ai-human-cogovernance-development-plan.md)と[P-06比較プロトコル](../evaluations/P-06-cogovernance-protocol.md)で、個人・組織・社会の違いを、Markdown等による手作業との対照で観測する。具体的な試行は[Issue #127](https://github.com/hat47x/tai-pleroma/issues/127)で追跡する。現時点では**全ケースNOT RUN**であり、R-01〜R-07の実物確認や公開権限を代替しない。

- 個人／組織／社会へ適用する際の、情報公開、承認主体、参加条件の違いを比較する。
- EKIの委任、TEIのモデル生成、SHOの文書編集を必要性が確認できた範囲で試す。
- **出口**: 一つの知的機能としての価値と、個々の基盤へ戻すべき仕事を区別できること。

## 判断を求める事項

1. 初回の対象例を「共同利用スペースの案内改善」としてよいか。
2. Phase 1の開発評価者は[2026-10-29のOwner判断](../evaluations/SCN-001-owner-decision-2026-10-29.md)により**現段階では生成AI**。合成文書によるdevelopment reviewと、後工程の実物・人間レビューを分ける。**公開承認・Authority検証・人間レビューは未完了**であり、案内文の実業務上の意味受理・公開は別途判断する。
3. Phase 2ではどの既存機能を選び、現在の動作と版をどの環境で確かめるか。

実装言語、専用Host、独自AIハーネス、統一データベース、新規Contractの採否は保留する。

## 横断計画（2026-10-30：Draft・本ロードマップのPhase 0〜3を置換しない）

[TAIシリーズの能力増幅・縮退適性と横断実証計画](harness-capability-lifecycle-2026-10.md) を別レーンで提案する。これは [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) のHarness-first構成と、[#165](https://github.com/hat47x/tai-pleroma/issues/165) 企業/未知業務、[#166](https://github.com/hat47x/tai-pleroma/issues/166) 生活の買い物、[#167](https://github.com/hat47x/tai-pleroma/issues/167) Personal Agencyを同一評価方法で比較するための計画であり、SCN-001の既存受理Gateや公開条件を変更しない。

- **接続だけで合格にしない**：既存ハーネス単体と、SEI/TEI/SHO等の最小機能を追加した場合の成果・信頼性・確認負担・運用コストを測る。
- **最小実行例を先行**：同じ意味の本文が戻ってもSourceの版・scopeが変わるA→B→A'のSEI判断再開を、外部ハーネス間で行い、現実の権限へ昇格しないことを検査する。
- **縮退も成果**：最新版の外部ハーネス単体で等価にできるならTAI独自処理を薄くする/廃止する処遇を選べる。共通HostやAgent Runtimeの新設は必須ではない。
- **進捗の区別（2026-11-01更新）**：SW-01 S1では同一OpenCode/GLM LatestのAレーン計3回と既存CLIのB構造検査が**限定合成実測済み**。Aは3回とも旧受理の自動転用を回避したが、Bとの条件は同一でなく、「検証器の追加価値」「別ハーネスでの再現」は未実証。EKIでは別の合成fixtureによりRA-2 Result Acceptanceと一部資源制限が実測済み。ただしTEIのloopback Task SubmitとEKI AcceptedResultは**同一Taskの通し証拠ではない**。SCN-004/005、本番業務効果、実ユーザーQoL、実発注/予約の受入は **NOT RUN**。
- **次の最小比較**：[SW-01評価票](../evaluations/SW-01-harness-handoff-qualification.md)のA2（原Basis情報のみ）とB1（同一次情報＋独立検証器）、currentTargetの実原典同定を優先。実利用可能な別ハーネスが現れたときD1を追加し、導入負担・確認負担も同時に比較する。新しい中央正本/Host/Gateは追加しない。
- **時点と同一案件の追跡（2026-11-01検討追加）**：[横断計画§16](harness-capability-lifecycle-2026-10.md)で、選択時点固定と実行時点条件解決を別の業務意味として扱う。TEI↔EKIの同一Task Submit→Attempt→Claim→AcceptedResultと、実成果物・業務Effectを独立に照合する既存P1-JE-1へ参照をつなぐ。部署間/人とAIの委任/再開でも「受付」「停止」「成果物を受け取った」「業務が完了した」を区別。TAI専用実行器・再試行権限・第二証拠正本は増やさない。新規通し試験はNOT RUN。
- **注意負担と未確認の保持（2026-11-01追補）**：[横断計画§17](harness-capability-lifecycle-2026-10.md)と[SW-01 S3/S5](../evaluations/SW-01-harness-handoff-qualification.md)では、通常優先度の未確認を通知しない場合も、その用途・鮮度不足・原記録への参照を引継ぎ可能にする対照を提案。通知件数0を確認事項0としない。既存SEI #660/#677/#678の正本・評価を再利用し、TAIに新通知基盤を作らない。Q-N/Q-P/Q-Cと別Harness引継ぎは未実施。
- **開示と再現・現行適用（2026-11-01追補）**：[横断計画§18](harness-capability-lifecycle-2026-10.md)で、TAI #28のmerged #163によるSUI局所保存再検証、SUI #3330/#3331/#3337の非レビュー構造非開示・実露出監査・歴史的Proposal判断、EKI #382のHTTP→ResultClaim process testと#366の子孫資源監視を、各々の限定実証として取り込む。非開示集合を「0件」、保存したbytes一致を現行正本の真正性、別TaskのAcceptanceを同一業務完了と呼ばない。SUI DocumentのTEI意味モデルがvalidでも、record/stringの実生成とConsumer適合は別に確認する。**TEI #2488は2026-11-01にClosed、PR #2489はMerged**だが、局所spikeを全Generator/実Consumerの合格とはしない（[整合性監査 #425](https://github.com/hat47x/tai-pleroma/issues/425) F2-01）。追加のVIEW/HISTORY/RECEIPT/ENVは計画・未実行。既存SW-01 A2/B1を先行。
- **機密RawのOS/Host境界（2026-11-01追補）**：[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)、[横断計画§19](harness-capability-lifecycle-2026-10.md)、[SW-01 S3/S5追加試験](../evaluations/SW-01-harness-handoff-qualification.md)。SEI/SUI等のSourceは用途に応じ管理境界内へ保持し、別Product/外部Harnessへはサーバ側で許可した最小Projectionのみ。機密Profileでは別OS Identity/ACL/Process/IPC/Network/Secret等でRawの直接読取り・外向き送出を実拒否する。EKIの資源制限と機密隔離は別。最初のC0アクセス棚卸し→合成Rawのread-only正例・直接読取り/egress負例→Linux/Windows実Profile比較を検討。新中央Host/認可正本なし、実隔離試験NOT RUN。SW-01 A2/B1の入力条件は許可済みProjectionでそろえる。
- **大量AI並列開発によるスコープ拡張（2026-11-01）**：[TAI #233](https://github.com/hat47x/tai-pleroma/issues/233)／[横断計画§20](harness-capability-lifecycle-2026-10.md)へ、TEI #2493の広範な業務・Plugin・Target Pressure、#2495のデータ構造/数学・単位・トポロジーの多facet分類、SEI組織文脈、SUI開示投影、SHO一体文書、EKI実委任を横断接続する。候補/Issue/製品領域の固定上限を置かず、逐次対並列Agent・共通Contract競合・機密OS隔離・別Harness/料金の4件ベースの独立対照を提案。探索候補と実証済み実能力、CI/Owner・統合負荷を別計測し、低価格トークンを実Owner意味受理や実Host権限に昇格させない。TAI #232で型名/Schema/件数等メタデータの機密性も評価。初回P-A〜P-Eと実利用料金の試験は未実施。従来SW-01 A2/B1の比較は独立に継続し、スコープ縮小のための固定上限は導入しない。
- **機密下でのClaim十分性とConsumer比較（2026-11-02）**：[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)、[横断計画§21](harness-capability-lifecycle-2026-10.md)、[SW-01 C1〜5](../evaluations/SW-01-harness-handoff-qualification.md)。同じ公開Projectionで内部世界が異なり全件Claimが相違する二世界の反例により、外部AIへ隠れた情報を想像で補わせない。Ownerの開示Policyが許す場合に限りSource側で限定Questionを検査して、許可した結果だけ返す候補を評価（**boolean結果自体も秘匿対象**）。TEI #2516 CC-01〜06、SEI #767、TAI #234/TEI #2515のSession Event/Team送出へ参照接続。通常TEI内の組織Dataを機密Profile一律対象にしない。C1/C3をSW-01 A2/B1へ最小追加、反復照会/実OS/Network/異Harnessは別資格。評価案・新規NOT RUN。**TAI PR #169は2026-11-02にMerged**（従前の「Draftでmainと乖離」は過去時点の記録）。残る評価票／情報保護／ポートフォリオの実証は最新mainを基準にレビューし、merge事実だけからOwner価値受理・実Harness適合を宣言しない（[整合性監査 #425](https://github.com/hat47x/tai-pleroma/issues/425) F1-03）。

### 2026-11-07 更新：初回Tool到達は観測済み、次は比較資格の確立

[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)／[TEI main収録Evidence #3113](https://github.com/hat47x/tei-platform/tree/main/plan/evidence/DSH_H2_TOOL_ONLY_READ_ONLY_2026-11-07)で、DSH外部AI Harnessから固定TEI Binaryを実起動した限定Observedが成立。以前の計画中「最初の外部H2 Tool Callが未実施」という記述は**以前の状態**。探索9試行中の完了3（Participant Task1）、実TEI起動32は技術的接続の証拠だが、参加者が許されないWorktreeを読めたため**隔離・比較資格は不合格／未証明**。独立Answer採点・H3 Loader・Egress／費用は未実施。探索9件を固定4Sessionへ流用しない。

**改訂した次の出口**：①実OS/Harness隔離でReviewer Expected/Skill/旧Log/許可外Sourceの到達拒否を確認→②固定Task/Binary/Workspace/Model/Profile/Cost/独立Expectedの新Trial Groupを開始前にPin→③**比較適格なH2を1Session**で実Tool/Answer/独立採点→④H3実Skill Load→⑤固定のH2→H3→H3→H2四Sessionで増分価値/ITT/PPを比較。技術的接続の繰返しより価値比較可能性を優先する。[VA-02 §13](../evaluations/VA-02-cross-product-first-run-protocol.md)と[VA-04 §8](../evaluations/VA-04-evidence-readiness-preflight.md)が実験条件。

**実行開始前の新たな確認**：[Runbook §24.3](https://github.com/hat47x/tai-pleroma/blob/docs/yi-harness-skills-20261102/docs/yi-constellation/first-real-skill-qualification-runbook-2026-11-02.md)の実保存Tool結果ではCatalogが8,192 bytesで途中切断、stdout JSONとPowerShell stderrの混在、56 Call/55 Result、探索Toolと正式Whitelistの差が判明。次のH2は隔離に加え、対象Subjectの限定inspect/validateの実stdoutとHarness受領・Tool IDを突合する。全Catalog完全性を初回Taskの必須条件とはせず、利用できた範囲・未知を明示。[VA-02 §13.1](../evaluations/VA-02-cross-product-first-run-protocol.md)／[VA-04 §8.1](../evaluations/VA-04-evidence-readiness-preflight.md)を参照。実Tool到達の証拠は[TEI main](https://github.com/hat47x/tei-platform/tree/main/plan/evidence/DSH_H2_TOOL_ONLY_READ_ONLY_2026-11-07)に収録されているが、正式比較H2はなお0/4。新Tool Proxy/中央Result Storeは不要。

**条件付き後続**：[TAI #514](https://github.com/hat47x/tai-pleroma/issues/514)のOKF Attested Computation（正規計算定義／型付きBind／実Receipt／独立Attester）は既存Skill試験の後にread-only計算1件で価値を判断し、H2/H3のSkill原文/Tool Profileに途中追加しない。SEI #820のOKF鮮度・交換とTEI #2605のProduct Skill契約を流用。新Attester Runtimeや第二Meaning Storeを最初から標準装備しない。


### 2026-11-07 最新Gate：H3実Load成立、比較入場G0/G1/G2は未達

[TEI mainの実DSH四Session](https://github.com/hat47x/tei-platform/blob/main/plan/evidence/DSH_H2_H3_FOUR_SESSION_2026-11-07/README.md)により、H3-A/Bで**固定Product Skill root 5,482 bytesと参照文書1件の実Tool読込を確認**。H2側Skill Toolは0。外部Tool接続とH3 Loaderは限定実証済みで、以前の「H3 Loader NOT RUN」は履歴状態。ただし過去Session再利用・Workspace path差・読取非隔離・Whitelist逸脱・独立採点不足により、**比較適格H2/H3は0/4**。

次のBlocking Exitは新機構実装ではなく既存[Runbook §24.4〜24.7](https://github.com/hat47x/tai-pleroma/blob/docs/yi-harness-skills-20261102/docs/yi-constellation/first-real-skill-qualification-runbook-2026-11-02.md)の3段階：**G0**同一OS/Tool Profileでpublic Read成功とReviewer/Skill/Raw/親Workspaceの実Read拒否、**G1**Model入力とSession Log等の副次送出・再送・適用Audienceの確認、**G2**許可Command/flags/実Workspace・完全Tool Reply／最終回答の受領。その後、固定Task・Binary・Source・Skill version・モデル条件・独立Expectedで**新4Sessionの事前割付**を行い、正答・Unknown/Warning・費用・手直しを比較する。[VA-02 §13.2](../evaluations/VA-02-cross-product-first-run-protocol.md)／[VA-04 §8.2](../evaluations/VA-04-evidence-readiness-preflight.md)に根拠と負例を集約。

**新たな実リスク**：[TEI H6-E1実測](https://github.com/hat47x/tei-platform/tree/main/plan/evidence/DSH_H6E1_READ_BOUNDARY_2026-11-07)ではread-onlyで合成Raw/.env/cwd外ファイルの拒否0、Model入力＋Session Logへ複製。[H6-E2 Local Mock](https://github.com/hat47x/tei-platform/tree/main/plan/evidence/DSH_SESSION_LOG_RETRY_AND_DEFAULT_2026-11-07)ではSession Log既定ON、503/不完全streamで未受理区間が再送。実Providerへの機密送出や全Network経路の検証ではないが、設定名をOS隔離・送出ゼロの証拠にしない。

**後続の限定採用**：[TAI #531](https://github.com/hat47x/tai-pleroma/issues/531)／[Draft #532](https://github.com/hat47x/tai-pleroma/pull/532)から、Tool完了と利用者Outcome、適切な非実行と誤拒否、Receiptと独立Readを分離した価値採点を[VA-01 §6.6](../evaluations/VA-01-product-value-necessity.md)へ接続。[TAI #489](https://github.com/hat47x/tai-pleroma/pull/489)の表現型/Role/SHO/SUI/SEI Skill連携、OKFの実Attesterは必要なProduct先行実証の後。初回H2/H3固定Task/Profile/Skillに新機能を挿入せず、新中央Host/Policy/Registryを作らない。

## 横断要件の適正化・多モデル独立レビュー（2026-11-04：提案）

[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)および[主要価値からの要件適正化と独立レビュー計画](yi-constellation/product-value-scope-audit-2026-11-04.md)を、Phase 0〜3と並列の**横断レビュー・計画更新レーン**として追加する。

- **目的はIssue数や研究領域を減らすことではない**。各Productの主要価値から必須要件、用途条件付き要件、研究候補、他Product/外部Harnessとの重複を区別し、標準構成・初期受入に不要な義務を積まない。安価なトークンによる広域・並列の探索は維持する。
- **多エージェント運用**：製品別の一次評価（TAI/TEI/SEI/SUI/SHO/EKI）、作成者から独立した反証、Source/Evidence/機密・Authority確認、Integratorによる小差分提案を分ける。モデルの合意は独立証拠でもOwner受理でもない。
- **初回の出口**：各製品の価値→最小体験→重要要件2〜3件の適用条件・負例・代替を照合し、少なくとも高優先2件について独立の反証票を作る。実験未実施はNOT RUN。Product固有変更は既存Issue/ADRのOwnerへ、Draft PRで提案する。
- **守る境界**：意味・出典・版・実行認可・機密と実効果の確認を削減対象にしない。新しい中央Host、第二Meaning/Authority正本、全Agent共通Runner/Registryを作らない。単独Productと外部Harnessの価値・費用の対照を用い、必要に応じて詳細だけ遅延読込みする。
- **現在地**：主要価値・Issueの一次Source-static照合と規則案の登録まで。全Issue網羅、2モデル比較、製品の正式な要件再分類、実ユーザー価値・Owner受理はNOT RUN。

### 初回独立反証パケットと価値・安全の両面比較（2026-11-04追加）

[VA-01：製品別8件の最小構成／高度化／負例と共通比較条件](../evaluations/VA-01-product-value-necessity.md)をG0/G1の初回入力として用いる。TEI #1180の**一Scenario→CLI/Webテスト派生**とEKI #58の**分散しない選択＋期限内回復**を優先反証とし、SHO #7のMarkdown L0・SEIの小さなResumeを並列対照する。TEIは専門家向けDSLとGo単一バイナリを別の設計判断として扱い、単一ビルドで足りる限りマルチビルドを義務化しない。

- **同条件のB0/B1/B2**：既存Harness/ファイル/ローカル実行、必要なProduct最小機能、汎用化した高度実装を比較し、利用価値・維持費・復旧・認可を別計測。高度化しないと安全/意味が壊れる負例と、加えても価値が増さない反例を両方保存する。
- **Issue更新の正確性**：EKI #381は11/4取得時点Closed。修正済み個別Issueの状態と、実EKI Jobの期限内完了・独立結果受理・外部業務EffectのE2E実証を同一視しない。
- **レビュー状態**：VA-01はSource-staticで作ったテスト候補。実モデル割当・Holdout・テスト実行・製品受理・利用者価値評価はNOT RUN。新しい中央Agent Host/Tester/第二SSOTは追加しない。


### 入力閉包と契約発見の実証前確認（2026-11-04追補）

[VA-00監査台帳 TAI #424](https://github.com/hat47x/tai-pleroma/issues/424)の9 Laneの文書整合性照合とF2のOwner判断59件を受け、[VA-04](../evaluations/VA-04-evidence-readiness-preflight.md)を[VA-02](../evaluations/VA-02-cross-product-first-run-protocol.md)のP0/P1前提に接続する。既存Phase 0〜3・各Productの採否は変更しない。

- **最優先の反証**：TEI #2822/#2823/#2824で確認された「validate okでも利用者Source未読込」「managed file≠Parser実消費」「CLI discovery≠安定版付きJSON」を、実Source/CLI/Scenario/Expectedの別証拠に分けて検証する。Source不足でも安全なCandidate探索は妨げず、完全な検証成功を名乗らない。
- **EKIの契約追随**：EKI #698の3値実装と4値ADR案の不整合をOwner待ちとして扱い、VA-E1はSuitabilityの非分散判断・Admission/Policy拒否・期限内回復を別々に記録する。
- **監査結果の扱い**：#424 S4完了はSource-static。実テスト、複数モデルの独立実証、Owner受理、製品E2Eは未実施。#424の担当Laneや各OwnerのIssueを二重化しない。
- **拡張研究**：EKI低レイテンシ/マルチモーダルのTransport選択は研究候補として残し、最小委任MVPへの先行義務にはしない。

### 用途相対の高度化と最新Source状態の再確認（2026-11-04）

[VA-COND-01：用途条件付き能力・Source状態ドリフト](../evaluations/VA-COND-01-conditional-capabilities-and-source-drift.md)を、VA-01/VA-02の補助評価票として追加。EKIのProduct Valueにある四つの外面（バッチ資源最適化／AIツール委任／隔離実行／軽量常駐認知）を、一律の長時間バッチ要件に縮めない。**低遅延・ストリーミング・マルチモーダルなData Planeは、仕事のデータ様式・応答期限・jitter・損失・開示資格が要求するときに検証する条件付き能力**であり、初回2 Worker E2Eにあらゆる通信方式を必須としない。認可、Local Governor、Task/Attempt、Results/Consumerは省略しない。

- **VA-00監査からの差分**：[TAI #424](https://github.com/hat47x/tai-pleroma/issues/424)の文書整合性9 Lane・別ContextによるS4監査を参照。F2のOwner判断待ちを価値レビューの受入と誤認しない。同一モデルの別Contextであり異モデル独立性は未達。
- **現状**：VA-COND-01はSource-staticの設計と反証候補のみ。EKIの実Latency/SLO、Media配信、TEI実Web、異モデル反証、Owner採否はNOT RUN。正式なTransport/Codec・新Agent Runner/中央Registryは採用しない。
- **次の小さな検証の固定（2026-11-04、[VA-02 §8](../evaluations/VA-02-cross-product-first-run-protocol.md)・[VA-04 §6](../evaluations/VA-04-evidence-readiness-preflight.md)）**：TEI #2828のJSON候補追加を既存Driver Scenario/CLIで限定試験し、独立Expected・Known Mutantを含む判別力を測る。並行してTEI #2819の宣言D1と実Build入力D2の相違を、当該SelectorのFail-closed必要条件として#2595に戻す。TAI H2/H3はDraft #270の既存4 Session比較を使い、実Skill Load/Task正答/費用を試験するまで増分価値を未確認とする。各実験は独立に進め、実CLI/実Builder/実Harnessを横断PRの新Runtimeへまとめない。今回の新規実験・異モデル反証はNOT RUN。
- **11月5日版の価値優先実証（[横断計画§16](yi-constellation/product-value-scope-audit-2026-11-04.md)、[VA-02 §9](../evaluations/VA-02-cross-product-first-run-protocol.md)）**：TEIはA/VA-T2-R（公開Source→実CLIのread-only照合）とB/VA-T2-W（Function→Command→実PG Commit/Receipt/独立Reader）を別のB0/B1/B2比較にする。Studio/SHO編集C、TEI Self-build Dは用途別・内部成熟度の並行レーンであり、A/Bの一律必須条件にしない。実PGの限定前進（TEI merged #2853）とABA別Key再適用（#2854）を相殺せず、Commit不明・OperationID・現在Grant・必要GuardをBに残す。DB Expand/Backfill/Validate/Cutover/Contract、Plugin Bundleの選択依存、AI提案/実行境界は既存#2555/#1251/#267/#1174のOwnerが用途ごとに検証し、新中央Host/Registryや全方式同時完成は要件化しない。VA-X/VA-Eの実試験、異モデル独立反証、Owner受理はNOT RUN。
- **変更時の再資格化と停止範囲（11月5日夜の照合、[横断計画§17](yi-constellation/product-value-scope-audit-2026-11-04.md)・[VA-02 §10](../evaluations/VA-02-cross-product-first-run-protocol.md)）**：候補の追加・実選択変更・現在Authority変更・再起動/移行境界を別の失効原因として評価する。最初の一件は実TEI 1 SubjectのTool-only対実Skill Load四Sessionであり、第2Harness/実旧新DB/全GUIは先行条件にしない。後続はTEI #2870の再起動Unknown消失＋#2854の新Key ABA、#1251の未使用Plugin非干渉と選択nested依存閉包、#2555の現在read/write OwnerとCDC水位、SHO #7の固定Parser/無音fallback禁止を各Ownerで限定検証。RunPlan事前PASS、Static Skill/CLI成功、Migration差分0、L0索引値一致は現在Effect/納品/Owner受理を代替しない。新中央Registry/Runner/二重Oracle正本は作らず、既存評価票だけ追加。今回の横断実試験・異モデル採点はNOT RUN。
- **2026-11-06 Authoringと価値実験の再資格化**：[他チャットで示された`*.tei`原則廃止→`*.tei.md`寄せる方向](https://github.com/hat47x/tei-platform/issues/2621)は、Owner方針と現在Issue末尾の旧案（`.tei.md`非標準化）が食い違うため、TEI #2621/#988/#1440へ**文書・Parser・CLI・旧Source移行の契約照合**を戻す。`*.tei.md`という意図表示はMeaning受理・Host Grantではなく、既存`*.tei`の自動一括変換/Reader対応を実装済みとしない。[横断計画§18](yi-constellation/product-value-scope-audit-2026-11-04.md)／[VA-02 §11](../evaluations/VA-02-cross-product-first-run-protocol.md)へ負例を追加。実証の次の出口はTAI #168の**外部Harness H2 Tool実Invoke1 Session**で、固定TaskのH2/H3四SessionはR割付とD実提供を別採点、失敗を落とさずITT/PPを分ける。既存TEI S1/Prebuilt GoなしCIと、SHO Draft #17固定HEAD 16/16候補Reader CIは局所既存証拠として扱い、実H3/SHO正式Grammar/Owner採用へ昇格しない。新Runner/Registry/第二Oracleなし。
- **2026-11-06 後半・価値と移行の着手順**：[製品価値監査§19](yi-constellation/product-value-scope-audit-2026-11-04.md)／[VA-01 §6](../evaluations/VA-01-product-value-necessity.md)で、能力H2/H3と実際のActivity再開SCN-001を別評価にした。実H2 Tool呼出し1Session→H3実Load→同Task4Sessionを先行し、その後SCN-001のB0手動/B1単独Product/B2 TAI追加価値を独立Expected・原文/反証/保留/保存後再読取・時間/人手/Token・再確認費用で比較。TAI #271 SC-15の選択外反証とHost非開示は正しさ/費用を相殺しない。TEI `*.tei.md`移行は[#3030](https://github.com/hat47x/tei-platform/pull/3030)のM0〜M6に照らして現Loader/Parser/Source選択から実証し、旧`*.tei`をRenameだけで除去しない。SHO G1b Readerの入力安全性の残余は[SHO #16](https://github.com/hat47x/sho-composer/issues/16)に返し、TEI初回H2の先行条件にしない。共通Engine/Registryを追加せず、Productの実証とTAIの価値比較を別のOwnerで維持。
- **2026-11-07 実証優先順の維持と資格更新**：[横断計画§19.1/19.2](yi-constellation/product-value-scope-audit-2026-11-04.md)／[VA-04 §7](../evaluations/VA-04-evidence-readiness-preflight.md)で、TEI Draft #3031の`TEI_MD_PARSER_UNBOUND`限定Go CI成功を**新形式の明示拒否**と評価（Parser実対応・Owner受理は未達）。旧新Source移行の仕様・検収主担当は最新のTEI #3030（M0〜M6/TM-01〜14）であり、#2667は横断経緯・引渡し。#3030内のAuthoring表層AU-01〜08は別の合否で扱い、二重計画化しない。TAI #271 SC-17の不正Cursor200先頭回帰/ETag変化と本文付き200、SC-18のPurpose/Audience変更を後続SCN-001のB0/B1/B2価値・選択的再検証へ接続する。現実験の次Exitは#168の外部AI Harness H2実Tool呼出し1 Sessionで固定し、新形式Parser、管理監査API全件/Cache、SHO Writerを一律の先行Gateにはしない。 2026-11-07追補：[VA-02 §12](../evaluations/VA-02-cross-product-first-run-protocol.md)に、TEI main #3042の事前拒否とExecutor後EffectUnknown、#3047の限定GrantAuthorizer、#2514のAI Scenarioによる誤Evaluator検出（Red Mutant Draft #3017は絶対merge禁止）を別資格として記録。[VA-01 §6.4](../evaluations/VA-01-product-value-necessity.md)ではTAI #271 SC-19〜21の「誤完了」と「過剰停止」の双方を後続B0/B1/B2価値試験で計測する。局所CIやHTTP 200は一改訂の実Host/Consumer成果ではなく、初回H2をこれらでブロックしない。


### 2026-11-07 追加：主要価値と必須依存の伝播監査

[横断計画 §21](yi-constellation/product-value-scope-audit-2026-11-04.md)と[VA-01 §7](../evaluations/VA-01-product-value-necessity.md)を既存[#422](https://github.com/hat47x/tai-pleroma/issues/422)の評価列へ追加する。新Product要件は採用せず、6Productごとに「最小利用体験・保持すべき不変条件・任意の高度化・B1不足を証明する反例」を一対で比較する。**探索数の上限は作らないが、他のProductに完成・起動・全件検査を要求する条件は持ち込まない**。

実装/試験の順位は (1) 既存H2/H3のG0実拒否、G1副次送出、G2実Tool受領・Source一致→新規4適格Session、(2) 各Product単独の価値断面（TEI #1127/#1180、SEI #711/#758、SUI ADR-0089/T2、SHO #4/#7、EKI #58）、(3) B1の欠落が独立Expectedで示された用途だけTAI #271、TEI #1223、SEI高度Method、SHO #8、EKI #19/#155/#67等を選択して比較、の順。並行Laneの研究・文書探索を止めるものではない。初回H2/H3に新しい共通Gate/Host/Scenario DBは追加しない。正式比較0/4適格、独立価値比較・異モデル反証・Owner採用は**NOT RUN**。


### 2026-11-07 補正：採用済み方針と初回実装量の分離

[横断計画 §22](yi-constellation/product-value-scope-audit-2026-11-04.md)／[VA-01 §8](../evaluations/VA-01-product-value-necessity.md)で、他Productの直近の限定実測を反映。**TEI Plugin-firstはmerged #3277／RQ-008に明記された製品要求**であり、研究だけの任意構想として扱わない。ただし実装はD0現行境界確認→D1 read-only Inspector一つの実Provider/Consumerから始め、全CLI/Studio/生成RuntimeやHot Swap同時完成を初回Exitにしない。Verified BOMは組合せ利用時の標準的な検証要件を保ちつつ、宣言12／候補Lock9、実Build/Load/Run未実証を分ける。Source Context Query #3262はAIのT1生成に必要なScopeで限定し、全Workspace一括取得を先行Gateにしない。

**既存Product実験の次の一歩**は、TEI T0既存Scenario→#3273の新しい行番号0負例T1、SUI #3397＋SHO #21の別Fixture成功→同一実FileのSHO CLI受領、SHO Reader限定CI→#4 Writer保存・再開、TEI文書要求→単一read-only実Plugin利用の4本。各Laneは独立に進行可能。別Fixture CIの18 PASS/1 SKIP、TEI局所C0相当10.1%/C1未測、旧SHO Reader Draft closed/unmerged、BOM Reference-onlyを製品全体の合格としない。RQ-035のBranch間意味衝突は採用前照合で止め、新Requirement Registryは作らない。TAI #168のG0/G1/G2と4 Session適格0/4、SEI #758、SUI実務T2、EKI #58は元の優先順のまま維持。**今回の新実行・独立価値比較・Owner受理はNOT RUN**。

### 2026-11-07夜：余計な必須性の解消と、必要なEvidenceの充足を別投資とする

[横断レビュー§22.4](yi-constellation/product-value-scope-audit-2026-11-04.md)と[VA-01 §9](../evaluations/VA-01-product-value-necessity.md)に、**Consumer契約の過剰必須性と、テスト/組合せに必要な実根拠の不足は逆方向の不具合**であることを明記。[TAI #533](https://github.com/hat47x/tai-pleroma/issues/533)/[#535](https://github.com/hat47x/tai-pleroma/issues/535)の局所試作では、SUI任意Edge種別をTAI投影側でも任意にすると欠落Edgeを維持できる一方、現行パイロット契約は必須のまま。合成層のIdentity/向き・多重辺・unknownの保持を既存Ownerで別確認し、受理前の一律置換はしない。

**テストは新規Caseを増やす前の不足診断を標準経路に**：TEI main [#3284](https://github.com/hat47x/tei-platform/pull/3284)/[#3299](https://github.com/hat47x/tei-platform/pull/3299)のT0.5/T0.6は実CLI/Source・Plugin Lock更新の負例まで限定CIで観測済みだが、`qualifiedTestGeneration=false`、C0相当10.1%/C1未測定。必要なDesign Context/Meaning/Required Sourceが足りなければ診断・取得を優先する。**既知Ruleの行番号0実走T1-Aは[main #3304](https://github.com/hat47x/tei-platform/pull/3304)の[実CI #42378033965](https://github.com/hat47x/tei-platform/actions/runs/42378033965)で限定達成**。次は正常JSONでも独立Required Ruleが部分欠落するTT-56を検出する[Draft #3326](https://github.com/hat47x/tei-platform/pull/3326)と[並行 #3324](https://github.com/hat47x/tei-platform/pull/3324)の**一方式への統合**。#3326はsubject/indexモード誤りの旧CI失敗を修正し、[専用CI #42385726717](https://github.com/hat47x/tei-platform/actions/runs/42385726717)が成功したが、2つのDraftを合成PASSにしない。一本化した実Source/Rule/Relation→Loader/Parser/Evaluatorの限定到達を経て、**未知RuleのAI盲検発見T1-B**を独立Expectedで試す。

**Verified BOMは実組合せを確認できた行だけ利用可能とする**：[TEI #3267](https://github.com/hat47x/tei-platform/issues/3267)/[Draft #3297](https://github.com/hat47x/tei-platform/pull/3297)のRQ-036は、candidate lock/pairwise/synthetic observed-passを実Provider×Consumer×Target×Artifactと同一Attempt/独立Expectedで`qualified`となる行と分離。mainのRQ-035 Workbenchとは同一視しない。検証済みBOMを標準提供する製品価値は維持するが、未資格の組合せの自動推薦は禁止。

**順序**：TAI #168 G0/G1/G2→新規H2/H3四SessionのBlockingは不変。Edge契約、TEI Design Context/T1、Verified BOMは既存各Product Ownerで並行。新Requirement Registry/中央Test Runner/全Product用BOM Serviceを先に追加しない。実User JobでのVA-MIN比較、TAIパイロット契約改定、盲検T1-B/実Target適格、Owner受理は**NOT RUN**（既知T1-Aの実CLIのみ限定Observed）。

