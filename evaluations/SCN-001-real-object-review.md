# SCN-001 実物ベース再レビュー（合成後）

状態: **合成によるdevelopment reviewはaccepted。実物レビューは未実施**。`reviewTrigger=post-synthetic-real-object`。

対象: [SCN-001](../scenarios/SCN-001-shared-space-guidance.md)、[D-04](../tools/reference-scn001/testdata/scn001.json)。

2026-10-29のOwner判断により、R-01〜R-05は合成文書を根拠にdevelopment review acceptedとした。評価者は生成AIであり、人間レビューは業務フロー一巡とAI品質確認の後に回す。この文書は、公開前に実物ベースで見直す条件を定める。**現在の受理は公開承認でもAuthority検証でもない。**

## 見直しの目的

合成fixtureとローカル参照接続で作ったD-04・DEC-02・統合receiptが、実在の資料・権限・利用条件でも成立するかを確認する。成立しない場合は仮承認を取り消し、未決へ戻す。

## 必要な証拠

| ID | 証拠 | 確認すること | 状態 |
| --- | --- | --- | --- |
| R-01 | 実在の施設規程・掲示・案内文の特定版 | 原文、出典、版、取得時点、適用範囲。O-02/O-03の矛盾が実在するか | 合成でdevelopment accepted。実物未取得 |
| R-02 | 公開権限者の本人・役割・承認範囲 | DEC-02の`provisional-owner`を実在の権限者へ置き換えられるか | 合成でdevelopment accepted。実権限未確認 |
| R-03 | MMIの実ワークスペース | 実資料を読み取り専用で参照し、O-02/O-03/O-07の原文と版を取得できるか | 合成MMIでdevelopment accepted。実ワークスペース未実施 |
| R-04 | SEIの実storeまたは実決定record | `dec-02`が実在の決定として記録され、`authority:unknown`/`publication:unapproved`/`review:real-object`が解消されるか | 合成SEIでdevelopment accepted。実store未実施 |
| R-05 | D-04の独立レビュー | 案内文としての意味、誤解、適用条件、公開可否 | 生成AI評価でdevelopment accepted。人間の独立レビューは未実施 |
| R-06 | P-06（主体規模比較）の判断 | 個人・組織・社会のどこを初回範囲にするか | 未実施 |
| R-07 | N-05（EKI委任）の要否 | 委任が価値を生むか、独立した成果確認ができるか | 未実施 |

## 判定

- R-01〜R-05は合成文書によるdevelopment review acceptedとする。ただし公開用の実物証拠ではない。
- 公開・外部作用は、実物レビューとR-02の権限確認が終わるまで行わない。公開gateはblockedのまま。
- R-06/R-07が未決なら、初回範囲から除外するか、未決のまま残す。
- 実物レビューで合成の前提が成立しない場合は、development review acceptedを取り消し、D-04を未決のDraftに戻す。

## 証拠の扱い

- 実在の個人情報・未公開資料・秘密情報は、このリポジトリへ複製しない。参照先、版、確認者、確認日だけを記録する。
- MMI/SEIの実環境のログや原本は、各基盤の管理場所に置く。
- 合成fixtureの`passed=true`を、実物レビューの証拠へ読み替えない。
- 公開gateは、`accepted`の各項目に`evidenceKind=real-object`を要求する。`synthetic`・`fixture`・`none`のままでは公開できない。

## review status JSONへの記録

`accepted`へ更新するときは、[SCN-001-review-status.json](SCN-001-review-status.json)の該当項目だけを次の形にする。

```json
{
  "id": "R-01",
  "status": "accepted",
  "evidence": "参照先・版・取得時点・確認者役割を短く記録",
  "evidenceKind": "real-object"
}
```

- `evidence`へ原文や個人情報を転載せず、参照先・版・確認日・確認者の役割だけを書く。
- `evidenceKind`は`real-object`だけを許可する。`synthetic`・`fixture`・`none`は不可。
- 取得できなかった項目は`accepted`にせず、`pending`のまま残す。O-08のような`unavailable`を、利用可能な証拠へ読み替えない。
- R-06/R-07を初回範囲から外す場合は、`not-applicable`と理由を記録する。

## 再レビューの記録

実施後、次の項目を追記する。

- 対象版（TAI、MMI、SEI、実資料）
- 確認者と役割
- R-01〜R-07の結果
- D-04の採否
- 仮承認の継続・取消
- 未確認事項

この文書は再レビューの計画であり、実施記録ではない。
