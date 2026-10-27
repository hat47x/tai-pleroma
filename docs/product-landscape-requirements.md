# Product Landscape 横断要求 v0（提案・未採用）

状態: **Draft / Proposed / acceptance NOT RUN**。この文書は製品群の位置づけをTAIへ集約するための**要求候補**である。TAI main `88a6fad6d088f98ccab6080b3b7be24b62399113` と [Draft PR #72](https://github.com/hat47x/tai-pleroma/pull/72) のレビュー対象であり、製品の仕様変更・正式な横断契約・製品リリース判断ではない。

## 1. 要求の対象と、対象外

**対象**: 読者が、公開可能なプロダクト群の *何が存在するか／何を担うか／どの関係が提案・確認されたか／出典と確認時点は何か／何が未確認か* をTAIから辿れること。重要な変更で、契約・責務・影響先を探索できる状態へ段階的に発展させる。

**対象外**: 各製品の全ての内部仕様の複製、SEIの意味記録・Decision/Authorityの第二正本、TEIのPlugin Resolver/Source Acceptance、SUIの人間による意味形成、SHO/MMIの編集・原資料正本、EKIの実委任・結果検証、中央Host・統一DB・単一Agent runtime。

**前提**: 公開リポジトリの発見はProduct認定ではない。五つの関連基盤＋TAIの初期図は全製品の網羅を示さない。SHOとMMI、TEIとStudio、CSWの位置づけは未決。

## 2. トレース可能な要求

各行の「必須」は**採用された場合の要求強度**であり、現段階で採用済みという意味ではない。Gateは[横断受入条件](product-landscape-acceptance.md)のG1（説明可能）/G2（機械検査可能）/G3（変更管理可能）。IDは**要求候補の索引**であり正式なプロダクト識別子ではない。

| ID | 要求案 | Gate | 受入と境界 |
| --- | --- | --- | --- |
| PL-REQ-01 | **入口**: TAI READMEから全体像・分類・根拠・未決へ辿れること | G1 | [俯瞰図](product-landscape.md)へのリンクが有効、シナリオ別の[責務境界](architecture-slice-001.md)と区別 |
| PL-REQ-02 | **母集団の明示**: 列挙の対象・観測時点・調査できない範囲を示すこと | G1 | [候補棚卸し](product-inventory-candidates.md)；未登録=不存在としない（P-12） |
| PL-REQ-03 | **分類の非昇格**: Repo/Project/Method/Skillを自動的にProductとしないこと | G1 | SHO≠MMIの自動同一視、CSW≠第六基盤の自動採用（P-17） |
| PL-REQ-04 | **製品の同一性**: 公開名、repo path、ローカルUI IDと論理同一性を区別すること | G2 | rename・同名異scope・衝突で不正確定しない（P-01/P-02/P-07） |
| PL-REQ-05 | **役割の分離**: Productの目的／Capability／提供候補／実接続／実行可能性を別々に表示できること | G1→G2 | `Provides`の文書記述を実動作のPASSと扱わない（P-06/P-16） |
| PL-REQ-06 | **辺の意味**: ビルド・実行・契約・補完・構成・役割参照を混ぜないこと | G2 | A→B→Cから直接A→CのContractを捏造しない（P-03/P-04/P-05） |
| PL-REQ-07 | **根拠の範囲**: Repository/Revision・資料・確認方法・条件・未確認を参照できること | G1→G2 | 古いPASSを新Revisionへ継承しない（P-09/P-14） |
| PL-REQ-08 | **状態の非昇格**: 仮説・設計・合成試験・実接続・意味受理・Authority・結果を独立に扱うこと | G1→G2 | `queued`は実行完了でない。AI提案は承認でない（P-15/P-19） |
| PL-REQ-09 | **矛盾と不明**: 相反する根拠と未解決状態を保持すること | G2 | 最新勝ち・未検出=否定としない（P-11/P-12） |
| PL-REQ-10 | **三つのViewpoint**: Landscape/Capability/Contractを別の問いと凡例で表せること | G1→G2 | [View Contract](product-landscape-view-contract.md)；実装依存の線を「役割参照」で代用しない |
| PL-REQ-11 | **Snapshot**: カタログと外部Sourceの版・時点・投影条件を分けること | G2→G3 | stale graph/epoch、旧判断の復活、同条件再生成を負例化（P-08/P-10/P-20） |
| PL-REQ-12 | **公開境界**: 公開できないEntity・Edge・属性・集計の情報を漏らさないこと | G2 | ノード非表示だけでなく間接漏洩を検査（P-13） |
| PL-REQ-13 | **責務の非複製**: 各ProductのAPI/Decision/Authority/原本をTAIの正本へコピーしないこと | G1→G3 | [知識モデル](product-knowledge-model.md)責務表・P-18 |
| PL-REQ-14 | **横断変更**: 関係のSource/Contract更新時に直接影響・間接影響・判断待ちを分けられること | G3 | 利用契約と影響可能性、候補とacceptedを区別 |
| PL-REQ-15 | **統合方式を固定しない**: 中央Host/共通Runtime/DB/Plugin名前空間を採用要件にしないこと | G1 | [TEI Draft #2226](https://github.com/hat47x/tei-platform/pull/2226)・[Draft #2298](https://github.com/hat47x/tei-platform/pull/2298)は他製品の提案で未merge |
| PL-REQ-16 | **変更の資格**: カタログを書ける権限と、製品所有者の合意・業務Authorityを同一視しないこと | G2→G3 | [TAI責務境界](architecture-slice-001.md)・[TEI #267](https://github.com/hat47x/tei-platform/issues/267) |

## 3. 正本・採否の責任分担（要求の前提）

| 対象 | TAIが採否を管理し得る内容 | 代替しないOwner |
| --- | --- | --- |
| Product分類と横断的位置づけ | 候補、公開可能性、役割・責務の横断合意 | 各製品の要求・実装・Release Owner |
| Contractの横断対応 | 誰が何の版を利用する**との合意があるか**の索引 | 提供Productが持つ契約本文／Consumerの実受入 |
| 観測・証拠・Decision | 公開可能な参照・対象Revision・採否記録の所在 | SEI等の意味正本、CIや実物観測、業務の権限者 |
| 画像・図・レポート | Viewpoint・凡例・情報収集範囲・Snapshot | 元データの発生源および個別製品の正本 |
| 操作・委任・公開 | 候補の説明・受入条件の表示 | TEI/SHO/EKI等の実実装とAuthority |

ここでいう「横断合意」はTAIの文書化/レビュー上の採否であって、他製品のAPI契約を法的・意味的・運用的に代行承認したことにならない。Owner判断・証拠がないときは`proposed`/`unresolved`とする。

## 4. 対応表：要求→設計→受入

- **G1（文書）**: PL-REQ-01/02/03/05/07/08/10/13/15。現在の[初期図](product-landscape.md)・[候補棚卸し](product-inventory-candidates.md)はDraftの材料であり、Ownerレビューはまだ**NOT RUN**。
- **G2（データ検査）**: PL-REQ-04/06/09/11/12/16。具体的な機械可読Schema/validator/view rendererを採用するか未決。P-01〜P-20のテストは**提案のみ**。
- **G3（横断変更）**: PL-REQ-11/13/14/16。実Productの互換性証拠・変更レビューに関する運用は**NOT RUN**。

## 5. 採用を求める判断と撤回条件

**Owner判断が必要**: 対象母集団、ProductとMethod/Skillの分類、TAI自体の単位、SHO/MMIとTEI Studioの扱い、公開メタデータの境界、IDとRelation語彙、G1の読者・評価方法、レビュー担当。

**撤回または縮小の条件**: 台帳を維持するコストが利用者の問いに見合わない／元製品の正本との矛盾を防げない／公開範囲が安全に定義できない／根拠と版を付けられない。まずはMarkdownと固定リンクに縮小し、過大なRegistryシステムの導入を避ける。

**非証明**: 本書の追加によってプロダクト間の接続、意味受理、権限、正式な分類、単一の正本DB、図生成エンジンの実装が成立したとは扱わない。
