#!/usr/bin/env node
// Exercise the real importer with in-memory storage; no browser/workspace writes.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {createRequire} = require('node:module');
const {execFileSync} = require('node:child_process');
const source = process.argv[2];
if (!source) { console.error('Usage: node scripts/check_yada_import.cjs /path/to/diagramer'); process.exit(1); }
const product = path.resolve(source);
const productRequire = createRequire(path.join(product, 'package.json'));
const ts = productRequire('typescript');
const writes = new Map();
const storage = {
  get_global_components_dir: async () => 'virtual://components',
  read_text_file: async () => { throw new Error('not found'); },
  save_text_file: async (name, content) => writes.set(name, content),
};
const code = ts.transpileModule(fs.readFileSync(path.join(product,'src/utils/workspaceZip.ts'),'utf8'), {
  compilerOptions: {module:ts.ModuleKind.CommonJS, esModuleInterop:true},
}).outputText;
const context = {exports:{}, console, require: name => {
  if (name === '../i18n/messages') return {message: () => 'imported'};
  if (name === '../services/storage') return {StorageService:storage,isTauri:()=>false};
  if (name.startsWith('@tauri-apps/')) return {};
  if (name === 'jszip') return productRequire(name);
  throw new Error(`Unexpected importer dependency ${name}; review the harness`);
}};
vm.runInNewContext(code,context);
const skill = path.resolve(__dirname,'../plugins/yada/skills/dproj-generator');
const examples = path.join(skill,'assets/examples');
const temporary = fs.mkdtempSync(path.join(os.tmpdir(),'yada-import-'));
(async () => {
  try {
    let count = 0;
    for (const file of fs.readdirSync(examples).filter(file=>file.endsWith('.json'))) {
      const input = path.join(examples,file), archive = path.join(temporary,'test.dproj');
      execFileSync(process.env.YADA_PYTHON || 'python3', [path.join(skill,'scripts/pack_dproj.py'),archive,path.join(skill,'assets/example-workspace.json'),input,'--components-dir',path.join(examples,'components')]);
      const expected = JSON.parse(fs.readFileSync(input,'utf8'));
      let saved;
      await context.exports.importWorkspace(fs.readFileSync(archive), async () => ({id:'test',name:'Test',path:'virtual://test'}), async (_path,_id,logical,visual) => { saved={logical:JSON.parse(logical),visual:JSON.parse(visual)}; }, async () => ({}), 'en');
      assert.deepEqual(saved.logical,expected.logicalData,file+' logical preservation');
      assert.deepEqual(saved.visual,expected.visualData,file+' visual preservation');
      count++;
    }
    assert.ok(writes.has('virtual://components/custom-comp-device.json'),'component template must reach library storage');
    console.log(`Product import verified: ${count} projects retain logical/visual data, custom template reaches library. Storage is mocked; this is not browser visual QA.`);
  } finally { fs.rmSync(temporary,{recursive:true,force:true}); }
})().catch(error=>{console.error(error);process.exitCode=1;});
