import aiohttp
import asyncio
from config import SERVER, DOC_ID, GRIST_API_KEY
from datetime import datetime
import uuid

TABLE_NAME = "Participations"
STATUS_TABLE_NAME = "Participation_statuses"


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

def insert_into_postgres(records, status_records):
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
    INSERT INTO participation (
        id, year, role_code, status_code, person_id, direction_id
    ) VALUES %s
    """

    # Optimized data preparation using list comprehension
    data = [
        (
            str(uuid.uuid4()), #TODO: notion_id in grist or sequential generation in postgres
            record['fields'].get('year'),
            record['fields'].get('role') if record.get('role') else '4 Волонтёр',
            status_records.get(record['fields'].get('status')),
            record['fields'].get('person'),
            record['fields'].get('team')
        )
        for record in records if (record['fields'].get('person') is not 0 and record['fields'].get('team') is not 0 and isinstance(record['fields'].get('person'), int))
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
    status_records = await fetch_grist_table(SERVER, DOC_ID, STATUS_TABLE_NAME, GRIST_API_KEY)
    status_dict = {record['id']: record['fields'].get('code') for record in status_records}
    insert_into_postgres(records, status_dict)

# Run the async function
asyncio.run(main())