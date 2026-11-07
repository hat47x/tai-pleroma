# VA-04：AI-first検証の入力閉包と契約発見の事前確認

- **状態**：2026-11-04、横断実証へのSource-static監査結果の受け渡し／実証手順案。VA-04固有の実行、独立Expectedの受理、Web/Provider E2E、Owner採用は **NOT RUN**。
- **参照**：[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)、[VA-01](VA-01-product-value-necessity.md)、[VA-02](VA-02-cross-product-first-run-protocol.md)、[VA-COND-01：用途別能力](VA-COND-01-conditional-capabilities-and-source-drift.md)、[TAI #424（VA-00監査台帳）](https://github.com/hat47x/tai-pleroma/issues/424)。
- **目的**：既存の実TEI CLI・Scenarioと他ProductのResultをAI/外部Harnessが誤って「全対象検証済み」と認定しないために、**何が宣言されたか・発見されたか・実際に読まれたか・何を検査したか・現在利用資格があるか**を分ける。第二のValidator/Source Registry/Execution Authorityは実装しない。
- **責務**：VA-00はIssue・ADR・文書の整合性監査、VA-01は価値・過剰要件、VA-02は実証ラダー、本VA-04は証拠から言えるClaimの上限を定める。製品側の不具合修正・仕様採否は当該Owner Issue。

## 1. 新しく確かめた既存事実と意味

| 課題 | 2026-11-04の実証/監査で確認済み | 横断側の停止・縮退条件 |
| --- | --- | --- |
| [TEI #2822](https://github.com/hat47x/tei-platform/issues/2822) | WSL Go 1.27で利用者宣言0件のworkspaceでもvalidate ok=true。model catalogは標準stdの13件があり、件数だけでは利用者定義の実在を示さない | ok=trueは「この読込経路で検出された診断なし」という限定Claim。宣言数、標準/利用者の区分、対象Scopeは別証拠が得られない限りunknown |
| [TEI #2823](https://github.com/hat47x/tei-platform/issues/2823) | manifestの未知/不存在sourcesやworkspace-filesに見える非対応拡張子が黙って読み飛ばされる場合がある | workspace-filesに存在＝Parser消費済みとはしない。要求されたSourceが未読込/不明なら対象範囲のfull validationを主張しない |
| [TEI #2824](https://github.com/hat47x/tei-platform/issues/2824) | tei commandsは19件、CLI契約文書は13件と記載。discoveryは各commandのschemaVersion/安定契約対象外worldを区別しない | 実binary・出力のschemaVersion・契約対象/非対象の個別照合を用い、発見一覧だけで安定した外部JSON契約/Versionを保証しない |
| [EKI #698のEKI-CA-02](https://github.com/hat47x/eki-fabric/issues/698) | Suitabilityの提案ADRは4結果値だが、実装/設計は3結果値（FABRIC_JUSTIFIED / FABRIC_NOT_JUSTIFIED / NEEDS_MEASUREMENT）。NOT_SUPPORTED相当はAdmission/Policy拒否 | [EKI #58](https://github.com/hat47x/eki-fabric/issues/58)を参照する比較表は実装結果とAdmission拒否を分ける。4値を実APIの戻り値と決めつけず、対応表はOwner判断待ち |
| [TAI #424](https://github.com/hat47x/tai-pleroma/issues/424) | 9 Laneの文書監査と別担当S4照合完了。F2はOwner判断項目59件（高20/中28/低11）。別context同一modelでありモデル独立ではない | VA-00の監査件数をVA-01の6Product価値受入・VA-02の実E2E成功として数えない。F1 Draft PRのmergeやF2採否を勝手に行わない |

**証拠境界**：TEI #2822〜24には別作業者のWSL実ビルド再現が含まれる。本VA-04ではそのIssueをSource-static確認したのみで、同じビルド/コマンドは再実行していない。main版の異なる観測は単一固定Snapshotと呼ばない。EKI #698のF2は未決の意味不整合であり、3値と4値のどちらが正式契約かを横断担当が決めない。

## 2. 実証前に照合する5つのClosure

| Closure | 必要な証拠 | False-greenとして拒否するもの |
| --- | --- | --- |
| C1 Declared | manifest source roots、選択条件、モデル/Scenario/Caseの要求集合とその版 | manifestに書いてない、あるいは綴り違いなのに検証対象と宣言 |
| C2 Discovered | Sourceの存在、読み込み候補ファイル一覧、Content Revisionと存在/不存在/partial/permission-denied | ファイル未取得を空集合/不存在確定へ昇格 |
| C3 Consumed | 実Parser/Resolverの入力集合、除外理由、実読込Sourceのdigest、適用Scope/Grain | workspace-filesに列挙された未読込ファイルをvalidated扱い |
| C4 Asserted | Accepted CanonicalとScenarioの関連、独立Expected、対象Step/Rule/Targetと実Assertion、実read/partial/unknown | diagnostics=[]、Case件数増、CLI exit 0だけで意味Coverage合格 |
| C5 Eligible & Received | 実binary/CLI JSON契約、Host/Provider許可、Task/Attempt、外部Effect/Consumer実受領、Current Grant | historical PASS・Claim ACK・Tool discoverだけで実行/受領/品質合格 |

**適用方法**：C1〜C3が未知でも公開可能な合成Candidateの作成・ローカル静的調査は可能。ただしそのClaimは「対象限定/未保証」と表示する。対象の実Sourceが必要な検証や危険なActionは、当該Product/Hostが必要な情報を解決できなければfail-closed。分母unknown/0をCoverage 100%とはしない。C5をTAIの中央権限機構として実装しない。

## 3. VA-X向け負例パケット（Expected提案・NOT RUN）

| ID | 入力・注入 | 守るExpected | 既存Owner |
| --- | --- | --- | --- |
| PF-01 | tei.workspace.yamlだけの宣言0件、validate ok=true、catalog 13 std | validated source population=0/unknown。User modelの完全性は未確認 | TEI #2822 |
| PF-02 | sourcesに不存在root、別rootに無視されるファイルを含む | manifest/実Readの差と原因を明示。全対象PASS禁止 | TEI #2823 |
| PF-03 | workspace-filesに .tei.bak や Application.tei | managed file と consumed sourceを分離。隠れた内容をSemantic PASSへ昇格させない | TEI #2823 |
| PF-04 | tei commands 19件、古い文書13件、worldを通常JSONとして読み込むHarness | exact binary/command/response schemaを照合し、worldの安定外部契約を推定しない | TEI #2824 |
| PF-05 | 6-Step ScenarioのみCLI PASS、未知StepとWeb未実行 | Step範囲限定PASS、Web/Auth/実EffectはNOT RUN、欠落Step fail-closed | TEI #1180 |
| PF-06 | Suitability 3値実装をADRの4値で解釈し、NOT_SUPPORTEDを実戻り値扱い | 提案・実装の差を未決で保持し、Admission拒否と評価結果を分離 | EKI #698/#58 |
| PF-07 | 過去のSource/Scenario/GrantではPASS、新Provider/HostやToken時点では失効 | 履歴証拠は保持、現在Eligibility/実Readを独立判定 | TEI #2600、TAI #271 |
| PF-08 | Trusted bundle時間窓・署名済み決定の壁時計飛びによる不規則拒否 | 時刻系の故障と認可の正常拒否を混ぜず、単調時間・実壁時計の範囲を記録。製品の許容Skew変更はEKI Owner判断 | [EKI #697](https://github.com/hat47x/eki-fabric/issues/697) |

PF-01〜04は実際のIssue再現手順を元にした**再検査案**であり、このVA-04として実行した結果ではない。PF-05〜08は追加の独立Oracle準備対象。生成AIが作成したJSON/Actualを独立Expectedへ自動採用しない。

## 4. 実行記録・G0〜G4へ組み込む手順

1. **G0 / Source freeze**：Product repo full SHA、該当Issue取得時刻、PR head、実binary/Go版、manifest/Source selector、fixtureとExpected作成者、観測できたClosureを記す。異なるmain版の検証結果は別Run扱い。
2. **G1 / Scope preflight**：PF-01〜04をTEI #2822〜24の既存Ownerと照合し、現行CLIから得られる情報のみでC1〜C3とcommand contractを点検。情報が欠けたら「unknown/limited」とする。第二のTEI ValidatorをTAIに作らない。
3. **G2 / AI-ext & EKI**：VA-02 AI-EXT-01〜03をP1の既存6-Step Scenarioに接続して実行（準備できないTargetはNOT RUN）。EKI PF-06は3値実装と4値提案の状態差を固定し、業務SuitabilityとPolicy拒否の二つのClaimを分けて比較。
4. **G3 / Owner handoff**：TEI #2822/#2823/#2824、EKI #698/#58、TAI #271に、実証結果を該当IssueのOwnerへ戻す。VA-00のF2優先度（高20/中28/低11）はOwnerの意味判断待ちとして保持。新しい二重Issueを乱立させない。
5. **G4 / selective requalification**：Source root/Reader、CLI契約版、Toolchain、Scenario/Plugin、EKI Suitability enum/Admission、Host Grantを個別変更し、C1〜C5の失効範囲を測る。旧Runの履歴を消さず、新版で有効かを別判定。

**最初のGo/No-Go**：少なくともPF-01・02・04・06について独立Expectedを固定し、現行製品環境でpositive/negativeを再実行できたときのみ「前提付き検証可能」とする。実行不能ならSource-staticの限定観測。全Productの整合性監査がS4まで完了した事実は、このGo判定を代替しない。

## 5. 別Laneに残す用途別Transportの研究

EKIの軽量認知・低レイテンシ・マルチモーダルなデータ通信は、[VA-COND-01：用途条件付き能力とSource状態ドリフト](VA-COND-01-conditional-capabilities-and-source-drift.md)のVA-F1が価値・適用条件・Transport比較を扱う。本VA-04は、どのTransportにも共通する「実際に読んだ入力範囲／権限／結果の受領」をClaimとして過大評価しないための事前確認に限定する。具体的な通信プロトコルや低遅延保証はEKI Ownerの未決事項であり、ここで独自の第二設計を作らない。

**非目標**：既存TEI CLI契約・EKI Admission/Trust/Transportの仕様を横断Issueで勝手に改訂すること、新しい統合Host・Permission Engine・中央Evidence DB・Run Controllerを設けること、整合性監査を正式な製品受入に読み替えること。

## 6. Sourceを「発見した」だけでなく実Build入力へ束縛する

[TEI PR #2819](https://github.com/hat47x/tei-platform/pull/2819)の限定反例は、manifestに宣言されたGo Source D1と、実go buildへ渡るD2が異なる場合でも、従来のSelectorが受容し、生成物はD2に由来する一方、ReceiptのSourceDigestはD1を示し得るというもの。この事実は、C1〜C5のうち**C3 ConsumedとC4 Assertedの接合が破綻する**実例である。D1/D2の一致を単一のhashの存在だけで推定せず、正確なBuilder入力集合、構築順、実Target、生成物集合、Toolchainを実観測と結び付ける。

**PF-B01（新たな負例候補）**：同一Source/Generator固定のControlと、宣言D1・ビルドD2のMismatchを実行。現状不一致の発見と、修正後に実入力closureの証拠がなければ当該Build適合を拒否することを別判定する。Controlも単にexit=0やbinary digestが同じだからPASSとはしない。独立Oracle担当はBuildの実入力をCandidate/Receiptの宣言値から導出しない。

ただし、これを全Productの実行を止める横断Gateにはしない。Sourceの**read-only調査**、合成DSLテスト候補作成、限定Scenario verifyは実Build・実Effectの資格に届かないと明記して進められる。**実Artifact/Target/業務Effectの適合Claim**には、当該Product Ownerが要求するBuilder入力の対応を必要条件とする。[TEI #2595](https://github.com/hat47x/tei-platform/issues/2595)へ修正・再実証のOwnerを返し、本VA-04では第二Build Registry/Validator/CLIを作らない。

本VA-04でのPF-B01実行、TEI EB-04修正、他Targetの資格、Owner受理は **NOT RUN**。

## 7. 2026-11-07：新TEI形式の明示診断とSource移行の資格差

[TEI Draft #3031](https://github.com/hat47x/tei-platform/pull/3031)は、旧Readerが新`*.tei.md`を無視すると`validate.ok=true`のままSubjectが消えるという誤成功に対し、未対応Sourceを`TEI_MD_PARSER_UNBOUND`として明示診断する限定コードを追加した。固定HEAD `63953ccb5c12ead26ec1268e7c0afdba4eff66ae`の[focused CI #42217379093](https://github.com/hat47x/tei-platform/actions/runs/42217379093)は成功。これは**未対応入力の拒否**であり、MarkdownをTEI定義として解析・受理できるという証拠ではない。

**PF-MD-01（履歴と現在実装の区別）**：V0＝旧`order.tei`が選択された結果、V1＝同じ定義を単純に`order.tei.md`へ改名してSource数が減る結果、V2＝#3031の診断で拒否される結果、V3＝将来の正式Markdown Readerで実Parse/Meaning照合が成功する結果を**別々の資格**とする。V0からV3へ試験結果を流用しない。独立Expectedは宣言数・実選択Source・解析済みSubject/Role・診断・実Source Indexを個別に固定する。V2の拒否試験が通っても、V3の成功条件は未達。

**Ownerと移行順（2026-11-07訂正）**：[TEI Draft #3030](https://github.com/hat47x/tei-platform/pull/3030)の最新追補に従い、**旧新Source移行仕様・検収IDの主担当は#3030（M0〜M6/TM-01〜14）**とする。[Draft #2667](https://github.com/hat47x/tei-platform/pull/2667)のTMDケースは横断経緯・引渡し参照であり、第二の移行Gateではない。#3030内の専門家向けMarkdown可読性/原文保持AU-01〜08も同PRに属するが、形式移行とAuthoring表層の合否は独立採点する。[#1920](https://github.com/hat47x/tei-platform/issues/1920)は版・互換、[#988](https://github.com/hat47x/tei-platform/issues/988)はK0 Source Kind/Language Plugin選択を担当。#3031の管理Source Rootの明示拒否は、許可された**非管理Raw Draft**の保存まで禁止してよい証拠ではない。旧形式＋通常Markdownは継続可能、新形式の必須定義は未対応なら拒否、実Parser成功後だけPromoteという正負対照を先に固定。新Parser/Registry/HostをTAI側に作らない。

**資格状態**：#3031の限定CIは実証済み、旧形式での公開CLI S1も限定実証済み。一方、`*.tei.md`の実Parser、旧新移行の全一改訂E2E、Owner意味受理、TAI外部Harness H2/H3は**NOT RUN**。この差があるため、旧固定SourceでのH2 Tool-only実験は継続できるが、新形式の利用可能性は主張しない。

## 8. 2026-11-07：実Tool到達と参加者隔離は別のClosure

[外部DSH実行記録 #3113](https://github.com/hat47x/tei-platform/pull/3113)により、[VA-02 §13](VA-02-cross-product-first-run-protocol.md)の外部Tool callは限定Observedになった。しかしH2の**Source実到達**と、必要なParticipant入力集合だけを読める**非露出の保証**は別。固定TEI Binary＋public `sales.order`のSource Fingerprint一致は前者を裏付けるが、DSHのread-only Profileから作業範囲外のWorktree Readが通ったことは後者の未達を示す。

| 対象 | 必要な観測 | 現在の判定 |
| --- | --- | --- |
| CLI起動・実Read | Tool Request、argv/cwd、実Binary/Source digest、exit/Reply、Source IndexとWorldFP、同Attemptの出力 | **局所Observed**：#3113は実起動32件・完成Task1件。全Tool traceの元DSH JSONL原文保存は未完 |
| 参加者への非露出 | Reviewer Expected・Skill参照・旧Log・許可外Sourceに対するOS/Harnessの**実拒否**、開始前File/Task/Tool/Profile固定 | **NOT QUALIFIED**：read-only Profileでは作業範囲外のReadが可能だった |
| Model/Adapter/Tool障害 | 失敗前のTool SuccessとTrial Completionを分離し、MALFORMED_RESPONSE 5、INVALID_CONFIG 1、完了3を全9探索の同じ分母で報告 | **探索実測**：失敗したTrialを成功H2として再分類不可 |
| Cost/通信・現在Grant | Model token/料金、Log拡張の実送出・観測可能な範囲、Host/OS隔離、現在の適用資格 | **Unknown/NOT RUN**：`session-log-deepseek.enabled=false`だけで送出ゼロとは言えない |

**局所的な工学的教訓**：検査済みSourceと、Modelが実際に読んだかもしれないSourceは別集合である。入力閉包をSource側（発見→実読取）とParticipant開示側（許可→物理的拒否・実観測）の両側から評価する。OS隔離の手段を共通Harness Runtimeとして先行実装せず、[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)と[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の実User Jobに必要な範囲で現Harness/Hostの能力を選ぶ。

**OKFを次段階に接続する場合**：[TAI #514](https://github.com/hat47x/tai-pleroma/issues/514)は、宣言された計算定義／Typed Bind／実Executor Receipt／AIとは別の決定的Attesterを分ける提案。Definitionの`verified`やAttester verdictは実Source/Consumer/現在GrantのClosureを置換しない。最初の比較H2/H3が未資格の間にSkill本文・Tool ABI・Expectedを差替えない。Attested Computationの実CLI/Attester PoCは**NOT RUN**。

### 8.1 完全なSource出力と、Tool返信に含まれた実情報を同一視しない

[TEI mainに収録されたDSH実証の保存Byte](https://github.com/hat47x/tei-platform/tree/main/plan/evidence/DSH_H2_TOOL_ONLY_READ_ONLY_2026-11-07)と[TAI Runbook §24.3](https://github.com/hat47x/tai-pleroma/blob/docs/yi-harness-skills-20261102/docs/yi-constellation/first-real-skill-qualification-runbook-2026-11-02.md)から、VA-04のC3「実消費」とC4「主張」の間に**受信完全性・伝達変換**を明示して確認する。既存Closureに検査項目を増やすだけで、新Pipe/中央Validatorを追加しない。

- **実Producer Source**：実TEI argv/Workspace・Binary・stdout/stderrのbyte長とdigest、終了状態、JSON bodyの構文可否を別観測。指定されたCLI以外のShell挙動を意味解析へ混ぜない。
- **実Tool経路**：CLI出力→PowerShell/Adapter→Harness Replyの実byte・切詰め閾値・最大出力設定とCall IDを照合。8,192 bytesのCatalogの先頭値だけを「全件実取得」や「Complete Source Index」にしない。原因未特定なら保持する。
- **実Model/Consumer**：受信済みResult（56 Call中55 Replyという不完全集合）、出所・未観測の明記、最終回答の独立Expected。Session completedで受信済み件数・回答正答・未取得不在を推定しない。
- **実Tool/Exposure Profile**：初回SKUのWhitelist（`version/commands/model catalog/inspect/trace/validate`）で固定Sourceの限定Readを確認。探索試行に使った`source-index`や任意PowerShellの成功を、そのままH2参加者の許可へ移送しない。read-onlyの設定名で親Checkoutの実読取拒否を保証しない。
- **実Model版と費用**：`~deepseek/deepseek-flash-latest`指定Aliasと実解決版を分離。Provider metadataとModel/Adapter失敗分類、実Costが揃わなければ一致/費用改善はunknown。

**Stop/Continue**：比較開始前にReviewer ExpectedやH3 Skill本文がH2から読めるならTrialを始めず、公開SourceのCLI/S1調査は独立に継続可能。開始後のTool truncation・欠ResponseはITT内失敗/unknownとして記録。正しく必要なSubject限定`inspect/validate`が受領できるなら、全Catalogの完全性が未確定でも当該Taskに必要な範囲だけ価値採点候補とする。必要Sourceの範囲すら証明できなければ適格とはしない。

**実施状態**：mainにEvidence Byte収録は確認したが、本更新でDSHを再実行したわけではない。受信切詰めの原因、OS/Network Egress、隔離済みH2、H3 Loader、4 Sessionの独立評価はNOT RUN。

### 8.2 Participant隔離と副次送出の実観測（2026-11-07）

[TEIのH6-E1実測](https://github.com/hat47x/tei-platform/tree/main/plan/evidence/DSH_H6E1_READ_BOUNDARY_2026-11-07)により、DSH read-onlyから合成Raw/.env/作業root外の読取が**止まらず**、実Tool結果がモデル入力とSession Logの二系統に入ることが局所Observedとなった。[H6-E2のLocal Mock実測](https://github.com/hat47x/tei-platform/tree/main/plan/evidence/DSH_SESSION_LOG_RETRY_AND_DEFAULT_2026-11-07)では`dsh_session_log`既定ON、未受理（503や空SSE）時の同水位再送が確認された。従来の「実Egressは全てNOT RUN」を、**Local Mock宛の副次送出はObserved／実Provider・全出口は未観測**に更新する。秘密や私的パスの実流出を意味しない。

**Evidenceを評価する5つの質問**：（a）何がOS/Hostで実読取可能だったか、（b）CLI/Toolが何を実消費したか、（c）どのSink（Model Messages／Session Log／Tool Reply／公開Issue/CI）へ実載ったか、（d）失敗/再開で何が重複送出されたか、（e）どのAudience向けに、そのObservationを公開してよいか。実検査のraw request bodyと公開可能なEvidence要約は分離し、合成Canaryの原文や実Reviewer Expectedを外部LLMにそのまま渡さない。[TEI #2515](https://github.com/hat47x/tei-platform/issues/2515)のH6-E13はEvidence自身の二次開示を既存Ownerが検証する。

[TEI mainのH3実Load記録](https://github.com/hat47x/tei-platform/blob/main/plan/evidence/DSH_H2_H3_FOUR_SESSION_2026-11-07/README.md)により、H3の固定root本文5,482 byteと1 Referenceの実受信は**Observed**。一方、H2のSkill非露出を物理的に強制できたか、実ReaderがSkill全Requiredを消費したか、実Consumer回答のIndependent Expected、現Grant、H3の付加価値は別のClosure。4実Session completed≠4比較適格で、適格**0/4**。旧§8のH3 Loaded「NOT RUN」は**当時の状態**として扱う。

**今の必須資格**：対象public Sourceの許可Read成功と、同一実Profileの許可外Read拒否を正負対で観測→副次Sinkを観測した範囲で開示判断→固定Whitelist/実argv/real root/Result欠落なし→新Trial Group割付。OSやGatewayの実拒否が未取得なら「外部に出なかった」と回答しない。物理root変更、Toolの名前だけread-onlyでもFS出力flagで書ける反例はG0/G2に吸収し、新ACL Engineは建てない。初回治験はread-onlyであり、新書込/OKF/Cloud等を要求しない。

**状態**：新しいDSH/Host/Network実試行を本評価票では実施していない。H6-E1/E2とH3は既存Product側の実測を引き継いだ限定証拠であり、正式G0/G1/G2適格・四Session独立評価・本番秘密運用・Owner受理はNOT RUN。

## 9. 2026-11-08：Design ContextのRequired閉包と受領モードを別資格にする

[TEI #3304](https://github.com/hat47x/tei-platform/pull/3304)の公開Validation・行番号0候補は生成済Pinned CLIで実判別（**既知T1-Aのみ**）。一方、[P-1b1 #3326](https://github.com/hat47x/tei-platform/pull/3326)の最初の実CI [#42385502023](https://github.com/hat47x/tei-platform/actions/runs/42385502023)は、**試験Consumerが`source-index`のsubjectモードを全件indexモードと誤認**して全3 RuleのDefinition参照を欠落と判定し失敗した。必要RuleがProductに実在しないという証拠ではない。既存CLIのindexモードを10番目のReadとして追加した[修正Run #42385726717](https://github.com/hat47x/tei-platform/actions/runs/42385726717)は`bounded-design-context` job **completed/success**。同一PRの新旧Runと[並行Draft #3324](https://github.com/hat47x/tei-platform/pull/3324)の別方式を一体実証として合算しない。

**VA-04の観測欄にRequired-Set Witnessを追加**（新Context Packet/検査器を作らず既存TEI #3262 Consumerを参照）：

| 入力／観測 | 採点できるClaimと反証 |
| --- | --- |
| Independent Required（用途・Subject・Rule/Relation・Source Role/Anchor・版） | 必要3 Ruleまたは狭い1 Rule＋Relationを**事前独立固定**。Consumerが返した件数からRequiredを後付け推定しない |
| Actual Discovered→Loader Read→Parser/Binding→Source Index | JSON構文成功・World/Index FP一致・`source-index`の**subject/indexモード**は別。DefinitionのRole/Path/ArtifactとSource実Read、Canonical属性を必要Scopeだけ突合 |
| Actual Tool Reply→Consumer Received | 連続10 CLI Readの一致は原子的な同一時点Snapshotではない。外部H2/H3のTool Response欠落・8KiB切断・Network/OS非露出はG0/G1/G2の別Witness |
| Independent Expectedと適切な保留 | Required Rule省略・重複/曖昧・Wrong Role・未Readは`partial/unknown`で拒否し、非Required Subject省略は正当に通す。既知T1-Aと未知T1-Bを分け、過剰停止と誤完了を同じ分母で扱う |

**採用順**：既存[#3262](https://github.com/hat47x/tei-platform/issues/3262)と[#3223](https://github.com/hat47x/tei-platform/issues/3223)のOwnerが#3326の独立3 Rule照合と#3324のRule+Relation/Canonical照合を整理し、一本化したexact HEADで正負対・Source/Lock変更・Result digestを確認。次にLoader→Parser→Evaluatorの実到達を1件、最後に未知Ruleを隠したT1-Bの盲検試験へ。**初回TAI #168のH2/H3のG0/G1/G2を追加で止めない**。

**資格**：保存済みTEI実CIの範囲は限定Observed。Owner受理、正式Product Design Context API・T1-B・C1／全Required・外部Consumer E2E・実Provider/Hostの一Attempt ClosureはNOT RUN。



## 10. 2026-11-08：局所の正の証拠と、不在を断定する証拠

**成熟した原則**：あるSource/Scope/Attemptについて実行・受領・Assertionを確認できた局所の正の証拠は保持する。一方、対象が一覧に無いことから「不存在」「未テスト確定」と主張するには、独立Required集合、列挙終端、選択・Loader/Parserの実読込、受領、開示範囲の閉包が必要。部分集合は局所成功の取り消しでも全件成功の証明でもない。この区別は[TEI #3223 §29](https://github.com/hat47x/tei-platform/issues/3223)、[TEI #3262](https://github.com/hat47x/tei-platform/issues/3262)、既存Driver Scenario #1180の受入境界を利用し、第二のCoverage Engineを作らない。

### 10.1 直近のSource状態を補正
- **統合済み**：[TEI #3354](https://github.com/hat47x/tei-platform/pull/3354)は2026-11-07 16:35Zにmerged。旧競合[#3324](https://github.com/hat47x/tei-platform/pull/3324)・[#3326](https://github.com/hat47x/tei-platform/pull/3326)はclosed/unmerged。#3354の[exact PR HEAD CI #42391707962](https://github.com/hat47x/tei-platform/actions/runs/42391707962)は、11実CLI Reply、独立Required3 Rule、32合成Consumer判別、既存6 pinned Stepと既知T1-A第7 Stepを限定PASS。これをmain統合後の別Run合格や全Required/業務意味/C1へ昇格しない。局所Go C0相当10.0%、C1未測。
- **未統合**：[Draft #3365](https://github.com/hat47x/tei-platform/pull/3365)はTT-105/106で部分目録と局所Receiptを分離。[#3223が報告するCI #42394673357](https://github.com/hat47x/tei-platform/actions/runs/42394673357)はこのDraft HEADの限定成功であり、全Product Coverageはunknown。局所肯定は保持、目録未受領は「未テスト確定」にしない。
- **合法な異形**：[Draft #3370](https://github.com/hat47x/tei-platform/pull/3370)はrequirementsの正常な空配列result、外側successShape、envelopeの相違を分ける。DraftのresultShapeをmainのDiscovery能力と呼ばない。CLIで正常に返った空配列は、全Subject不存在やTool Reply欠損の証明ではない。
- **Consumer・物理観測**：[Draft #3371](https://github.com/hat47x/tei-platform/pull/3371)のStudio Inspectorは未選択Factoryでのfallback拒否等を提案するが、CLI/Studio同一選択Provider実呼出は未資格。[Draft #3372](https://github.com/hat47x/tei-platform/pull/3372)のWorkbench FK/UNIQUE/Indexは合成Physical観測で、Accepted Business Relation/実DDL/SHO図面とは別。[TEI #3353 merged](https://github.com/hat47x/tei-platform/pull/3353)は空集合Handoffの確認条件を修正したが、HandoffConfirmedは依然Caller申告で実相手の受領証拠ではない。

### 10.2 三資格を別々に判定する
| 既存Ownerの資格 | 局所的に肯定できること | 守る負例・止める主張 |
| --- | --- | --- |
| **D: Design Input** (#3262) | 独立Requiredの範囲でSource/Role/Rule/Relationが実Loader/Parser/Scopeへ到達 | 正常JSON・FP一致でもRequired一件欠落するTT-56を拒否。合法な空配列、別mode、未選択Plugin、未Loader Markdownを無条件に全体失格にしない |
| **T: Tool/Consumer Delivery** (TAI #168/TEI #2509) | 同一AttemptのTool Callと全Reply/生byte/end、受領先を照合した範囲 | 56 Call/55 Reply、8,192 byte切詰め、SHO別Fixtureのdigest一致を完全なH2/H3受領や実同一File H1に昇格しない |
| **G: Test Generation/Oracle** (#1180/#2514/#3273) | 既知の行番号0を検出したT1-Aの局所実CLI結果 | 未提示ObligationをAIが盲検発見するT1-B、C1/全Coverageは別の独立Expectedで評価。既知Caseの繰返しはT1-Bではない |

**対称な判別**：必要なRuleを見逃す＝誤受入、不要Subjectの不在で全作業を止める＝誤拒否、部分目録で既存6 Stepの局所成功を消す＝過剰失効、6 Step実行で全Ruleを網羅したとする＝過剰昇格。False accept／false rejectを別件数で比較し、未確認をどちらにも繰り入れない。

### 10.3 次の実証順序と受け渡し
1. **D一件**：既存main #3354のContext Consumerに、合法なrequirements空配列・Source Index mode・独立Requiredの一Function不足を加え、Loader/Parser/Rule実到達と提示不足を区別する。Draft #3370の契約を先取りしない。
2. **T一件**：TAI #168/TEI #2509の既存Harnessで、H2一比較適格Sessionの禁止Read実拒否、Tool全Call/Reply、Session Log/Egress、実Consumer受信を同一Attemptで記録。H3実Loadは既知ObservedだがH2/H3比較は**適格0/4**。
3. **G一件**：既知T1-Aを基線に、未知Obligation発見T1-Bを未提示Holdoutと独立Oracle/Mutantで検証。正例の必要情報が不足する場合は局所探索のみ継続し、qualified生成とは呼ばない。
4. **並行して独立**：Inspector A/Bのselectedとactual invokedの一致（TEI #1251/#3371）、WorkbenchのPhysical→Business Meaning受理（#3270/#3372）、SHO Writer原文保存（SHO #4）とSUI→SHO同一実File受領（SHO #21）。互いを全面完成の前提にしない。

**記録水準**：本追補はGitHubの既存Issue/PR/CI報告の照合と文書更新だけ。#3354の局所CI、#3365 Draft CIは各Ownerの履歴証拠であり、本VA-04で新たな実CLI/外部H2/Plugin/SHO/独立T1-B/Owner受理を実行したわけではない。各新実験は **NOT RUN**。新しい共通Gate/Reader/Runner/Registry/Hostは設けない。
