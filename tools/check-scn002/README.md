# SCN-002 複数拠点メンテナンスの接続検査

3拠点・期限・故障・予算上限を持つ合成シナリオを、MMIとTEIで実行します。

- MMI: 5行の観測を読み取る。
- TEI: `Site` / `Asset` / `Budget` / `Priority`型をvalidateする。

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

## 境界

- 合成データです。実在の資産・契約・予算ではありません。
- 優先度の意味・安全判断・発注は未検証です。
- 公開gateはblockedのままです。
