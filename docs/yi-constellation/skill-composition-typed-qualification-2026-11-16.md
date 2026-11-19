# YICのSkill構成：型付き接続と利用資格の検証仕様（2026-11-16）

**状態：設計・試験への引渡し。** この文書で定めるのはYICの横断的な接続判断と、既存Ownerが返す証拠の検収方法である。共通の実行器、型変換器、Registry、認可機構、新しい製品APIは採用しない。実Product間の接続試験・外部Harness比較・意味受理は別に確認する。

関連：[Skill/Plugin全体計画](harness-skill-plugin-plan-2026-11-02.md)／[最小Skill構成](skill-composition-minimal-routing-scenarios-2026-11-02.md)／[型付きConnection](typed-connection-handoff-and-computation-context-2026-11-02.md)／[実利用資格](skill-knowledge-use-qualification-2026-11-15.md)／[Product間Handoff実行票](cross-product-handoff-execution-tickets-2026-11-11.md)。

## 1. 設計判断：Skillではなく、必要な能力から組み立てる

YICの仕事は、Skill文書をできるだけ多く読み込むことでも、独自の万能Tool Routerを設けることでもない。利用者の目的と現在の条件に合う**実在するProduct能力**を選び、必要なら作業手順としてSkillを加え、製品間の値と根拠を正しく受け渡すことである。

| 利用形態 | 使う条件 | どこが正本か |
| --- | --- | --- |
| **Product-only** | Product単体で目的を達成できる | Productの実装・意味・認可 |
| **Tool-only** | CLI/API/MCPの直接呼出しだけで十分 | Tool提供元と実Host |
| **Product Skill** | 専門的な順序、失敗時の判断、出典確認などの手順が有効 | 各ProductのSkill本文・参照・対象版 |
| **TAI横断Skill** | 複数Product間の目的・未決・Activity継続・再資格化が必要 | TAIの横断手順。各Productの正本を代行しない |

この四つは相互排他的な技術レイヤーではなく、**利用者の仕事に対する選択肢**である。Product Skillを追加しても新しいCapabilityや権限が生じるわけではない。TAIを使うこともProduct-onlyの経路を無効にしない。

採否は「正答／妥当な保留」「不要なTool・Skillの利用」「Sourceの現在性」「開示・作用の過不足」「時間・Token・人の確認負担」を別に測る。既存のB0（Tool-only）／B1（Product Skillあり）／B2（TAI Skillも使用可能）の試験を再利用し、少数の成功例から一律の最適構成を決めない。

## 2. 接続には三つの意味がある

1. **手順の接続**：誰が、何を、どの順序で調べ・確認・提案するか。Skillの担当はここが中心。作業計画が存在しても、Toolの実行やProductの結果を示さない。
2. **値の接続**：Productが公開する入力・出力と、型・Mapping・変換を対応付ける。TEIの標準Data/Semantic Type、Connection、Operator/Providerの既存契約を利用する。Skillが第二の型・意味正本を作らない。
3. **証拠と権限の接続**：Sourceを実際に読んだか、どの実装を呼んだか、利用時点のGrantが有効か、結果がConsumerへ届いたか。それぞれProduct/Host/Consumerの実観測で確認する。

この三つを単一の「接続済み」状態へ畳まない。図上の線は構成候補、型が合うことは構造上の適合、実Tool Replyは一試行の観測であって、業務上の受理や別Audienceへの開示資格ではない。

## 3. 型付きI/Oの接続は「粒度」と「変換」を独立に選ぶ

[TEI #5101](https://github.com/hat47x/tei-platform/pull/5101)で設計された二軸を、YICが**呼出し側として利用**する。新しいYIC Port Schemaは設けない。

| 受渡しの粒度 | 無変換 | 明示Adapter |
| --- | --- | --- |
| **複合型を一括** | 実Contractで適合が成立する場合のみ全体を渡す | 全体を別の実Contractへ変換。機密Field・順序・欠損を確認 |
| **Fieldを個別** | 必要な項目だけを対応付ける | 項目ごとに単位・精度・NULLなどを変換 |
| **混合** | WholeとFieldの接続範囲を明示 | 必要な一部だけAdapterを通す。二重Bindingを拒否 |

型が一致しても、業務上の単位、通貨、桁・丸め、母集団、Grain、Collectionの多重性・順序、GraphのIDと方向、NULL／未取得／Unknownが一致するとは限らない。「型を合わせたので意味も同じ」とはしない。

Adapterを挟む場合は、**どの値が失われるか**を示す。Wholeで必要のない非公開Fieldまで送ること、WholeとFieldを二重に束縛すること、Fan-outを複数の副作用付き実行へ無断変換することは不合格。Node Viewでは同じ接続を折り畳み・展開表示できても、表示操作を実Provider変更とみなさない。

## 4. 構成時点と使用時点の確認点

下記は既存Productの受入票を照合する**観測点**である。新しい共通状態機械や製品Gateの追加を意味しない。

| 観測点 | 確認すること | これだけでは証明しないこと |
| --- | --- | --- |
| **D0 候補** | 必要なSkill・Capability、実Toolの発見範囲・名称・引数 | 未発見Toolの不存在、実Load、実行権 |
| **D1 接続** | 入出力型・Whole/Field Mapping・Adapter・損失条件 | Source実Read、Ownerの意味受理 |
| **D2 資料** | 実Source・Occurrence・版・範囲・Read Footprint・完全性 | 現在Grant、別用途への開示 |
| **D3 作用直前** | 現行Operator/Provider/Target/Binding、Host側の現在Grant、必要なOwner判断 | 処理完了、永続化、外部効果 |
| **D4 実行結果** | 実Process/Tool/Attempt、結果・エラー・Effect Receipt・Bodyの同一性 | Consumer到達、業務完了 |
| **D5 消費側** | 実Consumerが受領・読取り・必要値/順序/出典を照合 | 別Audience・後日の再使用資格 |

D0の限定read-only Discoveryは製品の全Commandを列挙しない。D2で0件を取得しても「全件なし」とは限らない。D3に進む際、Skillの説明やMCP annotationを権限として扱わない。途中で実行結果が不明になった場合、Skillの判断だけで同じ業務作用を再送しない。

D4の単なるResult値一致も十分ではない。[TEI #5118](https://github.com/hat47x/tei-platform/pull/5118)の限定試験では、直接評価と生成Goの値が同じでも**実Read先のIDが違えば不一致**と判定する。これはテスト用Sourceによる限定実証であり、正式DB Provider・現在Grant・外部Consumerの同値性を示すものではない。

## 5. 変更があったときに再確認するもの

**Sourceと生成物**：[TEI #5109](https://github.com/hat47x/tei-platform/pull/5109)／[#5129](https://github.com/hat47x/tei-platform/pull/5129)は、BuildPlan確定後の生成Go変更と同梱原Markdown変更を、それぞれ旧Planのままでは拒否する回帰を製品に追加した。元byteへ戻ったとしても、それだけで旧Host Grantや業務意味の受理が復活するわけではない。

**実装選択**：Operator A→Bの選択はWorldの見た目やResult値が同じでも別資格になり得る。TEIの**現行mainには**、Scenarioの`OperatorSelectionSHA256`と、選択を変えた旧生成Commandの拒否を試す`TestGeneratedScenarioCommandInvalidatesOperatorSelectionChange`が存在する。これは組込みOperatorを使った限定的なCLI／Planの証拠であり、正式Plugin Lock、実Provider呼出し、A→B→Aの履歴資格までを保証しない。旧[#5114](https://github.com/hat47x/tei-platform/pull/5114)自体は未マージでクローズされたが、そのPR番号だけから現行機能の不存在を推測しない。計算定義の一本化を進める[#5150](https://github.com/hat47x/tei-platform/pull/5150)は確認時点ではopenであり、提案内容を実装済みの追加保証へ加算しない。

**SUIの出典**：SUI [#3464](https://github.com/hat47x/sui-sensemaking/pull/3464)は保存済みCard選択候補と現行Document Revision Headを、Source Raw取得前に照合する。旧[#3465](https://github.com/hat47x/sui-sensemaking/pull/3465)自体はクローズ・未マージだが、同じ変更は別の[mainマージコミット`71b13d`](https://github.com/hat47x/sui-sensemaking/commit/71b13d2966a3eb29ca61870dc12514a3657ffa7b)として存在し、Raw取得後のDocument再認可・Card再解決・Revision照合は**限定内部経路に実装済み**。さらに[main #3467](https://github.com/hat47x/sui-sensemaking/pull/3467)では、保存済みCard出典の再読経路でRaw取得後のSource Authority／PolicyRef再解決と二度目のSource専用PDP判定を追加した。**一般Source読取にはこの二重判定を適用しない**。選択Resolverや正式Source Provider等はテストダブル／未受理を含み、同一Commit CAS・原子的権限保証・別Productへの開示が成立したわけではない。

**SUIの投影と保存**：[SUI #3466](https://github.com/hat47x/sui-sensemaking/pull/3466)で、`from_artifact`は参照を作る読取経路、`to_documentv1_payload`は契約確認用に限定し、`documentv1_save_plan`と`documentv1_merge`をRoute/MCP/CLIへ接続しない方針がmainに統合された。したがって「TEIからSUIへ型が合うArtifactを渡せる」ことを「SUI文書の保存ができる」と説明しない。SUI文書への保存を要求する場合は別のOwner判断・ADRが先。

**Harnessを跨ぐ再開**：TAI [#271](https://github.com/hat47x/tai-pleroma/issues/271)の選択的再資格化を使う。以前のSkill Load、SourceのRead、Grant、ACKを他のSessionへそのまま移植しない。Activityが同じでも実Sessionの継続、資料の現在性、外部送出、Consumer受領を分ける。

## 6. 最初の縦断は「読取→参照」に限定する

初回の構成は、**TEIの公開read-onlyモデル調査と、SUIまたはSHOの実在する読取専用Consumer**を候補とする。受取側のTool/Endpoint、型、Source/Authorityが実在することを確認してから組み合わせる。ない場合はTool-onlyの結果で止め、架空の連携APIを設計上の便宜で呼ばない。

1. 公開Workspaceを固定し、まずTEIの実CLIのみで対象とSource位置・警告・未決を取得。
2. D1の型・Mappingを実Contractと照合。D2で元Sourceと実Read範囲を確認し、許可された最小Projectionだけを渡す。
3. 受取側の実Consumerが値と順序、必要なSource参照を読んだことを別Attemptで確認。参照の表示と保存／編集／納品は分ける。
4. 同じTaskをB0 Tool-only、B1 Product Skillあり、必要な場合にだけB2 TAI横断Skillでも試し、品質・過剰な呼出し・費用・再説明の手間を比較する。

これは最初の適格なH2/H3四Sessionの実証を置き換えない。TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)の実OS読取隔離→実送出→Tool Reply完全性→事前固定の独立H2→H3→H3→H2を先に成立させる。既存記録の比較適格**0/4**を、本設計の作成や合成Checkerの成功によって変更しない。TEIの非Plugin Windows Stage1→Stage2実セルフビルドも別P0のまま。

## 7. 既存試験へ渡す反証カード

以下は**試験候補**であり、新しい判定エンジンや合格結果ではない。

| ID | 反例 | 既存Owner・期待する判断 |
| --- | --- | --- |
| **YK-COMP-01** | Toolだけで済む調査へSkillを常時追加 | TAI #168/#488：B0/B1/B2で正答・保留・費用の差を測る |
| **YK-COMP-02** | Whole接続で未許可Fieldを送出 | TEI #5101／TAI #232：必要な型・ScopeとDisclosureを分けて拒否 |
| **YK-COMP-03** | WholeとFieldを同じ対象へ二重にBind | TEI #5101：Mappingの重複と意味上の競合を拒否 |
| **YK-COMP-04** | Adapterが単位・NULL・順序・多重度を無音で変換 | TEI #988/#5101：損失と独立Expectedを照合 |
| **YK-COMP-05** | 同じ値でも実Read先のFieldが違う | TEI #5118：値とRead Footprintを別に比較 |
| **YK-COMP-06** | Plan後に原Markdown／生成Goが変わって旧PlanでBuild | TEI #5109/#5129：旧PlanとArtifactを拒否 |
| **YK-COMP-07** | A→B→Aで元文言が戻ったので旧Card選択を再受理 | SUI #3464：現在のDocument Revisionを照合 |
| **YK-COMP-08** | SUI参照投影をWriterにつなぎ保存成功と説明 | SUI #3466：読み取りと保存を分離し、採用していない経路を呼ばない |
| **YK-COMP-09** | 限定DiscoveryにないCommandを不存在と断定 | TAI #488／既存Skill Checker：未判定に留める |
| **YK-COMP-10** | 旧Source Grant・Skill Load・Receiptで別HarnessへResume | TAI #271：現在の必要な依存だけ再確認 |
| **YK-COMP-11** | Tool ReplyをConsumer受領・外部効果とみなす | TAI #271／EKI/SHO Owner：Attempt、Body、実Readを別観測 |
| **YK-COMP-12** | 構造一致をOwner意味受理・実Provider権限へ昇格 | TEI #2514/#1180・TAI #488：D1とD3/D5を分離 |

## 8. 計画上の採否と実行順

- **採用する設計判断**：最小限のSkill選択、三種類の接続、Whole/Fieldと変換の二軸、D0〜D5の観測点、変更時の選択的再資格化。
- **採用しないもの**：新しい共通Router／Host／型Registry／権限正本／Skill用Build System／共通Expected、全Skillの常時Load、図上の線からの実行や保存の自動推定。
- **P0を維持**：TAI #168の独立H2/H3、TEIのWindows Stage1→Stage2。
- **P1**：最初の適格な実Tool-only→二Product読取Consumer、B0/B1/B2の増分比較、実Read/出典と型Mappingの照合。
- **P2**：別HarnessでのActivity再開、Selective Requalification、必要が証明されたAdapterの実装・検証。権限と実作用は各Product/HostのOwnerが決める。

**今回の検証上限**：既存PRと設計の静的照合。新しい外部Harness、実OS、実SUI/SHO Consumer、Provider／Grant／Effect、Owner意味受理を実行・実証したものではない。

## 9. Skillが案内できる実現方式は、Rule種別・現在の製品版ごとに判定する

[TEI #5166](https://github.com/hat47x/tei-platform/pull/5166)は、同じMarkdown内のDataとRuleをProduct Reader／Inspectorで選べても、そのRuleをすべての実現方式へ展開できるとは限らないことを具体化した。YICは「製品が使える」という総称を、実際のTaskで選ぶRule・入力・実現方式・Provider・Hostの資格へ分解する。これは新たなCapability Registry/APIを定めるものではなく、既存Productの検証結果から作る**利用案内の比較票**である。

| 実対象・方式 | 現行mainで確認できる範囲 | YICが主張してはならないこと |
| --- | --- | --- |
| 正値の数値Rule／P（直接評価） | 既存Evaluatorで局所評価。値と実Read IDを独立に比較する限定回帰がある | 正しい値が返ったので実DBの全件を読んだ |
| 正値の数値Rule／G（Go生成） | 選択した種類について局所生成・別Process実Binaryと、限定的な通常CLI Self-buildの試験がある | 全Rule、全Provider、全Targetで同一意味・同一Effectを保証する |
| 暦日の`not-after ... if present`／P | Workspace Readerと型検査、同日・日付順序・NULL・未取得を区別する直接評価の回帰がmainにある | 業務Ownerの意味受理、実DBからの取得状態、正式Host権限が成立した |
| 同じ暦日Rule／G | **未対応**。`unsupported generated kind`として生成を拒否することが試験に明記されている | Gが使えないのでPへ黙って切り替え、Gによる成果物を作成したと報告する |
| 関係の期間重複Rule、Contract Query行からの状態Reader | [#5148](https://github.com/hat47x/tei-platform/pull/5148)／[#5149](https://github.com/hat47x/tei-platform/pull/5149)はmainへ統合済み。期間RuleとSQL Executor後の状態Readerは局所試験の範囲で存在するが、正式な全件宣言／通常製品Runへの接続は別 | mainの正式Rule・実Provider入口・全件読取が完成したと扱う |
| Typed PluginのWhole/Field投影 | [#5101](https://github.com/hat47x/tei-platform/pull/5101)は設計をmainに導入。[#5156](https://github.com/hat47x/tei-platform/pull/5156)のpure Transform回帰はmainに統合済み。Wholeは追加Fieldも保持し、明示2 Field投影は余分なFieldを落とすが、公開可否の認可を代行しない | 実Port接続、未公開Fieldの自動排除、現在Grant、非Builtin Providerを検証済みとする |

P（直接解釈）、G（コード生成）、D（既存実装への委譲）を、**Rule種別に対する能力候補**として扱う。選択した方式が不適格なときは理由を残して保留し、別方式へ変更したい場合は新しい選択として再検証する。ユーザーが要求した成果物が「生成Go」なら、Pの成功だけで生成完了としない。HostのWails／CLI／MCP入口も実現方式とは別軸であり、同じProduct名を根拠に可搬性を推定しない。

## 10. 「判定できない」と「実行できない」の理由を混ぜない

[TEI #5142](https://github.com/hat47x/tei-platform/pull/5142)の限定的な三値Rule判定は、取得済みの値・NULL・未取得、関係が完全か部分取得かを区別する。例えば一意性の検査では、読んだ二行に確実な重複があれば、残りが部分取得でも不成立と判断できる。一方、読んだ範囲に重複がないだけでは、部分取得の集合全体が一意とは判断できない。

この意味上の判定と、Product/Hostの呼出し結果を分ける。

| 状況 | YICの取扱い |
| --- | --- |
| Ruleに必要な値が明示NULL、または未取得 | ProductのRuleが定める三値・理由を保持する。NULL＝未取得、未取得＝不成立にしない |
| 部分取得でも決定的な違反を観測 | Productが根拠付きで不成立と判断した範囲のみ伝える |
| 部分取得のためRule結果が変わり得る | `undecided`と理由・取得範囲を保持する。0件・正常終了から全件適合を推定しない |
| HostがReaderを拒否、PDPが失効・障害 | **認可／可用性の失敗**。業務データのNULLやRuleの`undecided`に偽装しない |
| 選択した実現方式が未対応 | **当該方式のunsupported**。別方式の利用可能性は別の候補で確認 |
| Tool応答が失敗、または途中で途切れた | **実呼出しの失敗／受領未確認**。応答中の成功風JSONや過去Receiptを採点に使わない |
| Effectの結果が不明 | Product/Host/EKIの同一Attempt記録を確認するまで保留し、Skillだけで再送しない |

D0〜D5の観測点には単一の「成功」を追加せず、**どの観測点について、何が成立し、何が不明か**を既存Receipt・Task記録で表す。YICの説明文がProductの意味判定、Source/DisclosureのAuthority、またはConsumerの独立Expectedを代替しない。

## 11. 実際のSourceを読んだあとにも残る利用資格の確認

SUIの現行mainでは、保存済みCard出典の限定経路に、次の順序が実装されている。①現在のDocument read判定と選択・Revision照合、②現在のSource Authority／PolicyとRaw read判定、③実Raw・選択byte照合、④**Source Authority／PolicyRef／PDPの再照合**、⑤**Document read・Card選択・Revisionの再照合**。これらの失敗時にはRawを外部へ返さない。

ただし、これは保存済みCardを復帰する**特定の内部入口**であり、一般Source APIや正式なProduct Source Providerの全操作を覆うものではない。二度の一致確認は原子的な同一Snapshotを意味せず、再確認後の失効、短時間のA→B→A、同じRaw byteを持つ別Root／Occurrence等の未確認は残る。[SUI #3466](https://github.com/hat47x/sui-sensemaking/pull/3466)の読取投影と保存禁止の区別も維持する。

YICが別Productへ渡すHandoffの受入票には、**実Callの開始時点のScope/Grant、返却前に再確認した範囲、Consumer別Disclosure、別Processで実際に受け取ったBody**を別欄で残す。どれか一つが成功しても、すべての欄を成功へ昇格しない。原文や非公開Policy Refを横断の一般Skillへ持ち出さず、既存Productが公開を許可した最小Projectionだけを渡す。

## 12. 既存Ownerへ渡す追加反証と実行順

| 反証ID | 一因子の変更・誤推定 | 既存Ownerと期待判定 |
| --- | --- | --- |
| **YK-COMP-13** | RuleをReaderが受理したのでGも対応しているとする | TEI #5166：暦日`not-after`はP可／G未対応を別々に表示 |
| **YK-COMP-14** | G未対応を黙ってPへ切り替えて「生成済み」と報告 | TEIのG/P/D契約・TAI #488：実現方式と成果物資格を失効／保留 |
| **YK-COMP-15** | partialな一意性Readで違反なし→全件成立と断定 | TEI #5142／TAI #271：未取得範囲の判定不能を保持 |
| **YK-COMP-16** | partialでも確定した違反まで`undecided`に変える | TEI #5142：独立Expectedに従う不成立を保持 |
| **YK-COMP-17** | Source PDP拒否をNULL・未取得・Ruleの`undecided`に変換 | SUI #3467／TAI #232：Authority拒否を別資格で止める |
| **YK-COMP-18** | 古いPR #3465が未マージなので、mainのRaw後再照合も存在しないと断定 | SUI main実コード／TAI #488：同内容の別Commit採否と入口範囲を確認 |
| **YK-COMP-19** | Operator選択Pinが存在するので、全Plugin実CallやA→B→Aの履歴も保証すると断定 | TEI Scenarioの現行実試験／TAI #271：局所CLI PinとProvider/Historyの資格を分離 |
| **YK-COMP-20** | Pinned Cardでの二度目のPDP successから、一般Source APIも原子的に保護されたと断定 | SUI #3467／TAI #232：入口限定・未検証の競合窓を保持 |

いずれも既存の[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488)／[#271](https://github.com/hat47x/tai-pleroma/issues/271)、[SK-01](../../evaluations/SK-01-harness-skills.md)、Product単独のテストへ割り付ける**追加の受入候補**である。新Checker・独立Expected Store・Harness Runnerを設けず、封印済みH2/H3のTask、Skill byte、順序と初回Blocking条件は変更しない。

**実行の順序**：最優先のTAI #168 H2/H3実OS隔離・独立四Sessionと、TEI非Plugin Stage1→Stage2の独立P0は据え置く。その後、現行mainに存在するRule種別のP/G差をTool-onlyで確認し、実在する二番目の読取専用ConsumerへのSource/型付きProjection受渡しを試す。Product Skill・TAI Skillの増分価値は、そのTaskについて実Call/受領が観測できた場合にだけ比較する。

**今回の到達範囲**：現行Product mainの実Source・PR採否と限定テストを照合した設計更新。上記YK-COMP-13〜20の新しい実Harness Trial、独立Consumer E2E、実OS、実DB/Host Grant、Owner意味受理は**NOT RUN**。

## 13. Skillが参照する能力は、候補の一意性・適用条件・実到達で三段階に絞る

能力の発見は「あるか、ないか」だけでは足りない。TEI [main #5197](https://github.com/hat47x/tei-platform/pull/5197)の現行`ResolvedSet.Capability`では、候補0件（不在）と複数件（曖昧）がどちらも`false`になり得る。Productの解決器を変更したわけではなく、テストによって**現行の曖昧さを確かめた**段階である。TAIのSkillは、この値だけを見て「提供元は存在しない」と説明してはならない。

TEI [main #5204](https://github.com/hat47x/tei-platform/pull/5204)では、Action／Observation／Evidence／Database Provider／Migration Tool／Featureの`Supports*`述語が、宣言された項目だけを真とする局所テストを備えた。ただし「Supports=true」は**能力の候補契約への適合**であって、選択Providerの実ロード、現在Grant、実呼出し、Result受領を示さない。[main #5205](https://github.com/hat47x/tei-platform/pull/5205)では、`.tei.md`に対応するParserが未選択の場合、選択可能な`tei.authoring/v1`／`tei.rule-authoring/v0`とmanifestの`languages:`設定を案内する診断が加わった。言語選択や利用条件の不備を、能力の不在と取り違えない。

**既存の製品応答を利用した最小判別**：

| 観測 | Skillの説明・次の行動 | 昇格させないもの |
| --- | --- | --- |
| Discoveryに実Commandが載り、対応するToolが実呼出しに応答 | **当該Command・当該対象で**限定到達を記録 | 全Commandが列挙済み、Owner意味受理 |
| Discoveryは限定範囲、または親Commandしか返さない | `not-observed`。既存CLIの対象操作の存在を別途照合 | `absent`という断定 |
| Productの解決結果が不在・曖昧を区別できない | `unresolved`。対象kind/id／候補の可視範囲を再確認 | 0件と2件以上の同一視、一意選択 |
| Language／Versionが未選択・不正 | 有効な候補と設定方法をProductの実診断から案内 | 診断なしの勝手な代替Language選択 |
| Supportsがtrue、しかしProvider/Grant未確認 | `contract-eligible`。実LoadとCallの検証へ進む | `invoked`／`granted`／`received` |
| 実Toolが失敗、Reader未取得または版不一致 | 観測した失敗理由を保持し、必要な辺だけ再確認 | 陰性結果を「対象なし」へ変換 |

ここでの英語の状態名は受入票の**説明用**であり、TEIの新しい戻り値・共通Skill Registry・製品間Result Schemaの採用を意味しない。現在の選択候補が曖昧なら呼出しを保留し、対象の一意性を確かめるまではAgentが提供者を推測で選ばない。

## 14. 実読取を再利用するには、元Sourceと「次の読取の前提」を別に固定する

YICの実行票は、ToolにCommandが存在すると知っているだけでなく、**固定したTEI commitから実際に何を呼び、どのbyteのどの範囲を読んだか**を残す方向へ進んでいる。

- TAI [#693](https://github.com/hat47x/tai-pleroma/pull/693)：固定TEI `926c8f2e3511`のclean cloneで、8件の既存Product/Rule読取Go回帰を実行したPR。対象HEADの`tai-reference`は全14ジョブsuccess。**PR #693はmainへ統合済み**（merge `5e6b44eb`）。固定HEADで実行した検証記録がmainに存在するが、実証範囲は製品ローカルA0であり、外部Harness/Consumer到達は含まない。
- TAI [#695](https://github.com/hat47x/tai-pleroma/pull/695)：固定TEI `926c8f2e3511`で`commands`、`model catalog`、`model locate`、`inspect`、`validate`の5コマンドを実行し、元Source位置・警告・`authorityLimits`を記録した。**mainへ統合済み**。ただし実行は製品ローカルのA0/R相当であり、外部Audienceへの送出許可・Consumer受領・Tool Reply完了を示さない。
- TEI [#5198](https://github.com/hat47x/tei-platform/pull/5198)：期待指紋による再読拒否の実装PRはmainへ統合済み。ただしTAI [#704](https://github.com/hat47x/tai-pleroma/pull/704)が固定TEI `a44b0ed2`の実バイナリで確認したのは、`trace`の`snapshotFingerprint`一致・不一致だけである。同じ固定版の`inspect`／`model locate`／`model catalog`は`-expected-fingerprint`を受理しなかった。**PRの説明や一つのCLIの成功から全Command／MCPへ一般化せず、使う実入口とBinaryで確かめる。**

したがって、Skillによる`inspect`の成功を元に別のToolへ進む場合、最低でも次を分ける。

| 区分 | 保存する最小の実証 | 再利用時の扱い |
| --- | --- | --- |
| **E0 対象と入力** | Task、対象kind/id、Workspace、実Product commit、Command family/argv、固定Source候補 | Tool/Skillの可搬性と無関係。対象が未選択なら停止 |
| **E1 読取の観測** | 実Exit、Result/Warning、元定義のSource rangeとSource Index、Read Footprint、実際の取得範囲 | 既存限定CLIの成功としてのみ案内 |
| **E2 前提条件の再確認** | 呼出し時点でProductが受理するRevision／fingerprint／Ownerの実再読結果 | 未対応Toolなら前提Pin済みとは書かず、手動再照合／保留 |
| **E3 Recipient利用** | 許可Audience、公開Projection、実送出byte、Consumer Body/Receipt、独立Expected | 受取側で未実行なら`not-run`を維持 |

**同じIDが見つかったこと**、**同じWorld Fingerprint**、**同じSource byte**、**その時点の開示Grant**を一つの同一性へ畳まない。ReaderがSourceを引用できることはProduct意味受理・外部AudienceへRawを送れることと別である。TAI #168の実OS隔離と独立H2/H3四Sessionを、このローカルBaseline試験で置き換えない。

## 15. Whole/Field投影は「情報を落とさない」と「公開し過ぎない」の両方を検査する

TEI [main #5156](https://github.com/hat47x/tei-platform/pull/5156)の既存pure Transformを使う局所試験では、Whole Recordの出力に追加`internalNote`が残り、明示的な2 Field Projectionでは追加Fieldを出力しない。必須`amount`の欠落を拒否し、明示NULLを「Fieldがない」に変換しない。**これが証明したのは純粋な値の投影**であり、Sourceの取得完全性・Scope・Fieldの公開権限・実Port BindとProvider Callではない。

Skillの利用者が「この2項目を文書へ渡す」と求めたなら、Whole Recordを簡便な代用として公開せず、元ProductのScope/Contractと明示投影が合致するかを確認する。ただしField Projectionで秘密項目が出力に含まれなくても、そのFieldが許可されたことの証明にはならない。Graphの多重性／順序、数値の単位・精度、NULL・未取得、Audienceごとの見せ方は、前述のD1／D2／D3で独立に検証する。

**最初の小さな統合試験**は、同じ公開DataのWhole／2 Field Projectionを使い、元Sourceが同一で追加Fieldだけを変えたときの出力差と、公開Audienceの最小Projection候補を比較する。既存Transform回帰のPASSを再利用しても、RecipientのDisclosure/Delivery、Provider、保存処理の受理までは主張しない。

## 16. 実行票へ引き渡す追加反証

| ID | 一因子の反証 | 既存Owner／期待する停止 |
| --- | --- | --- |
| **YK-COMP-21** | Capability lookupの`false`を候補0件の断定として返す | TEI #5197／TAI #488：曖昧な複数件を`absent`に変換しない |
| **YK-COMP-22** | Supports=trueだけで実Providerが呼ばれたことにする | TEI #5204／TAI #488：ContractとLoaded/Invoked/Receivedを分ける |
| **YK-COMP-23** | 未選択Languageを説明せず未知の能力として捨てる | TEI #5205／TAI #488：実候補・設定案内・対象外のFenceを区別 |
| **YK-COMP-24** | Limited DiscoveryでCommandが見えず「CLIに存在しない」と断定 | TAI #488／既存SK-01：限定範囲と不存在を分離 |
| **YK-COMP-25** | `inspect`のSource Rangeがあるので現在Grant／二次開示も成立とする | TAI #693/#695／TAI #232：元位置・現在許可・送出を分離 |
| **YK-COMP-26** | 前回の指紋が返るだけで、後続CLIが古い版を拒否できると主張 | TEI #5198／TAI #271：期待指紋を実受理した場合だけ再利用可 |
| **YK-COMP-27** | `validate ok`かつ警告3件をWarning 0として報告 | TAI #695／TAI #488：Exit/Result/Warningsを分ける |
| **YK-COMP-28** | Whole Recordの`internalNote`を二Field Projectionと同一として開示 | TEI #5156／TAI #232：Field集合とDisclosure Scopeを分離 |
| **YK-COMP-29** | NULLのFieldを欠落と読み替える、または必須Field欠落を黙認 | TEI #5156／TAI #271：値の状態とContractの欠落を別扱い |
| **YK-COMP-30** | ローカルGo 8件／CLI 5件の成功をH2/H3比較完了に数える | TAI #168/#488：実OSと外部Harness独立4Slotの分母を変えない |

これらは**試験候補**として既存Ownerに渡す。新しいScript群やRunnerをYICに新設せず、承認済みのTEI Product/CLI、TAIのReceipt Checker、SK-01評価とHandoff実行票を先に利用する。

**次段の判断**：P0はTAI #168の実OS G0→G1→G2から独立H2/H3四Slot（記録上比較適格0/4）、TEIの非Plugin Windows Stage1→Stage2とする。ローカルBaselineの確定後、公開TEI read-only Toolを同じTaskでB0/B1比較し、外部Consumerの実Readへ進める場合はRecipientごとに現行Source/Grantを再確認する。今回は文書と実証の区別を明確にする作業であり、**新しいProduct実行、OS隔離、外部Harness、二Productの実Consumer受理、Owner意味受理はNOT RUN**。

## 17. 一件の利用者作業を優先し、能力の証拠と開示の資格を混同しない

実読取の受入票を増やした結果、TAI [#693](https://github.com/hat47x/tai-pleroma/pull/693)／[#695](https://github.com/hat47x/tai-pleroma/pull/695)／[#704〜706](https://github.com/hat47x/tai-pleroma/pull/706)が対象とした5枚のカードは、すべて局所ProductでのI（対象）と、最大でもR（再解決）までの証拠に留まる。[#707](https://github.com/hat47x/tai-pleroma/pull/707)がこの境界を整理し、[#708](https://github.com/hat47x/tai-pleroma/pull/708)は`knowledge-context -disclose`でSectionの選択と省略を実測した。選択した情報の形を作れても、**特定の受信者に開示してよいと判定したことにはならない**。

Productが返す限界も根拠として保持する。例えば`local-read-is-not-disclosure-permission`、`selective-disclosure-is-not-access-control-or-redaction`、`omitted-knowledge-is-not-negative-evidence`は、局所読取・Section選択・省略の結果をどこまで解釈してよいかを直接制限する。[TAI #709](https://github.com/hat47x/tai-pleroma/pull/709)はReceiptへの限界文字列の保持を検査し、当時の対象12 Receiptのうち2件に含まれる17種類を数え、欠落0件を確認した。ただし**保持の検査は、限界に反する結論を書いていないことの検査ではない**。YICはこの情報を第二の権限エンジンに移さず、実行結果の表示・引継ぎにそのまま添える。

### 当面のSkillの対象はTEIの「受注の一変更」

TEIの優先順位の正本[plan/NOW.md](https://github.com/hat47x/tei-platform/blob/main/plan/NOW.md)は、実PostgreSQLからの受注明細読取、各行のRule判定、`*.tei.md`のRule一件変更、同じDBからの再読、生成Web画面での同じ答えの表示、という一巡に絞っている。TEI [#5271](https://github.com/hat47x/tei-platform/pull/5271)／[#5300](https://github.com/hat47x/tei-platform/pull/5300)では実Queryから行・Ruleへの限定的な経路ができた。全件性の証明がないため一意性の成立は判定保留になり得る。Webでの受領と、一巡の正式な受入はまだ残る。

YICは**同じTaskを最初から横断Skillへ移さない**。まず公開・合成の受注例と実在CLIにより、B0（Tool-only）で五段の到達点、利用したCommand/Source、Ruleの三値・理由、入力の完全性、失敗・再試行を記録する。B0で不便が確認された工程にだけB1（Product Skill）を追加し、発見・説明・手数・正答の増分を別の試行で測る。B2（TAI横断Skill）はProductをまたぐ用途と受信者が実在し、追加の価値が確認できる段階まで保留する。**Skillの比較をTEIの実Web完成の前提にしない**。外部H2/H3比較はTAI #168の独立G0〜G2を先に通す。

### P（開示）で区別する三つの操作

| 操作 | 製品で確認した範囲 | 必要な次の判断 |
| --- | --- | --- |
| 通常の内部read-only参照 | `tei inspect`や`tei view`等が、そのHost・Workspaceで値とSourceを返す | Sourceの現在性と取得完全性、意味判定。すべての内部業務Dataに横断ACLを必須化しない |
| Section／Fieldの投影・削減 | `knowledge-context -disclose`、純粋なWhole／Field Projection | 出力集合だけを検証し、秘匿・redaction・Recipientへの許可とは別にする |
| 別Product／外部Harness／別Audienceへの開示 | 受信者の特定・目的・Scope・現在Grantを伴うP判定が必要 | Source Owner／Product Hostの既存認可境界で許可を確認。許可できない場合は送らず、Taskを局所実行に戻す |

[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)の機密Profileは、外部開示や特例の秘密Sourceに対する個別の境界であり、通常のTEI組織Dataに一律のACL/OS隔離を作る指示ではない。また、**公開投影が同じでも内部の全件Claimの真偽が異なる**ことがある。外部側に見える一部だけから「全部が適合する」とは結論しない。内部で判定した真偽を1bitだけ返す場合でも、問いと結果の開示はOwnerの許可対象であり、Skillが勝手に追加するAPIにはしない。

### OS・ToolchainとReceiptの読み方

TAI [#697〜703](https://github.com/hat47x/tai-pleroma/pull/703)は、Goテストのexit 0に`SKIP`が混在する場合、Windows／Linuxによるpath境界・self-build・SUI参照Store試験の差、Go 1.26.11／1.27.0の成果物byte差を別Receiptとして記録した。**あるHostのPASSを別Hostへ転記しない**。Tool-onlyの初回基線ではOS/arch・Toolchain・対象commit・実行した試験とSKIP理由を保ち、Receiptの`PASS`とProduct意味受理、実Consumer受領を別に報告する。

今回の追加は、既存D0〜D5／I・R・P・T・C・Hを**実際の一件へ使う判断**であり、新しいSkill Registry、PDP、Runner、Provider、Expectedを足すものではない。目下の停止線は「**TEIの受注一変更を実CLI・実DB・実Webまで通す**」と「**TAI #168のOS隔離から独立H2/H3四Sessionを成立させる**」の独立した二本である。Web表示・外部Consumer・H2/H3比較適格は、関連する実証が出るまで未完了として扱う。

## 18. Skill選択の検収は、製品の実結果・開示・Harnessを別々に測る（2026-11-19）

最初の評価では、[TEIの公開手順0〜5](https://github.com/hat47x/tei-platform/blob/main/docs/first-change.md)をSkillなしで実行する。実際のDBから読めた行、Rule変更後の判定、画面で見えた結果と、独立した期待を一つの試行で比べる。**手順を通す前に新しいProduct Skillを配布しない。** 作業の完了後、使いにくかった箇所に限定してSkillの有無を比較し、所要操作・再説明・誤選択と結果の品質を記録する。製品機能の欠落をSkillの説明で隠さない。

横断評価に移る場合の最小の受渡し条件は次のとおり。既存の[実行票](cross-product-handoff-execution-tickets-2026-11-11.md)と[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)を再利用し、別の判定器は設けない。

| 観測箇所 | 現在わかっていること | 次に必要な検収 |
| --- | --- | --- |
| **R：元Product** | 固定したTEIの実CLI・Source位置を読んだ限定記録がある | 今回のWorkspace・対象・実Readに結び付くこと |
| **P：開示** | SUIの調査対象AccessRequestではRecipient別判定を確認できていない。一方、SUI→SHOのHandoff envelopeは受信者名の形式を検査できる | 形式だけでなく、今回の受信者と用途に対するProduct／Hostの実判断を得る |
| **T／C：配送・消費** | 別Processの受領とBody読取には限定実績があるが、Receipt一致だけでは内容や受信者の適格性を保証しない | 送出byteと受領byte、独立Expected、必要なFieldの一致・不一致を確認 |
| **H：Harness** | [既存Adapter](../../integrations/harness-adapter/README.md)にDSH等の実観測がある。DSH・Claude Code・Step Code・Codex execには終端判別とSession識別の解析部品がある | 選んだ実Harnessで終端・Tool Reply本文・Session同定を同一Attemptで確認 |

**受信者名の記載は開示許可ではない。** [受信者判定の調査](analysis/55-受信者の欄.md)では、SUI→SHO票の無関係な受信者名を形式検証器・SHO Consumer・ProducerのReceipt照合が受理した。この検証結果は受信者別Pの不成立を示すものであり、実際に秘密が外部へ送られたという意味ではない。受信者ごとの判定をProduct/Hostが確かめるまで、B2の外部送出は保留する。

**4 Sessionを一つの数で語らない。** [Harness Adapterの実観測](../../integrations/harness-adapter/README.md)では、DSHに4 Sessionを割り付け、H2/H3の配置・Loadから**比較に使える2対**を確認した。ただし正答の改善は未採点であり、OS隔離・完全なTool応答・独立Expectedを含む[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の先行4 Slotは**適格0/4**という別の評価である。どちらも証拠の範囲を変えずに保持する。

[Codex exec Adapter](../../integrations/harness-adapter/codex_exec.go)はGo側に実装済みで、合成JSONLのTool lifecycle欠落、未完了Reply、モデル切替などを誤って完了にしない（[PR #771](https://github.com/hat47x/tai-pleroma/pull/771)）。一方、現行C1はTool Offer、Skill配置、ContextRefとSession再開を未対応として起動前に拒否する。したがって**C1の単発実行をH2/H3のSkill効果や製品間Handoffの成功と数えない**。実Codex CLIの起動・認証・外部送出・権限は別に検証する。

既存Ownerに渡す追加の反証は四つに絞る。

- **YK-COMP-31（TAI #488）**：B0が未完了のままSkillの助言による見かけの成功をB1の増分価値と報告する。
- **YK-COMP-32（TAI #232／SUI・SHO Owner）**：Handoff票の受信者名が形式的に正しいだけで、別Audienceへの開示を許可したと扱う。
- **YK-COMP-33（TAI #168／#488）**：Adapter内のDSH比較可能な2対を、#168のOS隔離等を満たす4 Slotの合格と読み替える。
- **YK-COMP-34（TAI #168／#234）**：Codex C1のJSONL終端から、Tool/Skill/Contextの実利用やSession再開を推測する。

**Skill選択評価器の最小修正（S29〜S32）**：B0を評価するときに、`selected.tools`が空なのに`claimsToolReached: true`と書かれた申告を見落とさないようにする。既存の`unsupportedEvidenceClaim`を利用し、`evidence.toolReached: true`という自己申告があっても、選択したToolとの対応が無ければ不支持として数える。反対に、Tool選択も到達主張も無いB0を誤って失格にしない。B1で実際に選ばれたToolと正規の観測欄が揃うケースは従来どおり評価する。この修正は**申告の内部整合性の合成検査**であり、実Tool呼出しやTEI公開手順の完走を証明しない。製品の[初回利用手順](https://github.com/hat47x/tei-platform/blob/main/docs/first-change.md)を実行する検収と、[TEI #5588](https://github.com/hat47x/tei-platform/pull/5588)の実PG・Chrome試行の採否はTEI Ownerで追う。

**B0の試験条件を検査する（S33〜S38）**：B0はTool-onlyの基準であり、Product・Toolの直接使用を禁じないが、Skillの選択を認めない。これまでの採点器は`selected.products`と`selected.skills`を同じ集合にまとめていたため、同名のSkillだけで必要なProduct能力を満たしたと判定できた。B0ではSkillを必要能力の充足対象から外し、`skill:<名前>`を既存の`extra`へ**一度だけ**計上する。同じ名前のProductを正しく選んだ場合でもSkillの混入は見逃さず、B1でSkillが認められるケースやB0のTool-only成功は従来どおり扱う。保留したB0のSkill混入も、`wrongExecution`とは分けて数える。これも選択記録の合成試験であり、実Loadや実Tool実行の観測に置き換えない。

**TEIの現在の受入境界**：[TEI #5588](https://github.com/hat47x/tei-platform/pull/5588)は2026年11月19日にmainへ統合され、公開手順0・1・3のシェルを、同じ実DB・Workspace・Chromeの試行で実行するところまで進んだ。ただしWebプロセスの起動はテスト側が担い、初回利用者が手順書の全操作を実行したことまでは証明しない。この残りの利用者検収をB0の実結果として先に確かめ、Skillの採否比較はその後とする。

**比較群の入力資格（S39〜S41）**：既存の選択評価器が受け付ける比較群は`B0`・`B1`・`B2`の三つに限る。これまでの採点器は、`b0`や`H2`のような任意の非空文字列を別の群として集計できた。`b0`ならB0のSkill禁止規則が働かず、誤った比較結果になる。これらは文字列を推測補正せず、理由を添えて未採点にする。正規の三群の試行は同じ入力ファイルに混在していても個別に採点する。`H2/H3`は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の外部Harness資格試験であり、このB0/B1/B2の採点群に混ぜない。これは評価データの取り違えを防ぐ合成回帰で、実Skill Load・実Harness比較の成功を証明しない。

**TEIの先行自動試験**：[TEI #5608](https://github.com/hat47x/tei-platform/pull/5608)までで公開手順0〜4のCLIを検証し、[#5633](https://github.com/hat47x/tei-platform/pull/5633)・[#5642](https://github.com/hat47x/tei-platform/pull/5642)で公開`go run`と出荷Webのフォーム操作までを実PostgreSQL・Chrome試行に接続した。自動試験の到達点と初回利用者の実操作は区別し、後者の受入結果を得る前にB1の増分を主張しない。

**採点結果の機密保持（S42〜S47）**：評価者だけが持つExpectedには、漏出してはならない文字列が入る。従来の採点器は、検出した秘密の原文を`disclosure`の結果欄に表示し、改行を含む秘密はJSON文字列への変換で見逃すことがあった。改修後は実際のJSON文字列値・入れ子・項目名と数値を照合し、一致したExpectedの順番を`secret-1`などの匿名識別子として返す。漏出件数は従来の`disclosure`指標で集計する。**識別子は原文でもハッシュでもなく、正答や開示許可を示すものでもない**。評価者のExpectedファイルを参加Agentに見せない原則は変えない。入力Trialが最初から含む文字列や、Tool／Networkの実送出をこの静的照合が消去・検証できるわけではない。外部送出の実観測と開示許可は[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)の責務とする。

**採点結果全体に残る秘密（S48〜S53）**：`disclosure`欄だけを匿名化しても、採点結果に含まれる試行ID・結果名・費用情報や、未選択・過剰選択・不存在Toolの名称から同じ秘密を再出力し得る。公開する`score`結果では、評価者が保有するExpectedの秘密一覧を全Caseに照合し、一致した表示項目を`[REDACTED]`へ丸ごと置き換える。入れ子の`cost`はキーも含めて検出し、秘密を含む場合は一括非表示とする。一方、判定と群別集計は**元の試行値で先に計算**し、件数は変更しない。未採点の試行IDも対象にする。安全な費用値はそのまま残す。この処理は出力の二次漏出を防ぐ限定策であり、元Trial、実Tool応答、通信記録の秘密を消すものではない。原データに秘密が混じらない運用と、実送出時のHost/Owner側認可は引き続き必要である。

**同一試行の重複排除（S54〜S59）**：既存の採点器は、同じ`caseId`と`arm`の記録を何度投入しても群別指標へ加算できた。これでは重複転記と独立した再実行を区別できない。今回の評価形式には独立Attemptの識別子がないため、**同じCase・比較群の重複を一バッチ内で見つけた場合、いずれの行も理由付きで未採点**とする。最初の一行だけを恣意的に採用せず、秘密の漏出件数やエラー件数を重複で水増ししない。他のCaseやB0/B1/B2の別群は従来どおり採点し、形式不正の一行は正常な同名行を無効化しない。独立した反復試行の効果を測るときは、試行ごとに入力版・実Attempt・Expectedを固定し、別の採点バッチとして比較する。これは記録上の整合性検査であり、実OS/Hostが異なるAttemptを実行したと立証するものではない。

**TEIの初回利用検収への接続**：TEI [#5642](https://github.com/hat47x/tei-platform/pull/5642)では、実PostgreSQL・公開`go run`・出荷Webの4項目の実Chrome操作を、同じWorkspaceで独立Expectedに照合した。[#5643](https://github.com/hat47x/tei-platform/pull/5643)は初回利用者が手順0〜5を**空の検証用DBから補助なしで**実行する受入条件をmainへ統合したが、人による完走結果はまだない。最初のTaskは既存Ruleの書換えではなく、`unit_price_positive`の追加であり、`tei.workspace.yaml`・`semantic/sales/unit-price.tei.md`・`applications/order-entry/application.tei`の3ファイルを変更する（[TEI #5650](https://github.com/hat47x/tei-platform/pull/5650)）。B0/B1ではこの**同一Task・同一Tool範囲・同じ独立Expected**を固定し、手数・手戻り・支援の有無・所要時間と回答品質を別に記録する。数量0の明細（受注1001の主キー2）と単価0の明細（主キー3）を混同せず、受注1002のRelation一意性は各Readの実取得範囲に応じて判定する。初回と二回目以降の既存Rule改訂を混ぜてSkillの効果を水増ししない。[#5648](https://github.com/hat47x/tei-platform/pull/5648)の外部Origin通信遮断はCI用Browser Adapterの資格であり、本番Webの開示許可ではない。

**Studioの独立した到達点**：[TEI #5630](https://github.com/hat47x/tei-platform/pull/5630)の実Edge→Shared Acceptance→Windows Stage2可視表示はReference試験として動く。[#5647](https://github.com/hat47x/tei-platform/pull/5647)では、既存WorkbenchのCatalog／Inspect／Source出現位置を使う編集候補生成をmainへ追加したが、Source Indexの完全性、実Source byte、書込み資格を証明していない。製品Wails内での保存・再読込とOwner意味受理は別の未受入事項であり、B0の実利用試験に算入しない。

S29〜S59は選択評価器の合成回帰であり、実Product・外部Harness・利用者による試行ではない。まずB0の実利用一巡を優先し、P/T/C/HとB1/B2の実験は既存Ownerの実行条件が揃った段階で進める。新しいHarness本体、中央Router、共通認可器、Source正本、第二Expected Storeは作らない。
