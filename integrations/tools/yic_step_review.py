"""Ask Step 3.7 (architect role) whether the YI work has an honest stopping point.

The last twenty rounds added checks, aggregates and indices. None of that changes the
one fact that matters: G1 is undecided by the Owner, and P/T/C/H are unreached. This
prompts an architect-role review on whether continuing to add verification is the
right work, or whether it has become motion without progress.

The reply is recorded verbatim in the receipt; this script does not paraphrase it.
"""

import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PROMPT = """あなたは `architect` ロールです。TAI Pleroma の YIC 作業の進め方について判断してください。

## 現在地（事実）

- G1（Ownerが25件の候補を採否し、D1〜D6の6つの横断判断を決める）は**未了**。判断欄は15/15空。
- 到達点は I（意図）と R（元Product再解決）まで。**P（受信者別の開示）・T（配送）・C（Consumer）・H（Harness Reply）は未到達。**
- Pの判定主体を3案比較し、案C（記録だけ）を既定案として資料に残した。ただし案CはPを解決しない。
- 直近20ラウンドは、点検・集約・索引の整備に使った。具体的には、リンク着地、節番号、位置づけ行、デッキ枚数、ゲート文書の件数一致、G1パケットの判断可能性、未実施項目の後続証拠、Product宣言の限界保持、SKIPの可視性、receipt再現性、ツール配線など。

## 問い

1. **このまま点検を増やすのは前進か、それとも「動いているが進んでいない」状態か。** 判断と根拠を示してください。
2. もし後者なら、**次に取り切るべき最小の一歩**は何か。G1の判断を待たずに進められる作業の中で、意味のあるものを一つ挙げてください。
3. 逆に前者なら、**まだ点検されていない重要領域**を一つ挙げ、なぜそれが重要かを述べてください。

## 制約

- ファイルを変更しないでください。判断だけを返してください。
- G1の判断をTAIが代行することは禁じます（Ownerの領域）。
- 新しい中央サービス・正本を作る提案はしないでください。
- 日本語で書いてください。

## 出力形式

```markdown
## 結論
（前進か、停滞か。1〜2文）

## 根拠
- ...

## 次の最小の一歩
（具体的に一つ。実行可能な形で）

## それが意味を持つ理由
- ...

## 判断を保留する点
- ...
```
"""

RECEIPT = "evaluations/records/YIC-step-review-2026-11-18.json"


def digest(path):
    import hashlib
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    args_artifact = sys.argv[1] if len(sys.argv) > 1 else "evaluations/artifacts/scn-003-document.json"
    out = sys.argv[2] if len(sys.argv) > 2 else RECEIPT

    root = Path(__file__).resolve().parents[2]
    env_file = Path(os.environ.get("TEMP", "/tmp")) / "step-env.ps1"
    if not env_file.exists():
        print("step env file missing", file=sys.stderr)
        return 1

    # Source the env file inside a PowerShell invocation so the key never appears here.
    # Write the prompt to a file: passing a long multi-line string through -Command
    # invites quoting damage, and a truncated prompt would make the reply meaningless.
    prompt_file = Path(os.environ.get("TEMP", "/tmp")) / "yic-step-prompt.md"
    prompt_file.write_text(PROMPT, encoding="utf-8")

    shells = ["pwsh", "powershell"]
    script = (
        f". \"{env_file}\"; "
        '$env:PATH = "C:\\Users\\yhata\\.stepcode\\bin;C:\\Users\\yhata\\.stepcode\\agent\\bin;$env:PATH"; '
        f"step -p (Get-Content -Raw -Encoding UTF8 \"{prompt_file}\") "
        "--model step-3.7-flash --no-tools"
    )
    completed = None
    for shell in shells:
        try:
            completed = subprocess.run(
                [shell, "-NoProfile", "-Command", script],
                cwd=root, capture_output=True, text=True,
                encoding="utf-8", errors="replace", env={**os.environ}, timeout=1800,
            )
            break
        except FileNotFoundError:
            continue
    if completed is None:
        print("no PowerShell available", file=sys.stderr)
        return 1
    def usable(text):
        """A review must be prose, not a tool-call preamble."""
        if len(text) < 400:
            return False
        if "<tool_call>" in text or "<function=" in text:
            return False
        return "##" in text

    reply = (completed.stdout or "").strip()
    attempts = [{"chars": len(reply), "usable": usable(reply)}]
    if not usable(reply):
        # Retry once with the prohibition stated in the prompt itself.
        retry_prompt = prompt_file
        retry_prompt.write_text(
            PROMPT + "\n\n**重要**: ツールを呼び出さないでください。"
            "`<tool_call>`を出力しないでください。見出し付きの文章だけを返してください。\n",
            encoding="utf-8",
        )
        retry = subprocess.run(
            [shell, "-NoProfile", "-Command", script.replace(
                f'Get-Content -Raw -Encoding UTF8 \\"{prompt_file}\\"',
                f'Get-Content -Raw -Encoding UTF8 \\"{retry_prompt}\\"')],
            cwd=root, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env={**os.environ}, timeout=1800,
        )
        reply = (retry.stdout or "").strip()
        attempts.append({"chars": len(reply), "usable": usable(reply)})

    if not usable(reply):
        print(f"unusable reply after {len(attempts)} attempts: {attempts}", file=sys.stderr)

    receipt = {
        "schema": "tai.reference.yic-step-review/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the official Step Code CLI, model step-3.7-flash, no tools",
        "command": "python integrations/tools/yic_step_review.py evaluations/artifacts/scn-003-document.json " + RECEIPT,
        "result": "PASS" if usable(reply) else "FAIL",
        "artifact": {"path": args_artifact, "digest": digest(root / args_artifact)},
        "observed": {
            "model": "step-3.7-flash",
            "roleRequested": "architect",
            "tools": "none",
            "exit": completed.returncode,
            "replyChars": len(reply),
            "reply": reply,
            "replyReceived": bool(reply),
            "replyIsUsable": usable(reply),
            "attempts": attempts,
            "finding": (
                "Step 3.7のarchitectロールに、点検の追加が前進か停滞かを判断させた。"
                "返答はそのまま`reply`に保存し、要約・改変しない。"
                "`result`は返答を得られたかどうかを示す。"
                "**返答の内容が正しいかは判定しない**：これは意見の記録であり、検査ではない。"
            ),
        },
        "scope": (
            "Records one review reply from the Step Code CLI (step-3.7-flash, architect role, no "
            "tools) on whether adding more verification is progress. The reply is an opinion, not a "
            "finding: it was not executed, it decides nothing about G1, and its suggestions are not "
            "adopted by this receipt."
        ),
    }
    (root / out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"chars": len(reply), "exit": completed.returncode}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
