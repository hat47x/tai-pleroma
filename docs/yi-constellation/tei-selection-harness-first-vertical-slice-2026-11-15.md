# TEIで選んだ設計要素をAIへ渡して戻す：最初の実行票

**状態：実行計画／新しい実行はNOT RUN。** [横断計画§49–54](harness-cross-ui-session-probe-2026-11-14.md)の実装者向け短縮版。新しいCLI名、公開API/ABI、Context Store、Runner、Host、権限正本、受入基準の第二正本は作らない。

**途中で止まった場合**：送信ACK・Native Session ID・AIの回答・実Product Effectを同じ「完了」にまとめない。Source/Grantが変わったら送信前に再確認し、Tool Replyが不完全なら未受領、Sessionを再接続できなければ限定Activity Handoffへ縮退する。元ProductのEffectが不明な場合は再実行せず照会する。実際の表示例とOwner別の停止線は[横断計画§50](harness-cross-ui-session-probe-2026-11-14.md)を参照。

**11月15日の統合状況補正**：[TEI Pin #4597](https://github.com/hat47x/tei-platform/pull/4597)はGitHub上で**mainへマージ済み**。以下の「Draft／未マージ」は当時の検収記録として読み、現在のPR状態とは区別する。Pinの状態遷移が統合されたことだけで、配布Workbenchの生成／埋込byte一致、実Windows WebView2、実外部Harnessとの一往復、現在Root/Disclosureが確認できたわけではない。[TEI #4812](https://github.com/hat47x/tei-platform/pull/4812)の配布Bundle修復試行は**closed/unmerged**であり、別branchの成功を現在mainの配布受入に使わない。別Workerが生成物や同じ契約を修正する際の競合・統合後検査は[並行AI開発の実行票](parallel-agent-integration-first-trial-2026-11-15.md)を参照する。

## 最初の利用者の仕事

TEIで公開Reference Workspaceの一つの設計要素（例：semantic-data / sales.order）を選ぶ。「役割と依存関係を説明してほしい」と外部AIに依頼する。AIの返答は元の対象に戻し、現在別の要素を表示していても誤って反映しない。Sourceが変わっていれば旧回答を候補として保持し、再読取する。最初は**読み取り専用の説明と候補の受領まで**。

**実装前に確かめること**：実CLIで入口を発見できたこと、元Sourceの一意性と版が確かめられたこと、現在の共有・利用資格があること、実際にTool Replyを完全受領したこと、元ProductのConsumerが結果を読んだことを**別々に記録**する。Pluginの選択版／Lockが一致してもDocの帰属・Source Read・外部開示は未確認である（[TEI #4800](https://github.com/hat47x/tei-platform/pull/4800)、[#4714](https://github.com/hat47x/tei-platform/issues/4714)）。Workbench参照側の制限表示[TEI #4806](https://github.com/hat47x/tei-platform/pull/4806)は、実Windows配布と外部共有の許可を保証しない。詳細な再確認条件と負例は[横断計画§51](harness-cross-ui-session-probe-2026-11-14.md)に集約する。

**進め方**：公開SubjectのProduct-only読取は、GUI PinやPlugin文書取得が未完成でも現行CUIで検証する。外部送信はTAI #168の適格な実Host・Tool条件が成立するまで保留し、固定H2/H3四Slotに別Task・新Skillを混ぜない。Native Sessionの再接続不能時は現在資格付きActivity情報だけを新Sessionへ引き継ぎ、旧Sessionの復旧と呼ばない。

**AIへ委任する場合の追加判断**：最初に仕事の目的、元Issue/Source、独立Expected、変更可能な範囲を決めてから、必要な役割と実際に利用できるHarness/Model/Tool/契約経路を選ぶ。TEI [#2017](https://github.com/hat47x/tei-platform/issues/2017)のA0〜A4は**開発作業の権限区分**であって、外部AIへの送信やProductの実行Grantではない。最初の公開一Subject調査はA0のProduct-only／Tool-only基線を維持し、複数モデル・別Harnessへの引継ぎやSkillの増分比較は[横断計画§52](harness-cross-ui-session-probe-2026-11-14.md)の後続作業とする。TAI #168の固定H2/H3四試行のTask・モデル構成・独立Expectedは変更しない。

<!-- yic-real-capability-baseline-20261115 -->
## 実Capabilityで確かめる追加の最小基線（2026年11月15日）

従来の`semantic-data:sales.order`調査は保持しつつ、**製品mainの実Go回帰にある`semantic-capability:sales.order.submit`**を、もう一つの公開read-only対象にする。[TEI #4853](https://github.com/hat47x/tei-platform/pull/4853)／[#4870](https://github.com/hat47x/tei-platform/pull/4870)では、このSubjectと`semantic/sales/order.tei`の元byte範囲、Inspect/Trace、Source改訂時の失効を確認するコードがmainにある。これは外部AIが読んだことでも、実Provider Entryを実行したことでもない。

**次の実行者が最初に採る証拠**：同一TEI checkout・HEAD・実WorkspaceでCLIが対応するKind/IDを発見できることを先に確認し、既存Go回帰を実行する。参考となるテスト呼出しは次のとおり（ここでは未実行）。

~~~sh
go test ./internal/operations -run '^TestInspectCapabilitySourceEvidenceFromWorkspace$' -count=1
go test ./internal/operations -run '^TestCapabilitySourceOnlyEditInvalidatesPinnedRevision$' -count=1
~~~

現在mainのSource静的照合では、`reference/tei-studio-workbench/source-locations.ts`はS-LOC-0のread-only投影、PinのHost `authorityLimits` FixtureはTEI #4869で修正済み。一方、参照HTMLのボタンIDと現Handlerは未整合で[#4876](https://github.com/hat47x/tei-platform/pull/4876)が**未マージ**、配布`cmd/tei-studio/assets/workbench/index.html`にはPin UIが無い。よって**Nodeの参照テスト成功＝Windows配布画面の成功**とは扱わず、[#4879](https://github.com/hat47x/tei-platform/pull/4879)のSource→Pin→正式Bundle/Embed→実Windowsの独立検収へ引き渡す。

内蔵`tei.rule-authoring/v0`は現行製品Readerへ接続済みだが、外部Language Pluginや任意`*.tei.md`の完成とみなさない。SUI Sourceの現在Grant/Raw再読も別ProductのOwnerに残す。外部Harnessへの実配送はTAI #168の実OS隔離・現在Disclosure・完全Reply検収が成立した**後続Trial**だけで行い、元Subjectへの候補返却と独立Consumer確認を別々に記録する。各段階の現状と停止線は[横断計画§54](harness-cross-ui-session-probe-2026-11-14.md)に集約する。

<!-- yic-rule-markdown-a0-product-read-20261115 -->
## 内蔵Rule Markdownの実製品読取を、追加のA0基線にする

実Capabilityの読取と並行して、**正式に選択されたRule Markdownを製品の同一Loadから読む**試験を独立に実行する。[TEI #4890](https://github.com/hat47x/tei-platform/pull/4890)／[#4891](https://github.com/hat47x/tei-platform/pull/4891)のGo回帰はmain統合済み。次の三つのテスト関数は現行mainのSourceで存在を確認した。**この実行票では未実行**であり、過去HEADのCache成功／別Workflow失敗を合格扱いしない。

~~~sh
go test ./internal/workspace -run '^TestBuiltinRuleMarkdownProductAdmissionAndSourceIndex$' -count=1
go test ./internal/workspace -run '^TestBuiltinRuleMarkdownProductAdmissionRejectsUnselectedOrUnknownLanguage$' -count=1
go test ./internal/operations -run '^TestInspectSelectedRuleMarkdownFromSameLoad$' -count=1
~~~

**固定対象**：`internal/workspace/testdata/tei-md-rule`のManifest `languages: tei.rule-authoring/v0`、原文 `semantic/sales/order-line-rules.tei.md`。期待するのは二つの`tei`定義領域の二Ruleが`semantic-validation`として型付き取得され、元UTF-8 byte位置・Artifact指紋・Inspector/Traceが同一Loadに一致すること。説明用の`text`領域にだけ現れる`sales.order_line.unit_price_positive`はRuleとして取得されない。

**拒否・失効を同じ試験で扱う**：Language未選択（`TEI_MD_PARSER_UNBOUND`）、未知版（`TEI_LANGUAGE_UNAVAILABLE`）、説明文だけの改訂で旧Source Index失効。試験時には**固定repo HEAD、Go/OS環境、実コマンドと終了コード、失敗時の原因、Fixtureの版、結果の受領先**を既存TEI Ownerの記録へ残す。実Ruleが存在することとRule集合全件性／実Providerの入力集合全件性は別である。

**次に確認できる一段階**：[TEI main #4900](https://github.com/hat47x/tei-platform/pull/4900)で、従来のValidationとMarkdown Ruleの型付き意味同値、および同一Rule IDの二重宣言拒否を検査するコードが追加された。[main #4901](https://github.com/hat47x/tei-platform/pull/4901)では、実Ruleを既存Evaluatorに渡し、合成Sourceで数量・明細番号のRead要求と未取得／空集合／NULLを区別するGo回帰が追加された。次のコマンドは**現行mainでテスト名を照合した実行候補**であり、この文書更新では未実行。

~~~sh
go test ./internal/workspace -run '^TestRuleMarkdown(AndLegacyValidationHaveIdenticalProductMeaning|RejectsLegacyValidationWithSameIdentity)$' -count=1
go test ./internal/operations -run '^TestSelectedMarkdownRulesDriveEvaluatorReadFootprint$' -count=1
~~~

判定時は、同じ型付き意味になったこと、評価器が想定したAttribute/Relationだけを要求したこと、**実Providerから適格な入力集合を取得できたこと**を別欄に記録する。#4901のSourceは合成であり、最後の項目は今回の試験では**未確認**。実DB・外部Harness・実Effectは追加の独立Consumer試験を要する。

**YICへの受渡し**：Product-local A0で確認できたのは型付き意味・元Source・read-only参照であり、公開CLIが同じRuleを外部Harnessへ配送したことではない。既存`tei commands`の実Discoveryと現在のProduct/Host Reader・開示資格を別に確認する。TAI [#662](https://github.com/hat47x/tai-pleroma/pull/662)がmainへ統合したSkill検査器では、実CLI Exit非0またはJSON `ok=false`の応答に正常そうな`result`形状があっても成功扱いしない。Reader結果・Tool実配送・完全Reply・元Subject Consumerは独立して記録する。

このRule Readerを最初のTAI #168固定H2/H3四Slotに追加せず、同一Sourceの正負例を持つ**後続のTool-only／Product Skill比較候補**として保持する。RuleからGo生成→実Provider/通常CLI実行→Owner受理も別の製品実装である。状態：**実行票の追補のみ／新Go・外部Harness E2EはNOT RUN**。

## 6つの操作と実行担当

| 順番 | 現在利用するProduct／Harnessの入口 | 合否と停止線 |
| --- | --- | --- |
| 1. 対象を指定 | TEI CUIの実CatalogでSubject KindとCanonical IDを取得。Studioは#4515の明示Pinを後続利用 | Focusや表示ラベルで代用しない。Workspace/RootとSourceを区別。Studio PinはDraftに実装済みだが実Host未検収。C0の実証はCUI固定入力で独立に続行 |
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
- 要求発行時のPin世代、Workspace epoch、Kind/IDを保持し、遅着時には acceptPinObservation で厳密に照合する。Pin解除／再Pin／Workspace切替／A→B→A／同一レーンの後続要求で旧結果を失効。元Workspaceへ戻っても自動復活はさせず、現在のCatalogで同じSubjectが一意に確認できた場合に限り、利用者が「固定対象を再確認」を押して新世代に再束縛する。Pin状態の変更が、現在のBのEditor・Graph・Focus・Noticeを変更しないことを実DOM/Consumerで確かめる。
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
3. **実DOM/Hostの非干渉**：B表示中にAを固定して裏で再取得し、BのEditor/Graph/選択/Noticeが変化しないことを実WebView/Host Consumerで観測。Unpin、Pin A→B→A、Workspace A→B→Aで明示再確認した後の旧応答拒否、返信の遅着、Catalog/Source改版、Host拒否、同名異Rootを負例として残す。現在のread-only UIでDirty/Undo/IMEの編集安全を実証したとしない。
4. **外部YIC接続**：上記の実Product Pinと現在のHost Disclosureの別審査を経た後、既存の実Tool/Native Sessionが限定Contextを完全受領し、元Task/PinへReplyを返したことをTAI #168/#271・QH §10のI/R/P/T/C/Hで記録する。手元のPin状態やTool一覧、AI説明だけを送信成功にしない。

**Evidenceの状態**：GitHub SourceとUIのID対応を読戻し済み。新HEADのActions合格、生成Asset一致、実DOM/Windows Host、外部Harness受領、Source再読取、Owner意味受理はこの時点で**未確認**。実装が前進しても、TEI #4583の非Plugin Stage1→Stage2 DesktopとTAI #168の独立H2/H3四Slotを新しい順序制約で妨げない。


<!-- yic-pin-test-evidence-levels-20261115 -->
## PIN-R0検収票の補正：テスト名で実UI成功を先取りしない

[TEI Subject Pin Draft #4597](https://github.com/hat47x/tei-platform/pull/4597)の最新実装に対し、追加Unitテスト「閲覧Bが変わらない」の検査対象が実際のWorkbenchと結線されていない単なる固定値だったため、**Product ReaderのPin対象・版照合**を検証する名称と内容に訂正した（[commit 22d771a6](https://github.com/hat47x/tei-platform/commit/22d771a65249367ae2975e647ad69f231f486f8a)）。閲覧Bの非干渉は既存PIN-LANE-01の局所非同期レーン試験と、今回追加した**Workbench Source配線回帰**で補助的に確認する。

[pin-wiring.contract.test.mjs](https://github.com/hat47x/tei-platform/blob/feat/studio-pin-intent-state-20261113/reference/tei-studio-workbench/pin-wiring.contract.test.mjs)（[commit 5b4eeae0](https://github.com/hat47x/tei-platform/commit/5b4eeae0668d99e7f32a8e2bfd35b95b3edff664)）を通常のnpm testに登録（[commit aa3557d8](https://github.com/hat47x/tei-platform/commit/aa3557d8fba2e99c42e1ac7f6c5111c5802f2cee)）。内容は、実main.tsの独立 pinned-inspection／既存Host InspectSubject／readInspection経路、選択表示・Editor/Graph/Noticeを**直接**変更しないこと、6つのUI IDと3操作の結線を静的に監視する。背景読取から呼ぶ renderPin() の間接的な表示変更も回帰検査の対象とした（[追加修正 d3abbf57](https://github.com/hat47x/tei-platform/commit/d3abbf572e3672dfa2158f4508ecc5f75a1297d8)）。GitHub上の現Sourceに対し、直接・間接経路の静的15項目を確認（15/15）。**この静的合格はNode24/npmテスト合格、間接副作用なし、実DOM/Windows WebView2、最新Source/Grantの実再確認を証明しない**。

<!-- pin-product-reader-unit-test-20261115 -->
**PinのHost読取を実装から直接テスト可能にした。** TEIの[Pin PR #4597](https://github.com/hat47x/tei-platform/pull/4597)で、Workbenchの背景読取処理から、既存Host InspectSubject／Catalog一意性確認／readInspectionによるSubject・World・Source Index照合を独立した小さな `readPinnedSubject` 関数へ抽出（[commit 00467778](https://github.com/hat47x/tei-platform/commit/00467778f708d90d80d91aea3000f094cb415c22)、[呼出し配線 9d2c2480](https://github.com/hat47x/tei-platform/commit/9d2c2480a2442b9058331cd237b743eab302706e)）。結果は検証した版のみを返し、Canonical全文の外部送信を暗黙に許可しない。[Fake Hostによる5ケースのUnitテスト](https://github.com/hat47x/tei-platform/commit/a85568e02bfddbc616e41305ca65a683081d00ae)を[標準npm testへ登録](https://github.com/hat47x/tei-platform/commit/9a8c0f3ae9e271d715cb79691c565e04cf0394b0)。正常な元Workspace/Kind/IDと版、Catalog曖昧・不在でのHost呼出し0、誤Subject・旧版、Host拒否を対象とする。実Sourceの静的照合は18/18一致。さらに当該GitHub実Sourceの処理本体（Product Reader/Inspect/Eligibility）を抽出し、V8隔離実行で正常なHost引数/最小返却、曖昧・不在によるHost呼出し拒否、誤Subject、旧World・Source Index、Host拒否の**7ケースが7/7一致**した。ただし、この実行はNode24/npm test・TypeScript型検査・実Native Host試験ではなく、それらとRoot/Grant/Disclosure、外部Harness送受信は**未検収**。Pinの意図を保持しても、旧応答から現在性・権限を再付与しない。

検収を四段に固定する。①単体状態/Source配線の回帰、②同一HEAD・ツールチェーンで生成／Desktop埋込みbyte一致、③実Host/DOMでA背景読み込み中もBのEditor/Graph/Focus/Noticeが不変（Unpin・遅延・Root/Source変更の負例）、④許可済みProjectionの外部実送受信・完全Reply・元Task/Pin帰属。①のGitHub Source追補だけから②〜④を合格にしない。

後継UX計画は最新main基点の[TEI Draft #4721](https://github.com/hat47x/tei-platform/pull/4721)、StudioのCLI/AI接続設計は[Draft #4696](https://github.com/hat47x/tei-platform/pull/4696)を参照。旧協業UX Draft #4605は未mergeでclosed。いずれもPin実装の新しい第二正本にはせず、実コードは#4515/#4597の既存Ownerへ集約する。P0はTEI #4583とTAI #168のまま。現HEADの実Node24/生成/Windows/Harness試験・Owner受理は引続き未確認。

<!-- pin-ci-full-test-coverage-20261115 -->
### CIの実行対象を修正した（2026年11月15日）

TEI [Pin Draft #4597](https://github.com/hat47x/tei-platform/pull/4597) の専用Workflowを[commit ca172a1b](https://github.com/hat47x/tei-platform/commit/ca172a1b5ca89b311b1c8460f9ea9cad8f5754ea)で変更。従来のNode24 Jobは、旧Pin状態テスト2ファイルだけを実行しており、追加したProduct Reader（Fake Host 5件）とWorkbenchのUI配線テストが**標準npm testへ登録済みでもCIの対象外**だった。

修正後は既存のWorkflow内で、Node24上のnpm ci→npm test（Product Reader／配線回帰を含む全Workbench標準テスト）→TypeScript typecheck→正規Workbench buildを連続実行する。pull_request/pushの変更対象も、既存の数ファイル列挙から **reference/tei-studio-workbench/** 全体へ拡張した。新Host・新Runner・新テスト格納先は設けない。

この変更は**テストを実際に実行する経路の是正**であり、[commit ca172a1b](https://github.com/hat47x/tei-platform/commit/ca172a1b5ca89b311b1c8460f9ea9cad8f5754ea)に対応するGitHub Actions結果は確認時点で未取得。npm buildは配布先へのコピーやbyte比較を行わないため、既知のDesktop埋込Bundle不一致は、別Workflowと実Hostで引き続き検収する。

<!-- pin-return-to-workspace-20261115 -->
**現在の実装と再確認の条件（2026年11月15日）**：[TEI Pin Draft #4597](https://github.com/hat47x/tei-platform/pull/4597)では、Workspace A→B→AでもPinの意図だけを保持し、旧い観測結果は失効させる。元Workspaceへ戻り、同じSubjectが現在のCatalogで一意かつ**Model Revision・World Fingerprint・Source Index Fingerprintが固定時と一致**する場合に限り、利用者の「固定対象を再確認」から新しい世代で読み取れる（[UI修正](https://github.com/hat47x/tei-platform/commit/12118cb511f59944460285789f137289c7965b96)、[版照合](https://github.com/hat47x/tei-platform/commit/981241493434edb8298d93e50189a619d26a18a5)）。版が変わった場合は、現在のSubjectを新たに固定する。**版が空・空白の場合も一致とは認めず、Pin操作・Host読み取りを拒否**する（[Reader修正](https://github.com/hat47x/tei-platform/commit/0ee142519b829513fa730a681d9ac89db803df8e)、[UI修正](https://github.com/hat47x/tei-platform/commit/bafedd1b532495b4f995bbfb56bda2a92a7000bd)）。

**受入の負例**：別Workspace、対象不在・同ID曖昧、各版の一因子変更・未取得、旧Replyの後着、固定解除、現在表示中Bへの副作用を個別に検査する。実SourceのProduct Reader 7件と画面配線回帰7件は、それぞれ**隔離V8で7/7**期待一致（検査の途中で旧表示文言を参照するテストを修正、[修正コミット](https://github.com/hat47x/tei-platform/commit/41ab2d502cca93c4afa38ca495c3065d04483882)）。実際のNode24/npm・型検査・Bundle正規生成／Desktop埋込byte・Windows Wails/WebView2上のDOM・外部Harnessとの一往復の合格を示すものではない。

**境界**：現行Catalog型は正規のRoot／Source Origin識別を提供しない。Catalog版一致は再確認のための保守的な拒否条件であって、元Rootの同一性、現在の読取・開示権限、Ownerの意味受理を証明しない。新しいResolverやHostを作るのではなく、これらは既存のSource/Host/Disclosure Ownerで個別に検収する。無関係なCatalog改訂でも再Pinを求める場合があることを暫定仕様として明記する。

## 優先順位と停止線

- **独立P0-A**：TEI [#4583](https://github.com/hat47x/tei-platform/issues/4583)の非Plugin Studio Stage1→Stage2実Windows Desktop。#4597のPin純粋testや旧生成WebView CIとは別。
- **独立P0-B**：TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)のG0→G1→G2→物理的に独立したH2/H3四Slot（直近比較適格0/4）。
- **後続接合**：S0→S1とH0→H1の二レーンを独立に進め、S1/H1が各自合格してから同一Subjectの一往復を試す。正式なRelation Pin、Writable Editor、Quick Fix、二Harness比較は別の採用判断。

**完了したこと**：実行票、Pinの実Workbench Source配線、既存Hostの背景読取を分離した関数・Fake Host単体テストの追加、静的Source照合。**未検収**：新HEADのNode24テスト・型検査、生成/埋込JS一致、実DOM/Windows Host、Root/Grant/Disclosure、外部Harnessの完全Replyと元Subject帰着、Owner意味受理。両PRはDraft・未マージで、既存P0を変更しない。
