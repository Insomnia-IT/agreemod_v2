from updater.src.notion.client import NotionClient

data = {
    "Name": "",
    "Человек": {
        "name": "TESTTESTTEST",
        "url": "TESTTESTTEST"
    },
    "Год": 2055,
    "Службы и локации": {
        "name": "TESTTESTTEST",
        "url": "TESTTESTTEST"
    },
    "Роль": "TESTTESTTEST",
    "Тип": "TESTTESTTEST"
}

write_request = {
    "Name": {
        "title": [
            {"text": {"content": data["Name"]}}
        ]
    },
    "Человек": {
        "rich_text": [
            {
                "text": {
                    "content": data["Человек"]["name"],
                    "link": {"url": data["Человек"]["url"]}
                }
            }
        ]
    },
    "Год": {
        "number": data["Год"]
    },
    "Службы и локации": {
        "rich_text": [
            {
                "text": {
                    "content": data["Службы и локации"]["name"],
                    "link": {"url": data["Службы и локации"]["url"]}
                }
            }
        ]
    },
    "Роль": {
        "select": {
            "name": data["Роль"]
        }
    },
    "Тип": {
        "select": {
            "name": data["Тип"]
        }
    }
}


async def write_database(client: NotionClient):
    db_id_participation = "9f19e90d8ef74620b5c005ddf0dea4e4"
    try:
        response = await client._client.pages.create(
            parent={"database_id": db_id_participation},
            properties=write_request,
        )
        print("Data added to Notion database successfully!")
        return response
    except Exception as e:
        print("An error occurred:", e)
