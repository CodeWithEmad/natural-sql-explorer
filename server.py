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
    """STEP 4 (Optional): Create a Mermaid diagram from your SQL query results.
    This tool will analyze your data and create an appropriate visualization.
    
    Args:
        query: A SQL query that returns data to visualize (must be a SELECT query)
    
    Returns:
        A Mermaid diagram string that can be rendered by Claude.
    """
    # Execute query and convert to DataFrame
    results = db.execute_query_as_dict(query)
    df = pd.DataFrame(results)
    
    if df.empty:
        return "No data returned from query."
    
    # Analyze data types
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns
    
    # Create appropriate Mermaid diagram based on data
    if len(numeric_cols) >= 1 and len(cat_cols) >= 1:
        # Create a bar chart using Mermaid
        cat_col = cat_cols[0]
        num_col = numeric_cols[0]
        
        # Get top 5 categories and their values
        top_5 = df.groupby(cat_col)[num_col].sum().nlargest(5)
        
        mermaid = [
            "```mermaid",
            "pie",  # Using pie chart as it's well-supported in Mermaid
        ]
        
        # Add title
        mermaid.append(f'title {num_col} by {cat_col}')
        
        # Add data points
        for cat, val in top_5.items():
            # Clean category name for Mermaid compatibility
            cat_clean = str(cat).replace("'", "").replace('"', '')
            mermaid.append(f'"{cat_clean}" : {val:.1f}')
        
        mermaid.append("```")
        return "\n".join(mermaid)
    
    elif len(numeric_cols) >= 2:
        # Create a flowchart for numeric correlations
        mermaid = [
            "```mermaid",
            "flowchart LR",
        ]
        
        # Add correlations between numeric columns
        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i+1:]:
                corr = df[col1].corr(df[col2])
                if abs(corr) > 0.3:  # Only show meaningful correlations
                    mermaid.append(f'    {col1}-->|corr: {corr:.2f}|{col2}')
        
        mermaid.append("```")
        return "\n".join(mermaid)
    
    elif len(cat_cols) >= 1:
        # Create a flowchart showing category relationships
        mermaid = [
            "```mermaid",
            "flowchart TD",
        ]
        
        # Show category distributions
        for col in cat_cols[:2]:  # Limit to 2 columns to keep diagram readable
            value_counts = df[col].value_counts().head(5)
            mermaid.append(f'    {col}[{col}]')
            for val, count in value_counts.items():
                val_clean = str(val).replace("'", "").replace('"', '')
                mermaid.append(f'    {col} --> {val_clean}({count})')
        
        mermaid.append("```")
        return "\n".join(mermaid)
    
    return "Could not generate a visualization for this data. Try a query with numeric or categorical columns."
