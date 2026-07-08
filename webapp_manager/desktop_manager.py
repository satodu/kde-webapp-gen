import os
import glob
import re
import subprocess
import configparser
from typing import List, Dict, Tuple, Any
from webapp_manager.constants import APPLICATIONS_DIR
from webapp_manager.models import Webapp

class DesktopManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def update_desktop_db() -> None:
        """Tells the desktop environment to reload application shortcuts."""
        try:
            subprocess.run(["update-desktop-database", APPLICATIONS_DIR], check=False)
        except Exception:
            pass

    def create_entry(self, webapp: Webapp) -> None:
        """Writes the .desktop file with all necessary KDE webapp keys from a Webapp instance."""
        config = configparser.ConfigParser(interpolation=None)
        config.optionxform = str
        config['Desktop Entry'] = {
            'Version': '1.0',
            'Type': 'Application',
            'Name': webapp.name,
            'Comment': f'Webapp for {webapp.name}',
            'Exec': webapp.exec_line,
            'Icon': webapp.icon,
            'Terminal': 'false',
            'StartupWMClass': webapp.wm_class,
            'X-KDE-Webapp': 'true',
            'X-KDE-Webapp-Url': webapp.url,
            'X-KDE-Webapp-Browser': webapp.browser,
            'X-KDE-Webapp-Width': str(webapp.width),
            'X-KDE-Webapp-Height': str(webapp.height),
            'X-KDE-Webapp-UserDataDir': webapp.user_data_dir,
            'X-KDE-Webapp-Class': webapp.wm_class
        }
        
        with open(webapp.filepath, 'w') as f:
            config.write(f, space_around_delimiters=False)
        os.chmod(webapp.filepath, 0o755)
        self.update_desktop_db()
        webapp._saved_memento = webapp.create_memento()

    def delete_entry(self, filepath: str) -> None:
        """Removes the .desktop file and updates database."""
        if os.path.exists(filepath):
            os.remove(filepath)
            self.update_desktop_db()

    def load_all_entries(self, browsers: List[Tuple[str, str]]) -> List[Webapp]:
        """Loads and parses all webapp .desktop entries in the applications directory."""
        desktop_files = glob.glob(os.path.join(APPLICATIONS_DIR, "*.desktop"))
        webapps: List[Webapp] = []
        
        for filepath in desktop_files:
            try:
                parser = configparser.ConfigParser(interpolation=None)
                parser.optionxform = str
                parser.read(filepath)
                
                if 'Desktop Entry' in parser:
                    entry = parser['Desktop Entry']
                    is_webapp = False
                    
                    if entry.get('X-KDE-Webapp') == 'true':
                        is_webapp = True
                        url = entry.get('X-KDE-Webapp-Url', '')
                        browser_cmd = entry.get('X-KDE-Webapp-Browser', '')
                        try:
                            width = int(entry.get('X-KDE-Webapp-Width', '1024'))
                        except ValueError:
                            width = 1024
                        try:
                            height = int(entry.get('X-KDE-Webapp-Height', '768'))
                        except ValueError:
                            height = 768
                        user_data_dir = entry.get('X-KDE-Webapp-UserDataDir', '')
                        wm_class = entry.get('X-KDE-Webapp-Class', '')
                    else:
                        # Fallback heuristic: check if it runs a site-specific browser using --app=
                        exec_line = entry.get('Exec', '')
                        if '--app=http' in exec_line or '--app=https' in exec_line:
                            is_webapp = True
                            
                            # Parse URL
                            url_match = re.search(r'--app=["\']?(https?://[^\s"\']+)["\']?', exec_line)
                            url = url_match.group(1) if url_match else ""
                            
                            # Parse size
                            width, height = 1024, 768
                            size_match = re.search(r'--window-size=(\d+),(\d+)', exec_line)
                            if size_match:
                                try:
                                    width = int(size_match.group(1))
                                    height = int(size_match.group(2))
                                except ValueError:
                                    pass
                                
                            # Parse User Data Dir
                            user_data_dir = ""
                            ud_match = re.search(r'--user-data-dir=["\']?([^\s"\']+)["\']?', exec_line)
                            if ud_match:
                                user_data_dir = ud_match.group(1)
                                
                            # Parse Class
                            wm_class = ""
                            class_match = re.search(r'--class=["\']?([^\s"\']+)["\']?', exec_line)
                            if class_match:
                                wm_class = class_match.group(1)
                                
                            # Parse Browser
                            first_part = exec_line.split('--')[0].strip()
                            browser_cmd = "google-chrome-stable"
                            for b_name, b_cmd in browsers:
                                if b_cmd in first_part:
                                    browser_cmd = b_cmd
                                    break
                            else:
                                tokens = exec_line.split()
                                if tokens:
                                    browser_cmd = os.path.basename(tokens[0].replace('"', '').replace("'", ""))

                    if is_webapp:
                        app = Webapp(
                            name=entry.get('Name', 'Untitled'),
                            url=url,
                            browser=browser_cmd,
                            width=width,
                            height=height,
                            user_data_dir=user_data_dir,
                            wm_class=wm_class,
                            icon=entry.get('Icon', ''),
                            filepath=filepath
                        )
                        app._saved_memento = app.create_memento()
                        webapps.append(app)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
        
        # Sort alphabetically
        webapps.sort(key=lambda x: x.name.lower())
        return webapps
