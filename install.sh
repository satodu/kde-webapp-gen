#!/bin/bash
# Installer script for KDE Webapp Manager

set -e

BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
ICON="preferences-desktop-default-applications"

echo "Installing KDE Webapp Manager..."

# Create local bin and applications directories if they don't exist
mkdir -p "$BIN_DIR"
mkdir -p "$APP_DIR"
mkdir -p "$HOME/.local/share/icons"

# Copy main.py to bin
cp main.py "$BIN_DIR/kde-webapp-manager"
chmod +x "$BIN_DIR/kde-webapp-manager"

# Setup custom logo if present
ICON="preferences-desktop-default-applications"
if [ -f "images/kde-webapp-gen-icon-logo.png" ]; then
    cp "images/kde-webapp-gen-icon-logo.png" "$HOME/.local/share/icons/kde-webapp-manager.png"
    ICON="$HOME/.local/share/icons/kde-webapp-manager.png"
fi

# Create Desktop Shortcut
cat <<EOF > "$APP_DIR/kde-webapp-manager.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Webapp Manager
Comment=Create and edit webapps for KDE Plasma
Exec=$BIN_DIR/kde-webapp-manager
Icon=$ICON
Terminal=false
Categories=Utility;Settings;Qt;
StartupNotify=true
EOF

chmod +x "$APP_DIR/kde-webapp-manager.desktop"

# Update desktop shortcuts database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APP_DIR"
fi

echo "Installation completed successfully!"
echo "You can open the 'Webapp Manager' directly from the KDE Application Menu (K-Menu)."
echo "Or run it in the terminal using the command: kde-webapp-manager"
