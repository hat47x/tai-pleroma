#!/usr/bin/env node
"use strict";
/* Static integrity check for the TAI example Skill; NOT a Harness/Loader test. */
const fs = require("node:fs"), os = require("node:os"), path = require("node:path"), assert = require("node:assert/strict");
const SKILL = "examples/skills/yi-tai-activity/SKILL.md";
const REFS = [
  "examples/skills/yi-tai-activity/references/product-entrypoints.md",
  "examples/skills/yi-tai-activity/references/source-disclosure-evidence.md",
  "examples/skills/yi-tai-activity/references/requalification-deadline-recovery.md",
];
function inside(root, dest) {
  const rel = path.relative(root, dest);
  return rel === "" || (rel !== ".." && !rel.startsWith(".." + path.sep) && !path.isAbsolute(rel));
}
function bad(code, label) {
  const e = new Error(code + ": " + label); e.code = code; throw e;
}
function check(root) {
  const repo = path.resolve(root), canonical = fs.realpathSync(repo);
  const rels = [SKILL, ...REFS];
  for (const rel of rels) {
    const file = path.resolve(repo, rel);
    if (!inside(repo, file)) bad("PATH_ESCAPE", rel);
    if (!fs.existsSync(file) || !fs.statSync(file).isFile()) bad("MISSING_FILE", rel);
    if (!inside(canonical, fs.realpathSync(file))) bad("SYMLINK_ESCAPE", rel);
  }
  const docs = rels.map(rel => ({rel, text: fs.readFileSync(path.join(repo, rel), "utf8")}));
  const rootText = docs[0].text;
  const fm = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/.exec(rootText);
  if (!fm) bad("MISSING_FRONTMATTER", SKILL);
  const names = [...fm[1].matchAll(/^name:\s*(\S+)\s*$/gm)].map(x => x[1]);
  if (names.length !== 1 || names[0] !== "yi-tai-activity") bad("WRONG_NAME", SKILL);
  if (!/^description:\s*(?:>-?|.+)$/m.test(fm[1])) bad("MISSING_DESCRIPTION", SKILL);
  const rootRefs = new Set();
  let localLinks = 0;
  for (const {rel, text} of docs) {
    // This scanner handles the simple local Markdown links used by this package;
    // it is not a complete Markdown parser or an authorization validator.
    for (const x of text.matchAll(/\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g)) {
      const raw = x[1];
      if (/^(?:https?:|mailto:|#)/i.test(raw)) continue;
      const stripped = raw.split("#", 1)[0].split("?", 1)[0];
      if (!stripped) continue;
      let decoded;
      try { decoded = decodeURIComponent(stripped); }
      catch { bad("BAD_URL_ENCODING", rel + ": " + raw); }
      const file = path.resolve(repo, path.dirname(rel), decoded);
      if (!inside(repo, file)) bad("PATH_ESCAPE", rel + ": " + raw);
      if (!fs.existsSync(file) || !fs.statSync(file).isFile()) bad("BROKEN_LINK", rel + ": " + raw);
      if (!inside(canonical, fs.realpathSync(file))) bad("SYMLINK_ESCAPE", rel + ": " + raw);
      if (rel === SKILL) rootRefs.add(path.relative(repo, file).split(path.sep).join("/"));
      localLinks++;
    }
  }
  for (const ref of REFS) if (!rootRefs.has(ref)) bad("UNLINKED_REFERENCE", ref);
  return {
    kind: "static-package-integrity", result: "PASS",
    rootChars: rootText.length,
    referenceFiles: REFS.length, referenceChars: docs.slice(1).reduce((n,d) => n+d.text.length, 0),
    localLinks, noClaims: ["actual Harness load", "agent consumed reference", "meaning/correctness", "token saving", "OS/Host grants", "real egress"]
  };
}
function selfTest() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tai-pkg-"));
  const put = (rel, body) => {
    const dest = path.join(dir, rel); fs.mkdirSync(path.dirname(dest), {recursive:true});
    fs.writeFileSync(dest, body);
  };
  const base = "---\nname: yi-tai-activity\ndescription: >-\n  A test\n---\n";
  const links = REFS.map(ref => "[detail](" + path.relative(path.dirname(SKILL), ref) + ")").join("\n");
  let passed = 0;
  try {
    put(SKILL, base + links);
    REFS.forEach(ref => put(ref, "[doc](../../../../docs/demo.md)\n"));
    put("docs/demo.md", "# Test\n");
    assert.equal(check(dir).referenceFiles, 3); passed++;
    function expect(change, code) {
      const old = fs.readFileSync(path.join(dir, SKILL), "utf8");
      const first = fs.readFileSync(path.join(dir, REFS[0]), "utf8");
      try { change(); assert.throws(() => check(dir), e => e.code === code); passed++; }
      finally { put(SKILL, old); put(REFS[0], first); }
    }
    expect(() => put(SKILL, "invalid\n" + links), "MISSING_FRONTMATTER");
    expect(() => put(SKILL, base.replace("yi-tai-activity", "wrong-skill") + links), "WRONG_NAME");
    expect(() => put(SKILL, base + links.replace(/\[detail\]\([^)]*\)/,"[offsite](https://example.org)")), "UNLINKED_REFERENCE");
    expect(() => put(SKILL, base + links + "\n[broken](missing.md)"), "BROKEN_LINK");
    expect(() => put(SKILL, base + links + "\n[escape](../../../../../etc/passwd)"), "PATH_ESCAPE");
    expect(() => put(REFS[0], "[broken](missing.md)"), "BROKEN_LINK");
    expect(() => put(SKILL, base + links + "\n[bad](%ZZ)"), "BAD_URL_ENCODING");
  } finally {fs.rmSync(dir,{recursive:true,force:true});}
  return {kind:"synthetic-self-test",result:"PASS",assertions:passed,noClaims:["actual Product/Harness E2E"]};
}
if(require.main===module) {
  try {
    if(process.argv[2]==="--check") console.log(JSON.stringify(check(path.resolve(__dirname,"../..")),null,2));
    else if(process.argv[2]==="--self-test") console.log(JSON.stringify(selfTest(),null,2));
    else {console.error("Usage: --check | --self-test");process.exitCode=2;}
  } catch(e){console.error(e.message);process.exitCode=1;}
}
module.exports={check,selfTest};
