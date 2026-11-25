"""
Come si scrivono bemolle e diesis (2.13): con i simboli '♭' e '♯' o con le
lettere 'b' e '#'. Le due forme valgono sempre la stessa cosa; questo
modulo riscrive un testo dall'una all'altra senza toccare altro.

    normalize_accidentals(song_text, "symbols")   # 'eb' -> 'e♭', 'F#m7' -> 'F♯m7'
    normalize_accidentals(song_text, "ascii")     # 'e♭' -> 'eb', 'F♯m7' -> 'F#m7'

Si riscrivono le note, gli accordi (anche il basso dopo '/'), le tonalita'
('key=Eb', 'Tonalita: Bb'), le sigle '$Bb7' e le tappe di un portamento. Non
si toccano commenti, testi cantati, nomi di pattern, tracce e strumenti, le
altre righe di intestazione, e le alterazioni dentro la sigla di un accordo
('C7#9', 'Cm7b5'), che sono estensioni e non la nota.
"""

import re
from typing import List, Optional, Tuple

from ._i18n import tr
from .instruments import PERCUSSION_ALIASES
from .notation import (
    LYRIC_QUOTE, RE_CHORD, RE_HARMONY, RE_KEY_MODE, RE_NOTE, RE_REPEAT_GROUP, RE_SLIDE_POINT, RE_VOICES,
    _tokenize_spans_raw, split_note_value, split_voices, tokenize_spans,
)
from .stfile import RE_BAR_KEY, RE_KEY, RE_KEY_LIST_HDR, RE_ST_VERSION

STYLES = ("symbols", "ascii")

_TO_SYMBOL = {"b": "♭", "#": "♯"}
_TO_ASCII = {"♭": "b", "♯": "#"}
_ACCIDENTAL_CHARS = "#♯b♭"
_BLOCK = re.compile(r"^(\d*)\[(.*)\](.*)$", re.DOTALL)
_KEY_IN_HEADER = re.compile(r"([A-G])([#♯b♭])(m?)(?![A-Za-z0-9])")


def check_style(style: Optional[str]) -> Optional[str]:
    """Lo stile ('symbols', 'ascii') o None; altrimenti ValueError."""
    if style is not None and style not in STYLES:
        raise ValueError(tr("Stile delle alterazioni sconosciuto: '{style}'. Ammessi: {0}", ", ".join(STYLES),
                            style=style))
    return style


def _char(ch: str, style: str) -> str:
    return (_TO_SYMBOL if style == "symbols" else _TO_ASCII).get(ch, ch)


def _accidental_positions(base: str) -> List[int]:
    """Le posizioni, in 'base' (un token senza valore di nota), dei caratteri
    che sono l'alterazione di una nota, di un accordo o del suo basso."""
    positions: List[int] = []
    m = RE_NOTE.match(base)
    if m:
        if m.group(3) and m.group(3) in _ACCIDENTAL_CHARS:
            positions.append(m.start(3))
        return positions
    m = RE_CHORD.match(base)
    if m:
        from .chords import parse_chord_symbol
        try:
            parse_chord_symbol(m.group(2) + m.group(3) + m.group(4))
        except Exception:                  # non e' un accordo: una parola qualunque
            return []
        if m.group(3):
            positions.append(m.start(3))
        bass = m.group(6)
        if bass and len(bass) == 2:
            positions.append(m.start(6) + 1)
        return positions
    m = RE_KEY_MODE.match(base)
    if m and m.group(1):
        if len(m.group(1)) > 1 and m.group(1)[1] in _ACCIDENTAL_CHARS:
            positions.append(m.start(1) + 1)
        return positions
    m = RE_HARMONY.match(base)
    if m:
        if len(m.group(1)) > 1 and m.group(1)[1] in _ACCIDENTAL_CHARS:
            positions.append(m.start(1) + 1)
        if m.group(2) and len(m.group(2)) == 2:
            positions.append(m.start(2) + 1)
    return positions


def _plain(tok: str, style: str) -> str:
    if tok[:1] in (LYRIC_QUOTE, "%", "&") or tok.startswith('$"'):
        return tok
    if ">" in tok and not tok.endswith(">"):
        # portamento c*4>d*4>c*4: ogni tappa e' una nota
        points = tok.split(">")
        if all(RE_SLIDE_POINT.match(split_note_value(p)[0]) for p in points[:-1]):
            return ">".join(_plain(p, style) for p in points)
    base, _tail = split_note_value(tok)
    positions = _accidental_positions(base)
    if not positions or any(base[k] != tok[k] for k in positions if k < len(tok)) or len(base) > len(tok) + 1:
        return tok
    chars = list(tok)
    for k in positions:
        if k < len(chars):
            chars[k] = _char(chars[k], style)
    return "".join(chars)


def _token(tok: str, style: str) -> str:
    if tok[:1] in (LYRIC_QUOTE, "%", "&") or tok.startswith('$"'):
        return tok
    m = RE_VOICES.match(tok)
    if m:
        inner = ";".join(normalize_track_text(voice, style) for voice in split_voices(m.group(1)))
        return "{" + inner + "}"
    m = RE_REPEAT_GROUP.match(tok)
    if m:
        return f"{m.group(1)}(" + normalize_track_text(m.group(2), style) + ")"
    m = _BLOCK.match(tok)
    if m:
        return f"{m.group(1)}[" + normalize_track_text(m.group(2), style) + "]" + m.group(3)
    return _plain(tok, style)


def normalize_track_text(text: str, style: str) -> str:
    """Il testo di una traccia, di un pattern o di un box con le alterazioni
    scritte nello stile 'symbols' o 'ascii'; impaginazione e commenti come
    prima."""
    check_style(style)
    if style == "symbols" and "#" not in text and "b" not in text.lower() and "♯" not in text:
        return text
    # i token come sono scritti (con '♯'): tokenize_spans li da' gia' con '#'
    out, pos = [], 0
    for tok, start, end in _tokenize_spans_raw(text):
        out.append(text[pos:start])
        out.append(_token(tok, style))
        pos = end
    out.append(text[pos:])
    return "".join(out)


def _key_header(line: str, style: str) -> str:
    """Una riga 'Tonalita: ...' (anche per battuta) con le alterazioni dello stile."""
    head, sep, value = line.partition(":")
    if RE_KEY_LIST_HDR.match(line.strip()):
        return head + sep + RE_BAR_KEY.sub(lambda m: m.group(0)[:-len(m.group(2))] + _key_value(m.group(2), style), value)
    return head + sep + re.sub(r"^(\s*)(\S+)", lambda m: m.group(1) + _key_value(m.group(2), style), value, count=1)


def _key_value(value: str, style: str) -> str:
    return _KEY_IN_HEADER.sub(lambda m: m.group(1) + _char(m.group(2), style) + m.group(3), value)


def normalize_accidentals(text: str, style: str = "symbols") -> str:
    """Il testo di un brano (un file .st) con le alterazioni di note, accordi
    e tonalita' scritte con i simboli ('symbols': ♭ ♯) o con le lettere
    ('ascii': b #). Il brano suona uguale; la riga 'ST:' non cambia (vedi
    language_version). Commenti, testi cantati, nomi e le altre
    intestazioni restano come sono."""
    check_style(style)
    from .song import _notation_blocks
    lines = text.split("\n")
    out = list(lines)
    for i, line in enumerate(lines):
        if RE_KEY.match(line.strip()) and not line.startswith((" ", "\t")):
            out[i] = _key_header(line, style)
    for _kind, _name, start, end in _notation_blocks(lines):
        if end > start:
            out[start:end] = normalize_track_text("\n".join(lines[start:end]), style).split("\n")
    return "\n".join(out)


def _body_texts(text: str) -> List[str]:
    from .song import _notation_blocks
    lines = text.split("\n")
    return ["\n".join(lines[start:end]) for _k, _n, start, end in _notation_blocks(lines) if end > start]


def _plain_tokens(text: str):
    """I token semplici di un testo in notazione, anche dentro blocchi,
    gruppi e voci (ma non i testi cantati)."""
    for tok, _start, _end in tokenize_spans(text):
        if tok[:1] in (LYRIC_QUOTE, "%", "&") or tok.startswith('$"'):
            continue
        m = RE_VOICES.match(tok)
        if m:
            for voice in split_voices(m.group(1)):
                yield from _plain_tokens(voice)
            continue
        m = RE_REPEAT_GROUP.match(tok) or _BLOCK.match(tok)
        if m:
            yield from _plain_tokens(m.group(2))
            continue
        yield tok


def language_version(text: str) -> Optional[Tuple[int, int]]:
    """(2, 13) se il testo di un brano (o di una traccia) usa qualcosa che i
    lettori della 2.12 non conoscono: il simbolo '♯' o le abbreviazioni delle
    percussioni; altrimenti None. Chi salva un file dichiara con la riga
    'ST: 2.13' che servono."""
    bodies = _body_texts(text) or [text]
    for body in bodies + [line for line in text.split("\n") if RE_KEY.match(line.strip())]:
        if "♯" in body:
            return (2, 13)
        try:
            for tok in _plain_tokens(body):
                if re.sub(r"^\d+", "", split_note_value(tok)[0]) in PERCUSSION_ALIASES:
                    return (2, 13)
        except Exception:
            continue
    return None


def declare_language_version(text: str) -> str:
    """Il testo di un brano con la riga 'ST:' al numero che serve: 'ST: 2.13'
    se usa il simbolo '♯' o le abbreviazioni delle percussioni (vedi
    language_version) e dichiara una versione piu' vecchia, o nessuna.
    Altrimenti com'e'."""
    needed = language_version(text)
    if needed is None:
        return text
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = RE_ST_VERSION.match(line.strip())
        if m:
            if (int(m.group(1)), int(m.group(2))) < needed:
                lines[i] = "ST: %d.%d" % needed
            return "\n".join(lines)
    return ("ST: %d.%d\n" % needed) + text
