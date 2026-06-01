# Analitics

This repository contains a Cursor skill and local MCP tools for preliminary
patent clearance research in the Russian Federation using open sources only.

## Patent clearance skill

- Skill: `.cursor/skills/patent-clearance-russia-open/SKILL.md`
- MCP config: `.cursor/mcp.json`
- MCP server: `tools/patent_clearance_open/server.py`

The workflow focuses on:

- RU official sources: FIPS search, FIPS open registers, Rospatent search
  platform.
- EA official source: EAPO Eurasian patent register.
- Open discovery sources: Espacenet, WIPO PATENTSCOPE, Google Patents, The
  Lens.

The tools generate search plans, open-source links, report scaffolds, and
preliminary risk registers. They do not provide legal advice or replace review
by a patent professional.

## Tests

```bash
python3 -m unittest
```
