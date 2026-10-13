import os
import json
import shutil
from typing import List, Tuple

DEFAULT_PROFILE = "Default"

# Browser user data directories relative to ~/.config (or ~/.var/app/<id>/config for Flatpaks).
_CONFIG_SUBDIRS: List[Tuple[str, str]] = [
    ("brave", "BraveSoftware/Brave-Browser"),
    ("edge", "microsoft-edge"),
    ("vivaldi", "vivaldi"),
    ("chromium", "chromium"),
    ("chrome", "google-chrome"),
]

class BrowserDetector:
    @staticmethod
    def get_browser_config_dir(browser_cmd: str) -> str:
        cmd_lower = browser_cmd.lower()
        subdir = next((sub for key, sub in _CONFIG_SUBDIRS if key in cmd_lower), "google-chrome")
        if "flatpak run" in cmd_lower:
            parts = browser_cmd.split()
            if len(parts) >= 3:
                return os.path.expanduser(f"~/.var/app/{parts[2]}/config/{subdir}")
        return os.path.expanduser(f"~/.config/{subdir}")

    @staticmethod
    def detect_last_used_profile(browser_cmd: str) -> str:
        """Returns the profile folder the browser opens by default (e.g. 'Default' or 'Profile 1')."""
        local_state = os.path.join(BrowserDetector.get_browser_config_dir(browser_cmd), "Local State")
        try:
            with open(local_state, encoding="utf-8") as f:
                last_used = json.load(f).get("profile", {}).get("last_used")
        except (OSError, ValueError, AttributeError):
            return DEFAULT_PROFILE
        return last_used if isinstance(last_used, str) and last_used.strip() else DEFAULT_PROFILE

    @staticmethod
    def detect_browsers() -> List[Tuple[str, str]]:
        """Detects installed Chromium-based browsers that support the --app flag."""
        candidates: List[Tuple[str, str]] = [
            ("Google Chrome", "google-chrome-stable"),
            ("Google Chrome", "google-chrome"),
            ("Brave Browser", "brave-browser"),
            ("Brave Browser", "brave"),
            ("Chromium", "chromium-browser"),
            ("Chromium", "chromium"),
            ("Microsoft Edge", "microsoft-edge-stable"),
            ("Microsoft Edge", "microsoft-edge"),
            ("Vivaldi", "vivaldi-stable"),
            ("Vivaldi", "vivaldi"),
        ]
        browsers: List[Tuple[str, str]] = []
        seen = set()
        for name, cmd in candidates:
            path = shutil.which(cmd)
            if path:
                real_cmd = os.path.basename(path)
                if real_cmd not in seen:
                    seen.add(real_cmd)
                    browsers.append((name, cmd))
                    
        # Flatpak browsers detection
        if shutil.which("flatpak"):
            flatpaks: List[Tuple[str, str]] = [
                ("Google Chrome (Flatpak)", "com.google.Chrome"),
                ("Brave Browser (Flatpak)", "com.brave.Browser"),
                ("Chromium (Flatpak)", "org.chromium.Chromium"),
                ("Microsoft Edge (Flatpak)", "com.microsoft.Edge"),
                ("Vivaldi (Flatpak)", "com.vivaldi.Vivaldi"),
            ]
            for name, app_id in flatpaks:
                system_path = f"/var/lib/flatpak/app/{app_id}"
                user_path = os.path.expanduser(f"~/.local/share/flatpak/app/{app_id}")
                if os.path.exists(system_path) or os.path.exists(user_path):
                    # Save the full run command as the command data
                    cmd = f"flatpak run {app_id}"
                    if cmd not in seen:
                        seen.add(cmd)
                        browsers.append((name, cmd))
                        
        return browsers
