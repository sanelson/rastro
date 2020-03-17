import rawpy
import matplotlib as mpl
# TODO: See what backends are available and fallback to tkinter with a warning if none are available
mpl.use('Qt5Agg')  # Change plotting backend for increased performance: https://matplotlib.org/faq/usage_faq.html#what-is-a-backend
from matplotlib import pyplot as plt
import numpy as np
import numpy.ma as ma
import raw_math # Our computation routines
import tifffile # https://pypi.org/project/tifffile/  Good library for scientific image processing in TIFF format

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
    color_plane_map = raw_math.get_color_plane_map(color_plane_count, raw.color_desc)

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

def tiff_4channel_writer(raw_filename, color_planes, bit_depth_type, **options):
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
    color_plane_hist, color_plane_hist_bins = raw_math.numba_histogram(
      color_planes[color_plane_name]["1D"],
      bins
    )

    # Create plot for a basic histogram of this color plane
    plt.plot(color_plane_hist_bins[:-1], color_plane_hist, 
             color=raw_math.get_color_shade(color_plane_name), 
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






