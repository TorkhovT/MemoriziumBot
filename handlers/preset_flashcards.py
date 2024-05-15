from json import load
from os import listdir, path, remove
from random import shuffle, choice

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile

from image_generation.generate_img import create_photo
from keyboards.markup_keyboards import (
    reply_kb_flashcard_start_menu,
    reply_kb_correct_or_incorrect,
    reply_kb_start_studying_button,
    reply_kb_correct_or_incorrect_w_back,
    reply_kb_end_session
)
from keyboards.menu_strings import (
    TEXT_BUTTON_NO, TEXT_BUTTON_SHOW_BACK_SIDE,
    NO_CONDITIONS, YES_CONDITIONS,
    TEXT_BUTTON_PREBUILT_CARDS
)

preset = Router()
FRONT = 'front'  # Константа обозначения передней стороны флеш-карты
BACK = 'back'  # Обратная сторона
path_to_image_folder = 'image_generation/generated_cards/'


class ViewPreset(StatesGroup):
    study_preset = State()
    end_preset = State()


def flashcard_get_from_json():
    """
    Берет встроенные флеш-карты из json файла.
    """
    with open('handlers/preset_cards.json', 'r', encoding='utf-8') as f:
        flashcards = load(f)
    return flashcards


@preset.message(StateFilter(None), F.text == TEXT_BUTTON_PREBUILT_CARDS)
async def start_message(message: Message, state: FSMContext):
    await message.answer(
        f'<b>Memorizium</b> - это телеграм-бот, предназначенный для помощи в запоминании информации с помощью '
        f'флеш-карточек.',
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove())
    await message.answer(
        'Сейчас вы находитесь в режиме <b>встроенных карточек</b>.\n'
        'Этот режим существует для ознакомления с типовым использованием возможностей бота'
        ' на примере изучения наиболее распространенных фраз испанского языка,'
        ' и поэтому <b>не включает</b> в себя ключевые учебные функции.\n'
        '\nНажмите на кнопку <b>"Да"</b> чтобы просмотреть встроенные карточки.',
        parse_mode=ParseMode.HTML,
        reply_markup=reply_kb_start_studying_button()
    )
    await state.set_state(ViewPreset.study_preset)


@preset.message(ViewPreset.study_preset)
async def studying(message: Message, state: FSMContext):
    msg = message.text
    if msg is None:  # Не реагирует на стикеры
        pass
    else:
        msg = msg.lower()

        if msg in NO_CONDITIONS:
            await start_menu(message, state)
            return

        elif msg in YES_CONDITIONS:
            flashcards: list = flashcard_get_from_json()
            shuffle(flashcards)

            for card in flashcards:
                card_id, card_front, card_back, has_hint, hint, _ = card

                if isinstance(card_id, int):
                    create_photo(card_front, card_id, FRONT, 'preset')
                    create_photo(card_back, card_id, BACK, 'preset')

            await message.answer(f'Встроенные карточки скоро будут отправлены..\n'
                                 f'Используйте команду /end чтобы отменить изучение.')
            await state.update_data(flashcards=flashcards)

        elif msg == TEXT_BUTTON_SHOW_BACK_SIDE.lower():
            user_data = await state.get_data()
            card_id = user_data['card_id']
            side_path = BACK
            image_path = f'image_generation/generated_cards/{card_id}_{side_path}.png'
            image = FSInputFile(image_path)
            await message.answer_photo(image, caption='Обратная сторона',
                                       parse_mode=ParseMode.HTML,
                                       has_spoiler=True,
                                       reply_markup=reply_kb_correct_or_incorrect())
            return
        else:
            pass

        user_data = await state.get_data()
        usable_flashcards: list = user_data['flashcards']

        if usable_flashcards:
            flashcard = choice(usable_flashcards)
            card_id, card_front, card_back, has_hint, hint, _ = flashcard

            if isinstance(card_id, int):
                side = 'Лицевая сторона'
                side_path = FRONT
            else:
                side = 'Задняя сторона'
                side_path = BACK

            await state.update_data(card_id=card_id, card_back=card_back, side=side)
            image_path = f'image_generation/generated_cards/preset_{card_id}_{side_path}.png'
            image = FSInputFile(image_path)
            hint_message = f'Подсказка: <tg-spoiler> →      {hint}      ← </tg-spoiler>' if has_hint else ''
            await message.answer_photo(image, caption=(f'{side}.\n'
                                                       f'{hint_message}\n'
                                                       f'Ваш ответ был:'),
                                       parse_mode=ParseMode.HTML,
                                       reply_markup=reply_kb_correct_or_incorrect_w_back())

            usable_flashcards.remove(flashcard)
            await state.update_data(flashcards=usable_flashcards)
        else:
            await message.answer(f'Карточки закончились.\n'
                                 f'Нажмите на кнопку ниже, чтобы подвести итоги.',
                                 reply_markup=reply_kb_end_session())
            await state.set_state(ViewPreset.end_preset)


@preset.message(ViewPreset.end_preset)
async def end(message: Message, state: FSMContext):
    await message.answer(f'Тренировка карточек закончена.')
    flashcards = flashcard_get_from_json()
    for flashcard in flashcards:
        card_id = flashcard[0]
        if isinstance(card_id, int):
            for filename in listdir(path_to_image_folder):
                if filename.endswith(".png"):
                    file_path = path.join(path_to_image_folder, filename)
                    remove(file_path)

    await start_menu(message, state)


@preset.callback_query(F.text == TEXT_BUTTON_NO)
async def start_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Выберите действие:",
        reply_markup=reply_kb_flashcard_start_menu()
    )
