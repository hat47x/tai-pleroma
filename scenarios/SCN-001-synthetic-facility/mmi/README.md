# 合成施設文書のMMI読み取り専用workspace

[合成施設文書](../README.md)のうち、MMIの既存`inspect`/`select`参照が扱うO-02/O-03/O-07の3行だけをCSV化した検証用workspaceです。

- O-06/O-08は含まない。MMI参照の選択範囲が3行に固定されているため。
- MMIの書込み・保存・実運用の認可は行わない。
- `synthetic=true`、`evidenceKind=synthetic`としてreceiptへ記録する。

## 実行

```text
go run . -workspace ../../scenarios/SCN-001-synthetic-facility/mmi -synthetic \
  -out ../../evaluations/records/SCN-001-synthetic-mmi-2026-10-29.json
```

## 境界

- 実在の施設文書ではない。
- O-02/O-03/O-07の文言差を保持することだけを確認する。
- O-06/O-08や原本未取得の扱いは[合成文書の工程検査](../README.md)で確認する。
- review statusの`accepted`や`real-object`へ読み替えない。
