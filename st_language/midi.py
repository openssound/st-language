"""
Esportazione di un brano ST in un file MIDI standard (Standard MIDI File,
formato 1), senza librerie esterne: una traccia MIDI per traccia ST piu'
quella del tempo e della metrica.

    from st_language.song import load_song
    from st_language.midi import song_to_midi
    song_to_midi(load_song("brano.st"), "brano.mid")

Accordi scritti col voicing dello strumento, blocchi, percussioni sul
canale 10, dinamiche e rampe come velocity, articolazioni (staccato, mute,
legato) come durata udibile, pedale (CC64), slide come pitch bend,
automazioni (vol=, expr=, pan=, mod=, rev=, cho= e le forcelle) come
control change, tempo e metrica (anche i cambi), testo cantato come
eventi "lyrics".

Le funzioni che decidono note e canali sono le stesse dell'esportazione
di SoundText (core.midi_export), che aggiunge il mixaggio dell'app
(volume master, umanizzazione, mandate degli effetti).
"""

import struct
from typing import List, Optional, Tuple, TYPE_CHECKING

from .chords import apply_bass_note, parse_chord_symbol, pitch_to_midi, voice_chord
from .instruments import DRUM_MIDI_CHANNEL, PERCUSSION_MAP, InstrumentProfile
from .notation import RAMP_CURVES, Event, swing_time
from .timing import RE_METRICA_VALUE, build_metrica_beat_map, build_tempo_beat_map

if TYPE_CHECKING:          # solo per le annotazioni (nessun import circolare)
    from .song import Part, Song  # noqa: F401

TICKS_PER_BEAT = 480


# Ampiezza (in semitoni) del pitch bend impostata via RPN sui canali che
# contengono almeno uno slide/portamento (c*4>d*4): abbastanza ampia da
# coprire slide di piu' di un'ottava mantenendo comunque precisione utile.
SLIDE_PITCH_BEND_RANGE_SEMITONES = 24


def _resolve_event_notes(ev: Event, instrument: InstrumentProfile) -> Tuple[List[int], int]:
    """Ritorna (lista note MIDI, velocity) per un evento gia' parsato,
    applicando il motore di voicing (SoundText Engine) quando necessario."""
    velocity = ev.velocity

    if ev.kind in ("rest", "sustain", "tempo_marker", "control"):
        return [], velocity

    if ev.kind == "note":
        return [pitch_to_midi(ev.letter, ev.octave)], velocity

    if ev.kind == "slide":
        return [pitch_to_midi(ev.letter, ev.octave)], velocity

    if ev.kind == "chord":
        chord = parse_chord_symbol(ev.symbol)
        notes = voice_chord(chord, ev.octave, instrument, voicing_override=ev.voicing)
        if ev.bass:
            notes = apply_bass_note(notes, ev.bass, ev.octave)
        return notes, velocity

    if ev.kind == "percussion":
        return [PERCUSSION_MAP[ev.name]], velocity

    if ev.kind == "block":
        notes = []
        for item in ev.items:
            if item["kind"] == "note":
                notes.append(pitch_to_midi(item["letter"], item["octave"]))
            elif item["kind"] == "chord":
                chord = parse_chord_symbol(item["symbol"])
                chord_notes = voice_chord(chord, item["octave"], instrument,
                                           voicing_override=item.get("voicing"))
                if item.get("bass"):
                    chord_notes = apply_bass_note(chord_notes, item["bass"], item["octave"])
                notes.extend(chord_notes)
            elif item["kind"] == "percussion":
                notes.append(PERCUSSION_MAP[item["name"]])
        return sorted(set(notes)), velocity

    return [], velocity


# Automazioni (eventi "control") -> numero del control change MIDI
CONTROL_CC = {"vol": 7, "expr": 11, "pan": 10, "mod": 1, "rev": 91, "cho": 93}
# Una rampa diventa al piu' tanti punti, uno ogni CONTROL_STEP_TICKS almeno
CONTROL_MAX_POINTS = 128
CONTROL_STEP_TICKS = 10


# Numero "di controller" dato da control_points al pitch bend (bend=), che
# non e' un control change: valore 0-16383, 8192 = nessun bend.
PITCH_BEND = -1


def control_number(name: str) -> int:
    """Il controller MIDI di un'automazione (cc74 -> 74), PITCH_BEND per bend."""
    if name == "bend":
        return PITCH_BEND
    return CONTROL_CC[name] if name in CONTROL_CC else int(name[2:])


def control_cc_value(name: str, value: float, volume_scale: float = 1.0) -> int:
    """Valore MIDI (0-127) di un'automazione: pan da -1..1 a 1..127 (0 =
    centro, 64); vol moltiplicato per volume_scale (il volume del mixer);
    bend in semitoni come pitch bend 0-16383."""
    if name == "bend":
        bend = round(value / SLIDE_PITCH_BEND_RANGE_SEMITONES * 8192)
        return max(0, min(16383, 8192 + bend))
    if name == "pan":
        raw = 64 + value * 63
    elif name == "vol":
        raw = value * volume_scale
    else:
        raw = value
    return max(0, min(127, round(raw)))


def control_points(ev: Event, volume_scale: float = 1.0, ticks_per_beat: int = TICKS_PER_BEAT
                   ) -> List[Tuple[float, int, int]]:
    """I control change di un evento "control" come (beat, controller,
    valore): un punto solo per un valore fisso, per una rampa i valori
    lungo la curva (senza ripetere valori uguali consecutivi)."""
    cc = control_number(ev.name)
    if ev.duration <= 0 or ev.start_value is None:
        return [(ev.start, cc, control_cc_value(ev.name, ev.value, volume_scale))]
    span = ev.duration * ticks_per_beat
    steps = max(1, min(CONTROL_MAX_POINTS, int(span // CONTROL_STEP_TICKS)))
    shape = RAMP_CURVES[ev.curve or "lin"]
    points, last = [], None
    for k in range(steps + 1):
        x = k / steps
        value = control_cc_value(ev.name, ev.start_value + (ev.value - ev.start_value) * shape(x),
                                 volume_scale)
        if value != last:
            points.append((ev.start + ev.duration * x, cc, value))
            last = value
    return points


_ARTICULATION_DURATION_FACTOR = {
    "staccato": 0.5,   # nota accorciata del 50%, il resto e' silenzio
    "mute": 0.15,      # nota "stoppata": molto breve
    "legato": 1.15,    # nota leggermente prolungata, per legare alla successiva
}


def effective_articulation(ev: Event) -> Optional[str]:
    """L'articolazione con cui suona l'evento: quella scritta, altrimenti
    legato per le note dentro una legatura di portamento (tranne l'ultima)."""
    if ev.articulation:
        return ev.articulation
    return "legato" if ev.slur in ("start", "continue") else None


def sounding_span(ev: Event) -> Tuple[float, float]:
    """(inizio, fine) in quarti con cui l'evento suona: con lo swing (vedi
    notation.swing_time) le note sulle seconde meta' delle coppie si spostano."""
    return swing_time(ev.start, ev.swing), swing_time(ev.start + ev.duration, ev.swing)


def needs_bend_range(events: List[Event]) -> bool:
    """Se il canale va preparato per il pitch bend (slide o bend=)."""
    return any(ev.kind == "slide" or (ev.kind == "control" and ev.name == "bend") for ev in events)


def _apply_articulation(start_tick: int, end_tick: int, articulation: Optional[str]) -> int:
    """Ritorna il tick di fine nota effettivo (udibile) tenendo conto del
    modificatore staccato/mute/legato; la durata 'di griglia' (start/end
    nominali) resta invariata ai fini dell'avanzamento della timeline."""
    if not articulation:
        return end_tick
    factor = _ARTICULATION_DURATION_FACTOR.get(articulation, 1.0)
    nominal = end_tick - start_tick
    new_len = max(1, round(nominal * factor))
    return start_tick + new_len


def _assign_channels(tracks: List["Part"]) -> dict:
    """Assegna un canale MIDI a ciascuna traccia; le percussioni usano
    sempre il canale riservato (10 nella numerazione 1-based / 9 in 0-based).

    Un file MIDI ha solo 15 canali melodici: finche' bastano, ogni traccia ha
    il suo. Con piu' tracce (es. un import con molte voci) si assegna prima un
    canale a ogni strumento DIVERSO (a parita' di volume e pan, altrimenti al
    solo strumento), poi i canali che avanzano vanno alle tracce extra nell'ordine
    in cui compaiono, e le restanti condividono il canale del proprio
    strumento. Su un canale c'e' infatti un solo programma (Program Change), un
    solo volume/pan e un solo stato di pitch bend: condividerlo fra strumenti
    diversi farebbe suonare una traccia con lo strumento dell'altra (es. le
    chitarre di un brano suonate come sax e pianoforte). Solo con
    piu' strumenti diversi che canali si ricade sul riuso ciclico,
    inevitabile."""
    channel_pool = [c for c in range(16) if c != DRUM_MIDI_CHANNEL]
    mapping = {}
    melodic = []
    for t in tracks:
        if t.instrument.is_percussion:
            mapping[t.name] = DRUM_MIDI_CHANNEL
        else:
            melodic.append(t)

    if len(melodic) <= len(channel_pool):
        for t, channel in zip(melodic, channel_pool):
            mapping[t.name] = channel
        return mapping

    for group_key in (lambda t: (t.instrument_name, t.volume, t.pan),
                      lambda t: t.instrument_name):
        groups = list(dict.fromkeys(group_key(t) for t in melodic))
        if len(groups) > len(channel_pool):
            continue
        primary = {g: channel_pool[i] for i, g in enumerate(groups)}
        spare = channel_pool[len(groups):]
        seen = set()
        for t in melodic:
            g = group_key(t)
            if g not in seen:
                seen.add(g)
                mapping[t.name] = primary[g]
            elif spare:
                mapping[t.name] = spare.pop(0)
            else:
                mapping[t.name] = primary[g]
        return mapping

    for i, t in enumerate(melodic):   # piu' strumenti diversi che canali
        mapping[t.name] = channel_pool[i % len(channel_pool)]
    return mapping


# --------------------------------------------------------------- testi

def midi_text_bytes(text: str) -> bytes:
    """I byte del testo di un evento MIDI: latin-1 se basta (quello che si
    aspettano i lettori karaoke), altrimenti UTF-8 (vedi midi_text)."""
    try:
        return text.encode("latin-1")
    except UnicodeEncodeError:
        return text.encode("utf-8")


def midi_text(text: str) -> str:
    """Il testo di un evento MIDI letto come latin-1 (come fanno mido e
    molti lettori): se erano byte UTF-8 lo si ricostruisce."""
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


# --------------------------------------------------------------- file MIDI

def _vlq(value: int) -> bytes:
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append(0x80 | (value & 0x7F))
        value >>= 7
    return bytes(reversed(out))


def _meta(kind: int, data: bytes) -> bytes:
    return bytes([0xFF, kind]) + _vlq(len(data)) + data


def write_smf(path: str, tracks: List[List[Tuple[int, int, bytes]]], ticks_per_beat: int = TICKS_PER_BEAT) -> None:
    """Scrive un MIDI formato 1: per traccia [(tick, priorita', messaggio)];
    a parita' di tick vanno prima le priorita' basse."""
    chunks = []
    for events in tracks:
        data = bytearray()
        now = 0
        for tick, _order, message in sorted(events, key=lambda e: (e[0], e[1])):
            data += _vlq(max(0, tick - now)) + message
            now = max(now, tick)
        data += _vlq(0) + _meta(0x2F, b"")
        chunks.append(b"MTrk" + struct.pack(">I", len(data)) + bytes(data))
    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), ticks_per_beat)
    with open(path, "wb") as f:
        f.write(header + b"".join(chunks))


# priorita' a parita' di tick: prima si spegne, poi controlli e testi, poi si accende
_OFF, _CTRL, _ON = 0, 1, 2


def _part_events(part, events: List[Event], channel: int) -> List[Tuple[int, int, bytes]]:
    instrument = part.instrument
    out: List[Tuple[int, int, bytes]] = [(0, _CTRL, _meta(0x03, midi_text_bytes(part.name)))]
    if instrument.is_percussion:
        out.append((0, _CTRL, bytes([0xB0 | channel, 0, 120])))
    out.append((0, _CTRL, bytes([0xC0 | channel, instrument.gm_program & 0x7F])))
    out.append((0, _CTRL, bytes([0xB0 | channel, 7, max(0, min(127, round(part.volume)))])))
    out.append((0, _CTRL, bytes([0xB0 | channel, 10, max(0, min(127, part.pan))])))
    if needs_bend_range(events):
        for control, value in ((101, 0), (100, 0), (6, SLIDE_PITCH_BEND_RANGE_SEMITONES), (38, 0),
                               (101, 127), (100, 127)):
            out.append((0, _CTRL, bytes([0xB0 | channel, control, value])))
    factor = max(0.0, part.volume / 100.0)
    sustain = False
    end_tick = 0

    def tick(beats: float) -> int:
        return round(beats * TICKS_PER_BEAT)

    for ev in events:
        start, end = (tick(b) for b in sounding_span(ev))
        end_tick = max(end_tick, end)
        if ev.lyric and ev.lyric != "_":
            text = ev.lyric[:-1] if ev.lyric.endswith("-") and len(ev.lyric) > 1 else ev.lyric + " "
            out.append((start, _CTRL, _meta(0x05, midi_text_bytes(text))))
        if ev.kind == "control":
            for beat, cc, value in control_points(ev, part.volume / 100.0):
                if cc == PITCH_BEND:
                    out.append((tick(beat), _CTRL, bytes([0xE0 | channel, value & 0x7F, value >> 7])))
                else:
                    out.append((tick(beat), _CTRL, bytes([0xB0 | channel, cc, value])))
            continue
        if ev.kind == "sustain":
            sustain = ev.name == "on"
            out.append((start, _CTRL, bytes([0xB0 | channel, 64, 127 if sustain else 0])))
            continue
        if ev.kind == "slide":
            first = pitch_to_midi(ev.letter, ev.octave)
            points = [first] + [pitch_to_midi(letter, octave) for letter, octave in ev.slide_points]
            points.append(points[-1])
            total = sum(ev.slide_segment_durations) or 1.0
            bounds, acc = [start], 0.0
            for seg in ev.slide_segment_durations:
                acc += seg
                bounds.append(start + round((end - start) * acc / total))
            for i in range(len(ev.slide_segment_durations)):
                a, b = bounds[i], bounds[i + 1]
                steps = max(2, min(16, b - a))
                for k in range(steps + 1):
                    offset = points[i] - first + (points[i + 1] - points[i]) * k / steps
                    bend = max(-8192, min(8191, round(offset / SLIDE_PITCH_BEND_RANGE_SEMITONES * 8192))) + 8192
                    out.append((a + round((b - a) * k / steps), _CTRL,
                                bytes([0xE0 | channel, bend & 0x7F, bend >> 7])))
            out.append((end, _CTRL, bytes([0xE0 | channel, 0, 0x40])))
            notes = [first]
        else:
            notes, _vel = _resolve_event_notes(ev, instrument)
        notes = [n for n in notes if 0 <= n <= 127]
        if not notes or factor <= 0:
            continue
        velocity = max(1, min(127, round(ev.velocity * factor)))
        stop = _apply_articulation(start, end, effective_articulation(ev))
        for n in notes:
            out.append((start, _ON, bytes([0x90 | channel, n, velocity])))
            out.append((stop, _OFF, bytes([0x80 | channel, n, 0])))
    if sustain:
        out.append((end_tick, _CTRL, bytes([0xB0 | channel, 64, 0])))
    return out


def song_to_midi(song, path: str, only_audible: bool = True, midi_dir: Optional[str] = None) -> str:
    """Scrive il brano (st_language.song.Song) come file MIDI; ritorna path.
    Con only_audible si rispettano Mute e Solo."""
    tracks = [t for t in (song.audible_tracks() if only_audible else song.tracks) if not t.is_audio]
    events_by_track = {t.name: t.parsed_events(song.patterns, midi_dir=midi_dir) for t in tracks}
    conductor: List[Tuple[int, int, bytes]] = [(0, _CTRL, _meta(0x03, midi_text_bytes(song.name)))]
    for beat, bpm in build_tempo_beat_map(song, tracks=tracks, events_by_track=events_by_track):
        tempo = round(60_000_000 / max(1, bpm))
        conductor.append((round(beat * TICKS_PER_BEAT), _CTRL, _meta(0x51, tempo.to_bytes(3, "big"))))
    for beat, sig in build_metrica_beat_map(song):
        m = RE_METRICA_VALUE.match(sig or "")
        if not m:
            continue
        num, den = int(m.group(1)), int(m.group(2))
        power = max(0, den.bit_length() - 1)
        conductor.append((round(beat * TICKS_PER_BEAT), _CTRL, _meta(0x58, bytes([num, power, 24, 8]))))
    channels = _assign_channels(tracks)
    midi_tracks = [conductor]
    for t in tracks:
        midi_tracks.append(_part_events(t, events_by_track[t.name], channels[t.name]))
    write_smf(path, midi_tracks)
    return path
