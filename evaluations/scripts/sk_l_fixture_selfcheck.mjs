// Public synthetic reference consistency only. Not a Product/Skill/Harness test.
// Expectations are public and are not a sealed holdout.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const fixturePath = resolve(dirname(fileURLToPath(import.meta.url)), "..", "fixtures", "SK-01-authoring-context.synthetic.json");
const fixture = JSON.parse(readFileSync(fixturePath, "utf8"));

function evaluateFixture(f) {
  const cases=Object.fromEntries(f.cases.map(c=>[c.id,c]));
  const results=[];
  const check=(id,computed,expected,note)=>results.push({id,pass:computed===expected,computed,expected,note});
  let c=cases["SK-L01"];
  check("SK-L01",c.input.occurrences.some(x=>x.fetched)||c.input.fetch_authorized,false,"L0 URLs never imply paper body retrieval");
  c=cases["SK-L02"];
  check("SK-L02",c.input.occurrences.length-new Set(c.input.occurrences.map(x=>x.url)).size,1,"One duplicate occurrence but not an explicit cites edge");
  check("SK-L02-edge",c.input.explicit_academic_edges.length,0,"Indent is not an academic edge");
  c=cases["SK-L03"];
  check("SK-L03",c.input.semantic_role_declared,false,"A visually function-like table remains unbound authoring");
  c=cases["SK-L04"];
  check("SK-L04",c.input.semantic_role_declared && c.input.role==="Function" && c.input.rounding_policy===null && c.input.actual_test_run===false,true,"Function interpretation may be proposed, numeric policy and run remain unresolved");
  c=cases["SK-L05"];
  check("SK-L05",c.input.data_model_relations.length>0 && c.input.function_context.explicit_mappings.length===0 && c.input.fetch_request===false,true,"Data Model relations alone do not authorize/fetch rows");
  c=cases["SK-L06"];
  check("SK-L06",c.input.function_context.explicit_mappings.map(x=>x.path).join("|"),"order.lines","Only explicitly mapped line fields, not allocations/private notes");
  check("SK-L06-fetch",c.input.observed_fetches.length,0,"Declared mapping is not observed Provider fetch");
  c=cases["SK-L07"];
  check("SK-L07",c.input.provider_response.rows.length===0 && c.input.provider_response.complete===false,true,"Empty partial response does not prove absence");
  c=cases["SK-L08"];
  check("SK-L08",c.input.projection.lossy && c.input.edit.typed_action_binding===null && c.input.edit.source_identity_map===null,true,"Lossy derived view lacks typed reverse-write contract");
  c=cases["SK-L09"];
  check("SK-L09",c.input.native_sql.present && !c.input.native_sql.explicit_binding && c.input.provider_capabilities.atomic_batch===null,true,"Native SQL unbound and batch atomicity unknown");
  c=cases["SK-L10"];
  check("SK-L10",!c.input.document_fetched && c.input.design_proposal_created && !c.input.tei_meaning_accepted && !c.input.independent_test_executed,true,"Proposal not paper-reproduction or tested implementation");
  const result={fixture_id:f.fixture_id,classification:"pure-fixture-reference-invariants",pass:results.every(x=>x.pass),assertions:results.length,passed:results.filter(x=>x.pass).length,failed:results.filter(x=>!x.pass).length,results};
  if(!result.pass)throw Error("Synthetic fixture invariant failed: "+JSON.stringify(result.results.filter(x=>!x.pass)));
  return result;
}

const result = evaluateFixture(fixture);
console.log(JSON.stringify(result, null, 2));
