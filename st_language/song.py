"""
Un brano ST: piu' tracce (parti) con strumento, pattern, tempo, metrica e
tonalita', letto da un file di progetto .st (vedi la specifica, "Formato
dei file") o costruito in codice.

    song = load_song("brano.st")
    song = song_from_notation("4: c d e f", instrument="Piano")
    song = Song(name="Prova")
    song.add_track("Basso", "Bass", "4: c*2 g*1 2c*2")

Della forma completa dei file .st di SoundText il lettore usa quello che
riguarda la musica scritta (intestazioni, pattern, tracce, box, strumenti,
mute/solo/volume/pan del mixer) e salta il resto (effetti, plugin, clip
audio, riverbero), che e' proprio dell'applicazione.
"""

import os
import re
import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .instruments import DEFAULT_INSTRUMENTS, InstrumentProfile, instrument_for
from ._i18n import tr
from .notation import Event, Meter, NotationError, Pattern, COMMENT_MARK, parse_track_text, tokenize
from .stfile import (
    RE_AMBIENTE, RE_AUDIO_HDR, RE_BOX_HDR, RE_EFFECTS_HDR, RE_INSTRUMENT_HDR, RE_KEY, RE_MASTER,
    RE_MASTER_CHAIN_HDR, RE_METRICA, RE_METRICA_LIST_HDR, RE_MIXER_HDR, RE_PATTERN_HDR, RE_SYNTH_HDR,
    RE_TEMPO, RE_TEMPO_LIST_HDR, RE_TRACK_HDR, RE_TRACK_HDR_EXPLICIT, short_track_header,
    RE_PICKUP, RE_ST_VERSION, LANGUAGE_VERSION, parse_pickup, instrument_blocks,
    _extract_box_blocks, _extract_named_blocks, _parse_bar_value_list, _parse_instrument_body,
    _parse_mixer_body,
)

AUDIO_INSTRUMENT_NAME = "Audio"     # tracce audio di SoundText: senza notazione, saltate


@dataclass
class Clip:
    """Un box della vista a box: un pezzo di testo che comincia a start_beat."""
    name: str
    text: str
    start_beat: float = 0.0


@dataclass
class Part:
    """Una traccia: nome, strumento e testo in notazione ST."""
    name: str
    instrument: InstrumentProfile
    text: str = ""
    mute: bool = False
    solo: bool = False
    volume: int = 100          # 0-200, 100 = velocity invariata
    pan: int = 64              # 0-127, 64 = centro
    clips: List[Clip] = field(default_factory=list)
    is_audio: bool = False

    @property
    def instrument_name(self) -> str:
        return self.instrument.name

    def parsed_events(self, patterns: Dict[str, Pattern], midi_dir: Optional[str] = None,
                      meter: Optional[Meter] = None) -> List[Event]:
        return parse_track_text(self.text, patterns, default_octave=self.instrument.default_octave,
                                midi_dir=midi_dir, meter=meter)


@dataclass
class Song:
    name: str = "ST"
    tempo_bpm: int = 120
    time_sig: str = "4/4"
    key: str = ""
    tempo_changes: List[tuple] = field(default_factory=list)      # [(battuta, bpm)]
    metrica_changes: List[tuple] = field(default_factory=list)    # [(battuta, "N/D")]
    patterns: Dict[str, Pattern] = field(default_factory=dict)
    tracks: List[Part] = field(default_factory=list)
    instruments: Dict[str, InstrumentProfile] = field(default_factory=dict)   # dichiarati nel file
    pickup: float = 0.0                    # battuta in levare, in quarti (Levare:)
    st_version: Optional[tuple] = None     # versione dichiarata dal file (ST: 2.6), se c'e'

    def instrument(self, name: str) -> InstrumentProfile:
        return instrument_for(name, known={**DEFAULT_INSTRUMENTS, **self.instruments})

    def meter(self) -> Meter:
        """Dove cominciano le battute del brano (per le ancore bar=N)."""
        return Meter(self.time_sig, self.metrica_changes, self.pickup)

    def add_track(self, name: str, instrument="Piano", text: str = "") -> Part:
        profile = instrument if isinstance(instrument, InstrumentProfile) else self.instrument(instrument)
        part = Part(name=name, instrument=profile, text=text)
        self.tracks.append(part)
        return part

    def add_pattern(self, name: str, body: str) -> Pattern:
        self.patterns[name] = Pattern(name=name, tokens=tokenize(body))
        return self.patterns[name]

    def get_track(self, name: str) -> Part:
        for t in self.tracks:
            if t.name == name:
                return t
        raise KeyError(name)

    def audible_tracks(self) -> List[Part]:
        """Solo e Mute come in un mixer: con almeno una traccia in Solo
        suonano solo quelle (non in Mute)."""
        any_solo = any(t.solo for t in self.tracks)
        return [t for t in self.tracks if not t.mute and (t.solo or not any_solo)]

    def duration_beats(self, only_audible: bool = True) -> float:
        tracks = self.audible_tracks() if only_audible else self.tracks
        meter = self.meter()
        end = 0.0
        for t in tracks:
            if t.is_audio:
                continue
            for ev in t.parsed_events(self.patterns, meter=meter):
                end = max(end, ev.start + ev.duration)
        return end


# Grigliato usato per riempire i vuoti tra un box e il successivo: 1/16
# (4.0/16 = 0.25 beat), abbastanza fine da rappresentare esattamente
# qualunque posizione a cui il canvas puo' agganciare l'inizio di un box.
FILL_GRID_BEATS = 0.25


_FILL_GRID_TOKEN = "16:"


# Ogni box e' autosufficiente come il corpo di un Pattern: non deve
# ereditare lo stato lasciato dal riempimento del vuoto o dal box
# precedente. 'reset:' riporta tutto allo stato iniziale (griglia, velocity,
# swing, spostamento, trasposizione, modo delle altezze, tonalita'), anche
# per i comandi di stato che verranno.
_DEFAULT_STATE_PREFIX = "reset: "


def clip_duration_beats(text: str, patterns: Dict[str, Pattern], default_octave: int,
                        start_beat: float = 0.0, meter: Optional[Meter] = None) -> float:
    """Durata in beat del testo di un box, per la larghezza del box nel
    canvas e per rilevare sovrapposizioni. Stesso pattern di
    Song.duration_beats. 'start_beat' e 'meter' dicono dove il box comincia
    nel brano: servono alle ancore bar=N, che riempiono fino a una battuta
    assoluta. Un box che non si riesce a leggere (per esempio un &MIDI che
    manca su questo computer) dura 0: l'errore lo segnala chi suona o
    controlla la traccia, ma il brano si apre lo stesso."""
    try:
        events = parse_track_text(text, patterns, default_octave=default_octave,
                                  meter=meter, origin_beat=start_beat)
    except (NotationError, ValueError):
        return 0.0
    if not events:
        return 0.0
    return max(e.start + e.duration for e in events)


def flatten_clips_to_text(clips: List["Clip"], patterns: Dict[str, Pattern], default_octave: int,
                           fill_grid_beats: float = FILL_GRID_BEATS,
                           meter: Optional[Meter] = None) -> str:
    """Appiattisce i box di una traccia (ordinati per start_beat) in un
    unico testo st-language lineare, riempiendo gli eventuali vuoti con
    pause esatte. E' il valore che va salvato in Track.text quando
    Track.clips e' popolata, cosi' playback/export/validazione continuano a
    funzionare senza alcuna modifica."""
    if not clips:
        return ""
    ordered = sorted(clips, key=lambda c: c.start_beat)
    prefix = _DEFAULT_STATE_PREFIX
    parts: List[str] = []
    cursor = 0.0
    for clip in ordered:
        gap = clip.start_beat - cursor
        if gap > 1e-9:
            n = round(gap / fill_grid_beats)
            if n > 0:
                parts.append(f"{_FILL_GRID_TOKEN} {n}r")
                cursor += n * fill_grid_beats
        body = clip.text.strip()
        if COMMENT_MARK in body:
            body += "\n"   # un commento in fondo al box non deve inghiottire il box dopo
        parts.append(prefix + body)
        # Il box comincia dove lo porta il testo (cursor), che e' il suo
        # start_beat salvo sovrapposizioni.
        cursor += clip_duration_beats(clip.text, patterns, default_octave, start_beat=cursor, meter=meter)
    return " ".join(p for p in parts if p)


def song_from_notation(text: str, instrument: str = "Piano", name: str = "ST",
                       tempo_bpm: int = 120, time_sig: str = "4/4") -> Song:
    """Un brano di una sola traccia da un testo in notazione."""
    song = Song(name=name, tempo_bpm=tempo_bpm, time_sig=time_sig)
    song.add_track(instrument, instrument, text)
    return song


def _instrument_names(song: Song) -> set:
    return set(DEFAULT_INSTRUMENTS) | set(song.instruments)


def read_song(text: str, name: str = "ST") -> Song:
    """Il brano descritto da un file di progetto .st (vedi la specifica)."""
    lines = text.splitlines()
    song = Song(name=name)
    for inst_name, body in instrument_blocks(lines):
        song.instruments[inst_name] = _parse_instrument_body(inst_name, body)
    mixers = {n: _parse_mixer_body(body) for n, body in _extract_named_blocks(lines, RE_MIXER_HDR)}

    mode = None
    current_name = current_instrument = None
    buffer: List[str] = []

    def flush():
        nonlocal mode, current_name, current_instrument, buffer
        body = ("\n" if mode in ("track", "pattern") else " ").join(buffer).strip()
        if mode == "pattern" and current_name:
            song.add_pattern(current_name, body)
        elif mode == "track" and current_name:
            if current_instrument == AUDIO_INSTRUMENT_NAME:
                part = Part(current_name, InstrumentProfile(name=AUDIO_INSTRUMENT_NAME, gm_program=0),
                            is_audio=True)
                song.tracks.append(part)
            else:
                part = song.add_track(current_name, current_instrument, body)
            for key, value in mixers.get(current_name, {}).items():
                if hasattr(part, key):
                    setattr(part, key, value)
        mode, current_name, current_instrument, buffer = None, None, None, []

    skip_headers = (RE_MIXER_HDR, RE_EFFECTS_HDR, RE_MASTER_CHAIN_HDR, RE_SYNTH_HDR, RE_INSTRUMENT_HDR,
                    RE_BOX_HDR, RE_AUDIO_HDR)
    for raw_line in lines:
        line = raw_line.strip()
        if line == "":
            if mode:
                flush()
            continue
        m = RE_ST_VERSION.match(line)
        if m:
            if mode:
                flush()
            song.st_version = (int(m.group(1)), int(m.group(2)))
            if song.st_version > LANGUAGE_VERSION:
                warnings.warn(tr("Il file e' scritto con ST {0}.{1}, questa libreria conosce la {2}.{3}: "
                                 "qualcosa potrebbe non essere letto", *song.st_version, *LANGUAGE_VERSION))
            continue
        m = RE_PICKUP.match(line)
        if m:
            if mode:
                flush()
            song.pickup = parse_pickup(m.group(1))
            continue
        m = RE_TEMPO_LIST_HDR.match(line)
        if m:
            if mode:
                flush()
            song.tempo_changes = _parse_bar_value_list(m.group(1))
            first = next((v for b, v in song.tempo_changes if b == 1), None)
            song.tempo_bpm = first if first is not None else song.tempo_changes[0][1]
            continue
        m = RE_TEMPO.match(line)
        if m:
            if mode:
                flush()
            song.tempo_bpm = int(m.group(1))
            continue
        m = RE_METRICA_LIST_HDR.match(line)
        if m:
            if mode:
                flush()
            song.metrica_changes = _parse_bar_value_list(m.group(1), is_metrica=True)
            first = next((v for b, v in song.metrica_changes if b == 1), None)
            song.time_sig = first if first is not None else song.metrica_changes[0][1]
            continue
        m = RE_METRICA.match(line)
        if m:
            if mode:
                flush()
            song.time_sig = m.group(1)
            continue
        m = RE_KEY.match(line)
        if m:
            if mode:
                flush()
            song.key = m.group(1).strip()
            continue
        if RE_MASTER.match(line) or RE_AMBIENTE.match(line):
            if mode:
                flush()
            continue
        m = RE_PATTERN_HDR.match(line)
        if m:
            if mode:
                flush()
            mode, current_name = "pattern", m.group(1)
            continue
        if any(rx.match(line) for rx in skip_headers):
            if mode:
                flush()
            mode, current_name = "skip", None       # letti a parte, o propri di SoundText
            continue
        m = RE_TRACK_HDR_EXPLICIT.match(line)
        if m:
            if mode:
                flush()
            current_name, current_instrument, mode = m.group(1).strip(), m.group(2), "track"
            continue
        header = short_track_header(line, _instrument_names(song))
        if header:
            if mode:
                flush()
            instr, idx = header
            current_name = f"{instr} {idx}".strip() if idx else instr
            current_instrument, mode = instr, "track"
            continue
        if mode:
            buffer.append(line)
    if mode:
        flush()

    for track_name, box_name, start_beat, body in _extract_box_blocks(lines):
        try:
            part = song.get_track(track_name)
        except KeyError:
            continue
        if not part.is_audio:
            part.clips.append(Clip(box_name, body, start_beat))
    for part in song.tracks:
        if part.clips:
            part.text = flatten_clips_to_text(part.clips, song.patterns, part.instrument.default_octave,
                                              meter=song.meter())
    return song


def load_song(path: str, instrument: str = "Piano") -> Song:
    """Un file .st, oppure un file di sola notazione (una traccia con
    questo strumento) se non contiene tracce."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return text_to_song(text, os.path.splitext(os.path.basename(path))[0], instrument)


def text_to_song(text: str, name: str = "ST", instrument: str = "Piano") -> Song:
    """read_song, o un brano di una traccia se il testo non ha tracce."""
    song = read_song(text, name=name)
    if not song.tracks:
        song = song_from_notation(text, instrument=instrument, name=name)
    return song
