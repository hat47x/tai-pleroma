# SUI DocumentV1 とTEIパイロット投影の差分

SUIの実装が持つ`DocumentV1`と、TEIパイロットが参照ローカルで投影してきた4つのrecord契約を突き合わせ、再構築に必要な差分を整理します。ここに書くのは差分の整理であり、SUIの意味の受理や実装の変更ではありません。

## 参照した版

- SUI: `0a19ec56`（`03_Implement/backend/src/sui_sensemaking_api/models.py`）
- TEIパイロット: `integrations/pilot-sui-document/candidates/*/contract.json`

## 対応表

### Document

| DocumentV1 | パイロット `sui.document.record` | 差分 |
| --- | --- | --- |
| `id` | `documentId` | 名前が違う |
| `title` | `title` | 同じ |
| `version`（`Literal[1]`） | なし | 未モデル |
| `createdAt` / `updatedAt` | なし（`digest`を代わりに置いた） | 未モデル。`digest`はSUIのフィールドではない |
| `transform` | なし | 未モデル |
| `cards` / `edges` / `islands` / `affiliations` など | 各recordへ分割 | 合成層で扱う前提 |

### Card

| Card | パイロット `sui.card.record` | 差分 |
| --- | --- | --- |
| `id` | `cardId` | 名前が違う |
| `text` | `text` | 同じ |
| `x` / `y` | なし | 未モデル |
| `claimType` / `mergedIntoCardId` / `repOf` / `canonicalId` / `sources` / `critique` / `critiqueTags` | なし | 未モデル |
| `textReviewed` / `holdState` / `meta` / `ka` / `critiqueHistory` | なし | 未モデル |

### Island

| Island | パイロット `sui.island.record` | 差分 |
| --- | --- | --- |
| `id` | `islandId` | 名前が違う |
| `cardIds` | なし | 未モデル。所属は合成層でCardの`documentId`だけを見ている |
| `title` / `summaryText` / `summaryGrounding` / `summaryHistory` | なし | 未モデル |
| `parentIslandId` / `placardCardId` / `collapsed` | なし | 未モデル |
| `geometry` / `shape` / `representativeCue` | なし | 未モデル |

### Edge と所属

| SUI | パイロット `sui.edge.record` | 差分 |
| --- | --- | --- |
| `id` | `edgeId` | 名前が違う |
| `fromId` / `toId` | `fromCard` / `toCard` | 名前が違い、Card専用になっている |
| `fromKind` / `toKind` | なし | Islandとの関係を表せない |
| `type` | `relation` | 名前が違う |
| `Affiliation`（card-island、多対多） | なし | 未モデル |

## 差分の分類

1. **識別子の名前**: SUIは`id`、パイロットは`documentId`/`cardId`/`islandId`/`edgeId`。再構築ではどちらかを正本に決める必要がある。
2. **関係の一般性**: SUIのEdgeは`fromKind`/`toKind`でCardとIslandの両方を端点にできる。パイロットはCard専用。
3. **所属**: SUIは`Island.cardIds`と`Affiliation`で所属を表す。パイロットは`documentId`の一致だけを見ている。
4. **未モデルの要素**: 座標、レビュー状態、保持状態、図形、ナラティブ、時刻、変換、監査系の履歴。
5. **パイロット固有**: `digest`はSUIのDocumentV1にはない。パイロットの合成用に足したフィールドで、製品契約ではない。

## 再構築への含意

- 現在のパイロットは「投影と合成の経路が成立するか」の証拠であり、DocumentV1の完全な写像ではない。
- 実装へ移す前に、識別子の名前と関係の一般性（Card/Island両対応）を決める必要がある。
- 座標・レビュー状態・図形などのUI寄りフィールドを、TEIの意味へ入れるか、表示側の派生にするかを決める必要がある。

## 暫定意思決定（AI）

- パイロットの契約は、DocumentV1の完全な写像を目指さない。投影・生成・合成の経路の証拠として維持する。
- 実装接続の最初の増分では、`id`への名前統一と`fromKind`/`toKind`の追加を行い、座標やレビュー状態は後回しにする。
- `digest`はパイロット固有として扱い、製品契約へ持ち込まない。

## 未確認

- SUI側のAPI境界（どのエンドポイントがDocumentV1のどの部分を受理するか）は、この整理では確認していない。
- フロントエンドの型とPythonモデルの一致は、SUI側の契約試験に委ねる。
- 実装接続の工数と影響範囲は未見積もり。

## 実装状況（2026-11-02）

契約v3で、識別子を`id`へ、Edgeを`fromId`/`toId`/`fromKind`/`toKind`へ統一しました。合成層も追従し、単体テスト6件と結合経路17ケースがPASSしています（[alignment receipt](../evaluations/records/SUI-TEI-alignment-2026-11-02.json)）。座標・レビュー状態・所属（`cardIds`/`Affiliation`）は引き続き未モデルです。

## 写像の範囲（2026-11-02の暫定決定）

- 投影する: Documentのidとoptionalなtitle、Cardのid/text/x/y/claimType/holdState/textReviewed、Islandのid/title/cardIds、Edgeのid/fromId/toId/type/fromKind/toKind、Affiliationのid/cardId/islandId。
- 投影しない: `critiqueHistory`などの構造体配列、`transform`、`createdAt`/`updatedAt`、図形・要約・履歴。これらはSUI側の元データを正本とする。
- artifactは読み取り専用で、SUIのDocumentV1そのものではない。
## 追加で分かった規則（2026-11-03）

- `DocumentV1`は、`Island.cardIds`の包含と`Affiliation`が同じ`(cardId, islandId)`を指すと拒否する。合成層とfixtureを、重複しない形へ変更した。
- 合成結果は、`transform`と時刻を供給すれば`DocumentV1.model_validate`を通る。

## 写像の実測（2026-11-06）

差分表を、実装のモデル定義と契約ファイルから機械的に数え直した。[receipt](../evaluations/records/SUI-TEI-document-coverage-2026-11-06.json)

| 意味の単位 | モデルのフィールド数 | 契約のフィールド数 | 覆われた割合 | 覆われた項目 |
| --- | --- | --- | --- | --- |
| DocumentV1 | 24 | 3 | 0.125 | id / title / readingOrder |
| Card | 16 | 8 | 0.5 | id / text / x / y / claimType / holdState / textReviewed / sources |
| Island | 20 | 3 | 0.15 | id / title / cardIds |
| Edge | 6 | 6 | 1.0 | すべて |

- Edgeは端点種別まで含めて完全に写せている
- DocumentV1の未写像21項目は、カード・島・関係の集合（`cards`/`edges`/`islands`/`affiliations`/`voids`/`narratives`/`evidenceLinks`/`shelf`）、決定と履歴（`reviewAttribution`/`structureDecisions`/`mergeSuggestionDecisions`/`contradictionSignalDecisions`/`critiqueInputs`/`reproposalDiffs`/`patchApplyLog`/`relationSummaries`/`deterministicTieBreak`）、時刻と変換（`createdAt`/`updatedAt`/`transform`）、版（`version`）に分かれる
- 集合と決定の集合は合成層が担う設計だが、**それらを1つのrecordで表すには入れ子投影が要る**（[入れ子の実測](tei-sui-integration-2026-11-03.md)）
- パイロット固有のフィールドは残っていない（`digest`は撤去済み）

この数値は名前の一致だけを数えたもので、型・意味の一致は含まない。

## 型の一致（2026-11-06）

名前の一致だけでなく、SUIの型注釈と契約の`primitive`を突き合わせた。[receipt](../evaluations/records/SUI-TEI-document-types-2026-11-06.json)

```text
primitiveの不一致: なし（4単位・18フィールド）
コレクション（many）の不一致: なし
Optionalの不一致: Edge.fromKind / Edge.toKind
```

- SUIが`Literal[...]`で表す列挙は`std.code`、数値は`std.decimal`、真偽値は`std.boolean`へ対応する
- SUIが`str`で持つ`Edge.type`と`Card.claimType`/`holdState`は、契約側で`std.code`へ狭めている。値の集合を契約で持たないため、狭めた分は契約の外で担保する必要がある
- **SUIは`Edge.fromKind`/`toKind`を`Optional`として許すが、契約は必須にしている。** 実測すると、キーが無い場合は`missing`（欠けた項目名を返す）、JSONの`null`は`unresolved`になり、いずれも投影されない（[receipt](../evaluations/records/SUI-TEI-edge-optionality-2026-11-06.json)）。端点種別を持たないSUIのEdgeは、この契約では失われる。差分表の「未モデル」とは別種の、必須性の不一致である

## 合成層の端点種別の扱い（2026-11-06）

投影契約が端点種別を必須にしている一方、合成層（`document_assembler.py`）は欠落時に`card`を仮定する。[receipt](../evaluations/records/SUI-TEI-assembler-kinds-2026-11-06.json)

```text
明示的な種別 → その種別で解決
種別なし（card→card） → 合成される（出力の種別は null のまま）
種別なし（card→island） → 拒否（island を card として解決するため）
明示的な null → 種別なしと同じ扱い
未知の種別 → 拒否
```

初回の実測では、欠落時に`card`を仮定していた。これを**端点IDから解決する**よう変更した（[再実測](../evaluations/records/SUI-TEI-assembler-kinds-2026-11-06.json)）。

```text
種別なし（card→card） → 解決して合成（出力の種別は投影どおり）
種別なし（card→island） → 解決して合成（以前は誤って拒否）
端点が未知 → 拒否「no such endpoint」
端点がcardとislandの両方に一致 → 拒否「ambiguous endpoint」
```

- 仮定ではなく端点の同一性で種別を決めるため、**card→islandのEdgeが種別を欠いても失われない**
- 端点が特定できない場合は推測せず拒否する（fail-closed）
- 合成後のEdgeは投影された種別をそのまま保つ（解決結果を書き戻さない）
- 契約を任意に寄せた（`edge-record` v4、[receipt](../evaluations/records/SUI-TEI-edge-optional-contract-2026-11-06.json)）。**投影から合成までの一貫を実測した**（[chain](../evaluations/records/SUI-TEI-edge-chain-2026-11-06.json)）: 種別なしのcard→islandが投影され合成され、端点が解決できなければ拒否される
- 単体試験13件がPASS（[receipt](../evaluations/records/SUI-TEI-assembler-tests-2026-11-06.json)）

## 端点種別を任意にした契約の試作（2026-11-06）

製品（SUI）が端点種別を任意にしている以上、契約側を任意に寄せる選択肢はTAIで試せる。試作して生成器に通した。[receipt](../evaluations/records/SUI-TEI-edge-optional-contract-2026-11-06.json)

```text
両方あり → present（種別をそのまま投影）
種別なし → present（種別を出力から省略）
片方だけ null → present（もう片方の種別は残る）
```

- **任意にした契約は問題なく受理され、生成器も種別なしのEdgeを投影できる。** 現行契約の必須性は、製品の任意性に対して厳しすぎたことが分かる
- これで「端点種別を持たないSUIのEdgeが投影で失われる」問題は、契約側の変更で解ける。TEI側の変更を要さない
- ただし合成層（`document_assembler.py`）は依然として`card`を仮定する。投影で種別を省略した場合、合成側で「種別なし」をどう扱うかを別に決める必要がある
- 現行のパイロット契約は必須のまま維持した。契約版の更新は、合成層の扱いと併せて判断する