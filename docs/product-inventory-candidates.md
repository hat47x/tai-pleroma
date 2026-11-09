# 公開リポジトリの棚卸しとプロダクト候補（v0）

状態: **Draft / 調査記録。製品としての分類・TAIの管理対象範囲・相互接続は未採用／未実証を含む。**  
調査日: 2026-10-27。調査対象: この時点で確認できた `hat47x` 所有の**公開**GitHubリポジトリ。  
照合方法: リポジトリ一覧、各公開README、固定main commit。**この一覧だけで「全製品」を網羅したとは主張しない**。

## 1. 公開側の調査結果

| 対象 | 確認したmain SHA | READMEに記された位置づけ | 現時点の分類案 | TAI上の関係 |
| --- | --- | --- | --- | --- |
| [TAI Pleroma](https://github.com/hat47x/tai-pleroma) | [`88a6fad6`](https://github.com/hat47x/tai-pleroma/tree/88a6fad6d088f98ccab6080b3b7be24b62399113) | 知的活動の一巡を横断的に支える | 統合プロジェクト／Product境界は要確認 | 五基盤の役割を[TAI README](../README.md)が説明 |
| [SUI Sensemaking](https://github.com/hat47x/sui-sensemaking) | [`b0f5bae1`](https://github.com/hat47x/sui-sensemaking/tree/b0f5bae138c9289b46eae2d5f3fd6630a1175a08) | 観測・仮説・意味形成の過程を扱う | 独立基盤の候補 | TAI五基盤の一つ |
| [TEI Platform](https://github.com/hat47x/tei-platform) | [`2a1e68d5`](https://github.com/hat47x/tei-platform/tree/2a1e68d5919799f41cb09b7167cfeedf25905ee7) | 分野知識と実装技術の分離、モデル化・検証・実現 | 独立基盤の候補 | TAI五基盤の一つ |
| [SEI Cognition](https://github.com/hat47x/sei-cognition) | [`4bbc9fdf`](https://github.com/hat47x/sei-cognition/tree/4bbc9fdf2a60338b9921f84b026dc12349014e77) | 意味、判断、来歴、Capabilityを扱う | 独立基盤の候補 | TAI五基盤の一つ。SEI READMEにはTEIがCapability Provider候補と記載 |
| [EKI Fabric](https://github.com/hat47x/eki-fabric) | [`9c687a39`](https://github.com/hat47x/eki-fabric/tree/9c687a399377a7691bb7503ee82d6baa296ca7a3) | 限定委任と結果確認 | 独立基盤の候補 | TAI五基盤の一つ |
| [Markdown Matrix Injector (MMI)](https://github.com/hat47x/markdown-matrix-injector) | [`c1724e77`](https://github.com/hat47x/markdown-matrix-injector/tree/c1724e7788c4b8addda7d79a396f9e44e0a6e879) | 文書から表データを参照・検査するVS Code拡張／CLI等 | 独立ツール／Product区分は要確認 | TAIではSHO関連の**現行接続対象**として参照 |
| [Cultural Substrate Weaving (CSW)](https://github.com/hat47x/cultural-substrate-weaving) | [`63f08539`](https://github.com/hat47x/cultural-substrate-weaving/tree/63f08539479e9c204973af567670c9a35eebb0a2) | 外部文化体系を探索触媒とし対象材料で検証する補助AIスキル／研究方法 | 独立した方法・Skill群の候補 | TAIの五基盤としての採用・実接続は**未確認** |
| [hat47x.github.io](https://github.com/hat47x/hat47x.github.io) | main commit取得はHTTP 409（空リポジトリ） | READMEによる製品目的は未確認 | リポジトリ存在のみ確認。製品と分類しない | 未調査 |

**SHOの扱い**: TAI READMEに「SHO（現行のMMIを含む）」という**構想上の役割**がある。一方、この棚卸しでSHO独立の公開リポジトリや、SHO=MMIの製品同一性を確認したわけではない。よって「SHO」という役割概念と「MMI」という具体的なソフトウェアの識別を維持し、統合・置換・実装同一性の断定を避ける。

**TEI Studioの扱い**: TEIの一つの製品面・プロジェクト候補であり、別のProductとして独立IDを与えるかは未決。TEIの[Issue #1124](https://github.com/hat47x/tei-platform/issues/1124)のConsumer/Source Acceptance担当責務をTAIへ移さない。

**CSWの扱い**: 「文化的探索手法の利用可能性」と「TAIの製品間の契約・統合が既にある」は別命題。現状は公開READMEの内容に基づく**位置づけ候補の発見**までとし、SUI・SEIなどとの意味上の類似性から直接の依存・契約・権限を推論しない。CSW研究の構造やMethod実現についてはCSW自身が正本。

## 2. 「全製品」とは何を指すか

公開リポジトリ一覧 = 全製品一覧ではない。外部組織・非公開の成果物・将来構想・公開リポジトリ内の複数製品の有無はこの調査では確認できない。非公開対象の**名前・URL・存在の対応**を自動的に公開側へ複製しない。

完全性を主張するには、少なくとも次が必要:

1. **対象母集団**: TAIが扱う製品群と「その他の関連方法・ツール・組織資産」の境界をOwnerが定義する。
2. **分類規則**: Product / Project / Repository / System / Component / Method / Skill / Artifactを区別する。公開リポジトリ数を製品数と見なさない。
3. **棚卸し時点**: リポジトリのrevision・読取日、確認できた情報源、調査不能な範囲を残す。
4. **公開範囲**: 公開可能な項目だけを公開Catalogへ登録する。未承認の非公開情報は件数や隠した辺からも露出させない。
5. **責任主体と採否**: 自動発見はcandidateであり、製品分類・関係・責務・公開可否はOwnerの判断で確定する。

## 3. 形式化の前に必要な最小フィールド（提案）

初期の手作業台帳でも、対象ごとに以下を持つ:

- `discoveryKey`（調査用であって公式なProduct IDではない）
- `kindCandidate`（Product/Method/Tool等の分類案）
- `purpose`、`responsibility`、`nonGoals`
- `sourceRef`（URL、commit、README/ADR等の該当箇所）
- `relationshipCandidates`（関係型・方向・根拠・スコープ）
- `decisionStatus`（proposed/accepted/rejected/unresolved）
- `realizationStatus`（設計記述、静的確認、合成テスト、実環境観測を区別）
- `visibility`、`ownerReview`、`reviewedAt`

論理的なProduct IDを確定するまでは、READMEに記された略称をグローバルIDや認可権限に使用しない。

## 4. 追加の負例と受入ゲート

| Case | 事象 | 正しい扱い |
| --- | --- | --- |
| INV-01 | 7つの公開リポジトリが内容を持つ | 7 Productと即断しない |
| INV-02 | SHOとMMIに近接した文書化がある | 正式な同一性・置換関係を作らない |
| INV-03 | CSWとSUIが探索を扱う | 直接API依存や共通実行基盤を捏造しない |
| INV-04 | SEI文書がTEIをProviderと説明 | ドキュメント上の役割と実接続・互換性試験を区別 |
| INV-05 | 非公開対象を知っている | 公開Catalogへ詳細・存在を無断転載しない |
| INV-06 | 調査元READMEが更新された | 固定SHAの調査結果と最新版の再確認を分ける |
| INV-07 | Product IDの候補が同名 | スコープと型を保持し、曖昧な参照を確定しない |
| INV-08 | 製品関係図に線がない | 「関係が存在しない」とは断定しない |

**次のOwner判断**: TAI本体のProduct分類、SHO/MMIの粒度、TEI Studioの独立性、CSWなどの研究方法・SkillをTAIの対象に含める範囲、非公開資産のメタデータ公開方針。確認前に正式な`catalog/products/*.yaml`や公開Product IDを発行しない。

関連: [Product Landscape](product-landscape.md) / [知識モデル案](product-knowledge-model.md) / [Capability Inventory](../integrations/capability-inventory.md)。
