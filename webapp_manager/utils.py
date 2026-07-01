import os
import shutil
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath
from webapp_manager.constants import ICONS_DIR

def get_rounded_pixmap(pixmap: QPixmap, radius: int = 8) -> QPixmap:
    """Crops a QPixmap to have rounded corners for a premium appearance."""
    if pixmap.isNull():
        return pixmap
    
    # Scale to standard size (e.g. 40x40)
    scaled = pixmap.scaled(
        40, 40,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation
    )
    
    target = QPixmap(40, 40)
    target.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(target)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    
    path = QPainterPath()
    path.addRoundedRect(0, 0, 40, 40, float(radius), float(radius))
    
    painter.setClipPath(path)
    # Draw centered
    x = (40 - scaled.width()) // 2
    y = (40 - scaled.height()) // 2
    painter.drawPixmap(x, y, scaled)
    painter.end()
    return target

def get_app_logo_pixmap(size: Optional[int] = None) -> QPixmap:
    """Loads the app logo, checking installed paths, dev paths, and system icon theme fallback."""
    pixmap = QPixmap()
    
    # 1. Try direct installed paths (user space and system wide)
    installed_paths = [
        os.path.expanduser("~/.local/share/icons/kde-webapp-manager.png"),
        "/usr/share/pixmaps/kde-webapp-manager.png",
        "/usr/share/icons/hicolor/512x512/apps/kde-webapp-manager.png",
        "/usr/share/icons/hicolor/256x256/apps/kde-webapp-manager.png",
        "/usr/share/icons/hicolor/128x128/apps/kde-webapp-manager.png",
    ]
    for path in installed_paths:
        if os.path.exists(path):
            pixmap.load(path)
            if not pixmap.isNull():
                break
        
    # 2. Try dev local path relative to current script (dev environment)
    if pixmap.isNull():
        local_logo = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "images", "kde-webapp-gen-icon-logo.png"
        )
        if os.path.exists(local_logo):
            pixmap.load(local_logo)
            
    # 3. Try icon theme
    if pixmap.isNull():
        icon = QIcon.fromTheme("kde-webapp-manager")
        if not icon.isNull():
            pixmap = icon.pixmap(64, 64)
            
    # 4. Fallback to system default app icon
    if pixmap.isNull():
        icon = QIcon.fromTheme("preferences-desktop-default-applications")
        if not icon.isNull():
            pixmap = icon.pixmap(64, 64)
            
    if size and not pixmap.isNull():
        return pixmap.scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
    return pixmap

def migrate_profile_if_needed(user_data_path_raw: Optional[str]) -> None:
    """Detects if session is stuck in a literal '/home/user/$HOME' directory
    due to unexpanded manual launcher variables and migrates it to the correct path.
    """
    if not user_data_path_raw or "$HOME" not in user_data_path_raw:
        return
        
    target_path = os.path.expandvars(os.path.expanduser(user_data_path_raw))
    target_path = os.path.normpath(target_path)
    
    home_dir = os.path.expanduser("~")
    # Literal $HOME folder in home directory
    literal_path = os.path.join(home_dir, user_data_path_raw.replace("$HOME", "$HOME"))
    literal_path = os.path.normpath(literal_path)
    
    if os.path.exists(literal_path) and literal_path != target_path:
        if not os.path.exists(target_path):
            try:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.move(literal_path, target_path)
                print(f"Successfully migrated session profile from {literal_path} to {target_path}")
            except Exception as e:
                print(f"Failed to migrate session profile: {e}")
