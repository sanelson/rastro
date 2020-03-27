# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import re
from setuptools import setup, find_packages

version = re.search(
  '^__version__\s*=\s*"(.*)"',
  open('rastro/__init__.py').read(),
  re.M
).group(1)

with open("README.md", "rb") as f:
  long_description = f.read().decode("utf-8")

setup(
  name = "rastro",
  packages = find_packages(),
  entry_points = {
      "console_scripts": ['rastro = rastro.cli:main']
    },
  version = version,
  description = "Python tools for astronomical Raw image conversion and analysis using rawpy and libraw",
  long_description = long_description,
  long_description_content_type="text/markdown",
  author = "Sam Nelson",
  author_email = "sanelson@siliconfuture.net",
  url = "https://github.com/sanelson/rastro",
  # TODO: Add scikit-image and/or opencv to this list
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
      'Source Code': 'https://github.com/sanelson/rastro',
      'Bug Tracker': 'https://github.com/sanelson/rastro/issues',
  },
  python_requires='>=3.7',
  zip_safe=False,
)
