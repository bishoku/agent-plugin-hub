# Visual composition

Choose a profile, then apply it consistently:

| Profile | Composition | Detail |
|---|---|---|
| Architecture review | Clean, restrained colors, explicit boundaries | Responsibilities, protocols, trust/data boundaries |
| Presentation | Strong primary path, generous space, few callouts | One story per view; progressive timed explanations |
| Technical walkthrough | Overview plus focused flows/sequence | Payload/event names, failure paths, processing stages |

Start with the story, not coordinates. Establish entry, main processing, storage
and external systems. Use LR for pipelines, TB for layers, and a mixed layout for
service-owned stores. Place a shared broker centrally when it reduces crossings.
Keep overview and compensation/details separate when combining them obscures both.
Do not add infrastructure or error scenarios unsupported by the request without
identifying them as assumptions.

## Geometry

Use a consistent grid appropriate to actual card dimensions; 224×52 cards with
roughly 100–140 px horizontal clearance and 70–110 px vertical clearance are a
starting point, not universal minimums. Widen cards for long names. Reserve 40–60 px
inside sections, plus header clearance. Size inner sections first. Use roughly
aligned ranks and balanced whitespace rather than a very long single row.

Route edges through open corridors. Fan-out needs separate exit ports or spaced
branches; return/compensation paths should use a different corridor. Prefer
`smoothstep` for orthogonal architecture paths, `bezier` for a few organic links,
and `straight` for unobstructed short connections. Add explicit waypoints only
where automatic routing is inadequate. Recheck absolute waypoints after moving a
section. Place labels on clear segments using `labelPosition`; keep descriptions
short and move verbose detail to properties or notes.

## Visual hierarchy

Use one primary accent plus restrained role colors. A useful palette is indigo
for clients, emerald for entry, amber for compute, rose for stores, violet for
messaging, cyan for cache, slate for infrastructure. Consistency matters more than
using every color. Low-opacity section fills (about .05–.12) keep boundaries quiet.
Use color plus labels/dashes to distinguish errors; do not rely on red/green alone.
Use glow/gradient only for meaningful emphasis, not on all edges.

Technology icons are optional recognition aids. Use known technologies only;
retain readable labels for icon-only nodes. Do not mix wordmarks and normal icons
without checking size balance. Default to clean rendering for technical review;
choose sketchy when the user wants an informal workshop style.

## Review rubric

- Scope and principal flow are apparent at fit-to-view; labels remain readable
  at the intended presentation size. Split the diagram before shrinking excessively.
- No unintended card/note overlaps, clipped labels, header collisions or children
  outside sections. Ancestor containment is intentional, not an overlap defect.
- Connections avoid unrelated cards; shared endpoints and crossings remain traceable.
- Success/error/event paths have a consistent legend and arrow direction.
- Notes explain decisions, assumptions or failure behavior rather than repeat labels.
- Verify both the overview and dense areas in YADA. Geometry lint cannot see text
  metrics, actual curved paths, lazy-loaded icons or tooltip collisions.

Repair the largest readability issue first, then recheck affected neighbors.
A premium result is understandable at its intended size, not merely colorful.
