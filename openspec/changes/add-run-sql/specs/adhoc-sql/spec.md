# Capability: Ad-Hoc SQL Execution

## ADDED Requirements

### Requirement: Run SQL Tool
The system SHALL provide a run_sql tool that executes raw DuneSQL (Trino dialect) without creating a saved query in the user's library.

#### Scenario: Execute valid SQL
- **WHEN** run_sql is called with valid SQL string
- **THEN** the SQL is executed on Dune Analytics
- **AND** result rows are returned as JSON string

#### Scenario: Execute with performance tier
- **WHEN** run_sql is called with performance="large"
- **THEN** the query executes on the large compute tier

#### Scenario: Execute with row limit
- **WHEN** run_sql is called with limit parameter
- **THEN** results are limited to specified row count
- **AND** default limit is 50 rows if not specified

#### Scenario: Execute empty SQL
- **WHEN** run_sql is called with empty or whitespace-only SQL
- **THEN** error message "SQL query cannot be empty" is returned

#### Scenario: SQL syntax error
- **WHEN** run_sql is called with invalid SQL syntax
- **THEN** error message includes "SQL Syntax Error" with details from Dune

#### Scenario: Complex query timeout
- **WHEN** run_sql execution exceeds timeout
- **THEN** error message suggests using simpler query or smaller dataset

### Requirement: DuneSQL Dialect Support
The system SHALL accept SQL written in DuneSQL (Trino/Presto) dialect.

#### Scenario: Bytearray address syntax
- **WHEN** SQL contains Ethereum addresses as 0x... literals
- **THEN** the query executes correctly treating addresses as bytearrays

#### Scenario: Date interval syntax
- **WHEN** SQL contains interval syntax like "NOW() - INTERVAL '7' DAY"
- **THEN** the query executes correctly with proper date handling

#### Scenario: Decoded table access
- **WHEN** SQL references decoded project tables (e.g., uniswap_v3_ethereum.Factory_evt_PoolCreated)
- **THEN** the query executes against the decoded tables
