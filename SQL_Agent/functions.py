#text into vectors:
def vector_embedding(schema,model,genai):
  embeddings = []
  if isinstance(schema,list):
    for rows in schema:
      embedding = genai.embed_content(
                  model=model,
                  content=rows,
                  task_type="RETRIEVAL_QUERY")
      embeddings.append(embedding['embedding'])
  elif isinstance(schema,str):
    embedding = genai.embed_content(
                  model=model,
                  content=schema,
                  task_type="RETRIEVAL_QUERY")
    embeddings+=embedding['embedding']
  return embeddings


#Id creation for the schema:
def vector_Id(schema):
  ids = [f"table_{i}" for i in range(len(schema))]
  return ids

# creating meta data:
def vector_metadata(schema):
  metadata = metadata = [
    {"source": "sample_db", "owner": "System_User"} for i in schema]
  return metadata

# load the vector to vector db:
def vector_load(schema,schema_embeddings,schema_ids,schema_metadata,collection):
  collection.add(
    documents=schema,
    embeddings=schema_embeddings,
    ids=schema_ids,
    metadatas=schema_metadata
)
  return True

# query from the vector db:
def vector_query(query_vector,collection):
  results = collection.query(
    query_embeddings=[query_vector],
    n_results=3 )
  return results

#generate sql from the query:
def sqlquery_generator(retrieved_schema,query_text,genai):
  llm = genai.GenerativeModel("models/gemini-2.0-flash")

  prompt = f"""You are a SQL generator.

  Schema:
  {retrieved_schema}

  Instruction:
  Convert the user request to a SQL query.

  User Query:
  {query_text}

  Only output the SQL query without backticks.
  """

  response = llm.generate_content(prompt)
  return response.text.strip()

