# 合成receiptのラベル検査

合成入力の参照receiptが`synthetic=true`、`evidenceKind=synthetic`を失っていないかを確認します。

対象:

- SUI API
- TEI型検証
- SEI decision-memory
- 合成MMI
- 合成施設文書
- EKI Worker test環境

あわせて、R-01〜R-05が`pending`/`synthetic`、R-06/R-07が`pending`/`none`であることを確認します。

## 曖昧な記録の拒否

- JSONの同名キー（入れ子を含む）は拒否します。後に現れた値で`synthetic`や`status`を上書きしてはなりません。
- Review statusの同じ`id`の重複は、状態が一致していても拒否します。後の項目を優先しません。
- 破損JSON、配列でない`items`、不正な項目、対象外のschema/scenarioを拒否します。`evidenceKind=none`のR-06/R-07に証拠が書かれた場合も拒否します。
- これらは**記録の構造と合成ラベル**だけを検査します。元資料の真正性、人間の意味受理、公開権限、内容の正しさを保証しません。

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

`passed=false`なら、合成入力を実物証拠として扱い始めた可能性や、曖昧なJSONが混入した可能性があります。公開gateは解除しません。
