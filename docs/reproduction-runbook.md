# 再現手順（2026-11-06）

この文書は、TAIのTEIパイロット検証を**人が同じ手順で再現する**ための手順書です。計画のフィージビリティ判定5の「人が同じ手順で再現できる」に対応します。

ここに書いた手順は、著者（生成AI）が実際に実行して確認したものです。実インフラが要る検証は含みません（末尾の「再現できないもの」を参照）。

## 1. 前提

| 種別 | 必要なもの | 確認した版 |
| --- | --- | --- |
| OS | Windows | 11 |
| Go | `go` がPATHにある | 1.27 系 |
| Python | `python` がPATHにある | 3.12 |
| Node.js | `node` と `npm`（MMIの検証に使う） | 24.19 |
| GitHub CLI | `gh`（PRの作成とCI確認に使う） | 任意の現行版 |
| EKI | `eki-control` と `eki-agent` の実行ファイル | `66b0c04` ビルド |

Goのビルドキャッシュはリポジトリの外に置きます。既定の`%LOCALAPPDATA%`配下は権限や容量で失敗することがあるためです。

```powershell
$env:PATH = "D:\GIT\hat47x\tools\go\bin;$env:PATH"
$env:GOCACHE    = "D:\GIT\hat47x\.gocache"
$env:GOMODCACHE = "D:\GIT\hat47x\.gomodcache"
$env:GOTMPDIR   = "D:\GIT\hat47x\.gotmp"
$env:TMP        = "D:\GIT\hat47x\.gotmp"
$env:TEMP       = "D:\GIT\hat47x\.gotmp"
```

SUIの管理APIキーはローカル既定のテスト値を使います（本物の秘密情報は使いません）。

```powershell
$env:SUI_ADMIN_API_KEY = "test-admin-key"
$env:TAI_EKI_REQUEST = "D:\GIT\hat47x\tai-wt-dec2\evaluations\artifacts\eki-task-request-policy-aligned.json"
```

## 2. 検証対象の版を固定する

他プロダクトはTAIの外にあるため、worktreeを固定コミットで作ります。**この固定を省くと結果が再現しません。**

```powershell
git -C D:\GIT\hat47x\tei-platform  worktree add --detach D:/GIT/hat47x/tei-wt-r2      2d0b09b13
git -C D:\GIT\hat47x\sui-sensemaking worktree add --detach D:/GIT/hat47x/sui-wt-r2     09c24046
git -C D:\GIT\hat47x\eki-fabric      worktree add --detach D:/GIT/hat47x/eki-wt-proj2  66b0c04
```

| リポジトリ | 固定した版 |
| --- | --- |
| TEI（`tei-platform`） | `2d0b09b13` |
| SUI（`sui-sensemaking`） | `09c24046` |
| EKI（`eki-fabric`） | `66b0c04` |
| SEI（`sei-cognition`） | 作業ツリーの現行 |
| MMI（`markdown-matrix-injector`） | 作業ツリーの現行 |

MMIは`npm ci`で依存を入れておきます（`tsx`が無いと`inspect`が動きません）。

```powershell
npm ci --no-audit --no-fund    # 作業ディレクトリ: D:\GIT\hat47x\markdown-matrix-injector\03_Implement
```

EKIの検証は`EKI_REPO`（既定`D:\GIT\hat47x\eki-wt-proj`）を見ます。別名で作った場合は環境変数で指定します。

```powershell
$env:EKI_REPO = "D:\GIT\hat47x\eki-wt-proj2"
```

## 3. 一括検証を実行する

TAIの作業ツリーで1コマンド実行します。所要時間は35〜50分です（97段の実測）。

```powershell
python integrations/tools/run_suite.py `
  --tei-repo  D:\GIT\hat47x\tei-wt-r2 `
  --sui-repo  D:\GIT\hat47x\sui-wt-r2 `
  --sei-repo  D:\GIT\hat47x\sei-cognition `
  --mmi-repo  D:\GIT\hat47x\markdown-matrix-injector `
  --sei-schema D:\GIT\hat47x\sei-cognition\contracts\schemas\v1alpha1\decision-memory.schema.json `
  --mmi-schema D:\GIT\hat47x\markdown-matrix-injector\02_Architecture\format-profile-v1.schema.json `
  --eki-openapi D:\GIT\hat47x\eki-fabric\spec\external\openapi.json `
  --eki-control D:\GIT\hat47x\eki-control-66b0c04.exe `
  --eki-agent   D:\GIT\hat47x\eki-agent-66b0c04.exe
```

結果は`evaluations/records/TEI-suite-2026-11-03.json`に書かれます。`--skip-checker`を付けると最後のreceipt検査を省けます（検査は次項で単独実行できます）。

## 4. 期待する結果

```text
suite:   97段すべて returncode 0、result = PASS
checker: 合成61件・実実行184件、passed = true
doc整合: passed = true（97段、実実行184件が一致）
```

確認コマンド:

```powershell
python tools/check-synthetic-receipts/check.py --root .
python integrations/tools/doc_consistency_check.py
```

どちらもJSONを出力し、`"passed": true`なら一致しています。

## 5. つまずきやすい点

実際に遭遇した失敗と、その直し方です。

| 症状 | 原因 | 直し方 |
| --- | --- | --- |
| `No module named 'sui_sensemaking_api'` | SUI worktreeの中身が消えている、または`--sui-repo`が違う | worktreeを作り直し、`--sui-repo`を確認する |
| `Cannot find package 'tsx'` | MMIの`node_modules`が空 | `03_Implement`で`npm ci` |
| `FileNotFoundError: ... eki-wt-proj\conformance\...` | EKIのworktreeが無い、または`EKI_REPO`未設定 | worktreeを作り直すか`EKI_REPO`を設定 |
| `FileNotFoundError: ... eki-task-request-policy-aligned.json` | `TAI_EKI_REQUEST`が別の作業ツリーを指している | 自分の作業ツリーの絶対パスを設定 |
| suiteの一部だけ落ちる（`sui_agent_guard`） | 検証が`SUI_REPO`を見て旧worktreeを参照 | `--sui-repo`が渡されているか確認 |
| 契約JSONの`unknown field`でTEIが落ちる | 未知フィールドを拒否する入口（`tei-generator-select`）を使っている | 入口の違いは[段階4の実測](../evaluations/records/TEI-decode-divergence-2026-11-06.json)を参照 |
| `candidate wait failed` / `returned 1 of N responses` | long-runningプロファイルにone-shotな候補を渡している | 仕様どおりの失敗（[比較](../evaluations/records/TEI-target-profile-compare-2026-11-06.json)）。one-shotプロファイルを使う |

## 6. 再現できないもの

以下は実インフラが要るため、この手順に含みません。**未実施**として扱います。

- 実IdP（OIDC/OAuth）との連携
- 実Postgres以外の管理DB、実公開CA、実逆プロキシ
- 複数ホストへの配備とrolling更新
- 人の受理、意味の正しさ、生産性・自律性の評価（PoC完了後に測る）

これらを「通った」と書かないために、receiptの`scope`には毎回「何を証明しないか」を書いています。

## 7. この手順書自体の検査

手順書の段数が実際のsuiteとずれていないかは、`doc_consistency_check.py`が`integrations/tools/README.md`の段数と突き合わせます。段数を変えたときは、README・`docs/status.md`・この文書の3か所を同時に直します。
