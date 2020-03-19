# -*- coding: utf-8 -*-
"""
This module contains the mathmatical helper functions for the various raw utilities.
"""

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


