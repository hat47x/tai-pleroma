# 共通Harness Adapter（最小実装）

外部AIハーネス（DSH、Claude Code、Codex等）から、YI Constellation各Productの能力を
**交換可能な形で**呼び出すための薄いAdapterと、その契約試験。

- 状態: **PoC実装・限定実証**。Adapter単体の契約試験はCIで常時実行できる。実Harness接続は
  `-tags realconnect` と `HARNESS_ADAPTER_REAL=1` の両方が必要で、既定では実行されない。
- 親Issue: [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)（Harness間適合）、
  [TEI #2509](https://github.com/hat47x/tei-platform/issues/2509)（DSH固有実証）、
  [TEI ADR-0048](https://github.com/hat47x/tei-platform/blob/main/plan/adr/0048-shared-application-api-and-transport-adapters.md)（共通Application API）。
- 設計判断の記録: [harness-adapter-minimal-contract-2026-11-11.md](../../../docs/yi-constellation/harness-adapter-minimal-contract-2026-11-11.md)

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
| `claude-code` | `claude -p <prompt> --output-format stream-json --verbose [flags]` | **実接続済み**（Claude Code 2.1.302, Windows） |
| `direct-control` | モデルなし。Taskが宣言した製品Toolを決定的に実行 | **実装済み**。比較の対照腕 |
| `scripted-*` | 契約試験専用の二重結合。`FakeRunner` に再生させる | **契約試験のみ**。製品ではない |

`Registry` は呼び出し側が明示的に構築するプロセス内の名前解決。発見も読み込みもしない。
未登録のAdapter名を要求した場合は、登録済み一覧を出して**黙って別Adapterにフォールバックしない**。

## 4. TEI read-only Tool投影

`TEIReadOnlyTool` はTEI CLIの**既存**read-onlyカタログ（`tei commands`、
scope `selected-read-only-commands`）からの投影。新しいAPIを作らない。

- offerする: `version`, `model catalog`, `model overview`, `model locate`*, `workspace-files`,
  `inspect`*, `trace`*, `source-index`, `knowledge-context`*, `validate`
  （*はSubject参照を投影が持たないため offer されず、`unsupported` として報告される）
- offerしない: `view`, `self-build`, `dbcheck`, `artifacts`, `grants` など書込み・Effect系。
  `argvFor` が它们を組めないことで構造的に保証する。
- `-workspace` は投影が持つRootのみを指す。Toolは `AllowedRoots` にその論理名を宣言する。

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

## 6. 実接続で確認できたこと（2026-11-11）

証拠: [evidence/real-pilot-2026-11-11.json](evidence/real-pilot-2026-11-11.json)
（完全版はtrial directory。本repoのは結果bodyをdigestに置き換えた縮約版）

同一Task・同一Pinで三腕を実行:

| 腕 | transport | run | exit | tool calls | 観測 |
| --- | --- | --- | --- | --- | --- |
| `direct-control` | delivered | completed | n/a | 6 | 全Tool exit 0。製品envelopeから Operation/Validation を分離記録 |
| `dsh-headless` | delivered | completed | 0 | 5 | `skill` toolでProduct Skill実ロード、`pwsh`で実TEI CLI起動 |
| `claude-code` | delivered | completed | 0 | 2 | `Bash`で実TEI CLI起動。1回目は `-workspace` 不足で exit 2、2回目で成功 |

- divergences（自動算出）: `exit-code`, `session-state`, `tool-count`, `tool-names`, `unsupported`
- **同じTaskを異なるAdapterで実行でき、差分は名前付きで報告される**。差分は「非互換」の意味ではない。
- DSH腕: `model catalog` の結果が8192byteで投影截断 → `result:projection-truncated` を報告
- Claude Code腕: Skill Loader toolの呼出しが観測されず → `skill:load-not-observed` を報告
- 両腕とも宣言Root外のpath到達は0（バイナリをRoot内に置いた条件）

## 7. 未対応・Vendor固有の制約

### Adapterが持たないもの（設計上の未対応）
- **製品Toolの第一級登録**。DSH/Claude Codeへ型付きToolを直接登録する経路がない。
  実観測ではTool呼出しはHarness独自のshell tool（`pwsh`/`Bash`）経由で起こった。
  MCP Server Adapter（TEI側）またはHarness Pluginが次の候補。
- **許可Rootの強制**。AdapterはRootを宣言・記録するだけで、Harnessを拘束しない。
  読取り隔離の実証は [TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)／
  [TEI #2515](https://github.com/hat47x/tei-platform/issues/2515) のOwner。
- **Skillの自動発見・選択の効果測定**。配置とLoadの観測まで。正答への増分は未測定。
- **Consumer受領の独立観測**。`Receipt` は常に `not-observed`。
- **第二Harness間のHandoff・Session再開の同等性**。`--session-id`/`--resume` は渡せるが、
  同一cwd・同一Preset・live owner不在等のHarness側条件は検証しない。
- **実Effect・書込み**。read-only投影のみ。

### DSH（0.2.2-rc.1）固有
- `--json` は**有界投影**。非`final`の文字列/keyは8KiB、1イベント行は32KiBでcapされ
  `truncated: true` が付く。`final` は無界。監査にSession Log全体は使えない。
- `--json` 投影に**model欄がない**。モデル記録は `--dump-config` の宣言値
  （`ProbeEffectiveConfig`）か、呼び出し側のPinだけ。
- `tool_result.status=completed` はToolの復帰であって、内部commandのexit 0ではない。
- `process exit` は `reason.kind == "completed"` のときだけ0。
- 未知の `--session-id` はエラー（空履歴へのsilent fallbackなし）。
- 既定model routeは `deepseek-official` で `DEEPSEEK_API_KEY` が必要。headless profileでは
  `credentials` サービスがdisabledなので、認可は** launching environment のenv var**のみ。
- `session-log-deepseek` は既定 `enabled: true`。公式DeepSeek APIへモデル入力とは別の
  `dsh_session_log` を送出し得る。trialではcaller-supplied `--patch` で切った。
- Windows headlessは `bash-sandbox` がdisabledで `pwsh-sandbox` が使われ、
  read-only sandboxではPowerShellがConstrainedLanguageになり
  `[Console]::OutputEncoding` 設定が失敗してstderrが化ける。
- launcher flag（`--profile`, `--patch`）はapp flag（`--json` 等）より**前**に行く必要がある。
  逆順だと `unknown option '--patch'` でturn前にexit 1し、Harness失敗と同じに見える。

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

## 8. 使い方

```bash
cd integrations/harness-adapter
go test ./... -count=1                                   # 契約試験（外部接続なし）

go build -o /tmp/harness-adapter ./cmd/harness-adapter
/tmp/harness-adapter -task task.json -adapters direct-control -out report.json
/tmp/harness-adapter -task task.json -real \
  -adapters dsh-headless,claude-code,direct-control -out report.json
```

Task JSONは `Task` 型そのまま。Prompt・Pins・ContextRefs・Tools・Skills・Limitsを持つ。

## 9. 変更するときの規則

- `ContractVersion` を上げるのは、欄の**意味**が変わったときだけ。欄追加は上げない。
- `AllCapabilities()` は閉集合。増やすなら定数を足してこの文書も更新する。
- Adapterを足すときは `Adapter` interfaceを実装し、`Probe` は**必ず実プロセスを踏む**。
  `Reachable=true` を実行なしで返してはならない。
- 実接続テストは `realconnect_test.go` に閉じ、通常buildから除外する。
