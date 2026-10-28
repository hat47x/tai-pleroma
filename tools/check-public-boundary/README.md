# 公開境界の検査

公開リポジトリのtracked fileに、非公開リソース名・秘密鍵・代表的なtokenの混入がないかを検査します。

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

## 検出するもの

- 非公開リソースのリポジトリ名
- PEM秘密鍵の開始マーカー
- GitHub token、AWS access keyの代表的なprefix
- 特定のローカル絶対パス

## 境界

- これは回帰防止の補助検査であり、GitHub secret scanningや履歴全体の監査を置き換えません。
- 検出しない秘密情報を「存在しない」と主張するものではありません。
- バイナリファイルとGit履歴は対象外です。
