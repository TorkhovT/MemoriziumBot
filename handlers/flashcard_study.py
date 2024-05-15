from os import path, listdir, remove
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile

from db.db_management import (
    db_get_flashcard_info,
    db_get_flashcard_for_stats,
    db_update_box_number
)
from image_generation.generate_img import create_photo
from keyboards.markup_keyboards import (
    reply_kb_flashcard_start_menu,
    reply_kb_start_studying_button,
    reply_kb_correct_or_incorrect_w_back,
    reply_kb_correct_or_incorrect,
    reply_kb_end_session
)
from keyboards.menu_strings import (
    TEXT_BUTTON_NO,
    NO_CONDITIONS, YES_CONDITIONS,
    TEXT_BUTTON_CORRECT, TEXT_BUTTON_INCORRECT, EMOJI_STATS,
    TEXT_BUTTON_BEGIN_STUDYING, TEXT_BUTTON_SHOW_BACK_SIDE
)

study = Router()
FRONT = 'front'  # Константа обозначения передней стороны флеш-карты
BACK = 'back'  # Обратная сторона
path_to_image_folder = 'image_generation/generated_cards/'


class Studying(StatesGroup):
    study = State()
    end = State()


def flashcard_get(user_id):
    """
    Берет флеш-карты из базы данных в виде списка.
    """
    flashcards = db_get_flashcard_info(user_id)
    if len(flashcards) == 0:
        return False
    sorted_flashcards = sorted(flashcards, key=lambda x: x[5], reverse=True)
    return sorted_flashcards


def generate_flashcard_images(card_id, card_front, card_back, user_id):
    """
    Генератор картинок флеш-карт.
    :param card_id: Если ID карты - int, то сторона карточки является лицевой; иначе - обратной
    Если есть лицевая сторона, то генерируются обе картинки сторон
    :param user_id: ID пользователя
    :param card_front: Текст передней стороны
    :param card_back: Текст обратной стороны
    :return На выходе получаем две картинки '{card_id}_{side}.png'
    """
    if isinstance(card_id, int):
        create_photo(card_front, card_id, FRONT, user_id)
        create_photo(card_back, card_id, BACK, user_id)


@study.message(StateFilter(None), F.text == TEXT_BUTTON_BEGIN_STUDYING)
async def start_message(message: Message, state: FSMContext):
    flashcards: list = flashcard_get(message.from_user.id)
    if not flashcards:
        await message.reply(f'У вас нет карточек.\n'
                            f'Создайте их или используйте встроенные.',
                            reply_markup=reply_kb_flashcard_start_menu())
        await state.clear()
        return
    await message.reply(
        f'<b>Memorizium</b> - это телеграм-бот, предназначенный для помощи в запоминании информации с помощью '
        f'флеш-карточек.',
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove())
    await message.answer(
        'Бот действует как интерактивная и автоматизированная версия обычного обучения. С его помощью вы можете '
        'создавать и использовать свои собственные флеш-карты, что поможет вам в запоминании информации.\n'
        'Нажмите на кнопку <b>"Да"</b> чтобы начать свое обучение.',
        parse_mode=ParseMode.HTML,
        reply_markup=reply_kb_start_studying_button()
    )
    await state.set_state(Studying.study)


@study.message(Studying.study)
async def studying(message: Message, state: FSMContext):
    msg = message.text
    user_id = message.from_user.id

    if msg is None:  # Не реагирует на стикеры
        pass
    else:
        msg = msg.lower()
        if msg in NO_CONDITIONS:
            await start_menu(message, state)
            return

        elif msg in YES_CONDITIONS:
            flashcards = flashcard_get(user_id)

            for card in flashcards:
                card_id, card_front, card_back, has_hint, hint, box_number = card
                generate_flashcard_images(card_id, card_front, card_back, user_id)

            await message.reply(f'Ваши карточки скоро будут отправлены..\n'
                                f'Используйте команду /end чтобы отменить изучение.')
            await state.update_data(flashcards=flashcards)
            await state.update_data(correct=[])  # Позже используется в статистике

        elif message.text == TEXT_BUTTON_CORRECT or message.text == TEXT_BUTTON_INCORRECT:
            user_data = await state.get_data()
            card_id = user_data['card_id']
            if message.text == TEXT_BUTTON_CORRECT:
                db_update_box_number(user_id, card_id, 'promote')
                correct = user_data['correct']
                correct.append(card_id)
                await state.update_data(correct=correct)
            else:
                db_update_box_number(user_id, card_id, 'demote')

            flashcards = user_data['flashcards']
            for i in range(len(flashcards)):
                if card_id == flashcards[i][0]:
                    del flashcards[i]
                    await state.update_data(flashcards=flashcards)
                    break

        elif msg == TEXT_BUTTON_SHOW_BACK_SIDE.lower():
            user_data = await state.get_data()
            card_id = user_data['card_id']
            side_path = BACK
            image_path = f'image_generation/generated_cards/{user_id}_{card_id}_{side_path}.png'
            image = FSInputFile(image_path)
            await message.answer_photo(image, caption='Обратная сторона',
                                       parse_mode=ParseMode.HTML,
                                       has_spoiler=True,
                                       reply_markup=reply_kb_correct_or_incorrect())
            return
        else:
            pass

        user_data = await state.get_data()
        usable_flashcards = user_data['flashcards']

        if usable_flashcards:
            usable_flashcards.sort(key=lambda x: x[5])
            flashcard = usable_flashcards[0]
            card_id, card_front, card_back, has_hint, hint, box_number = flashcard

            if isinstance(card_id, int):
                side = 'Лицевая сторона'
                side_path = FRONT
            else:
                side = 'Задняя сторона'
                side_path = BACK

            await state.update_data(card_id=card_id, card_back=card_back, side=side)
            image_path = f'image_generation/generated_cards/{user_id}_{card_id}_{side_path}.png'
            image = FSInputFile(image_path)

            hint_message = f'\n\nПодсказка: <tg-spoiler> →      {hint}      ← </tg-spoiler>' if has_hint else ''
            await message.answer_photo(image, caption=(f'Лицевая сторона.\n'
                                                       f'Коробка: {box_number}\n'
                                                       f'Вспомните содержание другой стороны.{hint_message}\n\n'
                                                       f'Ваш ответ был:'),
                                       parse_mode=ParseMode.HTML,
                                       reply_markup=reply_kb_correct_or_incorrect_w_back())
        else:
            await message.answer(f'Карточки закончились.\n'
                                 f'Нажмите на кнопку ниже, чтобы подвести итоги.',
                                 reply_markup=reply_kb_end_session())
            await state.set_state(Studying.end)


@study.message(Studying.end)
async def end(message: Message, state: FSMContext):
    await message.answer(f'Тренировка карточек закончена.\n'
                         f'Ваши результаты:')
    user_data = await state.get_data()
    correct_answers = user_data['correct']

    correct_strings = []
    for i, answer in enumerate(correct_answers, start=1):
        card_id = answer if isinstance(answer, int) else answer.split()[0]
        front, back, _ = db_get_flashcard_for_stats(message.from_user.id, card_id)[0][1:]
        correct_strings.append(f"{i}: {front} → {back}" if isinstance(answer, int) else f"{i}: {back} → {front}")

    await message.reply(
        f'{EMOJI_STATS} За эту сессию вы успешно усвоили: '
        f'{len(correct_answers)} понятия(-ий).\n' + '\n'.join(correct_strings),
    )

    flashcards = flashcard_get(message.from_user.id)
    for flashcard in flashcards:
        card_id = flashcard[0]
        if isinstance(card_id, int):
            for filename in listdir(path_to_image_folder):
                if filename.endswith(".png"):
                    file_path = path.join(path_to_image_folder, filename)
                    remove(file_path)

    await start_menu(message, state)


@study.callback_query(F.text == TEXT_BUTTON_NO)
async def start_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Выберите действие:",
        reply_markup=reply_kb_flashcard_start_menu()
    )
