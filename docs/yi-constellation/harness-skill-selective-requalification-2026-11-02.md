# YI / TAI Harness：変更後の選択的再資格化と共同Claimの成立条件（2026-11-02）

**位置付け：横断評価仕様候補、Product実装・正式共通Schemaではない。** 対象：[TAI Draft #270](https://github.com/hat47x/tai-pleroma/pull/270)／[SK-01](../../evaluations/SK-01-harness-skills.md)。最新の[TEI #1445 H8-P13/P14](https://github.com/hat47x/tei-platform/issues/1445)（資格化の再検証費用と局所PASSからの共同Claim）、[TEI #2582](https://github.com/hat47x/tei-platform/issues/2582)（Function内のClaim別依存と非単調な結果更新）、[SEI Draft #770](https://github.com/hat47x/sei-cognition/pull/770)（問い相対の十分性、固定Corpusと未知世界、複数Readの混合）、[TEI #2628](https://github.com/hat47x/tei-platform/issues/2628)（出力同値とProvider実読取の差）、[SHO #6](https://github.com/hat47x/sho-composer/issues/6)（文書の原Source・評価時点・Derived/Review）、[EKI #467](https://github.com/hat47x/eki-fabric/issues/467)（現在Trustの確認不能）を接続。

## 1. 成熟した方針：「成果を保つ」と「現在の使用を許す」は別

Tokenの低価格化によって大量の候補・Skill・Product能力を開発できる。その一方で、**検証済み根拠の選択的な維持**と**実利用時の再適格性**を区別しなければ、全件再実行の負担か、古い資格の不正流用が増える。

- **過去の実証**：特定Source/Rule/Oracle/Tool/Host/時点について観測された成功は、歴史的な記録として保持する。
- **現在のClaim**：同じ問い・対象・粒度・時点・必要なRead-set・意味軸に対し、依存関係の変化が当該Claimへ影響するかを根拠付きで調べる。**依存を観測していないことは、非依存の証拠ではない**。
- **現在の実行・開示**：たとえ過去のClaimと生成物が不変でも、Host Grant/Issuer/Policy/Consumerの公開範囲は利用時に独立確認する。外部送出済みbyteは後から撤回できないため、過去の露出証拠も歴史的に保持する。
- **共同Claim**：個々の局所PASSが揃っても、Source/Scope/Grain/Snapshot/Rule/Oracleの連結が成立しなければ共同Claimは未確認。全面再実行をしても異なるProviderが共通Snapshotを保証しなければ解決しない。
- **不確実性に応じた作業継続**：特定の不可逆Effectを保留しても、許可済みread-only調査、合成fixture、非機密な文書整理は継続できる。CSW/SUIの自由な生成探索に途中の採否Gateを追加しない。

## 2. 既存Productが持つ依存・現在性を、TAI Skillは「参照」でつなぐ

| 領域 | 既存Ownerの判断・観測 | TAI横断Skillが扱う範囲 |
| --- | --- | --- |
| TEI Context/Query/Rule | #2582のClaim別Read依存・変更時点、#2628のProvider実アクセスWitness、#2514共同Oracle | 当該Claimに関わる既知依存と未解決を引用し、再取得対象を候補にする |
| SEI Inquiry | #767/#770の問い相対の十分性、未知世界での撤回、複数Readの時点 | 認知Methodの旧観測を現在の全称判断へ昇格させず、必要な追加Inquiryを候補として渡す |
| SUI/SHO | SUI投影の開示、SHO #6のSource改版／Review・Renderと引用の版 | 旧説明は歴史として保持し、本文Templateのみの変化とMeaning改版を分ける |
| EKI/Host | #465同Attemptの実Body、#466/#467現在Issuer・Trust、Host Permission | 旧ResultClaim/TrustやToolの説明を現在のEffect許可にしない |
| Product Skill/Series | #74のBundle閉包、#2605/TAI #270の実ロードとTool実体 | Script/参照文書変更時には該当Skill経路だけ再検査し、無関係なProduct Meaning全件を失効させない |

**新たなTAI共通の依存グラフDB・自律同期サービス・Authority・Oracleは作らない**。現状は各Issue/実ファイルの証拠参照を用いる受入票と、再確認したい対象を決めるための比較手順に限定する。

## 3. 変更イベントの種類ごとに再確認の範囲を変える

| 変更 | まず再確認する範囲 | 保持できる可能性があるもの | 特に危険な誤判断 |
| --- | --- | --- | --- |
| Source・取得Scope・Rule・Oracle改版 | 依存するClaimとその独立Oracle、現在Source/Read witness | 依存が**証明された**無関係なClaimの過去Evidence | 同じ表示ValueなのでRule/Readも同じと断定 |
| Skill root/参照Script/実Tool変更 | 配布閉包と実Sessionにロードされた内容、Tool/API対応、該当Skill経路 | 無関係な業務モデルと別Toolの実Evidence | root SHAだけ一致し、参照Script差替を見逃す |
| SHO説明Templateのみ改版 | 文書生成・引用/表示・著者Review、固定納品世代 | 正しく別管理されたTEI業務意味と実ライブラリ | 文章変更から業務意味まで変更した、または旧文書が自動採用されたとする |
| Grant/Disclosure/Trust変更 | **利用する都度**Product/Hostの現在許可、実送信先、発見・診断の開示可否 | 過去の局所テスト結果・著者が執筆した素材 | 過去の許可・Skillインストールを現在の外部送出/Commitへ流用 |
| EKI Body到着/Receipt変化 | 同一Task/Attempt/出力byte・AcceptedResult・必要な実Effect | Source/Meaning・ unrelated Task の過去Evidence | Claim ACKをFull OutputやBusiness完了と呼ぶ |
| Multi-Consumer結合 | 同じSource/Scope/Grain/Snapshot/Claim dependency・Oracleを再照合 | 各Consumerの限定的局所PASS | 局所PASS全件を共同Claim PASSと合算 |

## 4. 比較する三方式：全体再検証・選択的再検証・限定的保留

[TEI #1445 H8-P13/P14](https://github.com/hat47x/tei-platform/issues/1445)と合わせて、次を同一公開fixtureで比較する。

- **R0 全面再実行**：全ClaimとConsumerを再検証する。依存解析の不確実性が高い場合の比較基準。ただし実Providerが一貫Snapshotを出さなければ共同Claimの資格は得られない。
- **R1 根拠に基づく選択的再確認**：変更に依存するClaim/Skill/Publish経路だけ再検証し、影響なしを**根拠付き**で示せた部分を保持する。権限・開示は各利用時に別途検査する。
- **R2 不明点の限定保留**：依存がunknown/Provider実Read未観測・共同Snapshot未成立の場合、確認可能なClaimを限定して利用し、該当するEffectを保留。すべてを「PASS」「FAIL」「0件」に潰さない。

**比較KPI（提案）**：誤った既存資格の流用、不要な全面再検証、再取得と独立Oracleの件数、Product Skill/Tool呼出し、Runtime/Token/人の確認負荷、保留した危険なEffect、実利用者が継続できた安全な作業、外部へ実際に出た情報。見積Token数を実請求としない。別製品の合成PASSをTAI全体PASSとして足さない。

## 5. 12ケースの公開合成反例と受入順序

[SK-01 §Q](../../evaluations/SK-01-harness-skills.md)にSK-RQ01〜12を定義する。[公開fixture](../../evaluations/fixtures/SK-RQ-selective-requalification.synthetic.json)は**未封印の教育・整合性確認用**。公開Expectedを含むため独立した盲検Oracleではない。

1. Sourceが別領域で変更され、必要依存の完全な既知集合から非影響を説明できる（旧資格の局所保持）。
2. Claimが依存するRule改版で、表示が同じでも再検証対象となる。
3. Source/Rule依存が不完全で「影響なし」と断定できない。
4. root Skillは同じでも参照Scriptが変わり、実ロード・Tool動作資格を再確認する。
5. 開示Policyが狭くなり、歴史的根拠は保持、**外部公開**は再認可する。
6. EKI Trust Bundle読取不能により**危険なEffect**を保留、独立read-only作業は継続する。
7. 局所ReadはそれぞれPASSでもepochが混ざり、共同Claimを未確認にする。
8. TEI/SHOの公開Manifestと実fileが混合世代となり、公開一式を再確認する。
9. 同AttemptのEKI ResultClaim ACK後にBodyが届き、送達は再確認、Business Effectは別。
10. SHO Templateだけ改版され、文書再Reviewが必要だがTEI業務Meaningを一律失効させない。
11. Sourceが同じでも独立Expected/Oracle版が更新され、関連Claimを再検証する。
12. 問いの用途が変わり、byte同一でもScope・必要十分性・開示適格を再確認する。

**最初の試験順**：SK-G0／TEI #2605の実read-only入口→RQ01/RQ02/RQ03で過少・過剰再確認を合成比較→RQ07で共同Claimの追加条件→RQ05/RQ06でSource Ownerによる実権限・開示の差→Productの既存実Oracle/Providerの実測を受け、H2/H3/H4/H5のSkill増分へ。全12ケースの試行は、公開fixtureのセルフチェックとは区別する。

**Ownerと状態**：各Productの現在のRead/Rule/Issuer/Output/Publishの真偽・実装は各Ownerが保持する。TAIは比較可能なClaimと追加検証の選択を担い、外部Harnessが原資料Rawを閲覧できない場合は元Productの許可Projectionと内部再照会を使用する。本書は**計画案**であり、実Product/Tool/OS/Harness/Owner受理の検証はNOT RUN。

## 6. #271との役割統合：Activity再開と局所Skill再資格化を二重実装しない

同じ2026-11-02に[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)／[Activity継続計画](activity-selective-requalification-and-handoff-2026-11-02.md)が起票された。**こちらをActivity全体の唯一の横断Owner**とし、SK-C01〜15はSource→各Product→Consumer/Host/Harnessの**依存EdgeとHandoffの到達関係**を検証する。今回のSK-RQ01〜12は、**変更イベントを受けた特定Claim/Skill成果の再資格化が過少・過剰にならないか**を比較する補助的な評価視点とする。SK-C/SK-RQの期待判定を同じ共通Runtimeへ二重実装したり、両方の合成PASSを「27件の製品実証」に合算したりしない。

| 評価面 | 主Owner・受入表 | 他方への入力 |
| --- | --- | --- |
| Productを跨いだEvidence/Source/Bodyの実Handoff・復帰条件 | **#271／SK-C01〜15** | 履歴と現在性を区別したSource/Task/Owner参照 |
| 変更で影響するClaim・Skillだけを再確認する判断 | **#270 SK-01 §Q／SK-RQ01〜12** | 変更イベント、既存Productが実証した依存、未確定項目の保留 |
| 共同Claimの同一Snapshot・Rule/Read | TEI #2514/#2582、SEI #767/#770 | Productごとの正式な局所Oracle/Result |
| EKI Trust/Body、SHO文書、外部送出権限 | EKI #433/#465/#467、SHO #6、TAI #232 | 実Reader/Host/Policyの資格。過去SkillやHandoffの文章だけでは代用不可 |

**比較ラベルの衝突を避ける**：#271の`J0=全面再実行 / J1=選択的再資格化 / J2=旧成功を無検証で流用（意図した負例）`と、本書の`R0=全面再確認 / R1=依存に基づく再確認 / R2=未知だけ保留する安全な選択肢`は、**J2とR2が反対の意味**なので統一しない。横断レポートではラベルだけでなく、その定義・目的・実行された方式を併記する。次段で同一fixture上の共通評価が可能になれば、ベースライン比較を再利用して重複試行を減らす。

**状態**：#271側のSK-C公開fixture 15件とmutation 4件は同レーンのV8限定自己整合であり、SK-RQの12件/14分類とは別。どちらも実Product E2E・外部Harness・独立Oracle・Owner採用を示さない。新しいIssue・同内容の実装担当は増やさない。
