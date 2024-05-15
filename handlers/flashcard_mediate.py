from aiogram import Router, F, Bot
from aiogram.types import Message, BotCommand
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.markup_keyboards import (
    reply_kb_flashcard_create_menu,
    reply_kb_flashcard_start_menu,
    reply_kb_reminder_menu
)

from keyboards.menu_strings import (
    TEXT_BUTTON_REMINDER_MENU,
    TEXT_BUTTON_CREATION_MENU,
    TEXT_BUTTON_EXIT_A_MENU
)

mediate = Router()


async def start_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'Выберите действие:',
        reply_markup=reply_kb_flashcard_start_menu()
    )


@mediate.message(Command('start'))
async def command_start(message: Message, state: FSMContext):
    await start_menu(message, state)


@mediate.message(Command('end'))
async def command_end(message: Message, state: FSMContext):
    await start_menu(message, state)


@mediate.message(F.text == TEXT_BUTTON_EXIT_A_MENU)
async def back_button(message: Message):
    await message.answer(
        'Выберите действие:',
        reply_markup=reply_kb_flashcard_start_menu()
    )


@mediate.message(F.text == TEXT_BUTTON_REMINDER_MENU)
async def reminder_menu(message: Message):
    await message.answer(
        'В этом меню вы можете настроить свои напоминания.',
        reply_markup=reply_kb_reminder_menu()
    )


@mediate.message(F.text == TEXT_BUTTON_CREATION_MENU)
async def creation_menu(message: Message):
    await message.reply(
        'В этом меню вы можете создавать или удалять свои собственные флэш-карты.',
        reply_markup=reply_kb_flashcard_create_menu()
    )


async def menu_commands(bot: Bot):
    commands = [
        BotCommand(command='/end', description='Выйти из любого меню.'),
        BotCommand(command='/start', description='Открыть меню бота.')
    ]
    await bot.set_my_commands(commands)
