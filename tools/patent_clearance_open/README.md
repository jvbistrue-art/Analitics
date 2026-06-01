# Patent clearance open-source MCP tools

This directory contains a small dependency-free MCP server for preliminary
patent clearance / freedom-to-operate research in the Russian Federation.

The tools use only open sources and do not call paid patent databases or
authenticated APIs.

## Tools

- `validate_open_sources_policy` - checks whether a proposed source list
  includes blocked paid/closed databases.
- `build_official_patent_number_links` - generates direct FIPS lookup links for
  known RU patent/application numbers, avoiding misses from unindexed fresh documents.
- `build_parallel_open_search_workflow` - creates one parallel workflow with
  official FIPS/EAPO tasks and web-discovery tasks from the same inputs.
- `build_patent_clearance_search_plan` - creates a Russia-focused search plan,
  source links, suggested queries, and a report outline.
- `evaluate_patent_clearance_candidates` - turns manually collected candidate
  patent/application records into a preliminary risk register.
- `generate_open_fto_report` - combines the search plan and candidate evaluation
  into a markdown report scaffold.

## Run locally

```bash
python3 tools/patent_clearance_open/server.py
```

The server speaks MCP JSON-RPC over stdio and is registered in
`.cursor/mcp.json`.

## Important limitation

These tools do not produce a legal opinion. For a defensible patent clearance
conclusion, verify legal status in official FIPS/EAPO registers and have claim
charts reviewed by a qualified patent professional.
