# 生成的探索と証拠制約の接続：TAI横断研究の拡張（2026-11-02）

- **状態**: Research proposal / 設計上の考察。**Owner未受理、比較実験NOT RUN**。
- 対応: [横断研究アジェンダ](README.md) H1–H5、[SCN-001の固定予備実験](protocols/SCN-001_PILOT_FREEZE_2026-10-29.md)
- 確認したTAI main: `95253b11c18c0c335442194edec15e9ba7985646`（2026-11-02）。この版で本研究を実行したという意味ではない。
- 別Ownerの関連Draft: [#177 Harness境界](https://github.com/hat47x/tai-pleroma/pull/177)、[#231 価値・要望・要件](https://github.com/hat47x/tai-pleroma/pull/231)。本書はそれらの仕様・試験・受理を置換しない。

## 1. 議論を統合した研究の中核

従来の「意味・根拠を失わず他製品へ引き渡す」というH1/H5に、**発想の自由度と検証の厳格さを両立できるか**という新しい研究課題RQ6を加える。

**RQ6**: 文化的・概念的な生成規則、材料に即した帰納的探索、人間/AIの批評・媒介によって仮説空間を拡張しながら、Source・scope・Decision basis・Authority・Result/Outcomeを独立に照合することで、探索の有用性を損なわず誤った確定や行為を抑えられるか。

1. **生成 / Discovery**: 現在の証拠からはまだ確定できない仮説や再解釈を作る。CSWの生成・批評・媒介、SUIのcard/island/hypothesisが研究対象。3役を固定した3エージェントにしない。
2. **検証 / Warrant**: 仮説の根拠、競合する資料、適用範囲、当時の受理と現在の対象を調べる。SHO/MMIのSource、SEIのDecision/ExactBinding、TEIのModel/Conformanceが担当する。生成時の「もっともらしさ」は根拠ではない。
3. **行為 / Agency**: Providerが現在のPrincipal・操作・対象・効果を許可し、必要な場合のみEKI等が委任する。Taskの受付、固定コマンドのAcceptedResult、外部業務Outcomeは別々に確認する。

これは一つのAgentや中央Hostによる「成功段階」の定義ではない。各Ownerの既存正本・Provider Authorityと、通常のCLI/ファイル/外部ハーネスを用いて**Consumerで検査したい遷移の性質**である。TAIが新しいAuthorityや共通Schemaを発行する提案ではない。

## 2. 帰納・演繹の扱い：体系の構造と経験的正当化を分ける

CSWの現行[文化的体系スキル](https://github.com/hat47x/cultural-substrate-weaving/blob/70d8db5eab9cef76e340e196e0cb8c09f85f7086/skills/cultural-substrate-weaving/SKILL.md)は執筆を主要用途とする。そこから他ドメインへの有効性を自動で推定しない。

- **材料主導の帰納的探索**: 観測・文書・利用者の違和感から、まだ名前のない区別や候補を抽出する。観察事実とAIが作った解釈を区別する。
- **体系主導の演繹的・生成的探索**: 体系に規則・配置・変化がある場合、それに従って別の視点や候補を作る。たとえば易の上下卦や変爻の関係を探索の材料にできるが、伝統的意味を確認した箇所と今回構成した意味を区別する。
- **対照・反証・妥当性評価**: どちらから作った候補でも、業務上の事実・現行Source・人間のDecisionを導いたと自動的には言えない。材料との不一致は修正・保留・反例として残す。

「帰納と演繹は互いに排他的なCultural Substrate分類」「形式から生み出した候補だから経験的に真」「生成/批評/媒介を動かせばOwnerの受理が済む」という扱いをしない。認知Methodの効果は対象タスクと実際の利用に対して別に測る。

## 3. 研究上の最小形式化：主張と根拠の保証関係

特定の型・データ交換Schemaではなく、比較実験の判定上の関係として次を仮置きする。

`Support(c, e, s, r, t)`：主張`c`が、根拠`e`、scope`s`、revision`r`、確認時点`t`の範囲で支持される。

`Permit(p, o, x, t)`：Principal`p`が操作`o`を対象`x`へ時点`t`に実行することを、実際のProvider/Hostが許可する。

`OutcomeObserved(x, e, t)`：外部効果`x`を独立した観測`e`によって確認した。

研究上の**非昇格条件（proposed）**:
- `GeneratedHypothesis(c)` から `Support(c, ...)` を自動導出しない。仮説の生成成功は検証済みの意味を保証しない。
- `Support(c, e, s1, r1, t1)` から別scope/版/時点`Support(c, e, s2, r2, t2)` を自動導出しない。A→B→Aの同一本文も例外ではない。
- `Support(c, ...)` や`HumanAccepted(c)`だけから `Permit(...)` を導出しない。権限は現行Providerが確認する。
- `TaskQueued`、`ResultClaim`、`AcceptedResult`を`OutcomeObserved`と同一視しない。
- Sourceの欠落や図中に依存がないことから、未観測対象の不在を推論しない。透明性の主張には対象集合・scope・宣言/解決/観測の区別を付ける。

これらは標準的な形式意味論の公理として証明済みではない。各製品の現行契約の代替でもない。実験の反例設計を一貫させるための**比較用の述語**である。

## 4. 研究実験：成果品質と誤昇格を同時に測る

第一段階は、既存の[SCN-001研究Gold](protocols/SCN-001_PILOT_FREEZE_2026-10-29.md)と[SW-01ハーネス境界](https://github.com/hat47x/tai-pleroma/pull/177)のOwnerが定めるread-onlyの合成入力を、**同じ版・同じ課題**で使用する。新たなTAI接続を着手条件にしない。

| 条件 | 候補形成の方法 | 根拠・意味の検証 | 主目的 |
| --- | --- | --- | --- |
| G0 | 通常の単一回答/現行ハーネス | 表示と資料の通常参照 | 最小対照 |
| G1 | 候補を複数出し、人/AIで批評と媒介を行う（CSW由来のMethod候補） | G0と同じ検証条件 | 生成Methodの増分と認知負荷を分離 |
| G2 | G0と同じ候補形成 | 原record/版/scope/ExactBinding等の既存read-only検査 | 検証Methodの増分を分離 |
| G3 | G1の候補形成 | G2の根拠検証 | 生成×検証の交互作用を調べる |

**設計上の重要な統制**: 同じ質問文・生成AIモデル・参照資料・時間/トークン上限を各条件で可能な範囲で揃える。条件の順序、モデル知識の漏れ、探索時間、批評者の独立性を記録する。単一の正解が存在しない発想については、表現上の多様性・採用可能な候補・新たに確認すべき問いを複数評価者が評価し、機械digestの合否で創造性を判定しない。

### RQ6の事前に定義する観測

- **有用な探索**: 実務上別の確認・選択肢につながる候補の件数、既存の答えと重複しない候補、評価者が採用/保留/却下した理由。生成件数そのものを成功としない。
- **誤昇格**: AI案→事実、旧Decision→新対象の受理、Plugin形式適合→業務許可、AcceptedResult→外部Outcomeなどの無断昇格。
- **過剰拒否**: 正当なread-only閲覧、根拠確認、未決のままのDraft作成まで拒否していないか。
- **負担**: 人間のレビュー時間・質問数、トークン/計算費用、保持する証拠・説明の量。
- **転用可能性**: SCN-001の予約案内と、[SCN-002合成設備更新](https://github.com/hat47x/tai-pleroma/blob/95253b11c18c0c335442194edec15e9ba7985646/scenarios/SCN-002-synthetic-maintenance/README.md)の優先順位では、異なるGoldと人の判断条件を用いる。SCN-002をSCN-001の正解のコピーとして使わない。

実験者がCSWの生成を評価する際、生成者・批評者・媒介者の役割数を変えただけで「認知機構の効果」としない。Methodの手順・入力・採用規則と利用者価値に差があるかを測る。CSWの現行用途は創作であり、本実験の認知Method転用は**研究仮説**で、CSW本体の採用・性能実証ではない。

## 5. 先行研究に対する差分仮説（新規性未確定）

- W3C PROV-OはEntity/Activity/Agent、derivation、association、revision、delegationを記述する。**来歴を記録すること自体**を独創性として主張しない。[W3C PROV-O](https://www.w3.org/TR/prov-o/)
- 2026年のSource-Framing Propagation研究は、単純な出典忠実性だけでなく、根拠から判断・行動へ伝わる方向性を評価対象としている。TAI側の独創性候補は、さらにscope/版/人間の受理/現在のProvider Authority/Outcomeを**異なる独立製品の境界で**分けて測ることにある。論文との十分な比較と実証は未了。[ACL Anthology, EMNLP 2026](https://aclanthology.org/2026.emnlp-main.1871/)
- 2026年の批判的・創造的思考に関するレビューは、発散的生成と収束的評価を分けて考える重要性を報告する。CSWなどのMethod自体の新規性・効果を、これだけで保証しない。[Computers and Education: Artificial Intelligence (2026)](https://doi.org/10.1016/j.caeai.2026.100571)

原稿化の優先順位は、(1) H1の固定版・異scopeでの不当な昇格防止を再現可能に検査する、(2) 外部ハーネスで再現する、(3) RQ6の生成×検証の交互作用を測る、(4) 実物と人間の受理・Outcomeを別途得る、の順にする。初期成果を「汎用認知理論の実証」と呼ばない。

## 6. 実装・Ownerへの反映と停止条件

| 担当 | 次に反映する対象 | この研究で採用しないこと |
| --- | --- | --- |
| TAI研究PR #129 | 本書で研究仮説・比較条件・Goldと未実証範囲を保持 | 単一の成功Status、中央Host/DB/Runtime |
| TAI #168 / Draft #177 | 別ハーネスでのSource/scope/basis再確認の実際の比較 | 研究が製品受入やOwnerの判断を代行 |
| SUI / CSW | 生成・批評・媒介と複数仮説の認知上の増分を評価 | 3つの固定AIエージェント・文化的象徴による真理/権限証明 |
| SEI / TEI | ExactBinding、Source/Meaning、変換/Realization、図表のcoverage確認 | 既存Sourceの正本ID・意味受理をTAIが再定義 |
| EKI / Provider | AcceptedResultと外部Outcomeを分離しread-onlyまたは合成で負例を評価 | 合成Verifierを実世界の独立機関、本番sandbox、実業務Effectと同一視 |
| TAI #127 / Draft #231 | 価値判断、利用者への有用性、主体規模別のGoal/Authorityはそれぞれの計画を参照 | 研究用指標で人の選好・正式な採否を代行 |

初期Gateでは正式な資料/人間の意味受理/Providerへの副作用を伴わない。別ハーネス実行、Ownerによる実物受入、CSWの別用途への転用、独立評価者による比較は**NOT RUN**のまま。価値が得られなければG1/G3や新Adapterを削減し、既存CLI/ファイル/人間のレビューだけへ縮退できるようにする。

本書の採用条件は、(i) 既存Ownerと重複しない、(ii) 評価が反証可能、(iii) 開発に還元できる、(iv) 追加リスクを課さない、の4点であり、研究アイデアを正式な製品規範と同一視しない。
