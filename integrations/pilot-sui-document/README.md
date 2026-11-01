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

これは属性ごとに独立した契約を持つ段階であり、Card全体を1つのrecordとして投影する契約ではありません。record全体の投影は未達です。

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

これはツール工程の時間・試行回数・介入回数の記録であり、生産性や自律性の証明ではありません。比較対象（現行SUIの手作業）と評価集合はまだ定めていません。
