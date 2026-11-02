# YI Constellation：Capability由来のSkill Projection（2026-11-02）

状態：**構成・評価の提案。正式採用／実Product・Harnessでの動作はNOT RUN**。

## 設計の焦点

TEI [#2620](https://github.com/hat47x/tei-platform/issues/2620)は、標準データ構造への意味Role/Operator適用と、製品Pluginの実際のSchemaを基にしたAI向けSkillの生成・版固定を検討している。[#2621](https://github.com/hat47x/tei-platform/issues/2621)はMarkdown Authoring、[#2622](https://github.com/hat47x/tei-platform/issues/2622)はData Operations、[#988](https://github.com/hat47x/tei-platform/issues/988)はDSL/Operatorの意味契約を所有する。TEI [Draft #2625](https://github.com/hat47x/tei-platform/pull/2625)の限定合成Referenceでは、複数の表層構文から同じ標準データを得る可能性を検討している。実製品統合と意味受理は別。

この動きから、**Product Skillの技術的説明は実Product Contract/CLIから参照・投影し、使い方や専門Methodの手順は各Product側で執筆できる構造**を提案する。Skillの文面を製品意味と権限の第二正本にしない。

## 責務を五層に分ける

| 層 | Ownerと入力 | Skill側の使い方 |
| --- | --- | --- |
| Source/Syntax | 各Productの編集Source、Markdown/DSL等の表層と版 | Source位置と同一性を参照 |
| Role/Meaning | Productの解決済みRole・Operator版・受理された意味 | どの操作が何を意味するかを参照 |
| Capability/Tool | Productの契約・実CLI/API/MCP、バージョン/対象Host | 現物の入出力・失敗と対応を照合 |
| Skill/Method | 各Product repoで所有するSkillと専門手順 | 目的、操作順、根拠、未決、利用先を案内 |
| Harness/Activity | 外部Harness、TAI横断Skill、必要な配布Adapter | 利用可能な製品だけを選び、活動を引継ぎ |

**実行権限・外部送信可否・Provider効果**はProduct/Host側の現時点の判断として別に観測する。MCPのTool一覧やSkillの読み込みを、操作資格や業務完了の根拠としない。

## Capability-derived Referenceと手書きRecipe

- **Capability-derived Reference**：製品が公開を許した意味ID、契約版、実Tool名・引数、対象/Scope/失敗、未対応事項、検証済み範囲、Sourceへの参照。まず[TEI #2605](https://github.com/hat47x/tei-platform/issues/2605)/[Draft #2607](https://github.com/hat47x/tei-platform/pull/2607)のread-only操作で、実CLIとSkill記述の一致を照合する。
- **Task/Method Recipe**：利用者の目的の把握、必要時の追加調査、注意事項、他製品への引継ぎ。SEI Method、SUI探索、SHO制作、EKI委任はそれぞれの製品で育てる。
- **TAIの組合せ**：利用者の目標に応じ、直接Product Skillを使うか、TAIの横断Skillで組み合わせるかを選ぶ。TAIはProduct内のMeaning/Provider/Methodを複製しない。

### 複数表層構文の扱い

Markdown表、式、チェーン、Graphviz等が同じRole/Operator/型/対象と版へ解決できる範囲では、**別々の表層形式に実行能力Skillを一対一で増殖させず、意味Roleと実Tool能力に紐づける**。表示が似ていても、評価順・単位・NULL・Bag/Grain・Source Scopeの条件が異なる場合は同一能力として束ねない。文書中の例や未解決のRoleは候補であり、正式なFunctionや実行権限ではない。

### 更新時の区別

| 変更 | 再確認すべき事項 |
| --- | --- |
| 表層構文・書式のみ | Source箇所とRole/Meaningの同値性、SHO文書の表示・引用 |
| Role/Operator/契約版 | Skillの入出力説明、独立検証、適用対象と受理条件 |
| CLI/MCP/実行物 | 現物のTool契約、Skill手順、実環境の互換・権限 |
| 参照資料・Script | Skill依存ファイルを含む配布版、実際の読み込み・実行 |
| Provider/Context | 対象・版・取得範囲・完全性・情報開示、別Providerでの適合 |
| 公開範囲 | 外部Harnessへ見せるSkillや機能一覧。秘密の名称・件数の開示も検査 |

各Productの機能追加がSkill文面へ反映されない**ドリフト**と、古いSkillだけが残る場合の誤呼出しを比較対象とする。Source変更がSkillに影響するかは追跡可能な依存に限定し、未確認を無影響と決めない。

## SK-D評価案（すべてNOT RUN）

| Case | 観測したい差 |
| --- | --- |
| SK-D01 | TEI実CLIの契約記述とSkillの説明の一致 |
| SK-D02 | 同じ意味に解決する異なるMarkdown/DSL表現のSkill選択 |
| SK-D03 | 未確定Roleや説明用の表が操作可能機能として扱われないこと |
| SK-D04 | CLI仕様改版後の古いSkillのドリフト検出 |
| SK-D05 | Skill本体が同じでも参照資料やScriptが変わった時の配布差 |
| SK-D06 | 非公開Capabilityのみ異なる二世界で外部へ出す一覧が一致すること |
| SK-D07 | 同じSubjectに異なるProvider/Mappingがある時の候補保持 |
| SK-D08 | Tool一覧と実Host権限・外部送出の独立確認 |
| SK-D09 | Product単独SkillとTAI横断Skillの追加価値の比較 |
| SK-D10 | Skill更新とSHO文書・TAI活動再開・別Harness移植の影響 |

最初の比較は**TEIの既存read-only CLIとSkillなし／あり**のH2/H3を優先する。別製品ではSHO/MMIの実在Skillを検証候補にできる。能力説明の自動投影が手作業の維持負担と誤案内をどの程度減らすかを測ってから、共通生成規約を検討する。

## Owner境界と未実施範囲

Product契約・Role/Operator・ToolとProduct Skillは各Productが所有する。TAIは比較・横断選択・用途別束の版固定、[TAI #74](https://github.com/hat47x/tai-pleroma/issues/74)はシリーズ配布、[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)は製品横断の情報境界を担当する。新しい共通Host/Registry/第二の意味正本は前提にしない。

**状態：本書は計画のみ。Capability-to-Skill生成器、実CLI/Skill/複数Harness、実送信/認可、独立評価、正式Owner受理はNOT RUN。**


## 2026-11-02：最初の製品資産との静的照合

TEI main `9c9ef4d160640908e06ad13afb6c2b45c664c748` の [`cmd/tei/cli_contract.go`](https://github.com/hat47x/tei-platform/blob/9c9ef4d160640908e06ad13afb6c2b45c664c748/cmd/tei/cli_contract.go) を読み取り、Catalog `tei.cli.discovery/v0` のScopeが**`selected-read-only-commands`**であることを確認した。TEI [Draft #2607](https://github.com/hat47x/tei-platform/pull/2607)の `skills/yi-tei-modeling/SKILL.md`（Git blob `9cd8475bd6489c6661ae644bf771cfcce04188b1`）と詳細Reference（blob `ec2f90e85ed42659aca8b44a9be216987860b099`）には、`commands`、`model catalog`、`inspect`、`trace`、`validate -json`への手順が既にあり、CLI Catalogから読める選択項目を扱う設計であることを静的に照合した。

これが確認するのは、**read-only Tool名とSkill文章の対応候補**である。現行環境でそのToolが実行できること、CLIの全Plugin能力、Source/Modelの同一Snapshot、非公開データの送出資格、意味受理、外部Host作用の保証にはならない。ここを最初のH2/H3の実験基準点とし、機械由来説明の自動生成は**追加価値が確認された後の比較候補**に置く。



## 2026-11-02 証拠の更新：CLI実行とSkill利用を分けて扱う

初版の「実CLI NOT RUN」は、**TAIが直接実行した試験およびSkill利用に関する旧記述**である。TEI [Draft #2626](https://github.com/hat47x/tei-platform/pull/2626)では、[Focused CI #41456256348](https://github.com/hat47x/tei-platform/actions/runs/41456256348)の**2 Job success**を確認しており、HEAD `31c62e8bb44c1c5c59933a46924aa4c338637085`の実Go read-only CLIが9プロセスで限定Readを行い、同じRead witnessから人間MarkdownとAI JSONを作り**当該Job内で再読取した**。この実Product観測はCapability-derived Referenceの必要な基礎証拠となる。ただし**TEI Product Skillの実インストール・実ロード／H2-H3差／独立SHO Writer-Reader／外部Harness/OS公開資格は未確認**である。

新しい[Role Bootstrap合成Draft #2638](https://github.com/hat47x/tei-platform/pull/2638)では、Role/Interpreterの**Eager依存の版・実装内容の推移閉包**が未Pinなら、Root Role名/Version一致だけで解釈資格を導けない。逆にデータ構造の通常の遅延再帰Refは必ずしも不正なInterpreter起動循環ではない。Skill投影では、`Capability ID + declared version`だけでなく、Product Ownerが提供可能な範囲の**選択済み実装と必要依存・Source/Operator**を参照し、Lockの実閉包が不明な場合は「説明済み候補」「現在実行可能」を区別する。非公開依存名を外部のCatalogやErrorに漏らす必要はない。

[既存Go Language Pluginへの試験Draft #2639](https://github.com/hat47x/tei-platform/pull/2639)の二表層→Plain Data候補は、同じ形式の候補であっても受理済みMeaningやSource occurrenceの一致を主張しない。Script/Roleの能力を説明するSkillは、同じ表層の例示文を**真の受理済み操作の列挙**と扱わない。正式TEI DSL/Pluginの採用やAIによる構文理解成功も、別に測る。

Test-as-DataはTEI [#2621](https://github.com/hat47x/tei-platform/issues/2621#issuecomment-6578796587)と[#2514](https://github.com/hat47x/tei-platform/issues/2514)が独立Expected・Mutation・Source/改版を受け持つ。Skillに含まれるHow-toや公開Fixtureが利用者へ期待答を提示しても、Agentに同じExpectedを与えた結果を**独立・盲検のProduct正答率**として計測しない。[TAI SK-01 §W](../../evaluations/SK-01-harness-skills.md)のSK-IQ01〜12に引き渡す。

