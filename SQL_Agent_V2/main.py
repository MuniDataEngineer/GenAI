from langchain_google_genai import GoogleGenerativeAIEmbeddings
from schema_list import schema 
from chroma_db import create_vector_store
from langgraph_orchestration import orchestration
from IPython.display import Image, display
import os


#Gemini connection
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key= os.environ["GOOGLE_API_KEY"])

#load schema from the file
schema = schema

#chromadb setup
vector_store = create_vector_store(schema,embedding_model) 

#langgraph compile
graph = orchestration()

print("Flow diagram below..\n")
display(Image(graph.get_graph().draw_mermaid_png()))

#Invoke the chatmodel with questions
print("Hi there Now I can answer your question..\n")

while True:
  question = input("Ask anything about your schema..\n")

  result = graph.invoke({"question": question })

  print("\n")
  print(result["generated_sql"])      # See the generated SQL
  print("\n")
  print(result["query_result"])       # Final result from Snowflake
  









