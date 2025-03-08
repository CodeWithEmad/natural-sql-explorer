from mysql.connector import Error, MySQLConnection
import mysql.connector
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import plotly.express as px
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DBConnection:
    host: str = os.getenv('MYSQL_HOST', 'localhost')
    port: int = int(os.getenv('MYSQL_PORT', '3306'))
    user: str = os.getenv('MYSQL_USER', 'user')
    password: str = os.getenv('MYSQL_PASSWORD', 'password')
    database: str = os.getenv('MYSQL_DATABASE', 'test_db')
    connection: Optional[MySQLConnection] = None

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except Error as e:
            print(f"Database connection error: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connection is not None and self.connection.is_connected()

class DatabaseService:
    def __init__(self):
        self._connection: Optional[DBConnection] = None

    @property
    def connection(self) -> Optional[DBConnection]:
        return self._connection

    def connect(self) -> bool:
        """Connect to the database using environment variables"""
        self._connection = DBConnection()
        return self._connection.connect()

    def get_table_structure(self) -> Dict[str, List[Tuple[str, str]]]:
        """Get the database schema including all tables and their columns"""
        if not self._connection or not self._connection.is_connected():
            raise ValueError("Database not connected")

        cursor = self._connection.connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        structure = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            structure[table_name] = [(col[0], col[1]) for col in columns]

        cursor.close()
        return structure

    def get_sample_data(self, table_name: str, limit: int = 5) -> Tuple[List[str], List[Tuple]]:
        """Get sample data from a specific table"""
        if not self._connection or not self._connection.is_connected():
            raise ValueError("Database not connected")

        cursor = self._connection.connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        sample_data = cursor.fetchall()
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [col[0] for col in cursor.fetchall()]
        cursor.close()
        return columns, sample_data

    def execute_query(self, query: str) -> Tuple[List[str], List[Tuple]]:
        """Execute a SQL query and return results with column names"""
        if not self._connection or not self._connection.is_connected():
            raise ValueError("Database not connected")

        cursor = self._connection.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        return columns, result

    def execute_query_as_dict(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results as list of dictionaries"""
        if not self._connection or not self._connection.is_connected():
            raise ValueError("Database not connected")

        cursor = self._connection.connection.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results

    def can_visualize_data(self, df: pd.DataFrame) -> bool:
        """Check if the data can be visualized based on its structure"""
        if len(df) < 2:
            return False

        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
        categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns
        temporal_cols = df.select_dtypes(include=["datetime64"]).columns

        return len(numeric_cols) > 0 and (
            len(categorical_cols) > 0 or len(temporal_cols) > 0
        )

    def suggest_visualization(self, df: pd.DataFrame, query: str) -> Optional[Dict[str, Any]]:
        """Suggest appropriate visualization based on data and query"""
        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
        categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns
        temporal_cols = df.select_dtypes(include=["datetime64"]).columns

        # Convert date strings to datetime if possible
        for col in categorical_cols:
            if df[col].dtype == "object":
                try:
                    df[col] = pd.to_datetime(df[col])
                    temporal_cols = temporal_cols.append(pd.Index([col]))
                    categorical_cols = categorical_cols.drop(col)
                except:
                    pass

        # Keywords that suggest certain chart types
        time_keywords = r"\b(time|date|month|year|daily|weekly|monthly|yearly)\b"
        comparison_keywords = r"\b(compare|comparison|versus|vs|against)\b"
        distribution_keywords = r"\b(distribution|spread|range|frequency)\b"

        # Determine chart type based on data and query
        if len(temporal_cols) > 0 and (
            re.search(time_keywords, query.lower()) or len(df) > 5
        ):
            x_col = temporal_cols[0]
            y_col = numeric_cols[0]
            fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over time")
            return {"fig": fig, "type": "line"}

        elif len(categorical_cols) > 0 and len(numeric_cols) > 0:
            if re.search(comparison_keywords, query.lower()):
                x_col = categorical_cols[0]
                y_col = numeric_cols[0]
                fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                return {"fig": fig, "type": "bar"}

            elif re.search(distribution_keywords, query.lower()):
                x_col = categorical_cols[0]
                y_col = numeric_cols[0]
                fig = px.box(
                    df, x=x_col, y=y_col, title=f"Distribution of {y_col} by {x_col}"
                )
                return {"fig": fig, "type": "box"}

            else:
                x_col = categorical_cols[0]
                y_col = numeric_cols[0]
                fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                return {"fig": fig, "type": "bar"}

        elif len(numeric_cols) >= 2:
            fig = px.scatter(
                df,
                x=numeric_cols[0],
                y=numeric_cols[1],
                title=f"{numeric_cols[1]} vs {numeric_cols[0]}",
            )
            return {"fig": fig, "type": "scatter"}

        return None

# Create a global instance
db = DatabaseService()
