import google.generativeai as genai
import chromadb
import snowflake.connector
import pandas as pd
from functions import *
from snowflake import *

# Load the same persistent Chroma DB
client = chromadb.PersistentClient(path="./chroma_schema_db")

# Access the same collection by name
collection = client.get_collection(name="schema_collection")

#Getting API key:
API_KEY = input("Paste your Gemini API key here..")

#configure gemini with API key:
genai.configure(api_key=API_KEY)

#model(embeddings):
model_emb = 'models/embedding-001'
model_gen = 'models/gemini-2.0-flash'

#collection
collection = collection

#asking User_query:
user_query = input(" Now I can able to answer you question ..")

#user_query into vector:
query_vector =  vector_embedding(user_query,model_emb,genai)

#retrive schema from the db :
expected_Schema = vector_query(query_vector,collection)['documents'][0]

#return the sql query :
sql_query = sqlquery_generator(expected_Schema,user_query,genai,model_gen)

user = input("enter your username : \n")
password = input("enter your password : \n")
account = input("enter your Account Identifier : ex : qbavf-afgsr \n")
database = input("enter your database : \n")
schema = input("enter your schema : \n")
role = input("enter your role : \n")

conn = connection_snowflake(user, password, account, database, schema, role)
print("snowflake is connected. \n")

cursor = conn.cursor()
df = pd.read_sql(sql_query, conn)

# Show table
df.head()

#closing the connection
cursor.close()
conn.close()



