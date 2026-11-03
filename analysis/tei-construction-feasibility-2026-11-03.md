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
- 製品側の保存・実行（SUI以外は読み取りのみ。EKIはTask受理までで、実行系は未配線。Dispatchを有効にしpolicyを投入すると配置は検討するが、Worker未登録のため止まる）
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
