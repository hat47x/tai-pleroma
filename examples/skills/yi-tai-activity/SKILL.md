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
