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
- O-02/O-03/O-06/O-07/O-08の`textDigest`がSCN-001観測の本文digestと一致する。
- `I-01`がO-02/O-07、`I-02`がO-03/O-06、`I-03`がO-08を含む。
- `I-01`→`I-02`の`contradicts` edgeが1本ある（`documentEdgeCount=1`）。
- `documentEdgeCount`と`documentEdges`の件数が一致する。

観測・card・islandの各一覧で同じIDが重複する場合は、同じ値でも拒否します。islandのメンバーは配列の各項目として比較し、`["O-02 O-07"]`を`["O-02", "O-07"]`と同じ扱いにしません。並び順の違いと、IDが重複しない追加要素は許容しますが、選択外の要素の内容は照合しません。

Document IDとdigest値が空の場合も失敗とします。Document本文からのdigest再計算と、矛盾という関係の意味的な正しさは検証しません。

fixtureとSUI receiptの読込みでは、不正なUTF-8と、同じobject内で重複するJSON項目名を拒否します。大文字・小文字、Unicodeの大小文字対応、escape表記だけが違う同名項目も対象です。使わない追加項目の内部も検査し、後の値で前の主張を隠した入力を照合へ渡しません。不正入力は終了コード2・標準出力なしとなり、`-out`の既存ファイルも変更しません。重複のない追加項目を読み飛ばす動作と、正常な照合結果の形式は維持します。

この読込み検査は、実行済み記録の真正性や、保存済み統合記録との結び付きを証明しません。保存後に内容を再照合するには、今回のMMI観測を反映したfixtureと、対応する元のSUI receiptが必要です。統合実行の`-verify`は、この内容の再照合を行いません。

## 境界

- SUIの実資料・テナント・認可は未検証。
- SCN-001の意味形成・仮説の正しさは未検証。
- 合成fixtureのcard/island/edgeだけを対象にする。
- 公開・Owner判断・Authorityには触れない。
