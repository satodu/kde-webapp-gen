import unittest
import os
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from webapp_manager.gui import MainWindow
from webapp_manager.models import Webapp

# Ensure a single QApplication instance exists for GUI tests
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestGUI(unittest.TestCase):
    @patch("webapp_manager.gui.BrowserDetector.detect_browsers")
    @patch("webapp_manager.widgets.sidebar.DesktopManager")
    def setUp(self, mock_dm_class, mock_detect_browsers):
        # Mock detected browsers to isolate test from host system dependencies
        mock_detect_browsers.return_value = [("Brave", "brave"), ("Chromium", "chromium")]

        # Configure mocked webapps to load
        self.app1 = Webapp(
            name="Alpha App",
            url="https://alpha.io",
            browser="brave",
            filepath="/tmp/webapp_alpha.desktop"
        )
        self.app1._saved_memento = self.app1.create_memento()
        
        self.app2 = Webapp(
            name="Beta App",
            url="https://beta.io",
            browser="chromium",
            filepath="/tmp/webapp_beta.desktop"
        )
        self.app2._saved_memento = self.app2.create_memento()

        # Mock the DesktopManager returned entries
        self.mock_dm = MagicMock()
        self.mock_dm.load_all_entries.return_value = [self.app1, self.app2]
        mock_dm_class.return_value = self.mock_dm

        # Create window
        self.window = MainWindow()

    def test_sidebar_loads_webapps(self):
        # Check that sidebar list loaded both applications
        self.assertEqual(self.window.sidebar.list_widget.count(), 2)
        
        item_alpha = self.window.sidebar.list_widget.item(0)
        item_beta = self.window.sidebar.list_widget.item(1)
        
        self.assertEqual(item_alpha.data(Qt.ItemDataRole.UserRole).name, "Alpha App")
        self.assertEqual(item_beta.data(Qt.ItemDataRole.UserRole).name, "Beta App")

    def test_new_webapp_clears_fields(self):
        # Click new webapp
        self.window.sidebar.on_new_webapp_clicked()
        
        # Fields must be cleared and discard must be disabled
        self.assertEqual(self.window.editor.input_name.text(), "")
        self.assertEqual(self.window.editor.input_url.text(), "")
        self.assertFalse(self.window.editor.btn_discard.isEnabled())

    def test_editor_modifications_sync_and_revert(self):
        # Select "Alpha App"
        self.window.sidebar.list_widget.setCurrentRow(0)
        self.assertEqual(self.window.editor.input_name.text(), "Alpha App")
        self.assertFalse(self.window.editor.btn_discard.isEnabled())
        
        # Modify the app name in GUI
        self.window.editor.input_name.setText("Alpha Mod")
        
        # Ensure changes synced to self.current_webapp and is_dirty is true
        self.assertEqual(self.window.editor.current_webapp.name, "Alpha Mod")
        self.assertTrue(self.window.editor.current_webapp.is_dirty)
        self.assertTrue(self.window.editor.btn_discard.isEnabled())
        
        # Revert changes using the Discard button
        self.window.editor.discard_changes()
        
        # Ensure values reverted and dirty flag reset
        self.assertEqual(self.window.editor.input_name.text(), "Alpha App")
        self.assertFalse(self.window.editor.current_webapp.is_dirty)
        self.assertFalse(self.window.editor.btn_discard.isEnabled())

    def test_new_webapp_after_selection(self):
        # Select first item
        self.window.sidebar.list_widget.setCurrentRow(0)
        self.assertEqual(self.window.editor.input_name.text(), "Alpha App")
        
        # Click new webapp
        self.window.sidebar.on_new_webapp_clicked()
        
        # Type a new name
        self.window.editor.input_name.setText("Gamma App")
        
        # Verify that it creates a NEW item in the sidebar, rather than editing "Alpha App"
        self.assertEqual(self.window.sidebar.list_widget.count(), 3)
        self.assertEqual(self.window.sidebar.list_widget.item(2).data(Qt.ItemDataRole.UserRole).name, "Gamma App")
