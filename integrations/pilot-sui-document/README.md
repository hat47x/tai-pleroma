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
