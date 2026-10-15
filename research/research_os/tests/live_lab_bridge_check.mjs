import fs from 'node:fs';
import assert from 'node:assert/strict';
import { mapNativeWorkerEvent } from '../../live_lab_ux/adapters/platform-native.js';

const result = JSON.parse(fs.readFileSync('research/research_os/simulations/multi_engine_result.json', 'utf8'));
assert.equal(result.status, 'PASS');
assert.ok(Array.isArray(result.worker_events));
assert.ok(result.worker_events.length >= 14);

const mapped = result.worker_events.map(mapNativeWorkerEvent);
assert.equal(mapped.filter(Boolean).length, result.worker_events.length);
for (const event of mapped) {
  assert.ok(event.id);
  assert.ok(event.stream.startsWith('native:'));
  assert.ok(event.at);
}
console.log(`LIVE_LAB_BRIDGE=PASS events=${mapped.length}`);
