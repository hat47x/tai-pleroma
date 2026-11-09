# 製品側6判断のIssue草案（2026-11-06）

状態: **草案（未投稿）**。

> 2026-11-06追記: 6件のうち3件は決定済みとして閉じた — **agent資格情報の配線**と**`NOT_YET_VALID`**は製品の文書で、**未知adapterの扱い**は実装内の記述で。投稿する場合は、残る3件（受入の配線、複数Workerの分散、`readOnly`の非伝播＝要再特定）に絞る。[整理](../analysis/product-side-decisions-2026-11-06.md)
GitHubへのIssue起票は、リポジトリ外へ効果を出す操作として扱い、この作業では行っていません。判断の材料と本文をここに揃え、投稿するかどうかは別に決めます。

各項は、[製品側の判断が必要な6点](product-side-decisions-2026-11-06.md)の要約と、その根拠となるreceiptです。TAIは再観測と記録を担い、製品側の実装変更は行いません。

---

## 1. 実行結果の受入をEKI Control Planeへ配線する

**提案タイトル**: `EKI: Task実行結果の受入（result acceptance）をControl Planeへ配線する`

**本文**:

`internal/control`に`resultacceptance`の組み立てが無く、受入は`conformance/process`の試験が内部で構成しています。上流（`f4451df`、`66b0c04`）でも同じで、`internal/control/service/config.go`に受入の設定キーがありません。

現状、Task投入→Worker実行→claim提出までは通りますが、`GET /v1/tasks/{id}/result`は`409 RESULT_NOT_READY`を返し続けます。受入が無いため、結果を参照する経路が完成しません。

**論点**: 受入ポリシー（RA2等）、署名者の集合、閾値をControl Planeの構成として持つのか、運用側の別プロセスに置くのか。

**TAI側でできること**: 配線後の縦断確認（Task→実行→受入→結果参照）とreceipt化。

**根拠**: [product-side-decisions §1](product-side-decisions-2026-11-06.md)、[EKI-TEI-submit](../evaluations/records/EKI-TEI-submit-2026-11-03.json)

---

## 2. `NOT_YET_VALID`の時刻順序を計測・修正する

**提案タイトル**: `EKI: dispatchのNOT_YET_VALID延期を計測し、署名時刻と検証時刻の順序を定める`

**本文**:

同時投入時、dispatchが一部のTaskを`reserve lease: NOT_YET_VALID: approval is issued in the future`で延期します。延期は次tickで解消することが多く、Attemptが作られないまま残る場合があります。

`internal/core/placementverify`の`Revalidate`が`now.Before(a.IssuedAt())`で拒否し、dispatchは`l.now()`のスナップショットを取って署名後に`Reserve`で再検証します。

**論点**: 署名時刻と検証時刻の順序を単調にする（署名を先に確定させる、検証に署名時刻以降の時刻を使う等）のか、延期を仕様として受け入れるのか。

**TAI側でできること**: 修正後の再観測（同時投入でAttemptが全件作られるか）。

**根拠**: [product-side-decisions §2](product-side-decisions-2026-11-06.md)、[tei-sui-integration](../analysis/tei-sui-integration-2026-11-03.md)

---

## 3. 複数Workerの割り当てを分散させる

**提案タイトル**: `EKI: 複数Workerへの割り当て規則を定める`

**本文**:

Workerを2台登録しTaskを4件投入したところ、Attemptは2件しか作られず、いずれも同じWorkerに割り当てられました。

これは2の延期の副作用であり、分散の設計判断（配置の規則、同時実行の上限）は別途必要です。

**論点**: 配置をラウンドロビンにするのか、容量や負荷に基づくのか。同時実行の上限をどこで持つか。

**TAI側でできること**: 分散規則が入った後の再観測（Attemptが2台へ分かれるか）。

**根拠**: [product-side-decisions §3](product-side-decisions-2026-11-06.md)、[EKI-TEI-multi-worker](../evaluations/records/EKI-TEI-multi-worker-2026-11-03.json)

---

## 4. agent資格情報の配線をプロファイル非依存にする

**提案タイトル**: `SUI: agent資格情報のハッシュ鍵をプロファイル非依存に配線する`

**本文**:

`SUI_AGENT_CREDENTIAL_HASH_KEY`や`SUI_AGENT_OAUTH_AUDIENCE`を設定しても、local-devプロファイルでは`app.state`へ配線されず、agent要求は`503 agent_credential_unavailable`になります。配線は`settings.runtime_profile == "saas-multitenant"`の分岐内に、guest/saas系の12項目とまとめて置かれています。

設定値の有無だけでは有効化を判断できないため、運用時の切り分けが難しい状態です。

**論点**: agent資格情報をsaas限定の機能として扱い続けるのか、設定が揃っていれば他プロファイルでも有効にするのか。

**TAI側でできること**: 配線変更後の再観測（local-devでagent経路が通るか）。

**根拠**: [product-side-decisions §4](product-side-decisions-2026-11-06.md)、[SUI-TEI-agent-key-wiring](../evaluations/records/SUI-TEI-agent-key-wiring-2026-11-06.json)、[SUI-TEI-agent-read-path](../evaluations/records/SUI-TEI-agent-read-path-2026-11-06.json)

---

## 5. 未知のアクセス制御adapter名をエラーにする

**提案タイトル**: `SUI: 未知のSUI_ACCESS_CONTROL_ADAPTERを起動時に拒否する`

**本文**:

`SUI_ACCESS_CONTROL_ADAPTER`に未知の値を設定すると、`build_access_control_adapter`は例外にせず`NoopAccessControlAdapter`へ無言で退避します。noopは制御をしないアダプタなので、綴り違いが「統制が効いていない構成」を静かに成立させます。

SaaS事前検査は`access_control_adapter == "external_http"`を要求するためSaaSでは起動時に弾かれますが、single-tenantでは弾かれません。

**論点**: 綴り違いや未対応の値を起動時に拒否するのか、現状どおりnoopへ退避するのか。

**TAI側でできること**: 変更後の再観測（未知値で起動が止まるか）。

**根拠**: [product-side-decisions §5](product-side-decisions-2026-11-06.md)、[SUI-TEI-builders](../evaluations/records/SUI-TEI-builders-2026-11-06.json)

---

## 6. 呼び出し側の`read_only`を読み取りの決定へ伝播させる

**提案タイトル**: `SUI: AccessRequest.read_onlyを読み取りの決定へ伝播させる`

**本文**:

`AccessRequest(read_only=True, action="read")`を渡すと、`resolve_access_decision`は`allow=True, read_only=False`を返します。ローカル失効防止の`read_only`段は`write/export/share`のときだけ発火し、`read`では素通りしてPDPの決定がそのまま返ります。

呼び出し側が読み取り専用モードを宣言しても、決定の`read_only`欄には現れません。下流が`decision.read_only`だけを見て判断すると、宣言を見落とします。

**論点**: `read_only`を「書き込み禁止」の合図としてのみ扱うのか、読み取りの決定にも`read_only=True`として伝播させるのか。

**TAI側でできること**: 変更後の再観測（読み取りの決定に`read_only`が載るか）。

**根拠**: [product-side-decisions §6](product-side-decisions-2026-11-06.md)、[SUI-TEI-failsafe](../evaluations/records/SUI-TEI-failsafe-2026-11-06.json)

---

## 投稿する場合の手順（未実施）

1. 各草案を1件ずつIssueへ起票する（本文はそのまま使える）。
2. 既存の[#394](https://github.com/hat47x/tai-pleroma/issues/394)からリンクする。
3. 判断が下りたら、TAI側で再観測しreceiptを追加する。

この手順は外部への効果を含むため、実行の可否は人（Owner）の判断に委ねます。TAI側の記録と検証は、判断が下りた後も同じ手順で続けられます。
