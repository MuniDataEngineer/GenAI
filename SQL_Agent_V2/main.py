from snowflake_connection import connection
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from schema_list import schema 
from chroma_db.py import create_vector_store
from langgraph_orchestration import orchestration
import getpass


#Gemini connection
API_KEY = getpass("Paste your Gemini API here")

embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key= API_KEY)
generation_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key= API_KEY)


#snowflake connection
while True:
  user = input("enter your username : \n")
  password = getpass("enter your password : \n")
  account = input("enter your Account Identifier : ex : qbavf-afgsr \n")
  database = input("enter your database : \n")
  schema = input("enter your schema : \n")
  role = input("enter your role : \n")
  try:
    conn = connection(user, password, account, database, schema, role)
    print("snowflake is connected. \n")
    break
  except Exception as e:
    print(f"Connection failed: {e}")
    print("Please re-enter the details.\n")


#load schema from the file
schema = schema

#chromadb setup
vector_store = create_vector_store(schema,embedding_model) 

#langgraph compile
graph = graph

#Invoke the chatmodel with questions
print("Hi there Now I can answer your question..\n")
question = input("What Can I help you today..\n")

result = graph.invoke({"question": question })

print(result["generated_sql"])      # See the generated SQL
print(result["query_result"])       # Final result from Snowflake





