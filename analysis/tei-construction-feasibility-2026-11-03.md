# TEIによる構築のフィージビリティ（2026-11-03時点）

Status: **中間整理**。生産性や受入の判定ではない。判断材料と未検証を並べるだけの文書。

## 何を確かめたか

「TEIで製品の意味モデルを記述し、そこから投影artifactを作り、製品側で読めるか」を、4製品で試した。

| 製品 | 記述した範囲 | 到達点 |
| --- | --- | --- |
| SUI | Document / Card / Island / Edge / Affiliation | 合成・スキーマ・保存・往復・TLS・Postgres |
| SEI | Decision の平坦部分 | artifact・consumer・実artifact読み取り |
| MMI | Format Profile の平坦部分 | artifact・consumer・実artifact読み取り |
| EKI | TaskRequest の平坦部分 | artifact・consumer spike |

## 手順として再利用できたこと

4製品で同じ順序が使えた。

1. `.tei`で意味モデルを書く
2. `contract.json`で投影を定義する
3. `fixtures.json`で入出力を固定する
4. `run_selection.py`で生成・選抜する
5. artifactを作り、JSON Schemaで検証する
6. 製品側のconsumerで読む

SUIだけは複数要素の合成が必要で、`document_assembler.py`と参照整合性の検査を足した。他の3製品は単一recordで、手順はほぼ同じだった。

## 得られた知見

- artifactの封筒（schema / contract / source / payload）を共通にすると、製品ごとの違いをpayloadへ閉じ込められる
- `contractDigest`と`sourceDigest`は別物で、混同すると検証が壊れる
- TEIの属性名はcamelCaseからsnake_caseへ写される
- Windowsでは`TMP`/`TEMP`が書き込み可能でないと生成に失敗する
- Goの出力はUTF-8で読む
- consumerは製品本体の境界の外に置くと、製品の設計判断を変えずに読み取り契約だけを確かめられる
- receiptを機械検証すると、成功の記録と失敗の記録を混ぜない運用が必要になる

## 失敗から分かったこと

- Postgresの409は、テナント行の欠落による外部キー違反だった。ルートが409へ変換するため、原因が見えにくい
- SaaSプロファイルは6項目の外部前提が揃うまで起動しない。stubのURLでも起動自体は通るが、実認証の証明にはならない

## 未検証

- 実データでの投影（すべて合成fixture）
- 製品側の保存・実行のうち、EKIの実行は製品テストで成立を確認済み（本番Worker Protocol互換と結果受入の配線は未確認）
- SaaSの外部認証・ポリシー・capabilityの実接続
- 管理DB、TLS証明書の実CA、リバースプロキシ、実配備
- 生産性・開発効率の測定（PoC完了後に評価する前提）

## 判断しないこと

- 生産性が上がったかどうか
- 受入可否、公開可否
- 製品の設計をTEI前提へ変えるかどうか

## 次に進むなら

1. 1製品で、投影から保存・実行までを製品側の経路で通す
2. SaaSの外部署をstubではなく実物にする
3. 管理DB・TLS・配備を実環境に近づける
4. 実データを扱う範囲と、扱わない範囲を決める

## 残課題の整理\n\n確認できたことと残っていることを[Issue #394](https://github.com/hat47x/tai-pleroma/issues/394)へまとめた。受入判断ではない。\n\n## 100ラウンド時点の追記

- 4製品のartifact・正規レコード化・consumer・実artifact読み取りが揃った
- SUIは保存・往復・TLS・Postgres・ETag・競合・再試行まで確認した
- EKIは投影TaskRequestの投入（202/queued）と、policy/Worker行を入れた場合の`running`到達まで確認した
- 一括検証は16段（checker・artifact・digest・シナリオ・pipeline・compose・TLS・Postgres・migration・ETag・同時更新・継続競合・再試行・複数文書・レコード・EKI投入）
- 実行・結果受理、SaaS外部認証、管理DB・実CA・配備は未検証のまま

## 到達点の更新（2026-11-06）

初版の記述のうち、その後の実執行で変わった点を記す。数値は同日時点の実実行receiptに基づく。

| 項目 | 初版 | 現在 |
| --- | --- | --- |
| EKIの実行 | 未配線 | 製品テストでHTTP投入→Agent実行→claim受理を確認。自前のControl Plane設定・Trust Anchor・Agent設定でも実行とclaimまで到達 |
| EKIの登録・失効 | 未確認 | mTLSで登録でき、失効は最終状態。失効後は認証段で401 |
| SUIの保存 | 合成文書 | Postgres・TLS・ローカルCA・TLS終端プロキシ・2インスタンス共有でも確認 |
| SUIの製品面 | 未確認 | 監査エクスポート・管理APIの認証分離・利用者provision・TEI artifact配信・context query/bundle・CE4 resolve・モデル登録を確認 |
| 実行結果の受入 | 未配線 | 未配線のまま。claimは`new`で止まり、result APIは`409 RESULT_NOT_READY` |
| 複数Workerの分散 | 未確認 | 2台登録は成功。同時投入ではdispatchが一部を`NOT_YET_VALID`で延期し、Attemptが2件しか作られなかった |

未確認のまま残るもの: 実データ・実テナント・実IdP、管理DB、公開CA、本番Worker Protocol互換、結果受入の配線、複数Workerの分散、生産性の測定。

これらはTAI側の接続では解消できず、製品側の判断（受入の配線、時計の計測）か、利用可能な実インフラを要する。