# Capability: Execution Tools

## ADDED Requirements

### Requirement: Run Query Tool (Blocking)
The system SHALL provide a run_query tool that executes a saved Dune query by ID and waits for results, returning the data in a single response.

#### Scenario: Successful query execution
- **WHEN** run_query is called with a valid query_id
- **THEN** the query is submitted to Dune Analytics
- **AND** the system polls until completion
- **AND** result rows are returned as JSON string

#### Scenario: Query with parameters
- **WHEN** run_query is called with query_id and params dictionary
- **THEN** parameters are converted to QueryParameter objects
- **AND** the query executes with injected parameter values

#### Scenario: Query with performance tier
- **WHEN** run_query is called with performance="large"
- **THEN** the query executes on the large compute tier

#### Scenario: Query with row limit
- **WHEN** run_query is called with limit parameter
- **THEN** results are limited to specified row count
- **AND** default limit is 50 rows if not specified

#### Scenario: Query not found
- **WHEN** run_query is called with invalid query_id
- **THEN** error message "Query ID {id} not found. Please verify the ID." is returned

### Requirement: Submit Query Tool (Non-Blocking)
The system SHALL provide a submit_query tool that initiates query execution and immediately returns the execution_id without waiting for completion.

#### Scenario: Successful submission
- **WHEN** submit_query is called with valid query_id
- **THEN** execution is started on Dune Analytics
- **AND** execution_id is returned immediately
- **AND** message includes guidance to use get_execution_status

#### Scenario: Submission with parameters
- **WHEN** submit_query is called with query_id and params
- **THEN** parameters are passed to the execution request

### Requirement: Get Execution Status Tool
The system SHALL provide a get_execution_status tool that checks the state of a specific execution job.

#### Scenario: Check pending execution
- **WHEN** get_execution_status is called with execution_id
- **AND** the job is still running
- **THEN** state "QUERY_STATE_EXECUTING" or "QUERY_STATE_PENDING" is returned

#### Scenario: Check completed execution
- **WHEN** get_execution_status is called with execution_id
- **AND** the job has finished
- **THEN** state "QUERY_STATE_COMPLETED" is returned

#### Scenario: Check failed execution
- **WHEN** get_execution_status is called with execution_id
- **AND** the job has failed
- **THEN** state "QUERY_STATE_FAILED" is returned

### Requirement: Get Execution Results Tool
The system SHALL provide a get_execution_results tool that retrieves data from a completed execution job.

#### Scenario: Retrieve results
- **WHEN** get_execution_results is called with execution_id
- **THEN** result rows are returned as JSON string

#### Scenario: Retrieve results with pagination
- **WHEN** get_execution_results is called with limit and offset
- **THEN** specified page of results is returned

#### Scenario: Results from incomplete execution
- **WHEN** get_execution_results is called for non-completed execution
- **THEN** appropriate error message is returned

### Requirement: Error Mapping
The system SHALL map Dune API errors to semantic agent feedback messages.

#### Scenario: SQL syntax error
- **WHEN** query execution fails with 400 Bad Request
- **THEN** message includes "SQL Syntax Error" with details

#### Scenario: Authentication failure
- **WHEN** API returns 401 Unauthorized
- **THEN** message indicates "Authentication failed. Check your DUNE_API_KEY."

#### Scenario: Insufficient credits
- **WHEN** API returns 402 Payment Required
- **THEN** message indicates "Insufficient credits" with suggestion to use cached results

#### Scenario: Rate limit exceeded
- **WHEN** API returns 429 Too Many Requests
- **THEN** message indicates "Rate limit exceeded. Please wait before retrying."
