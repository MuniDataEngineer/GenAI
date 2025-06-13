import google.generativeai as genai
import chromadb
from functions import *
from schema_list import schema

#configuring vectordb:
print("Creating Chroma Database...")
client = chromadb.PersistentClient(path="GenAI/SQL_Agent/chroma_schema_db")
collection = client.get_or_create_collection(name="schema_collection")  #you can change the name of the collection

#Getting API key:
API_KEY = input("Paste your Gemini API key here..")

print("Converting schema into vectors...")

#configure gemini with API key:
genai.configure(api_key=API_KEY)

#model(embeddings):
model = 'models/embedding-001'

#schema:
schema = schema

#schema into vectors:
schema_vect = vector_embedding(schema,model,genai)
schema_ids = vector_Id(schema)
schema_meta_data = vector_metadata(schema)

#Load schema vector into chroma db:
print("loading your schema details into chroma db....")
vector_load(schema,schema_vect,schema_ids,schema_meta_data,collection)
print("Completed...")
