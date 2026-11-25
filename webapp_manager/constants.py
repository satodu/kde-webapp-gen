import os

APP_NAME: str = "KDE Webapp Manager"
APP_VERSION: str = "1.3.4"
APP_AUTHOR: str = "satodu"
APP_AUTHOR_URL: str = "https://github.com/satodu"
APP_REPO_URL: str = "https://github.com/satodu/kde-webapp-gen"

APPLICATIONS_DIR: str = os.path.expanduser("~/.local/share/applications/")
ICONS_DIR: str = os.path.expanduser("~/.local/share/icons/")
DEFAULT_USER_DATA_BASE: str = os.path.expanduser("~/.config/webapps/")

# Chromium flag that fixes a black screen on DRM video players (e.g. Netflix) on some GPU/Wayland setups.
VIDEO_FIX_FLAG = "--disable-gpu-compositing"
