# YI Constellation：外部Harness活用と独自Harness投資の段階判断（2026-11-08）

**状態：Ownerレビュー用の設計・投資判断案。独自Harness実装の決定ではない。**
**最初に実行すること**：[独立H2/H3比較のG0〜G2実行票](h2-h3-comparison-first-eligible-session-execution-card-2026-11-08.md)に沿い、同じ実Toolで公開Read正例／保護された合成Canary Read拒否を観測する。現状の比較適格は0/4。先に独自Loop/専門Pluginの投資実装を増やすのでなく、既存G0→G1/G2→新規独立4 Slotを成立させる。  
**Owner：TAI（横断比較・構成・配布）／各Product（専門能力・意味・証拠）／実Host・Provider（現行権限・実作用）。**  
**対象：YI Constellation全体。YI専用リポジトリ、第二の中央Host、統一Agent Runtime、第二Registry、第二Authorityの新設は前提としない。**  
関連：TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)、[#488](https://github.com/hat47x/tai-pleroma/issues/488)、[#271](https://github.com/hat47x/tai-pleroma/issues/271)、[#232](https://github.com/hat47x/tai-pleroma/issues/232)、[#234](https://github.com/hat47x/tai-pleroma/issues/234)、[Draft #270](https://github.com/hat47x/tai-pleroma/pull/270)、TEI [#2899](https://github.com/hat47x/tei-platform/issues/2899)、[#2509](https://github.com/hat47x/tei-platform/issues/2509)、[#2515](https://github.com/hat47x/tei-platform/issues/2515)、SEI [#767](https://github.com/hat47x/sei-cognition/issues/767)。

## 1. 結論候補：独自Harnessとは「専用実行ループの自作」と同義ではない

利用者が体験する **YI固有の知的作業環境** は、既存HarnessとYI ProductのSkill／Plugin／CLI／MCP／APIを組み合わせても構築できる。YIらしさの中核は会話Loopやツール一覧でなく、専門的な意味・根拠の評価、未知・保留の扱い、作用と権限の切分け、Productをまたぐ活動の継続にある。

**DSHのEverything is a Pluginの登場は、独自Runnerの機会費用を増やす一方、専門Pluginの投資価値を高める可能性がある。** DSH/Cordisはモデル・Agent Loop・Session・Tool・UIまで合成し直せるが、Pluginを登録しただけでProductの意味受理や外部Effectの真実性、OS隔離が成立するわけではない。DSHは2026-11-08時点でも開発者プレビューであり、仕様破壊的更新を明示している。YIは「DSH依存製品」ではなく、**DSHを含む複数Harnessの上で用途に応じて実現できる製品群**を目指す。

既存のTEI **Everything is Data** と **Core以外をPluginとする**方針を維持する。外部Harness用PluginとTEI内部のCapability/Operator/Provider/Target Pluginは、契約・配布・実行・認可の層が異なる。Cordis ABI/Node依存をTEI Go単一バイナリの標準DSL・Plugin ABIへ侵入させず、必要時のHarness Adapterで翻訳する。

## 2. 投資段階：段階別の「追加価値」が立証されるまでは上げない

| 段階（評価上の仮ラベル） | 提供形態 | 期待する固有価値／必要な証拠 | 判断 |
| --- | --- | --- | --- |
| HV-0 | LLM＋限定Tool／人の確認 | 低機能ベースライン。課題・正答・費用の基準を採る | 全比較の対照 |
| HV-1 | 既存Harness＋Product CLI/MCP/API（Skillなし） | 実Sourceの読取、Toolの呼出し、失敗・保留、監査を正しく実行 | 既定の出発点 |
| HV-2 | HV-1＋Product Skill／必要時のTAI Skill | 誤選択・誤解釈・確認負担が実際に減る。実Loadと適格評価が必要 | HV-1より改善したときだけ採用 |
| HV-3 | HV-2＋TEI/SEI等の**専門Plugin**、用途別YI Profile | 領域固有の判定・Evidence/権限確認・手順上の欠落を埋める | 本命の差別化候補。既存Productが正本 |
| HV-4 | YI自身がAgent Loop／Session／Scheduler等を所有 | 既存Harness＋Pluginでは埋まらない反復的で重大な欠落を実証 | 原則保留。独立Ownerの投資判断が必要 |

**注意**：HVは新しいCore状態値や互換ABIではなく、比較実験上のラベル。既存SK-02の **H2（Tool-only）=おおむねHV-1**、**H3（Product Skillあり）=おおむねHV-2** に対応するが、試験SlotのH2/H3と評価段階のHVを混用しない。TAI横断Skillの追加効果はHV-2内でさらに独立に比較し、無益なら常時ロードしない。HV-3で十分ならHV-4を実装しない。HV-4が必要になっても、局所Loop実装から検討し、全Product必須の統合Runtimeにはしない。

## 3. 専門領域で高い改善があり得る理由と、その外挿の限界

医療系の研究事例は、単に高性能モデルを使うのでなく、**患者・Source時点・権限・情報の完全性・検査順序・禁止操作・独立した結果確認**を実行過程へ組み込む価値を示唆する。ただし、医療でのHarness強化をYI全領域への一般的成功率改善へ読み替えない。

- 2026-10-11公開の **MedHarnessBench**（査読前プレプリント）は、342のHealthcare Taskと16,000超の制御実行を使い、領域専用のRuntime Supportが処理品質・タスク達成に改善をもたらすと報告。最終回答だけでなく、Supportの提供→起動→利用→後続行動への反映を分離評価する手法が有用。URL：https://arxiv.org/abs/2610.15714
- 一方、2026年の **npj Digital Medicine** のAgent比較研究は、汎用Agent化による精度向上が限定的で、Token量10倍超、遅延2倍超の例を報告。Agentの段階を増やせば必ず改善するという仮説を否定する対照資料。URL：https://www.nature.com/articles/s41746-026-02443-6
- **DSH一次資料**：Everything is Plugin／Cordis／Developer Preview。URL：https://github.com/deepseek-ai/deepseek-harness
- 2026-10-05公開の **MedicalHarness**（査読前プレプリント）は、107タスク×5モデル×5 Harnessで、結果分散の約4分の1がHarnessとモデルとの相互作用に関連し、全タスクに最良なHarnessはなかったと報告。比較時にModel・Tool・Taskを固定し、Context管理／計画／Tool公開を切替える分析が参考になる。URL：https://arxiv.org/abs/2610.05778

これは医療向け製品・自動診療の導入判断ではない。YIの横断実験はまず公開・合成資料で行う。医療相当の高リスク事例を将来扱う場合も、専門家の独立Expected、施設・データ保持者の実認可、Human Review、臨床的な実結果の検証を別に要求し、合成タスクのPASSを患者への適用資格としない。

YIで医療の知見を転用しやすいのは、まず **TEIの業務更新、SEIの根拠十分性、SHOの出典付き説明、EKIの効果・配送照合** である。診断能力そのものを共通Harnessの責務として実装しない。

## 4. YI各層の責務：Pluginで共有できるのは契約と限定投影

| Owner | 固有能力／Harnessへ渡す境界 |
| --- | --- |
| TAI | 目的・Task/Activity・必要Product/Skillの選択、横断継続、現在資格の再確認。中央Agent Loopを既定で所有しない |
| TEI | 受理されたSemantic、標準データ構造、Typed Query／Operation Intent、Data/Function/Procedure、Contract・検査・Artifact。Providerの実更新とMeaning受理は別 |
| SEI | Cognitive Method、根拠十分性、対立する仮説、Unknown／保留、判断の適用範囲。Harnessの自己採点を独立根拠としない |
| SUI | 意味探索、Card/Canvas/関係の投影・確認・再開。Product Raw全体や非公開Metadataを既定で外部へ渡さない |
| SHO | 原文保持、引用位置、編集・構成・保存と再開。Harnessの回答文を正式保存／出典検証済み成果物と混同しない |
| EKI／実Host／Provider | 必要時の委任、実アクセス・送出、操作同一性、Receipt、独立結果観測／配送。EffectはHarnessの応答で成立しない |
| OKF（接続対象） | 定義・検査可能な計算Claimの表現。計算契約の宣言／Attester／Receipt／Owner受理を別に扱い、TAIに第二Attesterを置かない |

**Activity/結果の境界**：Source Observation → Accepted Meaning → Current Qualification → Intent → Host Grant → Actual Effect/Receipt → Independent Observation → Consumer Delivery/Outcome。PluginのLoad/UseやAgentの回答は、この連鎖の一部にすぎない。特にCordisの可逆なPlugin登録解除はDB Commit/外部送信のRollbackではない。

機密ProfileはTAI #232／TEI #2515のOwnerが保持する。外部HarnessのRead-only Mode、別Session、別cwd、Plugin停止設定だけでRaw・Secret・別Laneの読込/外向き送出を防げたとは扱わない。

## 5. 既存Evidenceの範囲と、実験を増やす順序

**現況（2026-11-08）**：TEIの固定公開Sourceを用いるW0/S1の実Go CLI readは限定的に成立。外部DSHでTool実呼出しとH3 Product Skill原文の実Loadが4 Sessionの証拠にある。一方、同一条件の**比較適格Slotは0/4**。Workspace指定と配置の不一致、過去Session再利用、初回定義外Tool、欠けたResult、独立Expected未採点、親・他Laneへの実Read可能性により、正答・Skillの増分効果・隔離をPASSとしない。詳細の正本はTAI #168／TEI #2509とRunbook。

**順序を変えない（初回P0）**：
1. **G0：実OS identity／ACL／VM／Container等で、許可Sourceは読め、Reviewer-only/親Root/別Lane/秘密は読めない正負対**を観測。拒否を観測できない場合はenvironment-ineligible。プロンプトによる自制で代替しない。
2. **G1/G2：開示/送出・実起動CLI family/argv・stdout/stderr・Tool Replyの完全性**を確認。Task、Skill bytes、Root、Model、Tool Profile、予算、権限を事前Pin。
3. **新規独立4 Slot（H2→H3→H3→H2）**を事前割付。ITT全割付／PP適格を並記し、独立Expectedと実Tool/Skill Load観測で評価。既存4 Sessionを事後的に適格へ変えない。

**次の条件付き比較（P1）**：P0により方法が成立した後、同モデル・同Source・同予算・同Tool公開・同Grantで HV-0→1→2→3 を比較。Taskを (a) Productの確定対象読取・Source/Unknown提示、(b) **合成**の高影響業務操作の提案→認可拒否→未知Receiptの再送防止 に分ける。後者は実書込みや医療行為を伴わない。二Harness間の再開と現在資格再評価は既存SK-03／TAI #271へ委譲。既存TAI #488のX01〜X06、#232のCS-01〜06の独立Expected/負例を再利用し、新Validator/Oracle DBを作らない。

**追加の領域評価（P2）**：最初のP1に改善がなければHV-3のPluginを増やさない。改善が見え、既存Product Capabilityの不足が確認された場合だけ領域Pluginを実装する。PluginのResultを利用者が実際に受信し、根拠/保留が伝わったかを別観測する。

## 6. 増分価値と費用対効果の評価契約

**分母はTaskの事前割付全数（ITT）**。適格Sessionだけを集めた改善率を主成果としない。独立Expectedの評価と、Process/Deliveryの観測を分離する。初回4 Slotは検出・方法検証であり統計的な改善率の断言をしない。

- **品質**：独立Expectedに照らす正答・必要な保留、対象集合／意味軸／Sourceと時点の忠実性、重大な誤成功・重大な不要停止、誤操作・権限越境（重大度別）。未実施・非適格・不明をゼロ件の安全な成功へ変えない。
- **プロセス／配送**：Tool候補→Load→Invoke→Result→Agent採用→実Effect→独立Readback→Consumer受領を別列。根拠追跡・再開成功率と人の訂正回数も測る。
- **費用**：Tokenだけでなくモデル料金／Harness利用枠／追加API課金、Plugin開発・更新・依存追従、OS/Net隔離・運用、リトライ、独立採点、人的確認、遅延p50/p95、切替不能の損失まで含める。**安全・権限が不適格な安価構成は比較候補から除く**。
- **成果単価**：承認可能な正しい成果1件当たり総費用と、人の修正・再確認時間をHV段階別に比較。安全度が悪化した構成は単純な成果単価だけで採らない。試験ごとに可観測列、母数、CI/実Hostの区別を保持する。

**投資ゲート**：HV-4の検討を開始できるのは、(i) 独立した二つ以上の既存Harness上でHV-3まで試し、(ii) 同じ重大欠落が再現し、(iii) Plugin/設定/CLI/Host改善で解決できないことを説明でき、(iv) 欠落がYI固有の持続的価値と結び付き、(v) 保守・隔離・互換性・安全検証を含めた複数年TCOと責任主体が確認できたときに限る。これらを**採用条件案**としてOwnerがレビューする。閾値や投資額は実測前に決め打ちしない。HV-4を作らない判断も正式な成功とする。

## 7. 計画への接続と未実施の区別

- **TAI #168 / Draft #270**：実Harness、H2/H3、SK-01/02/03、ITT/PP、初回G0〜G2のOwnerを維持。この文書は初回Blocking Gateを増やさない。
- **TAI #488 / Draft #489**：HVの比較結果をX01〜X06の照合列に返すだけ。第二の試験Engine・独立Oracle・Fixtureを作らない。
- **TAI #234**：並列性・継続・費用・再起動は別評価。初回H2/H3が未適格のうちに常時稼働JobやSchedulerを構築しない。
- **TEI #2899 / #2509 / #2515**：DSH Plugin構造の研究、外部Harnessの実Tool/Skill、実OS/送出の境界を別Ownerで検査。DSHをTEI標準Runtimeにはしない。
- **Product Owner**：TEI/SEI/SUI/SHO/EKI/OKFそれぞれの受理・公開・実装判断を維持。YI横断構成が単独Productの価値・完成条件を増幅／先取りしない。

**未実施**：上記HV-0〜HV-4の同一母集団での独立比較、HV-3の実専門Pluginの増分、実臨床検証、二Harnessの実隔離適格試験、複数年TCO採点、Ownerによる独自Loop投資受理。これは2026-11-08時点の設計・実験計画であり、実装済み認定ではない。

## 8. 2026-11-08横断再整理：AI Harnessと業務Flow・共通APIを同一物として扱わない

**成熟した設計差分**：TEIの採用済み[ADR-0048](https://github.com/hat47x/tei-platform/blob/main/plan/adr/0048-shared-application-api-and-transport-adapters.md)は、CLI／MCP／Web／Desktopを一つの型付きApplication Operationへ集約する。APIはHTTPに限定されず、Hostが選択したProviderと現在の利用資格を束縛する。2026-11-08時点では全入口の同値性・実Provider二Consumer実証までは成立していない（[TEI #1251](https://github.com/hat47x/tei-platform/issues/1251)、[#1158](https://github.com/hat47x/tei-platform/issues/1158)）。**YIのHarness接続はこれに従うConsumer／薄いAdapter**となり、TEIの別操作Engine、Agent向け別意味APIや「CLI呼出しの文字列解析」を正式な第二APIとして作らない。

| 境界 | 所有者と不変条件 | Harness用に増設しないもの |
| --- | --- | --- |
| Model／Agent実行 | 選択した外部Harness。会話・Agent Loop・Tool選択／モデル接続。実OS/Providerの許可は別 | YI必須の自前Loop／Model Router／共通Scheduler |
| Application Capability | 各Productの型付きOperationとPlugin選択・意味/Validation（TEIはADR-0048） | CLI／MCP／Web／VUIで個別に複製した業務ロジック／万能Dispatcher |
| Domain Procedure／Workflow | 既存Productの状態と業務規則。合法遷移・期待版・保留・取消・再開条件は**決定論的に検査** | 自由文チャット履歴を業務状態やWorkflowの唯一の正本にする |
| Information／Meaning | SEI/SUI/SHO等のSource／Evidence・未決・引用・開示可能な投影。元データの保有者が現在Scopeを判定 | 自己申告だけの「検証済み」・無制限Rawコピー |
| Host／Effect | 実Provider/OS/HostがGrant、実送出、Attempt、Receipt、Consumer Readを観測 | Pluginの登録／unloadを実EffectやDB rollbackと同一視 |
| Activity／Handoff | TAIは必要なProduct能力と用途別Task/Evidence参照を継ぎ、履歴と現在性を区別 | Agent会話全文を第二の永続Business Canonicalへ昇格 |

**VUI／状態を伴うFlowは独自AI Harnessを要求しない**：音声入力・ASR・NLU／LLM候補・状態付き対話・確認・実Operation・TTS応答という媒体差は、それぞれProvider/Representation/Adapterとして組み合わせ、状態遷移の合法性はWorkflow/TEIのTyped Operation側で検査する。VUIが「やり直し」「次へ」「取消」「確認」等のFlow制御に相当するときは、必要な入力と遷移を明示してPause/Resumeする。音声UIで成功したという観測だけで本番操作のReceiptへ昇格しない。生成AIを使わない決定論的Flowを**同じ業務Taskの対照系**として維持する。これらはTEI標準APIへ別の必須VUI種別や新Workflow Engineを採用した決定ではない。

**PluginとTraitの接続**：TEI側のContract/Roleに対して原子的なTraitを合成し、手動実装要求とDefault実装の区別を保持する構想は、Harness固有のイベント一覧の模倣ではない。PluginのHookは **(a) optionalな提案・表示の差込点** と **(b) 不可避なHost/Providerの権限・Effect検査** を分ける。Cordis middlewareで可逆に登録した処理がスキップされたときに(b)を迂回できる設計は不適格。Trait・Hookpointの公開形式やTEI Source構文は各Product Owner判断前に固定しない。

## 9. 原則となる6つの接続点（SchemaやPlugin APIの先行採用ではない）

| 接続点 | 固定する要求と検証すべき負例 | Product／Host Owner |
| --- | --- | --- |
| P-1 能力発見・適用範囲 | Capability候補と現在選択／Load／Invokeを区別。Toolが見えるだけで意味受理・使用許可を宣言しない | TAI #168/#488、TEI #951/#1251 |
| P-2 入力・参照投影 | Source/Scope/時点/完全性/部分集合/非開示の残差を保つ。未承認RawやHidden ExpectedをHarnessに渡さない | SEI #767、TAI #232 |
| P-3 事前条件・操作Intent | Target/expected revision/業務状態と現在Host Grant/Disclosureを別検査。Tool説明文やSkillの規則を強制境界と誤らない | TEI ADR-0048、TAI #232 |
| P-4 実呼出しと結果翻訳 | CLI/MCP/Web/Desktop/VUIは**共通型付きOperation**へ。NULL/欠損、診断、部分成功、通信切断をテキストで潰さない | TEI #1158/#3419〜3422 |
| P-5 実Effectと独立確認 | Plugin dispose、Tool exit、LLMの完了発言をReceipt/実Readbackと分離。unknown/duplicate/partialは再送禁止条件へ | EKI／実Provider、TEI #2515、TAI #271 |
| P-6 再開・配送・説明 | Task/Evidence/Source revision/未決/期限/Consumer実受領を必要十分に渡す。別Harnessへ旧Grantを継承しない | TAI #271/#168、SHO/SEI |

P-1〜6は既存契約を**どこで検証するか**の目次であり、全工程を一つの巨大Hook interfaceへ移す提案ではない。ある媒体・業務で不要な段階を実装必須にしない。Plugin内の標準動作変更は、「どのContractを置換／合成し、何が引き続き強制されるか」が読めるようにし、選択した実Providerへの到達を確認する。同じ結果でも**Provider B選択→Provider A呼出し**なら失格とする。

## 10. 独自Harnessの費用対効果：Harness×Modelの交互作用と決定論的対照

**研究上の補正**：2026-10公開の査読前[MedicalHarness](https://arxiv.org/abs/2610.05778)は107タスク・5モデル・5 Harnessの制御比較で、HarnessとModelとの相互作用がOutcomeに大きく関わり、万能の「最良Harness」がないと報告した。医療専用[MedHarnessBench](https://arxiv.org/abs/2610.15714)の専門Support改善報告と、[npj Digital Medicine](https://www.nature.com/articles/s41746-026-02443-6)の汎用Agent費用増加を合わせると、YIの投資判断は**Task分布×Model×Harness×Product Tool/Skill/専門Plugin**ごとの比較が必要となる。ただし異なる論文のベンチマーク数値を同じ母集団として差引き・統合しない。

- **第一対照（既存P0）**：TAI #168のG0→G1/G2→事前割付4独立Slotを変更しない。比較資格0/4を動かす追加試験を要求しない。H2/H3でModel・Task・Tool・Sourceを固定してSkill一要因を測る。
- **第二対照（方法成立後）**：同Task＋固定Source/実Operation/Token上限/Grant/Exposureで (i) 決定論的Flow/人の通常操作、(ii) 外部Harness Tool-only、(iii) +Skill、(iv) +専門Plugin を比較。専門Pluginの差を見るときにHarnessを同時変更しない。正しい停止・保留・人の確認要求も評価対象とし、「自動完了」だけを最大化しない。
- **第三対照（必要時）**：同一Model/Providerで外部Harness二種を切替え、続いて同HarnessでModel二種を比較。順序・タスク難度・Secret/Expected漏えい・Tool面の差を統制し、結果の交互作用が無視できない場合は組合せごとの対応資格を記録。必ずしも全組合せの網羅を初期Gateとしない。

**費用対効果**：総費用は Provider/Token／接続/ロード／Test/独立Oracle／Host隔離／人手確認・修正／適格失敗の再試行／Pluginと外部Harness API追従／退避と置換を含む。収益面は「許可された正しいOutcomeの数、必要な保留、人の時間、漏洩・誤作用の損失を回避した範囲」を分ける。運用費が低くてもOS Read-deny不適格・情報開示違反・独立Result未確認は採択対象にならない。

**製品性の狭い定義**：YI固有のUXをつくることと、独自AI Loopを所有することを切り離す。Product固有の良質なOperation、可逆な専門Workflow、限定Evidence、説明/UIは外部Harness上にも製品として成立する。既存Harnessで欠けているのが**接続点や専門手順**なら先にPlugin／Application APIを改善し、独自Loop投資へ短絡しない。

## 11. 後続の計画分担・Owner判断

**優先度P0（既存のまま）**：TAI #168／Draft #270の実DSH隔離G0とTool/Reply G1/G2、独立4 Slotをまず成立させる。実際に必要な場合だけTAI #232／TEI #2515でHost強制境界を検証する。G0は現在の比較条件を満たすために必須であり、今回の追加設計による新Gateではない。

**P1（TEI操作面の成熟、既存Ownerの仕事）**：TEI ADR-0048と#1251/#1158/#3419〜3422に従い、Application APIの単一の選択済みProviderへCLI/MCP/Studio/Webから届くか、Resultだけでなくactual entryを検証。特に「B選択／A呼出し」、Result Envelope drift、typed error内Secret、未選択Pluginの露出、Source失効を負例とする。初回のH2/H3に全4操作・HTTP/実WebViewやVUIを追加Hard Gateとしない。

**P2（YI固有の専門能力の実験、必要性が確認されたとき）**：高影響だが**合成**の業務Flowを対象に、型付きOperation Intent→状態遷移→Authorization check→Mock Effect→Unknown Receipt→独立readback／Handoffを一Taskで比較する。決定論的Flow・外部Tool-only・Skill・専門Pluginの差を、既存Product Ownerの独立Expectedで採点。原子的Trait・Hook利用について実Providerに到達するかを確認し、外部HarnessでなくTEI内にあるべき強制条件を移設しない。VUIは同じFlowの異媒体Adapterという**条件付き第二例**で試す（ASRの誤認識と操作前確認・再開を反証）。医療データ／患者への実適用はしない。

**P3（独自Loop投資判断、依然保留）**：P0〜P2で同一の重大欠落が異なるHarness上で再現し、外部Plugin/API/Host改善では解けず、適格な品質・安全・保守TCOが投資対象として説明できる場合だけ、最小の局所Loop実装をOwnerへ提出。未実装・過剰なHuman確認／誤停止／誤実行のトレードオフを比較し、導入しない結論も受入とする。

**現在の資格**：ADR-0048は採用された設計方針。ただし共通Application APIの全入口同値・Provider二Consumer・VUI状態Flow・専門Pluginの価値、Harness×Modelの比較、HV-4の投資採用は**NOT RUN／未決**。新しいRuntime/Schema/Registry/Ownerの正式採用は行っていない。

## 12. 2026-11-08追補：活動・対話・業務の三つのFlowを区別する

[TEI #3503 Interaction Flow](https://github.com/hat47x/tei-platform/issues/3503)、[TAI #165 非定型活動](https://github.com/hat47x/tai-pleroma/issues/165)、[TEI #3278 原子的Trait](https://github.com/hat47x/tei-platform/issues/3278)を横断照合すると、従来の「Harness＝Agent Loop」と「Workflow＝業務手順」の二分法では足りない。**似た図で表せても、状態の正本・変更権限・失敗回復が異なる三つのFlow**を区別する。

| Flow | 中心となる問い | 管理するもの | 再開・強制の責務 |
| --- | --- | --- | --- |
| Activity / Adaptive Case | 次に何を調べ、何を保留し、何を進めるか | Goal、仮説、根拠、Task、期限、計画候補 | TAI/SEIが根拠・未決を扱い、外部Harnessが候補計画を実行。新事実時は再計画 |
| Interaction Flow | 必要情報をどう集め、対象と値をどう確認するか | Event、画面/対話Step、確認対象、Interaction State | TEI #3503が確定Event・Revision・確認失効・中断再開を扱う |
| Business Procedure / Operation | どの業務操作が合法で、何が実際に起きたか | Business State、Guard、型付きOperation、Effect | TEI/実Hostが現在Grant、expected revision、Operation identity、Receiptを検査 |

**Interaction State ≠ Business State ≠ Effect State**。チャット履歴が失われても、正しいSource/状態と再解決できる根拠をProduct側に残す。一方、AIの内部思考や全Sessionを第二の共有Canonicalへ保存する必要はない。

具体例：音声で注文確定の意図を検出→商品・金額・版を提示→利用者の確定Event→現在Business StateとHost Grantを再検証→型付きOperation送信→実Provider Receipt/独立Readback→Consumerへ結果表示。確認後に金額・対象・版が変われば確認失効。Commit後の通信断ならEffectはunknownであり、Harnessの再試行判断だけで再送しない。これは[TEI #3503](https://github.com/hat47x/tei-platform/issues/3503)のIF-02〜06と接続する設計例であり、実装済みフローではない。

## 13. 図表を生成・Validation入力とするLifecycle設計

他チャットの「**フロー図表から生成を駆動し、固定部分と拡張可能部分を明示する**」方針を、TEI #3503、[標準データ/Role #2620](https://github.com/hat47x/tei-platform/issues/2620)、[Extension #2090](https://github.com/hat47x/tei-platform/issues/2090)、[Trait #3279](https://github.com/hat47x/tei-platform/issues/3279)に接続する。図は説明の副産物ではなく、Authoritative Sourceに含まれるGraph/Role、またはその編集ProjectionとしてGeneratorと検証へ結ぶ。ただし新しいWorkflow DSL/Engineの採用を先行決定しない。

**想定される処理経路（概念図・実Schemaではない）**：

Authoritative Source（標準Graph＋Role＋出典） → Interpret/Required検査 → Contract/Trait/Provider/Target選択 → CLI/Web/Desktop/VUI別AdapterとFlow生成 → Hostで型付きOperation実行 → Receipt/独立Observation → 出典付き診断・差分をSourceへ戻す。

| 固定すべき意味・境界 | 拡張できる範囲 | 反証条件 |
| --- | --- | --- |
| Node/Edge identity、方向、多重性、Source/Revision/Scope | 図種・レイアウト・Journey・段階名 | 編集で未知Source/Edgeを消さない。意味Diffを表示 |
| Event/Operation型、Guard対象、欠損とNULL | 音声/テキスト/フォームの入力候補、表示/質問順 | 候補EventではCommit不可。確定Eventが同じならIntent同じ |
| Interaction/Business/Effect Stateの分離 | 対話の分岐、再入力、確認体験、媒体 | 確認後変更は旧確認失効。状態消失を成功へ変えない |
| Hostの現在権限、Effect Fence、Receipt確認 | Pluginが追加する検証・通知・観測・推薦 | Pluginを外しても強制境界を迂回できない |
| Trait Binding/required Fulfillmentと実Provider呼出し | 標準生成・manual-required・外部Provider | 手動実装未配置はFAIL。宣言のみはunverified |
| Targetと配送の実資格 | 独自Frontend、CLI、Web、Desktop、VUI | 必須Stepが落ちたTargetを同等と認定しない |

**Hookの責務を分ける**：Operation Hook（業務操作）、Interaction Hook（イベント/確認）、Generation Hook（表現/コード導出）、Observation Hook（診断/結果）という概念区分を比較する。Hookは生成コードへの文字列挿入位置ではなく型付きExtension Binding。合成順に依存する処理は明示的な順序・競合を診断し、Traitの原子的要求集合を実行順序と同一視しない。Cordis型の登録解除は既に発生した業務Effectの取消ではない。

**意味・実装・表示の失効**も分ける。図の配置だけ変わった場合と、Guard/Transition、Provider、Target生成器が変わった場合は異なる再Build・再検査範囲を持つ。説明図がいつの間にか第二の意味正本へ昇格しないよう、Source/編集投影/Generator入力を明示する。

## 14. 既存Ownerへ接続する4種類の比較実験

各ケースは**計画でありNOT RUN**。実験Tool、独立Expected、Fixtureは既存ProductのOwnerが保持し、本書で第二の試験Engineを作らない。

| 比較ケース | 実行Owner・時期 | 何を判断できるか | 危険な誤認定 |
| --- | --- | --- | --- |
| S0 公開TEIモデルのTool-only対Product Skill | TAI #168 / TEI #2509。**初回P0** | 同Task/Source/Model/Tool/GrantでH2とH3の増分 | Skillを読んだだけ／古い4 Sessionを適格化 |
| S1 Interaction Flow | TEI #3503 F0〜F4。P0の後に条件付き | CLI/Webの確定EventとOperationの一致、Hook選択・VUI追加の価値 | 音声応答や画面上成功＝実業務Effect |
| S2 未定型な適応活動 | TAI #165 SCN-004-B、#271／SEI #767。後段 | 固定手順より未知・反証・保留・安全な部分前進と再計画が改善するか | AIの計画文章＝受理済み事実/実権限 |
| S3 高度B2C | [TEI #3509](https://github.com/hat47x/tei-platform/issues/3509) B0〜B3。別レーン | Headless/独自Frontend維持でもExperiment、Conversion Journey、変更影響Pluginに追加価値があるか | UI生成成功＝CVR/売上改善。TEI Runtimeの強制 |

S3は**Harnessが不要という結論も出せる対照**である。B2C向けPluginは、既存Commerce/Analytics/Flag Providerを置換せず、Frontendの自由度を損なわない契約・計測・障害発見に価値を持ち得る。実CVR改善を主張する場合はExposure、Experiment allocation、Consent、外部Commerceで確定したOutcomeと独立した実験評価が要る。初回TEI H2/H3のHard GateにB2Cシナリオを持ち込まない。

S2では逆に、事前に全遷移が固定できないCaseにおけるAgentの動的計画が差別化候補。ただし、Actionの選択と、実際に作用してよいという現在資格を混同しない。[TAI #531](https://github.com/hat47x/tai-pleroma/issues/531)のOutcome Receipt / no-op / hold / policy denied / partial / unknownの区分と、独立Observationを後段の評価に接続する。

## 15. 独自Loopの投資判断：重大欠落の原因を先に識別する

「既存Harnessで失敗した」を一括して自前Loopの必要性にしない。G0の実隔離不成立、G1/G2の不完全Reply、Source/Required不足、未知の権限は、まず実験の資格問題として扱い、適格母集団の良い試行だけ残して成果率を計算しない。

| 具体的に観測された欠落 | 第一に試すもの | 自前Loopへ昇格できる条件案 |
| --- | --- | --- |
| Tool発見・使用が悪い | 既存Product Skill、Tool Profile、限定Design Context | Tool条件を揃えた複数Harnessで重大な同型失敗が再現 |
| 対話確認・Flowが不安定 | TEI #3503の確定Event/Guard、状態付きAdapter | 同じProduct OperationでもLoop固有の避けられない失敗が残る |
| 根拠・現在性の誤用 | SEI Method、TAI #271の選択的再資格化 | 許された十分な根拠でも複数Harnessで重大誤成功が再現 |
| Session切断・再開失敗 | Harness標準継続＋実HostのOperation Id/Receipt照会 | 同じ安全条件では局所Plugin/既存Hostで回避不可能 |
| 機密境界が守れない | OS/Hostの実隔離＋許可済みProjection | 機密条件で外部Harnessが不適格で、局所実装なら実拒否を示せる |
| B2Cの自由度や性能低下 | 完全Headless/独自Frontend＋必要な契約Plugin | UIとBackendの自由度を維持しても独自Loopだけが必要な実証 |

**投資判断票**には、Task分布・対照系と独立Expected、実Harness/Model/Tool/Skill byte、Source/Grant/Recipient、事前割付ITTと適格PP、重大事故/不要停止/保留、実Outcomeの配送、遅延と総費用、複数年のAPI追従/隔離/保守、縮退・撤退条件を揃える。閾値は業務用途別に事前設定し、結果を見て変更しない。安いToken・Plugin実ロード・AIの完了発言を成果認定の代わりにしない。

**現時点の停止線**：#3503のFlow Schema/実媒体・#3278のTrait実Fulfillment・#3509のB2C Conversion Plugin/CVR・#165の非定型CaseとHV-3/HV-4比較はいずれも提案・未実証。TAI #168の比較適格0/4と既存G0/G1/G2→新しい独立4 Slotを変更しない。新しい中央Host/Runtime、第二Operation/Workflow Engine、Trait専用Resolverの導入を決定しない。

## 16. 実証済み部品を独自Harnessの必要条件へ誤昇格しない：2026-11-08のEvidence照合

11月8日の他Productの実装状況を再確認した。YIが本当に新しいHarnessで埋めるべき隙間は、**局所で成立した能力を、同一Target／同一Attemptで、正しいScope・開示・配送を保ちながら組み合わせた後に残る隙間**である。以下の実績を足し算して横断E2E成立としない。

| Product / 出典 | 実績として主張できる範囲（確認時点） | Harness投資の根拠として不足するもの |
| --- | --- | --- |
| TEI [#3482](https://github.com/hat47x/tei-platform/issues/3482)／main `8ed583790e63b63527c1dd8f8aecc1d6ce6e3260` | 固定`sales.order.submit`の **13実CLI Reply、42件の限定Consumer負例**をmain push専用[CI #42462861657](https://github.com/hat47x/tei-platform/actions/runs/42462861657)でPASS。独立RequiredのCapability/Application/Source束縛を限定観測 | Function実Invoke/Provider/Grant、全設計閉包、外部H3 Tool Reply全byte、Owner意味受理は**別**。適格H2/H3の根拠には未使用 |
| TAI [#537](https://github.com/hat47x/tai-pleroma/issues/537) | Edge `edge-record` v4の端点種別optionalで投影→合成24件PASS、全体90段。省略/nullは型欠落として正規化、実端点未解決は合成で拒否 | Data Contractの成功≠実外部Harness受領・認可・意味受理。**NULLを未解決と断定する汎用Harnessルールは誤る** |
| EKI [#753](https://github.com/hat47x/eki-fabric/issues/753)／[PR #787](https://github.com/hat47x/eki-fabric/pull/787) | 同一試験プロセスで実Unixソケットを通して固定6 JSON Eventのバイト・順序と4種改変を検査。race付き5回の限定PASS | 別プロセス実Adapter/実Lease失効・Disposition/Connect/Provider Effect/受信Agentの活用は未資格 |
| SEI [#752](https://github.com/hat47x/sei-cognition/issues/752)／[#802](https://github.com/hat47x/sei-cognition/issues/802) | `sei resume --json`を構造化した既存CLI経路と、現MCP `resume`概要が原則人向けtextである差をSource・実例で指摘。#752はclosed、#802はopen | 現最新版の詳細表示差の再確認、**MCP概要の型付き同値**、実Harnessがbasis/rationale/unknownを受領して使えたことは未確認 |
| TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)／TEI [#2509](https://github.com/hat47x/tei-platform/issues/2509) | DSH実Tool呼出・Skill実Loadの局所技術Witness | 事前に隔離した新しいH2→H3→H3→H2の比較資格は**0/4**。OS G0実Read-deny、G1/G2完全配送、独立Expected/Grant等の再確認が必要 |

**型付きOperationだけでは「情報を十分に受け取れた」と言えない**。TEIのbounded-presentと完全なFunction定義、TAIのoptionalにおけるnull省略と未解決、SEIのCLI構造化再開とMCP自由文、EKIのOSソケット成功と実Worker Dispositionは、それぞれ**範囲の異なる観測**である。Harnessに不足データを推測で埋めさせるより、Productが開示可能な具体的な状態（present/partial/unknown、unsupported、effect unknown等）を既存APIで返し、Harnessは根拠・欠落・保留をそのままConsumerへ届ける設計を優先する。

### 16.1 四つの資格を一件のAttemptで分離する

比較票では以下の観測を同じタスクへ束縛する。ただし新しい横断公開Schema／Proof Store／Oracle Engineではなく、TAI #168/#488/#271の**試験記録の列**である。

| 確認内容 | 証拠と失格例 | 保持するOwner |
| --- | --- | --- |
| **D：必要情報の取得範囲** | Product/Source/Revision/Required集合と実Sourceを照合。単なる`validate.ok`、catalog件数、空配列を「必要条件が全件存在」と誤断定したら失格 | TEI #3262/#3482、SEI #767 |
| **T：実Tool情報の完全配送** | raw request→実CLI/MCP output→ordered reply/end→Harness/Consumerで受領したbyte。途中切断、request≠reply、stderr混入、schema差は失格・未知扱い | TAI #168、TEI #2509 |
| **Q：Claimに必要な認識・説明** | 独立Expected/Scope、Meaning未受理/保留、SEI basis/未知と選択根拠。推薦を判断や現在許可へ昇格したら失格 | SEI #767/#677、TAI #488 |
| **E：実行・配送・Outcome** | 現在Host Grant、Operation id、Provider Receipt、Readback、受け手の受領、Goal Outcomeを分離。Socket送受信やTool成功を業務Effectへ昇格したら失格 | EKI #753/#407、TEI #1174、TAI #271 |

D/T/Q/Eが独立であることが核心。**DがPASSでもT未資格なら外部Agentへの成果配送を主張しない**。TがPASSでもQが不十分なら適切に保留できたかを評価する。Eが未実施のread-only仕事では、Eを無理にPASSへ塗り替えず適用外と記録する。結果の類似やすべてのTool exit 0を横断の同等性としない。

### 16.2 次の最小実装・評価変更（初回SK-02の後段）

1. **まず既存TAI #168のP0のみ**：物理的なG0許可Read／拒否Readの正負対、G1/G2完全なTool/Replyと実送出の記録、新規4 Slotと独立Expected。TEI 13/42やEKI socketの局所PASSはP0の代用ではない。
2. **P0成立後の限定H3分析**：TEI `sales.order.submit`の一つの公開・合成モデル調査で、ProductのD列と外部HarnessのT列、独立採点Qを一Attemptで照合する。Tool schemaとSkill有無以外は固定し、H2/H3の回答に「該当Function宣言はboundedに存在する／InvokeやDB更新は実証していない」という適切な限界が残るかを比較する。TEI #3482の旧CIを同時実行の証拠にしない。
3. **後段の対照（別Trial Group）**：TEI→SEIの**H3-A0**は、[SEI Draft #824](https://github.com/hat47x/sei-cognition/pull/824)にて固定TEIの実`source-index`二モードを受け、実SEI CLIでRecommendationを保存→別`resume --json`で再Readする限定ローカル往復まで観測済み（2026-11-08）。これは評価者作成の提案記録であり、SEI Methodが独立に調査した証明、Decision前のUnknown保存や外部DSHのH3資格ではない。**次はA1**としてD0/D1/M1の同一問い・盲検Expected・陰性対照を比較し、Decision前の未決保存は#711/#678へ返す。MCPは別Transportとして後段比較。EKIは同一Task/Attemptの実Result BodyとConsumer受領が取れた場合に追加する。
4. **独自Loop判断はさらに後**：H3改善があればProduct Skill・専門Pluginを先に採用候補とし、同じ重大な未解決問題が二つ以上の外部Harnessで再現するまでHV-4を開始しない。

**優先順位・停止線**：この節は11月8日時点の既存実験の**適用範囲照合と、次の順序の具体化**であり、新しい4 SlotのBlocking要件／新しい実行Tool・Schema／追加Product実装の採用ではない。TEI実Provider／SEI→TAI実Harness Handoff／EKI実別プロセスConsumer／HV-3専門Pluginの増分／臨床利用／独自Loopは**NOT RUN**。最優先は環境実格差を解消してTAI #168の比較可能な試行を成立させることである。

## 17. CSWを独自Harnessではなく探索Methodの選択肢として接続する（2026-11-08）

**実験の参加者条件・評価票・現行Skill原文の固定参照**：[CX-01 独立探索比較プロトコル](../../evaluations/CX-01-csw-exploration-method-transfer-2026-11-08.md)（提案・未実行）。

[CSWの現行README](https://github.com/hat47x/cultural-substrate-weaving/blob/main/README.md)と実Skillを再確認した。mainは**執筆用の3つの軽量Skill**から成る： [cultural-substrate-weaving](https://github.com/hat47x/cultural-substrate-weaving/blob/main/skills/cultural-substrate-weaving/SKILL.md)、[affinity-synthesis](https://github.com/hat47x/cultural-substrate-weaving/blob/main/skills/affinity-synthesis/SKILL.md)、[writing-flow](https://github.com/hat47x/cultural-substrate-weaving/blob/main/skills/writing-flow/SKILL.md)。利用にRunnerやPlugin登録は必要なく、本文をAIへ読ませればよい。**元々の対象は執筆であり、工学上の要件発見・安全性・Product実装への有効性は未検証**。将来の認知MethodやCSW-MAGIは研究案であって、現状3 Skillに固定した全員必須フローや複数Agentの儀式を増やさない。

**YICへの転用仮説**：CSWが価値を持ち得るのは、既存のHarnessに代わるTool/Loop/Authorityではなく、(a)構造の見落としに気づく、(b)異質な枠組みから設計仮説を増やす、(c)表面的に似ているが実際には異なる関係・ライフサイクル・時間軸を発見する、という**探索Methodの限定的活用**である。AIによる探索、Sourceに支えられたDesign Candidate、独立Expectedで検証された案、Ownerが採用したMeaning、生成Targetの実動、Consumerに届いたOutcomeは同一視しない。

| 層／状態 | 適した手段 | 不変の受入境界 |
| --- | --- | --- |
| **自由探索** | CSW原文Skill／任意の発想支援。通常の会話・既存HarnessのSkillロード・直接本文Readのいずれでもよい | 候補の数量/多様性/予想外の分岐を許す。生成案をSource事実、検証済み安全要件と偽らない |
| **設計候補の照合** | TEI標準Graph/Role、Lifecycle/Hook/Atomic Trait、Source Revisionと反例、SEIの根拠・未決 | 原典から借りた関係と工学的に採用した関係を分離。Owner受理前にGuard/Grantを変えない |
| **検証・実装** | TEI #951/#1251/#3278/#3503、独立Scenario/Expected、実Provider/Target/Effect | Source→selected→built→invoked→receivedの実証。PluginのdisableはDB commit rollbackではない |
| **学習と再利用** | 成果と残差を必要時だけSkill/設計パターン候補へ還元 | 実務上の反証と作者判断を別に扱い、Private原稿・秘密・原Tool Logを無許可のSkill配布物へ混入させない |

**設計用の最初の圧力ケース（提案）**：TEI [#3503](https://github.com/hat47x/tei-platform/issues/3503)のPlugin Lifecycle/Interaction Flowに対して、Discover→Select→Bind→Activate→Invoke→Drain→Dispose/Upgradeの想定図を参照し、「固定Guardと可変Hookをどこで分けるか」「更新/再開時に何が失効するか」「Pluginを外した際に不可逆Effectが残るか」を自由探索する。ただしこの順序は**説明用の案であって採用済みのTEI Lifecycle/実装APIではない**。得られた候補は既存[#2090](https://github.com/hat47x/tei-platform/issues/2090)/[#2899](https://github.com/hat47x/tei-platform/issues/2899)/[#3278](https://github.com/hat47x/tei-platform/issues/3278)にFit/Gapとして渡し、CSW固有の新Engine／Rule正本を設けない。

### 17.1 効果測定はH2/H3とは独立の探索実験にする

他チャットで提案された「通常AI支援／一般的発想支援／CSW」の3条件を**CX-0/CX-1/CX-2**（本節の局所ラベル）とする。TAI #168のB0 CLI/B1 H2/B2 H3、HV-0〜4とは**別母数・別Treatment**であり、勝率を合算しない。

| Arm（提案） | 同じTask/資料/予算/モデル・権限 | 何を検出するか |
| --- | --- | --- |
| CX-0 | 通常の設計AI支援。追加Methodなし | 既存Issueや設計だけで足りるか |
| CX-1 | 同じAgent/Toolに一般的な発散・批評の指示を追加 | CSW固有でない通常の発想支援の効果 |
| CX-2 | **CSW現行Skillの必要部分だけ**を実Readして探索（元のSkillの著者向け用途とは別の探索実験） | 独立した設計反例／有効な新差分が増えるか、誤類推や保守負担を増やさないか |

**比較単位**：同じTEI LifecycleのSource/Issueと独立の判別観点・Blind Reviewを事前固定。生成候補数ではなく、既存設計に無い**根拠追跡可能で独立反証に耐える具体的な差分**、安全境界の過大推論、採用候補への到達所要時間、検証・手戻り・Token/外部送出コストを分ける。原文を評価者や通常Armが事前に見ていたら露出混入として記録。3条件は候補発見の比較であり、**Safety Guardの通過率や臨床適格性をCSWに与えない**。初回の小Taskは方法の判別力点検であり一般的な効果量を主張しない。

**DSHへの導入順**：(1)まずスキル本文を直接読ませる（DSH不要）、(2)読み込みの自動化が本当に役立つ場合だけ既存DSHのSkill/Profileを使う、(3)イベント・Tool・Session接続で固有の実益が実証された場合だけ薄いDSH Pluginを検討。**Cultural Substrate Weavingの執筆用原文・3 Skillの選択はCSW RepoがOwner**。Engineering用の有効性はTAI/TEIの限定試験として扱い、CSW本体へ勝手に産業用の規範・Plugin ABI・Router・CIを付加しない。

**状態と優先度**：CX実験、CSW→TEIの正式適用、DSH Skill/Profileによる実改善・Plugin効果は**NOT RUN**。最優先は既存TAI #168のG0物理隔離→G1/G2完全Delivery→新規独立4 Slot（現在0/4適格）を維持する。CSWはその**前提Gateにも、すべての開発Taskにロードする常時依存にもならない**。

## 18. TEI→SEIローカル往復の実証が示した「独自Harness以前」の到達点

[SEI Draft #824 H3-A0の限定実証](https://github.com/hat47x/sei-cognition/pull/824)で、固定TEI/SEIの実Go CLIを使ったTEI `source-index`の二モードRead→SEI Recommendation記録→別CLI Resumeの**ローカル二製品往復**が確認された。使用した実TEI `26b79a68...` と実SEI `6d98ddf2...`、TEI CI [#42474971439](https://github.com/hat47x/tei-platform/actions/runs/42474971439)はこの主張の対象版に限る。Recommendationの`--unresolved`は現行CLIではDecision限定のため、未決Inquiryの正式保存やMethodによる根拠十分性評価にはならない。固定Taskが同じ名前でも、他版TEIの13 Reply/42 Controls、TAI H2/H3の比較4 Slotと同一Attemptとして加算しない。

**次の選択（別レーン）**：A1は[SEI #767](https://github.com/hat47x/sei-cognition/issues/767)/[#711](https://github.com/hat47x/sei-cognition/issues/711)の問相対Methodを、同じ問いQ・予算・許可Read・Blind ExpectedのD0（無介入）／D1（決定論的Probe）／M1（Method支援）で比較する。**D1で十分ならM1の追加価値なし**と判定し、未知Questionの保存方式はA2に留保。M1が選んだReadの一部が偶然正答に見えても、Required Source範囲と実Read byte/Consumer受領を分ける。この手順はCSWのCX比較とも外部H2/H3とも別の評価体系であり、異質なArmの結果を混合しない。

**投資上の帰結**：TEIとSEIの局所連携は、新しいYI Harness Runtimeを導入せずに既存CLIで一部成立した。一方で外部Harnessの独立Skill増分、Unknownを保持した適応活動の継続、実Providerの副作用検証は未資格。機能の不足箇所がProduct/Transport/認知Methodで解けるうちは、HV-4の独自Loopではなく該当Ownerの狭い改善を先に測る。
