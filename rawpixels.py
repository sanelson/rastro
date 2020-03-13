#!/bin/env python3
import rawpy
import rawpy.enhance
import argparse

# Process command line arguments
parser = argparse.ArgumentParser(description='Show Raw file(s) bad pixels')
parser.add_argument('--hot_pixel_file', help='Hot pixel filename')
parser.add_argument('--dead_pixel_file', help='Dead pixel filename')
parser.add_argument('raw_files', nargs='+', help='Raw Filenames for analysis', type=str)

args = parser.parse_args()
raw_files = args.raw_files
dead_pixel_file = args.dead_pixel_file
hot_pixel_file = args.hot_pixel_file

# See: https://letmaik.github.io/rawpy/api/rawpy.enhance.html
dead_pixels = rawpy.enhance.find_bad_pixels(raw_files, find_hot=False, find_dead=True, confirm_ratio=1)
hot_pixels = rawpy.enhance.find_bad_pixels(raw_files, find_hot=True, find_dead=False, confirm_ratio=1)
#bad_pixels = rawpy.enhance.find_bad_pixels(raw_files, find_hot=True, find_dead=True, confirm_ratio=0.9)
#bad_pixels = rawpy.enhance.find_bad_pixels(['focus-test-inf-_shutterspeed-30_10-02-20_CRW_5737.CRW'], find_hot=True, find_dead=False, confirm_ratio=0.9)

# Eventually we should just write a complete RAW image conversion script in Python
# This could include calling:
# rawpy.enhance.repair_bad_pixels
# For now though, we will use both libraw and dcraw/rawtran together
# TODO: Look at porting rawtran to use libraw?

# Since we're still processing with dcraw/rawtran, we need the equivalent coordinates
# This should account for image area borders, etc...
rawpy.enhance.save_dcraw_bad_pixels(dead_pixel_file, dead_pixels)
rawpy.enhance.save_dcraw_bad_pixels(hot_pixel_file, hot_pixels)
