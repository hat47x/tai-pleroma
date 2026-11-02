# SCN-003 判断から仕事・形式・文書へ

Status: **提案（仮決定で進行中）**。受入判断ではない。

## 主体と目的

小さなチームが、ある選択を決め、その決定を仕事として実行し、成果を形式と文書に残したい。

- 判断した人: 選択の理由を残したい
- 実行する人: 何をどの実行条件で頼むかを受け取りたい
- 文書を読む人: 決定と結果を同じ場所で追いたい

## 前提

- 4製品の投影artifactはTAI側で生成済み
- 各製品のconsumerは読み取りのみ
- 保存・外部作用は未接続

## 入力・参照情報

| 段 | 製品 | artifact | 識別子 |
| --- | --- | --- | --- |
| 判断 | SEI | `sei-decision-projection.json` | `decision-1` |
| 仕事 | EKI | `eki-task-request-projection.json` | `dev.example.transform` |
| 形式 | MMI | `mmi-format-profile-projection.json` | `profile-a` |
| 文書 | SUI | `documentv1-projection.json` | `doc-1` |

## 期待する知的機能と成果

1. SEI: 選択と理由を平坦な判断として残す
2. EKI: その判断を実行する仕事のヘッダを写す
3. MMI: 出力の形式プロファイルを写す
4. SUI: 判断・仕事・形式を文書の要素として並べる

## 権限・承認

- 読み取りのみ。保存・実行・公開は行わない
- 製品側の権限判断を変更しない

## 観測可能な成功条件

- 4つのartifactが各自のスキーマで妥当
- 文書中に4つの識別子が現れる
- 再生成してもdigestが変わらない

## 反例

- artifactの識別子が食い違う
- 判断の理由が落ちている
- 実行条件が仕事のヘッダにない

## 検証

`integrations/tools/check_scenario_artifacts.py`で4つの識別子の存在を確認する。`integrations/tools/compose_scn_003.py`でSEIの判断・EKIの仕事・MMIの形式をSUIのカードとして合成し（5カード）、`serve_and_save.py`で一時SQLiteのSUIへ保存して往復を確認する。
