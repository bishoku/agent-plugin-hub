#!/usr/bin/env python3
"""Developer-only drift check. A change requests review, not an automatic overwrite."""
import argparse
import hashlib
import json
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('source',type=Path,help='Diagramer checkout'); a=p.parse_args()
root=Path(__file__).resolve().parents[1]
c=json.loads((root/'plugins/yada/skills/dproj-generator/assets/capabilities.json').read_text())
changed=[]
for file, expected in c['sourceHashes'].items():
    path=a.source/file
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected: changed.append(file)
print(f"Baseline {c['sourceRevision'][:8]}: {len(changed)} source files need compatibility review.")
for file in changed: print(file)
raise SystemExit(bool(changed))
