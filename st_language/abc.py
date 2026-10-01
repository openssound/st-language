"""
Esportazione del progetto in notazione ABC (standard 2.1), il formato di
testo per partiture usato da abcjs, EasyABC, abcm2ps, abc2midi e dalle
grandi raccolte di musica tradizionale.

Lavora sugli stessi attacchi dell'esportazione MusicXML (st_language.
musicxml): note, accordi gia' risolti dal motore di voicing, blocchi,
percussioni, battute, tuplet, legature fra battute. Ogni pentagramma di
ogni traccia diventa una voce ABC (V:), e le voci dei blocchi { ; } voci
in piu' sullo stesso pentagramma, raggruppate con %%score: pianoforti e
organi hanno due pentagrammi uniti da una graffa. Lo strumento passa con
%%MIDI program (la batteria sul canale 10, con le note dei suoni GM), la
tonalita' con K:, la metrica con M: e i cambi [M:] in tutte le voci, il
tempo con Q: e [Q:], le sigle degli accordi fra virgolette, le dinamiche
come decorazioni (!mf!), il testo cantato con w:. Il pedale del sustain
non c'e' (non e' nello standard).
Chitarre e bassi usano la chiave all'ottava bassa (treble-8, bass-8),
con le note scritte un'ottava sopra come vuole lo standard.
"""

import dataclasses
from fractions import Fraction
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from .instruments import PERCUSSION_MAP
from .musicxml import (QUANT_GRID, _Direction, _Entry, _Item, _clefs, _drop_repeated_harmonies,
                       _dynamic_changes, _frac, _grid_divisions, _mark_lyrics, _measures, _monophonic,
                       _spell_midi, _staff_entries, _track_items, key_fifths)

if TYPE_CHECKING:          # solo per le annotazioni (nessun import circolare)
    from .song import Part, Song  # noqa: F401

# Unita' di nota (L:) in quarti: l'ottavo, la piu' comune.
UNIT = Fraction(1, 2)
BARS_PER_LINE = 4
DRUM_CHANNEL = 10

_SHARP_ORDER = "FCGDAEB"
_MAJOR_NAMES = {-7: "Cb", -6: "Gb", -5: "Db", -4: "Ab", -3: "Eb", -2: "Bb", -1: "F", 0: "C",
                1: "G", 2: "D", 3: "A", 4: "E", 5: "B", 6: "F#", 7: "C#"}
_MINOR_NAMES = {-7: "Abm", -6: "Ebm", -5: "Bbm", -4: "Fm", -3: "Cm", -2: "Gm", -1: "Dm", 0: "Am",
                1: "Em", 2: "Bm", 3: "F#m", 4: "C#m", 5: "G#m", 6: "D#m", 7: "A#m"}
_ARTICULATIONS = {"staccato": ".", "mute": "!wedge!", "legato": "!tenuto!"}


def key_name(key: str) -> str:
    """La tonalita' del progetto come valore di K: ('C', 'Am', 'Bb', 'F#m')."""
    found = key_fifths(key)
    if not found:
        return "C"
    fifths, mode = found
    return (_MINOR_NAMES if mode == "minor" else _MAJOR_NAMES)[fifths]


def key_alters(fifths: int) -> Dict[str, int]:
    """Alterazione in chiave di ogni nota (lettera maiuscola -> -1/0/+1)."""
    alters = {step: 0 for step in "ABCDEFG"}
    for step in (_SHARP_ORDER[:fifths] if fifths > 0 else _SHARP_ORDER[::-1][:-fifths]):
        alters[step] = 1 if fifths > 0 else -1
    return alters


def length_suffix(units: Fraction) -> str:
    """Il moltiplicatore di durata ABC ('', '2', '3/2', '/2', '/4')."""
    if units == 1:
        return ""
    if units.denominator == 1:
        return str(units.numerator)
    if units.numerator == 1:
        return "/" if units.denominator == 2 else f"/{units.denominator}"
    return f"{units.numerator}/{units.denominator}"


def pitch_text(step: str, alter: int, octave: int, bar_alters: Dict[str, int],
               signature: Dict[str, int]) -> str:
    """Una nota ABC: l'alterazione solo se diversa da quella in vigore
    (armatura, o alterazione precedente nella battuta: per lo standard vale
    per quella nota in tutte le ottave, %%propagate-accidentals pitch)."""
    current = bar_alters.get(step, signature[step])
    accidental = ""
    if alter != current:
        accidental = {2: "^^", 1: "^", 0: "=", -1: "_", -2: "__"}[alter]
        bar_alters[step] = alter
    if octave >= 5:
        return accidental + step.lower() + "'" * (octave - 5)
    return accidental + step + "," * (4 - octave)


def chord_symbol(symbol: str, bass: Optional[str]) -> str:
    text = symbol.replace("♭", "b")
    if len(text) > 1 and text[1] == "-":
        text = text[0] + "b" + text[2:]
    if bass:
        text += "/" + bass.replace("♭", "b").replace("-", "b")
    return '"' + text.replace('"', "") + '"'


def _drum_items(items: List[_Item]) -> List[_Item]:
    """I colpi di batteria come note: la nota GM del suono (canale 10)."""
    out = []
    for item in items:
        pitches = sorted({PERCUSSION_MAP.get(d, 38) for d in item.drums})
        out.append(dataclasses.replace(item, pitches=[_spell_midi(p, False) for p in pitches], drums=[]))
    return out


def _clef_text(sign: str, octave_change: int) -> str:
    if sign == "percussion":
        return "perc"
    name = "treble" if sign == "G" else "bass"
    return name + ("-8" if octave_change < 0 else "+8" if octave_change > 0 else "")


def _lyric_syllable(entry: _Entry) -> str:
    """La sillaba w: di una nota: '*' senza testo, '_' per la nota legata
    che prosegue (lo standard le conta come note distinte)."""
    if not entry.first_of_item:
        return "_ "
    syllable = entry.item.lyric
    if not syllable:
        return "* "
    if syllable == "_":
        return "_ "
    text = syllable.replace(" ", "~").replace("*", "\\*")
    return text if text.endswith("-") and len(text) > 1 else text + " "


class _Voice:
    def __init__(self, vid: str, name: str, clef: str, program: Optional[int], drums: bool,
                 items: List[_Item], first: bool, transpose: int):
        self.vid = vid
        self.name = name
        self.clef = clef
        self.program = program
        self.drums = drums
        self.items = items
        self.first = first              # prima voce del pentagramma (pause visibili)
        self.transpose = transpose      # semitoni fra suono e scrittura (chiave all'ottava)
        self.directions: List[_Direction] = []
        self.has_lyrics = any(i.lyric for i in items)


def _entry_text(entry: _Entry, voice: _Voice, bar_alters, signature) -> str:
    units = entry.duration / UNIT
    if entry.tuplet:
        actual, normal = entry.tuplet
        units = units * actual / normal
    out = "".join(entry.directions)
    if entry.item is None:
        rest = "z" if voice.first else "x"
        return out + rest + length_suffix(units)
    if entry.first_of_item and entry.item.articulation in _ARTICULATIONS:
        out += _ARTICULATIONS[entry.item.articulation]
    notes = [pitch_text(p.step, p.alter, p.octave + voice.transpose // 12, bar_alters, signature)
             for p in entry.item.pitches]
    body = notes[0] if len(notes) == 1 else "[" + "".join(notes) + "]"
    return out + body + length_suffix(units) + ("-" if entry.tie_start else "")


def _measure_text(entries: List[_Entry], voice: _Voice, signature) -> Tuple[str, List[str]]:
    """La battuta di una voce e le sue sillabe."""
    parts: List[str] = []
    syllables: List[str] = []
    bar_alters: Dict[str, int] = {}
    in_tuplet = False
    for i, entry in enumerate(entries):
        if entry.tuplet_mark == "start":
            count = next(k for k, e in enumerate(entries[i:]) if e.tuplet_mark == "stop") + 1
            actual, normal = entry.tuplet
            parts.append(f"({actual}:{normal}:{count}")
            in_tuplet = True
        elif entry.tuplet and not in_tuplet:
            # tuplet isolata (una nota sola, es. una pausa di terzina)
            actual, normal = entry.tuplet
            parts.append(f"({actual}:{normal}:1")
        text = _entry_text(entry, voice, bar_alters, signature)
        if entry.tuplet_mark == "stop":
            in_tuplet = False
        joined = entry.beam in ("begin", "continue")
        parts.append(text + ("" if joined else " "))
        if entry.item is not None and voice.has_lyrics:
            syllables.append(_lyric_syllable(entry))
    return "".join(parts).rstrip(), syllables


def project_to_abc(project: "Song", only_audible: bool = True,
                   tracks: Optional[List["Part"]] = None, midi_dir: Optional[str] = None) -> str:
    """Il progetto come brano ABC (X:1), una voce per pentagramma."""
    from .timing import build_metrica_beat_map, build_tempo_beat_map

    if tracks is None:
        tracks = project.audible_tracks() if only_audible else project.tracks
    tracks = [t for t in tracks if not t.is_audio]
    events_by_track = {t.name: t.parsed_events(project.patterns, midi_dir=midi_dir) for t in tracks}
    key = key_fifths(project.key)
    flats = bool(key and key[0] < 0)
    signature = key_alters(key[0] if key else 0)

    grid = None
    for _attempt in range(2):
        parsed = {t.name: _track_items(events_by_track[t.name], t.instrument, flats, grid) for t in tracks}
        tempo_map = [(_frac(b, grid), bpm) for b, bpm in
                     build_tempo_beat_map(project, tracks=tracks, events_by_track=events_by_track)]
        end = max([i.end for items, _ in parsed.values() for i in items] + [Fraction(0)])
        measures = _measures(build_metrica_beat_map(project), end)
        times = [m[0] for m in measures] + [t for t, _ in tempo_map]
        for items, pedals in parsed.values():
            times += [i.start for i in items] + [i.end for i in items] + [t for t, _ in pedals]
        if _grid_divisions(times):
            break
        grid = QUANT_GRID

    voices: List[_Voice] = []
    score: List[str] = []
    for n, track in enumerate(tracks, 1):
        items, _pedals = parsed[track.name]   # il pedale non e' nello standard ABC 2.1
        _drop_repeated_harmonies(items)
        instrument = track.instrument
        drums = instrument.is_percussion
        clefs = _clefs(track, items)
        if drums:
            items = _drum_items(items)
        if len(clefs) == 2:
            upper = [dataclasses.replace(i, pitches=[p for p in i.pitches if p.midi >= 60])
                     for i in items if any(p.midi >= 60 for p in i.pitches)]
            lower = [dataclasses.replace(i, pitches=[p for p in i.pitches if p.midi < 60], harmony=None,
                                         lyric=i.lyric if not any(p.midi >= 60 for p in i.pitches) else None)
                     for i in items if any(p.midi < 60 for p in i.pitches)]
            staff_items = [upper, lower]
        else:
            staff_items = [items]

        directions: List[_Direction] = []
        if n == 1:
            directions += [_Direction(t, f"[Q:1/4={bpm}]") for t, bpm in tempo_map if t > 0]
        directions += [_Direction(i.start, chord_symbol(*i.harmony)) for i in items if i.harmony]
        if not drums:
            first_voice = min((i.voice for i in items), default=1)
            directions += [_Direction(t, f"!{mark}!") for t, mark in
                           _dynamic_changes(_monophonic([i for i in items if i.voice == first_voice]))]
        merged: Dict[Fraction, str] = {}
        for d in sorted(directions, key=lambda d: (d.time, not d.xml.startswith("["))):
            merged[d.time] = merged.get(d.time, "") + d.xml
        directions = [_Direction(t, text) for t, text in sorted(merged.items())]

        staves = []
        for s, s_items in enumerate(staff_items):
            by_voice: Dict[int, List[_Item]] = {}
            for item in s_items:
                by_voice.setdefault(item.voice, []).append(item)
            sign, _line, octave_change = clefs[s]
            ids = []
            for k, (_v, v_items) in enumerate(sorted(by_voice.items()) or [(1, [])]):
                v_items = _monophonic(v_items)
                _mark_lyrics(v_items)
                vid = f"T{n}" + ("" if s == 0 else "b") + ("" if k == 0 else f"v{k + 1}")
                name = track.name if s == 0 and k == 0 else ""
                voice = _Voice(vid, name, _clef_text(sign, octave_change), instrument.gm_program,
                               drums, v_items, k == 0, -12 * octave_change)
                if s == 0 and k == 0:
                    voice.directions = directions
                voices.append(voice)
                ids.append(vid)
            staves.append(ids[0] if len(ids) == 1 else "(" + " ".join(ids) + ")")
        score.append(staves[0] if len(staves) == 1 else "{" + " | ".join(staves) + "}")

    first_sig = f"{measures[0][2]}/{measures[0][3]}"
    bpm = tempo_map[0][1] if tempo_map and tempo_map[0][0] == 0 else round(project.tempo_bpm)
    out = ["X:1", f"T:{project.name}", f"M:{first_sig}", "L:1/8", f"Q:1/4={bpm}"]
    if len(voices) > 1:
        out.append("%%score " + " ".join(score))
    for voice in voices:
        line = f"V:{voice.vid} clef={voice.clef}"
        if voice.name:
            line += ' name="' + voice.name.replace('"', "'") + '"'
        out.append(line)
    out.append(f"K:{key_name(project.key)}")

    for voice in voices:
        out.append(f"V:{voice.vid}")
        out.append(f"%%MIDI channel {DRUM_CHANNEL}" if voice.drums else f"%%MIDI program {voice.program}")
        line: List[str] = []
        syllables: List[str] = []
        previous_sig = (measures[0][2], measures[0][3])
        for number, (m_start, m_len, num, den) in enumerate(measures, 1):
            entries = _staff_entries(voice.items, voice.directions, m_start, m_len, num, den)
            text, bar_syllables = _measure_text(entries, voice, signature)
            if (num, den) != previous_sig:
                text = f"[M:{num}/{den}] " + text
                previous_sig = (num, den)
            line.append(text + (" |]" if number == len(measures) else " |"))
            syllables += bar_syllables
            if number % BARS_PER_LINE == 0 or number == len(measures):
                out.append(" ".join(line))
                if voice.has_lyrics:
                    # sempre una riga w: (anche vuota): per lo standard la
                    # successiva si allinea dopo le note di questa
                    words = "".join(syllables).split(" ")
                    while words and words[-1] in ("*", ""):
                        words.pop()
                    out.append(("w: " + " ".join(words)).rstrip())
                line, syllables = [], []
    return "\n".join(out) + "\n"


def export_project_to_abc(project: "Song", path: str, only_audible: bool = True,
                          tracks: Optional[List["Part"]] = None, midi_dir: Optional[str] = None) -> str:
    """Scrive in path il brano ABC del progetto (vedi project_to_abc): le
    stesse tracce dell'esportazione MIDI e MusicXML."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(project_to_abc(project, only_audible=only_audible, tracks=tracks, midi_dir=midi_dir))
    return path
