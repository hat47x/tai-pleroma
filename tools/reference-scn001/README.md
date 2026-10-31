# TAI SCN-001 reference walkthrough

SCN-001のT0/T1/T2を合成fixtureとして評価し、P-01〜P-05とN-01〜N-04/N-06のうち、機械的に検査できる条件を再現する参照ツールです。

**実SUI/TEI/SEI/SHO/EKIには接続していません。** 実製品の動作、権限者の承認、利用者にとっての有用性を証明しません。

## 実行

```text
go test ./...
go run . -fixture testdata/scn001.json
```

`-out receipt.json`でreceiptを保存できます。`passed=true`は合成fixtureの検査が通ったことだけを示します。

`-mmi-receipt <path>`を指定すると、MMI読み取り専用接続のreceiptに含まれる`selected`でO-02/O-03/O-07の原文・出典・出典版・availabilityを置き換えます。Draft・仮説・判断・revisionはfixtureのままであり、人間の判断ではありません。


受け渡す3件のIDとfixture側の対応先は、それぞれ一意である必要があります。IDの重複・欠落・対象外の行、空の原文・出典・出典版、`available`以外の選択行は拒否します。検査は全件の反映前に行い、失敗時はfixtureを変更しません。正しい入力の行順は問いません。原文・出典・版の空白は、値が空でないことの検査だけに用い、保存時に削りません。

この検査で確かめるのは参照用入力の完全性と対応関係です。MMIの自己申告、出典の真正性、出典版の現行性、資料同士の意味的な矛盾は検証しません。`observedAt`は引き続き合成fixtureの値であり、MMIが実際に取得した時刻の証拠として使えません。実資料の取得時刻・対象範囲の受渡しは、既存の接続契約と照らして別途確認します。

`-out-fixture <path>`を指定すると、検証成功時の観測値を反映したfixtureを一時的なJSONとして保存できます。SCN評価と後続のD-04生成で**同じ観測集合**を使うための受渡しであり、新たな意味契約や正本を作る機能ではありません。保存先は作業用で、実資料を扱う場合はアクセス制御と削除を考慮してください。

## 検査する条件

- P-01: 全observationに原文・出典・出典版・取得時点・availability・digestがある。
- P-02: O-02とO-03を別observationとして保持し、仮説を未採用のまま残す。
- P-03: D-01がO-02/O-03を参照する未公開Draftで、「確認中」を明示する。
- P-04: 承認権限が未確認の間、公開・外部作用を保留する。
- P-05: T0→T1→T2がobservation集合を追加し、旧Draftを上書きしない。
- N-01: O-02とO-07が同じ文言で出典版が異なり、公開済みDraftがないことを確認する（構造の合成検査）。過去の受理が復活するかは扱わない。受理を伴う往復の構造は、[reference-sei-decision](../reference-sei-decision/README.md)の`-decision-validity`が合成bundleで別に調べる。
- N-02: 権限未確認のまま公開済み・承認済みと報告しない。
- N-03: 原本取得失敗を「存在しない」と断定せず、unavailableとして保持する。
- N-04: 仮説を規程として採用しない。
- N-06: 観測ID・Draft IDの重複を拒否し、各Draftが対応Revisionの時点ですでに得られた観測だけを根拠として参照する。観測が増えないDraft改訂は許容する。
- P-07: `development-review-only`の仮承認を、未公開のD-04へ限定する。
- N-07: 仮承認を公開承認・Authority検証として扱わない。

P-06（主体規模の比較）とN-05（EKI委任の独立確認）は`not-run`です。

## 境界

- 入力は架空のfixtureであり、実在の施設・規程・利用者ではない。
- receiptは`realProductsConnected=false`、`humanReviewed=false`、`authorityVerified=false`を常に持つ。
- 実製品の接続は、各基盤の既存契約を確認したうえで別の作業とする。
- このツールはTAI固有の状態DBや共通Contractを新設しない。シナリオ試験用の参照実装である。
