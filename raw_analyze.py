#!/bin/env python3
import argparse
import raw_math  # Our computation routines
import raw_util  # Our utility routines

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

# Process command line arguments
parser = argparse.ArgumentParser(description='Analyze Raw camera files.')
parser.add_argument('-v', '--verbosity', help='Enable more logging output', type=bool, default=False)
parser.add_argument('--version', action='version', version='%(prog)s 0.1')

# Enable subparsers/subcommands
subparsers = parser.add_subparsers(
    title='subcommands',
    description='valid subcommands',
    help='Sub command help',
    dest='command'
)

# Add histogram subcommand
parser_histogram = subparsers.add_parser('histogram', help='Compute histogram of RAW image data')
parser_histogram.add_argument('--raw_bit_depth', type=int, help='Bit depth of original RAW image', default=raw_bit_depth)
parser_histogram.add_argument('--bins', type=int, help='Number of bins to divide histogram into', default=256)
# bins will be scaled to be equal to range if a range that is smaller than bins is selected
parser_histogram.add_argument('--range_max', type=int, help='Maximum value to represent on histogram', default=raw_bit_depth)
parser_histogram.add_argument('--range_min', type=int, help='Minimum value to represent on histogram', default=0)

# Add argument for our input file
parser.add_argument('raw_filename', help='Raw Filename for analysis', type=str)

# Parse the args and make them available
args = parser.parse_args()

# Extract color planes from RAW file
color_planes = raw_util.raw_reader(args.raw_filename)

# Write output
if args.command == 'histogram':
  raw_util.plot_color_planes_histogram(color_planes, args.bins, args.raw_bit_depth)
else:
  pass
