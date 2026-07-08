import os
from typing import List, Tuple, Optional
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton
from webapp_manager.utils import get_app_logo_pixmap
from webapp_manager.desktop_manager import DesktopManager
from webapp_manager.models import Webapp
from webapp_manager.widgets.list_item import WebappListItemWidget

class SidebarPanel(QWidget):
    # Signals to communicate with MainWindow/Controller
    webapp_selected = pyqtSignal(object)
    new_webapp_requested = pyqtSignal()

    def __init__(self, browsers: List[Tuple[str, str]], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.browsers = browsers
        self.setObjectName("sidebarContainer")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(8)
        
        # Sidebar Header (Logo + Title)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 10, 15, 5)
        header_layout.setSpacing(10)
        
        lbl_logo = QLabel()
        logo_pixmap = get_app_logo_pixmap(28)
        if not logo_pixmap.isNull():
            lbl_logo.setPixmap(logo_pixmap)
        header_layout.addWidget(lbl_logo)
        
        lbl_title = QLabel("Webapps")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #f8fafc;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("searchBar")
        self.search_bar.setPlaceholderText("Search webapps...")
        self.search_bar.textChanged.connect(self.filter_webapps)
        layout.addWidget(self.search_bar)
        
        # Webapp List Widget
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("webappList")
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)
        
        # "+ New Webapp" Button
        self.btn_new = QPushButton("+ New Webapp")
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.clicked.connect(self.on_new_webapp_clicked)
        
        # Wrap button in layout to add margins
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(15, 5, 15, 10)
        btn_layout.addWidget(self.btn_new)
        layout.addLayout(btn_layout)

        self.load_webapps()

    def load_webapps(self) -> None:
        """Scans the standard local application directory for webapps, preserving any unsaved drafts in memory."""
        # Backup current drafts
        drafts = {}
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            app = item.data(Qt.ItemDataRole.UserRole)
            if app and app.is_dirty:
                key = app.filepath if app.filepath else app.name
                drafts[key] = app
                
        self.list_widget.clear()
        webapps = DesktopManager().load_all_entries(self.browsers)
        
        # Merge backed-up drafts back into the loaded list
        new_drafts = [app for app in drafts.values() if not app._saved_memento]
        
        all_apps = []
        for app in webapps:
            if app.filepath in drafts:
                all_apps.append(drafts[app.filepath])
            else:
                all_apps.append(app)
                
        all_apps.extend(new_drafts)
        all_apps.sort(key=lambda x: x.name.lower())
        
        for app in all_apps:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 60))
            item.setData(Qt.ItemDataRole.UserRole, app)
            
            self.list_widget.addItem(item)
            
            display_name = app.name
            if app.is_dirty:
                display_name += " *"
                
            widget = WebappListItemWidget(display_name, app.url, app.icon)
            self.list_widget.setItemWidget(item, widget)

    def filter_webapps(self) -> None:
        """Filters the webapp list according to text typed in the search bar."""
        query = self.search_bar.text().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            app_data = item.data(Qt.ItemDataRole.UserRole)
            
            if app_data:
                name_matches = query in app_data.name.lower()
                url_matches = query in app_data.url.lower()
                item.setHidden(not (name_matches or url_matches))

    def on_selection_changed(self) -> None:
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            app = selected_items[0].data(Qt.ItemDataRole.UserRole)
            if app:
                self.webapp_selected.emit(app)

    def on_new_webapp_clicked(self) -> None:
        self.list_widget.blockSignals(True)
        self.list_widget.setCurrentItem(None)
        self.list_widget.clearSelection()
        self.list_widget.blockSignals(False)
        self.new_webapp_requested.emit()

    def on_webapp_saved(self, webapp: Webapp) -> None:
        self.load_webapps()
        # Find and select the item we just saved
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            app_data = item.data(Qt.ItemDataRole.UserRole)
            if app_data and app_data.filepath == webapp.filepath:
                # Block signals temporarily to prevent redundant selection triggering
                self.list_widget.blockSignals(True)
                self.list_widget.setCurrentItem(item)
                self.list_widget.blockSignals(False)
                break

    def on_webapp_deleted(self) -> None:
        self.load_webapps()
        self.on_new_webapp_clicked()

    def on_webapp_changed(self, webapp: Webapp) -> None:
        """Called in real-time when the active webapp is edited in the form to update visual draft status."""
        current_item = self.list_widget.currentItem()
        if not current_item and webapp.name:
            # It's a new unsaved webapp draft! Let's add it to the list widget so it shows up.
            current_item = QListWidgetItem()
            current_item.setSizeHint(QSize(0, 60))
            current_item.setData(Qt.ItemDataRole.UserRole, webapp)
            
            # Temporarily block signals to avoid selecting the item and overwriting the inputs we are editing
            self.list_widget.blockSignals(True)
            self.list_widget.addItem(current_item)
            self.list_widget.setCurrentItem(current_item)
            self.list_widget.blockSignals(False)
            
            widget = WebappListItemWidget(webapp.name + " *", webapp.url, webapp.icon)
            self.list_widget.setItemWidget(current_item, widget)
        elif current_item:
            # We want to update the displayed list widget item text to indicate draft status
            widget = self.list_widget.itemWidget(current_item)
            if widget and isinstance(widget, WebappListItemWidget):
                display_name = webapp.name
                if webapp.is_dirty:
                    display_name += " *"
                widget.update_text(display_name, webapp.url)
