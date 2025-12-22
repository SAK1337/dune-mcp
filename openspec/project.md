# Project Context

## Purpose
mcp-server-dune is a Python-based Model Context Protocol (MCP) server that bridges AI agents with Dune Analytics blockchain data. It enables MCP-compliant clients (Claude Desktop, Cursor, autonomous Python agents) to natively query, analyze, and manage Dune Analytics data through a standardized interface.

The server exposes Dune's capabilities as discrete, discoverable Tools, Resources, and Prompts, eliminating the need for custom integration code for each agent implementation.

## Tech Stack
- **Language**: Python 3.11+
- **MCP Framework**: FastMCP v2.0+ (high-level decorator-based API)
- **API Client**: dune-client v1.10.0+ (official Dune Analytics SDK)
- **Validation**: Pydantic (type safety and JSON Schema generation)
- **Async**: asyncio with aiohttp for non-blocking HTTP

## Project Conventions

### Code Style
- Use Python type hints for all function parameters and returns
- Leverage Pydantic `Field()` for parameter descriptions and defaults
- Use `async def` for all tool functions (async-first design)
- Wrap synchronous SDK calls with `asyncio.to_thread()`
- Default row limits to 50 to prevent context overflow

### Architecture Patterns
- **Middleware Pattern**: Server translates high-level intent to Dune API calls
- **Dual-Mode Execution**:
  - Blocking mode for quick queries (<1 min)
  - Non-blocking mode with execution_id handoff for long-running queries
- **Stateless Translation Layer**: Server handles protocol translation, host manages state
- **Factory Pattern**: `get_dune()` helper for client instantiation

### Testing Strategy
- Test tool functions with mock DuneClient responses
- Verify error mapping produces semantic agent feedback
- Test async execution patterns and timeout handling
- Validate Pydantic schema generation for MCP compliance

### Git Workflow
- Main branch for stable releases
- Feature branches for new tools/resources
- Phased implementation following the roadmap

## Domain Context

### Dune Analytics
- Industry-standard blockchain analytics platform
- SQL-based querying of on-chain data
- Uses DuneSQL (Trino/Presto dialect)
- Credit-based execution metering
- Asynchronous job execution model

### DuneSQL Specifics
- Ethereum addresses are bytearrays: use `0x...` literals directly
- Date intervals: `NOW() - INTERVAL '7' DAY`
- Prefer decoded project tables (e.g., `uniswap_v3_ethereum.Factory_evt_PoolCreated`)
- Always include `LIMIT` clause to prevent timeouts
- Execution can take seconds to 30 minutes depending on complexity

### MCP Protocol
- Tools: Executable functions (run_query, create_query, etc.)
- Resources: Read-only data via URI scheme (dune://query/{id}/latest)
- Prompts: Reusable templates for LLM guidance

## Important Constraints

### Security
- `DUNE_API_KEY` via environment variable only (never hardcode)
- Default new queries to private (`is_private=true`)
- Support read-only deployment mode by disabling write tools
- Validate SQL strings are non-empty before submission

### Performance
- Default 50 row limit prevents context window overflow
- Prioritize `get_latest_result()` (zero credits) over fresh execution
- Handle 429 rate limits with explicit retry guidance to agent
- Use appropriate performance tier ("medium" vs "large")

### API Constraints
- Rate limits: 40 req/min (free tier), higher for paid
- Query results cached up to 90 days
- Execution timeout varies by compute tier
- Standard HTTP timeouts may be too short for complex queries

## External Dependencies

### Dune Analytics API
- **Base URL**: api.dune.com
- **Auth**: Bearer token via `DUNE_API_KEY`
- **Docs**: https://docs.dune.com/api-reference
- **SDK**: https://github.com/duneanalytics/dune-client

### FastMCP Framework
- **Docs**: https://gofastmcp.com
- **GitHub**: https://github.com/jlowin/fastmcp
- **Config**: fastmcp.json for dependencies and runtime

### Model Context Protocol
- **Spec**: https://github.com/modelcontextprotocol
- **Python SDK**: https://github.com/modelcontextprotocol/python-sdk
