# 共通Harness Adapter：Exit一覧と証拠の索引（2026-11-12）

**これは索引である。判断の正本は [後続計画](harness-adapter-followup-plan-2026-11-11.md) と
[実装README](../integrations/harness-adapter/README.md) にある。ここには
「どのExitを、どの実行で、どの証拠ファイルで示したか」だけを置く。**

- 契約: `yi.harness-adapter/v0`（[contract.go](../integrations/harness-adapter/contract.go)）
- 契約試験: `go test ./... -count=1` — 160件PASS（外部接続なし）
- 実接続試験: `HARNESS_ADAPTER_REAL=1 go test -tags realconnect ./...`（既定では走らない）
- Adapter: `dsh-headless`、`claude-code`、`step-cli`、`direct-control`、`scripted-*`（契約試験専用）

## 1. Exit一覧

| Exit | 状態 | 示した実行 | 証拠 |
| --- | --- | --- | --- |
| E1 2 Harness × 型付きTool × 同一Task | **達成**（3 Harness） | DSH / Claude Code / Step Code の各runで型付き呼出しを観測（shell call 0） | `real-pilot-typed-mcp-2026-11-11.json`、`real-pilot-typed-mcp-claude-2026-11-11.json`、`real-pilot-step-typed-mcp-2026-11-11.json` |
| E2 CLI直実行とMCP経路の同値 | **達成**（7欄一致） | Claude Code・Step Code の `tei_model_catalog` が schemaVersion/ok/errorCode/worldFingerprint/sourceIndexFingerprint/modelRevision/validationOk で一致 | 同上3ファイル |
| E3 Root外readの成否を記録 | **達成**（refused と readable の両方） | Claude Code=refused（Verified=true）、DSH=readable（Verified=false） | README §6.3、`realconnect_rootprobe_test.go` |
| E4 2Productを同一Taskで | **達成**（2 Harness × 2製品、+SHOはCLI実起動） | DSH と Claude Code が1 Task内で TEI+SEI を型付き到達 | `real-pilot-cross-product-2026-11-11.json`、`real-pilot-cross-product-claude-2026-11-11.json` |
| E5 Skill有無の差を測定 | **達成**（ITT 4/4、適格対2） | 事前割付 `S1-H2→S2-H3→S3-H3→S4-H2` をDSHで実行。H3 loaded 2/2、H2 clean 2/2 | `four-session-observation-2026-11-12.json`（Harness別の適格性は `skill-pair-observation-2026-11-11.json`、`skill-pair-step-2026-11-11.json`） |
| E6 Receiptが not-observed 以外 | **達成（partial）** | 独立読み手が partial を2回再現。claim欠落の理由をnoteに残す | `receipt-readback-2026-11-11.json`、`realconnect_receipt_test.go` |

## 2. この索引が主張しないこと

- **精度・効果量は測っていない。** E5は「適格な対ができた」までで、Skillが回答を改善したかは
  [TAI #488](https://github.com/hat47x/tai-pleroma/issues/488) の独立Expectedの担当。
  4 Sessionからの統計的結論も出していない（`notClaimed` に明記）。
- **隔離は実装していない。** `RootProbe` は実効を測るだけ。隔離のOwnerは
  [TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)／
  [TEI #2515](https://github.com/hat47x/tei-platform/issues/2515)。
- **製品の意味受理・実行許可・実Effectを示していない。** `Result.Promoted()` は常にfalse。
- **全Harness対応を宣言していない。** 示したのは「この3 Harness × 固定条件での限定互換」。

## 3. 未対応・未実施（根拠付き）

| 項目 | 状態 | 根拠 |
| --- | --- | --- |
| SUI の投影 | **unsupported** | `03_Implement/mcp` の stdio server は存在するが、同梱 `node_modules` が linux-x64 の esbuild（`@esbuild/linux-x64` があり `win32-x64` が無い）でWindowsでは起動できない。加えて `engines.node` は `22.x`、実環境は v24.19.0 |
| SHO の型付き経路 | **unsupported（CLIは実起動済み）** | `bin/sho-inspect.cjs` に stdio JSON-RPC 面が無い。MCP化には新しいserver実装が必要で、このAdapterは書かない。CLIとしての実起動は完了（`status:indexed`） |
| Codex / OpenCode / Gemini / Cursor / Aider / Goose | **not-run** | PATH上に存在しない（2026-11-12確認）。導入後に同じ `Adapter` interfaceで足す |
| Skill増分の精度比較 | **not-run** | 適格な4 Sessionは作れたが、独立Expectedの採点は TAI #488 の担当 |
| 実OS identity/ACL による隔離 | **not-run** | 本環境では測っていない。Ownerは TAI #232 / TEI #2515 |

## 4. 実接続で見つけた欠陥（すべて契約試験では出ず、実runで出た）

1. **許可Rootと到達bytesは別**。初回runで製品バイナリをrepo pathで指すと、DSHはそのpathを
   読んだ（`--permission-mode read-only` でも）。以後バイナリをRoot内に置く。
2. **DSHの`--json`投影は監査に使えない**。8KiBで切れ `truncated:true` が付く。MCP resultも同じ。
3. **新しいDSH entryは`insert` patchでのみ追加できる**。id指定patchは `entry not found`。
4. **Claude Codeの`result`は`subtype=success`と`is_error=true`を同時に返し得る**。
   subtypeだけで `run=completed` と判定していたのを直した。
5. **截断判定をbyte数にしていた**。Claude CodeはDSHのcapを適用しないので、14030byteの
   完全JSONを誤って比較対象外にした。JSON完全性で判定するよう直した。
6. **Skill対のpinを共有していた**。Skillを削除したH2が `placed=true` と記録された。
   pinをArmごとに取り、配置の有無を失格条件にした。
7. **`skill-history` の `discovered` をロードと読んでいた**。配置とロードを分けた。
8. **Step Codeの`config.toml`はBOMを受け付けない**。BOM付きはkey解析で拒否される。
9. **OpenRouterの予算制約**。`maxTokens: 65536` が残高で拒否され、4 Session全落ち。
   `8000` で通った。失敗分もITT分母に残した。

## 5. 再現手順（要約）

```bash
cd integrations/harness-adapter
go test ./... -count=1                        # 契約試験 160件（外部接続なし）

# 実接続（合成trial rootと、Harnessごとの認可が要る）
HARNESS_ADAPTER_REAL=1 \
HARNESS_ADAPTER_TRIAL_DIR=<trial> \
HARNESS_ADAPTER_TEI_BIN=<tei.exe> \
HARNESS_ADAPTER_TEI_WORKSPACE=<public reference workspace> \
HARNESS_ADAPTER_TEI_SKILL=<tei-platform/skills/yi-tei-modeling> \
HARNESS_ADAPTER_TEI_MCP_BIN=<tools/reference-mcp-readonly-adapter build> \
go test -tags realconnect -run TestRealPilotTypedMCPToolEquivalence -v .
```

Harnessごとの追加条件（DSHの`--patch`、Claude Codeの`--mcp-config`、Step Codeの
plugin配置と無人承認flag）は README §7 の「Vendor固有」節にある。
