"""
MCP Server for Dune Analytics.

This server provides tools, resources, and prompts for interacting with
Dune Analytics blockchain data through the Model Context Protocol.
"""

import asyncio
import json
import os
from typing import Any, Literal, Optional

from dune_client.client import DuneClient
from dune_client.query import QueryBase
from dune_client.types import QueryParameter
from fastmcp import FastMCP, Context
from pydantic import Field

# Initialize FastMCP Server
mcp = FastMCP(
    "Dune Analytics",
    dependencies=["dune-client", "pydantic"],
)


# =============================================================================
# Client Factory
# =============================================================================


def get_dune() -> DuneClient:
    """
    Create an authenticated DuneClient instance.

    Returns:
        DuneClient configured with API key from environment.

    Raises:
        ValueError: If DUNE_API_KEY environment variable is not set.
    """
    key = os.getenv("DUNE_API_KEY")
    if not key:
        raise ValueError("DUNE_API_KEY environment variable is not set.")
    return DuneClient(key)


# =============================================================================
# Error Mapping
# =============================================================================


def map_dune_error(error: Exception) -> str:
    """Map Dune API errors to semantic agent feedback messages."""
    error_str = str(error).lower()

    if "401" in error_str or "unauthorized" in error_str:
        return "Authentication failed. Check your DUNE_API_KEY environment variable."
    elif "402" in error_str or "payment" in error_str or "credits" in error_str:
        return "Insufficient credits to run this query. Try a smaller query or use cached results."
    elif "404" in error_str or "not found" in error_str:
        return f"Resource not found. Please verify the ID exists."
    elif "429" in error_str or "rate limit" in error_str:
        return "Rate limit exceeded. Please wait 60 seconds before retrying."
    elif "400" in error_str or "syntax" in error_str or "parse" in error_str:
        return f"SQL Syntax Error: {error}. Please correct your SQL and try again."
    elif "timeout" in error_str:
        return "Execution timed out. Please use the asynchronous submit_query tool for long-running queries."
    else:
        return f"Dune API Error: {error}"


# =============================================================================
# Execution Tools
# =============================================================================


@mcp.tool
async def run_query(
    query_id: int = Field(..., description="The Dune Query ID to execute."),
    params: Optional[dict[str, Any]] = Field(
        default=None, description="Query parameters as key-value pairs."
    ),
    performance: Literal["medium", "large"] = Field(
        default="medium", description="Execution tier: 'medium' (default) or 'large'."
    ),
    limit: int = Field(
        default=50, description="Maximum rows to return. Default 50."
    ),
    ctx: Context = None,
) -> str:
    """
    Execute a saved Dune query and wait for results.

    Use for queries expected to complete quickly (<1 min).
    For long-running queries, use submit_query instead.
    """
    client = get_dune()

    if ctx:
        ctx.info(f"Starting execution for Query {query_id}...")

    try:
        # Convert dict params to Dune SDK QueryParameter objects
        query_params = []
        if params:
            for key, value in params.items():
                query_params.append(QueryParameter.text_type(key, str(value)))

        query = QueryBase(query_id=query_id, params=query_params)

        # Use to_thread for the synchronous SDK call
        results = await asyncio.to_thread(
            client.run_query,
            query,
            performance=performance,
        )

        # Apply limit
        rows = results.result.rows[:limit] if results.result.rows else []

        if ctx:
            ctx.info(f"Query completed. Returned {len(rows)} rows.")

        return json.dumps(rows, default=str)

    except Exception as e:
        error_msg = map_dune_error(e)
        if ctx:
            ctx.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool
async def submit_query(
    query_id: int = Field(..., description="The Dune Query ID to execute."),
    params: Optional[dict[str, Any]] = Field(
        default=None, description="Query parameters as key-value pairs."
    ),
    performance: Literal["medium", "large"] = Field(
        default="medium", description="Execution tier: 'medium' or 'large'."
    ),
) -> str:
    """
    Submit a query for execution and return the Execution ID immediately.

    Use this for long-running queries to avoid timeouts.
    Check progress with get_execution_status.
    """
    client = get_dune()

    try:
        query_params = []
        if params:
            for key, value in params.items():
                query_params.append(QueryParameter.text_type(key, str(value)))

        query = QueryBase(query_id=query_id, params=query_params)

        execution = await asyncio.to_thread(
            client.execute_query,
            query,
            performance=performance,
        )

        return json.dumps({
            "execution_id": execution.execution_id,
            "state": execution.state.value if hasattr(execution.state, 'value') else str(execution.state),
            "message": f"Execution started. Use get_execution_status with ID '{execution.execution_id}' to track progress."
        })

    except Exception as e:
        return f"Error: {map_dune_error(e)}"


@mcp.tool
async def get_execution_status(
    execution_id: str = Field(..., description="The execution ID to check."),
) -> str:
    """Check the status of a specific execution ID."""
    client = get_dune()

    try:
        status = await asyncio.to_thread(client.get_execution_status, execution_id)
        state = status.state.value if hasattr(status.state, 'value') else str(status.state)
        return json.dumps({"execution_id": execution_id, "state": state})

    except Exception as e:
        return f"Error: {map_dune_error(e)}"


@mcp.tool
async def get_execution_results(
    execution_id: str = Field(..., description="The execution ID to get results for."),
    limit: int = Field(default=50, description="Maximum rows to return. Default 50."),
    offset: int = Field(default=0, description="Number of rows to skip for pagination."),
) -> str:
    """Retrieve the results of a completed execution."""
    client = get_dune()

    try:
        results = await asyncio.to_thread(client.get_execution_results, execution_id)

        if results.result and results.result.rows:
            rows = results.result.rows[offset:offset + limit]
            return json.dumps(rows, default=str)
        else:
            return json.dumps([])

    except Exception as e:
        return f"Error: {map_dune_error(e)}"


# =============================================================================
# Ad-Hoc SQL Tool
# =============================================================================


@mcp.tool
async def run_sql(
    sql: str = Field(..., description="The raw DuneSQL (Trino dialect) query to execute."),
    performance: Literal["medium", "large"] = Field(
        default="medium", description="Execution tier: 'medium' or 'large'."
    ),
    limit: int = Field(default=50, description="Maximum rows to return. Default 50."),
    ctx: Context = None,
) -> str:
    """
    Execute raw ad-hoc SQL without creating a saved query.

    SQL must be valid DuneSQL (Trino/Presto dialect).
    Use 0x... literals for Ethereum addresses.
    Use NOW() - INTERVAL '7' DAY for date intervals.
    """
    if not sql or not sql.strip():
        return "Error: SQL query cannot be empty."

    client = get_dune()

    if ctx:
        ctx.info("Executing ad-hoc SQL query...")

    try:
        results = await asyncio.to_thread(
            client.run_sql,
            sql,
            performance=performance,
        )

        rows = results.result.rows[:limit] if results.result.rows else []

        if ctx:
            ctx.info(f"Query completed. Returned {len(rows)} rows.")

        return json.dumps(rows, default=str)

    except Exception as e:
        error_msg = map_dune_error(e)
        if ctx:
            ctx.error(error_msg)
        return f"Error: {error_msg}"


# =============================================================================
# Query Management Tools
# =============================================================================


@mcp.tool
async def create_query(
    name: str = Field(..., description="The title of the query."),
    query_sql: str = Field(..., description="The SQL code for the query."),
    description: str = Field(default="", description="Description of the query's purpose."),
    is_private: bool = Field(default=True, description="Whether the query is private. Default true."),
) -> str:
    """
    Save a new query to your Dune library.

    New queries default to private for security.
    """
    if not query_sql or not query_sql.strip():
        return "Error: SQL query cannot be empty."

    client = get_dune()

    try:
        result = await asyncio.to_thread(
            client.create_query,
            name=name,
            query_sql=query_sql,
            description=description,
            is_private=is_private,
        )

        return json.dumps({
            "query_id": result.query_id,
            "message": f"Query '{name}' created successfully."
        })

    except Exception as e:
        return f"Error: {map_dune_error(e)}"


@mcp.tool
async def update_query(
    query_id: int = Field(..., description="The Dune Query ID to update."),
    query_sql: Optional[str] = Field(default=None, description="New SQL code."),
    name: Optional[str] = Field(default=None, description="New query name."),
    description: Optional[str] = Field(default=None, description="New description."),
) -> str:
    """Update an existing query's SQL, name, or description."""
    client = get_dune()

    try:
        kwargs = {}
        if query_sql is not None:
            kwargs["query_sql"] = query_sql
        if name is not None:
            kwargs["name"] = name
        if description is not None:
            kwargs["description"] = description

        if not kwargs:
            return "Error: No fields to update. Provide query_sql, name, or description."

        await asyncio.to_thread(
            client.update_query,
            query_id,
            **kwargs,
        )

        return json.dumps({
            "query_id": query_id,
            "message": f"Query {query_id} updated successfully.",
            "updated_fields": list(kwargs.keys())
        })

    except Exception as e:
        return f"Error: {map_dune_error(e)}"


@mcp.tool
async def archive_query(
    query_id: int = Field(..., description="The Dune Query ID to archive."),
) -> str:
    """Move a query to the archive, removing it from active workspace."""
    client = get_dune()

    try:
        await asyncio.to_thread(client.archive_query, query_id)

        return json.dumps({
            "query_id": query_id,
            "message": f"Query {query_id} archived successfully."
        })

    except Exception as e:
        return f"Error: {map_dune_error(e)}"


# =============================================================================
# MCP Resources
# =============================================================================


@mcp.resource("dune://query/{query_id}/latest")
async def get_latest_result(query_id: int) -> str:
    """
    Read the cached result of the last successful execution.

    Does NOT consume execution credits.
    Results are cached for up to 90 days.
    """
    client = get_dune()

    try:
        results = await asyncio.to_thread(client.get_latest_result, query_id)

        if results.result and results.result.rows:
            return json.dumps(results.result.rows, default=str)
        else:
            return json.dumps([])

    except Exception as e:
        return f"Error: {map_dune_error(e)}"


@mcp.resource("dune://query/{query_id}/sql")
async def get_query_sql(query_id: int) -> str:
    """
    Read the SQL definition of a query.

    Use this to understand how a metric is calculated.
    """
    client = get_dune()

    try:
        query = await asyncio.to_thread(client.get_query, query_id)
        return query.sql if hasattr(query, 'sql') else str(query)

    except Exception as e:
        return f"Error: {map_dune_error(e)}"


@mcp.resource("dune://execution/{execution_id}/status")
async def get_execution_status_resource(execution_id: str) -> str:
    """
    Read the current state of an execution job.

    States: QUERY_STATE_PENDING, QUERY_STATE_EXECUTING,
    QUERY_STATE_COMPLETED, QUERY_STATE_FAILED
    """
    client = get_dune()

    try:
        status = await asyncio.to_thread(client.get_execution_status, execution_id)
        state = status.state.value if hasattr(status.state, 'value') else str(status.state)
        return json.dumps({"execution_id": execution_id, "state": state})

    except Exception as e:
        return f"Error: {map_dune_error(e)}"


# =============================================================================
# MCP Prompts
# =============================================================================


@mcp.prompt
def generate_dune_sql(
    intent: str = Field(..., description="The analytical goal (e.g., 'Analyze OpenSea volume')."),
    chain: str = Field(default="ethereum", description="The blockchain network (e.g., 'ethereum', 'solana')."),
) -> str:
    """
    Generate a system prompt to help construct valid DuneSQL queries.

    Includes dialect instructions, syntax guidance, and best practices.
    """
    return f"""You are writing SQL for Dune Analytics using the DuneSQL dialect (Trino/Presto).

## Analytical Goal
{intent}

## Target Chain
{chain}

## DuneSQL Syntax Rules

### 1. Ethereum Addresses (Bytearrays)
- Addresses are bytearrays, NOT strings
- Use 0x... literals directly: WHERE "from" = 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
- For string input, use: FROM_HEX('d8dA6BF26964aF9D7eEd9e03E53415D37aA96045')

### 2. Date/Time Handling
- Current time: NOW() or CURRENT_TIMESTAMP
- Intervals: NOW() - INTERVAL '7' DAY
- Date truncation: DATE_TRUNC('day', block_time)

### 3. Table Naming Convention
- Prefer decoded project tables for better performance:
  - Good: uniswap_v3_{chain}.Factory_evt_PoolCreated
  - Good: opensea_{chain}.trades
- Use raw tables only when decoded unavailable:
  - {chain}.transactions
  - {chain}.logs

### 4. Safety Best Practices
- ALWAYS include LIMIT clause (suggest LIMIT 100) unless doing aggregations
- Use block_time filters to reduce scan size
- Prefer COUNT(*) over SELECT * for existence checks

### 5. Common Patterns
```sql
-- Recent transactions for address
SELECT * FROM {chain}.transactions
WHERE "from" = 0x...
  AND block_time > NOW() - INTERVAL '7' DAY
LIMIT 100;

-- Daily aggregation
SELECT DATE_TRUNC('day', block_time) as day,
       COUNT(*) as tx_count,
       SUM(value/1e18) as eth_volume
FROM {chain}.transactions
WHERE block_time > NOW() - INTERVAL '30' DAY
GROUP BY 1
ORDER BY 1;
```

Generate SQL that accomplishes the analytical goal using these conventions."""


@mcp.prompt
def analyze_result() -> str:
    """
    Generate a system prompt to help interpret Dune query results.

    Includes guidance on outliers, growth rates, and formatting.
    """
    return """You are analyzing JSON data returned from a Dune Analytics query.

## Analysis Guidelines

### 1. Data Overview
- First, describe the structure: number of rows, columns present
- Identify the time range if temporal data
- Note any NULL or missing values

### 2. Statistical Analysis
- Calculate key metrics: sum, average, min, max for numeric columns
- Identify outliers (values > 2 standard deviations from mean)
- Look for patterns or trends in time-series data

### 3. Growth Rate Calculation
For time-series data, calculate:
- Period-over-period change: (current - previous) / previous * 100
- Compound growth rate for longer periods
- Highlight significant increases or decreases (>20%)

### 4. Outlier Detection
Flag rows where:
- Values are significantly higher/lower than average
- Sudden spikes or drops in sequential data
- Unusual patterns compared to historical norms

### 5. Output Formatting
Present findings as:
1. **Summary**: 2-3 sentence overview
2. **Key Metrics**: Bullet points of important numbers
3. **Data Table**: Markdown table of top/relevant rows
4. **Insights**: Notable patterns or anomalies

### Example Markdown Table
| Date | Volume (ETH) | Tx Count | Avg Size |
|------|-------------|----------|----------|
| 2024-01-01 | 1,234.5 | 456 | 2.7 |

Provide actionable insights based on the data analysis."""


# =============================================================================
# Entry Point
# =============================================================================


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
