#!/bin/env python3
import argparse
import raw_math  # Our computation routines
import raw_util  # Our utility routines

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
parser.add_argument('--version', action='version', version='%(prog)s 0.1')

# Enable subparsers/subcommands
subparsers = parser.add_subparsers(
    title='subcommands',
    description='valid subcommands',
    help='Sub command help',
    dest='command'
)

# Add subcommands for different image types
parser_tiff = subparsers.add_parser('tiff', help='Export in TIFF format')
# TODO: ensure RGB image output must be in uint8
parser_tiff.add_argument(
    '--bit_depth_type',
    type=str,
    help='Bit depth and type of TIFF file',
    choices=['uint8','uint16','float32'],
    default='uint16'
)
parser_tiff.add_argument(
    '--4channel',
    type=bool,
    help='Emulate TIFF file output of libraw 4channel example program',
    default=False
)
parser_tiff.add_argument(
    '--uninterpolated_rgb',
    type=bool,
    help='Create uninterpolated 16bit RGB TIFF similar to <dcraw -h -T>',
    default=True
)

# Add argument for our input file
parser.add_argument('raw_filename', help='Raw Filename for extraction', type=str)

# Parse the args and make them available
args = parser.parse_args()

# Extract color planes from RAW file
color_planes = raw_util.raw_reader(args.raw_filename)

# Write output
if args.command == 'tiff':
  # Emulate libraw 4channel example tiff file output
  raw_util.tiff_4channel_writer(
      args.raw_filename,
      color_planes,
      args.bit_depth_type,
      compress=6
  )

  # Most basic extraction mode, write single RGB tiff with no interpolation.  Kind of like "dcraw -h -T".
  # see interesting discussion here: https://photo.stackexchange.com/questions/92926/is-there-a-demosaicing-algorithm-that-discards-the-2%C2%BA-green-pixel-and-produces-a
  # Method #1, do all raw processing manually
  # Method #2, use libraw's handy RGB conversion
  # Initially we will just do method 1 to ensure data is as unmodified as possible.
  raw_util.tiff_rgb_writer(
      args.raw_filename,
      color_planes,
      compress=6
  )
elif args.command == 'fits':
  # Placeholder for FITS file support
  pass
elif args.command == 'png':
  # Placeholder for PNG file support
  pass
elif args.command == 'jpeg':
  # Placeholder for JPEG file support
  pass
elif args.command == 'ppm':
  # Placeholder for PPM file support
  pass
elif args.command == 'pgm':
  # Placeholder for PGM file support
  pass
elif args.command == 'dng':
  # Placeholder for DNG file support
  # see: https://github.com/schoolpost/PyDNG/blob/master/pydng.py
  #      https://github.com/krontech/chronos-utils/tree/master/python_raw2dng
  pass
else:
  # Due to how subparsers work in Python, we never actually make it here...  Still figuring out if I care :)
  pass
