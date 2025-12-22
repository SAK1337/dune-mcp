# Capability: Core Server

## ADDED Requirements

### Requirement: FastMCP Server Initialization
The system SHALL initialize a FastMCP server with the name "Dune Analytics" and declare dependencies on dune-client and pandas.

#### Scenario: Server starts successfully
- **WHEN** the server is started with a valid DUNE_API_KEY environment variable
- **THEN** the FastMCP server initializes without errors
- **AND** the server is ready to accept MCP connections

#### Scenario: Server metadata is correct
- **WHEN** an MCP client connects to the server
- **THEN** the server identifies itself as "Dune Analytics"
- **AND** exposes its capabilities according to MCP protocol

### Requirement: Dune Client Factory
The system SHALL provide a get_dune() factory function that creates authenticated DuneClient instances using the DUNE_API_KEY environment variable.

#### Scenario: Client creation with valid key
- **WHEN** get_dune() is called
- **AND** DUNE_API_KEY environment variable is set
- **THEN** a DuneClient instance is returned configured with the API key

#### Scenario: Client creation with missing key
- **WHEN** get_dune() is called
- **AND** DUNE_API_KEY environment variable is not set
- **THEN** a ValueError is raised with message "DUNE_API_KEY environment variable is not set."

### Requirement: Project Configuration
The system SHALL use fastmcp.json to declare dependencies (dune-client>=1.10.0, fastmcp>=2.0.0, pandas) and require Python 3.11+ runtime.

#### Scenario: Configuration file structure
- **WHEN** fastmcp.json is parsed
- **THEN** it contains source, dependencies, env, and runtime sections
- **AND** DUNE_API_KEY is marked as required in env section
