# Edit, export and verify

## Edit existing projects

`python3 SKILL_DIR/scripts/unpack_dproj.py input.dproj edit-dir`

The destination must not already exist. All safe archive entries are preserved.
Read/edit only relevant JSON records. Repack with
`python3 SKILL_DIR/scripts/pack_dproj.py output.dproj edit-dir/workspace.json edit-dir/diagram.json --components-dir edit-dir/components --extras-dir edit-dir`
(omit components-dir when absent). Extras preserves non-core archive members.
Use a new output file; preserve IDs, unknown fields and untouched payloads.

## Export choices

| Deliverable | Path |
|---|---|
| Editable project | Bundled pack_dproj.py; default, works offline |
| Inline preview | Bundled build_share_url.py; standard nodes, no upload |
| PNG/SVG | YADA image exporter; inspect framing and labels |
| GIF/video | YADA animation exporter; codec/platform dependent |
| Standalone HTML player | YADA HTML exporter; verify renderer parity and assets |
| Mermaid | YADA exporter; inspect preserved sequence semantics |
| Cloud reference/PIN, embed, collaboration | YADA UI when explicitly requested; these are not offline exporter features |

Preview:
`python3 SKILL_DIR/scripts/build_share_url.py diagram.json --name "Orders" --output-md preview.md`
Optional `--base-url http://localhost:5173/` targets a running local YADA instance.
Link to preview.md without reading/printing the compressed payload. Anyone with
an inline URL can inspect its data. No credentials in diagrams. Above 32,000 URL
characters use `.dproj`; the command reports the limit, it does not export a fallback.
Custom-component previews require a viewer/library path and are rejected by this tool.

Strict validation is default. For legacy data explicitly add `--repair` to either
exporter. Repairs operate in memory and are reported; review changed coordinates
and annotations in YADA. Unsupported future schema versions are never downgraded.

## Quality gate

1. Run check_diagram; fix errors and review warnings. Use `--report report.json`
   for full machine-readable findings; default output is capped. Missing timeline
   data in imported documents is an error here even if YADA supplies defaults.
2. Open the resulting project in the intended YADA version, or open a local preview.
   Wait for fonts/icons. Inspect fit-to-view and dense regions at readable scale:
   names, headers, notes, crossing/return paths, custom assets and clipping.
3. Play the scenario. Inspect meaningful moments listed in playback.md. For sequence
   metadata switch views and inspect branches/activations. Check scrub and final state.
4. Correct the source JSON, re-export and recheck affected areas. Verify requested
   image/video/HTML output separately; renderers may differ from the editor.
5. Deliver concise links, assumptions and validation status. Distinguish structural
   checks, geometry warnings, import, visual review and playback checks. If no YADA
   runtime is available, deliver the editable artifact with that explicit limitation.

No bundled Python tool renders YADA or certifies visual quality. Use a running app
when available, not a substitute drawing that merely resembles the document.
