# --------------------------------------------------------------------------
# Copyright (C) 2010: Thomas Albrecht
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# --------------------------------------------------------------------------
#import Blender
#import bpy


from Blender import Window, sys
import BPyTextPlugin
import bpy
#import sys

import Blender
from Blender import sys as bsys
from Blender.Window import FileSelector

import XPlaneImport as im

####from ac3d_export_hack import *
from ac3d_export import *

def convert(infile, outfile):

    
    print "converting %s --> %s" % (infile, outfile)
    try:
        # -- import
        im.file_callback(infile)

        # -- export
        scn = Blender.Scene.GetCurrent()
        OBJS = list(scn.objects)
        f = open(outfile, 'w')
        try:
            AC3DExport(OBJS, f)
        except:
            pass
        f.close()
    except:
        pass
    clear()

def clear():
    cur = Blender.Scene.GetCurrent()
    newscene = Blender.Scene.New('newscene')
    newscene.makeCurrent() 
    Blender.Scene.Unlink(cur)

clear()
# -- read actual objects to convert from external file
execfile ('blender-autoimport-source.py')
print "autoimport finished."
sys.exit()
