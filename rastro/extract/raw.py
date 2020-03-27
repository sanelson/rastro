# -*- coding: utf-8 -*-
import rawpy

import numpy as np
import numpy.ma as ma

def get_color_plane_map(color_plane_count, color_desc):
  # Decode color plane indexes
  # TODO: Make this more robust so that other cameras color names work
  color_plane_map = list(range(color_plane_count))
  green_idx = 1
  for i in range(color_plane_count):
    color_name = color_desc.decode()[i]

    # Apply instance suffix to green channel names
    if color_name == 'G':
      color_name = color_name + str(green_idx)
      green_idx = green_idx + 1

    color_plane_map[i] = color_name

  return color_plane_map

def reader(raw_filename):
  """
     Takes a RAW filename as an argument and returns a dictionary containing 1D and 2D representations of
     the image data.
  """
  # TODO: slurp out metadata in this function?
  # see: https://www.libraw.org/node/2352  not sure if rawpy supports this (yet).
  # Open the RAW file for reading
  with rawpy.imread(raw_filename) as raw:
    color_plane_count = raw.num_colors + 1

    # Extract individual color planes
    color_plane_map = get_color_plane_map(color_plane_count, raw.color_desc)

    # Color plane dictionary 
    # TODO: make this more pythony and use an OO approach
    color_planes = {}
    for i in range(color_plane_count):
      color_planes[color_plane_map[i]] = {}

      # TODO: Document exactly what is taking place with this numpy array transformation
      mask = (raw.raw_colors_visible != i)
      color_plane_masked = ma.masked_array(np.copy(raw.raw_image_visible), mask)
      # TODO: Do camera sensors ever have an odd number of pixels in x/y?  This would skew results slightly.
      half_size_shape = tuple(int(dim/2) for dim in raw.raw_image_visible.shape)
      color_planes[color_plane_map[i]]["1D"] = color_plane_masked[~color_plane_masked.mask]

      # Reshape the array
      # TODO: Is this the best way?
      # See: https://docs.scipy.org/doc/numpy/reference/generated/numpy.reshape.html
      color_planes[color_plane_map[i]]["2D"] = np.reshape(color_planes[color_plane_map[i]]["1D"], half_size_shape)

    return color_planes


