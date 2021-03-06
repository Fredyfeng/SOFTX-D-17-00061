#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Erika Tudisco, Edward Andò, Stephen Hall, Rémi Cailletaud

# This file is part of TomoWarp2.
# 
# TomoWarp2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TomoWarp2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with TomoWarp2.  If not, see <http://www.gnu.org/licenses/>.

# ===================================================================
# ===========================  TomoWarp2  ===========================
# ===================================================================

# Authors: Erika Tudisco, Edward Andò, Stephen Hall, Rémi Cailletaud

# Deprecated. Moved to tools/kinematic_filters

import numpy

import sys

from tools.tsv_tools import ReadTSV, WriteTSV
from tools.calculate_node_spacing import calculate_node_spacing
from tools.kinematic_filters import kinematics_remove_outliers

def median_filter(  ):
  print "  -> median_filter: This function is deprecated, please look in:"
  print "     prior_field/prior_median_filter.py"



def median_filter_nans( in_matrix, filter_size ):
  # 2014-07-23 Eddy (on holiday in Greece...)
  # The median filter above seems both unnecessarily complicated and
  #   not general enough to deserve to name median_filter.
  # => Renaming it kinematics_median_filter.

  # Following the discussion on http://stackoverflow.com/questions/10683596/efficiently-calculating-boundary-adapted-neighbourhood-average
  #                     ...and  http://stackoverflow.com/questions/5480694/numpy-calculate-averages-with-nans-removed
  #   ...but we are not going to use a mask, just the properties of numpy.median.
  # Defining a simple, median filter which operates on a nd-matrix,
  #   This is done with "scipy.ndimage.generic_filter", with the operation numpy.median
  #   ...since this operation is not sensitive to NaNs, then we won't spread them around the matrix.
  # -> This doesn't work for numpy.mean, or .sum...
  # -> scipy.ndimage.filters.median_filter spreads NaNs more than this solution.

  # Input:
  #   - nd-matrix (possibly with NaNs, but not necessarily masked)
  #   - scipy.ndimage compatible size
  # Output: filtered array.

  import scipy.ndimage
  import numpy

  # Could consider making a circular mask/kernel,
  #   and passing it as footprint= instead of size=
  return scipy.ndimage.generic_filter( in_matrix, numpy.median, size=filter_size, mode='constant', cval=0.0 )




def kinematics_median_filter_fnc( positions, displacements, filter_size ):
  # The median filter above seems both unnecessarily complicated and
  #   not general enough to deserve to name median_filter.
  # Making a new stub (above) to warn users.

  #-----------------------------------------------------------------------
  #-  Calculate nodal spacing                                           --
  #-      (this comes from regular_prior_interpolator.py)               --
  #-----------------------------------------------------------------------
  number_of_nodes = positions.shape[0]
  number_of_displacements = displacements.shape[1]

  if positions.shape[1] != 3:
      print "  -> kinematics_median_filter(): Not given three positions. Stopping."
      return -1

  if number_of_nodes != displacements.shape[0]:
      print "  -> kinematics_median_filter(): Not given the same amout of positions and displacements. Stopping."
      return -1

  nodes_z, nodes_y, nodes_x = calculate_node_spacing( positions )
   

  try:
      # Figure out spacing from first two nodes positions
      y_spacing = nodes_y[1] - nodes_y[0]
      x_spacing = nodes_x[1] - nodes_x[0]
      if len(nodes_z) == 1:
        #we are working with 2D images
        z_spacing = y_spacing
      else:
        z_spacing = nodes_z[1] - nodes_z[0]
  except IndexError:
      raise Exception('Warning: Not enough nodes to calculate median filter')

  # If the node spacing is not the same in every direction, we're not sure that this
  #   can work.
  if z_spacing != y_spacing or z_spacing != x_spacing:
    raise Exception("kinematics_median_filter_fnc(): the spacing is different, and I'm not sure I can handle this. Stopping.")

  # Define output matrix
  result = numpy.zeros( ( number_of_nodes, number_of_displacements ) )

  #-----------------------------------------------------------------------
  #-  Reshape the displacements so that we easily have the neighbours   --
  #-----------------------------------------------------------------------
  # This is a 4D array of z, y, x positions + component...
  displacements = numpy.array( displacements.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ), number_of_displacements ) ) )

  for i in range( number_of_displacements ):
    result[ :, i ] = median_filter_nans( numpy.squeeze(displacements[ :, :, :, i ]), filter_size ).reshape( ( number_of_nodes ) )

  return result


if __name__ == "__main__":

    prefix = "output"
    filter_size = 3

    argv = sys.argv[1:]
    if len(argv) < 2:
      print 'Use: prior_median_filter <inputfile> <outputfile>'
      sys.exit(2)

    prior_file = argv[0]
    output_file = argv[1]

    print "prior_file = ",prior_file

    print "  -> Reading prior field..."
    prior = ReadTSV( prior_file,  "NodeNumber", [ "Zpos", "Ypos", "Xpos", "Zdisp", "Ydisp", "Xdisp" ], [1,0] ).astype( '<f4' )
    print "  -> Reading finished...\n"

    prior_filtered = prior.copy()
    #prior_filtered[ :, 4:7 ] = kinematics_median_filter_fnc( prior[ :, 1:4 ], prior[ :, 4:7 ] )
    prior_filtered[ :, 4:7 ] = kinematics_remove_outliers( prior[ :, 1:4 ], rior[ :, 4:7 ], filter_size )
    

    WriteTSV( output_file, [ "NodeNumber", "Zpos", "Ypos", "Xpos","Zdisp", "Ydisp", "Xdisp" ], prior_filtered )
