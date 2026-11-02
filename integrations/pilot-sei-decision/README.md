# SEI Decision 投影パイロット

SEIのDecision Memory（`sei.decision-memory/v1alpha1`）から、平坦に投影できる部分だけをTEIで記述する参照用のパイロット。

## 範囲

- 対象: Decisionの`contract`・`record_type`・`ref.kind`・`ref.id`・`statement`・`rationale`
- 対象外: `context_refs`などの参照配列、`lineage`、`extensions`
- SEIのコード・API・保存経路へは接続していない

## 実行

```sh
python integrations/tools/run_selection.py \
  --tei-repo <TEI> \
  --workspace integrations/pilot-sei-decision \
  --contract integrations/pilot-sei-decision/candidates/decision-record/contract.json \
  --fixtures integrations/pilot-sei-decision/candidates/decision-record/fixtures.json \
  --out evaluations/records/SEI-TEI-decision-selection-2026-11-03.json
```

## 結果

```text
cases: 4
passed: true
```

- [receipt](../../evaluations/records/SEI-TEI-decision-selection-2026-11-03.json)
- 生成戦略: `text-record-template`
- 一時ディレクトリを使うため、Windowsでは`TMP`/`TEMP`を書ける場所へ向ける

## 未確認

- SEIの実データ・実スキーマとの突き合わせ
- 参照配列の投影
- SEI側のconsumer・保存
