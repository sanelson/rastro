# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import re
from setuptools import setup

version = re.search(
  '^__version__\s*=\s*"(.*)"',
  open('rastro/rastro.py').read(),
  re.M
).group(1)

with open("README.md", "rb") as f:
  long_description = f.read().decode("utf-8")

#with open('VERSION') as version_file:
#    version = version_file.read().strip()

setup(
  name = "rastro",
  packages = ["rastro"],
  entry_points = {
      "console_scripts": ['rastro = rastro.rastro:main']
    },
  version = version,
#  use_scm_version=True,
#  setup_requires=['setuptools_scm'],
  description = "Python tools for astronomical Raw image conversion and analysis using rawpy and libraw",
  long_description = long_description,
  long_description_content_type="text/markdown",
  author = "Sam Nelson",
  author_email = "sanelson@siliconfuture.net",
  url = "https://github.com/sanelson/rastro",
  install_requires=[
      'numpy', 'tiffile', 'matplotlib', 'rawpy', 'numba', 'astropy', 'py3exiv2'
  ],
  classifiers=[
      "Programming Language :: Python :: 3",
      "Development Status :: 3 - Alpha",
      "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
      "Operating System :: OS Independent",
      "Environment :: Console",
      "Topic :: Multimedia :: Graphics :: Graphics Conversion",
      "Topic :: Scientific/Engineering :: Astronomy"
  ],
  project_urls={
      'Source': 'https://github.com/sanelson/rastro',
      'Tracker': 'https://github.com/sanelson/rastro/issues',
  },
  python_requires='>=3.8',
)
