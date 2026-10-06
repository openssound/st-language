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

from .chords import apply_bass_note, parse_chord_symbol, pitch_to_midi, scale_pitch_classes, voice_chord
from .instruments import DRUM_MIDI_CHANNEL, PERCUSSION_MAP, InstrumentProfile
from .notation import RAMP_CURVES, Event, swing_time
from .timing import RE_METRICA_VALUE, build_metrica_beat_map, build_tempo_beat_map, fermata_spans, with_fermatas

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
# ... e all'accordatura (tune=), scritta come RPN 1 (Channel Fine Tuning):
# valore 0-16383, 8192 = nessuno scostamento, +-100 cent agli estremi.
TUNE = -2


def control_number(name: str) -> int:
    """Il controller MIDI di un'automazione (cc74 -> 74), PITCH_BEND per
    bend, TUNE per tune."""
    if name == "bend":
        return PITCH_BEND
    if name == "tune":
        return TUNE
    return CONTROL_CC[name] if name in CONTROL_CC else int(name[2:])


def control_cc_value(name: str, value: float, volume_scale: float = 1.0) -> int:
    """Valore MIDI (0-127) di un'automazione: pan da -1..1 a 1..127 (0 =
    centro, 64); vol moltiplicato per volume_scale (il volume del mixer);
    bend in semitoni come pitch bend 0-16383, tune in cent come RPN 1
    0-16383."""
    if name == "bend":
        bend = round(value / SLIDE_PITCH_BEND_RANGE_SEMITONES * 8192)
        return max(0, min(16383, 8192 + bend))
    if name == "tune":
        return max(0, min(16383, 8192 + round(value / 100 * 8192)))
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


def tune_controls(value: int) -> List[Tuple[int, int]]:
    """I control change (controller, valore) che scrivono l'accordatura fine
    (RPN 1) col valore 0-16383 di control_cc_value; alla fine si deseleziona
    l'RPN (127/127) perche' un Data Entry successivo non la cambi."""
    return [(101, 0), (100, 1), (6, value >> 7), (38, value & 0x7F), (101, 127), (100, 127)]


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


def shift_ticks(ev: Event, tempo_ticks: List[Tuple[int, float]], tick: int,
                ticks_per_beat: int = TICKS_PER_BEAT) -> int:
    """I tick di micro-timing dell'evento (shift=N millisecondi), col tempo
    in vigore a `tick` nella mappa [(tick, bpm)] ordinata."""
    if not ev.shift:
        return 0
    bpm = tempo_ticks[0][1] if tempo_ticks else 120
    for at, value in tempo_ticks:
        if at > tick:
            break
        bpm = value
    return round(ev.shift / 1000 * bpm / 60 * ticks_per_beat)


# Accenti: la nota suona piu' forte (la velocity scritta resta quella della
# dinamica, cosi' la partitura non scrive un cambio di dinamica).
DECORATION_VELOCITY_FACTOR = {"accent": 1.25, "marcato": 1.4}
# Durata di ciascuna nota di un abbellimento (trillo, mordente, gruppetto):
# una biscroma a 480 tick per quarto.
ORNAMENT_STEP_TICKS = 60


def decorated_velocity(ev: Event, velocity: int) -> int:
    """La velocity con gli accenti ($accent, $marcato) dell'evento."""
    for deco in ev.decorations or ():
        if deco in DECORATION_VELOCITY_FACTOR:
            velocity = round(velocity * DECORATION_VELOCITY_FACTOR[deco])
    return max(1, min(127, velocity))


def _scale_neighbour(note: int, step: int, key: Optional[str]) -> int:
    """La nota della scala della tonalita' (C se manca) subito sopra (step=1)
    o sotto (step=-1)."""
    try:
        scale = set(scale_pitch_classes(key or "C"))
    except ValueError:
        scale = set(scale_pitch_classes("C"))
    candidate = note + step
    while candidate % 12 not in scale and abs(candidate - note) < 3:
        candidate += step
    return max(0, min(127, candidate))


def ornament_spans(ev: Event, note: int, start: int, stop: int, key: Optional[str] = None
                   ) -> List[Tuple[int, int, int]]:
    """Le note (inizio, fine, altezza) con cui suona una nota singola con un
    abbellimento: $tr alterna la nota e quella sopra nella scala, $mordent fa
    nota-sotto-nota, $turn sopra-nota-sotto-nota; senza abbellimenti (o su
    accordi e blocchi) la nota cosi' com'e'."""
    decos = set(ev.decorations or ()) & {"tr", "mordent", "turn"}
    if ev.kind != "note" or not decos or stop - start < 3:
        return [(start, stop, note)]
    upper, lower = _scale_neighbour(note, 1, key), _scale_neighbour(note, -1, key)
    length = stop - start
    if "tr" in decos:
        count = max(3, length // ORNAMENT_STEP_TICKS)
        if count % 2 == 0:
            count -= 1                                  # comincia e finisce sulla nota
        pitches = [note if k % 2 == 0 else upper for k in range(count)]
        bounds = [start + length * k // count for k in range(count + 1)]
        return [(bounds[k], bounds[k + 1], pitches[k]) for k in range(count)]
    pitches = [note, lower, note] if "mordent" in decos else [upper, note, lower, note]
    step = min(ORNAMENT_STEP_TICKS, length // len(pitches))
    spans = [(start + step * k, start + step * (k + 1), p) for k, p in enumerate(pitches[:-1])]
    return spans + [(start + step * (len(pitches) - 1), stop, pitches[-1])]


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


MIDI_CHANNELS = 16


def _assign_channels(tracks: List["Part"]) -> dict:
    """Assegna a ciascuna traccia uno "slot" MIDI = porta * 16 + canale; le
    percussioni usano sempre il canale riservato (10 nella numerazione
    1-based / 9 in 0-based) della porta 0.

    Ogni porta ha 15 canali melodici: le prime 15 tracce melodiche vanno
    sulla porta 0 (slot = canale, come un file MIDI classico), le successive
    sulle porte 1, 2... (meta evento "MIDI port" in testa alla traccia, vedi
    midi_ports_needed). Cosi' ogni traccia ha sempre il suo canale: un
    canale ha un solo programma, un solo volume/pan, un solo pitch bend e
    una sola accordatura, e condividerlo fra tracce mescolerebbe strumenti
    e automazioni."""
    channel_pool = [c for c in range(MIDI_CHANNELS) if c != DRUM_MIDI_CHANNEL]
    mapping = {}
    melodic = 0
    for t in tracks:
        if t.instrument.is_percussion:
            mapping[t.name] = DRUM_MIDI_CHANNEL
        else:
            port, index = divmod(melodic, len(channel_pool))
            mapping[t.name] = port * MIDI_CHANNELS + channel_pool[index]
            melodic += 1
    return mapping


def midi_ports_needed(mapping: dict) -> bool:
    """True se gli slot di _assign_channels usano piu' di una porta: solo
    allora si scrive il meta evento "MIDI port" (un file con 15 tracce
    melodiche o meno resta identico a prima)."""
    return any(slot >= MIDI_CHANNELS for slot in mapping.values())


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


def _part_events(part, events: List[Event], slot: int, key: Optional[str] = None, ports: bool = False,
                 tempo_ticks: Optional[List[Tuple[int, float]]] = None) -> List[Tuple[int, int, bytes]]:
    instrument = part.instrument
    port, channel = divmod(slot, MIDI_CHANNELS)
    out: List[Tuple[int, int, bytes]] = [(0, _CTRL, _meta(0x03, midi_text_bytes(part.name)))]
    if ports:
        out.append((0, _CTRL, _meta(0x21, bytes([port]))))
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
        moved = shift_ticks(ev, tempo_ticks or [], start)
        start, end = max(0, start + moved), max(0, end + moved)
        end_tick = max(end_tick, end)
        if ev.lyric and ev.lyric != "_":
            text = ev.lyric[:-1] if ev.lyric.endswith("-") and len(ev.lyric) > 1 else ev.lyric + " "
            out.append((start, _CTRL, _meta(0x05, midi_text_bytes(text))))
        if ev.kind == "control":
            for beat, cc, value in control_points(ev, part.volume / 100.0):
                if cc == PITCH_BEND:
                    out.append((tick(beat), _CTRL, bytes([0xE0 | channel, value & 0x7F, value >> 7])))
                elif cc == TUNE:
                    for control, data in tune_controls(value):
                        out.append((tick(beat), _CTRL, bytes([0xB0 | channel, control, data])))
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
        velocity = decorated_velocity(ev, round(ev.velocity * factor))
        stop = _apply_articulation(start, end, effective_articulation(ev))
        for n in notes:
            for a, b, pitch in ornament_spans(ev, n, start, stop, key):
                out.append((a, _ON, bytes([0x90 | channel, pitch, velocity])))
                out.append((b, _OFF, bytes([0x80 | channel, pitch, 0])))
    if sustain:
        out.append((end_tick, _CTRL, bytes([0xB0 | channel, 64, 0])))
    return out


def song_midi_tracks(song, only_audible: bool = True, midi_dir: Optional[str] = None
                     ) -> Tuple[List[List[Tuple[int, int, bytes]]], List["Part"], dict]:
    """Le tracce MIDI del brano [(tick, priorita', messaggio)] (la prima e'
    quella del tempo), le tracce del brano che vi corrispondono e i loro slot
    (porta * 16 + canale, vedi _assign_channels). Usate da song_to_midi e
    dall'export MTXT (st_language.mtxt)."""
    tracks = [t for t in (song.audible_tracks() if only_audible else song.tracks) if not t.is_audio]
    events_by_track = {t.name: t.parsed_events(song.patterns, midi_dir=midi_dir, meter=song.meter()) for t in tracks}
    conductor: List[Tuple[int, int, bytes]] = [(0, _CTRL, _meta(0x03, midi_text_bytes(song.name)))]
    tempo_map = build_tempo_beat_map(song, tracks=tracks, events_by_track=events_by_track)
    tempo_ticks = []
    for beat, bpm in with_fermatas(tempo_map, fermata_spans(events_by_track)):
        tempo_ticks.append((round(beat * TICKS_PER_BEAT), bpm))
        tempo = round(60_000_000 / max(1, bpm))
        conductor.append((round(beat * TICKS_PER_BEAT), _CTRL, _meta(0x51, tempo.to_bytes(3, "big"))))
    for beat, sig in build_metrica_beat_map(song):
        m = RE_METRICA_VALUE.match(sig or "")
        if not m:
            continue
        num, den = int(m.group(1)), int(m.group(2))
        power = max(0, den.bit_length() - 1)
        conductor.append((max(0, round(beat * TICKS_PER_BEAT)), _CTRL, _meta(0x58, bytes([num, power, 24, 8]))))
    channels = _assign_channels(tracks)
    ports = midi_ports_needed(channels)
    midi_tracks = [conductor]
    for t in tracks:
        midi_tracks.append(_part_events(t, events_by_track[t.name], channels[t.name], song.key, ports,
                                        tempo_ticks))
    return midi_tracks, tracks, channels


def song_to_midi(song, path: str, only_audible: bool = True, midi_dir: Optional[str] = None) -> str:
    """Scrive il brano (st_language.song.Song) come file MIDI; ritorna path.
    Con only_audible si rispettano Mute e Solo."""
    write_smf(path, song_midi_tracks(song, only_audible, midi_dir)[0])
    return path
