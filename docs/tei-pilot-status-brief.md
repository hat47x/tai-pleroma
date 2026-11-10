# TEIパイロットの現況（2026-11-06）

TEIによるプロダクト構築のフィージビリティ検証について、**何が示せて、何が示せていないか**を1枚にまとめる。判断が要る点は、そのまま並べる。詳細は各リンク先とreceiptを見る。

この文書は受入判断ではない。公開gateは`blocked`のままである。

**判定は[TEIパイロットの判定](../analysis/tei-pilot-conclusion-2026-11-06.md)に分けて書いている**（結論は未達。条件ごとに「示せた／部分／反例」と、何が変われば達するか）。

## 1. 示せたこと

| 条件 | 状態 | 根拠 |
| --- | --- | --- |
| 生成単位が生成器 | **示せた**。5契約を意味から再生成でき、生成コードの手修正は3回の意味変更でいずれも0行 | [任意の追加](../evaluations/records/TEI-meaning-change-2026-11-06.json)、[必須の追加](../evaluations/records/TEI-meaning-change-required-2026-11-06.json)、[任意→必須](../evaluations/records/TEI-meaning-change-requiredness-2026-11-06.json) |
| 証拠が版に束縛される | **示せた**。契約digest・sourceDigest・TEIのcommitを含む実実行receiptが200件。全receiptに必須項目と限界記述があり、登録漏れも検査している | [status](status.md)、[体裁](../evaluations/records/TEI-receipt-scope-2026-11-06.json) |
| 意味が版付きで存在する | **部分**。契約とfixturesは版付きで、生成物とdigestで対応する。ただし製品への写像は手書き | [写像](../evaluations/records/SUI-consumer-mapping-2026-11-06.json) |
| 適合試験がある | **部分**。1回の意味変更は25ケースで確認できる。ただし試験は被覆に依存し、被覆の無い変更は緑のまま通る | [被覆](../evaluations/records/TEI-fixture-coverage-2026-11-06.json) |
| 実行先が交換できる | **反例あり**。one-shotでは通るが、long-runningでは生成候補が応答し続けられない | [record](../evaluations/records/TEI-target-profile-compare-2026-11-06.json)、[text](../evaluations/records/TEI-target-profile-compare-text-2026-11-06.json) |
| 人が同じ手順で再現できる | **部分**。2つのrunbookと1コマンド（103段）で再現できる。実インフラが要る検証は含まない | [再現手順](reproduction-runbook.md)、[意味変更の進め方](meaning-change-runbook.md) |

## 2. 反例（そのまま残す）

1. **実行モデルは交換できない。** Profileの宣言を差し替えても、生成候補は標準入力1件で終わるためlong-runningで動かない（`text`と`text-record`の両テンプレートで確認）。原因はさらに絞れた。TEIにlong-running用テンプレートはあるが、**投影の生成戦略はone-shotの2つだけ**で、投影契約にlong-running戦略を渡すと生成器が拒否する（[receipt](../evaluations/records/TEI-projection-strategy-2026-11-06.json)）。この組み合わせはTEIの試験にも文書にも無く（1629件の`*_test.go`と`docs`/`plan`の検索で0件）、**暗黙の結合であって宣言された制約ではない**。
2. **十進値は丸められる。** `0.1234567890123456789` → `0.12345678901234568`、`12345678901234567890` → `12345678901234567000`（[receipt](../evaluations/records/TEI-decimal-fidelity-2026-11-06.json)）。
3. **新しい意味は製品に自動で届かない。** 消費側は既知フィールドには忠実だが、知らないフィールドは`valid: true`のまま落ちる。
4. **入れ子の投影は受理も拒否もされない。** `build`は平坦化して通し、`select`は`unknown field`で拒否する（[receipt](../evaluations/records/TEI-decode-divergence-2026-11-06.json)）。

## 3. TEI側で判断が要る点

[Issue草案](../analysis/tei-side-gaps-issue-drafts-2026-11-06.md)に4件。1と3は同じ原因を指すため、実質は3論点。ただし**3論点の性格は同じではない**。数値配列の制約はTEIの試験が拒否を表明している意図した仕様（拡張の提案）、デコード方針と投影×process modelは試験にも文書にも無い暗黙の挙動（方針の決定）。

1. 契約のデコード方針を一本化するか（未知フィールドを拒否するか、入れ子を受理するか）
2. 数値・真偽値の配列（`many`）を扱えるようにするか
3. 生成テンプレートをTarget Profileのprocess modelに対応させるか

十進値の精度と`optional`のnull省略は、TEI側で既に#2585として追跡されている。TAIからは新しいIssueを作らない。

## 4. 製品側で判断が要る点

[整理](../analysis/product-side-decisions-2026-11-06.md)に6件。**判断待ちは残っていない。**

- 決定済み4件: agent資格情報の配線（ADR-0093）、`NOT_YET_VALID`（#437として計測で閉じる）、未知adapterの扱い（noopは常に許可）、複数Workerの分散（`pickWorker`が最初の使用可能Workerを選ぶと明記）
- 実施項目2件: 受入（RAC-1）を本番経路へ配線する（パッケージは実装・文書化済み、呼び出しが無い）、`enforce_access`が`decision.read_only`を見るようにする（潜在的）

## 5. 実インフラが要る検証（未実施）

実IdP、実管理DB、公開CA、実逆プロキシ、複数ホスト配備、人の受理。**これらを「通った」とは書かない。**

## 6. 再現方法

```text
python integrations/tools/run_suite.py --tei-repo <TEI> --sui-repo <SUI> ... （103段、35〜50分）
python tools/check-synthetic-receipts/check.py --root .
python integrations/tools/doc_consistency_check.py
```

期待結果は[再現手順](reproduction-runbook.md)§4に固定してある。判断が下りたときの測り直しは[再観測の準備](re-observation-plan.md)にまとめてある。

## 7. この文書が証明しないこと

- 生産性・自律性の向上（PoC完了後に評価する。中間評価を人の判断材料にしない）
- 意味の正しさ、業務上の受入
- パイロットの成功が全プロダクトの移行成功を意味すること
- 実環境での動作

## 8. 更新の仕方

段階が進んだら、§1の表と§2の反例をreceiptに合わせて更新する。数値（段数・receipt件数）は`doc_consistency_check.py`が文書間で突き合わせる。
