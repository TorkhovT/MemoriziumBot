from emojis import encode

TEXT_BUTTON_BEGIN_STUDYING = (encode(':pencil:') + ' Начать')
TEXT_BUTTON_PREBUILT_CARDS = (encode(':floppy_disk:') + ' Встроенные карточки')
TEXT_BUTTON_CREATION_MENU = (encode(':gear:') + ' Создать флэш-карты')

TEXT_BUTTON_REMINDER_MENU = (encode(':stopwatch:') + ' Напоминания')
TEXT_BUTTON_CREATE_REMINDER = (encode(':alarm_clock: ') + ' Установить напоминание')
TEXT_BUTTON_CLEAR_REMINDER = (encode(':x:') + ' Удалить напоминание')

TEXT_BUTTON_ADD_FLASHCARD = (encode(':new:' + ' Создать флэш-карту'))
TEXT_BUTTON_DEL_FLASHCARD = (encode(':put_litter_in_its_place:') + ' Удалить флэш-карту')
TEXT_BUTTON_LIST_FLASHCARDS = (encode(':page_facing_up:' + ' Список созданных карточек'))


TEXT_BUTTON_YES = (encode(':white_check_mark:' + ' Да'))
TEXT_BUTTON_NO = (encode(':no_entry:' + ' Нет'))
TEXT_BUTTON_CORRECT = (encode(':white_check_mark:' + ' Правильный'))
TEXT_BUTTON_INCORRECT = (encode(':no_entry:' + ' Неправильный'))

TEXT_BUTTON_EXIT_A_MENU = (encode(':rewind:') + ' Выйти из меню')
TEXT_BUTTON_SHOW_BACK_SIDE = (encode(':arrows_counterclockwise:' + ' Показать обратную сторону'))

YES_CONDITIONS = ['да', 'д', 'yes', 'y', TEXT_BUTTON_YES.lower(), encode(':white_check_mark:')]
NO_CONDITIONS = ['нет', 'н', 'no', 'n', TEXT_BUTTON_NO.lower(), encode(':x1:'), encode(':no_entry:')]

EMOJI_HOURGLASS1 = encode(':hourglass_flowing_sand:')
EMOJI_HOURGLASS2 = encode(':hourglass:')
EMOJI_STATS = encode(':bar_chart:')
