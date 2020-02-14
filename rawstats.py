#!/bin/env python3
import rawpy
import imageio
import argparse

# Process command line arguments
parser = argparse.ArgumentParser(description='Show Raw camera file statistics.')
parser.add_argument('raw_file', help='Raw Filename for analysis', type=str)

args = parser.parse_args()
raw_file = args.raw_file

with rawpy.imread(raw_file) as raw:
#  rgb = raw.postprocess()
  print("Black level per channel: ", raw.black_level_per_channel)
  print("Camera White Balance: ", raw.camera_whitebalance)
  print("Camera Color Description: ", raw.color_desc)
#  print("Camera Color Matrix: ", raw.color_matrix)
  print("Daylight White Balance: ", raw.daylight_whitebalance)
  print("Number of Colors: ", raw.num_colors)
#  print("Raw Colors: ", raw.raw_colors)
  print("Raw Type: ", raw.raw_type)
  print("Sizes: ", raw.sizes)


  #rgb = raw.postprocess(no_auto_scale=True, no_auto_bright=True, output_bps=16, use_camera_wb=False, use_auto_wb=False, output_color=rawpy.ColorSpace.raw, demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD)
#  rgb = raw.postprocess(no_auto_scale=True, no_auto_bright=True, output_bps=16, use_camera_wb=False, use_auto_wb=False, output_color=rawpy.ColorSpace.raw)
  rgbg = raw.postprocess(gamma=(1,1), no_auto_bright=True, output_bps=16, four_color_rgb=True, no_auto_scale=True, demosaic_algorithm=0)

  #print("Num rows: ", len(rgb[:,:]))
  #print("Num columns: ", len(rgb[0]))
#  red, green1, blue, green2 = rgbg[:,:,0], rgbg[:,:,1], rgbg[:,:,2], rgbg[:,:,3]
  print(rgbg)

#  print(red)
#  print(green1)
#  print(blue)
#  print(green2)


  #print("Raw Image: ", raw.raw_image)
#  print("Raw Image (Visible): ", raw.raw_image_visible)
#  print("Raw Pattern: ", raw.raw_pattern)
#
#  print("Raw Colors (Visible): ", raw.raw_colors_visible)
