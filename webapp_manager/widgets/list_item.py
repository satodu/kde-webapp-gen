import os
from typing import Optional
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtGui import QIcon, QPixmap
from webapp_manager.utils import get_rounded_pixmap

class WebappListItemWidget(QWidget):
    """Custom widget for webapp items in the sidebar list with oriental brutalist styling."""
    def __init__(self, name: str, url: str, icon_path_or_name: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("webappListItemWidget")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)
        
        # Rounded technical icon container
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setStyleSheet("background-color: #0b0e13; border: 1px solid rgba(222, 223, 215, 0.08); border-radius: 8px;")
        layout.addWidget(self.icon_label)
        
        # Text block
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        
        name_container = QHBoxLayout()
        name_container.setContentsMargins(0, 0, 0, 0)
        name_container.setSpacing(6)
        
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-weight: 700; font-size: 13px; color: #dedfd7; background: transparent;")
        name_container.addWidget(self.name_label)
        name_container.addStretch()
        text_layout.addLayout(name_container)
        
        display_url = url.replace("https://", "").replace("http://", "")
        if len(display_url) > 34:
            display_url = display_url[:32] + "..."
        self.url_label = QLabel(display_url)
        self.url_label.setStyleSheet("font-family: 'JetBrains Mono', 'DejaVu Sans Mono', monospace; font-size: 10px; color: #7e8790; background: transparent;")
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
        display_url = url.replace("https://", "").replace("http://", "")
        if len(display_url) > 34:
            display_url = display_url[:32] + "..."
        self.url_label.setText(display_url)
