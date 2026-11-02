# SCN-001 合成施設文書

**このディレクトリの文書は、製造工程の課題検出のために独自に創作した架空の資料です。** 実在の施設・規程・掲示・案内文ではありません。実物レビューの証拠として扱いません。

## 目的

公開されている施設利用案内の一般的な論点を参考に、次の工程上の欠陥を検出できる合成入力を用意します。

- 総則と例外の書き分けが曖昧になり、利用者が「予約不要」と誤解する。
- 会議室の予約制と、施設全体の「予約不要」が同じ文書群に併存する。
- 配布文書の版が変わり、以前の条件が消える。
- 予約規程の原本を取得できないまま、要約だけで判断しようとする。

## 文書と観測の対応

| 文書 | 想定する観測 | 内容 |
| --- | --- | --- |
| [entrance-notice.md](entrance-notice.md) | O-02 | 館内掲示。施設全体は予約不要と要約し、会議室は別案内へ委ねる |
| [meeting-room-guidance.md](meeting-room-guidance.md) | O-03 | 会議室・研修室は事前予約制 |
| [distribution-2026-10.md](distribution-2026-10.md) | O-06 | 2026-10版の配布文書。会議室は事前予約制 |
| [distribution-2026-11.md](distribution-2026-11.md) | O-07 | 2026-11版の配布文書。会議室の記載が消え、施設全体は予約不要 |
| [original-policy-note.md](original-policy-note.md) | O-08 | 予約規程の原本を取得できなかった記録 |

## 参考にした公開情報の例

次の公開ページは、施設利用案内の一般的な構成を確認するために参照した例です。文章・施設名・日付・数値は独自に創作しており、内容を転記していません。

- [鹿児島市 中会議室の利用案内](https://www-city-kagoshima-lg-jp.cache.yimg.jp/kyoiku/kyoiku/syogaigaku/shisetsu/shogai/019_260001_318.html)
- [大分市 南大分公民館の施設情報](https://www.city.oita.oita.jp.e.adk.hp.transer.com/o047/minamiooitakominnkanshisetu.html)
- [藤枝市 広幡地区交流センターの利用案内](https://www.city.fujieda.shizuoka.jp/soshiki/shiminkyodo/hirohata/gyomu/19470.html)
- [三島市 中郷公民館の予約と使用の方法](https://www.city.mishima.shizuoka.jp/site/kominkan/1573.html)

## 境界

- 実在の施設名・住所・電話番号・担当者・予約状況は含めない。
- この文書群を`evidenceKind=real-object`としてreview statusへ記録しない。
- 公開gateは`blocked`のまま。合成入力の検出結果を、実物レビューの受理へ読み替えない。
