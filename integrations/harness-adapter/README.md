# 共通Harness Adapter（最小実装）

外部AIハーネス（DSH、Claude Code、Codex等）から、YI Constellation各Productの能力を
**交換可能な形で**呼び出すための薄いAdapterと、その契約試験。

- 状態: **PoC実装・限定実証**。Adapter単体の契約試験はCIで常時実行できる。実Harness接続は
  `-tags realconnect` と `HARNESS_ADAPTER_REAL=1` の両方が必要で、既定では実行されない。
- 親Issue: [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)（Harness間適合）、
  [TEI #2509](https://github.com/hat47x/tei-platform/issues/2509)（DSH固有実証）、
  [TEI ADR-0048](https://github.com/hat47x/tei-platform/blob/main/plan/adr/0048-shared-application-api-and-transport-adapters.md)（共通Application API）。
- 設計判断の記録: [harness-adapter-minimal-contract-2026-11-11.md](../../docs/yi-constellation/harness-adapter-minimal-contract-2026-11-11.md)

## 1. 何をするか／しないか

**する**: Session参照、Context投影、Tool呼出し、Skill利用、結果受領、診断、Evidence追跡。
**しない**: 製品の意味、Source Revisionの権限、権限・認可、情報開示の判断、実際の副作用の管理。
それらは製品・Host・Provider側に残す。Agent Loop、モデルRouter、中央Session Server、
第二Registry、認可Engineは**作らない**。

## 2. 契約の核：七つのPinと五つの成否水準

一つのTaskは、互いに代入できない七つのPinを持つ（`contract.go`）。

| Pin | 型 | 何を縛るか |
| --- | --- | --- |
| Source | `SourcePin` | 製品のSource/Revisionと、**実際に消費したbytes**のdigest |
| Model | `ModelPin` | Provider/Model/Versionと、到達経路（Route） |
| Skill | `SkillPin` | Skill ID、配置先、**実際に置いたbytes**、Load状態（三値） |
| Tool schema | `ToolSchemaPin` | Harnessが**実際に広告した**schema、呼出しの有無 |
| 許可Root | `RootPin` | 論理名、解決済みpath、access mode、独立検証の有無 |
| 実送出Byte列 | `OutboundRecord` | 方向（argv/stdin/task-text/skill-bytes/stderr）ごとのdigestとbyte数 |
| Consumer受領状態 | `Receipt` | 読み手が**実際に**受領したbytes。既定は `not-observed` |

Harness側のSession IDは `SessionRef.ExternalID` として**不透明な観測**としてのみ保持する。
`--session-id` を要求してHarnessが別IDを返した場合は `SessionRejected` であり、継続ではない。

成否は五つの水準に分かれ、一つに畳まない（ADR-0048 §2.4）。

1. `Transport` — 要求がHarnessに届いたか（`delivered` / `failed` / `unknown`）
2. `Run` — Harness自身のターンの帰結（`completed` / `aborted` / `error` / `unknown`）
3. `HarnessStatus` — Tool呼出しに対するHarnessの報告（`completed` / `error`）
4. `ExitCode` — Toolが包む製品CLIの終了コード
5. `ProductVerdict` — 製品側の意味。`OperationCompleted` と `ValidationPassed` は**別欄**

`Result.Promoted()` は常に `false` を返す。このPackageのどの観測も、製品の意味的受理・
実行許可・実Effectの証明にはならない。

## 3. Adapter

| Adapter | 実行形態 | 状態 |
| --- | --- | --- |
| `dsh-headless` | `dsh --profile <p> [--patch ...] --json [flags] <task>` | **実接続済み**（DSH 0.2.2-rc.1, Windows） |
| `claude-code` | `claude -p <prompt> --output-format stream-json --verbose [flags]` | **実接続済み**（Claude Code 2.1.302, Windows）。2026-11-11夜は利用枠が枯渇 |
| `step-cli` | `step --approve --mode json -p [flags] <task>` | **実接続済み**（Step Code 0.1.7, Windows） |
| `direct-control` | モデルなし。Taskが宣言した製品Toolを決定的に実行 | **実装済み**。比較の対照腕 |
| `scripted-*` | 契約試験専用の二重結合。`FakeRunner` に再生させる | **契約試験のみ**。製品ではない |

`Registry` は呼び出し側が明示的に構築するプロセス内の名前解決。発見も読み込みもしない。
未登録のAdapter名を要求した場合は、登録済み一覧を出して**黙って別Adapterにフォールバックしない**。

Adapterが提供する補助:

| 要素 | 何をするか | 何をしないか |
| --- | --- | --- |
| `MCPServerSpec` + `WriteDSHPatch` / `WriteClaudeMCPConfig` | 型付きProduct ToolをVendor固有の設定形へ投影し、投影bytesのdigestを記録 | MCPを話さない、serverを起動しない、秘密を書かない |
| `ParseProductEnvelope` + `CompareProductEnvelopes` | CLI経路とMCP経路を同じ欄で比較し、未報告欄を「示されていない」として残す | 一致を単一boolのPASSにしない |
| `RootProbe` + `ApplyRootProbe` | Root外readの成否を独立Armで測る | 隔離を実装しない。読めた事実を隠さない |
| `ObserveSkillUse` + `ObserveSkillPair` | Skill LoadStateをtool callから判定しH2/H3の適格性を出す | 正答の比較をしない |
| `FileReadback` / `ClaimReadback` / `DirectReadback` | Consumerが読んだbytesをdigest・claimで照合する | producerの自己申告をreceiptにしない |

### Codex exec：限定的な追加（C1）

`codex-exec` は `codex exec --json --ephemeral --sandbox read-only -` の**単発JSONL経路**を扱う。Task本文はargvでなくstdinへ渡し、実Toolの結果とTurnの終端を分離して記録する。Codexの公開Source（`640b86dc879ceaaa126cdf183b417731e291f476`）の `exec_events.rs` を参照して実装した**契約試験段階**であり、Codex実バイナリ・認証・Tool・OS隔離の実接続は未実施。

- 既存の `Task`、`Result`、`Registry`、`Runner` を使い、共通契約の版は変更しない。`codex-exec` は `-real` 指定時のみCLIから有効になる。
- 本AdapterはContextRef・ToolOffer・Skill配置・Native Session resumeをまだ構成できないため、要求があれば**実行前にunsupportedで停止**する。読めるはずの資料やToolを黙って省略しない。
- `thread.started`、`turn.started`、`item.completed`、`turn.completed`／`turn.failed` の関係を解釈するが、`turn.completed`だけでは製品結果を受理せず、Receiptは常に `not-observed`。欠落した終端、Tool結果、壊れたJSONLは `unknown` のまま残す。
- `--ephemeral` によりNative Threadを保持しないため、ここで観測したThread IDから後日のresumeを保証しない。App Serverの双方向通信・承認・継続Sessionは[別途C2](../../docs/yi-constellation/codex-source-integration-decision-2026-11-17.md)で扱う。
- `--sandbox read-only` は設定の宣言であり、MCP／OS／ネットワークによる実効隔離や現在のSource開示資格の証拠にはならない。実外部Harness試験には別の環境・権限・送出確認が必要。

## 4. Product Tool投影

`TEIReadOnlyTool` はTEI CLIの**既存**read-onlyカタログ（`tei commands`、
scope `selected-read-only-commands`）からの投影。新しいAPIを作らない。

- offerする: `version`, `model catalog`, `model overview`, `model locate`*, `workspace-files`,
  `inspect`*, `trace`*, `source-index`, `knowledge-context`*, `validate`
  （*はSubject参照を投影が持たないため offer されず、`unsupported` として報告される）
- offerしない: `view`, `self-build`, `dbcheck`, `artifacts`, `grants` など書込み・Effect系。
  `argvFor` がこれらを組めないことで構造的に保証する。
- `-workspace` は投影が持つRootのみを指す。Toolは `AllowedRoots` にその論理名を宣言する。

`SEIReadOnlyTool` はSEI CLIのread-only面を投影する。SEI固有の差分は投影の中に閉じる。

- offerする: `resume`（必ず `-json`）、`doctor`、`version`。
- offerしない: `init`（store作成）・`add`・`export`・`gate`（書込み）・`mcp`（transport）。
  `verify` はbundle pathを投影が持たないため `unsupported`。
- MCP経由では `sei mcp -read-only` を必ず使う。このflagで `resume` だけが広告され、
  `-allow-decision` を渡さないため `add_recommendation`/`add_decision` の経路が
  構造的に存在しない。

**Productごとの語彙は共有契約に持ち込まない。** TEIは `worldFingerprint`、
SEIは `snapshot_digest` を報告する。`ProductEnvelope.Identity` に製品固有名のまま保持し、
比較は**両方に存在するkeyの交差**だけを行う。共有keyが無ければ identityは比較せず、
その旨をnoteに残す。

## 5. 契約試験と実接続試験の区別

| | 契約試験 | 実接続試験 |
| --- | --- | --- |
| 起動 | `go test ./...` | `HARNESS_ADAPTER_REAL=1 go test -tags realconnect ./...` |
| 外部Process | なし（`FakeRunner`） | 実Harness・実LLM |
| 断言 | 観測の構造・argv・成否の分離 | 観測が記録されたこと。**正答は断言しない** |
| Harness不在 | 常にPASS | `ineligible` として記録。偽PASSにしない |

実接続試験が要求する環境変数（未設定なら `t.Skip`）:
`HARNESS_ADAPTER_TEI_BIN`, `HARNESS_ADAPTER_TEI_WORKSPACE`,
`HARNESS_ADAPTER_TEI_SKILL`, `HARNESS_ADAPTER_TRIAL_DIR`,
`HARNESS_ADAPTER_HARNESSES`（既定 `dsh-headless,direct-control`）。
MCP系の試験は追加で `HARNESS_ADAPTER_TEI_MCP_BIN`、SEI系は
`HARNESS_ADAPTER_SEI_BIN` / `HARNESS_ADAPTER_SEI_STORE` を要する。

## 6. 実接続で確認できたこと（2026-11-11）

証拠: 下表の各ファイル（完全版はtrial directory。本repoのは結果bodyをdigestに置き換えた縮約版）。

### 6.1 shell経由のread-only往復

[evidence/real-pilot-2026-11-11.json](evidence/real-pilot-2026-11-11.json)

同一Task・同一Pinで三腕を実行:

| 腕 | transport | run | exit | tool calls | 観測 |
| --- | --- | --- | --- | --- | --- |
| `direct-control` | delivered | completed | n/a | 6 | 全Tool exit 0。製品envelopeから Operation/Validation を分離記録 |
| `dsh-headless` | delivered | completed | 0 | 5 | `skill` toolでProduct Skill実ロード、`pwsh`で実TEI CLI起動 |
| `claude-code` | delivered | completed | 0 | 2 | `Bash`で実TEI CLI起動。1回目は `-workspace` 不足で exit 2、2回目で成功 |

- divergences（自動算出）: `exit-code`, `session-state`, `tool-count`, `tool-names`, `unsupported`
- DSH腕: `model catalog` の結果が8192byteで投影截断 → `result:projection-truncated` を報告
- Claude Code腕: Skill Loader toolの呼出しが観測されず → `skill:load-not-observed` を報告

この段階のTool呼出しは**Harness独自のshell tool経由**であり、製品は型付き要求を受けていない。
6.2でこれを型付き経路へ広げた。

### 6.2 型付きMCP tool（H-A-1 / E1・E2）

[evidence/real-pilot-typed-mcp-2026-11-11.json](evidence/real-pilot-typed-mcp-2026-11-11.json)、
[evidence/real-pilot-typed-mcp-claude-2026-11-11.json](evidence/real-pilot-typed-mcp-claude-2026-11-11.json)、
[evidence/real-pilot-step-typed-mcp-2026-11-11.json](evidence/real-pilot-step-typed-mcp-2026-11-11.json)

promptは**型付きtool名**を名指しし、shellもCLI直実行も禁止した。

| Harness | 型付きtool名の形 | 観測 |
| --- | --- | --- |
| `dsh-headless` | `mcp__tei__tei_model_catalog` | 2件、shell call 0 |
| `claude-code` | `mcp__tei__tei_model_catalog` | 2件、shell call 0 |
| `step-cli` | `yi-harness-adapter-mcp__tei__tei_model_catalog` | 2件、shell call 0 |

- **E1 達成**（3 Harness）。Step Codeは `<pluginId>__<server>__<tool>` を使うので、
  共通契約は「Harnessごとの綴りを記録し、復号する」形にした。`mcp__*` を標準形に固定しない。
- **E2 達成**: Claude Code と Step Code で `tei_model_catalog` が
  schemaVersion / ok / errorCode / worldFingerprint / sourceIndexFingerprint /
  modelRevision / validationOk の**7欄すべて一致**。
  `tei_validate` は5/5一致（`validationOk` は両routeが報告しない）。
- DSHだけが投影cap（8KiB）で `tei_model_catalog` を截断するので、DSHの当該比較は
  `not shown` として記録する。**サイズではなくJSONが閉じているかで判定する**
  （byte数の閾値で判定していた旧実装は、Claude Codeの14030byte完全JSONを
  誤って比較対象外にしていた。実runで踏んで直した）。
- Claude Codeの当初の挙動（`subtype=success` + `is_error=true`、"You've hit your
  session limit"）は **quota制限**であり、製品の失敗でもtoolの失敗でもない。
  `run:harness-quota-or-rate-limit` として独立に記録する。枠回復後の再実行で
  2件の型付き呼出しが観測された。

### 6.3 許可Root外read（H-A-2 / E3）

canaryを宣言Rootの外に置き、別セッションのprobe Armで読ませた。

| Harness | outcome | attempted | echoed | Verified |
| --- | --- | --- | --- | --- |
| `claude-code`（acceptEdits） | **refused** | true | false | **true** |
| `dsh-headless`（read-only） | **readable** | true | true | false |

- DSHは **Root外を読めた**。`--permission-mode read-only` は書込みを止めるが読取りは通す。
  TEI #3173/#3216/#3228 の予測と一致する。これはfindingであり、PASSでもFAILでもない。
- Claude Codeはcanaryへ**到達して失敗**した（`tool Read` のエラー）。そのときだけ
  `Verified=true` になる。同じ権限設定でも2 Harnessの境界は同じでない、という観測。
- Claude Codeの拒否はこの経路（Read tool + acceptEdits + cwd固定）での話である。
  OS identity/ACLによる隔離証明には昇格させない。

### 6.4 Product横断（H-A-3 / E4）

[evidence/real-pilot-cross-product-2026-11-11.json](evidence/real-pilot-cross-product-2026-11-11.json)、
[evidence/real-pilot-cross-product-claude-2026-11-11.json](evidence/real-pilot-cross-product-claude-2026-11-11.json)

1回のRunで2製品を型付きtoolとして呼んだ。**DSH と Claude Code の両方で成立**。

- DSH: `mcp__tei__tei_model_catalog`, `mcp__tei__tei_validate`, `mcp__sei__resume`
- Claude Code: 同じ3件。shell call 0
- TEIとSEIはidentity語彙を共有しないため、identityの交差比較は行わず、その旨をnoteに残した。

SHOは型付き経路が無い。`SHOReadOnlyTool` は製品CLIを直接起動し、次のように記録した。

- `sho-inspect.cjs inspect <pinned.md>` が exit 0・11018 bytes、`status:indexed`
- product verdict: `completed=true`、`failureCode=""`、`validationPassed=nil`（SHOは検証を評価しない）
- 文書がRoot外なら offer せず `sho.inspect:document-outside-allowed-root`
- MCP spec要求はエラー。**SHOにstdio JSON-RPC面が無い**ためMCP腕は試行していない

SUIは投影していない。`03_Implement/mcp` のstdio server自体は存在するが、同梱の
`node_modules` が **linux-x64 のesbuild** で、Windowsでは起動できない
（`@esbuild/linux-x64` があり `win32-x64` が無い）。依存を入れ直さない限り
`unsupported:environment-esbuild-platform-mismatch` として扱う。
同梱 `package.json` の `engines.node` は `22.x` で、この環境のNodeは v24.19.0 であり、
依存を入れ直しても engine 制約は満たさない。両方を記録する。

### 6.5 Consumer受領（H-A-5 / E6）

[evidence/receipt-readback-2026-11-11.json](evidence/receipt-readback-2026-11-11.json)

Harnessが書いたファイルを別プロセスが読んだ。

- digest形（Arm自身のfinalTextをexpectedにする）: **partial**。Armは要約を書いたため不一致。
  弱い形が complete に到達しないことを実測。
- claim形（**別route** = 製品CLIが返したidentityをexpectedにする）: **partial**。
  `worldFingerprint`・`modelRevision` は存在、`sourceIndexFingerprint` は欠落。
- expectedをproducerの自己申告にしない。自己申告に合わせると自己整合な捏造でもcompleteになる。

### 6.6 Skill対（H-A-4 / E5）

[evidence/four-session-observation-2026-11-12.json](evidence/four-session-observation-2026-11-12.json)、
[evidence/skill-pair-observation-2026-11-11.json](evidence/skill-pair-observation-2026-11-11.json)、
[evidence/skill-pair-step-2026-11-11.json](evidence/skill-pair-step-2026-11-11.json)

割付を実行前に固定し（`S1-H2 → S2-H3 → S3-H3 → S4-H2`）、その順序で4 Sessionを回した。
順序は設計の一部である（Harnessが途中で温まっただけの差をSkillの効果と誤読しないため）。

DSHの4 Session（Skill bytes固定 `sha256:aa3068df...`）:

| Session | 割付 | tools | LoadState |
| --- | --- | --- | --- |
| S1 | H2 | 1 | `unknown`（配置なし） |
| S2 | H3 | 2 | **`loaded`** via `skill` |
| S3 | H3 | 2 | **`loaded`** via `skill` |
| S4 | H2 | 1 | `unknown`（配置なし） |

- ITT: allocated=4、H3 loaded=2/2、H2 clean=2/2 → **2つの適格な対**。
  `skillEffect` は両対とも `"eligibility-confirmed; accuracy not measured"`。
- **採点はしていない**。`notClaimed` に「accuracy or an effect size」
  「4 Sessionからの統計的結論」「ロードしたSkillが回答を改善したこと」を明記した。
  照合票は4 Sessionの生観測と2つの適格対だけを運び、精度の主張は
  [TAI #488](https://github.com/hat47x/tai-pleroma/issues/488) の独立Expectedに残す。
- Harnessごとに適格性が違う: DSH=eligible、`claude-code`=H3が `not-loaded`（SKILL.mdは
  置いたがLoader toolが呼ばれない）、`step-cli`=H3が `not-loaded`
  （`skill-history=discovered` のみ＝配置であってロードでない）。
  **未ロードは「効果なし」ではない**。`ineligibleReasons` に理由を書き、効果を主張しない。
- 実接続で2つの欠陥を発見した。(1) 1つの共有pinを両Armへ渡していたため、Skillを削除した
  H2が `placed=true` と記録された。pinを**Armごと**に取り、H2の配置・H3の未配置を
  失格条件にした。(2) `skill-history` の `discovered` をロードと読んでいた。
  discoveredより強い状態だけをロードとして扱うよう分けた。どちらも契約試験では出ず、
  実runで初めて出た。
- 予算の制約も記録した: OpenRouterの残高が `maxTokens: 65536` を受けられず、最初の4 Sessionは
  `PI_AI_ERROR` で落ちた。`maxTokens: 8000` で通った。**失敗した4 Sessionも ITT の分母に
  残し**、成功分だけを数えていない。

## 7. 未対応・Vendor固有の制約

### Adapterが持たないもの（設計上の未対応）
- **MCP clientの実装**。Adapterは設定の生成と記録だけを行う。各Harnessが持つMCP client
  （DSHの `@deepseek-ai/dsh-mcp-client`、Claude Codeの `--mcp-config`）を使う。
  第二のclientを内蔵すると、契約が禁じている並行機構になる。
- **許可Rootの強制**。AdapterはRootを宣言・記録するだけで、Harnessを拘束しない。
  `RootProbe` は実効を**測る**が、隔離を**実装しない**。隔離のOwnerは
  [TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)／
  [TEI #2515](https://github.com/hat47x/tei-platform/issues/2515)。
- **Skillの正答増分**。配置とLoadの観測まで。`SkillPairObservation` は適格性を判定するが、
  正答の比較は [TAI #488](https://github.com/hat47x/tai-pleroma/issues/488) の独立Expectedの担当。
- **Consumer受領の完全性**。`FileReadback`/`ClaimReadback` は実測できるが、completeに
  到達するには配信物が要求claimをすべて含む必要がある。実測では partial で止まった。
- **第二Harness間のHandoff・Session再開の同等性**。`--session-id`/`--resume` は渡せるが、
  同一cwd・同一Preset・live owner不在等のHarness側条件は検証しない。
- **実Effect・書込み**。投影はread-only面のみ（SEIは `-read-only` を強制）。
- **SHO/SUI**。SHOは `bin/sho-inspect.cjs` の冒頭に「not yet a finalized public CLI
  contract」とあり契約未確定。投影はしたが、SHOにMCP面が無いので型付き経路は作れない。
  SUIはstdio serverが存在するが、同梱依存が linux-x64 esbuild でWindowsでは起動できず、
  `engines.node` も `22.x`（実環境は v24）。どちらも未投影。

### DSH（0.2.2-rc.1）固有
- `--json` は**有界投影**。非`final`の文字列/keyは8KiB、1イベント行は32KiBでcapされ
  `truncated: true` が付く。`final` は無界。監査にSession Log全体は使えない。
  **MCP tool resultもこのcapの対象**であり、大きなmodel catalogは8192byteで切れる。
- `--json` 投影に**model欄がない**。モデル記録は `--dump-config` の宣言値
  （`ProbeEffectiveConfig`）か、呼び出し側のPinだけ。
- `tool_result.status=completed` はToolの復帰であって、内部commandのexit 0ではない。
- `process exit` は `reason.kind == "completed"` のときだけ0。
- 未知の `--session-id` はエラー（空履歴へのsilent fallbackなし）。
- 既定model routeは `deepseek-official` で `DEEPSEEK_API_KEY` が必要。headless profileでは
  `credentials` サービスがdisabledなので、認可は**launching environment のenv var**のみ。
- `session-log-deepseek` は既定 `enabled: true`。公式DeepSeek APIへモデル入力とは別の
  `dsh_session_log` を送出し得る。trialではcaller-supplied `--patch` で切った。
- Windows headlessは `bash-sandbox` がdisabledで `pwsh-sandbox` が使われ、
  read-only sandboxではPowerShellがConstrainedLanguageになり
  `[Console]::OutputEncoding` 設定が失敗してstderrが化ける。
- launcher flag（`--profile`, `--patch`）はapp flag（`--json` 等）より**前**に行く必要がある。
  逆順だと `unknown option '--patch'` でturn前にexit 1し、Harness失敗と同じに見える。
- **新しいentryはid指定のpatchで追加できない**。`entry "<id>" not found` で失敗する。
  追加は `- insert:` 形式（`--dump-config-schema` の `$defs.patch`）が必須。
- **`--permission-mode read-only` はRoot外readを止めない**。実測で宣言Root外のcanaryを
  読めた。read-onlyは書込みを止めるが読取りは通す。この環境を隔離済みと呼ばない。

### Claude Code（2.1.302）固有
- `--tools` はbuilt-in toolのみを絞る。**MCP登録toolは広告一覧に残り到達可能**。
  実観測で `--tools "Bash,Read,Glob,Grep"` でも `mcp__claude_ai_*` が24件広告された。
- `--permission-prompts none` を付けないと、promptが必要な操作はすべて拒否され
  tool callなく終わる。無人read-only実行では `--permission-mode` の設定が実質的な前提。
- Session IDはUUID。`--session-id <uuid>` は新規、`--resume <id>` が継続。
- `--print --output-format stream-json` はコスト（`total_cost_usd`）とusageを返す。
  DSHの投影にはない。
- `rate_limit_event` など本decoderがモデル化しないevent型があり
  `harness-unknown-event-types` として警告される。
- `result` eventは `subtype="success"` と `is_error=true` を同時に返し得る。
  実runで "You've hit your session limit" がこの形だった。subtypeだけで
  `run=completed` と判定してはならない。

### Step Code（0.1.7）固有
- 実行形は `step --approve --mode json -p`。終端は `agent_settled` で、
  exit 0だけでは完了と言えない。`isError` のtool resultは `run=error` として扱う。
- **Tool名の形が2つある**。`~/.stepcode/config.toml` の `[mcp_servers.<name>]` 経由は
  `<server>__<tool>`、plugin宣言経由は `<pluginId>__<server>__<tool>`。
  `mcp__` 接頭辞は無い。`StepToolName` が両方を復号する。
- **plugin宣言の置き場所**は `<cwd>/.stepcode/plugins/<safe-name>/step.plugin.json`
  で、projectを `--approve` で信頼する必要がある。`step install <dir>` は
  marketplace facadeで、manifestの `entry` は「recorded but not loaded」。
  MCP宣言だけなら config.toml か project-scoped plugin が効く。
- **`config.toml` はBOMを受け付けない**。BOM付きだと
  "only letter, numbers, dashes and underscores are allowed in keys" で拒否される。
- 無人でMCP toolを呼ぶには `--approval-mode auto --non-interactive-approval allow` が要る。
  既定では「workspaceを変更し得る」と判定され、toolが拒否される。
- Skillは `kind:"skill", stage:"discovered"` だけが観測される。活性化stageは無いので、
  `--skill` を渡しても `skill:load-not-observed` を報告する。
- `--mode json` はrun logであり、永続session transcriptとは別物。

## 8. 使い方

```bash
cd integrations/harness-adapter
go test ./... -count=1                                   # 契約試験（外部接続なし）

go build -o /tmp/harness-adapter ./cmd/harness-adapter
/tmp/harness-adapter -task task.json -adapters direct-control -out report.json
/tmp/harness-adapter -task task.json -real \
  -adapters dsh-headless,step-cli,claude-code,direct-control -out report.json
```

Task JSONは `Task` 型そのまま。Prompt・Pins・ContextRefs・Tools・Skills・Limitsを持つ。

## 9. 変更するときの規則

- `ContractVersion` を上げるのは、欄の**意味**が変わったときだけ。欄追加は上げない。
- `AllCapabilities()` は閉集合。増やすなら定数を足してこの文書も更新する。
- Adapterを足すときは `Adapter` interfaceを実装し、`Probe` は**必ず実プロセスを踏む**。
  `Reachable=true` を実行なしで返してはならない。
- 実接続テストは `realconnect*_test.go` に閉じ、通常buildから除外する。
- Tool名の復号はHarnessごとに別関数にする。`mcp__*` を全Vendorの標準形に固定しない。
