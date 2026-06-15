import os
import shutil
import subprocess
import configparser
from typing import Optional, Tuple

class KWinRuleManager:
    @staticmethod
    def get_browser_wmclass_prefix(browser_cmd: str) -> Tuple[str, str]:
        """Returns the main prefix and sub-prefix for KWin window rules based on the selected browser."""
        main_prefix = "chrome"
        sub_prefix = "chrome"
        
        cmd_lower = browser_cmd.lower()
        if "com.brave.browser" in cmd_lower:
            main_prefix = "com.brave.Browser"
            sub_prefix = "brave"
        elif "com.google.chrome" in cmd_lower:
            main_prefix = "com.google.Chrome"
            sub_prefix = "chrome"
        elif "org.chromium.chromium" in cmd_lower:
            main_prefix = "org.chromium.Chromium"
            sub_prefix = "chromium"
        elif "com.microsoft.edge" in cmd_lower:
            main_prefix = "com.microsoft.Edge"
            sub_prefix = "msedge"
        elif "com.vivaldi.vivaldi" in cmd_lower:
            main_prefix = "com.vivaldi.Vivaldi"
            sub_prefix = "vivaldi"
        elif "brave" in cmd_lower:
            main_prefix = "brave-browser"
            sub_prefix = "brave"
        elif "edge" in cmd_lower:
            main_prefix = "microsoft-edge"
            sub_prefix = "msedge"
        elif "chromium" in cmd_lower:
            main_prefix = "chromium-browser"
            sub_prefix = "chromium"
        elif "vivaldi" in cmd_lower:
            main_prefix = "vivaldi-stable"
            sub_prefix = "vivaldi"
            
        return main_prefix, sub_prefix

    @classmethod
    def add_rule(cls, app_name: str, url: str, browser_cmd: str, desktop_file_basename: str,
                 width: Optional[int] = None, height: Optional[int] = None) -> None:
        """Automatically adds or updates a KDE KWin window rule to force association
        between the browser window (detected via Wayland app-id/WM_CLASS) and the desktop shortcut file.
        """
        import uuid
        kwinrules_path = os.path.expanduser("~/.config/kwinrulesrc")
        
        config = configparser.ConfigParser(interpolation=None)
        config.optionxform = str
        
        if os.path.exists(kwinrules_path):
            try:
                config.read(kwinrules_path)
            except Exception as e:
                print(f"Error reading kwinrulesrc: {e}")
                return
                
        # Check if a rule for this desktop file already exists
        rule_uuid = None
        for section in config.sections():
            if section == 'General':
                continue
            if config.get(section, 'desktopfile', fallback='') == desktop_file_basename:
                rule_uuid = section
                break
                
        if not rule_uuid:
            rule_uuid = str(uuid.uuid4())
            
        # Format url to derive class name
        clean_url = url.replace("https://", "").replace("http://", "")
        if clean_url.endswith("/"):
            clean_url = clean_url[:-1]
            
        parts = clean_url.split("/", 1)
        domain = parts[0]
        path = parts[1] if len(parts) > 1 else ""
        path_clean = path.replace("/", "_")
        
        main_prefix, sub_prefix = cls.get_browser_wmclass_prefix(browser_cmd)
        wmclass = f"{sub_prefix}-{domain}__{path_clean}-Default"
        full_wmclass = f"{main_prefix} {wmclass}"
        
        rule_data = {
            'Description': f'Window settings for {app_name} webapp',
            'desktopfile': desktop_file_basename,
            'desktopfilerule': '2', # 2 means "Force" (Forçar)
            'types': '1', # 1 means "Normal Window"
            'wmclass': full_wmclass,
            'wmclasscomplete': 'true',
            'wmclassmatch': '1' # 1 means "Exact match"
        }
        
        if width and height:
            rule_data['size'] = f"{width},{height}"
            rule_data['sizerule'] = '3' # 3 means "Apply Initially"
            
        config[rule_uuid] = rule_data
        
        if 'General' not in config:
            config['General'] = {'count': '0', 'rules': ''}
            
        rules_list = config.get('General', 'rules', fallback='').split(',')
        rules_list = [r.strip() for r in rules_list if r.strip()]
        
        if rule_uuid not in rules_list:
            rules_list.append(rule_uuid)
            
        config['General']['rules'] = ','.join(rules_list)
        config['General']['count'] = str(len(rules_list))
        
        try:
            with open(kwinrules_path, 'w') as f:
                config.write(f, space_around_delimiters=False)
            print(f"KWin window rule added/updated for {app_name} ({desktop_file_basename})")
            
            # Notify KWin to reload rules (try qdbus, qdbus6, then dbus-send)
            try:
                if shutil.which("qdbus"):
                    subprocess.run(["qdbus", "org.kde.KWin", "/KWin", "reconfigure"], check=False)
                elif shutil.which("qdbus6"):
                    subprocess.run(["qdbus6", "org.kde.KWin", "/KWin", "reconfigure"], check=False)
                elif shutil.which("dbus-send"):
                    subprocess.run(["dbus-send", "--session", "--dest=org.kde.KWin", "/KWin", "org.kde.KWin.reconfigure"], check=False)
            except Exception as dbus_err:
                print(f"Failed to notify KWin via DBus (rules are saved but not reloaded dynamically): {dbus_err}")
        except Exception as e:
            print(f"Failed to write to kwinrulesrc: {e}")

    @staticmethod
    def remove_rule(desktop_file_basename: str) -> None:
        """Automatically removes the associated KWin window rule when deleting a webapp."""
        kwinrules_path = os.path.expanduser("~/.config/kwinrulesrc")
        if not os.path.exists(kwinrules_path):
            return
            
        config = configparser.ConfigParser(interpolation=None)
        config.optionxform = str
        
        try:
            config.read(kwinrules_path)
        except Exception as e:
            print(f"Error reading kwinrulesrc: {e}")
            return
            
        rule_uuid = None
        for section in config.sections():
            if section == 'General':
                continue
            if config.get(section, 'desktopfile', fallback='') == desktop_file_basename:
                rule_uuid = section
                break
                
        if rule_uuid:
            config.remove_section(rule_uuid)
            
            if 'General' in config:
                rules_list = config.get('General', 'rules', fallback='').split(',')
                rules_list = [r.strip() for r in rules_list if r.strip() and r.strip() != rule_uuid]
                config['General']['rules'] = ','.join(rules_list)
                config['General']['count'] = str(len(rules_list))
                
            try:
                with open(kwinrules_path, 'w') as f:
                    config.write(f, space_around_delimiters=False)
                print(f"KWin window rule removed for {desktop_file_basename}")
                
                # Notify KWin to reload rules (try qdbus, qdbus6, then dbus-send)
                try:
                    if shutil.which("qdbus"):
                        subprocess.run(["qdbus", "org.kde.KWin", "/KWin", "reconfigure"], check=False)
                    elif shutil.which("qdbus6"):
                        subprocess.run(["qdbus6", "org.kde.KWin", "/KWin", "reconfigure"], check=False)
                    elif shutil.which("dbus-send"):
                        subprocess.run(["dbus-send", "--session", "--dest=org.kde.KWin", "/KWin", "org.kde.KWin.reconfigure"], check=False)
                except Exception as dbus_err:
                    print(f"Failed to notify KWin via DBus: {dbus_err}")
            except Exception as e:
                print(f"Failed to write to kwinrulesrc: {e}")
