from math import sqrt
from datetime import datetime as dt
from utils import *


def get_distance(a, b, sq=False):
    x1, y1 = a[0], a[1]
    x2, y2 = b[0], b[1]

    x = x2 - x1
    y = y2 - y1

    if sq:
        return sqrt(x * x + y * y)
    else:
        return x * x + y * y


def get_total_non_drawing_driving_distance(shapes):

    total_distance = 0

    if len(shapes) > 1:
        for current_shape, next_shape in zip(shapes[:-1], shapes[1:]):
            total_distance += get_distance(current_shape[-1], next_shape[0], sq=True)

    return total_distance


def optimise_path(shapes, sq=False):
    """
    Optimizes driving distance between shapes. Will add shapes to a new list in an order
    that minimizes the non-drawing driving. If needed will reverse the order of points
    drawn in a shape (if last point of next shape was closer to the last point of current shape
    than the first point of next shape).

    """
    t1 = dt.now()
    new_order = [shapes.pop(0)]
    l = len(shapes)
    while len(new_order) <= l:

        shortest = float("Inf")
        last = new_order[-1][-1]  # last point of last shape
        print(f' - Last = {last}')

        reverse = False
        selection = None

        for shape in shapes:

            d = get_distance(last, shape[0], sq)
            d2 = get_distance(last, shape[-1], sq)

            if d < shortest:
                shortest = d
                selection = shape
                reverse = False

            if d2 < shortest:
                shortest = d2
                reverse = True
                selection = shape

        print(f'  - Shortest found distance = {shortest} from {"reversed" if reverse else "normal"} order of new shape')

        if reverse:
            new_order.append([x for x in reversed(selection)])
        else:
            new_order.append(selection)

        shapes.remove(selection)

    timer(t1, "optimizing       ")
    return new_order
