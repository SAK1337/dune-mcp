# Change: Add MCP Prompts for SQL Generation and Result Analysis

## Why
Writing valid DuneSQL requires specific knowledge of Trino dialect, table naming conventions, and bytea array syntax. MCP Prompts provide reusable templates that guide the LLM's behavior, reducing SQL errors and improving result interpretation.

## What Changes
- Add `generate_dune_sql` prompt for constructing valid DuneSQL queries
- Add `analyze_result` prompt for interpreting query output
- Include dialect instructions, bytearray syntax, date handling, and table naming conventions

## Impact
- Affected specs: mcp-prompts (new capability)
- Affected code: server.py (add prompt definitions)
- Dependencies: Requires core-server capability (proposal 1)
- **Benefit**: Significantly reduces SQL syntax errors from LLM-generated queries
