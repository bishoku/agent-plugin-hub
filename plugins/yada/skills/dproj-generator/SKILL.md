---
name: dproj-generator
description: Create or edit YADA architecture and sequence diagrams, animated flows, .dproj projects, and preview links.
---

# YADA diagram authoring

Produce editable, readable diagrams with faithful flow playback. Use the user's
language and terminology. Python 3.10+; bundled tools use only the standard library.
Resolve tool paths from this installed skill; write outputs to the user's workspace.

## Workflow

1. Establish the audience, system boundaries and scenario from the request. Separate
   supplied facts from assumptions; do not invent technology just to add an icon.
   Choose overview, detailed flow, or sequence; split crowded scenarios when useful.
2. For new diagrams read [format](references/diagram-format.md) and
   [design](references/visual-design.md). For narrow edits read only the relevant
   section and preserve IDs, unknown fields, components and unrelated content.
3. Build both logical and visual layers. For a starting point select one
   [example](references/examples.md), not the whole collection. Load conditional guidance only as needed:

   | Need | Reference |
   |---|---|
   | Animated calls, events, parallelism, compensation | [Playback](references/playback.md) |
   | Sequence view, conditions, loops, activations | [Sequence](references/sequence.md) |
   | Custom components, freeform, drawing overlays | [Advanced visuals](references/advanced-visuals.md) |
   | Import/edit, export, preview, visual QA | [Delivery](references/delivery.md) |

4. Run `python3 SKILL_DIR/scripts/check_diagram.py diagram.json` (add
   `--components-dir components` for custom components). Fix errors; review layout
   warnings. This checks data and geometry, not actual rendering or playback.
5. Export by default:
   `python3 SKILL_DIR/scripts/pack_dproj.py output.dproj workspace.json diagram.json`.
   Add `--components-dir components` when used. New output is strict; `--repair`
   is an explicit legacy migration option, not a substitute for fixing authorship.
6. Inspect in YADA when available, following delivery's QA procedure. Return the
   artifact, a brief flow/assumption summary and what was actually verified.
   If rendering is unavailable, state that limitation; never claim visual QA.

## Context economy

- Read a reference once, only when relevant. Do not load the whole catalog or all
  examples. `scripts/catalog.py --icon postgres` finds icon IDs; `--types` lists types.
- Execute helpers without reading their source unless diagnosing a failure.
- Build repeated structures with local loops/shared style dictionaries. Serialize
  complete JSON to disk; do not echo it, SVG caches, base64 or compressed URLs.
- For edits use `scripts/unpack_dproj.py input.dproj edit-dir`, then modify only
  affected records. Do not regenerate unchanged diagrams to make a small edit.
- Tool summaries are bounded; use `check_diagram.py --report report.json` for full
  findings. Inspect only failing IDs. Keep artifact internals out of the response.

## Invariants

Annotations are visual-only; edges cannot terminate on sections or notes. Child
positions are parent-relative; edge waypoints are canvas coordinates. Each sequence
has its own timeline. Async steps do not automatically wait for event delivery.
Use features that clarify the scenario; completeness does not mean decoration.
A simulation illustrates behavior, not measured performance or executable logic.
