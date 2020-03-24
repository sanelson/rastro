# -*- coding: utf-8 -*-

from rawpy import enhance

def enhance_rawpixels(hot_pixel_file, dead_pixel_file, raw_filenames):
  # See: https://letmaik.github.io/rawpy/api/rawpy.enhance.html
  dead_pixels = rawpy.enhance.find_bad_pixels(raw_filenames, find_hot=False, find_dead=True, confirm_ratio=1)
  hot_pixels = rawpy.enhance.find_bad_pixels(raw_filenames, find_hot=True, find_dead=False, confirm_ratio=1)
  #bad_pixels = rawpy.enhance.find_bad_pixels(raw_files, find_hot=True, find_dead=True, confirm_ratio=0.9)
  #bad_pixels = rawpy.enhance.find_bad_pixels(['focus-test-inf-_shutterspeed-30_10-02-20_CRW_5737.CRW'], find_hot=True, find_dead=False, confirm_ratio=0.9)

  # Eventually we should just write a complete RAW image conversion script in Python
  # This could include calling:
  # rawpy.enhance.repair_bad_pixels

  # Since we're still processing with dcraw/rawtran, we need the equivalent coordinates
  # This should account for image area borders, etc...
  rawpy.enhance.save_dcraw_bad_pixels(dead_pixel_file, dead_pixels)
  rawpy.enhance.save_dcraw_bad_pixels(hot_pixel_file, hot_pixels)

