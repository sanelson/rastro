# -*- coding: utf-8 -*-

import matplotlib as mpl
# TODO: See what backends are available and fallback to tkinter with a warning if none are available
mpl.use('Qt5Agg')  # Change plotting backend for increased performance: https://matplotlib.org/faq/usage_faq.html#what-is-a-backend
from matplotlib import pyplot as plt

import numba
import numpy as np

# Stolen from numba histogram example: https://numba.pydata.org/numba-examples/examples/density_estimation/histogram/results.html
@numba.jit(nopython=True)
def get_bin_edges(a, bins):
  bin_edges = np.zeros((bins+1,), dtype=np.float64)
  a_min = a.min()
  a_max = a.max()
  delta = (a_max - a_min) / bins
  for i in range(bin_edges.shape[0]):
    bin_edges[i] = a_min + i * delta
  
  bin_edges[-1] = a_max  # Avoid roundoff error on last point
  return bin_edges


@numba.jit(nopython=True)
def compute_bin(x, bin_edges):
  # assuming uniform bins for now
  n = bin_edges.shape[0] - 1
  a_min = bin_edges[0]
  a_max = bin_edges[-1]

  # special case to mirror NumPy behavior for last bin
  if x == a_max:
    return n - 1 # a_max always in last bin

  bin = int(n * (x - a_min) / (a_max - a_min))

  if bin < 0 or bin >= n:
    return None
  else:
    return bin


@numba.jit(nopython=True)
def numba_histogram(a, bins):
  hist = np.zeros((bins,), dtype=np.intp)
  bin_edges = get_bin_edges(a, bins)

  for x in a.flat:
    bin = compute_bin(x, bin_edges)
    if bin is not None:
      hist[int(bin)] += 1

  return hist, bin_edges

def get_color_shade(color_plane_name):
  """
    Return a floating point RGB color array definition from a color plane name.
    Multiple instances of the same color plane have their color shifted using the color
    plane index.
  """
  # Only supports RGB image color planes for now
  color_shade = color_plane_name[0].upper()

  # Check for color plane index
  try:
    color_shade_instance = int(color_plane_name[1])
  except IndexError:
    color_shade_instance = 1

  color_shades_map = {
      "R": [1.0, 0, 0],
      "G": [0, 1.0, 0],
      "B": [0, 0, 1.0]
  }

  color_shade_rgb = [rgb_shade / float(color_shade_instance) for rgb_shade in color_shades_map[color_shade]]

  return color_shade_rgb

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
    color_plane_hist, color_plane_hist_bins = numba_histogram(
      color_planes[color_plane_name]["1D"],
      bins
    )

    # Create plot for a basic histogram of this color plane
    plt.plot(color_plane_hist_bins[:-1], color_plane_hist, 
             color=get_color_shade(color_plane_name), 
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


