// Public synthetic reference: negative dependencies, temporal ABA and scoped reuse.
// This is NOT an implementation of TEI Query/Provider, TAI qualification or Host authority.
// Usage: node evaluations/tools/check-sk-n-negative-witness.cjs
"use strict";
function assert(x, name) { if (!x) throw new Error("FAILED "+name); }
function same(a,b){return JSON.stringify(a)===JSON.stringify(b)}
function absence(w){
  if(w.matchedWitness && w.witnessScopeAndPredicateVerified && w.witnessCurrent)
    return "refuted-with-witness";
  if(w.rows===0 && w.rowsetComplete && w.predicateEvaluated &&
     w.scopeVerified && w.cohortVerified && w.readCurrent)
    return "qualified-within-scope";
  return "not-established";
}
function currentRecheck(e){
  if(e.opaqueDependencies) return "not-established";
  if(e.changed.some(x=>e.dependencies.includes(x))) return "requalify";
  return e.currentReadAndGrantVerified ? "eligible-for-claim-review" : "historical-only";
}
function unchangedSince(events,coverageComplete){
  if(!coverageComplete)return "not-established";
  return events.length===0 ? "unchanged" : "changed";
}
function query(items,filterBeforeLimit){
  const sorted=items.slice().sort((a,b)=>a.id.localeCompare(b.id));
  if(filterBeforeLimit)return sorted.filter(x=>x.active).slice(0,1).map(x=>x.id);
  return sorted.slice(0,1).filter(x=>x.active).map(x=>x.id);
}
function adopt(window,response){
  return window.id===response.window && window.selection===response.selection &&
    window.epoch===response.epoch && window.source===response.source;
}
function pinValid(root,pins,installed){
  const visiting=new Set();
  function check(name){
    if(visiting.has(name))return false;
    const expected=pins[name],actual=installed[name];
    if(!expected||!actual||expected.version!==actual.version ||
      expected.contract!==actual.contract || expected.implementation!==actual.implementation)
      return false;
    visiting.add(name);
    const valid=(actual.eagerDependencies||[]).every(check);
    visiting.delete(name);return valid;
  }
  return check(root);
}
function runSelfcheck(){
 const out=[];
 function test(id,rule){assert(rule(),id);out.push(id)}
 const base={rows:0,matchedWitness:false,witnessScopeAndPredicateVerified:false,
   witnessCurrent:false,rowsetComplete:true,predicateEvaluated:true,
   scopeVerified:true,cohortVerified:true,readCurrent:true};
 test("NX-01-complete-zero",()=>absence(base)==="qualified-within-scope");
 test("NX-02-partial-zero",()=>absence({...base,rowsetComplete:false})==="not-established");
 test("NX-03-partial-positive",()=>absence({...base,rowsetComplete:false,matchedWitness:true,
   witnessScopeAndPredicateVerified:true,witnessCurrent:true})==="refuted-with-witness");
 test("NX-04-no-predicate-proof",()=>absence({...base,predicateEvaluated:false})==="not-established");
 test("NX-05-ABA-history-vs-current",()=>{
   const t0={time:0,rows:0},t1={time:1,rows:1},t2={time:2,rows:0};
   const sameValue=t0.rows===t2.rows;
   const changed=t0.rows!==t1.rows || t1.rows!==t2.rows;
   return sameValue && changed && absence(base)==="qualified-within-scope" &&
     unchangedSince([{time:1,delta:1},{time:2,delta:-1}],true)==="changed";
 });
 test("NX-06-filter-limit-noncommutative",()=>{
   const rows=[{id:"A",active:false},{id:"B",active:true}];
   return same(query(rows,true),["B"]) && same(query(rows,false),[]) &&
     !same(query(rows,true),query(rows,false));
 });
 test("NX-07-two-windows-local-stale",()=>{
   const win1={id:"W1",selection:"B",epoch:"e2",source:"s1"};
   const win2={id:"W2",selection:"A",epoch:"e1",source:"s1"};
   const oldW1={window:"W1",selection:"A",epoch:"e1",source:"s1"};
   const ownW2={window:"W2",selection:"A",epoch:"e1",source:"s1"};
   return !adopt(win1,oldW1)&&!adopt(win2,oldW1)&&adopt(win2,ownW2);
 });
 test("NX-08-relation-rebinding",()=>{
   const v1={displayAmount:600,customer:"C1",creditLimit:700};
   const v2={displayAmount:600,customer:"C2",creditLimit:500};
   return v1.displayAmount===v2.displayAmount &&
     (v1.creditLimit>=v1.displayAmount)!==(v2.creditLimit>=v2.displayAmount) &&
     currentRecheck({dependencies:["customerRef","creditLimit"],changed:["customerRef"],
       opaqueDependencies:false,currentReadAndGrantVerified:true})==="requalify";
 });
 test("NX-09-unobserved-not-unchanged",()=>currentRecheck({
   dependencies:["holds"],changed:[],opaqueDependencies:true,
   currentReadAndGrantVerified:false})==="not-established");
 test("NX-10-unrelated-change",()=>currentRecheck({
   dependencies:["orderAmount"],changed:["unrelatedMarkdownTitle"],
   opaqueDependencies:false,currentReadAndGrantVerified:true})==="eligible-for-claim-review");
 test("NX-11-transitive-implementation-pin",()=>{
   const p={role:{version:"1",contract:"c1",implementation:"i1"},
       lib:{version:"1",contract:"cl1",implementation:"il1"}};
   const a={role:{...p.role,eagerDependencies:["lib"]},
       lib:{...p.lib,eagerDependencies:[]}};
   const b={role:a.role,lib:{...a.lib,implementation:"il2"}};
   return pinValid("role",p,a)&&!pinValid("role",p,b);
 });
 test("NX-12-discovery-not-complete",()=>{
   const selected=["model catalog","inspect"];
   const dispatcher=["model catalog","inspect","operations","artifacts"];
   return !selected.includes("operations") && dispatcher.includes("operations");
 });
 test("NX-13-policy-only-change",()=>{
   const historical={value:600,sourceRevision:"s1"};
   const earlier={canDisclose:true,currentGrant:true};
   const later={canDisclose:false,currentGrant:true};
   return historical.value===600 && earlier.canDisclose && !later.canDisclose;
 });
 test("NX-14-output-unchanged-rule-change",()=>{
   const before={outputDigest:"same",rule:"r1"},after={outputDigest:"same",rule:"r2"};
   return before.outputDigest===after.outputDigest && before.rule!==after.rule &&
     currentRecheck({dependencies:["rule"],changed:["rule"],opaqueDependencies:false,
       currentReadAndGrantVerified:true})==="requalify";
 });
 test("NX-15-unqualified-scope-witness",()=>absence({...base,rowsetComplete:false,
    matchedWitness:true,witnessScopeAndPredicateVerified:false,witnessCurrent:true})==="not-established");
 test("NX-16-stale-witness",()=>absence({...base,rowsetComplete:false,
    matchedWitness:true,witnessScopeAndPredicateVerified:true,witnessCurrent:false})==="not-established");
 test("NX-17-no-notification-is-not-no-change",()=>unchangedSince([],false)==="not-established" &&
    unchangedSince([],true)==="unchanged" && unchangedSince([{delta:1}],true)==="changed");
 return {name:"SK-N bounded synthetic negative-witness selfcheck",cases:out,checks:out.length,
   status:"PASS",scope:"public deterministic reference; no Product/Provider/Host/Harness execution"};
}
if(typeof module!=="undefined"){
 module.exports={runSelfcheck,absence,currentRecheck};
 if(typeof require==="function"&&require.main===module)
   console.log(JSON.stringify(runSelfcheck(),null,2));
}
