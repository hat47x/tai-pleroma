# 合成プロセスマトリクス

MMI・TEI・SEI・EKI・SUIの正常系、拒否系、契約系のreceiptを1つに集約し、プロセス遂行能力の現在地を確認します。

## 集約するreceipt

- 変種マトリクス（2変種 × 5製品）
- 不正入力マトリクス（TEI/MMI/EKI/SUI）
- SUI未知edge type契約
- SEI重複decision拒否
- 合成フロー

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

## 境界

- 合成入力の集約です。実在の規程・権限・Task実行ではありません。
- 公開gateはblockedのままです。
