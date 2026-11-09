# YI / TAI Harness Skill：Semantic ContextからのAction選択とUI非依存連携（2026-11-02）

状態：**設計提案・受入計画 / 未採用 / SK-M全件NOT RUN**。関連：[YI Skill構成計画](harness-skill-plugin-plan-2026-11-02.md)／[SK-01](../../evaluations/SK-01-harness-skills.md)。TEIのSemantic Action/Function Data Context/Patternの意味正本・実装・適合Oracleは**TEI**に置き、TAIは外部Harnessからの製品・能力選択と、Product境界を横断した誤った成功主張を検証する。本稿は新TEI Action API、TAI Runtime状態型、中央Capability Registry、UI制御Hostを採用するものではない。

## 1. 他チャットとの接続・新しい着眼点

[TEI #2507](https://github.com/hat47x/tei-platform/issues/2507)は、画面やX-TEAのFunction Type別にActionを固定せず、**受理済み意味対象／Function Data Context／Required Data Shape／Operationの関係から適用可能なAction候補を見つける**構想を具体化した。[TEI #2500](https://github.com/hat47x/tei-platform/issues/2500)は、Table/Chart/TreeなどのViewChangeを型付きOperation Intentの**候補**へ逆写像する条件を所有する。[TEI #2586](https://github.com/hat47x/tei-platform/issues/2586)は Query→Data Context→Claim→Pattern→操作候補を一つのHeadless試験で受け渡す統合Owner。[TEI #2622](https://github.com/hat47x/tei-platform/issues/2622)はSmartDBをRDB専用機能からData Operations/多Providerへ一般化する候補である。

TAI Skillが新たに解くべき問いは、**利用者の目的をもとに、現在の製品が提示したAction候補のうち何を外部Harnessへ案内できるか、どこからProduct側の意味/権限/結果に委ねるか**である。たとえば「受注明細L1を修正したい」という同じ意図を、CLI、Web Form、表の行、対話AIから起動しても、Actionの対象・粒度・版・適用条件はTEI側の同一契約から来る。Harness Skillは操作手順を選択し、TEIに代わって新たな業務Ruleを解釈・再実装しない。

## 2. 互換的な六つの分離（評価レンズ、正式共通Schemaではない）

| 段 | 主な問い | 責任を持つ場所 | 代表的な誤昇格 |
| --- | --- | --- | --- |
| **Purpose** | 何を達成したいか。どの意味Claim/対象/時点が必要か | 利用者、TAI/SEI | 利用者の希望を承認済み業務Ruleに読み替える |
| **Semantic subject/context** | Entity/Relation/Occurrence/Aggregate/Unit/Grain/Scope/Read-set/版を何と解決したか | TEI Data/Function Context・実Source | UI行番号、JOIN行、集計棒を編集対象Entity IDと見なす |
| **Applicability / offer** | Contract/必要Data shape・Roleに対して何が候補か、何が曖昧か | TEI Pattern/Operation Owner | Tool listingやUIボタン表示を実行許可と呼ぶ |
| **Presentation / invocation** | CLI/表/Form/Graph/外部Harnessでどう表示・渡すか | TEI/UI/各Harness adapter | UI rendererやAI文書にBusiness Ruleを複製する |
| **Authorization / execution** | 現在の主体・対象・epoch・Grant・Provider/Tx条件で実行してよいか | 実Host/Provider/EKI/各Product Owner | Skill文書、Tool annotation、enabledボタンをAuthorityにする |
| **Observation / effect** | 同一Task/Attemptに対しどのReceipt/Artifact/独立結果を観測したか | 実Provider/Control/Consumer | HTTP 200、Tool exit 0、Claim ACKを業務完了と呼ぶ |

**Skillが返す候補は原則read-onlyの説明**。実行・Commit・外部作用は、対象Product/Hostが持つ現時点の認可と結果契約へ進む。同じ対象に複数の表示/CLI/AI入口があっても、別Rendererで新たに業務意味を受理しない。必要な許可は各操作時点で再検証する。現行UI外部制御の正本は[TEI #2391](https://github.com/hat47x/tei-platform/issues/2391)であり、Headless-firstの後にテスト用入口・Production物理除去を検証する。

## 3. 型や種類ではなく「対象＋目的＋適用条件」でSkillを選ぶ

単純な「テーブル操作Skill」「画面保存Skill」などの固定分類に頼ると、同じData OperationがCUI/Graph/Formから使えず、SQL/GraphQL/REST等のProviderごとに業務意味が複製される。TAI側での提案は以下。

1. **Intentを確認**：例「L1の明細金額を見る」「L1の単価を変更したい」「全配送明細を削除する」「集計結果を修正する」。対象/Claimが曖昧なら候補と不確定を示し、暗黙に確定しない。
2. **見えているProduct能力を発見**：候補Capabilityの名前だけでなく、当該Harnessで読める実Tool/CLIの版、Product別開示条件、必要操作/実現条件を確認。発見できないことと、禁止・未実装・未確認を区別。
3. **Contextから候補の適合を確認**：Entity/Relation Edge/Path occurrence/Group、同一Context epoch、必要なData shape・Read-set completeness・単位・Query/Rule版。Sourceをまだ取得していない、または一部しか取得できない場合はその不足を保持。
4. **専門Product Skill／Toolへ委ねる**：対象がTEI Data/FunctionならTEI Product Skill・実CLI、SUI CardならSUI、SHO引用ならSHO/MMI、SEI InquiryならSEIを優先。複数が本当に必要な活動でのみTAI横断Skillが受渡しを調整する。HarnessにSkill同士の自動呼出し能力を仮定せず、必要なら実Toolへ直接接続する。
5. **OfferとAuthorityを分離**：意味的に適用可能なAction候補が存在しても、現時点で実行権限があるかは別検証。高機密Profileでは「そのActionが存在する」という発見自体が開示対象。
6. **実体と効果を再観測**：tSelect/tResolve/tInvoke/tCommit/tObserveを一語で「成功」にしない。同一Source/対象/版/実受領Artifact/Provider Receiptを必要なClaimに限って比較。新しいTAI独自の実行台帳は設けない。

### 同じ操作の異なるAffordance

合成明細`L1`を選び、`line.amount`を見るというRead-only意図をTableの1行、Formの選択中項目、CUIのID指定、AIのTool引数に投影できる。**操作意図の意味ID・Source/Context版・対象Entityは同じ**とみなす候補になる。一方、Chartの「合計200」を「合計220」に変更する意図は、2明細のどれを更新するか不定なら逆写像できない。GraphでEdgeを解除する意図も、Entity自体の削除とは異なる。

TEIが適用条件と型付きOperationを提供する場合に限って共通化できるのであり、TAIがそのCapabilityを新規発明するものではない。X-TEAのSmartDBなどの機能をPluginとして再利用する場合も、Data Provider/Host bindingと意味Contractは[TEI #2622](https://github.com/hat47x/tei-platform/issues/2622)/[#2390](https://github.com/hat47x/tei-platform/issues/2390)のOwnerへ戻す。通常のTEI組織Dataを一律に特別保護する方針ではない。機微属性・非公開構造・外部LLM送出については用途と実権限に応じて[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)の境界を利用する。

## 4. 故障モードの整理とSkillが返す結果の資格

**同じ入力を渡しても、操作が可能とは限らない**。Tool availability/semantic applicability/authorization/result-observationを並べた単一PASSの合成値は避け、必要な欄を別々に記録する。

| ケース | 原因 | Skillが言えること | Product/Hostに返すこと |
| --- | --- | --- | --- |
| L1単体参照 | 型付きEntity IDとread-only Contextが一致 | 参照操作の候補がある。実取得済みならそのRead結果のみ提示 | Source/current revision/可視範囲 |
| L1単体更新 | L1のTarget解決済みだがGrant未確認 | 意味上の更新候補を提示。実Commitの許可は未確認 | 操作時点の認可・Target/Rule版・Receipt |
| Chart集計の更新 | 集計は多対一で逆写像不定 | 更新候補が曖昧。選択対象を補完しない | 明示Target選択・変換意味の検証 |
| D2全件削除 | D2は1/3のみ取得 | 部分集合の存在は言えるが全件操作の母集団は未確認 | Complete read-set、現在Scope/権限 |
| JOINの6行 | D1が2 Entity、D2が3 Entity | JOIN出力件数は更新対象Entity数ではない | Query Grain・Identityの解釈 |
| GraphのEdge解除 | Edge/Path occurrenceとEntityは別 | 関係操作候補のみ | Relation Contract/Constraint |
| 旧selection epoch | 選択A後にBへ移動、旧A応答 | 現在選択を再照合するまで旧Offer失効候補 | TEI Context/Epochと現在Source |
| 低権限Tool一覧 | 一部能力・IDは非公開 | 許可された能力だけを説明 | 内部Policy評価、実OS/Server強制 |
| Providerが受領 | HTTP 202/queued/Claim ACK | 受付/試行/Claimの局所結果のみ | EKI同Attempt Body/AcceptedResult/外部Effect |

## 5. SK-M実証への還流

[SK-01評価票](../../evaluations/SK-01-harness-skills.md)にSK-M01〜M10の正負対を追加。**検証対象はTAI Skillが架空の能力や実行資格を足さないこと**であり、TEI自体のAction applicabilityをTAIで実装する試験ではない。

- **SK-M01/M02**：同じ`L1`をTable/CUI/Formで扱う。read-onlyとupdate候補は同じ対象/意味版へ戻り、updateの実許可を飛ばさない。
- **SK-M03/M04**：集計Chartの逆写像不定と、D2 1/3の全件操作に必要なRead-set不足を分ける。
- **SK-M05/M06**：Graph Edge解除はEntity削除と異なる。JOIN 6行を6つのEntityと数えない。
- **SK-M07/M08**：古いselection epoch/版でのAction Offerを再利用せず、低権限ではTool名・条件・理由も開示対象。
- **SK-M09/M10**：Provider受領をEffect完了へ昇格しない。対象がDocument/Simulation/Event/Graph/StreamならCRUDパターンを万能視せず、当該専門Product契約に戻す。

比較条件は既存H2/H3、H4/H5（同じ公開Source、同じ契約説明、同じTool実可用性、別Oracle）。期待値は本番Agentの入力に含めず評価側で独立管理する。**全ケースNOT RUN**。将来実行した場合は`Skillが呼んだProduct Tool`・`Productが返した適合判断`・`Hostが実行した操作`・`観測されたEffect`を別々のEvidenceとして保存し、SK-J/LのSource版・Role・実送達評価を併用する。

## 6. 開発と配布の次段

TAI側は**固定形のAction Skill一覧ではなく、用途・Context・Product能力に基づく選択指針を強める**。実体は各製品のSkill／既存CLI/API/MCPとし、各製品の機能増加に伴って自然に組み合わせ可能性が拡がるようにする。

1. 既存[TEI #2507](https://github.com/hat47x/tei-platform/issues/2507)のSA-01〜07と[TEI #2586](https://github.com/hat47x/tei-platform/issues/2586)のHJ-01〜07を**Product Ownerの適合基準**として参照。新Core/新Toolの採用はTEI判断。
2. TAI SK-G0/G1とTEI #2605のread-only実CLIを先行し、Product単独Skillの効果を測る。SK-Mはこの後段の独立評価Laneとして並列追加してよい。
3. 機能を複数Productで使うケースでは、同じClaim/Context/Tool版・開示条件でTAIあり/なしを比較。単一Productで足りる時はTAIなしを合格候補として保持。
4. 簡潔なSkill入口から実Tool・必要な詳細に段階的に辿る。TEI DSLは標準データ構造とRoleへ連動する構想（[TEI #2619](https://github.com/hat47x/tei-platform/issues/2619)〜[#2622](https://github.com/hat47x/tei-platform/issues/2622)）であり、独立した大量のFunction Type固有Skillを必須化しない。
5. 実SourceとProduction Artifactの一致、GUI用追加入口の物理除去、権限、同Attemptの成果物Body/EffectはそれぞれのProduct/Hostで別途実証する。TAIは局所結果の適用範囲を報告する。

**Owner未決**：TAI Skillが動的Capability発見の何を外部へ公開してよいか、Productが意味的なAction候補情報をどの既存APIで取得可能とするか、無権限時の公開診断、AdapterにSkillをどこまで同梱するか。これらを設計の固定Schemaとして宣言しない。
