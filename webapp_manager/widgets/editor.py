import os
import re
import shutil
import subprocess
import shlex
from typing import List, Tuple, Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QSpinBox, QComboBox,
    QPushButton, QLabel, QFileDialog, QMessageBox, QFrame, QScrollArea
)
from PyQt6.QtGui import QIcon, QPixmap
from webapp_manager.constants import APPLICATIONS_DIR, ICONS_DIR, DEFAULT_USER_DATA_BASE
from webapp_manager.utils import get_rounded_pixmap, migrate_profile_if_needed
from webapp_manager.desktop_manager import DesktopManager
from webapp_manager.kwin_manager import KWinRuleManager
from webapp_manager.models import Webapp

class EditorPanel(QWidget):
    # Signals to communicate with MainWindow/Sidebar
    webapp_saved = pyqtSignal(object)
    webapp_deleted = pyqtSignal()
    webapp_changed = pyqtSignal(object)

    def __init__(self, browsers: List[Tuple[str, str]], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.browsers = browsers
        
        self.current_webapp: Optional[Webapp] = None
        self.current_filepath: Optional[str] = None
        self.custom_icon_path: Optional[str] = None
        self.is_modifying_userdata: bool = False
        self.is_modifying_class: bool = False
        
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        # Header / Title
        self.header_title = QLabel("Create New Webapp")
        self.header_title.setObjectName("titleLabel")
        layout.addWidget(self.header_title)
        
        # --- FORM AREA ---
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setSpacing(12)
        
        # Webapp Name
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("e.g. WhatsApp, Netflix")
        self.input_name.textChanged.connect(self.on_name_changed)
        form_layout.addRow("App Name:", self.input_name)
        
        # URL
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("https://web.whatsapp.com")
        self.input_url.textChanged.connect(self.update_command_preview)
        form_layout.addRow("Site URL:", self.input_url)
        
        # Browser Selection
        self.combo_browser = QComboBox()
        for b_name, b_cmd in self.browsers:
            self.combo_browser.addItem(b_name, b_cmd)
        self.combo_browser.currentIndexChanged.connect(self.on_browser_changed)
        form_layout.addRow("Launch Browser:", self.combo_browser)
        
        # Window Dimensions (Horizontal Layout)
        dim_layout = QHBoxLayout()
        dim_layout.setSpacing(8)
        
        self.spin_width = QSpinBox()
        self.spin_width.setRange(100, 10000)
        self.spin_width.setValue(1024)
        self.spin_width.valueChanged.connect(self.update_command_preview)
        
        self.spin_height = QSpinBox()
        self.spin_height.setRange(100, 10000)
        self.spin_height.setValue(768)
        self.spin_height.valueChanged.connect(self.update_command_preview)
        
        dim_layout.addWidget(self.spin_width)
        dim_layout.addWidget(QLabel("x"))
        dim_layout.addWidget(self.spin_height)
        dim_layout.addStretch()
        
        form_layout.addRow("Window Size:", dim_layout)
        
        # Icon Section
        icon_field_layout = QHBoxLayout()
        icon_field_layout.setSpacing(10)
        
        self.input_icon = QLineEdit()
        self.input_icon.setPlaceholderText("applications-internet or full path")
        self.input_icon.textChanged.connect(self.on_icon_input_changed)
        icon_field_layout.addWidget(self.input_icon)
        
        self.btn_select_icon = QPushButton("Select Image...")
        self.btn_select_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_icon.clicked.connect(self.select_custom_icon)
        icon_field_layout.addWidget(self.btn_select_icon)
        
        form_layout.addRow("App Icon:", icon_field_layout)
        
        # Icon Thumbnail Preview Box
        icon_preview_layout = QHBoxLayout()
        self.icon_preview_frame = QFrame()
        self.icon_preview_frame.setObjectName("iconPreviewBox")
        self.icon_preview_frame.setFixedSize(50, 50)
        
        ip_frame_layout = QVBoxLayout(self.icon_preview_frame)
        ip_frame_layout.setContentsMargins(0, 0, 0, 0)
        ip_frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_icon_preview = QLabel()
        self.lbl_icon_preview.setFixedSize(48, 48)
        ip_frame_layout.addWidget(self.lbl_icon_preview)
        
        icon_preview_layout.addWidget(self.icon_preview_frame)
        icon_preview_layout.addStretch()
        form_layout.addRow("", icon_preview_layout)
        
        layout.addLayout(form_layout)
        
        # Separator / Section title
        adv_title = QLabel("Advanced Options (Auto-generated)")
        adv_title.setObjectName("sectionTitle")
        layout.addWidget(adv_title)
        
        # Advanced Form Settings
        adv_form_layout = QFormLayout()
        adv_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        adv_form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        adv_form_layout.setSpacing(12)
        
        # Isolated profile directory
        self.input_userdata = QLineEdit()
        self.input_userdata.setPlaceholderText("Calculated automatically")
        self.input_userdata.textChanged.connect(self.on_userdata_edited)
        adv_form_layout.addRow("Profile Path:", self.input_userdata)
        
        # Wayland App ID / WM_CLASS
        self.input_class = QLineEdit()
        self.input_class.setPlaceholderText("Calculated automatically")
        self.input_class.textChanged.connect(self.on_class_edited)
        adv_form_layout.addRow("Window Class:", self.input_class)
        
        layout.addLayout(adv_form_layout)
        
        # Executable Preview Section
        cmd_title = QLabel("Execution Command Preview")
        cmd_title.setObjectName("sectionTitle")
        layout.addWidget(cmd_title)
        
        self.lbl_cmd_preview = QLabel()
        self.lbl_cmd_preview.setObjectName("commandPreview")
        self.lbl_cmd_preview.setWordWrap(True)
        layout.addWidget(self.lbl_cmd_preview)
        
        # --- ACTION BUTTONS BAR ---
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
        
        self.btn_discard = QPushButton("Discard Changes")
        self.btn_discard.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_discard.clicked.connect(self.discard_changes)
        self.btn_discard.setEnabled(False)
        action_layout.addWidget(self.btn_discard)
        
        action_layout.addStretch()
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_webapp)
        self.btn_delete.setEnabled(False)
        action_layout.addWidget(self.btn_delete)
        
        layout.addLayout(action_layout)
        layout.addStretch()
        
        self.new_webapp()

    def load_webapp(self, webapp: Webapp) -> None:
        """Loads a webapp's configurations into the fields."""
        self.current_webapp = webapp
        self.current_filepath = webapp.filepath
        self.header_title.setText(f"Edit: {webapp.name}")
        
        # Block signals temporarily to prevent loop updates
        self.input_name.blockSignals(True)
        self.input_url.blockSignals(True)
        self.combo_browser.blockSignals(True)
        self.spin_width.blockSignals(True)
        self.spin_height.blockSignals(True)
        self.input_icon.blockSignals(True)
        self.input_userdata.blockSignals(True)
        self.input_class.blockSignals(True)
        
        self.input_name.setText(webapp.name)
        self.input_url.setText(webapp.url)
        
        idx = self.combo_browser.findData(webapp.browser)
        if idx >= 0:
            self.combo_browser.setCurrentIndex(idx)
            
        self.spin_width.setValue(webapp.width)
        self.spin_height.setValue(webapp.height)
        self.input_icon.setText(webapp.icon)
        
        expanded_ud = os.path.expandvars(os.path.expanduser(webapp.user_data_dir))
        self.input_userdata.setText(expanded_ud)
        self.input_class.setText(webapp.wm_class)
        
        self.custom_icon_path = webapp.icon if os.path.exists(webapp.icon) else None
        
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
        
        self.update_icon_preview(webapp.icon)
        self.update_command_preview()
        
        self.btn_delete.setEnabled(True)
        self.btn_discard.setEnabled(webapp.is_dirty)

    def new_webapp(self) -> None:
        """Resets the editor layout back to a blank new webapp template."""
        self.current_filepath = None
        self.custom_icon_path = None
        self.current_webapp = Webapp(name="", url="", browser="", width=1024, height=768)
        
        self.header_title.setText("Create New Webapp")
        
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
        
        self.update_icon_preview("")
        self.update_command_preview()
        
        self.btn_delete.setEnabled(False)
        self.btn_discard.setEnabled(False)

    def on_name_changed(self) -> None:
        name = self.input_name.text()
        slug = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
        
        if not self.is_modifying_userdata:
            self.input_userdata.blockSignals(True)
            if slug:
                browser_cmd = self.combo_browser.currentData() or ""
                if "flatpak run" in browser_cmd:
                    parts = browser_cmd.split()
                    app_id = parts[2] if len(parts) >= 3 else "com.unknown.Browser"
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
            
        if self.input_icon.text() in ["applications-internet", ""] and slug:
            self.input_icon.setText(slug)
            
        self.update_command_preview()

    def on_browser_changed(self) -> None:
        browser_cmd = self.combo_browser.currentData() or ""
        slug = re.sub(r'[^a-zA-Z0-9]', '_', self.input_name.text().lower())
        
        if not self.is_modifying_userdata:
            self.input_userdata.blockSignals(True)
            if slug:
                if "flatpak run" in browser_cmd:
                    parts = browser_cmd.split()
                    app_id = parts[2] if len(parts) >= 3 else "com.unknown.Browser"
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
        self.sync_webapp_from_fields()

    def select_custom_icon(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Webapp Icon", "",
            "Images (*.png *.svg *.jpg *.jpeg *.ico);;All Files (*)"
        )
        if file_path:
            self.custom_icon_path = file_path
            self.input_icon.setText(file_path)
            self.update_icon_preview(file_path)

    def update_icon_preview(self, icon_path_or_name: str) -> None:
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
        browser_cmd = self.combo_browser.currentData() or "google-chrome-stable"
        width = self.spin_width.value()
        height = self.spin_height.value()
        url = self.input_url.text().strip() or "https://..."
        user_data = self.input_userdata.text().strip()
        wm_class = self.input_class.text().strip()
        
        temp_app = Webapp(
            name="",
            url=url,
            browser=browser_cmd,
            width=width,
            height=height,
            user_data_dir=user_data,
            wm_class=wm_class
        )
        return temp_app.exec_line

    def update_command_preview(self) -> None:
        self.lbl_cmd_preview.setText(self.get_built_command())
        self.sync_webapp_from_fields()

    def sync_webapp_from_fields(self) -> None:
        if self.input_name.signalsBlocked():
            return
            
        if not self.current_webapp:
            return
            
        self.current_webapp.name = self.input_name.text().strip()
        self.current_webapp.url = self.input_url.text().strip()
        self.current_webapp.browser = self.combo_browser.currentData() or ""
        self.current_webapp.width = self.spin_width.value()
        self.current_webapp.height = self.spin_height.value()
        self.current_webapp.user_data_dir = self.input_userdata.text().strip()
        self.current_webapp.wm_class = self.input_class.text().strip()
        self.current_webapp.icon = self.input_icon.text().strip()
        
        self.webapp_changed.emit(self.current_webapp)
        self.btn_discard.setEnabled(self.current_webapp.is_dirty)

    def discard_changes(self) -> None:
        if not self.current_webapp:
            return
            
        if self.current_webapp._saved_memento:
            self.current_webapp.restore(self.current_webapp._saved_memento)
            self.load_webapp(self.current_webapp)
        else:
            self.new_webapp()
            self.webapp_deleted.emit()

    def test_run(self) -> None:
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
        
        temp_app = Webapp(
            name="",
            url=url,
            browser=browser_cmd,
            width=width,
            height=height,
            user_data_dir=user_data,
            wm_class=wm_class
        )
        
        try:
            args = shlex.split(temp_app.exec_line)
            subprocess.Popen(args, start_new_session=True)
        except Exception as e:
            QMessageBox.critical(self, "Error Launching", f"Failed to execute browser:\n{e}")

    def save_webapp(self) -> None:
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
            ext = os.path.splitext(self.custom_icon_path)[1] or ".png"
            dest_name = f"webapp_{app_slug}{ext}"
            dest_path = os.path.join(ICONS_DIR, dest_name)
            
            try:
                shutil.copy2(self.custom_icon_path, dest_path)
                final_icon_value = dest_path
            except Exception as e:
                print(f"Error copying icon: {e}")

        # Ensure self.current_webapp exists
        if not self.current_webapp:
            self.current_webapp = Webapp(
                name=name,
                url=url,
                browser=browser_cmd,
                width=width,
                height=height,
                user_data_dir=user_data,
                wm_class=wm_class,
                icon=final_icon_value,
                filepath=self.current_filepath or ""
            )
            
        if not self.current_filepath:
            app_slug = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
            self.current_webapp.filepath = os.path.join(APPLICATIONS_DIR, f"webapp_{app_slug}.desktop")
        else:
            self.current_webapp.filepath = self.current_filepath

        self.current_webapp.icon = final_icon_value

        try:
            DesktopManager().create_entry(self.current_webapp)
            KWinRuleManager.add_rule(self.current_webapp)
            
            QMessageBox.information(self, "Success", f"Webapp '{name}' saved successfully!")
            
            self.webapp_saved.emit(self.current_webapp)
            
            # Reload fields
            self.load_webapp(self.current_webapp)
        except Exception as e:
            QMessageBox.critical(self, "Error Saving", f"Failed to save .desktop file:\n{e}")

    def delete_webapp(self) -> None:
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
                if self.current_webapp and self.current_webapp.icon and os.path.exists(self.current_webapp.icon) and ICONS_DIR in self.current_webapp.icon:
                    os.remove(self.current_webapp.icon)
                        
                desktop_file_basename = os.path.splitext(os.path.basename(self.current_filepath))[0]
                KWinRuleManager.remove_rule(desktop_file_basename)
                DesktopManager().delete_entry(self.current_filepath)
                
                QMessageBox.information(self, "Success", f"Webapp '{name}' deleted.")
                
                self.new_webapp()
                self.webapp_deleted.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error Deleting", f"Failed to delete the shortcut:\n{e}")
