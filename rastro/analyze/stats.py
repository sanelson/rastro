# -*- coding: utf-8 -*-

import rawpy
import io
import pyexiv2
from pyexiv2.exif import ExifTag, ExifValueError
import numba
import numpy as np
import numpy.ma as ma

from rastro.extract import raw

## ### Numba Function Speedups ###
## # TODO: These should probably move to a new package/module soon
## @numba.jit(nopython=True)
## def numba_mean(a):
##   return np.mean(a)
## 
## @numba.jit(nopython=True)
## def numba_amin(a):
##   return np.amin(a)
## 
## @numba.jit(nopython=True)
## def numba_amax(a):
##   return np.amax(a)
## 
## @numba.jit(nopython=True)
## def numba_median(a):
##   return np.median(a)
## 
## @numba.jit(nopython=True)
## def numba_std(a):
##   return np.std(a)
## 
## @numba.jit(nopython=True)
## def numba_var(a):
##   return np.var(a)

def output_basic_stats(raw_filename):
  # see: https://python3-exiv2.readthedocs.io/en/latest/api.html#buffer
  # Little hack to not have to open the RAW file more than once to gather stats/info
  metadata = pyexiv2.ImageMetadata(raw_filename)
  metadata.read()

  # Print out all the exif data
  for key in metadata.exif_keys:
    try:
      # print(str(key) + "=" + str(metadata[key].value))
      print(str(key) + "=" + str(metadata[key]))
    except ExifValueError:
      print("Unable to decode raw value for key [{}]".format(key))

  # Create io buffer to re-use with rawpy
  byteio = io.BytesIO(metadata.buffer)

  # Operate on the IO buffer
  with rawpy.imread(byteio) as rawimage:
  #  rgb = rawimage.postprocess()
    print("Black level per channel: ", rawimage.black_level_per_channel)
    print("Camera White Balance: ", rawimage.camera_whitebalance)
    print("Camera Color Description: ", rawimage.color_desc)
  #  print("Camera Color Matrix: ", rawimage.color_matrix)
    print("Daylight White Balance: ", rawimage.daylight_whitebalance)
    print("Number of Colors: ", rawimage.num_colors)
  #  print("Raw Colors: ", rawimage.raw_colors)
    print("Raw Type: ", rawimage.raw_type)
    print("Sizes: ", rawimage.sizes)

    # Get RAW CFA image data for overall stats
    raw_bayer_plane = rawimage.raw_image_visible

    # Visible sensor stats
    #print("Raw Bayer Plane: \n", raw_bayer_plane)
    # TODO: convert numpy stats to numba stats (if available)
    print("------ Bayer plane stats ------\n")
    print("Max pixel value: ", np.amax(raw_bayer_plane))
    print("Min pixel value: ", np.amin(raw_bayer_plane))
    print("Median pixel value: ", np.median(raw_bayer_plane))
    print("Average pixel value: ", np.average(raw_bayer_plane))
    print("Stdev of pixel values: ", np.std(raw_bayer_plane))
    print("Variance of pixel values: ", np.var(raw_bayer_plane))

    # These are actually slower than standard numpy...  Probably something I'm doing wrong
    #print("------ Bayer plane stats ------\n")
    #print("Max pixel value: ", numba_amax(raw_bayer_plane))
    #print("Min pixel value: ", numba_amin(raw_bayer_plane))
    #print("Median pixel value: ", numba_median(raw_bayer_plane))
    #print("Average pixel value: ", numba_mean(raw_bayer_plane))
    #print("Stdev of pixel values: ", numba_std(raw_bayer_plane))
    #print("Variance of pixel values: ", numba_var(raw_bayer_plane))

    # Analyze color plane data
    color_plane_count = rawimage.num_colors + 1

    # Extract individual color planes
    color_plane_map = raw.get_color_plane_map(color_plane_count, rawimage.color_desc)

    # Color plane dictionary 
    # TODO: make this more pythony and use an OO approach
    color_planes = {}
    for i in range(color_plane_count):
      color_planes[color_plane_map[i]] = {}

      # TODO: Document exactly what is taking place with this numpy array transformation
      mask = (rawimage.raw_colors_visible != i)
      color_plane_masked = ma.masked_array(np.copy(rawimage.raw_image_visible), mask)
      # TODO: Do camera sensors ever have an odd number of pixels in x/y?  This would skew results slightly.
      half_size_shape = tuple(int(dim/2) for dim in rawimage.raw_image_visible.shape)
      color_planes[color_plane_map[i]]["1D"] = color_plane_masked[~color_plane_masked.mask]

      # Individual color plane stats
      # TODO: Do we need to remove the mask before calculating stats?
      # /usr/lib/python3/dist-packages/numpy/core/fromnumeric.py:745: UserWarning: Warning: 'partition' will ignore the 'mask' of the MaskedArray.  a.partition(kth, axis=axis, kind=kind, order=order)

      print("------ {} color plane stats ------\n".format(color_plane_map[i]))
      print("Max pixel value: ", np.amax(color_planes[color_plane_map[i]]["1D"]))
      print("Min pixel value: ", np.amin(color_planes[color_plane_map[i]]["1D"]))
      print("Median pixel value: ", np.median(color_planes[color_plane_map[i]]["1D"]))
      print("Average pixel value: ", np.average(color_planes[color_plane_map[i]]["1D"]))
      print("Stdev of pixel values: ", np.std(color_planes[color_plane_map[i]]["1D"]))
      print("Variance of pixel values: ", np.var(color_planes[color_plane_map[i]]["1D"]))

      # Reshape the array
      # TODO: Is this the best way?
      # See: https://docs.scipy.org/doc/numpy/reference/generated/numpy.reshape.html
      #color_planes[color_plane_map[i]]["2D"] = np.reshape(color_planes[color_plane_map[i]]["1D"], half_size_shape)
      # For now, I don't think we need 2D for stats



  #print("Raw Image: ", rawimage.raw_image)
#  print("Raw Image (Visible): ", rawimage.raw_image_visible)
#  print("Raw Pattern: ", rawimage.raw_pattern)
#
#  print("Raw Colors (Visible): ", rawimage.raw_colors_visible)


