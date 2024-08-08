import mysql.connector

# Connect to the database using read-only user credentials
cnx = mysql.connector.connect('<SQL CREDS>')

cursor = cnx.cursor()

# # Query to get all database names
# cursor.execute("SHOW DATABASES")
# databases = cursor.fetchall()

# # Iterate through the databases and print their names
# print("Databases available:")
# for (database_name,) in databases:
#     print(f" - {database_name}")

# # Close the cursor and connection
# cursor.close()
# cnx.close()


# Query to get all table names
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

# Iterate through the tables and get their columns
for (table_name,) in tables:
    print(f"Table: {table_name}")
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()
    for column in columns:
        print(f" - Column: {column[0]}, Type: {column[1]}")

# Close the cursor and connection
cursor.close()
cnx.close()
