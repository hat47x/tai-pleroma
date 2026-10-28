# 合成施設文書のMMI読み取り専用workspace

[合成施設文書](../README.md)のO-02/O-03/O-06/O-07/O-08をCSV化した検証用workspaceです。

- MMIの`inspect`/`select`に`Sheet1!A1:E6`を指定し、5行を取得する。
- MMIの書込み・保存・実運用の認可は行わない。
- `synthetic=true`、`evidenceKind=synthetic`としてreceiptへ記録する。

## 実行

```text
go run . -workspace ../../scenarios/SCN-001-synthetic-facility/mmi \
  -table 'Sheet1!A1:E6' -expected-rows 5 -synthetic \
  -out ../../evaluations/records/SCN-001-synthetic-mmi-2026-10-29.json
```

## 境界

- 実在の施設文書ではない。
- O-02/O-03/O-07の文言差を保持することだけを確認する。
- O-06/O-08や原本未取得の扱いは[合成文書の工程検査](../README.md)で確認する。
- review statusの`accepted`や`real-object`へ読み替えない。
