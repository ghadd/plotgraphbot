from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from functools import lru_cache


@lru_cache
def get_menu_markup():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Plot a graph", callback_data="graph"),
        InlineKeyboardButton("Plot a figure", callback_data="figure")
    )

    return markup


@lru_cache
def get_modification_markup():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Change x limit", callback_data="xlim"),
        InlineKeyboardButton("Change y limit", callback_data="ylim"),
        InlineKeyboardButton("Change x label", callback_data="xlab"),
        InlineKeyboardButton("Change y label", callback_data="ylab"),
        row_width=2
    )

    markup.add(
        InlineKeyboardButton("Change title", callback_data="title"),
        InlineKeyboardButton("I'm okay with current parameters", callback_data="proceed"),
        row_width=1
    )

    return markup
