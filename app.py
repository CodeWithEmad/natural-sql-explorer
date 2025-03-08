import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import mysql.connector
from mysql.connector import Error
import pandas as pd
import plotly.express as px
from typing import Dict, Any
import re


# --- Database Connection ---
def connect_to_db(host, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        st.success("Connected to database!")
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None


# --- Tool 1: Fetch Table Structure ---
def get_table_structure(connection):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    structure = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        structure[table_name] = [
            (col[0], col[1]) for col in columns
        ]  # (column_name, data_type)
    return structure


# --- Tool 2: Extract Sample Data ---
def get_sample_data(connection, table_name, limit=5):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    sample_data = cursor.fetchall()
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    columns = [col[0] for col in cursor.fetchall()]
    return columns, sample_data


# --- Tool 3: Execute SQL Query ---
def execute_sql_query(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return columns, result


def can_visualize_data(df: pd.DataFrame) -> bool:
    """Check if the data can be visualized based on its structure."""
    # Need at least 2 rows for visualization
    if len(df) < 2:
        return False

    # Check if there are numeric or temporal columns along with categorical ones
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns
    temporal_cols = df.select_dtypes(include=["datetime64"]).columns

    return len(numeric_cols) > 0 and (
        len(categorical_cols) > 0 or len(temporal_cols) > 0
    )


def suggest_visualization(df: pd.DataFrame, query: str) -> Dict[str, Any]:
    """Suggest appropriate visualization based on data and query."""
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
        # Time series plot
        x_col = temporal_cols[0]
        y_col = numeric_cols[0]
        fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over time")
        return {"fig": fig, "type": "line"}

    elif len(categorical_cols) > 0 and len(numeric_cols) > 0:
        if re.search(comparison_keywords, query.lower()):
            # Bar chart for comparisons
            x_col = categorical_cols[0]
            y_col = numeric_cols[0]
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
            return {"fig": fig, "type": "bar"}

        elif re.search(distribution_keywords, query.lower()):
            # Box plot for distributions
            x_col = categorical_cols[0]
            y_col = numeric_cols[0]
            fig = px.box(
                df, x=x_col, y=y_col, title=f"Distribution of {y_col} by {x_col}"
            )
            return {"fig": fig, "type": "box"}

        else:
            # Default to bar chart
            x_col = categorical_cols[0]
            y_col = numeric_cols[0]
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
            return {"fig": fig, "type": "bar"}

    elif len(numeric_cols) >= 2:
        # Scatter plot for numeric relationships
        fig = px.scatter(
            df,
            x=numeric_cols[0],
            y=numeric_cols[1],
            title=f"{numeric_cols[1]} vs {numeric_cols[0]}",
        )
        return {"fig": fig, "type": "scatter"}

    return None


# --- LangChain LLM Query Generation ---
def generate_sql_query(openai_api_key, schema, sample_data, user_request):
    llm = OpenAI(api_key=openai_api_key, temperature=0)
    prompt_template = PromptTemplate(
        input_variables=["schema", "sample_data", "request"],
        template="""
        You are working with a MySQL database. Use MySQL-specific syntax.
        For date operations use:
        - DATE_SUB(NOW(), INTERVAL n MONTH/DAY/YEAR) for past dates
        - DATE_ADD(NOW(), INTERVAL n MONTH/DAY/YEAR) for future dates
        - DATEDIFF(date1, date2) for date differences

        Given the following database schema: {schema}
        And sample data: {sample_data}
        Generate a MySQL-compatible SQL query for this request: {request}

        The query must use valid MySQL syntax and functions.
        """,
    )
    prompt = prompt_template.format(
        schema=schema, sample_data=sample_data, request=user_request
    )
    sql_query = llm(prompt)
    return sql_query.strip()


# --- Streamlit App ---
st.title("Data Query Assistant")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Navbar for credentials
with st.sidebar:
    st.header("Database Credentials")
    host = st.text_input("Host", "localhost")
    user = st.text_input("User", "user")
    password = st.text_input("Password", "password", type="password")
    database = st.text_input("Database", "test_db")
    openai_api_key = st.text_input("OpenAI API Key", type="password")

# Automatically attempt connection
connection = connect_to_db(host, user, password, database)
if connection:
    if "connection" not in st.session_state:
        st.session_state["connection"] = connection
        # Cache the structure when first connecting
        structure = get_table_structure(connection)
        st.session_state["structure"] = structure
        # Cache sample data
        sample_data_dict = {}
        for table_name in structure.keys():
            cols, data = get_sample_data(connection, table_name)
            sample_data_dict[table_name] = dict(zip(cols, zip(*data)))
        st.session_state["sample_data"] = sample_data_dict

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your data..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    if "connection" in st.session_state:
        with st.chat_message("assistant"):
            structure = st.session_state["structure"]
            sample_data = st.session_state["sample_data"]

            # Show thinking effect
            with st.status("🤔 Thinking...", expanded=True) as status:
                st.write("Analyzing your question...")

                # Generate SQL query
                sql_query = generate_sql_query(
                    openai_api_key, str(structure), str(sample_data), prompt
                )
                st.write("Generated SQL query:")
                st.code(sql_query, language="sql")
                status.update(label="⚡ Executing query...", state="running")

                # Execute query and get results
                try:
                    columns, result = execute_sql_query(
                        st.session_state["connection"], sql_query
                    )
                    status.update(label="✅ Query completed!", state="complete")

                    # Format the response
                    st.markdown("### Results")
                    if result:
                        df = pd.DataFrame(result, columns=columns)
                        st.dataframe(df, use_container_width=True)
                        st.markdown(f"*Found {len(result)} results*")

                        # Try to visualize the data
                        if can_visualize_data(df):
                            st.markdown("### Data Visualization")
                            viz_suggestion = suggest_visualization(df, prompt)
                            if viz_suggestion:
                                st.plotly_chart(
                                    viz_suggestion["fig"], use_container_width=True
                                )
                                st.markdown(
                                    f"*Showing a {viz_suggestion['type']} chart based on the data structure*"
                                )
                    else:
                        st.info("No results found for your query.")

                    # Add response to chat history
                    response_text = f"I analyzed your request and here's what I found:\n\n```sql\n{sql_query}\n```\n\n{f'Found {len(result)} results.' if result else 'No results found for your query.'}"
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response_text}
                    )

                except Exception as e:
                    status.update(label="❌ Error occurred", state="error")
                    error_message = (
                        f"I encountered an error while querying the database: {str(e)}"
                    )
                    st.error(error_message)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_message}
                    )
    else:
        st.error("Please connect to the database first using the sidebar credentials.")
