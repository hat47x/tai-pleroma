# RQ7: 有界なパイプライン完全性と人間・AIの認知負担 — 比較研究プロトコル

- **状態**: 研究提案／実行前プロトコル候補（2026-11-06）、**RQ7比較実験 NOT RUN、Owner未受理**
- **基準TAI main**: `51196bc941609f5a9dfaafa7afb0ef2c6ed2dd0f`。このSHAで本研究を実行したという意味ではない
- **研究正本**: [TAI横断研究アジェンダ](../README.md) H1/H2/H5、[RQ6生成×検証](../COGNITIVE_GENERATION_AND_EVIDENCE_2026-11-02.md)
- **製品Owner**: [TEIセルフビルド #2831](https://github.com/hat47x/tei-platform/issues/2831)、[TEIファイル／メッセージ連携 #2542](https://github.com/hat47x/tei-platform/issues/2542)、[TEI生産性測定 #2018](https://github.com/hat47x/tei-platform/issues/2018)
- **隣接するTAI Owner**: [Harness-first #168](https://github.com/hat47x/tai-pleroma/issues/168)、[候補の可視性 Draft #443](https://github.com/hat47x/tai-pleroma/pull/443)、[事前出力の観測面 Draft #272](https://github.com/hat47x/tai-pleroma/pull/272)、[Product Value #422](https://github.com/hat47x/tai-pleroma/issues/422)
- 本研究は**製品のBuild graph/ETL engine/UI/トレース採取器を実装せず**、既存Ownerが提供する版付き宣言・解決結果・実観測を比較評価する

## 1. 中心の研究課題

**RQ7**: 宣言したパイプラインの図表を、実際に解決した入力・実行・Consumer読取りの証拠と**scopeを明示して**提示すると、同一情報量のテキスト表示や宣言図だけの場合に比べ、担当する人間・AIが暗黙処理・欠落・古い証拠を正確かつ少ない負担で発見できるか。

ユーザーの「図中になければ実際に存在しないと判断できる透明性」は設計上の理想だが、**全世界の不存在保証ではない**。判定対象を`Scope S`と`Revision R`、監視できる実行境界`Boundary B`、必要な観測面`Observer set O`で固定したときだけ、該当スコープに対する「観測済みの完全性」を主張する。

特に、同じTEI標準構造で表現できることと、**異なる実行・配送・Consumerが同じ資格を得たこと**を区別する。BuildとETL/MFTの共通Graphは、共通Runner・共通トランザクション・自動的なBusiness Completeを意味しない。

## 2. 観測・保証の比較軸（新共通Schemaではない）

| 観点 | その水準で確認した主張 | その水準だけでは確認できない主張 |
| --- | --- | --- |
| Declared | 有効な宣言内のNode/Edge/Source/Target/依存が列挙された | 依存解決、実行、漏れなし |
| Resolved | 同じRun／VersionのProvider・Source closure・Builder/Transform・Inputが解決された | 実際に使われたbytes、隠れたhook、実Runner |
| Observed | 対象Boundaryで実行・入力/出力・状態遷移が記録された | Monitorの観測範囲外の作用、偽造記録、外部読取り |
| Consumed | Consumerが特定世代のArtifact/Data/Receiptを読んだ | 業務的な正しさ、権限、人の受理、実世界Outcome |
| Accepted | 当該Ownerが対象・scope・時点を限定して意味/作用を受理した | 別Consumer、別版、別権限への転用 |

機械的な「完全性」は、`Declared ≟ Resolved ≟ Observed`という**集合の単純な等号ではない**。条件分岐・正当なskip・retryや失敗時のpartial attemptがあり得るため、事前に定めたグラフ意味論の下で次を別々に検査する。

1. **実観測が宣言内で許された経路か**（undeclared observed actionを検出）。
2. **実行されるべき経路が欠けていないか**（expected required action、例外と合法skipを区別）。
3. **どの範囲が監視できているか**（観測器の欠落時は`unknown`。出力digestの一致だけで内部工程の完全性を証明しない）。
4. **現在のConsumerがどの世代の成果物を実際に読んだか**（生成・公開・受領・読取りの区別）。
5. **必要な意味受理・Provider権限・Outcomeは別の証拠か**（この研究はそれらを代行しない）。

判定時の観測範囲が閉じていない場合、グラフにない対象について`absent`ではなく`not observed / unknown`を返す。完全な実行追跡を収集するために機密情報や無制限のAgent内部推論の取得を要求しない。開示可能なProjectionだけを比較する。

## 3. 既存の二つの実行Consumerを用いた反証

| Domain | 既存の実装・評価資産（所有者） | 今回の独立した研究課題 |
| --- | --- | --- |
| **B: TEI全体セルフビルド** | [#2831](https://github.com/hat47x/tei-platform/issues/2831)のSB-P0.1〜0.3。標準Graphと実build入力/Command/Artifact/Lockの照合、seed→stage1→stage2、暗黙hookやstale Inputを扱う。PluginだけのSB-3とTEI全体ビルドを混同しない | 図／テキストから未宣言操作・古いGraph・合法skipを判定する正確性と負担 |
| **F: ETL/MFT／ファイル・メッセージ** | [#2542](https://github.com/hat47x/tei-platform/issues/2542)のEF-01〜05、[ETL Draft #2827](https://github.com/hat47x/tei-platform/pull/2827)。2-member Artifact/Manifest、ordered≠gap-free、Transfer ACK≠Import/Business Event、別Provider | 同様の図／テキストを見ても異なる成功境界・ID粒度を混同しないか |

両者のData構造は共有できても、BuildのArtifact再現性とETLの業務効果は**同じGold**にしない。最初は各Ownerの隔離された合成ケースを受け取り、実処理の資格は各Ownerが出した証拠でしか判定しない。

[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)では公開TEI Sourceを実CLIのW0で照合した限定CIがある一方、外部HarnessでのH2/H3の実AI Tool/Skill比較は未完了。本研究はW0のCI成功を「実AIの認知負担が改善した」と扱わない。

## 4. 2×2 比較（研究の本体）

同一の意味情報・タスク・版・許可された開示範囲を4条件に与え、**表示方式 × 実観測への接続**の寄与を測る。実行前に各表示に含める情報量と参照可能性を揃える。

| Arm | 表示形式 | 実行証拠 | 何を測るか |
| --- | --- | --- | --- |
| V0 | テキストの工程・依存一覧 | Declaredのみ | ベースライン |
| V1 | 静的な工程Graph | Declaredのみ | 図式化だけの効果と過信 |
| V2 | テキストの工程・依存一覧＋同一RunのResolved/Observed/Consumer参照 | 有界な証拠 | 観測の効果 |
| V3 | 工程Graph＋同一RunのResolved/Observed/Consumer参照 | 有界な証拠 | 図と観測の組合せ効果 |

実Graph UIが存在しない場合でも、**固定版Graphから生成した読み取り専用の同等図**で予備実験は可能。ただしそれをTEI Studio実UIや編集/Authorityの試験と数えない。V0/V1が情報不足になる設計ではなく、利用可能な情報が違うことを実験介入として明示する。比較実施時、個々の回答者へその情報不足を知らせずに誤確定を誘導する場合も、事前の倫理・許可条件に従う。

被験者（人/AI）の順序は交差・入替え、同じ入力の学習効果を記録する。人とAIの結果を同じ母集団へ無条件に混ぜない。表示形式の効果と、実ログ情報量の差を別々に推定する。各条件のデータが揃わなければ効果量はN/A。

## 5. 候補となるGold／故障注入ケース（すべてRQ7としてNOT RUN）

| Case | 注入／読み取り課題 | 必須Goldと誤判定 |
| --- | --- | --- |
| B-P01 | 実buildの条件分岐により宣言済Nodeを合法にskip | skipを「工程がない」「不正」と誤断定しない |
| B-N01 | 実buildに未宣言pre/post hookが発生 | 実監視に現れた未宣言処理を検出。監視不足ならunknown |
| B-N02 | Source closure・toolchainが旧版、Artifact digestは偶然一致 | 同一bytesだけで同じ実消費Input/Graphと判断しない |
| B-N03 | 監視器が一工程を観測できず、宣言Graphには工程がある | 未観測を未実行／不存在としない |
| B-N04 | stage1/stage2成果物一致、seedの信頼・独立Oracleは未確認 | 収束をseed trustや意味受理に昇格しない |
| F-P01 | 明細・件数合計の2-member Manifestを一世代で実読取り | Generation/Publication/Consumedを別々に肯定できる |
| F-N01 | 片方のmemberだけ新世代、もう片方は旧世代 | 同一Manifest世代の完全受理と判定しない |
| F-N02 | Transfer ACKあり、Importerの受信やBusiness Receiptなし | 転送受付を取込/業務完了と誤称しない |
| F-N03 | 順序付き転送に欠番、後続は受信済み | `ordered`を`gap-free`と同一視しない |
| F-N04 | 同じFile digestだがTransfer AttemptとImport Unitが別 | 冪等キーを統合せず、異対象の二重処理に注意 |
| X-N01 | 宣言範囲の外に不可視Provider、監視器も未登録 | 「図中にないから実際に存在しない」と断定しない |
| X-N02 | Graph版とConsumer読取り版が異なる | 旧版Graphから現行Consumerの資格を主張しない |

Goldは「真の完全な世界の情報」を仮定せず、**隔離した試験で意図的に注入した現象と各Ownerの独立Oracle**を使う。ケースを研究者自身が作った場合は公開開発セットと未使用のholdoutを分ける。現行TEI #2831と#2542の実証ではない。

## 6. 評価の指標

1. **False completeness rate** = Gold上の非完全／観測不能ケースに対し、対象Graph/Runが「網羅済み・不存在保証」と答えた回数 ÷ 判定可能な非完全／観測不能ケース数。
2. **False block rate** = Gold上の正当なbranch/skip・部分的なread-only作業を過剰に禁止した回数 ÷ 正当実施可能ケース数。
3. **Coverage statement correctness** = 回答が対象`S/R/B/O`・未観測・必要なConsumer資格を正しく説明できた件数 ÷ 適格件数。単に`unknown`と答えるだけで満点にせず、どの証拠を次に確認するかも評価する。
4. **Change impact accuracy** = 入力・Source・Manifest/Artifact版変更時の影響Node/Consumerの見逃し数と過検出数。独立Oracleの影響集合を先に固定する。
5. **Review burden** = 判定時間、根拠への再到達回数、人間の追加質問/介入、LLM tokenとツール呼出し、導入・維持コスト、誤検出の復旧工数。
6. **Scope leakage** = 本来非開示のSource/Plugin/Provider名、内部診断、Agent候補名などが公開・別Harnessへ漏れたケース。実OS/Egress非干渉の証明は別Owner。

判定不能・unsupported・not-run・blockedを区別し、分母0の率はN/A。4条件のうち未実施条件がある場合は欠測として示し、優劣の結論を埋めない。最初の小数例では信頼区間や一般化可能性を過大評価しない。

## 7. 学術的差分と先行研究

- **SLSA Build Provenance** は`buildDefinition`、`runDetails`、`resolvedDependencies`、`subject`とBuilderの信頼境界を区別する。Build来歴自体を新規発明とは言わない。[SLSA v1.2](https://slsa.dev/spec/v1.2/build-provenance)
- **Process Mining / Conformance Checking** は宣言されたProcessと観測Event logのずれ・不確実性を扱う。モデルとログを比較すること自体を独創性と主張しない。[van der Aalst et al., overview](https://doi.org/10.1007/978-3-031-08848-3_1)、[uncertain conformance](https://doi.org/10.1016/j.engappai.2023.106895)
- **図表とテキストの理解実験** は既存研究がある。図が人の理解に寄与すると結論を先取りしない。[Software engineering whispers (2020)](https://doi.org/10.1007/s10664-020-09835-6)

差分候補は、**異なる実行Consumer（buildとETL/MFT）に共通する有界な「不存在・完了」主張**を、人とAIの判断正確性、過剰拒否、追加コスト、資料開示制限と同時に比較すること。学術的な新規性・有効性は**未確定**であり、先行研究レビューと独立評価が必要。

## 8. 製品開発へ戻す順序・停止条件

| Gate | 最小成果 | Ownerに戻すもの |
| --- | --- | --- |
| RQ7-G0 | TEI #2831/#2542から実行可能なGold・版付き証拠・未実証を取得。二Consumerを統合実行しない | 各Productの受入証拠への参照のみ |
| RQ7-G1 | B-P01/B-N01/B-N03、F-P01/F-N01/F-N02を公開合成入力と独立holdoutへ分離 | 誤った「完全」と合法skip拒否の最小反例。Ownerが不足する観測面を判断 |
| RQ7-G2 | V0〜V3の同条件の読取り専用比較を実施。まずAIと評価者を分離して少数試行 | 認知負担・誤確定・不必要な複雑さの増減 |
| RQ7-G3 | 新しいDomain（非ソフトウェア）/異なるHarnessへ限定転用し、比較結果を再現 | 何を標準構造にすべきか／Adapterで十分か／削除すべきかを判断 |
| RQ7-G4 | 結果と独立採点を固定して研究報告化 | Product Owner判断とは独立に論文の可否を検討 |

**非目標**: 第二のGraph Store/Resolver、TEIの統一Runner、外部MFTの実配送、全Agentの内部候補の監視、共通Schema、TAI専用Host、Plugin Registryの採否、Studioへの編集・Operation Authority、新しい実データ公開、論文の新規性確定。

**撤回条件**: V1/V3がV0/V2より誤確定を増やす、正当な処理の過剰拒否が増える、検査・図表維持費用が効果を上回る、Source/Scopeの欠落を検出できない、独立評価で再現しない場合は、より単純なテキスト＋既存CLI/receiptへ縮退する。Product受理と研究結果は別に記録する。

**今回の変更資格**: 研究計画のみ。TEIの標準型／ETL／self-build実装・実Target E2E・SUI/CSWの認知効果・人間/AI実験・独立holdout・権限・公開の検証は **NOT RUN**。この研究計画では、TAI/TEI/EKI/SHO/SEI/SUI/CSWの既存Ownerの採否を変更しない。
