# -*- coding: utf-8 -*-

import rawpy
import io
from astropy.io import fits
import pyexiv2
from pyexiv2.exif import ExifTag, ExifValueError

from datetime import timezone

from rastro.extract import raw

# TODO:
#   * Write unit tests for these functions!
#   * Create class which wraps RAW file open and metadata capture process

"""
FITS Reference Information

Links:
    https://heasarc.gsfc.nasa.gov/docs/fcg/standard_dict.html
"""

def single_channel_writer_header(raw_filenames, color_plane_name, rastro_command, VERSION):
  # Handle multiple raw files
  for raw_filename in raw_filenames:
    # see: https://python3-exiv2.readthedocs.io/en/latest/api.html#buffer
    # Little hack to not have to open the RAW file more than once to gather stats/info
    metadata = pyexiv2.ImageMetadata(raw_filename)
    metadata.read()

    # Check for weird edge case noticed on Canon 40D with nonstandard lens and the stored value for 
    # Exif.Photo.ApertureValue, typically for a nonstandard lens the value would should be 0 or -2147483648
    # For some reason the value is set to POSITIVE 2147483648. This causes the APEX value calculation to return
    # basically an infinite value.  See: https://rt.cpan.org/Public/Bug/Display.html?id=29609
    # Ideally, we'll squash the garbage value with an manually specified aperture value during image capture. But just in case.
    if metadata['Exif.Photo.ApertureValue'].value == int(2**32/2):
      aperture = 'F0.0'
    else:
      aperture = metadata['Exif.Photo.ApertureValue'].value
  
    # Build FITS header data structure
    # This initial structure is inspired by the format used by rawtran.
    # See https://www.aavso.org/aavso-extended-file-format
    #     https://diffractionlimited.com/help/maximdl/FITS_File_Header_Definitions.htm
    #     https://fits.gsfc.nasa.gov/fits_standard.html
    #     https://www.cv.nrao.edu/fits/documents/standards/year2000.txt
    # Add option to include sub-second timing if available
    #    * Exif.Photo.SubSecTime and strftime('%Y-%m-%dT%H:%M:%S.%f')
    # Add option to choose time zone of RAW camera set image timestamp.  Default would be to use system timezone on computer where
    # rastro is run.  UTC would probably be the best choice in the future on the camera.  Newer cameras hopefully support 
    # datetime with TZ information.
    # CRITICAL! Write tests to check these date conversions and assumptions...
    #print(metadata['Exif.Photo.ApertureValue'].value)
    fits_header = {
       'PHOTSYS': ('Instrumental', 'Photometry filter system'),
       'FILTER': ('T' + color_plane_name[0], 'Spectral filter'),    # Using "tri-color" RGB nomenclature from AAVSO for DSLR & CCD
       'DATE-OBS': (metadata['Exif.Image.DateTime'].value.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f'), 'Date and time of the observation'), 
       # Default in FITS standard is UTC
       # represents the START of observation
       'TIMESYS': ('UTC', 'Time system for dates'),
       'EXPTIME': (float(metadata['Exif.Photo.ExposureTime'].value), '[s] exposure time in seconds'),
       'ISO': (int(metadata['Exif.Photo.ISOSpeedRatings'].value), 'ISO speed'),
       'INSTRUME': (str(metadata['Exif.Image.Model'].value), 'Camera manufacturer and model'),
       #'APERTURE': ('f/' + str(float(metadata['Exif.Photo.ApertureValue'].value)), 'Aperture'),
       'APERTURE': (aperture, 'Aperture'),
#       'COMMENT': ('Command: ' + rastro_command),
#       'COMMENT': ('Created by rastro v' + VERSION + ' https://github.com/sanelson/rastro'),
      #('COMMENT', 'Additional EXIF data'),
      #('COMMENT', 'Sensor size: '),   # Get from rawpy
    }
    # Grab the metadata we want
    #exif_data = {
    #        '':'',
    #}
    #for key in metadata.exif_keys:
    #  try:
    #    # print(str(key) + "=" + str(metadata[key].value))
    #    print(str(key) + "=" + str(metadata[key]))
    #  except ExifValueError:
    #    print("Unable to decode raw value for key [{}]".format(key))
  
    # Create io buffer to re-use with rawpy
    byteio = io.BytesIO(metadata.buffer)
  
  #  # Operate on the IO buffer
  #  with rawpy.imread(byteio) as rawimage:
    color_planes = raw.reader(byteio)

    # Incorporate our custom header entries into the standard header
    hdr = fits.Header()
    hdr.update(fits_header)
    hdr['COMMENT'] = 'Command: ' + rastro_command
    hdr['COMMENT'] = 'Created by rastro v' + VERSION + ' https://github.com/sanelson/rastro'
    hdu = fits.PrimaryHDU(color_planes[color_plane_name]['2D'], header=hdr)
  
    hdul = fits.HDUList([hdu])
  
    fits_filename = raw_filename + '.' + color_plane_name + '.fits'
    hdul.writeto(fits_filename)
 

def single_channel_writer(raw_filename, color_plane, color_plane_name, **options):
  hdu = fits.PrimaryHDU(color_planes[color_plane_name]['2D'])

  hdul = fits.HDUList([hdu])

  fits_filename = raw_filename + '.' + color_plane_name + '.fits'
  hdul.writeto(fits_filename)


