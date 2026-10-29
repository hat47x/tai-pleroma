# 保存済みSUI照合と今回のMMI観測が一致しない反例

状態: 合成入力による未解消の反例。人による意味受理、権限確認、公開承認の証拠ではありません。[Issue #28](https://github.com/hat47x/tai-pleroma/issues/28)の残件です。

## 問題と確認範囲

`reference-scn001-run -sui-link`は、以前作られたSUI照合の要約を読み込みます。PR #92でcard・islandのID集合を検査するようになりましたが、今回MMIから取得した観測の本文とSUI cardの内容を照合していません。

合成workspaceのコピーだけでO-02/O-07の本文を「施設の利用は予約不要（SUI照合の比較試験）」に変更し、IDを維持したところ、次の差が生じました。保存済みSUI要約と元のSUI receiptは変更していません。

| 経路 | 観測結果 |
| --- | --- |
| 統合実行 + 保存済みSUI要約 | `passed=true`、`suiLink.passed=true` |
| 今回の成果物を指定した再検査 | `passed=true`、`artifactBytesVerified=true` |
| 今回のMMI観測を反映したfixture + 元のSUI receiptを既存の`reference-sui-link`へ渡す | `passed=false`: `card digest does not match the SCN observation: O-02` |
| 変更前の合成fixture + 同じSUI receiptを既存の`reference-sui-link`へ渡す | `passed=true`（再現スクリプトの対照試験） |

今回の成果物には変更した本文が入っています。入力ID集合と成果物bytesの一致を確認しても、SUI結果が今回の観測内容に対応するとはいえません。既存のSUI照合器は、この内容の差を検出できています。

初回実証に使用したTAI headは`1e39775df0f249b60692c1641e422e45dd436e48`です。PR #92のmergeは`d2945d996116f1690614aae7285bdc3a88ce4f5e`です。MMIは`a8addd1560bd02131b29ade4d9d1cfa7ca5f9b21`、SEIは`c289f1ea9e51142abaff123880fd7d112169007a`の隔離した開発checkoutを使いました。Go 1.27.0、Node 22.23.2、Python 3.12で実行しました。元のCSV・SUI要約・元のSUI receiptと、変更後のコピーが試験中に書き換わらないことをhashで確認しました。

初回の実行digestは`sha256:bbaf5165aa6355596af7f824479ef4581f8ea41333f0d3a1ba4b8a1765d02f36`、成果物digestは`sha256:146da2667ededb22d65f4f3e7cff686f821105c231bb47b6a3c85d470b1d0441`でした。再現手順の合否には、固定値との一致ではなく、統合実行・成果物再検査・SUI直接照合の結果の差を使います。

2026-10-29にmain `f6c574ae0fbe906f76c594498f7a7ac26a07f7f9`から分離した環境で再現スクリプトを実行し、同じ不一致と入力不変性を確認しました。Linux上で実施したもので、Windowsでの再現スクリプト実行は未実施です。

## 再現手順

[reproduce-sui-observation-gap.py](reproduce-sui-observation-gap.py)は、6つの参照モジュールとreview statusを新規ディレクトリへコピーしてから合成CSVを変更します。元リポジトリは変更しません。既存の出力ディレクトリは再利用せず、失敗後の自動再試行もしません。

GoとNodeをPATHへ設定し、`MMI_ROOT`と`SEI_ROOT`で依存を準備した隔離checkoutを指定します。リポジトリのルートから、未作成の出力先を渡します。

```sh
python3 evaluations/reproduce-sui-observation-gap.py --out /absolute/path/to/new-evidence
```

出力先に`report.json`、今回のMMI receipt・反映済みfixture・実行記録・成果物、各実行の標準出力とエラーを残します。終了コード0と`gapObserved=true`は、上記の不一致が再現したことだけを示します。製品検証の成功ではありません。将来修正されて結果が変わった場合も、理由を調べられるように終了コードを非0にします。CIの受入条件には組み込んでいません。

## 対応と残る範囲

[PR #125](https://github.com/hat47x/tai-pleroma/pull/125)では、任意の`-sui-receipt`経路から元のSUI receiptを受け取り、同じ統合実行でMMI観測を反映したfixtureと一緒に既存の`reference-sui-link`へ渡します。2026-10-29にこの追加経路の採用判断を得ました。保存済み要約だけの`-sui-link`は構造検査として残るため、上記の再現スクリプトは引き続き従来経路の不一致を検出します。保存形式や基盤間のreceipt schemaは変更しません。

合成入力では、変更していない観測での成功、同じIDで本文を変えた場合の拒否、入力不変性、失敗時に成功packetを生成しないことを確認しました。追加経路では、内容不一致なら実行記録・成果物を保存せず終了します。保存後の`-verify`は元のSUI receiptと今回の観測を再照合しないため、実行時の内容照合と保存済み記録の構造検査を区別してください。

この対応後も、SUI Document本文とDocument digestの再計算、実APIの認可、実資料の真正性・現行性・取得範囲、人による意味受理、公開権限は別の未検証範囲です。合成入力によるcard内容の照合で、それらを確認済みにはしません。
