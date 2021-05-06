from os import stat
from peewee import *
import jsonpickle

from plotters import GraphPlotter

db = SqliteDatabase("plotterbot.sqlite")


class JSONField(TextField):
    def db_value(self, value):
        return jsonpickle.dumps(value)

    def python_value(self, value):
        if value is not None:
            return jsonpickle.loads(value)


class State:
    NEUTRAL = 0
    ENTERING_EXPRESSION = 1
    TUNING_GRAPH = 2
    SETTING_XLIM = 3
    SETTING_YLIM = 4
    SETTING_XLAB = 5
    SETTING_YLAB = 6
    SETTING_TITLE = 7


class User(Model):
    uid = IntegerField(primary_key=True)
    state = IntegerField(default=State.NEUTRAL)

    # graph_plotter = ForeignKeyField(GraphPlotterModel, null=True)
    # figure_plotter = ForeignKeyField(FigurePlotterModel, null=True)

    @staticmethod
    def set_state(uid, new_state):
        User.update(
            state=new_state
        ).where(
            User.uid == uid
        ).execute()

    @staticmethod
    def get_state(uid):
        return User.get(User.uid == uid).state

    class Meta:
        database = db


class GraphPlotterModel(Model):
    creator = ForeignKeyField(User)
    expression = CharField()

    xlim = JSONField(default=(-10, 10))
    ylim = JSONField(null=True)
    xlab = CharField(default='x')
    ylab = CharField(default='y')
    title = CharField(default='Plot')

    @staticmethod
    def get_plotter(uid):
        gpm = GraphPlotterModel.get(
            GraphPlotterModel.creator == uid
        )

        gp = GraphPlotter(
            expression=gpm.expression,
            xlim=gpm.xlim,
            ylim=gpm.ylim,
            xlab=gpm.xlab,
            ylab=gpm.ylab,
            title=gpm.title
        )

        return gp

    @staticmethod
    def get_plotter_settings(uid):
        gpm = GraphPlotterModel.get(
            GraphPlotterModel.creator == uid
        )

        return f"Expression: {gpm.expression}\n" + \
               f"X boundaries: {gpm.xlim or 'Not set'}\n" + \
               f"Y boundaries: {gpm.ylim or 'Not set'}\n" + \
               f"X label: «{gpm.xlab}»\n" + \
               f"Y label: «{gpm.ylab}»\n" + \
               f"Graph title: «{gpm.title}»\n"

    class Meta:
        database = db


class FigurePlotterModel(Model):
    pass
