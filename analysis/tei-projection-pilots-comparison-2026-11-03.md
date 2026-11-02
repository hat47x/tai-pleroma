# TEI投影パイロットの横断比較

2026-11-03時点。SUI・SEI・MMI・EKIの4パイロットを、artifactの形と到達点で比べる。受入判断ではない。

## 共通の封筒

4つとも同じ形の封筒を使う。

```text
schema     投影の種類を表す文字列
contract   {id, version}
source     {teiCommit, contract{contractId, contractVersion, contractDigest, sourceDigest, cases}}
<payload>  製品ごとの本体
```

- `contractDigest`は契約JSONのLF正規化ハッシュ
- `sourceDigest`は生成候補ソースのdigest
- `teiCommit`は生成に使ったTEIのコミット

## 本体の違い

| 製品 | payload | 要素数 | 参照整合性 |
| --- | --- | --- | --- |
| SUI | `document`（Document/Card/Island/Edge/Affiliation） | 複数 | あり（端点・cardIds・所属） |
| SEI | `decision` | 単一 | なし |
| MMI | `profile` | 単一 | なし |
| EKI | `taskRequest` | 単一 | なし |

## 到達点

| 製品 | 選抜 | artifact | スキーマ検証 | 製品側consumer | 保存 |
| --- | --- | --- | --- | --- | --- |
| SUI | 21ケース | あり | あり | あり（Python） | あり（HTTP・一時SQLite） |
| SEI | 4ケース | あり | あり | あり（Go） | なし |
| MMI | 3ケース | あり | あり | あり（TypeScript） | なし |
| EKI | 4ケース | あり | あり | なし | なし |

## 投影の表現力

| 機能 | 使用例 |
| --- | --- |
| 必須の文字列・識別子 | 4製品すべて |
| optional | SUI（title/claimType/holdState/textReviewed）、EKI（priority/clientRequestId） |
| 配列 | SUI（sources/readingOrder/cardIds） |
| 真偽値 | SUI（textReviewed） |
| 数値 | SUI（x/y） |
| 構造体配列 | 対象外（4製品とも） |

## 分かったこと

- 封筒を共通にすると、製品ごとの違いをpayloadへ閉じ込められる
- 単一recordの製品は、選抜からartifactまでが短く、同じ手順で4製品に広げられた
- 参照整合性が必要なのはSUIだけで、合成層に検査を置く形が合う
- 製品側consumerはSUI（Python）・SEI（Go）・MMI（TypeScript）にある。SEIとMMIは実artifactの読み取りまで確認済み。SEIは実artifactの読み取りまで確認済み。保存まで進んだのはSUIだけ

## つまずきの共有

- `tei.workspace.yaml`がないと選抜が落ちる
- TEIの属性名はcamelCaseからsnake_caseへ写される
- Windowsでは`TMP`/`TEMP`が書き込み可能な場所でないと生成に失敗する
- Goの出力はUTF-8で読む
- receipt名に`TEI-pilot`を含めると既存の検証規則に当たる

## 次の候補

1. 単一record製品のいずれかでconsumerを作る
2. 4製品のartifactを同じ手順で再生成できるか確認する
3. 本番DB・配備の検証

公開gateは`blocked`のまま。外部作用・公開は未承認。
