from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List, Tuple
from db_service import db
import pandas as pd

# Create an MCP server
mcp = FastMCP("SQL Data Server")

# Try to connect to the database using environment variables
if not db.connect():
    print("Failed to connect to database using environment variables")
    exit(1)
print("Successfully connected to database")

@mcp.tool()
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

@mcp.tool()
def visualize_data(query: str) -> str:
    """STEP 4 (Optional): Create a visualization from your SQL query results.
    This tool will analyze your data and create an appropriate chart.
    
    Args:
        query: A SQL query that returns data to visualize (must be a SELECT query)
    
    Returns:
        An HTML string containing the interactive Plotly chart.
        You can display this in a web browser or in supported chat interfaces.
    """
    # Execute query and convert to DataFrame
    results = db.execute_query_as_dict(query)
    df = pd.DataFrame(results)
    
    # Get visualization suggestion
    suggestion = db.suggest_visualization(df, query)
    if suggestion:
        return suggestion['fig'].to_html(full_html=False, include_plotlyjs='cdn')
    else:
        return "Could not generate a visualization for this data. Try a different query that includes numeric and categorical/temporal columns."
