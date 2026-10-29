# MMIのpreview行数制約

7行の合成観測を`A1:E8`で選択したところ、`selectedRows=5`となり、`expectedRows=7`を満たせなかった。

- 観測: `selectedRows=5`
- `conflictPreserved=true`
- 結果: `passed=false`
- 理由: `select did not preserve the O-02/O-03 observations`（行数不一致）

MMIの`select`はpreviewを最大5行に固定している（`03_Implement/src/navigate/select.ts`の`logical.bodyRows.slice(0, 5)`）。TAIの参照実装はpreviewの行数を`selectedRows`として数えるため、5行超の表はこの経路では行数一致を検証できない。

7行全体の選択・検証は、preview以外の読み取り経路が必要。現時点では未確認。

## 境界

- 合成入力です。
- MMIの読み取り経路の制約であり、実在の規程ではありません。
- 公開gateはblockedのままです。
