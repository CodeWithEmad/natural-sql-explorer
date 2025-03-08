import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import pandas as pd
from db_service import db
import os
# --- LangChain LLM Query Generation ---


def generate_sql_query(openai_api_key: str, schema: dict, sample_data: dict, user_request: str) -> str:
    """Generate SQL query using OpenAI LLM"""
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

# Navbar for OpenAI API key
with st.sidebar:
    st.header("Settings")
    openai_api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv('OPENAI_API_KEY', ''))

# Automatically attempt connection using environment variables
if db.connect():
    st.success("Connected to database!")
    if "connected" not in st.session_state:
        st.session_state["connected"] = True
        # Cache the structure when first connecting
        structure = db.get_table_structure()
        st.session_state["structure"] = structure
        # Cache sample data
        sample_data_dict = {}
        for table_name in structure.keys():
            cols, data = db.get_sample_data(table_name)
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
    if "connected" in st.session_state:
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
                    columns, result = db.execute_query(sql_query)
                    status.update(label="✅ Query completed!", state="complete")

                    # Format the response
                    st.markdown("### Results")
                    if result:
                        df = pd.DataFrame(result, columns=columns)
                        st.dataframe(df, use_container_width=True)
                        st.markdown(f"*Found {len(result)} results*")

                        # Try to visualize the data
                        if db.can_visualize_data(df):
                            st.markdown("### Data Visualization")
                            viz_suggestion = db.suggest_visualization(df, prompt)
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
