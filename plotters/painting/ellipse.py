from math import pi
import cairo
from .shape import Shape, save_restore, filler


class Ellipse(Shape):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.x = args[0]
        self.y = args[1]
        self.w = args[2]
        self.h = args[3]
        self.angle = args[4] if len(args) > 4 else 0

    @save_restore
    @filler
    def draw_on(self, ctx: cairo.Context):
        # ctx.set_line_width(self.stroke_width)
        # ctx.set_source(self.stroke_color)

        Ellipse.path(ctx, self.x, self.y, self.w, self.h, self.angle)

        # ctx.stroke()

    @staticmethod
    def path(cr, x, y, width, height, angle=0):
        """
        x      - center x
        y      - center y
        width  - width of ellipse  (in x direction when angle=0)
        height - height of ellipse (in y direction when angle=0)
        angle  - angle in radians to rotate, clockwise
        """
        cr.save()
        cr.translate(x, y)
        cr.rotate(angle)
        cr.scale(width / 2.0, height / 2.0)
        cr.arc(0.0, 0.0, 1.0, 0.0, 2.0 * pi)
        cr.restore()
