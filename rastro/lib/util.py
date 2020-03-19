import rawpy
from rawpy import enhance
import io
import pyexiv2
from pyexiv2.exif import ExifTag, ExifValueError
import matplotlib as mpl
# TODO: See what backends are available and fallback to tkinter with a warning if none are available
mpl.use('Qt5Agg')  # Change plotting backend for increased performance: https://matplotlib.org/faq/usage_faq.html#what-is-a-backend
from matplotlib import pyplot as plt
from astropy.io import fits

import numba
import numpy as np
import numpy.ma as ma
#import math # Our computation routines
from . import math # Our computation routines
import tifffile # https://pypi.org/project/tifffile/  Good library for scientific image processing in TIFF format

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

def raw_reader(raw_filename):
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
    color_plane_map = math.get_color_plane_map(color_plane_count, raw.color_desc)

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

def fits_single_channel_writer(raw_filename, color_plane, color_plane_name, **options):
  hdu = fits.PrimaryHDU(color_plane)

  hdul = fits.HDUList([hdu])

  fits_filename = raw_filename + '.' + color_plane_name + '.fits'
  hdul.writeto(fits_filename)

def tiff_all_channels_writer(raw_filename, color_planes, bit_depth_type, **options):
  # Write color plane to file
  for color_plane_name in color_planes:
    tiff_filename = raw_filename + "." + color_plane_name + ".tiff"
    options['metadata'] = {'DocumentName': tiff_filename}
    tifffile.imsave(tiff_filename, color_planes[color_plane_name]['2D'].astype(bit_depth_type), options)

def tiff_rgb_writer(raw_filename, color_planes, **options):
  # Average green color planes
  # We're going to write a 16bit TIFF file since an 8bit file would look like garbage, plus we would lose quite a 
  # large amount of the camera sensor and ADC sensitivity.
  # Casting the averaged (float) value to uint16 appears to perform a floor() on the value.  1266.5 => 1266
  green_color_plane = (( color_planes["G1"]["2D"] + color_planes["G2"]["2D"] ) / 2.0).astype('uint16')
  red_color_plane = color_planes["R"]["2D"].astype('uint16')
  blue_color_plane = color_planes["B"]["2D"].astype('uint16')

  # Combine color plane arrays
  # see: https://docs.scipy.org/doc/numpy/reference/generated/numpy.stack.html#numpy.stack
  rgb_color_planes = np.stack((red_color_plane, green_color_plane, blue_color_plane), axis=-1)

  tiff_filename = raw_filename + ".RGB.tiff"
  options['photometric'] = 'rgb'
  options['metadata'] = {'DocumentName': tiff_filename}
  tifffile.imsave(tiff_filename, rgb_color_planes, options)

def plot_color_planes_histogram(color_planes, bins, raw_bit_depth):
  # High DPI screen plot resolution hack
  # TODO: figure out how to add some intelligence for handling different display DPIs
  # Qt5Agg plotting backend seems to handle this gracefully (and plots faster!)
  #mpl.rcParams['figure.dpi'] = 300

  # Switch matplotlib to greyscale mode
  # TODO: do we still need this?
  #plt.gray()

  for color_plane_name in color_planes:
    # Use Numba to compute histogram, more performant than simply using numpy
    color_plane_hist, color_plane_hist_bins = math.numba_histogram(
      color_planes[color_plane_name]["1D"],
      bins
    )

    # Create plot for a basic histogram of this color plane
    plt.plot(color_plane_hist_bins[:-1], color_plane_hist, 
             color=math.get_color_shade(color_plane_name), 
             alpha=0.75, 
             linewidth=1,
             label=color_plane_name
    )

    # Mess with axes dimensions
    # TODO: implement args range_max & range_min
    ax = plt.gca();
    ax.set_ylim(0.0)
    ax.set_xlim(0.0, 2**raw_bit_depth)

  # Draw histogram plot
  plt.title("RAW Image ADU counts")
  plt.xlabel('ADU')
  plt.ylabel('Count')
  plt.legend()
  plt.show()

  # Useful for performance testing
  # plt.show(block=False)
  # plt.pause(1)
  # plt.close()

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
  with rawpy.imread(byteio) as raw:
  #  rgb = raw.postprocess()
    print("Black level per channel: ", raw.black_level_per_channel)
    print("Camera White Balance: ", raw.camera_whitebalance)
    print("Camera Color Description: ", raw.color_desc)
  #  print("Camera Color Matrix: ", raw.color_matrix)
    print("Daylight White Balance: ", raw.daylight_whitebalance)
    print("Number of Colors: ", raw.num_colors)
  #  print("Raw Colors: ", raw.raw_colors)
    print("Raw Type: ", raw.raw_type)
    print("Sizes: ", raw.sizes)

    # Get RAW CFA image data for overall stats
    raw_bayer_plane = raw.raw_image_visible

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
    color_plane_count = raw.num_colors + 1

    # Extract individual color planes
    color_plane_map = math.get_color_plane_map(color_plane_count, raw.color_desc)

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



  #print("Raw Image: ", raw.raw_image)
#  print("Raw Image (Visible): ", raw.raw_image_visible)
#  print("Raw Pattern: ", raw.raw_pattern)
#
#  print("Raw Colors (Visible): ", raw.raw_colors_visible)

def enhance_rawpixels(hot_pixel_file, dead_pixel_file, raw_filenames):
  # See: https://letmaik.github.io/rawpy/api/rawpy.enhance.html
  dead_pixels = rawpy.enhance.find_bad_pixels(raw_filenames, find_hot=False, find_dead=True, confirm_ratio=1)
  hot_pixels = rawpy.enhance.find_bad_pixels(raw_filenames, find_hot=True, find_dead=False, confirm_ratio=1)
  #bad_pixels = rawpy.enhance.find_bad_pixels(raw_files, find_hot=True, find_dead=True, confirm_ratio=0.9)
  #bad_pixels = rawpy.enhance.find_bad_pixels(['focus-test-inf-_shutterspeed-30_10-02-20_CRW_5737.CRW'], find_hot=True, find_dead=False, confirm_ratio=0.9)

  # Eventually we should just write a complete RAW image conversion script in Python
  # This could include calling:
  # rawpy.enhance.repair_bad_pixels

  # Since we're still processing with dcraw/rawtran, we need the equivalent coordinates
  # This should account for image area borders, etc...
  rawpy.enhance.save_dcraw_bad_pixels(dead_pixel_file, dead_pixels)
  rawpy.enhance.save_dcraw_bad_pixels(hot_pixel_file, hot_pixels)

