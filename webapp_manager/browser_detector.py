import os
import shutil
from typing import List, Tuple

class BrowserDetector:
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
