# Tasks: Add Query Execution Tools

## 1. Blocking Execution
- [x] 1.1 Implement run_query tool with @mcp.tool decorator
- [x] 1.2 Add query_id, params, performance, limit parameters
- [x] 1.3 Implement parameter conversion to QueryParameter objects
- [x] 1.4 Add asyncio.to_thread wrapper for sync SDK call
- [x] 1.5 Add Context logging for progress feedback

## 2. Non-Blocking Execution
- [x] 2.1 Implement submit_query tool
- [x] 2.2 Return execution_id with guidance message
- [x] 2.3 Implement get_execution_status tool
- [x] 2.4 Implement get_execution_results tool with limit/offset

## 3. Error Handling
- [x] 3.1 Add DuneError exception handling
- [x] 3.2 Map HTTP status codes to semantic messages
- [x] 3.3 Handle timeout scenarios with guidance

## 4. Validation
- [x] 4.1 Test run_query with valid query_id
- [x] 4.2 Test run_query with invalid query_id (404)
- [x] 4.3 Test non-blocking flow (submit -> status -> results)
- [x] 4.4 Verify default limit of 50 rows
