# MMI Format Profile 投影パイロット

MMIのFormat Profile v1（`02_Architecture/format-profile-v1.schema.json`）から、平坦なヘッダ部分だけをTEIで記述する参照用のパイロット。

## 範囲

- 対象: `schemaVersion`・`id`・`label`・`purpose`・`status`・`featureVersion`・`sourceProfileId`・`features`・`sourceEvidence`
- 対象外: `provenance`
- MMIのコード・API・保存へは接続していない

## 実行

```sh
python integrations/tools/run_selection.py \
  --tei-repo <TEI> \
  --workspace integrations/pilot-mmi-format-profile \
  --contract integrations/pilot-mmi-format-profile/candidates/format-profile-record/contract.json \
  --fixtures integrations/pilot-mmi-format-profile/candidates/format-profile-record/fixtures.json \
  --out evaluations/records/MMI-TEI-format-profile-selection-2026-11-03.json
```

## 結果

```text
cases: 3
passed: true
```

- [receipt](../../evaluations/records/MMI-TEI-format-profile-selection-2026-11-03.json)

## 注意

MMIの文書に出てくる「TEI」はText Encoding Initiativeを指す場合が多く、製品群のTEI（`tei-platform`）とは別です。このパイロットは`tei-platform`側の投影であり、TEI XMLの実装ではない。

## artifact（2026-11-03）

`build_artifact.py`で、fixtureの`present`からFormat Profileの投影artifactを作ります。

```text
schema: tai.reference.tei-mmi-format-profile-projection/v0
profileValid: true
cases: 3
```

- [artifact](../../evaluations/artifacts/mmi-format-profile-projection.json)
- [receipt](../../evaluations/records/MMI-TEI-artifact-2026-11-03.json)