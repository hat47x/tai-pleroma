# 合成バリエーションのプロセス検査

SCN-001の合成文書を、構成の異なる2変種へ広げ、MMIとTEIの参照実装が入力差を扱えるかを確認します。

## 変種

- `variant-b`: 本館と別館で予約条件が異なる。適用範囲の差を保持する。
- `variant-c`: 全館予約制と旧掲示の差。版の差を保持する。

各変種は5行の`observations.csv`と、`Building`/`RoomPolicy`または`PolicyVersion`/`Notice`/`Conflict`型を持つTEI workspaceです。

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

## 境界

- 合成入力です。実在の施設・規程ではありません。
- MMIの読み取りとTEIの型検証だけを確認します。意味の受理・公開承認ではありません。
- 公開gateはblockedのままです。
