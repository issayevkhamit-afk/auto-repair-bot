import json
import os
from typing import Dict, Any

TRANSLATIONS_FILE = os.path.join(os.path.dirname(__file__), "translations.json")

def load_translations() -> Dict[str, Dict[str, str]]:
    if not os.path.exists(TRANSLATIONS_FILE):
        return {}
    with open(TRANSLATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

TRANSLATIONS = load_translations()

def save_translations(new_translations: Dict[str, Dict[str, str]]):
    global TRANSLATIONS
    with open(TRANSLATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(new_translations, f, ensure_ascii=False, indent=2)
    TRANSLATIONS = new_translations

def t(key: str, lang: str = "ru") -> str:
    """Returns the translated string for a given key and language."""
    if lang not in TRANSLATIONS:
        lang = "ru"
    return TRANSLATIONS[lang].get(key, key)
