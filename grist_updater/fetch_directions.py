import aiohttp
import asyncio
from config import SERVER, DOC_ID, GRIST_API_KEY
from datetime import datetime
import uuid

#TODO: Seems that we want Teams, not directions
#TABLE_NAME = "Directions2025"
TABLE_NAME = "Teams"

TYPES_TABLE_NAME = ""

import psycopg2
from psycopg2.extras import execute_values

async def fetch_grist_table(server, doc_id, table_name, api_key):
    url = f"{server}/api/docs/{doc_id}/tables/{table_name}/records"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('records', [])
            else:
                raise Exception(f"Failed to fetch data: {response.status}")

def insert_into_postgres(records):
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
    INSERT INTO direction (
        id, name, type, first_year, last_year, nocode_int_id
    ) VALUES %s
    """

    # Optimized data preparation using list comprehension
    data = [
        (
            str(uuid.uuid4()), #TODO: notion_id in grist or sequential generation in postgres
            record['fields'].get('team_name'),
            record['fields'].get('type_of_team'),
            record['fields'].get('year_of_establishment_'),
            record['fields'].get('last_year'),
            record['id']
        )
        for record in records
    ]
    
    # Execute the bulk insert
    execute_values(cursor, insert_query, data)
    
    # Commit the transaction
    conn.commit()
    
    # Close the cursor and connection
    cursor.close()
    conn.close()

# Example usage
async def main():
    records = await fetch_grist_table(SERVER, DOC_ID, TABLE_NAME, GRIST_API_KEY)
    insert_into_postgres(records)

# Run the async function
asyncio.run(main())