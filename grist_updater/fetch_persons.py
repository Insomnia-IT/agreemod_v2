import aiohttp
import asyncio
from config import SERVER, DOC_ID, GRIST_API_KEY
from datetime import datetime

TABLE_NAME = "People"

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
    INSERT INTO person (
        id, name, last_name, first_name, nickname, other_names, 
        telegram, phone, email, gender, birth_date, city, comment, 
        nocode_int_id, last_updated
    ) VALUES %s
    """
    #vegan - grist, diet - postgres
    #ntn_id - grist, nocode_int_id - postgres ?
    #notes - grist, NONE - postgres
    #updated_at - grist, last_updated - postgres
    #emailList - grist, NONE - postgres

    # Optimized data preparation using list comprehension
    data = [
        (
            #record['id'], #ntn_id ???
            record['fields'].get('ntn_id'), #TODO: i'm not sure this is a good idea
            record['fields'].get('name'),
            record['fields'].get('last_name'),
            record['fields'].get('first_name'),
            record['fields'].get('nickname'),
            [record['fields'].get('other_names')] if isinstance(record['fields'].get('other_names'), str)
            else record['fields'].get('other_names', []),
            record['fields'].get('Telegram'),
            record['fields'].get('phone'),
            record['fields'].get('Email'),
            record['fields'].get('gender'),
            datetime.fromtimestamp(record['fields'].get('birth_date')).strftime('%Y-%m-%d')
            if record['fields'].get('birth_date') else None,
            #record['fields'].get('vegan', False),
            record['fields'].get('city'),
            record['fields'].get('comment'),
            record['id'], #get('ntn_id'),
            #record['fields'].get('notes'),
            #record['fields'].get('created_at'),
            #record['fields'].get('updated_at'),
            #record['fields'].get('emailList', [])
            datetime.fromtimestamp(record['fields'].get('updated_at')).strftime('%Y-%m-%d')
            if record['fields'].get('updated_at') else None,
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