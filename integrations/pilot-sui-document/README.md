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
- 欠落は`missing`、
ull`は`unresolved`
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

## SUI側の読み取り接続（2026-11-02）

SUIのartifact kind許可リストへ`documentv1-projection`を追加し（[sui-sensemaking #3364](https://github.com/hat47x/sui-sensemaking/pull/3364)、`963adb0`）、TAIのartifactをtenant別ディレクトリから読めることを確認しました。

```text
read:            PASS（payloadがartifactと一致）
tenant isolation: PASS（別tenantはnot-a-file）
```

- [receipt](../../evaluations/records/SUI-TEI-sui-reader-2026-11-02.json)
- SUIのtransport moduleを直接読み込み、HTTPサーバ・認証・配備は通していません

## 運用者バインディング（2026-11-02）

`assembler/install_artifact.py`で、artifactを`tenants/<tenant>/<doc>/documentv1-projection.json`へ置き、`epistemic-bindings.json`へバインディングを記録します。

```sh
python integrations/pilot-sui-document/assembler/install_artifact.py \
  --root <SUI_TEI_REFERENCE_DIR> --tenant tenant-a --doc doc-1 \
  --artifact evaluations/artifacts/documentv1-projection.json
```

`verify_sui_reader.py`で、バインディングの解決と読み取りを確認しました。

```text
binding resolved: PASS（documentv1-projection）
read:             PASS（payloadがartifactと一致）
tenant isolation: PASS（別tenantはnot-a-file）
```

- [receipt](../../evaluations/records/SUI-TEI-binding-2026-11-02.json)
## 座標の投影（Card v5、2026-11-02）

TEIの数値投影（[PR #2578](https://github.com/hat47x/tei-platform/pull/2578)）を使い、Card record v5へ`x`と`y`を追加しました。

```text
sui.card.record: id, text, x, y
```

- `std.decimal`のフィールドはJSON数値として出力
- 合成層は値の型に依存しない
- 21ケースPASS、単体9件PASS

- [receipt](../../evaluations/records/SUI-TEI-coordinates-2026-11-02.json)
- [artifact](../../evaluations/artifacts/documentv1-projection.json)

`claimType`・`textReviewed`・`holdState`などのoptionalな列挙・真偽値は未対応です。record契約は全フィールド必須のため、optionalを扱うには別の表現が必要です。
## optionalフィールド（Card v6、2026-11-02）

TEIのoptional投影（[PR #2580](https://github.com/hat47x/tei-platform/pull/2580)）を使い、Card record v6へ`claimType`と`holdState`をoptionalとして追加しました。

```text
sui.card.record: id, text, x, y, claimType?, holdState?
```

- 入力に存在しない、またはnullのoptionalフィールドは出力から省略
- 必須フィールドの`missing`/`unresolved`は従来どおり
- 21ケースPASS、単体9件PASS

- [receipt](../../evaluations/records/SUI-TEI-optional-2026-11-02.json)
- [artifact](../../evaluations/artifacts/documentv1-projection.json)

`textReviewed`や`critiqueHistory`のような真偽値・配列のoptionalは未対応です。
## 真偽値（Card v7、2026-11-02）

TEIの真偽値投影（[PR #2581](https://github.com/hat47x/tei-platform/pull/2581)）を使い、Card record v7へ`textReviewed`をoptionalの真偽値として追加しました。

```text
sui.card.record: id, text, x, y, claimType?, holdState?, textReviewed?
```

- `true`/`false`をJSON真偽値として出力
- 欠落時は出力から省略
- 21ケースPASS、単体9件PASS

- [receipt](../../evaluations/records/SUI-TEI-reviewed-2026-11-02.json)
- [artifact](../../evaluations/artifacts/documentv1-projection.json)

`critiqueHistory`のような構造体の配列は未対応です。
## artifactの構造検証（2026-11-02）

`assembler/validate_artifact.py`で、artifactのenvelopeと要素の形を検査します。

```text
schema / contract / source.teiCommit
document.id、cards[].id/text/x/y、islands[].cardIds
edges[].fromId/toId/type/fromKind/toKind、affiliations[]
```

`check_artifact.py`でreceiptを出し、13件の単体テストがPASSしました（[receipt](../../evaluations/records/SUI-TEI-artifact-validation-2026-11-02.json)）。

### 写像の範囲（暫定）

- 対象: Document(id,title)、Card(id,text,x,y,claimType,holdState,textReviewed)、Island(id,title,cardIds)、Edge(id,fromId,toId,type,fromKind,toKind)、Affiliation(id,cardId,islandId)
- 対象外: `critiqueHistory`などの構造体配列、`transform`、`createdAt`/`updatedAt`、図形・要約・履歴
- 対象外は、投影契約ではなくSUI側の元データを正本とする
## Document/Islandのoptional title（2026-11-02）

SUIの`DocumentV1.title`と`Island.title`はoptionalなので、契約を合わせました。

```text
sui.document.record v4: id, title?
sui.island.record v5:   id, title?, cardIds[]
```

- `title`がない場合は出力から省略
- `id`と`cardIds`は必須のまま
- 21ケースPASS、単体13件PASS

- [receipt](../../evaluations/records/SUI-TEI-optional-core-2026-11-02.json)
## 管理経路の読み取り（2026-11-02）

SUIの管理経路面（`GET /admin/tei-epistemic/artifacts/{artifact_kind}`）でも同じartifact kindを読めることを確認しました。

```text
tenant binding: PASS
read:           PASS
tenant isolation: PASS
admin path:     PASS
```

`verify_sui_reader.py`が、tenant別ディレクトリと運用者レベル（ルート）の両方から同じpayloadを読めることを検査します（[receipt](../../evaluations/records/SUI-TEI-admin-path-2026-11-02.json)）。

HTTPサーバ・認証・実配備は未検証です。
## 所属とcontainmentの整合（2026-11-03）

SUIの`DocumentV1`は、`Island.cardIds`の包含と`Affiliation`が同じ組を指すと拒否します。合成層へ同じ規則を追加しました。

- island.cardIdsに入っているCardのAffiliationは`AssemblyError`
- パイロットのfixtureを、containmentとAffiliationが重複しない形へ変更

## DocumentV1モデルでの検証（2026-11-03）

`assembler/validate_against_sui.py`で、artifactをSUIのconsumerに読ませ、`DocumentV1`モデルで検証しました。

```text
documentId: doc-1
cards: 2 / islands: 1 / affiliations: 1
DocumentV1 valid: true
```

`transform`と時刻は呼び出し側から供給しています（[receipt](../../evaluations/records/SUI-TEI-documentv1-validation-2026-11-03.json)）。
## 保存計画CLI（2026-11-03）

`assembler/plan_save_cli.py`で、artifactと既存DocumentV1から保存計画を作れます。

```sh
python integrations/pilot-sui-document/assembler/plan_save_cli.py \
  --sui-repo <SUI> --artifact evaluations/artifacts/documentv1-projection.json \
  --existing <existing-documentv1.json> --out <receipt.json>
```

- 既定は非破壊マージ（`preserve_existing=True`）
- 追加・変更・保持・警告をreceiptへ記録
- 書き込みは行わない

観測（1回）:

```text
action: update
cardsAdded: 1 / cardsChanged: 1
preservedCards: 1 / preservedIslands: 1
warnings: 0 / writes: false
```

- [receipt](../../evaluations/records/SUI-TEI-save-plan-cli-2026-11-03.json)
### 保存契約の検証（2026-11-03）

CLIは、保存計画のpayloadをSUIの保存経路と同じA1契約アダプタで検証します。

- payloadに`schemaVersion`は不要（付与しない）`n- 既存文書はマージ前に`validate_existing_document`で検証する
- 非破壊マージ後のpayloadが契約を通ることを確認
- 観測: `contractValid: true`、`contractCards: 3`

- [receipt](../../evaluations/records/SUI-TEI-save-contract-2026-11-03.json)
## 保存の実行（2026-11-03）

`assembler/save_to_sui.py`で、投影artifactをSUIのHTTP APIへ保存します。

- SUIアプリを一時SQLite DBで起動（`local-dev`、APIキーなし）
- `PUT /docs/{doc_id}`で作成し、`GET`で読み戻し
- 既存文書を検証したうえで非破壊マージし、`PUT`で更新
- 最終`GET`まで確認

観測:

```text
create: 200 / read: 200
update: 200 / final read: 200
cards: 2 / writes: true
database: temporary SQLite
```

- [receipt](../../evaluations/records/SUI-TEI-save-e2e-2026-11-03.json)
- 本番DB・認証・実配備は未検証
## 認証ありの保存（2026-11-03）

`--api-key`を渡すと、業務APIキーを設定した状態で保存します。

```text
APIキーなしの PUT: 401
正しい X-API-Key:  200（作成・読み戻し・更新・最終GET）
```

- [receipt](../../evaluations/records/SUI-TEI-save-auth-2026-11-03.json)
- 一時SQLite、`local-dev`のまま
- 本番認証・本番DB・実配備は未検証
## 保存後の往復整合（2026-11-03）

保存後の`GET`と投影を比較します。

```text
cardIds / cardText / cardPosition: 一致
islandIds / islandCardIds:         一致
edgeIds:                           一致
roundTrip: true
```

- [receipt](../../evaluations/records/SUI-TEI-save-roundtrip-2026-11-03.json)
## 実サーバでの保存（2026-11-03）

`assembler/serve_and_save.py`で、SUIをuvicorn上の実HTTPサーバとして起動して保存します。

- 127.0.0.1の実ソケット、一時SQLite、APIキーあり
- `PUT /docs/doc-1` 作成: 200
- `GET` 読み戻し: 200、roundTrip: true
- APIキーなしの`PUT`: 401

- [receipt](../../evaluations/records/SUI-TEI-server-2026-11-03.json)
- 本番DB・TLS・リバースプロキシ・実配備は未検証
## 決定性（2026-11-03）

`assembler/determinism_check.py`で、同じ入力の投影を2回実行し、artifactのdigestを比較します。

```text
runs: 2 / identical: true
digest: 6d39148c...bacf34（両回一致）
casesPassed: 21 / 21
```

- [receipt](../../evaluations/records/SUI-TEI-determinism-2026-11-03.json)
- 異なるホスト・ツールチェーン間の決定性は未検証
## 保存計画と保存の統合（2026-11-03）

`save_to_sui.py`は、既存文書がある場合に`plan_save(preserve_existing=True)`のpayloadをそのまま`PUT`へ渡します。

観測（2回目の保存）:

```text
planAction: update
planCardsAdded: 0 / planCardsChanged: 0
planPreservedCards: 0 / planWarnings: 0
roundTrip: true
```

同じ内容の再保存が差分ゼロで通ることを確認しました。

- [receipt](../../evaluations/records/SUI-TEI-save-plan-2026-11-03.json)
## 複数文書の保存（2026-11-03）

`assembler/multi_save.py`で、同じ投影を10の文書IDへ保存します。

```text
documents: 10
createdAll: true / readAll: true
isolatedIds: true
writes: true
```

- [receipt](../../evaluations/records/SUI-TEI-multi-doc-2026-11-03.json)
- 大量カード・同時書き込み・本番DBは未検証
## 大量カードの保存（合成、2026-11-03）

`assembler/large_save.py`は、パイロット投影へ合成Cardを追加して保存します。

```text
requestedCards: 300 / savedCards: 300
putStatus: 200 / readStatus: 200
payloadBytes: 22744
syntheticCardsAdded: 298
```

- [receipt](../../evaluations/records/SUI-TEI-large-doc-2026-11-03.json)
- **合成fixture**であり、パイロットの実証ではない
- 本番上限・同時書き込みは未検証
## ETag前提条件（2026-11-03）

`assembler/etag_check.py`で、保存経路の`If-Match`を確認します。

```text
ETagあり: true
古い If-Match: 409
一致する If-Match: 200
前提条件なし: 200（local-devのlast-write-wins）
```

- [receipt](../../evaluations/records/SUI-TEI-etag-2026-11-03.json)
- SaaSプロファイルの前提条件必須動作、同時書き込みは未検証
## Cardのsources（2026-11-03）

Cardのoptionalな`sources`配列を投影へ追加しました。

```text
sui.card.record v8: id, text, x, y, claimType?, holdState?, textReviewed?, sources[]?
```

- 契約・fixture・SUI consumer・DocumentV1 payloadまで反映
- 21ケースPASS、SUI unittest 21件PASS
- `validate_against_sui`でDocumentV1妥当性を確認

- [receipt](../../evaluations/records/SUI-TEI-sources-2026-11-03.json)
- [validation](../../evaluations/records/SUI-TEI-sources-validation-2026-11-03.json)
## DocumentのreadingOrder（2026-11-03）

Documentのoptionalな`readingOrder`配列を投影へ追加しました。

```text
sui.document.record v5: id, title?, readingOrder[]?
```

- 契約・fixture・SUI consumer・DocumentV1 payloadまで反映
- 21ケースPASS、SUI unittest 24件PASS
- `validate_against_sui`でDocumentV1妥当性を確認

- [receipt](../../evaluations/records/SUI-TEI-reading-order-2026-11-03.json)
- [validation](../../evaluations/records/SUI-TEI-reading-order-validation-2026-11-03.json)
## 追加フィールドの往復（2026-11-03）

`sources`と`readingOrder`を含むartifactで保存し、読み戻しを比較しました。

```text
cardSources: true / readingOrder: true
roundTrip: true（8項目すべて一致）
planAction: update / 差分なし
```

- [receipt](../../evaluations/records/SUI-TEI-fields-roundtrip-2026-11-03.json)
## 契約の版をartifactへ記録（2026-11-03）

artifactの`source.contracts`へ`contractId`と`contractVersion`を記録するようにしました。

```text
card-record: sui.card.record v8 / cases 5
document-record: sui.document.record v5 / cases 4
```

契約ファイルのハッシュは`sourceDigest`（生成候補ソースのdigest）とは別物なので、版の確認には`contractVersion`を使います。

- [receipt](../../evaluations/records/SUI-TEI-contract-versions-2026-11-03.json)
## 契約内容の照合（2026-11-03）

artifactの`contractDigest`（契約JSONのLF正規化ハッシュ）と、契約ファイルを比較できます。

```text
contracts: 5
mismatches: []
allMatch: true
```

- [artifact flow receipt](../../evaluations/records/SUI-TEI-contract-digest-2026-11-03.json)
- [digest check](../../evaluations/records/SUI-TEI-contract-digest-check-2026-11-03.json)
## 一括実行（2026-11-03）

`assembler/run_pilot.py`で、投影フロー・DocumentV1検証・契約digest照合を1コマンドで実行します。

```text
flow: 21ケースPASS
documentV1: valid
contractDigests: allMatch
result: PASS
```

- [receipt](../../evaluations/records/SUI-TEI-pipeline-run-2026-11-03.json)
- 保存は含まない
## 一括実行に保存を追加（2026-11-03）

`--save`を付けると、検証の後に保存と往復整合まで実行します（既定は無効）。

```text
flow: 21ケースPASS
documentV1: valid
contractDigests: allMatch
save: roundTrip true / planAction update / 200
result: PASS
```

- [receipt](../../evaluations/records/SUI-TEI-pipeline-save-2026-11-03.json)
- 一時SQLite・`local-dev`
## artifactのJSON Schema（2026-11-03）

`artifact.schema.json`を追加し、`assembler/validate_artifact_schema.py`でartifactを検証します。

```text
valid: true
errors: []
```

- 検証する: envelope・契約メタデータ・要素の形
- 検証しない: 参照整合性・DocumentV1
- [receipt](../../evaluations/records/SUI-TEI-artifact-schema-2026-11-03.json)