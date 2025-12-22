# Capability: MCP Resources

## ADDED Requirements

### Requirement: Latest Cached Result Resource
The system SHALL provide a resource at URI `dune://query/{query_id}/latest` that returns the cached result of the last successful query execution without consuming execution credits.

#### Scenario: Read cached result
- **WHEN** client reads dune://query/{query_id}/latest
- **AND** a cached result exists for the query
- **THEN** result rows are returned as JSON
- **AND** no execution credits are consumed

#### Scenario: No cached result available
- **WHEN** client reads dune://query/{query_id}/latest
- **AND** no cached result exists (never executed or cache expired)
- **THEN** appropriate error message is returned

#### Scenario: Query not found
- **WHEN** client reads dune://query/{query_id}/latest
- **AND** query_id does not exist
- **THEN** error message "Query ID {id} not found" is returned

#### Scenario: Resource MIME type
- **WHEN** client reads dune://query/{query_id}/latest
- **THEN** content type is application/json

### Requirement: Query SQL Definition Resource
The system SHALL provide a resource at URI `dune://query/{query_id}/sql` that returns the raw SQL text of a query for inspection.

#### Scenario: Read query SQL
- **WHEN** client reads dune://query/{query_id}/sql
- **THEN** the query's SQL code is returned as plain text

#### Scenario: Query not found
- **WHEN** client reads dune://query/{query_id}/sql
- **AND** query_id does not exist
- **THEN** error message "Query ID {id} not found" is returned

#### Scenario: Resource MIME type
- **WHEN** client reads dune://query/{query_id}/sql
- **THEN** content type is text/plain

### Requirement: Execution Status Resource
The system SHALL provide a resource at URI `dune://execution/{execution_id}/status` that returns the current state of an execution job.

#### Scenario: Read pending status
- **WHEN** client reads dune://execution/{execution_id}/status
- **AND** execution is still running
- **THEN** JSON object with state field is returned
- **AND** state is "QUERY_STATE_EXECUTING" or "QUERY_STATE_PENDING"

#### Scenario: Read completed status
- **WHEN** client reads dune://execution/{execution_id}/status
- **AND** execution has completed
- **THEN** JSON object with state "QUERY_STATE_COMPLETED" is returned

#### Scenario: Read failed status
- **WHEN** client reads dune://execution/{execution_id}/status
- **AND** execution has failed
- **THEN** JSON object with state "QUERY_STATE_FAILED" is returned

#### Scenario: Execution not found
- **WHEN** client reads dune://execution/{execution_id}/status
- **AND** execution_id does not exist
- **THEN** error message is returned

#### Scenario: Resource MIME type
- **WHEN** client reads dune://execution/{execution_id}/status
- **THEN** content type is application/json
