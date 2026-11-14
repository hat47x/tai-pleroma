# 初期PoCの作業順序

状態: **Proposed（Owner受理待ち）**。直近の計画案であり、導入済み機能やコミット済みの実行結果を示さない。

## 2026-11-11〜14 現行証拠からの着手順（既存Phase・Gateへの索引）

[TAI横断読解ガイド §7〜15](tai-crossview-reader-guide-2026-11-09.md)に、[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)の価値・要件適正化、[#488](https://github.com/hat47x/tai-pleroma/issues/488)のSkill選択、[#168](https://github.com/hat47x/tai-pleroma/issues/168)の実Harness適格、[#271](https://github.com/hat47x/tai-pleroma/issues/271)の再資格化、[#127](https://github.com/hat47x/tai-pleroma/issues/127)の実利用価値評価を**重複させず**接続した。新しい中央Agent/Runtime/Registry・共通Gate・Product正本は作らない。

1. **まず「追加しない」基準を保存**：[merged #601](https://github.com/hat47x/tai-pleroma/pull/601)のTEI単独CLI（3コマンドでread-only調査成立）をB0の限定証拠として使用する。SkillのJSON Path driftはTEI #2605へ戻す。**実モデルB0/B1/B2初回比較は2026-11-13にTAI merged #647でJ2各Arm n=1限定実施済み**。結論は全Arm一致、SkillなしB0で正しい保留に到達。時間/Tokenの統計的優位性、横断Activity継続価値・実OS/H2/H3比較は未実証（後段§14）。
2. **横断連携の最初の実物は既存作業へ**：2026-11-11 merged [PR #602](https://github.com/hat47x/tai-pleroma/pull/602)のSUI→SHO実Producer/Consumer・TEI read-only根拠引用・別Harness CLI観測を独立の限定証拠として扱う。G6は`reference-linked-unverified`までで、ProductのClaim closure、実Source/Host Grant/OS egress、実業務Outcomeは**未成立**。同PRのOwner境界・未実施を保ち、第二のHandoff実装を作らない。
3. **再開の価値は「定義・行・不在」を分けて検証**：merged [#594](https://github.com/hat47x/tai-pleroma/pull/594)のRevision/旧Receipt判別と、Draft [#600](https://github.com/hat47x/tai-pleroma/pull/600)の実PostgreSQL合成行の反例を区別。World fingerprint一致では行Claimや可視範囲を再利用しない。現試験は**誤再利用の抑制を示したが、選択的再読取の費用節約を示していない**。
4. **価値の判定は最後に独立実験**：同じJob/Source/権限/独立Expectedで「既存Toolだけ」「必要Product＋Skill」「用途別TAI追加」を比較し、誤成功・不必要な保留・実Consumer受領・本人の選択と成果・時間/Token/人手を別評価する。初回は既存#422/#488/#127の手順を利用し、新規評価エンジンや全製品同時実装を必須にしない。
5. **成果を一つのPASSへ畳み込まない**：[Draft #624](https://github.com/hat47x/tai-pleroma/pull/624)のSCN-001合成D-04（Artifact bytes／別実装Reader／公開の制約充足／公開Goal未達／人間Value未評価）を、#127のOutcome評価と#422の能力必要性評価の入力にする。正しい停止は制約のPASSだが、公開Goal達成ではない。本文digest一致でも別Attemptの`passed:true`を再受理しない。実物/人間/本来の受取先、実Provider Effectは未証明。
6. **図の完全性と実実行閉包を別証拠にする**：merged [#622](https://github.com/hat47x/tai-pleroma/pull/622)のAX直接Edge説明は可視Graphの関係伝達試験であり、TEI [#4299](https://github.com/hat47x/tei-platform/issues/4299)の自己申告State分離反例や実Pipeline閉包を証明しない。Portfolio上の未表示・非公開は「不存在」とせず、TEIのDeclared/Actual/Artifact/Qualificationの判定をTEI Ownerへ戻す。CSW三役は任意の探索MethodとしてB0/B1/B2反証を#422・CSW Ownerに残す。
7. **量化Claimと外部回復の観測を既存Ownerへ**：[横断ガイド §10](tai-crossview-reader-guide-2026-11-09.md)に、存在／不存在／全称／ETL全件完了／同一Task／現在Grant／Outcomeを独立の問として追加。TEI merged [#4409](https://github.com/hat47x/tei-platform/pull/4409)はETL**設計のみ**、TEI Draft [#4487](https://github.com/hat47x/tei-platform/pull/4487)は量化の反証案（新実行NOT RUN）、Draft [#4464](https://github.com/hat47x/tei-platform/pull/4464)は限定投影11セルと未カバー21組（全体適合は未証明）。TAI merged #636/#637/#638でG5 A/B実受領と二Agent/現在Host資格を分離。Draft [#624](https://github.com/hat47x/tai-pleroma/pull/624)のEKI実lost-ACKは同一Task二重実行抑制を示す一方、Agent再起動後の出力本体回復は未達。本番EffectはNOT RUN。 **P0は既存Ownerの未実証Claimを正しく残すことであり、TAI共通Proof/Registryの新設ではない**。
8. **履歴を保持しつつ現在用途と今回Attemptを再資格化**：[横断ガイド §11](tai-crossview-reader-guide-2026-11-09.md)でHistorical Claim（H）／現在利用資格（U）／当該Tool/Consumer Attempt（A）を別質問とする。merged [TAI #640](https://github.com/hat47x/tai-pleroma/pull/640)とSHO #47の旧Receipt Replay負例では、A/B一致でも今回のB Consumer実起動を証明できない。TEI Draft [#4504](https://github.com/hat47x/tei-platform/pull/4504)は同内容別Root・同offset別Subject、TEI Draft [#4516](https://github.com/hat47x/tei-platform/pull/4516)はPhysical Read／Population／Temporal Cut・Resume/Delta/Restatement、TEI Draft [#4487](https://github.com/hat47x/tei-platform/pull/4487)はLegacy L／Accepted Desired D／Target T の非推移性をそれぞれOwnerに残す。**先にR-A Replay（既存main実証を再利用）→R-B Subject/Root（TEI Owner）→R-C 実Provider/時間母集団（TAI #271＋TEI #1130/#2586）**の順に失敗を検出する。新しい共有Proof Engine/Schema/Runnerは作らず、TAI #168の先行G0→G2とH2/H3適格0/4を追加Blockingしない。CSW現行3 Skillは独立単独利用可能で、MAGI三役の独立効果は研究中（比較NOT RUN）。
9. **投影時のUnknown・Conflict保存と過大Claimの抑止**：[横断ガイド §12](tai-crossview-reader-guide-2026-11-09.md)で、Model・Projection・Handoff・Tool/CIの各層が前層の証拠を勝手に強化しないためのCP-1〜4を追加。TEI merged [#4524](https://github.com/hat47x/tei-platform/pull/4524)は同Kind同IDのModel局所診断／曖昧Index除外を実装済み。TAI merged [#642](https://github.com/hat47x/tai-pleroma/pull/642)は派生CRUD/Graph/Studio PinとQH-02の受入文書を所有し、GUIでの適用合格ではない。TEI Draft [#4516](https://github.com/hat47x/tei-platform/pull/4516)は複数SourceのRead完了と共通Temporal Cut、JOIN/Validate意味保存を区別。TEI Draft [#4464](https://github.com/hat47x/tei-platform/pull/4464)の未カバー表現は不可ではなく未判定。TAI merged [#640](https://github.com/hat47x/tai-pleroma/pull/640)／SHO #47はReceipt Replay、TEI merged [#4456](https://github.com/hat47x/tei-platform/pull/4456)は未統合コマンドを要求するorphan testを反例として参照。**P0は新横断Engineでなく各Owned Consumerで誤成功を拒否すること**。正式IssueのOwner・TAI #168の初回G0→G2/H2/H3比較適格0/4・実利用価値の評価を変更しない。
10. **有用な部分証拠を、安全に生かす**：[横断ガイド §13](tai-crossview-reader-guide-2026-11-09.md)で、陽性Witness・法則付きBound・限定Projection・全件/不存在/Final・現在公開/作用許可を分離。非負の真正Subsetに対する部分SUMは条件付き下界として使えても、負の返品・重複・別Temporal Cutがあるとその下界は偽になる。**実Providerの現行到達点**はTEI main統合済み [#4539](https://github.com/hat47x/tei-platform/pull/4539)のEnvironment→PG16.15→Function Data Context→別プロセス`tools/reference-browse-read`限定であり、正式`tei` CLI・Studio/他ConsumerはNOT RUN、0行・RLS・列マスクは全件/不存在にしない。TEI main統合済み #4513/#4514/#4524/#4534/#4551により構造的なData参照・CRUD衝突/明示-only修正は前進したが、read-only review≠Owner Meaning/Apply。SHO main [#48](https://github.com/hat47x/sho-composer/pull/48)の同Markdown異Source/Target受領は、byte受領≠元TEI Subject再解決の既存反例。**優先PB-1〜4**は、既存TEI #1130/#2586、TAI #271/#422/#488/#127、QH §10へ反証を委譲し、正しく保留した件数だけでなく、避けられた無用な保留・有用な限定情報・人間の負担を別に測る。新Claim Enum、Proof Store、Batch Runner、TAI必須Hostなし。TAI #168のG0/G1/G2→独立H2/H3適格0/4は不変。
11. **能力追加の増分価値と、承認主体の実観測を分離**：[横断ガイド §14](tai-crossview-reader-guide-2026-11-09.md)で、[TAI merged #647](https://github.com/hat47x/tai-pleroma/pull/647)の初回Sonnet J2（実TEI/SEI CLI・B0/B1/B2各Arm1回）を記録。B0＝6 Tool/66,847 Tokens、B1＝8/74,447、B2＝8/70,884、全Arm同じ「記述内容一致・版根拠未成立」の正しい保留。B2 TAI Skillは実ロード・使用されB1比38,517 bytes増えたが**このJobの結論差はゼロ**。n=1で一般的費用効果・不要性を断定しない。中断→再開と実Product ConsumerをAV-2/4として測る。[TAI Draft #624](https://github.com/hat47x/tai-pleroma/pull/624)の実SEI/SUI Approval ProbeはA0文言／A1自己申告Decision／A2別資格の記録／A3実権限Owner判断を分離し、A3**観測0件**、SCN-001 P-Publish未達。SUI member資格を実人承認と誤認せず、TAIに新Authorizerを作らない。TEI Draft [#4587](https://github.com/hat47x/tei-platform/pull/4587)の実Windows生成Inspector/ WebView2限定成功と[Draft #4570](https://github.com/hat47x/tei-platform/pull/4570)の合成X-TEA三視点Pluginは別Fixture/Attempt。Stage1→Stage2 Desktop・QH-P0実TEI→SUI→SHO・Host Effectを一本のE2Eへ合算しない。**評価順**はAV-1 J2再現→AV-2中断再開→AV-3独立承認→AV-4実Product Consumer（並列可）、既存Owner #422/#488/#127/#271、TEI #4583/#1124とQH §10に委譲。TAI #168のG0/G1/G2→独立H2/H3比較適格0/4は不変。
12. **中断・再開の増分を、引継ぎPacketとSkillに分ける**：[横断ガイド §14.5〜14.7](tai-crossview-reader-guide-2026-11-09.md)に、TAI merged [#647](https://github.com/hat47x/tai-pleroma/pull/647) J2の**各Arm n=1・全結論同等**を受けたAV-2の最小因果対照を追加。T0の「SEI rec-1の内容は現TEIと一致するが、根拠Source/版の対応は不明」を固定してSession終了→T1新Sessionで復元する。M00（Packet無/Skill無）・M10（同一許可Packet有/Skill無）・M01（Packet無/Skill有）・M11（Packet有/Skill有）の**2×2**を、同じ実Product CLI/Tool/Source/現在Grant/独立Expected下で比較。M10−M00で単純メモの価値、M11−M10で**同じ情報を持つTAI Skillの純増分**を判別し、隠れメモリ/追加Readerアクセスによる交絡は不適格とする。W0 Source不変とW1 Source-only改版または別Rootの負例を並列用意し、旧Basisの自動復活と未確認権限の誤継承を禁止。結果がM10で十分ならまず**薄いHandoff/メモ**を採り、Skill固有の価値が出ない限り拡張を見送る。評価Ownerは既存[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488)/[#271](https://github.com/hat47x/tai-pleroma/issues/271)/[#422](https://github.com/hat47x/tai-pleroma/issues/422)/[#127](https://github.com/hat47x/tai-pleroma/issues/127)。[CSW Draft #600](https://github.com/hat47x/cultural-substrate-weaving/pull/600)の原AI案/実改稿/著者採否の区別をPacket来歴に反映し、三役を必須にしない。**計画のみ/NOT RUN**、TAI #168の物理隔離とH2/H3適格0/4、TEI #4583のStage1→Stage2 Desktopを先行Gateに変更しない。 **採否に使う計測はT1のTool回数・Tokenだけでなく**、T0のPacket準備・根拠確認・Redaction、配送、T1再資格化、手戻りを含む全Lifecycle費用（人手/Token/時間を別列）、割付全AttemptのITTと適格AttemptのPP、独立Expectedと情報露出の固定を条件とする。4セル×W0/W1は8条件であって8独立反復ではない。Skill固有増分が同一Packet下で反復して確認できなければ薄いメモを優先。源泉誤束縛・旧Grant・承認自己申告を費用節約で相殺しない。費用比較・人間受理・独立反復はまだNOT RUN。 **識別力の補強**：既存#647の`rec-1`は根拠参照なしであり、M00〜M11全Armが「未確認」と答えても再利用能力は評価できない。AI比較前のP0として[TAI Draft #585](https://github.com/hat47x/tai-pleroma/pull/585)の実TEI/SEI CLI Probe（M意味/L位置/K集合、J0都度再Read/J1選択的/J2旧記録無検査転用）を新Runnerにせず再利用し、**D0未根拠／D1根拠付き・局所不変／D2局所変更・新Required／D3非意味的差分・対象外Validation NG**の独立Expectedが区別できるか確認する。まずD0/D1の**AIなしProduct適格**→同じM00/M10/M01/M11で判別可能な二Jobだけを探索→D2/D3の過剰保留と危険な誤再利用を反証→必要時に独立反復/費用/人間受理へ拡張。`--basis`記録と現在Product根拠、意味受理/権限は別。TEI merged [#4557](https://github.com/hat47x/tei-platform/pull/4557)のValidation NGでも限定read-only閲覧できる例を一律拒否の負例候補に接続する。既存[#271](https://github.com/hat47x/tai-pleroma/issues/271)/[#488](https://github.com/hat47x/tai-pleroma/issues/488)をOwnerとし、**新D0〜D3比較はNOT RUN**。
13. **業務的な失敗許容を横断Activityの成功条件から分離**：[横断ガイド §15](tai-crossview-reader-guide-2026-11-09.md)に、[TEI #3250](https://github.com/hat47x/tei-platform/issues/3250)の要件圧力・Failure Acceptance Envelope（SP-R/N/FE、設計提案）を、TAIが横断で成果を読む際の**Claim上限**として接続。受注と引当のK（強い確定条件維持）／S（受付と確定の業務状態分離）／L（業務Owner受理の故障許容＋回復義務）は**要求が違う選択肢**であり、越境CUD=0やTask ACKから原子的Commit・業務完了は推論しない。TAI Activityの継続・Product Operationの受付・実Effect・結果不明・復旧責任・最終Goal/Owner Meaningを別列に保ち、未受理の業務条件/期限/容量をAIが補完しない。[TAI Draft #624](https://github.com/hat47x/tai-pleroma/pull/624)実EKI lost ACKの`duplicate`は限定Task証拠（`effect_mode: none`）であり、現実の在庫引当や返金の一度限り実施を証明しない。既存[TAI Draft #648](https://github.com/hat47x/tai-pleroma/pull/648)のGoal/Schedule/Native Session/Activity/EKI境界と、TEI #1129/#1174/#3250の実装/要件Ownerを維持する。**後続P1**はTEIのread-only最小業務FixtureのWitnessをTAIの結果観測表へ結ぶだけにし、初回TAI #168物理隔離/H2-H3（適格0/4）とTEI #4583 Desktopセルフビルドの独立P0を追加Blockingしない。受入済み要件変更・実DB Effect・業務運用試験はNOT RUN。
14. **Packet比較では新Session IDだけで独立としない**：§14.5に[TAI Draft #649](https://github.com/hat47x/tai-pleroma/pull/649)の**親IDなしでもfork履歴を継承する**反例を反映。exact HEAD `bac29b0f`の合成SK-02 CI 82件successは**実Native/OS独立の証明ではない**。M00/M10/M01/M11の各T1についてroot開始・送信メッセージ・seeded/inherited-event・Native Tool情報が分かる範囲を固定し、継承・条件不明の場合はPacket/Skill純増分を比較適格へ昇格させない。Native fork自体の継続価値を測るときは別Treatment。既存#168 Trial/Checkerを複製せず、#488/#422の値測定へ接続する。CSW [Draft #600](https://github.com/hat47x/cultural-substrate-weaving/pull/600)の独立R-Dでもroot/文脈継承を別評価する。今回新しい実Native Trial/人間Outcome/外部OS隔離はNOT RUN。

**本追補は作業順と証拠の適用範囲の提案**。初版の基準main `2a8fd9fa11a082c28e634ec3412aa88354bc4e63`、追補した#624/#622の照合基準main `2d44d82583354ec46dc8e4241c01d49c8c20d67d`（いずれも2026-11-11）。旧版の証拠を新時点の実証と同一視しない。列挙した固定PR/Issueの記録も、それぞれの適用範囲で照合した。 2026-11-12時点の追加照合はTAI main `ec9089a8874f7972fd481d62eb11af855f606b14`、TEI main `ea9e4560a835323c1d6d748486216b9ea011a965`。§11追補の照合はTAI main `eb2900df05bad75c51a740d5010aa03f9e8dcca7`／TEI main `8c3d1a5582cf3e9a40b52b3a2ebaa041739b4fd2`（同じ2026-11-12でも別Snapshot）。 §12の追加照合はTAI main `eb2900df05bad75c51a740d5010aa03f9e8dcca7`、TEI main `487f1235e39341091a3f9d415afd7803fea20293`。 §13の追加照合はTAI main `32ffba1232cd9b3e73309ba782d58e89efcb726b`、TEI main `1a2271d8c8586e928a8ed90fb516ec573118c9f9`（2026-11-13）。 §14の追加照合はTAI main `76ddd583d01dd8cb90b6d4d62018e0fcba0b9e0c`、TEI main `f3b58e7b580f0ecbea1d2feb156f52c2147f63a7`（2026-11-13）。観測の固定版とmainの時間差を保持し、既存#168 H2/H3比較適格0/4や実Owner受理を変更しない。前のPhase 0〜3や既存Ownerの判断・実証状態を上書きしない。初回のSCN-001実物Owner受理、人間のOutcome、H2/H3の適格比較、実Source/Host権限の確認は本変更ではNOT RUN。


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



**2026-11-07・用途別の過剰停止を検証する追補**： [横断監査§22.5](yi-constellation/product-value-scope-audit-2026-11-04.md)、[VA-01 §10](../evaluations/VA-01-product-value-necessity.md)へ実反証3ケースを追加。①**TEI #3337 merged**で宣言された12能力中6の未選択を観測したが、未選択は異Environment向け候補やBinding Kind差を含む正常状態になり得るため、Inspector一操作に必要なCapabilityの**実選択・実消費だけ**を求める。②**TEI #3336 merged**は子Process Build/Artifact SHAの限定実測でありself-build L3ではない。通常BuildをL3未達でブロックしない。③[SHO #19/#20](https://github.com/hat47x/sho-composer/issues/20)の通常Markdown/Vault Raw保存は、TEI Markdown Loaderの未束縛、OKF/Cloud/AIの未導入と独立に成立させる。意味解釈・遠隔同期・出典受理は利用する場合だけ現在資格を検査する。

これらを**新しい横断Blocking Gateにはしない**。単独User Jobでの正しい部分継続と、対象Capability/Source/Reader/Artifact不足時の正しい局所拒否を対で測る。SUI→SHO [#21](https://github.com/hat47x/sho-composer/pull/21)の20 PASS・1 SKIPはCheckout Guardの限定成功であり、同一実FileのH1は未実行。TEIの既知Rule T1-Aは実CLI限定Observed、次は盲検T1-Bであり、旧T1-Aの再実行を新Gap発見としない。SHO Writer、Plugin実Consumer、self-build L3、B0/B1/B2実比較、Owner受理は**NOT RUN**。


### 2026-11-08：既存CI成果の受理範囲と次の一辺を更新

[横断計画§22.6](yi-constellation/product-value-scope-audit-2026-11-04.md)／[VA-04 §10](../evaluations/VA-04-evidence-readiness-preflight.md)を当面の実証順へ接続。TEIのTT-56を扱った#3324/#3326はclosed/unmerged、一本化した[#3354](https://github.com/hat47x/tei-platform/pull/3354)がmerged。11実CLI Reply・3 Required Rule・32合成Consumer Controlのexact PR HEAD CIは**限定成功**だが、main別Run・全Required・T1-Bを保証しない。部分Scenario目録の局所Receiptと全体unknownを分ける[#3365](https://github.com/hat47x/tei-platform/pull/3365)はDraft。既知の行番号0 T1-Aは局所達成、未知RuleのAI盲検T1-Bは未実行。

**次の不足一辺を三方向で並走**：Dは既存Design Contextで独立Requiredの一Function/Ruleと合法な空配列・異modeを区別、TはTAI #168/TEI #2509で実H2の禁止Read・Tool全Call/Replyと副次Sink受領を確認、Gは#3273/#2514の事前固定HoldoutによるT1-B。Dの限定Readが成立してもTとGを自動PASSにせず、Tの外部比較適格0/4を維持する。Provider選択→実Inspector Invoke、物理Schema→業務Relation、SHO Raw Writer→保存再開・SUI同一実File H1は各Product Ownerで並行検証し、初回H2/H3の新しい必須依存にしない。

**価値の対照**：正常な未選択Capability、未読込のRequired外Subject、SHO未解釈Draftなどは局所利用を誤って止めない。同時に、必要なRule/Provider/Receipt/現在Grantを欠いた操作は誤って完了表示しない。B0/B1/B2で誤拒否と誤受入を別測定。外部Harnessの正式比較、実Target/Consumer同一Attempt、BOM適格、C1・全Coverage、Owner受理は**NOT RUN**。新しい中央Gate/Runner/Registryを設けない。


### 2026-11-08夕：外部解析・配送・Ontology・HTTP例外の採用時点を分ける

[VA-COND-01 §6](../evaluations/VA-COND-01-conditional-capabilities-and-source-drift.md)を、既存Phase 0〜3と[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)のH2/H3比較を変えない**並行評価の索引**として追加する。製品別の詳細設計・実装・意思決定は各Owner Issueに残す。

- **近接の一機能（TEI/SHO）**：[TEI #3394](https://github.com/hat47x/tei-platform/issues/3394)でREA実Evidenceの**外部read-only観測（T1-A）**と、明示的なTEI Authoring提案/Loader受入（T1-B）を分離。先に一Functionの元Source/Rule/CRUD候補だけを観測し、独立Expected/SHO Writer/旧Runtime同値は後段にする。外部解析なしの通常のTEI/SHO作業を停止しない。
- **近接の契約対照（EKI）**：[EKI #753](https://github.com/hat47x/eki-fabric/issues/753)・[merged #785](https://github.com/hat47x/eki-fabric/pull/785)は6イベント独立Expectedと参照意味の負例が限定成立。Local IPC/Connectの実配送・Leaseの適格性/遅延は**未実施**。既存Expectedのまま2 Adapter実測後に[#754](https://github.com/hat47x/eki-fabric/issues/754)で通信方式を選ぶ。
- **長期の研究（TEI/SEI/SUI）**：[TEI #3475](https://github.com/hat47x/tei-platform/issues/3475)のOntology SDK/Decision TwinはO0のFit/Gap・DSL可読性・メッセージ契約研究のみ先行可。実デジタルツインやシミュレーション（O2/O3）はTEI全体セルフビルド受理とSUI基本機能完成**後**に限る。既存P0/SHO独立Writer/SEI判断を待たせない。
- **局所のHTTP契約（TEI）**：[TEI #3274](https://github.com/hat47x/tei-platform/issues/3274)・[PR #3478](https://github.com/hat47x/tei-platform/pull/3478)で実Go Host Handlerの分岐/監査を検査する構想が進展。既存Node CI成功と新Go CI実行を別資格にし、HTTP 202/Client受信/AuditをBusiness EffectやCommit確認へ昇格しない。

**これらは新しい横断Blocking Gateではない**。各Productで必要な一辺だけを実行してから、同一User JobのB0/B1/B2で誤成功・過剰停止・費用を比較する。新しいHost/Plugin Registry/Runner/Transport基盤を先行実装しない。最新Issue・PR確認と本計画の反映のみで、実REA/実Adapter/Twin/新Go Host CI・Owner受理は本更新では**NOT RUN**。


### 2026-11-08夜：既存Harnessを基準にYI固有能力の増分価値を測る

[VA-01 §12](../evaluations/VA-01-product-value-necessity.md)と[VA-04 §11](../evaluations/VA-04-evidence-readiness-preflight.md)を既存Phase 0〜3の**採用判断と実証順序**へ追加する。汎用Agent Harnessを自作する費用対効果は外部Tool/Skill/Pluginが備える機能に左右されるため、**先に外部Harness＋YIのProduct Tool/Skill/Plugin/Methodを測る**。専用実行ループは既存方式で満たせない一条件と独立Expectedがある場合だけ比較対象へ進める。既存H2/H3の事前固定Task/Skill/Tool/Model/参加者割付は変更しない。

| 順序 | 直近の最小出口 | 記録すべき結果／未達 |
| --- | --- | --- |
| **0：外部Harness比較資格** | [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)／TEI #2509/#2515でG0実読取拒否→G1実Sink/Egress→G2全Call/Reply/byteのH2/H3適格一Session。既存4 completed/H3 Loaded ≠4適格 | 旧探索は比較資格0/4。実施後のITT/PP、独立Expected、Token/人手/誤判断/再開費用を別記 |
| **1：Product独立能力** | [TEI #3482 merged](https://github.com/hat47x/tei-platform/pull/3482)のFunction宣言↔独立Required/Sourceを実CLIで検収し、#2586のFunction→Query→実Provider Readを別実行。[SEI Draft #824](https://github.com/hat47x/sei-cognition/pull/824)のH3-X02 D0/D1/M1を同一Task/Scopeで独立採点 | TEIの13 ReplyとFunction declaredは実Provider/SEI Methodではない。D1に対するM1の優位が見えなければMethod必須化しない |
| **2：成果物と配送の局所実証** | [EKI #786 merged](https://github.com/hat47x/eki-fabric/pull/786)の固定Trace ComparatorにLocal IPC/Connect実Adapter観測を入力。[SHO Draft #25](https://github.com/hat47x/sho-composer/pull/25)のtest-only Working CopyからG2-W2実Editor保存・no-op・再開へ進む | Fixture比較器PASS≠Delivery；Working Copy byte一致≠正式保存・CAS/ABA・SUI同一File H1。各Ownerで並走可能 |
| **3：Harness追加投資判断** | 同一User JobでProduct単独／Toolのみ／Product Skill／Plugin・SEI Methodを比較し、実測で不足が残る場合だけ専用ループ案を検討（VA-01 HV-0〜HV-4） | 後続の実外部Harness比較・異モデルVA-X/VA-E、Owner受理・専用Runtime採用はNOT RUN |

**重要な停止線**：Sourceの現在性はConsumer World FPだけで保証しない。[TEI Draft #3479](https://github.com/hat47x/tei-platform/pull/3479)のImported Provider Source-only driftなど、入力原文の版を別照合する。Repo/PRの統合は合成ケースの実Target/Provider/Current Grant/Consumer受領の証明ではない。必要範囲のSource/Grantが未資格ならそのActionのみ保留し、合法なローカル探索・通常Markdown読取・既存Product単独作業を止めない。

**この追補で実行したこと**：GitHubのIssue/PR/記録済み限定CIの読取り、VA-01/VA-04/本ロードマップ更新。新TEI実Read、SEI Method、EKI二実Adapter、SHO Editor、本番外部Harness/独立価値比較・Owner受理は**NOT RUN**。新たな共通Runner/Authority/Registryを作らない。


### 2026-11-08：SUIの認知増分と情報統合を別レーンで実証する

[監査 §23](yi-constellation/product-value-scope-audit-2026-11-04.md)／[VA-01 §13](../evaluations/VA-01-product-value-necessity.md)に、現行[SUI ADR-0089](https://github.com/hat47x/sui-sensemaking/blob/main/01_Plans/adr/ADR-0089-product-value-canon.md)と2026-11-08の[#3400](https://github.com/hat47x/sui-sensemaking/issues/3400)／[#3401](https://github.com/hat47x/sui-sensemaking/issues/3401)の2つの価値軸を結び付けた。**意味形成SUI-V**は理由未分化の資料→配置・別見立て→保留→後日再開で、AIなしB0/B1・必要ならAI B2と比較。**異種Source統合SUI-I**は、B0手動／B1カード手動取込／B2限定3系統read-only参照＋2 Viewを別レーンで比較。#3401は戦略的主題の提案であり、ADR採用済みやSUI-Vの初期必須機能とはしない。

**次の実行優先**：SUI #3400 V0の現実装Fit/Gap→SUI外の実務資料でV1（初回10分/翌日再開・AI提案前の本人見立て・違和感/異論と新気付きを観測）。同時に#3401 I0のSource/Scope/Identity棚卸しをread-onlyで行い、実3系統Sourceを必要とする場面のI1/I2を後続。共同編集#3399は二Client CAS/409とdirty buffer保持から始め、全操作Event/CRDTや共通認可Hostを先行しない。Canvas複数表示・Item未分類・ActionIntentは自動Business Event/実Effectへ昇格しない。本文保存、業務意味、人の採否、外部Provider/Grant/Receiptを別正本・別資格として扱う。

TAI #168のG0/G1/G2・H2/H3固定Task/Skill/Profile/比較適格0/4は**不変**。SUI内部dogfoodやT3モデル候補をT2の実ユーザー効果へ換算しない。5件のVA-SUI対照・実T2/T1/3実Source/2 Client E2E、Owner採否は**NOT RUN**。追加の全Product共通Engine/Registry/DB/Runnerを作らない。


### 2026-11-08夜：一機能の共通API・実読取・実作用を分けて検収

[VA-04 §12](../evaluations/VA-04-evidence-readiness-preflight.md)と[VA-COND-01 §7](../evaluations/VA-COND-01-conditional-capabilities-and-source-drift.md)を、先行横断Phase 0〜3を置換しない**具体的な作業順**として接続する。新しい共通Application APIを構築するのではなく、TEI main採用済みADR-0048を一Functionで段階的に検証する。

1. **確実に達成済みの有限証拠から開始**：TEI #3482のmain commit `8ed583790e63b63527c1dd8f8aecc1d6ce6e3260`専用[push CI #42462861657](https://github.com/hat47x/tei-platform/actions/runs/42462861657)で **13実CLI Reply/42 bounded Controls PASS**。対象 `sales.order.submit`のRequired宣言・Source/Application Scopeまで。全Repo Health、全Rule/Business、実Provider/Function実行は別評価。旧「main後CI未確認」という履歴記述を現在のClaimとして使わない。
2. **一つの共通Operationを正しく照合**：main [#3458](https://github.com/hat47x/tei-platform/pull/3458)のCLI/MCP `validate`成功・Load失敗・意味エラーの同値を基線に、read-only `catalog/inspect/trace`についてSource・Scope・Meaning・diagnostics・Transport errorをそれぞれ測る。全CLI/MCP/HTTP/Studio同値やPlugin actual invokeは未実証。差は各TEI #3419〜3422・#951/#1251へ戻す。
3. **実Read／表示／Action資格を別に追加**：TEI [#3492 Draft](https://github.com/hat47x/tei-platform/pull/3492)のGraph/CRUD M1a Source readは、#2586のQuery→Provider実Read、#3491のUI unsafe integer、#3489のMigration unknown/DDL Apply、#3485のE1-Go Route test-only一致と独立。必要なFunctionのData/Meaningを採用しない限り、Writeを伴うUser Jobへ昇格しない。
4. **小さな実配送の成果を認め、引渡し資格を過大視しない**：[EKI #787 merged](https://github.com/hat47x/eki-fabric/pull/787)の試験用Unix Socket 6 Event実送受信は局所Observed（同プロセス）。[SHO Draft #27](https://github.com/hat47x/sho-composer/pull/27)の公開TEI固定原文4 File private CLI Reader受領は限定CI成功。EKI本番Adapter/別Worker/性能、SHO実SUI Producer H1、正式Writer Save、Owner受理にはそれぞれ追加実証が必要。
5. **価値判断は既存評価票を再利用**：[VA-01 §12](../evaluations/VA-01-product-value-necessity.md)のHV-0〜4でProduct単独/外部Harness Tool/Skill/Pluginを比較。新しいHarness Runtimeに投資する前に不足の一条件を実測。旧TAI H2/H3は適格0/4で、実OS拒否/副次送出/Tool Reply完全受領を未解決のまま四試行の利益へ計上しない。

**判定の対称性**：Function宣言≠実Provider、CLI/MCP同値≠Host Grant、Graph表示≠業務意味、DDL History unknown≠適用済み、UI数値丸め≠原値、HTTP 202≠Commit、OS socket実byte≠Production Delivery、Raw Reader≠正式Writer。正常なread-only作業や未解釈Markdownは高度機能が未完成でも局所継続する。反例FQ-01〜06は各Ownerで独立Expectedを固定し、不要な全体ブロックと誤成功の両方を評価する。

今回の変更は**GitHubの現状照合と計画反映のみ**。新しい共通API E2E、実Provider DB read/write、EKI二実Adapter比較、SHO正式保存、TAI H2/H3適格、B0/B1/B2利用者価値比較は**NOT RUN**。既存IssueのOwner・Scopeを維持し、第二Runtime/Runner/Registry/Authorizationを追加しない。


### 2026-11-08：確定したはず／失敗したはずを区別する回復価値の試験

[横断計画 §24](yi-constellation/product-value-scope-audit-2026-11-04.md)と[VA-01 §14](../evaluations/VA-01-product-value-necessity.md)へ **VA-RC-01（RC-01〜05）** を追加。既存各製品が所有するWrite/Save/Lease/外部Toolの「確定前失効」「確定後ACK喪失」「途中受領」を、**実Ownerへの独立Readと同一AttemptのConsumer受領**で判別する。未知結果から成功・未実行を推測せず、非冪等操作を無条件再試行しない。影響を受けないread-only・Markdown単独編集・手動作業は継続し、誤停止も測る。

**次の作業**：SUI #3399の2 Client CAS/ACK、SHO #20の文書保存、TEI #2892のHistory unknown、EKI #77のAttempt/Lease、TAI #168のTool Replyのうち実入口が存在する最小一件を、それぞれProduct Owner側で確認する。全体共通Store/Transaction/Runnerの導入やTAI H2/H3への新Blockingは行わない。**本追補は計画のみでRC実注入／Owner受理はNOT RUN**。


### 2026-11-08：型付きHookとVUI Interaction Flowの横断ゲート

[横断監査 §26](yi-constellation/product-value-scope-audit-2026-11-04.md)と[VA-01 §16](../evaluations/VA-01-product-value-necessity.md)に **VA-HOOK-01** を追加。Operation Lifecycleへモデル正本のAdd/Replace/Transform/Compose Bindingを接続し、CLI/Web/Desktop/MCP/VUIをAdapterとして生成する。VUIは状態付きInteraction Flowであり、音声I/Oだけに縮約しない。Interaction/Business/Execution Stateを分離する。実装の最小順はread-only Inspector実Provider→Hook競合/Selected≠Invoked→VUI確認・中断・再開。生成器・実Provider・Cross-target・Owner受理は **NOT RUN**。


### 2026-11-08：三Flowを図表・Generator・Pluginの共通契約へ

[横断監査 §27](yi-constellation/product-value-scope-audit-2026-11-04.md)と[VA-01 §17](../evaluations/VA-01-product-value-necessity.md)に **VA-FLOW-01** を追加。Adaptive Activity Flow／Interaction Flow／Business Operation Flowを分離し、標準固定部・Plugin可変Slotを持つ図表をGenerator/Validationの入力とする。最小順序はread-only実Provider Trace→三Flow図表とManifest照合→専門Web/Chat/VUI Consumer→B2C負荷・UX比較。専門B2Cに標準UIやAI Harnessを強制しない。既存OwnerのIssueとTEI MASTER_PLANを正本とし、新たな中央Host/Workflowを導入しない。**実試験・Owner受理はNOT RUN**。


### 2026-11-08：Evidence資格を保持したAIチューニング閉路

[横断監査 §28](yi-constellation/product-value-scope-audit-2026-11-04.md)と[VA-01 §18](../evaluations/VA-01-product-value-necessity.md)へ **VA-TUNE-01** を追加。Observe→Diagnose→Propose→Preview→Verify→Accept→Apply→Re-observeの最小閉路を、CLI/Studioのread-only実Provider Traceから着手する。Source/Structural/Accepted Meaning/Build/Executionの資格を分離し、World FP一致やCache hitだけでEvidenceを再利用しない。Query/Index・Cache・Plugin置換を独立Expected、P50/P95、実Plan、旧Artifact保全で比較。中央Evidence Storeを初期必須としない。**実負荷・AI変更適用・Owner受理はNOT RUN**。


### 2026-11-08：CSWの選択的実践

[横断監査 §29](yi-constellation/product-value-scope-audit-2026-11-04.md)と[VA-01 §19](../evaluations/VA-01-product-value-necessity.md)へ **VA-CSW-01** を反映。CSWは選択的Skill/Pluginと独立検証の開発ループであり必須Runtimeではない。既存HarnessのOS隔離・送出範囲・完全Replyを先に実測し、独自Loopは比較で不可欠性が示されるまで保留。**実比較・Owner受理はNOT RUN**。


### 2026-11-08：段階的なEvidence資格（F0〜F5）を実証計画へ

[横断監査 §30](yi-constellation/product-value-scope-audit-2026-11-04.md)と[VA-01 §20](../evaluations/VA-01-product-value-necessity.md)に **VA-EVID-01** を追加。Source→API→Representation→Provider→Effect→Deliveryを同一Attemptで追跡し、局所成功を実E2Eへ加算しない。最初は一Functionの実Provider Rowset、次に正式Writer Readbackと実Consumer受領。既存の限定的なCLI/Reader/IPC PASSは維持し、Owner受理や本番Effectへ昇格しない。**実注入・Owner受理はNOT RUN**。


### 2026-11-08：初回Product実Readをrecent_ordersへ固定（横断証拠の訂正）

[VA-04 §13](../evaluations/VA-04-evidence-readiness-preflight.md)に**初回一Functionの実行票**を固定。[TEI Master Plan](https://github.com/hat47x/tei-platform/blob/main/plan/MASTER_PLAN.md)のP0-R初回対象は **`order_entry.recent_orders`** であり、[main #3482](https://github.com/hat47x/tei-platform/pull/3482)の13実CLI Reply・42限定Controlは別の **`sales.order.submit`宣言照合**。両者を同一FunctionのF0→F3と数えない。

**次の最短経路（既存#2586/#2506/#2514がOwner）**：`recent_orders`に対し、実Source/Query raw→実選択DataSource/Provider→actual SQL＋typed args→実Rowset＋Mapper→Function Data Contextを**同一Attempt・同一Scope・独立Expected**で照合する。その後に限ってForm/Tableの二read-only Consumer、三視点Graph/CRUD、性能統計の実Consumerを追加する。実PG SKIP／別Domainの合成Connector／HTTP合成Adapter／AI Synthetic PacketのPASSを実Function Rowsetへ合算しない。

**訂正済み現況**：[TEI #3479](https://github.com/hat47x/tei-platform/pull/3479)のImported Provider raw/Manifest失効反例、および[#3381](https://github.com/hat47x/tei-platform/pull/3381)のSelected Inspector二Go call-siteはmain統合済み。ただし後者の通常CLI/Wails Product WiringはS2未達。[#3516](https://github.com/hat47x/tei-platform/pull/3516)のHTTP合成Adapter7経路と[#3520](https://github.com/hat47x/tei-platform/pull/3520)のAI性能合成19件は限定成功。実Provider/性能改善/本番Effectは未資格。RQ-036は[main #3505](https://github.com/hat47x/tei-platform/pull/3505)の全容Model Mapを維持し、同番号を使う[BOM Draft #3297](https://github.com/hat47x/tei-platform/pull/3297)はOwner再採番まで無修正統合禁止。衝突の追跡は[TAI Draft #532](https://github.com/hat47x/tai-pleroma/pull/532)を再利用。

**判定**：P0-RのR0〜R2実ReadとR-QUAL-01〜06は本更新ではNOT RUN。現TAI H2/H3適格0/4、未知AIテストT1-B、Owner意味受理を変えない。不要なPlugin/Graph/AI/SHO/外部Harnessの全完成を実Readの先行必須にせず、Source取得/権限/実受領の必要な一辺だけを正しく停止・再資格化する。


### 2026-11-08夜：直列Fゲートの誤読を防ぎ、既存の限定成果から実Consumerへ接続

[横断監査 §30.1/30.2](yi-constellation/product-value-scope-audit-2026-11-04.md)／[VA-01 §20.1](../evaluations/VA-01-product-value-necessity.md)／[VA-04 §13](../evaluations/VA-04-evidence-readiness-preflight.md)に、最新実証の進捗とClaim適用条件を反映。**F0〜F5を全操作必須の直列Gateや成熟度総得点にしない。** read-onlyではF4実業務更新をnot-applicableにできる一方、実UpdateはF4の現Grant/Commit/独立Readが必要。F5の実受領はread-onlyでも別に確認し、F5からF3 Provider/実Owner Effectを推論しない。

**直近の限定成果**：TEI main #3482の13実CLI Reply・42 Consumer Controls、[TEI→SEI A0実CI #42474971439](https://github.com/hat47x/tei-platform/actions/runs/42474971439)の独立Requiredに基づく**評価者作成Recommendation**の保存・Resume、[SHO Draft #25](https://github.com/hat47x/sho-composer/pull/25)のtest-only実Working Copy書込→別Open Readback（二OS CI限定PASS）、[EKI #785](https://github.com/hat47x/eki-fabric/pull/785)の6 Event Reference意味負例をそれぞれ別資格に固定。従来の「SHOはWriterの実書込を一切試していない」「SEIへ一度も保存・再開できていない」という広すぎる未実施表現を補正。ただし正式Editor Save、SEI Method自動発見、EKI実配送、TEI実Provider SQL、SUI→SHO H1、H2/H3適格比較は未達。

**次に欠けている最小一辺**：TEI一Functionの選択Provider＝実Provider→Rowset→Consumer、SHO正式Editor保存→再Open、SEI H3-A0の先でD0/D1/M1の比較、EKI実Transport二方式、TAI G0/G1/G2実適格（他Productと非阻害）。**要求番号の採用は別**：TEI main RQ-036はModel Map。BOM Draft #3297のRQ-036はID競合を再発しており、Ownerによる別番号採番・参照整合までBOM要求の正式採用を保留する。BOM研究・既存読取作業や初回H2/H3を停止しない。新中央Registry/Host/Runner/Schemaは作らず、Owner受理・実価値比較は**NOT RUN**。
