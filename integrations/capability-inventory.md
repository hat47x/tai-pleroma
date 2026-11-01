# 関連基盤の接続調査（初期）

確認日: 2026-10-26（下の表）。状態: **README/設計文書の静的確認と、MMI・SEI・TEI・SUI・EKIへの参照接続5件、および統合参照実行**。この一覧は現在のAPI接続やEnd-to-Endの動作保証ではない。

確認したmainのcommitを固定する。文書中の記載があっても、現在のheadでの関連試験や外部呼出しは別途確認する。表の版は静的確認に使った参照文書の版であり、参照接続の実行に使った版とは限らない。実行に使った版は各参照接続のreceiptと[evaluations/records](../evaluations/records/)に記録する（例: SEIは記録済みの統合参照実行で`d818028`）。

| 基盤 | 確認したmain | 静的に確認できる範囲 | SCN-001で未検証のこと |
| --- | --- | --- | --- |
| [SUI](https://github.com/hat47x/sui-sensemaking/blob/b0f5bae138c9289b46eae2d5f3fd6630a1175a08/README.md) | `b0f5bae` | 意味形成、候補と保留、出典へ戻れるカード・島、レビューを伴う出力をREADMEで説明。APIの`/healthz`・`/openapi.json`・`/docs`・5 card/3 island/1 edgeのGETを確認 | 観測カードとTAIの入力を正本の意味を損なわず受け渡す方法、実資料・認可 |
| [TEI](https://github.com/hat47x/tei-platform/blob/490dd205cdcdd03c1af03d67a6f8803c83eca0be/docs/status.md) | `490dd20` | CLIと参照Workspace、モデル検証・生成等の参照実装。SCN-001型のvalidate参照接続を追加 | 会議室の規程の正式モデル化・実データ・受理・作用・結果確認 |
| [SEI](https://github.com/hat47x/sei-cognition/blob/fd329e10554c677058702d574ae9678fed786842/README.md) | `fd329e1` | 意味の区別、来歴、semantic-contract、限定的な参照実行を説明。SCN-001のdecision-memory projection参照を追加 | 実運用store、権限、公開、SCN-001入力との契約適合 |
| [SHO前身MMI](https://github.com/hat47x/markdown-matrix-injector/blob/a8addd1560bd02131b29ade4d9d1cfa7ca5f9b21/04_Documentation/mcp-server.md) | `a8addd1` | MMIのCLI/MCPで読出し、検索、選択、検査、render等を提供と記載。TAIから`inspect`/`select`を呼ぶ参照接続を追加 | 配布版・実運用の認可・版固定、SHO Composerの書込み系契約 |
| [EKI](https://github.com/hat47x/eki-fabric/blob/84f03d116f60454636dd1c1b37b30b395bcd17fb/README.md) | `84f03d1` | 範囲・期限・信頼に応じた委任を中核とする構想、限定されたArchitecture Baselineを説明。`eki-control`/`eki-agent`のversionとControl APIの認証通過を確認 | 実Provider・Taskの送信、委任、Worker、結果検証、Authority |

## 参照接続の記録

- **MMI**: [reference-mmi-readonly](../tools/reference-mmi-readonly/README.md)がローカル開発チェックアウトのMMI MCP `markdown-matrix-injector/0.2.0`へstdio接続し、`inspect`と`select`を実行した。O-02/O-03/O-07の3行を取得し、O-02とO-03の文言差を保持した。境界外`../outside.csv`と存在しない`missing.csv`を拒否し、CSV/guideのdigestは不変だった。配布版、実運用の認可、版固定、書込みは未検証。
- **SEI**: [reference-sei-decision](../tools/reference-sei-decision/README.md)がSEIの一時storeへ`rec-01`と`dec-01`を記録し、`sei resume --json`で2 records、`dec-01`、未解決`authority:unknown`を確認した。合成fixtureであり、実運用store・権限・公開・署名は未検証。
- **TEI**: [reference-tei-model](../tools/reference-tei-model/README.md)がSCN-001の`Observation`/`RuleCandidate`型をTEIの`validate`で検証し、`ok`とworkspace digest不変を確認した。型宣言だけで、実データ・意味・Authorityは未検証。
- **SUI**: [reference-sui-api](../tools/reference-sui-api/README.md)がSUI APIの`/healthz`、`/openapi.json`、`/docs`、5 card/3 island/1 edgeのDocumentV1を読み、`status=ok`、OpenAPI `3.1.0`、65 paths、`scn001-demo`（O-02/O-03/O-06/O-07/O-08、I-01/I-02/I-03）を確認した。[reference-sui-link](../tools/reference-sui-link/README.md)がcard digestとisland構成をSCN-001 fixtureへ照合した。実資料・テナント・認可・意味形成の正しさは未検証。
- **EKI**: [reference-eki-cli](../tools/reference-eki-cli/README.md)が`eki-control --version`と`eki-agent --version`を実行し、`eki-control dev`/`eki-agent dev`、commit、Go versionを確認した。[reference-eki-api](../tools/reference-eki-api/README.md)が一時Control Planeの`GET /v1/tasks`で405（認証通過）を確認し、合成Task 1件を`queued`で受理した。Workerを起動していないため、実行・結果・委任完了・Authorityは未検証。
- **統合参照実行**: [reference-scn001-run](../tools/reference-scn001-run/README.md)がMMI・SEI・SCN-001評価を1つのreceiptへ束ね、`runDigest`を生成した。`humanReviewed=false`、`authorityVerified=false`、`published=false`であり、知的機能の受入合格ではない。

## 接続を増やす順序

1. **最初の候補**: 文書または既存ツールによる読み取り専用の情報取得と、出典版を追跡する手動記録。出力の内容を検査できることを優先する。
2. **次の候補**: 意味と判断を保持したまま、SEI等の既存契約に照らして適合性を検査する。適合しない場合は変換の採否を別途判断する。
3. **必要になった段階**: TEIの正式モデル・生成、SHOの編集・保存、EKIの限定委任を、各製品における成立条件とともに検証する。

どの段階でも、製品の「設計に記載されている」「合成試験済み」「実接続済み」「人間に有用と確認済み」を区別する。公開・書換え・権限付与を伴う操作はOwnerの確認を要する。

## 不足が判明したら

不足を見つけた場合は、その場で新APIを設計するのではなく、対象の基盤、対象版、使いたい利用者操作、既存機構との差、反証できる観測条件を記録する。必要なら元の基盤のIssueへ接続する。
