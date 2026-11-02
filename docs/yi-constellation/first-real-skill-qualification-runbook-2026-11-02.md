# YI Constellation：最初の実Product Skill資格確認 Runbook（2026-11-02）

状態：**実行可能な手順案／実TEI CLI・外部Harness・製品横断の実行はNOT RUN／Owner未受理**。設計の参照資料であり、将来のCI必須Gateや新しい統合Runner/Registryではない。

## 目的：合成fixture中心の議論から、実際のProductを使用した証拠へ

[TAI Draft #270](https://github.com/hat47x/tai-pleroma/pull/270)にはSK-01の合成Corpus（SK-J、L、M、TB、F、RQ、C等）と限定セルフチェックが存在する。一方、実Product Tool・Skillのロード・外部Harness・OS隔離・Owner意味受理の横断試験は未実行。**次に優先すべき成熟は新しい合成分類の追加ではなく、実際に使ったSource・Tool・Skill・Output・現在資格を区別できる一件の再現可能な縦切り**である。大量の低価格Tokenで探索や新Issueを並列増加させる方針と、最初の**品質主張**を小さな実証単位に固定することを両立する。

本Runbookの所有はTAI（比較・記録）。TEI固有のSkill/CLIは[TEI #2605](https://github.com/hat47x/tei-platform/issues/2605)／[Draft #2607](https://github.com/hat47x/tei-platform/pull/2607)。シリーズ配布は[TAI #74](https://github.com/hat47x/tai-pleroma/issues/74)。Activity再開・条件付き再資格化は[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)。SEIの限定Claimは[#767](https://github.com/hat47x/sei-cognition/issues/767)、SHOの編集は[#10](https://github.com/hat47x/sho-composer/issues/10)、EKIの実Bodyは[#465](https://github.com/hat47x/eki-fabric/issues/465)が担当。TAIに第二のProduct実装・SSOT/Host/Authorityを設けない。

## 1. 静的に確認済みの前提と、実際に確認すべきもの

**2026-11-02にGitHub mainから読取ったTEIの実Source参照**：
- `docs/getting-started.md` Git blob `4c235fed4d9ca8e889d1da16dc7b705db5bfd5cb` は、`go build -o tei ./cmd/tei`、`tei version -json`、`commands`、`model catalog -workspace`、`inspect`、`trace`、`validate -workspace -json`を記載。
- `cmd/tei/cli_contract.go` Git blob `2f1c79e2ee361c674d1dc6c783c7b757bc5c9a76` は、`tei.cli.discovery/v0`の`selected-read-only-commands`という限定Catalogを宣言。**全Plugin/全Actionの登録簿ではない**。
- `validate`はexit 0でもWarningが残り得る。`ok`／`diagnostics`を別に検査。正常読取の`worldFingerprint`と`sourceIndexFingerprint`は同版参照用であり、Owner受理・実Build/Host権限ではない。CRLF/LF差でSource byte版が変わり得る。実環境の`git status`とGo/OS/製品版を必ず記録する。
- `examples/first-workspace`は小さな合成モデル作業領域としてREADMEに存在が記載されているが、**本Runbookで実ローカルcheckoutの実行可能性を確認したことにはならない**。

## 2. 最初のS1：TEI単独CLIの現物読取り（TAIとHarnessなし）

**実施環境**：オペレーターが権限を持つTEI checkout。別途保存した未公開Sourceを自動アップロードしない。低機密の`examples/first-workspace`を使用。Go buildはプロジェクトの依存取得があり得るため、OS・依存キャッシュ・ネットワークのPolicyを先に確認し、必要ならネットワーク遮断・提供済みmodule cacheで実行する。既存build成果物と未コミットの編集を破壊しない。以下は**実行環境を固定したLinux/WSL/macOS向け手順例であり、未実行**。Windowsネイティブではパス/一時ディレクトリの形式を適切に読み替え、別実証する。実施する端末のcheckoutへ移動してから実行する。

```bash
# Linux/WSL/macOSで、権限のあるTEI checkout内から実行する例
git rev-parse HEAD
git status --porcelain
go version
TEI_BIN_DIR="$(mktemp -d)"
go build -o "$TEI_BIN_DIR/tei" ./cmd/tei
"$TEI_BIN_DIR/tei" version -json
"$TEI_BIN_DIR/tei" commands
"$TEI_BIN_DIR/tei" model catalog -workspace examples/first-workspace
"$TEI_BIN_DIR/tei" validate -workspace examples/first-workspace -json
# 試験後、保存する必要がない一時バイナリのみ管理者の判断で削除
```

**比較対象を選ぶ**：catalogから`ambiguous=false`の正確な`entries[].subject.kind/id`を**実結果から取得して**inspectし、関係を調べたい場合にのみtrace。固定の仮IDを推測呼出ししない。2回のTool観測で`worldFingerprint`／`sourceIndexFingerprint`が違う場合、同一Snapshotの全結果とみなさずSource差・Checkout改行・時点を調査。validationのexit code、`ok`、Warning/Error、diagnostics、Output実byte digestを別々に記録。

**S1 Exit**：実Binary/Tool/Source版/Principal/各Tool argv/返却実byteと証拠の保存先を再現可能に記録し、read-onlyの対象・Warning・不明点を正確に説明できた場合だけ「TEI CLI S1実証」を宣言。Model Validation成功をJava/.NET/Wasm生成・DB/外部Host実行・Business意味受理と呼ばない。Product SkillはこのS1の実施に必須ではない。

## 3. S2：同一HarnessでH2 Toolのみ vs H3 Product Skillあり

H2/H3は**同じTEI checkout、同じworkspaceとPrompt/Question、同じHarness/モデル/Profile、同じTool・権限・Source実byte**で比較する。Product SkillはTEIの正式Repoの固定版（候補`skills/yi-tei-modeling/SKILL.md`とreferences）で、**実ロード経路／実Session読込に関する証拠**を分ける。Skillを使うH3のみに目的の正答・内部Oracle・事前選別した対象IDを渡してはならない。Tool resultが非公開の環境でCloud Harnessに送る場合は、まずHost側の開示・Egress資格を確認し、合成/公開可能資料だけを用いる。

**最小の同一依頼例**：「指定Workspaceにあるモデル要素を一覧し、曖昧でない1要素の元Source/版を確認し、validationの警告と、現在説明できない範囲を分けて日本語で報告する」。Tool呼出し観測でない“利用した”というモデル自己申告は利用証拠へ昇格させない。

記録する差：Task成立、誤ったSubject選択・架空CLI/Function、source/world fingerprintの一致、Warning/unknown維持、独立に照合できるTool出力、実Tool call数・Context受領量・応答時間・Token・人の確認回数・余分な情報開示。**同一Tool/同一入力に対するSkill増分価値**だけを主張し、H3単独PASSからTAI横断Skillの価値を推定しない。

**独立判定**：評価用Oracleは実Tool/Sourceの観測から実行担当と別に作成し、H2/H3のModel入力へ期待値を埋め込まない。公開のSK-C・SK-RQ等のExpected付きfixtureは**説明・セルフチェック用**であり、盲検のHarness能力比較に流用しない。実Environmentが実H2/H3の経路を提供しなければ`UNSUPPORTED/NOT RUN`と記録する。

## 4. S3：二製品の必要な結合だけを試す（H4 vs H5）

実MMI CLI/Skillが利用可能なら、SHOやTAIの架空CLIを使わず、**MMIによる既存参照観測とTEIの実Model read-only結果**を同一の公開可能な合成Source対応に結び付ける。最初の正例は明示した対応がある場合、負例は同じ「注文」等の表示名でも**明示Source→Meaning対応がない場合**。両Productの`subject.id`/digest/「accepted」という語が同じでも、勝手に一つの正本へ統合しない。

H4＝必要なProduct Tools＋Product Skills、H5＝H4＋TAI横断Skill。実Tool出力の取得、別Product Sourceの対応、同一Claimの条件、外部公開適格性と成果の実受領を別列にする。**SHOの保存/納品**は現段階で実Tool/実Owner未受理なので、MMI参照の調査・文書案の完成からSHO完了へ昇格させない。**EKIの実Body**については[#465](https://github.com/hat47x/eki-fabric/issues/465)の実配線が未確認ならmock Claim ACKを実送達としない。

[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)のActivity再開をこの時点で接続する場合は、旧Source/意味/Tool/Skill/Grant/Body/Consumer ReadのどのEdgeが変更されたかを参照し、影響する部分だけ再資格化。履歴の正しさと現在の利用・送出・実行許可を分け、未知依存を無影響とせず、独立read-only作業を続けられるようにする。

## 5. 先行条件と観測の資格（混同しない）

| 観測 | 合格主張として許される範囲 | 別試験/Owner |
| --- | --- | --- |
| RepoのMarkdown、Tool helpが存在 | 静的な候補とコマンド仕様の読取り | TEI #2605／Product Skill |
| S1実CLIを動かした | 指定checkout・版・CLI・public fixtureのTool実観測 | TEI・実OS環境 |
| H2/H3を実際に行った | Product Skill追加による**そのHarnessと資料での**差 | TAI SK-01 |
| H4/H5で二ProductのSource対応を確認 | 明示された対応辺に限定した横断結果 | TAI #168／各Owner |
| Source改版後の局所再資格化 | 根拠がある依存辺とScopeに限る再利用 | TAI #271／各Product |
| 出力Body/Manifest一式・SHO実消費を確認 | 当該Attempt/出力版/Consumerの到達 | EKI #465／TEI #2604／SHO #6/#10 |
| 高機密でTool/Log/Network送出を防いだ | そのHost/Principal/Policy/Sourceだけの強制結果 | TAI #232／TEI #2515 |
| 作業が利用者の価値へ届いた | 本人の目的・結果・負担についての独立評価 | TAI #165/#167、YI価値研究 |

**進行管理**：上のS1/S2を一つの実測ルートとして優先しつつ、TEI数学/SQL/DSL/多Target、SEI Method、SUI、SHO Research Index、EKIの専門Product SkillやIssueは並行して拡大できる。トークン消費数・新規PR数を直接の成功指標とせず、**実際に確認できたClaimがどのOwnerからどのConsumerへ届いたか**と、そのための費用・誤断定・確認負荷を測る。現状はPlan-only、実行資格を得たとみなさない。

## 6. 大規模Draftをレビュー可能な差分へ整理する条件

2026-11-02の照合ではTAI Draft #270は**mainに93コミット先行・後行0、32ファイル差分、未Merge**。多くの合成評価と設計文書の蓄積は研究成果である一方、**93コミットあることを92個の独立実証より成熟している証拠とは扱わない**。実行可能な改善と仕様候補を段階的に審査できるよう、既存Draftを将来次の**責務別差分**へ整理する方針を提案する（今回は新PR・rebase・mergeを実行しない）。

- **A 最初の実動作**：TEI Product Skillのread-only CLI現物とH2/H3。最初の正負結果が生じて初めて実効Skill評価とする。
- **B 役割と境界**：TAI横断/各ProductのSkill Owner、声明／利用／Current Grant／Product開示。既存TAI #168/#232/#271を参照し、重複する設計を削減して小差分にする。
- **C 合成Reference**：SK-01各Corpus、独立の公開fixture checker、実行記録と未実行資格。どの成果が公開Expectedに依存するセルフチェックかを明記する。
- **D 配布・再開**：TAI #74のProduct ReleaseとSkill依存閉包、各Harness Adapter、現在Trust/Disclosureの差分確認。Owner採否・実配布を別Gateとする。

**統合前に照合すること**：mainの現行変更、同一Issue内の重複案・見出し/相対リンク、Productの正式採用範囲、機密データの公開権限、脚注・合成fixtureの独立性、現在の実Product可用性。実行証拠が不足する項目はDraftとして維持でき、他の独立PoCを止める理由にはしない。


## 7. 2026-11-02 更新：実Product CLIは一部観測済み。Skill試験は未実施

本Runbookの初期状態欄「Plan-only」「S1実CLI未実施」は**初版執筆時点の履歴**である。後続のTEI [Draft PR #2626](https://github.com/hat47x/tei-platform/pull/2626)に実Product観測が追加されたため、以下を現時点の資格として優先する。

| 根拠 | 確認済みの範囲 | そこから主張しないこと |
| --- | --- | --- |
| [TEI CI #41445984686](https://github.com/hat47x/tei-platform/actions/runs/41445984686)、HEAD `2e7aef560e35b79d658bb9c41c1575129f6a62a6` | 実Goバイナリのread-only CLIを別プロセスで9回実行。catalog/inspect/trace/validateとSource/World fingerprint・Warning/診断・stale拒否を限定観測 | Product Skillをハーネスから呼んだこと、実DB/外部Provider/Host資格 |
| **現行[TEI CI #41456256348](https://github.com/hat47x/tei-platform/actions/runs/41456256348)**、PR HEAD `31c62e8bb44c1c5c59933a46924aa4c338637085` | GitHub Actionsの`synthetic-construction-context`と`observed-tei-cli-read`の**2 jobsともcompleted/success**をGitHub側から照合。合成15+表示13件、実CLI Readでの72 Catalog entries／2 Trace rows／3 diagnostics、同じ実Read Witnessから一時領域にAI JSONと人間Markdownを生成・**同一Jobで個別再読取**した報告 | 独立したSHO Composer Reader、外部LLM/HarnessでのSkill load、Consumer独立受領、OS/Network Disclosure、業務意味受理 |
| [TEI Product Skill Draft #2607](https://github.com/hat47x/tei-platform/pull/2607) | `yi-tei-modeling`のread-only Skill文書と実CLIの対応候補をSource-static照合 | 上記CIのプロセスがこのSkillを**実際に読んだ／利用した**という証拠 |
| TAI [SK-01](../../evaluations/SK-01-harness-skills.md) H2/H3/H4/H5 | 同一Source/Tool/モデル/AgentでSkillの有無・TAI追加価値を測る**次の試験** | 既存TEI CI successを横断H2/H3実施済みと数えること |

今回、CIの成功について[GitHub ActionsのJob一覧とStep一覧](https://github.com/hat47x/tei-platform/actions/runs/41456256348)を再確認した。実際のConsumerは**同Jobの投影ファイル再読取Checker**であり、SHO Writer/Reader・別HarnessのConsumerではない。同じWitnessから二素材を出力できることと、別の製品がその意味/出典/開示資格を保持して読み取ったことは分ける。PR #2626もDraftであり、mainの現行実行契約に採用済みと扱わない。

### 次の実行票：観測済みCLIをSkillの追加価値へ結び付ける

- **R1 Product所有のSkill実使用**：TEI #2605/#2607が提供する実際のSkill root/Referenceのload byte、必要時の資料展開、選択されたCLI実binary/argv/workspace/Source/診断を、SkillなしのH2とSkillありのH3で同じHarness上で比較する。実CIと同一Tool版・Sourceであると確認できない場合は**別試行**。
- **R2 正負の独立比較**：誤Subject選択、Warningの無視、異Fingerprint、STALE、Source改行、非公開Metadata、Skill rootだけで依存資料変更を隠すケースを、Skillへ期待値を渡さず評価する。ユーザーが必要とする判断の質と、実呼出数・Token/人の確認コストの双方を記録。
- **R3 二Productへ接続**：実TEI read witnessをSHO/MMIの文書素材として渡す場合、**保存→別Readerによる読取→Source再解決**を新たな実観測として要求する。実CLIがMarkdownを書いたことをSHOの完了とは呼ばない。
- **R4 引継ぎ/再資格化**：同じSource byteでもRole/Operator解釈Plugin版やProvider Route/非表示Rule依存が変われば、証拠・Consumer資格の局所再確認が必要。TAI #271はProduct Ownerが認めた依存閉包に限り再利用する。

**現状の最も強い実証**：公開Workspace・指定HEADに対するTEI実Go read-only CLIの9プロセス観測と、同じJob内のAI JSON／人間Markdown派生素材の再読取。**未実証**：実Skill loadを用いたH2/H3、二Harness、SHO独立Reader、実Provider、OS egress、Owner意味受理。

## 8. Role解釈の依存閉包とTest-as-DataをSkillの追加検査にする

[TEI Role Bootstrap Draft #2638](https://github.com/hat47x/tei-platform/pull/2638)は、有限Bootstrap・eager interpreter dependencyの循環とdeferred Refの循環を区別し、**Root RoleにPinがあってもEager依存先のRole/Providerが固定されていないと選択資格は成立しない**という反例を19件の限定V8合成で確認している。ただし実TEI Extension Lock/Hostでの確認ではない。

[TEI Go Language Reference Draft #2639](https://github.com/hat47x/tei-platform/pull/2639)は、既存`ParseSelected`・`ParsePipelineSyntax`・`LowerPinnedPipeline`・`ResolveOperator`への二表層接続を提案する。Source span/候補標準Data/Accepted Meaning/Providerを分離する。**Go Referenceを利用した候補解釈と、正式TEI Role採用/実行資格は別**。複数表層で同じ候補値を得ても、lexical scope、NULL/Bag/Grain/Effect、Target版、Source occurrenceとOwnerの解釈が同一とは限らない。

[TEI #2621 Test-as-Data](https://github.com/hat47x/tei-platform/issues/2621#issuecomment-6578796587)は、Markdown/JSONの入力と期待値を同じ表へ置ける利便性を保ちつつ、**期待値を実装の同じ計算式から生成した場合は独立Oracleではない**と区別した。例：数量2×単価50のExpected=100を固定すれば乗算→加算の変更（Actual=52）を検出できるが、Expectedも同じ変更式から再生成すると偽PASSする。CaseがOwner受理を得ているか、Expected由来/版、意図的Mutation、最小反例で保つ必要なScope/Unit/Grain/時点を別に確認する。

Product Skillの能力一覧／Source→Role解釈の**実依存閉包**／Operator版／実Tool signature／実Source/Role witness／独立Expected／現在のDisclosure・Grantは、段階的に検査する。Role解釈エンジン、Oracle Runner、Host AuthorityをTAIへ移設しない。TAI [SK-01 §V](../../evaluations/SK-01-harness-skills.md)へケースを追加し、実Productの能力と未知の範囲に応じて選択的に適用する。

