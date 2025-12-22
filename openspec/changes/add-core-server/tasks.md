# Tasks: Add Core MCP Server Infrastructure

## 1. Project Setup
- [x] 1.1 Create pyproject.toml with Python 3.11+ requirement
- [x] 1.2 Create fastmcp.json configuration file
- [x] 1.3 Create src/mcp_server_dune/ package directory

## 2. Server Implementation
- [x] 2.1 Create server.py with FastMCP initialization
- [x] 2.2 Implement get_dune() client factory function
- [x] 2.3 Add environment variable validation for DUNE_API_KEY

## 3. Entry Point
- [x] 3.1 Add __main__.py for CLI execution
- [x] 3.2 Configure mcp.run() entry point

## 4. Validation
- [x] 4.1 Verify server starts without errors
- [x] 4.2 Test API key missing error handling
- [x] 4.3 Confirm uv run execution works
