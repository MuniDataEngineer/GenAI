import google.generativeai as genai
import chromadb
from functions import *

# Load the same persistent Chroma DB
client = chromadb.PersistentClient(path="./chroma_db")

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
sql = sqlquery_generator(expected_Schema,user_query,genai,model_gen)

print(sql)


