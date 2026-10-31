# TAI Pleroma（泰）

> 本リポジトリは、生成AIを用いた初期開発中のソースコードを公開するものです。現時点で人的レビューを伴っておらず、仕様や実装は変更される場合があります。

TAI Pleromaは、人が知識を得て、考え、判断し、成果を生み、その結果から学ぶまでの活動を支えるプロジェクトです。個人だけでなく、組織や社会での知的活動も対象にしています。

「泰」は易経第11卦の「地天泰」、「Pleroma」は充足した全体性に由来します。目指すのは、個々の機能を増やすことよりも、必要な知的能力を組み合わせて、利用者が一つの課題を継続して扱えることです。

## 何をつなぐのか

TAIは、役割の異なる五つの関連基盤を必要に応じて利用します。

| 基盤 | 主に扱うこと |
| --- | --- |
| SUI | 観測、異なる解釈や仮説の整理、意味の探索 |
| TEI | 業務のデータ・規則・機能のモデル化と検証 |
| SEI | 観測から判断までの意味の区別、根拠と判断履歴の保持 |
| SHO（現行のMMIを含む） | 文書の作成・参照、出典をたどれる成果物 |
| EKI | 範囲や権限を定めた処理の委任と、その結果の確認 |

各基盤には独立した役割と開発の進め方があります。TAIはそれらの機能を重複して実装したり、独自の中央Hostへ集約したりすることを目的にしていません。

## YI Constellationとの関係（統合・配布の構想）

**YI Constellation**は、関連製品群を紹介する**ブランドとウェブサイト**の名称です。専用のリポジトリは設けず、サイトの制作・公開設定はTAIリポジトリで管理する方向で検討しています。

TAI Pleromaは知的課題を横断して扱う**統合製品**です。さらに本リポジトリを、各製品で独立して開発・検証した版付き成果物を必要に応じて**選択・統合検証・組立て・配布する拠点**とする構想を進めます。各製品の正本、単独リリース、意味上の判断と実行権限は、それぞれのOwnerに残します。

これは[製品群統合・配布の設計案](docs/product-family-delivery.md)、[受入条件案](docs/product-family-release-requirements.md)、[ウェブサイト構想](docs/yi-constellation-website.md)および[Issue #74](https://github.com/hat47x/tai-pleroma/issues/74)で審議する**提案**です。現状のTAI CIは参照試験を中心とし、シリーズ全体の統合ビルド・リリース機能やYIの公開サイトが既に成立したという意味ではありません。

## 最初に扱う課題

最初の題材は、[SCN-001：共同利用スペースの案内改善](scenarios/SCN-001-shared-space-guidance.md)です。これは架空の資料を使った検証用シナリオです。

施設の掲示には「予約不要」、別の案内には「会議室は事前予約が必要」と書かれています。両者が本当に矛盾するのか、一般則と例外なのか、古い案内が残っているのかを調べます。

この過程で、元の資料と版を残し、複数の解釈を検討し、確認できた範囲で案内文を改訂します。新しい資料で文言が以前と同じに戻っても、過去の判断が自動的に有効になるとは扱いません。

製造工程の課題検出用に、公開施設案内の一般的な論点を参考へ独自創作した[合成施設文書](scenarios/SCN-001-synthetic-facility/README.md)もあります。実在の施設・規程ではなく、R-01〜R-05の`accepted`や`real-object`証拠ではありません。

合成入力で現在どこまで確認でき、何が未確認かは[合成入力による工程検証の現在地](docs/synthetic-validation.md)にまとめています。

## 現在、確認できること

SCN-001について、次の参照実装と検証記録があります。

| 対象 | 現在の確認範囲 |
| --- | --- |
| [SCN-001評価](tools/reference-scn001/README.md) | 架空の観測・仮説・改訂履歴の構造的な検査 |
| [MMIとの接続](tools/reference-mmi-readonly/README.md) | 開発用の文書を読み取り専用で参照し、観測を取得 |
| [SEIとの接続](tools/reference-sei-decision/README.md) | 合成した判断記録の保存・再開時の参照 |
| [D-04文書生成](tools/reference-scn001-render/README.md) | 内部レビュー用Markdownの生成 |
| [統合参照実行](tools/reference-scn001-run/README.md) | MMI・SEI・SCN-001評価・文書生成とSUIの照合結果を記録 |
| [SUIとの接続](tools/reference-sui-api/README.md)・[観測照合](tools/reference-sui-link/README.md)・[D-04照合](tools/reference-sui-draft/README.md) | 文書内のカードと観測本文の対応、島の構成、D-04の根拠行を確認 |
| [TEIとの接続](tools/reference-tei-model/README.md) | SCN-001で使う型宣言の検証 |
| [EKIとの接続](tools/reference-eki-api/README.md)・[CLI確認](tools/reference-eki-cli/README.md) | API認証と合成Taskの受付・待機状態、CLI起動を確認 |
| [EKI Worker test環境](tools/reference-eki-worker/README.md) | WSL/DockerでAgent/Control test profileとバイナリbuildを確認 |
| [公開条件の検査](tools/reference-publication-gate/README.md) | レビュー項目R-01〜R-07の状態を判定。現在は公開を保留 |
| [公開境界の検査](tools/check-public-boundary/check.py) | 非公開リソース名・秘密鍵・tokenの混入をtracked fileから検出 |

これらは開発・評価用の接続です。架空の資料に対する検査やTaskの受付を、実在の規程の確認、人による意味の受理、公開権限、実際の処理完了と同一視しません。特に、EKIでの`queued`はWorkerによる実行完了を意味しません。

## どこから読むか

初めて読む方は、[SCN-001のシナリオ](scenarios/SCN-001-shared-space-guidance.md)から始めてください。そのあと、[責務の分担](docs/architecture-slice-001.md)と[現在の状態](docs/status.md)を読むと、目標と実装範囲を区別できます。

実装や評価に関わる方には、以下の資料があります。

- [受入観点と負例](evaluations/SCN-001-acceptance.md) — 何を確認し、何が未確認か
- [統合参照実行の手順](tools/reference-scn001-run/README.md) — 必要な開発環境、実行方法、検証範囲
- [実物による再レビュー計画](evaluations/SCN-001-real-object-review.md) — 実在の資料や権限者を確認するための条件
- [ロードマップ](docs/roadmap.md)・[クリティカルパス](docs/critical-path-2026-10.md) — 今後の作業と判断事項

GitHub Actionsの`tai-reference`はGo・Pythonの参照試験を対象としています。外部基盤の開発チェックアウトが必要な試験は、環境によって実行されません。個々の検証結果とCIの実行状況は、対象の版ごとに確認してください。

## 公開範囲

本リポジトリは、初期開発中のソースコードと、そこで用いる合成fixture・評価記録を公開します。実在の顧客資料・個人情報・認証情報・非公開の作業資料は含めていません。

TEI Platformの非公開作業資料、第三者の原文・抽出物は、著作権・利用条件・関係者文脈の確認前のため公開していません。公開条件は非公開リポジトリ内のREADMEに記録し、公開リポジトリへ内容を複製しません。

## リポジトリの構成

| 場所 | 内容 |
| --- | --- |
| [docs/](docs/) | 目的、設計、判断経緯、計画 |
| [scenarios/](scenarios/) | 利用者の課題と検証用シナリオ |
| [integrations/](integrations/) | 既存基盤との接続の調査 |
| [evaluations/](evaluations/) | 評価条件、合成試験、実行記録 |
| [tools/](tools/) | 参照実装と検証用ツール |

開発時の作業規則は[AGENTS.md](AGENTS.md)を参照してください。脆弱性の報告は[SECURITY.md](SECURITY.md)、変更の進め方は[CONTRIBUTING.md](CONTRIBUTING.md)を参照してください。

## ライセンス

[MIT](LICENSE)
