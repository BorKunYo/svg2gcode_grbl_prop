"""G-code emitted at the start of processing the SVG file"""
preamble = "G90"


"""G-code emitted at the end of processing the SVG file"""
postamble = "(postamble)"

"""G-code emitted before processing a SVG shape"""
shape_preamble = "(shape preamble)"
#shape_preamble = "Z0"

"""G-code emitted after processing a SVG shape"""
shape_postamble = "(shape postamble)"
#shape_postamble = "Z100)"

"""Workspace width mm"""
workspace_max_x = 420

"""Workspace height in mm"""
workspace_max_y = 600

""" 
Used to control the smoothness/sharpness of the curves.
Smaller the value greater the sharpness. Make sure the
value is greater than 0.1

"""
smoothness = 1

""" height that the z axis will use to travel between strokes """
zTravel = 0

""" height that the z axis will use to draw """
zDraw = -50

""" feed rate """
feed_rate = 4000

""" decimal precision of gcode"""
precision = 4


""" scale gcode to fit bed size"""
auto_scale = True

""" optimize path - slow for large files"""
optimise = True

""" should home in x and y at the end? """
home_when_done = False

""" 
illustrator exports svg's in points, not mm
set to "mm" if you don't want to convert to mm
"""
#units = "points"
units = "mm"