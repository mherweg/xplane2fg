#!/bin/bash

set -u
#set -x  # print commands before executing
export PYTHONHOME=$PWD/fakeroot/usr/
export PYTHONPATH=$PWD/.blender/scripts/:$PWD/.blender/scripts/bpymodules
export LD_LIBRARY_PATH=$PWD/fakeroot/usr/lib/
#if [ $1 == "-i" ]; then
#    python25
#fi
echo $PYTHONPATH
blender/blender $*
