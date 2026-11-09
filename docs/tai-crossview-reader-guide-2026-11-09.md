# TAI全体像の横断読解ガイド v0 — 課題から製品選択・証拠・結果まで

状態: **Draft / 読者向けの解釈・検査案 / Owner未受理 / 本書固有の検証NOT RUN**（2026-11-09）。
照合したTAI main: `0b5115a629863d57566b8db36a6d67bc21727039`。他Productの現行main全件照合、実Harness再実行、実業務の結果観測を実施したという意味ではない。

## 1. この文書の位置

[Product Landscape](product-landscape.md)は「誰が何を担うか」、[View Contract](product-landscape-view-contract.md)は「役割の線と実接続の線を混同しない条件」、[知識モデル](product-knowledge-model.md)は「型・根拠・判断・版」、[配布設計](product-family-delivery.md)は「固定されたProduct Artifactの組合せ」を説明する。

**本書だけが追加する問い**は「一つの利用目的から始めて、これらの別々の説明をどの順に読み、何がまだ言えないかを判断するか」である。新しいViewpoint、Product Registry、canonical Activity Store、共通Contract、Host、Runtime、Owner、受入Gateを導入しない。現行文書に存在するV1〜V5と各Issueへ接続する**読者用の横断ナビゲーション**である。

**中心命題（検証対象）**: YI Constellationの増分価値は、全部のProductを常に動かすことではなく、主体が目的に応じて独立能力を選択・交換・省略でき、解釈・判断・実行・結果の区別を失わずに活動を継続できることにある。これは価値仮説であり実利用者の価値受理ではない。

## 2. 「全体」を一つの図へ押し込まない

| 読者の問い | 既存の閲覧先 | 正本・意思決定の所在 | その資料からは言えないこと |
| --- | --- | --- | --- |
| **何があり、何が独立か** | [Product Landscape](product-landscape.md) V1、[対象棚卸し](product-inventory-candidates.md) | 各Productの固有説明。横断の対象・分類は[TAI #73](https://github.com/hat47x/tai-pleroma/issues/73)で未決 | 公開Repo一覧＝全製品、役割の破線＝API接続 |
| **必要な能力を誰が提供するか** | [View Contract](product-landscape-view-contract.md) V2、[接続調査](../integrations/capability-inventory.md) | CapabilityとContractの詳細は各Provider/Product | 同名Skill/Tool＝実Load済み、互換、呼出資格 |
| **どの条件で利用・観測したか** | V3、[status](status.md)、[SCN-001](../scenarios/SCN-001-shared-space-guidance.md) | 実Source・Consumer・Effect・Meaningは各Owner/Host | 合成PASS＝現実の業務受入、Task受付＝実Effect |
| **どう構成を届けるか** | [配布設計](product-family-delivery.md)、[TAI #74](https://github.com/hat47x/tai-pleroma/issues/74) | 各Productの単体Release、TAIの構成別Release案、YIサイトの公開判断は別 | Bundleの版固定＝現在のProvider/Grant/Use-time適格 |
| **変更後も何を使えるか** | V4/V5（後段）、[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271) | 依存・Evidenceの適用範囲を照合し、各Productが必要な再資格化を実行 | 旧PASSの全用途継承、unknown辺＝無関係 |
| **本人にどんな結果・価値が生まれたか** | [価値研究](yi-constellation/value-needs-requirements-2026-11-01.md)、[評価計画](yi-constellation/value-realization-research-protocol-2026-11-01.md)、[TAI #127](https://github.com/hat47x/tai-pleroma/issues/127) | 本人・影響者の評価、正当なOwnerの採否、実世界のProvider記録 | 正答・納品・Tool成功＝本人の満足、QoL、社会の同意 |

特に **YI Constellation＝ブランド／サイト名**、**TAI Pleroma＝横断する独立Product**、**TAIリポジトリ＝横断索引と構成別配布の作業拠点**は異なる。同じリポジトリで文書を管理することは、TAIが各ProductのRuntime・Source・意味・権限を所有することを意味しない。

`SUI / SEI / TEI / SHO（MMIとの同一性は未決）/ EKI` は初期の五つの関連基盤であり、CSWは探索Method/Skill等の分類候補、TEI StudioはTEIに関係する開発・表示領域の候補である。これらを自動的に第六・第七の正式基盤、または独立Productと確定しない。

## 3. 活動を読む順路（概念上の依存ではなく、問いの順序）

```mermaid
flowchart TB
  V["本人・関係者の目的／望むこと／望まないこと"] --> Q["何を調べ・判断・実現する必要があるか"]
  Q --> C["必要な能力・Productを選ぶ（不要なら使わない）"]
  C --> P["実行する場合、現在のSource／Scope／Tool／権限／開示を確認"]
  P --> W["適切なProduct／既存Harness／手作業で進める"]
  W --> O["結果・根拠・未決を独立に観測"]
  O --> R["本人・Ownerによる価値評価と再検討"]
  R -. "意図や条件が変われば" .-> Q
```

*これは実装済みのWorkflow、強制順序、中央Orchestrator、サービス間の通信図ではない。各段の内部処理も省略された概念図であり、TEIの「有効Pipelineの完全表示」と同じ不存在判断には利用できない。*

- **選択の自由**: 外部Harness＋通常ファイル／Markdown／CLIだけで十分なら、追加のTAI横断SkillやProduct利用を義務化しない。独立したProductの単体利用も維持する（[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)、[#422](https://github.com/hat47x/tai-pleroma/issues/422)）。
- **認知の境界**: SHO/MMIの出典、SUIの仮説、SEIのDecision/未決、TEIのモデル・実現、EKIの委任・Effectを一つの`success`へまとめない。CSWは探索の豊かさを増す候補であり、正式受理を代行しない。
- **実行の境界**: 外部Harnessは推論・Tool呼出し等を担い得るが、現在の開示、対象への作用、独立観測は各Product/Host/Providerに従う。`read-only`の説明だけではRawの隔離・送出制御を証明できない（[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)）。
- **時点の境界**: 固定Releaseの再現性と、現在ActivityでのSource/Grant/Provider/Consumer適格性は別（[TAI #74](https://github.com/hat47x/tai-pleroma/issues/74)、[#271](https://github.com/hat47x/tai-pleroma/issues/271)）。
- **成果の境界**: Artifact生成、受領、独立Read/Effect、本人が目的を達したか、第三者に負担を生んだかは別の問い。技術的な結果から人間の価値を自動推論しない。

## 4. SCN-001で「同じ活動」を三つの別の図として読む

題材は架空の施設案内「予約不要」と「会議室は事前予約」の解釈である。合成fixtureと参照接続を使う例であって、実施設の規程、公開許可、全Productの実API互換は未確認。

| 図の種類 | この事例で追うもの | 観測／保留の境界 |
| --- | --- | --- |
| **役割図（V1）** | 原資料をSHO/MMI、異なる解釈をSUI、判断の由来をSEI、規則候補の検査をTEI、必要なら委任をEKI、活動全体の索引をTAIとして説明 | 全Productが必須、製品間が直接接続という意味ではない |
| **接続・証拠図（V3）** | どの固定fixture・API/CLI・出力のどの範囲が実際に読まれ、照合されたか。根拠は[status](status.md)、[接続調査](../integrations/capability-inventory.md) | MMI/SEI/TEI/SUIの限定観測、合成Decision、EKIの`queued`は実業務のEffectやOwner受理ではない |
| **受入・結果図** | 人が例外規則を確かめ、変更案を受け入れ、公表し、利用者への結果を観測したか | [R-01〜R-07](../evaluations/SCN-001-real-object-review.md)の実物受入・公開判断と利用者への効果は別。現在の合成記録から完了を断定しない |

同じデータや名前を表示する場合でも、図ごとに凡例・対象版・実施状態・未実証を付ける。ある図の矢印から他図の「契約」「権限」「効果」を生成しない。

### 読者が試せる質問

1. **TEIをこのケースから外したら何が変わるか？** 必要な規則の意味検査が失われる条件を示せるか。単なる案内文の比較で価値差が無ければ利用を強制しない。
2. **EKIで`queued`となったら何が言えるか？** Taskが受付段階にあることに限り、実作業完了と答えない。
3. **案内文がA→B→Aと元に戻れば、過去の判断を復活できるか？** 文言一致で現在のOwner受理・Authorityを復活させない（[TAI #33](https://github.com/hat47x/tai-pleroma/issues/33)）。
4. **文書・Sourceが新しい版になったら、過去のどの証拠を残すか？** 旧証拠は歴史として保持し、現行利用の資格は影響範囲を検討して再確認する（[#271](https://github.com/hat47x/tai-pleroma/issues/271)）。
5. **外部Harnessを別のものへ替えたら何を再確認するか？** 実Skill Load、Tool到達、Source/Disclosure/Grant、同一Attemptの結果と実Consumerを区別する。実H3 Loadの限定証拠があっても、H2/H3の比較適格は未成立とする（[#168](https://github.com/hat47x/tai-pleroma/issues/168)）。
6. **利用者が「使わない」「延期する」を選んだら失敗か？** 目的と正当な本人意思に照らす。Task完了率だけで価値を評価しない（[#127](https://github.com/hat47x/tai-pleroma/issues/127)、[#422](https://github.com/hat47x/tai-pleroma/issues/422)）。

## 5. G1の読者検査から実証へ進む最小順序（提案）

| 段階 | 最小成果 | 失敗・保留の条件 | 既存Owner |
| --- | --- | --- | --- |
| **A. G1読者確認** | 五基盤＋TAIの役割と、未分類（SHO/MMI・CSW・TEI Studio）・対象外/未調査を言い分けられる | 図の破線を実APIと読む、非公開対象の存在を漏らす、候補を正式製品にする | [#73](https://github.com/hat47x/tai-pleroma/issues/73) |
| **B. 価値のベースライン** | 同じSCN-001等をMarkdown/既存Harness/手作業でも行い、TAI連携の増分・負担を対照する | 製品数・機能数・合成PASSを価値の代理指標とする | [#127](https://github.com/hat47x/tai-pleroma/issues/127)、[#422](https://github.com/hat47x/tai-pleroma/issues/422) |
| **C. 必要時の実Product/Harness証拠** | 実Source read、実Tool/Skill load、利用Consumer、結果を別々に確認する | 不適格な隔離、試験間のSource差、独立Expected不足、実Effect未観測 | [#168](https://github.com/hat47x/tai-pleroma/issues/168)、[#271](https://github.com/hat47x/tai-pleroma/issues/271)、各Product |
| **D. 配布と使用を別判定** | 固定Product/Skill/Adapter構成と、その用途での現在資格を別に報告 | Release PASSを現在権限や文書ClaimのPASSへコピー | [#74](https://github.com/hat47x/tai-pleroma/issues/74)、各Product |
| **E. 人の受理と価値評価** | 対象のOwner受理、実際の結果、本人/影響者の評価 | 自動試験の成功だけで社会的同意・業務公開の許可を宣言 | [#127](https://github.com/hat47x/tai-pleroma/issues/127)、既存の実物レビュー |

**本書では読者試験、H2/H3比較、実Owner受理、実顧客/個人の価値調査、製品横断E2E、シリーズReleaseを実施していない。** #73のG1、#74の配布、#168のHarness、#271の再資格化、#422の価値適正化の完了条件を一つの新しい合否に統合しない。

## 6. 更新規則と反証可能性

- 読者が必要とする問いを示せない項目は、製品・エッジ・共通スキーマを増やす根拠にならない。
- 他Productの仕様や結果は固定Revisionと出典に戻る。TAI側に技術・意味・実行権限の第二正本を設けない。
- 旧Snapshotの記述と最新Issueの追補が衝突する場合、まずそれぞれの確認時点と適用範囲を提示し、旧図を黙って「現在図」に置き換えない。
- 図に「表示されない」ことは、未収集、適用範囲外、秘匿、検査不成立、真の不存在のどれかが未確定である可能性を保つ。TEIの閉じた実効Pipelineにおける不存在判定を、公開範囲未確定のYI/Product Catalogへ移植しない。
- この文書が他の既存資料と同じ説明を増やすだけなら、リンクだけを残し削除する。新しいEngineや永続データ構造を正当化するための文章にはしない。
