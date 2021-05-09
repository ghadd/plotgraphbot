import cairo
from .shape import Shape, save_restore, filler


class Rectangle(Shape):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

        self.x = args[0]
        self.y = args[1]
        self.w = args[2]
        self.h = args[3]

    @save_restore
    @filler
    def draw_on(self, ctx: cairo.Context):
        ctx.rectangle(self.x, self.y, self.w, self.h)
