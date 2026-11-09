# TEI側の不足3件のIssue草案（2026-11-06）

状態: **草案（未投稿）**。GitHubへのIssue起票はリポジトリ外へ効果を出す操作として扱い、この作業では行っていません。判断の材料と本文をここに揃え、投稿するかどうかは別に決めます。

対象は[段階4の判断](tei-stage4-decision-2026-11-06.md)で「TAIでは解消できない」と確定した3件です。いずれもTAIは再観測と記録のみを担います。

---

## 1. 入れ子の投影フィールドを無言で捨てず、拒否するか受理するか

**提案タイトル**: `reference-generator-selection: 契約の未知フィールドを無言で捨てず、入れ子の投影を明示的に扱う`

**本文**:

`tools/reference-generator-selection`の`renderCandidateBytes`は、契約JSONを`encoding/json`の`Unmarshal`で読んでいます。`encoding/json`は既定で未知のフィールドを無視するため、`projection.fields[]`に宣言していない`fields`キー（入れ子の投影）は**エラーにならず捨てられます**。

結果として、契約には入れ子が書かれているのに、生成物は平坦なフィールドとして出力されます。契約を読んだ人は入れ子だと解釈し、生成物はそうではありません。

再現（TAIのパイロットで実測）:

```text
projection.kind に未知の値（"nested"）→ 契約検証で拒否され、生成なし
projection.fields[] に fields キー → 拒否されず、生成成功、平坦な出力
平坦な対照契約 → 従来どおり生成
```

`ProjectionField`に`fields`が無いため、`DisallowUnknownFields`を使っていない現状では、この入れ子宣言は書けるように見えて実効しません。

**論点**:

1. 未知フィールドを拒否する（`DisallowUnknownFields`を有効にする）か。既存契約に未知フィールドが混ざっていれば破壊的変更になる。
2. 入れ子の投影を正式に受理するか（`ProjectionField`に`fields`を追加し、生成テンプレートも入れ子を出力する）。
3. 拒否も受理もしない中間（現状）を許すか。黙って捨てる挙動は、契約と生成物の食い違いを生むため推奨しない。

**TAI側でできること**: 変更後の再観測（入れ子契約が明示的に拒否されるか、入れ子のまま生成されるか）。

**根拠**: [TEI-nesting receipt](../evaluations/records/TEI-nesting-2026-11-06.json)、[TEI-GAP §6](../integrations/pilot-sui-document/TEI-GAP.md)

---

## 2. `ProjectionField`の`many`が扱えるprimitiveを広げるか

**提案タイトル**: `reference-generator-selection: record投影のmanyフィールドでstd.identifier以外を扱う`

**本文**:

`validateContract`は、`many`なrecordフィールドについて`std.text`と`std.identifier`以外を拒否します（#2585 PFC-06の対応として、record templateがmanyを文字列として描画するための制約です）。

SUIのDocumentV1には、数値の配列（例: 図形の座標列）や真偽値の配列を持つ要素があります。TAIはこれらを投影せず元データを正本としていますが、入れ子投影を受理する場合や、座標列のような数値配列を投影する場合は、`many`と`std.decimal`の組み合わせが要ります。

TAIの実測（6通り、[receipt](../evaluations/records/TEI-many-primitive-2026-11-06.json)）:

```text
std.text / std.identifier の many → 受理され、生成・実行できる（[a,b] をそのまま出力）
std.decimal / std.boolean / std.integer の many → 拒否
  record field "xs": many is not supported for primitive "std.decimal" in this Target profile
std.decimal の単一（many なし）→ 受理
```

**論点**: 制約を維持するか、テンプレートをprimitiveごとの要素型に広げるか。広げる場合、生成テンプレートの変更と、既存の`std.text`/`std.identifier`の`many`が壊れないことの確認が要ります。 現状は単一の数値が通るのに配列だけが落ちるため、座標列を持つ文書は平坦な合成で表現できません。

**TAI側でできること**: 拡張後の再観測（数値配列の契約が生成・実行できるか）。

**根拠**: [TEI-many-primitive receipt](../evaluations/records/TEI-many-primitive-2026-11-06.json)、[写像の実測](../docs/sui-documentv1-tei-gap.md)

---

## 3. 生成器の契約デコードを`RenderForWorld`と`Generate`で揃えるか

**提案タイトル**: `reference-generator-selection: 契約のデコード経路を一本化する`

**本文**:

`readJSON`は`DisallowUnknownFields`を有効にしていますが、`renderCandidateBytes`は`json.Unmarshal`を直接使っています。同じ「契約を読む」処理が2つの方針で存在するため、`tei-generator-select`のように`readJSON`を通る経路では未知フィールドが拒否され、`tei-generator-build`のように`renderCandidateBytes`を通る経路では無視されます。

TAIの実測では、**同じ入れ子契約が入口によって逆の答えになりました**（[receipt](../evaluations/records/TEI-decode-divergence-2026-11-06.json)）。

```text
tei-generator-build → 受理（終了0、候補を生成。入れ子宣言は捨てられる）
tei-generator-select → 拒否（`json: unknown field "fields"`）
```

1つの契約に対して「生成できて選抜できない」状態で、どちらの入口を使ったかで未知フィールドの扱いが変わります。

**論点**: デコード方針を1つに揃えるか。揃えるならどちらへ揃えるか（拒否側か無視側か）。現状は`select`が拒否、`build`が無視で、契約の妥当性がコマンドで変わる。

**TAI側でできること**: 一本化後の再観測（同じ入れ子契約が両入口で同じ答えになるか）。

**根拠**: [TEI-decode-divergence receipt](../evaluations/records/TEI-decode-divergence-2026-11-06.json)（両入口を実測）、[TEI-nesting receipt](../evaluations/records/TEI-nesting-2026-11-06.json)

---

## 補足: #2585 として既に追跡されている2件

TAIのパイロットで、TEIの`TEI_PRODUCT_CRITICAL_PATH_2026-10.md`§34が挙げていた2つの懸念が**そのまま再現した**。どちらも#2585で追跡されているため、新しいIssueにはしない。

| 現象 | TAIでの実測 |
| --- | --- |
| 十進値の`float64`経由の精度喪失 | `0.1234567890123456789` → `0.12345678901234568`、`12345678901234567890` → `12345678901234567000`（[receipt](../evaluations/records/TEI-decimal-fidelity-2026-11-06.json)） |
| `optional`のmissing/null同一省略 | JSONの`null`が「省略」に畳まれ、`missing`との区別が付かない（[receipt](../evaluations/records/TEI-meaning-change-requiredness-2026-11-06.json)） |

TAI側の意味は「生成成功≠型付き意味保持」である。金額のように丸めを許さない値を持つ契約は、#2585の判断が出るまで`std.decimal`で投影しない。

## 4. 投影の生成戦略がprocess modelに対応していない

**提案タイトル**: `reference-generator-selection: 投影の生成戦略をTarget Profileのprocess modelに対応させる`

**本文**:

同じ受理済み契約・fixture・生成候補を、one-shotとlong-runningの2つのTarget Profileで実行しました（[record](../evaluations/records/TEI-target-profile-compare-2026-11-06.json)、[text](../evaluations/records/TEI-target-profile-compare-text-2026-11-06.json)）。

```text
sui-record-oneshot  (oneshot)      → PASS  5プロセス・5リクエスト・5応答
sui-record-rolling  (long-running) → FAIL  1プロセス・5リクエスト・1応答  candidate wait failed: exit status 2
sui-text-oneshot    (oneshot)      → PASS  4プロセス・4リクエスト・4応答
sui-text-rolling    (long-running) → FAIL  1プロセス・4リクエスト・1応答  candidate returned 1 of 4 responses
```

`text-template`と`text-record-template`の両方で同じ非対称が出ました。生成されるプログラムは標準入力から1件読んで1件返して終わるため、1プロセスに複数リクエストを送るlong-runningプロファイルでは2件目以降に応答できません。

原因をさらに特定しました（[receipt](../evaluations/records/TEI-projection-strategy-2026-11-06.json)）。TEIにはlong-running用のテンプレート（`template-long-running.go.tmpl`など）がありますが、**`projection: true`の戦略は`text-template`と`text-record-template`の2つだけ**で、どちらもone-shotです。投影契約にlong-running用の戦略を渡すと生成器が拒否します。

```text
projection kind "record" + long-running-template
→ projection kind "record" requires the text-record-template strategy
```

**「long-runningが無い」のではなく、「long-runningで動く投影の生成戦略が無い」**ということです。

**TEI側の試験と文書にも、この組み合わせを扱った記述はありません。** 2026-11-06時点の`tei-wt-r2`（`2d0b09b13`）で次を検索し、いずれも0件でした。

| 対象 | 検索 | 結果 |
| --- | --- | --- |
| `*_test.go`（1629件） | `projection.*oneshot`、`oneshot.*projection`、`projection.*long-running`、`long-running.*projection` | 0件 |
| `docs/`・`plan/`の`*.md` | 同上（単語間の任意語を許す形） | 0件 |

つまり、この結合はコードの中に暗黙にあり、試験でも文書でも宣言されていません。**意図的な制約として文書化されているわけではない**ので、「設計どおりか」ではなく「組み合わせが検証されていない」という論点として扱うのが正確です。

**論点**:

1. 生成テンプレートをprocess modelごとに用意するか（one-shot用とlong-running用で別のmainを生成する）。
2. Target Profileの`processModel`宣言を、生成候補の実行モデルと突き合わせて検証するか（今は実行時に初めて分かる）。
3. long-runningを「未対応」として明示し、対応するまでProfile側で拒否するか。

TAIの立場では、これは「実行先が交換できる」の反例です。同じ意味でも実行モデルが変われば候補の作り直しが要り、意味の検証だけを引き継ぐことはできません。TAIは下流に回避実装を足さず、判断待ちとします。

**TAI側でできること**: 対応後の再観測（同じ契約が両Profileで通るか）。

**根拠**: [record比較](../evaluations/records/TEI-target-profile-compare-2026-11-06.json)、[text比較](../evaluations/records/TEI-target-profile-compare-text-2026-11-06.json)

---

## 投稿する場合の手順（未実施）

1. 各草案をTEIリポジトリ（`hat47x/tei-platform`）へ1件ずつIssueとして起票する。
2. 2と3は、1の判断（拒否か受理か）に従属する。1を先に投稿し、2・3はその決定に合わせて調整する。4は独立して投稿できる。
3. TAI側は、判断が下りたら同じパイロットで再観測しreceiptを追加する。

この手順は外部への効果を含むため、実行の可否は人（Owner）の判断に委ねます。
