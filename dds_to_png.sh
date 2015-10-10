#!/bin/bash

PROG=dds_to_png.sh
USAGE="$PROG file"
DESC="<One line of description>"
HELP="<Zero or more lines of Help>"
AUTHOR="Thomas Albrecht"

#[ "$1" == "" ] || [ "$1" == "-h" ] || [ "$1" == "--help" ] && \
#    echo -e "Usage: $USAGE\n$DESC\n$HELP" && exit 1

set -u

# Here follows your own code
mkdir dds/
dds=`find . -type f -name "*.dds"`
for the_dds in $dds; do
  base=${the_dds%.dds}
  filename=`basename $the_dds .dds`
  echo $the_dds $base
  convert $the_dds $base.png
  mv $the_dds dds/
  ln -s $filename.png $base.dds
  #mv $base.png $base.dds
done

  