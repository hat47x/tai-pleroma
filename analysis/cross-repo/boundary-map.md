# リポジトリ間の機能分界に関する整理

作成日: 2026-10-06
更新日: 2026-10-09
状態: 2026-10-06〜09時点の整理資料。起票した内容と、判断を待つ点をまとめる。2026-10-31にgit管理外の親ディレクトリから本リポジトリ（`analysis/cross-repo/`）へ移設し、版管理下に置いた。記載内容は当時のスナップショットであり、現在の状態を示すものではない。

## 0. 2026-10-09の更新

2026-10-06の整理の後、3日で状況が変わった。次の点は、本文の記述より新しい。

- **F1の大部分は解消した。** SEIが、remoteになかったbranch `docs/family-apex-backflow-20260927`を`develop/v0.2.0`へmergeした（`041c3fa`）。引用されていた5文書は、2件が同名で、3件が新しい番号で見つかった（ADR-0032はADR-0035、ISSUE-000081は000086、ISSUE-000082は000087）。F1で「どこにも存在しない」と書いたのは、そのbranchが別の環境にだけあったためで、起票時に注意書きとして残していた可能性が当たった。
- **測定手法を直した。** 2026-10-06の測定は、作業ツリーを走査していたので、git管理外の作業コピー（`.local/`など）まで数えていた。また、SEIの統合の線は`main`ではなく`develop/v0.2.0`なのに、全てを`origin/main`と照合していた。現在の`xref_audit.py`は、git管理下のファイルだけを対象にし、引用先ごとに統合branchを持ち、「mainにある／統合branchにだけある／どこにも無い」を区別する。
- **TEIの起票を組み直した。** 引用の欠落は解消済みだったので、Issueにはせず、TEIの引用を新しい名前に直接直した（版`@041c3fa`を固定。TEI `eb1ed11c`）。ダイジェスト規則のIssueは、数え落としを直して000085として起票した。当初の「4種」は不完全で、実際は7種・4系統だった。
- **番号が衝突した。** 000083と000084は、その間に別セッションがTEIで使った。SEIでは、私の000080が先に番号を取ったため、SEI側の別のIssueが000084へ付け替えられた。

2026-10-09時点の測定（git管理下のみ）は、引用32件・参照先23種で、取得状況は「mainにある10、統合branchにだけある3、版を固定して取得できる5、どこにも無い5」である。どこにも無い5種の内訳は、MMIの旧ADR-0032が1、vs-bearの旧ISSUE-000081が1、CSWが引用するSUIの廃止済み文書が3である。

## 1. 調べたこと

対象は、tei-platform、sei-cognition、sui-sensemaking、markdown-matrix-injector、eki-fabric、cultural-substrate-weaving、vs-bear-simulatorの7リポジトリである。2026-10-06に全てfetchした。vs-bear-simulator-galleryは対象にしていない。

次の3つの方法で調べた。

- 各リポジトリのREADMEと価値文書で、自分の責務をどう宣言しているかを読んだ。
- 製品名の言及を、双方向に数えた（`audit/mention_matrix.py`）。
- `hat47x/<repo>:<path>`の形の引用を抜き出し、引用先の`origin/main`に存在するかを確かめた（`audit/xref_audit.py`）。

読んだのは文書で、各製品の実装は動かしていない。引用の数は下限である。EKIのように、リポジトリの接頭辞を付けずに引用する文書があるためだ。

## 2. 現在ある分担

SEIの`product/definition/SEI_PRODUCT_SHAPE.md`§6.4が、四者の分担を一つの表にしている。

| 製品 | 担当 |
| --- | --- |
| SUI | sensemakingと意味の創発 |
| SEI | 持続する認知と判断の意味 |
| TEI | 形式化された業務Capabilityと、その実現の境界 |
| EKI | 分散した計算の配置と実行基盤 |

同じ箇所は、製品の親和性が、必須の依存、共有Universal Core、共有Evidence claimのどれでもないと明記している。SUI、TEI、EKIをまたぐ共通の統合標準は、同文書で「Not Established」とされている。MMI、CSW、vs-bearは、この表に入っていない。

製品の組ごとに、取り決めの有無と向きを整理した。

| 組 | 状態 |
| --- | --- |
| SEI と TEI | 双方向。SEIのADR-0014（Accepted）と、TEIの価値文書「隣接Productとの境界」がある |
| TEI と EKI | 双方向。TEIのISSUE-000081（評価待ち）と、EKIの`orchestrator-integration-and-layering.md`がある |
| SEI と EKI | 双方向。SEIの`SEI_PRODUCT_SHAPE.md`§6.3と、EKIの`sei-cognition-mapping.md`がある。ただしSEIの評価文書`distributed-execution-fabric`は、EKIに触れていない |
| TEI と SUI | TEI側の`SUI_REFERENCE_ADOPTION_DESIGN`がある。SUI側の対は、2026-10-01の整理でmainから外れた |
| SEI と SUI | SEIがSUIに言及する文書は17件、SUIがSEIに言及する文書は0件 |
| CSW と SUI | CSWがSUIに言及する文書は15件、SUIがCSWに言及する文書は0件 |
| vs-bear と SEI | vs-bearがSEIに言及する文書は4件、SEIがvs-bearに言及する文書は0件 |
| MMI と SEI | MMIがSEIに言及する文書は5件、SEIがMMIに言及する文書は1件。MMIの対応ノートは、依存を作らない参考資料と明記している |

## 3. 見つかったこと

### F1 引用先が取得できない

明示的な引用35件の参照先22種のうち、9種が引用先のmainに存在しない。内訳は次のとおり。

- SEIの5件は、SEIのどのbranchにも履歴にも存在しない。引用側はTEI、MMI、EKI、CSW、vs-bearの5製品で、延べ20か所である。SEIのIssue番号は全refを通して79が最大で、引用された81と82は、SEIにまだ存在しない番号である。ADR-0032の番号は、別の内容のADRが使っている。
- SUIの3件と、TEIが挙げるSUI側の対1件は、SUIが2026-10-01に管理文書を整理したあとのmainにない。4件のうち3件は未統合のbranchに残り、1件は履歴にだけ残る。
- SEIの1件（`evaluation/local-typed-comparator/README.md`）は、未統合のbranchにだけある。

### F2 家族の境界を決める提案の本文がない

SEIが2026-09-27に出した「SEIを製品群の統合の頂点に置く」提案の本文は、どこからも取得できない。TEIは、提案の採否に関係なく自分の線を維持すると書いている。EKIとMMIも、SEIに依存しない立場を書いている。そのため各製品の立場は成り立つが、提案が置かれていると説明するbranchは、SEIのremoteにない。

### F3 SUIを定義するのは他の製品だけである

SUIの役割や境界は、SEIとCSWの文書が述べている。SUI自身が他製品との関係を述べた文書は、ほとんどない。TEIとEKIに触れる文書が各2件あり、SEIとCSWに触れる文書は0件である。SUIのAGENTS.mdは、管理文書を作らない方針を定めており、他製品がSUIの文書を引用しにくい構造になっている。

### F4 同じ見た目のダイジェストが、別の規則で作られている

`sha256:<64桁>`の形の値を、TEIは4通り、SEIは2つのprofile、MMIは独自の規則で作っている。見た目が同じでも、同じ内容が同じ値になるとは限らない。MMI自身が、この問題を文書に書いている。

### F5 横断の成果物に置き場がない

`product-progress.*`、`gen-progress.js`、`yomiyasu-lint-report.md`、この文書と監査スクリプトは、親ディレクトリにある。親ディレクトリはgit管理外で、版も所有者もない。（2026-10-31追記: この文書・監査スクリプト・`product-progress.*`・`gen-progress.js`は、本リポジトリの`analysis/cross-repo/`へ移設した。`yomiyasu-lint-report.md`は文章推敲の作業記録であり、横断の分析成果物ではないため対象外とした。）

### 確認したが、境界の問題にしなかったもの

- `ponytail`スキルは、7リポジトリに同一の内容で置かれている。違いは行末コードだけである。出典や版の宣言は無いが、機能の分担に関わる問題ではないため、起票していない。
- SEIの`evaluation/distributed-execution-fabric`と、EKIは、同じ2026-09-12に始まった。範囲が重なるが、SEIの`SEI_PRODUCT_SHAPE.md`§6.3は、すでにEKIへ委ねる形で書かれている。SEIの起票に含めた。

## 4. 要件

| 番号 | 要件 | 担当 | 起票 |
| --- | --- | --- | --- |
| FB-1 | 他製品の文書は、取得できる範囲でだけ根拠にする。引用先は、文書の存否を決めて引用側へ示す | 引用先と各引用側 | TEI ISSUE-000084、SEI ISSUE-000080。他の引用側は、SEIの決定を待つため未起票 |
| FB-2 | 家族の境界を述べる基準の文書を一つに定め、対象の製品を決める | SEI | SEI ISSUE-000080 |
| FB-3 | 一方が他方の役割を書いたら、他方は受けるか、断るか、書かない方針を示す | SUI、SEI、CSW | 未起票 |
| FB-4 | 製品間で見える値は、ハッシュ対象のbyte規則を示す | 各製品 | TEI ISSUE-000083。MMIは既存の計画がある。SEIは既存のprofileがある |
| FB-5 | 横断の成果物に、版管理された置き場と所有者を置く | 利用者 | 未起票 |

FB-3は、SUIの方針（管理文書を作らない）に反しない形が要る。ADRを1本書くか、ROADMAPに1行足すか、何も書かない方針を明示するかは、SUIの判断である。FB-5は、新しいリポジトリの作成を含むため、起票せずに残した。

## 5. 起票した場所と状態

| 場所 | 内容 | 状態 |
| --- | --- | --- |
| tei-platform | ISSUE-000085（ダイジェスト規則の宣言）。引用の修正 | pushした（`eb1ed11c`）。当初の000083と000084は、別セッションが番号を使ったため取り下げた。引用は、Issueにせず直接直した |
| sei-cognition | ISSUE-000080（他製品が引用するSEI文書の所在） | 起票は`develop/v0.2.0`にmerge済み（`1a840ec`は`041c3fa`の祖先）。進捗の記録は、local branch `docs/issue-000080-record-progress-20261009`（`3a05c9c`）にあり、pushしていない。状態をOpenからIn Progressに変えた。SEIの3つの検査はPASS |
| sui-sensemaking | なし | SUIの方針で、Issueを置かない |
| markdown-matrix-injector、vs-bear-simulator | なし | SEIの改番で、MMIは旧ADR-0032を1か所、vs-bearは旧ISSUE-000081を2か所で引用している。直すのは各製品。対応表はSEIのISSUE-000080にある |
| cultural-substrate-weaving | なし | SUIの廃止済み文書3件を引用している。直すのはCSW |
| eki-fabric | なし | 取得できない引用はない |

## 6. 判断が必要な点

1. FB-5。横断の成果物を、新しいリポジトリに置くか、既存のどれかに置くか。
2. FB-3。SUIが、SEIとCSWの記述に対して、どの形で立場を示すか。
3. SEIのISSUE-000080の進捗記録（local branch、未push）を、どう取り込むか。

## 7. 再現

```bash
cd analysis/cross-repo/audit
python3 xref_audit.py      # 引用35件の照合と、取得できない参照先の一覧
python3 mention_matrix.py  # 製品名の言及を、双方向に数えた表
```

2本とも、各リポジトリの`origin/main`を読む。各リポジトリの置き場は環境変数`HAT47X_ROOT`（既定は`/mnt/d/GIT/hat47x`）で指定する。実行前に、全リポジトリをfetchしておく。
