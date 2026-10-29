# 合成不正入力の拒否検査

TEI・MMI・EKI・SUIが、意図的に不正な合成入力を拒否するかを確認します。

- TEI: ハイフンを含む不正なnamespaceで`validation`が失敗する。
- MMI: CSVの範囲外を指すガイドで`TABLE_NOT_FOUND`になる。
- EKI: `priority=low`のTask requestを400で拒否する。
- SUI: `claimType=bogus`のDocumentV1を422で拒否する。

`passed=false`のreceiptを期待し、受理された場合はcheckerが失敗します。

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

## 境界

- 拒否経路の確認であり、実在の規程・権限ではありません。
- 公開gateはblockedのままです。
