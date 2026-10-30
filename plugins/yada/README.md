# YADA

Version 1.1.0. Create editable architecture diagrams, sequence views and animated
flows with the portable `dproj-generator` skill and optional Copilot YADA architect.
Python 3.10+; no API key, MCP server, third-party Python runtime package or Diagramer
checkout is required. Install using the [hub guide](../../README.md).

## Authoring

The skill selects relevant references instead of loading a monolithic manual.
It covers current node types, nested sections, advanced connections, timing,
sequence metadata, custom components and drawing overlays. Use features that serve
the diagram's purpose. Product source baseline is recorded in the bundled
`assets/capabilities.json`; the hosted viewer may be on a different revision.

> Create a YADA project for a RAG agent with vector search and an LLM. Explain
> assumptions and show retrieval before generation.

> Show a SAGA compensation flow with clear return paths and readable annotations.

> Update this .dproj to add a cache lookup, preserving IDs, custom components and
> unrelated content. Report structural and visual verification separately.

## Tools

Inside `skills/dproj-generator/scripts/`:

| Tool | Purpose |
|---|---|
| `catalog.py --types` / `--icon postgres` | Small capability lookup |
| `check_diagram.py diagram.json --report report.json` | Structural checks and geometry warnings; bounded console output |
| `pack_dproj.py out.dproj workspace.json diagram.json` | Strict project packaging |
| `unpack_dproj.py input.dproj new-directory` | Preserve archive contents for editing |
| `build_share_url.py diagram.json --name Orders --output-md preview.md` | Offline inline preview URL; optional `--base-url` |

For custom templates add `--components-dir components` to check/pack. To retain
non-core members from an unpacked project add `--extras-dir new-directory` when
packing. Legacy repairs now require explicit `--repair`; new output is validated
without silently changing coordinates. Inputs remain unchanged.

## Quality and examples

The examples under `assets/examples/` cover request/cache, asynchronous fan-out,
compensation, nested boundaries, RAG, sequence alternatives and a custom component.
See [the example index](skills/dproj-generator/references/examples.md) for selection.

Validation checks authoring invariants, not every possible YADA field or visual
result. Geometry warnings identify box overlap/overflow and likely long labels;
they do not model actual edge paths or font metrics. Review rendering and playback
in YADA before claiming visual verification. Animation is explanatory, not measured
latency or executable conditional logic.

PNG/SVG, GIF/video, HTML, Mermaid, cloud/PIN links, embeds and collaboration use
YADA's existing UI; the Python tools do not implement those exporters or publish
anything. Inline preview links contain the diagram data and are limited to 32,000
characters. Custom components require `.dproj` because inline preview does not
load their library. Do not put credentials in diagrams.

## Maintenance

Run the repository tests and `scripts/validate.py`. Developers with the product
checkout can run `python3 scripts/check_yada_upstream.py /path/to/diagramer` to flag
source drift for review. `node scripts/check_yada_playback.cjs /path/to/diagramer`
checks the examples against the actual product scheduler (requires its installed
TypeScript development dependency). `node scripts/check_yada_import.cjs /path/to/diagramer` checks real product import
with in-memory storage, including custom templates. These are not user runtime
dependencies. Update baseline
hashes only after reviewing affected schema, rendering and playback behavior.

See [NOTICE.md](NOTICE.md) for provenance and licenses.
