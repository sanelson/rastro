import rawpy
import numpy as np
import numpy.ma as ma
import raw_math # Our computation routines
import tifffile # https://pypi.org/project/tifffile/  Good library for scientific image processing in TIFF format

def raw_reader(raw_filename):
  """
     Takes a RAW filename as an argument and returns a dictionary containing 1D and 2D representations of
     the image data.
  """
  # TODO: slurp out metadata in this function?
  # see: https://www.libraw.org/node/2352  not sure if rawpy supports this (yet).
  # Open the RAW file for reading
  with rawpy.imread(raw_filename) as raw:
    color_plane_count = raw.num_colors + 1

    # Extract individual color planes
    color_plane_map = raw_math.get_color_plane_map(color_plane_count, raw.color_desc)

    # Color plane dictionary 
    # TODO: make this more pythony and use an OO approach
    color_planes = {}
    for i in range(color_plane_count):
      color_planes[color_plane_map[i]] = {}

      # TODO: Document exactly what is taking place with this numpy array transformation
      mask = (raw.raw_colors_visible != i)
      color_plane_masked = ma.masked_array(np.copy(raw.raw_image_visible), mask)
      # TODO: Do camera sensors ever have an odd number of pixels in x/y?  This would skew results slightly.
      half_size_shape = tuple(int(dim/2) for dim in raw.raw_image_visible.shape)
      color_planes[color_plane_map[i]]["1d"] = color_plane_masked[~color_plane_masked.mask]

      # Reshape the array
      # TODO: Is this the best way?
      # See: https://docs.scipy.org/doc/numpy/reference/generated/numpy.reshape.html
      color_planes[color_plane_map[i]]["2d"] = np.reshape(color_planes[color_plane_map[i]]["1d"], half_size_shape)

    return color_planes

def tiff_4channel_writer(raw_filename, color_planes, bit_depth_type, **options):
  # Write color plane to file
  for color_plane_name in color_planes:
    tiff_filename = raw_filename + "." + color_plane_name + ".tiff"
    options['metadata'] = {'DocumentName': tiff_filename}
    tifffile.imsave(tiff_filename, color_planes[color_plane_name]['2d'].astype(bit_depth_type), options)
