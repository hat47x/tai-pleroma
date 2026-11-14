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


## 現行Workbenchへの接合点とCI停止要因（2026-11-15照合）

次の実装担当が迷わないよう、[Pin Draft #4597](https://github.com/hat47x/tei-platform/pull/4597) の固定HEAD a9c91e56eecdb6b588064188490fc3de950c1744、同HEADのGitHub Actionsログ、現mainを照合した断線を記録する。これは**既存コード・CIの読取り**であり、今回新たにGo／Node／Windowsを実行したものではない。

### 背景Pinの再取得に、現在のInspectをそのまま使わない

- TEIの reference/tei-studio-workbench/main.ts にある現行 inspect(subject) は、selected、タイトル、editor.setDocument、graph.update、Graph選択、noticeをまとめて更新する。したがってBを閲覧している間に、Pin Aをこの関数で裏から再検査すると**Bの画面を変更してしまう**。
- 既存 pin-state.ts（Pin／Unpin／Undo／Invalidate／pinRequest／acceptPinObservation）と responses.ts の**独立レーン pinned-inspection**を実Workbenchへ接続する。通常の inspection レーンには触れず、対象を固定したときだけHost-ownedの client.inspectSubject(workspaceID, kind, id) へ問い合わせる。呼出し前に inspectEligibility、応答後に readInspection で対象・Catalogueとの一致を確認する。これらの検査が成功しても現在のGrant、Disclosure、Owner意味受理まで自動的に成立したことにはしない。
- 要求発行時のPin世代、Workspace epoch、Kind/IDを保持し、遅着時には acceptPinObservation で厳密に照合する。Pin解除／再Pin／Workspace切替／A→B→A／同一レーンの後続要求で旧結果を失効。Pin状態の変更が、現在のBのEditor・Graph・Focus・Noticeを変更しないことを実DOM/Consumerで確かめる。
- 初回は明示Pin/Unpinの一Subjectだけ。FocusやEsc/IMEによって勝手に解除せず、Relation描画用の parent: Edge IDは意味Relation occurrenceと見なさない。外部HarnessへのContext共有ボタンやWriterを、PinのProduct Reader実配線より先に合格扱いしない。

### 現行の実CI失敗は二つの別原因

| 固定HEAD a9c91e56 の観測 | 結果と次の対処 |
| --- | --- |
| Studio Pin intent state contract | **completed/success**。局所状態と非同期レーンのテストは合格。ただし実main.ts、Wails WebView、外部Harnessの成功ではない |
| [TEI PR・main 健全性確認 run 43574298349](https://github.com/hat47x/tei-platform/actions/runs/43574298349) | **failure**。TestPlanReadmesMentionEveryEntry が CONSUMER_QUALIFIED_CROSS_LANE_ACCEPTANCE_2026-11-14.md の索引漏れを指摘。現mainの plan/design/README.md には該当リンクがあり、このPin Draftブランチにはない。まずmainとの整合を取り、独立に再テストする。Pinの機能不具合と混同しない |
| [Workbench embedded bundle run 43574298492](https://github.com/hat47x/tei-platform/actions/runs/43574298492) | **failure**。Node test／typecheck／buildの後、生成 dist/main.js とDesktop収録 cmd/tei-studio/assets/workbench/main.js はbyte 649340、line 18643で不一致。同じHEAD/Toolchainで正規の生成元から再ビルドし、実埋込byteとの一致を検査する。生成済みJSだけを手修正してPASSとしない |
| [生成Desktop Draft #4587](https://github.com/hat47x/tei-platform/pull/4587) HEAD 9b58533d | そのHEADの12 Workflowは成功。ただし別PR/別HEADのWindows B0限定結果。#4597のPin UIや、非Plugin Stage1→Stage2実再構築、外部Harness実接続の受入には流用しない |

**現時点の次の実装仕事**：正規の main.ts に明示Pinと背景Readerを配線→現WorkbenchでBの表示/Graph/Focus/Notice非干渉を実DOM/Clientで確認→同一HEADのPin test・型検査・生成/埋込byte一致を確認→必要な範囲で実Windows Wails/WebView2のHost InspectSubjectを観測。各段階は独立したEvidenceとして記録し、実Source/Grant/外部送信/Owner採用を勝手に合算しない。TEI #4583のP0とTAI #168のG0/G1/G2・独立H2/H3四Slotは、どちらも追加のBlocking条件なく継続する。

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


<!-- yic-pin-bundle-current-status-20261115 -->
## 11月15日の再照合：PinのCI是正と生成Bundleの再現性

**索引漏れについて実際に修正したこと**：[TEI Pin Draft #4597](https://github.com/hat47x/tei-platform/pull/4597) の plan/design/README.md に、現行mainに存在する CONSUMER_QUALIFIED_CROSS_LANE_ACCEPTANCE_2026-11-14.md の参照を**一行だけ**復元した（[commit c8f90425](https://github.com/hat47x/tei-platform/commit/c8f904258257e7f1f1e1f4436bca71fc4e2c1a3e)）。これは失敗ログに現れた欠落への修正であって、GitHub Actionsの新HEAD合格・PR全体合格は**未確認**。

**Bundle不一致について新たに確認できたこと**：固定した比較対象はPin Draft #4597の旧HEAD a9c91e56...と、Windows検証Draft [#4587](https://github.com/hat47x/tei-platform/pull/4587)のHEAD 9b58533d...。両者の reference/tei-studio-workbench/main.ts、build.mjs、package-lock.json のGit blobは一致する。一方、同じmain.tsがimportする presentation.ts はそれぞれ 06d329bd...／cd4319a6... で異なり、Desktopに埋め込まれた main.js も 27b2b9a4...／7c3225ee... で異なる。**同じEntry Sourceでも推移依存が違えば生成物を流用できない**。この事実だけで旧HEADのbyte 649340不一致の真因が確定したわけではない。成功した#4587の生成JSを#4597へコピーする対応は採らない。

### 残る修復と合格条件

1. **#4597の最新HEADでCI再確認**：索引漏れのテストとPin契約テストを別に記録し、Healthが本当に通ったか確認する。旧HEAD a9c91e56 のCI結果を新commit c8f90425 の結果と取り違えない。
2. **Bundle生成の原因特定**：実際に使用されたNode/esbuild・lockfile・全推移Source・build script・Outputを同一HEAD・同一Attemptで固定し、dist/main.js と cmd/tei-studio/assets/workbench/main.js の最初のbyte差と原因を確認する。正規生成から配布Assetへ反映して再比較。Sourceファイルが同じでも依存presentation.tsが違えば別Build Closureとして記録する。手書きJSや他PR生成物の横流しで見かけのPASSを作らない。
3. **Pinを画面へ接続**：PIN-R0の最初の実装は、main.tsの現行inspect(subject)を背景Pinから呼ばず、既存pin-state.tsと独立pinned-inspection laneからHost-owned Readerを読む。閲覧中Bの表示・Graph・Focus・Noticeが不変、AのPin世代・Source版が一致しなければ旧Resultが表示されない、をDOM/実Hostで独立検証。
4. **送出・編集は別**：PinのProduct-local成功から外部Tool受領やCurrent Disclosureを推定せず、AIの候補を未保存Bufferへ無音Applyしない。TEI #4583非Plugin Desktop B2/B3、TAI #168のG0/G1/G2・独立H2/H3四Slotは並行独立P0のまま。

**観測範囲**：上の修正はGitHub上で一行のSource修正を実施した事実。CI結果の差分確認、生成実行、Node/Windows実E2E、Pin UIと外部Harnessの実受領はこの追補時点では新規実行していない。GitHub Draftは未マージであり、Owner正式受理を意味しない。


<!-- yic-pin-readonly-actual-implementation-20261115 -->
## 実装追補：Pinの背景読み取りをWorkbenchへ接続（新HEADの実機検収は未完了）

[TEI Pin Draft #4597](https://github.com/hat47x/tei-platform/pull/4597)の専用ブランチで、対象を固定・解除・再確認するUIと背景のHost-owned Inspect呼出しを追加した。実装Sourceコミットは[背景Reader 2eee5fbf](https://github.com/hat47x/tei-platform/commit/2eee5fbf86371d83f7f7ced21eaa7e596991b7fc)、[UI 94f196d8](https://github.com/hat47x/tei-platform/commit/94f196d8231ac979e893e7f8fb9bf4553d0641e2)、[Style df79b1ad](https://github.com/hat47x/tei-platform/commit/df79b1ad2fe70e2a759b24601518cecfd16c502e)、[投影テスト 52fa6b64](https://github.com/hat47x/tei-platform/commit/52fa6b64999d7804b543c43000fee509df0de91b)（Draft・未merge）。

- 一時選択と固定対象を独立させたまま、固定Aの再確認は専用の pinned-inspection 応答レーンで実行する。Aの非同期結果から閲覧中BのEditor、Graph、Focus、Noticeを書き換えるコードを置かない。
- 呼出し前は既存Catalogで対象の一意性を検査し、実Hostの InspectSubject 応答に既存 readInspection のSubject/World/Source Index Fingerprint検査を通す。固定要求のWorkspace epoch/Pin generationが変わった旧応答は採用しない。これは**read-only Product観測**であってCurrent Grant/外部Disclosure/編集資格の証明ではない。
- Unitテスト PIN-READER-01/02を既存 responses.pin.test.mjs へ追加。対象Aと結果Bの不一致、World/Source Index Fingerprintの旧版を含めて検査する。テストはSourceとして追加した段階であり、**新HEADでの実行合格は未確認**。
- この時点のUIは現在read-only Editorに接続された一Subjectだけ。モデルのSource本文/診断全量やRelation occurrenceを新しいHarness Schemaで送る機能、AI受信結果のReview/Applyは**実装していない**。

### 次の検収順と棄却条件

1. **Source/Node契約**：最新HEADで Pin/Reader 既存・追加テスト、型チェック、通常のWorkbench Buildが成功すること。失敗時は対象SourceとToolchain/正規生成入力を固定し、原因を切り分ける。
2. **配布の同一性**：生成JSとDesktop収録JSを正規生成・同一HEADでbyte照合すること。以前から存在するBundle不一致は、本UIコード追加だけで修復されたと扱わない。異BranchのJS/Artifactを流用しない。
3. **実DOM/Hostの非干渉**：B表示中にAを固定して裏で再取得し、BのEditor/Graph/選択/Noticeが変化しないことを実WebView/Host Consumerで観測。Unpin、Pin A→B→A、Workspace A→B→A、返信の遅着、Catalog/Source改版、Host拒否、同名異Rootを負例として残す。現在のread-only UIでDirty/Undo/IMEの編集安全を実証したとしない。
4. **外部YIC接続**：上記の実Product Pinと現在のHost Disclosureの別審査を経た後、既存の実Tool/Native Sessionが限定Contextを完全受領し、元Task/PinへReplyを返したことをTAI #168/#271・QH §10のI/R/P/T/C/Hで記録する。手元のPin状態やTool一覧、AI説明だけを送信成功にしない。

**Evidenceの状態**：GitHub SourceとUIのID対応を読戻し済み。新HEADのActions合格、生成Asset一致、実DOM/Windows Host、外部Harness受領、Source再読取、Owner意味受理はこの時点で**未確認**。実装が前進しても、TEI #4583の非Plugin Stage1→Stage2 DesktopとTAI #168の独立H2/H3四Slotを新しい順序制約で妨げない。

## 優先順位と停止線

- **独立P0-A**：TEI [#4583](https://github.com/hat47x/tei-platform/issues/4583)の非Plugin Studio Stage1→Stage2実Windows Desktop。#4597のPin純粋testや旧生成WebView CIとは別。
- **独立P0-B**：TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)のG0→G1→G2→物理的に独立したH2/H3四Slot（直近比較適格0/4）。
- **後続接合**：S0→S1とH0→H1の二レーンを独立に進め、S1/H1が各自合格してから同一Subjectの一往復を試す。正式なRelation Pin、Writable Editor、Quick Fix、二Harness比較は別の採用判断。

**完了したこと**：着手順・実入口・別Owner・負例・観測列を一つの短い実行票にしたことのみ。**未実行**：新TEI CLI検証、Workbench Pinの実UI結線、実Harness、外部詳細Fetch、AI回答の元Subject実帰着、正式Owner受理。mainへ自動Mergeしない。
