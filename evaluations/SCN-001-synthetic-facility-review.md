# SCN-001 合成施設文書による工程欠陥検査

状態: **検証用（synthetic）**。実物ベース再レビューではない。

## 目的

公開されている施設利用案内の一般的な論点を参考に創作した文書で、製造工程の欠陥検出が機能するかを確認する。実在の規程・権限・公開可否を確認するものではない。

## 入力

[SCN-001合成施設文書](../scenarios/SCN-001-synthetic-facility/README.md)

- O-02: 館内掲示の「施設全体は予約不要」
- O-03: 会議室・研修室の「事前予約制」
- O-06: 2026年10月版の配布文書
- O-07: 2026年11月版の配布文書
- O-08: 予約規程の原本を取得できなかった記録

## R-01〜R-05との関係

| ID | 合成入力での確認 | 実物レビューとの違い |
| --- | --- | --- |
| R-01 | 文書の版・出典・適用範囲を識別できるか | 実在の施設文書ではない |
| R-02 | 公開権限者を`unknown`のまま保持できるか | 実在の権限者・承認範囲は未確認 |
| R-03 | MMIで読み取り専用参照できるか | 実ワークスペース・実資料ではない |
| R-04 | SEIで未決判断を保持できるか | 実store・実決定ではない |
| R-05 | D-04の意味・公開境界を独立レビューできるか | 生成AI評価でdevelopment accepted。人間の独立レビューは未実施 |

2026-10-29のOwner判断により、R-01〜R-05は合成入力を根拠に`status=accepted`、`evidenceKind=synthetic`のdevelopment review acceptedとする。**実物レビューの受理や公開承認へ読み替えない。**

review statusでは、R-01〜R-05を`status=accepted`、`evidenceKind=synthetic`、合成入力への参照つきで記録する。公開gateは`real-object`以外を`developmentAccepted`として記録し、公開はblockedのままにする。

## 検出する工程欠陥

- 総則の「予約不要」と会議室の「事前予約制」が併存する。
- 10月版と11月版で会議室の条件が変わる。
- 11月版から会議室の記載が消える。
- 予約規程の原本を取得できていない。
- 原本未取得を、利用可能な証拠へ読み替えていない。

## 実行

```text
python tools/reference-synthetic-facility/check.py \
  --root scenarios/SCN-001-synthetic-facility
```

出力は`synthetic=true`、`evidenceKind=synthetic`、`publicationAllowed=false`。`passed=true`は合成入力の検査だけを示す。

## 境界

- 実在の施設・規程・顧客・個人情報を含まない。
- 公開gateは`blocked`のまま。
- この文書を実物レビューの実施記録にしない。
