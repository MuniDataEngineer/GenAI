import google.generativeai as genai
import chromadb
#from chromadb.config import Settings
from functions import *
#from schema_list import schema

#configuring vectordb:
'''client = chromadb.PersistentClient(path="./chroma_schema_db")
collection = client.get_or_create_collection(name="schema_collection")  #you can change the name of the collection'''

#Getting API key:
API_KEY = input("Paste your Gemini API key here..")

#configure gemini with API key:
genai.configure(api_key=API_KEY)

#model(embeddings):
model = 'models/embedding-001'

'''#schema:
schema = schema

#schema into vectors:
schema_vect = vector_embedding(schema,model,genai)
schema_ids = vector_Id(schema)
schema_meta_data = vector_metadata(schema)

#Load schema vector into chroma db:
print("loading your schema details into chroma db....")
vector_load(schema,schema_vect,schema_ids,schema_meta_data,collection)
print("Completed...\n")'''

#asking User_query:
user_query = input(" Now I can able to answer you question ..")

#user_query into vector:
query_vector =  vector_embedding(user_query,model,genai)

#retrive schema from the db :
expected_Schema = vector_query(query_vector,collection)['documents'][0]

#return the sql query :
sql = sqlquery_generator(expected_Schema,user_query,genai)

print(sql)


