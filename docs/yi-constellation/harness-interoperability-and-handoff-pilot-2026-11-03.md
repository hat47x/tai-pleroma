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
