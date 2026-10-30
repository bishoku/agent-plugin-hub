#!/usr/bin/env python3
"""Bounded diagnostics; full report stays on disk instead of in model context."""
import argparse
import json
from pathlib import Path
from diagram_validation import validate_diagram, geometry_warnings, load_components


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('diagram'); parser.add_argument('--components-dir'); parser.add_argument('--report')
    parser.add_argument('--limit',type=int,default=12)
    args=parser.parse_args()
    try:
        data=json.loads(Path(args.diagram).read_text(encoding='utf-8'))
        errors=validate_diagram(data)
        if not errors: errors += load_components(args.components_dir,data)[1]
        warnings=geometry_warnings(data) if not errors else []
    except (OSError, ValueError) as exc: errors=[str(exc)]; warnings=[]
    report={'errors':errors,'warnings':warnings,'visualVerified':False,'playbackVerified':False}
    if args.report:
        path=Path(args.report); path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(f'{len(errors)} errors, {len(warnings)} warnings. Visual/playback review not performed.')
    findings=[f'ERROR {e}' for e in errors]+[f'WARN {w}' for w in warnings]
    for finding in findings[:max(0,args.limit)]: print(finding)
    if len(findings)>max(0,args.limit): print('More findings omitted; use --report for full results.')
    return int(bool(errors))

if __name__=='__main__': raise SystemExit(main())
