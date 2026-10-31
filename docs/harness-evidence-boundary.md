# ハーネス横断の認知・作用・証拠の境界（設計案）

状態：**Draft / 非規範 / 提案、実際のハーネス間統合は未受入**  
基準TAI main：`74981e9b02e8c74f4950e2dbc57ac4a8058f72b8`（2026-10-31、作業ブランチの基点）。  
追跡：[Harness-first #168](https://github.com/hat47x/tai-pleroma/issues/168)、[P-06 #127](https://github.com/hat47x/tai-pleroma/issues/127)、[外部ハーネス計画 Draft #169](https://github.com/hat47x/tai-pleroma/pull/169)、[研究計画 Draft #129](https://github.com/hat47x/tai-pleroma/pull/129)。

## 1. 必要な設計判断

TAIシリーズの主要な利用入口はClaude Code、Codex、Dots、Grok Bot等の**外部生成AIハーネス**を想定する。TAIは第二のAgent、中央Host、共通DB、万能Plannerを先に作らず、必要な製品能力を呼び出すための活用知識・参照・検査・継続を扱う。独立製品の意味正本、Providerの実権限、本番の外部結果を取得したつもりにならない。

**追加したい横断の焦点は、「次の作業にどの主張を渡してよいかを、証拠の射程とともに示すこと」である。** ハーネスが「判断済み」「実行済み」「公開可能」と説明しても、元の証拠がその主張を保証しなければ、表示・受渡し・次の操作で昇格させない。これは新しい交換SchemaやAuthorityの制定ではなく、各製品の既存契約を確認するための**Consumer側の評価観点**である。

## 2. 主張を分解する：一つの PASS に集約しない

| 主張の種類 | その主張に必要な証拠例 | 主なOwner・既存責務 | 単独では保証しないもの |
| --- | --- | --- | --- |
| 原資料の参照 | Sourceの種類・版・範囲・取得可否、必要なら原byte/digest | 原資料Owner、SHO/MMI、各Source Provider | 解釈の正しさ、利用許可、最新版性 |
| 仮説・反証の形成 | 観測との対応、競合仮説、欠測と保留 | SUI、利用者、必要に応じCSW等の認知Method | 正しい事実・正式なDecision |
| 意味参照と時点 | qualified semantic ref、scope、source/model revision、当時のbasis、lineage | SEI、TEI、既存Source/Model Owner | 現在の受理、現行Authority |
| 構造・型・生成物の検証 | 対象集合、適用した検査、実行版、期待/観測、digest | TEI、各製品テスト・Validator | 業務意味の適合、第三者の同意 |
| 人による意味受理 | 対象・版・適用範囲・責任主体・採否・確認時点 | 人間/業務Owner、各製品の既存記録 | ほかのscopeへの自動転用、実行許可 |
| 実行の認可 | 現在の主体・対象・操作・期限・効果の範囲をProviderが検査 | 実際のHost/Provider、運用主体 | 機能発見、Tool呼出し成功では代用不可 |
| Task実行・結果受理 | attempt、ResultClaim、独立verifier、AcceptedResult | EKI/対象Runner・Verifier | 外部システムでの業務完了 |
| 実世界の効果・成果 | Provider receipt・再照会・独立した状態観測と目的の評価 | 外部Provider/実世界のOwner、利用者 | Task terminal・処理exit・AIの成功報告 |
| 公開・配布 | 対象・公開主体・権利・機微情報検査・承認と版 | 原Product/Publisher/サイトOwner | CI PASSやRegistry attestだけで公開許可 |

一連の処理が複数段階を通過しても「全ての権限を継承した」と推定しない。実験のreceiptは、**検証がどこまで行われたか**の記録であり、意味判断やAuthorityの正本ではない。

## 3. 更新・選択・委任の新旧を混同しない

同じ本文やdigestに戻った場合でも、次の軸は独立に変わる。

1. **認知の基礎**：出典/取得時点/Source revision、観測した本文、未取得、反証。
2. **意味の同一性**：対象のqualified scope/semantic ref、Model/Projection revision、Graph/Consumerの選択epoch。
3. **判断の射程**：Decisionの当時のbasis、採用・失効・再受理の範囲、誰がどの時点で判断したか。
4. **能力と操作の現在性**：Plugin/Contract/Provider/Instance、利用できるCapability、現行の認証・権限・操作対象。
5. **処理と結果**：Task/Attempt/ResultClaim/AcceptedResult、外部effectと独立Outcome、結果不明時の再照会。

この5つは、**同一の統一Revision型**にまとめる提案ではない。各Ownerの既存表現に必要な粒度で対応付け、足りないときは`unknown`/保留する。例えばTEI Studio #1124の古いGraph選択・scope不明は、SEIのDecision基礎を参照する権限でもSourceBridgeの正本IDでもない。TEI #2391のUI locatorが一致しても、業務Actionの意味受理やProvider effectを保証しない。

## 4. ハーネスに渡せる最小の「証拠付き引渡し」

定義するのは**情報のチェックリスト**であり、今すぐ導入する共通JSON Schemaや第二の状態Storeではない。

| 引渡し時の問い | 最小の検査 |
| --- | --- |
| 何の仕事の続きか | 本人または組織が現在掲げる目的・許可された範囲が明示されているか |
| 何を確かめたか | Sourceの版・参照範囲・証拠種別（synthetic/observed/未取得）が区別されているか |
| 何が仮説/未決か | 候補、反証、未確認が「確定済み」に書き換わらないか |
| どれが過去の判断か | scope・basis・lineageが原記録へ戻れるか。表示用resumeだけなら不足を明記するか |
| 何が使用可能か | Capabilityの発見、現在のProvider実装・権限・認証・ユーザの許諾を分離したか |
| 何をまだ実行していないか | 受付、試行、独立結果受理、外部Outcomeが個別に示されているか |
| 何を渡してはならないか | Token、非公開資料、個人データ、非公開の対象存在情報、内部推論全文の不必要な転載がないか |
| 次に何を確認するか | 追加調査、確認者、拒否/停止、独立結果照会の操作が定まっているか |

**厳格な完全性を主張できる条件**：対象集合と調査scopeが明示され、宣言された依存・実際に解決した依存・観測した実行が照合されていること。未観測の外部Providerや非公開Actionを「図にないから存在しない」と主張しない。TEIの図表透明性・生成パイプライン構想、公開RegistryでのDeclared/Resolved/Observed証拠表示の議論は、この慎重な境界と整合する。ただしRegistry/Composition/Plugin継承の設計提案をTAIが採用済みと断定せず、新Resolverも作らない。

## 5. 認知Method、Plugin、実行権限は異なる

- **CSW**は異なる文化的・概念的な体系を交差させる**一般的な認知機構の研究候補**であり、固定したマルチエージェント数やTAIの必須第七製品ではない。生成・批評・媒介の役割は、人とAIいずれも担える。批評で仮説を改善できても、原資料の真正性、実装の適合、本人の意味受理、実行許可の証拠にはならない。
- **易経64卦**は製品の位置と潜在的な拡張領域を探索するための象徴・問いの情報空間であり、技術要求の適合や経験的真理の証明には用いない。象徴から得た案は、利用者課題・反証・検査へ接続して初めて開発候補になる。
- **TEIプラグインと公開Registry**はPlugin、Contract、Provider、Instanceや、発見・検証証拠・採用・現在の権限を区別する検討がある。公開されたAttestationや形式適合検査を、利用者環境への導入許可、実行資格、業務意味の採用へ昇格させない。TAIから第二のRegistry/Resolverを作らない。
- **TEI Studio**はAuthoring/Observation WorkbenchのConsumerであり、可視化やUI操作の成立はSource acceptance / realization readiness / Operation Authorityと別。Host原則廃止の提案とWails/Theia非必須を守り、Studio側のscope/freshness/selectionのP0をTAIで再実装しない。

## 6. 実証の優先順位：新しい汎用プロトコルより先に小さな負例

| 優先 | 既存の成果と次の具体差分 | 次に確認する失敗条件 | 主管 |
| --- | --- | --- | --- |
| P0 | [SW-01 S1初回receipt](../evaluations/records/SW-01-S1-harness-2026-10-31.json)を基準に、**別ハーネス**で同じread-only判断再開を試す。初回Aはモデルの推論で保留、Bはscopeとlineageで根拠付き拒否 | ハーネスの会話表示だけを根拠に同文言A→B→Aの旧受理を転用 | TAI #168、SEIのbasis参照 |
| P1 | 旧scopeとSource/Projectionの更新を別々に変える。参照元のOwner/版と呼出し数・出力を観測する | 同じview-node ID、同じdigestで別scopeを暗黙選択、未観測APIを「拒否できた」と表示 | TEI #1124/#1120/#2391（TAIはシナリオの比較のみ） |
| P1 | EKIの新しい合成Result Acceptance recordを使い、外部効果/Outcomeの未観測を残す | AcceptedResultをProvider receipt／注文成立／本人の望む成果と混同する | EKI/Provider、TAI #168 |
| P2 | 認知探索と批評を入れた条件と、通常ハーネス単体の条件を同じ資料で比較 | 批評後の有力候補を、受理/権限/実行成功に昇格 | CSW研究、SUI/SEI、TAI #127 |
| P2 | SCN-004（組織）・SCN-005/#167（個人）で役割と情報公開のscopeを変え、同じ引渡し観点を評価 | 個人の自己決定を組織の承認へ転送、休息/延期を失敗扱い、社会で単一承認者を創作 | TAI #165/#166/#167/#127 |
| P3 | 版付き構成と検証証拠の連鎖をTAIシリーズ配布案に対応づける | 検証済みプラグイン/製品を自動インストール可・公開可と主張 | TAI #74、TEI RegistryのOwner |

[ハーネス引渡しの反証ケース](../evaluations/harness-boundary-negative-cases.md)を、P0/P1の具体的な観測票とする。既存 #169のライフサイクル/ablation計画、#129の研究比較、#127の三規模受入を**置き換えない**。

## 7. 何をまだ主張できないか

- SW-01 S1は合成条件の初回1モデル/1ハーネス対照。Aレーンの追加2回（初回と合わせ計3回）の記録は[PR #176](https://github.com/hat47x/tai-pleroma/pull/176)で扱われ、**異なるハーネスでの再現ではない**。
- 2026-10-31の[EKI execution](../evaluations/records/EKI-execution-2026-10-31.json)と[Result Acceptance](../evaluations/records/EKI-acceptance-2026-10-31.json)は、限定的な固定コマンド実行・合成Verifierである。外部の業務成果、本番のsandboxと資源制限は未検証。
- TEI能力連鎖の[receipt](../evaluations/records/TEI-capability-chain-2026-10-31.json)は型宣言の整合性だけで、実行生成・Source意味受理ではない。
- P-06の個人・組織・社会の比較、SCN-004/005のRC、実利用者QoL/有用性、実物の原本・権限・外部作用は、この設計文書によって**実施済みにならない**。

この文書自体は**提案の責務整理**であり、採用済みCross-Product Contract、既存製品の受入、権限付与、発行済み検証証明ではない。
