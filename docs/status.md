# TAI Pleromaの現在状態

更新日: 2026-11-02。状態: **参照実装と仮承認の記録**。製品受入・公開承認ではない。

## 要約

SCN-001の合成walkthrough、MMI読み取り専用MCP、SEI decision-memory、SUIのcard/island/edge、TEIの型検証、EKIのTask admission/cancel、統合参照実行、D-04レビュー成果物、Owner判断packetまでを参照実装として接続した。

TEI構築移行のパイロットとして、SUI DocumentV1の文字列投影（card本文とdocument_id）を、TEIの契約→生成→適合選抜→one-shot Target Profile実行まで通した。示せたのは参照ローカルの最小経路であり、record全体、実環境、人の受理、生産性の向上は未検証である。

Owner指示（2026-10-26）とOwner判断（2026-10-29）により、`development-review-only`の仮承認でCP-3まで進めている。R-01〜R-05は合成文書でdevelopment review accepted。**公開・外部作用は未承認**であり、公開用の実物レビューを合成後の工程として残す。

## 実接続の証拠（2026-11-01）

次のreceiptは`synthetic=false`かつ`evidenceKind=real-execution`で、受入済みの合成receiptとは別に保持している。いずれも`publicationAllowed=false`である。

| 基盤 | 実実行の内容 | receipt |
| --- | --- | --- |
| EKI | Linuxの`conformance/process`、bwrap sandbox 5件、executor承認のdigest形式検証 | [process](../evaluations/records/EKI-linux-process-2026-11-01.json)、[bwrap](../evaluations/records/EKI-bwrap-linux-2026-11-01.json) |
| EKI | HTTP submit 202 → dispatch → Agent実行 → ResultClaim → Result Acceptance（TEST PROFILE、同一ホスト再実行の検証）。run receiptへdigestで参照 | [http-agent](../evaluations/records/EKI-http-agent-2026-11-01.json)、[run](../evaluations/records/SCN-001-run-2026-11-01.json) |
| TEI | EKI Control APIへの`POST /v1/tasks`（202）、replay、problem+json、409 conflict | [live](../evaluations/records/TEI-EKI-live-2026-11-01.json) |
| SUI | ローカル起動の`/healthz`・OpenAPI・合成documentのPUT/GET。テナント境界・認可adapterのtest 40件 | [live](../evaluations/records/SUI-live-2026-11-01.json)、[auth](../evaluations/records/SUI-auth-2026-11-01.json) |
| SEI | SEIチェックアウトに対する`TestSCN001DecisionMemoryProjection`と`TestValidityThroughSEIVerify` | [live](../evaluations/records/SEI-live-2026-11-01.json) |
| MMI | 依存導入したCLIでfixture xlsxを`inspect --json` | [live](../evaluations/records/MMI-live-2026-11-01.json) |
| TEI構築パイロット | SUI DocumentV1投影をTEIの意味モデルで`validate ok`。文字列・record契約から候補を生成し、4ケースで選抜。one-shot Target Profileで実行。text/document_idの属性契約とCard record（text+documentId）、Island/Edge/Document recordを選抜。生成・選抜の工程とT1比較を測定し、rolling配備とrollbackを実行 | [model](../integrations/pilot-sui-document/README.md)、[pilot receipt](../evaluations/records/SUI-TEI-pilot-2026-11-01.json)、[spike](../evaluations/records/SUI-TEI-generation-spike-2026-11-01.json)、[selection](../evaluations/records/SUI-TEI-selection-2026-11-01.json)、[generation](../evaluations/records/SUI-TEI-text-generation-2026-11-01.json)、[target](../evaluations/records/SUI-TEI-target-2026-11-01.json)、[workflow](../evaluations/records/SUI-TEI-workflow-2026-11-02.json)、[multi](../evaluations/records/SUI-TEI-multi-attribute-2026-11-02.json)、[record](../evaluations/records/SUI-TEI-card-record-2026-11-02.json)、[compare](../evaluations/records/SUI-TEI-compare-2026-11-02.json)、[deploy](../evaluations/records/SUI-TEI-deploy-2026-11-02.json)、[island-edge](../evaluations/records/SUI-TEI-island-edge-2026-11-02.json)、[document](../evaluations/records/SUI-TEI-document-record-2026-11-02.json)、[assembler](../evaluations/records/SUI-TEI-assembler-2026-11-02.json)、[flow](../evaluations/records/SUI-TEI-integration-flow-2026-11-02.json)、[alignment](../evaluations/records/SUI-TEI-alignment-2026-11-02.json)、[affiliation](../evaluations/records/SUI-TEI-affiliation-2026-11-02.json)、[cardIds](../evaluations/records/SUI-TEI-island-cardids-2026-11-02.json)、[artifact](../evaluations/records/SUI-TEI-artifact-2026-11-02.json)、[sui-reader](../evaluations/records/SUI-TEI-sui-reader-2026-11-02.json) |

これらが示すのは、各基盤の**その版・そのfixture・そのホスト**での観測である。実データ、実権限、独立した検証主体、公開承認を示すものではない。

未接続として残るもの:

- EKIの`HTTP submit → dispatch → Agent execute → ResultClaim → Result Acceptance`はTEST PROFILEで到達した。検証は同一ホストの再実行による再現性確認であり、Worker Protocolや独立検証は未実施である。
- SUIは合成documentであり、SCN-001の実資料は未検証である。テナント境界と認可adapterはtest 40件がPASSしたが、実運用の認可判断・実資格情報・複数テナントでの確認ではない。マルチテナント化はTEIによるSUIの再構築を進めた後に扱う（Owner指示 2026-11-01）。
- MMIの候補は`inferred`であり、意味の受理ではない。

## 実装と証拠

| 対象 | 状態 | 証拠 | 限界 |
| --- | --- | --- | --- |
| SCN-001合成walkthrough | 実装済み | [reference-scn001](../tools/reference-scn001/README.md) | 合成fixture。P-06/N-05はnot-run |
| MMI読み取り専用MCP | ローカル参照接続済み | [reference-mmi-readonly](../tools/reference-mmi-readonly/README.md) | ローカル開発チェックアウト限定。実運用の認可・版固定は未確認 |
| MMI CLIの実実行 | 依存を導入したMMI CLIでfixture xlsxをinspectし、9候補・source digest・fingerprintを取得 | [live](../evaluations/records/MMI-live-2026-11-01.json) | fixtureのみ。候補はinferredで、意味の受理・本番文書は未検証 |
| SEI decision-memory | 一時storeで3 recordsを参照済み（synthetic）。別に、合成bundleで原記録の根拠参照と、旧Decisionの現行対象への構造上の束縛を検査（実装済み）。SEIチェックアウトに対する`TestSCN001DecisionMemoryProjection`と`TestValidityThroughSEIVerify`もPASS | [reference-sei-decision](../tools/reference-sei-decision/README.md)、[record](../evaluations/records/SEI-decision-2026-10-26.json)、[live](../evaluations/records/SEI-live-2026-11-01.json) | 合成fixture。実store・権限・署名・意味受理は未確認。SEI CLIで作る実storeのDecisionはExactBindingのbasisを持たず、束縛検査の対象外 |
| 統合参照実行 | 実装済み（SUI linkを含む） | [reference-scn001-run](../tools/reference-scn001-run/README.md)、[record](../evaluations/records/SCN-001-run-2026-10-26.json) | `runDigest`は内部整合のみ。署名・Authorityは未検証 |
| D-04レビュー成果物 | 生成済み | [artifact](../evaluations/artifacts/SCN-001-D-04-provisional.md) | 公開用ではない。実在の規程ではない |
| Owner判断packet | 生成可能 | `-owner-packet` | 承認ではない。実物レビュー待ち |
| 合成後レビュー | 合成でR-01〜R-05をdevelopment accepted。実物は未実施 | [判断](../evaluations/SCN-001-owner-decision-2026-10-29.md)、[計画](../evaluations/SCN-001-real-object-review.md) | R-06/R-07はPending。公開用real-objectは未取得 |
| 生成AI development review | D-04を観点に照らして`quality=sufficient-for-development` | [rubric](../evaluations/SCN-001-ai-development-review-rubric.md)、[receipt](../evaluations/records/SCN-001-ai-review-2026-10-29.json) | 人間レビュー・公開承認ではない |
| 合成フロー接続 | 文書→MMI→SEI→TEI→SUI→D-04→AI review→EKI Worker test環境→EKI feasibility review→gateが接続済み | [receipt](../evaluations/records/SCN-001-synthetic-flow-2026-10-29.json) | EKIはTask実行ではない。実在の規程・権限でもない |
| Owner review packet | 開発レビューの受理、証拠、公開blocker、次の確認を一覧化 | [packet](SCN-001-owner-review-packet.md) | 承認ではない。人間レビューは未実施 |
| 合成バリエーション | 本館/別館、全館/旧掲示の2変種でMMI/TEI/SEI/EKI/SUIがPASS | [matrix](../evaluations/records/SCN-001-variant-matrix-2026-10-29.json) | EKIはTask admission/cancel、SUIはPUT/GETのみ。実在の規程ではない |
| 合成不正入力 | TEI/MMI/EKI/SUIが不正入力を拒否 | [matrix](../evaluations/records/SCN-001-negative-matrix-2026-10-29.json) | 拒否経路の確認のみ。公開gateはblocked |
| SUI未知edge type | `bogus`をPUT/GETで保持（既知契約） | [contract](../evaluations/records/SCN-001-sui-contract-2026-10-29.json) | 意味の検証ではない |
| SEI重複decision | 同じ`dec-01`の2回目を拒否 | [receipt](../evaluations/records/SCN-001-invalid-sei-2026-10-29.json) | 重複IDの拒否のみ。意味の受理ではない |
| MMI 5行超 | 7行選択は`selectedRows=5`で未検証 | [制約](../evaluations/SCN-001-mmi-preview-limit.md) | preview上限の可能性。実在の規程ではない |
| 合成プロセスマトリクス | 5製品の正常系・拒否系・契約系を集約 | [matrix](../evaluations/records/SCN-001-process-matrix-2026-10-29.json) | 合成入力の集約。実Task実行ではない |
| SCN-002 複数拠点メンテナンス | 3拠点・期限・故障・予算の合成シナリオをMMI/TEI/SEI/EKI/SUIで実行 | [slice](../evaluations/records/SCN-002-slice-2026-10-29.json) | EKIはadmission/cancelのみ。優先度・安全判断・発注は未検証 |
| SCN-002 D-05優先度案 | 合成概算2000万円、予算上限3000万円。見積・承認は未確定 | [artifact](../evaluations/artifacts/SCN-002-D-05-priority-plan.md)、[AI review](../evaluations/records/SCN-002-ai-review-2026-10-29.json) | 発注なし。公開承認なし。実在の資産・契約ではない |
| SCN-002 D-06承認パケット | 合成見積2100万円。予算責任者・調達・安全の承認待ち | [artifact](../evaluations/artifacts/SCN-002-D-06-approval-packet.md)、[AI review](../evaluations/records/SCN-002-D-06-ai-review-2026-10-29.json) | 承認1件も完了せず。発注なし |
| SCN-002 承認シミュレーション | 3名の承認待ちdecisionをSEIへ記録 | [receipt](../evaluations/records/SCN-002-approvals-2026-10-29.json) | 4 records / 3 decisions。承認は未完了 |
| SCN-002 差戻しシミュレーション | 安全・調達の差戻し理由をSEIへ記録 | [receipt](../evaluations/records/SCN-002-rejections-2026-10-29.json) | 3 records / 2 rejections。承認なし |
| SCN-002 D-07再提出 | 差戻し2件へ対応。合成見積2160万円。再承認待ち | [artifact](../evaluations/artifacts/SCN-002-D-07-resubmission.md)、[AI review](../evaluations/records/SCN-002-D-07-ai-review-2026-10-29.json) | 発注なし。再承認は未完了 |
| 横断シナリオ | SCN-001/SCN-002/SCN-003を1つの実務能力マトリクスへ統合 | [matrix](../evaluations/records/SCN-cross-scenario-2026-10-29.json) | 合成入力。公開gateはblocked |
| SCN-003 補助金一次審査 | 3申請・収入要件差・上限・利益相反・採択枠をMMI/TEI/SEI/EKI/SUIで実行 | [slice](../evaluations/records/SCN-003-slice-2026-10-29.json) | 合成データ。採択判断は未検証 |
| SCN-003 D-08一次審査 | A保留、B不適格、C通常審査外。採択なし | [artifact](../evaluations/artifacts/SCN-003-D-08-first-review.md)、[AI review](../evaluations/records/SCN-003-D-08-ai-review-2026-10-29.json) | 採択・通知・公開なし |
| SCN-002/003採用 | Owner判断でdevelopment review対象に採用。D-07/D-08の未決は保持 | [判断](../evaluations/SCN-002-003-owner-decision-2026-10-30.md)、[status](../evaluations/SCN-002-003-review-status.json) | 実物レビューは先送り。公開gateはblocked |
| 公開gate | blocked | [gate](../tools/reference-publication-gate/README.md) | syntheticはdevelopmentAccepted。公開にはreal-objectが必要 |
| TEIモデル検証 | 型宣言をvalidate済み（synthetic） | [reference-tei-model](../tools/reference-tei-model/README.md)、[record](../evaluations/records/TEI-model-2026-10-29.json) | 実データ・意味・Authorityは未検証 |
| SUI API到達性 | 合成fixtureでは`/healthz`・`/openapi.json`・`/docs`・5 card/3 island/1 `contradicts` edgeのDocumentV1 GETを確認。ローカルSUIバックエンドの実起動では`/healthz` 200、65 path、合成1 cardのPUT 200とGET・digestを確認 | [probe](../tools/reference-sui-api/README.md)、[record](../evaluations/records/SUI-api-2026-10-26.json)、[live](../evaluations/records/SUI-live-2026-11-01.json) | 実在のSCN-001資料・テナント・認可は未検証。live側は合成document |
| SUI→SCN-001対応 | card digestとisland構成を照合済み | [link](../tools/reference-sui-link/README.md) | 意味形成の正しさ・実資料は未検証 |
| SUI→D-04対応 | D-04の観測行と公開境界を照合済み | [link](../tools/reference-sui-draft/README.md) | 意味の受理・公開承認は未検証 |
| 合成施設文書の工程検査 | 4種類の工程欠陥を検出済み（synthetic） | [receipt](../evaluations/records/SCN-001-synthetic-facility-2026-10-28.json) | 実物レビューの証拠ではない |
| 合成workspaceのMMI参照 | O-02/O-03/O-06/O-07/O-08の5行を読み取り専用で確認（synthetic） | [receipt](../evaluations/records/SCN-001-synthetic-mmi-2026-10-29.json) | 実資料・実認可ではない |
| 合成receiptの横断検査 | SUI/TEI/SEI/MMI/施設/EKI-envの`synthetic`ラベルと、実実行receiptの`real-execution`ラベルをCIで確認 | [checker](../tools/check-synthetic-receipts/README.md) | 合成receiptは実物証拠ではない |
| EKI process試験のLinux実行 | WSL2 Ubuntuで`conformance/process`全件がPASS。Agent実行・ResultClaim・メモリ上限停止を確認 | [receipt](../evaluations/records/EKI-linux-process-2026-11-01.json) | テストプロファイル。本番配備・Worker Protocol準拠・公開承認ではない |
| EKI bwrap sandboxのLinux実行 | WSL2 Ubuntuで通常実行・読み取り専用root・network interfaceなし・CPU上限停止・作業ディレクトリ書込みの5件がPASS | [receipt](../evaluations/records/EKI-bwrap-linux-2026-11-01.json) | `linux-bwrap` profileのみ。他のmount経由の絶対パスまで保証しない |
| EKI CLI起動 | `eki-control`/`eki-agent`のversionを確認済み | [probe](../tools/reference-eki-cli/README.md)、[record](../evaluations/records/EKI-cli-2026-10-26.json) | 実Task・委任・Authorityは未検証 |
| EKI Control API認証 | `GET /v1/tasks`の405で認証通過を確認済み | [probe](../tools/reference-eki-api/README.md)、[record](../evaluations/records/EKI-api-2026-10-26.json) | Task送信・委任・Worker・結果検証は未実施 |
| EKI Task admission | 合成Task 1件を`queued`で受理し、同一keyの再送が同じtask_idを返すことを確認済み | [submit](../tools/reference-eki-api/README.md)、[record](../evaluations/records/EKI-task-2026-10-26.json) | Worker未起動。実行・結果・委任完了は未検証 |
| EKI Task cancel | 合成Task 1件を`cancelled`/`CANCELLED`まで確認済み。result APIは501 | [cancel](../tools/reference-eki-api/README.md)、[record](../evaluations/records/EKI-cancel-2026-10-26.json) | Worker未起動。実行・結果は未検証 |
| EKI Worker test環境 | WSL/DockerでAgent/Control test profile、claim wire、Control Planeを確認済み | [worker env](../tools/reference-eki-worker/README.md)、[record](../evaluations/records/EKI-worker-env-2026-10-28.json) | Task実行主体ではなく、結果・委任完了は未検証 |
| EKI 固定コマンド実行 | 別プロセスのControl/Agentで実行とResultClaim送信を確認。Attemptは`verifying` | [receipt](../evaluations/records/EKI-execution-2026-10-31.json) | sandbox・資源上限なし |
| EKI Result Acceptance | 2名の独立verifier、RA-2で受理。再実行で出力digestを確認。AcceptedResult保存、Task terminal | [receipt](../evaluations/records/EKI-acceptance-2026-10-31.json) | 再実行は同一ホスト。sandboxなし。network/temp-disk制限なし |
| EKI 実行中CPU・メモリ・一時ディスク・network | 20ms間隔で監視し、超過時にプロセスツリーを停止。Linuxはプロセスグループ全体を集計。WindowsはJob Object（プロセス単位とジョブ合計のメモリ・CPU時間）、Linuxはbwrapで分離。bwrapはnetworkを持たないためnetwork上限を通信ゼロとして満たす。失敗がClaimとしてControlへ届きAttemptがclosedになることをe2eで確認 | [receipt](../evaluations/records/EKI-runtime-limits-2026-11-01.json) | 瞬間的な超過は取り逃し得る。bwrapはWSL Ubuntuで確認。network帯域・byte数は計測しない |
| TEI能力連鎖 | `TaskRequest→Attempt→ResultClaim→AcceptedResult`の型連鎖、flow順序、DataEffect、binding実装、HTTP binding契約をTEI定義・TAI契約で検査。順序はcompositionの`ActivationOrder`から導出し、依存を外すと名前順へ戻る負例も確認 | [chain](../evaluations/records/TEI-capability-chain-2026-10-31.json)、[caps](../evaluations/records/TEI-product-capabilities-2026-10-31.json) | 専用の順序構文はない。HTTP binding契約は合成receipt、実接続（202・400・再送・409）は[live receipt](../evaluations/records/TEI-EKI-live-2026-11-01.json)に分離。Worker実行は未実施 |
| SW-01 S1 ハーネスA/B | 外部ハーネス相当の隔離サブセッション（表示のみ、計3回）と既存read-only構造検査の対照。同文言・別scopeの旧受理転用を、Aは3回とも根拠の検証不能なまま保留・拒否し、Bはscope差とlineageの構造事実として拒否 | [record](../evaluations/records/SW-01-S1-harness-2026-10-31.json)、[rerun](../evaluations/records/SW-01-S1-harnessA-rerun-2026-10-31.json) | 同一モデル3回。別ハーネス製品での再実行（G2）はnot-run。実受理・権限は未検証 |
| EKI Task lifecycle on WSL | `queued`→`cancelled`/`CANCELLED`を確認済み | [worker env](../tools/reference-eki-worker/README.md) | Worker実行・結果は未検証 |
| EKI Native Runner spike | 終了コード・出力上限・期限/取消し・Supervisor接続・Windows/Linuxのプロセスツリー停止を確認。未対応sandbox/資源上限/GPU/digest/引数を拒否 | [eki-fabric #275](https://github.com/hat47x/eki-fabric/pull/275) | sandbox・CPU/メモリ制限なし。未信頼Task不可 |

## 検証

- GitHub Actions `tai-reference`のmatrixで10ツール（SCN-001、MMI、SEI、統合実行、D-04 render、TEI、公開gate、SUI link、SUI→D-04、EKI CLI）を`gofmt`・`go vet`・`go test`。
- 別jobでSUI API/EKI API/EKI Task/公開境界のPython testを実行する。
- MMI/SEIの実接続試験は、sibling checkoutがないCIではskip。
- 保存済みの統合実行recordは常に`runDigest`とcomponent invariantsを検証。
- 2026-10-28時点のmain CIはsuccess。

## 公開状態

- TAI、EKI、SEI、MMIは公開リポジトリ。MITライセンス。
- README先頭に、生成AIを用いた初期開発中のソースコード公開であることを明記。
- 4リポジトリでsecret scanning・push protection・Private vulnerability reportingを有効化。
- TEI Platformの非公開作業資料は非公開を維持し、非公開理由と公開条件を別の非公開リポジトリのREADMEに記録。
- 公開境界の回帰検査をCIで実行。

## 仮承認の境界

- `provisionalApproved=true`、`publicationApproved=false`、`authorityVerified=false`。
- 仮承認の根拠は`owner-instruction-2026-10-26`と`owner-decision-2026-10-29`。
- R-01〜R-05は合成文書でdevelopment accepted。公開用real-objectレビューは合成後の工程へ移す。
- 合成後の実物レビューで前提が崩れた場合は`provisionalApproved=false`へ戻し、D-04を未決へ戻す。
- 公開・外部作用・予約実行は行わない。

## 未確認

- 実在の施設規程・掲示・案内文とD-04の適合。
- 公開権限者の本人・役割・承認範囲。
- MMI/SEIの実運用環境、監査、版固定、複数利用者。
- P-06（主体規模比較）、N-05（EKI委任）。
- 受理→要再確認→同文言復帰を、実在の判断記録・権限・実資料で扱った結果。構造上の束縛の検査（`-decision-validity`）は合成bundleだけで、受理の有効性は判定しない。受理の有効性をDecision・lineage・Profileのどこに置くかはOwner判断（[#33](https://github.com/hat47x/tai-pleroma/issues/33)）。
- 利用者にとっての有用性。

## 次の判断

実物ベース再レビューの担当・日程・証拠の入手方法を決める。実装を先行させる場合は、R-01〜R-05の証拠が揃うまで仮承認の範囲を超えない。
