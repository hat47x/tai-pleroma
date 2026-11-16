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

**実装選択**：Operator A→Bの選択はWorldの見た目やResult値が同じでも別資格になり得る。旧生成Scenario Commandの選択Pin強化を提案したTEI [#5114](https://github.com/hat47x/tei-platform/pull/5114)は**クローズ・未マージ**であり、現行製品の一般保証として案内しない。

**SUIの出典**：SUI [#3464](https://github.com/hat47x/sui-sensemaking/pull/3464)では、保存済みCard選択候補を現行Document Revision Headと照合する内部処理がmainへ統合された。本文がA→B→Aと戻ってもDocument版・Revisionの差を確認する。ただし選択Resolver等にはテストダブルが残り、正式なSource保存・開示資格は未成立。Raw読取後の再検証を加えた[#3465](https://github.com/hat47x/sui-sensemaking/pull/3465)は**クローズ・未マージ**であり、返却直前の再確認を実装済みと主張しない。

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
