from typing import List

from telebot import types


class KeyboardBuilder:
    def __init__(self):
        self._markup = types.InlineKeyboardMarkup()

    def add_row(self, *buttons: types.InlineKeyboardButton) -> 'KeyboardBuilder':
        if buttons:
            self._markup.row(*buttons)
        return self

    def add_rows(self, buttons: List[types.InlineKeyboardButton], row_width: int = 1) -> 'KeyboardBuilder':
        for i in range(0, len(buttons), row_width):
            self.add_row(*buttons[i:i + row_width])
        return self

    def build(self) -> types.InlineKeyboardMarkup:
        return self._markup

    def build_webapp(self) -> types.InlineKeyboardMarkup:
        return self._markup
