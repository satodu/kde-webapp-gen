import os
import glob
import re
import subprocess
import configparser
from typing import List, Dict, Tuple, Any
from webapp_manager.constants import APPLICATIONS_DIR

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

    def create_entry(self, name: str, url: str, exec_line: str, final_icon_value: str,
                     wm_class: str, browser_cmd: str, width: int, height: int,
                     user_data: str, filepath: str) -> None:
        """Writes the .desktop file with all necessary KDE webapp keys."""
        config = configparser.ConfigParser(interpolation=None)
        config.optionxform = str
        config['Desktop Entry'] = {
            'Version': '1.0',
            'Type': 'Application',
            'Name': name,
            'Comment': f'Webapp for {name}',
            'Exec': exec_line,
            'Icon': final_icon_value,
            'Terminal': 'false',
            'StartupWMClass': wm_class,
            'X-KDE-Webapp': 'true',
            'X-KDE-Webapp-Url': url,
            'X-KDE-Webapp-Browser': browser_cmd,
            'X-KDE-Webapp-Width': str(width),
            'X-KDE-Webapp-Height': str(height),
            'X-KDE-Webapp-UserDataDir': user_data,
            'X-KDE-Webapp-Class': wm_class
        }
        
        with open(filepath, 'w') as f:
            config.write(f, space_around_delimiters=False)
        os.chmod(filepath, 0o755)
        self.update_desktop_db()

    def delete_entry(self, filepath: str) -> None:
        """Removes the .desktop file and updates database."""
        if os.path.exists(filepath):
            os.remove(filepath)
            self.update_desktop_db()

    def load_all_entries(self, browsers: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Loads and parses all webapp .desktop entries in the applications directory."""
        desktop_files = glob.glob(os.path.join(APPLICATIONS_DIR, "*.desktop"))
        webapps: List[Dict[str, Any]] = []
        
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
                        webapps.append({
                            'filepath': filepath,
                            'name': entry.get('Name', 'Untitled'),
                            'url': url,
                            'browser': browser_cmd,
                            'width': width,
                            'height': height,
                            'user_data_dir': user_data_dir,
                            'wm_class': wm_class,
                            'icon': entry.get('Icon', '')
                        })
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
        
        # Sort alphabetically
        webapps.sort(key=lambda x: x['name'].lower())
        return webapps
