# SCN-001「実行→検証→受理」の三視点整合

状態: **Draft（上流の整理）**。方法の定義は[EKI ADR-0033](https://github.com/hat47x/eki-fabric/blob/main/plan/adr/0033-three-element-realignment.md)を正本とし、この文書はSCN-001の経路へ適用した結果だけを記します。新しい要求や受理済み判断を作るものではありません。

## 1. なぜ上流へ戻るか

下流のreceiptは揃いました。EKIはHTTP submitからResult Acceptanceまで到達し、TAIのrun receiptはそのreceiptをdigestで参照しています。しかし、次の問いはまだ業務の判断として決まっていません。

- 誰が「この検証方法でよい」と決めるのか
- 誰がVerifierを信頼の基盤として認めるのか
- 誰がResultを受理し、その判断を説明するのか

これらを決めずに機能とデータだけを足すと、記録は増えても「誰の判断か」が空のままになります。ADR-0033の順序（業務 → 機能 → データ）に従い、経路を三視点で整理し直します。

## 2. 三視点

| 視点 | この経路での内容 | 主な参照 |
| --- | --- | --- |
| **業務** | 依頼、検証方法の承認、Verifierの信頼、Resultの受理、公開の判断 | [Owner packet](SCN-001-owner-review-packet.md)、[実物ベース再レビュー](../evaluations/SCN-001-real-object-review.md) |
| **機能** | 受理、配置、実行、Result Claim、検証、Result Acceptance、公開gate | EKIの`internal/control`、[run receipt](../evaluations/records/SCN-001-run-2026-11-01.json) |
| **データ** | Task、Attempt、Lease、WorkOrder、ResultClaim、AcceptedResult、run receipt、Owner packet | EKIの`internal/core`、[EKI receipt](../evaluations/records/EKI-http-agent-2026-11-01.json) |

同じ対象が視点によって別の要素になります。たとえばAcceptedResultは、データとしては実体、機能としては受理の出力、業務としては依頼元への説明の根拠です。

## 3. 三つの対応

### 3.1 業務 → 機能

| 業務の判断 | 支える機能 | 現在の状態 |
| --- | --- | --- |
| 仕事を依頼する | Client APIのTask admission | 実装済み。TEST PROFILEで202を確認 |
| 仕事を実行可能にする | READYへの昇格とdispatch | 昇格はtest内の明示操作。運用者向けのAPI・UIは確認できない |
| 検証方法を承認する | Result Policy（RA1/RA2、dimension） | 静的設定。承認した主体と日時は記録されない |
| Verifierを信頼する | Verifierの受理呼出し | 信頼の判断を記録する場所がない |
| Resultを受理する | Result Acceptance | プロセス内のサービス。Client APIからの受理入口は確認できない |
| 公開する | Publication gate | `allowed=false`。blockedのまま |

### 3.2 機能 → データ

| 機能 | 書くデータ | 残る範囲・残らない範囲 |
| --- | --- | --- |
| Task admission | Task | 依頼内容のdigestと状態 |
| dispatch | Attempt（ASSIGNED→DISPATCHED）、Lease、WorkOrder | 誰がdispatchしたかは運用者の操作として残らない |
| Agent実行 | ResultClaim | 実行したWorkerと出力digest |
| 検証 | Verification（受理呼出しの引数） | dimensionの値は受理の判断に使われるが、独立したデータとして残らない |
| Result Acceptance | AcceptedResult、Attemptのclose、Taskのterminal化 | Verifier ID、assurance level、policy digestは残る。dimensionの値と信頼した主体は残らない |

`AcceptedResult`が保持するのはVerifier ID、assurance level、policy digestなどです（`internal/core/acceptedresult`の`Record`を2026-11-01に確認）。「何が独立していたか」と「誰がそのVerifierを信頼したか」は、受理後にデータから示せません。

### 3.3 データ → 業務

| データ | 誰のどの判断の根拠か | 現在の状態 |
| --- | --- | --- |
| AcceptedResult | 依頼元への説明、施設担当の受理判断 | 受理した主体は記録されない |
| run receiptの`externalExecution` | Ownerの公開判断の材料 | EKI receiptをdigestで固定。参照であり実行そのものではない |
| Publication gate receipt | 公開してよいかの判断 | `allowed=false`とblocker一覧 |

## 4. 欠けている視点

| ID | 欠け | 症状 |
| --- | --- | --- |
| G1 | 業務: 受理判断の主体、Verifierを信頼する主体 | 機能とデータは揃ったが、誰の判断か説明できない |
| G2 | 機能: 受理の外部入口 | 受理はtestのプロセス内でしか呼べておらず、運用者が実行する経路がない |
| G3 | データ: 独立性のdimensionと信頼した主体 | 受理後に「何が独立していたか」を示せない（Assurance Model Axis E） |
| G4 | 業務→機能: 公開gateのblocker | Verifierの信頼がblockerの項目になっていない |

これらは実装の難しさではなく、上流の判断が欠けていることの現れです。G1を決めずにG2やG3を実装すると、誰も使わない入口や、説明できない記録を増やすことになります。

## 5. 次に決めること（業務 → 機能 → データの順）

1. **業務**: SCN-001でResultを受理する主体と、Verifierを信頼する主体を決める。Owner packetの「検証の独立性」の3問がこれにあたる。
2. **機能**: 受理を誰がどの経路で実行するかを決める。外部API、運用コマンド、人間の手動確認のどれか。
3. **データ**: 上の決定に応じて、dimensionの値、信頼した主体、受理した主体を残すかを決める。

### SUIの扱い（Owner指示 2026-11-01）

SUIのマルチテナント化は、TEIによるSUIの再構築を進めた後に扱います。現行SUIのテナント境界・認可adapterのtestは既存実装の確認であり、マルチテナント化へ着手する根拠にはしません。SCN-001の意味形成を、再構築後のSUIへ接続するか、現行の参照接続を維持するかは、再構築の設計が決まってから判断します。再構築の進め方は[TEIによるプロダクト構築への移行計画](tei-construction-migration-plan.md)に置きます。

## 6. 境界

- この文書は要求の正本ではありません。要求は各リポジトリの`requirements/`、方法はADR-0033が正本です。
- ここに書いた「確認できない」は、2026-11-01時点のコードと成果物を読んだ範囲の観測です。
- 公開gateは`blocked`のままです。合成結果を実証拠として扱いません。
