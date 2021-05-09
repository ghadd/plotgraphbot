import cairo
from .shape import Shape, save_restore, filler


class Line(Shape):
    DEFAULT_LINE_WIDTH = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.x1 = args[0]
        self.y1 = args[1]
        self.x2 = args[2]
        self.y2 = args[3]
        self.stroke = True

    @save_restore
    @filler
    def draw_on(self, ctx: cairo.Context):
        ctx.move_to(self.x1, self.y1)
        ctx.line_to(self.x2, self.y2)
