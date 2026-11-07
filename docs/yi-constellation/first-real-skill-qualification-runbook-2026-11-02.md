# YI Constellation：最初の実Product Skill資格確認 Runbook（2026-11-02）

**状態（2026-11-07確認）**：固定TEI実CLIの公開Source W0/S1は限定達成。[TAI実S1 #42107393245](https://github.com/hat47x/tai-pleroma/actions/runs/42107393245)のSource Index／台帳照合に加え、[TEI PR #3113](https://github.com/hat47x/tei-platform/pull/3113)の**実DSH外部Harness Tool-only探索Session**で固定TEI実バイナリの呼出し・Tool応答・最終回答が観測された（§24）。ただし**H2の実ファイル／Skill／Reviewer隔離が未証明**のため、4独立Sessionの比較適格Slotには算入しない。H3のSkill実Load・4Session採点・実Egress否定／Owner意味受理は**NOT RUN**。次のBlocking Exitは新たなTool接続の存在確認ではなく**隔離・Source／Tool／Grantが固定された比較適格H2 Session**（§24.2）。旧§1〜14の「TAIでCLI未実行」等は当時の履歴で、現在の事実ではない。新Harness Runner/統合Registryなし。

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
### 18.2 実argvと作業ディレクトリをS1証拠台帳に束縛する（2026-11-06）

[前節の31項目Ledger照合](../../evaluations/tools/probe-tei-s1-real-source.cjs)は、CLI 4呼出しの標準出力Hash/終了コードを固定していたものの、Receiptの`observations[].args`・`cwd`は実際には比較していなかった。これでは、同じstdout digestを引用しながら異なるWorkspace・Subjectを読んだかのようにargv/cwdだけを書き換えた票を形式上PASSにできる。最初のread-only S1ではその差がTaskの意味に直結する。

**実装**：既存S1 Probeの`verifyLedger`内で、Ledgerに固定された`reference/workspace`と当回Receiptの絶対CWDを使い、**4つのCLI argvをコマンド・順序・Workspace・Subject/Format・追加Optionまで完全一致**で照合。4呼出しすべてのCWDが同じことも検査する。これを既存31項目に8比較追加して計39項目とする。S1-W14〜W19は正常な4呼出し／別Workspace／別Subject／write-option混入／別CWD／CLI順序交換の合成負例。さらに既存の[TAI S1実CLI Workflow](../../.github/workflows/tai-tei-s1-real-public-cli.yml)で、**本物の実CLI出力Digestを残したまま**ReceiptのCatalog Workspaceだけ、Inspect CWDだけをそれぞれ改変して拒否を確認する。

**証拠の限界**：同じargv/cwd文字列が記録されていることは、Host/Processが本当にその引数を渡したことの第三者証明ではなく、symbolic linkや別mountの実Target同一性も示さない。このテストは既存Probeが生成した実CLI Receiptの**内部整合と失効検知**に限る。歴史台帳の新しい認証方式や実Harness連携、追加Product Gateは作らない。CIのPASSは当該実行のexact-head/Jobログで確認するまでは宣言しない。最初のH2独立Sessionの実Tool/Loader観測を引き続き優先する。

## 19. 2026-11-06：W0成立後に実施する「最初のH2実Session」実行票

本節は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の初回H2実行票。制定時は外部HarnessでのTool実起動も未実施だったが、[TEI PR #3113](https://github.com/hat47x/tei-platform/pull/3113)のDSH探索的Tool-only Sessionで**実Tool transport到達**が観測済み（§24）。**比較資格に必要なSkill非露出・実隔離・同条件・独立Expected／Egressは未確認**。§12 Trial Card／§17／§18を再利用し、第二Script・独立Runtime・新共通Evidence Schemaは追加しない。

### 19.1 固定した公開実験入力（歴史的S1 Witnessと新しい実起動物を混同しない）

| 要素 | 実験で固定する値と現在の資格 |
| --- | --- |
| TEI Product Source | `hat47x/tei-platform` exact commit `50ebf8014340fd1906f6b35cfa30173e0ee2fc6c`。新HEADへ切替えるなら新W0で再固定 |
| Workspace／Subject | `reference/workspace`／`semantic-data:sales.order`。Sourceは `semantic/sales/order.tei`、SHA-256 `f2063418b893a60a9f948edbb2b23ec821f7a15ed8e5863c36e1b72abade1e33` |
| W0実CLI Witness | Go `go1.26.10`／`linux/amd64`、歴史的CI実Binary SHA-256 `6769ec0908007f1147de0502b3e88421159e0b2c4df70fc57b53c9d29ccbc36f`。**H2で同じBinaryが実起動された証拠ではない** |
| W0台帳 | [公開S1結果](../../evaluations/records/TAI-TEI-S1-real-public-source-2026-11-06.json)、[台帳照合付き実CI #42107393245](https://github.com/hat47x/tai-pleroma/actions/runs/42107393245)。台帳は試験者が保持し、HarnessのTask/Toolに事前投入しない |
| H2 Tool-only | 外部Harnessの**実名称・版・Model・Session ID・実Tool Profile**をTrial Cardへ実記入。Skillをロードしない構成／参照ファイルの非露出を確認。候補名だけで対応済みとしない |
| H3 Product Skill | H2のTask・Binary/Workspace・Tool権限を同一にし、TEI Product Skillの**固定実byte**のみ追加。初回の固定Treatmentは**同じTEI commit `50ebf8014340fd1906f6b35cfa30173e0ee2fc6c`に含まれる**[Product Skill](https://github.com/hat47x/tei-platform/tree/50ebf8014340fd1906f6b35cfa30173e0ee2fc6c/skills/yi-tei-modeling)のroot Git blob `9cd8475bd6489c6661ae644bf771cfcce04188b1`＋reference Git blob `ec2f90e85ed42659aca8b44a9be216987860b099`（§22）。[Draft #2863](https://github.com/hat47x/tei-platform/pull/2863)は別Treatmentであり初回に混ぜない |

**実行環境の準備**：外部Harnessへは**固定済みの実行バイナリと公開Workspaceだけ**をTool側の作業空間として与える。W0台帳／独立Expected／前Session回答／採点表はAIから見えない試験者側に保管。H2のTool経由でSkill文書を検索・開ける状態なら、Skill非ロード対照としての適格性を再評価する。H3のSkill追加が隠れたTool/権限/モデル/Source変更を伴えば同一Pairにしない。

実BinaryのハッシュとWorkspaceの実Source byteを**各Sessionの使用直前**に確認する。Linux CIのバイナリは別Host/別OSで同じSHAと推定できない。別OS/Go版/新ビルドでSHAが違えば、その試行専用の**新W0実測**を先に取り、H2とH3の両方がその同じ実行物を使うことを保証する。固定Rootをコピーした後のSource移動・差替えはTrialの失効事由とする。Toolが単純なshellを備えず認可済みMCP/CLI Adapterで呼ぶ場合も、当該実動作・実引数の観測を要求し、**新たなMCP Server開発を初回の前提にしない**。

### 19.2 参加者向けの実験Taskは一つの固定ファイルを使う

H2/H3の4独立Sessionに渡す唯一の参加者向け指示は、[固定Participant Task](../../evaluations/fixtures/sk02-tei-public-read-participant-task-2026-11-06.txt)の**実byte列**。§17や§19の設計用Obligation・例示BlockquoteをTaskの代替にしない。固定SHA-256は§20を参照する。

固定Taskは、**対象の意味、定義元Source、注文合計額を表す属性の識別子と型、Validateの診断/Warning/未知、実CLI根拠**を要求する。Source Indexのfingerprint/definition referenceはReviewerの技術的な証拠照合であり、Participantへ正答を教える別指示ではない。Taskの文面・末尾LFを含むbyteを四Sessionで維持する。変更が必要なら両腕同時に新Task raw SHAと独立Expectedを再固定し、旧Trial Groupへ混入させない。

### 19.3 実Tool呼出しの最小Receiptと、最初の一Session出口

**実H2-01で試験者が取得する項目**：①外部Harness/Model/設定版・独立Session ID、②Harnessから発行された実Tool Request/Invocationの順序と時刻、③Tool側が実起動したTEI executableのpath/byte digest＋cwd＋実argv＋exit＋stdout/stderr byte digest、④その時点のWorkspace/Source/Subject/World・SourceIndexの照合値、⑤Harnessが実受信したTool Responseと利用者向け回答の差、⑥実Task・Audience/Grant・許可されたDisclosure、⑦Token/時間/人手と失敗理由。**実値が無い項目は空欄のまま推定せずunknown**。独立ExpectedはTask提出後に試験者が採点する。

CLIで必要となるread-only呼出し例（実際に使ったargvは**HarnessのToolログ**で観測する。これは試験者の参考値であり、Tool呼出しの代替証拠ではない）：

```sh
"$TEI_BIN" model catalog -workspace "$TEI_WORKSPACE"
"$TEI_BIN" inspect -workspace "$TEI_WORKSPACE" -subject-kind semantic-data -subject-id sales.order
"$TEI_BIN" validate -workspace "$TEI_WORKSPACE" -json
```

**H2 Tool transportの限定PASS**＝外部Harnessの実Session→実Tool request→Product CLI実起動→CLI responseを同一Taskで突合できたこと。DSH探索Sessionはこの限定条件に達したが、**H2比較適格のPASSとは別**（§24）。CLI Outputの正答/警告保持は**別採点**。LLM回答中の「Toolを使った」、TAI CIの直接呼出し、Trial JSON自己申告boolだけでは不足。実Toolログを取得できない場合は `insufficient-evidence`、Tool自体がない場合は`unsupported/unknown`としてそのHarnessのH3へ進まず、既存#168の実接続経路を確認する。新Runner/常駐Agentを追加しない。

### 19.4 H2後のH3と四Session比較の条件

**Skill非露出・実Sandbox／Tool／Task／Source同一性と現在Grantまで確認された比較適格H2 Session**が成立した場合のみ、次の**独立Session**でH3の実Skill root消費と必要reference消費を、Harness/Adapterの実ログまたは参照byteの実Readと照合する。Skill Directoryに置いた/Skill名が宣言された/AIがSkillを引用しただけでは**Loaded**としない。H3でTool権限やRepository全体アクセスまで増えた場合は、Skillの効果と混ぜずPair不適格とする。

最終順序 `H2→H3→H3→H2`、モデル/ハーネス/Profile・固定Source・Task・Tool Set・最大許容費用を同条件に保ち、**各Sessionは会話・結果・Skill状態を引き継がない**。結果判定は①比較適格性（既存SK-02 Checkerと実ログ照合）、②独立Expectedに対する正答・Warning/Unknown保持、③Skill差分の追加価値とToken/時間/人手を別票で扱う。H3が同等または悪化すればTool-onlyを維持。第二Harness・TAI Handoff・write/DB/RunPlan/MFTは**四Sessionの実在性と差分が判定可能になった後の条件付き工程**。

**現在地（§24参照）**：W0/S1のCI限定成功に加え、DSH探索的Tool-only 1 Sessionの実Tool request／実CLI／Harness replyは観測済み。ただし**実作業Dir外へのReadが可能でH2の非露出・隔離は不適格／未確認**。H3 Skill Loader・四Session比較・独立Expected採点・OS/Network非漏えい・Owner意味受理は**NOT RUN**。9探索Attemptを4Slotの先行実績へ算入しない。



<!-- sk02-dbcheck-outside-readonly-scope-20261106 -->
### 19.5 新CLIを読むだけでread-only対応コマンドと誤認しない（2026-11-06）

[TEI merged #2894](https://github.com/hat47x/tei-platform/pull/2894)で新しくProduct CLIに`tei dbcheck`が加わった。ただしこのCommandはDSNが与えられれば実PostgreSQLに接続し、**一時表のCREATE/DROP DDL**を実行する。成功したら表が消える設計でも、初回SK-02の「Source/モデルを読み取るだけのTool」とは異なる。DSNが無い場合のexit 2／非実行も実DB資格ではない。

**H2/H3両腕の既定Command whitelistを変更しない**：既存SK-02 Checkerが選択済みとする`version`、`commands`、`model catalog`、`inspect`、`trace`、`validate`の必要read-only呼出しのみ。既存[SK-02 Checker](../../evaluations/tools/check-sk02-pair-eligibility.cjs)の`readOnlyCommandFamily`は`dbcheck`を`outside-initial-readonly-profile`に分類する。`commands`一覧に載っていること・CLIに実装されていること・内部で一時表を削除することは実行許可ではない。`dbcheck`やその他未選択コマンドを起動した試行は比較資格を停止し、実Host/DB側の副作用が無かったとも断定しない。OS/Tool Policyの実許可境界は別観測。

**実DB準備確認はTEI [#2555](https://github.com/hat47x/tei-platform/issues/2555)の後続専用レーン**に置く。H2 Tool-onlyのToolが`dbcheck`実行を必要とする設計なら、このread-only Taskの範囲を変えた新実験として両腕を同時に再設計し、最初の四Sessionに混入させない。

## 20. 2026-11-06：実Harness四試行へ渡す参加者TaskとHoldout隔離

### 実参加者へ渡す唯一のTask（H2/H3共通）

[参加者向け固定Task本文](../../evaluations/fixtures/sk02-tei-public-read-participant-task-2026-11-06.txt)を**全4独立Sessionへ同じbyte列**で渡す。UTF-8・末尾LF込みのSHA-256は `38a0b238018e050f2116f10f1ca2cb3a54319c2743e2fb9bbe128d4be96a84cf`。Participant Taskはモデル要素 `semantic-data:sales.order`、公開 `reference/workspace` を明示するが、**回答すべき属性名・型、実Source file、診断件数、正答判定票を記さない**。実CLI・Product Sourceの読取りに基づく回答を要求する。Taskの自然言語をH3だけ言い換えない。

**Participant隔離が必須**：両腕からアクセス可能にするのは当該Task本文と**固定TEI実Binary＋公開`reference/workspace`のみを抽出した限定ビュー**、および各腕で許可したToolだけ。**TEI Repository全体のCheckoutを参加者へ公開しない**（そこにはH3のSkillも含まれる）。TAI repo全体、SK-02の評価計画、S1 Evidence台帳、Reviewer用独立Expected/採点表、他SessionログをParticipant向けWorkspace・添付・Tool出力へ配置しない。H2にProduct Skill root/referencesを一切示さない。H3は同一TEI固定版の[Product Skill `yi-tei-modeling`](https://github.com/hat47x/tei-platform/tree/50ebf8014340fd1906f6b35cfa30173e0ee2fc6c/skills/yi-tei-modeling)（§22のroot＋必須referenceの固定byte）だけを**実Load可能な仕組みに置き、その実ロードSource byteと経路を別記**。単にファイルを配置してもLoadedと見なさない。GitHub等を自由に検索できるProfileでは評価資料が漏れるため、両腕の実Tool scopeを固定・観測し、Oracleが取得可能なら盲検評価とは呼ばず停止する。

### 実行者向け準備と独立Holdout（Participantへ送らない）

- **Product証拠のPin**：実S1 [#42106804110](https://github.com/hat47x/tai-pleroma/actions/runs/42106804110)の固定TEI commit `50ebf8014340fd1906f6b35cfa30173e0ee2fc6c`、Source digest `sha256:f2063418b893a60a9f948edbb2b23ec821f7a15ed8e5863c36e1b72abade1e33`、Go 1.26.10 Linux/amd64 binary digest `sha256:6769ec0908007f1147de0502b3e88421159e0b2c4df70fc57b53c9d29ccbc36f`を**基準候補**にする。実Harnessが別OSやビルド方法なら値を旧S1に偽装せず、双方の腕を新しい同一実Binary/環境/Sourceに再固定し、Holdoutも同時に再確認する。`workspace_tree_digest`はS1の単一Source digestやWorldFPを代入して捏造せず、実Checkout全管理対象の明示したScope・順序・byteから算出・記録する。
- **Reviewer-only Expected**：実Sourceの原byteと固定TEI実CLI出力をAgentとは独立の手順で確認し、Subject kind/id、定義元Sourceとbyte、注文合計属性名と型、validateの診断・Warning/Unknown・許容される未確認表現、引用必須項目、実行してはならない操作を**Session開始前に別保管**。採点表の完全byte/digestは実Reviewer管理下に置き、四Sessionが終了するまでParticipantへ配布しない。公開SourceをAgentが調査すること自体は正常だが、答えを評価票から漏らしてよいことにはならない。
- **選定するHarness**：モデル・Build・Provider、tool/profile/権限、実ネットワーク/外部送信観測可能範囲、Product Skill実Load表示、Session分離能力を現物で確認。選べないHarness名を事前に合格扱いしない。観測不能な効果欄は`unknown`で保持し、`false`を作らない。

### 四つの新規Session／独立評価

| 順序 | 腕 | 実際に必要な隔離・観測 |
| --- | --- | --- |
| 1 | H2 Tool-only | 独立Session・Skill非公開かつ非ロード・実Tool args/outputs |
| 2 | H3 Product Skillあり | 新Session・同じToolとTask、同一Skill Packageの**実ロード** |
| 3 | H3 Product Skillあり | 再び新Session・2とは会話履歴を共有せず、同一Skill byte/activation |
| 4 | H2 Tool-only | 新Session・Product Skillを露出せず、先行三回答の漏出なし |

[既存SK-02 Checker](../../evaluations/tools/check-sk02-pair-eligibility.cjs)に供給する4 Trialの`session_id/arm`、同一`prompt_digest/repo_head/binary_digest/workspace_tree_digest/world_fingerprint/source_index_fingerprint/cli_cwd/harness_build/model_profile/tool_profile_digest/principal/grant_profile_digest/disclosure_profile_digest/oracle_version`、CLI argv・実Exit/Stdout・Tool/Skill Load根拠を、**観測した元ログの位置**と結びつける。H2の`skill_exposed=false/skill_loaded=false`、H3の`skill_loaded=true`などは**実Harnessから検証できたときだけ**記入する。Egress/Grant不明なら比較適格性を自動PASSとしない。

**合格・停止**：Checkerの`eligible-to-score`はメタデータ比較資格のみ。次に別保管した独立Expectedで**回答の正しさ/不明とWarningの保持**を採点し、実Tool回数、実Token/コスト、経過時間、手直し回数を独立欄で比較する。実Skillがロードできなければ「H3結果」ではなく試行不成立、どちらも誤答ならSkill Benefitにしない。n=4の結果を統計的優越/全Harness適用へ一般化しない。外部Harnessへの実Skill Install/Loadと4 Sessionは現時点**NOT RUN**。新Runner・別共通Oracle・新Policyを実装しない。




---

<!-- sk02-rd-itt-pp-separation-20261106 -->
## 21. 2026-11-06：Skill割付と実提供を区別した比較・価値評価

### 21.1 R/DとITT/PPの分離

**R（Requested/assigned）**は実験で割り付けたH2＝Tool-only／H3＝Product Skill付き条件。**D（Delivered/observed）**は、外部Harness/Adapterの実ログでSkill root・必要referencesをロードした事実、Tool request→実CLI result、Source/実Binary/Current Grantの同条件が確認された状態。RがH3でもDが不明・未提供ならSkillが有効だったとしない。Trial JSONの`skill_loaded=true`やLLMの自己説明はDの一次証拠ではない。

**ITT（割付ベースの記述的比較）**は、実Skillロード失敗・Tool利用不能・未知を含め、割り付けた4 Sessionすべての運用結果・追加費用・失敗分類を残す。成功したH3だけを抽出して運用上の価値を過大評価しない。**PP（実提供ベースの条件付き比較）**は、H3でSkill/必要refsの実Load、H2でSkill非露出、両腕で実Tool/Source/Model/Taskの比較条件が観測された試行だけを、既存SK-02の比較資格と独立Oracleで分析する。PPの「条件成立サブセット」はITTや全Harnessの導入利益と同一ではない。4 Sessionは実用的な初期反証であって、母集団の効果推定・p95比較ではない。

### 21.2 既存Trial Cardに記録すべき内容（新Runtime/Oracle Schemaは不要）

| 項目 | 試行中に保持する実証拠 | Claimの限界 |
| --- | --- | --- |
| **固定Task** | §20のParticipant Task raw SHA、Task本文、Independent Expectedの別保管状態 | 各腕でTaskが変わったらSkillの効果ではなくTask差 |
| **R：割付** | Session ID、割付arm、順序、固定Tool/Profile/Model/実Binary | 割付だけでSkill実Loadとは言えない |
| **D：提供** | Harness Tool Request／Adapter実CLI argv/exit/stdout、Loaderの実Skill root/refs byte-read | 申告boolのみならunknown、PP不適格 |
| **回答品質** | 出典、対象Source/属性・型・診断・Warning・Unknownを別Reviewerが事前Expectedと比較 | loadedやeligible-to-scoreは正答保証ではない |
| **運用費** | 成功／失敗を問わずToken/Tool呼出/経過時間/準備・人手再実行／観測範囲 | 四試行の記述的結果まで。配布済み/全Harness適合へ外挿しない |

**Participant Taskの原byteを比較条件に結ぶ**：実4 Sessionの記録を採点するReviewerは、固定[参加者Task](../../evaluations/fixtures/sk02-tei-public-read-participant-task-2026-11-06.txt)とTrial JSONを別々に保持する。Checkerを`node evaluations/tools/check-sk02-pair-eligibility.cjs actual-four-trials.json --task-file evaluations/fixtures/sk02-tei-public-read-participant-task-2026-11-06.txt`の形式で使用し、原byteから計算したSHA-256が4試行の記録に等しいときだけ比較資格の判定へ進む。Task原文未指定なら`insufficient-evidence`、全腕の記録が同じでも事前固定Taskと異なるなら`ineligible`。元Promptの実Harness受信、試行の実Source読取・Skill非露出/実Loadは別のログで確認する。[CI #42110536408](https://github.com/hat47x/tai-pleroma/actions/runs/42110536408)では**合成4 TrialのCLI評価**で一致・全腕誤Prompt・原文不明を実検査し成功。実4 Sessionの結果ではない。

### 21.3 追加の反証は既存Checker／実ログ照合で扱う

- **RD-01：H3割付だがSkill未ロード**。R=H3を維持し、D=not-deliveredならITTに失敗を含め、PPには不適格。勝手にH2へ付替えない。
- **RD-02：H2がSkillを閲覧可能**。Skill非ロードでもTool/GitHub/Workspace経由でSkillの文書が見えていた場合、H2の非接触の前提を再評価しPPを停止。
- **RD-03：H3だけ別Task/Oracle版**。同一Pair不適格。§20の同じbyte Taskを唯一の配布物とする。
- **RD-04：回答が一致しても実Tool未観測**。D=unknown、別CIの実CLI S1成功はHarness実呼出しの代理不可。
- **RD-05：実Skill Loadは成功、回答は誤り**。Dは成立しても独立Oracle不合格。技術的ロード成功を価値成功へ昇格しない。

**実行の優先順**：§19の最初の外部H2一Sessionを実Toolログ込みで観測→H3の実Loader/参照文書消費を別Sessionで確認→固定順`H2→H3→H3→H2`の四Sessionと事前Holdoutによる独立採点。追加合成CI・第二Agent Host・配布Registryは初回に不要。今回の追補は**試験方法の補正**であり、実H2/H3四Session、ITT/PPの正答・費用、Owner受理は**NOT RUN**。

## 22. 2026-11-06：H3 Product Skillを実Toolと同一TEI改訂から固定する（Load未実証）

初回H2/H3比較の前提として、**H3だけ別TEI改訂のSkillを読むこと**と、**Skillファイルを実Harnessがロードしたこと**を混同しない。W0の実Product Source pin `50ebf8014340fd1906f6b35cfa30173e0ee2fc6c`に、H3で使用候補とする次のTEI Product Skillファイルが実際にあることを、固定Git blobで確認した。

| H3候補（TEI Product管理の原文） | 固定Git Blob SHA-1（Git object identity） |
| --- | --- |
| `skills/yi-tei-modeling/SKILL.md` | `9cd8475bd6489c6661ae644bf771cfcce04188b1` |
| `skills/yi-tei-modeling/references/read-only-model-investigation.md` | `ec2f90e85ed42659aca8b44a9be216987860b099` |

[既存TAI実Product S1 CI](../../.github/workflows/tai-tei-s1-real-public-cli.yml)に固定TEI Checkoutから`git hash-object`で上記2ファイルの**実バイト所属**を検査するPreflightを追加した。Git blob identityと実H3 LoaderのRead観測は別。実H3では配置したSkill root・実参照ファイルのPath/byte/Load時点・既存Loader観測方法を新Sessionの証拠へ記録する。H2には同ファイルを**公開・Mount・Tool検索対象に含めない**。H2のTEI SourceやCLI実行バイナリだけを保持し、両腕のTool Profile・Grant・実Buildを合わせる。`git hash-object`合格で`skill_loaded=true`を記入しない。

### 22.1 この固定版に実在する内容上のリスク

- **Catalog JSONの形式不一致**：この固定Product Skill rootの手順は `entries[].subject.kind/id` と書くが、同一改訂の実`model catalog` CLIは`tei.cli.model/v0` envelopeに含まれる **`result.entries[].subject.kind/id`** を返す。[実CLI契約](https://github.com/hat47x/tei-platform/blob/50ebf8014340fd1906f6b35cfa30173e0ee2fc6c/cmd/tei/cli_model.go)およびTAI S1初回失敗[#42099147476](https://github.com/hat47x/tai-pleroma/actions/runs/42099147476)から独立に確認できる。H3がSkillの記述に従って失敗しても、実験後に回答や観測を修正して成功にしない。製品文書の修正はTEI #2605へ引き渡し、新版なら新しいSkill treatmentを登録する。
- **`go run`と固定Binaryの混同**：同Skillは例示コマンドに `go run ./cmd/tei` を示すが、今回比較は既存S1で固定した実Go Binaryだけを両腕の**同一Tool Profile**として使う。H3の提案が許可外 `go run`へ逸れたときは、Tool Profile差/不成立と、実際に何を試したかを別に記録する。`go run`を同じBinary使用と偽らない。実Harness Adapterが呼出しを制限・拒否した場合もToolログを残す。
- **参加者課題と既存例の近接**：参照ファイルには `semantic-data:sales.order`と同じ`subject-id sales.order`の実行例が存在する。これは固定Taskが直接指名したSubjectであるため、独立Oracleの答えを漏洩したという証明ではない。ただし**例示ありの公開Taskに対する手順効果**という評価範囲に限定し、未例示Subjectの自律発見・一般的Skill優位を結論にしない。将来の未例示Taskは、別の事前固定Task/Source/Expectedを持つ別Trial Groupで評価する。
- **文書の状態表示**：同改訂のSkillには旧`NOT RUN`表記が残る。[TEI Draft #2863](https://github.com/hat47x/tei-platform/pull/2863)は限定Product CLI成功／Harness未実施を正しく書き分ける文書修正であり、この固定S1改訂と同一内容ではない。H3だけDraft #2863を混入させることは初回Skill PackageのPin変更。新版を採用するときは両H3 SessionのPackage byteとTrial Groupを明示して登録し、旧S1と新Skillを同一Versionとして扱わない。

### 22.2 実H2/H3着手の停止線

初回のH2 Tool-onlyではTEI Product **Skill非露出**と実Binary呼出しを観測する。H3は同じCLI/Task/Sourceで上記root＋必要referencesの実ロード証拠が揃ったときだけD（Delivered）成立とする。ファイルがCheckoutに存在するだけなら**Available**であり**Loaded**ではない。`R=H3`でLoad失敗はITTに含め、PPのSkill実提供条件は未成立。Tool呼出しが間違ったcommand/result pathを参照した場合は、その失敗をそのまま記録し、修正されたSkillを試すなら別治験とする。

**状態**：上記はTEI固定CheckoutからのGit原文照合と再現可能なCI Preflightの設計・実装。外部Harnessへの実配布／実Load／4 Sessionは**NOT RUN**。Source Index／Skill byte／AI Tool Usage／Owner Meaning／Current Grantの証拠を混同しない。

### 22.3 H2のSkill非露出は「Loadしない」だけでは足りない

**同一TEI Checkoutを丸ごとHarnessへ公開してはならない**。固定TEI commitには`skills/yi-tei-modeling/SKILL.md`が元から含まれるため、H2へTEI Repositoryのファイル検索・GitHub Browser等を自由に渡すと、`skill_loaded=false`でもSkill本文や手順例を**閲覧できる可能性**がある。その場合はH2の非露出条件が未確認／汚染であり、PP比較資格を与えない。

[既存TAI実S1 Workflow](../../.github/workflows/tai-tei-s1-real-public-cli.yml)に、**同じTEI Binaryと公開`reference/workspace`をH2/H3それぞれへコピー**し、H2にSkillファイルが存在せず、H3だけ固定Product rootとreferenceが存在する作業用ビューを一時的に作るStepを追加。両方のビューで実TEI CLIの`model catalog`・`inspect`・`validate`を実行し、Source artifact fingerprint、WorldFP、Source Index FP、診断数が先のS1 Ledgerと一致するか検査する。元CheckoutのGoソース・TAIの評価票・独立Oracleはビューに含めない。この準備は**ローカルCIにおけるファイル露出の反証**であり、実HarnessのTool/ネットワーク範囲・OS隔離やSkill Loaderを確認したことではない。

実H2起動時には、①固定BinaryとWorkspaceをParticipantへ渡す位置、②その位置にSkill・評価票・他Session Logが存在しないこと、③GitHub・汎用Web・親ディレクトリの読取等の迂回経路が**実Tool Profileとして制限・観測**されていること、④実CLIのargv/cwd/exit/stdoutと対象Sourceの一致を記録する。H3のみProduct Skill rootと必要referenceを別に提供するが、**ファイルが置かれている＝実ロードではない**。Skill rootからリンクされた追加Product文書の参照閉包／その実Readは別に報告し、欠落を架空の成功にしない。

**再現性の注意**：上のCIビューはRun終了時に破棄する臨時ファイル群で、正式な配布Bundleでも、専用Harness Adapterでも、新しいKernelやSandboxではない。`chmod`とCLIの限定読込だけで実OS/Egressの非漏洩を証明できるわけではない。実H2で隔離状態を観測できない場合は、成功したW0/S1を根拠に`skill_exposed=false`へ補完せず、Unknown/不適格として扱う。

### 22.4 固定Skill候補と最小ファイルビューの実CLI証拠

[実GitHub Actions #42112462908](https://github.com/hat47x/tai-pleroma/actions/runs/42112462908)のProduct-only Jobは**completed/success**。Go 1.26.10/Linuxの同じ固定TEI Binaryを、必要な公開`reference/workspace`だけをコピーした**H2 Skillなし／H3候補ありの一時ファイルビュー**からそれぞれ実起動。両ビューの`model catalog`／`inspect`／`validate`が固定S1 LedgerのSource／World FP／Source Index FP／診断件数と一致し、`h2SkillPresent=false`／`h3CandidateFilesPresent=true`を出力した。StepごとのSuccessと実ログを確認し、**H2/H3外部Harness 4 Sessionの成功には計上しない**。

同Jobは固定TEI Checkout内のProduct Skill root SHA-256 `cf137ae534e655881dfc686d70afbf14138cb21a61885b987c224dd893ea2282`、reference SHA-256 `72f6deb92e8800f0846c8ec6a8ac4e69eed7b637fc3b02868db9fe116dd49497`を出力し、Git Blob pinを確認した。[Product Skill限定Evidence記録](../../evaluations/records/TEI-H3-fixed-product-skill-staged-preflight-2026-11-06.json)に固定し、CIから実原byteに再照合する。TEI Product Owner [#2605への契約不一致報告](https://github.com/hat47x/tei-platform/issues/2605#issuecomment-6670006488)を別途作成。修正案を今回の固定H3 Skill byteに黙って混入させない。

**実H2セッションへ引渡す条件**：参加者は実Binary/公開Workspaceの限定ビューだけを受け取り、別の親Directory・GitHub/Search経由でProduct Skill/採点票へ到達できない実Tool Profileを用いる。H3は同じTool/Source条件に加え、上記固定Skill候補の実Loader Readを必ず別ログで確認。CIの局所`chmod`を実OS隔離／External Egress防止／Skill非露出の本番保証へ読み替えない。

<!-- sk02-h8-path-parity-sibling-observation-20261106 -->
### 22.5 実Harnessでの同一論理パスとH2非露出（CIビューの次の不足）

[Product-only staged CI #42112462908](https://github.com/hat47x/tai-pleroma/actions/runs/42112462908)が成功したのは、同じGo BinaryとSource byteを**二つの異なるCIファイルビュー**で読めたことまで。現在の[Workflow](../../.github/workflows/tai-tei-s1-real-public-cli.yml)は同じJobに `$RUNNER_TEMP/sk02-staged/h2` と `.../h3` を並べる。これは実Harnessの**隔離済み二つのProcess Namespace/Host**ではなく、H2側へ親Directoryの探索権限があれば `../h3/skills/yi-tei-modeling/SKILL.md` が届き得る。H2直下に `SKILL.md` が見つからなかったという局所チェックと、**H2からSkillが実際に閲覧不能**というClaimは別物である。CIでの `chmod -R a-w` は読取り隔離でも外部Network Denyでもない。

**実Sessionの最小配置条件**：各Sessionは別の実Sandbox/コンテナ等、選定Harnessで既に使えるファイル可視性境界を用い、参加者に見える共通の論理位置（例：`/trial/tei` と `/trial/workspace`、同じ `cwd=/trial`）へ**同一digestの実Binary／Workspace**を置く。H3のみ事前PinしたProduct Skill rootとreferenceを既存Loaderに提供する。H2からH3のSkill、採点票、前Sessionログ、元Checkoutへ親Directory・Tool・GitHub/Web経由で到達できないかを、参加者に正答やSkill pathを提示しない**試験者側の実アクセス観測**で確かめる。外部Harnessがファイル読取範囲を実効制限できない場合、Skill非露出は `unknown`、PP比較は保留とする（当該SessionのITT・費用は記録）。

**実引数の差を隠さない**：現行[SK-02 Checker](../../evaluations/tools/check-sk02-pair-eligibility.cjs)は `cli_cwd` と実 `-workspace` 引数の**文字列一致**を比較条件としている。CIビューの `.../h2/workspace` と `.../h3/workspace` の実argvを、そのまま四試行の入力として転用すると、仮にSource Fingerprintが同じでも現行Checkerでは不適格である。したがって**同一見かけパスを個別の隔離された実行環境へマウントする**方式を先に選ぶ。実Harness都合で同一論理パスにできない場合は事前登録の別Groupとして、物理Read・実Binary・Source byte・Tool ProfileとPath同値性の判定規則を**実観測に基づき別途レビュー**し、既存Checkerに異なるpathを偽って記載しない。

**H3側の参照閉包**：今回のStageでコピーするのはrootとreferenceの2ファイルだけ。rootが示す `../../plan/design/...` や `../../docs/getting-started.md` 等の**Package外の相対リンク**は、この2ファイルだけからは解決できない。初回の実験条件ではそのまま「リンク先利用不能／未使用／観測不能」を記録し、追加文書をH3だけに後付けして正答率を改善しない。追加した正式Treatmentは別Group・別byte pinで評価。Required referencesが実Loaderで読めなければH3のDelivered資格を与えない。

**試験時の反例（実Harnessは未実施）**：PV-01＝H2自身のDirectoryだけ不在だが `../h3` 経由でSkillに到達、PV-02＝別pathを同一 `-workspace` と虚偽報告、PV-03＝同じbyteでもH3のLoaderがroot/refを未読込、PV-04＝H3だけ追加Document/Toolまたは他Session Answerへアクセス。これらは既存Trial CardのObservationとSK-02比較資格へ写し、独立のSandbox/Runner/Permission Registryを新設しない。

**到達点（§24更新）**：CIでのProduct-only 2-view readに加え、DSH探索的H2 Tool Request→TEI CLI→Replyは限定観測済み。ただしDSHのread-onlyでは隔離Directory外の読取が可能だった。**現在のBlockingは比較適格H2 Sessionでの実Skill非露出／Tool/OS可視性境界／同条件／実ログ成立**。H3 Loader、4独立Session、独立Expected採点・実費用・Egress否定は未実施／未証明。


---

<!-- tai-scn001-first-activity-value-exit-20261106 -->

<!-- harness-h8-goless-cli-probe-20261106 -->
### 22.6 Productの単一バイナリ実行とBuild環境の資格を分ける

[TEI #2953](https://github.com/hat47x/tei-platform/issues/2953)の実観測では、`go.mod`要求版より古いGoで `go run` を行うと失敗する。これは**SourceからのBuild／`go run`前提**であり、すでにBuildされた固定TEI実行ファイルを使う今回のH2/H3条件を直接否定しない。先行する[TEI #2605](https://github.com/hat47x/tei-platform/issues/2605)のProduct Skill文面にはなお`go run`例があるため、実験用ToolはあらかじめBuild済みの同じBinaryだけを両腕へ提供し、Skillの提案が`go run`へ逸れたら観測Outcomeとして記録する。

**実証済みの範囲**：既存[TAI実S1 Workflow](../../.github/workflows/tai-tei-s1-real-public-cli.yml)の両方の一時ビューで、`env -i PATH=/nonexistent <実TEI Binary> model catalog -workspace <公開Workspace>`を実行し、通常CLIとWorld/Source Index Fingerprint・対象`semantic-data:sales.order`が一致することを検査。実行Commit `6a5c8eddac5ed48c3952ef02ff429508112d6ffb`の[GitHub Actions #42182253212](https://github.com/hat47x/tai-pleroma/actions/runs/42182253212)で**completed/success**、実Jobログの該当コマンドと結果を確認した。同HEADの[SK-02](https://github.com/hat47x/tai-pleroma/actions/runs/42182253192)、[Skill静的](https://github.com/hat47x/tai-pleroma/actions/runs/42182253318)、[tai-reference](https://github.com/hat47x/tai-pleroma/actions/runs/42182253249)も成功。

**Claimの上限**：これはLinux CIで**Go実行コマンドをPATHから解決できない環境変数下**の固定Executable動作を示す。Goがホストから完全にアンインストールされていること、別OS/アーキテクチャへの適合、単一Binaryの全依存の封入、Sandboxの隔離、外部HarnessでのTool呼出し・Skill実Loadを実証したものではない。`go version`が採れないことはPrebuilt Toolの不適格理由にならず、**実Binary byte＋Platform＋実CLI呼出し**で資格化する。一方、Source Buildを要求する別Taskには`go.mod`とToolchainの別Gateを使う。

DSH探索的H2では実Tool Request→実Executable→実Tool Replyは限定観測済み。次は**適格H2で同じ経路と強制された非露出／隔離を再観測**する（§24）。Product-only CI成功とSkill有益性/業務Owner受理を合算しない。

<!-- sk02-tei-md-migration-versioned-groups-20261107 -->
### 22.7 `*.tei.md`全面統一の製品決定を、固定S1/H2/H3の版比較とは分離する（2026-11-07）

**製品方針と実装状態を区別**：TEI Authoringの標準名を`*.tei.md`へ寄せ、`*.tei`を原則段階廃止するのはOwnerが選択した方向。[TEI Draft #3030](https://github.com/hat47x/tei-platform/pull/3030)は形式選択・Source Fidelity・段階移行の計画、[TEI Draft #3031](https://github.com/hat47x/tei-platform/pull/3031)は未接続の`*.tei.md`が存在するとき明示診断`TEI_MD_PARSER_UNBOUND`で止める暫定Guard。**両PRは現時点Draft／未merge**で、後者は新形式をParseできる保証ではない。

**比較対象となる4つの独立した状態（V0〜V3）**：

| 段階 | 製品ビルド／入力 | Source・Resultの期待 | 実証資格 |
| --- | --- | --- | --- |
| V0 歴史的固定S1 | 初回比較固定TEI `50ebf8014340fd1906f6b35cfa30173e0ee2fc6c`＋`semantic/sales/order.tei` | `semantic-data:sales.order`が1件Loaded、実Byte/World/Source Index Pin一致 | 従来形式の限定Product-only実CLI証拠；**このSource/Skill/Taskを四Session途中で移行しない** |
| V1 非互換検知 | 同一旧バイナリ＋同じDSL bytesを`order.tei.md`へRename | 旧Loaderの`*.tei`列挙から漏れ、対象Subjectが0件でも`validate.ok=true`となり得る | **拒否されない非互換は失敗**。一時Fixtureで実挙動を観測し、独立Expectedの「対象1件」を保つ |
| V2 暫定Fail-closed | 新Guardを含む別TEI改訂＋未Parser対応`*.tei.md` | 明示`TEI_MD_PARSER_UNBOUND`／Source pathを報告、意味受理・生成・実行は停止 | 新形式の**安全な不受理**まで。Loader/Markdown/DSL意味解釈の対応済みとは呼ばない |
| V3 将来の実対応 | 明示Frontend/Role/Operator版・Markdown Source/構造範囲をPinした新Reader／Binary | Source実Read、対象Subject・定義・Relation・診断／Source byte位置・依存、独立Expected一致。併存時の同一Subject重複拒否も確認 | **別Trial Group**で初めてSkill比較／実Consumerの受入を実施可能 |

初回四SessionはV0で比較する。V1/V2/V3を同じ`repo_head`・`workspace_tree_digest`・`source_index_fingerprint`・`binary_digest`のまま流用しない。`order.tei`の旧S1 Source pathと`order.tei.md`の新Source pathが異なれば、内容bytesが同じでもSource Identity／引用・Source Index／Bundle／Reader・Skillが参照したVersionを別に記録し、意味が不変かは独立Expectedで評価する。A→B→Aや古いReceiptの再利用も自動資格化しない。Migration後のLegacy Sourceを無条件Deleteしたり新旧両方を同時に有効化したりしない。

**文字列拡張子とMarkdown文法も独立**：新拡張子はTEI用途を表すMarkdownであり、旧裸DSL bytesを改名だけで正式Markdownへ昇格させない。Markdown内のどのCode Fence／Table／BlockがTEI Role/Sourceなのか、OKF frontmatter、Source byte範囲・原表記保持、Parser選択、失敗時のraw Draft保持はTEI #2621/#988と[Draft #3030](https://github.com/hat47x/tei-platform/pull/3030)のOwner契約。H3 SkillがMarkdown形式を知らない場合も旧Skillの試行と新版の試行を混ぜない。

**試験Ownerと非目標**：旧V0→V1の一時負例だけは既存[TAIのProduct-only S1 Workflow](../../.github/workflows/tai-tei-s1-real-public-cli.yml)へ局所追加し、旧Runnerが誤って`ok=true`を成功扱いすることの**回帰特性**として保存する。V2/V3の正式実装・Go単体試験・非互換診断・Source Index/Studio/SHO/OKF対応はTEIの担当計画へ戻す。TAI SK-02 Checker、実際の4 Trial、Task/Expected、Tool/Host/OS権限に移行特例を追加しない。新形式の試行を開始する前にSource/Skill/Binary/実Tool Profile/Expectedを新規事前登録する。

**現在地（2026-11-07再照合）**：V0は固定版Product-only CI成功。V1の単純RenameによるSubject 1→0／validate.ok=trueは[旧版実CLI CI #42239797449](https://github.com/hat47x/tai-pleroma/actions/runs/42239797449)で観測済み。さらに**V1の旧新併存**は[実CLI CI #42256480002](https://github.com/hat47x/tai-pleroma/actions/runs/42256480002)でSourceIndexFP変化・WorldFP不変・検証の診断**件数**不変を観測した（次節§22.8）。V2はTEI [Draft #3031の専用CI #42217379093](https://github.com/hat47x/tei-platform/actions/runs/42217379093)で**未対応Sourceの明示拒否**だけ成功。V3のMarkdown Parser/Loader実読込、旧新意味同等、外部AI Harness H2/H3、Owner意味受理は引き続き**NOT RUN**。Product-only負例やDraft GuardのCIをV3に加算しない。

<!-- harness8-source-index-versus-interpreted-world-20261107 -->
### 22.8 旧 `*.tei` と未対応 `*.tei.md` が併存する際のSource Index／意味実消費の差（実CLI負例）

**新しい実測（旧版の回帰特性）**：[TAI実S1 CI #42256480002](https://github.com/hat47x/tai-pleroma/actions/runs/42256480002)、Job `128024911844`、exact TAI Commit `1ff9fd7f79fcb2a21ba35036c3015a9b1e3d24e4`、実TEI Product `50ebf8014340fd1906f6b35cfa30173e0ee2fc6c`。既存の公開 `semantic/sales/order.tei` の原bytesを固定した単一Source Workspaceと、同じlegacyを保持したまま **`order.tei.md`内の`attribute total type std.money`を`std.text`へ変更**した混在Workspaceを比較した。両方の実`model catalog`・`validate`出力を個別に取得し、終了コード一致・診断数一致を確かめた。

| 独立比較列 | legacy単独→legacy＋`order.tei.md` | 実際に言えること |
| --- | --- | --- |
| `semantic-data:sales.order` | **1件→1件** | 読込済み旧定義の存在は維持。新定義を解釈した証拠ではない |
| `worldFingerprint` | **一致** | 解析済みWorldに新ファイルの意味変更は反映されなかった |
| `sourceIndexFingerprint` | **不一致** | 管理Sourceの追加をSource Indexで観測。ただし**Artifact登録≠Semantic定義の実Parse** |
| `validate`と診断 | **同じok状態・診断3件・同じexit** | 検証結果が同じでも必要な新定義の反映・対象集合完全性は不明 |
| 新形式への単純Rename | **1件→0件**／`renamedValidateOK=true` | 旧Loaderでの未読化。空成功を受入成功へ昇格しない |

**受入規則（新しい判定器は不要）**：Source inventory、ManifestIdentity/Source Root、Source Index Artifact（発見/byte）、**Parserが実消費したSource/Occurrence**、World/Model Revision、必要なSubject/Role/依存集合のCoverage、Owner Accepted Meaningを別列で照合する。Source Index差だけで意味変更を推測しない一方、World FPが一致するから新Sourceを未読込でも完全と扱わない。「新しい管理Fileが有る」と「必要定義が有効」は独立Expectedで別採点。対象Sourceが未読込なら `unbound/partial/unknown` を残し、旧モデルを新ファイルのMeaningと見立てて利用・Build・Artifactへ進めない。完全性を否定するためにSource IndexのArtifact列だけを利用しない。

**移行段階への帰属**：TEI [#3030 TM-03/14](https://github.com/hat47x/tei-platform/pull/3030)で実Parser対応・旧新衝突をOwner検収し、[Draft #3031](https://github.com/hat47x/tei-platform/pull/3031)は未接続`*.tei.md`の**明示拒否**だけを実証済みとする。旧固定Binaryの併存例を、#3031のGuardに誤用しない。原文・Role・Parse範囲の確認後でなければ失効範囲/再受理の最適化はしない（#2621/#2582/#2514）。**初回H2/H3の4 Session、固定Skill・Task・Sourceの版は変更しない**。新形式の実Skill評価は別Group。

**Fixtureの形式上限**：今回の`order.tei.md`は旧DSL原bytesを単純に改名／一属性だけ改稿した**未対応ファイル**であり、MarkdownのFenceやRoleを持つ正式な`*.tei.md`著者入力を模したものではない。これは`*.tei.md`の内容が実Semanticへ反映されたかを検査する以前の、**実LoaderによるSource選択漏れ**の反証である。将来の合法Markdown/Roleを伴うReader受入は別PoC／独立Expected。

**今回の範囲**：実Go CLIと一時公開FixtureのSource/Index/World/diagnostics比較を観測。新Readerの受理、Markdown Source Span、業務意味Owner判断、実Provider/Build Consumer、外部AI Harness H2/H3、Skill実Load/Costは**NOT RUN**。失敗した先行CI `#42256065696` は独立最小Workspaceのvalidateが必ず`ok=true`という仮定の誤りを含むため合格証拠にせず、修正後の同条件比較だけを参照する。

<!-- harness8-one-factor-unparsed-source-byte-mutation-20261107 -->
### 22.9 Sourceパス追加と同一パスの原byte変更を分け、解析済みMeaningとの束縛を検査（実CLI）

[TAI実S1 CI #42297500012](https://github.com/hat47x/tai-pleroma/actions/runs/42297500012)（exact HEAD `f968dd55b2c8344e38e91407c5797d60c042ba8b`、Job `128166440777`、固定TEI `50ebf8014340fd1906f6b35cfa30173e0ee2fc6c`）で、§22.8の「管理File**追加**でIndexFPが変わる」試験を、一因子の「**同じFile path、変更するのは未解析`order.tei.md`の内容byteだけ**」へ補完した。

比較した2つの一時Workspaceは、Manifestの原byte、旧`order.tei`原byte、両方のSource path名が一致し、`order.tei.md`内の`attribute total type std.money` → `std.text`だけ異なる。どちらも旧固定バイナリで`model catalog`を実行した。実ログは`samePathUnparsedBytesChangeIndex=true`、`samePathUnparsedBytesKeepWorld=true`、旧`semantic-data:sales.order`が両方1件。元の単純Renameは対象0件／`validate.ok=true`、旧新併存は診断件数3件・WorldFP不変・IndexFP変化の別負例として維持。

**今回、反例で分離できた3つの命題**：
1. `Source path追加→IndexFP差`：管理ファイルの有無をIndexが識別する。
2. `同じSource pathの原byte変更→IndexFP差`：未解析であっても管理Fileのbyte変化をIndexが識別する。
3. `同じSource pathの原byte変更→WorldFP同値`：同じ管理Sourceがあっても、現行Parserがその内容を実消費したとは限らない。

**受入への適用**：SourceIndexの差を「新内容の意味採用済み」と呼ばず、WorldFP一致を「新Sourceは実際に解析・無影響と検証済み」と呼ばない。独立Expectedで必要なSource occurrence／Role／属性型・依存集合を指定し、Inventory→実Reader消費→World→Owner Meaning→実Build消費を段階別に確認する。逆に、選択外で必要依存のない文書のbyte変更を理由にすべてのClaimを無条件失効させるのも避ける。**必要依存集合の完全性が実証できない間は「影響なし」も「一律再受理」も自動判定しない**（TEI [#3030 TM-03/14、AU-07](https://github.com/hat47x/tei-platform/pull/3030)、[#2514](https://github.com/hat47x/tei-platform/issues/2514)、[#2600](https://github.com/hat47x/tei-platform/issues/2600)）。

別の横断論点である[TAI #271 SC-21](https://github.com/hat47x/tai-pleroma/issues/271)（実行Profile変更時の現在Capability再資格化）はこれらのSource証拠とは独立。仮に同じBinary/Index/Worldの履歴が維持されても、次のHarness Sessionで同じTool・現在のGrantが利用可能とは推論しない。最初のH2-01実Sessionでは実Tool Request→Process→Tool Reply受領、Profile/許可範囲を、その時点で別観測する。これは初回Trialの条件を増やすものではなく既存Required evidenceの確認である。

**状態・限界**：旧版のProduct-only Go CLI／公開一時Workspaceで3命題を実測。今回の`order.tei.md`は旧DSLを移した**未対応形式**であり、正式Markdown Frontend/Role/Source spanの成功ではない。[TEI Draft #3031](https://github.com/hat47x/tei-platform/pull/3031)の未対応Parser明示拒否は別ビルドのCI、採用済みmainではない。外部Harness H2/H3四Session、H3 Skill実ロード、Markdown Parser、意味Owner受理、Provider Effectは**NOT RUN**。

## 23. 2026-11-06：Tool/Skillの成立と「活動を継続できる価値」を別に実証する（SCN-001／計画）

### 23.1 二種類の価値を混同しない

本RunbookのW0/S1→H2/H3は、**公開TEIの一要素を実際に調査できるか**、Product Skillによって正答・不明点の保持・費用がどう変わるかを判別する**能力利用の試験**である。これが合格しても、TAI Pleroma固有の「中断後も目的・根拠・未決・成果を取り戻し、別の必要能力へつなぐ」**活動継続の価値**は未実証である。逆に、活動継続の試行をH2/H3の最初の実Tool観測のBlocking条件に追加しない。

活動価値のOwnerは[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)（根拠・現在資格・Handoff）と[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)（価値・必要性の比較）。本Runbookは**引渡し先と独立した最小比較の入口**だけを固定する。SCN-001のSource・成果・判定は既存[Scenario](../../scenarios/SCN-001-shared-space-guidance.md)、Product意味・認可・文書保存/公開・委任は各Ownerが正本。TAI用の中央Activity DB、共通Host、判断Engine、承認者Registryを作らない。

### 23.2 既存SCN-001の一つのUser Jobで比較する

**目的を固定**：架空の案内の「予約不要」と「会議室は要予約」の相違を、O-01〜O-05の原文・出典・時点に基づき説明し、H-01〜03を未採用の候補として残したまま、案内文Draft D-04を作る。中断後にO-06を受領し、過去の記録を消さず、差分・必要な再確認・現在利用可能なDraftを提示する。管理者の正式承認、施設への公開、実予約、外部DB書込みは**試験対象外**。

| 比較構成 | 同じ利用目的に必要な最小手順 | TAIの価値として数えないもの |
| --- | --- | --- |
| **B0：既存手段** | Markdown／ファイル・手動索引・外部Harnessで原典／仮説／未決／D-04／中断点を保存し、O-06後に再照合 | 手作業やHarness自身ですでに実現する能力 |
| **B1：Product単独** | 必要な範囲だけ既存MMI/SHO・SUI・SEI等の公開・利用可能な入口を利用し、それぞれのSource/Receiptを保持。未実装のProduct機能は「不可／未確認」とする | Product自身の意味解釈、文書Read/Save、決定Methodの効果 |
| **B2：TAI横断** | **同じTask/許可入力**から必要なProductの実在能力だけ選択し、中断時の既存参照と未完了義務を許可Projectionで引継ぎ、O-06時の再確認先を提示 | TAIがProductのOwner受理・現在Grant・公開許可・実Effectを代理したとする主張 |

B0/B1/B2は[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)の価値比較に準拠し、[#271](https://github.com/hat47x/tai-pleroma/issues/271)の**J0全面再確認／J1選択的／J2無検査再利用**とは別軸である。最初から全五基盤を起動する必要はない。B1で一製品だけで十分なら、その結果を正例として採用する。B2だけ追加のTool・Source・権限を許す比較や、未提供Product機能の推測補完は**不適格**。

### 23.3 独立Expectedと「役に立つ再開」の判定

同じ合成Source版・入力可視性・Audience/Grant・時点で、比較開始前に**参加者から分離したExpected**を固定する。評価票は新Schemaにせず、既存SCN-001／#271／VA-X/VA-Eに置く。

1. **理解の保存**：O-02/O-03を現行規程と断定せず、矛盾／例外／旧版の候補を識別し、O-05の「確認した範囲に見当たらない」を権限者の不存在へ昇格しない。
2. **中断と再開**：Source原文・位置・版、H-01〜03の採否未決、D-04のDraft/非公開、完了／未完了のProduct/Consumer責務を参照可能な状態で再構成する。LLMの会話記憶や「完了しました」だけを証拠にしない。
3. **変化時の現在資格**：O-06でA→B→Aの同文面へ戻っても旧判断の現在有効性を復活させない。変更を受けたClaim・Source/Parser・Grant・開示だけ再確認を提案し、依存不明を無影響としない。
4. **成果物と利用権限**：D-04が実ファイルとして保存・再読取できたかを文面生成と区別し、Owner未承認なら公開しない。ProductからのACK、Body実受領、最終Consumer読取を必要な場合だけ別観測とする。
5. **作業負担と安全**：根拠復元の欠落数／誤った現在Claim／不要な再取得、Tool回数、Token・経過時間・人手修正、実際の書込み／外部送出の可視範囲を別欄で比較。機密・現在Grantは実Host/Source Ownerで確認し、TAIの自己申告でPASSにしない。

**反証の出口**：B0またはB1で同等の安全性・根拠・再開をより少ない負担で達成すれば、当該用途へのTAI横断Skillは**任意／不要**と判定できる。B2が有利でも、出所欠落、Unknownの消去、権限拡大、未観測の保存・送出があれば合格にしない。これはTAIという製品の存否の判断ではなく、このUser Jobで追加する構成の必要性の判断である。

### 23.4 進める順と実証の現在地

1. **先行P0の出口を具体化**：#168/SK-02では外部DSHの探索H2実Tool Request→実CLI argv/exit/stdoutは限定観測された。次は**実隔離／H2 Skill非露出／同一Tool・Task・Sourceを確認した比較適格H2一Session**、次にH3実Loader、その後固定4 SessionのITT/PP・独立Expected/費用採点。ここへSCN-001の新Toolを混入させない。
2. **並行準備**：SCN-001の既存O-01〜06・D-04・Reference実装と必要Product CLI/Readerの現物を#271/#422の担当で棚卸し、できること／未実装／Owner未受理を分ける。公開合成資料のみ使う。独立ExpectedをTrial開始前に封印する。
3. **後続の最小活動試行**：B0→B1→B2を同じTaskで別Session/明示したConsumer Scopeとして実施し、最初は**一度の中断→O-06→Draft再開**を比較する。2 Harness切替、実EKI業務Effect、SHO Publish、全Product構成はこの試行の必須条件ではない。必要性を示す反例が得られたときだけ追加する。
4. **資格更新**：SourceやHarness、Skill、Product Reader、Grantが変われば、新Attemptと現在用途に対する適用だけ再照合し、履歴の正しいObservationを保存する。比較の成果はProduct側の受理/修正Ownerへ戻し、TAIを第二の正本にしない。

**状態（2026-11-06）**：SCN-001は架空Sourceの参照工程・評価を持つが、ここで提案したB0/B1/B2の実独立Session比較、外部HarnessにまたがるActivity再開、現在Grant/非送出の実強制、Owner価値受入は**NOT RUN**。固定TEI CLIのProduct-only S1とH2/H3準備CIをこれらへ加算しない。

---

<!-- tai-sk02-dsh-external-h2-real-tool-noneligible-20261107 -->
## 24. 2026-11-07：DSH外部Harness実Tool到達とH2比較資格を分ける

### 24.1 実測証拠を既存Runbookへ取り込む

[TEI #2509／merged PR #3113](https://github.com/hat47x/tei-platform/pull/3113)に、外部AI HarnessであるDSH 0.2.2-rc.1（Windows、headless、read-only、OpenRouter経由DeepSeek）の実行記録が追加された。[Product側Evidence原本](https://github.com/hat47x/tei-platform/blob/docs/dsh-h2-readonly-evidence-20261107/plan/evidence/DSH_H2_TOOL_ONLY_READ_ONLY_2026-11-07/README.md)を参照し、TAIへTool原文・Model思考・Credentialを複写しない。

- **実Tool transportの限定成立**：固定TEI commit 50ebf8014340fd1906f6b35cfa30173e0ee2fc6c、同じ公開sales.orderと、参加者用固定Task原byteSHA-256 38a0b238018e050f2116f10f1ca2cb3a54319c2743e2fb9bbe128d4be96a84cf。h2-08のSessionはcompletedで、Tool call 56件／受領Tool result 55件、うちTEI実行物の起動32件。commands／version／catalog／inspect／source-index／validateの実結果が残る。Workspaceのコピーと固定worktreeでWorld/SourceIndex fingerprint一致。最終回答は存在するが独立Expectedによる正答採点は**未実施**。
- **9試行の別分母**：[構造化記録](https://github.com/hat47x/tei-platform/blob/docs/dsh-h2-readonly-evidence-20261107/plan/evidence/DSH_H2_TOOL_ONLY_READ_ONLY_2026-11-07/attempts-summary.json)には、Participant Task完了1、短い接続確認Task完了2、MALFORMED_RESPONSE停止5、INVALID_CONFIG停止1がある。複数Tool呼出しを一つの不正なJSONへ連結して返す問題は、maxParallelToolCalls:1でも防げなかった。最初の試行は隔離用cwdでなかった。これらを成功した4Session Trialに遡及編入しない。
- **比較適格性の未成立**：read-only設定のまま作業Directory外の固定TEI worktreeを実Readできたため、参加者の作業DirだけへSource/Skill/Reviewer Expectedを隔離する§20の条件を実証していない。「Skillを配置しなかった」だけでは親Path・他Tool・GitHub/Web経由の非露出を証明できない。session-log-deepseekをoffにした設定だけでは実Egress不在を証明しない。Windows workspace-write Sandboxの準備はWin32 5で失敗。
- **固定Tool Profileとの差**：DSHの実ログには`tei source-index`の起動がある。しかし[既存SK-02 Checker](../../evaluations/tools/check-sk02-pair-eligibility.cjs)の`readOnlyCommandFamily`は`version`／`commands`／`model catalog`／`inspect`／`trace`／`validate`だけを初回許可群とし、**`source-index`を`outside-initial-readonly-profile`に分類**する。実Toolが読取専用だったとしても、選択外Commandを使った探索Attemptを比較適格H2へ後付け編入しない。`pwsh/read/grep`が限定Directory外を読む可能性も、実Toolの公開面／FS拒否点として別観測する。
- **実証の上限**：DSH usage/token数はDSH自己集計であり実請求費用・H3効果・TAI Activity価値ではない。Tool結果ファイルと9試行の要約はPRにあるが、生DSH JSONL全体はコミットされておらず、原Logの独立再構成は別。Sourceだけで回答を採点したと宣言しない。

| Claim | 現在の到達と上限 |
| --- | --- |
| Product-only S1 | 既存CIで公開固定CLI/Sourceの限定PASS |
| **実外部Harness H2 Tool呼出し** | **限定成立**。同一Sessionで実argv・Tool reply・回答が観測された |
| **H2の固定4Session比較適格性** | **未成立／未確認**。実作業Dir隔離、Skill非露出、同条件、独立Expected、実Audience/Egressが未実証 |
| H3実Skill Load／四Session比較 | **NOT RUN**。Skillの増分価値、Owner受理、TAI Activity OutcomeもNOT RUN |

### 24.2 次の最小ゲートを「H2が起動したか」から「H2比較に適格な1Session」へ更新

1. **先に実隔離**：既存OS/VM/Container/Harnessの強制境界で、固定TEI実行物・公開Workspace・参加者TaskだけをReaderへ到達させる。原Worktree、親Path、H3 Skill、Reviewer-only Expected、過去Session logへのPath/他Tool/Network経由のアクセス拒否を実観測。read-onlyを物理的な読取範囲制限と誤解しない。実強制不能ならTrialはenvironment-ineligibleとし歴史Tool witnessは保持。
2. **別Trial Groupとして事前固定**：固定Task byte/Source/Binary、Harness Version/Model/Tool/permission profile、同一論理cwdとargv、4SlotのH2→H3→H3→H2割付R、実Deliver D、独立Expected保管・停止条件・費用/失敗分母を起動前に固定。**許可したCLI familyと引数を実Tool側で拘束・観測**し、`source-index`など未選択Commandが必要なら事前に両腕・独立Expectedを改訂した**別Group**とする。使用後にCheckerの許可群やTrial JSONを都合よく変更しない。今回の9探索試行を後から成功4試行へ選抜しない。
3. **MALFORMED_RESPONSEを保持**：Model/AdapterがTool JSONを壊す場合は失敗として記録し、Tool引数修正や未サポートConfigで成功を捏造しない。Model/Adapter修正版は別Pin/Groupで比較。途中の実Tool実行とSession最終結果を分ける。
4. **実送出とGrant**：session-log設定、実Provider/Proxy送出、Source Read scope、実Host/OS拒否を別資格として記録する。否定証拠が無いならegress unknown。未承認の実データや私的な原文を外部Modelに送らない。
5. **実Tool→Consumer評価**：実Request→Process argv/cwd/exit/stdout→Harness ReplyとSource/Warning/Unknownを同一Attemptで照合し、§21のITT全割付とPP適格を分ける。適格化した後にH3で固定Product Skill root＋必要referencesの実Loader Readを比較する。Skillなしで十分なら常時TAI/Skill介在を推奨しない。

**Owner／順序**：TEI #2509／PR #3113は外部DSH実Tool実測、TAI #168／SK-02は比較資格と独立Expected、#232はDisclosure/OS境界、#271はActivityの再資格化、#422はB0/B1/B2価値、#514は後続OKF定義/Run Attestation。新Runner、独立Verifier、Agent Host、正本Registryは追加しない。初回固定TEI H2/H3のTask/Skill bytes/Tool profileは、今回の探索的証拠で自動改訂しない。

<!-- h8-dsh-h2-tool-result-completeness-and-isolation-preflight-20261107 -->
### 24.3 実H2の次の一手：Tool出力の完全性と、隔離された実Profileの証拠を先に揃える

[TEI #2509／PR #3113の保存された実Tool結果](https://github.com/hat47x/tei-platform/tree/375b8a95c9fdd7851e55c8ad49a867a745229c5f/plan/evidence/DSH_H2_TOOL_ONLY_READ_ONLY_2026-11-07)を、ファイル単位で再照合した。これは**外部AI Harnessからの呼出しは成立したが、実結果の全部がTool観測として完全ではない**という独立の負例である。

| Product結果／外部Tool保存ファイル | 実際の保存状態 | Claimの上限 |
| --- | --- | --- |
| `cli-model-catalog.txt` と `cli-model-catalog-pinned-worktree.txt` | **各8,192 bytes**で同じ内容。末尾が`"id":"repair_intake.intake`で途切れ、`JSON.parse`不能 | 先頭に含まれるWorld／Source Index FPの一致は観測可能。ただし**Catalog全要素の一致・全Source列挙完了・末尾の欠落なし**は証明できない。元CLIが欠落させたのか、Tool/記録経路の制限かも原ログ無しでは断定不可 |
| `cli-inspect-sales-order.txt`／`cli-validate-json.txt`／`cli-source-index-sales-order.txt`／`cli-commands.json` | 各ファイルの**先頭のstdout JSON部分は正常にParse可能**。後続`[stderr]`にはPowerShellの`CannotCreateTypeConstrainedLanguage`（`[Console]::OutputEncoding`設定の失敗）がある | **合成されたTool reply全文はJSONではない**。stdout/stderrを分離した上でSource／診断等を照合。Shell初期化に由来するstderrを自動的にTEIの意味診断とは扱わず、かといって失敗を隠さない |
| 56 Tool Call／55 Result | 1件のRequestにResult未記録。最終Sessionはcompleted | Session completed＝**全Tool Result受信完了**ではない。Call ID／Actual argv／Result ID・bytes・digestで対応する範囲だけClaimsを成立させる |

**比較適格H2の運用前検査（既存§19〜21／SK-02票に記録し、新Runner／独立Verifierは作らない）**：

1. **Reviewer側だけで範囲を点検**：参加者に実Secret／独立Expectedのパスを与えず、同じOS／Harness／Toolの**有効Profile**で、許可対象の`tei`実Binary＋公開Sourceへの正例Read、親Checkout・Skill・別Session・Reviewer用情報の非露出を検証する。拒否は実OS／Toolの制限結果で確かめ、単に`cwd`内にSkillが無いという一覧や`read-only`ラベルを証拠にしない。合成canaryのみを使用。実験用の外部Modelへcanaryや拒否対象の実パスをそのまま渡して検証しない。
2. **受領結果をSource/Tool/Replyごとに束縛**：実Command family／実argv／cwd／Binary byte／Result Call ID、stdout byte/digest、stderr byte/digest、Harnessへ渡った文字列と欠落・切詰めの有無を照合する。機械可読JSONは**そのJSON bodyだけ**をParseできることと、当該Tool Replyの全文が同じJSONかを区別。許容サイズを超える場合はCommandとTaskを勝手に変更せず、許可済みの**対象Subject `inspect`／`validate`**などで必要な限定Resultを新Callとして実取得し、Catalog全件完全性は`unknown`のまま残す。
3. **Tool許可を実際に強制**：既存SK-02初回Whitelistの`version/commands/model catalog/inspect/trace/validate`、Workspaceパス／フラグをTool実行前とログで照合する。DSHの探索成功時に使った`source-index`、任意PowerShell／File探索などを遡及的に初回Profileへ許す扱いにしない。Tool Model出力が不正JSONを連結した試行は`MALFORMED_RESPONSE`のまま保持する。
4. **試行資格の2段階**：割付前の実隔離／Profile検査がNGなら**未割付・環境不適格**として4Slotは開始しない。開始後のSkill漏出、Tool越境、欠けたResponse、未知Grant／EgressはそのSlotに残し、ITTには失敗／未知を記録し、PPのSkill効果には算入しない。実験途中にModel/AdapterやSandboxを差し替えるときは新しいGroup／事前固定条件を作る。
5. **Modelの実版を過大認定しない**：今回の`~deepseek/deepseek-flash-latest`はDSHの指定モデル識別子。表記が同じでもProviderが実Weights/Revisionを同じものとして返したかは今回のEvidenceでは未確認。モデル別名／経路／有効設定と、実解決されたモデル版／Provider応答metadataを別欄に保持し、取得不能なら`unknown`。全4試行のモデル同一性を自己申告Aliasだけで確定しない。

**Ownerと上限**：DSH `pwsh` 経路でのTool Result分離／8KiB中断・Windows ConstrainedLanguageの扱いは[TEI #2509](https://github.com/hat47x/tei-platform/issues/2509)へ、OS／Filesystem／Networkの実拒否は[TEI #2515](https://github.com/hat47x/tei-platform/issues/2515)・[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)へ、四SessionのR/D・資格と独立採点は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)／[TEI #2018](https://github.com/hat47x/tei-platform/issues/2018)へ帰属。PowerShellの言語保護を弱めることを解決策として前提にせず、実際に使うHarness/Tool Profileの可用性・安全性を別検証する。**ここで実Toolを再実行したわけではなく、保存ファイルを再検査した結果と次の試験契約**。H2/H3比較適格0/4、H3 Loaded 0、Owner意味受理／実送出観測NOT RUNの状態を変えない。

<!-- h8-h6e1-h6e2-real-canary-read-and-session-log-20261107 -->
### 24.4 DSH H6-E1/H6-E2実測をH2入場前の拒否試験へ結ぶ（2026-11-07）

**新しい実証拠（比較Trialとは別）**：[TEI PR #3173](https://github.com/hat47x/tei-platform/pull/3173)／[H6-E1実記録](https://github.com/hat47x/tei-platform/blob/b8f12dd0326722c3afcdf20bc0e1554dc54f29b1/plan/evidence/DSH_H6E1_READ_BOUNDARY_2026-11-07/README.md)では、DSH 0.2.2-rc.1の`headless / read-only / approval-policy never`を使い、Mockが`read`を順に強制。合成Projection、Raw、`raw/.env`、cwd外の合成Peerを**2回とも全4件実Readでき、拒否0件**。そのcanaryはMock Endpointに到達したモデル入力だけでなく`dsh_session_log`にも現れた。これは**現状のDSH read-onlyを許可されたRead範囲のOS/Tool強制と見なせない直接的な負例**であり、実Secretや外部Providerは使っていない。別ユーザーACL・VM/mount/Networkでの**拒否成立**はNOT RUN。

**Session Logの別経路**：TEI mainへ統合済みの[#3153](https://github.com/hat47x/tei-platform/pull/3153)／[#3161](https://github.com/hat47x/tei-platform/pull/3161)によるローカルMock観測では、`session-log-deepseek`が**出荷既定で有効**、Tool結果は通常の`tool_result`に加えSession Logの`data.message`／`data.meta`にも載る。明示`enabled:false`では同fieldが消えたが、同Sessionで`true`に戻すと未送信Eventを再送し、503やstream切断では水位が進まず後続要求で再送される。**モデル入力、Session Log、他のEgress経路は別**。ここで実Providerへの送出・全Socket/Telemetry/MCP経路の非送出は未観測であり、設定`off`やRequest Body内にfieldが無いことだけで「外向き送出ゼロ」とは認定しない。

**SK-02初回の入口への具体的な適用（既存Trial Cardを使用）**：

| 関門 | 正例／反例を事前に観測 | 未達時の扱い |
| --- | --- | --- |
| G0 実可視性 | 同じ実OS identity・Profileで許可された`tei` binary／Public Workspace／Taskのreadが成功し、別Principalで保持した合成Raw・Skill root/references・Reviewer Expected相当・他Sessionと親Checkoutが、直接path／cwd外／他Tool経由で実拒否される | **拒否が実証できなければ未割付 environment-ineligible**。H6-E1の拒否0件を「Skillを置かないから安全」へ読み替えない |
| G1 送出・残留 | Effective Config、Provider経路、`dsh_session_log`設定／水位、実観測したNetwork/Tool出口を分離し、H2/H3のAudienceと許可データに一致させる。初回は公開Sourceのみを投入し、Holdout/機密canaryの原文を実Modelへ与えない | 未観測出口を`no egress`とは記録しない。Mock到達は**Mock限定の送出観測**で、実Provider/OS拒否資格ではない |
| G2 Tool/Result | 両腕同一`version/commands/model catalog/inspect/trace/validate` Tool Profile、実argv／cwd／Binary／Source、stdout・stderr・Tool replyの完全性を照合（§24.3） | `source-index`越境、8KiB Catalog断片／混合stderr／未Resultは別列で失敗またはunknown。Trial開始後はITTに保持 |

**採否順**：G0/G1の**実環境としての事前検査**とG2の許可Tool受領経路が整ってから、H2→H3→H3→H2を**新しい事前登録4Slot**で開始する。開始後に露出・出力欠損・Model JSON不正が生じても、そのSlotをH3に付け替えず、ITTへ保持しPPを不適格にする。DSHのH6-E1/E2実測は既存9探索Attemptと**別母数**で、初回H2/H3試行数に算入しない。

**担当**：実読取否定・実Network境界は[TEI #2515](https://github.com/hat47x/tei-platform/issues/2515)／[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)。DSH ToolとMock Wireは[TEI #2509](https://github.com/hat47x/tei-platform/issues/2509)。Harness比較と独立採点は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)、現在資格／Model Profile driftは[#271](https://github.com/hat47x/tai-pleroma/issues/271)。P0で新しいHost／共通Permission Registry／Runnerを実装しない。**ここで新規DSH試行を行ったわけではなく、既存の実H6-E1/E2を初回SK-02受入へ反映した**。比較適格H2/H3は0/4、H3実Load／Owner受理はNOT RUN。
