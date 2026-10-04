"""
Ponte verso MTXT (https://github.com/Daninet/mtxt), il formato di testo
"di esecuzione" con un evento per riga e i tempi assoluti in quarti.

song_to_mtxt scrive il brano come MTXT 1.0 partendo dalle stesse tracce
MIDI dell'export (st_language.midi.song_midi_tracks): gli accordi sono gia'
note, swing, shift=, ornamenti, rampe e forcelle sono gia' nei tempi e nei
valori, e le rampe diventano una serie di valori come nel MIDI. Ogni
traccia e' un canale MTXT (lo slot porta * 16 + canale: MTXT ne ha 65535),
con il nome (meta name) e lo strumento (voice, il nome MTXT e quello
General MIDI); la batteria usa gli alias con i nomi ST (alias kick C2). Il
pitch bend (bend=) e l'accordatura (tune=) del canale diventano insieme
"cc pitch" in semitoni.

mtxt_to_midi legge un file MTXT e scrive un MIDI (una traccia per canale,
le porte oltre il sedicesimo), da cui SoundText importa il brano come da
qualunque MIDI (quantizzazione, voci, accordi). Valgono note, on/off,
alias, cc (con transizioni e curve), voice, tempo (con transizioni),
timesig, meta (titolo, nomi dei canali, testo cantato); i cent sulle note
(C4+50) si arrotondano al semitono, tuning, reset e sysex si ignorano.
"""

import re
from typing import Dict, List, Optional, Tuple

from ._i18n import tr
from .instruments import DRUM_MIDI_CHANNEL, PERCUSSION_MAP, gm_instrument_catalog
from .midi import TICKS_PER_BEAT, _meta, midi_text, midi_text_bytes, song_midi_tracks, write_smf

MTXT_VERSION = "1.0"
MTXT_NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
MTXT_PITCH_CLASSES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

# Nomi standard dei controller (quelli dell'implementazione di riferimento).
MTXT_CC_NAMES = {
    1: "vibrato", 2: "breath", 4: "foot", 5: "portamento", 7: "volume", 8: "balance", 10: "pan",
    11: "expression", 64: "sustain", 65: "portamento_switch", 66: "sostenuto", 67: "soft", 68: "legato",
    70: "sound_variation", 71: "timbre", 73: "attack", 74: "cutoff", 75: "decay", 76: "vibrato_rate",
    77: "vibrato_depth", 78: "vibrato_delay", 91: "reverb", 92: "tremolo", 93: "chorus", 94: "detune",
    95: "phaser",
}
MTXT_CC_NUMBERS = {name: number for number, name in MTXT_CC_NAMES.items()}
MTXT_CC_NUMBERS.update({"resonance": 71, "brightness": 74})
MTXT_SIGNED_CC = (8, 10)          # balance e pan vanno da -1 a 1
# Ampiezza del pitch bend scritta (RPN 0) sui canali che usano "cc pitch":
# quella di MTXT (+-12 semitoni), o 24 se il file va oltre (come bend= di ST).
MTXT_PITCH_RANGE = 12
MTXT_WIDE_PITCH_RANGE = 24
# Una transizione diventa al piu' tanti punti, uno ogni MTXT_STEP_TICKS.
MTXT_MAX_POINTS = 128
MTXT_STEP_TICKS = 10

# Nome MTXT (voice) di ciascun programma General MIDI, dall'implementazione
# di riferimento di MTXT (MIT/Apache-2.0).
MTXT_VOICES = [
    "piano_acoustic", "piano_acoustic", "piano_electric_grand", "piano_acoustic", "piano_electric",
    "piano_electric_tine", "harpsichord", "clavinet", "glockenspiel", "glockenspiel", "kalimba",
    "vibraphone", "marimba", "xylophone", "tubular_bells", "zither", "organ_tonewheel", "organ_percussive",
    "organ_rock", "organ_pipe", "organ_reed", "accordion", "harmonica", "accordion", "guitar_acoustic_nylon",
    "guitar_acoustic_steel", "guitar_electric_jazz", "guitar_electric_clean", "guitar_electric_muted",
    "guitar_electric_overdrive", "guitar_electric_overdrive", "guitar", "bass_acoustic", "bass_electric",
    "bass_pick", "bass_fretless", "bass_electric", "bass_electric", "bass_synth", "bass_synth", "violin",
    "viola", "cello", "contrabass", "strings", "strings", "harp", "timpani", "strings", "strings",
    "strings_synth", "strings_synth", "voice_solo", "voice_solo", "voice", "drums_orchestral", "trumpet",
    "trombone", "tuba", "trumpet", "french_horn", "brass", "brass_synth", "brass_synth", "sax_soprano",
    "sax_alto", "sax_tenor", "sax_baritone", "oboe", "english_horn", "bassoon", "clarinet", "piccolo",
    "flute", "recorder", "pan_flute", "flute", "flute", "whistle", "flute", "synth_lead_square",
    "synth_lead_saw", "synth_lead", "synth_lead", "synth_lead", "voice_solo", "synth_lead", "synth_lead",
    "synth_pad", "synth_pad_warm", "synth_pad", "synth_pad_choir", "synth_pad_glass", "synth_pad",
    "synth_pad", "synth_pad", "shaker", "synth_pad", "glockenspiel", "guitar", "guitar", "synth_pad",
    "synth_pad", "synth_pad", "sitar", "banjo", "sitar", "zither", "kalimba", "bagpipe", "violin", "oboe",
    "glockenspiel", "woodblock", "steelpan", "woodblock", "taiko", "melodic_tom", "drums_electronic",
    "cymbals", "silence", "silence", "silence", "silence", "silence", "silence", "silence", "silence",
]


# --------------------------------------------------------------- numeri e testi

def _beat(tick: int) -> str:
    """Un tempo in quarti con al piu' 5 decimali (3.25, 0.0)."""
    text = f"{tick / TICKS_PER_BEAT:.5f}".rstrip("0")
    return text + "0" if text.endswith(".") else text


def _number(value: float) -> str:
    text = f"{value:.5f}".rstrip("0")
    return text + "0" if text.endswith(".") else text


def _unit(value: int) -> str:
    """Un valore MIDI 0-127 come frazione 0..1, che un lettore che tronca
    (value * 127) riporta allo stesso intero."""
    return _number(min(1.0, (value + 0.001) / 127))


def _signed(value: int) -> str:
    """Pan e balance: 0-127 come -1..1 (64 = centro)."""
    return _number(max(-1.0, min(1.0, 2 * (value + 0.001) / 127 - 1)))


def escape(text: str) -> str:
    """Il testo di una meta su una sola riga (\\n, \\t, \\\\...)."""
    out = []
    for c in text:
        if c == "\\":
            out.append("\\\\")
        elif c == "\n":
            out.append("\\n")
        elif c == "\r":
            out.append("\\r")
        elif c == "\t":
            out.append("\\t")
        elif ord(c) < 32:
            out.append(f"\\x{ord(c):02x}")
        else:
            out.append(c)
    return "".join(out)


def unescape(text: str) -> str:
    return re.sub(r"\\(x[0-9a-fA-F]{2}|.)", lambda m: (
        chr(int(m.group(1)[1:], 16)) if m.group(1).startswith("x") and len(m.group(1)) == 3
        else {"n": "\n", "r": "\r", "t": "\t", "0": "\0"}.get(m.group(1), m.group(1))), text)


def note_name(number: int) -> str:
    """60 -> C4 (MTXT: ottava + 1 = numero // 12, come ST)."""
    return f"{MTXT_NOTE_NAMES[number % 12]}{number // 12 - 1}"


def _meta_data(msg: bytes) -> bytes:
    """I dati di un meta evento (FF tipo lunghezza-VLQ dati)."""
    i = 2
    while i < len(msg) and msg[i] & 0x80:
        i += 1
    return msg[i + 1:]


def _key_text(key: str) -> str:
    return f"{key[:-1]} minor" if key.endswith("m") else f"{key} major"


def _voice_line(program: int) -> str:
    """Il nome MTXT e poi quello General MIDI: un sintetizzatore usa
    l'ultimo che conosce, il piu' preciso."""
    gm_names = {p: name for p, name, _family in gm_instrument_catalog()}
    names = [MTXT_VOICES[program]] if 0 <= program < len(MTXT_VOICES) else []
    names.append(gm_names.get(program, str(program)).replace(",", " "))
    return ", ".join(names)


def _drum_aliases() -> Dict[int, str]:
    """Numero di nota GM -> primo nome ST della batteria con quel suono."""
    out: Dict[int, str] = {}
    for name, number in PERCUSSION_MAP.items():
        out.setdefault(number, name)
    return out


# --------------------------------------------------------------- export

def song_to_mtxt(song, only_audible: bool = True, midi_dir: Optional[str] = None) -> str:
    """Il brano (st_language.song.Song) come testo MTXT 1.0."""
    return midi_tracks_to_mtxt(song_midi_tracks(song, only_audible, midi_dir)[0], song.key)


def midi_tracks_to_mtxt(midi_tracks: List[List[Tuple[int, int, bytes]]], key: Optional[str] = None) -> str:
    """Testo MTXT 1.0 da tracce MIDI [(tick, priorita', messaggio)] a 480
    tick per quarto: la prima e' quella del tempo (col titolo), le altre
    una per traccia (nome, porta, canale)."""
    from . import __version__
    conductor = sorted(midi_tracks[0], key=lambda e: (e[0], e[1])) if midi_tracks else []
    title = next((midi_text(_meta_data(m).decode("latin-1")) for _t, _o, m in conductor if m[:2] == b"\xff\x03"),
                 "")
    head = [f"mtxt {MTXT_VERSION}"]
    if title:
        head.append(f"meta global title {escape(title)}")
    head.append(f"meta global generator st-language {__version__}")
    if key:
        head.append(f"meta global key {_key_text(key)}")
    body = ["", "// " + tr("tempo e metrica")]
    for tick, _order, msg in conductor:
        if msg[:2] == b"\xff\x51":
            bpm = 60_000_000 / int.from_bytes(_meta_data(msg), "big")
            body.append(f"{_beat(tick)} tempo {_number(round(bpm, 3))}")
        elif msg[:2] == b"\xff\x58":
            data = _meta_data(msg)
            body.append(f"{_beat(tick)} timesig {data[0]}/{2 ** data[1]}")
    drums = _drum_aliases()
    used_drums = set()
    for events in midi_tracks[1:]:
        lines, drum_notes = _track_lines(events, drums)
        used_drums |= drum_notes
        body += lines
    aliases = [f"alias {drums[n]} {note_name(n)}" for n in sorted(used_drums)]
    if aliases:
        head += ["", "// " + tr("batteria")] + aliases
    return "\n".join(head + body) + "\n"


def _track_lines(events, drums: Dict[int, str]) -> Tuple[List[str], set]:
    """Le righe MTXT di una traccia MIDI: il canale MTXT e' porta * 16 +
    canale MIDI."""
    events = sorted(events, key=lambda e: (e[0], e[1]))
    name = next((midi_text(_meta_data(m).decode("latin-1")) for _t, _o, m in events if m[:2] == b"\xff\x03"), "")
    port = next((_meta_data(m)[0] for _t, _o, m in events if m[:2] == b"\xff\x21"), 0)
    channel = next((m[0] & 0x0F for _t, _o, m in events if m[0] < 0xF0), None)
    if channel is None:
        return [], set()
    slot = port * 16 + channel
    lines = ["", f"// {escape(name)}" if name else "", f"ch={slot}"]
    if name:
        lines.append(f"meta name {escape(name)}")
    timed: List[Tuple[int, int, str]] = []          # (tick, ordine, riga)
    open_notes: Dict[int, List[Tuple[int, int, int]]] = {}
    drum_notes = set()
    is_drums = channel == DRUM_MIDI_CHANNEL
    rpn = [127, 127]
    bend_range = 2.0
    bend, tune = 0.0, 0.0
    tune_data = [64, 0]

    def pitch_line(tick: int, order: int) -> None:
        timed.append((tick, order, f"{_beat(tick)} cc pitch {_number(round(bend + tune / 100, 5))}"))

    for order, (tick, _prio, msg) in enumerate(events):
        status = msg[0]
        if status == 0xFF:
            kind, text = msg[1], midi_text(_meta_data(msg).decode("latin-1"))
            if kind == 0x05 and text.strip():
                timed.append((tick, order, f"{_beat(tick)} meta lyric {escape(text.strip())}"))
            elif kind == 0x01:
                timed.append((tick, order, f"{_beat(tick)} meta text {escape(text)}"))
            continue
        kind = status & 0xF0
        if kind == 0x90 and msg[2] > 0:
            open_notes.setdefault(msg[1], []).append((tick, msg[2], order))
        elif kind in (0x80, 0x90):
            started = open_notes.get(msg[1])
            if not started:
                continue
            start, velocity, at = started.pop(0)
            name = note_name(msg[1])
            if is_drums and msg[1] in drums:
                name = drums[msg[1]]
                drum_notes.add(msg[1])
            timed.append((start, at, f"{_beat(start)} note {name} dur={_number((tick - start) / TICKS_PER_BEAT)} "
                                      f"vel={_unit(velocity)}"))
        elif kind == 0xC0:
            program = msg[1]
            voice = "drums, " + str(program) if is_drums else _voice_line(program)
            timed.append((tick, order, f"{_beat(tick)} voice {voice}"))
        elif kind == 0xE0:
            bend = ((msg[1] | msg[2] << 7) - 8192) / 8192 * bend_range
            pitch_line(tick, order)
        elif kind == 0xB0:
            control, value = msg[1], msg[2]
            if control in (101, 100):
                rpn[0 if control == 101 else 1] = value
            elif control in (6, 38) and tuple(rpn) == (0, 0):
                if control == 6:
                    bend_range = float(value)
            elif control in (6, 38) and tuple(rpn) == (0, 1):
                tune_data[0 if control == 6 else 1] = value
                if control == 38:
                    tune = ((tune_data[0] << 7 | tune_data[1]) - 8192) / 8192 * 100
                    pitch_line(tick, order)
            elif control == 0:
                continue                           # bank select del kit di batteria
            else:
                name = MTXT_CC_NAMES.get(control, str(control))
                value_text = _signed(value) if control in MTXT_SIGNED_CC else _unit(value)
                timed.append((tick, order, f"{_beat(tick)} cc {name} {value_text}"))
    timed.sort(key=lambda t: (t[0], t[1]))
    # tune e bend allo stesso tick: conta l'ultimo punto di pitch
    last_pitch = {tick: i for i, (tick, _o, line) in enumerate(timed) if " cc pitch " in line}
    lines += [line for i, (tick, _o, line) in enumerate(timed)
              if " cc pitch " not in line or last_pitch[tick] == i]
    return lines, drum_notes


# --------------------------------------------------------------- import

class MtxtError(ValueError):
    """Un file MTXT non valido (il messaggio dice la riga)."""


RE_MTXT_NOTE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d+)([+-]\d+(?:\.\d+)?)?$")
_MAJOR_FIFTHS = {"Cb": -7, "Gb": -6, "Db": -5, "Ab": -4, "Eb": -3, "Bb": -2, "F": -1, "C": 0, "G": 1, "D": 2,
                 "A": 3, "E": 4, "B": 5, "F#": 6, "C#": 7}
_MINOR_FIFTHS = {"Ab": -7, "Eb": -6, "Bb": -5, "F": -4, "C": -3, "G": -2, "D": -1, "A": 0, "E": 1, "B": 2,
                 "F#": 3, "C#": 4, "G#": 5, "D#": 6, "A#": 7}
_DIRECTIVES = ("ch", "dur", "vel", "offvel", "transition_curve", "transition_interval")
_OFF, _CTRL, _ON = 0, 1, 2


def _strip_comment(line: str) -> str:
    """La riga senza il commento '//' (ma non quello di un URL, '://')."""
    i = 0
    while True:
        i = line.find("//", i)
        if i < 0:
            return line
        if i > 0 and line[i - 1] == ":":
            i += 2
            continue
        return line[:i]


def mtxt_note_numbers(text: str, aliases: Dict[str, List[int]]) -> List[int]:
    """Le note MIDI di un nome MTXT (C4, bb2, F#3+50) o di un alias; i cent
    si arrotondano al semitono."""
    if text.lower() in aliases:
        return aliases[text.lower()]
    m = RE_MTXT_NOTE.match(text)
    if not m:
        raise ValueError(tr("Nota MTXT non valida: {note}", note=text))
    accidental = {"#": 1, "b": -1, "": 0}[m.group(2)]
    number = (int(m.group(3)) + 1) * 12 + MTXT_PITCH_CLASSES[m.group(1).upper()] + accidental
    number += round(float(m.group(4) or 0) / 100)
    if not 0 <= number <= 127:
        raise ValueError(tr("Nota MTXT fuori dall'estensione MIDI: {note}", note=text))
    return [number]


def _program(voices: List[str]) -> int:
    """Il programma GM di una lista di voci MTXT: vale l'ultima riconosciuta
    (nome General MIDI, nome MTXT, numero, o l'inizio di un nome MTXT)."""
    gm = {name.lower(): p for p, name, _family in gm_instrument_catalog()}
    for voice in reversed(voices):
        v = voice.strip().lower()
        if v in gm:
            return gm[v]
        if v in MTXT_VOICES:
            return MTXT_VOICES.index(v)
        if v.isdigit() and int(v) < 128:
            return int(v)
        family = next((i for i, name in enumerate(MTXT_VOICES) if name.startswith(v + "_")), None)
        if family is not None:
            return family
    return 0


def _curve(s: float, alpha: float) -> float:
    """La forma della transizione MTXT (alpha > 0 parte piano, < 0 veloce)."""
    return (s + max(alpha, 0) * (s ** 4 - s) - max(-alpha, 0) * ((1 - (1 - s) ** 4) - s))


class _Reader:
    def __init__(self):
        self.aliases: Dict[str, List[int]] = {}
        self.defaults = {"ch": None, "dur": 1.0, "vel": 1.0, "offvel": 1.0, "transition_curve": 0.0}
        self.records: List[tuple] = []           # (beat, n, riga, comando, argomenti, parametri)
        self.title: Optional[str] = None
        self.key: Optional[bytes] = None

    def error(self, number: int, message: str) -> MtxtError:
        return MtxtError(tr("Riga {line}: {message}", line=number, message=message))

    def read(self, text: str) -> None:
        version = False
        for number, raw in enumerate(text.splitlines(), 1):
            line = _strip_comment(raw).strip()
            if not line:
                continue
            words = line.split()
            if not version:
                if words[0] != "mtxt" or len(words) != 2:
                    raise self.error(number, tr("un file MTXT inizia con 'mtxt 1.0'"))
                if words[1].split(".")[0] != "1":
                    raise self.error(number, tr("versione di MTXT non supportata: {v}", v=words[1]))
                version = True
                continue
            try:
                self._line(number, line, words)
            except MtxtError:
                raise
            except (ValueError, IndexError) as e:
                raise self.error(number, str(e) or tr("riga non valida")) from e
        if not version:
            raise MtxtError(tr("File MTXT vuoto: manca la riga 'mtxt 1.0'"))

    def _line(self, number: int, line: str, words: List[str]) -> None:
        if all("=" in w for w in words):
            for w in words:
                name, value = w.split("=", 1)
                if name not in _DIRECTIVES:
                    raise ValueError(tr("impostazione sconosciuta: {name}", name=name))
                self.defaults[name] = int(value) if name == "ch" else float(value)
            return
        if words[0] == "alias":
            notes: List[int] = []
            for part in "".join(words[2:]).split(","):
                notes += mtxt_note_numbers(part, self.aliases)
            self.aliases[words[1].lower()] = notes
            return
        if words[0] == "meta" and len(words) > 1 and words[1] == "global":
            kind, value = words[2], unescape(line.split(None, 3)[3].strip() if len(words) > 3 else "")
            if kind == "title":
                self.title = value
            elif kind == "key":
                self.key = _key_signature(value)
            return
        try:
            beat = float(words[0])
            command, rest = words[1], words[2:]
        except ValueError:
            beat, command, rest = 0.0, words[0], words[1:]
        if beat < 0:
            raise ValueError(tr("posizione negativa"))
        params = {}
        args = []
        for w in rest:
            name, eq, value = w.partition("=")
            if eq and name in ("ch", "dur", "vel", "offvel", "transition_curve", "transition_time",
                               "transition_interval"):
                params[name] = int(value) if name == "ch" else float(value)
            else:
                args.append(w)
        if command in ("note", "on", "off", "cc", "voice", "meta"):
            ch = params.get("ch", self.defaults["ch"])
            if ch is None:
                raise ValueError(tr("manca il canale: scrivi prima ch=N"))
            params["ch"] = ch
        if command in ("note", "on", "off"):
            params.setdefault("vel", self.defaults["vel"])
            params.setdefault("offvel", self.defaults["offvel"])
            params.setdefault("dur", self.defaults["dur"])
            args = [mtxt_note_numbers(args[0], self.aliases)]
        elif command in ("cc", "tempo"):
            params.setdefault("transition_curve", self.defaults["transition_curve"])
        elif command == "meta":
            m = re.search(r"\bmeta\s+(?:ch=\d+\s+)?(\S+)\s*(.*)$", line)
            args = [m.group(1), unescape(m.group(2).strip())]
        elif command == "voice":
            args = [v for v in " ".join(args).split(",") if v.strip()]
        elif command not in ("timesig", "tuning", "reset", "sysex"):
            raise ValueError(tr("comando MTXT sconosciuto: {command}", command=command))
        self.records.append((beat, len(self.records), number, command, args, params))


def _key_signature(text: str) -> Optional[bytes]:
    words = text.split()
    if not words:
        return None
    minor = len(words) > 1 and words[1].lower() == "minor"
    table = _MINOR_FIFTHS if minor else _MAJOR_FIFTHS
    root = words[0][:1].upper() + words[0][1:]
    if root not in table:
        return None
    return _meta(0x59, bytes([table[root] & 0xFF, 1 if minor else 0]))


def _tick(beat: float) -> int:
    return round(beat * TICKS_PER_BEAT)


def mtxt_to_midi_tracks(text: str) -> List[List[Tuple[int, int, bytes]]]:
    """Le tracce MIDI (come write_smf) di un testo MTXT: la prima e' quella
    del tempo, poi una per canale MTXT in ordine di numero."""
    reader = _Reader()
    reader.read(text)
    conductor: List[Tuple[int, int, bytes]] = [(0, _CTRL, _meta(0x03, midi_text_bytes(reader.title or "MTXT")))]
    if reader.key:
        conductor.append((0, _CTRL, reader.key))
    channels: Dict[int, List[Tuple[int, int, bytes]]] = {}
    names: Dict[int, str] = {}
    values: Dict[tuple, float] = {}
    tempo = 120.0
    uses_pitch = set()
    pitch_range = MTXT_PITCH_RANGE
    for _b, _n, _line, command, args, _params in reader.records:
        if command == "cc" and len(args) >= 2 and args[-2].lower() == "pitch":
            try:
                if abs(float(args[-1])) > MTXT_PITCH_RANGE:
                    pitch_range = MTXT_WIDE_PITCH_RANGE
            except ValueError:
                pass

    def out(ch: int) -> List[Tuple[int, int, bytes]]:
        return channels.setdefault(ch, [])

    def glide(start: float, end: float, v0: float, v1: float, alpha: float, step: int):
        """I punti (tick, valore) di una transizione da start a end."""
        span = _tick(end) - _tick(start)
        steps = max(1, min(MTXT_MAX_POINTS, span // step))
        return [(_tick(start + (end - start) * k / steps), v0 + (v1 - v0) * _curve(k / steps, alpha))
                for k in range(1, steps + 1)]

    for beat, _n, number, command, args, params in sorted(reader.records, key=lambda r: (r[0], r[1])):
        try:
            ch = params.get("ch")
            status = (ch % 16) if ch is not None else 0
            if command in ("note", "on"):
                velocity = max(1, min(127, round(params["vel"] * 127)))
                for note in args[0]:
                    out(ch).append((_tick(beat), _ON, bytes([0x90 | status, note, velocity])))
                    if command == "note":
                        off = max(0, min(127, round(params["offvel"] * 127)))
                        out(ch).append((_tick(beat + params["dur"]), _OFF, bytes([0x80 | status, note, off])))
            elif command == "off":
                off = max(0, min(127, round(params["offvel"] * 127)))
                for note in args[0]:
                    out(ch).append((_tick(beat), _OFF, bytes([0x80 | status, note, off])))
            elif command == "voice":
                out(ch).append((_tick(beat), _CTRL, bytes([0xC0 | status, _program(args)])))
            elif command == "meta":
                kind, value = args
                if kind in ("name", "trackname"):
                    names[ch] = value
                elif kind == "lyric":
                    out(ch).append((_tick(beat), _CTRL, _meta(0x05, midi_text_bytes(value))))
                elif kind == "keysignature":
                    key = _key_signature(value)
                    if key:
                        conductor.append((_tick(beat), _CTRL, key))
                elif kind in ("text", "marker", "cue"):
                    out(ch).append((_tick(beat), _CTRL, _meta({"text": 0x01, "marker": 0x06, "cue": 0x07}[kind],
                                                               midi_text_bytes(value))))
            elif command == "timesig":
                num, den = (int(x) for x in args[0].split("/"))
                conductor.append((_tick(beat), _CTRL, _meta(0x58, bytes([num, max(0, den.bit_length() - 1), 24, 8]))))
            elif command == "tempo":
                bpm = float(args[0])
                if bpm <= 0:
                    raise ValueError(tr("tempo non valido: {bpm}", bpm=args[0]))
                fade = params.get("transition_time", 0.0)
                points = glide(beat - fade, beat, tempo, bpm, params["transition_curve"], 60) if fade > 0 \
                    else [(_tick(beat), bpm)]
                for tick, value in points:
                    conductor.append((tick, _CTRL, _meta(0x51, round(60_000_000 / value).to_bytes(3, "big"))))
                tempo = bpm
            elif command == "cc":
                if args[0].lower() not in MTXT_CC_NUMBERS and not args[0].isdigit() and len(args) > 2:
                    args = args[1:]                     # "cc C4 volume 0.5": la nota non c'e' nel MIDI
                name, target = args[0], float(args[1])
                key = (ch, name)
                fade = params.get("transition_time", 0.0)
                points = glide(beat - fade, beat, values[key], target, params["transition_curve"], MTXT_STEP_TICKS) \
                    if fade > 0 and key in values else [(_tick(beat), target)]
                values[key] = target
                last = None
                for tick, value in points:
                    message = _cc_message(name, value, status, pitch_range)
                    if message is None:
                        break
                    if name == "pitch":
                        uses_pitch.add(ch)
                    if message != last:
                        out(ch).append((max(0, tick), _CTRL, message))
                        last = message
        except (ValueError, IndexError) as e:
            raise MtxtError(tr("Riga {line}: {message}", line=number, message=str(e) or tr("riga non valida"))) from e

    ports = any(ch >= 16 for ch in channels)
    tracks = [conductor]
    for ch in sorted(channels):
        head = [(0, _CTRL, _meta(0x03, midi_text_bytes(names.get(ch, tr("Canale {n}", n=ch)))))]
        if ports:
            head.append((0, _CTRL, _meta(0x21, bytes([ch // 16]))))
        if ch in uses_pitch:
            status = ch % 16
            head += [(0, _CTRL, bytes([0xB0 | status, c, v])) for c, v in
                     ((101, 0), (100, 0), (6, pitch_range), (38, 0), (101, 127), (100, 127))]
        tracks.append(head + channels[ch])
    return tracks


def _cc_message(name: str, value: float, status: int, pitch_range: int = MTXT_PITCH_RANGE) -> Optional[bytes]:
    """Il messaggio MIDI di un controller MTXT, None se non ha un equivalente."""
    key = name.lower()
    if key == "pitch":
        bend = round(max(-1.0, min(1.0, value / pitch_range)) * 8192) + 8192
        bend = max(0, min(16383, bend))
        return bytes([0xE0 | status, bend & 0x7F, bend >> 7])
    if key == "aftertouch":
        return bytes([0xD0 | status, max(0, min(127, round(value * 127)))])
    number = MTXT_CC_NUMBERS.get(key)
    if number is None and key.isdigit() and int(key) < 128:
        number = int(key)
    if number is None:
        return None
    if number in MTXT_SIGNED_CC:
        raw = (max(-1.0, min(1.0, value)) + 1) / 2 * 127
    else:
        raw = max(0.0, min(1.0, value)) * 127
    return bytes([0xB0 | status, number, max(0, min(127, int(raw + 0.5)))])


def mtxt_to_midi(text: str, path: str) -> str:
    """Scrive come file MIDI un testo MTXT; ritorna path."""
    write_smf(path, mtxt_to_midi_tracks(text))
    return path
