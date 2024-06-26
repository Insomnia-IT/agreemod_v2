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
    pages = fetch_all_pages(database_id)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pages, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    notion_token = config.notion.token
    database_id = '56b5571508e046e8b0db41b3e448d557'

    notion = Client(auth=notion_token)
    output_file = 'notion_badge_database_dump.json'
    dump_database_to_json(database_id, output_file)
    print(f"Database dumped to {output_file}")
