import json
import locale
import os
from typing import Dict, Optional

LANGUAGES: Dict[str, str] = {
    "en": "English",
    "pt": "Português",
    "es": "Español",
}
DEFAULT_LANGUAGE: str = "en"

_I18N_DIR = os.path.dirname(os.path.abspath(__file__))
_catalogs: Dict[str, Dict[str, str]] = {}
_current: str = DEFAULT_LANGUAGE


def _load(lang: str) -> Dict[str, str]:
    if lang not in _catalogs:
        try:
            with open(os.path.join(_I18N_DIR, f"{lang}.json"), encoding="utf-8") as f:
                _catalogs[lang] = json.load(f)
        except (OSError, ValueError) as e:
            print(f"Failed to load translations for '{lang}': {e}")
            _catalogs[lang] = {}
    return _catalogs[lang]


def detect_system_language() -> str:
    """Returns the first supported language from the environment locale, or English."""
    candidates = [os.environ.get(var, "") for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG")]
    candidates.append(locale.getlocale()[0] or "")
    for value in candidates:
        for part in value.split(":"):
            code = part.split("_")[0].split(".")[0].lower()
            if code in LANGUAGES:
                return code
    return DEFAULT_LANGUAGE


def set_language(lang: Optional[str]) -> str:
    global _current
    _current = lang if lang in LANGUAGES else DEFAULT_LANGUAGE
    return _current


def current_language() -> str:
    return _current


def tr(key: str, /, **kwargs: object) -> str:
    """Translates a key to the current language, falling back to English and then to the key itself."""
    text = _load(_current).get(key) or _load(DEFAULT_LANGUAGE).get(key) or key
    return text.format(**kwargs) if kwargs else text
