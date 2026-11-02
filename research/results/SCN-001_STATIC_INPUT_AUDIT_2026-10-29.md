# SCN-001 確認済み合成入力の静的digest照合（研究の基礎資料）

- 状態: **Static observation only / 製品試験NOT RUN**（2026-10-29）
- 研究: [H1プロトコル](../protocols/SCN-001_EPISTEMIC_CONTINUITY.md) と [予備比較の事前固定案](../protocols/SCN-001_PILOT_FREEZE_2026-10-29.md)
- 読取対象: TAI main `c388e47c708c6f35b6c6f8f42a546a1b31710f3d`
- **実行したこと**: GitHub上の固定内容を読み取り、Python 3.13.5の`hashlib.sha256(text.encode("utf-8"))`で日本語の観測文字列を計算し、既存のSUI receiptの`textDigest`と比較。
- **実行していないこと**: GoのTAI統合試験、MMI/SUI/SEIの実接続、製品の`-sui-link`／`-sui-receipt`の新規比較実行、実用評価、人間による受理。

## 1. 使用した固定ファイル

| 固定ファイル | Git blob SHA | 観測した範囲 |
| --- | --- | --- |
| [SCN-001の合成fixture](../../tools/reference-scn001/testdata/scn001.json) | `6de80588e14d8b091448dbfe7d6b1cc3d9c14f3d` | O-02、O-03、O-07、O-08の`text` |
| [SUIの元probe receipt](../../evaluations/records/SUI-api-2026-10-26.json) | `3e84d786cc022d01c02907907e8803f05db99f4a` | `documentCards[*].id/textDigest` |
| [SUI照合の旧要約](../../evaluations/records/SUI-SCN-link-2026-10-26.json) | `a3f099ee58288b89981af3213780878c091378b9` | card ID集合、island、成功フラグ |
| [既存の差替え再現記録](../../evaluations/SCN-001-sui-current-observation-gap.md) | `e290cd13bc61002a10f9833ef294bdafff9b075a` | 先行する開発時の動作記録（今回の実行ではない） |

Git blob SHAはこの参照版のファイル同一性用であり、本文文字列のSHA-256や実験runの`runDigest`ではない。

## 2. 静的計算の結果

| Case | 対象の文字列 | 計算したSHA-256 | SUI receiptのdigestと一致 |
| --- | --- | --- | --- |
| CTRL-01 / O-02、O-07 | `施設の利用は予約不要` | `02f44f2912500f6b1d8cd02221ac450964c2f82e5991529ddf46a31574ec9537` | はい（両card） |
| CTRL-01 / O-03 | `会議室の利用には事前予約が必要` | `e11416b06a952168954074bf904627c2bbc74ff59f25503a508b8c67ce23acb0` | はい |
| CTRL-01 / O-08 | `予約規程の原本を取得できなかった` | `678ba80b4b84681e98ce7d4dde324622a89f6ad4dd4d9a102e73ac82c7ebe68c` | はい |
| MUT-01 / O-02、O-07 | `施設の利用は予約不要（SUI照合の比較試験）` | `6cb93810e585a7983faf090243e6df2d543ea17a4c90e31acc460497a98b3928` | いいえ（旧receiptを保持した場合） |

元のSUI receiptのO-02とO-07は同じ`textDigest=sha256:02f44…`を持つ。本文を差し替えた合成コピーでは、同じIDでも`sha256:6cb938…`となり一致しないことが、文字列に対するSHA-256の比較だけで確かめられた。

これは**固定された文字列・保存済みreceipt間の計算**である。MMIが実際に新しい本文を返したこと、SUIの実APIが古いカードを返したこと、TAIの統合実行が新しい本文を受理または拒否したことを、今回新たに実証したものではない。

## 3. 開発記録に既存の動作証拠がある範囲

[既存反例記録](../../evaluations/SCN-001-sui-current-observation-gap.md)では、隔離した合成MMIコピーを使い、保存済みSUI要約を含む統合runが成功した一方、今回観測を反映したfixtureと元SUI receiptの直接照合は`card digest does not match the SCN observation: O-02`で拒否された、と記録されている。これは**歴史的な開発時の観測**であり、本研究の比較実験を新たに実行した結果へ加算しない。

現在の main には`-sui-receipt`による内容照合の経路がある。さらに[Draft PR #142](https://github.com/hat47x/tai-pleroma/pull/142)はMMI選択・SCN評価・D-04の同一run内の`inputBindingVerified`を追加する提案であり、対象は**SUIとの現在観測照合とは別**。このPRの未採用コードのテスト結果を、mainにおける保証や研究上の独立再現とみなさない。

## 4. 研究上の解釈と次の実験

- **確かめられたこと**: 固定された元観測と元SUI receiptの一部digestは一致し、同一IDの合成本文差替えでdigestが変わる。
- **未確定**: 各比較armの独立runによる誤通過率、過剰拒否率、コスト、実ファイル不変性、主体による意味判断、別ドメインへの一般化。
- **次の研究実施**: [事前固定案](../protocols/SCN-001_PILOT_FREEZE_2026-10-29.md)のCTRL-01とMUT-01を、同一固定実行版・同等のコピーworkspace・元receiptで、B1/B2それぞれ実行しログを残す。
- **次の製品Gate**: 実行の結果が#28の既存受入条件と異なった場合に限り、版・再現手順・不一致をOwnerへ報告。新契約をTAI研究側で勝手に採用しない。

この静的結果を用いてH1の効果量、有意差、安全性や一般的な優越性を主張しない。R-01〜R-07、P-06/N-05、公開、実権限、実Workerは引き続き未確認・NOT RUNである。
