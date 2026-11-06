# RQ7 公開予備刺激・採点・実行前固定

- 状態: **Prepilot protocol / NOT RUN**（2026-11-06）
- 研究本体: [RQ7 有界Graph完全性](RQ7_BOUNDED_GRAPH_OBSERVABILITY_2026-11-06.md)
- 公開刺激: [10ケースの合成入力](../fixtures/RQ7_BOUNDED_COMPLETENESS_PILOT.synthetic.json)
- 公開Gold: [独立した採点表](../fixtures/RQ7_BOUNDED_COMPLETENESS_GOLD.public.json)（**公開開発用で、blind/sealed holdoutではない**）
- 生成・構造チェック用: [Python標準ライブラリのみのfixture tool](../tools/rq7_pilot.py)。ProductのExecution/Graph/Oracleを実装・検証するツールではない

## 1. 研究上の改善点：表示と証拠の因子を本当に分離する

比較条件は下表の2×2である。**同じ証拠水準なら、グラフ/テキストが表現するNode・Edge・版・scope・述語の集合は同一**にする。「図だけに正解が書いてある／テキストだけに異常が明示されている」という比較は無効にする。

| Arm | 表示 | 提示内容 | goldの扱い |
| --- | --- | --- | --- |
| V0 | Node/Edgeをテキストで列挙 | Declared Graph、質問、対象scope、graph revision | 証拠がない実行主張は`undetermined` |
| V1 | 同じNode/EdgeのMermaid図 | V0と論理的に等価なDecl. Graph | V0と同じGold。図の表示だけの増分 |
| V2 | V0形式＋解決/観測/読取りの根拠 | Declared＋Resolved＋Observed＋Consumer | 検査可能な差分をGoldとして判定 |
| V3 | V1形式＋V2と**同じ文言の追加根拠** | Graph＋Resolved＋Observed＋Consumer | V2と同じGold。図の付加価値を比較 |

声明の正しさは**何が提示されたか**にも依存する。宣言のみでは結論を出せないケースでV0/V1が`undetermined`を返すことは正答であり、被験者を「推理して当てたか」で評価しない。B-D01/F-D01のように宣言だけで解決可能な正常例も入れ、常に保留するモデル・人間を高評価にしない。

Graphの描画エンジンが異なる場合、矢印・分岐・表示テキスト・a11y・順序が変わり得る。**実験時にレンダラーと版・画像を固定**し、文字列同一だけではUI/視認性の等価性を主張しない。Mermaid本文は宣言表現の一例であり、TEI Studioの実Graph UIではない。

## 2. 観測範囲の意味：「不在」の四つの区別

| 言い方 | 実験の意味 | 誤った昇格 |
| --- | --- | --- |
| `undeclared` | 当該Graph/版にNode/Edgeの宣言がない | 実行されなかった、存在しない |
| `unobserved` | 収集されたTrace内でEventを見つけなかった | 実行されなかった |
| `confirmed absent within B` | 閉じた対象集合・時間窓・失イベントのない観測が別途成立し、その境界でEventが無かった | 境界外の実世界全体でも存在しない |
| `unknown` | Observer不完全、scope外、必要なConsumer/Provider確認不足 | 失敗または成功を勝手に確定 |

合成fixtureの`observer_coverage=closed-for-specified-steps`は、**閉じた観測を仮定した問題文**であり、実際のMonitorが全工程を網羅した証明ではない。TEIのP0-A0/A1やReal Providerの資格と混同しない。Closedであっても、その保証は記録にあるscopeとEvent種類に限定する。

## 3. 公開合成セット10件のGold（実測なし）

| Case | 問い | 宣言だけ（V0/V1） | 追加根拠あり（V2/V3） | 評価の要点 |
| --- | --- | --- | --- | --- |
| B-P01 | 選択したBuild branchのrequired実行 | 未定 | **支持** | Optional testの合法skipを許す |
| B-N01 | 未宣言工程がないか | 未定 | **反証** | Hookが観測された |
| B-N02 | 実消費Sourceが一致したか | 未定 | **反証** | s1宣言・s2実消費 |
| B-N03 | required工程を全部実行したか | 未定 | **未定** | 監視不完全、Package未観測 |
| B-D01 | 宣言GraphにSource→Package経路があるか | **支持** | **支持** | 実行と関係なく宣言だけで答えられる |
| F-P01 | Consumerが同世代の2 memberを読んだか | 未定 | **支持** | Read両memberがg1 |
| F-N01 | Consumerが同世代の2 memberを読んだか | 未定 | **反証** | Detailがg2、Controlがg1 |
| F-N02 | Consumerが同世代の2 memberを読んだか | 未定 | **未定** | Transfer ACKのみ、read観測不足 |
| F-D01 | 宣言GraphでTransfer→Read順か | **支持** | **支持** | 物理受領・取込完了ではない |
| X-N01 | 境界外Providerが呼ばれていないか | 未定 | **未定** | Local Observerの外部を結論づけられない |

上表・Gold JSONは**公開開発用の正解**。これらのケースを見て設計・調整した同じモデル/Agentを「未知のテストへの一般化」と呼ばない。独立holdoutは、製品側Ownerまたは研究者以外の評価者が**未公開の変種**を実行前に作り、Goldを隔離管理する必要がある。実PIIや業務原本を使わない。

## 4. 再現する操作と採点

### 公開fixtureの構造確認・刺激表示（予定コマンド）

`python3 research/tools/rq7_pilot.py --check`

`python3 research/tools/rq7_pilot.py --case B-P01 --arm V0`

`python3 research/tools/rq7_pilot.py --case B-P01 --arm V3`

`--check`はJSONのschema/公開fixture宣言、case ID一致、Graph edgeのdangling、required/skippedの矛盾、4条件のGoldの同一情報量条件、非公開データ混入フラグ等を点検する。**これはProduct側の正しさ・Observer completeness・学術仮説の証明ではない。** Product CIへ必須Gateとして配線する必要はない。

初回実験で保存する`run record`: `study_version`、`case_id`、`arm`、`stimulus_hash`、`gold_hash`（研究採点者のみ）、`rendered_byte_hash`、`renderer_version`、`source_commit`、`presentation_order`、`participant_class`（human/AI別）、`model+temperature+prompt+tool_policy`、`time_budget`、`answer`、`reason`、`referenced_nodes/events`、`next_check`、`elapsed`、`tokens`、`manual_actions`、`reviewer_id`、`status`（NOT RUN/BLOCKED/RUN/INELIGIBLE）、`scope_coverage`、`disclosure_profile`。

Gold判定者と表示を作る者を可能なら分ける。少なくとも最初の採点基準を**観測前**に固定し、失敗後に都合よく変更しない。Open Gold上のサンプルだけでモデルの性能を比較する場合は「公開fixture pilot」と明記する。

### 主たる採点（初回候補）

1. **Verdict**（0/1）：適切な`supported/refuted/undetermined`。不確かな対象を拒否・許可の二値に潰さない。
2. **Grounding**（0/1）：対象Graph/Scope/版、理由と必要な追加観測を提示したか。定義のみでの支持なのか実読取りでの支持なのか区別する。
3. **False completeness**（0/1）：観測範囲が閉じていないのに「存在しない」「すべて実行済み」と回答したか。誤主張を検出したケースの数だけでなく誤主張数も記録する。
4. **False block**（0/1）：B-P01の合法skipや、Declだけで支持可能なB-D01/F-D01を過剰に拒否／永久保留したか。
5. **Burden**：時間、追加資料の要求数、ツール/Token、レビュー工数を**品質と別指標**で測定。誤回答を速く出しても「生産性改善」としない。

主解析は2×2の**表示形式の効果・追加証拠の効果・交互作用**。同一被験者が複数caseを解くときはcase/被験者ごとの相関と学習効果を扱う。データが少ない間は記述統計と個別case差だけを示し、P値や一般化を主張しない。

### 実際の評価に使う際の統制

- TaskとGoldを固定した上で、V0/V1間・V2/V3間で**表示の情報内容が等価**かを独立レビューする。Render確認なしに比較結果を採用しない。
- 同じ被験者に同じcaseを4回見せるとGoldの学習が起こる。初回は被験者/モデルの独立Sessionでの割当や異なる同等caseへの分配を検討し、学習・Prompt修正を記録する。
- 端末・文字サイズ・描画可能な幅、a11y、色、レンダリング性能、Graph理解の経験、AIの図理解方式を別記する。Mermaidをコードとして入力したAIと実画像を見た人間を同じ「図表条件」に集約しない。
- 合成ケースを作成した担当者と独立Holdout評価者を同一にしない。Gold公開後に調整したPromptで公開fixtureを解くことは探索であり、holdoutの結果ではない。
- 実Property「未宣言工程が発生しなかった」を証明する場合は、テスト用Observerを置いたこと・対象scopeが完全なことの**外部証拠**を要求する。観測欠落の反例はTEI #2831側で独立に用意する。
- 低権限表示に秘密のProvider/Pluginの名前・件数・有無を漏らさない。公開版は架空文字列のみ。実TEI #2515とTAI #232に開示の本番保証は残す。

## 5. 各Ownerへの反映の境界

| 所有者 | 反映可能な成果 | 反映しない内容 |
| --- | --- | --- |
| [TEI #2831](https://github.com/hat47x/tei-platform/issues/2831) | 監視不完全と合法skipの誤断定を分けるGold/表示要件の候補 | 新Runtime、第二Graph検査器、実Build成功の代替 |
| [TEI #2542](https://github.com/hat47x/tei-platform/issues/2542) | Manifest世代とTransfer ACK/Readの区別を認知タスクとして評価 | Transfer Provider/MFT/DBの実効果 |
| [TEI #2018](https://github.com/hat47x/tei-platform/issues/2018) | 変更検証における人間/AIの確認工数の測定定義の比較 | TEI固有Benchmarkの正本・事前Goldの改変 |
| [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) | 実Harness比較へ将来持ち込む表示条件・H2/H3との境界 | W0実CLI結果をAIによる図解読成功と読み替える |
| [TAI RQ6](../COGNITIVE_GENERATION_AND_EVIDENCE_2026-11-02.md) | 候補探索と検証の分離へ「何が見えているか」の追加共変量 | CSW Methodや人的価値の採用済み宣言 |

最初に可視化・回答タスクの負例が安定しない場合は、Graphツールを作らずテキストと既存receiptを用いる。研究上の「完全性」は開示・観測・対象scopeを欠かした一般的な不存在証明ではない。**RQ7の実被験者・実モデル・実Product・独立Holdoutの結果はすべてNOT RUN**。
