# 横断シナリオの実務能力マトリクス

SCN-001（単一施設の予約案内）とSCN-002（複数拠点の設備更新）を1つのマトリクスへ統合します。

- SCN-001: MMI/TEI/SEI/EKI/SUIの正常系・拒否系
- SCN-002: MMI/TEI/SEI/EKI/SUI、D-05/D-06、AI review

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

## 境界

- 合成入力の集約です。実在の規程・資産・契約・予算ではありません。
- 公開gateはblockedのままです。
