from langchain_chroma import Chroma

def retrieve_schema_node(state):
    vectordb = Chroma(
        collection_name="example_collection",
        persist_directory="./chroma_langchain_db",
        embedding_function=embeddings,
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
    conn = conn
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()

    # Convert to displayable format
    rows = [dict(zip(columns, row)) for row in result]
    return {"query_result": rows}
