#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET
import shapes as shapes_pkg
from shapes import point_generator
from config import *
import re
from datetime import datetime as dt
from optimise import optimise_path, get_total_non_drawing_driving_distance
from utils import *

debug = False


# todo fix total distance algorithm
# todo can we guess the units?
# todo add manual scale option
# todo add z rise option
# todo why do i need to flip?

def get_shapes(path, auto_scale=True):
    t1 = dt.now()
    svg_shapes = {'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path'}
    shapes = []
    tree = ET.parse(path)
    root = tree.getroot()

    pointRatio = 0.352778

    width = root.get('width')
    height = root.get('height')

    if width is None or height is None:
        viewbox = root.get('viewBox')
        if viewbox:
            _, _, width, height = viewbox.split()

    if width is None or height is None:
        print("Unable to get width and height for the svg")
        sys.exit(1)

    # width = float(re.sub("[^0-9]", "", width))
    # height = float(re.sub("[^0-9]", "", height))

    width = float(re.findall(r"[-+]?\d*\.\d+|\d+", width)[0])
    height = float(re.findall(r"[-+]?\d*\.\d+|\d+", height)[0])
    print("width / height        ", width, height)

    if units == "points":
        print(f'"points" units detected, applying points to mm scale factor ({pointRatio}) to width and height')
        width *= pointRatio
        height *= pointRatio

    if auto_scale:
        print("\nauto scaling")

        scale_x = workspace_max_x / width
        scale_y = workspace_max_y / height

        scale_x = min(scale_x, scale_y)
        scale_y = scale_x

        print("width / height        ", width, height)
        print("scale factor          ", scale_x, "\n")

    for elem in root.iter():

        #print(f'- trying elem {elem}')

        try:
            _, tag_suffix = elem.tag.split('}')

        except ValueError:
            continue

        if tag_suffix in svg_shapes:

            #print(f'found shape: {tag_suffix}')
            shape_class = getattr(shapes_pkg, tag_suffix)
            shape_obj = shape_class(elem)
            d = shape_obj.d_path()
            m = shape_obj.transformation_matrix()  # todo work out what d and m are

            coords = []

            if d:  # begin shape processing

                p = point_generator(d, m, smoothness)  # tuples of x y coords
                first = True

                for x, y in p:  # todo sort out this nightmare

                    if units == "points":
                        x *= pointRatio
                        y *= pointRatio

                    y = -y + height

                    if auto_scale:
                        x *= scale_x
                        y *= scale_y

                    if first:
                        coords.append((x, y))

                    else:

                        if not (x, y) == coords[-1]:
                            coords.append((x, y))

                    if first:
                        first = False

            shapes.append(coords)

    timer(t1, "parsing gcode    ")

    return shapes


def g_string(x, y, z=False, prefix="G1", p=3):
    if z is not False:
        return f"{prefix} X{x:.{p}f} Y{y:.{p}f} Z{z:.{p}f}"

    else:
        return f"{prefix} X{x:.{p}f} Y{y:.{p}f}"


def shapes_2_gcode(shapes):
    t1 = dt.now()
    with open("header.txt") as h:
        header = h.read()

    commands = [f"{header}", f'F{feed_rate}', f'{preamble}']

    for i in shapes:
        commands += ['', shape_preamble, ""]

        commands.append(g_string(i[0][0], i[0][1], zTravel, "G0", p=precision))

        for j in i:
            commands.append(g_string(j[0], j[1], zDraw, p=precision))

        commands.append(g_string(i[-1][0], i[-1][1], zTravel, "G0", p=precision))

        commands += ["", shape_postamble, ""]

    commands += [" ", postamble, ""]

    commands += ["(home)", f"G0 {zTravel}", f"G0 X0 Y0" if home_when_done else ""]

    timer(t1, "shapes_2_gcode   ")
    return commands


def write_file(output, commands):
    t1 = dt.now()
    with open(output, 'w+') as output_file:
        for i in commands:
            output_file.write(i + "\n")
    timer(t1, "writing file     ")


def find_bb(shapes):
    minx=10000000
    maxx =-10000000
    miny=100000000
    maxy=-10000000
    
    for s in shapes:
        sx, sy = s[0]
        ex, ey = s[1]

        if sx < minx:
            minx = sx
        if sx > maxx:
            maxx = sx
            
        if ex < minx:
            minx = ex
        if ex > maxx:
            maxx = ex

        if sy < miny:
            miny = sy
        if sy > maxy:
            maxy = sy

        if ey < miny:
            miny = ey
        if ey > maxy:
            maxy = ey

    return [minx, maxx, miny, maxy]


def main(file_path, output):
    shapes = get_shapes(file_path, auto_scale)

    if optimise:

        pre_distance = get_total_non_drawing_driving_distance(shapes)

        print("unoptimised distance: ", get_total_non_drawing_driving_distance(shapes))

        new_order = optimise_path(shapes, sq=True)

        post_distance = get_total_non_drawing_driving_distance(new_order)

        print("unoptimised distance: ", pre_distance)
        print("optimised distance    ", post_distance)
        print("factor:               ",
              (post_distance / pre_distance) if pre_distance > 0 else "no change, 1 shape only")

        commands = shapes_2_gcode(new_order)

        print(find_bb(new_order))

    else:

        commands = shapes_2_gcode(shapes)
        print(find_bb(shapes))

    write_file(output, commands)

    print("done")


if __name__ == "__main__":
    # file_path = "./svg/lines.svg"
    # file_path = "./svg/medium_example.svg"
    #file_path = "./svg/text.svg"
    # file_path = "./svg/example.svg"
    # file_path = "./svg/lines.svg"

    #output = "./gcode_optimised/1.gcode"

    #main(file_path, output)

    print("run by calling convert.py")
