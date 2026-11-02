---
name: yi-tai-activity
description: >-
  YI Constellationで、利用者の一つの課題をSEI/SUI/TEI/SHO/EKIなどの製品へ
  必要に応じて分担し、出典・未決・権限・結果を保って活動を続けるときに使う。
  単独製品で十分な場合はその製品のSkill/CLIを直接使い、横断処理を増やさない。
---

# TAI Activity：目的に必要な能力を組み合わせる（試作）

> **試作・NOT RUN**：このSkillは配布前の設計・評価サンプルである。ここに書いた手順や製品名は、CLI/MCP接続や実行権限が現在のHarnessに存在することを保証しない。YIブランドは製品別契約の正本ではない。

## 適用範囲

- 利用者が調査→判断→設計/文書化→委任→結果評価まで、一連のActivityの継続を求める場合に利用する。
- モデリングだけならTEI Skill、既存表の文書参照だけならMMI Skill、文書編集だけならSHO Skill等を優先できる。TAIの利用は任意とする。
- SEIは根拠・判断・専門Method、SUIは仮説と意味形成、TEIはモデル・生成・検証、SHOは文書、EKIは委任と独立結果確認の責任を持つ。

## 作業手順

1. **依頼を目的・用途に落とす**。何を改善したいか、対象/時点、許可された資料、望む成果、本人・Owner判断が必要な箇所を確認する。必要以上の情報収集・通知を前提にしない。
2. **実際に使える能力を確認する**。利用可能な各製品のSkillと現行CLI/API/MCP Toolの存在・バージョン・実接続を照合する。`SKILL.md`中の説明や任意のTool annotationだけで利用可能性・実効権限を断定しない。未搭載機能を実在するコマンドとして生成しない。
3. **必要な製品だけを選ぶ**。依頼を各Productの専門責務に対応させる。各製品の原Source・Meaning・Resultの正本を尊重する。利用者の目的に必要なければ追加Tool/Skillをロードしない。
4. **開示条件に従って受け渡す**。Source保持側が許可するProjectionのみを外部Harness・別Productに渡す。Raw・秘密・非公開の構造情報・権限Grantを転送しない。見えない対象の全体件数や真偽を推定で確定しない。
5. **提案・検証・採否・作用を区別する**。観測、仮説、専門Method提案、歴史的accepted、現在の適用性、Owner意味受理、Tool実行、外部Effectのどの段階か明示する。正本側から得た状態を再解釈して勝手に昇格させない。
6. **作用時点を検証する**。書込み・公開・外部作用の前に各Product/Host/Providerによる現時点の権限・Target・revision・期限を確認する。失敗・結果不明での無条件の再試行を避ける。Tool responseと正式Receiptおよび実結果を分離する。
7. **活動を引き継げる形にする**。利用者の目的、許可範囲、使用したSource revision、対象・時点、確認できた根拠、候補/未決、作成物、各Productが検証した事項、現在の実効果/未知、次の候補を最小限の参照で提示する。別Harnessへ秘密・Raw・不必要な内部推論をコピーしない。
8. **能力不足を明記して縮退する**。Skill/MCP/CLIの未設置、ネットワーク断、OS制限などは`unsupported/unavailable`として区別し、許される読み取り・文書作業などを継続する。

## 結果の書き方

次の見出しは必要に応じてのみ使う：`目的・対象`、`使用したProduct／版`、`確認できた資料と出典`、`仮説・未決`、`提案／実装／意味受理／外部作用の別`、`検証した結果と未実施`、`次に必要な作業`。

検証可能な情報はSource/Tool/Receiptへ戻れる参照を付ける。実行できなかったことや、入力を受領しただけの状態を「完了」と書かない。Ownerの採否は製品ごとの既存経路に残す。

## Skill自身の能力を過大申告しないための追加条件

- **製品向けSkillの実在確認**：ルート`skills/ponytail`は開発一般向けでありSEI/SUI/EKIの製品操作Skillではない。MMIの`skills/mmi`は既存の製品向けSkillだが、利用Harnessの実Tool接続を別途確認する。
- **比較するClaimを取り違えない**：数値・文章の一致と、対象集合／粒度／単位／時間／用途が同一のClaimであることは別。必要な情報が許可Projectionから区別できないならSource保持側の限定照会を使い、不可能なら`unknown`を維持する。
- **Methodと実現を区別**：SEIの認知Method、SUIの意味探索、TEIのDSL/Domain Plugin、SHOの文書投影、EKIの実Body/Receiptは別のOwner。SkillはMethodの提案・Tool利用の案内であり、製品機能の実装や正式結果受理ではない。
- **実際のSkillロードと秘密の受渡し**：同名Skillが存在する場合は実pathとcontent digest、Harness/Profileを確認する。別Harnessへ活動を移すとき、開示許可、認可、実施結果の現在適用性を再確認する。DSH等のSession LogやTool拡張送信も確認可能な範囲で検査する。


## Skill・Toolの実体と開示に関する追加注意（評価案）

- **能力の説明と実能力を区別**する。Skillの名前や説明、CLI/MCPの一覧は候補発見にすぎない。実際に利用できるTool、Toolの版、当該SessionのHost資格を確かめ、確認できない項目はunknownとする。
- **実ロードを推測しない**。配布・参照したroot Skill文書のdigestが一致しても、参照先の資料・Script・MCP Toolの内容や、実際にHarnessへロードされたbyteは同一と限らない。観測できる範囲だけを利用記録として示す。
- **発見の段階でも開示制限を守る**。外部へ返すSkill/Tool名・一覧、引数Schema、Error、件数、拒否理由が機密になり得る。公開可否はSource保持Product/Hostの実Policyに従い、Skillの記述で権限を増やさない。
- **隠れたSourceの真偽を創作しない**。同じ開示投影から内部全体の問いに異なる答えがあり得る場合、元Productによる許可済みの限定検査か、根拠不足のまま扱う。内部検査のYes/No自体が非公開の場合、結果開示を要求しない。
- **TEI単独等の正規入口を尊重**する。Product自身のread-only Skillで完結する仕事にTAIや別Productを必須化しない。TEI #2605のCLI操作は実環境で検証したものだけを利用し、validateのexit 0を意味受理に昇格させない。

これらは動作済み安全保証ではなく、[SK-01 SK-E01〜07](../../../evaluations/SK-01-harness-skills.md)で反証するための手順案である。


## Source改版・生成物を他製品へ渡す場合

- Sourceの現在版（S）、版間の対応**候補**（C）、Ownerが受理した意味（M）、導出結果・Generator/Template版（G）、完成した一式の公開とConsumerによる実読取り（P）は別の証拠。A→B→Cの候補経路があってもA→Cの意味同値・旧受理の再利用を約束しない。
- 文書・ライブラリ・複数ファイルの成果物について、Manifest/Digest/生成コマンド成功だけで同一世代の一式を利用者が取得したと断定しない。実Productに世代固定・ファイルbyte照合の入口がない場合、公開の整合はunknownとして各Product Ownerへ返す。
- EKIのTask/AttemptでResultClaimやACKを確認できても、同一Attemptの出力Bodyが送達されたか、AcceptedResult・外部Effectが得られたかは別に報告する。見えないBodyを補作・再実行しない。
- 参照先のSourceやManifestが非公開なら、存在することや件数を推測しない。必要な事実の照合は、許可された保持Productの内部検査を利用する。

この注意は[SK-01 SK-J](../../../evaluations/SK-01-harness-skills.md)の未実施反例に基づく**評価用指針**であり、任意のTEI/SHO/EKI Productに新しいToolや実行権限を与えない。



## Markdown・TEI Function Context・SHO Research Indexをまたぐ依頼

- **Markdownを読むことと実行意味の受理を分ける。** 表・式・説明・Test Caseが同一Markdownにあっても、それぞれのRoleの明示的な解決条件をTEIの実在するCLI/Pluginで確認する。Role未指定の表をFunction/Testとして実行しない。Expectedが書いてあってもテストが実行されたわけではない。
- **Relationと取得Scopeを分ける。** Data Modelに関係が定義されていても、Function Data ContextのEntity/Relation path/Field/grain/scope/完全性の明示Mappingがない限り、隠れたRelationを取得対象に追加しない。Contextが指定されていても実Provider Read、認可、同一Snapshot、全件取得は別証拠。
- **表示と保存の意味を分ける。** Derived Dataset/集約文字列などの非可逆Projectionを編集しても、Source ID/型付きIntent/更新Rule/現在Hostの権限が確認できなければ、DBへのPATCHや全置換の成功とは扱わない。Native SQLは特殊な明示Bindingがある場合のみに扱う。
- **論文リンクは論文本文ではない。** SHO Research IndexのL0はリンク・順序・字下げの保存だけで価値がある。URLや見出しだけから論文の主張・引用/発展関係・実装済みのアルゴリズムを断定しない。著者が明示したacademic edgeと整理用の親子を分け、原典未取得なら未取得として設計候補までを支援する。
- **必要な製品を選ぶ。** リンク整理だけならSHO単体、モデル調査だけならTEI単体の適切なread-only Skillで足りる場合がある。複数製品を使う目的に限ってTAI横断Skillで根拠と未決をつなぐ。新しいTEI Markdown Role解決器・SHO Paper→Code機能をSkill文書の存在から実装済みと扱わない。

上記は[SK-01 SK-L01〜L10](../../../evaluations/SK-01-harness-skills.md)の評価設計であり、現在のTEI/SHOの機能完了・OS/Provider/Owner受理を保証しない。

## 関連

- [横断設計](../../../docs/yi-constellation/harness-skill-plugin-plan-2026-11-02.md)
- [評価票](../../../evaluations/SK-01-harness-skills.md)
- [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)
- [MMI既存Skill](https://github.com/hat47x/markdown-matrix-injector/blob/main/skills/mmi/SKILL.md)

本ファイルは`examples/`内のportable Skill例であり、各Harnessへの自動インストール・Plugin配布は行わない。


## Semantic Contextと操作候補を組み合わせる場合（評価用追加）

- **目的に合う実在するProduct機能を選ぶ**。外部HarnessでのAction選択は、利用者の目的・Subject/Grain/Role・ContextのSource/epoch・必要Operation・許可Projectionと、実際に提供されているCLI/MCP/Providerを突合する。Table/Form/CUI/GraphのどのUI入口かだけでBusiness Actionの意味を決めない。
- **Offerと実行を分ける**。意味的に適用できるActionが候補として示されても、その時点の認可・Target revision・実Provider効果は別に照合する。集計行/Join結果/Graph Edgeと業務Entity IDを混同しない。部分集合しか取得していない場合、全件操作・不存在Claimを確定しない。
- **単独製品を優先できる**。TEIの意味/ActionはTEI製品Skillへ、SEI MethodはSEIへ、SUI意味探索はSUIへ、SHOの執筆・SourceはSHO/MMIへ、EKIの委任はEKIへ委ねる。TAI Skillは一件のTaskが複数製品を必要とする場合にActivityを組み合わせ、実行系を二重実装しない。
- **UIとHarnessの届く範囲を観測する**。Productが実際に開示したCapability/Toolだけを案内する。ボタン表示・MCP Annotation・HTTP Ackを権限/完了の根拠としない。元Productが現在のTarget/権限/Effectを確認できないなら未確認と記録する。

[設計とSK-M評価](../../../docs/yi-constellation/harness-skill-semantic-action-routing-2026-11-02.md)。新Action API・CLI・Providerを本Skillが実装済みと宣言するものではない。


## Product契約からSkillを案内する場合の整合性（評価用）

製品がCapability/Operation/意味Roleの説明を公開している場合、Skill側にはその**実Source・契約版・実Toolの署名と未対応事項**を参照する。生成済み説明であっても現在利用可能なCLI/MCP、Product実装と照合し、古いTool例を実能力へ昇格させない。説明文とProduct契約が違う場合、外部Harness向けの手順とOwner側の現行契約を区別して報告する。

- Markdown、式、Graphviz、DSL等の違いだけで重複Action能力を宣言しない。意味Role/Operator/入力・出力/Target版が一致するかをProduct側の結果から確認する。引用・例示・未解決Roleは実行可能という根拠ではない。
- Product SkillのTechnical Referenceと、人/AIが執筆したMethod・Task Recipeは役割が異なる。Product Coreと実APIの正本が優先され、Skillだけで新しい権限や完了が生じることはない。
- 非公開Capabilityの名前、件数、存在や診断理由を外部へ公開するかもProduct/Hostが判断する。Product単独で仕事が成立する場合にはTAIを必須にせず、複数Productが必要になった場合のみ横断接続する。

[Capability-derived Skill設計](../../../docs/yi-constellation/capability-derived-skill-projections-2026-11-02.md)と[SK-01 SK-D](../../../evaluations/SK-01-harness-skills.md)は未実装の比較計画である。

## 現在のTrust・設定読取り失敗を伴うSkill接続（合成評価指針）

- Skillをインストールできたこと、古いHarnessで接続できたこと、現行Issuer/Grantを確認したこと、実Providerへ作用できることを分ける。**認証の最終判断は現在のHost/各Product側**へ委ね、TAI SkillからmTLS/Trust Bundle/Owner Authorityを再実装しない。
- Source側の導入状態が**明示的な未導入（Ownerが旧互換方式を許可した場合）**なのか、**導入済みだが読取り障害・レコード不正・履歴喪失**なのかを消さない。後者を「未設定だから通す」に変換せず、適切なProductのUnavailable/Denied結果へ引き継ぐ。
- SHA等のDigest比較では**対象byteとアルゴリズムを確認**する。両側が同じ関数で生成した一致値は独立Oracleではない。Issuer Fingerprint／Skill Bundle／Source／ArtifactのDigestを同じ信頼資格にまとめない。
- 他Harnessへ再開する際は、旧Skillの内容一致やTask受付履歴を現在の機密Source開示資格・実行Grantへ昇格させない。権限確認が不足する作用は保留し、実権限のある非機密の調査や文書下書きを継続可能とする。

本節は[SK-01 SK-TB01〜09](../../../evaluations/SK-01-harness-skills.md)の合成比較計画であり、EKI #433/#466/#467の製品修正・実mTLS合格や現在の外部ハーネス接続を保証しない。

## Data取得・Rule依存・Planner開示の手順案

ProductにData/Rule/ProviderのEvidenceがある場合は、**何を要求したか**（Function Data ContextとRule Dependency）、**実Requestが何を要求したか**、**どの範囲を実際に読んだと観測できたか**、**目的Claimを評価できるか**、**どこへ開示できるか**を別々に確認する。実ProductにTraceがなければ取得量を推測で断定しない。

- Display Mapping外のDataをRuleが必要とする場合、受理済みRule DependencyをProduct側で調べる。Ruleを評価するために秘密入力が必要でも、外部Harnessが無断でその原値や判定Booleanを要求・取得しない。Product内で評価でき、かつ結果公開が許される範囲を利用する。
- `all`という取得宣言は、実観測したResultの完全性とは異なる。別Source/時点/epochのReadを統合する場合は、Product側の同一Snapshot根拠がなければ結合Claimを未確定として保持する。
- Tool/Skillの存在・候補・非公開Field名・拒否理由自体が開示対象になり得る。外部Plannerに非公開のProvider/Actionの有無を直接使わせず、許可済みの公開Capability/Toolから作業を構成する。
- Toolがread-onlyでも、LLM/APIへの外部送出許可は別。実Host/NetworkとConsumer Policyによる送出証拠を参照する。Rule Preview/Method提案/Claim ACKと外部Action完了も区別する。

これは[SK-01 SK-F](../../../evaluations/SK-01-harness-skills.md)の反例用の作業指針。TAI SkillがTEI Rule Engine、SEI Inquiry、OS非干渉監査や新Capabilityを実装した事実ではない。

## 過去の成果を再利用する前の局所再確認（評価用）

- **現在の問いに必要な証拠を特定する。** Source/Rule/Oracle/取得Snapshot/型・粒度・意味版、Skillの参照Script・実Tool/Host、文書Template/公開Artifact、現在の開示・実行権限を別々に確認する。必要な依存関係が不明なら過去のPASSを現在の全面PASSへ昇格させない。
- **影響するClaimだけ再評価候補とする。** 例えばD1だけに依存する既存の集計は無関係のD2変更で一律失効させず、D1×D2のJOINは再評価対象。依存が完全に観測できなければ、影響なしと断定せず不明としてProduct Ownerに照会する。
- **共同結論は別に成立条件を確認する。** SEI/TEI/SHO等の局所結果がそれぞれPASSしても、同じSource/Scope/Grain/epoch/Claimであるかは追加の証拠が必要。古いSnapshotや別Consumerの結果を単純に結合しない。
- **現在の権限は都度Product/Hostに確認する。** Model/Skill/Manifest/過去Trustが同じでも、現在のHost Grant・Issuer・外部開示は別。確認不能なEffect/送出を保留し、公開合成資料による独立read-only作業は継続可能な範囲で行う。

[SK-01 §P／SK-RQ01〜12](../../../evaluations/SK-01-harness-skills.md)は以上の指針に対する公開合成受入案。実製品の再評価API・独立Oracle・Effect認可を本Skillが実装したという意味ではない。

## Activity再開とProduct別の選択的再資格化（評価案）

前のSession/Agent/Skillの「成功」「検証済み」を、別のSource・時点・Provider・Consumer/Hostへ自動的に移植しない。**履歴として当時成立した観測**と、**現在の目的にその結果を利用できる資格**を別々に説明する。

- 目的のClaim・Scope・時点に必要なTEI Source/意味Role・Rule、SEI Method、EKI Task/Attempt/Body、SHO Source Occurrence・実読取版、Host Current Grant/Trustの**存在する参照**を調べる。存在しないToolや証拠は未実施・unknownで扱う。
- 変更されたSource/能力/Methodと、実際に受理済みの依存関係に基づき、再確認の必要なProductだけを選ぶ。Edgeが不明なら「無影響」と推測しない。無関係な履歴・独立作業は利用可能な範囲で継続する。
- EKIのClaim ACKをBody実受領にせず、Body digest照合をSHOの実読取・固定納品にせず、生成Artifactの存在を利用者の受取にしない。遅延Bodyを再確認することと、別Attemptの効果を再実行することを分ける。
- 以前のGrantやTrust Bundleの成功では現在の危険操作は許可されない。現在の実Host資格と開示範囲が不明な操作は保留し、権限のあるread-only調査や説明は続けられる。
- 秘密・非公開のSource/Capability/Tool/結果/診断はConsumerごとに許可されたProjectionへ落とし、活動引継ぎ票自体も情報公開対象として扱う。

[選択的再資格化の計画](../../../docs/yi-constellation/activity-selective-requalification-and-handoff-2026-11-02.md)と[SK-01 SK-C](../../../evaluations/SK-01-harness-skills.md)は**公開合成だけの評価案**。現行TAI Skillが新しい実行器、Oracle、中央Claim DB、Provider、Owner受理資格を取得した証拠ではない。
