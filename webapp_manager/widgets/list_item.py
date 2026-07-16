import os
from typing import Optional
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtGui import QIcon, QPixmap
from webapp_manager.utils import get_rounded_pixmap

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
        self.name_label.setStyleSheet("font-weight: 600; font-size: 13px; color: #ffffff; background: transparent;")
        text_layout.addWidget(self.name_label)
        
        self.url_label = QLabel(url)
        self.url_label.setStyleSheet("font-size: 11px; color: #8c9c9e; background: transparent;")
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
        
        rounded = get_rounded_pixmap(pixmap, radius=20)
        self.icon_label.setPixmap(rounded)

    def update_text(self, name: str, url: str) -> None:
        self.name_label.setText(name)
        self.url_label.setText(url)
