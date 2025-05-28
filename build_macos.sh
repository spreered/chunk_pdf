#!/bin/bash

# Script to build the macOS .app and .dmg for PDFChunker using hdiutil

# --- Configuration ---
APP_NAME="PDFChunker"
MAIN_SCRIPT="pdf_chunker_gui.py"
ICON_FILE="assets/icon.icns" # Relative path from project root
PROJECT_ROOT_DIR=$(pwd) # Assumes script is run from project root

# Output directories
DIST_DIR="${PROJECT_ROOT_DIR}/dist"
BUILD_DIR="${PROJECT_ROOT_DIR}/build" # Used for PyInstaller build and temp DMG source
DMG_OUTPUT_DIR="${DIST_DIR}" # Where the final DMG will be placed
DMG_FILENAME="${APP_NAME}.dmg"

# Temporary staging directory for DMG contents
DMG_TEMP_SOURCE_DIR="${BUILD_DIR}/dmg_source"

# --- Helper Functions ---
cleanup() {
    echo "Cleaning up previous build directories..."
    rm -rf "${DIST_DIR}"
    rm -rf "${BUILD_DIR}" # This will also remove DMG_TEMP_SOURCE_DIR if it's inside
    # Remove any existing .spec file for a clean build
    rm -f "${APP_NAME}.spec"
    echo "Cleanup complete."
}

check_command_exists() {
    command -v "$1" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Command '$1' not found."
        echo "Please install it first."
        exit 1
    fi
}

# --- Main Script ---

echo "Starting macOS build process for ${APP_NAME} (using hdiutil)..."
echo "Project root: ${PROJECT_ROOT_DIR}"

# 0. Check for required tools
check_command_exists "pyinstaller"
check_command_exists "hdiutil" # Now checking for hdiutil

# 1. Clean up previous builds
cleanup
mkdir -p "${BUILD_DIR}" # Ensure build directory exists for temp DMG source

# 2. Run PyInstaller to create the .app bundle
echo "Running PyInstaller to create ${APP_NAME}.app..."
pyinstaller --name "${APP_NAME}" \
            --onefile \
            --windowed \
            --icon="${PROJECT_ROOT_DIR}/${ICON_FILE}" \
            "${PROJECT_ROOT_DIR}/${MAIN_SCRIPT}"

# Check if PyInstaller was successful
APP_BUNDLE_PATH="${DIST_DIR}/${APP_NAME}.app"
if [ ! -d "${APP_BUNDLE_PATH}" ]; then
    echo "Error: PyInstaller failed to create ${APP_NAME}.app."
    echo "Please check the PyInstaller output above for errors."
    exit 1
fi
echo "${APP_NAME}.app created successfully at ${APP_BUNDLE_PATH}"

# 3. Create the .dmg file using hdiutil
echo "Preparing files for DMG creation..."

# Create and prepare the temporary source directory for the DMG
mkdir -p "${DMG_TEMP_SOURCE_DIR}"

# Copy the .app bundle to the temp source directory
echo "Copying ${APP_BUNDLE_PATH} to ${DMG_TEMP_SOURCE_DIR}/"
cp -R "${APP_BUNDLE_PATH}" "${DMG_TEMP_SOURCE_DIR}/"

# For hdiutil to set a volume icon, it typically looks for .VolumeIcon.icns
# We'll use the app icon as the volume icon.
if [ -f "${PROJECT_ROOT_DIR}/${ICON_FILE}" ]; then
    echo "Copying volume icon..."
    cp "${PROJECT_ROOT_DIR}/${ICON_FILE}" "${DMG_TEMP_SOURCE_DIR}/.VolumeIcon.icns"
else
    echo "Warning: Application icon file not found at ${PROJECT_ROOT_DIR}/${ICON_FILE}. DMG will not have a custom volume icon."
fi

echo "Creating ${DMG_FILENAME} using hdiutil..."

# Ensure output directory for DMG exists
mkdir -p "${DMG_OUTPUT_DIR}"
DMG_FULL_PATH="${DMG_OUTPUT_DIR}/${DMG_FILENAME}"

# Remove existing DMG if any
if [ -f "${DMG_FULL_PATH}" ]; then
    echo "Removing existing DMG: ${DMG_FULL_PATH}"
    rm "${DMG_FULL_PATH}"
fi

hdiutil create \
  -srcfolder "${DMG_TEMP_SOURCE_DIR}" \
  -volname "${APP_NAME}" \
  -fs HFS+ \
  -fsargs "-c c=64,a=16,e=16" \
  -format UDZO \
  -imagekey zlib-level=9 \
  -ov \
  "${DMG_FULL_PATH}"

# Check if DMG creation was successful
if [ -f "${DMG_FULL_PATH}" ]; then
    echo "DMG created successfully: ${DMG_FULL_PATH}"
else
    echo "Error: Failed to create DMG with hdiutil."
    echo "Please check the hdiutil output above for errors."
    # Clean up temporary DMG source directory on failure here as well
    echo "Cleaning up temporary DMG source directory: ${DMG_TEMP_SOURCE_DIR}"
    rm -rf "${DMG_TEMP_SOURCE_DIR}"
    exit 1
fi

# Clean up temporary DMG source directory
echo "Cleaning up temporary DMG source directory: ${DMG_TEMP_SOURCE_DIR}"
rm -rf "${DMG_TEMP_SOURCE_DIR}"

echo "Build process complete!"
exit 0
