# SUI DocumentV1投影のTEIパイロットモデル

状態: **パイロット段階1（意味のモデル化）**。生成・実行・配備はまだ行っていません。

## 目的

[TEIによるプロダクト構築への移行計画](../../docs/tei-construction-migration-plan.md)の段階1として、SUIのDocumentV1読み取りとcard/island/edge投影を、TEIの三視点のうちデータと機能の意味へ写します。業務の視点（誰が意味を受理するか）は、このモデルに含めません。

## 範囲

- データ: `Document`、`Card`、`Island`、`Edge`と、その識別子・本文・digest
- 機能: 4つの`record`パターン（document、card、island、edge）
- アプリケーション: `sui_document_projection`

含めないもの:

- 画面、認可、テナント分離
- 永続化、API、実行先
- 意味形成の手順と判断
- SUIの実装コードの生成

## 再現

TEIのチェックアウトで実行します。

```sh
go run ./cmd/tei validate -workspace <TAI>/integrations/pilot-sui-document
go run ./cmd/tei world -workspace <TAI>/integrations/pilot-sui-document
go run ./cmd/tei source-index -workspace <TAI>/integrations/pilot-sui-document -subject-kind semantic-data -subject-id sui.document
```

`validate`が`ok`を返し、`world`が`sui.document`などの識別子を表示し、`source-index`が定義位置と指紋値を返すことを確認します。

## このモデルが示すこと・示さないこと

示すこと:

- SUIのdocument/card/island/edgeを、TEIの意味モデルとして表現できる
- `validate`が通り、意味の識別子と定義位置を機械的に引ける

示さないこと:

- 意味から成果物を生成できること
- 生成物が適合試験を通ること
- 実行先で動作すること
- 人が意味を受理したこと
- 生成AIの効率や自律性が向上したこと

## 段階2の試行結果（2026-11-01）

生成へ進めるかを確認するため、TEIの`reference-generator-selection`を2通りで試しました。

1. 既存の数値契約をこの作業領域へ適用すると、`accepted attribute sales.order_line.quantity was not found in the Workspace`で拒否されました。契約の属性がWorkspaceに存在することを前提にしています。
2. `std.text`だけの契約を作り、`tei-generator-build -strategy template`へ渡すと、`contract rounding precision/scale is invalid`で拒否されました。生成器の契約が数値・money・roundingを前提にしています。

このため、SUIのrecord/string投影は、現状の生成器では生成できません。不足は[tei-platform #2488](https://github.com/hat47x/tei-platform/issues/2488)へ記録しました。段階2は、TEI側の生成契約が整うまで停止します。回避のための別実装をTAI側へ追加しません。

必要な拡張の案と受入試験は[TEI-GAP.md](TEI-GAP.md)に置きました。TEI側の設計判断を拘束しない提案です。

その後、TEI側でspike（[PR #2489](https://github.com/hat47x/tei-platform/pull/2489)）が統合され、`std.text`の契約を`rounding`なしで記述し、`present`・`empty`・`missing`・`unresolved`の4ケースを区別して比較できることを確認しました。

さらに、文字列投影を既存の`reference-generator-selection`へ取り込み（[PR #2520](https://github.com/hat47x/tei-platform/pull/2520)）、この作業領域の`candidates/text-identity`を選抜できることを確認しました。4ケースが一致し、`qualified=["text-identity"]`、`passed=true`です（[receipt](../../evaluations/records/SUI-TEI-selection-2026-11-01.json)）。

続いて、`text-template`戦略を追加し（[PR #2524](https://github.com/hat47x/tei-platform/pull/2524)）、同じ契約から候補を**生成**して選抜しました。4ケースが一致し、`qualified=["text-template"]`、`passed=true`です（[receipt](../../evaluations/records/SUI-TEI-text-generation-2026-11-01.json)）。

これで「意味（TEIの契約）→生成器→候補→適合fixtureによる選抜」の最小経路が、文字列投影の1属性で通りました。

さらに、`profiles/oneshot.json`を追加し、`tei-target-profile run`で同じ候補をone-shotのTarget Profileで実行しました。4ケースが`exitCode=0`で一致し、`processModel=oneshot`、`generatorId=text-template`、`passed=true`です（[receipt](../../evaluations/records/SUI-TEI-target-2026-11-01.json)）。ただし、これは同じホスト上の参照実行であり、実機・実OS・実配備を示しません。

生成したのは投影の候補であり、SUIの実装コードでも実行可能な画面・APIでもありません。段階2は最小経路とTarget Profile実行まで到達し、複数属性・record全体・実環境が残っています。

### 複数属性への拡張（2026-11-02）

`candidates/document-id/`に2つ目の契約（`sui.card.document_id`）を追加し、同じ`text-template`で生成・選抜しました。4ケースが一致し、`qualified=["text-template"]`、`passed=true`です（[receipt](../../evaluations/records/SUI-TEI-multi-attribute-2026-11-02.json)）。

これは属性ごとに独立した契約を持つ段階であり、Card全体を1つのrecordとして投影する契約ではありません。

### record全体への拡張（2026-11-02）

`candidates/card-record/`に、Cardの`text`と`documentId`を1つのrecordとして投影する契約を追加しました。`projection.kind=record`と`fields`を使い、`text-record-template`（[PR #2549](https://github.com/hat47x/tei-platform/pull/2549)）で生成しました。

```text
present:    {"documentId":"doc-1","text":" hello "}
missing:    ["text"]
unresolved: （値なし）
```

4ケースが一致し、`qualified=["text-record-template"]`、`passed=true`、`profiles/record.json`のone-shot実行も`passed=true`です（[receipt](../../evaluations/records/SUI-TEI-card-record-2026-11-02.json)）。

record投影は、Cardの2属性に限った参照ローカルの実装です。Cardの他の属性、Island/Edge、実装コードの生成は未達です。

## 段階3の最初の測定（2026-11-02）

`measure_workflow.py`で、生成と選抜のツール工程を測定しました。

```sh
python integrations/pilot-sui-document/measure_workflow.py \
  --tei-repo <TEI> --workspace integrations/pilot-sui-document \
  --contract .../contract.json --fixtures .../fixtures.json \
  --out evaluations/records/SUI-TEI-workflow-2026-11-02.json
```

観測（1回、Windows、同じホスト）:

| 項目 | 値 |
| --- | --- |
| generate | 406ms |
| select | 3312ms |
| cases | 4 |
| 人の介入（呼び出し側の申告） | 0 |
| 自律ステップ | 2 |

receipt: [SUI-TEI-workflow-2026-11-02.json](../../evaluations/records/SUI-TEI-workflow-2026-11-02.json)

これはツール工程の時間・試行回数・介入回数の記録であり、生産性や自律性の証明ではありません。

## 比較測定（T1、2026-11-02、参考）

評価集合を1課題に固定しました。

```text
T1: 投影の種別を normalize（前後空白の除去）から identity へ変える
契約: sui.card.text
fixture: present / empty / missing / unresolved の4ケース
```

`compare_workflow.py`で、TEI経路と、手書き候補を直接編集する経路を同じfixtureで実行しました。

| 項目 | TEI経路 | 手書き経路 |
| --- | --- | --- |
| 結果 | PASS | PASS |
| 経過時間 | 3500ms | 1485ms |
| 契約の変更行 | 2 | - |
| ソースの変更行 | - | 3 |
| fixtureの変更行 | 2 | 2 |

receipt: [SUI-TEI-compare-2026-11-02.json](../../evaluations/records/SUI-TEI-compare-2026-11-02.json)

**この比較は生産性の評価ではありません。** 本開発はPoCであり、生産性はプロダクト完成後に評価します。このreceiptは生成AIが自分の進め方を振り返るための材料であり、人による受入判定や生産性の基準にはしません。

比較から言えるのは、TEI経路では契約とfixtureが変更面になり、同じ4ケースで両経路を検証できることです。人の作業時間、学習曲線、長期保守は測っておらず、PoC中には測りません。

## 配備とロールバック（2026-11-02）

`profiles/rolling.json`を追加し、`tei-target-profile deploy`で異なる2つの生成物を順に配置してから、`rollback`を実行しました。

```text
1回目: slot=a, rollbackAvailable=false
2回目: slot=b, previousSlot=a, rollbackAvailable=true
rollback: passed=true, slot=a, previousSlot=b
```

receipt: [SUI-TEI-deploy-2026-11-02.json](../../evaluations/records/SUI-TEI-deploy-2026-11-02.json)

これはローカルfilesystem上のslot切替であり、実Target、supervisor、無停止更新、health check、drainを示しません。

## Island/Edgeへの拡張（2026-11-02）

`candidates/island-record/`と`candidates/edge-record/`を追加し、同じ`text-record-template`で生成・選抜・実行しました。

```text
sui.island.record: islandId, documentId
sui.edge.record:   edgeId, fromCard, toCard, relation
```

どちらも4ケースが一致し、`qualified=["text-record-template"]`、`passed=true`、`profiles/record.json`のone-shot実行も`passed=true`です（[receipt](../../evaluations/records/SUI-TEI-island-edge-2026-11-02.json)）。

Edgeのfrom/toは、入れ子の参照ではなく識別子の組（`fromCard`、`toCard`）としてflatなrecordに置きました。

### Document本体のrecord（2026-11-02）

`candidates/document-record/`に、Documentの`documentId`・`title`・`digest`を投影する契約を追加しました。

```text
sui.document.record: documentId, title, digest
```

4ケースが一致し、`qualified=["text-record-template"]`、`passed=true`、one-shot実行も`passed=true`です（[receipt](../../evaluations/records/SUI-TEI-document-record-2026-11-02.json)）。

Documentは、Document・Card・Island・Edgeの4つのflat recordをアプリケーション側で合成する形です。入れ子のDocument契約は作っていません。

### 合成層（2026-11-02）

`assembler/document_assembler.py`で、4つのflat recordを1つのDocumentへ合成します。

- 同じ`documentId`に属するか
- Card/IslandのIDが重複していないか
- Edgeの`fromCard`/`toCard`が実在するか

を検査し、不整合は`AssemblyError`にします。`python -m unittest`で6件がPASSしました（[receipt](../../evaluations/records/SUI-TEI-assembler-2026-11-02.json)）。

あわせて`sui.card.record`へ`cardId`を追加し、4ケースの選抜を再実行しました（`qualified=["text-record-template"]`、`passed=true`）。

### 結合経路（2026-11-02）

`assembler/integration_flow.py`で、4つの契約から候補を生成し、各候補を実行して、presentの出力を合成層へ渡しました。

```text
contracts: 4
cases: 17/17 PASS
composed: cards=2, islands=1, edges=1
dangling edge: rejected
```

生成した候補を実際にプロセスとして実行し、その標準出力を入力にしている点が、これまでの選抜との違いです。結合経路全体は[receipt](../../evaluations/records/SUI-TEI-integration-flow-2026-11-02.json)に記録しました。

### SUI名への統一（契約v3、2026-11-02）

差分整理で挙げた識別子名とEdgeの端点種別を、契約v3でSUIに寄せました。

```text
Document: id, title
Card:     id, text
Island:   id, title
Edge:     id, fromId, toId, type, fromKind, toKind
```

- `sui.edge.from_id` / `to_id` / `from_kind` / `to_kind`を意味モデルへ追加
- 合成層を`id`と`fromKind`/`toKind`へ追従（`card`/`island`の両端を解決）
- 単体テスト6件と結合経路17ケースを再実行

結合経路は`cases=17/17`、`composed=2 cards, 1 island, 1 edge`、未知端点のEdgeは拒否です（[receipt](../../evaluations/records/SUI-TEI-alignment-2026-11-02.json)）。

### Affiliationの投影（2026-11-02）

CardとIslandの多対多所属を表す`sui.affiliation.record`を追加しました。

```text
sui.affiliation.record: id, cardId, islandId
```

意味モデルへ`Affiliation`を追加し、合成層は所属のCard/Islandが実在するかを検査します。単体テスト8件と、5契約を通す結合経路21ケースがPASSしました（[receipt](../../evaluations/records/SUI-TEI-affiliation-2026-11-02.json)）。

`Island.cardIds`（Island側の包含リスト）は、投影契約が配列を扱えないため未対応です。所属はAffiliationで表す暫定決定とします。

### 配列投影とIsland.cardIds（2026-11-02）

投影フィールドに`many`を追加し（[PR #2576](https://github.com/hat47x/tei-platform/pull/2576)）、`sui.island.record`をv4へ上げて`cardIds`を文字列配列として投影しました。

```text
sui.island.record: id, title, cardIds[]
```

- 空配列は`present`で`[]`
- 欠落は`missing`、`null`は`unresolved`
- 合成層は`cardIds`の各要素が実在するCardを指すか検査

単体テスト9件と結合経路21ケースがPASSしました（[receipt](../../evaluations/records/SUI-TEI-island-cardids-2026-11-02.json)）。

### 暫定意思決定（AI）

- Document全体は、flatなrecordを要素ごとに投影し、アプリケーション側で合成する。入れ子のDocument契約は、TEIの投影契約が複合構造を扱えるようになるまで作らない。
- Edgeの関係は、`relation`を`std.code`の文字列として保持する。関係の意味の検証は、この契約では行わない。

## SUI本体との差分

DocumentV1と現在の投影契約の差分は[SUI DocumentV1とTEI投影の差分](../../docs/sui-documentv1-tei-gap.md)に整理しました。名前・関係の一般性・未モデル要素が残っています。

## SUI API境界への接続案

`GET /docs/{doc_id}/epistemic/projection`を最初の接続面とする案を[SUI API境界とTEI投影の接続案](../../docs/sui-api-boundary-tei-mapping.md)に整理しました。読み取り専用のartifact kind追加を先に行い、DocumentV1の書き込みは後回しにします。

## 投影artifactの生成（2026-11-02）

結合経路に`--artifact-out`を追加し、SUIが読める形のJSONを生成しました。

```json
{
  "schema": "tai.reference.tei-documentv1-projection/v0",
  "contract": {"id": "sui.documentv1.projection", "version": "1"},
  "source": {"teiCommit": "...", "contracts": {"...": {"sourceDigest": "...", "cases": 4}}},
  "document": {"document": {...}, "cards": [...], "islands": [...], "edges": [...], "affiliations": [...]}
}
```

- [artifact](../../evaluations/artifacts/documentv1-projection.json)
- [receipt](../../evaluations/records/SUI-TEI-artifact-2026-11-02.json)
- receiptはartifactのpathとdigestを保持し、checkerが実ファイルのdigestと照合します

このartifactはまだSUIへ配置していません。SUI側のartifact kind追加と運用者バインディングが次の接続点です。
