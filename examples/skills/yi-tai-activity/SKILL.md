---
name: yi-tai-activity
description: >-
  YI Constellationで、利用者の一つの課題をSEI/SUI/TEI/SHO/EKIなどの製品へ
  必要に応じて分担し、出典・未決・権限・結果を保って活動を続けるときに使う。
  単独製品で十分な場合はその製品のSkill/CLIを直接使い、横断処理を増やさない。
---

# TAI Activity：目的に必要な能力を組み合わせる（試作）

> **試作・NOT RUN**：このSkillは配布前の設計・評価サンプルである。ここに書いた手順や製品名は、CLI/MCP接続や実行権限が現在のHarnessに存在することを保証しない。YIブランドは製品別契約の正本ではない。

## 適用範囲

- 利用者が調査→判断→設計/文書化→委任→結果評価まで、一連のActivityの継続を求める場合に利用する。
- モデリングだけならTEI Skill、既存表の文書参照だけならMMI Skill、文書編集だけならSHO Skill等を優先できる。TAIの利用は任意とする。
- SEIは根拠・判断・専門Method、SUIは仮説と意味形成、TEIはモデル・生成・検証、SHOは文書、EKIは委任と独立結果確認の責任を持つ。

## 作業手順

1. **依頼を目的・用途に落とす**。何を改善したいか、対象/時点、許可された資料、望む成果、本人・Owner判断が必要な箇所を確認する。必要以上の情報収集・通知を前提にしない。
2. **実際に使える能力を確認する**。利用可能な各製品のSkillと現行CLI/API/MCP Toolの存在・バージョン・実接続を照合する。`SKILL.md`中の説明や任意のTool annotationだけで利用可能性・実効権限を断定しない。未搭載機能を実在するコマンドとして生成しない。
3. **必要な製品だけを選ぶ**。依頼を各Productの専門責務に対応させる。各製品の原Source・Meaning・Resultの正本を尊重する。利用者の目的に必要なければ追加Tool/Skillをロードしない。
4. **開示条件に従って受け渡す**。Source保持側が許可するProjectionのみを外部Harness・別Productに渡す。Raw・秘密・非公開の構造情報・権限Grantを転送しない。見えない対象の全体件数や真偽を推定で確定しない。
5. **提案・検証・採否・作用を区別する**。観測、仮説、専門Method提案、歴史的accepted、現在の適用性、Owner意味受理、Tool実行、外部Effectのどの段階か明示する。正本側から得た状態を再解釈して勝手に昇格させない。
6. **作用時点を検証する**。書込み・公開・外部作用の前に各Product/Host/Providerによる現時点の権限・Target・revision・期限を確認する。失敗・結果不明での無条件の再試行を避ける。Tool responseと正式Receiptおよび実結果を分離する。
7. **活動を引き継げる形にする**。利用者の目的、許可範囲、使用したSource revision、対象・時点、確認できた根拠、候補/未決、作成物、各Productが検証した事項、現在の実効果/未知、次の候補を最小限の参照で提示する。別Harnessへ秘密・Raw・不必要な内部推論をコピーしない。
8. **能力不足を明記して縮退する**。Skill/MCP/CLIの未設置、ネットワーク断、OS制限などは`unsupported/unavailable`として区別し、許される読み取り・文書作業などを継続する。

## 結果の書き方

次の見出しは必要に応じてのみ使う：`目的・対象`、`使用したProduct／版`、`確認できた資料と出典`、`仮説・未決`、`提案／実装／意味受理／外部作用の別`、`検証した結果と未実施`、`次に必要な作業`。

検証可能な情報はSource/Tool/Receiptへ戻れる参照を付ける。実行できなかったことや、入力を受領しただけの状態を「完了」と書かない。Ownerの採否は製品ごとの既存経路に残す。

## 関連

- [横断設計](../../../docs/yi-constellation/harness-skill-plugin-plan-2026-11-02.md)
- [評価票](../../../evaluations/SK-01-harness-skills.md)
- [TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)
- [MMI既存Skill](https://github.com/hat47x/markdown-matrix-injector/blob/main/skills/mmi/SKILL.md)

本ファイルは`examples/`内のportable Skill例であり、各Harnessへの自動インストール・Plugin配布は行わない。
