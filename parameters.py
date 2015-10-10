#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Central place to store parameters / settings / variables in osm2city.
All length, height etc. parameters are in meters, square meters (m2) etc.

The assigned values are default values. The Config files will overwrite them

Created on May 27, 2013

@author: vanosten
"""

import argparse
import sys
import types
from os.path import os
from vec2d import vec2d
from pdb import pm

# default_args_start # DO NOT MODIFY THIS LINE
#=============================================================================
# PARAMETERS FOR ALL osm2city MODULES
#=============================================================================

# -- Scenery folder, typically a geographic name or the ICAO code of the airport
PREFIX = "LSZR"

# -- Boundary of the scenery in degrees (use "." not ","). The example below is from LSZR.
BOUNDARY_WEST = 9.54
BOUNDARY_SOUTH = 47.48
BOUNDARY_EAST = 9.58
BOUNDARY_NORTH = 47.50

OSM_FILE = "buildings.osm"  # -- file name of the file with OSM data. Must reside in $PREFIX
USE_PKL = False             # -- instead of parsing the OSM file, read a previously created cache file $PREFIX/buildings.pkl
IGNORE_PKL_OVERWRITE = True # -- Ignore overwriting of Cache File

# -- Full path to the scenery folder without trailing slash. This is where we
#    will probe elevation and check for overlap with static objects. Most
#    likely you'll want to use your TerraSync path here.
PATH_TO_SCENERY = "/home/user/fgfs/scenery/TerraSync"

# -- The generated scenery (.stg, .ac, .xml) will be written to this path.
#    If empty, we'll use the correct location in PATH_TO_SCENERY. Note that
#    if you use TerraSync for PATH_TO_SCENERY, you MUST choose a different
#    path here. Otherwise, TerraSync will overwrite the generated scenery.
#    Also make sure PATH_TO_OUTPUT is included in your $FG_SCENERY.
PATH_TO_OUTPUT = "/home/user/fgfs/scenery/osm2city"

NO_ELEV = False             # -- skip elevation probing
ELEV_MODE = "FgelevCaching" # -- elev probing mode. Possible values are FgelevCaching (recommended), Manual, or Telnet
FG_ELEV = '"D:/Program Files/FlightGear/bin/Win64/fgelev.exe"'

# -- Distance between raster points for elevation map. Xx is horizontal, y is
#    vertical. Relevant only for ELEV_MODE = Manual or Telnet.
ELEV_RASTER_X = 10
ELEV_RASTER_Y = 10

#=============================================================================
# PARAMETERS RELATED TO BUILDINGS IN osm2city
#=============================================================================

# -- check for overlap with static models. The scenery folder must contain an "Objects" folder
OVERLAP_CHECK = True
OVERLAP_RADIUS = 5
BUILDING_REMOVE_WITH_PARTS = False

TILE_SIZE = 2000            # -- tile size in meters for clustering of buildings

MAX_OBJECTS = 50000         # -- maximum number of buildings to read from OSM data
CONCURRENCY = 1             # -- number of parallel OSM parsing threads. Unused ATM.

# -- skip buildings based on their OSM name tag or OSM ID, in case there's already a static model for these, and the overlap check fails.
SKIP_LIST = ["Dresden Hauptbahnhof", "Semperoper", "Zwinger", "Hofkirche",
  "Frauenkirche", "Coselpalais", "Palais im Großen Garten",
  "Residenzschloss Dresden", "Fernsehturm", "Fernsehturm Dresden", "87807683"]

# -- Parameters which influence the number of buildings from OSM taken to output
BUILDING_MIN_HEIGHT = 3.4           # -- minimum height of a building to be included in output (does not include roof)
BUILDING_MIN_AREA = 50.0            # -- minimum area for a building to be included in output
BUILDING_REDUCE_THRESHOLD = 200.0   # -- threshold area of a building below which a rate of buildings gets reduced from output
BUILDING_REDUCE_RATE = 0.5          # -- rate (between 0 and 1) of buildings below a threshold which get reduced randomly in output
BUILDING_REDUCE_CHECK_TOUCH = False # -- before removing a building due to area, check whether it is touching another building and therefore should be kept
BUILDING_SIMPLIFY_TOLERANCE = 1.0   # -- all points in the simplified building will be within the tolerance distance of the original geometry.
BUILDING_NEVER_SKIP_LEVELS = 6      # -- buildings that tall will never be skipped

BUILDING_COMPLEX_ROOFS = 1          # -- generate complex roofs on buildings?
BUILDING_COMPLEX_ROOFS_MAX_LEVELS = 5 # -- don't put complex roofs on buildings taller than this
BUILDING_COMPLEX_ROOFS_MAX_AREA   = 2000 # -- don't put complex roofs on buildings larger than this
BUILDING_SKEL_ROOFS = 1             # -- generate complex roofs with pySkeleton? Used to be EXPERIMENTAL_USE_SKEL 
BUILDING_SKEL_ROOFS_MIN_ANGLE = 20  # -- pySkeleton based complex roofs will  
BUILDING_SKEL_ROOFS_MAX_ANGLE = 50  #    have a random angle between MIN and MAX
BUILDING_SKEL_MAX_NODES = 10        # -- max number of nodes for which we generate pySkeleton roofs
BUILDING_SKEL_MAX_HEIGHT_RATIO = 0.7 # --

EXPERIMENTAL_INNER = 0              # -- do we still need this?

# -- Parameters which influence the height of buildings if no info from OSM is available.
#    It uses a triangular distribution (see http://en.wikipedia.org/wiki/Triangular_distribution)
BUILDING_CITY_LEVELS_LOW = 2.0
BUILDING_CITY_LEVELS_MODE = 3.5
BUILDING_CITY_LEVELS_HEIGH = 5.0
BUILDING_CITY_LEVEL_HEIGHT_LOW = 3.1
BUILDING_CITY_LEVEL_HEIGHT_MODE = 3.3
BUILDING_CITY_LEVEL_HEIGHT_HEIGH = 3.6
# FIXME: same parameters for place = town, village, suburb

# -- The more buildings end up in LOD rough or bare, the more work for your GPU.
#    Increasing any of the following parameters will decrease GPU load.
LOD_ALWAYS_DETAIL_BELOW_AREA = 150  # -- below this area, buildings will always be LOD detail
LOD_ALWAYS_ROUGH_ABOVE_AREA = 500   # -- above this area, buildings will always be LOD rough
LOD_ALWAYS_ROUGH_ABOVE_LEVELS = 6   # -- above this number of levels, buildings will always be LOD rough
LOD_ALWAYS_BARE_ABOVE_LEVELS = 10   # -- really tall buildings will be LOD bare
LOD_ALWAYS_DETAIL_BELOW_LEVELS = 3  # -- below this number of levels, buildings will always be LOD detail
LOD_PERCENTAGE_DETAIL = 0.5         # -- of the remaining buildings, this percentage will be LOD detail,
                                    #    the rest will be LOD rough.

LIGHTMAP_ENABLE = 1                 # -- include lightmap in xml
OBSTRUCTION_LIGHT_MIN_LEVELS = 15   # -- put obstruction lights on buildings with >= given levels

CLUSTER_MIN_OBJECTS = 5             # -- discard cluster if to little objects

#=============================================================================
# EXPERIMENTAL PARAMETERS, work in progress, YMMV
#=============================================================================



#=============================================================================
# PARAMETERS RELATED TO PYLONS, POWERLINES, AERIALWAYS IN osm2pylons.py
#=============================================================================

C2P_PROCESS_POWERLINES = True
C2P_PROCESS_AERIALWAYS = True
C2P_PROCESS_OVERHEAD_LINES = True
C2P_PROCESS_STREETLAMPS = True

# Each powerline and aerialway has segments delimited by pylons. The longer the value the better clustering and
# the better the performance. However due to rounding errors the longer the length per cluster the larger the
# error.
C2P_CLUSTER_POWER_LINE_MAX_LENGTH = 300
C2P_CLUSTER_AERIALWAY_MAX_LENGTH = 300
C2P_CLUSTER_OVERHEAD_LINE_MAX_LENGTH = 130
C2P_CABLES_NO_SHADOW = True

# The radius for the cable. The cable will be a triangle with side length 2*radius.
# In order to be better visible the radius might be chosen larger than in real life
C2P_RADIUS_POWER_LINE = 0.1
C2P_RADIUS_POWER_MINOR_LINE = 0.05
C2P_RADIUS_AERIALWAY_CABLE_CAR = 0.05
C2P_RADIUS_AERIALWAY_CHAIR_LIFT = 0.05
C2P_RADIUS_AERIALWAY_DRAG_LIFT = 0.03
C2P_RADIUS_AERIALWAY_GONDOLA = 0.05
C2P_RADIUS_AERIALWAY_GOODS = 0.03
C2P_RADIUS_TOP_LINE = 0.02
C2P_RADIUS_OVERHEAD_LINE = 0.02

# The number of extra points between 2 pylons to simulate sagging of the cable.
# If 0 is chosen or if CATENARY_A is 0 then no sagging is calculated, which is better for performances (less realistic)
# 3 is normally a good compromise - for cable cars or major power lines with very long distances a value of 5
# or higher might be suitable
C2P_EXTRA_VERTICES_POWER_LINE = 3
C2P_EXTRA_VERTICES_POWER_MINOR_LINE = 3
C2P_EXTRA_VERTICES_AERIALWAY_CABLE_CAR = 5
C2P_EXTRA_VERTICES_AERIALWAY_CHAIR_LIFT = 3
C2P_EXTRA_VERTICES_AERIALWAY_DRAG_LIFT = 0
C2P_EXTRA_VERTICES_AERIALWAY_GONDOLA = 3
C2P_EXTRA_VERTICES_AERIALWAY_GOODS = 5
C2P_EXTRA_VERTICES_OVERHEAD_LINE = 2

# The value for catenary_a can be experimentally determined by using osm2pylon.test_catenary
C2P_CATENARY_A_POWER_LINE = 1500
C2P_CATENARY_A_POWER_MINOR_LINE = 1200
C2P_CATENARY_A_AERIALWAY_CABLE_CAR = 1500
C2P_CATENARY_A_AERIALWAY_CHAIR_LIFT = 1500
C2P_CATENARY_A_AERIALWAY_DRAG_LIFT = 1500
C2P_CATENARY_A_AERIALWAY_GONDOLA = 1500
C2P_CATENARY_A_AERIALWAY_GOODS = 1500
C2P_CATENARY_A_OVERHEAD_LINE = 600

C2P_CATENARY_MIN_DISTANCE = 30

C2P_POWER_LINE_ALLOW_100M = False

C2P_STREETLAMPS_MAX_DISTANCE_LANDUSE = 100
C2P_STREETLAMPS_RESIDENTIAL_DISTANCE = 40
C2P_STREETLAMPS_OTHER_DISTANCE = 70
C2P_STREETLAMPS_MIN_STREET_LENGTH = 20

#=============================================================================
# PARAMETERS RELATED TO landuse.py
#=============================================================================
LU_LANDUSE_GENERATE_LANDUSE = True
LU_LANDUSE_BUILDING_BUFFER_DISTANCE = 25
LU_LANDUSE_BUILDING_BUFFER_DISTANCE_MAX = 50
LU_LANDUSE_MIN_AREA = 5000

#=============================================================================
# PARAMETERS RELATED TO roads.py
#=============================================================================

TRAFFIC_SHADER_ENABLE = False
MAX_SLOPE_MOTORWAY = 0.03       # max slope for motorways
MAX_SLOPE_ROAD = 0.08
MAX_TRANSVERSE_GRADIENT = 0.1   #
BRIDGE_MIN_LENGTH = 20.         # discard short bridges, draw road instead
DEBUG_PLOT = 0
CREATE_BRIDGES_ONLY = 0         # create only bridges and embankments
# default_args_end # DO NOT MODIFY THIS LINE

def set_loglevel(foo):
    pass
    

def set_parameters(param_dict):
    for k in param_dict:
        if k in globals():
            if isinstance(globals()[k], types.BooleanType):
                globals()[k] = parse_bool(k, param_dict[k])
            elif isinstance(globals()[k], types.FloatType):
                float_value = parse_float(k, param_dict[k])
                if None is not float_value:
                    globals()[k] = float_value
            elif isinstance(globals()[k], types.IntType):
                int_value = parse_int(k, param_dict[k])
                if None is not int_value:
                    globals()[k] = int_value
            elif isinstance(globals()[k], types.StringType):
                if None is not param_dict[k]:
                    globals()[k] = param_dict[k].strip().strip('"\'')
            elif isinstance(globals()[k], types.ListType):
                globals()[k] = parse_list(param_dict[k])
            else:
                print "Parameter", k, "has an unknown type/value:", param_dict[k]
        else:
            print "Ignoring unknown parameter", k


def get_OSM_file_name():
    """
    Returns the path to the OSM File
    """
    return PREFIX + os.sep + OSM_FILE


def get_center_global():
    cmin = vec2d(BOUNDARY_WEST, BOUNDARY_SOUTH)
    cmax = vec2d(BOUNDARY_EAST, BOUNDARY_NORTH)
    return (cmin + cmax) * 0.5

def get_extent_global():
    cmin = vec2d(BOUNDARY_WEST, BOUNDARY_SOUTH)
    cmax = vec2d(BOUNDARY_EAST, BOUNDARY_NORTH)
    return cmin, cmax

def show():
    """
    Prints all parameters as key = value
    """
    print '--- Using the following parameters: ---'
    my_globals = globals()
    for k in sorted(my_globals.iterkeys()):
        if k.startswith('__'):
            continue
        elif k == "args":
            continue
        elif k == "parser":
            continue
        elif isinstance(my_globals[k], types.ClassType) or \
                isinstance(my_globals[k], types.FunctionType) or \
                isinstance(my_globals[k], types.ModuleType):
            continue
        elif isinstance(my_globals[k], types.ListType):
            value = ', '.join(my_globals[k])
            print k, '=', value
        else:
            print k, '=', my_globals[k]
    print '------'


def parse_list(string_value):
    """
    Tries to parse a string containing comma separated values and returns a list
    """
    my_list = []
    if None is not string_value:
        my_list = string_value.split(',')
        for index in range(len(my_list)):
            my_list[index] = my_list[index].strip().strip('"\'')
    return my_list


def parse_float(key, string_value):
    """
    Tries to parse a string and get a float. If it is not possible, then None is returned.
    On parse exception the key and the value are printed to console
    """
    float_value = None
    try:
        float_value = float(string_value)
    except ValueError:
        print 'Unable to convert', string_value, 'to decimal number. Relates to key', key
    return float_value


def parse_int(key, string_value):
    """
    Tries to parse a string and get an int. If it is not possible, then None is returned.
    On parse exception the key and the value are printed to console
    """
    int_value = None
    try:
        int_value = int(string_value)
    except ValueError:
        print 'Unable to convert', string_value, 'to number. Relates to key', key
    return int_value


def parse_bool(key, string_value):
    """
    Tries to parse a string and get a boolean. If it is not possible, then False is returned.
    """
    if string_value.lower() in ("yes", "true", "on", "1"):
        return True
    if string_value.lower() in ("no", "false", "off", "0"):
        return False
    print "Boolean value %s for %s not understood. Assuming False." % (string_value, key)
    # FIXME: bail out if not understood!
    return False


def read_from_file(filename):
    print 'Reading parameters from file:', filename
    try:
        f = open(filename, 'r')
        param_dict = {}
        full_line = ""
        for line in f:
            # -- ignore comments and empty lines
            line = line.split('#')[0].strip()
            if line == "":
                continue

            full_line += line  # -- allow for multi-line lists
            if line.endswith(","):
                continue

            pair = full_line.split("=", 1)
            key = pair[0].strip().upper()
            value = None
            if 2 == len(pair):
                value = pair[1].strip()
            param_dict[key] = value
            full_line = ""

        set_parameters(param_dict)
        f.close()
    except IOError, reason:
        print "Error processing file with parameters:", reason
        sys.exit(1)

def show_default():
    """show default parameters by printing all params defined above between
        # default_args_start and # default_args_end to screen.
    """
    f = open(sys.argv[0], 'r')
    do_print = False
    for line in f.readlines():
        if line.startswith('# default_args_start'):
            do_print = True
            continue
        elif line.startswith('# default_args_end'):
            return
        if do_print:
            print line,

if __name__ == "__main__":
    # Handling arguments and parameters
    parser = argparse.ArgumentParser(
        description="The parameters module provides parameters to osm2city - used as main it shows the parameters used.")
    parser.add_argument("-f", "--file", dest="filename",
                        help="read parameters from FILE (e.g. params.ini)", metavar="FILE")
    parser.add_argument("-d", "--show-default", action="store_true", help="show default parameters")
    args = parser.parse_args()
    if args.filename is not None:
        read_from_file(args.filename)
        show()
    if args.show_default:
        show_default()

