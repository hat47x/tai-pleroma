# 評価・検証

統一的な知的機能が実際に成立するかを、再現可能な試験と観測で確かめます。

対象シナリオ・対象版、期待結果、負例、実行条件、結果と未実施項目を記録してください。合成fixture・モック・実環境観測を明確に区別します。機微情報の原本は格納せず、公開可能な証拠への参照を利用します。

## P-06 利用者価値と協働統治の比較（計画／NOT RUN）

- [個人・組織・社会の比較プロトコル](P-06-cogovernance-protocol.md)：AIの提案、各主体の決定・承認・公開を区別し、手作業との対照で増分価値を確かめる。
- [試行記録テンプレート](P-06-trial-template.md)：評価前の目標、版、負例、判定と未実施を記録する。**このファイルは試験結果ではない**。
- [Issue #127](https://github.com/hat47x/tai-pleroma/issues/127)：最初の利用者・権限者と、開始条件のOwner判断を追跡する。

## 参照実行の記録

- [SCN-001実物ベース再レビュー](SCN-001-real-object-review.md): 合成後に行う公開用実物レビューの計画。R-06/R-07は未実施。
- [SCN-001合成施設文書による工程欠陥検査](SCN-001-synthetic-facility-review.md): 創作文書で工程欠陥を検出する検証。実物レビューではない。
- [応答を失ったあとの回復判断：実EKIでの1件](EKI-effect-unknown-recovery-2026-11-12.md): ResultClaimの受理確認を失わせた実プロセス観測。同じ識別子の再送は重複排除、Agent再起動では出力本体が失われ、Client APIからは区別できない。業務上の外部作用は未実施。
- [SCN-001 成果の観測](SCN-001-outcome-observation-2026-11-11.md): 技術的成果・受取先の受領・公開権限・公開というGoal・価値を別々に判定した記録。T-Draftは成立、公開は未達、価値は未評価。
- [SCN-001実物レビュー要求の変更](SCN-001-owner-decision-2026-10-29.md): 合成文書によるdevelopment acceptedと、生成AI評価・人間レビュー後置のOwner判断。
- [SCN-001生成AI development reviewの観点](SCN-001-ai-development-review-rubric.md): D-04を確認する5観点。
- [SCN-001-ai-review-2026-10-29.json](records/SCN-001-ai-review-2026-10-29.json): 生成AIによるdevelopment review receipt。`quality=sufficient-for-development`、`humanReviewed=false`。
- [SCN-001-synthetic-flow-2026-10-29.json](records/SCN-001-synthetic-flow-2026-10-29.json): 合成文書→MMI→SEI→TEI→SUI→D-04→AI review→EKI test環境→gateの接続receipt。`publicationAllowed=false`。
- [SCN-001-eki-feasibility-2026-10-29.json](records/SCN-001-eki-feasibility-2026-10-29.json): EKI Worker test環境のfeasibility review。`quality=sufficient-for-feasibility`、`taskExecution=false`。
- [SCN-001-synthetic-facility-2026-10-28.json](records/SCN-001-synthetic-facility-2026-10-28.json): 合成文書の欠陥検査receipt。`synthetic=true`、`publicationAllowed=false`。
- [SCN-001-synthetic-mmi-2026-10-29.json](records/SCN-001-synthetic-mmi-2026-10-29.json): 合成workspaceのMMI読み取り専用receipt。`synthetic=true`、`selectedRows=5`。実認可は未検証。
- [SCN-001-review-status.json](SCN-001-review-status.json): R-01〜R-05は合成で`accepted`/`synthetic`。R-06/R-07は`pending`。公開gateはblocked。
- [SCN-001-D-04-provisional.md](artifacts/SCN-001-D-04-provisional.md): 仮承認に基づく内部レビュー用Draft。公開用ではない。
- [SEI-decision-2026-10-26.json](records/SEI-decision-2026-10-26.json): SEI decision-memoryの合成fixture receipt。`synthetic=true`、`recordCount=3`。
- [TEI-model-2026-10-29.json](records/TEI-model-2026-10-29.json): TEI型検証の合成fixture receipt。`synthetic=true`、`validation=ok`。
- [SUI-api-2026-10-26.json](records/SUI-api-2026-10-26.json): SUI APIの`/healthz`、`/openapi.json`、`/docs`、5 card/3 island/1 edgeのDocumentV1 GET record。`synthetic=true`。実資料・認可・SCN-001データは未検証。SUI→SCN-001対応は[reference-sui-link](../tools/reference-sui-link/README.md)で照合。
- [EKI-cli-2026-10-26.json](records/EKI-cli-2026-10-26.json): `eki-control`/`eki-agent`のversion起動record。Task・委任・Authorityは未検証。
- [EKI-api-2026-10-26.json](records/EKI-api-2026-10-26.json): EKI Control APIの`GET /v1/tasks`が405を返し、Client credentialの認証通過を確認したrecord。
- [EKI-task-2026-10-26.json](records/EKI-task-2026-10-26.json): 合成Task 1件を`queued`で受理し、同一Idempotency-Keyの再送が同じtask_idを返したrecord。Worker未起動のため、実行・結果・委任完了は未検証。
- [EKI-cancel-2026-10-26.json](records/EKI-cancel-2026-10-26.json): 合成Task 1件を`cancelled`/`CANCELLED`まで確認したrecord。Worker未起動のため、実行・結果は未検証。
- [SCN-001-run-2026-10-26.json](records/SCN-001-run-2026-10-26.json): MMI・SEI・SCN-001合成評価の統合receipt。`runDigest=sha256:53600dc...`、`humanReviewed=false`、`authorityVerified=false`、`published=false`。`reference-scn001-run`の`-verify`で内部整合を再確認できる。受入合格ではない。
- [yi-constellation-structure-2026-11-01.json](records/yi-constellation-structure-2026-11-01.json): Yi Constellationの64卦表、8×8配置、36変爻、象の引用、綜卦、序卦の構造検算。`passed=true`、`errors=0`。意味の解釈は対象外。
- [yi-64-hexagrams.json](fixtures/yi-64-hexagrams.json): 64卦の番号、卦名、卦の並び、大象のfixture。19の検算が使う。
- [yi-appendix-quotes.json](fixtures/yi-appendix-quotes.json): 序卦伝と雑卦伝の八つの引用のfixture。19の検算が使う。
- [audit-yi-constellation.py](audit-yi-constellation.py): 上記の検算を再実行するスクリプト。外部ライブラリは不要。
- [audit-robotics-records.py](audit-robotics-records.py): 自動運転とロボティクスの四つの記録を、合成fixtureで検証するスクリプト。外部ライブラリは不要。
- [robotics-records-2026-11-02.json](records/robotics-records-2026-11-02.json): 四つの記録の合成fixture九件の検証receipt。`synthetic=true`、`passed=true`、自己試験あり。実車・実ロボット・実安全制御器は未検証。
- [ad/](fixtures/ad/): 自動運転の合成fixture。テイクオーバー、インシデント、ディスエンゲージメント、旧ECUからの移行。
- [robotics/](fixtures/robotics/): ロボティクスの合成fixture。ピックアンドプレースの受け渡し、出来事、判断、意味の対応。
- [schemas/](../docs/yi-constellation/schemas/): 出来事、受け渡し、判断、意味の対応のJSON Schema。暫定版0.1。
- [46-四つの記録のスキーマ](../docs/yi-constellation/analysis/46-四つの記録のスキーマ.md): 四つの記録の暫定スキーマ、合成fixture、検証結果、回収した知見。

## ハーネス引渡しの負例（新規実験NOT RUN）

- [証拠・権限の負例マトリクス](harness-boundary-negative-cases.md) — ハーネス切替時の過去Decision、Source/Scope、Pluginの検証、EKIの結果受理と実世界Outcome、個人・組織・社会の権限を別々に検査する候補。これは試験結果ではなく、[横断設計](../docs/harness-evidence-boundary.md)に対応する評価計画。

## TEI投影・保存の検証（2026-11-03）

4製品の投影から、合成・TLS・実DB保存までを記録した。いずれも`publicationAllowed=false`で、受入・公開の判断ではない。

### 投影とconsumer

- [SEI Decision選抜](records/SEI-TEI-decision-selection-2026-11-03.json)・[artifact](records/SEI-TEI-artifact-2026-11-03.json)・[consumer](records/SEI-TEI-consumer-2026-11-03.json)・[実artifact読み取り](records/SEI-TEI-real-artifact-2026-11-03.json)
- [MMI Format Profile選抜](records/MMI-TEI-format-profile-selection-2026-11-03.json)・[artifact](records/MMI-TEI-artifact-2026-11-03.json)・[consumer](records/MMI-TEI-consumer-2026-11-03.json)・[実artifact読み取り](records/MMI-TEI-real-artifact-2026-11-03.json)
- [EKI TaskRequest選抜](records/EKI-TEI-task-request-selection-2026-11-03.json)・[artifact](records/EKI-TEI-artifact-2026-11-03.json)・[consumer spike](records/EKI-TEI-consumer-2026-11-03.json)
- 横断: [4製品のスキーマ検証](records/TEI-artifacts-crosscheck-2026-11-03.json)・[再生成の同一性](records/TEI-artifacts-determinism-2026-11-03.json)

### 合成と保存

- [SCN-003の識別子確認](records/SCN-003-artifact-links-2026-11-03.json)・[合成](records/SCN-003-compose-2026-11-03.json)・[SUI保存](records/SCN-003-save-2026-11-03.json)
- [TLS配信](records/SUI-TEI-tls-2026-11-03.json)
- [埋め込みPostgres保存](records/SUI-TEI-postgres-2026-11-03.json)・[Alembic migration経由](records/SUI-TEI-postgres-migrate-2026-11-03.json)
- 一括: [suite](records/TEI-suite-2026-11-03.json)（8段）

### 失敗・未解決

- [Postgres最初の試行](postgres-attempt-2026-11-03.json): 409。原因はテナント行の欠落で、後に解消。
- [SaaS起動試行](saas-startup-probe-2026-11-03.json)・[stub起動](saas-stub-startup-2026-11-03.json): 6項目の不足と、stub設定での起動・401。外部HTTP先は未実装。
- [SaaS前提の整理](../analysis/sui-saas-prerequisites-2026-11-03.md)

### EKIへの投入と配置（2026-11-03）

- [EKIへ投入](records/EKI-TEI-submit-2026-11-03.json): 投影TaskRequestを実`eki-control`へPOSTし、202・queued・同一Idempotency-Keyの同一task_idを確認。
- [Dispatch有効化の試行](eki-dispatch-attempt-2026-11-03.json): 署名鍵とDispatch設定で起動。policy未投入では「policy is not available」。
- [policy投入後の試行](eki-dispatch-attempt-2026-11-03.log): Taskは検討対象になるが「no usable worker is registered」。
- [policyとWorker行の投入](records/EKI-TEI-dispatch-running-2026-11-03.json): Taskがrunningへ進む。Workerプロセスは動かしておらず、結果は無い。
- 実行・結果受理はEKI側で未配線（[EKIの実行系が未配線](../analysis/tei-sui-integration-2026-11-03.md)）。

### SUIの製品面（2026-11-03）

- [監査ログのHTTPエクスポート](records/SUI-TEI-audit-2026-11-03.json): 閲覧でイベント1件、docIdとBearerヘッダを確認
- [管理APIの認証分離](records/SUI-TEI-admin-2026-11-03.json): 匿名401・業務キー401・管理キー200
- [利用者provision](records/SUI-TEI-provision-2026-11-03.json): 201・冪等・監査3件
- [TEI artifactの配信](records/SUI-TEI-reference-2026-11-03.json): `GET /docs/{id}/epistemic/projection`が200でartifactを返す
- [Postgres+TLS](records/SUI-TEI-postgres-tls-2026-11-03.json): 保存・取得・匿名401
- [TLS終端プロキシ](records/SUI-TEI-proxy-2026-11-03.json): プロキシ越しの保存・取得
- [ローカルCAのチェーン](records/SUI-TEI-ca-chain-2026-11-03.json): 信頼は通るが未信頼クライアントは拒否
- [2インスタンスと共有Postgres](records/SUI-TEI-multi-instance-2026-11-03.json): 相互読み取りと古いETagの409

