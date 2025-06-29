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
