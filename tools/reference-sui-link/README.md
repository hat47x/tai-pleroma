# TAI → SUI → SCN-001 link

SUI API probeのreceiptとSCN-001 fixtureを照合し、SUI上のcard digestとisland構成がSCN-001の観測と一致するかを確認します。

**実在のSUI資料・認可・意味形成の正しさは検証しません。** 合成fixtureのcard/island/edgeとSCN-001観測の対応だけを確認します。

## 実行

```text
go test ./...
go run . -fixture ../reference-scn001/testdata/scn001.json \
  -sui-receipt ../../evaluations/records/SUI-api-2026-10-26.json
```

確認内容:

- SUI receiptが`readOnly`・`realProductConnected`・`documentRead`である。
- O-02/O-03/O-07の`textDigest`がSCN-001観測の本文digestと一致する。
- `I-01`がO-02/O-07、`I-02`がO-03を含む。
- `documentEdgeCount=1`。

観測・card・islandの各一覧で同じIDが重複する場合は、同じ値でも拒否します。islandのメンバーは配列の各項目として比較し、`["O-02 O-07"]`を`["O-02", "O-07"]`と同じ扱いにしません。並び順の違いと、IDが重複しない追加要素は許容しますが、選択外の要素の内容は照合しません。

Document IDとdigest値が空の場合も失敗とします。Document本文からのdigest再計算と、矛盾という関係の意味的な正しさは検証しません。

## 境界

- SUIの実資料・テナント・認可は未検証。
- SCN-001の意味形成・仮説の正しさは未検証。
- 合成fixtureのcard/island/edgeだけを対象にする。
- 公開・Owner判断・Authorityには触れない。
