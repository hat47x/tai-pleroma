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
