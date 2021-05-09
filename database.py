from os import stat
from peewee import *
import jsonpickle

from plotters import GraphPlotter, FigurePlotter

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

    CHOOSING_SHAPE = 8
    ENTERING_SHAPE_PROPS = 9
    EDITING_STYLE = 10
    SETTING_FILL_COLOR = 11
    SETTING_STROKE_COLOR = 12
    SETTING_STROKE_WIDTH = 13


class User(Model):
    uid = IntegerField(primary_key=True)
    state = IntegerField(default=State.NEUTRAL)

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
    creator = ForeignKeyField(User)
    shapes = JSONField(default=[])

    style_config = JSONField(default={
        'fill': True,
        'stroke': True,
        'fill_color': 'black',
        'stroke_color': 'black',
        'stroke_width': 3
    })

    current_shape_type = CharField(null=True)
    current_shape = JSONField(null=True)

    @staticmethod
    def get_painter(uid):
        fpm = FigurePlotterModel.get(
            FigurePlotterModel.creator == uid
        )

        fp = FigurePlotter(
            shapes=fpm.shapes
        )

        return fp

    class Meta:
        database = db
