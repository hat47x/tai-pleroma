# YIC：並行AI開発から安全な統合へ――最初の実行票

**状態：実行計画／新しい試行はNOT RUN（2026年11月15日）。** [YIC横断計画§52–53](harness-cross-ui-session-probe-2026-11-14.md)、[TAI #233](https://github.com/hat47x/tai-pleroma/issues/233) の並列開発比較、[TAI #422](https://github.com/hat47x/tai-pleroma/issues/422) の独立レビュー、[TEI #2017](https://github.com/hat47x/tei-platform/issues/2017) のA0〜A4作業票を既存正本として利用する。この実行票は並行作業用の**運用手順と結果欄**であり、新しいTask Schema、Runner、Merge Bot、Verifier、Authorityを作らない。

## まず何を確かめるか

一人のAIが三つの仕事を順番に進める場合と、独立した作業者がそれぞれのbranch/contextで進める場合を、**同じ公開入力・同じ成果条件・同じ独立Expected・同じ検証環境**で比べる。並列化の成果は「提案が増えた」だけでなく、統合できた成果、競合、修正費用、見逃した負例、利用者の確認工数で評価する。

最初の測定対象は、実製品の意味や権限を変えない公開read-only調査と、合成fixtureに対する隔離branchの小規模改修に限定する。**TEI非Plugin Stage1→Stage2実Windowsセルフビルド／TAI実OS隔離・H2/H3四Slotを、この試験の依存Gateにしない**。逆に、本試験の成功を両P0の合格へ転用しない。

## 実際に起きた三つの失敗を、独立反例として使う

| 現行GitHubで確認した歴史的な失敗 | この試験で判別すること | 正しく止まれる条件 |
| --- | --- | --- |
| [TEI main #4844](https://github.com/hat47x/tei-platform/pull/4844)：`internal/jsonl`で`ReadBytes`が二重定義され、全体Goビルド不能。修復PRはmain統合済み | 別branchで同等機能を重複実装したとき、merge先の**実Source closure**に同名宣言が残らないか | 同じ名前の関数を複数ファイルで定義した合成負例を全体Compileで検出。現在mainが再び故障していると主張しない |
| [TEI main #4831](https://github.com/hat47x/tei-platform/pull/4831)：並行統合後にREA比較Statusの重複宣言とNoteの二重追加が残存。後続修復はmain統合済み | コンパイル可否だけでなく、**同じ意味の診断・注記が一度だけ生成されるか** | 同一Source・AttemptでNote二重追加を独立Expectedで拒否。文言差や件数の多さを成功とみなさない |
| [TAI main #658](https://github.com/hat47x/tai-pleroma/pull/658)：限定read-only `commands`にないCLIを「製品に存在しない」と断定した誤りを既存検査器で修正 | Agentが異なる発見範囲（`usage`／`commands`／Plugin説明）を突合したとき、absenceとunsupported/unknownを混同しないか | 見つからない理由・Discoveryの範囲を保持。別の機能や権限を勝手に補完しない |

これらのPRは**修復の実例**であり、ここで新しい並行AI試行を実行した証拠ではない。新試行の独立Expectedは既存Tool/CI結果やAgentの最終回答から生成せず、試行前に評価者が固定する。

## 実行の前に固定するもの

| 項目 | どこへ記録するか／再確認すること |
| --- | --- |
| 仕事の目的・依頼Issue・比較Arm | [TAI #233](https://github.com/hat47x/tai-pleroma/issues/233) のP-A逐次／P-B並行／P-C競合と、この**小さな事前パイロット**の区別。P-B本試験の四件を勝手に三件へ変更しない |
| Source・baseと更新方針 | 事前に固定した公開fixture、repo/base SHA、全Source Closure、許可path/禁止path。作業中のmain改訂と別Sourceの受入を区別 |
| 作業権限と隔離 | A0＝読み取り、A1＝決定的派生、A2＝隔離branch変更。A3統合は対象Ownerの既存条件のみ、A4意味・権限・配布は人に戻す。Prompt/branch名だけでOS隔離としない |
| Harness/Modelの実経路 | 実Session ID、Provider/Model/Tool版、Skillの実Load、既存HostのOS/Network制限、契約・利用枠と観測できた費用。未確認はunknown |
| 独立Expected | 作業者の出力とは別に保管し、Reviewer用情報を実行Workerへ見せない。ExpectedのSource/Revisionと開示境界は評価者が保持 |
| 試験・結果の帰属 | branch HEAD、実行コマンド・終了コード、CI Run ID、取得SourceとCoverage、実Consumer、未実施欄。元HEADのPASSは新HEADのPASSでない |

**秘密の扱い**：公開合成fixtureと許可された文書で始める。Raw、Reviewer-only Expected、非公開Path/件数/Digest、Credentialや別Laneの成果を、Prompt・Agent log・Session log・Tool/Provider送信へ無条件に含めない。TAI #232とTEI #2515の実OS/Network制限が確認できない場合、別Lane間の機密隔離を成立済みと呼ばない。

## 第1巡：三つの独立作業を先に通す

最初は**A0の三作業**を同じ公開Snapshotから開始する。①現行TEIのCLI/Plugin発見範囲の確認、②現行TEIの一Subject/Sourceの確認、③YIC/TEIの公開Manualの適用範囲と未実装機能の照合。それぞれ実Toolからの取得範囲・unknown・未解決事項を独立して残す。並行ArmではWorkstreamごとに別Session/Context/出力先を用い、初回から共有編集ファイルやWriterを与えない。

逐次Armでも同じ三つを同一基準入力で処理する。順番や追加の情報取得で公平性が崩れた場合は、その試行をそのまま観測しつつ比較資格を分ける。**作業者の数が三つあることと、独立な証拠が三件あることは同じではない**。

## 第2巡：小さなA2変更をbranchごとに隔離する

A0の成果だけで並行開発の成功とはしない。続く別Trialでは公開合成fixtureの複製を使い、二つのA2 Workerが別branchで、次を**意図的に**扱う。

- **非競合の対照**：異なるファイルに互いに独立した検査を追加。共通契約・依存変更が無いことをOwner側で確認し、両方を統合した結果を新HEADで再検査する。
- **同名宣言の競合**：同じ公開関数相当を別ファイルから二度追加。各branch単独ではPASSし得ても、統合後の全体Compileでは失敗するExpectedを固定。重複を放置したまま統合不可。
- **意味上の重複**：実装名が異なっても、同じ診断やイベントが二重に出力される変更を競合させる。構文Conflictなしのmerge成功やCompile PASSだけで採用不可。
- **発見範囲の食い違い**：片方が限定CLI一覧、他方が別のDiscoveryを観測した例を作り、未検出を「機能の不存在」と決めつけた結論を不採用にする。

この段階では**合成fixture以外の本番Sourceへ衝突を注入しない**。Gitのbranch・PR・CIは既存機能を使用し、中央のAgent Lock Server／新Merge Engineは作らない。

## 統合の手順：提出・検証・受理を分ける

1. **提出**：各Workerは元Issue、base、HEAD、変更path、diff、実テスト／未テスト、失敗・未知を残す。提出PRやAgentの完了報告は、採用結果ではない。
2. **重なりの発見**：Gitのmerge conflictだけでなく、宣言の重複、同じ診断の二重生成、共通API・Source/Contract改訂、参照資料の版差を確認する。別ファイルでも同じ意味を変更していれば競合として扱う。
3. **独立Challenger**：作成者と異なるContext/Reviewerが、事前に隔離したExpected・反例と現在のSourceを確認する。反例を作業者の回答から逆算しない。別モデルを使っても実Sourceが共通ならEvidence独立性は別判定。
4. **統合候補の作成**：Ownerが現在mainを確認し、別baseの作業は必要な範囲だけ再適用する。衝突した設計の一方を都合よく黙殺せず、差・理由・未受理をIssueへ戻す。各ブランチのGreenを合算しない。
5. **統合候補の再検証**：**統合した候補のexact HEAD**で必要なCompile/Unit/Contract/Consumer/配布資産を実行する。元PRの成功は履歴参照であり、失敗したWorkflowは失敗のまま残す。
6. **採否とmainへの反映**：A3で機械統合できる条件を満たすか元Product Ownerが判断し、A4に触れたら人へ戻す。merge完了後も新main SHAで確認すべき回帰・配布・Consumerの範囲を明示し、PR mergedだけで正式製品完了としない。

## 結果の記録欄（実行したときに既存Issue/PRへ記入）

| 比較項目 | 逐次Arm | 並行Arm | 判別条件 |
| --- | --- | --- | --- |
| 開始時のSource/base/Expectedと実Tool到達 | NOT RUN | NOT RUN | 同条件を満たすか。違えば比較不適格の理由 |
| 独立した候補・独立の反証 | NOT RUN | NOT RUN | 重複候補を独立価値と数えない |
| 許可path外変更／秘密流出／未知結果の誤成功 | NOT RUN | NOT RUN | 発生条件と実Host観測。未観測はゼロ件にしない |
| 単独branchの検査と統合HEADの検査 | NOT RUN | NOT RUN | Compile／意味重複／Source Closureの別判定 |
| 完成・Owner受理・main反映済み成果 | NOT RUN | NOT RUN | PR作成数と区別し、Product Meaning/Effectは別 |
| 所要時間・Token/実料金・CI・Reviewer修復負担 | NOT RUN | NOT RUN | 実測が取れない項目はunknown。単一総合スコアにしない |

未実行・環境不足・Source不一致・一部Tool切断を後から成功Armだけ除外しない。ITT（割付済み全試行）とPP（事前に決めた比較適格試行）は別に示す。並列の速さでレビュー・競合処理が増えるなら、その負担も結果に含める。

## Ownerへ返す結果と、今は採用しない仕組み

- **TAI #233**：逐次対並行、P-C競合、探索の幅と統合に残った成果。三作業の初回パイロットを既存のP-B正式四件の完了とは扱わない。
- **TAI #422**：VA-X反証とVA-EのSource/証拠監査。モデル多数決では採否を決めない。
- **TEI #2017／#1189**：A0〜A4、変更path、同一HEADのCIとmerge前検証。IssueがClosedであっても新Trialの実合格ではない。
- **TAI #168／#232／#271**：Harness実隔離、開示、Activity引継ぎを対象ごとに確認。最初のH2/H3四Slotの資格・分母へ本試行を合算しない。

**本実行票の完了**は、Owner/Expectedへの参照、比較する二Armと競合負例、必要なSource/HEAD/CI/Consumer欄、停止線を定め、実装担当がそのまま試行を開始できる状態まで。**実試行の完了**は、上記の実証欄に実測と独立評価が付いてから別途判断する。現時点では前者のみを設計し、新Agent Session、合成fixture実行、main統合検証の新試行、正式Owner受理は**NOT RUN**。

<!-- yic-frontend-ship-closure-20261115 -->
## 後続対照：参照画面だけ新しく、配布画面は古い場合

並行開発の競合は、同じGo関数を二度定義する場合だけではない。[TEI main #4879](https://github.com/hat47x/tei-platform/pull/4879)の時点では、参照側`reference/tei-studio-workbench/index.html`のPin操作が、実配布`cmd/tei-studio/assets/workbench/index.html`へ入っていない。この二つのSourceを現行mainから直接読んだところ、参照HTMLには`pin-current`／`pin-check`／`pin-release`があり、配布HTMLにはPinパネルがない。さらに参照TS HandlerのボタンID不一致を直す[#4876](https://github.com/hat47x/tei-platform/pull/4876)は未マージである。

この**別の後続Trial（未実行）**では、二Workerが参照TS/HTMLと生成・埋込資産を別々に変更したケースを扱い、次の四点を分けて判定する。

1. 各変更の元Source/HEAD、依存関係・生成手順・Toolchain/Lockを確認する。両Workerが単独で成功しても、統合前の正しさに留まる。
2. 統合候補の同一HEADでPin HandlerのID／実DOMのID、Node24テスト・型チェック・正規Buildを再確認する。
3. 正規生成した`dist`とWails側の埋込JS/HTML/CSS等をbyteで照合し、**実Windows WebView2が同じ成果物を読んだこと**を別の実Consumerとして確かめる。成功側の古いJS/HTMLを手コピーして合格を演出しない。
4. Sourceも配布も一致して初めてUI Consumerの一段階を検収する。Pin Aの背景確認がFocus Bに影響しないこと、Source/Grantの再確認、外部Harnessへの送信資格、Stage1→Stage2はさらに別の受入とする。

これは[TEI #4879](https://github.com/hat47x/tei-platform/pull/4879)のOwner検収を参照する**並行統合の反例**であり、新しいYIC配布BuilderやFrontend Checkerの採用ではない。**当時**は参照HTMLと配布HTMLでPin要素の有無が異なったが、その後[TEI main #4920](https://github.com/hat47x/tei-platform/pull/4920)でPin配線が修正され、[main #4945](https://github.com/hat47x/tei-platform/pull/4945)で正規Bundleが埋込Assetへ同期された。現mainの両HTML／両CSSはそれぞれ同一Git Blobで、該当HEADのEmbedded CIも成功した。一方、Windows WebView2 Smokeには失敗があり（修復候補[#4955](https://github.com/hat47x/tei-platform/pull/4955)は未マージ）、**配布byteの一致と実Consumerの成功は別**。二Worker並行作業と新YIC Trial、Windows/Owner受理は今回**NOT RUN**。

<!-- yic-overlapping-rule-tests-20261115 -->
## 現行の重複提案を使った比較：既にmainにある回帰と、新しいDraft

[TEI main #4890](https://github.com/hat47x/tei-platform/pull/4890)の`tei_md_rule_product_read_test.go`は、内蔵Rule Markdownの製品`Workspace.Load`、二Ruleの型付き意味、同一Load原byteのSource Index、説明文改訂による旧Index失効、Language未選択・版不一致拒否を扱う。一方、[TEI Draft #4893](https://github.com/hat47x/tei-platform/pull/4893)は、同じFixtureで同じ機能領域を別テストファイルに実装している（確認時点でopen/draft・未マージ）。**別PR/別テスト名であるだけでは独立した成果件数に数えない**。

このDraftには、**元ファイルの変更後に旧Loadからもう一度Indexを組み立てても、新しいディスク内容を取り込まない**ことなど、既存#4890の旧Index `Validate`失効負例とは区別して確認すべき候補もある。後続の実装担当は、(1)現行mainの正負条件、(2)Draftだけが観測する追加の故障、(3)同一HEADで成立する実結果、(4)その負例を既存のどのOwnerテストへ返すか、を比較する。独自性が確認できた検査だけを最小差分で提案し直し、同じ期待を満たす別Parser/第二Expected/Fixtureを丸ごと増設しない。

ここで行ったのはmainの実GoテストとDraft差分のSource照合。#4893の実CI検収・追加ケースの効果・統合判断は**NOT RUN／Owner未採用**。TAI #233の探索候補を削除・制限する措置ではなく、**候補の幅と採用済み成果の数え方を分ける**運用である。

**後続に共通化した検収**：実TEIの同じ型付きRuleが別の記述表層にある場合も、元Source位置・Revisionは別である。SUI [main #3459](https://github.com/hat47x/sui-sensemaking/pull/3459)では同じ文字列が二箇所に存在すると選択Digestは一致しても選択byte位置が異なる。両者を組み合わせた**意味・原文の位置・配布物の一致を分ける反例**と、Ownerへの引渡しは[横断§56](harness-cross-ui-session-probe-2026-11-14.md)へ集約した。この並行作業票では同じ証拠Packet/Runnerを重複定義しない。TAI #168の独立H2/H3四Slot（比較適格0/4）とTEI #4583のStage1→Stage2を、この追加反例の必須条件にしない。
