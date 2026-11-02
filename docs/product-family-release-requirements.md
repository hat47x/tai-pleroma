# シリーズ統合ビルド・リリース要求／受入条件（Draft v0）

状態: **すべて提案／NOT RUN**。製品間の統合ビルドや公開Releaseが成立したという報告ではない。  
参照: [全体アーキテクチャ](product-family-delivery.md)、[Website構想](yi-constellation-website.md)、[Issue #74](https://github.com/hat47x/tai-pleroma/issues/74)、TAI [現況](status.md)、[参照CI](../.github/workflows/tai-reference.yml)。

## 1. 受入要求案

| ID | 要求候補 | 検査/受入の焦点 |
| --- | --- | --- |
| DLV-01 | YI Constellation／TAI Pleroma／TAI repository／各製品／bundleを区別 | 名前が似ていてもProduct IDやOwner権限を自動共有しない |
| DLV-02 | 実装・製品固有テスト・Release受入は各Product Ownerの正本を参照 | TAIのbundle PASSは各Productの意味受理を代行しない |
| DLV-03 | 製品別の固定commit・Artifact digest・Platform/Profileを持つ | `latest`参照、checksum未照合を再現可能な配布とは呼ばない |
| DLV-04 | 配布構成ごとの**必須／任意**部品と適合性条件を明記 | 欠品した必須部品のとき、構成全体をReadyにしない |
| DLV-05 | 候補、取得、検証、組立て、審査、公開の状態を分ける | source取得済み=テスト済み=公開承認の短絡禁止 |
| DLV-06 | 製品別の証拠と、bundle内の製品間証拠を区別 | 個別CI PASSだけで製品間互換のPASSは出さない |
| DLV-07 | 観測できなかったことと失敗したことを分ける | skipped、not-run、unavailableを成功扱いにしない |
| DLV-08 | ロールバック時にも過去bundle manifest/署名/利用条件を残す | A→B→Aで旧承認を無条件に復活させない |
| DLV-09 | 配布物のライセンス・第三者著作物・機密性・脆弱性等の確認 | 権利未確認の成果物を公開配布しない |
| DLV-10 | 公開対象のノード/辺/ログ/数値/エラーを独立に検査 | 非公開Productの存在や内部パスを公開サイトから推測させない |
| DLV-11 | 構成ごとの導入・更新・障害時復旧手順を用意 | インストーラ不在で再現に必要な手順が欠落しない |
| DLV-12 | YIサイトをTAI内で制作しつつ、コンテンツ審査を独立させる | 公開サイトが未受入の実装・社会的効果を保証しない |
| DLV-13 | 単体製品の利用を妨げない。全製品の同時ビルド・同梱は必須にしない | 特定TAI HostやTAIサービス障害で単体Productを不必要に停止させない |
| DLV-14 | 設定・鍵・管理者権限はbundle作成と本番利用で分離する | TAIのビルド権限が他製品の実行権限になることを拒否 |
| DLV-15 | 最初は小規模なprofileで、実際の利用者が導入できるか測定する | 「複雑な仕組みを構築した」だけで価値があるとしない |

番号はIssue #74に対応する候補ID。正式なSchema、全製品に対する強制Contract、運用SLOは未採用。

## 2. Versionと受入単位

最低限別々に識別するもの:

- **Product Version**: 製品自身が保守・公開するバージョン。
- **Artifact Revision/Digest**: 取り込んだ実際のバイナリ・ソース・パッケージを固定する値。
- **Bundle Revision**: 複数のProduct Version／Artifactを組み合わせた構成の識別。
- **Website Publication Revision**: 記述内容、画面と図、リンクの公開版。
- **Scenario/Evidence Revision**: SCN-001等の検証対象、実行範囲、Human Acceptanceの記録。

`same UI name`、`same tag`、`same byte contents`であっても、Source revision・配置条件・受入者が変わる場合は無条件に前の判断を再使用しない。[TAI #33](https://github.com/hat47x/tai-pleroma/issues/33)のA→B→A型の問題を、シリーズ構成にも明示して検査する。

## 3. 配布フロー案と停止条件

```text
Product's own release process
  ↓  exact source/artifact/version
TAI: Acquire & Pin
  ↓  verify digest, platform, license/rights, visibility
TAI: Resolve Profile
  ↓  required components all available; optional limitations explicit
TAI: Integration Validate
  ↓  static/synthetic/live evidence distinguished
TAI: Assemble & Document
  ↓  install/update/rollback guidance + provenance manifest
Independent Review & Publication
  ↓  only approved binary/site/scenario publication channel
```

**停止/保留条件**: 固定した対象を取得できない、digestが不一致、必須Productの版が不明、互換性根拠がない、ライセンス/配布権が未確定、秘密情報混入、受理者・公開権限が不明、実行した試験を特定できない。採否を待つものは`pending`、検証未実行は`not-run`、失敗は`failed`と分ける。

**結果の区別**: packageの組立て成功はユーザー導入成功ではない。利用者の意味上の受入や成果確認までを、自動化されたbuild pipelineのPASSから推論しない。

## 4. 負例とテスト計画（いずれもNOT RUN）

| ID | 入力／失敗例 | 期待される結果 | 初期Gate |
| --- | --- | --- | --- |
| DLV-N01 | Product `latest`と未固定外部URLのみ | 再現可能なbundleと宣言しない | G1 |
| DLV-N02 | Artifact digestが不一致 | 配布対象から除外し失敗根拠を保持 | G1 |
| DLV-N03 | 必須Productをskip、CI jobだけ緑 | bundle PASSにしない | G2 |
| DLV-N04 | 二製品は単体PASS、API契約に不整合 | 結合不適合として停止 | G2 |
| DLV-N05 | Builderの機密資産と可視化用公開manifestが混在 | 秘密と存在・数・エラーの漏洩を拒否 | G1→G3 |
| DLV-N06 | 旧bundle Aの構成へ戻る | 新たな受入なしに旧release権限を再使用しない | G2 |
| DLV-N07 | Site公開OKだが実資料のシナリオ公開がblocked | サイトの案内と個別シナリオ成果公開を分離 | G3 |
| DLV-N08 | 製品単体releaseが更新されたがTAI bundle未検証 | バンドルの構成を自動更新しない | G1→G2 |
| DLV-N09 | オフライン・単体使用でもTAI中央サービス必須 | 不必要な強制依存を設計で拒否 | G0 |
| DLV-N10 | ProductのCIにアクセスできない | 不存在やPASSと断定せず取得不能を明示 | G1 |
| DLV-N11 | 配布物を作成できたがインストール手順なし | 導入可能として配布しない | G3 |
| DLV-N12 | サイトの製品説明に未検証実績が混入 | Brand content reviewで公開保留 | G3 |

## 5. 道筋と「導入しない」判断

- **G0（文書）**: 価値・所有元・サイトと配布の境界、対象範囲をOwnerレビュー。独立したYIリポジトリは作らない。
- **G1（小さな候補構成）**: 一つの開発用profileの固定版マニフェスト。source/Artifact実物とリンクし、checksum・ライセンス・公開範囲を点検。全製品を必須にしない。
- **G2（組合せ検証）**: 必要な二つ以上の製品間で、現実のパッケージを用いて互換性、failure、retries等を検査する。モックの成功と独立した結果確認を区別する。
- **G3（配布可能性）**: install/update/rollbackを実演、review recordを残す。各製品側の固有受入との整合性を確認。
- **G4（サイト公開）**: ブランドページ、製品ページ、課題別ガイド、版付き配布案内をTAIから制作し審査。サイトはG2/G3を終えていない機能を「開発中」と説明してもよいが、公開済み配布物と誤認させない。

**縮小条件**: 累積メンテナンス費用が導入価値を超え、複数製品の結合が利用者の課題に不要なら、TAIは単に固定版へのリンクとシナリオガイドだけを維持してよい。大規模なビルド基盤は作らない。

## 6. 境界の証拠（固定時点）

- TAI main `88a6fad6d088f98ccab6080b3b7be24b62399113`: [workflow](../.github/workflows/tai-reference.yml)はGo/Python参照試験。シリーズ構成マニフェスト・自動リリースの実装とは違う。
- [TAI status](status.md)（2026-10-26更新）: SCN-001が合成試験で、公開はblocked。EKIではTask受付とWorker実行を区別。
- [TAI Product Landscape Draft #72](https://github.com/hat47x/tai-pleroma/pull/72)／[G1分類 Issue #73](https://github.com/hat47x/tai-pleroma/issues/73): 対象をProduct/Repository/Methodとして正確に扱うためのレビュー。ここで先に正式Product IDを発行しない。
