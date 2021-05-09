import cairo
from .shape import Shape, save_restore, filler


class Polygon(Shape):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

        self.points = args[0]
        self.points.append(self.points[0])

    @save_restore
    @filler
    def draw_on(self, ctx: cairo.Context):
        for i in range(len(self.points) - 1):
            ctx.line_to(*self.points[i + 1])
        ctx.close_path()
