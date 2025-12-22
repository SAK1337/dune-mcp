# Change: Add Run SQL Tool for Ad-Hoc Queries

## Why
Agents need the ability to execute raw, ad-hoc SQL without creating saved queries. This enables dynamic analysis where the agent writes its own SQL to answer unique user questions, supporting an iterative write-run-correct feedback loop.

## What Changes
- Add `run_sql` tool to execute raw DuneSQL (Trino dialect)
- Support performance tier selection
- Apply default row limit of 50
- Add basic SQL validation (non-empty check)

## Impact
- Affected specs: adhoc-sql (new capability)
- Affected code: server.py (add tool definition)
- Dependencies: Requires core-server capability (proposal 1)
- **Note**: This empowers agents to act as data analysts
