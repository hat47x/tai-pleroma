# 再観測の準備（2026-11-06）

[判定](../analysis/tei-pilot-conclusion-2026-11-06.md)で「未達」の理由を条件ごとに分けた。この文書は、**判断が下りたときに何を測り直すか**を、そのまま実行できる形で並べる。

TAIは範囲を広げない。判断が来たら、下のコマンドを回してreceiptを足し、判定表を1行だけ書き換える。

## 1. TEI側3論点

### 1-a. 投影戦略がprocess modelに対応したとき

```powershell
python integrations/tools/tei_projection_strategy_probe.py `
  --tei-repo <TEI> --workspace integrations/pilot-sui-document `
  --artifact evaluations/artifacts/scn-003-document.json `
  --out evaluations/records/TEI-projection-strategy-2026-11-06.json

python integrations/tools/tei_target_profile_compare.py `
  --tei-repo <TEI> --workspace integrations/pilot-sui-document `
  --artifact evaluations/artifacts/scn-003-document.json `
  --out evaluations/records/TEI-target-profile-compare-2026-11-06.json
```

- いまの期待値: 投影契約＋long-running戦略は拒否、one-shotは受理
- **変わる条件**: 1つ目の出力で`projectionIsPinnedToOneShotStrategy`が`false`になったら、2つ目で`longRunningRefused`が`false`になるかを確かめる
- 判定への効き方: 条件3「実行先が交換できる」が**部分→達成**になり得る

### 1-b. デコード方針が決まったとき

```powershell
python integrations/tools/tei_contract_decode_probe.py `
  --tei-repo <TEI> --workspace integrations/pilot-sui-document `
  --artifact evaluations/artifacts/scn-003-document.json `
  --out evaluations/records/TEI-decode-divergence-2026-11-06.json
```

- いまの期待値: `build`は受理（平坦化）、`select`は`unknown field`で拒否（`prefixDistinguishable: true`）
- **変わる条件**: `prefixDistinguishable`が`false`になったら、両入口が同じ答えになったということ。そのうえで入れ子契約を**受理するのか拒否するのか**を確かめる（受理なら投影の作り直し、拒否なら現行の平坦方式が正式になる）
- 判定への効き方: 「意味が正本」の**部分**が動く。受理された場合は、文書全体を1つの意味で表せるかをもう一度測る

### 1-c. 数値・真偽値の配列が扱えるようになったとき

```powershell
python integrations/tools/tei_many_primitive_probe.py `
  --tei-repo <TEI> --artifact evaluations/artifacts/scn-003-document.json `
  --out evaluations/records/TEI-many-primitive-2026-11-06.json
```

- いまの期待値: `std.text`/`std.identifier`のみ受理、`std.decimal`/`std.boolean`/`std.integer`は拒否
- **変わる条件**: `numericManyRefused`が`false`になったら、数値配列の投影契約を1つ作り、座標列のような値を実際に通す
- 判定への効き方: 直接は左右しない（拡張）。ただし座標列を持つ文書を扱えるようになる

## 2. 製品側の実施項目

### 2-a. RAC-1が本番経路へ配線されたとき

```powershell
python integrations/tools/eki_manual_execution.py
```

- いまの期待値: `409 RESULT_NOT_READY`（`internal/control/resultacceptance`を呼ぶ経路が無い）
- **変わる条件**: Task→実行→受入→結果参照が1回の縦断で通るか
- 記録: 通った場合も、受理の根拠（検証証拠・方針・独立性）が誰のものかをreceiptへ書く

### 2-b. `enforce_access`が`decision.read_only`を見るようになったとき

```powershell
python integrations/pilot-sui-document/assembler/agent_key_wiring_check.py --sui-repo <SUI>
```

- いまの期待値: 既定構成では到達しない（noopは素の`allow`を返す）
- **変わる条件**: `allow=True, read_only=True`を返すスタブアダプターを構成し、`write`が403になるか
- 注意: **このためのスタブはTAI側にまだ無い**。実行するには先にスタブを作る（下の「作業の予約」）

## 3. 環境が用意されたとき（条件5）

実IdP、実管理DB、公開CA、実逆プロキシ、複数ホストのいずれかが使えるようになったら、[再現手順](reproduction-runbook.md)§6の「再現できないもの」から1つを外し、その手順を追加する。**外した項目だけ**をreceiptにする。

## 4. 作業の予約（判断を待たずにできる準備）

| 準備 | 状態 |
| --- | --- |
| 各Probeの実行コマンドと期待値 | 本文書に記載済み |
| `allow+read_only`を返すスタブアダプター | **作成済み**（[receipt](../evaluations/records/SUI-readonly-enforcement-2026-11-06.json)）。`enforce_access`が`decision.read_only`を見ないことを実行で確認した |
| 入れ子契約を受理する版の試作 | 未作成。受理された場合に備え、Document全体を1つのrecordで表す契約を試作できる（現行は平坦方式） |
| 数値配列の投影契約の試作 | 未作成。`many`拡張後すぐ試せるよう、座標列の契約を用意できる |

スタブアダプターは作った（実行で確かめられたため）。残る2件（入れ子契約・数値配列契約の試作）は、**判断が来てから**作る。判定は変わらないため、先に作ると使われない試作が増える。
