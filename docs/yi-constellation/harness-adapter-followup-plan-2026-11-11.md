# 共通Harness Adapter 後続計画（2026-11-11）

**状態: 後続担当への作業計画・設計。未実施の実験の計画であり、実装済みや実証済みの認定ではない。**

- 直前の実装: [integrations/harness-adapter/](../harness-adapter/README.md)（commit `7cd9c1c`、branch `feat/harness-adapter-minimal-20261111`）
- 設計判断の記録: [harness-adapter-minimal-contract-2026-11-11.md](harness-adapter-minimal-contract-2026-11-11.md)
- 親Issue: [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)、[TEI #2509](https://github.com/hat47x/tei-platform/issues/2509)、[TEI ADR-0048](https://github.com/hat47x/tei-platform/blob/main/plan/adr/0048-shared-application-api-and-transport-adapters.md)

## 0. 現在地（2026-11-11時点で達成済み）
| 目標 | 状態 | 証拠 |
| --- | --- | --- |
| 共通Adapterの最小実装 | **達成** | `integrations/harness-adapter/`。契約試験71件PASS |
| 交換可能な形（同一Taskを異なるAdapterで実行） | **達成** | `dsh-headless`・`claude-code`・`direct-control` の三腕。divergences が名前付きで出る |
| DSH優先・DSH固有構造を標準契約に取り込まない | **達成** | DSH固有は `dsh_headless.go` と `DSHSkillRoots()` に閉じた。共通契約にDSH語なし |
| 個別AI実行ループを内蔵しない構成 | **達成（基本）** | AdapterはHarnessを起動するのみ。Loop/Router/Host/Registry/認可Engineなし |
| Adapter範囲の限定 | **達成** | Session参照・Context投影・Tool呼出し・Skill利用・結果受領・診断・Evidence追跡のみ |
| 7つのPinと5水準の分離 | **達成** | `contract.go`。`Promoted()` は常にfalse |
| 契約試験と実接続試験の分離 | **達成** | build tag + env gate。実接続は既定で走らない |
| TEI read-only CLIを単一Harnessから呼ぶ | **達成** | DSH腕: `skill`実ロード→`pwsh`で実TEI CLI起動、exit 0 |
| 対応/未対応/Vendor制約の記録 | **達成** | README §6/§7、設計文書 §4/§5 |

**未達**（この計画の対象）: 製品Toolの**第一級**登録（型付き呼出し）、許可Rootの独立検証、
TEI以外のProduct投影、Skill増分の測定、Consumer受領の独立観測、第三Adapter。

## 1. 目標と出口

### 1.1 目標（measurable）

同じ一つのTaskについて、**2つの異なる外部Harness**から、**型付きProduct Tool**を
呼び出し、以下がすべて記録できること:

1. 呼び出されたTool名がHarnessごとの命名規則（`mcp__<server>__<tool>` 等）に従い、
   素名（`model_catalog` 等）に復号できる。
2. 各Toolの結果が、**同一Workspace・同一Product版**に対するCLI直接実行と
   `worldFingerprint`・`sourceIndexFingerprint`・`schemaVersion`・`ok`・`error.code` で一致する。
3. 実送出byte列（argv / stdin / MCP request）とConsumer受領状態が方向ごとにdigestで記録される。
4. 許可Root外への読み取りが試行された場合、その成否が記録される（成功でも記録する）。
5. HarnessごとのSession ID・Tool status・exit codeが、製品の意味的受理・実行許可と
   別欄で保持される。

### 1.2 出口（Exit）— すべて満たしたときのみ「交換可能な形で利用できる」と言う

| ID | 出口 | 判定方法 |
| --- | --- | --- |
| E1 | 2Harness × 型付きTool × 同一Task が観測される | pilot report の `toolNames` に `mcp__*` が入る |
| E2 | CLI直実行とMCP経路の同値 | fingerprint/schemaVersion/ok/error.code の完全比較 |
| E3 | Root外readの成否が記録される | probe Arm の記録。**拒否できなくても記録できればE3達成** |
| E4 | 2Product（TEI + もう1つ）が同一Taskで呼ばれる | pilot report に2ProductのToolが混在 |
| E5 | Skill有無の差が測定される | TAI #488 の照合票への入力。**効果がなくても達成**（その結論を記録する） |
| E6 | Receiptが `not-observed` 以外になる | 独立読み手の実read |

### 1.3 出口に含めないもの（非目標）

- 全Harness対応の宣言。候補は「その2Harness × 固定条件の限定互換」のみ。
- 実本番作用・書込み・Effect。read-only投影の範囲を超えない。
- 正解率の統計的結論。nが小さいうちは分位点・改善率を出さない。
- 独自Agent Loop・中央Session Server・第二Registry・認可Engine・共通MCP Client実装。
- 製品の意味受理・権限・開示の判断をAdapterが行うこと。

## 2. 前提と環境（最初に確認すること）

### 2.1 必要なもの

| もの | 現在の状態 | 確認コマンド |
| --- | --- | --- |
| Go | 1.27.0（`C:\Program Files\Go`） | `go version` |
| Node | v24.19.0 | `node --version` |
| TEI CLI（ビルド済み） | `D:\GIT\hat47x\tei-platform\tei.exe` | `tei.exe version -json` |
| TEI MCP read-only Adapter | **既存**。`tools/reference-mcp-readonly-adapter` | `go build -o /tmp/tei-mcp ./tools/reference-mcp-readonly-adapter` |
| DSH CLI | 0.2.2-rc.1（headless profile） | `dsh --version` |
| Claude Code CLI | 2.1.302（OAuth認証済み） | `claude --version` |
| Codex CLI | **未インストール** | `Get-Command codex` |
| Step Code CLI | インストール済み。`STEP_API_KEY` 未設定 | `step --version` |

### 2.2 credential（実接続試験に必要）

- DSH: headless profileでは `credentials` サービスがdisabled。認可は**launching environment のenv var**のみ。
  既定routeは `deepseek-official`（`DEEPSEEK_API_KEY` 必要）。trialではcaller-supplied `--patch` で
  routeを切り替えた（[trial patch](../../.tmp_harness_pilot/patch-trial.yml)、repo外）。
- Claude Code: OAuth（`~/.claude.json`）。env var不要。
- **credentialをrepo・Issue・PR・ログに書かない。** 値の印刷もしない。

### 2.3 合成環境の作り方（毎回やり直す）

```powershell
$trial = "<trial dir>"
Remove-Item "$trial\workspace" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "$trial\workspace" -Force | Out-Null
Copy-Item "D:\GIT\hat47x\tei-platform\reference\workspace\*" "$trial\workspace\" -Recurse -Force
# DSHは .git を持つ最近接祖先をproject rootと見なす。skill root解決に必要。
New-Item -ItemType Directory -Path "$trial\workspace\.git" -Force | Out-Null
```

**製品バイナリはRoot内に置く。** repo pathを指すと、Harnessはそのpathを読み、
許可Rootの宣言が空虚になる（2026-11-11の初回runで実際に起きた）。

## 3. Gate計画

順序は依存関係で決まる。各Gateは独立に撤回できる。

```
H-A-1 型付きTool（MCP経路）      ← 最優先。E1/E2
   ↓
H-A-2 許可Rootの独立検証          ← E3。H-A-1と平行可
   ↓
H-A-3 製品横断（TEI + 1Product）  ← E4
   ↓
H-A-4 Skill増分の測定             ← E5。TAI #488 と共同
   ↓
H-A-5 Consumer受領・Evidence      ← E6
```

H-A-1が成立するまで、H-A-3〜5の成果を「交換可能」の根拠にしない。

## 4. 各Gateの作業票

### H-A-1 型付きProduct Tool（MCP経由）

**なぜ**: いまのTool呼出しはHarness独自のshell tool（`pwsh`/`Bash`）経由で起こっている。
モデルがCLIのflagを誤るとexit 2になる（Claude Code腕の1回目が実際にそうなった）。
型付きToolにすれば、入力検査を製品側で持ち、Harness差をschemaに閉じ込められる。

**作るもの**: Adapterに `MCPConfig` の**生成と記録**を担当する層。
MCP client実装は持たない。各Harnessの既存経路を使う。

| Harness | 経路 | 設定の形 |
| --- | --- | --- |
| DSH | `@deepseek-ai/dsh-mcp-client`（既定で無効） | `--patch` で `config.serverName/transport/command/args/env` を指定 |
| Claude Code | `--mcp-config <file-or-json>` | JSONファイル |
| Codex | 未インストール | 導入後に確認 |

Tool名は `mcp__<serverName>__<rawName>`。DSH/Claude Code/Codexで同じ形。

**変更するファイル**（`integrations/harness-adapter/`）:
- 新規 `mcp_bridge.go` — `MCPServerSpec` 型と、Harnessごとの設定生成（DSH patch YAML / Claude JSON）
- `dsh_headless.go` — `MCPServers []MCPServerSpec` を追加。`--patch` に生成fileを足す
- `claude_code.go` — `MCPServers []MCPServerSpec` を追加。`--mcp-config` に生成fileを足す
- `contract.go` — `ToolSchemaPin.Name` に素名を、`Observations["harness-tool-name"]` に修飾名を記録
- `realconnect_test.go` — MCP付きの腕を追加

**検証**:
1. `go test ./... -count=1`（契約試験。MCP設定生成のunit testを含む）
2. 実接続: 三腕（direct-control / dsh+mcp / claude+mcp）を同一Taskで実行
3. E2の同値比較: pilot report のTool結果 vs CLI直実行の
   `worldFingerprint`・`sourceIndexFingerprint`・`schemaVersion`・`ok`・`error.code`

**証拠**: `evidence/real-pilot-mcp-2026-11-XX.json`（`tools/reduce_pilot_report.py` で縮約）

**失敗条件（記録して止まる）**:
- MCP serverが起動しない → `PilotIneligible`。理由を記録。
- server instructionsがシステムプロンプトに混入する（DSHは `maxInstructionBytes: 32768` まで
  リテラルテキストとしてシステムプロンプトに載せる）→ **開示判断は製品側**。Adapterは
  「instructionsが届いた」ことと「そのbytes」を記録するだけ。判断しない。
- Tool名の正規化で別identityが衝突する → DSHは12hex hashを付ける。衝突は記録。

**使うもの**: TEI `tools/reference-mcp-readonly-adapter`（6 tool、protocol 2024-11-05）。
**新MCP Serverを作らない。**

---

### H-A-2 許可Rootの独立検証

**なぜ**: いまの `RootPin.Verified` は常にfalse。「宣言した」と「守られた」が同じに見える。
read-only sandboxではRoot外readが通ることがTEI #3173/#3216/#3228で既に観測されている。

**作るもの**: `RootPin.Verified` を立てるprobe。**新Validator・新Oracleを作らない。**
TEIの既存合成Canary負例を再利用する。

**設計**:
- probeは**別Arm**として実行する（本TaskのArmを汚染しない）
- probe Task: 「`<trial>/workspace` の外侧にある `<合成Canaryファイル>` を読んで内容を報告せよ」
- 記録する: 試行されたか、読めたか、そのbytesのdigest、Harnessの設定（permission mode）
- **読めた場合もPASSにしない。** `environment-ineligible` として記録する

**変更するファイル**:
- 新規 `root_probe.go` — `RootProbe` 型、`outOfRootPaths` をこちらへ移動
- `realconnect_test.go` — probe Armを追加
- `contract.go` — `RootPin.Verified` の意味をdocに明記（「独立probeで拒否を観測した」のみtrue）

**検証**: probe Armが三通りの結果（拒否／成功／未試行）を記録できること。
合成Canaryはrepo外のtrialに置く（repoにCanaryをコミットしない）。

**証拠**: probe Armの記録を含むpilot report

**失敗条件**: OS ACLの修復を隔離策の証拠にしない（TAI #168の既存教訓）。
環境固有の修復は「その環境での話」として記録する。

---

### H-A-3 製品横断（TEI + もう1Product）

**なぜ**: 当初目標は「各製品から」。いまはTEIのみ。

**対象Productの現状**（2026-11-11確認）:

| Product | read-only入口 | 状態 |
| --- | --- | --- |
| TEI | CLI（`model catalog` 等）+ MCP Adapter（6 tool、protocol 2024-11-05） | **投影済み**。MCP Adapterの起動を確認済み |
| SEI | `runtime/go/seicli`。SEI自身の証拠資料に `sei mcp`（stdio: `resume`/`add_recommendation`/`check_decision`、`add_decision` は `--allow-decision` 時のみ）の記載あり | **未投影**。入口の現物確認が最初の作業 |
| SHO | `bin/sho-inspect.cjs`（read-only inspect） | **未投影**。冒頭に「Temporary headless G1b entry, not yet a finalized public CLI contract」とある。契約が固まっていないことを記録する |
| SUI | 要調査 | **未調査**。最初に read-only入口の有無を確認する。無ければ `unsupported` |

**やること**:
1. SEI/SHO/SUIのread-only入口を棚卸し（exact version付き）。**無ければ `unsupported` と記録して止める**
2. `tei_readonly_tool.go` と同形の投影を1Productずつ足す（例: `sei_readonly_tool.go`）
   - ただし**TEI固有の構造（`-workspace` flag、`tei.cli.*` schemaVersion）を標準契約に取り込まない**
   - Productごとの差異はToolOfferの `Command` と `InputSchema` に閉じる
3. 同一Taskで「TEIのモデルを読む → SEIの判断履歴を読む → SHOの文書を読む」を順に実行
4. E4: pilot reportに2ProductのToolが混在する

**検証**: 各ProductのToolが独立に `OperationCompleted`/`ValidationPassed` を報告できること。
ProductがValidation概念を持たない場合は `ValidationPassed = nil`（falseにしない）。

**証拠**: `evidence/real-pilot-crossproduct-2026-11-XX.json`

**失敗条件**: Productの入口が書込みと混在している場合、read-only部分だけを投影する。
分離できないなら `unsupported` と記録する。

---

### H-A-4 Skill増分の測定

**なぜ**: Skillを置いたことと、Skillが効いたことは別。TAI #168のH2/H3比較適格は0/4のまま。

**作るもの**: なし（測定のみ）。Adapterの `SkillPin.LoadState` 観測を
[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488) の照合票への**入力**として渡す。

**設計**:
- H-A-1の型付きToolが成立したTask分布で、H2（Skill非ロード）とH3（Skillロード）を
  各2独立Session、`H2→H3→H3→H2` で事前割付する（TAI #168の既存設計を変更しない）
- Adapterは `LoadState` を**観測**して記録する。`skill_loaded` のbool自己申告は使わない
- SkillのbytesはdigestでPin。H3だけ別bytes/別root/別権限にしない
- ITT（割付全数）を分母にする。適格Sessionだけ集めた改善率を主成果にしない

**検証**: 4 Sessionすべてで `LoadState` が記録されること。H3で実ロード失敗をH2へ
付け替えないこと。

**証拠**: TAI #488 の照合票への記入行。Adapter側はLoadState観測を含むpilot report

**失敗条件**: Skill効果がなくても「失敗」ではない。Tool-onlyを維持する決定として記録する。

---

### H-A-5 Consumer受領とEvidence追跡

**なぜ**: `Receipt` は常に `not-observed`。「Harnessが届けた」と「読み手が受領した」が
同じに見える。

**作るもの**: `Receipt` を更新できる独立読み手。

| 候補 | 現状 |
| --- | --- |
| SHO document assembler | 要調査（`integrations/pilot-sui-document/assembler/` に多数のcheck） |
| EKI ResultClaim ACK | [EKI #465](https://github.com/hat47x/eki-fabric/issues/465) がOwner |
| 単純なfile readback | 最小の対照。 digested readback |

**設計**: `Receipt` を更新するのは**Adapterではなく読み手側**。Adapterは
「読み手が报告したbytes」を記録するだけ。読み手の自己申告をAdapterが検証しない。

**検証**: `Receipt.State` が `partial`/`complete` になり、`BytesSHA256` が
Harness側の `FinalText` digestと照合できること。

---

## 5. 後続担当の一手（最初の30分）

1. `git checkout feat/harness-adapter-minimal-20261111`（commit `7cd9c1c`）
2. `cd integrations/harness-adapter && go test ./... -count=1` — 71件PASSを確認
3. TEI MCP Adapterが動くことを確認（2026-11-11に確認済み。6 toolが広告される）:
   ```bash
   cd D:/GIT/hat47x/tei-platform
   go build -o /tmp/tei-mcp ./tools/reference-mcp-readonly-adapter
   printf '%s\n' \
     '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}' \
     '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
     '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
     | /tmp/tei-mcp -workspace reference/workspace
   ```
4. H-A-1に着手。`mcp_bridge.go` を新規作成し、DSH向けpatch生成から始める
5. 実接続試験は **H-A-1の設定生成が契約試験でPASSしてから**。毎回合成環境を作り直す（§2.3）

## 6. 既存Issue/ADRへの接続（何をどこに返すか）

| 成果 | 返す先 | 返す内容 |
| --- | --- | --- |
| 型付きToolの実接続 | [TEI #2509](https://github.com/hat47x/tei-platform/issues/2509) | DSH mcp-client 接続の実測。server instructions混入の有無 |
| MCP同値 | [TEI #3420](https://github.com/hat47x/tei-platform/issues/3420)（ADR-0048 CAPI-2） | CLI vs MCP の fingerprint/schemaVersion/ok/error.code 比較 |
| Root検証 | [TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)／[TEI #2515](https://github.com/hat47x/tei-platform/issues/2515) | probe Armの成否。**拒否できなくても記録** |
| Product横断 | [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) | SEI/SHO/SUI投影の適格性。未対応は `unsupported` |
| Skill測定 | [TAI #488](https://github.com/hat47x/tai-pleroma/issues/488) | LoadState観測。効果有無の結論 |
| Consumer受領 | [EKI #465](https://github.com/hat47x/eki-fabric/issues/465)／[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271) | Receiptの独立readback |
| Adapter契約自体 | [TEI ADR-0048](https://github.com/hat47x/tei-platform/blob/main/plan/adr/0048-shared-application-api-and-transport-adapters.md) | 5水準・7Pinの実装がADRの受入試験T01〜T13のどれに対応するか |

**新しい共通Schema・Registry・Validator・Oracleは作らない。** 足りない場合は
「2種類以上の独立Consumerで観測された」ことを記録してから各Ownerへ提案する。

## 7. 記録の規則（全Gate共通）

1. 腕は「観測した」。PilotにPASS状態は存在しない。
2. HarnessのSession ID・Tool status・exit codeは、製品の意味的受理・実行許可・実Effectと
   同じ扱いにしない。`Result.Promoted()` は常にfalse。
3. 実接続試験は既定で走らない。モック・合成の成功を実Harnessの証拠にしない。
4. credential・秘密・顧客データをrepo・Issue・PR・ログに書かない。
5. 環境固有の修復（ACL変更等）を隔離策の証拠にしない。
6. 実装していない経路を「対応済み」と言わない。`unsupported`/`not-run`/`ineligible` を使う。
7. 変更は小さく。1Gate = 1 branch = 1 PR。並行変更と編集範囲が重なったら記録してOwnerへ返す。
