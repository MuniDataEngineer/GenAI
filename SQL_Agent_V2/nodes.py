from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from snowflake_connection import connection
from prompt import prompt
import os

embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key= os.environ["GOOGLE_API_KEY"])
snow_conn = connection(os.environ["USER"],os.environ["PASSWORD"],os.environ["ACCOUNT"],os.environ["DATABASE"],os.environ["SCHEMA"],os.environ["ROLE"])
sql_chain = prompt()


def retrieve_schema_node(state):
    vectordb = Chroma(
        collection_name="example_collection",
        persist_directory="./chroma_langchain_db",
        embedding_function=embedding_model,
    )
    query = state["question"]
    doc = vectordb.similarity_search(query, k=2)
    context = "\n".join([i.page_content for i in doc])
    return {"schema_context": context}


def generate_sql_node(state):
    result = sql_chain.invoke({
        "schema_context": state["schema_context"],
        "question": state["question"]
    })
    return {"generated_sql": result.content}
  

def execute_sql_node(state):
    sql = state["generated_sql"]
    conn = snow_conn
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()

    # Convert to displayable format
    rows = [dict(zip(columns, row)) for row in result]
    return {"query_result": rows}
