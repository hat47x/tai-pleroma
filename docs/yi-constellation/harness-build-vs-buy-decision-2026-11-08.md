# YI Constellation：外部Harness活用と独自Harness投資の段階判断（2026-11-08）

**状態：Ownerレビュー用の設計・投資判断案。独自Harness実装の決定ではない。**  
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
| KON Dataspace | データの着地・取得・履歴・複数Consumer向けの足場の構想。**第二Canonical/必須クラウド/Agent Session Storeに直結しない**。二Consumer実消費までは独立基盤の採用を保留 |
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
- **Product Owner**：TEI/SEI/SUI/SHO/EKI/KON/OKFそれぞれの受理・公開・実装判断を維持。YI横断構成が単独Productの価値・完成条件を増幅／先取りしない。

**未実施**：上記HV-0〜HV-4の同一母集団での独立比較、HV-3の実専門Pluginの増分、実臨床検証、二Harnessの実隔離適格試験、複数年TCO採点、Ownerによる独自Loop投資受理。これは2026-11-08時点の設計・実験計画であり、実装済み認定ではない。
