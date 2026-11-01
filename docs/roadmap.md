# 初期PoCの作業順序

状態: **Proposed（Owner受理待ち）**。直近の計画案であり、導入済み機能やコミット済みの実行結果を示さない。

## Phase 0 — 利用者の課題と検証条件を定める

- 対象を[SCN-001](../scenarios/SCN-001-shared-space-guidance.md)に限定する。
- [評価条件](../evaluations/SCN-001-acceptance.md)を先に定め、既存の基盤の[現在地](../integrations/capability-inventory.md)と照合する。
- **出口**: 入力の矛盾、成果物、反例、判断権限が記述できていること。実用・実装済みとは評価しない。

## Phase 1 — 手動の一巡（次の最小実証）

- 合成walkthroughの参照実装を追加した。T0/T1/T2の参照関係とP/Nの機械検査可能部分を確認するが、**人間の手動一巡や受入合格ではない**。
- 架空の観測O-01〜O-05から、仮説、暫定文書案、更新候補までを作る。
- 元の観測、仮説、未決、文書版の対応をMarkdownと手動記録で再構成する。
- O-06を追加し、A→B→Aや取得失敗時に何が保持されるか試す。
- **出口**: P-01〜P-05およびN-01〜N-04/N-06の結果が対象版とともに記録されること。

## Phase 2 — 既存の実機能を一つ接続

- 読み取り専用の実接続を一つ選び、既存コマンド／MCPの入力・出力、版・権限を確認する。
- MMI MCPの`inspect`を呼ぶ参照接続を追加した。stdin/stdout、`initialize`、ワークスペース外の拒否、原本digest不変を確認するが、実運用の認可・版固定は未確認。
- 手動一巡に対して何が改善したか、反例はどう変わるかを測定する。
- **出口**: 実接続の再現手順と負例が残ること。各基盤の契約を無断で拡張しない。

## Phase 3 — 主体の規模と実行形態を比較

- 個人／組織／社会へ適用する際の、情報公開、承認主体、参加条件の違いを比較する。
- EKIの委任、TEIのモデル生成、SHOの文書編集を必要性が確認できた範囲で試す。
- **出口**: 一つの知的機能としての価値と、個々の基盤へ戻すべき仕事を区別できること。

## 判断を求める事項

1. 初回の対象例を「共同利用スペースの案内改善」としてよいか。
2. Phase 1の観測を人がレビューする担当と、案内文の意味を受理する担当は誰か。**役割を決めるまで公開・実行は扱わない。**
3. Phase 2ではどの既存機能を選び、現在の動作と版をどの環境で確かめるか。

実装言語、専用Host、独自AIハーネス、統一データベース、新規Contractの採否は保留する。

## 横断計画（2026-10-30：Draft・本ロードマップのPhase 0〜3を置換しない）

[TAIシリーズの能力増幅・縮退適性と横断実証計画](harness-capability-lifecycle-2026-10.md) を別レーンで提案する。これは [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) のHarness-first構成と、[#165](https://github.com/hat47x/tai-pleroma/issues/165) 企業/未知業務、[#166](https://github.com/hat47x/tai-pleroma/issues/166) 生活の買い物、[#167](https://github.com/hat47x/tai-pleroma/issues/167) Personal Agencyを同一評価方法で比較するための計画であり、SCN-001の既存受理Gateや公開条件を変更しない。

- **接続だけで合格にしない**：既存ハーネス単体と、SEI/TEI/SHO等の最小機能を追加した場合の成果・信頼性・確認負担・運用コストを測る。
- **最小実行例を先行**：同じ意味の本文が戻ってもSourceの版・scopeが変わるA→B→A'のSEI判断再開を、外部ハーネス間で行い、現実の権限へ昇格しないことを検査する。
- **縮退も成果**：最新版の外部ハーネス単体で等価にできるならTAI独自処理を薄くする/廃止する処遇を選べる。共通HostやAgent Runtimeの新設は必須ではない。
- **進捗の区別（2026-11-01更新）**：SW-01 S1では同一OpenCode/GLM LatestのAレーン計3回と既存CLIのB構造検査が**限定合成実測済み**。Aは3回とも旧受理の自動転用を回避したが、Bとの条件は同一でなく、「検証器の追加価値」「別ハーネスでの再現」は未実証。EKIでは別の合成fixtureによりRA-2 Result Acceptanceと一部資源制限が実測済み。ただしTEIのloopback Task SubmitとEKI AcceptedResultは**同一Taskの通し証拠ではない**。SCN-004/005、本番業務効果、実ユーザーQoL、実発注/予約の受入は **NOT RUN**。
- **次の最小比較**：[SW-01評価票](../evaluations/SW-01-harness-handoff-qualification.md)のA2（原Basis情報のみ）とB1（同一次情報＋独立検証器）、currentTargetの実原典同定を優先。実利用可能な別ハーネスが現れたときD1を追加し、導入負担・確認負担も同時に比較する。新しい中央正本/Host/Gateは追加しない。
- **時点と同一案件の追跡（2026-11-01検討追加）**：[横断計画§16](harness-capability-lifecycle-2026-10.md)で、選択時点固定と実行時点条件解決を別の業務意味として扱う。TEI↔EKIの同一Task Submit→Attempt→Claim→AcceptedResultと、実成果物・業務Effectを独立に照合する既存P1-JE-1へ参照をつなぐ。部署間/人とAIの委任/再開でも「受付」「停止」「成果物を受け取った」「業務が完了した」を区別。TAI専用実行器・再試行権限・第二証拠正本は増やさない。新規通し試験はNOT RUN。
- **注意負担と未確認の保持（2026-11-01追補）**：[横断計画§17](harness-capability-lifecycle-2026-10.md)と[SW-01 S3/S5](../evaluations/SW-01-harness-handoff-qualification.md)では、通常優先度の未確認を通知しない場合も、その用途・鮮度不足・原記録への参照を引継ぎ可能にする対照を提案。通知件数0を確認事項0としない。既存SEI #660/#677/#678の正本・評価を再利用し、TAIに新通知基盤を作らない。Q-N/Q-P/Q-Cと別Harness引継ぎは未実施。
- **開示と再現・現行適用（2026-11-01追補）**：[横断計画§18](harness-capability-lifecycle-2026-10.md)で、TAI #28のmerged #163によるSUI局所保存再検証、SUI #3330/#3331/#3337の非レビュー構造非開示・実露出監査・歴史的Proposal判断、EKI #382のHTTP→ResultClaim process testと#366の子孫資源監視を、各々の限定実証として取り込む。非開示集合を「0件」、保存したbytes一致を現行正本の真正性、別TaskのAcceptanceを同一業務完了と呼ばない。SUI DocumentのTEI意味モデルがvalidでもrecord/string生成は#2488/#2489の既存課題。追加のVIEW/HISTORY/RECEIPT/ENVは計画・未実行。既存SW-01 A2/B1を先行。
- **機密RawのOS/Host境界（2026-11-01追補）**：[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)、[横断計画§19](harness-capability-lifecycle-2026-10.md)、[SW-01 S3/S5追加試験](../evaluations/SW-01-harness-handoff-qualification.md)。SEI/SUI等のSourceは用途に応じ管理境界内へ保持し、別Product/外部Harnessへはサーバ側で許可した最小Projectionのみ。機密Profileでは別OS Identity/ACL/Process/IPC/Network/Secret等でRawの直接読取り・外向き送出を実拒否する。EKIの資源制限と機密隔離は別。最初のC0アクセス棚卸し→合成Rawのread-only正例・直接読取り/egress負例→Linux/Windows実Profile比較を検討。新中央Host/認可正本なし、実隔離試験NOT RUN。SW-01 A2/B1の入力条件は許可済みProjectionでそろえる。
