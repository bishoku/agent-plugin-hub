#!/usr/bin/env python3
"""Validate this hub's conventions and portable manifests without network access."""
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas/agent-plugins/1.0.0"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def frontmatter(path):
    parts = path.read_text(encoding="utf-8").split("---", 2)
    require(len(parts) == 3 and not parts[0].strip(), f"{path}: missing frontmatter")
    data = yaml.safe_load(parts[1])
    require(isinstance(data, dict), f"{path}: frontmatter must be an object")
    for key in ("name", "description"):
        require(isinstance(data.get(key), str) and data[key].strip(),
                f"{path}: missing {key}")
    return data


def validate(root=ROOT):
    manifests = {}
    for plugin in sorted((root / "plugins").iterdir()):
        if not plugin.is_dir():
            continue
        for path in [plugin, *plugin.rglob("*")]:
            require(path.resolve().is_relative_to(plugin.resolve()),
                    f"{path}: path escapes plugin")
            require(not path.is_symlink(), f"{path}: hub packages must not use symlinks")
        manifest = read_json(plugin / "plugin.json")
        Draft202012Validator(read_json(SCHEMAS / "plugin.schema.json")).validate(manifest)
        require(manifest["name"] == plugin.name, f"{plugin}: name differs from directory")
        require(re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?",
                             manifest.get("version", "")), f"{plugin}: expected release version")
        for file in ("README.md", "LICENSE"):
            require((plugin / file).is_file(), f"{plugin}: missing {file}")
        skills = list((plugin / "skills").glob("*/SKILL.md"))
        mcp = plugin / "mcp.json"
        require(skills or mcp.is_file(), f"{plugin}: no portable components")
        for skill in skills:
            data = frontmatter(skill)
            require(data["name"] == skill.parent.name, f"{skill}: name differs from directory")
            require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["name"]),
                    f"{skill}: invalid skill name")
        for agent in (plugin / "com.github.copilot/agents").glob("*.agent.md"):
            frontmatter(agent)
        if mcp.is_file():
            Draft202012Validator(read_json(SCHEMAS / "mcp.schema.json")).validate(read_json(mcp))
        manifests[plugin.name] = manifest
    require(manifests, "No plugins found")
    for location in (".agents/plugins/marketplace.json", ".github/plugin/marketplace.json"):
        catalog = read_json(root / location)
        require(catalog["name"] == "agent-plugin-hub", f"{location}: unexpected marketplace name")
        names = set()
        for entry in catalog["plugins"]:
            name = entry["name"]
            require(name not in names, f"{location}: duplicate {name}")
            names.add(name)
            require(name in manifests, f"{location}: unknown plugin {name}")
            source = entry["source"]
            if location.startswith(".agents"):
                require(source["source"] == "local", f"{location}: expected local source")
                path = source["path"]
                require(entry["policy"]["installation"] == "AVAILABLE",
                        f"{location}: plugins must be opt-in")
                require(entry["policy"]["authentication"] in ("ON_INSTALL", "ON_USE"),
                        f"{location}: authentication policy missing")
                require(bool(entry["category"]), f"{location}: category missing")
            else:
                path = source
                require(entry["version"] == manifests[name]["version"],
                        f"{location}: stale version for {name}")
            require(path == f"./plugins/{name}", f"{location}: invalid source path for {name}")
        require(names == set(manifests), f"{location}: missing plugin entries")
    return len(manifests)


if __name__ == "__main__":
    print(f"Validated {validate()} plugin(s), both catalogs, and bundled metadata.")
