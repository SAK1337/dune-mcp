# **Comprehensive Specification for a Python-Based Model Context Protocol Server Integration with Dune Analytics**

## **1\. Executive Summary and Strategic Context**

The intersection of generative artificial intelligence and blockchain analytics represents a critical frontier in modern data science. As Large Language Models (LLMs) evolve from passive text generation engines into agentic systems capable of executing multi-step reasoning and tool usage, the requirement for robust, standardized interfaces to high-value data repositories becomes paramount. Dune Analytics, widely recognized as the industry standard for on-chain data querying and visualization, hosts a massive repository of structured blockchain data accessible via SQL (Structured Query Language). However, the complexity of interacting with the Dune API—which involves asynchronous job execution, complex credit metering, and specific SQL dialects—creates a significant barrier for generalized AI agents.

This document serves as an exhaustive technical specification for mcp-server-dune, a middleware application designed to bridge this gap using the Model Context Protocol (MCP). The MCP, an open standard for connecting AI assistants to systems of record, provides the necessary architectural framework to expose Dune’s capabilities as discrete, discoverable **Tools**, **Resources**, and **Prompts**.1 By implementing this server, developers can empower any MCP-compliant client (such as Claude Desktop, IDEs like Cursor, or autonomous Python agents) to natively understand, query, and manage Dune Analytics data without requiring custom, brittle integration code for each new agent implementation.

The architecture proposed herein leverages the fastmcp Python framework to ensure rapid development, strict type safety via Pydantic, and asynchronous concurrency compatibility.3 Furthermore, it utilizes the official dune-client SDK to handle the nuances of HTTP/2 communication, retries, and result pagination.5 This report details every aspect of the system, from the theoretical underpinnings of the asynchronous execution model to the granular definition of remote procedure call (RPC) signatures, ensuring a production-grade, secure, and extensible integration.

## **2\. Architectural Principles and System Design**

The design of the mcp-server-dune application is governed by a set of architectural principles derived from the unique constraints of the Dune API and the requirements of real-time AI interaction.

### **2.1 The Middleware Pattern in Agentic Workflows**

The MCP server functions as a stateless translation layer. It sits logically between the **Host** (the AI Agent or Client) and the **Data Provider** (Dune Analytics).

* **The Host** is responsible for state management, conversation history, and decision-making (e.g., determining *when* to execute a query versus when to search for an existing one).  
* **The Server** is responsible for capability negotiation, schema exposure, and protocol translation. It converts high-level intent (e.g., "Run query 123") into the specific HTTP requests required by Dune's execution engine.1  
* **The Data Provider** executes the compute-intensive SQL tasks and stores the results.

This separation of concerns is critical. By offloading the API complexity to the MCP server, the LLM remains focused on reasoning rather than implementation details. The server acts as a "driver" for the Dune "hardware," exposing a clean API to the operating system (the Agent).

### **2.2 Asynchronous Concurrency Model**

A defining characteristic of the Dune Analytics API is its asynchronous nature. Executing a query is not a synchronous request-response cycle; rather, it involves submitting a job, receiving an execution ID, and polling for completion.8 Queries can take anywhere from a few seconds to 30 minutes to complete depending on the compute tier (Medium vs. Large) and dataset size.10

Standard HTTP timeouts for MCP clients are often short (e.g., 60 seconds). Therefore, the server architecture must support a **Dual-Mode Execution Strategy**:

1. **Blocking Mode (Synchronous Wrapper):** For lightweight queries, the server awaits the result internally, polling Dune on behalf of the agent, and returns the final data in a single RPC response. This improves the user experience for quick lookups.6  
2. **Non-Blocking Mode (Async Handoff):** For complex analytical queries, the server submits the job and immediately returns the execution\_id to the agent. The agent is then responsible for checking the status via a separate tool call (get\_execution\_status).

To support this, the server implementation must utilize Python’s asyncio library. The fastmcp framework is designed as "async-first," allowing tool definitions to be async def functions. This ensures that a long-polling operation for one user or query does not block the main event loop, keeping the server responsive to health checks and other tool calls.3 The underlying dune-client also supports async execution patterns, allowing for efficient, non-blocking HTTP requests via aiohttp.13

### **2.3 Type Safety and Schema Introspection**

Reliability in agentic systems depends heavily on the clarity of the interface. If an agent hallucinates a parameter, the operation fails. To mitigate this, mcp-server-dune will leverage strict Python typing. The fastmcp framework inspects Python type hints (e.g., query\_id: int, performance: Literal\["medium", "large"\]) and Docstrings to automatically generate the JSON Schema descriptions required by the MCP protocol.3 This ensures that the LLM receives precise instructions on valid inputs, significantly reducing the rate of 400 Bad Request errors from the Dune API.

### **2.4 Security and Environment Isolation**

Granting an AI agent access to a paid API requires stringent security controls.

* **API Key Management:** The DUNE\_API\_KEY must never be hardcoded. It will be injected via environment variables, managed by the fastmcp.json configuration standard or the host system's secret management.15  
* **Write Access Control:** While reading public data is safe, the specification includes tools for **Creating**, **Updating**, and **Archiving** queries.16 These "write" operations modify the user's persistent library. The server design treats these as distinct capabilities, allowing for deployment configurations that might restrict the server to "Read-Only" mode if desired by disabling specific tools during registration.

## **3\. Technology Stack and Dependency Analysis**

The implementation of mcp-server-dune requires a carefully selected set of libraries to ensure performance, maintainability, and protocol compliance.

### **3.1 Core Framework: FastMCP**

The fastmcp library (v2.0+) is selected as the server backbone. Unlike the low-level mcp SDK, fastmcp provides a high-level, decorator-based API (@mcp.tool, @mcp.resource) that significantly reduces boilerplate code. It handles the lifecycle of the connection, error serialization, and—crucially—integrates natively with Pydantic for data validation. This choice accelerates development and ensures adherence to the latest MCP specifications.4

### **3.2 API Client: Dune Client SDK**

The official dune-client (v1.10.0+) is the engine for API interactions. It wraps the Dune v1 API endpoints, handling authentication headers, request serialization, and error parsing. Importantly, it provides utility methods like refresh() (execute and wait) and get\_latest\_result() (fetch from cache), which map directly to the desired MCP tool behaviors.5 The SDK's dependency on aiohttp aligns with the server's asynchronous requirement, enabling high-concurrency throughput.19

### **3.3 Package Management: uv**

To manage the Python environment and dependencies, uv is mandated. uv offers significantly faster resolution times than pip and provides a lockfile mechanism (uv.lock) to ensure reproducibility. It also simplifies the execution of the server via uv run, which allows the server to run in an ephemeral environment without manual virtual environment activation.5

## **4\. Comprehensive Tool Specification**

In the Model Context Protocol, **Tools** represent executable functions that an agent can invoke. They allow the agent to perform actions or retrieve dynamic data. The following section exhaustively defines the tools that mcp-server-dune must expose to provide full coverage of the Dune Analytics capabilities.

### **4.1 Execution Tools**

These tools are the primary mechanism for retrieving data. They handle the "Execute" and "Result" endpoints of the Dune API.

#### **Tool: run\_query**

* **Purpose:** Executes a specific, pre-existing query by its ID and waits for the results. This is the "happy path" for retrieving fresh data for known metrics.  
* **Mechanism:** Wraps dune\_client.run\_query. It submits the execution, polls the status loop, and returns the result rows.  
* **Parameters:**  
  * query\_id (integer, required): The unique identifier of the query (e.g., 123456).  
  * params (object, optional): A dictionary of query parameters to inject (e.g., {"token\_address": "0x...", "interval": "24h"}). The server must serialize these into the format expected by the Dune API.10  
  * performance (string, optional): The execution tier. Valid values are "medium" (default) or "large". Using "large" consumes more credits but processes faster.  
  * limit (integer, optional): The maximum number of rows to return. **Default:** 50\. This is a crucial guardrail to prevent overflowing the LLM's context window with massive datasets.21  
* **Returns:** A JSON-formatted string containing the list of result rows.  
* **Error Handling:** Must catch DuneError and return a descriptive message (e.g., "Query failed due to SQL syntax error in line 4") rather than a generic 500 fault.22

#### **Tool: run\_sql**

* **Purpose:** Allows the agent to execute raw, ad-hoc SQL without creating a saved query in the library. This enables dynamic analysis where the agent writes its own SQL to answer unique user questions.  
* **Mechanism:** Wraps the POST /v1/sql/execute endpoint.8  
* **Parameters:**  
  * sql (string, required): The raw DuneSQL (Trino dialect) string.  
  * performance (string, optional): "medium" or "large".  
  * limit (integer, optional): Default 50\.  
* **Implication:** This tool empowers the agent to act as a data analyst. It allows for a feedback loop: write SQL \-\> run \-\> see error \-\> correct SQL \-\> run again.  
* **Security Note:** While Dune handles the isolation of the SQL execution, the MCP server should enforce a basic sanity check (e.g., ensuring the string is not empty) before submission.

#### **Tool: submit\_query (Non-Blocking)**

* **Purpose:** Initiates a query execution but returns immediately. This is required for long-running queries to avoid HTTP timeouts.  
* **Mechanism:** Wraps dune\_client.execute\_query (which returns an execution ID).  
* **Parameters:** Same as run\_query (query\_id, params, performance).  
* **Returns:** A JSON object containing the execution\_id and the initial state (usually "PENDING").  
* **Agent Instruction:** The return message should explicitly instruct the agent: "Execution started with ID {id}. Use get\_execution\_status to monitor progress."

#### **Tool: get\_execution\_status**

* **Purpose:** Checks the state of a specific job.  
* **Mechanism:** Wraps GET /v1/execution/{id}/status.  
* **Parameters:**  
  * execution\_id (string, required).  
* **Returns:** The state string (e.g., "QUERY\_STATE\_EXECUTING", "QUERY\_STATE\_COMPLETED", "QUERY\_STATE\_FAILED").

#### **Tool: get\_execution\_results**

* **Purpose:** Retrieves the data for a completed job.  
* **Mechanism:** Wraps GET /v1/execution/{id}/results.  
* **Parameters:**  
  * execution\_id (string, required).  
  * limit (integer, optional): Default 50\.  
  * offset (integer, optional): For pagination.  
* **Returns:** The result rows in JSON format.

### **4.2 Query Management Tools (CRUD)**

To be truly useful, an agent must manage its workspace. These tools map to the Query Management endpoints.16

#### **Tool: create\_query**

* **Purpose:** Saves a new query into the user's Dune library.  
* **Parameters:**  
  * name (string, required): The title of the query.  
  * query\_sql (string, required): The SQL code.  
  * description (string, optional): Metadata about the query's purpose.  
  * is\_private (boolean, optional): Default true. It is best practice to default to private to prevent accidental leakage of sensitive logic.  
* **Returns:** The new query\_id.

#### **Tool: update\_query**

* **Purpose:** Modifies an existing query. This allows the agent to refine a saved query based on user feedback (e.g., "Add a filter for volumes \> $1M").  
* **Parameters:**  
  * query\_id (integer, required).  
  * query\_sql (string, optional).  
  * name (string, optional).  
  * description (string, optional).  
* **Returns:** Success status.

#### **Tool: archive\_query**

* **Purpose:** Moves a query to the archive, decluttering the workspace.  
* **Parameters:**  
  * query\_id (integer, required).  
* **Returns:** Success status.

### **4.3 Data Discovery Tools**

Before an agent can query data, it often needs to know what queries exist.

#### **Tool: list\_queries**

* **Purpose:** Lists the queries owned by the authenticated user.  
* **Mechanism:** Wraps GET /v1/queries (if supported by client/API) or relies on the agent knowing IDs. *Note: The Dune API for listing queries is limited; strictly speaking, the API focuses on execution. If the SDK supports a library listing, it should be exposed. Otherwise, this tool might be omitted or limited to recently executed queries.*

## **5\. Resource Specification**

In MCP, **Resources** are passive data sources that can be read like files. They are distinct from tools in that they are typically read-only and stateless. The mcp-server-dune will expose Dune data via custom URI schemes.

### **5.1 URI Scheme: dune://**

The server will register a resource handler for the dune:// scheme.

### **5.2 Resource Definitions**

#### **Resource: Latest Cached Result**

* **URI Template:** dune://query/{query\_id}/latest  
* **Purpose:** Returns the result of the *last successful execution* of the query. This endpoint consumes **zero execution credits**, as it only reads from Dune's internal cache (valid for up to 90 days).8  
* **Behavior:** The server calls client.get\_latest\_result(query\_id).  
* **Use Case:** Ideal for frequently accessed dashboards where real-time freshness is not critical (e.g., "Daily Active Users" which only changes once a day). The agent should be prompted to try reading this resource *before* triggering a new execution via run\_query.  
* **MIME Type:** application/json.

#### **Resource: Query Definition (SQL)**

* **URI Template:** dune://query/{query\_id}/sql  
* **Purpose:** Returns the raw SQL text of a query.  
* **Behavior:** Fetches the query metadata and extracts the query\_sql field.  
* **Use Case:** Allows the agent to "read" the logic of a query to understand how a metric is calculated. This is essential for "Chain of Thought" reasoning, where the agent verifies the methodology before reporting the number.  
* **MIME Type:** text/plain (specifically application/x-sql or similar).

#### **Resource: Execution Status**

* **URI Template:** dune://execution/{execution\_id}/status  
* **Purpose:** A lightweight resource to check the status of a job.  
* **Behavior:** Returns a simple JSON string {"state": "QUERY\_STATE\_COMPLETED"}.  
* **Use Case:** Agents can poll this resource URI rather than calling a tool repeatedly, which semantics align better with "watching" a state change.

## **6\. Prompt Engineering and Context Injection**

**Prompts** in MCP are reusable templates that the server provides to the client. They help guide the LLM's behavior and input generation. For Dune, this is critical because writing valid DuneSQL (Trino) requires specific knowledge of table names and syntax quirks.

### **6.1 Prompt: generate\_dune\_sql**

* **Name:** generate\_dune\_sql  
* **Description:** A system prompt designed to assist the LLM in constructing valid DuneSQL queries.  
* **Arguments:**  
  * intent (string): The user's analytical goal (e.g., "Analyze OpenSea volume").  
  * chain (string): The blockchain network (e.g., "ethereum", "solana").  
* Template Content:  
  The prompt text injected into the context should include:  
  1. **Dialect Instruction:** "You are writing SQL for Dune Analytics (Trino/Presto dialect)."  
  2. **Bytearray Syntax:** "Ethereum addresses must be treated as bytearrays. Use 0x... literals directly or cast using from\_hex if dealing with strings."  
  3. **Date Handling:** "Use standard SQL interval syntax: NOW() \- INTERVAL '7' DAY."  
  4. **Table Naming Convention:** "Prefer decoded project tables (e.g., uniswap\_v3\_ethereum.Factory\_evt\_PoolCreated) over raw calls (ethereum.transactions) for better performance."  
  5. **Safety:** "Always include LIMIT 100 unless performing a specific aggregation, to avoid timeout errors."  
  6. **Schema Context:** If possible, dynamically inject the schema of relevant tables if the user specifies a project.

### **6.2 Prompt: analyze\_result**

* **Name:** analyze\_result  
* **Description:** A prompt that guides the agent on how to interpret the JSON output from a Dune query.  
* **Content:** Instructions on how to look for outliers, calculate growth rates from the returned rows, and format the output into a Markdown table for the user.

## **7\. Performance and Resource Management**

Integrating with a metered API requires careful resource management to avoid cost overruns and ensure system stability.

### **7.1 Credit Consumption Strategy**

Dune's pricing model charges "Credits" for execution. Complex queries cost more.

* **Caching First:** The server implementation must prioritize the get\_latest\_result logic. The dune-client exposes max\_age\_hours. The MCP server tools should expose a refresh parameter (boolean). If false (default), the server attempts to fetch a cached result. Only if refresh=true or no cache exists does it trigger a new execution.  
* **Limit Enforcement:** The mandatory limit parameter in the run\_query tool defaults to 50 rows. This prevents a single accidental query from pulling gigabytes of data, which would not only consume API credits (if bandwidth is metered) but also crash the LLM client.

### **7.2 Rate Limiting and Backoff**

The Dune API enforces rate limits (e.g., 40 requests/minute for free tier, higher for paid).24

* **Handling 429 Errors:** The dune-client likely handles basic retries, but the MCP server must explicitly catch 429 Too Many Requests exceptions.  
* **Agent Feedback:** When a 429 occurs, the server must return a ToolResult indicating failure with a specific message: "Rate limit exceeded. Please wait 60 seconds before retrying." This allows the agent to pause its execution loop.

## **8\. Error Handling and Observability**

Robust error handling is the difference between a frustrating agent and a helpful one. The server must translate technical API errors into semantic feedback.

### **8.1 Exception Mapping Table**

| Dune API Status | Exception Type | Agent Feedback Message |
| :---- | :---- | :---- |
| **400 Bad Request** | DuneError (Syntax) | "SQL Syntax Error:. Please correct your SQL and try again." |
| **401 Unauthorized** | DuneError (Auth) | "Authentication failed. Check your DUNE\_API\_KEY environment variable." |
| **402 Payment Required** | DuneError (Credits) | "Insufficient credits to run this query. Try a smaller query or use cached results." |
| **404 Not Found** | DuneError (ID) | "Query ID {id} not found. Please verify the ID using list\_queries." |
| **500 Server Error** | DuneError (Server) | "Dune internal error. This is temporary; please retry later." |
| **Timeout** | TimeoutError | "Execution timed out. Please use the asynchronous submit\_query tool for this request." |

### **8.2 Logging via Context**

The fastmcp framework provides a Context object that can be injected into tool functions.

* **Progress Reporting:** For long-running queries, the server should use ctx.info() to send logs back to the client console.  
  Python  
  @mcp.tool  
  async def run\_query(query\_id: int, ctx: Context):  
      ctx.info(f"Submitting query {query\_id}...")  
      \#... execution...  
      ctx.info("Query finished. Fetching results...")

* **Visibility:** This provides the user with visual confirmation that the system is working, even during the "black box" period of query execution.1

## **9\. Deployment and Configuration**

To ensure the server is reproducible and secure, the deployment strategy relies on modern Python tooling.

### **9.1 fastmcp.json Configuration**

The use of fastmcp.json serves as the single source of truth for the server's configuration.15

JSON

{  
  "source": "server.py",  
  "dependencies": \[  
    "dune-client\>=1.10.0",  
    "fastmcp\>=2.0.0",  
    "pandas"  
  \],  
  "env": {  
    "DUNE\_API\_KEY": "ENV\_VAR\_REQUIRED"  
  },  
  "runtime": {  
    "python": "3.11"  
  }  
}

### **9.2 Package Management with uv**

The server uses uv for dependency resolution. uv ensures that the dependencies listed in fastmcp.json are installed in an isolated environment at runtime, preventing conflicts with the host system.5

### **9.3 Local vs. Remote Execution**

* **Local (Stdio):** For usage with Claude Desktop. The configuration file claude\_desktop\_config.json points to the uv run command. This keeps the API key on the user's local machine, maximizing security.25  
* **Remote (SSE):** For hosting on a server (e.g., Render/Railway). fastmcp supports an SSE transport mode (fastmcp run server.py \--transport sse). This allows a shared server instance to be accessed by multiple agents, though it requires careful management of the API key (which becomes a shared secret).1

## **10\. Implementation Roadmap**

The development of mcp-server-dune should follow this phased approach:

1. **Phase 1: Core Connectivity (Read-Only)**  
   * Initialize FastMCP server.  
   * Implement dune-client connection.  
   * Implement run\_query (blocking) and dune://latest resource.  
   * *Deliverable:* An agent can run existing queries and read results.  
2. **Phase 2: Asynchronous & Management (Power User)**  
   * Implement submit\_query / get\_status loop.  
   * Implement create/update/archive tools.  
   * Refine Pydantic models for strict validation.  
   * *Deliverable:* An agent can perform long-running analysis and save its work.  
3. **Phase 3: Expert Features (Analyst)**  
   * Implement run\_sql for ad-hoc queries.  
   * Add generate\_dune\_sql prompts.  
   * Implement extensive error mapping and user feedback.  
   * *Deliverable:* A fully autonomous data analyst agent.

## **11\. Conclusion**

The mcp-server-dune specification defines a high-performance, resilient, and secure integration between the Dune Analytics ecosystem and the emerging world of AI agents. By rigorously adhering to the Model Context Protocol and leveraging the asynchronous capabilities of modern Python, this server unlocks a new paradigm of data interaction. Agents will no longer be limited to static knowledge; they will possess the capability to actively query, analyze, and monitor the blockchain in real-time, providing users with insights that were previously inaccessible without manual expertise. This architecture ensures that as LLMs improve, their ability to leverage Dune's data improves in lockstep, creating a future-proof foundation for automated crypto-analytics.

# ---

**Technical Reference: Python Implementation Skeleton**

The following code structure serves as the normative reference for the implementation, embodying the principles defined in this report.

Python

\# server.py  
from fastmcp import FastMCP, Context  
from dune\_client.client import DuneClient  
from dune\_client.query import QueryBase  
from dune\_client.types import QueryParameter  
from pydantic import Field  
import os  
import asyncio  
from typing import Optional, List, Dict, Any

\# Initialize FastMCP Server  
mcp \= FastMCP("Dune Analytics", dependencies=\["dune-client", "pandas"\])

\# Helper: Client Factory  
def get\_dune() \-\> DuneClient:  
    key \= os.getenv("DUNE\_API\_KEY")  
    if not key:  
        raise ValueError("DUNE\_API\_KEY environment variable is not set.")  
    return DuneClient(key)

\# \--- TOOLS: Execution \---

@mcp.tool  
async def run\_query(  
    query\_id: int \= Field(..., description="The Dune Query ID to execute."),  
    params: Dict\[str, Any\] \= Field(default\_factory=dict, description="Query parameters."),  
    limit: int \= Field(50, description="Max rows to return. Default 50."),  
    ctx: Context \= None  
) \-\> str:  
    """  
    Executes a saved Dune query and waits for results.   
    Use for queries expected to complete quickly (\<1 min).  
    """  
    client \= get\_dune()  
    ctx.info(f"Starting execution for Query {query\_id}...")  
      
    \# Convert dict params to Dune SDK QueryParameter objects  
    query\_params \= \[QueryParameter.enum\_type(k, v) for k, v in params.items()\]  
    query \= QueryBase(query\_id=query\_id, params=query\_params)  
      
    \# Use to\_thread for the synchronous SDK call to avoid blocking the loop  
    \# Note: Modern dune-client may support async, check version docs.  
    try:  
        results \= await asyncio.to\_thread(client.run\_query, query, limit=limit)  
        ctx.info(f"Query completed. Returned {len(results.result.rows)} rows.")  
        return str(results.result.rows)  
    except Exception as e:  
        ctx.error(f"Dune Execution Failed: {str(e)}")  
        return f"Error: {str(e)}"

@mcp.tool  
async def submit\_query(  
    query\_id: int,  
    params: Dict\[str, Any\] \= None,  
) \-\> str:  
    """  
    Submits a query for execution and returns the Execution ID immediately.  
    Use this for long-running queries to avoid timeouts.  
    """  
    client \= get\_dune()  
    query \= QueryBase(query\_id=query\_id)  
    \# Submission only  
    execution \= await asyncio.to\_thread(client.execute\_query, query)  
    return f"Execution Started. ID: {execution.execution\_id}. Use get\_execution\_status to track."

@mcp.tool  
async def get\_execution\_status(execution\_id: str) \-\> str:  
    """Checks the status of a specific execution ID."""  
    client \= get\_dune()  
    status \= await asyncio.to\_thread(client.get\_execution\_status, execution\_id)  
    return status.state

\# \--- RESOURCES: Data Access \---

@mcp.resource("dune://query/{query\_id}/latest")  
def get\_latest\_result(query\_id: int) \-\> str:  
    """  
    Reads the cached result of the last successful execution.  
    Does NOT consume execution credits.  
    """  
    client \= get\_dune()  
    \# Logic to fetch latest result  
    results \= client.get\_latest\_result(query\_id)  
    return str(results.result.rows)

\# \--- ENTRY POINT \---

if \_\_name\_\_ \== "\_\_main\_\_":  
    mcp.run()

#### **Works cited**

1. The official Python SDK for Model Context Protocol servers and clients, accessed December 21, 2025, [https://github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)  
2. Model Context Protocol \- GitHub, accessed December 21, 2025, [https://github.com/modelcontextprotocol](https://github.com/modelcontextprotocol)  
3. Tools \- FastMCP, accessed December 21, 2025, [https://gofastmcp.com/servers/tools](https://gofastmcp.com/servers/tools)  
4. jlowin/fastmcp: The fast, Pythonic way to build MCP servers and clients, accessed December 21, 2025, [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)  
5. dune-client \- PyPI, accessed December 21, 2025, [https://pypi.org/project/dune-client/](https://pypi.org/project/dune-client/)  
6. Execution & Results \- Dune Docs, accessed December 21, 2025, [https://docs.dune.com/api-reference/quickstart/results-eg](https://docs.dune.com/api-reference/quickstart/results-eg)  
7. MCP Python SDK \- PyPI, accessed December 21, 2025, [https://pypi.org/project/mcp/1.7.1/](https://pypi.org/project/mcp/1.7.1/)  
8. Overview \- Dune Docs, accessed December 21, 2025, [https://docs.dune.com/api-reference/executions/execution-object](https://docs.dune.com/api-reference/executions/execution-object)  
9. Client SDKs \- Dune Docs, accessed December 21, 2025, [https://docs.dune.com/api-reference/overview/sdks](https://docs.dune.com/api-reference/overview/sdks)  
10. Execute Query \- Dune Docs, accessed December 21, 2025, [https://docs.dune.com/api-reference/executions/endpoint/execute-query](https://docs.dune.com/api-reference/executions/endpoint/execute-query)  
11. paradigmxyz/spice: Simple client for extracting data from the Dune ..., accessed December 21, 2025, [https://github.com/paradigmxyz/spice](https://github.com/paradigmxyz/spice)  
12. Build MCP Servers in Python with FastMCP \- Complete Guide, accessed December 21, 2025, [https://mcpcat.io/guides/building-mcp-server-python-fastmcp/](https://mcpcat.io/guides/building-mcp-server-python-fastmcp/)  
13. Python Client v2.5 \- Async Support \- Aleph Alpha Docs, accessed December 21, 2025, [https://docs.aleph-alpha.com/docs/changelog/2022-11-14-async-python-client/](https://docs.aleph-alpha.com/docs/changelog/2022-11-14-async-python-client/)  
14. Asynchronous API Calls in Python with \`asyncio\` \- Calybre, accessed December 21, 2025, [https://www.calybre.global/post/asynchronous-api-calls-in-python-with-asyncio](https://www.calybre.global/post/asynchronous-api-calls-in-python-with-asyncio)  
15. Project Configuration \- FastMCP, accessed December 21, 2025, [https://gofastmcp.com/deployment/server-configuration](https://gofastmcp.com/deployment/server-configuration)  
16. Update Query \- Dune Docs, accessed December 21, 2025, [https://docs.dune.com/api-reference/queries/endpoint/update](https://docs.dune.com/api-reference/queries/endpoint/update)  
17. Create Query \- Dune Docs, accessed December 21, 2025, [https://docs.dune.com/api-reference/queries/endpoint/create](https://docs.dune.com/api-reference/queries/endpoint/create)  
18. fastmcp \- PyPI, accessed December 21, 2025, [https://pypi.org/project/fastmcp/](https://pypi.org/project/fastmcp/)  
19. dune-client \- PyPI Download Stats, accessed December 21, 2025, [https://pypistats.org/packages/dune-client](https://pypistats.org/packages/dune-client)  
20. duneanalytics/dune-client: A framework for interacting with ... \- GitHub, accessed December 21, 2025, [https://github.com/duneanalytics/dune-client](https://github.com/duneanalytics/dune-client)  
21. Dune Analytics introduction tutorial (with examples) \- Medium, accessed December 21, 2025, [https://medium.com/zengo/dune-analytics-introduction-tutorial-with-examples-d2c764600d6](https://medium.com/zengo/dune-analytics-introduction-tutorial-with-examples-d2c764600d6)  
22. Troubleshooting Errors \- Dune Docs, accessed December 21, 2025, [https://docs.dune.com/api-reference/overview/troubleshooting](https://docs.dune.com/api-reference/overview/troubleshooting)  
23. Overview \- Dune Docs, accessed December 21, 2025, [https://docs.dune.com/api-reference/queries/endpoint/query-object](https://docs.dune.com/api-reference/queries/endpoint/query-object)  
24. Rate Limits \- Dune Docs, accessed December 21, 2025, [https://docs.dune.com/api-reference/overview/rate-limits](https://docs.dune.com/api-reference/overview/rate-limits)  
25. Use MCP servers in VS Code, accessed December 21, 2025, [https://code.visualstudio.com/docs/copilot/customization/mcp-servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)