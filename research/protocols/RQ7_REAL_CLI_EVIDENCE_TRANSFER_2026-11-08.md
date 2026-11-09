# RQ7 実CLI証拠の移管資格：直接参照を全Graph完全性へ誤昇格させない

- **状態**: 研究計画／実TEIの公開可能な証拠への移行判定（2026-11-08）。**RQ7の実被験者・AI比較は NOT RUN、独立holdout・実Policyは未証明**
- **TAI研究Owner**: [RQ7比較研究](RQ7_BOUNDED_GRAPH_OBSERVABILITY_2026-11-06.md)／[公開Gold校正](../results/RQ7_PUBLIC_GOLD_BASELINE_CALIBRATION_2026-11-08.md)
- **TEI実証Owner**: [最新main基点の限定実CLI→Node Consumer Draft #3321](https://github.com/hat47x/tei-platform/pull/3321)、[旧複合図表・限定不在Draft #2881](https://github.com/hat47x/tei-platform/pull/2881)、[統合済み研究 #2966](https://github.com/hat47x/tei-platform/pull/2966)
- **実証固定版**: TEI #3321 head `4dfdaf75145059859593d5f320ce43025e9736b0`。TAIからこのPRのSource/Consumer/Ownerを変更しない

## 1. 実行済み証拠と、その上限（旧Draftの合成実験とは独立）

[TEI専用Actions #42385227799](https://github.com/hat47x/tei-platform/actions/runs/42385227799)は**completed / success**。実Job logでNode `14 tests / 14 pass / 0 fail`、Go `1.26.10`による実`tei trace` 2回、Node `verify-cli-trace.mjs`の終了メッセージを直接確認した。

> `actual-cli-direct-reference-observation=PASS; caller-scope-only=OBSERVED; source-closure=NOT-PROVEN; relation-identity=NOT-PROVEN`

実装Sourceの固定Blobは [`direct-trace.mjs`](https://github.com/hat47x/tei-platform/blob/4dfdaf75145059859593d5f320ce43025e9736b0/reference/tei-topology-coverage/direct-trace.mjs) `713bb96fb94b52fc53487b4c49e70e0508ffb69c`、[検証Script](https://github.com/hat47x/tei-platform/blob/4dfdaf75145059859593d5f320ce43025e9736b0/reference/tei-topology-coverage/verify-cli-trace.mjs) `ade7e1eeb8e379a8d218fcc1d396c4b94a6728fb`。このBlobはテスト対象の同一性の参照であり、リリース署名や各製品の受理ではない。

- 実`reference/workspace`で`semantic-relation:sales.order.customer`を指定して2つの**Caller提供Scope**（`reference-observation`/`alternate-observation`）でread-only `tei trace`を実行した。
- 同一応答の`trace.subject`と`source.key`（Scope＋Kind＋ID）・Source Index referencesの`subject.kind/id`・Load時のWorkspace Manifest等の構造が照合された。
- Nodeの独立した言語・実装によるConsumer検査は**独立したSource ReaderによるSource閉包証明ではない**。Source Index Referenceには独立のScopeがない。
- Source/World Fingerprintが同一でも、Caller-Scopeに束縛された`snapshotFingerprint`が変わる。これをSource内容変更やSource-declared Scopeの証明に転用しない。
- 別Scopeの結果から同じ表示名のRelation Entityや全roleを合成せず、`relationEntityIdentity:not-provided`、`multiRoleClosure:unproven`、`sourceAndPluginClosure:unproven`、`absentClaim:unknown`を保つ。
- raw CLIはSource path/Evidenceを含み得る。**現在のPolicyが許したSliceを通さずにTAIの実験・Prompt・外部AIへ転載しない**。

## 2. RQ7の問いに対する資格の対応表

| 研究の問い／Claim | #3321固定Headで得た根拠 | 答えられる範囲 | 誤った昇格／次に必要な独立保証 |
| --- | --- | --- | --- |
| C-01: 指定したSubjectの**直接Edge候補**は実CLIに存在したか | 実Workspace `tei trace`→Node、固定Selector、2方向の期待Edge | **対象実行の直接参照候補は観測** | 別Scope/Sourceへの一般化禁止。Actual Packet/時点と同一Consumerの受理は別 |
| C-02: Source Navigationは選択Subjectを指すか | `source.key`、Reference `subject.kind/id`の同一Packet整合・改変負例 | **Packet内部のIdentity照合** | 独立Source再読取、現在のSource RevisionやAcceptanceは未成立 |
| C-03: Source自身がこのScopeを宣言していたか | `derivedbridge.FromIndex(d,scope)`のCaller指定Scope | **unknown**。`caller-supplied-projection-scope`でありSource宣言ではない | Source上の宣言Scopeと独立Reader／Qualified Identityが必要 |
| C-04: Relation ID・多項Role・Cardinalityが全て揃うか | `Edge.Relation`は種別、Direct traceの一ページ | **unknown**。独立Relation Entity/全RoleのClosureはなし | #1120/#2620とReaderの対象全集合・実Roleを検証 |
| C-05: 図にない外部Step/Source/Relationは存在しないか | `full` direct page、Load Manifest、CLI fingerprint | **unknown**。Direct pageが全Source/Plugin/Runtime/Relationの閉包とは限らない | 独立Enumerator、必要Root closure、Window、Observation面・権限が必要 |
| C-06: Workspace Manifest digestは実使用した全Sourceを保証するか | `workspace.manifest.path/sha256`のLoad時情報 | **load-time manifest provenance only** | 実Source bytesの独立Read、実Generator/Consumerとの同一Attemptを別に確認 |
| C-07: 現在の利用者はInspect/編集/公開できるか | `trace.authority=candidate-read-only` | **not authorized by this evidence** | Current Policy/Grant/DisclosureとStudio実ConsumerのOwner受入 |
| C-08: 意味・実Effect・業務完了は受理されたか | CLI direct traceと固定CIのみ | **NOT PROVEN** | #267／実Provider／独立Effect Observer／業務Ownerが別Gate |

**注意**: `unknown`と`not authorized by this evidence`は、全世界で不可能・非実在という意味ではない。現在ある証拠の範囲で**その主張に資格がない**ことを示す。外部機密が非開示である事実自体を公開Viewへ漏らしてはいけない。

## 3. 研究として追加する5つの反証課題（実験刺激は未生成・NOT RUN）

| Case | 誤って受理しがちな回答 | 正しく確認すべきこと |
| --- | --- | --- |
| R-TRACE-01 | `SourceNavigation.key`一致 → 全Sourceと同一受理済み意味 | 同一PacketのSourceIndex `kind/id`は確認済みだが、Sourceを独立再読取していない |
| R-TRACE-02 | 同一EdgeのScopeが別のCLIで変化 → Sourceが改版された | CallerがScopeを変えただけ。`worldFingerprint`は同じ、selector-bound `snapshotFingerprint`は異なる |
| R-TRACE-03 | `full` pageで検索0件 → Relation全体不存在 | Fullは直接Traceのページ条件。Relation/Plugin/Reader closureはない |
| R-TRACE-04 | Manifestが同じ → Builder/Consumerの実消費Sourceも同じ | ManifestはLoad provenance、Builder consumed inputsや別Attemptの同一性とは異なる |
| R-TRACE-05 | 独立NodeがPASS → 独立Source Oracle/現在の権限まで保証された | 別言語ConsumerによるPacket検査と、独立Source Enumerator／Current Policy／Ownerの受理を区別 |

**現時点でR-TRACE-01〜05は研究プロトコル上の新しい候補**。公開v0/v1 Goldや39件のRQ7限定Pythonテストに含めない。#3321の固定本番同等受入結果とも数えない。独立Goldの出典と現在の開示可能性を固定するまでHuman/AIの試験へは出さない。

## 4. 比較研究の重大な交絡：どのGraphを「宣言」と呼ぶか

`tei trace`は実Workspaceから組み立てられた**直接参照の観測Projection**であり、TEIにおけるBuildIntent、ETLのLogical Plan、Ownerが受理した業務Relation全体の宣言正本ではない。`tei trace`をそのままRQ7のV0/V1`Declared Graph`として扱うと、Graphの起源である実観測情報が対照群へ流入し、**「図表形式×追加Evidence」の2×2実験で因子が混ざる**。

よって、追加の比較を二段階に分ける。

1. **E-trace（先行可能な限定タスク）**：固定#3321のread-only直接参照とPacket一致／Caller Scope／不確実性を**実観測の説明**として扱う。比較は「同じ実観測をテキスト／図へ表示した際の過信・確認工数」。`Declared-vs-Observed`の因果効果は測定しない。
2. **E-pipeline（後続の独立タスク）**：Build/ETLの**独立に固定した宣言Graph/意味**と、同一Attemptに結び付く`Resolved/Observed/Consumed`を別Sourceから取得する。初めてRQ7 V0〜V3の「追加実行証拠」因子を比較できる。必要なSource closureやOwner意味が欠ける場合は`BLOCKED`であり、空白を合成Goldで埋めない。

本区分により、**TEI #3321の実CLI成果を無駄にせず研究に利用しつつ、#2831セルフビルドと#2542 ETL/MFTの独立実証Gateを先取りしない**。

## 5. G-Cal2実施順序とOwner／開示

| 順 | 取得するもの | 受入の上限・停止条件 |
| --- | --- | --- |
| G2-a | #3321のexact-head CIとBlob／Ownerが認めたread-only Packet資格 | 実CLI direct edge候補と同一Packet一致のみ。Source閉包・業務受理へ昇格しない |
| G2-b | #2516のCurrent Disclosure/Grantにより、**研究者が実際に見てよい**Source/CLI内容または許可済みPublic Slice | 未公開Source path、Raw JSON、内部存在件数、診断をTAI側へコピーしない。未許可なら**metadata-onlyの実証記録**に留める |
| G2-c | E-traceのGraph/Textを、実レンダラー/版/alt表示込みで独立レビュー | **図とテキストの意味情報同一性**を確認。Mermaidソースが存在するだけで視覚的同等としない |
| G2-d | #2831/#2542の独立にピン留めした宣言・実消費・結果Readerの証拠 | ここが揃うまでE-pipelineの2×2はNOT RUN |
| G2-e | 独立holdout・被験者割付・時間/Token/False claim/保留を事前固定 | 機材校正と人/AI研究の効果を混ぜない |

実効Policy／Source真正性／受理済み意味の採否はTEI側Ownerの仕事であり、本計画から新しいSource Reader/別Runner/Graph Resolver/共通Host/Policyエンジンを作らない。最優先の[Studio #1124](https://github.com/hat47x/tei-platform/issues/1124) M0実CLI→同一Workbench Consumer／[TEI #2831](https://github.com/hat47x/tei-platform/issues/2831)のBuild P0をブロックしない。

## 6. 先行規格からの帰結（独自性の非主張）

[SLSA Build Provenance](https://slsa.dev/spec/v1.2/build-provenance)ではBuild definition、resolved dependencies、run details、builderの信頼境界を区別し、依存列挙の完全性にも保証水準を要求する。したがって「実行に関する来歴を固定する」という考え自体はRQ7の新規発明でない。RQ7が検討するのは、**資格の異なる証拠を同じ図に載せたとき、人間・AIが不適切なClaim昇格を回避できるか**の実験上の評価である。学術的新規性・認知効果は未確定。

**今回の結論資格**：#3321実CLI観測結果の**外部で確認できる限定CIとSource上の停止線**を研究計画へ接続した。TAIからTEIのRaw CLI実出力を取得・再実行していない。RQ7 E-trace実表示、E-pipeline、実AI/Human評価、Independent Source Reader、Policy/Permission、全Source/Relation Closure、Owner Meaning/Effectは**NOT RUN / NOT PROVEN**。
