#!/bin/env python3
import rawpy
import imageio
import argparse
import matplotlib as mpl
# TODO: See what backends are available and fallback to tkinter with a warning if none are available
mpl.use('Qt5Agg')  # Change plotting backend for increased performance: https://matplotlib.org/faq/usage_faq.html#what-is-a-backend
from matplotlib import pyplot as plt
import numpy as np
import numpy.ma as ma
import raw_math  # Our computation routines

# High DPI screen plot resolution hack
# TODO: figure out how to add some intelligence for handling different display DPIs
# Qt5Agg plotting backend seems to handle this gracefully (and plots faster!)
#mpl.rcParams['figure.dpi'] = 300

# Links:
# https://docs.scipy.org/doc/numpy/reference/maskedarray.generic.html
# https://github.com/semolex/astrawpy/blob/master/cfa.py

# Notes
# 1. Try to determine original raw file image depth in order to build an accurate histogram
#    a. Yuck, this is harder than I thought: https://www.libraw.org/node/2205
# 2. Profile python scripts using pyinstrument
#    a. eg. pyinstrument /opt/rawconvert/raw_analyze.py 20200310_0065.cr2

# Process command line arguments
parser = argparse.ArgumentParser(description='Analyze Raw camera files.')
parser.add_argument('-v', '--verbosity', help='Enable more logging output', type=bool, default=False)
subparsers = parser.add_subparsers(help='Sub command help')

# Add histogram subcommand
parser_histogram = subparsers.add_parser('histogram', help='Compute histogram of RAW image data')
parser_histogram.add_argument('--bit_depth', type=int, help='Bit depth of original RAW image', default=14)
parser_histogram.add_argument('--bins', type=int, help='Number of bins to divide histogram into', default=256)
# bins will be scaled to be equal to range if a range that is smaller than bins is selected
parser_histogram.add_argument('--range_max', type=int, help='Maximum value to represent on histogram', default=2**14)
parser_histogram.add_argument('--range_min', type=int, help='Minimum value to represent on histogram', default=0)

# Add argument for our input file
parser.add_argument('raw_file', help='Raw Filename for analysis', type=str)

# Parse the args and make them available
args = parser.parse_args()

# Switch matplotlib to greyscale mode
plt.gray()

# Open the RAW file for reading
with rawpy.imread(args.raw_file) as raw:
  color_plane_count = raw.num_colors + 1

  # Extract individual color planes
  color_plane_map = raw_math.get_color_plane_map(color_plane_count, raw.color_desc)
  for i in range(color_plane_count):
    # TODO: Document exactly what is taking place with this numpy array transformation
    mask = (raw.raw_colors_visible != i)
    color_plane_masked = ma.masked_array(np.copy(raw.raw_image_visible), mask)
    # TODO: Do camera sensors ever have an odd number of pixels in x/y?  This would skew results slightly.
    half_size_shape = tuple(int(dim/2) for dim in raw.raw_image_visible.shape)
    color_plane_1d = color_plane_masked[~color_plane_masked.mask]

    # Reshape the array (not needed for histogram, probably useful for other future analysis functions)
    # TODO: Is this the best way?
    # See: https://docs.scipy.org/doc/numpy/reference/generated/numpy.reshape.html
    # color_plane_2d = np.reshape(color_plane_1d, half_size_shape)
    # print('Reshaped Color plane data: \n', color_plane_2d.data)

    # Use Numba to compute histogram, more performant than simply using numpy
    color_plane_hist, color_plane_hist_bins = raw_math.numba_histogram(color_plane_1d, args.bins)

    # Create plot for a basic histogram of this color plane
    plt.plot(color_plane_hist_bins[:-1], color_plane_hist, 
             color=raw_math.get_color_shade(color_plane_map[i]), 
             alpha=0.75, 
             linewidth=1,
             label=color_plane_map[i])

    # Mess with axes dimensions
    # TODO: implement args range_max & range_min
    ax = plt.gca();
    ax.set_ylim(0.0)
    ax.set_xlim(0.0, 2**args.bit_depth)

  # Draw histogram plot
  plt.title("RAW Image ADU counts")
  plt.xlabel('ADU')
  plt.ylabel('Count')
  plt.legend()
  plt.show()

#  Useful for performance testing
#  plt.show(block=False)
#  plt.pause(1)
#  plt.close()
