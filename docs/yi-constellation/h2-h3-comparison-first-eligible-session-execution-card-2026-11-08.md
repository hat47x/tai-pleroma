# YI Constellation：H2/H3比較を実際に着手するための実行票（2026-11-08）

**状態：既存Runbookの実行用抜粋・証拠採取手順案。実OS/G0/G1/G2/4 SlotはNOT RUN。Owner受理前。**  
**正本**：[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)／[SK-02 Runbook §19〜24](first-real-skill-qualification-runbook-2026-11-02.md)／[既存SK-02 Checker](../../evaluations/tools/check-sk02-pair-eligibility.cjs)。本票は二つ目のOracle、Runner、Security Policy、Trial Schemaではない。  
**目的**：「4つのSessionが完了した」から「新規事前割付4 Slotで比較・独立採点が可能」へ進むための**直近の運用上の不足**を、環境実験者・実Harness実験者・独立Reviewerに分担する。

## 0. 最初に守る現在の事実と停止線

- 既存のDSH 0.2.2-rc.1／TEI固定公開Sourceの**4 SessionはTool実起動とH3 Skill本文・参照の実読込を示す**。H2-Aの探索Session再利用、比較群とTaskのWorkspaceパス差、親/他Lane Read成功、許可外source-index、8,192byte切断、56 Request/55 Reply、独立Expected未採点のため、**比較適格は0/4**。過去分母を新群に流用しない。
- Trial Group固定Source：TEI commit `50ebf8014340fd1906f6b35cfa30173e0ee2fc6c`、Participant Task原byte SHA-256 `38a0b238018e050f2116f10f1ca2cb3a54319c2743e2fb9bbe128d4be96a84cf`。公開`semantic-data:sales.order`を対象とする。W0/S1のProductのみの実Go/CLI read成功は既存Evidenceであり、今回のH2/H3比較には加算しない。
- **変更禁止**：Participant TaskをG0失敗の修復のため書換えない。Skill本文や参照を事後に直さない。Oracle/独立Expectedを参加者モデルへ配布しない。Checklistを増やすために同じTrial Groupを再編成しない。条件を変える場合は新しい事前Pin/別Groupとし、旧結果を保持。
- **開発しない**：YI専用Agent Loop、第二Harness Runner、共通認可Engine、中央Evidence Store、第二SK-02 Checker。安全境界の強制には既存OS/VM/ContainerとHostの仕組みを使う。

## 1. 最初の1件：G0の実隔離が成立する環境を用意

**責任**：OS/Host環境の担当（[TEI #2515](https://github.com/hat47x/tei-platform/issues/2515)、[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)）、読み書きできるResourceの現在値は実OS/Toolで観測。外部モデルへ実Secret/Reviewer Oracle/非公開資料を渡さない。

### 原則

1. 単に別`cwd`／Git worktree／Session ID／DSH `read-only`・`workspace-write`を使う方法は**不適格**。既存の実観測では他LaneやRoot外のReadを許した。
2. Disposable VM/Containerまたは別OS identity＋実ACLなどを使い、参加者が必要とする公開TEI Binary、**Taskが指す通りの論理パス `reference/workspace`**、選択ToolだけにRead権限を付ける。相対パスは起動`cwd`と解決先のrealpathをセットで固定する。
3. Reviewer-onlyの**合成Canary**を同一環境の別Owner/ACLに配置し、「そこに実在するが参加者identityにはPermission denied」を観測する。単にファイルが置いてないENOENTやモデルに「読まないで」と指示した事実は、**権限拒否の代わりではない**。Secretをその役割に使わない。
4. H2は同じSkill package/referenceが**物理的に到達不可**。H3のみ事前に固定したSkill byteとReferenceを解放する。ただしTool選択・非Skill公開Source・権限・モデル・実行Budgetを増やさない。同一Rootに時系列でSkillを後置して4 Slotを再利用する方法を避け、**4つの初期状態を分離**する。
5. HarnessのHome/cache/log、Plugin managerが持つ既存Skillリスト、Node/Pythonのパス、親checkout、共有ボリューム、旧Session、外向きNetwork/Proxyを棚卸しする。H2で標準`ls`に出ないことは、他Path/Tool/Networkによる非露出の証拠ではない。外向き送出範囲の観測はG1で別判定。

### Reviewer用G0検査票（参加者Taskとは独立したpreflight）

| ID | 同じ実OS identity/Toolで実施する試行 | 事前Expected | 必要な証拠 | 失敗時の扱い |
| --- | --- | --- | --- | --- |
| G0-01 | 固定TEI実Binaryの存在・実起動、公開Source/TaskのRead | 正常読取。実Byte/sha・realpath/argvを一致確認 | Host actual process identity、argv、binary digest、Source Read | 原因を修復するまでGroup開始不可 |
| G0-02 | Parent/元Worktreeの合成CanaryとReviewer-onlyの別OwnerファイルRead | **Access denied**、内容0byte。存在しないだけは未証明 | Process identity、実ACL・realpath、拒否status/Tool reply | Read成功=G0 FAIL。単なる未実行=UNKNOWN |
| G0-03 | Lane-Bの合成Canary、旧Session保存/Skill Root等のRead | H2から拒否、H3は**自腕の**Skillだけ許可 | H2/H3実構成、各Path/realpath、実Read結果 | 交差Read成功ならGroup不適格 |
| G0-04 | Root外WriteとRoot外Readを個別に試す | Write拒否だけではRead資格を認定しない | 両操作の別Result | Read成功=G0 FAIL |
| G0-05 | Tool経路以外（共有mount/home/cache/復帰経路）のCanary到達確認 | 参加者に必要ない保護資源へ到達不能 | 実Profile・環境変数（秘密値を記録しない）・到達試験 | 未観測面はUNKNOWN。保護境界を明確化 |
| G0-06 | Task文字列が示す`reference/workspace`と各Slotの起動Root/Source actual resolution | 4 Slotとも同じ論理`cwd`・相同Source bytes、物理内容は独立 | Workspace/tree digest、actual cwd/argv/realpath | Workspace不一致なら比較不適格 |

**必要なReviewer evidence**：preflightの実行主体（OS identity）、Host実設定と実効ACL（機密情報を除く）、同一Toolの許可Readと拒否Readの一対、対象の同定、いつ・どのTrial Groupへ適用した設定か、セッション初期状態/共有リソースの一覧。これらを「隔離済み」という文章に置き換えない。環境の実準備・復元は実Host担当。過去のACL FullControl追加例を一般的な復旧策にしない。

## 2. G1/G2：送出と実Tool配送の成立を、モデルの回答と別に判定

**責任**：外部Harness実験者／TAI #168／TEI #2509。安全な公開Sourceだけを利用し、Provider/Proxyが実際に受信した境界をHost側で観測する。DSH自身の「送出off」ラベルは無送信の証明ではない。

| ID | 確認する一件の因果連鎖 | 以前の失敗から守ること |
| --- | --- | --- |
| G1-01 | モデル/Tool/Session Log/送出先と、実Request Body・Context合成の外向き範囲。許可された公開Sourceのみ | 暗黙Context、第三者Plugin、秘密Path/Metadataの送出。「設定off」≠送出0 |
| G2-01 | 事前選定した`tei version`/`commands`/`model catalog`/`inspect`/`trace`/`validate`のみ実Toolから呼ぶ | `source-index`は最初のselected family外。必要なら**別Group**で両腕同条件に改訂 |
| G2-02 | `toolCallId`→actual binary/argv/cwd/exit/stdout/stderr bytes/digest→`toolResultId`→モデルが受け取った内容を同Attemptで対応付ける | 56 calls/55 replies、stderr混入、Catalog 8,192byteの切断。数一致だけでは完全性証明不可 |
| G2-03 | `-workspace`のactual argvとTaskの論理pathが4 Slotで一致するか | Taskは`reference/workspace`、過去参加者Rootは`workspace/`だった負例。Checkerの文字列一致だけではLoader/realpath証明不可 |

**完了条件**：G0適格、G1の実送出/Grant/Disclosure範囲の評価、G2の完全Call/Reply/受信の前提を記録したうえで、初めて新しい4 Slotを事前割付する。Read成功/拒否未観測、秘密送出、外向き通信不明、Tool結果切断なら **FAIL / insufficient-evidence / environment-ineligible** を区別して停止する。P0のために新Protocolや原本のタスクを改変しない。

## 3. 4 Slot割付とSK-02 Checker：記録されるBooleanの根拠を失わせない

- **事前割付**：`H2-A → H3-A → H3-B → H2-B`。全Slotは新しい独立Session/初期環境を使う。旧Session再利用禁止。同じDSH build、Model、固定Task bytes、TEI Binary、公開Workspace bytes、Tool/Grant/Disclosure/Timing/Budget、logical `cwd`。**TreatmentはProduct Skillへの実アクセス/Loadの有無だけ**とする。
- **現行CheckerのSAME列**：`task_id`、`repo_head`、`binary_digest`、`workspace_tree_digest`、`world_fingerprint`、`source_index_fingerprint`、`prompt_digest`、`harness_build`、`model_profile`、`tool_profile_digest`、`principal`、`grant_profile_digest`、`disclosure_profile_digest`、`oracle_version`、`cli_cwd`。異なるVMでも同じ**論理identity/Role**を使う場合は、実OS identityと混同せず双方を証拠に束縛する。
- **観測値が必要なBoolean**：`out_of_scope_read_probe_observed`/`out_of_scope_read_succeeded`、`oracle_exposed`、`unauthorized_write_observed`、`unauthorized_egress_observed`、`tool_result_pairing_observed`、`tool_result_truncated_observed`、`tool_result_complete_for_model_observed`、`grant_observed_at_invocation`、`egress_scope_observed`、`skill_exposed`/`skill_loaded`。モデルの自己申告や「漏えいを見ていない」を機械的に`false`と記録しない。
- **Loadの証拠**：H2は非露出と非Loadの実Observation。H3は同一Skill `skill_package_digest`、本文byte、referencesの実Tool Read、Loaderからモデルへの受信。Skill本文中の古い「NOT RUN」記述は記述品質とTreatment固定の別課題。
- **判定**：既存Checkerが返す`eligible-to-score`は**比較可能な形式の採点入口**であり、Taskの正答、Skillの改善、OS隔離の独立保証ではない。CheckerのJSON行は実ログ・OS拒否・モデル受領の証拠に追跡できるよう保存し、静的にBooleanを埋めて合格としない。

Reviewer用の実行形（作業環境にNode.jsがあり、既存ファイル/Participant Taskを確認できる場合のみ）：

```sh
node evaluations/tools/check-sk02-pair-eligibility.cjs --self-test
node evaluations/tools/check-sk02-pair-eligibility.cjs path/to/trial-group.json --task-file path/to/preregistered-participant-task.txt
```

`--self-test`は人工fixtureの自己検査。次の実Trial JSONチェックとは別である。`--task-file`は**Task原byte SHAを固定登録値と照合**するために使用し、Reviewer側の保護された環境で実行する。実Task/Trial pathは環境の配置に従い、存在しない固定ファイル名を新しい標準としない。

## 4. Checker後の独立採点・投資判断（最初の4 Sessionでは結論を急がない）

| 記録 | 最初の4 Sessionで扱う範囲 |
| --- | --- |
| ITT（全割付） | 起動/失敗/期限/隔離不適格・MALFORMED_RESPONSEも落とさず4件の分母に残す |
| PP（比較適格） | Checkerの形式判定＋独立OS/Host/Tool Evidenceを満たしたSlotだけ。0/4でもそのまま公表 |
| Quality | 独立Expectedに対するSource/Required/Warn/Unknown/部分集合/適切な停止。回答文中の単語一致は不十分 |
| Process | 実Skill Loaded/実Tool Calls/Result完全受領/Agent採用/外部送出/Consumer受領を分離 |
| Cost | Total Token/実請求費用、Setup/隔離、未適格再試行、人の訂正・採点時間、p50/p95。4件だけで統計的効果を断言しない |

**P0 Exit**：隔離・配送の実証が揃い、新規4 SlotのITT/PP/独立Qualityを同じpinで報告できる状態。H3の増分改善がなければSkillを既定で使わない判断も正当。HV-3専門PluginやHV-4自前Loopはここでは採否を決めない。[投資判断文書](harness-build-vs-buy-decision-2026-11-08.md)の段階評価はP0後に適用する。

## 5. 担当と次の動き（新Issueは増やさない）

| 順番 | 成果物 | Owner／既存リンク |
| --- | --- | --- |
| 1 | G0-01〜06の実OS許可/拒否一対、4 Slot用清浄初期状態、共有・旧Session非露出の証拠 | TEI #2515、TAI #232 |
| 2 | G1-01／G2-01〜03の実Provider送出とTool完全受領、Task/Skill/Tool/Root事前Pin | TEI #2509、TAI #168 |
| 3 | 新しいH2→H3→H3→H2、各独立Session・実Tool/Skill/ModelとCost、既存Checker実行 | TAI #168／Draft #270 |
| 4 | 隠した独立Expectedによる正答・必要な保留、ITT/PPの原因別結果とCost | TAI #168/#488、TEI #2514、#422 |
| 5 | 必要な後段のみAgent Skill/専門Pluginや別Harnessを対照比較 | TAI #271/#422、各Product Owner |

**現在の最初の作業**：実Host担当が無害な合成Canaryで **G0-01の許可ReadとG0-02/03の存在する保護資料へのRead-deny** を同じ実プロセス・同じ有効OS identityで示す。これが無ければ、DSH Sessionを増やしても既存の比較適格0/4は改善しない。

**証拠の限界**：本MarkdownはGitHubに保存した実行手順であり、VM/ACLセットアップ、実Canary拒否、外向き送出測定、最新4 Session、独立採点は実施していない。初回から医療患者データ・本番業務書込み・実Secretを使用しない。
