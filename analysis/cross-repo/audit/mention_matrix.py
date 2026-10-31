import os, re
import os as _os
ROOT=_os.environ.get("HAT47X_ROOT","/mnt/d/GIT/hat47x")
R=["tei-platform","sei-cognition","sui-sensemaking","markdown-matrix-injector","eki-fabric","cultural-substrate-weaving","vs-bear-simulator"]
# product-name patterns (word-ish boundaries); long slug forms included
P={
 "tei-platform":r"(?<![A-Za-z])TEI(?![A-Za-z])|tei-platform|鼎",
 "sei-cognition":r"(?<![A-Za-z])SEI(?![A-Za-z])|sei-cognition",
 "sui-sensemaking":r"(?<![A-Za-z])SUI(?![A-Za-z])|sui-sensemaking",
 "markdown-matrix-injector":r"(?<![A-Za-z])MMI(?![A-Za-z])|markdown-matrix-injector",
 "eki-fabric":r"(?<![A-Za-z])EKI(?![A-Za-z])|eki-fabric|EKI Fabric",
 "cultural-substrate-weaving":r"(?<![A-Za-z])CSW(?![A-Za-z])|cultural-substrate-weaving",
 "vs-bear-simulator":r"vs-bear-simulator|vs-bear",
}
P={k:re.compile(v) for k,v in P.items()}
SKIP={".git","node_modules","dist","outputs",".venv","__pycache__",".claude","worktrees","research-archive"}
tot={}
for s in R:
    cnt={d:0 for d in R}; n=0
    for dp,dn,fn in os.walk(f"{ROOT}/{s}"):
        dn[:]=[d for d in dn if d not in SKIP]
        for f in fn:
            if not f.endswith(".md") or f=="CHANGELOG.md": continue
            n+=1
            t=open(os.path.join(dp,f),encoding="utf-8",errors="ignore").read()
            for d in R:
                if d!=s and P[d].search(t): cnt[d]+=1
    tot[s]=(n,cnt)
short={r:r[:4] for r in R}
print("md files that mention the column product (excl. CHANGELOG, worktrees)")
print(f"{'':28s}{'#md':>5s} "+" ".join(f"{short[d]:>5s}" for d in R))
for s in R:
    n,c=tot[s]
    print(f"{s:28s}{n:5d} "+" ".join(f"{('-' if d==s else c[d]):>5}" for d in R))
print("\nasymmetric pairs (A mentions B in >=3 files, B never mentions A):")
for a in R:
    for b in R:
        if a!=b and tot[a][1][b]>=3 and tot[b][1][a]==0:
            print(f"  {a} -> {b}: {tot[a][1][b]} files ; reverse: 0")
