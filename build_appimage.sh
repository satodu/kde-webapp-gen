#!/bin/bash
# AppImage building script for KDE Webapp Manager v1.0.1
# Requires: pyinstaller (installable via paru/pacman)

set -e

echo "=== Starting AppImage Build Process ==="

# 1. Clean up previous build directories
echo "Cleaning up old build files..."
rm -rf build dist AppDir *.AppImage appimagetool

# 2. Check for PyInstaller dependency
if ! command -v pyinstaller &> /dev/null; then
    echo "ERROR: pyinstaller is not installed."
    echo "Please install it with: paru -S pyinstaller"
    exit 1
fi

# 3. Build standalone directory using PyInstaller
echo "Compiling Python source code with PyInstaller..."
pyinstaller --name kde-webapp-manager \
            --windowed \
            --onedir \
            --add-data "webapp_manager/*.png:webapp_manager/" \
            main.py

# 4. Create AppDir directory structure
echo "Setting up AppDir structure..."
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/pixmaps

# Copy compiled PyInstaller assets
cp -r dist/kde-webapp-manager/* AppDir/usr/bin/

# Copy logo icon
cp images/kde-webapp-gen-icon-logo.png AppDir/usr/share/pixmaps/kde-webapp-manager.png

# Symlink main icon to root of AppDir (required by AppImage standard)
ln -s usr/share/pixmaps/kde-webapp-manager.png AppDir/kde-webapp-manager.png

# Create metadata desktop entry inside share/applications/
cat <<EOF > AppDir/usr/share/applications/kde-webapp-manager.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=Webapp Manager
Comment=Create and edit webapps for KDE Plasma
Exec=kde-webapp-manager
Icon=kde-webapp-manager
Terminal=false
Categories=Utility;Settings;Qt;
StartupNotify=true
EOF

# Copy desktop launcher to root of AppDir (required by AppImage standard)
cp AppDir/usr/share/applications/kde-webapp-manager.desktop AppDir/kde-webapp-manager.desktop

# Create the standard AppRun launch script
cat <<'EOF' > AppDir/AppRun
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/kde-webapp-manager" "$@"
EOF
chmod +x AppDir/AppRun

# 5. Pack AppDir into AppImage using appimagetool
echo "Packaging AppDir..."
if ! command -v appimagetool &> /dev/null; then
    echo "appimagetool not found on system path, downloading portable release..."
    curl -Lo appimagetool https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool
    
    # Run downloaded appimagetool
    ./appimagetool AppDir
    rm -f appimagetool
else
    appimagetool AppDir
fi

# Clean temporary folders
rm -rf AppDir build dist

echo "=== AppImage Build Completed Successfully! ==="
