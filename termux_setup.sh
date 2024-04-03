#!/bin/sh
# Install the dependencies on Termux, which could be difficult, especially hunspell.

# Update packages
pkg update -y

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

# Install libyaml
pkg install -y libyaml

# Install other dependencies
pip install -r server/requirements.txt

# Install opencc-0.2, which works well despite the scary version number.
pkg install -y libopencc
pip install opencc

# Set up exteral storage
# termux-setup-storage
# This is non-blocking, so we have to let the user do it manually.

# Configure default source directory
mkdir -p /sdcard/Documents/Dictionaries
mkdir -p ~/.silverdict
echo -e "history_size: 100\nnum_suggestions: 10\nsources:\n- /sdcard/Documents/Dictionaries" > ~/.silverdict/misc.yaml

# Create Termux:Widget shortcuts
mkdir -p ~/.shortcuts
PROJECT_DIR=$(pwd)
echo -e "#!/bin/sh\ntermux-wake-lock\npython $PROJECT_DIR/server/server.py 0.0.0.0 &> ~/.silverdict/server.log &" > ~/.shortcuts/SilverDict-Start.sh
echo -e "#!/bin/sh\nkillall -SIGTERM python\ntermux-wake-unlock\nexit" > ~/.shortcuts/SilverDict-Stop.sh
chmod +x ~/.shortcuts/*
# Release the lock upon logout
echo "#!/bin/sh\ntermux-wake-unlock" >> ~/.bash_logout