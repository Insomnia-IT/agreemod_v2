from grist_updater import GristSync, TABLES_CONFIG
import asyncio

import asyncio

async def sync_loop():
    sync = GristSync()
    while True:
        print("\n--- Начало цикла синхронизации ---")
        await main_cycle(sync)
        sync._save_sync_state()
        print("--- Цикл завершен. Ожидание 5 минут ---")

        await asyncio.sleep(30)

async def main_cycle(sync):
    print("Обновление ролей и статусов...")
    await sync.update_utility_data()
    
    ordered_tables = sync.order_tables_by_dependencies(TABLES_CONFIG)
    for config in ordered_tables:
        print(f"Синхронизация таблицы: {config['grist_table']}")
        await sync.sync_table(config)

if __name__ == "__main__":
    asyncio.run(sync_loop())