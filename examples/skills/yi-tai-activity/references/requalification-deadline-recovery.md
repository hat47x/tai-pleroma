# 再資格化・期限・回復の手順（必要時だけ参照）

> **評価資料・Product実動作未受理**。このファイルは[TAI Activity Skill](../SKILL.md)が必要な場合にだけ参照する詳細手順。旧rootの該当節を省略せず分離した。製品Skillの実ロード・実Tool呼出し、Host Grant/Disclosure/Owner意味受理を保証しない。

## 過去の成果を再利用する前の局所再確認（評価用）

- **現在の問いに必要な証拠を特定する。** Source/Rule/Oracle/取得Snapshot/型・粒度・意味版、Skillの参照Script・実Tool/Host、文書Template/公開Artifact、現在の開示・実行権限を別々に確認する。必要な依存関係が不明なら過去のPASSを現在の全面PASSへ昇格させない。
- **影響するClaimだけ再評価候補とする。** 例えばD1だけに依存する既存の集計は無関係のD2変更で一律失効させず、D1×D2のJOINは再評価対象。依存が完全に観測できなければ、影響なしと断定せず不明としてProduct Ownerに照会する。
- **共同結論は別に成立条件を確認する。** SEI/TEI/SHO等の局所結果がそれぞれPASSしても、同じSource/Scope/Grain/epoch/Claimであるかは追加の証拠が必要。古いSnapshotや別Consumerの結果を単純に結合しない。
- **現在の権限は都度Product/Hostに確認する。** Model/Skill/Manifest/過去Trustが同じでも、現在のHost Grant・Issuer・外部開示は別。確認不能なEffect/送出を保留し、公開合成資料による独立read-only作業は継続可能な範囲で行う。

[SK-01 §P／SK-RQ01〜12](../../../../evaluations/SK-01-harness-skills.md)は以上の指針に対する公開合成受入案。実製品の再評価API・独立Oracle・Effect認可を本Skillが実装したという意味ではない。

## Activity再開とProduct別の選択的再資格化（評価案）

前のSession/Agent/Skillの「成功」「検証済み」を、別のSource・時点・Provider・Consumer/Hostへ自動的に移植しない。**履歴として当時成立した観測**と、**現在の目的にその結果を利用できる資格**を別々に説明する。

- 目的のClaim・Scope・時点に必要なTEI Source/意味Role・Rule、SEI Method、EKI Task/Attempt/Body、SHO Source Occurrence・実読取版、Host Current Grant/Trustの**存在する参照**を調べる。存在しないToolや証拠は未実施・unknownで扱う。
- 変更されたSource/能力/Methodと、実際に受理済みの依存関係に基づき、再確認の必要なProductだけを選ぶ。Edgeが不明なら「無影響」と推測しない。無関係な履歴・独立作業は利用可能な範囲で継続する。
- EKIのClaim ACKをBody実受領にせず、Body digest照合をSHOの実読取・固定納品にせず、生成Artifactの存在を利用者の受取にしない。遅延Bodyを再確認することと、別Attemptの効果を再実行することを分ける。
- 以前のGrantやTrust Bundleの成功では現在の危険操作は許可されない。現在の実Host資格と開示範囲が不明な操作は保留し、権限のあるread-only調査や説明は続けられる。
- 秘密・非公開のSource/Capability/Tool/結果/診断はConsumerごとに許可されたProjectionへ落とし、活動引継ぎ票自体も情報公開対象として扱う。

[選択的再資格化の計画](../../../../docs/yi-constellation/activity-selective-requalification-and-handoff-2026-11-02.md)と[SK-01 SK-C](../../../../evaluations/SK-01-harness-skills.md)は**公開合成だけの評価案**。現行TAI Skillが新しい実行器、Oracle、中央Claim DB、Provider、Owner受理資格を取得した証拠ではない。

## Taskの期限・成果の品質期限・回復可能性を扱う場合（評価案）

- 利用者の明示した**最大lead time、求める成果の質、費用上限、開示先、許容中断・回復範囲**を確認し、Product／Harness候補と実権限を比較する。Taskに無い数値・SLA・許可をSkillが創作しない。所要時間分布や復旧余裕に証拠がないときは、安価な候補を「期限内成功確実」と報告しない。
- まずSource/意味・Tool/CLI実在性・Audience/Host Grant・品質要件を守り、次に期限内の成功可能性と回復余裕、その後に実Token/Tool/人手/料金を比較。Rate Limitの一時停止とQuotaの枠切れ、定額権利と課金APIは別。無断で有料経路・別Audienceへ切り替えない。
- **実行時間と品質確認時間を分ける**。EKI `COMPLETED`／Agentの回答完了は、必要なTEI品質CheckSet・対象Scope・Snapshot・有効期限・例外採否・SHO Consumer再読取を証明しない。必要な検査をProduct Ownerが指定していなければ、全件をブロックする汎用Quality Gateは追加しない。
- **EKIを使うのは明示的な委任が必要な場合だけ**。EKIは既存Worker/Lease/Admission/Recovery Permit/物理資源予算のOwner。TAI SkillはWorker順位や金銭の中央台帳を実装しない。予測残余・回復用の確保・実予約・使用済み予算を分け、同Attempt Body再送と別Attempt業務再実行を混同しない。
- 必要な期限・品質・費用が確認できない場合はその不足と実際に成立した限定成果を報告し、read-only調査や独立した文書作業は継続できる範囲で進める。Skillを多く呼んだことや最安モデルの採用を成功条件にしない。

出典／反例：[SK-03 §8](../../../../docs/yi-constellation/harness-interoperability-and-handoff-pilot-2026-11-03.md)、[TAI #168 CQ-04/05](https://github.com/hat47x/tai-pleroma/issues/168)、[EKI #19](https://github.com/hat47x/eki-fabric/issues/19)/[#155](https://github.com/hat47x/eki-fabric/issues/155)、[TEI #2667](https://github.com/hat47x/tei-platform/pull/2667)。本節は配布前の**試作Skill手順**であり、実Harness/Provider/Worker予算最適化・品質受理を実証したものではない。
