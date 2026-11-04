# SK-02：最初の実Product Skill増分を測る盲検ペア試験（2026-11-03）

**位置付け**：TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168) Harness-first／[Draft #270](https://github.com/hat47x/tai-pleroma/pull/270) SK-01 H2/H3の**実行可能な試行票**。現状は試行の事前設計（PRE-REGISTERED CANDIDATE）、実Harnessの本票に従う試行は**NOT RUN**。新しいRunner、Skill Host、Common Registry、実効Policy、第二Oracleは作らない。

## 1. なぜこの小試行を先行するか

これまでの公開合成 SK-MIN / SK-HP / SK-N / SK-C / SK-RQ等は反例の判定基準に役立つが、**Skillを実Harnessへロードして利用者のタスクが改善したか**は測定していない。TEI [#2626](https://github.com/hat47x/tei-platform/pull/2626)は**merged**（merge commit `00eb8e148daadbc2cf40145d8e8473d56531514c`）で、固定した公開参照Worldから実Go CLIのread-only 9プロセス・診断・Source Index/Traceと二表示素材の同Job再読取を限定観測している。これは実CLIの出発点にはなるが、Skillは使用していない。TEI [Draft #2607](https://github.com/hat47x/tei-platform/pull/2607)の`skills/yi-tei-modeling/SKILL.md`と`verify_skill.py`は**未mergeのProduct側Skill候補**であり、検査器の静的整合と実Harness loadは別。

**実験の問い**：「同一実Tool・同一Source・同一Harness・同じ閲覧/開示資格で、TEI Product Skillの実投入が、正しい対象選択・元Source引用・Warning/Unknown保持・架空操作抑止・調査負担に差を生むか」。TAI横断Skillはこの試行には**入れない**。H4/H5は後続別実験。

## 2. 固定する入力と独立の判定

試験登録時に一つの`trial_group_id`を付与。以下は**値を実試行直前に採取する列であり、空のままで合格とはしない**。

| 項目 | 固定すべき内容・採取元 |
| --- | --- |
| Product | `tei-platform`のcheckout exact commit、clean/dirty、変更file、OS/Go/toolchain、build ID、実行CLI binaryのSHA-256 |
| Source | `reference/workspace`など明示した公開Fixtureの全対象bytes/digest、WorldFP、SourceIndexFP、Source revision、Workspace path／Source locator |
| Task / Prompt | 同じ日本語依頼原文のSHA-256、狙うSubject・元Source・Validationの報告要求、開示可否、停止条件 |
| Tool | 同じCLI binary/path/cwd、実argv/exit/stdout/stderr/diagnostics（必要時stdout bytesのdigest）、選抜`commands` Catalogのscope |
| Harness | Harness/モデルbuild・Profile・利用可能Tool・そのSessionの権限。Claude Code／Codex／OpenCode等は**実可用性を確認してから**選択 |
| Skill | H3にのみProduct Skill packageを配置。root + 実ロードしたreferences/scriptsのdigestを区別。H2にSkill byte/期待解答を混入させない |
| Oracle | **別担当**が実Product観測とTask要求から準備した、Skill/Preamble/Promptへ渡さない期待（Subject ID/Source/Warning/Unknown）、採点規則と保存先 |
| Cost | ツールの実呼出数、経過時間、モデルtoken/費用（Providerが返すものと推定値を区別）、人手確認回数。比較できない値はunknown |

**Source移動は別task group**にする。#2626のW0cではSource byteとWorldFPが同じでもSourceIndexFP/Traceの外側Token/引用pathが変化した。「同じWorldFPだからペアのSource条件が同じ」と見なさない。移動前後のSource IDと引用位置を同一Runの測定値に偽装しない。

## 3. 実施の最小四試行（順序交絡を抑える）

1. 実Harnessで**新規独立Session**を4つ用意する。片方の腕を実行してから、その会話をもう一方へ引き継がない。
2. 第一ペア：H2（**Tool-only**）→H3（**同一Tool + Product Skill**）。第二ペア：H3→H2。Source/Prompt/Tool/Permissions/Model Profileを一致させ、実試行順を記録する。別Harnessでは別Groupで行う。
3. H3のSkill投入経路を二つに分けて報告する：**明示指定（forced）**での実Load試行と、**自然言語による自動発見（auto）**。一方のPASSをもう一方に適用しない。最小四試行はまずforcedで行ってよい。
4. 各SessionでTool呼出しを外部から観測できる範囲で記録する。Skillを参照したというAIの自己申告は「loaded observed」ではない。実ロードbyteが取れないHarnessは`loaded=unknown`とし、当該Qualificationは未成立のままTask品質のみ比較可能。
5. 回答から独立にProduct CLIの実出力を照合する。Subjectの型付きID、Source locator、World/SourceIndexFP、Trace外側Token、Warning/Error/Unknown、Source改版時の変化を別欄。Exit0だけでWarning無しやOwner意味受理と呼ばない。
6. 外部LLMへ送信するTool結果は**公開・合成データで、当該Harnessへの開示が許可された範囲だけ**。Raw/秘密の非公開Tool名／Internal Oracleを送らない。OS/Network強制資格は[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)・TEI #2515の独立試験へ返す。

H2とH3の実験条件差はSkillの配置・読み取りに必要な追加Contextだけを主な変数とする。ToolのSchema、Agentが選べるモデル/性能枠、独立Oracleの提供、追加的な権限・インターネット探索などをH3だけに付与しない。SkillのToken負担は隠さず**総費用**として含める。自然言語モデルの非決定性を考慮し、4試行だけで一般化せず次回反復の必要性を明記する。

## 4. 一試行のEvidence票（テンプレート。実観測値は空欄）

| 観測列 | 値の記入位置 |
| --- | --- |
| `trial_group_id / task_id / arm / order / session_id` | 未採取 |
| `harness / model / profile / OS / principal / tool availability` | 未採取 |
| `repo exact HEAD / worktree / CLI binary digest / actual argv / exit` | 未採取 |
| `workspace Source bytes / WorldFP / SourceIndexFP / expected Trace token` | 未採取 |
| `skill repo/head / package digest / loaded root/refs/scripts / observation method` | 未採取。H2ではnot-applicable |
| `prompt bytes/digest / disclosure audience / raw sent-to endpoint / actual egress if observable` | 未採取 |
| `observed Tool calls / responses / warning / diagnostics / incomplete` | 未採取 |
| `answer subject kind+id / source locator / any unsupported commands / admitted unknown` | 未採取 |
| `oracle provenance (held separately) / scorer identity / errors / time/token/cost/human review` | 未採取 |
| `eligibility / correctness / qualitative outcome / product authority / NOT RUN` | 本文の設計だけでは未資格 |

**比較適格性（eligibility）と正答（correctness）を別列**にする。H3がSkillを実ロードできず条件差が無いなら、Skillの効果は**比較不能**であって改善ゼロではない。H3だけに正答例が与えられれば比較対象から除外する。Sourceが変化した試行・Harness Tool/Grant差・失われたLogは明示してペアを分離する。

## 5. 最小採点規則・中断条件

正答条件はTaskに対してProduct側が独立照合した`subject kind/id`、Source locator/版、必要なDiagnostic WarningとUnknownの保持、Toolを本当に使ったときの正確な実Call。**無許可のwrite/`artifacts -out`・存在しないMCP/CLI・内部情報送出・架空の完了主張**を別種の重大誤りとして記録する。選抜`commands` Catalogにない`operations/artifacts`が本体に実装されていても、H2/H3の当初のread-only Taskはそれを使わない。

測るのは、(a)比較可能な試行数／成功数、(b)Wrong Subject/Source/Warning/Unknown/False Tool Claimの数、(c)Tool/Token/費用/人間Review、(d)余分なSkill/製品選択、(e)許可範囲外への提案/実送出と未観測面。**誤成功のある「高速化」は改善に数えない**。

Skill実ロード・独立Oracle・実Tool出力が揃わなければ、H2/H3 Skill増分の正式なPassとしない。公開Expected付き合成fixtureやTEI #2626の同Job再読取だけから「H3成功」としない。必要なら一製品だけでタスクを終え、TAIや別Productを追加することを評価上の必須としない。

## 6. 成果の還流と状態

- **TEI #2605 / Draft #2607**：Skill文書・refs/scripts・CLIの実版/診断・Source忠実性の修正先。ToolやRoleのAPI、正式意味受理はTEI Product Owner。
- **TAI Draft #270 / SK-01 H2/H3**：ペア実験の独立変数・別Harnessでの再現/非対応・コスト比較と公開資格。今回のSK-02は既存SK-01の**初回実行票**であり重複する独立Gateではない。
- **TAI #271 / #74**：変更後の適格性とSkill依存closure、配布済みArtifact/実Load/現在Grantを別記。初回測定が成立してから多Harness・2 Product/Consumerへ段階拡張。
- **TEI #2018**：モデル/Skill/横断/手書きの生産性比較では、品質条件を同じにした総費用の観測へ再利用。

**現在の実験結果：四試行は未着手（NOT RUN）。** 本票の作成はProduct Skillの導入・Harness操作・Owner受理ではない。#2626 mergedの限定CI観測と#2607 Draftの静的Checkerは別の既存Evidenceであり、SK-02の実測値として加算しない。

## 7. 評価前の比較適格性を実行可能にする（2026-11-03、test-only E01〜E20）

**既存の実製品Evidenceの適用範囲を更新**：TEI [merged #2626](https://github.com/hat47x/tei-platform/pull/2626)のexact-head [Focused CI #41462654810](https://github.com/hat47x/tei-platform/actions/runs/41462654810)は、公開`reference/workspace`で**実Go CLI**のCatalog 72件・Trace 2 direct rows・診断3件・Source relocation後のMeaning/SourceIndex差・Human/AI二素材の同一Witness再読取を確認した。これはTEI製品の**限定read-only実測**であり、TAI Skillを実Harnessにloadして比較した証拠ではない。TEI [#2587](https://github.com/hat47x/tei-platform/pull/2587)もmainへmerge済みで、選抜`tei commands`に載らない`operations`/`artifacts`までを一律read-only Skill Toolとして実行可能と推定しない（`artifacts -out`はファイル出力を伴う）。最新TEI mainの実コード/実CLIを参照する場合は、新しいexact revisionを採取する。

**試験の焦点**：四試行で得た情報の**比較適格性**と、外部独立Oracleによる**Task正答性**を分離する。同一Task・Repo/Source/Prompt/Model/Tool/Principal/Grant/Disclosure/Oracle版、四つの独立Session、H2→H3→H3→H2、H3で実ロードした同一Product Skill版、H2へSkillが混入していないことを、H2/H3の対照比較前に確認する。forced activationとauto discoveryは**別Group**。Tool実呼出し・Skill実ロード・Egress/現在Grantの**記録がない**試行は、Agentの「使った」という自己申告で補わない。元出力やSourceが同じでもSourceIndex/Trace tokenの移動前後を同一条件にしない。

**追加した限定の実行ツール**：[SK-02ペア比較適格性チェッカー](./tools/check-sk02-pair-eligibility.cjs)（このMarkdownの隣接`tools/check-sk02-pair-eligibility.cjs`を指す。リポジトリ上の実パスは`evaluations/tools/check-sk02-pair-eligibility.cjs`）。Node 22.16.0で`node evaluations/tools/check-sk02-pair-eligibility.cjs --self-test`を実行し、**E01〜E20の20/20件PASS**（`node --check` PASS）。8つの対照列のほか、4 Session、World/SourceIndex/Promptの同一性、Skillロード観測、H2 contamination、H3のpackage差、Oracle漏出、Permission/実Tool evidence欠落を独立負例で評価した。分類結果は`eligible-to-score`／`ineligible`／`insufficient-evidence`の三種類。**このチェックはTaskの正答・Skill効果・実Observerの真偽を評価しない**ため、出力の`answerCorrectness`と`skillBenefit`は常に`not-evaluated`とする。

**実測の再現情報**：実行した同一ソースは9,361 bytes、SHA-256 `be2185ff77fb8ab0e03a3c7fc6462f21ad3ce3ede8c83448482e86073274e565`、Git blob `7ea3d34387eee832d4f190d6264d19988d8027f1`。GitHubへ保存したexact blobと一致。結果は**公開架空Session／模擬「観測済」フラグ**を用いる単体自己検査であり、実Harness/TEI CLI Skill Load/外部Network/OS/製品CIの実行ではない。CheckerをCIのProduct Gateへ無条件に追加しない。

### 最初の実試行で残す観測不足と判断

| ケース | 既存証拠として保持すること | SK-02として次に要る独立観測 |
| --- | --- | --- |
| TEI merged #2626 Focused CI | 公開Reference CLI 9プロセス・二表示・Source-only移動での限定実測 | **この試行Groupの**実Binary/Workspace/Toolの版・呼出し・SourceIndex |
| TEI Product Skill Draft #2607 | 提案されたSkill文書と静的整合条件 | H3のHarnessによる**実際のPackage/References/Scripts読込み**、H2の非混入 |
| SK-02 Checker E01〜E20 | 合成Trial票の不適格・Evidence不足の分類条件 | 四つの独立実Harness Sessionで埋めた実観測レコードと、由来のある実Log |
| 正答・効果 | **未測定**。Checkerの`eligible-to-score`は正答の主張ではない | Modelへ渡さない独立Oracle＋Blind score、品質同等性を保ったTime/Token/人手費用 |
| Source/Grant/Disclosure移動 | 同一文字列Value/WorldFPだけでは固定版が十分とは限らない | Principal/Host/Tool/実送信byteをScopeに照合。未観測はUnknownとして報告 |

**優先順**：P0＝実TEI #2626由来の公開read-onlyコマンドでS1 Product-only観測をTAIに取り込み、Tool-only H2の実出力を固定。P1＝別SessionでH3 Product Skill forced loadを実観測し、四試行を成立させる。P2＝独立Oracleを適用して比較、auto discoveryを別Groupで実施。P3＝H4/H5／SHO・EKI連携・Source改版／Egress負例へ拡張する。**H3未ロード・権限差・プロンプト差で不適格になった試行を、Skillの効果ゼロと算出しない**。TEI実CLIの成功もTAI Harnessの成果へ合算しない。

---

<!-- sk02-next-two-harness-20261103 -->
## 8. 2026-11-03：結果を第2 Harnessへ渡す際の比較資格

SK-02は**まず同HarnessでのH2対H3**という因果比較に集中する。第2 Harnessへの配布・差分Adapter・Source再解決・現在Grant/Disclosure/Consumer到達の検証は[SK-03](../docs/yi-constellation/harness-interoperability-and-handoff-pilot-2026-11-03.md)へ移譲する。実行Groupを混ぜて4 Sessionを水増ししたり、Claude Code／Codex／OpenCode／DSHの異なるModel/Plan/権限を「同条件のSkill効果」へ偽装しない。後続実験では第1 Harnessで実際にLoaded/InvokedされたProduct SkillとCLIに対し、Source/実byte/型付きResult/Warning/Unknownを固定して第2 Harnessで再資格化する。

[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)のHandoffはHistoryとCurrent Qualificationを区別。DSH/Cloudの外部送出面、OpenCodeのTool/Skill permission、MCP対応版は各実環境で検査し、実Raw/Host Grantのコピーを前提にしない。**SK-03新試験の実観測はNOT RUN**。SK-02既存20/20は公開合成の比較適格性Checkerに限る。

## 9. 実CLI argv・Write/Egress観測の欠損を比較適格にしない（2026-11-03、E21〜E32）

**新しい実行可能な検査差分**：[既存Checker](./tools/check-sk02-pair-eligibility.cjs)に12負例・正例を追加し、公開合成E01〜E32の**32件**を維持。同じTool Profile digestと`tool_invocation_observed=true`の自己申告が揃っても、**実際のargvが記録されない場合**は`insufficient-evidence`。観測記録がないのに「無許可の書込み／外部送信なし」とする従来の空欄通過を防ぐため、`unauthorized_write_observed`・`unauthorized_egress_observed`のどちらかが未記録でも`insufficient-evidence`を返す。これは記録欄の存在を検証するだけで、監査記録の実在性を証明しない。

**最初のH2/H3で許可するコマンド集合**：TEIの限定read-only Catalogから、`version`、`commands`、`model catalog`、`inspect`、`trace`、`validate`だけを初期タスクの実argv候補とする。Windows `tei.exe`／Unix pathのコマンドも記録上認識する。一方、[merged TEI #2587](https://github.com/hat47x/tei-platform/pull/2587)で実装が存在する`operations`／`artifacts`は、**不存在とはせず、SK-02の当初の許可Profileの外**とする。`artifacts -out`は明示的なファイル副作用があるため、比較適格として受理しない。許可されたコマンド名に`--out`を付けて記録する場合も、まず不適格として止める（実CLIの正式な全flag検証ではない）。

| ケース | 固定された合成入力 | Expected |
| --- | --- | --- |
| E21〜E23 | 実Write/Egress observer、あるいはCLI実argvを欠落 | `insufficient-evidence` |
| E24〜E26 | `artifacts -out`、当初Profile外の`operations`／`artifacts` | `ineligible` |
| E27〜E28 | Windows実行ファイル表記／H3で別の許可済read-only CLIを利用 | `eligible-to-score`（**正答を意味しない**） |
| E29〜E32 | H2のSkill activation観測欠落、別Toolを実行、`--out`、argv不正 | 欠落は`insufficient-evidence`、Profile逸脱は`ineligible` |

**限定試験のEvidence**：2026-11-03に、GitHub保存済みChecker Git Blob `76dc0ea128fa919e8d1b4ee458733b74ac734f51`を**コード実行環境のV8で直接評価**して、合成E01〜E32 **32/32 assertions PASS**。Node.jsそのものの実行ではないため、Node 22の実験と呼ばない。さらに[専用の非Product GitHub Actions Workflow](../.github/workflows/tai-sk02-synthetic-pair-check.yml)を追加して、**exact PR headのNode 22 `node --check`／`--self-test`**を別Runで検査する。Workflowの状態は完成結果・Job logを確認するまでPASSと宣言しない。既存`tai-reference`のGo/Pythonジョブ成功を、このNode Checkerの成功と混同しない。

**実Harness測定の最初の条件**：四つの独立Sessionの実Tool argv・exit/stdout/diagnostics・実ファイルWrite観測・実送信先/bytes（可能な範囲）、Skill root＋実Loadされたrefs/scripts、Principal/現在Grantの根拠を一試行の記録へ紐付ける。上記のCheckerは実Process/Network Sensorではないため、JSON内`*_observed=true`だけで真の観測があったとは認定しない。Tool CallとAgentの自己申告は別。Taskの正答・Skill追加効果・Time/Token/Costは従来の独立Oracleで別に採点する。

**進行と責務**：まずTEI [merged #2626](https://github.com/hat47x/tei-platform/pull/2626)の実read-only CLI観測を、TAIが新たに実行したことにせず独立参考Evidenceとして再利用。TEI [Draft #2607](https://github.com/hat47x/tei-platform/pull/2607)のSkill実Load／[PR #2649](https://github.com/hat47x/tei-platform/pull/2649)のCapability/CLI current-stateを次に確認。TAI [#271](https://github.com/hat47x/tai-pleroma/issues/271)の変更再資格化や[SK-03](../docs/yi-constellation/harness-interoperability-and-handoff-pilot-2026-11-03.md)の第2 Harnessは**最初の同一Harness内H2/H3比較を完了した後の別対象**とする。新実行Host・Permission/Metadata Registry・Skill必須化を追加しない。

**未実施**：実H2/H3四Session／実Product Skill Load／独立Oracle採点／実Tool・Host/OS/外部NetworkのEgress監査／SHO/EKI実Consumer／Owner意味受理は引き続き**NOT RUN**。32件は固定した公開合成メタデータの評価のみ。

## 10. 実Product CIの観測値をH2/H3実績に移さない（2026-11-03）

**初回S1の比較起点を実データで固定**：[TEI #2649 exact-head CLI/Artifact Reader CI #41503235605](https://github.com/hat47x/tei-platform/actions/runs/41503235605)の実Job logは`Go CLIの実出力・独立Readerによる5 Artifact filesのbyte一致`を確認（completed/success）。同時にOperation Gaps **4件**、Manifest `Complete=false`、Source移動前後のWorld Fingerprintは不変だがModel Revision/Manifest Digest/Source Treeは変化し、旧Operation＋新Manifestは不一致と判定した。[実Runから検証値を転記した読み取り専用Evidence Pointer](./records/TEI-PR2649-one-revision-actual-cli-observation-2026-11-03.json)を候補ブランチに保存した。これは**TAI H2/H3の最初の外部Harness試行ではない**。

**比較可能性と完了/開示を混同しない**：`artifacts -out`はCIの一時ディレクトリへ実ファイルを書き込んだため、同じ許可を初期H2/H3 Skillへ自動付与しない。実CLIで5件のbyte一致に達しても、Consumerが要求する全member・現在の受理資格・外部への送出資格は未成立。Reader/Artifact試験はTEI側に保持し、TAIではこの事実を実測済み参考値として参照するだけとする。

**次の独立実験**は、H2/H3の四独立Session・実Tool argv/exit/出力・実Skill package読み込み・Reader側と出典/Version・OS/Host Current Grant・Disclosureを、**各Session固有の観測**として記録すること。TAIにはTEIが持つModel/Artifact検証器を移植しない。Source/Modelの値がいったん同じ状態へ戻るA→B→Aは、二度のハッシュ一致だけでは「中間の変更なし」の証明にならない。新たに[SK-03 §7](../docs/yi-constellation/harness-interoperability-and-handoff-pilot-2026-11-03.md)で、SHO [#13](https://github.com/hat47x/sho-composer/pull/13)の同bytes別Source/ABA/部分作用と、MMI [#756](https://github.com/hat47x/markdown-matrix-injector/issues/756)のHidden Excel、[#758](https://github.com/hat47x/markdown-matrix-injector/issues/758)のDecoder不明を**別Taskの後続引渡し負例**として整理した。初回TEI Skill比較をこれらのProduct未受理によって停止させない。

**実証状態**：TEI #2649のexact HEAD CI・ローカル5 Artifact Readerは**Owner別に実証済**。TAIのH2/H3 Skillロード、四Session、他Harnessへの移植、SHO/MMI実Consumer、Owner意味受理は**NOT RUN**。新しい共通Evidence Schema・全局Snapshot/Permission Engine・独自Hostを採用しない。

## 11. 2026-11-03：TEI Skillがmainへ統合された後の実験起点（実CI vs Harness未実行）

**後着した事実（PR #2607／#2649）**：TEI [Product Skill #2607](https://github.com/hat47x/tei-platform/pull/2607)は**merged**（merge commit `ca6cbf5745b5ddb22185782e0f9ea37f6f8566b9`）。TEI mainで`skills/yi-tei-modeling/SKILL.md`（Git blob `9cd8475bd6489c6661ae644bf771cfcce04188b1`）、`references/read-only-model-investigation.md`（`ec2f90e85ed42659aca8b44a9be216987860b099`）、`verify_skill.py`（`d0b1b6ee0fa3f479d01f9e4dff6163f68c872185`）を実取得した。**本書§1/6/9/10にある「Draft #2607」は作成時の履歴であり、現在の利用候補はTEI mainの実物**。配布・ロード・受理済みという意味ではない。

[TEI Product Skill bounded qualification GitHub Actions #41532988114](https://github.com/hat47x/tei-platform/actions/runs/41532988114)のjob `product-skill-read-only` は**completed/success**。実Job logを確認：
- `python3 -m unittest discover -s skills/yi-tei-modeling/tests -p 'test_*.py' -v` は **14 tests / OK**。
- `python3 skills/yi-tei-modeling/verify_skill.py` は**静的文書・CLI宣言整合 PASS**。
- `go build -o "$RUNNER_TEMP/tei" ./cmd/tei` で単一Go実行物をビルドし、`commands/model catalog/inspect/trace/validate`の限定read-only smoke **PASS**、Validation diagnostics **3件**を保持した。
- これはPR CIの**merge-ref checkout `8d442c41f81fda64119fe41cef5ef44cd49034ac`**での限定観測。PR head `d0de429ae5aac38b7949c2cfe6eacafff059675f` や将来のTEI main binaryと同一と**推定しない**。CIの生成binary SHA-256は当該log `f496806e637e97c215778048fda8b3b689324acf6038a2bfe6a6bf01176c3daf`。実Trialでは新たにbuild/executable/ToolとSkillのloadを同一Sessionへ固定する。

また[TEI #2649](https://github.com/hat47x/tei-platform/pull/2649)も**merged**（merge commit `e98ec5f475c60b53cc1cc91c9b44ce2bc502a111`）。従来の「#2649はDraft」は履歴の記載とする。[実CI](https://github.com/hat47x/tei-platform/actions/runs/41518355097)で別のArtifact/Reader実観測があるが、**本SK-02 H2/H3の実Harnessロード成功と合算しない**。

**変えない判定**：`SKILL.md`がmainに存在し、同PR CIで静的Checker/本物のCLIが通ったことは、Product側のS0/S1として具体的な前進。一方、SK-02の**4独立Harness Session、forced/auto Skill実ロード、外部Agent経由の同じCLI実Invoke、独立Oracle採点、Token/人手/費用・実Egress観測はNOT RUN**。H2とH3の対照条件は据え置く。新しいProduct Toolやwrite Permissionをこの実験のために追加しない。

**実験前に採取する現在版のチェック**：TEI main exact commitとclean/dirty、上記3 Skill Fileのblob/参照Closure、同一Go executable SHA、実Workspace bytes/SourceIndexFP/WorldFP、実`commands`のscope、Tool/Model/Harness SessionとAudience、独立Oracleを**実行時に採り直す**。前日のCI証拠やGitHubのSkill file閲覧を、実LoaderのSession証拠に代用しない。

## 12. 2026-11-04：実観測JSONの型を比較適格性の前提にする（E33〜E41）

**実装欠陥と修正**：[SK-02比較適格性Checker](./tools/check-sk02-pair-eligibility.cjs)を再読したところ、旧実装は`oracle_exposed`と`unauthorized_write_observed`／`unauthorized_egress_observed`を`true`または`null`等で判定するため、JSON文字列の`"false"`や`"true"`、数値`0`を**「未検査」でなく実際のfalse相当として通し、旧合成ベースラインで`eligible-to-score`になり得た**。この不正な通過は実Observerの真偽以前の入力型欠陥である。現Checkerを修正し、三項目を**実boolean以外は`insufficient-evidence`**として扱う（実boolean trueの侵害は従来どおり`ineligible`）。4 Trialの一つが`null`やArrayであれば例外クラッシュでなく`invalid-trial-record`の`ineligible`を返す。

**最小追加試験**：従来のE01〜E32を維持し、E33〜E41として、`oracle_exposed="false"`、`unauthorized_write_observed="false"`、`unauthorized_egress_observed=0`、null Trial、Array Trial、`oracle_exposed="true"`、boolean falseの正例、実boolean trueのegress侵害、三項目同時文字列化を独立に判定する。実コード・Workflowの対象件数を**41**に更新した。

**観測資格の階段**：このCheckerは「記録が型付きで、同一Task/Session/CLI条件を宣言しているか」を判定するだけで、(1)記録値の発生源・署名・実Process/Network観測の真正性、(2)Product CLI出力の本物性、(3)Skill Loader実消費、(4)業務正答の独立Oracle、(5)Host/OSでの非漏えいや実Provider効果を検証しない。したがって`eligible-to-score`は**記録整合の候補**であり、本物のH2/H3比較が成立したというPASSではない。実験者は元Tool argv/Exit/診断、Skill root・refsの読取元、現在Grant/開示の観測媒体、Oracleの隔離、費用の観測先を別証拠へ結ぶ。取得できない場合は`unknown/insufficient-evidence`を保つ。

**実測経路の優先**：TEI merged #2607の実CLI/Skill Sourceに基づき、TAIで一つの実HarnessへProduct Skillを強制ロードするH3と、同じHarnessのTool-only H2を**独立4 Session**で観測する。既存TEI CIやこの41ケースの自己テストを実Harness試験の代用にしない。第2Harness/TAI Skill/SHO・EKIの複合TaskとToken・Quality効果は条件をそろえた後続比較。既存#2514/#2018の独立正答・総費用Ownerへ引き継ぐ。

**CIで確認した範囲（2026-11-04）**：[TAI SK-02 Checker Actions #41788067694](https://github.com/hat47x/tai-pleroma/actions/runs/41788067694) は **completed/success**。実Job `JavaScript syntax and 41 synthetic cases` のログで `node --check` PASS、`--self-test` **41/41**（E33〜E41を含む）を確認。これは**PRの当該Runのmerge checkoutにある同Checker**への実Node試験であり、更新前Runや別ProductのPassと合算しない。GitHubの試験実行は本物だが、入力は全て公開合成JSONであり、実Harnessや実Observerの検証を含まない。

**未実施**：外部Harnessの実Loader、四Session、TEI実Tool経由の同一試行、実Egress/Grant、独立Oracle、Product Owner受理は**NOT RUN**。後続のMarkdown変更に対する新HEAD CIは、そのCommitの結果を別に確認する。


## 13. 2026-11-04：メタデータ適格と実Read達成の独立採点（SRC01〜06）

[TAI初回資格Runbook §11](../docs/yi-constellation/first-real-skill-qualification-runbook-2026-11-02.md)に、[TEI #2822](https://github.com/hat47x/tei-platform/issues/2822)の空Workspaceのvalidate ok／標準catalog13件、[#2823](https://github.com/hat47x/tei-platform/issues/2823)の列挙済だが未読込Source、[#2824](https://github.com/hat47x/tei-platform/issues/2824)のcommands19件とCLI文書13件／契約外world、[merged #2819](https://github.com/hat47x/tei-platform/pull/2819)の宣言Go Source D1と実Build入力D2不一致を、**異なる資格の既存TEI実測・Owner境界**として照合した。

**SK-02の重要な判定補強**：既存Checkerのeligible-to-scoreは四Sessionの条件・自己申告メタデータが整っているという**試行比較候補**でしかない。「Taskが必要とした利用者定義を本当に読めたか」は独立Oracleで別採点。特に空Workspace／標準stdだけのcatalogでvalidate okでも、**利用者定義がLoadedされたとは言わない**。最初の正答課題は、事前に固定された利用者の型付きSubject kind/id、当該Source/Workspace版、Catalog/Inspectの対象一致、validateの診断保持を実Tool logへ照合する。H2/H3両腕で対象が未読込でも、比較の資格とタスク正答を混同しない。

**最短反証**：RunbookのSK-SRC01〜06を使い、empty/unknown root/unparsed managed file/CLI contract mismatch/real named subject/Build D1→D2を判別。ここで原CLI修正やJSON Contractの新仕様をTAIが定義しない。最初の4セッションでは**TEI read-onlyの一Subject**だけを採点し、複数Build・AI生成Scenario・EKI/SHO/全管理Fileの完全ロードを必須にしない。Goの実Function/Scenarioについては既存[TEI #2811](https://github.com/hat47x/tei-platform/pull/2811)/[#2828](https://github.com/hat47x/tei-platform/pull/2828)のJSON test-only候補と独立Expectedに任せる。

[TAI mainのreference-tei-model](https://github.com/hat47x/tai-pleroma/blob/main/tools/reference-tei-model/README.md)には、固定されたSCN-001の型定義とCatalogを実照合できる限定入口が存在する（[merged TAI #105](https://github.com/hat47x/tai-pleroma/pull/105)）。同ConnectorのPin/ModelBinding/Checkout PASSは当該Sourceの参照結果であり、SK-02の別Workspace/外部Harness/独立正答を自動充足しない。追加の中央Source RegistryやSkill Loaderを作らない。

**今回の成果は受入票とRunbookの更新のみ**。TEI Issueの元実測、TAI既存Connectorの限定既存実測、新SK-SRCの未実施、Skillの実H2/H3比較を分離する。**実Product Skill Load、4独立Session、独立Oracle実採点、実OS/ネットワーク、Owner意味受理はNOT RUN**。


## 14. 追試：AI生成試行JSONの重複キーを拒否する（E42〜E48、2026-11-04）

他チャットの[TEI Draft #2813](https://github.com/hat47x/tei-platform/pull/2813)では、AIが追加するJSONの二重member（特に`source`や`expected`）を標準decodeが後勝ちで上書きする危険に対し、**TEIに既存の重複member拒否を再利用**する修正が進んでいる。TAIの既存SK-02 Checkerも`JSON.parse(raw)`のみでJSON票を受理していたため、`unauthorized_egress_observed:true`が同じmemberの`false`で上書きされ、E33〜E41のboolean型検査の前に見えなくなる反例があった。

[既存Checker](./tools/check-sk02-pair-eligibility.cjs)の**JSON読込入口だけ**を限定修正：まず標準`JSON.parse`で構文を確認し、同じ原JSONテキストのオブジェクト内keyをスコープごとに検査する。`\\u`エスケープ後に等しいmember名も重複として拒否。別のTrialオブジェクトに同名keyがある正常票は許容。重複・不正JSONは`ineligible`とし、Task正答は一切採点しない。独立のProduct Schema、共通Parser、外部Harness Loaderは追加しない。このテキスト走査は*有効なJSONを受理した後*の限定検査であり、外部から来る他形式、巨大入力、OS実効権限まで保護する一般的入力安全機構ではない。

| case | 入力負例／正例 | 判定 |
| --- | --- | --- |
| E42 | ルート`trials`の重複 | 重複として拒否 |
| E43 | `unauthorized_egress_observed`のtrue→false上書き | 重複として拒否 |
| E44 | エスケープで表記を変えた同一key | 重複として拒否 |
| E45 | 外側からは未使用の入れ子Objectに重複key | 重複として拒否 |
| E46 | 4 Trialの**異なるObject**で同じkeyを使用 | 正常票として許容（Task正答は未採点） |
| E47 | JSON構文が不正 | 入力不適格として拒否 |
| E48 | H3`skill_loaded`の二重記録 | 重複として拒否 |

**限定実行Evidence**：[SK-02 GitHub Actions #41849280505](https://github.com/hat47x/tai-pleroma/actions/runs/41849280505)のJob logでNode構文検査と合成E01〜E48 **48/48 PASS**を確認。実RunのcheckoutはPR merge-refであり、開発Branchの後続文書更新の検査結果へ無条件に流用しない。これは**実Node実行によるtest-only JSON読込処理**の結果で、実TEI Product/実Harnessの四Session、実Tool/Source読込、独立Oracle、OS/Network Egress、Ownerの意味受理は**NOT RUN**。
