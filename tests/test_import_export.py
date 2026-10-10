import unittest
import os
import json
import shutil
import tempfile
from unittest.mock import patch
from webapp_manager.models import Webapp
from webapp_manager import import_export
from webapp_manager.import_export import ImportExportError


class TestImportExport(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(dir=os.getcwd())
        self.export_path = os.path.join(self.test_dir, "webapps.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def write_payload(self, payload):
        with open(self.export_path, "w") as f:
            json.dump(payload, f)

    def test_round_trip_preserves_fields(self):
        app = Webapp(
            name="WhatsApp",
            url="https://web.whatsapp.com",
            browser="chromium",
            width=1200,
            height=900,
            wm_class="whatsapp",
            icon="whatsapp-icon",
            isolated_profile=False,
        )
        import_export.export_webapps([app], self.export_path)
        loaded = import_export.load_import_file(self.export_path)

        self.assertEqual(len(loaded), 1)
        result = loaded[0].webapp
        self.assertEqual(result.name, "WhatsApp")
        self.assertEqual(result.url, "https://web.whatsapp.com")
        self.assertEqual(result.browser, "chromium")
        self.assertEqual(result.width, 1200)
        self.assertEqual(result.height, 900)
        self.assertEqual(result.wm_class, "whatsapp")
        self.assertEqual(result.icon, "whatsapp-icon")
        self.assertFalse(result.isolated_profile)

    def test_user_data_dir_is_not_exported_and_regenerated(self):
        app = Webapp(name="Slack", url="https://app.slack.com", browser="chromium",
                     user_data_dir="/home/someone/custom/profile")
        import_export.export_webapps([app], self.export_path)

        with open(self.export_path) as f:
            raw = json.load(f)
        self.assertNotIn("user_data_dir", raw["webapps"][0])
        self.assertNotIn("filepath", raw["webapps"][0])

        loaded = import_export.load_import_file(self.export_path)[0].webapp
        self.assertEqual(loaded.user_data_dir, loaded.generate_default_user_data_dir())

    def test_custom_icon_is_embedded_and_restored(self):
        icon_src = os.path.join(self.test_dir, "icon.png")
        with open(icon_src, "wb") as f:
            f.write(b"\x89PNG fake icon bytes")

        app = Webapp(name="Notion", url="https://notion.so", browser="chromium", icon=icon_src)
        import_export.export_webapps([app], self.export_path)
        imported = import_export.load_import_file(self.export_path)[0]
        self.assertEqual(imported.icon_ext, ".png")

        icons_dir = os.path.join(self.test_dir, "icons")
        with patch("webapp_manager.import_export.ICONS_DIR", icons_dir):
            import_export.write_embedded_icon(imported.webapp, imported)

        self.assertEqual(imported.webapp.icon, os.path.join(icons_dir, "webapp_notion.png"))
        with open(imported.webapp.icon, "rb") as f:
            self.assertEqual(f.read(), b"\x89PNG fake icon bytes")

    def test_missing_icon_file_falls_back_to_default(self):
        app = Webapp(name="X", url="https://x.com", browser="chromium", icon="/nope/missing.png")
        self.assertEqual(import_export.webapp_to_dict(app)["icon"],
                         {"type": "theme", "value": import_export.DEFAULT_ICON})

    def test_invalid_json_raises(self):
        with open(self.export_path, "w") as f:
            f.write("{not json")
        with self.assertRaises(ImportExportError):
            import_export.load_import_file(self.export_path)

    def test_wrong_format_or_version_raises(self):
        self.write_payload({"format": "other", "version": 1, "webapps": []})
        with self.assertRaises(ImportExportError):
            import_export.load_import_file(self.export_path)

        self.write_payload({"format": import_export.FORMAT_ID, "version": 99, "webapps": []})
        with self.assertRaises(ImportExportError):
            import_export.load_import_file(self.export_path)

    def test_missing_required_field_raises(self):
        self.write_payload({"format": import_export.FORMAT_ID, "version": 1,
                            "webapps": [{"name": "A", "browser": "chromium"}]})
        with self.assertRaises(ImportExportError):
            import_export.load_import_file(self.export_path)

    def test_url_with_whitespace_is_rejected(self):
        self.write_payload({"format": import_export.FORMAT_ID, "version": 1,
                            "webapps": [{"name": "A", "url": "https://a.com --evil", "browser": "chromium"}]})
        with self.assertRaises(ImportExportError):
            import_export.load_import_file(self.export_path)

    def test_conflict_policies(self):
        existing = [Webapp(name="Gmail", url="https://mail.google.com", browser="chromium",
                           user_data_dir="/keep/this/profile")]
        imported = import_export.ImportedWebapp(
            Webapp(name="Gmail", url="https://mail.google.com/u/1", browser="chromium")
        )

        self.assertIsNone(import_export.resolve_for_install(
            imported, existing, import_export.CONFLICT_SKIP, ["chromium"], "chromium"))

        overwritten = import_export.resolve_for_install(
            imported, existing, import_export.CONFLICT_OVERWRITE, ["chromium"], "chromium")
        self.assertEqual(overwritten.filepath, existing[0].filepath)
        self.assertEqual(overwritten.user_data_dir, "/keep/this/profile")

        renamed = import_export.resolve_for_install(
            imported, existing, import_export.CONFLICT_RENAME, ["chromium"], "chromium")
        self.assertEqual(renamed.name, "Gmail (2)")
        self.assertNotEqual(renamed.filepath, existing[0].filepath)

    def test_missing_browser_uses_fallback(self):
        imported = import_export.ImportedWebapp(
            Webapp(name="Teams", url="https://teams.microsoft.com", browser="some-unknown-browser")
        )
        result = import_export.resolve_for_install(
            imported, [], import_export.CONFLICT_RENAME, ["chromium", "brave"], "brave")
        self.assertEqual(result.browser, "brave")


if __name__ == "__main__":
    unittest.main()
