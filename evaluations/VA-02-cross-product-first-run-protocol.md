# VA-02：製品独立性を保った初回実証・証拠引継ぎ手順

- **状態**：2026-11-04、横断設計の実行手順案。実行試験・独立モデル反証・Owner受理は **NOT RUN**。
- **統括**：[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)／[VA-01](VA-01-product-value-necessity.md)／[横断計画](../docs/yi-constellation/product-value-scope-audit-2026-11-04.md)。
- **目的**：既存G0〜G4とVA-01の価値比較を、TEI単独→入口差→外部Harness→委任/Consumerへ進められる、実行・停止・証拠判定の手順にする。新しい共通Host、Scenario SSOT、資格Registry、Agent Runner、巨大な共通Schemaを作るものではない。
- **管理境界**：各Productの要件・意味・認可・テストの正本はそのProductに残す。この文書の例は合成Fixture案であり、業務意味や実製品の挙動を認定しない。

## 1. 分離したまま前進する実証ラダー

| 段階 | 試す能力・最小構成 | 開始条件 | 出口の証拠／次へ進めない場合 |
| --- | --- | --- | --- |
| P0 出典・Oracle固定 | TAI/TEI/EKI/SHO/SEI/SUIのIssue・main・対象Sectionと合成fixtureを記録 | Product Ownerの既存Issueと権限が特定できる | full SHA、Issue取得時点、未確認範囲、生成Agentから独立したExpected。未固定はNOT RUN |
| P1 TEI単独 | [TEI #1180](https://github.com/hat47x/tei-platform/issues/1180)でmainに存在する6-Step保存ScenarioとCLI verify/generate/run/checkをCharacterizeし、AI拡張候補を別に評価 | 2026-11-04にmainのScenario JSON/Parser/CLIの実ファイルを確認済み。対応範囲/実試験の成功は別検証 | 固定6 StepのCoverage、pins/digest、独立Expected、実Readと非対応拒否を別票。Sourceの存在だけで製品PASS/Web E2E成立としない |
| P2 入口差 | 同じAccepted Application/ScenarioからCLIとWeb経路を実行 | Target binding、Host/Policy、実行環境を個別に固定 | 共通Business AssertionとTarget固有のAuth/Transport/UI/Visualの別票。CLI PASS≠Web PASS |
| P3 外部Harness | Product CLI単独(H2)と必要時だけSkillを読む(H3)を同一公開入力で比較 | 実binary・Skillの現行版、必要なTool、許可された開示範囲 | Tool発見→実呼出し→結果Reader→再開を観測。説明だけの能力は不合格。二つ目のHarnessは独立の別実験 |
| P4 単独Consumer/委任 | SHO L0 Markdown保存と再読込／EKI #58の非分散判定（実装のSuitability結果値は別途固定）を各々単独で確認 | SHOは[SHO #4/#7](https://github.com/hat47x/sho-composer/issues/7)、EKIは[Suitability #58](https://github.com/hat47x/eki-fabric/issues/58)の現行契約を確認 | SHO文書保存≠原典を理解、EKI Task完了≠Body受領・業務Effect。各製品が単独成立するかを先に判定 |
| P5 任意の連携 | TAI再開→TEI証拠→EKI Attempt→SHO Consumerという**必要な部分だけ**のHandoff | P1〜P4の該当部分が実証済み・公開可能なsynthetic projectionがある | 同一Attempt・同一Source/Semantic/Toolchain/Provider・Consumer実Readと現在資格。連携不能でも単独製品のPASSを取り消さない |

**依存規則**：P4のSHO単独とEKIのLOCAL判定はP1〜P3完成を待たず並走できる。P5を全製品の標準起動順序と解釈しない。Go単一バイナリはTEIの基本配布形態だが、Function/Invocation/Trigger/Buildを混同せず、必要性を示せないMulti-Buildを初回必須にしない（[TEI #1130](https://github.com/hat47x/tei-platform/issues/1130)、[#2600](https://github.com/hat47x/tei-platform/issues/2600)）。

## 2. 操作と証拠の7段階（第二の共通状態機械ではない）

| 状態／Claim | そのClaimに必要な観測 | それだけでは言えないこと |
| --- | --- | --- |
| Declared | Skill/DSL/Operation定義と対象Source | 現在のCLI/Toolに実装されている |
| Available | 実binary/version・Tool discovery結果 | 対象・引数・現在Grantが解決した |
| Resolved | Operation ID、Target Identity、Scope、Context、引数 | 実Providerが許可した |
| Eligible | 実Host/Providerでの当該時点の認可、Disclosure、対象Policy版 | 実行・Commitが起きた |
| Observed effect | 実呼出し、実作用、明示的な失敗/未知Commit | ArtifactをConsumerが受領した |
| Received | 同一AttemptのBody/digestとConsumer/Readerの実Read | 正しい意味・品質・Owner受理 |
| Qualified | 独立Expected、業務条件、該当するOwner受理（必要な場合） | 後続時点・別Scopeでの現在資格 |

前段がUnknown/Partial/Deniedなら後段を推論でPASSへ上げない。過去にQualifiedだったEvidenceは履歴として残し、現在のEligible/再検証を独立判定。異常は最低でも「未探索」「取得失敗」「部分取得」「許可拒否」「不明Commit」「未受領」「NOT RUN」を分ける。

## 3. 初回Negative Oracle（設計済み、実行はNOT RUN）

VA-Xは一次案に依存せず、各期待値を先に固定する。合成データの値や業務Ruleは各Product Ownerが受理したFixtureに従う。以下は**状態判定のExpected**であり、実プロダクトのテスト結果ではない。

| ID | 合成入力／注入 | 独立Expected | Owner |
| --- | --- | --- | --- |
| V02-01 | Skillにはあるが現binaryのCLI/Tool未実装 | Declaredのみ、Available=false。自動fallbackでSuccess禁止 | TAI #168、TEI #1180 |
| V02-02 | CLIで実ReadとBusiness Result一致、Webは別Subjectで403 | CLI Businessの結果のみPASS。Web E2E FAIL/Denied、同等のAuthを主張しない | TEI #1180 |
| V02-03 | 対象1,001件・取得上限1,000、またはRelation未取得とSQL NULLの混在 | Completeness=partial、NULLとmissingを混同せず、「該当なし」判定禁止 | TEI #2516、TAI #271 |
| V02-04 | 更新POST送信後503、Commit返答なし、同一要求再送候補 | Effect=unknown。Receipt確認前の無条件再試行を拒否。送信済みと未送信を分ける | TEI #1130、EKI #58 |
| V02-05 | Source A→B→A、同byte別Toolchain、Role/Policy変更 | Artifact可再利用・Evidence可再利用・Meaning再受理・現在Grantを各別判定 | TEI #2600、TAI #271 |
| V02-06 | EKI Claim ACKのみ、Body欠損または別AttemptのBody | Received=false、AcceptedResult/SHO実受領へ昇格不可 | EKI #407/#465、TAI #271 |
| V02-07 | 同じ故障ドメインの安価Workerへ再割当、締切前に回復不可 | Fabric選択を成功としない。現行実装の3値とAdmission/Policyの拒否を分離し、ADRの4値との差はEKI Owner判断待ちとして比較 | EKI #58 |
| V02-08 | SHO Markdown 3リンクの保存・再開、原典URL移動・同名異内容 | 文書保存は独立PASS可能、原典再解決/引用の現在性は別FAIL/Unknown | SHO #4/#7 |
| V02-09 | 履歴Evidenceは一致するがHost Grant失効、read-only操作は継続可能 | 履歴Evidence保持・危険ActionはDenied。過剰な全停止も無条件実行も不適合 | TAI #232/#271 |

**追加保留**：Graphの同名別ノード、1:N fanoutと業務キー、時間有効な組織所属、Sourceのpartial/offline、Generatorの未対応StepはTEIの既存Owner Issueへ接続し、横断VA-02で第二Fixture正本を作らない。

## 4. 事前登録と実行記録（Issue/PRの一表で足りる）

各Runは次の列を欠かさない。

| 区分 | 記録 |
| --- | --- |
| 入力同定 | Case ID、User Job、Baseline B0/B1/B2、repo full SHA、Issue/Section取得時点、Scenario ID/revision、実データ分類 |
| 実行経路 | binary/tool/plugin/generator version、Target、Host/Provider、Subject/Scope/Grant、Entry Surface、Task/Attempt ID（該当時） |
| 独立性 | Expected作成者、固定時刻・保存場所、実装者との資料共有範囲、VA-X別context/別model実績、VA-E監査 |
| 観測 | 実コマンドと終了状態、HTTP/Provider effect、実Read bytes/digest、Consumer receipt、failed/partial/unknown/stale |
| 比較 | Outcome correctness、安全・意味不変条件、壁時計時間、計算/Token/金額、移送量、人の審査、回復余裕と再実行費用 |
| 判定 | Source-static / synthetic-executed / product-integrated / real-world-observed / owner-accepted、NOT RUN、残余Unknown、Ownerへの提案差分 |

**報告規則**：出典の一致、実試験、利用者の成果、採用判断は別段階。「CLI 0終了」「Studio Committed=true」「Claim ACK」「同じDigest」「モデル多数決」のどれも上位段階の代替にしない。Secrets、私的Raw、非公開Oracleは公開Issueと外部Harnessへ送らない。OS/Hostの実隔離はTAI #232が所有する。

## 5. 実証へのGo/No-GoとG0〜G4への接続

1. **G0**：P0で固定できなければ下流のPASS宣言禁止。主なIssueは #422、[TEI #1180](https://github.com/hat47x/tei-platform/issues/1180)、[EKI #58](https://github.com/hat47x/eki-fabric/issues/58)、[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)。
2. **G1**：V02-01〜09のExpectedを独立に事前登録。少なくともV02-02とV02-07で、「削ると壊れる案」と「増やさなくてよい案」の双方をVA-Xが反証する。
3. **G2**：P1/P2とEKI単独P4を先行実行。可用性が無い・実Provider未接続の場合はstatic観測/NOT RUNまでとし、想像によるPASSを付けない。B0/B1/B2で権限や保証が違えば比較不能と表記する。
4. **G3**：VA-EがSource/版/入力範囲/Host・Actual Read/結果の主張を照合。各Product Owner Issueへ小さな差分を提案し、#422には索引と異論だけ還流する。
5. **G4**：Source、Role、Toolchain、Provider、Grant、Consumerを個別に変えて再資格化範囲を確認。実Artifact/証拠/意味/資格の失効判定を独立に記録。

**Exit**：VA-T2・VA-E1のそれぞれで実測の正例/負例、独立Oracle、VA-X・VA-E署名相当の明記、B0/B1/B2比較可否、少なくとも一つの実Consumer/Reader観測が揃うこと。ただし汎用Scenario拡張・Web E2E生成/実Host/実EKI Provider/外部Harness/Owner受理は別々の未達として扱う。

**現状**：この文書自体はSource-staticの提案。2026-11-04時点でV02-01〜09の実行結果、実Harness比較、独立モデル割当、正式なProduct受理を示すものではない。


## 6. 2026-11-04 Source再確認：AI-firstテスト拡張の三層

前段P1の「保存Scenario未実装」は古いIssue記述由来であり、現在のmainの限定実装に対して誤り。2026-11-04に下記のファイル実体を確認。これは**Source-static**であり、今回のGo test/CLI実行成功を意味しない。main full SHAとDraft HEADは各実証RunのG0で別途固定する。

- [保存済み6-Step JSON](https://github.com/hat47x/tei-platform/blob/main/reference/driver-scenarios/order-entry-pattern-smoke.json)（schema: tei.driver-scenario/v0、blob SHA 371487312eacf2cbd7f425f33ea1ce5dfc9dfec3）
- [Scenario parser](https://github.com/hat47x/tei-platform/blob/main/internal/scenariotest/scenario.go)（blob SHA 5990584dbf1415363a1940092d4e388ef757bb74）
- [CLI implementation](https://github.com/hat47x/tei-platform/blob/main/cmd/tei/scenario.go)（verify/generate/run/check、blob SHA a6525579fc083060b400c970990a64d57fd0a6d3）
- [TEI Draft PR #2811](https://github.com/hat47x/tei-platform/pull/2811)：AI-first Scaffold/Coverage設計。限定実装とWeb E2E未検証を区別（open/draft）。
- [TEI Draft PR #2813](https://github.com/hat47x/tei-platform/pull/2813)：AIがJSONを追加するPipeline構文・Operator pin・型連続性・Source byte spanのテスト専用Reference（open/draft）。保存業務Scenarioの正本ではない。

### P1で混同しない三層
| 層 | 保持する正本/役割 | AIが拡張できること | 禁止する昇格 |
| --- | --- | --- | --- |
| L1: Pipeline Candidate | #2813等の構文/型/Operator固定テスト。業務意味のSSOTではない | 固定Anchorを改変せず候補JSON・負例を増やす。Expectedは独立点検 | Candidate PASS→Accepted Scenario/業務意味 |
| L2: Driver Scenario | Accepted Canonicalは意味SSOT、保存済みScenarioはシナリオテストSSOT | 隔離コピーでCase/Step候補を提示し、verify/generateの差分を観察。Accepted本体の自動上書きは不可 | 現存6 Step→任意Command/Provider対応済み |
| L3: Target Evidence | CLI plan/run、将来のWeb E2E、実Provider effect、Consumer readは派生物/観測 | 実Target・fixture・Grantがある範囲のみ実行 | CLI PASS→Web/Auth/Commit/Owner受理 |

### G0〜G3に追加する最小の実験（提案・NOT RUN）
- **AI-EXT-01: 拡張性** — main/PR HEADと基準JSONを固定し、AIが新JSONファイルで正例・不正Type・effect拒否候補を追加。重複JSON member・Operator pin・UTF-8 source位置の拒否を観測。独立Expectedを事前に別担当が保管。採用を自動決定しない。
- **AI-EXT-02: 既存Scenarioの上限** — 6-Step保存Scenarioのverify→generate→run→checkを同一版で実行。対応Operationのみを数え、意図的なStep欠落、stale fingerprint、未知Operationのfail-closedを検証。Web E2Eと実DB/Host Writeは別Run/NOT RUN。
- **AI-EXT-03: Coverageの分母** — L1候補数、L2 Step/Rule/Branch/データ分割、L3 Target/Host/Effect/Consumerを別分母で列挙。enumerated、applicable、attempted、executed、asserted、independently-qualified、unsupported、unknownを区別。空分母と未発見を100%にしない。Candidate件数が増えても未試験Targetが合格に変わらない反例を採用。

**変更後の優先順位**：「新Scenario基盤の再実装」ではなく、**現有CLI/Scenarioの範囲固定→AIに自由な候補拡張→独立ExpectedとCoverage/差分→Target/Host実検証**。実行やOwner受理がない限り製品PASSと書かない。実装と試験SSOTはTEI #1180/PR #2811/#2813のOwnerへ戻し、VA-02は横断判定の索引に限定する。


## 7. 入力閉包・CLI Discovery・EKI結果値を実証前に再照合

[VA-04：入力閉包と契約発見の事前確認](VA-04-evidence-readiness-preflight.md)をP0→P1の**証拠Claim限定**に接続する。TEI #2822/#2823の実再現ではvalidate ok=trueでも利用者宣言0件またはSourceが未読込となり得る。[TEI #2824](https://github.com/hat47x/tei-platform/issues/2824)ではdiscoveryと契約一覧にドリフトがある。従って**Scenario/World/Toolchainのfingerprintがあることは、その前段で要求されたSourceがすべて実消費された証拠ではない**。

- P0：宣言→発見→消費→Assertion→現在資格/実受領を5つのClosureで点検し、欠落/不明/取得不能なら該当Claimをlimitedまたはunknownと表示。安全な静的候補追加は継続してよい。
- P1/AI-EXT：既存6-Step ScenarioのCLI結果と、読み込めたUser定義/対象Scope、命令の現行JSON契約、未対応/skipを別々に記録。Candidate増加をCoverage完全性としない。
- P4/EKI：実装側Suitabilityは現時点3結果、ADR-0029案は4結果で衝突（[EKI #698](https://github.com/hat47x/eki-fabric/issues/698) EKI-CA-02）。非分散という業務上の判定と具体enum/Policy拒否を分離し、4値を現行APIと断定しない。
- VA-00：文書整合性の監査S4は[TAI #424](https://github.com/hat47x/tai-pleroma/issues/424)で完了済み（Source-static）。59件のF2 Owner判断項目と修正Draft PRは尊重し、VA-02に第二の文書監査Laneを追加しない。

**更新に伴う分類**：既存CLI/Scenarioの実ファイル確認＝source-static、TEI #2822〜24の製品Issueに記録されたWSL再現＝そのIssueの局所実験、本VA-02での再実行・Web/Provider/EKI E2E＝NOT RUN。証拠の水準を混合しない。

## 8. 実在するテスト候補とSource→Buildの資格を分離した最初の二実験（2026-11-04）

[#1180](https://github.com/hat47x/tei-platform/issues/1180)と[TEI PR #2828](https://github.com/hat47x/tei-platform/pull/2828)を照合した結果、**AIがJSONの候補を追加→既存Scenario CLIを再利用**する最小test-only経路はSource上の具体案として存在する。一方、[#2819](https://github.com/hat47x/tei-platform/pull/2819)には**宣言Source D1と実Goビルド入力D2の不一致を現状で拒否できない**限定的な再現がある。単一のSourceDigest・BinaryDigestがあっても、実入力の一致が保証されなければBuild資格を主張しない。#2819の発見をTEI全体のあらゆるBuildに一般化せず、対象Selectorでの既知の不一致として扱う。

| 事前登録ID | B0/比較する小さい操作 | Expectedと失敗注入 | 実行結果として主張できる上限 |
| --- | --- | --- | --- |
| **V02-AI-01：追加候補の判別力** | 保存済み6-Stepを変更せず、#2828のJSON候補（Validation成功/拒否）を既存 verify→generate→check→pinned run へ渡す。Go test-onlyの固定Anchorと独立Oracleを比較 | 固定Case/Stepの衝突、Expected改変、旧生成Plan、入力Parserの未サポートStep、同根Expectedによる偽PASSを別々に注入。独立Expectedは候補の作成者と分離し、少なくとも既知Mutantを1件検出 | #2828のコードとPR説明の**存在はsource-static**。同HEADの実テスト/CIがPASSした場合でも限定CLI/Fixtureまで。実Web/Auth/Provider、6-Step業務意味の全面受理、全分母Coverageは別 |
| **V02-BUILD-01：宣言と実消費Sourceの束縛** | 同一のGo入力を宣言・ビルドするcontrolと、宣言D1/ビルドD2を意図的に食い違わせるcase（#2819の既知反例を再利用） | Controlは宣言と実Build入力のbyte/順序・Generator/Toolchain pinが一致したときだけ資格候補。Mismatchは少なくとも**現行の不一致を露出する**こと。修正後は該当Selectorがfail-closedになること | #2819で確認されたのは特定Selectorの不一致受容（source-staticで記録された製品側局所試験）。修正EB-04や実TEI全Target E2Eは未確認。Byte一致≠Owner Meaning/Host Grant |

**最初の判断順**：①製品側の実Baselineとexact HEADを固定、②独立Expected/既知Mutantを別担当に委ねる、③既存テスト・既存CLIの範囲内で上記二Caseを実行、④必要になったときだけWeb/Provider/外部Harnessへ接続する。過剰要件判定では、**追加Case数やRunnerの機能数ではなく、誤PASSを拒否できた範囲・独立Expectedの判別力・導入/保守の費用**を測る。

**他の独立レーン**：TAI [Draft #270](https://github.com/hat47x/tai-pleroma/pull/270)のH2（外部Harness+Product CLI、Skillなし）/H3（同Harness+実ロードした必要Skill）の4独立Sessionは、モデル/Tool/Source/Grantを一致させて比較する。TEI Product Skillの静的CIやmainの存在は、そのTAI Harness上でのSkill実ロード・追加価値の証拠ではない。SK-02がすでに保持する既存Checkerと評価票を再利用し、VA-02側へ第二Skill評価Runnerを追加しない。

**現状**：本節は既存Issue/PRのSource-static照合に基づく反証手順。V02-AI-01／V02-BUILD-01の本活動による実走、独立Expected、TAI H2/H3の実Harness、TEI実Web/DB、Owner意味受理は**NOT RUN**。Product側局所CIの事実は実験Ownerとexact HEADごとに再確認する。

## 9. 11月5日以降のRead/Write二経路：同じ価値と実行資格を混ぜない

[TEI Critical Path #1119](https://github.com/hat47x/tei-platform/issues/1119)と[TAI #422のVA-TEI受渡し](https://github.com/hat47x/tai-pleroma/issues/422#issuecomment-6655780152)に従い、VA-T2を**VA-T2-R（参照）／VA-T2-W（更新）**へ分ける。どちらもB0通常手段とB1 TEIを同じUser Job／Source／独立Expectedで比較し、B2汎用化を標準条件に含めない。

| 比較票 | 最小固定条件 | 必須正例・負例／結果の記録 | 現在地 |
| --- | --- | --- | --- |
| **VA-T2-R** | 同じ公開Source、実CLI版・実読込Source closure、Read-only Tool/Skillの有無、Warning/Unknown、独立Expected | 対象Source存在と正常Read／宣言したが読んでいないSource・空Workspace・部分対象・同名Source移動。正答、unknown保持、必要な操作数・再検証時間を個別記録 | TEI #1180の保存6-Step/限定CLIと#2822〜24の負例を再利用。今回のB0/B1実試行はNOT RUN |
| **VA-T2-W** | 一件のFunction・Purpose・Target/Key、Provider、OperationID、Caller/Grant、PG Schema/Period、実Commit/Receipt/独立Reader | 正常一回適用／認可拒否／Commit応答喪失unknown／同Key replay／別Key ABA再適用／Rollback後の先行副作用。実Effect・Business Result・Reader取得・二重適用の有無を別列 | TEI merged #2853は製品Invoker+実PGの限定成功、merged #2854はABAの反例。横断の同一Revision/Web/Host/Consumer受入はNOT RUN |

**Source→Acceptanceの連鎖**：宣言→発見→実Parse/Read→実Build/Runtime消費→個別Oracle/Guard→現在Grant→実Effect→独立Reader→Consumer/Owner Meaningを、当該Claimに必要な段階だけRequiredにする。AのReadにはWrite Effect不要、BのWriteにはCallback ACK/RunPlan precheckだけでは不足。各試行ごとに`required／observed／unknown-or-undischarged／exact revision／environment／independent oracle／elapsed+review cost`を既存Issueコメントに記録するだけでよく、共通Receipt DBは作らない。

**次の拡張候補（未採用）**：[TEI #2555](https://github.com/hat47x/tei-platform/issues/2555)の旧新並走／Migration段階、[#1251](https://github.com/hat47x/tei-platform/issues/1251)のPlugin Bundleの実選択依存、[#2831](https://github.com/hat47x/tei-platform/issues/2831)のG4セルフビルドは、各自のUser Jobを指定してから比較。業務Writeに全Migrationフレームワーク、Readに全Self-buildを前提化しない。

**受入資格**：TEIの局所PG試験・別IssueのCLI CIを利用可能な既存Evidenceとして提示できるが、各々のexact HEAD/実行環境/対象/Scopeを維持し、異なるRunを単一TEI価値実験のPASSへ合成しない。VA-X別モデル反証とVA-E独立Oracle照合、実User Jobの費用比較、Owner正式受理は本比較ではNOT RUN。

## 10. 変更・再起動・選択先更新時の限定再資格化（11月5日議論の反証票）

[横断計画§17](../docs/yi-constellation/product-value-scope-audit-2026-11-04.md)のN0〜N3を、新しい実行方式でなく**既存Case／Receiptを再利用する故障注入**としてVA-02に接続する。

| ケース | Setup／正負の対照 | Expectedと誤成功の拒否 | Owner・現在の実証 |
| --- | --- | --- | --- |
| **V02-RCV-01** | TEI Commandで応答不明→同一Key／同じOperationでProvider Receipt lookup→Lifecycle再起動相当。対照は別KeyでA→B→Aを経た更新 | 同じKeyのPG側replayを「新しい業務実行成功」にしない。Restart後のin-memory unknownの消失は回復成功でなくGuard喪失。別Key ABAによる再適用を検出し、Provider確認まで新Key再送禁止 | TEI [#2870](https://github.com/hat47x/tei-platform/pull/2870)／[#2854](https://github.com/hat47x/tei-platform/pull/2854)／[#1174](https://github.com/hat47x/tei-platform/issues/1174)。局所実PGは他Ownerで観測。本VA-02の同一Attempt実製品E2EはNOT RUN |
| **V02-MIG-01** | Expand→Backfill→Validate→Cutover→Contractの限定2 Client。旧側の歴史的Read、Cutover後の同じ表面値・別Owner、CDC遅延0件、ACK Unknownを各1件 | 行数一致／逆同期差分0／同一WorldFPから現在read/write主体・全不存在・現Grantを推定しない。過去Readは履歴として保持し、必要時に現在Cohort/Scope/Watermarkと元OperationIDのReceiptを再確認 | [TEI #2555 MIG-H01〜07](https://github.com/hat47x/tei-platform/issues/2555)、[TAI #271 SC-13](https://github.com/hat47x/tai-pleroma/issues/271)。本横断実移行はNOT RUN |
| **V02-SEL-01** | 同じTEI Targetに未選択Pluginを追加/更新（N0）と、実選択Provider/Nested moduleの依存を変更（N1） | 未使用変更で必要Target Artifact/実initが変われば非干渉失敗。一方、root test PASSでも選択Studio moduleのgo.sum不足ならTarget不適合。選択された実依存の欠落を未使用非干渉の成功で相殺しない | [TEI #1251 PB-01/02/07/10](https://github.com/hat47x/tei-platform/issues/1251)、[TEI #2831](https://github.com/hat47x/tei-platform/issues/2831)。PB-10の歴史的バグはmainで修正済み。本横断実BuildはNOT RUN |
| **V02-SHO-01** | 一文書Markdownを固定Parser profileでReadしてL0作成。未選択Parser追加（N0）／選択Parser欠落（N1）／原文移動/Review版変更（N2） | 明示固定Parserなら未選択候補追加で索引自動失効を強制しない。選択Parser欠落は無音fallback禁止。索引値再利用と現在引用/Review/外部AI送出資格を別判定。L0保存・再開は継続 | [SHO #7 RI-PS01〜07](https://github.com/hat47x/sho-composer/issues/7)、[#4 FR-01〜08](https://github.com/hat47x/sho-composer/issues/4)。実SHO ReaderはNOT RUN |
| **V02-H23-01** | TAI H2（Tool-only）2試行/H3（実Product Skill Load）2試行、公開TEI 1 Subject、同じ実CLI/Source/Oracle/Host条件 | 実Loaded Witness＋実Tool argv/Scope/Warnings＋独立Expectedと費用を分ける。Skillファイル存在、人工Checker PASS、Product単独CIをH3のSkill追加価値と呼ばない | [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)・[TAI Draft #270](https://github.com/hat47x/tai-pleroma/pull/270)。実四Harness SessionはNOT RUN |

**Go/No-Go**：各ケースにRequired Source/Condition、独立Expectedの出典と版、実行Byteと環境、実際に使ったSelector/Parser/Provider、実Observation、現在Authority/Disclosure、実Readerの受領を**必要な範囲だけ**記載する。Not-run・unknown・unavailable・unsupported・拒否は区別し、Caseが成立しないときは当該User Jobの結論のみ保留。単一のRunの成功を別Target/別Revision/別Ownerへ転載しない。

**最初の実行順**：V02-H23-01を先行（TEIのProduct-only S1の実データは対照に留める）。並行してV02-RCV-01の合成→実PG局所を既存Ownerで確認。その後、明示的なPlugin選択の最小A/B、SHO製品Reader、実旧新Client移行へ順に拡張。H23の初回実行へ実DB MigrationやStudio/SHO完成を必須化しない。今回は**実行なし・評価票更新のみ**。

## 11. 11月6日：拡張子移行・Skill割付・SHO G1bを独立に反証する

[横断計画§18](../docs/yi-constellation/product-value-scope-audit-2026-11-04.md)に接続。**TEI `*.tei.md`方向転換の実装/互換性判定、TEI/TAI実Harnessの増分価値、SHO G1b Parserの正式受理を同じPASSへ潰さない**。独立ExpectedとSource/Build/Attempt/Ownerの参照を既存Case/Issueへ付けるのみ。以下は追加の試験**案**であり、実行済みFixture・CIではない。

| 番号・Owner | 固定するControl／独立負例 | 期待結果・禁止推論 |
| --- | --- | --- |
| **FMT-01：.tei.mdの意図表示** ([TEI #2621](https://github.com/hat47x/tei-platform/issues/2621)) | plain.md、OKF`tags:[tei]`付き.md、`model.tei.md`の3入力。説明表と未確定Rule、実Parser対象を混在 | `*.tei.md`という認識可能性は高めても、名前/tagだけで構造を解釈済み／OwnerがMeaningを受理済み／実Build許可としない。SHO単独Markdown編集は継続 |
| **FMT-02：旧.tei→.tei.md移行** ([TEI #2621](https://github.com/hat47x/tei-platform/issues/2621)/[#1180](https://github.com/hat47x/tei-platform/issues/1180)) | 同一原byteの旧名/新名、旧Source Reference/Workspace manifest/Build Selector、移動後のSourceIndexとDiagnosticを別取得 | 移行前後に実Readerが何を読んだかを数え、未読込が黙って`ok`となったらfail/unknown。Source path/Occurrence変更とMeaning byte不変を区別し、旧Receipt/Reviewを現在資格へ自動復活させない。移行互換規則はOwner未決 |
| **FMT-03：編集の忠実性** ([TEI #2621](https://github.com/hat47x/tei-platform/issues/2621)/[#1440](https://github.com/hat47x/tei-platform/issues/1440)) | 表・式・DOT・フェンス・CRLF/UTF-8を含む`*.tei.md`。No-op Save、一意箇所の値Patch、曖昧/競合Patch | No-opでbyte同一、構造化編集で非対象byte不変、選択外の未確認意味を自動確定しない。AI候補は根拠・不明とともにPreview、同じAIが生成したExpectedは独立Oracle不可 |
| **H23-RD-01：割付／実提供** ([TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)/[#488](https://github.com/hat47x/tai-pleroma/issues/488)) | 固定Participant Task raw byte・同Source/Model/Tool/Grant。H2/H3各2 Session。H3でSkill非ロード、H2にSkill混入、CLI未実呼出しを各負例 | R=割付とD=実ログ証明を分離。H3未ロードをH2成功へ付替えずITTに全4試行を残す。PPは実提供成立試行だけ採点。Tool原結果・独立Expected/Warning/Unknown・時間/Token/Review費用を別取得。4試行だけで有意な一般差を主張しない |
| **SHO-G1B-01：索引の限定被覆** ([SHO #16](https://github.com/hat47x/sho-composer/issues/16)) | 固定Markdownとraw BOMあり/なし、未定義Reference Linkと定義済みLink、2MiB境界、同一Parser profile/lock | BOMで同じ索引でもraw SHA相違を明示。サイズ超過は原文非書換え・適切な拒否。未解決候補のdiagnosticは`unresolvedReferenceCandidatesEvaluated=false`のままなら**未検証**とする。16/16 CIを全Grammar・Writer・Owner受理へ昇格しない |

**実験の分母と段階**：TEI B0のCLI実Product S1は限定証拠がある。最初の新しい出口は、**外部Harnessが実H2 Tool Request→固定CLI→結果を実受信した1 Session**。その後H3実Loaderを別観測し4独立SessionでITT/PPを区別する。FMT試験はTEI #2621の新方針と互換性設計のOwner決定後に実装Ownerが必要なConsumerへ反映、SHO-G1BはSHO既存#16のOwnerが受理/実行。新Runner・中央Editor・第二Oracle/Scenario SSOTをこのPRで作らない。

**資格**：本§11追加の新Fixture／実Migration／外部Harness H2/H3／TEI Reader/Writer／SHO正式G1b／Owner受理は**NOT RUN**。TEI S1/Prebuilt CIとSHO候補16/16は元Job・版・Scopeに限り既存実験として参照する。

## 12. 2026-11-07：事前拒否、実行後Unknown、独立な誤実装検出を別資格とする

前節のTEI Read/Write価値比較に、現在の限定的なProduct実証を**互いに加算しない証拠**として取り込む。新しいCommand Host・検証基準Store・Mutant Runnerは作らず、[TEI #1174](https://github.com/hat47x/tei-platform/issues/1174)、[#2514](https://github.com/hat47x/tei-platform/issues/2514)、[#1180](https://github.com/hat47x/tei-platform/issues/1180)の既存Ownerが持つ期待値を使う。

| ケース | 正負対照・観測する根拠 | 合格と誤認してはいけないこと |
| --- | --- | --- |
| **VA-W-A01 作用前の拒否** | [TEI merged #3042](https://github.com/hat47x/tei-platform/pull/3042)でAuthorizer未設定は`COMMAND_AUTHORIZER_UNAVAILABLE`、宣言された期間状態が不明なら`COMMAND_PERIOD_STATE_UNAVAILABLE`。認可→期間の順で検査し、未認可呼出しへ期間情報を不必要に返さない。[merged #3047](https://github.com/hat47x/tei-platform/pull/3047)は宣言許可と発行済み許可の不足を判別する局所Go対照 | ReferenceAuthorizerやGrantAuthorizerの局所試験は現在の主体・実Host/CLIのPermission発行や正式Grant接続を証明しない。拒否前にExecutorが未到達かを独立に観測 |
| **VA-W-A02 作用後に結果不明** | Executorが呼ばれた後で宣言外Effect/Outcomeを検出したら、#3042は`EffectUnknown`／Lifecycle `unknown` を返す。事前拒否、作用後unknown、実Receipt＋独立Readで確定した結果を別扱い。元OperationID/Keyを保持 | `rejected`表示、Cancel ACK、期限切れ、`UnitOfWork`存在だけでrollback/no effectとしない。応答喪失後の別Key自動再送を禁じ、Provider照会前はunknownのまま。#3042の実PostgreSQL検証は未実施 |
| **VA-E-M01 AI追加Caseの検出力** | [TEI #2514](https://github.com/hat47x/tei-platform/issues/2514)の正例[PR #2901の限定Health](https://github.com/hat47x/tei-platform/pull/2901)と、誤実装[Draft #3017](https://github.com/hat47x/tei-platform/pull/3017)を**同一Scenario/Fixture/独立Expected**で比較。MutantはEvaluatorのrelation-unique結果を一行だけ誤変更。負例の[Health #42181290981](https://github.com/hat47x/tei-platform/actions/runs/42181290981)では対象AI追加Case自身が実失敗 | CI全体が赤いだけでは検出力とはしない。対象Caseが誤りを検出した局所M1と、他のTestのみ失敗・Infraのみ失敗・Mutant生存を区別。#3017は**意図的に誤ったコードを含む絶対merge禁止Draft**。合格はこの1 Rule/Fixture/Go実装に限定し、全Rule/実Provider・業務Meaning受理を主張しない |

**価値への接続**：VA-T2-Rの公開Source CLI read-only価値や[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の初回H2はVA-W-A01/02の実DB対応や全AI Caseの網羅性でブロックしない。VA-T2-Wで業務Effectを価値とする場合には、作用前拒否と作用後unknownを正しく区別し、Host Grant／Providerの実作用／受領側の独立ReadをそのScopeの必須条件とする。通常成功の正例と異常の負例を**同じSource/操作/独立Expected**で比較し、「全部拒否する実装」が合格する試験も避ける。

**状態**：#3042/#3047は限定的なmain統合済み局所Go試験、#2514のM1は合成Fixture・意図的Redの限定実測。それらを今回のVA横断E2EやOwner意味採用に統合したわけではない。新VA-W-A01/A02/E-M01の同一Attempt横断実行、実DB照会、外部Harness、異モデル独立採点、正式Owner受理は**NOT RUN**。
