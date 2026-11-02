# TAI → SUI API read-only probe

SUI APIの`/healthz`、`/openapi.json`、`/docs`のメタデータ一覧、任意の`/docs/{doc_id}`を読む参照です。

**SUIのテナント・認可・SCN-001データは検証しません。** 検証では一時DBに合成DocumentV1（空のものと、fixtureの5 card）をPUTしてからGETしています。

Document本文の読み取りは、明示的に`--doc-id`を指定した場合だけ行います。

## 実行

SUI APIが起動している環境で実行します。このリポジトリの検証では、WSL Ubuntu-22.04上でSUIバックエンドを起動し、`127.0.0.1:8765`へ接続しました。

```text
python -m unittest -v probe_test.py
python probe.py --base-url http://127.0.0.1:8765 --out ../../evaluations/records/SUI-api-2026-10-26.json
python probe.py --base-url http://127.0.0.1:8765 --doc-id scn001-demo --timeout 30 --out ../../evaluations/records/SUI-api-2026-10-26.json
```

`--doc-id`指定時は`/docs/{doc_id}`を読み、`documentTitle`、`documentCardCount`、`documentDigest`、各cardの`id`・`claimType`・`textDigest`、`documentIslandCount`、`documentEdgeCount`、`documentEdges`をreceiptへ追加します。生のcard本文は記録しません。

検証時の入力fixtureは[fixtures/scn001-document.json](fixtures/scn001-document.json)で、O-02/O-03/O-06/O-07/O-08の5 cardと、予約不要/必要/原本未取得の3 island、`contradicts` edgeを持ちます。検証では一時DBへPUTしてからGETしました。

## 確認すること

- `/healthz`が`{"status":"ok"}`を返す。
- `/openapi.json`が`paths`を持つ。
- `/docs`がDocumentメタデータの配列を返す。
- `openapi` version、`pathCount`、`documentCount`、`documentIds`をreceiptへ記録。
- `readOnly=true`、`realProductConnected=true`、`passed=true`。
- 追加フィールド`serverIdentity`・`pin`・`checkout`（既定は`pin.checked=false`で記録のみ）。schema文字列と既存フィールドは変えない。

保存済みrecord（2026-10-26）には`revision`がなく、どの版のSUIで得たかは未確認です。このrecordは再生成していません。

## どのサーバが応答したかを固定する（任意）

期待値を渡さない既定の実行は記録だけです。`/healthz`の前に認証不要の`GET /version`を1回読み、`serverIdentity`（`revision`・`runtimeProfile`・`openapiInfoVersion`など）へ記録します。`/version`が無い・壊れている・64KiBを超える場合も失敗にせず`status=unavailable`で続けます。到達不能なホストでは待ち時間が`/version`の分だけ増えます（`--timeout`が2回分）。サーバが返した文字列は`[A-Za-z0-9._-]{1,64}`に合う場合だけ保存します。

```text
python probe.py --base-url http://127.0.0.1:8765 --doc-id scn001-demo   --expect-revision <SUI_APP_REVISION> --expect-document-digest sha256:<hex>   [--sui-checkout <SUIチェックアウトのトップ>]
```

- `--expect-revision`（env `TAI_SUI_EXPECT_REVISION`、フラグが優先）: `/version`の`revision`との完全一致。`unknown`は使えません。
- `--expect-document-digest`（env `TAI_SUI_EXPECT_DOCUMENT_DIGEST`）: DocumentV1のdigest。`--doc-id`が必須です。digestだけの固定も可能です。
- `--sui-checkout`: そのチェックアウトのHEADと追跡ファイルの状態を記録します。固定時は期待revisionが40/64桁のcommitのときだけ照合し、HEAD一致・追跡変更なし・assume-unchanged/skip-worktreeなし・実行前後で不変を要求します。タグ形式のrevisionでは`unavailable`で失敗します。未追跡ファイルは記録のみで失敗にしません（稼働中のSUIがDBやログを作るため）。

固定実行の順序は、checkout検査 → `/version` → `/healthz` → `/openapi.json` → `/docs` →（`/docs/{id}`）→ `/version`再読 → checkout再検査です。checkout・scheme（httpとhttpsのみ）・プロキシ・revisionのどれかが外れると、以降のリクエストを送らず`passed=false`で、reasonは固定文です。固定時はリダイレクトを拒否し、HTTPプロキシ設定が適用される場合は止まります。パス・OSのエラー文は固定時のreceiptに入れません。gitは`GIT_DIR`などの環境変数を除き、`--no-replace-objects`で、indexを元のmtimeごと一時コピーして実行します（SUIチェックアウトの`.git`は変更しません）。

限界:

- `revision`は運用者が`SUI_APP_REVISION`で渡す文字列で、サーバがgitから算出した値ではありません。一致は「申告されたラベルと期待が合った」ことだけを示し、コードの同一性・SUIの正しさ・認可は示しません。`unknown`（Composeの既定）のサーバには固定できません。
- `/openapi.json`の`info.version`はFastAPIの既定値で版を識別しないため、記録のみです。
- 実行前後の`/version`の間の差し替えと戻しは防げません。ロードバランサ背後で別インスタンスが答える場合も検出できません。
- `--sui-checkout`のHEAD一致は、サーバがそのチェックアウトから起動したことを示しません。`core.fsmonitor`は無効化していますが、リポジトリの`.git/config`に`filter.*.clean`などが設定されていると`git diff`が外部コマンドを実行し得ます（残リスク。信頼できるチェックアウトにだけ使う）。
- リポジトリ側のgit設定で差分が隠れ得ます。`core.fileMode=false`では実行ビットだけの変更が、`diff.ignoreSubmodules`ではsubmoduleの変更が「追跡変更なし」になります（残リスク。`core.fileMode`の強制はWindowsの既定と食い違うため行いません）。試験が支えるのは、ステージ済み変更・`git rm --cached`・`git replace`による差し替え・実行中のHEAD移動とassume-unchanged設定・indexコピーのmtime保持までで、`GIT_*`変数ごとの除去と`-c core.fsmonitor=false`・`--no-replace-objects`以外の個別の防御は変異試験で確認していません。
- `/openapi.json`が無効な本番系プロファイルと、`X-API-Key`設定時の`/docs`は従来どおり対象外です（鍵は送りません）。
- 実SUIの`/version`の実応答は未確認です（ソース読みのみ）。

## 境界

- SUI Document本文の作成・更新はprobeでは行わない。検証用の一時DBへ空のDocumentV1を別途PUTした。
- `--doc-id`の本文読み取りは、合成fixtureの5 cardだけを対象にした。実在のSCN-001資料・実カードは未接続。
- テナント、認可、監査、本人確認は未検証。
- SCN-001の観測・仮説・DraftとSUIの意味形成は接続していない。
- `realProductConnected=true`はAPIプロセスの到達性だけを示す。固定実行の一致も、申告されたrevisionとdigestが期待と合ったことだけを示す。
