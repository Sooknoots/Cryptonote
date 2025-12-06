#!/bin/bash

echo "========================================"
echo "   Cryptonote Linux Build Script"
echo "========================================"
echo

echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "Creating build directory structure..."
rm -rf build dist
mkdir -p build dist

echo
echo "Building executable..."
echo "(This may take several minutes...)"
echo

pyinstaller cryptonote_linux.spec

if [ $? -ne 0 ]; then
    echo "ERROR: PyInstaller build failed"
    exit 1
fi

echo
echo "Build completed successfully!"
echo "Executable created: dist/Cryptonote"
echo

# Create release package
echo "Creating release package..."
VERSION="v1.0.1"
RELEASE_DIR="Releases/Cryptonote_Linux_${VERSION}"
mkdir -p "$RELEASE_DIR"

cp dist/Cryptonote "$RELEASE_DIR/"
cp README.md "$RELEASE_DIR/"
cp RELEASE_NOTES.md "$RELEASE_DIR/"
cp Commercial_Distribution_Readme.md "$RELEASE_DIR/"

# Create zip archive
cd Releases
zip -r "Cryptonote_Linux_${VERSION}.zip" "Cryptonote_Linux_${VERSION}/"
cd ..

echo "Release package created: Releases/Cryptonote_Linux_${VERSION}.zip"
echo
echo "========================================"
echo "   Build Complete!"
echo "========================================"