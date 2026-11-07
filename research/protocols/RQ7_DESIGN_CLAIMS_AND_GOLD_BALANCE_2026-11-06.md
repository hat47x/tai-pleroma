# RQ7 研究追補：設計意図・観測事実・保証主張の判別とGold偏りの是正方針

- 状態: **比較実験の事前改善案／新しい人間・AI評価はNOT RUN**（2026-11-06、JST）
- 既存研究: [RQ7 有界Graph完全性](RQ7_BOUNDED_GRAPH_OBSERVABILITY_2026-11-06.md)、[公開prepilot採点](RQ7_PILOT_STIMULUS_AND_SCORING_2026-11-06.md)、[公開Gold](../fixtures/RQ7_BOUNDED_COMPLETENESS_GOLD.public.json)
- 作業時点TAI main: `eaac8414f3933deabc8c0644c5745f6b74b86628`、研究Draft [#473](https://github.com/hat47x/tai-pleroma/pull/473)の旧head `02ef0b4d0fd52405fc0c27b5f667c1e147b39a17`
- Product正本/担当: [TEI #2495](https://github.com/hat47x/tei-platform/issues/2495) メタ概念軸、[#1126](https://github.com/hat47x/tei-platform/issues/1126) 業務Key/FD/ER、[#2620](https://github.com/hat47x/tei-platform/issues/2620) Role/自己記述、[#267](https://github.com/hat47x/tei-platform/issues/267) Source/意味Acceptance、[#2514](https://github.com/hat47x/tei-platform/issues/2514) 独立Oracle、[既存SQL/DDL設計Draft #2778](https://github.com/hat47x/tei-platform/pull/2778)
- **非目標**: TEIの正式な属性型、Enum実装、強属性定義、設計アラートエンジン、Source Reader、第二の受理正本をTAI研究側で作らない。

## 1. 観測された研究上の問題：宣言のみのGoldが偏っている

既存[公開Gold](../fixtures/RQ7_BOUNDED_COMPLETENESS_GOLD.public.json)の値をGitHub blobから再集計した結果（**研究被験者の回答結果ではない**）：

| Arm | Supported | Refuted | Undetermined | 合計 |
| --- | ---: | ---: | ---: | ---: |
| V0（宣言Text） | 2 | **0** | 8 | 10 |
| V1（宣言Graph） | 2 | **0** | 8 | 10 |
| V2（Text＋合成証拠） | 4 | 3 | 3 | 10 |
| V3（Graph＋同じ証拠） | 4 | 3 | 3 | 10 |

V0/V1で`undetermined`を固定出力するだけの被験者でも8/10件のVerdictが合う。従って「V0とV1の正答率が高い／差がない」は**図の理解力・校正能力の証拠として弱い**。V2/V3ではGold分布が異なるため、単純な正答数の比較から「Graphだけの効果」と「証拠の効果」を切り分けて因果解釈しない。

**既存の公開10ケースとGoldは後から変更しない**。今回の分布と欠陥候補を、公開prepilotの診断として記録し、研究論文の母集団・効果の根拠に使わない。次の未公開holdoutは**別版・別Case群・独立採点**を必要とする。

## 2. 「意図→Source→解釈→実実行→受理」は五つの主張

RQ7は処理Graphの完全性だけでなく、TEIのデータ・業務定義と旧ソースからの意味抽出にも共通する「何をもって主張できるか」を比較する。ただしTEIのCanonical Schemeを新設するものではない。

| 評価面 | 記録する対象 | この面だけから自動導出しないこと |
| --- | --- | --- |
| Intended | 設計者・Ownerが**意図した**制約、対象scope、有効期間と例外 | Source実装済み、実行観測済み |
| Source-static | 固定Source/DDL/コード/設計表から機械的に読み取った**構文事実** | 業務上の意味、現在のDB全データ、外部Hostの許可 |
| Inferred | 読取れたSourceからの業務意味・分類・FD・閉値域の**推定候補** | Accepted Meaningや全件完全性 |
| Observed | 固定Run/DB/Provider/Consumerの**実観測結果**、適用できる窓・Source版 | 別Run・別scopeへの転用、望ましい仕様 |
| Accepted | 意味・対象・時点・Authorityのある主体による**現行受理** | 実Effectや別Providerへの万能許可 |

例として、コードに`switch`の列挙があっても、それだけで業務値域がMECE（相互排他かつ網羅的）だとは言えない。DBに`CHECK (status IN ('A','B'))`があっても、PostgreSQLでは`CHECK`の評価が`UNKNOWN`なら制約違反にならないため、`NULL`許容性は`NOT NULL`などと独立に点検する必要がある。[PostgreSQL 16公式Constraints](https://www.postgresql.org/docs/16/ddl-constraints.html)

「値の集合を二つに分けた」「状態の移行が正しい」「将来値が増えない」「全Recordが同じ制約を遵守している」「操作が許可される」は、すべて別Claim。MECEと呼ぶ前に**分類する全体集合、未知／NULL／未取得、版と時間、複数facet、例外の許容**を指定する。

「強属性」はユーザーが研究候補として挙げた名称だが、渡辺氏による**一次定義を今回確定できていない**。他の属性制約と同一視して正式な機械推論を作らず、原典の用語・範囲・適用事例を確認してからTEI側Ownerへ候補を渡す。

## 3. 手動・自動・推定・警告を分ける最小判定表

| 特性・問い | 設計者/Ownerの入力 | 自動で扱える範囲 | 未確認時の出力とAlert |
| --- | --- | --- | --- |
| 値域が閉じているか（Enum的） | 閉世界の意図、分類対象、版、許容例外、未知をどう扱うか | enum/union/SQL制約などの**構文上の集合・制約**を抽出 | `inferred candidate`。意図が未登録なら「閉値域確定」としない |
| 相互排他・網羅性 | 何を全体集合とするか、重複所属可否、観測窓 | 選ばれた独立母集団とOracleに対する重複・未分類・未取得を検査 | Source集合が不完全なら`unknown`、全世界のMECEを断定しない |
| 必須値/NULL/欠落 | Requiredか、NULLと「未取得」をどう区別するか | `NOT NULL`・`CHECK`・実DB制約・Observationを面ごとに検査 | DB制約だけを業務上の必須意味としない |
| Key・FD・業務ID | Business identity、粒度、期間、reissueの扱い | 物理PK/UNIQUE・候補FD・独立反例を照合 | DBキーだけから業務IDを自動受理しない |
| Relationの帰属・Cardinality | Relation scope、各端点scope、role、期間 | 固定Readerの範囲でqualified keyと実Graph/Tableを比較 | 端点scopeからRelationの所属を導出せず`unknown` |
| Pipeline閉包/依存 | 必須Step、合法skip、非公開要素と対象Boundaries | declared/required/selected/consumed/observedを**同Attempt**で照合 | 未観測≠不在、Source Graph≠実行Graph |
| Effect/Authority | どの操作とPrincipalがどの時点に許可されるか | Providerの現在Policy/独立Effect Observerを観測 | Constraint PASSやHuman Meaning AcceptanceをPermitへ昇格しない |

**アラートの最小区別（研究用。製品通知Policyではない）**：

1. `confirmed-mismatch`: 同一subject/scope/revisionに限定した**独立観測事実**と受理済み意図が矛盾するとき、根拠を添える。ただし修正内容・権限の採否はOwner。
2. `requires-check`: 意図が未入力、Source不完全、推定だけ、Provider/Consumer未観測、対象版が不一致のとき。矛盾の確証がないのに「実装バグ」と断定しない。
3. `compatible-within-scope`: 同じ対象・根拠と閉包を確認できる範囲で矛盾を検出できないとき。全体保証や「必ず正しい」の表現を避ける。
4. `withheld`: 該当Consumerへ根拠/存在が非開示の場合。`withheld`を低権限の公開面に特定の内部要素の存在を漏らす方式で使用しない。公開へのProjectionは現行Policyに従う。

**重要**: `supported/refuted/undetermined`は証拠に関する判定で、`withheld`は開示PolicyによるProjection状態であり、同一Enumの真理値4択に混在させない。観測上のUnknownとビジネス上の未決も区別する。

## 4. 未使用の後続Case群（既存Goldの変更を禁止）

次は**候補のみ・未生成・未実行**。宣言だけで`refuted`を正しく導ける課題を追加し、全回答を`undetermined`にする策略を反証する。全てのCaseで論理的な問と提供情報を先に独立採点する。

| ケース候補 | 対象 | V0/V1で確認したい結論 | 実証のために不足すること |
| --- | --- | --- | --- |
| D-R01 | 宣言Graphに`Source→Package`経路が無いのに「宣言内にある」と問う | `refuted`（対象Graphのみに関する問い） | 同じ対象・版のGraphの正しい固定 |
| D-R02 | 必須Stepと合法skipが同一branchで重複している | `refuted` または invalid stimulus（判定種別を事前確定） | 未受理不整合の入力をどう質問するかのOracle |
| D-P01 | 複数roleのRelationで、宣言された全roleの対応が明示されている | `supported`（宣言範囲に限る） | n項Relationの読取と独立Expected |
| D-U01 | 値域がEnum風だが`NULL`、未知値、Source版、実DB Recordの読取範囲が不明 | `undetermined`（業務MECE） | 受理済みClosed-world契約・実Reader |
| I-N01 | 設計上`status`必須、実DDLで`CHECK IN`のみ、`NOT NULL`無し | 構文事実とIntent差の**確認候補** | 実PG/既存DB version・Nullable確定・Owner意図 |
| I-N02 | コード`switch`に分岐が少ないが業務値域は複数Versionで増減 | `undetermined`（値域全件） | accepted Meaning・Version/Scope |

新しいCaseは、TEI #2495/#1126/#2514/#2620/#2778のOwnerが与える対応の前に**TAIで業務意味を独立創作・受理しない**。実証時には語彙に適合するか、価値・人/AI負担が減るかを測り、既存TEI #2018の経済性計測と混同しない。

## 5. 次回実験における分析計画

- `prepilot_v0`（公開10件）は現状のまま読み出し専用で保存。今回の再集計は**元データの記述統計**であり、AI/人間の成績ではない。
- 新しい`prepilot_v1`は、宣言だけで`supported/refuted/undetermined`がすべて出現するようにした**別の公開開発用**組にする。均等配分を必須とするのでなく、各層で誤回答を検出できることを要件化。
- 独立holdoutは各条件・Domain・判定種別での適格な件数とGold独立性を前固定。公開Goldや修正済みPrompt/モデルがholdoutを見た場合は被験者に再利用しない。
- 素朴な正答率だけでなく、`always-unknown baseline`、`always-support baseline`、`declaration-only-to-execution promotion`の三つに対する**層別誤り**を集計する。Graphの値とEvidenceの質の両方が問われる場合、単純な総正答率ではなく各要因・交互作用を別に報告。
- `alert precision / recall`は独立したIntent・Source/Actual・OwnerのGoldに対してのみ計算する。警告数の増加や不確定を一律に赤にする手法を改善とは呼ばない。
- Graph UI実描画、AIへの文字列Mermaid vs 画像、Readerの独立閉包、公開用Disclosureの非干渉、正解・負例の外部評価者、人的/計算費用はそれぞれ**別Gate**。既存RQ7の14テストPASSは公開刺激ツール自体の正常動作に限る。

## 6. 反映するOwnerと停止条件

- [TEI #2495](https://github.com/hat47x/tei-platform/issues/2495): データ構造を分類する問いと複数facetの意味。Enum等に関する専用Core enumを追加した提案ではない。
- [TEI #1126](https://github.com/hat47x/tei-platform/issues/1126): FD/Key/Relationと業務意味。静的DDLの形＝Ownerが受理した業務Keyではない。
- [TEI #2620](https://github.com/hat47x/tei-platform/issues/2620) / [#267](https://github.com/hat47x/tei-platform/issues/267): Role/Sourceの読取、Owner Meaning Acceptance。実装を研究側に移管しない。
- [TEI #2514](https://github.com/hat47x/tei-platform/issues/2514): ケースの独立Oracle・既知Mutant・適用範囲。公開Goldをsealed holdoutとしない。
- [TEI #2831](https://github.com/hat47x/tei-platform/issues/2831) / [#2542](https://github.com/hat47x/tei-platform/issues/2542): Build/ETLの有界な実観測。Graph UI成功を実行資格へ転用しない。
- [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) / [TAI #443 Draft](https://github.com/hat47x/tai-pleroma/pull/443): Harness、生成候補の未提示を区別。モデル内部推論の強制公開はしない。

必要なSource/Meaning/実Recordが揃わなければ`unsupported/unknown`で停止し、強引に仕様へ昇格させない。研究側に新たな汎用Constraint Engine、第二の正本、常駐Host、Plugin Registry、実行Authorityを導入しない。**本追補は研究設計への反映で、TEIの製品実装・alert UI・独立モデル/Human実験・実DBを実行したことではない。**


## 7. 2026-11-07：Gold分布を変えた公開prepilot v1

研究で検出したGold偏りの**対応を実際の別データセットとして保存**した。従来v0の10ケース・Goldには変更を加えない。

- [公開刺激12ケース（v1）](../fixtures/RQ7_BALANCED_PUBLIC_PREPILOT_V1.synthetic.json)
- [公開Gold（v1）](../fixtures/RQ7_BALANCED_PUBLIC_PREPILOT_V1_GOLD.public.json)
- [選択式Renderer / チェッカー](../tools/rq7_pilot.py) で `--dataset v0` と `--dataset v1` を切り替えられる。旧CLIの既定はv0。
- [専用回帰テスト](../tools/test_rq7_balanced_v1.py) では新12ケース×4表示の48通り、宣言EdgeとPath、情報量ごとの同一Gold、旧版非変更、Gold漏出禁止を点検する。
- [研究用の限定CI](../../.github/workflows/rq7-public-prepilot.yml) はTAI製品の正式GateやTEIのSource Reader/Targetを検査しない。

| 評価集合 | V0/V1 Supported / Refuted / Undetermined | V2/V3 Supported / Refuted / Undetermined |
| --- | --- | --- |
| 公開v0（10ケース） | 2 / 0 / 8 | 4 / 3 / 3 |
| **公開v1（12ケース）** | **4 / 4 / 4** | **5 / 5 / 2** |

v1ではBuildとFile-Relayの両Domainに、**宣言内の直接Edge・推移的な有向Pathについて支持／反証できる質問**をそれぞれ4件設定し、実行証拠を要する2件・観測不足の2件を加えた。Graph/テキスト表示で同じ事実を与え、`direct edge`と`directed path`の取り違えを反例化する。

### 実験上の限界と次に固定するもの

**Gold分布が均衡したこと ≠ 認知課題の難度・出題順・言語負担・概念の独立性が均衡したこと**。今回の宣言問いには互いに似た構造が含まれ、旧v0より簡単に解ける可能性がある。v0・v1を混在させた生の正答率を介入効果や製品効果としない。v1の公開Goldは繰り返し閲覧できるため、独立holdoutには使わない。

本番の比較では、同一EvidenceのGraph/テキストを別の評価者が監査し、出題順・提示形式・学習や同じNode名への馴化を記録する。保持すべき独立変数は`presentation medium`（人は**実描画画像**、AIは受け取った形式を明記）と`additional scoped evidence`の二つ。正しい保留と、何を次に確認すべきかの説明を分けて採点する。

### 他チャットのTEI設計・実装進展との接続

[TEI #3248](https://github.com/hat47x/tei-platform/pull/3248)は税・通貨・採番・休日に関連する17のAttribute Role名を検証語彙として受理する変更としてmainに統合された（確認したTEI main `680646b8629ce7af5b9bb0ba7db3529151b63a4c`）。**Role名の辞書受理は、Role↔型適合・業務値域のMECE・Owner Meaning Acceptance・実データの適合を保証しない**。この差を次段のIntended/Source/Observed候補へ引き渡す。

[TEI複合図表Reference Draft #2881](https://github.com/hat47x/tei-platform/pull/2881)は、合成Graph/Tableに加え実`tei trace`から別言語Node Consumerへのread-only直接Edge候補接続を提示し、Caller指定scopeとSource宣言scopeを区別する証拠を追加した。ただし**直接Edge・Caller scopeは完全Relation／有界不存在の製品資格でない**。RQ7の実Source比較はこの既存経路を候補として利用し、第二Reader/Resolverを開発しない。

[TEI研究計画 PR #2966](https://github.com/hat47x/tei-platform/pull/2966)と[ETL/MFT設計 PR #2827](https://github.com/hat47x/tei-platform/pull/2827)は2026-11-07に統合済み。TAI研究PRはその設計正本を複製せず、被験者の判定・根拠再構成・費用の研究票を保持する。

**実験上の状態**: v1は公開合成ケースと研究ツールの開発。TEI実Role意味受理、独立holdout、人間・AIのV0〜V3成績、実Graph UI、実Provider Authority、実配送／自己ビルドG4の認知効果は全て**NOT RUN / NOT PROVEN**。

## 8. 2026-11-08：Roleの静的型資格の進展と実Meaning

[TEI PR #3308](https://github.com/hat47x/tei-platform/pull/3308)はmainへ統合され、標準業務のAttribute Roleが必要とする`date/decimal/integer`プリミティブと宣言Typeの適合性を、AliasのUnderlyingを辿って検査できる。[#3318](https://github.com/hat47x/tei-platform/pull/3318)も統合され、例Workspace上の税・為替・採番・休日の役割付きDataから結合までの限定試験が成立した。**「Role名だけ受理でき型検査は未実装」という旧時点の記述を現行実装状態として使わない**。

一方、型適合がPASSでも、金額・税率の丸め・適用期間、データの実行時Source真正性、実DB/外部Provider受入、Ownerが意図した業務意味、実Consumerの作用は**別のClaim**。強属性の原典に基づく定義と正式実装は引き続き未確認。研究のIntended/Source-static/Inferred/Observed/Acceptedを分ける理由は型チェックの進展後にも残る。

[TEI #3321実CLI evidence資格](RQ7_REAL_CLI_EVIDENCE_TRANSFER_2026-11-08.md)にも同じ区分が必要であり、`World/Manifest fingerprint`からSource/Role全体の意味や完全なRelationを自動推論しない。
