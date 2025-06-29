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
