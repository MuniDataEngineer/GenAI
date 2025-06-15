import google.generativeai as genai
import chromadb
from functions import *
from schema_list import schema

#schema:
schema = schema

#model(embeddings):
model = 'models/embedding-001'

#Getting API key:
API_KEY = input("Paste your Gemini API key here..")

#configure gemini with API key:
genai.configure(api_key=API_KEY)

#configuring vectordb:
print("Creating Chroma Database..\n")
client = chromadb.PersistentClient(path="./chroma_schema_db")
print("Chroma db has been created..\n")
print("Creating collection..\n")
collection = client.get_or_create_collection(name="schema_collection")  #you can change the name of the collection
print("Collection has been created..\n")

#schema into vectors:
print("Converting schema into vectors..\n")
schema_vect = vector_embedding(schema,model,genai)
schema_ids = vector_Id(schema)
schema_meta_data = vector_metadata(schema)

#Load schema vector into chroma db:
print("loading your schema details into chroma db....")
vector_load(schema,schema_vect,schema_ids,schema_meta_data,collection)
print("Completed...")
