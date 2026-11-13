# YI Constellation：Skill選択・意味連携・実効権限・可搬性の深化（2026-11-02）

状態：**提案／設計検証の追加、Owner未受理**。本ファイルは[親構成計画](harness-skill-plugin-plan-2026-11-02.md)と[SK-01](../../evaluations/SK-01-harness-skills.md)の補助設計。新しい共通ABI/Schema・共通Host・中央Registry・第二Authority/意味正本の採用を宣言しない。別Harness実接続、Skill選択精度、OS隔離、TEI/SEI/SUI/SHO/EKIの新E2Eは**NOT RUN**。

## 1. 現行Product Skillの実在状況を固定（2026-11-02 GitHub main静的調査）

この表で検査したのは、各mainの**ルート直下の`skills/`ディレクトリ**。他のディレクトリ・ユーザー環境に存在しないことまでの証明ではない。代表Skill名はすべて設計候補。

| Repo | main commit（照合時） | ルートの`skills/` | 資格 |
| --- | --- | --- | --- |
| `tai-pleroma` | `95253b11c18c0c335442194edec15e9ba7985646` | なし。PR #270内`examples/skills/yi-tai-activity`は**未配布の試作** | 正式Skill未確認 |
| `sei-cognition` | `234c3f91ce86b59b0f202295f454bad74dc6758c` | `ponytail`のみ | 汎用開発支援Skillであり、SEIの認知Method/製品呼出しSkillではない |
| `sui-sensemaking` | `42ec002699766d3eec5efa9754b90353cc0c01e7` | `ponytail`のみ | 同上。SUIのCard/Island/Projection操作Skillではない |
| `tei-platform` | `9c9ef4d160640908e06ad13afb6c2b45c664c748` | ルートに`skills/`なし | TEI専用Skill未確認 |
| `markdown-matrix-injector` | `e293927e7decb548c9662c4a19a140c1d017a1a8` | **`mmi`**、`ponytail` | `mmi`は実在のMMI CLI/MCPを用いた**製品向け**Agent Skill（ただし本調査ではHarness実接続していない） |
| `sho-composer` | `489e9e7d84c783f35ee029d8eee500cdff091c23` | ルートに`skills/`なし | SHO製品Skill未確認。MMIを機能正本として再利用 |
| `eki-fabric` | `eceb997c5c2261b279a0bc320275a35e37a0a04b` | `ponytail`のみ | 同上。Task/Resultの製品向けSkillではない |

**補正**：既存`ponytail`を「各Productの実在するSkill接続」と扱わない。これは共通のコーディング方針Skillであり、`yi-sei-inquiry`や`yi-eki-delegation`の代替にならない。各RepoにProduct固有Skillを作る場合は別Ownerの新規実装資格。既存`mmi`も記述と実CLIの存在が確認できることと、特定Harnessへの導入・実実行・ユーザー便益は別のEvidence。

## 2. 三つのSkill役割＋二つの独立したPlugin

**役割A：製品技能（Product Skill）**。各製品が自分の具体的な操作を教える。何を読んだか、どの版のCLI/API/MCPが使えるか、どの範囲が検証済みかを示す。自Repoで正本を更新し、TAIを要求しない。

**役割B：認知・専門Method（Method Skill）**。SEIのMethod適用、CSWの自由探索、数学/単位/SQL/学術論文解析等の専門手順。ユーザーの問いに応じてMethodを**提案・適用**しても、SEI Method Applicationの正式な経緯やTEI受理済み意味をSkill文書に代替保存しない。専門家がAI、人、決定的実装のいずれでもMethodの入力・根拠・残余を区別（[SEI #767](https://github.com/hat47x/sei-cognition/issues/767)）。

**役割C：活動・組合せ（TAI Activity Skill）**。利用者の目的/用途に応じて必要な製品・Methodを**選択/省略**し、成果と残余を次の操作や別Harnessへ引き継ぐ。実行スケジューラや第二Agent/Model Routerを自作しない。ハーネス内のSkill-to-Skillの直接呼出し機能は環境により異なるため、**複数Skillの「自動入れ子呼出し」を前提条件にしない**。必要ならTAIが製品のCLI/Toolを直接使い、専門Skillは参照手順として利用する。

**Plugin-I：Productの機能拡張Plugin**。例：TEI DSL/Domain Plugin/TALON系Composite Function、外部Host向けService Contract＋Provider実現、UI contribution。これは製品のモデル意味／Target機能に関わる（[TEI #2390](https://github.com/hat47x/tei-platform/issues/2390)、[#988](https://github.com/hat47x/tei-platform/issues/988)）。「Agent Skillを置けば製品Pluginが実装された」と扱わない。外部HostでのC0契約-only/C1静的組込み/C2隔離呼出し/C3 Host拡張の実証資格とも別。

**Plugin-II：外部Harness向け配布Plugin**。Skills、MCP/CLI接続設定、必要ならHooks/Commands/依存を、選択されたHarnessの形式でまとめる。Skillsが基本の再利用可能な手順、Pluginが配布単位（[OpenAI仕様](https://learn.chatgpt.com/docs/customization/overview)、[Plugin docs](https://developers.openai.com/plugins/concepts/skills)）。**Harness Pluginの導入やProductへのログインはProduct Pluginの登録・業務効果の許可ではない**。

この二Pluginは別名前空間・別ライフサイクルで管理する。Skillが`scripts/`を含む場合は**実行可能コード**として依存・改ざん・ファイル/ネットワーク/権限を監査する。文章だけでもPrompt Injectionで外部Toolを操作し得るので、SkillのSource trustはToolの認可ではない。

### 推奨する発見・読込み

外部Harnessが最初に見える`name/description`は短く、**必要時にだけ詳細Skill/Referencesを読み込む**。Agent Skills仕様のProgressive Disclosureを利用し、多数の専門Skillを増やしても全本文を一括投入しない（[Codex Skills公式](https://learn.chatgpt.com/docs/build-skills)）。探索・大量AI並列を目的別のSkill細分化で許容するが、常時全Skillロードは設計目標にしない。

Skill名の衝突は、実際のHarnessが実装する選択挙動を検査する。たとえば同名`mmi`の改変Skillを別パスへ導入した場合、`Skill name`のみで同一Source/信頼資格と扱わず、**実際に読み込んだファイルのpath＋content digest＋呼出しProfile**を特定する。ImplicitとExplicit invocationも別ケースとする。

## 3. Capability情報は「発見できる」「使える」「資格がある」を分離

Capability Discoveryは利用者の作業のための**候補発見**。自己申告のManifestを全信頼しない。新しい共通常駐Registryは不要。

| 資格段階 | 要求する観測 | それだけでは言えないこと |
| --- | --- | --- |
| D0 Declared | Skill/README/Manifestに能力の説明がある | 現環境にTool/実装が存在するか |
| D1 Installed | Toolバイナリ/Endpoint/Skill pathの実存在とexact版 | 実行可能・呼出し許可があるか |
| D2 Listed | Tool/CLI Catalogに現在の入力出力が列挙される | 強い操作が実Hostで拒否されるか |
| D3 Accessible | 現Actor/Scopeでread-only／mock callが成功し、実入力を検証 | 現在の意味契約・外部作用が受理されたか |
| D4 Qualified | 対象のClaim/時点/Source/Target/PermissionでProduct側Conformance＋Owner必要判断が成立 | 別用途・別Consumer・将来の資格 |
| D5 Effect Observed | 実作用が必要な場合は同一Task/Attempt/Provider Receiptと独立Observationで結果を確認 | 何も行わずとも効果がある、または全体の活動価値 |

**D0〜D5は評価票上の説明用であり、全製品共通Runtime状態enumではない。** Product Ownerの既存証拠を参照し、Agentごとに同じ事実の独立正本を作らない。CLI/MCP/PluginのTransportやMCP tool annotationはD4/D5の根拠にしない。

同じTaskを異なるHarnessで実現する場合は、`Capability identity`と`現Harness上のTool名`を分ける。Tool nameだけで別Owner・別環境の同一契約を自動joinしない。明示的に未対応のCapabilityは`unsupported`、Toolが一時的に落ちた場合は`unavailable`、照合情報が得られない場合は`unknown`。

## 4. Cross-Product Skill Handoffを「情報量」でなくClaimと受渡しの適格性で設計

TAIがProduct間で運ぶのはすべてをまとめた普遍JSONではなく、**用途に必要なSource/Claim/Operation/時点/開示資格への参照**と、正本側が許した投影。TEI [#2516](https://github.com/hat47x/tei-platform/issues/2516)のConstruction ContextとSEI [#767](https://github.com/hat47x/sei-cognition/issues/767)のInquiry診断を参照する。

- 同一の数値でも、Grain/Bag multiplicity/Group/Unit/Quantifier/時間/Scopeが違えば同一Claimとは限らない。値が異なっても比較範囲が異なるなら「矛盾」としない。
- **同じ公開Projection `P(x)=P(y)`でも判定Claim `Q(x)≠Q(y)`になり得るなら、外部HarnessはQを確定できない。** Source保有Product内部の用途限定照会が必要であり、回答の真偽や理由そのものにも開示判断が必要。繰返し照会・件数・エラー・差分による推知を防ぐ。
- SEI Skillが担うのは「どの追加証拠や専門Methodを要求すべきか」の選択であり、TEI Query/Math比較器の再実装ではない。SUI Skillは複数仮説の生成・保留を損なわず、探索中に強制採否Gateを入れない。
- SHO Skillは「文書保存（作業成立）／Source再解決／説明成立／レビュー／固定納品資格」を独立に扱い、TEI意味受理やHTML表示成功で一括PASSにしない（[SHO #1](https://github.com/hat47x/sho-composer/issues/1)、[#6](https://github.com/hat47x/sho-composer/issues/6)、MMI #658/#672）。
- TEI Skillで「論文→実装」を扱う場合は、原論文のSource/引用・数学的意味/単位・TEIモデル仮説・検証済みGenerator/TargetとSHO説明文書を分ける。**論文URL/索引/インデントによる親子関係の記録だけ**でも独立した最小ユースケースとし、すべての論文を実行コードへ変換しない。論文同士の参照、親子、版間の対応は探索・発見と意味受理を分離する。
- TEI Script/DSL、Composite Function、Domain Plugin、SQL/組織構造へのSkill適用では、`Definition/Instance/Realization`、入力・出力・効果・Assumptions/Guarantees、Targetの外部Hostを尊重。Skillはモデルの編集手順であり、実行意味を定義する権限ではない。

### 受渡しの連続性は4種類

1. **Informational**：原資料への再到達、版、Scope、開示された根拠とunknown。
2. **Semantic**：Claim/モデル/Methodの意味・受理範囲・必要な未決/再確認。
3. **Operational**：実Task/Attempt/Artifactと可視な状態（EKIのClaim ACK/Body/AcceptedResultを別観測）。
4. **Authority/Effect**：現時点のGrant・本人/Owner判断・外部Providerの実効果。**他HarnessへGrantをコピーして継続とはしない**。

活動継続は4つが常に全部揃うことを意味せず、どの連続性を保存したかを明示する。とくに[EKI #465](https://github.com/hat47x/eki-fabric/issues/465)のRun→Body senderの断絶が残る場合、Claimの状態から成果物本体取得を推定しない。

## 5. ハーネス環境とSkill配布の実装差分

| 対象 | 先に検査すること | TAIで固定しないこと |
| --- | --- | --- |
| Codex/ChatGPT | 実Skill path、name/descriptionの発見、implicit/explicit、Tool依存、Plugin導入の可否 | ChatGPTとCodexの全環境の機能同等性。Codexは`.agents/skills`等を使うが、試作`examples/skills`は自動検出位置ではない |
| Claude Code | `.claude/skills`や配布Pluginとの違い、CLI/MCP接続、明示Skill/暗黙選択 | 他社Plugin manifestをそのまま読み込めるとの仮定 |
| OpenCode/DSH | 実Profile/Tool接続、外部Subagent/Goal/Scheduleの有無、モデル・料金枠、OS資格 | DSHの`sdk-minimal`とheadless/Baseを同じ機能・安全性とみなすこと |
| Dots/Grok等 | 各ユーザーの実利用可能な連携方式・Plugin/Skillのサポート | Claude Codeの`SKILL.md`をそのままアップロード可能との決めつけ |

**実送出を独立測定**：DSHの`dsh-session-log-deepseek`は`messages`以外の`dsh_session_log`や未受理backlogを送る可能性がある（[TEI #2515](https://github.com/hat47x/tei-platform/issues/2515)、[TAI #234](https://github.com/hat47x/tai-pleroma/issues/234)）。Model input token数だけを機密送出量と扱わない。Credential/OS user/Network/Session cache/Tool response/Clipboard/Issue出力を合成canaryで確認し、Skillの「送らない」指示を防護の証拠としない。TEI外部UI制御（[#2391](https://github.com/hat47x/tei-platform/issues/2391)）はE0〜E3 Headless先行で、E4のTest instrumentation・Production物理除去を追加資格とする。Skill有無が本番生成物に危険な制御入口を残さないことを実Artifactで検証する。

## 6. Skill更新・衝突・縮退：変更の種類ごとの再確認

| 変更 | 再確認の候補 | 勝手に復活しない資格 |
| --- | --- | --- |
| Skill `description`・選択語 | Intent routing、誤起動/不足/同名衝突、経路間優先順位 | Product機能/Owner意味受理は再認定されない |
| Skill `SKILL.md`手順・Scripts・依存 | 脆弱性/Tool呼出し・許可path・実送出・再生試験 | 以前のTool挙動や権限 |
| CLI/MCP Tool signature/JSON/Output変更 | 使うSkillだけ入力出力互換・negative tests | 別Consumer/別Hostの有効性 |
| TEI意味/Model/Rule/Source/Target改版 | 影響を受けるClaim・生成/Business/再実行契約の既存Owner検証 | 旧生成/旧受理/旧Effect |
| SHO本文/テンプレート/KaTeX/SVG変更 | 引用出典・Render入力・説明・配布済固定版への影響を分離 | TEIモデルの意味受理 |
| SUI・SEIの開示／用途条件改訂 | Product内投影資格、外部問合せ、通知/未決の保存 | 過去に外部送信したbytesは取り消せない |
| EKI Task/Result/Provider改版 | 同一Attempt/実Body bytes/受理/Effectの追跡 | 結果不明の自動再試行 |
| Harness/Plugin/Profile入替 | 読込Skill exact path/hash、Tool発見・Host実効権限・Session Log・外向き通信 | 以前のHarnessへの受入資格 |

**局所再検証**は、明示的に依存関係が確認された範囲に限定する。未知の依存を「影響なし」としない。Deploy前固定manifestの記録は有用だが、実行するSkill/Tool/Provider bytesの**実同一性**を別途観測する。

## 7. 多数のSkillを増やすための製品横断ポートフォリオ

必要な代表Skillは入口であり、領域別のMethodや手順は自由に増やせる。大きなSkill一つへ全部の知識を入れるのではなく、**用途・対象・期待する証拠が異なる場合に分割**する。データ構造やDomain PluginとSkill数の間に1:1を強制しない。

- TEI：モデル再利用/合成、自己記述DSL、SQL構造/粒度、時間・組織・数学/単位/Topology、Java/.NET/WASM Target、多言語Conformance、外部Provider、テスト/Lean、論文からの設計、Headless UI。
- SEI：Method候補探索、Evidence Sufficiency/Question triage、人物や組織の暗黙要求の用途別Fit（人に関する機微情報は最小限）。
- SUI/CSW：仮説・反例・多解釈、非レビューの開示、自由な生成と意味編集、対象へのTarget-return。
- SHO/MMI：Source reference、C-01/T2再解決、文章/図表/式/KaTeXと文書固定版、アクセシビリティ、専門分野の説明。
- EKI：委任Profile、同一Task/Attempt/Outputの実送達・受理・取消、実OS SandboxとProvider効果。
- TAI：SCN-001の読取り連携、SCN-004の業務横断、SCN-005の生活支援、Skill発見・選択・統合、別Harness再開と実効果照合。ユーザーのQoL/負担は別の独立評価とする。

**優先実証**（新Skill評価はNOT RUN）：①MMI既存Skill vs Toolのみ、②TEI単体既存CUIからのProduct Skill試作、③SEI Claim診断とSHO文書へ用途別Projection、④TAI Skillのある／なしで同じ複数Product作業、⑤EKI mock成果物の同一Attempt引継ぎ、⑥機密・UI・DSHの負例、⑦複数Harnessの配布/再開。候補の探索は並行拡大、正式意味/権限/本番資格は各Ownerが保持。

## 8. Owner判断と停止条件

**Owner判断待ち**：製品入口Skillの正式名称・版表現、どのProduct/Methodを既定暗黙ロードするか、Skill script利用と署名/配布、技術能力の公開/非公開Profile、Handoffの最小参照、比較するHarness実環境、ProductionのAuthorityとRelease資格。

**停止条件**：存在しないToolの推測呼出し／別Product Rawの越境／同じ可視投影から全体Claimの断定／Skill更新のすり替え／AIが業務意味を自動受理／不明Taskの無条件retry／SDK/Pluginの存在からHostの動作保証／新共通Host・共通意味SSOTの先行導入。

関連する既存Owner：TAI #168/#74/#232/#234、TEI #2390/#2391/#2515/#2516/#2493、SEI #660/#677/#767、SUI #3275（既に修正PRが別途存在）／agent projection、SHO #1/#6・MMI #658/#672、EKI #407/#465。正式受理や実装の証拠は各Issueへ戻す。


---

<!-- 20261106-product-reader-before-skill-and-parser-safety -->
## 9. 2026-11-06：Product Readerの実在とParserの安全性をSkill配布・再資格化へ接続

**時点注記（2026-11-07）**：以下の本文・表に残る「H2/H3未実施」「SHO mainにReaderなし」「SHO #17 Draft/14件」は**2026-11-06当時の基線**。現在の限定観測と未達は次の§10を優先し、過去時点の証拠を消去・再解釈しない。

**直近Product証拠の非対称性**：[TEI Product Skill #2605](https://github.com/hat47x/tei-platform/issues/2605)はTAI側からも固定公開Source/実Go CLI/SourceIndexを限定実証済み（[TAI実CI #42107393245](https://github.com/hat47x/tai-pleroma/actions/runs/42107393245)）。外部HarnessのH2/H3は依然NOT RUN。対して[SHO #16 G1b](https://github.com/hat47x/sho-composer/issues/16)には実装候補[Draft #17](https://github.com/hat47x/sho-composer/pull/17)が追加され、限定実Reader／Disk CLIとUbuntu/Windows各14/14の[実CI #42109343155](https://github.com/hat47x/sho-composer/actions/runs/42109343155)が成立。**SHO mainへの統合・正式CLI/Parser採用は未了**。従来のDraft #12〜14はFixture/Python test-only CLI／MMI Rendererの別資格として扱う。[SHO #10](https://github.com/hat47x/sho-composer/issues/10)の`yi-sho-compose`を「Product CLI利用可能」「配布受理済み」に昇格させない。

### 適用に必要な資格を分離する（新共通State Schemaは採用しない）

| 資格／Owner | TEI先行の実観測 | SHO G1bの現在状態 |
| --- | --- | --- |
| Product read-only Tool実装／Product Owner | 指定公開Subjectで実CLIのCatalog/Inspect/ValidateをTAI CIから実読取済み | SHO mainのReaderは未統合。Draft #17では実Reader+Disk CLIが限定Ubuntu/Windows CI成功。MMIのCLI/ProbeをSHOの正式Toolへ読み替えない |
| Parser/Source consumption／Product Owner | SourceIndex artifact/definition refと独立Source bytesが同一Fixtureで一致 | Draft #17は実disk raw bytes・厳格UTF-8・SHA-256・Parser 14.3.3/lock/profile/限定Link occurrenceを観測。dirty buffer／全Grammar／永続Occurrence ID／精密byte spanは未立証 |
| Skill Package／TAI Release Owner | Product Skill文書はmainに存在、実外部H3 Loadは未観測 | SHO Skillは提案候補。Parser/Toolが無い場合でも文書候補の検証はできるが**実装済みSkillによるReader実行とは表示しない** |
| Harness invocation／TAI #168 | 先にTEI H2実Tool log 1 Session、その後H3実Loadと四Session比較 | Draft G1b候補は実GoでなくNode製品候補のDisk CLIまで確認。Owner採用とexact実契約固定後、必要があればSHO別TaskのH2/H3へ |
| Owner Meaning／SHO #4/#7・TEI #267 | CLI正常終了はMeaning/Owner受理ではない | Markdown Link/ReferenceのSyntax Projectionと著者Review、公開/納品、TEI連携Meaningは別資格 |

### G1b版・入力・失敗の最小Negative Qualification（SHOの既存Issueへ渡す）

- **SHO-PQ01（危険Parser版）**：同じMarkdown/`package.json`記載でも、実`lockfile`/`require.resolve`でロードした`markdown-it`のexact版がCVE-2026-111758影響域（14.1.0以上14.3.3未満、または15.0.0以上15.0.3未満）なら、当該Readerを安全性確認済みと公表しない。GitHub [GHSA-gfr2-rv44-r23c](https://github.com/advisories/GHSA-gfr2-rv44-r23c)の修正版は14.3.3／15.0.3。**修正版本体を使ったことだけで入力資源上限・DoS対策・OS非送信まで証明したとはしない**。
- **SHO-PQ02（Parser変更と見た目同一）**：14系と15系でraw MarkdownのLink occurrence・参照定義解決・見出し/List階層を独立Expectedと比較。同じLink件数・Rendered HTMLでも同じIndex/Source positionとは断定しない。Parser/profile/Optionsの無言fallbackを禁止。
- **SHO-PQ03（未検証のLinkやSource）**：code fence・raw HTML・未定義参照・裸URL・部分入力・誤字によるReader不発を「Linkなし／Sourceが存在しない」としない。実読み取り可否、Grammar scope、warning/unknownを分離する。
- **SHO-PQ04（配布Skillだけ存在）**：`yi-sho-compose`がHarnessに発見/LoadedされてもSHO Readerが無い・実参照Fileを消費していなければ`Product Reader invoked`は未成立。MMIの実Toolを代わりに用いたなら別Product/Toolの限定効果とラベルする。
- **SHO-PQ05（非公開ソース）**：ローカルでReaderがMarkdownを読めても外部LLMへの原byte/引用メタデータ送信は別Grant。Skill説明文やParser設定から外向き送信許可を付与しない。

**導入順**：TEIのH2 Tool-only初回セッションは既存[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)／[Runbook §19](first-real-skill-qualification-runbook-2026-11-02.md)のまま最優先。SHOは同時並行で[#16 G1b](https://github.com/hat47x/sho-composer/issues/16)の[Draft #17](https://github.com/hat47x/sho-composer/pull/17)実Runner/実Parser/独立Fixture #12をレビューし、未取得のParser14/15比較・脆弱入力資源上限・正式API受理を狭く検証。その後にSHO #10のProduct Skill評価を検討。TAI #74は配布資格の表示だけ、TAI #271は跨ProductのSource/Revision変更時の限定再資格化だけを担当。**この節は既存実装の証拠を正しく配置する設計追補で、新Parser/Reader/Skillや実Harness連携のコードは追加していない。**

**状態**：TEI公開CLI限定S1と、SHO Draft #17のReader候補（exact HEAD `b4176b0df6ac62b02b40108391d024336ed71d7b`／Ubuntu・Windows各14/14）が実観測済。実ロードParser 14.3.3はCVE-2026-111758の該当系列修正版であり、**Parser選定承認・敵対的入力のCPU/Memory保証・OS egressまでの安全性実証ではない**。SHO main統合・正式G1b受理、SHO Skill Install/Load/Tool invocation、TAI外部Harness実H2/H3、Product間文書納品・Owner受理はNOT RUN。


---

<!-- tai-sho-sui-plugin-first-qualification-20261107 -->
## 10. Plugin-firstとSUI→SHO実Markdown受渡しを、Product Skillの実資格へ接続する（2026-11-07）

### 10.1 TEI Plugin-firstは要求・静的Fit/Gapまで。Skill経由の実Provider消費は未達

[TEI main Plugin-first方式設計](https://github.com/hat47x/tei-platform/blob/main/plan/design/PLUGIN_FIRST_TOOLING_RUNTIME_DOGFOOD_2026-11.md)／[merged PR #3277](https://github.com/hat47x/tei-platform/pull/3277)で、Core以外を原則Pluginとし、CLI/StudioでのPlugin開発・利用を生成Application Runtimeのdogfoodingにする製品要求・移行順序が記載された。実ソース監査では、CLIが静的dispatch、Studio Bridgeが少数操作の固定実装、既存Plugin/Compositionが一般Tool Surfaceへ未接続。**Plugin-firstの設計がmainへ入ったことは、Tool実呼出しがPlugin Contract/Resolver/Conformanceで成立した証拠ではない**。

[TEI #3278](https://github.com/hat47x/tei-platform/issues/3278)／[#3279](https://github.com/hat47x/tei-platform/issues/3279)は原子的Traitをrequired（generated／Provider／manual-required等の履行義務）またはadvisoryに分け、Contract→実装Fulfillment→Evidenceへ接続する設計案。**Trait宣言≠履行済み≠実TargetでLoad/Invoke済み≠現Host Grant**をSkill選択時に独立確認する。TraitまたはPluginの全種類をTAI内に再定義せず、既存[TEI #951](https://github.com/hat47x/tei-platform/issues/951)と[#3267](https://github.com/hat47x/tei-platform/issues/3267)のexactなResolved Composition／BOM・Testを参照する。Contract違反や未実装義務が残る場合は、実Tool候補としての不適合理由を表示するだけで代替実行を捏造しない。

**導入順**：TEI #3277のD0棚卸し→D1実read-only Inspector/Model Catalogの一縦切り→Product Skillから当該Toolの実利用／Source・Reply完全性を確認→必要な場合だけStudio/生成Runtimeへ同一Contractの拡張。これは後続Groupであり、TAI #168の初回固定TEI H2/H3のTask/Skill/Tool Profileを変更しない。正式Plugin Surface Conformance、Target実Build、Trait Fulfillment、Owner採用はNOT RUN。

### 10.2 SUI→SHO：同一期待byteのProduct別CIはPASS、実同一File HandoffはSKIP

[SUI Draft #3397](https://github.com/hat47x/sui-sensemaking/pull/3397)の実buildContextProjection→renderReadOnlyMarkdownDraftは、選択された公開・reviewed・非hold Cardから**通常Markdown 354 raw UTF-8 bytes**（SHA-256 7fd6fde2…c171cd）を生成。元CardのSource/ID、Island/Edge、秘匿件数、OKFの出典/検証を含めず、未信頼本文の疑似リンクをEscapeする。[SUI CI #42352776477](https://github.com/hat47x/sui-sensemaking/actions/runs/42352776477)で固定Expectedとの限定一致を確認。

[SHO mainのG1b Reader](https://github.com/hat47x/sho-composer/blob/main/src/g1b-reader.cjs)／[CLI](https://github.com/hat47x/sho-composer/blob/main/bin/sho-inspect.cjs)は実コードとして存在する（旧#17はClosed/Unmerged。**main存在と正式公開API/Owner受理は別**）。[SHO Draft #21](https://github.com/hat47x/sho-composer/pull/21)の別FixtureとReaderでは同一期待354 byte／Parser markdown-it@14.3.3／link_open=0／unresolved reference未評価を実照合。初回Windows CIはCRLF checkoutで**354→368 byteのRaw不一致**。合成FixtureだけLFを固定し、[SHO CI #42353651398](https://github.com/hat47x/sho-composer/actions/runs/42353651398)の両OS各18/18 PASSへ改善（著者文書全体のLF正規化はしない）。

**次のExitはまだ実施していない**：両製品のopt-in環境変数 SUI_SHO_P0_OUTPUT／SHO_SUI_P0_INPUT で**SUIの実書出し1 File→SHO実sho-inspectの同じFileへのRead**を連続実行し、SUI実生成Raw/実path・SHO実受領Raw・SHA/mtime不変・各HEAD・Parser/結果coverageを**同一Attempt**に結ぶ。[SHO CI #42370393890](https://github.com/hat47x/sho-composer/actions/runs/42370393890)は各OS18 PASS/1 SKIPで、**その1件が実Handoff試験**。CIの全体緑をHandoff成功へ昇格しない。SUI/SHOのProduct Ownerは[SUI #3391](https://github.com/hat47x/sui-sensemaking/issues/3391)／[SHO #16](https://github.com/hat47x/sho-composer/issues/16)、後続のWriter Save/RestartはSHO #4、TAI Activity Handoffは[#271](https://github.com/hat47x/tai-pleroma/issues/271)。

**二次配布・Skill資格の停止線**：Raw digest一致やlink_open=0は元Sourceの不存在、SUI Island/Tree意味同値、OKF/SEI認識十分性、SHO文書の保存済み状態ではない。実Product間1 File ReadがPASSしても、yi-sho-composeのHarness install/load・実Tool invoke、外部LLMへ送るDisclosure/current Recipient Grant、Writerの保存後Reader/再開は**別試験**。SHO単独で必要なことはSHO単独で検証し、TAI常時介在・新Document Core/Parser/Host/Transport/Registryを前提にしない。

**YIC/TAI実証の順序**：初回TEI H2/H3の実OS Read-deny→G1通常モデル入力/暗黙Context/Session Log→G2 Tool Reply完全性→新4独立Session（比較適格0/4）を変更しない。SUI→SHOの1 Fileは**並行する小さいProduct間試験**として実施可能だが、TAI #271のSCN-001 B0/B1/B2の実Task価値・Skillの増分効果・正式Source Meaning受理へ自動昇格しない。


---

<!-- tai-interoperability-tei-shared-app-api-mcp-reference-20261108 -->
## 10.3 TEI共通アプリケーションAPIとMCP参照Adapterを、Skillの実Tool資格に接続する（2026-11-08）

[TEI採用ADR-0048](https://github.com/hat47x/tei-platform/blob/main/plan/adr/0048-shared-application-api-and-transport-adapters.md)は、CLI／MCP／HTTP／Web／Desktopを**同じ型付きアプリケーション操作のAdapter**とし、操作ID・Request/Result/Failure/Source Scope・効果・版を既存Ownerから取得する方針。HTTPサーバーや一つの認証方式を全入口の必須Hostにしない。既存のCLI-firstとGo単一バイナリ・外部Hostへの導出を維持する。これは**採用済み設計**だが、全入口実装・同値試験の完了ではない。

### 10.3.1 先行MCPの実在と、何を実測したか

[TEI merged #3403](https://github.com/hat47x/tei-platform/pull/3403)で、mainの[read-only MCP参照Adapter](https://github.com/hat47x/tei-platform/blob/main/tools/reference-mcp-readonly-adapter/main.go)が実在する。起動時に固定Workspaceを指定するstdio JSON-RPC Adapterで、model catalog／inspect／trace／validateの**4 Toolだけ**を既存internal/operationsへ渡す。モデルからpath/rootを書き換えるSchemaではなく、受理・書込み・Grantの操作は公開しない。PRの限定実測では、同じ公開Workspaceの各操作から抜き出したFingerprint・主要値・schemaVersionの対照で不一致0を報告。**その部分集合一致を、全JSON・失敗分類・Source/Host隔離・外部Harness全受領の完全同値へ昇格しない**。その後[TEI merged #3458](https://github.com/hat47x/tei-platform/pull/3458)でvalidateの意味失敗・Load失敗とCLI/MCP診断の限定パリティは進んだが、全Toolの完全同値は依然未実証。旧[TEI #3400](https://github.com/hat47x/tei-platform/issues/3400)の「当時MCP入口なし」は歴史的Source版の観測であり、現在mainに薄いReferenceが存在することと矛盾しない。

### 10.3.2 TAI/YICが参照する適合条件と次の最小差分

| 現行Evidence | Skill選択・Handoffへの利用 | 未成立の主張 |
| --- | --- | --- |
| 採用ADR-0048＋4 read-only Operation | 同じ目的のRequest/Result/Failureの正本は**TEI操作契約**とし、CLI/MCP tool名・JSON-RPC numeric code・CLI exitをAdapter投影として扱う | CLI/MCP/HTTP/IPCを含む実Full Parity、実Toolを使った同一Harness Trial |
| 参照MCP／部分値一致 | **存在確認済み、限定Tool呼出しのProduct候補**。実Tool Result Bytes・Protocol/Schema版・Workspace固定・Source Index/World Fingerprint・diagnosticsを、Task/Attemptで別に照合 | 書込み可能／Host認可済み／全Sourceがモデルに届いた／同じエラーを全入口が等しく判定 |
| [TEI merged #3458](https://github.com/hat47x/tei-platform/pull/3458)のvalidate限定修正／[#3420](https://github.com/hat47x/tei-platform/issues/3420)の残余 | 実CLIと実参照MCPを直接起動し、正常／Source Load失敗／重複宣言の3系列で共通WorkspaceValidationReport・ok・isError・文字列failure.code／CLI exitを限定確認。旧MCPのisError:false偽成功は**修正済み負例**として保持 | 未知欄・型違い・NULL・上限・全Protocol、catalog/inspect/trace全失敗、全CLI/MCP parity、CAPI-1/2/3/4完成 |
| [TEI #3422](https://github.com/hat47x/tei-platform/issues/3422)の後続Effect | read-only成功、正常Result、試験用allow-allを現在のwrite Grant/Owner Accepted Meaningへ移さない。期限切れ/通信断はRollback確証でない | 異入口からの実Mutation同値、未知Effectの安全Retry、本番Host資格 |

**実行順序**：TEI #1158／#3419が共通4操作の型を固定→#3420が実CLI/stdio MCPで成功・失敗・NULL・未知欄／Workspace拒否を同条件比較→必要なTaskのみに#3421のHTTP/IPC、#3422の作用を追加。YICは既存X01/X03/X05/X06を用い、実Productが返した操作資格を消費するだけで、第二API仕様・Schema変換器・Runner・認証Policy正本を持たない。[YIC適合計画 §26](https://github.com/hat47x/tai-pleroma/blob/docs/yic-skill-crosslane-qualification-20261106/docs/yi-constellation/skill-crosslane-qualification-and-order-2026-11-06.md)とTAI #271の現在Grant/受領資格へ参照で渡す。

**初回SK-02を固定**：既存[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)のH2→H3→H3→H2は**固定TEI pin＋CLI Tool／H3 Skill**の比較であって、今回新設されたMCP Adapterを途中から混ぜない。比較適格0/4、G0 OS実Read拒否→G1実Sink/Egress→G2完全Tool Reply→事前割付独立4 Sessionのまま。実Full CLI/MCP parity、実Host＋外部Harness／MCP接続、正式Product APIとしてのOwner採用、横断Activityの増分価値は**NOT RUN**。

<!-- tai-harness-incremental-buy-vs-build-axes-20261108 -->
## 11. 既存Harness／YI Skill／薄いAdapter／独自Loopの増分価値を、製品価値試験と分離する（2026-11-08）

他チャットで検討中の「外部HarnessのPlugin拡張によりYI独自Harnessの投資価値が変わる」という問いを、既存[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)のSkill資格、[#422](https://github.com/hat47x/tai-pleroma/issues/422)のB0/B1/B2 User Job、[TEI merged #3487](https://github.com/hat47x/tei-platform/pull/3487)の共通API/独自Harness価値検証へ接続する。**外部Harnessの製品仕様全体や費用優位を今回独立に実測したわけではない**ため、TEIのDocs合意や比較候補をTAIの新Runtime採用へ変換しない。

### 11.1 「B0/B1/B2」が二種類あることを明示する

| 比較の問い | B0 | B1 | B2 |
| --- | --- | --- | --- |
| **Value試験（TAI #422/Activity §18）** | 人間／既存の素朴な作業手順 | Product単体で完了するJob | TAI Activity連携を加えたときのJob |
| **Harness試験（TEI #3487）** | 決定的CLI/共通API | 外部HarnessでSkillなし／ありの差を検証 | 外部Harnessの不足だけを埋める薄いAdapter |

**[TAI Draft #423](https://github.com/hat47x/tai-pleroma/pull/423)の既存HV-0〜HV-4候補**は独自Harness投資判断の詳細計画であり、この§11はその実行資格・用語衝突をSK-02計画へ接続するもの。HV番号を別のRunner/Scoreや正式公開Schemaとして作り直さない。同じ「B1」を一つのTrial/Value Countへ混ぜない。Trialには`comparisonAxis=value|harness`（**実験記録上の区別であり公開Schema追加ではない**）、Task/参加者、実Source/版、Actual Delivery、独立Expected、費用・観測可能なEffectを紐づける。前者は**TAIを足す必要性**、後者は**外部Harnessに加えた実装の必要性**を評価する。既存SK-02のH2/H3はHarness B1内部のSkill差であり、H2/H3結果からValue B2の価値や独自Harness採否を直接推定しない。決定的APIのB0に文章生成能力がないことを不合格とせず、Source/Contractの正確さ・拒否の正しさ・費用の基準として観測する。

### 11.2 増分実装の候補と採用停止線

1. **既存CLI／共通Application API**：採用済み[TEI ADR-0048](https://github.com/hat47x/tei-platform/blob/main/plan/adr/0048-shared-application-api-and-transport-adapters.md)を使い、実Source/Design Required/ReplyをProduct内部で確認。新しいHarness/Registryは不要。
2. **既存外部Harness＋YI Product Skill**：まずH2/H3のOS強制Read境界・実Tool全byte配送・Skill実Load・独立採点が成立するか。現時点はH3 Root/Referenceの歴史的実Loadがあるが、**正式比較適格0/4**。H2/H3の旧4Sessionの数字を費用改善・採用証拠にしない。
3. **薄いTransport／Plugin Adapter**：必要な`inspect/trace/validate`等のCurrent Sourceと限定Resultを既存Product操作から返す。実際に外部Harnessで既存CLI Toolより不足が減るときだけ採用。Productが持つOriginal Source、Meaning、Authorization、Provider EffectはAdapterの新正本にしない。
4. **独自Agent Loop/Host**：上記1〜3で解消できない**繰返し再現した問題**（用途別根拠閉包・実時間制約・非開示・部分効果の復旧など）があり、独立した複数Task/Domainで品質・費用・運用負担・隔離の**純増益**が確認できた場合にのみ検討。外部Harnessが拡張可能だから必ず十分、または医療等の高リスク領域だから独自Loop必須とは決めない。高リスクの実Authority/Owner採用は個別Domain判断。

共通評価欄は、業務Taskの正答／重要な誤判断／`unknown`の保持、実Consumer全byte受領、OS/Tool/Log/Networkの開示境界、Userに見える負担（手戻り・再調査・停止）、端末実行時間、実料金・維持費とする。改善値が確定していない段階でROIを定量値として作らない。**同じTask/Source/Host Profileを維持し、追加した一要素だけを比較**する。Skill/Adapter/Loopを同時に入れ替えない。

### 11.3 Transport実装の現在地とPluginの実効果を分ける

**MCPの実装状態とCLIとの限定一致は前節§10.3を正本**とする。ここではその[TEI参照Adapter](https://github.com/hat47x/tei-platform/pull/3403)を、既存外部HarnessでCLIよりどれだけ負担・誤解釈を減らせるかという**増分価値候補**としてのみ扱う。正式公開MCP ABI/DSH実接続・Consent/Grant・モデル全byte受領は未確認。[SK-02 Runbook §24.17](first-real-skill-qualification-runbook-2026-11-02.md)のとおり初回は固定CLI、MCPは後続の別Transport比較とする。

[TEI merged #3363](https://github.com/hat47x/tei-platform/pull/3363)の参照能力表では、公開Workspaceの24 Binding中22 selected、2 missing。ただしこれは**宣言の解決**であり、実Plugin Artifact/Load/Invoke/Client Deliveryではない。[TEI merged #3474](https://github.com/hat47x/tei-platform/pull/3474)の読取調査では、部署・環境Bindingが計画に反映されても、参照実行は固定Capabilityを直接呼ぶ経路が残り、`routing.Router`も非試験実行で構築されていなかった。断絶はPoC段階の意図的分離かもしれず、即「不具合」とは呼ばない。


<!-- tai-harness-d1-selected-go-consumers-and-synthetic-host-20261108 -->

**11月8日に進んだ「実Call」の限界**：[TEI merged #3381](https://github.com/hat47x/tei-platform/pull/3381)では、既存Compositionのexact-selected Provider BとHost登録Go Bを`inspect`の型付き入口へ接続したうえ、CLI注入HelperとStudio Host APIの**6 Subject×2＝12回のin-process Go call-site対照**をmainへ統合した。B→A誤登録、Provider scope/contract/digest違い、Host撤回、Epoch失効や不適合Resultの拒否があるため、**参照Go CallがBを実際に呼んだことは限定観測**できる。これは前の「selectedのみ」の一部を前進させる重要な区別。ただし通常`cmd/tei/main.go`のユーザーCLI dispatchはBuiltin経路のままで、実Wails Studio BridgeもBをProduction配線していない。Host登録の合成digestは**実配布Binary/Plugin Code fingerprint/署名/現在Grantの証拠ではない**。旧統合候補[#3517](https://github.com/hat47x/tei-platform/pull/3517)は重複を避けてunmerged close、D1 S2の通常起動はTEI #1251の次段とする。

**別Runtimeの意味的な停止線**：[TEI merged #3516](https://github.com/hat47x/tei-platform/pull/3516)は実Reference Go HTTP HostからCanonical認可→Driver→**合成Adapter Callback**の正例/拒否7ケースを検証した。Hostの実Callback到達であって実DB Commit/外部Plugin Effect/クライアント完全受領ではない。[TEI merged #3520](https://github.com/hat47x/tei-platform/pull/3520)はDesign/Provider申告/統計Window/Reply parts/Disclosureを**Synthetic入力だけで**独立19件判別した。JSONの`providerInvoked=B`だけでHostのB実Callを証明したり、統計上の改善を業務性能改善と呼んだりしない。これらの限定Witnessは、各Ownerが先行する**実Plugin Call→実Query/Provider Read→実Consumer Delivery→独立Benchmark**の必要な区間で再利用し、TAIハーネスへ新Hook/Optimizer/Hostを作る根拠にはしない。

必要な1 Pluginの資格は **Declared → Environment-selected → Actual Binary/Provider Included → 実Loaded/Invoked → Current Grant/Scope → Resultを実Consumerが受領 → Effectが必要なら独立Read/Receipt** のうち、Taskが要求する地点までに限定する。「22 selected＝22動く」「CLI/MCP値一致＝Plugin実Invoke」「Consumerが見た＝Owner Meaning採用」を禁ずる。実Inspector一つのread-only Load/Invokeを既存TEI Owner #951/#1251へ委ね、別のTAI Plugin Registry/Runner/Policy Engineを追加しない。

### 11.4 SHOの限定保存を独自Harnessの前提にしない

SHO [Draft #25](https://github.com/hat47x/sho-composer/pull/25)では、新規別名Working Copyを実Fileへ保存し、別Openで読んだRaw bytesを照合する**test-only** W1を両OS CIで限定実証。Source/Output File Identity変化や同byte A→B→Aを独立反例にしたが、正式Writer・安全な本番Save/no-op write0・原子的Publish・SUI実H1・Owner受理は未実証。この段階のP0/P1 Producer→Consumer／G2-W1は、外部AI Harnessの常時介在なしで進められる。B1 Product単独でUser Jobが満たされればTAIの常時仲介も独自Loopも不要。

**優先順**：初回SK-02比較適格1 H2→同一試験Groupの独立4 Sessionを先に成立させる。SHO/SUI/Plugin実Invoke/独自Loopは各Ownerの並行Gateで進め、初回の固定Task/Tool/Skill Profileへ詰め込まない。ここで新外部Harness実試行・ROI測定・実Provider・正式Owner受理はNOT RUN。

<!-- tai-plugin-declaration-consumer-actual-reach-20261109 -->
### 11.5 宣言の解決は実行ではない――6種のBindingとHook結末名の現在地（2026-11-09）

[TEI merged #3757](https://github.com/hat47x/tei-platform/pull/3757)のread-only製品コード調査では、Environmentの6種類の宣言のうち、**非試験の解決まで届くものが3種類、実行まで届くものが1種類**と整理された。特に`ObservationProviders`／`EvidenceProviders`は実`cmd/tei/main.go`からBindingを解決する一方、`observation.Router`／`evidence.Router`の組立ては試験のみで、Productの`Observe`／`Collect`呼出しは観測されていない。参照コードの解決・試験Router・実Product Provider Invocationを一括して「Pluginが動いた」と数えない。C-1〜C-4でどの宣言を実行へ繋ぐべきかはTEI Ownerの未決判断であり、TAIに全Bindingを強制配線する理由ではない。

[TEI merged #3761](https://github.com/hat47x/tei-platform/pull/3761)は、Hookが返す不成立`outcome`名を`internal/hook`境界で検査し、宣言外なら`HOOK_OUTCOME_UNDECLARED`とする6試験を追加した。**境界内部で語彙が守られる**ことは前進だが、実Pluginは未接続であり、CLI JSON/別Process/外部Transportへこの検査が及ぶことも未確認。名前の正当性、実Plugin呼出し、失敗の原因、実副作用を別資格とする。名前が空でも理由付き不成立が合法なため、空値を一律欠落扱いしない。

[TEI merged #3760](https://github.com/hat47x/tei-platform/pull/3760)では、明示したcatalog/digest/source-rootから`tei self-build` entryがin-processで計画を導き、参照child経路と同一`planFingerprint`を出した。実観測は`ok=true`でも**`qualified=false`／`l2bClaimed=false`**。同じ計画Hash、Receipt形式、Artifact Bindingの一致を、catalogの真正性、Runtime Authority、実配備の成功へ昇格させない。Skill/PluginがこのSelf-build経路を利用する際も、入力Source・導出主体・Trust・Tool/Target実行・受領を分ける。

**実装順**：既存TEI OwnerのProduct実配線が必要なCapabilityを一つだけ選び、Declared→Resolved→Router/Entry Constructed→実Invoked→結果受領のうち未到達箇所を**単一Consumer**で検証する。Hookの外部境界やSelf-buildのL2-bはそれぞれ別Gate。TAI側に新Router/Hook Registry/自己ビルドHostを設けず、初回SK-02 H2/H3の固定Tool Profileへ追加しない。実Provider/Pluginの全経路、外部Hook outcome、正式L2-b、Owner受理はNOT RUN。

<!-- tai-studio-element-directed-ai-harness-20261109 -->
### 11.6 TEI Studioの要素選択をAI指示の主入口にする――Harnessは交換可能な実行器（2026-11-09）

**価値仮説**：汎用Chatからモデル全体を説明させるより、TEI Studioの図・表・ツリー・プロパティ・CRUD交点・Function・SQL・診断・試験結果を**ユーザーが直接選択して指示する**方が、指示対象の同定、必要Contextの最小化、変更範囲の限定、検証結果への往復に優れる。特に大きなData/Function/Business三要素図では、**全体図の現在地を保ったまま局所選択→AI提案→差分確認→同じ位置へ復帰**を優先する。これは[TEI merged #3847](https://github.com/hat47x/tei-platform/pull/3847)がRQ-036/三要素Method §19.8に追加したG1〜G7とMAP-17〜23（全件NOT RUN）を**AI指示の入口として利用する案**であり、別の図面正本やTEI Studio実装済み機能の主張ではない。

**境界と最小データ**：選択UIは`ModelElementId/Kind`、`Source/Model Revision`、選択した表現上の`view/selection/span`、`Audience/Grant`、要求する`Intent`、近傍参照の範囲と欠落を、既存Modeler/ADR-0048 Application APIから読み出す。UI座標・ハイライト・展開状態は**Presentation state**でありAccepted Meaning/業務Keyへ昇格させない。選択対象が変更・移動・削除されていたら再解決して停止／再確認し、**古い座標から別要素を黙って編集しない**。要素のRole/Meaning/Action/ContextはAIの候補として提示できるが、Accepted Meaning・Grant・実Event・業務副作用を自動確定しない。

| 操作段階 | 正本／担当 | 必要な否定試験 |
| --- | --- | --- |
| Select & Inspect | TEI Modeler＋既存CLI/API/MCP read-only、図の現在地・近傍・出典 | 同名別ID、削除済みID、旧Revision、表示上の非公開部分、図と構造化表現の不一致 |
| AI Instruction & Preview | 外部Harness（DSH等）＋YI Skill、対象限定Context、提案Patch | 非選択要素への変更、Context過送出、未知Field/Sourceを捏造、複数選択の曖昧な作用範囲 |
| Preflight & Apply | TEIの既存型付きApplication API/Host/Provider/現在Grant | 意味受理なし、旧Revision、権限なし、無関係要素への副作用、partial write |
| Post-check & Return | TEIの既存差分・Driver/Receipt・図面/CRUDクロス参照 | UI表示成功≠保存成功、Build PASS≠意味保持、Receipt≠実Effect、図面上の現在地喪失 |

**構成選択**：DSHのACP/SDK/Headlessなどの入口は**接続候補**として評価し、TEI StudioにDSH固有のSession Store/Agent Loopを組み込むことを前提にしない。まず外部Harnessを**交換可能なSidecar/Adapter**として、Studio Selection→既存Application APIでContext取得→Skill/Harnessへ最小Context→提案をTEI側Preflightへ戻す細い経路を比較する。DSHのサービス契約・利用規約・組織向け配布／モデル接続条件は別に確認し、定額Consumer契約が任意の自動API/ヘッドレス利用を許すとは推定しない。企業向けにはモデル選択・通信先・機密データの送信範囲・ローカル処理・監査を**Harnessから独立に設定可能**にする。特定Harnessの名称や出自を採用必須条件にしない。

**最小価値試験（新しい必須Gateを増やさない）**：同じTEI Function/Diagramの局所変更を、B0=Studio手動、B1=Studio+外部Harness汎用指示、B2=Studio選択要素からの直接AI指示で比較する。対象特定までの時間、投入Context byte、無関係差分数、正しいSource/Model/Revisionへの帰着、独立Expected/Ownerレビュー、総Cost、失敗時の回復を記録。**B2がB1に対して実測で改善した範囲だけ**製品要件へ昇格する。初回TAI #168のH2/H3固定Skill比較と混ぜない。TEIの実UI Selection/Modeler Bridge/外部Harness接続/企業認可/実業務書込/Owner受理はNOT RUN。実装OwnerはTEI RQ-036/ADR-0048/既存Studio Issue、TAIは価値比較とSkill契約のみ。

<!-- tai-shared-harness-session-product-ui-kj-csw-20261109 -->
### 11.7 SEI/SUI/TEI/CSWを跨ぐSessionを主体にし、各UIへHarnessを内蔵しない（2026-11-09）

**§11.6の精密化**：TEI Studioの選択要素からAIへ指示する機能は有力だが、**TEI StudioがHarnessの所有者になる**という意味ではない。利用者が一つのHarness Activity/Sessionを継続し、TEI Modeler、SUI Canvas、SEIの判断レビュー、CSWの知識操作UIを必要に応じて切り替える。各Product UIは自分の選択・表示・編集と既存APIを所有し、**Harness Sessionは外部の交換可能な実行環境**が保持する。各製品への常駐Agent Loop、Session Store、共通Host、中央Registry、全製品同時接続は要求しない。TEI UIを使わないCLI/MCP/Headless経路も等価な第一級入口として残す。

**Session共有の意味**は「同じActivity IDを各製品が持つ」ことではなく、**許可された目的・履歴・未解決の問い・検証状態を、異なるProductへ再提示できること**。共有してよいのは再解決可能な参照と明示的な要約／選択的なEvidenceだけ。元Source全量・非公開Canvas・SEIの未受理判断・CSWの探索メモ・認可Tokenを暗黙複製しない。切替時には`Product/SourceRef/Revision`、`SelectedElement/Scope`、`Purpose/Audience/Disclosure/Grant`、`Intent/Unresolved Questions`、`Evidence References + Status`、`Return Location`を、**既存Product APIで現在の権限と鮮度を再確認して**渡す。これは概念上の最小Handoff項目であり、共通Schema/Storeの採用決定ではない。UI座標やハイライトはPresentation stateであり、ProductのAccepted Meaningへ逆流させない。

**CSW×SUIのKJ法的協調**は、Harnessが推論と会話の連続性を支え、SUIがCard/Island/Canvasの配置・関係・履歴・共同操作を正本として保持し、CSWが視点の切替・問いの生成・仮説比較を提供する形を第一候補とする。たとえばSUI上のCard群を選択→CSWで分類軸を複数提案→SUIで島の再配置案を**Preview**→人間が採否を選ぶ→TEIで必要な構造化モデル候補を作る→SEIで根拠付き判断を検討する。KJ法的な探索は**島の配置が即Accepted Meaningとなる操作ではない**。元Cardの引用位置・Island所属・非公開RelationはSUI投影で失われ得るため、§27の非単射/非公開境界を維持し、公開Projectionだけから原配置を逆生成しない。CSW固有の語彙を全Productに必須化せず、CSWなしでもSUIの通常操作を完結できる。

| 切替反例 | 必要な動作／停止条件 |
| --- | --- |
| TEIで選択したFunctionをSUIへ移動、元Model Revisionが変更 | 選択の現在性を再解決し、旧Revisionの自動Patchを停止 |
| SUIの非公開Island/RelationをCSWに要求 | 現Audience/Grantで許された範囲のみ取得し、未公開を不存在としない |
| CSWの仮説がSEIのRecommendationへ渡る | 仮説・根拠候補・Owner受理済み意味を区別し、決定として自動採用しない |
| Sessionがfork/再開される | 親Contextの継承と実送出を別に観測し、独立Sessionとは数えない（Runbook §24.18） |
| Session Logに巨大event、画面上は作業継続 | 保存／送出／モデル受領を分ける（Runbook §24.19） |
| UIでPreview成功、TEI/EKIの実Effectが不明 | Preview/Delivery/Commit/Receiptを分離し、未知Effectを自動再実行しない |

**価値比較の順序**：P0=各Product単独のUI/CLIで同じJobを完結、P1=同一外部Harness Sessionで2製品を明示的に切替、P2=CSW＋SUIのCard/Island協調で創造的探索を行う。P1は参照の再解決、Context byte、対象同定誤り、移動前後の作業再開、不要な送出、失敗時の復帰をP0と比較。P2は候補数でなく**異なる分類軸、反例の発見、元Cardへの遡及、採否の負担**をP1と比較する。CSWの認知効果とHarnessのSession継続効果を混同しない。**利用者がP0で十分ならHarnessを必須化しない**。

**実装Owner/停止線**：各UI/Source/Grantは各Product Owner、TAIは薄いSkill/Handoffと比較方法、Harnessは既存DSH等の交換可能な外部実行器。まずTEI↔SUIのread-only選択参照で同一Sessionを再開できるか検証し、その後CSW↔SUIのCard/Island Preview、最後にTEI書込やSEI判断へ段階拡張する。新しい全製品共通Session DB/AuthorityやYI独自Agent Loopを先行しない。**実Product間Session共有、SUI実Canvas連携、CSW認知比較、Owner受理はNOT RUN**。初回TAI #168のH2/H3固定4 Sessionには混入しない。

<!-- tai-harness-20261112-selection-and-session-qualification -->
### 11.8 複数UIにまたがる選択・補正・再資格化を実装に落とす（2026-11-12：設計と受入案）

**結論**：前節の「外部Harnessを製品UIで共有」を、全Productで同一Agent Loop／同一画面／同一意味Storeを持つ構成に解釈しない。各UIは**精密な対象選択を生成・表示・補正できる独立したProduct Client**であり、外部Harnessは現在のActivityを扱う*交換可能な実行器*。利用者がプロンプトで対象を選びGUIで補正する場合も、GUIで先に範囲選択しプロンプトで絞る場合も、最終的には各Productが解決した**型付きの現在対象参照**を用いる。CLI/CUI・AI OFF経路を第二級にしない。

**今回の成熟差分**はSelectionの正本/状態機械や新共有Schemaを発明することではなく、既存の[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)（Activity、再資格化）、[#168](https://github.com/hat47x/tai-pleroma/issues/168)（Harness実Tool/Skill、Capability）、[#232](https://github.com/hat47x/tai-pleroma/issues/232)（Host隔離・Disclosure）と各Productの既存Projectionに、実装時に検証すべき**対象束縛・再解決・同時性・送出・結果**を接続すること。前段H2/H3の実Source/Tool/隔離検証は優先のまま、UI案を初回4 Sessionの追加Blockingにしない。

#### 11.8.1 活動と選択の五つの非同一性

| 対象 | 保持する情報の最小候補 | 同一視してはいけないもの |
| --- | --- | --- |
| **Activity / Task** | 利用者が進めたい目的、用途、未決、必要なProduct参照 | 会話履歴、独立の実施権限 |
| **Harness Session** | Harness/Version、実Session ID、Tool/Skill実受領、実送出範囲 | Activity全体、他製品の現在Grant |
| **Product Focus / Pinned Selection** | Product/Workspace/Document、View occurrence、Element kind/安定ID、SourceとViewの版、明示選択条件と補正、対象を固定した意図 | フォーカス、画面XY、同名ラベル、現在存在するという保証 |
| **Context Projection / Disclosure** | 用途/相手/許可済み範囲、取得した項目と未取得、送出予定byte/参照、Source/鮮度/可視性 | 元World全体、Sourceにない根拠、全件完全性 |
| **Operation / Result** | Product/Hostが実行したRequest/Attempt、現在認可、実Receipt/独立観測またはUnknown | Selection、AI案、Tool ACK、実業務Effect |

Pinned Selectionは**入力操作中のUI focusから独立**する。Esc・別ウィンドウ・編集カーソル移動・Chat入力で誤って解除しない。Pinと表示Highlightは別、Unpin/再束縛は明示操作。Pin後のSource移動、同名別対象、削除、A→B→A、Role/Grant変更では、古い参照と新Candidateを提示して現在版で再解決する。Pinそのものが永続的な資料IdentityやMeaning受理とはならない。TEI Studioの所有計画は[TEI #1824](https://github.com/hat47x/tei-platform/issues/1824)/[#1124](https://github.com/hat47x/tei-platform/issues/1124)、構造を跨ぐUI制御は[#2391](https://github.com/hat47x/tei-platform/issues/2391)に委譲。

#### 11.8.2 自然言語選択と空間補正は、同じ操作結果で比較する

- **自然言語→GUI**：Productが許可済み範囲で解決した候補集合Qと、検索条件・取得Coverageを示す。人はCanvasの囲み、追加A、除外E、関係/比較役割を補正し、最終候補集合 `S=(Q−E)∪A` を次の指示へ渡す。Qは可視・実取得範囲に限り、非公開/未探索を「候補なし」と言わない。
- **GUI→自然言語**：人の明示的な囲み/複数選択をRefとして固定し、「この範囲で、時点が異なるものだけ」等の追加条件をProduct側のread-only解決で評価する。LLMの内部推測やCanvasの座標だけで隠れたObject IDを発明しない。
- **動的条件と固定集合**：`Predicate`を次に実行した場合の集合と、時点rで実解決した安定ID集合を区別する。人が修正したE/Aを無断で動的集合へ再適用しない。編集・大量操作時は対象候補を固定し、現在Grant/Source/対象存在を実行直前に再確認する。
- **多様な関係**：SUIのCard/Island/affiliation/Canvas x,y/非階層Relation/仮Tree、TEIの三視点Model/CRUD交点、SEIのClaim/Decision、EKIのWorker/Grant/Taskは固有の意味で扱う。SUI [#3430](https://github.com/hat47x/sui-sensemaking/issues/3430)/[#3431](https://github.com/hat47x/sui-sensemaking/issues/3431)の構造Draftの区別をSelection共通型で潰さない。近接＝因果、CSW仮の束＝採用済みMeaning、SUI Island＝TEI組織Membershipを禁止推論とする。
- **提案と作用**：AI/CSWの分類・表札・配置は複数候補としてPreview。選択・提示・利用者補正・明示保存・人のReview・実Host Action/Receiptは別。undoは未保存UI操作と、保存済みCAS条件付き逆変更を分ける（SUI #3399）。人の修正理由をAIが後付けしない。

#### 11.8.3 同一Sessionの二画面接続と、別Sessionへの再開の判定

- **Live shared Session**：Harnessが*実際に*複数Clientによる同一Sessionのattach/復帰を許すかを版・Transport単位で確認。二画面から同時指示を送る場合、Task/Message/Selection/Source revisionに返答を束縛し、遅着を別画面の現在状態へ貼り付けない。多重Writer不対応ならunsupportedと表示し、強制的な偽Session共有をしない。
- **Activity Handoff**：Live attach不能なら、既存TAI #271の用途限定Ref/未決/Unknownを別Sessionへ渡す。Task再開は可能でも、**同じ会話Sessionを継続した証拠ではない**。Handoffは旧Tool Resultや旧Grantを承認済み・現在利用可能へ格上げしない。
- **機密境界**：同一Sessionの過去Contextに別製品の秘密があれば、後続画面で「限定投影しか送らない」だけではモデル内に残った秘密を隔離できない。Audience/Principal/Host trust boundaryが変わる場合は適切な隔離Sessionへ分岐し、許可Refのみを新Sessionで取得する。共有Session優先は権限分離より下位。OS/Host読取拒否、Tool args/Reply、Session Log、送信先Networkまで[#232](https://github.com/hat47x/tai-pleroma/issues/232)で評価する。
- **過去と現在**：TEI Sourceのworld fingerprint一致はDB Rowset/RLS/current Grantの不変証拠ではない。[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)の2026-11-11の実PG試験は、同worldで行・可視0件が変化し得ることを示した。Provider実Read/Source Snapshot/Coverageが取れないときの「0件」は不在Claimへ昇格しない。

#### 11.8.4 初期1枚の実験票（後続の受入。実施は全てNOT RUN）

既存[TAI #271 ASV-08〜12](https://github.com/hat47x/tai-pleroma/issues/271#issuecomment-6784691025)／[SUI #3400](https://github.com/hat47x/sui-sensemaking/issues/3400)の独立Expectedを再利用し、新しい巨大共通Schemaや中央Session Runnerを追加しない。

| 段階 | 実際に固定するもの／期待結果 | 不適格・停止条件 |
| --- | --- | --- |
| **P0 公開Source・read-only** | 一つの許可済み公開SUI投影＋TEI read-only SubjectについてSource/Version/Disclosure/Tool実能力を確定。実際のSUI `context-projection.v1`は許可済みCard/Island/Relation/Countまでで、元Source rev/全Document完全性は読み取れない（SUI #3368）。 | Tool未存在、隠れたCard/Edge/件数漏れ、Tool reply欠落、実OS read-deny不成立。内部世界全体のClaimをしない |
| **P1 単一UI・Selection補正** | 公開合成Card 6〜12枚、曖昧・孤立・多重所属を含む。AI生成候補Q→人が1件除外/1件追加→次のread-only QueryがSを対象にしたことを実ID/版で検証。AI OFF手動操作を対照。 | レンダラXY/ラベルだけをIdentityにする、修正理由の捏造、Source/Grantの変化を無視 |
| **P2 二UI・Session切替** | SUI UIとTEIまたはSHO UIの間で、同一Session attach実験と用途限定Activity Handoffを分ける。実SelectionRef/Source/Revision、Request→Tool Reply→Consumer表示を同一Attemptで観測。二画面同時操作・後着応答も確認。 | Native attach非対応を同一Session PASSにする、他Productの旧Audience/秘密を再送出する、返信を異なるFocus/Pinに誤適用 |
| **P3 CSW・SEI・EKI後続** | CSW親和図法はSUIで仮の束/表札/関係を複数案としてPreviewし、元材料の具体・反証・孤立を保持。SEIは根拠・未決を再調査。EKIは多数Worker/Grantのread-only SelectionとPreviewまでを先に比較。 | KJ法の強制工程化、提案をMeaning確定、EKIのClient側Worker指定を実Authorityとする、Task ACKを業務完了とする |

比較指標は**対象同定誤り、再説明回数、補正Undo/Recovery、許可済み送出byte、実Toolの完全受領、実再開率、実Action前後の誤完了、追加費用**。CSWの認知方法の増分（通常探索vs一般的発想vsCSW）は、Canvas UIの増分・Harness transport/Skill loadの増分から別に測る。初回のDSH H2/H3固定四Session（比較適格0/4）を後続P0〜P3で事後的に合格へ変更しない。

**次の判断ゲート**：既存Product read-only CapabilityとUIのTarget/Selection Pinの実経路を1件ずつ確認し、P1に必要な実Read/Highlight/Selectionの欠落だけをOwner Issueへ返す。実験で複数Adapterが必要とした場合に限り、共通Adapter契約を追加検討する。現時点で**共通Selection ABI、共有Session Server、常設CSW Agent、横断E2E、本番Write権限、Owner受理は未採用／未実証**。

<!-- tai-harness-20261112-identity-coverage-qualification -->
#### 11.8.5 「選択できた」を「対象の一意性・意味・現在性が確認された」としない

§11.8.1〜4と[TAI Draft #633 §19.4/§19.5・§48](https://github.com/hat47x/tai-pleroma/pull/633)が、**Pin後の製品別再解決・送信・遅着返信・適用の受入順**を担当する。旧[#630](https://github.com/hat47x/tai-pleroma/pull/630)は§46/47の重複を避けて未マージ終了したため、現行の実施計画には用いない。再解決の前提である**選択元のIdentity/Projection自体が適格か**は別に判別する。これは新しい全製品共通ID・状態Enum・Verifierを採用する提案ではない。現在のProduct診断・Source/型付き参照・Receiptを正本のまま用いる。

| 判断すべき点 | 反例と既存Owner | 独立Expected・必要観測 |
| --- | --- | --- |
| **参照の単射性と一意性** | [TEI #4475](https://github.com/hat47x/tei-platform/issues/4475)の同Kind同ID後勝ちを、[merged #4524](https://github.com/hat47x/tei-platform/pull/4524)は重複診断と曖昧Index除外を実装・main統合済み | Qualified Kind/ID、Source/Workspace/Revisionと元配列の重複をProductに照合。**Index結果1件を元Source唯一の証拠としない**。model-localの修正をCRUD/Graph/Studio/外部ConsumerのPASSに昇格しない |
| **派生Viewの完全性と矛盾の露出** | [TEI merged #4513](https://github.com/hat47x/tei-platform/pull/4513)はData Index取り違えを修正、[merged #4534](https://github.com/hat47x/tei-platform/pull/4534)は構造OKとCRUD矛盾レビューを分離、[merged #4551](https://github.com/hat47x/tei-platform/pull/4551)は明示CRUD-onlyの交点・未使用Data判定を限定修正。後続Consumerの現在Apply資格は未受入 | CRUD表にセルが無いことを「作用なし」と推論しない。明示Source・派生View差・矛盾・Scopeを別観測。部分修正をCRUD全体整合のPASSにしない |
| **資格確認の純粋性** | [TEI merged #4507](https://github.com/hat47x/tei-platform/pull/4507)がModelFingerprintの入力Slice破壊・自己参照を修正し、モデル図へのAuthorityLimits保持を回帰。現mainで複製してからハッシュする実コードを確認 | この純粋性修正は既到達として記録。Fingerprintが同じでもSource-only改版・現在Grant/Provider Dataの不変は証明しない。[merged #4514](https://github.com/hat47x/tei-platform/pull/4514)のSource stale再確認と別資格 |
| **View表示と意味Identityの違い** | TEI同端点多重Edge/CRUD交点、SUI同Card別Canvas occurrence/二Island所属/非階層Relation、SHO同一文字列の異なる二Occurrence | 同名・同座標・同文字列でも別Targetを混ぜない。同Cardの複数表示を独立Evidenceとして二重計上しない。SUIは[#3430](https://github.com/hat47x/sui-sensemaking/issues/3430)/[#3431](https://github.com/hat47x/sui-sensemaking/issues/3431)、SHOは[#29/#38](https://github.com/hat47x/sho-composer/pull/38)を参照 |
| **開示と意味上の完全性** | [SUI #3368](https://github.com/hat47x/sui-sensemaking/issues/3368)：実context-projection.v1は許可済みCard/Island/Relation/Countのみ。原Source Revisionや全構造は投影外で、同じ公開投影が複数の内部Worldに対応し得る | 実取得集合と未取得/partial/unknownを区別。非公開ID/件数・関係をTool args、診断文、差分で漏らさない。外部Harnessは「これ以外に存在しない」と推論しない |
| **定義とProvider Dataの現在性** | [TAI #271の2026-11-11実PostgreSQL試験](https://github.com/hat47x/tai-pleroma/issues/271)：World Fingerprint同一でも行とRLS可視範囲が変化 | 用途・時点に合う対象集合を必要に応じて再Readし、実Provider/Scope/Query completenessを観測。可視0件や部分取得を不存在へ昇格しない |
| **跨製品の意味対応** | CSWの着想→SUIのIsland仮説→SEIのRecommendation→TEIのData/Function/Business。用語や見た目が同じでも意味は未受理 | 各ProductのQualified Refを別々に保持し、**対応関係自体をProposal**として提示。意味差・Source Loss・非開示を示し、Owner受理と実Host Grantを自動的に継承しない |

**初回の判別試験（後続、NOT RUN）**：TEIの同Kind同IDと多重Edge、SUIの同Card別Canvas表示と非公開Island、SHOの同文字列別Occurrenceを、それぞれのProductのread-only Operationで観測する。期待結果は (a)型と位置・版によって一意に解決、(b)曖昧性が残るため保留、(c)許可Projectionが不足するためUnknown、のいずれか。**曖昧でも最初の1件へ黙って束縛しない**。現ProductのRead/CLIの到達有無と、設計書の想定を分ける。

**Owner分担**：TEI Fingerprintはmerged #4507、同Kind重複IDはmerged #4524、CRUD索引はmerged #4513、構造OK/CRUDレビューはmerged #4534、明示-onlyと未使用診断はmerged #4551、Source-only staleはmerged #4514、Product Readerの限定回帰は[Draft #4504](https://github.com/hat47x/tei-platform/pull/4504)、Studio Pinは[#4515](https://github.com/hat47x/tei-platform/issues/4515)。SUI安全投影は#3368、SHO Buffer/Occurrence再解決は#29/#38、UIでのPin再束縛・非同期返信の受入順は[TAI Draft #633](https://github.com/hat47x/tai-pleroma/pull/633)、実Hostの非漏えいは[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)。本§11.8.5は横断適格性比較と禁止推論のみを所有し、第二のID Store/Parser/Checkerを実装しない。

**既存順序**：§11.8.4 P0でstable IDの取得だけでなく、実Productの曖昧性・Coverageの確認を加える。P1のQ/E/Aは許可済み解決候補だけを対象とする。P2のHandoffでは意味対応と現在資格を別に判断する。P3のCSW候補をAccepted Meaningへ昇格せず、EKIの選択を配置権限と同一視しない。初回[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)のH2/H3実隔離・Tool完全受領は新規Blockingを設けず最優先のまま。

**状態**：本§は設計・受入条件。TEI #4507/#4524/#4513/#4534/#4551/#4514の限定修正はmainに到達済み。一方、各Derived Consumerでのモデル不適格表示・実Studio Pin、SUI/SHO/TEI/EKI実UI一往復、跨製品Meaning受理、Live Session共有、外部Harness実E2Eは未資格／NOT RUN。

<!-- tai-harness-20261112-parallel-lanes-first-real-job -->
#### 11.8.6 独立開発経路を並走させ、外部送出の接合点だけを資格化する（2026-11-12）

**前節P0〜P3は横断E2Eの証拠を積む順序であって、Product内部のread-only選択/Pinの開発を、外部HarnessのH2/H3全試験完了まで止める理由ではない。** 反対に、UIで選択/Pinができたことを、外部Harnessの実OS隔離・完全Tool Reply・Skill実Loadの代用品にしてはならない。二つの並列経路を**接合点でのみAND条件**にする。

| 経路 | 実装・独立Expected | 他経路を待つ必要／停止線 |
| --- | --- | --- |
| **S：Product-local** | SUIの公開合成Cardでread-onlyのQ→人によるE/A補正→結果S、TEIのQualified Kind/ID/Source revisionの一意/曖昧診断、CUI/GUIのPin保持/Undoを、まずAI OFFまたは合成Selectorで評価。[SUI #3400](https://github.com/hat47x/sui-sensemaking/issues/3400)/[TEI #1124](https://github.com/hat47x/tei-platform/issues/1124)/[Draft #633](https://github.com/hat47x/tai-pleroma/pull/633)のOwnerに帰属 | 外部HarnessやSkillの資格は**不要**。未実装のSUI外部Selection APIを偽装しない。未レビュー情報の公開と本番保存/実Effectは対象外 |
| **H：Harness／実開示** | [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の現G0 OS Read-deny、G1実送出、G2 Tool request/reply完全性、事前PinしたH2/H3四独立Session・独立Expected。実Tool-onlyとProduct Skill配信を別に判別 | UI/CUIのPin完成は**不要**。G0未達のHarnessへ非公開Sourceを渡さない。H2/H3比較適格0/4を別のGUI成功で上書きしない |
| **J：接合（実Harness E2E）** | 公開・合成1 ProductのPin/Selection→現在Audience/Hostが許可したProjection/Recipientの送出Preview→実Harness Tool request/reply/終端→元Pinへの結果表示を**同一Attempt**で確認。実送出byte、許可対象集合とSource revision、実Session ID、Request/Response IDを束縛 | **SとHの対象機能ごとの資格が両方必要**。後述の既存Handoff v1受領テストがPASSしていても実Harness受領と同一Session共有は別資格。旧Pinへ後着したReplyを現在の別対象へ適用しない。同一Session attach未対応ならunsupportedを明示、別Session Activity Handoffは別評価 |
| **C：創造的方法の増分価値** | CSWあり/なしで、同じ材料からSUIの仮の束/表札/未統合Cardを再構成する効果を、まずProduct-localで比較。外部Harness共有の価値はJの後に別測定 | [TAI Skill計画§47](https://github.com/hat47x/tai-pleroma/blob/main/docs/yi-constellation/harness-skill-plugin-plan-2026-11-02.md)に従いTool-onlyで足りる場合はSkillを自動投入しない。CSW利用時も原典・異論・保留を保持し、採用済みMeaningとしない |

**接合より前に実行する既存Product Handoff（Hの前提ではない）**：[mainのHandoff実行票 §10 QH-P0](https://github.com/hat47x/tai-pleroma/blob/main/docs/yi-constellation/cross-product-handoff-execution-tickets-2026-11-11.md)で、公開TEIの実 `model catalog` 読取と既存SUI→SHO Handoff v1の実受領を使う。追加のTarget/Schemaを作らず、**I=対象選択の由来、R=実Consumerが元対象を一意に再解決したか、P=許可済みProjection、T=実Transport/Receipt、C=実Consumerの意味利用、H=Harness/Skill/Effect**を既存票の列に記録する。例えばSHOがMarkdown bytesを再ReadしてもTEIのSourceを自分で読み直していなければ、Tの限定PASSをR/CのPASSへ昇格させない。必要なProduct Capabilityが未提供ならその列をunsupported/not-runとする。このProduct Handoffは**Sに続けてHと独立に実施できる**が、Jの代替ではない。具体的なOwner/実行順は[後継Draft #633 §48](https://github.com/hat47x/tai-pleroma/pull/633)を参照する。旧PR #632の設計票はmain §10へ到達済みであり、本書に第二のQH Test/Runnerを作らない。

<!-- tai-20261112-audience-declaration-vs-host-grant -->
**実RunnerのClaim Ceiling（G4 N2／Audience）**：[SHOの既存Runner](https://github.com/hat47x/sho-composer/blob/main/scripts/handoff-cross-product.cjs)の2026-11-12時点のコードでは、元SUI票のAudience [sho-composer]を[sho-composer, other-consumer]へ変更する操作があり、コメントでは「狭めた／拡大を拒否」と説明されていた。実際には受信者の**宣言を拡大**し、SHO Consumerが新しい票を再Readしたことの確認である。**Hostが拡大を認可した／拒否した証拠ではない**。訂正は[SHO merged #42](https://github.com/hat47x/sho-composer/pull/42)でmain反映済み。G4 N2実Consumer回帰はUbuntu/Windowsの限定CIで確認済みだが、**SUI/TEI三製品RunnerとHost送出認可はNOT RUN**。初回QH-P0はこのG4 N2を「現在の宣言票の受領」とだけ記録し、実Audience Grant/送出可能性は[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)の別資格で検証する。Handoffのdisclosure.audienceという**データ**を認可Token/Host Policyの代用品にしない。

<!-- tai-20261112-qhp0-repro-and-claim-ceilings -->
**QH-P0の実実行カード（新Runnerは作らない）**：既存の[TAI Handoff実行票§10](https://github.com/hat47x/tai-pleroma/blob/main/docs/yi-constellation/cross-product-handoff-execution-tickets-2026-11-11.md)を唯一の記録先とし、[SHO mainの実Runner](https://github.com/hat47x/sho-composer/blob/main/scripts/handoff-cross-product.cjs)をSHO checkoutで、絶対パスを渡して起動する（例：`node scripts/handoff-cross-product.cjs --sui-frontend <absolute-SUI-frontend> --tei-root <absolute-TEI-repo>`。山括弧は実パスへ置換）。実行前に(1) SHO/SUI/TEIのHEADとSHA、SUI Producer対象3ファイルのGit blob、対象ファイルの未変更状態、SUIの`node_modules/vitest/vitest.mjs`、Go/Node版を確認する。(2) Runnerが固定する**354-byte payload、独立SHA256、Product Producer Blob**を後追いで最新へ書換えない。Pin不適格ならfail/unsupportedのままSource差分レビューへ戻す。(3) Runnerの`TEI model catalog`が実際に行われ、`effect=read-only`・WorldFP・ModelRevision・AuthorityLimitsが受領Ticketに残ることを確認。(4) Consumerの別Process実Read、実Receipt・欠落/改変の拒否を記録。失敗しても別の合成RunnerでPASSを代用しない。

**QH-P0のClaim Ceiling（独立Expected例、次回実行まではNOT RUN）**：

| 観測列 | 実測で採用できる範囲 | この実行からは採用しない範囲 |
| --- | --- | --- |
| `I` | Driverが明示した合成選択 | 実GUI/CUIのPinned Target操作 |
| `R` | TEI CLIが自身のCatalogを読んだ場合は**Driver由来の観測** | SHO Consumerが元TEI Qualified Subjectを同Workspace/Scope/Revisionで独立再解決したという主張 |
| `P` | 公開・合成票とTicketに記録されたAudienceの**宣言** | 実OS/Host Grant/Recipient追加拒否、全Source完全性 |
| `T` | SUI実Producer→SHO実ConsumerのTicket/Payloadの実byte受領と限界付きReceipt | 外部Harnessの実Network egress、同じLive Sessionへのattach |
| `C` | SHOが受信Markdownと制約を保持したこと | TEI元Meaning/Owner受理、Source現在性、別Consumerの完全理解 |
| `H` | 本RunnerのHarness名はラベル。別Process再受領は別Processとしてのみ記録 | Harness Skill実ロード、実共有Session、実業務Effect |

**G4 N3のClaim Ceiling**：[SHO Runner](https://github.com/hat47x/sho-composer/blob/main/scripts/handoff-cross-product.cjs)の2026-11-12時点の`g4-n3-edited-receipt-not-adopted`は、過去のReceiptを改変した後に**新たにConsumerを呼び出し、そこで発行されたreceivedAtが改変した日時と違う**ことをassertしている。しかし、当該N3区間は**改変された旧ReceiptをProducerの実Review機能へ入力して拒否結果を得る試験ではない**。従って「新規受領で旧日時を採用しない」の限定PASS候補に留め、「改変旧Receiptが独立Verifierで必ず拒否された」とは主張しない。G2で実施するReceipt一致Reviewの証拠は別票で扱う。修正範囲と真正性CheckerのOwnerは[SHO #42](https://github.com/hat47x/sho-composer/pull/42)および現行SUI/SHO Producer/Consumerに返す（改変受領を扱うべきかもOwnerが判断）。これを外部HarnessのOS認可やSession継続の証明へ昇格しない。

**モデル識別の追加対照（TEI現行Draft）**：[TEI #4504](https://github.com/hat47x/tei-platform/pull/4504)では、同じSource byte offsetに別Subjectが置かれる負例、同じSemantic Source/WorldFPでも**別Workspace**になる対照の回帰コードが追加された。旧Pinが一致するラベル・Span・Fingerprintだけで再束縛されないことを、TEI Productの既存read-only `ReadWorkspaceSubject`で先に評価し、[TEI #4504](https://github.com/hat47x/tei-platform/pull/4504)のProduct Reader 3回帰はexact HEADの11 CI成功を確認した**限定到達**。ただしDraft・main未統合、実Studio Pin/他Consumer再解決はNOT RUN。QH-P0のHandoff v1には独立Consumer Resolverが無いのに`workspaceId`の新正式Fieldを作ったことにはしない。Scope/Workspaceを現Schemaで無損失に渡せない場合は[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)/[後継 #633](https://github.com/hat47x/tai-pleroma/pull/633)へFit/Gapを返す。

<!-- tai-20261112-actual-progress-sho48-tei4515 -->
**実受信と元対象解決を切り離す追加の反証**：[SHO merged #48](https://github.com/hat47x/sho-composer/pull/48)のConsumer/CLI・Ubuntu/Windows回帰は、**同じMarkdown byte**から (A) TEI Data ID/Source A、(B)同ID/別Source B、(C)同Source B/別IDの3票をいずれも受領できることを示す。Payload SHA一致や独立再読取がtrueでも、元Sourceを実ReadしていなければoriginalSourcesRead=false・sourceRevisionCurrent=false・meaningAccepted=falseのまま。[SHO merged #47](https://github.com/hat47x/sho-composer/pull/47)は外部BのReceipt JSONを事前作成して再生するだけでもA/B一致し得る負例を確認。受信(T)、元Subject再解決(R)、実外部B Consumer/Skill/Session(H)は別。観測は[mainのQH §10.4/§10.5](https://github.com/hat47x/tai-pleroma/blob/main/docs/yi-constellation/cross-product-handoff-execution-tickets-2026-11-11.md)へ集め、第二のCheckerを作らない。**TEI実Workspace＋SUI Producer＋SHO Consumerでの新QH-P0はNOT RUN**。

**次に着手するProduct-local UI縦切り**：[TEI Studio #4515](https://github.com/hat47x/tei-platform/issues/4515)の既存Workbench/Host Inspectを使う**read-only Subject Pin 1件**。kind/id/workspaceのPin Intent、実Inspect/Source版、失効・遅着・別Root/同Fingerprint、明示Unpin/Undoを別表示し、Graph描画用parent:関係IDを意味Relation/正式Edgeへ自動昇格しない。Keyboard/IME/Escによる選択保持に加え、今は公開できない原文・隠れた対象のDOM/ARIA漏洩を[TEI #2516](https://github.com/hat47x/tei-platform/issues/2516)のDisclosure Ownerへ返す。**SUIのR0現Source→Reader→再起動後Readback**は[SUI Draft #3437](https://github.com/hat47x/sui-sensemaking/pull/3437)に委譲し、Raw/Canvas/AI導線全体をこの一件の先行Gateにしない。Product-local試験は外部Harness無しで着手可、本番Write/DB Schema/実Host Grantは別。
<!-- tai-20261113-priority-convergence-studio-reader-selfbuild -->
**2026-11-13の実装優先順位（追加の試験正本は作らない）**：Product内の安全な選択を、実装の最小機能と横断接続資格に切り分ける。

1. **TEI Studio S0**：[#4515](https://github.com/hat47x/tei-platform/issues/4515)のSource TypeScript＋現行Host Inspectで公開合成Subjectを1件明示Pin。既存PIN-S0-01〜07でFocus/IME/Esc/別Root・同FP/旧Reply/Undo/描画用Edgeを対照。**Read-onlyのPin Intentを残すこと**と**現在Apply/Disclosureが可能なこと**を別表示し、未受理/矛盾モデルは修正・調査目的のReaderを閉鎖しない。CRUD-only参照や曖昧モデルの参照数0は、[main #4551](https://github.com/hat47x/tei-platform/pull/4551)と[#4524](https://github.com/hat47x/tei-platform/pull/4524)の元宣言との一致・Scope完全性を確認しない限り「削除可能」と表示しない。TEI #4504のReader CI成功をWorkbench GUI試験へ昇格しない。
2. **SUI R0/R1**：[#3438](https://github.com/hat47x/sui-sensemaking/issues/3438)の現DocumentV1を実HTTPで保存し、独立Process/Readerから再読取した事実と、Raw URLのみ・未取得/Partial・501件目/未レビューをFit/Gapとして記録。Reader成功を外部Harness・Source全件取得・AI認知価値の実証にしない。
3. **QH-P0**：[main Handoff実行票 §10](https://github.com/hat47x/tai-pleroma/blob/main/docs/yi-constellation/cross-product-handoff-execution-tickets-2026-11-11.md)の既存Runnerで、TEI Product ReaderのQualified Kind/ID/WorkspaceRefとSUI/SHO Handoff v1に表現されたTargetを実照合する。**三要素モデルのData kind、TEI Source Readerのkind、Handoffのtarget.kindを文字列類似から同一視しない**。必要な対応がProduct公開IFに存在しないならR=unsupported/unknown、Tの限定PASSは保持。SHO #48の同Payload別Source負例と#47の外部Receipt再生は独立Expectedとして再利用し、第二Resolver/Schemaは作らない。
4. **並行する最優先Product目標**：TEI Desktop実Wails Window/IPC/APIと、Stage1→Stage2のTEIセルフビルドは[TEI #1824](https://github.com/hat47x/tei-platform/issues/1824)/[#2831](https://github.com/hat47x/tei-platform/issues/2831)が主Owner。Studio Pinは実Workbench UXの先行部品だが、QH-P0・H2/H3/CSW/Raw拡充をDesktop起動・セルフビルドのHard Gateに加えない。[merged #4539](https://github.com/hat47x/tei-platform/pull/4539)の実PG→Function Contextは限定Reference CLIまでの到達で、一般tei CLI/Studio/Hostの実DB読取とは別。

**完了の定義**：各Ownerが独立Expected・実呼出し先・実Consumer・exact HEAD/Attempt・失効時の停止を確認した範囲のみPASS。TEI内部Read/Studio表示、SUI別Process Reader、QH実受信、外部Harness実Tool、Host Effectを同一「完成」へ合算しない。実行票はTEI PIN-S0/SUI RIR/TAI QH/TAI #168を再利用し、中央Host/Registry/Selection ABI/第二SSOTを増設しない。
**小さな独立Expectedの例（合成／設計のみ・NOT RUN）**：SUI内部の合成資料には8件のCardを置くが、外部へ公開可能な範囲は権限により制限する。許可済み検索結果Qが3件（仮ID A・B・D）なら、人がBを除外し許可済みFを追加した後のSは**A・D・F**である。実際にProductが読めない隠れたCardはQ/Aへ自動追加されず、外部Harnessに隠れたCardのID・件数・検索差を公開しない。元Source r1→r2の改版、表示上同名別Card、二Canvasの同Card occurrence、別Recipient、同一Sessionへの後着を一因子ずつ変化させる。各例で「Pin済み／現在一意に再解決済み／許可ProjectionでRead済み／実Toolへ配送済み／Consumerで受領済み」を**異なる観測**として記録する。

**新たなHarness能力を選択条件にしない**：同一実Sessionの複数Client attach・並列Writer・Skill loaderを、代表Harnessすべてが提供するとは推定しない。実Support表で受信者Capabilityを確認し、Product側は1本の外部Sessionの利用または用途限定Activity Handoffに縮退する。外部HarnessのModel/provider切替、セッションのCancel、旧Grantの残留はProductの実Operation取消・情報消去の証拠にならない。

**Go/No-Go**：Sの単独成果はProduct UX/型付き参照だけの資格。Hの単独成果はHarness Transport/OS隔離だけの資格。Jで実Receiptが無ければ横断E2E成功を主張しない。Cの追加価値が確認できなければCSW Skill常用化も新UI機能の必須化もしない。実現しなかった能力の一覧・再説明回数・Context byte・人間の補正手数・誤対象率・未知のResultを、既存[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)と[#422](https://github.com/hat47x/tai-pleroma/issues/422)の結果票で測る。新しい共通Runner/Checker/Selection Storeの事前導入は不要。

