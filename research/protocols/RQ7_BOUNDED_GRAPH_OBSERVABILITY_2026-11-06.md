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

## 9. 2026-11-06の追補：有界な不存在の保証／開示／最適化の三境界

[公開予備実験プロトコル](RQ7_PILOT_STIMULUS_AND_SCORING_2026-11-06.md)に、10合成ケースとV0〜V3の提示・採点条件を設けた。これは`B-P01/B-N01/B-N02/B-N03/B-D01、F-P01/F-N01/F-N02/F-D01、X-N01`の公開開発セットで、前節の12候補をすべて実行または実装したものではない。合成データの構造点検と、実験・Product実行・独立holdoutの証拠は区別する。

### 9.1 不存在証明は観測境界の閉包を要求する

`Declared`にない、`Observed`にない、`Consumer`が読まない、は同じ事実ではない。`no-event-in-scope`は、対象集合、観測器のcoverage、時点、欠損なしという条件が別に固定された場合に限定して研究上の結論とする。`Scope/Revision/Observer`が不完全なら`unknown`を返し、推論で隠れた工程を消去しない。

### 9.2 表示上の完全性と実行完全性、開示可能性は別

低権限のHuman/AIへ見せる図は、Provider・Source・Pluginの存在、件数、関係、診断やa11yラベルを秘匿する必要がある場合がある。このとき`policy-complete authorized projection`は可能でも、全Sourceの`execution-complete graph`と呼ぶべきではない。観測に必要な権限がないこと自体を事故や全体の欠落と推定せず、資格のあるProduct/Host側の独立検証へ委ねる。

この区別は[TEI三要素Method Draft #2878](https://github.com/hat47x/tei-platform/pull/2878) T06〜T09、[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)、[TAI事前出力観測 Draft #272](https://github.com/hat47x/tai-pleroma/pull/272)と整合する。**開示禁止の存在を漏らさずに「図の対象範囲」を伝える方法自体が未実証**。公開fixtureでは機密値を使用せず、Provider実制御を再実装しない。

### 9.3 論理Graphと実行Graphは一対一とは限らない

[TEI Plugin実現・最適化 Draft #2933](https://github.com/hat47x/tei-platform/pull/2933)では、Provider差替え、fusion、pushdown、partial evaluation、並列化、キャッシュが検討されている。最適化後の物理実行Eventが論理Node/Edgeの単純な一対一列挙と一致しなくても、**意味・順序・型/NULL・Unknown・Effect/Authorityが保持され、対応付けの証拠がある**なら正当な場合がある。他方、最終Artifactのbyte一致だけでは未宣言の作用や失われた分岐の不在を保証しない。

後続の反証候補（**未追加・NOT RUN**）:
- **O-P01**: 論理`A→B`を物理`Fused(A,B)`に変換する。事前固定した対応と意味・Effect Oracleが成立する場合、Node数の差だけで誤拒否しない。
- **O-N01**: 最終byteは同じだが、変換でUnknown/NULL、順序、認可確認などの意味上必須のEffectが欠落する。Graphの見た目やOutput digest一致で受理しない。
- **O-N02**: 物理Providerが出力できるのは部分Traceのみ。正しい最適化と未観測工程の欠落を区別できなければ、完全性の判定を保留する。

これはTEI側のNormalizer、Optimizer、Conformance、Source/Target OracleをTAIで定義・実装する要望ではない。RQ7が評価するのは、**論理↔物理対応の証拠をConsumerに提示したとき、人間/AIの誤確定・誤拒否・確認負担が改善するか**である。現行V0〜V3にこの追加要因を混ぜず、独立した後続比較とする。

### 9.4 今回の段階

[TAI研究用公開刺激](../fixtures/RQ7_BOUNDED_COMPLETENESS_PILOT.synthetic.json)、[公開Gold](../fixtures/RQ7_BOUNDED_COMPLETENESS_GOLD.public.json)、[読取り専用レンダラー](../tools/rq7_pilot.py)を追加。公開開発セットなので評価用sealed holdoutではない。既存の[TEI self-build #2831](https://github.com/hat47x/tei-platform/issues/2831)のP0-A0/A1/実CLI Artifact、[ETL/MFT Draft #2827](https://github.com/hat47x/tei-platform/pull/2827)のTransport/Data Processing/Business Atomic/Execution Grouping、[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の実Harness H2/H3は各Ownerへ残す。

**未実証**: 実Go/Node/外部MFT/Model、独立した図表示の認知効果、正式Observer閉包、実Grant/Disclosure、実最適化後の意味同値、TEI全体Self-build G4とProduct Owner受理。研究Goldを製品Gateへ移植しない。

## 10. 2026-11-06: 関係scope・時間窓・再入Buildによる完全性の限界（他チャット研究との接合）

**更新元**: [公開予備Tool実測](../results/RQ7_PUBLIC_PILOT_TOOL_VERIFICATION_2026-11-06.md)は元Git blobと一致するPython 3.13.5環境で`14/14`を確認。これは表示刺激ツールの局所結果で、TEI/EKI実Runner・独立研究Gold/被験者の認知効果は未検査。

### 10.1 関係の同一性は端点や表示名から導出しない

[TEI標準Graph/Tableの限定不在Draft #2881](https://github.com/hat47x/tei-platform/pull/2881)、[TEI自己記述 #2620](https://github.com/hat47x/tei-platform/issues/2620)は同名・異scope／表示ID再利用の拒否を扱う。研究用のGraph刺激では、必要な対象を次の**別々の参照**として保持する。

- `RelationSubject=(relation-scope, relation-id, revision)`。関係自身のscopeと端点のscopeは一致すると仮定しない。
- `EndpointSubject=(endpoint-scope, semantic-id, source-revision)`。端点の対応解決は関係の見た目と独立した証拠。
- `Occurrence/DisplayID`はUIの一時的キーであって、Qualified Subject、Source内容、Accept済MeaningやRuntime AgentのIDではない。
- 同じRelationの外観/配置だけを根拠に、別scopeのRelationや別Source occurrenceへ現在のGraph資格を移さない。

**追加の研究候補（未実装・NOT RUN）**: `Q-N01` = Relation表示名・始点終点labelが同じだがRelation scopeのみ異なる／`Q-N02` = 同じRelation scope+IDでも端点revisionが失効／`Q-P01` = 開示済みGraphだけで対象内の完全性を正しく限定し、未開示の存在件数を漏らさない。これらは公開10ケースの分母に加えず、TEIの実Consumer／Oracleが独立に対象を固定してから評価する。

### 10.2 「期間を閉じた」「入力がすべて届いた」「業務が確定した」は異なるClaim

[TEI ETL/ELT・MFT Draft #2827](https://github.com/hat47x/tei-platform/pull/2827)と[#2542](https://github.com/hat47x/tei-platform/issues/2542)では、配送の順序・ACK・Import Unit・業務イベントが異なる実体として整理されている。観測窓`[t0,t1]`の`complete`は、その期間・基準日・配送保証・利用可能なSource集合・確定規則の範囲でのみ妥当。遅延到着・欠番・更正・reopen時に`t1`の完了を現行全体へ自動更新しない。

**追加の研究候補（未実装・NOT RUN）**: `T-N01` = Transfer ACKは全件だがBusiness periodのclosed判定は未確認／`T-N02` = 期間closed後の遅延イベントにより再集計・改版が必要／`T-P01` = gap-freeな受領集合と業務受理が**別の独立証拠**で成立。ReceiptやManifestのdigestが同じでも、Transfer Attempt/Import Unit/Business Eventを同一IDへ統合しない。期間・watermark・reopenの技術方式はTEI/Product Ownerの設計判断とする。

### 10.3 Self-buildの「完了」は3つの独立段階

[TEI全体セルフビルド #2831](https://github.com/hat47x/tei-platform/issues/2831)の2026-11-06追補は、新たなP0を実施順に分類している。

- `SB-0`: `cmd/tei`の実選択外部moduleとオフラインSupply/Source closure/Toolchainの確認。
- `L1`: 外部のGo Toolchain/Adapterによる実TEI CLI Artifactの生成。
- `L2`: TEI標準BuildIntent・Typed Graphから実Build・Source/Target/Artifactを結ぶ。
- `L3`: stage1生成TEI自身の**実Process**がstage2のPlan解決・Builder実行を駆動してArtifactへ到達したという再入証拠。

`stage1/stage2`のbyte一致や外部Go launcherの2回起動だけを`L3`と評価しない。さらに`L3`が成立してもSeed Trust・Owner意味受理は別。研究側は別Build SystemやLauncherを製品に導入しない。

**追加の研究候補（未実装・NOT RUN）**: `S-N01` = stage1 digest一致でもstage2実Processが別Builder／`S-N02` = 外部moduleが未選択か未取得かを観測できず、Build graph完全と誤称／`S-P01` = L1/L2の到達を正しく支持し、L3については判断保留。自己構築を異なる深さで正答する能力を測る。

### 10.4 未知を抑制するのでなく、正しい確認操作へつなげる

V0〜V3で`undetermined`を回答したとき、採点者は「どのscope/Relation/Module/Period/Consumer/Readerを、誰のどの権限で次に確かめるか」を別の`next-check`欄で評価する。確認不能を単に全否定する方式、正当なskipを止める方式、権限外のSourceを照会して秘密を漏らす方式は高得点としない。

この研究対象は、完全なGraphを万能に証明する技術ではなく、**有界な証拠と図表が人間・AIの判断をどこまで改善するか**である。形式証明・学術的新規性は未確定。前節のPublic Fixture 10件のGoldをこの追補で事後変更せず、追加候補は別コホート／独立holdoutでOwnerと実験前固定する。TEI本体のCritical Path、Plugin/ETL実装、Studio M0→M1、現在のHost/Provider権限、CSWの探索手法はそのOwnerに残す。

## 11. 2026-11-06: Intent/Source/ObservationのClaimと公開Gold分布

[Gold分布と設計特性の自動判定に関する研究追補](RQ7_DESIGN_CLAIMS_AND_GOLD_BALANCE_2026-11-06.md)で、公開10ケースのV0/V1 Goldは supported=2/refuted=0/undetermined=8、V2/V3は4/3/3と実データを再集計した。これは人間/AIの実行結果ではなく**刺激側の分類分布**。従来の公開Goldを事後変更せず、次の独立Caseセットでは「宣言だけで反証可能」な問いも含め、always-unknownの過大評価を防ぐ。

併せて、TEIのEnum的な閉値域・Key/FD・Relation scope/Role・必須値・Pipeline閉包を**Intended / Source-static / Inferred / Observed / Accepted**のClaimへ分離。設計者のClosed-world宣言とSource上の列挙・DB観測の同一視を止める。`strong attribute`の一次定義は未確認であり、TEI Coreや正式判定を追加しない。検証結果のsupported/refuted/undeterminedと、Policyによるwithheldを同一の真理値Enumへ混合しない。

研究では確認済み齟齬と情報不足と低権限非開示を別に数え、誤警告・過剰拒否・確認負担を評価する。独立Oracle・現在のHost/Provider Authority・Owner意味受理は既存TEI側の責務。研究対象の設計補完であって、実Constraint Runnerや人間/AIの改善実験の成果ではない。


## 12. 2026-11-08：公開Goldの判別力校正と実行証拠の理解を分離

[実行記録と再計算可能なBaseline校正](../results/RQ7_PUBLIC_GOLD_BASELINE_CALIBRATION_2026-11-08.md)で、公開v1（12問）のV2/V3は宣言Graphのみを構造的に解く校正器でも**10/12**を得ることが分かった。ただしこの校正器は被験者に見せない`question_selector`にアクセスできるため、LLM・Humanの競争相手ではなく**出題・採点設計の診断**。固定head `232bd7122997062d60e333a27669c684d4d58929`の[限定Actions #42384655226](https://github.com/hat47x/tai-pleroma/actions/runs/42384655226)で研究用Python **39/39 PASS**、Product受入・研究効果は未実証。

**追加のGate**：以後の比較では(1)宣言構造の判定、(2)追加Evidenceで決定可能になった2問、(3)追加Evidence後も正しく未定とする2問を分層集計し、(2)+(3)のEvidence層を総正答率から独立に報告する。誤確定／過剰保留／反対向きの解釈を別々に測る。研究者がGoldを見た公開v1でのモデル回答を独立holdoutの成績としない。

[TAI #443](https://github.com/hat47x/tai-pleroma/pull/443)の候補生成/選択/参照と、[SUI Runtime実Context限定照合 #490](https://github.com/hat47x/tai-pleroma/pull/490)のBundle選択/反証参照の区別にも、「存在する/選ばれた/実Consumerで使われた/許可された」を単一Stageに潰さない原理が通じる。しかし本PRはそれらの製品Contract/正本を再実装しない。TEI #2881のCaller-supplied direct-edge Traceを実Relation宣言scopeの証明として扱わない。現行研究機材は公開合成Graphであり、実Source/独立Holdoutと人間・AI認知効果は**NOT RUN**。
