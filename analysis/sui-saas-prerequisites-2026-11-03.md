# SUI SaaSプロファイルの前提

2026-11-03時点。`SUI_RUNTIME_PROFILE=saas-multitenant`で起動するために足りない設定を、コードと実行で確認した結果。受入判断ではない。

## 実行で確認したこと

埋め込みPostgresを`alembic upgrade head`で初期化し、APIキーと管理者キーを設定しても、起動は次の6項目で止まる。

1. external access control
2. deny fail-safe mode
3. external document policy binding
4. external tenant capability resolution
5. SaaS OAuth broker authorize endpoint configured
6. SaaS auth-session hash key configured

`SUI_ACCESS_CONTROL_FAIL_SAFE_MODE=deny`だけを足すと、2番目が消えて5項目になる。[knob確認](../evaluations/saas-failsafe-knob-2026-11-03.json)`n`n6項目すべてに値を入れる（外部HTTP先は未実装のURL）と、SaaSプロファイルで起動し、未認証のリクエストは401になった。[stub起動](../evaluations/saas-stub-startup-2026-11-03.json)`n`n値が欠けた状態では、実行によって拒否（6項目の列挙）または30秒無応答のいずれかになった。環境や順序に依存する可能性がある。

## 設定の対応表

| 要件 | 設定 | 期待値 | 現状 |
| --- | --- | --- | --- |
| PostgreSQL tenant DB guard | `SUI_DATABASE_URL` | `postgresql://...` | 充足（埋め込みPostgres） |
| disabled JIT provisioning | `SUI_ALLOW_JIT_PROVISIONING` | `false` | 既定で充足 |
| deny fail-safe mode | `SUI_ACCESS_CONTROL_FAIL_SAFE_MODE` | `deny` | 設定すると1項目消える |
| external access control | `SUI_ACCESS_CONTROL_ADAPTER` | `external_http` | 未設定。HTTP先も必要 |
| external document policy binding | `SUI_DOCUMENT_POLICY_BINDING_RESOLVER` | `external_http` | 未設定。HTTP先も必要 |
| external tenant capability resolution | `SUI_TENANT_CAPABILITY_RESOLVER` | `external_http` | 未設定。HTTP先も必要 |
| SaaS OAuth broker | `SUI_SAAS_OAUTH_BROKER_HTTP_AUTHORIZE_ENDPOINT`ほか | 実在するエンドポイント | 未設定 |
| SaaS auth-session hash key | `SUI_SAAS_AUTH_SESSION_HASH_KEY` | 十分な長さの鍵 | 未設定 |

external系のHTTP先には、それぞれ次の設定がある。

- access control: `SUI_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT`・`..._AUTH_MODE`・`..._STATIC_BEARER_TOKEN`など
- document policy binding: `SUI_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT`・`..._API_KEY`
- tenant capability: `SUI_TENANT_CAPABILITY_HTTP_ENDPOINT`・`..._API_KEY`

## 意味

6項目のうち2つ（Postgres・JIT）は既に満たせる。残り4つは外部の認証・ポリシー・capabilityのHTTP先か、OAuth brokerと鍵の用意が要る。ローカルのstubで形だけ満たすことはできるが、それは実認証の証明にならない。

## 未確認

- stubで起動を通した場合の挙動
- 実OAuth broker・実ポリシーサーバとの接続
- 管理DB・TLS・配備

## 外部HTTPの契約（コードから抽出）

実装済みのアダプタが送受信する形。実サーバは未接続で、以下はコードの読み取りに基づく。

### access control（`access_control.py`）

POST。ヘッダは`content-type: application/json`、`x-acl-auth-mode`、必要に応じて`x-trace-id`・`x-idp-issuer`・`Authorization: Bearer ...`。

```json
{
  "action": "read",
  "auth": {"actorRef": "...", "roles": [], "groups": [], "userId": "..."},
  "resource": {"docId": "...", "visibility": "Org", "policyRef": "...", "tenantId": "...", "kind": "document"},
  "safeMode": true,
  "readOnly": false,
  "tenant": {"tenantId": "...", "membershipId": "...", "resolvedBy": "..."}
}
```

応答は`allow`（真偽値）を含むJSONで、`readOnly`・`reason`などを任意で持つ。400/401/403/422は拒否、その他は再試行可能な失敗として扱われる。

### document policy binding（`document_policy_binding.py`）

POST。

```json
{"tenantId": "...", "bindingId": "...", "policyVersion": "..."}
```

応答は`{"policyRef": "..."}`のみ。

### tenant capability（`tenant_capability.py`）

POST。

```json
{"principalId": "...", "tenantId": "...", "membershipId": "..."}
```

応答は`effectiveCapabilities`と`capabilityVersion`のみ。

### OAuth broker

`SUI_SAAS_OAUTH_BROKER_HTTP_AUTHORIZE_ENDPOINT`などの設定名のみ確認済みで、要求・応答の形は未確認。