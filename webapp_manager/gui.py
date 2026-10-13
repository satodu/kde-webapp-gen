import os
import sys
from typing import Optional

from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QUrl, QSettings, QTranslator, QLocale, QLibraryInfo,
    qVersion, PYQT_VERSION_STR
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QScrollArea, QMenuBar,
    QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QAction, QActionGroup, QKeySequence, QDesktopServices

from webapp_manager import i18n
from webapp_manager.i18n import tr
from webapp_manager.constants import APP_NAME, APP_VERSION, APP_AUTHOR, APP_AUTHOR_URL, APP_REPO_URL
from webapp_manager.utils import get_app_logo_pixmap
from webapp_manager.browser_detector import BrowserDetector
from webapp_manager.style import DARK_THEME_QSS
from webapp_manager.widgets.sidebar import SidebarPanel
from webapp_manager.widgets.editor import EditorPanel

SETTINGS_LANGUAGE_KEY = "language"
_qt_translator: Optional[QTranslator] = None


def get_settings() -> QSettings:
    return QSettings("kde-webapp-manager", "kde-webapp-manager")


def apply_qt_translation(lang: str) -> None:
    """Translates Qt's own widgets (standard dialog buttons, file dialogs) to match the app language."""
    global _qt_translator
    app = QApplication.instance()
    if app is None:
        return
    if _qt_translator is not None:
        app.removeTranslator(_qt_translator)
        _qt_translator = None
    if lang == i18n.DEFAULT_LANGUAGE:
        return
    translator = QTranslator(app)
    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if translator.load(QLocale(lang), "qtbase", "_", path):
        app.installTranslator(translator)
        _qt_translator = translator


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("KDE WEBAPP MANAGER.")
        self.resize(980, 680)
        
        # Set window icon
        logo_pixmap = get_app_logo_pixmap()
        if not logo_pixmap.isNull():
            self.setWindowIcon(QIcon(logo_pixmap))
            
        self.browsers = BrowserDetector.detect_browsers()
        
        self.init_ui()
        self.apply_theme()
        self.migrate_existing_webapps()

    def migrate_existing_webapps(self) -> None:
        """Migrates all existing webapps to use the new native Wayland/X11 icon forcing system."""
        try:
            from webapp_manager.desktop_manager import DesktopManager
            from webapp_manager.kwin_manager import KWinRuleManager
            import configparser
            
            webapps = DesktopManager().load_all_entries(self.browsers)
            updated_any = False
            kwinrules_path = os.path.expanduser("~/.config/kwinrulesrc")
            
            for app in webapps:
                if not app.isolated_profile and not app.profile_directory:
                    app.profile_directory = BrowserDetector.detect_last_used_profile(app.browser)
                real_wmclass = app.get_real_wm_class()
                
                # Check .desktop file StartupWMClass
                desktop_outdated = True
                if os.path.exists(app.filepath):
                    parser = configparser.ConfigParser(interpolation=None)
                    parser.optionxform = str
                    parser.read(app.filepath)
                    current_wmclass = parser.get('Desktop Entry', 'StartupWMClass', fallback='')
                    current_profile = parser.get('Desktop Entry', 'X-KDE-Webapp-Profile', fallback='')
                    if current_wmclass == real_wmclass and current_profile == app.profile_directory:
                        desktop_outdated = False
                        
                # Check KWin rule
                rule_outdated = True
                if os.path.exists(kwinrules_path):
                    kwin_config = configparser.ConfigParser(interpolation=None)
                    kwin_config.optionxform = str
                    kwin_config.read(kwinrules_path)
                    desktop_file_basename = os.path.splitext(os.path.basename(app.filepath))[0]
                    main_prefix, _ = app.get_browser_prefixes()
                    full_wmclass = f"{main_prefix} {real_wmclass}"
                    for section in kwin_config.sections():
                        if section == 'General':
                            continue
                        if kwin_config.get(section, 'desktopfile', fallback='') == desktop_file_basename:
                            if kwin_config.get(section, 'wmclasscomplete', fallback='') == 'true' and \
                               kwin_config.get(section, 'wmclass', fallback='') == full_wmclass:
                                rule_outdated = False
                            break
                            
                if desktop_outdated or rule_outdated:
                    print(f"Migrating/Updating webapp '{app.name}' desktop entry and KWin rules...")
                    DesktopManager().create_entry(app)
                    KWinRuleManager.add_rule(app)
                    updated_any = True
                    
            if updated_any:
                print("Migration of webapps complete.")
        except Exception as e:
            print(f"Error during webapps migration: {e}")

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
        editor_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        editor_scroll.setWidget(self.editor)
        
        # Add to splitter
        splitter.addWidget(self.sidebar)
        splitter.addWidget(editor_scroll)
        
        # Set initial layout proportions (generous spacing / Ma concept)
        splitter.setSizes([310, 670])
        
        # Connect signals between panels to coordinate actions
        self.sidebar.webapp_selected.connect(self.editor.load_webapp)
        self.sidebar.new_webapp_requested.connect(self.editor.new_webapp)
        
        self.editor.webapp_saved.connect(self.sidebar.on_webapp_saved)
        self.editor.webapp_deleted.connect(self.sidebar.on_webapp_deleted)
        self.editor.webapp_changed.connect(self.sidebar.on_webapp_changed)

        self.init_menu()
        
        # Smooth window entrance animation
        self.window_opacity_effect = QGraphicsOpacityEffect(central_widget)
        central_widget.setGraphicsEffect(self.window_opacity_effect)
        self.window_anim = QPropertyAnimation(self.window_opacity_effect, b"opacity")
        self.window_anim.setDuration(240)
        self.window_anim.setStartValue(0.2)
        self.window_anim.setEndValue(1.0)
        self.window_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.window_anim.finished.connect(lambda: central_widget.setGraphicsEffect(None))
        self.window_anim.start()

    def init_menu(self) -> None:
        # A fresh menu bar replaces (and deletes) the previous one when the language changes.
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu(tr("menu.file"))

        action_new = file_menu.addAction(tr("menu.new"))
        action_new.setShortcut(QKeySequence.StandardKey.New)
        action_new.triggered.connect(self.sidebar.on_new_webapp_clicked)

        file_menu.addSeparator()

        action_import = file_menu.addAction(tr("menu.import"))
        action_import.setShortcut(QKeySequence("Ctrl+I"))
        action_import.triggered.connect(self.sidebar.on_import_clicked)

        action_export = file_menu.addAction(tr("menu.export"))
        action_export.setShortcut(QKeySequence("Ctrl+E"))
        action_export.triggered.connect(self.sidebar.on_export_clicked)

        file_menu.addSeparator()

        action_quit = file_menu.addAction(tr("menu.quit"))
        action_quit.setShortcut(QKeySequence.StandardKey.Quit)
        action_quit.triggered.connect(self.close)

        settings_menu = menu_bar.addMenu(tr("menu.settings"))
        language_menu = settings_menu.addMenu(tr("menu.language"))
        language_group = QActionGroup(language_menu)
        for code, label in i18n.LANGUAGES.items():
            action_lang = language_menu.addAction(label)
            action_lang.setCheckable(True)
            action_lang.setChecked(code == i18n.current_language())
            action_lang.setData(code)
            language_group.addAction(action_lang)
        language_group.triggered.connect(lambda action: self.change_language(action.data()))

        help_menu = menu_bar.addMenu(tr("menu.help"))

        action_repo = help_menu.addAction(tr("menu.github"))
        action_repo.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(APP_REPO_URL)))

        help_menu.addSeparator()

        action_about = help_menu.addAction(tr("menu.about", app=APP_NAME))
        action_about.triggered.connect(self.show_about)

    def has_unsaved_changes(self) -> bool:
        for i in range(self.sidebar.list_widget.count()):
            app = self.sidebar.list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            if app and app.is_dirty:
                return True
        return False

    def change_language(self, lang: str) -> None:
        if lang == i18n.current_language():
            return
        if self.has_unsaved_changes():
            confirm = QMessageBox.question(
                self, tr("language.title"), tr("language.unsaved"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm != QMessageBox.StandardButton.Yes:
                self.init_menu()
                return

        i18n.set_language(lang)
        get_settings().setValue(SETTINGS_LANGUAGE_KEY, lang)
        apply_qt_translation(lang)
        self.init_ui()

    def show_about(self) -> None:
        author_link = f"<a href='{APP_AUTHOR_URL}'>{APP_AUTHOR}</a>"
        text = (
            f"<h3>{APP_NAME} <small>v{APP_VERSION}</small></h3>"
            f"<p>{tr('about.description')}</p>"
            f"<p>{tr('about.author', author=author_link)}</p>"
            f"<p>{tr('about.source')} <a href='{APP_REPO_URL}'>{APP_REPO_URL}</a></p>"
            f"<p style='color:#7e8790; font-size:11px;'>"
            f"{tr('about.built_with', qt=qVersion(), pyqt=PYQT_VERSION_STR)}</p>"
        )
        box = QMessageBox(self)
        box.setWindowTitle(tr("about.title", app=APP_NAME))
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        box.setText(text)
        logo_pixmap = get_app_logo_pixmap()
        if not logo_pixmap.isNull():
            box.setIconPixmap(logo_pixmap.scaled(
                72, 72, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        box.addButton(QMessageBox.StandardButton.Ok)
        btn_about_qt = box.addButton(tr("about.about_qt"), QMessageBox.ButtonRole.ActionRole)
        box.exec()
        if box.clickedButton() is btn_about_qt:
            QApplication.aboutQt()

    def apply_theme(self) -> None:
        """Applies the custom, high-fidelity dark stylesheet with Oriental Brutalist aesthetic."""
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        arrow_up = os.path.join(pkg_dir, "chevron-up.svg").replace(os.sep, '/')
        arrow_up_hover = os.path.join(pkg_dir, "chevron-up-hover.svg").replace(os.sep, '/')
        arrow_down = os.path.join(pkg_dir, "chevron-down.svg").replace(os.sep, '/')
        arrow_down_hover = os.path.join(pkg_dir, "chevron-down-hover.svg").replace(os.sep, '/')
        check_icon = os.path.join(pkg_dir, "check.svg").replace(os.sep, '/')

        qss = DARK_THEME_QSS.replace("ARROW_UP_PATH", arrow_up) \
                            .replace("ARROW_UP_HOVER_PATH", arrow_up_hover) \
                            .replace("ARROW_DOWN_PATH", arrow_down) \
                            .replace("ARROW_DOWN_HOVER_PATH", arrow_down_hover) \
                            .replace("CHECK_ICON_PATH", check_icon)
        self.setStyleSheet(qss)

def main() -> None:
    os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.wayland.textinput=false")
    app = QApplication(sys.argv)
    saved_language = get_settings().value(SETTINGS_LANGUAGE_KEY, "", type=str)
    lang = i18n.set_language(saved_language or i18n.detect_system_language())
    apply_qt_translation(lang)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
