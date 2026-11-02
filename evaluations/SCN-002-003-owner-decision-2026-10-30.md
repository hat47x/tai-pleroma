# SCN-002/SCN-003の採用とEKI次段階（Owner判断）

日付: 2026-10-30  
状態: **development review accepted / publication blocked**

## 判断

Ownerは次を承認した。

1. SCN-002（複数拠点メンテナンス）とSCN-003（補助金一次審査）を、TAIのdevelopment review対象に含める。
2. D-07（差戻し後再提出）とD-08（補助金一次審査）を、未決を保持したままdevelopment acceptedとして扱う。
3. EKIをadmission/cancelから次の段階へ進める。
4. 実物レビュー（`post-synthetic-real-object`）は当面先送りする。

## 未決の扱い

### D-07

- A拠点の更新期限差は、原本未確認のため未決のまま。
- 合成見積2160万円は予算上限3000万円の範囲内だが、確定額ではない。
- 再承認は未完了。発注は行わない。

### D-08

- 申請Aは収入要件の食い違いのため保留。
- 申請Bは上限超過で不適格。
- 申請Cは利益相反で通常審査外。
- 採択・通知・公開は行わない。

## 公開境界

- `publicationAllowed=false`
- 人間レビュー・Authority検証・実物レビューは未実施。
- 公開には`post-synthetic-real-object`が必要。

## EKIの次段階

admission/cancelの次として、次を進める。

- Taskを実行するWorker/Runnerの接続。
- 実行結果の検証と、失敗時のfail-closed。
- sandbox・CPU/メモリ制限の扱いを明示する。

EKIのTask実行結果は、実際に実行した範囲だけを記録する。合成の成功を実Taskの成功として扱わない。
