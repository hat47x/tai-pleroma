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
| 関係の期間重複Rule、Contract Query行からの状態Reader | [#5148](https://github.com/hat47x/tei-platform/pull/5148)／[#5149](https://github.com/hat47x/tei-platform/pull/5149)は確認時点でopen。局所実装・試験の提案段階 | mainの正式Rule・実Provider入口・全件読取が完成したと扱う |
| Typed PluginのWhole/Field投影 | [#5101](https://github.com/hat47x/tei-platform/pull/5101)は設計をmainに導入。[#5156](https://github.com/hat47x/tei-platform/pull/5156)のpure Transform回帰は確認時点でopen | 実Port接続、未公開Fieldの自動排除、現在Grant、非Builtin Providerを検証済みとする |

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
