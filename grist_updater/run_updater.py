from grist_updater import GristSync, TABLES_CONFIG
import asyncio

from grist_updater import GristSync, TABLES_CONFIG
import asyncio

async def main():
    sync = GristSync()
    print("Начало синхронизации...")
    
        # 1. Обновляем служебные данные (роли и статусы)
    print("Обновление ролей и статусов...")
    #await sync.update_utility_data()
    print(f"Получено {len(sync.roles)} ролей и {len(sync.status_mapping)} статусов")
    
    # 2. Сортируем таблицы по зависимостям
    print("Сортировка таблиц...")
    ordered_tables = sync.order_tables_by_dependencies(TABLES_CONFIG)
    print("Порядок синхронизации:")
    for table in ordered_tables:
        print(f"   - {table['grist_table']}")
    
    # 3. Синхронизируем таблицы
    for config in ordered_tables:
        #if config["grist_table"] is not "Badges_2025":
        #    continue
        if config["grist_table"] is not "Arrivals_2025":
            continue
        print(f"Синхронизация таблицы: {config['grist_table']}")
        await sync.sync_table(config)
        print(f"Таблица {config['grist_table']} синхронизирована")
            

if __name__ == "__main__":
    asyncio.run(main())