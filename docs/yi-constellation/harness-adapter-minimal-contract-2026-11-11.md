# 共通Harness Adapterの最小契約（2026-11-11）

**状態: 設計判断と最小実装の記録。PoC。製品の要求受理・Owner採用・実本番運用の証明ではない。**

- 実装: [integrations/harness-adapter/](../harness-adapter/README.md)
- 親Issue: [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)、
  [TEI #2509](https://github.com/hat47x/tei-platform/issues/2509)、
  [TEI ADR-0048](https://github.com/hat47x/tei-platform/blob/main/plan/adr/0048-shared-application-api-and-transport-adapters.md)、
  [TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)、
  [TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)／[TEI #2515](https://github.com/hat47x/tei-platform/issues/2515)
- 位置づけ: [TAI Draft #270 SK-02/03](https://github.com/hat47x/tai-pleroma/pull/270) の後続、
  [TAI #168 の2026-11-10追補](https://github.com/hat47x/tai-pleroma/issues/168)（製品横断Session導線）の
  **実装側の最小単位**。

## 1. 解く問い

各Productが個別のAI実行ループを内蔵するのではなく、**外部HarnessとのSessionを共有し、
必要な製品ContextとToolを限定的に提供する**。そのとき、Harnessを交換しても
Task・Source・Skill・Tool・許可Root・実送出bytes・Consumer受領の対応が崩れない
最小の契約は何か。

DSHを初期実証対象として先に実装したが、**DSH固有の構造をTEIやTAIの標準契約に取り込まない**。
DSH固有の事項（Profile/Patch/Skill root/Session Log）はAdapter内部か
Adapterごとの設定として閉じ、共通契約の欄にしない。

## 2. 採択した判断

| 判断 | 内容 | 採用しない案 |
| --- | --- | --- |
| Adapterは薄い | Session参照・Context投影・Tool呼出し・Skill利用・結果受領・診断・Evidence追跡のみ | 中央Agent Host、第二Registry、認可Engine、独自Agent Loop |
| Taskが交換単位 | 同一Taskを任意の適合Adapterで実行できる | 会話履歴の移植、Harness固有Packet |
| Pinは七つに分ける | Source/Model/Skill/Tool schema/許可Root/実送出bytes/Consumer受領 | 一つの「コンテキスト」に畳む |
| 成否は五水準 | transport/run/harness status/product exit/product verdict | 単一 `ok` |
| 観測は判定しない | Pilotの腕の状態は `observed`/`ineligible`/`errored`/`not-run`。PASSは存在しない | 適格腕だけ集めた成功率 |
| 契約試験と実接続試験を分ける | 既定は外部接続なし。実接続はbuild tag＋env gate | モックの成功を実接続の証拠にする |
| 製品Toolは既存面の投影 | TEI read-only CLIカタログからの投影。新APIを作らない | AI向けの別意味API |
| 対照腕を残す | `direct-control`（モデルなし決定論）を常に含める | Harnessあり／なしの比較をしない |

## 3. 実装の骨格

```
integrations/harness-adapter/
├── contract.go            # Task/Pins/Result/Session/Diagnostic と closed Capability set
├── runner.go              # ExecSpec/Runner  seam（ProcessRunner / FakeRunner）
├── dsh_headless.go        # DSH headless adapter + NDJSON投影decoder
├── claude_code.go         # Claude Code print adapter + stream-json decoder
├── direct_control.go      # 決定的対照腕 + 製品envelopeの Operation/Validation 分離
├── scripted_adapter.go    # 契約試験専用の二重結合
├── tei_readonly_tool.go   # TEI read-only CLI投影（allowlist付きargv構築）
├── skill_placement.go     # Product Skill配置とdigest。Load状態は三値
├── registry.go            # 名前解決（発見しない）
├── pilot.go               # 同一Taskを複数Adapterで実行し divergences を名前付きで報告
├── realconnect_test.go    # 実接続試験（build tag + env gate）
└── cmd/harness-adapter/   # CLI
```

## 4. 実証結果（2026-11-11、限定）

同一Task・同一Pinで三腕を実行し、観測を記録した（証拠: `evidence/real-pilot-2026-11-11.json`）。

| 腕 | run | exit | tool calls | 観測できたこと |
| --- | --- | --- | --- | --- |
| `direct-control` | completed | n/a | 6 | 全Tool exit 0。Operation/Validation 分離 |
| `dsh-headless` | completed | 0 | 5 | `skill` toolでProduct Skill実ロード。`pwsh`で実TEI CLI起動 |
| `claude-code` | completed | 0 | 2 | `Bash`で実TEI CLI起動。1回目 `-workspace` 不足でexit 2、2回目成功 |

**確認できた**: 同一Taskを異なるVendorのAdapterで実行でき、差分は
`exit-code`, `session-state`, `tool-count`, `tool-names`, `unsupported` として名前付きで出る。

**確認できなかった**（NOT RUN）:
- 正答の独立採点。Skillの増分効果。二Harness間のHandoff同等性。
- 実OS読取り隔離（G0）。実ネットワーク送出境界。実Effect・Consumer受領。
- 製品Toolの第一級登録（MCP/Plugin経由）。許可Rootの強制。

## 5. 実証中の発見（設計を変えたもの）

1. **許可Rootと到達bytesは別**。最初のrunでは製品バイナリをリポジトリpathで指し、
   DSH腕はそのpathを読んだ。`--permission-mode read-only` は止めなかった。
   以後、trialはバイナリをRoot内に置き、Root宣言が検証可能にした。
   このrunでは両腕ともRoot外到達0。
2. **DSHの`--json`投影は監査に使えない**。`model catalog` の結果が8192byteで截断され
   `truncated: true` が付いた。投影は完全証拠ではない。
3. **DSH投影にmodel欄がない**。モデル記録は`--dump-config`の宣言値か呼び出し側のPinだけ。
4. **Claude Codeの`--tools`はMCP toolを絞らない**。`--tools "Bash,Read,Glob,Grep"` でも
   `mcp__claude_ai_*` が24件広告・到達可能だった。
5. **Skillは配置≠Load**。DSHは`skill` toolで実ロードした。Claude CodeはLoader toolの
   呼出しが観測されず `skill:load-not-observed`。SKILL.mdだけ置くと、SKILL.mdが参照する
   `references/read-only-model-investigation.md` が存在せず、DSH腕の`read`が
   `not found` になった（配置物の閉包がProduct Skill全体ではないことの実証）。
6. **launcher flagの順序**。DSHで`--patch`を`--json`の後に置くと
   `unknown option '--patch'` でturn前にexit 1し、Harness失敗と同じに見える。

## 6. 次の一手（優先順）

1. **製品Toolの第一級登録**。TEI側のMCP Server Adapter（[ADR-0048](https://github.com/hat47x/tei-platform/blob/main/plan/adr/0048-shared-application-api-and-transport-adapters.md)の既存4 read-only操作）を
   DSH/Claude CodeのMCP clientから接続し、shell経由ではなく型付き呼出しで同じTaskを実行する。
   AdapterにMCP clientを内蔵するのではなく、**各Harnessの既存MCP経路を使う**。
2. **許可Rootの独立検証**。`RootPin.Verified` を立てるprobe（Root外readの拒否観測）を
   [TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)／[TEI #2515](https://github.com/hat47x/tei-platform/issues/2515) と共有する。
3. **Skill増分の測定**。[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488)の照合票に、
   本Adapterの`LoadState`観測を入力として渡す。新Validatorは作らない。
4. **Consumer受領の独立観測**。`Receipt`を`not-observed`以外にできる読み手を用意する。
5. **第三Adapter**。Codex CLI（`codex exec`）は本環境に未インストールのため未実装。
   導入されたら同じ`Adapter` interfaceで足す。

## 7. 記録の規則

- 腕は「観測した」であり「PASSした」ではない。PilotにPASS状態は存在しない。
- HarnessのSession ID・Tool status・exit codeは、製品の意味的受理・実行許可・実Effectと
  同じ扱いにしない。`Result.Promoted()`は常にfalse。
- 実接続試験は既定で走らない。モック・合成の成功を実Harnessの証拠にしない。
- 環境固有の修復（ACL変更等）を隔離策の証拠にしない。
