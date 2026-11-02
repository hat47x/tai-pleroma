# プロダクト横断知識モデルと管理境界 v0

状態: **Draft / 提案**。横断情報をTAIへ集約するという方向性と、以下の具体的なスキーマ・運用・検査規則の採用判断を区別する。  
基準: TAI main `88a6fad6d088f98ccab6080b3b7be24b62399113`。図は[Product Landscape](product-landscape.md)。既存の[責務境界](architecture-slice-001.md)、[接続調査](../integrations/capability-inventory.md)、[開発ルール](../AGENTS.md)を優先する。

## 1. なぜ単なるリンク集で足りないか

横断情報の主たる問いは「何が存在するか」「なぜ独立しているか」「誰が何を提供するか」「何が何に依存するか」「変更時に誰の確認が必要か」である。その回答を、証拠に結び付けた型付き関係として再構成できるようにする。一枚の全体図には異なる意味の矢印を混ぜない。

ただし**TAIは意味・判断・証拠の汎用正本を作るプロダクトではない**。TAIの責務は、横断的な事実・提案・合意の索引と、責務分担に関する自らの判断を明示すること。個別実装、意味記録、権限、公開判定、Task実行は原則として各所有元に残す。

## 2. 概念と同一性

| 概念 | 定義 | 正本と境界 |
| --- | --- | --- |
| Product | 継続的な利用価値・責務とライフサイクルの単位 | 横断的なID/位置づけはTAI、固有設計は当該製品 |
| Project | 期間・目的を持つ探索または実装活動 | Productと同一視しない |
| Repository | Git等の管理場所 | 1 Product : N Repository、N Product : 1 Repositoryの双方を許す |
| System / Component | 構成・実装の単位 | 実装内部は各基盤で管理 |
| Capability | 何ができるかの意味的な能力 | 定義／提供候補／能力の実証を区別する |
| Contract | 利用側と提供側の合意された入出力・意味・版の境界 | 詳細な仕様は提供側。横断合意と利用対応はTAI |
| Artifact / DataAsset | 生成・利用・保持する成果物／データ | 原本と実体は所有元、TAIは参照のみ |
| RelationshipAssertion | 特定の主体が、特定条件で主張した関係 | TAIに索引、根拠元へリンク |
| EvidenceReference | 根拠への固定版参照と検証範囲 | 実物の真偽やAuthorityをTAIが自動認定しない |
| CrossProductDecision | 製品境界・相互利用・移行に関する横断判断 | TAIで扱う。ただしSEIのDecision/Authorityの意味モデルを代替しない |
| Viewpoint | どの問いにどの関係を投影するか | TAIが所有 |

**識別子の候補**: `tai:product:<scope>/<slug>`、`tai:capability:<scope>/<slug>`、`tai:contract:<scope>/<slug>`。型・スコープ・不変のIDを分け、名称やGitHub URLをIDにしない。廃止したIDは他対象に再利用しない。ただしこの文法は提案であり、**現在の製品の公式IDやTEI `tei.*` plugin名前空間を変更しない**。

## 3. 関係の分類と推論規則

| 種別 | 例 | 採用時に必要な条件 |
| --- | --- | --- |
| 提供 | `provides_capability` | Provider・意味・根拠・有効範囲 |
| 利用 | `consumes_contract` | Consumer、Contractの版・環境、利用根拠 |
| 構成 | `part_of` | 主体/対象の型。循環を拒否 |
| ビルド | `build_depends_on` | 依存版とビルドprofile |
| 実行 | `runtime_depends_on` | 実行環境と観測または設計根拠 |
| 機能的補完 | `complements` | 意味上の理由。実行依存を導出しない |
| 移行 | `supersedes` / `replaces` | 旧新の同一性、移行条件と有効期間 |
| 証拠参照 | `supported_by` | 対象Version/Revision、根拠範囲 |

少数の関係型から始め、`depends_on`という一つの矢印へビルド・実行・意味的利用を押し込めない。`A→B→C`の到達可能性は間接影響候補を示せるが、AがCのContractを**直接利用**していると推論しない。

## 4. Claim / Evidence / Decisionは混ぜない

関係の記録には少なくとも以下の独立した次元が必要:

- **主張**: 誰が何を、どの対象・スコープ・時点で述べたか。
- **根拠参照**: どのリポジトリ・文書・行・API・試験recordのどのRevisionか。失敗や未取得も記録する。
- **横断判断**: TAIの横断方針として proposed / accepted / rejected / superseded のどこか。
- **実現**: design-only / partial / implemented / unknown。
- **検証**: not-run / static-reviewed / tested / observed / unknown。特定の対象と条件の証拠に限定。

同じ主張に複数の根拠・反証があれば両方残す。新しい情報によって過去の意味受理が自動復活したと扱わない（[TAI #33](https://github.com/hat47x/tai-pleroma/issues/33)）。SHAやdigestの一致は証拠のbyte一致であって、意味受理・認可・結果の正しさではない（[TAI #28](https://github.com/hat47x/tai-pleroma/issues/28)）。

**SEIとの非重複**: `Observation != Interpretation != Recommendation != Decision != Authority != Execution != Outcome` はSEIの責務と整合させる。TAIは参照と横断判断の受入経緯を持てるが、SEIのsemantic contractやDecisionの履歴、受理権限を独自形式で置換しない。

## 5. 時間、対象版、未知

少なくとも次を分けて記録する。

- **validAt / validFrom / validUntil**: その関係が成立すると主張する対象時点。
- **recordedAt**: TAIで記録した時点。
- **sourceRevision / artifactDigest / environment / profile**: 検証の対象。
- **decisionRevision**: 採用・失効・再受理の経緯を指す参照（SEI等の契約に従う）。

旧Revisionの検証成功は新RevisionのReadyを保証しない。A→B→Aで同じ表示文言に戻っても、受理の復活を推論しない。未登録/未観測/不明/否定/禁止/不存在の確認は異なる。完全性を宣言できないカタログから「関係なし」は導かない。

Snapshotの候補は、TAI catalog commit、参照した各製品のSource Revision一覧、viewpoint/filter、参照証拠のdigestを束ねること。Gitコミットだけを固定して外部URLの現行内容を読む方式を「再現可能」と呼ばない。

## 6. リポジトリの責務分担

| TAIで維持する | 各基盤の所有元で維持する |
| --- | --- |
| 横断Productの識別・位置づけと図 | 製品内部の要件・設計・実装・テスト |
| 提供能力・利用関係・互換性課題の索引 | API/semantic契約の詳細な定義 |
| 製品間の合意・廃止・移行の判断 | 実行時Authority、Task、source acceptance |
| 根拠への固定版参照と検証範囲 | 原本、意味記録、証拠の実体・監査 |
| 横断変更の影響候補とレビュー先 | 各製品の採否・実装・展開 |

**共有正本の誤解を避ける**: 「プロダクト横断の情報はTAIに集約する」はコピー集中・中央Host必須を意味しない。新たな共通DB、エージェントランタイム、共通Contractを先に実装しない。[architecture-slice-001](architecture-slice-001.md)の「必要性が証明されるまでTAI固有の状態DB・統一Contractを設けない」という制約を維持する。TEI独自Host廃止方針は[Draft PR #2226](https://github.com/hat47x/tei-platform/pull/2226)で審査中であり、merge済みと書かない。

## 7. 段階的導入（段階間のゲート）

**G1: 人間に説明可能** — 登録対象の棚卸し範囲が定義され、各Productの目的・責務・リンクを説明できる。代表図に凡例、構想/事実の区別、情報収集の不足がある。

**G2: 機械で検査可能** — Product IDの一意性・参照解決・関係型と対象型・構造循環・Evidence Revision・図の再現性をテスト。最初はMarkdown/手作業でもよく、必要性が確認できた段階でYAML/JSON Schemaへ進む。

**G3: 変更管理に利用可能** — Contractの変更による直接Consumer・間接影響候補、未解決の互換性、関係製品のレビューを出せる。影響分析は許可・実行・意味の受理ではない。

負例: (1) 同名異スコープ、(2) 未登録IDとunknown、(3) `part_of`循環、(4) 間接経路から直接Contractを捏造、(5) static-onlyをruntime-testedに昇格、(6) sourceRevision更新後に旧PASS再利用、(7) 非公開Entityまたは関係から情報漏洩、(8) `queued`をWorker完了へ昇格、(9) AI提案を人間のDecision/Authorityへ昇格、(10) 旧判断の無条件復活。

図へ確定した関係を投影する前のscope/qualified identity、Source Revision、Decision/Evidenceのチェック、非公開情報とstale表示の負例は[横断情報の受入・更新プロトコル（Draft）](product-landscape-acceptance.md)へ集約する。公開プロダクトの棚卸し範囲とSHO/MMI・CSWの未決分類は[公開リポジトリ候補](product-inventory-candidates.md)を参照。

## 8. 今回は固定しないこと

- すべてのリポジトリをProductとするか、研究・ツール・ライブラリをどう分類するか（全製品棚卸しが先）。
- 正式なProduct ID文法、Relation語彙の最終集合、所有者・レビューフローの権限。
- YAML・RDF・グラフDB・専用UI・TEI連携などの実装方式。
- TAIが実製品のAPIやSemantic Authorityを代表して認可・承認を行うこと。
- 公開できる情報の範囲。非公開リソースの存在・内容を公開マニフェストへ自動複製しない。

まず[Product Landscape](product-landscape.md)の初期範囲を確認し、最少の型と関係で実際の読者が答えたい問いを満たすか検証する。提案・静的確認・実接続・人間による採否を混同しない。
