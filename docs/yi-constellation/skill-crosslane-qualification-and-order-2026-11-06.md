# YIC Skill横断適合・実行順序への統合追補（2026-11-06）

> 状態：計画追補・Owner未受理。新しい実AI Harness試行／実Skill Load／製品間E2E／本番Authority／シリーズReleaseは本追補ではNOT RUN。既存の各Product契約、TAI #168、#271、#74、#232、Draft PR #270、SK-01/SK-02/SK-03を正本として尊重する。新Host・中央Registry・共通Evidence Engineは設けない。

## 1. 背景と差分

- [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) の2026-11-06更新では、固定したTEI実Go Binary/公開Source（TEI pin `50ebf8014340fd1906f6b35cfa30173e0ee2fc6c`、`reference/workspace`、`semantic-data:sales.order`）に対するTAI→TEI W0/S1読取りが限定達成。これはAI HarnessがToolを呼んだ証拠でもSkillを実Loadした証拠でもない。
- [TAI Draft #270](https://github.com/hat47x/tai-pleroma/pull/270) の計画§39〜41・[実験Runbook §21〜22](https://github.com/hat47x/tai-pleroma/blob/docs/yi-harness-skills-20261102/docs/yi-constellation/first-real-skill-qualification-runbook-2026-11-02.md)には、固定Participant Taskのraw digest照合、R（割付）とD（実提供）、ITT/PP、H2 Skill非露出、H3 root/reference pin、一時ファイルビューが既に定義されている。新しいRunner/Checker/Skill Formatを作らず**そこを使用する**。
- [CI #42112462908](https://github.com/hat47x/tai-pleroma/actions/runs/42112462908) は固定Skill候補のbyte照合、H2/H3各ファイルビューに対する同一実CLIのread-only実行について成功。ただし実HarnessのTool実呼出し、Loader read、公開経路の物理隔離はNOT RUN。
- [TEI #2605](https://github.com/hat47x/tei-platform/issues/2605)の固定Product SkillにはCLI応答の `entries` と `result.entries` の取り違え、および実比較Tool Profileとは異なる `go run` 記述が残る。初回H3の治験条件を変えず、実行上の影響を記録する。修正版は別Trial Groupとし、元のPackageを黙って差し替えない。
- 前回の[TAI #488](https://github.com/hat47x/tai-pleroma/issues/488)は、既存SK-01/SK-02/Runbookの試験本体を二重管理するのではなく、各ProductのOwner・横断ゲート・Evidence資格を結びつける**照合票**として用いる。

## 2. 所有境界（構成は任意の組合せ）

| 境界 | 担当 | 誤って昇格させないもの |
| --- | --- | --- |
| Product Skill | TEI/SEI/SUI/SHO/EKIなど各Product | Skill説明→意味受理、Tool存在、Provider実行 |
| TAI横断Skill | 目的別Product選択、共同Claimの保留、Activity/Handoff・再資格化 | 任意のTAI経由→全Product必須、中央意味正本 |
| 外部Harness | モデル推論、実Loader、Tool呼出し、セッション記録 | モデルの自己申告→実Tool実行/秘密保護 |
| Product CLI/API/MCP | 実コマンド/Schema、現在のSource解釈と結果 | コマンド成功→Ownerの意味受理・Effect成功 |
| 実OS/Host/Provider | 開示可能範囲、Host Grant、実行作用、独立結果 | read-only説明→物理権限・無送出保証 |
| TAI #74 配布 | 個別Product pinを束ねたシリーズ検査/ガイド候補 | Bundle PASS→各Product Release/受理 |

すべてのSkillを常時読込むのではなく、Taskに必要なSkillのname/descriptionから候補を得て、許される情報範囲だけで実Tool/Sourceの存在を確認し、必要になったreferencesのみロードする。存在しない機能・Toolは補完せず、Unavailable/Unsupported/Unknownで止める。Discovery結果やError自体が機密なら開示前にProduct/OS/Host境界で制限する。

## 3. 選択適合を左右する四つの独立条件

1. **Required**：Taskの目的、必要なOperation、意味粒度（Grain/Bag/Null/Missing）、許されるConsumer/Disclosure、受理主体。
2. **Supplied**：特定版のProduct Skill root＋参照ファイル閉包、Product CLI/MCP/API・Schema、Role/Operator/Source pin、Tool/OS/Host profile。
3. **Observed**：Harnessでの実際のSkill read、Tool request/argv/cwd/exit/stdout、Source span/fingerprint、Warning、Evidence/Effect/Consumerを個別に観測した範囲。
4. **Undischarged / Claim ceiling**：欠落・矛盾・不可視・未実行の根拠と、それにより主張できない上限。未観測をfalseへ変換しない。

適用可能性は「RequiredがSuppliedで満たされ、実効開示が許され、現在の依存と版が確認できる範囲」でのみ成立。候補の発見、インストール、実ロード、Tool利用、Source/意味受理、Host権限、Result/効果、現在資格は独立状態とする。**Skillの読み込みを実証しても、その手順に従ったことや回答の正しさまでは自動的に証明しない。**

空結果は、完全に列挙した集合の空・読取不能・部分取得・権限により不可視・未実行のどれかを区別する。完全空や不存在からの推論は、列挙範囲と時点の**否定依存（negative dependency）**を保持する。Source A→B→A、Dependency追加/削除、Owner受理撤回、Operator/Host/Disclosure改版では、過去のDigest一致だけで現在資格を復活させない。歴史的再現可能性と現行用途の利用資格を分け、既存[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)へ委譲する。

## 4. 実行順序と停止条件（既存Runbook優先）

| 順 | Gate | 必須の一次証拠 | 不足時の状態 |
| --- | --- | --- | --- |
| P0 | 固定TEI Binary/Source/Subject・Task byte・Tool/Disclosure/Model pin | TAI W0/S1の実CLI/Source/argv/Source IndexとSkill root/reference pin。H2 Skill非露出の実Tool File View | 不一致=ineligible、直接観測不足=insufficient-evidence |
| P1 | **H2-01：外部HarnessのSkillなしTool-only一実セッション** | 実Harness Session ID、実Tool request/response、argv/cwd/exit/stdout、Sourceと回答。Skillや採点票への迂回到達も検査 | 実Tool呼出し不明=NOT RUN/INELIGIBLE |
| P2 | **H3：同HarnessでProduct Skillあり** | 同一Task/Source/Tool/モデル/Grant。root/referenceの実Loader Read。固定候補の実手順エラーも保持 | 配置のみ=Available、実Load不明=Unknown |
| P3 | H2→H3→H3→H2の4独立Session | 割付R、実提供D、ITT全数、条件を満たしたPP、独立Expected、品質・誤操作・費用・経過時間・人手 | 対照不成立=比較不可。4件だけで一般的改善率を主張しない |
| P4 | 必要になった場合だけ追加Product/TAI横断Skill・別Harness | 既存SK-01/SK-03と #271 によるTask別Handoff・Consumer/Host再資格化 | 単独Skillで十分ならTAI介在を省く |
| P5 | 実配布・権限・外部作用 | #74・#232と各Product Ownerの現行Grant、実Outcome、独立Consumer読取、Release条件 | 参照CI/合成PASSの横流し禁止 |

この順序はAI並行開発の探索件数を制約しない。最初の反証単位を限定するのは結果の帰属を確かめるためであり、YIC全体の製品Scopeを狭めるものではない。

## 5. #488照合票の既存試験への対応

| #488 | 必ず再利用する既存評価/Owner | 追加で確認する欠落 |
| --- | --- | --- |
| X01（CLI/H2/H3/TAI選択） | SK-01 H0〜H7、SK-02のH2/H3、TEI #2018 | H3のPackage treatment、R/D・ITT/PPと対照の汚染有無 |
| X02（空Workspace誤陽性） | TEI #2822/#2605、SK-01 E06 | `validate ok`≠ユーザー宣言存在。`std` entriesと`not-indexed`を識別 |
| X03（Tool/環境失敗） | TEI #2953/#2605、SK-01 E03/R03 | Go版不整合とSkill/CLI/Tool不可用を意味失敗へ混入しない |
| X04（失効・否定依存） | TAI #271、SK-01 RQ群 | Source ABA、依存増減、partial/empty、Old Grantの再利用可否 |
| X05（秘密・部分作用） | TAI #232、TEI #2515、EKI既存Result/Trust Owner | Tool/Skill表示とOS実拒否、応答喪失と同Attempt Bodyの受領を分離 |
| X06（Product間引渡し） | SK-03、TAI #271、TEI #2516、SHO #10、SEI #769 | 履歴資格と現在資格、共同Claim、実Consumer読取を別々に記録 |

SK-01/SK-02のFixture・Expected・実験票を複製しない。#488は「未充足のどれが誰のIssueにあるか」とExit判断を保持する。試験の結果を新しい中心資格エンジンへ移さない。

## 6. 最新のProduct別状況を反映する

- **TEI**：実S1は固定公開Source読取りの限定PASS。Product Skillの固定版にCLI応答Pathの実不一致があるため、最初のH3で観測し、修正後のSkill治験と混合しない（#2605、Draft #2863）。
- **SHO**：[Draft #17](https://github.com/hat47x/sho-composer/pull/17)の限定Markdown ReaderにはNode/両OS実CIの局所証拠がある。リンク列挙は全参照/意味/保存/納品の資格ではない。SHO Product SkillとTEI→SHO Handoffは初期H2/H3の必須依存にしない。
- **SEI/SUI/EKI**：各Product Skill候補のOwner（SEI #769、SUI #3368、EKI #468）と実能力/Tool/開示面を照合。既存Skill・Product CLI・実Authorityを混同しない。必要な複数Product TaskができるまでTAIの新しい統合実装を先取りしない。
- **TEI Everything is Data**：#2619〜#2622のAuthoring Source／意味Role／明示Data Context／Provider作用を別段階として扱う。Markdown表や期待値があることを実Test/実Source取得/Owner受理と判定しない。

## 7. 並行開発・レビューへの落とし込み

- **実験実施レーン**：TAI #168 / SK-02 Ownerは最初のH2 Sessionと4 Sessionの一次ログ・独立Oracleを保管。Harnessが使えない場合はNOT RUNを維持。
- **Product修正レーン**：TEI #2605はSkill/CLI応答Path、#2822は空Workspace、#2953は前提Go版。修正は別PR/別Trial GroupのPinにする。SHOなど他製品は各Repo Ownerで独立進行。
- **横断照合レーン**：TAI #488は既存SK-01/SK-02とProduct Issueの不足・整合だけを追跡。TAI #422/#424の独立レビュー規則を適用し、他レーンのファイル・試験結果・受理状態を上書きしない。
- **安全/配布レーン**：#232は実OS/Host/Disclosure、#271は現在資格、#74はシリーズ束ね。Taskに不要な本番書込み・PG/Provider/別HarnessをH2の前提に追加しない。

全レーンが各自の改訂・Input pin・Expected/Observed/Unknownを明示し、独立Reviewerが一次証拠とClaim ceilingを照合する。Source-static設計、合成Checker、実Product CLI、実Harness Tool、Owner受理、公開Releaseを一つのPASSへ合算しない。

## 8. 次に満たす具体的Exit

1. 固定Participant Taskと実Binary/Source/Tool条件のH2-01実Harnessログを1件確保し、Skill非露出・argv/Source/回答の一次観測を成立させる。
2. 同HarnessのH3で固定Product Skill root/referenceの実Loader Readを確認し、既知のCLI応答Path不一致を含めて観測する。
3. H2→H3→H3→H2の全4セッションを独立Expectedと実費用・失敗分類で採点。追加Skillの有益性が観測できなければTool-onlyを維持。
4. 初回比較の後にのみ、Taskの要求によって第二Harness、TAI横断Skill、TEI→SHO/SEI/EKI引渡し、再資格化を進める。

**今回の追加は計画・照合表のみであり、Skill・Host・Provider・実Harnessの新規実装、実試験の実行、正式採用・main統合を表さない。**
