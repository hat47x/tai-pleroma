# YI Constellation：最初の実Product Skill資格確認 Runbook（2026-11-02）

状態（**2026-11-06の最新観測**）：**TAIから固定した実TEI CLIを呼んだ公開Source W0/S1は限定達成**。[TAI実S1 #42107393245](https://github.com/hat47x/tai-pleroma/actions/runs/42107393245)で、実Binary・Source Index・指定Subject・固定台帳の照合とJSON重複キー拒否を確認。ただし**外部AI HarnessによるTool実呼出し、Skill実ロード、H2/H3四独立Session、Owner意味受理はNOT RUN**。最新の実験準備・停止線は§17〜19。旧§1〜14の「TAIでCLI未実行」等は当時の記録であり、現在のW0状態を示さない。実OS/Host/Provider資格、正式ReleaseやProduct横断E2Eへ一般化しない。新Harness Runner/統合Registryを設けず既存検査を再利用する。

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

2026-11-02の初回照合ではTAI Draft #270は**mainに93コミット先行・後行0、32ファイル差分、未Merge**だったが、その後同日mainが更新された。**本書の今回の最終照合ではmainに103コミット先行・98コミット後行、32ファイル差分**となっている（GitHub比較時点の値であり、将来も固定とは限らない）。そのため**現在mainを基点にOwnerごとの採用済み変更・競合・残る差分を比較し直す必要がある**。多くの合成評価と設計文書の蓄積は研究成果である一方、**93コミットあることを92個の独立実証より成熟している証拠とは扱わない**。実行可能な改善と仕様候補を段階的に審査できるよう、既存Draftを将来次の**責務別差分**へ整理する方針を提案する（今回は新PR・rebase・mergeを実行しない）。

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

Product Skillの能力一覧／Source→Role解釈の**実依存閉包**／Operator版／実Tool signature／実Source/Role witness／独立Expected／現在のDisclosure・Grantは、段階的に検査する。Role解釈エンジン、Oracle Runner、Host AuthorityをTAIへ移設しない。TAI [SK-01 §W](../../evaluations/SK-01-harness-skills.md)へケースを追加し、実Productの能力と未知の範囲に応じて選択的に適用する。


## 9. 2026-11-03 後着確認：#2626 mergedと次のHarness実証を区別

このRunbookの§1〜§6は作成当時の手順・状態、§7〜§8は後着の実CLIとRole/Oracle検討である。**TEI [PR #2626](https://github.com/hat47x/tei-platform/pull/2626)は2026-11-02T18:35Z時点でmerged**（merge commit `00eb8e148daadbc2cf40145d8e8473d56531514c`）。公開参照Workspaceでの実Go CLI 9プロセス／同Job内二Projectionの再読取／Source-only移動に伴うSourceIndex/Trace位置変化は、今後はmerged Sourceを実起点とする。ただし本Runbook自身が新mainでTEIを再実行したという意味ではなく、元PRの固定HEADで観測された局所Evidenceを参照する。

**新たに優先して比較する作業**：実在TEI Skill [#2605](https://github.com/hat47x/tei-platform/issues/2605)/[Draft #2607](https://github.com/hat47x/tei-platform/pull/2607)の正式なLoaded byte（rootだけでなくreferences/scripts）を確認し、同一Harness・同一Tool/SourceでH2/H3を反復。その後、[複数Harnessと実Capability資格化計画](harness-portability-and-capability-qualification-2026-11-03.md)のSK-HP01〜14へ接続する。

特に [TEI Draft #2649](https://github.com/hat47x/tei-platform/pull/2649) の実Source-static照合で、`commands`はselected read-only Catalogに限定される一方で`operations`/`artifacts` CLI dispatchが別に存在する。この**一覧外＝不存在ではない**という陰性所見と、`artifacts -out`の実ファイル書込分岐を、最新の実バイナリとargvで必要時に検査する。実コマンドの発見はSkillのread-only権限をwriteへ拡張しない。

二番目のHarnessはClaude Code／Codex／OpenCode（DSH構成は別Profile）等の**実際に使える**環境から選び、Dots/Grok BotはAccount availabilityが確認できた場合のみ個別Profileとして評価する。比較は公式文書の機能一覧ではなく、実Skill load/Tool arrival/出力・現在権限・外部受信によって行う。公開済み資料でできるTaskは本番秘密を用いず、未接続はunsupportedとする。

**変更後もNOT RUN**：H2/H3の実Harness比較、二Harness移植、SHO別Reader、実OS/外部Host拒否、TAI所有の活動E2E、独立Owner意味受理。本節は後着事実の参照訂正とRunbookの実行順序変更のみ。

## 10. 実TEI CLIの既存実証とSK-02比較適格性の引渡し（2026-11-03）

2026-11-02に[TEI #2587](https://github.com/hat47x/tei-platform/pull/2587)（操作・Artifact生成）と[TEI #2626](https://github.com/hat47x/tei-platform/pull/2626)（実CLIでModel/Source/Traceを読取るConstruction Context）がmainに統合された。#2626 exact-head `42b7ec43fa7901359120008105e812eda7e9d6e7`の[Focused GitHub Actions #41462654810](https://github.com/hat47x/tei-platform/actions/runs/41462654810)は実Go CLI・二表示・Source-only Relocationの限定実証に成功している。2026-11-03時点でTAIが同じCLIを**当該Harnessから実呼出しした証拠は未取得**であり、TEI自身のPASSをS1/H2/H3/H4/H5の実績として移し替えない。

**対象コマンドの資格**：`tei commands`の限定Discoveryは全Dispatch列挙ではない。`tei operations`／`tei artifacts`は実装されているが、`artifacts -out`はローカルファイル書込みを伴い、初回Tool-only/Skill比較で許可するread-only操作と同一視しない。[TEI #2649](https://github.com/hat47x/tei-platform/pull/2649)はCapability→CLI→Product Skillを別証拠で整理し、候補Workflowの完了結果はそのexact headのRunごとに確認する。

**最初の実験の判定順**：
1. **S1 Product-only**：固定したTEI実Binary・Source/worktree・Read-only実argvと出力、SourceIndex/WorldFP、ValidationのWarning/Unknownを、TAIの独立した実行票として観測。既存#2626 CIは対照にするだけ。
2. **H2/H3を交差順で4独立Session**：同じ`repo_head/binary/workspace-tree/World/SourceIndex/prompt/harness/model/tool-profile/principal/grant/disclosure/oracle-version`を実照合。H2がSkill非露出、H3が同一版Skillを**実ロード**したことを確認。ForcedとAutoは別Group。
3. **比較適格性をTask採点前に判定**：[実行可能なtest-only Checker](../../evaluations/tools/check-sk02-pair-eligibility.cjs)に、一件の`{trials:[H2,H3,H3,H2]}`を入力する。同Checkerの`eligible-to-score`はTrialの記入欄の整合候補に限り、実Observerの真正性／Task正答／Skill追加価値を証明しない。未観測は`insufficient-evidence`で保持し、Source/Grant/Model/Skillの不一致は`ineligible`として別Groupへ戻す。
4. **Independent Oracleと総費用**：比較適格なGroupについてのみ、独立採点者がTool原出力と期待を照合し、正答/誤成功/Token/Time/人手確認を別に記録する。Oracleを片側SessionやSkill本文へ混入させない。

**限定の新規実測**：Checker本体9,361byte、SHA-256 `be2185ff77fb8ab0e03a3c7fc6462f21ad3ce3ede8c83448482e86073274e565`／Git blob `7ea3d34387eee832d4f190d6264d19988d8027f1`。Node.js v22.16.0で公開架空Trial票の**20/20自己試験PASS**（`node --check` PASS）。実Harnessでの4試行、Product Skillの実Load、外部AIの送出、OS/Host Policy強制、独立Oracle採点・Owner受理は**NOT RUN**。別の新Runnerや中央Host・新しい認可正本を追加しない。


## 11. 2026-11-04：Source実消費とCLI検証成功を分離するS1/SK-02入場条件

### 他チャットの実測を既存実験に接合

- [TEI #2822](https://github.com/hat47x/tei-platform/issues/2822)（WSL/Go実CLI、main 97aba8146）：利用者定義0件のWorkspaceでも **validateはok=true／diagnostics=[]／exit0**。model catalogは **標準stdの13件**を返し、sourceStatus=not-indexed。従ってvalidate成功＋Catalog非空は利用者のSourceをロードした証拠ではない。
- [TEI #2823](https://github.com/hat47x/tei-platform/issues/2823)（同環境の実CLI）：Workspace manifestの未知・不存在rootが無診断となる例、workspace-filesにはあるがLoaderで解析しない拡張子／ファイル名がある。**Declared・Enumerated・Parsed/Loadedを区別**し、未読込ファイルの不存在や品質合格を主張しない。
- [TEI #2824](https://github.com/hat47x/tei-platform/issues/2824)（同環境の実CLI）：commandsは**19件**の限定一覧だが、既存契約文書に「13件」の古い記述。catalog上のworldは安定したtei.cli.* JSON契約外、各entryに個別schemaVersionなし。**Tool名・read-only属性・安定JSON契約・全Tool可用性は別**。標準型catalog13件とcommands19件は別の数値。
- [TEI merged #2819](https://github.com/hat47x/tei-platform/pull/2819)はGenerator宣言Source D1と実Go Build入力D2の相違を拒否しない限定Go Characterization。宣言したSourceのHash一致は、実Buildが消費したByte同一性を証明しない。ただし最初のSK-02 read-only試験へGeneratorの検証まで必須化しない。
- [TEI Draft #2828](https://github.com/hat47x/tei-platform/pull/2828)は既存Driver Scenario v0にAI生成JSON候補をつなぐtest-only提案。AIが追加したテストの自己ExpectedとProduct独立Oracleは別。TAIに第二Scenario Runnerを作らない。

### 実Sourceに到達したことを一件のClaimへ束縛

| 段階 | S1で固定・実確認するもの | 合格とみなさないもの |
| --- | --- | --- |
| W0 **Declared** | manifestのroot、元Source bytes、実行前に固定した期待Subject kind/id | YAMLに記述しただけのもの |
| W1 **Discovered** | 同一実Binaryのcommandsと、必要ならProduct-only S1でworkspace-files | 管理対象ファイルの一覧を実Parser消費と同一視すること |
| W2 **Loaded/Applicable** | model catalogで期待する**利用者定義**SubjectをID/namespace/sourceStatusまで確認、同版inspectでSource locatorへ到達 | 標準std13件だけ、空・未解析のSource、他Subjectの成功 |
| W3 **Validated** | validateのexit、ok、Warning/diagnostics、WorldFP/SourceIndexFPをW2と照合 | validate.ok=trueだけで必要Sourceを全ロードしたという結論 |
| W4 **Executed** | 実Binary SHA/argv/cwd、Tool stdout・exit/diagnostics、同一Session・Audience、必要なLoaded Source版 | Skill文書・Agent自己申告・Tool候補だけによる実実行主張 |
| W5 **Observed** | 外部Harnessへの許可済み実受信範囲、独立ExpectedによるTask正答・Warning/Unknown・Sourceの引用 | Product Skill配布、比較適格、外部Effect/Reader/品質期限の自動PASS |

**二つの採点を統合しない**：現[SK-02比較適格性Checker](../../evaluations/tools/check-sk02-pair-eligibility.cjs)は四Sessionのメタデータ整合のみを検査する。H2/H3がともに空Workspaceなら、実験条件は一致していても**要求した利用者SubjectのRead成功は不成立**。SK-02正答採点の独立OracleがW0〜W3に対する実CLI/Source Evidenceを評価する。型が正しい自己申告を実Sourceのロード証明にしない。新Loader/Registry/共通Schema追加なし。

### 既存TAI接続を重複実装しない

[TAI merged #105](https://github.com/hat47x/tai-pleroma/pull/105)のmainにある [reference-tei-model](https://github.com/hat47x/tai-pleroma/blob/main/tools/reference-tei-model/README.md) は、SCN-001のObservation／RuleCandidateの**宣言された属性と実CatalogのmodelBinding=bound**、validateJson=consistent、選択時のexpect-commit/expect-go-version／Checkout不変を照合する。実TEI接続の限定証拠となるが、SK-02で選ぶ他Workspace/Subject、H2/H3実Harness Loader、全Source Closure、Host/Owner受理を代表するものではない。新しいTAI Pin Driver/Tool正本を増やさない。

### SK-SRC01〜06：独立Expected候補（追加試行はすべてNOT RUN）

| ID | 負例・正例 | 期待する判定 |
| --- | --- | --- |
| SRC01 | 利用者定義0件でもvalidate.ok=true、標準13件 | Tool正常と要求Subject読込成功を分け、後者は未達 |
| SRC02 | workspace-filesに列挙されるが未解析のファイル | Enumeratedのみ、Loadedではない |
| SRC03 | manifestの存在しないroot／typoが無診断 | 安全拒否済みと主張せず、宣言と実Load差を記録 |
| SRC04 | commands 19件、古い文書13件、world契約外 | Command存在と安定JSON/全Tool契約を分離 |
| SRC05 | 独立に指定した利用者Subjectへcatalog＋inspect＋validateが同版で到達 | **指定Subjectの限定read-only観測**のみ合格 |
| SRC06 | Generator宣言D1と実Build D2が相違 | Generator試行は不適格／証拠不足。初回read-only Taskには不要な追加要件を課さない |

**帰属**：TEI #2822〜24のSource/CLI修正、#2595のBuild Source固定は各TEI Ownerの判断。TAIが実測したのは本節の文書照合のみ。新SK-SRC試験、実H2/H3四Session、独立Oracle/Provider/OS/Network、Owner Meaning Acceptanceは**NOT RUN**。既存のTool-onlyとProduct Skillの実験順を変更しない。


---

<!-- sk02-one-real-trial-freeze-20261104 -->
## 12. 2026-11-04：これ以上の合成PASSを実Harness資格の代替にしない――最初の実試行を凍結する実施票

**決めること**：[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の要求（DSHに限定しない代表Harness）、[TEI #2605](https://github.com/hat47x/tei-platform/issues/2605)の実Product Skill、[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)の過剰要件監査に基づき、最初の実験で必要なものを**1 Product／1 read-only User Subject／1 Harness／同じ実CLI／四つの独立Session／独立Expected**へ限定する。第2 Harnessはこの実験の後のSK-03に含める。合成E01〜60、NC01〜19、外部MCP仕様のケース追加はそれぞれ有用だが、この最初の真の証拠を置き換えるものではない。

### 12.1 事前に固定する一枚のTrial Card（新Canonical Schemaではない）

| 固定項目 | 採取元・決め方 | 失格/保留 |
| --- | --- | --- |
| **Task／唯一のSubject** | 公開TEI Workspace（初期候補：`reference/workspace`）、**実Catalogで存在が確認できる利用者定義**の`subject.kind/id`を、Agentへ渡す前に独立担当が固定。候補例`semantic-data:sales.order`は実版未確認ならCandidate | `validate.ok=true`や標準stdのCatalog 13件だけではRequired User Subject読込の証拠にならない（TEI #2822/#2823） |
| **Source／再現性** | checkout exact HEAD・clean/dirty、workspace Source tree byte／改行・World/SourceIndex FP・該当Subjectの実元Source locator | Source位置だけが移動した試行やdirty差が混在すれば、同じ条件の腕として採点しない |
| **CLI／能力** | `go build`した**一つの実Binary**のSHA256・Go/toolchain/OS・実argv/cwd/exit/stdout/stderr・`commands`の現物。既存TAI [reference-tei-model](https://github.com/hat47x/tai-pleroma/blob/main/tools/reference-tei-model/README.md)の厳格Pin/Checkout/ModelBindingを**別の限定比較証拠**として再利用可能 | `commands`の19件を「全CLI／全JSON安定契約」としない（TEI #2824）。`operations -out`、`artifacts -out`、Shell redirect/chainを初期read-only Scopeに混ぜない |
| **Harness条件** | 実起動できた外部Harness名・版・model/provider・plan/請求経路・Profile・Session・実Tool可用性・現在の公開/権限。最初のHarnessのブランドを**必須指定しない** | Claude Code/Codex/OpenCode/DSHの公称仕様で実Install/実Skill loadを代替しない。Cloud/IDEは異なる実行Profile |
| **Skill差分** | H2=実CLI Tool-only、H3=同Tool＋TEI Product `yi-tei-modeling`の実Package/References/Scripts closure。TAI横断Skillは投入しない。H3のforced loadとauto discoveryは別のTrial Group | H2にSkill文書・前Sessionの答・Oracleが紛れたら比較を中止。H3の実Load byte/経路が未観測ならSkillの因果効果は採点不能 |
| **独立Oracle** | Productの実Catalog/inspect/Source/Warningに基づき、Agent試行前に独立担当が対象ID・元Source・Version・必須Warning/Unknown・許可Toolを事前登録。Agent/Skillへの正答漏出を防ぐ | Agent自身の回答や合成Checkerを独立Expectedへ転用しない。空/部分Sourceを「完全な正解」にしない |
| **利用と開示** | **合成・公開済みTEI Modelだけ**を実験に使用。Harnessが読み込んだTool結果、外部へ許可された送信内容/実観測先、current Grantと未観測面を限定記録 | 実OS/Network全面非漏えい・Cloud retention・本番Host権限はこの実験の合格範囲外。秘密Rawや内部OracleをHarnessへ投入しない |

**コマンド例（利用者が実TEI checkoutと公開Fixtureを固定した後にのみ実行）**：
```sh
# Product-only baseline。独立した一時directory、固定したGo/toolchainで一度だけビルド
go build -mod=readonly -buildvcs=false -o /tmp/tei-sk02 ./cmd/tei
/tmp/tei-sk02 version -json
/tmp/tei-sk02 commands
/tmp/tei-sk02 model catalog -workspace reference/workspace
# Catalog実出力を見てSubject kind/idを確定。以下は公開資料上の候補
/tmp/tei-sk02 inspect -workspace reference/workspace -subject-kind semantic-data -subject-id sales.order
/tmp/tei-sk02 validate -workspace reference/workspace -json
```
`/tmp/tei-sk02`は例示の保存先でありWindows等では環境に合わせて変更する。Git HEAD/実Binary hash、workspace tree、Exit/Warningを別途採取する。stdoutに含まれるSource path等は公開する前に用途とAudienceを確認する。上の`inspect`候補が見つからない場合は**現在のCatalogから実在する一つを選ぶ**。存在しないSubjectのまま「成功」させない。Traceは必要なときだけ別に実行する。

### 12.2 実行順序と停止規則（既存SK-02 Checkerを再利用）

1. **W0／No Harness Product baseline**：Product単独CLIの実Source読込・各exit・実Source Indexを照合。TAI [merged #105](https://github.com/hat47x/tai-pleroma/pull/105)のConnectorを使う場合は、そこで照合したSCN-001の型と**今回のSubjectが同一か**別に記録し、別Task/版を混用しない。
2. **W1／H2 2独立Session**：同じ公開Taskと実Binaryを外部Harness Tool-onlyで呼ぶ。初期設定の違い、実Tool args/results、許可開示、Prompt/Source/Model/Grantの一致を観測。CLIを手元で動かしただけでは「Harnessが呼べた」にならない。
3. **W2／H3 2独立Session**：TEI Product Skillの同一closureを**実ロード**し、別Sessionで同じToolを呼ぶ。順序は`H2→H3→H3→H2`、forced loadを先にしてよい。auto discoveryは別Group。
4. **W3／比較資格と正答**：[既存SK-02 Checker](../../evaluations/tools/check-sk02-pair-eligibility.cjs)で**合成専用の事前チェックを実Trialの記録の検査にも再利用**する（新Checkerを作らない）。非重複JSON key、実観測の証拠参照・Source同一性を確認するが、Checker出力`eligible-to-score`は回答正答/機密非漏えいを意味しない。独立Oracleが指定Subject/Source/Warning/Unknownと実Tool結果を別採点。
5. **W4／決定**：正答、余分なTool/Token/Adapter/人手、誤った成功、現在Grant未確認を**別欄**で比較。Skillが実ロードできなければ`ineligible/insufficient-evidence`、Skillに効果がなければ**Tool-onlyを維持**。最初の1組の限定結果から全Harnessの改善・p95・標準配布を主張しない。
6. **W5／別Harnessは後続**：W0〜W4のTask/Source/独立Expectedを引継ぐ条件が満たされた時点で、[SK-03](harness-interoperability-and-handoff-pilot-2026-11-03.md)の二Harness Tool/Skill互換と[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)の現在性再資格化へ進む。MCP cache/MRTR/Tasks、組織別Read、EKI低遅延/マルチモーダル、TEI複数Buildは**必要な実環境が現れた時だけ**追加検査し、初回をブロックしない。

**直ちにSTOP／Claimを制限する条件**：実HarnessにAccess不可／実Tool未呼出し／Product CLI/Skill実Load不明／対象User Subjectが未読込／Sourceの版または試行腕が混在／公開許可なし／入力JSONが重複member／Oracle混入／予期しない書込み／実Host Grant不足。停止時は成功扱いにも「全Harness非対応」にもしない。安全なProduct-only read-only診断を維持して不足点だけ各Ownerへ返す。

### 12.3 採用判断と価値の確認

- **今回確定している局所実績**：TEI本体にmergedの`yi-tei-modeling`があり、TEIの実CLIの限定CIとTAIの既存`reference-tei-model`は別の実証として存在。SK-02 Checkerは[合成E01〜60／人工SK-03 NC01〜19の限定Node CI](https://github.com/hat47x/tai-pleroma/actions/runs/41851651173)で60/60・19/19 PASS。SK-03の実Node子プロセスは人工JSON Producerであり、TEI/外部Harness実呼出しではない。
- **まだない実績**：SK-02の**実四Session/実Skill Loader/モデルからのCLI実呼出し／独立業務正答採点／実モデル送出/実OS強制**。それらの未実行分を`NOT RUN`として明示し、旧局所CI・合成試験・Agent自己申告で埋めない。
- **Owner/Gate**：本票は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)とTAI Draft #270のSK-02実行準備であり、[TEI #2605](https://github.com/hat47x/tei-platform/issues/2605)がProduct CLI/Skill、[TEI #1180](https://github.com/hat47x/tei-platform/issues/1180)が独立Driver Scenario、[TEI #2018](https://github.com/hat47x/tei-platform/issues/2018)が費用と品質、TAI #232/TEI #2515が外向き開示/実OS、TAI #422が過剰要件回避。**新Host/Registry/Agent Loop/Schemaや追加Mandatory Test Suiteを先行しない。**


## 13. 2026-11-04：初回H2/H3でCLIの作業場所と実argvのWorkspaceを固定する

[SK-02 §14](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)へ**実CLIのCWD・Workspace引数の比較資格**を接続した。四Sessionで`workspace_tree_digest`とWorldFP/SourceIndexFPだけが同一でも、`tei model catalog -workspace A`と`tei validate -workspace B`では同じSourceに到達したとは言えない。H2/H3の結果を比較する際は、同じ実Binary・公開Workspace・元Source・Tool/Profileに加え、**実行時のCLI作業ディレクトリ文字列（`cli_cwd`）と各Scoped Readの実`-workspace`引数**を記録する。

既存[比較適格性Checker](../../evaluations/tools/check-sk02-pair-eligibility.cjs)にE49〜E60を追加した。CWDの欠落は証拠不足、CWD差は不適格。最初の一Workspace Taskに限り、複数の異なるWorkspaceを同一Trialで使う／4Trialで対象を変更する／`-world`へ切り替える／Workspace二重指定は比較不適格。Scoped Read自体の欠落、Workspace値が空・Option名しかない場合は証拠不足。`-workspace=path`と`--workspace path`は正当な記述として扱う。

**対象を過大に固定しない**：この判定は原argv内のWorkspace文字列同一性だけを確認する。CWDが同じでもsymbolic link先・入力実Byte・実Loaderが消費したFile/Role、実Processによるargv取得の真正性は保証しない。その確認は[§11](#11-2026-11-04source実消費とcli検証成功を分離するs1sk-02入場条件)のS0〜S5と独立Oracle/実Observerが担う。別Workspaceを比較する正当なTaskは**異なるTask Group／別Profile**にし、無理にこの初回比較へ押し込まない。TEI製品CLIに新しいFlagやProviderを要求しない。

**実行済みの範囲**：[GitHub Actions #41850429887](https://github.com/hat47x/tai-pleroma/actions/runs/41850429887)の実Node Jobで、E01〜E60の公開合成票**60/60 PASS**（新規E49〜E60を含む）。実H2/H3四Session、実CLI Source読込、実外部Harness/独立Oracle採点、Host/OS Egress、Owner意味受理は**NOT RUN**。


---

<!-- sk02-live-s1-witness-reuse-20261105 -->
## 14. 2026-11-05：既存のTEI S1実CLI証拠を再利用し、残るS2の実ハーネス価値検証へ進む

### 最新の製品事実とTAIが行うべきこと

[TEI #2605](https://github.com/hat47x/tei-platform/issues/2605)を最新化。[Product Skill #2607 merged](https://github.com/hat47x/tei-platform/pull/2607)、[実CLI Actions #41532988114](https://github.com/hat47x/tei-platform/actions/runs/41532988114)（対象 HEAD `d0de429ae5aac38b7949c2cfe6eacafff059675f`、product-skill-read-only Job success）は**既存Product S0/S1の限定実績**。公開`reference/workspace`と`sales.order`／`sales.order.customer`について、実ビルド済同一TEI Binaryの`commands → model catalog → inspect → trace → validate`を実行した。[TEI Draft #2863](https://github.com/hat47x/tei-platform/pull/2863)では、Skill本文に残る「Product CLI未実行」の古い記述を修正提案中。これは**main統合済Skillと、今回の文書Draftの区別**である。

**既存W0を再実行すべきかの基準**：

- **既存S1の限定Evidenceを歴史Observationとして参照できる**：同じTask／元Source／必要Subject／同じGo/CLI実Binary/版／元回答で必要なProofがそろう場合。実験の独立Expectedが要求する全項目について実ジョブログと実データを照合し、証拠が足りない部分は追加で読取る。
- **現在の実験W0をやり直す**：現在mainや別Binary、別Workspace、別Source位置・内容、異なるRequired Subject、実行時のUnknown/Warning、異なる実開示条件が必要な場合。旧Run successを新Binaryの実実行とみなさず、同じ独立Expectedを試行前に確定する。
- **STOP／実験資格不足**：標準`std` 13件／`validate.ok=true`のみ、manifest宣言・workspace-files列挙だけの未Parsed Source、`world`の契約外出力、別Workspaceへの暗黙変更、Current Grant不明。TEI [#2822](https://github.com/hat47x/tei-platform/issues/2822)／[#2823](https://github.com/hat47x/tei-platform/issues/2823)／[#2824](https://github.com/hat47x/tei-platform/issues/2824)は製品側の未解決事項。TAI側に第二Loader/Validatorを設けない。

### 残る初回実証は同じHarnessのH2/H3四Session

- **最小受入の単位**：一Harness実版・一公開TEIユーザー定義Subject・一実Binary・同一Tool ProfileとDisclosure、独立Expected、四独立Session `H2→H3→H3→H2`。TAI横断Skillは不要。固定していない実モデル/ProviderをSKILL.mdで推測しない。
- **Skill効果の因果的区別**：H2はTool-onlyかつSkill非表示、H3は[Product Skill root/参照資料](https://github.com/hat47x/tei-platform/tree/main/skills/yi-tei-modeling)が実ロードされた場合のみ比較する。H3の単なる配置／AIが文書を引用しただけではSkill効果を認定しない。
- **受入分離**：[SK-02 test-only Checker](../../evaluations/tools/check-sk02-pair-eligibility.cjs)の`eligible-to-score`はメタデータ比較の適格候補。Product Sourceの実読込、独立Expectedに対する正答／Warning・Unknown保持、Toolの実argv・受信、Token/Time/人手、実開示のCurrent Grantを別々に採点する。[局所合成CI #41851651173](https://github.com/hat47x/tai-pleroma/actions/runs/41851651173)は60件の適格性と人工Node子Process19件の表現整合を試験しただけである。

### 後続へ渡す方式判断を意図的に制限

[TEI #2850 merged](https://github.com/hat47x/tei-platform/issues/2850)は`after-commit/compensation`効果を観測する`EffectObserver`が無いとき**当該無人Actionの手前で停止**する実装。この成熟した判断はTAIの将来のAction Handoff／EKI Task再委任で、実Provider Receipt/不明結果に応じて**必要時に**検証する。read-onlyのH2/H3比較へWrite/Commit/compensation Engineを必須化しない。TEI [Role自己記述 #2860 Draft](https://github.com/hat47x/tei-platform/pull/2860)、DB別SQL Asset/2way SQL案、EKI低レイテンシ・マルチモーダルやSHOは各Ownerの限定機能として、求めるTaskが現れた段階で追加する。

**実行状態**：TEI実Binaryによる限定S1は**既存実CIで確認済み**、SK-02合成60/60とSK-03人工Node19/19は別の局所試験。**実AI HarnessのSkill install/load/invoke、H2/H3四Session、第二Harness、現在OS/Networkの非漏えい・実書込みEffect・Owner意味受理は引き続きNOT RUN**。新しい独立Host/Registry/Oracle/Runnerは作らない。


<!-- sk02-conditional-write-resume-real-pg-20261105 -->
### 14.1 初回read-onlyの後に接続する「結果不明の書込み」条件（実PG証拠へ更新）

実験がwrite/after-commit/Provider Effectへ進む場合のみ、[TEI #1174](https://github.com/hat47x/tei-platform/issues/1174)／[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)を必要条件として再確認する。初回SK-02のread-only四Sessionには組み込まない。

- [merged TEI #2853](https://github.com/hat47x/tei-platform/pull/2853)の**製品Command→実PostgreSQL CAS、模擬ACK-loss→`COMMAND_COMMIT_UNCERTAIN`/unknown、同OperationIDのReceipt lookup/独立Read**は、過去の「全て合成Mock」から一歩進んだ限定Product証拠。ただし実Network断・Process kill・完全な本番権限ではない。
- [merged TEI #2854](https://github.com/hat47x/tei-platform/pull/2854)の実DB ABA反例は**別Keyによる同一論理操作の再適用があり得る**ことを示す。Harness Bの新Session/新Taskや新idempotency key生成を、安全なRetryの資格としない。同じOperationIDと別Keyは明確に区別する。
- [merged TEI #2850](https://github.com/hat47x/tei-platform/pull/2850)の`EffectPreconditions`はObserver**有無のpreflight**であってEffect観測済みのReceiptではない。停止Stepより前のEffectが発生していない保証にもならない。
- その段階の追加受入は**Current Host/Provider Grant・Operation identity・同Attempt/Result/Receipt・ACK lossの実確認・Consumer実読取**。認可や実Effectの意味はProduct/Host/EKIが所有。TAIは実Harness間のTransfer/選択的再資格化/費用を検証し、第二のTx/Evidence Engineを作らない。

この追補の採用は**計画上の条件付き判断**。実PostgreSQLの製品局所試験は存在するが、TAIの実Harness A→B書込み再開／実Network断／Business Owner受理は**NOT RUN**。

## 15. 2026-11-06：TAIから固定TEI実Binaryの公開Sourceを独立S1観測

従来の[TAI mainにあるreference-tei-model](https://github.com/hat47x/tai-pleroma/tree/main/tools/reference-tei-model)はSCN-001の限定型宣言を実TEIに対照していた。今回はSK-02に直接関係する公開reference/workspaceのユーザー定義semantic-data:sales.orderについて、TAI独立CI Jobから**固定版TEIの実Go CLIを実読取**した。TEI側CIの結果を引用しただけではない。

**記録された実証値**：[限定JSON Evidence票](../../evaluations/records/TAI-TEI-S1-real-public-source-2026-11-06.json)へCIジョブログで確認したSource/実Binary/4 CLI stdoutのSHAと負例を転記した。これは独立署名済みの生Receiptではなく、観測値と未立証Claimの読取り用要約である。

**再現資産**：[TAI S1 Source Probe](../../evaluations/tools/probe-tei-s1-real-source.cjs)／[専用GitHub Actions](../../.github/workflows/tai-tei-s1-real-public-cli.yml)。TEIをfull SHAで別Checkoutし、go.modに対応するToolchainで一度ビルド。実Binaryをcommands、model catalog、inspect、validate -jsonの4呼出しに用いる。Git Checkout・Source/実Binary SHA256・実argv/cwd/exit/stdout digestを限定JSON Receiptに保存する。Sourceを直接読み固定のdata Order・attribute total type std.moneyと照合し、CLI Catalog/InspectからSubjectの実ロードを別確認する。テスト用の独立静的期待条件であって、業務意味の独立Oracleではない。

| 証拠（固定CI checkout） | 実測した限定結果 |
| --- | --- |
| [最終Workflow #42099390431](https://github.com/hat47x/tai-pleroma/actions/runs/42099390431) | 完了・成功、実ジョブログ確認 |
| TEI Source pin | 50ebf8014340fd1906f6b35cfa30173e0ee2fc6c |
| 実バイナリSHA-256 | 6769ec0908007f1147de0502b3e88421159e0b2c4df70fc57b53c9d29ccbc36f |
| 実Source SHA-256 | reference/workspace/semantic/sales/order.tei = f2063418b893a60a9f948edbb2b23ec821f7a15ed8e5863c36e1b72abade1e33 |
| 利用者Subject | semantic-data:sales.orderをCatalogで1件、sourceStatus=indexed、Inspect ok=true |
| Validate | ok=true、diagnostics=3。診断ゼロとは扱わない |
| 空Workspaceの負例 | validate.ok=trueでも対象Subject 0件、同fixtureの標準std entries 12件。TEI #2822の別fixture 13件と混同しない |

**失敗履歴**：[初回CI #42099147476](https://github.com/hat47x/tai-pleroma/actions/runs/42099147476)はTEI Go Build成功後、TAI ProbeがTEI Catalogの実契約result.entriesをトップレベルentriesと誤認しFAIL。[TEI cli_model.go](https://github.com/hat47x/tei-platform/blob/50ebf8014340fd1906f6b35cfa30173e0ee2fc6c/cmd/tei/cli_model.go)で応答Contractを照合して修正し、Pipeにset -euo pipefailを設定。[修正後CI #42099390431](https://github.com/hat47x/tai-pleroma/actions/runs/42099390431)でBuild→CLI→Receipt検査が成功した。初回の失敗を最初からPASSだったと扱わない。

**次の資格**：この実測は指定公開SourceとSubjectを固定版の**実TEI Product CLIから読む限定S1**。Product Skillは実Harnessへロードしていない。H2→H3→H3→H2の4独立Session、モデルが実Toolを使用した証拠、外部開示/Grant、独立Task Oracle、Owner意味受理、実Provider Effect、Windowsは**NOT RUN**。同一版・実バイナリ・Sourceを両腕へ受け渡すか、新版へ更新するなら両腕のSource・Oracleも再固定する。S1の旧PASSを新HEADの同値・全Source closure・実効認可に移さない。常時必須の新Product Gateや第二のTEI Bridgeは追加しない。

## 16. 2026-11-06：Inspectの実Source参照・バイト指紋・定義参照を照合

§15の初回S1が確認したのは「期待するSource byteを試験側が別読取した」「Catalogに同IDが出た」「Inspectが成功した」までだった。これだけでは、**そのSourceのbyteが実CLIのSource Indexに取り込まれたこと**を同一検査で保証できない。TEIの既存[Source Index Fingerprint](https://github.com/hat47x/tei-platform/blob/50ebf8014340fd1906f6b35cfa30173e0ee2fc6c/internal/sourceindex/model.go)／[Inspect Contract](https://github.com/hat47x/tei-platform/blob/50ebf8014340fd1906f6b35cfa30173e0ee2fc6c/internal/operations/inspect.go)の公開型を利用し、**新しくOwner正本やSource Resolverを導入せず**検査を追加した。

**実装**：[既存TAI S1 Probe](../../evaluations/tools/probe-tei-s1-real-source.cjs)のInspect応答内に、①Subject kind/idが指定Subject、②sourceStatus=indexed、③artifactsに期待pathが**一意**、④そのfingerprintが別Readした原byte SHA-256と等しい、⑤当該path・Subjectにrole=definitionの実referencesが存在、という必要条件を設定。さらにCatalog・Inspect・ValidateのWorldFP／SourceIndexFPの相互一致を検査。ただし、別Process間の多ファイル原子的Snapshotや変更間の同一性を保証する仕様ではない。

**CI実測**：[TAI S1 #42101157330](https://github.com/hat47x/tai-pleroma/actions/runs/42101157330) **completed/success**。Product pin 50ebf8014340fd1906f6b35cfa30173e0ee2fc6c、Source semantic/sales/order.tei、Subject semantic-data:sales.order。Inspectは当該SourceのFingerprint `sha256:f2063418b893a60a9f948edbb2b23ec821f7a15ed8e5863c36e1b72abade1e33`と**definition reference 1件**を返し、独立Readと一致。S1-W01〜08の公開合成テスト8/8 PASS（別file、stale bytes、ref欠落、別Subject、not-indexed、重複artifact等を拒否）。S1の旧空Workspace negativeは維持。詳細は[限定証拠JSON](../../evaluations/records/TAI-TEI-S1-real-public-source-2026-11-06.json)に転記した。

**資格の上限と次の差分**：この検査は**固定された単一TEI Checkout／単一SubjectのSource Index参照を実CLIで確認**したことまで。[TEI自己記述Draft #2860](https://github.com/hat47x/tei-platform/pull/2860)のRequired/Observed分離と同様、Role文字列やSource一致をOwner意味受理・Build Closure・外部Authorityへ昇格させない。H2/H3では、実HarnessのSkill Loader/Tool実呼出し・Context Audience・独立Task Oracle/費用が次の未了。Business Writeの結果不明・ABA・Receiptは既存§14.1とSK-03の**Conditional**であり、初回read-only試験をブロックしない。


---

<!-- sk02-harness-live-observation-witness-20261106 -->
## 17. 2026-11-06：S1の実Source証拠が揃った後のH2/H3「実利用」入場票

### 17.1 進捗の位置：W0は一つの公開Sourceに限って実測済み

[TAI 実S1 Run #42101157330](https://github.com/hat47x/tai-pleroma/actions/runs/42101157330)のsuccessを[証拠記録](../../evaluations/records/TAI-TEI-S1-real-public-source-2026-11-06.json)と照合。TEI `50ebf8014340fd1906f6b35cfa30173e0ee2fc6c`、Go 1.26.10、公開`reference/workspace`、`semantic-data:sales.order`について、Catalog/Inspect/Validateを**実ビルド済CLI**で呼び、別読取した`semantic/sales/order.tei`のbyte SHA-256と**実Inspect Source Index artifact fingerprint/definition reference**を照合。S1-W01〜08合成負例8/8と実CLIの限定観測が完了した。初回失敗Run #42099147476（Catalog JSONの`result.entries`契約の誤読）と後続修正Runの違いは保持する。

ここで達成したのは、**単一Source Index/Subjectの実CLI読取基線**。全Required Source解析、Ownerの意味受理、外部Harness/Skillロード、Windows、Host実権限・DB Effectはまだ未証明である。H2/H3実行時に上記固定版・Binary byte／Sourceが使われなければ歴史S1を現在の実呼出しとして継承せず、新しいW0で再固定する。

### 17.2 次の最小Taskと提出物を固定（新Runner・第二Oracle Schemaは作らない）

**Task**：同一の公開Subject `semantic-data:sales.order`を既存TEI CLIで調べ、(a)実Catalog/Inspectのkind/id、(b)Source Indexの実File/Byte fingerprintと参照、(c)Validateの警告/diagnostics、(d)未観測範囲を**それぞれ出典と共に説明**する。外部Provider Write/DB/経済取引や非公開入力は含めない。Independent Expectedは[TEI #1180](https://github.com/hat47x/tei-platform/issues/1180)のScenario/ObligationとS1固定実Sourceを使い**試行前**に別担当が保持し、Harness/Skill文書へ正答を入れない。

| Evidenceの当事者 | 受け取るべき実観測（試験者の記入欄として既存票へ付ける） | 言ってはいけないこと |
| --- | --- | --- |
| **Product基線 W0** | 固定TEI checkout/Binary SHA、実Source byte、実CLI stdout/exit、World/SourceIndex FP、今回の対象/時点 | 歴史S1のPASSから新HEADの同一性、全Source解析、意味受理を推定しない |
| **Harness H2 Tool-only** | 実Session IDとHarness/Model/Provider/Profile、Skillが与えられなかったConfig/Context、Tool呼出しの**Harness/Adapter実ログ**、実argv/cwd/exit/stdout digest、現在許可の用途・Audience | モデル回答の「Toolを使った」だけでToolの起動、Skill非接触、実権限を主張しない |
| **Harness H3 Skillあり** | H2と同じ実Binary/Workspace/Task・Tool権限、実LoaderのSkill root/参照ファイル**消費ログとbyte digest**、実Tool呼出し/出力、独立Session | Skillを配布場所にコピーしただけでLoaded、本文を回答へ引用しただけで使われたとしない |
| **独立採点** | 固定Expectedと実Consumer Answer/Warning/Unknownを第三者が比較。適格・正答・追加価値・Token/時間/人手を別判断 | SK-02 Checkerの`eligible-to-score`から正答やSkill有益性を導かない |
| **現在資格** | 実Host/Tool permission、送出Audienceと可観測の実境界、別Harnessへ持ち出せるEvidence範囲 | Configに書いた`egress_scope_observed=true`をOS/Network全経路の非漏えい実証としない |

**現有Checkerの利用制限**：[SK-02 test-only `check-sk02-pair-eligibility.cjs`](../../evaluations/tools/check-sk02-pair-eligibility.cjs)はJSON内の`tool_invocation_observed`、`skill_loaded`等の**申告された状態と比較整合**を検査するもので、実Tool、実Skill loader、実Hostの実ログを読み取っているわけではない。比較資格の前に、記録されたbooleanをどの具体的log/receipt/Source refが裏付けるか検査者が別欄で照合する。根拠未提出なら`insufficient-evidence`として、記録を真のH2/H3四Session実証と称しない。新Generic Evidence Validatorは作らない。

### 17.3 5つの検査段階と失効を混同しない

[TEI #1180](https://github.com/hat47x/tei-platform/issues/1180)の**Obligation→実Evidence→Claim資格**を、既存の[TEI #1163](https://github.com/hat47x/tei-platform/issues/1163)と同じ考え方で適用する。Unit/合成Fixtureは入力分類・否定Control、Conformanceは特定Contract、実Product CLI/Providerは実Source/Backend、Harness/Host観測は消費・操作境界、Owner受理は業務Meaning/用途承認をそれぞれ検査する。どの一段階のPASSも他段階の証明にはならない。

S1の歴史Evidenceは当時のSource/実バイナリに限定して保持。失効条件を①Source/Index/Meaning変更、②Binary/Skill/Tool Closure・Model・Harness Profile変更、③現在Grant/Recipient/開示変化、④Task/Expected/Consumer用途変更、⑤観測期限・Unknown/Partialの変化に分類し、影響したClaimのみ再資格化する。単に同じSHAや同じ説明文という理由で現在の許可・全件性・Skill実ロードを復活させない。

### 17.4 最初に実行する順と出口

既存の`H2→H3→H3→H2`四独立Sessionをそのまま実行し、**最初のH2一Sessionの実Tool log/実CLI receiptが存在するか**を初期停止線にする。無ければH3や第2Harnessを先に増やさず、Harnessで実CLI Toolが使えるかを明らかにする。H2が成立したときのみH3の実Load/Reference File利用を評価し、その後同条件で四Sessionと独立採点へ進む。効果がなければTool-only維持。必要な実観測が取れないHarnessは`unsupported / unknown`であり、全Harnessが使用不能という断定にしない。

**状態**：この§17は既存実S1証拠と次の実Harness実験を接合したRunbook追補であり、Product/Checker/Loader/Hostに新実装なし。H2/H3四独立Session・外部Harness Tool invocation・実Skill loader・独立採点/Cost・Owner受理・実Network非漏えいは**NOT RUN**。初回read-onlyへDB移行/RunPlan/Plugin全セットを必須化しない。


## 18. 2026-11-06：実TEI S1証拠台帳を新しい実行結果へ再束縛する

§15〜16で証拠をJSONに転記しただけでは、将来の再実行でSource/実Binary/CLI/Source Indexが変化しても、古いEvidence票を読んで成功したと誤認し得る。今回、既存[TAI S1 Probe](../../evaluations/tools/probe-tei-s1-real-source.cjs)に**限定的な`--verify-ledger`入口**を追加。実Go CLIで生成した当回Receiptを、先に固定された[公開S1証拠台帳](../../evaluations/records/TAI-TEI-S1-real-public-source-2026-11-06.json)へ突合する。別のE2E Runner/新Source Registry/Owner受理システムは作らない。

**実装された一致条件**：固定TEI Commit、実Source path/byte SHA-256、実GoバイナリSHA-256、Subject kind/id、Catalog 1件/indexed、Inspect成功、Validate結果と診断件数、空Workspace対照、Inspectが示すSource artifact/path/fingerprint/definition reference、WorldFP/SourceIndexFP、各CLI 4呼出しのexit・stdout SHA-256を**計31項目**照合する。過去RunのID/日時/Owner受理を新Runで再発行する仕組みではない。採点が一致しても「新しいModel Revisionに自動更新済み」「AIがSkillを使用した」にはならない。

**CI実証**：[TAI 実S1＋台帳照合 #42106804110](https://github.com/hat47x/tai-pleroma/actions/runs/42106804110) は**completed/success**。実ジョブログで`compared=31`、`verdict=matching-bounded-S1-evidence`を確認。さらに当回ReceiptのSource SHA-256を意図的に0へ置換した負例は非0終了し、`ledger mismatch: source bytes`を記録した。[専用GitHub Actions](../../.github/workflows/tai-tei-s1-real-public-cli.yml)には**台帳だけが変更された場合もCIを起動**するパス条件を追加した。これは公開固定Fixture・一環境の実CLI比較であり、第三者署名済みReceipt・H2/H3の実Skillロード・現行Grant・Business Oracleではない。

**差分時の判断**：新TEI HEADへ移る際は、古い台帳の一致を証明するためSourceやBinaryを暗黙に差し替えない。まず失効として扱い、独立Expected・対象Subject・Source bytes・実CLIを両腕で再固定したうえで**新しい版の受入票を別途作る**。旧Ledgerは過去のS1限定証拠として保持。GoのTarget、Provider、本番組織Action、SHO Reader、EKI回復へ証拠を一般化しない。


### 18.1 台帳・Receipt・実CLI応答のJSONを曖昧に解釈しない（2026-11-06）

実S1の履歴台帳と当回Receiptが「31項目で一致した」という主張は、そもそも**同じJSON memberが二回現れて値を後勝ちで上書きした入力**を受理しては成立しない。[SK-02試行JSONの重複member拒否](../../evaluations/tools/check-sk02-pair-eligibility.cjs)を、[TAI S1 Probe](../../evaluations/tools/probe-tei-s1-real-source.cjs)の実CLI JSON読込および`--verify-ledger`の台帳／当回Receipt読込から再利用する。**新Parserや横断Schemaは追加しない**。構文不正・同一Object内のmember重複・Unicode escape後に等価なmemberを入力不適格として拒否し、別Object内の同じkeyは合法とする。

合成負例S1-W09〜13と、実S1 CIで固定台帳／当回Receiptの実ファイルそれぞれへ重複keyを注入する故障試験を追加。検査失敗は`DUPLICATE_TRIAL_JSON_MEMBER`として非0終了し、Ledger照合の合格記録を出さない。テスト結果は当該変更後のActions実Jobで判定する。**正規JSONの同一値が署名済み・独立収集済み・出典の鮮度が保証されたこととは異なる**。履歴S1に署名や実Harnessロード資格を付与しない。次段の最初のH2セッションは§17で独立に実施する。


---

<!-- sk02-h2-first-real-session-operational-cut-20261106 -->
## 19. 2026-11-06：W0成立後に実施する「最初のH2実Session」実行票

本節は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の**次のBlocking Exit**を、準備の議論ではなく**外部AI Harnessが実TEI Toolを起動した一つの実観測**へ収束するための最小運用手順。既存§12 Trial Card／§17 W0→H2/H3／§18 S1 ledgerを使用し、第二Script・独立Runtime・新共通Evidence Schemaを追加しない。実H2は**本節追加時点ではNOT RUN**。

### 19.1 固定した公開実験入力（歴史的S1 Witnessと新しい実起動物を混同しない）

| 要素 | 実験で固定する値と現在の資格 |
| --- | --- |
| TEI Product Source | `hat47x/tei-platform` exact commit `50ebf8014340fd1906f6b35cfa30173e0ee2fc6c`。新HEADへ切替えるなら新W0で再固定 |
| Workspace／Subject | `reference/workspace`／`semantic-data:sales.order`。Sourceは `semantic/sales/order.tei`、SHA-256 `f2063418b893a60a9f948edbb2b23ec821f7a15ed8e5863c36e1b72abade1e33` |
| W0実CLI Witness | Go `go1.26.10`／`linux/amd64`、歴史的CI実Binary SHA-256 `6769ec0908007f1147de0502b3e88421159e0b2c4df70fc57b53c9d29ccbc36f`。**H2で同じBinaryが実起動された証拠ではない** |
| W0台帳 | [公開S1結果](../../evaluations/records/TAI-TEI-S1-real-public-source-2026-11-06.json)、[台帳照合付き実CI #42107393245](https://github.com/hat47x/tai-pleroma/actions/runs/42107393245)。台帳は試験者が保持し、HarnessのTask/Toolに事前投入しない |
| H2 Tool-only | 外部Harnessの**実名称・版・Model・Session ID・実Tool Profile**をTrial Cardへ実記入。Skillをロードしない構成／参照ファイルの非露出を確認。候補名だけで対応済みとしない |
| H3 Product Skill | H2のTask・Binary/Workspace・Tool権限を同一にし、TEI Product Skillの**固定実byte**のみ追加。現在の実験候補は[TEI Draft #2863 exact commit `97161e2b5535378edb5a8b6ea6b398454aa0c84c`](https://github.com/hat47x/tei-platform/pull/2863)の `skills/yi-tei-modeling/SKILL.md` と必要な `references/`。Draft/未mergeを正式配布物として扱わない |

**実行環境の準備**：外部Harnessへは**固定済みの実行バイナリと公開Workspaceだけ**をTool側の作業空間として与える。W0台帳／独立Expected／前Session回答／採点表はAIから見えない試験者側に保管。H2のTool経由でSkill文書を検索・開ける状態なら、Skill非ロード対照としての適格性を再評価する。H3のSkill追加が隠れたTool/権限/モデル/Source変更を伴えば同一Pairにしない。

実BinaryのハッシュとWorkspaceの実Source byteを**各Sessionの使用直前**に確認する。Linux CIのバイナリは別Host/別OSで同じSHAと推定できない。別OS/Go版/新ビルドでSHAが違えば、その試行専用の**新W0実測**を先に取り、H2とH3の両方がその同じ実行物を使うことを保証する。固定Rootをコピーした後のSource移動・差替えはTrialの失効事由とする。Toolが単純なshellを備えず認可済みMCP/CLI Adapterで呼ぶ場合も、当該実動作・実引数の観測を要求し、**新たなMCP Server開発を初回の前提にしない**。

### 19.2 実験Task（H2/H3へ同じ文章を与え、答えを事前に渡さない）

> 支給された公開TEIモデルの `semantic-data:sales.order` を、使用可能なread-only TEI CLI/Toolで調査してください。Catalog/Inspect/Validateの実結果に基づき、(1)利用者定義の対象kind/idを特定できるか、(2)そのSource Indexのファイル・指紋・definition参照を確認できるか、(3)Validationの `ok`／診断・Warningの有無を区別できるか、(4)その結果だけでは確認できない事項は何かを、使用したコマンドと出典を示して報告してください。Source編集・DB書込み・外部公開・権限追加は行わず、実行不能または未確認ならそう記してください。

このTaskは具体的な期待結果やハッシュの正答をHarnessへ教えない。初回H2では**実Tool呼出しを観測することが先決**であり、`trace`/追加Operator/複数DBへの展開を要求しない。H3でも**Task本文は完全に同じ**とし、Skill Loaderのある/なしだけを主な介入変数にする。

### 19.3 実Tool呼出しの最小Receiptと、最初の一Session出口

**実H2-01で試験者が取得する項目**：①外部Harness/Model/設定版・独立Session ID、②Harnessから発行された実Tool Request/Invocationの順序と時刻、③Tool側が実起動したTEI executableのpath/byte digest＋cwd＋実argv＋exit＋stdout/stderr byte digest、④その時点のWorkspace/Source/Subject/World・SourceIndexの照合値、⑤Harnessが実受信したTool Responseと利用者向け回答の差、⑥実Task・Audience/Grant・許可されたDisclosure、⑦Token/時間/人手と失敗理由。**実値が無い項目は空欄のまま推定せずunknown**。独立ExpectedはTask提出後に試験者が採点する。

CLIで必要となるread-only呼出し例（実際に使ったargvは**HarnessのToolログ**で観測する。これは試験者の参考値であり、Tool呼出しの代替証拠ではない）：

```sh
"$TEI_BIN" model catalog -workspace "$TEI_WORKSPACE"
"$TEI_BIN" inspect -workspace "$TEI_WORKSPACE" -subject-kind semantic-data -subject-id sales.order
"$TEI_BIN" validate -workspace "$TEI_WORKSPACE" -json
```

**H2-01のPASS**＝外部Harnessの実Session→実Tool request→Product CLI実起動→CLI responseを同一Taskで突合できたこと（CLI Outputの正答/警告保持は**別採点**）。LLM回答中の「Toolを使った」、TAI CIの直接呼出し、Trial JSON自己申告boolだけでは不足。実Toolログを取得できない場合は `insufficient-evidence`、Tool自体がない場合は`unsupported/unknown`としてそのHarnessのH3へ進まず、既存#168の実接続経路を確認する。新Runner/常駐Agentを追加しない。

### 19.4 H2後のH3と四Session比較の条件

H2-01の実呼出しが確認された場合のみ、次の**独立Session**でH3の実Skill root消費と必要reference消費を、Harness/Adapterの実ログまたは参照byteの実Readと照合する。Skill Directoryに置いた/Skill名が宣言された/AIがSkillを引用しただけでは**Loaded**としない。H3でTool権限やRepository全体アクセスまで増えた場合は、Skillの効果と混ぜずPair不適格とする。

最終順序 `H2→H3→H3→H2`、モデル/ハーネス/Profile・固定Source・Task・Tool Set・最大許容費用を同条件に保ち、**各Sessionは会話・結果・Skill状態を引き継がない**。結果判定は①比較適格性（既存SK-02 Checkerと実ログ照合）、②独立Expectedに対する正答・Warning/Unknown保持、③Skill差分の追加価値とToken/時間/人手を別票で扱う。H3が同等または悪化すればTool-onlyを維持。第二Harness・TAI Handoff・write/DB/RunPlan/MFTは**四Sessionの実在性と差分が判定可能になった後の条件付き工程**。

**本節の実施状態**：W0固定公開Source・実CLI・台帳照合のCIだけが限定成功。**外部Harness H2-01の実Tool log、H3のSkill Loader/Reference実読込、H2/H3四Session、比較採点、OS/Network非漏えい・Owner意味受理はNOT RUN**。
