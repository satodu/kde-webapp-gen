import os
from typing import List, Tuple, Optional
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QFrame
)
from webapp_manager.desktop_manager import DesktopManager
from webapp_manager.models import Webapp
from webapp_manager.widgets.list_item import WebappListItemWidget
from webapp_manager.widgets.decorations import HankoBadge, StatusIndicatorPill, TechnicalCrosshairs

class SidebarPanel(QWidget):
    # Signals to communicate with MainWindow/Controller
    webapp_selected = pyqtSignal(object)
    new_webapp_requested = pyqtSignal()

    def __init__(self, browsers: List[Tuple[str, str]], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.browsers = browsers
        self.setObjectName("sidebarContainer")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(10)
        
        # --- SIDEBAR HEADER (Oriental Brutalism) ---
        header_container = QWidget()
        header_vbox = QVBoxLayout(header_container)
        header_vbox.setContentsMargins(18, 4, 18, 6)
        header_vbox.setSpacing(6)
        
        # Row 1: Hanko Seal + Title + Crosshairs
        header_top_row = QHBoxLayout()
        header_top_row.setContentsMargins(0, 0, 0, 0)
        header_top_row.setSpacing(8)
        
        # Hanko Seal Badge [ 網 ] (Electric Cobalt Accent)
        hanko_stamp = HankoBadge("網", style_variant="blue")
        hanko_stamp.setToolTip("KDE Webapp Manager // Oriental Brutalism")
        header_top_row.addWidget(hanko_stamp)
        
        lbl_title = QLabel("WEBAPPS.")
        lbl_title.setStyleSheet("font-weight: 800; font-size: 15px; color: #dedfd7; letter-spacing: -0.3px;")
        header_top_row.addWidget(lbl_title)
        
        header_top_row.addStretch()
        
        # Technical crosshairs
        crosshairs = TechnicalCrosshairs(3)
        header_top_row.addWidget(crosshairs)
        
        header_vbox.addLayout(header_top_row)
        
        # Row 2: Technical Subtitle Tag & Status Pill
        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(8)
        
        tech_meta = QLabel("SYS.KATALOG // 01")
        tech_meta.setObjectName("technicalTag")
        row2.addWidget(tech_meta)
        row2.addStretch()
        
        status_pill = StatusIndicatorPill("SYS.READY", active=True)
        row2.addWidget(status_pill)
        
        header_vbox.addLayout(row2)
        
        layout.addWidget(header_container)
        
        # Thin hairline separator
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(222, 223, 215, 0.06); border: none; margin: 0px 18px;")
        layout.addWidget(separator)
        
        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("searchBar")
        self.search_bar.setPlaceholderText("BUSCAR WEBAPP...")
        self.search_bar.textChanged.connect(self.filter_webapps)
        layout.addWidget(self.search_bar)
        
        # Webapp List Widget
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("webappList")
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)
        
        # Bottom Button: "+ NOVO WEBAPP."
        self.btn_new = QPushButton("+ NOVO WEBAPP.")
        self.btn_new.setObjectName("btnPrimary")
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.clicked.connect(self.on_new_webapp_clicked)
        
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(16, 4, 16, 4)
        btn_layout.addWidget(self.btn_new)
        layout.addLayout(btn_layout)

        self.load_webapps()

    def load_webapps(self) -> None:
        """Scans the standard local application directory for webapps, preserving any unsaved drafts in memory."""
        drafts = {}
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            app = item.data(Qt.ItemDataRole.UserRole)
            if app and app.is_dirty:
                key = app.filepath if app.filepath else app.name
                drafts[key] = app
                
        self.list_widget.clear()
        webapps = DesktopManager().load_all_entries(self.browsers)
        
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
            item.setSizeHint(QSize(0, 62))
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
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            app_data = item.data(Qt.ItemDataRole.UserRole)
            if app_data and app_data.filepath == webapp.filepath:
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
            current_item = QListWidgetItem()
            current_item.setSizeHint(QSize(0, 62))
            current_item.setData(Qt.ItemDataRole.UserRole, webapp)
            
            self.list_widget.blockSignals(True)
            self.list_widget.addItem(current_item)
            self.list_widget.setCurrentItem(current_item)
            self.list_widget.blockSignals(False)
            
            widget = WebappListItemWidget(webapp.name + " *", webapp.url, webapp.icon)
            self.list_widget.setItemWidget(current_item, widget)
        elif current_item:
            widget = self.list_widget.itemWidget(current_item)
            if widget and isinstance(widget, WebappListItemWidget):
                display_name = webapp.name
                if webapp.is_dirty:
                    display_name += " *"
                widget.update_text(display_name, webapp.url)
