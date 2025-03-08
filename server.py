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

@mcp.tool()
def execute_query(query: str) -> List[Dict[str, Any]]:
    """Execute a SQL query and return the results as a list of dictionaries"""
    return db.execute_query_as_dict(query)

@mcp.resource("mcp://schema")
def get_database_schema() -> Dict[str, List[Tuple[str, str]]]:
    """Get the database schema including all tables and their columns"""
    return db.get_table_structure()

@mcp.tool()
def get_table_sample(table: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get sample data from a specific table with optional limit"""
    columns, data = db.get_sample_data(table, limit)
    return [dict(zip(columns, row)) for row in data]

if __name__ == "__main__":
    # For development mode
    mcp.run_dev()
