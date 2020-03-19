# rastro
Python tool for Raw image conversion and analysis using rawpy and libraw

# Installing Dependencies

## py3exiv2

Library currently has a bug which prevents it from finding libboost_python3 on Linux for linking.  I've submitted a fix to the maintainers but until it is merged, you can install from my github (https://github.com/sanelson/py3exiv2/tree/fix_libboost_python_build)

# Code Style

I use the YAPF tool to easily reformat the code to a style I like.  Here's an example usage.

```
yapf --style='{based_on_style: facebook, indent_width: 2}' <filename.py>
```
