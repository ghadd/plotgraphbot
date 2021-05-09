import cairo
from .painting import Shape, Rectangle

from pathlib import Path
from tempfile import gettempdir
from uuid import uuid1


class FigurePlotter:
    DEFAULT_WIDTH = 600
    DEFAULT_HEIGHT = 600
    DEFAULT_BG = 'white'

    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, **kwargs):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.context = cairo.Context(self.surface)

        self.width = width
        self.height = height

        self.bg = kwargs.get('bg') or self.DEFAULT_BG
        self.shapes = []

        self.add_shape(Rectangle(
            0, 0, self.width, self.height, fill_color=self.bg
        ))

        load_shapes = kwargs.get('shapes')
        if load_shapes:
            for shape in load_shapes:
                self.add_shape(shape)

    def add_shape(self, shape: Shape):
        self.shapes.append(shape)
        shape.draw_on(self.context)

    def add_shapes(self, *args):
        for shape in args:
            self.add_shape(shape)

    def save(self, location):
        self.surface.write_to_png(location)

    def save_figure(self):
        filename = str(Path(gettempdir()) / f'{uuid1()}.png')
        print(f"Saving at {filename}")

        self.save(filename)
        return filename
