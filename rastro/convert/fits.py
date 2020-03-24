# -*- coding: utf-8 -*-

from astropy.io import fits

def single_channel_writer(raw_filename, color_plane, color_plane_name, **options):
  hdu = fits.PrimaryHDU(color_plane)

  hdul = fits.HDUList([hdu])

  fits_filename = raw_filename + '.' + color_plane_name + '.fits'
  hdul.writeto(fits_filename)


