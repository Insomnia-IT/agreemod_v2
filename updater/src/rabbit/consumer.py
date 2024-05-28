import asyncio
import logging

from aiogram import Bot
from rabbit.consumer import RabbitMQAsyncConsumer
from updater.src.config import config
from updater.src.updater import Updater


logger = logging.getLogger(__name__)


class UpdaterRabbitConsumer(RabbitMQAsyncConsumer):
    def __init__(self, queue_name, rabbitmq_url, updater: Updater):
        super().__init__(queue_name, rabbitmq_url)
        self.updater = updater
        self.bot = Bot(token=config.TELEBOT_TOKEN)

    async def callback(self, message):
        try:
            json_message = await super().callback(message)
            table = json_message.get("table")  # TODO: add pydantic model
            user_id = json_message.get("user_id")
            logger.info("message:", json_message)

            await self.process_update(table, user_id)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def process_update(self, table, user_id):
        match table:
            case "directions":
                await self.update_directions(user_id)
            case "persons":
                await self.update_persons(user_id)
            case _:
                logger.warning(f"No action defined for table {table}")

    async def update_directions(self, user_id):
        if (
            not self.updater.states.location_updating
            and not self.updater.states.all_updating
        ):
            logger.info("start updating directions")
            await self.bot.send_message(
                user_id, "Команда выполнена. Обновление Направлений запущено."
            )
            asyncio.create_task(self.updater.run_locations(user_id, self.bot))
        else:
            await self.notify_updater_running(user_id)

    async def update_persons(self, user_id):
        if (
            not self.updater.states.people_updating
            and not self.updater.states.all_updating
        ):
            logger.info("start updating persons")
            await self.bot.send_message(
                user_id, "Команда выполнена. Обновление Человеков запущено."
            )
            asyncio.create_task(self.updater.run_persons(user_id, self.bot))
        else:
            await self.notify_updater_running(user_id)

    async def notify_updater_running(self, user_id):
        logger.info("Updater is already running")
        await self.bot.send_message(
            user_id, "Отмена команды. Обновление было запущено ранее."
        )
