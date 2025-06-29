from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os

chat_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key= os.environ["GOOGLE_API_KEY"])

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
  sql_chain = sql_prompt | chat_model
  return sql_chain
