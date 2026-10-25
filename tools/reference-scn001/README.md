# TAI SCN-001 reference walkthrough

SCN-001のT0/T1/T2を合成fixtureとして評価し、P-01〜P-05とN-01〜N-04/N-06のうち、機械的に検査できる条件を再現する参照ツールです。

**実SUI/TEI/SEI/SHO/EKIには接続していません。** 実製品の動作、権限者の承認、利用者にとっての有用性を証明しません。

## 実行

```text
go test ./...
go run . -fixture testdata/scn001.json
```

`-out receipt.json`でreceiptを保存できます。`passed=true`は合成fixtureの検査が通ったことだけを示します。

## 検査する条件

- P-01: 全observationに原文・出典・出典版・取得時点・availability・digestがある。
- P-02: O-02とO-03を別observationとして保持し、仮説を未採用のまま残す。
- P-03: D-01がO-02/O-03を参照する未公開Draftで、「確認中」を明示する。
- P-04: 承認権限が未確認の間、公開・外部作用を保留する。
- P-05: T0→T1→T2がobservation集合を追加し、旧Draftを上書きしない。
- N-01: 文言がA→B→Aへ戻っても、出典版が別であり旧承認を自動復活させない。
- N-02: 権限未確認のまま公開済み・承認済みと報告しない。
- N-03: 原本取得失敗を「存在しない」と断定せず、unavailableとして保持する。
- N-04: 仮説を規程として採用しない。
- N-06: observation IDの重複を拒否し、Draftが属する時点のRevisionに存在する観測だけを参照する。全期間で既知でも、未来の観測を過去のDraftの根拠にはできない。

P-06（主体規模の比較）とN-05（EKI委任の独立確認）は`not-run`です。

## 境界

- 入力は架空のfixtureであり、実在の施設・規程・利用者ではない。
- receiptは`realProductsConnected=false`、`humanReviewed=false`、`authorityVerified=false`を常に持つ。
- 実製品の接続は、各基盤の既存契約を確認したうえで別の作業とする。
- このツールはTAI固有の状態DBや共通Contractを新設しない。シナリオ試験用の参照実装である。
