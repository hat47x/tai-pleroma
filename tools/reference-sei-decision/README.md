# TAI → SEI decision-memory reference

SCN-001の`DEC-01`を、SEIの一時storeへ合成fixtureとして記録し、`sei resume --json`のprojectionだけを読む参照接続です。

確認するのは、決定がrecommendationに依拠し、`authority:unknown`を未解決として残し、公開・承認済みと扱わないことです。

**実運用のstore・権限・公開を検証しません。** 合成fixtureをSEIの一時storeへ記録するため、SEIの`init`/`add`を使ってから`resume`を読みます。

## 実行

SEIの開発チェックアウトとGoが必要です。

```text
go test ./...
go run . -sei-root ../../../sei-cognition
```

`SEI_ROOT`でも指定できます。SEIのcheckout（`SEI_ROOT`または既定の`../../../sei-cognition`）があると、実SEIの`go run ./cmd/sei`を何度も呼ぶ統合試験も走り、負荷によっては`go test`の既定の10分を超えます。その場合は`go test -timeout 30m ./...`で実行してください。checkoutがない環境（CI）では、統合試験は省かれます。

`validity_cli_test.go`は、構造検査をしない偽の`sei verify`を一時ディレクトリに置き、ビルドした実行体の成功経路（フラグの受け渡し、`-out`、exit code）だけを確認します。実SEIの構造検査の代わりではありません。

合成バリエーションは`-variant b`または`-variant c`で記録できます。

```text
go run . -sei-root ../../../sei-cognition -variant b -synthetic -out variant-b.json
```

## 確認すること

- `sei init`で一時storeを作る。
- `rec-01`をrecommendationとして記録する。
- `dec-01`をdecisionとして記録し、`rec-01`へ依拠し、`authority:unknown`を未解決に残す。
- `dec-02`をdevelopment-review-onlyの仮承認として記録し、`publication:unapproved`も未解決に残す。
- `sei resume --json`で3 records、`dec-01`/`dec-02`、未解決`authority:unknown`/`publication:unapproved`を確認。
- receiptは`provisionalApproved=true`、`authorityVerified=false`、`humanReviewed=false`、`published=false`。
- `-synthetic`指定時は`synthetic=true`、`evidenceKind=synthetic`。実物レビューの証拠ではない。

## 境界

- storeは一時ディレクトリで、終了時に削除する。実在の規程・権限・利用者ではない。
- `resume`はprojectionであり、決定の意味・正しさ・Authorityを証明しない。
- `readOnlyProjection=true`は`resume`の読み取りだけを示し、SEI全体の読取専用を意味しない。
- 実運用の監査、複数利用者、署名、公開は未検証。

## 原記録の根拠参照を読む

`resume`は表示用の一覧であり、ExactBindingのscope・digest・表現profileを同じ形で返すものではありません。原記録を確認する場合は、SEIの既存`export`で取得したportable bundleを、次のモードで読みます。

```text
go run . -sei-root ../../../sei-cognition -basis-bundle review-bundle.json -out basis-inspection.json
```

このモードは`init`/`add`を呼びません。入力のbyte列を一時snapshotとして固定し、同じsnapshotについて既存の`sei verify --input`と参照抽出を行います。入力全体の`sourceDigest`、元record ID、元記録内の`jsonPointer`、Decisionの論理参照、`basis_refs`の各項目と値を返します。参照をkind:idだけに縮めず、論理参照とExactBindingの両方を保持します。出力JSONの空白・エスケープ等は再符号化されるため、断片の元byte列の保存を意味しません。

- 認識した`sei.decision-memory/v1alpha1`のDecisionだけを抽出します。未認識Contractは意味を解釈せず、`notVerifiedRecordCount`で残します。抽出0件を「元案件に判断がない」と読み替えません。
- 同じDecision論理IDが複数のrecordにあっても、record IDと元の位置で別々に返します。
- `recordStructureChecked=true`はSEIの構造検査が成功したことだけを示します。`exactTargetsVerified`・`humanReviewed`・`authorityVerified`・`publicationApproved`はすべてfalseです。
- `-out`は既存ファイルを上書きしません。入力と同じパスや、その別名を指定しても、既存ファイルのまま失敗します。
- 不正なUTF-8、同名JSON項目、末尾の追加データを拒否します。値を置換文字で補いません。case foldingで同名になる項目も拒否するため、この診断の受入範囲はSEI本体より狭く、拒否はSEI Contract違反の判定ではありません。

出力は原記録へ戻るための参照資料です。新しい製品間Contractや状態の正本ではありません。参照先の内容・現行性・署名・権限は検証せず、受理の継続・失効・再受理も決めません。既定のSCN-001一時storeによる実行と、そのreceiptは変更しません。旧い判断の構造上の束縛だけは、次節の`-decision-validity`で別に調べます。これも受理の継続・失効の判断ではありません。

## 旧い判断が現行対象へ構造上束縛されるかを調べる

```text
go run . -sei-root ../../../sei-cognition \
  -decision-validity review-bundle.json \
  -current-target current-target.json \
  -decision decision:dec-accept-1 \
  -out validity.json
```

合成のportable bundleだけを対象にした構造検査です。`init`/`add`は呼びません。

- `-decision-validity`: portable bundle。`-basis-bundle`と同じく、読んだbyte列の同じsnapshotをSEIの`verify --input`で検査し、失敗したら報告を作りません（exit 1）。不正なUTF-8、同名JSON項目（case foldingを含む）、末尾の追加データも拒否します。
- `-current-target`: 現行対象のExactBinding（`logical_ref`・`content_digest`・`representation_profile`）1件のJSON。呼出し側が渡す値で、実在・最新性・digestの再計算は検証しません（出力は`currentTargetSource=caller-supplied`）。
- `-decision kind:id`: 受理として扱うDecisionの論理参照。繰り返せます。Decisionの文面から受理かどうかは判断しないため、指名が要ります。scope付きのDecisionは指名できません。

### 何を調べるか

- 各Decisionの`basis_refs`のExactBindingを、現行対象と6成分（`logical_ref`のkind・id・scope、`content_digest`、`representation_profile`のprofile_id・version）で比べます。比較はGoの文字列一致で、case folding・正規化はしません。scopeの省略と空文字は同じとして扱います（SEIと同じ）。論理参照（kind:id）だけのbasisは比べられず、`no-exact-basis`です。指名したDecisionがこの状態のときは、束縛されていないとは言わず、阻害要因`named-decision-has-no-exact-basis`を`unresolved`に出して両フラグを`null`にします。現行対象と別のArtifact（kindまたはidが違う）だけを指すDecisionを指名したときは、同じ対象かどうかを判断せず、情報`named-decision-basis-other-identity`を`unresolved`に出します。
- `digestOnlyMatchRecordIds`は、本文digestだけを比べると一致するDecisionです。`digestOnlyMatchButNotBoundRecordIds`は、そのうち構造上束縛されなかったものです。後者が空でないことは、本文が元へ戻った後に旧受理が復活しなかった証拠ではありません。scopeなど他の成分が違うだけで同じ結果になり、途中のBを記録しないbundleでも同じです。
- `supersedes`/`withdraws`が端点として参照するDecisionと現行対象は、向きを問わず束縛扱いにしません。SEI v1alpha1はlineageのfrom/toの向きと、relationが受理へ及ぼす効果を定めていないためです。端点は、Decisionの論理identity、現行対象の論理identity（kind・id・scope）、現行対象に当たるDecisionの他のbasisの論理identityで照合します。SEIはlineageをArtifact間の関係として定義するため、現行対象やbasisのArtifactを端点とするlineageも閉じる扱いです。
- 端点とのscopeの有無が食い違う場合（一方だけscope付き）は、同じ対象か判断できないため阻害要因（`closing-lineage-endpoint-scope-unspecified`）にします。両方scope付きで別のscopeなら別の対象として、情報（`closing-lineage-endpoint-other-scope`）だけを残します。
- `revises`は閉じない扱いです。これはTAIの暫定仮定で、SEIの定めではありません。束縛されたDecisionが`revises`の端点のときは`revises-referenced`で表に出します。

### 出力の読み方

- `structurallyBoundToCurrentTarget`は`true`・`false`・`null`です。`true`は、指名したDecisionのいずれかが現行対象のExactBindingをbasisに持ち、閉じるlineageの端点でないという構造事実だけです。`null`は未確認で、未解釈のrecord、指名の欠落・重複、不完全な参照、上記の阻害要因などがあるときです。
- `reacceptanceRequired`は`true`か`null`だけです。`true`は、指名したDecisionのどれも構造上束縛されていないことを示し、Ownerの意味判断ではありません。現行対象と別のArtifactを指すDecisionだけを指名した場合や、再受理Decision自身が`supersedes`/`withdraws`の端点になる場合も`true`になります。再受理がないという断定ではありません。束縛があるときも`false`にはせず`null`とします。受理の有効性（意味・期間・権限・bundleへの書込み主体）は確認していません。
- exit codeは、報告を出せたら0です（束縛の有無にかかわらず）。入力を拒否したときは1（報告なし）、使用法の誤りや出力の書込み失敗は2です。合否の判定ではなく、報告の項目を読みます。`-out`は既存ファイルを上書きしません。
- `unresolved`に未確認の一覧（`blocking`の有無つき）を返します。指名したDecisionの`unresolved_refs`（例: `authority:unknown`）は判定に使わず、原値のまま通して`named-decision-has-unresolved-refs`で知らせます。`responsibility_refs`も原値のままで、権限の根拠にしません。

### 示さないこと

- 受理の意味・期間・権限、人間によるレビュー、公開承認、参照先の内容。`exactTargetsVerified`・`humanReviewed`・`authorityVerified`・`publicationApproved`は常にfalseで、digestは再計算しません。
- 束縛は、bundleへDecisionを書ける主体なら誰でも作れます。書込み主体は確認しません。
- 同一ExactBindingに戻り、閉じるlineageがbundleに記録されていない往復は検出できません。閉じるlineageがあっても、端点が上記の論理identityのどれにも当たらなければ見つかりません。basisの内容・現行性は確認せず、他のbasisの現行性は対象ごとに`-current-target`を替えて調べる必要があります。
- 最初から未受理だったA→B→A（現行N-01と同じ状況）では、指名したDecisionがbundleにないため`null`で、非復活の実証にはなりません。
- 再受理を`supersedes`または`withdraws`で旧Decisionに結ぶと、新Decision自身もlineageの端点として束縛されず、`reacceptanceRequired`は`true`のままになります（向きを仮定しないための帰結で、向き不明の偽陽性を含みます）。再受理が束縛として現れ得るのは、`revises`で結ぶ場合（TAIの暫定仮定）か、lineageを付けない場合だけです。
- SEI CLIの`add decision`が作る実storeのDecisionは、basisが論理参照でlineageも持たないため対象外です（`no-exact-basis`）。指名すると阻害要因`named-decision-has-no-exact-basis`を返し、両フラグは`null`です。実資料・意味受理は未確認です。
- 入力は小さな合成bundleを前提にし、サイズ・入れ子の深さ・件数の上限はありません。極端に深い入れ子ではGoの再帰がスタック上限に達して異常終了することがあり（既存の`-basis-bundle`も同じ）、処理量はDecision数×lineage数に比例して増えます。
- 次はOwner判断です。lineageの向きとrelationの効果（SEI側）、`revises`の扱いと再受理を表すrelationの規約、どのDecisionが受理かを示す規約（指名の代わり）、受理の有効性をどこに置くか。

fixtureは`testdata/validity/`にあります。すべて合成で、実在の名前・規程・個人情報を含みません。`bad-*`はSEI d818028の`verify --input`が拒否することを手動で確認した形（試験がSEIで毎回確認するのは`bad-relation`・`bad-same-logical-no-exact`・`bad-partial-exact-endpoint`の3件だけで、残る5件の拒否は試験で固定していません）、`x-*`はSEIが受理するがlineageの解釈が分かれる形、`ok-*`はSEIが受理し、この検査が未確認として残す形（未解釈record・同じ論理IDの重複・参照先のないendpoint）です。出力は診断であり、新しいContractや状態の正本ではありません。
