import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';

const here=dirname(fileURLToPath(import.meta.url));
const root=resolve(here,'..');
async function json(rel){return JSON.parse(await readFile(resolve(root,rel),'utf8'));}

test('preprod capability registry exposes final roles but launches none in production',async()=>{
  const registry=await json('runtime/CAPABILITY_REGISTRY.json');
  assert.equal(registry.mode,'PREPROD_SIMULATION_ONLY');
  assert.equal(registry.production_worker_launch_authorized,false);
  assert.equal(registry.economic_experiment_authorized,false);
  assert.equal(registry.prospective_observation_authorized,false);
  assert.equal(registry.real_capital_authorized,false);
  assert.equal(registry.live_trading_authorized,false);

  const ids=new Set(registry.capabilities.map(x=>x.capability_id));
  for(const expected of ['legacy_recovery','quant_mechanisms','fundamental','event_document','institutional_flows','validator','red_team','portfolio_map']){
    assert.ok(ids.has(expected),expected);
  }
  for(const capability of registry.capabilities){
    assert.equal(capability.production_enabled,false,capability.capability_id);
    assert.equal(capability.simulation_enabled,true,capability.capability_id);
  }
});

test('synthetic final architecture simulation exercises the intended stage ordering',async()=>{
  const sim=await json('simulations/FINAL_ARCHITECTURE_V0.json');
  assert.equal(sim.mode,'SYNTHETIC_PREPROD');
  assert.equal(sim.synthetic_candidate.economic_data_real,false);
  assert.deepEqual(sim.stages.map(x=>x.capability),[
    'fundamental',
    'event_document',
    'validator',
    'red_team',
    'portfolio_map',
    'validator'
  ]);
  assert.equal(sim.expected_terminal_state.decision,'PARK');
  assert.equal(sim.expected_terminal_state.capital_authority,'NONE');
  for(const value of Object.values(sim.assertions))assert.equal(value,false);
});

test('portfolio map contract cannot carry capital authority',async()=>{
  const contract=await json('contracts/portfolio-map-entry.schema.json');
  assert.equal(contract.properties.capital_authority.const,'NONE');
});

test('prospective contract separates evidence timing, integrity and authorization',async()=>{
  const contract=await json('contracts/prospective-contract.schema.json');
  assert.ok(contract.properties.evidence_timing);
  assert.ok(contract.properties.prospective_integrity);
  assert.ok(contract.properties.observation_authorization);
});

test('trial ledger separates observed attempts from estimated effective trials',async()=>{
  const contract=await json('contracts/trial-ledger.schema.json');
  assert.ok(contract.properties.observed_attempt_count);
  assert.ok(contract.properties.estimated_effective_trials);
  assert.deepEqual(contract.properties.effective_trials_status.enum,[
    'KNOWN','ESTIMATED','PARTIALLY_BOUNDED','UNKNOWN'
  ]);
});
