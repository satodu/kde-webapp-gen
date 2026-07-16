import os
import sys
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QScrollArea,
    QHBoxLayout, QVBoxLayout
)
from PyQt6.QtGui import QIcon, QPixmap

from webapp_manager.utils import get_app_logo_pixmap
from webapp_manager.browser_detector import BrowserDetector
from webapp_manager.style import DARK_THEME_QSS
from webapp_manager.widgets.sidebar import SidebarPanel
from webapp_manager.widgets.editor import EditorPanel

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("KDE Webapp Manager")
        self.resize(920, 650)
        
        # Set window icon
        logo_pixmap = get_app_logo_pixmap()
        if not logo_pixmap.isNull():
            self.setWindowIcon(QIcon(logo_pixmap))
            
        self.browsers = BrowserDetector.detect_browsers()
        
        self.init_ui()
        self.apply_theme()

    def init_ui(self) -> None:
        # Central widget
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Content Layout (Horizontal Splitter)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Instantiate Sidebar
        self.sidebar = SidebarPanel(self.browsers, self)
        
        # Instantiate Editor and wrap in a Scroll Area
        self.editor = EditorPanel(self.browsers, self)
        
        editor_scroll = QScrollArea()
        editor_scroll.setObjectName("editorScroll")
        editor_scroll.setWidgetResizable(True)
        editor_scroll.setWidget(self.editor)
        
        # Add to splitter
        splitter.addWidget(self.sidebar)
        splitter.addWidget(editor_scroll)
        
        # Set initial layout proportions
        splitter.setSizes([320, 600])
        
        # Connect signals between panels to coordinate actions
        self.sidebar.webapp_selected.connect(self.editor.load_webapp)
        self.sidebar.new_webapp_requested.connect(self.editor.new_webapp)
        
        self.editor.webapp_saved.connect(self.sidebar.on_webapp_saved)
        self.editor.webapp_deleted.connect(self.sidebar.on_webapp_deleted)
        self.editor.webapp_changed.connect(self.sidebar.on_webapp_changed)

    def apply_theme(self) -> None:
        """Applies the custom, high-fidelity dark stylesheet to match KDE dark elements."""
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        arrow_up = os.path.join(pkg_dir, "arrow-up.png").replace(os.sep, '/')
        arrow_up_hover = os.path.join(pkg_dir, "arrow-up-hover.png").replace(os.sep, '/')
        arrow_down = os.path.join(pkg_dir, "arrow-down.png").replace(os.sep, '/')
        arrow_down_hover = os.path.join(pkg_dir, "arrow-down-hover.png").replace(os.sep, '/')

        qss = DARK_THEME_QSS.replace("ARROW_UP_PATH", arrow_up) \
                            .replace("ARROW_UP_HOVER_PATH", arrow_up_hover) \
                            .replace("ARROW_DOWN_PATH", arrow_down) \
                            .replace("ARROW_DOWN_HOVER_PATH", arrow_down_hover)
        self.setStyleSheet(qss)

def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
