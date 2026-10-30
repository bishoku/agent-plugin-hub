# Schema v2 authoring contract

Reviewed against the source revision in `assets/capabilities.json`. Runtime source
and registries take precedence over older embedded AI prompts. Hosted YADA may lag
local source; test advanced features in the intended viewer before delivery.

`.dproj` is ZIP: `workspace.json`, `diagram.json`, optional `components/<id>.json`.
Workspace minimum: `{ "name":"Orders", "description":"Checkout flow",
"path":"virtual://workspace/imported", "lastModified":"2026-10-30T00:00:00Z" }`.
Preserve additional metadata on edits; use the actual creation timestamp.

Diagram: `{ "schemaVersion":2, "logicalData":{ "schemaVersion":2,
"nodes":[], "edges":[], "sequences":[] }, "visualData":{ "canvas":{
"zoom":1,"pan":{"x":0,"y":0},"gridVisible":false}, "layoutNodes":{},
"layoutEdges":{}, "timelines":{} } }`.

## Logical layer

- Node: `{id,type,name,parentId?,properties?}`. Built-in types:
  `client`, `cdn`, `firewall`, `load_balancer`, `gateway`, `auth`, `server`,
  `worker`, `database`, `cache`, `storage`, `search`, `queue`, `event_bus`,
  `external_api`, `llm`, `ai_agent`, `freeform`, `section`.
  `custom-comp-*` requires a packaged template. `sticky_note` is NOT a logical node.
  Imported `service` is accepted for compatibility; author new services as `server`.
- Edge: `{id,sourceId,targetId,isAsync,protocol?,description?,properties?}`.
  Endpoints are component nodes, never sections or annotations. Keep names precise:
  e.g. `POST /orders`, `OrderCreated`, `SELECT inventory`. Properties preserve
  technical detail without making every label long.
- Sequence: `{id,stepNumber,edgeId,isAsync,isRoundTrip?}`. One edge can appear in
  multiple sequences. See playback reference before designing timing.
- Optional `sequenceDiagram`: see sequence reference. No coordinates in logical data.

## Visual layer

Records are keyed by their object's ID. Do not leave orphan visual/timeline entries.

| Record | Fields |
|---|---|
| `layoutNodes[id]` | `id,x,y,width?,height?,theme?,handles?,zIndex?,displayMode?,rotation?,customStyles?,freeformContent?` |
| `layoutEdges[id]` | `id,sourceHandle?,targetHandle?,particleType?,showArrow?,color?,connectionType?,strokeWidth?,lineStyle?,arrowStart?,arrowEnd?,gradientColor?,labelPosition?,glowIntensity?,waypoints?` |
| `timelines[sequenceId]` | `sequenceId,duration,delay,animationMode?,repeatParticleCount?,internalProcess?:{text,duration}` |
| `annotations[id]` | `id,header,body,style,startTime,endTime,alwaysVisible?` plus a matching `layoutNodes[id]` |

Node defaults are 224×52; give sections explicit dimensions. `displayMode` is
`default` or `icon-only`. Canvas `renderStyle`: `clean` or `sketchy`.

Themes: `indigo,emerald,amber,rose,violet,cyan,slate,white` or a custom hex color.
`customStyles`: `backgroundColor,bgOpacity,borderColor,borderStyle,borderRadius,
borderOnly,iconColor,productIcon,productIconColored,productIconWordmark,
iconLabelPosition,sectionTitleMode,sectionTitleEdge,sectionTitleAlign,
headerBgColor,headerBgImage`.
- Node borderStyle: `solid|dashed|dotted`; bgOpacity: 0–1.
- iconLabelPosition: `none|top|bottom|left|right`.
- Section title: mode `inline|header|none`, edge `top|right|bottom|left`,
  alignment `left|center|right`. Reserve space for the chosen header edge.
- Look up icons with `scripts/catalog.py --icon <term>`; don't assume brand IDs.

Edge enums:
- connectionType: `bezier|smoothstep|step|straight`.
- lineStyle: `solid|dashed|dotted|longDash|dashDot`.
- arrowStart/arrowEnd: `none|triangle|open|diamond|circle`.
- glowIntensity: `none|subtle|strong|neon`; labelPosition: 0–100 along the path.
- particleType: `dot|arrow|envelope|rest|grpc|ws|graphql|kafka|pkg|sql`.

## Coordinates and ports

Each child is relative to its immediate parent section. Compute absolute position
by summing all ancestor positions; never subtract only the root for a nested child.
Size sections bottom-up, including header space and padding. Put parents before
children in arrays for portability. The app derives section depth/z-order.

Default ports: `top:50,right:50,bottom:50,left:50`. Custom ports are declared in
`handles:[{id:"right:25",side:"right",offset:25}]`; a nonempty handles array replaces
the defaults, so include all ports used. Match source/target ports to geometry.
Waypoints `{x,y}` are absolute canvas coordinates even for nested components.

## Notes

Example annotation (layout stored separately):
```json
{"id":"note-context","header":"Consistency","body":"Events are eventually consistent.",
 "style":{"backgroundColor":"#0f172a","borderColor":"#6366f1","textColor":"#e2e8f0",
 "fontFamily":"Inter","fontSize":14,"borderRadius":8,"opacity":1},
 "startTime":0,"endTime":8000,"alwaysVisible":true}
```
Use timed notes to explain individual phases; use always-visible notes for the
legend, scope and assumptions. Keep notes outside traffic corridors.
