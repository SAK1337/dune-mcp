# Tasks: Add Query Management Tools

## 1. Create Query Tool
- [x] 1.1 Implement create_query tool with @mcp.tool decorator
- [x] 1.2 Add name, query_sql, description, is_private parameters
- [x] 1.3 Default is_private to True for security
- [x] 1.4 Return new query_id on success

## 2. Update Query Tool
- [x] 2.1 Implement update_query tool
- [x] 2.2 Add query_id (required), query_sql, name, description (optional)
- [x] 2.3 Only update provided fields
- [x] 2.4 Return success status

## 3. Archive Query Tool
- [x] 3.1 Implement archive_query tool
- [x] 3.2 Add query_id parameter
- [x] 3.3 Return success status

## 4. Error Handling
- [x] 4.1 Handle query not found (404)
- [x] 4.2 Handle permission denied errors
- [x] 4.3 Validate query_sql is non-empty on create

## 5. Validation
- [x] 5.1 Test create_query with valid SQL
- [x] 5.2 Test update_query on owned query
- [x] 5.3 Test archive_query on owned query
- [x] 5.4 Verify private default on create
