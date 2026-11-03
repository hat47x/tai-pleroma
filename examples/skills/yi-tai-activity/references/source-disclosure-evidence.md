# Source・Tool・受渡し・開示の証拠境界（必要時だけ参照）

> **評価資料・Product実動作未受理**。このファイルは[TAI Activity Skill](../SKILL.md)が必要な場合にだけ参照する詳細手順。旧rootの該当節を省略せず分離した。製品Skillの実ロード・実Tool呼出し、Host Grant/Disclosure/Owner意味受理を保証しない。

## Skill・Toolの実体と開示に関する追加注意（評価案）

- **能力の説明と実能力を区別**する。Skillの名前や説明、CLI/MCPの一覧は候補発見にすぎない。実際に利用できるTool、Toolの版、当該SessionのHost資格を確かめ、確認できない項目はunknownとする。
- **実ロードを推測しない**。配布・参照したroot Skill文書のdigestが一致しても、参照先の資料・Script・MCP Toolの内容や、実際にHarnessへロードされたbyteは同一と限らない。観測できる範囲だけを利用記録として示す。
- **発見の段階でも開示制限を守る**。外部へ返すSkill/Tool名・一覧、引数Schema、Error、件数、拒否理由が機密になり得る。公開可否はSource保持Product/Hostの実Policyに従い、Skillの記述で権限を増やさない。
- **隠れたSourceの真偽を創作しない**。同じ開示投影から内部全体の問いに異なる答えがあり得る場合、元Productによる許可済みの限定検査か、根拠不足のまま扱う。内部検査のYes/No自体が非公開の場合、結果開示を要求しない。
- **TEI単独等の正規入口を尊重**する。Product自身のread-only Skillで完結する仕事にTAIや別Productを必須化しない。TEI #2605のCLI操作は実環境で検証したものだけを利用し、validateのexit 0を意味受理に昇格させない。

これらは動作済み安全保証ではなく、[SK-01 SK-E01〜07](../../../../evaluations/SK-01-harness-skills.md)で反証するための手順案である。

## Source改版・生成物を他製品へ渡す場合

- Sourceの現在版（S）、版間の対応**候補**（C）、Ownerが受理した意味（M）、導出結果・Generator/Template版（G）、完成した一式の公開とConsumerによる実読取り（P）は別の証拠。A→B→Cの候補経路があってもA→Cの意味同値・旧受理の再利用を約束しない。
- 文書・ライブラリ・複数ファイルの成果物について、Manifest/Digest/生成コマンド成功だけで同一世代の一式を利用者が取得したと断定しない。実Productに世代固定・ファイルbyte照合の入口がない場合、公開の整合はunknownとして各Product Ownerへ返す。
- EKIのTask/AttemptでResultClaimやACKを確認できても、同一Attemptの出力Bodyが送達されたか、AcceptedResult・外部Effectが得られたかは別に報告する。見えないBodyを補作・再実行しない。
- 参照先のSourceやManifestが非公開なら、存在することや件数を推測しない。必要な事実の照合は、許可された保持Productの内部検査を利用する。

この注意は[SK-01 SK-J](../../../../evaluations/SK-01-harness-skills.md)の未実施反例に基づく**評価用指針**であり、任意のTEI/SHO/EKI Productに新しいToolや実行権限を与えない。

## 現在のTrust・設定読取り失敗を伴うSkill接続（合成評価指針）

- Skillをインストールできたこと、古いHarnessで接続できたこと、現行Issuer/Grantを確認したこと、実Providerへ作用できることを分ける。**認証の最終判断は現在のHost/各Product側**へ委ね、TAI SkillからmTLS/Trust Bundle/Owner Authorityを再実装しない。
- Source側の導入状態が**明示的な未導入（Ownerが旧互換方式を許可した場合）**なのか、**導入済みだが読取り障害・レコード不正・履歴喪失**なのかを消さない。後者を「未設定だから通す」に変換せず、適切なProductのUnavailable/Denied結果へ引き継ぐ。
- SHA等のDigest比較では**対象byteとアルゴリズムを確認**する。両側が同じ関数で生成した一致値は独立Oracleではない。Issuer Fingerprint／Skill Bundle／Source／ArtifactのDigestを同じ信頼資格にまとめない。
- 他Harnessへ再開する際は、旧Skillの内容一致やTask受付履歴を現在の機密Source開示資格・実行Grantへ昇格させない。権限確認が不足する作用は保留し、実権限のある非機密の調査や文書下書きを継続可能とする。

本節は[SK-01 SK-TB01〜09](../../../../evaluations/SK-01-harness-skills.md)の合成比較計画であり、EKI #433/#466/#467の製品修正・実mTLS合格や現在の外部ハーネス接続を保証しない。

## Data取得・Rule依存・Planner開示の手順案

ProductにData/Rule/ProviderのEvidenceがある場合は、**何を要求したか**（Function Data ContextとRule Dependency）、**実Requestが何を要求したか**、**どの範囲を実際に読んだと観測できたか**、**目的Claimを評価できるか**、**どこへ開示できるか**を別々に確認する。実ProductにTraceがなければ取得量を推測で断定しない。

- Display Mapping外のDataをRuleが必要とする場合、受理済みRule DependencyをProduct側で調べる。Ruleを評価するために秘密入力が必要でも、外部Harnessが無断でその原値や判定Booleanを要求・取得しない。Product内で評価でき、かつ結果公開が許される範囲を利用する。
- `all`という取得宣言は、実観測したResultの完全性とは異なる。別Source/時点/epochのReadを統合する場合は、Product側の同一Snapshot根拠がなければ結合Claimを未確定として保持する。
- Tool/Skillの存在・候補・非公開Field名・拒否理由自体が開示対象になり得る。外部Plannerに非公開のProvider/Actionの有無を直接使わせず、許可済みの公開Capability/Toolから作業を構成する。
- Toolがread-onlyでも、LLM/APIへの外部送出許可は別。実Host/NetworkとConsumer Policyによる送出証拠を参照する。Rule Preview/Method提案/Claim ACKと外部Action完了も区別する。

これは[SK-01 SK-F](../../../../evaluations/SK-01-harness-skills.md)の反例用の作業指針。TAI SkillがTEI Rule Engine、SEI Inquiry、OS非干渉監査や新Capabilityを実装した事実ではない。
