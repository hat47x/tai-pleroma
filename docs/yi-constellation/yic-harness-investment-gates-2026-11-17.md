# YICハーネス構想：独自化の判断基準と最初の実行順（2026年11月17日）

状態: 設計判断の整理と実行計画（2026-11-17）。新しいHarness・共有Agent Loop・実OS/Provider E2E・Owner受理はNOT RUN。

> **位置づけ：設計判断の整理・実行計画。新しいHarness、共有Agent Loop、実OS/Provider E2E、正式なOwner受理はNOT RUN。** 本文は[TAI #234](https://github.com/hat47x/tai-pleroma/issues/234)の投資判断、[#168](https://github.com/hat47x/tai-pleroma/issues/168)の実Harness適格性、[#271](https://github.com/hat47x/tai-pleroma/issues/271)のActivity継続、[既存の横断UI計画](harness-cross-ui-session-probe-2026-11-14.md)を短い実装判断へ結ぶ補助票である。新規の契約正本、検査器、中央Host、Runner、Session Store、Lock、Registry、認可器を設けない。

**Codex公開ソースの取り込み方：** [Codex公開Harnessの活用判断と接続実行票](codex-source-integration-decision-2026-11-17.md)に、固定した上流Source、既存Go Harness Adapterでの単発実行、App Serverの双方向Session接続、実証負例とC0〜C5の順序を整理した。これはH-01／H-03以降の補助票であり、二本の独立P0、B4内製判定、受入Ownerを変更しない。

**Codexに関する確定方針（2026-11-18）：** 更新が速いCodexの実装はYICへ埋め込まず、外部Harnessの接続・比較対象とする。一方、対象Pin、進捗、承認、Native Session／限定Activity Handoff、Tool・Evidence、並列Workstreamの安全な統合などはYIC・各Productの既存Ownerへ取り込む。[Codex接続実行票](codex-source-integration-decision-2026-11-17.md)に責務対応表と版更新時の確認条件を追加した。B4独自Loopの不採用判断、#168 G0/G1/G2／四Slot適格0/4、TEIセルフビルドの独立P0は変更しない。

## 結論：独自UIは先に、独自Agent Loopは後から判断する

YICが実現したいのは「AIを自分で回すこと」ではなく、**利用者が選んだ仕事と対象を、異なる製品・画面・Harnessの間で安全に扱い続けられること**である。外部HarnessのNative Sessionをそのまま共有できる場合はその能力を利用する。できない場合も、許可されたActivityの目的・対象参照・未決事項を新Sessionへ引き継ぐ経路を用意する。ただし両者を同一の「Session復旧」と呼ばない。

- **YIC／TAIが担う**：仕事の入口、対象固定と再確認、使用可能な能力の提示、現在の開示範囲に合わせた短い引継ぎ、結果候補の戻り先、複数作業の見通し。
- **外部Harnessが担う**：モデル呼出し、Native Session、Turn、Tool実行、利用可能なGoal／Schedule／Subagent。DSHは検証順でわずかに先行するが、Codex、Claude Code、OpenCode等も同等の候補とし、機能の存在・権限・費用・復旧保証は構成ごとに実測する。
- **各Product／Hostが担う**：TEIの意味・Source・Build、SUIの選択・原文、SEIの判断、SHOの保存・出典、EKIの委任・Result、Host／Providerの現在認可と実作用。TAIは第二の業務意味正本や権限正本を持たない。

[TEI #4583](https://github.com/hat47x/tei-platform/issues/4583)のWindows実Stage1→Stage2セルフビルドと、TAI #168の外部Harness適格性は、**互いに独立したP0**。どちらかの局所的な成功を他方へ加算しない。

## 1. 分離する四つの識別と三つの時点

| 対象 | 帰属する正本 | やってはいけないこと |
| --- | --- | --- |
| **Activity**（依頼・目的・保留） | TAI #271 | Native Session IDを活動のIDとする |
| **View／Pinned Target**（Focus、選択意図、元対象） | 各Product | 画面上の現Focusへ遅れて届いたAI回答を自動適用する |
| **Native Session／Turn**（実Tool・Transcript） | 外部Harness／Host | Session ID・完了発話・Cancel ACKをProductの結果とする |
| **Product Operation／Attempt**（Effect、Receipt、Consumer） | TEI・SHO・EKI等の既存Owner | Tool exit=0やCommitの自己申告を業務成功・成果物受領に置換する |

**操作前**は現在のSource／Root／対象／Scope／Grant／開示先を再解決する。**操作中**は実Tool Request、Responseの完全性、実行したProviderとAttemptを区別する。**操作後**は候補・実Effect・Receipt・独立Consumer受領を別々に照合する。古いSessionやHashが同じでも、現在の利用資格が同じとは限らない。

対象固定には、(a)いま画面に見えるFocus、(b)利用者が維持したいPinの意図、(c)その時点でProductが実際に解決した対象、の三段階がある。前二者をそのまま実操作のAuthorityに昇格させない。

## 2. 機能は接続形式ではなく、できる操作ごとに確認する

既存の横断UI計画M0〜M4を再利用し、独自のCapability ABIは作らない。

| 利用者に示すモード | 必要な実測 | 不成立時の扱い |
| --- | --- | --- |
| **M0 Product-only** | Product単独で対象を正しく扱える | 通常利用は維持 |
| **M1 Activity handoff** | 許可Projection、既存Handoff v1、次Consumerによる実Read | Product-onlyに戻る |
| **M2 Native Session view** | 現Sessionと過去Transcriptの双方を現在の閲覧先に開示できる | 新SessionへのM1に縮退 |
| **M3 Native Session control** | M2に加え、実HostによるTurn帰属と同時操作制御 | 単独Writer＋別Viewは閲覧のみ |
| **M4 Product apply** | 元Pinの再解決、Product受理、現在Grant、Effect／Receipt／Consumer | 候補差分に留める。作用不明なら照会 |

この表は**受入票の観点**であり、新しい共通状態遷移エンジンの仕様ではない。CLI、MCP、Wails Bridge、Web APIは、各Productの既存Typed Operationへ薄く接続する。Wails上の同一Go Applicationを優先し、別Process Workerや独立Serverは[TEI #4635](https://github.com/hat47x/tei-platform/issues/4635)の配置別実証が必要になってから比較する。Go→WASMも、体感上の遅延を再現測定できた工程に限って検討する。

## 3. 最初の二本のP0と、その先の最小作業

### P0-A：TEI Studioの実セルフビルド

[TEI #4583](https://github.com/hat47x/tei-platform/issues/4583)をOwnerとして、同じ実Build Intent・同じAttemptで、Stage1実TEI Processが選択Generator／Builderを起動し、生成Desktopを実Windows WebView2が受領したことまで確認する。通常Desktopの合格、生成物のHash一致、別HEADのCI Greenは別Claim。YICの共有SessionやHarness追加は、このExitを妨げる新条件にしない。

### P0-B：最初の外部Harness比較を資格化する

[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の公開TEI固定Taskを変えず、G0（実OSの公開Read成功／非許可Read拒否）→G1（実Egressの送出範囲）→G2（Tool Replyとstdout/stderr完全性）を先行する。その後に**新規割付したH2→H3→H3→H2の4独立Slot**を実行し、Skillなし対Product Skillありの品質、Unknownの保持、費用、人手を独立Expectedで比較する。

DSH実H3ではSkill本文の受領とTool transportに限定的な証拠がある。一方、過去Session再利用・Root不一致・完全でないTool Result・Read隔離不足により**比較適格は0/4**。H3でSkillを読めたことだけをSkill有効性へ昇格しない。既存[TAI #680](https://github.com/hat47x/tai-pleroma/issues/680)で指摘されたCI途中失敗によるSkill自己試験のskipも、試験不実施として扱う。

### 後続J1：対象を一つ選び、返答候補を元Productへ戻す

既存の[最初のTEI連携実行票](tei-selection-harness-first-vertical-slice-2026-11-15.md)と[QH実行票](cross-product-handoff-execution-tickets-2026-11-11.md)を使用する。公開TEIの一Subjectを実CLIで読む→Pinned Targetと元Sourceを再解決→開示可能な短いProjectionを表示→許可されたTool-only Harnessへ送達→完全Replyを受け取る→元Productの候補として表示する、という一往復に限定する。GUI Pinの成功とCLIのSource read、外部Harness受領を一括で採点しない。

### 後続J2：二Harness・二Product・長時間委任

J1が成立した範囲で、別Harnessの新Sessionに許可済みActivityだけ引き継ぎ、実際のCapability、開示先、費用を再判定する。その後にTEI→SHOなど二Productの**同じ実Artifactの受領**へ拡張する。Goal／Schedule、Quota切替、Host再起動、複数Workstreamは[TAI #234](https://github.com/hat47x/tai-pleroma/issues/234)のG1〜G6と[TEI #2017](https://github.com/hat47x/tei-platform/issues/2017)の開発作業票を使用。業務Effectや期限内復旧が必要なら[EKIの既存契約](https://github.com/hat47x/eki-fabric/issues/57)を利用する。新しい中央Scheduler・Queue・Job DBを先に作らない。

## 4. 独自Agent Loopへの投資を決める判定票

比較単位は「モデル」単独ではなく、**User Job × Product × Harness実行物／版 × Provider／Model × Tool／Skill × OS／開示Profile × 課金経路**。モデル名やAPI互換性から、購読枠・Tool・権限を継承したことにしない。

| 判定軸 | 独立に観測すること | 判断 |
| --- | --- | --- |
| **V：価値** | 同じ仕事をAIなし／外部Tool-only／Product Skill／TAI Skillで完了できるか。品質・再説明回数・人手・費用を分ける | 既存手段で十分なら自作不要 |
| **C：実Capability** | 二つ以上の代表Harnessで同じ必要操作を実際に使えるか。Session復元とActivity再開は別 | 一Harness固有の不足だけで共通Loopを作らない |
| **S：安全性** | 開示拒否、OS read-deny、現在Grant、応答喪失、重複作用の負例が落ちるか | 未確認なら用途限定で停止 |
| **O：運用** | Host再起動、Quota枯渇、Goal/Schedule不達、部分失敗、独立レビュー、Git統合の費用 | 外部Host／EKI／既存CIで埋まるなら再利用 |
| **D：差別化** | 外部Harness＋薄いAdapterでは代替できないLoop固有の必須欠落が、同じJobで再現するか | 欠落・代替不能・保守費用・Owner受理が揃った場合だけ内製を検討 |

V/C/S/O/Dは合計点にしない。**B4独自Agent Loopは未採用**。技術的に作れることは投資理由ではない。費用比較では、定額利用権、従量API、正規の外部Gateway、ローカル実行を別々に扱い、契約・現行Quotaが確認できない自動Fallback課金は行わない。

## 5. 開発への落とし込みと停止条件

| 作業票 | 既存Owner／受入 | 今回加える判断 |
| --- | --- | --- |
| **H-01** 実Harness四Slotの資格化 | TAI #168／#488、#232 | 絶対にTask・Skill byte・独立Expectedを途中変更しない。G0失敗ならenvironment-ineligible |
| **H-02** Desktop生成物の実Consumer | TEI #4583／#1824 | 正規BuilderとStage1再入、生成Windows実受領を独立確認 |
| **H-03** CLI・UIのPin→返答一往復 | TEI #4515／#3419、TAI QH §10 | 現Focus≠Pinned Intent≠Current Resolved Targetを負例で確認 |
| **H-04** 別Harnessへの限定Activity再開 | TAI #271／#234 | 旧Raw/Transcript/Grantを無条件に渡さず、Live Session復旧とは別採点 |
| **H-05** 複数AIの仕事の統合 | TEI #2017、TAI #422／#233 | モデル→役割→作業を分け、Branch/Path/HEAD・Focused Test・独立レビュー・実Mergeを各別記録 |

実装担当は、各票の対象Repoと**exact HEAD、実使用したCLI/Tool、入力Source、環境、結果、未確認・SKIP、独立Expected、差分PRとMerge後の確認**を既存Ownerへ返す。開発中のAgentには担当Branch／Path以外を無断編集させず、成功した別HEADの試験を現在のmainへ自動移送しない。AI生成の提案はOwner意味受理、PRのGreenは製品実作用、CommitはConsumer受領の証拠ではない。

## 6. 現時点の受入状況と次の判断

- **確認済み（限定）**：外部DSHによる実Tool transportとH3固定Skillの受領。Product側ではTEI CLIやStudio Pin、SUI内部Source再解決、Rule Reader／生成の個別回帰が進んでいるが、それぞれ対象HEAD・Host・Claimが異なる。
- **未成立／NOT RUN**：TAI #168の適格な独立4/4比較（現0/4）、二Harness切替の価値比較、Native Sessionの横断Live control、現在のGrantを伴うProduct Apply、YICを通した同一Attemptの二Product実受領、B4自作Loopの必要性立証。
- **次の判断**：まずH-01とH-02を独立に完了させる。その後、H-03の最小一往復から効果を測る。H-04／H-05の結果を経て初めてB4の投資判断を再開する。研究候補や並列タスク数には一律上限を設けないが、未実証の機構をMVP必須へ昇格させない。
