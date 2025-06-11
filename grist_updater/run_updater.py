from grist_updater.grist_updater import GristSync, TABLES_CONFIG
import asyncio
import logging
from dotenv import load_dotenv
import random

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
        logger.error("Error in sync loop", exc_info=True)
        raise e
    finally:
        await sync.close_rabbitmq()

async def sync_table_with_retry(sync, config, max_retries=5):
    """Attempt to sync a table with retries and exponential backoff"""
    retry_count = 0
    while retry_count < max_retries:
        try:
            await sync.sync_table(config)
            return  # Success, exit the function
        except Exception as e:
            retry_count += 1
            if retry_count == max_retries:
                logger.error(f"Failed to sync table {config['grist_table']} after {max_retries} attempts", exc_info=True)
                raise  # Re-raise the last exception after all retries are exhausted
            
            # Calculate delay with exponential backoff and jitter
            delay = min(300, (2 * retry_count) + random.uniform(0, 1))
            logger.warning(f"Error syncing table {config['grist_table']}, attempt {retry_count}/{max_retries}. Retrying in {delay:.2f} seconds...")
            await asyncio.sleep(delay)

async def main_cycle(sync):
    print("Обновление ролей и статусов...")
    await sync.update_utility_data()
    
    ordered_tables = sync.order_tables_by_dependencies(TABLES_CONFIG)
    for config in ordered_tables:
        print(f"Синхронизация таблицы: {config['grist_table']}")
        await sync_table_with_retry(sync, config)

if __name__ == "__main__":
    asyncio.run(sync_loop())