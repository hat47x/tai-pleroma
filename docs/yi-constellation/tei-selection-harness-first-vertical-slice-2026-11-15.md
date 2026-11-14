# TEIで選んだ設計要素をAIへ渡して戻す：最初の実行票

**状態：実行計画／新しい実行はNOT RUN。** [横断計画§49](harness-cross-ui-session-probe-2026-11-14.md)の実装者向け短縮版。新しいCLI名、公開API/ABI、Context Store、Runner、Host、権限正本、受入基準の第二正本は作らない。

## 最初の利用者の仕事

TEIで公開Reference Workspaceの一つの設計要素（例：semantic-data / sales.order）を選ぶ。「役割と依存関係を説明してほしい」と外部AIに依頼する。AIの返答は元の対象に戻し、現在別の要素を表示していても誤って反映しない。Sourceが変わっていれば旧回答を候補として保持し、再読取する。最初は**読み取り専用の説明と候補の受領まで**。

## 6つの操作と実行担当

| 順番 | 現在利用するProduct／Harnessの入口 | 合否と停止線 |
| --- | --- | --- |
| 1. 対象を指定 | TEI CUIの実CatalogでSubject KindとCanonical IDを取得。Studioは#4515の明示Pinを後続利用 | Focusや表示ラベルで代用しない。Workspace/RootとSourceを区別。GUI Pin未実装ならCUI固定入力で続行 |
| 2. TEIで再確認 | 現行Inspect、Locate、Trace、Validate、Host-owned Reader | 実Subject存在、版、Source位置、診断、関連の取得範囲を保持。空Indexを不存在としない |
| 3. 送信前に準備 | Product/Hostが用途・Audience別に許可した短いProjectionをPreview | 受信先、送信予定内容、除外・unknownを確認。生File Path・秘密のID/件数/Digest等を既定で送らない |
| 4. 外部へ配送 | 実在するProduct CLI/MCP等のTool、または当該Harnessの適格Native Session | 実Tool Call、送出byte、実Reply終端、受信者、Current Grantを別観測。準備・ログ出力だけを実送信としない |
| 5. 元の対象へ返す | 元RequestとPin/Activity/Sourceを対応付け、Product側で現在対象を再検証 | 遅延Reply、別Workspace、Pin変更、旧Sourceでは候補として保持。現在Focusへ自動Applyしない |
| 6. 必要時の変更 | TEI既存のDiff、診断、明示適用、Owner受理 | 今回のread-only実証では対象外。AIの説明・Diff・Tool Replyは書込みや実Effectの証拠でない |

**入口と配送の二軸**：CUIでの実CLI指定／Studioでの明示PinはProductの選択入口。既存Native Sessionへの配送／TAI Activityから新Sessionへの限定Handoffは運搬方式。Session共有不能なら新Sessionへ縮退し、旧Grantや全Transcriptを渡さない。既存yi.handoff.context/v1が必要なRoot・Relation occurrenceを表せなければunsupportedとして止め、架空の欄を加えない。

## 現行CLIから始める基線（実行例、今回未実行）

実装時にTEI checkout、Go版、Workspace原byte、Tool version、HEADを記録し、最新のdocs/getting-started.mdとコマンド発見結果を確認する。

~~~sh
go run ./cmd/tei commands
go run ./cmd/tei model catalog -workspace reference/workspace
go run ./cmd/tei model locate -workspace reference/workspace -subject-kind semantic-data -subject-id sales.order
go run ./cmd/tei inspect -workspace reference/workspace -subject-kind semantic-data -subject-id sales.order
go run ./cmd/tei validate -workspace reference/workspace -json
~~~

同一World Fingerprintだけで別Rootの同一性や現在の権限を主張しない。modelRevisionは管理Sourceの版であり意味受理ではない。Catalogの操作成功とvalidation.okを分け、Validate Exit 0でもWarningsを残す。Related Graphに描かれたparent:のEdge IDは業務Relation occurrence IDではない。必要な関係が未解決なら完全な依存Graphとは言わない。

## 実装するのは二つの独立レーン

**S：TEI Product／Workbench（TEI #4515、#3788、UX Draft #4605）**  
S0：一つの公開Subjectについて、実CLIでKind/ID・Source・版・診断・unknownを実観測する。S1：[Pin Draft #4597](https://github.com/hat47x/tei-platform/pull/4597)の局所状態遷移を現Workbenchの実Inspect応答・DOM表示へつなぐ。**Pin Aを背景で再読しても、現在閲覧中のBのread-only表示、Graph、Focus、Noticeが変わらない**ことを実Consumerで確認する。現在のEditorはread-onlyなので、Dirty Buffer/Undo/IME保持は将来の編集可能Consumerで別検証し、S1の合格にしない。

**H：YIC外部Harness接続（TAI #168、#271、#232、QH §10）**  
H0：S0の公開Resultから許可された短い作業Contextを生成。Task・対象・Source/Scope・unknown・返却先を区別し、詳細は必要時にHostへ再問合せ。Pluginの上位公開図・Manualは[TEI #4679](https://github.com/hat47x/tei-platform/issues/4679)の短いProduct Skill＋Document Indexから必要時だけ取得。全Manual/生Source/Session全文を常時注入しない。H1：TAI #168のG0 OS Read-deny→G1実Egress→G2完全Tool Replyの適格実装を確認した**別の後続Trial**で、Tool-onlyの実送受信・完全Reply・元Requestへの帰属を検証。固定H2/H3四Slotに新しい条件を増やさない。H2：Session継続できないときはActivityから現在資格を再確認して新Sessionへ。H3：返却候補を元Subjectへ結び、現在Sourceで差分・再診断。Source write/Build/Owner Acceptanceは別のProduct検収。

## 初回の独立Expectedへ回す反例

| 入力・故障 | 成立してほしい結果 |
| --- | --- |
| 別Rootに同じKind/IDと同Hash | 元Rootを取り違えず、現在資格不明なら送信保留 |
| Pin Aの背景Inspect中にFocus B | Bのread-only UI非干渉、旧Reply表示0 |
| A→B→Aと古い結果の遅延到着 | 古い観測・Grantが自動復活しない。現Focusへの書込み0 |
| Index・Traceの空/partial/unknown | 不存在/全件取得へ誤昇格しない |
| Tool Reply終端なし、ACKのみ、Local PathをRemoteへ渡す | 完全受領・実Source取得を主張しない |
| Preview後にGrant撤回 | 送信前に再資格化し拒否。送信済み情報の完全撤回は主張しない |
| 保存済みR0に基づくAI案、編集途中Buffer R1 | 勝手にR1へApplyしない。現read-only EditorでDirty保持を実証したとはしない |
| 上位Pluginの非公開Manualを下位Plugin経由で要求 | 公開範囲外の存在・ID・内容・件数を漏らさず拒否 |

記録先は既存[QH §10](cross-product-handoff-execution-tickets-2026-11-11.md)の**I（Intent）／R（Product再解決）／P（Disclosure）／T（Transport）／C（Consumer）／H（Harness）**。各列に実Source/HEAD/Attempt、Input、期待/実結果、欠落、受信側の再読取、Ownerを残す。価値比較は送信byte/Token、追加Fetch数、Tool往復、誤対象、確認工数を測り、長いSkill全文ロードを必須にしない。

## 優先順位と停止線

- **独立P0-A**：TEI [#4583](https://github.com/hat47x/tei-platform/issues/4583)の非Plugin Studio Stage1→Stage2実Windows Desktop。#4597のPin純粋testや旧生成WebView CIとは別。
- **独立P0-B**：TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)のG0→G1→G2→物理的に独立したH2/H3四Slot（直近比較適格0/4）。
- **後続接合**：S0→S1とH0→H1の二レーンを独立に進め、S1/H1が各自合格してから同一Subjectの一往復を試す。正式なRelation Pin、Writable Editor、Quick Fix、二Harness比較は別の採用判断。

**完了したこと**：着手順・実入口・別Owner・負例・観測列を一つの短い実行票にしたことのみ。**未実行**：新TEI CLI検証、Workbench Pinの実UI結線、実Harness、外部詳細Fetch、AI回答の元Subject実帰着、正式Owner受理。mainへ自動Mergeしない。
