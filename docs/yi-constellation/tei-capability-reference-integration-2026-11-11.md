# TEI能力参照の段階的連携（2026-11-11）

状態: **実装・限定検証の記録（提案／未採用）**。TAIがYI Constellationの製品構成・能力参照・活動継続に必要な情報を、TEIの型付きモデルと共通CLI契約から参照する最小経路を実装し、4つのActivity状態で確かめた。製品仕様・Capability契約の採用判断ではない。

## 1. 目的と位置づけ

TAIの価値は、製品間の知的活動の統合と継続にある。TEIの意味モデル、Source/Revision、read-only投影をTAIへ移植するのではなく、**TEIを製品意味の正本のまま参照し、TAI側で活動の文脈と現在性を扱う**。この文書はその最初の段階の設計と検証範囲を記す。

実装は[integrations/pilot-tei-capability-reference](../../integrations/pilot-tei-capability-reference/README.md)に置く。TAI専用の新しい共通Agent Host、Registry、Scheduler、Storeは作らない。既存のTEI CLI、TEI Product Skill（`yi-tei-modeling`）が前提にする読み取り手順、TAIの既存Issue/評価の置き場を再利用する。

### 非目的

- TEI Kernel、Plugin、製品構成、公開Capability契約の変更。
- TEIの能力・Skill・意味受理をTAIへ複製すること。
- TEIの候補や診断を、TAIの活動判断・操作許可・業務完了へ昇格すること。
- 外部Harnessや実Consumerの接続を、合成ScenarioのPASSで成立扱いすること。

## 2. 参照した既存の議論

| 対象 | 参照した内容 | この実装での扱い |
| --- | --- | --- |
| [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) | Harness-first Integration。外部Harnessから各製品を利用する接続。 | 実Harness接続はS2として**NOT RUN**。この実装はCLI read-only経路のみ。 |
| [TAI #271](https://github.com/hat47x/tai-pleroma/issues/271) | Activity継続の選択的再資格化。過去観測と現在資格の分離。 | Revision差分とConsumer受領のstale検査に限定して接続。 |
| [TAI #488](https://github.com/hat47x/tai-pleroma/issues/488) | YIC Skill横断適合。Product単独性・実Load・現在資格の区別。 | `skillLoad=not-observed`を明示し、CLI成功をSkillロードへ昇格しない。 |
| [TAI #232](https://github.com/hat47x/tai-pleroma/issues/232) | Harness・製品間の機密境界。 | Handoffを選択・Source・Revision・Disclosure Scopeに限定。 |
| [TAI #74](https://github.com/hat47x/tai-pleroma/issues/74) | YI Constellation配布構想。 | 配布・版固定の判断は行わない。 |
| [TEI #2605](https://github.com/hat47x/tei-platform/issues/2605) | TEI Product Skill初期実証。 | Skill本文の手順を参照。実Loadの証跡とはしない。 |
| [TEI #3262](https://github.com/hat47x/tei-platform/issues/3262) | read-only Queryの共通投影。 | `model overview` / `model catalog` / `inspect` / `knowledge-*` / `trace`だけを使用。 |
| [TEI #3419](https://github.com/hat47x/tei-platform/issues/3419), [#1158](https://github.com/hat47x/tei-platform/issues/1158) | 共通APIの型付き契約。 | JSONの`schemaVersion`、`ok`、`error.code`、`authorityLimits`をそのまま保持。 |
| [TEI #951](https://github.com/hat47x/tei-platform/issues/951) | Plugin Capability契約。 | 契約変更はせず、`semantic-capability`の参照だけを行う。 |
| [TAI Draft #585](https://github.com/hat47x/tai-pleroma/pull/585) | 実TEI/SEI CLIによる再資格化Probe（並行Lane）。 | 変更しない。本実装は製品構成・能力参照の提示経路が対象。 |

TEI Product Skillの[SKILL.md](https://github.com/hat47x/tei-platform/blob/main/skills/yi-tei-modeling/SKILL.md)が示すとおり、`model catalog`の非空や`inspect`の成功は、利用者定義の読込み・意味受理・実行権限を意味しない。本実装もその区別を維持する。

## 3. 段階

| 段階 | 内容 | 状態 | 終了条件 |
| --- | --- | --- | --- |
| S0 | 製品構成・能力の限定一覧と詳細を、既存read-only CLIから取得して提示する | 実装・限定検証済み | 実CLIで`declared`と`SUBJECT_NOT_FOUND`を区別でき、Tool不在と混同しない |
| S1 | 活動継続に必要なRevision・Disclosure Scope・Consumer受領を束縛する | 実装・限定検証済み | Source更新と古いRevision受領を、TEIの型付き診断とTAI側の比較で検出する |
| S2 | 外部Harness SessionでProduct Skillを実Loadし、実Tool呼出しと回答を観測する | **NOT RUN** | 実Session ID、Skill本文digest、Tool request/response、独立Expectedが揃う（#168/#488、TEI #2509/#2605） |
| S3 | 別Productの実ConsumerへHandoffを渡し、受領・現在資格・Effectを各Ownerで確認する | **NOT RUN** | 実Consumerの受領記録と、Source/意味/権限の現在資格が別々に揃う（#271、各Product Owner） |
| S4 | 製品構成全体・公開Capability契約の変更 | 対象外 | 対象ProductのIssueで独立レビューを受ける |

S2/S3をS0/S1のPASSから推定しない。S4はこのパイロットの変更範囲に含めない。

## 4. 型付きの対応

| TAI側の項目 | TEIの既存入口 | 保持する内容 |
| --- | --- | --- |
| `productComposition` | `model overview`の`sections` / `sectionScope` | Application等の限定一覧、未カバーkind、宣言数 |
| `capabilityCandidates` | `model catalog`の`entries`（`semantic-capability`のみ） | 上限付きの能力一覧と総数 |
| `capabilities[].productCapability` | `inspect -subject-kind semantic-capability -subject-id` | `canonical`、Source artifact/位置、`authorityLimits`、世界/Source Index fingerprint |
| `capabilities[].disclosure` | `knowledge-context -disclose <scope>` | 選択・開示・省略Section、disclosure fingerprint |
| `capabilities[].dependencies` | `knowledge-context` | 宣言済みのoutgoing/incoming |
| `activityContinuation.reviewPlan` | `knowledge-review-plan` | 継続時のレビュー順、停止規則、plan fingerprint |
| `activityContinuation.trace` | `trace -scope current` | snapshot fingerprint、未解決投影 |
| `source.revision` | 上記結果の`worldFingerprint` / `sourceIndexFingerprint` / `modelRevision` | 同一Activityの比較単位 |

同じ実行内で返った値だけを`source.revision`へ採用する。複数コマンドの値を混ぜて「一回の全件検証」と呼ばない。

## 5. 次元の分離と負例

`view`は次の次元を独立に持つ。どれか一つの成功で他を補完しない。

1. **Product Capability**: `inspect`が宣言済み意味要素を返したか。`SUBJECT_NOT_FOUND`は対象IDの不在であり、能力全体の不在ではない。
2. **Tool availability**: `version -json`が`tei.cli.version/v0`とbuild identityを返したか。Tool不在ではProduct Capabilityを`unknown`に保つ。
3. **Skill load**: このツールでは`not-observed`。CLIの成功、Skill文書の存在、Skillの記述内容を実Loadの証拠にしない。
4. **Execution authority**: 要求Grantなし、`not-evaluated`。TEIが返す`authorityLimits`を保持し、`inspect`成功を操作許可へ読み替えない。
5. **Consumer receipt**: 明示HandoffとReceiptがなければ`not-delivered`。受領は現在資格・活動判断ではない。

代表的な取り違えを、実装の負例（`N1`、`R2`、`R4`）で固定した。Tool不在→`unknown`、対象不在→`not-found`、古いRevision→`stale`であり、いずれも`promotion`は`not-performed` / `not-made` / `not-granted`のままである。

## 6. 文脈の境界

TAIからTEIへ渡す要求は、次の4つに限定する。

- 選択対象（`semantic-capability:<id>`。1回の観測で最大5件）
- Workspace/Source（CLI引数のWorkspace。会話や別Productのデータは渡さない）
- Revision（Consumer検査では受領済みの`worldFingerprint` / `sourceIndexFingerprint` / artifact fingerprint / trace snapshotを使用）
- Disclosure Scope（`definition` / `dependencies` / `source`の明示選択。空は拒否）

TAIからConsumerへのHandoffは、上記に加えてActivity IDとConsumer IDだけを運ぶ。Handoffは固定allowlistで組み立て、`conversation`、`transcript`、`messages`、Workspace全体のbytesを含めない。`envelopeDigest`で内容の同一性を確認する。

TEIのselective disclosureは、TEI自身の`authorityLimits`が示すとおり**Access ControlやRedactionではない**。開示範囲の限定は、TAI側が送る範囲を狭める措置であり、TEIの認可判断の代替ではない。

## 7. 自動昇格しない境界

`view`、`compare`、`verify-consumer`は共通して次を返す。

- `teiCandidateToTaiDecision: not-performed`
- `teiDiagnosticToOperationPermission: not-performed`
- `activityDecision: not-made`
- `operationPermission: not-granted`

`stale`は「再資格化が必要」という参照状態であり、活動を止める判断でも、再実行の許可でもない。`fresh`も利用許可ではない。これらをTAIの活動判断へ変えるのは、既存のOwner/Host/Providerの判断と、必要なら人の確認による。

## 8. 検証

- 実行: `python integrations/pilot-tei-capability-reference/run_scenarios.py --tei <tei> --workspace <TEI>/reference/workspace --out evaluations/records/TAI-TEI-capability-reference-2026-11-11.json`
- 対象: TEI main `b8cbd432aae22ccf3fa75b0119e1d90d87ef0d11`のWindowsビルド、公開`reference/workspace`（manifest `sha256:8e367b05…f471af74`）。
- 結果: R1/H1/R2/R3/R4/N1がPASS。詳細は[evaluations/records/TAI-TEI-capability-reference-2026-11-11.json](../../evaluations/records/TAI-TEI-capability-reference-2026-11-11.json)。

**実行した検証**: 実CLIのJSON契約、型付き診断、fingerprintの変化、Handoffの最小性、Tool不在の分離。
**実行していない検証**: 外部Harnessの実Session、Product Skillの実Load、実Consumerへの配送、別Workspace・別権限・OS隔離、意味の正しさの独立採点。

## 9. 制約と未決

- `model overview`は`plugin` / `database` / `release`等を覆わない（`sectionScope.notCoveredKinds`）。製品構成全体の正本ではない。
- `model catalog`はSourceを読んだことの証拠であり、利用者定義の意味受理・現在資格の証拠ではない。
- `trace -expected-fingerprint`は外側`result.snapshotFingerprint`と比較する。内側の`result.trace.snapshotFingerprint`と混同しない。
- `effect: read-only`は正本の意味を変えないという意味であり、プロセスのファイル書込みが無いことの証明ではない。本実装は書込みフラグを渡さない。
- `knowledge-review-plan`はルーティングの指針であり、意味の現在資格・Cross-view変更の適格性を決めない。
- 1回の観測は最大5 Subject、一覧は既定20件に制限する。多数Subjectの一括参照は別の設計判断とする。
- 実Consumerの受領状態は、この実装ではファイルベースのReceiptで模擬する。実Product間の配送はS3。

## 10. 独立レビューの対象

この変更はTAIの接続実装・Scenario・記録だけを含み、TEIの製品構成・公開Capability契約・Authorityを変更しない。次に当たる変更は、このパイロットの一部として行わず、対象ProductのIssueで独立レビューを受ける。

- 製品構成全体の定義、Capabilityの公開契約、Plugin契約、意味受理の規則を変える変更。
- HandoffをTAIの共通契約・新しいRegistry・新しいAgent Hostへ昇格する変更。
- `fresh` / `stale`の判定を、活動の実行許可や業務完了の判定へ接続する変更。
