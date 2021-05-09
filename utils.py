from ast import literal_eval

from plotters.painting import Line, Rectangle, Ellipse, Polygon


def is_number(s):
    """ Returns True is string is a number. """
    try:
        float(s)
        return True
    except ValueError:
        return False


def parse_shape(shape_type, shape_props):
    inner_data = literal_eval(shape_props)
    assert type(inner_data) == list
    for el in inner_data:
        assert type(el) in [tuple, int, float]
        if type(el) == tuple:
            assert len(el) == 2

    if shape_type == 'line':
        x1, y1 = inner_data[0]
        x2, y2 = inner_data[1]

        return Line(x1, y1, x2, y2)

    elif shape_type == 'rectangle':
        x, y = inner_data[0]
        if type(inner_data[1]) == tuple:
            w, h = inner_data[1]
        else:
            w = h = inner_data[1]

        return Rectangle(x, y, w, h)

    elif shape_type == 'ellipse':
        x, y = inner_data[0]
        if type(inner_data[1]) == tuple:
            w, h = inner_data[1]
        else:
            w = h = inner_data[1]

        angle = float(inner_data[2] if len(inner_data) == 3 else 0)

        return Ellipse(x, y, w, h, angle)

    elif shape_type == 'polygon':
        return Polygon(inner_data)
