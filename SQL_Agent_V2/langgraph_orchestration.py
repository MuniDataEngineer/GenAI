from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional

def orchestration():
  # Define state shape
  class GraphState(TypedDict):
      question: str
      schema_context: str
      generated_sql: str
      query_result: list
  
  builder = StateGraph(GraphState)
  
  # Add nodes
  builder.add_node("retrieve_schema", retrieve_schema_node)
  builder.add_node("generate_sql", generate_sql_node)
  builder.add_node("run_sql", execute_sql_node)
  
  # Define flow
  builder.set_entry_point("retrieve_schema")
  builder.add_edge("retrieve_schema", "generate_sql")
  builder.add_edge("generate_sql", "run_sql")
  builder.add_edge("run_sql", END)
  
  graph = builder.compile()
  return graph
