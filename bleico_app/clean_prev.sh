#!/usr/local/bin/bash
# Clear previous installation

echo "Cleaining build and dist"
echo "$(rm -rf build/)"
echo "$(rm -rf dist/bleico)"
echo "$(rm -rf dist/bleico.app/)"
echo "$(rm -rf dist/bleico_img.dmg*)"
echo "$(rm -rf dist/SHA256)"
echo "Done!"
