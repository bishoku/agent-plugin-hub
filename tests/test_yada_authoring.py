"""Behavioral coverage for authoring, migration and lossless project editing."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'plugins/yada/skills/dproj-generator'
sys.path.insert(0,str(SKILL/'scripts'))
from diagram_validation import validate_diagram, geometry_warnings, load_components
from pack_dproj import prepare_diagram
from unpack_dproj import unpack


class AuthoringTests(unittest.TestCase):
    def setUp(self): self.data=json.loads((SKILL/'assets/example-diagram.json').read_text())
    def run_tool(self, name, *args):
        return subprocess.run([sys.executable,str(SKILL/'scripts'/name),*map(str,args)],capture_output=True,text=True)
    def test_examples_pack_without_repairs(self):
        for path in (SKILL/'assets/examples').glob('*.json'):
            with self.subTest(path=path.name), tempfile.TemporaryDirectory() as directory:
                output=Path(directory)/'out.dproj'
                result=self.run_tool('pack_dproj.py',output,SKILL/'assets/example-workspace.json',path,'--components-dir',SKILL/'assets/examples/components')
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertNotIn('Repair:',result.stdout)
                with zipfile.ZipFile(output) as archive:
                    self.assertEqual(json.loads(archive.read('diagram.json')),json.loads(path.read_text()))
                    self.assertIn('components/custom-comp-device.json',archive.namelist())
    def test_invalid_structure_is_diagnostic(self):
        for value in (None,[],{}, {'schemaVersion':2,'logicalData':{'nodes':[None,{'id':[]}],'edges':[3],'sequences':False},'visualData':{'layoutNodes':None}}):
            with self.subTest(value=value): self.assertTrue(validate_diagram(value))
    def test_duplicates_parent_cycles_invalid_timing_and_enums(self):
        mutations=[
            lambda d:d['logicalData']['nodes'].append(copy.deepcopy(d['logicalData']['nodes'][0])),
            lambda d:d['logicalData']['nodes'][2].update(parentId='s-core'),
            lambda d:d['logicalData']['nodes'][0].update(parentId='n-gw'),
            lambda d:d['visualData']['timelines']['s1'].update(duration=-1),
            lambda d:d['visualData']['timelines']['s1'].update(delay=float('nan')),
            lambda d:d['visualData']['timelines'].pop('s1'),
            lambda d:d['visualData']['layoutEdges']['e1'].update(connectionType='invented'),
            lambda d:d['logicalData']['edges'][0].update(targetId='s-core'),
            lambda d:d['visualData']['layoutNodes']['n-client'].update(x='zero'),
            lambda d:d['visualData']['layoutEdges']['e1'].update(sourceHandle='right:25'),
        ]
        for mutation in mutations:
            d=copy.deepcopy(self.data); mutation(d); self.assertTrue(validate_diagram(d))
    def test_sequence_imported_service_preserved(self):
        self.data['logicalData']['nodes'][0]['type']='service'
        fixed,repairs,errors=prepare_diagram(self.data)
        self.assertFalse(errors)
        self.assertEqual(fixed['logicalData']['nodes'][0]['type'],'service')

    def test_preview_size_limit_and_local_target(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'diagram.json'; output=Path(folder)/'preview.md'
            path.write_text(json.dumps(self.data))
            result=self.run_tool('build_share_url.py',path,'--name','Local','--base-url','http://localhost:5173/','--output-md',output)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('http://localhost:5173/#share=',output.read_text())
            output.unlink()
            import random
            randomizer=random.Random(17)
            self.data['logicalData']['nodes'][0]['properties']={'large': ''.join(randomizer.choices('abcdefghijklmnopqrstuvwxyz0123456789',k=80000))}
            path.write_text(json.dumps(self.data))
            result=self.run_tool('build_share_url.py',path,'--name','Large','--output-md',output)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('32,000',result.stderr)
            self.assertFalse(output.exists())

    def test_all_current_node_types_supported(self):
        from diagram_validation import VALID_TYPES
        for typ in VALID_TYPES-{'section'}:
            d=copy.deepcopy(self.data); d['logicalData']['nodes'][0]['type']=typ
            self.assertEqual(validate_diagram(d),[],typ)
    def test_geometry_excludes_ancestors_but_finds_overflow(self):
        d=json.loads((SKILL/'assets/examples/nested-platform.json').read_text())
        self.assertEqual(geometry_warnings(d),[])
        d['visualData']['layoutNodes']['service']['x']=1000
        self.assertTrue(any('outside section' in w for w in geometry_warnings(d)))
    def test_legacy_repairs_are_opt_in_and_nonmutating(self):
        self.data['visualData']['layoutEdges']['e1']['sourceHandle']='right:25'
        original=copy.deepcopy(self.data)
        _,repairs,errors=prepare_diagram(self.data)
        self.assertTrue(errors); self.assertFalse(repairs)
        fixed,repairs,errors=prepare_diagram(self.data,True)
        self.assertFalse(errors); self.assertTrue(repairs)
        self.assertEqual(self.data,original)
        self.assertTrue(any(h['id']=='right:25' for h in fixed['visualData']['layoutNodes']['n-client']['handles']))
        self.data['schemaVersion']=99
        self.assertTrue(prepare_diagram(self.data,True)[2])
    def test_component_missing_and_malformed(self):
        d=json.loads((SKILL/'assets/examples/custom-device.json').read_text())
        self.assertTrue(load_components(None,d)[1])
        self.assertFalse(load_components(SKILL/'assets/examples/components',d)[1])
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder)/'custom-comp-device.json').write_text('{"componentId":"wrong"}')
            self.assertTrue(load_components(folder,d)[1])
    def test_edit_preserves_unknown_fields_components_and_extras(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); source=root/'input.dproj'; dest=root/'edit'; output=root/'out.dproj'
            self.data['futureExtension']={'opaque':[1,2,3]}
            with zipfile.ZipFile(source,'w') as archive:
                archive.writestr('diagram.json',json.dumps(self.data))
                archive.writestr('workspace.json',(SKILL/'assets/example-workspace.json').read_bytes())
                archive.writestr('assets/preserved.bin',b'\x00unchanged\xff')
                archive.writestr('components/custom-comp-device.json',(SKILL/'assets/examples/components/custom-comp-device.json').read_bytes())
            unpack(source,dest)
            d=json.loads((dest/'diagram.json').read_text()); d['logicalData']['nodes'][0]['name']='Renamed'
            (dest/'diagram.json').write_text(json.dumps(d))
            result=self.run_tool('pack_dproj.py',output,dest/'workspace.json',dest/'diagram.json','--components-dir',dest/'components','--extras-dir',dest)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(json.loads(archive.read('diagram.json')),d)
                self.assertEqual(archive.read('assets/preserved.bin'),b'\x00unchanged\xff')
                self.assertIn('components/custom-comp-device.json',archive.namelist())
    def test_unpack_rejects_traversal_without_creating_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); source=root/'bad.dproj'; dest=root/'edit'
            with zipfile.ZipFile(source,'w') as z: z.writestr('../escape','bad')
            with self.assertRaises(ValueError): unpack(source,dest)
            self.assertFalse(dest.exists()); self.assertFalse((root/'escape').exists())
    def test_sequence_references_checked(self):
        d=json.loads((SKILL/'assets/examples/sequence-alternatives.json').read_text())
        self.assertFalse(validate_diagram(d))
        d['logicalData']['sequenceDiagram']['events'][2]['branches'][0]['events'][0]['sequenceId']='missing'
        self.assertTrue(validate_diagram(d))
    def test_preview_custom_components_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'preview.md'
            result=self.run_tool('build_share_url.py',SKILL/'assets/examples/custom-device.json','--name','Custom','--output-md',output)
            self.assertNotEqual(result.returncode,0); self.assertFalse(output.exists())
    def test_report_bounded_and_does_not_claim_visual_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'diagram.json'; report=Path(folder)/'report.json'
            for node in self.data['visualData']['layoutNodes'].values(): node['x']=0; node['y']=0
            path.write_text(json.dumps(self.data))
            result=self.run_tool('check_diagram.py',path,'--limit','1','--report',report)
            self.assertEqual(result.returncode,0)
            self.assertLessEqual(len(result.stdout.splitlines()),3)
            content=json.loads(report.read_text()); self.assertFalse(content['visualVerified']); self.assertGreater(len(content['warnings']),1)

if __name__=='__main__': unittest.main()
