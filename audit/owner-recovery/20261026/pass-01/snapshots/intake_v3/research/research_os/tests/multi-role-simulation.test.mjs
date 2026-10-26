import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';

const here=dirname(fileURLToPath(import.meta.url));
const root=resolve(here,'..');
async function json(rel){return JSON.parse(await readFile(resolve(root,rel),'utf8'));}

test('control plane routes workflow lanes and forbids invented work',async()=>{
  const cp=await json('runtime/CONTROL_PLANE.json');
  assert.equal(cp.mode,'PRODUCTION_RESEARCH_WORKERS');
  assert.equal(cp.workflow_model,'ONE_LINEAGE_MULTI_STAGE');
  assert.equal(cp.task_selection.invent_work_when_empty,false);
  assert.equal(cp.task_selection.max_lineages_per_wake,1);
  assert.equal(cp.task_selection.multi_stage_same_lineage,true);
  assert.equal(cp.claim_protocol.optimistic_lock,'CURRENT_BLOB_SHA');
  assert.equal(cp.global_authority.production_worker_launch_authorized,true);
  assert.equal(cp.global_authority.economic_experiment_authorized,false);
  assert.equal(cp.global_authority.prospective_observation_authorized,false);
  assert.equal(cp.global_authority.real_capital_authorized,false);
  assert.equal(cp.global_authority.live_trading_authorized,false);
  const lanes=new Set(cp.routing.map(x=>x.lane));
  for(const expected of ['market_discovery','fundamental_events','evidence_data','independent_challenge','integrator_portfolio']) assert.ok(lanes.has(expected));
  assert.equal(cp.independence_rules.discovery_lane_may_not_validate_own_hypothesis,true);
});

test('parallel specialist simulation converges through shared governed pipeline',async()=>{
  const sim=await json('simulations/MULTI_ROLE_PARALLEL_V0.json');
  assert.equal(sim.mode,'SYNTHETIC_PREPROD');
  assert.equal(sim.candidates.length,4);
  assert.deepEqual(sim.candidates.map(x=>x.origin_capability),[
    'quant_mechanisms','fundamental','event_document','institutional_flows'
  ]);
  assert.deepEqual(sim.shared_pipeline,[
    'FROZEN_HYPOTHESIS','VALIDATOR','RED_TEAM','ECONOMIC_IDENTITY','PORTFOLIO_MAP','DECISION_RECORD'
  ]);
  assert.equal(sim.duplicate_control.cross_candidate_overlap_check_required,true);
  assert.equal(sim.assertions.shared_conversation_memory_required,false);
  assert.equal(sim.assertions.production_workers_launched,false);
  assert.equal(sim.assertions.real_capital_authorized,false);
});

test('scientific ledger can reference negative knowledge and portfolio map independently',async()=>{
  const ledger=await json('contracts/scientific-ledger-entry.schema.json');
  assert.ok(ledger.properties.refs.properties.negative_knowledge);
  assert.ok(ledger.properties.refs.properties.portfolio_map_entry);
  assert.ok(ledger.properties.refs.properties.prospective_contracts);
});
