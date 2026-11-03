# YI Constellation：代表的Harnessの相互運用、最小Adapter、Skill実効性とHandoffの段階実証

2026-11-03。TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)の対応要求を、[Draft #270](https://github.com/hat47x/tai-pleroma/pull/270)のSK-01/SK-02、[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)の再資格化、[TEI #2605](https://github.com/hat47x/tei-platform/issues/2605)のProduct Skillへ接続する**追加実証計画**。本書自体は実Harness接続・製品機能の受理を意味しない（全新試験 NOT RUN）。

## 1. 成熟させる意思決定

**DSHだけを標準のHarnessとしない。** Claude Code、Codex、OpenCode、DeepSeek Harness（DSH）を初期の異質なCLI/Agent群、Gemini CLI、Copilot Agent（IDE/Cloudを別環境として扱う）、Cursor、Clineを次の比較群、Dots・Grok Bot・ChatGPT Work等をCloud/継続型の別群とする。Continue・Aider・Goose等は需要/機能差に応じて追加する。機能の公称有無だけで「対応済み」とはしない。

**重要な訂正**：OpenCodeにDeepSeekモデルを設定した環境と、独立実行物のDeepSeek Harnessは**別Harness**。モデル提供者、Harness実装/版、利用プラン/請求経路、起動Profile、OS権限を別列にする。DSH固有のsdk-minimal/headless/Session Log送出試験は[TEI #2509](https://github.com/hat47x/tei-platform/issues/2509)がOwner。OpenCodeでMCP/Skillsが使えると確認してもDSHでの実可用性や送出制御を保証しない。

Harnessは対話・推論・Tool/Process起動・Agent UXの実装主体。各ProductはSource/Meaning/契約/Version/型付きResult/検証と独立して利用可能なCLI・APIを保持する。MCP/Agent Skill/IDE・Pluginは接続面。TAIは必要なProduct選択、公開範囲に沿った限定Handoffと横断評価だけを担当。**共通Agent Runtime、第二Host/Registry/Authority、Harness互換Clone、Product別の重複Meaning契約は作らない。**

## 2. 対応の単位は「ブランド」ではなく条件付きCapabilityベクトル

Harnessごとの実行環境（Local CLI、IDE Agent、Cloud/Managed、Headlessなど）に対して、以下の**直交する**列を調べる。1つの総合等级/全機能の一括PASSは作らない。

| 観測軸 | 実際に確かめるもの | 混同を避けるもの |
| --- | --- | --- |
| 環境 | 実Harnessの製品・version/build、model/provider、plan、profile、OS/UID、session、起動形態 | 公式文書のfeature記載と実アカウントの可用性 |
| Skill | インストール場所、発見、実ロード、rootとreferences/scriptsの**実消費**版、permission | ファイルをコピーしたこととAgentが読んだこと |
| Tool/Transport | CLI実binary/argv/cwd/exit/stdout/stderr、またはMCP handshake/protocol revision/tool schema/alias/実call、独立APIの実result | MCP server登録、Tool listing、実call、Result到達 |
| Meaning/Context | Source/occurrence、World/SourceIndex、Role/依存Pin、Scope/Grain、Warning/Unknown、Consumer要求 | 出力文字列一致と同じ業務意味／同じSourceの保証 |
| Effective Rights | read locally、外部LLM向けprojection公開、file write、external Effect、再開Grant、OS/network/credential | Skill/Tool説明文とHost/Providerの現在権限 |
| Delivery | 実受信bytes、保存/失効、同Attempt Body/ACK、SHOなどのConsumer実読取 | LLM最終回答、送信要求、送達、適用/業務効果 |
| Cost | 起動・初期設定/配布・修正Adapter、Token/Context load、Tool I/O、Human review、反復回数 | 安いモデル単価だけで総開発費を評価 |

状態は軸ごとに <code>not-investigated / documented-candidate / not-run / observed-pass / observed-fail / unsupported / unknown</code> 等を限定して記録。例えばMCPが非対応でもCLIは使える、Skill非発見でもTool-onlyで成功するなど、**可能な経路を正確に残す**。未調査をunsupportedにも合格にも丸めない。

CLIやMCPのどちらかを**必ず**通すのではなく、実Harnessにとって最も薄い入口を先に選ぶ。ただし同一意味契約と独立Expected/失敗分類への照合は変えない。OpenCodeのv1/v2、MCP protocol revision、Tool名prefixやpermission差は実config/handshakeで記録し、特定版の設定例を他Harnessへ盲目的に流用しない。ACP等のEditor↔Agent通信用Protocolを、ProductのMCP Tool提供・意味正本と同一視しない。

## 3. Portable SkillとHarness固有Adapterの責務を分ける

**同じ意味と操作条件**（対象/適用時点/Source/失敗/停止/証拠）をProduct所有のSkill本文で記述し、Package/配置Path/Skill発見/Tool alias/起動設定/permission UIだけをHarness別Adapterとして扱う。SKILL.mdを互換パスへコピーできても、Skillの自動発見・実ロード・参照Scriptの読み込み、Host Authorityはそれぞれ実試験する。Adapterは既存Product CLI/API/MCPを呼ぶ薄い設定と案内であり、Productの意味判定や権限を再実装しない。

実Runnerに権限の広いshellがあっても、Modelへ渡してよいSource Rawや外部Network送信が自動許可されるわけではない。実OS/Host/Networkで強制可能な範囲と、UI/Tool/Modelへ実際に渡されたbyteを**別々に**観測する（[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)、[TEI #2515](https://github.com/hat47x/tei-platform/issues/2515)）。公開IssueへRaw trace/秘密由来digestを貼り付けない。実Receiverの詳細証拠は保護領域に、共有結果は開示許可済み投影に限定する。

**配布と評価の違い**：YIシリーズ配布[TAI #74](https://github.com/hat47x/tai-pleroma/issues/74)はProduct Skill正本への版参照、必要依存closure、Harness別の対応/制限、再現手順を組み立てる。各ProductのSkill本文をTAIの新たなCanonical Copyへ無条件複製しない。利用者はTEI単独・TAI無し・MCP無しでread-only利用できる。

## 4. 試験パイロット SK-03：同じTaskを2 Harnessで実観測

**開始前提**：[SK-02](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)が定義したH2（実Tool-only）対H3（実Tool+Product Skill）の独立Session・逆順比較・独立Oracleを優先する。SK-02の合成20/20適格性Checkerは実SessionのPASSではない。最初のProductはTEI #2605で、固定公開Workspaceの「対象ID/型/Source/Validation WarningとUnknownを保持してread-onlyで説明する」一件とする。TEI [merged #2626](https://github.com/hat47x/tei-platform/pull/2626)の実CLI限定観測は初期候補を裏付けるが**SK-02/03の外部Harness実行とは別証拠**。

### 実証順序と比較因子

1. **SK03-G0／環境棚卸し**：初めに既存契約/実installを確認した2 Harnessを選ぶ。例えばClaude CodeとOpenCodeを候補、CodexとDSHもP0代替/追加比較。モデル・Tool・CLI・Source・Host権限を可能な限り固定。固定不能な項目は**Harness性能やSkill効果の因果比較を保留**。DSH/Cloudを最初の必須P0成功条件にはしない。
2. **SK03-G1／同HarnessでSkill効果**：SK-02のH2/H3（新規SessionでH2→H3とH3→H2）、forced loadとauto discoveryを別group。Task oracleはAgentに非提示。実Skill loaded closureと実Tool args/resultが無い場合、比較資格を保留する。
3. **SK03-G2／2番目のHarnessで可搬性**：共通Product Skill本文/参照closureと同じCLI executable/fixture/Expectedを移し、Harness固有の配置設定・Tool mappingのみを変更。Tool-only成立・Skill load可否・意味忠実性と失敗を**別々に採点**。異なるモデルを使う場合、Skill効果やモデル品質ではなく「その構成での操作・契約互換性」に限定して結論する。
4. **SK03-G3／変更注入とHandoff**：Aの公開合成作業票をBに受け渡し、Source-only移動（WorldFP同値・SourceIndexFP変化）、Skill参照Script改版、Tool alias/schema/実binary変更、Grant/Disclosure失効、受信済みACKだがBody未受領などを一項目ずつ注入。Aが以前に成功したことを現在Bでの実call/公開/Effectの許可にしない。
5. **SK03-G4／2 Product・外部Result**：SK-02/03の最初のExitを満たした後、必要な場合のみSHO出典再解決・EKI同Attempt配送/Consumer読取、Mock write/Receiptまで拡張。Agent/Tool成功を実Product作用へ昇格しない。

各段の成功は**その段の観測のみ**。CLI接続が成立してもSkill効果は未知、Skill移植が成立しても跨Harness再開は未知。実行不能な対象Harnessは機能の正確なunsupportedを残し、別Harnessのpassで代用しない。

### Handoff票に保持する最小要素（新共通Schemaではない）

<code>task purpose / source+occurrence / known meaning+owner status / scope+epoch / artifact+tool+skill closure references / actual observation and unknown / last result+attempt+body receipt / permission+disclosure recheck requirement / current target consumer / residual work</code>。これを一時的な**受渡し用Projection**として作り、原本は各Product/Hostが保持。Aの秘密の生Data・内部Oracle・Credential・未公開Tool名・チャット内部思考は引き継がない。Bは少なくともSource/実Tool/loaded Skill/Grant/Recipient/Effectを**用途と現在時点に応じて再確認**する。Receiptが不明なEffectは、同じTask文言での無条件再送をしない（TAI #271、EKI #465）。歴史的Observationと現在資格を混同せず、再読取不要と確認できた独立Claimの履歴は保持する。

## 5. SK-03の独立負例（受入票；現状すべてNOT RUN）

| ID | 変化・反例 | 正しく示すべき範囲 |
| --- | --- | --- |
| HX-01 | OpenCode + DeepSeekモデルをDSH実行と誤記 | Harness identity/profileを分離し、DSHの試験資格を与えない |
| HX-02 | 同じSkill root、Bでreferences/scriptsを読めない／別byte | 配布・発見・実ロードclosureを分離 |
| HX-03 | MCPはconnect済みだがtool schema/alias/transport revision違い | 当該Sessionの実Tool契約とargsを検査、不可ならunsupported/unknown |
| HX-04 | 同TaskでCLI結果は同じだがRaw/診断/Session Logの別Sink送出あり | 最終回答同値から非漏えいを推論せず、観測した実Receiverだけ報告 |
| HX-05 | Source-only移動後にWorldFPのみ一致、引用locatorは旧版 | Meaning Historyを保持できてもSource/SHO現在性の再解決が必要 |
| HX-06 | AからBへSkill・Toolの「可用」という文章のみ継承 | Bの実Load/Tool/Host/Grant/Disclosure未確認はunknown |
| HX-07 | AにACKのみ、Bが新AttemptでEffectを再実行 | 同AttemptのBody/実受信と新Effectを分離。無条件replayしない |
| HX-08 | CloudのTool/Skill表示は存在するがLocal CLI/Raw不可 | 実利用可能なread-only投影だけで部分対応。Raw送出を拒否 |
| HX-09 | H3のみ期待答/追加Model権限/Toolが入っている | Skill単独効果の比較資格はineligible |
| HX-10 | H3は正しいがToken/Adapter費用増・Human Review増 | 正答・費用・導入費を別報告し、改善と断定しない |

本パイロットの採点は、(a)各Harnessの対応可能な接続面、(b)H2/H3の**有効な比較のみ**のTask正確性、(c)Source/Warning/Unknown/Receiverの忠実性、(d)初回Adapter工数＋反復時総費用、(e)False complete/False unsupported/False grant、(f)未知・未観測出口の残余に限定。全体を一個のpercent supportedにしない。違うHarness間でModelの性能・料金やTool/API環境が異なれば、個別の支配的原因を断定せず構成比較として報告する。

## 6. 既存Ownerと更新判定

- **TAI #168 / Draft #270 SK-01 / 本SK-03**：Harness環境行列・移植性・評価、ToolとSkillの実到達、他Harnessへのresume。
- **TAI #271**：意味・依存・Current Grant/Disclosure・同Attempt Bodyの選択的再資格化。TAIは全ProductのDependency Graphを新実装しない。
- **TAI #74**：配布Candidateの版固定/必要依存・Adapter差分・配布説明と各構成の受入状態。実配布は別。
- **TEI #2605 / Draft #2607 / #2649**：TEI Product Skill・CLI/Source/Role/Operationの実在とeffect分類。TEI独自HostやHarnessごとの意味正本は作らない。
- **TEI #2509**：DSH固有の実送信を確認、**他Harnessとの横断比較のOwnerではない**。
- **TAI #232 / TEI #2515**：実OS隔離/Host権限/Receiver別の実Egress、内部Evidenceと公開証拠を分離。
- **TEI #2018**：同じ品質条件で初回・反復コストと誤成功を比較し、生産性指標をOwnerで扱う。

**公開仕様の出典と条件**：OpenAI Skills <https://developers.openai.com/plugins/concepts/skills>、Codex/ClaudeのMCP Client例 <https://developers.openai.com/learn/docs-mcp>、OpenCode Skills <https://opencode.ai/docs/skills> とv2 MCP <https://opencode.ai/v2/docs/mcp-servers>、Gemini CLI <https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md>、Cursor MCP <https://cursor.com/docs/mcp>、Copilot Agent <https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/use-copilot-agents/use-agent-mode>。これらは**公称仕様**であり、特定のAccount/Session/OSでの実可用性・安全性や本パイロット合格を証明しない。

**2026-11-03時点の資格**：TEI #2626の限定CLI証拠や既存TAI合成ReferenceはOwner別に存在するが、HX-01〜10、SK-03-G0〜G4、2 HarnessでのProduct Skill実Load/Tool Call、実OS/外部Receiver/継続Task/Current Authority、独立OracleによるTool Skill増分、Owner受理は**NOT RUN／未採用**。まず既存SK-02の実試行が必要であり、さらに合成Checkerだけを追加して実Harnessの代用とはしない。

## 7. 実Product CIの成果をSkill／Source／納品の一般資格へ昇格させない：一件の実TEI Artifactと他Productの反証

### 固定した実証起点（合成Checkerではなく実Go CLIのCI）

[TEI PR #2649](https://github.com/hat47x/tei-platform/pull/2649)の**exact HEAD `30a486324c6ca1fe0b5cd16d6e358dc7fa5a8fa0`**に対する[CI Run #41503235605](https://github.com/hat47x/tei-platform/actions/runs/41503235605)、Job `real-cli-one-revision`（Job ID `125475831812`）は2026-11-02T19:21Zに**completed/success**。TAIが実行したことにせず、TEI Owner実行のJob logから限定観測値を抽出し、TAI Draftに**読み取り専用の[Evidence Pointer JSON](../../evaluations/records/TEI-PR2649-one-revision-actual-cli-observation-2026-11-03.json)**として保存した。このJSONはProduct別Source/DB/Policyを統合する新共通Schemaではなく、元Runへ戻れる比較票である。

- **本物のCLIとReader**：Go 1.26.10、Linux、指定HEADのCLIが`operations`／`artifacts`を別プロセスで実行、`artifacts -out`が一時出力した**5つのArtifact実ファイル**を独立Python Readerで再読取し、期待Content bytesと一致（`reader_validated_bytes=true`）。
- **完結性の反例**：前後とも`Manifest.Complete=false`／**Operation Gaps=4**、Findings=0。**5つのbyte一致・Findings=0を「全ての必要Artifactが揃った」「業務Operationが実行可能」「納品/Review受理完了」へ読み替えない**。ConsumerのRequiredMemberを独立に定める必要がある（TEI #2630/#2633／MMI #658）。
- **版の反例**：Source fileをbyte不変で移動させると、World fingerprint `sha256:bd53dbac...`は一致する一方、**Source Tree、Model Revision、Manifest Digestは変化**。実Checkerは旧Operationと新Artifactの混合を`qualified=false`として拒否。**「同じWorld意味」と「同じSource引用、同じManifest/Consumerに渡せる世代」を混同しない**。
- **行為の範囲**：`-out`による一時ファイル生成は明確なローカル副作用。TEI #2649の実CLI CI成功は、SK-02の**初期read-only H2/H3 Profileでそのコマンドを許可したことではない**。今回の実Runで確認できるのはテスト用Workspace/Readerまでであり、外部HarnessへArtifact bytesが届いた実績ではない。
- **時間的な限界**：前後でSource digestを照合しても、二つの呼出しの間に書換えがなかったことや、履歴がABAを含まないことは示さない。TEIのObservationが立証した「その時のResult」とStorageの原子的Snapshot/Fenceは別保証。

### 外部への受渡しを誤る三つの反例

| 経路 | 既に確認できた局所事実 | **このパイロットでまだ取得していない**資格 |
| --- | --- | --- |
| **SHO [Draft #13](https://github.com/hat47x/sho-composer/pull/13)** | Python test-only CLIの17/17局所実行記録。**同bytes別パス、A→B→Aの未検知、出力部分書込みや作成後Source変更の要照合状態**を区別。 | SHO実製品/Node/Editor/Storage fence/現在のReview・Consumer読取。旧bytes復帰はReview復活ではない |
| **MMI [#756](https://github.com/hat47x/markdown-matrix-injector/issues/756)** | 旧mainの実MCP/CLIでveryHidden Sheet・非表示Row/Columnがinspect/select/renderへ展開され、結果にVisibilityの説明がない。 | 原本Ownerの意図・機密区分、選択Scope/非表示属性の実Provenance、SHO引用・外部Recipientの開示資格 |
| **MMI [#758](https://github.com/hat47x/markdown-matrix-injector/issues/758)** | 旧mainの実MCP/CLIでCP932 CSVは値へ復号されるが、出力には採用Decoderがない。 | Raw Source digestとDecoder rule/versionからValueへの再現保証、別Harnessの値一致、外部送信 |

重要なのは、**Source bytes／Source identity／Interpretation（Decoder・Parser）／Selection（Visibility・Scope）／Published artifact／実Consumer読取／現在Audience資格／継続的な版不変性**を一つの`sameHash`や`success`で代替しないこと。反対に、同digest別SourceやVisibility不明を即「秘密漏えい・業務不合格」と決めつけない。MMI #756/#758のDefault、SHO #13の正式保存・復旧、TEI #2630のRequiredMember、TAI #232のEgress強制はいずれも既存Ownerに留める。

### 次の実行票：先行するSK-02と後続SK-03を混ぜない

| ID | 実施対象／Inputを固定する箇所 | 実際のExit（Owner・現状） |
| --- | --- | --- |
| **HX-11** | TEI #2649実CIの固定Sourceと5 ArtifactをReaderが実読取した事実を、**TAI実H2/H3のTrial IDへ誤転記しない** | 前述のJSON Evidence Pointerとして**元Run実観測を固定済み**。TAI Skill/H2/H3はNOT RUN |
| **HX-12** | TEI旧Operation＋Source移動後の新Manifest、同WorldFPだが異ModelRevision | Consumer必要集合/Actual Reader版の一致を試す前は**混合再利用を拒否**。元TEI Checker限定PASS、実SHO未実行 |
| **HX-13** | SHO #13 A→B→A、部分作業ファイル残存、同digest別パスの3独立ケース | 履歴不変／未作用と断言せず、`unknown/reconciliationRequired`をConsumerへ引き渡す。**SHO実Product/TAI Skill未実行** |
| **HX-14** | MMI #756 hidden・#758 CP932の実Toolを将来の**別公開合成Task Group**でH2/H3比較 | `sourceDigest`と値が一致してもVisibility/Decoder/開示が未知ならそのClaimのみunknown。MMI実Product改修、Harness実ロード・EgressはNOT RUN |

**優先工程**：(P0) SK-02のTEI`commands→catalog→inspect→trace→validate`を一つの外部Harnessから実呼出し、現在のSource/Skill版・Tool argv/結果を観測。(P1) H3のSkill実ロードと四独立Sessionの比較適格性、独立Oracleと総費用を測定。(P2) SK-03の第二Harnessへ公開Evidenceだけを引継ぎ、同Sourceの参照再解決・現在Host/Disclosureの確認を行う。(P3) SHOまたはMMIを必要とする別Taskへ進む。**TEI実CIの成功を最初の外部Harness実行として数えない**。

この追加は実TEI CIの独立再読取と他Productの局所反証を受渡し条件に変換した**設計・Evidence Pointerの更新のみ**。本稿でTAI実Harness・SHO/MMI製品・OS/DB/外部Receiver試験を実行したわけではない。既存SK-02、TAI #271／#74、TEI #2605/#2516/#1119、SHO #4、MMI #658の受入とOwnerは変更せず、中央Host/Reader/Claim Store・自動許可Engineを追加しない。

## 8. 2026-11-03：Harness選択の時間・費用・品質期限をEKI/TEIへ正しく引き渡す

**横断成熟事項**：[TAI #168 CQ-01〜08](https://github.com/hat47x/tai-pleroma/issues/168)は「利用者の許容lead time・予算・中断/再開」を前提にHarnessを選ぶが、実Worker/Placementの実行制御は[EKI #19](https://github.com/hat47x/eki-fabric/issues/19)/[#57](https://github.com/hat47x/eki-fabric/issues/57)/[#155](https://github.com/hat47x/eki-fabric/issues/155)等がOwner。[TEI横断Draft #2667](https://github.com/hat47x/tei-platform/pull/2667)は**Data/Quality Checkの期限・Scope・例外**を別論点として持つ。TAI/Skillが単一の「ジョブ完了」「品質PASS」「納品完了」に畳むと、安価なHarness選択でも業務結果を誤報する。**本節は既存のTask・Product契約を使った候補選択/説明/評価であり、新Scheduler/予測API/共通Schemaを作らない。**

### 8.1 二つの時間軸と三つのOwner

| 時間軸／制約 | Skill／TAIが行うこと | 最終的な判断と現物Owner |
| --- | --- | --- |
| Taskの最大Lead Time／締切 | 利用者が要求した期限、現在時点、完了の定義、データ・初期化・レビュー・再開/復旧に必要な時間・不確実性を記録。候補の実績分布がなければ「期限内できる」と予測で断言しない | 外部Harness/Providerの実Tool実行・実結果。EKIへの明示委任では既存Admission/Lease/Recovery |
| Data Quality／監査結果の有効期限 | 完了という返答が必要なCheckSetのScope、Snapshot/recorded/valid time、必須Online・期限付きDeferred・Advisory・例外期限に依存するかを**Productへ確認**。Product側が指定していない全検査強制をしない | TEI Data Quality Rule/CheckSet/Provider/Owner（#2667）。EKI `COMPLETED`は品質が期限内に検査されたという意味ではない |
| 費用／回復予備 | 対象Model/Provider・課金経路、承認された価格/量、成功に必要な予備時間/Retry予算/データ転送/人手、Quota/Rate Limitの違いを比較。料金上限不明なら未知とする | 当該Harness/契約/費用Owner。EKIは物理資源Budget/Permit/LeaseのOwnerで、金額/通貨・外部料金をCoreへ埋め込まない（EKI ADR-0010、#19） |

**選択の順序**：(1) Source/Meaning/Disclosure/Host Grant・Tool/Adapter現在性・必要品質というhard constraints、(2) Deadlineに対する観測済み分布・復旧余裕／中断時のResume資格、(3) 予算・人のReviewと総費用、(4) 判定不能なら期限保証を保留し安全な限定成果へ縮退。費用最小化を安全・現在意味・Quality期限の不足を覆う目的関数にしない。逆に、全タスクに重いQuality Gateを機械的に挿入せず**用途/Ownerが必要とした検査のみ**評価する。

**回復予備の区別**：予測残余時間／将来利用できそうな資源／予約済みcapacity／実際のLease・Permitと消費済みBudgetは異なる。Skill側の「あと一回試せそう」は実EKI回復余裕ではなく、別Attemptの再実行を認める承認でもない。実EKIへ委任していない単なる外部Harness Taskを、暗黙にEKI Task/Workerと呼ばない。

### 8.2 既存CQ/HXに追加する四つの受入負例（SK-03の拡張、NOT RUN）

| ID | 同一タスクの対照 | Skillが避ける誤判定／必要なProduct実証 |
| --- | --- | --- |
| **HX-15 安いが期限不適** | 価格が低いHarness Aの平均所要時間は短い一方、Rate Limit/再開で尾部完了が期限を越え得る。Bは高価だが実績分布と復旧余裕がある | token単価・平均時間だけでAを確定しない。Bも実Tool/Grant/Disclosureに適合しなければ選ばず、不足分は`unknown / cannot-qualify-deadline` |
| **HX-16 ResultとQualityの締切差** | EKIでJobが`COMPLETED`だが、TEIの必須CheckSetが別Snapshot・期限超過、またはRLSで観測Scopeが不足 | 実Task完了・品質観測・使用可能な業務Claimを分離。ProductのCheckSet/例外・現在Audienceへ問い合わせ、全社品質PASSへ昇格しない |
| **HX-17 RecoveryとAttempt** | Worker停止→Claim ACKはあるが同Attempt Body未受領。再送できる見込みがある一方、別Attempt再実行は副作用不明 | 同AttemptのBody取得/再転送と別Attemptの再実行を分離。EKI #465/#468の現実装・許可・期限を参照し、Skillが追加Effectを勝手に作らない |
| **HX-18 公平性と最短完了** | urgent Taskが連続到着、best-effort Taskの回復枠が長期飢餓。最安値ルートは他利用者の予約・Fair shareを侵す | Product Skillが優先順位・fairness/回復枠を上書きしない。EKI #155/実Admission/Recoveryを尊重、勝手な資源横取りを「最適化」と呼ばない |

**次に試す具体順序**：まず既存SK-02の公開WorkspaceでTEI実CLI/H2-H3（Skill merged・実Harness未実施）→二Harness SK-03 HX-01〜14（実Tool/Source/Disclosureを固定）→既存TAI #168 CQ-04/05に対して**公開mock rate-limit/quota/中断時刻・既存EKIの実API資格が確認できるものだけ**HX-15〜18を重ねる。次にTEI #2667側の独立Quality Fixtureが実証された範囲だけ品質期限を検査する。Source fidelity/SHO M0のdraft成功、EKI scheduling predictionや公平性の研究段階を、ここでProduct Coreの合格・自動Scheduler採用と呼ばない。

**評価列**：`requested_deadline; actual_started/completed/consumer_received; deadline_probability+calibration_source; source_epoch/consumer_scope; required_quality_checkset/validation_epoch/expiry/exception; rate_limit_vs_quota; requested_price_budget/approved_billing_route; recovery_reserve_predicted_vs_held_vs_consumed; output_claim_vs_body_receipt; cancellation/retry authority; unmeasured`。これは**記録欄の候補**であり正式な交換Schema/機密データの外部送信を定めない。

**現在の事実と未証明**：TEI [#2607](https://github.com/hat47x/tei-platform/pull/2607) Product Skillと[#2649](https://github.com/hat47x/tei-platform/pull/2649) Capability/Artifact証拠計画は**2026-11-03にmerged**。TEI #2607の[実CI #41532988114](https://github.com/hat47x/tei-platform/actions/runs/41532988114)は同PR merge-ref上で**静的14 tests・Skill整合Check・Go CLI read-only smokeの限定成功**を確認済み。ただし**H2/H3・二Harness・EKI実Worker、期限内確率の校正・TEI実Quality Rule/Provider・Host/OS実Egress、Owner業務受理はNOT RUN**。既存Owner #168/#74/#271/TEI #2018/EKI #19/#155/TEI #2667へ還流し、非対応・未測定・実権限拒否を隠さない。


---

<!-- hx19-hx26-mcp2026-live-conformance-20261103 -->
## 9. 2026-11-03横断深化：MCP 2026-07-28のTool一覧鮮度・追加入力・非同期TaskをHarness互換と誤認しない

### 9.1 新たに解消する不確実性と一次資料

[Agent Skills仕様](https://agentskills.io/specification)は`SKILL.md`と参照素材/Scriptの**配布形式**を規定するが、各Harnessの探索・自動起動・Tool実効権限・読み込んだbyte列の一致までは保証しない。従来のSK-02 H2/H3とSK-03 HX-01〜18は継続し、単なるSkill形式の共通化を実動作互換へ昇格させない。

[MCP 2026-07-28仕様の公式リリース説明](https://blog.modelcontextprotocol.io/posts/2026-07-28/)では、statelessなrequest、`tools/list`等の`ttlMs/cacheScope`によるキャッシュ可能性、ToolのHTTPルーティング用`Mcp-Method/Mcp-Name`、`resultType: input_required`と`inputResponses`を使うMulti Round-Trip Requests、coreから分離されたTasks拡張が導入されている。[Python SDKのキャッシュ説明](https://py.sdk.modelcontextprotocol.io/client/caching/)ではprivate/publicの認可文脈別キャッシュに言及される。**仕様がその機能を許すことと、対象Harness・Server・中継Proxyが当該Revisionを交渉して安全に実装したことは異なる。** 2025世代等への下位互換経路は実handshake/通信経路で別確認する。ACPはEditor↔Agentの連携面であり、Product ToolのMCP/TEI業務契約/EKIのTask正本に置き換えない。

### 9.2 コアの意味と実在能力の五つの境界

1. **宣言された能力（Catalog）**：`tei commands`はselected read-only commandsのみ、MCP `tools/list`も特定Server/Principalで返された時点の候補。両者の「非掲載」は製品全体の不存在証明ではない。
2. **発見に使った有効文脈（Discovery Context）**：Harness/Server/Protocol revision、認可主体、Audience/Scope、cache scope・TTL・実取得時刻・実config。Cache hitとServer実応答を同一観測にしない。
3. **実起動面（Effective Binding）**：呼び出し直前に実Tool名/schema/alias、CLI executable+argv全体、Skill+Script closure、必要Source/Provider/Toolの版・契約を照合。表示名一致やHTTP route headerの一致は意味同値ではない。
4. **現在の行為資格（Current Authority）**：権限変更後もキャッシュ済みToolは画面に見え得る。実Host/Provider/OSが各Actionの現在Grant・開示先・Tenant・Effectを拒否できる必要がある。TTL/スキーマ/Skillの自己申告をAuthorityとしない。
5. **実結果と到達（Effect/Consumer Evidence）**：MCP `tools/call`、input required、別Requestでの再開、Task handle/状態、Provider Receipt、独立Readback、同Attempt Body/Consumer受領は別。これらの段階を単一「成功」に折り畳まない。

**異種Harness共通の資格表**では`(Harness revision, Model/Provider/billing, protocol negotiated, Tool/Skill actual closure, principal+audience, source+scope+epoch, measured calls/results, eligibility, residual)`を読み取り専用の比較票として組み立てる。固定の新ABI/API/schemaを製品に要求せず、既存TAI #168/TEI #2605/#2516/TAI #271の証拠参照へ接続する。

### 9.3 HX-19〜26：既存SK-03に追加する独立反証（提案・実試験NOT RUN）

| Case | 正負の独立入力・故障注入 | 必須観測／誤った昇格の拒否 |
| --- | --- | --- |
| **HX-19 Cache scope** | 同じMCP URLでPrincipal AにはTool X、Principal Bには非公開Tool Yが許可される。Proxy/Clientが`tools/list`をcacheする | 実`cacheScope`、caller/tenant、server response、client visible catalog、cache hitの区別。Aのprivate listがBへ再利用されれば**漏えい**。Tool名・schemaも開示対象（TAI #232） |
| **HX-20 CatalogとGrantのTOCTOU** | 取得時はX許可、TTL内にHost Grantが失効。Harnessには旧Tool名が表示されたまま | Tool listingが残っていても**実invokeをHost/Providerで拒否**。catalog更新待ちやTTL満了を認可失効の強制手段にしない |
| **HX-21 「一覧にない」と「利用できない」** | TEI選抜`commands`外の実dispatch、MCP Server側のTool追加、Server起動不全を独立注入 | 本体で不存在／catalog未掲載／不許可／未接続／古いcacheを分類。旧一覧だけで「実装なし」や「現在実行可」を断言しない |
| **HX-22 Revision/alias差と下位互換** | 2026-07-28と旧RevisionのServer/Client、MCP名prefix、`Mcp-Name`経路で異なるToolが解決される条件 | negotiated Revision、実route、実Tool schema/args/result/失敗が一致する範囲のみ資格化。旧clientへのsilent fallbackを同一プロトコルPASSにしない |
| **HX-23 MRTR再試行と承認** | `tools/call`が`input_required`を返し、利用者回答後に`inputResponses`付きで再要求。応答前のProvider Effectは未知 | 追加入力UI/別Requestを「新しい業務承認」「副作用未発生」「同一Attempt継続」だと勝手に認定しない。実Effect不明ならHost/Provider Receipt照会へ。読取り専用Taskは独立して継続可 |
| **HX-24 MCP Tasks≠EKI Task** | MCP Tasks拡張のhandle/Cancel/Resultと、EKI Task/Attempt/Lease/ResultClaimを同名扱いするAdapter | 物理Transport/Agent Job statusとEKI Authority、実Body受領、Business Verifiedを分離。cancel APIの応答は実Provider停止/副作用取消しの証拠ではない |
| **HX-25 Tool集合の非単調変化** | 同名候補Provider追加、alias変更、Tool列挙順変化、prompt-injection入りTool description | 以前選んだContract/Provider/Scopeの意図しない代替・権限昇格を拒否。未信頼descriptionはTool/GrantのAuthorityでない。推奨順序の変化は変更理由を記録 |
| **HX-26 Cached resourceとSource所在** | `resources/read`のcacheは存続するがSource同bytes別path、SourceIndex/引用locatorまたはDecoder規則が変化 | 資源cacheのFresh判定≠Product Source occurrence/Accepted Meaning/実Consumer読取の現在資格。再解決が未観測なら関連Claimのみunknown。SHO/MMI/TEI元Ownerへ戻す |

**局所の観測可能性**：本表での「実拒否」「漏えいなし」は、実Server・Proxy・OS/Networkを含め、検査したSink/Principal/版に限る。可視化されたTool名・最終回答一致・Modelの「安全」との自己申告では保証しない。Mock canary、公開TEI Workspace、独立Expected、Error/Unknown/未取得の区別を使い、保護対象Raw/実Credential/有料Providerの送信をP0実験の前提にしない。

### 9.4 最小の実行順とProtocol観点を追加する判定表

- **S1（前提）**：merged TEI Product Skill #2607とCLIで、Skillなし／ありのSK-02実4 Sessionが開始できることを固定。Tool/Skill実Load未観測ならSkill効果は`insufficient-evidence`。これを代替する新Mock Skill Harnessを構築しない。
- **S2（二Harness）**：SK-03で固定公開Workspace/独立Expectedを二Harnessで呼ぶ。同じモデルを設定できなければ**構成上の相互運用**に限定し、Skill/Model効果の因果帰属をしない。
- **S3（MCP差分）**：S2でMCPが実可用と確認できた場合のみ、ローカルMock/ProxyでHX-19/20/21/22/25のCatalog/Grant/Revisionを一条件ずつ変更。**CLI-only経路は別対照として継続**し、MCP必須Core化しない。
- **S4（対話・非同期）**：MCP MRTR/Tasksに実対応するHarness/ServerでのみHX-23/24の`input_required`、Task Cancel、Result/Body/Receiverを測る。EKIに実委任していないHarness TaskにEKIのAttempt/Lease/保証を付与しない。
- **S5（Source/配布）**：HX-26、Skill/Adapter/Protocolの必要依存閉包変更、TAI #271のJ0全再検証／J1選択的再資格化／J2旧成功の無検証採用を比較。危険なJ2は公開合成環境のみ。現在の権限は古い証拠で免除しない。
- **S6（運用）**：第8節のDeadline・Quality期限・Budget・Recoveryと接合。単にTool callが完了しても、必要なQuality Check/Artifact Body/Consumerが締切内に完了しない場合は`business-usable`としない。

**比較列**：`actual handshake revision / discover and list endpoint / ttlMs / cacheScope / cache hit / principal+audience / actual tool identity+schema+route / call attempt / input_required+inputResponses / async handle+cancel / Host deny/allow point / effect receipt / reader outcome / actual network sink / unknown coverage`。実装/仕様の異なるHarnessで取れない列は未観測とする。公開仕様の列に値があることを実起動証拠へ昇格しない。

**Owner**：本SK-03／TAI #168が**外部Harnessとの運用互換**を担当。**TAI #74**は版付きPackage/Adapter/Tool/Protocolの配布、**TAI #271**は現在性とHandoff、**TEI #2605/#2354/#2516**はCLI/Source/意味/実Consumer、**TAI #232/TEI #2515**はOS/Network/Receiver、**EKI #57/#465**はTask/Lease/Body/実Effectを担当。MCP公式仕様適合検査とProduct意味/Host認可は別。MCP特有の本体改変は実測必要性が見えるまで提案のみ。

**状態（2026-11-03）**：HX-19〜26とS1〜S6の新規実Harness実行はNOT RUN。MCP 2026-07-28は外部仕様調査に基づく候補。TEI限定CLI CIやTAI合成Checker、旧MCPクライアントの静的設定を本パイロットの実証PASSに合算しない。


---

<!-- sk03-negative-closure-witness-20261103 -->
## 10. 2026-11-03横断統合：否定的な結論をHarnessの要約・Handoffで強めない（NC-01〜16）

### 10.1 未解決だった問題と原則

他レーンの[TEI #2586（Query→Context→Claim）](https://github.com/hat47x/tei-platform/issues/2586)、[#2516（用途別Projection/現在性）](https://github.com/hat47x/tei-platform/issues/2516)、[#2497（投影の情報保存）](https://github.com/hat47x/tei-platform/issues/2497)、[TAI #271（再資格化）](https://github.com/hat47x/tai-pleroma/issues/271)を接続すると、**異なるHarnessが同じ空配列`[]`や「見つからない」という文字列を返しても、元Source/母集団・読取範囲・非出力条件・権限・観測時点が一致する保証はない**。例えば「明細が存在しない」と「部分取得でまだ見えていない」「組織権限外で非開示」「SQL/Providerが失敗」「Tool結果が途中で切られた」は、薄いAdapterの表示では同じ`[]`に見える。

形式的には、許されたProjection `P` について`P(x)=P(y)`なのに、要求する否定Claim `Q(x)≠Q(y)`となる二つの世界があれば、`P`の結果だけではQを断定できない。これは**情報保存に関する設計条件**であり、Harnessが真のQuery/業務意味を推論し直す機構ではない。最初は「言える結論を強めない」「足りない根拠をProductに照会する」「照会/開示ができなければunknownを残す」だけを義務とする。

### 10.2 既存Productが出せるEvidenceを運び、第二のOracleを作らない

HarnessやSkillが結果を「0件」「存在しない」「問題なし」「完了」「実行可能」と表示する場合、最低限**主張の種類ごとに**以下の成立範囲を確認する（全出力へ同一の巨大共通Schemaを要求しない）。

| 主張の型 | 実観測が必要な条件 | 対照する誤った結論 |
| --- | --- | --- |
| **局所的な存在** | 実読取した1件のID・Source/Scope/epoch・可視範囲・重複/粒度 | 部分集合の実在1件を全件数や永続的存在へ拡張 |
| **局所的な不存在** | 母集団・Predicate（非表示条件/Relation path含む）・authorized population・Source/Read cohort・全ページ/coverage・例外/欠損・Productの「このScopeで判定可能」という根拠 | `[]`やnull/Tool timeoutからグローバル不存在を断定 |
| **操作が利用できない** | 実Harness/SessionにおけるCLI dispatchとTool/Skill discovery・版・現在Grantを分ける | `tools/list` cacheに非掲載なのでTEI本体にOperationが存在しない |
| **副作用が起きていない** | 意図/要求/Attempt・Provider Receipt・独立Readback・不明Commitの扱い | MCP Cancel/通信失敗・EKI ACK欠落から未実行・安全Retryを断定 |
| **チェック完了/利用可能** | 当該ConsumerのRequiredMember/CheckSet・Scope・Quality期限・実Artifact Body/Reader・未完・部分結果 | TEI manifest `Complete=false`／EKI Claim ACKだけで業務成果が完成 |
| **非公開である/漏れていない** | そのAudience・Tool候補/診断・実Egress/DOM/Log等、検査した各SinkにおけるHost/OS/Receiver観測 | 最終回答同値・redacted promptだけで全出口非漏えいを断定 |

同一Query結果でも、肯定Claimは実読取した存在証人だけで成立することがある一方、否定Claimは**閉じた探索範囲**が必要。SQL `WHERE`の**出力に現れないPredicate/組織Rule/Provider Route**も不存在の依存となる（TEI #2586/#2634/#2637）。部分取得やRLSで非表示の行を「無い」とも「ある」とも無断公開しない。Source/Scope/epochが一致しない共同Claimは各Productへ戻す。Claimの正誤・SQL/RLS意味・Original RawのOwnerはTEI/保持Productであり、TAIは受領者が判断に必要な差異を失っていないか検査するConsumerである。

**Handoffの安全則**：Harness Aで`not-found`と回答した履歴はBで`currently-absent`へ昇格しない。Aの根拠/対象/時刻を保持し、Bに公開可能な範囲でSource/実Read/現在Host Grant/required quality/Consumerを必要に応じて再確認する。可視性の理由が秘匿対象なら「権限範囲内で確認不能」など用途相対の許可済み説明に限定。原因/Tool名/候補件数の露出も開示制御を受ける（TAI #232/#272）。

### 10.3 実行した限定Referenceと実製品で残る義務

**新たに実際に検査したもの（局所16/16 PASS）**：

- [test-only Node script](../../evaluations/tools/check-sk03-negative-claim-transport.cjs)を追加。`node --check`と`node ... --self-test`をNode v22.16.0/Linux上で実行。7種類の**人工Producer Profileを別のNode子プロセスから実stdout/stderr/exitとして取得**し、Adapterの投影を変更した16正負ケースで検査した。
- [限定実行記録](../../evaluations/records/SK03-NC-local-transport-2026-11-03.json)にScript SHA-256/Blob・ケース結果を保持。**NC-01**は「列の存在が保持され、独立したProduct採点に回せる」ことだけを`evidence-preserved-for-scoring`とする。**真の不存在を確認したわけではない**。
- **NC-02〜05/12/16**：部分取得、権限外に隠れた母集団、coverage/非出力依存/read cohort欠落、全Tenantへの量化を`insufficient-evidence`へ。**NC-06〜08**：partial→complete捏造、Predicate差替え、Warning欠落を`evidence-mismatch`へ。**NC-09〜11/15**：実行で行が存在、Producer失敗、壊れた/切れたstdoutを「正常0件」にせず分類。**NC-13/14**：epoch/SourceIndex移動を`stale-or-different-binding`へ。
- 現在のScriptは**合成Sourceからの実ローカルProcess通信**であり、実TEI CLI/SQL/DB/MCP/Claude Code/Codex/OpenCode/DSH/SHO/EKI、実RLS・OS/Network遮断、独立業務Oracleではない。Sourceに宣言した`coverage=complete`の真偽を自動認定しない。リアルなSource未観測の成功に転用しない。

**次の真正なExit**（既存SK-02/03/TAI #271に接続。新Gate/Oracle/Runtimeを増やさない）：
1. **P0 Product**：TEI [merged #2607](https://github.com/hat47x/tei-platform/pull/2607)のread-only `commands→model catalog→inspect→trace→validate`を、固定公開Workspace・実Binary・全argv/Exit/Warning/SourceIndex付きで実行。すでにあるTEI製品CIの実証を再利用し、TAI Harness試験へ偽転記しない。
2. **P1 Harness A**：実Tool-onlyとSkill Loadの別Sessionを比較し、元CLI JSON→受信Tool結果→利用者への説明で、失敗・未取得・Source引用と否定Claimの限定を維持。Tool結果切り捨て/Response縮約/出力上限を観測する。
3. **P2 Harness B**：Aの許可済みread-only HandoffをBへ移す。全探索・現在Grant・実Consumerが確認できない場合の`unknown`を認め、単に回答文が一致しただけではPASSしない。
4. **P3 Productの否定Claim**：TEI #2586で独立Oracleと実Query/Context/Scopeのread closureが実証された範囲だけ、RLS・0件・Window/NULL・非出力Predicate・Quality期限の具体的Claimを適合判定する。未実装APIは作らず、実Toolを使える範囲に限定。
5. **P4 Outcome**：EKI同Attempt Body／SHO Reader・実Deliver、OS/Network/Egressと実Effectは各Ownerへ。Agentの`done`文字列で納品や非漏えいを保証しない。

**本節の資格**：新しいNode Scriptの局所16/16は観測済。2 Harnessや実Source/ConsumerのSK-03試験、否定ClaimのProduct Oracle、実保護/業務効果、Owner採用は**NOT RUN**。ScriptをProduct/TAI CoreのValidatorへ格上げしない。
