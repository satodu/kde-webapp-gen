import json
import os
import unittest
from unittest.mock import patch

from webapp_manager import i18n


class TestI18n(unittest.TestCase):
    def tearDown(self):
        i18n.set_language("en")

    def test_all_languages_have_the_same_keys(self):
        keys = {}
        for code in i18n.LANGUAGES:
            with open(os.path.join(i18n._I18N_DIR, f"{code}.json"), encoding="utf-8") as f:
                keys[code] = set(json.load(f))
        for code, lang_keys in keys.items():
            self.assertEqual(lang_keys, keys["en"], f"{code}.json keys differ from en.json")

    def test_tr_formats_and_falls_back(self):
        i18n.set_language("es")
        self.assertEqual(i18n.tr("editor.saved", name="YouTube"), "¡Webapp 'YouTube' guardado correctamente!")
        self.assertEqual(i18n.tr("missing.key"), "missing.key")

    def test_unknown_language_falls_back_to_english(self):
        self.assertEqual(i18n.set_language("fr"), "en")
        self.assertEqual(i18n.tr("menu.file"), "&File")

    def test_detect_system_language(self):
        with patch.dict(os.environ, {"LANGUAGE": "", "LC_ALL": "", "LC_MESSAGES": "", "LANG": "pt_BR.UTF-8"}):
            self.assertEqual(i18n.detect_system_language(), "pt")
        with patch.dict(os.environ, {"LANGUAGE": "es_ES:en", "LC_ALL": "", "LC_MESSAGES": "", "LANG": "C"}):
            self.assertEqual(i18n.detect_system_language(), "es")
        with patch.dict(os.environ, {"LANGUAGE": "", "LC_ALL": "", "LC_MESSAGES": "", "LANG": "de_DE.UTF-8"}), \
             patch("locale.getlocale", return_value=(None, None)):
            self.assertEqual(i18n.detect_system_language(), "en")


if __name__ == "__main__":
    unittest.main()
