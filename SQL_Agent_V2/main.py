from snowflake_connection import connection
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from schema_list import schema 
from SQL_Agent_V2/chroma_db.py import create_vector_store
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
vector_store = create_vector_store(schema,generation_model) 




