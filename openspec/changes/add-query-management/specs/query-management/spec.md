# Capability: Query Management

## ADDED Requirements

### Requirement: Create Query Tool
The system SHALL provide a create_query tool that saves a new query to the user's Dune Analytics library.

#### Scenario: Create query with required fields
- **WHEN** create_query is called with name and query_sql
- **THEN** a new query is created in the user's library
- **AND** the new query_id is returned

#### Scenario: Create query with description
- **WHEN** create_query is called with name, query_sql, and description
- **THEN** the query is created with the provided description

#### Scenario: Create query defaults to private
- **WHEN** create_query is called without is_private parameter
- **THEN** the query is created with is_private=true
- **AND** the query is not publicly visible

#### Scenario: Create public query
- **WHEN** create_query is called with is_private=false
- **THEN** the query is created as publicly visible

#### Scenario: Create query with empty SQL
- **WHEN** create_query is called with empty query_sql
- **THEN** an error message is returned indicating SQL is required

### Requirement: Update Query Tool
The system SHALL provide an update_query tool that modifies an existing query's SQL, name, or description.

#### Scenario: Update query SQL
- **WHEN** update_query is called with query_id and query_sql
- **THEN** the query's SQL is updated
- **AND** success status is returned

#### Scenario: Update query name
- **WHEN** update_query is called with query_id and name
- **THEN** the query's name is updated

#### Scenario: Update query description
- **WHEN** update_query is called with query_id and description
- **THEN** the query's description is updated

#### Scenario: Update multiple fields
- **WHEN** update_query is called with query_id, query_sql, and name
- **THEN** both SQL and name are updated in single request

#### Scenario: Update non-existent query
- **WHEN** update_query is called with invalid query_id
- **THEN** error message "Query ID {id} not found" is returned

#### Scenario: Update query without permission
- **WHEN** update_query is called on query not owned by user
- **THEN** error message indicating permission denied is returned

### Requirement: Archive Query Tool
The system SHALL provide an archive_query tool that moves a query to the archive, removing it from active workspace.

#### Scenario: Archive owned query
- **WHEN** archive_query is called with valid query_id
- **AND** the query is owned by the authenticated user
- **THEN** the query is moved to archive
- **AND** success status is returned

#### Scenario: Archive non-existent query
- **WHEN** archive_query is called with invalid query_id
- **THEN** error message "Query ID {id} not found" is returned

#### Scenario: Archive query without permission
- **WHEN** archive_query is called on query not owned by user
- **THEN** error message indicating permission denied is returned
