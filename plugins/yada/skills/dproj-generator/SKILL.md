---
name: dproj-generator
description: Generate or edit YADA architecture diagrams as .dproj project files or shareable simulation URLs. Use for YADA diagrams, distributed system flows, SAGA, CQRS, event sourcing, or microservice visualizations intended for YADA.
---

# YADA diagram generator

Turn an architecture description into an editable YADA diagram with flow playback.
Use Python 3.10 or newer; bundled scripts require only the standard library.
Resolve paths relative to this skill's installed directory. Write results to the
user's workspace, never into the installed plugin.

## Workflow

1. Identify components, domain boundaries, protocols, and the ordered/parallel flow.
   Preserve supplied names and distinguish architectural assumptions from facts.
2. Read [the format and layout reference](references/diagram-format.md) before
   authoring JSON. Use [the example diagram](assets/example-diagram.json) and
   [workspace](assets/example-workspace.json) as working examples when useful.
3. Build `diagram.json` with schema version 2, `logicalData`, and `visualData`.
   Use stable IDs when editing. Keep existing content outside the requested change.
4. Choose a project file by default. Honor an explicit preview URL request, or
   produce both if requested. A preview contains the diagram in its URL; anyone
   receiving the URL can inspect its content. Do not add credentials to diagrams.
5. Run the selected exporter below, review any repair messages, and correct
   validation failures. The scripts apply legacy repairs in memory; input JSON
   remains unchanged. Repairs do not replace a layout review.
6. Return a link to the generated artifact, describe the flow and assumptions,
   and explain how to open it. Claim visual verification only if actually done.

## Export a project

Create `workspace.json` with a name, description, virtual path, and ISO timestamp.
Run (replace `SKILL_DIR` and file paths with actual paths):

```sh
python3 SKILL_DIR/scripts/pack_dproj.py output.dproj workspace.json diagram.json
```

Open the file with YADA's project import. A `.dproj` is a ZIP containing
`workspace.json` and `diagram.json`; it is not a standalone rendered image.

## Export a preview

```sh
python3 SKILL_DIR/scripts/build_share_url.py diagram.json \
  --name "Order Processing" --description "Order flow with Kafka events" \
  --output-md preview.md
```

The script writes a clickable YADA link into `preview.md`. Link to that file;
avoid reading or echoing the compressed URL into the conversation. No upload or
MCP server is required to generate it. Opening it loads the hosted YADA app.
If the URL exceeds 32,000 characters, export a `.dproj` instead and explain why.

## Final checks

- Every logical node/edge has matching visual data; sequence references exist.
- Annotations have layout entries and never occur as logical nodes.
- Children use parent-relative coordinates; section bounds include padding.
- Step delays are local, not accumulated; parallel steps share a step number.
- Match handles to layout direction and particles to protocols.
- Use readable spacing and role-based themes, with icons for known technology.

The optional YADA architect agent uses this same workflow. This skill does not
require a particular assistant, the Diagramer source checkout, or an API key.
