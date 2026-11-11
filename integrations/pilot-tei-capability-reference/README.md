# TEI能力参照パイロット（TAI側の最小経路）

状態: **実装済み・限定検証済み（2026-11-11）**。提案・採用判断ではない。TAIからTEIの製品構成・能力参照・活動継続に必要な情報を、TEIの既存read-only CLIの型付きJSONだけから提示する最小経路である。

## 何をするか

- 実CLIの`version`でTool可用性を確かめ、`model overview`で製品構成の限定一覧、`model catalog`で能力の限定一覧を取得する。
- 選択した`semantic-capability`について、`inspect`（定義・Source位置・fingerprint）、`knowledge-context -disclose`（指定したDisclosure Scopeだけ）、`knowledge-review-plan`（継続時のレビュー順・停止規則）、`trace`（snapshot fingerprint）を取得する。
- TAI側の表示（`view`、JSON/Markdown）、消費者への限定Handoff（`handoff`）、受領記録（`receipt`）、Revision比較（`compare`）、古いRevisionの検査（`verify-consumer`）を提供する。

TEIへ渡す要求は、**選択対象（Subject）・Workspace/Source・要求するDisclosure Scopeだけ**である。会話、Workspace全体の内容、別Productのデータを暗黙に送らない。

## 何をしないか

- TEIの機能をTAIへ移植しない。TAI専用の新しい共通Agent Host、Registry、Scheduler、正本Storeを作らない。
- 製品構成全体や公開Capability契約を変更しない。変更が必要なら独立レビューの対象にする。
- TEIの候補・診断を、TAIの活動判断・操作許可・業務Effectの証拠へ自動昇格しない。
- Product Skillの実Load、外部Harnessの実Tool呼出し、実Consumerへの配送を、このパイロットのPASSから推定しない。

## 区別する5つの状態

| 次元 | 出力での表現 | 観測方法 | 推定してはいけないこと |
| --- | --- | --- | --- |
| Product Capability | `declared` / `not-found` / `unknown` | `inspect`の型付き結果と診断コード | そのActivityで利用可能・実行可能という意味 |
| Tool availability | `available` / `unavailable` | `version -json`が契約を返したか | Product Capabilityの有無 |
| Skill load | `not-observed` | このツールでは観測しない | CLI成功＝Skillロード成功 |
| Execution authority | `not-evaluated` / `not-granted` | 要求Grantなし。TEIの`authorityLimits`を保持 | 読取り成功＝操作許可 |
| Consumer receipt | `not-delivered` / `received` / `fresh` / `stale` | 明示HandoffとRevision照合 | 受領＝現在資格・活動判断 |

`not-found`は**指定したSubject IDの不在**であり、製品全体に能力が無いことの証明ではない。Tool不在の場合は`productCapability`を`unknown`に保ち、`not-found`へ落とさない。

## 使い方

```bash
python integrations/pilot-tei-capability-reference/tei_capability_reference.py observe \
  --tei <tei executable> \
  --workspace <TEI workspace> \
  --subject semantic-capability:sales.order.submit \
  --disclosure definition,source,dependencies \
  --format markdown \
  --out view.md
```

```bash
python integrations/pilot-tei-capability-reference/tei_capability_reference.py handoff \
  --view view.json --consumer tai-activity-session-1 \
  --disclosure definition,source --out handoff.json
python integrations/pilot-tei-capability-reference/tei_capability_reference.py receipt \
  --envelope handoff.json --consumer tai-activity-session-1 --out receipt.json
python integrations/pilot-tei-capability-reference/tei_capability_reference.py compare \
  --before view1.json --after view2.json --out delta.json
python integrations/pilot-tei-capability-reference/tei_capability_reference.py verify-consumer \
  --receipt receipt.json --tei <tei executable> --workspace <TEI workspace> --out check.json
```

`observe`は`--disclosure`が必須で、空または未知のSectionを拒否する。`handoff`もDisclosure Scopeが空なら拒否する。Handoffの鍵は固定allowlistで、`conversation`、`transcript`、`messages`、Workspace全体のbytesを運ばない。

## 4つのシナリオ検証

同じActivity IDで、実CLIに対して次を確認する。

| ID | 条件 | 期待する観測 |
| --- | --- | --- |
| R1 | TEI参照が成功する | `declared`、Source位置とfingerprint、限定能力一覧、Review Plan |
| R2 | 対象が見つからない | `SUBJECT_NOT_FOUND`、`not-found`、製品構成は引き続き観測 |
| R3 | Sourceが更新された | `worldFingerprint`・`sourceIndexFingerprint`・`modelRevision`・artifactの変化と`requalificationRequired` |
| R4 | Consumerが古い結果を受け取る | `stale`、TEIの`STALE_SNAPSHOT`、`requalification-required` |
| H1 | Handoffの最小性 | 選択・Source・Revision・Disclosure Scopeだけを運び、空Scopeを拒否 |
| N1 | Tool不在 | `toolAvailability=unavailable`、`productCapability=unknown` |

実行:

```bash
python integrations/pilot-tei-capability-reference/run_scenarios.py \
  --tei <tei executable> --workspace <TEI>/reference/workspace \
  --out evaluations/records/TAI-TEI-capability-reference-2026-11-11.json
```

2026-11-11の実行結果は[evaluations/records/TAI-TEI-capability-reference-2026-11-11.json](../../evaluations/records/TAI-TEI-capability-reference-2026-11-11.json)に記録した。固定した対象は次のとおり。

- TEI main `b8cbd432aae22ccf3fa75b0119e1d90d87ef0d11`をWindows向けにビルドした実CLI（`tei version -json`の`vcsRevision`と一致）
- 公開`reference/workspace`（manifest `sha256:8e367b05…f471af74`）
- `semantic-capability:sales.order.submit`、Disclosure Scope `definition,source,dependencies`

**NOT RUN**: 外部Harness SessionでのProduct Skill実Load、実Tool実行・意味受理・実行権限、別Productの実Consumerへの配送、公開Reference以外のWorkspace・権限・OS隔離。合成のScenario PASSを実システムの完了やOwner受理へ読み替えない。

## 境界と独立レビュー

このパイロットはTAIリポジトリ内の接続実装・試験・記録だけを変更する。TEIのKernel、Plugin契約、製品構成、公開Capability契約、OwnerのAuthorityは変更しない。製品構成全体や公開Capability契約の変更が必要になった場合は、このパイロットの延長として扱わず、対象ProductのIssueで独立レビューを受ける。

設計と段階の詳細は[docs/yi-constellation/tei-capability-reference-integration-2026-11-11.md](../../docs/yi-constellation/tei-capability-reference-integration-2026-11-11.md)を参照する。
