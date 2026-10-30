# Sequence view

The same logical nodes, edges and sequences support architecture and sequence
views. Use sequence view for call order and alternatives; architecture view for
boundaries and topology. A `.dproj` does not guarantee the viewer opens in sequence
mode; explain switching views. Do not confuse `currentView:"diagram"` (vs studio)
with `viewMode:"sequence"`.

`logicalData.sequenceDiagram` is optional:
```json
{"version":1,"title":"Checkout","autonumber":{"start":1,"increment":1},
 "events":[
  {"type":"message","sequenceId":"s-request"},
  {"type":"activation","participantId":"order","active":true},
  {"type":"fragment","sectionId":"f-result","kind":"alt","label":"Payment result",
   "branches":[
    {"label":"Accepted","events":[{"type":"message","sequenceId":"s-confirm"}]},
    {"label":"Declined","divider":"else","events":[{"type":"message","sequenceId":"s-reject"}]}
   ]},
  {"type":"activation","participantId":"order","active":false}
 ]}
```
Every reference must resolve: fragment sectionId to a logical section, message to
a sequence, activation to a participant node. Notes use
`{type:"note",annotationId,participantIds:[...],position:"left of|right of|over"}`
with a real visual annotation and matching layout.

Fragment kinds: `alt,opt,loop,par,critical,break,rect`; branch divider:
`else,and,option`. Branches contain recursive events. Keep activations balanced.
Metadata preserves the semantic story for import/export. The current live sequence
renderer orders slots from calculated schedules, not the metadata event array.
Do not claim conditions or loops are evaluated during playback.

When the input is Mermaid, prefer YADA's own Mermaid importer to preserve its
supported semantics; inspect both views afterward. For direct JSON authoring use
only documented metadata and preserve existing properties on edits. YADA also
exports Mermaid; use its exporter rather than reconstructing a second source of
truth manually. Do not promise lossless conversion of unsupported Mermaid syntax.

## Current renderer contract and limits

Set fragment section `properties:{fragmentType:"alt",sequenceIds:["s-confirm","s-reject"]}`
in addition to sequenceDiagram metadata. Otherwise the live view can show a generic
`ref` frame or infer a larger span from participant containment. Participant
`properties.mermaidOrder` controls left-to-right order; `mermaidActor` preserves
actor intent. Edge `properties.arrowType` preserves Mermaid arrow forms such as
`->>`, `-->>`, `-x`, `-)`; these are separate from architecture-view arrow styles.

The current live layout reads fragmentType, sequenceIds and arrowType, but does
not fully render the metadata event tree's branch dividers, note placement or
explicit activation events. Activity bars derive from playback. Preserve this
metadata for export, and explain the visual limitation instead of promising full
UML behavior. Use separate scenario diagrams when branch distinction is essential.

Mermaid and Tempo imports can contain `type:"service"`; the validator accepts this
product-generated type for preservation. For newly authored services use `server`.
Tempo/OTLP traces should use YADA's importer and retain supplied measurements;
do not turn explanatory animation durations into claimed trace timings.
