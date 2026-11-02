# TAI Activity継続の選択的再資格化：意味・証拠・権限・成果物の条件付き再利用

2026-11-02。**設計提案／公開合成Referenceのみ。Owner受理と実Product/Harness統合はNOT RUN。**

Owner作業票：[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)。

関連：[TAI全体計画](harness-skill-plugin-plan-2026-11-02.md)、[SK-01](../../evaluations/SK-01-harness-skills.md)、[Evidence/開示](harness-skill-read-witness-rule-disclosure-2026-11-02.md)、[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)、[TEI #2516](https://github.com/hat47x/tei-platform/issues/2516)、[SEI #767](https://github.com/hat47x/sei-cognition/issues/767)、[EKI #465](https://github.com/hat47x/eki-fabric/issues/465)、[SHO #10](https://github.com/hat47x/sho-composer/issues/10)。

## 1. 今回の追加差分：履歴の真実と現在の利用資格は異なる

TAIのActivity継続を、前のAgentの「成功」文章を再利用する処理から、**当該用途について、必要なEvidenceと現在の適格性を見直す処理**へ具体化する。

- **Historical Observation**：あるSource/Meaning/Tool/Host/Attempt/時点で実際に観測された結果。後に状態が変わっても当時の記録は保持される。
- **Current Qualification**：今、別の目的・Consumer・時点・Hostでその結果を用いてよいか。依存根拠、Scope/Grain/完全性、Role/Rule、Source/epoch、権限・開示を照合する。
- **Requalification Candidate**：必要な差分だけを再確認する提案。Ownerの新たな意味受理、実Provider Read、実Artifact到達、現在Grant/TrustをSkillの決定だけで確定しない。
- **Historical resultとCurrent Effectの別**：過去のCommit/Receiptがあっても、現時点の再実行許可はなく、同一AttemptのBody再送と別Attemptの業務再実行は分ける。

この比較票で使うIDや状態名は、共通の新Canonical Claim Store/State Machineを採用する仕様ではない。各Productがすでに持つSource/Role/Claim/Request/Artifact/Acceptanceの実参照を利用する。

## 2. 複数Productの実物に必要な依存線

一つの依頼が「論文索引→TEIの型付き定義とTarget→SEI評価→EKI委任→SHOの文書/納品→TAI活動継続」のようにつながる場合、依存先を**用途に必要な範囲だけ**明示する。

| 依存の種類 | Product Owner | 影響確認の例 |
| --- | --- | --- |
| 原典の改訂・出現箇所 | SHO #7/#8、MMI C-01/T2 | URLの題名変更と原論文本文改版、Markdownの行移動、Source locator再解決は別 |
| TEI意味とTarget | TEI #2620/#2516/#2604 | Role/Operator版、丸め/NULL/Source correspondence、生成した版と実Consumerが読んだ版 |
| FunctionのRead/Rule | TEI #2506/#2624/#2628 | Providerだけ変更した場合とRule意味が変更した場合を区別し、実Read witnessなしをunknown |
| 認識の問い相対十分性 | SEI #767、TEI #2516 | 局所観測PASSと複数Readの共通epoch/Source、未知世界、開示可能な結論の違い |
| 委任の結果・出力の移送 | EKI #407/#465/#468 | Task/AttemptのClaim ACK、同一AttemptのBody bytes/digest/受領、Consumer実読取り |
| 現在のGrant/Trust/Disclosure | Product/OS/Host、TAI #232、EKI #466/#467 | 過去にSkillがロードされたことと、現在の危険Actionの実行資格は別 |
| Activity Resumeと横断選択 | TAI #168/#74 | 失効したProductの再調査だけを選び、無関係なProductの探索・書式化は継続 |

**影響範囲は証拠付きの依存Edgeから求める。** Source/Meaning/時点/Consumerの依存解決が曖昧なら、影響を受けないと断言せず、対象となり得る範囲をunknownに残す。Field名だけ・同名URLだけ・画面構文だけから同一性を決めない。

## 3. 段階的な再利用と再実行の判断

| 差分／観測 | 履歴として保持するもの | 現在の確認・操作 |
| --- | --- | --- |
| SHOの表示用リンク題名だけ変更、TEI契約へ依存せず | TEI計算・EKI過去Attempt等の当時の結果 | SHO索引とTAI説明だけ差分反映。モデル/Targetの一括再実行は不要 |
| TEI Source/受理済みRole版変更 | 旧版の生成物・独立Oracle・過去利用記録 | 依存するTEI意味/生成/SHO説明の現在性を再検査。無関係なSEI/EKI結果は保存 |
| Query Provider/Alias変更 | 旧Sourceでの業務意味・旧Query/Trace | 実Read/完全性/Current Bindingを再確認。Model全体の意味変更とは限らない |
| SEI Method版変更 | 旧問い・旧Methodの限定結論 | Q相対の適格性、Source/epoch/公開範囲を再評価。TEI Targetを必ず再生成するとは限らない |
| EKI Claim ACK済み、Body未受領 | 同一Attemptの申告とACK | 同一AttemptのBody送達状況を確認。新Attemptの業務操作を自動再実行しない |
| Body/digest一致、SHOが未読 | EKI受信側の照合結果 | 実際のSHO受領/読取版・出典再解決・Render/Save/Deliverを別に確認 |
| 現在Grant/Trustが失効・読取障害 | 過去Grant下で生じた履歴と独立Source | 危険Effectのみ現在Hostで拒否し、許されたread-only調査/説明を継続 |
| Rule結果の外部公開不可 | 製品内部での正当なRule観測（外部へは渡さない） | 許可されたProjectionだけ提示。Tool選択/候補/診断にも秘密差分を出さない |

再検証の**最小単位**は、同じ「完全成功」フラグではなく、利用目的・Claim・証拠依存の組み合わせで決める。例えばD1の単件存在証言は再利用可能でも、D2全件集計は部分取得のまま再利用不可という場合がある。

## 4. Activityの中断・Harness交換時の引継ぎ票

共通Provider/Authority/DBを新設せずに受け渡すため、**既存参照を列挙する一時的な作業票**の候補を用意する。名前・項目・JSONは正式な契約案ではなく、実製品から返せた範囲を表にするだけ。

| 欄 | 記録する参照・条件 |
| --- | --- |
| Request/Purpose | 利用者の目的、対象Claimと必要な時点/粒度 |
| Accepted Meaning | Productの意味ID/Role/Operator/Source版とOwner受理の有無 |
| Evidence/Unknown | Source/Oracle、実Tool、観測範囲/実Result、未実施/不足条件 |
| Product delivery | EKI Task/Attempt、Claim ACK、Body digest/到達、SHO Source read/納品版等 |
| Current qualification | 実利用前に照合すべきGrant、Host、Disclosure/Tool Profile、Trust |
| Resumption choice | `reuse with same scope`／`requalify named dependency`／`withhold`／`unsupported`／`await receipt` |

活動票は秘密の生Data、非公開Tool/Skill名、認証情報を外部Harnessへ単純転記するものではない。正当な範囲だけをSource Ownerが投影し、**参照だけでは実データを読み取った証拠にならない**。実Egress経路はTAI #232等で確認する。

## 5. 検証の増分価値を測定する

同じ公開合成Activityの変更イベントと独立した期待結果に対し、以下を対照する。

- **J0 全面再検証**：すべてのProduct・Target・Skill/Hostをやり直す基準。
- **J1 Selective Requalification**：Source/依存Edgeの変化と対象Claimから必要な観測だけを選ぶ。必要Edge不明なら追加検査へ戻す。
- **J2 直前のAgentの成功をそのまま採用**：危険な最小作業量の負例として、偽成功・古いSource・未送達を検出する。

測定は変更検知の**漏れ**、無関係再検証の**過剰**、Root Source/実Process/実Consumed版一致、ClaimとOwner受理、外部Tool回数/トークン、Human review/再開時間、開示と作用の境界。J1がJ0より検査数を減らしても不正な結果が増えるなら生産性向上と呼ばない。Sourceの依存が未記録な場合、J1の節約を保証できない。

## 6. SK-C01〜C15公開合成Reference

[Fixture](../../evaluations/fixtures/SK-C-continuation-requalification.synthetic.json)は**架空の明示Dependency Graph**と委任・公開に関する限定状態で構成する。
[check-sk-c-fixture.cjs](../../evaluations/tools/check-sk-c-fixture.cjs)は依存閉包と固定された正負判定を計算するだけの自己整合チェッカー。[限定実行記録](../../evaluations/records/SK-C-public-fixture-selfcheck-2026-11-02.json)を同じGitHubブランチに保存。

- **SK-C01〜06**：SHO索引題名、TEI Source、Provider Binding、SEI Method、EKI Attempt、現在Grantの変更による依存閉包と無関係作業の保存。
- **SK-C07〜15**：現在Grant欠如、Claim ACKだけ、Body未到達/検証失敗、Consumer未読、Source/epoch混合、結果非開示、Scope不完全、Owner受理未確認を、総合「完了」と分離。
- **Mutation負例4件**：必要Edgeの除去、受理の偽装、Grantの差替え、無関係Edgeの追加を検出できるか。

2026-11-02、GitHubから取得した保存済みJS（shebangのみ除外）・Fixtureを、V8＋`fs`/pathの限定Shimで実行し、**公開Expectedとの整合15/15、mutation検出4/4**を確認。**Node.js実ランタイム、TEI/SEI/SHO/EKI/TAI実Product、OS/Network/Harness、実Dependency Graph抽出、実Owner受理・独立sealed OracleはNOT RUN**。GraphとOutcomeは公開の架空条件なので、真の最小再検査範囲や製品保証は未成立。

## 7. 製品別の実施順序

- **P0**：TAI SK-Cの限定構造と既存SK-J/TB/Fとの重複・不足をレビュー。Evidence/変化の所有者を明示した公開Sourceを用意する。
- **P1**：実Productの既存read-only CLI/Methodから一つのSource→Evidence→Consumer参照を観測。参照先不明を保存して再開可能性を測る。
- **P2**：TEI/SEIが現在のScope/Source/Method/RuleでClaimを再資格化し、EKIの同一Attempt Bodyを取得、SHOが実読取版を確認する小さな連携。実操作のある範囲だけを計測。
- **P3**：新Harnessと旧Harnessで同一Taskを比較し、旧成功の誤流用を防ぎ、既存Product/Host Permissionを保持して再開する。
- **P4**：J0/J1/J2の再検査漏れ・費用・Reviewコスト・誤成功を比較し、TEI #2018／TAI #168/#74の製品価値に反映する。

製品単独のPoCやRead-only調査は、全製品を待たずに並行して進められる。EKI Result BodyやSHO実保存、TEI実Providerが欠ける連携はその段階のみ未実施と記録する。CSW自由探索の途中に採否Gateを挿入せず、受理・実作用の段階で既存の製品責務へ戻す。

## 8. 同じResultでも再資格化が必要な場合：依存の閉包と受渡し資格を二軸で照合（QH-01〜18）

**追加の問題**：従来のSK-Cは、入力した合成Dependency Graphが十分なEdgeを持つことを前提とした。現実には、返却列に現れないWHERE/EXISTS/Sort/Validation入力、複数Persistence Mappingの実Route、Consumerが要求するArtifact Member集合などが**実依存から漏れる**。値・digestや同じOperation IDが不変でも、依存根拠が変われば旧「利用可能」を再適用できるとは限らない。

実験の出所：[TEI Query QX-27 Draft #2634](https://github.com/hat47x/tei-platform/pull/2634)（Go DerivedIR OutputField Inputsと非出力Predicate等の区別）、[TEI Operation Draft #2632](https://github.com/hat47x/tei-platform/pull/2632)（同一Operation IDで多Mapping・Alias順変更・Basis/Inputsが変動する特性記述）、[TEI ArtifactSet Draft #2633](https://github.com/hat47x/tei-platform/pull/2633)／[設計 #2630](https://github.com/hat47x/tei-platform/pull/2630)（内部Manifest/CheckSet整合とConsumer相対Required集合・実member bytesを分離）、[MMI Draft #755](https://github.com/hat47x/markdown-matrix-injector/pull/755)（HTML comment・inline-codeの偽参照を実CIで拒否）、[SHO #6](https://github.com/hat47x/sho-composer/issues/6)（複数Claimの合成の独立性）、[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)。

**原則**：現在の一つのClaim/Activityで「以前の根拠が影響を受けるか」と「現在のConsumerに渡してよいか」を**独立に判定する**。`reusable-dependency-evidence`は、対象Claimに必要な依存が本当に列挙済みであって、変更がその閉包外にあると確認できる場合の**候補**。その上でRead Cohort／実Read Trace／Consumer Required Member／実Artifact byte／同Attempt Body／Egress許可／Effect Grant／Owner受理のうち必要な資格を個別に満たす。

| 比較軸 | 不変の証拠が許す主張 | 追加で要求する独立証拠 |
| --- | --- | --- |
| Dependency/Meaning | Source上のResult/digest・見かけのRule値が不変 | 非出力Predicate/Filter/Negative dependency、Rule/Role/Operator、Mapping/Provider Routeの**必要な依存の閉包** |
| Data/Time | 同じ画面値、同名Snapshot token | 必要なScope/Field Presence/Read Cohortの実保証。要求Readと実Provider Witnessの区別 |
| Artifact/Receiver | ProducerのManifest `Complete`、Claim ACK、同じSHA | ConsumerのExpectedMember集合、実読取member bytes、同じAttemptのBody到達 |
| Actor/Authority | 以前のSkill説明・Tool成功・Grant | 現時点の許可／Recipient／実送出・実Effect／業務Owner採用。権限不明ならその作用を保留 |

### test-only実装と観測（製品コード・共通Schemaではない）

公開の[合成Nodeチェッカー `check-sk-qh-qualification.cjs`](../../evaluations/tools/check-sk-qh-qualification.cjs)へQH-01〜18を保存。**保存済みと同一Git blobのNode v22.16.0、`node /mnt/data/check_sk_qh_qualification.cjs`で18/18の独立assertionsがPASS**（2026-11-02、Python 3.13.5で計数とSHA-256を確認）。実行ファイル6,054 bytes／SHA-256 `3a9ee6bfe98c950166092a28c0f75564044254de4709b4d937c0510a0e92b317`／git blob `6c078c980c1d739abc0dccdac8b27e35d536b1d3`、GitHub保存Blobと一致。RepoのNode製品CI/Harnessに組み込んだことは意味しない。単体再実行方法は`node evaluations/tools/check-sk-qh-qualification.cjs`。

- **QH-01/02**：既知の依存閉包外でSHOリンク題名だけ変わった場合、TEIの当該意味Evidence候補を保持できる。
- **QH-03〜07**：出力Digestが同じでも、非出力Predicate／隠れたValidation Rule／Provider Route／Artifact Required集合／Role/Operator版が変わればそのClaimの再資格化候補。
- **QH-08〜10**：必要依存の閉包が不明、Read Cohort未保証、Provider Read Witnessが無い場合。未観測を「影響なし」「完全な同時Snapshot」「過剰Readなし」へ変えない。
- **QH-11〜13**：Manifest `Complete`でもRequired Member未確定、実member bytes不一致、ACKはあるが同Attempt Body未受領なら各々のConsumer資格を保留。
- **QH-14〜18**：Egress/Effect Grant/Owner受理の独立欠落、複数の不足が同時にある場合、未知依存とBody欠落が重なる場合。単一の列挙statusだけで理由を消さない。

**意図的な不健全基準J2の対照**：全18ケースで表示`outputDigest`を同じ文字列に固定し、「前回成功・同digestなので再利用」というJ2で全件再利用すると、必要な依存再評価または受渡し資格不足の**16件を誤再利用**する（公開・合成入力に限定した試験）。全件再確認J0では局所影響が無い2件まで再確認する可能性がある。J1の利益は、上記情報が実Productから取得でき、独立Oracleで偽再利用0を確認してから測る。

**最も重要な負例（依存閉包の虚偽）**：チェッカー内のMutationは`predicate:hidden_flag`の依存Edgeを削ったまま`dependencyCoverageVerified=true`とすると、同じ変更を「requalify」から**誤ってreuse候補**へ分類する。この合成例は、**形式的に整ったGraph/Checkerがあっても、必要依存Edgeの漏れをそれだけで検出できない**ことを示す。実製品ではTEI #2387/#2634のSQL非出力依存、#2624のValidation入力、#2632のActual Mapping/Route、#2633のConsumer Requiredを各Ownerが独立に照合し、閉包が示せない範囲をunknownへ残す。TAIには第二SQL Analyzer、Repository-wide Claim Graph、共通Grant Engineを導入しない。

**優先実証**：P1＝TEI既存read-only CLI/Go（#2586）から**Source/Role/Function Context/Query/Rule/Provider Route/実Result**の同Attempt参照を一件取得できるか。P2＝実Consumer Requiredと読取Artifact版、必要なSnapshot/Dependency証拠、EKI同Attempt Bodyを段階的に接続。P3＝別Harnessへ再開し、J0/J1/J2の偽再利用・再読取数・token/手戻りを比較。Mutation合格は製品の閉包証明ではなく、独立Source/Oracleと実Read traceが揃った場合だけより強い主張へ進む。

**資格**：今回PASSは**保存済み公開synthetic checkerのNode実行のみ**。TEI #2632/#2633/#2634の実Go製品試験（それぞれのPRに記載された観測資格を参照）、実Provider/DB/OS、SHO保存再開、EKI送受信、TAI実Skillロード、正式完全性Oracle/Owner意味受理はこの試行でNOT RUN。既存SK-C/RQ、MMI C-01/T2 G0-0、TEI #1119 Gateを変更しない。

## 9. 2026-11-02：値が変わらない変更でも、公開・提案・消費資格は再確認対象になり得る

[TAI Draft #272](https://github.com/hat47x/tai-pleroma/pull/272)の[回答前観測面の計画](https://github.com/hat47x/tai-pleroma/blob/docs/preanswer-observation-surface-20261102/docs/yi-constellation/preanswer-observable-surface-and-consumer-handoff-2026-11-02.md)と、[Mock Receiverを用いた限定6/6局所実行](https://github.com/hat47x/tai-pleroma/blob/docs/preanswer-observation-surface-20261102/evaluations/records/AS-LB-loopback-http-2026-11-02.json)を現在資格の依存評価へ接続する。**今回の実Mockで検証したのは架空のHTTP送信を一つのlocalhost Portが受信した範囲**であり、実Productの外部送信・非干渉・OS拒否は未観測。

| 変更（内部Value/元Sourceが同じ場合もある） | 必要な再確認の候補 | 保持してよい可能性があるもの／追加注意 |
| --- | --- | --- |
| **開示Policy/Audienceが変更** | Consumerへ今から提供するSkill/Tool一覧、結果・非公開Reason、Request/Log、現在のEgress資格 | 内部Read・過去の意味判断の**履歴**は保持。ただし従来の公開物を再送する権限はない |
| **Planner/Skillの参照Scriptが変更** | 実ロード依存閉包、候補Action/Probe名、実Tool call、Audience向けTrace | Product Sourceが不変でも「同じSkillが同じ応答を出す」と言えない |
| **SHO Renderer profileだけ変更** | 表示DOM/anchor/a11y/Clipboard/リンク自動取得とConsumerの表示資格 | Markdown Link Token/原文保持は可。表示一式や公開Egressの無変更を保証しない |
| **Tool/Action discovery集合が変更** | 公開Tool候補の理由・件数、実Available、明示Context、Current Grant | 昔のTool実行・研究結果は歴史として保持。隠れた新Toolの存在は開示Policyによっては非公開 |
| **EKI Body受領/SHO Consumer readだけ変化** | 同じTask/Attemptのdigest・実Artifact到達・Reader確認、必要な公開資格 | ResultClaim ACKの履歴は保持。受領から業務Effect/Owner意味受理へ自動昇格しない |

この表は**TAI #271の再確認候補**であり、TAIがProductの依存Graph・Policy正本・Rendererを再実装する指示ではない。依存が未観測のまま「現在値が同じだから無影響」「最終回答が同じだから送出問題なし」とするのは避ける。一方、影響のない独立なread-only活動をOS/Providerの資格が許す範囲で継続できるようにする。

**最初の反証**：開示Policyだけを狭め、内部Sourceと値を固定した二世界で、J0（全面再検証）、J1（当該外部Consumerの公開再資格化）、J2（過去成功を無条件再利用）を比較する。J1では内部Ownerの以前の確定Claimを無意味に破棄せず、**新規の外部Tool候補・Session Event・送信内容**の公開だけ現行Policyに従うか観測。さらにRenderer profileだけ変える別対照で、SHOの原文保持と表示再検証が分離できるかを試す。[SK-01 §U](../../evaluations/SK-01-harness-skills.md)で実Product側に引き渡す。合成Mock 6/6をJ1の実Product評価成功とは扱わない。

**状態**：Source差分/公開変更と選択的再資格化の検証計画。外部Harnessからの実Planner Trace・DOM・実Network/OS拒否・現在の業務Authority、SHO実読取、EKI実BodyやOwner受理は**NOT RUN**。

## 10. 2026-11-02：空集合・ABA・Relation再束縛をActivityの再利用資格に含める（SC-N）

**成熟したProduct側Evidence**：[TEI #2582](https://github.com/hat47x/tei-platform/issues/2582) の負依存・Relation path再束縛・複数Window、[TEI #2387 QX-31](https://github.com/hat47x/tei-platform/issues/2387) の実SQLite 12件（合成SQLの局所実行）、[#2640](https://github.com/hat47x/tei-platform/pull/2640)の正常0件/演算順序/ABA、[#2638](https://github.com/hat47x/tei-platform/pull/2638)のRole＋Eager依存先のVersion/Contract/Implementation Pin、[#2649](https://github.com/hat47x/tei-platform/pull/2649)の実CLI dispatch≠選抜discoveryを既存TAI #271の再資格化へ結ぶ。これらのOwnerのSource/Query/Role/Extension実装をTAI側に移設しない。

### 10.1 失効を判定する対象は「出力に出た値の変更」より広い

Result行が0件であるとき、既存行IDによる参照依存は空でも、**WHERE/NOT EXISTSのPredicate、Relation path/Binding、Parent selection、Provider Route、Read Scope・Cohort・page completeness、Ruleの非出力Field**は結果を成立させる条件。これらの依存を把握できないなら、0件という履歴を残しつつ、現在の「該当がない」というClaimは`not-established`か独立再取得候補とする。

特に0件の全件性は**対象Scopeを決めた上での完全Read**に相対。partial readから「対象なし」は言えないが、帰属が確かな1件の一致が見つかれば、「なし」の否定は部分Readでも成立する場合がある。**不存在の証明と存在の反例で必要な完全性が非対称**であることを区別する。

`t0=0→t1=1→t2=0`では、(A)t0が当時正しかった履歴、(B)t2に独立に再取得して確認した現在0件、(C)t0以降ずっと変化しなかったという期間Claimは異なる。(A)と(B)がtrueでも(C)はfalse。イベントが見えないProviderで(C)を断定せず、TTL・同じDigest・同じ最終値を無変更証明に転用しない。

`Filter→Order→Limit`と`Order→Limit→Local Filter`は演算順序が違えば0件/1件が変化し得る。UIの「0件」をActionの不存在・全件性へ昇格しない。SQLのPushdown/Local residualは各Targetの演算/NULL/Collation/Scope/時点を確認する必要がある。

### 10.2 影響範囲の二つの閉包を分ける

**Data/Query現在性の閉包**：出力Fieldに見えないRule入力、Relationの付替え、Row membershipへの否定依存、実ProviderのRead Cohortと変更観測範囲。これを持つOwnerはTEI #2506/#2582/#2387/#1708。

**Capability/Skill/Consumer現在性の閉包**：Role自身とEager依存先の`version + contract fingerprint + implementation fingerprint`の確認、実`Tool` dispatch/利用可能性と限定catalogの差、実Skill/References/Scriptsのロード、公開Policy、現在Host Grant、Renderer/Consumer Read、成果物同世代。これを持つOwnerはTEI #2620/#2638/#2649/#2605、TAI #270/#272/#232、SHO #6、EKI #465。

両閉包で同じ`SourceRev`文字列を持っていても、現時点の実取得・実Role実装、外部への開示権限まで一致するとは限らない。いずれも**意味のOwner受理/実Provider Effectを自動発行しない**。TAIが実装するのは各Productの現在証拠を要求し、必要なConsumerへ開示可能な結果だけ渡す横断Activityの選択・引継ぎである。

### 10.3 製品別Ownerへ戻す反証票

| Case | 変更と観測 | TAIの適切な帰結 |
| --- | --- | --- |
| **SC-N1 0件の否定依存** | 0件の完全Read、partial 0件、partialだが対象一致1件 | 歴史的「0件観測」／有界Scope内の不存在／不存在の反例を混同しない |
| **SC-N2 ABA** | 0→1→0。t0とt2の結果値は同じ | 履歴保持・現在再確認・期間無変更Claimを別判定 |
| **SC-N3 演算順序** | Filter→Order→LimitがB、Order→Limit→Local Filterが0件 | 同じSource/Command名で演算を入替えてfalse absenceにしない |
| **SC-N4 複数Window** | Window1はA→B、古いA応答後着。Window2は独立にAの現在資格を持つ | Window1へ旧Aを混入させず、Window2の正しい独立証拠を一律失効しない |
| **SC-N5 Relation再束縛** | 表示amount=600不変、O1.customerRefがC1/limit700→C2/limit500 | Rule依存を再束縛・再評価し、独立したAmount表示の履歴は保持可 |
| **SC-N6 Role実装Pin** | Root Role version固定、Eager依存先の実装fingerprintだけ変化 | 旧Role資格を現在の適用資格へ昇格しない。無関係Roleの全面失効も不要 |
| **SC-N7 Tool一覧差** | TEI選抜`commands`に実dispatchの`operations`が未掲載 | Discovery非掲載からUnsupportedを断定せず、**Toolを実際に呼べること／権限を持つことも推測しない** |
| **SC-N8 Output一致・Rule改版** | Output digestは同じでもRule/Policyだけ変更 | 対象Claimの再資格化。元Outputの履歴は保存し、今のGrant/Disclosureを再判定 |

[SK-01 §YのSK-N](../../evaluations/SK-01-harness-skills.md)へ[公開合成14件の自己整合Script](../../evaluations/tools/check-sk-n-negative-witness.cjs)と[V8限定記録](../../evaluations/records/SK-N-public-negative-witness-selfcheck-2026-11-02.json)を接続した。**14/14 PASSは公開の模擬関数と期待条件の自己整合**であり、TEIの実SQL/Go Executor・Role Extension Lock・実Window・TAI Harness/OS/Current Grant・独立Oracleの実証ではない。実TEI sqlite QX-31の12件PASSも**独立したProduct側実験**として保持し、TAIの14件と合算しない。

### 10.4 J0/J1/J2の評価で誤集計しない

`TAI.SC-06:J0`＝必要な全確認、`TAI.SC-06:J1`＝依存に基づく選択的再資格化、`TAI.SC-06:J2`＝古い成功の無検証再利用（危険な負例）。[TEI #1445](https://github.com/hat47x/tei-platform/issues/1445)のJ0/J1/J2は別定義なのでラベルを混ぜない。既存[TEI #2018](https://github.com/hat47x/tei-platform/issues/2018)の`BR-FULL/BR-SELECTIVE/BR-UNVERIFIED/BR-JOINT`と比較する際も**対応を明記してから**測定する。

測定軸：`false_absence_pass / ABA_as_no_change / missed_negative_dependency / unnecessary_invalidation / wrong_Window_adoption / stale_Role_implementation / actual_Reads / external disclosure / human review / total_cost`。Source version、実Provider I/O、必要Member、Read Scope/Cohort、Rule/Role実装、実Consumer資格とOwner/独立Oracleを揃え、`unknown/NOT RUN`を実成功として加算しない。既存TEI #1119 P0 Critical Pathを変更せず、**合成での早期反証と実Product/Hostでの証明を分ける**。

**状態**：本節はOwner別の設計統合・公開合成Referenceの14件自己整合のみ。実TAI Product/外部Harness、TEI Go Query/Provider/Role実装、SHO Renderer/保存、EKI Body、OS/Network強制、Owner業務受理は**NOT RUN**。新Negative Cache／Reactive/Policy/Agent Host／中央依存Graphを先に採用しない。
