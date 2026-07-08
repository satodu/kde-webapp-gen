import os
import shutil
import subprocess
import configparser
from typing import Optional, Tuple
from webapp_manager.models import Webapp

class KWinRuleManager:
    @classmethod
    def add_rule(cls, webapp: Webapp) -> None:
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
                
        # Calculate desktop file basename (e.g. webapp_whatsapp)
        desktop_file_basename = os.path.splitext(os.path.basename(webapp.filepath))[0]
        
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
        clean_url = webapp.url.replace("https://", "").replace("http://", "")
        if clean_url.endswith("/"):
            clean_url = clean_url[:-1]
            
        parts = clean_url.split("/", 1)
        domain = parts[0]
        path = parts[1] if len(parts) > 1 else ""
        path_clean = path.replace("/", "_")
        
        main_prefix, sub_prefix = webapp.get_browser_prefixes()
        wmclass = f"{sub_prefix}-{domain}__{path_clean}-Default"
        full_wmclass = f"{main_prefix} {wmclass}"
        
        rule_data = {
            'Description': f'Window settings for {webapp.name} webapp',
            'desktopfile': desktop_file_basename,
            'desktopfilerule': '2', # 2 means "Force" (Forçar)
            'types': '1', # 1 means "Normal Window"
            'wmclass': full_wmclass,
            'wmclasscomplete': 'true',
            'wmclassmatch': '1' # 1 means "Exact match"
        }
        
        if webapp.width and webapp.height:
            rule_data['size'] = f"{webapp.width},{webapp.height}"
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
            print(f"KWin window rule added/updated for {webapp.name} ({desktop_file_basename})")
            
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
