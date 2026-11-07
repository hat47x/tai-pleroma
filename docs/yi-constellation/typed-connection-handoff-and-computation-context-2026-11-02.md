# 型付き接続・計算文脈・証拠依存を区別する横断Handoff（2026-11-02）

**状態：TAIのConsumer設計・反証計画。Product API／共通Schemaの採用、実Harness・実Provider試験、Owner意味受理はNOT RUN。**

[全体計画](harness-skill-plugin-plan-2026-11-02.md)／[SK-01](../../evaluations/SK-01-harness-skills.md)／[Activity再資格化](activity-selective-requalification-and-handoff-2026-11-02.md)。主な既存OwnerはTEI [#988](https://github.com/hat47x/tei-platform/issues/988)、[#2507](https://github.com/hat47x/tei-platform/issues/2507)、[#2586](https://github.com/hat47x/tei-platform/issues/2586)、[#2620](https://github.com/hat47x/tei-platform/issues/2620)、[#2622](https://github.com/hat47x/tei-platform/issues/2622)、[#2497](https://github.com/hat47x/tei-platform/issues/2497)、TAI [#271](https://github.com/hat47x/tai-pleroma/issues/271)。

## 1. 深化した判断：接続は線の存在だけでは意味が定まらない

他レーンのTEI議論では、Block/Compositeを**構造、Behavior Semantics、Model of Computation、Realization**の直交する側面で扱い、接続の意味をPluginが与える方向が具体化した。Graphvizの同じ `a -> b` でも、参照、データフロー、Event、制御、制約、観測、Evidence依存は異なる。実際にTEI [#2620のGraphviz追補](https://github.com/hat47x/tei-platform/issues/2620#issuecomment-6576898946)は、`DOT → Graph Data`と`Graph Data + contextRole + mapping + plugin version → Domain Data`を別の解決としている。

TAIでは、この関係を**Product間Handoffが何を主張できるか**に結び付ける。図、Skill説明、Issue、ファイルのリンク、Tool Callが接続していても、その線だけで値の移動・因果・実行・利用者への到達を確定しない。TEIが内部の接続意味を解釈するOwnerであり、TAIは各Productから得た**既存の解釈済みの証拠**を用途相対に選択・引継ぎするConsumerとなる。

## 2. 比較する接続Roleと成立証拠

以下は**検査のための分類**であり、正式Role enumや新たなGraph Canonicalを指定するものではない。ひとつの接続に複数Roleが成立する場合もあり、解釈部品の版・Sourceを明示する。

| 接続の問い | 表現の例 | 追加で確認する内容 | 誤った昇格 |
| --- | --- | --- | --- |
| 参照 / containment | URL・Markdown字下げ・SHO Source occurrence | 対象・文書版・リンクの解決状態と関係の種別 | 親子整理を「論文AはBを引用」と断定 |
| データフロー / mapping | TEI Query→Context→Derived Dataset | Source/Field/Scope/Grain/Read footprint/取得完全性/Consumer実読取 | 設計Mappingだけで実取得・全件・保存済みと断定 |
| Event / notification | EKI Claim ACK、変更通知、外部Webhook | 起点、event/attempt ID、配送・受理・処理・重複、時点 | 送信ACKをBusiness Effect・文書納品と断定 |
| Control / Action Intent | 画面Action、TAI委任、TEI Command | 適用条件、現在Host Grant、対象Version、実CommitとReceipt | Action候補が見えたので実行許可ありと断定 |
| Constraint / validation | Data Rule、Method、Operator law | 宣言・対象全件性・評価実施・失敗/診断・強制位置 | 図上の禁止条件をOS/DBに実装済みと断定 |
| Observation / measurement | SEI根拠、テスト結果、TEI read trace | Claimの対象・観測時点・独立Oracle・公開範囲 | 値が同じなので別時点・別粒度の共同Claimも成立 |
| Evidence dependency | Source→Claim→SHO納品／再資格化 | どのClaimのどの条件を支えるか、依存の根拠・版・欠落 | 単にリンクした全ノードを同じ依存として全再検査 |

**Evidence依存は意味論的Dataflowと同じEdgeではない。** Dataflowが存在しても、あるClaimがその特定Field/版へ実際に依存したことは別の観測。逆に、文章の引用関係は処理データの流入を意味しない。既存TAI #271の選択的再資格化では、依存が特定できる部分だけを局所再検査し、根拠のない「依存なし」はunknownとして残す。

## 3. Model of ComputationとHandoffの時間条件

接続の成立は計算方式にも依存する。同期Call、Snapshot Batch、Reactive signal、Event stream、非同期Task/Attempt、Transaction/Commitでは、同じ矢印から導ける結果が異なる。

- **Batch / Snapshot**：Read set/ページ連結が一つのcohortと観測できるか。Keysetで順番が安定しても、ページ間に更新が入れば単一Snapshot Claimは成立しない（TEI [#2586 HJ-02/03/04](https://github.com/hat47x/tei-platform/issues/2586)）。
- **Reactive / Event**：通知が届いたこと、消費側が処理したこと、結果状態が更新されたこと、実Effectが観測されたことを区別する。再送・重複・順序入替え・停止後のEventにはAttempt/Sourceの束縛が必要。
- **Transactional Action**：現在Grantの検証とCommit/外部送信の境界、失敗時の部分結果/不明、冪等再試行の条件は実Host/Providerの責務（TEI #1174、EKI #407/#465）。Skillは説明と利用判断を助け、専用Transaction Engineを所有しない。
- **Stream / Window**：どのイベント集合、時間窓、Watermark、欠損/遅着まで含めたかで「全件」「最新」の範囲が変わる。通常のTable Queryと同じ全件Claimへ無音変換しない。
- **Composite / Rate mismatch**：上流と下流の評価頻度・Clock/Version/Sourceが異なると、局所PASSを同時成立とみなせない。意味上必要な一致条件が不明なら共同Claimはunknown。

これらはTEI #988のOperator評価順/副作用、TEI #2582の鮮度、TEI #2600の増分再計算、EKIの実配送/Attempt、SEI #767の認識十分性へ役割別に戻す。

## 4. 同じ値・同じ矢印でも成立条件が異なる事例

**SelectとValidate**：全明細 `L=[(A,q=2),(B,q=0)]` に `filter(q>0)` を行えば派生結果はAのみで正しい。しかし派生結果の `all(q>0)` は、元の全明細の `all(q>0)` と異なる。Dataflowによる「選別」を、全母集団への「制約充足」Edgeと扱うと、許されないActionに至る。TEI [#988 SV-04/05](https://github.com/hat47x/tei-platform/issues/988#issuecomment-6577015922)／[#2586 HJ-SV1](https://github.com/hat47x/tei-platform/issues/2586#issuecomment-6577037688)が意味Owner。

**近似数値を経由したAction**：上流の誤差 `|x−x̂|≤0.01` は、下流の `f(x)=x²` の誤差0.01を保証しない。閾値 `x²≥100` は `x=9.99` と `x=10.01` で判定が変わる。Value表示・Metricの近似適合と、Business Action/Claimに必要な境界条件・許容誤差は別。Domainと演算Lawを含めて上流保証→下流必要条件を照合する（TEI #2507 AC-Q）。

**引用と成果物到達**：SHOの論文URLは資料への参照であり、本文取得・解析・TEI設計への意味受理を保証しない。EKIのTask ACKは出力本体を届けない。**同一AttemptのBody digestと実受領→SHO実読取版→利用者へのDeliver**を別の証拠でつなぐ。TAIは結果の引用を単に増やすのではなく、当該Handoffで成立した段階を説明する。

## 5. Product間で引き継ぐ最低限の比較列

新しいシリーズ中央DBやManifest Schemaを採用するのではなく、既存Productが持つ証拠から用途に必要な列を選択する。

| 領域 | 比較列 |
| --- | --- |
| 対象 | Product、Source/Subject/Occurrence/版、Role/Operator IDと解釈版 |
| 接続 | 端点・接続Role・Direction・Binding/Transform・Role未決 |
| 計算 | Model of Computation、Clock/epoch/Window、Read/Effectの順序 |
| Claim | 何を保証するか、対象Scope/Grain/Bag/NULL、前提・独立Oracle、Failure/Unknown |
| 物理 | 実Tool/Provider/Host版、実Read/Delivered/Consumer receipt、Attempt・digest |
| 公開 | Consumer別公開資格、Metadata秘匿、現時点のGrant、Owner受理状態 |
| 再開 | 何が変わったか、実際の依存線、再資格化対象、旧履歴として保持する結果 |

不明な列は「all」「none」「valid」といった強い値で埋めない。参照できる既存Productの実観測と、AI/図からの候補を区別する。

## 6. SK-CE受入群と実施順序

[SK-01 §S](../../evaluations/SK-01-harness-skills.md)の**SK-CE01〜CE16**を比較ケースとする。先行[SK-C](../../evaluations/SK-01-harness-skills.md)はEvidenceの変更依存閉包、SK-CEは**接続の意味の誤分類／時間・観測条件の喪失**を検出する担当。TEI内部のOperator/Connection適合・正式Role判断はTEIで受理し、TAIにはその結果だけを渡す。

- **P0 Read-only**：SHO研究リンク、TEI標準データ/Typed DOT、SEIの独立Claim、EKI Attemptの公開合成例を同じ「Edge」と仮定した場合との差を比較。新Role Schema・図専用Editorを前提としない。
- **P1 Product別**：TEI実CLI/Meaning/Providerに現存するRead-only情報で、対象Bindingと未知を記録。SEIのClaim十分性、SHO Source occurrence、EKI Body受渡しは各Ownerの既存Toolが存在する範囲で観測。
- **P2 二製品**：実行できる2 Product間の一つの引用・Dataflow・Result Bodyのいずれかを選び、同一Source/Clock/Claimでの資格を評価。局所テストPASSを共同Claimへ自動昇格しない。
- **P3 横断/Harness**：イベント再送・Clock変更・Plugin追加・非公開能力・Host Grant変化を含み、Product単独SkillとTAI横断Skill（H2/H3/H4/H5）、全再検査と選択的再資格化（J0/J1/J2）を比較。誤成功、必要な再試験の見落とし、不要な再実行、Tool/Token/Review費用を測定。

**受理境界**：本設計はSkill/TAIによる操作意味の創設ではない。CSWの自由探索中に評価Gateを挿入するものでもない。既存Product Ownerが意味・提供能力・実Target/Authorityを保持する。正式な各Product Tool、複数Host、実ユーザー環境での検証はNOT RUN。
