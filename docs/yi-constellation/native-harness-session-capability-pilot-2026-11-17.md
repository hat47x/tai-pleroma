# YIC 外部HarnessのNative Session機能を検証する最小実行票

> **2026-11-17 / Proposed / Docs-only / 実Harness試行 NOT RUN。** [横断計画](harness-cross-ui-session-probe-2026-11-14.md)のM0〜M4を、Harness固有の実APIに当てはめて確かめる後続実行票。新Agent Loop、共通Session DB、中央Lock、共通Transcript ABI、第二Expected/Authority、共通Hostは設けない。最初の[TEI実行票](tei-selection-harness-first-vertical-slice-2026-11-15.md)と[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の固定比較条件を変更しない。

## 先に決めること：仕事の引継ぎと会話の再接続は違う

YICが提供したいのは、利用者がTEI Studioなどで固定した対象について、別の画面やAIでも適切に仕事を続けられることである。そのために**既存Harnessが本来持つ操作だけ**を利用し、できない機能をUIができるかのように見せない。

- **Activity継続（TAI #271）**：目的、元対象への参照、保留、許可済み根拠、次の作業を新しいSessionへ限定して伝える。旧TranscriptやGrantをそのまま移さない。これはNative Session再接続とは別。
- **Native Session再接続（Harness Owner）**：同じ実Session/Threadへ復帰し、許可された履歴とTurnを取り扱う。保存されたID、同じモデル名、会話の見た目だけでは成立を認めない。
- **Product Operation（TEI/EKI等）**：実行要求・権限・副作用・Receipt・独立Consumerを各製品が所有する。Sessionの中断や再開を実Effectの中断・再実行とみなさない。
- **View（各製品）**：UIのFocus、明示Pin、AI候補の表示は独立。Focus Bへ移った後にPin Aの回答が来てもBへ適用しない。

Native Sessionについての「閲覧可能」「再開可能」「別UIから操作可能」「同時に操作可能」は四つの別判定とする。どれか一つが欠けても、Product-onlyまたは新SessionへのActivity Handoffを妨げない。

## APIの相違を残したまま調べる

以下は2026-11-17時点の**公開仕様の読取**であり、利用者の環境での実実装・認可・複数UI動作は未確認である。

| 対象 | 公開仕様で見える候補 | 実験で決めること／仮定しないこと |
| --- | --- | --- |
| **Codex App Server** | Thread/Turn/Item、`thread/start`、`thread/resume`、`thread/fork`、`turn/start`、`turn/interrupt`、イベント通知 | 初期化Handshaking、一覧/履歴ページング、Provider変更時のresume拒否、完全なTool Result、別Clientの履歴閲覧資格、二Writerの制御を実測。「fork」は同一Sessionとは呼ばない |
| **Codex experimental readState** | 永続ローカルThreadの一部でRevision付きの未読位置・更新が提供される | 読了/未読のUI補助とTurn/業務Result/Receiptを区別。対象外Thread、競合、未対応版では表示を縮退。YIC独自の既読正本を作らない |
| **Claude Agent SDK** | Sessionの列挙/履歴、resume、forkの機構がある実装。SDK・API世代に差がある | V1とV2を区別し、選択したSDK実版で呼べる操作を実測。forkした履歴はProductのファイルやGrantの複製とは呼ばない |
| **Claude Managed Agents** | Cloud側のAgent/Environment/Session、イベント送受信、Session Thread | Local Agent SDKとは別の実行・認可面。Session APIがあってもLocal CLIのTranscriptを共有できるとは仮定しない |
| **DSH / OpenCode等** | 当該選択版のNative Session/Tool/Log/Share実装を調べる | 説明上のLiveShare、Session ID、別cwd、read-onlyだけで読取隔離・外部送出の適格を認定しない。機能がなければunsupportedでよい |

仕様の参照先：[Codex App Server](https://learn.chatgpt.com/docs/app-server)、[App Server実装ドキュメント](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md)、[Claude Agent SDK Session Browser](https://platform.claude.com/cookbook/claude-agent-sdk-05-building-a-session-browser)、[Claude Managed Agentsへの移行説明](https://platform.claude.com/docs/en/managed-agents/migration)。APIの語彙が似ていても、実Sessionの所有者、保存位置、実権限、請求経路は同一ではない。

## 一件だけ実験する順序（既存Ownerの受入票を再利用）

**対象**：既存の公開TEI `semantic-data:sales.order`。最初のAI依頼は「この設計要素の役割と依存を、読めたSourceの範囲に限って説明する」。実行環境、選択されたHarness/実Binary・SDK/Provider・Model/Tool Profile、Root、Principal、送信先、Source Revision、結果の不足範囲を開始前に固定する。秘密や独立Expectedは外部Harnessへ渡さない。

1. **Product基線**：AIなしの現行TEI CLIでSubjectを実読取。元Pin AとFocus Bを区別して、許可される短いProjectionを準備する。ここは既存TEI実行票のS0/H0であり、新しいParserやContext形式を作らない。
2. **Native能力の照合**：同じHarnessの選択版で、履歴一覧、既存Sessionのresume、終了イベント、別Clientからの閲覧、Turn操作、forkを**各別**にprobeする。公開仕様で存在しても当該環境に無ければunsupported。未試験はunknown。
3. **まず一つの操作元**：適格なHostで、Pin Aを固定したUI/CLIからread-only依頼を一回送る。実Tool Request/ReplyとResult終端を確認し、AI回答は元Pin Aへの候補に限定する。二番目のUIは原則閲覧だけにし、多Writerを暗黙に許可しない。
4. **別UIと縮退**：同じNative Sessionの閲覧/再開が実証できた場合のみM2を試す。できなければ許可された参照・不明事項だけで新Sessionを起こすM1へ縮退し、Native Session共有成功とは記録しない。
5. **後続判断**：単一WriterのTurn操作がHost/Nativeで実保証される場合だけM3を試す。実Product変更M4は既存TEIの現在Grant、明示Acceptance、Operation/Receipt/独立Readへ別途渡す。初回はread-onlyのまま終了する。

**P0を増やさない**：この実験は[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168)の実OS G0 Read-deny→G1 Egress→G2完全Reply→新規H2/H3四Slot（直近の比較適格0/4）より後。TEI [#4583](https://github.com/hat47x/tei-platform/issues/4583)のWindows Stage1→Stage2セルフビルドは独立P0。両方をこのTicketの前段Taskと束ねて一つのPASSにしない。

## Native API差を見落とさない反例

以下は既存[TAI #234](https://github.com/hat47x/tai-pleroma/issues/234) HC、[#271](https://github.com/hat47x/tai-pleroma/issues/271) Activity、[#232](https://github.com/hat47x/tai-pleroma/issues/232) Disclosure、[QH §10](cross-product-handoff-execution-tickets-2026-11-11.md)に割り付ける**後続検証案**であり、独立Expectedの第二正本ではない。

| ケース | 観測する異常 | 期待する限定動作 |
| --- | --- | --- |
| NS-01 | 保存Session IDはあるが履歴の一部が欠落、ページ継続未取得 | 「完全な履歴」「完全なTool Reply」と表示しない。必要範囲を再読取できなければunknown |
| NS-02 | 別UIのPrincipal/Audienceが狭い。旧Sessionに過去Rawが含まれる | 別UIからのattachを拒否し、開示可能なActivity Handoffだけを候補にする |
| NS-03 | Native resumeがProvider/Profile/CWD不一致で拒否 | 無断でProviderを変更・新API課金せず、拒否理由と新Sessionへの限定再開を区別 |
| NS-04 | 二つのUIがほぼ同時に同じSessionへTurnを送る | Nativeの実保証が無ければ一つの操作元だけ許可。他方は閲覧/別Sessionに縮退。UI-local mutexを実分散排他と呼ばない |
| NS-05 | `turn/interrupt`またはCancelは受理されたがProduct Effect/Tool Bodyは不明 | Session停止・Tool停止・Provider Receipt・独立Consumerを別照会し、Effectを自動再試行しない |
| NS-06 | fork後の会話に以前のWorkspace/承認/Skillが見える | 新Session/新環境として現時点のSource、Disclosure、Grant、Tool実ロードを再検証。履歴継承を権限継承にしない |
| NS-07 | 新しいAI結果の到着前にFocus Bへ移動し、Pin AのSource/Grantが変更 | Bへ自動反映しない。Aの旧回答を候補として保持し、AのSourceと現在資格を再確認 |
| NS-08 | Quota不足/Tool非対応/イベント切断でNative操作が途中終了 | Product-onlyを維持。未完了/不明を保持し、承認のない課金先変更・Tool代替・秘密再送をしない |

**最小の記録列**：試験ID、固定Task/Source・HEAD、Harness実Binary/SDK/Model/Provider/Profile、Host/OS/Principal/Recipient、実行したNative OperationとRequest/Response（公開可能な範囲のみ）、History/Tool Replyの完全性、Product Pin・再Read、Current Grant、Observed/unknown/unsupported/NOT RUN、独立Expectedの参照、Consumer Result。記録の保管と開示は既存TAI/各Productの受入Ownerに従い、中央Session Storeを増やさない。

## 合格条件と次の判断

- **M1（限定Activity Handoff）**：旧Sessionなしでも、許可済みの目的/元Subject/未決を新Sessionの受信者が実読取でき、元Productの現在Scopeへ再解決できた範囲だけ合格。
- **M2（Native Live view）**：同一実Sessionに別UIからアクセスし、履歴/イベントの受信と可視範囲を実観測できた場合のみ合格。M1成功を代用しない。
- **M3（Native control）**：同時Turnの実制御、操作の帰属、Cancel/Replyの完全性まで確認した場合のみ合格。現状は未受入。
- **内製Agent Loop（B4）の判断**：二つ以上の代表Harnessで同じ適格なJobを試し、Adapter/既存Hostで解消できないAgent Loop固有の欠落と便益・費用が観測され、Ownerが採用した場合にだけ再提案。Native API差があるだけではB4の理由にならない。

**現状**：公開仕様と既存TAI/TEI受入票の照合に基づくDocs-onlyの実験計画。NS-01〜08、同一Sessionの二UI閲覧/同時操作、実二Harness比較、外部開示、Host権限、独立Consumer、Owner正式受理はいずれもNOT RUN。製品単独利用、Tool-only、現在のGo単一バイナリ＋外部Host方針を変更しない。
