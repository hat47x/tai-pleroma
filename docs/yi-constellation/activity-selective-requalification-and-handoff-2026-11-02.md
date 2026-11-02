# TAI Activity継続の選択的再資格化：意味・証拠・権限・成果物の条件付き再利用

2026-11-02。**設計提案／公開合成Referenceのみ。Owner受理と実Product/Harness統合はNOT RUN。**

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
