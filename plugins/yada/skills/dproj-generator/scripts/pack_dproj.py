#!/usr/bin/env python3
"""Validate and pack YADA projects. Strict by default; --repair opts into legacy
handle, coordinate and annotation migration. Inputs are never modified."""

import sys
import json
import zipfile
import os

from diagram_validation import VALID_TYPES, validate_diagram, load_components
from pathlib import Path
import argparse

VALID_SIDES = {"top", "right", "bottom", "left"}
DEFAULT_HANDLES = [
    {"id": "top:50",    "side": "top",    "offset": 50},
    {"id": "right:50",  "side": "right",  "offset": 50},
    {"id": "bottom:50", "side": "bottom", "offset": 50},
    {"id": "left:50",   "side": "left",   "offset": 50},
]
DEFAULT_HANDLE_IDS = {h["id"] for h in DEFAULT_HANDLES}


def parse_handle_id(handle_id: str):
    parts = handle_id.split(":")
    if len(parts) != 2:
        return None
    side, raw_offset = parts
    if side not in VALID_SIDES:
        return None
    try:
        offset = int(raw_offset)
    except ValueError:
        return None
    if not (0 <= offset <= 100):
        return None
    return side, offset


# ─── Workspace validation ──────────────────────────────────────────────────────

def validate_workspace(data: dict) -> list:
    if not isinstance(data, dict): return ['workspace.json must be an object']
    return [f"workspace.json missing nonempty '{key}'" for key in ('name','path')
            if not isinstance(data.get(key),str) or not data[key].strip()]


# ─── Repair 1: Handle injection ────────────────────────────────────────────────

def repair_handles(data: dict) -> list:
    """
    Inject handle IDs referenced in layoutEdges that are missing from node
    handles arrays. Mutates data in place.
    """
    repairs = []
    ld = data.get("logicalData", {})
    vd = data.get("visualData", {})
    edges = ld.get("edges", [])
    layout_nodes = vd.get("layoutNodes", {})
    layout_edges = vd.get("layoutEdges", {})

    required: dict = {}
    for le in edges:
        ve = layout_edges.get(le.get("id", ""))
        if not ve:
            continue
        src = le.get("sourceId")
        tgt = le.get("targetId")
        if ve.get("sourceHandle") and src:
            required.setdefault(src, set()).add(ve["sourceHandle"])
        if ve.get("targetHandle") and tgt:
            required.setdefault(tgt, set()).add(ve["targetHandle"])

    for node_id, handle_ids in required.items():
        vn = layout_nodes.get(node_id)
        if not vn:
            continue

        existing = vn.get("handles")
        if existing and len(existing) > 0:
            existing_ids = {h["id"] for h in existing}
            current = list(existing)
        else:
            existing_ids = set(DEFAULT_HANDLE_IDS)
            current = [dict(h) for h in DEFAULT_HANDLES]

        changed = False
        for hid in sorted(handle_ids):
            if hid in existing_ids:
                continue
            parsed = parse_handle_id(hid)
            if not parsed:
                repairs.append(f"  ⚠  Node '{node_id}': cannot parse handle id '{hid}' — skipped")
                continue
            side, offset = parsed
            current.append({"id": hid, "side": side, "offset": offset})
            existing_ids.add(hid)
            changed = True
            repairs.append(f"  ✎  Node '{node_id}': injected missing handle '{hid}'")

        if changed:
            vn["handles"] = current

    return repairs


# ─── Repair 2: Section-relative coordinates ────────────────────────────────────

def repair_section_coordinates(data: dict) -> list:
    """
    Child nodes with parentId must use section-relative coordinates.
    Detects and converts absolute canvas coordinates to relative using a
    two-condition heuristic. Mutates data in place.
    """
    repairs = []
    ld = data.get("logicalData", {})
    vd = data.get("visualData", {})
    nodes = ld.get("nodes", [])
    layout_nodes = vd.get("layoutNodes", {})

    sections = {}
    for n in nodes:
        if n.get("type") == "section":
            vn = layout_nodes.get(n["id"])
            if vn:
                sections[n["id"]] = vn

    for n in nodes:
        parent_id = n.get("parentId")
        if not parent_id or parent_id not in sections:
            continue

        vn = layout_nodes.get(n["id"])
        if not vn:
            continue

        section = sections[parent_id]
        sx = section.get("x", 0)
        sy = section.get("y", 0)
        sw = section.get("width", 9999)
        sh = section.get("height", 9999)
        nx = vn.get("x", 0)
        ny = vn.get("y", 0)
        nw = vn.get("width", 224)
        nh = vn.get("height", 52)

        outside_as_relative = nx > sw or ny > sh or nx < -nw or ny < -nh
        rel_x = nx - sx
        rel_y = ny - sy
        inside_after_conversion = 0 <= rel_x < sw and 0 <= rel_y < sh

        if outside_as_relative and inside_after_conversion:
            vn["x"] = rel_x
            vn["y"] = rel_y
            repairs.append(
                f"  ✎  Node '{n['id']}': abs ({nx},{ny}) → relative ({rel_x},{rel_y})"
                f" within section '{parent_id}'"
            )

    return repairs


# ─── Repair 3: Schema V2 Cleanups (Sticky notes & Sequence animations) ─────────

def repair_schema_v2(data: dict) -> list:
    """
    Migrates diagram data to Schema V2:
      1. Purge sticky_note entries from logicalData.nodes (belong in visualData.annotations).
      2. Ensure layoutNodes entry exists for every annotation.
      3. Move animationMode / repeatParticleCount from SequenceStep to VisualDiagram.timelines.
      4. Bump schemaVersion to 2.
    """
    repairs = []
    ld = data.get("logicalData", {})
    vd = data.get("visualData", {})

    # 1. Clean sticky_note from logicalData.nodes
    nodes = ld.get("nodes", [])
    clean_nodes = [n for n in nodes if n.get("type") != "sticky_note" and not (n.get("properties") or {}).get("_visualOnly")]
    if len(clean_nodes) != len(nodes):
        ld["nodes"] = clean_nodes
        repairs.append(f"  ✎  Removed {len(nodes) - len(clean_nodes)} legacy sticky_note entries from logicalData.nodes")

    # 2. Ensure layoutNodes entry exists for every annotation
    annotations = vd.get("annotations", {})
    layout_nodes = vd.setdefault("layoutNodes", {})
    for note_id in annotations:
        if note_id not in layout_nodes:
            layout_nodes[note_id] = {
                "id": note_id,
                "x": 50,
                "y": 50,
                "width": 280,
                "height": 160
            }
            repairs.append(f"  ✎  Annotation '{note_id}': synthesised missing layoutNodes entry at (50, 50)")

    # 3. Move animation fields from sequences to timelines
    sequences = ld.get("sequences", [])
    timelines = vd.setdefault("timelines", {})
    for s in sequences:
        mode = s.pop("animationMode", None)
        count = s.pop("repeatParticleCount", None)
        if mode is not None or count is not None:
            seq_id = s.get("id")
            if seq_id:
                t = timelines.setdefault(seq_id, {"sequenceId": seq_id, "duration": 1000, "delay": 0})
                if mode is not None:
                    t["animationMode"] = mode
                if count is not None:
                    t["repeatParticleCount"] = count
                repairs.append(f"  ✎  Sequence '{seq_id}': moved animation parameters to timelines")

    # 4. Bump schemaVersion
    if data.get("schemaVersion") != 2:
        data["schemaVersion"] = 2
        ld["schemaVersion"] = 2
        repairs.append("  ✎  Bumped schemaVersion to 2")

    return repairs


# ─── Diagram validation ────────────────────────────────────────────────────────

def prepare_diagram(data, repair=False):
    """Explicit legacy migration. Never silently rewrite a future schema."""
    import copy
    data = copy.deepcopy(data)
    repairs = []
    if repair:
        if not isinstance(data, dict) or data.get('schemaVersion') not in (1, 2):
            return data, repairs, ['repair supports schemaVersion 1 or 2 only']
        try:
            repairs.extend(repair_section_coordinates(data))
            repairs.extend(repair_schema_v2(data))
            repairs.extend(repair_handles(data))
            if data.get('logicalData', {}).get('schemaVersion') != 2:
                data['logicalData']['schemaVersion'] = 2
                repairs.append('Set logicalData.schemaVersion to 2')
        except (AttributeError, TypeError, KeyError, ValueError) as exc:
            return data, repairs, [f'legacy data malformed: {exc}']
    return data, repairs, validate_diagram(data)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Validate and pack a YADA project (strict by default).')
    parser.add_argument('output')
    parser.add_argument('workspace')
    parser.add_argument('diagram')
    parser.add_argument('--components-dir')
    parser.add_argument('--extras-dir', help='Preserve non-core files from an unpacked project')
    parser.add_argument('--repair', action='store_true', help='Explicitly repair legacy data in memory')
    args = parser.parse_args()
    try:
        workspace = json.loads(Path(args.workspace).read_text(encoding='utf-8'))
        source = json.loads(Path(args.diagram).read_text(encoding='utf-8'))
        data, repairs, errors = prepare_diagram(source, args.repair)
        errors += validate_workspace(workspace)
        component_dir = args.components_dir
        if not component_dir and args.extras_dir and (Path(args.extras_dir)/'components').is_dir():
            component_dir = Path(args.extras_dir)/'components'
        components, comp_errors = load_components(component_dir, data) if not errors else ({}, [])
        errors += comp_errors
        if errors:
            print('Validation failed:\n' + '\n'.join(errors[:20]))
            if len(errors)>20: print(f'{len(errors)-20} more errors; use check_diagram.py --report')
            return 1
        output = Path(args.output)
        if output.suffix != '.dproj': output = Path(str(output)+'.dproj')
        if args.extras_dir and output.resolve().is_relative_to(Path(args.extras_dir).resolve()):
            raise ValueError('output must be outside extras directory')
        extras = {}
        if args.extras_dir:
            folder = Path(args.extras_dir)
            if not folder.is_dir(): raise ValueError('extras directory not found')
            for path in folder.rglob('*'):
                if path.is_symlink(): raise ValueError(f'symlink not allowed: {path}')
                if not path.is_file(): continue
                relative = path.relative_to(folder).as_posix()
                if relative in ('workspace.json','diagram.json') or relative in {f'components/{cid}.json' for cid in components}: continue
                if path.resolve() == Path(args.output).resolve(): raise ValueError('output must be outside extras directory')
                extras[relative] = path.read_bytes()
        if output.resolve() in (Path(args.workspace).resolve(),Path(args.diagram).resolve()): raise ValueError('output cannot replace input')
        output.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('workspace.json', json.dumps(workspace,indent=2,ensure_ascii=False))
            zf.writestr('diagram.json', json.dumps(data,indent=2,ensure_ascii=False))
            for cid, component in components.items(): zf.writestr(f'components/{cid}.json',json.dumps(component,indent=2,ensure_ascii=False))
            for name, content in extras.items(): zf.writestr(name,content)
        for message in repairs[:20]: print('Repair: '+message)
        print(f'Created {output.resolve()} ({len(components)} components, {len(extras)} extras). Structural validation passed; visual/playback review still required.')
        return 0
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
