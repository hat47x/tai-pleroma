# RQ7 G-Cal1b-AX：可視Graphと支援技術への関係説明の同等性

- **状態**: 公開合成DAGのみの研究機材改善（2026-11-11）。Chromium Accessibility Treeの機械照合は実施対象、**実スクリーンリーダー操作・Human/AI認知実験・実TEI Source/Disclosure/Authority/Owner受理はNOT RUN**。
- **正本**: [RQ7研究プロトコル](RQ7_BOUNDED_GRAPH_OBSERVABILITY_2026-11-06.md)、[G-Cal1b幾何検査](RQ7_CHROMIUM_GEOMETRY_GATE_2026-11-09.md)、[公開合成ツール](../tools/rq7_svg.py)、[ブラウザー検査](../tools/rq7_browser_smoke.py)、[負例](../tools/test_rq7_svg.py)。
- **差分の作用範囲**: SVGのアクセシビリティ名と詳細説明、およびそれらの検査。公開v0/v1のGold/刺激、Graph topology、Node配置、Edge経路、TEIのProduct・Studio・Policyは変更しない。

## 1. 新たに確認した反例

従来のSVGは`role="img"`、`title`、`desc`を備えていたが、`desc`は「Nodeにラベルがあり矢印が関係を表す」という**一般説明だけ**だった。具体的な`src → compile`や`compile → package`を伝えないため、**視覚上のRelationが正しくても画像の説明からRelationを復元できない**。

また`aria-labelledby="graph-title graph-description"`のため、ChromiumのAccessibility Treeでは一般説明まで画像の**name**に含まれた。ローカルChromiumの最小実験で`aria-labelledby="graph-title"`と`aria-describedby="graph-description"`を分けると、画像の短いnameと詳しいdescriptionを別フィールドで観測できた。

## 2. 今回の最小契約

| 面 | 新しく照合する内容 | 保証の上限 |
| --- | --- | --- |
| 宣言Graph | 固定Fixtureの全Nodeと**直接Edge**、方向、ラベル | 実Sourceの全関係の保証ではない |
| 可視SVG | NodeのID/Label、Edgeの方向、前回の幾何検査 | 人間が誤解なく読めるかは未証明 |
| **Text代替説明** | `svg > desc`で全Node ID＋Label、全**直接有向Edge**、件数、宣言のみ・未実証の停止線を明示 | transitive path／Run・Effect／Authorityを推定・追記しない |
| **Chromium AX Tree** | `image.name`は短いケース名、`image.description`は上記全Node/Edge説明と完全一致 | 実スクリーンリーダーがどう読み上げるかは未確認 |
| Negative | SVG本体を残し`desc`からEdgeだけを削除・別内容に差替え | **画像が正しいからa11yも正しい**という誤判定を防ぐだけ |

実装は`accessible_graph_description(case)`から直接、NodeとEdgeの一覧を生成する。Gold、Observer、Consumer、Runtime Receipt、外部Sourceを読む経路は増やさない。`aria-labelledby`と`aria-describedby`を分離し、HTML/XMLで意味を持つ文字は標準XMLエスケープする。

機械的な完全一致でも、元Fixtureが不完全なら説明も不完全である。同じSourceを使う構造チェックは**投影の一致**であり、独立Source Oracleではない。

## 3. 他チャットで得られた反例との対応

| 既存の根拠 | RQ7の研究上の学び |
| --- | --- |
| [TEI merged #4382](https://github.com/hat47x/tei-platform/pull/4382) | `CommandPeriodRef`の`close-requires/correction`は存在しても`ApplicationPeriodRef`/text/Studio期間表に未投影だった。**Sourceと複数Projectionの面別検証が必要**。今回は公開合成GraphのSVG visual/AX説明の一面だけを検証 |
| [TAI merged #619](https://github.com/hat47x/tai-pleroma/pull/619) | 同じ件数を示すReceiptでも対象集合・意味が一致する保証はない。RQ7のNode/Edge**件数だけでなくID、Label、方向**を比較する |
| [TEI merged #3321](https://github.com/hat47x/tei-platform/pull/3321) | 同じ観測tokenが異物理Root/Read Attemptにも出現し得る。SVG/AX説明の一致からWorkspace/Source同一性は主張できない |
| [TEI merged #4240](https://github.com/hat47x/tei-platform/pull/4240) | Manifestの前後一致と期間中の安定性／Memberの物理実体同一性は別。画面の2つのProjectionの一致も実Sourceの完全性ではない |
| [TEI merged #4299](https://github.com/hat47x/tei-platform/pull/4299) | Childの自己申告したState分離と実際の物理State分離は別。UIやBrowserの自己申告をActual Effectと同一視しない |

いずれも**他ProductのOwnerと検証結果をTAIが代理受理するものではない**。非公開のTEI CLI PacketやSource PathをFixtureへ転記しない。

## 4. 適用・検証条件

- 公開v0/v1は計22ケース、異なる宣言Graphは3種類だけ。22ケース・3GraphでのAX面照合を、全TEI Graphや多項Relation一般に拡大しない。
- Python標準`xml.etree.ElementTree`でSVG構造の`title/desc`と全Node/Edgeの完全一致を検査。説明の欠落・改竄・ARIA参照の誤り、XML要素注入を負例化。
- Playwright/Chromiumを用い、`Accessibility.getFullAXTree`の実際の`image.name`と`image.description`を固定Sourceからの期待値と照合する。ブラウザーDOMの`desc`だけを改竄した場合にも検出されることを必須とする。
- **AX Tree検査成功≠Screen Reader受入**。キーボードでの個別Node/Edge選択、各スクリーンリーダー・OS、長い説明の読みやすさ、公開Policyによる情報の抑制は別Gateとする。
- 元のSVGは固定幅Nodeで長いLabelのはみ出しが既知。説明に完全Labelが載っても、見えているラベルが欠ける問題が治ったとは数えない。視覚表示の長文対応は別タスクとする。
- 人間・AIの認知効率やGoldへの理解改善は未実験。図表表示のSource忠実性、実表示、AX情報、認知、業務意味、Current Authorityを独立した段階で評価し続ける。

## 5. 合否と停止条件

**G-Cal1b-AX**に合格と記録できるのは、**本PRの固定head**でPythonユニット試験・Chromium実AX Tree・既存幾何試験・TAI Referenceが成功した場合のみ。CI結果は既存headから自動継承しない。

既存`G-Cal1b-geometry`は[PR #556](https://github.com/hat47x/tai-pleroma/pull/556)でmainに統合済み。今回の改善が失敗した場合、根拠がないままa11yの完全対応と宣言せず、Draftを維持する。実ATによる独立した操作・認知の評価前に、TEI Studioへの正式なUI受入条件や実Run資格へは昇格しない。
