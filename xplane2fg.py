#!/usr/bin/env python2

# usage:
# ./xplane2fg.py -i ../xp10/Custom\ Scenery/EDLM_Scenery_Pack/ -o /mh/scenery/test -n

# elevation probing does not work


import sys
from pdb import pm
import argparse
import logging
import os
import string
import calc_tile
from vec2d import vec2d 
import glob
import fgelev
import fnmatch
import pyparsing
import parameters

import ac3d

def install_files(file_list, dst):
    """link files in file_list to dst"""
    for the_file in file_list:
        print "cp %s " % the_file,
        the_dst = dst + os.sep + os.path.split(the_file)[1]
        print the_dst

        try:
            os.link(the_file, the_dst)
        except OSError, reason:
            if reason.errno not in [17]:
                logging.warn("Error while installing %s: %s" % (the_file, reason))

class Stats(object):
    def __init__(self):
        self.exported = 0
        self.to_convert = 0

class Object_def(object):
    def __init__(self, path, ID):
        path = path.replace('\\', '/')
        splitted = path.strip().split('/')
        self.ID = ID
        if len(splitted) > 1:
            self.prefix = string.join(splitted[:-1], os.sep) + os.sep
        else:
            self.prefix = ""

        self.file, self.ext = os.path.splitext(splitted[-1])
        self.name = self.prefix + os.sep + self.file

    def __str__(self):
        return "%s / %s %g %g %g" % (self.prefix, self.file)


class Object(object):
    def __init__(self, obj_def, lon, lat, hdg, msl=None):
        self.pos = vec2d(lon, lat)
        self.hdg = hdg
        self.msl = msl
        self.file = obj_def.file
        self.prefix = obj_def.prefix
        self.ext = obj_def.ext
        self.textures_list = []
    
    def __str__(self):
        return "%s : %g %g %g" % (self.file, self.pos.lon, self.pos.lat, self.hdg)

def read_dsf(path_to_dsf, path_to_txt, objects_def):
    if 1:
        os.system(dsftool + " --dsf2text '%s' '%s'" % (path_to_dsf, path_to_txt))

    objects = []
    ID = 0
    f = open(path_to_txt, 'r')
    for line in f.readlines():
        if line.startswith('OBJECT_DEF '):
            obj = Object_def(line[11:], ID)
            objects_def[obj.ID] = obj
            ID += 1
        
        elif line.startswith('OBJECT '):
            ID, lon, lat, hdg = [float(v) for v in line.split()[1:]]
            ID = int(ID)
            obj = Object(objects_def[ID], lon, lat, hdg)
            objects.append(obj)

        elif line.startswith('OBJECT_MSL '):
            ID, lon, lat, msl, hdg = [float(v) for v in line.split()[1:]]
            obj = Object(objects_def[ID], lon, lat, hdg, msl=msl)
            objects.append(obj)
            
    f.close()
    
    return objects

       
def get_source_path(obj, dir_only=False):
    # try given scenery path
    the_path = path_to_xp_in + os.sep + obj.prefix + obj.file + obj.ext
#    prefix_splitted = obj.prefix.split(os.sep)
#    if prefix_splitted[0] == 'opensceneryx':
#        return False
#    print "try", t
#    print "o", obj.prefix    
    if os.path.exists(the_path):
        if dir_only:
            return os.path.split(the_path)[0]
        return the_path
    return False
    

def mk_dirs(path):
    try:
        os.makedirs(path)
    except OSError:
        pass
#        print path, base_path + os.sep + prefix

def find_textures_below(base_path):
    matches = []
    for root, dirnames, filenames in os.walk(base_path):
        the_list = []
        for ext in ['*.dds', '*.png']:
            the_list += fnmatch.filter(filenames, ext)
        for filename in the_list:
            matches.append(os.path.join(root, filename))
    return matches

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)

    # -- Parse arguments. Command line overrides config file.
    parser = argparse.ArgumentParser(description="Convert X-plane scenery to FlightGear")
    parser.add_argument("-f", "--file", dest="filename",
                      help="read parameters from FILE (e.g. params.ini)", metavar="FILE")
    parser.add_argument("-i", "--input-path", help="path to x-plane scenery", metavar="PATH", default=None)
    #parser.add_argument("-d", "--dsf-file", help="path to x-plane dsf file", metavar="FILE")
    parser.add_argument("-o", "--output-path", help="path to fg scenery", metavar="PATH")
    parser.add_argument("-n", "--no-blender", action="store_true", help="don't run blender", default=False)
    parser.add_argument("-d", "--flip-DDS", action="store_true", help="flip DDS textures", default=False)
    parser.add_argument("-p", "--convert-DDS-to-PNG", action="store_true", help="convert DDS textures to PNG", default=False)
    parser.add_argument("-e", "--no-elev", action="store_true", help="don't probe elevation", default=False)
#    parser.add_argument("-c", dest="c", action="store_true", help="do not check for overlapping with static objects")
#    parser.add_argument("-u", dest="uninstall", action="store_true", help="uninstall ours from .stg")
    parser.add_argument("-l", "--loglevel", help="set loglevel. Valid levels are VERBOSE, DEBUG, INFO, WARNING, ERROR, CRITICAL")
    args = parser.parse_args()
    
    if args.filename is not None:
        parameters.read_from_file(args.filename)
    parameters.set_loglevel(args.loglevel)  # -- must go after reading params file

stats = Stats()
# get base from dsf path
#splitted = args.dsf_file.split(os.sep)
#if splitted[-3] != "Earth nav data":
#    logging.error("expected 'Earth nav data', got %s" % splitted[-3])
#    sys.exit(-1)
if False:
#    args.input_path = "/home/tom/fgfs/scenery/convert/EDDM/EDDM_4_0"
    args.input_path = "/home/tom/fg/scenery/convert/KaiTak_9dragons"
    #args.input_path = "/home/tom/fgfs/scenery/convert/OZ/YMML/YMML Melbourne (ISDG)"
    #args.input_path = "/home/tom/fgfs/scenery/convert/OZ/YMML/YMML Melbourne (ISDG)"
    
    #args.input_path="/home/tom/fg/scenery/convert/Kaitak/Kai_Tak"
#    args.output_path="/media/home/tom/daten/fgfs/fg_scenery/Scenery-devel"
    args.output_path = "/home/tom/fg/scenery/convert/KaiTak_9dragons.fg"
#    args.no_blender = True

# -- cmd line params override input file
#VARS = ['input_path', 'output_path']
#for the_param in args.__dict__:
#    print the_param
#    #THE_PARAM = string.upper(the_param)
#    if args.__dict__[the_param]
#bla
if args.input_path:
    parameters.INPUT_PATH = args.input_path
if args.output_path:
    parameters.OUTPUT_PATH = args.output_path
    
    

if args.input_path == None:
    logging.error("Need path")
    sys.exit(-1)

# TODO: more input path checking

#base="/run/media/tom/btmpl/tom/daten/fgfs/my/xplane2fg/portable_blender_2.49b/"
dsftool="DSFTool"

#base = string.join(splitted[:-5], os.sep)
#path_to_dsf = args.dsf_file
#"d_eddn/Earth nav data/+40+010/+49+011.dsf"
#path_to_txt = "d_eddn/Earth nav data/+40+010/+49+011.txt"
args.input_path = args.input_path.rstrip(os.sep)
path_to_xp_in  = args.input_path
path_to_fg_out = args.input_path + '.fg'
path_to_fg_out = args.output_path #"/home/tom/fgfs/fg_scenery/Scenery-devel"
path_to_tmp    = args.input_path + '.tmp'

#print path_to_txt
print path_to_xp_in
print path_to_fg_out
print path_to_tmp
mk_dirs(path_to_tmp)


# -- we maintain two lists:
#    1. objects: all scenery objects. Can have duplicates
#    2. ac_files_list: .ac files on disk. Can have "duplicates", too: same file in different folders, e11n47/tree.ac and a11n48/tree.ac

# -- read objects from all DSF in "Earth nav data" folder
dsfs = glob.glob(path_to_xp_in + os.sep + "Earth nav data" + os.sep + '???????' + os.sep + '???????.dsf')
logging.info("dsfs " + str(dsfs))

objects = []
objects_def = {}
for dsf in dsfs:
    path_to_txt = path_to_tmp + os.sep + os.path.basename(dsf) + '.txt'
    the_objects = read_dsf(dsf, path_to_txt, objects_def)
    objects += the_objects

#objects = objects[0:10]
#for o in objects:
#    print o

#sys.exit(-1)

path_to_fgelev = "fgelev"
path_to_scenery = "/home/mherweg/.fgfs/TerraSync/"
elev_prober = fgelev.Probe_fgelev(path_to_fgelev, path_to_scenery,cache=False)

autoimport = open('blender-autoimport-source.py', 'w')
import stg_io2
OUR_MAGIC = "osm2test"


# convert .obj to .ac (obj_def)
#logging.info("converting .obj to .ac")
#for o in objects_def:


# 1. Init STG_Manager
stg_manager = stg_io2.STG_Manager(path_to_fg_out, OUR_MAGIC, overwrite=True)

logging.info("probing elevation")
ac_file_list = []
ac_object_list = []
for o in objects:
    if o.msl == None:
        if not args.no_elev: 
            o.msl = elev_prober(o.pos)
        else:
            o.msl = 0.1
        #logging.debug("object %s: elev probed %s" % (o.file, str(o.msl)))
    else:
        logging.debug("object %s: using provided MSL=%g" % (o.file, o.msl))

    stg_file_name = calc_tile.construct_stg_file_name(o.pos)
    stg_path = calc_tile.construct_path_to_stg(path_to_fg_out, o.pos)
    #print stg_file_name, stg_path
    # -- build list of objects to be converted
    full_path = get_source_path(o)
    full_path = "/tmp"
    if full_path != False:
        path_to_stg = stg_manager.add_object_shared(o.prefix + o.file + ".ac", o.pos, o.msl, 90-o.hdg)
        mk_dirs(path_to_stg + o.prefix)
        o.path_to_ac = path_to_stg + o.prefix + o.file + '.ac'
        if o.path_to_ac not in ac_file_list:
            ac_file_list.append(o.path_to_ac)
            ac_object_list.append(o)
            if os.path.exists(o.path_to_ac):
                print "EX ", o
            else:
                s = "convert('%s', '%s')\n" % (full_path, o.path_to_ac)
                autoimport.write(s)
                stats.to_convert += 1
                print "OK ", o
            stats.exported += 1
    else:
        print "!  ", o

    #print elev, 
elev_prober.save_cache()

autoimport.close()

# 4. finally write all cached lines to .stg files.
logging.info("writing stg")
stg_manager.write()

logging.info("done stg")
print "stats"
print "  exported %i" % stats.exported
print "  objects  %i" % len(objects)
print "  convert  %i" % stats.to_convert

if not args.no_blender: 
    logging.info("Starting blender")
    os.system("./blender.sh -P autoimport.py")

# -- copy textures.
#    read .ac objects. Store number of vertices and faces in o
#    
#for ac_file, o in zip(ac_file_list, ac_object_list):
    #logging.info(" %s uses" % (ac_file))
    #try:
        #ac = ac3d.File(ac_file)
    #except pyparsing.ParseException:
        #continue
    #logging.info("  %i texture(s): %s" % (len(ac.texture_list), str(ac.texture_list)))

    #ac_path = os.path.split(ac_file)[0]
    #src_path = get_source_path(o, dir_only=True)
    ## -- search for texture file
    ##    try same path as .ac, and relative those in texture_relative_path_list
    #texture_relative_path_list = ['.', 'textures']
    
    #for texture in ac.texture_list:
        #print "Tex", texture
##        if texture == 'None':
##            continue
        #final_texture_path = None
        #for rel_path in texture_relative_path_list:
            
            #texture_path = src_path + os.sep + rel_path + os.sep + texture
            #if os.path.exists(texture_path):
                #final_texture_path = texture_path
                #break
    
        ## -- convert DDS texture if requested
        #if args.convert_DDS_to_PNG:
            #pass
        
        ## -- flip DDS texture if requested
        #if args.flip_DDS:
            #pass
    
        #if final_texture_path:
            #install_files([final_texture_path], ac_path)
        #else:
            #logging.warn("Texture not found: %s" % texture)

print "Done."
sys.exit()

sys.exit(0)

#  TODO. should use actual texture from .ac
wd = os.getcwd()
os.chdir(path_to_xp_in)
logging.debug("Now in " + os.getcwd())
textures = find_textures_below('.')
# FIXME: also copy textures -- destination folder not extisting?

logging.info("installing textures")
for t in textures:
#    print t[len(path_to_xp_in)+1:]
    print t
    install_files([t], path_to_stg)
os.chdir(wd)
sys.exit()

# -- convert to .png textures

    

# todo:
# x convert obj only once
# - get textures
# - statistics
# - read ac, show number of nodes, faces etc
# - exchange texture with png

# read .dsf
# build list of input .obj
# convert
# get their coords
# probe alt
# write to fg

