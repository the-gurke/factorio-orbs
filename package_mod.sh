#!/bin/bash
# Package the Orbs mod into a distributable zip file

set -e

# Get mod name and version from info.json
MOD_NAME=$(grep '"name"' info.json | sed 's/.*"name": "\(.*\)".*/\1/')
MOD_VERSION=$(grep '"version"' info.json | sed 's/.*"version": "\(.*\)".*/\1/')

MOD_FOLDER="${MOD_NAME}_${MOD_VERSION}"
ZIP_FILE="${MOD_FOLDER}.zip"

echo "Packaging ${MOD_NAME} v${MOD_VERSION}..."

# Get current directory name
CURRENT_DIR=$(basename "$PWD")

# Remove old zip if it exists
rm -f "$ZIP_FILE"

# Go to parent directory and create zip with enclosing folder
cd ..

# Check if 7z is available
if command -v 7z &> /dev/null; then
  echo "Using 7z..."

  # Create zip with 7z, excluding unwanted files
  7z a -tzip "${CURRENT_DIR}/${ZIP_FILE}" \
    -xr'!.*' \
    -xr'!gallery' \
    -xr'!*.md' \
    -xr'!package_mod.py' \
    -xr'!package_mod.sh' \
    "${CURRENT_DIR}/*"

  # Add back README.md and LICENSE
  7z a -tzip "${CURRENT_DIR}/${ZIP_FILE}" "${CURRENT_DIR}/README.md" "${CURRENT_DIR}/LICENSE"

else
  echo "Using zip..."

  # Create zip with regular zip command
  zip -r "${CURRENT_DIR}/${ZIP_FILE}" "${CURRENT_DIR}" \
    -x "${CURRENT_DIR}/.*" \
    -x "${CURRENT_DIR}/**/.*" \
    -x "${CURRENT_DIR}/gallery/*" \
    -x "${CURRENT_DIR}/*.md" \
    -x "${CURRENT_DIR}/package_mod.py" \
    -x "${CURRENT_DIR}/package_mod.sh"

  # Add back README.md and LICENSE
  zip "${CURRENT_DIR}/${ZIP_FILE}" "${CURRENT_DIR}/README.md" "${CURRENT_DIR}/LICENSE"
fi

# Go back to original directory
cd "${CURRENT_DIR}"

# Show result
FILE_SIZE=$(du -h "$ZIP_FILE" | cut -f1)
echo ""
echo "Package created: $ZIP_FILE"
echo "Size: $FILE_SIZE"
