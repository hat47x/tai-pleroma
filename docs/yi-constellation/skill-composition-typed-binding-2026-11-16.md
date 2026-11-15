# YIC Skill構成：型付き接続・資格境界・実行時再確認（2026-11-16）

**状態：設計案・既存受入計画への引渡し。新しいSkill Router、Product API、型変換Provider、実Harness試験、Owner意味受理はNOT RUN。**

参照：[YIC Skill/Plugin計画](harness-skill-plugin-plan-2026-11-02.md)／[型付きConnectionと計算文脈](typed-connection-handoff-and-computation-context-2026-11-02.md)／[Skill最小構成シナリオ](skill-composition-minimal-routing-scenarios-2026-11-02.md)／[Skill実利用資格](skill-knowledge-use-qualification-2026-11-15.md)／[Product間Handoff実行票](cross-product-handoff-execution-tickets-2026-11-11.md)。

## 1. 問題と設計上の決定

YICで構成すべきものは、Skill文書の単なる連結でも、CLI/MCP Toolの名前だけをつないだフローでもない。利用者の目的に対して、**利用可能な製品能力と必要な手順を選び、型付きの値・根拠・実行結果を、それぞれのOwnerが受理する条件で受け渡す**構成である。

次の四区分を、同じ実装階層や排他的な種類として扱わない。

| 利用形態 | YICの責務 | 実際の正本 |
| --- | --- | --- |
| Product-only | Skillや外部Harnessを介さない直接利用を妨げない | Productの機能、認可、意味、検証 |
| Tool-only | 実在するCLI/API/MCPの呼出し方法と現在の可用性を確認 | Tool提供者と実Host |
| Product Skill | 製品固有の作業の進め方、能力選択、結果確認の手順 | Product側が管理するSkillの原文・参照・対応版 |
| TAI横断Skill | 複数Productを使う目的、未決、引継ぎ、再確認を構成 | TAIのActivity/手順。業務意味や実行権限は所有しない |

基本形は「目的 → 必要能力の選択 → 型付き接続候補 → 実行時資格の確認 → Product/Hostによる実処理 → 受領・証拠の検収」。不要なSkillや製品はロードしない。Tool-onlyで足りる作業にTAI横断Skillを必須にしない。

## 2. 接続を三段階に分ける

**A. 手順の接続（Skill Composition）**：何を調べ、何を判断し、どのProductに委ねるか。成功を宣言するのではなく、途中で必要になる能力・未決事項・停止条件を記述する。

**B. データの接続（Typed Port/Mapping）**：Productが実際に公開する入出力Contractを使い、値をどの粒度で受け渡すかを定める。構造全体を接続してもよいし、項目ごとに接続してもよい。異なる型の間では、実在する明示的なAdapterを使用する。Adapterは変換前後の型、NULL・欠損・多重度、順序、精度、失われる情報を説明できなければならない。**接続線が描けることと、変換が実行・受理されたことは別**。

**C. 証拠・資格の接続（Evidence/Authority）**：実Source、意味、実Tool、現在Grant、Consumer受領のうち、どれが実際に成立したかを残す。入力型が一致しても、Scope・時間・権限・根拠のない別製品への転送は認めない。

Bの構造適合はCを証明しない。逆に、Cの履歴Receiptが存在しても、新たなBの値・現行Source・別Audienceへ自動的に有効化できない。接続の種類は既存TEI標準構造／Owner側の意味解釈を参照し、YIC独自の中央Graph、Schema Registry、Policy Engineを採用しない。

## 3. 一つの接続を確認する最小情報

下表は**受入票の比較列**であり、正式なYIC共通Manifestや新DSL構文ではない。実行環境が提供しない列は未確認として残す。

| 領域 | 確認するもの | Owner |
| --- | --- | --- |
| 目的 | Task、Activity、用途、Audience、要求する成果 | 利用者／TAI |
| 能力 | Product/Capabilityの実在、版、Tool/Commandと必要引数、実環境での可用性 | 各Product／Harness |
| 入出力 | Input/Output型、Field/Whole型接続、NULL/欠損/Bag/順序、Scope/Grain、実Adapter | 各Product／TEI等の型・意味Owner |
| Source | Subject/Occurrence、revision、実Read、完全性、依存、epoch | Sourceを保持するProduct |
| 実行 | 選択したOperator/Provider/Host、実Binary/Tool、Attempt、現在の許可とEffect分類 | Product／Host |
| 受領 | Result/Error、実際に利用したRead Footprint、出力Body、Consumer実Read、独立Expected | Product／Consumer／既存検証Owner |
| 継続 | 変わったSource/Tool/Grant/Consumerと、再確認を要する辺、未確定の辺 | TAI #271と各Owner |

特に、型の同一性は業務意味の同一性ではない。同じ数値型でも通貨・単位・精度・評価時点・粒度が異なれば、別の意味判断が必要である。また、同じ名前のCommandが別のPlugin/Operator実装へ束縛された場合には、表示名が一致するだけで旧資格を再利用しない。

## 4. コンパクトな構成例（実在APIではなく設計上の例）

例：利用者がTEIでモデルの根拠を確認し、SHO文書へ採用候補として差し込む。

1. TAI横断Skillは「モデルを調べ、Source付きの候補を提示し、文書への反映前に確認を得る」という**手順**を記述する。
2. TEIのProduct Skillは、実環境で発見されたread-only Toolから、対象ID・型付き結果・Source参照・既存の検証状態を取得するための手順を示す。実Toolが無い場合は架空のCLI名を補わない。
3. SHOのProduct Tool/Skillは、SHOが受け付ける文書候補型に対し、必要な項目を明示Mappingする。TEIの結果構造がそのまま対応すればWhole接続、必要項目が限定されればField接続、異なる意味構造なら明示的なAdapterの検査を要求する。
4. **候補Preview**と**実文書保存**を区別する。保存を要求する際は、SHO/Hostによる現行権限・Source occurrenceの再解決・未保存編集の保護と実受理が別途必要である。
5. TAIはProductが返した受領段階をActivityに対応づける。TEIのRead成功をSHOへの書込み成功としない。EKIのACKをBody受領や納品としない。

Product単独で同じ結果を得られる場合は、TAIを経由しない構成を優先候補に残す。TAI横断Skillの増分価値は別の比較試験で判定する。

## 5. 接続時点と使用時点を分ける

| 段階 | 合格させる範囲 | 次段階へ自動昇格させないもの |
| --- | --- | --- |
| D0 選択候補 | Taskに合うSkill/Tool/Capabilityの候補 | 実在、現在利用可能、権限 |
| D1 静的接続 | 実Contractの型・Mapping・Adapter条件に一致 | 実Read、実行、意味受理 |
| D2 実Source確認 | 選択したSource/Field/Scope/Read/時点の実Reply | 全件、別用途への開示、現在Grant |
| D3 実行直前 | Product/Hostの現在のTarget/Binding/Grantと前提条件 | 実Effect・原子性・完了 |
| D4 実行後 | 実Attempt/Result/Error/Effect Receipt/Body | 別Consumerへの到達、業務完了 |
| D5 Consumer | Consumerが現物を読み、必要な構造・順序・値を照合 | 別Audience・別時点・他の成果物 |

D0〜D2が成功しても、D3でSource変更やGrant失効を確認したら作用を中止する。D4の記録はD5の代用にならない。途中失敗・部分結果・実行したか不明な場合に、Skillの判断だけで再実行・補償・成功申告を行わない。

## 6. 既存評価へ渡す反証カード（新Checkerは作らない）

| ID | 対象となる誤り | 期待判定と引渡し先 |
| --- | --- | --- |
| YK-COMP-01 | Tool-onlyで足りる公開ReadにProduct/TAI Skillを常時ロードする | B0/B1/B2で正答・保留・追加Tool/Tokenを比較。TAI #168/#488 |
| YK-COMP-02 | Whole構造が一致したので必須Fieldの欠損、NULL、Bag/順序を無視 | D1保留。TEI #988/#2620、既存SK-CE |
| YK-COMP-03 | Fieldを個別に結線したが、Source/epoch/Grainが異なる | 共同Result・全件のClaimを保留。TEI #2586、TAI #271 |
| YK-COMP-04 | Adapterが数値精度・単位・順序・属性を黙って落とす | Adapter適合未成立。TEIの型/意味Ownerへ |
| YK-COMP-05 | Plan確定後に選択Operator、Source、生成Artifact byteが変わる | 旧Plan/旧Receiptを現在資格へ昇格しない。TEI Build/Operator Owner、TAI #271 |
| YK-COMP-06 | Read-only Skillの説明からWriter/外部送出の許可を推定 | D3で停止。Product/Host/TAI #232 |
| YK-COMP-07 | 旧SUI Consumer FAILを新PASSと扱う、または旧Receiptを上書き | D5の新Attemptを要求し歴史的FAILを保全。TAI #271、SUI Consumer Owner |
| YK-COMP-08 | Tool Replyが成功風のJSONだがExit非0、DiscoveryのScope/引数が不適格 | D0/D2未判定。既存Skill drift checker、TAI #488 |
| YK-COMP-09 | Skill文書のリンクだけで出典の実Read・Product意味受理を宣言 | Sourceと受入を別確認。各Product、TAI #488 |
| YK-COMP-10 | 別HarnessへResumeしたとき古いGrant/Skill Loadを流用 | 変更依存を選別再確認。TAI #271、既存SK-03 |

これらは既存[SK-01](../../evaluations/SK-01-harness-skills.md)の型付きConnection/最小構成、[SK-C](../../evaluations/fixtures/SK-C-continuation-requalification.synthetic.json)の再資格化、既存の[Skill選択Checker](../../integrations/tools/skill_selection_check.py)へ割り付ける**受入候補**である。固定評価指標や封印Expectedの書換え、新規Router/Checker/中央Authorityを正当化しない。

## 7. 実行順と停止線

**P0を増やさない。** 最優先は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の既定実OS G0→G1→G2と外部Harness独立H2/H3四Slot。既存文書で比較適格0/4とされる未完了部分を、今回の型付き設計で合格にしない。TEIの非Plugin Windows Stage1→Stage2は別P0。

**次に一件だけ実接続する。** TEIの既存read-onlyの実Outputを、選択した二番目のProduct/Consumerの実Inputへ、型・Source・Attemptを明示して渡す。まずTool-onlyで、次に必要なProduct Skillを追加する。両者の実効果・費用を比較し、TAI横断Skillは中断再開・再資格化が必要なTaskでだけ追加する。

**実施後のOwner判断。** D1/D2/D5の失敗がどこで観測できるか、既存TEI/SHO/SUI/EKIの契約と検査で足りるかを先に確かめ、不足が具体化した場合にのみ各ProductのIssueへ最小変更を提案する。新しい標準型・Plugin Contract・Protocolを先に採用しない。

**今回の到達範囲：** GitHub上の既存設計と受入条件を接続した文書案。実Tool/OS/Provider/Windows、外部AI Session、実Consumer再実行、Ownerによる意味受理は**NOT RUN**。
