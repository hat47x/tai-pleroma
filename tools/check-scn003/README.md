# SCN-003 補助金一次審査の接続検査

3件の申請、収入要件の食い違い、事業費上限、利益相反、採択枠を、MMIとTEIで実行します。

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

## 境界

- 合成データです。実在の制度・申請・審査ではありません。
- 採択・不採択の確定判断ではありません。
- 公開gateはblockedのままです。
