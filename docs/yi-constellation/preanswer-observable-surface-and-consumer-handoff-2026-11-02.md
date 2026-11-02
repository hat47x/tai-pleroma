# YI Constellation：回答前の観測面・実Consumer表示・Tool候補の開示資格（2026-11-02）

> **状態：設計・合成Referenceのみ。** 各ProductのOwner正式採用、実MCP/CLI/DOM/Renderer/Host/Network/外部AI接続、実際の漏洩の再現は**NOT RUN**。TAI #168/#232/#271と、各Productの既存Ownerへ帰属する横断受入案。共通Host／中央Policy Engine／共有Resource Registry／新しい意味正本は導入しない。

## 1. 横断発見：最終回答が同じでも、途中に公開される行動候補・描画結果は違い得る

2026-11-02の最新の独立Product成果を照合した。

- [SEI #767／Draft #770](https://github.com/hat47x/sei-cognition/pull/770)：内部に非公開の`private.reconcile`がある場合だけ、外部PlannerのTool候補にそれが出現する合成負例。**最終回答は両世界で同一でも候補列が異なる**。公開合成Python7/7は実MCP/OS/Network証拠ではない。
- [TEI #2507／Draft #2623 §7](https://github.com/hat47x/tei-platform/pull/2623)：Consumerが閲覧できるRouteが一つであっても、正式なOperation対象Routeが意味上唯一とは限らない。隠れた別Mapping、Grant、明示Binding、Action Purposeを個別に照合。合成Python RD-01〜12は実Host認可を証明しない。
- [SHO #7／Draft #12](https://github.com/hat47x/sho-composer/pull/12)：同じMarkdown Source・同じ2件のLink tokenでも、raw HTML許可のRenderer設定によってクリック可能なanchorの数が2/3件に変わる合成Parser実測。**索引済みリンク集合 ≠ 実Rendererが作る参照面**。実SHO DOM/Browser未実測。
- [TEI #2391](https://github.com/hat47x/tei-platform/issues/2391)：Diagnosticの文字列や可視Action、a11y、Renderer epochと、実Operation/Effectは別。非公開のFinding引数・Tool response/Clipboard/Session Log等が副次公開面になり得る。
- [EKI #465/#468](https://github.com/hat47x/eki-fabric/issues/465)：ResultClaim ACKとBody bytes受領/digest/Reader実消費は別。
- [TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)：個別Productから外部Harnessへ渡る範囲と、実OS/Networkの送出経路を分離。通常のTEI組織データを一律Secret扱いせず、**保護が必要なProfile/Source/Consumer**で適用。

**成熟した新しい接合観点**：ユーザーへの最終回答だけを監査しても、「答える前に何を列挙したか」「どのToolを選んだか」「Rendererがどのリンクを作ったか」「どのChannelに実送出したか」は判別できない。TAIのActivity/Skill選択には、この**回答前・Consumer実表示・副次面**を独立の観測領域として追加する。

## 2. 目的相対の観測面（新Canonical Schemaではなく試験用列）

| 面 | 対象となる既存Consumer/Operation | 誤った成功条件 |
| --- | --- | --- |
| **Authoring/Parse** | Source bytes、Markdown token、DSL Role/Source span、構文Plugin版 | Token検出だけで全参照・実Function・正式Roleが成立したとする |
| **Discovery/Planning** | Product/TAI Skill候補、Tool list、Method/Action/Route提案、内部診断の公開Projection | 同じ公開情報でもHidden Tool/Routeの存在で候補・数・理由が変化する |
| **Presentation** | Renderer profile/版、HTML/DOM/a11y/clipboard/screenshot、文書Preview、UI epoch | Parseした候補集合＝実際に操作可能な画面要素とする |
| **Invocation** | 実Tool Request/args、実Capability Binding、対象Resource/expected-state、現在Grant | 見えたButton、Tool description、Skill load＝認可済み実行とする |
| **Transport** | model messages、追加Request fields/Session Event、MCP/Tool返却、HTTP/DNS、ログ/配布 | 最終回答のredactionだけで外部送出も安全と宣言 |
| **Delivery/Effect** | EKI ACK/Body・SHO実Reader/保存、TEI Commit/Receipt/別Read | ACK/成功Toast/Manifest一致を実Readや業務完了へ昇格させる |

**三つの正当な非対称**：

1. 機密情報の利用権がある内部Productは、必要な内部計算を行える。その内容を外部Audience/Toolへ開示する資格は独立に決める。
2. 明示的に開示が認められた差は、Consumerの候補や回答に現れてよい。公開可能集合や現在Grantが異なる正例まで一律同一化を要求しない。
3. 同じSourceが別のRenderer/実Consumerで異なる操作面へ投影される場合、Source/Parserの検査で完了とせず、**実表示・実作用**を別の具体的な試験にする。

## 3. 用途相対の非干渉を「反例探索」として利用する

保護Profileを明示した二つの内部世界 `W0/W1` を用意し、対象Audienceへ公開してよいProduct Projectionと現在許可されたCapability集合が同じであるとする。

```text
W0/W1 (underlying Product data; may differ in restricted input)
  → Product-owned permitted projection P(W, audience, purpose, epoch)
  → Skill/Planner/Renderer/Consumer
  → observable trace T = offered actions + tool choice + request + messages +
                       DOM/a11y + delivery/status + transport/log (observed scope)
```

対象Audience/用途に関して許可された違いがないのに、`T(W0) != T(W1)`なら、**未公開の違いを利用した可能性がある具体的な負例**。これは小さい合成例を使った反証の方法であり、あらゆるタイミング、隠れたNetwork経路、暗号学的非干渉を証明するものではない。Productが許可している明示的な例外・利用者Principalの差・公開時点/公開観測集合を固定してから比較する。実漏洩の有無はHost/OS/Networkの実観測へ委譲する。

反対に、外部Tool名が一件だけ表示されたことから「本体に別の非公開Toolが存在しない」とは主張しない（TEI #2623 RD-02）。外部に詳細を出せないとき、内部ではambiguity・denied・staleを区別し、外部では許可に応じた説明だけを返す。原因や候補数、応答時刻も観測面である。

## 4. 合成Reference AS-01〜12（実Productは未実行）

[合成V8/Node-compatible参照スクリプト](../../evaluations/tools/check-preanswer-surface.cjs)をこのDraftへ同梱。参照値・比較ルールは公開の固定合成であり、各Productの実出力を収集したものではない。

| Case | 比較する二世界／操作 | 確認する差 |
| --- | --- | --- |
| AS-01 | 同一公開Tool集合・非公開Toolのみ有無を変更し、内部情報依存Plannerへ渡す | 最終回答は同じでも提案Tool列が違い得る |
| AS-02 | 同じ二世界、許可公開Toolのみを使うPlanner | 合成例では候補・Tool Request・最終回答を同じにできる |
| AS-03 | 権限に基づき公開Tool集合そのものを正当に拡大 | 許可された違いは表示候補に現れてよい |
| AS-04 | 内部Hidden Route ambiguityとGrant denyが異なる | Audience向けGeneric unavailableは同じにできる。Timing等は別試験 |
| AS-05 | Source/Link token同一、Renderer profileのみ変更 | 実anchor集合が変わり得る（SHO #7の実Parser再現を参考） |
| AS-06 | Rendererで外部Linkが可視だがクリック・自動取得は未実施 | 表示・実HTTP取得・AI送出を区別 |
| AS-07 | Model messages同一、追加Session Event fieldだけ違う | 最終回答とmodel本文だけでは副次送出を判別できない |
| AS-08 | 最終回答同一、a11y treeに合成秘密markerあり／なし | UI/Agentの副次観測面を別確認 |
| AS-09 | Actionは既に提示したが、Host Grantのみ失効 | 旧Affordanceを実Invocation許可へ継承しない |
| AS-10 | EKI Claim ACKあり、Bodyは未受領／受領・digest確認・Consumer読取済み | ACKだけでDelivered/Consumedを確定しない |
| AS-11 | 同じ`op: delete`が引用Sourceと正式Role Bindingに現れる | Source値同一と意味適用・起動資格を区別 |
| AS-12 | 過去表示の操作候補が新しいContext epochの画面へ残る | 表示資格・Action対象を現在のEpochへ再束縛 |

**試験時に必要な実記録**：Source/Renderer/Tool/Skillの実ロード版、対象AudienceとProductの現在公開Policy、実入力・内部Synthetic Canary、実出力・DOM/Tool list・Transport field/byte・Host拒否ログ、Observation time/epoch、別Productへ渡したArtifactとそのRead、OwnerのClaim。中間的な`not observed`を`no egress`へ格上げしない。

## 5. 既存Productへの実施順（Gateを新設せず独立実験を並行）

**P0・小合成対照**：AS-01/02/03でPlan候補の誤開示/正当公開を識別し、AS-05で解析Sourceと実Rendererの差を区別。各Productの既存合成反例（SEI #770、TEI #2623 RD、SHO #12）を再利用する。今回の独立Checkerは、製品安全性の独立Oracleではない。

**P1・同じ公開Sourceで二Consumer**：SHOの実Parser/Renderer/DOMをLink/HTML/Code Fenceに対して観測、TEIのModel/Action read-only Inspectで可視Action・内部候補・実Execution Eligibilityを区別する。TAIはProductが許したProjectionをHarnessへ渡す。未実装Toolや隠れたRaw/Routeを発見可能と偽らない。

**P2・実Tool/Harness**：TAI SK-01 H2/H3/H4/H5を利用し、Tool without Skill、Skill without Tool、同時利用で、`tools/list`、候補名、Action Suggestion、Request args、Tool response、Diagnosticsが何を外部へ露出したか測る。Productの認可・明示的な委任/強権限をそのまま尊重。

**P3・実OS/Transport**：TAI #232、TEI #2515/#2509のMock Endpoint+Synthetic Canaryで、Model payloadとSession Log/追加Request field、ログ/clipboard/DOMの実送出を計測。非公開値の実Dataを試験に投入しない。通信断後のbacklog再送も既存責務へ。

**P4・Consumer受領とEffect**：EKI同一Attempt Body→SHO実読取/納品、TEI Action→Host Current Grant→Receipt/独立Readを別縦切りとして結ぶ。最終回答・表示Action・ACK・Toastの単独一致を完了としない。

**P5・選択的再資格化**：TAI #271のJ0全面/J1選択的/J2無確認に、Sourceだけ変更／Renderer profileだけ変更／Hidden Toolだけ変更／公開Policyだけ変更／Grantだけ失効を一軸ずつ追加。**結果値の再計算が不要でも、現時点の提案・表示・開示・実行資格が変わるケース**を検出する。実作業・Tool呼出・Token/レビュー負担と誤公開率を比較し、最新のProduct実証拠なしに効果を数値化しない。

## 6. Ownerと既存計画への引渡し

- **TAI #232**：保護Profileにおける外部観測面、適切な開示Profile、実Host/OS/Network検証の統括。二世界に共通の「許可Projection」があることを**Product側から**受け取る。
- **TAI #168/#271／Skill計画**：必要なProduct Skill/CLI/Toolを選ぶ際、構文索引・実Renderer・Tool候補・実Invocation・Deliveryを段階別の履歴/現在資格としてつなぐ。Product固有の判定をTAIの新Engineで置き換えない。
- **SEI #767/#770**：公開情報に相対的なInquiry/Probe提案と観測十分性。
- **TEI #2507/#2623/#2391/#1174**：Operator/Action候補、Route Meaning、UI/a11y、Host実Effect。#2516/#2515がConsumer Disclosureと実Egressを扱う。
- **SHO #7/#8/#10／MMI**：Link索引、研究資料中の引用Role、Renderer/保存、外部Tool送出の実証。SHO独立利用を維持し、MMI C-01/T2 G0-0の未完了を統合成功へ数えない。
- **EKI #465/#468**：Task ACK/Result Body実受領、同一Attempt/異AttemptとDeliveryの帰属。

### 未採用と未実行

`AS-01〜12`は同じSynthesized worldを用いた**局所的な判別力確認**であり、非干渉の完全証明でも、実MCP/実Renderer/OS/Host/Networkによる漏えい・遮断の証明でもない。保護対象の範囲と許された公開差は各Product/Ownerが決める。既存のTEI #1119 Critical PathとSHO S0/MMI G0-0、TAI #168/#271段階試験を変更せず、単独Productの探索・実装・AIの自由な提案生成を維持する。
