from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from db.db_management import (
    db_add_flashcard,
)
from keyboards.markup_keyboards import (
    reply_kb_go_back,
    reply_kb_yes_or_no,
    reply_kb_flashcard_create_menu
)
from keyboards.menu_strings import (
    TEXT_BUTTON_ADD_FLASHCARD, EMOJI_HOURGLASS1, EMOJI_HOURGLASS2,
    TEXT_BUTTON_YES, YES_CONDITIONS,
    TEXT_BUTTON_NO, NO_CONDITIONS

)

creation = Router()
MAX_LENGTH = 180


class CardCreation(StatesGroup):
    get_front_side = State()
    get_back_side = State()
    ask_hint = State()
    get_hint = State()
    end = State()


async def check_message_length(message: Message):
    """
    Проверяет длину сообщения.
    """
    user_message = message.text
    if user_message is None or len(user_message) > MAX_LENGTH:
        await message.answer(f'Произошла ошибка.\n'
                             f'Повторите попытку; ваше сообщение должно быть менее <b>{MAX_LENGTH}</b> символов.',
                             parse_mode=ParseMode.HTML)
        return False
    else:
        return True


@creation.message(StateFilter(None), F.text == TEXT_BUTTON_ADD_FLASHCARD)
async def start(message: Message, state: FSMContext):
    await message.answer(f'Введите слова или фразы <b>передней</b> стороны карточки.\n'
                         f'Максимальное количество символов - <b>{MAX_LENGTH}</b>. {EMOJI_HOURGLASS1}',
                         parse_mode=ParseMode.HTML,
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(CardCreation.get_front_side)


@creation.message(CardCreation.get_front_side)
async def middle(message: Message, state: FSMContext):
    if await check_message_length(message):
        await state.update_data(front=message.text)
        await message.answer(f'Введите слова или фразы <b>задней</b> стороны карточки.\n'
                             f'Максимальное количество символов: <b>{MAX_LENGTH}</b>. {EMOJI_HOURGLASS2}',
                             parse_mode=ParseMode.HTML)
        await state.set_state(CardCreation.get_back_side)


@creation.message(CardCreation.get_back_side)
async def intermediate(message: Message, state: FSMContext):
    if await check_message_length(message):
        await state.update_data(back=message.text)
        await message.answer(f'Включить подсказки для этой карточки?',
                             reply_markup=reply_kb_yes_or_no())
        await state.set_state(CardCreation.ask_hint)


@creation.message(CardCreation.ask_hint)
async def ask_hint(message: Message, state: FSMContext):
    msg = message.text
    if msg is None:
        pass
    else:
        msg = msg.lower()
        if msg in (YES_CONDITIONS + NO_CONDITIONS):
            allow_hint = msg in YES_CONDITIONS
            await state.update_data(allow_hint=allow_hint)
            if allow_hint:
                await message.answer(f'Напишите подсказку для своей карточки.\n\n'
                                     f'Совет:\n'
                                     f'Подсказка должна только направить к ответу, но не содержать его.\n'
                                     f'<i>Пример: (передняя сторона - подсказка - задняя сторона)\n'
                                     f'"Столица Австралии" - "Не Сидней" - "Канберра".</i>\n'
                                     f'Вы также можете использовать любой подходящий мнемонический метод.',
                                     parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
                await state.set_state(CardCreation.get_hint)
            else:
                await message.answer(f'Карточка создана.',
                                     reply_markup=reply_kb_go_back())
                await state.set_state(CardCreation.end)
        else:
            await message.answer(f'Вы должны выбрать "Да" или "Нет".')


@creation.message(CardCreation.get_hint)
async def get_hint(message: Message, state: FSMContext):
    user_data = await state.get_data()
    allow_hint = user_data.get('allow_hint', False)
    if not allow_hint:
        return
    if await check_message_length(message):
        await state.update_data(hint=message.text)
        await message.reply(f'Карточка создана.',
                            reply_markup=reply_kb_go_back())
        await state.set_state(CardCreation.end)


@creation.message(CardCreation.end)
async def end(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    allow_hint = 'hint' in user_data

    db_add_flashcard(user_id, user_data["front"], user_data["back"],
                     allow_hint, user_data.get("hint", ""))
    await message.answer(f'Информация:')
    info_message = (
        f'Передняя сторона: <b>{user_data["front"]}</b>\n'
        f'Задняя сторона: <b>{user_data["back"]}</b>\n'
        f'Включить подсказки?: <b>{TEXT_BUTTON_YES if allow_hint else TEXT_BUTTON_NO}</b>\n'
    )
    if allow_hint:
        info_message += f'Ваша подсказка: <b>{user_data["hint"]}</b>'

    await message.answer(
        info_message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_kb_flashcard_create_menu())
    await state.clear()
