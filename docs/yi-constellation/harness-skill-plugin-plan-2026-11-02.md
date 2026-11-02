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
