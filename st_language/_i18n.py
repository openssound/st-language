"""
Messaggi della libreria (errori di sintassi, avvisi) nella lingua scelta.

I testi sono scritti in italiano nel codice, dentro tr(), come in
SoundText; i cataloghi locales/<lingua>.json ({testo italiano:
traduzione}) danno l'inglese, il francese e lo spagnolo. La lingua si
sceglie con set_language() o con la variabile d'ambiente ST_LANGUAGE
(altrimenti LANG); senza indicazioni, l'inglese.

Un programma che ha gia' le sue traduzioni (SoundText) puo' sostituire
tr con set_translator(): tutti i messaggi passano allora da li'.
"""

import json
import os
from typing import Callable, Dict, Optional

LANGUAGES = ("it", "en", "fr", "es")
SOURCE_LANGUAGE = "it"
DEFAULT_LANGUAGE = "en"

_translator: Optional[Callable] = None
_language: Optional[str] = None
_catalog: Dict[str, str] = {}


def set_translator(fn: Optional[Callable]) -> None:
    """fn(testo_italiano, *args, **kwargs) -> testo; None torna ai cataloghi."""
    global _translator
    _translator = fn


def _env_language() -> str:
    for var in ("ST_LANGUAGE", "LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        for part in os.environ.get(var, "").split(":"):
            code = part.strip().lower()[:2]
            if code in LANGUAGES:
                return code
    return DEFAULT_LANGUAGE


def set_language(code: Optional[str] = None) -> str:
    """Sceglie la lingua dei messaggi (None: dall'ambiente); ritorna quella in uso."""
    global _language, _catalog
    code = (code or _env_language()).lower()[:2]
    if code not in LANGUAGES:
        code = DEFAULT_LANGUAGE
    _language = code
    _catalog = {}
    if code != SOURCE_LANGUAGE:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales", f"{code}.json")
        try:
            with open(path, encoding="utf-8") as f:
                _catalog = {k: v for k, v in json.load(f).items() if isinstance(v, str) and v}
        except (OSError, ValueError):
            _catalog = {}
    return code


def language() -> str:
    if _language is None:
        set_language()
    return _language


def tr(text: str, *args, **kwargs) -> str:
    if _translator is not None:
        return _translator(text, *args, **kwargs)
    if _language is None:
        set_language()
    out = _catalog.get(text, text)
    if args or kwargs:
        try:
            return out.format(*args, **kwargs)
        except (IndexError, KeyError, ValueError):
            return text.format(*args, **kwargs)
    return out
