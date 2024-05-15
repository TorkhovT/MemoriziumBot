from asyncio import create_task, sleep
from datetime import datetime, timedelta
from settings import config

from aiogram.enums import ParseMode
from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards.markup_keyboards import reply_kb_flashcard_start_menu
from keyboards.menu_strings import TEXT_BUTTON_CLEAR_REMINDER, TEXT_BUTTON_CREATE_REMINDER


reminder = Router()
bot = Bot(token=config.bot_token.get_secret_value())


class SetReminder(StatesGroup):
    choosing_type = State()
    setting_time = State()


user_tasks = {}


@reminder.message(StateFilter(None), F.text == TEXT_BUTTON_CREATE_REMINDER)
async def set_reminder(message: Message, state: FSMContext):
    await message.reply(f'Выберите тип напоминания:\n\n'
                        f'1 - Стандартные уведомления;\n'
                        f'2 - Интервальные <i>(основаны на методе интервальных повторений).</i>',
                        parse_mode=ParseMode.HTML)
    await state.set_state(SetReminder.choosing_type)


@reminder.message(SetReminder.choosing_type)
async def get_type(message: Message, state: FSMContext):
    user_message = message.text
    if user_message is None or user_message not in ['1', '2']:
        await message.reply('Неверный выбор.')
        return
    await state.update_data(reminder_type=message)
    await message.reply('Введите время напоминания в формате <b>"ЧЧ:MM"</b> <i>(в 24-часовом формате)</i>.',
                        parse_mode=ParseMode.HTML)
    await state.set_state(SetReminder.setting_time)


@reminder.message(SetReminder.setting_time)
async def get_time(message: Message, state: FSMContext):
    reminder_time = message.text.strip()

    try:
        hour, minute = map(int, reminder_time.split(':'))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError
    except ValueError:
        await message.reply(f'В вашем сообщении неправильно указано выбранное время.'
                            f'\nПожалуйста, введите время в формате "ЧЧ:ММ".')
        return

    current_time = datetime.now()
    reminder_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if reminder_time < current_time:
        reminder_time += timedelta(days=1)
    await state.update_data(reminder_time=reminder_time)

    user_id = message.from_user.id
    if user_id in user_tasks:
        user_tasks[user_id].cancel()

    data = await state.get_data()
    reminder_type = data.get('reminder_type')
    reminder_message = 'Пора учиться!'
    if reminder_type == '2':  # Метод интервальных повторений
        intervals = [1, 3, 7, 14, 30] 
        for i in intervals:
            reminder_time += timedelta(days=i)
            user_tasks[user_id] = create_task(
                send_reminder_at_time(user_id, reminder_time, reminder_message))
            
    else:  # Обычные напоминания
        user_tasks[user_id] = create_task(
            send_reminder_at_time(user_id, reminder_time, reminder_message))

    await message.reply('Напоминание установлено. Время: {}.'.format(reminder_time.strftime('%H:%M')),
                        reply_markup=reply_kb_flashcard_start_menu())
    await state.clear()


@reminder.message(F.text == TEXT_BUTTON_CLEAR_REMINDER)
async def clear_reminder(message: Message):
    user_id = message.from_user.id
    if user_id in user_tasks:
        user_tasks[user_id].cancel()
        del user_tasks[user_id]
        await message.reply('Напоминание удалено.')
    else:
        await message.reply('Нет активных напоминаний.')


async def send_reminder_at_time(user_id, reminder_time, reminder_msg):
    current_time = datetime.now()
    wait_seconds = (reminder_time - current_time).total_seconds()

    await sleep(wait_seconds)
    await bot.send_message(user_id, reminder_msg)

    reminder_time += timedelta(days=1)
    user_tasks[user_id] = create_task(send_reminder_at_time(user_id, reminder_time, reminder_msg))

    await bot.session.close()
