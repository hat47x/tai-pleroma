# YI Constellation：外部ハーネス向けSkill／Plugin構成計画（2026-11-02）

状態：**設計提案 / Owner未受理 / 新Skillのハーネス実接続・配布・効果比較はNOT RUN**。本書はTAIの製品横断連携案であり、各Productの契約・実装・意味受理・権限正本を変更しない。

## 1. 目的と前提

利用者のAIハーネス（Claude Code、Codex/ChatGPT、OpenCode/DeepSeek Harness、利用可能な他社ハーネス）に、YI Constellationの各Productを**単独でも組合せでも**利用できる入口を提供する。要件探索や専門Skillの数に固定的な上限は設けず、使う場合の文脈負荷・危険性・検証可能性を測る。

* **YI Constellation**は製品群のブランド／シリーズ配布名。専用の正本Repositoryは新設せず、シリーズ構成・互換検証・配布計画はTAIで扱う（[TAI #74](https://github.com/hat47x/tai-pleroma/issues/74)）。
* **TAI Pleroma**は目的・活動の継続とProduct選択／組合せを担う。専門的な認識・意味形成・モデル・文書・委任の実装はSEI/SUI/TEI/SHO/EKIに残す（[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)）。
* **外部ハーネス**は対話・推論・ツール選択・自律作業・スケジュール等、実際に提供する機能を担当する。TAI専用のAI Host、常駐Agent、第二の共有Store/Authority/Registryは作らない。
* **各Product**は自身のSource・モデル・業務意味・Release・操作の権限検査・検証責任を持ち続ける。技能文書が権限・正本・実行完了を作り出すことはない。

根拠：Agent Skillsは必要に応じて`SKILL.md`と参照資料をロードする。MCPはTool discovery/呼出しの共通経路を提供するが、Tool annotationsは**権限保証でなくヒント**。Codexは`AGENTS.md`（永続規約）／Skill（再利用手順）／MCP（外部機能）を区別する。
- https://agentskills.io/specification
- https://developers.openai.com/plugins/concepts/skills
- https://learn.chatgpt.com/docs/customization/overview
- https://modelcontextprotocol.io/specification/2026-07-28/server/tools

## 2. 責務と配置の原則

| 層 | 主な責務 | 保有する正本・制約 |
| --- | --- | --- |
| Product Core（各製品） | 実際の分析・編集・検証・生成・委任と固有の意味契約 | Productごとの正式契約と結果 |
| Product CLI/API/MCP | 操作の型付き入口、入力検査、認可された応答、実証可能な結果 | CLI/API実装に従う。MCPは認可の代替にならない |
| **Product Skill** | どの目的・条件でどの能力を使い、何を証拠として報告するか | 各ProductのRepositoryが正本 |
| **TAI横断Skill** | 利用者のActivity・目的・用途から必要な能力を発見／選択し、引継ぎと結果照合を組み立てる | TAIが正本。製品意味・権限の第二正本にしない |
| **Harness adapter / Plugin bundle** | 同じportable Skillを環境固有のロード形式・設定へ配布する | 配布単位の版・互換検証。Core機能を複製しない |

* ユーザーがTEIのみを利用する場合はTAI Skillを必須にしない。TAIを利用しても、不要なProductは起動・インストールしない。
* Skillの`name`/`description`は起動条件を明確にする。複数製品の汎用的な「全部できます」記述による自動選択衝突を避ける。詳細な手順とfixtureは`references/`へ遅延読込みする。
* `AGENTS.md`はRepo開発の恒常的規約、Skillは利用者の反復可能な作業、Product内Pluginは機能拡張、Harness Pluginは導入パッケージとして区別する。
* 横断SkillはProductが公開した結果・操作を**参照**して活動をつなぐ。SEIの認識・SUIの意味探索・TEIの意味契約・SHOの文書・EKIの実行受理を自身の推測で置換しない。

## 3. Product別のSkillポートフォリオ（初期候補）

| Owner / 入口候補 | 目的別Skill候補（拡張可能） | まず再利用する実在機能・関連Owner |
| --- | --- | --- |
| **TAI** `yi-tai-activity` | `activity-scope`、`product-routing`、`cross-product-handoff`、`resumption`、`outcome-evidence` | TAI #168、#232、#234。SCN-001と既存Reference接続 |
| **SEI** `yi-sei-inquiry` | 観測・根拠の十分性・Method選択・用途相対判断・専門家照会・再開 | [SEI #660](https://github.com/hat47x/sei-cognition/issues/660)、[#677](https://github.com/hat47x/sei-cognition/issues/677)、[#767](https://github.com/hat47x/sei-cognition/issues/767)。専門Method内部とHarness手順の混同を避ける |
| **SUI** `yi-sui-sensemaking` | 候補生成・Card/Island/Relation探索・許可済みProjection・意味可視化・提案差分レビュー | SUI agent view/露出監査、Proposal history。非レビュー構造を外部へ漏らさない |
| **TEI** `yi-tei-modeling` | model discovery/authoring/validation・SQL／構造/組織意味・multi-target生成・適合/再生成・既存システム移植 | [TEI #2017](https://github.com/hat47x/tei-platform/issues/2017)、[#2390](https://github.com/hat47x/tei-platform/issues/2390)、[#2516](https://github.com/hat47x/tei-platform/issues/2516)。外部Host向け成果物生成を尊重 |
| **SHO** `yi-sho-compose` | 文書構成・出典再解決・Candidate review・編集・監査・出版 | SHO Composerの固有体験と既存MMI CLI/Skillの再利用。**現行MMIには`skills/mmi/SKILL.md`が既存**。新Skillから参照し機能複製しない |
| **EKI** `yi-eki-delegation` | 委任範囲・Task受付/観測・取消・Attempt/ResultClaim/AcceptedResult照合・限定再試行 | EKI既存Control/Agent/受入。合成Task受付・部分process PASSを実効果へ昇格しない |
| **専門方法（任意）** | CSW探索、業態・法律・DBなどの専門Method／専門家照会 | 独立方法は任意導入。生成的探索の途中に強制採否Gateを挿入しない。専門家が人間／AI／内部実装のいずれでも責務を分ける |

表の名称は**候補**。現在の製品に存在することを表すものではない。`skills/ponytail`など各Repoに既に存在する資産は棚卸し対象とし、一律の改名・複製をしない。SHO専用Repositoryは独立製品としての固有Skillを持ち、MMIの再利用機能の正本はMMIに残す。

## 4. 能力の発見と組合せ

### 4.1 発見の順序

1. Harnessがユーザーの目的・用途・許可されたデータ範囲から、該当Skillを選択する（Skillなしで十分なら使わない）。
2. Skillは**導入済みの**CLI/API/MCP Toolを確認する。実環境の`--help`/`--version`／既存API契約／MCP `tools/list`等で存在と版を確認する。未実装の抽象コマンド名を実在APIとして呼ばない。
3. 必要ならTAIは別製品のSkillを案内する。Productごとに許可された投影・Source revision・時点・操作結果を受け渡す。
4. 変更を伴う動作は、そのProduct／Adapter／Hostの認可・保存前検査へ通す。実作用はProvider receiptと独立Observationで確認する。

### 4.2 任意のProduct Capability descriptor（設計候補）

共通の巨大なRegistryの代わりに、各Productから**必要な粒度の説明文書／version付きmanifest／既存Tool一覧**を提示する方法を比較する。候補属性：

`product, capability_id, purpose, product_version, tool_or_command, input_contract, output_contract, source_freshness, read_write_effect_class, visibility, required_authority, verification, compatibility`

これは**提案上の棚卸し項目**であり、固定した共通JSON schema/採用済みAPIではない。発見結果を権限や信用の根拠にせず、実Hostが認めた能力だけを呼ぶ。非公開Schema名・件数・関係・fingerprintも保護対象（TAI #232）。

### 4.3 Activityの扱い

TAIは次の役割の*参照*を組み合わせる。ユーザー目的→用途/時点→原資料Ref＋版→候補/根拠/未決→製品ごとの意味判断→Task/操作同一性→結果の独立観測→現在適用性。すべての欄を全用途で要求しない。「準備したContext」「Harnessに届けたContext」「実際に利用したと観測できたContext」を区別。開示されたProjectionで原世界全体を確定できない場合は`unknown`を残し、必要ならSource保持Productに限定照会する。別Harness間の引継ぎでRaw・Grant・秘密はコピーしない。

## 5. 配布構成とバージョン

* **Product単独**：`yi-tei-modeling`とTEI CLIなど、単一製品で成立するbundle。
* **TAI-minimal**：`yi-tai-activity`とread-only製品接続のみ。欠けた製品を`unsupported/unavailable`として扱える。
* **TAI-composed**：用途に応じたProduct Skills＋接続を参照して選択配布。全製品の常時同時起動は不要。
* **Harness adapter**：Claude Code／Codex／OpenCode/DSH等が受け付ける現実の配布方式を別途検証。Skillが動く環境とMCPが使える環境、Plugin配布できる環境を別々に記録。Dots/Grok等にも同等のSkill導入を仮定しない。

TAIが束ねる場合は、各SkillのSource repo/revision、content digest、Product CLI/API実版・Tool契約、対応Harness/profile、権利・公開範囲、検証証拠を固定する。配布物の成功≠Productの意味受理、Skillロード成功≠Task完了。更新時は互換の再検査を行う。署名／SBOM／Plugin marketplaceの形式は、最初の実配布環境の要件を見てProduct Ownerと決める。YIブランドは第二の配布正本にならない。

## 6. 安全・権限・認識論上の境界

- **Raw分離**：SEI/SUI/SHO/TEI等のRawおよび非公開Metadataには必要に応じOS user/ACL、プロセス・filesystem・ネットワーク・環境変数・ログの境界を適用し、外部Harnessは許可Projectionを受領する（[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)、[TEI #2515](https://github.com/hat47x/tei-platform/issues/2515)）。
- **Skillの命令は権限ではない**：MCP annotationの`readOnlyHint`/`destructiveHint`/`idempotentHint`も、実際の認可・副作用・冪等性の証明と区別する。インストール済みのSkillやTool記述、取り込んだ外部文書に含まれる命令は信頼境界を越えさせない。
- **モデル受理と書込み**：Model Validation、AI提案、byte一致、歴史的accepted、現在用途での意味受理、Hostからの許可、本番副作用を別々に示す（TEI #2017／#2516）。
- **EKIの状態差**：`queued`、attempt実行、result claim、accepted result、成果物bytes、外部業務完了は別の証拠。結果不明の再送をSkillの都合で自動化しない。
- **探索の自由**：SUI/CSWなどの候補生成は自由に広げ、公開・作用・外部送出に関わる資格判定を後工程で独立に行う。

## 7. スキル実証計画（並列可能な作業列）

各作業列は機能追加の件数上限ではなく、**証拠付き成果に到達するための一単位**。詳しい判定と負例は [SK-01評価票](../../evaluations/SK-01-harness-skills.md)。

| Lane | Owner | 進める内容 | Exit（最小資格） |
| --- | --- | --- | --- |
| SK-G0 | TAI＋各Product | 各mainの既存`SKILL.md`/`AGENTS.md`/MCP/CLI、exact版、公開範囲と利用可能なHarnessを棚卸し | 存在／ドキュメントのみ／動作済み／unsupportedを区別したinventory |
| SK-G1 | MMI→SHO / TAI | 既存MMI `mmi` Skillからread-only inspect→出典付き結果をSCN-001で利用。TAI側portable Skillは評価用サンプルから開始 | 同Source/同versionでSkillなし・ありを比較し、余分なツール呼出しを測る |
| SK-G2 | SEI/SUI/TEI/SHO/EKI | 各OwnerがProduct入口Skillを試作。契約/負例/能力一覧は自Repoに保存 | 目的別Skillが単独起動・既存CLIを利用でき、未実装ならunsupportedを返す |
| SK-G3 | TAI | 複数Productの必要時選択、Activity resume／間接証拠の扱いと出典逆引きを試す | TAIあり/なし、製品直接/間接を同一fixtureで対照 |
| SK-G4 | Harness adapter担当 | Claude Code・Codex＋可能ならDSH/OpenCodeで同じportable Skillの配布・手渡し | Core無改変で2環境以上、相違はadapterと記録された能力差に閉じる |
| SK-G5 | Product Security／TAI | prompt injection、偽装Tools、Raw/Metadata漏洩、旧版Skill、副作用、切断時の縮退の実Host負例 | 実OS/Host拒否と独立証拠。Prompt遵守のみで合格としない |
| SK-G6 | TAI配布／各Product Release | 製品別配布・用途別束・固定digest・互換・公開条件を確認 | owner別製品受理とシリーズ配布受理を別途記録 |

最初の正例は**SCN-001の合成資料→MMI inspect→SEI判断根拠→SHO案**。次にTEIの型・生成、EKIのmock Taskを追加する。同時に業務・生活・未知課題などのPressureを増やせるが、実業務の意味・購入・本番作用の資格は別に検証する。

## 7.1 2026-11-02他製品の最新設計との突合・進行中の判定

詳細は[Skill相互運用・意味・実効権限の深化](harness-skills-interoperability-and-evidence-2026-11-02.md)。2026-11-02の各mainを固定して`skills/`を照合した結果、**製品操作を実際に案内するSkillとして確認できたのはMMI `mmi`**であり、SEI/SUI/EKIの`ponytail`は一般的な開発作業Skillだった。製品操作Skillの実接続済みという根拠にしない。TAIの`yi-tai-activity`は本Draft内の未導入試作である。

今回追加した独立評価軸は、①Skill発見/ロード、②現環境にあるCLI/MCPとアクセスできる範囲、③Claim/Source/時点/Scopeに対する情報十分性、④実OS/Hostの機密・書込み・送出権限、⑤同一Task/Attemptと結果・外部Effect、⑥別Harnessへの情報/意味/運用/権限の継続範囲である。Product Capabilityの文書上の宣言から、実Host資格や業務Owner意味受理へ自動昇格しない。

SEIのMethod Skillは認識のための**手順**であり、TEI DSL/Domain PluginやProduct Capabilityの正式契約とは別。TAIが横断Activity Skillを持っても、各HarnessがSkillから別Skillをプログラム的に起動できることは前提にしない。多言語Target・SQL/組織構造・論文/式の構成・SHO文書・EKI実Bodyの候補Skillを各Ownerで並列拡充し、TAIは用途別の組合せと増分価値だけを追跡する。

## 8. 既存計画への接続・未決

- **統括** [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)（Harness-first）を既存親とし、[Draft #169](https://github.com/hat47x/tai-pleroma/pull/169)のA/B/C/D/E比較にSkill／Plugin有無の**独立変数**を追加する。#169はmainとの差があるDraftのため自動mergeしない。
- **シリーズ配布** [TAI #74](https://github.com/hat47x/tai-pleroma/issues/74)にbundleの版・権利・検証を接続。**機密** #232、**Harness可用性** [#234](https://github.com/hat47x/tai-pleroma/issues/234)をそのまま参照する。
- **TEI** #2390・#2017・#2516、**SEI** #660・#677・#767、**SUI** Agent Projection、**SHO/MMI** `skills/mmi` と#658/#672、**EKI** acceptance/sandbox等にProduct固有差分を還流する。TAIに第二の実装Ticketを重複作成しない。

Owner判断として残すもの：入口Skillの正式命名、配布Profileと公開範囲、各Productの有償／非公開能力の扱い、Capability descriptorの最低互換面、各Harnessで実際に提供できるPlugin/MCPの種類、操作時認可と効果の正式なOwner検証。設計文書の作成はこれらの採用・稼働の証拠にならない。


## 9. 2026-11-02 横断設計追補：必要能力の最小閉包と、Skill追加が必ずしも有益でない理由

**提案／SK-R試験NOT RUN。** 既存SK-G0〜G6とH0〜H7を置換しない。本節は、[TEI #2497の損失あるProjection](https://github.com/hat47x/tei-platform/issues/2497)、[#2500の部分的なOperation逆対応](https://github.com/hat47x/tei-platform/issues/2500)、[#2516のConsumer別Claim](https://github.com/hat47x/tei-platform/issues/2516)、[SEI #767の根拠十分性](https://github.com/hat47x/sei-cognition/issues/767)、[SHO #4/#6](https://github.com/hat47x/sho-composer/issues/6)の議論をSkillのルーティング判断へ接続する。

### 9.1 新たな判断：導入したSkillが増えても、実効能力や判断品質は単調に増えない
同じ依頼に対してSkill/Toolの候補を増やすと、説明文の類似、コマンドの同名、ツールの誤選択、暗黙Contextの増量、開示面・実効Reachabilityの増加により、むしろ失敗が増え得る。**全製品インストールを前提にしない**従来方針を、同じ固定Taskと利用者権限で反証可能な評価へ落とす。

TAIが選ぶのは「似た名前のProduct Skill」ではなく、**目的が要求する観測・判断・書込み・保存・独立結果確認を満たす、必要最小限の能力の組合せ**。機能の多さだけで最適を主張せず、Tool call/Context/情報露出/未決維持/正しい成果のトレードオフをH2↔H3、H4↔H5で実測する。

### 9.2 発見／接続／実行の別々の証拠
次の段階は**相互に昇格しない**。いずれも汎用の公式Runtime状態型ではなく、SK-01の照合欄とする。

1. **Declared**：Product Repoの実在Skill・Tool説明、Source revisionとファイルdigest、必要入力/期待Output/効果分類。
2. **Packaged/Installed**：Harness向け実配布物のdigestと、実インストール先・有効Profile。TAIのBundle manifestだけでは配置を実証しない。
3. **Available/Reachable**：当該Sessionで実際に利用可能なSkillとCLI/MCP Tool、実Tool version・実Endpoint・実OS principal。Skillファイルが存在しても、Harnessがロードしたかは未観測ならunknown。Tool annotationは強制Policyでない。
4. **Authorized/Disclosable**：操作と対象・時点についてHost/Productの実許可、結果をそのConsumerへ渡す許可。Tool discovery成功から許可を推論しない。
5. **Executed/Observed**：実際の引数・Source・出力・Error/Exitと、必要なら別Provider/独立Read/正式Receiptで確かめた効果。生成Message/Agent成功とProduct意味受理/業務完了を区別。

VersionはProduct/CLI/MCP/Skill/Adapter/Harness/Connection/Policyそれぞれにある。**Plan時の棚卸しを、長期Activity再開時の現行接続証明に再利用しない**。ただし読み取り済み歴史成果物の再現と、その現在利用資格は別。

### 9.3 曖昧な依頼でも意味を取り違えない具体ルーティング
固定合成課題：「Excelの表を参照した設計書を確認し、必要なら保存して報告する」。

| 利用者が求めたOperation | 最小の所有元候補 | 追加資格と不適切な置換 |
| --- | --- | --- |
| 既存Excel表の位置・範囲調査、Markdown参照候補 | **MMI** の実CLI `inspect` / `check` / `render` | `check`終了0だけで C-01/T2 のSource再解決・納品をPASSにしない |
| 文書原文の保存、引用Occurrence、著者編集・Review | **SHO Composer**（現段階は契約/実装未確認） | MMIの`render`をSHO保存完了と呼ばない。実在しないSHO CLIを生成しない |
| 受理済みTEI意味モデルや生成ライブラリを検証 | **TEI**の実在入口と適切なTarget/Contract | MMI文書検査成功から業務Meaning/Java/.NET target適合を推論しない |
| 根拠の十分性・質問分解・異論を扱う | **SEI**の該当Method/入口 | 文書作成や検証の結果をOwner判断へ無断昇格しない |
| 複数製品を跨いだ目的・継続と、必要な接続選択 | **TAI**横断Skill | 単独MMIで十分ならTAI/SEI/SHOを増やさない |

似た`validate`、`check`、`commit`、`render`という語ではなく、**どのProductのどのObjectに対して、どの粒度・どのSource版・どの結果保証までを要求するのか**で選択する。複数能力が必要で依存が未成立なら、既に成立したread-only部分は報告し、欠けた能力だけをunsupported/未接続として残す。

### 9.4 更新・再開の受入原則
- Session再開、Plugin交換、同名Skillの優先順位変更、CLI/Tool出力形状変更の後は、当該操作に必要な**実接続と互換**を再確認。過去H3のPASSを新Harness/H5へ持ち越さない。
- 狭いProduct Skillで十分だったTaskへTAI横断Skillを加えても、無関係のRaw/Source/Toolを読む正当化にはならない。不要なProduct/Toolをロードしないこと自体をSK-01の正例として測る。
- Skillが指示した安全上の制約と、実Host/OS/Providerの**強制拒否**を別証拠とする。機密メタデータの存在すら見せない運用が必要な場合は、Capability discoveryの出力・件数・失敗理由も保護対象。
- 認可されたread-only投影で内部の真相が判別不能なら、外部Harnessは結論を推定せず、Product内部の限定検証と開示Policyを使う（SEI #767／TEI #2516／TAI #232）。
- 有償能力・非公開構成・第三者Skillのライセンスや公開適合性は、統合Bundle担当 #74とProduct Ownerの判断で扱う。Skill配布とProduct Release/Owner Acceptanceを混同しない。

### 9.5 受入への接続
[SK-01追補 SK-R01〜R08](../../evaluations/SK-01-harness-skills.md)で、単独Productに余分なSkillを入れる逆効果、曖昧コマンド、導入済みだが実Tool不在、read-only入口とwrite別入口、同名Tool版差、切断・部分成功、ロード実体の未観測、現在権限差を**同一合成Taskの正負対**として検証する。前段はメタ情報・契約の静的棚卸し、次段は実Harness/CLI/MCP/OS・独立Oracle。PlanだけではSkill有効性、実Tool接続、OS隔離、Owner受理を証明しない。

## 10. 2026-11-02：Skillの実入力束縛と発見面の開示資格（設計候補）

他チャットの[TEI #2605](https://github.com/hat47x/tei-platform/issues/2605)（実在CLI限定の最初のProduct Skill）、[TEI #2595](https://github.com/hat47x/tei-platform/issues/2595)（宣言Sourceと実使用byteの差）、[TEI #2515](https://github.com/hat47x/tei-platform/issues/2515)（全送出面）、[TEI #2516](https://github.com/hat47x/tei-platform/issues/2516)（Consumer別Claim）、[SEI #767](https://github.com/hat47x/sei-cognition/issues/767)（根拠十分性）をTAIのSkill評価へ接続する。各Productの内部Oracle/CLI/意味正本は各Ownerのまま。

### 10.1 SkillのSHA一致は、実際の手順全体を使った証拠ではない

レビュー済みのルートSkill文書と、配布Bundle、実SessionにロードされたSkill、参照先のreferences・scripts・URL先、MCP/CLIバイナリ、実際に読んだSource byteは別々の観測対象。root SKILL.mdのdigestが一致しても依存ファイルが差し替われば、実際の動作は変わり得る。次の資格を分け、必要な列だけSK-01へ追加する。

| 観測 | 残す参照 | それだけでは断定できないこと |
| --- | --- | --- |
| Reviewed | Skill/参照資料のSource repo・commit・digest | 実Harnessへのロード |
| Packaged/Installed | Bundleと依存scripts・Adapterのdigest、実配置先 | 当該Sessionの実消費 |
| Delivered/Loaded | 実配布され、直接観測できた断片とTool定義、実読取範囲 | モデルの内部理解・非計測の依存ファイル |
| Invoked | 実Tool名・argv・Process principal、CLI/Host版、実Sourceと出力 | 独立Oracleによる正しさ・本番許可 |
| Qualified/Effect | Claim・Scope・Grain・as-of・独立検証・必要な実Provider receipt | 別Harnessや将来版での同じ資格 |

実ロードbyteが観測不能ならunknownとする。Skillの自己申告で「使用済み」と認定しない。TEI #2595の実SourceとBuildの照合はTEIの実装Ownerに戻し、TAIではその結果の適用範囲だけを評価する。

### 10.2 発見段階にも情報開示がある

Skill名、CLI help、Tool schema、MCP tools/list、ErrorやCapabilityの件数だけでも、非公開の業務構造・顧客・Tenant固有機能の存在が分かる可能性がある。高機密Profileでは、discovery → invocation → result → final explanationを**別々の開示先・開示資格**で点検する。内部世界が異なるのに公開可能な一覧が同じであるべき二つの合成Tenantでは、一覧・Toolエラー・暗黙Skill選択から秘密を推測させない。

公開一覧を隠せたことはRawや別Portのアクセス拒否の証拠ではない。実OS/Server強制は[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)とTEI #2515を参照する。特定の問いを内部Productで評価する場合も、結果true/falseや拒否理由が秘密を漏らし得るため、用途限定の既存QueryとOwnerの開示Policyを使用する。任意Predicateを汎用Skillとして開放しない。

### 10.3 実在CLIを使った最初の対照

TEI #2605／[候補Draft #2607](https://github.com/hat47x/tei-platform/pull/2607)では、portable read-only Product Skill文書をTEI自身が保有し、実行入口のdiscoveryは全Plugin一覧ではなく限定したselected-read-only-commandsと報告されている。候補SkillのMarkdownがブランチに存在することと、実CLI/Harness稼働とは別。最初のTEI Skillは、実在が確認された model catalog、inspect、trace、validate -json 等に限定する。validateの終了コード0とok・diagnostics・Warningを分け、複数呼出しのworld/source fingerprintが同じSnapshotに対応するか確認する。モデル検査だけでOwner受理や外部Host上のJava/.NET/WASMの動作を保証しない。

Product単独利用（TAIなし）の対照H2↔H3を先行し、複数製品が本当に必要なケースでH4↔H5を実行する。Skill追加が有益とは限らず、同じ公開仕様・Tool版・入力Sourceと独立期待値を保持し、余分なTool呼出し・Context・開示・誤成功も計測する。

**責務と状態**：これは既存SK-G0〜G6・H0〜H7の詳細化であり、新しい中央Capability Registry/Agent Runtime/第二Authorityを追加しない。[SK-01のSK-E試験](../../evaluations/SK-01-harness-skills.md)を参照。実Skill/CLI/Harnessロード、二Tenant非開示、OS制御、正式受理はNOT RUN。


### 10.4 各Productでの並列受入作業（2026-11-02起票）

TAIが横断Skillの正本・AB比較・シリーズ配布を担当し、**各Productが専用Skillの具体的入口とテストを所有**する方針を、次の独立Issueへ還流した。

| Product Owner | 専用Skill検証のIssue | 既存Core/契約と切り分ける差分 |
| --- | --- | --- |
| TEI | [#2614](https://github.com/hat47x/tei-platform/issues/2614)（拡張範囲）／[#2605](https://github.com/hat47x/tei-platform/issues/2605)・[Draft #2607](https://github.com/hat47x/tei-platform/pull/2607)（現行read-only CLIの初期Skill） | 実CLIのread-onlyモデル調査を最初に実証。Modeler/DSL/Generator/Targetは段階的な別資格で、#2516のClaimと#2390のProvider意味を重複実装しない |
| SEI | [#769](https://github.com/hat47x/sei-cognition/issues/769) | Inquiry/Methodの手順と根拠/残余の引渡し。#767の独立Method/Evidenceを利用 |
| SUI | [#3368](https://github.com/hat47x/sui-sensemaking/issues/3368) | 許可されたAgent Projectionを使った意味探索。#3297の未決開示判定を先取りしない |
| SHO | [#10](https://github.com/hat47x/sho-composer/issues/10) | MMIの既存`mmi` Skillを利用し、文書/出典/説明/固定納品を別資格にする |
| EKI | [#468](https://github.com/hat47x/eki-fabric/issues/468) | Task/Attempt/Output/Resultの実在入口を使用し、#465のBody転送未解決を隠さない |

各Productの専門Skillは要求と受入計画を中心とし、TEIには**read-only入口の候補Markdown/Draft #2607**がある。実CLI/別Harnessの通し動作・本番OS許可・正式API/Owner受理は別資格。TAI #168の横断作業と、各製品実装の状況を混同しない。

## 11. 2026-11-02：Source改版から「利用者が受け取った一式」までのSkillの責務

他チャットの[TEI #2505／Draft #2615](https://github.com/hat47x/tei-platform/pull/2615)は原資料のA→B→C改版とConsumer別の影響を、[TEI #2604](https://github.com/hat47x/tei-platform/issues/2604)は複数Artifactの**物理公開と読取り一貫性**を分けた。[SHO #6](https://github.com/hat47x/sho-composer/issues/6)は文書と原Source・表示依存の受渡し、[EKI #465](https://github.com/hat47x/eki-fabric/issues/465)は実Runnerの出力BodyからSenderまでの断絶を具体化した。これらをTAIのProduct SkillルーティングとActivity再開の**失敗資格**へ還元する。各実装・OracleはそれぞれのOwnerに残す。

### 11.1 五層の同一性をSkillの「成功」一語に畳まない

| 層 | 何を区別するか | Skillが付けてよい報告資格 |
| --- | --- | --- |
| **S Source** | ZIP/member/view/atomと固定版の位置参照、実Source bytes | 特定版の出典を再取得・照合した |
| **C Correspondence** | A→B、B→Cの多対多の**対応候補** | 版間の候補経路と不明点を提示した |
| **M Meaning** | Ownerが受理したClaim/Rule・対象/適用範囲・版 | その意味受理を正本から確認した（候補≠受理） |
| **G Generation** | Target/Template/Generator/Rule版・出力実byte・Manifest/Findings | 指定入力から指定出力を生成・局所検証した |
| **P Publication/Consumption** | 完成したArtifact一式の世代、Consumerが実際に読んだファイル・Digestと開示先 | 同一世代の完成一式を当該Consumerが取得したことを観測した |

これはTEI #2615のS/C/M/G/Pを**評価の説明**に借りるもので、TAIの新しい共通意味Schemaや公式状態機械ではない。GのPASSからP、PのPASSから現在の業務意味・実Host/DB効果へ昇格しない。入力文書を受け取ったことと、SHOで著者が実際にレビュー・固定納品できたことも別。EKIではResultClaim/Claim ACKから**同AttemptのBody bytes**到着を推測しない。

### 11.2 Skillが作るのは「再評価の候補」であり、旧受理の自動移植ではない

A版で受理した説明をC版で使用する際、A→BとB→Cの個別候補が高確度でも、A→Cが一意・同義とは限らない。二要素がBで統合されCで再分割された場合、合成経路は複数。Skillは候補理由/曖昧性と利用先Claimを示し、現行Ownerによる用途別受理・再検証へ返す。**原本byteの同一、同一表面文言、同じhashの復活も現在適用の保証ではない**。Dependencyが明確な場合は影響の小さいConsumerだけを再評価候補にできるが、依存未観測を「影響なし」と断定しない。

SHOの説明文・引用出典・表示用画像/式・固定納品版と、TEIの意味モデル・Java/.NET/WASM出力は異なる派生系列。Templateだけが変わった場合にLibraryの業務意味を改版扱いすることも、意味が改版されたのに旧文書を自動承認することも避ける。

### 11.3 Artifactの物理公開をSkill操作結果から独立検証する

TEI #2604で現行未統合候補のSource-static所見となった**逐次上書き後にManifest書込み**のケースでは、R1一式からR2更新途中のエラーが起これば、Consumerに旧Manifest＋新しい一部ファイルが見え得る。消されたtableの旧ファイル残存やslug衝突も別負例。したがって、Tool exit 0／ManifestのComplete／生成物Digest／SHO Render成功は、**消費者が同じ完成世代を読めた証拠ではない**。

Skillの初期read-only経路は、実Product側の公開プロトコルが提供する場合、**一つの固定世代／Manifest参照を取得→列挙されたファイルの実byteを照合→旧残存物を公開一式へ混ぜない→対象Consumerの読取り状態を報告**する。Product側でsnapshot取得・不変の世代が提供されない場合は、同一世代の証明を捏造せず`unknown/partial`として既存Owner #2604へ返す。TAI Skillが独自にatomic writeや第二のArtifact Storeを実装する方針ではない。

### 11.4 機密ProfileではManifest・出力名自体を開示範囲に含める

Output filename、Manifest列挙、Subject ID・件数、対象バージョン、生成ログ、失敗箇所は非公開の構造を漏らし得る。外部Harnessへ渡すのはSource保持Product/実Hostの**許可済み公開投影と検証結果のみ**。内部で完全集合と同版byteを確認しても、詳細なManifestや検証Booleanを外部へ返せるとは限らない（TAI #232／TEI #2515/#2516）。Client Skillがファイルを隠しただけではOSでRawを禁止した証拠にならない。

[TAI #168のSK-C01〜06接続検討](https://github.com/hat47x/tai-pleroma/issues/168#issuecomment-6572833447)は**製品間のSubject/Source/時点/意味の対応**、本§11とSK-Jは**版間対応候補・物理公開世代・実成果物の送達**を扱う。横断H4/H5の「完了」にはどちらか一方の単体PASSでは足りず、必要な結合辺の実証が要る。

### 11.5 計画と検証Owner

[SK-01 §J](../../evaluations/SK-01-harness-skills.md)のSK-J01〜J07で、版間曖昧性、同版Template差分、混合世代、残存物、CompleteとFindings、EKI Body未送達、Manifestの存在推知を公開合成fixtureで対照する。TEI #2505/#2604、SHO #6、EKI #465に**各Productの実装・試験を委譲**し、TAIは単体Skillと横断Skillが誤った完了主張をしないか評価する。Skill/Tool/Consumerの実接続、実OS拒否、実Artifact公開・読取り、Owner受理は全て新規NOT RUN。P0は従来のSK-G0/G1とTEI #2605 read-only一件を維持し、拡張候補と検証Laneを並列増加してよい。

## 12. 2026-11-02：Markdownを「文書・モデル・テスト」として使う時のSkill適用境界

**Ownerの新しい横断方針**：TEI [#2619](https://github.com/hat47x/tei-platform/issues/2619)／[#2620](https://github.com/hat47x/tei-platform/issues/2620)／[#2621](https://github.com/hat47x/tei-platform/issues/2621)／[#2622](https://github.com/hat47x/tei-platform/issues/2622)では、**標準データ構造に意味Roleを適用して、Markdown／表／式／構造UIから定義・例・テストを扱う**設計が具体化された。一方、[SHO #7](https://github.com/hat47x/sho-composer/issues/7)／[#8](https://github.com/hat47x/sho-composer/issues/8)／[#9](https://github.com/hat47x/sho-composer/issues/9)は、リンクだけでも成立するResearch Index、論文→設計→プログラムの根拠連鎖、通常テキストとの対照を所有する。

**横断Skillの仕事は文書全体に単一の実行意味を与えることではなく、利用者の目的に沿って、文書のどの部分をどのProductの実在能力へ委ねられるか判断すること**。TAIに共通Parser/DocDB/Script Interpreterや第二のTEI意味正本を作らない。Role付与・Context Mapping・Studio実装はTEI、文書原文・Occurrence・Research IndexはSHO、参照再解決はSHO/MMI既存Owner、Methodの問いと十分性はSEIが保有する。TAIはSkillの選択・受渡しと成果の過大主張を比較する。

### 12.1 三つの独立した境界：Authoring／Meaning／Materialization

| 境界 | 具体例 | AI/Skillが行えること | 確認すべき別資格 |
| --- | --- | --- | --- |
| **Authoring Source** | Markdown文章、リンク付き階層、表、計算式、テスト例 | 原文とSource span/文書版を読取り、説明/候補を提案 | 明示Roleの有無。説明文や全表をFunction/Testとして自動起動しない |
| **Semantic Binding** | Data Model Relation、型付きFunction、Rule、Function Data Context | TEI側が認識するRole/Operator/ID、型・単位・grain、明示Mappingを読取る | どの候補が解決・Owner受理済みか。Relationは**アクセス可能な関係**であり、その存在だけで全Relationを取得しない |
| **Materialization / Effect** | ProviderのData fetch、Derived Dataset、生成コード、ViewChange→Action、実Test | 実在CLI/Hostで許された対象だけを照合し、実取得Scope・Read-set/版を記録 | 取得権限・必要完全性・NULL/未取得、Generator/実Provider、非可逆書戻し、業務Owner受理、実Output/外部Effect |

例えば親注文→明細→割当のData Modelが存在しても、Function Data Contextで指定したRelation path/Field/粒度/Scopeの取得だけが候補となる。**AI向け補完は未採用候補として可視化し、暗黙取得・隠れたJOIN・実行済みread-setへ昇格させない**。通常の取得/集約にはTEIの標準Data Operations（名称は仮称）を利用する構想で、Native SQLは明示した例外的な実装Binding。TEI #2622でのProviderごとのread/filter/expand/aggregate/PATCH/full-replace/atomicity差をTAI Skillが隠さない。

### 12.2 一つのMarkdown内のRoleは、部分ごとに確認する

同一Markdown中の一般の表、説明用計算例、型付きFunction表、独立Expectedテストは**見た目が似ていても同一のRoleではない**。TEI #2621ではProfile/見出し/宣言されたRoleによる識別、曖昧な場合の候補提示と明示的な確定を提案している。

- **記述→候補**：自由文・表・式に対し、AIが「Functionかもしれない」と提案できる。説明用表を実Testや実Functionとして自動実行することは別。
- **Role Binding→意味候補**：Ownerが確定したSource span/意味ID/Role/Operator版、型・丸め・NULL・単位・時点を参照。簡潔な式だけを見て丸めやNULLの規則を補完しない。
- **Expected→独立評価**：文書内のExpectedは人が提示した期待・Independent Oracleの入力候補。生成コードが再計算したExpectedを独立証拠として使わない。Testの「定義済み」「実行済み」「結果確認済み」は別。
- **Studio→構造Projection**：同じ意味IDを表・Tree・Graph・式・モデルInstanceとして投影する契約はTEI側で検証。TAI Skillは表示が似ていることから異なるSource/Roleを誤同定しない。

### 12.3 「論文を索引に入れた」ことと「原典を読んだ」ことを分ける

SHO #7のL0はMarkdown見出し・字下げ・リンクURLだけで完成する独立した研究活動。リンクの親子は第一に**整理上の包含/順序**であり、論文AがBを引用/発展/反証したという学術関係ではない。同一URLの複数Occurrenceと、論文原典Identity・版は別。

外部AIが次に行えるのは、(a)リンク集を保存・並べ替える、(b)原文取得候補を提案する、(c)実Source/権限を確認して許される場合だけ取得し、(d)取得済みの節/式から根拠付きClaim・Designへ進む、という**段階的な選択**。SkillはURLだけで未取得論文の内容・数式・学術関係を創作しない。ユーザーがリンク整理だけを求めるときは、SHOの単体入口が存在する場合にはTAI/TEI/SEIを読み込む必要がない。

論文→設計→プログラム（SHO #8）では、source-stated／interpretation／design proposal／TEI accepted model／executed targetを分ける。**TEIを使わずSHO＋外部コードRepoだけで実装する選択も有効**。構造化による実価値はSHO #9のA0/A1/A2、B0/B1/B2の同資料・同予算比較で測り、AIの理解が自動的に向上したとは先取りしない。

### 12.4 Skillが現在の対象を扱う際の正負対と受入の組立て

[SK-01 §K](../../evaluations/SK-01-harness-skills.md)にSK-L01〜L10を配置する。公開の合成Fixtureで(A)未Role表、(B)明示Roleと未解決の型・丸め、(C)Relationは存在するがContextは限定、(D)集約Projectionと非可逆編集、(E)論文L0しか存在しない状態を固定し、**Skillなし／Product Skill／TAI横断Skill**で目的達成と不要な取得・未確認の保持を比較する。

**Data取得の要否・開示・実観測は別**：`model_has_relation=true`、`context_mapped=true`、`source_access_authorized=true`、`read_observed=true`、`complete_for_claim=true`は別。これらは評価列の説明で、TAIの新しい共通モデル型ではない。Contextのない問い合わせで暗黙に取得したり、ローカル閲覧可能なRawを外部LLMへ送ったりしてはいけない。**通常のTEI内組織Dataすべてに特別OS隔離を課す方針ではない**。秘密指定Sourceや外部Host/AIへの送出時は[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)の実境界を参照。

**既存の受入順序と拡張**：SK-G0/G1・TEI #2605の実CLIを先行し、L01/L02（SHOリンクの未取得）、L03/L04（Markdown Role/Expected）、L05〜L08（TEI明示Context/非可逆保存）、L09/L10（根拠を保った研究→設計の段階）を独立Laneで追加する。大量AI並列開発では候補の種類を増やしてよいが、各Productの実行受理・外部送信・実Provider・Owner判断の証拠は単純加算しない。

**状態**：設計・SK-01の追加試験候補。TEI #2619〜2622とSHO #7〜9は現時点でIssue上の設計であり、正式Core/Studio/Markdown CompilerやSHO単体保存・Paper→Code E2Eの実動作を確定していない。SK-L全件・実Tool/Harness・Source/DB/Host・OS拒否・正式Owner受理はNOT RUN。


## 13. Semantic Action Affordanceと外部HarnessのSkill選択（2026-11-02）

**成熟した接続点**：[TEI #2507](https://github.com/hat47x/tei-platform/issues/2507)のSemantic Context起点の汎用Action、[#2500](https://github.com/hat47x/tei-platform/issues/2500)のViewChange逆写像、[#2586](https://github.com/hat47x/tei-platform/issues/2586)の一Function Headless縦断、[#2622](https://github.com/hat47x/tei-platform/issues/2622)の汎用Data Operationsを、TAI横断Skillが利用する**能力選択の入力**として位置付ける。具体的な境界・受入は[Semantic Action Routing設計](harness-skill-semantic-action-routing-2026-11-02.md)。

TAIの責務は利用者の目的・対象・時点から**実在する製品と適用可能な能力を選び、必要な許可済み根拠/Resultへつなぐこと**。TEIのAction適合判断・Type/Role/Read-set・Operation Intent・Provider/Host権限をTAIに再実装しない。**同一Meaning ActionをTable/Form/Graph/CUI/外部Harnessで異なるAffordanceとして提供**する構想はTEI #2507/#2500のOwner。SkillがActionを発見した事実を、表示資格・現在の実行許可・Receipt/Business完了へ自動昇格させない。

[SK-01 §M](../../evaluations/SK-01-harness-skills.md)では、L1を異なるUI/CUIから参照する同一性、Chart aggregate更新の逆写像不能、D2の部分取得での全件操作、Graph edgeとEntityの差、JOIN行とEntity数、stale epoch、secret CapabilityのDiscovery、Provider ACKの未完了、Event等の専門Operationを10件の合成反例として追加する。公開[fixture](../../evaluations/fixtures/SK-M-semantic-action.synthetic.json)と[Node selfcheck source](../../evaluations/tools/check-sk-m-fixture.cjs)を付けた。V8で**公開fixture内の宣言と分類の限定整合10/10を確認**した[記録](../../evaluations/records/SK-M-public-fixture-selfcheck-2026-11-02.json)があるが、**Node runner自体・TEI実CLI/Pattern・実Harness/OS/権限/Effect・独立sealed OracleはNOT RUN**。Product側実装・意味/権限の受理は従来Ownerへ委譲し、TAIはH2/H3/H4/H5でSkillを追加する価値だけを評価する。



## 14. 2026-11-02：Capabilityから製品Skillへ派生する参照とドリフト検証

[設計・評価計画](capability-derived-skill-projections-2026-11-02.md)に、TEI [#2620](https://github.com/hat47x/tei-platform/issues/2620)の「Plugin schemaからのSkill生成・版固定」構想をYI全体の**責務境界**として接続した。

製品自身の意味Role/Operator・実CLI/API/MCP契約から**技術的に照合できる説明をProduct Skillへ参照・投影**し、課題別の使い方や専門MethodのRecipeは各Productが独立に編集する。TAIの活動SkillはProductの意味/ツール契約を複製せず、必要なProductとSkillの選択・引継ぎを行う。DSL表層（Markdown表・式・Graphviz・チェーン）と正規化された意味が一致する場合、表層ごとに別の実行能力を宣言する必要はない。未確定Role、引用中の例、Source構文の類似から受理や実行許可を推定しない。

同じ意味Roleでも、Provider/Target/Scope、実CLI/Tool版、Agentへの公開範囲、SkillのReferences/Scriptsと実ロード、現在の権限/Effectは別の観測対象。[SK-01 §N](../../evaluations/SK-01-harness-skills.md)にSK-D01〜D10を追加して、Source/Meaning/Capability/Skill/Adapterの版間ドリフトとDisclosureを評価する。**初回P0はTEI #2605とDraft #2607のread-only Skillと実CLI H2/H3の比較を維持**する。全製品用の新共通Skill Compilerや共有Registryを先に確定せず、実際に重複と誤案内が減るかから判断する。

**状態**：構成・評価計画のみ。自動投影の実装、実Skill/CLIロード、複数Harnessでの実証、Product意味/OS認可/外部Effect/Owner受理はNOT RUN。

## 15. 2026-11-02：Skillが参照する「信頼の現在性」と失敗時の縮退

**新たな横断反例**：[EKI #466](https://github.com/hat47x/eki-fabric/issues/466)ではIssuer Fingerprintの二重SHA-256、[#467](https://github.com/hat47x/eki-fabric/issues/467)では**導入済みTrust Bundleの読取エラーを「未設定」と同じfalseへ畳み、現行版検査を省略し得る**経路がSource-staticで指摘された。これは実mTLS攻撃・本番バイパスの実証ではなく、EKI #433の製品Ownerが修正・検証する個別Blocker。外部Harness向け[EKI Skill #468](https://github.com/hat47x/eki-fabric/issues/468)と、TEI/SEI/SUI/SHOのProduct Skill群に**「SkillやToolの見え方」と「現在のTrust/開示/実作用の資格」を分ける**横断評価を追加する。

### 14.1 失敗情報は「未導入」「現行版」「検証不能」「不正/失効」に分かれる

| 実際に観測したSource/Host状態（合成） | 正しい行動の候補 | 誤った合流 |
| --- | --- | --- |
| **未導入**：明示された旧互換profile、従来認証は有効 | **Ownerが互換性を認めた場合に限り**従来経路へ進む。全許可ではない | 未導入をあらゆる「読めない」の代替にする |
| **導入済み・現行版読取成功** | 最新Bundleのissuer・期限・revocationと既存CA/Registry等の認証を段階確認 | Signed Bundleが存在するだけで本人のAction・Grantを認可 |
| **導入済み・I/O error／破損／過去導入後NotFound** | 版を検証できない接続は実Hostが**安全側に拒否／unavailable**。正確な内部理由の外部開示はPolicy別 | errorをfalse/noneとして旧CAへfallbackし、失効状態を復活 |
| **現行版でissuer除外・期限切れ** | 現行規則に従い拒否、証拠として有効な版と独立Oracleを参照 | 昔の成功receipt・旧Skillの案内で再許可 |

これは全製品一律の失敗State enumではなく、**異なる意味の観測値を消さない**というSK-01評価の要点。失効時の明確な拒否と、そもそも互換モードが正式に許可されている正例を両方確認する。SEIの`unknown`と`negative`、SUIの`not disclosed`と`nonexistent`、SHOの`not fetched`と`content-empty`でも同様の誤合流を調べるが、各Productの正式状態型を共通化しない。

### 14.2 同じハッシュ関数を検証側でも使うことは、独立Oracleではない

EKI #466の特定実装では、要求が「CA DERのSHA-256一回」である一方、コードが`sha256(sha256(DER))`を返すことが分かった。テストExpectedまで同じ`IssuerFingerprint`を使えば実装とテストが**同じ誤り**を共有し、自己整合PASSになり得る。SK-01の`Skill digest / Source fingerprint / Artifact manifest / Issuer fingerprint`は役割・対象byte・アルゴリズムを明示して比較し、単に「sha256」ラベルや両側一致で外部互換・現在Trustを保証しない。独立Expectedは標準hash／外部生成DER等を使い、機密SourceのDigestやTrust Bundle本文を低権限Harnessへ無断公開しない。

### 14.3 Product Skill群とTAI横断の責務

2026-11-02に各製品のSkill **Issue候補**が出そろった：[TEI #2605／Draft #2607](https://github.com/hat47x/tei-platform/issues/2605)、[SEI #769](https://github.com/hat47x/sei-cognition/issues/769)、[SUI #3368](https://github.com/hat47x/sui-sensemaking/issues/3368)、[SHO #10](https://github.com/hat47x/sho-composer/issues/10)、[EKI #468](https://github.com/hat47x/eki-fabric/issues/468)。**起票済みであることはSkillの実インストール・動作・Owner受理を意味しない**。TAIは「実Toolを選ぶ」「許可された情報/結果だけを引継ぐ」「現在の実資格を再確認する」ための横断Skillを持つ。Trust BundleのParser/署名検証・mTLS Listener・CA更新、認証の正本はEKI #433/#466/#467に保持する。

外部Harness A→Bの引継ぎでは、**Skillの固定Digest、Task/Attempt結果の実証、Issuer/Policyの現在版、Consumerの現在権限は互いに異なる**。Aで成功したTrust/GrantをBへ移すことはできない。接続の前に既存Product/Hostへ現時点の認証・開示を確認し、失敗なら該当の危険な作用だけを中止する。**公開の合成資料を使った調査、文書下書き、Sourceの局所整理は別に続けられる**。

### 14.4 受入へ：通常系／障害系／回復系を一対にする

[SK-01 §N](../../evaluations/SK-01-harness-skills.md)に、未導入互換・現行issuer・失効issuer・Bundle読取障害・不正record・導入後喪失・独立SHA一回vs二回・Harness再開・開示用診断を含む**SK-TB**対照を設計する。試験は**合成fixtureだけ**で開始し、EKI実証は[#433](https://github.com/hat47x/eki-fabric/issues/433)のOwnerへ、外部送信・情報開示は[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)へ引き渡す。型・時間・意味・認可の実検査がない他Productに同等の状態管理を強制しない。

**状態**：本節は各Productの最新Issueから成熟した失敗境界を横断評価へ整理した**計画**。公開合成SK-TB 9件の[Node.js再実行Script](../../evaluations/tools/check-sk-tb-fixture.cjs)は、固定fixture/ScriptがGitHub Blobと完全一致する環境で**9/9の限定セルフチェックPASS**（[記録](../../evaluations/records/SK-TB-public-fixture-selfcheck-2026-11-02.json)）。期待値が公開されており、外部Harnessの独立能力試験ではない。実EKI mTLS、Trust Bundle migration、Skill経由作業、別Harness現在認可、OS/Network送出の正負試験は**NOT RUN**。トークン大量調達を前提に探索領域は並行拡張しつつ、実証資格は各Ownerに維持する。

## 16. 2026-11-02：Requested／Rule／Actual Read／Disclosureの接続

[新設計・Owner接続表](harness-skill-read-witness-rule-disclosure-2026-11-02.md)に、TEI [Draft #2624](https://github.com/hat47x/tei-platform/pull/2624)のDisplay Mapping≠Rule依存（合成20+18件）、TEI [Draft #2628](https://github.com/hat47x/tei-platform/pull/2628)のOutput同値≠実Provider取得範囲（合成12件）、SEI [Draft #770](https://github.com/hat47x/sei-cognition/pull/770)のClaim相対十分性・複数Read版混合・Planner Discovery時の情報開示を**各Ownerの独立Evidenceのまま**組み込んだ。

**横断Skillの追加機能候補**は、Declared Mapping（D）→Rule Dependency（R）→Realized Request（Q）→実Read Witness（W）→Claim Qualification（C）→Consumer Projection（P）→Actual Egress/Effect（E）の**必要な証拠がどこで観測されたかと、どこから不明かの連結**。このD/R/Q/W/C/P/Eは評価の説明列であり、TAI独自の共通実行Schema、全情報フローEngine、第二Provider/Policy/Claim正本ではない。

**新たな重要反例**：画面がOrder Amount 600のみ表示していても、与信Ruleの評価は内部Credit Limit 700/500で変わり得る。一方、そのRule結果のBoolean自体を外部AIへ公開できない場合、どちらの世界でも開示済み情報から結果を判別させない。読取り結果が同じでもProviderが秘密Fieldを追加で取得した可能性があり、Adapterのread-only TraceをDB物理I/Oの保証と混同しない。最終回答の非開示だけでなく、Tool/Skill発見・Planner候補・途中のAPI呼出し名による存在推知を検査する。

[SK-01 §P](../../evaluations/SK-01-harness-skills.md)にSK-F01〜F12と、[公開合成fixture](../../evaluations/fixtures/SK-F-access-rule-disclosure.synthetic.json)、[整合チェッカー](../../evaluations/tools/check-sk-f-fixture.cjs)、[限定V8記録](../../evaluations/records/SK-F-public-fixture-selfcheck-2026-11-02.json)を追加。**GitHubから再取得した正確なscriptとfixtureをV8上でfs-shimを用いて実行し、公開期待値との自己整合12/12を確認**。Node.js環境での実行、ProductのRule/Provider/実DB監査、外部Harness/OS/Network、独立holdout、Owner受理は**NOT RUN**。H2/H3とH4/H5ではProduct単独Skillとの比較と、機密/完全性/誤成功の検出を別軸で測る。

**採用上の先後**：既存TEI read-only CLI実利用（#2605）→現ProductのRule/Providerの実根拠→必要なProduct間データ連携→外部Harnessの消費・開示/送出と実効権限。候補探索と独立PoCは並列に増やしてよい。局所合成PASSを一Activityの業務成果受理として扱わない。

## 17. 2026-11-02：変更後の選択的再資格化と共同Claim（SK-RQ）

[新しい設計・受入表](harness-skill-selective-requalification-2026-11-02.md)へ、[TEI #1445 H8-P13/P14](https://github.com/hat47x/tei-platform/issues/1445)（検証費用と共同Claim）、[#2582](https://github.com/hat47x/tei-platform/issues/2582)（局所依存・非単調なDerived結果）、[SEI Draft #770](https://github.com/hat47x/sei-cognition/pull/770)（問いQ相対の十分性・観測同値類・複数Readのepoch混合）、[TEI #2628](https://github.com/hat47x/tei-platform/issues/2628)（Output同値と実Read Witnessの非同値）、[SHO #6](https://github.com/hat47x/sho-composer/issues/6)、[EKI #467](https://github.com/hat47x/eki-fabric/issues/467)を既存各Ownerとして接続した。

**横断Skillに必要な一段先の能力**は、単にProduct結果を結合するだけでなく、**何が変更されたとき、どの既存Claim／Skill／Document／公開一式を再確認し、何を履歴として保持できるかを根拠付きで区別すること**。Source/Rule/Oracle/Skill/Template/Policy/Trustの影響先は異なる。依存不明なら「影響無し」を保証できず、実Provider Read/共同Snapshot/開示資格も別。過去の成功を歴史として保ちながら、現在のActionとEgressは実Product/Hostが再認可する。CSW/SUIの自由な探索には採否ゲートを追加しない。

**比較候補**：R0全面再検証、R1依存に基づく選択的再確認、R2未観測依存や共同Snapshot不足の限定保留。なお別レーンで起票された[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)／[Activity継続の依存・Handoff試験](activity-selective-requalification-and-handoff-2026-11-02.md)を横断Activity側のOwnerとし、SK-C01〜15の**依存閉包／実到達**と、SK-RQ01〜12の**Claim別再資格化**を明確に分担する。#271の`J2=旧成功を無検証で採用する負例`と本節の`R2=未知だけを安全に保留`は異なるので、**J2≠R2**。ラベルだけを一つにまとめない。正しい再利用数だけでなく、`false reuse`と`unnecessary invalidation`の双方、適切な危険作用の保留と、継続可能な独立read-only作業を別計測する。TAIへ第二の依存解析器／共通Snapshotサービス／中央Policy・Authorityを作らず、各製品の実Source・Oracle・変更通知を参照する。

[SK-01 §Q](../../evaluations/SK-01-harness-skills.md)にSK-RQ01〜12を追加し、[公開合成fixture](../../evaluations/fixtures/SK-RQ-selective-requalification.synthetic.json)と[Node用再実行Script](../../evaluations/tools/check-sk-rq-fixture.cjs)を保存した。GitHubに保存されたfixtureをV8参照分類で**12ケース／14項目の自己整合PASS**（[限定記録](../../evaluations/records/SK-RQ-public-fixture-selfcheck-2026-11-02.json)）。**Nodeスクリプト自体・実Product/Tool/AI Harness/OS/Provider・独立sealed Oracle・Owner受理はNOT RUN**。公開Expectedは盲検ではない。

**評価順**：SK-G0・TEI #2605実read-only→RQ01〜03の過少/過剰再確認→RQ07の共同ClaimとSource時点→RQ05/06の実権限／開示→H2/H3 Product Skillありなし→H4/H5横断Skillの追加価値。並列探索範囲を広く取りながら、実行資格は各製品の正本へ戻す。

## 18. 2026-11-02：Activity継続の選択的再資格化とProduct横断Handoff

[新しい計画](activity-selective-requalification-and-handoff-2026-11-02.md)と[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)に、TEI [#2586](https://github.com/hat47x/tei-platform/issues/2586)/[#2516](https://github.com/hat47x/tei-platform/issues/2516)のClaim相対・局所結論と、SEI [#767](https://github.com/hat47x/sei-cognition/issues/767)の問いQ相対の限定十分性、EKI [#465](https://github.com/hat47x/eki-fabric/issues/465)のClaim ACKとBody受取の断絶、SHO [#10](https://github.com/hat47x/sho-composer/issues/10)の文書読取/納品資格、TAI #168のHarness交換・活動再開を統合した。

**成熟した設計判断**：履歴における有効な観測（Historical Evidence）と、その証拠を現在の目的・Source/epoch/Scope/Host/Consumerに使える資格（Current Qualification）を区別する。**変更を受けた依存Claimだけ**再評価し、正当な旧記録は履歴として保つ。依存線が不明なら無影響を宣言せず、必要な確認を追加する。Skillが既存ProductのAuthority、意味受理、DB Read/Result本体の実観測を代行しない。

比較軸は、**J0全面再検証／J1依存限定の選択的再資格化／J2旧成功の無検証再利用**。J1では見落とし・過剰再検証・Tool/Token/人のReview・情報開示・実作用誤成功を別々に測り、単なる作業回数削減を品質向上とは呼ばない。

[SK-01 §R](../../evaluations/SK-01-harness-skills.md)へ**SK-C01〜C15**を追加し、公開の[依存/委譲Fixture](../../evaluations/fixtures/SK-C-continuation-requalification.synthetic.json)と[自己整合Checker](../../evaluations/tools/check-sk-c-fixture.cjs)、[限定V8実行記録](../../evaluations/records/SK-C-public-fixture-selfcheck-2026-11-02.json)を接続した。GitHub保存済みJS・JSONのexact bytesをV8＋fs/path Shimで評価し、**公開合成15/15整合、Mutation負例4/4検出**。**実Node.js実行、実Product/OS/外部Harness、Owner意味受理、EKI Body送達/SHO実読取、独立sealed OracleはNOT RUN**。これはTAI/TEI/EKIの製品仕様採用ではなく、Draft設計・反証用Corpusである。

**相補的な評価**：SK-RQはClaimの現在性・変更による再確認の必要性とUnknownの保持、SK-Cは明示されたCross-Product依存線・EKI Body・SHO Consumer Read・Grantまでの継続/Handoffを対象とする。RQのR2は不明箇所だけを保留する安全側の対照、CのJ2は旧成功を無検証で転用する危険な負例であり、同じ再実行方針を意味しない。


## 19. 型付きConnectionとModel of ComputationのProduct間Handoff

[型付き接続と計算文脈のConsumer設計](typed-connection-handoff-and-computation-context-2026-11-02.md)を追加し、TEI #988/#2507/#2620/#2586の最新の「接続そのものの意味」「Graphvizを文脈付き標準Data変換として扱う」構想を、TAIのProduct選択・活動継続に接続した。

接続は、**参照／データフロー／Event／Control Intent／Constraint／Observation／Evidence依存**など、意味Role・解釈版と実際の成立証拠で区別する。図の `a -> b`、Markdownの字下げ、Skillのリンク、Tool Callの記録から、実Read/Commit/Effect/Consumer receipt/Business受理を推測しない。**Model of Computation**（Batch Snapshot／Reactive／Event Stream／Async Attempt／Transaction）とClock/epoch/順序もClaimの成立条件に含める。

具体例は、(1) `filter(q>0)`の選別と**元母集団の全称Validation**は別、(2) `|x−x̂|≤0.01`という上流近似が下流非線形関数/閾値Actionを保証するとは限らない、(3) EKI Claim ACK／Body受領／SHO実読取／納品は異なる段階、(4) 文書の参照やDOTの単なるEdgeは実依存・実権限・学術的引用の確定ではない、の四群とした。

[SK-01 §S](../../evaluations/SK-01-harness-skills.md)にSK-CE01〜16を置く。既存SK-RQ/SK-CがEvidenceの変更依存・再資格化を扱うのに対し、SK-CEは**Edge意味と計算時点の取り違えによる誤結合**を検出する。各意味のOwner/Oracleは既存Product側に残し、TAIは実在するProductの結果を用途相対に引継ぎ、別の中央Graph/Role Engine/Hostを作らない。

**資格**：Markdownの設計と受入ケースのみ。TEIの実DSL/Operator/Provider、Product間接続、実Clock/Event/Host、Agent Skill load・Owner意味受理・独立OracleはNOT RUN。複数製品の局所Reference PASSを横断E2Eへ昇格させない。

## 20. 2026-11-02：合成評価の拡大と最初の実Product観測を分けて進める

[最初の実Product Skill資格確認Runbook](first-real-skill-qualification-runbook-2026-11-02.md)を追加した。TEI mainの`docs/getting-started.md`・`cmd/tei/cli_contract.go`を静的に再照合し、**実CLIの存在を文書上で確認できる範囲**と、実環境で実Toolを呼んで観測すべき範囲を分けた。これは今まで増やした公開合成SK-M/TB/F/RQ/C/Jなどを縮小する方針ではない。開発の対象とProduct Skill候補を引き続き並列拡張する一方、**品質・実装の成熟度として主張する証拠**は次の実測に進める。

| Work lane | 最初の可動単位 | 「次の段階へ進んだ」と言える最小観測 |
| --- | --- | --- |
| **L0 Product単体** | 権限のあるcheckoutで、TEIの実在read-only CLI（commands/catalog/inspect/validate）を利用。TEI #2605/#2607 | binary/Go/OS/worktree、CLI version、実argv・実Output、Source fingerprint・Warningとunknownを記録した。TAIは不要 |
| **L1 Skill増分** | 同Harness・同Source・同ToolでH2（Toolだけ）対H3（TEI Product Skill追加） | Product Skillの実ロード範囲・呼出し差・誤判断/Tool時間・人の確認負担を比較。期待値をSkillへ与えない |
| **L2 製品横断** | 現在のMMI参照観測＋TEIモデル読取、必要な対象だけH4 vs H5 | MMI Source→TEI Meaningの根拠のある対応と、別Source/不明の分離。SHO保存やEKI Bodyを仮装しない |
| **L3 Activity再開** | TAI #271の限定したSource/Policy差分を利用したA→B Harness引継ぎ | historical evidence/current qualification、現在Host Grant、実Consumer read、再確認対象の選別を実観測 |
| **L4 機密／実作用** | 該当Productの実Profile・Provider側で拒否試験 | OS/HostのRaw・Capability・外向き通信・現在Trustの実拒否と、同Attempt成果物／業務Effectの独立観測 |

**実受入に向けて先に解決・確認する依存**：TEI #2605の実CLI S1／TAI SK-01 H2/H3が最初の候補。SHO Research Indexは作者のMarkdownとLink構文索引（SHO #7／Draft #12）から原文取得・文書保存・納品へ自動昇格させない。EKI #465のRunner→Body SenderはSource-static上の実配線課題であり、Body送達E2E前に既存Ownerで確認する。SEI #767の公開合成世界への限定十分性／Planner候補の機密性を、外部AIへの実Q判定/実OS開示保証に昇格しない。TAI #271の依存Graphは公開合成で15/15の自己整合を持つが、現実の依存線抽出・Owner受理は未実施。

**合格の帰属**：L0のProduct read-only実測、L1のSkill増分、L2の意味接合、L3の現在再資格化、L4の強制拒否/実Effectは**互いに独立した証拠**。一部成功を横断E2Eと称さない。同じSource名でも実byte/Source revision、同じSnapshot labelでも実epoch/Scope、Tool exit 0でもWarning、Trust歴史でも現在Grant、Manifest Completeでも実Consumer読取を別観測にする。公開fixtureにはExpectedを含むため、実Skillの独立能力比較には封印した評価側のケースを用いる。

**状態**：Runbookと順序・責務の計画追補。実TEIビルド/CLI、別HarnessのH2/H3/H4/H5、SHO/EKIの実Artifact・OS/Networkの負例、Owner採用は**NOT RUN**。新共通Host/中央Registry/第二の証拠正本/万能Agentは追加しない。

## 21. 2026-11-02：回答前の観測面と実HTTP受信byteをSkill資格へ接続

別Draft [TAI #272](https://github.com/hat47x/tai-pleroma/pull/272)の[横断観測面計画](https://github.com/hat47x/tai-pleroma/blob/docs/preanswer-observation-surface-20261102/docs/yi-constellation/preanswer-observable-surface-and-consumer-handoff-2026-11-02.md)を、本Draft #270の「何をSkillが実際に外部へ出したか」の**実測可能な範囲**へ接続する。SEI [#767/#770](https://github.com/hat47x/sei-cognition/pull/770)の公開Planner候補、TEI [#2507](https://github.com/hat47x/tei-platform/issues/2507)の隠れたAction/Route、SHO [#7/#12](https://github.com/hat47x/sho-composer/pull/12)のMarkdown Link TokenとRenderer anchorの差、TAI #232の実OS/Host開示境界をそれぞれのOwnerから参照。**TAIへ新しいPolicy Engine/Planner/Renderer/MCP Serverを追加するものではない**。

**新しく取得した限定実行証拠**：[PR #272のNode HTTP loopback Receiver](https://github.com/hat47x/tai-pleroma/blob/docs/preanswer-observation-surface-20261102/evaluations/tools/check-preanswer-loopback.cjs)が、実際のPOST bodyを9回受信し、**6/6局所合成試験PASS**（[記録](https://github.com/hat47x/tai-pleroma/blob/docs/preanswer-observation-surface-20261102/evaluations/records/AS-LB-loopback-http-2026-11-02.json)）。HTTP bodyのbytesが同じか／非公開Tool名やSession Eventの**架空Canary**が実際の受信bytesに入ったかを観測した。LB-02/LB-03のPASSは**わざと漏らす合成模擬系を検出した**意味で、実Productの防御成功ではない。実Node v22.16.0、Linux、loopback `127.0.0.1`のみ、Product/OS/SDK/Harness/実Browserは**NOT RUN**。

この試験が追加したのは、従来AS-01〜12の**純粋な合成値比較**から、`serialized payload → http.request → local Receiver → actual received bytes`までの1本の**実Transport観測経路**である。これにより「モデル本文・最終回答は同じだが、実受信Session Eventだけ違う」ケースを実HTTP bodyで区別できた。ただし、Mock宛のRequestだけを見ても、別Port/DNS/Tool/Log/Clipboard/外部Model Providerへの漏出**不存在は証明できない**。

### 21.1 SK-01に引き渡す厳密な対照

- **同一公開Projectionの二世界**：内部Hidden Actionの有無だけを変える。Audience/Purpose/Release Profile/Tool listを固定し、提供できる最終回答だけでなく、外部に露出した`offered tools / selected tool / request args / response / session events / rendered links / error`を観測。最初にTool-only H2で同条件、Skill追加H3でも同条件を維持する。実Toolの有無が不明なら`unknown`、推測コマンドは使用しない。
- **意図的に許可公開を変える正例**：Owner/Hostが公開可能なTool集合を増やした場合は、公開候補に差が生じても正当。秘密だけ変えた場合の差と分け、情報を隠すために正常な機能まで一律停止しない。
- **実Renderer差は別実験**：SHOのLink token一覧が同じでもraw HTML profileで実anchorが異なり得る。NodeのloopbackテストはDOMやa11yを実生成していないので、実SHO/Browser Rendererを持つProduct Ownerが別途検証する。
- **実Egress資格はHostで**：外部LLM/MCP/Browserへ送る実Data/Toolの現在資格はSource保持Product/実Hostが判定する。TAI #232で機密ProfileのOS直アクセス・別Port・Session/Network/Timing/Logを別に観測し、Clientのread-onlyやSkillの説明を防御資格へ転用しない。
- **非決定的Agentの比較**：実Harnessが確率的に異なるTool提案や順序を返す場合、単一回の本文byte不一致だけでは「秘密の存在を推定した」証拠にしない。同一Model/設定/公開入力を揃え、実Traceを複数試行で採取して差の再現・原因を独立分析する。逆に数回の一致で**全経路の非干渉を保証しない**。

[SK-01 §U](../../evaluations/SK-01-harness-skills.md)を観測面の横断受入表とする。最初の実TEI Skill Runbook（§20）は依然優先し、**今回の局所Mockの6/6をTEI CLI S1/H2/H3やTAI H4/H5の実行済みと扱わない**。独立Product Skillの用途は拡張してよいが、ProductのSource/Meaning、現在Host Grant、実公開・納品の資格は引き続き別である。


## 22. 2026-11-02：実CLI観測の到達、Role依存閉包、Test-as-Dataの独立性

[実Product Skill資格確認Runbook §7〜8](first-real-skill-qualification-runbook-2026-11-02.md)で、従来の静的・公開合成評価だけだった証拠に、TEI [Draft #2626](https://github.com/hat47x/tei-platform/pull/2626)の**実Go CLI Read／同一Read WitnessからのAI JSON・人間Markdown二投影**を新たに対応付けた。PR HEAD `31c62e8bb44c1c5c59933a46924aa4c338637085`の[GitHub CI #41456256348](https://github.com/hat47x/tei-platform/actions/runs/41456256348)は**2 Job successを確認**。実CLI 9プロセスによる限定観測、Source/World指紋、Catalog/Trace/Validate、二素材を同Jobで個別に再読取した資格のみ主張できる。

**次のProduct成熟階段**は、①実Product Tool観測（部分成立）、②既存TEI Product Skillを実ロードして同Source・ToolのH2/H3で改善を測る（未実施）、③二Productの別Reader・独立意味/Sourceを接続するH4/H5（未実施）、④別Harness/現Grant/実Effect/Current Requalification（未実施）。**TEI CI successをTAI Skill install・SHO実Writer/Reader・実外部LLM送出・Owner意味受理へ昇格しない**。以前のPlan-only表現は初版当時の履歴であり、この項の資格更新を優先する。

新しい[SK-01 §W](../../evaluations/SK-01-harness-skills.md) SK-IQ01〜12では、TEI [Draft #2638](https://github.com/hat47x/tei-platform/pull/2638)のRole bootstrap/eager依存閉包・deferred data Refの区別、[Draft #2639](https://github.com/hat47x/tei-platform/pull/2639)の実Go Language Plugin Referenceへの二表層接続、TEI [#2621](https://github.com/hat47x/tei-platform/issues/2621#issuecomment-6578796587)のTest-as-Data/独立Expected・Mutationを**Product側受理の必要条件を見落とさないためのConsumerケース**へ接続。Root RoleのPinだけで依存Interpreterを保証しない。Markdown/Skillの説明に現れる`role`文字列から意味受理や実Toolの有効性を推定しない。ExpectedとImplementationが同じ式に依存するセルフチェックを独立Oracleと呼ばない。

Owner分担：TEI #2620/#988はMeaning/Role/Plugin、#2605は実Product Skill、#2621/#2514はTest/Oracle、#2516は二Consumerの用途相対Projection、#2600は再生成/再資格化、TAI #168/#271は選択/Harness比較/Activity引継ぎ、SHOはWriter/Readerの実到達。共通Host/Registry/第二Role Resolver・Oracle Runnerは追加しない。**SK-IQ01〜12とH2/H3/H4/H5実験はNOT RUN**。


## 23. 必要最小のSkill構成を実利用タスクで比較する（SK-MIN）

[二つの実利用シナリオとSK-MIN01〜12](skill-composition-minimal-routing-scenarios-2026-11-02.md)を[SK-01 §X](../../evaluations/SK-01-harness-skills.md)へ接続した。横断Productを全て使うことは統合品質ではない。**Research Index L0のリンク編集だけならSHO/通常Markdown単独、TEI read-onlyモデル調査だけならTEI単独**を先に評価し、Source取得・問い相対の根拠・正式な意味採否・文書Consumer・外部作用が実際に必要になった段階だけ各Product/TAIを候補にする。

SC-AはMarkdownリンク整理→必要な元資料の取得・SEI/SUIの根拠/探索→TEI意味候補とOwner受理→SHO Writer/Reader・レビュー・納品を**未取得/未実装を伏せずに**追う。SC-BはTEI実read-only CLI→Product Skill有無→Context-aware Action Offer→隔離mock Host/Providerの実Effectを分ける。各段階で実Tool/Skill/Consumer/権限がなければunsupported、存在するだけならstatic-known、実到達は該当Ownerの独立証拠として記録する。TAIがProduct内Method/Role/権限/出典正本を複製せず、許可済み最小Handoffだけを担当する。

**追加の測定目的**：H2/H3とH4/H5の質の向上だけでなく、不要なSkill呼出し・未必要なTool発見・誤った完了・Tool/Plannerの余剰開示・Token/人の確認/時間の追加費用を同一Taskで測定する。Product数増加を加点しない。実行の優先は既に一部成功した[TEI Draft #2626](https://github.com/hat47x/tei-platform/pull/2626)実CLIの範囲を利用するH2/H3であり、実Skillロード・SHO別Reader・別Harness・Host/OSの証拠は未取得。**SK-MIN全件NOT RUN、Owner正式受理・main統合なし**。

## 24. 2026-11-03：代表的な外部Harnessと意味→実Capabilityの非単調な到達を接続（SK-HP）

[詳細設計・Harness別評価群](harness-portability-and-capability-qualification-2026-11-03.md)に、DSH以外の**Claude Code／Codex／OpenCode／利用可能なDots・Grok Bot等**を代表候補として、アカウントと環境の実可用性を未確認のまま「対応済み」としない受入方式を追加した。Harnessの利用可否とモデル提供者、Skill導入場所、Skill実ロード、CLI/MCP到達、現在Grant/公開資格、実Consumer結果は独立に評価する。既存SK-G0〜G6、H2/H3・H4/H5、[SK-MIN](skill-composition-minimal-routing-scenarios-2026-11-02.md)を置換しない。

[TEI Draft #2649](https://github.com/hat47x/tei-platform/pull/2649)が整理した**C0 意味Source/Role→C1 Operation候補→C2 実CLI/Tool→C3 Skill/Harness→C4 Consumer/Disclosure→C5実Effect**の照合を、TAI側の横断記録として参照する。ただしTEI正式Core状態型ではない。特にTEI `commands`の選抜read-only catalogから `operations/artifacts` の不掲載＝未実装と推測しない。逆に実dispatchやCLI `artifacts -out` のファイル書込み経路を確認しても、最初のread-only Product Skill/外部Hostのwrite権限へ昇格しない。実引数でeffect分類が変化する。

**後着進捗の訂正**：[TEI #2626](https://github.com/hat47x/tei-platform/pull/2626)は2026-11-02T18:35Z時点で**merged**、merge commit `00eb8e148daadbc2cf40145d8e8473d56531514c`。以前の本Draft §20〜22で「別Draft」「main未統合」と書いた箇所は当時の履歴であり、実Go CLI read-only 9回と同JobのMarkdown/JSON再読取、Source-only移動によるSourceIndex/Trace変化の限定証拠は現mainへ統合済みのPRに帰属する。ただし**本Draft #270の外部Harness Product Skill H2/H3・二Harness移植・SHO独立Reader・Host実Effectは全てNOT RUN**。別のTEI #2649は依然Draft／Source-static 15件の限定照合で、merged #2626の実CI資格を自己の実行証拠に転用しない。

[SK-01 §Y](../../evaluations/SK-01-harness-skills.md)にSK-HP01〜14を追加。代表Harnessの実験では「Skill未ロード／Tool未接続／現在Grant不足／公開Raw送信不可／同SourceでTool呼出可能」を区別し、異Harness間のUnsupported・unknownを明示する。さらに**同一目的がTEI単独で満たせればTAI横断Skillを不要として評価する**。Role/Tool/Skill Scriptの版変化、Source移動、Tool discovery→Planner→実Egress、EKI同Attempt Body/SHO実Readerを、各Ownerの証拠のまま引き継ぐ。

**現在の資格**：公開仕様と既存Repoの文書に基づく設計・評価票の追補のみ。実Harness Skill install/load/Tool invoke、別Harnessの比較、実OS/Network、正式配布・Owner意味受理はNOT RUN。新たな共通Host/Registry/Tool schema／第二Policy Engineは作らない。

## 25. 2026-11-03：結果が同じでも消えない依存と、現行のSkill／Role実装資格（SK-N）

[TAI #271のActivity継続計画§10](activity-selective-requalification-and-handoff-2026-11-02.md)に、[TEI #2582](https://github.com/hat47x/tei-platform/issues/2582)の負依存/Relation Path、[TEI #2640](https://github.com/hat47x/tei-platform/pull/2640)の0件・ABA・演算順序、[TEI #2638](https://github.com/hat47x/tei-platform/pull/2638)のRole自己記述のEager実装Pin、[TEI #2649](https://github.com/hat47x/tei-platform/pull/2649)の実CLI dispatch≠選抜Capability Discoveryを**同一Activityの変更後の再利用資格**として接続した。従来の「値が同じなら再利用可能」「旧StatusがPASSなら成功」という二つの誤昇格を分けて反証する。

- **0件と否定依存**：SQL結果の行ID集合が空でも`NOT EXISTS`/JOIN/Filter/TopNなどのPredicate・Relation・Scope/Provider・全件性への依存は消えない。partial 0件は対象不存在ではない。存在の反例についても**現在Scope・Predicate・時点の照合済みWitness**が必要で、別Tenant/過去時点の行は反証にならない。Change Event 0件も監視範囲の完全性がなければ期間無変更の証拠ではない。一方、同Scopeの帰属が明白な1件Witnessは部分取得でも不存在を反証し得る。
- **ABAとWindow**：0→1→0は同じ最終値でも「期間内無変更」ではない。Window1でA→Bへ切替えた後の古いA応答と、Window2が独立に取得したAは別。現在のOutput値とSource/Context epoch/選択Identity/Provider Cohortを照合する。
- **式・実Target順序**：Filter→Order→LimitとLimit→Local Filterを交換できない場合、偽0件の結果が生じる。表示数値の同一性から規則・実Read・結果の意味の同一性を推測しない。
- **Role/Skillの実装同一性**：Role versionだけでなくContract/実装fingerprint、必要なEager依存Pinの全体、実CLI/Adapter版、Skillの実ロード依存物を区別する。実Tool dispatchがあること、Toolが選抜catalogに載ること、現在のAgentへ公開/実行を許すこと、結果が届くことは独立資格。
- **誤判定の両方向**：依存の未観測はunknownにして必要な対象だけ再確認。ただし、無関係なSource/Renderer変更で歴史的に正しい独立Claimを一律失効させない。Agentが実際に使えなかったToolを使ったと報告させず、Contextの限定Scopeを超える判断を避ける。

[SK-01 §Z](../../evaluations/SK-01-harness-skills.md)の**SK-N01〜17**と、[Script](../../evaluations/tools/check-sk-n-negative-witness.cjs)／[限定V8実行記録](../../evaluations/records/SK-N-public-negative-witness-selfcheck-2026-11-02.json)を追加し、公開の合成値を使った**17/17自己整合**を確認。これはProductの元SQLやProviderを実行しない**作者自身のReference**であり、TEI #2387 QX-31の実SQLite12/12・TEI #2638の模擬Role Pin24/24・既存TAI QH18/18は、各Owner／試行の別証拠のまま保持する。合算した数値をYI製品E2E合格としない。

**実証の先後を更新**：[TEI PR #2626](https://github.com/hat47x/tei-platform/pull/2626)は2026-11-02T18:35:59Zにmainへmerge済みで、実Go CLI read-only/Context Consumerの限定観測は存在する。よって「TEI CLIはすべて静的文書のみ」という過去記述は**現在のTEI製品レーンには当てはまらない**。ただしTAIの外部HarnessでのH2/H3、複数Harness切替、TAI Activityでの実Skill load/Tool invocation、実OS/Host等は未実施。最初はTEI製品側実Tool・Source/Consumerの既存証拠を固定し、Product Skill有無の差→必要な最小Product組合せ→Activity再開J0/J1/J2へ進める。探索や新Issueは並列に増やし、品質を主張するための検証単位は小さく保つ。

**Scope**：ProductのQuery依存解析・Reactive State/Role Resolver・Authority・Policyの正本は各Owner。TAIで中央Reactive Engine、Negative Cache、統合Agent Runtime/Host、第二の共通Capability Registryを作らない。現在のHost Grant/Disclosure・実Consumer読取・実DB/業務Effectと独立Oracle/Owner受理は別の資格。SK-N/Activity実ProductテストはNOT RUN。

## 26. 2026-11-03：最初の実Skill有効性を盲検ペアで測る（SK-02）

これまでのSK-01 H2/H3と[TEI merged #2626](https://github.com/hat47x/tei-platform/pull/2626)の現物CLI証拠の間を、[**SK-02実行試行票**](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)で具体的に接続した。初回は**Product TEI Skillのみ**を対象として、**H2 Tool-only vs H3 Product Skillあり**を一つの実Harness、同じ実CLI binary／公開Source／Prompt／実Tool契約／開示条件／独立Oracleで比較する。Skill packageの存在、実Loaded byte（root+references/scripts）、実CLI/Tool呼出し、Source/Warning/Unknown、消費Token・人手確認を別々に記録する。二Product連携とTAI横断Skill H4/H5は**この初回の合格条件ではない**。

方法上の新しい決定は(1) H2→H3とH3→H2の**逆順ペア＋各Session独立**、(2) 実Skillロードの**明示指定と自動発見を別条件**として混ぜない、(3) 期待値をSkill/Promptに埋め込まず独立採点する、(4) 有効性の比較資格と結果の正しさを別軸にする、(5) Tool/CLIの実コマンド範囲と`artifacts -out`等のFile writeを同一read-only Permissionに含めない、(6) WorldFP一致でもSourceIndex/Trace/引用locatorsが変わる改版は別task groupにする、の六点。**条件が揃わない「改善0」は不当**で、比較不能/unsupported/unknownとして残す。

候補Harnessは実利用可能なClaude Code／Codex／OpenCodeから一つずつ検証、続いて第二Harnessへ同Task/Skillを移植する。Dots/Grok Bot等の利用資格は実確認がない限り採用したと扱わない。各Productの適合・Host認可・開示・本番Effectは引き続きそれぞれのOwner。**SK-02の実Session、実Skill Load、実Harness比較は全件NOT RUN**。現状は実行計画・記録欄が成熟した段階であり、繰り返し公開fixtureを増やすことを実証の代替にしない。

---

<!-- yi-skill-multi-harness-sk03-20261103 -->
## 27. 2026-11-03：DSHを唯一の基準にせず、Skill・Tool・Handoffを直交的に評価する（SK-03）

[代表Harness相互運用と段階実証 SK-03](harness-interoperability-and-handoff-pilot-2026-11-03.md)を、既存[SK-02](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)と[SK-01 §Y](../../evaluations/SK-01-harness-skills.md)の**後続の実証計画**として採用候補に追加。DSHと「OpenCodeでDeepSeekモデルを使用」は別Harness実装であり、Model/Provider、Harness、Subscription/請求経路、OS/Tool権限を同一視しない。Claude Code／Codex／OpenCode／DSHを初期P0、Gemini CLI／Copilot Agent／Cursor／Clineを次群、Cloud型のDots／Grok Bot／ChatGPT Workを別環境として評価する。

**新たに固定する設計判断**：
- Productが公開するSource/意味・型付き結果・CLI/APIの契約が先。Skillは目的/手順、MCPは任意のTool搬送、Harness Adapterは環境依存の配置・Tool alias/設定。特定HarnessのAgent LoopやPermission EngineをTAIで再実装しない。
- 対応可否はSkill discover/load、CLI/MCP実call、Source/Unknown/Version、現在Grant/Disclosure、実受信/Effect、費用の**別軸**。MCP無しでもCLI利用、Skill無しでもTool-only利用を正確に部分対応とする。公称仕様やSkill root存在を実可用性に昇格しない。
- **比較因果を守る**：まず1 HarnessでSK-02 H2/H3を同版・独立Session・逆順ペアで実測。続くSK-03で第2 Harnessへ同じProduct Skill/Tool/公開Sourceを移植し、Adapter差のみを確認。Model/Permissionが異なる場合は「構成間の契約互換性」だけを比較し、SkillやModelの優劣を断定しない。
- **Handoffはデータのコピーではなく現在資格の再確認**。別Harnessへ渡すのは許可済みのSource/Scope/既存Result/Unknown/残作業の限定Projection。旧Tool/Grant/公開権限/ACKを移植せず、同Attempt Body/実Consumer Read/Provider Effectを別観測。TAI #271のJ0/J1/J2を再利用する。
- 初期SK-03のHX-01〜10は**NOT RUN**。TEI merged #2626のread-only CLI観測とTAI SK-02合成20件CheckerのPASSは、外部Harness Skillロード/跨Harness再開のPASSではない。既存Critical Pathや他Product単体利用を全Harness実証待ちにしない。

対応先：TAI #168（一覧と比較）、#74（版固定・配布）、#271（再資格化）、TEI #2605（製品Skill/CLI）、#2509（DSH固有）、#2018（生産性/費用）、TAI #232/TEI #2515（機密実隔離）。新Core enum、共通Host/Registry、二重Authority/Oracleは作らない。

## 28. 2026-11-03：実Product Skill統合後の基準版と期限・品質・回復制約のSkillルーティング

### 28.1 歴史的Draft記述の更新と実証境界

[TEI Product Skill PR #2607](https://github.com/hat47x/tei-platform/pull/2607)（merge `ca6cbf5745b5ddb22185782e0f9ea37f6f8566b9`）と[TEI Capability/CLI/Artifact PR #2649](https://github.com/hat47x/tei-platform/pull/2649)（merge `e98ec5f475c60b53cc1cc91c9b44ce2bc502a111`）が**mainへ統合済み**。旧§20〜27やSK-02内で「Draft #2607/#2649」と書いた箇所は当時の時系列記録であり、現在の試行には**実mainに存在するSkill/実CLI**を使う。この更新によって外部Harnessの導入や意味受理まで証明されたわけではない。

[SK-02 §11](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)に、[TEI GitHub Actions #41532988114](https://github.com/hat47x/tei-platform/actions/runs/41532988114)の**14 Python Checker tests + document/CLI static check + 単一Go binaryのread-only `commands/catalog/inspect/trace/validate` smoke success**を、**PR merge-ref `8d442c41f81fda64119fe41cef5ef44cd49034ac`限定Evidence**として記載。実Skillロード・同一Harness H2/H3四Session・第二Harness SK-03は**未実施**である。CIに出たbinary SHA/Job・Product Skill実Blobは登録候補であり、現行Harnessで実消費した実行物とは区別する。

### 28.2 目標関数を単なる「低Token単価」にしない

[SK-03 §8](harness-interoperability-and-handoff-pilot-2026-11-03.md)に、他チャットの[TAI #168 CQ-04/05](https://github.com/hat47x/tai-pleroma/issues/168)、[EKI #19](https://github.com/hat47x/eki-fabric/issues/19)/[#155](https://github.com/hat47x/eki-fabric/issues/155)、[TEI Draft #2667](https://github.com/hat47x/tei-platform/pull/2667)を接続した。HarnessやProductの選択は、**(a) Source/Disclosure/Contract/Host Grant/必要品質のhard constraints → (b) 許容lead timeと障害後の回復余裕 → (c) 総費用・人間レビュー → (d) 不足時の縮退/保留**の順。推定成功確率・安価なToken・Skillが説明するCapabilityを、現在の実行権限や品質/期限保証に昇格しない。費用実績や時間分布がなければその部分は`unknown`であり、架空の最適Workerを選ばない。

**二つの完了時点**を明示する。①Task実行/Body Consumer受領の期限、②そのOutputを特定用途で利用するためのTEI Quality Check/例外/Scope/期限。EKIでJob完了でもTEI品質検査が未実行、またはSHOが文書を書けてもReaderが新Versionを読んでいないなら、依頼の成果条件を達成したと報告しない。他方、OwnerがDeferred/Advisoryと定義するCheckSetをTAI Skillで全用途ブロックしない。

EKIの明示的な委任時は既存Task/Attempt/Admission/Worker/Lease/Recovery/物理資源予算だけをEKIへ渡し、TAIは二重Schedulerや価格/通貨の中央台帳を持たない。安価なHarness再起動とEKI Result Bodyの同Attempt再送を同じRetryとして扱わない。公開合成条件の[HX-15〜18](harness-interoperability-and-handoff-pilot-2026-11-03.md)で、期限miss/Quality期限違反/Body ACK不一致/資源回復公平性を反証する。いずれも現在**NOT RUN**。

### 28.3 採用候補・保留・次の実証

**採用を推奨する設計境界**：外部Harness-first、Product Skillは各Product owner、TAIの横断SkillはTaskの必要最小の選択と受渡し、Data/Quality・Policy・Pricing・HPC/Provider専門実装を共通化せず各Ownerへ委ねる。Runtimeに追加するのは現時点では**なし**。これらは設計上の候補であって正式Owner採用ではない。

**実施の順序**：公開Workspace上の既存TEI Skill/CLIを**同一Harnessで実ロード・4セッションH2/H3**→独立Expectedと警告/Source/Scopeの正しさ・Token/Tool/時間を測る→**二つ目の利用可能Harnessへ同Task/Skillの実移植**→必要な条件でOnly Product/TAI/SHO/EKI・期限/Recovery・Data Qualityの横断Handoffへ拡張する。未完了がある工程のPASSを他工程へ伝播しない。[TAI #74](https://github.com/hat47x/tai-pleroma/issues/74)のBundle配布受入・[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)の現在性再資格化を既存Ownerとして維持。

## 29. 2026-11-03：UI・Job・組織ScopeをSkillの入口別に分解する（SK-IV）

[新しい入口別契約・SK-IV01〜12](skill-entrypoint-ui-job-organization-boundaries-2026-11-03.md)を、Product単体の実行モデルとYICのSkill選択が衝突しない**用途別判断票**として加えた。利用者が「モデルを読む」「Studioで計画/参照実行」「UIを拡張」「業務Actionを作用」「cron/ServiceからFunction起動」「組織に基づくReader/参照専用」「EKIへTask委任」「保存・納品」を要求する場合、**同じTEI Skill名でも実CLI・生成物・Interaction・Host権限・Consumerの資格を分ける**。

**既存実装と提案を分離**：[TEI #2747](https://github.com/hat47x/tei-platform/pull/2747)はmergedでStudio `PlanCommand/ExecuteCommand`のWails/Node/Go Reference経路が実在する。ただしReference応答`Committed=true`を外部Provider/DB commitとして扱わない。[TEI #2616](https://github.com/hat47x/tei-platform/pull/2616)では、正しいBinding＋成功Outcomeが選択O-1でなくO-2の変更でも成立する限定Go負例がある（実Host事前拒否は未証明）。[TEI #2781](https://github.com/hat47x/tei-platform/pull/2781)の組織可視性33件は合成検査であって実RLS/Providerの証明ではない。

**成熟した責務境界**：TEIの業務System/SubSystem/Function IdentityとBuild/Deployment/Triggerの分割を混ぜず、ユーザー方針の**Go単一バイナリを基本**に、複数Buildが必要になった場合だけ対応表と固定版を追加する。WailsはPresentation側のAdapterであり、業務Action意味/Host実権限を担わない。UI拡張は宣言→Component→生成Code→独立Processの候補を評価するが、安定Hook/ABI実在・更新互換はOwner/実試験待ち。EKIは実際に明示委任するときだけTask/Attempt/Lease/Resultを所有。TAI/Skillは新しいJob Runtime、Wails Extension API、Org ACL、共通Hostや中央Capability Registryを作らない。

**Handoff/失効**：Action Purpose/Target/Scope/Expected-state、Source/Role/Build・Org valid/known time、現在Grant、Provider/Receipt/Reader、期限/品質/開示を各Productの実証へ結ぶ。Previewや`rows=[]`や`COMPLETED`を、現在の更新許可・全件不存在・業務品質PASSへ昇格しない。Role/Rule/Source変更を、UI書式だけの変更と同じ再受理コストにしない。

[SK-01 §AC](../../evaluations/SK-01-harness-skills.md)へ**SK-IV01〜12**を追加（全件NOT RUN）。SK-02の最初の実H2/H3は引き続き**TEI mainのread-onlyモデル調査だけ**を対象として、Studio/Job/Org/Provider全体の未証明によって停止させない。その後、実装が存在する範囲だけ用途別のUI/Job/Org試験・SK-03第2Harness比較に拡張する。OwnerはTEI #1130/#1824/#2507/#2598/#1174/#2386/#2605、EKI #112/#57、TAI #168/#74/#271、SHO #4の既存責務を維持。

## 30. 2026-11-03：TAI Skillの常時読込を最小化し、詳細手順を必要時だけ参照する

**既存PoCの設計矛盾を修正**：TAIは一製品で済む仕事に不要、外部Harnessへの情報開示とtoken負担も最小化すべきだが、[旧`examples/skills/yi-tai-activity/SKILL.md`](https://github.com/hat47x/tai-pleroma/blob/5e578c05b8c4ad8e17e08fb7891dfc7c448cde13/examples/skills/yi-tai-activity/SKILL.md)は、追加した評価・Role・UI・EKI・Source・Trustの詳細を全量rootに積み重ねて**13,967文字**となっていた。Skillが自動発見・ロードされる環境で常時この説明を投入するのは、必要最小のSelection/Contextと相反し、手順の優先順位を理解しにくくする。

**今回の実体変更**：TAI例示Skillのrootを**3,162文字（文字数で77.4%減）**へ整理し、作業の核となる「複数製品が必要な場合だけ起動→目的と停止条件→実能力→Source/意味/開示→作用前資格→期限/品質/回復→必要範囲の結果」を7段階へ統合。詳細13節は欠落させず、同じProduct Repo内の3つの遅延参照ファイルへ移動した。

| 参照範囲 | 必要なときだけ読むファイル | 旧rootから保存した節 |
| --- | --- | --- |
| Product/入口/意味 | [`references/product-entrypoints.md`](../../examples/skills/yi-tai-activity/references/product-entrypoints.md) | 6節：TEI CLI/Studio/UI/Job/Org、Markdown/SHO、Action、型付きConnectionなど |
| Source/Tool/Disclosure | [`references/source-disclosure-evidence.md`](../../examples/skills/yi-tai-activity/references/source-disclosure-evidence.md) | 4節：Skill実ロード/Tool/Source/Artifact/現在Trust/Planner Disclosure |
| 再資格化/期限/回復 | [`references/requalification-deadline-recovery.md`](../../examples/skills/yi-tai-activity/references/requalification-deadline-recovery.md) | 3節：過去成果の局所再確認、Activity再開、EKI/品質期限 |

**検査結果（実GitHubファイル照合）**：変更前のexact commitと新ファイルをGitHubから再取得し、13節の本文を相対リンク調整後に**一節ずつ文字列比較して13/13一致、欠落0**。4つの新ファイルに含まれるローカル参照**27件／重複排除14 PathをGitHub実ファイルとして確認し、broken link 0**。Frontmatterの`name: yi-tai-activity`と`NOT RUN`警告は維持した。これは**文書・パッケージ構造の静的確認**であり、Harnessによる選択/参照ロード実行、Token計測、正答・安全性向上の実測ではない。詳細3ファイルを全部読んだ場合に総Prompt量が減るとは主張しない。

**利用時規則**：rootはTAIが必要なときだけ適用。詳細は一件のTaskで必要な一つだけを優先し、Readerが実際に読んだ参照版を記録する。Agentの「読んだ」という自己申告は実Loader証拠の代用ではない。**root縮小の良否は[SK-01 §AD](../../evaluations/SK-01-harness-skills.md)で、最小Tool/Skill選択・正答・誤選択・資料過少/過剰ロード・Token/費用・人のReviewを同一Taskで比較する**。既存SK-02 H2/H3（TEI Product Skill）にTAI Skillを混入させず、TAI Skill追加群は後続SK-MIN P2/H4/H5で扱う。

**採用範囲**：TAI Draft #270の**試作Skillの構造改善のみ**。各Productの正式Skill、実CLI、Owner Meaning/Authority/Current Grant、外部Harness install/load、シリーズReleaseは変更・受理していない。新Host/Registry/Tool ABIを加えない。


## 31. 2026-11-04：軽量Skillの参照閉包をCIで固定し、品質・組織・Actionの資格を分離する

### 31.1 Skill rootの軽量化を再び無効化しない

前節のTAI Skill root 3,162文字＋3参照資料という構成は維持し、広域なTEI/SHO/EKI設計追補をrootに追加しない。追加機能はそのProductがOwner。TAIが担当するのは「そのProductを実際に使う必要があるか」「適切な情報だけをその実Productへ渡し、結果と未知を説明できるか」の判断。Rootの文字数には必須の固定上限を設けず、実Taskで正答・過剰ロード・Token/人手を測る。

**実行できる変更**：[TAI例示Skill package静的Checker](../../evaluations/tools/check-tai-skill-package.cjs)と[独立GitHub Actions](../../.github/workflows/tai-example-skill-package-check.yml)をDraft #270に追加。Skill frontmatter name/description、3参照ファイルの実在とrootリンク、root+references内の相対Markdownリンクを読み、参照切れ・Repository外へのPath escape・Symbolic Link越境を拒否する。標準Node 22以外の依存やSkill専用Runtimeは導入しない。

Checkerの自己検査は8つの公開合成条件（正常、frontmatter欠落、name不一致、必須参照未結合、参照切れ、Repository外パス、詳細資料の参照切れ、URL encoding異常）。単なるファイル構造とパスの試験であり、実Harnessによるread/loaded、Semantic/Owner受理、機密情報送出、Skillの正答率を調べるものではない。CIは前述の4ファイル/Checker変更だけで起動し、既存SK-02の比較適格性Workflowとは独立とする。Exact HEADのCI結論はJob logの確認後に限定記録し、queued/in-progressをPASSにしない。

### 31.2 Productの受入能力を「何を読んだ」「何を検出できる」「何をしてよい」に分ける

他チャットの[TEI Everything is Data Draft #2667](https://github.com/hat47x/tei-platform/pull/2667)では、Data Coverage（取得・検査したScope）とFault Detection（独立Expected/Mutationを用いて本当に検出できた誤り）の分離が成熟した。すべての行にアクセスできても、生成した検査式が誤っているなら品質PASSとは限らない。よってYIC Skillが出す「検証済み」には **(A)実Source/Query Cohort/Row・Field Completeness/版、(B)Accepted Ruleと独立Oracleに対するFault Detectionの範囲、(C)現在のConsumer用途・Quality期限・例外**を別々に置く。AIが生成したRuleとAIの自己期待を相互に照合しただけで独立Oracleと呼ばない。

[TEI Organization Draft #2781](https://github.com/hat47x/tei-platform/pull/2781)のRecord visibility/read-only圧力試験でも、Hierarchy/Membershipのvalid-at・known-at、Policy scope-root/axis、部分Queryの隠れたRow/Field、ReadとExportの許可、未保存編集、既配布コピーを分けている。組織上の閲覧/参照専用/Reader UI状態をHost/Providerの実Grant・Approval/Write権限へ昇格させない。公開対象でないRole/Tool/Recordの件数・ヒント自体もSkillの開示対象となる。実Providerでの強制はTEI Ownerの未検証領域。

[TEI Action PR #2616](https://github.com/hat47x/tei-platform/pull/2616)／[#2784](https://github.com/hat47x/tei-platform/pull/2784)の現行実証では、Offer時のPurpose/Target/Periodと、実Invocation/Provider Commit時のTarget・現在Grant・Periodは異なる時点の資格。正しいBindingや参照Executionのsuccessを、同対象へのBusiness Commit／現在権限に昇格しない。期間未指定のReference挙動も、全業務で期間省略を正式受理した根拠にはならない。実DB Transaction/Receipt/独立Readは#1174/#2598等のOwner。

### 31.3 一つの必要十分な実証順序

**P0 静的準備**：Skill package Integrity Checkの実CIを確認し、TEI merged #2607 Skill root+refsとCLI binary/Source版・公開範囲を採取。参照資料全部の強制ロードはしない。

**P1 実比較**：単一の利用可能な外部HarnessでTEI Tool-only H2／Product Skill H3を同Source・Binary・権限・Task/独立Oracleで4独立Session比較。Package/Python静的成功を実Skillロードに数えない。

**P2 実引継ぎ**：別Harnessで実Tool結果、実Reader/開示、Changed Source/Revision/Grantの必要部分を再資格化。SK-03の既存子Process公開合成16件を二Harness互換と呼ばない。

**P3 必要なProductだけ拡張**：Quality/Organization/Actionなど、利用者の実Taskが必要とする既存Product実API・Providerと独立Expectedに限り追加試験し、各Ownerが出した限定結果だけをTAI Skillへ引き継ぐ。Full Query/全Org機能/全Provider/全Harness対応を先行Gateにしない。

**状態・Owner**：本節はTAI Draft上の試作Skill静的保全＋Product別の受入境界設計であり、実Harness・品質Oracle・Provider/OS/Host認可・Owner業務受理はNOT RUN。対応先はTAI #168/#74/#271、TEI #2605/#2514/#2667/#2781/#2598/#1174、EKI #57、SHO #4。第二Host・Registry・Policy Engine・共通Oracleを作らない。

## 32. 2026-11-04：SK-02実証前の観測票を型付きにし、生成AIテストの足場を小さく保つ

[SK-02 §12](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)で、**Product/Skillの意味や適合より先に、試験票そのものの観測型が正しいかを検査**する実装差分を追加した。旧Checkerは`unauthorized_*_observed="false"`等のJSON文字列を観測不足として検出せず、架空の実験Metadataを比較可能と誤分類し得た。実Booleanのみ認め、String/Numberを`insufficient-evidence`、不正なTrial Rowを`ineligible`として判定。E01〜E32を維持しE33〜E41へ拡張した。

これはユーザーの「必要なテストをAIが自発生成・拡張できる足場」を、**巨大な共通Test Runtimeや新たなOwner受理Engineを置かずに**具体化する試みである。モデルが増やした負例を既存Checkerへ足せる一方、Expectedが同一AI/同一Scriptから生成される自己整合と、Productの独立Oracleとは区別する。Syntheticsの件数・CI緑・実Sourceを読んだとする自己申告を、実H2/H3 Skill改善率や非漏えい保証に昇格しない。

次の一件は**実Harness一種類、TEI Product Skill一つ、公開Source一つ、read-only CLI**に限定する。記録の型を満たしただけでは弱いため、実Tool出力の取得元と手順・Binary/Source/Skill消費版・Observation/Disclosure・独立Oracleを、SK-02の既存Runbookと試行票に追加資料を増やさず記録する。Tool-onlyが十分ならSkill非採用という結論を許し、第二HarnessやEKIを初回の必須要件としない。TAIは新Host/Provider/API/中央Registry/Oracleを持たない。

**確認状況**：本更新時点で修正コード・41件を実GitHub branchへ保存。exact HEADでのCIは別途Job log確認、実ハーネス・本番権限・独立Business Oracleは**NOT RUN**。


## 33. 2026-11-04：Source読込・検証・実使用を分離し、SK-02の誤成功を防ぐ

他チャットの[TEI Everything is Data横断計画 #2667](https://github.com/hat47x/tei-platform/pull/2667)、AI-firstテスト基盤[Draft #2811](https://github.com/hat47x/tei-platform/pull/2811)、実CLI Source診断Issue [#2822](https://github.com/hat47x/tei-platform/issues/2822)/[#2823](https://github.com/hat47x/tei-platform/issues/2823)/[#2824](https://github.com/hat47x/tei-platform/issues/2824)、Build Source不一致を特性化した[merged #2819](https://github.com/hat47x/tei-platform/pull/2819)、[AI JSON Scenario Draft #2828](https://github.com/hat47x/tei-platform/pull/2828)を横断照合した。採用済みのTEI CLI/Go Scenario実装と、未実装のSource完全性／Build入力固定／独立Oracleを分ける。

**成熟した判断**：Source/Skill/Function/Scenarioに「宣言がある」「発見できた」「Reader/Parserが実読込した」「要求された意味へ適用した」「選択した実Binary/Build/Providerで消費した」「利用者・外部Consumerが実結果を受領した」という違う資格がある。空Workspaceでvalidate okかつ標準catalog13件、存在しないmanifest root、managedだがParser未読込、commands19件と文書13件の不整合を、**初回Skill実証の負例**へ接続する。技能の説明やツール列挙を正本Source読込へ昇格させない。

- **P0 read-only Taskのみ**：[実行Runbook §11](first-real-skill-qualification-runbook-2026-11-02.md)で独立期待Subject・実Source根拠・Catalog/Inspect/Validateの同版を照合する。SK-SRC01〜06は**評価案／NOT RUN**。実LoaderはTEI Ownerへ委譲し、新公共Schema/Registryを設計しない。
- **P1 現H2/H3比較**：[SK-02 §13](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)の**比較適格性とTask正答の分離**を徹底。四Session/元CLI出力/独立Oracleで正答を採点し、両腕が同じ「空Workspace」を読めてもTask成功にしない。Checkerの41件合成PASSはJSON比較条件の限定証拠。
- **P2 範囲拡張は必要時のみ**：AIが自発追加するJSON ScenarioはTEI mainの既存Scenario v0／各DraftのTest-only候補へ渡し、独立Expected/Mutant Detectionを別証拠とする。Build/Targetを要するときだけ実Source byteと実Build入力を照合（TEI #2595）；Batch/低レイテンシ/マルチモーダルを初回Harness選択の必須要件にしない。EKI Taskを要する時だけ契約・Body/Recoveryを検証する。
- **TAIの既存資産再利用**：[merged TAI #105](https://github.com/hat47x/tai-pleroma/pull/105)のreference-tei-modelは限定SCN-001のvalidate/Catalog/ModelBinding/Pinned Checkoutを実接続できる。別TEI Workspace、別Source、Skillハーネスロードまでの共通証明とはしない。新たなTEI Bridge/Pin EngineをTAI Draft #270へ実装しない。
- **価値と実装境界**：[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)の過剰要件監査に従い、生成AIに検証候補の数を制限せず、標準構成に必要な機構を増やさない。Owner/Authority/実Source読込の確認自体は削減対象とせず、Product単独TaskにTAI、EKI、SHO、全Scenarioを必須化しない。

今回の差分は**実験Runbook＋SK-02採点範囲＋計画の更新**。TEI #2822〜24/merged #2819はProduct Ownerが別環境で行った限定実観測、TAI #105は既存Connection実装。TAI自身による今回の実TEI CLI／外部Harness／AI自動生成のScenario 実Trial、独立Oracle採点、実Provider/Consumer効果は **NOT RUN**。Draft #270を維持する。


### 33.1 JSON入力の重複と外部Sourceの指示混入を、必要な実験の範囲で扱う（2026-11-04）

**実装済みの差分**：[SK-02 §14](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)のE42〜48。AI生成／外部由来の試行JSONに同名keyが重複した場合、`JSON.parse`の後勝ち上書きは比較前に監査・不正送出欄を失わせる。文字列`"false"`の型検査（E33〜41）に加え、**JSON解釈前の重複member拒否を既存Node Checker内部だけへ実装**した。GitHub Actions #41849280505は合成48/48 PASS。ただし記録票の真実性・Skill実ロード・Task正答を保証しない。

**外部Source／Promptの別境界**：[TEI PR #2669](https://github.com/hat47x/tei-platform/pull/2669)では、`ignore_prior_instructions_validation_test.go`のような**実Source候補のファイル名**が、実Go Rerank経路からモデル向け`Instructions`文字列へ入り得ることを限定的に確認している。これはモデルが指示に従ったという証拠ではない。TAI Skillはファイル名、Markdown本文、検索結果、Tool応答、Skill候補説明を**低信頼の資料内容**として扱い、利用者/Hostが認めたInstruction・実Tool契約・Grantへ自動昇格しない。実送信/受信byte、Audience、外部開示制限はTAI #232/#272と各Provider/Harnessが検証する。普遍的Prompt Sanitizerや第二Policy Engineは増設しない。

**初回実証の条件付き分類（[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)）**：
- **Blocking**：SK-02一件の実H2/H3では、公開Sourceの対象Subject・実Binary/argv/版・実Skillのロード、四つの独立Session、比較適格性、独立Oracleが必要。JSON票に重複があれば記録を棄却する。
- **Conditional**：非公開Sourceの外部送出、Tool出力に紛れた不正Instruction、SHO/MMI ReaderやEKI委任、組織Scopeは、その経路を実際に使うときに対象Ownerの開示・Role・Consumer/Result資格を確認する。
- **Nonblocking**：初回のread-only Product Skill比較に、全Harness/全CLI/Web/GUI/Provider、Go生成物、低遅延Event・マルチモーダルEKI、SHOの実Editor/Saveまで必須化しない。
- **Unknown**：許可済み範囲で実観測できないGrant/Source/Consumerは不明と記録。未観測を「安全」「不存在」や費用0の成功に変換しない。

**他チャットの実Product成果の置き場**：[SHO Draft #14](https://github.com/hat47x/sho-composer/pull/14)で固定MMI CLIの合成Markdown→HTML RenderがCIで実行されたが、SHO自身のReader/Writerの実証ではない。EKI低遅延/マルチモーダルは[TAI Draft #423](https://github.com/hat47x/tai-pleroma/pull/423)で条件付き扱いを維持。これらをSK-02のBlocking条件にも、YIC全体の必須機構にも追加しない。

今回の実体変更は**既存SK-02の試行票読込とその限定CI**だけ。Product正本の契約変更、新Skill/Host/Registryの設置、外部Harness実ロード・実Provider/実OS実験はしない。


### 33.2 製品横断の実証ゲートは、Ownerの現行契約に基づき条件付きで選択する（2026-11-04）

[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)と[Draft #423](https://github.com/hat47x/tai-pleroma/pull/423)の過剰要件監査では、機能要件の数を減らすのではなく、**各Productの単独での主要価値を成立させる最小受入**と、横断時にだけ必要な資格を分ける。今回照合したOwnerの現状は次のとおり。

| Product・条件 | 確認した現在の到達点 | YIC Skillが主張しないこと／必要な場合の次Gate |
| --- | --- | --- |
| **TEI一製品のread-onlyモデル調査** | merged #2607のProduct Skill、既存CLI、SK-02試験票とJSON 48件の合成検査。CLIファイル入力でも重複JSON・不正JSONを拒否する実Node CI [#41849868908](https://github.com/hat47x/tai-pleroma/actions/runs/41849868908) | 実AI Harness 4 Session／実Skill Load／独立Oracle・利用者価値は未実施。TAI Skillを自動追加しない |
| **SHO単独の文書・Research Index** | [SHO Draft #14](https://github.com/hat47x/sho-composer/pull/14)はpinされた実MMI CLIの合成Markdown→HTML Renderを限定CIで確認 | **SHO自身のReader／編集・保存・再開は未実施**。[SHO #15](https://github.com/hat47x/sho-composer/issues/15)はG1b／G1-SHO等のゲートIDの不一致をOwner判断待ちと記録。IDだけで「SHO Reader完了」にしない。TEI SK-02へSHOを必須化しない |
| **EKI委任・結果・Recovery** | [EKI #698](https://github.com/hat47x/eki-fabric/issues/698)のsource-static監査では、提案ADR-0029のSuitability **4値**と実API／設計の**3値**が不一致（Owner未決） | 初回TEI Skill比較にEKIを要件化しない。委任Taskを実施する場合は現APIの判定値・Admission拒否・実Body/Receipt/Recoveryを照合し、提案の4値を実装済みと偽らない。低遅延／マルチモーダルTransportは用途に応じた条件付き検証 |
| **SEI・SUIの認知／意味探索** | 根拠十分性・残余の問い・異論/保留を扱うProduct別計画がある | Source候補を増やしたことを網羅・正答・開示適格と認定せず、実際に使う場合だけ問い相対のRead／Owner判断とSource/Disclosureを検証 |

**ゲート適用の規則**：初回SK-02ではTEI実Tool/実Skill Load/独立Task Oracleに限りBlocking。SHO Reader・EKI Suitability・SEI/SUI Method・外部2nd Harness・TEI Build/Provider/Studioは、そのProductを実際に経由するTaskのConditional Gateとする。Owner未決の4値／3値、G1bの名称差、Catalog/Source読込の未確認は**Unknown**として保存し、TAIの便宜で共通正本・共通Gateへ再定義しない。

**検査資格**：TAIのJSON重複拒否は入力試行票の構文・一部型とメタデータ整合しか保証しない。[TEI #2813](https://github.com/hat47x/tei-platform/pull/2813)のAI候補や[TEI #2669](https://github.com/hat47x/tei-platform/pull/2669)のSource→モデルInstructions流入に対する独立検証・安全保証を代行しない。新たな一般JSON ParserやPrompt Sanitizer、Agent Host、中央Policy、Product別RuntimeをTAIへ追加しない。Product横断の価値と費用は既存のSK-MIN/H2/H3実証で比較する。

**状態**：この節は既存Ownerのsource-static／実CI範囲の対応づけ。上記の別Product実操作・二Product Consumer Handoff、EKI新Transport、SHO Reader、複数モデル実験、Owner正式受理は **NOT RUN**。


## 34. 2026-11-04：同じHashだけで異なるCLI Workspaceを比較しない

既存[SK-02 Checker](../../evaluations/tools/check-sk02-pair-eligibility.cjs)には、4 Sessionの`workspace_tree_digest`・WorldFP・SourceIndexFPを揃えても、**実argvのWorkspace pathやCLI CWDが一方だけ異なる試行を比較候補と誤分類し得る**欠陥があった。外部ハーネス間のSource忠実性、TEI SourceのDeclared/Loaded/Consumed、TAI #271の再資格化の議論を、追加の正本やRuntimeを作らず**既存試験票の比較可能性**へ還元した。

**実装**：[SK-02 §14](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)に従い`cli_cwd`を初回試行の同条件欄に追加し、`model catalog/inspect/trace/validate`の各`-workspace`引数を同Trial・全4Trialで検査する。曖昧なWorkspace二重指定、異なるpath、初回Profile外の`-world`は不適格、記録不足は`insufficient-evidence`とする。これはGo CLI全flagやSource Byteを解析するものではなく、同一path文字列＝同一原Source、同一Authority、同一Business Meaningという判断はしない。

**限定CI Evidence**：[TAI GitHub Actions #41850429887](https://github.com/hat47x/tai-pleroma/actions/runs/41850429887)にて既存E01〜E48とE49〜E60を含む合成60/60 PASSを実Job logで確認。これまでの48件に対して実入力条件の負例を12件追加した。Product経路で実観測された4 Session、Token/Wall time/独立Oracle/外部Egressは未実行。CI緑をProduct効果へ転用しない。

**負担の制限**：[初回Runbook §12](first-real-skill-qualification-runbook-2026-11-02.md)の同一read-only Workspace Taskだけに適用し、複数Source／EKI分散ジョブ／SHO文書再開／別環境へHandoffする場合はそれぞれの既存Owner・既存SK-03へ返す。root TAI Activity Skillを増大させず、Product Skillに新たな共通Host/Schemaを要求しない。結論として初回の次の価値検証は依然**実H2/H3 Skill Loadと独立Oracleの4 Session**であり、今回追加したのはその判定票の実装品質だけである。


### 33.3 H2/H3のWorkspace同一性を、申告HashだけでなくCLI引数に結ぶ（2026-11-04）

[SK-02 §15](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)で、四SessionのWorkspace Hash/WorldFPが一致しても実argvで異なるSourceを読んでいる可能性を、新たな独立メタデータ負例 **E49〜E60** として判別する。従来のE01〜E48を維持し、最初のread-only一Workspace課題に限ってCLIの作業ディレクトリとworkspace引数の文字列同一性をチェックする。これはファイル解決・実Read・権限・Source完全性の証明ではなく、**同じタスク条件で比較できるための必要条件**である。

[SK-02 GitHub Actions #41850563772](https://github.com/hat47x/tai-pleroma/actions/runs/41850563772) の実Job LogでNode構文検査、**合成60/60 PASS**、重複・不正JSONを実ファイルCLI入口から拒否する確認を実施。別Product/別Harness/実TEI CLI／独立OracleのPASSへ加算しない。相対パスの物理Source実同一性やsymlinkの解析は現Checkerが保証せず、実試行のSource/Process Observerへ委ねる。SK-02の初回対象はTEI Product-onlyの限定read-only調査であり、EKI/SHO、組織API、Generator Buildや全Protocol対応を必須化しない。


## 35. 2026-11-05：Required Case GateとDB／Role／Actionの条件付きSkill案内

### 必須テストが「実行されて成功した」証拠へ進める

[TEI merged #2835](https://github.com/hat47x/tei-platform/pull/2835)の実PostgreSQL偽緑対策を既存SK-02試験票へ移植した。[SK-02 §16](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)の[既存CI](../../.github/workflows/tai-sk02-synthetic-pair-check.yml)でE01〜E60の**required ID集合、報告ID、重複、欠落、合成実行結果**を別に確認する。実CI [#42011377630](https://github.com/hat47x/tai-pleroma/actions/runs/42011377630)はrequired/reported/distinct=60、欠落・未知0、passed=total=60で限定PASS。前段のNode終了コード0だけに頼らない。

ただし、現実のH2/H3に必要なSourceの実消費・Skill実Loader・実Tool Invocation・独立Task Oracle、実Audience/GrantとEgressはこのCIで検証しない。Test-only自己報告をBusiness正答・全Source Coverage・Owner受理に昇格しない。[TEI AI-first計画 #2811](https://github.com/hat47x/tei-platform/pull/2811)のRequired/Discovered/Attempted/PASS/SKIP/Qualified分離を採る。TEI Draft [#2813](https://github.com/hat47x/tei-platform/pull/2813)のDSL JSONと[#2828](https://github.com/hat47x/tei-platform/pull/2828)のDriver Scenario JSON、[#2830](https://github.com/hat47x/tei-platform/pull/2830)の固定6-Step証拠は**異なるProduct試験**。各exact-head CI成功も当該局所Go/Scenarioに限り、AI自律生成・H2/H3独立Oracleや外部二Harnessを証明しない。新共通Scenario Runnerなし。

### TEIの高度機能は用途を選んで専門入口へ委譲する

[TEI Draft #2862](https://github.com/hat47x/tei-platform/pull/2862)で成熟したDB別Query/2way SQLの判断は、**意味上のData/Query Contract→Function Data Context/実Data Source Binding（Read/Write・Scope）→Provider/Dialect SQL候補選択→Source/候補集合・Lock→実Build/DB読取・結果→Consumer/実Effect**を分ける。DB名やNative SQLファイル名で接続先・Authorityを推測せず、固定済み専用SQLが消えた場合も共通SQLへ無音Fallbackしない。2way SQLのコメント例値は実引数／独立Expectedではなく、動的WHEREが外れてRead Scopeが拡大する負例に注意。**#2862は設計Draft・実Provider/DB互換は未実証**。最初のTEI read-onlyモデル調査やTAI Skill rootに、SQL Parser・新DB Adapter・DBX-01〜09すべてを必要条件として持ち込まない。

[TEI 自己記述 Draft #2860](https://github.com/hat47x/tei-platform/pull/2860)のRole/Attribute・Semantic Parser/Source locatorは、**構文読取・Role属性・Accepted Meaning・実Role Interpreter/Provider資格**を分ける（Role属性があるだけで正式Role契約ではない）。[TEI Action #2616](https://github.com/hat47x/tei-platform/pull/2616)は、渡されたPreconditionがPASSでも必要なPeriod/Effect/Grant等の**全Required Checkを満たすとは限らない**こと、RunPlanが途中Blockしても先行StepのEffectが残り得ることを反証へ追加した。実PostgreSQL CAS等の個別成果が存在しても、**Source→Offer→現Grant→実Target/DB/Provider→Receipt→独立Readの一Attempt成立**とは別。実書込みを伴う要求が来た時だけ、そのProduct Ownerの実Contractと観測を要求し、TAIへ第二のAction/SQL/Policy Hostを作らない。

### 初回の投資判断を据え置く

**Blocking**はまずTEI Product Skillの同一Harness H2/H3・4独立Session、実Skill Load・許可されたCLI/Source・独立Task Oracle・総コストだけ。DB方言、2way SQL、Role自己解釈、実DB更新、SHO Reader、EKI低遅延/マルチモーダル、第二Harnessは**その能力を要する実TaskでのみConditional**。同じ形式のSourceや成功したテストがあっても、用途・Audience・期限・Scope・Provider資格が異なれば結果を移植しない。不要なSkillを使用しなかったことも成功条件にできる。

状態：本節は**既存CIの小変更とProduct別Design/CI証拠の整理**。外部Harnessの4Session、DB別SQLの実行・性能、自己Roleの正式解釈、Owner意味受理、TAI製品間Consumer E2EはNOT RUN。#2862/#2860の後着CIはそのexact HEAD/実Jobごとに判定する。Product側正本をTAIへ複製しない。


## 36. 2026-11-05：Required Evidenceの欠落を拒否し、Product固有拡張を初回Skill実証へ持ち込まない

**成熟した実装差分**：[SK-03 §12](harness-interoperability-and-handoff-pilot-2026-11-03.md)に対応し、既存SK-02/03のGitHub Actionsを修正。SK-02のE01〜E60に続いて、SK-03のNC01〜NC19の**Required ID・件数・重複・期待する結果分類**を独立表と照合し、必要なケースが実行されていなくてもプロセス終了0／総数一致だけでPASSとなる抜け道を閉じた。[限定的な実CI #42011655021](https://github.com/hat47x/tai-pleroma/actions/runs/42011655021)ではSK-02 60/60、SK-03 19/19のケース一覧と分類が一致。今回の「PASS」は**Node実プロセス上の人工テスト**の完全性であり、実Product/Harness、Source Load、独立Oracleを保証しない。

**背景**：[TEI merged #2835](https://github.com/hat47x/tei-platform/pull/2835)は実PostgreSQL TestのSKIPにもかかわらずGo exit0の反例を確認済み。[TEI Draft #2811](https://github.com/hat47x/tei-platform/pull/2811)が区別する Required／Discovered／Loaded／Executed／Qualified と、[TEI Draft #2830](https://github.com/hat47x/tei-platform/pull/2830)のScenario Execution Mode／Evidence Natureを、TAIでも**必要な実Taskの観測票の欄として**受け取る。すべてのCaseがPASSということと、実行が何を消費し、どの効力を持ち、現在どの用途で有効かは別。別製品のGo testをTAI Checkerで再実装したり、新横断Test Runner/Oracleを作ったりしない。

**初回H2/H3の入場条件**：TEI Product Skillの実ロード有無、同一の実CLI Binary/Workspace/Source、4独立Sessionと実Tool invocation、現時点の必要な開示/Grant、独立Expected・Task正答/Warning/Unknownを照合する。再実行されなかった必須項目はSKIP／NOT RUN／Unknownとして保存し、実際に成功した件数へ含めない。CI適格性と実験Value／Token/時間/人手は別票。初回一つのread-onlyモデル調査に、全DB/多Provider/GUI/Web/EKI/SHOを義務化しない。

**Product別の条件付き接続**：

- [TEI DSL自己記述 Draft #2860](https://github.com/hat47x/tei-platform/pull/2860)は実Workspace/Source Index/Go Parserに紐づくtest-only境界を追加したが、Role文字列を解析できることはRequired Shape／意味受理／実Host権限ではない。必要なTaskにのみTEI OwnerのSource/Role/Operator版と実Loaded Witnessを要求。
- [TEI DB別Query/2way SQL Draft #2862](https://github.com/hat47x/tei-platform/pull/2862)はDocs-only。特殊SQLを必要とする場合だけ実対象DB/Provider Bindingから候補を選び、SQL Asset版・適用Scope・失効・無音fallback禁止・動的条件の全件化・Provider実Effectを別検証。DB名やSQLファイル名が実接続先／実権限を自動確定したとは言わない。最初のSkill比較にDB別SQL仕様採用を要求しない。
- [TEI merged #2850](https://github.com/hat47x/tei-platform/pull/2850)はafter-commit／compensation EffectObserverが必要なのに無い場合、無人Actionを**その手前で停止する**限定実装。Actionを本当に委任するときにだけ現在Grant・PreconditionのRequired Set・実Observer・Commit／不明結果・Consumer再読取をOwnerの実Receiptで確認する。read-only TaskにWrite Gateを追加しない。
- [TEI Scenario Draft #2830](https://github.com/hat47x/tei-platform/pull/2830)の合成6 Step証拠をAIが追加したScenarioの独立Oracleや実Provider E2Eへ昇格させない。Scenarioを実使用する場合だけ必要CaseのDiscovered/Executed/PASS、ExecutionMode/EvidenceNature/Source版・独立Expectedを照合。

**選択基準**：[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)の価値適正化に従い、上記を一括導入するのでなく、利用者Taskに必要なProduct・検証能力だけを条件付きで追加。無関係なDomain固有の検査をTAI Skill rootへ移さず、Product Ownerの契約を保つ。今回の追加は既存Workflowと計画の差分であり、実H2/H3のSkill効果／実第二Harness／実DB／Provider／Owner意味受理は **NOT RUN**。
