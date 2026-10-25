# TAI中心のクリティカルパス（2026-10）

状態: **Draft（計画・参照実装の記録）**。実製品間の接続、人間の承認、利用者価値の確認は未実施です。

## 目的

TAI Pleromaを中心に、TEI / SEI / SUI / SHO（MMI） / EKIを一つの知的機能として接続するまでの順序を、**利用者の課題から観測できる成果**で整理します。接続製品数や設計文書の枚数を進捗にしません。

対象は[SCN-001 共同利用スペースの案内改善](../scenarios/SCN-001-shared-space-guidance.md)です。

## 現在地

| 基盤 | 現在確認できること | SCN-001での役割候補 | クリティカルな不足 |
| --- | --- | --- | --- |
| TAI | SCN-001、責務境界、評価条件、手動トレース例がDraft。合成walkthroughの参照評価を追加 | 観測・仮説・Draft・判断・再観測の参照関係を維持する | 人間の判断、実基盤接続、利用者価値 |
| SUI | 意味形成、カード・島、候補と保留、出典へ戻るUIをREADMEで説明 | 観測カードと複数仮説の意味形成 | 実データの読出し・受渡し契約、認証済み操作 |
| TEI | CLI、参照Workspace、モデル検証・生成等の参照実装。実Target・Authorityは未確認 | 規程候補のモデル化・検証（必要性が確認できた場合） | 施設規程の正式モデル、実実行先、受理 |
| SEI | 意味の区別、来歴、semantic-contract、限定的な参照実行。SCN-001のdecision-memory projection参照を追加 | 観測・解釈・決定の意味分離と来歴 | 実運用store、権限、公開、契約適合 |
| SHO（MMI） | 読み取り専用MCP/CLIの文書読出し・検索・検査。TAIからの`inspect`参照接続を追加 | 原資料の参照、案内文の組立て・レビュー | 実運用の認可・版固定・書込み契約 |
| EKI | 範囲・期限・信頼に応じた限定委任の構想とArchitecture Baseline | 承認済み処理の限定委任 | SCN-001で委任が価値を生むかの検証、実Provider・Task |

静的な確認の出典と固定版は[接続調査](../integrations/capability-inventory.md)にあります。この表は接続済みを意味しません。

## クリティカルパス

### CP-0 意味と権限の境界を固定する（人間）

- 観測 ≠ 解釈 ≠ 提案 ≠ 承認 ≠ 実行 ≠ 結果を、シナリオ上の記録項目として維持する。
- 案内文の意味を受理する担当、公開権限、緊急時の停止条件を決める。
- **Gate**: 担当・権限・停止条件が文書化されるまで、公開・外部作用を実装しない。

### CP-1 合成walkthroughで参照関係を検査する（実施済み・参照のみ）

- [reference-scn001](../tools/reference-scn001/README.md)がT0/T1/T2のfixtureを評価する。
- P-01〜P-05、N-01〜N-04/N-06の機械検査可能な部分を確認する。
- P-06（主体規模比較）とN-05（EKI委任）は`not-run`のまま残す。
- **Gate**: `passed=true`は合成fixtureの整合だけを示す。人間の手動一巡や受入合格にはしない。

### CP-2 読み取り専用の実接続を一つだけ行う（参照接続を追加）

- 第一候補はSHO（MMI）の読み取り専用MCP/CLIによる原資料参照とする。理由は、SCN-001のO-02/O-03のような文書断片を、書込み・権限付与なしで扱えるため。
- [reference-mmi-readonly](../tools/reference-mmi-readonly/README.md)で、MMI MCPの`initialize`、`inspect`、`select`、O-02/O-03の文言差の保持、ワークスペース外・missingの拒否、呼出し前後の原本digest一致、MMI commit/`package-lock.json`/Node versionの記録を確認した。
- [reference-scn001](../tools/reference-scn001/README.md)の`-mmi-receipt`で、MMIの`selected`をO-02/O-03/O-07へ重ねる参照経路を追加した。Draft・仮説・判断はfixtureのままであり、実データと合成評価の混合である。
- これは**ローカル開発チェックアウトへの参照接続**であり、実運用の認可・版固定・複数利用者・書込みは未確認。
- 接続できた事実と、内容の正しさ・規程の確定を分ける。
- **Gate**: 再現手順、固定版、負例（読取失敗・版不一致・参照切れ）が残るまで次へ進まない。

### CP-3 判断・成果物・再観測を一つの記録で往復する

- CP-2の実資料参照とCP-1の参照関係を、利用者の一回の案内改善で往復する。
- 新しい観測O-06/O-07でDraftを改訂し、旧版・旧判断・新しい未確定を混在させない。
- [reference-sei-decision](../tools/reference-sei-decision/README.md)で、SEIの一時storeに`dec-01`と`authority:unknown`を記録し、`resume`のprojectionだけを読む参照経路を追加した。合成fixtureであり、人間の判断ではない。
- [reference-scn001-run](../tools/reference-scn001-run/README.md)で、MMI・SEI・SCN-001評価を1回の参照実行に束ね、`runDigest`付きのreceiptを生成した。`humanReviewed=false`、`authorityVerified=false`、`published=false`のままである。
- 同ツールの`-owner-packet`で、権限者・P-06・N-05・初回範囲の判断を求める`awaiting-owner` packetを生成できる。これは承認ではなく、Owner判断の入力である。
- **Gate**: 人間の判断と、独立した成果観測が記録されるまで「知的機能として成立」としない。

### CP-4 主体規模・委任・実行先を比較する

- 個人・組織・社会の違い、EKI委任の利益、TEIモデル化・SHO編集・SUI意味形成の必要性を、CP-3の記録から判断する。
- **Gate**: 委任成功コードや生成物の存在を、業務効果・内容の正しさの証拠にしない。

## 依存関係と停止条件

- CP-1はCP-0の権限確定を代替しない。
- CP-2はSUI/TEI/SEI/SHO/EKIの全接続を意味しない。一つの読み取り専用接続に限定する。
- CP-3/CP-4は人間の判断、実データ、実権限を必要とする。
- 不明な版・取得失敗・相反する観測は`unavailable`/`未決`として保持し、最新資料を無条件に採用しない。
- 新しい中央Host、統一DB、共通Contract、TAI固有の状態正本は、必要性が観測されるまで作らない。

## 直近の作業

1. CP-1のfixtureと受入条件を人間がレビューし、P-06/N-05の扱いを決める。
2. CP-2の候補をSHO（MMI）の読み取り専用MCP/CLIに限定し、固定版・入力・出力・負例を確認する。
3. CP-0の担当・権限・停止条件を、実在のシナリオownerと合意する。
4. CP-3の一回の往復を、実製品を無理に自動化せず手動で記録する。

この計画はDraftであり、製品採用・意味の受理・権限付与ではありません。
