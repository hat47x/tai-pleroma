# 製品側の判断が必要な5点（2026-11-06）

Status: **整理**。TAIが接続検証で突き当たった、製品側の設計判断を要する点を並べる。ここで可否を決めない。

## 1. 実行結果の受入をControl Planeへ配線するか

観測: 自前構成でTaskを実行し、Agentは`result_claim_submitted`（`claim_decision: new`）まで進むが、`GET /v1/tasks/{id}/result`は`409 RESULT_NOT_READY`を返す。[receipt](../evaluations/records/EKI-TEI-manual-execution-2026-11-03.json)

根拠: `internal/control`に`resultacceptance`の組み立てが無く、受入は`conformance/process`の試験が内部で構成している。2026-11-06時点の上流（`f4451df`）でも同じで、`internal/control/service/config.go`に受入の設定キーが無い。

論点: 受入（RA2等のポリシー、署名者の集合、閾値）をControl Planeの構成として持つのか、運用側の別プロセスに置くのか。

TAI側でできること: 受入が配線された後の縦断確認（Task→実行→受入→結果参照）。配線そのものは製品変更。

## 2. `NOT_YET_VALID`の時刻順序を計測・修正するか

観測: 同時投入時、dispatchが一部のTaskを`reserve lease: NOT_YET_VALID: approval is issued in the future`で延期する。延期は次tickで解消することが多く、Attemptが作られないまま残る場合がある。[分析](tei-sui-integration-2026-11-03.md)

当たり: `internal/core/placementverify`の`Revalidate`が`now.Before(a.IssuedAt())`で拒否する。dispatchは`l.now()`のスナップショットを取り、署名後に`Reserve`で再検証する。

論点: 署名時刻と検証時刻の順序を単調にする（署名を先に確定させる、検証に署名時刻以降の時刻を使う等）のか、延期を仕様として受け入れるのか。

TAI側でできること: 修正後の再観測。計測・修正は製品変更。

## 3. 複数Workerの割り当てを分散させるか

観測: Workerを2台登録しTaskを4件投入したところ、Attemptは2件しか作られず、いずれも同じWorkerに割り当てられた。[receipt](../evaluations/records/EKI-TEI-multi-worker-2026-11-03.json)

論点: これは2の延期の副作用であり、分散の設計判断（配置の規則、同時実行の上限）は別途必要。

TAI側でできること: 分散規則が入った後の再観測。規則の設計は製品変更。

## 4. agent資格情報の配線をプロファイル非依存にするか

観測: `SUI_AGENT_CREDENTIAL_HASH_KEY`や`SUI_AGENT_OAUTH_AUDIENCE`を設定しても、local-devプロファイルでは`app.state`へ配線されず、agent要求は503 `agent_credential_unavailable`になる。配線は`settings.runtime_profile == "saas-multitenant"`の分岐内に、guest/saas系の12項目とまとめて置かれている。[receipt](../evaluations/records/SUI-TEI-agent-key-wiring-2026-11-06.json)

当たり: `main.py`のモジュールレベルで、`if settings.runtime_profile == "saas-multitenant":`ブロックの中に`app.state.agent_credential_hash_key`等が入っている。ASTで確認した。

論点: agent資格情報をsaas限定の機能として扱い続けるのか、設定が揃っていれば他プロファイルでも有効にするのか。設定値の有無だけでは有効化を判断できないため、運用時の切り分けが難しい。

TAI側でできること: 配線変更後の再観測（local-devでagent経路が通るか）。配線の変更は製品変更。

## 5. 未知のアクセス制御adapter名をエラーにするか

観測: `SUI_ACCESS_CONTROL_ADAPTER`に未知の値を設定すると、`build_access_control_adapter`は例外にせず`NoopAccessControlAdapter`へ無言で退避する。[receipt](../evaluations/records/SUI-TEI-builders-2026-11-06.json)

当たり: `access_control.py`の`build_access_control_adapter`が、既知の4名（noop/mock/http/external_http/external）以外を`NoopAccessControlAdapter()`で返す。

論点: 綴り違いや未対応の値を、起動時に拒否するのか、現状どおりnoopへ退避するのか。noopは制御をしないアダプタなので、退避は「統制が効いていない構成」を静かに成立させる。SaaS事前検査は`access_control_adapter == "external_http"`を要求するため、SaaSでは退避が起動時に弾かれるが、single-tenantでは弾かれない。

TAI側でできること: 変更後の再観測（未知値で起動が止まるか）。値の扱いの変更は製品変更。

## 共通の注記

- いずれもTAIの接続では解消できない。TAIは再観測と記録を担う。
- 生産性・受入可否の判断には使わない（PoC完了後に評価する前提）。
- 公開gateは`allowed=false`のまま。

