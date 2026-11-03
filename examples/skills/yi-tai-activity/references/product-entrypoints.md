# Productの用途・操作入口・モデル境界（必要時だけ参照）

> **評価資料・Product実動作未受理**。このファイルは[TAI Activity Skill](../SKILL.md)が必要な場合にだけ参照する詳細手順。旧rootの該当節を省略せず分離した。製品Skillの実ロード・実Tool呼出し、Host Grant/Disclosure/Owner意味受理を保証しない。

## Skill自身の能力を過大申告しないための追加条件

- **製品向けSkillの実在確認**：ルート`skills/ponytail`は開発一般向けでありSEI/SUI/EKIの製品操作Skillではない。MMIの`skills/mmi`は既存の製品向けSkillだが、利用Harnessの実Tool接続を別途確認する。
- **比較するClaimを取り違えない**：数値・文章の一致と、対象集合／粒度／単位／時間／用途が同一のClaimであることは別。必要な情報が許可Projectionから区別できないならSource保持側の限定照会を使い、不可能なら`unknown`を維持する。
- **Methodと実現を区別**：SEIの認知Method、SUIの意味探索、TEIのDSL/Domain Plugin、SHOの文書投影、EKIの実Body/Receiptは別のOwner。SkillはMethodの提案・Tool利用の案内であり、製品機能の実装や正式結果受理ではない。
- **実際のSkillロードと秘密の受渡し**：同名Skillが存在する場合は実pathとcontent digest、Harness/Profileを確認する。別Harnessへ活動を移すとき、開示許可、認可、実施結果の現在適用性を再確認する。DSH等のSession LogやTool拡張送信も確認可能な範囲で検査する。

## Markdown・TEI Function Context・SHO Research Indexをまたぐ依頼

- **Markdownを読むことと実行意味の受理を分ける。** 表・式・説明・Test Caseが同一Markdownにあっても、それぞれのRoleの明示的な解決条件をTEIの実在するCLI/Pluginで確認する。Role未指定の表をFunction/Testとして実行しない。Expectedが書いてあってもテストが実行されたわけではない。
- **Relationと取得Scopeを分ける。** Data Modelに関係が定義されていても、Function Data ContextのEntity/Relation path/Field/grain/scope/完全性の明示Mappingがない限り、隠れたRelationを取得対象に追加しない。Contextが指定されていても実Provider Read、認可、同一Snapshot、全件取得は別証拠。
- **表示と保存の意味を分ける。** Derived Dataset/集約文字列などの非可逆Projectionを編集しても、Source ID/型付きIntent/更新Rule/現在Hostの権限が確認できなければ、DBへのPATCHや全置換の成功とは扱わない。Native SQLは特殊な明示Bindingがある場合のみに扱う。
- **論文リンクは論文本文ではない。** SHO Research IndexのL0はリンク・順序・字下げの保存だけで価値がある。URLや見出しだけから論文の主張・引用/発展関係・実装済みのアルゴリズムを断定しない。著者が明示したacademic edgeと整理用の親子を分け、原典未取得なら未取得として設計候補までを支援する。
- **必要な製品を選ぶ。** リンク整理だけならSHO単体、モデル調査だけならTEI単体の適切なread-only Skillで足りる場合がある。複数製品を使う目的に限ってTAI横断Skillで根拠と未決をつなぐ。新しいTEI Markdown Role解決器・SHO Paper→Code機能をSkill文書の存在から実装済みと扱わない。

上記は[SK-01 SK-L01〜L10](../../../../evaluations/SK-01-harness-skills.md)の評価設計であり、現在のTEI/SHOの機能完了・OS/Provider/Owner受理を保証しない。

## Semantic Contextと操作候補を組み合わせる場合（評価用追加）

- **目的に合う実在するProduct機能を選ぶ**。外部HarnessでのAction選択は、利用者の目的・Subject/Grain/Role・ContextのSource/epoch・必要Operation・許可Projectionと、実際に提供されているCLI/MCP/Providerを突合する。Table/Form/CUI/GraphのどのUI入口かだけでBusiness Actionの意味を決めない。
- **Offerと実行を分ける**。意味的に適用できるActionが候補として示されても、その時点の認可・Target revision・実Provider効果は別に照合する。集計行/Join結果/Graph Edgeと業務Entity IDを混同しない。部分集合しか取得していない場合、全件操作・不存在Claimを確定しない。
- **単独製品を優先できる**。TEIの意味/ActionはTEI製品Skillへ、SEI MethodはSEIへ、SUI意味探索はSUIへ、SHOの執筆・SourceはSHO/MMIへ、EKIの委任はEKIへ委ねる。TAI Skillは一件のTaskが複数製品を必要とする場合にActivityを組み合わせ、実行系を二重実装しない。
- **UIとHarnessの届く範囲を観測する**。Productが実際に開示したCapability/Toolだけを案内する。ボタン表示・MCP Annotation・HTTP Ackを権限/完了の根拠としない。元Productが現在のTarget/権限/Effectを確認できないなら未確認と記録する。

[設計とSK-M評価](../../../../docs/yi-constellation/harness-skill-semantic-action-routing-2026-11-02.md)。新Action API・CLI・Providerを本Skillが実装済みと宣言するものではない。

## Product契約からSkillを案内する場合の整合性（評価用）

製品がCapability/Operation/意味Roleの説明を公開している場合、Skill側にはその**実Source・契約版・実Toolの署名と未対応事項**を参照する。生成済み説明であっても現在利用可能なCLI/MCP、Product実装と照合し、古いTool例を実能力へ昇格させない。説明文とProduct契約が違う場合、外部Harness向けの手順とOwner側の現行契約を区別して報告する。

- Markdown、式、Graphviz、DSL等の違いだけで重複Action能力を宣言しない。意味Role/Operator/入力・出力/Target版が一致するかをProduct側の結果から確認する。引用・例示・未解決Roleは実行可能という根拠ではない。
- Product SkillのTechnical Referenceと、人/AIが執筆したMethod・Task Recipeは役割が異なる。Product Coreと実APIの正本が優先され、Skillだけで新しい権限や完了が生じることはない。
- 非公開Capabilityの名前、件数、存在や診断理由を外部へ公開するかもProduct/Hostが判断する。Product単独で仕事が成立する場合にはTAIを必須にせず、複数Productが必要になった場合のみ横断接続する。

[Capability-derived Skill設計](../../../../docs/yi-constellation/capability-derived-skill-projections-2026-11-02.md)と[SK-01 SK-D](../../../../evaluations/SK-01-harness-skills.md)は未実装の比較計画である。

## 接続Roleと計算文脈を伴うProduct Handoff（評価用）

Product間の引用、Graph Edge、Event、データの受渡し、Command、Constraint、Observation、Evidence依存を一律の「接続」とみなさず、**Source/Role/Operator版・対象Scope・実作用・計算時点をProductの既存契約で確認する**。

- 単なるMarkdown URL・Graphvizの矢印・Skillへのリンクは、参照または形状の観測。論文取得、実Dataflow、因果、実操作権限・証拠依存を推測しない。
- `filter`による選別結果と元集団の`validate-all`、数値近似と下流の閾値Action、通知ACKと実消費／Effectを区別する。正式Operator/Role/Lawの同値性はTEI側Ownerの結果を参照する。
- Batch/Reactive/Event Stream/Async Attempt/Transactionでは、Source Snapshot、Clock/Window、重複/再送、実Grant・Body receiptが各々必要になり得る。ProductのToolが観測していない資格をTAIで補完しない。
- Productの単独Skillで充分ならそのまま利用し、複数Productの結果を共同Claimとして扱うときだけ**成立したEdgeと不足しているEdge**を伝える。非公開Edge/Actionの名称や件数もConsumerごとの開示条件に従う。

[型付きHandoff設計](../../../../docs/yi-constellation/typed-connection-handoff-and-computation-context-2026-11-02.md)／[SK-CE01〜16](../../../../evaluations/SK-01-harness-skills.md)は、正式Toolの導入・現実の権限の保証ではなく、説明と反例の計画である。

## TEIの入口をUI・Job・組織Scopeごとに選ぶ場合（評価用）

- **依頼の動詞と完成条件を先に決める**。「読む」「計画を表示」「参照実行」「業務Actionを実作用」「CLI/cron/APIから起動」「UIを拡張」「組織Scopeで閲覧」「文書を出版」は別。必要Productと実Command/Interactionを確認し、同一Skill名・画面名・標準Operation名から対象/権限を推測しない。
- **TEI単独read-only**：main統合済みのTEI `yi-tei-modeling`と実CLIが使えるなら、まずその範囲で調査できる。TAIやStudio/Wails/Job/EKIを必須にしない。Skill文書内の候補と実ロード・実CLI結果を区別する。
- **Studio**：[merged #2747](https://github.com/hat47x/tei-platform/pull/2747)の`PlanCommand/ExecuteCommand`はReference経路。`Committed=true`を外部DB/Provider Commit/Receiptにしない。UIのAction Offer・Labelと実Action Purpose/Entity ID/Target/Host Grantを分離し、未確認の操作を勝手に実行しない。
- **Function／Job／配布**：業務Function identityとBuild/Target/Triggerを別に確認する。Go単一バイナリを標準とし、複数Buildは必要な時だけ明示Mappingを持つ設計候補。実CLI/cron/Service/EKI経路が存在しない場合は未対応と説明し、`job run`等の架空コマンドを使わない。EKIのResource/Task/Attempt/Recoveryは実委任時にのみ利用する。
- **組織の可視性**：Org階層・所属・有効期間・画面可視性・参照専用・業務承認/更新権限を同一視しない。部分取得/非表示/古いReplicaの0件から業務対象不存在やAction可を宣言せず、許可されたProjectionだけを他Harnessへ公開する。
- **完了と再資格化**：Source/Role/Build/Org/Permission/Provider/Timeのうち実際に依存するものを必要な時点で再照合。Preview、Plan、Reference Execute、Provider Effect、Receipt、Consumer Read、品質期限は別Claim。UI書式変更だけで無関係なAccepted Meaningを失効させず、意味/Authority変更は旧PASSのまま流用しない。

出典と反証：[入口別SK-IV01〜12](../../../../docs/yi-constellation/skill-entrypoint-ui-job-organization-boundaries-2026-11-03.md)、[SK-01 §AC](../../../../evaluations/SK-01-harness-skills.md)。**これは試作Skillの利用手順**であり、新UI Extension API・複数Build Tool・Business Host認可・実Product/Harnessの動作実証ではない。
