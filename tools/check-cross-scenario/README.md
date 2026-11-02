# 横断シナリオの実務能力マトリクス

SCN-001（単一施設の予約案内）、SCN-002（複数拠点の設備更新）、SCN-003（補助金一次審査）を1つのマトリクスへ統合します。

- SCN-001: MMI/TEI/SEI/EKI/SUIの正常系・拒否系
- SCN-002: MMI/TEI/SEI/EKI/SUI、D-05/D-06/D-07、AI review
- SCN-003: MMI/TEI/SEI/EKI/SUI、D-08、AI review

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

## 境界

- 合成入力の集約です。実在の規程・資産・契約・予算ではありません。
- 公開gateはblockedのままです。
