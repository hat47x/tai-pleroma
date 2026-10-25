# TAI SCN-001 combined reference run

SCN-001の1回の参照実行として、次の3つを順に実行し、1つのreceiptへ束ねます。

1. MMI読み取り専用MCPの`inspect`/`select`。
2. SEI decision-memoryの`resume` projection。
3. MMIの観測行を重ねたSCN-001合成評価。

**人間の判断・権限・公開を実行しません。** 合成fixtureとローカル参照接続の記録です。

## 実行

MMIの開発チェックアウト（`node_modules`を含む）、SEIの開発チェックアウト、Goが必要です。

```text
go test ./...
go run . -root ../..
```

`-out run.json`でreceiptを保存できます。`-verify run.json`で`runDigest`を再計算し、`humanReviewed`・`authorityVerified`・`published`がすべてfalseであることを確認できます。

`-owner-packet run.json -out owner.json`で、Owner判断を求めるpacketを作れます。`status=awaiting-owner`、`approved=false`、`humanReviewed=false`、`authorityVerified=false`、`publicationApproved=false`であり、承認ではありません。

## 確認すること

- MMI: `selectedRows=3`、O-02/O-03の文言差保持、境界外・missing拒否、digest不変。
- SEI: 2 records、`dec-01`、未解決`authority:unknown`、`authorityVerified=false`。
- SCN-001: `observationSource=mmi-reference`、P-01〜P-05/N-01〜N-04/N-06の合成検査。
- 統合receipt: `passed=true`、`realProductsConnected=true`、`humanReviewed=false`、`authorityVerified=false`、`published=false`。
- `runDigest`は3 componentのJSONに対するSHA-256。

## 境界

- 3ツールの`passed`は、それぞれのローカル参照実行の範囲だけを示す。
- P-06（主体規模比較）とN-05（EKI委任）は`not-run`。
- SEIの一時storeは合成fixtureで、実在の規程・権限・利用者ではない。
- MMIはローカル開発チェックアウトで、配布版・実運用の認可は未確認。
- このreceiptは知的機能の受入合格ではない。
