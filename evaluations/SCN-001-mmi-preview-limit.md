# MMIのpreview行数制約

7行の合成観測を`A1:E8`で選択したところ、`selectedRows=5`となり、`expectedRows=7`を満たせなかった。

- 観測: `selectedRows=5`
- `conflictPreserved=true`
- 結果: `passed=false`
- 理由: `select did not preserve the O-02/O-03 observations`（行数不一致）

MMIの参照実装は選択結果のpreview（最大5行）を`selectedRows`として数えている可能性がある。7行全体の選択・検証はこの経路では未確認。

## 境界

- 合成入力です。
- MMIの読み取り経路の制約であり、実在の規程ではありません。
- 公開gateはblockedのままです。
