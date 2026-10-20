import test from 'node:test';
import assert from 'node:assert/strict';

import {ACTIVITY} from '../core/model.js';
import {buildOracleIngressPacket,ORACLE_NATIVE_CONTRACT,ORACLE_NATIVE_SCOPE} from '../adapters/oracle-native-contract.js';

const base={
  sessionId:'oracle-session',leaseId:'oracle-lease',generation:4,sequence:1,eventId:'oracle-event-1',
  actionId:'FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003-g4',label:'Generate candidate',detail:'Local bounded pre-outcome reasoning',
};

test('Oracle start packet binds explicit visual semantics and no economic claims',()=>{
  const packet=buildOracleIngressPacket({...base,type:'ACTION_STARTED'});
  assert.equal(packet.scope,ORACLE_NATIVE_SCOPE);
  assert.equal(packet.worker_id,'oracle-research-v1');
  assert.equal(packet.ui_activity,ACTIVITY.HYPOTHESIS_GENERATION);
  assert.equal(packet.ui_role,'researcher');
  assert.equal(packet.ui_label,'Oracle');
  assert.ok(!Object.hasOwn(packet,'progress'));
  assert.ok(!Object.hasOwn(packet,'economic_result'));
});

test('heartbeat is explicit presence packet with no hypothesis-generation motion authority',()=>{
  const packet=buildOracleIngressPacket({...base,type:'WORKER_HEARTBEAT'});
  assert.equal(packet.ui_activity,ACTIVITY.NONE);
  assert.equal(ORACLE_NATIVE_CONTRACT.heartbeatAuthorizesBusinessMotion,false);
});

test('completion requires durable effect proof and clears activity',()=>{
  const packet=buildOracleIngressPacket({...base,type:'ACTION_COMPLETED',effectProof:{exit_code:0,output_sha256:'a'.repeat(64)}});
  assert.equal(packet.ui_activity,ACTIVITY.NONE);
  assert.deepEqual(packet.effect_proof,{exit_code:0,output_sha256:'a'.repeat(64)});
  assert.throws(()=>buildOracleIngressPacket({...base,type:'ACTION_COMPLETED'}),/EFFECT_PROOF_REQUIRED/);
});

test('effect proof cannot be attached to start or heartbeat',()=>{
  assert.throws(()=>buildOracleIngressPacket({...base,type:'ACTION_STARTED',effectProof:{exit_code:0,output_sha256:'b'.repeat(64)}}),/EFFECT_PROOF_ONLY_ALLOWED/);
});

test('contract refuses to claim a production endpoint before Site principal deployment',()=>{
  assert.equal(ORACLE_NATIVE_CONTRACT.ingressEndpoint,'UNBOUND_UNTIL_SITE_PRINCIPAL_IS_DEPLOYED');
  assert.equal(ORACLE_NATIVE_CONTRACT.authenticatedPrincipalRequired,true);
  assert.equal(ORACLE_NATIVE_CONTRACT.economicOutcomeFieldsAllowed,false);
});
