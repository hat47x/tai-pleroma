# SCN-001 成果の観測：何が成立し、何が成立していないか

状態: **観測記録（合成資料・開発レビューの範囲）**。合格報告ではない。公開承認、人間レビュー、利用者による価値評価は**未実施**。
対象: [SCN-001 受入観点](SCN-001-acceptance.md)の「矛盾する施設案内資料から、出典付きの暫定案内Draftを作成する」。
記録: [SCN-001-outcome-2026-11-11.json](records/SCN-001-outcome-2026-11-11.json)。道具: [`scn001_outcome_probe.py`](../integrations/tools/scn001_outcome_probe.py)。

新しいEngine、Store、Workflowは追加していない。既存の `reference-scn001-run`（生成・検証）、`reference-publication-gate`、SHOの読み取り専用 `sho-inspect` を実行し、その出力を読むだけである。各Productの意味・権限・結果の正本はそれぞれのリポジトリにあり、ここへ複製しない。

## 1. 読み方の規則

実行記録の `passed: true` は成果ではない。次の主張を**別々に**判定し、一つの結論へ足し合わせない。

| 主張 | 言っていること | 成立に要る観測 |
| --- | --- | --- |
| T-Draft | 根拠付きの暫定Draftが、記録どおりのbytesで存在する | 保存後に読み直したbytesが記録のdigestと一致する。MMI選択行・評価入力・D-04根拠行の本文digestが一致する。その記録が、主張の対象であるAttemptのものである |
| R-Deliver（別実装） | 生成側と別の実装が同じbytesを読んだ | 別実装が計算したdigestと記録のdigestを**比較した結果**が一致。上限は「限定成立」 |
| R-Deliver（本来の受取先） | Goalが名指す受取先が受領した | 受取先自身による受領の観測 |
| Authority | 公開を許す現在のOwner権限がある | Owner本人の判断。成果物・記録・AIの記述からは導出しない |
| S-NoUnauthorizedPublish | 権限なしに公開していない（**制約**） | 公開gateの拒否の観測、公開の不在 |
| P-Publish | 案内が公開された（**Goal**） | 権限と、公開先での観測 |
| Effect | 外部への作用 | none／no-op／known／partial／unknown |
| Value | 本人・関係者に価値が生じた | 本人・関係者の評価 |

規則は四つある。

1. 成果物のbytesを比較していない検証は、T-Draftを**保留**とする。
2. Readerが成功を返したことは一致の証拠にしない。一致は、独立に計算した二つのdigestを比べて初めて言える。
3. 安全に止めたことは制約の充足であり、Goalの達成ではない。「公開しなかった」は S-NoUnauthorizedPublish の充足と P-Publish の未達を同時に意味する。片方をもう片方の値にしない。
4. Effectが unknown／partial のときは、独立な読取で確かめるまで再試行しない。

## 2. 今回の実行

- TAI: main `2d44d82583354ec46dc8e4241c01d49c8c20d67d`。
- MMI `386f81c3f7bf4dc5e9e4b0f24eb3aa03d30be453`（`markdown-matrix-injector/0.3.0`、実MCPの `inspect`／`select`）。
- SEI `cd6eb02582f0e0ca84b91c9d273880a602e8e784`（一時storeの `resume`）。
- SHO `88a15786cc1484c9ee004c8b5253cc2a203a66d6`（`bin/sho-inspect.cjs inspect`、別プロセス）。
- 環境: WSL2 Ubuntu、Go 1.27.0、Node 24.22.2、Python 3.12.3。Windowsネイティブでは**未実施**。
- `tools/reference-scn001-run` の `go test ./... -count=1 -v` は、MMI・SEIの固定版を置いた状態で PASS 54、SKIP 0、FAIL 0。

今回のAttemptでD-04を新しく生成し、保存し、次の五つを同じ検証器で確かめた。期待値は実行前に道具の中へ書いてある。

| 場合 | 検証器の応答 | T-Draft | R-Deliver（別実装） |
| --- | --- | --- | --- |
| 正例：保存した成果物を比較 | exit 0、`passed:true`、`artifactBytesVerified:true` | **成立** | 限定成立（SHOが同じsha256、1,969 bytes） |
| 成果物を比較しない | exit 0、**`passed:true`**、`artifactBytesVerified:false` | **保留** | — |
| 1文を差し替えた成果物 | exit 1、`passed:false` | 不成立 | 不成立（SHOは exit 0・`indexed` のまま別のsha256を返す） |
| 成果物が存在しない | exit 1、`cannot read review artifact` | 不成立 | 不成立（SHOは exit 2、`not-found`） |
| 11-01の記録を今回の成果物に当てる | exit 0、**`passed:true`**、`artifactBytesVerified:true` | **保留**（別Attemptの記録） | — |

最後の行が示すとおり、D-04は合成fixtureから決定的に生成されるので、digestは実行をまたいで同じになる。成果物のdigestは「今回の実行」の証拠にならない。Attemptの区別は `runDigest` と `generatedAt` でしかできない。

公開gateは `allowed=false`、blocker 7件、exit 1 で拒否した（R-01〜R-05は合成のdevelopment accepted、R-06・R-07は pending）。公開は実行していない。この拒否の観測は既存の[YI-publication-refusal](records/YI-publication-refusal-2026-11-11.json)と同じ道具によるもので、ここでは重ねて主張しない。

## 3. 成立したもの、していないもの

| 項目 | 判定 | 言ってはいけないこと |
| --- | --- | --- |
| Goal（本来） | 利用者本人のGoal確認は無い。受入票の観点で代用している | 「Goalを達成した」 |
| Work Product | D-04、1,969 bytes が存在する | 「内容が正しい」 |
| T-Draft | **成立**（合成資料、今回のAttempt） | 「実資料で成立」 |
| R-Deliver（別実装） | **限定成立**。bytesのみ、成果物のコピー、同一操作者・同一ホスト | 「Consumerが受領した」「出典を確認した」 |
| R-Deliver（本来の受取先） | **未実施**。受取先が決まっていない | — |
| Authority（公開） | **無い** | 「仮承認済みなので公開できる」 |
| S-NoUnauthorizedPublish | **充足** | 「だからGoalを達成した」 |
| P-Publish | **未達**（Authority待ち） | 「失敗」と一括すること |
| Effect | none（記録の宣言。外部の作用先が無い） | 「Effectなしを確認した」 |
| Value | **未評価** | 「価値があった」 |

SHOのReaderが読む範囲は、bytesとMarkdownリンクである。D-04の根拠表はリンクではなく文字列なので `linkOccurrenceCount: 0` で、Readerは出典を確かめていない。`revision` は `unknown` を返す。

## 4. 偽の成功・偽の失敗

受入票の負例と[TAI #531](https://github.com/hat47x/tai-pleroma/issues/531)のOR-01／OR-04／OX-02／OX-04に対応させた。

| 反例 | 防ぐ規則 | 確かめ方 |
| --- | --- | --- |
| O1 Tool成功、成果物なし | 規則1 | 実行（欠落、比較なし） |
| O2 記録は成功、Readerは別bytes | 規則2 | 実行（差替え） |
| O3 成果物は正しい、受取先が未受領 | T-DraftとR-Deliverを別の行にする | 実行（本来の受取先は未実施のまま）＋自己試験 |
| O4 承認済みの自己申告 | AuthorityはOwnerの判断だけ（N-02、OX-02） | **自己試験のみ**。敵対的な実試験は未実施 |
| O5 適切に止めたDraftを全面失敗とする | 規則3 | 実行（T-Draft成立とP-Publish未達が同時に出る） |
| O6 停止を理由にGoalまで成功とする | 規則3 | 実行（同上） |
| O7 Commit後に応答喪失 | 規則4（OX-04） | SCN-001では**自己試験のみ**（外部Providerが無い）。実EKIでの1件は[応答を失ったあとの回復判断](EKI-effect-unknown-recovery-2026-11-12.md)（2026-11-12追加） |
| O8 同じ内容だが別のAttempt・別の用途 | 記録をAttemptと適用範囲に束縛して読む（N-06） | 実行（11-01の記録）＋自己試験（用途違い） |

自己試験は、判定規則に手書きの観測を17通り与えて期待と比べるもので、Providerの挙動の観測ではない。規則を6通りに壊して、6通りとも自己試験が失敗することを確かめた（記録には含めていない。手元での確認）。

## 5. 三つの構成の比較

同じUser Job、同じ五つの場合で比べた。

| 観点 | B0 通常のファイルとコマンドだけ | B1 既存Productの証拠＋この読み方 | B2 独立したEngine／共通Store |
| --- | --- | --- | --- |
| 実施 | 実行した（`sha256sum`、`grep`、JSONの目視） | 実行した（この記録） | **作っていない。測定値なし** |
| 真の成立の検出 | bytesの一致は言える。入力束縛（MMI選択＝評価＝D-04）は手では確かめられず、T-Draftは保留止まり | 成立を検出 | — |
| 偽成功（5場合中） | 0件。ただし手順を守った場合に限る | 規則なしで `passed` だけを読むと**2件**（比較なし、旧記録）。規則を適用すると0件 | — |
| 偽失敗（5場合中） | 0件 | 0件 | — |
| 成果物・受取先の確認範囲 | bytesのみ。別実装の読取なし | bytes＋入力束縛＋別実装の読取（限定） | — |
| 不明・部分成功の維持 | 書き手に依存 | 主張ごとに別の行で維持。外部Effectは自己試験のみ | — |
| 不正な公開の拒否 | 状態ファイルを読むだけ（観測ではない） | gateの拒否を観測 | — |
| 追加したProduct／Tool | なし | 新規の道具1本（約500行、検査用）。Productへの追加なし | — |
| 機械の所要時間 | 0.19秒 | 約10〜12秒（生成を含む） | — |
| 人手・保守の負担 | **未測定** | **未測定** | **未測定** |

B2が要ると言える反例は見つからなかった。外部Effectの不明（O7）を解くにはProvider側の操作の識別と独立な読取が要り、TAIに置いたStoreからは観測できない。旧記録の再利用（O8）は既存の `runDigest` で区別できる。したがって**B1を採り、B2は採らない**。利用者にとっての効果と人手の費用は測っていないので、この選択は正確性と追加機構の要否についてだけの判断である。

## 6. 代行したOwner判断

2026-11-11、リポジトリOwnerの指示により、次の判断をAIが代行した。**人間による内容のレビューではなく、公開承認・利用者評価の代行でもない。** Ownerはいつでも取り消せる。

| ID | 判断 | 理由 |
| --- | --- | --- |
| OD-1 | D-04の本来の受取先は、合成後に行う実物レビュー（R-06・R-07）の人間のレビュー者とする。人が指名されるまで R-Deliver（本来の受取先）は「未実施」のまま | 代用品で受領を装わない |
| OD-2 | 公開の承認者は不明のまま据え置く。P-Publish は「未達（Authority待ち）」で固定する | 代行の範囲に公開承認を含めない |
| OD-3 | 別Productの実装による読取（同一操作者）は、開発段階では「限定成立」まで認める。「成立」にはしない | 別主体による受領ではない |
| OD-4 | P-01「出典へ戻れる」は、開発レビューの段階ではD-04単体での解決を求めない。実物レビューの開始時に再判断する | D-04の出典は `notice` 等のラベルで、fixtureと併せて初めて辿れる。受入票の合格条件は変更しない |
| OD-5 | `reference-scn001-run` の `passed` の表示は変えない。読み方の規則1で扱い、事実だけを[#28](https://github.com/hat47x/tai-pleroma/issues/28)へ返す | #28 の担当範囲に重ねない |
| OD-6 | この観測記録はTAIの `evaluations/` に置く。SCN-001専用で、共通Schemaとはしない | #531 は索引のみを持つ |

判断していないもの: [#127](https://github.com/hat47x/tai-pleroma/issues/127) P-06でどの規模から始めるか、実物レビューの開始時期と参加者。実在の人と資料が要る。

## 7. 未実施と限界

- 実資料、出典の真正性、取得時点（`observedAt` は合成値）。
- 本来の受取先による受領、人間レビュー、Owner権限、利用者による価値評価。
- 外部Providerと実Effect（O7）、承認の自己申告への敵対的な実試験（O4）。
- Windowsネイティブでの実行。11-01の記録ではSEIの `decision.statement` が文字化けしているが、今回のLinux実行では正しく「公開は保留」と記録された。Windowsでの再現と原因は未調査。
- 今回の実行記録（`run.json`）と成果物のコピーは保存していない。成果物は保存済みの[D-04](artifacts/SCN-001-D-04-provisional.md)とbyte一致である。
- 期待値を書いた者と観測した者は同じである。独立した第三者によるExpectedではない。

## 8. 再現

```text
# MMI・SEI・SHOの固定版を用意し、MMI（03_Implement）とSHOで npm ci を済ませる
export MMI_ROOT=<MMI> SEI_ROOT=<SEI>
python integrations/tools/scn001_outcome_probe.py --self-test
python integrations/tools/scn001_outcome_probe.py --tai-root . \
  --stale-run evaluations/records/SCN-001-run-2026-11-01.json \
  --sho-root <SHO> --out <新しい出力先>
```

`--sho-root` を省くと R-Deliver（別実装）は「未実施」になり、失敗にはならない。
