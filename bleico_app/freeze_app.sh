#!/usr/local/bin/bash
# Clear previous installation

echo "Creating app bundle..."
echo "$(pyinstaller -w -y -n bleico -i bleico.icns --windowed bleico_macos.spec)"
echo "Done!"
