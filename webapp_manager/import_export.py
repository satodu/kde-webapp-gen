import os
import re
import json
import base64
import binascii
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from webapp_manager.constants import ICONS_DIR
from webapp_manager.models import Webapp

FORMAT_ID = "kde-webapp-gen"
FORMAT_VERSION = 1

DEFAULT_ICON = "applications-internet"
ALLOWED_ICON_EXTENSIONS = {".png", ".svg", ".jpg", ".jpeg", ".ico", ".xpm"}
MAX_ICON_BYTES = 5 * 1024 * 1024

CONFLICT_SKIP = "skip"
CONFLICT_OVERWRITE = "overwrite"
CONFLICT_RENAME = "rename"


class ImportExportError(Exception):
    pass


class ImportedWebapp:
    """A validated webapp read from an export file, not yet written to disk."""

    def __init__(self, webapp: Webapp, icon_ext: str = "", icon_data: bytes = b"") -> None:
        self.webapp = webapp
        self.icon_ext = icon_ext
        self.icon_data = icon_data


def _icon_to_dict(icon: str) -> Dict[str, str]:
    if icon and os.path.isabs(icon):
        ext = os.path.splitext(icon)[1].lower()
        if os.path.isfile(icon) and ext in ALLOWED_ICON_EXTENSIONS and os.path.getsize(icon) <= MAX_ICON_BYTES:
            with open(icon, "rb") as f:
                data = base64.b64encode(f.read()).decode("ascii")
            return {"type": "embedded", "extension": ext, "data": data}
        return {"type": "theme", "value": DEFAULT_ICON}
    return {"type": "theme", "value": icon or DEFAULT_ICON}


def webapp_to_dict(webapp: Webapp) -> Dict[str, Any]:
    return {
        "name": webapp.name,
        "url": webapp.url,
        "browser": webapp.browser,
        "width": webapp.width,
        "height": webapp.height,
        "isolated_profile": webapp.isolated_profile,
        "wm_class": webapp.wm_class,
        "icon": _icon_to_dict(webapp.icon),
    }


def build_export(webapps: List[Webapp]) -> Dict[str, Any]:
    return {
        "format": FORMAT_ID,
        "version": FORMAT_VERSION,
        "exported_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "webapps": [webapp_to_dict(app) for app in webapps],
    }


def export_webapps(webapps: List[Webapp], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(build_export(webapps), f, indent=2, ensure_ascii=False)
        f.write("\n")


def _require_str(data: Dict[str, Any], key: str, index: int) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ImportExportError(f"Webapp #{index + 1}: campo '{key}' ausente ou inválido.")
    return value.strip()


def _optional_int(data: Dict[str, Any], key: str, default: int) -> int:
    value = data.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or not (100 <= value <= 10000):
        return default
    return value


def _parse_icon(raw: Any, index: int) -> Tuple[str, str, bytes]:
    """Returns (theme_icon_name, embedded_extension, embedded_bytes)."""
    if not isinstance(raw, dict):
        return DEFAULT_ICON, "", b""

    if raw.get("type") == "embedded":
        ext = str(raw.get("extension", "")).lower()
        if ext not in ALLOWED_ICON_EXTENSIONS:
            raise ImportExportError(f"Webapp #{index + 1}: extensão de ícone não suportada '{ext}'.")
        try:
            data = base64.b64decode(str(raw.get("data", "")), validate=True)
        except (binascii.Error, ValueError):
            raise ImportExportError(f"Webapp #{index + 1}: ícone embutido corrompido.")
        if not data or len(data) > MAX_ICON_BYTES:
            raise ImportExportError(f"Webapp #{index + 1}: ícone embutido vazio ou grande demais.")
        return DEFAULT_ICON, ext, data

    value = raw.get("value")
    # Theme icons are names only; absolute paths would point to the exporting machine.
    if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.+-]+", value):
        return value, "", b""
    return DEFAULT_ICON, "", b""


def webapp_from_dict(data: Any, index: int = 0) -> ImportedWebapp:
    if not isinstance(data, dict):
        raise ImportExportError(f"Webapp #{index + 1}: entrada inválida.")

    name = _require_str(data, "name", index)
    url = _require_str(data, "url", index)
    browser = _require_str(data, "browser", index)

    # The URL ends up in the Exec line, so whitespace would inject extra arguments.
    if not re.fullmatch(r"https?://\S+", url):
        raise ImportExportError(f"Webapp #{index + 1}: URL inválida '{url}'.")

    wm_class = data.get("wm_class", "")
    if not isinstance(wm_class, str) or not re.fullmatch(r"[A-Za-z0-9_.-]*", wm_class):
        wm_class = ""

    isolated = data.get("isolated_profile", True)
    if not isinstance(isolated, bool):
        isolated = True

    icon_name, icon_ext, icon_data = _parse_icon(data.get("icon"), index)

    webapp = Webapp(
        name=name,
        url=url,
        browser=browser,
        width=_optional_int(data, "width", 1024),
        height=_optional_int(data, "height", 768),
        wm_class=wm_class,
        icon=icon_name,
        isolated_profile=isolated,
    )
    return ImportedWebapp(webapp, icon_ext, icon_data)


def load_import_file(path: str) -> List[ImportedWebapp]:
    """Parses and validates the whole file. Raises ImportExportError before anything is written."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, UnicodeDecodeError) as e:
        raise ImportExportError(f"Não foi possível ler o arquivo:\n{e}")
    except json.JSONDecodeError as e:
        raise ImportExportError(f"Arquivo não é um JSON válido:\n{e}")

    if not isinstance(payload, dict) or payload.get("format") != FORMAT_ID:
        raise ImportExportError("Arquivo não é uma exportação do KDE Webapp Manager.")

    version = payload.get("version")
    if not isinstance(version, int) or version > FORMAT_VERSION or version < 1:
        raise ImportExportError(f"Versão de formato não suportada: {version}.")

    entries = payload.get("webapps")
    if not isinstance(entries, list):
        raise ImportExportError("Campo 'webapps' ausente ou inválido.")

    return [webapp_from_dict(entry, i) for i, entry in enumerate(entries)]


def find_conflict(webapp: Webapp, existing: List[Webapp]) -> Optional[Webapp]:
    for app in existing:
        if app.filepath == webapp.filepath:
            return app
    return None


def unique_name(name: str, existing: List[Webapp]) -> str:
    taken = {app.filepath for app in existing}
    counter = 2
    while True:
        candidate = Webapp(name=f"{name} ({counter})", url="", browser="")
        if candidate.filepath not in taken and not os.path.exists(candidate.filepath):
            return candidate.name
        counter += 1


def resolve_for_install(
    imported: ImportedWebapp,
    existing: List[Webapp],
    conflict_policy: str,
    browser_cmds: List[str],
    fallback_browser: str,
) -> Optional[Webapp]:
    """Returns a fresh Webapp ready to be written, or None if it must be skipped."""
    src = imported.webapp
    browser = src.browser if src.browser in browser_cmds else fallback_browser
    name = src.name
    user_data_dir = ""

    conflict = find_conflict(src, existing)
    if conflict:
        if conflict_policy == CONFLICT_SKIP:
            return None
        if conflict_policy == CONFLICT_RENAME:
            name = unique_name(src.name, existing)
        else:
            # Keep the existing profile so the user doesn't lose their logged-in session.
            user_data_dir = conflict.user_data_dir

    return Webapp(
        name=name,
        url=src.url,
        browser=browser,
        width=src.width,
        height=src.height,
        user_data_dir=user_data_dir,
        wm_class=src.wm_class if name == src.name else "",
        icon=src.icon,
        isolated_profile=src.isolated_profile,
    )


def write_embedded_icon(webapp: Webapp, imported: ImportedWebapp) -> None:
    if not imported.icon_data:
        return
    os.makedirs(ICONS_DIR, exist_ok=True)
    dest_path = os.path.join(ICONS_DIR, f"webapp_{webapp.get_slug()}{imported.icon_ext}")
    with open(dest_path, "wb") as f:
        f.write(imported.icon_data)
    webapp.icon = dest_path
