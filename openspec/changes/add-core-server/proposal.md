# Change: Add Core MCP Server Infrastructure

## Why
The mcp-server-dune project requires a foundational FastMCP server with Dune Analytics client integration. This establishes the base architecture for all subsequent tools, resources, and prompts.

## What Changes
- Initialize FastMCP server with proper metadata and dependencies
- Create DuneClient factory with environment-based API key management
- Establish project structure with proper Python packaging
- Configure uv for dependency management with fastmcp.json

## Impact
- Affected specs: core-server (new capability)
- Affected code: server.py, fastmcp.json, pyproject.toml
- Dependencies: fastmcp>=2.0.0, dune-client>=1.10.0, pydantic
