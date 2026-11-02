# TEI投影パイロットの手順

SUIのDocumentV1で通した手順を、別の製品・別の要素へ流用するための覚書。コマンドはTAIのリポジトリルートで実行する。

## 1. セマンティックモデル

`integrations/pilot-sui-document/semantic/sui/document.tei`を雛形にする。

```tei
namespace <product>

data <Element> {
    attribute <element>Id type std.identifier
    attribute <field> type std.text
}
```

- 配列は契約側で`many`、真偽値は`std.boolean`、数値は`std.decimal`
- 省略可能な項目は契約側で`optional`

## 2. 契約とfixture

`candidates/<element>-record/contract.json`と`fixtures.json`を作る。

```json
{
  "schema": "tei.reference.generator-contract/v0",
  "id": "<product>.<element>.record",
  "version": "1",
  "projection": {
    "kind": "record",
    "fields": [
      {"name": "id", "input": "id", "attribute": "<product>.<element>.<element>Id", "primitive": "std.identifier"}
    ]
  }
}
```

fixtureは`present`・`missing`・`unresolved`の3種類を最低限そろえる。

## 3. 生成と選抜

```sh
go run ./tools/reference-generator-selection/cmd/tei-generator-build \
  -contract <contract.json> -strategy text-record-template -out <candidate-dir>

go run ./tools/reference-generator-selection/cmd/tei-generator-select \
  -workspace integrations/<pilot> -contract <contract.json> \
  -fixtures <fixtures.json> -candidates <candidate-dir>
```

- `identity`/`normalize`は`text-template`、`record`は`text-record-template`
- 両方を混ぜると拒否される

## 4. 合成とartifact

```sh
python integrations/<pilot>/assembler/integration_flow.py \
  --tei-repo <TEI> --workspace integrations/<pilot> \
  --out <receipt.json> --artifact-out <artifact.json>
```

- 参照整合性（Edge端点、Islandの`cardIds`、Affiliation）を合成時に検査する
- `Island.cardIds`と`Affiliation`は同じ組を指してはいけない

## 5. artifactの検証

```sh
python integrations/<pilot>/assembler/validate_artifact.py --artifact <artifact.json>
python integrations/<pilot>/assembler/validate_against_sui.py \
  --sui-repo <SUI> --artifact <artifact.json> --out <receipt.json>
```

- `transform`と時刻は投影に含まれない。呼び出し側が渡す`n- `source.contracts[].sourceDigest`は契約JSONのハッシュではなく、生成された候補ソースのdigest。契約ファイルの同一性確認には使えない
- 保存契約はpayloadに`schemaVersion`を要求しない

## 6. 保存

```sh
python integrations/<pilot>/assembler/plan_save_cli.py \
  --sui-repo <SUI> --artifact <artifact.json> \
  --existing <document.json> --out <plan.json>

python integrations/<pilot>/assembler/save_to_sui.py \
  --sui-repo <SUI> --artifact <artifact.json> --api-key <key> --out <receipt.json>
```

- 既存文書はマージ前に`validate_existing_document`で検証する
- 保存は`plan_save(preserve_existing=True)`のpayloadを使う
- 古い`If-Match`は409

## 7. 記録

- 実実行は`synthetic: false`、`evidenceKind: real-execution`
- 合成fixtureは`synthetic: true`、`evidenceKind: synthetic`にして区別する
- receiptは`tools/check-synthetic-receipts/check.py`の対象へ追加する

## つまずいた点

- 契約のattribute名がセマンティックモデルにないと選抜が落ちる
- 契約のdigestは改行コードに影響される。LFに統一する
- `null`は`unresolved`、欠落は`missing`。fixtureで両方を固定する
- 既存文書の不正フィールドは非破壊マージで残る。マージ前検証が必要
- 本番DB・TLS・実配備はこの手順に含まれない
