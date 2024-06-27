import datetime
import json
from notion_client import Client

from updater.src.config import config


def fetch_all_pages(database_id):
    all_pages = []
    has_more = True
    next_cursor = None

    while has_more:
        response = notion.databases.query(
            **{
                "database_id": database_id,
                "start_cursor": next_cursor
            }
        )
        all_pages.extend(response.get('results', []))
        has_more = response.get('has_more', False)
        next_cursor = response.get('next_cursor', None)

    return all_pages


def dump_database_to_json(database_id, output_file):
    now = datetime.datetime.utcnow()
    timestamp = now.strftime("%d-%m-%y-%H-%M")
    output_file_with_timestamp = f"{output_file}_{timestamp}.json"

    pages = fetch_all_pages(database_id)
    with open(f"dev/{output_file_with_timestamp}", 'w', encoding='utf-8') as f:
        json.dump(pages, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    now = datetime.datetime.utcnow()
    timestamp = now.strftime("%y-%m-%d-%H-%M")
    notion_token = config.notion.token
    database_id = '961e56d8f00e474bb3ab468c00eab53a'

    notion = Client(auth=notion_token)
    output_file = 'notion_badge_database_dump'
    dump_database_to_json(database_id, output_file)
    print(f"Database dumped to {output_file}")
