#!/bin/env python3
import rawpy
import tifffile # https://pypi.org/project/tifffile/  Good library for scientific image processing in TIFF format
import imageio
import argparse
import matplotlib as mpl
import numpy as np
import numpy.ma as ma
import raw_math  # Our computation routines

"""
https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

TIFF file support
In order to build the imagecodecs dependency for tifffile, I had to install the following development packages
There are likely other dependencies that could be needed that I already had installed.

sudo apt install libaec-dev libblosc-dev libbrotli-dev libgif-dev libopenjp2-7-dev \
  libjxr-dev liblz4-dev lzma-dev liblzma-dev libsnappy-dev libtiff-dev libwebp-dev \
  libzopfli-dev libzstd-dev

Then
  pip3 install --user tifffile

ALTERNATIVE

You may also be able to install the imagecodecs-lite module which has fewer external library dependencies than
imagecodecs

  pip3 install --user imagecodecs-lite
Then
  pip3 install --user tifffile

FITS File support
https://docs.astropy.org/en/stable/io/fits/#creating-a-new-fits-file

TODO:
1. Add basic TIFF file export support.  Create 4 TIFF files, corresponding to each RAW color frame.
2. Add color plane selection option.  For instance, only output Green1 color plane.
3. Add basic FITS file export support.  Single color plane only.
4. Add FITS header handling support.  Copy basic information from EXIF data in RAW file.
5. Add advanced FITS header support.
   a. Option for earth coordinates (lat,long)
   b. Estimated/input sensor characteristics (gain, noise, etc...)
   c. Atmospheric extinction estimation (use WCS, geolocation and image timestamp to calculate atmospheric thickness)
   d. Add lens information that Astrometry.net solve-field can use to more quickly solve images.
      i.e. angular size of FOV
   e. Add tags to indicate image type (light, dark, flat, bias, etc...).  Is there a standard for this?
6. Have some math fun with color planes.
   a. Output averaged green plane (g1 + g2)/2 like rawtran "Gi" plane.
   b. Mess around with different interpolation methods to create a full resolution interpolated Green 
      frame from g1 and g2.  Could also use red and blue planes to increase interpolation accuracy.  
      I don't think this type of output would be useful for photometry, but it might be helpful for 
      finding small image details.  Plus, why waste that nice extra green data!
7. Add memory saving options like memory mapped files so that very large images can be processed

Stretch Goals:
1. Build easy to use binaries for different platforms using:
    https://hub.docker.com/r/cdrx/pyinstaller-windows
    https://pypi.org/project/py2app/
"""

# Process command line arguments
parser = argparse.ArgumentParser(description='Extract and convert RAW camera files.')
parser.add_argument('-v', '--verbosity', help='Enable more logging output', type=bool, default=False)
subparsers = parser.add_subparsers(help='Sub command help')

# Add subcommands for different image types
parser_tiff = subparsers.add_parser('tiff', help='Export in TIFF format')
# TODO: ensure RGB image output must be in uint8
parser_tiff.add_argument('--bit_depth_type', type=str, help='Bit depth and type of TIFF file', choices=["uint8","uint16","float32"], default='uint16')

# Add argument for our input file
parser.add_argument('raw_file', help='Raw Filename for extraction', type=str)

# Parse the args and make them available
args = parser.parse_args()

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

    # Reshape the array
    # TODO: Is this the best way?
    # See: https://docs.scipy.org/doc/numpy/reference/generated/numpy.reshape.html
    color_plane_2d = np.reshape(color_plane_1d, half_size_shape)

    # Use Numba to compute histogram, more performant than simply using numpy
    #color_plane_hist, color_plane_hist_bins = raw_math.numba_histogram(color_plane_1d, args.bins)

    # Create plot for a basic histogram of this color plane
    #plt.plot(color_plane_hist_bins[:-1], color_plane_hist, 
    #         color=raw_math.get_color_shade(color_plane_map[i]), 
    #         alpha=0.75, 
    #         linewidth=1,
    #         label=color_plane_map[i])

    # Write color plane to file
    tiff_filename = args.raw_file + "." + color_plane_map[i] + ".tiff"
    tifffile.imsave(tiff_filename, color_plane_2d.astype(args.bit_depth_type), metadata={'DocumentName': tiff_filename}, compress=6)
