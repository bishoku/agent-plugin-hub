#!/usr/bin/env python3
"""Look up capabilities without loading the whole registry into context."""
import argparse
from diagram_validation import CAPABILITIES
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--types',action='store_true'); p.add_argument('--icon'); a=p.parse_args()
if a.types: print(', '.join(CAPABILITIES['nodeTypes']))
if a.icon is not None:
    matches=[i for i in CAPABILITIES['productIcons'] if a.icon.lower() in i.lower()]
    print(', '.join(matches[:30]) or 'No matching icon; use the node type icon.')
    if len(matches)>30: print(f'{len(matches)-30} more; narrow the search.')
if not a.types and a.icon is None: p.print_help()
