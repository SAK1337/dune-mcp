# mcp-server-dune

A Model Context Protocol (MCP) server for integrating AI agents with [Dune Analytics](https://dune.com) blockchain data.

## Requirements

- Python 3.11+
- Dune Analytics API key

## Features

### Tools
- **run_query** - Execute saved Dune queries and wait for results
- **submit_query** - Submit queries asynchronously for long-running jobs
- **get_execution_status** - Check the status of running queries
- **get_execution_results** - Retrieve results from completed executions
- **run_sql** - Execute raw ad-hoc DuneSQL queries
- **create_query** - Save new queries to your Dune library
- **update_query** - Modify existing queries
- **archive_query** - Archive queries from active workspace

### Resources (dune:// scheme)
- `dune://query/{id}/latest` - Cached results (zero credits)
- `dune://query/{id}/sql` - Query SQL definition
- `dune://execution/{id}/status` - Execution job status

### Prompts
- **generate_dune_sql** - Guide for writing valid DuneSQL
- **analyze_result** - Guide for interpreting query results

## Installation

```bash
# Install from source
pip install -e .

# Or install dependencies directly
pip install fastmcp>=2.0.0 dune-client>=1.10.0 pydantic>=2.0.0
```

## Configuration

Set your Dune API key as an environment variable:

```bash
# Linux/macOS
export DUNE_API_KEY="your-api-key-here"

# Windows Command Prompt
set DUNE_API_KEY=your-api-key-here

# Windows PowerShell
$env:DUNE_API_KEY="your-api-key-here"
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dune": {
      "command": "python",
      "args": ["-m", "mcp_server_dune"],
      "env": {
        "DUNE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Direct Execution

```bash
# Run the server
python -m mcp_server_dune
```

## Usage Examples

### Execute a Saved Query

```python
# Run query ID 123456 with parameters
run_query(
    query_id=123456,
    params={"token_address": "0x..."},
    performance="medium",
    limit=50
)
```

### Execute Ad-Hoc SQL

```python
# Run raw DuneSQL
run_sql(
    sql="""
    SELECT DATE_TRUNC('day', block_time) as day,
           COUNT(*) as tx_count
    FROM ethereum.transactions
    WHERE block_time > NOW() - INTERVAL '7' DAY
    GROUP BY 1
    ORDER BY 1
    LIMIT 100
    """,
    performance="medium"
)
```

### Read Cached Results (Zero Credits)

Access the resource `dune://query/123456/latest` to get cached results without consuming execution credits.

## DuneSQL Tips

- Addresses are bytearrays: use `0x...` literals directly
- Date intervals: `NOW() - INTERVAL '7' DAY`
- Prefer decoded tables: `uniswap_v3_ethereum.Factory_evt_PoolCreated`
- Always include `LIMIT` to prevent timeouts

## Development

```bash
# Clone the repository
git clone https://github.com/your-org/mcp-server-dune
cd mcp-server-dune

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run the server locally
python -m mcp_server_dune
```

## License

MIT
