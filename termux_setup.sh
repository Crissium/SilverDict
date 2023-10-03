#!/bin/sh
# Install the dependencies on Termux, which could be difficult, especially hunspell.

# Update packages
pkg update

# First, make sure pip is installed.
pkg install -y python-pip

# Install hunspell (the original C++ package).
pkg install -y hunspell

# Fix the file paths of headers and libraries.
ln -s $PREFIX/include/hunspell/* $PREFIX/include/
ln -s $PREFIX/lib/libhunspell-*.so $PREFIX/lib/libhunspell.so

# Now install the python package with pip
pip install hunspell

# Install lxml's dependencies
pkg install -y libxml2 libxslt

# Install other dependencies
pip install -r server/requirements.txt
pip install -r http_server/requirements.txt

# TODO: automatically install the latest opencc
pip install opencc