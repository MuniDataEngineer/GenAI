from langchain_chroma import Chroma
from langchain_core.documents import Document
from uuid import uuid4

def create_vector_store(schemas: list[str],embedding_model):
  docs = [Document(page_content=s, metadata={"source": "schema"}) for s in schemas]
  uuids = [str(uuid4()) for _ in range(len(docs))]
  vector_store = Chroma(
      collection_name="example_collection",
      embedding_function=embedding_model,
      persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
  )
  vector_store.add_documents(documents=docs, ids=uuids)
  return vector_store
