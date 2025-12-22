# Capability: MCP Prompts

## ADDED Requirements

### Requirement: Generate DuneSQL Prompt
The system SHALL provide a generate_dune_sql prompt that guides LLMs in constructing valid DuneSQL queries with proper syntax and conventions.

#### Scenario: Retrieve prompt with intent
- **WHEN** client retrieves generate_dune_sql prompt with intent argument
- **THEN** prompt template is returned with analytical goal context

#### Scenario: Retrieve prompt with chain
- **WHEN** client retrieves generate_dune_sql prompt with chain argument (e.g., "ethereum", "solana")
- **THEN** prompt template includes chain-specific context

#### Scenario: Prompt includes dialect instruction
- **WHEN** generate_dune_sql prompt is retrieved
- **THEN** template specifies "You are writing SQL for Dune Analytics (Trino/Presto dialect)"

#### Scenario: Prompt includes bytearray syntax
- **WHEN** generate_dune_sql prompt is retrieved
- **THEN** template explains that Ethereum addresses are bytearrays and use 0x... literals

#### Scenario: Prompt includes date handling
- **WHEN** generate_dune_sql prompt is retrieved
- **THEN** template explains interval syntax: "NOW() - INTERVAL '7' DAY"

#### Scenario: Prompt includes table naming convention
- **WHEN** generate_dune_sql prompt is retrieved
- **THEN** template advises using decoded project tables over raw tables

#### Scenario: Prompt includes safety reminder
- **WHEN** generate_dune_sql prompt is retrieved
- **THEN** template reminds to include "LIMIT 100 unless performing a specific aggregation"

### Requirement: Analyze Result Prompt
The system SHALL provide an analyze_result prompt that guides LLMs in interpreting JSON output from Dune queries.

#### Scenario: Retrieve analyze prompt
- **WHEN** client retrieves analyze_result prompt
- **THEN** prompt template for result analysis is returned

#### Scenario: Prompt includes outlier detection
- **WHEN** analyze_result prompt is retrieved
- **THEN** template includes guidance on identifying outliers in data

#### Scenario: Prompt includes growth calculation
- **WHEN** analyze_result prompt is retrieved
- **THEN** template includes instructions for calculating growth rates

#### Scenario: Prompt includes formatting guidance
- **WHEN** analyze_result prompt is retrieved
- **THEN** template includes instructions for formatting output as Markdown tables
