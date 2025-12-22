# Design: Core MCP Server Infrastructure

## Context
This is the foundational layer of mcp-server-dune. All subsequent tools, resources, and prompts depend on this infrastructure. The design prioritizes security (API key handling), async compatibility, and FastMCP best practices.

## Goals / Non-Goals
- Goals:
  - Establish FastMCP server with proper metadata
  - Secure API key management via environment variables
  - Async-first architecture for non-blocking operations
  - Clean separation between server initialization and client factory
- Non-Goals:
  - Implementing any tools, resources, or prompts (subsequent proposals)
  - Supporting multiple API keys or multi-tenant scenarios
  - Remote SSE transport (can be added later)

## Decisions

### Decision: Use FastMCP v2.0+ decorator-based API
- Rationale: Reduces boilerplate, provides automatic JSON Schema generation from type hints, integrates with Pydantic
- Alternatives: Low-level mcp SDK (rejected - more verbose, less type safety)

### Decision: Single get_dune() factory function
- Rationale: Centralizes client creation, makes API key validation explicit, enables future connection pooling
- Pattern: Factory pattern with environment variable injection

### Decision: Environment variable for API key
- Rationale: Never hardcode secrets, follows 12-factor app principles
- Variable: DUNE_API_KEY
- Behavior: Raise ValueError with clear message if missing

## Risks / Trade-offs
- Risk: API key exposure in logs → Mitigation: Never log the key value
- Risk: Missing key at runtime → Mitigation: Fail fast with descriptive error
- Trade-off: Single client instance vs connection pool → Start simple, optimize later

## Project Structure
```
mcp-server-dune/
├── pyproject.toml
├── fastmcp.json
└── src/
    └── mcp_server_dune/
        ├── __init__.py
        ├── __main__.py
        └── server.py
```

## Open Questions
- None for this phase
