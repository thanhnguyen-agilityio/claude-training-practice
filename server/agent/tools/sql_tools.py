"""
Tools use from SQLDatabase toolkit:
- info_tool: Fetch the available tables in the database (use as it is)
- list_tool: Fetch the available tables in the database (use as it is)
- query_tool: Execute the query and fetch result OR return an error message if the query fails

Tools custom:
- check_and_execute_query_tool:
    Double check if the query is correct before executing it -> call query_tool in code (not through agent to reduce token usage)
"""

from agent.llms import model
from langchain_community.tools.sql_database.prompt import QUERY_CHECKER
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLDatabaseTool,
)
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from utils.utils import get_path

db_path = get_path("ecommerce_store.db", "db")
db = SQLDatabase.from_uri(
    f"sqlite:///{db_path}",
    # No sample to avoid issue on sample url image not correct
    sample_rows_in_table_info=0,
)
# print("TEST DATABASE:::::::::::::", db.run("SELECT * FROM Product LIMIT 2;"))
sql_db_list_tables = ListSQLDatabaseTool(
    db=db,
    description="""
    Get database table names
    Input is an empty string, output is a comma-separated list of tables in the database. Call this only if table names are unknown.
    """,
)
sql_db_schema = InfoSQLDatabaseTool(
    db=db,
    description=(
        "Get the schema and sample rows for the specified SQL tables."
        "Example input: 'table1, table2, table3'"
        "Use after verifying table names."
        "Prerequisite: Call sql_db_list_tables first if tables are unknown."
    ),
)


@tool
def check_and_execute_query_tool(query: str) -> str:
    """
    Validate and execute SQL queries.

    Requirements:
    - Prior calls to sql_db_list_tables and sql_db_schema.
    - Ensure SQL syntax correctness.

    Example query: "SELECT * FROM Product WHERE name LIKE '%cotton%';"

    Returns: Query result or error for retry.
    """

    query_tool = QuerySQLDatabaseTool(
        db=db,
        description="""
        Execute a SQL query against the database and get back the result.
        If the query is not correct, an error message will be returned.
        If an error is returned, rewrite the query, check the query, and try again.
        If empty result is returned, check the query and try again to expand search result, use LIKE %query%.
        """,
    )

    query_check_prompt = PromptTemplate(
        template=QUERY_CHECKER, input_variables=["dialect", "query"]
    )

    query_checker_chain = query_check_prompt | model.bind_tools(
        [query_tool], tool_choice="required"
    )

    # Run the query checker chain
    result_query_checker = query_checker_chain.invoke(
        {"query": query, "dialect": db.dialect}
    )

    # Call db_query_tool if the query is correct
    tool_calls = result_query_checker.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call["name"] == query_tool.name:
                return query_tool.invoke(tool_call["args"])

    return result_query_checker
