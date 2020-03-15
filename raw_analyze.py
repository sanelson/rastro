#!/bin/env python3
import rawpy
import imageio
import argparse
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import numpy.ma as ma
import PIL

def get_color_shade(color_plane_name):
  """
    Return a floating point RGB color array definition from a color plane name.
    Multiple instances of the same color plane have their color shifted using the color
    plane index.
  """
  # Only supports RGB image color planes for now
  color_shade = color_plane_name[0].upper()

  # Check for color plane index
#  color_shade_instance = 1
  try:
    color_shade_instance = int(color_plane_name[1])
  except IndexError:
    color_shade_instance = 1

  color_shades_map = {
      "R": [1.0, 0, 0],
      "G": [0, 1.0, 0],
      "B": [0, 0, 1.0]
  }

  #color_shade_rgb = color_shades_map[color_shade] / float(color_shade_instance)
  color_shade_rgb = [rgb_shade / float(color_shade_instance) for rgb_shade in color_shades_map[color_shade]]

  return color_shade_rgb

# High DPI screen plot resolution hack
# TODO: figure out how to add some intelligence for handling different display DPIs
mpl.rcParams['figure.dpi'] = 300

# Links:
# https://docs.scipy.org/doc/numpy/reference/maskedarray.generic.html
# https://github.com/semolex/astrawpy/blob/master/cfa.py

# Notes
# 1. Try to determine original raw file image depth in order to build an accurate histogram
#    a. Yuck, this is harder than I thought: https://www.libraw.org/node/2205

# Process command line arguments
parser = argparse.ArgumentParser(description='Analyze Raw camera files.')
#parser.add_argument('-o', '--output', help='Filename for conversion output', type=str)
#parser.add_argument('-h', '--histogram', help='Generate histogram of RAW file image data')
parser.add_argument('raw_file', help='Raw Filename for analysis', type=str)

args = parser.parse_args()
raw_file = args.raw_file

# Open the RAW file for reading


#with open(raw_file, 'r') as raw_fd:
# Low level processing of raw image
#with rawpy.RawPy.open_file(raw_file) as raw:
#rawpy.open_file(raw_file)
#rawpy.unpack()
  # Unpack the file
#  raw_image = raw.unpack()

# Switch matplotlib to greyscale mode
plt.gray()

with rawpy.imread(raw_file) as raw:
  color_plane_count = raw.num_colors + 1
  print('Raw pattern: \n', raw.raw_pattern)
  print('Color plane count: ', color_plane_count)
  print('Color matrix: \n', raw.color_matrix)
  print('Color description: \n', raw.color_desc)

  # Decode color plane indexes
  # TODO: Make this more robust so that other cameras color names work
  color_plane_idx = list(range(color_plane_count))
  green_idx = 1
  for i in range(color_plane_count):
    color_name = raw.color_desc.decode()[i]

    # Apply instance suffix to green channel names
    if color_name == 'G':
      color_name = color_name + str(green_idx)
      green_idx = green_idx + 1

    color_plane_idx[i] = color_name

  # Extract individual color planes
#  color_plane = np.copy(raw.raw_image_visible)
  color_planes = list(range(color_plane_count))
  for i in range(color_plane_count):
    print("Working on color plane [{}] [{}]".format(str(i), color_plane_idx[i]))
    mask = (raw.raw_colors_visible != i)
    #print('mask: \n', mask)
    #color_plane = np.copy(raw.raw_colors_visible)
    #color_plane = ma.masked_array(np.copy(raw.raw_image_visible), mask)
    color_plane_masked = ma.masked_array(np.copy(raw.raw_image_visible), mask)
    #color_plane = np.copy(raw.raw_image_visible).compress(mask, axis=2)
    #color_plane = np.compress(mask, raw.raw_image_visible, axis=0)
#    color_plane = raw.raw_image_visible.compress(mask, axis=0)
#    color_plane[mask] = 0
#    color_plane = ma.masked_array(np.copy(raw.raw_image_visible), mask)
    #print("Shape: ", color_plane.shape)
    half_size_shape = tuple(int(dim/2) for dim in raw.raw_image_visible.shape)
    #print("Half-Size Shape: ", half_size_shape)

    color_plane_1d = color_plane_masked[~color_plane_masked.mask]
    #print("Shape: ", color_plane_1d.shape)
#    color_plane = ma.masked_array(np.copy(raw.raw_image_visible), mask)
    #print('Color plane data: \n', color_plane_1d.data)
    
    # Reshape the array
    # TODO: Is this the best way?
    color_plane_2d = np.reshape(color_plane_1d, half_size_shape)
    #print('Reshaped Color plane data: \n', color_plane_2d.data)

    #print("2D Shape: ", color_plane_2d.shape)

    # Plot a basic histogram of this color plane

    print("Color shade: ", get_color_shade(color_plane_idx[i]))
    #plt.hist(color_plane_2d, bins = range(0, 2^14, 1))
    #plt.hist(color_plane_2d, bins = range(0, 255, int((2**14/256)/2)))
    #plt.hist(color_plane_1d, bins = range(0, 255, int((2**14/256)/2)))
    #plt.hist(color_plane_1d, 256, density=True, facecolor='g', alpha=0.75)
    #plt.hist(color_plane_1d, 256, density=False, facecolor='g', alpha=0.75)
    #plt.hist(color_plane_1d, 256, density=False, facecolor=color_plane_idx[i][0].lower(), alpha=0.75)
    plt.hist(color_plane_1d, 1024, density=False, facecolor=get_color_shade(color_plane_idx[i]), alpha=0.75, label=color_plane_idx[i])
    #plt.title("Image Histogram")
    #plt.show()

    #plt.imshow(color_plane.data, interpolation='nearest')
    #plt.imshow(color_plane_2d, interpolation='nearest')
    #plt.show()
    
    #plt.savefig("{}.{}.{}".format(raw_file, color_plane_idx[i], "png"))
    #plt.imsave("{}.{}.{}".format(raw_file, color_plane_idx[i], "png"), color_plane_2d)
#    plt.imsave("{}.{}.{}".format(raw_file, color_plane_idx[i], "tiff"), color_plane_2d)

  plt.title("Image Histogram")
#  plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
#  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=2, mode="expand", borderaxespad=0.)
  plt.legend()
  plt.show()

##  rgb = raw.postprocess()
#  raw_image = raw.raw_image_visible
#  #print(type(raw_image))
#  #print(raw_image)
#  print(raw.raw_type)
#  print(raw.raw_pattern)
#  print(raw.rgb_xyz_matrix)
#  print(raw.sizes)
#  print(raw_image.shape)
#  print(raw_image[1,2])


