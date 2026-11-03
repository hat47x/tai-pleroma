# EKI TaskRequest 投影パイロット

EKIの公開契約`eki.task-request/v1`（`spec/external/openapi.json`）から、平坦なヘッダ部分だけをTEIで記述する参照用のパイロット。

## 範囲

- 対象: `schema`・`executor.id`・`executor.version_constraint`・`priority`・`client_request_id`
- 対象: `resources`の5項目と`reliability`の6項目も平坦な値として投影（`inputs`は空配列、`parameters`は空オブジェクトとして再構成）`n- 対象外: `inputs`の要素・`extensions`
- EKIのコード・APIへは接続していない

## EKIの既存Spikeとの違い

EKIには`spikes/tei-workload-projection`があり、TEIの仕事をEKIのTaskRequestへ投影する。依存の向きはTEI → EKI。このパイロットは逆向きで、EKIの公開契約をTEIで記述する。名前も範囲も別。

## 実行

```sh
python integrations/tools/run_selection.py \
  --tei-repo <TEI> \
  --workspace integrations/pilot-eki-task-request \
  --contract integrations/pilot-eki-task-request/candidates/task-request-record/contract.json \
  --fixtures integrations/pilot-eki-task-request/candidates/task-request-record/fixtures.json \
  --out evaluations/records/EKI-TEI-task-request-selection-2026-11-03.json
```

## 結果

```text
cases: 4
passed: true
```

- [receipt](../../evaluations/records/EKI-TEI-task-request-selection-2026-11-03.json)

## artifact（2026-11-03）

`build_artifact.py`で、fixtureの`present`からTaskRequestの投影artifactを作ります。

```text
schema: tai.reference.tei-eki-task-request-projection/v0
taskRequestValid: true
cases: 4
```

- [artifact](../../evaluations/artifacts/eki-task-request-projection.json)
- [receipt](../../evaluations/records/EKI-TEI-artifact-2026-11-03.json)