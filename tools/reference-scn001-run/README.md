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

`-out run.json`でreceiptを保存できます。SUIのcard/island照合を含める場合は`-sui-link ../../evaluations/records/SUI-SCN-link-2026-10-26.json`を指定します。今回生成したD-04も残す場合は、`-artifact-out review.md -out run.json`を指定します。両方の出力先は新規・別名のファイルに限り、既存ファイルは上書きしません。保存したbyte列を読み直し、実行記録のdigestとの一致を確認します。`-verify run.json`で`runDigest`を再計算し、`humanReviewed`・`authorityVerified`・`published`がすべてfalseであることを確認できます。


`-verify run.json -artifact review.md`では、指定したローカルファイルを読み直し、`reviewArtifact.artifactDigest`とbytesを照合します。実行記録の検証とbyte照合の両方が成功した場合だけ、`passed=true`・`artifactBytesVerified=true`になります。欠損・差替え・改行の変換は失敗です。`-artifact`を付けない検証は`artifactBytesVerified=false`で、ファイルの一致を主張しません。`-artifact`は`-verify`または`-owner-packet`と併用します。`-verify`と`-owner-packet`は同時に指定できません。

```text
go run . -verify ../../evaluations/records/SCN-001-run-2026-10-26.json -artifact ../../evaluations/artifacts/SCN-001-D-04-provisional.md
```

保存済みのMarkdownはLFで取得するよう`.gitattributes`で指定します。検証器は改行や文字コードを正規化しません。この照合は指定ファイルと記録の一致だけを示し、出典の真正性、人間の意味判断、最新の公開可否、署名を検証しません。履歴の公開gateを現在の承認として扱わないでください。

保存済みの参照実行は[evaluations/records/SCN-001-run-2026-10-26.json](../../evaluations/records/SCN-001-run-2026-10-26.json)にあり、`go test`の`TestRecordedRunVerifies`で`runDigest`とcomponent invariantsを再確認します。

`-owner-packet run.json -artifact review.md -out owner.json`で、実行記録と成果物を照合したOwner判断packetを作れます。`artifactBytesVerified=true`はその時点のbyte一致だけを示します。packetには実際に読んだ実行記録と成果物の絶対パスを入れ、固定された過去の成果物・実行記録へのリンクは補いません。`-artifact`を省略した場合は`artifactBytesVerified=false`で、成果物へのリンクも補いません。packetの出力先も新規ファイルに限ります。packetはD-04のdigest/status、公開gateの`allowed`/blocker、説明文書と再レビュー計画への参照を含みます。`status=awaiting-owner`、`approved=false`、`humanReviewed=false`、`authorityVerified=false`、`publicationApproved=false`であり、承認ではありません。


まとめ欄のscenario・合成範囲、仮承認・再レビュー要否・実接続のフラグ、公開判定とblocker一覧は、個別結果と一致する必要があります。blockerの欠落・差替えや未知の公開gate schemaは、componentのdigestが一致しても拒否します。

SUI linkを含む記録では、cardのID集合がO-02/O-03/O-06/O-07/O-08、islandのID集合がI-01/I-02/I-03とそれぞれ一致することを確認します。件数だけが同じ別IDや空IDは拒否し、並び順の違いは許容します。この検査はID集合の一致を確認するもので、SUI Document本文や今回のMMI観測との内容の一致を再検証するものではありません。

### 追加候補: 今回の観測を使うSUI照合

状態: Draftの実装候補。元のSUI receiptを受け渡すCLIの採用はOwner判断待ちです。保存済み要約での不一致は[再現記録](../../evaluations/SCN-001-sui-current-observation-gap.md)を参照してください。

`-sui-receipt`は、元のSUI API probe receiptを読み取り、今回MMI観測を反映したfixtureと一緒に既存の`reference-sui-link`へ渡す候補です。D-04生成に使うfixtureと同じものを渡し、cardの内容が一致しない場合は実行記録と成果物を保存せずに終了します。元のreceiptは一度だけ読み、曖昧なJSONを拒否した同じbytesの一時コピーを照合器へ渡します。

```text
go run . -root ../.. \
  -sui-receipt ../../evaluations/records/SUI-api-2026-10-26.json \
  -artifact-out review.md -out run.json
```

`-sui-link`とは同時に使えず、`-verify`・`-owner-packet`とも併用できません。この候補での`-out`は新規ファイルに限り、元のreceiptや既存出力を上書きしません。引数の不正や内容の不一致は終了コード2となり、成功した実行記録を標準出力へ返しません。

既存のreceipt schemaと`runDigest`の計算方法は変えません。SUIの個別結果には既存の要約を保持し、説明文で今回の照合と保存済み要約の読込みを区別します。ただし、説明文だけを実行の証明として扱えません。保存後の`-verify`は記録の構造と任意の成果物bytesを調べるもので、元のSUI receiptと今回の観測を再照合しません。この追加候補でもDocument本文のdigest再計算、SUI実APIの認可、実資料の真正性、人による意味受理、公開権限は未検証です。

JSONの読出しでは、不正なUTF-8と、同じobject内で重複する項目名を拒否します。大文字・小文字、Unicodeの大小文字対応、escape表記が違うだけの同名項目も対象です。保存済み記録の検査・packet生成と、5つの個別ツールの返却値に同じ検査を適用し、後の値で前の主張が消えることを防ぎます。未使用の追加項目は引き続き読み飛ばしますが、その内部の重複も拒否するため、一般的なJSONより受け付ける範囲は狭くなります。追加項目の意味や承認は検証しません。正常な既存記録のschemaとdigestは変えません。

`-verify`の`passed=true`は記録の整合性を示し、参照実行自体の成功とは別です。整合した失敗記録は検査できますが、Owner判断packetは成功した参照実行の記録からだけ生成します。公開gateの入力条件を満たしても、packetの人間レビュー・Authority・公開承認はfalseのままです。

個別結果が失敗扱いでも、人間レビュー・権限確認・公開や公開承認を済ませたという主張は拒否します。失敗記録は調査用に残せますが、この参照実行の範囲を超える主張の根拠にはなりません。通常実行も返却・保存の前に保存済み記録と同じ整合性検査を通します。矛盾があればエラーを返し、CLIは実行記録を出力・保存しません。矛盾のない失敗記録は引き続き検査できます。この検査は実際の人間レビューや公開権限の有無を確認するものではありません。


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
- `suiLink`指定時は、SUIのlinked cards・island groups・edge count・contradictionをcomponentへ追加する。
- `runDigest`はcomponentのJSONに対するSHA-256。

## 境界

- 4ツールの`passed`は、それぞれのローカル参照実行の範囲だけを示す。
- P-06（主体規模比較）とN-05（EKI委任）は`not-run`。
- SEIの一時storeは合成fixtureで、実在の規程・権限・利用者ではない。
- MMIはローカル開発チェックアウトで、配布版・実運用の認可は未確認。
- このreceiptは知的機能の受入合格ではない。
