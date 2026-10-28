# コントリビューション

TAI Pleromaは初期開発中です。変更は小さく、検証可能な単位で送ってください。

## 進め方

1. 既存のIssue・PR・docsを確認する。
2. 変更の目的、境界、未検証事項をIssueまたはPR本文へ書く。
3. 最新の`main`から短命ブランチを作る。
4. 変更に対応するtestを追加・更新する。
5. CIを確認してからPRを統合する。

## 禁止事項

- 実在の顧客資料、個人情報、認証情報、非公開の作業資料をコミットしない。
- 非公開リソースの内容を、この公開リポジトリへ複製しない。
- AIの提案を、業務上の承認・公開権限・Authorityとして扱わない。
- 合成fixtureの成功を、実システムでの成功として主張しない。

## 検証

- Go: `gofmt -l .`、`go vet ./...`、`go test ./... -count=1`
- Python: `python -m unittest -v ...`
- 公開境界: `python tools/check-public-boundary/check.py --root .`
- CI: `.github/workflows/tai-reference.yml`

## 文書

- 日本語を基本とし、識別子・API名・コマンドは原表記を保つ。
- 状態（要件、提案、実装済み、検証済み、未検証）を混ぜない。
- 実データを使わず、合成fixtureで再現できる形にする。

## ライセンス

貢献はMITライセンスの下で受け入れます。詳細は[LICENSE](LICENSE)を参照してください。
