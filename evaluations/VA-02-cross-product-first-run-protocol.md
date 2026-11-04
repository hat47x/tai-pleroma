# VA-02：製品独立性を保った初回実証・証拠引継ぎ手順

- **状態**：2026-11-04、横断設計の実行手順案。実行試験・独立モデル反証・Owner受理は **NOT RUN**。
- **統括**：[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)／[VA-01](VA-01-product-value-necessity.md)／[横断計画](../docs/yi-constellation/product-value-scope-audit-2026-11-04.md)。
- **目的**：既存G0〜G4とVA-01の価値比較を、TEI単独→入口差→外部Harness→委任/Consumerへ進められる、実行・停止・証拠判定の手順にする。新しい共通Host、Scenario SSOT、資格Registry、Agent Runner、巨大な共通Schemaを作るものではない。
- **管理境界**：各Productの要件・意味・認可・テストの正本はそのProductに残す。この文書の例は合成Fixture案であり、業務意味や実製品の挙動を認定しない。

## 1. 分離したまま前進する実証ラダー

| 段階 | 試す能力・最小構成 | 開始条件 | 出口の証拠／次へ進めない場合 |
| --- | --- | --- | --- |
| P0 出典・Oracle固定 | TAI/TEI/EKI/SHO/SEI/SUIのIssue・main・対象Sectionと合成fixtureを記録 | Product Ownerの既存Issueと権限が特定できる | full SHA、Issue取得時点、未確認範囲、生成Agentから独立したExpected。未固定はNOT RUN |
| P1 TEI単独 | [TEI #1180](https://github.com/hat47x/tei-platform/issues/1180)の現行test-local Go ScenarioをCharacterizeし、小さな保存済みDriver Scenario→CLI plan生成を比較 | 保存可能Scenarioは**未実装とのIssue記述**があるため、実在確認を先行 | 未対応Stepを黙示skipしないCoverage Matrix、入力/操作/結果/実Read。保存Scenarioが無ければ未実装Gapと記録し、生成成功と偽らない |
| P2 入口差 | 同じAccepted Application/ScenarioからCLIとWeb経路を実行 | Target binding、Host/Policy、実行環境を個別に固定 | 共通Business AssertionとTarget固有のAuth/Transport/UI/Visualの別票。CLI PASS≠Web PASS |
| P3 外部Harness | Product CLI単独(H2)と必要時だけSkillを読む(H3)を同一公開入力で比較 | 実binary・Skillの現行版、必要なTool、許可された開示範囲 | Tool発見→実呼出し→結果Reader→再開を観測。説明だけの能力は不合格。二つ目のHarnessは独立の別実験 |
| P4 単独Consumer/委任 | SHO L0 Markdown保存と再読込／EKI #58のLOCAL判定を各々単独で確認 | SHOは[SHO #4/#7](https://github.com/hat47x/sho-composer/issues/7)、EKIは[Suitability #58](https://github.com/hat47x/eki-fabric/issues/58)の現行契約を確認 | SHO文書保存≠原典を理解、EKI Task完了≠Body受領・業務Effect。各製品が単独成立するかを先に判定 |
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
| V02-07 | 同じ故障ドメインの安価Workerへ再割当、締切前に回復不可 | Fabric選択を成功としない。LOCAL/NEEDS_MEASUREMENT/NOT_SUPPORTED等を比較 | EKI #58 |
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

**Exit**：VA-T2・VA-E1のそれぞれで実測の正例/負例、独立Oracle、VA-X・VA-E署名相当の明記、B0/B1/B2比較可否、少なくとも一つの実Consumer/Reader観測が揃うこと。ただし未実装のScenario source/実Web Host/実EKI Provider/外部Harness/Owner受理は別々の未達として扱う。

**現状**：この文書自体はSource-staticの提案。2026-11-04時点でV02-01〜09の実行結果、実Harness比較、独立モデル割当、正式なProduct受理を示すものではない。
