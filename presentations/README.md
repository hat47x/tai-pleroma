# YI Constellation — シリーズ紹介プレゼンテーション（Draft）

本ディレクトリは、**YI Constellation**（製品ファミリーのブランドとウェブサイト名）の概要と各製品の役割を、初めて読む人へ説明する**PowerPoint制作向けMarkdown原稿**を置く場所です。**YI専用のGitHubリポジトリは設けません**。

## ファイル

- [本編24枚＋付録3枚の原稿](yi-constellation-family-overview.md) — 製品価値、社会的意義、六つの役割、ブランドの星座、TAIの統合・配布構想、事例、現在地。Mermaid図と各ページの話者ノート付き。
- [制作ガイド](yi-constellation-design-guide.md) — 高密度の図・表を16:9で読みやすく配置するための色、文字、線種、版面、スライド別ストーリーボード。
- [改稿・批評・検証記録](yi-constellation-editorial-review.md) — 前版からの変更、yomiyasu手動点検、現行実装との距離とNOT RUN。

## 実製品・リポジトリとの境界

- **YI Constellation**: ブランド／製品紹介ウェブサイト名。専用リポジトリ／Productの固有実行Hostではない。
- **TAI Pleroma**: 知的課題を横断して扱う**製品**。既存の`tai-pleroma`リポジトリは、利用知識の整備と製品版の統合検証・構成別配布・サイト制作の**拠点とする提案**。
- **SUI／SEI／TEI／SHO・MMI／EKI**: 固有の意味・ソース・実装・受入・単独リリースの正本はそれぞれの製品側に残す。
- **星座の概念関係 ≠ 配布物の受渡し ≠ 実行時API依存**。説明用の点線を、確定した互換性や組織の上下関係にしない。

この構想の正本となるOwner判断は[TAI Issue #74](https://github.com/hat47x/tai-pleroma/issues/74)、実装未完の設計提案は[Draft PR #75](https://github.com/hat47x/tai-pleroma/pull/75)で追跡する。製品分類と関係性は別の[Issue #73](https://github.com/hat47x/tai-pleroma/issues/73)、[Draft PR #72](https://github.com/hat47x/tai-pleroma/pull/72)にある。

**現状:** GitHub上のTAIのmainはSCN-001等の参照試験が中心で、全製品を組み立てるBundle ReleaseとYIサイトの本番公開は未実装。本文は視覚説明の**Draft**であり、正式ブランド承認・第三者受入・PPTX実描画を意味しない。

外部公開する前に、各製品のOwnerによる説明の確認、商標・ブランドアセットの利用確認、スライドの投影・可読性検証を行うこと。
