# TEI構築パイロット 段階4の判断記録（2026-11-06）

状態: **AIによる暫定意思決定**。Owner判断ではありません。計画[tei-construction-migration-plan.md](../docs/tei-construction-migration-plan.md)の段階表における段階4「次の範囲へ広げるか、TEI側の不足を先に埋めるか」への回答を、証拠付きで記録します。

## 1. 判断の対象

段階3までの到達点は次のとおりです（同日時点の実実行receiptに基づく）。

| 段階 | 到達点 | 主なreceipt |
| --- | --- | --- |
| 1 | SUIの対象範囲を三視点で記述 | [gap](../docs/sui-documentv1-tei-gap.md)、[boundary](../docs/sui-api-boundary-tei-mapping.md) |
| 2 | 契約→生成→4ケース選抜→one-shot Target Profile実行→rolling配備・rollback | [text-generation](../evaluations/records/SUI-TEI-text-generation-2026-11-01.json)、[target](../evaluations/records/SUI-TEI-target-2026-11-01.json)、[deploy](../evaluations/records/SUI-TEI-deploy-2026-11-02.json) |
| 2 | Card/Island/Edge/Documentのflat record投影と合成（入れ子は未達） | [card-record](../evaluations/records/SUI-TEI-card-record-2026-11-02.json)、[island-edge](../evaluations/records/SUI-TEI-island-edge-2026-11-02.json)、[document](../evaluations/records/SUI-TEI-document-record-2026-11-02.json)、[assembler](../evaluations/records/SUI-TEI-assembler-2026-11-02.json) |
| 2 | 直接実行したSUIの製品面（保存・認可・監査・管理・context・CE4） | [suite](../evaluations/records/TEI-suite-2026-11-03.json)（82段、全PASS） |
| 3 | 工程の測定と小さな比較（生産性の評価は完成後） | [workflow](../evaluations/records/SUI-TEI-workflow-2026-11-02.json)、[compare](../evaluations/records/SUI-TEI-compare-2026-11-02.json) |

段階2の出口条件のうち、**入れ子投影だけが未達**です。Document全体はflat recordの合成で表し、合成層と結合経路の試験を通しています。

## 2. 残っている不足の分類

不足を「TEI側で埋めるもの」と「製品側の判断が要るもの」と「実インフラが要るもの」に分けます。

### 2.1 TEI側の不足

| 不足 | 影響 | 現状 |
| --- | --- | --- |
| 入れ子投影（配列の配列、構造体の配列） | 契約で複合構造を表現できず、Document全体を1つのrecordで表せない。**さらに、入れ子の`fields`を書いた契約は拒否されず、無言で平坦化されて生成される**（[probe](../evaluations/records/TEI-nesting-2026-11-06.json)） | flat recordの合成で回避中。[gap](../docs/sui-documentv1-tei-gap.md) |
| 統合モデラー・編集環境 | 意味の変更をGUI/対話で行えず、意味の正本を手で編集している | TEI statusで未完成と記載 |
| Target Profileの種類 | one-shotとrollingの2種のみ確認。実OS・実配備の差分は未確認 | [target](../evaluations/records/SUI-TEI-target-2026-11-01.json) |
| 証拠の束縛の範囲 | 生成器・成果物・契約のdigestは記録できるが、生成AIの入力文脈は記録していない | [contract-digest](../evaluations/records/SUI-TEI-contract-digest-2026-11-03.json) |

### 2.2 製品側の判断が要るもの

[product-side-decisions-2026-11-06.md](product-side-decisions-2026-11-06.md)の6項目です。

1. 実行結果の受入をEKI Control Planeへ配線するか
2. `NOT_YET_VALID`の時刻順序を計測・修正するか
3. 複数Workerの割り当てを分散させるか
4. agent資格情報の配線をプロファイル非依存にするか
5. 未知のアクセス制御adapter名をエラーにするか
6. 呼び出し側の`read_only`を読み取りの決定へ伝播させるか

### 2.3 実インフラが要るもの

実IdP、管理DB、公開CA、実リバースプロキシ、複数ホスト配備。[sui-saas-prerequisites-2026-11-03.md](sui-saas-prerequisites-2026-11-03.md)に整理済み。

## 3. 判断

**段階4では、次の範囲へ広げるのではなく、TEI側の不足のうち「入れ子投影」を先に埋める経路を選び、並行して製品側の6判断をIssueへ渡せる形に整えます。**

理由:

- 段階2の出口条件のうち未達は入れ子投影だけであり、ここを埋めると段階2が完了する。範囲を広げる前に出口条件を満たすのが計画の趣旨に沿う。
- 統合モデラーはTEIの製品側作業であり、TAIの接続からは埋められない。入れ子投影は契約表現の問題として、TAIのパイロットで検証できる余地がある。
- 製品側の6判断は、TAIが代行できない。判断記録を整え、Issueへ渡せる状態にしておくことで、判断が下りた後の再観測をすぐ行える。
- 実インフラは利用可能になるまで待つしかなく、待つ間にできる作業を先に進める。

## 4. 見直し条件

- TEI側が入れ子投影を別の形（統合モデラー側の表現）で解決したとき
- 製品側の6判断のいずれかが下りたとき（下りた項目から再観測する）
- 実インフラが利用可能になったとき（配備検証を優先する）
- 段階2の入れ子投影が、TAIの接続では解消できないと判明したとき（TEI側へIssueで戻す）

## 5. この判断が拠らないもの

- 生産性・自律性の評価。PoC完了後に測る（仮決定）。
- 公開可否。公開gateは`allowed=false`のまま。
- 意味の正しさ、業務上の受入。いずれも人と製品の判断。

## 6. 次の作業と結果（2026-11-06）

判断の後に実行し、結果が判断を変えるかを確かめた。

| 作業 | 結果 | 判断への影響 |
| --- | --- | --- |
| 入れ子投影の契約表現を試作 | **入れ子の`fields`は拒否されず、無言で平坦化されて生成された**（[probe](../evaluations/records/TEI-nesting-2026-11-06.json)） | 入れ子はTAIでは解消できない。TEI側へ戻す条件に当たる |
| 製品側6判断をIssue粒度に要約 | 6件の草案を作成（[草案](product-side-decisions-issue-drafts-2026-11-06.md)） | 起票は外部作用のため未実施。判断待ちのまま |
| 写像率の実測（名前） | DocumentV1 0.125 / Card 0.5 / Island 0.15 / Edge 1.0（[coverage](../evaluations/records/SUI-TEI-document-coverage-2026-11-06.json)） | 段階2の未達が入れ子だけであることを裏づけ |
| 型・必須性の一致 | primitiveの不一致なし。`Edge.fromKind`/`toKind`はSUIが任意・契約が必須（[types](../evaluations/records/SUI-TEI-document-types-2026-11-06.json)） | 新たな不足を1件追加 |
| 端点種別を持たないEdgeの投影 | `missing`/`unresolved`で落ち、投影されない（[edge](../evaluations/records/SUI-TEI-edge-optionality-2026-11-06.json)） | 上記の不足の影響を確定 |
| 合成層の端点種別の仮定 | 欠落時に`card`を仮定して解決し、出力には種別が残らない（[assembler](../evaluations/records/SUI-TEI-assembler-kinds-2026-11-06.json)） | 契約と合成層の不一致を追加 |

### 結果を踏まえた判断の修正

1. **入れ子投影はTAIで解消できないことを確定する。** 契約のデコードが未知フィールドを無視するため、TAI側からは「拒否させる」ことも「受理させる」こともできない。TEI側の変更が要る。
2. **TEI側の不足は3件になった**: 入れ子投影の受理（または明示的な拒否）、`Edge.fromKind`/`toKind`の任意性の扱い、端点種別の必須性を契約と合成層で揃えること。
3. 段階4の作業は、これ以上TEI側へ踏み込まず、次の2つに絞る: (a) TEI側3件の判断材料を整える、(b) 製品側6判断の材料を整える。いずれも起票は外部作用のため行わない。

`Edge.fromKind`/`toKind`の任意性と合成層の仮定は、**TEIの契約表現ではなくTAIのパイロット側の設計**でもある。製品のDocumentV1が端点種別を任意にしている以上、契約側を任意に寄せる選択肢があり、それはTAI側で試せる。**試作の結果、任意にした契約は受理され、種別なしのEdgeを省略付きで投影できた**（[receipt](../evaluations/records/SUI-TEI-edge-optional-contract-2026-11-06.json)）。端点種別の欠落はTEI側ではなく契約側で解ける。残る論点は合成層が種別なしをどう扱うかだけである。
