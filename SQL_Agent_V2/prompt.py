from langchain_core.prompts import PromptTemplate
def prompt():
  sql_prompt = PromptTemplate.from_template(
      """You are a SQL generator.
  
    Schema:
    {schema_context}
  
    Instruction:
    Convert the user request to a SQL query.
  
    User Query:
    {question}
  
    Only output the SQL query without backticks."""
  )
  sql_chain = sql_prompt | llm
  return sql_chain
