import aiohttp
import asyncio
import psycopg2
import json
from psycopg2.extras import execute_values
from config import SERVER, DOC_ID, GRIST_API_KEY

async def fetch_column_choices(server, doc_id, table_name, column_name, api_key):
    url = f"{server}/api/docs/{doc_id}/tables/{table_name}/columns"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                #print(data)
                # Find the column with the specified name
                for column in data['columns']:
                    if column['id'] == column_name:
                        print(column)
                        widget_options = json.loads(column['fields'].get('widgetOptions', '{}'))
                        return widget_options.get('choices', [])
                raise Exception(f"Column '{column_name}' not found")
            else:
                raise Exception(f"Failed to fetch column metadata: {response.status}")

def insert_roles_into_postgres(roles):
    # Define your PostgreSQL connection parameters
    conn_params = {
        'dbname': 'agreemod',
        'user': 'agreemod',
        'password': 'pswd',
        'host': 'localhost',
        'port': '5432'
    }
    
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    # Define the SQL query for bulk insert
    insert_query = """
    INSERT INTO participation_role (code, name) VALUES %s
    """
    
    # Prepare the data for bulk insert
    data = [(role, role) for role in roles]
    
    # Execute the bulk insert
    execute_values(cursor, insert_query, data)
    
    # Commit the transaction
    conn.commit()
    
    # Close the cursor and connection
    cursor.close()
    conn.close()

async def main():
    TABLE_NAME = "Participations"
    COLUMN_NAME = "role"
    
    # Fetch choices for the 'role' column
    choices = await fetch_column_choices(SERVER, DOC_ID, TABLE_NAME, COLUMN_NAME, GRIST_API_KEY)
    
    # Insert choices into PostgreSQL
    insert_roles_into_postgres(choices)
    
    print(f"Inserted {len(choices)} roles into PostgreSQL")

# Run the async function
asyncio.run(main())