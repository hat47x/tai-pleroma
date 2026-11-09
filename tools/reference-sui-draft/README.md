# TAI → SUI → D-04 link

SUIのcard/island照合receiptと、SCN-001のD-04暫定案内を突き合わせ、SUIで扱った観測がD-04の根拠行と公開境界に現れているかを確認します。

**意味の受理・公開承認・Authorityを検証するものではありません。**

## 実行

```text
go test ./...
go run . -sui-link ../../evaluations/records/SUI-SCN-link-2026-10-26.json \
  -artifact ../../evaluations/artifacts/SCN-001-D-04-provisional.md
# 任意: link receiptのdocumentDigestを固定（env TAI_SUI_EXPECT_DOCUMENT_DIGEST、フラグが優先）
go run . -sui-link ... -artifact ... -expect-document-digest sha256:<hex>
```

## 確認すること

- SUI linkが`passed=true`で、5 cardを持つ。
- D-04にO-02/O-03/O-06/O-07/O-08の観測行がある。
- O-08が`unavailable`のまま保持されている。
- D-04が`provisional`、`公開承認: なし`、`Authority: 未検証`、`review:real-object`を保つ。
- D-04のbyte列のSHA-256をreceiptへ記録。
- 追加の`pin`項目: 期待値なしは記録のみ（`pin.checked=false`）。`-expect-document-digest`を渡すと、link receiptの`documentDigest`との一致を要求し、不一致・欠落は`passed=false`です。形式不正は終了コード2・標準出力なしです。

## 境界

- D-04は合成fixtureから生成した内部レビュー用Draftであり、実在の規程ではない。
- SUIの実資料・テナント・認可・意味形成の正しさは未検証。
- 公開gateはblockedのまま。
- revisionは扱いません（link段で確認）。固定はreceiptファイルの申告の照合にとどまり、改ざんは検出しません。
