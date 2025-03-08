from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List, Tuple
from db_service import db

# Create an MCP server
mcp = FastMCP("SQL Data Server")

# Try to connect to the database using environment variables
if not db.connect():
    print("Failed to connect to database using environment variables")
    exit(1)
print("Successfully connected to database")

@mcp.resource("mcp://schema")
def get_database_schema() -> Dict[str, List[Tuple[str, str]]]:
    """STEP 1: Get the database schema to understand available tables and their columns.
    Returns a dictionary where:
    - Keys are table names
    - Values are lists of (column_name, column_type) tuples
    
    Use this first to understand the database structure before creating queries.
    """
    return db.get_table_structure()

@mcp.tool()
def get_table_sample(table: str, limit: int = 5) -> List[Dict[str, Any]]:
    """STEP 2 (Optional): Get sample data from a specific table to understand its contents.
    This helps in understanding the actual data before writing queries.
    
    Args:
        table: Name of the table to sample
        limit: Number of rows to return (default: 5)
    
    Returns a list of dictionaries where each dictionary represents a row.
    """
    columns, data = db.get_sample_data(table, limit)
    return [dict(zip(columns, row)) for row in data]

@mcp.tool()
def execute_query(query: str) -> List[Dict[str, Any]]:
    """STEP 3: Execute a SQL query after understanding the schema and data.
    
    IMPORTANT: Before using this tool:
    1. First call get_database_schema() to understand available tables and columns
    2. Optionally use get_table_sample() to see example data
    3. Then construct and execute your SQL query
    
    Args:
        query: A valid SQL query string (SELECT, INSERT, UPDATE, DELETE)
    
    Returns a list of dictionaries where each dictionary represents a row in the result.
    """
    return db.execute_query_as_dict(query)
