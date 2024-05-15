from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from db.db_management import (
    db_get_deletable_flashcard,
    db_delete_flashcard
)

from keyboards.markup_keyboards import (
    reply_kb_flashcard_start_menu,
    reply_kb_flashcard_create_menu
)

from keyboards.menu_strings import TEXT_BUTTON_DEL_FLASHCARD, TEXT_BUTTON_LIST_FLASHCARDS

deletion = Router()


class CardDeletion(StatesGroup):
    end = State()


def get_flashcard_info(user_id):
    """
    Создает сообщение из карт, взятых из дб для отправки при удалении/просмотре инфо
    """
    flashcards = db_get_deletable_flashcard(user_id)
    info_array = [f'{i + 1}:  {flashcard[1]}  -  {flashcard[2]}\n' for i, flashcard in enumerate(flashcards)]
    return info_array


async def display_flashcards(message: Message):
    """
    Отображает карточки пользователя
    """
    flashcard_info: list = get_flashcard_info(message.from_user.id)
    if not flashcard_info:
        await message.answer(f'У вас нет карточек.\n'
                             f'Создайте их.',
                             reply_markup=reply_kb_flashcard_start_menu())
        return

    await message.answer(f'Ваши карточки:', reply_markup=reply_kb_flashcard_create_menu())
    for card in flashcard_info:
        await message.answer(card)


@deletion.message(StateFilter(None), F.text == TEXT_BUTTON_DEL_FLASHCARD)
async def delete_start(message: Message, state: FSMContext):
    flashcards = db_get_deletable_flashcard(message.from_user.id)
    if not flashcards:
        await message.answer(f'У вас нет карточек.\n'
                             f'Создайте их.',
                             reply_markup=reply_kb_flashcard_start_menu())
        return

    await message.answer(
        f'Чтобы удалить карточку, введите её ID как на примере:\n'
        '<b>БОТ:</b> 15:    Ю. А. Гагарин - Первым совершил полет в Космос\n'
        '<b>ПОЛЬЗОВАТЕЛЬ:</b> 15\n\n'
        'Отправьте несколько ID для массового удаления:\n'
        '<b>БОТ:</b> 1: фыва - asdf по-русски\n'
        '<b>БОТ:</b> 2: asdf - фыва по-английски\n'
        '<b>ПОЛЬЗОВАТЕЛЬ:</b> 1 2',
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )
    await display_flashcards(message)
    await state.set_state(CardDeletion.end)


@deletion.callback_query(F.data == 'cancel_action')
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(f'Действие отменено..\n'
                                  f'Возвращаем вас в меню..', reply_markup=reply_kb_flashcard_start_menu())
    await state.clear()


@deletion.message(CardDeletion.end)
async def delete_end(message: Message, state: FSMContext):
    user_input = message.text
    if user_input is None:
        await message.answer('Вы не ввели ID карточки.\n'
                             'Повторите попытку.')
        await state.set_state(CardDeletion.end)
    else:
        flashcards = db_get_deletable_flashcard(message.from_user.id)
        list_id = sorted(user_input.split(), reverse=True)
        for card_id in list_id:
            if not card_id.isdigit() or int(card_id) > len(flashcards):
                await message.answer('В вашем сообщении нет ID карточки.\n'
                                     'Повторите попытку.')
                await state.set_state(CardDeletion.end)
                continue
            db_delete_flashcard(message.from_user.id, flashcards[int(card_id) - 1][1], flashcards[int(card_id) - 1][2])
            await message.reply(f'Карточка {card_id} была удалена.', reply_markup=reply_kb_flashcard_start_menu())
            await state.clear()


@deletion.message(StateFilter(None), F.text == TEXT_BUTTON_LIST_FLASHCARDS)
async def view_cards(message: Message, state: FSMContext):
    await display_flashcards(message)
    await state.clear()
