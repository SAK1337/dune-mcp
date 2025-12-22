# mcp-server-dune

A Python-based Model Context Protocol (MCP) server for integrating AI agents with Dune Analytics blockchain data.

## Project Overview

This MCP server acts as middleware between AI agents (Claude Desktop, Cursor, autonomous Python agents) and the Dune Analytics API. It exposes Dune's capabilities as discrete, discoverable Tools, Resources, and Prompts following the MCP standard.

## Technology Stack

- **Framework**: FastMCP v2.0+ (decorator-based MCP server)
- **API Client**: dune-client v1.10.0+ (official Dune Analytics SDK)
- **Python**: 3.11+
- **Validation**: Pydantic for type safety and schema generation

## Configuration

- **Environment Variable**: `DUNE_API_KEY` (required, never hardcode)
- **Config File**: `fastmcp.json` for server configuration
- **Transport**: Stdio (local) or SSE (remote deployment)

## MCP Tools

### Execution Tools
- `run_query` - Execute saved query and wait for results (blocking)
- `run_sql` - Execute raw ad-hoc DuneSQL (Trino dialect)
- `submit_query` - Submit query and return execution_id immediately (non-blocking)
- `get_execution_status` - Check job state
- `get_execution_results` - Retrieve completed job data

### Query Management Tools
- `create_query` - Save new query to library
- `update_query` - Modify existing query
- `archive_query` - Move query to archive

## MCP Resources (dune:// scheme)

- `dune://query/{query_id}/latest` - Cached result (zero credits)
- `dune://query/{query_id}/sql` - Query SQL definition
- `dune://execution/{execution_id}/status` - Execution status

## MCP Prompts

- `generate_dune_sql` - Guide LLM for valid DuneSQL syntax
- `analyze_result` - Guide result interpretation

## Development Guidelines

### DuneSQL Conventions
- Uses Trino/Presto SQL dialect
- Ethereum addresses as bytearrays: use `0x...` literals
- Date handling: `NOW() - INTERVAL '7' DAY`
- Prefer decoded project tables over raw tables
- Always include `LIMIT` to prevent timeouts

### Async Patterns
- Use `asyncio.to_thread()` for synchronous SDK calls
- Support both blocking and non-blocking execution modes
- Default row limit: 50 (prevents context overflow)

### Error Handling
- Map Dune API errors to semantic agent feedback
- 400: SQL syntax errors
- 401: Auth failures
- 402: Insufficient credits
- 404: Query not found
- 429: Rate limit (include retry guidance)

### Security
- Never hardcode API keys
- Default queries to private (`is_private=true`)
- Support read-only deployment mode

## Implementation Phases

1. **Phase 1**: Core connectivity - `run_query`, `dune://latest` resource
2. **Phase 2**: Async & management - `submit_query`, CRUD tools
3. **Phase 3**: Expert features - `run_sql`, prompts, error mapping

<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->