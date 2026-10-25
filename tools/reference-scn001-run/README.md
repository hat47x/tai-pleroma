# TAI SCN-001 combined reference run

SCN-001の1回の参照実行として、次の3つを順に実行し、1つのreceiptへ束ねます。

1. MMI読み取り専用MCPの`inspect`/`select`。
2. SEI decision-memoryの`resume` projection。
3. MMIの観測行を重ねたSCN-001合成評価。

**人間の判断・権限・公開を実行しません。** 合成fixtureとローカル参照接続の記録です。

SCN-001評価はMMIの選択結果を合成fixtureへ反映し、検証成功時の**同じ観測集合を一時fixtureとしてD-04生成へ渡します**。文書生成だけが元のfixtureを読み直す経路を避けます。出典の真正性、MMIと実資料の一致、成果物の保存先での独立したbyte照合は引き続き未検証です。

## 実行

MMIの開発チェックアウト（`node_modules`を含む）、SEIの開発チェックアウト、Goが必要です。

```text
go test ./...
go run . -root ../..
```

`-out run.json`でreceiptを保存できます。`-verify run.json`で`runDigest`を再計算し、`humanReviewed`・`authorityVerified`・`published`がすべてfalseであることを確認できます。

保存済みの参照実行は[evaluations/records/SCN-001-run-2026-10-26.json](../../evaluations/records/SCN-001-run-2026-10-26.json)にあり、`go test`の`TestRecordedRunVerifies`で`runDigest`とcomponent invariantsを再確認します。

`-owner-packet run.json -out owner.json`で、Owner判断を求めるpacketを作れます。packetはD-04成果物のdigest/statusと、artifact・record・再レビュー計画への参照を含みます。`status=awaiting-owner`、`approved=false`、`humanReviewed=false`、`authorityVerified=false`、`publicationApproved=false`であり、承認ではありません。

## 確認すること

- MMI: `selectedRows=3`、O-02/O-03の文言差保持、境界外・missing拒否、digest不変。
- SEI: 3 records、`dec-01`、`dec-02`（development-review-onlyの仮承認）、未解決`authority:unknown`/`publication:unapproved`、`authorityVerified=false`。
- SCN-001: `observationSource=mmi-reference`、P-01〜P-05/P-07/N-01〜N-04/N-06/N-07の合成検査。
- 統合receipt: `passed=true`、`realProductsConnected=true`、`provisionalApproved=true`、`reviewRequired=true`、`reviewTrigger=real-object`、`humanReviewed=false`、`authorityVerified=false`、`publicationApproved=false`。
- `reviewArtifact`: D-04の内部レビュー用Markdownの`status=provisional`、`artifactDigest`、`publicationApproved=false`。
- `publicationGate`: R-01〜R-07のreview statusを読み、`allowed=false`とblockerを記録する。
- `runDigest`は5 componentのJSONに対するSHA-256。

## 境界

- 4ツールの`passed`は、それぞれのローカル参照実行の範囲だけを示す。
- P-06（主体規模比較）とN-05（EKI委任）は`not-run`。
- SEIの一時storeは合成fixtureで、実在の規程・権限・利用者ではない。
- MMIはローカル開発チェックアウトで、配布版・実運用の認可は未確認。
- このreceiptは知的機能の受入合格ではない。
