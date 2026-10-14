import unittest
import os
import shutil
import tempfile
from unittest.mock import patch
from webapp_manager.models import Webapp
from webapp_manager.desktop_manager import DesktopManager

class TestDesktopManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory in workspace for test desktop files
        self.test_dir = tempfile.mkdtemp(dir=os.getcwd())

    def tearDown(self):
        # Clean up temporary test files
        shutil.rmtree(self.test_dir)

    def test_create_read_delete_entry(self):
        # Patch APPLICATIONS_DIR to self.test_dir during execution
        with patch("webapp_manager.desktop_manager.APPLICATIONS_DIR", self.test_dir):
            webapp = Webapp(
                name="Test Application",
                url="https://testapp.org",
                browser="chromium",
                width=1200,
                height=900,
                filepath=os.path.join(self.test_dir, "webapp_test_application.desktop")
            )

            dm = DesktopManager()
            
            # Create
            dm.create_entry(webapp)
            self.assertTrue(os.path.exists(webapp.filepath))
            self.assertIsNotNone(webapp._saved_memento)
            
            # Load / Read
            loaded_list = dm.load_all_entries(browsers=[("Chromium", "chromium")])
            self.assertEqual(len(loaded_list), 1)
            
            loaded = loaded_list[0]
            self.assertEqual(loaded.name, "Test Application")
            self.assertEqual(loaded.url, "https://testapp.org")
            self.assertEqual(loaded.browser, "chromium")
            self.assertEqual(loaded.width, 1200)
            self.assertEqual(loaded.height, 900)
            self.assertEqual(loaded.filepath, webapp.filepath)

            # Delete
            dm.delete_entry(webapp.filepath)
            self.assertFalse(os.path.exists(webapp.filepath))
            
            # Load list again
            loaded_list_after_delete = dm.load_all_entries(browsers=[("Chromium", "chromium")])
            self.assertEqual(len(loaded_list_after_delete), 0)

    def test_shared_profile_is_pinned_and_reloaded(self):
        with patch("webapp_manager.desktop_manager.APPLICATIONS_DIR", self.test_dir), \
             patch("webapp_manager.desktop_manager.BrowserDetector.detect_last_used_profile", return_value="Profile 2"):
            webapp = Webapp(
                name="Shared App",
                url="https://shared.example.com",
                browser="google-chrome-stable",
                isolated_profile=False,
                filepath=os.path.join(self.test_dir, "webapp_shared_app.desktop")
            )
            dm = DesktopManager()
            dm.create_entry(webapp)

            with open(webapp.filepath) as f:
                content = f.read()
            self.assertIn('--profile-directory="Profile 2"', content)
            self.assertIn("StartupWMClass=chrome-shared.example.com__-Profile_2", content)

            loaded = dm.load_all_entries(browsers=[("Google Chrome", "google-chrome-stable")])[0]
            self.assertEqual(loaded.profile_directory, "Profile 2")
            self.assertFalse(loaded.is_dirty)


    def test_new_launcher_is_named_after_app_id(self):
        with patch("webapp_manager.desktop_manager.APPLICATIONS_DIR", self.test_dir):
            webapp = Webapp(name="Shortwave", url="https://app.shortwave.com", browser="vivaldi-stable")
            path = DesktopManager.choose_new_filepath(webapp)
            self.assertEqual(path, os.path.join(self.test_dir, "vivaldi-app.shortwave.com__-Default.desktop"))

            # A second webapp for the same site/browser/profile must not overwrite the first launcher
            webapp.filepath = path
            DesktopManager().create_entry(webapp)
            other = Webapp(name="Shortwave Work", url="https://app.shortwave.com/", browser="vivaldi-stable")
            self.assertEqual(DesktopManager.choose_new_filepath(other),
                             os.path.join(self.test_dir, "webapp_shortwave_work.desktop"))

    def test_new_shared_launcher_uses_pinned_profile_in_name(self):
        with patch("webapp_manager.desktop_manager.APPLICATIONS_DIR", self.test_dir), \
             patch("webapp_manager.desktop_manager.BrowserDetector.detect_last_used_profile", return_value="Profile 1"):
            webapp = Webapp(name="YouTube", url="https://www.youtube.com", browser="google-chrome-stable",
                            isolated_profile=False)
            self.assertEqual(os.path.basename(DesktopManager.choose_new_filepath(webapp)),
                             "chrome-www.youtube.com__-Profile_1.desktop")


class TestBrowserProfileDetection(unittest.TestCase):
    def test_reads_last_used_profile_from_local_state(self):
        from webapp_manager.browser_detector import BrowserDetector
        with tempfile.TemporaryDirectory() as home:
            config = os.path.join(home, ".config", "BraveSoftware", "Brave-Browser")
            os.makedirs(config)
            with open(os.path.join(config, "Local State"), "w") as f:
                f.write('{"profile": {"last_used": "Profile 3"}}')
            with patch.dict(os.environ, {"HOME": home}):
                self.assertEqual(BrowserDetector.detect_last_used_profile("brave"), "Profile 3")
                self.assertEqual(BrowserDetector.detect_last_used_profile("google-chrome-stable"), "Default")
