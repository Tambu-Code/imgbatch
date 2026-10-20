import json
from pathlib import Path

from core.settings import Settings

PROFILES_FILE = Path.home() / ".imgbatch_profiles.json"


def load_profiles():
    """Restituisce un dizionario {nome: Settings}."""
    if not PROFILES_FILE.exists():
        return {}
    try:
        data = json.loads(PROFILES_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return {name: Settings.from_dict(values) for name, values in data.items()}


def _write_profiles(profiles):
    data = {name: s.to_dict() for name, s in profiles.items()}
    PROFILES_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_profile(name, settings):
    profiles = load_profiles()
    profiles[name] = settings
    _write_profiles(profiles)


def delete_profile(name):
    profiles = load_profiles()
    if name in profiles:
        del profiles[name]
        _write_profiles(profiles)