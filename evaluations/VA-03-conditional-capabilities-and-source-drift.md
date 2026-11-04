# VA-03：用途条件付き能力とSource状態ドリフトの横断判定票

- **状態**：2026-11-04、既存Product Value／要求／IssueとVA-00の整合性監査に基づくSource-static判断。実実行・独立Oracle評価・実異モデル比較・Owner要件採用は **NOT RUN**。
- **起点**：[横断 #422](https://github.com/hat47x/tai-pleroma/issues/422)／[VA-01](VA-01-product-value-necessity.md)／[VA-02](VA-02-cross-product-first-run-protocol.md)。
- **既存監査を再利用**：[TAI #424](https://github.com/hat47x/tai-pleroma/issues/424)（9 Lane、S1〜S5とS6のF2整理）、[TAI #425](https://github.com/hat47x/tai-pleroma/issues/425)（TAIのSource状態相違）。このファイルは第二のIssue/ADR台帳ではない。
- **Source境界**：以下のIssue状態は2026-11-04時点の個別照合であり、全Productを一つのcommitで固定したことを意味しない。実試験の前に各Laneで現行full SHAと必要なSource closureを固定する。

## 1. 「複雑さが必要」の条件を先に定義する

最小の導入構成は、**必要な価値が成立していること**と、**用途条件が要求する不変条件を満たすこと**の両方で判定する。

一つの評価結果で次を相殺しない：
- **価値**：利用者が目的を達成できたか、期待以上の情報/選択/再開を得たか。
- **保証**：意味・権限・Source・機密・結果受領・締切・回復を満たしたか。
- **負担**：起動/読込/構成/移送、CLI/GUIの入力数、レイテンシ（中央値とtailを分ける）、CPU/GPU/メモリ、課金、レビュー・導入/更新・復旧の費用。
- **適用範囲**：誰のどのUser Job、どのHost/Trust/データ特性/期限に対する結果か。

**判断の分岐**：
1. 既存Harness・CLI・通常ファイル・既存Hostで安全に達成できるなら、それをB0として残す。
2. B0で不足するProduct固有の価値をB1で加える。ただし依存先の単独機能をB1の開始条件にはしない。
3. B2高度化は、B1が満たせない明示的な条件（遅延予算、異Trust、複数Target、組織全件性、大規模同時利用等）があるときだけ要求候補とする。
4. 現在の実行環境で条件を満たせなければ`unsupported / unknown / denied`を保持する。「複雑すぎるから安全性を削る」のも「安全そうだから全環境へ一律搭載する」のも避ける。

## 2. EKIは「長時間バッチだけ」ではない：4つの外面と通信方式を分ける

[EKI Product Value](https://github.com/hat47x/eki-fabric/blob/main/product/value.md)は、**委任の核**をもつ4つの外面（広域資源最適化・AI推論/ツール実行の統治・隔離実行・軽量常駐認知）を明記する。従って「低レイテンシ通信やマルチモーダル応答はEKIに過剰」と一律に分類してはならない。一方、最初の2 WorkerバッチE2Eへ全データ様式の高速プロトコルを必須化するのも誤り。

**最小不変条件**：有効期間付きの委任/Capability、TaskとAttemptの同一性、Worker側のLocal Governorと停止、実データの開示範囲、結果の検証・受領を、使用する通信様式に関係なく保つ。Streamの途中の到着と最終AcceptedResultは別Claim。常駐認知は「存在は継続しても権限は有限」である。

| Workload / User Job | 最初の実験経路（必須採用ではない） | 高度化を要求できる条件 | 負例・保存する保証 |
| --- | --- | --- | --- |
| 有限Job、非同期バッチ | 現行Task Submit/Status、Artifact Body、ResultClaim/AcceptedResult | 大量データ/帯域や分散回復に明確な価値がある | Control-planeに大きなMedia Bodyを流す／ACKだけで実Resultとする |
| 軽量認知・低遅延イベント | 既存Control/実行委任を保ち、**データ通知のtransportを別経路候補として比較**。最初は1 Producer-Consumer・合成Eventで測る | 応答期限・jitter・ordering・backpressure・切断後の再開条件が具体的に必要 | 単発同期呼出しの待ちが予算超過／全イベントを再送してdeadlineを失う／権限が失効しても配信継続 |
| マルチモーダル出力 | Media/Payloadは既存の外部Service/ProviderとData Planeで扱い、EKIは必要な委任と結果参照をつなぐ | 音声・画像・時系列・映像等の分割配信と同期が実User Jobで必要 | Mediaの転送開始≠完整な受信・同期・業務上の承認。秘密の未許可送出を防ぐ |
| 常駐型プロセス | 現行の期限・Budget・Local Governorを用い、期限更新/停止を合成試験 | 長寿命セッション、故障時再接続、再資格化が実測で必要 | 常駐の継続を無期限Grantへ昇格／リソース提供者が停止不能 |

**通信採用の問い**：対象データの様式、更新頻度、end-to-endの許容遅延（測定点）、最大遅延とjitter、loss/ordering/再送、backpressure、認証/開示、OS/ネットワーク制約、接続・維持費を先に固定。HTTPS/JSON、Connect/Protobufなど既存Baselineの適用範囲から始め、必要なData Planeやstream transportの候補だけを隔離して比較する。未採用のプロトコルをCoreの既定ABIにしない。EKIの既存 [RQ-008](https://github.com/hat47x/eki-fabric/blob/main/requirements/PRODUCT_REQUIREMENTS.md)、[MVP計画](https://github.com/hat47x/eki-fabric/blob/main/architecture/MVP_IMPLEMENTATION_PLAN.md)と整合させる。

**初期Expected案**：高速経路あり／なしの同一合成Event列で、(A)期限内Delivered+Authorized、(B)期限超過だが届いた、(C)権限失効/Local Governor拒否、(D)受信側が途中離脱、(E)Media完了通知のみで実Byte欠落、を別結果にする。中央値が速くても(B)〜(E)をPASSにしない。全て**NOT RUN**。

## 3. 既存の実装の到達点が変わったら、削減議論も更新する

| Sourceから確認した状態 | 以前の説明を修正する点 | Value監査に必要な結論 |
| --- | --- | --- |
| [TEI #1180](https://github.com/hat47x/tei-platform/issues/1180)：現mainに保存6-Step Scenarioと`scenario verify/generate/run/check`の限定入口がある（[VA-02 §6](VA-02-cross-product-first-run-protocol.md)のBlob証拠） | 「永続Scenario/CLIは全て未実装」は誤り。ただし一般Command/Web E2Eは未実証 | 既存入口を使い、AIのCase候補、独立Expected、Target固有観測を補う。新Scenario SSOTを作らない |
| [EKI #381](https://github.com/hat47x/eki-fabric/issues/381)はClosed（2026-11-03）、[EKI #58](https://github.com/hat47x/eki-fabric/issues/58)はOpen | 「active→verifying未配線」を現在未解決の一律前提にしない | 実Attempt/Result/期限回復のE2E確認とIssue状態を別に判定 |
| [TAI #169](https://github.com/hat47x/tai-pleroma/pull/169)は2026-11-02にClosed（mergedは[監査 #425](https://github.com/hat47x/tai-pleroma/issues/425)で別確認） | `docs/roadmap.md`の「Draft #169はmainに大幅後行中」は現在の状態と矛盾 | Draft/mergeは実行結果・Owner価値受理ではないが、最新版への導線と残課題を併記 |
| [TEI #2488](https://github.com/hat47x/tei-platform/issues/2488)はClosed、[TEI #2489](https://github.com/hat47x/tei-platform/pull/2489)もClosed／[TAI #425](https://github.com/hat47x/tai-pleroma/issues/425)でmerged確認 | 文書の「既存未解決課題」という記述が現Issue状態と合わない | record/string投影の個別spike実証と、製品の全Generatorで使える保証を分ける |

[TAI #424](https://github.com/hat47x/tai-pleroma/issues/424)のS1〜S5完了報告は**9 LaneのSource-static整合性監査**であり、VA-X/VA-Eによる実価値の比較や独立した別モデルの検証ではない。同Issueが報告するF2判断事項は**Owner判断待ち**として扱い、Issue件数・PR mergeやDocリンク一致を製品成功の代用にしない。検証は同じモデルの別Contextと明記されており、異モデルの一致とは呼ばない。

## 4. レビュー作業自体を重くしすぎないための実務ルール

- 既存[TAI #424](https://github.com/hat47x/tai-pleroma/issues/424)が全repoの文書整合性を所有。VA-03は**価値／保証／費用／適用条件の比較だけ**を追加し、リンク点検・F1/F2記録の第二台帳を持たない。
- Issue/PRの状態が変わればSource-static引用を更新し、実意味/実効果の再受理はOwnerと独立Evidenceに委ねる。変更のない原典・Artifactを無条件に全面検証する義務にしない。
- 同じSource、同じ資料、同じProviderから複数モデルへ要約を送って合意しても、外部実証や独立Oracleにはならない。VA-Xは代替/反例、VA-EはSource/実測を独立に点検し、異論は残す。
- 作業者が属するTrust Domainの外へ、非公開Raw・秘密の存在/件数・内部Expectedを出さない。限定Projectionでも真偽/件数は開示の対象。
- **停止線**：新しい横断Quality DB、万能Transport/Session Engine、Product共通Agent Scheduler、全製品一括常駐、全部署共通の状態表をこのレビューのために実装しない。

## 5. 次の実証候補（Value判定のための比較であり新しいProduct Gateではない）

- **VA-F1（EKI）**：有限Job vs 低遅延イベント vs 常駐処理。委任資格は共通に保持し、Data Planeを用途別に比較。期限、p95/p99、jitter、CPU/帯域、損失、切断復旧、Human-first停止を別指標で測定する。実Productや実ネットワークでの測定はNOT RUN。
- **VA-F2（TEI）**：既存6-Step Scenarioに独立期待結果とAI生成の負例を加え、`verify/generate/run/check`の限界を確認。実Target/Web E2Eは別扱い。既存TEI Owner [#1180](https://github.com/hat47x/tei-platform/issues/1180)へ作業を返す。
- **VA-F3（TAI/SHO/SEI/SUI）**：TAIなしの各単独製品作業と、必要なSkillだけ読んだ構成を比較。SHO L0、SEI Resume、SUI異論・保留の保持が機能数と関係なく成立するか測る。
- **VA-F4（監査の負担）**：VA-00からOwnerが本当に判断すべきF2だけを抽出。F1を再発見するAgent工数を減らし、異モデル反証は「最も重い価値判断」に優先投入する。

**採否未決**：何をEKI低遅延Profileとして受け入れるか、具体的なTransport/Codec、SLA/SLO、独立Expected、F2の正式判断順序。Data Planeの高速化は必要性を確認するまでProduction Contractへ昇格しない。
