from .create_support_ticket import create_support_ticket
from .lookup_documents import lookup_documents
from .save_memory import save_memory
from .search_google_shopping import search_google_shopping
from .sql_tools import check_and_execute_query_tool, sql_db_list_tables, sql_db_schema

safe_tools = [
    lookup_documents,
    check_and_execute_query_tool,
    sql_db_list_tables,
    sql_db_schema,
    save_memory
]
sensitive_tools = [
    search_google_shopping,
    create_support_ticket,
]
sensitive_tool_names = {t.name for t in sensitive_tools}
tools_mapping = {
    "lookup_documents": lookup_documents,
    "check_and_execute_query_tool": check_and_execute_query_tool,
    "sql_db_list_tables": sql_db_list_tables,
    "sql_db_schema": sql_db_schema,
    "save_memory": save_memory,
    "search_google_shopping": search_google_shopping,
    "create_support_ticket": create_support_ticket,
}
# allow import from tools module
__all__ = [
    safe_tools,
    sensitive_tools,
    sensitive_tool_names,
    tools_mapping,
]

