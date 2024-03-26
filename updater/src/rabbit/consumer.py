import logging

from aiogram import Bot
from rabbit.consumer import RabbitMQAsyncConsumer
from updater.src.updater import Updater

from app.config import Config


# TODO: move to bot logic to separate service
config = Config()
logger = logging.getLogger(__name__)
bot = Bot(token=config.TELEBOT_TOKEN)


class UpdaterRabbitConsumer(RabbitMQAsyncConsumer):
    def __init__(self, queue_name, rabbitmq_url, updater: Updater):
        super().__init__(queue_name, rabbitmq_url)
        self.updater = updater
        self.actions = {
            "directions": {
                "check_running": self.updater.states.is_location_updater_running,
                "run": self.updater.run_locations,
                "start_message": "Команда выполнена. Обновление Направлений запущено.",
                "complete_message": "Обновление таблицы Направлений завершено",
            },
            "persons": {
                "check_running": self.updater.states.is_location_updater_running,
                "run": self.updater.run_persons,
                "start_message": "Команда выполнена. Обновление Человеков запущено.",
                "complete_message": "Обновление таблицы Человеков завершено",
            },
        }

    async def callback(self, message):
        try:
            json_message = await super().callback(message)
            table = json_message.get("table")  # TODO: add pydantic model
            user_id = json_message.get("user_id")
            logger.info("message:", json_message)

            if table in self.actions:
                action = self.actions[table]
                if not action["check_running"]():
                    logger.info("start updating " + table)
                    await bot.send_message(user_id, action["start_message"])
                    await action["run"]()
                    await bot.send_message(user_id, action["complete_message"])
                else:
                    logger.info(f"{table} updater is already running")
                    await bot.send_message(
                        user_id, "Отмена команды. Обновление было запущено ранее."
                    )
            else:
                logger.warning(f"No action defined for table {table}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
