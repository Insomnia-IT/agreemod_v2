from database.meta import async_session
from updater.src.db.repos.participation import ParticipationRepo
from updater.src.notion.client import NotionClient


# def convert_to_notion_object(participation):
#     properties = {
#         "Name": {
#             "title": [
#                 {
#                     "text": {
#                         "content": participation.notion_id
#                     }
#                 }
#             ]
#         },
#         "Службы и локации": {
#             "relation": [
#                 {
#                     "id": participation.direction_id.replace('-', '')
#                 }
#             ]
#         },
#         "Человек": {
#             "relation": [
#                 {
#                     "id": participation.person_id.replace('-', '')
#                 }
#             ]
#         },
#         "Год": {
#             "rich_text": [
#                 {
#                     "text": {
#                         "content": str(participation.year)
#                     }
#                 }
#             ]
#         },
#         "Роль": {
#             "select": {
#                 "name": "Бригадир" if participation.role_code == 'TEAM_LEAD' else "Other"
#             }
#         },
#         "Тип": {
#             "select": {
#                 "name": "Городская служба" if participation.status_code == 'PENDING' else "Other"
#             }
#         }
#     }

#     return properties


async def write_database(client: NotionClient, database=None):
    db_id_participation = "9f19e90d8ef74620b5c005ddf0dea4e4"
    async with async_session() as session:
        all_data = await ParticipationRepo.retrieve_all(session)

    for data in all_data:
        # converted_for_notion = convert_to_notion_object(data)
        try:
            response = await client._client.pages.create(
                parent={"database_id": db_id_participation},
                properties=data,
            )
            print("Data updated in the Notion database successfully!")
            return response
        except Exception as e:
            print("An error occurred:", e)


if __name__ == "__main__":
    import asyncio

    from updater.src.config import config

    notion = NotionClient(token=config.notion.token_write)
    asyncio.run(write_database(notion))
