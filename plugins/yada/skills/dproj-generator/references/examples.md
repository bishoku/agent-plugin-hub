# Select one example

Read only the example relevant to the task. These are teaching fixtures, not
production architecture claims. Workspace metadata can use `assets/example-workspace.json`.

| File under assets/examples/ | Demonstrates |
|---|---|
| request-cache.json | Nested synchronous calls and a cache-miss write |
| event-fanout.json | Async publish, delayed parallel consumers |
| saga-compensation.json | Failed payment and compensating reservation release |
| nested-platform.json | Two-level parent-relative sections and routed identity lookup |
| agent-rag.json | Provider-neutral retrieval before generation |
| sequence-alternatives.json | Sequence metadata and alternative branches |
| custom-device.json | Template packaged from examples/components/ |

Validate with check_diagram.py; pass `--components-dir assets/examples/components`
for custom-device. The legacy assets/example-diagram.json remains for compatibility.
