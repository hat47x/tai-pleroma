# TAI中心のクリティカルパス（2026-10）

状態: **Draft（計画・参照実装の記録）**。5基盤への参照接続は追加済みですが、実製品間の通し接続、人間の承認、利用者価値の確認は未実施です。

## 目的

TAI Pleromaを中心に、TEI / SEI / SUI / SHO（MMI） / EKIを一つの知的機能として接続するまでの順序を、**利用者の課題から観測できる成果**で整理します。接続製品数や設計文書の枚数を進捗にしません。

対象は[SCN-001 共同利用スペースの案内改善](../scenarios/SCN-001-shared-space-guidance.md)です。

## 現在地

| 基盤 | 現在確認できること | SCN-001での役割候補 | クリティカルな不足 |
| --- | --- | --- | --- |
| TAI | SCN-001、責務境界、評価条件、手動トレース例がDraft。合成walkthroughの参照評価を追加 | 観測・仮説・Draft・判断・再観測の参照関係を維持する | 人間の判断、実基盤接続、利用者価値 |
| SUI | 意味形成、カード・島、候補と保留、出典へ戻るUIをREADMEで説明。API到達性、DocumentV1の3 card/2 island/1 edge、SCN-001観測とのdigest照合を参照接続 | 観測カードと複数仮説の意味形成 | 実データ・テナント・認可、意味形成の正しさ |
| TEI | CLI、参照Workspace、モデル検証・生成等の参照実装。SCN-001型のvalidate参照接続を追加 | 規程候補のモデル化・検証（必要性が確認できた場合） | 施設規程の正式モデル、実データ、実実行先、受理 |
| SEI | 意味の区別、来歴、semantic-contract、限定的な参照実行。SCN-001のdecision-memory projection参照を追加 | 観測・解釈・決定の意味分離と来歴 | 実運用store、権限、公開、契約適合 |
| SHO（MMI） | 読み取り専用MCP/CLIの文書読出し・検索・検査。TAIからの`inspect`参照接続を追加 | 原資料の参照、案内文の組立て・レビュー | 実運用の認可・版固定・書込み契約 |
| EKI | 範囲・期限・信頼に応じた限定委任の構想とArchitecture Baseline。CLI起動、Control API認証、合成Taskの`queued`受理を参照接続 | 承認済み処理の限定委任 | Worker実行・結果・委任完了、実Provider・Task、Authority |

静的な確認の出典と固定版は[接続調査](../integrations/capability-inventory.md)にあります。この表は接続済みを意味しません。

## クリティカルパス

### CP-0 意味と権限の境界を固定する（人間）

- 観測 ≠ 解釈 ≠ 提案 ≠ 承認 ≠ 実行 ≠ 結果を、シナリオ上の記録項目として維持する。
- 案内文の意味を受理する担当、公開権限、緊急時の停止条件を決める。
- **2026-10-26のOwner指示**: 実装を止めないため、`development-review-only`の仮承認で先へ進む。実際の公開権限・Authorityは未確定であり、`reviewTrigger=real-object`で実物ベースの再レビューを必須とする。再レビュー条件は[SCN-001実物ベース再レビュー](../evaluations/SCN-001-real-object-review.md)に置く。
- **Gate**: 仮承認は公開・外部作用を許可しない。公開・外部作用は、実在の担当・権限・停止条件が確認されるまで実装しない。

### CP-1 合成walkthroughで参照関係を検査する（実施済み・参照のみ）

- [reference-scn001](../tools/reference-scn001/README.md)がT0/T1/T2のfixtureを評価する。
- P-01〜P-05、P-07、N-01〜N-04/N-06/N-07の機械検査可能な部分を確認する。
- P-06（主体規模比較）とN-05（EKI委任）は`not-run`のまま残す。
- **Gate**: `passed=true`は合成fixtureの整合だけを示す。人間の手動一巡や受入合格にはしない。

### CP-2 読み取り専用の参照接続を基盤ごとに確認する（参照のみ）

- 第一候補はSHO（MMI）の読み取り専用MCP/CLIによる原資料参照とする。理由は、SCN-001のO-02/O-03のような文書断片を、書込み・権限付与なしで扱えるため。
- [reference-mmi-readonly](../tools/reference-mmi-readonly/README.md)で、MMI MCPの`initialize`、`inspect`、`select`、O-02/O-03の文言差の保持、ワークスペース外・missingの拒否、呼出し前後の原本digest一致、MMI commit/`package-lock.json`/Node versionの記録を確認した。
- [reference-scn001](../tools/reference-scn001/README.md)の`-mmi-receipt`で、MMIの`selected`をO-02/O-03/O-07へ重ねる参照経路を追加した。Draft・仮説・判断はfixtureのままであり、実データと合成評価の混合である。
- [reference-tei-model](../tools/reference-tei-model/README.md)で、SCN-001の`Observation`/`RuleCandidate`型をTEIの`validate`で検証した。型宣言だけであり、実データ・意味・Authorityは未検証である。
- [reference-sui-api](../tools/reference-sui-api/README.md)で、SUI APIの`/healthz`・`/openapi.json`・`/docs`と、3 card/2 island/1 edgeのDocumentV1を一時DBで確認した。[reference-sui-link](../tools/reference-sui-link/README.md)がcard digestとisland構成をSCN-001観測へ照合した。実資料・テナント・認可は未検証である。
- [reference-eki-cli](../tools/reference-eki-cli/README.md)と[reference-eki-api](../tools/reference-eki-api/README.md)で、EKIのCLI起動、Control API認証、合成Taskの`queued`受理を確認した。Workerは起動しておらず、実行・結果・委任完了は未検証である。
- これらは**ローカル開発チェックアウトへの参照接続**であり、実運用の認可・版固定・複数利用者・書込みは未確認。
- 接続できた事実と、内容の正しさ・規程の確定を分ける。
- **Gate**: 再現手順、固定版、負例（読取失敗・版不一致・参照切れ）が残るまで次へ進まない。

### CP-3 判断・成果物・再観測を一つの記録で往復する

- CP-2の実資料参照とCP-1の参照関係を、利用者の一回の案内改善で往復する。
- 新しい観測O-06/O-07でDraftを改訂し、旧版・旧判断・新しい未確定を混在させない。
- [reference-sei-decision](../tools/reference-sei-decision/README.md)で、SEIの一時storeに`dec-01`と`authority:unknown`、`dec-02`（development-review-onlyの仮承認）を記録し、`resume`のprojectionだけを読む参照経路を追加した。合成fixtureであり、実在の人間の判断ではない。
- 同ツールの`-basis-bundle`と`-decision-validity`は、合成portable bundleから原記録の根拠参照と、旧Decisionの現行対象への構造上の束縛を読む。`-decision-validity`は、SEI CLIで作る実storeのDecision（ExactBindingのbasisを持たない）を比べられず、指名しても両フラグを未確認（null）にする。受理の有効性は判定しない。
- [reference-scn001-run](../tools/reference-scn001-run/README.md)で、MMI・SEI・SCN-001評価・D-04レビュー成果物・SUI linkを1回の参照実行に束ね、`runDigest`付きのreceiptを生成した。`humanReviewed=false`、`authorityVerified=false`、`published=false`のままである。
- [reference-scn001-render](../tools/reference-scn001-render/README.md)で、D-04を`provisional`・`publicationApproved=false`・`reviewTrigger=real-object`の内部レビュー用Markdownとして生成した。公開用の成果物ではない。
- 同ツールの`-owner-packet`で、権限者・P-06・N-05・初回範囲の判断を求める`awaiting-owner` packetを生成できる。これは承認ではなく、Owner判断の入力である。
- **Gate**: 人間の判断と、独立した成果観測が記録されるまで「知的機能として成立」としない。

### CP-4 主体規模・委任・実行先を比較する

- 個人・組織・社会の違い、EKI委任の利益、TEIモデル化・SHO編集・SUI意味形成の必要性を、CP-3の記録から判断する。
- SUIのcard/island/edgeは参照接続済みだが、実資料・認可・意味形成の正しさは未確認。
- EKIは合成Taskの`queued`受理までで、Worker実行・結果・委任完了は未確認。
- **Gate**: 委任成功コードや生成物の存在を、業務効果・内容の正しさの証拠にしない。

## 依存関係と停止条件

- CP-1はCP-0の権限確定を代替しない。
- CP-2はSUI/TEI/SEI/SHO/EKIの全接続を意味しない。一つの読み取り専用接続に限定する。
- CP-3/CP-4は人間の判断、実データ、実権限を必要とする。
- 不明な版・取得失敗・相反する観測は`unavailable`/`未決`として保持し、最新資料を無条件に採用しない。
- 新しい中央Host、統一DB、共通Contract、TAI固有の状態正本は、必要性が観測されるまで作らない。

## TAI追加を踏まえた優先順位（2026-10-26）

TAIの最初の成果は、一件の案内改善で根拠・判断・成果物・再観測をたどれることとする。各基盤は独立して開発を続け、SCN-001で必要な接続だけを既存の仕組みで検証する。

| 優先 | 対象 | 次に確かめること | 依存と残る判断 |
| --- | --- | --- | --- |
| 1 | 資料から成果物までの対応（[TAI #28](https://github.com/hat47x/tai-pleroma/issues/28)） | 同じ観測集合からの生成に加え、保存後に読み直したD-04のbytesと実行記録の一致を確認する。差替え・欠損・改行変換を成功にしない | 原資料の真正性とMMI選択ID・版の整合は別途確認する |
| 2 | 更新後の判断の扱い（[TAI #33](https://github.com/hat47x/tai-pleroma/issues/33)） | 合成bundleで、旧い判断のExactBindingが現行対象と一致しない、または閉じるlineage（supersedes/withdraws）が参照する場合に、構造上束縛されないことを検査する（`reference-sei-decision -decision-validity`、実装済み）。最初から未受理のA→B→Aとは区別する | 意味受理・期間・権限・実資料は未確認で、構造上の束縛は受理の有効性を意味しない。lineageのfrom/toの向きと、relationがDecisionの受理へ及ぼす効果はSEIが定めておらず、向きを仮定せずfail closedで扱う（revisesを閉じない扱いはTAIの暫定仮定）。現行N-01（文言・版・未公開の合成検査）とは別 |
| 3 | 実物による一巡（R-01〜R-05） | 実資料、担当と権限、実store、独立レビューを特定版に結び付ける | 人による意味の受理と公開権限の判断が必要。証拠未取得のまま公開へ進めない |
| 必要性の確認後 | SUI・TEI・SHOの追加接続 | 複数仮説の比較、規則モデル化、文書編集が一巡をどう改善するかを観測する | 既存の読出し・型検証を、実データの意味受理や保存・commitの成功と混同しない |
| 委任する場合 | EKI（N-05 / R-07） | 委任しない場合との利益、限定範囲、独立した結果確認を比較する | 実Provider・Task、認証、通信契約はEKI側の条件。委任不要の案内改善の前提にしない |

この順序は実装・検証の優先順位案であり、初回の業務範囲やP-06/N-05の採否を決定するものではない。人の判断を要するR-01〜R-07の準備は並行できる。公開gateがblockedでも、読み取り専用の参照実装と負例の検証は続けられる。

### 各基盤の現在版と、TAIの証拠の版

今回確認した版はTAI `ccd49fa`、TEI `490dd20`、SUI `b0f5bae`、EKI `84f03d1`の各main。これは履歴・作業範囲の確認であり、これらの組合せで製品間の通し試験を実行した記録ではない。MMI・SEI・TEIの参照接続で使った版は[接続調査](../integrations/capability-inventory.md)と各receiptに固定し、新しいmainの版へ読み替えない。

EKIでは別プロセス間の試験用TLS配送（[#220](https://github.com/hat47x/eki-fabric/pull/220)）と不完全な受理確認の拒否（[#221](https://github.com/hat47x/eki-fabric/pull/221)）がmainにある。これはSCN-001の委任接続、Worker認証方式の採用、[通信契約 #198](https://github.com/hat47x/eki-fabric/issues/198)の確定を示さない。TEIの実DB・Host・作用境界、SUIの候補とレビューの境界も、それぞれの製品のIssue・PRで検証する。TAIで別の実装や状態正本を作らない。

この計画はDraftであり、製品採用・意味の受理・権限付与ではありません。
