def generate_sql_node(state):
    result = sql_chain.invoke({
        "schema_context": state["schema_context"],
        "question": state["question"]
    })
    return {"generated_sql": result.content}
