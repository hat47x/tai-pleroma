# 合成SCN-001フローの接続検査

合成施設文書からD-04、生成AI development review、EKI Worker test環境、公開gateまでが一続きに接続されているかを確認します。

## 確認する流れ

```text
合成施設文書
  -> MMI 5行
  -> SEI 3 records
  -> TEI validation=ok
  -> SUI 5 cards / 3 islands / 1 edge
  -> D-04
  -> 生成AI development review
  -> EKI Worker test環境（Task実行ではない）
  -> 公開gate
```

- D-04にO-08の`unavailable`、`provisional`、公開承認なしが残っていること。
- AI reviewが`quality=sufficient-for-development`で、人間・公開承認を主張していないこと。
- EKI Worker test環境が`workerExecution=false`、`taskResult=false`のままであること。
- gateが`allowed=false`で、R-01〜R-05を`developmentAccepted`にしていること。

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

## 境界

- 合成入力とtest環境の接続確認です。
- 実在の規程・権限・独立レビューではありません。
- 公開gateのblockedを解除しません。
