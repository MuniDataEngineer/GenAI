from langchain_google_genai import GoogleGenerativeAIEmbeddings
from schema_list import schema 
from chroma_db.py import create_vector_store
from langgraph_orchestration import orchestration
import os


#Gemini connection
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key= os.environ["GOOGLE_API_KEY"])

#load schema from the file
schema = schema

#chromadb setup
vector_store = create_vector_store(schema,embedding_model) 

#langgraph compile
graph = orchestration()

#Invoke the chatmodel with questions
print("Hi there Now I can answer your question..\n")
question = input("What Can I help you today..\n")

result = graph.invoke({"question": question })

print(result["generated_sql"])      # See the generated SQL
print(result["query_result"])       # Final result from Snowflake





