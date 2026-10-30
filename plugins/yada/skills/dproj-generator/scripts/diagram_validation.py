"""Portable authoring checks, not a replacement for YADA's renderer."""
import json
import math
from pathlib import Path

CAPABILITIES = json.loads((Path(__file__).resolve().parents[1] / 'assets/capabilities.json').read_text())
VALID_TYPES = set(CAPABILITIES['nodeTypes']) | set(CAPABILITIES.get('importedNodeTypes', []))
SIDES = {'top', 'right', 'bottom', 'left'}
DEFAULT_PORTS = {f'{side}:50' for side in SIDES}
EDGE_ENUMS = {
    'connectionType': {'bezier', 'smoothstep', 'step', 'straight'},
    'lineStyle': {'solid', 'dashed', 'dotted', 'longDash', 'dashDot'},
    'arrowStart': {'none', 'triangle', 'open', 'diamond', 'circle'},
    'arrowEnd': {'none', 'triangle', 'open', 'diamond', 'circle'},
    'glowIntensity': {'none', 'subtle', 'strong', 'neon'},
    'particleType': {'dot', 'arrow', 'envelope', 'rest', 'grpc', 'ws', 'graphql', 'kafka', 'pkg', 'sql'},
}


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_diagram(data):
    errors = []
    def fail(path, message): errors.append(f'{path}: {message}')
    def obj(value, path):
        if not isinstance(value, dict):
            fail(path, 'expected object'); return {}
        return value
    def arr(value, path):
        if not isinstance(value, list):
            fail(path, 'expected array'); return []
        return value
    def string(value, path):
        if not isinstance(value, str) or not value:
            fail(path, 'expected nonempty string'); return False
        return True
    def num(value, path, minimum=None, maximum=None):
        if not number(value) or (minimum is not None and value < minimum) or (maximum is not None and value > maximum):
            fail(path, f'expected finite number in [{minimum}, {maximum}]')
    def boolean(value, path):
        if not isinstance(value, bool): fail(path, 'expected boolean')
    def enum(value, choices, path):
        if not isinstance(value, str) or value not in choices: fail(path, 'invalid value')
    def indexed(value, path):
        out = {}
        for i, raw in enumerate(arr(value, path)):
            item = obj(raw, f'{path}[{i}]'); key = item.get('id')
            if string(key, f'{path}[{i}].id'):
                if key in out: fail(path, f'duplicate id {key}')
                out[key] = item
        return out
    def records(value, path, idfield='id'):
        out = {}
        for key, raw in obj(value, path).items():
            item = obj(raw, f'{path}.{key}')
            if item.get(idfield) != key: fail(f'{path}.{key}', f'{idfield} must match record key')
            out[key] = item
        return out
    def ref(value, collection, path):
        if not isinstance(value, str) or value not in collection: fail(path, f'{value!r} not found')
    def optional_enum(item, key, choices, path):
        if key in item: enum(item[key], choices, f'{path}.{key}')
    def point(raw, path):
        p = obj(raw, path)
        for k in ('x', 'y'): num(p.get(k), f'{path}.{k}')
    data = obj(data, 'diagram')
    ld = obj(data.get('logicalData'), 'logicalData'); vd = obj(data.get('visualData'), 'visualData')
    for path, value in [('schemaVersion', data.get('schemaVersion')), ('logicalData.schemaVersion', ld.get('schemaVersion'))]:
        if type(value) is not int or value != 2: fail(path, 'must be 2')
    nodes = indexed(ld.get('nodes'), 'nodes'); edges = indexed(ld.get('edges'), 'edges')
    seqs = indexed(ld.get('sequences'), 'sequences')
    vn = records(vd.get('layoutNodes'), 'layoutNodes'); ve = records(vd.get('layoutEdges'), 'layoutEdges')
    times = records(vd.get('timelines'), 'timelines', 'sequenceId')
    notes = records(vd.get('annotations', {}), 'annotations')
    for key in nodes.keys() & notes.keys(): fail(key, 'annotation cannot also be a logical node')
    for key in (nodes.keys() | notes.keys()) - vn.keys(): fail(key, 'missing layoutNodes entry')
    for key in vn.keys() - (nodes.keys() | notes.keys()): fail(key, 'orphan layoutNodes entry')
    for key in edges.keys() - ve.keys(): fail(key, 'missing layoutEdges entry')
    for key in ve.keys() - edges.keys(): fail(key, 'orphan layoutEdges entry')
    for key in seqs.keys() - times.keys(): fail(key, 'missing timeline')
    for key in times.keys() - seqs.keys(): fail(key, 'orphan timeline')
    canvas = obj(vd.get('canvas'), 'canvas')
    num(canvas.get('zoom'), 'canvas.zoom', .000001); point(canvas.get('pan'), 'canvas.pan')
    optional_enum(canvas, 'renderStyle', {'clean', 'sketchy'}, 'canvas')
    ports = {}
    for key, n in nodes.items():
        string(n.get('name'), f'{key}.name')
        t = n.get('type')
        if not isinstance(t, str) or (t not in VALID_TYPES and not t.startswith('custom-comp-')): fail(key, f'unknown type {t!r}')
        if 'properties' in n:
            props = obj(n['properties'], f'{key}.properties')
            if 'sequenceIds' in props:
                for sid in arr(props['sequenceIds'], f'{key}.sequenceIds'): ref(sid, seqs, f'{key}.sequenceIds')
            optional_enum(props, 'fragmentType', {'alt','opt','loop','par','critical','break','rect','ref'}, key)
        parent = n.get('parentId')
        if parent is not None:
            ref(parent, nodes, f'{key}.parentId')
            if isinstance(parent, str) and parent in nodes and nodes[parent].get('type') != 'section': fail(key, 'parent must be section')
        seen = {key}; cursor = parent
        while isinstance(cursor, str) and cursor in nodes:
            if cursor in seen: fail(key, 'parent cycle'); break
            seen.add(cursor); cursor = nodes[cursor].get('parentId')
    for key, v in vn.items():
        point(v, key)
        for k in ('width', 'height'):
            if k in v: num(v[k], f'{key}.{k}', .000001)
        if nodes.get(key, {}).get('type') == 'section':
            for k in ('width','height'):
                if k not in v: fail(key, f'section requires {k}')
        optional_enum(v, 'displayMode', {'default','icon-only'}, key)
        handles = v.get('handles', [])
        if not isinstance(handles, list): fail(key, 'handles must be array'); handles = []
        ports[key] = set() if handles else DEFAULT_PORTS
        for i, raw in enumerate(handles):
            h = obj(raw, f'{key}.handles[{i}]'); hid = h.get('id')
            if string(hid, f'{key}.handle.id'):
                if hid in ports[key]: fail(key, f'duplicate handle {hid}')
                ports[key].add(hid)
            enum(h.get('side'), SIDES, f'{key}.handle.side'); num(h.get('offset'), f'{key}.handle.offset', 0, 100)
        styles = obj(v.get('customStyles', {}), f'{key}.customStyles')
        for field, choices in {'borderStyle':{'solid','dashed','dotted'},'sectionTitleMode':{'inline','header','none'},'sectionTitleEdge':SIDES,'sectionTitleAlign':{'left','center','right'},'iconLabelPosition':{'none','top','bottom','left','right'}}.items(): optional_enum(styles, field, choices, key)
        if 'bgOpacity' in styles: num(styles['bgOpacity'], f'{key}.bgOpacity', 0, 1)
        if 'productIcon' in styles: enum(styles['productIcon'], set(CAPABILITIES['productIcons']), f'{key}.productIcon')
        if 'freeformContent' in v and v['freeformContent'] is not None:
            content = obj(v['freeformContent'], f'{key}.freeformContent'); arr(content.get('elements'), f'{key}.elements')
    for key, edge in edges.items():
        boolean(edge.get('isAsync'), f'{key}.isAsync')
        for field in ('sourceId','targetId'):
            endpoint = edge.get(field); ref(endpoint, nodes, f'{key}.{field}')
            if isinstance(endpoint, str) and nodes.get(endpoint, {}).get('type') == 'section': fail(key, 'edges cannot connect sections')
        visual = ve.get(key, {})
        for field, choices in EDGE_ENUMS.items(): optional_enum(visual, field, choices, key)
        for field, endpoint in [('sourceHandle',edge.get('sourceId')),('targetHandle',edge.get('targetId'))]:
            if field in visual: ref(visual[field], ports.get(endpoint, set()) if isinstance(endpoint,str) else set(), f'{key}.{field}')
        if 'labelPosition' in visual: num(visual['labelPosition'], f'{key}.labelPosition',0,100)
        if 'strokeWidth' in visual: num(visual['strokeWidth'], f'{key}.strokeWidth',.000001)
        if 'waypoints' in visual:
            for i,p in enumerate(arr(visual['waypoints'],f'{key}.waypoints')): point(p,f'{key}.waypoints[{i}]')
    for key, seq in seqs.items():
        ref(seq.get('edgeId'), edges, f'{key}.edgeId'); boolean(seq.get('isAsync'), f'{key}.isAsync')
        step = seq.get('stepNumber')
        if type(step) is not int or step < 1: fail(key, 'stepNumber must be positive integer')
        if 'isRoundTrip' in seq: boolean(seq['isRoundTrip'], f'{key}.isRoundTrip')
        t = times.get(key, {})
        for k in ('duration','delay'): num(t.get(k), f'{key}.{k}', 0)
        optional_enum(t, 'animationMode', {'normal','roundTrip','repeat'}, key)
        if t.get('animationMode') == 'roundTrip' and not seq.get('isRoundTrip'): fail(key, 'roundTrip mode requires isRoundTrip')
        if seq.get('isRoundTrip') and t.get('animationMode','roundTrip') != 'roundTrip': fail(key, 'isRoundTrip conflicts with animationMode')
        if 'repeatParticleCount' in t or t.get('animationMode') == 'repeat':
            count = t.get('repeatParticleCount')
            if type(count) is not int or count < 1: fail(key, 'repeatParticleCount must be positive integer')
        if 'internalProcess' in t:
            process = obj(t['internalProcess'], f'{key}.internalProcess')
            string(process.get('text'), f'{key}.internalProcess.text'); num(process.get('duration'), f'{key}.internalProcess.duration',0)
    for key, note in notes.items():
        for k in ('header','body'):
            if not isinstance(note.get(k),str): fail(key, f'{k} must be string')
        style = obj(note.get('style'), f'{key}.style')
        for k in ('backgroundColor','borderColor','textColor','fontFamily'): string(style.get(k),f'{key}.style.{k}')
        for k in ('fontSize','borderRadius'): num(style.get(k),f'{key}.style.{k}',0)
        num(style.get('opacity'),f'{key}.style.opacity',0,1)
        if 'alwaysVisible' in note: boolean(note['alwaysVisible'], f'{key}.alwaysVisible')
        for k in ('startTime','endTime'): num(note.get(k),f'{key}.{k}',0)
        if number(note.get('startTime')) and number(note.get('endTime')) and note['endTime'] < note['startTime']: fail(key,'endTime precedes startTime')
    strokes = records(vd.get('freehandStrokes',{}),'freehandStrokes')
    for key, stroke in strokes.items():
        enum(stroke.get('tool'),{'select','rectangle','ellipse','diamond','line','arrow','pen','highlighter','text','eraser'},f'{key}.tool')
        for p in arr(stroke.get('points'),f'{key}.points'): point(p,key)
        string(stroke.get('color'),f'{key}.color'); num(stroke.get('size'),f'{key}.size',0); num(stroke.get('opacity'),f'{key}.opacity',0,1)
    def events(raw, path):
        for i, ev in enumerate(arr(raw,path)):
            ev=obj(ev,f'{path}[{i}]'); kind=ev.get('type')
            if kind == 'message': ref(ev.get('sequenceId'),seqs,path)
            elif kind == 'activation':
                ref(ev.get('participantId'),nodes,path); boolean(ev.get('active'),path)
            elif kind == 'note':
                ref(ev.get('annotationId'),notes,path)
                for p in arr(ev.get('participantIds'),path): ref(p,nodes,path)
                enum(ev.get('position'),{'left of','right of','over'},path)
            elif kind == 'fragment':
                ref(ev.get('sectionId'),nodes,path)
                sid=ev.get('sectionId')
                if isinstance(sid,str) and nodes.get(sid,{}).get('type') != 'section': fail(path,'fragment must reference section')
                enum(ev.get('kind'),{'alt','opt','loop','par','critical','break','rect'},path)
                for branch in arr(ev.get('branches'),path):
                    branch=obj(branch,path); optional_enum(branch,'divider',{'else','and','option'},path); events(branch.get('events'),path+'.branch')
            else: fail(path,'unknown sequence event type')
    if 'sequenceDiagram' in ld:
        meta=obj(ld['sequenceDiagram'],'sequenceDiagram')
        if meta.get('version') != 1: fail('sequenceDiagram','version must be 1')
        events(meta.get('events'),'sequenceDiagram.events')
    return errors


def geometry_warnings(data):
    """Conservative box checks. Excludes intended ancestor containment."""
    if validate_diagram(data): return []
    nodes={n['id']:n for n in data['logicalData']['nodes']}
    visual=data['visualData']; layouts=visual['layoutNodes']; boxes={}; warnings=[]
    def box(key):
        if key in boxes: return boxes[key]
        v=layouts[key]; parent=nodes.get(key,{}).get('parentId')
        px,py=box(parent)[:2] if parent else (0,0)
        boxes[key]=(v['x']+px,v['y']+py,v.get('width',224),v.get('height',52))
        return boxes[key]
    def ancestors(key):
        result=set(); parent=nodes.get(key,{}).get('parentId')
        while parent:
            result.add(parent); parent=nodes[parent].get('parentId')
        return result
    for key in layouts:
        box(key); parent=nodes.get(key,{}).get('parentId')
        if parent:
            x,y,w,h=boxes[key]; px,py,pw,ph=box(parent)
            if x<px or y<py or x+w>px+pw or y+h>py+ph: warnings.append(f'{key}: extends outside section {parent}')
        name=nodes.get(key,{}).get('name','')
        if len(name)*7+56 > boxes[key][2] and layouts[key].get('displayMode') != 'icon-only': warnings.append(f'{key}: long label; inspect actual text width')
    ids=list(boxes)
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            if a in ancestors(b) or b in ancestors(a): continue
            ax,ay,aw,ah=boxes[a]; bx,by,bw,bh=boxes[b]
            if min(ax+aw,bx+bw)>max(ax,bx) and min(ay+ah,by+bh)>max(ay,by): warnings.append(f'{a}, {b}: overlapping bounds; inspect intent')
    for s in data['logicalData']['sequences']:
        edge=next(e for e in data['logicalData']['edges'] if e['id']==s['edgeId'])
        if s['isAsync'] != edge['isAsync']: warnings.append(f"{s['id']}: sequence/edge async semantics differ; review intent")
    return warnings


def load_components(folder, data):
    """Return template JSON and actionable errors; retain unused supplied templates."""
    result={}; errors=[]
    if folder:
        folder=Path(folder)
        if not folder.is_dir(): return {},[f'components directory not found: {folder}']
        for path in sorted(folder.glob('*.json')):
            try:
                template=json.loads(path.read_text(encoding='utf-8'))
                if not isinstance(template,dict): raise ValueError('template must be object')
                if template.get('componentId') != path.stem or not path.stem.startswith('custom-comp-'): raise ValueError('componentId must match custom-comp-* filename')
                for field in ('name','category','createdAt'):
                    if not isinstance(template.get(field),str) or not template[field]: raise ValueError(f'{field} required')
                dims=template.get('dimensions',{})
                if not isinstance(dims,dict) or any(not number(dims.get(k)) or dims[k]<=0 for k in ('width','height')): raise ValueError('positive dimensions required')
                layers=template.get('layers')
                if not isinstance(layers,list): raise ValueError('layers array required')
                ids=set()
                for layer in layers:
                    if not isinstance(layer,dict) or not isinstance(layer.get('id'),str) or layer['id'] in ids: raise ValueError('unique layer IDs required')
                    ids.add(layer['id'])
                    if layer.get('type') not in {'rectangle','circle','text','image','triangle','star','polygon','line'}: raise ValueError('unknown layer type')
                    if any(not number(layer.get(k)) for k in ('x','y','width','height','zIndex')): raise ValueError('layer geometry required')
                    if not isinstance(layer.get('style'),dict): raise ValueError('layer style required')
                result[path.stem]=template
            except (OSError,ValueError) as exc: errors.append(f'{path.name}: {exc}')
    if isinstance(data,dict) and isinstance(data.get('logicalData'),dict):
        for n in data['logicalData'].get('nodes',[]):
            if isinstance(n,dict) and isinstance(n.get('type'),str) and n['type'].startswith('custom-comp-') and n['type'] not in result: errors.append(f"{n['id']}: missing component template {n['type']}")
    return result, errors
