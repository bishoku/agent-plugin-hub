#!/usr/bin/env node
// Developer-only: run teaching fixtures through the real product scheduler.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {createRequire} = require('node:module');
const source = process.argv[2];
if (!source) { console.error('Usage: node scripts/check_yada_playback.cjs /path/to/diagramer'); process.exit(1); }
const product = path.resolve(source);
const ts = createRequire(path.join(product,'package.json'))('typescript');
const code = ts.transpileModule(fs.readFileSync(path.join(product,'src/store/scheduler.ts'),'utf8'), {
  compilerOptions: {module:ts.ModuleKind.CommonJS},
}).outputText;
const context = {exports:{}};
vm.runInNewContext(code, context);
const fixtures = path.resolve(__dirname,'../plugins/yada/skills/dproj-generator/assets/examples');
function schedule(name) {
  const d = JSON.parse(fs.readFileSync(path.join(fixtures,`${name}.json`),'utf8'));
  return context.exports.calculateSchedules(d.logicalData.sequences,d.visualData.timelines,d.logicalData.edges,d.logicalData.nodes);
}
const fanout = schedule('event-fanout');
assert.equal(fanout.s2.start, fanout.s1.end);
assert.equal(fanout.s2.start, fanout.s3.start);
const rag = schedule('agent-rag');
assert.ok(rag.s4.start >= rag.s2.end, 'generation must wait for retrieval');
assert.ok(rag.s1.end > rag.s4.end, 'outer request returns after generation');
const saga = schedule('saga-compensation');
assert.ok(saga.s3.start >= saga.s2.end, 'compensation follows declined payment');
const request = schedule('request-cache');
assert.ok(request.s4.start >= request.s3.end, 'store after cache lookup');
assert.ok(request.s1.end > request.s2.end, 'outer return after nested call');
console.log('Product scheduler verified: fan-out, RAG, compensation, nested request/cache. Rendering remains a separate check.');
