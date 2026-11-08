# CX-01：CSW執筆Skillの探索手法をTEI設計に転用できるか（事前登録用・未実行）

**位置付け：YI Constellation横断の小さな実験案。正式なCSW Skill・TEI契約・外部Harnessの受入条件を変更しない。**
**Owner案：TAI #422/#233（比較の品質・開発工程）／TEI #1445/#2090/#2899/#3503/#3278（設計Candidateと独立検証）／CSW Repo（既存3つの執筆Skillの原文）。**
**関係：[Build-vs-Buy §17](../docs/yi-constellation/harness-build-vs-buy-decision-2026-11-08.md)／[統合計画 §45](../docs/yi-constellation/harness-skill-plugin-plan-2026-11-02.md)。**

## 1. 仮説と停止線

**検討したいこと**：通常AIの設計支援に対し、自由な発散やCSWの生成的探索を追加すると、TEIのPlugin Lifecycle/Hook/Graph編集における、**根拠と反証のある新しい設計差分**が増え、独立した検証可能性を維持できるか。

**独立させること**：外部HarnessのH2/H3（Tool-only / Product Skill）比較とは別。CSWは**主に執筆を支援する3つのテキストSkill**であり、工学上の適合や安全性の証明はまだない。初回TAI #168のG0 Read-deny→G1/G2実Tool受領→独立4 Slot、現状の比較適格0/4を**変更しない**。新しいAgent Loop/CSW Router/Plugin ABI/Registry/人の承認フローを作らない。

## 2. 凍結する入力・版・露出

- **Domain素材**：[TEI #3503](https://github.com/hat47x/tei-platform/issues/3503) Interaction Flow、[#3278](https://github.com/hat47x/tei-platform/issues/3278) Atomic Trait、[#2899](https://github.com/hat47x/tei-platform/issues/2899) DSH Lifecycle比較と関連する**公開・合成**の最小Issue/Sourceだけ。各Armへ同一bytes/順序で渡し、Task開始時に参照したIssue raw／当該Source full commitを固定する。今回のIssue URLは編集可能であり、URLだけをfingerprintとはしない。
- **比較用CSW Source**：[CSW main](https://github.com/hat47x/cultural-substrate-weaving/blob/main/README.md)の3 Skill（cultural-substrate-weaving、affinity-synthesis、writing-flow）。今回のファイル確認時のGit blobは順に `281fe544bd5de6cdb1799409fd1529997cb0c743`、`7e24d80ee5908103e1894c4304b8af10af4639df`、`643ecdc88d329f30025858741ed5de66c0d2813b`。**本番試験で使用した実commitと実Readしたbyte**を別途固定し、予定版と混同しない。
- **不変の環境**：同じモデルとAPI設定、Tool Profile、許可Source/OS/開示、Task、Budget/Timebox、候補提出フォーマット。CSW Skillを渡す以外は事前に同一とする。実Consumerへ見せてよい限定Projectionのみ使用する。
- **Reviewer-only**：評価基準/正負例は試行前に独立側へ登録。参加者へ独立Expected、過去の高得点案、採用判断を提示しない。評価者・実験者が同じ生成文を自己採点する場合は非独立と明記する。

## 3. 三Arm（YI-HV・TAI B0/B1/B2とは別）

| Arm | 参加者へ追加するもの | 同じ入力を使ったときに比較すること |
| --- | --- | --- |
| **CX-0**（通常AI設計） | 工学的設計レビューの通常依頼のみ | 既存の知識・Source・Issueから差分を出せるか |
| **CX-1**（一般的発散・批評） | 「違う見方・反証・代替案・負例を考える」という一般的な追加指示 | 汎用発想支援の増分。CSW特有の改善と混同しない |
| **CX-2**（CSW Method転用） | 現CSW Skill本文の**必要部分だけを実Read**して探索。方法は創造的仮説の発見まで。検証・受理は既存TEI/TAIへ戻す | 特定の枠組みから有効な設計差分が増えるか、それとも誤類推・費用増か |

CX-2のSkillは**執筆用原文**であり、内容を工学的な業務規則に自動転用しない。本文を直接Readする方法を基線に、DSH Skill/Profile、DSH専用Plugin化は別要因として後段比較。DSH利用をCX-2の必要条件にしない。

## 4. 同一のParticipant Task（たたき台。採点規準は含めない）

> TEIのPluginを導入・更新・無効化しても、実際の選択Providerと業務Operationの意味を保つには何が必要か。提示されたSourceのLifecycle/Interaction/Atomic Traitに対し、既存の設計記述では足りない可能性のある**具体的な境界・失敗・検査方法**を探索する。各候補について、(1)対象ElementとSource参照、(2)新しい設計仮説、(3)否定できる実験/故障注入、(4)採用時に変える必要がある一つの契約・Adapter、(5)残る不明、を短く記す。既にSourceに記載された要求の言い換えや象徴的なたとえは、新しい工学上の発見として数えない。コードの本番変更・秘密データ送出・実Provider作用をしない。

このTaskは一つの**同一対象**を用いてMethod差を判別するもの。既存Issueに反例が明示済みの「登録解除してもDB Commitは戻らない」等を、そのまま新発見と主張するのは誤計上。選んだ文化体系に元来ない意味・規則を既存TEI/業務契約へ見かけ上のAuthorityとして載せない。

## 5. 受入票・評価契約（採点は未実施）

| 変数／判定 | 取得方法 | 誤陽性・負例 |
| --- | --- | --- |
| 新規で非重複のCandidate | 対象Pinned Sourceに含まれない差分かを独立Reviewerが出典付き照合 | 既存Issueの別表現・アイデア数・比喩の数を成功数に加算しない |
| 具体性と検証可能性 | 対象Contract、生成/実装変更、識別可能な反例/負例が揃うか | Trait未実装なのに名称だけ宣言、Provider B選択→実A呼出しを見落とす |
| 意味・権限の過大推論 | Source/Revision、Owner Acceptance、現在Host Grant、実Effectを分離しているか | 候補の多様性を受理・認可・安全証明へ昇格させた案は採用不能 |
| 失効と継続の判別 | 無関係Source変更・A→B→A・Plugin removal・未知Effectの違いを説明 | すべて再実行／古い証拠の自動復活／通信切断後の二重Effect |
| 成果の運用費 | モデル料金、Token、Latency、人の確認・修正、参照実Read/評価時間 | 安いが独立Expectedを満たさない案を優先しない |
| 比較の資格 | Assigned Arm全数（ITT）、実処置/適格（PP）、Skill実LoadとModel受領、C0/C1/C2汚染 | Skill未読のCX-2、CX-0へのCSW説明漏れ、途中条件変更を成功例だけ除外 |

**評価の段階**：(a)Source/Output/Costの実観測と露出の確認、(b)根拠・検証可能性・非重複・危険性のBlind Review、(c)有望な案だけTEI/CSWの各Ownerが採否を判断。見つけた発想を機械的に適用する実験ではない。統計的な普遍改善率を小規模試行で主張しない。

## 6. 実施順・終了条件

1. **CX-0基準系**：現行Source／Tool／Agent実環境と出力／欠落を記録。Task入力、レビュー規則、禁止事項を凍結。誰も試験結果をまだ見ていない状態を記録。
2. **CX-1／CX-2**：同一モデル・Source・予算で独立Sessionを事前割付して実行。順序・経験・参照資料の漏えいを記録。CSW SkillsはCX-2に必要な原文だけを遅延Read。
3. **独立点検**：単なる発散の数ではなく、実装可能な独立差分／違反／不要な変更／レビュー総費用を出す。厳密なSource比較の結果、差分0ならそれも許容する。
4. **Owner判断**：意味上の変更候補はTEI #3503/#3278/#2090/#2899へ戻す。CSWの執筆Skillを変更すべき根拠は、CSW Repo自身の編集・利用評価に返す。観測結果に基づき利用を選択/保留/縮小する。

**終了条件**：比較可能な実入力・原文版・露出・出力・独立レビューが残り、CSWによる改善／未改善／害のどれかを判断できる。**未実施**：CX-0/1/2実生成、DSH実Skill/Profile/Plugin試験、工学向けCSW効果、TEI Target変更、正式Owner受理、実H2/H3比較。試験を追加しただけで最優先のTAI #168を完了としない。
