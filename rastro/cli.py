# -*- coding: utf-8 -*-

"""rastro.cli: provides entry point main()."""

import argparse
import sys
from os.path import basename
from . import __version__ as VERSION

# Import our libraries
#from rastro.extract import raw, exif
from rastro.extract import raw
from rastro.convert import tiff, fits
from rastro.analyze import histogram, stats, rawpixels

def main():
  # Used the following guides to organize this python project
  #  * https://github.com/jgehrcke/python-cmdline-bootstrap
  
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
     f. Use local Astrometry.net installation to plate solve (should be easy to test on Ubuntu)
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

  # Links:
  # https://docs.scipy.org/doc/numpy/reference/maskedarray.generic.html
  # https://github.com/semolex/astrawpy/blob/master/cfa.py
  
  # Notes
  # 1. Try to determine original raw file image depth in order to build an accurate histogram
  #    a. Yuck, this is harder than I thought: https://www.libraw.org/node/2205
  # 2. Profile python scripts using pyinstrument
  #    a. eg. pyinstrument /opt/rawconvert/raw_analyze.py 20200310_0065.cr2
  
  # Set some variables
  # Default bit RAW image bit depth
  # There are alot of factors at play with regards to raw bit depth.  Mostly this is just used to sanely scale the 
  # plotted histogram so that it corresponds with the camera ADU values.  My math and assumptions are very Canon EOS
  # specific, other cameras have different sensor and ADC configurations which might make my analysis worthless.
  raw_bit_depth = 14

  # Grab the invocation command
  rastro_command = " ".join([basename(sys.argv[0])] + sys.argv[1:])
  #print(rastro_command)
  
  # Process command line arguments
  #parser = argparse.ArgumentParser(description='Extract and convert RAW camera files.')
  parser = argparse.ArgumentParser(description='Process and analyze RAW camera files.')
  parser.add_argument('-v', '--verbosity', help='Enable more logging output', type=bool, default=False)
  parser.add_argument('--version', action='version', version='%(prog)s {}'.format(VERSION))
  
  # Enable main commands (first level subparsers)
  commands = parser.add_subparsers(
      title='commands',
      description='valid commands',
      help='Command help',
      dest='command'
  )
  
  # Add command for conversion tasks
  parser_convert = commands.add_parser('convert', help='Convert RAW image data')

  # Enable conversion subcommands
  convert_commands = parser_convert.add_subparsers(
      title='convert_commands',
      description='valid conversion commands',
      help='Convert Command help',
      dest='convert_command'
  )
 
  # Add subcommands for different image types
  parser_tiff = convert_commands.add_parser('tiff', help='Export in TIFF format')
  # TODO: ensure RGB image output must be in uint8
  parser_tiff.add_argument(
      '--bit_depth_type',
      type=str,
      help='Bit depth and type of TIFF file',
      choices=['uint8','uint16','float32'],
      default='uint16'
  )
  parser_tiff.add_argument(
      '--all_channels',
      action='store_true',
      help='Emulate TIFF file output of libraw 4channel example program'
  )
  parser_tiff.add_argument(
      '--uninterpolated_rgb',
      action='store_true',
      help='Create uninterpolated 16bit RGB TIFF similar to <dcraw -h -T>',
  )
  
  # Add FITS subcommand
  parser_fits = convert_commands.add_parser('fits', help='Export in FITS format')
  
  parser_fits.add_argument(
      '--color_plane_name',
      type=str,
      help='Single color plane/channel to export in FITS format',
      choices=['R', 'G1', 'G2', 'B'],
      default='G1'
  )

  # Add command for analysis tasks
  parser_analyze = commands.add_parser('analyze', help='Analyze RAW image data')

  # Enable analysis subcommands
  analyze_commands = parser_analyze.add_subparsers(
      title='analyze_commands',
      description='valid analysis commands',
      help='Analyze Command help',
      dest='analyze_command'
  )
 
  # Add histogram subcommand
  parser_histogram = analyze_commands.add_parser('histogram', help='Compute histogram of RAW image data')
  parser_histogram.add_argument('--raw_bit_depth', type=int, help='Bit depth of original RAW image', default=raw_bit_depth)
  parser_histogram.add_argument('--bins', type=int, help='Number of bins to divide histogram into', default=256)
  # bins will be scaled to be equal to range if a range that is smaller than bins is selected
  parser_histogram.add_argument('--range_max', type=int, help='Maximum value to represent on histogram', default=raw_bit_depth)
  parser_histogram.add_argument('--range_min', type=int, help='Minimum value to represent on histogram', default=0)

  # Add stats subcommand
  parser_stats = analyze_commands.add_parser('stats', help='Output basic stats of RAW image data')

  # Add rawpixels subcommand
  parser_rawpixels = analyze_commands.add_parser('rawpixels', help='Try to determine hot/bad pixels in one or more RAW image files')

  # Process rawpixel enhancement args
  #parser_rawpixels.add_argument('--hot_pixel_file', nargs=1, help='Hot pixel filename', type=str)
  #parser_rawpixels.add_argument('--dead_pixel_file', nargs=1, help='Dead pixel filename', type=str)
  parser_rawpixels.add_argument('--hot_pixel_file', help='Hot pixel filename', type=str)
  parser_rawpixels.add_argument('--dead_pixel_file', help='Dead pixel filename', type=str)

  # Add argument for our input file(s)
  #parser.add_argument('raw_filenames', help='Raw Filename(s) for processing', nargs=argparse.REMAINDER, type=str)
  parser.add_argument('raw_filenames', help='Raw Filename(s) for processing', nargs='*', type=str)

  # Parse the args and make them available
  #args = parser.parse_args()
  # This is really gross but it works for now. For some reason argparse trips over more than one raw filename.
  args, raw_filenames = parser.parse_known_args()

  #print("args :", args)
  #print("unknown :", unknown)
  #print("raw_filenames :", raw_filenames)


  if args.command == 'analyze' and args.analyze_command == 'stats':
    # TODO: pop an error if trying to run basic stats on more than one file.
    #      OR, we could fall back to a summarization mode?
    stats.output_basic_stats(raw_filenames[0])
  elif args.command == 'analyze' and args.analyze_command == 'rawpixels':
    # Note that this function takes one or more RAW files.  The more the better for analysis.
    # TODO: Pass hot/dead pixel files as named arguments.  If no output files are provided, 
    # simply output pixel list to STDOUT
    rawpixels.enhance_rawpixels(args.hot_pixel_file, args.dead_pixel_file, raw_filenames)
  else:
    # Extract color planes from RAW file
    #color_planes = raw.reader(raw_filenames[0])
    pass

  # Write output
  if args.command == 'convert':
    if args.convert_command == 'tiff':
      if args.all_channels:
        for raw_filename in raw_filenames:
          color_planes = raw.reader(raw_filename)

          # Emulate libraw 4channel example tiff file output
          tiff.all_channels_writer(
              raw_filename,
              color_planes,
              args.bit_depth_type,
              compress=6
          )
      elif args.uninterpolated_rgb:
        for raw_filename in raw_filenames:
          color_planes = raw.reader(raw_filename)

          # Most basic extraction mode, write single RGB tiff with no interpolation.  Kind of like "dcraw -h -T".
          # see interesting discussion here: https://photo.stackexchange.com/questions/92926/is-there-a-demosaicing-algorithm-that-discards-the-2%C2%BA-green-pixel-and-produces-a
          # Method #1, do all raw processing manually
          # Method #2, use libraw's handy RGB conversion
          # Initially we will just do method 1 to ensure data is as unmodified as possible.
          tiff.rgb_writer(
              raw_filename,
              color_planes,
              compress=6
          )
      else:
        for raw_filename in raw_filenames:
          color_planes = raw.reader(raw_filename)

          # By default, just spit out an RGB tiff
          tiff.rgb_writer(
              raw_filename,
              color_planes,
              compress=6
          )
    elif args.convert_command == 'fits':
      if args.color_plane_name:
        # Translate EXIF data to FITS format 
        fits.single_channel_writer_header(raw_filenames, args.color_plane_name, rastro_command, VERSION)

#        for raw_filename in raw_filenames:
#          color_planes = raw.reader(raw_filename)
#
#          fits.single_channel_writer(
#              raw_filename,
#              color_planes[args.color_plane_name]['2D'],
#              args.color_plane_name
#          )
      else:
        # TBD
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
  if args.command == 'analyze':
    if args.analyze_command == 'histogram':
      color_planes = raw.reader(raw_filenames[0])
      histogram.plot_color_planes_histogram(color_planes, args.bins, args.raw_bit_depth)
    else:
      pass

