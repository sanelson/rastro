#!/bin/env python3
import rawpy
import imageio
import argparse

# Process command line arguments
parser = argparse.ArgumentParser(description='Convert Raw camera files.')
parser.add_argument('-o', '--output', help='Filename for conversion output', type=str)
parser.add_argument('raw_file', help='Raw Filename for conversion', type=str)

args = parser.parse_args()
raw_file = args.raw_file
output_file = args.output

with rawpy.imread(raw_file) as raw:
    rgb = raw.postprocess()
imageio.imsave(output_file, rgb)
