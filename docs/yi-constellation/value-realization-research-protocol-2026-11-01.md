# YI Constellation：価値の実現と検証をつなぐ研究計画

> **Research / Proposed / Owner未受理 / 利用者調査NOT RUN**（2026-11-01）。この文書は [価値・要望・要件の整理](value-needs-requirements-2026-11-01.md) の研究方法と具体的な実証設計を補う。新しいTAI Core／共通Store／権限エンジン／評価Gateの設計決定ではない。

## 現在の実証基線（2026-11-08 夕方照合。各Productの後続受入を優先）

- **TEI Design Context/T1**：merged #3354の11実CLI Reply／32局所Consumer対照、既知T1-Aの第7 Stepを限定実行済み。merged #3477のmain実CIでWorld同一・Source Index改版による旧Context拒否と、Context→Scenario前後再照合を確認。**AIによる未見Rule発見T1-BはNOT RUN**。Required Scope外はpartial / exploration-only / qualifiedTestGeneration=false。
- **外部Provider Source**：#3479はmain統合済みで、import先Sourceのみ改版しConsumer World/Source Indexが不変となる反例を限定確認。初回同一LoadのProvider実Parser byte/Manifest private witnessはDraft #3524で移植検証中。外部Source全Closure・Product実Read/現在Host Grantは未認定。
- **TEI Self-build**：Reference Driverだけでなく、cmd/tei自身のStage1生成物がStage2 Invokerとなる**L3形状の局所実測**が#3440/#3447にある。Build Intent解決の**L2は未成立**、G4全体UNQUALIFIED。#3476のSupply Verifier/Intent前提はDraftの限定実験、resolved=false。
- **SHO Document**：公開SUI→SHO固定354byte相互運用は別Repo CI限定PASS、真正一File HandoffはSKIP。SHO #25のtest-only Working Copy保存→別Open readbackと元/出力FD同一性・ABAの限定CIはPASS。正式Editor Writer、永続Store CAS、Source真正性とOwner受理は別。
- **YIC Skill/BOM/未来構想**：H2/H3はSkill実Loadを限定観測済みだが比較適格0/4。現mainのRQ-035はWorkbench、**RQ-036は全容Model Map**。BOM Draft #3297のRQ-036は意味衝突しており、Ownerの採番・PAS/Gap Audit整合前にマージできない。SUIの一次価値／高度統合を分離し、Ontology/Decision Twinは後続段階。


- **TEI 1 Function宣言Required**：merged #3482／main push CI #42462861657のbounded Contextは13実CLI Reply、42局所Consumer Controlsを限定PASS。Capability定義・Application uses・Validation/Sourceの独立照合であり、実Call Binding/Provider/Grantはnot-observed。
- **SHO実Cross-Repo Reader**：Draft #27のprivate-owned CI #42462172893で公開TEIのPin済み4 Markdown Fileを実G1b ReaderがRaw byte/限定Linkとして受領。Frontmatter F0/同一Provider二Consumer K2/SUI Producer H1/G2 Writerは未検証。

- **EKI低層Transport**：#787の試験用Unix socketで6イベントを実送受信し4負例/race5回を局所PASS。ただし同一Goプロセス内goroutine・JSON compact比較であり、実Local IPC/Connect Adapter／別Worker／Lease Grant／原Wire byteの同一性は未検証。#786の実Adapter Trace比較は未入力SKIP。
- **TEI共通API／SEI記録**：TEI main #3458はvalidate一操作のCLI/MCP共通Reportを実装済み、他3 Toolの意味同値や外部Harness受領は未資格。SEI CLIはRecommendation/DecisionのAddとResumeのみを正式な保存入口とし、Question未決やMethod Applicationの書込・TEI Source真正性は未証明。

- **最新Requirement衝突（要対応）**：mainのRQ-036は全容Model Map／Diagram（merged #3505）。未マージBOM Draft #3297もRQ-036を別意味に再利用している。BOM IDはOwnerが再採番するまで現行採用IDとして扱わず、当該Draftをそのまま統合しない。実Host #3516の7合成Adapter Cases、SQL #3500合成Connector、AI Tuning #3520の19合成対照は各局所限定であり、実Provider/Client/本番Outcomeではない。

- **Plugin-first Inspector**：TEI #3381はmain統合済み。既存Compositionでselected BをHost登録Go実装へ束縛し、CLI注入HelperとStudio Host APIの6対象×2経路を限定Go試験。通常CLI dispatchと実Wails StudioBridgeの製品S2配線は未実装。#3531はstatus/master planへ差分を反映。
- **実Provider／性能統計**：TEI #3500 DraftはNative Browse Pattern→Postgres Executor→instrumented SQL Connector→MapperのGo試験成功、実Postgres opt-inはSKIP。main #3520はAI Tuning合成19対照成功、実Provider計測・Latency/Cost/CVR改善は未実施。main #3516のHTTP合成Adapter7ケースも実DB Effectではない。
- **配信・KONの非強制性**：完全Headless/B2C独自Frontend、静的Site、SHO、KON Dataspaceは任意に採用する別Consumer/Provider。#3528/#3512は設計Draft、実公開・KON API・CVR改善・第三者の受領は未実証。

---
## 1. 研究で問い直す対象

YI Constellationの目標は、六製品の機能の総和を大きくすることよりも、**主体が実際に選べること、考えられること、実現できること、関係を育てられることを広げる**ことにある。成果の数だけでなく、成果に至る理由、断った選択肢、途中で変えた希望、利用していない人への影響を含めて評価する。

### 1.1 五つの異なる概念を接続する

| 概念 | 問うこと | 例 | 取り違え |
| --- | --- | --- | --- |
| **価値（Value）** | なぜそれが望ましいか。誰にとって、いつ、どの範囲か | 自分で創作を進めること／誰かの負担を押し付けずに協働すること | プロダクトの機能一覧を価値と呼ぶ |
| **要望（Wish / Need）** | どの状況の誰が何を望むか。表明・推測・利害の差は何か | 「創作時間を保ちながら締切も守りたい」 | AIの推定を本人の意思とする |
| **実質的な選択肢（Capability）** | 利用者がその行為を選ぼうと思えば実際にできるか | 自分で書く／AIに下調べを任せる／延期する／何もしない | ボタンがあるだけで選択可能とする |
| **要件・実現手段（Requirement / Means）** | その選択を可能にする振る舞い・制約は何か | 再開点、時間予算、既存ツール接続、許可範囲 | 必要な価値を一つの新Coreへ直結する |
| **結果・学習（Outcome / Learning）** | 実際に何が起き、本人や影響者はどう評価し、次に何を変えるか | 再開できた、納得して延期した、誤発注を回避した | Tool SUCCESSやTask terminalをQoL向上とする |

これは調査・レビュー用の**区別**であり、全製品が共通スキーマを保存する必須条件ではない。Capability（実質的な選択可能性）はTEI等のソフトウェアCapability名と語義が異なるため、文脈を明記する。

### 1.2 規模の違いは「主体の数」だけではない

| 規模 | 目的・権限が現れる場所 | 価値の観測 | 典型的な失敗 |
| --- | --- | --- | --- |
| 個人 | 本人の期間限定の意図、共同生活者の別の許諾 | 選択肢、着手・再開、納得、創作/休息の余白 | 一時の推測を恒久嗜好に固定 |
| 組織 | 担当、兼務、代理、部署、会社、契約先の異なる権限 | 業務意味の保持、正しい対象・効果、手戻りと部門間の負担 | 全社最適の名で少数部署へ負担転嫁 |
| 社会 | 異論を含む参加者、影響を受ける人、正当な決定主体、公開条件 | 発言可能性、変更できる規則、説明・異議申立て、受益/負担 | 一部の意見を全体の総意として発表 |

個人・組織・社会を「同じ巨大Agentの別スケール」と決めつけない。共通するのは、**主体・目的・関係・条件・時間・結果・再評価という問いの立て方**。主体を認識できることと、その主体の代わりに実行できることは別。

## 2. 価値の緊張を、探究を豊かにする対として扱う

評価対象は一律の最適化値ではなく、**価値の緊張がどの条件でどう変わるか**。正負両方の仮説を保持する。

| 緊張と問い | 最小の実験 | 観測する差／不可侵の境界 | 既存の接続先 |
| --- | --- | --- | --- |
| **自律性 ⇄ 先回り支援**：AIに多く任せた方が自由が増えるのか、選択感が減るのか | 同じ創作課題を①モデル主導修正②本人の考えを引き出す協働で比較 | 成果の質、案の多様性、本人の所有感、確認/操作負荷 | [TAI #167](https://github.com/hat47x/tai-pleroma/issues/167)、SUI/SEI |
| **探索の開放 ⇄ 外部作用の確かさ**：自由な仮説生成から安全に行為へ移れるか | 未定型の状況で案を広く生成し、作用前に必要なAuthorityだけ照合 | 探索で残った少数案、未許可の実作用0、過剰な停止 | [TAI #165](https://github.com/hat47x/tai-pleroma/issues/165)、SUI/CSW・TEI/EKI |
| **継続 ⇄ 更新・撤回**：過去の理由を保ちつつ、現行の意思を守れるか | Source A→B→A'、本人の意図を変更/撤回、別Harnessで再開 | 旧判断の無断復活0、必要な再開理由、不要な問い合わせ | [TAI #33](https://github.com/hat47x/tai-pleroma/issues/33)、[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) |
| **効率 ⇄ 相互性**：ある主体の成功が他者の負担を増やしていないか | 3主体の合成共同作業。提供者/受益者/負担者の分布を変更 | 便益を得る人とコストを負う人、異議・調整機会 | [EKI #392](https://github.com/hat47x/eki-fabric/issues/392)、TAI評価 |
| **自律的な行動 ⇄ 節度と余白**：処理しない選択は価値を保てるか | 予算・休息制約下で通知・代行・下書き・停止を比較 | 本人が選んだ活動の維持、不要な介入、停止の実効、再開 | [TAI #167](https://github.com/hat47x/tai-pleroma/issues/167)、[EKI #393](https://github.com/hat47x/eki-fabric/issues/393) |
| **局所自治 ⇄ 共同調整**：誰の同意で何が変わるか | 家庭の共同購入／部署間移管／公開議論を同じ語彙で比較 | 局所許諾の越境0、適切な参加・異議処理、未決の保持 | TEI組織モデル、[TAI #127](https://github.com/hat47x/tai-pleroma/issues/127) |
| **同一モデル ⇄ 多様な実現**：表現の統一は環境の多様性に耐えるか | 同じ業務意味を異なるTarget/Hostに投影し、負例を注入 | 値域/時点/集合完全性/丸め/実Effectを独立照合 | TEI意味モデル、[TAI #165](https://github.com/hat47x/tai-pleroma/issues/165) |

**研究上の原則**：SUI/CSWによる生成的探索は、分岐・仮説の豊かさを育てる工程として扱う。反証・採否・Owner受理は**後段の別工程**とする。外部作用の境界には用途に必要な検査を置くが、探索そのものの停止条件を先回りして増やさない。CSWの利用は探索Methodの候補であり、YIの正式第七製品への自動分類ではない。

## 3. 価値を具体化する、三つの対照研究

### CASE-V01 個人：創作、副業、休息を両立する

- **目的**：創作を自分の意図で進め、期限付き作業も処理し、休息の余地を保つ。
- **事前状態**：本人が合成で表明した「創作1時間・副業締切・通知少なめ・休む自由」。AIによる未確認の内的状態推定は利用しない。
- **介入**：A=既存予定表とHarness単体、B=Harness＋SEIの期間/根拠付き再開、C=B＋必要時のみSHO/SUIの構造化メモ。別Harness再開条件Dも既存#168へ接続。
- **変化**：締切が前倒し、過去の「常に午後は制作」が今回は不適切、本人が休息を選ぶ。
- **正例**：制作・延期・休息のいずれも選択可能であり、本人の判断と理由を適切に保持。準備作業だけを安全に代行し、必要時に短い確認で再開。
- **失敗例**：提案数や完了率を稼ぐため休息を侵食／前回の未確認推定を本人の固定選好として利用／提示しただけで本人が実行したと報告。
- **測定**：選択肢の実現可能性、本人の所有感、成果満足度、創造的多様性、確認/通知回数、実作業時間、再開損失、不要な情報保存。合成ケースは動作検査であり、QoL実改善は実利用者評価が必要。
- **先行試験**：read-only/prepareのみ。購入・外部連絡はこのケースでは行わない。

### CASE-V02 組織：未知課題と既知の重大脆弱性への対応

- **目的**：脆弱性対応の構成差分を素早く把握しつつ、未知の事象では仮説を保持して安全な準備を継続する。
- **事前状態**：3資産（影響あり・影響なし・不明）、担当の兼務/代理、修正候補と合成権限。
- **介入**：A=既存Issue/CI+Harness、B=A+TEIで業務意味/実現差分のモデル照合、C=B+SEI/SHOで根拠と未決を長期追跡。効果が変わらなければ導入数を減らす。
- **変化**：新しい脆弱性情報、異なる保守窓、代理者の任期終了、部分取得Rが要求対象Lを満たさない。
- **正例**：候補パッチ/テスト/RCまでAI主導で進み、実本番更新は有効権限に留保。局所的に確かな作業を続け、保留箇所と独立Effect照合を明示。
- **失敗例**：`checkAll(R)`だけでLの全件確認扱い／承認済み役割を現在権限と同一視／テストPASSを本番効果へ昇格／全部を保留し安全な準備さえ停止。
- **測定**：対象完全性、検出した不明点、無断作用、修復候補の適合、CI時間と人の確認、他部署へ移した負担、RC品質。Ownerの業務意味/本番受理は別。
- **実装方針**：他チャットで方向づけられた**AI-first / Headless-first / GUI-later**を適用する場合、TEIのモデル/構成/プラグインの机上評価→AI向けCLI/typed operationsで最小一巡→GUIはその動作と差分を検証して構築。これはTEI側設計の接続であって、YI全製品のGUI廃止を意味しない。

### CASE-V03 社会：共有資源をめぐる異論と参加

- **目的**：複数当事者が情報や立場を確認し、権利を侵害せずに共同資源の使い方を検討する。**探索票のみ、現実の社会集団を対象とする実証は未設計**。
- **合成材料**：利用者A（便益が多い）、提供者B（費用が多い）、影響を受けるが利用していないCの三視点。規則の改定案、異なる資料の出典・時点、公開範囲。
- **介入**：A=通常の議事録とAI要約、B=対立仮説を保持するSUI/SEIの照合、C=B+必要時のみEKIの提供/受益データ照合。投票・承認の本番機能は作らない。
- **変化**：新たな費用情報、非参加者Cの異論、古い文書の版更新。
- **正例**：便益/費用/発言可能性を区別し、立場を変更でき、第三者への非公開情報露出を避け、未決を未決として次の問いを立てる。
- **失敗例**：議事録の多数意見を「社会の承認」と表示／匿名化した少数者の存在を推定できる表示／データを持つ主体だけが議論に参加できる。
- **測定**：声を持つ主体の範囲（調査母集団を明示）、根拠の再解決、異論の保存、修正反映、受益/負担の分布、データ公開の可否。結果の公正さは件数だけから判定しない。
- **前提**：Ostrom IADは参加者・行為の場・規則・相互作用・結果を見る研究上の観点であり、社会の統治制度をTAIが代理設計する権限を与えるものではない。

## 4. 抽象価値と技術的観測の接合

### 4.1 最小の追跡行（設計評価表。製品共通Storeではない）

`Value -> Stakeholder/Context -> Expressed need -> Candidate requirement -> Realization owner -> Evidence -> Outcome claim -> Review status`

記録時には、次の**識別可能な差**だけを必要量保持する。

| 区分 | 記録すること | 根拠の資格 |
| --- | --- | --- |
| 出所 | 利用者自身の表明／製品文書の方針／AI推論／外部研究の示唆 | 推論は本人の受理でない |
| 対象 | 誰の、何の、どの時点・目的・有効期間か。影響する第三者は誰か | 未調査を「存在しない」にしない |
| 実現 | 既存Harness／SEI／SUI／TEI／SHO／EKI／外部Providerのどこが何を担うか | TAIが二重に正本を作らない |
| 観測 | 実験入力、比較条件、版、操作可能性、作用の有無、結果の確認者 | 合成試験と実ユーザー受理は別 |
| 処遇 | Candidate／Contradicted／Supported in fixture／Needs stakeholder review／Accepted by actual Owner 等 | 固定の採用状態機械ではなく記録上の区別 |

### 4.2 評価は複数の軸を並列に保持する

1. **目的適合**：表明された目的に沿った選択・結果が生まれたか。
2. **認識の質**：重要な根拠、不明、相反する見解を適切に扱えたか。
3. **主体性**：利用者や関係者が実際に選択・変更・停止・異議を申し立てられたか。
4. **意味の継続**：担当者、ハーネス、版が変わっても適用条件と理由を再構成できるか。
5. **実行と結果**：外部作用は実際に起きたか、誰の受理か、結果不明を残せたか。
6. **学習と修正**：誤った仮定・古い意味・不十分な実現を改められたか。
7. **持続性**：注意、費用、時間、資源、他者の負担、撤回・縮退の余地を尊重できたか。

一つの総合スコアで権限越境、欠落、非参加者の負担を相殺しない。正例だけでなく、**有効な選択肢を過度に拒否する偽陽性**も測る。とくに「何もしない」は、本人が選んだ**肯定的な結果**と、支援不能で着手できなかった**未達**を分離する。

## 5. 技術を過剰固定しないための研究・開発の順序

| 既存計画と接続する段階 | 研究として追加する成果 | 行為・検証との境界 |
| --- | --- | --- |
| **探索（D1：概念・意味）** | V01〜V10の意味、反価値、緊張、予期しない関係を幅広く生成。SUI/CSW等のMethodは自由な候補探索として使用 | 生成中の否定・採否Gateで探索を萎縮させない |
| **現場化（D2：当事者と文脈）** | 直接/間接受益者、非利用者、本人の言葉、時間、地域・組織条件を収集 | 合成ペルソナは実利用者の発言に昇格させない |
| **技術比較（D3：対照）** | CASE-V01〜03から小さな正負例、A/B/Cと必要時Harness交代。まず既存ファイル/CLI/Toolsを使う | AI主導の隔離PoCは人の中間レビューなしで進められるが、実作用・公表・Owner意味受理は別 |
| **解釈と採否（D4）** | 異なる価値の緊張を調整し、不要な仕組みを委譲/薄いAdapter化/撤去する選択を比較 | 各製品のContractや権限の正式変更は当該Owner |
| **継続評価（D5）** | 利用者からの訂正、状況変化、受益分布、停止/取消の実効を継続観測 | 公開できる内容と実証済みの価値を区別し、YIサイトで過大な主張をしない |

**既存計画への割当**：個人はTAI #167/#166、組織は#165、協働統治は#127、ハーネス比較は#168とDraft #169、シリーズと公開は#73/#74。価値の研究自体は本PRの文書と既存TAIシナリオ評価票を使い、別の全社Gate/共通モデル管理システムを起こさない。

### 実施順の推奨（受理前）

1. **資料整合**：現行PPTXの内容とDraft #81原稿の実差分、未所在の`RQ-YI-013〜015`原典・採用履歴を再照合。
2. **先行CASE-V01**：創作＋期限＋休息の同一入力で、モデル主導/質問型協働、Harness単体/必要な製品を追加の比較設計。利用者なしの合成結果はQoLの証明に使わない。
3. **先行CASE-V02**：#165の同一合成資産3件で、情報不足と停止の両方を注入して、正しい部分作業が続くか確かめる。
4. **CASE-V03準備**：社会の利用場面では当事者の母集団・代理権・匿名性・公開範囲を先に調査。合成評価票は作れるが、公的・社会的な受理は扱わない。
5. **対照で縮退**：既存Harness単独で同じ価値が出た機能は、必要であれば外部委譲/薄い接続/撤去。役割を維持する理由は実証結果で判断する。

## 6. 新たに確認した外部研究と、適用範囲

| 出典 | 読み取れる研究上の事実 | YIで借用する問い・留保 |
| --- | --- | --- |
| [University of Washington: Value Sensitive Design](https://ischool.uw.edu/research/impact-stories/value-sensitive-design)、[VSD systematic review](https://doi.org/10.1007/s10676-023-09700-2) | VSDは概念/実証/技術の反復、直接/間接の利害関係者の考慮を重視。レビューは技術的検討の不足も論じる | 「価値モデル→要件」と一方向にせず、試用結果で価値解釈まで戻る |
| [Stanford Encyclopedia of Philosophy: Capability Approach](https://plato.stanford.edu/entries/capability-approach/)（2025改訂） | 実際に達成した状態（functioning）と、選べる実質的機会（capability）は異なる。資源が選択肢になるには環境条件も影響する | 完了率と選択可能性を別に測る。非実施も意図的選択なら価値になり得る |
| [Ryan & Deci (2000), APA](https://www.apa.org/research-practice/conduct-research/self-determination-theory) | 自律性、有能感、関係性を人の動機づけ・成長の観点から研究 | 個人支援が本人の主体性と成長を促すか。心理状態や医療的効果の推定は別研究 |
| [CHI 2026: Partnering with Generative AI](https://doi.org/10.1145/3772318.3791185) | 創作課題の実験でモデル主導は案の品質を高めつつ多様性/所有感を下げ、反省を促す協働はそれらを保ちやすいと報告 | **CASE-V01の比較仮説**。これが全領域・全Harness・TAIの改善を示すとはしない |
| [Ostrom Workshop: IAD](https://www.ostrom.indiana.edu/courses-teaching/teaching-tools/iad-framework/index.html) | 参加者、行為の場、ルール、相互作用、結果とその評価を分析 | 社会の多主体協働で、AIが暗黙の決定者になることを防ぎ、権限・受益・異議を区別する |
| [ISO/IEC 25019:2023](https://www.iso.org/standard/78177.html)／[ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) | **25019:2023は利用時品質モデル**、**25010:2023は製品品質モデル**。2011年版の利用時品質と混同しない | 目的・状況に即した価値と、技術的な製品品質を独立の観測軸にする |
| [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) | Govern/Map/Measure/Manageを通じてAIリスクを扱う | 高影響行為のリスクと実ユーザー価値を併せて検証。あらゆる探索に審査Gateを導入する根拠にはしない |

リンク先は研究・標準の紹介ページや研究論文であり、規格本文をすべて閲覧・適合性認証したという主張ではない。外部知見→価値仮説→要件候補の**翻訳**はYI側の判断で、研究そのものの結論と区別する。

## 7. 次回レビュー時に埋める欄

- **価値の出自**：Ownerが明示的に望んだこと／AIによる解釈／利用者への未確認の仮説／外部研究の示唆。
- **当事者**：直接利用者、共同利用者、影響を受ける非利用者、権限者。必要な場合に限り代理・参加条件を整理。
- **代替案**：追加機能／既存Harness／人の手作業／何もしない／縮退の比較。
- **観測の境界**：同一入力か、同じ権限か、試験場所と版、同一案件の実Effectか、未実施を明示したか。
- **変更先**：要件が正式に採用されるなら、その製品の既存Issue/ADR/計画へ差分だけ反映。横断の評価はTAIの既存シナリオへ。
- **公開可否**：一般化可能な価値と、公開許諾のない資料/関係者情報を分離。

**現時点の結論**：価値の研究を継続すること自体に意義がある。実装を急ぐ場面では、探索の自由・利用者の選択・実世界で確認できる結果の三つを守り、適切な独立製品と外部Harnessで小さく試す。評価結果によって価値の定義・製品境界・実装計画のいずれも見直し得る。

---

## 8. 2026-11-07 追補：Oracle Fusion AgenticのOutcomeをYIの価値検証に接続

**位置づけ**：外部Pressure Caseの一次資料、要件OR-01〜12と反証OX-01〜12、専門Ownerの対応は [TAI #531](https://github.com/hat47x/tai-pleroma/issues/531) が索引。本節は価値研究としての比較条件・独立Expected・測定順序を追補する。各Productの意味契約・共通Schema・認可の第二正本は作らない。現状は研究／提案／Owner未受理。

### 8.1 Outcomeと手段・業務効果を区別する

[OracleのOutcome Receipt解説（2026-11-06）](https://blogs.oracle.com/fusioncoe/fusion-claw-03-outcome-receipt)、[Hiring Workspace実操作例](https://blogs.oracle.com/fusioncoe/fusion-claw-lab-hiring-workspace)、[構成要素解説](https://blogs.oracle.com/fusioncoe/fusion-claw-04-building-blocks) は、Outcomeを測定可能な目的として扱い、Research（実変更なし）とFull Auto（限定Action）、事前Readと変更後Readback、Policyによる保留にもReceiptを設ける構成を説明している。Oracle製品のデモであってYIC実装済みの根拠ではない。

比較票では Value/Need → Intended Outcome（望まない結果を含む） → Candidate Plan → 適格Capability → 現在認可されたAttempt → 実Effect／非Effect → 業務Outcome判定 → 意思・前提の更新を接続する。

- **目的を提案したAIは、その目的のOwnerや組織上のAuthorityを取得しない**。目的の妥当性と現在の実行許可を独立に確認する。
- 技術的Receiptの完全性、計算適合、Providerの実Effect、業務の満足度は別の観測。「verified」単独では全段階の受理を表せない。
- **意図的な非実施**は肯定的なOutcomeになり得るが、失敗・未対応・未確認Effectとは区別。研究上のラベルであり共通Core enumを規範化しない。
- 「一切実行しない」はセキュリティのみならず本人の節度、資源節約、第三者の負担減少という価値を持ち得る。すべての停止を成功ともみなさない。

### 8.2 Receipt-firstを評価方法として取り込む

業務処理を設計する前に「後から第三者が何を観測できれば、目的・手順・実際の結果を判断できるか」を定義する。ただしReceiptの予定項目を記述したことは実Providerの証明ではない。

| 必要な観測 | 既存Owner | 誤って導いてはいけないこと |
| --- | --- | --- |
| 価値・本人の意図・利害当事者 | TAI価値研究、本人／業務Owner | LLMがまとめたGoalを本人の恒久的な同意とする |
| 意味・Source・母集団・時点／Projection | TEI #958/#2586、SEI #767、SHO | 取得結果0件から世界の不存在を断定 |
| Business DecisionとExecution Grant | TEI #1125/#2386/#2499、実Host | Approver＝Issuer＝Invoker＝現在Principalと同一視 |
| 現在対象・Operation・実Effect・Receipt | TEI #2598/#1174、EKI #407/#465 | HTTP/ACK/記録署名が実DB変更や成果を証明 |
| Outcomeと反対意見・継続価値 | TAI #271、SEI/SUI、業務Owner | 技術的成功を利用者の価値達成と同一視 |

開示できない項目はConsumer許可Projectionだけを扱い、観測できない項目は不明とする。監査を口実に機密の生PayloadやTraceを広く保存・送信しない。

### 8.3 既存CASE-V01/V02/V03の追加独立Expected

| 元ケース | 追加対照 | 正しいExpected／負例 |
| --- | --- | --- |
| **V01 個人：創作・休息** | 昨日は作業を依頼、今日は本人が休むことを選んだ。Heartbeatが古いGoalを再発見 | 現在の非実施を尊重し自動実行・不要通知を停止。許可された下調べだけ続ける選択肢は保持。古い予定を現在委任へ昇格しない |
| **V02 組織：脆弱性対応** | 3資産のうち影響有・無・不明、代理権が検討後に失効 | 確定分のread-only調査と隔離Patch試験は継続し、不明資産を全件済みにしない。本番変更には現在のHost Grant、拒否・保留の証拠も必要。適切な行為まで全面停止させる過剰拒否を測る |
| **V03 社会：資源配分** | 多数の賛同・一人の異論・非公開の第三者負担 | 多数意見、AI要約、件数の多寡は業務上の決定Authorityではない。異論・負担・未決を保持し、正当な主体の決定と分ける |

合成評価は各Productの意思決定や本番受理を代行しない。TEI/EKI実Effect検証は既存Ownerへ渡す。

### 8.4 追加すべき転換点の負例：Research → Action → 継続

Oracleの公開実操作例には、調査結果のActionカードからFull Autoに移り、対象・現在許可・実変更後のReadbackを確認し、**その後のフォローアップモードもFull Autoのまま残り得る**と記載がある。これは「モードの表示」と「実行可否」が違うことを示すUX圧力となる。

1. **古い推薦**：Researchのr0で候補Aが表示、Full Auto時r1で対象の状態・権限が変化。r0の結果だけで書込みを許可せず、実Hostが現在対象・許容Action・Grantを再評価する（TEI #2598/#2499/#1174）。
2. **モード残存**：Full Auto後の曖昧な追問を次の書込み承認とみなさない。現在の依頼内容と実権限を確認し、無用な二重確認を強制する方式だけに固定しない。無断Effectと過剰拒否を同時に評価（TAI #168/#422、SUI UI Consumer）。
3. **Readbackの範囲**：同じサービス上の変更後Readback成功は限定的なEffect観測であり、外部SaaS、Replica遅延、他Tenant、社会的Outcomeまで保証しない（TEI #1174、EKI #465、TAI #514）。
4. **結果不明からの再開**：Commit応答喪失・Runbook作成不明では自動再送を避け、同一Operation/Task/Attemptの照会・独立Readによって未確定を狭める（TAI #531 OX-04/07、TAI #271）。Oracle FSCR公開Runbookのunknown時停止は検討材料であり、全Providerの原子性証明ではない。

初回実証は [TAI #531 OX-01/02/04/07](https://github.com/hat47x/tai-pleroma/issues/531) の固定Fixtureを再利用する。既存TAI #168のH2/H3実Harness比較のBlocking Exitは増やさない。

### 8.5 D1〜D5／既存G0〜G4への差分と計測

- **D1/D2**：Outcome・非目的・本人の停止選択・関連する第三者を列挙する。外部事例の企業向けSOPをそのままYIC全体の価値として固定しない。
- **D3・G0/G1**：同じ合成Taskを既存Harness単体／Harness＋必要な製品Capability／異質な複数製品連携で比較し、増分価値が無い場合は薄いAdapterや不採用とする。
- **D3・G2/G3**：正当な部分作業の継続・適切な拒否・過剰な拒否・同一AttemptのEffectとReceipt・不明欄・独立Expectedを並列測定。Source-static／合成／実CLI／実Harness／実Providerの資格は独立。
- **D4・G4**：製品の意味受理と業務成果の判断をOwnerに戻す。決定論的計算や署名付きReceiptだけで自律実行許可を拡大しない。
- **D5**：Outcome FeedbackをSkill選択・Method選択・費用改善の候補に使うが、旧Grant・Accepted Meaning・Disclosure資格を現在へ自動継承しない。

測定軸は、目的達成、本人の主体性、誤副作用、適切な保留、過剰拒否、再開損失、追跡可能性、実測時間/費用、影響者別受益・負担。Oracle側の推論短縮率を独立検証なしに目標値へ流用しない。これらの比較票は技術システム共通Ledgerや新しい統一Policy Engineを必要としない。

**2026-11-07時点の資格**：一次資料と既存設計の比較、具体的Expectedの設計のみ。新たなYIC実E2E、H2/H3正式比較、実Host強制、本番DB／SaaS Effect、Owner意味受理、実利用者調査は **NOT RUN**。


---

## 9. 2026-11-07 再照合：Outcome Claimを「Receiptの存在」から「限定された実観測」へ下ろす

**状態**：外部事例の評価設計／既存Productの局所実証の再分類。新たなYIC統合実行・業務Owner受理は未実施。横断索引 [TAI #531](https://github.com/hat47x/tai-pleroma/issues/531)、Value/Owner [#422](https://github.com/hat47x/tai-pleroma/issues/422)。既存§8のReceipt-firstを**証拠の強さを分ける検査方法**へ精緻化する。本節は各ProductのRuntimeや正式Outcome schemaを再定義しない。

### 9.1 OracleのReceiptの強みと、YICが追加で証明すべき範囲

[OracleのOutcome Receipt解説（2026-11-06）](https://blogs.oracle.com/fusioncoe/fusion-claw-03-outcome-receipt)はRequester/Owner/Approver、SOP version、Source、Workflow/Service、Correlation ID、Linked transactions、署名、Policy hold、read-only runを挙げる。[Hiring Workspace実操作例](https://blogs.oracle.com/fusioncoe/fusion-claw-lab-hiring-workspace)はFull Auto前の再Readと許容Action照合、変更後のreadback、次の追問にFull Auto modeが残ることを説明する。**これらはOracleの公開デモである**。Oracle Receiptの署名/Verified表示が外部Provider全件の現在状態やOwner Outcomeを独立に証明したという評価は行わない。

YICは**保存した証拠の存在 / 改ざん検出 / 計算の適合 / ProviderのReceipt / Provider資源の現在観測 / Consumerへ到達した結果 / OwnerのOutcome受理**を独立に検査する。証拠の欠落・期限・部分取得・非開示を、単一successフラグへ畳まない。

**実製品で進展した事実**：[TEI merged PR #3155](https://github.com/hat47x/tei-platform/pull/3155)後のPersistenceStateは not-applicable / not-observed / receipt-observed / resource-observed の4種。実参照実行は committed=true でも persisted=false / not-applicable / durability=none。persisted=true は resource-observed に限定される。実PostgreSQL別poolの資源値readback等は限定試験で観測済み（[TEI #2998の更新](https://github.com/hat47x/tei-platform/issues/2998#issuecomment-6701739581)）。**旧mainでの「Receiptしか無いのにpersisted=true」は現時点の未修正バグとして繰返さない。**

他方、別Writerの同値ABA、実ReadのVersionとCommit時Version、複数行・明細集合の完全性、別Tenant/現Grant、実compositionでResourceReadを使えるか、Replica遅延、Consumer Disclosure/Owner受理は別検証。Resource bytes一致だけで「業務対象全件が確定した」とは扱わない。[TEI #1174](https://github.com/hat47x/tei-platform/issues/1174)、[#2564](https://github.com/hat47x/tei-platform/issues/2564)、[#2586](https://github.com/hat47x/tei-platform/issues/2586)の既存Ownerが受け持つ。

### 9.2 Outcome Evidence の必要閉包（比較用の評価列。共通Schemaではない）

以下を同じTask / Attemptで**本当に結べる場合だけ**各主張を採用可能とする。

| 段階 | 比較する証拠 | 証拠が無ければ導かない主張 |
| --- | --- | --- |
| GoalとContext | 明示された目的／非目的、Scope、本人の変更・撤回、関係する第三者 | AIの要約から本人の現在の同意・業務決裁 |
| MeaningとSource | 必要Semantic/Ruleが選択・実Loader Read・Parserで消費され、Accepted Meaning/Source revision/Provider bindingが対応 | validate okやCatalog件数から、実行した業務意味の充足 |
| OfferとIntent | Purpose、対象集合/Occurrence、粒度、時点、現在のAction適合候補、Request payload | UIで選べることから、Targetで変更してよいこと |
| Execution Authority | Trusted issuer、現在Host Grant/Scope、実Target、実Artifact、Commit境界の版条件 | 過去の承認、Full Auto表示、Skill説明からの実権限 |
| Effectと回復 | Operation/Attempt identity、実Provider Receipt、現在のresource read、別Operation混入・ABA・Unknown、適用可能な補償 | Receipt存在やCommand committed=trueから実保存・exactly-once |
| Delivery/Use | ResultClaim、実Body bytes/digest、Consumer受領、現在Disclosure、業務Owner review | ACK/JSON返却から納品物到達・経営成果 |
| Negative Outcome | 必要なEffect surfaceの範囲、未実行の根拠、保留のPolicy、既に起きた部分Effect、停止後残存作用 | 「blocked」や「read-only」という表示から全作用0 |

必要なSource全件と、何が使われていないかの**負の依存閉包**を確認できなければ「全業務ルールを満たした」「対象が存在しない」「他作用なし」を保証しない。SEI #767は問い相対の十分性、TEI #2506/#2586は取得Scope/Grainと実Read、TAI #271は現在資格を所有。非公開情報の存在そのものが漏れ得るため、外部Consumerには現在の許可済みProjectionのみ渡す（TAI #232、TEI #2516）。

### 9.3 独立Expectedで判別する追加反例

| ケース（既存OXへ付加） | 注入 | 独立Expected／過大Claimを拒否する条件 |
| --- | --- | --- |
| **ORX-01（OX-04）** | 参照実行は committed=true、Persistenceは not-applicable | UI・Harnessとも **保存済み／業務完了と表示しない**。merged #3155の現行契約を基準にし、古い欠陥を再起票しない |
| **ORX-02（OX-04/10）** | PostgreSQLの対象値は同じだが、別Operationで Versionを変えてA→B→A。同じ資源値へ戻る | bytes一致単独で「同じCommit/Attemptのpost-imageを検証」とはしない。版・Operation・時点の識別不能性を報告 |
| **ORX-03（OX-10）** | Header保存成功、明細D1は全2行、D2は3行中1行のみ取得。全体のReceiptには成功表示 | Header/一部Effectの観測を、複合業務の全件成立へ昇格させない。Grain/Scope/Completeness/必要Rule/Receiptを局所照合 |
| **ORX-04（OX-04/07）** | EKIのResultClaimはACK、Bodyは未着／別InstanceのRunnerから空Body（[EKI #465](https://github.com/hat47x/eki-fabric/issues/465)の実Source由来圧力） | Claim ACK、Body受領/digest、AcceptedResult、Business Outcomeを別判定。同一AttemptのBodyだけ再送、同じ業務Effectを新Attemptで無条件再実行しない |
| **ORX-05（OX-01/11）** | TEI commandsのread-only広告でも、-execute と記録用オプションで指定Pathにファイル出力（[TEI #3182](https://github.com/hat47x/tei-platform/issues/3182)） | 読取り専用の**正本データ効果**と、Workspace/記録ファイルへの効果を分ける。外部HarnessのOS隔離/出力先と開示を実確認。read-only名称だけから書込ゼロを主張しない |
| **ORX-06（OX-06/08）** | 空のWorkspace/未ロードSourceでもvalidate ok、OKF index/verifiedは整合だが実Claimに必要な非出力Predicate・非開示情報が欠ける | 形式PASS、Tool invocation、意味上の十分性、開示資格は独立。未取得・partial・permission denied・not found・0件を使い分け、実Source/独立Expectedを確認 |
| **ORX-07（OX-01/12）** | Full Auto実行後の曖昧な追問で前回モードが残存。目的/本人の意図は変化 | Mode表示を新しいGrant/明示Intentと同一視せず、正当な操作の過剰停止も測る |
| **ORX-08（OX-05/07）** | 過去Receiptは改ざんなし、現在のGrantは失効。Skill/Runbookも改版 | 履歴Receiptの正当性と現在の実行可能性を分離し、必要依存のみ再資格化。Approval/Ownerの再受理を自動発行しない |

### 9.4 優先実行順と適格性ゲート

**先行現状の訂正（2026-11-07、後続実証を反映）**：[TEIの4 Session実証](https://github.com/hat47x/tei-platform/blob/main/plan/evidence/DSH_H2_H3_FOUR_SESSION_2026-11-07/README.md)により、DSH→実TEI CLI起動に加え、H3-A/BでSkill本文5,482byteと参照資料の**実Tool Load**も限定達成。旧h2-08をH2-Aに再利用、Task Path不一致、OS Read隔離とHoldout非露出が未成立、独立採点未実施のため**比較適格は0/4**。Tool実行・Skill実LoadをNOT RUNへ戻さず、同時にSession完了からSkill効果/業務Outcomeを主張しない。現行H2/H3のBlocking ExitにORXを混入しない。

1. **P0-A（今使える製品証拠）**：既存#3155のresource-observedとReference not-applicable、#1174のPG Unknown/CAS/ABA、#3182のnamed output、EKI #465のSource gapを異なる資格のまま比較票へ記入。既にある実Go/PG試験を再実装しない。
2. **P0-B（独立検証設計）**：ORX-02/03/04/05のSource・Operation・Provider・Observer・Consumerのうち、実観測可能なところをOwnerの既存Fixtureで特定。未観測列をUnknownへ残す。機密Rawや独立Expectedを外部Harnessへ公開しない。
3. **P1（業務縦切り）**：受注1件の意味からWeb/CUI/外部ConsumerのAction Offer→現在Grant→実Provider→Receipt/独立Read→業務Outcomeを **同一Attempt** で追う。実行前拒否と既に一部Effectが起きた停止は別。既存TEI #1119/#1174/#2598、EKI #407、TAI #271がOwner。
4. **P2（価値と多対象）**：既存CASE-V01〜03で本人の選択・過剰通知、第三者の受益/負担、業務の一部だけが達成された結果を比較。形式・実装成熟度・人の受理を分離し、外部の独立利用者評価がない限り実価値改善と断定しない。

**利用条件**：Oracleが称するOutcome Receiptの設計そのもの、FSCR Runbookの形式、署名方式、中央Policy/Agent RuntimeをYICの必須共通基盤にしない。TEI #2845は監査用Receiptの本番保存/署名・保持期間（未決）を所有し、ローカルdigest-onlyのReferenceを本番署名済み証拠とみなさない。業務Ownerの意味・成果受理は最後まで別列とする。

**資格の結論**：Oracle公開資料の確認／既存YIC Source・実Go/PGの限定実証の評価まで。今回この追補の新しいORX-01〜08を同一YIC実Harness・実Provider・独立Consumerで実行した証拠は **NOT RUN**。


---

## 10. 2026-11-07 追加接合：実Skill配達・投影情報損失とOutcome判定資格の分離

**状態**：現行他Productの実験記録・実コードテストを読んだ、価値研究用の限定比較と独立Expected。外部Pressureの一次資料索引は[TAI #531](https://github.com/hat47x/tai-pleroma/issues/531)、同Harnessの正式試験は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)、Skillマトリクスは[#488](https://github.com/hat47x/tai-pleroma/issues/488)。本節でTAIの新しいExecution Host、横断Semantic Registry、共通Proof/Policy Engine、強制的なSkill Manifest、別Trial Gateを作らない。

### 10.1 Tool・Skillが実際に届くことと、比較適格・実質的価値は違う

[TEIの実4-Session Evidence](https://github.com/hat47x/tei-platform/blob/main/plan/evidence/DSH_H2_H3_FOUR_SESSION_2026-11-07/README.md)を、前の「H3 Tool Loadは未実施」という歴史的表記より優先する：

- **実Tool Transport**：DSH 0.2.2-rc.1から固定TEI実BinaryへTool request→Resultが往復した（限定達成）。
- **実Skill Delivery**：H3-A/BはProduct Skill本文**各5,482bytes**＋参照文書を実Toolから受領。同一のSkill本文byteである。H2-A/BはSkill Tool呼出しなし。Skill一覧が出たことと、実本文を読んだことは分離できた。
- **Comparison Eligibility（比較採用資格）**：**0/4適格**。H2-Aは旧探索Session h2-08再利用、Taskの \`reference/workspace\` と隔離Rootの \`workspace/\` が不一致、H2が元Worktreeへread可能、同Hostの別Lane・独立Expectedへの非到達が実証できない。Tool初回の許可範囲と8,192byte等の部分返答も比較条件として未解決。4 Session IDの存在だけでは事前独立割付を意味しない。
- **Quality / Value**：回答へ必要語が登場することは独立Expectedによる正答採点ではない。Skillの効果・誤操作抑止・費用節減・利用者成果のいずれも**未証明**。DSH Usage Tokenの数字は課金額や差分効果ではない。

比較票は当面 \`Transport T / Skill body delivery L / Trial eligibility E / Independent answer quality Q / Incremental user value V\` の5列を区別する**論理評価軸**とする（新しいProductステータスenumではない）。特にL=observed と E=unqualified、Q=not scored、V=not demonstrated は同時に成立する。

**次の実行**：既存TAI [Draft #270のRunbook](https://github.com/hat47x/tai-pleroma/pull/270)と[#488](https://github.com/hat47x/tai-pleroma/issues/488)が所有する。参加者に見せるTask/実Workspace論理path・固定binary・Source・Model・Tool Profile、独立ExpectedのReviewer-only非露出、実OS/Hostの別Lane Read拒否をまず確認。新しいTrial Groupを事前割付して4つの独立Sessionで比較する。**本計画は手順/採点の第二正本を作らない**。

### 10.2 同じ公開Projectionから、同じ原世界を導けない

[SUI Draft PR #3396](https://github.com/hat47x/sui-sensemaking/pull/3396)の実製品関数 \`buildContextProjection\` を使った固定HEAD \`a7893f9c...\` の3テストで、次を限定実証した（[7ジョブのCI確認](https://github.com/hat47x/sui-sensemaking/actions/runs/42345897113)）。

- World A/Bで同一Cardの**原出典Source参照だけ**変えると、公開Projectionの**オブジェクト全体が一致**する。Card textやDigestだけを比較したわけではない。
- 別のA/Bで**Island所属のCard集合とCanvas座標だけ**を変更しても、公開Projection全体が一致する。Island titleは残るが、\`cardIds\`や原座標から元関係を復元できない。
- 正例として、公開Card本文・レビュー済みIsland題名を変更するとProjectionと対応Digestが変化する。常時同一の偽陽性ではない。

したがって、\`Projection(A)=Projection(B)\` なのに評価したい出典・構造Claimが異なる場合、**そのProjectionだけを入力とするConsumerは両者を識別できない**。文書を再構成しても、AIを高性能化しても、失われたSource/Edge/Occurrenceを原本から読まずに復元・帰属する保証は得られない。これは用途相対の**情報不足**であり、現在の公開Projection自体の欠陥と決めつけない（機密保護のための意図的なLossもある）。

[TEIの合成写像設計 Draft #3236](https://github.com/hat47x/tei-platform/pull/3236)では、\`D → V → W\` の部分写像・非単射・必要な否定依存・開示を区別。TEI側CX-01〜10は**設計／NOT RUN**。SUIの限定実試験をTEIの実Renderer/実Provider/SHO Writer/SEI Consumer横断E2Eへ読み替えない。

**価値上の帰結**：公開された本文が正しい・形式がOKF適合というだけで、原典の引用、Graphの構造、島の所属、逆編集対象、業務Outcomeの説明が正しいとは判定しない。必要なら許可されたProduct原資料Readerへ用途限定で照会し、十分性・出典一致を再評価する。外部AIへ非公開Sourceを渡して穴埋めしない。取得不能ならunknown/unsupportedを明示する。OwnerはSUI [#3392](https://github.com/hat47x/sui-sensemaking/issues/3392)／[Draft #3396](https://github.com/hat47x/sui-sensemaking/pull/3396)、TEI #2497/#2507、SHO #19、SEI #767、TAI #232。

### 10.3 ORX-09〜13：独立Expectedによる追加Pressure（新規の同一横断実験は未実施）

| Case | 独立して操作する条件 | Expected と拒否する過大Claim | 既存Owner |
| --- | --- | --- | --- |
| **ORX-09（OX-07）** | H3 Toolから実Skill 5,482bytes受領、4Session completed。ただしH2旧Session流用・Holdout非隔離・採点未実施 | T/Lは限定observed、Eは0/4 qualified、Q/Vはunverified。Skill実LoadをNOT RUNへ戻さず、Token/Tool差から価値の因果効果を推論しない | TAI #168/#488、TEI #2509 |
| **ORX-10（OX-01/11）** | \`--permission-mode read-only\`下で隔離Root外の元WorktreeをRead。内容はbyte一致だが論理pathと許可rootは異なる | 同一bytesでも許可されたSource Identity/現在Scope/Host Read隔離の成立は別。Output/Egress、OS read拒否とwrite拒否を別観測。許可外Readを継続可能なSkillの資格としない | TAI #168/#232、TEI #2509/#2515/#3181 |
| **ORX-11（OX-08）** | SUIのSource \`example:A\`→\`example:C\` のみ変更、公開Projection全体が一致 | Consumerは原Source・脚注・Review出典を公開Projectionから捏造しない。許可された原Readerが無ければ帰属unknown、SHOの文書出典受理も不可 | SUI #3392/#3396、SHO #18/#19、SEI #767 |
| **ORX-12（OX-01/08）** | SUI CardのIsland所属・Canvas位置だけ変更、同じ公開Projection。公開Card本文変更を正例対照にする | 公開表現が等しくても元Topologyは一意でなく、Markdown/OKF見出しから元Graph/Canvasへ自動逆Patchしない。可視本文の更新候補と明示元Subject Editを分離 | SUI #3391/#3396、TEI #2497/#2500/#3236 |
| **ORX-13（OX-06）** | Product SkillはLoadされたが、ToolのCatalogが上限で途中切断、指定されなかったRoot/必要Ruleがある | 「回答に必要語があった」「部分Catalogで対象が見えない」「validate ok」を対象全件・Rule消費・不存在の証拠としない。Result Completeness、必要Source/negative dependencies、実対象scopeを元Product Readerと独立Expectedで検査 | TAI #168、TEI #2586/#2823、SEI #767 |

**保持する区別**：Product自身のReadが成功したことと外部Harnessが安全に受領できること、Deliveryの成功と実Consumerでの意味適合、Stageの過去の実証と現在の同版利用資格。前回§9のEffect/Receipt/Bodyを重複して実装せず、追加5反例は**情報の取得・投影・比較試験の資格**だけを対象とする。

### 10.4 実証への順序：現行価値・Product計画を侵食しない

1. **P0、既存Skill初回試験**：TAI #168/#270に隔離・Task Path・独立Session/Expected・実Skill Load/独立採点を委譲。既にある4Sessionの実Load証拠を認めつつ、比較採用0/4を維持。ORX-09/10/13を新しいBlocking Exitとして**追加しない**。
2. **P1、投影の用途別十分性**：SUIのSource/Island非単射の実試験を横断Pressureとして読み、TEI #3236のCX-01/04/08、SHO #19、SEI #767の既存Fixtureと対応付ける。原典Sourceと公開投影を無理に同一可視化しない。
3. **P2、最小業務縦切り**：#2586のRead／Context、#2507のAction Offer、#1174の実Effect＋資源観測、EKIのResult Body、TAIのOutcomeを同じ意味・Attempt／Scopeで説明できるかを比較。実E2Eが無い間は局所PASSの合算をしない。
4. **D4/D5の価値判断**：内容を失うが使いやすい投影と、出典・逆編集に必要な原典に戻れる投影を、用途・説明負荷・許可範囲・過剰拒否・本人の選択で比較する。すべてをLosslessにすることや、全出典を外部Harnessへ配布することを要求しない。

**今回の達成と非達成**：TAI/TEIの実Tool＋H3 Skill本文LoadとSUIのProduction Projection非単射（Draft CI）の限定Evidenceを計画へ反映した。新しい4適格Session、独立Q/V採点、OS Read隔離、TEI CXの実Provider、SUI→SHO→SEI投影E2E、OKF実Attester、Owner意味/業務Outcome受理は **NOT RUN／NOT PROVEN**。


---

## 11. 2026-11-07 追加：自己証明の遮断、証拠の独立性、実利用先までの同一性

**状態**：既存Productの実コード・局所試験とIssueを再照合した横断価値研究。新共通Evidence Store、証明エンジン、Runtime Status、Gateは提案しない。§8〜10のOutcome/Receipt/Skill/Projectionの比較を、証拠自身の正当化と「実際に消費した対象」まで拡張する。対象の事実・評価上の主張・Owner受理を混同しない。

### 11.1 主張が証拠になるための5つの独立した問い

| 問い | 必要なWitness | 禁止する推論 |
| --- | --- | --- |
| 何を主張したか | Claim、対象、Operation/Attempt、Source・実行物・Contractのexact revision | 同じ名前／Digest／版文字列から、違うProcessや時点も同じだと推定 |
| 何に基づいたか | Claim本文とは独立に用意した原資料、期待値、Issuer・Ownerの資格 | 主張やAI生成文を、同じ主張の独立根拠に転用 |
| 誰が何を観測したか | 実Reader/Verifierが受け取ったbyte、Scope、完全性、Comparatorと判定結果 | 検証者名・署名の存在から、実取得・全件性・意味受理まで推定 |
| 今も使えるか | Source・Trust・Grant・Consumer・Purpose・Target・epoch・失効条件 | 過去に正しかった結果を、現在の権限・実Outcomeへ昇格 |
| 価値は生じたか | 本人/OwnerのChoice・業務Outcome・影響者・追加検証の費用と過剰拒否 | テストPASSやToken差から望まれた成果を直接推定 |

**独立性は一つのboolでない**。別言語のReader、独立に準備したExpected、別DB接続、別Issuer、現在のHost Grant、Ownerの意味受理は別の性質を検証する。

循環参照自体は情報整理上認められ得る。しかし、Aの根拠がA自身、またはA→B→Aだけから独立の真偽判定を成立させてはならない。議論・文書内の循環リンクと、外部根拠に裏付けられたClaimの区別を保持する。未検証は未検証とし、循環を無理に消して過去の記録を改変しない。

### 11.2 2026-11-07現在の既存Product実装証拠

**SEI：直接自己参照の登録拒否は限定修正済み**。[merged #822](https://github.com/hat47x/sei-cognition/pull/822)／[Issue #794](https://github.com/hat47x/sei-cognition/issues/794)で、Decisionのbasis/unresolvedが自身の論理参照を指す新規登録をCLI/MCP入口で拒否。既存Storeはread可能で、歴史を自動改変しない。[#752](https://github.com/hat47x/sei-cognition/issues/752)はRecommendationのresume JSONへbasis_references、responsibility_references、rationaleを追加。**参照を表示できることは参照先の内容・独立性・現在性の検証ではない。** 外部Bundleの間接循環や独立Witnessは未検証。mainのruntime/go/seicli/input.goは、新規書込み時の入力検査と既存Store読取りを明示して区別する。

**EKI：版の自己申告は限定改善済み**。[merged #783](https://github.com/hat47x/eki-fabric/pull/783)／[#248](https://github.com/hat47x/eki-fabric/issues/248)で、eki-control/eki-agentのVersionはvcs.revision、vcs.modified、Go版を返し、VCS不明ならunknownを明示。mainのinternal/buildinfoは、この申告を改ざんされていないことの証明とは**みなさない**と明記。実Process/実Worker Wire/API版、署名・Build来歴、Consumerに到達した結果は別資格。以前の固定dev表示を現在の未解決バグとして扱わない。

**TEI Plugin Registry：別Readerで同じテスト用主張を照合する限定実証**。[Draft #3244](https://github.com/hat47x/tei-platform/pull/3244)／[#2589](https://github.com/hat47x/tei-platform/issues/2589)は、Go/Nodeで実SHA-256・Ed25519を用い、Release・必須Artifact role/bytesとVerifier StatementのSubject/Profile/Targetを照合。専用CIの限定successは既存Issueに記録。両実装の公開鍵は固定された**テスト用信頼起点**、Owner Epoch/Issuer Trust/freshnessはmock、signed passedは実Conformanceを実行した証拠ではない。2言語の実装があっても、同一Fixture・模擬信頼への合意を実外部Issuer/Consumerの独立検証に昇格しない。実GitHub ReleaseのReadback、実Trust、全必須Member取得、Consumer側の実LoadはE1〜E3の未達。

**TEI Self-build：Artifact再現とSource閉包は非同値**。[Issue #2831](https://github.com/hat47x/tei-platform/issues/2831)／[mainの外部Module受入判断資料](https://github.com/hat47x/tei-platform/blob/main/plan/design/EXTERNAL_GO_MODULE_ADMISSION_CONTRACT_2026-11.md)によると、隔離外部Go Module供給でcmd/teiはBuildでき、独立2回の同じArtifact byte、実選択12 Moduleの供給照合と入力Member列挙まで局所実証。他方、現行ResolveSourceClosureは同対象の閉包をrejectedとする。外部Module受入A/B/CはOwner未採用、G4はUNQUALIFIED。Build/同byteという事実をQualified Source closureやRecursive self-buildへ昇格しない。

**TEI Completion：実Reader観測はCallerの完全性申告を正当化しない**。[Draft #3238](https://github.com/hat47x/tei-platform/pull/3238)は隔離PostgreSQLの固定Tenant Aで2件取得とTOP1を対照にし、独立Expected L={3,9}を試験に使用。部分取得R={3}へCallerがCoverageComplete=trueを渡すと、現EvaluateCompletionはholdsを返し得る。実Source/Query選択、物理Provider、Field/Predicate実評価、Scope/Page末端の閉包は[#2586](https://github.com/hat47x/tei-platform/issues/2586)の別責務。部分取得を「実Readerを使ったから全件確認」としない。

### 11.3 ORX-14〜19の追加独立Expected（新横断試験はNOT RUN）

| ID | 対照事例 | 独立Expected／保証範囲 | 既存Owner |
| --- | --- | --- | --- |
| **ORX-14 自己参照根拠** | SEI Decision Aのbasis/unresolved=A | mainの**新規直接自己参照拒否は達成済み**。旧Store readは非破壊。自己の記録存在だけで外部根拠が成立しない | SEI #794/#822 |
| **ORX-15 間接循環と推薦根拠** | Decision A→Recommendation B→A、またはBにbasis文字列だけある | 推薦の根拠参照の表示と実内容照合・独立Witnessを別判定。外部Bundle/間接循環の適格性は未実証 | SEI #752/#767、TAI #271 |
| **ORX-16 自己申告の版** | EKI実行ファイルがrevision Xを申告してもAPI/Worker実Versionと異なる | Version表示改善は実装済み。実Process/Connection/Worker、独立Artifact digest、Current Grantの一致を別観測。Unknownをdevに丸めない | EKI #248/#198、TAI #271 |
| **ORX-17 署名付きfixture PASS** | TEIの固定鍵で署名・Digest整合するが実Publisher失効／Consumerが異なるbytesを取得 | 署名検証は限定PASS、実Trust・Member実Readback・実Conformance・実Target Loadは別。検証器の多言語性≠独立Issuer | TEI #2589/#1104/#1105/#1370 |
| **ORX-18 再現Build／閉包拒否** | 2試行のcmd/tei Artifact byte一致、外部Module閉包はrejected | Artifact再現PASSとG4 UNQUALIFIEDは両立。A/B/C案のOwner決定までSource資格を発行しない | TEI #2831/#1090 |
| **ORX-19 実Read／虚偽Complete** | PGでL={3,9}、TOP1のR={3}、CallerはCompleteと自己申告 | 独立のL/Scope/ページ末端/実Predicate Witnessなしに全件結論を出さない。局所PG実試験とProduct E2Eを分離 | TEI #3238/#2586/#2514、SEI #767 |

### 11.4 実行計画と価値判断

1. **P0/H2-H3は現行Exitを変更しない**：TAI #168/#270の実OS Read隔離、独立4 Session、独立Expected/回答採点が先行。ORX-14〜19をSkill比較の新Blocking条件にしない。
2. **既に達成したProductの局所成果は取り消さない**：SEI #822、EKI #783のmain統合と、TEI #3244/#3238のDraft限定試験を分けて記録。コードが統合されたか、Consumerに届いたか、Ownerが意味を受理したかは別。
3. **次の一業務Functionの実証に必要な分だけ接続**：TEI #2586の選択Query/SQL/実Rowset/Completeness、#2507のForm/Table、#1174の実Effectと独立Read、EKI同AttemptのBody、SEIの必要根拠、TAI Outcomeを、実際に確認できた相関だけで束縛。各局所PASSを足して横断E2E成功にしない。
4. **CASE-V01〜03のValueへ返す**：Witness/再Readで減る誤Claim・誤作用と、余分な待機・確認負担・非開示・過剰拒否を両方測定。すべての文章・検討過程へ署名や本番Attestationを義務化せず、用途と影響度で必要な観測を選ぶ。
5. **組織・Subsystem分割は別資格**：[TEI #3250](https://github.com/hat47x/tei-platform/issues/3250)はCRUD更新凝集・越境CUD最小化のread-only設計候補。論理分割のScoreから実Effect/Tx、物理DB配置、Owner責任・現在Grantを自動確定しない。VA/H2の新Hard Dependencyにしない。

**資格の結論**：この追補では現行実Source・Issue/PRと既存実CI/PGの限定証拠を照合して研究計画へ採用候補を記録。ORX-14〜19を同一実Target・独立Consumerで横断再実行した事実、TEI G4、Registryの実Trust、業務Owner受理、実利用者の成果価値は**NOT RUN／NOT PROVEN**。

---

## 12. 2026-11-07：Claim判別可能性による最小Witness選定（横断評価法）

**状態**：研究・既存試験への適用提案。§9〜11のOutcome/独立性に対する反証を、テスト設計で使いやすい形にする。新Proof Engine、共通データ形式・State、全面監査・全Source取得を追加しない。独立ExpectedのOwnerはTEI #2514、各Productのテスト・実Hostはそれぞれの既存Issue。

### 12.1 観測だけからClaimを判別できるか

同じ用途・Consumerに対する許可済み観測を O、判定したい業務上の問いを Q、実際のWorldを A/B とする。**O(A)=O(B) なのに Q(A)≠Q(B)** の二世界を構成できれば、Oだけを受け取る判定器はAとBの両方について必ず正答することはできない。これはモデルの能力や多重推論の不足ではなく、観測情報の判別力の不足である。

その場合にできることは、(1) QをOから判定できる局所Claimへ狭める、(2) 対象Use-siteで必要な元Product/ProviderのWitnessだけを許可付きで追加取得する、(3) 取得できなければunknown/限定保証を保持する、のいずれか。**非公開Sourceの存在や値を外部Consumerへ漏らして穴埋めしてはならない**。遮断・非取得がある世界でも、当該Consumerへ公開可能な出力は開示Policyを満たす範囲に限る。

正例対照も必須とする。Qに関係する公開値や実Providerの実Readが変化した場合、O/判定が適切に変化することを示す。「すべてunknown」「すべてdeny」による表面的な誤成功防止も合格にしない。

### 12.2 既存二世界Fixtureを新規作成せず、何を判定できるかを照合

| 対照する二世界 | 観測上の同一性 | 異なるQと必要Witness | Owner／現在の資格 |
| --- | --- | --- | --- |
| **出典A/B**：SUI Card本文は同じ、元Sourceだけ異なる | SUI公開Projection全体が一致 | 原典帰属・脚注は判定不可。許可された原Source Reader/Occurrenceを別照合 | [SUI Draft #3396](https://github.com/hat47x/sui-sensemaking/pull/3396)の本体テストは限定PASS。SHO #19、SEI #767への実配達は未実施 |
| **構造A/B**：Island所属/Canvas位置だけ異なる | 同じ公開Projection | 元Graph/Canvasへの逆編集対象は判定不可。元ProductのSubject/Topology・Source/epochが必要 | SUI #3396は限定PASS、[TEI Draft #3236](https://github.com/hat47x/tei-platform/pull/3236)はCX/WXの設計 |
| **全件/部分**：L={3,9}とTOP1 R={3}、呼出元がどちらもCompleteと自己申告 | ConsumerのCoverageComplete=true表示が同じになり得る | 全件性はReaderのrowset/Query/Scope/Page終端と独立Lが必要 | [TEI Draft #3238](https://github.com/hat47x/tei-platform/pull/3238)隔離PG限定Read到達、Product #2586は未接続 |
| **同名別Workspace**：同じsales.order識別子だが実Manifest/Contextが違う | Subject名や外形が同じ | 実Function/Row/Action対象の同一性にはSource/Manifest/Context epoch・Tenant/Scopeが必要 | [TEI #2507](https://github.com/hat47x/tei-platform/issues/2507) WX-01/02、CLI #3181。現段階は独立負例の計画 |
| **署名と現在Trust**：同じRelease Digest/署名、Issuer失効時点だけ違う | 署名検証結果は両方PASSし得る | 現在のPublication/Consumer Use資格は別Trust/Freshness/Release Readbackが必要 | [TEI Draft #3244](https://github.com/hat47x/tei-platform/pull/3244)固定Fixtureの署名PASS、E1〜E3未資格 |
| **同じ版文字列/別実体**：EKIの--versionが同値、実Process/WorkerまたはBuild入力が違う | 実行物自己申告の文字列が同じ | 実Artifact/Process/Connection・実Consuming Hostの同一性は独立観測 | [EKI merged #783](https://github.com/hat47x/eki-fabric/pull/783)は自己申告改善済み。実Host資格は別 |
| **組織の図で見えない辺**：同じER/CRUD表示、外部CUD Edgeの未取得/非開示だけが異なる | 可視図・layoutが同じ | 「越境更新が0」は未知。受理Sourceの必要Closure、Scope、実EffectとOwnerが必要 | [TEI #3250](https://github.com/hat47x/tei-platform/issues/3250) SP-02/05・[#2514](https://github.com/hat47x/tei-platform/issues/2514) WX-05は計画 |

### 12.3 Evidenceの『強さ』を全順序にしない

署名済み記録、独立Reader、Product実Read、業務Ownerの受理は同じ軸の点数ではない。あるClaimにはSource byteの同一性が必要でも、別のClaimには現時点の法的権限・業務責任・開示の妥当性が必要。**必要な証拠の種類が異なるため、単一のProof ScoreやReceiptの最大段階で一律判定しない**。

同じWitnessを用途ごとに再利用する場合は、(i) Claimに必要な依存、(ii) 実際に観測したbyte/Member/Query/時点、(iii) 証拠を独立に採点した基準、(iv) 現在のConsumer Disclosure、(v) 改訂・失効の条件を比較する。[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)の選択的再資格化、[TEI #2600](https://github.com/hat47x/tei-platform/issues/2600)のBuild再利用を利用し、**履歴の正しさ／再計算省略／現在の実行資格**は別々に扱う。実際に必要な依存が列挙できないならunknownを保つが、無関係な変更で全Claimを再計算する必要もない。

### 12.4 最小実証と価値評価

1. **P0：既存の実証を採用**。SUI #3396の二世界と正例、TEI #3238のwhole/TOP1、TEI #3244の署名/Trust模擬対照、SEI #822の直接自己参照拒否、EKI #783のunknown version出力を、それぞれの限定した資格で比較票へ記入。新たな一式E2EのPASSとは呼ばない。
2. **P1：1 Claimごとの誤判定耐性**。TEI #2514のIndependent Expected／Mutantを正本として、Oが同じでQが異なる場合に誤allow・誤全件・誤出典が起きないことを検証。Qが本当にOから判別可能な正例では、不要な拒否を減らす。
3. **P2：追加Witnessの費用対効果**。CASE-V01〜03で、Source/Providerの再ReadやOwner確認が誤Claimを減らす効果、待ち時間、金銭費用、Disclosureリスク、人手介入、適正な非実行、正当なActionの過剰拒否を分けて測る。技術的なテスト成功を利用者の実価値としない。
4. **実行順の非干渉**。TAI #168のH2/H3初回比較のGateは変更しない。最初のProduct実ReadはTEI #2586、Action/Effectは#2598/#1174、独立受入は#2514、認知十分性はSEI #767、投影はSUI/SHO、Artifact配布と実消費はTEI #2589/EKI既存Ownerが担当。

**未達**：この節の二世界をYIC同一Attemptで横断する実Validator/実Consumer/Owner受理はNOT RUN。正しい部分Claimに過剰な制約を足すことも、全件を保証できないのに成立と称することも、共に改善対象にする。


---

## 13. 2026-11-07 夕方追補：独立Expectedを「実際に欠陥を見分ける製品動作」へ接続する

**状態**：最新の既存実Product/CIを用途限定で採用した価値研究・受入計画。§8〜12のOracle Outcome/Receipt/Claim判別可能性を、実際に動いたTEIのテストDogfood、SUI→SHOの固定Raw引渡し、TEIのBOM/Design Context候補へ接続する。新しいYI Common Test Engine、Proof Engine、Runner/Registry、横断Host、別の独立Expected正本は作らない。

### 13.1 TEIのT0は初回の製品Dogfoodとして成立。ただしT1は別の実験

[TEI #3262](https://github.com/hat47x/tei-platform/issues/3262)と[統合済みPR #3264/#3266/#3268](https://github.com/hat47x/tei-platform/pull/3266)を再照合。[exact main 69a2996187852a036057b7155d6e847527b67346のpush CI #42359610226](https://github.com/hat47x/tei-platform/actions/runs/42359610226)はcompleted/success。単一の実TEIバイナリでread-only CLI **9コマンド**、Product Skillの静的検査**14件**、既存固定Driver Scenario **6 Step**、実CLI負例**4件**と「必須Step欠落／常時satisfied」の独立義務負例**2件**を実行・検出。局所的なGo文カバレッジは限定したcmd/tei単一Test選択の**C0相当10.1%**であり、全製品C0でもC1でもない。CI Artifactは保持7日という期限付き。実観測と保存先/現在アクセス可能性も別の証拠。

これは**既存Pinned Scenarioで既知の誤実装・誤Expected・欠測を拒否できる**というT0の限定資格。AIが未カバーRuleを発見して**新しい**テストを生成できるT1は未実施。[Draft #3273](https://github.com/hat47x/tei-platform/pull/3273)では公開合成Rule「line_number_positive」の0入力を次の未カバーNegativeとし、Required Source/Loader → Coverage Gap → Pattern選択 → Scenario候補 → 既存CLIへのPinned Run → #2514独立Expected/Mutant判定をTG-01〜06として設計。**提案したCaseが実行された/必要Source閉包を満たしたとは書かない**。

[PR #3268](https://github.com/hat47x/tei-platform/pull/3268)のCI path filter拡大は変更時の**実行トリガー**のCoverageであって、Testの枝C1やDomain Rule判別率、実依存閉包とは別。#3262はSubject/Rule/Business/NFRのRequired closureとTool応答の完全性をP-1の対象に持つ。#3264のCLI実読取・SourceIndex一致・required Source Loader Read・stale/欠落負例は限定達成だが、全ScopeのDesign Context QueryやMCP、実Provider・Business意味の全結合ではない。

**価値評価の分母**：実行されたCase数 / 独立に判別したMutation数 / Required Ruleのうち実カバー・未カバー・unknown / CI Triggerの対象依存と未検知 / 実Harness操作回数・回答訂正コストを別々に記録する。C0数値をC1や要件網羅率へ流用しない。最初は単一の業務RuleからT1に進む。既存Scenario SSOT=#1180、Independent Expected=#2514、Design Context=#3262、AI-test技法=#3223、価値費用=#2018。

### 13.2 SUI→SHOは固定原文でProducerとReaderが動作。実転送/出典/保存は別

[SUI Draft #3397](https://github.com/hat47x/sui-sensemaking/pull/3397)は現ProductのbuildContextProjectionから、許可された非保留の公開Card本文だけを**read-onlyの通常Markdown草稿**へ変換し、未信頼Markdown文法をエスケープしてSource/Footnote/OKFのverified等を捏造しない。固定HEADの[CI #42352776477](https://github.com/hat47x/sui-sensemaking/actions/runs/42352776477)は生成原文**354 raw UTF-8 bytes**と独立Expected SHA-256一致を限定実証。

[SHO Draft #21](https://github.com/hat47x/sho-composer/pull/21)はその**同一固定原文**を独立FixtureとしてSHO G1b実Readerに与える試験を作成。[修正後のUbuntu/Windows CI #42353651398](https://github.com/hat47x/sho-composer/actions/runs/42353651398)では両OSとも**18/18 PASS**。初回WindowsはLF→CRLFの14改行で**354→368 bytes**となりFAILしたため、修正は**当該合成Fixtureだけ**をLF固定とした。著者本文や製品Writerの改行を勝手に正規化する方式は採用していない。エスケープされたLinkはlink_open=0、解除した対照は1となる限定Parser判別も含む。

これで「実SUI Producerが生成した固定Rawと独立のSHO Reader用Fixtureの整合」「各Repo固定HEADのProduct別CI」が**限定成立**。ただしこの2回のCIは**一つの実ファイルをSUIプロセスからSHO CLIへ自動搬送した同一Attemptではない**。原Card Source/Island/Edgeは公開投影から失われ、SHO側は元出典・Occurrenceの真正性、文書Owner Meaning、外部再配布、G2 Writer Save/Restart、SEI Inquiry、OKF Conformanceを保証しない。SHO G1bの未解決参照/特殊FIFO readerの既存未受理も残る。

価値上は、「慎重な文章化で出典を捏造しない」ことに加え、**異OSでもSource Raw byte不変で引き渡せること**が重要。最初のP1は、静的Fixtureの証拠を保持したまま**実SUI生成物のbyteをSHO CLIへ実File/Process Handoffし、独立に再Hash/Parse/受領**を同一Attemptで確認する。元資料を必要とする用途は別の許可されたSource Readerへ戻し、原典無しで脚注・逆編集を行わない。OwnerはSUI #3391/#3392、SHO #16/#19/#21、SEI #820、TAI #232/#271。

### 13.3 Verified Composition BOMは「計画器」が動き始めた段階

[TEI #3267](https://github.com/hat47x/tei-platform/issues/3267)は検証済みPlugin組合せBOMと多版MatrixをTEI基本機能として定義し、[Draft #3269](https://github.com/hat47x/tei-platform/pull/3269)はGoのread-only候補/Version Matrix Referenceへ前進。隔離ローカルGoの**15 Test/race/vetの限定PASS**と、2×2・Pairwise計画の実行記録があるが、**GitHub exact HEAD CIと実TEI Resolver/Scenario/Build/Consumer接続は未認定**。

特に supplied-locks-pairwise の試験では、3軸×2値の宣言全8組のうちexact Lock候補が4行提供された場合、宣言ペア12のうち**観測候補ペア9/12、計画上の被覆9/9、未出現3ペア**となる。これは「提示されたCandidate集合の中のPairwise計画の完全性」であり、実現可能なCandidate Universeの完全性、実Target実行、3-wayの相互作用、Qualified BOM発行を証明しない。Referenceのqualified=false / planning-onlyを維持する。

二つの個別BOMが各々Qualifiedでも、**結合したContract/Effect/Artifactの跨BOM相互作用が未試験なら、UnionをQualifiedと呼ばない**。また、SBOMの依存在庫と実互換検証、Lockの選択と実Consume、Cache hitと最新資格、上流が「open/unpromised」としたAPIへの下流独自依存を混同しない。まず#3262 Design ContextでCandidate/Required closureの範囲を求め、#951/#1016の実Resolver/Lock、#1180/#2514の実Scenario/Expected、#943/#2600の実Artifact/実Memberに接続して初めて評価対象となる。開放的なPlugin公開を一律禁止するのではなく、**下流利用者が自ら適合検証する経路**を残す。

### 13.4 2026-11-07に進んだ周辺Product設計の位置付け

- [TEI #3277](https://github.com/hat47x/tei-platform/pull/3277)：Core外のCLI/StudioをPlugin-firstにする要求と現コード監査はmain統合。静的CLI Dispatch・固定Wails Bridgeが残るので、通常CLI/Studio実行が既存#951/#1016のResolver/Contract/Providerを実際に通ったというClaimはまだ無い。最初は一つのread-only Inspector/Model CatalogのDogfood、全面移行は後。
- [TEI #3270](https://github.com/hat47x/tei-platform/issues/3270)：汎用Data Source Workbenchの標準職掌はSchema/TableのCREATE/ALTER/DROP等の開発者向けDDLまで含む。サーバ起動/Backup/Replica等のDBA運用は標準外。Schema Previewと実Apply/現在Grant/独立再読取は別。既存#2586のProduct実Row→Data Context未接続を飛び越えない。
- [TEI #3274](https://github.com/hat47x/tei-platform/issues/3274)：REST例外をHTTP statusだけでなく Server Decision Graph → HTTP/Problem Details → Client Reaction → unknown Effect/Recoveryとして検証する設計は成熟したPressure。HTTP 202/401/403/409/412/422等と業務結果を混同せず、未知Commitの自動再送を避ける。ただし実Graph/HTTP E2EはNOT RUN。
- [TEI #3250](https://github.com/hat47x/tei-platform/issues/3250)：Subsystemの図・CRUD・論理分割とEffective Effect/Owner/Targetは別資格。仮のdiagram/scoreから本番配置や権限を自動決定しない。

これらをOracle比較の追加Blockingとせず、**各Productの独立実証トラック**として扱う。既存TAI #168 H2/H3四Sessionの比較適格性0/4、TEI #2831 G4 UNQUALIFIED、TEI #2586の一Function実Provider Read未成立は維持する。

### 13.5 ORX-20〜26：実行済みと未実施を同じテスト枠へ混ぜない

| ID | 対照 | 独立ExpectedとClaim ceiling | 担当 |
| --- | --- | --- | --- |
| **ORX-20 既知Mutantに強いが未カバーRule** | TEI実Scenario既存6 StepはPASS、line_number=0の新負例は未実行 | T0の既存Negative検出を認め、AI新Case提案/実RunのT1は未達、C0 10.1%は局所のみ | TEI #3262/#2514/#1180、Draft #3273 |
| **ORX-21 CI Trigger盲点** | Domain/Scenarioを変更したがWorkflowのpath filter対象外 | テスト自体の判別力と実CIが起動する範囲を別判定。#3268のwatch拡張を実依存の完全閉包としない | TEI #3268/#2600 |
| **ORX-22 OS改行でRaw不一致** | SUI Expected 354 byte、Windows checkoutはCRLFで368 byte | 原Byte不一致を認め、fixture LFで固定した新CIは限定PASS。見かけのMarkdown同一性からRaw Identityを推論しない | SUI #3397、SHO #21 |
| **ORX-23 固定Fixtureで2Repo PASS** | SUI Producer/SHO Readerが同じ354 byteを別CIで検査 | 両方の限定PASSを認めるが、実Producer→Reader同一Attempt輸送と、元出典・Owner受理は未実証 | SUI #3397、SHO #21 |
| **ORX-24 Pairwise分母の差** | declared 12 pairs、supplied candidates 9、計画は9/9 | Candidate9/9を全12/12や実互換PASSに昇格させず、未出現3はunknown。pairwiseは高次互換を保証しない | TEI #3267/#3269/#3262 |
| **ORX-25 BOMの組合せ不干渉** | A+B、B+CがそれぞれPASS、A+B+Cは未試験 | Union資格を発行しない。必要な跨BOM相互作用の独立Scenarioへ | TEI #3267/#1180/#2514 |
| **ORX-26 HTTP応答の成功過大Claim** | 202 Acceptedの後にcommit unknown/旧Receipt、Retry-Afterあり | ClientはBusiness Completedとせず、実Operation/Receipt/Readbackで再資格化。現在Grantなしに無条件再送しない | TEI #3274/#1174、EKI #407 |

**初回DoD**：TEI T0とSUI→SHO Product別固定Byteの限定PASS、TEI BOM計画器のローカルFixture PASSを別列で認め、必要な横断一往復・新規T1・実Resolver/Target/Provider・正式Owner価値受理を**未実施/未認定**として残す。最初の追加実験はT1の1 RuleとSUI→SHOの1 Raw File handoffで十分。毎段に別のProduct共通Verifierを増やさない。

---

## 14. 2026-11-07 夜追補：T0.5実失敗拒否・BOM要求ID収束・原子的Traitの実装義務

**状態**：2026-11-07 12:31 UTC時点の既存Product actual code／main CI／Issue／Draftを再照合した価値研究の現在化。以下は製品OwnerからYIC評価への引渡しであり、新共通Kernel/Runner/Proof Engine/認可正本の仕様ではない。先行§13の#3269は当時の実験履歴、現在のBOM採用候補は#3297。

### 14.1 T0からT0.5へ：安全に止められることを実際の本体CLIで確認

[TEI Issue #3262](https://github.com/hat47x/tei-platform/issues/3262)の[merged PR #3284](https://github.com/hat47x/tei-platform/pull/3284)では、既存TEI CLIの9 read-only JSON応答を消費する**テスト用Context Gate**がmainへ統合済み。必須Source/Loader読取、Subject、World/Index Fingerprint、Schema/欠落を突き合わせ、正常な限定Contextでも **partial / exploration-only / qualifiedTestGeneration=false** を返す。Contextが不完全でも仮説・provisional Test Pattern候補の検討はできるが、独立Expected未確認のまま実Scenarioの採用資格は発行しない。

その後[merged PR #3296](https://github.com/hat47x/tei-platform/pull/3296)では、旧Draft [#3293](https://github.com/hat47x/tei-platform/pull/3293)が重複する第二Packet Readerを作りかけた問題を解消。#3293は**closed/unmerged**、既存Consumerを直接拡張した。特にworkspace-files側だけでRoot欠落が観測された場合、validate結果だけで成功とせずblockedへ倒す。実CLI応答の一時コピーで、ファイル欠落、途中切断、改行終端欠落、重複JSON member（Unicode escape等価を含む）、NaN、後続JSON、Required Source二重計上等を拒否。

**mainでの限定実測**：[TEI main d6a452f79023744e7926669c3556d2699f546697 の実Push CI #42371592023](https://github.com/hat47x/tei-platform/actions/runs/42371592023)はcompleted/success。**9実CLI応答、既存7＋Manifest/Source Root2＋Tool Reply Byte変異7＝計16判別Control、Pinned Scenario6 Step、既存Test Ability6 Control**を同じ実バイナリのCIで確認。局所単一テスト選択のGo statement C0相当10.1%、C1未測定。実Binary SHA256 314f1e4f7f558ab5f69163d62f6cdd02b924447c9d1235a184d87021f320b0ef。Artifact ID 13574450699は7日保持の短期証拠で、永久保存の保証ではない。

**保証の上限**：16件は実外部H3 Tool Replyを切断して再送した試験ではなく、実CLI応答を一旦受領した**ローカル一時byteの合成破壊**。Tool受領のG2、OS Read禁止のG0、外部EgressのG1とは独立。対象sales.orderのParser/Accepted Meaning、Function/Business/RuleのRequired全件Closure、C1/NFR、Product実Readも未達。合成NegativeのPASSと『外部Deliveryの全欠落を防いだ』は別Claim。

**次の順序**：mainの既存Gateを維持 → #3262 P-1b1でline_number_positive一RuleのRequired/Observed/Unknown・実Source/Role/Parser/非出力依存をtyped referenceで表現 → [Draft #3273](https://github.com/hat47x/tei-platform/pull/3273)のT1でAIが未カバー line_number=0 を提案 → #1180の既存Scenarioで実Run → #2514独立Expected/Mutant判別。Tool Replyがpartialのときprovisional案は許すが、正式なScenario/Resultへの昇格は停止。新CLI/MCPや完全な万能Context APIをT1より前の必須条件にしない。

### 14.2 SkillのComparator合格と、試験環境の独立性を分離

[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488)の[Comparator CI #42370311513](https://github.com/hat47x/tai-pleroma/actions/runs/42370311513)でSK-02合成72/72、SK-03 19/19の限定合格が記録された。これは試験票・反例の判別能力であり、実OSのSkill/Holdout領域へのRead拒否、実Egress全Sink拒否、H2/H3の比較適格4Session、独立Q/V採点の合格ではない。G0実OS Read deny→G1実送出→G2 Tool Call/Reply同一Attempt完全受領→H2/H3割付・独立採点という[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の既存Exitは変更しない。H3 Skill実Loadの過去限定達成も取り消さない。

### 14.3 BOMの要件ID・Draftを最新mainへ正規化

§13の[旧TEI Draft #3269](https://github.com/hat47x/tei-platform/pull/3269)は**closed/unmerged**。並行開発でBOM側に付けたRQ-035が、mainに先に統合された**RQ-035＝異種Data Source Workbench（Schema CRUD、#3270）**と意味衝突したため、現行の統合候補は[**Draft #3297**](https://github.com/hat47x/tei-platform/pull/3297)へ切替えた。BOMは**RQ-036**としてRequirement・PAS・Gap Auditで別追跡する。旧番号を新要件として再利用しない。#3297の新exact-head CIはこの照合時点では未資格、製品要求のmain採用・実BOM発行へ先取りしない。

新Draftは既存Go Referenceの2×2／pairwise／supplied exact Locksに、**same-Attempt witness audit**を追加した。Source/Artifact/Target/Tenant Scope/Scenario/Independent Expected/checks/Attemptが一致したかをsynthetic入力で評価する。コード上の reported-pass は、証拠ID・digestの**申告整合**を確認しただけであり、Receiptの真正性、独立Expectedの作成経路、実Runner実行、Conformanceの外部適格性、現在Grantを証明しない。candidate pair9/9とdeclared pair12/12、Coverage/実行/Trusted Evidencesを別分母で管理。二つのQualified部分BOMをUnionした合成は別の実相互作用試験を要する。

### 14.4 原子的Traitは表示ラベルではなく『履行すべき義務』

[TEI #3278](https://github.com/hat47x/tei-platform/issues/3278)／[#3279](https://github.com/hat47x/tei-platform/issues/3279)では、Traitを小さなContract/Required obligationとして設計し、提供・生成・手動必須・外部Hostという実現方式の違いを残す。manual-requiredで実Implが無ければunfulfilled、宣言のみで実Conformanceが無ければprovided-but-unverified。Traitの順序非依存の合成と、実PipelineのEffect順序は異なる。Open/unpromised APIに下流が依存することは許し、Publisherが約束していないStable保証やInternal/SecretをBOMが代弁しない。

**Product境界**：#951の既存Resolver/Conformanceを唯一のOwnerとし、#3267/現在Draft #3297はその成果を使う。Traitの署名/型一致、Build Artifact、Product Functionでの実Invoke、現在のHost Grant、業務Owner受理は別資格。Trait追加によって次段T1の新しいHard Gateを一律追加しない。原子的Traitの実装検証は未実施、二つの類似Issueに第二Resolverや共通enumを実装しない。

### 14.5 ORX-27〜34：独立Expectedの追加、既存main成功を非実施へ戻さない

| ケース | 既存Product入力差分 | 独立Expected・保証上限 |
| --- | --- | --- |
| **ORX-27** | mainでCLI9応答を受領、Function/Business/Ruleは未観測 | **T0.5のpartial・exploration-only限定PASS**。全設計読取やAI T1成功には昇格しない（TEI #3262/#3284）。 |
| **ORX-28** | validateはRoot欠落なし、workspace-filesには未知Root | 現main Gateはblocked。未観測を空集合とみなさない（TEI #3296）。 |
| **ORX-29** | 受領済JSONの途中切断・重複escaped key・NaN・終端欠落 | 既存LoaderのローカルByte負例で拒否（main実証）。**実DSH Tool delivery自体の攻撃試験ではない**（TEI #3296、TAI #168）。 |
| **ORX-30** | Context incompleteだがAIがline_number=0の新負例を提案 | 候補提示はprovisionalで可。実Source/Required/独立Expectedと現Targetが揃うまで新Caseのqualified採用は禁止。T1実行はNOT RUN（TEI #3273/#2514）。 |
| **ORX-31** | 合成Comparator72/72だがOSで別Lane/Holdoutが読める | Comparatorの限定PASSを認めつつ、正式4Session比較は0/4適格を維持。外部G0/G1/G2を既存Runbookで検収（TAI #168/#488）。 |
| **ORX-32** | 旧DraftがWorkbench/BOM両方をRQ-035と呼ぶ | mainのWorkbench RQ-035を保持しBOM側DraftはRQ-036。旧#3269はclosed/unmerged、現候補#3297の資格を個別検収（TEI #3267/#1119）。 |
| **ORX-33** | BOMの署名付き自己申告Check PASSを別Attemptから合算 | Source/Artifact/Scope/Expected/Attemptが合わなければ拒否。合ってもsynthetic reported-pass≠実Trusted Run/Qualified BOM（TEI #3297）。 |
| **ORX-34** | Trait manual-requiredが欠落、またはImpl存在だがTarget Conformance未観測 | 欠落はunfulfilled、実装宣言だけならunverified。BOM/CLI/Studioが現在Host Grantや業務意味を自動認可しない（TEI #3278/#3279）。 |

### 14.6 価値実現計画へ入れる優先度

**P0、既存mainの実測を再利用**：TEIのT0/T0.5局所証拠、TAI合成Comparator、SUI/SHO固定RawのProducer/Readerを別Laneの限定PASSとして表示。次は一Ruleのtyped必要Closure→AI新Candidate→既存Scenario実Run・独立Expected。AIの指示回数/人手の訂正時間/意図しない誤allow/過剰unknown/外部Disclosureを別々に計測する。

**P1、組合せの同一性を次の横断反証へ**：TEI #3297のRead-only witness auditを実#951/#1016 Lockと実#1180 Scenarioへ段階接続。Traitを後付けタグにせずFulfillmentの必須Missing診断へ。現在のContextには観測できないRequired集合が残るため、Product資格・Verified BOMは継続保留。

**P2、独立Consumer/Hostの真の実観測**：SUI実Producer→SHO実Readerの同一Attempt File handoff、TEI #2586実Function/Provider、EKI実Result Body、実Host read-deny/送出/Receiptを、必要な個別Claimでだけ接続する。外部Skill H2/H3は既存Task/Tool/Expected固定と比較適格を優先。T2、T3 SelfBuildや全OS/DB対応は最初のT1をブロックしない。

**現時点の非達成**：新しいT1でAIが未見Ruleを生成・独立Holdoutを正答した証拠、Typed設計情報の全Required closure、外部G0 Read deny／G2 Reply実全受領、Verified BOMの実発行、Trait Product Fulfillment、横断E2EとOwnerの意味・価値受理はNOT RUN/NOT PROVEN。mainへの#3296統合と実CIの限定PASSは達成済みとして保持する。


---

## 15. 2026-11-07 実証基線：既知T1-A実走とRequired Rule閉包

**位置付け**：他Productの最新実Source/Issue/固定main CIに基づく§13〜14の状態更新。設計提案と実製品成果、局所CIと同一Attempt横断受入を分離。新しいPacket Reader、Scenario SSOT、Test Oracle、Authority、共通Runnerは作らない。

### 15.1 T1-A：予定されていた新規候補を実CLIで実行できた

[TEI merged PR #3304](https://github.com/hat47x/tei-platform/pull/3304) / [統合後main CI #42378271383](https://github.com/hat47x/tei-platform/actions/runs/42378271383) により、既存の固定Scenario6 Stepの原本を変更せず、一時コピーへ行番号0のCandidateを第7 Stepとして追加。実TEI CLIのscenario verify→generate→check→generated-pinned runで、行番号正数だけnot-satisfied、数量・一意性はsatisfiedを独立Expectedに照らし確認。偽Expected・偽Fixture・古いPinの3実CLI負例も拒否した。

これは**T1-A：既知の未実行Rule境界をCandidate化し実行・判別する限定到達**。旧§13〜14の「新行番号0 Caseは未実施」はその記録時点の履歴。現在の実験基線として未実施と書き戻さない。一方**T1-B：Agentが未見Rule/Obligationを独立Holdoutを見ずに発見し、入力差分を提案したか**は未実施。既存[Draft #3273](https://github.com/hat47x/tei-platform/pull/3273)のCaseを読み返しただけなら新規発見の価値として採点しない。Design Contextはpartial / exploration-only / qualifiedTestGeneration=falseであり、正式Scenario正本の追加・Owner受理も未実施。

[merged PR #3299](https://github.com/hat47x/tei-platform/pull/3299) / [main CI #42373611474](https://github.com/hat47x/tei-platform/actions/runs/42373611474) では、実Workspace CopyのSource型変更とPlugin Lock byte変更によって旧Pinned Scenarioを拒否する限定実証も成立した。ただしA→B→Aで元Source byteに戻るとPinは再成功し、中間の変更不存在、Owner再受理、現在Host Grantや実Plugin Loadの証拠にはならない。

### 15.2 TT-56：正しいJSON・同FingerprintでもRequired Ruleは失われ得る

[TEI Draft #3326](https://github.com/hat47x/tei-platform/pull/3326) は現9 CLI ReplyのCatalog/Source Index/Loaderと独立固定の公開Validation3 Ruleを照合する候補。正常Schema/同FingerprintでもRule/Relation/Role/Source Pathが欠落する7負例と、非必須Subject省略で過剰拒否しない正例を提案する。[別Draft #3324](https://github.com/hat47x/tei-platform/pull/3324) はinspect-validationを実CLIに1件追加し、単一RuleのCanonical Operator/Attribute/Source Roleまで照合する候補。**どちらも未統合・新規exact-head CI未確認**であり、説明上の8 Controlsをmainの16件へ足して実証済みとしない。

両Draftとも同じcontext_gate.py・同じWorkflow・同じ横断計画を編集する。これを別Reader/別Required正本の二重実装へ発展させない。#3262/#2514がOwnerとして、(1)独立Requiredの必要集合、(2)実Source/Loader/Definition Relation、(3)正常な非必須欠落の不必要な拒否を避ける正例、(4)追加inspectが本当に必要な意味属性、を比較。まず既存9 CLI応答で検出できるRequired欠測を検証し、それだけで判定できないRule属性に限定して10番目のinspectを採用するか決める。Draftの競合はOwner決定待ちであり、独断でPRを閉じない。

### 15.3 CLI Identity・Surface契約・実作用を一つに畳まない

[TEI Draft #3311](https://github.com/hat47x/tei-platform/pull/3311)等に、Workspace manifest identity、commandsの引数値・型・既定値、viewの名前付き出力効果が実CLIへ結び付く進展がある。ただし**現在の全CLIが同じIdentity列を返した実証ではない**。model catalog/inspect/trace/validate/workspace-filesの候補実装と、source-index/knowledge-*の未対応、別Workspace、実Readerがその列を消費する経路は個別に検査する。

Advertised read-onlyと実際の- execute付きFile書込み、OS Read-deny、実Source名とmanifest fingerprint、Harness Tool Replyの全Byte到達は別の命題。契約の自己説明が豊かになればAIの指示回数は減らせる可能性があるが、現在Grant、Source意味受理、実外部送出・元Result Body完全性は自動確定しない。

### 15.4 SHO一括Runnerは実装済みだが目的の一File HandoffはSKIP

[SHO Draft #21](https://github.com/hat47x/sho-composer/pull/21)はtest-onlyの一括Runnerを追加し、SUI真正Checkout HEAD、Frontend実Path/Tracked Clean、354byteの固定SHA、SHO CLI Reader/Parser、Private Temp File cleanupを一試行で確かめる入口を用意。[CI #42377986797](https://github.com/hat47x/sho-composer/actions/runs/42377986797) / [Push #42377982763](https://github.com/hat47x/sho-composer/actions/runs/42377982763) ではUbuntu/Windows各**20 PASS / 0 FAIL / 1 SKIP**。偽Checkoutで偽Producerを起動前に拒否する限定負例PASSを認めるが、**1 SKIPは真正SUI実Producer→SHO実CLIの一File本体**。Runnerが存在・CI成功しても実同一Attempt Deliveryにはならない。

[SHO Draft #22](https://github.com/hat47x/sho-composer/pull/22)はPOSIX writerなしFIFOとsymlinkへのOpen前ハングを、限定nonblocking Openとfstatで拒否する修正。Ubuntu実CLI17/17、Windows16/16＋POSIX固有1 SKIP（[CI #42373230247](https://github.com/hat47x/sho-composer/actions/runs/42373230247)）。Windows Named Pipe・Path TOCTOU・実Writer/Editor保存再開/Owner受理まで保証しない。

### 15.5 ORX-35〜40：新しい局所成果を誤って横断Outcomeに昇格しない

| ID | 独立した反例とExpected |
| --- | --- |
| **ORX-35 既知候補とAI未知発見** | T1-A第7 Stepの実CLI成功は認める。AIが既知#3273を再掲しただけならT1-Bの新発見・盲検価値は未証明。 |
| **ORX-36 同FingerprintのRequired Rule欠落** | JSONは妥当でも独立RequiredにあるRule/Relationが実Projectionから抜ければpartial/blocked。Draft #3324/#3326はOwner収束・実CIが必要。非必須Subject欠落の正例を不当に止めない。 |
| **ORX-37 A→B→AのPin再成功** | byte一致で旧Plan再成功はあり得る。中間変更なし・Source受理/現在Grant・実Build資格とは別。Source/Lock変更時の拒否はmain実証済み。 |
| **ORX-38 CLI説明だけのRead-only** | commandsのSurface記述とview -executeの名前付きFile効果、別Workspace Manifest、OS読取とTool完全受領は別観測。 |
| **ORX-39 Runner準備と本体SKIP** | 偽Producer拒否PASSを認めるが、真正SUI→SHO実One-fileの同一AttemptのReader ReceiptはNOT RUN。 |
| **ORX-40 POSIX FIFO回帰とHost全体** | Linux実CLIの特定FIFOを拒否してもWindows/特殊File/Path交換/実Writerは未実証。 |

### 15.6 次の順序・価値判定

1. **TEIの最短経路**：T0.5/T1-Aを再発明せず、TT-56の並行Draftを一つのRequired/実Consumerへ収束→一RuleのSource/Relation/Operatorの適格観測→Agentが未見Gapを提案するT1-B→既存#1180で独立レビュー・実Pinned CLI。全Function/Providerを前提にして局所read-only試験を不必要に止めない。
2. **SUI/SHOの独立経路**：偽Checkout拒否・Cross-OS固定Rawを保持し、真正SUI Checkoutからopt-in Runnerでnon-skipの同一File実Reader/独立SHAを1回観測。その後にのみWriter Save/Restartや原出典、SEI/OKF、二次Recipient Grantを別に検証。YICの全Activityへ一律前提化しない。
3. **Plugin/外部Harnessの独立経路**：BOM RQ-036 Draft #3297、Atomic Trait、CLI metadata、Go外部Module opt-in、HTTP Graphを、必要なConsumer ClaimのWitnessとして限定参照。TAI #168のG0実OS read-deny→G1送出→G2 Tool全Reply→新H2/H3四Slotの比較資格（現0/4）を優先。新共通Host/Registry/Verifierを設けない。
4. **価値判断**：Userの指示回数、真の未カバーRule判別、正常Caseの過剰拒否、実取得Sourceの増分・開示、修正の手数、CIと実行待ち時間を別指標にする。技術的局所PASSからOwnerが望むOutcomeを直接推論しない。

**状態**：T1-Aの実CLI Case判別と旧Source/Lock Pin拒否は**mainで限定達成**。TT-56は競合するDraft段階、HandoffはRunner防御の限定PASSで本体SKIP、外部H2/H3は比較適格0/4。未知GapのT1-B、Product全Required Closure、真正One-file Reader受領、実BOM/Host、Owner Meaning・利用者価値は**未実証**。

---

## 16. 2026-11-08 横断統合：欠落の意味を契約別に判定し、実消費の最短ループへ

**位置付け**：2026-11-08未明のTEI／TAI／SUI／SHOの実Product・限定CI・既存計画を突合した横断価値研究。§15のTT-56『未収束』は履歴として保持するが、現行状態はこの節と冒頭の基線を正とする。新共通Missing enum／Resolver／Proof Engine／Runner／Authorityは設けない。

### 16.1 同じ「欠落」を同じ意味で処理しない

**新しい横断設計原則**：欠落の判定は、対象の**契約上の必須性**と観測の**取得・開示範囲**の二軸で行う。『任意項目が無い』と『必須情報を実際に読めなかった』は逆方向のケース。安全性だけを理由に全てdenyすると正当な利用可能性を失い、便利さだけを理由に全てdefaultすると虚偽の完全性・対象取り違えを起こす。

| 対照 | 正しい局所判定 | 禁止する昇格 |
| --- | --- | --- |
| 契約でoptionalな端点種別が省略・null、端点IDは一意解決可能 | 当該Pilot Contractの解決規則でEdgeを受ける | 任意Kind省略をGraph全域のNode Type非存在やnull一般則へ拡張しない |
| required RuleがCatalog/Source Index/Loaderから抜ける | 独立Requiredとの不足を返す | JSONが正常・Fingerprint一致を『Ruleが無い』や『全件取得した』としない |
| Scenario一覧がpartial、要求Stepが一覧にない | そのStepはnotObserved、実観測済み別Stepの局所結果は維持 | untestedConfirmed／全体Coverage0や全件Coverage100を作らない |
| 空集合Targetかつhandoffが未確認 | 独立Empty証拠があっても受領の要件は別、当該PolicyのHoldsを保留 | 空集合を理由に実受領済み・Effect済みとしない |
| Capabilityがselected、Providerは未呼出 | Selectionの事実だけ保持、実Invoke・Effectはunknown | Selected/宣言されたTraitをFulfilled/Host Grantにしない |
| requirementsの成功resultが空のJSON配列 | 型に合う成功応答として受領し、その内訳・Required欠落を別比較 | 配列≠objectをTool failureと断定、空配列を完全性へ昇格しない |

この区別は独立の『Global Missing State』を増やさず、各Productの現Contract/Required/Consumer Scope/Receiptに相対化して評価する。Source非公開ならその存在件数を外部Audienceへ漏らして診断しない。

### 16.2 TT-56は既存単一Consumerへ統合済み（Product局所PASS）

[TEI merged #3354](https://github.com/hat47x/tei-platform/pull/3354) が、旧競合Draft #3324/#3326を同じ `context_gate.py` に**一つへ収束**。Source Indexの全件・Focused Inspectを加え、**11実CLI read-only Reply**について独立Required3 Rule、Canonical positive/attribute、Relation Parent、Definition role、SourcePath/Artifact/Fingerprintを照合した。正常JSONかつ同FPでもRequired Rule/Relationだけが省略された場合を拒否し、非必須Subjectの省略は過剰拒否しない。

[PR exact-head CI #42391707962](https://github.com/hat47x/tei-platform/actions/runs/42391707962)はcompleted/success。既存16＋独立Requiredの7拒否・1正常＋Canonical/Relation/Sourceの8拒否＝**32件の局所合成Consumer対照**が成功。既存Pinned ScenarioとT1-A候補も同CIで検証した。局所C0相当10.0%、C1未計測。32を実コードMutant kill数や実Product欠陥数とは呼ばない。旧Draftはclosed/unmerged、別Gate/Readerを実装しない。**統合後main Push CIの個別run**は本照合では別証拠として未確認であり、PR exact-headのsuccessをそこへ転記しない。

この到達は最初の公開Validation Scopeに限定。docs/plan Markdownは[TEI #3346](https://github.com/hat47x/tei-platform/issues/3346)でmanagedFilesにあってもreadByLoader=false、意味読込ではない。[#3345](https://github.com/hat47x/tei-platform/issues/3345)のview局所FPとWorld FPは対象範囲が違い、[#3347](https://github.com/hat47x/tei-platform/issues/3347)のJSON result shapeもCommand依存。これらを『Requiredなし』や『完全』へ推論しない。T1-Bの前に全部のMarkdown Parserを導入するのではなく、対象Task/Ruleに必要なSourceだけを明示し、不足を具体的に返す。

### 16.3 TAIのEdge Pilotは『許される欠落』の実正例

[TAI merged #537](https://github.com/hat47x/tai-pleroma/pull/537)はpilotの `edge-record` v4で端点種別をoptionalにし、欠落・片側null等を含む7 Fixture、投影→合成の24ケース／90段を限定PASS。IDからCard/Islandが一意に解決できる場合はEdgeを合成し、存在しない端点は拒否。曖昧な端点IDでは推測でcardを選ばない。**当該Pilotではoptional Kindの明示nullも省略へ畳まれる**が、一般のDomain NULL/欠損/非開示に同規則を強制しない。

つまり、旧Contractで必須としたKeyを常時要求することは『厳密』でなく、合法なCard→IslandのEdgeを捨てて利用者価値を減らし得る。一方、合法な省略だからといって関係ID・向き・多重性・ScopeのWitnessを省略してよいわけではない。Assemblerの内部分類結果が実Consumerへ同じ意味で配送されたか、元Source Disclosure/Owner Meaningを満たすかは別実証。

### 16.4 Processを駆動した実体と、単なる同Byte生成を分ける

[TEI #3360](https://github.com/hat47x/tei-platform/pull/3360)のSelf-build Referenceでは、外部Go Seedで作った自分自身を再構築可能な**参照Driver**を対象に、Stage1 ArtifactをStage2 Invokerとして実起動し、Stage1/2 Artifactのbyte一致・同Child/同引数をローカル実試験で観測。`l3Claimed=true`は**この参照Driverの一試行に限定**する。これはStage1の実生成物が駆動側Processに使われたという重要な新証拠だが、対象は**cmd/teiではなく**、TEI本体G4 L3資格は依然UNQUALIFIED。自称Invoker digestの検証と実Process image一致も別[TEI #3362](https://github.com/hat47x/tei-platform/pull/3362)で扱う。正しいbyteのArtifactを外部Processで作るだけの収束と実再入場を混同しない。

### 16.5 Plugin-first／Studioは最初の実Consumer選択へ収束させる

[TEI main #3337](https://github.com/hat47x/tei-platform/pull/3337)ではDeclared/Selected Capabilityをread-onlyに列挙できる。途中で選択集計の技術名とCapability IDの比較規則が改まり、historical unselected 6から別revisionの4へ変化したが、元分母・判定規則を無視した改善率として扱わない。**Package選択≠Capability Binding≠実Provider Load≠Invoke≠現在Host Grant**。一つのread-only Inspectorを、既存#951/#1016のSelected Contract/Provider→実CLI呼出→Studio Consumerへ接続する最短縦断を優先する。

[TEI Draft #3371](https://github.com/hat47x/tei-platform/pull/3371)ではStudio Host Factoryが選んだInspectionServiceへ明示的に委譲し、未提供・誤Subject/Schema/Effect/FP/Canonicalや不正JSONでfail closedする実装・試験候補がある。ただしFactoryと#951 Resolver/実Build/CLIの結合、2 Consumer実観測、現Wails/OS Grantは未接続であり、DraftのSourceだけからProduct Plugin-firstを完成扱いしない。

### 16.6 ORX-41〜48：『許された省略』『未取得』『実証済み』の混同を反証

| ID | 二世界／判定条件 | 実証上限・既存Owner |
| --- | --- | --- |
| **ORX-41 必須RuleのSilent Loss** | 同一FP/妥当JSONでもRequired3 Ruleの一部だけ欠落→不足。非必須Subject省略は正常 | TEI #3354の局所32合成対照PASS、全Required/意味は不明 |
| **ORX-42 Optional Kindの過剰拒否** | Pilot EdgeでKind省略/nullだがEndpoint一意→Edge保持、ID曖昧→拒否 | TAI #537投影→合成24/90限定PASS、Downstream Deliveryは別 |
| **ORX-43 部分ScenarioのFalse Untested** | partial目録にStepが見えないが、局所実Receiptはある | TEI Draft #3365のTT-105/106。新7対照のexact-head CI/正式Owner採用は別 |
| **ORX-44 空集合と受領未確認** | Targets=[]、EmptyJustified=true、HandoffConfirmed=false | TEI merged #3353はHoldsをUnverifiedへ限定修正。実Host受領はなおCaller申告 |
| **ORX-45 Selected Traitと実Invoke** | Capability選択だけ成立、Required Trait/Provider実装は無い | TEI #3337/#3368/#3278。Selection局所PASSを実Invocation/BOMへ昇格しない |
| **ORX-46 Reference L3とTEI G4** | Self DriverのStage1 ArtifactがStage2を駆動して同Byteを出すが、cmd/teiは別対象 | TEI #3360の参照実試行を認めつつ本体G4未資格 |
| **ORX-47 正常ArrayとContext欠落** | requirements result=[]は正常shape、別SourceのRequired Ruleは不足 | TEI #3347／Draft #3370。未申告shapeをobjectと推測しない |
| **ORX-48 Host選択と実Consumer不一致** | Studio選択Inspector=B、実呼出はbuilt-in Aへfallback／Result誤Contract | TEI Draft #3371はHost側明示委譲の候補。実CLI↔Studio↔Providerは未実証 |

### 16.7 実行計画の変更（最小依存／最大の判別力）

**P0-A：既存mainの到達を保存**：#3354局所Required Rule/Relation対照、#3304のT1-A候補実走、TAI #537のoptional Kind正例、TEI #3360参照Driver局所再入を別資格で記録。PR CIとmain Push CI、Reference Driverとcmd/tei、内部解決と実Consumerを各々独立に採点する。

**P0-B：二つの不足だけに絞った本当の次の試験**：(1)TEI #3262/#3223/#3273で独立Required・Source読取Scopeを適格な一Functionに閉じ、Unknown Test ObligationのAI盲検提案T1-B→#1180実Pinned→#2514独立Expected・正当例の非過剰拒否、(2)SHO #21で実SUI真正Checkout→一File→SHO実CLI受領をnon-skipで一試行。新Reader/Runner/Gateなし。

**P1：実利用資格を確かめる横断一辺**：Plugin Inspector一件のSelected Capabilityと実Provider Invoked/CLI→Studio 2 Consumer、またはTEI #2586の実Function selected SQL→physical Provider Read→Contextのどちらか**先に実接続できた一辺**を比較。Source/Meaning/Grantを無関係なLaneでHard Blockにせず、実Effect/RecipientへのClaimを増やすときだけ必要条件を要求する。

**価値判定**：欠落を理由に合法なEdge・局所成功Step・許可済み調査を不当に拒否しない度合いと、未取得Rule／未Delivery／未Invokeを誤って完了扱いしない度合いを**両方**測定。必要な追加Source Reader/独立Witnessのコスト、AI指示数、確認負担、情報開示、修正手数も別に記録。TAI #168のH2/H3比較は現0/4適格であり、G0/G1/G2→新4独立Sessionの既存Exitを変更しない。

**未実証**：本節のORX-41〜48のYIC同一Attempt横断実験、T1-B未知Rule盲検発見、TT-105/106の実採用、SUI→SHO一File本体、cmd/tei本体G4、CLI/Studioの同じ実Provider二Consumer、実BOM／本番Host Grant、Owner意味・利用者価値受理はNOT RUN/NOT PROVEN。

---

## 17. 2026-11-08：同一性の分離と実際に使える成果への接続

**位置付け**：§16の実証更新後に確認したmain実CLI、cmd/teiのセルフビルド、SHOの実File試験、外部Providerの負例候補、CLI/MCPの契約差を統合する。相互に独立したProductの限定証拠を横断E2Eへ合算しない。Core/Authority/Registry/Runner/Tester/Canonicalを新設する設計判断ではない。

### 17.1 「同じ」の対象を取り違えない最小証拠

モデルの内容が同じ、Sourceの原byteが同じ、実Fileが同じ、Processが同じ、権限を持つConsumerが実受領した、業務上の意味や価値が同じ、はそれぞれ異なる命題。用途別のClaimに対し、必要なWitnessのみを参照する。YICへ新しい全製品共通IDを導入するのではなく、各Ownerの既存World FP、Source Index/Provider Source occurrence、実FD/path、実Artifact/Invoker、Grant、Outcome/Owner受理を**比較時の列**として並べる。

| Claim | 主な必要観測 | 認めないショートカット |
| --- | --- | --- |
| Meaning/Modelが同じ | 同じScopeでのWorld/Rule/Version、Accepted Meaningの適用範囲 | 同じlabel/pathを同じ業務対象とする |
| 出典が現在も正しい | 原Source（外部Providerを含む）の実Byte/Revision、Readerの実受領、必要Source closure | World/Consumer Source Indexの一致だけで外部原文の不変を断定 |
| 実際に保存・再読取した | 元Source FD・実出力FD・実Path・byte、部分作用、必要に応じ現在CAS/fence | SHA同一＝同File、同File＝更新履歴なし、readback＝durable publish |
| 生成したプログラムが駆動した | 実Stage1 ArtifactとStage2 invoker image/argv、Child、BuildPlan/Intent解決 | Artifact byte一致＝セルフビルド全成立 |
| Consumerが利用できる | 実Provider/Tool Adapterの選択→Load/Invoke/Result、現Audience/Grant | 説明・宣言・ReaderローカルCI・送信ACK＝現在資格 |

証拠は全てのClaimで一律必要ではない。例えばSourceだけのLF変更は、バイト同一性を壊しても特定のSemantic Worldを変えないことがある。歴史的な実行Receiptを保存したまま、現在の引用・再配送資格だけを必要範囲で再照合できるようにする。Source fingerprintとmeaning fingerprintを単一Hashへ畳まない。

### 17.2 TEI：Source-only変更を本当に見分けられる範囲

[TEI merged #3477](https://github.com/hat47x/tei-platform/pull/3477)の[exact main push CI #42461058083](https://github.com/hat47x/tei-platform/actions/runs/42461058083)はcompleted/success。既存**11 read-only CLI Reply／32 Context判別Control／Design Context Packet9負例／6 Pinned Scenario／既知T1-A Candidate**を保持し、Context取得時のWorld/Source Index FPをScenarioの候補生成前と実Pinned Run後の実CLI `model catalog`と再比較。`validation.tei`末尾LFのみ変更した合成実Workspaceでは**World不変、Source Indexのみ改版**となる。WorldのみPinした旧Scenarioが通っても、Context Consumerが旧Source Indexの継続使用を拒否することを実観測。この一Workspace・一Callerの限定した時点差検出は実装済みであり、§16の『Source-only drift検査未実施』へ巻き戻さない。

ただし[新Draft #3479](https://github.com/hat47x/tei-platform/pull/3479)は、**importした外部Providerの原Source**について別の観測盲点を指摘する。ConsumerのWorld/Source Indexの両FPが同じでも、Provider raw Byte/`LocateImportedSource` occurrenceが改版している反例のGo試験候補を置いた。現在の外部Source Snapshot/Provider Reader・インポート時点の閉包は未実証で、このDraftの新focused Go test/CI完了も未確認。**同一Workspaceでの#3477のPASS**を他Providerや複数File原子的Snapshotへ外挿しない。

最小修正案：Consumer Contextへ巨大な第二Source Indexを複写せず、用途に必要な外部Provider Source occurrenceのRef/Revisionを、既存#2743/#3262/#951/#1163へ関連付ける。独立Expectedは(1)World同じ・Provider Source異なる、(2)World/Sourceとも同じ正常対照、(3)Providerがpermission denied/partial、(4)A→B→Aで現Byte復帰でも過去履歴を再構築しない、を区別する。取得していない秘密SourceのID/件数は未許可Recipientへ漏らさない。

### 17.3 TEI自身のL3を現在値に更新：実Process再入とL2意味解決を分離

§16は参照DriverでのL3限定成立までを記録したが、その後[TEI #3440](https://github.com/hat47x/tei-platform/pull/3440)で対象を**実cmd/tei自身**に変えた再入をWSL2 Ubuntu/Go1.27.3の限定実験で観測し、[台帳更新 #3447](https://github.com/hat47x/tei-platform/pull/3447)に記録した。Stage1で生成したTEI実行ファイルがStage2 invokerとなり、Child・引数・Artifactを別列で照合した。入口の `l3Claimed` は常にfalseで、検証値の照合から限定的に再入場を判断する。**cmd/tei自身のL3形状の局所実証は達成、L2（TEI標準Build Intent/Graphから実Buildを解決）は未成立、G4全体はUNQUALIFIED**。旧『cmd/tei L3一切NOT RUN』は現在値ではない。

[TEI #3463](https://github.com/hat47x/tei-platform/pull/3463)では自己Build CLIの前提/出力no-clobber/実Child Invocationを検査。[新Draft #3476](https://github.com/hat47x/tei-platform/pull/3476)ではIntent宣言JSONと、明示Supply Verifierの結果がfalseならChild起動前拒否する限定Go/WSL実験を実施。**Intentはresolved=false**であり、Supply VerifierのSchemaと実行を確認することは、供給PublisherのTrustや標準BuildGraphの実導出ではない。`qualified=false`維持。L3とL2を便宜的な大小順ではなく、再入場の実観測／意味からBuildへ導く資格という**別の受入軸**として報告する。

### 17.4 SHO：Raw Byte一致に加え、元File・出力File・保存履歴を区別

[SHO Draft #25](https://github.com/hat47x/sho-composer/pull/25)は、test-only Working Copyを`wx`で新規作成→close→別FDで再Open→実G1b CLIでReadbackする限定のG2-W1を実装。特定のtested HEAD `eb12e0cc2eff01ef0be9270c3a0a6adb77b3a09a` に対する[Ubuntu/Windows CI #42461729731](https://github.com/hat47x/sho-composer/actions/runs/42461729731)はUbuntu20/20、Windows19 PASS＋POSIX専用1 SKIPの限定成功。現Draft最終HEADへ成功を無断継承しない。

独立反例W15〜20は、**同じ原byteだが元Sourceが別File、Source A→B→A、OutputがReadback前に別Fileへ差替えられる（同byteでも）、Output A→B→A、File Identity未観測**を分離した。比較可能なFD dev/inoで差を検知できても、OS間・FileSystem間・inode再利用・Path raceでは現在の同一性を確定できない。Byte Readbackの局所成功を正式Editor Save、no-op write0、atomic publish/fsync、衝突CAS、Owner受理、SUI→SHO実Handoffへ拡大しない。効果が一部起きた場合は`needs-reconciliation`を保持し、無条件削除・再試行を行わない。

また、[SHO Draft #27](https://github.com/hat47x/sho-composer/pull/27)の前提となる公開TEI側[Actions #42461670105](https://github.com/hat47x/tei-platform/actions/runs/42461670105)では、公開TEIのCI tokenから非公開SHOをcheckoutできず**Reader起動前に拒否**された。これはSource Grammar FAILでなくRepository Grantの境界。非公開SHO側から許可済み公開TEI Fixtureを固定版で読取る逆向きCIを提案し、公開TEIにprivate repo権限や秘密PATを配布しない。#27実Readerの同一File CIは新たな別資格。SHOの単独編集・保存を別製品の実装完了へ依存させない。

### 17.5 CLI/MCP・SUI/SEI：有用な後続構想は現P0へ割り込ませない

[TEI #3420](https://github.com/hat47x/tei-platform/issues/3420)/[#3458](https://github.com/hat47x/tei-platform/pull/3458)はCLIと参照MCP Adapterの`validate`で、同じ意味エラーがCLI側failureなのにMCP側`isError=false`となり得る差を実コードで特定し、共通Validation Reportと限定Go/Windows回帰を追加。**共通構造/実Adapterの局所PASS**と実stdio/外部Harness受領、実Host Grant・Client Reactionは別。Transportを越えた最小APIの必要性は認めるが、WebServerや新共通認可を最初から導入しない。

[SUI #3400](https://github.com/hat47x/sui-sensemaking/issues/3400)の違和感→関係発見→理解の変化という一次価値と、[#3401](https://github.com/hat47x/sui-sensemaking/issues/3401)の異種Source/対象/時系列/状況理解という長期的価値を**別の評価軸として併存**させる。AIが関係候補を得たことと、Ownerが意味を受理したことを混同しない。[TEI Ontology/Decision Twin #3475](https://github.com/hat47x/tei-platform/issues/3475)はO0の比較・独立Expected設計のみ現在可能で、本格Twin/外部Sim/SEI判断移譲の実装は**TEI全体Self-buildとSUI基本機能の完成後**へ保持。こうした構想は利用者価値で再評価し、今は既存製品のRead/Save/CLI/Scenarioの縦断実証を優先する。

### 17.6 ORX-49〜56：実成果・未観測・必要な追加Witness

| ID | 相反する世界／判定 | 受入と状態 |
| --- | --- | --- |
| **ORX-49 同World・Source-only差** | `validation.tei` LF変更でWorld同一・Source Index異版 | #3477 main実CLIは旧Context拒否を限定達成。古いScenario Run成功をSource現在性へ昇格しない |
| **ORX-50 同Consumer FP・別Provider原文** | 外部Imported Sourceだけ改版しConsumer World/Indexは同じ | #3479 DraftのFocused反例は実CI未確認。Provider Occurrenceを別Witnessとして要求、全Consumer失効を無条件に起こさない |
| **ORX-51 実cmd/tei L3だがL2なし** | Stage1 TEI自体がStage2を駆動、Intent解決は未成立 | #3440局所L3再入を認め、G4 UNQUALIFIED・L2未成立を別列で報告 |
| **ORX-52 Intent宣言/供給Verifierと実資格** | JSON digestは取得できるがBuildPlan未解決、Verifier指定なし／未承認 | #3476 Draftの局所実拒否を限定認め、resolved=false・qualified=false。Trust/Pub/Targetは未認定 |
| **ORX-53 Source同byte/別FileとOutput交換** | Working Copy再読取はbytes一致、元/出力パスは別実File | SHO #25実CI W15/W18はFD identity差を限定検出。FD identity不明ならunknown。Editor Save/Publishの受理なし |
| **ORX-54 Source/Output ABA盲点** | A→B→Aで同Byte・同FD Identityに戻る | SHO #25 W16/W19は変化履歴を判定できない。CAS/fence/actual historyがなければ未証明 |
| **ORX-55 Public→Private権限拒否** | 公開TEI CIが非公開SHOをcheckoutしようとしてFAIL | Repository Grant不足として分類。Private側CIに公開Fixtureを取り込む案は別Draft #27で未検証 |
| **ORX-56 CLI/MCP意味失敗の齟齬** | CLIが意味Validation失敗、MCP Adapterが成功扱い | #3458の共通Report局所試験を評価し、実外部MCP/Clientの同版E2Eは別検収 |

### 17.7 計画への反映と停止線

**P0（今回すでに動いた成果を保持）**：#3477の同Workspace Source-only Context→Scenario版失効、#3440のcmd/tei実L3形状、SHO #25のG2-W1バイト/FD両系統の局所テストを、同一Attempt・対象・Revisionを明記して評価。計画上の旧NOT RUNを歴史として残しつつ、次のOwner表はこの現在実証を基線とする。ただしPR exact-head／main／ローカルと、初回失敗→修正後PASSを混合しない。

**P1（最短の価値ループ）**：TEIではT1-Bの未見Gap/独立Expectedを一件、並行して#2586のFunction selected Query→SQL byte→Bind→実Provider Rowset/Consumerを一件。SUI/SHOでは真正SUI Producer→一File→SHO Reader non-skipと、SHOの正式G2 Writer Save/Restartを別ゲートで各一件。Sourceが足りなければ局所的にpartialと返し、許可された正常操作まで不必要に停止しない。

**P2（資格の範囲だけ拡張）**：TEI #3479の外部Provider Source-only反例を現main固定で独立試験し、CLI/MCP validateの失敗契約、PluginのSelection→実Invoke→Studio/CLI同一Consumer、BOM exact tuple、cmd/tei self-buildのL2意味解決を、独立Owner・既存Product入口で検証。SUIの高度統合とTEI Ontology/Decision Twinは長期研究のO0に留め、現在の業務P0/SUI一次価値をブロックしない。

**価値の分母**：同じ内容が何回見えたかではなく、必要な一次Sourceへ戻れて誤判断を防げた件数、原本/Working Copyを失わず保存再開できた件数、AIが未知の不足を適切に発見した件数、合法な省略・部分成功の過剰拒否、追加Reader/確認時間・情報開示費用を独立に測る。未実施試験の成績を0点とせずunknown/NOT RUN、必要ない機能を必須化した失敗も測る。

**未実証**：YIC一つの実横断Outcome、外部Imported Provider Snapshot閉包、TEI L2/G4全資格、正式SHO Writer/Store CAS、SUI→SHO真正One-file、T1-B、実Function Provider Read、外部Harness比較適格（現0/4）、横断ストレージ物理統合、実SEI Decision/Twin/Simulation、Ownerの意味・価値受理。研究計画と各Draftは実運用認定ではない。


---

## 18. 2026-11-08：宣言を使える成果へ接続する一辺と、実Reader受領の範囲

**位置付け**：§16〜17で分けたSource Identity/Byte/Process/Consumer Receiptを、実際の業務Function一件の必要条件と、異なる公開範囲にある二製品の実Readへ接続する。新Central Function Registry、万能Predicate、Proof Engine、Host、Transport、Test Runner、Owner Meaning正本は追加しない。検証結果を利用者のOutcomeと呼ぶには、利用先ごとの独立根拠が必要。

### 18.1 TEI #3482は13実CLI・42局所対照をmainへ統合した

[TEI merged PR #3482](https://github.com/hat47x/tei-platform/pull/3482) は既存のContext Gateを再利用し、独立Requiredによって一つのFunction **sales.order.submit** の宣言上の必要情報を検査する。Targetはsemantic-capabilityのinput/output型、application:order_entryのsales namespace利用、3 Validation、sales_core DB requirement、Source IndexのDefinition Role・実Loader Read・実Catalog/typed Inspectを含む。前節の11応答にCapability/Applicationの2つの既存typed Inspectを足して、**13実CLI Reply**を使用する。

[専用CI #42462672188](https://github.com/hat47x/tei-platform/actions/runs/42462672188) はcompleted/success。**従来32＋新しい不足・不正拒否9＋正常の過剰拒否防止1＝42個のtest-only Consumer判別対照**を同じ実TEI Binaryで実行した。既存Context Packet9対照、Pinned Scenario6 Step、T1-A既知候補、World同一/SourceIndex改版の拒否も回帰。[main merge 8ed583790e63b63527c1dd8f8aecc1d6ce6e3260](https://github.com/hat47x/tei-platform/commit/8ed583790e63b63527c1dd8f8aecc1d6ce6e3260)後の[main push CI #42462861657](https://github.com/hat47x/tei-platform/actions/runs/42462861657)についても、bounded-design-context Jobの**completed/successを直接再確認**した。Go局所statement C0相当9.4%は限定選択のみ、C1/全要件/NFRではない。合成対照を実Go Product Mutant kill数や実DB件数へ読み替えない。

ここまでに成立したのは **Function/Capability/Applicationの宣言Sourceと依存を、現在の対象Scopeで限定照合できた**こと。とくにApplicationのuses semantic salesは**Namespace依存**であって、そのApplicationから具体Capabilityの**Call/Invocation Binding**が存在・選択・起動する証拠ではない。sales_core DB requirementは接続要求であって、実Provider Instance/Rowset、Runtime Grant、Write Commitではない。Function execution / query-or-provider-read / host-grant-and-effectは**not-observed**のまま、bounded Function SliceがpresentでもqualifiedTestGeneration=falseを維持する。

### 18.2 最初の欠落一辺をCall Bindingに固定し、Source→Outcomeを小さく実証

次の#2586実Provider Readと#951/#1016 Plugin実Consumerへ進むための、重複しない最小対照：

| Case | 観測対象 | 独立Expected／禁止する昇格 |
| --- | --- | --- |
| **ORX-57 実Invocation不在** | Capability定義・Application uses・Sourceが一致するが、Function Entry/Call bindingは未存在 | Design Sliceはbounded-present、実Invocationはnot-observed。ビルド成果物やDB要求宣言から実Callを推測しない |
| **ORX-58 同宣言別Provider** | 同一Source定義でProviderがunbound／別Instanceを選択 | Declaration資格を保持し、actual Provider load/SQL bind/Rowset/current Grantがない場合、Read/Effectはunknown |
| **ORX-59 追加された正常Refの非過剰拒否** | 必須3 Rule/Sourceは同じで非必須Subjectだけ増減 | Independent Required充足の局所資格は維持。追加Sourceを無条件に全失効させず、新たな実依存があれば選択再評価 |
| **ORX-60 Workbench物理Graphだけの成功** | Provider.IntrospectのFake Catalogから物理FK/Indexは投影可能、業務Relation/Function CRUDは未受理 | 物理観測/現在Grant/実DB Reader/三視点意味受理・Schema Applyを別Claimへ分離。旧#3372はclosed/superseded、現Draft #3486はexact HEAD CI未認定 |

[TEI #2586](https://github.com/hat47x/tei-platform/issues/2586)で重要な「一辺」は、宣言上のCapabilityが見えることから、**実際に選択・呼び出されたFunction／SQL byte・bind → 実Provider Read/Result Grain・Completeness → Consumerへ返ったFunction Data Context**への接続である。まずread-only Browseの現SQLのstatus eq bindと2列Rowsetを実証し、ne・sort/pageの宣言と実効果の差は別負例で検証する。実Writeはその後にAction/Host/Receipt/独立Readbackの資格を追加する。先に新しいQuery/Provider/Authority Hostを作らない。

### 18.3 宣言の二視点がそれぞれPASSでも、実Bindingは別

[TEI merged PR #3485](https://github.com/hat47x/tei-platform/pull/3485) は、E1 Web PlanのRoute/ActionとGo Hostのmethod/path/actionIdという**二つの宣言を、合成Fixtureで別々に変異させて照合する実Testコード**をmainへ追加した。片側のNode/Goローカル適格が他方のRuntime Bindingを保証しない、というPressure。旧[CI #42461546535](https://github.com/hat47x/tei-platform/actions/runs/42461546535)での旧Node/Go構成のPASSは確認済みだが、今回新規のE1-Go相互差を検出するテストの同版CI結果は**本照合では未取得**。Product E1 Source→Go Hostの実選択・実Invoke、Auth Guard、Client Reaction、Commit/202/ReceiptはNOT PROVEN。

これは18.2のFunction/Provider未Bindingと同じ**証拠の形の不足**であり、TEIに共通の巨大Binding Engineを新設する理由ではない。既存Application API ADR-0048、#3274 Server/Client Decision Graph、#1174 Host/Effect、#2514独立Expectedの各Ownerで、**declared pair → selected pair → actual invoked pair → externally observable result**の列を見せる。各Ownerの意味・作用・資格を別々に検収する。

### 18.4 private側のSHO実Readerは公開TEI原文4件を本当に受領済み

前節の「[SHO #27](https://github.com/hat47x/sho-composer/pull/27)実Reader成功未確認」は履歴の状態に限る。**private SHO-owned Draft #27**の初回[CI #42461984903](https://github.com/hat47x/sho-composer/actions/runs/42461984903)は、Readerが四Fileを読んだ後にnode_modules untrackedのclean判定でRed。修正HEAD ec169bf63f5010c3dc5d3389ee4efe2522419775 の[CI #42462172893](https://github.com/hat47x/sho-composer/actions/runs/42462172893)は実Job **completed/success**を直接確認した。公開TEIのPin済み合成K1 Markdown **index/data/functions/business の4実File**をPrivate側の実G1b CLI Readerが読取り、原byte・SHA/限定Link、missing fileと正常0 Linkの区別、Parser版14.3.3を検収した。

この成果は二Repoの**権限を越えてSecretを渡さずに実Fileを読む**限定したK1Rであり、前回§17の「Public TEI→Private SHO Checkout失敗」は権限境界の歴史的Redとして残す。公開TEI CIにPrivate Repo token/PATを付ける必要はない。ただし**OKF YAML Frontmatter正式F0、同一Providerが選択されたK2二Consumer、SUI真正Producer→SHO同一File H1（別Fixture・通常CI SKIP）、SHO Writer Save/Restart、Source/Disclosure/Owner受理**は未成立。K1Rの成功をH1に横流ししない。

### 18.5 ORX-61〜64：実Reader・Transport・Sourceの到達と事業価値を切り離す

| ID | 二世界／判定 | 結果と次のOwner |
| --- | --- | --- |
| **ORX-61 正規Readと意味Parser** | SHO G1bが公開TEI Markdown4 FileのRawを読めてもOKF Frontmatter意味は未解析 | K1R限定PASS。OKF F0/K2/Owner/現在Grantへ昇格しない（SHO #18/#27） |
| **ORX-62 Handoff誤昇格** | SHOが公開TEIの4 FileをReadできたがSUI実Producer H1はSKIP | H1は別の同一Attempt非Skip Readerを要求。両Repo・Fixture・目的の異同を追跡（SHO #21/#27） |
| **ORX-63 Transport Comparatorと実配送** | EKI #786 test-only Comparatorで8負例PASSだが実Adapter Trace未入力 | 実Local IPC/Connect配送・受領/Grant/EffectはSKIP・未実行。Test報告の型一致を配送Receiptにしない（EKI #753/#786） |
| **ORX-64 予定表とOwnerの成果** | TEI 13 CLI/42対照・SHO K1R成功でも利用者のTaskが実完了したか未観測 | 必要なFunction実Read/SHO原稿保存・利用先の受領がない限りOutcome未証明。各Product局所成果を独立に評価 |

### 18.6 改訂した最短の価値実証順と停止線

**現在実証済みとして表示**：TEI #3482 bounded Function declarationの13実CLI・42 Controls（main CI含む）、TEI #3477同Workspace Source-only失効、SHO #27 Private-owned Public Fixture4実File Reader K1R、TEI #3440の自己Stage1→Stage2 invoker局所観測。従来Source-static/Fixture-onlyと混ぜず、対象・Test Commit・利用先と制限を添える。

**次の必要一辺は二つ**：(a) TEIのFunction Call/Provider Read一件と、そのResultが本当にFunction Data Context/Consumerに届くこと。(b) SHOの普通の文書Working Copyから実Writer Save/別Open、SUI起点の必要時に限る非Skip実One-File H1。実Data Source/Consumerを明示し、Source/Meaning/現在Grantは要求された用途に限って追加確認する。AIの未知Gapを盲検で選ぶT1-Bも既存#3262/#2514/#1180で並走。

**長期構想は別**：Ontology/Decision Twinの実装や異種Data Storeの共通サービス化を、最初のFunction Read・Studio Inspector・SHO Raw Saveの前提としない。将来のシミュレーションによるOutputと、実際のHost Effect/SEI Decisionを混同しない。必要なConsumer二件と再利用価値の独立測定なしに中央機構を増設しない。

**価値の分母**：実Consumer成功数、原文/Source取得の追加労力、false completed／false stopped、実Provider呼出の必要回数、正しいSource/Meaning/Scopeへ到達できた件数、保存・読取・再開の修復手数、ユーザーが実際に得た選択肢を分けて記録する。技術的Go/CI/Reference PASSからOwnerの実価値受理は自動発行しない。

**引き続き未実証**：1 Functionの実Invocation/Provider Read、TEI↔Studio二実Consumer、外部H2/H3比較適格（0/4）、SHO Writer正式保存、SUI→SHO真正H1、OKF F0/K2、実EKI Connect/Local IPC配送、独立AI T1-B、Verified BOM、本番Host Grant、OwnerのMeaning・利用者Outcome。局所達成を取り消さず、未成立のClaimだけを保留する。


---

## 19. 2026-11-08：Transport実Byteと認知・利用の資格を、既存Productの実装境界で検収する

**位置付け**：§18で確認したTEIのFunction宣言13 Reply／42 Consumer対照とSHO private-owned Readerの限定実証に対し、EKIで実際に動いた低層通信、TEIの共通Application API、SEIに実在する保存・再開機能を追加照合する。いずれも各製品の既存Owner／CLI／証拠正本を使用し、新しいYI共通Message Bus、Store、Agent Runtime、Proof Engine、Host、API Registryを導入しない。

### 19.1 EKI：OSソケットによる6イベントの実通信は成立。ただしProduct Adapterの実配送ではない

[EKI merged #785〜#787](https://github.com/hat47x/eki-fabric/pull/787)と[Owner #753](https://github.com/hat47x/eki-fabric/issues/753)を再確認。mainの実 test-only Source（spikes/data-delivery-transport/unix_fixture_test.go）は、OSのUnix-domain socketを使い、固定Fixtureの6イベントを同一Goテストプロセス内の送受信goroutine間で実送受信する。ローカルLinux x86_64 / Go 1.23.2の隔離試験で内容・順序比較PASS、欠落・重複・順序変更・内容改変4負例の拒否PASS、race付き5回PASS。[実結果記録](https://github.com/hat47x/eki-fabric/blob/main/spikes/data-delivery-transport/RESULTS_2026-11-08.md)には実環境とScopeが明記されている。これを**Transport T0-Socket：試験用OSソケットの実通信は限定達成**とする。

重要な限定は二つ。第一に送受信は同一テストプロセス内であり、EKI本番Local IPC/Connect Adapter、別プロセスWorker、Lease失効強制、実Host Grant、Provider Effectの実通信ではない。第二に比較関数は双方のJSONをcompactしてから等価照合しており、**送信原Byte列と受信原Byte列の完全一致、Frame単位の全受領証跡、履歴の完全性を保証する設計ではない**。送信内の lease_revoked や result_claim 文字列は配送されたPayloadであり、認可失効や業務Resultの実成立ではない。

[merged #786](https://github.com/hat47x/eki-fabric/pull/786)のObserved Trace Comparatorは、Case/Fixture digest/Profile/Run ID/Adapter Revision/Capture Method/Dispositionを受領して、独立Expectedとの8種類の不正を拒否する別のtest-only入口。実Adapter Traceを指定しなければその試験はSKIP。**Comparatorの単体PASSと、別試験のOSソケットPASSを足してEKI実Adapter Disposition／有効Grant／Consumer実Action PASSにしない**。次は#753の既存実Adapterを一件だけ対象とし、固定6 Event→実Transport→実受領Trace→独立Comparatorを同一Attempt/同版で連結する。Connect/WebRTC方式の先行採用はしない。

### 19.2 TEI：共通APIのvalidate限定修正は成立。他3操作と外部Tool受領は別

[TEI ADR-0048／#3419/#3420](https://github.com/hat47x/tei-platform/issues/3420)では、プロセス内・CLI・MCP・HTTP・Desktopの**操作の意味契約**を同じ既存Application側から利用する方向を採用。ただしHTTP Hostを必須化しない。[main merged #3403](https://github.com/hat47x/tei-platform/pull/3403)のstdio read-only MCP参照Adapterはcatalog/inspect/trace/validateの4 Toolを実装。[main merged #3458](https://github.com/hat47x/tei-platform/pull/3458)では実既存operations.WorkspaceValidationReportFromをCLIとMCPが共有し、validateの意味失敗とMCP isError判定の不一致を限定修正した。現mainの実Source internal/operations/validation_report.goとMCP Adapter main.goを再取得し、実Contractに存在することを確認。

**MCPへの実応答経路があることと、全Operationの契約一致・現在の読取許可があることは違う**。現Adapter optionalStringは引数が不正な型／空値の場合もfallbackへ落とし得る。未指定と不正指定、Workspace固定と実Scope、意味ErrorとProtocol Error、JSON-RPC frame成功とモデルConsumerが内容を全件受領したことを独立照合する必要がある。特に正常validateのResultがCLI/MCPで共通投影されても、catalog/inspect/traceが同じSource・Scope・RevisionのConsumer結果を返すと自動認定しない。外部DSH探索のCatalog 8,192byte切断と56 Request/55 Replyを、このローカルMCPの限定実装によって解消したことにはならない。

最小の次段：#3420の既存Ownerで、現CLIと現MCPを実プロセスとして同じ対象一件へ呼び出す。正常／source-root-error／unknown kind／型違いinput／part欠落を独立Expectedで対照し、Protocol固有envelopeを無理に原Byte同一にせず、同じOperation意味とFailureを検証する。TEI #3262のRequired Source全Closure・#2586のFunction実Provider Read・TAI #168の外部Harness比較を、MCP Adapterの内側で重複実装しない。

### 19.3 SEI：保存できるRecommendationと、根拠が解決したDecisionを混同しない

[SEI #767](https://github.com/hat47x/sei-cognition/issues/767)／[Draft #824](https://github.com/hat47x/sei-cognition/pull/824)と現main runtime/go/seicli/seicli.goを照合。実CLIには推薦・決定の追加と、既存Record Bundleからのresumeがある。しかし現時点で正式なObservation／Question／Method ApplicationのWrite/Resumeが実在するわけではない。さらにrecommendation追加のCLIにQuestion未解決をそのまま記録する --unresolved があるわけではなく、resumeのUnresolvedは認識済みDecisionが明示したUnresolvedRefsに限定される。

したがって、**推薦した／保存した／再開できた**はそれぞれ別の局所到達であり、未受理Questionが欠けずに表現できること、TEIのSource/Meaningが受理されたこと、SEI Methodが本当に適用されたこと、Owner Decisionが成立したことを保証しない。--basis kind:id や --source は証拠の外部根拠の真偽を自動検証するWitnessではなく、snapshot_digestはSEI束のrawだけを識別する。MCP resumeのread-onlyと、ログを書き得る他のToolを「SEI Tool全体read-only」と広告しない。

最短のSEI検収は、既存TEIの実source-indexを独立Requiredで限定読取 → 実Result/Source Byte/Tool受領状態を固定 → 現SEI CLIの**Recommendation追加・resume JSONによる再読取**を隔離Storeで実行 → 情報損失・不明な外部根拠・Owner未決をそのまま見せること。新SEI Method Storeや質問用CLI Writeを前提化しない。その後D0（Toolのみ）／D1（設計不足を説明）／M1（Method候補を使用）を同条件・同予算・独立Expectedで比較し、M1がD1を改善しないならMethodの常時呼出しを採用しない。**このTEI→SEI実二製品受渡し・D0/D1/M1比較は未実施**。

### 19.4 ORX-65〜72：同じ成功表示でも成立した作用が違う

| ID | 最小二世界／反例 | 独立Expected・実測の限界 |
| --- | --- | --- |
| **ORX-65 SocketとAdapter** | 試験用goroutine間Unix socketを6件通したが、実Worker/Local IPC Adapterは未起動 | EKIのOSソケット試験PASSを認め、製品のLease/Grant/Delivery/Consumer Dispositionはunknown（#787/#753） |
| **ORX-66 JSON意味と原Byte** | JSON compact後の内容・順序が一致するが、原Byte/Frameは別 | EKI参照試験は意味上のイベント一致、Raw transport byte・完全Frame receipt・永続観測の証明にはしない（#787） |
| **ORX-67 ComparatorのSKIP** | 独立Comparator8負例と別の実ソケット試験が各PASS、実Adapter Trace入力なし | 合格行のUnionを実AdapterのObserved Resultと呼ばない。実Adapter Traceを受領して初めて判定（#786/#787） |
| **ORX-68 CLI/MCP validateと全API** | validateのみ意味失敗の共通Report、catalog等は未実照合 | validate局所改善は認め、CLI/MCP全操作パリティ・外部H3全Resultには昇格しない（#3458/#3420） |
| **ORX-69 不正入力がDefaultになる** | MCP側でsubjectKindが不正型／emptyなのにfallbackへ解決 | 未指定と不正指定を別判定し、別Subjectに成功したことを元Subjectの取得・Grantにしない（#3420） |
| **ORX-70 Recommendationと未決Question** | SEIにRecommendation記録は存在するがQuestion未解決を専用CLIでは保存できない | Resumeに未決が無いことを『未決Questionなし』と判定しない。未採用Recommendation≠未決Question（SEI #824/#767） |
| **ORX-71 Snapshotの出典誤認** | SEI Bundle digest一致だがTEI原Sourceが移動・差替え | SEI再読取は履歴Recordの一致。実TEI Sourceの現在Byte/Scope/AuthorityをReader再確認（SEI #824／TEI #3262） |
| **ORX-72 動作する3製品の合算** | TEI Context13 Reply、SEI既存Add/Resume、EKI Socketが別々に動いた | それぞれの局所事実を保持するが同一Attempt実TEI→SEI→EKIのConsumer成果・Owner ValueはNOT RUN |

### 19.5 次の実行順序と、研究に残す価値の問い

**先行P0（追加Coreなし）**：TEIの独立Requiredを持つ一FunctionのCall Binding／実Provider Readを一件、または現CLI/MCP同じOperationの実2 Processでの意味失敗比較を一件。どちらも現在動いている入口と既存Ownerのみで始める。価値判断は『正しいAction/Sourceへ到達』『追加Reader/説明に要した時間』『正当ケースの過剰拒否』で比較し、MCPというプロトコルを使えた件数だけをOutcomeにしない。

**並行P1（保存と移送の区別）**：SHOは既存のWorking Copy実保存と正式Writer/再開の差をOwner #4に維持し、SUI真正One-fileのnon-skip実Handoffを1回実行する。EKIは上記固定6 Eventについて実Adapter Trace／同一Attempt・同じ独立Expectedを接続。SEIは推薦保存・再開で実際に表現可能な未知/未採用だけを記録し、実Method ApplicationやQuestion記憶を先行必須にしない。

**後続P2（増分価値がある場合だけ）**：TEI/SEI/SHOの実Consumerが追加のMethod／外部Delivery／形式を必要とする利用者Jobが成立してから、D0/D1/M1比較やYICの横断Product Skillを評価する。SEI Methodに増分価値が無ければ省略し、EKI配送が必要ないローカルJobをブロックしない。既存TAI #168 H2/H3は比較適格0/4を維持し、OS G0・全Egress G1・Tool Reply G2と独立4Slotの既存Gateを増設しない。

**現時点のClaims**：EKI #787の**実OS socket試験PASS**、TEI #3458の**validate限定API共有**、SEI現CLIの**Add/Resume経路存在**は別々に認める。実EKI本番Adapter通信/Lease、TEI↔SEI同一Attempt引渡し、全CLI/MCP Adapter受領、SEI Method実適用、Function実Provider/Host Effect、SUI→SHO H1、T1-B、Ownerの意味・価値受理は **NOT RUN／NOT QUALIFIED**。


---

## 20. 2026-11-08 夜：図表正本と実呼出し、計測証拠の分離およびRQ-036再衝突

**範囲**：TEIの現行mainのProduct Requirements／最新実CLI・Go Test／Draft差分と、他チャットで深化したAdaptive Activity、Interaction Flow、Business Operation、B2C Headless、AI性能最適化を、YIC価値研究の目的別受入へ接続する。各Product Source・Ownerの意味／認可／Scenarioを正本とし、YICへ新しいモデル、図表Canon、Host、Runner、Optimizer、Registry、Proof Engineを増やさない。KON固有の構成・リポジトリ・製品化議論は、本横断価値文書に移植しない。

### 20.1 最優先の正本衝突：RQ-036をBOMの採用済みIDとして使えない

**確認した実File**：TEI mainの requirements/TEI_PRODUCT_REQUIREMENTS.md（blob 010fa6d653a3aca8ae9bb29d76a7c3944f108c6b）は、RQ-035=異種Data Source Workbench、**RQ-036=ドメインの全容を図表とナビゲーションで理解・拡張できること**。Model Mapの[merged PR #3505](https://github.com/hat47x/tei-platform/pull/3505)で後者がmainへ入った。ところが未統合[Plugin BOM Draft #3297](https://github.com/hat47x/tei-platform/pull/3297)の requirements/TEI_PRODUCT_REQUIREMENTS.md（refs/pull/3297/head、blob 0fe86718c033c172a889aa2a172cdb1206ecec94）は、**RQ-036=検証済みPlugin構成のBOMと複数バージョン組合せ試験**とする。両者は異なる要求であり、以前の「RQ-035 Workbench／RQ-036 BOMで衝突解消」という§14〜19の記録は**その時点の履歴**、現在の受入資格ではない。

**統合停止線**：この状態で#3297をそのままmergeしてRQ-036のMeaning／PAS／Gap Auditを上書きしない。現行main採用のRQ-035／RQ-036の意味と履歴を維持。BOMの要求IDは最新の未使用番号を#3267／#1119のProduct Ownerが実Source確認して別途採番する（ここでは未採番、候補番号を決め打ちしない）。BOMのReference、同一Attempt Witness監査、Pairwise Coverageの有用なコード・証拠は保存し、番号とPAS／Gap Audit／文書索引を現mainへ合わせ直してからexact-head CIと差分レビューをする。DraftのSynthetic 2×2 PASSを本番BOMとしない。**これは検証済み正本衝突であり、単なる新しい設計案ではない**。

### 20.2 全容MapはTEI標準要求に採用、実Map M0は部分投影のDraft

[merged TEI #3505](https://github.com/hat47x/tei-platform/pull/3505)のRQ-036は、Data / Function / Business / Event / State / Rule / Pattern / Operation / Provider / Pluginを孤立した図形でなく、型付き参照・クロスリファレンス・出典から辿る標準受入を要求する。図表で固定すべきものは特定のノード順ではなく、型、Identity、Owner意味、Guard、Authority、Effect Fence、Receipt、Source/Revision/Scope等の**全経路不変条件**。案件で変更可能なFlow／HookはTyped Graph Patchとして構成し、実効Graphの差と競合／到達不能／Version境界を検証したうえでTarget Generatorへ渡す。Layout/座標変更を意味Graphの実装変更にしない。

[TEI Draft #3518](https://github.com/hat47x/tei-platform/pull/3518)のread-only typed Model Map M0は既存Native World/Catalog/Source IndexからPattern→Data/Query、Relation→Target等のKind+Canonical IDのLink候補を導出し、ambiguous/unresolved/partial-projectionを明示する設計と実Go差分がある。**Draft exact HEADのGo/CI成功は未確認**。M0にEvent/State全件、Renderer/SHO/Studio/CLI相互Navigation、Sourceへの逆編集、Graph Patch→生成、実Hostを実装済みとしない。resolvedは当該Catalog内で参照先が存在する局所結果で、受理済みMeaningやRuntime Grantの証明ではない。

[TEI Draft #3507](https://github.com/hat47x/tei-platform/pull/3507)のLifecycle Graph/Interaction Flowと[main merged #3510](https://github.com/hat47x/tei-platform/pull/3510)のTrait経路Obligationを役割分離し、**Authoring Source → Typed Graph → Diagram View → 選択Plugin Patch → Effective Graph → Target Generated Code → Actual Observed Trace**で異なるRevision／観測を追跡する。今回の新Graph/Generator E2E、Chat／VUI／B2C実Targetは未実施。

### 20.3 実SelectedとActual Invocation：Go Hostには前進、通常CLI/Studioは別

[main merged TEI #3516](https://github.com/hat47x/tei-platform/pull/3516)では、既存の実Workspace Pattern/Capability/CustomGoBinding、実Go HTTP Handler、Canonical Authorizer、Driver、**合成Adapter**を同一Requestで呼ぶ限定テストが追加された。[専用CI #42474818698](https://github.com/hat47x/tei-platform/actions/runs/42474818698)の7ケースは、202受理とAdapter到達、Viewer/CSRF/Session拒否、Adapter解決/呼出し障害、Business Result契約違反の実Call順・Auditを観測した。ただし**合成Adapterは実DB／外部Providerではない**。HTTP 202、Callback到達、Host Audit、Business Commit、Client Received、実Grantは別のClaims。Adapter Invoke後の503から「副作用なし」と推論しない。

一方、[CLI/Studio selected Inspector PR #3517](https://github.com/hat47x/tei-platform/pull/3517)は現時点で**closed/unmerged**。選択済みService BをCLI typed helperとStudio Go call siteから呼ぶ12 callbackの実装提案・負例は、通常TEI CLI Dispatchや実Wails Bridgeに接続した製品到達として数えない。D1は#1251/#951で一つのSelected Service→実Call→Resultをまず正式経路に結ぶこと。今回のGo Hostに実Callbackの証拠があることを、別Surfaceや本番Plugin Runtimeへの証拠に転用しない。

### 20.4 SQL/Performance/B2Cは同一の実Business Readを必要な分だけ共有

[TEI Draft #3500](https://github.com/hat47x/tei-platform/pull/3500)では、Native Org Caseの一時Application Browse Pattern→既存Driver/Resolver→Postgres Executor→instrumented database/sql Connector→明示Semantic MapperのGoテストが[限定CI #42469646869](https://github.com/hat47x/tei-platform/actions/runs/42469646869)で成功。逆順Raw列でも明示MappingはC1/D1、named SQL Parameterの実dispatchも確認。しかしConnectorは**合成**で、隔離PostgreSQLのopt-in試験はSKIP。別ドメインの正例を目的Functionの実DB Readへ移植しない。[TEI main plan #3513](https://github.com/hat47x/tei-platform/pull/3513)の次一件は既存#2586が持つ **order_entry.recent_orders → Pattern → Query/SQL原Byte → 選択Provider → 実SQL＋args → Rowset/Mapper → Function Data Context** に固定。独立ExpectedとSource/DB identity/Scope/Result Grainの不足を同じAttemptで記録する。

[TEI merged #3520](https://github.com/hat47x/tei-platform/pull/3520)ではread-onlyの合成Performance Design Hint/Statistics/Delivery/Disclosure Joinと独立Expected19件の[専用CI #42476197836](https://github.com/hat47x/tei-platform/actions/runs/42476197836)が限定成功。Source/World/Scope、selectedとinvoked、Grant epoch、統計Window、partial Tool Reply、欠測と秘匿を区別する。しかしReported invokedは実Provider Call Receiptではない。実Telemetry Collector、実Benchmark、AI提案・性能向上、Production Disclosureは**NOT RUN**。このReferenceを実Function Readから出す統計のConsumerにする時も、新Optimizerや全域Collectorを先に作らない。

[B2C Draft #3512](https://github.com/hat47x/tei-platform/pull/3512)のHeadless UI／Conversion Engineeringは、独自Frontendへの非拘束を守り、Assignment／Exposure／Intent／Effect／Conversionを別のイベント・母集団にする**設計**。独自B2CサイトにTEIの標準Renderer・Flow UIを強制しない。統計・実験A/Bの成功から業務Commit／実売上を推測しない。実Browser B2C／CVR upliftは未実施。汎用Workbenchの実Provider Readの確立をB2C固有Experimentの絶対前提にも、逆にB2C機能をTEI最初のFunction Readの前提にもしない。

### 20.5 適応活動／Interaction／Business OperationとOutcomeの3フロー

[TAI Product Value Draft #423](https://github.com/hat47x/tai-pleroma/pull/423)では、主体の意図と反省・委任範囲を扱う**Adaptive Activity**、媒体ごとの選択・確認・中断を扱う**Interaction Flow**、型付きOperationとHostでEffect/Resultを扱う**Business Operation**を分ける横断価値研究が進む。それぞれのFlowに同じ状態名を付けてもOwner・Meaning・Authority・実行証明を共有したことにはならない。AI Chatのstream deltaやVUIの途中入力は未確定Candidate、B2Cのclick/experiment exposureはBusiness Commitではなく、元のClient/Hostに認可されるまでActionを生じさせない。

YICの最初の価値測定は、**局所read-only Mapから理解が改善したか、実Providerで一つのFunctionの出力を得たか、必要な確認で誤実行を防げたか、Context/Actionの追加操作がどれだけ減ったか**の別票。次の初学者・ドメイン専門家の実利用調査で、図表の意味の正確さ、理解・Navigation完了、固定部/カスタム部の誤操作率を比較する。今回の新しい図表・Flow生成と人間評価はNOT RUN。

### 20.6 ORX-73〜82：一つの成功表示に畳めない実Productの差

| ID | 二世界と独立Expected |
| --- | --- |
| **ORX-73 RQ番号の意味衝突** | main RQ-036=全容図表、Draft #3297 RQ-036=BOM。どちらのMeaningも壊さず、BOMを現在採用済み要求と報告しない。Owner再採番まで当該要件のマージ保留 |
| **ORX-74 画像化と全件Map** | Catalog Linkの一部がresolvedでもEvent/State/Effect/Disclosureが未資格ならpartial-projection。表示可能集合を全Businessとしない |
| **ORX-75 Patchの不変条件迂回** | Plugin PatchでGuard/Authorizeを抜いたEffective Pathは、原子Traitの個別PASSに関わらず拒否。Generatorと実Traceが未照合ならRuntime Guaranteeはunknown |
| **ORX-76 HTTP 202と実Effect** | 実Handlerが合成AdapterをInvokeした7-Case限定PASSを保持。202・AuditだけでDB Commit/Client Received/副作用なしを肯定しない |
| **ORX-77 CLI/Studio Source一致と実Service** | #3517 selected helperのDraft差分≠通常CLI/Wails Bridge実呼出。Source/Contractと実Consumer call-site/Runtime Grantを個別観測 |
| **ORX-78 SQL Test Connectorと実PG** | Native Browse Patternが合成Postgres Executorへ到達し逆順列を正しくMapperへ送った限定PASS。隔離PG opt-in SKIP・実Rowset/current Scopeはunknown |
| **ORX-79 統計の自己申告Invoke** | Synthetic Packetがinvoked=Bと主張しても実Provider Callback/Traceなしなら実Callはunverified。Window/欠測/Grantの差も独立 |
| **ORX-80 Performance最適化と売上** | Synthetic Design/Statistics Test19/19は本番Latency/CVR改善でない。Assignment/Exposure/Conversionを同一母集団・同一実Attemptで別計測 |
| **ORX-81 Chat/VUI確定前の誤実行** | 部分音声/stream token/曖昧IntentをOperation確定に昇格しない。確認後の対象・金額・Source版変更は以前の承認を失効 |
| **ORX-82 局所Go PASSとRepository Gate** | #3516のGo Host7件は限定成功だが同Run全体Health #42474818899はREADME索引欠落でFAIL。局所テストPASS／Repo Gate Fail／E2E Unknownを別列にし、旧Runを書換えない（後続修正Draft #3521） |

**現行実証ラダー**：A=設計/Diagram Link（必要Sourceの限定取得）；B=選択・実Call（同一Target/Plugin/Provider）；C=実Data Read／実Host Adapter；D=結果の必要Consumer受領；E=OwnerのMeaning・Outcome。Aだけ成立ならAを保存し、B〜Eを未観測にする。B2C、VUI、SHO、SEIのような異質Consumerへ無条件に全段を課さず、当該JobのClaimに必要な最短辺を検証する。全機能一律Blockを防ぎ、虚偽完了も拒む。

**次のP0**：①#3297のRQ-036衝突をOwnerが解消して現main Requirementを壊さない。②#2586 HJ-09でorder_entry.recent_ordersの実Provider ReadからFunction Contextに至る一辺を同一Attempt検証する。③#1251のCLI/Studio正規入口でSelected→Actual Invokedを一件検収する。これらは**並行**実施可能。既存TAI #168 H2/H3比較適格0/4を別の最優先実験として維持し、Map/Plugin/B2C/性能機能を追加Hard Gateにしない。

**後続P1**：#3518のM0 Mapを実Source/RequiredとCurrent Disclosureへ接続し、Source/Diagram/Effective Graph/Target Codeの差を正負1件ずつ判別する。#3520のTuning Referenceは実Provider Readが出てから独立Benchmarkへ接続する。SEI Method、Adaptive Flow、Chat/VUI/B2Cの追加効果は、既存Toolと比較して効果が出た場合のみ次段採用する。**本節で新しい実Provider／PG／Map Generator／Chat／VUI／本番性能／実横断Outcome／Owner受理試験は実行していない**。


---

## 21. 2026-11-08 夜：選択した実装を実Consumerまで接続する

**位置付け**：§19〜20で整理した世界の同一性・部分取得・Outcomeと、11月8日mainに反映されたTEI Plugin-first実装・Source鮮度／性能観測の差分を接続する。現存するProduct Owner/CLI/Source/Scenarioを使い、新しい共有Host、Repository、Optimizer、Runner、認可・Proof Engineを作らない。未実証の領域を一律ブロックせず、用途に必要な観測だけ追加する。

### 21.1 Inspector：Goの二Consumer呼出しはmain達成、通常CLI・Wails配線は残務

[TEI mainに統合された #3381](https://github.com/hat47x/tei-platform/pull/3381) は、既存Compositionのexact Scope/Selection/Contract/Epochを選択済みInspectorのHost登録実装に結ぶtyped adapterを追加した。現mainの internal/inspectoradapter/selected.go と docs/status.md を再取得して確認した。実Reference WorkspaceのData、Validation、Relation、Capability、Application、Patternという6対象を、CLI側の**注入Helper**とStudio Host ReadOnly APIの**二つのGo call site**でそれぞれ呼び、合計12回のHost CallbackとResult投影を局所テストする構成。B選択／A登録、失効Epoch、Host Guard拒否、Schemaや秘密Errorを含む拒否が別対照。

[統合済み #3531](https://github.com/hat47x/tei-platform/pull/3531) は製品状態とMaster Planで、**S0/S1＝Go局所経路、S2＝通常Product配線**を明記。通常のtei CLI main dispatchはBuiltinを呼び、実Wails StudioBridgeから同じselected Bが呼ばれた事実はまだない。合成Artifact digestは実Linked Binaryやcurrent Grantの証拠ではない。先行Go testは部分成功したが、Repository Healthが設計README索引欠落でFAILしたHEADも存在。新HEAD全Healthと通常CLI E2Eは別証拠として残す。

**最小S2**：通常tei inspect実Processと実Studio Bridgeの各一操作について、同一Source/Target/Selection/Host EpochでBの実Callbackを観測し、B→A誤経路／Guard失効／不正Resultを双方で拒否。対象は最初は一Subjectでよく、全6件やBOMの2×2資格を同時に要求しない。#1251/#951/#1016/#1824/#1158をOwnerとして第二Inspector Runtimeを作らない。

### 21.2 Provider Source、Rule、Buildの失効は実消費Dependencyで決める

[main #3479](https://github.com/hat47x/tei-platform/pull/3479)の限定反例は、外部import先の原SourceやManifestが改版してもConsumer World/Source Indexの両Fingerprintが変わらない世界を示す。[main #3490](https://github.com/hat47x/tei-platform/pull/3490)はPluginを選択するRule/Policy側の鮮度も合成観測へ接続した。[Draft #3524](https://github.com/hat47x/tei-platform/pull/3524)は、同一LoadでParserに渡ったprivate Provider Source/Manifest byteのWitnessを現mainへ前方移植する候補。ただし新HEAD CIは照合時にqueuedで、同時点の全Source Closureや外部AudienceへのDisclosureは認定しない。

比較の列を **Consumer World/Source Index、Provider Raw/Manifest、Rule Revision/Selection、実Source Occurrence/Loader、Build Artifact、actual invoked Provider、Target/Scope/Grant** に分ける。Sourceが更新されたという理由だけで実消費していない全Artifactと歴史Receiptを失効させない。一方、原Sourceに依存する現在の引用やBOM資格はConsumer FPの一致だけで再利用しない。same-Loadと複数Fileのatomic snapshot、A→B→Aの更新履歴も異なるClaim。

### 21.3 次のProduct Valueはrecent_ordersの実Rowsetと二つの実Consumerから

[TEI #2586](https://github.com/hat47x/tei-platform/issues/2586)のP0-Rは **order_entry.recent_orders** の一件を正本とする。必要な実観測は、Function/Pattern→実Query/SQL raw・bind args→選択Provider/実DB Executor→Rowset/明示Mapping→Function Data Context（grain/NULL/completeness）→実Consumer受領→独立Expectedを**一Attempt**で連結すること。別Operation・別SessionのPASSを継ぎ足さない。

[Draft #3500](https://github.com/hat47x/tei-platform/pull/3500)は別SubjectのOrganization Caseで、実Native Browse Pattern→Resolver→Postgres Executor→instrumented Connector→explicit Mapperの局所Go専用CIに成功した。物理Postgres opt-inはSKIP。これは実既存Contractへの接続前例だが、recent_ordersの実Rowsetでも現在Host Scopeでもない。[main #3516](https://github.com/hat47x/tei-platform/pull/3516)の7ケースはSubmit Command系の実Go HTTP Host/認可/Driverから**合成Adapter**に到達した試験。202やHost Auditは業務DB Commit・Client再受領の証拠ではなく、#3500と合算してProduct Function Readを完成扱いしない。

### 21.4 AI性能のReferenceとB2C・KONの任意性は、測れたOutcomeに従う

[main #3520](https://github.com/hat47x/tei-platform/pull/3520)はDesign Hint、合成Call/Statistics、Provider選択/Invoke申告、Scope/Grant、Window、Reply part/end、欠測をread-onlyで突合するReference。固定[専用CI #42476197836](https://github.com/hat47x/tei-platform/actions/runs/42476197836)の合成19件PASSは維持する。しかし実Provider Telemetry、実p95/Cost/CPU、Sourceに対する実Query plan、実B2C CVR改善を観測していない。[main #3530](https://github.com/hat47x/tei-platform/pull/3530)の計画は既存T0〜T4にCache/Query/Lifecycle/Trait/Headlessの検証方法を統合したもので、新Optimizerを実装した成果ではない。

**性能改善の必要証拠**は、同じSubject/Workload/ScopeにおけるBefore→変更差分・実行されたProvider/Query→After→正しい結果/副作用/開示/負荷の独立Guardrail。キャッシュがHitした、Synthetic Packetが一致した、AIが速いと評価しただけでは改善としない。公開WorkflowのHealth失敗は設計索引/Checkout pin/CI timeoutなど固有原因を含み、局所19合成PASSと、Repository Gate全合格と、脆弱性検査のネットワーク障害を別々に扱う。

[TEI B2C Draft #3512](https://github.com/hat47x/tei-platform/pull/3512)と[TEI/KON/SHO非強制計画Draft #3528](https://github.com/hat47x/tei-platform/pull/3528)は、TEIの標準Renderer/UXを使わず独自Frontendだけで完結する完全Headlessを許す方針。KON Dataspaceは必要な場合の保存・版付き公開の足場、SHOは文書Consumerであり、最初のTEI Function Read、CLI配布、B2Cサイト自体に常駐を強制しない。Assignment/Exposure/Intent/Effect/Conversion/利益を別観測として、Publish Artifact→Storage Revision→Publish ACK→外部Readerの実受領Byteを分離。B2CブラウザE2E/因果CVR改善やKON実サービスAPIは未実施。

### 21.5 採用済みRQ-036は全容Model Map。BOM DraftはOwner再採番待ち

現mainの正式Requirementsを再Readした結果、**RQ-035＝Data Source Workbench、RQ-036＝全容Model Map/Diagram**。旧§14〜19にある「RQ-036＝Verified BOM」は当時の旧Draftの歴史であり、最新の採用済み要求ではない。現在の[BOM Draft #3297](https://github.com/hat47x/tei-platform/pull/3297)にRQ-036の別Meaningが残っているため、**無修正でmainへマージ不可**。[TEI #3267](https://github.com/hat47x/tei-platform/issues/3267)／[#1119](https://github.com/hat47x/tei-platform/issues/1119)には既に衝突とOwnerによる採番・PAS/Gap Audit整合が引き渡されている。YIC側で未使用IDを自動確定させず、既存RQ-036を上書きしない。BOM synthetic Pairwise/Witness研究は並行継続可能。

### 21.6 ORX-83〜92：新しい実証成果の判別ケース

| ID | 独立Expectedと禁止する飛躍 |
| --- | --- |
| **ORX-83 Go二Consumerと実製品入口** | BのGo Helper／Studio Host API計12CallbackがPASSしても通常CLI dispatch／Wails実BridgeでBが呼ばれた証拠ではない（#3381/#3531） |
| **ORX-84 Selected誤結線と失効** | 選択B・実登録A、Host Guard撤回、Epoch失効、型違いなら対象Readを拒否。全Product/Grantに拡張しない |
| **ORX-85 外部Source改版・二FP同値** | Provider Raw/Manifestだけ変われば必要な実Source Witnessを再確認。影響がないArtifact全件を強制失効しない（main #3479／Draft #3524） |
| **ORX-86 Ruleの資格現在性** | 旧Policyで選択可でも新Ruleで適合かは別。Rule Fingerprint/Selectionと実Invocation／Host Grantを切り離す（main #3490） |
| **ORX-87 異Subjectの成功合算** | Org Case SQL Instrumented GoとSubmit Command Host合成7ケースはrecent_orders実Provider Read/Function Contextの同一Attemptではない（#3500/#3516） |
| **ORX-88 HTTP Adapterと業務Commit** | 合成Adapter実Invokeと202があっても外部DB post-image・Client受領・再送の安全を肯定しない |
| **ORX-89 Synthetic統計と実改善** | 19合成ControlがPASSしても実Latency/Cost/DB負荷改善ではない。Before/Afterと独立Guardrailが必要（#3520） |
| **ORX-90 Headless自由度の実証** | 独自UIのみでTEI標準Renderer JS等を必須にせず動くことを実Bundle/Network/操作で確認する。設計文書だけでは製品保証としない（#3512） |
| **ORX-91 公開ACKと外部受領** | Site生成・Git/KON StoreのACK後も第三者が古いByteを読む場合はPublish Outcome未確認。外部ReaderのRevision/Scope/Byteが必要（#3528） |
| **ORX-92 CI局所PASSと全体Gate** | AI Tuning合成19PASS、全Repository Healthの索引失敗、脆弱性チェックの外部通信失敗は異なる観測。古いFAILを後からPASSに書き換えない |

### 21.7 次の最短P0と並列P1

**P0-a：一Functionの実Readを優先**。#2586/HJ-09 recent_ordersで一Attemptの実SQL・Provider・Rowset・Function Data Contextの**最初の未接続一辺**を実観測。Provider/Source/Scope/NULL/Grainが不明ならそのClaimだけunknownにし、既存read-only探索は継続。

**P0-b：Plugin S2の実選択先を使う**。通常CLIと実StudioBridgeの一Subjectずつでselected Bの実Callback、B→A誤配線・Epoch失効・独立Expectedを検収。既存Go 6×2を再実装しない。

**P0-c：BOM要件ID衝突の解消**。Ownerが採用済みRQ-036を保護し、BOMのReq/PAS/Gap Auditを一括整合するまで#3297をそのままmergeしない。計測・Reference開発と並行可。

**P1：必要なConsumerに限って拡張**。#3518 Model Mapはpartial M0からSource/Diagram／標準Custom／実効Graph/実Targetを比較。AI Tuningは実Provider一Readと実統計を束縛してから改善を測る。静的公開・KON・SHO・B2Cは各User Jobに必要なときだけ別Consumerとして評価。TEST-T1B未知Gap／外部H2/H3（正式比較適格0/4）も既存Ownerの独立Gateを維持。

**未資格**：recent_ordersの実物理Rowset／正式Function Data Context、D1通常CLI/Wails Bridgeのselected B実Provider、BOMの2×2実組合せ、性能Before/After実改善、B2C転換率・KON配信実Consumer、T1-B、外部H2/H3正式比較、OwnerによるMeaningと利用者Outcomeの受理。新中央基盤を追加するより、動いているProductの次の一辺を接続する。
