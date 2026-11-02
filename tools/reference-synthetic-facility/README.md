# SCN-001 合成施設文書の欠陥検査

`scenarios/SCN-001-synthetic-facility/`の創作文書を読み、製造工程で検出したい次の欠陥が入力に含まれているかを確認します。

- 総則の「予約不要」と会議室の「事前予約制」が併存する。
- 10月版と11月版で会議室の条件が変わる。
- 11月版から会議室の記載が消える。
- 予約規程の原本を取得できていない。

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../../scenarios/SCN-001-synthetic-facility
```

## 出力

- `synthetic=true`
- `evidenceKind=synthetic`
- `publicationAllowed=false`
- `detectedDefects`に検出した工程欠陥
- `passed=true`は合成入力の検査だけを示す

## 境界

- 実在の施設・規程・権限を確認した証拠ではありません。
- review statusの`accepted`や`evidenceKind=real-object`へ読み替えません。
- 公開gateはblockedのままです。
