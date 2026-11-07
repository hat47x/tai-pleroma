# integrations/tools

TEI投影パイロットを検証するための小さなツール群。製品のコードは各リポジトリにあり、ここは接続と検証だけを置く。

## 前提

- Goが`PATH`にあり、`GOCACHE`/`GOMODCACHE`/`TMP`が書き込み可能
- Python 3.12に`jsonschema`
- MMIのconsumerを動かすときだけNode 24と`tsx`\n- SaaS契約テストは`SUI_ADMIN_API_KEY`を必要とする。SEIの段は`--sei-repo`（または`SEI_REPO`）、MMIの段は`--mmi-repo`（または`MMI_REPO`）を使う。`--sei-repo`が無いと既定のチェックアウトを見るSUIのpytestは`SUI_*`環境変数を外して実行する
- EKIへ投入するときだけ、ビルド済みの`eki-control`
- 各製品リポジトリのパス（TEI・SUI・SEI・MMI・EKI）

## 一括検証

```text
python integrations/tools/run_suite.py \
  --tei-repo <TEI> --sui-repo <SUI> \
  --sei-schema <SEI>/contracts/schemas/v1alpha1/decision-memory.schema.json \
  --mmi-schema <MMI>/02_Architecture/format-profile-v1.schema.json \
  --eki-openapi <EKI>/spec/external/openapi.json \
  --eki-control <eki-control binary>
```

80段（checker・artifact・digest・MMIのassert/consumer/inspect/inventory/delivery・SEIのgate変種・TEI artifact複数配信・公開gateの再確認・SUI製品面8段・SaaS外部HTTP3種・ログイン開始・コールバック・token検証・SUIのSaaS/文書/認証連携/セッションテスト・SEIのCLI/gate/MCP・シナリオ・pipeline・compose・TLS・Postgres・migration・ETag・同時更新・継続競合・再試行・複数文書・レコード・EKI投入）を実行し、`evaluations/records/TEI-suite-2026-11-03.json`へ記録する。

- receipt自身をcheckerが読むため、FAILのreceiptが残っていると次の実行もFAILになる。その場合は`--skip-checker`で実行し、後からcheckerを単独で回す
- `--eki-control`・`--eki-agent`を省くとEKI投入の段は実行しない

## 個別ツール

| ツール | 用途 |
| --- | --- |
| `run_selection.py` | 1契約の生成・fixture選抜 |
| `validate_artifacts.py` | 4製品artifactのスキーマ検証 |
| `verify_artifact_digests.py` | artifactのcontractDigestを契約ファイルから再計算 |
| `check_scenario_artifacts.py` | SCN-003の識別子確認 |
| `compose_scn_003.py` | 判断・仕事・形式をSUI文書へ合成 |
| `check_determinism.py` | 単一record artifactの再生成同一性 |
| `validate_records.py` | 4製品artifactを正規レコードへ変換して検証 |
| `eki_submit_projection.py` | 投影TaskRequestを実eki-controlへ投入 |

## 注意

- Windowsでは`TMP`/`TEMP`を書き込み可能な場所へ向ける
- Goの出力はUTF-8で読む
- 選抜のreceipt名に`TEI-pilot`を含めると既存の検証規則に当たる
- 外部作用は行わない。EKI投入はTaskの受理までで、Workerは起動しない

- doc_consistency_check.py: 一括検証の段数とreceipt件数が文書と一致するかを確認する





























