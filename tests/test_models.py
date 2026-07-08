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
