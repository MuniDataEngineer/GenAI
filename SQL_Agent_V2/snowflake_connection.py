import snowflake.connector

def connection(user,password,account,database,schema,role):
  conn = snowflake.connector.connect(
        user = user,
        password = password,
        account = account,
        database = database,
        schema = schema,
        role = role
    )
  return conn
