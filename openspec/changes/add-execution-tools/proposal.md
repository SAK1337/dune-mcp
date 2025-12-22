# Change: Add Query Execution Tools

## Why
Query execution is the primary use case for Dune Analytics integration. Agents need both blocking (synchronous) and non-blocking (asynchronous) execution modes to handle queries of varying complexity and duration.

## What Changes
- Add `run_query` tool for blocking execution with result waiting
- Add `submit_query` tool for non-blocking execution returning execution_id
- Add `get_execution_status` tool for checking job state
- Add `get_execution_results` tool for retrieving completed job data
- Implement proper error mapping for Dune API errors

## Impact
- Affected specs: execution-tools (new capability)
- Affected code: server.py (add tool definitions)
- Dependencies: Requires core-server capability (proposal 1)
