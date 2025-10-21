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

# Define exclude patterns
EXCLUDE_PATTERNS=(
  ".*"           # Hidden files
  "gallery/*"      # Gallery folder
  "*.md"         # Markdown files (will add back specific ones)
  "orbs_*.zip"        # Zip files
  "package_mod.sh"  # This script
)

# Define files to include back
INCLUDE_FILES=(
  "README.md"
  "LICENSE"
)

# Remove old zip if it exists
rm -f "$ZIP_FILE"

# Go to parent directory and create zip with enclosing folder
cd ..

# Check if 7z is available
if command -v 7z &> /dev/null; then
  echo "Using 7z..."

  # Build exclude arguments for 7z
  EXCLUDE_ARGS=()
  for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_ARGS+=("-xr!${pattern}")
  done

  # Create zip with 7z, excluding unwanted files
  7z a -tzip "${CURRENT_DIR}/${ZIP_FILE}" "${EXCLUDE_ARGS[@]}" "${CURRENT_DIR}/*"

  # Add back specific files
  for file in "${INCLUDE_FILES[@]}"; do
    7z a -tzip "${CURRENT_DIR}/${ZIP_FILE}" "${CURRENT_DIR}/${file}" 2>/dev/null || true
  done

else
  echo "Using zip..."

  # Build exclude arguments for zip
  EXCLUDE_ARGS=()
  for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_ARGS+=("-x" "${CURRENT_DIR}/${pattern}")
    # Also exclude in subdirectories for hidden files
    if [[ "$pattern" == ".*" ]]; then
      EXCLUDE_ARGS+=("-x" "${CURRENT_DIR}/**/${pattern}")
    fi
  done

  # Create zip with regular zip command
  zip -r "${CURRENT_DIR}/${ZIP_FILE}" "${CURRENT_DIR}" "${EXCLUDE_ARGS[@]}"

  # Add back specific files
  for file in "${INCLUDE_FILES[@]}"; do
    zip "${CURRENT_DIR}/${ZIP_FILE}" "${CURRENT_DIR}/${file}" 2>/dev/null || true
  done
fi

# Go back to original directory
cd "${CURRENT_DIR}"

# Show result
FILE_SIZE=$(du -h "$ZIP_FILE" | cut -f1)
echo ""
echo "Package created: $ZIP_FILE"
echo "Size: $FILE_SIZE"
