#!/usr/bin/env python3
import sys
import os
import shutil
import subprocess
import re
import glob
import configparser

from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QSpinBox, QComboBox, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QScrollArea,
    QFrame, QGraphicsDropShadowEffect, QSplitter
)
from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor, QPainter, QPainterPath

# Paths
APPLICATIONS_DIR = os.path.expanduser("~/.local/share/applications/")
ICONS_DIR = os.path.expanduser("~/.local/share/icons/")
DEFAULT_USER_DATA_BASE = os.path.expanduser("~/.config/webapps/")

# Create directories if they don't exist
os.makedirs(APPLICATIONS_DIR, exist_ok=True)
os.makedirs(ICONS_DIR, exist_ok=True)
os.makedirs(DEFAULT_USER_DATA_BASE, exist_ok=True)

def update_desktop_db():
    """Tells the desktop environment to reload application shortcuts."""
    try:
        subprocess.run(["update-desktop-database", APPLICATIONS_DIR], check=False)
    except Exception:
        pass

def get_rounded_pixmap(pixmap, radius=8):
    """Crops a QPixmap to have rounded corners for a premium appearance."""
    if pixmap.isNull():
        return pixmap
    
    # Scale to standard size (e.g. 40x40)
    scaled = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
    
    target = QPixmap(40, 40)
    target.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(target)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    
    path = QPainterPath()
    path.addRoundedRect(0, 0, 40, 40, radius, radius)
    
    painter.setClipPath(path)
    # Draw centered
    x = (40 - scaled.width()) // 2
    y = (40 - scaled.height()) // 2
    painter.drawPixmap(x, y, scaled)
    painter.end()
    return target

def detect_browsers():
    """Detects installed Chromium-based browsers that support the --app flag."""
    candidates = [
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
    browsers = []
    seen = set()
    for name, cmd in candidates:
        path = shutil.which(cmd)
        if path:
            real_cmd = os.path.basename(path)
            if real_cmd not in seen:
                seen.add(real_cmd)
                browsers.append((name, cmd))
    return browsers

def migrate_profile_if_needed(user_data_path_raw):
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

def get_browser_wmclass_prefix(browser_cmd):
    """Returns the main prefix and sub-prefix for KWin window rules based on the selected browser."""
    main_prefix = "chrome"
    sub_prefix = "chrome"
    
    cmd_lower = browser_cmd.lower()
    if "brave" in cmd_lower:
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

def add_kwin_rule(app_name, url, browser_cmd, desktop_file_basename):
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
    
    main_prefix, sub_prefix = get_browser_wmclass_prefix(browser_cmd)
    wmclass = f"{sub_prefix}-{domain}__{path_clean}-Default"
    full_wmclass = f"{main_prefix} {wmclass}"
    
    config[rule_uuid] = {
        'Description': f'Window settings for {app_name} webapp',
        'desktopfile': desktop_file_basename,
        'desktopfilerule': '2', # 2 means "Force" (Forçar)
        'types': '1', # 1 means "Normal Window"
        'wmclass': full_wmclass,
        'wmclasscomplete': 'true',
        'wmclassmatch': '1' # 1 means "Exact match"
    }
    
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

def remove_kwin_rule(desktop_file_basename):
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

class WebappListItemWidget(QWidget):
    """Custom widget for the list items in the sidebar, displaying icon, name, and URL."""
    def __init__(self, name, url, icon_path_or_name, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(40, 40)
        layout.addWidget(self.icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #ffffff; background: transparent;")
        text_layout.addWidget(self.name_label)
        
        self.url_label = QLabel(url)
        self.url_label.setStyleSheet("font-size: 11px; color: #8a99ad; background: transparent;")
        text_layout.addWidget(self.url_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.update_icon(icon_path_or_name)

    def update_icon(self, icon_path_or_name):
        pixmap = QPixmap()
        if icon_path_or_name and os.path.exists(icon_path_or_name):
            pixmap.load(icon_path_or_name)
        elif icon_path_or_name:
            icon = QIcon.fromTheme(icon_path_or_name)
            if not icon.isNull():
                pixmap = icon.pixmap(64, 64)
        
        if pixmap.isNull():
            # Fallback icon
            icon = QIcon.fromTheme("applications-internet")
            if not icon.isNull():
                pixmap = icon.pixmap(64, 64)
        
        rounded = get_rounded_pixmap(pixmap, radius=8)
        self.icon_label.setPixmap(rounded)

    def update_text(self, name, url):
        self.name_label.setText(name)
        self.url_label.setText(url)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KDE Webapp Manager")
        self.resize(900, 650)
        
        self.browsers = detect_browsers()
        self.current_filepath = None
        self.custom_icon_path = None
        self.is_modifying_userdata = False
        self.is_modifying_class = False
        
        self.init_ui()
        self.apply_theme()
        self.load_webapps()
        self.new_webapp()

    def init_ui(self):
        # Splitter to divide Sidebar and Main panel
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)
        
        # --- SIDEBAR CONTAINER ---
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebarContainer")
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 10, 0, 10)
        sidebar_layout.setSpacing(8)
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("searchBar")
        self.search_bar.setPlaceholderText("Search webapps...")
        self.search_bar.textChanged.connect(self.filter_webapps)
        sidebar_layout.addWidget(self.search_bar)
        
        # List of webapps
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("webappList")
        self.list_widget.itemSelectionChanged.connect(self.on_webapp_selected)
        sidebar_layout.addWidget(self.list_widget)
        
        # Add Webapp Button
        self.btn_new = QPushButton("+ New Webapp")
        self.btn_new.setObjectName("btnPrimary")
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.clicked.connect(self.new_webapp)
        
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(10, 5, 10, 5)
        btn_layout.addWidget(self.btn_new)
        sidebar_layout.addLayout(btn_layout)
        
        # --- MAIN EDITOR CONTAINER ---
        editor_scroll = QScrollArea()
        editor_scroll.setWidgetResizable(True)
        editor_scroll.setObjectName("editorScroll")
        
        editor_widget = QWidget()
        editor_widget.setObjectName("editorContainer")
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(25, 25, 25, 25)
        editor_layout.setSpacing(15)
        
        # Header title
        self.header_title = QLabel("Create New Webapp")
        self.header_title.setObjectName("titleLabel")
        editor_layout.addWidget(self.header_title)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Name
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("e.g. WhatsApp")
        self.input_name.textChanged.connect(self.on_name_changed)
        form_layout.addRow("App Name:", self.input_name)
        
        # URL
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("e.g. https://web.whatsapp.com")
        self.input_url.textChanged.connect(self.update_command_preview)
        form_layout.addRow("Site URL:", self.input_url)
        
        # Browser selection
        self.combo_browser = QComboBox()
        for name, cmd in self.browsers:
            self.combo_browser.addItem(name, cmd)
        if not self.browsers:
            self.combo_browser.addItem("No Chromium browser detected!", "")
        self.combo_browser.currentIndexChanged.connect(self.update_command_preview)
        form_layout.addRow("Browser:", self.combo_browser)
        
        # Dimensions layout
        dim_layout = QHBoxLayout()
        self.spin_width = QSpinBox()
        self.spin_width.setRange(200, 4000)
        self.spin_width.setValue(1024)
        self.spin_width.valueChanged.connect(self.update_command_preview)
        
        self.spin_height = QSpinBox()
        self.spin_height.setRange(200, 4000)
        self.spin_height.setValue(768)
        self.spin_height.valueChanged.connect(self.update_command_preview)
        
        dim_layout.addWidget(self.spin_width)
        dim_layout.addWidget(QLabel(" x "))
        dim_layout.addWidget(self.spin_height)
        dim_layout.addStretch()
        form_layout.addRow("Dimensions:", dim_layout)
        
        # Icon row
        icon_row_layout = QHBoxLayout()
        
        self.icon_preview_frame = QFrame()
        self.icon_preview_frame.setObjectName("iconPreviewBox")
        self.icon_preview_frame.setFixedSize(54, 54)
        icon_preview_layout = QVBoxLayout(self.icon_preview_frame)
        icon_preview_layout.setContentsMargins(6, 6, 6, 6)
        
        self.lbl_icon_preview = QLabel()
        self.lbl_icon_preview.setScaledContents(True)
        icon_preview_layout.addWidget(self.lbl_icon_preview)
        
        icon_row_layout.addWidget(self.icon_preview_frame)
        
        icon_input_layout = QVBoxLayout()
        icon_input_layout.setSpacing(4)
        
        self.input_icon = QLineEdit()
        self.input_icon.setPlaceholderText("System icon name or image file path")
        self.input_icon.textChanged.connect(self.on_icon_input_changed)
        icon_input_layout.addWidget(self.input_icon)
        
        self.btn_select_icon = QPushButton("Select Image...")
        self.btn_select_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_icon.clicked.connect(self.select_custom_icon)
        
        icon_btn_layout = QHBoxLayout()
        icon_btn_layout.addWidget(self.btn_select_icon)
        icon_btn_layout.addStretch()
        icon_input_layout.addLayout(icon_btn_layout)
        
        icon_row_layout.addLayout(icon_input_layout)
        form_layout.addRow("Icon:", icon_row_layout)
        
        # Advanced Title
        advanced_title = QLabel("Advanced Settings")
        advanced_title.setObjectName("sectionTitle")
        form_layout.addRow("", advanced_title)
        
        # User Data Dir
        self.input_userdata = QLineEdit()
        self.input_userdata.setPlaceholderText("Auto-generated")
        self.input_userdata.textChanged.connect(self.on_userdata_edited)
        form_layout.addRow("Profile (User Data):", self.input_userdata)
        
        # Window Class
        self.input_class = QLineEdit()
        self.input_class.setPlaceholderText("Auto-generated")
        self.input_class.textChanged.connect(self.on_class_edited)
        form_layout.addRow("Window Class:", self.input_class)
        
        editor_layout.addLayout(form_layout)
        
        # Command Preview Header
        cmd_title = QLabel("Command to be Executed:")
        cmd_title.setStyleSheet("font-weight: bold; color: #a5b4fc; margin-top: 10px;")
        editor_layout.addWidget(cmd_title)
        
        # Command Preview Block
        self.lbl_cmd_preview = QLabel()
        self.lbl_cmd_preview.setObjectName("commandPreview")
        self.lbl_cmd_preview.setWordWrap(True)
        editor_layout.addWidget(self.lbl_cmd_preview)
        
        # Button bar
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        action_layout.setContentsMargins(0, 15, 0, 0)
        
        self.btn_test = QPushButton("Test Launch")
        self.btn_test.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_test.clicked.connect(self.test_run)
        action_layout.addWidget(self.btn_test)
        
        self.btn_save = QPushButton("Save Webapp")
        self.btn_save.setObjectName("btnPrimary")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self.save_webapp)
        action_layout.addWidget(self.btn_save)
        
        action_layout.addStretch()
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_webapp)
        action_layout.addWidget(self.btn_delete)
        
        editor_layout.addLayout(action_layout)
        editor_layout.addStretch()
        
        editor_scroll.setWidget(editor_widget)
        
        # Set up splitter widgets
        splitter.addWidget(sidebar_widget)
        splitter.addWidget(editor_scroll)
        
        # Set sidebar proportion
        splitter.setSizes([320, 580])

    def apply_theme(self):
        """Applies the custom, high-fidelity dark stylesheet to match KDE dark elements."""
        qss = """
        QMainWindow {
            background-color: #11141a;
        }

        QSplitter::handle {
            background-color: #1b202c;
            width: 2px;
        }

        /* Sidebar Container */
        QWidget#sidebarContainer {
            background-color: #161a23;
            border-right: 1px solid #222a3a;
        }

        /* Search Bar styling */
        QLineEdit#searchBar {
            background-color: #1e2433;
            border: 1px solid #283147;
            border-radius: 16px;
            padding: 6px 14px;
            margin: 8px 10px;
            color: #ffffff;
            font-size: 13px;
        }

        QLineEdit#searchBar:focus {
            border-color: #00b4d8;
        }

        /* Webapp List View */
        QListWidget#webappList {
            background-color: transparent;
            border: none;
            outline: none;
        }

        QListWidget#webappList::item {
            background-color: #1e2433;
            border-radius: 8px;
            margin: 4px 8px;
            border: 1px solid #283147;
        }

        QListWidget#webappList::item:hover {
            background-color: #262e42;
            border-color: #384666;
        }

        QListWidget#webappList::item:selected {
            background-color: #313d59;
            border-color: #00b4d8;
        }

        /* ScrollBar styling */
        QScrollBar:vertical {
            border: none;
            background: #11141a;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #283147;
            min-height: 20px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover {
            background: #3e4d6f;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
            background: none;
        }
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            background: none;
        }

        /* Main Editor area */
        QScrollArea#editorScroll {
            border: none;
            background-color: #11141a;
        }

        QWidget#editorContainer {
            background-color: #11141a;
        }

        QLabel {
            color: #c4cbd4;
            font-size: 13px;
        }

        QLabel#titleLabel {
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
            padding-bottom: 5px;
            border-bottom: 2px solid #1b202c;
        }

        QLabel#sectionTitle {
            font-size: 14px;
            font-weight: bold;
            color: #00b4d8;
            margin-top: 15px;
            margin-bottom: 5px;
        }

        QLineEdit, QSpinBox, QComboBox {
            background-color: #1e2433;
            border: 1px solid #2c364c;
            border-radius: 6px;
            padding: 8px 12px;
            color: #ffffff;
            font-size: 13px;
        }

        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border: 1px solid #00b4d8;
            background-color: #22293a;
        }

        /* QSpinBox custom styling to nest up/down buttons and look integrated */
        QSpinBox {
            padding-right: 24px;
        }

        QSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #2c364c;
            border-top-right-radius: 5px;
            background-color: #252d3d;
        }

        QSpinBox::up-button:hover {
            background-color: #313d59;
        }

        QSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 20px;
            border-left: 1px solid #2c364c;
            border-bottom-right-radius: 5px;
            background-color: #252d3d;
        }

        QSpinBox::down-button:hover {
            background-color: #313d59;
        }

        QSpinBox::up-arrow {
            image: url(none);
            width: 0;
            height: 0;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: 4px solid #ffffff;
        }

        QSpinBox::down-arrow {
            image: url(none);
            width: 0;
            height: 0;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #ffffff;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left-width: 0px;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }

        /* Buttons styling */
        QPushButton {
            background-color: #22293a;
            border: 1px solid #323d56;
            border-radius: 6px;
            padding: 10px 18px;
            color: #ffffff;
            font-weight: bold;
            font-size: 13px;
        }

        QPushButton:hover {
            background-color: #2b354c;
            border-color: #43547a;
        }

        QPushButton:pressed {
            background-color: #1d2230;
        }

        QPushButton#btnPrimary {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0077b6, stop:1 #00b4d8);
            border: none;
            color: #ffffff;
        }

        QPushButton#btnPrimary:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0096c7, stop:1 #00c4ec);
        }

        QPushButton#btnPrimary:pressed {
            background: #0077b6;
        }

        QPushButton#btnDanger {
            background-color: #3a1a1f;
            border: 1px solid #6b212c;
            color: #ff8b94;
        }

        QPushButton#btnDanger:hover {
            background-color: #4f1d24;
            border-color: #902d3b;
            color: #ffb3b8;
        }

        QPushButton#btnDanger:pressed {
            background-color: #291215;
        }

        /* Command preview code block */
        QLabel#commandPreview {
            background-color: #090b0e;
            border: 1px solid #1c212b;
            border-radius: 6px;
            padding: 12px;
            font-family: "Monospace", "Courier New", monospace;
            font-size: 12px;
            color: #a5b4fc;
        }

        /* Icon preview box */
        QFrame#iconPreviewBox {
            background-color: #161a23;
            border: 1px solid #283147;
            border-radius: 8px;
        }
        """
        self.setStyleSheet(qss)

    def load_webapps(self):
        """Scans the standard local application directory for webapps."""
        self.list_widget.clear()
        
        desktop_files = glob.glob(os.path.join(APPLICATIONS_DIR, "*.desktop"))
        webapps = []
        
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
                            for b_name, b_cmd in self.browsers:
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
        
        for app in webapps:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 60))
            item.setData(Qt.ItemDataRole.UserRole, app)
            
            self.list_widget.addItem(item)
            
            widget = WebappListItemWidget(app['name'], app['url'], app['icon'])
            self.list_widget.setItemWidget(item, widget)

    def filter_webapps(self):
        """Filters the webapp list according to text typed in the search bar."""
        query = self.search_bar.text().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            app_data = item.data(Qt.ItemDataRole.UserRole)
            
            if app_data:
                name_matches = query in app_data['name'].lower()
                url_matches = query in app_data['url'].lower()
                item.setHidden(not (name_matches or url_matches))

    def on_webapp_selected(self):
        """Handles loading a webapp's details into the editor when selected in the sidebar."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        app = item.data(Qt.ItemDataRole.UserRole)
        
        if not app:
            return
            
        # Trigger migration in background if it has literal $HOME profile path
        migrate_profile_if_needed(app['user_data_dir'])
            
        self.current_filepath = app['filepath']
        self.header_title.setText(f"Edit: {app['name']}")
        
        # Block signals temporarily to prevent loops during form population
        self.input_name.blockSignals(True)
        self.input_url.blockSignals(True)
        self.combo_browser.blockSignals(True)
        self.spin_width.blockSignals(True)
        self.spin_height.blockSignals(True)
        self.input_icon.blockSignals(True)
        self.input_userdata.blockSignals(True)
        self.input_class.blockSignals(True)
        
        self.input_name.setText(app['name'])
        self.input_url.setText(app['url'])
        
        # Select browser
        idx = self.combo_browser.findData(app['browser'])
        if idx >= 0:
            self.combo_browser.setCurrentIndex(idx)
        
        self.spin_width.setValue(app['width'])
        self.spin_height.setValue(app['height'])
        self.input_icon.setText(app['icon'])
        
        # Pre-fill expanded path in field if it was imported as $HOME, but keep track of it
        expanded_ud = os.path.expandvars(os.path.expanduser(app['user_data_dir']))
        self.input_userdata.setText(expanded_ud)
        self.input_class.setText(app['wm_class'])
        
        self.custom_icon_path = app['icon'] if os.path.exists(app['icon']) else None
        
        # Keep track if they customized these manually
        self.is_modifying_userdata = True
        self.is_modifying_class = True
        
        self.input_name.blockSignals(False)
        self.input_url.blockSignals(False)
        self.combo_browser.blockSignals(False)
        self.spin_width.blockSignals(False)
        self.spin_height.blockSignals(False)
        self.input_icon.blockSignals(False)
        self.input_userdata.blockSignals(False)
        self.input_class.blockSignals(False)
        
        self.update_icon_preview(app['icon'])
        self.update_command_preview()
        
        self.btn_delete.setEnabled(True)

    def new_webapp(self):
        """Resets the form fields to default values for creating a new webapp."""
        self.list_widget.clearSelection()
        self.current_filepath = None
        self.custom_icon_path = None
        self.is_modifying_userdata = False
        self.is_modifying_class = False
        
        self.header_title.setText("Create New Webapp")
        
        self.input_name.setText("")
        self.input_url.setText("")
        self.spin_width.setValue(1024)
        self.spin_height.setValue(768)
        self.input_icon.setText("applications-internet")
        self.input_userdata.setText("")
        self.input_class.setText("")
        
        if self.combo_browser.count() > 0:
            self.combo_browser.setCurrentIndex(0)
            
        self.update_icon_preview("applications-internet")
        self.update_command_preview()
        
        self.btn_delete.setEnabled(False)
        self.input_name.setFocus()

    def on_name_changed(self):
        """Auto-completes fields like user-data-dir and window class as the user types the app name."""
        name = self.input_name.text()
        slug = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
        
        if not self.is_modifying_userdata:
            if slug:
                self.input_userdata.setText(os.path.join(DEFAULT_USER_DATA_BASE, slug))
            else:
                self.input_userdata.setText("")
                
        if not self.is_modifying_class:
            self.input_class.setText(slug)
            
        # Also auto-update icon name if it was a default placeholder
        if self.input_icon.text() in ["applications-internet", ""] and slug:
            self.input_icon.setText(slug)
            
        self.update_command_preview()

    def on_userdata_edited(self):
        self.is_modifying_userdata = True
        self.update_command_preview()

    def on_class_edited(self):
        self.is_modifying_class = True
        self.update_command_preview()

    def on_icon_input_changed(self):
        icon_text = self.input_icon.text().strip()
        self.update_icon_preview(icon_text)

    def select_custom_icon(self):
        """Opens a file dialog to choose a custom local image (PNG/SVG) for the app icon."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Webapp Icon", "",
            "Images (*.png *.svg *.jpg *.jpeg *.ico);;All Files (*)"
        )
        if file_path:
            self.custom_icon_path = file_path
            self.input_icon.setText(file_path)
            self.update_icon_preview(file_path)

    def update_icon_preview(self, icon_path_or_name):
        """Updates the icon preview thumbnail in the form."""
        pixmap = QPixmap()
        if icon_path_or_name and os.path.exists(icon_path_or_name):
            pixmap.load(icon_path_or_name)
        elif icon_path_or_name:
            icon = QIcon.fromTheme(icon_path_or_name)
            if not icon.isNull():
                pixmap = icon.pixmap(48, 48)
        
        if pixmap.isNull():
            icon = QIcon.fromTheme("applications-internet")
            if not icon.isNull():
                pixmap = icon.pixmap(48, 48)
                
        rounded = get_rounded_pixmap(pixmap, radius=6)
        self.lbl_icon_preview.setPixmap(rounded)

    def get_built_command(self):
        """Constructs the exact command string to run the webapp."""
        browser_cmd = self.combo_browser.currentData() or "google-chrome-stable"
        width = self.spin_width.value()
        height = self.spin_height.value()
        url = self.input_url.text().strip() or "https://..."
        user_data = self.input_userdata.text().strip()
        wm_class = self.input_class.text().strip()
        
        cmd = f"{browser_cmd} --window-size={width},{height}"
        if wm_class:
            cmd += f" --class={wm_class}"
        cmd += f" --app={url}"
        if user_data:
            cmd += f" --user-data-dir={user_data}"
            
        return cmd

    def update_command_preview(self):
        """Renders the command preview label with the current form values."""
        self.lbl_cmd_preview.setText(self.get_built_command())

    def test_run(self):
        """Launches the app in a background process to test settings before saving."""
        browser_cmd = self.combo_browser.currentData() or "google-chrome-stable"
        width = self.spin_width.value()
        height = self.spin_height.value()
        url = self.input_url.text().strip()
        user_data = self.input_userdata.text().strip()
        wm_class = self.input_class.text().strip()
        
        if not url or url == "https://...":
            QMessageBox.warning(self, "Warning", "Please enter a valid URL first.")
            return
            
        # Run profile migration if needed before launching
        migrate_profile_if_needed(user_data)
            
        args = [
            browser_cmd,
            f"--window-size={width},{height}",
            f"--class={wm_class}",
            f"--app={url}"
        ]
        if user_data:
            resolved_ud = os.path.expandvars(os.path.expanduser(user_data))
            args.append(f"--user-data-dir={resolved_ud}")
            
        try:
            # Run detached so it keeps running when manager closes
            subprocess.Popen(args, start_new_session=True)
        except Exception as e:
            QMessageBox.critical(self, "Error Launching", f"Failed to execute browser:\n{e}")

    def save_webapp(self):
        """Saves or edits the webapp shortcut (writes the .desktop file)."""
        name = self.input_name.text().strip()
        url = self.input_url.text().strip()
        browser_cmd = self.combo_browser.currentData()
        
        if not name:
            QMessageBox.warning(self, "Warning", "Please fill in the App Name.")
            self.input_name.setFocus()
            return
        if not url or url == "https://...":
            QMessageBox.warning(self, "Warning", "Please fill in the Site URL.")
            self.input_url.setFocus()
            return
        if not browser_cmd:
            QMessageBox.warning(self, "Warning", "No valid Chromium browser selected.")
            return

        width = self.spin_width.value()
        height = self.spin_height.value()
        user_data = self.input_userdata.text().strip()
        wm_class = self.input_class.text().strip()
        icon_input = self.input_icon.text().strip()

        # Migrate profile if needed before saving
        migrate_profile_if_needed(user_data)

        # Handle Icon copying
        final_icon_value = icon_input
        if self.custom_icon_path and os.path.exists(self.custom_icon_path):
            app_slug = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
            ext = os.path.splitext(self.custom_icon_path)[1]
            if not ext:
                ext = ".png"
            
            dest_name = f"webapp_{app_slug}{ext}"
            dest_path = os.path.join(ICONS_DIR, dest_name)
            
            try:
                shutil.copy2(self.custom_icon_path, dest_path)
                final_icon_value = dest_path
            except Exception as e:
                print(f"Error copying icon: {e}")

        # Construct desktop file path
        if self.current_filepath:
            filepath = self.current_filepath
        else:
            app_slug = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
            filepath = os.path.join(APPLICATIONS_DIR, f"webapp_{app_slug}.desktop")

        # Build execution line
        exec_line = f"{browser_cmd} --window-size={width},{height}"
        if wm_class:
            exec_line += f" --class={wm_class}"
        exec_line += f" --app={url}"
        if user_data:
            resolved_ud = os.path.expandvars(os.path.expanduser(user_data))
            exec_line += f" --user-data-dir={resolved_ud}"

        # Write desktop file
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

        try:
            with open(filepath, 'w') as f:
                config.write(f, space_around_delimiters=False)
            os.chmod(filepath, 0o755)
            update_desktop_db()
            
            # Auto-generate KWin window rule to force correct icon on Wayland
            desktop_file_basename = os.path.splitext(os.path.basename(filepath))[0]
            add_kwin_rule(name, url, browser_cmd, desktop_file_basename)
            
            QMessageBox.information(self, "Success", f"Webapp '{name}' saved successfully!")
            
            # Refresh list and select the item
            self.load_webapps()
            
            # Find and select the item we just saved
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                app_data = item.data(Qt.ItemDataRole.UserRole)
                if app_data and app_data['filepath'] == filepath:
                    self.list_widget.setCurrentItem(item)
                    break
        except Exception as e:
            QMessageBox.critical(self, "Error Saving", f"Failed to save .desktop file:\n{e}")

    def delete_webapp(self):
        """Deletes the current webapp shortcut and its launcher desktop file."""
        if not self.current_filepath:
            return
            
        name = self.input_name.text()
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the webapp '{name}'?\nThis will remove the shortcut from the KDE menu.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                selected_items = self.list_widget.selectedItems()
                if selected_items:
                    app = selected_items[0].data(Qt.ItemDataRole.UserRole)
                    if app and app['icon'] and os.path.exists(app['icon']) and ICONS_DIR in app['icon']:
                        os.remove(app['icon'])
                        
                desktop_file_basename = os.path.splitext(os.path.basename(self.current_filepath))[0]
                remove_kwin_rule(desktop_file_basename)
                
                os.remove(self.current_filepath)
                update_desktop_db()
                
                QMessageBox.information(self, "Success", f"Webapp '{name}' deleted.")
                
                self.load_webapps()
                self.new_webapp()
            except Exception as e:
                QMessageBox.critical(self, "Error Deleting", f"Failed to delete the shortcut:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
