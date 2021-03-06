#!/usr/bin/env python
############################################################################
#
# MODULE:       v.stream.network.basin
#
# AUTHOR(S):    Andrew Wickert
#
# PURPOSE:      Build a drainage basin from the subwatersheds of a river  
#               network, based on the structure of the network.
#
# COPYRIGHT:    (c) 2016 Andrew Wickert
#
#               This program is free software under the GNU General Public
#               License (>=v2). Read the file COPYING that comes with GRASS
#               for details.
#
#############################################################################
#
# REQUIREMENTS:
#      -  uses inputs from r.stream.extract
 
# More information
# Started 14 October 2016
#%module
#% description: Build a linked stream network: each link knows its downstream link
#% keyword: vector
#% keyword: stream network
#% keyword: basins
#% keyword: hydrology
#% keyword: geomorphology
#%end
#%option G_OPT_V_INPUT
#%  key: input_streams
#%  label: Stream network
#%  required: no
#%end
#%option G_OPT_V_INPUT
#%  key: input_basins
#%  label: Subbasins built alongside stream network
#%  required: no
#%end
#%option
#%  key: cat
#%  label: Farthest downstream segment category
#%  required: yes
#%  guidependency: layer,column
#%end
#%option G_OPT_V_OUTPUT
#%  key: output_basin
#%  label: Vector output drainage basin
#%  required: yes
#%end
#%option G_OPT_V_OUTPUT
#%  key: output_streams
#%  label: Streams within vector output drainage basin
#%  required: yes
#%end

##################
# IMPORT MODULES #
##################
# PYTHON
import numpy as np
from matplotlib import pyplot as plt
import sys
# GRASS
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules.shortcuts import vector as v
from grass.pygrass.gis import region
from grass.pygrass import vector # Change to "v"?
from grass.script import vector_db_select
from grass.pygrass.vector import Vector, VectorTopo
from grass.pygrass.raster import RasterRow
from grass.pygrass import utils
from grass import script as gscript

###############
# MAIN MODULE #
###############

def find_upstream_segments(cats, tostream, cat):
    """
    Find segments immediately upstream of the given one
    """
    

def main():
    """
    Links each river segment to the next downstream segment in a tributary 
    network by referencing its category (cat) number in a new column. "0"
    means that the river exits the map.
    """

    options, flags = gscript.parser()
    
    streams = options['input_streams']
    basins = options['input_basins']
    cat = options['cat']
    output_basins = options['output_basin']
    output_streams = options['output_streams']
    
    print options
    print flags

    # Attributes of streams
    colNames = np.array(vector_db_select(streams)['columns'])
    colValues = np.array(vector_db_select(streams)['values'].values())
    tostream = colValues[:,colNames == 'tostream'].astype(int).squeeze()
    cats = colValues[:,colNames == 'cat'].astype(int).squeeze() # = "fromstream"

    # Find network
    basincats = [cat] # start here
    most_upstream_cats = [cat] # all of those for which new cats must be sought
    while True:
        if len(most_upstream_cats) == 0:
            break
        tmp = list(most_upstream_cats) # copy to a temp file: old values
        most_upstream_cats = [] # Ready to accept new values
        for ucat in tmp:
            most_upstream_cats += list(cats[tostream == ucat])
            basincats += most_upstream_cats
            
    basincats = list(set(list(basincats)))

    basincats_str = ','.join(map(str, basincats))
    
    # Many basins out -- need to use overwrite flag in future!
    SQL_OR = 'rnum = ' + ' OR rnum = '.join(map(str, basincats))
    SQL_OR = 'cat = ' + ' OR cat = '.join(map(str, basincats))
    v.extract(input=basins, output=output_basins, where=SQL_OR, overwrite=True)
    v.extract(input=streams, output=output_streams, cats=basincats_str, overwrite=True)

    # We can loop over this list to get the shape of the full river network.
    selected_cats = []
    segment = int(cat)
    selected_cats.append(segment)
    
    selected_cats_str = list(np.array(selected_cats).astype(str))
    selected_cats_csv = ','.join(selected_cats_str)

    v.extract(input=options['streams'], output=options['outstream'], cats=selected_cats_csv, overwrite=True)

if __name__ == "__main__":
    main()

