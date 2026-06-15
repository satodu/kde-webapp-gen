import os
import re
import shutil
import sys
import subprocess
from typing import Optional

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QSpinBox, QComboBox, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QScrollArea,
    QFrame, QSplitter
)
from PyQt6.QtGui import QIcon, QPixmap

from webapp_manager.constants import APPLICATIONS_DIR, ICONS_DIR, DEFAULT_USER_DATA_BASE
from webapp_manager.utils import get_rounded_pixmap, get_app_logo_pixmap, migrate_profile_if_needed
from webapp_manager.browser_detector import BrowserDetector
from webapp_manager.kwin_manager import KWinRuleManager
from webapp_manager.desktop_manager import DesktopManager

class WebappListItemWidget(QWidget):
    """Custom widget for the list items in the sidebar, displaying icon, name, and URL."""
    def __init__(self, name: str, url: str, icon_path_or_name: str, parent: Optional[QWidget] = None) -> None:
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
        self.name_label.setStyleSheet("font-weight: 600; font-size: 13px; color: #f8fafc; background: transparent;")
        text_layout.addWidget(self.name_label)
        
        self.url_label = QLabel(url)
        self.url_label.setStyleSheet("font-size: 11px; color: #94a3b8; background: transparent;")
        text_layout.addWidget(self.url_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.update_icon(icon_path_or_name)

    def update_icon(self, icon_path_or_name: str) -> None:
        pixmap = QPixmap()
        if icon_path_or_name and os.path.exists(icon_path_or_name):
            pixmap.load(icon_path_or_name)
        elif icon_path_or_name:
            icon = QIcon.fromTheme(icon_path_or_name)
            if not icon.isNull():
                pixmap = icon.pixmap(64, 64)
        
        if pixmap.isNull():
            icon = QIcon.fromTheme("applications-internet")
            if not icon.isNull():
                pixmap = icon.pixmap(64, 64)
        
        rounded = get_rounded_pixmap(pixmap, radius=8)
        self.icon_label.setPixmap(rounded)

    def update_text(self, name: str, url: str) -> None:
        self.name_label.setText(name)
        self.url_label.setText(url)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("KDE Webapp Manager")
        self.resize(900, 650)
        
        # Set window icon
        logo_pixmap = get_app_logo_pixmap()
        if not logo_pixmap.isNull():
            self.setWindowIcon(QIcon(logo_pixmap))
        
        self.browsers = BrowserDetector.detect_browsers()
        self.current_filepath: Optional[str] = None
        self.custom_icon_path: Optional[str] = None
        self.is_modifying_userdata: bool = False
        self.is_modifying_class: bool = False
        
        self.init_ui()
        self.apply_theme()
        self.load_webapps()
        self.new_webapp()

    def init_ui(self) -> None:
        # Splitter to divide Sidebar and Main panel
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)
        
        # --- SIDEBAR CONTAINER ---
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebarContainer")
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 10, 0, 10)
        sidebar_layout.setSpacing(8)
        
        # Sidebar Header (Logo + Title)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 10, 15, 5)
        header_layout.setSpacing(10)
        
        logo_label = QLabel()
        logo_label.setFixedSize(28, 28)
        logo_label.setScaledContents(True)
        
        logo_pixmap = get_app_logo_pixmap(28)
        logo_label.setPixmap(get_rounded_pixmap(logo_pixmap, radius=4))
        header_layout.addWidget(logo_label)
        
        sidebar_title = QLabel("Webapp Manager")
        sidebar_title.setStyleSheet("font-weight: bold; font-size: 15px; color: #ffffff; background: transparent;")
        header_layout.addWidget(sidebar_title)
        header_layout.addStretch()
        
        sidebar_layout.addLayout(header_layout)
        
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
        self.combo_browser.currentIndexChanged.connect(self.on_browser_changed)
        form_layout.addRow("Browser:", self.combo_browser)
        
        # Dimensions layout wrapper widget for alignment and padding
        dim_widget = QWidget()
        dim_layout = QHBoxLayout(dim_widget)
        dim_layout.setContentsMargins(0, 0, 0, 0)
        dim_layout.setSpacing(8)
        
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
        form_layout.addRow("Dimensions:", dim_widget)
        
        # Icon row wrapper widget for vertical centering and padding
        icon_row_widget = QWidget()
        icon_row_layout = QHBoxLayout(icon_row_widget)
        icon_row_layout.setContentsMargins(0, 0, 0, 0)
        icon_row_layout.setSpacing(12)
        
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
        icon_input_layout.setContentsMargins(0, 0, 0, 0)
        icon_input_layout.setSpacing(4)
        
        self.input_icon = QLineEdit()
        self.input_icon.setPlaceholderText("System icon name or image file path")
        self.input_icon.textChanged.connect(self.on_icon_input_changed)
        icon_input_layout.addWidget(self.input_icon)
        
        self.btn_select_icon = QPushButton("Select Image...")
        self.btn_select_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_icon.clicked.connect(self.select_custom_icon)
        
        icon_btn_layout = QHBoxLayout()
        icon_btn_layout.setContentsMargins(0, 0, 0, 0)
        icon_btn_layout.setSpacing(0)
        icon_btn_layout.addWidget(self.btn_select_icon)
        icon_btn_layout.addStretch()
        icon_input_layout.addLayout(icon_btn_layout)
        
        icon_row_layout.addLayout(icon_input_layout)
        form_layout.addRow("Icon:", icon_row_widget)
        
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
        cmd_title.setStyleSheet("font-weight: 600; color: #60a5fa; margin-top: 10px;")
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

    def apply_theme(self) -> None:
        """Applies the custom, high-fidelity dark stylesheet to match KDE dark elements."""
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        arrow_up = os.path.join(pkg_dir, "arrow-up.png").replace(os.sep, '/')
        arrow_up_hover = os.path.join(pkg_dir, "arrow-up-hover.png").replace(os.sep, '/')
        arrow_down = os.path.join(pkg_dir, "arrow-down.png").replace(os.sep, '/')
        arrow_down_hover = os.path.join(pkg_dir, "arrow-down-hover.png").replace(os.sep, '/')

        qss = """
        QMainWindow {
            background-color: #020817;
        }

        QSplitter::handle {
            background-color: #0f172a;
            width: 1px;
        }

        /* Sidebar Container */
        QWidget#sidebarContainer {
            background-color: #020817;
            border-right: 1px solid #0f172a;
        }

        /* Search Bar styling */
        QLineEdit#searchBar {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 6px;
            padding: 8px 12px;
            margin: 10px 15px;
            color: #f8fafc;
            font-size: 13px;
        }

        QLineEdit#searchBar:focus {
            border-color: #3b82f6;
        }

        /* Webapp List View */
        QListWidget#webappList {
            background-color: transparent;
            border: none;
            outline: none;
            padding: 0px 10px;
        }

        QListWidget#webappList::item {
            background-color: transparent;
            border-radius: 6px;
            margin: 4px 0px;
            border: 1px solid transparent;
        }

        QListWidget#webappList::item:hover {
            background-color: #0f172a;
            border-color: #1e293b;
        }

        QListWidget#webappList::item:selected {
            background-color: #0f172a;
            border-color: #3b82f6;
        }

        /* ScrollBar styling */
        QScrollBar:vertical {
            border: none;
            background: #020817;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #1e293b;
            min-height: 20px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover {
            background: #334155;
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
            background-color: #020817;
        }

        QWidget#editorContainer {
            background-color: #020817;
        }

        QLabel {
            color: #94a3b8;
            font-size: 13px;
        }

        QLabel#titleLabel {
            font-size: 20px;
            font-weight: 600;
            color: #f8fafc;
            padding-bottom: 8px;
            border-bottom: 1px solid #0f172a;
        }

        QLabel#sectionTitle {
            font-size: 14px;
            font-weight: 600;
            color: #3b82f6;
            margin-top: 15px;
            margin-bottom: 5px;
        }

        QLineEdit, QSpinBox, QComboBox {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 6px;
            color: #f8fafc;
            font-size: 13px;
            min-height: 32px;
            max-height: 32px;
        }

        QLineEdit {
            padding: 4px 12px;
        }

        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border: 1px solid #3b82f6;
            background-color: #0f172a;
        }

        /* QSpinBox custom styling to nest up/down buttons and look integrated */
        QSpinBox {
            padding: 4px 24px 4px 12px;
        }

        QSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 20px;
            height: 15px;
            border-left: 1px solid #1e293b;
            border-bottom: 1px solid #1e293b;
            border-top-right-radius: 5px;
            background-color: #0f172a;
        }

        QSpinBox::up-button:hover {
            background-color: #1e293b;
        }

        QSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 20px;
            height: 15px;
            border-left: 1px solid #1e293b;
            border-bottom-right-radius: 5px;
            background-color: #0f172a;
        }

        QSpinBox::down-button:hover {
            background-color: #1e293b;
        }

        QSpinBox::up-arrow {
            image: url(ARROW_UP_PATH);
            width: 10px;
            height: 10px;
        }

        QSpinBox::up-button:hover QSpinBox::up-arrow {
            image: url(ARROW_UP_HOVER_PATH);
        }

        QSpinBox::down-arrow {
            image: url(ARROW_DOWN_PATH);
            width: 10px;
            height: 10px;
        }

        QSpinBox::down-button:hover QSpinBox::down-arrow {
            image: url(ARROW_DOWN_HOVER_PATH);
        }

        QComboBox {
            padding: 4px 32px 4px 12px;
        }

        QComboBox::drop-down {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 30px;
            border-left: 1px solid #1e293b;
            border-top-right-radius: 5px;
            border-bottom-right-radius: 5px;
            background-color: transparent;
        }

        QComboBox::down-arrow {
            image: url(ARROW_DOWN_PATH);
            width: 12px;
            height: 12px;
        }

        QComboBox::drop-down:hover QComboBox::down-arrow {
            image: url(ARROW_DOWN_HOVER_PATH);
        }

        QComboBox QAbstractItemView {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            selection-background-color: #1e293b;
            selection-color: #f8fafc;
            color: #94a3b8;
            outline: 0px;
        }

        /* Buttons styling */
        QPushButton {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 6px;
            padding: 4px 16px;
            color: #f8fafc;
            font-weight: 500;
            font-size: 13px;
            min-height: 32px;
            max-height: 32px;
        }

        QPushButton:hover {
            background-color: #1e293b;
            border-color: #334155;
        }

        QPushButton:pressed {
            background-color: #0f172a;
        }

        QPushButton#btnPrimary {
            background-color: #2563eb;
            border: none;
            color: #ffffff;
        }

        QPushButton#btnPrimary:hover {
            background-color: #1d4ed8;
        }

        QPushButton#btnDanger {
            background-color: #7f1d1d;
            border: 1px solid #991b1b;
            color: #fca5a5;
        }

        QPushButton#btnDanger:hover {
            background-color: #991b1b;
            border-color: #b91c1c;
        }

        QFrame#iconPreviewBox {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 6px;
        }

        QLabel#commandPreview {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 6px;
            padding: 12px;
            font-family: monospace;
            color: #38bdf8;
            font-size: 12px;
        }
        """
        qss = qss.replace("ARROW_UP_PATH", arrow_up) \
                 .replace("ARROW_UP_HOVER_PATH", arrow_up_hover) \
                 .replace("ARROW_DOWN_PATH", arrow_down) \
                 .replace("ARROW_DOWN_HOVER_PATH", arrow_down_hover)
        self.setStyleSheet(qss)

    def load_webapps(self) -> None:
        """Scans the standard local application directory for webapps."""
        self.list_widget.clear()
        webapps = DesktopManager().load_all_entries(self.browsers)
        
        for app in webapps:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 60))
            item.setData(Qt.ItemDataRole.UserRole, app)
            
            self.list_widget.addItem(item)
            
            widget = WebappListItemWidget(app['name'], app['url'], app['icon'])
            self.list_widget.setItemWidget(item, widget)

    def filter_webapps(self) -> None:
        """Filters the webapp list according to text typed in the search bar."""
        query = self.search_bar.text().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            app_data = item.data(Qt.ItemDataRole.UserRole)
            
            if app_data:
                name_matches = query in app_data['name'].lower()
                url_matches = query in app_data['url'].lower()
                item.setHidden(not (name_matches or url_matches))

    def on_webapp_selected(self) -> None:
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

    def new_webapp(self) -> None:
        """Resets the form fields to default values for creating a new webapp."""
        self.list_widget.clearSelection()
        self.current_filepath = None
        self.custom_icon_path = None
        
        self.header_title.setText("Create New Webapp")
        
        # Block signals temporarily to prevent setting flags/previews during form reset
        self.input_name.blockSignals(True)
        self.input_url.blockSignals(True)
        self.combo_browser.blockSignals(True)
        self.spin_width.blockSignals(True)
        self.spin_height.blockSignals(True)
        self.input_icon.blockSignals(True)
        self.input_userdata.blockSignals(True)
        self.input_class.blockSignals(True)
        
        self.input_name.setText("")
        self.input_url.setText("")
        self.input_icon.setText("")
        self.input_userdata.setText("")
        self.input_class.setText("")
        
        if self.combo_browser.count() > 0:
            self.combo_browser.setCurrentIndex(0)
            
        self.is_modifying_userdata = False
        self.is_modifying_class = False
        
        self.input_name.blockSignals(False)
        self.input_url.blockSignals(False)
        self.combo_browser.blockSignals(False)
        self.spin_width.blockSignals(False)
        self.spin_height.blockSignals(False)
        self.input_icon.blockSignals(False)
        self.input_userdata.blockSignals(False)
        self.input_class.blockSignals(False)
        
        self.update_icon_preview("applications-internet")
        self.update_command_preview()
        
        self.btn_delete.setEnabled(False)
        self.input_name.setFocus()

    def on_name_changed(self) -> None:
        """Auto-completes fields like user-data-dir and window class as the user types the app name."""
        name = self.input_name.text()
        slug = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
        
        if not self.is_modifying_userdata:
            self.input_userdata.blockSignals(True)
            if slug:
                browser_cmd = self.combo_browser.currentData() or ""
                if "flatpak run" in browser_cmd:
                    parts = browser_cmd.split()
                    if len(parts) >= 3:
                        app_id = parts[2]
                    else:
                        app_id = "com.unknown.Browser"
                    user_data_base = os.path.expanduser(f"~/.var/app/{app_id}/config/webapps/")
                else:
                    user_data_base = DEFAULT_USER_DATA_BASE
                self.input_userdata.setText(os.path.join(user_data_base, slug))
            else:
                self.input_userdata.setText("")
            self.input_userdata.blockSignals(False)
                 
        if not self.is_modifying_class:
            self.input_class.blockSignals(True)
            self.input_class.setText(slug)
            self.input_class.blockSignals(False)
            
        # Also auto-update icon name if it was a default placeholder
        if self.input_icon.text() in ["applications-internet", ""] and slug:
            self.input_icon.setText(slug)
            
        self.update_command_preview()

    def on_browser_changed(self) -> None:
        """Triggered when the user changes the browser in the dropdown."""
        browser_cmd = self.combo_browser.currentData() or ""
        slug = re.sub(r'[^a-zA-Z0-9]', '_', self.input_name.text().lower())
        
        if not self.is_modifying_userdata:
            self.input_userdata.blockSignals(True)
            if slug:
                if "flatpak run" in browser_cmd:
                    parts = browser_cmd.split()
                    if len(parts) >= 3:
                        app_id = parts[2]
                    else:
                        app_id = "com.unknown.Browser"
                    user_data_base = os.path.expanduser(f"~/.var/app/{app_id}/config/webapps/")
                else:
                    user_data_base = DEFAULT_USER_DATA_BASE
                self.input_userdata.setText(os.path.join(user_data_base, slug))
            else:
                self.input_userdata.setText("")
            self.input_userdata.blockSignals(False)
            
        self.update_command_preview()

    def on_userdata_edited(self) -> None:
        self.is_modifying_userdata = True
        self.update_command_preview()

    def on_class_edited(self) -> None:
        self.is_modifying_class = True
        self.update_command_preview()

    def on_icon_input_changed(self) -> None:
        icon_text = self.input_icon.text().strip()
        self.update_icon_preview(icon_text)

    def select_custom_icon(self) -> None:
        """Opens a file dialog to choose a custom local image (PNG/SVG) for the app icon."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Webapp Icon", "",
            "Images (*.png *.svg *.jpg *.jpeg *.ico);;All Files (*)"
        )
        if file_path:
            self.custom_icon_path = file_path
            self.input_icon.setText(file_path)
            self.update_icon_preview(file_path)

    def update_icon_preview(self, icon_path_or_name: str) -> None:
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

    def get_built_command(self) -> str:
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

    def update_command_preview(self) -> None:
        """Renders the command preview label with the current form values."""
        self.lbl_cmd_preview.setText(self.get_built_command())

    def test_run(self) -> None:
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
            
        migrate_profile_if_needed(user_data)
            
        if "flatpak run" in browser_cmd:
            args = browser_cmd.split() + [
                f"--window-size={width},{height}",
                f"--class={wm_class}",
                f"--app={url}"
            ]
        else:
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

    def save_webapp(self) -> None:
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

        try:
            DesktopManager().create_entry(
                name=name,
                url=url,
                exec_line=exec_line,
                final_icon_value=final_icon_value,
                wm_class=wm_class,
                browser_cmd=browser_cmd,
                width=width,
                height=height,
                user_data=user_data,
                filepath=filepath
            )
            
            # Auto-generate KWin window rule to force correct icon on Wayland
            desktop_file_basename = os.path.splitext(os.path.basename(filepath))[0]
            KWinRuleManager.add_rule(name, url, browser_cmd, desktop_file_basename, width, height)
            
            QMessageBox.information(self, "Success", f"Webapp '{name}' saved successfully!")
            
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

    def delete_webapp(self) -> None:
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
                KWinRuleManager.remove_rule(desktop_file_basename)
                DesktopManager().delete_entry(self.current_filepath)
                
                QMessageBox.information(self, "Success", f"Webapp '{name}' deleted.")
                
                self.load_webapps()
                self.new_webapp()
            except Exception as e:
                QMessageBox.critical(self, "Error Deleting", f"Failed to delete the shortcut:\n{e}")

def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
