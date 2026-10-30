# Advanced visuals

## Custom components

Use for meaningful domain-specific symbols when built-in types/icons are inadequate.
Logical type is the template's `componentId` (`custom-comp-*`). Package every used
template at `components/<componentId>.json`; pass `--components-dir` to pack/check.
Template shape:
```json
{"componentId":"custom-comp-device","name":"Device","category":"Domain",
 "dimensions":{"width":224,"height":80},"createdAt":"2026-10-30T00:00:00Z",
 "layers":[{"id":"body","type":"rectangle","name":"Body","zIndex":0,
 "x":0,"y":0,"width":224,"height":80,
 "style":{"fill":"#e0e7ff","stroke":"#6366f1","strokeWidth":2,"rx":12}}]}
```
Layer types: `rectangle,circle,text,image,triangle,star,polygon,line`.
Each layer has id/type/name/zIndex/x/y/width/height/style; optional locked/visible/content.
Styles include fill/stroke/strokeWidth/opacity/rx/rotation, text fontSize/fontFamily/
fontWeight/textAlign/letterSpacing, polygon sides, star points/innerRadius.
Optional `editDimensions` represents studio editing bounds. Use actual timestamps.
Keep fonts/assets portable and inspect rendering. The local preview-link tool
rejects custom components: its payload does not load their library. Use `.dproj`.

## Freeform and drawing overlays

`type:"freeform"` is a node with visual `freeformContent:{elements,appState?,files?,
svgCache?}`. This is Excalidraw data. Prefer creating it in YADA's editor or preserving
an existing export; do not invent an SVG cache inconsistent with the elements.
A valid JSON shape alone cannot prove an Excalidraw scene renders.

`visualData.freehandStrokes[id]` is independent of logical nodes:
`{id,tool,points:[{x,y,pressure?}],color,size,opacity,text?,fontSize?,fontFamily?,
roughness?,fill?,fillStyle?,x?,y?,width?,height?,startTime?,endTime?,alwaysVisible?}`.
Tools: `select,rectangle,ellipse,diamond,line,arrow,pen,highlighter,text,eraser`.
FillStyle: `solid,hachure,none`. Prefer shape/text/highlighter overlays for purposeful
emphasis; drawing tools such as select/eraser are not useful authored marks.
Timed overlays should match actual playback. Avoid enormous point arrays or base64
in model context; work with files and preserve existing content.

Canvas `renderStyle:"sketchy"` changes presentation, not architecture semantics.
Image headers (`headerBgImage`) and custom image layers require asset availability
in the target viewer. Check portable export and light/dark appearance before use.
