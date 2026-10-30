# Provenance

Adapted from Diagramer's `.agents/skills/dproj-generator` skill and its two Python
export scripts, supplied by the repository owner on 2026-10-20. Upstream source:
https://github.com/bishoku/diagramer (MIT; see LICENSE).

The hub reorganizes the instructions, provides a complete example and a Copilot
agent, and fixes UTF-16 handling in preview compression. The embedded compression
implementation derives from lz-string 1.5.0 by pieroxy. Its MIT license is retained
in `skills/dproj-generator/LICENSE.lz-string`.

Version 1.1.0 adds source-reviewed capability snapshots, authoring references and
validation/editing tools. The baseline revision and file hashes are recorded in
`skills/dproj-generator/assets/capabilities.json`.
