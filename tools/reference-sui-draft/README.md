# TAI → SUI → D-04 link

SUIのcard/island照合receiptと、SCN-001のD-04暫定案内を突き合わせ、SUIで扱った観測がD-04の根拠行と公開境界に現れているかを確認します。

**意味の受理・公開承認・Authorityを検証するものではありません。**

## 実行

```text
go test ./...
go run . -sui-link ../../evaluations/records/SUI-SCN-link-2026-10-26.json \
  -artifact ../../evaluations/artifacts/SCN-001-D-04-provisional.md
```

## 確認すること

- SUI linkが`passed=true`で、4 cardを持つ。
- D-04にO-02/O-03/O-06/O-07の観測行がある。
- D-04が`provisional`、`公開承認: なし`、`Authority: 未検証`、`review:real-object`を保つ。
- D-04のbyte列のSHA-256をreceiptへ記録。

## 境界

- D-04は合成fixtureから生成した内部レビュー用Draftであり、実在の規程ではない。
- SUIの実資料・テナント・認可・意味形成の正しさは未検証。
- 公開gateはblockedのまま。
