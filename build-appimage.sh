#!/bin/bash
# Build script to compile KDE Webapp Manager into a standalone AppImage

set -e

echo "Starting KDE Webapp Manager AppImage build..."

# 1. Create virtual environment to run PyInstaller
echo "Creating temporary virtual environment for build..."
python3 -m venv --system-site-packages build_env
source build_env/bin/activate

echo "Installing PyInstaller in virtual environment..."
pip install pyinstaller

echo "Compiling application using PyInstaller..."
# Compile PyQt6 app into a directory
pyinstaller --noconfirm --onedir --windowed --add-data "images:images" --name "kde-webapp-manager" main.py

# Deactivate virtual environment
deactivate

echo "Structuring AppDir..."
# Recreate AppDir folder
rm -rf AppDir
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

# Copy the compiled build assets
cp -r dist/kde-webapp-manager/* AppDir/usr/bin/

# Copy launcher and icon to AppDir root (required for AppImage specification)
cp images/kde-webapp-gen-icon-logo.png AppDir/kde-webapp-manager.png
cp images/kde-webapp-gen-icon-logo.png AppDir/usr/share/icons/hicolor/256x256/apps/kde-webapp-manager.png

# Create desktop entry in AppDir root
cat <<EOF > AppDir/kde-webapp-manager.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=Webapp Manager
Comment=Create and edit webapps for KDE Plasma
Exec=usr/bin/kde-webapp-manager
Icon=kde-webapp-manager
Terminal=false
Categories=Utility;Settings;Qt;
StartupNotify=true
EOF

# Create AppRun launcher script
cat <<EOF > AppDir/AppRun
#!/bin/sh
SELF=\$(readlink -f "\$0")
HERE=\$(dirname "\$SELF")
exec "\$HERE/usr/bin/kde-webapp-manager" "\$@"
EOF
chmod +x AppDir/AppRun

# 2. Get appimagetool
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget -O appimagetool-x86_64.AppImage https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# 3. Build the AppImage
echo "Bundling AppDir into AppImage..."
export ARCH=x86_64
./appimagetool-x86_64.AppImage --appimage-extract-and-run AppDir kde-webapp-manager-x86_64.AppImage

# 4. Clean up temporary files
echo "Cleaning up temporary directories..."
rm -rf build/ dist/ AppDir/ build_env/

echo "--------------------------------------------------------"
echo "Build completed successfully!"
echo "Generated executable: kde-webapp-manager-x86_64.AppImage"
echo "--------------------------------------------------------"
