"""
ST-language: la notazione musicale testuale di SoundText come libreria
Python autonoma (nessuna dipendenza esterna, Python 3.8+).

    import st_language as st

    events = st.parse("4: c d e f | 2g 2g")          # eventi con tempi in quarti
    ok, error = st.validate("4: C Am | F G")
    warnings = st.check("4: c d e | f")               # controlli di battuta, testo cantato

    song = st.load_song("brano.st")                    # o st.read_song(testo)
    st.to_midi(song, "brano.mid")
    st.to_musicxml(song, "brano.musicxml")
    st.to_abc(song, "brano.abc")

La specifica del linguaggio e del formato .st e' in docs/spec/ del
repository di SoundText; i comandi da terminale sono 'st-language'
(check, midi, musicxml, abc, events), 'stcheck', 'st2mid', 'st2musicxml',
'st2abc'.
"""

from typing import Dict, List, Optional, Tuple

from ._i18n import language, set_language, set_translator  # noqa: F401
from .notation import (  # noqa: F401
    BarIssue, Event, NotationError, Pattern, check_bar_lines, notation_warnings, parse_track_text,
    tokenize, transpose_tokens, validate_track_text,
)
from .song import Clip, Part, Song, load_song, read_song, song_from_notation, text_to_song  # noqa: F401

__version__ = "2.2.0"

__all__ = [
    "BarIssue", "Clip", "Event", "NotationError", "Part", "Pattern", "Song", "check", "check_bar_lines",
    "language", "load_song", "notation_warnings", "parse", "parse_track_text", "read_song",
    "set_language", "set_translator", "song_from_notation", "text_to_song", "to_abc", "to_midi", "to_musicxml",
    "tokenize", "transpose_tokens", "validate", "validate_track_text",
]


def parse(text: str, patterns: Optional[Dict[str, Pattern]] = None, default_octave: int = 4) -> List[Event]:
    """Gli eventi di un testo in notazione (una traccia)."""
    return parse_track_text(text, patterns or {}, default_octave=default_octave)


def validate(text: str, patterns: Optional[Dict[str, Pattern]] = None) -> Tuple[bool, str]:
    """(True, '') se il testo e' valido, altrimenti (False, messaggio)."""
    return validate_track_text(text, patterns or {})


def check(text: str, patterns: Optional[Dict[str, Pattern]] = None, time_sig: str = "4/4",
          metrica_changes=()) -> List[BarIssue]:
    """Gli avvisi che non impediscono di suonare: controlli di battuta e
    testo cantato con troppe sillabe."""
    return notation_warnings(text, patterns or {}, time_sig, metrica_changes)


def to_midi(song: Song, path: str, only_audible: bool = True) -> str:
    from .midi import song_to_midi
    return song_to_midi(song, path, only_audible=only_audible)


def to_musicxml(song: Song, path: str, only_audible: bool = True) -> str:
    from .musicxml import export_project_to_musicxml
    return export_project_to_musicxml(song, path, only_audible=only_audible)


def to_abc(song: Song, path: str, only_audible: bool = True) -> str:
    from .abc import export_project_to_abc
    return export_project_to_abc(song, path, only_audible=only_audible)
