DARK_THEME_QSS = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(10, 24, 38, 0.42), stop:0.5 rgba(6, 14, 22, 0.58), stop:1 rgba(2, 4, 6, 0.72));
    border: none;
}

QWidget#centralWidget {
    background-color: transparent;
    border: none;
}

QSplitter {
    border: none;
}

QScrollArea {
    border: none;
}

QSplitter::handle {
    background-color: rgba(255, 255, 255, 0.04);
    width: 1px;
}

/* Sidebar Container */
QWidget#sidebarContainer {
    background-color: rgba(0, 0, 0, 0.15);
    border-right: 1px solid rgba(255, 255, 255, 0.03);
}

/* Search Bar styling */
QLineEdit#searchBar {
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 6px 12px;
    margin: 10px 15px;
    color: #e0f2f1;
    font-size: 13px;
}

QLineEdit#searchBar:focus {
    border-color: #1d99f3;
    background-color: rgba(255, 255, 255, 0.07);
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
    border-radius: 8px;
    margin: 4px 0px;
    border: 1px solid transparent;
}

QListWidget#webappList::item:hover {
    background-color: rgba(29, 153, 243, 0.04);
    border-color: rgba(29, 153, 243, 0.12);
}

QListWidget#webappList::item:selected {
    background-color: rgba(29, 153, 243, 0.12);
    border-color: rgba(29, 153, 243, 0.35);
}

/* ScrollBar styling */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.08);
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.15);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    background: none;
}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    background: none;
}

/* Main Editor area scroll wrapper */
QScrollArea#editorScroll {
    border: none;
    background-color: transparent;
}

QWidget#editorContainer {
    background-color: transparent;
}

QLabel {
    color: #8c9c9e;
    font-size: 13px;
    background: transparent;
}

QLabel#titleLabel {
    font-size: 20px;
    font-weight: 600;
    color: #ffffff;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

QLabel#sectionTitle {
    font-size: 14px;
    font-weight: 600;
    color: #1d99f3;
    margin-top: 15px;
    margin-bottom: 5px;
}

QLineEdit, QSpinBox, QComboBox {
    background-color: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #ffffff;
    font-size: 13px;
    min-height: 34px;
    max-height: 34px;
}

QLineEdit {
    padding: 4px 12px;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #1d99f3;
    background-color: rgba(0, 0, 0, 0.35);
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
    border-left: 1px solid rgba(255, 255, 255, 0.08);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    border-top-right-radius: 7px;
    background-color: rgba(0, 0, 0, 0.15);
}

QSpinBox::up-button:hover {
    background-color: rgba(255, 255, 255, 0.08);
}

QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    height: 15px;
    border-left: 1px solid rgba(255, 255, 255, 0.08);
    border-bottom-right-radius: 7px;
    background-color: rgba(0, 0, 0, 0.15);
}

QSpinBox::down-button:hover {
    background-color: rgba(255, 255, 255, 0.08);
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
    border-left: 1px solid rgba(255, 255, 255, 0.08);
    border-top-right-radius: 7px;
    border-bottom-right-radius: 7px;
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
    background-color: #0e1e20;
    border: 1px solid rgba(255, 255, 255, 0.08);
    selection-background-color: rgba(29, 153, 243, 0.15);
    selection-color: #ffffff;
    color: #8c9c9e;
    outline: 0px;
}

/* Buttons styling */
QPushButton {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 4px 16px;
    color: #e0f2f1;
    font-weight: 500;
    font-size: 13px;
    min-height: 34px;
    max-height: 34px;
}

QPushButton:disabled {
    background-color: rgba(255, 255, 255, 0.01);
    border-color: rgba(255, 255, 255, 0.03);
    color: #4a5456;
}

QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.15);
}

QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.02);
}

QPushButton#btnPrimary {
    background-color: #154d97;
    border: none;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#btnPrimary:hover {
    background-color: #1d63c4;
}

QPushButton#btnDanger {
    background-color: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #fca5a5;
}

QPushButton#btnDanger:hover {
    background-color: rgba(239, 68, 68, 0.25);
    border-color: rgba(239, 68, 68, 0.6);
}

/* Clickable Icon Button Preview */
QPushButton#iconPreviewButton {
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 0px;
    min-height: 52px;
    max-height: 52px;
    min-width: 52px;
    max-width: 52px;
}

QPushButton#iconPreviewButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border-color: #1d99f3;
}

QLabel#commandPreview {
    background-color: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 12px;
    font-family: monospace;
    color: #00e676;
    font-size: 12px;
}
"""
