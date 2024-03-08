import telebot

from app.config import Config

config = Config()
TOKEN = config.TELEBOT_TOKEN
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if message.content_type == 'text':
        bot.send_message(chat_id, f"Привет, твой идентификатор: {chat_id}")


@bot.message_handler(commands=['update_directions'])
def update_directions(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Запущен процесс синхронизации Служб и Локаций")
    # TODO:
    bot.send_message(chat_id, f"Процесс синхронизации служб успешно завершён")


@bot.message_handler(commands=['update_persons'])
def update_directions(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Запущен процесс синхронизации Человеков")
    # TODO:
    bot.send_message(chat_id, f"Процесс синхронизации Человеков завершён")


if __name__ == '__main__':
    bot.infinity_polling()
