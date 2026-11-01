# TEIの生成契約に必要な拡張（SUI DocumentV1投影）

状態: **提案（TEI側の設計判断待ち）**。この文書は、パイロット段階2で観測した不足を、TEIが判断できる形に整理したものです。要求の正本ではありません。

## 1. 目的

SUIのDocument/Card/Island/Edgeのrecord/string投影を、受理した意味から生成したい。現在の`reference-generator-selection`は、数値・money・roundingを前提にしており、この種の投影を扱えません。

## 2. 観測した制約（2026-11-01）

| 制約 | 根拠 |
| --- | --- |
| 契約に`rounding`が必須 | `std.text`だけの契約は`contract rounding precision/scale is invalid`で拒否される |
| 比較結果がmoney固定 | `selection.Result`は`state`・`amount`・`currency`・`code`だけを持つ |
| 生成器のstrategyがmoney前提 | `tei-generator-build`のstrategyは金額計算のテンプレートを出力する |
| 契約属性がWorkspaceに存在する前提 | 数値契約をSUIの作業領域へ適用すると`accepted attribute ... was not found`で拒否される |

## 3. 最小拡張案

TEIの設計判断を拘束しない範囲で、最小の拡張案を示します。

### 3.1 契約

```json
{
  "schema": "tei.reference.generator-contract/v0",
  "id": "sui.card.text",
  "version": "1",
  "status": "reference-local",
  "inputs": [{"attribute": "sui.card.text", "primitive": "std.text"}],
  "output": {"primitive": "std.text"},
  "projection": {"kind": "identity"}
}
```

- `projection.kind`は`identity`または`normalize`のいずれかから始める
- `rounding`は数値契約だけに要求し、文字列契約では省略できるようにする
- 既存のmoney契約は変更しない

### 3.2 fixture

```json
{
  "schema": "tei.reference.generator-fixture/v0",
  "contractId": "sui.card.text",
  "contractVersion": "1",
  "cases": [
    {"id": "present", "input": {"text": "hello"}, "want": {"state": "present", "text": "hello"}},
    {"id": "missing", "input": {}, "want": {"state": "missing"}},
    {"id": "empty", "input": {"text": ""}, "want": {"state": "present", "text": ""}},
    {"id": "unresolved", "input": {"text": null}, "want": {"state": "unresolved"}}
  ]
}
```

`present`・`missing`・`empty`・`unresolved`を区別します。空文字を欠損へ畳まないことが、この拡張の主な意味です。

### 3.3 比較と生成器

- 比較結果を`state`と`text`（またはprimitiveごとの値）へ一般化する
- 生成器は、入力を読み、`state`と値を返す最小のtemplateを1つ用意する
- source/binary digest、実行時間、provenanceの記録は既存の仕組みをそのまま使う

## 4. 受入試験

1. `tei-generator-select`が、上記の契約とfixtureで1つ以上の候補を比較できる
2. `present`・`missing`・`empty`・`unresolved`の4ケースが期待どおりに判定される
3. 候補のsource digestと実行証拠がreceiptに残る
4. 既存のmoney契約のfixtureが引き続き通る

## 5. TEI側で決めること

- `projection`を契約の正式な項目にするか、別の契約種別にするか
- 比較結果の一般化と、既存money契約との互換性
- 生成器familyの名前と版の扱い
- `empty`と`unresolved`の意味を、TEIの既存の未確定表現とどう対応させるか

## 6. 境界

- この文書は提案であり、TEIの要求・ADRではありません。
- 実装はTEI側で行います。TAI側に回避の別実装を追加しません。
- 公開gateは`blocked`のままです。
