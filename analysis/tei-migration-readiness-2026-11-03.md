# TEI構築への移行準備 — リポジトリ別の棚卸し

2026-11-03時点。`D:\GIT\hat47x`配下の各リポジトリの作業ツリーを対象に、`.tei`ファイルと`contract.json`の数を数えた。

## 方法

- 対象: `tei-platform`、`sui-sensemaking`、`sei-cognition`、`eki-fabric`、`markdown-matrix-injector`、`tai-pleroma`
- `.tei`はTEIのセマンティックモデル、`contract.json`は参照生成器の契約
- 数え方は拡張子ベース。製品が持つPydantic/TypeScriptのドメインモデルは含まない
- 各リポジトリのメイン作業ツリーのみ。派生worktreeは含まない

## 結果

| リポジトリ | `.tei` | `contract.json` |
| --- | ---: | ---: |
| tei-platform | 99 | 5 |
| tai-pleroma | 8 | 7 |
| sui-sensemaking | 0 | 0 |
| sei-cognition | 0 | 0 |
| eki-fabric | 0 | 0 |
| markdown-matrix-injector | 0 | 0 |

## 読み取り

- TEI自身は`.tei`で自己記述されている
- TAIにはSUI向けのパイロット投影（`integrations/pilot-sui-document/semantic/sui/document.tei`）と契約がある
- SUI・SEI・EKI・MMIのリポジトリには`.tei`も参照契約もまだない`n- TAI側にはSEI Decisionの参照パイロット（`integrations/pilot-sei-decision`）を追加した。SEI本体は未変更`n- TAI側にはMMI Format Profileの参照パイロット（`integrations/pilot-mmi-format-profile`）も追加した。MMI本体は未変更
- したがって、これら4製品のTEIによる構築は、現時点では**未着手**に近い
- TAIのSUIパイロットは、製品側のドメインモデルを写した参照実装であり、製品の構築手段がTEIへ移ったわけではない

`.tei`がないことは、ドメインモデルがないことを意味しない。各製品は独自のPydanticモデルやTypeScript型を持っている。棚卸しは「TEIで記述されているか」だけを見ている。

## 移行の単位

製品ごとに、次の順で薄い縦断を作るのが妥当と考えられる。

1. 製品のドメインモデルから、中心となる要素を1つ選ぶ
2. その要素を`.tei`で記述する
3. 参照生成器の契約とfixtureを作る
4. 生成物を製品の型へ変換し、読み取りで検証する
5. 保存経路は、読み取りの検証が通ってから扱う

SUIのDocumentV1で言えば、Document/Card/Island/Edge/Affiliationの投影と読み取り・保存までがこの形で通っている。次にTEI化する製品は、同じ形を一度なぞるのが早い。

## 未確認

- 各製品のドメインモデルのうち、どれがTEIのprimitiveで表せるか
- 製品側のビルド・テスト環境でTEI生成物をどう扱うか
- TEIのセマンティックモデルを製品リポジトリへ置くか、TAI側に置くか

## 次の候補

1. SUIの投影セマンティックモデルを、TAIのパイロットからSUIリポジトリへ移すか決める
2. SEI・EKI・MMIのうち1製品で、最小の`.tei`記述と契約を作る
3. 製品ごとのドメインモデルとTEI primitiveの対応表を作る

公開gateは`blocked`のまま。外部作用・公開は未承認。

## SEIの既存TEI接続（誤読防止）

SEIにはすでにTEIとの接続がある。`runtime/go/teiintegration`がTEI executableを呼び、`deployment-provider-plan`をcapability observationへ写す。これはProvider計画の取得であり、Decision Memoryの投影とは役割が違う。

- `.tei`がSEIリポジトリにないことは、TEI未接続を意味しない
- TAIの`pilot-sei-decision`はDecisionの投影であり、`teiintegration`を置き換えない
- 将来SEIへ投影のconsumerを足すなら、`teiintegration`とは別パッケージにする

この整理は重複実装を避けるためのもので、SEIの設計判断を変更しない。
## EKIとMMIの注意点

EKIは`conformance/productboundary`で、製品コードがSEI・TEIへ依存しないことを確かめている。EKIの投影パイロットを作る場合も、製品コードへ`tei-platform`への依存や語彙を持ち込まず、TAI側の`integrations/`に置く。

MMIの文書に出てくる「TEI」は、Text Encoding Initiative（TEI XML）を指す場合が多い。製品群のTEI（`tei-platform`）とは別物なので、検索結果をそのまま接続の証拠にしない。