#!/bin/bash
# Package the Orbs mod into a distributable zip file

set -e

# Get mod name and version from info.json
MOD_NAME=$(grep '"name"' info.json | sed 's/.*"name": "\(.*\)".*/\1/')
MOD_VERSION=$(grep '"version"' info.json | sed 's/.*"version": "\(.*\)".*/\1/')

MOD_FOLDER="${MOD_NAME}_${MOD_VERSION}"
ZIP_FILE="${MOD_FOLDER}.zip"

echo "Packaging ${MOD_NAME} v${MOD_VERSION}..."

# Remove old zip if it exists
rm -f "$ZIP_FILE"

# Check if 7z is available
if command -v 7z &> /dev/null; then
  echo "Using 7z..."

  # Create zip with 7z, excluding unwanted files
  7z a -tzip "$ZIP_FILE" \
    -xr'!.*' \
    -xr'!gallery' \
    -xr'!*.md' \
    -xr'!package_mod.py' \
    -xr'!package_mod.sh' \
    ./*

  # Add back README.md and LICENSE
  7z a -tzip "$ZIP_FILE" README.md LICENSE

else
  echo "Using zip..."

  # Create zip with regular zip command
  zip -r "$ZIP_FILE" . \
    -x '.*' \
    -x '**/.*' \
    -x 'gallery/*' \
    -x '*.md' \
    -x 'package_mod.py' \
    -x 'package_mod.sh'

  # Add back README.md and LICENSE
  zip "$ZIP_FILE" README.md LICENSE
fi

# Show result
FILE_SIZE=$(du -h "$ZIP_FILE" | cut -f1)
echo ""
echo "Package created: $ZIP_FILE"
echo "Size: $FILE_SIZE"
