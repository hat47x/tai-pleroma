# 横断プロダクト情報の受入・更新プロトコル（提案 v0）

状態: **Draft / NOT RUN**。本書はTAIの製品群カタログと図が満たすべき条件の**提案**であり、現行実装やOwnerの合意を示さない。  
対象: [Product Landscape](product-landscape.md)、[公開棚卸し候補](product-inventory-candidates.md)、[知識モデル](product-knowledge-model.md)。  
関連: TAI [#28](https://github.com/hat47x/tai-pleroma/issues/28)、[#33](https://github.com/hat47x/tai-pleroma/issues/33)、[#67](https://github.com/hat47x/tai-pleroma/issues/67)、[PR #71](https://github.com/hat47x/tai-pleroma/pull/71)（Draft）；TEI [#1120](https://github.com/hat47x/tei-platform/issues/1120)（Closed・共通参照契約）、[#1124](https://github.com/hat47x/tei-platform/issues/1124)（Consumer/Presenter）、[#267](https://github.com/hat47x/tei-platform/issues/267)（Proposal Acceptance）、[PR #2226](https://github.com/hat47x/tei-platform/pull/2226)（Draft・未merge）。

## 1. 第一原則: 事実の評価と横断方針の採用を別工程にする

対象ごとに次を分ける。単一の`status=ready`へ畳み込まない。

| 軸 | 表示すべきこと | 明確に否定する推論 |
| --- | --- | --- |
| Identity | 種別・スコープ付きの安定参照／未解決参照 | 表示名・UI ID・repo URL=永続Product ID |
| Role | 何の役割やCapabilityを意図するか | 機能の類似=同一Product、共通API |
| Claim | 誰がどの関係を主張したか | 登録済み=合意済み |
| Evidence | どの版・環境・対象で何を確認したか | digest一致=意味/Authorityの保証 |
| Cross-product Decision | 何が横断方針として採用/撤回/保留か | AI提案=人の承認 |
| Realization | 仕様、合成試験、実接続、結果観測のどの段階か | `queued`=実行/結果 |
| Visibility | 何を誰へ公開できるか | ノードだけ隠せば関連エッジから漏れない |

横断Decisionの詳細な意味・来歴をSEI等の既存機構から奪わない。TAIで保持するのは、意思決定の所在、採否と影響対象を説明できる**横断索引と文書**である。

## 2. 関係を投影する前の解決規則（規範案）

```text
discovery/source reference
  -> type + scope + logical identity を確定できるか
  -> 対象の同一性/版/有効範囲を照合できるか
  -> relation predicate の主体・対象型が適合するか
  -> assertionの種別とDecision/Evidenceの状態を保持できるか
  -> viewerの公開範囲でnodeとedgeの両方を出せるか
  -> viewpointの条件に従って表示／保留／隔離
```

失敗時は、**確定辺の描画へ進まない**。出典、候補、未確定理由を保持し、必要なら別の「unresolved」一覧に表示する。scopeの欠落した同名候補、複数のSource locator候補、取得不能、古い版は一意の成功と見なさない。

同じ画面用node IDは表示層の局所識別子とし、Workspace/図の変更、snapshot/epoch切替で対応表を再検証する。node IDから直接、製品の永続ID、API locator、Authorizationを導出しない。これはTEI #1120/#1124の既存責務を**TAI側の表示で尊重するための条件**であって、TEIのResolverやSourceBridgeをTAIに実装する要請ではない。

関係の到達可能性は影響候補の分析には使えるが、`A→B→C`から直接`A→C`の契約や許可を生成してはならない。候補と確定辺を異なる線種・凡例・テキストで示す。

## 3. 時点・版・有効性の再評価

```text
catalogSnapshot = {
  taiCommit,
  externalSourceRevisions[],
  evidenceRefs[],
  viewpointId,
  filters: { effectiveTime, environment, audience }
}
```

上記は候補構造であって採用済みSchemaではない。相手の`main`やライブURLを読み直した結果を旧snapshotとして返さない。固定Commit/Artifact digestが変われば再照合が必要。**以前の合格を新しい対象へ無断に持ち越さない**。

[TAI #33](https://github.com/hat47x/tai-pleroma/issues/33)と[Draft PR #71](https://github.com/hat47x/tai-pleroma/pull/71)が扱うA→B→Aでの旧Decisionの自動復活禁止は、そのまま一般カタログの「同じ表示文字列に戻れば同じ合意として再利用できる」とはならないことを示す。#71が扱うExactBindingの合成試験を実資料の意味受理に拡張したと主張しない。

## 4. 更新フローの権限境界（提案）

1. **Discover**: 製品側文書・リポジトリ・Issueから関係候補を読み取る。非公開情報を公開側へ転記しない。
2. **Qualify**: 対象の型、論理ID、スコープ、Source Revision、調査範囲と未確認を記録する。
3. **Critique**: 同名衝突、競合する主張、推移の誤推論、型不一致、公開範囲を検討する。
4. **Review**: Product Owner/関係Productの担当が、製品分類と横断関係の採否を判断する。リポジトリへのpush権限は意味上の承認・実行Authorityを自動的に与えない。
5. **Publish view**: 閲覧者に公開可能なEntity/Relationshipのみを、選択したViewpointとSnapshotで表現する。
6. **Reconcile**: Source変更を検出したら旧根拠を履歴として維持し、現在の関係を再評価する。矛盾は修正まで未解決として表示する。

公開への変更提案はPRレビューで追跡可能にするが、GitHub PRのmerge単独で、外部製品への機能採用・契約互換性・人間の業務Authorityが成立したとは扱わない。

## 5. 受入試験マトリクス（**提案、未実行**）

| ID | 負例／操作 | 期待される不変条件 | Gate |
| --- | --- | --- | --- |
| P-01 | Product名やリポジトリ名変更 | 安定Product IDを無断再発行しない | G1 |
| P-02 | 同名別スコープ/別kind | 候補を区別し、一意にresolveできなければ保留 | G2 |
| P-03 | 存在しないContract参照 | 確定した利用辺を生成しない | G2 |
| P-04 | `part_of`循環 | 型付き構成関係の循環を拒否 | G2 |
| P-05 | A→B、B→C | A→Cの直接契約や権限を捏造しない | G2 |
| P-06 | 設計記述のみの関係 | `observed`、`tested`へ昇格しない | G1 |
| P-07 | 複数の候補Source locator | 対象を誤確定表示しない | G2 |
| P-08 | stale snapshot/表示epoch | 旧成功応答で現在の辺・Readyを上書きしない | G2 |
| P-09 | 旧revでPASS、新rev未検証 | 新revをReadyと判定しない | G2 |
| P-10 | A→B→Aで同一表示文に戻る | 旧Decisionは無条件復活しない | G2 |
| P-11 | 二つの矛盾する関係主張 | 最新勝ちにせず両方の根拠を保持 | G2 |
| P-12 | 現行Catalogに未登録 | 不存在・禁止を導出しない | G1 |
| P-13 | ノード非公開だが関係が公開対象 | edge、名称、統計値で存在を漏らさない | G2 |
| P-14 | MMIでbyte digest一致 | 文書の正しさやAuthorityを自動承認しない | G2 |
| P-15 | EKIのTask `queued` | Worker実行/結果確認済みに変換しない | G2 |
| P-16 | SEIのCapability Provider候補 | Providerの実測・互換性と区別する | G2 |
| P-17 | SHO≒MMI、CSW≒SUIと名称/能力が近い | 同一Product、契約、実行依存を推測で作らない | G1 |
| P-18 | 各Product側の仕様更新 | TAI内のコピーを第二正本にしない | G3 |
| P-19 | AIが推奨関係を生成 | human Acceptedや実行Authorityへ昇格しない | G2 |
| P-20 | Snapshot固定の図を再生成 | 同一の入力・projection policyで意味上同等のビューを再生 | G3 |

**実行と評価の区別**: 本PRはテストデータ・自動検証器・CIを追加しない。上表は将来の受入条件であって、既存テストのPASS報告ではない。実装・CI・人間レビューの各結果は、その都度SHAと条件を固定して報告する。

## 6. Owner判断前に凍結しないもの

全Product範囲、Product/Project/Method分類、SHOとMMIの所有・対応、CSWの位置づけ、`tai:...` ID文法、関係語彙の採用、Schema/DB/UI実装、横断Review権限、公開可能なメタデータ、SEIの意味契約への追加。まず人が理解できる図（G1）の有用性を確認し、G2/G3は必要性と所有境界を確かめて進める。
