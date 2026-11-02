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

## 19. 2026-11-02：合成評価の拡大と最初の実Product観測を分けて進める

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

**状態**：Runbookと順序・責務の計画追補。実TEIビルド/CLI、別HarnessのH2/H3/H4/H5、SHO/ EK Iの実Artifact・OS/Networkの負例、Owner採用は**NOT RUN**。新共通Host/中央Registry/第二の証拠正本/万能Agentは追加しない。
