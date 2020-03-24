import tifffile # https://pypi.org/project/tifffile/  Good library for scientific image processing in TIFF format

def all_channels_writer(raw_filename, color_planes, bit_depth_type, **options):
  # Write color plane to file
  for color_plane_name in color_planes:
    tiff_filename = raw_filename + "." + color_plane_name + ".tiff"
    options['metadata'] = {'DocumentName': tiff_filename}
    tifffile.imsave(tiff_filename, color_planes[color_plane_name]['2D'].astype(bit_depth_type), options)

def rgb_writer(raw_filename, color_planes, **options):
  # Average green color planes
  # We're going to write a 16bit TIFF file since an 8bit file would look like garbage, plus we would lose quite a 
  # large amount of the camera sensor and ADC sensitivity.
  # Casting the averaged (float) value to uint16 appears to perform a floor() on the value.  1266.5 => 1266
  green_color_plane = (( color_planes["G1"]["2D"] + color_planes["G2"]["2D"] ) / 2.0).astype('uint16')
  red_color_plane = color_planes["R"]["2D"].astype('uint16')
  blue_color_plane = color_planes["B"]["2D"].astype('uint16')

  # Combine color plane arrays
  # see: https://docs.scipy.org/doc/numpy/reference/generated/numpy.stack.html#numpy.stack
  rgb_color_planes = np.stack((red_color_plane, green_color_plane, blue_color_plane), axis=-1)

  tiff_filename = raw_filename + ".RGB.tiff"
  options['photometric'] = 'rgb'
  options['metadata'] = {'DocumentName': tiff_filename}
  tifffile.imsave(tiff_filename, rgb_color_planes, options)

