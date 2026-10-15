import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';
import {mapNativeWorkerEvent} from '../../live_lab_ux/adapters/platform-native.js';

const here=dirname(fileURLToPath(import.meta.url));
const root=resolve(here,'..');

async function json(rel){return JSON.parse(await readFile(resolve(root,rel),'utf8'));}

const contractPaths=[
  'contracts/research-task.schema.json',
  'contracts/worker-event.schema.json',
  'contracts/worker-receipt.schema.json',
  'contracts/hypothesis.schema.json',
  'contracts/experiment-result.schema.json',
  'contracts/evidence-assessment.schema.json',
  'contracts/economic-identity.schema.json',
  'contracts/trial-ledger.schema.json',
  'contracts/prospective-contract.schema.json',
  'contracts/decision-record.schema.json',
  'contracts/portfolio-map-entry.schema.json'
];

test('all final-shape thin contracts parse as JSON',async()=>{
  for(const path of contractPaths){
    const doc=await json(path);
    assert.equal(doc.type,'object',path);
    assert.ok(Array.isArray(doc.required),path);
  }
});

test('autonomy canary is terminal PASS and stayed non-economic',async()=>{
  const task=await json('tasks/AUTONOMY-CANARY-001.json');
  assert.equal(task.status,'COMPLETE');
  assert.equal(task.completion.result,'PASS');
  assert.equal(task.lease.generation,1);
  assert.ok(task.completion.receipt);
  assert.equal(task.completion.artifacts.length,2);
  assert.equal(task.authority.economic_experiment_authorized,false);
  assert.equal(task.authority.prospective_observation_authorized,false);
  assert.equal(task.authority.real_capital_authorized,false);
  assert.equal(task.authority.live_trading_authorized,false);
});

test('native-shaped worker event remains consumable by the existing Live Lab mapper',()=>{
  const event={
    event_id:'evt-sim-1',
    session_id:'session-sim',
    worker_id:'simulated-worker',
    action_id:'SIM-TASK',
    event_type:'ACTION_STARTED',
    event_seq:1,
    generation:1,
    emitted_at:'2026-10-15T00:00:00Z',
    payload:{label:'Synthetic architecture simulation',detail:'Contract-only preprod flow'}
  };
  const mapped=mapNativeWorkerEvent(event);
  assert.ok(mapped);
  assert.equal(mapped.workerId,'simulated-worker');
  assert.equal(mapped.task,'Synthetic architecture simulation');
  assert.equal(mapped.progress.mode,'UNKNOWN');
});
