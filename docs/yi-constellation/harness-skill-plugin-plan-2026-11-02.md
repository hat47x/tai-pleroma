# YI Constellation：外部ハーネス向けSkill／Plugin構成計画（2026-11-02）

状態：**設計提案 / Owner未受理 / 新Skillの正式配布・H2/H3独立比較と効果検証はNOT RUN**。外部DSHでTEI実Tool起動とH3 Product Skill本文・参照の限定実Loadは確認済みだが、比較適格0/4である。本書はTAIの製品横断連携案であり、各Productの契約・実装・意味受理・権限正本を変更しない。

**直近の実行経路**：[G0実OS Read許可/拒否→G1/G2 Tool/送出→新独立4 Slotの実行票](h2-h3-comparison-first-eligible-session-execution-card-2026-11-08.md)を参照。追加の設計案を初回Blocking条件にしない。

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

## 37. 2026-11-06：TAIからTEI実Product CLIの公開Sourceを実読取し、次を実Harnessへ限定する

横断計画§35〜36のNode合成必須Case Gateは維持しつつ、**実Product S1へ進めた成果**を独立に追加した。[TAI S1実Go CLI #42099390431](https://github.com/hat47x/tai-pleroma/actions/runs/42099390431)（実Job PASS）：TEI full SHA 50ebf8014340fd1906f6b35cfa30173e0ee2fc6cのGoバイナリをTAI CIでBuildし、公開Sourceのsemantic-data:sales.orderをmodel catalogで1件indexed・inspect OK・validate ok=true/診断3件として確認。空Workspace対照はvalidate ok=trueでもSubject 0件であり、検証成功と必要なSource消費を区別した。

実験用の[Node S1 Probe](../../evaluations/tools/probe-tei-s1-real-source.cjs)・[限定GitHub Actions](../../.github/workflows/tai-tei-s1-real-public-cli.yml)をDraft #270に追加。CLI応答がresult.entriesに包まれる点を初回失敗[#42099147476](https://github.com/hat47x/tai-pleroma/actions/runs/42099147476)で発見・修正し、最終Jobはexit propagationを含めてPASS。[Runbook §15](first-real-skill-qualification-runbook-2026-11-02.md)がSource/実Binaryハッシュと完全な実測範囲の記録、[SK-02 §17](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)が次のH2/H3への引き渡しを担当する。

**最優先の未達Gateは変わらない**：外部Harness一つでH2 Tool-only/H3 TEI Product Skill実Loadedを同一公開Subject・固定Binary・独立Task OracleでH2→H3→H3→H2と比較する。新S1はTEI側既存CLIをTAIから直接実行した**Product-only実観測**であり、実AI/Skill Loader・第二Harness・実Grant/外部Egress・独立業務Oracle・Owner意味受理を証明しない。TEI既存#2605・TAI #168/#271/#422を継続Ownerとし、DB/Provider、Studio、EKI、SHOの高度機構や新Host/中央Registry/第二Readerを初回の必須Gateへ追加しない。


## 38. 2026-11-06：実DB/未知Commitの成果を条件付きHandoffへ接続する

他チャットのTEI Script起動・実DBテスト・Harness #8の証拠鎖を[SK-03 §13](harness-interoperability-and-handoff-pilot-2026-11-03.md)へ集約した。特にTEI [merged #2853](https://github.com/hat47x/tei-platform/pull/2853)による**製品Invoker→Lifecycle→実PostgreSQL CASの限定E2E**、[merged #2854](https://github.com/hat47x/tei-platform/pull/2854)の**A→B→A／新idempotency keyで再適用され得る反例**、[merged #2850](https://github.com/hat47x/tei-platform/pull/2850)の**観測不能なafter-commit／compensationを無人で開始しない停止条件**を、既存Productの実装事実として採用する。Receiptの本番永続化・署名・保持、OS/Network障害、業務受理をこれらの試験結果から推定しない。

**判断**：Skillを通じた業務操作には、Source/Meaning/Current Grant、実Invocation、Operationの永続同一性、Tx outcome、Receipt、独立read、Consumer納品の段階を設ける。しかし**これらはTEI/EKI/Hostの実機能・観測を使う**のであり、TAI Skillが自動再送Policy・第二のOperation ledger・共通Provider/Hostを実装するのではない。結果不明時は、同じOperation IDを再照会できる証拠が無い限り、新Keyの再送を成功回復として扱わない。値一致のCASだけで二重作用を防止できるとも主張しない。

**ロードマップの変更点**：P0のread-only TEI Product Skill H2/H3は**変更しない**。P1の第二Harness引継ぎは実read-only Source/Tool/Grantを対象に開始し、P2で必要な**実書込みTaskだけ**HX-CM01〜07を条件付き実証する。Script起動設計の失敗時境界・TEI #1129/#1174/#2564、EKI Result/Recovery Ownerとの重複Issueを増やさない。横断価値の測定は「何を実際に安全に完遂できたか／回復できたか」とToken/時間/人手を別々に扱う。

**実証資格**：本節のGitHub変更はTAIの文書・試作Skill参照に限り、実DB・Command・Effect/OS・外部Harnessの新実行ではない。正式Runbook・Product契約の採用、実接続・Owner意味受理は**NOT RUN**。

## 39. 2026-11-06：実Sourceの宣言・Index byte・Requiredを独立に照合し、実Harnessへ進む

前節§37の実TEI S1について、Catalog/Inspect成功を**指定原文がIndexに取り込まれた証拠**へ一段強めた。[TAI S1 Source Probe](../../evaluations/tools/probe-tei-s1-real-source.cjs)と専用CIで、実InspectのSubject、artifacts.pathとSHA-256、role=definitionのSource Index referenceを、別読込した公開Sourceのbyteへ照合。さらにCatalog／Inspect／ValidateのWorldFP・SourceIndexFPを突合し、別file・古いfingerprint・他Subject・Index/definition欠落などS1-W01〜08の負例を検査。**[実CI #42101157330](https://github.com/hat47x/tai-pleroma/actions/runs/42101157330) completed/success**：合成8/8、同一固定TEIの実InspectでSource一致・definition参照1件を確認。[Runbook §16](first-real-skill-qualification-runbook-2026-11-02.md)と[SK-02 §18](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)を実行／比較の正本へ追補。元Runの証拠値は[記録JSON](../../evaluations/records/TAI-TEI-S1-real-public-source-2026-11-06.json)へ保存。

**他チャットとの整合**：[TEI自己記述Draft #2860](https://github.com/hat47x/tei-platform/pull/2860)の独立Required対照と同じく、**候補が自分で宣言したRequired・Role/Source・返したPASSだけで自身の意味を認定しない**。TAIのS1では固定の外側Expectedを先に持ち、TEI実LoaderのIndexと比較する。ただしAtomic全Import closure・Owner Meaning Acceptance・現在Host Grant・Build/Targetの実消費は別。§38の実DB/未知Commitは将来の**write Taskのみの条件付き出口**とし、実AI Harness read-only H2/H3のBlocked条件に追加しない。

**次の実証**：既に成立したProduct-only S1を同版でH2/H3の両腕へ引き継ぎ、実HarnessによるSkillロード、CLI呼出し、独立正答判定と実費用を比較する。TAI側に新しい共通Source Resolver／実行Host／Test Runner・第二のOracleを導入しない。AIによる試験候補の増加は制限しないが、必須結果と未実行を識別する。二Harness Handoff・実DB/Provider・SHO/EKIは用途別に後続する。


### 39.1 実S1の再現性を台帳・実CLI再実行で検査（2026-11-06）

**成熟した実装差分**：既存S1 Source Probeへ[`--verify-ledger`](../../evaluations/tools/probe-tei-s1-real-source.cjs)を追加し、新しいProduct-only実CLI Receiptと従来の固定[Evidence JSON](../../evaluations/records/TAI-TEI-S1-real-public-source-2026-11-06.json)を**31項目**突合する。[Actions #42106804110](https://github.com/hat47x/tai-pleroma/actions/runs/42106804110)では実TEI Go CLIを固定改訂で再ビルド・実読取して**31項目一致**、Source digestを改ざんしたReceiptは`ledger mismatch: source bytes`で非0拒否。この検査をCIの実ファイル入力経路に接続し、Evidence台帳そのものの変更でもWorkflowが起動するよう更新。[初回実Skill Runbook §17](first-real-skill-qualification-runbook-2026-11-02.md)へ再資格化の停止規則を反映した。

**比較実験への取り込み**：SK-02のH2/H3に使うS1 Source/実Binary Pinの**再現性証拠**として使うが、対象を実Harnessが読んだこと、実Skillがロード・利用されたこと、独立Task Oracleで正答したこと、通信が実Grantの範囲内だったことは別Gate。新HEADや別Hostへ旧Ledgerを「そのままPASSで移植」しない。差分はMismatch→Source/Expectedの再固定→新Ledger作成の順であり、**旧記録を上書きして履歴を消さない**。以上はTAIのProduct S1 test-only検査であり、TEI本体のSource/Role/Host契約を変更しない。

**他チャットからの条件付き判断**：[TEI merged #2882](https://github.com/hat47x/tei-platform/pull/2882)は実Workspaceテキスト由来のPeriod/Effect前提を合成した限定Go試験で未充足ならStep実行を止める。[TEI Draft #2884](https://github.com/hat47x/tei-platform/pull/2884)はScript起動のSelection/Context Epoch、Operation identity、Commit結果不明、Required/Observed/Undischargedを区別する**文書設計**であって実Restart試験ではない。両成果はTAIから実際にWrite/再開を委任するときだけ、既存§38のTEI/EKI Ownerによる`EffectPreconditions`・Operation Receipt・Current Grant照合へ引き継ぐ。初回のread-only TEI Product Skill比較へCommit/Period/二Process再開を必須化しない。

**未実施**：実AI HarnessによるH2→H3→H3→H2、Skill実ロード、別Harness Transfer、Consumer実受信、業務意味Owner受理、現行OS/Network開示強制。実CIの再現性PASSを外部Agentや本番業務のPASSへ昇格しない。


### 39.2 既存S1 Ledgerの曖昧JSONを実行前に拒否する（2026-11-06）

実ProductのS1証拠は、固定された[公開台帳](../../evaluations/records/TAI-TEI-S1-real-public-source-2026-11-06.json)と実CLIの当回Receiptの31項目照合まで進んだ。一方、`JSON.parse`単体では同一member二重定義が後勝ちで上書きされ、台帳／Receipt／CLI戻り値に曖昧な入力があっても一致に見える余地があった。そこで**新しい正本やParserを導入せず**、既存SK-02の[重複キー拒否](../../evaluations/tools/check-sk02-pair-eligibility.cjs)を[実S1 Probe](../../evaluations/tools/probe-tei-s1-real-source.cjs)で再利用し、S1-W09〜13と、実Receipt/台帳への二重key注入を[既存CI](../../.github/workflows/tai-tei-s1-real-public-cli.yml)へ接続した。

初回CI [#42107218625](https://github.com/hat47x/tai-pleroma/actions/runs/42107218625)では、実Go Binary→Source照合31項目・既存SHA改変拒否は通過したが、**重複key拒否ログに機械判定用エラーコードが出ず、新しく加えたgrepでJob失敗**。受入を推測のPASSにせず、S1 ProbeのCLIエラー出力へ既存`e.code`を付与する限定修正を実施。成功判定はその後のexact-head実CI完了を待って記録する。

**資格の上限**：JSONの解釈を一意にすること≠Ledgerの第三者署名、独立Oracle、Source全閉包、Productのmeaning受理、外部HarnessのSkill Load。**次の価値確認は依然H2 Tool-onlyを実Harnessの一Sessionで動かした記録**であり、S1で新しいハーネス／DB／Actor Runtimeを作らない。[実施Runbook §17/18](first-real-skill-qualification-runbook-2026-11-02.md)に従う。


### 39.3 実Skill比較のParticipant Taskを固定し、評価票を隔離する（2026-11-06）

現行S1の「公開TEI Productを実読めた」成功から、次の価値検証SK-02へ直接渡す**新しい実装・運用差分**を確定した。[参加者向け固定Task](../../evaluations/fixtures/sk02-tei-public-read-participant-task-2026-11-06.txt)の本文だけをH2/H3各Sessionへ渡し、SHA-256 `38a0b238018e050f2116f10f1ca2cb3a54319c2743e2fb9bbe128d4be96a84cf`を既存の[SK-02 CI](../../.github/workflows/tai-sk02-synthetic-pair-check.yml)で固定した。Taskは公開Subjectを調査させるが、採点対象の属性名・型、Source path、診断件数を教えない。**H3だけ異なるPromptを使うとSkill差を測れない**ため、4 Sessionに同じbyte列を使用する。[Runbook §18](first-real-skill-qualification-runbook-2026-11-02.md)と[SK-02 §19](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)に実H2→H3→H3→H2の運用手順、Skill実Loaded/Tool実受信とChecker比較資格/独立Oracle正答を分離する停止条件を記載した。

**隔離の重要条件**：TAIリポジトリ全体を外部HarnessへMountすると、本Repo内のRunbook/証拠台帳から評価対象の答えが閲覧され得る。Participantには固定Task本文＋許可された公開TEI Source・Toolのみを渡す。Reviewerの独立Expected/答え合わせ票・他Session回答を、Prompt・Skill・閲覧可能なFile/Tool出力へ漏らさない。共有できる公開Sourceをモデルが自ら読むことは正常なTask行為。Host観測が無いのに`oracle_exposed=false`、`unauthorized_egress_observed=false`と自己申告することは比較資格ではない。

**変えない範囲**：TEIのS1実CLI/Source/Indexの再現性ゲートは保持。SK-02の一つのread-only Product TaskにEKI/SHO DB Provider/Target Build/TAI横断Skillを投入しない。新Wrapper・Task Runner/Owner Oracleの実装を増やさない。次の本質的な証拠は**実HarnessでH2の一Sessionが動き、Skill非露出と実Tool argv/Sourceの観測が得られたこと**から開始する。Skillあり二Session・残りH2を続け、4試行後にのみ増分価値を採点する。現在は**NOT RUN**。


### 39.4 S1の実CLI実行引数と証拠Hashを別々に検査する（2026-11-06）

**成熟した欠落の修正**：[S1 Probe](../../evaluations/tools/probe-tei-s1-real-source.cjs)が実CLIの`stdoutDigest`をLedgerの固定Digestへ照合していても、元Receiptの`observations[].args`と`cwd`の一致は検査していなかった。実Source読込、モデル/ワークスペースの参照閉包、H2/H3比較条件を横断して検討した結果、**「結果Byteが一致」と「どの対象を要求したか」が別証拠である**ことを既存検査へ反映した。4つの固定read-only argv・同一絶対CWDを照合し、31既存比較→39項目（追加8項目）、合成S1-W14〜W19と実CLI Receipt改変負例を追加した。

これにより、外部Harnessへの移行前に偽のWorkspace・別Subject・write option・別CWD・順序入替を**実S1票の内部矛盾として**拒否できる。GitHub Actionsの成否は変更後のJobログに束縛する。**改変可能なReceiptの文字列検査は実Processの第三者証明でも実Host認可でもなく**、Source実消費の全閉包、Owner Meaning、H2/H3 Tool呼出しやSkill実Loadを保証しない。

順序は従来どおり、固定TEI実CLIによるW0/S1→**外部Harnessで最初のH2実Tool呼出し**→H3のProduct Skill実ロード→H2/H3四Session／独立Oracleと費用比較→必要時のみSK-03の第二Harness。新Runner／万能Evidence Platform／中央Validatorは増やさず、書込み/未知Commitは既存条件付きHandoffへ残す。[実証Runbook §18.2](first-real-skill-qualification-runbook-2026-11-02.md)で具体的実装・停止条件を管理する。


### 39.5 実Skill比較の評価母集団とOracleを分離する

実H2/H3の価値評価では、Skillの配布・Load失敗を除外したPP（実利用に限った適格比較）だけを示すと実運用の価値を過大評価し得る。初回4独立Sessionについては[SK-02 §20](../../evaluations/SK-02-first-real-product-skill-paired-pilot-2026-11-03.md)の**ITT＝割付全数**と**PP＝実Skill/Source/Tool利用が観測された比較対象**を分け、試行数・Loaded/Not Loaded・Task Oracle・Tool回数・費用と未確認の割合を一緒に記録する。Checker`eligible-to-score`はPP候補の形式判定であってITT実績を消さず、Skillの因果改善率にもならない。

まず既定の公開Subjectを明示したTaskで最初の実H2一Sessionを観測し、H3実Loaderと4Session比較へ進む。事前に例示されていないSubjectの探索は将来の**別Task/別Expected**とし、参加者Promptや参照ファイルに正答を漏らさない。Task種別をR/Dと命名せず、Runbook §21のR＝割付・D＝実提供の定義を維持する。[Runbook §21.1](first-real-skill-qualification-runbook-2026-11-02.md)へ連携。TEI実S1とSK-02メタデータ合成CIの合格は、この実験の利用価値・外部Harness機能をまだ証明しない。

**今回の実装をP0へ反映**：比較腕の`prompt_digest`を互いに比較するだけでは、**4腕すべて同じ誤Prompt**でも比較資格ありと誤認し得る。既存[SK-02 Checker](../../evaluations/tools/check-sk02-pair-eligibility.cjs)に`--task-file`を設け、[事前固定Participant Task](../../evaluations/fixtures/sk02-tei-public-read-participant-task-2026-11-06.txt)の**原byte SHA-256**をReviewer側で算出して試行票と照合。原文が無ければ`insufficient-evidence`、全腕同じ誤Promptなら`ineligible`。[GitHub Actions #42110536408](https://github.com/hat47x/tai-pleroma/actions/runs/42110536408)では実CLIファイル引数の合成正例・二負例と旧E01〜60が成功。SK-02 §20とRunbook §21に引継ぎ、**実Harnessへ受信したPromptの一次記録は依然必要**とする。新共有Runtime/Oracle/Adapterは導入しない。

**他チャットの新しい反証を条件付き保持**：[TEI自己記述Draft #2860](https://github.com/hat47x/tei-platform/pull/2860)が確認した同PathのLoad後Source変更と、同一属性への重複Role宣言がParserで上書きされ得る例は、Candidate/宣言値だけでSourceの版・Role一意性・Owner受理を主張できないことを示す。必要なTaskで元Source byte・Source Index・使用時点の差を調べるが、今回の公開`sales.order` read-only TaskにRole InterpreterやStudio Writerを実装させない。[TEI Script起動Draft #2884](https://github.com/hat47x/tei-platform/pull/2884)の再起動後Operation ID／Receipt未確定の扱いは、実Write Taskへ進む場合だけ§38のConditional Gateへ接続する。いずれも**Draftの設計・限定characterizationを本番完全性の実証とは見なさない**。


## 40. 2026-11-06：SHO実Reader候補の両OS実証を条件付きProduct Skillへ引き継ぐ

[SK-03 §16.5](harness-interoperability-and-handoff-pilot-2026-11-03.md)へ、SHO [Draft Reader #17](https://github.com/hat47x/sho-composer/pull/17)の実装と[Ubuntu/Windows実CI #42109343155](https://github.com/hat47x/sho-composer/actions/runs/42109343155)のJobログを反映。固定HEAD `b4176b0d…`では`markdown-it 14.3.3`を実ロードし、Markdown raw file/digestを読み、限定GrammarのLink Occurrenceを抽出する**実Node Reader候補**が各OSで14/14 PASS。旧計画の「SHOには製品Reader実装がない」は、少なくともDraft候補の存在という点で更新が必要だった。

**製品ごとの異なる資格**：TEIには固定Go CLI/一公開Source Indexの実S1が存在する。SHOにはNode22の実disk Reader／選択Parser／発生順・包含行を確認する局所CIが存在する。いずれも**外部AI HarnessがSkillを実ロード・活用した証拠ではなく**、Source/Parser/Targetの全てに同じPlugin資格を付与しない。SHO候補の`status=indexed`は`coverage.allDocumentReferencesEnumerated=false`を伴い、全参照・リンク先取得・実レンダリング・文書意味受理の主張ではない。`source.revision=unknown`とSnapshot局所ordinalを永続Source/Occurrence IDへ昇格させない。

**優先条件の更新**：P0は依然、固定Participant TaskによるTEIの**最初のH2実Harness Tool call**→H3実Skillロード→4独立SessionのITT/PP・独立Oracle比較。P1のSHOは「Readerを0から作る」ではなく、#16/#17の**正式Reader/Parser契約・未定義参照/BOM等の不足・Parser版差・Source失効**のOwner受入に必要な残差を検証する。P2のSHO Skill配布やTEI↔SHO引継ぎはProduct能力・実Audience/現在Grant・実Reader/Consumer受領が必要なTaskが存在したときだけ実施。Document WriterやProvider/外部Webを初回のTEI H2/H3試験へ足さない。

この統合は文書上の**観測事実・次試験の優先順修正**であり、TAIがSHO Readerを実CLIで呼んだことや、SHO #17がmain統合・Owner正式受理されたことを意味しない。QSB-01〜05、実SHO Skill、実二Harness、実ネットワーク/公開、Source Identity／全引用の意味受理は引き続き**NOT RUN／NOT ACCEPTED**。新中央Host/Plugin Registry/Readerを導入しない。

## 41. 2026-11-06：初回H2のSkill非露出とH3のProduct Skill版を同じ実TEIで固定する

横断SK-02の次価値Gateは実AI Harnessの**最初のH2 Tool-only 1 Session**であり、合成CheckerやProduct CLI CIを積み増すことではない。ただし、初回のファイル露出とSkill Package pinに**実験条件の欠落**があった。固定TEI Checkout自体に`skills/yi-tei-modeling`が含まれているため、**H2へTEI repo丸ごと公開してSkill Loaderだけ無効化しても、Skillの原文を読む迂回経路が残る**。これをH2の非露出成立とは認めない。

**同じProduct改訂からの2種類の証拠**：固定TEI commit `50ebf8014340fd1906f6b35cfa30173e0ee2fc6c`の実Go CLI／公開`reference/workspace`を共通に用いる一方、H3でだけ与えるProduct Skill root（Git blob `9cd8475bd6489c6661ae644bf771cfcce04188b1`）とreference（`ec2f90e85ed42659aca8b44a9be216987860b099`）の原文を固定。[既存TAI実S1 CI](../../.github/workflows/tai-tei-s1-real-public-cli.yml)に`git hash-object`による2ファイルの照合と、**H2にはBinary＋Workspaceのみ／H3には同じもの＋Skill candidate root/referenceだけ**を配置した一時ファイルビューによる実`model catalog`／`inspect`／`validate`の対照を追加。CIが成功した場合に言えるのは、同じ実CLIの限られたSourceをH2/H3両ビューで読めるという**準備段階の事実**まで。実HarnessのMount・Tool、ネットワーク遮断、Skill実Loader、Ownerの意味受理を証明しない。

**固定Product Skillに残る真正の不一致を保持する**：同Product Skill rootは`model catalog`を`entries[].subject.kind/id`と記載するが、同TEI版のCLIは `result.entries[].subject.kind/id` を返す。TAI S1初回の同じ契約誤読失敗と実Go sourceから確認済み。詳細referenceには今回Task指定の`subject-id sales.order`そのものを使う例がある。またSkillは`go run ./cmd/tei`を例示するが、比較Tool Profileの実行対象は両腕の固定済みGo Binaryに限定する。これらをH3の実験途中で黙って修正・差し替えず、**Skill版由来の手順エラー／例示依存／逸脱として実観測**する。[TEI Product Owner #2605](https://github.com/hat47x/tei-platform/issues/2605)へCLI envelope記載の訂正を戻し、[文書修正Draft #2863](https://github.com/hat47x/tei-platform/pull/2863)を混ぜるなら別Skill treatment・別Trial Groupで再資格化する。

**判断**：初回の問いは「公開Subjectを**提示した**場合に、既存のProduct Skillが同じToolで誤操作を減らすか」。Skill詳細に同Subjectの例示がある以上、未例示Subjectの自律発見一般・平均因果改善の主張はしない。実H2/H3では、同一Task SHA・元Source/Tool/Model/Grant・独立Oracleを固定し、H2にSkillやTAI試験票がTool/GitHub/検索経由で漏れないこと、H3の実root/reference byte Loadを別ログで観測する。**R（割付）／D（実提供）・ITT／PP**は既存Runbook §21、[新§22](first-real-skill-qualification-runbook-2026-11-02.md)に接続し、実Loaderが無ければ成功試行のふりをしない。新Harness Host、専用Sandbox、第二Skill配布Registry／再実装CLIを作らない。

**他Productとの接続**：SHO [Draft #17](https://github.com/hat47x/sho-composer/pull/17)の限定Readerの実Node/両OS証拠は§40へ既に反映済み。TEI [Draft #2860](https://github.com/hat47x/tei-platform/pull/2860)の同Source時間差・Role繰返し情報落ちと[Script起動Draft #2884](https://github.com/hat47x/tei-platform/pull/2884)の再起動後Unknown/Operation IDは、将来その機能がTaskに必要な場合のみ既存Owner受入Gateへ戻す。これらをTEI初回read-only Harnessの必須実装としない。

**追試済みの証拠と保存先**：[TAI実S1 Actions #42112462908](https://github.com/hat47x/tai-pleroma/actions/runs/42112462908)のJobは**completed/success**。固定Product Skill root/referenceのGit Blob一致、実Byte SHA-256取得、H2 Skillなし／H3 root+ref候補ありの別ファイルビューに同一実TEI Go Binaryと公開Workspaceを配置したこと、各ビューの実CLI `catalog/inspect/validate`とSource／World／Index FP・diagnostics一致をログで確認した。詳細は[Runbook §22.4](first-real-skill-qualification-runbook-2026-11-02.md)と[新Evidence記録](../../evaluations/records/TEI-H3-fixed-product-skill-staged-preflight-2026-11-06.json)へ固定し、CIでEvidence RecordのSource raw byte pinも検査する。Product Skillに残るCLI envelope記述の不一致は[TEI #2605](https://github.com/hat47x/tei-platform/issues/2605#issuecomment-6670006488)へ報告した。

**残る出口**は変わらない：実AI Harnessで限定ビューを渡したH2 1 SessionのTool Request／実argv/exit/stdoutとSkill非露出、続くH3でのProduct root/refの実Loadを**実Harness自身のログ**で確認してから、4 SessionのITT／PP・独立Expected採点へ進む。ファイルを配置したCIの成功を「実Skill Loaded」や「Host/OS Egress隔離」としては使わない。

## 42. 2026-11-08：独自Harnessの投資境界、TEI共通Application API、状態付き媒体を接続する

**独自Agent Loopの設計・導入は未決定**。関連判断の正本：[外部Harness活用と独自Harness投資の段階判断](harness-build-vs-buy-decision-2026-11-08.md) §1〜11。外部DSHを含むHarnessはTool/Model/LoopをPlugin化できるため、YI側はまずProductが持つ型付きCapability・意味・根拠・Effectと、薄いHarness Adapter/必要時だけLoadするSkill/専門Pluginの価値を実証する。DSH/CordisにTEI内部Plugin ABIを固定しない。

**2026-11-08採用済みTEI ADR-0048との差分**：CLI/MCP/HTTP/Web/Desktopの同じOperationはTEI内の共通Application API（HTTP必須ではない）を呼び、Hostが選んだProviderとGrantを使用する。外部HarnessのTool／SkillやVUIのStateful Dialogueは、このOperationを呼ぶ*利用者*であって第二Operation Engineではない。音声/ASR/TTS・人の操作・画面・LLMの候補生成は媒体別Adapterに分け、業務上の合法遷移、expected revision、承認、Idempotency/Unknown ReceiptはProduct／実Hostが強制する。Flowを扱うからといってYI中央Agent Loop／Workflow Serverを必須にしない。

**投資判断の比較軸**：
- **HV-0〜HV-4**＝LLM/従来操作の対照→既存Harness＋Product Tool→＋Skill→＋専門Plugin→独自Loop。これは**実験ラベルのみ**。初回のH2 Tool-only/H3 Skill有は既存SK-02のSlot名であり新しいHV段階と同じステータス体系ではない。
- 独立Task/Source/Expectedに対してModel・Harness・Tool/Skill/Pluginを**一度に一要因**変え、正答だけでなく保留/重大誤成功/不要停止、Source引用、未知Effect再送、Host開示、Consumer実受領、時間と総TCOを評価。必要時にModel×Harnessの交互作用も検査。音声を使わない決定論的Flowも対照系として維持。
- 専門PluginはCapability Discovery／限定Projection／Preflight／型付き結果／実Effect/Receipt／Handoffの**既存Ownerを結ぶ接続点**から最少採用。Plugin lifecycle cleanupを業務rollbackと同一視しない。Provider Bを選んでAが呼ばれたら同ResultでもFAIL。TEIの[ADR-0048](https://github.com/hat47x/tei-platform/blob/main/plan/adr/0048-shared-application-api-and-transport-adapters.md)・[#1251](https://github.com/hat47x/tei-platform/issues/1251)・TAI #232/#271の資格を横断で参照し、別Validator/Registry/Authorityを設けない。

**実行順（Hard Gateを増やさない）**：P0は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)既存G0 Read-deny→G1/G2 Tool/送出/Reply→独立H2→H3→H3→H2 4 Slot（現状0/4比較適格）。P1はTEI ADR-0048の限定Production入口と実Provider選択のOwner試験。P2は**合成**の状態付き高影響FlowをTool-only/Skill/専門Plugin/決定論的Flowで比較し、必要ならVUIを異媒体の追加対照とする。P3は複数の外部Harnessで同じ重大欠落が再現し、専門Pluginでは解消できず、複数年TCOとOwnerが受理可能な場合に限り**局所独自Loop**を評価する。

**現状の限界**：採用済みなのはTEIの設計ADRであり、全入口の同値・実Provider選択の全操作、専門PluginのHV-3有効性、VUI Flow、H2/H3の独立適格比較、独自Loopの必要性は未実証。医療分野の研究結果は医療以外へそのまま外挿しない。Owner正式採用／本番運用はNOT RUN。

## 43. 2026-11-08：Interaction／Business／Adaptive FlowとHarness投資の接続（既存Ownerへの引渡し）

**今回の正本**：[Build-vs-Buy判断§12〜15](harness-build-vs-buy-decision-2026-11-08.md)。[TEI #3503](https://github.com/hat47x/tei-platform/issues/3503)で新たに具体化されたInteraction Flow、[TEI #3509](https://github.com/hat47x/tei-platform/issues/3509)のB2C完全Headless/Conversion Engineering Plugin、[TEI #3278/#3279](https://github.com/hat47x/tei-platform/issues/3278)の原子的Trait実装義務、[TAI #165](https://github.com/hat47x/tai-pleroma/issues/165)の非定型Case活動を、既存TAI #168/#271/#488の後続試験に**別の領域圧力ケース**として配置する。外部Harnessで動くことと、TEI自身が生成する業務アプリ／Flowで動くことを一つの合格にしない。

| 領域 | Harnessが担うところ | Productが強制するところ | 最初の反証（既存OwnerがExpectedを管理） |
| --- | --- | --- | --- |
| Activity/Adaptive Case | Goalに沿う探索と再計画・道具選択 | TAI/SEIのSource/未決/期限・現在資格。Effectは実Host | 未知事象→矛盾観測→低リスク作業は継続、高リスクAction停止（TAI #165） |
| Interaction Flow | 入力候補・質問・応答・説明 | TEIの確定Event/State/Revision/Operation binding | ASR曖昧、確認後の価格変更、旧Grant、timeout/resumeでEffect 0またはunknown（TEI #3503 IF-02〜06） |
| Business Operation | Tool/MCP/CLIを通じた型付きOperationの呼出候補 | TEI ADR-0048、実Provider/HostのGrant・Operation ID・Receipt | 選択B→実A呼出し、古いRevisionのCommit、ACKだけで成功判定（TEI #1251/#3503） |
| 高度B2C | 必要なときだけ開発・分析支援Skill | Headless Contractと独自Frontend、Analytics/Commerceの各Owner | TEI UI/AgentなしでもUX/売上導線を妨げず、Experiment/Actionの契約差分が有益（TEI #3509） |

**図表とPluginの再利用条件**：FlowはSourceのGraph/Roleまたは正本への編集ProjectionからGenerator入力へ接続する候補。固定するのはEvent/Operation/Effect/RevisionとHost強制境界であり、媒体別の文言・図面・表示・状態付き質問は選択Targetの差として扱う。Extension/HookはOperation/Interaction/Generation/ObservationのTyped Bindingとし、Traitのrequired/manual/provider/generated履行はTEI #951/#3278/#3279の既存Resolverで検査する。単なるPlugin/Skillの存在、表示成功、DecoratorをGuardの強制や実Provider呼出しの証拠にしない。

**収束を保つ実施順**：P0は変えず、まずTAI #168のG0実Read-deny／G1-G2完全Tool/Reply／新規H2→H3→H3→H2の独立4 Slot（**現在の比較適格0/4**）を満たす。TEI側F0〜F4とB2C B0〜B3はそれぞれのProduct実証として**並列に探索してよいが、初回H2/H3を新Hard Gateで止めない**。続くP2では「決定論的Flow、Tool-only、＋Product Skill、＋専門Plugin」を同Source/Model/Hostの小Taskで分離し、必要時だけVUI/異Harness/非定型Caseへ拡張。B2Cの成功は収益実験のConsumer/Exposure/Commerce Outcomeで別採点し、Harnessの自動化効果へ流用しない。自前Loopは複数Harnessに共通する重大な未解決差があり、API/Plugin/Host改善で解けず複数年TCOとOwner受理が成立した場合のみ検討する。

**資格の区別**：TEI #3503/#3509/#3278/#3279のFlow/Conversion Plugin/Trait Fulfillmentは設計・受入提案であり、実媒体・実Provider・本番収益改善・Owner採用はNOT RUN／NOT ACCEPTED。今回の更新はMarkdown計画・責務接続のみ。TAI横断Skill／Product Skill／実Harness Tool呼出し／外部受信・現在Grant・業務Outcomeの既存Evidenceを上書きしない。第二Harness Runtime/Operation Engine/Workflow Host/Validator/Registry/Authorityを新設しない。

## 44. 2026-11-08：実Productの限定PASSとH2/H3比較資格を分離した実行計画

**判断の詳説**：[Build-vs-Buy文書 §16](harness-build-vs-buy-decision-2026-11-08.md)。今回追加したものはProduct横断の実施順と証拠資格の照合であり、TAI側に新しいHarness Runtime／統一Proof Store／Schema／Verifierを作らない。

| 既存能力の実証 | 実際に成立したこと | 横断Harness Trialに必要で未成立のこと |
| --- | --- | --- |
| [TEI #3482](https://github.com/hat47x/tei-platform/issues/3482) main `8ed5837` | `sales.order.submit`の限定Requiredに対し**13実CLI Reply／42 Consumer判別**がmain専用CIでPASS | 実Toolの完全配送、Function Invoke/Provider、全意味受理 |
| [TAI #537](https://github.com/hat47x/tai-pleroma/issues/537) | optional Edge型v4：投影→合成**24ケースPASS**（90段suite）。null/省略は契約上同じ投影だが参照先未解決は失敗 | Harnessの「null＝未解決」という一般的推測を禁止。異なる契約の意味を転用しない |
| [SEI #802](https://github.com/hat47x/sei-cognition/issues/802) | CLI `resume --json`とMCP `resume`概要textの現行差・実例がIssue化 | MCP実Consumerの構造化同値、basis/未決を受け取った後の利用確認 |
| [EKI #753](https://github.com/hat47x/eki-fabric/issues/753) | 実Unixソケットで**6イベント順序/内容＋4改変負例**を同一試験プロセス内で限定PASS | 別プロセス実Worker、Lease Fence、Result Body/独立DeliveryとEffect |
| [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) | DSH Tool Call／H3 Skill実ロードの限定技術証拠 | OS G0の許可/拒否正負対→G1/G2完全受信→独立4 Slot。比較適格**0/4** |

**判定規則を4列へ整理**：D=必要なSourceとScopeの充足、T=実Tool ByteのConsumer完全受領、Q=Claimに必要な根拠と適切な保留、E=実Host Effect/Receipt/Delivery/Outcome。D/T/Q/Eは同一Attemptでも別資格であり、read-only作業のEは適用外と明記できる。Sourceの限定PASSを外部Agentにそのまま伝えただけでQやEを合格にしない。新しい公開enumではなく既存[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488)比較票の記録列。

**作業順序**：
1. **不変のP0**：#168／[初回Runbook §20〜24](first-real-skill-qualification-runbook-2026-11-02.md)を実行。先にG0 OS Read-deny、G1/G2、独立H2→H3→H3→H2（ITT/PPと固定Expected）。別Productの準備完了を初回試験の前提にしない。
2. **限定Product Skill増分（P0後）**：同Source/TEI CLI/Model/Tool公開面でH2とH3を比較。DをTEI #3482の限定Requiredで検査し、Tは実Harness Tool Reply完備、Qは独立Expectedで「宣言確認と実Invoke未実証」を識別。古いCI 13/42を新Session同一Attemptの証拠にしない。
3. **別Trial Group（後段）**：[SEI Draft #824](https://github.com/hat47x/sei-cognition/pull/824)の**H3-A0**は固定TEI→SEI実CLIで推薦のローカル保存・別Resumeを限定実証済み（実Method/未決Question保存/外部Harnessではない）。次にA1でD0/D1/M1の問相対・盲検Expected比較、A2の未決保存方式はSEI #711/#678へ。MCPは同一Tool Profileを変更しない別Transport比較。EKI配送は実別Process/Result Body/ConsumerのOwner Evidenceが揃った場合のみ追加。
4. **独自Loopの投資判断（最終）**：二つ以上の外部Harnessで実重大残差を確認し、既存Product/Skill/専門Plugin/Hostで解けない場合のみ。意思決定と費用のOwnerは#422、Provider/Meaning受理は各Product。

**NOT RUN**：新独立H2/H3、SEI実Harness受領、EKI実Worker、TEI実Provider、HV-3/HV-4、Owner正式採用。本節は追補であり既存TAI #168/#271/#488やTEI #3262/#1251に第二のOwnerを作らない。

## 45. 2026-11-08：CSW探索Methodの任意導入とTEI→SEI実ローカル往復

**独立実験の実行票（後段・NOT RUN）**：[CX-01 CSW Method転用のCX-0/1/2比較](../../evaluations/CX-01-csw-exploration-method-transfer-2026-11-08.md)。現在の主P0/H2/H3に追加Blockingは設けない。

**判断の正本**：[Build-vs-Buy §17〜18](harness-build-vs-buy-decision-2026-11-08.md)。本節は「CSWを新しいAgent Harnessにしない」「必要なときだけ既存3執筆Skillから探索的手法を借りる」「実TEI→SEIローカル到達と外部DSH資格0/4を同じPASSにしない」ための実施計画。新API/Kernel/Agent Loop/Session Storeは作らない。

**実績更新（2026-11-08）**：[SEI Draft #824](https://github.com/hat47x/sei-cognition/pull/824)のH3-A0で、固定TEI `source-index`のindex/subject両Modeと独立Required、SEIのRecommendation保存→別`resume --json`読戻し、Decision専用`--unresolved`拒否後のStore不変を**実Go CLIのローカル二製品経路で限定確認**。次はA1 D0（無介入）/D1（決定論的追加Read）/M1（認知Method支援）を同じQ/予算/盲検Expectedと陰性対照で比較。方法の価値がなくてもPASSとする。これはTAI #168のH2/H3試行でなく、外部Harness実受領・SEI UnknownのNative保存・Meaning受理は未資格。

**CSWの境界**：[CSW main](https://github.com/hat47x/cultural-substrate-weaving/blob/main/README.md)は文化的体系・親和図法・思考執筆フローの**執筆用3 Skill**。そのCoreに工学向けAI Router、Runtime、Provider、認可、Mandatory Lifecycle、試験制度を加えない。TEI Plugin Lifecycleに転用する場合は、TEI #3503/#3278/#2090を題材とした**別の探索有効性実験**。現行CSWが工学要件発見に効果を持つことは未検証であり、CSWのProduct分類はTAI #73のまま未決。

| 独立実験群 | 比較Arm | 先に固定すべき観測 | 合格と誤認しないもの |
| --- | --- | --- | --- |
| SK-02／TAI #168 **最優先** | 既存B0 CLI直接／B1 H2 Tool-only／B2 H3 Skill | G0 Read許可・拒否、G1/G2完全Tool Byte、H2→H3→H3→H2新規4 Slot、盲検Expected/ITT/PP | 古い4 SessionやH3 Skillの実Loadだけの「比較PASS」 |
| SEI #824／#767 **別レーン** | H3-A0局所実CLI **限定PASS** → A1 D0/D1/M1 → A2未決 | どのSourceを実Readしたか、推薦のbasis、未決保持の資格、盲検Oracle | M1がD1と同じProbeを選んだだけで効果、推薦保存＝Method適用 |
| **CSW探索（提案、後段）** | CX-0通常AI設計、CX-1一般発散/批評、CX-2元のCSW Skillの必要部分をRead | 同じTEI Source/Task/Model/予算、既知Issue/反証のBlind Review、独立した有効な新差分と検証費 | アイデアの量、象徴からの類推、書き手の主観、原典の解釈＝TEI契約の自動受理 |

**CSW→DSHの比較順序**：①スキル本文直接Readを対照（DSH不要）→②必要な場合だけDSH既存Skill/Profileの読み込み→③Tool/Session/イベント接続の**測定された不足**がある場合に限り薄いAdapter/Pluginを検討。初回P0にCSWをロードせず、原文Skillの必要範囲・CSW CommitをPinする。探索結果はProposed Design CandidateとしてSource位置/既存Contractとの差分/反例とともにTEIに渡し、Owner受理/実Provider/Host GrantをCSW側から付与しない。

**成果測定**：独立した具体的欠落・誤類推、差分の実装可能性、検証負担、総実費と人手、追加修正の不必要さを区別。「全部のAgentが賛成した」は独立Expectedではない。既存[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)の独立VA-X/VA-E、[TEI #1445](https://github.com/hat47x/tei-platform/issues/1445)の工程比較、[#2514](https://github.com/hat47x/tei-platform/issues/2514)の判別力を再利用し、新しいOracle Engineを作らない。

**現状**：H3-A0は限定ローカルPASS、CSW-CX比較／実DSH-CSW-Plugin／A1認知Method改善／4適格H2/H3／Owner正式採用は**NOT RUN**。Productの正本は各Repo、TAIに第二正本・テスト基盤は作らない。

**追加の評価上の区別（2026-11-08／§45への接続）**：[Build-vs-Buy §6.1](harness-build-vs-buy-decision-2026-11-08.md)で、**認知Method（D0/D1/M1）・外部Harness（H2/H3）・CSW発散探索（CX-0/1/2）を互換の「能力段階」とは扱わず、別の実験軸**とした。SEI [Draft #824](https://github.com/hat47x/sei-cognition/pull/824)はTEI実CLI→SEI Recommendation保存/別CLI ResumeのA0限定PASSまで。A1 D0/D1/M1は未実施であり、同じ問い/許可Read/Budget/Blind Expectedで**妥当な決定論的Probe（D1）を弱くしない**ことが前提。D1で十分ならM1必須化もTAIの中央ルーティング実装もしない。CSW CXはアイデアの具体的新差分の独立評価であり、SEIの根拠十分性・Productの業務Meaningを置換しない。

**費用・遅延の観測Owner**：[TEI #3520](https://github.com/hat47x/tei-platform/pull/3520)のAI Tuning Observation Referenceの19合成負例はDesign/Provider/Statistics/Delivery/Disclosureの検査**のみ限定PASS**。実生成AI改善やDB性能改善はNOT RUN。横断H2/H3のTask比較は、Model Token/Tool read・Transfer/Product実処理/隔離Setup/人の修正・確認/非適格再実行を区別し、必要なSource/Provider/Scope/Revisionと実Consumer受領を結び付ける。TEI [#3479](https://github.com/hat47x/tei-platform/pull/3479)のProvider原文のみ改訂でConsumer World/Indexが変わらない反例を考慮し、Source不一致を「同一条件のコスト改善」に含めない。最初の4 Slotでは分位点や改善率の一般化をしない。これは**独自Harness要否の後段投資比較**であり、既存[SK-02 G0〜G2実行票](h2-h3-comparison-first-eligible-session-execution-card-2026-11-08.md)の新Hard Gateではない。

**直近の行動は一本化**：TAI #168のG0実Read許可・拒否の正負対を同一OS identityで示し、G1/G2の全実Tool Replyと送出を確認してから、新規H2→H3→H3→H2を割付・独立採点する。SEI Method、CSW、Tuning、実Provider、二Harness横断とHV-4は、結果に応じた別試行。必要性未確認のProduct Skill/専門Pluginは標準セットへ無条件に含めない。

## 46. 2026-11-12：選択対象の固定からHarnessへ明示送出する利用体験（後段設計／NOT RUN）

**出発点**：GUI/CUI上でユーザーが選ぶ対象（TEIのData/Function/Business・図の辺/CRUD/Query、SHOの文書/引用Occurrence、SUIのCard/Island/Canvas、EKIのNetwork/Task/Grant）は、画面遷移や誤クリックで消えてはならない。一方、選択対象を固定しただけで、AIへの送出・現在の権限付与・編集実行を自動確定しない。この節は[TAI #271のActivity/Session/View/Operation区分](https://github.com/hat47x/tai-pleroma/issues/271)、[#168のHarness接続](https://github.com/hat47x/tai-pleroma/issues/168)、[#488のSkill適合票](https://github.com/hat47x/tai-pleroma/issues/488)へ接続する**操作原則と試験入力**であり、新たなUI共通ABI・Canonical Context Store・中央Session Hostの採用ではない。

### 46.1 操作で分ける三つの対象集合

| 対象 | 利用者に見せる意味 | 責任と制限 |
| --- | --- | --- |
| **Transient Focus** | カーソル・一時ハイライト・ホバー・現在の表示範囲 | 選択元UIの状態。誤クリック・画面移動で変わる。これだけをAI依頼の対象束縛にしない |
| **Pinned Work Set** | 利用者が明示的に固定した対象・含める/除外する要素・意図・関連文脈への参照 | Product/Workspace/Qualified ID/Source・View Revision/Occurrence/Scopeを区別。画面移動で自動解除しない。実Sourceの失効や対象不在でも意図の履歴を保持し、適格性は unknown/stale 等で示す |
| **Shared Qualified Projection** | 今回のAudience・目的・操作に向けて実際にHarnessへ渡す限定Context | Product/Hostの現在のRead/Disclosureで再構成し、Preview後に明示送出。Pin内容・全画面・会話履歴・未公開関係が丸ごと送出されたとは見なさない。実送出byteとHarness受領を別に記録 |

標準的な**認知順**は「一時選択 → 対象を固定 → 含める文脈と対象版を確認 → 現在のSource/Grant/Disclosureを照合 → 送出内容をPreview → 明示Share → Harnessで実受領 → 候補を元ProductでReview/適用」。CUIでも同じ意味を持つ操作を提供するが、ここで具体的なコマンド名・ホットキー・実APIを固定しない。固定操作・解除操作は明示し、Undo/再固定を可能にする。**画面遷移中のPin保持**と**アプリ再起動・別Harness Session後の復元**は別機能であり、後者は実Productの保存/再解決が観測された範囲に限る。一度の明示Shareが、同一目的・対象・許可範囲内での毎Tool呼出しごとの重複確認を必須化するものでもない。対象拡大・Audience変更・再資格不足時は送出前に再Preview/確認する。編集Draft・未保存Bufferの存在、対象の現在性、共有の許可はそれぞれ独立に表示する。

### 46.2 Skill／Harness／Productの境界

- **Product**はQualified Targetの実解決、Source/Revision、編集可能範囲、Preview/Undo/Acceptanceと現在のDisclosureを担う。[TEI #1124](https://github.com/hat47x/tei-platform/issues/1124)の三視点/Source編集、[#2516](https://github.com/hat47x/tei-platform/issues/2516)の用途相対Construction Context、[SHO #19](https://github.com/hat47x/sho-composer/issues/19)の文書編集、[SUI #3368](https://github.com/hat47x/sui-sensemaking/issues/3368)の許可Projectionを再利用。CUI/GUIの同一意味はTEI [#3420](https://github.com/hat47x/tei-platform/issues/3420)など既存入口の実契約で確認する。
- **Product Skill**は「今固定されている対象をどう調査・操作し、何を確認するか」の再利用手順を案内する。固定対象やTool名だけで依頼を広げず、実Tool/Profileを再発見する。**TAI横断Skill**は複数Product間で必要なときだけ許可済み参照・未決・作業目的をつなぎ、現在Grantは移送しない。
- **Harness Session**は会話とTool利用の実単位。Pinned Work SetはSessionの同一性に依存しない利用者の作業意図であり、別Sessionへ持ち込む際は再解決・再開示確認する。モデル/ロール/開発Workerの割当は[TEI #4218](https://github.com/hat47x/tei-platform/issues/4218)の別責務であり、このSkill選択を上書きしない。
- **Evidenceと配布**：Rawログ/非公開Source/高容量エビデンスを、Skill bundleやGitHubへ無条件にコピーしない。**GitHubにEvidence実体だけでなく存在情報・Digest・Locatorを一切送らないlocal-only運用**も許容し、[TEI #4307](https://github.com/hat47x/tei-platform/issues/4307)のGit連動（任意）・Local CAS/NAS/S3の保管Profileと責務を再利用する。参照先・digest・取得可能性・Retention・送出範囲の区別を[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)／[#74](https://github.com/hat47x/tai-pleroma/issues/74)と各Productの保存Ownerへ委譲。保存済み≠取得済み≠現在利用可能であり、URI/Digestは新しい認可権でも読取成功の証拠でもない。

### 46.3 後続の独立反証（YIC-FC-01〜08）

| Case | 条件 | Expected / 禁止する誤判定 |
| --- | --- | --- |
| FC-01 | 固定したTEIノード/SHO引用の後に画面を切替・別箇所をクリック | 意図したPinが残り、一時Focusだけが変わる。暗黙解除・別対象への操作をしない |
| FC-02 | Pin後に原Sourceを改版・移動・権限失効 | 履歴上の意図は残るが、共有/変更の現在資格は再検証まで不明・不適格。旧版を最新としない |
| FC-03 | 同名別Scope/別Workspace、Graph多重辺・同表示名 | Qualified ID/occurrence/方向/対象版で区別。曖昧な場合はRead-only確認に留める |
| FC-04 | 未保存Bufferと保存済みSourceの内容が不一致 | 選択した対象がどちらかを示し、編集DraftをSource確定・Owner受理としない |
| FC-05 | 複数選択/大量の関連文脈で一部取得・切断 | 選択数・実共有数・欠損/切断/Unknownを区別し、部分集合を全件と断定しない |
| FC-06 | 同じ可視Contextで隠れたRaw/Relation/Tool候補が異なる | Preview/実送出Body/Tool列挙/Logに秘密の存在・件数・名前を漏らさず、[#232](https://github.com/hat47x/tai-pleroma/issues/232)/[#562](https://github.com/hat47x/tai-pleroma/issues/562)の現行Host/観測で確認 |
| FC-07 | Harness A→Bまたは同じSessionでTEI→SUI→SHOへ移る | Activity目的とPin参照は保持できても、BのTool/Source/Disclosureは現在再確認。Session継続≠Product Context/Grant継承 |
| FC-08 | 固定したEKI Task/TEI Functionへ変更・取消を依頼 | Pin/Preview/Skill Load/Task ACK≠実Host Authority/Effect。現行Grantと対象差分、Receipt/独立Readが無ければ未実施/不明 |

**順序**：最初の[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)のTEI固定H2/H3（G0実OS Read拒否→G1/G2→新独立4 Slot、比較適格0/4）へFC群を追加Blockingしない。次の別TrialでFC-01〜04を**TEI/SHOの既存公開合成Source・CLI/UI**でread-only検証し、FC-05〜07をSUI含む共有SessionとDisclosureで、FC-08をEKI/TEIのMockと実Host Ownerで検証する。CUIとGUIの差・誤解除率・誤対象・再説明/Undo・Token/Tool/人手を記録し、Skillなし・Product Skill・TAI Skillの価値を別比較。未提供のProduct機能はunsupported/NOT RUNとする。

**状態**：本節はユーザー体験/Owner境界/反証条件の計画化のみ。実UI Pin、Harness受領、共有Session、実OS/Network拒否、実Product保存・Effect、Owner採用は**NOT RUN**。新Session Server、TEI/SHO共通Agent Runtime、全製品強制起動、第二Context/Policy/Source正本を先行採用しない。

## 47. 2026-11-12：実Product Handoffに接続したSkill起動条件と現在資格（設計・限定Evidence）

### 47.1 基本判断：Skillの数ではなく、実在Capabilityと作業意図で選ぶ

§46のTransient Focus／Pinned Work Set／Shared Qualified Projectionに、**実Product Capability・必要なMethod・Harness実Load**を接続する。ただしPinやTool DiscoveryそのものをSkill自動実行・現在Grant・Meaning受理へ昇格しない。**選択の順序**は、①作業の目的と固定対象/版・Audienceを確認、②Product単独の実CLI/APIが満たせるか発見、③不足が「操作手順・専門Method」なら該当Product Skillを必要部分だけ読み込み、④複数Productで出典・未決・受領の継続が必要な場合だけTAI Activity Skill、⑤Tool/Hostで現在資格・Disclosure/Effectを独立検査、⑥実回答・結果をProductへ返し必要な根拠だけ再確認、である。

**別の選択軸**：開発向けModel→Role→Issue/PR dispatcher（[TEI #4218](https://github.com/hat47x/tei-platform/issues/4218)、Step Code/DSH等のWorkerを選ぶ）はProduct Skillの自動Routerではない。ユーザー向けHarnessはDSHだけに固定せず、実Skill Loader/Tool Profile/Session復帰の差は現在のHarnessごとに扱う。モデル名・料金・Skill説明は権限や実操作の証拠にならない。探索の自由を残し、Skill内では説明のために全Source/全参照を毎回ロードしない。

| 作業の実条件 | 選択候補 | 選択の停止線 |
| --- | --- | --- |
| 単一Productのread-only調査・索引、実Toolのみで十分 | Product Tool/CLIのみ（Skill不要でもよい） | Read範囲、実Version/Command、現在開示、Sourceの欠落を確認 |
| 専門手順・文書/モデルの診断・認知Methodに追加価値がある | そのProduct/CSWのSkillを**必要時だけ** | Skillファイルの存在≠Loader実Read/Tool実呼出、CSW案≠Source事実 |
| SUI→SHO・TEI→SHO等の出典・未決・Consumer受領をまたぐ | 実Product API＋必要なProduct Skills、条件付きTAI Activity Skill | Handoff受領≠Harness Live Session継続≠Authority/Owner受理 |
| EKIのTask/Attempt/Grant・Provider等に実Effectが関係 | 実EKI/Host Capability、明示Actionの前はread-only Preview | Skill/Task ACK/Receiptだけでは業務Effect成功・不存在を確定しない |
| 実Capability不在、現在Source/Scope/Read資格不明 | unsupported / unknown / not-runを正しく返す | 架空のTool/Skill/新Routerを生成せず、許可された独立作業のみ続ける |

### 47.2 2026-11-12に確認できる製品実績をSkillの案内へ接続

| 範囲 | 実際に確認できる限定Evidence | Skill/Harnessへ拡張できない結論 |
| --- | --- | --- |
| **TEI** | [Product Skill main](https://github.com/hat47x/tei-platform/blob/main/skills/yi-tei-modeling/SKILL.md)と実CLI read-only。外部DSH H3のSkill本文・参照実Readは[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)で限定観測 | H2/H3四Slot比較適格は**0/4**。OS実隔離/全送出/独立効果は未資格 |
| **SHO単独** | [SHO #30 merged](https://github.com/hat47x/sho-composer/pull/30)でRaw Draft保存/再開/競合、[read-only Product Skill main](https://github.com/hat47x/sho-composer/blob/main/skills/yi-sho-compose/SKILL.md)でResearch Index手順を提供 | SHO Skillが保存/編集/納品を実行可能と書き換えない。現在のSkill本文には旧「正式Writerなし」等の歴史記述が残るため[SHO #10](https://github.com/hat47x/sho-composer/issues/10) Ownerで実Product状況と分離して同期 |
| **TEI→SHO Draft** | [TEI #4317 merged](https://github.com/hat47x/tei-platform/pull/4317)、[SHO #36 merged](https://github.com/hat47x/sho-composer/pull/36)で限定モデル→文書Draft→著者編集/保存/再開。[TEI #4467 merged](https://github.com/hat47x/tei-platform/pull/4467)で再投影時の著者文保護・候補差分を整備 | GUI上の固定対象→HarnessからWriter→意味受理/正式納品が成立したわけではない。文書競合/Author ReviewはSHOが持つ |
| **SUI→SHO、TEI観測の引用** | [SHO #34 merged](https://github.com/hat47x/sho-composer/pull/34)と[#39 merged](https://github.com/hat47x/sho-composer/pull/39)、[TAIの実行票](cross-product-handoff-execution-tickets-2026-11-11.md)で実Producer/Consumer/TEI read-only引用、別Processでの実SHO Consumer再Readは限定PASS。一方、G5は**A=ローカルNode実Consumer／B=外部ARGVのReceipt形式JSON申告が一致**したのみ（[SHO main #47](https://github.com/hat47x/sho-composer/pull/47)、[TAI main #640](https://github.com/hat47x/tai-pleroma/pull/640)） | **Bが過去Receiptを再出力するだけでも一致した実負例あり**。B Consumer当該実行・Payload再Read・Replay排除はnot-proven。二Agent/同一Live Session・実Skill Load・現在Grant/全Sink Egressは未実証 |

**Handoffの既存正本を再利用**：[yi.handoff.context/v1計画](cross-product-handoff-context-v1-2026-11-11.md)とその[後続実行票](cross-product-handoff-execution-tickets-2026-11-11.md)。票を非信頼入力としてConsumerが実byte/digest/Sourceを独立再Readし、受領Receiptを意味受理や効果の承認へ昇格しない。Owner判断により**新しいv2/chainや中央Ledgerを先行追加しない**。元票の未知フィールドは消さず未知のまま保持し、Product Skill実Loadの有無をHandoff文面だけで「実証済み」としない。実施済みG2/G3等の限定PASSと、同じ実Harness Sessionの再開／外部OS送出／各Product GUI未実施を別票で管理する。

### 47.3 後続の受入ケース（既存TAI #488／#271に還元・全て新Trial NOT RUN）

| Case | 判別する負例 | Expected |
| --- | --- | --- |
| **YS-01** | 実Toolのみで十分な単独SHO/TEI調査なのにTAI Skill/他Productを強制Load | Product Tool-onlyで完結可能、過剰Tool/Token/準備負担を増やさない |
| **YS-02** | SHOのProduct Skillがread-only記述のままなのに、SHO Writer main統合を理由にSkillが自動Saveすると宣言 | ToolとSkillの実Capabilityを再発見し、read-only Skillの境界・対象/実CLI/Host Grantを保つ |
| **YS-03** | Handoff票の`productSkill`欄が存在する、あるいはUnknown欄が転送されたことをSkill実Load・受理の証拠へ昇格 | 実Loader read／Tool invocation／Consumer readbackを独立ログで確認。UnknownはUnknown |
| **YS-04** | 別Process再受領Receiptを同一Harness Live Sessionの復元成功と誤記 | 同一実Session ID/再開時のTool/Source資格が実証されない限り`not-run` |
| **YS-05** | SUI UIで動的検索QをPinした後、AIが追加A/除外Eを提案、実Source改版／RLS可視範囲変更 | [TAI Draft #629](https://github.com/hat47x/tai-pleroma/pull/629)の集合選択案は参照のみ。固定ID/動的Predicate、取得範囲、現在Source/Data/Grantを再Read。改版時の対象すり替えを防ぐ |
| **YS-06** | TEI→SHO再投影が著者の文章や引用Occurrenceを暗黙上書き | 元Source/文書Revision/明示Patchと差分・競合をProductへ返し、著者文の保全・採否をSHOで確認 |
| **YS-07** | CSWの探索案をSUI Canvasへ映したことから意味確定・Skill寄与を主張 | 手動KJ/一般AI/CSW Skill（別のMethod）とUI/Harness効果を別Armで評価し、反証/保留を保持 |
| **YS-08** | 匿名/期限切れ/部分SourceでもTool/Skill選択説明だけでEKI業務作用を許可 | Product/Hostの現在Grant・対象の一致・Receipt/独立Readを確認できないならActionを止める |

**順序・責務**：最優先の[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) H2/H3固定TEI read-only比較（G0実Read隔離、G1外部送出、G2 Tool Reply、独立4Slot）は変更しない。次に既存の実Handoff v1を使い、**固定対象→許可Projection→独立Consumer実Read**を**同じ公開Task/Source**で接続し、Tool-only／Product Skill／必要時TAI Skillを対照する。実製品UI・Canvas/CSW・別Harness Live Session・書込み/Effectは別Trial。実行・独立ExpectedはTAI #168/#271と各Product Owner、横断照合表だけTAI #488。Skill配布は#74。現在の追加部分は計画・実証資格の整理であり、独自Harness/中央Router・Policy Engine・第二Product Storeは作らない。

## 48. 2026-11-12：固定対象から実Product Handoffへ進む1往復の受入票

**統合判断**：本mainは[PR #628](https://github.com/hat47x/tai-pleroma/pull/628)の§46「一時Focus／Pinned Work Set／許可済Projection」と[merged PR #631](https://github.com/hat47x/tai-pleroma/pull/631)の§47「Tool-only→必要なProduct Skill→条件付きTAI Skill」の**採用済み計画**を持つ。本節は同内容を別§46として重複させず、[Draft #629](https://github.com/hat47x/tai-pleroma/pull/629)のQ/E/A・識別一意性、[本Draft #633](https://github.com/hat47x/tai-pleroma/pull/633)のProduct別再解決、既存[Handoff v1実行票](cross-product-handoff-execution-tickets-2026-11-11.md)を**一件の実行資格**へ接続する後続試験の優先順のみ追加する。

### 48.1 まず確認する唯一の実線：Product限定ContextのProducer→Consumer往復

**ユーザーJob**：許可済みのTEI 1 Subject（またはSHO 1選択範囲）をHeadlessで実Readし、用途・Source Revision・役割・開示Audienceを固定する。現Productの許可ProjectionからHandoff v1へ表せる範囲だけを既存Consumerへ渡し、**別Processで実Body/digestと受領Replyを再照合**する。返り値は元Productの現在のPin/Taskに「根拠付き候補」として関連付け、実Sourceへの書込みや正式Meaning受理をしない。GUI Pinが現行APIに無ければHeadlessの固定対象Refから開始し、GUI成功を装わない。SHOでは永続Occurrence IDを要求せず、原文Buffer/byte spanをSourceの現在値で再解決する。

| 実行順 | 参照する既存Owner/Capability | 必須の独立観測と停止条件 |
| --- | --- | --- |
| **R0：Productの現実** | TEI #1124/#1824/#3262、SHO #29/#30、SUI #3368 | 実Tool/Command、型付きTarget、Source/Buffer RevisionとRead Scopeを**コード/実Replyで確認**。未実装はunsupported。TEI同Kind同ID/CRUD脱落問題は[TEI #4475](https://github.com/hat47x/tei-platform/issues/4475)/[#4472](https://github.com/hat47x/tei-platform/issues/4472)へ返しIndex1件を一意性の証拠にしない |
| **R1：意図と現在対象** | main §46、TAI #629 §11.8.5、各Product UI | Focus≠Pin。ID/Origin/Source span/Rev/role、実解決集合とCoverageを対比。同名・多重Edge/異OccurrenceやRLS変更は曖昧・partialのまま停止。単一UI/CUIの実操作を初期実証にしてよい |
| **R2：Handoff実受領** | [SHO merged #34/#39](https://github.com/hat47x/sho-composer/pull/39)、[TEI merged #4317/#4467](https://github.com/hat47x/tei-platform/pull/4467)、[既存Handoff v1](cross-product-handoff-context-v1-2026-11-11.md) | Sourceで許されたProjection/digest/範囲だけ。実Producer→Consumerの独立Byte/Receipt/再Readは同一Attemptで評価。別Process受領やDeepSeek→Claude CodeのCLI引継ぎは、Live Harness同一Session復帰ではない |
| **R3：必要な能力の起動** | main §47、TAI #488、各Product Skill正本 | Tool-onlyで十分ならSkill/TAIを不必要に起動しない。必要なProduct Skillの実LoadとTool実Callを別々に記録。Product横断の継続が本当に必要な場合だけTAI Skill。Skill説明と現在CLI/Scopeが矛盾したら説明を優先せず再発見・保留 |
| **R4：UI/Harness戻り先** | TAI #271/#168、TEI #1824、SUI #3400、SHO #19 | Replyには実Task/Session/Source/Pin意図版と受信Contentを照合。二画面遅着やPin A→B→A、Audience/Grant変更で現UIを黙って上書きしない。Native Session attach非対応は別Session Handoffの結果に分類 |
| **R5：書込み/Effect（後続のみ）** | TEI ADR-0048、SHO Writer、EKI/Host | Proposal→Preview/独立再Read→現在Grant/Provider→実Receiptの順。Handoff ACK、Pin、Tool exit0、文書Draft保存は業務EffectやOwner意味受理の証拠ではない |

### 48.2 最小独立Expectedと費用比較

- **SR-01 一意性**：TEI同Kind同ID/同端点別Edge、SHO同文字列別Occurrenceを使い、現在Sourceで一意に選べないときに勝手に最初の1件を採らない。Product修正前は失格原因を対象のProvider/Index/Projectionへ帰属させる。
- **SR-02 保存と送出**：Pin意図が維持されても、追加した隠れたCard、未探索Relation、Reviewer Expected、Secret、旧RawはPrompt/Tool/Logに漏らさない。GitHubへのEvidence物理配置/Locatorも任意のlocal-only Profileに従う（TEI #4307）。
- **SR-03 HandoffとSession**：実Handoff v1 Reader/ReceiptがPASSしても外部Harness同Session継続はnot-run。Live attachの対応を別Probeで測り、非対応は明示Handoff縮退で区別。
- **SR-04 作業方法の比較**：同Task/Source/Target/開示制約で A=Product Tool-only、B=＋Product Skill、C=＋TAI Activity Skillを必要な場合のみ比較する。Skill文面・User Prompt・Harness/Modelを同時変更して因果効果を断定しない。正答/必要保留/対象誤指定/人間の再説明/実Tool数/Token/費用を区別し、AI OFF Productも維持。
- **SR-05 消失・古さ**：CUI→GUI切替、dirty Buffer、Source改版、二画面後着とRead-only Consumer欠落を注入。古い候補は履歴と再評価可能なRefを保持しても現在操作に自動適用しない。


### 48.3 現mainの実Receiptに基づく資格の再評価（11月12日）

[TAI main #632](https://github.com/hat47x/tai-pleroma/pull/632)の[Handoff実行票 §10](cross-product-handoff-execution-tickets-2026-11-11.md)は、意図・Pin（I）、実Product対象の再解決（R）、開示投影（P）、配送・Receipt（T）、Consumerの実利用資格（C）、Harness・Skill・Effect（H）を既存Owner別に評価する。この節では新Runner/Schemaを設けず、§48.1の手順がどの列を実測したかだけを記録する。

| 現在確認できる成果 | 成立する限定的な結果 | 未実証の資格 |
| --- | --- | --- |
| [SHO merged #45/#46/#47](https://github.com/hat47x/sho-composer/pull/47)、[TAI merged #635/#636/#638/#640](https://github.com/hat47x/tai-pleroma/pull/640) | G5のAローカルConsumer実呼出とB外部ARGVのReceipt JSON取得・照合。**Bが事前Receiptを再生しても一致する負例**をUbuntu/Windowsで確認 | B実Consumer呼出、今回のPayload再Read、Replay排除はnot-proven。実Agent/同一Live Session、現在Tool/Grant・全Sink送出・実Effectも未証明 |
| SHO #46のProducer Skill宣言引継ぎ試験 | Skill名を未知の付随情報として保持し、Consumerの権限・Writer結果に転用しない | 実HarnessによるSkill Loader Read、Tool Invocation、専門Skillの改善 |
| [SHO merged #48](https://github.com/hat47x/sho-composer/pull/48) | 同じMarkdown実byteを持つTEI Source A／別Source B／別Target IDの3票を実SHO Consumer/CLIが受領し、Payload SHA同一・independentReread=trueを確認。Ubuntu/Windows CI成功 | 元TEI WorkspaceのSource/TargetをSHOが独立再解決したわけではなく、originalSourcesRead=false／sourceRevisionCurrent=false／meaningAccepted=falseを維持 |
| [SHO merged #49](https://github.com/hat47x/sho-composer/pull/49)、[TAI merged #643](https://github.com/hat47x/tai-pleroma/pull/643) | 既存SUI→SHO RunnerのMachine Receiptで、TEI Catalogを**引用**した事実とSHOのPayload再Readを分離。SHO #49はexact HEADの全7 CI成功後にmain統合 | 同一NodeでのHarnessラベル変更を実二Agent・権限非増幅へ昇格しない。TEIの元SubjectをSHOが実Readしたか、実Host Grant・全送出は未実証 |
| [SHO #42](https://github.com/hat47x/sho-composer/pull/42)、[TAI #637](https://github.com/hat47x/tai-pleroma/pull/637) | Audienceを拡大した現在Ticketを実Consumerが再読取。自動権限継承は申告しない | 拡大先Recipientの実Host認可・拒否。縮小例G4-N2Rは別試験 |
| [TEI merged #4507](https://github.com/hat47x/tei-platform/pull/4507)／[merged #4524](https://github.com/hat47x/tei-platform/pull/4524) | Fingerprint非破壊・図NodeのAuthorityLimits保持に加え、三要素モデルの同Kind同ID重複をerror診断し、重複要素をIndexから除外。#4524 exact HEADのGo/Health CI成功を確認 | Derived CRUD/図/文書のすべてのConsumerがValidate結果を尊重する保証、Workspace/Occurrenceの現在再解決は別。Source-only drift [#4514](https://github.com/hat47x/tei-platform/pull/4514)・CRUDのData索引 [#4513](https://github.com/hat47x/tei-platform/pull/4513)はmain統合済み。明示CRUD-onlyの行脱落・未使用Data誤判定は[TEI merged #4551](https://github.com/hat47x/tei-platform/pull/4551)でmain修正済み（HEAD `e2066044`の初回8 CIは成功、merge `1a2271d8`）。派生Document/Studioの全Consumer受入やOwner意味受理は別。異Workspace/Subject Reader回帰 [#4504](https://github.com/hat47x/tei-platform/pull/4504)は別Draft |

**次の1件の実証**：既存[QH §10](cross-product-handoff-execution-tickets-2026-11-11.md)のRunnerをそのまま用いて公開TEI 1 Subject→SUI Handoff v1→SHO実Consumerを利用し、①Source/Workspace/Kind+ID・Revision、②Productで実Readした対象とConsumerで実際に再Readした対象、③Audience/Scopeと送出Body、④Tool/Skill実Loaderの有無、⑤最新Receiptの主張範囲を別列に残す。SHOが元TEI Subjectを再Readしていなければ、R/Cを未観測として保持しTの受領成功と混同しない。 [SHO #48](https://github.com/hat47x/sho-composer/pull/48)の3票を現在のQH-07の負例基線とし、Payload一致／票に記されたSource・Targetの違い／実Consumerが読んだ原Sourceを別観測にする。既存v1に必要な束縛が表現できない場合はGapをOwnerへ返し、新v2や第二Resolverを先に開発しない。

**独立負例**：同じSource位置でも異なるSubject、同じWorld Fingerprintでも異なるWorkspace、Producerが宣言したSkill名と実Loadの不一致、Audience拡大のHost認可未確認、外部Nodeの起動を実Agent Sessionと誤称、実ConsumerがしていないTEI再Readの成功表示。正しく未資格と停止することも合格対象とする。

**優先順位**：QH-P0は実Product側のread-only試験として並行できるが、[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)のG0実OS Read拒否→G1送出→G2完全Tool Reply→新H2/H3独立4 Slot（比較適格0/4）の追加条件としない。二製品GUI固定Pin、実Agent Live Session、CSW方法の寄与、実Provider EffectはNOT RUN。新中央Runtime/Policy/Storeは追加しない。

**着手順**：最初の[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) G0実OS Read-deny→G1送出→G2完全Tool Reply→新独立H2→H3→H3→H2（適格0/4）のBlockingは**変更しない**。その後の最小Product横断はR0→R1→R2（read-only）であり、実UI Pinned Context・Live Session・CSW Canvas・EKI Effectの実試験は段階的に分離。各Product Ownerの独立Expected/Scenarioを利用し、新共通Selection ABI、中央Handoff v2/Registry/Runnerや既存Productの意味受理正本を作らない。

**資格**：main統合済みSHO/TEIの限定Handoff/文書Draftは実績だが、ここに示す**Pin→Handoff→Harness→Product UI一往復、Tool-only/Product Skill/TAI Skillの比較、実Live Session attach、横断Owner受理はNOT RUN**。本節は実行手順候補とOwner接続の追加である。

### 48.4 実Receipt再生と同内容別Workspaceの対象再確認（11月12日）

[SHO main #47](https://github.com/hat47x/sho-composer/pull/47)のG5-N5は、B側で当該AttemptのConsumerを起動せず、事前作成Receipt JSONを再出力するだけでも一致する負例を実Runner/Ubuntu・Windows CIで示した。[TAI main #640](https://github.com/hat47x/tai-pleroma/pull/640)のG5-N5/QH-08も、この範囲の成功に主張を限定している。**旧G5の履歴Receiptを消さず**、現在の実証は「A実Consumerの応答とB外部ARGVが申告したJSONの整合」までとする。

[TEI Draft #4504](https://github.com/hat47x/tei-platform/pull/4504)と[Workbench Owner #4515](https://github.com/hat47x/tei-platform/issues/4515)では、完全に同じManifest/Sourceを別Workspace Rootへ複製すると、Workspace Name/Manifest SHA/Kind・ID/Canonical/World/SourceIndex/Model Fingerprintが**すべて同じ**になっても、利用者がPinしたWorkspaceは別であると対照した。PinはProduct内部でユーザーが選んだ**WorkspaceRef/root**とQualified Subjectを保持し、別Rootへ無言で再束縛しない。Rootの現在の許可や実Host Grantも再確認が必要で、Raw path/機微情報を外部Harnessへそのまま送らない。TEI #4504は未マージDraftであり、実Studio固定PinやHarness送出を実証していない。

| 判別対象 | 最小限必要な独立観測 | 認定してはならないもの |
| --- | --- | --- |
| I/R 対象選択・再Read | ユーザーのWorkspaceRef/root、Qualified Kind・ID、Source/Scope/Revision/Occurrence、候補一意性 | 別Root同内容・同offset別Subject・同Kind同IDのHash一致だけから同一編集対象と推論 |
| T 配送 | 実Ticket byte、許可Audience、外部ARGVからのJSONと申告Digest/byte数 | JSON一致をB実Consumer起動・今回のTool Deliveryと認定 |
| C Consumer実利用 | 当該Attemptにおける実Consumer自身のSource Open/Read Closureと実Target・Revisionの照合 | 過去Receipt、申告Nonce/日時、外部exit0、モデル発話だけで現在Reader資格を認定 |
| H Agent/Effect | 実Harness Session、Tool/Skill Loader・Invoke/全Reply、Host Grant/OS送出・Effectの各独立観測 | A/BのLabel、Receipt一致で二Agent・同一Session・送出安全を認定 |

**次の検証**：①[TEI #4504](https://github.com/hat47x/tei-platform/pull/4504)の同Root正例／別Root同内容負例／同offset別Subjectはexact HEADの全11 CI成功・Draft未マージと区別してProduct Readerで観測、②既存G5-N5を実Consumer未実行でもJSON一致する対照として再利用、③実Consumerの当該Attempt再Readを独立に観測できない場合はC=not-provenを維持、④実外部Agent Tool経路とG0/G1/G2はTAI #168の別Gate。Receiptの自己申告時刻・Nonceを加えるだけで実実行/Replay除去が証明されたとは言わず、新Attester/中央ID Store/Handoff v2/Runnerを導入しない。

**資格**：SHO #47のReplay負例、#48の同一Payload異Source/Target受領負例と各CIは限定PASS。TEI #4524はmain修正済み、#4504はCI成功のDraft、B Consumerの当該再Read・実Agent/Live Session・現在Host Grant・GUI Pin→Harness→Product UI復帰、QH-P0新TrialはNOT RUN/not-proven。Product局所試行はTAI #168の固定H2/H3初回4 Slot（比較適格0/4）の追加Blockingではない。

### 48.5 Pinを持つAI変更提案から、Modeler／DBの明示操作へ進む条件

**接続する他レーンの判断**：[TEI 三要素モデル Draft #4478 §27/§28](https://github.com/hat47x/tei-platform/pull/4478)、[Studio実装Owner #4515](https://github.com/hat47x/tei-platform/issues/4515)、[REA横断 Draft #4508](https://github.com/hat47x/tei-platform/pull/4508)、[組織モデリング Draft #4500](https://github.com/hat47x/tei-platform/pull/4500)が共通して区別したのは、画面上の項目、TEIのData/Function/Business各モデルにある意味要素、Declared/Desired Source、実DBのObserved Schema、実Migration/Host Effectである。AIがUI上のPinから「この項目を追加・削除」と答えても、どのレベルへの提案かを**Product側で再解決してから**適用候補にする。YICはこの業務意味やTable Writerを新たに定義せず、既存ProductのOperation/Previewに案内する。

| 作業対象・変更指示 | Pinから先に確認すること | 禁止する暗黙操作 |
| --- | --- | --- |
| UI Widgetを1件追加・配置変更 | UI Occurrenceと対応するMapping、未結合なら未結合と表示 | UI要素の作成をTable Column生成・実DB DDL・Accepted Meaningの自動変更にしない |
| 既存TableのFieldを削除・改名 | Declared Sourceの現Revision、Data Model/CRUD/Query/Rule/画面の被参照、部分取得か全量か | 画面Widgetを無断削除、同名別Fieldへ自動結合、依存未観測を「影響なし」、実DB Applyを完了扱いしない |
| Raw DBでColumnが増減して見える | Observed DB SchemaとDesired/Declaredの差、接続先/Scope、現在取得の完全性 | 観測差や権限不足からTEI Sourceを書換えず、部分取得や不可視をColumn不存在にしない |
| AIが構造化Patchを提案 | 元のWorkspaceRef/root、Qualified Target、Source Revision、写像の解決、Proposalの目的と差分 | Pin/Prompt承認だけでHost Grant、Source Commit、Migration実行、Business Effectを認定しない |
| 三要素分析法のModel/図・CRUDを選択 | 原典のデータモデル・機能モデル・業務モデルと正式なSource上のRelationを確認 | 描画用parent Edgeや汎用Roleだけで原典のモデル/業務Flow/Relation意味が確定したとしない |

**R5の最小負例を既存Ownerで検収する**：
- **YIC-UI-01**（[TEI DMU-01](https://github.com/hat47x/tei-platform/pull/4478)）：AIが「画面へ項目追加」を提案し人がUI操作だけ選んだ場合、UI Occurrence +1／Declared Column +0／実DB Apply 0。別途「列を作り関連付ける」と明示した操作は別Proposal・影響Previewを要する。
- **YIC-UI-02**（DMU-03/04/07）：Field Cを参照する画面2件でDeclared Field Cを削除。UI2件は残すが、有効Mapping 0・警告2・旧CへのWrite 0。Query/Rule/CRUDの依存が部分取得ならunknownを残す。
- **YIC-UI-03**（[PIN-S0-02/03/04](https://github.com/hat47x/tei-platform/issues/4515)）：別Rootに複製した同Manifest/同Source、A→B→A、描画用のparent Edgeを混在。元Pin Intentは保持しても別Workspace/別Column/別Relationへ無音Rebind 0。実Source/Host資格を再Readできなければ送出とApplyを停止。
- **YIC-UI-04**：AIが元Source上の実ColumnやAuthoritative Tableの変更を示唆しても、UI/モデルSourceのPreview→選ばれた明示Patch→実保存Receipt→必要時DB Migration Plan/Apply/Readbackを別々に記録。ローカルUndoと実DBロールバックは同一視しない。

**最初の実装を肥大化させない**：TEI [#4515](https://github.com/hat47x/tei-platform/issues/4515)は現Workbenchの既存Inspectに対する**read-only Subject Pin**だけを先行し、同IssueへTable/Widget/Schema Writer・Relation Pinを持ち込まない。UI/Mapping/Schemaの負例実装は[#1124](https://github.com/hat47x/tei-platform/issues/1124)、[#1143](https://github.com/hat47x/tei-platform/issues/1143)、[#4478](https://github.com/hat47x/tei-platform/pull/4478)、[#4125](https://github.com/hat47x/tei-platform/issues/4125)、[#2514](https://github.com/hat47x/tei-platform/issues/2514)の既存Source/Expectedを参照し、適格になってからR5へ渡す。通常の開発相当の意味確認で足りる場合に新Owner承認Engineを要求しない。OKF等による出典/版管理は任意の既存手段とする。

**参照・被参照を用いた作業対象の確認**：通常Editor/Workbenchの参照移動・逆参照・未使用候補の受入Ownerは[TEI Issue #3788](https://github.com/hat47x/tei-platform/issues/3788)と[#1124](https://github.com/hat47x/tei-platform/issues/1124)。Script/Entry公開とDSL近傍直接テストを結び付ける設計は[新Draft #4543](https://github.com/hat47x/tei-platform/pull/4543)に移管済みで、旧[Draft #4525](https://github.com/hat47x/tei-platform/pull/4525)は**差分0でクローズ・未統合**。現在の主張はScript/Entry/TriggerやModelerの参照元への移動、参照数0の候補表示、同じ対象への戻り操作の**計画**に留まり、実Workbenchの横断動作や現在のFunction起動資格を証明しない。ただし参照数0は**調査できたSource/Plugin/Role/Consumer範囲内の0件**に限り、未読込・動的参照・部分取得・非開示があれば`partial/unknown`を維持する。選択時は元のQualified Target/Source Revision/WorkspaceRefを保持し、索引結果を実Read/現在Grant/Source Writerの証拠にしない。参照逆引き・Keyboard操作・Plugin非干渉の性能計測はTEI #1124/#4515/Script Launch既存Ownerの次段であり、**QH-P0やTAI #168初回Gateには追加しない**。

**現在資格**：本節は他レーンの**Draft設計と後段受入条件の接続のみ**。Workbench実Pin、DMU-01〜15、DB Apply、Host Effect、AI変更提案の実Product再現、外部Harness→GUI→DBのE2EはNOT RUN。先行R0〜R2のread-only／TAI #168の実OS G0→G2・独立H2/H3 4 Slot（比較適格0/4）には追加Hard Gateを設けない。

### 48.6 Productの現在資格を、局所的な必要条件と実Readで判定する（11月12日夜）

**成熟した実装結果を再利用する**：[TEI merged #4530](https://github.com/hat47x/tei-platform/pull/4530)は、独立した変更・問いと無関係なunknownを全体失効へ拡大しない修正を限定Referenceへ実装した。Required（今回の問いに必要な対象）とChanged（変更元から到達する依存経路）を区別し、関係する未解決端点はunknownのまま残す。**関連するunknownを見逃さないことと、無関係なunknownで全Productの読取を停止しないことの両立**が重要。#4530は合成Referenceの局所修正で、実Provider/外部Disclosureの認証ではない。

**実データは別の資格**：[TEI merged #4539](https://github.com/hat47x/tei-platform/pull/4539)では、公開ReferenceのFunction `order_entry.recent_orders` を、Environment→一意のDB Instance/Provider→実PostgreSQL 16.15→Raw Rows→Function Data Context→別プロセスの `tools/reference-browse-read` まで到達させた実試験が記録された。0行・RLS・JOINでの重複・NULL・列権限・別DBによる行変化も独立Expectedと照合済み。**PR #4539の最新HEAD `ece566af`に対応するRepository Healthなど7ワークフローはcompleted/success**と再確認した。main統合（merge `ee1af44c`）後も**正式な製品 `tei` CLIには未接続**であり、Reader自身が正しく取得した行と「許可対象の全行」「元Sourceが現在」「Host Disclosureが許可」「SHO/TAIで受領した」を区別する。特に `coverage=unestablished`／`EmptyJustified=false`／`visibility=unobserved` を省略しない。

**CRUDの構造OKとレビュー**：[TAI main QH §10.6](cross-product-handoff-execution-tickets-2026-11-11.md)を唯一のQH検収正本とする。[TEI merged #4534](https://github.com/hat47x/tei-platform/pull/4534)のmain実装では、矛盾CRUDを無条件hard errorにする初回案を撤回し、`okScope=structural-diagnostics-only` と `crudConflictStatus=conflicts-require-review` を分離する。矛盾のあるモデルはread-onlyで表示・診断可能にしても、モデルの構造 `OK=true`、CRUD投影の生成、変更適用許可を同一視しない。Severityと業務意味はTEI Ownerが判断する。矛盾全件収集とCLI表示の実装は、旧HEAD `15eb15d7`のgofmt失敗を[コミット `bd9d2512`](https://github.com/hat47x/tei-platform/commit/bd9d2512d73a558d1bcd28cf6eb3205fb7b4a665)で修正後、当該HEADの8本のGitHub Actionsが**すべてcompleted/success**。その後[PR #4534](https://github.com/hat47x/tei-platform/pull/4534)はmainへ統合された（merge `5f35d5dc`）。**限定的なモデル診断/CLI出力の実績**であり、CRUDに矛盾がある時の実Writer停止、全派生図面、正式Owner意味受理、Source/Host Grantを保証しない。矛盾SeverityはOwner保留のまま。

| 最小判別 | 利用者への正しい挙動 | Owner／結果の現在地 |
| --- | --- | --- |
| Required外の無関係なunknownが残る | その問いで確認できたread-only調査を継続し、全作業を一律失効させない | TEI #4530は限定main修正。実Product/Disclosureは別 |
| Requiredまたは変更経路に未解決端点がある | 関係する選択・AI送信・Applyだけを再確認し、未観測を「未使用・0件・変更影響なし」にしない | TEI #3262/#2516、TAI #271の現在資格 |
| 一意のFunction/Sourceだが、DBで0行／RLS／Masked NULL | 観測したConnection/SQL/Scopeでの結果だけを説明し、全体不存在や完備を主張しない | TEI #4539の独立実PG試験はmain統合済み。正式CLI・二Product ConsumerはNOT RUN |
| 構造OKだが矛盾CRUDが残る | 診断閲覧と固定Intentは維持可能。適用候補は現在のSource/Meaning/レビュー・Host Grantの確認まで保留 | TEI #4534のモデル/CLIはmain統合済み。派生ConsumerのApply資格は別、QH §10.6はTAI main |
| SUI→SHOのReceiverがTEI Catalogを引用しただけ | Handoffの実受領(T)を限定表示し、元TEI Subject再Read(R/C)や実Agent(H)を未実施と表示 | SHO #49／TAI #643はmain。QH-P0新3製品実試行はNOT RUN |

**生成AIによるGenerator生成との接続（新P0 Gateにしない）**：生成時DSL・案件の変換工程は[TEI #1063](https://github.com/hat47x/tei-platform/issues/1063#issuecomment-6837967224)、**Generator自身のG1生成規約→G3独立Conformance→G2合成・選抜の実証Ownerは[TEI #4544](https://github.com/hat47x/tei-platform/issues/4544)**とする。既存`reference-generator-selection`の候補生成・Source snapshot・meta depth-1を再利用し、標準Generatorを優先する。[自己記述Draft #4541](https://github.com/hat47x/tei-platform/pull/4541)はRole/意味の入力条件、[Script Launch Draft #4543](https://github.com/hat47x/tei-platform/pull/4543)はEntry/実Target起動への下流条件のみを担う。別チャットですでにG1実装委任中のため、TAIで二重起票しない。**Tool/Generatorが実在することと、そのProduct Skillが実Loaderで使われたこと、現在のModel/Hostを変更する資格は別**。実Go Generator・生成AIへの委任・Plugin ABIは未検証であり、TAIは結果を運ぶ場合もTEIのBuilder/Conformance/Source/Owner判断を再定義しない。最初のHarness H2/H3・QH-P0を新Generator開発の待ちにしない。

**DesktopセルフビルドとHandoffの並行接続**：[TEI #1824](https://github.com/hat47x/tei-platform/issues/1824)／[#3421](https://github.com/hat47x/tei-platform/issues/3421)のStudio Desktopと[#2831](https://github.com/hat47x/tei-platform/issues/2831)のセルフビルドをProduct側の最優先実装とする。他チャットで整理されたS0〜S4（現行Studio/共通APIの起動基線→Build定義と実入力閉包→Stage1の実Artifact→**Stage1自身の実ProcessがStage2 Buildへ再入**→実Desktop操作と再現性）を既存Ownerの受入へ参照接続する。単なるGo二回Build、Stage1/2 digest一致、TEI Reference Generatorの成功を**TEI自身によるセルフビルド成立**とは扱わない。X-TEA三要素分析法（データモデル／機能モデル／業務モデル）のDesktop Plugin移管は[#1124](https://github.com/hat47x/tei-platform/issues/1124)の原典準拠モデル／Cross Referenceを守り、この縦断へ段階接続する。TAIが関与するのは、後でProductが確定したSubject/操作のread-only Projectionを外部Harnessへ渡す部分だけ。Studioの実起動・Buildの新試験・X-TEA Pluginの移管完了は、本節では**NOT RUN**。

**次の実装の優先順位**：TAIが第二のReader/Query/CRUD Judgeを作らず、(a) TEIの実Product Reader／Studio #4515、(b) SUI #3438の現在Source再読込、(c) SHOの実Consumer、(d) TAI #168の外部Harness G0→G2を独立に前進させる。各Productで独立Expectedと実Version/Attempt/Read Closureが得られて初めて既存QH §10のR/C/Hを実証する。未接続なら `not-run/unsupported/partial` を残し、回避のためにRaw Sourceを外部Agentへ一括送出しない。新しいHandoff v2・中央Registry・Agent Loop・一律の新Hard Gateは追加しない。

### 48.7 2026-11-13：実装済みの対象確認と、まだ接続していないUI・Buildを区別する

<!-- yic-48-7-exact-ci-and-product-requalification-20261113 -->

この追補は、§48.1のR0〜R2を**既存Productの実Readerで一件通す**ための最新基線である。各製品の実装Ownerと、#1180/#2514の独立Expected、QH §10の実行票を維持する。TEI Studio Desktopの再構築を最優先とし、TAIの追加Harness機構をその先行条件にはしない。

| 接続点 | 確認した実装・検証 | 現時点では主張しないこと／次に検証すること |
| --- | --- | --- |
| **R0：Subjectの存在** | [TEI #4584](https://github.com/hat47x/tei-platform/pull/4584)は**main統合済み**。source-indexのsubjectモードは、Canonical Subjectが存在しなければ空配列の成功にせず、既存Inspectを用いてSUBJECT_NOT_FOUND等を区別する。HEAD dcfe1d69の対象8 CIはsuccess | references:[]は、存在するSubjectの参照0件かどうかを**実Subject確認と組み合わせて**判断する。Source一意性・現在Root/Scope・外部送出Grantまでは自動で得られない |
| **R1：固定意図の状態** | [TEI Draft #4597](https://github.com/hat47x/tei-platform/pull/4597) HEAD 247a6baの[Pin専用CI #43394212153](https://github.com/hat47x/tei-platform/actions/runs/43394212153)はsuccess。Pin/Unpin/Undo、世代とWorkspace A→B→Aに対する局所状態遷移を検査 | 同HEADの[Workbench embed CI #43394213664](https://github.com/hat47x/tei-platform/actions/runs/43394213664)はfailure。Pinは実main.ts・Inspector/Graph/AI送信へ未配線。専用CI成功をNative UI/配布済みBundleの資格にしない |
| **Desktopへの読取部品** | [TEI Draft #4587](https://github.com/hat47x/tei-platform/pull/4587) HEAD d7ad13ceの[Windows Run #43388804188](https://github.com/hat47x/tei-platform/actions/runs/43388804188)でN0〜N3の**指定ファイル**のSHA目録、生成/通常WebView2、実配信JS照合が限定success。次HEAD 7babc6adは**その実生成TSをWorkbenchがesbuildで読む入力位置へ配置**し、[Windows CI #43394244960](https://github.com/hat47x/tei-platform/actions/runs/43394244960)で生成/通常WebView2 Jobともcompleted/success | 目録は工程後のファイル再読取を含み、qualifiedBuildIntent=false／dependencyClosure=unknown。実生成TSの入力配置は当該CIで限定PASS。ただしBuildIntent全工程実駆動B1-B、Stage1→Stage2 Desktop B2、Stage2実WebView2 B3は[TEI #4583](https://github.com/hat47x/tei-platform/issues/4583)で別実証 |
| **X-TEAの三要素分析法** | [TEI Draft #4570](https://github.com/hat47x/tei-platform/pull/4570)は通常Studio Hostと同じBridgeを使うread-only三視点Pluginを実装し、WSL/serverのGo/Node/ブラウザによる限定ローカル試験成功を報告 | 同PR exact HEADのRepository Health/Studio Wails Host CIはfailure、Native Windowsの通常/生成Studio両版での実Plugin呼出し、原典Sourceの再読取、Stage2実収録は未検証。[#4601](https://github.com/hat47x/tei-platform/pull/4601)のRuntime Role整理はdocs-only。X-TEA全機能をB1-Bの必須Gateにしない |

**まず実行する最小往復**：現在のWorkspaceと一意なSubjectをinspectで確認し、source-indexで参照を調べ、現在Source Revision/Scopeとともにread-only Projectionを作る。そこから既存Handoff v1→実SHO Consumerまで**当該Attemptで再Readした内容**を照合する。不存在の旧ID、同Byte別Workspace Root、後着Reply、Pin A→B→Aを個別の拒否対照にする。Pin状態遷移テストの成功だけで、この製品横断経路が実行済みとはしない。送出・実Consumer・Host Grantは各Ownerで別確認し、秘密のRaw Rootを外部へ渡さない。

**BuilderとAIの判断境界**：N0の生成物がN2にインストールされたこと、N3 exeがWebView2で起動したこと、Product Skillが実Loaderで使われたことは、それぞれ別の観測である。Build ArtifactやHandoff票のHash、Skill名、AIによる「確認済み」という発話を現在のProduct Subject・受理済みMeaning・実Tool送出の代わりにしない。TAI #488の中断後の別Session比較（Tool-only／Product Skill／TAI Skill）はこの再資格化が実際に行われたかを測り、独立H2/H3四Slotの成功数へ転用しない。

**進捗区分**：上表は各PRの限定実験とmain統合状態の照合であり、**本節のTEI→SHO新往復、実UI Pin、B1-B〜B3、外部Harness OS G0〜G2、H2/H3はNOT RUN**。追加Runner、中央Registry、Handoff v2、第二Meaning/Expected正本は設けない。

### 48.8 2026-11-14：実TEI起動が加わった現在の受入境界と横断実行順

<!-- yic-20261114-real-pr-head-n0-crosslane-qualification -->

§48.7は11月13日時点のSnapshotとして維持する。以降のPR／CIで進んだ事実を**同じHeadの現在実装と誤認せず**更新する。TEI Studio DesktopをTEI自身でセルフビルドする目標は不変。横断HarnessとSUIの機能をその前提条件に追加しない。

| 接続先 | 最新の確認済み範囲 | 次の停止線・実装Owner |
| --- | --- | --- |
| **TEI N0→N3 Windows** | [TEI Draft #4587](https://github.com/hat47x/tei-platform/pull/4587) exact HEAD `24bfaed8fadcce5687fb7f02a121a21fd70f2861`／[Windows CI #43450255223](https://github.com/hat47x/tei-platform/actions/runs/43450255223)は生成版・通常版WebView2 Jobを含む**同Head 7 Workflow成功**。TEI通常CLI自身が`self-build -child/-child-arg-file/-artifact`でN0生成器の実Processを起動。親子image SHA・実argv・exit・子の報告とディスク再読TS byteを照合、二重生成no-clobber拒否も実施。N0実出力をN2 esbuild選択入力へ渡し、N2 **24件**、N3 Go選択**303件**、native exe SHA `f7acb50feb74f9e93afe61ff60fc14718b5ffaf7cf6a88c38f837a6a8f757209`、実WebView2配信JS SHA `755e5e85f8487d4e5361fe4262c77595c3ebc048068f2647b0b27862de804299`を一Jobで確認 | **N0はprimitive `-child`起動**。Builder Catalog/BuildIntent選択なし、TEI CLIは通常`go build`版、N1〜N3の起動者はCI Workflow。`qualifiedBuildIntent=false`／`dependencyClosure=unknown`。既存[TEI #4583](https://github.com/hat47x/tei-platform/issues/4583) B1-Bで選択Builder→実Invoker→Artifact、次B2実Stage1→Stage2 Windows、B3そのStage2実WebView2を別検収 |
| **X-TEA三要素モデル** | [TEI Draft #4570](https://github.com/hat47x/tei-platform/pull/4570)は合成Workspaceの三視点/CRUD/Sourceへの移動・固定意図保持を**実Windows WebView2**で限定確認（[CI #43419938104](https://github.com/hat47x/tei-platform/actions/runs/43419938104)）。`tei-studio -three-view` Headlessも同一Bridgeで実呼出し | 人によるDesktop受入、原典`.xead/.xeaf`、正式`tei` CLI入口、Pin保存、Profileに沿うPlugin選択/収録は[TEI #4611〜#4615](https://github.com/hat47x/tei-platform/issues/4611)等へ。Studio B1のHard Gateにしない |
| **Rawから独立Recipientへの資格** | [TEI Registry Draft #4617](https://github.com/hat47x/tei-platform/pull/4617)の[CI #43438531175](https://github.com/hat47x/tei-platform/actions/runs/43438531175)では別Node OS Processがlocalhost HTTPで未信頼signed Releaseを取得し独立検証、Required Memberの実byteを別GET。正常1・拒否9成功 | 固定テスト鍵・同一マシンのReference。実配布/現在Publisher Trust・Origin・失効・Plugin実Load、TAIのHandoff受領資格へ昇格しない。TEI #2589がOwner |
| **現在Product Context** | [TEI #4616](https://github.com/hat47x/tei-platform/pull/4616)のexact HEAD `80bf742`は同Source/Model Revisionで**宣言済Rootの実在だけが変わるとValidation結果が変わる**回帰試験を[CI #43441013751](https://github.com/hat47x/tei-platform/actions/runs/43441013751)等で成功。#4584の不存在Subjectと参照0件の区別はmainに統合済 | Source byteやModel Revision同値で現在Root/Validation・Scope/Grantを省略しない。TEI #4515のPinとTAI Product Handoffの再Readで確認。GUI自動検知・実開示/送出は未証明 |

**実装の接続順を三系統へ分ける。** (1) **Build**：TEI #4583のB1-B（N0 primitiveから正式Catalog/Intent実選択へ）→N2/N3の各Invoker/Artifactを同一Attemptで束縛→B2→B3。(2) **Harness**：[TAI Draft #648](https://github.com/hat47x/tai-pleroma/pull/648)のProduct-only→限定Activity Handoff→Native Transcript閲覧→実Turn操作→Product候補Applyを別段階で検証。Activityの受領をTranscript閲覧資格、UI局所操作の排他をHostの実同時実行保証と呼ばない。既存TAI #234/#271、#168 G0/G1/G2→H2/H3適格4 Slot（**0/4**）を維持。(3) **情報統合**：[SUI Draft #3442](https://github.com/hat47x/sui-sensemaking/pull/3442)のIG0 AI OFF→IG1 Raw→Card→別Process/Browser原文復帰→IG2二資料照合→IG5 SHO等RecipientのLoss付き受領を既存Ownerで順に検収。SUI Cardの表示だけでRaw再取得・Meaning/Permission・SHO実受領を合格にしない。

**横断で共有するのは採点原則だけ**：Build Attempt（実Builder/Output）、Product Context（Workspace/Qualified Subject/Source Revision/Root/現在Disclosure）、Harness Session（Activity/Turn/Transcript）、SUI Raw→Occurrence→Card/SHO Draftを一つのAuthority・継続Session・汎用`verified`状態にしない。既存Handoff v1の許可済Projectionだけを渡し、別Recipientは当該Read/受領を独立確認する。新Handoff v2/Host/Runner/Lock/Selection Registry/Meaning正本を追加しない。

**最小反証の持帰り先**：N0が正しいTSを生成してもCatalogから実Builderが選ばれていなければB1-B合格0（TEI #4583 BD-13）。Activityだけ届いてTranscriptが取得できなければNative Session閲覧合格0（TAI #234）。同じRaw digestでRootだけ変化した場合は旧Validation/Pin利用資格を復元しない（TEI #4616/#4515）。SUI Cardが描画されても元Rawへ別Processで戻れなければIG1未達（SUI #3442）。これらは各Ownerの独立Expectedを使用し、**新たな横断E2E試験は本追補ではNOT RUN**。

**この節の限界**：既存CIと他のDraftの証拠を照合したdocs更新のみ。TEI BuildIntent B1-B/B2/B3、外部HarnessのOS境界と同一Session多UI、SUI IG1製品E2E、SHO独立Writer、Current Grant/Owner意味受理は未実施。#4587、#4570、#4617、TAI #648、SUI #3442の個別CI/契約を本TAI Draftの製品適合へ加算しない。

### 48.9 2026-11-14：Builderの起動前同一性検査を、Catalogによる正式選択と分ける

<!-- yic-20261114-builder-pin-qualified-exact-head-8of8 -->

**新たに成立した限定実装**：[TEIセルフビルド共有CLI Draft #4623](https://github.com/hat47x/tei-platform/pull/4623) exact HEAD `929fcf857cd0f6a792a69fb23cadfb5eccc05e90`で、既存`tei self-build -child`のCallerに`-expected-child-digest sha256:<64 lowercase hex>`を許容し、実子ファイルのSHA-256が違えば`exec.Command/Start`前に停止する。明示pinが一致したときだけ`selectedChildDigest/childPinChecked/childPinMatched`をReceiptに記録。元mainのOS境界`selfBuildBoundary`／`driveSelfBuildIn`を維持し、不正pin／選択B→実A／Launcher経由の拒否・一致pinでも虚偽Artifact digestを合格にしないGo回帰を加えた。差分2ファイル。**[Self-build CI #43537292107](https://github.com/hat47x/tei-platform/actions/runs/43537292107)と[Repository Health #43537292191](https://github.com/hat47x/tei-platform/actions/runs/43537292191)を含む同HEAD 8/8 Workflowがcompleted/success**。

| 独立する資格 | 今の到達点 | 次の未成立Edge |
| --- | --- | --- |
| **Caller pinの起動前照合** | #4623／HEAD `929fcf85`のGo/CLI回帰とSelf-build／Health含む8 CI success。実Childが選択SHAと異なればChild起動と出力作成を禁止 | Callerの選択文字列自体が現在Authorized Builderであること、OS Loaderが開いた同一byte、full dependency closureは未資格 |
| **正式Builder選択→実Child** | #4623の**新HEAD `f1e219a25976946bcc8a19ef57f5490333ec8a84`に実装候補が追加**：opt-in `-bind-resolved-builder`（`-build-catalog/-build-catalog-digest/-build-source-root`必須）でin-process Resolveの`PlanReceipt`を検証し、`Plan.Builder.ArtifactDigest`を起動前Child Pinへ渡す。一致／選択B→実Aの拒否／CatalogなしBindingの拒否Goテストを追加。**このHEADの全CIはまだ未確定** | 旧`929fcf85`の8/8成功は**pin primitiveだけのHEAD**。新HEADのResolver接合、Product Windows N0、非Plugin Desktopを同等PASSとしない。最新HEADの自動CI・意図した契約/Target/実image/argvの同一Attemptを要検収。次Owner [TEI #4583](https://github.com/hat47x/tei-platform/issues/4583)／#2831 |
| **N0→Windows Consumer** | [TEI #4587](https://github.com/hat47x/tei-platform/pull/4587)のpin追加前HEAD `24bfaed8`でTEI CLI実N0 Child→esbuild→Wails→Windows実WebView2が[CI #43450255223](https://github.com/hat47x/tei-platform/actions/runs/43450255223)成功 | #4587の新pin追加HEAD `12bd80bf03f24092f7947e0c9395dada552a3cbc`は**mainと競合（mergeable=false）**し、当該HEADのWindows Workflowはこの確認時点で未観測。#4623のGo 8/8と#4587旧Windows Greenを合算して新pinのWindows PASSとしない |
| **非Plugin Desktop/多工程セルフビルド** | `go-command` Source分岐はあるが`BuildIntent.Validate`は`plugin` Subject限定、出力`plugin.BuildPlan`にもPlugin IDがある | Desktop.exeをPluginへ偽装せず#1080/#1097のBuildExecution/ArtifactSetと実N2/N3 Target Adapterを薄く接続→B2 Stage1自身のStage2 Windows Desktop Build→B3当該Stage2実WebView2。**NOT RUN** |

<!-- yic-20261114-resolver-to-child-optin-candidate-f1e219 -->
**最新HEADの差分と検収上限**：[TEI Draft #4623](https://github.com/hat47x/tei-platform/pull/4623)は先の`929fcf85`から2コミット進んだ`f1e219a25976946bcc8a19ef57f5490333ec8a84`に、`cli_self_build_outer.go`と`cli_self_build_resolved_builder_test.go`を追加。`-bind-resolved-builder`は**in-process Builder Catalog／BuildIntent解決が成功した場合だけ**選択digestを供給し、Plan Fingerprintとの一致を検査してから`driveSelfBuild`へ渡す。違えば`SELF_BUILD_BUILDER_SELECTION_MISMATCH`としてChildRunを生じさせず拒否する。テストは固定Fixtureの選択一致/不一致/解決経路なし拒否を対象とし、正式non-plugin Desktopを扱った実証ではない。**新HEAD CIは確認時点で8件中6件success、Self-build実証・Repository Healthの2件がin_progress**。結果未確定の2件をPASSに数えず、旧HEADの8/8と合算しない。Windows Draft #4587の新pin適用は依然CI未観測／競合あり。
**採用条件の追加圧力**：Callerの明示pinが成功しても、同内容別Provider ID／Authorityの混同、Expected Builder Bなのに別Artifact Pinを渡す混同、検査後OS LoaderまでのPath差替え（TOCTOU/ABA）、N2の実JSとN3のEmbed違い、別HEADの成功合算を拒否する。独立Expectedは#4583 BD-03/09/10/11/13と既存[#1180](https://github.com/hat47x/tei-platform/issues/1180)/[#2514](https://github.com/hat47x/tei-platform/issues/2514)へ差分帰属し、新たなTest正本は作らない。

**Plugin／Script／Harnessとの非混同**：[Plugin Contract→Actual Use Draft #4621](https://github.com/hat47x/tei-platform/pull/4621)、[主線反映 Draft #4620](https://github.com/hat47x/tei-platform/pull/4620)が提案するContract/Build/Invocation/Effect/Disclosureの区分は評価欄として再利用可能だが、実Buildで子を拒否した証拠をProductのRuntime Provider・現在Grant・Business Effect受理には使わない。[Script Entry Draft #4618](https://github.com/hat47x/tei-platform/pull/4618)のSelected Provider→Actual Invoker照合も独立Runの責務。AI Skillや外部HarnessはBuilder IdentityのIssuer/承認者ではない。TAI #168のG0/G1/G2・H2/H3独立4 Slot（適格0/4）を別P0に保つ。

**計画の実装順**：まずTEI #4623の最新HEAD `f1e219a`に追加された**Resolve→起動前pin接続のGo/CLI正負試験**をexact-head CI・Ownerレビューで検収する（Draft・未統合）。次に#4583でBuilder/Contract/Source/Target/Artifact Roleを同じAttemptへ束縛し、非Plugin Studio DesktopのN2/N3実消費→B2→B3へ進む。#4587のmain競合を解消した後、**当該HEADの新pin込みWindows WebView2**を独立検証。TAIは本体Builder/Resolver/Stage Ownerを代行しない。

**状態**：本節は製品ソース差分・exact-head GitHub CIの再確認に基づく**docs-only更新**。新たなTEI Go/Node/Windows E2E、Loader実byte、正式BuildIntent実Builder接続、Stage1→Stage2、外部Harness実Session/OS送出、SHO/SUI独立Consumerの今回の実行は**NOT RUN**。すべてのPRは個別のDraftとOwnerレビューであり、本TAI Draftも未merge。新Runner・Host・Registry・第二Acceptance正本を導入しない。

<!-- yic-skill-adoption-gates-20261114 -->
## 49. 2026-11-14：Skillの起動・失効時縮退・標準採用を独立に判断する（後続計画）

### 49.1 既存議論を重複せず接続する
本節は、main §47のTool-only優先、§48のR0〜R5実Product往復、[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488)の横断比較、[Draft #648 §10〜12](https://github.com/hat47x/tai-pleroma/pull/648)の三閉包・Activity Packet×TAI Skill四群比較を、**Skillの採用判断と失敗時の行動**に接続する。比較の独立Expected・実行Runnerは[TAI Draft #621](https://github.com/hat47x/tai-pleroma/pull/621)／#488と[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)・各Product Ownerが保持し、第二のSkill Router、Validator、Agent Loop、Handoff v2は作らない。

**使用時にSkillを起動する判断**と、**標準配布に含める判断**は異なる。Jobに対して現在のProduct CLI/API/MCP Tool-onlyで足りるならSkillなしで進める。製品専門手順が必要ならProduct Skillの必要部分のみを実ロードする。複数Productの活動・出典・未決・再開が必要な場合に限りTAI Activity Skillを評価する。Skillの存在・説明・署名はTool実装・実Host Grant・意味受理・実効果の証明ではない。

### 49.2 使用時の最小判断票（三つの閉包と独立結果）
| 判断対象 | 実証主体と見る実物 | 不足・変更時の処理 |
| --- | --- | --- |
| Instruction / Package（I） | Product OwnerのSkill root・実際に参照するScript/資料の版とbyte、Harness実Loader Read、Adapter対応（TAI #74/#168） | 参照差分・部分Loadは当該Skillだけ再資格化。実Toolが適格ならTool-onlyへ縮退 |
| Subject / Information（S） | ProductのWorkspace Root・Source/Subject/Occurrence・現在Revision・Required/Consumed・取得範囲・Validation（各Product／TAI #629/#271） | 同byte別Root、A→B→A、partial・not-enumerated・根拠の欠損ではPinの意図を保ち、影響Claimだけ現在Readerで再評価 |
| Capability / Authority（C） | 実CLI/API/MCP、選択Plugin/Builder・実Invoker、現在Host/OS/Network Grant、受信AudienceとDisclosure（Product/Host、TAI #232） | Tool欠損、選択B・実A、期限切れGrant、送出範囲不明なら権限拡大・Write・外部Shareを停止 |
| 実行後の利用資格 | 完全Tool Reply、同一AttemptのConsumer実Body再Read、Receipt、Ownerによる現在Meaning/Effect（TAI QH §10／各Product） | 旧Receiptの再利用、欠落Reply、ACK喪失を現行実Consumer成功や安全な自動再送にしない |

これは**共通Schemaでも全Skillを常時チェックする新Engineでもない**。既存Ownerの実証票で対象に関連する列だけ記録する。歴史的観測H／現在用途資格U／今回の実Attempt Aを別々に扱い、構造Fingerprintの不変を現在Validation/Grantへ昇格させない。Product側の生データやSkill内部情報の名前・存在・digestも、許可なく公開Prompt/Manifestへ漏らさない。

### 49.3 状況別の縮退は安全な作業まで一律停止しない
| 今の不足 | 維持できる行動 | 禁止する飛躍 |
| --- | --- | --- |
| Skillが未Load／参照Scriptだけ変更 | 権限のある既存Toolでのread-only調査。影響したSkillだけ再Load | SkillがLoaded/Usedだと自己申告 |
| Sourceが曖昧／集合partial／UI Pinの元Rootが異なる | 旧意図・保留を保持したPreview、Product Readerで再解決 | 先頭1件への暗黙付替え、部分集合を全件・0件と扱う |
| Tool/Host Grant/Disclosure未確認 | 現Product内で許可済みの操作、または停止・明示確認 | 別Toolへ無断切替、外部送出、Write/Effect |
| Tool Replyの途中切断・旧Receipt再生・ACK不明 | 状態をunknownに保ち、同一Attemptの独立再Readを行う | 非冪等Operationを結果未確定のまま盲目的再送 |
| 同一外部Harness Sessionに別UIから接続不可 | 既存Handoff v1による用途限定のActivity引継ぎを検討 | Transcript/Grant/Tool Stateを丸ごと移し同一Live Sessionと呼ぶ |

Product UIとCLIの認知順は、**対象と意図 → 現在のSource/欠損 → 利用可能なTool → Skillの必要性 → 送出Preview → 実行結果と元Productでの受理**を基本とする。自動Share・自動Applyや共通UI ABIの新採用ではない。SUIのAI OFF原資料利用、TEI StudioのPin／Desktop、SHO WriterはそれぞれのOwnerが実操作を検証する。

### 49.4 配布標準への採用を、Job/環境別の価値で判定する
| 配布・起動候補 | 採用の条件 | Owner |
| --- | --- | --- |
| Product単独 Tool-only | 当該ToolとSourceが実到達し独立Expectedを満たす。Skillが不要でも利用可能性を維持 | 各Product |
| Product Skill（用途別の任意導入） | 同じTask/Source/Tool/Harness条件で専門手順・根拠・誤操作回避・修正負担に固有の改善。実Loaderと参照閉包、追加費用も記録 | Product Owner／TAI #488 |
| TAI Activity Skill（条件付き） | Product Toolと限定Packetだけでは不足する、複数Product間の継続・再資格化に実測増分価値。Packetの生成/照合費用も計上 | TAI #271/#488/#74 |
| unsupported／unknown／not-run | 実能力・資格未確認時は公表する適用範囲を限定。調査候補は残すが常時起動にはしない | 各Owner／TAI #422 |

**比較のOwnerを重複させない**：[Draft #648 §11](https://github.com/hat47x/tai-pleroma/pull/648)のM00（Packetなし/Skillなし）、M01（Skillだけ）、M10（Packetだけ）、M11（両方）を利用し、M10−M00はPacket寄与、M11−M10はPacket固定のSkill追加寄与として判定する。[TAI #647](https://github.com/hat47x/tai-pleroma/pull/647)のrec-1はSkillなしでも適切な結論で、TAI Skill追加の回答差はなく、約38KBと2 Tool Callが増えた**n=1かつG0不適格の限定結果**。これを普遍的なSkill無効論にしない。根拠が有効なときの適切な限定再利用、意味変更時の停止、無関係変更時の過剰保留も試験前の独立Expectedで評価する。

### 49.5 実装順序とClaim上限
最優先は独立した二つのP0：①[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の実OS Read-deny G0→実Egress G1→完全Tool Reply G2→新規独立H2→H3→H3→H2（比較適格**0/4**）；②[TEI #4583](https://github.com/hat47x/tei-platform/issues/4583)／#1824の選択Builder→実Invoker/ArtifactSet→Stage1自身のStage2 Desktop再構築→Stage2実WebView2。TEI [Draft #4623](https://github.com/hat47x/tei-platform/pull/4623)の起動前Builder digest／Resolve-to-pinの局所実装は、非Plugin Desktopの全工程BuildIntent受理、OS LoaderのTOCTOU排除、B2/B3成功とは分離する。どちらのP0も他方の新Hard Gateにしない。

後続は、各Product単独のSubject/Raw実Read → 既存Handoff v1の独立Consumer再Read → Tool-onlyとProduct Skillの実比較 → 中断再開におけるPacket×SkillのJ-V四群比較 → 用途／Harness／開示Profileごとの条件付き配布の順。UIの同一Session閲覧・同時Turn／Interrupt・実Product反映は[Draft #648](https://github.com/hat47x/tai-pleroma/pull/648)にある別資格のままとする。

**状態：本節はDocs-onlyの計画更新**。新しい外部Harness試験、OS/Network、J-V四群、複数UI同一Live Session、元Source Consumer E2E、TEI B2/B3、実業務Effect、Owner正式受理は今回**NOT RUN**。Draftのままレビューを待つ。

### 49.6 Native Sessionの独立性を番号でなく実Context系譜で判定（2026-11-14）

<!-- yic-sk02-native-lineage-h2h3-20261114 -->
[TAI Draft #649](https://github.com/hat47x/tai-pleroma/pull/649)の既存SK-02比較Checker変更を、H2/H3の**実行前適格条件を判別する具体的な候補**として採る。実装対象は既存 check-sk02-pair-eligibility.cjs とSynthetic CI Workflowだけ。元Sessionからfork/resumeされた子は、新しいNative Session IDを持っていても独立試行とは認めない。**実測で継承が陽性ならineligible、不完全・不正な系譜情報ならinsufficient-evidence**。root IDが重複、親IDが非空、fork depth>0、session_start_modeがfork/resume、session_is_seeded=true、inherited_event_count>0を反証として扱う。通常forkで親IDが消えてもseed/event継承が残り得るため、親IDの不在を独立の肯定証拠にしない。

**合成ケースの範囲**：E73〜E82の10件を追加し、既存72件と合わせた**82件のSelf-testはTAI Draft #649 exact HEAD bac29b0fでCI成功**（[SK-02 Run #43545823209](https://github.com/hat47x/tai-pleroma/actions/runs/43545823209)、同HEAD S1 Product-only・tai-referenceも成功）。Checkerに追加されたroot/parent/depth/seed等は**観測できる場合の任意診断**であり、既存Trial Schemaや初回4 Slotの必須入力を変更しない。既存のindependent_session_observed=true、4 IDの相違、Checkerでeligible-to-scoreを返すこと自体は、OS物理Read-deny／真正な完全Native履歴／Raw遮断／実外部Trial成立を証明しない。PR #649はDraft・未mergeのため、**本計画へChecker採用規則を反映しても現行main適用とは呼ばない**。

**最初の一手**は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)と既存RunbookのG0実OS許可Source Read正例＋Reviewer/親Root/他Lane/旧Session実Read拒否（負例）。G1実際のRecipient・Egress、G2 stdout/stderr・完全Tool Reply、その後に初めてH2→H3→H3→H2の**新規4独立Session**。DSHなどのNative実ログでroot/session/thread・seeded/event継承とOS/Contextを確かめる。Skill有無の比較Arm、固定Task/CLI/Tool/Expected、ITT/PPは変更しない。G0が不適格なら新Skill/Providerへ逃げずenvironment-ineligibleで停止。評価上の適格は**現時点0/4**。

**実証状態**：#649の合成82件・CI成功は既存PRの限定証拠であり、今回TAI計画側でNode自己試験やOS/Harness実験を再実行したわけではない。新実DSH四Session、実OS/Network隔離、独立Expected採点、Skill効果とOwner受理はNOT RUN。

<!-- yic-cross-client-context-delivery-20261114 -->
## 50. 2026-11-14：CLI／Studio Desktop／Studio Web／外部Harness間のSkillと情報の実適格性（後続計画）

### 50.1 Skill可搬性と実行環境の資格を分離する

[TEI Studio #1824](https://github.com/hat47x/tei-platform/issues/1824)の共通Go Service・TypeScript WorkbenchとWails Desktop／Web候補、[TAI Draft #648](https://github.com/hat47x/tai-pleroma/pull/648)のActivity引継ぎ・Session閲覧・同時操作の分離を接続する。**同じProduct Skill本文を配置できること**と、当該環境の対象Source／実Tool／Host権限を使えることは別資格。Tool-only→必要時Product Skill→必要なTAI Activity Skillの選択原則（§47/49）は維持する。

| Consumer候補 | 対象と実権限のOwner | Skillが仮定してはならないこと |
| --- | --- | --- |
| 単独CLI | Product Process/Workspace Root/実CLI・OS Principal | CLI存在＝Skill Loader成功・Source全体取得 |
| Studio Desktop | Wails/Studio Host・許可Root・Host Inspect・UI Pin Intent | GUI Focus/描画Edge ID＝意味対象ID、同一OS利用者＝プロセス間Raw隔離 |
| Studio Web（将来構想） | 認証済み利用者とチームServer・Workspace/Branch/Revision・現在Grant | 同じURL/Document/Session＝同じ権限、DesktopのローカルFile APIをそのままWebで利用可能 |
| 外部Harness／別Product | 実Harness Loader/ToolとProduct/Hostが許可したProjection/Recipient | Handoff/Transcript＝現在Raw・Grant・同一Live Session・業務Effect |

Web共同開発の**L1テキスト同時編集／L2意味変更と競合処理／L3 Git・PRによる正式版確定**はTEI Studio側の設計・実装判断。SkillがL1の文字列同期をL2のMeaning MergeやL3の正式受理へ昇格させず、AI変更案は各ProductのCandidate Review／明示Applyを介する。別ユーザーのDirty BufferやPinの状態を無断上書きしない。Webの中央Serverが必要でも、YIC専用の共通Skill Runtime/中央Agent Hostの新設理由にはしない。

### 50.2 取得されたContextの完全性をSkill説明から推定しない

[TEI Design Context Query #3262](https://github.com/hat47x/tei-platform/issues/3262)の**required／declared／discovered／loaded／parsed／bound／returned**と、Page／Continuation／End・Tool Reply完全性はProduct Queryの実資格として参照する。Skillは当該Subject・Workspace Root・Source Revision・Required Scope・取得Coverage・対象Audience/Grantを確認し、観測できた範囲だけを説明する。

- 8,192 byte等の途中切断、RequestとReplyの不一致、分割取得中のSource/Grant変更、Source Index参照0、空Catalogや成功validateから**完全取得／不存在／現在意味受理を推定しない**。対応済みのProduct Readerがある場合だけ同対象・同Snapshot条件で再Queryし、未提供ならunknown/partialのまま保持する。
- Skill rootの短い案内と必要referencesの遅延LoadはModel Contextの節約であり、元のProduct Source／必要な依存がすべて取得済みであるという主張ではない。**Instructionの実Load／Subject情報の十分性／Tool Replyの完全受領／独立Consumer Read**は別列。
- PermissionとDisclosureは実Product/Hostが判断する。非公開のObject名、Hidden ID、件数、Digest、内部Pathやログ、Cursor等の情報も開示対象に含まれる場合があり、Productが許す範囲以外は外部Prompt/公開Manifestへ移送しない。

### 50.3 先に実施する小さい適合実験（追加の巨大E2Eなし）

[TEI #3262](https://github.com/hat47x/tei-platform/issues/3262)、[#4515](https://github.com/hat47x/tei-platform/issues/4515)、[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488)の**既存Expected/Ownerを再利用**し、公開許可された1 Subjectについて①実CLIのQualified Subject/必要集合/出典/欠損、②実Studio Hostで同じ対象をInspectした結果、③実提供できる場合だけHarness Tool-onlyとProduct Skill実Loaderを対照する。Web共同編集やNative Session共有を最初の検証に必須としない。

独立負例は、(a)同Kind/IDでも別Workspace Root、(b)分割取得途中のSource/Grant変更、(c)切断Replyを全件0として結論、(d)UI FocusとPinの混同、(e)Toolの実未提供／Skill references未Load、(f)二利用者のDirty BufferとAI Candidateの暗黙上書き。各Productが実現していない経路はunsupported/NOT RUNとする。TAIは実QueryやOS Policyを複製せず、評価票で異なるConsumer間のClaim上限を照合するだけ。

**優先順の不変**：[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)のG0実OS Read-deny→G1送出→G2完全Tool Reply→独立H2→H3→H3→H2（比較適格0/4）と、TEI #1824/#4583の実Studio Desktop／Stage1→Stage2セルフビルドは独立P0。追加するWeb/Skill横断検証をこれらのHard Gateにしない。本節は**Docs-only Draft**。実Web共同編集、実異Principal Grant、外部Harness完全受領、Studio→Harness→Product E2E、Owner受理は今回**NOT RUN**。


<!-- yic-web-skill-surface-qualification-20261114 -->
### 50.4 2026-11-14：実Wails ServerのMethod分類とSkill公開資格を区別する

**実装から確かめた境界**：[TEI Draft #4627](https://github.com/hat47x/tei-platform/pull/4627) exact HEAD 9491bf9eは、StudioBridgeのWails Service登録と、実Go exported method setの**15件**をserver build-tagテストで検査する。分類は read projection 7、bounded source read 1、command plan 1、reference command 4（in-memory effectあり）、external child process／file path 2。新しいmethodや登録変更ではレビューが必要となる。ただしこれは**露出候補の棚卸し**であり、Public Webの認可、Wailsの全HTTP Route、WebSocket配送、外部Tool/Skill実操作を許可する証明ではない。

同HEADの[Wails Host CI #43544229895](https://github.com/hat47x/tei-platform/actions/runs/43544229895)ではnested Go module／server tagの実試験と、loopback Server／Chromium二BrowserContextsの表示分離・後着Catalog処理が限定成功した。**二つのBrowserContexts＝別Principalの現在Grant・Workspace分離・WS機密情報の非配送ではない。** 利用者向けのJS Viewから機能を隠したこともGo Serviceでの呼出拒否を意味しない。

| 既存試験Ownerに戻す負例 | 独立Expected／縮退条件 | 担当 |
| --- | --- | --- |
| WS-SK-01 実Service面とSkill案内の差 | Product/Hostが当該Audienceへ許した実read-only ToolだけをSkill/Tool discoveryで案内。exported methodを全件公開済みCapabilityと誤認しない。Hostで拒否を測れなければShared Web公開を保留 | TEI #1824/#3421/#4627、TAI #488 X03 |
| WS-SK-02 二Principal・二Workspace | 二つの実Actor/Grantで同じ公開Subjectを閲覧しても、非公開Source/件数/Path/旧TranscriptやWS Tool Eventの越境到達を実拒否できること。UI表示分離だけならM0 Product-only／限定M1とし、M2/M3 Live共有は未資格 | TEI #1043/#2515/#1824、TAI #232／#234 HC-15 |
| WS-SK-03 Command／Path入口 | ExecuteCommand系、OpenShoDocument／ResumeShoDocument、REA local-only Evidence PathなどをWeb/外部Harnessから任意Command/PathでInvokeできないことをHostで検証。必要ならActor/Root/Scopeを持つProductの許可入口へ限定 | TEI #3421/#3394/#4625、TAI #488 |
| WS-SK-04 後着結果とProduct Apply | 二Browser Tab、旧Pin／別Root同digest、切断したTool ReplyをNative TurnとProduct Source epochへ別々に帰属。画面表示は成立しても現在Productへの無断Apply 0。Native多Writer保証が不明ならM2/M1へ縮退 | TEI #4515、TAI #234 HC-16〜18／Draft #648 |

**その後の同一Ownerの進展**：[Draft #4627](https://github.com/hat47x/tei-platform/pull/4627)はexact HEAD f2f49a7でService登録検査を実 application.Options.Services のASTへ寄せ、未知Service差込・二重登録・登録式の変更を含む**6件の合成負例**を追加。[Wails Host Workflow #43545456013](https://github.com/hat47x/tei-platform/actions/runs/43545456013)のnested server-tag Go testはcompleted/success。Browser由来の allowed string list は**Host Grantではない**と分類。これでも静的Inventoryとloopback二BrowserContextsの証拠に限られ、異PrincipalのHTTP/WS拒否は未実施。旧HEAD 9491bf9eの実績は履歴として残し、新HEADの別CIと混ぜない。

<!-- yic-wails-4627-gofmt-recheck-20261114 -->
**後続CI差分の注意**：TEI #4627のHEAD f2f49a7／a0850047は、それぞれ[Health #43545455990](https://github.com/hat47x/tei-platform/actions/runs/43545455990)／[Health #43547953342](https://github.com/hat47x/tei-platform/actions/runs/43547953342)で同テストのgofmt不一致によりFAIL。修正した**最新HEAD b9cf5447は5/5 Workflow completed/success**（[Health #43549001517](https://github.com/hat47x/tei-platform/actions/runs/43549001517)、[Wails Host #43549001431](https://github.com/hat47x/tei-platform/actions/runs/43549001431)、Windows Desktop WebView等）。過去失敗は履歴に保持。この証拠は15 Method Inventory＋6合成負例の静的ガードに限定し、実Principal/WorkspaceのHTTP/WS認可・Tool拒否やPublic Web適格へ拡張しない。

**最小の接続順**：①現loopback Wails Serverの実method inventoryとProduct Inspectを限定観測、②TEI Ownerがread-only公開面／実Actor・Workspace拒否を独立試験、③適格な実Web Capability Discoveryが得られたときだけSkillへ当該read-only手順を提示。Product Skill名・共通UIコンポーネント・表示結果をWeb認可のIssuerにしない。公開用Facade/Hostの判断はTEI、TAIは既存X/HC票の比較欄のみを所有する。

**Buildという別の実到達**：[TEI Draft #4587](https://github.com/hat47x/tei-platform/pull/4587) HEAD 0fcb7b6／[Windows CI #43542664470](https://github.com/hat47x/tei-platform/actions/runs/43542664470)では、同一AttemptのN2生成bundle→N3 Go EmbedFilesのmember/byte digest照合、改変コピー拒否、native WebView2受領を限定確認。実Consumer選択の良い独立証拠だが、Web Actor認可、Tool/Skill配布、compiler read-time依存全閉包、非Plugin BuildIntent、Stage1→Stage2 Desktop完了ではない。DesktopセルフビルドとTAI #168のH2/H3比較（適格0/4）の二P0へ追加Hard Gateを設けない。

**状態**：本節はDocs-onlyの追補。新たな二Principal実Grant/WS隔離・公開Web Host拒否・外部Harness Skill実Load・Stage2 Desktop・Owner受理は今回NOT RUN。

<!-- yic-skill-resume-evidence-promotion-20261114 -->
### 50.5 再開するSkillの適用可否は、履歴を引き継ぐ前に現在のProductとHostへ照会する

[TAI Draft #648 §26〜32](https://github.com/hat47x/tai-pleroma/pull/648)は長時間Goal/Schedule/Native Session/Turn/Activity、Product Operation、EKI Task/Attempt/Lease/Result、および複数Harnessの開発作業票の**既存Owner別の実証順**を担当。本Skill計画はその参照を利用し、**新Scheduler・Agent Loop・Work Package Schema・Session Store・Git Merge Engineを作らない**。

| 再開時に確認すること | Skill／Harnessが実行できること | 誤って昇格しないClaim |
| --- | --- | --- |
| **Session fork／Context継承** | 実Native root・parent・seed・inherited events・Source/Current Grantを実確認。実比較SK-02では継承陽性のSessionを不適格とし、作業再開用途では必要な履歴だけ許可Projectionとして新Sessionへ明示引継ぎ | 異Session ID＝独立Trial、fork＝同じLive Writer、過去Session Grant＝現Granted Capability |
| **Goal再起動・予定欠落・Delivery ACK** | 外部Harness/Providerの現在Goal/Occurrence/Inboxと元Product Operation/Taskを**別照会**し、公開pure/read-only Jobに限る再実行許可を確認 | Goal armed／配送ACK／Tool Response＝Product開始・Effect・Owner承認 |
| **Reply/Effect不明・Lease失効** | 元Operation ID/Attempt/Lease/Receipt/Result BodyとConsumerをProduct/EKIに再照会。実Body未取得・旧Effect unknownなら保留し人に戻す | Blind retry、別Native Sessionでの無条件重複作用、旧Worker結果の復活 |
| **3独立開発Workstreamの引継ぎ** | [TEI #2017](https://github.com/hat47x/tei-platform/issues/2017)の既存A0〜A4作業票にIssue・base/HEAD・許可Path・Source/Builder/Tool版・独立Test・未決・開示制限を紐付ける。次HarnessはSourceを再Readし、候補だけをProduct Ownerへ返す | Transcript丸ごと移植、Git merge＝意味受理、別BranchのCI Greenを統合HEADのBuild証拠とする |
| **Evidenceを別Agent/PRへ渡す** | TAI #232／TEI #2515の既存Disclosure条件で公開可能な結果・unknownのみ配る。保護されたTool argv/Raw/Stderr/Private Path/秘密由来Digestは別Audienceの検査結果と分離 | 安全試験で取得した秘密RawのCI/Issueへの転載、Sourceの存在/件数の漏洩 |

**次の小実験**は、TAI #234／#422の**許可された公開read-only 3独立Workstream**を Product-only→Tool-only→必要時限定Handoffの順に比較すること。ただしPacket×Skill四群(M00/M01/M10/M11)の独立Expected・実CostはTAI #621/#488へ戻し、Workstream数とSkill群を一度に増やさない。統合の受入はGit Scope、Subject/Meaning、Build/Runtime、独立Review、Product/Owner Acceptanceを**別票**として判定する。A2隔離Branch/A3既存Git/CI/A4人間判断の順は適格時だけ進め、初回H2/H3比較とDesktopセルフビルドP0には加えない。

**具体的な停止線**：前回はSkill/Toolの三閉包I/S/Cだけを更新すれば済む場合と、元Product OperationのEffect unknownで再実行できない場合が異なる。Skillの再LoadやActivity再開が成功してもProductの自動再Submitには移らない。ここに記載したGoal/3 Workstream/二Harness/Native Resume/Result Bodyの新実験は今回NOT RUN。既存Draft #648の手順・Expectedをそのまま参照する。

<!-- yic-real-host-role-tool-route-qualification-20261114 -->
### 50.6 Skill採用を「仕事→役割→実行経路」で判断する（Hostと契約の交差点）

[TAI Draft #648 §18.1／§28.1〜28.3](https://github.com/hat47x/tai-pleroma/pull/648)の**モデル→役割→仕事の二段割当**、Native Capabilityと利用権限、契約／Quota／費用／復旧の区別を、前§49のSkill起動判断へ接続する。モデル・Harness・Host・Product Tool・Subscription／API・Skillは、一つの「利用可能」フラグにまとめない。新しいYIC Model Router、Quota Server、共通Execution ABIは作らない。

| 実Jobの判断順 | その場で必要な実観測 | 不成立時の縮退・禁止する昇格 |
| --- | --- | --- |
| 1. 目的・Task・独立Expected | Product Subject/Source/Root、純粋ReadかEffectか、必要Precision・期間・公開Audience | Task自体が不確定ならAI Roleや高額Modelを先に固定しない。重要なEffectはOwnerへ |
| 2. 役割と推論の候補 | 探索／実装／独立反証／Reviewの役割、同条件で必要なContext・推論品質 | Model名を能力の証明、複数Sessionを独立Reviewerの証明にしない |
| 3. 当該Harness/Hostでの実Capabilities | Native Session・CLI/MCP Toolの**実Discovery/Invoke/完全Reply**、Skill root＋参照の**実Load**、Product実Version/Schema、OS/Grant/Disclosure | Package installed・Model available・Tool listedだけでLoaded/Invokedとしない。未対応なら正当なTool-only／Product-onlyへ |
| 4. 正規利用経路と資源 | 公式CLI認証／公式APIの別権利／第三者Gateway契約／ローカル実行のうち、今回の**正規Host/Plan/Rate Limit/Quota/予算** | 定額App枠をAPI/Gatewayへ流用できると推定しない。GatewayのOpenAI-compatible応答を同一Toolや価格保証としない |
| 5. Skillの増分効用と現在のSubject資格 | 同じ公開Task/Source/Expected・実Tool/Host条件でTool-only対照、追加Load/失効再確認/費用/誤判断を測る | Tool-onlyで足りるならSkillを標準Loadしない。古いSkillやContextを現在Product権限へ昇格させない |
| 6. 途中変更・失敗時の復旧 | NativeのQuota/Tool/Reply、元Product Operation/Attempt/Result、Source・Recipientの現在資格 | 失敗した応答やEffect unknownを成功・Rollback扱いにせず、別Model/Hostへ権限と秘密を無断移送しない |

**配布の判断は利用時とは別**：[TAI #74](https://github.com/hat47x/tai-pleroma/issues/74)は当該HarnessへPackageを配置できるか、[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488)は実Loader/Toolと増分品質、[TAI #234](https://github.com/hat47x/tai-pleroma/issues/234)はNative Session/Goal／Quota、[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422)と[TEI #2018](https://github.com/hat47x/tei-platform/issues/2018)は実仕事の費用・Reviewer工数を判定する。Skill内容はProductの読取手順・停止条件へ限定し、Quotaや料金を版の変わるSkill本文へ埋込み固定しない。Tierの名称や公式経路の可用性は利用者Account/時点ごとの実確認事項。

**Studioの実行境界をSkill Capabilityに混ぜない**：[TEI #4635](https://github.com/hat47x/tei-platform/issues/4635)／[#1824 LPC-01〜08](https://github.com/hat47x/tei-platform/issues/1824)がProduct共通Operationの配置を**四方式**で比較する。**A**＝Wails/GoのNative同一Process、**B0**＝同じGUI実行ファイルからself-spawnするWorker子Process＋local IPC、**B1**＝別のserver-tag Wails Server実行ファイル＋loopback HTTP/WS、**B2**＝別Server実行ファイル＋Named Pipe/UDS（Browser JSがPipeへ直接接続せず、Native Bridge→Go IPC Client→子Service）。B0は単一配布ファイルでも**二つのOS ProcessとGo Runtime**であり、B1のWails Server modeを意味しない。B1/B2の別Server Artifactも、同一バイナリや公開Web認可を意味しない。**配置B0/B1/B2とセルフビルド工程B0〜B3は別軸**である。

四方式は同じProduct typed Operation／Subject・Root・Revision・Failure契約を保ち、実Process imageと起動引数、Peer ID／ACL、version handshake、Child crash/Orphanと旧Reply、Cancel後Effect unknown、Source/Current Grant、許可Audience、配布とBuild receiptを独立に検査する。Windows Named Pipeの既定ACLを安全なPeer制限として仮定せず、別Principal／別Workspace／Remote接続拒否をProduct Hostで実測する。短いRPC・数十KB一覧・大きなProjection／長時間Buildについて、冷温起動、p50/p95/p99、UI入力遅延、CPU/合計メモリ／配布bytesを**同一Fixture**で比較する。実測前にPipe/UDSがHTTP/WSより速い、あるいはB0がNativeより速いと決めない。**外部AI HarnessのNative Session／Tool／Skill接続はこれらのDesktop内部配置と直交**しており、local Pipe/HTTP/ExecuteCommand/任意Pathを外部Harnessへ公開しない。P0はA方式のDesktopセルフビルド、B0/B1/B2の最適化はP1以降である。

**小さい実験と実装位置**：既存公開TEI一Subjectで①Product-only CLI、②同じHostのHarness Tool-only、③必要なProduct Skillの実Loadの順に観測する。正規利用経路・追加費用・Quota・Capability欠落とCurrent Grantを別記録。初回H2/H3四SlotはG0/G1/G2と独立Source/Tool Profileを固定したままで、本§の第二Harness/別課金経路/Studioの配置B0/B1/B2を初回比較に混ぜない。後続J-S/J-Vでだけ、利用可能な第二HarnessまたはDesktopトポロジーを一つずつ対照する。

**状態**：本節は既存TAI Draft #648・TEI Draft #4634・Product Owner票を結ぶDocs-only採否／受入計画。新しい実Quota/課金観測、四配置方式の性能・安全性の同条件Benchmark、実第二Harness、Web Authority、実Stage2、Owner意味受理はNOT RUN。TAI #168適格0/4とTEI #4583 P0は独立継続。

<!-- yic-real-product-command-skill-promotion-20261114 -->
## 51. 2026-11-14：新Product機能をSkillの案内へ昇格する条件（後続計画）

### 51.1 Productコマンドの存在・束縛・実使用を分ける

[TEI mainのyi-tei-modeling](https://github.com/hat47x/tei-platform/blob/main/skills/yi-tei-modeling/SKILL.md)の**正式な案内範囲はread-onlyモデル調査**であり、新しいREA/Build/Studio/GraphなどのProduct機能が開発されたときもSkillの対応機能を自動拡張しない。Skillの説明が現在のCLI/API/Plugin実能力と乖離しないため、具体的な入口ごとに**発見 → 対象の実束縛 → 実呼出し → 完全Reply・独立Consumer確認 → 現在用途への採用**を分ける。この列は新しい共通ABIやRegistryではなく既存Product/TAIの評価票である。

| Product入口の具体例 | 確認した実装・実証段階 | Product Skillの昇格条件 |
| --- | --- | --- |
| TEI catalog／inspect／trace／validate | mainの既存read-only入口と限定DSH H3実Loader Read。H2/H3比較適格は0/4 | 実CLI/Source版・Root・Tool Replyの観測範囲で従来案内を維持。Skill参照の遅延Loadは必要時のみ |
| REA Evidenceのlocal-only型付き外部候補 | [TEI Draft #4625](https://github.com/hat47x/tei-platform/pull/4625)は、保存済みREA Evidenceを既存Operationで読むlocal-only external-candidates入口の候補。外部REA実Processは起動しない | **未配布／未採用**。正式Product入口の採否と当該バイナリcommands/help/実Invocation/正負試験を確認して初めて、read-onlyの追加reference候補とする。ローカルPath引数や内部Pathを含み得る診断をStudio Web/MCP/Remoteへ転用禁止 |
| Source/Builder/Dependencyの宣言とResolver出力照合 | [TEI Draft #4624](https://github.com/hat47x/tei-platform/pull/4624)は不一致拒否のProduct内部候補。Go局所試験とWindows/外部Hostは別 | Resolver契約が正しいだけでSkillに任意BuildやPlugin呼出権限を追加しない |
| Resolver選択Builderと実子Imageの実行前digest照合 | [TEI Draft #4623](https://github.com/hat47x/tei-platform/pull/4623) exact HEAD f1e219aの8系統CI成功は**限定したPlugin主体の選択→実子起動前照合** | 非Plugin Desktop N0〜N3全Build、Stage1→Stage2 Windows、OS Loaderまでの差替え、実Current Grantは未証明。read-only Skillをセルフビルド実行Skillへ自動拡張しない |
| SUI Raw・SHO Writer・TEI Studio Desktop/Web・EKI Effect | 各Product/Hostの実装と受入Owner。TAI [Draft #648](https://github.com/hat47x/tai-pleroma/pull/648)のNative Session/Capability対応は後続 | Skillは用途限定で実Providerの能力を案内する。UI Focus/Handoff/Tool exitは元Source読取、Author Review、Write／Effectと独立 |

### 51.2 Product Skillを改訂する実際の順序

**Step A：まずProduct本体を確認する。** RepoのSkill説明文でなく、選択した実Executable/Serverのcommands/help、実schemaVersion/result shape、argv/subject/root/Source、実Read Scope、失敗分類を確認。利用者用に公開できない情報はProduct/Host側で必要部分だけ投影し、Toolの発見情報だけから現在Grant/配布資格を作らない。

**Step B：必要な専門手順だけを増やす。** 現Skillのread-only入口が足りない具体Taskを固定する。新機能がProduct main/対象配布Profileで実利用でき、独立Expectedの成功・失敗・Tool完全受領が観測できた場合だけ、Owner判断でSkillの該当referencesへ小さく手順を加える。Skillルートの名称/descriptionで未実装Capabilityを先行宣伝しない。既存H2/H3固定比較のSkill byteを途中差し替えない。

**Step C：ローカルとRemoteの境界を保持する。** #4625のEvidence Path入力はローカル専用のProduct境界。実元SourceやProviderの現在資格、Current Grant/Disclosureは保存Evidenceのdigestからは導けない。Web・外部Harnessで使う場合は別のHost許可済Reader/Projectionと実Consumer受領の検証が必要であり、その機能が無ければunsupportedとする。非公開のPath・Object名・存在や内部診断を出力から漏らさない。

**Step D：選択と実行を同一Attemptにする。** #4624のIntent/Resolver一致と#4623のBuilder実子起動前チェックは別PRの限定Evidence。正式な非Plugin Studio Desktopセルフビルドを主張するには[TEI #4583](https://github.com/hat47x/tei-platform/issues/4583)でBuilder Catalog→実Invoker→N2/N3 Artifact→Stage1→Stage2 Desktop→実WebView2を各Ownerが同一Attemptで検証。Skillは実Build/Meaning受理のIssuerにも、実Host権限の代行者にもならない。

### 51.3 判別する最小の負例・後続Owner

| 負例 | 独立に拒否・保留すること | 既存Owner |
| --- | --- | --- |
| Skill説明に新commandがあるが選択CLIには無い／出力shape・実versionが違う | 架空Tool呼出や旧結果shapeの自己補完をしない | TEI #2605、TAI #488 X01/X03 |
| Local CLIで保存REA Evidenceを読めるがWeb経由で任意Evidence Pathが渡された | Host許可Byte Reader未提供ならunsupported。内部Path診断を外部送出しない | TEI #3394/#4625、#2516、TAI #232 |
| Resolverが宣言と違うBuilderを返す／Builder digest一致でも実Role/Authorityが違う | 宣言・選択・実Invoker・Host GrantのどのClaimまで成立したか区別 | TEI #4624/#4623/#4583 |
| Product Scopeは部分取得、Tool Reply欠損、別Workspace同byte | 完全性／現在Subject同一性／不存在への過大Claimを拒否 | TEI #3262/#4515、TAI #271/#488 |
| TAI Skillが不要な単独Product Taskで追加Loadだけ増える | Tool-onlyの成功を維持。Skill価値は既存M00/M01/M10/M11で別測定 | TAI #488/#621/#648、配布#74 |

**実行順は維持**：[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)のG0実OS Read-deny→G1送出→G2完全Reply→独立H2→H3→H3→H2（適格0/4）と、TEI Desktop #1824/#4583のStage1→Stage2を独立P0。新Product ToolのSkill案内更新やREA remote化、WASM/Web適合を初回比較・セルフビルドのHard Gateにしない。§51は既存Source/Issue/局所CIの照合から作った**Docs-only Draft**。新実CLI/OS/Harness/REA二Consumer/Studio/EKI Effectの横断E2E・Owner正式受理は今回NOT RUN。

<!-- yic-source-selection-to-operation-admission-20261114 -->
### 51.4 2026-11-14：AIが選んだ出典からProduct実Operationまで、飛び越せない二つのProduct境界

[Draft #648 §20〜25](https://github.com/hat47x/tai-pleroma/pull/648)がActivity→Product→Harnessの因果帰属を扱う。本節はさらに、**選択された原資料の位置**と**呼び出されるCapabilityの結果契約**を、実コードで進展した個別Ownerに還元する。両者を新しい共通YIC操作Schemaへ統合せず、Skillは既存Product API/受入票にだけ案内する。

**A. Source-selection境界**：[SUI Draft #3443](https://github.com/hat47x/sui-sensemaking/pull/3443) の単一Text Run限定Referenceは、許可されたRaw byteを与えた場合に、BOM・混在改行・日本語・非BMP文字を保持した**UTF-16表示選択 → UTF-8半開byte範囲**を写像し、surrogate内位置やRenderer不一致を拒否する。固定57-byte Referenceでは同一表記の前方/後方をそれぞれ[11,30)／[38,57)へ分離する。**純粋変換・単一Text Node／合成Rawの実Chromium回帰は確認済み**だが、Product Root・Grant/別Process Card GET/現Source実再読は未資格。SUI #3441/#3438がOwner。見た目の文字列一致、同じ相対PathとRaw digestだけで選択したSource occurrence／Rootを同一としない。選択位置を持つCardやSHO文書は、保存後に元資料を再解決できた場合だけ該当出典Claimを再利用する。

<!-- yic-sui-content-snapshot-20261114 -->
**SUIの同一Snapshot補正**：[SUI Draft #3443](https://github.com/hat47x/sui-sensemaking/pull/3443)の現HEAD 7665442では、DOM選択のRaw byte位置とselectedText、全Raw/選択byte SHA-256用の入力を**非同期WebCrypto前に同一コピーとして固定**し、途中で呼出元がバイト列を書き換えても混合時点のCheckpointを作らないよう改善した。中間HEAD dd11826の実Chromium 11 E2E成功は単一の合成Text Nodeの範囲であり、**現HEAD `7665442c03504856848cbe83f0cb2afdfd4d0170`の[SUI単体CI](https://github.com/hat47x/sui-sensemaking/pull/3443/checks)はcompleted/success**。返るのはcontent-match-only／stale-contentで、Root/Grant/Source Revisionの連続性・A→B→A・Cardの別Process保存再読は未証明。**後続の実画面接続**：同Draft #3443 HEAD 6eed48baは既存SUI StartPanelに「原文の一時確認（保存しません）」を組み込み、ブラウザーFile API（最大1MiB）→元Raw byte/BOM/EOL維持→単一Text Node選択→UTF-8 byte範囲［38,57）とCheckpoint表示→折りたたみで一時React Stateを破棄する。実[Chromium CI #43557030239](https://github.com/hat47x/sui-sensemaking/actions/runs/43557030239)は当該HEADの代表E2E **13件PASS**、Raw/Checkpoint 11件・File API 2件・StartPanel 5件の単体検査および型検査/build/Backend契約も成功。ただし実OS File Pickerでの人手選択、正式Source Host/Root/Grant、Document/Card保存、別Process GET、元資料への現在版再到達は**未検証**。折りたたみはOS File消去や完全メモリゼロ化の保証でもない。Skill/Handoffが受領したContent Hashや一時Previewを正式Source資格へ昇格させない。

**B. Product-operation境界**：[TEI merged #4629](https://github.com/hat47x/tei-platform/pull/4629) は既存Capability Invokeに、Adapter実呼出し**前**の不正Result契約拒否を実装・main統合済み。HEAD 00ea8523のGitHub Actions **9/9 completed/success**。空Capability ID、単一Outputとnamed Outcomesの矛盾、Result未宣言、重複Outcome名、Outcome名/型参照欠落の**6不正契約でAdapter Call=0**を回帰検証する。Go内部の限定PreflightはProduct実装済みだが、正しいResult形でも実公開Entry／選択Providerの真正性、現在Host Grant／Effect、nullable値・意味受理は未証明。TEI #4495/#3421／Draft #4618が後続Ownerであり、Skill/外部Harnessは実Capabilityを認可する主体ではない。

**C. 公開Host境界**：[TEI Draft #4627](https://github.com/hat47x/tei-platform/pull/4627)のServer Service Inventoryと6つのmutation-negativeは、公開し得るService面が意図せず増えることを検出する**静的レビューガード**。二つのBrowserContextsの画面分離と異PrincipalのHTTP/WS認可・秘密配送遮断は別。Web Client由来allowed list、Skillのread-only宣言、外部HarnessのTool DiscoveryをCurrent Host Admitに変換しない。TEI #1824/#3421/#1043、TAI #232/#488を使用する。

| 最小の後続実験（既存Expectedを使う） | Product/TAIで残す合否と禁止する飛躍 | Owner |
| --- | --- | --- |
| **出典候補**：同じ日本語が2回、BOM/改行/非BMP、同内容別Root | Raw UTF-8 byte範囲の正負を検査。実DOM複数Text RunやRoot未解決なら候補のまま。別Process ProductのRaw実ReadなしにSource確定としない | SUI #3441/#3438、SHO #48、TAI #271 |
| **操作候補**：不正なCapability結果契約／valid Outcome | 不正時Adapter Call=0と実errorを確認。正常な結果宣言でも実Provider Invocation/Host許可と区別。Ownerの意味・Effectへ昇格しない | TEI #4629/#4495、TAI #488 |
| **Web受領**：Browser supplied allowed／二Principal異Workspace／旧Reply | 実Hostで不許可Method/Path/HTTP/WSの拒否を確認。Inventoryや表示だけの成功ではWeb公開を保留。旧Pin/Turnへの後着ReplyはProduct Apply 0 | TEI #4627/#1824/#3421、TAI #234 HC-15〜18 |
| **Skillに必要な案内**：SUI Card→TEI検証→SHO候補文書 | 各ProductのCurrent Source/Scope/Disclosure/Toolをその都度再発見。未実装操作をunsupportedとし、配布/ロード済みSkillでも非認可機能を推測して実行しない | Product各Owner、TAI #488/#74 |

**最小の実装投資先**はProduct側の既存ReferenceとAdapter前の拒否・現在Host側の実Method/Principal拒否である。YICはSkillの専門手順・限定Projection・Activity Handoff・比較結果を管理するにとどめる。Sourceの写像器、Capability Runner、公開Web Authorization、二Consumer/二Principal試験の正本を新設しない。

**実行順と証拠上限**：初回P0は引き続きTEI #4583 Desktop Stage1→Stage2、およびTAI #168 G0→G1→G2→独立H2→H3→H3→H2（比較適格0/4）。この追加のSUI/Script/Web検証は後続・並行でありBlockingにしない。#3443の限定smoke、**main統合済み#4629の内部Call=0**、#4627の限定CIを**一つのProduct横断E2Eに合算しない**。本節はDocs-only・新しい実ブラウザーSource再読／Provider呼出／Web二Principal認可／外部Harness Skill比較・Owner受理は今回NOT RUN。

<!-- yic-reabytehost-observed-ci-20261114 -->
### 51.5 REAの実CLIとHost byte-only入力を別段階としてSkill案内へ取り込む

- [TEI Draft #4625](https://github.com/hat47x/tei-platform/pull/4625) HEAD 24863bd6の**9/9 GitHub Workflow成功**は、ローカルEvidence Pathを用いた実CLI子Process／commands/catalog/JSON/Pinの限定技術検証。**Draft・未merge**。Tool自体は存在する候補だが、現行TEI main/公開Profileの機能とは宣伝しない。Web/Remote/MCPへ任意Pathを外部入力させない。
- [TEI Draft #4630](https://github.com/hat47x/tei-platform/pull/4630) HEAD 1ad749fcの**12/12 Workflow成功**（Windows Smokeは初回Timeout FAIL→当該JobのAttempt 2でPASS）は、R2 Candidate解釈を**Host管理byte列から受け取るProduct内部境界**へ分離する小実装候補。**Draft・未merge**。Hostが実Principal/Root/現在Sourceを確認してbounded Readし、同じ受信byteを実Consumerへ投影したことまでは保証しない。
<!-- yic-r3b-local-reader-stacked-20261114 -->
- [TEI stacked Draft #4637](https://github.com/hat47x/tei-platform/pull/4637) HEAD 170f9be5は#4630のbyte-only Operationを受け、Studio Host起動時にだけ固定したWorkspace/Selector→Workspace相対のEvidence Pathを内部で解決し、既存ReadOnly.workspaceとworkspace.ReadSourceの**4MiB bounded single Read**から解析する局所Reader候補。呼出側はWorkspace/Selector/Observation/Relationを渡すだけで任意Pathを指定できない。同Rootの重複Selector、unknown Workspace、path脱出、symlink、Raw Pin不一致、Root差替えなどを負例にする。内部Path/秘密Edgeを含み得る失敗は一般化し、Host内部の原因と外部応答を分ける。**実装依存は#4630のbyte-only Operation**。現在PRのbaseはmainだが差分4ファイルに#4630由来2ファイルを含み、mainにはFromBytesが未統合であるため、#4630の採否後に重複差分を整理する。旧HEAD 170f9be5は12/12 Workflow成功。別OS子ProcessのHost Reader実読取試験を加えたHEAD f9e355d5はHealthのgofmt不一致で11/12、整形修正HEAD f38117dcは12/12成功。さらに同じProducer Evidence ID・申告Source Revision・Node/Relationでも、二つのWorkspace Rootから実Readする負例を追加した[TEI Draft #4637](https://github.com/hat47x/tei-platform/pull/4637)現HEAD 9b8f5ca9b50d34040cfa0682f026f4fc29090f01は、[同HEADのCI](https://github.com/hat47x/tei-platform/pull/4637/checks)が**12/12 Workflow completed/success**（GitHub Actionsを再取得し確認）。中間HEADで改変後のRaw DigestをHost Bindingへ再Pinすると正常Producerとして受理できるという誤Expectedが実Go試験で否定され、**試験のExpectedを訂正してR2 Producer byte整合条件を維持**。片Rootだけ異byte／再Pin／Root実体差替えを拒否し、元byteへのA→B→A復帰で再Readできても変更履歴の連続性は証明しない。子Processはテスト用で、正式Studio／CLI／外部Harness Consumerではない。 Readerは現状Wails/HTTP/MCP/外部Harnessへ公開されず、Current Principal/Grant・Audience別Disclosure・A→B→A履歴・別Consumerは未適格。Skill説明に「遠隔REAの読取り対応」を追加しない。

**次の実用昇格条件**は、TEI #3394/#4503/#2516側で既存Studio Hostの許可Selector→一度だけ限定byte実Read→既存Operation→許可Projection→第二Consumer実Readをつなぎ、同名別Root／Symlink／改版／内部Error Pathの外部非開示をProduct Ownerが検査すること。REAの実解析・保存Evidence・現在原資料の資格も別。YIC Skillは実CLI/Hostで提供済み・許可済みの**read-only受領手順**のみを案内し、新File ServerやPath Resolverを構築しない。

**Skillへの昇格判定**：#4625（Local CLI）と#4630（Host-owned bytes Operation）は各固定HEADの局所CI成功。#4637のHost固定Selector／4MiB bounded実Readも旧HEADのCIは成功したが、最新二Root追加HEAD 9b8f5caも**12/12 Workflow成功**を確認。ただし正式Source同一性・Current Grant／Audience・実Product Consumerを合格にしない。ただし現TEI main／正式配布Skill Profileから実利用できることは確認していない。`NewLocalREAReader`はWails/HTTP/MCP Toolに未登録であり、Tool説明やSkill本文へ「外部HarnessからREAを読める」と記載してはいけない。まずProduct Ownerが配布対象Executable/HostでのDiscovery、現在Host Grant、返却値のAudience/Disclosure、実Tool完全Reply、元Source/第二Consumerの再Readを個別に検証する。その後、必要Taskに限って既存Skill referencesへ**local-only手順から段階的に追加**する。前提PRのmain統合、Skill配布版、実Consumer試験は別Claim。新R3-Bの外部Agent/Meaning受理は未実証。初回H2/H3とDesktop Stage1→Stage2の追加Blockingにはしない。

<!-- yic-real-product-evidence-promotion-20261114 -->
### 51.6 実装・CI成功と、Skillが案内可能な製品機能の間に残る受入条件（2026-11-14）

他チャットの実装進展を、**局所テスト／現mainの実Product Capability／当該Hostでの実Tool呼出し／Model完全受領／独立Consumer／Owner受理**の別Claimで検収する。新たな横断Registry/Host/Runnerは作らず、既存Product Ownerの受入票とTAI #488の比較欄を使う。

| 対象・確認済みの実成果 | 残るProduct受入とSkillでの停止線 |
| --- | --- |
| [TEI merged #4629](https://github.com/hat47x/tei-platform/pull/4629)と[merged #4636](https://github.com/hat47x/tei-platform/pull/4636)：各9/9 exact HEAD CI。ResultだけでなくInput名・型／Effect宣言の不整合／nil Contextを**Go Adapter呼出し0回**で拒否 | TEI #4495/#3422：受理済みpure Entry→Host選択の**実Go Provider**→通常CLI/Studioの実Result、Current Grant/Owner Meaning。静的宣言の検査だけでEntry公開・業務EffectをSkillから案内しない |
| [TEI Draft #4625](https://github.com/hat47x/tei-platform/pull/4625) 9/9、[Draft #4630](https://github.com/hat47x/tei-platform/pull/4630) 12/12、[Draft #4637](https://github.com/hat47x/tei-platform/pull/4637)の子Process追加HEAD f9e355d5はHealth gofmt FAIL（11/12）、修正HEAD f38117dcは12/12成功。二Root・同Producer ID／異byte／再Pin拒否を加えたHEAD 9b8f5caは**12/12 Workflow成功**（11/12は完了前の中間観測） | ローカルCLI保存Evidence／byte-only Operation／Host固定Selectorの**4MiB bounded実Read**は局所技術実績。TEI #3394/#4503/#2516がCurrent Root/Grant/Disclosure、同一Producer→独立Reader/第二Consumerを検収するまでは、Wails/MCP/Remote Skillの「REA利用可能」と宣言しない |
| [TEI Workspace Validation #4655](https://github.com/hat47x/tei-platform/pull/4655) HEAD `3261d172` は7/8 CI success・[Repository Health FAIL](https://github.com/hat47x/tei-platform/actions/runs/43572997113)。同名/空Capability Inputを既存DSL Parser→World→Validatorで発見し、main統合済み#4636のAdapter前Call0拒否と比較するDraft | Runtimeで不正構造を拒否できてもStudioのSource診断／正式Entry公開・実Provider利用は別。Healthの**gofmt未整形**とmainのConsumer設計README索引漏れ（[小修正 #4658](https://github.com/hat47x/tei-platform/pull/4658)）を解消し、**新HEADで再CI**するまで本機能の完全適合やSkill案内は保留 |
| [TEI Draft #4627](https://github.com/hat47x/tei-platform/pull/4627) HEAD b9cf5447 **5/5 Workflow成功**（過去二HEADのgofmt失敗は履歴） | Wails Options.Services／15 Method＋6合成負例の静的ガード。TEI #1824/#3421で実匿名・二Principal／異Workspace HTTP/WS拒否とEvent Audience隔離が成立するまでは公開Web Capabilityの資格なし |
| [TEI Draft #4638](https://github.com/hat47x/tei-platform/pull/4638) HEAD 0ce3a52f：[実隔離PG16 CI #43553849861](https://github.com/hat47x/tei-platform/actions/runs/43553849861)で参照Readerの7ケース全成功 | 実ReceiptはReference Executorの範囲であり**Product Read accepted=false／Host Grant accepted=false**。TEI #2586はRA-0 #4626のCurrent World/歴史Frozen Sourceを別資格で検査（新HEAD 94876821で歴史RunnerをFrozen Worktreeだけ旧byteへ復元、現在Sourceの宣言は保持）。Browser/API依存監査でsqlgen symbol検出が継続しE1は失敗のため、Allowlistを緩めない。RA-1→正式Product Operation→通常tei CLI→Function Context→異質二Consumerを**同じ適格Checkout**で実受領する必要がある。Skillに参照Readerを正式Toolとして掲載しない |
| [SUI Draft #3443](https://github.com/hat47x/sui-sensemaking/pull/3443) HEAD 6eed48ba：既存StartPanelの一時Raw Preview・実File API・DOM後方Selection・byte位置表示・破棄まで[実Chromium代表E2E 13件PASS](https://github.com/hat47x/sui-sensemaking/actions/runs/43557030239)。Raw/Checkpoint等の限定単体検査も成功 | 表示は**unqualified-local-file-preview**。実Source Root/Scope/Grant、CardへのSource Binding、Document CAS Save、別Process GET、A→B→Aを実証しない。SUI #3441/#3438のOwner決定と正式Product Readerの再読取前は、Skillから永続出典を案内しない |
| [TEI Query仮統合 Draft #4644](https://github.com/hat47x/tei-platform/pull/4644) HEAD `b5c23044` **3/3 CI成功**：RA-0 typed `:from`→RA-1 Executor前拒否→RA-2実PG16の参照Readを同一Checkoutで確認 | Product通常`tei` CLI→実Provider→Function Context→Native/別Consumerの同一Attempt Read、現在Grant/公開Scopeは未実装。歴史Runnerの旧Sourceと現Worldを混ぜない。Browser/API `sqlgen`二symbolの失敗が残り、Product Skillで「注文Queryが利用可能」と案内しない |
| [TEI Function Context Draft #4647](https://github.com/hat47x/tei-platform/pull/4647) HEAD `a962a3f6` **7/7 CI成功**：RLS/LIMIT/JOIN/宣言外Relationを実観測したときのみ`partial`。Native SQLは`native-sql-predicate-not-closed`を残し`complete`／`EmptyJustified=true`は出さない | 実SQL関数内Predicate・W4列由来・QueryのScope/Current Grant/Source Revisionは未資格。`unestablished`や`partial`、0件を全件不存在と表示・回答・Skill指示に変換しない。TEI #2586/#2506の本来のClaim Ownerへ戻す |
| [SUI Source予約欄拒否 Draft #3444](https://github.com/hat47x/sui-sensemaking/pull/3444) HEAD `6f864be6` **3/3 CI成功**：未採用Binding/Selection予約欄をClient送信前/緩いImport/Backend PUT前で拒否し、既存Card/ETagを保つ限定負例 | A/B/C Source保存方式は未採用。SUI #3441が正式Root/Grant/ReadとCard Save→別Process GET→元Raw byte範囲復帰をOwner受理するまで、#3443のFile previewを永続Source Skillとして案内しない。HTTP 422は権限の実証ではない |
| [TEI Go toolchain観測 Draft #4648](https://github.com/hat47x/tei-platform/pull/4648) HEAD `64fb0f9a` **8/8**、[State観測 Draft #4537](https://github.com/hat47x/tei-platform/pull/4537) HEAD `cb7faf8d` **8/8 CI成功** | 同じPlanでも異Go Compilerで別Binaryが生じる。`toolchainObservation.matched`は指定Pathのbyte照合で実起動確認ではない。`stateObservation.effect-observed`は旧StateのcopyやOS隔離を保証しない。二Draftの共通Self-buildファイルが競合し得るため、Owner #2831で同一HEAD再テストが必要。Stage2完成/生成物Skill実行許可へ昇格しない |
| [TEI Studio #4587](https://github.com/hat47x/tei-platform/pull/4587) **最新HEAD `9b58533d`で12/12 CI成功**、[Windows #43572235468](https://github.com/hat47x/tei-platform/actions/runs/43572235468)も成功。生成bundle N0→N2→N3・実Desktop WebView2受領の限定B0。旧`357345d7`は通常DesktopのOS probe timeoutで11/12だった履歴。[Builder #4634](https://github.com/hat47x/tei-platform/pull/4634) `7d6a1238` 8/8は別HEADのPlugin主体のResolver/Child pin | **別HEAD／別Attemptの成功を足さない**。TEI #4583/#2831で非Plugin BuildIntent N0〜N3実ArtifactSet→生成Stage1→Stage2→当該Stage2のWindows WebView2を同一Attemptで確認。未完了のWindows WorkflowをH1/B2/B3合格としない |

**新しいProduct成果をSkillに昇格させる前の4つの否定条件**（現行§51.6、2026-11-14）。以下は既存Ownerへの受入索引であり、初回SK-02のTask/Skillを変更しない。

| Product側で成立した限定検査 | Skillが守る説明・実行上の停止線 |
| --- | --- |
| [TEI #4644](https://github.com/hat47x/tei-platform/pull/4644) HEAD `b5c23044`：RA-0/1/2仮統合Checkoutの3/3 CI成功＋隔離PG16実参照Read | 製品通常`tei` CLI／正式Context／Native別Consumerとは未接続。RA-0単独にはBrowser/API E1 `sqlgen`違反が残る。Type宣言なしの生成CLI [#4559](https://github.com/hat47x/tei-platform/pull/4559) の文字列`:from`をTyped Provider入力として案内しない |
| [TEI #4647](https://github.com/hat47x/tei-platform/pull/4647) HEAD `a962a3f6`：実PGでRLS・LIMIT・JOIN等の`partial`を観測、CI 7/7 | native SQLは不可視関数述語を含み得るため`complete`／`EmptyJustified=true`を案内しない。0行を「該当注文なし」とせず、`native-sql-predicate-not-closed`と`partial/unestablished`を独立Claimに維持 |
| [SUI #3444](https://github.com/hat47x/sui-sensemaking/pull/3444) HEAD `6f864be`：未採用Source Binding欄をFrontend送信前・緩いImport・Backend PUTで明示拒否、CI 3/3 | HTTP 422は正式Source/出典保存の完了ではない。旧Card/held/異論/ETagを保ちながら、Document readとSource readのGrantを分離。Card→Save→別Process GET→元Raw復帰は#3441 Ownerへ |
| [TEI #4648](https://github.com/hat47x/tei-platform/pull/4648) `64fb0f9a`／[#4537](https://github.com/hat47x/tei-platform/pull/4537) `cb7faf8`：各8/8 CI。異Go toolchainで同一Plan・異Artifact byte、State Effect/Process Imageの限定観測 | `l2b.claimed=true`、報告されたToolchain Digest一致、`stateObservation=effect-observed`は、Builder実起動物／State隔離／Seed Trustを証明しない。実Product ToolやSkillの「再現可能」宣言には#2831 Ownerの正式BuildIntent入力・現Runtime検証が必要 |

**昇格条件**：使用先Productの実Version/Root/Host/Scopeで`selected→actually invoked→received`を測定し、Source/Provider/Coverage/Artifact/Toolchainが問合せ・用途・受信者に十分かを判定する。任意の一面のCI成功やダイジェスト一致から`complete`、実Grant、Skill Load、業務意味受理を推定しない。未提供の機能は`unsupported`、被覆不明は`unestablished`／`unknown`とする。非Plugin Stage1→Stage2とTAI #168の実H2/H3 0/4はP0として不変。

**配布済みのbyteと利用資格を二段階に分ける**：[TEI main統合 #4617](https://github.com/hat47x/tei-platform/pull/4617) は独立Node Consumerが**test-only HTTP**からEd25519署名付きReleaseと二つのArtifact Memberを別GETで検証するE1-C（正常1／拒否9）。これはPublisher/Verifierの固定テスト鍵によるProduct外Referenceであり、実GitHub Release/Asset、Current Trust/失効、Hostの実Plugin/Skill選択・Tool Load/Invocation、RecipientへのDisclosureは未受理。[TEI Registry Draft #4640](https://github.com/hat47x/tei-platform/pull/4640)が実Release、redirect/認証転送、immutable設定、公開と秘密の混在を既存Owner #2589へ割り当てた。YIC Skill導入順は**実配布物の署名・member byte一致 → 今のHost/Workspace/Principalへ許可されたProvider/Capabilityを実選択 → 実Tool呼出し・完全受領 → 実Consumer/価値**であり、署名確認だけで使用許可・実意味・H2/H3資格に昇格しない。新Registry/Verifier/Trust Authorityを作らない。

**Skill利用時のClaim設計**：実Source/Rowset/Score/引用/出典を表示する場合は、`coverage=partial`と`coverage=unestablished`、`unknown`・`not-run`を入力の現時点/受信者のScopeとともにそのまま伝える。Product Ownerが完全性を独立検証していないNative SQLでは、0行に対して「該当しない」「購入していない」「全件検索済み」と断定しない。読み込めないSource BindingをSkillが本文・Card・Receiptへ黙って保存しない。失効・未対応時はread-only限定の`unsupported`/`unknown`へ縮退する。これらは**案内の制限**でありYICが新しいQuery Planner/認可/Raw Storeを持つ決定ではない。

**昇格する実際の順**：①Product Ownerが現main／選択Targetの実Source・Scope・Tool/Entryを確認、②実Host Admitと許可ProjectionのProduct read-only結果を取得、③実HarnessでTool Invoke／完全Replyを実観測、④必要なら別Consumerで原Sourceを独立再Read、⑤同Task/Tool/RootでTool-onlyとProduct Skillの実Loader/価値を比較する。Product専用の局所CIだけなら候補のまま。Unknown／Unsupportedの明示は正常。

**先行P0を妨げない**：TAI #168のG0実OS Read-deny→G1実Egress→G2完全Reply→新規独立H2→H3→H3→H2（比較適格0/4）とTEI #4583のDesktop Stage1→Stage2を独立維持。新しいREA、PG、SUI、Studio Toolを初回四Slotに追加しない。[TAI Draft #649](https://github.com/hat47x/tai-pleroma/pull/649)のfork/seed/inherited eventsでは異Session IDでも実Context継承を独立母数に算入せず、[TAI Draft #621](https://github.com/hat47x/tai-pleroma/pull/621)のEffect unknownはSkill再Load・Activity再開で盲目的に再試行しない。本節はDocs-only、OS/Harness/DB/GUI新実験とOwner受理はNOT RUN。


<!-- yic-skill-crossroot-pretransport-20261114 -->
### 51.7 Skillの引用・送信・保存前に、出典の同一性と開示資格を独立に照合する

[TAI Draft #648 §37〜38](https://github.com/hat47x/tai-pleroma/pull/648)のJ-R0（二Root局所Read）→J-R1（送信前拒否）→J-R2（正式Source保存・別Process再Read）→J-S（Harness受領）を、**実Productの現在資格に従ってSkillが使うか保留するか**という採否へ結び付ける。新しい共通YIC Resolver・AuthZ・Store・Runnerや二重のExpected正本は設けない。

[SUI Draft #3444](https://github.com/hat47x/sui-sensemaking/pull/3444) exact HEAD 6f864beの[3 Workflow成功](https://github.com/hat47x/sui-sensemaking/pull/3444/checks)は、未採用Source Binding予約欄に限り、FrontendのHTTP送信前拒否、緩いImportの明示拒否、Backend PUT 422、Agent投影の純粋関数負例を確認した（Backend 323件／Frontend 1,943件）。**送信前拒否はBackend拒否と別の保証**であり、正式Source保存Schema・Source別Grant・実Agent/Guest HTTP開示やDocument全属性の非漏洩は未実装。

| 既存Expectedを使う反証 | Skill／Activityができることと停止線 | 所有者 |
| --- | --- | --- |
| Documentの閲覧は許可されたが、元Sourceへの現在Grantは無い | Document閲覧資格からRaw・Locator・件数・Digest・Source存在や外部共有を推定しない。Doc内の自由記述・GET payload自体が秘密を含む場合は、Productの許可Projectionが無ければ外部へ転送しない | SUI #3441/#3444、TEI #2516、TAI #232 |
| Root Aは許可、Root Bは不許可。二Rootに同Producer ID・同Revision申告があり、Raw byteまたは保存場所が異なる | 元Hostが選んだWorkspace Root・Selector・Producer Pin・読取Attemptを現在Productで照合。Root Aの成功をRoot Bへ転用しない。BのRaw Digestを再Pinしても元Producer deliveryが更新されたとは解釈しない | TEI #4503/#4637、TAI #271 |
| SUI一時File Previewは成功したが、出典保存A/B/Cは未採用 | Previewは未資格の候補にとどめる。Source Binding予約欄を黙ってCardへ保存せず、Client送信前に拒否し、元Card・held・異論・ETagを保つ。正式CAS Save→別Process GET→現在Source再Readが未成立なら出典確定と呼ばない | SUI #3441/#3444、SHO #48 |
| Local Source Readerは成功したが、外部Recipient／Tool Replyは未資格 | 実HostのAudience/Recipient許可Projection、Egress、完全Tool Replyと独立Consumerを別々に照合。テスト用OS子ProcessやAgent投影純粋関数を製品Studio／外部Harness受領へ昇格しない | TEI #4503/#3421、TAI #168/#488 |
| QueryはNULL・0行・一部Rowsだけ返した | [TEI Draft #4647](https://github.com/hat47x/tei-platform/pull/4647)のpartial／unestablishedを保持し、native SQLの閉じていない関数述語やRLSを無視して全件検索・不存在・EmptyJustifiedを案内しない | TEI #2586/#2506、TAI #488 |

**後続の一仕事の観測票**：既存Productの公開・許可済み一Subjectについて、①出典候補と元Root/Revision、②Document閲覧・元Source Read・送信Audienceの別々の現在Grant、③送信前に拒否した項目と実Wireで出た内容、④実Operation・Tool Reply全体の受領、⑤独立Consumerの元Source再Read、をProduct/TAI各Ownerの既存試験へ記録する。Sourceの存在・拒否理由自体が秘密なら、別Audienceへ詳細を漏らさずunqualifiedとする。Source bytes一致・SHA・過去Receipt・Client許可リストをHost認可へ昇格しない。

**優先順位は不変**：このJ-R0〜J-Sは後続のProduct/Skill適合検査。初回TAI #168 G0実OS拒否→G1実Egress→G2完全Reply→新規H2/H3四Slot（現適格0/4）、TEI #4583 Native Stage1→Stage2 Desktopセルフビルドは別P0のまま。現行Product-only／Tool-onlyで許可された仕事は継続する。本節はDocs-onlyで、横断実E2E・実二Principal開示・意味Owner受理を新たに実証していない。

