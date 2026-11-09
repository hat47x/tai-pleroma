# 製品側の判断が必要な6点（2026-11-06）

Status: **整理**。TAIが接続検証で突き当たった、製品側の設計判断を要する点を並べる。ここで可否を決めない。

> 追記（2026-11-06）: 各項目について、**製品側の文書がすでに決めていないか**を確認した。決まっている項目は、TAIの観測をその決定に照らして閉じる。決まっていない項目だけを判断待ちとして残す。

## 1. 実行結果の受入をControl Planeへ配線するか

観測: 自前構成でTaskを実行し、Agentは`result_claim_submitted`（`claim_decision: new`）まで進むが、`GET /v1/tasks/{id}/result`は`409 RESULT_NOT_READY`を返す。[receipt](../evaluations/records/EKI-TEI-manual-execution-2026-11-03.json)

根拠: `internal/control`に`resultacceptance`の組み立てが無く、受入は`conformance/process`の試験が内部で構成している。2026-11-06時点の上流（`f4451df`）でも同じで、`internal/control/service/config.go`に受入の設定キーが無い。

論点: 受入（RA2等のポリシー、署名者の集合、閾値）をControl Planeの構成として持つのか、運用側の別プロセスに置くのか。

TAI側でできること: 受入が配線された後の縦断確認（Task→実行→受入→結果参照）。配線そのものは製品変更。

製品側の文書（2026-11-06確認）: EKIの`architecture/AUTHORITY_BOUNDARIES.md`は**RAC-1 Result Acceptance Authority**の役割・入力・他Authorityとの関係を定義している（「ResultClaimをAccepted Resultに昇格させる、最終的なRelying Party」）。一方で、RAC-1を**どのプロセスで動かすか**（Control Planeの構成か、運用側の別プロセスか）は書かれていない。**役割は決定済み、配置は未決**。判断待ちのまま残す。

追加の観測（2026-11-06、TEIの意味変更から）: 受入の有無と別に、**製品が意味を受け取る経路そのものが手書きの許可リスト**であることが分かった。SUIの`from_artifact`はカード・島・辺の各フィールドを明示的に読み、知らないキーは読まない。そのため新しい意味は`DocumentV1`の検証を通過したまま落ちる（[mapping](../evaluations/records/SUI-consumer-mapping-2026-11-06.json)、[meaning change](../evaluations/records/TEI-meaning-change-2026-11-06.json)）。

この事実は、受入を配線する判断にも効く。受入が「投影された意味をそのまま受理する」のか「製品のモデルに写した後の値を受理する」のかで、受理の対象が変わる。写像が許可リストである限り、後者を選ぶと新しい意味は受入の対象にならない。

## 2. `NOT_YET_VALID`の時刻順序を計測・修正するか

観測: 同時投入時、dispatchが一部のTaskを`reserve lease: NOT_YET_VALID: approval is issued in the future`で延期する。延期は次tickで解消することが多く、Attemptが作られないまま残る場合がある。[分析](tei-sui-integration-2026-11-03.md)

当たり: `internal/core/placementverify`の`Revalidate`が`now.Before(a.IssuedAt())`で拒否する。dispatchは`l.now()`のスナップショットを取り、署名後に`Reserve`で再検証する。

論点: 署名時刻と検証時刻の順序を単調にする（署名を先に確定させる、検証に署名時刻以降の時刻を使う等）のか、延期を仕様として受け入れるのか。

TAI側でできること: 修正後の再観測。計測・修正は製品変更。

製品側の文書（2026-11-06確認）: EKIの`plan/UPSTREAM_PLAN.md`が#437として同じ事象を調べている。`dispatch.Tick`は毎tick Readyを列挙し直すため「一度未来と判断されたら永久に止まる」は成り立たず、同日3回の再実行は3回ともPASSだった。**決定: 修正ではなく計測で閉じる**（再開条件は「idleのしるしが90秒出ないのに落ちる」「低負荷でも再現する」の2つ）。

この決定により、本項目は**判断待ちから外す**。TAIの観測は決定と矛盾しない（延期は事実だが、恒久停止ではない）。TAIは再開条件に当たる事象を見たときだけ再観測する。

## 3. 複数Workerの割り当てを分散させるか

観測: Workerを2台登録しTaskを4件投入したところ、Attemptは2件しか作られず、いずれも同じWorkerに割り当てられた。[receipt](../evaluations/records/EKI-TEI-multi-worker-2026-11-03.json)

論点: これは2の延期の副作用であり、分散の設計判断（配置の規則、同時実行の上限）は別途必要。

TAI側でできること: 分散規則が入った後の再観測。規則の設計は製品変更。

## 4. agent資格情報の配線をプロファイル非依存にするか

観測: `SUI_AGENT_CREDENTIAL_HASH_KEY`や`SUI_AGENT_OAUTH_AUDIENCE`を設定しても、local-devプロファイルでは`app.state`へ配線されず、agent要求は503 `agent_credential_unavailable`になる。配線は`settings.runtime_profile == "saas-multitenant"`の分岐内に、guest/saas系の12項目とまとめて置かれている。[receipt](../evaluations/records/SUI-TEI-agent-key-wiring-2026-11-06.json)

当たり: `main.py`のモジュールレベルで、`if settings.runtime_profile == "saas-multitenant":`ブロックの中に`app.state.agent_credential_hash_key`等が入っている。ASTで確認した。

論点: agent資格情報をsaas限定の機能として扱い続けるのか、設定が揃っていれば他プロファイルでも有効にするのか。設定値の有無だけでは有効化を判断できないため、運用時の切り分けが難しい。

製品側の文書（2026-11-06確認）: SUIの`01_Plans/adr/ADR-0093-tenant-bound-agent-credentials-for-mcp.md`が**Accepted**（2026-10-09）で、外部agentを「所属を持たない別種の主体（agent principal）」として扱い、**テナントの管理者が登録した文書付与つきの資格情報だけ**で読み取り専用の投影を許すと決めている。テナントに束縛することが安全の根拠なので、テナントを持たないプロファイルで有効にする余地は設計上ない。

**この項目は決定済みとして閉じる。** TAIの観測（local-devでは`agent_credential_unavailable`）は決定どおりの挙動であり、不具合ではない。設定値が見えても有効にならないのは「設定より安全側の既定」ではなく「テナント束縛が前提だから」である。

TAI側でできること: 配線変更後の再観測（local-devでagent経路が通るか）。配線の変更は製品変更。

## 5. 未知のアクセス制御adapter名をエラーにするか

観測: `SUI_ACCESS_CONTROL_ADAPTER`に未知の値を設定すると、`build_access_control_adapter`は例外にせず`NoopAccessControlAdapter`へ無言で退避する。[receipt](../evaluations/records/SUI-TEI-builders-2026-11-06.json)

当たり: `access_control.py`の`build_access_control_adapter`が、既知の4名（noop/mock/http/external_http/external）以外を`NoopAccessControlAdapter()`で返す。

論点: 綴り違いや未対応の値を、起動時に拒否するのか、現状どおりnoopへ退避するのか。noopは制御をしないアダプタなので、退避は「統制が効いていない構成」を静かに成立させる。SaaS事前検査は`access_control_adapter == "external_http"`を要求するため、SaaSでは退避が起動時に弾かれるが、single-tenantでは弾かれない。

TAI側でできること: 変更後の再観測（未知値で起動が止まるか）。値の扱いの変更は製品変更。

## 6. 呼び出し側の`read_only`を読み取りの決定へ伝播させるか

観測: `AccessRequest(read_only=True, action="read")`を渡すと、`resolve_access_decision`は`allow=True, read_only=False`を返す。ローカル失効防止の`read_only`段は`write/export/share`のときだけ発火し、`read`では素通りしてPDPの決定がそのまま返る。[receipt](../evaluations/records/SUI-TEI-failsafe-2026-11-06.json)

当たり: `access_control.py`の`apply_local_failsafe`が`request.read_only and request.action in {"write", "export", "share"}`でのみ拒否を作る。`_read_only_fallback`が使われるのはpolicy_ref欠落・PDP失敗の経路だけ。

論点: `read_only`を「書き込み禁止」の合図としてのみ扱うのか、読み取りの決定にも`read_only=True`として伝播させるのか。現状は呼び出し側が読み取り専用モードを宣言しても、決定の`read_only`欄には現れないため、下流が`decision.read_only`だけを見て判断すると宣言を見落とす。

TAI側でできること: 変更後の再観測（読み取りの決定に`read_only`が載るか）。伝播の変更は製品変更。

## 共通の注記

6項目はIssueへ起票できる粒度に要約済み（[Issue草案](product-side-decisions-issue-drafts-2026-11-06.md)、2026-11-06）。起票は外部への効果を含むため未実施。


- いずれもTAIの接続では解消できない。TAIは再観測と記録を担う。
- 生産性・受入可否の判断には使わない（PoC完了後に評価する前提）。
- 公開gateは`allowed=false`のまま。

## 整理の結果（2026-11-06）

| 項目 | 状態 |
| --- | --- |
| 1. 受入の配線 | **未決**（RAC-1の役割は定義済み、配置が未記載） |
| 2. `NOT_YET_VALID` | **決定済み**（#437として計測で閉じる。再開条件つき） |
| 3. 複数Workerの分散 | **未決**（2の副作用であり、配置の規則は未記載） |
| 4. agent資格情報の配線 | **決定済み**（ADR-0093。テナント束縛が前提） |
| 5. 未知adapterの扱い | **決定済み**（実装内に理由つきで記述。noopは常に許可） |
| 6. `readOnly`の非伝播 | **要再特定**（`read_only`は認可経路にあるが、効果は未確認） |

決定済みの2件は判断待ちから外した。残る4件のうち3・5・6は、製品側の文書をさらに当たるか、Issueで見解の供給を受ける必要がある。

この整理で分かったのは、**TAIが「製品の設計判断が要る」と見ていた項目のうち2件は、製品側ですでに決まっていた**ことである。TAIは製品の文書を先に確認する順序を取るべきだった。次回以降、接続検証で判断待ちを作るときは、製品のADR・設計文書を先に当たる。

## 追記（2026-11-06、項目5・6の再確認）

### 5. 未知adapterの扱い — 決定済み

SUIの`routes/docs.py`に、**noopアダプターの挙動と、その理由が実装の中に書かれている**。

> The default adapter (no adapter configured at all, or the "noop" name) always allows GET/PUT /docs/{doc_id} regardless of visibility — apply_tenant_boundary_guard is the sole gate in that mode. Filtering the list by visibility there would make the list *more* restrictive than the single-document read path it is a foundation for, not more correct.

つまり「未知・未設定のadapterはnoopとして常に許可し、一覧の可視性フィルタは単票の読み取り経路より厳しくしない」ことが**意図として書かれている**。TAIが観測した挙動は仕様どおりで、不具合ではない。**この項目は閉じる。**

### 6. `readOnly`の非伝播 — 要再特定

SUIには認可経路に`read_only: bool`の引数がある（`routes/docs.py`の`_authorize_request`）。しかし、この値がアダプターの判定まで届くか、届かない場合に何が起きるかは**まだ確かめていない**。

- 分かっていること: `read_only`は認可要求の組み立てに渡されている
- 分かっていないこと: 外部PDPやnoopアダプターがその値を判定に使うか、使わないなら「読み取り専用の要求が書き込みとして扱われ得る」のか
- 次にやること: `_authorize_request`の呼び出し元と、アダプターの`AccessRequest`に`read_only`が入るかを読む。**実行での確認はその後**

この項目を「製品の判断待ち」に置くのは、**根拠を読めていないため**であって、不具合を見つけたためではない。根拠が確定するまで判断待ちとして数えない。
