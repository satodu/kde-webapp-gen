import os
import re
from typing import Tuple, Optional
from webapp_manager.constants import APPLICATIONS_DIR, DEFAULT_USER_DATA_BASE

class WebappMemento:
    def __init__(
        self,
        name: str,
        url: str,
        browser: str,
        width: int,
        height: int,
        user_data_dir: str,
        wm_class: str,
        icon: str
    ) -> None:
        self.name = name
        self.url = url
        self.browser = browser
        self.width = width
        self.height = height
        self.user_data_dir = user_data_dir
        self.wm_class = wm_class
        self.icon = icon

class Webapp:
    def __init__(
        self,
        name: str,
        url: str,
        browser: str,
        width: int = 1024,
        height: int = 768,
        user_data_dir: str = "",
        wm_class: str = "",
        icon: str = "",
        filepath: str = ""
    ) -> None:
        self.name = name.strip()
        self.url = url.strip()
        self.browser = browser.strip()
        self.width = width
        self.height = height
        
        # Heuristics for default values if not supplied
        self.user_data_dir = user_data_dir.strip() if user_data_dir else self.generate_default_user_data_dir()
        self.wm_class = wm_class.strip() if wm_class else self.get_slug()
        self.filepath = filepath.strip() if filepath else self.generate_default_filepath()
        self.icon = icon.strip() if icon else "applications-internet"
        
        # Baseline memento to track unsaved edits/drafts
        self._saved_memento: Optional[WebappMemento] = None

    def get_slug(self) -> str:
        """Generates a clean slug from the app name (e.g. 'WhatsApp' -> 'whatsapp')."""
        return re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())

    def generate_default_user_data_dir(self) -> str:
        """Calculates default user data directory path based on flatpak or native browser runtime."""
        slug = self.get_slug()
        if not slug:
            return ""
            
        if "flatpak run" in self.browser:
            parts = self.browser.split()
            if len(parts) >= 3:
                app_id = parts[2]
            else:
                app_id = "com.unknown.Browser"
            return os.path.expanduser(f"~/.var/app/{app_id}/config/webapps/{slug}")
        else:
            return os.path.join(DEFAULT_USER_DATA_BASE, slug)

    def generate_default_filepath(self) -> str:
        """Calculates default .desktop file path."""
        slug = self.get_slug()
        return os.path.join(APPLICATIONS_DIR, f"webapp_{slug}.desktop")

    def get_browser_prefixes(self) -> Tuple[str, str]:
        """Detects the prefix of the executable and sub-prefix for KWin/WM_CLASS."""
        main_prefix = "chrome"
        sub_prefix = "chrome"
        cmd_lower = self.browser.lower()
        
        if "com.brave.browser" in cmd_lower or "brave" in cmd_lower:
            main_prefix = "com.brave.Browser" if "com.brave" in cmd_lower else "brave-browser"
            sub_prefix = "brave"
        elif "edge" in cmd_lower:
            main_prefix = "com.microsoft.Edge" if "com.microsoft" in cmd_lower else "microsoft-edge"
            sub_prefix = "msedge"
        elif "chromium" in cmd_lower:
            main_prefix = "org.chromium.Chromium" if "org.chromium" in cmd_lower else "chromium-browser"
            sub_prefix = "chromium"
        elif "vivaldi" in cmd_lower:
            main_prefix = "com.vivaldi.Vivaldi" if "com.vivaldi" in cmd_lower else "vivaldi-stable"
            sub_prefix = "vivaldi"
            
        return main_prefix, sub_prefix

    @property
    def exec_line(self) -> str:
        """Constructs the complete Exec string for the desktop entry."""
        exec_str = f"{self.browser} --window-size={self.width},{self.height}"
        if self.wm_class:
            exec_str += f" --class={self.wm_class}"
        exec_str += f" --app={self.url}"
        if self.user_data_dir:
            resolved_ud = os.path.expandvars(os.path.expanduser(self.user_data_dir))
            exec_str += f" --user-data-dir={resolved_ud}"
        return exec_str

    def create_memento(self) -> WebappMemento:
        """Creates a snapshot of the current state of this webapp."""
        return WebappMemento(
            name=self.name,
            url=self.url,
            browser=self.browser,
            width=self.width,
            height=self.height,
            user_data_dir=self.user_data_dir,
            wm_class=self.wm_class,
            icon=self.icon
        )

    def restore(self, memento: Optional[WebappMemento]) -> None:
        """Restores this webapp's attributes from the given memento."""
        if not memento:
            return
        self.name = memento.name
        self.url = memento.url
        self.browser = memento.browser
        self.width = memento.width
        self.height = memento.height
        self.user_data_dir = memento.user_data_dir
        self.wm_class = memento.wm_class
        self.icon = memento.icon

    @property
    def is_dirty(self) -> bool:
        """Checks if the current in-memory attributes differ from the saved baseline."""
        if not self._saved_memento:
            return True
        m = self._saved_memento
        return (self.name != m.name or
                self.url != m.url or
                self.browser != m.browser or
                self.width != m.width or
                self.height != m.height or
                self.user_data_dir != m.user_data_dir or
                self.wm_class != m.wm_class or
                self.icon != m.icon)
