# 合成入力による工程検証の現在地

状態: **合成検証のみ**。実物レビュー・公開承認・Authority検証ではない。

## 目的

製造工程の課題検出を、実在の顧客資料を使わずに確認する。合成入力を実物証拠へ読み替えず、公開gateは`blocked`のまま維持する。

## 入力

[SCN-001合成施設文書](../scenarios/SCN-001-synthetic-facility/README.md)

- O-02: 館内掲示の「施設全体は予約不要」
- O-03: 会議室・研修室の「事前予約制」
- O-06: 2026年10月版の配布文書
- O-07: 2026年11月版の配布文書
- O-08: 予約規程の原本を取得できなかった記録

## 確認結果

| 対象 | 結果 | 証拠 | 未確認 |
| --- | --- | --- | --- |
| 合成文書の工程検査 | 4種類の欠陥を検出 | [receipt](../evaluations/records/SCN-001-synthetic-facility-2026-10-28.json) | 実在の規程ではない |
| SUI | 5 card/3 island/1 `contradicts` edge | [receipt](../evaluations/records/SUI-api-2026-10-26.json) | 実資料・テナント・認可 |
| MMI | O-02/O-03/O-06/O-07/O-08の5行、digest不変 | [receipt](../evaluations/records/SCN-001-synthetic-mmi-2026-10-29.json) | 実認可・書込み |
| SEI | 3 records、`authority:unknown`/`publication:unapproved`を保持 | [receipt](../evaluations/records/SEI-decision-2026-10-26.json) | 実store・署名・権限 |
| TEI | 型宣言`validation=ok`、workspace digest不変 | [receipt](../evaluations/records/TEI-model-2026-10-29.json) | 実データ・意味 |
| EKI | Control Plane 405、Agent claim delivery、Task `queued`→`cancelled` | [receipt](../evaluations/records/EKI-worker-env-2026-10-28.json) | Task実行・結果・Authority |
| EKI Native Runner | 固定コマンド、期限/取消し、出力上限、Windows/Linuxのツリー停止、引数/GPU/資源/digestのfail-closed | [eki-fabric #275](https://github.com/hat47x/eki-fabric/pull/275) | sandbox・CPU/メモリ制限・結果検証 |

## 検出する工程欠陥

- 総則の「予約不要」と会議室の「事前予約制」が併存する。
- 10月版と11月版で会議室の条件が変わる。
- 11月版から会議室の記載が消える。
- 予約規程の原本を取得できていない。
- 原本未取得を、利用可能な証拠へ読み替えていない。

## review status

| ID | status | evidenceKind | 意味 |
| --- | --- | --- | --- |
| R-01 | accepted | synthetic | 合成文書によるdevelopment review。実在の規程ではない |
| R-02 | accepted | synthetic | development reviewのみ。権限者は未確認 |
| R-03 | accepted | synthetic | 合成MMI workspaceによるdevelopment review |
| R-04 | accepted | synthetic | 合成SEI fixtureによるdevelopment review |
| R-05 | accepted | synthetic | 生成AIによるdevelopment review。人間の独立レビューは未実施 |
| R-06 | pending | none | 未実施 |
| R-07 | pending | none | 未実施 |

R-01〜R-05はOwner判断によりdevelopment review accepted。評価者は生成AIで、人間レビューは業務フロー一巡とAI品質確認の後に回す。公開用の`real-object`証拠ではない。公開gateは`developmentAccepted`へ記録し、公開は`blocked`。

## 再実行

```text
python tools/reference-synthetic-facility/check.py --root scenarios/SCN-001-synthetic-facility
cd tools/reference-mmi-readonly
go run . -workspace ../../scenarios/SCN-001-synthetic-facility/mmi \
  -table 'Sheet1!A1:E6' -expected-rows 5 -synthetic \
  -out ../../evaluations/records/SCN-001-synthetic-mmi-2026-10-29.json
```

EKI環境は[reference-eki-worker](../tools/reference-eki-worker/README.md)を参照。

## 境界

- 実在の施設・個人・規程・認可を含まない。
- 合成fixtureの`passed=true`を実物レビューの受理へ読み替えない。
- EKI Agentはclaim deliveryのtest profileであり、Task実行主体ではない。
- 公開gateのblockedを解除しない。
