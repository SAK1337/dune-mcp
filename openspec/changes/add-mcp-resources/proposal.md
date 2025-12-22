# Change: Add MCP Resources with dune:// URI Scheme

## Why
MCP Resources provide passive, read-only data access that is semantically distinct from tool execution. Exposing cached query results as resources enables zero-credit data access and allows agents to "watch" execution states without repeated tool calls.

## What Changes
- Register custom `dune://` URI scheme handler
- Add `dune://query/{query_id}/latest` resource for cached results (zero credits)
- Add `dune://query/{query_id}/sql` resource for query SQL definition
- Add `dune://execution/{execution_id}/status` resource for execution state

## Impact
- Affected specs: mcp-resources (new capability)
- Affected code: server.py (add resource definitions)
- Dependencies: Requires core-server capability (proposal 1)
- **Benefit**: Cached result access consumes no execution credits
