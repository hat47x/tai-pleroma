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

`SUI_ACCESS_CONTROL_FAIL_SAFE_MODE=deny`だけを足すと、2番目が消えて5項目になる。[knob確認](../evaluations/saas-failsafe-knob-2026-11-03.json)

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
