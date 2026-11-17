# Codex公開Harnessの活用判断とYIC・TEI接続実行票（2026年11月17日）

> **状態：接続方針と後続検証の実行票。Go製C1 Adapterと合成JSONL契約試験はmainへ統合済み。実Codex接続、C2 App Server、Studio連携、OS隔離、二Harness同条件比較、Owner受理は未実施。** 既存の[Harness Adapter](../../integrations/harness-adapter/README.md)、[投資判断](yic-harness-investment-gates-2026-11-17.md)、[Native Session検証票](native-harness-session-capability-pilot-2026-11-17.md)を具体化する補助資料。新しい共通契約・実行Host・Agent Loop・Session DB・権限正本・Build Engineは追加しない。

## 結論：公開ソースは「Harness接続の根拠」として活用する

CodexをYICの唯一の実行基盤にするのではなく、DSH、Claude Code、Step Code、OpenCodeと並ぶ外部Harnessとして接続する。YICはActivity、対象選択と限定Handoff、各Harnessの実効Capabilityを扱い、TEI等の製品は元Source・意味・検証・Effectを正本として保持する。CodexのThread、Turn、Tool ItemをTAIのActivityやTEIのProduct Operationへ直接対応させない。TEI本体は引き続きGo単一バイナリを基本とし、Rust製Codexは**外部プロセス**として扱う。

**接続は二つの用途に分ける。** 既存のGo Harness Adapterで同条件比較を始める場合は、非対話型 `codex exec` のイベントと結果を薄く投影する。Studioの継続対話、進捗、割り込み、承認要求を扱う場合は `codex app-server` のNative Sessionを使う。両者の出力を同じJSON形式と仮定しない。最初の実装単位を「App Serverの全面移植」にしない。

TEI Studioでは既存の型付きApplication APIを入口にし、Wails Bridge専用の業務ロジックや新しいAPI正本を作らない。Codexから製品を呼ぶ方向は、各Harnessの既存MCP clientとTEIの既存read-only MCP／CLIを優先する。別個のMCP clientやTEI専用Hostは作らない。

## 判断の優先順位（2026年11月18日追補）：外部Codexを利用し、必要な機能はYICへ

**CodexはYICの内蔵エンジンにしない。** 開発速度の速いCodexのRustコード、Agent Loop、内部Session Store、実行Policy、承認キュー、Transcript形式、Plugin登録処理をYICへコピー／Fork／静的リンクする方式は採用しない。Codexの存在を前提にTEIのGo単一バイナリやProduct単独動作を変更しない。Codexが将来変わっても、YICと各Productは外部Harnessなしで動作し続ける。

Codexの公開ソースから学ぶのは、**機能そのものの構造と、境界・失敗・操作の振る舞い**である。採用する仕組みはCodex以外のHarnessにも役立つ契約・Product APIとして定義し直す。公開実装を読み、実バイナリを別途固定して確認することと、特定の内部実装へ依存することを区別する。

| Codexから参考にする機能 | YIC側に持ち込む機能・Owner | 実装判断と境界 |
| --- | --- | --- |
| Thread／Turn／Itemと進捗通知 | TAI Activity／Harness AdapterのNative観測、TEI Studioの実行表示 | Product Operationとは別ID。互換イベントは限定投影し、未知通知はUnknown |
| 継続、履歴、Fork、Handoff | TAI #271、Native Session機能票 | 実Sessionの再接続と許可済みActivityの別Session引継ぎは別。共通Transcript DBなし |
| MCP・Tool利用 | 各Productの既存型付きApplication API、Harness AdapterのToolOffer／MCPServerSpec | Codex固有MCP clientをコピーしない。広告、実呼出し、完全Reply、Consumer受領は別確認 |
| Approvalと実行前確認 | Hostの現在Grant・Audience・Disclosure、Product側のAcceptance | Nativeの承認要求UIは補助。モデルやHarnessの許可がHost権限にはならない |
| Sandbox／Network／Process境界 | 実OS隔離、Egress制限、TAI #232／#168 | Codexのread-onlyやcwd宣言だけではRoot外read拒否を保証しない |
| Context管理・Project/Skill | TEI/SUI/SHOの元Sourceから生成した許可済みProjection、YIC既存Skill契約 | 会話履歴から秘密・旧Grantを自動転記しない。配置と実Loadを区別 |
| Worktree／並列開発／差分確認 | TEI #2017のBranch/HEAD/Pathと既存CI、Ownerレビュー | 別Agent Loop・中央Schedulerを設けない。CI成功とProduct意味受理は別 |
| 実行費用・Quota・診断 | TAI #234のHarness/Provider/Model Route別観測 | API・Subscription・Gatewayの利用権を推定しない。無断で別課金先に切り替えない |
| エラー・途中切断・再試行 | EKIのActual Attempt／Effect／Receipt、TAIのUnknown | Native Turn完了、Effect確定、Consumer Readbackを区別。原因不明の副作用を自動再実行しない |

この表は新しい共通正本を作る指示ではなく、既存Ownerが必要な差分を判断するための一覧である。**既存Capability/Tool/Operationで実現できるものは新設せず、初めて検証された不足に限ってAdapterやProductを拡張する。** 最も速い上流追従より、利用者が対象・根拠・安全な実行範囲を保ったまま異なるHarnessを選べることを優先する。

### Codexの更新を受け入れる条件

上流のmain、リリースバイナリ、実行Protocol、モデル提供／課金経路、Sandboxの実効性は**別々の可変要素**である。Codexの新バージョンが公開されただけでは、YICの互換性・開示資格・採用判定を更新しない。

1. **Source調査：** 読み取った上流のexact commit／該当ソース位置／公開仕様・実験的APIの違いを記録する。ソース版が一致しても実バイナリの版・bytes一致を推定しない。
2. **実行物固定：** 実CLI `codex --version`、パス、SHA-256、Host/OS、Provider/Model Route、Profile、設定／Skill／MCP、実際のCode/Schema組合せを資格票に記録する。新しい `-codex-version` は**出力文字列の厳密一致を任意指定するC1のPreflight**であり、Binary SHA・現在権限・OS隔離の代わりではない。未指定ならバージョンは未資格と明示する。
3. **Wire契約の確認：** C1は `thread.started` → `turn.started` → Item → Terminalの合成fixtureを維持する。未知のThread/Turn/Item制御イベント、Terminal後の追加イベント、Result本文欠落・不整合は `RunUnknown` またはparse失敗へ縮退し、成功を推定しない。任意の追加Telemetryは無視せず件数を観測する。
4. **実効Capability再検証：** Codexが提供すると説明する機能、選択版で実際に呼べる操作、Hostが現在許可する範囲、Consumerが実受領した結果を四段に分ける。外部Harnessを切り替えた時もCapabilityとGrantを再確認する。
5. **段階的な反映：** 差分契約試験→実Codexでの明示的なopt-in試験→TEIの公開read-only一往復→独立G0/G1/G2→必要なNative C2操作の順。変更単位ごとに既存Harness非退行を確認し、失敗した版は使わず既存Product-only／他の適格Harnessへ**利用者が明示的に**縮退する。

**Ambientな設定への注意：** `--ephemeral` はSession保存、`--sandbox read-only` はCodex内の実行要求に関わる宣言であり、親環境の設定・Skill/MCP・Credential・送出先の封じ込めを証明しない。新しい版の利用前にCodexの実設定源と送出を確認し、必要ならHost側で別identity／root／networkを強制する。C1単体のGo契約試験を実隔離のPASSに流用しない。

## 1. 観測した上流実装と固定する版

2026-11-17の調査で参照したOpenAI公式リポジトリのmainは **`640b86dc879ceaaa126cdf183b417731e291f476`**。これは**調査用Source pin**であり、実際に配布・起動するCodexバイナリの版・SHAではない。実験時はCLI／App Serverの実バイナリ、設定、Provider、Protocol対応を改めてpinする。

| 出典 | 検討に使う事実 | 注意 |
| --- | --- | --- |
| [Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform) | 単発処理は `codex exec`、製品内の継続対話はApp Server、製品Toolはアプリ所有 | 公式の統合例は製品の業務受理やEffectの保証ではない |
| [Cargo workspace](https://github.com/openai/codex/blob/640b86dc879ceaaa126cdf183b417731e291f476/codex-rs/Cargo.toml) | core、app-server、sandbox、execpolicy等の実装境界を調査できる | Rust内部型をTEIの共通型に移植しない |
| [App Server入口](https://github.com/openai/codex/blob/640b86dc879ceaaa126cdf183b417731e291f476/codex-rs/app-server/src/main.rs) | `--listen stdio://` が既定。Unix socket、WebSocket等の選択肢もある | 初回はローカルstdio、外部HTTP/WS公開なし |
| [App Server処理](https://github.com/openai/codex/blob/640b86dc879ceaaa126cdf183b417731e291f476/codex-rs/app-server/src/lib.rs) | stdioはsingle-clientモードとして処理される | 別UIから同じ生stdioへ直接書き込ませない |
| [App Server README](https://github.com/openai/codex/blob/640b86dc879ceaaa126cdf183b417731e291f476/codex-rs/app-server/README.md) | Thread履歴、experimentalな既読状態、承認要求、ネットワークPolicy、エラー等の版依存仕様がある | experimental機能を必須前提にしない |
| [公式のApp Server操作例](https://developers.openai.com/siwc/token-sharing-open-source/codex-app-server) | `initialize` 成功→`initialized`→`thread/start`→`turn/start`、終了時は `turn.status` を確認 | OAuth例は別途の登録・契約・認可要件がある |
| [ライセンス](https://github.com/openai/codex/blob/640b86dc879ceaaa126cdf183b417731e291f476/LICENSE) | Apache-2.0 | コード再配布・改変時の表示・NOTICE等を別途確認。モデル利用権とは別 |

上流の最新mainに追随すること自体を成果としない。**固定した公開Source、実実行物、使用したWire Protocol、当該時点の機能**を分けて記録する。App Serverの公開項目は追加・実験・変更があるため、未知の通知や旧版の欠損を安易にエラー／成功へ読み替えない。

## 2. YIC・製品・Codexの責務

| 対象 | 所有者 | Codex連携で守る境界 |
| --- | --- | --- |
| Activity・Job意図、限定Handoff | TAI [#271](https://github.com/hat47x/tai-pleroma/issues/271) | Native Thread IDはActivity IDではない。旧Transcript／Grantを無条件に移送しない |
| 外部Harnessの実機能と比較 | TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)／[#234](https://github.com/hat47x/tai-pleroma/issues/234) | Capabilityは宣言と実可用性を分け、切替先の機能・費用・送出先を再確認 |
| 一時Focus・Pin・現Subject | TEI [#4515](https://github.com/hat47x/tei-platform/issues/4515)／[#4503](https://github.com/hat47x/tei-platform/issues/4503) | Focus Bへ移ってもPin Aの応答をBに反映しない。現在Source／Grantは再確認 |
| TEI Application API・業務意味 | TEI [ADR-0048](https://github.com/hat47x/tei-platform/blob/main/plan/adr/0048-shared-application-api-and-transport-adapters.md) | Wails／CLI／MCPから同じProduct操作を使う。Harness内でValidationを再実装しない |
| 実Tool・Native Thread／Turn・承認要求 | 選択したCodex実行物 | 承認UIの表示・Thread終了はHost認可、Product Commit／Receiptとは別 |
| 実作用・結果・Consumer受領 | 各Product／Host／EKI | `turn/completed` やCancel ACKからEffectの成功・失敗・取消しを推定しない |
| Windows Stage1→Stage2セルフビルド | TEI [#4583](https://github.com/hat47x/tei-platform/issues/4583) | Codexは開発支援者。Builder選択・Artifact・実Windows Consumerの証拠を置換しない |

**経路：** TEI Studio／CLI／SHOなどの既存UI → 共有Go Application APIと現在Scopeの確認 → 薄いHarness Adapter → Codex子プロセス。反対向きは、Codex内のMCP Client → 既存製品read-only Tool → 製品側のSource／認可／Response。Studioは結果の候補・進捗・差分を表示し、正本変更は別の製品操作に戻す。

## 3. 二つの接続経路を混同しない

### C1：単発のCodex CLI Adapter（まず既存契約に合わせる）

既存 `integrations/harness-adapter` の `Runner`／`ExecSpec`、`Task`、七つのPin、五水準の成否、`Result.Promoted() == false`、`Registry`を維持する。まず実CLIを調査し、固定した版の `codex exec` の非対話イベント形式と終端を実測する。CLI不在時は `not-run`／`ineligible` にし、代替Harnessへ黙って切り替えない。

- 実行前：Task／cwd／実バイナリSHA／Model Route／設定／MCP server／許可Root／Skill byte／実送信予定を固定する。Token、秘密、未許可Sourceは記録やモデル入力に含めない。
- 実行中：stdin、stdout、stderr、Tool呼出し、terminal statusを個別に観測する。イベント断片・JSON未完成・途中終了は `unknown` とする。
- 実行後：Product CLI直実行とMCP経路の既存7項目を比較し、差分と未測定を残す。CLI自体の成功をProduct意味受理へ昇格しない。

**既存資産の制約：** 現在の `ProcessRunner.Exec` はProcess終了後にstdoutをまとめて返す。これはC1の有界な単発runには利用できるが、C2の承認要求や双方向イベント処理にそのまま転用できない。C1用の解析器をC2のWire Protocol実装だと呼ばない。

### C2：App Server Go接続（Studioに必要な機能だけ）

選択版の `codex app-server --listen stdio://` を、Go側が起動・保持するローカル子プロセスとして扱う。stdioの読取／書込を単一所有者に限定し、request IDとresponse、notification、server-initiated approval requestを区別する。初期化完了、終端Status、Process切断、未完了Tool、承認不在をそれぞれ可視化する。

**最小動作：** initializeとinitialized、thread/start、turn/start、item/agentMessage/delta、turn/completedを固定版で検証する。続いてthread/read・resume、interrupt、承認要求を**別のprobe**で追加。履歴ページング、多Client、fork、experimentalなreadState、Goal、Guardian、daemonは初回のBlocking条件にしない。非対応は `unsupported`、未確認は `unknown`。

**実装箇所：** 既存Adapter packageの近くに小さなGo transport seamとContract Testを置く案。既存 `ExecSpec` に双方向Connectionや多UI Lockを無理に付け足さず、App ServerのProcess／Connectionの寿命を限定して明示する。これはNative APIの接続部であり、新しいAgent Loop、Session永続DB、中央Runnerではない。複数UIでは共有Goサービスを通して**単一操作元＋必要なら閲覧専用**から始め、実多Writer保証を推定しない。Wails ServerのHTTP/WS公開範囲は[TEI #4635](https://github.com/hat47x/tei-platform/issues/4635)などの既存Ownerで別に検証する。

**中断・回復：** `turn/interrupt` 受理や通信切断だけではToolの実作用は不明。別SessionへActivityを限定Handoffする場合も、過去のThreadにある情報を現在のDisclosure／Host Grantとして継承しない。

## 4. 最初の一件のProduct往復

対象は既存公開TEIの `semantic-data:sales.order` とする。Taskは「この設計要素の役割と依存を、実際に読めたSourceの範囲だけで説明する」。新しい業務DSLやサンプルDBを起こさない。

1. **Product単独の基線：** 既存TEI CLIでSubjectと元Sourceを実Read。Workspace、Source revision／実bytes、対象ID、開示可能なProjection、未取得領域を記録する。
2. **Tool-only：** 既存read-only MCP Tool経路からCodexが同じ対象を調査。実Tool Request、完全なReply／stderr、Prompt・Context送出範囲、回答のUnknownを観測する。Product Toolが使えなければshell代替を同等扱いせず別記する。
3. **返答の帰属：** Pin Aの結果をAの候補として受け取り、Focus Bへの誤適用を拒否。Source／Grant／Policyの変化後は再資格化する。
4. **後続のSkill比較：** SkillなしH2とProduct SkillありH3を既存TAI #168／#488の固定Taskと独立Expectedで比較する。Skill配置・広告・実Loadは別。今回はCodex追加のために既存四Slotの採点条件を改変しない。
5. **実際の変更：** 初回はread-onlyで終了。生成差分の採用、コード生成、Git統合、実DB更新は既存[TEI #2017](https://github.com/hat47x/tei-platform/issues/2017)のA0〜A4と各Productの正式Operationへ進める場合だけ扱う。

**現在のEvidenceを混ぜない：** 既存Harness AdapterはDSH／Claude Code／Step Codeの型付きToolや限定的なH2/H3観測を持つ。一方、TAI #168が要求する実OS read-deny → G1送出 → G2完全Reply → 新規独立4 Slotは、旧比較の成果をそのまま採点できず、直近の公式受入は適格0/4。Adapter実装のE1〜E6とTAI #168の適格比較は別の資格とする。

## 5. 独立の負例と停止線（既存Expected Ownerへ配分）

| ID | 反例／故障注入 | 必要な観測と停止条件 | Owner |
| --- | --- | --- | --- |
| CX-01 | Codex未導入／バイナリ版不明／Provider利用権なし | `ineligible` または `unsupported`。他モデルへの自動課金・暗黙切替なし | TAI #168／#234 |
| CX-02 | initialize失敗／未知method／experimental機能不在 | Thread開始済みと偽らない。限定的機能へ縮退 | TAI #234・Native票 |
| CX-03 | JSONLの分割到着／未知notification／応答ID逆転 | request相関と終端を保つ。未知イベントの見落としを成功にしない | Adapter契約 |
| CX-04 | Tool Replyの途中切断・截断、Turnだけcompleted | Product回答の完全性 `unknown`。CLI/MCP一致を偽造しない | TAI #168 |
| CX-05 | 承認要求時にUI不在、別Principal、承認対象差替え | 実行拒否。UIの押下＝Host権限とはみなさない | TAI #232／TEI #2515 |
| CX-06 | Thread resume先のcwd／Provider／版／Historyが異なる | 同一Native Session成功とせず、必要なら限定Activity Handoff | TAI #271 |
| CX-07 | 同Hash別Root、A→B→A、Source／Policy変更 | 現在のSubject／Read／Disclosure資格を再照合。旧資格の自動復帰なし | TEI #4503／#4515 |
| CX-08 | FocusをBへ変更後、Pin Aの遅延Replyが到着 | Bへ自動適用0。元Aの候補に帰属 | TEI #4515 |
| CX-09 | read-only宣言でもRoot外read／ネットワーク送出可能 | 実OS read-deny／Egressを負例で確認できなければ適格0 | TAI #232／TEI #2515 |
| CX-10 | Interrupt ACK後にProduct Effectの帰結が不明 | 自動再試行しない。Receipt／独立Readbackを別取得 | EKI #57／TEI #1174 |
| CX-11 | OAuth／API／Gateway／定額枠を取り違える | Routeと権利・Quotaの実確認。CredentialとRaw Tokenを公開証拠に残さない | TAI #234 |
| CX-12 | 別UIの過去Transcript閲覧、二Writerの同時Turn | 現在のAudience／Disclosure、実Native排他を確認。未成立なら一Writer | TAI #234／TEI #2516 |
| CX-13 | Skillを配置したが未Load、Tool schemaを入替 | `not-loaded`／不適格を保持。既存比較票に記録 | TAI #168／#488 |
| CX-14 | Codexが別Worktree・他Lane・秘密ファイルを読取 | 許可path／OS隔離／実Source pinを照合し、A2自動統合禁止 | TEI #2017／TAI #232 |

負例はこの文書を第二Expected正本にせず、既存Ownerの実行票へ追加するための**差分候補**とする。開始前に元Expected・固定Task・独立採点者を指定し、失敗例の条件を試行後に変更しない。

## 6. 開発順序とマージの単位

| 順 | 最小成果物 | 実装・受入の出口 | 性質 |
| --- | --- | --- | --- |
| C0 | Codex固定版の機能表、実Binary／Protocol／契約経路pin | Sourceと実実行物を分離。OS／認証／Model Routeを確認 | 調査／read-only |
| C1 | 既存Go Harness Adapter用 `codex exec` 腕 | 合成契約試験＋実CLIでTask・Tool・出力とunknownを観測 | 小PR、他Adapter非退行 |
| C2 | App Serverのstdio ConnectorとFake Server試験 | initialize→Turn→終端、承認拒否、切断・再開、未知通知の正負 | 別PR、外部実行はopt-in |
| C3 | TEI StudioのPinned Subject／Native Session表示 | Focus≠Pin、Progressと承認、Candidateの元対象帰属を確認 | TEI側の既存UIを拡張 |
| C4 | Codex／既存Harnessの条件付き比較 | TAI #168のG0/G1/G2およびH2/H3独立資格の範囲でのみ採点 | 認可／Evidenceは別 |
| C5 | 実Git Worktree・PR・統合の追跡 | A2→レビュー→既存CI→A3限定Merge。A4は人判断 | TEI #2017で評価 |

**既存P0は不変：** TEI #4583のWindows Stage1→Stage2実セルフビルドと、TAI #168の外部Harness適格4 Slotは独立進行。C1/C2の検証をP0-AやP0-Bの新しいBlocking条件にしない。C2はC1の完了を技術的な必須条件としないが、比較可能な観測列は共有する。

**レビュー・統合：** 各PRは変更path、base／exact HEAD、実行環境、重点試験、既存試験の非退行、未実行、Source版、独立レビュー、マージ後のmain再確認を記録する。Docs-onlyの合格は実Codex接続成功の根拠ではない。

### C1の実装差分（2026年11月17日）

`integrations/harness-adapter/codex_exec.go` と契約試験、CLI登録を追加した。既存契約を変更せず、`codex exec` のJSONLからThread／Turnの終端、MCP・Commandの完了Itemを読み取る。全ToolOffer・Skill・ContextRefは未対応として事前拒否し、`codex --version` による実行物の到達と、認証済み／Tool利用可能／OS隔離成立を混同しない。プロセスはstdinへTaskを渡し、危険なsandbox bypassや自動Git境界無視を指定しない。

**成立範囲は契約試験による合成JSONLの解釈まで。** 実Codexバイナリ、正規モデルRoute、TEIの型付きMCP実Tool、完全Reply、Root外Read-deny、実Egress、Studio、App Server接続はNOT RUN。C1の実装でC0の実実行物固定、TAI #168の適格Slot、C2〜C5を自動的に完了扱いしない。次の実装出口は、C0の実Binary pinと、Taskに必要なTool/Skillを改変しない**明示的なCodex MCP設定方式**の検証である。

## 7. 採用・保留

- **採用する設計：** 外部プロセス接続、Codexの二種類の実行面、既存Go Harness Adapterと型付き製品API、Studioに返す限定候補、実権限／Effect／Evidenceの分離。
- **実験で判断する：** App Serverの版依存API、Session resume／履歴の完全性、承認強制、ネットワーク・OS隔離、CodexにおけるSkills／MCP、費用、複数UI、低価格モデルのResponses互換。
- **当面採用しない：** Rust Core全面Fork、TEIへのRust埋込み、共通Transcript DB、独自Agent Loop、新しい中央Auth／Runner／Registry、Wails ServerをCodex専用Hostにする案、CLIとApp Serverの強引なABI統一。

コードの複製・配布が必要になった場合はApache-2.0の許諾・表示条件と依存ライセンスを別途精査する。**公開コードを利用できることは、OpenAIのモデル、アカウント、定額枠を転用できることではない。**

**未確認のまま残す事項：** Codex実Binaryの導入／version／SHA、実MCP・Product Consumer、Host／OS／通信の負例、実Capability／モデル利用権、実Codex接続・外部E2E試験、Owner受理。GoのC1実装と合成試験はmainへ統合済み。これらを「設計の採用」から実行済みへ昇格させない。
