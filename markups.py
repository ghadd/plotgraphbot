from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from functools import lru_cache

from plotters.painting import Line


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


@lru_cache
def get_shapes_markup():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Rectangle", callback_data="rectangle"),
        InlineKeyboardButton("Ellipse", callback_data="ellipse"),
        InlineKeyboardButton("Polygon", callback_data="polygon"),
        InlineKeyboardButton("Line", callback_data="line"),
        InlineKeyboardButton("This looks fantastic already", callback_data="proceed-figure"),
        row_width=2
    )

    return markup


@lru_cache
def get_shape_style_markup(**kwargs):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(f"Fill {'✅' if kwargs['fill'] else '🚫'}", callback_data='fill'),
        InlineKeyboardButton(f"Stroke {'✅' if kwargs['stroke'] else '🚫'}", callback_data='stroke'),
        row_width=2
    )
    markup.add(
        InlineKeyboardButton(f"Fill Color [{kwargs['fill_color']}]", callback_data='fill_color'),
        InlineKeyboardButton(f"Stroke Color [{kwargs['stroke_color']}]", callback_data='stroke_color'),
        InlineKeyboardButton(f"Stroke Width [{kwargs['stroke_width']}]", callback_data='stroke_width'),
        InlineKeyboardButton("I'm okay with current setup", callback_data='proceed-shapes'),
        row_width=1
    )

    return markup
