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
| QH-FIELD-13 | ○ | ○ | − | − | − | − |

凡例: ○＝receiptで観測、−＝未到達（NOT RUN）。

### 2.1 各カードが実際に観測したもの

| カード | receipt | 観測した範囲 |
| --- | --- | --- |
| QH-RESOLVE-09 | [YIC-qh-resolve-09](../../../evaluations/records/YIC-qh-resolve-09-2026-11-16.json) | 能力解決の「曖昧＝不在」、Supports述語の所属判定。**Subjectを解決していない**のでRには届かない |
| QH-A0-RUN-10 | [YIC-tei-product-read](../../../evaluations/records/YIC-tei-product-read-2026-11-16.json) | 8件のGo回帰がclean cloneでPASS。Subject・元byte範囲の取得を含む |
| QH-CLI-RANGE-11 | [YIC-tei-readonly-cli](../../../evaluations/records/YIC-tei-readonly-cli-2026-11-16.json) | 5つのCLIが応答。`inspect`が`offset 124, line 7, column 6`〜`129`を返す |
| QH-REVALIDATE-12 | [YIC-qh-revalidate](../../../evaluations/records/YIC-qh-revalidate-2026-11-16.json) | `trace`が`snapshotFingerprint`一致を受理し、不一致を`STALE_SNAPSHOT`で拒否 |
| QH-FIELD-13 | [YIC-qh-field-13](../../../evaluations/records/YIC-qh-field-13-2026-11-16.json) | Whole Recordが追加Fieldを残し、明示2 Field投影が落とす |

## 3. 到達していない段階と、その理由

### 3.1 P（開示）に到達しない理由

5枚はいずれも**受信者を定めていない**。Product内のread-only参照であり、Audience/Recipient別の許可判定を通っていない。`inspect`自身が`local-read-is-not-disclosure-permission`を`authorityLimits`に返している。

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

## 5. 次の一段階

到達点を上げるには、**P の判定主体を決める**必要がある。5枚はいずれも受信者を持たないため、Pを作れない。最初の一歩は、TEI側で「このSubjectを、このAudienceへ、今開示してよいか」をProductが答える経路を実測することである。これは既存の`disclose`系コマンドの範囲に関わる。

## 6. この記録が示さないこと

- 外部Harnessの実送受信、完全なTool Reply
- 実組織PDP、実Provider Effect、Owner意味受理
- 別OS・別Hostでの同じ到達点
- 到達点○の質（テストが測れている範囲は、それぞれのreceiptの`scope`に書いた）

## 7. 変更履歴

- 2026-11-16 初版。§10.15の5枚のreceiptを読み、I/R/P/T/C/Hの到達点を段階別に整理した。
