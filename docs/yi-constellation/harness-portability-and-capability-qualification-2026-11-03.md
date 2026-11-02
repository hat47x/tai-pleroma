# YI Constellation：複数HarnessのSkill可搬性と実Capabilityの資格化（2026-11-03）

**状態：TAI Draft #270への設計追補／未採用。実際のHarness install/load・MCP/CLIの複数Harness比較・現在のHost Grant・Production Effectは NOT RUN。** ここに書く候補は外部製品の導入を完了したという意味ではない。

## 1. 狙いとOwner

[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) Harness-first、[TAI #74](https://github.com/hat47x/tai-pleroma/issues/74) Skill/Pluginのシリーズ配布、[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271) Activity継続、[TAI Draft #270](https://github.com/hat47x/tai-pleroma/pull/270) SK-01を同じ評価計画へ接続する。「DSH以外の代表的ハーネスにも対応」という要求に対し、**一社固有のHarness実装をYI Coreへ入れず、外部Harnessの実装差を明示する**。

* Product Skillは各Product（TEI #2605/#2607、SEI #769、SUI #3368、SHO #10、EKI #468、MMI既存Skill）が所有する。TAIは用途に応じた小さなルーティング・Handoffの手順と、比較試験・シリーズ参照だけを所有。
* ProductのDomain/Role/Operator、Rule/Context、実CLI/API/MCP/Provider、意味受理/Authorityと、Harness内のSkill/Tool availabilityは別Owner・別資格。TAIに中央Agent/Registry/Host/Policy Engine/Capability Oracleを実装しない。
* 利用可能Harnessのない環境、CLIのみの環境、複数Productを要さないタスクは、それぞれ妥当な完成形となり得る。CSW/SUIの自由探索や、TEI/SHO単体利用をHarness接続待ちの全体Gateで止めない。

## 2. 最初に比較するHarness群と、同じと仮定しない点

以下は**候補の評価群**であり、利用者アカウントで各機能が利用可能・接続可能という意味ではない。比較する単位はブランド名ではなく、**Harness product/version + feature/profile + permission + session + loaded skill bytes + actual tool path**。

| 評価群 | 評価用の候補 | 最初の確認点 | やってはいけない同一視 |
| --- | --- | --- | --- |
| 開発用ローカルAgent | Claude Code | `SKILL.md`の探索、実ロード、shell/CLI、MCPの実接続、hooks/agent制限を実環境で確認 | Skill文書を読ませたこと＝実Tool許可 |
| 開発用Agent／ChatGPT連携 | Codex（必要ならChatGPT Plugin経路は別Profile） | Repo規約`AGENTS.md`、Skill/Pluginの実配置・ロード、CLI/MCP・Approvalの実観測 | CodexのローカルCLIとChatGPT/WorkのCloud操作が同じ |
| OSS CLI Harness／低コスト探索 | OpenCode（DSH/DeepSeekを利用する構成は独立Profile） | `.opencode/.claude/.agents`の実発見、permissionでhidden/denied/ask、MCPを使う場合の設定/版 | モデル提供者・料金プランの名前をHarnessのSkill/Tool対応実証とみなす |
| 継続型Cloud Agent | Dots（アカウントで利用可能な場合） | 接続Plugin・Skill・継続/通知の本物の提供範囲、Cloudの実受信・Approval | Codexと同じローカル`SKILL.md`ディレクトリが使えると仮定 |
| 継続型Bot | Grok Bot（利用可能な場合） | Skill/Connected App/Routineの実共有範囲、Schedule・Task実行・成果の受領 | Routineが作成されたこととProduct/EKI Task成功が同義 |
| 比較の基準 | CLI/通常ファイル／Tool-only（Harness無しまたはSkill無し） | 同じタスク・Source/Expectedを達成できる最小手段 | 導入済みSkill数が多いことを性能と見なす |

**公式資料の確認先（仕様資料であり利用資格の証拠ではない）**：
- OpenAI Plugin Skills：https://developers.openai.com/plugins/concepts/skills
- OpenCode Skill：https://opencode.ai/docs/skills
- OpenCode MCP（版ごとの設定差がある）：https://opencode.ai/v2/docs/mcp-servers
- Grok Bot Skills/Routines：https://docs.x.ai/grok-bot/skills-routines-and-automations
- Claude Code Skill：https://code.claude.com/docs/en/skills
- OpenAI Codex Repo Skill例：https://developers.openai.com/blog/skills-agents-sdk

2026-11-03時点の公開仕様は製品・プラン・Harness版で更新され得る。例えばOpenCodeの古いMCP設定表記とv2の設定表記を**同一Adapter設定として使い回さない**。実験前に該当実行環境のバージョンと公式仕様を再確認する。DSHは低コストモデル/推論の利用案とSkill/Tool Runtimeの実可用性を分けて記録する。

## 3. Candidateから実Effectまでを六つの同一性で切り分ける

[TEI Draft #2649](https://github.com/hat47x/tei-platform/pull/2649)のC0〜C5を**横断試験の記録軸として参照**し、TEIの採用済みCore Contractとしては扱わない。

| 軸 | TAIで記録すること | 留意する非単調な反例 |
| --- | --- | --- |
| C0 意味Source/Role | intended Source + occurrence、実bytes/version、Role/Operator採否と依存Pin | 同じWorldでもSource-only移動で引用・Trace資格が変わる。Role eager依存未固定 |
| C1 目的/Operation候補 | Product公開の候補・必要Context、Provider Gap、未解決Route | Operation名があるだけではProviderが結線されない |
| C2 実Interface | 対象バイナリ/Tool、actual dispatch、discoverable catalogのscope、argv、effect | TEI `commands`はselected read-onlyのみ。catalogにない`operations/artifacts`は静的dispatchあり。欠落＝不存在でない |
| C3 Skill/Harness | root+references+scripts依存closure、Package/Install/Load/Invoke、Harness/profile | Install済み≠Load済み、Skill root同値でもreferenced Scriptが違う |
| C4 Consumer/開示 | 読込者/audience、許可Projection、Tool候補・実Egress、SourceIndex/Renderer、実Read/receipt | 最終回答同値でもPlan/DOM/Network送出は異なり得る。JSON/MD生成≠別SHO Reader実受領 |
| C5 実効果 | 同時点・対象のGrant/Expected State、Provider独立Observation、Task/Attempt/BodyとOutcome | 過去成功/ACK/Manifest Complete≠現在のGrant/Body到達/Business受理 |

**重要な実証更新（2026-11-03）**：TEI [PR #2626](https://github.com/hat47x/tei-platform/pull/2626)は**2026-11-02T18:35Zまでに merged**（merge commit `00eb8e148daadbc2cf40145d8e8473d56531514c`）。このPRの実Go CLI CIでread-only 9プロセス、同JobのMarkdown/JSON再読取、Source-only移動とSourceIndex/Trace変化が限定観測済み。ただし**TAI H2/H3でSkillを実ロードしたこと／SHO別Reader／別Harness／Owner受理／本番Host効果の証拠はない**。TAIの既存Runbook中の「#2626 Draft」は履歴として読替えるが、#2649の独立Source-static Draftまでmergedと推定しない。

またTEI [Draft #2649](https://github.com/hat47x/tei-platform/pull/2649)では実Go Sourceの`operations`/`artifacts` dispatchが確認され、`artifacts -out`はファイル書込みを起こし得る。CLIの「閲覧」「JSON stdout」と**`-out`でのファイル副作用**は同じread-only権限で扱わない。Tool引数をeffect分類の一部として実観測する。Source移動を伴わないSkill文面改訂だけで過去のProduct意味証拠が全失効するとも推定しない。

## 4. Harness Adapterは能力差の投影であり実行器ではない

Harness固有の包装は、まず次の観測票を作る。これは**試験の列**であって、採用済みJSON Schema、共通Skill ABI、Tool/Authority Registryではない。

`harness name+build+profile; session/location; skill discovery path/version; packaged digest; loaded root/references/scripts digests; visible tool names/versions/aliases; actual invocation path (CLI/MCP/GUI/API); argument+effect class; input source+epoch; permitted audience; observed outputs/errors/diagnostics; actual egress receiver/bytes (testable portion); authorization/check time; effect/receipt/consumer-read status; unsupported/unknown; evidence owner/URI`

- `load`可でも `invoke`できないHarnessは、文書支援／通常ファイルhandoffだけに縮退できる場合がある。存在しないMCP/CLIをSkill説明で作らない。
- MCP Tool名はHarnessやバージョンでprefix/normalizationが変わり得る。文面の固定名ではなく、**当該Sessionの実Tool一覧と契約**で照合する。
- Skill名／Tool schema／非公開Action候補／error/trace/時間差も開示対象。許可された公開投影のみ外部へ出し、未公開情報の有無を外部に推測させる列を無断公開しない（TAI #232／Draft #272、SEI #770、SUI #3368）。
- 外部Harnessへ許可したProjectionと、Product内で閲覧できるRawは同一でない。実OS/Host/Network強制をSkillのプロンプトで代替しない。可視化だけで安全性をPASSとしない。
- Activityの中断再開ではHarness Aの旧Permission/Grant/Tool SessionをBへ複製しない。残すのは必要最小限の出典参照・未決・履歴結果、現在のTool/AuthorityはB側/Host側で再照合。

## 5. 試験の組み方：能力の独立変数と意味の独立性

**M0：現在の事実** — 既存TAI SK-G0、TEI #2605/#2649に従い、Harnessごとに「文書記載／インストール確認／実ロード／実Tool Call／実Consumer Read」を区分し、同一版のCLI/Sourceを固定。秘密の実環境データは送らない。

**M1：最小TEI読取** — [merged TEI #2626](https://github.com/hat47x/tei-platform/pull/2626)の公開参照Workspaceを使い、H2（Toolのみ）対H3（TEI Product Skill追加）の同Harness比較から始める。CLI read-only範囲は選択的catalogと、別コマンドの実dispatchを分ける。`operations/artifacts`は発見しても初回Skillで呼ぶ必須条件にしない。

**M2：第二Harness** — 同じProduct Skill本文・依存closure・Task/Prompt/Source/Tool/独立Expectedを別Harnessへ持ち込み、(a) loadそのものが不可、(b) load可/Tool不可、(c) Tool可/現在Grant不可、(d) read-only成立、(e) cloud/remote送出に不適、を別々に判定。機能を推測せず、実可用性がなければunsupported。

**M3：製品横断Skill** — [SK-MIN](skill-composition-minimal-routing-scenarios-2026-11-02.md)に従い、同じタスクで必要Productのみを使ったH4と、TAI Skill追加H5を比較。単体作業で全製品/全Skill導入を促した場合はむしろ負例。

**M4：変更／再開** — WorldFP不変・SourceIndexFP変更、Role eager依存改版、Skill reference script改版、Harness Profile/MCP alias変更、Provider/Grant期限切れ、Ownerレビュー版変更を**個別注入**。歴史Evidenceの保持と、現在必要なConsumer／Claim／Actionの選択的再確認（TAI #271）を別採点する。

**M5：実Provider／外部送出** — 適切なOwner管理下の公開合成canaryとmock Endpointで、Tool提案／実Invoke／HTTP Receiver／Consumer Read／Host側拒否を追う。別Egress経路、OS isolation、実業務Effectが未観測なら該当Claimはunknown/not-run。

初期合格の主張：**二つの実際に利用可能なHarnessに対して、同じ小タスクのProduct Skillロードからread-only Tool結果まで（または正確なunsupported）を説明できること**。単に2製品のマニュアルにSkillsと書かれているだけでは不合格。比較不能な環境は欠測とし、使える二環境の代わりに未観測のDots/Grok等を成功へ数えない。

## 6. 追加の反証Case（SK-HP01〜14、すべてNOT RUN）

| ID | 反証条件 | 期待する分類 |
| --- | --- | --- |
| SK-HP01 | `commands`限定一覧に`operations`なし、mainにはdispatchあり | 不掲載≠不存在。実Call/Effectは未確認 |
| SK-HP02 | `artifacts` stdoutを見たあと`-out`を付ける | 引数で副作用Classが変わる。既存read-only Skill許可を流用しない |
| SK-HP03 | Harness AはSkillを発見、Bは配置が違う | Bのloadはunsupported/未観測。GitHub保存だけでは済まない |
| SK-HP04 | Skill同名でも参照Script byteが違う | 別Skill closureとして比較。旧適合を自動継承しない |
| SK-HP05 | OpenCode Skill permission denyで候補が非表示 | 公開Viewが非表示でも内部の能力不存在を断言しない |
| SK-HP06 | MCP serverの接続成功、Tool名prefix/引数が変わる | Nameだけ一致でcallせず実Tool契約とaliasを再照合 |
| SK-HP07 | 一Product read-onlyで目的達成可能 | TAI/SHO/EKI追加を加点せず費用と過剰開示を計測 |
| SK-HP08 | 実CLI WorldFP同値、SourceIndex/Traceは別 | 意味再生成と出典/SHO再解決の資格を分離 |
| SK-HP09 | Root Role固定だがeager依存Pin欠落 | 意味候補はあっても正式解釈適格性は保留 |
| SK-HP10 | 実Skill LoadedだがCLI/MCP Toolなし | 「使えた」ではなく文書作業のみ/unsupported |
| SK-HP11 | Harness A成功、Bの現在Grant期限切れ | 歴史的結果は保持、Bの危険Actionを拒否しread-onlyを継続 |
| SK-HP12 | 同一最終回答だがTool候補・Session Eventが違う | 許可公開差と保護情報漏出を実受信で区別 |
| SK-HP13 | Cloud HarnessへSource Raw送信不可、ローカルCLI読取可 | ローカルread-only成立と外部開示適格性を分ける |
| SK-HP14 | EKI ACK済みだがBody未着、別Readerも未読 | Task/Attempt/Body/Consumerを別資格。「完了」禁止 |

**記録する指標**：Task成立と誤成功、Source/Role/Tool現在性、false unsupportedとfalse callable、余分なTool/Skill/製品選択、Context token、Tool回数、実費用・時間・人手確認、外部送出の対象/bytes、更新時の再資格化費用、他Harnessへ移す修正量。Toolの実呼出し資格と、業務Owner意味受理／Product正式リリースは別。評価集合・各Harness版・独立Expectedを実行前に固定。

## 7. 既存計画へ還流する単位

- **TAI Draft #270**：本書とSK-01 §YのSK-HP01〜14を導入、Harness固有差と実Capabilityの選択を評価。上位のSK-G0〜G6・H0〜H7・SK-MINを維持。
- **TAI #74**：配布ManifestにはProduct Skillの正本、参照closure/版、Harness Adapterの受理環境、Tool契約、権利/公開範囲、検証結果の区分を保持する。具体的な配布方式はOwner審査。
- **TEI #2605 / Draft #2649**：CLI実在性・選抜Catalog・命令effectの責任はTEI。新Skillの範囲を自動でwriteへ拡大しない。
- **SEI/SUI/SHO/EKI**：各製品がSource/Claim/Document/Resultの真偽と公開を所有。TAIは横断の候補判別だけ担当。
- **TEI #2018**：H2/H3、H4/H5、別Harnessの総費用と品質を同一Task/独立Expectedで比較する。成功時間短縮が品質を毀損した場合は生産性向上としない。

**今回の状態**：追加したのはProduct間/Harness間の評価方法と反証票であり、いずれのHarnessの実導入・実Tool呼出し・各Ownerの契約採用・GitHub mainへの統合も行っていない。
