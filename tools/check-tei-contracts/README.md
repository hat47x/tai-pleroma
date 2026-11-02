# TEIプロダクト能力連鎖の検査

TEIの`reference/product-contracts`から取得したcapability定義を使い、EKIの能力連鎖とSUI/SEI/MMIの同一性を確認します。

```text
eki_task_submit: TaskRequest -> Attempt
eki_attempt_execute: Attempt -> ResultClaim
eki_result_accept: ResultClaim -> AcceptedResult
```

- 前段の`output`が次段の`input`と一致すること。
- SUI/SEI/MMIの能力が入力と出力で同じ型を保つこと。
- TEIの`worldFingerprint`と`sourceIndexFingerprint`が記録されていること。

## 実行

```text
python -m unittest -v check_test.py
python check.py --root ../..
```

## 境界

- TEIの型宣言から取得した能力の整合性確認です。
- 実装・権限・Result Acceptanceではありません。
- 公開gateはblockedのままです。
