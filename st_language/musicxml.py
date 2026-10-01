"""
Esportazione del progetto in MusicXML (partitura), leggibile da MuseScore,
Finale, Sibelius, Dorico e dagli altri programmi di notazione.

Lavora su un brano (st_language.song.Song) o su qualunque oggetto con gli
stessi attributi (name, key, tempo_bpm, time_sig, tempo_changes,
metrica_changes, patterns, tracks, audible_tracks(); per ogni traccia
name, instrument, is_audio, parsed_events()): il progetto di SoundText lo
e'.

Parte dagli stessi eventi dell'esportazione MIDI (core.midi_export): note,
accordi gia' risolti dal motore di voicing, blocchi e percussioni. In piu'
scrive quello che nel MIDI non c'e' ma in una partitura serve:
  - le sigle degli accordi (Am7, C/E...) sopra il pentagramma;
  - la tonalita' del progetto come armatura di chiave;
  - la metrica con le battute, i cambi di tempo e di metrica;
  - le dinamiche (dalla velocity), le forcelle (dalle rampe di vol= ed expr=
    e dalle forcelle sulle note), le articolazioni e il pedale.

Ogni traccia diventa una parte; le voci dei blocchi { ; } diventano voci
separate dello stesso pentagramma (gambi in su e in giu'), il testo
cantato le sillabe sotto le note. Pianoforti
e organi hanno due pentagrammi (chiave di violino e di basso, divisi al
Do centrale), chitarre e bassi la chiave all'ottava bassa come nelle
parti stampate, la batteria il pentagramma a percussione con le teste
di nota usuali (x per i piatti). Le durate che non corrispondono a un
valore di nota vengono spezzate in note legate, e le note che scavalcano
la stanghetta proseguono legate nella battuta successiva.
"""

import dataclasses
import datetime
import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from xml.sax.saxutils import escape, quoteattr

from .chords import parse_chord_symbol, parse_key_signature, voice_chord, apply_bass_note
from .instruments import PERCUSSION_MAP, gm_family_for_program
from .notation import DYNAMICS_TO_VELOCITY, Event

if TYPE_CHECKING:          # solo per le annotazioni (nessun import circolare)
    from .song import Part, Song  # noqa: F401

# Durate in quarti: una griglia fine abbastanza per le tuplet della
# grammatica (terzine, quintine, settimine) sui valori piu' brevi. Oltre
# questo denominatore comune le durate vengono arrotondate a QUANT_GRID.
MAX_DIVISIONS = 16 * 3 * 5 * 7 * 4
QUANT_GRID = 48

_NOTE_TYPES = [("breve", Fraction(8)), ("whole", Fraction(4)), ("half", Fraction(2)),
               ("quarter", Fraction(1)), ("eighth", Fraction(1, 2)), ("16th", Fraction(1, 4)),
               ("32nd", Fraction(1, 8)), ("64th", Fraction(1, 16)), ("128th", Fraction(1, 32))]
_DOTS = [(0, Fraction(1)), (1, Fraction(3, 2)), (2, Fraction(7, 4))]
# (note reali, note normali) delle tuplet: le stesse della grammatica
# (vedi core.notation.TUPLET_SCALE), piu' la sestina.
_TUPLETS = [(3, 2), (5, 4), (6, 4), (7, 4)]

_STEPS_SHARP = [("C", 0), ("C", 1), ("D", 0), ("D", 1), ("E", 0), ("F", 0),
                ("F", 1), ("G", 0), ("G", 1), ("A", 0), ("A", 1), ("B", 0)]
_STEPS_FLAT = [("C", 0), ("D", -1), ("D", 0), ("E", -1), ("E", 0), ("F", 0),
               ("G", -1), ("G", 0), ("A", -1), ("A", 0), ("B", -1), ("B", 0)]

# Armatura: numero di alterazioni (positivo diesis, negativo bemolle) della
# tonalita' maggiore con quella tonica. Le toniche enarmoniche (Fa#/Solb,
# Do#/Reb, Si/Dob) seguono l'alterazione scritta nella tonalita'.
_MAJOR_FIFTHS = {0: 0, 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 1: -5, 8: -4, 3: -3, 10: -2, 5: -1}
_ENHARMONIC_FIFTHS = {6: (6, -6), 1: (7, -5), 11: (5, -7)}   # pc -> (con diesis, con bemolle)

# Batteria: posizione sul pentagramma (step, ottava) e testa di nota, come
# nella notazione usuale per drum set (cassa in basso, piatti in alto con
# la x). Le percussioni latine e gli altri suoni hanno comunque ciascuno
# il proprio strumento MIDI nella parte, quindi suonano giusti anche dove
# la posizione e' condivisa.
_DRUM_DISPLAY = {
    "kick": ("F", 4, "normal"), "kick2": ("E", 4, "normal"),
    "snare": ("C", 5, "normal"), "snare2": ("C", 5, "normal"), "rimshot": ("C", 5, "x"),
    "clap": ("B", 4, "x"),
    "hihat": ("G", 5, "x"), "hihat_open": ("G", 5, "circle-x"), "hihat_pedal": ("D", 4, "x"),
    "crash": ("A", 5, "x"), "crash2": ("B", 5, "x"), "china": ("C", 6, "x"), "splash": ("B", 5, "x"),
    "ride": ("F", 5, "x"), "ride2": ("F", 5, "x"), "ride_bell": ("F", 5, "diamond"),
    "tom_hi": ("E", 5, "normal"), "tom1": ("D", 5, "normal"), "tom_lowmid": ("D", 5, "normal"),
    "tom2": ("B", 4, "normal"), "tom_highfloor": ("A", 4, "normal"), "floor": ("G", 4, "normal"),
    "tambourine": ("B", 5, "triangle"), "cowbell": ("E", 5, "triangle"),
}
_DRUM_DEFAULT_DISPLAY = ("C", 5, "normal")

_ARTICULATIONS = {"staccato": "staccato", "mute": "staccatissimo", "legato": "tenuto"}

# Sigle: intervalli dell'accordo -> valore 'kind' di MusicXML. Il testo
# mostrato resta comunque quello scritto nel progetto (attributo text).
_CHORD_KINDS = {
    (0, 4, 7): "major", (0, 3, 7): "minor", (0, 3, 6): "diminished", (0, 4, 8): "augmented",
    (0, 4, 7, 11): "major-seventh", (0, 3, 7, 10): "minor-seventh", (0, 4, 7, 10): "dominant",
    (0, 3, 6, 9): "diminished-seventh", (0, 3, 6, 10): "half-diminished",
    (0, 3, 7, 11): "major-minor", (0, 4, 8, 10): "augmented-seventh",
    (0, 4, 7, 9): "major-sixth", (0, 3, 7, 9): "minor-sixth",
    (0, 2, 7): "suspended-second", (0, 5, 7): "suspended-fourth", (0, 7): "power",
    (0, 4, 7, 10, 14): "dominant-ninth", (0, 4, 7, 11, 14): "major-ninth",
    (0, 3, 7, 10, 14): "minor-ninth",
}


@dataclass
class _Pitch:
    step: str
    alter: int
    octave: int
    midi: int


@dataclass
class _Item:
    """Un attacco della traccia: note (o colpi di batteria) che iniziano e
    finiscono insieme, con cio' che va scritto accanto."""
    start: Fraction
    end: Fraction
    pitches: List[_Pitch] = field(default_factory=list)
    drums: List[str] = field(default_factory=list)
    harmony: Optional[Tuple[str, Optional[str]]] = None   # (sigla, basso)
    articulation: Optional[str] = None
    velocity: int = 80
    voice: int = 1
    lyric: Optional[str] = None            # sillaba come scritta ("Ma-", "_")
    lyric_xml: str = ""                    # <lyric> gia' pronto (vedi _mark_lyrics)


@dataclass
class _Direction:
    time: Fraction
    xml: str


@dataclass
class _Entry:
    """Una nota (o accordo, o pausa) scritta in una battuta."""
    start: Fraction                # rispetto all'inizio della battuta
    duration: Fraction
    item: Optional[_Item]          # None = pausa
    note_type: Optional[str]       # None = pausa di battuta intera
    dots: int = 0
    tuplet: Optional[Tuple[int, int]] = None
    tie_start: bool = False
    tie_stop: bool = False
    first_of_item: bool = False
    tuplet_mark: Optional[str] = None   # "start" / "stop" / None
    beam: Optional[str] = None          # "begin" / "continue" / "end" / None
    directions: List[str] = field(default_factory=list)


def _frac(value: float, grid: Optional[int] = None) -> Fraction:
    if grid:
        return Fraction(round(value * grid), grid)
    return Fraction(value).limit_denominator(960)


def key_fifths(key: str) -> Optional[Tuple[int, str]]:
    """(numero di alterazioni in chiave, 'major'/'minor') per una tonalita'
    come Project.key ('C', 'Am', 'F#', 'Ebm'); None se vuota o non valida."""
    if not key:
        return None
    try:
        pc, minor = parse_key_signature(key)
    except ValueError:
        return None
    major_pc = (pc + 3) % 12 if minor else pc
    fifths = _MAJOR_FIFTHS[major_pc]
    if major_pc in _ENHARMONIC_FIFTHS:
        sharp, flat = _ENHARMONIC_FIFTHS[major_pc]
        written = key.strip()[1:2]
        if written == "#":
            fifths = sharp
        elif written in ("b", "♭", "-"):
            fifths = flat
        elif minor:          # la tonica scritta senza alterazione: Re#m, Sol#m e Sibm restano i piu' comuni
            fifths = sharp if pc in (3, 8) else flat
    return fifths, "minor" if minor else "major"


def _spell_midi(midi: int, flats: bool) -> _Pitch:
    step, alter = (_STEPS_FLAT if flats else _STEPS_SHARP)[midi % 12]
    return _Pitch(step, alter, midi // 12 - 1, midi)


def _spell_letter(letter: str, octave: int) -> _Pitch:
    from .chords import pitch_to_midi
    alter = 0
    if len(letter) > 1:
        alter = 1 if letter[1] == "#" else -1
    return _Pitch(letter[0].upper(), alter, octave, pitch_to_midi(letter, octave))


def _voiced_pitches(symbol: str, octave: int, voicing, bass, instrument, flats: bool) -> List[_Pitch]:
    chord = parse_chord_symbol(symbol)
    notes = voice_chord(chord, octave, instrument, voicing_override=voicing)
    if bass:
        notes = apply_bass_note(notes, bass, octave)
    chord_flats = flats or (len(symbol) > 1 and symbol[1] in ("b", "♭", "-"))
    if len(symbol) > 1 and symbol[1] == "#":
        chord_flats = False
    return [_spell_midi(n, chord_flats) for n in notes if 0 <= n <= 127]


def _track_items(events: List[Event], instrument, flats: bool, grid: Optional[int]
                 ) -> Tuple[List[_Item], List[Tuple[Fraction, str]]]:
    """Attacchi della traccia e cambi del pedale (tempo, 'start'/'stop')."""
    items: List[_Item] = []
    pedals: List[Tuple[Fraction, str]] = []
    for ev in events:
        start = _frac(ev.start, grid)
        end = _frac(ev.start + ev.duration, grid)
        if ev.kind == "sustain":
            pedals.append((start, "start" if ev.name == "on" else "stop"))
            continue
        if ev.kind in ("rest", "tempo_marker") or end <= start:
            continue
        item = _Item(start, end, articulation=ev.articulation, velocity=ev.velocity,
                     voice=ev.voice, lyric=ev.lyric)
        if ev.kind in ("note", "slide"):
            item.pitches.append(_spell_letter(ev.letter, ev.octave))
        elif ev.kind == "chord":
            item.pitches = _voiced_pitches(ev.symbol, ev.octave, ev.voicing, ev.bass, instrument, flats)
            item.harmony = (ev.symbol, ev.bass)
        elif ev.kind == "percussion":
            item.drums.append(ev.name)
        elif ev.kind == "block":
            for sub in ev.items:
                if sub["kind"] == "note":
                    item.pitches.append(_spell_letter(sub["letter"], sub["octave"]))
                elif sub["kind"] == "chord":
                    item.pitches += _voiced_pitches(sub["symbol"], sub["octave"], sub.get("voicing"),
                                                    sub.get("bass"), instrument, flats)
                    if item.harmony is None:
                        item.harmony = (sub["symbol"], sub.get("bass"))
                elif sub["kind"] == "percussion":
                    item.drums.append(sub["name"])
        else:
            continue
        seen = set()
        item.pitches = [p for p in sorted(item.pitches, key=lambda p: p.midi)
                        if not (p.midi in seen or seen.add(p.midi))]
        item.drums = list(dict.fromkeys(item.drums))
        if item.pitches or item.drums:
            items.append(item)
    return items, pedals


def _track_wedges(events: List[Event], grid: Optional[int]) -> List[Tuple[Fraction, Fraction, str]]:
    """Forcelle (inizio, fine, 'crescendo'/'diminuendo') dalle rampe di
    volume e di espressione (vol=, expr=, forcelle sulle note)."""
    wedges = []
    for ev in events:
        if (ev.kind == "control" and ev.name in ("vol", "expr") and ev.duration > 0
                and ev.start_value is not None and ev.value != ev.start_value):
            wedges.append((_frac(ev.start, grid), _frac(ev.start + ev.duration, grid),
                           "crescendo" if ev.value > ev.start_value else "diminuendo"))
    return sorted(wedges)


def _wedge_directions(wedges: List[Tuple[Fraction, Fraction, str]], end: Fraction) -> List[_Direction]:
    """Le forcelle come indicazioni sotto il pentagramma; quelle che si
    sovrappongono hanno numeri diversi (attributo number, 1-6)."""
    directions: List[_Direction] = []
    busy: List[Tuple[Fraction, int]] = []      # (fine, numero) delle forcelle aperte
    for start, stop, kind in wedges:
        stop = min(stop, end)
        if start >= stop:
            continue
        busy = [(e, n) for e, n in busy if e > start]
        free = [n for n in range(1, 7) if n not in {n for _, n in busy}]
        if not free:
            continue
        number = free[0]
        busy.append((stop, number))
        directions.append(_Direction(start, _direction_xml(
            f'<wedge type="{kind}" number="{number}"/>', 1, placement="below")))
        directions.append(_Direction(stop, _direction_xml(
            f'<wedge type="stop" number="{number}"/>', 1, placement="below")))
    return directions


def _monophonic(items: List[_Item]) -> List[_Item]:
    """Una voce per pentagramma: un attacco che arriva prima della fine del
    precedente lo accorcia (come fa il MIDI con due note uguali)."""
    out: List[_Item] = []
    for item in sorted(items, key=lambda i: i.start):
        if out and item.start < out[-1].end:
            if item.start <= out[-1].start:
                out.pop()
            else:
                out[-1] = dataclasses.replace(out[-1], end=item.start)
        out.append(item)
    return out


def _mark_lyrics(items: List[_Item]) -> None:
    """Il testo cantato come <lyric>: 'Ma-' apre o continua una parola
    (syllabic begin/middle), la sillaba dopo la chiude (end), '_' prolunga
    la sillaba precedente (extend)."""
    continues = False
    for item in sorted(items, key=lambda i: i.start):
        syllable = item.lyric
        if not syllable:
            continue
        if syllable == "_":
            item.lyric_xml = '<lyric number="1"><extend/></lyric>'
            continue
        hyphen = syllable.endswith("-") and len(syllable) > 1
        text = syllable[:-1] if hyphen else syllable
        syllabic = ("middle" if hyphen else "end") if continues else ("begin" if hyphen else "single")
        continues = hyphen
        item.lyric_xml = (f'<lyric number="1"><syllabic>{syllabic}</syllabic>'
                          f"<text>{escape(text)}</text></lyric>")


def _note_value(q: Fraction):
    for name, base in _NOTE_TYPES:
        for dots, factor in _DOTS:
            if base * factor == q:
                return name, dots, None
    for actual, normal in _TUPLETS:
        scaled = q * actual / normal
        for name, base in _NOTE_TYPES:
            if base == scaled:
                return name, 0, (actual, normal)
    return None


def _split_duration(q: Fraction):
    """[(tipo, punti, tuplet, durata), ...] la cui somma e' q: un solo
    valore se q si scrive con una nota (anche puntata o in tuplet),
    altrimenti piu' valori da legare, dal piu' lungo."""
    out = []
    while q > 0:
        value = _note_value(q)
        if value:
            out.append(value + (q,))
            break
        for name, base in _NOTE_TYPES:
            if base < q:
                out.append((name, 0, None, base))
                q -= base
                break
        else:                      # piu' breve di ogni valore: la durata resta esatta
            out.append(("128th", 0, None, q))
            break
    return out


def _measures(metrica_map, end: Fraction) -> List[Tuple[Fraction, Fraction, int, int]]:
    """[(inizio, lunghezza, numeratore, denominatore)] fino a coprire end."""
    from .timing import RE_METRICA_VALUE
    changes = []
    for beat, sig in metrica_map:
        m = RE_METRICA_VALUE.match(sig or "")
        if m and int(m.group(1)) > 0 and int(m.group(2)) > 0:
            changes.append((_frac(beat), int(m.group(1)), int(m.group(2))))
    if not changes:
        changes = [(Fraction(0), 4, 4)]
    out = []
    t = Fraction(0)
    num, den = changes[0][1], changes[0][2]
    while t < end or not out:
        for beat, n, d in changes:
            if beat <= t:
                num, den = n, d
        length = Fraction(4 * num, den)
        out.append((t, length, num, den))
        t += length
    return out


def _beat_group(num: int, den: int) -> Fraction:
    if den == 8 and num % 3 == 0 and num > 3:
        return Fraction(3, 2)
    if den >= 4:
        return Fraction(4, den) if den <= 4 else Fraction(1)
    return Fraction(1)


def _staff_entries(items: List[_Item], directions: List[_Direction], m_start: Fraction,
                   m_len: Fraction, num: int, den: int) -> List[_Entry]:
    """Note, pause e indicazioni di un pentagramma in una battuta."""
    m_end = m_start + m_len
    cuts = {m_start, m_end}
    spans = []
    cursor = m_start
    for item in items:
        if item.end <= m_start or item.start >= m_end:
            continue
        s, e = max(item.start, m_start), min(item.end, m_end)
        if s > cursor:
            spans.append((cursor, s, None))
        spans.append((s, e, item))
        cursor = e
    if cursor < m_end:
        spans.append((cursor, m_end, None))
    dirs_here = [d for d in directions if m_start <= d.time < m_end]
    cuts |= {d.time for d in dirs_here}
    pieces = []
    for s, e, item in spans:
        points = sorted({s, e} | {c for c in cuts if s < c < e})
        for a, b in zip(points, points[1:]):
            pieces.append((a, b, item))

    entries: List[_Entry] = []
    if len(pieces) == 1 and pieces[0][2] is None and not dirs_here:
        return [_Entry(Fraction(0), m_len, None, None)]
    for a, b, item in pieces:
        values = _split_duration(b - a)
        t = a
        for i, (name, dots, tuplet, q) in enumerate(values):
            entry = _Entry(t - m_start, q, item, name, dots, tuplet)
            if item is not None:
                entry.tie_stop = (i > 0) or (a > item.start)
                entry.tie_start = (i < len(values) - 1) or (b < item.end)
                entry.first_of_item = (i == 0 and a == item.start)
            if i == 0:
                entry.directions = [d.xml for d in dirs_here if d.time == a]
            entries.append(entry)
            t += q
    _mark_tuplets(entries)
    _mark_beams(entries, _beat_group(num, den))
    return entries


def _mark_tuplets(entries: List[_Entry]) -> None:
    """Parentesi delle tuplet: un gruppo si chiude quando le sue note
    riempiono lo spazio delle note normali (es. tre crome di terzina = due
    crome)."""
    i = 0
    while i < len(entries):
        ratio = entries[i].tuplet
        if ratio is None:
            i += 1
            continue
        target = dict(_NOTE_TYPES)[entries[i].note_type] * ratio[1]
        j, total = i, Fraction(0)
        while j < len(entries) and entries[j].tuplet == ratio and total < target:
            total += entries[j].duration
            j += 1
        if j - i > 1:
            entries[i].tuplet_mark = "start"
            entries[j - 1].tuplet_mark = "stop"
        i = j


_BEAMABLE = {"eighth", "16th", "32nd", "64th", "128th"}


def _mark_beams(entries: List[_Entry], beat: Fraction) -> None:
    run: List[_Entry] = []

    def flush():
        if len(run) > 1:
            run[0].beam = "begin"
            for e in run[1:-1]:
                e.beam = "continue"
            run[-1].beam = "end"
        run.clear()

    for entry in entries:
        group = entry.start // beat
        fits = (entry.item is not None and entry.note_type in _BEAMABLE
                and (entry.start + entry.duration - Fraction(1, 10 ** 6)) // beat == group)
        if not fits:
            flush()
            continue
        if run and run[0].start // beat != group:
            flush()
        run.append(entry)
    flush()


def _dynamic_mark(velocity: int) -> str:
    return min(DYNAMICS_TO_VELOCITY, key=lambda d: abs(DYNAMICS_TO_VELOCITY[d] - velocity))


# Una dinamica nuova si scrive solo se dura almeno tanti attacchi di fila:
# nei brani importati da MIDI la velocity cambia quasi a ogni nota, e una
# dinamica per nota renderebbe la parte illeggibile.
DYNAMIC_MIN_RUN = 4


def _dynamic_changes(items: List[_Item]) -> List[Tuple[Fraction, str]]:
    """[(tempo, dinamica)]: la prima, poi ogni cambio che si mantiene per
    almeno DYNAMIC_MIN_RUN attacchi (o fino alla fine della parte)."""
    marks = [_dynamic_mark(item.velocity) for item in items]
    out: List[Tuple[Fraction, str]] = []
    i = 0
    while i < len(items):
        j = i
        while j < len(items) and marks[j] == marks[i]:
            j += 1
        if not out or (marks[i] != out[-1][1] and (j - i >= DYNAMIC_MIN_RUN or j == len(items))):
            out.append((items[i].start, marks[i]))
        i = j
    return out


def _drop_repeated_harmonies(items: List[_Item]) -> None:
    """La sigla si scrive solo quando l'accordo cambia, come in un lead
    sheet: un accordo ribattuto non la ripete."""
    last = None
    for item in sorted(items, key=lambda i: i.start):
        if item.harmony is None:
            continue
        if item.harmony == last:
            item.harmony = None
        else:
            last = item.harmony


def _direction_xml(inner: str, staff: int, placement: str = "above", sound: str = "") -> str:
    return (f'<direction placement="{placement}"><direction-type>{inner}</direction-type>'
            f'<staff>{staff}</staff>{sound}</direction>')


def _harmony_xml(symbol: str, bass: Optional[str]) -> str:
    chord = parse_chord_symbol(symbol)
    root_len = 2 if len(symbol) > 1 and symbol[1] in ("#", "b", "♭", "-") else 1
    root = symbol[:root_len]
    suffix = symbol[root_len:]
    alter = 0 if root_len == 1 else (1 if root[1] == "#" else -1)
    intervals = tuple(sorted({i % 24 for i in chord.intervals}))
    kind = _CHORD_KINDS.get(intervals, "other")
    xml = f"<harmony><root><root-step>{root[0].upper()}</root-step>"
    if alter:
        xml += f"<root-alter>{alter}</root-alter>"
    xml += f"</root><kind text={quoteattr(suffix)}>{kind}</kind>"
    if bass:
        xml += f"<bass><bass-step>{bass[0].upper()}</bass-step>"
        if len(bass) > 1:
            xml += f"<bass-alter>{1 if bass[1] == '#' else -1}</bass-alter>"
        xml += "</bass>"
    return xml + "<staff>1</staff></harmony>"


def _entry_xml(entry: _Entry, divisions: int, voice: int, staff: int, drum_ids: Dict[str, str],
               stem: Optional[str] = None) -> str:
    duration = int(entry.duration * divisions)
    xml = "".join(entry.directions)
    item = entry.item
    if item is None:
        if entry.note_type is None:
            rest = f'<rest measure="yes"/><duration>{duration}</duration><voice>{voice}</voice>'
        else:
            rest = (f"<rest/><duration>{duration}</duration><voice>{voice}</voice>"
                    f"<type>{entry.note_type}</type>" + "<dot/>" * entry.dots
                    + _time_modification(entry))
        notations = _tuplet_notation(entry)
        return xml + f"<note>{rest}<staff>{staff}</staff>" + \
            (f"<notations>{notations}</notations>" if notations else "") + "</note>"

    if entry.first_of_item and item.harmony:
        xml += _harmony_xml(*item.harmony).replace("<staff>1</staff>", f"<staff>{staff}</staff>")
    heads = [("pitch", p) for p in item.pitches] + [("drum", d) for d in item.drums]
    for i, (kind, value) in enumerate(heads):
        note = "<note>" + ("<chord/>" if i else "")
        if kind == "pitch":
            note += f"<pitch><step>{value.step}</step>"
            if value.alter:
                note += f"<alter>{value.alter}</alter>"
            note += f"<octave>{value.octave}</octave></pitch>"
        else:
            step, octave, _head = _DRUM_DISPLAY.get(value, _DRUM_DEFAULT_DISPLAY)
            note += f"<unpitched><display-step>{step}</display-step><display-octave>{octave}</display-octave></unpitched>"
        note += f"<duration>{duration}</duration>"
        if entry.tie_stop:
            note += '<tie type="stop"/>'
        if entry.tie_start:
            note += '<tie type="start"/>'
        if kind == "drum":
            note += f'<instrument id="{drum_ids[value]}"/>'
        note += f"<voice>{voice}</voice><type>{entry.note_type}</type>" + "<dot/>" * entry.dots
        note += _time_modification(entry)
        if kind == "drum":
            head = _DRUM_DISPLAY.get(value, _DRUM_DEFAULT_DISPLAY)[2]
            note += f"<stem>{stem or 'up'}</stem>"
            if head != "normal":
                note += f"<notehead>{head}</notehead>"
        elif stem:
            note += f"<stem>{stem}</stem>"
        note += f"<staff>{staff}</staff>"
        if entry.beam and i == 0:
            note += f'<beam number="1">{entry.beam}</beam>'
        notations = ""
        if entry.tie_stop:
            notations += '<tied type="stop"/>'
        if entry.tie_start:
            notations += '<tied type="start"/>'
        if i == 0:
            notations += _tuplet_notation(entry)
        if entry.first_of_item and item.articulation in _ARTICULATIONS and i == 0:
            notations += f"<articulations><{_ARTICULATIONS[item.articulation]}/></articulations>"
        if notations:
            note += f"<notations>{notations}</notations>"
        if entry.first_of_item and i == 0:
            note += item.lyric_xml
        xml += note + "</note>"
    return xml


def _time_modification(entry: _Entry) -> str:
    if not entry.tuplet:
        return ""
    actual, normal = entry.tuplet
    return (f"<time-modification><actual-notes>{actual}</actual-notes>"
            f"<normal-notes>{normal}</normal-notes></time-modification>")


def _tuplet_notation(entry: _Entry) -> str:
    return f'<tuplet type="{entry.tuplet_mark}"/>' if entry.tuplet_mark else ""


def _clefs(track: "Part", items: List[_Item]) -> List[Tuple[str, int, int]]:
    """[(segno, linea, cambio d'ottava)] per ciascun pentagramma della parte."""
    instrument = track.instrument
    if instrument.is_percussion:
        return [("percussion", 2, 0)]
    family = gm_family_for_program(instrument.gm_program)
    if family in ("Pianoforti", "Organi"):
        return [("G", 2, 0), ("F", 4, 0)]
    if family == "Chitarre":
        return [("G", 2, -1)]
    if family == "Bassi":
        return [("F", 4, -1)]
    pitches = sorted(p.midi for item in items for p in item.pitches)
    if pitches and pitches[len(pitches) // 2] < 55:
        return [("F", 4, 0)]
    return [("G", 2, 0)]


def _grid_divisions(times: List[Fraction]) -> int:
    divisions = 16
    for t in times:
        divisions = divisions * t.denominator // math.gcd(divisions, t.denominator)
        if divisions > MAX_DIVISIONS:
            return 0
    return divisions


def project_to_musicxml(project: "Song", only_audible: bool = True,
                        tracks: Optional[List["Part"]] = None, midi_dir: Optional[str] = None) -> str:
    """Il progetto come documento MusicXML (partwise 4.0), una parte per
    traccia con notazione (le tracce audio non hanno note da scrivere)."""
    from .timing import build_tempo_beat_map, build_metrica_beat_map

    if tracks is None:
        tracks = project.audible_tracks() if only_audible else project.tracks
    tracks = [t for t in tracks if not t.is_audio]
    events_by_track = {t.name: t.parsed_events(project.patterns, midi_dir=midi_dir) for t in tracks}
    key = key_fifths(project.key)
    flats = bool(key and key[0] < 0)

    grid = None
    for _attempt in range(2):
        parsed = {t.name: _track_items(events_by_track[t.name], t.instrument, flats, grid) for t in tracks}
        tempo_map = [(_frac(b, grid), bpm) for b, bpm in
                     build_tempo_beat_map(project, tracks=tracks, events_by_track=events_by_track)]
        end = max([i.end for items, _ in parsed.values() for i in items] + [Fraction(0)])
        measures = _measures(build_metrica_beat_map(project), end)
        times = [m[0] for m in measures] + [m[0] + m[1] for m in measures]
        times += [t for t, _ in tempo_map]
        for items, pedals in parsed.values():
            times += [i.start for i in items] + [i.end for i in items] + [t for t, _ in pedals]
        wedges = {t.name: _track_wedges(events_by_track[t.name], grid) for t in tracks}
        times += [t for ws in wedges.values() for w in ws for t in w[:2]]
        divisions = _grid_divisions(times)
        if divisions:
            break
        grid = QUANT_GRID
    else:
        divisions = _grid_divisions(times) or QUANT_GRID

    out = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
           '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
           '"http://www.musicxml.org/dtds/partwise.dtd">',
           '<score-partwise version="4.0">',
           f"<work><work-title>{escape(project.name)}</work-title></work>",
           "<identification><encoding><software>SoundText</software>"
           f"<encoding-date>{datetime.date.today().isoformat()}</encoding-date></encoding></identification>",
           "<part-list>"]
    drum_ids_by_part: Dict[str, Dict[str, str]] = {}
    for n, track in enumerate(tracks, 1):
        pid = f"P{n}"
        instrument = track.instrument
        out.append(f'<score-part id="{pid}"><part-name>{escape(track.name)}</part-name>')
        if instrument.is_percussion:
            used = list(dict.fromkeys(d for item in parsed[track.name][0] for d in item.drums))
            ids = {d: f"{pid}-I{PERCUSSION_MAP.get(d, 38) + 1}" for d in used}
            drum_ids_by_part[pid] = ids
            for d, iid in ids.items():
                out.append(f'<score-instrument id="{iid}"><instrument-name>{escape(d)}</instrument-name></score-instrument>')
            for d, iid in ids.items():
                out.append(f'<midi-instrument id="{iid}"><midi-channel>10</midi-channel>'
                           f"<midi-program>{instrument.gm_program + 1}</midi-program>"
                           f"<midi-unpitched>{PERCUSSION_MAP.get(d, 38) + 1}</midi-unpitched></midi-instrument>")
        else:
            out.append(f'<score-instrument id="{pid}-I1"><instrument-name>{escape(instrument.name)}'
                       f"</instrument-name></score-instrument>"
                       f'<midi-instrument id="{pid}-I1"><midi-program>{instrument.gm_program + 1}'
                       f"</midi-program></midi-instrument>")
        out.append("</score-part>")
    out.append("</part-list>")

    for n, track in enumerate(tracks, 1):
        pid = f"P{n}"
        items, pedals = parsed[track.name]
        _drop_repeated_harmonies(items)
        clefs = _clefs(track, items)
        is_drums = track.instrument.is_percussion
        if len(clefs) == 2:
            upper = [dataclasses.replace(i, pitches=[p for p in i.pitches if p.midi >= 60], drums=[])
                     for i in items if any(p.midi >= 60 for p in i.pitches)]
            lower = [dataclasses.replace(i, pitches=[p for p in i.pitches if p.midi < 60], drums=[],
                                         harmony=None,
                                         lyric=i.lyric if not any(p.midi >= 60 for p in i.pitches) else None)
                     for i in items if any(p.midi < 60 for p in i.pitches)]
            staff_items = [upper, lower]
            # la sigla va sopra il primo pentagramma anche se li' c'e' una pausa
            harmonies = [i for i in items if i.harmony and not any(p.midi >= 60 for p in i.pitches)]
        else:
            staff_items = [items]
            harmonies = []
        # Per pentagramma: {voce: attacchi}, ciascuna voce scritta come
        # una linea sola (vedi _monophonic).
        staff_voices = []
        for s_items in staff_items:
            by_voice: Dict[int, List[_Item]] = {}
            for item in s_items:
                by_voice.setdefault(item.voice, []).append(item)
            voices = {v: _monophonic(v_items) for v, v_items in sorted(by_voice.items())} or {1: []}
            for v_items in voices.values():
                _mark_lyrics(v_items)
            staff_voices.append(voices)

        directions: List[_Direction] = []
        if n == 1:
            for t, bpm in tempo_map:
                directions.append(_Direction(t, _direction_xml(
                    f'<metronome><beat-unit>quarter</beat-unit><per-minute>{bpm}</per-minute></metronome>',
                    1, sound=f'<sound tempo="{bpm}"/>')))
        for item in harmonies:
            directions.append(_Direction(item.start, _harmony_xml(*item.harmony)))
        if not is_drums:
            first_voice = min((i.voice for i in items), default=1)
            for t, mark in _dynamic_changes(_monophonic([i for i in items if i.voice == first_voice])):
                directions.append(_Direction(t, _direction_xml(
                    f"<dynamics><{mark}/></dynamics>", 1, placement="below")))
        for t, kind in pedals:
            directions.append(_Direction(t, _direction_xml(
                f'<pedal type="{kind}" line="yes"/>', len(clefs), placement="below")))
        if not is_drums:
            directions += _wedge_directions(wedges[track.name], end)
        directions.sort(key=lambda d: d.time)

        out.append(f'<part id="{pid}">')
        previous_sig = None
        for number, (m_start, m_len, num, den) in enumerate(measures, 1):
            out.append(f'<measure number="{number}">')
            attributes = ""
            if number == 1:
                attributes += f"<divisions>{divisions}</divisions>"
                if key and not is_drums:
                    attributes += f"<key><fifths>{key[0]}</fifths><mode>{key[1]}</mode></key>"
            if (num, den) != previous_sig:
                attributes += f"<time><beats>{num}</beats><beat-type>{den}</beat-type></time>"
                previous_sig = (num, den)
            if number == 1:
                if len(clefs) > 1:
                    attributes += f"<staves>{len(clefs)}</staves>"
                for s, (sign, line, octave_change) in enumerate(clefs, 1):
                    number_attr = f' number="{s}"' if len(clefs) > 1 else ""
                    attributes += f"<clef{number_attr}><sign>{sign}</sign><line>{line}</line>"
                    if octave_change:
                        attributes += f"<clef-octave-change>{octave_change}</clef-octave-change>"
                    attributes += "</clef>"
            if attributes:
                out.append(f"<attributes>{attributes}</attributes>")
            written = False
            for s, voices in enumerate(staff_voices, 1):
                m_end = m_start + m_len
                active = [v for n_v, (v, v_items) in enumerate(voices.items())
                          if n_v == 0 or any(i.start < m_end and i.end > m_start for i in v_items)]
                for n_v, v in enumerate(active):
                    if written:
                        out.append(f"<backup><duration>{int(m_len * divisions)}</duration></backup>")
                    written = True
                    staff_dirs = directions if (s == 1 and n_v == 0) else []
                    stem = None if len(active) == 1 else ("up" if n_v == 0 else "down")
                    xml_voice = (s - 1) * 4 + n_v + 1
                    for entry in _staff_entries(voices[v], staff_dirs, m_start, m_len, num, den):
                        out.append(_entry_xml(entry, divisions, xml_voice, s,
                                              drum_ids_by_part.get(pid, {}), stem))
                    if number == len(measures):
                        # cio' che finisce col brano (una forcella) va dopo l'ultima nota
                        out += [d.xml for d in staff_dirs if d.time >= m_end]
            if number == len(measures):
                out.append('<barline location="right"><bar-style>light-heavy</bar-style></barline>')
            out.append("</measure>")
        out.append("</part>")
    out.append("</score-partwise>")
    return "\n".join(out) + "\n"


def export_project_to_musicxml(project: "Song", path: str, only_audible: bool = True,
                               tracks: Optional[List["Part"]] = None, midi_dir: Optional[str] = None) -> str:
    """Scrive in path la partitura MusicXML del progetto (vedi
    project_to_musicxml): le stesse tracce dell'esportazione MIDI, cioe'
    quelle udibili, rispettando Solo e Mute."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(project_to_musicxml(project, only_audible=only_audible, tracks=tracks, midi_dir=midi_dir))
    return path
