# I/R/P/T/C/Hの到達点（2026-11-16時点）

状態: 観測の整理。新しい受入正本は作らない。正式な受入は[横断計画§50](harness-cross-ui-session-probe-2026-11-14.md)、TEI #4515/#4583、TAI #168/#234/#271、QH §10にある。

本資料は、§10.15の5枚の検証カードが**I（依頼意図）／R（元Productの実再解決）／P（現在の開示）／T（配送）／C（実Consumer）／H（Harness）**のどこまで到達したかを、実行したreceiptに基づいて並べたものである。目的は一つである。**「カードが埋まった」を「利用者の仕事が一巡した」と読まない**ため。

## 1. 6段階の意味

| 段階 | 意味 | 何をもって「到達」とするか |
| --- | --- | --- |
| **I** | 依頼の意図と対象が固定される | 公開Task、Workspace/Root、Kind/ID、Source/Model/World版、実Binary/HEAD、Audience が記録されている |
| **R** | 元Productが対象を実再解決する | 元Productの実CLIがSubjectとSource位置・版を返す |
| **P** | 現在の開示が確認される | Recipient/Audience別の許可がProduct/Hostで判定される |
| **T** | 実際に配送される | 実Tool Call、送出byte、受信者が観測される |
| **C** | 実Consumerが受領する | 別ProcessのConsumerが実Bodyを読み、独立Expectedと比較する |
| **H** | HarnessのReplyが完全に返る | 外部HarnessのTool Reply終端・Result本文が受領される |

## 2. 5枚のカードの到達点

| カード | I | R | P | T | C | H |
| --- | --- | --- | --- | --- | --- | --- |
| QH-RESOLVE-09 | ○ | − | − | − | − | − |
| QH-A0-RUN-10 | ○ | ○ | − | − | − | − |
| QH-CLI-RANGE-11 | ○ | ○ | − | − | − | − |
| QH-REVALIDATE-12 | ○ | ○ | − | − | − | − |
| QH-FIELD-13 | ○ | − | − | − | − | − |

凡例: ○＝receiptで観測、−＝未到達（NOT RUN）。

**この表はreceiptから機械的に再生成して突き合わせている**（[点検のreceipt](../../../evaluations/records/YIC-reach-table-2026-11-17.json)）。Iはcommitとclean checkoutの記録、Rはカードごとに名指した証拠field（`inspectReturnedByteRange`／`snapshotFingerprint`／`everyListedRegressionPassed`）の値を要求する。**初回の点検でQH-FIELD-13のRが根拠なしと判明したので、この表を修正した。**

### 2.1 各カードが実際に観測したもの

| カード | receipt | 観測した範囲 |
| --- | --- | --- |
| QH-RESOLVE-09 | [YIC-qh-resolve-09](../../../evaluations/records/YIC-qh-resolve-09-2026-11-16.json) | 能力解決の「曖昧＝不在」、Supports述語の所属判定。**Subjectを解決していない**のでRには届かない |
| QH-A0-RUN-10 | [YIC-tei-product-read](../../../evaluations/records/YIC-tei-product-read-2026-11-16.json) | 8件のGo回帰がclean cloneでPASS。Subject・元byte範囲の取得を含む |
| QH-CLI-RANGE-11 | [YIC-tei-readonly-cli](../../../evaluations/records/YIC-tei-readonly-cli-2026-11-16.json) | 5つのCLIが応答。`inspect`が`offset 124, line 7, column 6`〜`129`を返す |
| QH-REVALIDATE-12 | [YIC-qh-revalidate](../../../evaluations/records/YIC-qh-revalidate-2026-11-16.json) | `trace`が`snapshotFingerprint`一致を受理し、不一致を`STALE_SNAPSHOT`で拒否 |
| QH-FIELD-13 | [YIC-qh-field-13](../../../evaluations/records/YIC-qh-field-13-2026-11-16.json) | Whole Recordが追加Fieldを残し、明示2 Field投影が落とす。**構成したRecordに対するTransformの試験であり、WorkspaceのSubjectを解決していない**のでRには届かない |

## 3. 到達していない段階と、その理由

### 3.1 P（開示）の形は作れるが、判定主体にはなっていない

5枚はいずれも**受信者を定めていない**。Product内のread-only参照であり、Audience/Recipient別の許可判定を通っていない。`inspect`自身が`local-read-is-not-disclosure-permission`を`authorityLimits`に返している。

**ただしProductには開示を選ぶ入口がある。** `knowledge-context -disclose`は、Subjectに対してSectionを選ばせ、選んだものを`disclosedSections`、残りを`omittedAvailableSections`に分けて返す（[receipt](../../../evaluations/records/YIC-tei-knowledge-disclosure-2026-11-16.json)、`a44b0ed2`）。

| 指定 | `disclosedSections` | `omittedAvailableSections` |
| --- | --- | --- |
| `definition` | `["definition"]` | `["data-design","dependencies","source"]` |
| 4つすべて | 4つすべて | なし |
| `unknown` | 拒否（`KNOWLEDGE_BUILD_FAILED`、対応Sectionを列挙） | — |

**これはPの判定ではない。** コマンド自身が次の4つの限界を返している。

- `selective-disclosure-is-not-access-control-or-redaction`
- `selective-disclosure-is-derived-not-authority`
- `omitted-knowledge-is-not-negative-evidence`
- `disclosure-fingerprint-is-cache-identity-not-semantic-proof`

つまり「**何を渡すか選べる**」ことは確かめられたが、「**この受信者に渡してよいか**」は答えていない。Pの判定主体は依然として未定である。

### 3.2 T（配送）に到達しない理由

外部Harnessへの実送信を行っていない。TAI #168のG0実OS Read-deny→G1実Egress→G2完全Tool Replyが独立P0として未了である。**Product内のCLI呼出しはプロセス境界を越えるが、組織境界を越えない。**

### 3.3 C（Consumer）に到達しない理由

元Subjectへ候補を返し、**別ProcessのConsumerが実Bodyを読む**段階がない。5枚は「読めた」ことを観測したが、「返して、読まれた」ことを観測していない。

### 3.4 H（Harness）に到達しない理由

外部HarnessのTool Replyを受領していない。TAI #168の比較適格は**0/4**のままである。

## 4. この表が示すこと

**5枚のカードが埋まったことは、一巡の完了ではない。** 到達点は最大で**R**であり、P・T・C・Hは全て未到達である。

とくに注意すべきは、次の読み替えが起きやすいことである。

| 実際に観測したこと | 読み替えてはいけないこと |
| --- | --- |
| CLIがSubjectを解決した | その人が今そのSourceを読む資格がある |
| `inspect`がbyte範囲を返した | その範囲を別Productへ開示してよい |
| Product内でToolが動いた | 外部Harnessへ配送された |
| テストがPASSした | Consumerが実Bodyを受領した |
| receiptが`PASS`である | 利用者の仕事が一巡した |

## 4.1 Pの判定主体が、製品の入口に見つからないこと

「開示を選べる」ことは§3.1で確かめた。では「この受信者に渡してよいか」を製品が答える入口はあるのか。**最も近い候補**である`internal/plugin/management`の`DocumentReadPreflight`を実行して確かめた（[receipt](../../../evaluations/records/YIC-preflight-disclosure-2026-11-17.json)、`a44b0ed2`）。

テスト**21件はすべてPASS**した。そのうえで、型自身のコメントが次を明示している。

| 宣言 | 何を否定しているか |
| --- | --- |
| `does not discover a Document` | 対象文書を特定していない |
| `read its bytes`（否定文脈） | 本文byteを読んでいない |
| `check Audience/Disclosure`（否定文脈） | **受信者別の開示を判定していない** |
| `grant publication`（否定文脈） | 公開を許可していない |

これは「未実装の機能」ではなく、**その入口が別の仕事をする道具**だという宣言である。文書の`DocumentReadPreflight`は「Plugin選択の証拠を、公開文書読取の前提へ投影する」もので、開示の可否を答えるものではない。

したがって、**Pの判定主体は、少なくともこの入口には無い。** 別の入口があるかは未確認だが、「近い道具が兼ねている」とは言えないことが、実行で確かめられた。

## 4.2 自分で拒否できる判定は存在する。ただし対象が違う

TEIの2つの入口はどちらも受信者別の開示を判定しなかった。しかし**外部の判断を待たずに自分で拒否する**判定は、別の製品にある。SUIの`resolve_access_decision`を`require_tenant_scope=True`で実行した（[receipt](../../../evaluations/records/YIC-sui-tenant-boundary-2026-11-17.json)、`sui-sensemaking` `0c2a2c548058`、linux、8件PASS）。

| 状況 | 判定 | 外部Adapterの呼出し |
| --- | --- | --- |
| Tenant不一致・scope不一致 | `allow=false`（`tenant_mismatch`） | **0回** |
| Tenant一致 | `allow=true` | 1回（PDP評価へ進む） |

**`adapter.calls == 0`が要点である。** 拒否はPDPアダプタを呼ぶ前に決まる。待って返ってきた「いいえ」ではなく、**自分で出した「いいえ」**である。

ただし判定しているのは**Tenant境界**であって、受信者・Audience別の開示許可ではない。テストのAdapterは記録用のダブルで、実組織PDPではない。

**Pの形（自分で判断して止められる）は存在する。** 問われているのは「その判断の対象が開示かどうか」であって、「そういう判断ができるかどうか」ではない。

## 4.3 受取側が自分で拒否する例は、EKIにもある

SUIのTenant境界に続き、EKIにも**受取側が自分で出す拒否**がある（[receipt](../../../evaluations/records/YIC-eki-private-input-2026-11-17.json)、`eki-fabric` `256feb8bab9c`、2件PASS）。

| 要求 | 証明の開示Profile | 判定 |
| --- | --- | --- |
| `RequirePrivateInputProof = true` | `public-io` | **拒否**（"must not be treated as zero knowledge by default"） |
| `RequirePrivateInputProof = true` | `private-input` | **受理** |

同じ要求に対して、証明のProfileだけで結果が変わる。**これは対称性の検査であり、片側だけでは「常に拒否する実装」と区別できない**ので、受理側も併せて実行している。

ただし判定しているのは**証明の開示Profile**であって、「この受信者にこの内容を渡してよいか」ではない。

## 4.4 三つの製品で見たPの形

ここまでに確認した「自分で判断して止められる」入口を並べる。

| 製品 | 入口 | 判定している対象 | 受信者別の開示か |
| --- | --- | --- | --- |
| TEI | `knowledge-context -disclose` | 開示するSectionの選択 | **違う**（選択であり許可ではない） |
| TEI | `DocumentReadPreflight` | Plugin選択の投影 | **違う**（開示を判定しないと明示） |
| SUI | `resolve_access_decision`（Tenant scope） | Tenant境界 | **違う**（Tenantの一致） |
| EKI | `Accept`（`RequirePrivateInputProof`） | 証明の開示Profile | **違う**（Profileの種別） |

**4つの入口すべてが「自分で止められる」形を持ち、4つとも対象が開示ではない。** これは「開示を判定する能力が無い」ことの証明ではない。確認した入口が4つである、という記録である。

## 5. 次の一段階

`knowledge-context -disclose`で**開示の選択と報告**は実測できた（§3.1）。

一方、`DocumentReadPreflight`は**受信者別の開示を判定しないと自分で宣言している**（§4.1）。

残るのは、**受信者・Audience別の許可判定を、どの主体が担うか**である。Productが「この受信者に渡してよいか」を答える経路はまだ見つかっていない。

ただし§4.2で見たとおり、**自分で拒否できる判定そのものはSUIに存在する**（対象はTenant境界）。したがって「開示を判定できる主体が無い」と一般化してはいけない。問いは「その判断の対象が開示か」に絞られる。ここはOwner判断を含むため、既定案を実装せず、次に確かめる対象として置く。

**「見つからない」と「無い」を混同しない。** 確認したのは2つの入口だけである。

## 5.1 Productが自分で宣言する限界を、記録から落とさない

P・T・C・Hの議論で繰り返し現れたのは、**Product自身が「これは許可ではない」と宣言している**ことだった。YICのreceiptがProduct出力を写すとき、この宣言を言い換えたり落としたりすると、「できること」と「許可されていること」の区別が記録から消える。

そこで、receiptが保持している限界文字列を機械的に数える点検を足した（[点検のreceipt](../../../evaluations/records/YIC-authority-limits-2026-11-16.json)）。現在の結果は次のとおり。

| 項目 | 値 |
| --- | --- |
| YICのreceipt | 12件 |
| 限界を保持しているreceipt | 2件 |
| 収集した異なり限界 | **17種** |
| 限界を持つはずのProduct出力で、限界を落としたreceipt | **0件** |

収集した17種のうち、P/T/C/Hの読み替えに直接効くもの:

| 限界 | 何を禁じるか |
| --- | --- |
| `local-read-is-not-disclosure-permission` | 手元で読めたことを開示許可と呼ばない |
| `selective-disclosure-is-not-access-control-or-redaction` | 開示Sectionの選択を権限制御と呼ばない |
| `selective-disclosure-is-derived-not-authority` | 開示の派生を権限と呼ばない |
| `source-location-is-not-semantic-acceptance` | 位置の取得を意味の受理と呼ばない |
| `inspection-is-a-derived-read-only-projection` | 参照を正本と呼ばない |
| `omitted-knowledge-is-not-negative-evidence` | 省略を不存在の証拠と呼ばない |

**この点検が見るのは保持だけである。** 限界をそのまま写していても、その限界が禁じる結論を出しているreceiptは通る。限界の解釈は人の判断に残る。

## 6. この記録が示さないこと

- 外部Harnessの実送受信、完全なTool Reply
- 実組織PDP、実Provider Effect、Owner意味受理
- 別OS・別Hostでの同じ到達点
- 到達点○の質（テストが測れている範囲は、それぞれのreceiptの`scope`に書いた）

## 7. 変更履歴

- 2026-11-16 初版。§10.15の5枚のreceiptを読み、I/R/P/T/C/Hの到達点を段階別に整理した。
