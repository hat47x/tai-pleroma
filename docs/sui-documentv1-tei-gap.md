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

- 投影する: Documentのid/title、Cardのid/text/x/y/claimType/holdState/textReviewed、Islandのid/title/cardIds、Edgeのid/fromId/toId/type/fromKind/toKind、Affiliationのid/cardId/islandId。
- 投影しない: `critiqueHistory`などの構造体配列、`transform`、`createdAt`/`updatedAt`、図形・要約・履歴。これらはSUI側の元データを正本とする。
- artifactは読み取り専用で、SUIのDocumentV1そのものではない。