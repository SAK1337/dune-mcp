# Tasks: Add MCP Resources with dune:// URI Scheme

## 1. Latest Result Resource
- [x] 1.1 Implement resource handler for dune://query/{query_id}/latest
- [x] 1.2 Call client.get_latest_result() (no credits consumed)
- [x] 1.3 Return JSON formatted result rows
- [x] 1.4 Set MIME type to application/json

## 2. Query SQL Resource
- [x] 2.1 Implement resource handler for dune://query/{query_id}/sql
- [x] 2.2 Fetch query metadata and extract query_sql field
- [x] 2.3 Return raw SQL text
- [x] 2.4 Set MIME type to text/plain

## 3. Execution Status Resource
- [x] 3.1 Implement resource handler for dune://execution/{execution_id}/status
- [x] 3.2 Return JSON object with state field
- [x] 3.3 Set MIME type to application/json

## 4. Error Handling
- [x] 4.1 Handle query/execution not found
- [x] 4.2 Handle no cached result available
- [x] 4.3 Return appropriate error messages

## 5. Validation
- [x] 5.1 Test latest resource returns cached data
- [x] 5.2 Verify no credits consumed for latest resource
- [x] 5.3 Test SQL resource returns query text
- [x] 5.4 Test status resource returns valid states
