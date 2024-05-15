from asyncio import run
from logging import basicConfig as StartLogging, INFO

from aiogram import Bot, Dispatcher

import handlers.flashcard_mediate
import handlers.flashcard_creation
import handlers.flashcard_deletion
import handlers.flashcard_study
import handlers.preset_flashcards
import reminder.reminder

from settings import config

dp = Dispatcher()


async def main():
    dp.include_routers(
        handlers.flashcard_mediate.mediate,
        handlers.flashcard_creation.creation,
        handlers.flashcard_deletion.deletion,
        handlers.flashcard_study.study,
        handlers.preset_flashcards.preset,
        reminder.reminder.reminder
    )
    bot = Bot(token=config.bot_token.get_secret_value())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    StartLogging(level=INFO)
    run(main())
