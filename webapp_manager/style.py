"""Oriental Brutalist Minimalist Theme for KDE Webapp Manager.
Follows the Art Guide Panda design system tokens:
- Canvas / Surface-0: #090a0f / #0c1015 (Deep mineral obsidian / matte finish)
- Panels / Cards / Surface-1: #14171f (Dark matte graphite)
- Interactive / Hover / Surface-2: #1c242c
- Text Primary: #dedfd7 (Stark off-white matte)
- Text Muted: #7e8790 (Industrial slate gray)
- Structural Borders: 1px solid rgba(222, 223, 215, 0.08)
- Signature Accent: #2563eb / #3b82f6 (Electric Cobalt Blue)
"""

DARK_THEME_QSS = """
/* Global Window & Surface */
QMainWindow {
    background-color: #090a0f;
    border: none;
}

QWidget {
    font-family: "Space Grotesk", "Inter", "Segoe UI", "Noto Sans", "Cantarell", sans-serif;
    color: #dedfd7;
}

QWidget#centralWidget {
    background-color: #090a0f;
    border: none;
}

QSplitter {
    background-color: #090a0f;
    border: none;
}

QSplitter::handle {
    background-color: rgba(222, 223, 215, 0.06);
    width: 1px;
}

QSplitter::handle:hover {
    background-color: #3b82f6;
}

/* Top Menu Bar */
QMenuBar {
    background-color: #0d1217;
    border-bottom: 1px solid rgba(222, 223, 215, 0.08);
    padding: 2px 8px;
    font-size: 12px;
}

QMenuBar::item {
    background: transparent;
    color: #7e8790;
    padding: 5px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected, QMenuBar::item:pressed {
    background-color: #1c242c;
    color: #dedfd7;
}

QMenu {
    background-color: #14171f;
    border: 1px solid rgba(222, 223, 215, 0.08);
    border-radius: 6px;
    padding: 4px;
    font-size: 12px;
}

QMenu::item {
    color: #dedfd7;
    padding: 6px 28px 6px 14px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: rgba(37, 99, 235, 0.18);
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: rgba(222, 223, 215, 0.08);
    margin: 4px 8px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

/* Sidebar Container */
QWidget#sidebarContainer {
    background-color: #0d1217;
    border-right: 1px solid rgba(222, 223, 215, 0.08);
}

/* Hanko Seal Badges (Oriental stamp - Cobalt & Vermilion) */
QLabel#hankoBadge, QLabel#hankoBadgeBlue {
    background-color: rgba(37, 99, 235, 0.12);
    border: 1px solid #2563eb;
    border-radius: 4px;
    color: #60a5fa;
    font-weight: 800;
    font-size: 11px;
    padding: 2px 6px;
    font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace;
}

QLabel#hankoBadgeRed, QLabel#hankoBadgeVermilion {
    background-color: rgba(230, 57, 70, 0.14);
    border: 1px solid #E63946;
    border-radius: 4px;
    color: #ff6b72;
    font-weight: 800;
    font-size: 11px;
    padding: 2px 6px;
    font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace;
}

QLabel#technicalTag {
    color: #7e8790;
    font-size: 10px;
    font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace;
    font-weight: 600;
    letter-spacing: 1px;
}

QLabel#crosshairDecor {
    color: rgba(222, 223, 215, 0.16);
    font-size: 11px;
    font-family: monospace;
    font-weight: 700;
    letter-spacing: 2px;
}

/* Translucent Data Pills & Corner Accents */
QWidget#statusPill {
    background-color: rgba(20, 23, 31, 0.85);
    border: 1px solid rgba(222, 223, 215, 0.08);
    border-radius: 12px;
}

QWidget#statusPill:hover {
    border-color: rgba(59, 130, 246, 0.30);
}

/* Search Bar styling */
QLineEdit#searchBar {
    background-color: #14171f;
    border: 1px solid rgba(222, 223, 215, 0.10);
    border-radius: 8px;
    padding: 8px 14px;
    margin: 8px 16px;
    color: #dedfd7;
    font-size: 12px;
}

QLineEdit#searchBar:focus {
    border: 1px solid #3b82f6;
    background-color: #171c26;
}

QLineEdit#searchBar::placeholder {
    color: #555e68;
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
    margin: 3px 0px;
    border: 1px solid transparent;
}

QListWidget#webappList::item:hover {
    background-color: rgba(37, 99, 235, 0.06);
    border: 1px solid rgba(59, 130, 246, 0.20);
}

QListWidget#webappList::item:selected {
    background-color: rgba(37, 99, 235, 0.14);
    border: 1px solid #2563eb;
}

/* ScrollBar styling */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: rgba(222, 223, 215, 0.10);
    min-height: 24px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(59, 130, 246, 0.40);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    background: none;
}

QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    background: none;
}

/* Main Editor Area */
QScrollArea#editorScroll {
    border: none;
    background-color: #090a0f;
}

QWidget#editorContainer {
    background-color: #090a0f;
}

/* Bento Cards (Modular Brutalist Blocks) */
QFrame.bentoCard {
    background-color: #14171f;
    border: 1px solid rgba(222, 223, 215, 0.08);
    border-radius: 12px;
    padding: 16px 20px;
}

QFrame.bentoCard:hover {
    border-color: rgba(222, 223, 215, 0.14);
}

QLabel {
    color: #dedfd7;
    font-size: 13px;
    background: transparent;
}

/* Display Titles (with dry terminal period) */
QLabel#titleLabel {
    font-size: 20px;
    font-weight: 800;
    color: #dedfd7;
    letter-spacing: -0.5px;
    padding-bottom: 4px;
}

QLabel#sectionTitle {
    font-size: 11px;
    font-weight: 800;
    color: #60a5fa;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace;
    margin-bottom: 8px;
}

/* Same height as the 40px fields so labels center on them, and a shared column width across cards */
QLabel#fieldLabel {
    color: #8a949e;
    font-size: 12px;
    font-weight: 600;
    font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace;
    min-height: 40px;
    min-width: 140px;
}

/* Form Inputs (40px total height: 38px content + 1px hairline borders) */
QLineEdit, QSpinBox, QComboBox {
    background-color: #0d1216;
    border: 1px solid rgba(222, 223, 215, 0.08);
    border-radius: 8px;
    color: #dedfd7;
    font-size: 13px;
    padding: 0px 12px;
    min-height: 38px;
    max-height: 38px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QLineEdit:hover, QSpinBox:hover, QComboBox:hover {
    border-color: rgba(255, 255, 255, 0.20);
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QComboBox:on {
    border-color: #3b82f6;
    background-color: #10161b;
}

QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {
    color: #4b5563;
    border-color: rgba(222, 223, 215, 0.04);
}

QLineEdit::placeholder {
    color: #4b5563;
}

/* QSpinBox: stacked chevrons inside the field border */
QSpinBox {
    padding-right: 34px;
}

QSpinBox::up-button, QSpinBox::down-button {
    subcontrol-origin: padding;
    width: 28px;
    height: 19px;
    border: none;
    border-left: 1px solid rgba(222, 223, 215, 0.08);
    background-color: transparent;
}

QSpinBox::up-button {
    subcontrol-position: top right;
    border-bottom: 1px solid rgba(222, 223, 215, 0.08);
    border-top-right-radius: 7px;
}

QSpinBox::down-button {
    subcontrol-position: bottom right;
    border-bottom-right-radius: 7px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #1c242c;
}

QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
    background-color: #141a1f;
}

QSpinBox::up-arrow, QSpinBox::down-arrow {
    width: 9px;
    height: 9px;
}

QSpinBox::up-arrow {
    image: url(ARROW_UP_PATH);
}

QSpinBox::up-button:hover QSpinBox::up-arrow {
    image: url(ARROW_UP_HOVER_PATH);
}

QSpinBox::down-arrow {
    image: url(ARROW_DOWN_PATH);
}

QSpinBox::down-button:hover QSpinBox::down-arrow {
    image: url(ARROW_DOWN_HOVER_PATH);
}

/* QComboBox: borderless chevron area, list-style popup */
QComboBox {
    padding-left: 14px;
    padding-right: 36px;
    combobox-popup: 0;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 36px;
    border: none;
    background-color: transparent;
}

QComboBox::down-arrow {
    image: url(ARROW_DOWN_PATH);
    width: 10px;
    height: 10px;
}

QComboBox:hover QComboBox::down-arrow, QComboBox:on QComboBox::down-arrow {
    image: url(ARROW_DOWN_HOVER_PATH);
}

QComboBox QAbstractItemView {
    background-color: #141a1f;
    border: 1px solid rgba(222, 223, 215, 0.12);
    border-radius: 8px;
    color: #dedfd7;
    outline: 0px;
    padding: 4px;
}

QComboBox QAbstractItemView::item {
    min-height: 32px;
    padding: 0px 10px;
    border-radius: 6px;
}

QComboBox QAbstractItemView::item:hover, QComboBox QAbstractItemView::item:selected {
    background-color: #1c242c;
    color: #ffffff;
}

/* CheckBox */
QCheckBox {
    color: #dedfd7;
    font-size: 13px;
    spacing: 8px;
    min-height: 40px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid rgba(222, 223, 215, 0.16);
    border-radius: 4px;
    background-color: #0b0e13;
}

QCheckBox::indicator:hover {
    border-color: #3b82f6;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #3b82f6;
    image: url(CHECK_ICON_PATH);
}

/* Buttons Styling */
QPushButton {
    background-color: #1c242c;
    border: 1px solid rgba(222, 223, 215, 0.10);
    border-radius: 6px;
    padding: 4px 18px;
    color: #dedfd7;
    font-weight: 600;
    font-size: 12px;
    min-height: 36px;
    max-height: 36px;
}

QPushButton:hover {
    background-color: #242f3a;
    border-color: rgba(222, 223, 215, 0.20);
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #171e25;
}

QPushButton:disabled {
    background-color: rgba(222, 223, 215, 0.02);
    border-color: rgba(222, 223, 215, 0.04);
    color: #4b5563;
}

/* Primary Button (Electric Cobalt Blue) */
QPushButton#btnPrimary {
    background-color: #2563eb;
    border: 1px solid #3b82f6;
    color: #ffffff;
    font-weight: 700;
    letter-spacing: 0.5px;
}

QPushButton#btnPrimary:hover {
    background-color: #3b82f6;
    border-color: #60a5fa;
}

QPushButton#btnPrimary:pressed {
    background-color: #1d4ed8;
}

/* Danger Button (Brutalist Red Accent) */
QPushButton#btnDanger {
    background-color: rgba(239, 68, 68, 0.10);
    border: 1px solid rgba(239, 68, 68, 0.35);
    color: #f87171;
    font-weight: 600;
}

QPushButton#btnDanger:hover {
    background-color: rgba(239, 68, 68, 0.20);
    border-color: rgba(239, 68, 68, 0.60);
    color: #fca5a5;
}

QPushButton#btnDanger:pressed {
    background-color: rgba(239, 68, 68, 0.28);
}

QPushButton#btnDanger:disabled {
    background-color: transparent;
    border-color: rgba(222, 223, 215, 0.04);
    color: #4b5563;
}

/* Clickable Icon Preview Button */
QPushButton#iconPreviewButton {
    background-color: #0d1216;
    border: 1px solid rgba(222, 223, 215, 0.08);
    border-radius: 8px;
    padding: 0px;
    min-height: 38px;
    max-height: 38px;
    min-width: 38px;
    max-width: 38px;
}

QPushButton#iconPreviewButton:hover {
    background-color: #1c242c;
    border: 1px solid rgba(255, 255, 255, 0.20);
}

/* Execution Command Terminal Box */
QWidget#commandContainer {
    background-color: #07090c;
    border: 1px solid rgba(222, 223, 215, 0.08);
    border-radius: 8px;
}

QLabel#commandPreview {
    background-color: transparent;
    border: none;
    font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace;
    color: #60a5fa;
    font-size: 11px;
    padding: 2px 0px;
}

QLabel#commandTerminalPrompt {
    color: #34d399;
    font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 0px;
}

/* Dialogs & Modals Styling */
QDialog, QMessageBox {
    background-color: #14171f;
    border: 1px solid rgba(222, 223, 215, 0.16);
    border-radius: 12px;
}

QMessageBox QLabel {
    color: #dedfd7;
    font-size: 13px;
    font-weight: 500;
    background: transparent;
    padding: 6px;
}

QDialogButtonBox {
    dialogbuttonbox-buttons-have-icons: 0;
    button-layout: 0;
}

QMessageBox QPushButton, QDialog QPushButton {
    background-color: #1c242c;
    border: 1px solid rgba(222, 223, 215, 0.14);
    border-radius: 6px;
    padding: 4px 16px;
    color: #dedfd7;
    font-weight: 600;
    font-size: 12px;
    min-height: 30px;
    max-height: 30px;
    min-width: 80px;
    margin: 4px;
}

QMessageBox QPushButton:hover, QDialog QPushButton:hover {
    background-color: #2563eb;
    border-color: #3b82f6;
    color: #ffffff;
}

QMessageBox QPushButton:pressed, QDialog QPushButton:pressed {
    background-color: #1d4ed8;
}

QMessageBox QPushButton:default, QDialog QPushButton:default {
    background-color: #2563eb;
    border-color: #3b82f6;
    color: #ffffff;
    font-weight: 700;
}

QMessageBox QPushButton:default:hover, QDialog QPushButton:default:hover {
    background-color: #3b82f6;
    border-color: #60a5fa;
}
"""
