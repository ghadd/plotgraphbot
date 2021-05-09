from markups import *
import sys
import os

from dotenv import load_dotenv, find_dotenv
from telebot import TeleBot

from plotters import GraphPlotter, FigurePlotter
from database import db, User, State, GraphPlotterModel, FigurePlotterModel
from utils import is_number, parse_shape

if not load_dotenv(find_dotenv()):
    sys.exit(1)

db.create_tables([User, GraphPlotterModel, FigurePlotterModel])

bot = TeleBot(os.getenv('BOT_TOKEN'))


@bot.message_handler(commands=['start'])
def start(msg):
    user = User.get_or_none(User.uid == msg.from_user.id)
    if not user:
        User.create(uid=msg.from_user.id)
        resp = "Welcome! I will help you with plotting graphs and geometric figures. ✍️"
    else:
        resp = "Welcome back! Try plotting something! 🎓"

    bot.send_message(
        msg.from_user.id,
        resp,
        reply_markup=get_menu_markup()
    )


@bot.message_handler(commands=['menu'], func=lambda msg: User.get_or_none(User.uid == msg.from_user.id))
def menu(msg):
    bot.send_message(
        msg.from_user.id,
        "Choose what you want to plot. 📝",
        reply_markup=get_menu_markup()
    )


def start_plotting_graph(cb):
    bot.answer_callback_query(cb.id)
    bot.delete_message(
        cb.from_user.id,
        cb.message.message_id
    )

    User.set_state(
        cb.from_user.id,
        State.ENTERING_EXPRESSION
    )

    bot.send_message(
        cb.from_user.id,
        "Cool. Send me the function, you want to plot. "
        "Now, we support one-variable functions, so you can send something like <code>sin(x)^2 + 3*x</code> "
        "<b>(note, 3*x must be used explicitly)</b>.",
        parse_mode='HTML'
    )


def start_plotting_figure(cb):
    bot.answer_callback_query(cb.id)
    bot.delete_message(
        cb.from_user.id,
        cb.message.message_id
    )

    plotter_model = FigurePlotterModel.get_or_none(
        creator=cb.from_user.id,
    )
    if not plotter_model:
        FigurePlotterModel.create(
            creator=cb.from_user.id
        )
    else:
        plotter_model.shapes = []
        plotter_model.save()

    bot.send_message(
        cb.from_user.id,
        'Choose type of your future shape',
        reply_markup=get_shapes_markup()
    )

    User.set_state(
        cb.from_user.id,
        State.CHOOSING_SHAPE
    )


@bot.callback_query_handler(func=lambda cb: cb.data in ['graph', 'figure'])
def start_plotting(cb):
    mode = cb.data
    if mode == 'graph':
        start_plotting_graph(cb)
    else:
        start_plotting_figure(cb)


@bot.message_handler(func=lambda msg: User.get_state(msg.from_user.id) == State.ENTERING_EXPRESSION)
def enter_expression(msg):
    plotter_model = GraphPlotterModel.get_or_none(
        creator=msg.from_user.id,
    )
    if not plotter_model:
        GraphPlotterModel.create(
            creator=msg.from_user.id,
            expression=msg.text
        )
    else:
        plotter_model.expression = msg.text
        plotter_model.save()

    bot.send_message(
        msg.from_user.id,
        "Now, it's time to set your graph parameters.",
    )

    bot.send_message(
        msg.from_user.id,
        f"Current setup:\n<code>{GraphPlotterModel.get_plotter_settings(msg.from_user.id)}</code>",
        reply_markup=get_modification_markup(),
        parse_mode='HTML'
    )

    User.set_state(
        msg.from_user.id,
        State.TUNING_GRAPH
    )


@bot.callback_query_handler(func=lambda cb: cb.data in ['xlim', 'ylim', 'xlab', 'ylab', 'title', 'proceed'])
def handle_setting(cb):
    if cb.data == 'xlim':
        new_state = State.SETTING_XLIM
        resp = "Ok, now send me new boundaries for <b>x</b> (comma separated), (ex. «-5, 5»). 🛠"

    if cb.data == 'ylim':
        new_state = State.SETTING_YLIM
        resp = "Ok, now send me new boundaries for <b>y</b> (comma separated), (ex. «-5, 5»). 🛠"

    if cb.data == 'xlab':
        new_state = State.SETTING_XLAB
        resp = "Ok, now send me a new label for <b>x</b>. 🛠"

    if cb.data == 'ylab':
        new_state = State.SETTING_YLAB
        resp = "Ok, now send me a new label for <b>y</b>. 🛠"

    if cb.data == 'title':
        new_state = State.SETTING_TITLE
        resp = "Ok, not send me a new title for your graph. 🛠"

    if cb.data == 'proceed':
        new_state = State.NEUTRAL
        resp = "Here is your graph! ✅"

    if cb.data == 'proceed':
        finalize_graph(cb)
    else:
        bot.send_message(
            cb.from_user.id,
            f"Current setup:\n<code>{GraphPlotterModel.get_plotter_settings(cb.from_user.id)}</code>",
            parse_mode='HTML'
        )
        bot.send_message(
            cb.from_user.id,
            resp,
            parse_mode='HTML'
        )

    bot.answer_callback_query(
        cb.id
    )
    bot.delete_message(
        cb.from_user.id,
        cb.message.message_id
    )

    User.set_state(
        cb.from_user.id,
        new_state
    )


def parse_limit(limit_text):
    limit = limit_text.split(", ")
    if len(limit) == 2:
        lower, upper = limit
        if is_number(lower) and is_number(upper):
            return float(lower), float(upper)


@bot.message_handler(func=lambda msg: User.get_state(msg.from_user.id) in [
    State.SETTING_XLIM,
    State.SETTING_YLIM,
    State.SETTING_XLAB,
    State.SETTING_YLAB,
    State.SETTING_TITLE
])
def change_parameter(msg):
    state = User.get_state(msg.from_user.id)
    if state in [State.SETTING_XLIM, State.SETTING_YLIM]:
        limit = parse_limit(msg.text)
        if limit:
            if state == State.SETTING_XLIM:
                GraphPlotterModel.update(
                    xlim=limit
                ).execute()
            else:
                GraphPlotterModel.update(
                    ylim=limit
                ).execute()
        else:
            bot.send_message(
                msg.from_user.id,
                "Unfortunately, I could not parse this limit. 😔"
            )

    else:
        if state == State.SETTING_XLAB:
            GraphPlotterModel.update(
                xlab=msg.text
            ).execute()
        if state == State.SETTING_YLAB:
            GraphPlotterModel.update(
                ylab=msg.text
            ).execute()
        if state == State.SETTING_TITLE:
            GraphPlotterModel.update(
                title=msg.text
            ).execute()

    bot.send_message(
        msg.from_user.id,
        f"Current setup:\n<code>{GraphPlotterModel.get_plotter_settings(msg.from_user.id)}</code>",
        reply_markup=get_modification_markup(),
        parse_mode='HTML'
    )

    User.set_state(
        msg.from_user.id,
        State.TUNING_GRAPH
    )


def finalize_graph(msg):
    success = True
    try:
        plotter = GraphPlotterModel.get_plotter(msg.from_user.id)
        plotter.plot()
        filename = plotter.save_plot()
    except (SyntaxError, ValueError, TypeError):
        success = False

    if success:
        bot.send_photo(
            msg.from_user.id,
            open(filename, 'rb').read(),
            caption=f"#plot <code>{plotter.expression}</code>",
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            msg.from_user.id,
            "Could not parse that expression. Try again. 😔"
        )


@bot.callback_query_handler(func=lambda cb: User.get_state(cb.from_user.id) == State.CHOOSING_SHAPE)
def choose_shape(cb):
    bot.answer_callback_query(cb.id)
    bot.delete_message(
        cb.from_user.id,
        cb.message.message_id
    )

    if cb.data == 'proceed-figure':
        finalize_figure(cb)
        return

    FigurePlotterModel.update(
        current_shape_type=cb.data
    ).where(
        FigurePlotterModel.creator == cb.from_user.id
    ).execute()

    hint = "No hint"
    if cb.data == 'line':
        hint = "[(100, 100), (200, 200)] will draw a line from the point (100, 100) to the point (200, 200)."
    elif cb.data == 'rectangle':
        hint = "[(100, 100), (200, 200)] will draw a rectangle (a square) with top-left corner at the point (100, 100)" \
               " and width&height of 200 and 200 respectively.\n\n" \
               "[(100, 100), 200] will draw the same square."
    elif cb.data == 'ellipse':
        hint = "[(100, 100), (200, 200), 45] will draw an ellipse with center at the point (100, 100)," \
               " diameters of 200 and 200 respectively, rotated 45deg. clockwise.\n\n" \
               "[(100, 100), 200, 45] and [(100, 100), 200] will draw the same circle."
    elif cb.data == 'polygon':
        hint = "[(100, 100), (200, 200), (150, 150)] will draw a polygon with given points."

    bot.send_message(
        cb.from_user.id,
        "Alright, now, enter properties of your future shape.\n"
        "Hint:\n"
        f"<code>{hint}</code>",
        parse_mode='HTML'
    )

    User.set_state(
        cb.from_user.id,
        State.ENTERING_SHAPE_PROPS
    )


@bot.message_handler(func=lambda msg: User.get_state(msg.from_user.id) == State.ENTERING_SHAPE_PROPS)
def enter_shape_props(msg):
    painter_model = FigurePlotterModel.get_or_none(
        creator=msg.from_user.id,
    )
    current_shape_type = painter_model.current_shape_type

    try:
        shape = parse_shape(current_shape_type, msg.text)
    except (AssertionError, SyntaxError, ValueError, TypeError):
        bot.send_message(
            msg.from_user.id,
            "This is invalid, please try again."
        )
        return

    FigurePlotterModel.update(
        current_shape=shape,
    ).where(
        FigurePlotterModel.creator == msg.from_user.id
    ).execute()

    shape_style_markup = get_shape_style_markup(**painter_model.style_config)
    bot.send_message(
        msg.from_user.id,
        "Cool, now fit styling of your shape",
        reply_markup=shape_style_markup
    )

    User.set_state(
        msg.from_user.id,
        State.EDITING_STYLE
    )


@bot.callback_query_handler(func=lambda msg: User.get_state(msg.from_user.id) == State.EDITING_STYLE)
def edit_style(cb):
    bot.answer_callback_query(cb.id)

    painter_model = FigurePlotterModel.get_or_none(
        creator=cb.from_user.id,
    )
    config = painter_model.style_config

    if cb.data == 'proceed-shapes':
        shape = painter_model.current_shape
        for k, v in config.items():
            setattr(shape, k, v)
        shape.process_colors()
        painter_model.shapes.append(shape)
        painter_model.save()

        painter = FigurePlotterModel.get_painter(cb.from_user.id)
        painter.add_shape(shape)
        filename = painter.save_figure()

        bot.send_photo(
            cb.from_user.id,
            open(filename, 'rb').read(),
            caption="Here is your painting at the moment!"
        )

        bot.send_message(
            cb.from_user.id,
            'Choose type of your future shape',
            reply_markup=get_shapes_markup()
        )

        User.set_state(
            cb.from_user.id,
            State.CHOOSING_SHAPE
        )
        return

    resp = ''
    new_state = State.EDITING_STYLE

    if cb.data in ['fill', 'stroke']:
        config[cb.data] ^= True
    elif cb.data == 'fill_color':
        resp = "Choose fill color"
        new_state = State.SETTING_FILL_COLOR
    elif cb.data == 'stroke_color':
        resp = "Choose stroke color"
        new_state = State.SETTING_STROKE_COLOR
    elif cb.data == 'stroke_width':
        resp = "Choose stroke width"
        new_state = State.SETTING_STROKE_WIDTH

    if resp:
        bot.delete_message(
            cb.from_user.id,
            cb.message.message_id
        )

        bot.send_message(
            cb.from_user.id,
            resp
        )

        User.set_state(
            cb.from_user.id,
            new_state
        )
    else:
        FigurePlotterModel.update(
            style_config=config
        ).where(
            FigurePlotterModel.creator == cb.from_user.id
        ).execute()

        bot.edit_message_reply_markup(
            cb.from_user.id,
            cb.message.message_id,
            reply_markup=get_shape_style_markup(**config)
        )


@bot.message_handler(func=lambda msg: User.get_state(msg.from_user.id) in [State.SETTING_FILL_COLOR,
                                                                           State.SETTING_STROKE_COLOR,
                                                                           State.SETTING_STROKE_WIDTH])
def set_style_prop(msg):
    state = User.get_state(msg.from_user.id)
    new_value = msg.text
    if state == State.SETTING_STROKE_WIDTH:
        new_value = float(new_value)

    field = 'fill_color' if state == State.SETTING_FILL_COLOR else 'stroke_color' \
        if state == State.SETTING_STROKE_COLOR else 'stroke_width'

    painter_model = FigurePlotterModel.get_or_none(
        creator=msg.from_user.id,
    )
    config = painter_model.style_config

    config[field] = new_value
    FigurePlotterModel.update(
        style_config=config
    ).where(
        FigurePlotterModel.creator == msg.from_user.id
    ).execute()

    bot.send_message(
        msg.from_user.id,
        "OK.",
        reply_markup=get_shape_style_markup(**config)
    )

    User.set_state(
        msg.from_user.id,
        State.EDITING_STYLE
    )


def finalize_figure(msg):
    painter = FigurePlotterModel.get_painter(msg.from_user.id)
    filename = painter.save_figure()

    bot.send_document(
        msg.from_user.id,
        open(filename, 'rb').read(),
        caption='Here is your final figure!',
        thumb=open(filename, 'rb').read()
    )


if __name__ == "__main__":
    bot.polling(none_stop=True)
