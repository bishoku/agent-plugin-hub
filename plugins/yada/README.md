# YADA

Version 1.0.0. Generate editable [YADA](https://bishoku.github.io/yada/) architecture
diagrams from a description of a system, pattern, or interaction.

## Components

- `skills/dproj-generator`: portable generation instructions, visual/schema
  reference, working JSON example, and Python exporters.
- `com.github.copilot/agents/yada-architect.agent.md`: a specialized Copilot agent
  that uses the same skill.

Install through the hub's catalog as described in the [hub guide](../../README.md).
Python 3.10+ is required for exporting; no API key, MCP server, Diagramer checkout,
or third-party Python package is needed.

## Example requests

> Use dproj-generator to create an editable YADA project for a checkout flow with
> an API gateway, order service, PostgreSQL, Redis, Kafka, and payment service.

> Create a YADA preview URL for a SAGA compensation flow. Show which messages are
> asynchronous and annotate the failure path.

> Update this .dproj to add a cache lookup before the database query. Preserve the
> existing component IDs and explain your assumptions.

The default output is a `.dproj` archive. Import it through YADA's project import.
When requested, the exporter creates a Markdown file containing a preview link.
Large previews fall back to a project file. Simulation depicts message flow, not
measured latency, throughput, or the correctness of a deployed system.

The exporters retain upstream legacy repairs for handles, section coordinates,
and schema-v2 annotations. Review their repair messages. Validation covers
structural relationships but is not a complete YADA schema validator; inspect
layout and playback in YADA before sharing a final diagram.

See [NOTICE.md](NOTICE.md) for the Diagramer source and third-party attribution.
