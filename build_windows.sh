#!/bin/bash

# Build script for Windows EXE
# This script assumes you have python and pip installed and available in PATH.
# If using Git Bash or WSL, ensure python resolves to your Windows python installation
# or you are in an environment that can cross-compile (not recommended/easy for PySide6).

echo "Installing PyInstaller..."
pip install pyinstaller

echo "Cleaning up previous builds..."
rm -rf build dist

echo "Building EXE..."
# --noconsole: Don't show terminal window
# --onefile: Bundle everything into a single .exe
# --name: Name of the output executable
# --add-data: Add assets if we had them (e.g. "assets;assets") but currently we use code-generated icons mostly.
#             However, src/utils/paths.py expects assets folder. Let's include it if it exists.

ADD_DATA_FLAG=""
if [ -d "assets" ]; then
  # On Windows separator is ; for add-data
  ADD_DATA_FLAG="--add-data 'assets;assets'"
fi

pyinstaller --noconsole --onefile --name "WireGuardGUI" $ADD_DATA_FLAG src/main.py

echo "Build complete."
echo "Executable can be found in dist/WireGuardGUI.exe"
