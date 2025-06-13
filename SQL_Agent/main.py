import google.generativeai as genai
import chromadb
from Chroma_db import collection
from functions import *

#Getting API key:
API_KEY = input("Paste your Gemini API key here..")

#configure gemini with API key:
genai.configure(api_key=API_KEY)

#model(embeddings):
model = 'models/embedding-001'

#asking User_query:
user_query = input(" Now I can able to answer you question ..")

#user_query into vector:
query_vector =  vector_embedding(user_query,model,genai)

#retrive schema from the db :
expected_Schema = vector_query(query_vector,collection)['documents'][0]

#return the sql query :
sql = sqlquery_generator(expected_Schema,user_query,genai)

print(sql)


