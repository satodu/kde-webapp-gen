DARK_THEME_QSS = """
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

QPushButton:disabled {
    background-color: #0f172a;
    border-color: #1e293b;
    color: #475569;
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
