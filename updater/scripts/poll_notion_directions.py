import logging

from notion_client import Client
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.meta import PG_URL_MIGRATIONS
from app.db.repos.direction import DirectionRepo
from app.models.direction import Direction

from app.config import config

logger = logging.getLogger(__name__)

engine = create_engine(PG_URL_MIGRATIONS)

if __name__ == '__main__':
    client = Client(auth=config.notion.token)
    database_id = "0755cd9bb4ee4c09b70a2602f5ad6590"
    response = client.databases.query(
        **{
            "database_id": database_id
        }
    )

    with Session(engine) as session:
        repo = DirectionRepo(session)
        for result in response["results"]:
            try:
                data_raw = result["properties"]
                data = Direction.from_notion_data(data_raw, result.get('id'))
                repo.create_sync(data)
            except Exception as e:
                logger.critical(e)
