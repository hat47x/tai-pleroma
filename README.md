# TAI Pleroma

> 本プロジェクトは現在開発中です。仕様や実装は変更される場合があります。

個人・組織・社会の各水準において、知識・認識・思考・意思形成・創造・実践・学習が充実した全体として機能することを目指すプロジェクトです。

名称の「泰」は易経第11卦・地天泰、「Pleroma」は充足した全体性を表します。

関連基盤: SUI / TEI / SEI / SHO / EKI。TAIは、それらの集合や新たな中央Hostの構築自体ではなく、利用者から見た統一的な知的機能の成立と、その検証に重点を置きます。

## 最初の実証

- [SCN-001 共同利用スペースの案内改善](scenarios/SCN-001-shared-space-guidance.md) — 架空の資料の矛盾を保持し、判断と文書改訂までを扱うシナリオ（Draft・未実施）
- [知的機能スライスの責務境界](docs/architecture-slice-001.md) — 統一する機能と既存基盤の分担（Draft）
- [受入観点と負例](evaluations/SCN-001-acceptance.md) — 実証すべき成功・失敗条件（未実施）
- [初期PoCロードマップ](docs/roadmap.md) — 手動一巡から実接続へ進む案
- [TAI中心のクリティカルパス](docs/critical-path-2026-10.md) — TEI/SEI/SUI/SHO/EKIをどの順で接続するか（Draft）
- [現在状態](docs/status.md) — 実装済み・検証済み・仮承認・未確認の整理
- [SCN-001合成walkthrough](tools/reference-scn001/README.md) — T0/T1/T2の参照関係を検査する参照実装（実製品未接続）
- [MMI読み取り専用MCP接続](tools/reference-mmi-readonly/README.md) — MMIの`inspect`/`select`を呼ぶ参照接続（書込み・権限は未検証）
- [SEI decision-memory参照接続](tools/reference-sei-decision/README.md) — SCN-001の未決決定をSEIの一時storeへ記録し、`resume`を読む参照（合成fixture）
- [SCN-001統合参照実行](tools/reference-scn001-run/README.md) — MMI・SEI・SCN-001評価を1つのreceiptへ束ね、development-review-onlyの仮承認とOwner判断packetを生成する（公開承認ではない）
- [SCN-001レビュー用成果物](tools/reference-scn001-render/README.md) — D-04を内部レビュー用Markdownとして生成する（公開用ではない）
- [TEIモデル検証接続](tools/reference-tei-model/README.md) — SCN-001のObservation/RuleCandidate型をTEIでvalidateする（意味・実データは未検証）
- [公開gate](tools/reference-publication-gate/README.md) — R-01〜R-07の状態から公開可否だけを判定する（現在はblocked）
- [SUI API到達性probe](tools/reference-sui-api/README.md) — `/healthz`・`/openapi.json`・`/docs`・DocumentV1を読む（実資料・認可は未検証）
- [SUI→SCN-001対応](tools/reference-sui-link/README.md) — SUIのcard digestとisland構成をSCN-001観測へ照合する
- [EKI CLI起動probe](tools/reference-eki-cli/README.md) — `eki-control`/`eki-agent`のversionだけを確認する（委任・Authorityは未検証）
- [EKI Control API認証probe](tools/reference-eki-api/README.md) — `GET /v1/tasks`の405で認証通過を確認する（Task送信は未実施）

## 検証

GitHub Actionsの`tai-reference`が、`tools/`配下のGo参照実装に対して`gofmt`、`go vet`、`go test`を実行します。MMI・SEIの実接続試験は、それぞれの開発チェックアウトがない環境ではskipします。保存済みのSCN-001参照実行recordは常に検証します。

## 作業領域

- [docs/](docs/) — 目的・設計・判断経緯
- [scenarios/](scenarios/) — 個人・組織・社会の利用シナリオ
- [integrations/](integrations/) — 既存基盤との必要最小限の接続
- [evaluations/](evaluations/) — 評価基準・試験・検証記録

開発エージェントは [AGENTS.md](AGENTS.md) を参照してください。
