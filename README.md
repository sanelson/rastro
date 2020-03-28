# Rastro

Python tool for Raw image conversion and analysis using rawpy and libraw

# Purpose

I needed a tool which could take RAW images from my Canon EOS cameras and convert them to other formats (TIFF, FITS, etc.) with as little processing as possible to be used for stellar photometry measurements.  One key for photometry is to try to avoid any pre-processing of the raw image data.  There are lots of really great tools out there which can do this, but the process can be a little involved and include multiple confusing and error prone steps.  The fantastic rawtran wrapper for dcraw did about 99% of what I needed, but I was worried about it being based on the now unmaintained dcraw code.  I found rawpy and the libraw library which it uses and I decided to just write my own tool.

For now the program's main purpose is to process low level raw data and extract it as unchanged as possible.  I'm also working on some analysis functions like a histogram and image stats (see the great rawshack tool for an example).

# Installing

## Ubuntu Linux

Get the base system packages needed.

```
sudo apt install libraw19 libraw-bin libraw-dev python3-opencv python3-pyqt5 exiv2 libexiv2-dev libboost-python-dev 
```

The remaining python module dependencies should be handled automatically by the installer.  I like to install all of my python modules in a local user location.

To install locally

```
python3 setup.py install --user
```


If you'd like to run the tool in development mode where changes you make in the source files are instantly reflected in the installed tool, use:

```
python3 setup.py develop --user
```

Eventually, once it has a reasonable feature set, I'll upload this tool to PyPi and you can simply pip install it.

## Mac OSX

TBD

## Windows

TBD

# Code Style

I use the YAPF tool to easily reformat the code to a style I like.  Here's an example usage.

```
yapf --style='{based_on_style: facebook, indent_width: 2}' <filename.py>
```


