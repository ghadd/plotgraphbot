from markups import *
import sys
import os

from dotenv import load_dotenv, find_dotenv
from telebot import TeleBot

from plotters import GraphPlotter
from database import db, User, State, GraphPlotterModel
from utils import is_number

if not load_dotenv(find_dotenv()):
    sys.exit(1)

db.create_tables([User, GraphPlotterModel])

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
        "Now, we support one-variable functions, so you can send something like 'sin(x)^2'."
    )


def start_plotting_figure(cb):
    bot.answer_callback_query(
        cb.id,
        "This feature is not implemented yet.",
        show_alert=True
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
    except SyntaxError:
        success = False
    except ValueError:
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


if __name__ == "__main__":
    bot.polling(none_stop=True)
