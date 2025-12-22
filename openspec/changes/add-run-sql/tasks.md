# Tasks: Add Run SQL Tool for Ad-Hoc Queries

## 1. Tool Implementation
- [x] 1.1 Implement run_sql tool with @mcp.tool decorator
- [x] 1.2 Add sql (required), performance, limit parameters
- [x] 1.3 Use POST /v1/sql/execute endpoint via SDK
- [x] 1.4 Apply default limit of 50 rows

## 2. Input Validation
- [x] 2.1 Validate SQL string is not empty
- [x] 2.2 Return clear error message for empty SQL

## 3. Error Handling
- [x] 3.1 Map SQL syntax errors to helpful messages
- [x] 3.2 Handle timeout for complex queries
- [x] 3.3 Apply standard error mapping (401, 402, 429)

## 4. Async Support
- [x] 4.1 Wrap SDK call with asyncio.to_thread
- [x] 4.2 Add Context logging for progress

## 5. Validation
- [x] 5.1 Test with valid SELECT query
- [x] 5.2 Test with syntax error
- [x] 5.3 Test with empty SQL string
- [x] 5.4 Verify default limit is applied
