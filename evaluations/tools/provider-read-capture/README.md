# 実Provider Read証拠の取得用ハーネス（評価者が使う。製品コードではない）

`judge-provider-read-requalification.cjs` が読む入力を作る手順。TEIのリポジトリには変更を加えず、使い捨てのアーカイブコピーで実行する。

1. 試験対象のTEI版を `git archive` で使い捨てディレクトリへ展開する（試験時は Draft #4076 の head `5a8fac512e370171c1e63d436ece27ad8e5a7aa6`。mainには実Provider Readの入口が無い）。
2. `capture_probe_test.go.txt` を `internal/driver/queryruntime/postgres/zz_probe_test.go` として置く。製品の `Resolver.ExecuteBrowseQueryInEnvironment` と `postgresquery.Executor` を呼び、**同じ1本の接続**でProviderの申告（クラスタ識別子、DB名とOID、接続ユーザー、RLS迂回権限、表のRLS有無）を読取の前後に取る。作成・更新・投入は一切しない（セッションは読み取り専用に固定）。
3. 使い捨てPostgreSQL（127.0.0.1のみ。合成データ `seed.sql`）に対し、`T3A_DSN` `T3A_WS` `T3A_OUT` `T3A_READS` を環境変数で渡して実行する。
4. 変種は、Workspaceのコピーを編集する（定義側）か、**同じDBを書き換えて戻す**（データ側。DBを複製するとDB OIDが変わり、Provider同一性の判定が誤る）。接続先DBやRoleを変えるのは、Provider側の変種。
5. `tei inspect -subject-kind query|application-pattern -subject-id order_entry.recent_orders` の応答を、ケースごとに `<case>.inspect-query.json` `<case>.inspect-pattern.json` として保存する。
6. `node judge-provider-read-requalification.cjs --dir <出力先> --history base --claims claims.example.json --out judge-result.json`。期待は評価者が別に用意し、`score-provider-read-requalification.cjs` に渡す。

実PostgreSQLの資格情報・実データは使わない。コンテナは試験後に削除する。
