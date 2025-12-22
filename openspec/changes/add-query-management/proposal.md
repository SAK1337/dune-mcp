# Change: Add Query Management Tools

## Why
Agents need to manage their Dune Analytics query workspace beyond just executing queries. Creating, updating, and archiving queries enables agents to save analytical work for reuse and iterate on query logic based on feedback.

## What Changes
- Add `create_query` tool to save new queries to the user's library
- Add `update_query` tool to modify existing query SQL, name, or description
- Add `archive_query` tool to move queries to archive
- Default new queries to private for security

## Impact
- Affected specs: query-management (new capability)
- Affected code: server.py (add tool definitions)
- Dependencies: Requires core-server capability (proposal 1)
- **Note**: These are write operations that modify the user's Dune library
