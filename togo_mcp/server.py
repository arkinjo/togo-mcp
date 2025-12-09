from fastmcp import FastMCP
import csv
from typing import Dict
import os
import json
import httpx
import asyncio

# The MIE files are used to define the shape expressions for SPARQL queries. 
CWD = os.getenv("TOGOMCP_DIR", ".")
MIE_DIR = CWD + "/mie"
MIE_PROMPT= CWD + "/resources/MIE_prompt.md"
RDF_PORTAL_GUIDE= CWD + "/resources/rdf_portal_guide.md"
SPARQL_EXAMPLES= CWD + "/sparql-examples"
RDF_CONFIG_TEMPLATE= CWD + "/rdf-config/template.yaml"
ENDPOINTS_CSV = CWD + "/resources/endpoints.csv"

def load_sparql_endpoints(path: str) -> Dict[str, str]:
    """Load SPARQL endpoints from a CSV file."""
    endpoints = {}
    with open(path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            db_name, endpoint_url = row
            key = db_name.lower().replace(' ', '_').replace('-', '')
            endpoints[key] = endpoint_url
    return endpoints

# The SPARQL endpoints for various RDF databases, loaded from a CSV file.
SPARQL_ENDPOINT = load_sparql_endpoints(ENDPOINTS_CSV)
DBNAME_DESCRIPTION = f"Database name: One of {", ".join(SPARQL_ENDPOINT.keys())}"

# Making this a @mcp.tool() becomes an error, so we keep it as a function.
async def execute_sparql(sparql_query: str, dbname: str) -> str:
    """ Execute a SPARQL query on RDF Portal. 
    Args:
        sparql_query (str): The SPARQL query to execute.
        dbname (str): The name of the database to query. To find the supported databases, use the `get_sparql_endpoints` tool.
    Returns:
        dict: The results of the SPARQL query in CSV.
    """

    if dbname not in SPARQL_ENDPOINT:
        raise ValueError(f"Unknown database: {dbname}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            SPARQL_ENDPOINT[dbname], data={"query": sparql_query}, headers={"Accept": "text/csv"}
        )
    response.raise_for_status()
    return response.text

# The Primary MCP server
mcp = FastMCP("TogoMCP: RDF Portal MCP Server")

# creating an auxiliary MCP server from TogoID OpenAPI (to be merged)
togoid_client = httpx.AsyncClient(base_url="https://api.togoid.dbcls.jp")
with open("resources/togoid_oas.json", "r") as f:
    openapi_spec = json.load(f)

togoid_mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=togoid_client,
    name="TogoID MCP Server",
    mcp_names={
        "getAllDataset": "togoId_getAllDataset",
        "getDataset": "togoId_getDataset",
        "getAllRelation": "togoId_getAllRelation",
        "getRelation": "togoId_getRelation",
        "convertId": "togoId_convertId",
        "countId": "togoId_countId",
        "getDescription": "togoId_getDescription"
    }
)

# Merging TogoID tools into the primary MCP server
togoid_tools = asyncio.run(togoid_mcp.get_tools())
for key in togoid_tools:
    mcp.add_tool(togoid_tools[key])
