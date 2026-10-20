# Agent Plugin Hub

A community-ready collection of plugins for AI coding assistants, targeting
[Agent Plugins 1.0.0](https://agent-plugins.org/specification).

Each plugin is an independent package. Install only what you need.

| Plugin | What it does | Requirements |
| --- | --- | --- |
| [YADA](plugins/yada/README.md) | Creates editable architecture diagrams and animated flow previews; includes a YADA architect agent | Python 3.10+; YADA to view results |

## Install and use

Clone [bishoku/agent-plugin-hub](https://github.com/bishoku/agent-plugin-hub),
then use one of the options below.

```sh
git clone https://github.com/bishoku/agent-plugin-hub.git
cd agent-plugin-hub
```

### Codex

Register your local checkout:

```sh
codex plugin marketplace add .
```

Or register the published repository:

```sh
codex plugin marketplace add bishoku/agent-plugin-hub
```

Open the desktop plugin directory, select **Agent Plugin Hub**, and install
**yada**. Start a new chat and ask:

> Use dproj-generator to create a YADA .dproj for an order service that stores
> orders in PostgreSQL and publishes OrderCreated events to Kafka.

Catalog registration and plugin installation are separate steps. Refresh a
registered repository with `codex plugin marketplace upgrade agent-plugin-hub`,
then check the installed plugin in the desktop app.
See [OpenAI's packaging guide](https://developers.openai.com/plugins/build/plugins).

### GitHub Copilot CLI

```sh
copilot plugin marketplace add bishoku/agent-plugin-hub
copilot plugin install yada@agent-plugin-hub
```

For local development, use `copilot plugin marketplace add .` first.
Select the `yada-architect` agent in a client that supports plugin agents, or ask
Copilot to use the `dproj-generator` skill.
See [Copilot's plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference).

### Other assistants

Point an Agent Plugins 1.0-capable client's local plugin installer at
`plugins/yada`. Installation commands and component support vary by client.
For assistants that support Agent Skills but lack plugin installation, copy the
**entire** `plugins/yada/skills/dproj-generator` directory into that assistant's
documented skill directory. Include scripts, references, assets, and licenses.

The portable skill supplies the diagram-generation behavior. The named agent
under `com.github.copilot/agents/` is a Copilot extension; other clients do not
automatically discover it. Claude Code legacy plugin packaging is not included.

## Try YADA without an assistant

From the repository root:

```sh
mkdir -p output
python3 plugins/yada/skills/dproj-generator/scripts/pack_dproj.py \
  output/order-processing.dproj \
  plugins/yada/skills/dproj-generator/assets/example-workspace.json \
  plugins/yada/skills/dproj-generator/assets/example-diagram.json

python3 plugins/yada/skills/dproj-generator/scripts/build_share_url.py \
  plugins/yada/skills/dproj-generator/assets/example-diagram.json \
  --name "Order Processing" --output-md output/preview.md
```

Import the `.dproj` into [YADA](https://bishoku.github.io/yada/), or open the link
inside `output/preview.md`. Exporters run locally without dependencies or an API
key. Preview links contain the diagram data; opening them loads the hosted app.

## Repository layout

```text
.agents/plugins/marketplace.json       Codex catalog
.github/plugin/marketplace.json        Copilot catalog
.github/workflows/validate.yml         Pull-request checks
plugins/
  yada/
    plugin.json                       Agent Plugins 1.0 manifest
    com.github.copilot/agents/         Optional client-specific agent
    skills/dproj-generator/            Portable skill and export tools
    README.md, LICENSE, NOTICE.md
schemas/agent-plugins/                 Vendored official validation schemas
scripts/validate.py                    Package and catalog checks
tests/                                Export regression checks
CONTRIBUTING.md                        Adding skills, agents, and MCP servers
```

The two catalogs reference the same packages. Agent Plugins 1.0 standardizes
skills and MCP configuration, while marketplaces and named agents are
client-specific. YADA needs no MCP server; future plugins can add a root
`mcp.json`. See [the specification](https://agent-plugins.org/specification).

## Validate and contribute

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for a new-plugin walkthrough and review
requirements. [Publishing](docs/publishing.md) explains how to release updates.

Validation checks package metadata, catalog consistency, and export behavior.
It does not certify every assistant or replace a real installation and YADA
import/playback check. Client integration instructions follow current official
documentation; end-to-end client installation remains a release check.

## License

Hub content is [MIT licensed](LICENSE). Retain each plugin's license and notices.
Vendored Agent Plugins schemas are Apache-2.0; the YADA preview compressor
includes MIT-licensed lz-string-derived code.
