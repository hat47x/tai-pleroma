# 承認を「観測」として受け取れるか：SEI・SUI・TEI・EKIでの確認

状態: **観測記録と読み方の判断**。各Productの仕様変更の提案ではない。公開承認・Owner判断・利用者評価は**行っていない**。
問い: 「公開してよい」という人の承認を、TAIが新しい機構なしに観測として受け取れる実Productはあるか。あるなら、AIの自己申告をどこで弾けるか。
背景: [SCN-001 成果の観測](SCN-001-outcome-observation-2026-11-11.md)で、公開というGoal（P-Publish）は「承認者不明」で止まり、反例O4（承認の自己申告）は自己試験だけだった。
記録: [SEI](records/SEI-self-declared-approval-2026-11-13.json)、[SUI](records/SUI-proposal-decision-authority-2026-11-13.json)、[EKI](records/EKI-self-declared-approval-2026-11-13.json)。実験の原文は [tools/approval-probes](tools/approval-probes/)。

## 1. 結論

**現時点で、SCN-001の公開承認を観測として受け取れるProductは無い。** したがって P-Publish は「未達（Authority待ち）」のままである。新しい機構は足さない。

承認の記録が「観測」と呼べるための条件は四つある。

| 条件 | 意味 |
| --- | --- |
| (a) 主体が認証から決まる | 承認者は要求の本文ではなく、Productが認証した主体から記録される |
| (b) 作り手の資格では承認できない | 成果物を作った側（AI・agent）の資格では、承認の操作そのものが拒否される |
| (c) 対象に束縛される | 承認が特定の成果物（digest・版）に結び付き、別の対象には使えない |
| (d) 外から読める | 承認の有無を、承認者以外が読み取りだけで確かめられる |

実Productでの結果：

| Product | (a) | (b) | (c) | (d) | 読み方 |
| --- | --- | --- | --- | --- | --- |
| SEI Decision | ✗ 自由記述 | ✗ gateは自己申告をallow | ✗ digestへの束縛なし | ○ | 「誰かがそう記録した」という記録。権限の証拠にしない |
| SUI Proposal判定 | ○ sessionから取得 | ○ agent資格は403 | △ ProposalのsourceBundleHashに束縛 | △ 状態と時刻のみ。判定者は読めない | 資格の種類は分けられる。対象はSUI内のProposalで、外部成果物ではない |
| TEI | ✗ | ✗ | ✗ | — | 受理の経路が無い（`ownerDecision` は常に `pending`）。コード読みのみ |
| EKI受付 | ○ トークンの主体 | — | — | — | 人の承認という概念が無い |

## 2. 観測

### SEI（`cd6eb025`、実バイナリ）

- agentが自分で「`person:owner` が承認」と書いたDecisionを、gateは **allow** した。`agent:claude` を名乗ったDecisionも allow で、区別しない。
- basisとrationaleを要求する方針にしても、それらを書き添えたDecisionは allow になった。
- storeのファイルを直接書き換えても `verify` は成功し、digestが変わるだけだった。
- gateは毎回、「責任者がこの行為の権限を持つこと」「行為がDecisionの範囲に合うこと」を**未検証**として返す。
- 書込みを止められたのは、MCPで `add_decision` を提供しない場合（既定、`--read-only`）だけだった。

これはSEIが自分で述べている限界（QUICKSTART、ADR-0016「Decisionの存在は権限を成立させない」）のとおりで、欠陥ではない。

### SUI（`5d234892`、自身のテスト用構成でバックエンドを実行）

- agent資格でProposalの判定を記録しようとすると **403 `agent_write_not_enabled`**。member用のheaderを併せて付けても同じで、記録は0件だった。
- memberの判定は記録され、agent資格から `accepted` と `decidedAt` を読めた。**判定者は読めない。**
- 本文で別の判定者を名乗る要求は422、ProposalのsourceBundleHashと合わない要求は409、主体が空の要求は401。
- **限界**：SUIが分けるのは資格の種類であり、判定者が人であることは証明しない。試験構成では `x-forwarded-user` の値がそのまま主体になった。member sessionを持つAIは人と区別できない。

### TAI自身の記録

SCN-001の実行記録にある `provisionalApproved: true` は、**TAIの参照ツール自身が書いたSEI Decision**（`dec-02`、`--source tai`、`--responsible role:provisional-owner`、`tools/reference-sei-decision/main.go:140-143`）から導かれている。根拠の `owner-instruction-2026-10-26` は文字列である。これは自己申告の記録であり、Ownerの承認の観測ではない。記録は従来から `authorityVerified: false`、`humanReviewed: false` を併記しており、その読み方は正しい。

## 3. TAIが守る読み方

承認に触れるときは、次のどの段階の根拠かを必ず添える。上の段階へ読み替えない。

| 段階 | 根拠 | 言えること | 例 |
| --- | --- | --- | --- |
| A0 文言 | 自由記述の欄や本文にある承認の文言 | 何も言えない | EKIの `parameters` に書いた `approved_by` |
| A1 自己申告の記録 | 誰でも書ける記録。主体は自由記述 | 「承認の記録がある」 | SEI Decision、TAIの `provisionalApproved` |
| A2 資格を分けた記録 | Productが認証した主体が記録し、作り手の資格では書けない。対象に束縛 | 「作り手とは別の資格の主体が判定した」 | SUI Proposal判定 |
| A3 Ownerの承認 | 判定した主体が、その行為の権限を持つ人であることの確認 | 「Ownerが承認した」 | **該当するProductなし** |

- P-Publish の成立には A3 が要る。A1 と A2 は足しても A3 にならない。
- A2 は「agentが承認者の資格を持っていない」ことが前提である。**この作業環境では、agentはリポジトリOwnerのGitHubアカウントで `gh` を操作している。** したがってGitHub上の承認・merge・コメントは、Ownerの名義であっても A1 として読む。
- 安全な停止（公開しない）は従来どおり制約の充足であり、A1 の記録があっても公開しない。

## 4. 新しい機構が要るか

要らない。足りないのは仕組みではなく、**承認者の資格をagentから分けること**と、**誰が承認者かというOwnerの指名**である。どちらも設定と人の判断で、TAIの実装では解けない。

既存の面で A2 に届くのはSUIだけだが、対象はSUI内のProposalである。D-04の公開判断をそこへ載せるかどうかは、SUIとTAIのOwnerの判断であり、ここでは採らない。

## 5. 未実施と限界

- 実在の人による承認、本番の認証基盤（OIDC等）、署名、権限の提供元は使っていない。
- SUIは自身のテスト用構成（SQLite、header由来の主体）で、配備された環境ではない。文書の版への束縛、編集後に古い判定が残るか（A→B→A、N-01）は確かめていない。
- TEIはコードを読んだだけで実行していない。
- SEIは1回の実行。同一の操作者が記録と検査の両方を行った。
- A3 に当たる観測は0件である。

## 6. Ownerに残る判断

1. SCN-001の公開を承認する人を指名するか。指名が無い限り P-Publish は成立しない。
2. agentの資格を、承認者の資格（GitHubアカウント、SUIのmember session）から分けるか。
3. D-04の公開判断を既存のどの面で記録するか（SUIのProposal判定に載せる、リポジトリ外の手続にする、等）。
4. `provisionalApproved` という名前が承認と誤読されるおそれを、名前の変更で扱うか、読み方で扱うか（[#28](https://github.com/hat47x/tai-pleroma/issues/28)の範囲）。
