import unittest
import os
from webapp_manager.models import Webapp, WebappMemento
from webapp_manager.constants import APPLICATIONS_DIR, DEFAULT_USER_DATA_BASE

class TestWebappModels(unittest.TestCase):
    def test_default_calculations(self):
        webapp = Webapp(
            name="Test Web App",
            url="https://example.com/app/path",
            browser="google-chrome-stable"
        )
        self.assertEqual(webapp.name, "Test Web App")
        self.assertEqual(webapp.get_slug(), "test_web_app")
        self.assertEqual(webapp.wm_class, "test_web_app")
        self.assertEqual(webapp.filepath, os.path.join(APPLICATIONS_DIR, "webapp_test_web_app.desktop"))
        self.assertEqual(webapp.user_data_dir, os.path.join(DEFAULT_USER_DATA_BASE, "test_web_app"))
        self.assertEqual(webapp.icon, "applications-internet")

    def test_exec_line_generation(self):
        webapp = Webapp(
            name="Gemini",
            url="https://gemini.google.com",
            browser="brave",
            width=800,
            height=600,
            user_data_dir="/tmp/gemini_profile",
            wm_class="my-custom-class"
        )
        expected = "brave --window-size=800,600 --class=my-custom-class --app=https://gemini.google.com --user-data-dir=/tmp/gemini_profile"
        self.assertEqual(webapp.exec_line, expected)

    def test_non_isolated_exec_line(self):
        webapp = Webapp(
            name="Gemini",
            url="https://gemini.google.com",
            browser="brave",
            width=800,
            height=600,
            user_data_dir="/tmp/gemini_profile",
            wm_class="my-custom-class",
            isolated_profile=False
        )
        expected = "brave --window-size=800,600 --class=my-custom-class --app=https://gemini.google.com"
        self.assertEqual(webapp.exec_line, expected)

    def test_memento_draft_tracking(self):
        webapp = Webapp(
            name="WhatsApp",
            url="https://web.whatsapp.com",
            browser="chromium"
        )
        
        # Initially, with no saved memento, it counts as dirty/unsaved
        self.assertTrue(webapp.is_dirty)
        
        # Save a memento (simulate successful save to disk)
        webapp._saved_memento = webapp.create_memento()
        self.assertFalse(webapp.is_dirty)
        
        # Edit an attribute
        webapp.name = "WhatsApp Web"
        self.assertTrue(webapp.is_dirty)
        
        # Restore from memento
        webapp.restore(webapp._saved_memento)
        self.assertFalse(webapp.is_dirty)
        self.assertEqual(webapp.name, "WhatsApp")

    def test_real_wm_class(self):
        # Test Google Chrome
        webapp1 = Webapp(
            name="YouTube",
            url="https://www.youtube.com/",
            browser="google-chrome-stable"
        )
        self.assertEqual(webapp1.get_real_wm_class(), "chrome-www.youtube.com__-Default")

        # Test Brave Browser
        webapp2 = Webapp(
            name="Docker",
            url="http://localhost:9000/#!/3/docker/dashboard",
            browser="brave-browser"
        )
        self.assertEqual(webapp2.get_real_wm_class(), "brave-localhost__-Default")

        # Test Microsoft Edge
        webapp3 = Webapp(
            name="Gemini",
            url="https://gemini.google.com/app",
            browser="microsoft-edge-stable"
        )
        self.assertEqual(webapp3.get_real_wm_class(), "msedge-gemini.google.com__app-Default")
