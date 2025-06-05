from .grist_updater import GristSync, TABLES_CONFIG
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

async def sync_loop():
    sync = GristSync()
    try:
        while True:
            print("\n--- Начало цикла синхронизации ---")
            await main_cycle(sync)
            sync._save_sync_state()
            print("--- Цикл завершен. Ожидание 30 секунд ---")
            await asyncio.sleep(30)
    except Exception as e:
        logger.error(f"Error in sync loop: {e}")
    finally:
        await sync.close_rabbitmq()

async def main_cycle(sync):
    print("Обновление ролей и статусов...")
    await sync.update_utility_data()
    
    ordered_tables = sync.order_tables_by_dependencies(TABLES_CONFIG)
    for config in ordered_tables:
        print(f"Синхронизация таблицы: {config['grist_table']}")
        await sync.sync_table(config)

if __name__ == "__main__":
    asyncio.run(sync_loop())