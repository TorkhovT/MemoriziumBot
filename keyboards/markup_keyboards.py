from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import (
    ReplyKeyboardMarkup,
    InlineKeyboardBuilder,
    InlineKeyboardButton
)

from keyboards.menu_strings import (
    TEXT_BUTTON_BEGIN_STUDYING,
    TEXT_BUTTON_CREATION_MENU,
    TEXT_BUTTON_PREBUILT_CARDS,

    TEXT_BUTTON_REMINDER_MENU,
    TEXT_BUTTON_CREATE_REMINDER,
    TEXT_BUTTON_CLEAR_REMINDER,

    TEXT_BUTTON_SHOW_BACK_SIDE,
    TEXT_BUTTON_ADD_FLASHCARD,
    TEXT_BUTTON_DEL_FLASHCARD,
    TEXT_BUTTON_LIST_FLASHCARDS,
    TEXT_BUTTON_EXIT_A_MENU,

    TEXT_BUTTON_YES,
    TEXT_BUTTON_NO,
    TEXT_BUTTON_CORRECT,
    TEXT_BUTTON_INCORRECT
)

PLACEHOLDER_CHOOSE_AN_ACTION = 'Выберите действие:'
PLACEHOLDER_SETUP_CARDS = 'Настройте свои карточки.'
PLACEHOLDER_YOUR_ANSWER = 'Ваш ответ был:'
PLACEHOLDER_END_SESSION = 'Нажмите на кнопку, чтобы завершить текущую сессию.'


def create_keyboard(buttons, placeholder):
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True,
                                   input_field_placeholder=placeholder)
    return keyboard


def reply_kb_reminder_menu():
    buttons = [[KeyboardButton(text=TEXT_BUTTON_CREATE_REMINDER), KeyboardButton(text=TEXT_BUTTON_CLEAR_REMINDER)]]
    return create_keyboard(buttons, PLACEHOLDER_CHOOSE_AN_ACTION)


def reply_kb_yes_or_no():
    buttons = [[KeyboardButton(text=TEXT_BUTTON_YES), KeyboardButton(text=TEXT_BUTTON_NO)]]
    return create_keyboard(buttons, '')


def reply_kb_flashcard_start_menu():
    buttons = [
        [KeyboardButton(text=TEXT_BUTTON_BEGIN_STUDYING), KeyboardButton(text=TEXT_BUTTON_PREBUILT_CARDS)],
        [KeyboardButton(text=TEXT_BUTTON_CREATION_MENU), KeyboardButton(text=TEXT_BUTTON_REMINDER_MENU)],
    ]
    return create_keyboard(buttons, PLACEHOLDER_CHOOSE_AN_ACTION)


def reply_kb_flashcard_create_menu():
    buttons = [
        [KeyboardButton(text=TEXT_BUTTON_ADD_FLASHCARD), KeyboardButton(text=TEXT_BUTTON_DEL_FLASHCARD)],
        [KeyboardButton(text=TEXT_BUTTON_LIST_FLASHCARDS), KeyboardButton(text=TEXT_BUTTON_EXIT_A_MENU)],
    ]
    return create_keyboard(buttons, PLACEHOLDER_SETUP_CARDS)


def reply_kb_correct_or_incorrect_w_back():
    buttons = [
        [KeyboardButton(text=TEXT_BUTTON_CORRECT), KeyboardButton(text=TEXT_BUTTON_INCORRECT)],
        [KeyboardButton(text=TEXT_BUTTON_SHOW_BACK_SIDE)],
    ]
    return create_keyboard(buttons, PLACEHOLDER_YOUR_ANSWER)


def reply_kb_correct_or_incorrect():
    buttons = [[KeyboardButton(text=TEXT_BUTTON_CORRECT), KeyboardButton(text=TEXT_BUTTON_INCORRECT)]]
    return create_keyboard(buttons, PLACEHOLDER_YOUR_ANSWER)


def reply_kb_end_session():
    buttons = [[KeyboardButton(text='Завершить обучение.')]]
    return create_keyboard(buttons, PLACEHOLDER_END_SESSION)


def reply_kb_go_back():
    buttons = [[KeyboardButton(text='Далее')]]
    return create_keyboard(buttons, '')


def reply_kb_start_studying_button():
    buttons = [[KeyboardButton(text=TEXT_BUTTON_YES), KeyboardButton(text=TEXT_BUTTON_NO)]]
    return create_keyboard(buttons, '')


def inline_kb_cancel_action():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text='Отменить действие',
            callback_data='cancel_action'
        )
    )
    return builder.as_markup()
