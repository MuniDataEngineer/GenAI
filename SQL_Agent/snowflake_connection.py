import snowflake.connector

# Connect to your Snowflake account
def connection_snowflake(user,password,account,database,schema,role):
  return snowflake.connector.connect(
      user=user,
      password=password,
      account=account,       
      database=database,
      schema=schema,
      role=role
  )
