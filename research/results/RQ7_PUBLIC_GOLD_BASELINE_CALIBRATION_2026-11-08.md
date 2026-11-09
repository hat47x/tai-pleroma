# RQ7 公開Goldの判別力校正 — 決定的Baseline実測（2026-11-08）

**状態**: PUBLIC SYNTHETIC TOOLING / GitHub Actions **39/39 PASS**。**人間・AIによるV0〜V3の認知効果比較、独立holdout、TEI実Product/Source/ProviderはNOT RUN**。

- 研究問い: [RQ7研究設計](../protocols/RQ7_BOUNDED_GRAPH_OBSERVABILITY_2026-11-06.md)、[公開pilot/Gold](../protocols/RQ7_PILOT_STIMULUS_AND_SCORING_2026-11-06.md)、[Gold偏りの指摘](../protocols/RQ7_DESIGN_CLAIMS_AND_GOLD_BALANCE_2026-11-06.md)
- 実行資産: [Baseline校正器](../tools/rq7_calibrate.py)、[11単体テスト](../tools/test_rq7_calibrate.py)、[v0/v1選択Renderer](../tools/rq7_pilot.py)
- **厳密な実行対象HEAD**: TAI研究PR [#473](https://github.com/hat47x/tai-pleroma/pull/473) commit `232bd7122997062d60e333a27669c684d4d58929`
- **CI run**: [rq7-public-prepilot #42384655226](https://github.com/hat47x/tai-pleroma/actions/runs/42384655226) → completed/success、Job `128439384024` → Python 3.13、`Ran 39 tests / OK`（2026-11-07 15:05 UTC、JST 2026-11-08 00:05頃）。以前の[28/28のHead](https://github.com/hat47x/tai-pleroma/actions/runs/42348122502)とは別の実行。
- Source blobs（当時のHEAD確認）: `rq7_calibrate.py=1b3758a9c572de49df6f1f6ae9209d9955d90e7d`、`test_rq7_calibrate.py=604e731e8f70019d8ba4de4a9c18bbc920ec04a1`、`rq7_pilot.py=5ff2529bf5832f9f3dc544c8010acf67cea89979`、公開v1入力`c50fbfa0e857415dec9bc895edfeb747628a31e7`／Gold`7dc6f987cf3203f530752e685c6478c115bc0101`。SHAはGit blob同一性であり、Product資格ではない。

## 1. 校正の範囲：人間・AI回答ではない

`rq7_calibrate.py`は既に**公開**されたGoldとSourceを直接読み、答えを生成できる幾つかの単純な規則に当てはめる。対象は出題の**判別力と指標設計**であって、AIの実力・人間の作業効率・Product上の推論の実証ではない。

比較規則:
- `always-supported`／`always-refuted`／`always-undetermined`: 全問に同じラベルを返す。
- `typed-selector-else-undetermined`: Fixture中の`question_selector`（direct-edgeまたはdirected-path）から構造質問だけを回答し、それ以外は未定にする。

後者の`question_selector`は**被験者に渡すレンダリングには含まれない試験用メタデータ**。このBaselineの成績は特権的な**研究機材の上限/感度チェック**であって、人間・LLMが同じ入力から10件解けた証拠や公正な対照モデルではない。研究者によるGold誘導と意味的自己確認の限界も残る。

## 2. 計測結果：総正答率の見かけに注意

Goldは`supported / refuted / undetermined`の3値。`unknown`が正答の問題も存在する。

| Dataset/Arm | Gold S/R/U | always-S | always-R | always-U | selector-only＋保留 |
| --- | --- | ---: | ---: | ---: | ---: |
| v0 10件、V0/V1 | 2 / 0 / 8 | 2/10 | 0/10 | **8/10** | 8/10（v0にselectorなし） |
| v0 10件、V2/V3 | 4 / 3 / 3 | 4/10 | 3/10 | 3/10 | 3/10（v0にselectorなし） |
| v1 12件、V0/V1 | 4 / 4 / 4 | 4/12 | 4/12 | 4/12 | **12/12** |
| v1 12件、V2/V3 | 5 / 5 / 2 | 5/12 | 5/12 | 2/12 | **10/12** |

**最重要の限界**: v1のうち8件はSourceのDeclared Graphについての質問であり、**同じGraphから計算したselector基準は、V2/V3の追加Evidenceを一切読まなくても10/12正解**になる。全問正答率だけで「Evidenceが理解された」「Graph形式が認知負担を削減した」「方法が一般化した」と結論してはいけない。

### 追加Evidenceが必要な層（v1・4件）

| v1層 | V0/V1のGold | V2/V3のGold | selector-only＋保留のV2/V3結果 |
| --- | --- | --- | --- |
| 8件のDeclared質問 | S4/R4/U0 | S4/R4/U0 | **8/8**（Evidence増分なし） |
| 4件のEvidence質問 | S0/R0/U4 | S1/R1/U2 | **2/4**（S/Rの2件は見逃す） |

*V2/V3 Evidence層での正確な意味*：追加Evidenceがあって初めて判断できる`B-EP01`の「合法skip＋required observed」を支持、`B-EN01`の「未宣言hookなし」を反証、`F-EU01`と`X-EU01`の未観測は正しく保留する。これは**合成入力**上のGoldであり、実TEIの実装/観測の正しさではない。

## 3. 今回、計測可能になった誤答の4種類

研究の`score()`は単純な正答数に加え、次を区別する。

1. **false_certainty**: Goldが`undetermined`なのに`supported/refuted`と断言（根拠不足の無断昇格）。
2. **unnecessary_abstention**: Goldが`supported/refuted`なのに`undetermined`で保留（過剰拒否・探索停止の兆候）。
3. **wrong_direction**: Goldが`supported`なのに`refuted`、または逆（証拠の向きや直接/推移の取り違え）。
4. **correct**: 完全一致。4種は対象を固定したGoldに相対的で、`withheld`などの公開Policy状態を真理値に混ぜない。

v1のselector-only基準（V2/V3）は`10/12`で、`unnecessary_abstention=2`。**追加されたEvidenceの意味を読まずに、正しく主張できたはずの2件を保留した**ことが見える。単純な総正答率だけだとこの盲点が埋もれる。

## 4. 比較研究として事前に固定すべき評価表

次回、実被験者／実モデルで条件V0〜V3を割り当てる場合は次の順で結果を読む（**未実施**）。

| 主要報告 | 分母と要件 |
| --- | --- |
| 宣言構造のVerdict/理由 | `study_case_stage=declared-only`の固定母集団。GraphとTextは意味情報等価、独立Rendererの視認・a11yを確認 |
| **追加EvidenceのVerdict/理由** | `evidence-dependent`を**独立に報告**。特にEvidenceがS/Rへ変化させた対象を測る。4件の局所結果から一般化しない |
| 誤確定／過剰保留／逆向き判断 | 各StratumとGold真理値に条件付けた混同行列。`undetermined`を単なる誤答扱いしない |
| 根拠・次の正当な確認行為 | Source/Scope/Attempt/Reader/Disclosureが正しく指示され、Provider権限外の照会を推奨しないか、独立評価者が採点 |
| 認知・運用負担 | 品質と別軸でelapsed、tool/Token、再確認、human intervention、図表構築/維持費を記録 |

モデル・Prompt・参加者が同じ公開Goldを参照済みなら、その結果を**independent held-out cognition**と呼ばない。盲検GoldはOwnerまたは独立評価者が出題前に保持し、同一Source/Revision、開示範囲、図表の描画、表示順と学習効果を固定する。Graph/Tex共通の正本ID・観測範囲が実Sourceで照合できない場合は比較しない。

## 5. 他チャットで得られた発見との非重複な接続

- [TAI Draft #443](https://github.com/hat47x/tai-pleroma/pull/443)と[Draft #490](https://github.com/hat47x/tai-pleroma/pull/490)は、SUI/CSW等で**生成された候補、選択された候補、反証として参照した候補、実Consumerが受領した候補**を区別する。今回のRQ7は同種の誤昇格をBuild/ETLの`Declared/Resolved/Observed/Consumed`で判定する**研究上の比較観点**を提供するだけで、SUI Context Schema、candidate registry、外部Runtimeへは手を加えない。
- [TEI #2881](https://github.com/hat47x/tei-platform/pull/2881)には、実`tei trace`→Nodeの**直接Edge候補**とCaller-supplied scopeの分離を扱う限定実証がある。研究の`typed-selector`はその実装と連結しておらず、**Sourceの宣言scopeやRelationの全Role/完全閉包を証明しない**。実接続は当該Ownerの受入証拠へ戻す。
- [TEI #2495](https://github.com/hat47x/tei-platform/issues/2495)／[#1126](https://github.com/hat47x/tei-platform/issues/1126)の閉値域・FD・属性特性、[#3248](https://github.com/hat47x/tei-platform/pull/3248)のRole語彙受理について、**語彙名の認識と業務上のMeaning/Actual/Accepted**は別。RQ7の新しい`score()`が「未定を正しく維持する」ことと「有効な意味を不必要に拒絶する」ことを分けるのと対応する。
- CSWの生成・批評・媒介・著者の採否を分ける研究でも、媒介者の選択や最終出力だけを独立評価者によるGoldに置き換えない。新しいCognitive Methodの効果は各Productの別Ownerと独立実験で検査する。

**境界**: この校正器は新しいGraph Reader、第二Semantic Store、Owner Approval Engine、Policy、TEI Code Generator/ETL Runner、共通Host、独立AI evaluatorではない。研究実験の設計・可観測性を改善する局所ツールである。

## 6. 次のGate

- **G-Cal0（実施済）**: 公開Gold v0/v1の校正ツールをGitHub exact headで実行し、39/39単体テスト。公開fixtureの構造的整合性と単純対照を確認。
- **G-Cal1（NOT RUN）**: actual Mermaidレンダラー＋同等Textの画面、accessibility・情報量・表示長を独立検査。静的Mermaidコード自体は「視覚的UI」として計数しない。
- **G-Cal2（NOT RUN）**: TEI実CLI/Source Readerの狭い同一Attempt・Reader証拠を、既存#2881等から**現行Policyで開示可能な範囲**だけ受け取り、Product Ownerの資格と研究用Synthetic Oracleを混合しない。
- **G-Cal3（NOT RUN）**: 事前登録した独立Holdout（最低でも構造とEvidenceの両層）でHuman/AIのV0〜V3結果を取り、分層結果・誤確定・誤保留・コストを報告。

**停止／撤回**: 実Reader版・Scope/Policyが固定できない、Goldが出題者の自己整合に留まる、表示方式による追加負担が利益を上回る、品質改善が再現しない場合は、既存CLI・Textと明示された未解決のままにする。これらが成立する前にRQ7を製品の受入・学術的優位性として公表しない。
