# TAIシリーズの能力増幅・縮退適性と横断実証計画（2026-10-30）

状態: **Draft / Proposed / NOT RUN**。設計検討と既存Issueの証拠を整理する非規範的計画。Ownerによる正式な意味受理、Production Authority、RC完成、実ユーザーQoLの効果検証を宣言しない。新しい中央Host、共有DB、第二の正本、独自生成AIハーネス、新統一Schemaを前提にしない。

## 1. 製品命題

TAI PleromaはClaude Code / Codex / Dots / Grok Bot等の**外部生成AIハーネスから必要に応じて用いる**SEI/SUI/TEI/SHO/EKI等の製品シリーズであり、そのハーネスの知的・実務的な能力を実証可能な形で増幅する。基盤モデル・ハーネスの成熟により重複機能を縮退・移譲・廃止する一方、用途を超えて必要となるコア価値へ集中する。

「能力増幅」を呼出し可能なツール数、Agentの稼働時間、生成量で定義しない。利用者の目的を、根拠と権限と結果を失わずに実現する**成果・信頼性・人間の認知負担の増分**で判定する。

- **意味の分離**：観測 ≠ 解釈 ≠ 候補 ≠ 人の判断 ≠ 業務意味受理 ≠ 現行権限 ≠ 要求送出 ≠ 外部効果 ≠ 目的上の成果。
- **時点と適用範囲**：本文・digestが再一致しても旧受理は自動復活しない。source、model、subject、scope、review、authority、resultの版を必要に応じ固定する。
- **不確実性**：未取得、未解析、未確認、矛盾、結果不明を「なし」や「成功」に変換しない。対象集合の欠落を全件検査PASSから隠さない。
- **認知負担**：通知・質問・承認・モデル入力・確認作業はコスト。必要な安全停止条件を弱めず、通常時は最小十分の介入にする。
- **交換可能性**：ハーネス固有の記憶・計画・APIを製品群の意味正本としない。実行に必要な権限や秘密をハーネス間で自動継承しない。
- **実現先独立**：TEIの生成物は外部Hostで動く。SEIが汎用エージェントRuntimeを持たず、EKIがすべての簡単な処理を引き受ける必要もない。

## 2. 製品別：縮退可能な表層と候補コア

| 製品 | ハーネスへ委譲/縮退する候補 | 継続して検証する価値 | 受入で検査する反例 |
| --- | --- | --- | --- |
| SEI | 汎用RAG、要約、普通の記憶/Method routing | Method適用条件・反例、出所/時点/文脈付き判断履歴、再開時の古い判断の隔離 | 同じ文章が戻ると旧確認復活、未調理を嫌いと推定 |
| SUI | 普通のマップ/図解生成、一般的なアイデア出し | 曖昧さ・違和感・少数意見を失わない意味形成、編集結果から根拠へ戻れること | AIが「多数派」を唯一の意味へ確定 |
| TEI | 定型CRUD/画面/SQL/コード生成、一般的なデバッグ | 受理した業務・データ・機能の意味と生成物、シミュレーション、変更影響の照合 | 対象集合Lと返却集合Rの欠落、unsupported roundingを意味受理と混同 |
| SHO | 一般校正・要約・フォーマット生成 | 文書内の主張/図/表から正しい原典・版・表示依存へ再到達できること | 同名異内容xlsxへの出典誤解決、SVG変更を表示同一と主張 |
| EKI | 一般的なAgent起動・スケジューラ・retry | 信頼条件付きの委任、権限失効、Worker結果と最終的な外部効果の独立確認 | queuedを完了扱い、ACK喪失後の二重作用 |
| TAI | 汎用planner/チャット/常時通知/万能dashboard | 人とAIの継続的な活動、複数目的の調整、軽い日常から未知課題への段階的な適応、余白の保全 | 完了件数最大化のため休息と人の意図を侵食 |

※これは各製品の「残す価値」の仮説であり、各プロダクトの実装仕様/正式なCore分類を固定しない。

## 3. 開発判断：4つの縮退処遇

1. **外部に委譲**：汎用Agent計画、会話、ツール操作、定期実行。外部機能で差がなければ重複実装しない。
2. **薄いAdapter/Skill**：参照変換、Method提示、配布、独立結果照合だけに絞る。MCP・CLI・ファイル・APIの一つを必要に応じ選ぶ。
3. **独立コア維持**：意味の契約、受理/制約の境界、version-aware validation、適用範囲、独立検証、fixture、事故の反例を保持する。必ずしも独立常駐製品とは限らない。
4. **撤去**：価値も独立確認の必要性も失った場合に、利用者のデータと意味の移行/復元経路を確保したうえで廃止する。過去の開発費を存続理由にしない。

判断は**モデルの機能説明ではなく、同じ入力・同じ境界・同じ対象版でのablation評価**で行う。新しいモデル/ハーネスの版が出たら一部を再評価できるようにする。

## 4. 外部ハーネスへの接続面

- **Tools/MCP**：既存のread-only inspect/validate/lookupを最優先。MCP transportの認証と、業務上のAction認可は別。stdioにHTTP OAuth仕様を機械的に当てはめない。
- **Skills**：適用条件、失敗/停止条件、Method根拠、入出力、反例を記述。プロンプトは安全フェンスや「実行済み」の証拠にならない。
- **通常ファイル/CLI**：最小で確実な経路。ハーネス間のhandoffは必要な文脈だけを出力し、秘密・個人の生データ・内部推論全文を複製しない。
- **Agent-to-Agent/A2A**：複数の外部Agent間に本当にリモートタスク受渡しが必要になったときのみ比較。Capability discoveryとtask exchangeは、TAI/SEIの意味受理や実外部効果を保証しない。
- **Traces**：OpenTelemetry GenAIのagent/workflow/tool/skill spanを観測参照候補として用いる。ただし実行トレースと、正式な業務receipt、Decision履歴、結果は別。個人の予定・注文・プロンプト等の漏えいを避ける。

参考（実装採用・接続合格を意味しない）:
- MCP 2026-07-28 https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/basic/index.mdx
- A2A 1.0.0仕様 https://a2a-protocol.org/v1.0.0/specification
- OTel GenAI Semantic Conventions（Development） https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md

## 5. 初期の実践：薄い運用から高度化し、不要なら縮退

- **L0**：ハーネス＋Markdown/CSV/Excel/既存カレンダー/Issue。少量の作業はここで完結できる。
- **L1**：既存CLI/MCP、版つきSource、最小のMethod・候補・結果照合。本人が望む部分だけ自動準備する。
- **L2**：複数情報・同時更新が必要なら既存DB/SQLite、TEIの限定モデル、SEIの時点つき再評価、SHOの出典付き文書。
- **L3**：複数主体・高い不確実性・不可逆作用・災害/BCPなら、用途に必要な委任/権限/独立効果照合/可視化を追加。

L0〜L3は固定の権限階層・Schemaではなく説明用の便宜である。低リスクの行為でも既存の実行先Authorityを飛ばさない。高負荷でない重要行為にも最低限の安全フェンスが必要。状況が落ち着けば、仕組みと通知を**降格**できること。

### 5.1 仮定の回収

初動で置いた「NULL=ゼロ」「同名=同一対象」「部門=現在の許可」「一度の行動=永続嗜好」「各部署別テーブル」「全組織共通Rule」を、Sourceと当時の適用範囲、依存先、反例、外部作用の有無、再確認条件へ紐付ける。業務の安全を左右する仮定は当初から作用を停止する。そうでない仮定は運用安定後に**影響の大きさ、不可逆性、変更の必要性、確認負担を別軸で見て**少数の質問へ整理する。質問を表示した事実と人が確認・受理した事実は分ける。訂正後は影響範囲だけ再検査し、履歴を上書きしない。

## 6. 3本の縦切りを一つの方式で比較

| シナリオ | 具体的な変化 | TAi/SEI/TEI/SHO/EKIの増分候補 | 不合格条件 |
| --- | --- | --- | --- |
| SCN-004（企業/未知課題） | 合成危機→仮設DB/手作業→供給観測変更→安定期の仮定確認 | Safe partial Action、出典/未決、意味化、限度付き委任 | 未確認の意味を受理、R≠Lの欠落を見逃す、証跡があっても実効果不明 |
| SCN-005（自炊/購買） | 予定変更→未調理→食材不足→代替SKU→注文応答喪失 | 嗜好の時間スコープ、在庫/単位計算、カート/注文の独立結果 | 二重注文、推測を恒久嗜好に固定、毎回確認を強制 |
| Personal Agency #167 | 趣味創作＋副業期限＋休息→予定変更/中断/再開 | 活動の継続、適時準備、本人の価値と余白の尊重 | タスク完了率のため休息を侵食、無断予約/契約、再開時の根拠欠損 |

同じ最小の参照関係（正本のコピーではない）で3件の目的・当時の根拠・変更・Action・Outcomeをたどれるか検証する。業務専用のTEIモデルを個人生活全般へ強制せず、個人の心理や健康状態を自動推定して正本化しない。実利用者へのQoL改善は合成試験では証明できない。

## 7. 再現可能な評価票と最小実験

### 7.1 対照条件
- A：外部ハーネス単体＋既存のカレンダー/Issue/CLI。
- B：同じハーネス＋製品一つ（最初は既存SEIの判断再開、またはSHO/MMIのinspect）。
- C：同じハーネス＋実際に必要な2製品以上（使わない製品は起動しない）。
- D：途中でハーネスを交換し、元のSourceと判断履歴から続行。
- E：最新の強いハーネスのみで再実施し、TAI機能の**撤去可能性**を測定。

比較時に固定するもの：入力のrevision/sha、source visibility、利用可能なツール、許可、人物の意図、時刻条件、環境・生成モデルの版。結果不明や利用不可は別分類。追加トークン/価格、処理時間、人の確認回数、情報露出面積を記録。

### 7.2 現存機構の再利用と未観測
現行TAIのREADMEと参照接続には、SHO(MMI)のread-only inspect/select、SEI一時storeのdecision/resume、TEIの型validate、SUIのカード連結、EKIのAPI/queuedといった**限定された参照観測**がある。これは製品間の実業務一巡、意味の受理、外部効果、実ユーザー価値を示さない。
[接続調査](../integrations/capability-inventory.md) と [クリティカルパス](critical-path-2026-10.md) に固定版と制約あり。最新mainに過去receiptを流用しない。

### 7.3 最初の追加fixture（一件だけ）
合成案件「同じ本文だが、出典のscopeが変化した判断の再開」：
1. Harness Aが原Source S1/v1をSHO(MMI)で参照、SEI Decision候補Dを保存。AIの推論は提案であり、本人の受理なし。
2. S1/v2で内容がA→B→Aへ復帰するが、target scopeとsource revisionを変更。判定の本文が同じでもDの旧受理は自動復活しない。
3. Harness Bへ通常ファイル/CLIの最小handoffを渡す。Bが対象版・Unknown・確認経路を維持できるか照合。
4. 単体Harnessの会話要約条件と比較し、正しく再開するための人手確認回数と余計なメタデータを測定。
5. 次にだけmock Actionを付加し、認可失効/応答喪失後の再送を禁止、独立Lookup結果を照合する。

**停止条件**：現行の既存SEI出力が必要なscope/digestを投影しない場合、そう表示する。暗黙に埋めず、原recordへの再照会で補えるか調査する。既存TAI #33やSEI #711/#660等の実装不足を、新しい正本の導入で迂回しない。

### 7.4 Gateと成果物
- **G0 inventory**：2つの外部ハーネスで同じread-only機能が利用可能か、unsupported/未接続を別記。exact versions/契約。
- **G1 semantic handoff**：A→B→A'のScope/Source差と失効、部分参照・未取得を正しく保持する。Source、原record、投影を比較する。
- **G2 action**：mockだけ。Proposal、Policy check、Host Authority、Submit、Receipt、Independent Outcomeを独立列にする。
- **G3 adaptation**：SCN-004/005/#167に各一件の予定/Source/環境変化を注入。過剰質問・無断一般化・過少エスカレーションを負例にする。
- **G4 ablation**：一機能を除去/新版Harnessへ交換し、実効品質が落ちなければ縮退処遇を提案。RC準備へ受入条件とNOT RUNを引き継ぐ。

合格には実行コマンド・exact版・観測ログ・結果・対照・未実行・再現手順が必要。新しい共通データモデル/プロトコル/評価エンジンの採用は実証後。

## 8. 横断引渡しとOwner判断境界

| 担当 | 既存参照と必要な差分 | 留保 |
| --- | --- | --- |
| TAI #168 | Harness-first、能力縮退、ablation評価・3シナリオ合流を所有 | 外部Harnessの比較を未実施の成功にしない |
| TAI #165/#166/#167 | 個別シナリオ・成果評価/認知負担・例外と仮定回収 | すべてが本番運用可能という扱いをしない |
| SEI #660/#677/#711 | 文脈、根拠、Method、実storeとの接続経路 | 新Decision正本や心理状態の断定を避ける |
| TEI #958/#1120/#1440/#1444/#2017/#2092 | Source→意味候補→受理境界、選択的Action実現、AI書込み窓 | 合成試験/byte一致/生成成功を意味受理としない |
| SHO/MMI #508/#658/#672、C-01/T2 | 原典と引用/表示依存の整合、保存/再開、必要な配布CLI検証 | 出典未解決やread-only不足を成功としない |
| EKI #57/#138 | 信頼条件、Task受付/Worker Result/実作用の境界 | queued≠done |
| SUI | 未解決・異論・反証を人/AIが読み取れる投影 | 図ができたことを意味確定としない |

Ownerに残すのは、対象業務の意味の正式受理、本番の権限と適用範囲、個人の委任・データ共有の許諾、どの外部Providerが結果正本を持つか、実利用を開始するか。これらの決定をAIの推奨やIssueコメントで代替しない。合成RCまでの設計・小試験は独立して進める。

## 9. 計画の改訂・削減基準

- 進捗＝文書数ではなく、同じ根拠と判断をハーネス間で失わず再開し、前後の実際の効果まで検証できた件数。
- コアの価値が外部機能の成熟で消えたら、不要な部分を削除することを**成功**として記録する。
- 未完成を隠す汎用Schema・監視・Scheduler・新Hostを追加しない。
- 初期検証で有益な差が出ない場合は、独立製品の複合導入を進めない。CLI+通常ファイル+既存Harnessに縮退する。
- この文書は各Issue/契約の正本を置き換えず、横断実証・採否を議論するための計画である。

## 10. 他製品の直近設計による補正（2026-10-30）

**A. 外部Plugin Consumer = ハーネス向けMCPではない。** [TEI #2390](https://github.com/hat47x/tei-platform/issues/2390) のC0（契約だけ）、C1（外部Library）、C2（隔離呼出し）、C3（Host固有wrapper）を接続候補として参照する。TEIのPluginが外部製品から使えることと、そのPluginをMCP経由でAIへ公開することは別。MCPのツール説明、WIT/JSON shape、ライブラリロード成功は業務意味の受理や実行許可ではない。初回のread-only資料/Decisionの検査をTEI外部Consumer実装と重複させない。

**B. UI外部制御はビルド可能性の境界。** [TEI #2391](https://github.com/hat47x/tei-platform/issues/2391) の標準UI外部制御Pluginは、テスト/Computer Useの支援に限って試す。本番の生成物に必須の常駐制御Port/Debug情報を残さず、build optionによる完全除去も受入候補とする。TAIで同じUI制御APIを再実装しない。AIの操作容易性を増してもProviderの認可・作用フェンスを広げない。

**C. 現在の詳細取得と権限を混ぜない。** [TEI #1045](https://github.com/hat47x/tei-platform/issues/1045) はProjectionを軽く保ち、Target/Context/Evidenceの詳細を必要時だけ、**semantic queryとTransport Accessを分けて**取得する検討。TAI/SEIは相手の権限を推定して詳細を複製しない。取得不能な根拠と、現在の世界に根拠が存在しないことを区別し、redacted情報の有無を漏らさない。Tool戻り値に埋め込まれた任意の文章を次のHarnessの高優先度Instructionにしない。

**D. SEIが現在公開していない書込み面を想定しない。** [SEI #711](https://github.com/hat47x/sei-cognition/issues/711) ではCLI/MCPのObservation/Interpretation/QuestionのWrite経路が未確定。初回は既存Decisionと原recordへ戻れる read-only 確認を優先する。個人の仮定や観測を、SEIに保存済みだと捏造しない。

**E. SHO出典再解決・納品閉包は別責任。** [MMI #658](https://github.com/hat47x/markdown-matrix-injector/issues/658) の「文書が宣言した参照／存在が確認された実体／契約上の要求」は別。C-01/T2の同名別ファイル誤解決と#672の配布CLI受入もTAIに再実装せず、出典の取得・未取得の証拠を受け取る。TAIによる最終の報告が正しく見えても、SHOの原本解決が誤れば元の欠陥は消えない。

## 11. 最小の実証スライス SW-01（他チャットとの差分だけ）

[TAI #33](https://github.com/hat47x/tai-pleroma/issues/33)では、SEIの原bundleからExactBindingを取り出す既存 `reference-sei-decision -basis-bundle` と、SEI `BuildResume` がkind:idへ情報を縮める差がすでに確認されている。**この抽出CLIやA→B→A' fixtureをTAI #168側で作り直さない。** 再利用するのは既存CLIの出力と、各Harnessが判断に使うread-only Handoffまでに限定する。

### 11.1 同一出力に見えても異なる三条件

| Case | 固定する入力 | 何を分けられるか | 期待される振る舞い |
| --- | --- | --- | --- |
| SW-01a | 同じDecision表示。Source v1→v2→v3、v1/v3の本文bytes同一、scope別 | 内容一致とhistorical basisの同一性 | v1の旧判断をv3に自動適用しない。差分を原recordのbindingで示す |
| SW-01b | Sourceがunknown / failed retrieval / access redactedの三条件 | 存在否定・取得不能・権限不足 | 不在/矛盾なしとは断定せず、見せてよい範囲の未確定だけ伝える |
| SW-01c | 検証済みの原記録は同じ、現在の適用Contextまたは依頼の作用範囲だけ変更 | 歴史の完全性と現在の適用/委任条件 | 過去の判断履歴は残し、現時点の適用可能性/実行許可は別の未判定列にする |

初回の合成入力は個人属性・実購買/業務資料を含めず、実際の受理イベントを偽装しない。Reference fixtureが過去の意思決定を持たない場合は **historical review=not established** と記録する。

### 11.2 ハーネスの出力を監査するための最小観測票

既存CLI/APIの出力をそのまま証拠とし、追加するのは一時的な比較表のみ。正本schemaとして新設しない。

| 観測列 | 確認する具体的な違い |
| --- | --- |
| Input/revision | 元のSource ID / exact versionまたはdigest / effective context / 利用可能な権限の範囲 |
| Harness/tool | 生成AI製品/モデル版、Skill/MCP/CLI/ファイルの経路、実際の成功・失敗、利用できなかった機能 |
| Historical basis | 原recordのBasisRefsに再到達したか、kind:idへ縮めたか、content digestだけでscopeが消えたか |
| Current applicability | current contextに対しconfirmed / needs-review / indeterminate / access-unavailable等、確認できる範囲だけ表示したか（例示カテゴリ、固定enumではない） |
| Current authority | 外部作用を扱う場合に有効な委任/Host Provider認可を別に確認したか。read-only試験ではnot-tested |
| Human attention | 適切な次の一問/質問なし/不要な多重確認、本人の休息・予定変更への適応 |
| Result evidence | ハーネス文面と原record/実Providerの独立照合、NOT RUN・unknownを失わないか |
| Cost | Token/時間/初期設定・追加依存・再実行負荷・個人データ露出の増分 |

### 11.3 必須の対照・負例

- **A** Harness単体（取得可能な同じ原Sourceを与える）、**B** +既存SEI read-only Basis照合、**C** +SHOのSource locatorが必要な場合だけ追加、**D** 同じread-onlyデータから別Harnessで再開。機能を足す順序が比較結果を歪めないよう、同じ入力とツール利用条件を記録する。
- **負例1**：LLMが「旧結論は現在も有効」と回答しても、原記録・有効期間・主体の確認がなければpassとしない。
- **負例2**：basis digestだけ一致しても、scope/target/原locatorが違うものを同一扱いしない。
- **負例3**：同じHarnessが正しい回答をしても、Toolがhidden Evidenceの有無を漏らしたならfail。
- **負例4**：必要な情報が未取得なのに、Harnessがもっともらしい補完で質問を省略してもfail。
- **負例5**：Productの機能差がないのに、TAIの追加設定・通知・Token負担だけ増えたらablation候補。

**作業者が最初に実行すること**：TAI mainとSEIの実際のsource/CLI版を固定して #33 の既存`-basis-bundle`再現手順・fixtureを取得し、`BuildResume`表示との差を照合。新たなHarnessの呼出しができる環境では、同一fixtureでA/Bを一巡してログと質問数を採る。外部Harnessの利用が未接続なら **NOT RUN/unsupported** と明記し、単なる手作り予測をactualとしない。

### 11.4 成果物・担当・受入判定

- **TAI横断担当**：A/B/C/D比較票、source/head、知識・権限・活動の別列、ablation処遇案。#33の原試験/SEI内部実装を変更せず参照。
- **SEI担当**：原recordの参照・scope/target/Basis差とcurrent-use判断の不足を分類。#660/#711を正本として使い、TAI専用のDecision正本を作らない。
- **SHO/MMI担当**：Source locatorの実解決先と取得可能性、必要なときだけ詳細資料を提供。#658/C-01/T2/#672は独立評価を維持。
- **TEI/EKI担当**：初回はno-effect。将来のmock Effectで、Execution intentとcurrent Host authority、Provider receipt/最終結果の照合を既存#1174等へ引き渡す。
- **Owner待ち**：実業務意味、本人/組織の委任、共有してよい実資料、本番作用はOwnerが判断。合成read-only比較は先行できる。

**SW-01のExit**：2つの実際に利用可能な外部Harnessを用いて、同じ元資料から (i) historical basis差分、(ii) 現在の適用性、(iii) 現行権限を混同せず、(iv) Aに対するB/Cの増分または増分なしを、ログで反証可能に示す。二つのHarnessが未接続なら本条件は未達。現時点でこの実行は **NOT RUN**。

### 11.5 既存READMEから確定できる準備コマンド（**未実行**）

以下はTAI `tools/reference-sei-decision/README.md` と `tools/reference-mmi-readonly/README.md` にある既存の参照経路。各コマンドは **それぞれ指定ディレクトリ内** から実行する。Portable bundleのファイル名は取得時に実在を確認する。各テストのexit/Go/Node/SEI/MMI版を記録し、現在のmainへ過去のreceiptを自動適用しない。

```sh
# TAI checkout の tools/reference-sei-decision 内
cd tools/reference-sei-decision
go test ./...
go run . -sei-root ../../../sei-cognition \
  -basis-bundle /absolute/path/to/existing-portable-bundle.json \
  -out /absolute/path/to/new-basis-inspection.json
```

```sh
# TAI checkout の tools/reference-mmi-readonly 内（SEIのディレクトリからではない）
cd tools/reference-mmi-readonly
go test ./...
go run . -workspace testdata/workspace -mmi-root ../../../markdown-matrix-injector
```

初回に確認できるのは、**既存原bundleの構造/ExactBinding参照を縮めず抽出できること**と、**MMIの合成workspaceを読み取り専用で扱えること**まで。両結果を統合して「同一の現行業務意味」「Source真正性」「実行許可」と言い切らない。

失敗時は、①portable bundleの取得・入力format/未認識contract、②source version/scope/target bindingの欠落、③SEI/MMIへの依存/配置、④MCP実呼出しとTool出力、⑤Harnessの回答に移した時の情報欠落、⑥認可やread accessの境界、を別々の失敗列にする。原bundleが見つからない場合は新しい「受理済み」fixtureを作らず、#33で使われた入力の位置/保全方法を担当へ照会する。

## 12. 2026-10-31 横断収束：TAIが提供するのは「別のAgent」ではなく、状況付きで使える能力

この節は、TEI [#2390](https://github.com/hat47x/tei-platform/issues/2390) の10/31追補（Consumer×Provider×Host×Context×Time）、[#2391](https://github.com/hat47x/tei-platform/issues/2391) のUI外部制御、[#2386](https://github.com/hat47x/tei-platform/issues/2386) の組織/代理、[#2387](https://github.com/hat47x/tei-platform/issues/2387) のQuery構造Explain、[SEI #677](https://github.com/hat47x/sei-cognition/issues/677) の組織意志の引継ぎを横断して整理した **Draft / 未実証** の補足である。

### 12.1 三つの独立した問い

外部Harnessが「その能力を使うべきか」と判断する際、Tool列挙・Skillを読めたことをそのまま答えにしない。

| 問い | 確認するもの | 誰が正本/必要条件を持つか |
| --- | --- | --- |
| **何が実在し、どういう意味か** | Plugin/非実行定義/Service Contract/Provider/選択されたphysical artifact、入力・出力・拒否・NULL・0件・単位・時点、実Load member | 各製品の既存意味契約・Build証拠、Consumer要求、外部Host |
| **今この用途に適するか** | Source/対象集合/Context/鮮度/欠落/不確実性、必要Host API・Lifecycle phase・実行Target、現在の利用資格 | SEIの文脈処理、TEIの分野意味、Consumer/Hostの実条件 |
| **何が実際に起きたか** | 操作送信・UI反応・Provider結果・Commit/Receipt・独立Outcome・本人/組織の目標への効果 | 実際のProvider/Host・利用者。TAIは参照と比較、決定を自称しない |

「portable Plugin」という静的属性で全環境の互換性を宣言しない。意味、配布、実ロード、実利用、権限、外部効果は別々の適合性である。Pluginは**呼び出すサービスだけではなく**、Message定義、テンプレート、DSL/表示資源、Hostイベント用の拡張点を含み得る。非実行定義に架空のRPCやCommitを要求しない。必要なContract/Resource単位を選び、Plugin package丸ごと利用を前提にしない。

### 12.2 論理的に不使用でも、物理的に存在するもの

**TAI-COLOC（既存#2390のP-COLOCを参照）**：read-only機能AしかHarnessに公開していないつもりでも、同じartifactにread-write機能BとHost imports、初期化処理、公開可能なentrypointが残る場合がある。AのみのTool登録・read-only宣言は、Bの到達不能や副作用不存在を保証しない。

- **Adapter/Logical selection**：外部Harnessへ見える能力を必要最小限にする。これはHost Resource/実Load物の隔離の代わりではない。
- **Physical closure**：選択したphysical membersと実Load bytes/依存、到達可能entrypoint、初期化時の副作用を、必要な実装単位で別に観測する。
- **Build exclusion**：TEI #2391の専用UI制御はTest/Developmentで使っても、既定Production成果物から物理除去する。Production UIのブラックボックス試験は可能。Wails/WebViewが既存のMCP等を提供する場合はそれを第一候補とし、TEI独自の重複制御Serverを先に作らない。
- **根拠の更新**：同じコンテンツdigestでも、Source/Target scope、Hostの現行権限、Render用SVG/辞書/テンプレートが変われば、全てが同じ資格で使えるとは限らない。SHO/MMIは表示時に使う資産の依存を必要範囲で照合する。

### 12.3 組織モデルとDSLに求める意味の可搬性

[TEI #2386](https://github.com/hat47x/tei-platform/issues/2386) のOrg/Assignment/Acting Contextでは、所属・兼務・代理は業務意味だが、別テナントへの実行権限は別。異動/組織改編の**有効時点**と**記録時点**も分ける。個人生活では家族/共同購入者の意向を統合許諾へ自動変換しない。組織/家庭どちらも複数主体の権限を「AIが理解した」として自動受理しない。

[TEI #2387](https://github.com/hat47x/tei-platform/issues/2387) のQuery構造Explainは複雑なSQL/CTEを可視化できる候補だが、図やLineageの生成はQueryが要求対象を**すべて取得した**証明ではない。例：要求集合 `L={A(正値),B(数量0)}`、Provider返却 `R=[A]` のとき `checkAll(R)`は成立しても、`R=L`は成立しない。対象集合、取得完全性、NULL/未取得、Scope、Provider同版鮮度を別に検証する。高価な「不存在の一般証明」を義務化せず、対象業務で必要なOracle/独立照合を採用する。

### 12.4 新しいTAI Runtimeを作らずに評価できる価値

TAIの増分価値は**利用者の一つの活動が、根拠の適合性、行為の可否、結果の確実性の三つを混同せず前進すること**である。これには、外部Harnessと独立したSEIの原記録・TEIの意味/Provider検証・SHOのSource参照・EKIの信頼条件/Result観測を必要時に利用すればよい。新しい共通状態正本/汎用Orchestrator/一括Grant Engineを前提にしない。

## 13. 既存EKI実証の進展を正確に受け取る（2026-10-31）

TAI mainに [合成EKI固定コマンド実行のrecord](../evaluations/records/EKI-execution-2026-10-31.json) が追加された。記録が示す範囲は **別OS processのControl/Agentで固定コマンド実行→ResultClaim送信→Attempt `verifying`** まで。 `executionStatus=completed` でも `resultVerified=false`、`resultAccepted=false`、`taskResultAccepted=false`、`sandbox=false`、`resourceLimitsEnforced=false` である。この観測を旧「queuedのみ」へ戻してはいけない一方、外部作業の受理・安全な未信頼Task実行・ビジネス効果が成立したと主張してもいけない。正式な結果検証はEKI側責務のまま。

| 境界 | 最新TAI参照証拠 | 対応する未実証 |
| --- | --- | --- |
| Dispatch / Execute | 合成固定commandの別process実行が記録済み | 任意Task入力、sandbox/Resource制御、ProductionのOwner委任 |
| ResultClaim / Verify | Claim送信まで観測、Attemptはverifying | Result VerificationとAcceptance、独立Output/Effect照合 |
| Business Outcome | なし | Providerの作用確定、受理された業務成果、個人のQoL |

この区別は [TEI #1174](https://github.com/hat47x/tei-platform/issues/1174) のEffect Fenceと、ユーザーが望む「ハーネスに任せても完了を偽装しない」に直結する。応答喪失時の再送可否をHarnessの推測で決めず、対応するProvider側の照会/冪等性/効果識別子に従わせる。

## 14. 最小の能力増幅判定（SW-01後、独立の次段候補）

### 14.1 四つの独立した評価対象

| ID | 検証対象 | ハーネス単体に対して何を比較するか | 不合格とする誤り |
| --- | --- | --- | --- |
| EV-1 認識/継続 | A→B→A'、欠落/取得不能、別Harnessで再開 | 正しい根拠・不明点・scopeの保全、再開の人手 | 旧受理自動復活、redacted dataの開示、正本とprojectionの混同 |
| EV-2 可搬Provider | Pure計算/Message定義等を外部Hostで必要分だけ使用 | 実Load byte、独立Oracle、Host依存、Adapter量 | TEI Runtime必須化、shapeだけで意味合格、COLOCから権限漏れ |
| EV-3 副作用 | 有効委任、mock Submit、ACK喪失、二重実行、独立lookup | 不正作用・結果不明の扱い・照会回数 | queued/ClaimをAcceptedに昇格、権限失効後の作用、二重効果 |
| EV-4 本人/組織への価値 | 個人の休息・創作/買い物、企業の遅延/負担転嫁を同時評価 | 意図実現、不要な質問・承認・費用、犠牲となった別目的 | 完了率のみでQoL/組織利益を宣言、負担を他部署へ転嫁 |

**開始順序**：SW-01（既存#33の原記録・SEI/SHOのread-only比較）を先行。EV-2はTEI #2390/#2392の外部Consumer実証を参照し**別Oracleを作らない**。EV-3はEKI/TEI担当の既存Result・Effect Gateが利用可能になってからmockのみ。EV-4は#165/#166/#167とSEI #677の合成ケースへ接続。各Gateは他のGateの成功を意味しない。

### 14.2 本当に縮退可能であるための判定

同じ入力・許可・Harness版・実利用文脈を固定して、(A)Harness単体、(B)+SEI、(C)+用途に必要な別製品、(D)別Harness引継ぎ、(E)更新された強いHarness単体を比較する。安全境界の必須違反が一つでも起これば平均品質の改善で覆さない。増分がない/外部能力で代替可能なら**委譲/薄いAdapter化/削除**を正式な選択肢とする。追加Pluginの依存/更新負担、利用者の問い合わせ回数と個人情報の露出を、品質と同時に測る。

重要な反証：**「機能を呼べた」だけではEV-1〜4すべてNOT RUN。** Model/Skillの将来成熟を仮定して、未実施の良い結果を先取りしない。実測結果に応じてTAIシリーズの責務・製品境界自体を更新してよい。
