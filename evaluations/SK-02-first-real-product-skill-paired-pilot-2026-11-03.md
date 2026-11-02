# SK-02：最初の実Product Skill増分を測る盲検ペア試験（2026-11-03）

**位置付け**：TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168) Harness-first／[Draft #270](https://github.com/hat47x/tai-pleroma/pull/270) SK-01 H2/H3の**実行可能な試行票**。現状は試行の事前設計（PRE-REGISTERED CANDIDATE）、実Harnessの本票に従う試行は**NOT RUN**。新しいRunner、Skill Host、Common Registry、実効Policy、第二Oracleは作らない。

## 1. なぜこの小試行を先行するか

これまでの公開合成 SK-MIN / SK-HP / SK-N / SK-C / SK-RQ等は反例の判定基準に役立つが、**Skillを実Harnessへロードして利用者のタスクが改善したか**は測定していない。TEI [#2626](https://github.com/hat47x/tei-platform/pull/2626)は**merged**（merge commit `00eb8e148daadbc2cf40145d8e8473d56531514c`）で、固定した公開参照Worldから実Go CLIのread-only 9プロセス・診断・Source Index/Traceと二表示素材の同Job再読取を限定観測している。これは実CLIの出発点にはなるが、Skillは使用していない。TEI [Draft #2607](https://github.com/hat47x/tei-platform/pull/2607)の`skills/yi-tei-modeling/SKILL.md`と`verify_skill.py`は**未mergeのProduct側Skill候補**であり、検査器の静的整合と実Harness loadは別。

**実験の問い**：「同一実Tool・同一Source・同一Harness・同じ閲覧/開示資格で、TEI Product Skillの実投入が、正しい対象選択・元Source引用・Warning/Unknown保持・架空操作抑止・調査負担に差を生むか」。TAI横断Skillはこの試行には**入れない**。H4/H5は後続別実験。

## 2. 固定する入力と独立の判定

試験登録時に一つの`trial_group_id`を付与。以下は**値を実試行直前に採取する列であり、空のままで合格とはしない**。

| 項目 | 固定すべき内容・採取元 |
| --- | --- |
| Product | `tei-platform`のcheckout exact commit、clean/dirty、変更file、OS/Go/toolchain、build ID、実行CLI binaryのSHA-256 |
| Source | `reference/workspace`など明示した公開Fixtureの全対象bytes/digest、WorldFP、SourceIndexFP、Source revision、Workspace path／Source locator |
| Task / Prompt | 同じ日本語依頼原文のSHA-256、狙うSubject・元Source・Validationの報告要求、開示可否、停止条件 |
| Tool | 同じCLI binary/path/cwd、実argv/exit/stdout/stderr/diagnostics（必要時stdout bytesのdigest）、選抜`commands` Catalogのscope |
| Harness | Harness/モデルbuild・Profile・利用可能Tool・そのSessionの権限。Claude Code／Codex／OpenCode等は**実可用性を確認してから**選択 |
| Skill | H3にのみProduct Skill packageを配置。root + 実ロードしたreferences/scriptsのdigestを区別。H2にSkill byte/期待解答を混入させない |
| Oracle | **別担当**が実Product観測とTask要求から準備した、Skill/Preamble/Promptへ渡さない期待（Subject ID/Source/Warning/Unknown）、採点規則と保存先 |
| Cost | ツールの実呼出数、経過時間、モデルtoken/費用（Providerが返すものと推定値を区別）、人手確認回数。比較できない値はunknown |

**Source移動は別task group**にする。#2626のW0cではSource byteとWorldFPが同じでもSourceIndexFP/Traceの外側Token/引用pathが変化した。「同じWorldFPだからペアのSource条件が同じ」と見なさない。移動前後のSource IDと引用位置を同一Runの測定値に偽装しない。

## 3. 実施の最小四試行（順序交絡を抑える）

1. 実Harnessで**新規独立Session**を4つ用意する。片方の腕を実行してから、その会話をもう一方へ引き継がない。
2. 第一ペア：H2（**Tool-only**）→H3（**同一Tool + Product Skill**）。第二ペア：H3→H2。Source/Prompt/Tool/Permissions/Model Profileを一致させ、実試行順を記録する。別Harnessでは別Groupで行う。
3. H3のSkill投入経路を二つに分けて報告する：**明示指定（forced）**での実Load試行と、**自然言語による自動発見（auto）**。一方のPASSをもう一方に適用しない。最小四試行はまずforcedで行ってよい。
4. 各SessionでTool呼出しを外部から観測できる範囲で記録する。Skillを参照したというAIの自己申告は「loaded observed」ではない。実ロードbyteが取れないHarnessは`loaded=unknown`とし、当該Qualificationは未成立のままTask品質のみ比較可能。
5. 回答から独立にProduct CLIの実出力を照合する。Subjectの型付きID、Source locator、World/SourceIndexFP、Trace外側Token、Warning/Error/Unknown、Source改版時の変化を別欄。Exit0だけでWarning無しやOwner意味受理と呼ばない。
6. 外部LLMへ送信するTool結果は**公開・合成データで、当該Harnessへの開示が許可された範囲だけ**。Raw/秘密の非公開Tool名／Internal Oracleを送らない。OS/Network強制資格は[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)・TEI #2515の独立試験へ返す。

H2とH3の実験条件差はSkillの配置・読み取りに必要な追加Contextだけを主な変数とする。ToolのSchema、Agentが選べるモデル/性能枠、独立Oracleの提供、追加的な権限・インターネット探索などをH3だけに付与しない。SkillのToken負担は隠さず**総費用**として含める。自然言語モデルの非決定性を考慮し、4試行だけで一般化せず次回反復の必要性を明記する。

## 4. 一試行のEvidence票（テンプレート。実観測値は空欄）

| 観測列 | 値の記入位置 |
| --- | --- |
| `trial_group_id / task_id / arm / order / session_id` | 未採取 |
| `harness / model / profile / OS / principal / tool availability` | 未採取 |
| `repo exact HEAD / worktree / CLI binary digest / actual argv / exit` | 未採取 |
| `workspace Source bytes / WorldFP / SourceIndexFP / expected Trace token` | 未採取 |
| `skill repo/head / package digest / loaded root/refs/scripts / observation method` | 未採取。H2ではnot-applicable |
| `prompt bytes/digest / disclosure audience / raw sent-to endpoint / actual egress if observable` | 未採取 |
| `observed Tool calls / responses / warning / diagnostics / incomplete` | 未採取 |
| `answer subject kind+id / source locator / any unsupported commands / admitted unknown` | 未採取 |
| `oracle provenance (held separately) / scorer identity / errors / time/token/cost/human review` | 未採取 |
| `eligibility / correctness / qualitative outcome / product authority / NOT RUN` | 本文の設計だけでは未資格 |

**比較適格性（eligibility）と正答（correctness）を別列**にする。H3がSkillを実ロードできず条件差が無いなら、Skillの効果は**比較不能**であって改善ゼロではない。H3だけに正答例が与えられれば比較対象から除外する。Sourceが変化した試行・Harness Tool/Grant差・失われたLogは明示してペアを分離する。

## 5. 最小採点規則・中断条件

正答条件はTaskに対してProduct側が独立照合した`subject kind/id`、Source locator/版、必要なDiagnostic WarningとUnknownの保持、Toolを本当に使ったときの正確な実Call。**無許可のwrite/`artifacts -out`・存在しないMCP/CLI・内部情報送出・架空の完了主張**を別種の重大誤りとして記録する。選抜`commands` Catalogにない`operations/artifacts`が本体に実装されていても、H2/H3の当初のread-only Taskはそれを使わない。

測るのは、(a)比較可能な試行数／成功数、(b)Wrong Subject/Source/Warning/Unknown/False Tool Claimの数、(c)Tool/Token/費用/人間Review、(d)余分なSkill/製品選択、(e)許可範囲外への提案/実送出と未観測面。**誤成功のある「高速化」は改善に数えない**。

Skill実ロード・独立Oracle・実Tool出力が揃わなければ、H2/H3 Skill増分の正式なPassとしない。公開Expected付き合成fixtureやTEI #2626の同Job再読取だけから「H3成功」としない。必要なら一製品だけでタスクを終え、TAIや別Productを追加することを評価上の必須としない。

## 6. 成果の還流と状態

- **TEI #2605 / Draft #2607**：Skill文書・refs/scripts・CLIの実版/診断・Source忠実性の修正先。ToolやRoleのAPI、正式意味受理はTEI Product Owner。
- **TAI Draft #270 / SK-01 H2/H3**：ペア実験の独立変数・別Harnessでの再現/非対応・コスト比較と公開資格。今回のSK-02は既存SK-01の**初回実行票**であり重複する独立Gateではない。
- **TAI #271 / #74**：変更後の適格性とSkill依存closure、配布済みArtifact/実Load/現在Grantを別記。初回測定が成立してから多Harness・2 Product/Consumerへ段階拡張。
- **TEI #2018**：モデル/Skill/横断/手書きの生産性比較では、品質条件を同じにした総費用の観測へ再利用。

**現在の実験結果：四試行は未着手（NOT RUN）。** 本票の作成はProduct Skillの導入・Harness操作・Owner受理ではない。#2626 mergedの限定CI観測と#2607 Draftの静的Checkerは別の既存Evidenceであり、SK-02の実測値として加算しない。
