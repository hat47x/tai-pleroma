# 合成receiptのラベル検査

合成入力の参照receiptが`synthetic=true`、`evidenceKind=synthetic`を失っていないかを確認します。

対象:

- SUI API
- TEI型検証
- SEI decision-memory
- 合成MMI
- 合成施設文書
- EKI Worker test環境

あわせて、R-01〜R-05が`accepted`/`synthetic`、R-06/R-07が`pending`/`none`であることを確認します。

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

`passed=false`なら、合成入力を実物証拠として扱い始めた可能性があります。公開gateは解除しません。
