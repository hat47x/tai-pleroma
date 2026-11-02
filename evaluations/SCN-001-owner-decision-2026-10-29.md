# SCN-001 実物レビュー要求の変更（Owner判断）

日付: 2026-10-29  
判断: **合成文書を実物レビューの代替として用いる。**

## 理由

TAIの開発は、配下のプロダクト群を上位要素から活用するための駆動力として進めている。現段階では、厳密に独立した意味レビューを求める要求が誤りであり、合成文書による開発レビューを先に完了させる。

## 変更する扱い

- R-01〜R-05は、合成文書を根拠に**development review accepted**とする。
- `evidenceKind`は`synthetic`のまま記録する。
- 評価者は生成AIとする。業務フローが一巡し、生成AIによる品質確認が済むまで、人間レビューへ回さない。
- 実物レビューは、合成文書の後に別途行う工程へ移す。`reviewTrigger=post-synthetic-real-object`。
- 公開承認・Authority検証・人間による独立レビューは未完了のままとする。

## 評価者

- 現段階の評価者は生成AIであり、人間の独立レビューではない。
- 業務フローが回り切ることを確認する前に、人間へ確認を回さない。
- 生成AIによる品質確認が済んだ後に、人間レビューと実物レビューを行う。

## 公開gateとの関係

公開gateは、公開用の`real-object`証拠を引き続き要求する。R-01〜R-05が`synthetic`でacceptedの場合、gateは`developmentAccepted`へ記録し、公開はblockedのままにする。

- `publicationApproved=false`
- `authorityVerified=false`
- `humanReviewed=false`
- `publicationAllowed=false`

## 境界

この判断は、公開・外部作用・Authorityを承認するものではない。合成文書を実在の規程や権限の証拠として扱わない。
