// 進捗(p, 0-100%)と規模点(w, 相対工数)の見積もり。根拠は product-progress.md を参照。
// w は同一リポジトリ内の相対的な工数。リポジトリ間では比較しない。
module.exports = {
  asof: '2026-10-04',
  repos: [
    {
      id: 'tei', name: 'tei-platform（鼎 TEI）', start: '2026-08-29', kind: 'ローコード基盤（意味・実装・実行・観測の分離）',
      features: [
        ['M0 上位基線（価値・要求・PAS）', 95, 3, '価値・要求33件・受入シナリオの正本あり'],
        ['M1 意味とSource（Canonical identity）', 80, 8, 'native source・派生索引・Diagnosticが接続。Plugin/DSLは設計段階'],
        ['M2 Application・既存互換', 75, 10, 'Gate A Ready。実外部資産（Oracle等）の保証は別'],
        ['M3 Driver実証（認証〜Command〜Observation）', 85, 10, 'Gate B Ready（実PostgreSQL含む3系統のactual Evidence）'],
        ['M4 第一Web Target', 70, 10, 'Gate C Ready。R7 Replayable Behaviorは設計進行中・未実行'],
        ['M5 第二Application／Target', 25, 10, 'ISSUE-000040 S5〜S8完了。Target Projectionは未評価'],
        ['M6 Studioの安全な編集（Accept/Reject）', 30, 12, 'review fingerprintに束縛したaccept、RQ-027/028を実装中'],
        ['M7 知識探索・AI提案', 15, 14, 'semantic extension architecture（RQ-031〜033）を設計中'],
        ['M8 Provider・Runtime交換', 8, 10, 'spike・設計のみ'],
        ['M9 実利用の運用境界（HA・供給網・監査）', 2, 13, '未着手']
      ]
    },
    {
      id: 'sei', name: 'sei-cognition（井 SEI）', start: '2026-08-31', kind: '認知・意思決定基盤（意味境界・Provenance）',
      features: [
        ['Semantic Contract群（5契約＋2 Profile）', 85, 8, 'v1alpha1。fixture範囲のExecutable Evidenceあり'],
        ['Semantic runtime（Go）・Verifier Registry', 75, 10, 'v0.2.0で同梱。実運用の負荷・互換は未確認'],
        ['Product Interaction（resume-first）', 60, 8, 'first usable slice。実人間レビュー待ち'],
        ['Local Single-Node Packaging', 55, 6, 'v0.2.0 Linux/amd64 reference package。他profileは未'],
        ['Product Access／Collaboration分離', 45, 6, '責務分離probeまで'],
        ['Provider／Realization portability', 50, 9, 'TEI・Ollamaの版交換・歴史的再構成。ISSUE-000072/74はOpen'],
        ['Cognitive Method（KJ Atlas等）', 40, 9, 'stub／実modelで実行。成果品質の人間評価は未'],
        ['探索評価（SACS等の疎連想認知）', 35, 8, '探索段階。要求へ未昇格'],
        ['E4 Operational portability', 3, 8, 'Not Yet Verified'],
        ['PMS-08 運用・採用Evidence', 0, 10, 'Not Yet Verified']
      ]
    },
    {
      id: 'sui', name: 'sui-sensemaking', start: '2026-02-08', kind: '定性データのKJ法系sensemakingキャンバス',
      features: [
        ['KJキャンバス（カード・島・関係・保留）', 85, 8, '実装済み（ROADMAP「現在地」）'],
        ['インポート（Markdown／ZIP）', 80, 4, '堅牢化済み'],
        ['SafeModeの共有・書き出し', 80, 5, '未レビュー本文を出さない確認まで'],
        ['永続化・認証・マルチテナント', 75, 10, 'RDB content store、guest admission、監査。DB移植性は検証済み範囲あり'],
        ['外部AIとの提案やり取り（AI-IR）', 65, 6, 'LLM入力の中間表現が完了。規模対応は未決'],
        ['check-narrative の規模対応', 55, 3, '全量送信で約14万トークン。分割要否を判断中'],
        ['価値検証（T2/T3パイロット）', 30, 6, 'T3はprovisional。T2（実務）で確認が次'],
        ['認知支援候補層（ADR-0090）', 25, 7, '決定論的候補をT2で確認する段階'],
        ['UI・アクセシビリティ', 70, 5, 'キーボード／スクリーンリーダ受入スクリプトあり'],
        ['大規模な質的統合（カード統合・島の階層化）', 5, 10, '将来候補（約束ではない）'],
        ['定額制・オフラインAI協働', 20, 4, '将来候補']
      ]
    },
    {
      id: 'mmi', name: 'markdown-matrix-injector（MMI）', start: '2026-03-19', kind: 'VS Code拡張＋MMI記法（表の読み取り専用参照）',
      features: [
        ['埋め込み記法とデータ源（xlsx/csv/xml）', 95, 6, 'v0.1.0。Issue 190/211件がDone'],
        ['クエリパラメータ・Smart Fallback・印刷制御', 90, 5, '実PDFで再現実証済み'],
        ['Diagnostics・補完・貼り付け/D&D', 85, 5, '一部の視覚確認はmanual-e2e待ち'],
        ['納品マニフェスト・プレビュー・パッケージ', 80, 4, '.vsix配布。Marketplace公開は準備中'],
        ['MMI Notation v1仕様＋適合コーパス（L0〜L3）', 80, 5, '20ケースのexecutable corpus'],
        ['ドキュメント・実務サンプル12本', 85, 3, 'チュートリアル・マニュアル・動画'],
        ['取り込み補助（表・画像・階層→標準Markdown、台帳）', 45, 12, 'Phase 13 認知支援層を実装中'],
        ['共通Core・CLI・他ホスト対応', 15, 10, '構想段階'],
        ['Marketplace／Releases公開', 20, 3, '公開準備中']
      ]
    },
    {
      id: 'vs', name: 'vs-bear-simulator', start: '2026-09-19', kind: 'Godot製PCゲーム（v1.x Encounter Core）',
      features: [
        ['M0 Foundation・再現可能ビルド', 100, 3, 'main統合済み'],
        ['M1 Ringの縦切り', 100, 6, 'main統合済み（Ring全周テラス化まで）'],
        ['M2 クマの物理・感覚運動の基線', 90, 10, '製品用クマモデル v1.10.0まで'],
        ['M3 Simulation／Recorder／Replay', 90, 8, 'main統合済み'],
        ['M4 アーカイブ・結末・実績', 85, 7, 'main統合済み'],
        ['M5 生物着想認知の決定ゲート', 50, 8, '実験基盤のみ。採用候補なし（決定論基線で出荷可）'],
        ['M6 演出・アセット確定', 35, 12, 'クマ造形は進行。人間・環境・UIは途上'],
        ['M7 Steam出荷準備', 5, 10, 'ストア文面の設計のみ'],
        ['M8 リリース候補', 0, 8, '未着手']
      ]
    },
    {
      id: 'eki', name: 'eki-fabric（益 EKI）', start: '2026-09-12', kind: '遊休計算資源の安全な分散実行基盤',
      features: [
        ['アーキテクチャ設計基線（上流）', 80, 6, 'architecture／ADR／DEPLOYMENT_PROFILES'],
        ['Task Admission・Suitability Gate', 40, 4, 'pure boundaryのみ'],
        ['Durable Task／Attempt／Lease状態', 45, 7, 'taskstate＋StateStore SPI'],
        ['Placement Authorization・WorkOrder署名', 35, 6, 'authority・contract・COSE decoder'],
        ['External Client API', 8, 5, 'cmd/eki-controlの骨組み'],
        ['Baseline Scheduler', 5, 5, '未実装'],
        ['Worker Agent・Local Governor', 8, 8, 'spikeのみ'],
        ['Executor Runtime', 5, 8, '未実装'],
        ['Artifact Store・ArtifactGrant', 10, 7, 'spikeのみ'],
        ['結果検証・受理', 15, 6, 'spike（独立検証）'],
        ['Telemetry・Audit', 5, 4, '未実装'],
        ['Security Conformance Suite（C1〜C6）', 15, 8, '一部をcore側テストで先行']
      ]
    },
    {
      id: 'csw', name: 'cultural-substrate-weaving（CSW）', start: '2026-07-26', kind: '生成AI向け補助スキル（文化体系を触媒にした統合）',
      features: [
        ['中核スキル（probe／preview／de-binding）', 85, 8, 'v0.4.0公開、v0.5.0開発中'],
        ['多プラットフォーム配布（Claude Code／Codex／ChatGPT／M365）', 75, 6, 'ja／en、M365アダプタ再設計済み'],
        ['ビルド・検証・手動リリースゲート', 85, 4, 'Actions停止後のローカルゲート整備済み'],
        ['英語runtime', 60, 5, ''],
        ['Living Lab（実作業での観測記録）', 50, 6, 'Schema 0.2'],
        ['文化フレームワーク・コーパス拡張', 45, 7, ''],
        ['affinity-synthesis（研究プロトタイプ）', 40, 8, '独立公開はまだ'],
        ['iterative-inquiry-synthesis（研究プロトタイプ）', 30, 8, ''],
        ['認知機能の段階的改善（4段階）', 25, 8, '第1段階の独立試行まで'],
        ['効果の実証（product quality program）', 30, 9, '効果検証は継続中']
      ]
    }
  ]
};
