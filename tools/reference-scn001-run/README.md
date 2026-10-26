# TAI SCN-001 combined reference run

SCN-001の1回の参照実行として、次の3つを順に実行し、1つのreceiptへ束ねます。

1. MMI読み取り専用MCPの`inspect`/`select`。
2. SEI decision-memoryの`resume` projection。
3. MMIの観測行を重ねたSCN-001合成評価。

**人間の判断・権限・公開を実行しません。** 合成fixtureとローカル参照接続の記録です。

SCN-001評価はMMIの選択結果を合成fixtureへ反映し、検証成功時の**同じ観測集合を一時fixtureとしてD-04生成へ渡します**。文書生成だけが元のfixtureを読み直す経路を避けます。出典の真正性、MMIと実資料の一致、実資料の意味・権限の確認は引き続き未検証です。保存後の成果物は次の明示的なbyte照合で検査できます。

## 実行

MMIの開発チェックアウト（`node_modules`を含む）、SEIの開発チェックアウト、Goが必要です。

```text
go test ./...
go run . -root ../..
```

`-out run.json`でreceiptを保存できます。今回生成したD-04も残す場合は、`-artifact-out review.md -out run.json`を指定します。両方の出力先は新規・別名のファイルに限り、既存ファイルは上書きしません。保存したbyte列を読み直し、実行記録のdigestとの一致を確認します。`-verify run.json`で`runDigest`を再計算し、`humanReviewed`・`authorityVerified`・`published`がすべてfalseであることを確認できます。


`-verify run.json -artifact review.md`では、指定したローカルファイルを読み直し、`reviewArtifact.artifactDigest`とbytesを照合します。実行記録の検証とbyte照合の両方が成功した場合だけ、`passed=true`・`artifactBytesVerified=true`になります。欠損・差替え・改行の変換は失敗です。`-artifact`を付けない検証は`artifactBytesVerified=false`で、ファイルの一致を主張しません。`-artifact`は`-verify`または`-owner-packet`と併用します。`-verify`と`-owner-packet`は同時に指定できません。

```text
go run . -verify ../../evaluations/records/SCN-001-run-2026-10-26.json -artifact ../../evaluations/artifacts/SCN-001-D-04-provisional.md
```

保存済みのMarkdownはLFで取得するよう`.gitattributes`で指定します。検証器は改行や文字コードを正規化しません。この照合は指定ファイルと記録の一致だけを示し、出典の真正性、人間の意味判断、最新の公開可否、署名を検証しません。履歴の公開gateを現在の承認として扱わないでください。

保存済みの参照実行は[evaluations/records/SCN-001-run-2026-10-26.json](../../evaluations/records/SCN-001-run-2026-10-26.json)にあり、`go test`の`TestRecordedRunVerifies`で`runDigest`とcomponent invariantsを再確認します。

`-owner-packet run.json -artifact review.md -out owner.json`で、実行記録と成果物を照合したOwner判断packetを作れます。`artifactBytesVerified=true`はその時点のbyte一致だけを示します。packetには実際に読んだ実行記録と成果物の絶対パスを入れ、固定された過去の成果物・実行記録へのリンクは補いません。`-artifact`を省略した場合は`artifactBytesVerified=false`で、成果物へのリンクも補いません。packetの出力先も新規ファイルに限ります。packetはD-04のdigest/status、公開gateの`allowed`/blocker、説明文書と再レビュー計画への参照を含みます。`status=awaiting-owner`、`approved=false`、`humanReviewed=false`、`authorityVerified=false`、`publicationApproved=false`であり、承認ではありません。


まとめ欄のscenario・合成範囲、仮承認・再レビュー要否・実接続のフラグ、公開判定とblocker一覧は、個別結果と一致する必要があります。blockerの欠落・差替えや未知の公開gate schemaは、componentのdigestが一致しても拒否します。

`-verify`の`passed=true`は記録の整合性を示し、参照実行自体の成功とは別です。整合した失敗記録は検査できますが、Owner判断packetは成功した参照実行の記録からだけ生成します。公開gateの入力条件を満たしても、packetの人間レビュー・Authority・公開承認はfalseのままです。


```text
go run . -root ../.. -artifact-out review.md -out run.json
go run . -owner-packet run.json -artifact review.md -out owner.json
```

実行記録・成果物・packetの保存は、複数ファイルをまとめた原子的な処理ではありません。途中で失敗した場合に一部の新規ファイルが残ることがありますが、成功として扱わず、既存ファイルを再試行で上書きしません。照合後のファイル変更まで防ぐ機能ではないため、レビュー時にも`-verify run.json -artifact review.md`で再確認します。byte一致は内容の正しさ・人間の意味受理・公開権限を証明しません。

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
