# SEIの重複decision拒否

同じ`dec-01`を2回addし、SEIが2回目を拒否することを確認します。

```text
python run_negative.py --sei-root ../../../sei-cognition --go <go> --out receipt.json
python -m unittest -v check_test.py
python check.py --root ../..
```

## 境界

- 合成fixtureです。実store・権限・署名ではありません。
- 重複IDの拒否だけを確認します。意味の受理・公開承認ではありません。
- 公開gateはblockedのままです。
