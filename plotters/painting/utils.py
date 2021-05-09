import cairo
from matplotlib import colors


def get_rgb(color):
    try:
        res = colors.to_rgb(color)
    except ValueError:
        res = colors.to_rgb('black')
    finally:
        return res


def get_hex_from_pattern(pat: cairo.SolidPattern):
    return colors.to_hex(pat.get_rgba())


def get_solid_pattern(color):
    pat = cairo.SolidPattern(*get_rgb(color))
    return pat
