# 💬🧠 SQL Agent (RAG-based) using Langchain and Langgraph

## 📌 Description

This project converts **natural language questions** into **SQL queries** and executes them on a **Snowflake** database. It follows the **Retrieval-Augmented Generation (RAG)** pattern by combining **vector-based schema retrieval** and **Generative AI-powered SQL generation**.

The standout feature is the use of **Chroma Vector Database** to store and retrieve **database schema** (tables, columns), which is then passed to a **Gemini-based GenAI model** for accurate SQL creation.

---

## 🌟 Why RAG?

RAG (Retrieval-Augmented Generation) enhances GenAI models by providing **contextually relevant external knowledge** during generation.

In this project:

- 🔍 **Retrieve**: Use Chroma vector DB to fetch the most relevant schema from stored embeddings
- 🧠 **Generate**: Feed the schema + user query into Gemini API to generate SQL
- 📊 **Result**: Execute the SQL on Snowflake and display the result
- 🛠️ **Framework** : Langchain and Langgraph (orchestration)

This approach improves:
- 🧠 Schema understanding
- 🗂️ SQL accuracy
- ⚡ Real-time querying flexibility

---

## 🧠 Features
- Accepts plain English queries
- Retrieves matching table/column schema using Chroma vector search
- Uses GenAI (Gemini) to generate precise SQL
- Connects and executes on Snowflake (Not only snowflake can connect any database)

---

## 🛠️ Tech Stack

- 🧠 **Gemini API** (Google GenAI)
- 🗃️ **Chroma Vector DB** (for schema embedding & retrieval)
- ❄️ **Snowflake** (Cloud Data Warehouse)
- 🔧 **Python**
- 🦜 ***Langchain*** (Framework for LLM based app)
- 🧭 ***Langgraph*** (Orchestrating Flow) 

---


## 📌 Notes
- Make sure your schema is indexed into **Chroma vector DB**
- **Gemini API key** is mandatory
- **Snowflake credentials** required for execution
- You can change the **schema details** in the `schema_list.py`
- Before cloning the repository set the env variables for API key and DB credentials refer  `nodes.py` file to get the variable names.

---


## ▶️ How to Run 
⚠️ **Important:** Run this on the notebook in Google Colab for the best experience.
1. Clone the repository :
`!git clone https://github.com/MuniDataEngineer/GenAI.git`
2. Install dependencies :
`!pip install -r /content/GenAI/SQL_Agent_V2/requirements.txt`
3. Run the main.py file :
`%run /content/GenAI/SQL_Agent_V2/main.py`

---


🌐Colab
🔗 https://colab.research.google.com/

---
