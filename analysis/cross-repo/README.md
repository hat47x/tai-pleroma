# 横断の分析成果物

複数のリポジトリにまたがる整理・監査の成果物を置く。TAIが置き場と所有者を持つ。**製品としての受入や意味の受理を示すものではない。**

## 出所

もとは親ディレクトリ `D:\GIT\hat47x`（git管理外）にあった。版も所有者もなく、参照の取得可否を確かめるたびに結果が変わりうる状態だった。横断の境界整理でF5・FB-5として記録し、2026-10-31に本リポジトリへ移設した（[#181](https://github.com/hat47x/tai-pleroma/issues/181)）。内容は移設時点のままで、再評価はしていない。

| ファイル | 内容 | 時点 |
| --- | --- | --- |
| `boundary-map.md` | 7リポジトリの機能分界の整理、起票状況、判断待ちの点 | 2026-10-06〜09 |
| `audit/xref_audit.py` | `hat47x/<repo>:<path>` 形式の引用を、引用先の統合branchと照合する | 2026-10-09 |
| `audit/mention_matrix.py` | 製品名の言及を双方向に数える | 2026-10-09 |
| `audit/xref_audit.result.json` | `xref_audit.py` の出力（実行時点の記録） | 2026-10-09 |
| `progress/product-progress.md` | 製品機能リストと進捗の推定 | 2026-10-04 |
| `progress/product-progress.json` | 同スナップショットのJSON（`gen-progress.js` の入力由来） | 2026-10-04 |
| `progress/product-progress-data.js` | 機能・規模点・根拠の生データ | 2026-10-04 |
| `progress/gen-progress.js` | `product-progress-data.js` からMarkdownとJSONを生成する | 2026-10-04 |

`yomiyasu-lint-report.md` は文章推敲の作業記録であり、横断の分析成果物ではないため対象外とした。

## 実行

監査スクリプトは、各リポジトリの `origin/main` を読む。置き場は環境変数 `HAT47X_ROOT`（既定 `/mnt/d/GIT/hat47x`）で指定する。実行前に全リポジトリをfetchしておく。

```bash
cd analysis/cross-repo/audit
python3 xref_audit.py
python3 mention_matrix.py
```

進捗の再生成は、同じディレクトリで `node gen-progress.js` を実行する。`product-progress.json` と `product-progress.md` を上書きする。

## 境界

- ここに置くのは分析と推定であり、製品の受入・契約・意味の受理ではない
- 各製品の正本は、それぞれのリポジトリのREADME・docs・Issueにある
- 記載は各ファイルの時点のスナップショットであり、現在の状態を示すものではない
- 引用の照合結果は、取得時点の `origin/main` に依存する。再実行すれば変わりうる
