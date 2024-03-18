import multiprocessing

from app.main import run_api
from bot.main_bot import run_bot_async
from updater.main import run_updater_async

if __name__ == "__main__":
    bot_process = multiprocessing.Process(target=run_bot_async)
    updater_process = multiprocessing.Process(target=run_updater_async)
    api_process = multiprocessing.Process(target=run_api)

    bot_process.start()
    updater_process.start()
    api_process.start()
