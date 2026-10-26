import test from 'node:test';
import assert from 'node:assert/strict';
import * as T from '../ui/vendor/three.js';
import {buildHumanoid} from '../ui/characters.js';
test('reading head articulation remains attached to its neck',()=>{
 const parent=new T.Group(),agent=buildHumanoid(parent);parent.updateMatrixWorld(true);
 const before=new T.Box3().setFromObject(agent.head).getCenter(new T.Vector3());
 agent.head.rotation.x=.25;parent.updateMatrixWorld(true);
 const after=new T.Box3().setFromObject(agent.head).getCenter(new T.Vector3());
 assert.ok(after.distanceTo(before)<.07,'a reading nod must not carry the head away from the neck');
 assert.ok(new T.Box3().setFromObject(agent.head).getSize(new T.Vector3()).y>.20,'retain an adult-sized head');
});
