import cairo
from abc import ABC, abstractmethod
from .utils import get_rgb


def save_restore(func):
    def func_wrapper(self, ctx):
        ctx.save()
        func(self, ctx)
        ctx.restore()

    return func_wrapper


def filler(func):
    def func_wrapper(self, ctx: cairo.Context):
        func(self, ctx)

        if self.fill:
            ctx.set_source_rgb(*self.fill_color)
            if self.stroke:
                ctx.fill_preserve()
            else:
                ctx.fill()

        if self.stroke:
            ctx.set_line_width(self.stroke_width)
            ctx.set_source_rgb(*self.stroke_color)
            ctx.stroke()

    return func_wrapper


def parse_bool(value, default):
    return value if value is not None else default


class Shape(ABC):
    DEFAULT_FILL = True
    DEFAULT_STROKE = True
    DEFAULT_FILL_COLOR = 'black'
    DEFAULT_STROKE_COLOR = 'black'
    DEFAULT_STROKE_WIDTH = 3

    def __init__(self, *args, **kwargs):
        self.fill = parse_bool(kwargs.get('fill'), self.DEFAULT_FILL)
        self.stroke = parse_bool(
            kwargs.get('stroke'), self.DEFAULT_STROKE)

        if not self.fill and not self.stroke:
            raise ValueError("Invisible object with no fill and no stroke")

        self.fill_color = kwargs.get('color') or kwargs.get(
            'fill_color') or self.DEFAULT_FILL_COLOR
        self.stroke_color = kwargs.get(
            'stroke_color') or self.DEFAULT_STROKE_COLOR
        self.stroke_width = kwargs.get(
            'stroke_width') or self.DEFAULT_STROKE_WIDTH

        self.process_colors()

    def process_colors(self):
        self.fill_color = get_rgb(self.fill_color)
        self.stroke_color = get_rgb(self.stroke_color)

    @abstractmethod
    def draw_on(self, ctx) -> None:
        raise NotImplementedError
