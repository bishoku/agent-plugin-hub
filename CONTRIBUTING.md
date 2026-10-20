# Contributing

Contributions should deliver a focused, useful capability that another developer
can install without access to your machine. Keep all repository content in English.

## Add a plugin

1. Create `plugins/<name>/` using a stable lowercase kebab-case name.
2. Add a root `plugin.json`:

   ```json
   {
     "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
     "name": "your-plugin",
     "version": "1.0.0",
     "description": "Describe a concrete capability.",
     "license": "MIT"
   }
   ```

3. Add at least one useful skill under `skills/<skill-name>/SKILL.md`, with YAML
   `name` and `description`. Match the name to its directory. Include all runtime
   scripts and references within the plugin. Use YADA as a working example.
4. Include a README with prerequisites, installation, sample prompts, output,
   limitations, and verification steps. Include LICENSE and attribution for
   reused material.
5. Add an entry to both marketplace catalogs. Follow their existing shapes;
   point each source at `./plugins/<name>`. Keep the Copilot entry version equal
   to the package version.
6. Run the validation commands in the root README and exercise a realistic task
   in your intended assistant. Add behavior tests for executable functionality.
7. Submit a pull request with the capability, intended clients, test evidence,
   and any external services or authentication requirements.

## Add an agent

Agent Plugins 1.0 does not define a universal named-agent format. Keep reusable
instructions in a portable skill. For Copilot, add
`com.github.copilot/agents/<name>.agent.md` with `name` and `description` frontmatter
and point its instructions to the skill. Other client adapters need their own
documented namespace and tested discovery path. Do not add unsupported top-level
`agents` fields to a portable manifest.

## Add MCP tools

When a plugin needs a real MCP service, place `mcp.json` at its root:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "your-service": {
      "type": "streamable-http",
      "url": "https://YOUR-SERVICE.example/mcp"
    }
  }
}
```

This is a documentation example, not a usable endpoint. Replace it with a tested
service before submitting. Explain the service's owner, permissions, data sent,
authentication, and installation requirements. Never commit credentials.
For stdio servers, use the standard plugin variables for bundled paths, pin
dependencies, and test startup from outside your development checkout.
The repository validator checks either configuration against the vendored schema;
connection and tool behavior need separate tests.

## Maintenance rules

- Packages must be self-contained; no absolute developer paths or escaping links.
- Keep optional client features separate from portable components.
- Increment the plugin version for published changes and update both catalogs
  where a version is recorded. Use semantic versioning.
- Preserve upstream licenses and record modifications in plugin notices.
- Keep generated outputs, credentials, caches, and virtual environments out of Git.
- Review shell commands, dependencies, and network effects before distribution.
- Do not claim client compatibility that has not been verified.

For release steps, see [publishing](docs/publishing.md).
