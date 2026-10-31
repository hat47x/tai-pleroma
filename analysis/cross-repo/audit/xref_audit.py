#!/usr/bin/env python3
"""hat47x/<repo>:<path>[@rev] 形式の他リポジトリ引用を抽出し、引用先で取得できるかを確かめる。

2026-10-09の改訂
- 走査対象は git ls-files（追跡中のファイル）だけにした。.local/ や .claude/worktrees/ のような
  git管理外の作業コピーを数えない。
- 引用先ごとに統合branchを持つ。SEIの統合の線は main ではなく develop/v0.2.0。
- 取得状況を3つに分ける: main にある / 統合branchにだけある / どこにも無い。
- 引用に @rev が付いていれば、その版に対して検査する。
"""
import collections, json, os, re, subprocess, sys

ROOT = os.environ.get("HAT47X_ROOT")
if not ROOT:
    sys.exit("HAT47X_ROOT is not set: point it at the directory that holds the repositories")
REPOS = ["tei-platform", "sei-cognition", "sui-sensemaking", "markdown-matrix-injector",
         "eki-fabric", "cultural-substrate-weaving", "vs-bear-simulator"]
INTEGRATION = {r: "origin/main" for r in REPOS}
INTEGRATION["sei-cognition"] = "origin/develop/v0.2.0"
EXTS = (".md", ".json", ".yaml", ".yml", ".go", ".py", ".txt")
PAT = re.compile(r"hat47x/(" + "|".join(map(re.escape, REPOS)) + r"):([A-Za-z0-9_./\-]+?)(?:@([0-9a-f]{7,40}))?(?=[\s`)\]、。，,;:）]|$)")

def git(repo, *a):
    return subprocess.run(["git", "-C", f"{ROOT}/{repo}", *a], capture_output=True, text=True)

def has(repo, rev, path):
    return git(repo, "cat-file", "-e", f"{rev}:{path}").returncode == 0

rows = []
for src in REPOS:
    files = git(src, "ls-files").stdout.split("\n")
    for rel in files:
        if not rel.endswith(EXTS):
            continue
        try:
            text = open(f"{ROOT}/{src}/{rel}", encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for m in PAT.finditer(text):
            dst, path, rev = m.group(1), m.group(2).rstrip(".,;:"), m.group(3)
            if dst == src:
                continue
            rows.append((src, rel, text.count("\n", 0, m.start()) + 1, dst, path, rev))

def classify(dst, path, rev):
    if rev:
        return "pinned-ok" if has(dst, rev, path) else "pinned-MISSING"
    if has(dst, "origin/main", path):
        return "on-main"
    if has(dst, INTEGRATION[dst], path):
        return "integration-only"
    return "absent"

cls = {}
for r in rows:
    key = (r[3], r[4], r[5])
    if key not in cls:
        cls[key] = classify(*key)

print("integration branches:", {k: v for k, v in INTEGRATION.items() if v != "origin/main"} or "all origin/main")
print(f"\ntracked-file citations (hat47x/<repo>:<path>): {len(rows)}   unique targets: {len(cls)}")
tot = collections.Counter(cls.values())
print("target status:", dict(tot))
pair = collections.defaultdict(collections.Counter)
for s, f, l, d, p, rev in rows:
    pair[(s, d)][cls[(d, p, rev)]] += 1
print("\nsrc -> dst : citations by status")
for (s, d), c in sorted(pair.items(), key=lambda kv: -sum(kv[1].values())):
    print(f"  {s:27s} -> {d:27s}: {dict(c)}")
bad = [(k, v) for k, v in cls.items() if v in ("absent", "pinned-MISSING")]
print(f"\n=== not retrievable anywhere checked ({len(bad)}) ===")
for (dst, path, rev), st in bad:
    print(f"- [{st}] {dst}:{path}" + (f"@{rev}" if rev else ""))
    for s, f, l, d, p, r in rows:
        if (d, p, r) == (dst, path, rev):
            print(f"    cited by {s}/{f}:{l}")
only = [(k, v) for k, v in cls.items() if v == "integration-only"]
print(f"\n=== only on the integration branch, not on main ({len(only)}) ===")
for (dst, path, rev), st in only:
    print(f"- {dst}:{path}")
json.dump({"rows": rows, "status": [[*k, v] for k, v in cls.items()]},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "xref_audit.result.json"), "w"), ensure_ascii=False)
