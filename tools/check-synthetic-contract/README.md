# SUIの未知edge type保全検査

SUIの契約では、未知の`edges[].type`を破棄せず往復保持します。`bogus`をPUTし、GETで同じ値が返ることを確認します。

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

## 境界

- 合成DocumentV1です。実テナント・認可ではありません。
- 未知typeを「正しい関係」と解釈する意味検証ではありません。
- 公開gateはblockedのままです。
