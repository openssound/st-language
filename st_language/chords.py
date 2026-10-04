"""
Parsing di accordi astratti (es. Cmaj7, Am, G7, Dsus4) e motore di
voicing automatico dipendente da strumento/registro/estensione.

Implementa il livello 1->2 descritto nella Visione del prodotto:
    Intenzione musicale astratta  ->  Voicing e note concrete
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .instruments import InstrumentProfile
from ._i18n import tr

PITCH_CLASS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

# Qualita' armoniche supportate: nome-suffisso -> intervalli in semitoni dalla fondamentale
CHORD_QUALITIES = {
    "": [0, 4, 7],
    "maj": [0, 4, 7],
    "m": [0, 3, 7],
    "min": [0, 3, 7],
    "7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "m7": [0, 3, 7, 10],
    "min7": [0, 3, 7, 10],
    "dim": [0, 3, 6],
    "dim7": [0, 3, 6, 9],
    "aug": [0, 4, 8],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "6": [0, 4, 7, 9],
    "m6": [0, 3, 7, 9],
    "9": [0, 4, 7, 10, 14],
    "maj9": [0, 4, 7, 11, 14],
    "m9": [0, 3, 7, 10, 14],
    "mMaj7": [0, 3, 7, 11],
    "m7b5": [0, 3, 6, 10],
    "add9": [0, 4, 7, 14],
    "7sus4": [0, 5, 7, 10],
    "7b9": [0, 4, 7, 10, 13],
    "7#9": [0, 4, 7, 10, 15],
    "5": [0, 7],                        # power chord: solo fondamentale+quinta, niente terza
    "°": [0, 3, 6],                     # alias di 'dim' (notazione classica)
    "°7": [0, 3, 6, 9],                 # alias di 'dim7'
    "7alt": [0, 4, 7, 10, 13],           # dominante alterato: approssimato come 7b9
    "11": [0, 4, 7, 10, 14, 17],
    "13": [0, 4, 7, 10, 14, 21],        # l'11 e' omesso, come da prassi jazz comune
    "maj13": [0, 4, 7, 11, 14, 21],
}

# La classe di caratteri include '#' per poter esprimere qualita' come
# '7#9' (Hendrix chord) direttamente nel suffisso, non solo come
# alterazione della fondamentale (gruppo precedente).
# Alterazione: '#' per diesis; 'b', '♭' (simbolo musicale reale) o '-' per bemolle,
# tra loro equivalenti (vedi note_name_to_pc). '-' e' pensato come scorciatoia di
# digitazione: l'editor la sostituisce automaticamente con '♭' non appena viene
# digitata subito dopo una lettera nota (vedi gui/voicing_picker.py), per evitare
# l'ambiguita' visiva tra la 'b' di alterazione e la 'b' lettera-nota (Si).
CHORD_RE = re.compile(r"^([A-G])([#b♭-]?)([A-Za-z0-9#°]*)$")


@dataclass
class ParsedChord:
    root_pc: int
    quality: str
    intervals: List[int]
    symbol: str
    # Semitoni da aggiungere a midi_note(root_pc, ottava) per le fondamentali
    # che scavalcano il Do (vedi pitch_to_midi): -12 per Cb, +12 per B#, 0
    # per tutte le altre.
    octave_shift: int = 0


def parse_chord_symbol(symbol: str) -> ParsedChord:
    m = CHORD_RE.match(symbol)
    if not m:
        raise ValueError(tr("Simbolo di accordo non valido: '{symbol}'", symbol=symbol))
    letter, accidental, suffix = m.groups()
    raw = _letter_semitones(letter + accidental)
    pc = raw % 12

    if suffix not in CHORD_QUALITIES:
        raise ValueError(
            tr("Qualita' di accordo non riconosciuta: '{suffix}' in '{symbol}'. Supportate: {0}", ', '.join(q or 'maj' for q in CHORD_QUALITIES), suffix=suffix, symbol=symbol)
        )
    return ParsedChord(root_pc=pc, quality=suffix, intervals=CHORD_QUALITIES[suffix], symbol=symbol,
                       octave_shift=raw - pc)


MAJOR_SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
NATURAL_MINOR_SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]
MAJOR_PENTATONIC_INTERVALS = [0, 2, 4, 7, 9]
MINOR_PENTATONIC_INTERVALS = [0, 3, 5, 7, 10]
# Blues (esatonica): pentatonica minore + quinta diminuita di passaggio ("blue
# note"). A differenza di diatonica/pentatonica non ha una variante 'maggiore'
# distinta: e' la stessa scala indipendentemente dal modo (maggiore/minore)
# della tonalita' scelta, si applica sempre a partire dalla tonica.
BLUES_INTERVALS = [0, 3, 5, 6, 7, 10]

SCALE_TYPES = ("diatonica", "pentatonica", "blues")

# Tonalita': lettera nota (A-G) + alterazione opzionale + 'm' opzionale per il
# minore (naturale), es. 'C', 'F#', 'Ebm', 'Am' - stessa convenzione usata da
# mido per i messaggi meta 'key_signature' del MIDI, cosi' import/export non
# richiedono alcuna conversione di formato.
KEY_RE = re.compile(r"^([A-Ga-g])([#b♭-]?)(m?)$")


def parse_key_signature(key: str) -> Tuple[int, bool]:
    """Analizza una tonalita' (es. 'C', 'Am', 'F#') in (classe di altezza
    della tonica 0-11, e' minore). Solleva ValueError se il formato non e'
    riconosciuto."""
    m = KEY_RE.match(key.strip())
    if not m:
        raise ValueError(tr("Tonalita' non valida: '{key}'", key=key))
    letter, accidental, minor_suffix = m.groups()
    pc = PITCH_CLASS[letter.upper()]
    if accidental == "#":
        pc += 1
    elif accidental in ("b", "♭", "-"):
        pc -= 1
    return pc % 12, bool(minor_suffix)


def scale_pitch_classes(key: str, scale_type: str = "diatonica") -> List[int]:
    """Ritorna le classi di altezza (0-11, in ordine crescente di grado a
    partire dalla tonica) della scala scelta per la tonalita' data:
    - 'diatonica' (default, 7 note): maggiore o minore naturale a seconda
      del modo della tonalita' (es. 'Am' -> la minore naturale);
    - 'pentatonica' (5 note): maggiore o minore a seconda del modo, stesso
      criterio della diatonica;
    - 'blues' (6 note): sempre la stessa esatonica a partire dalla tonica,
      indipendentemente dal modo (vedi BLUES_INTERVALS).
    Solleva ValueError se 'key' non e' una tonalita' valida (vedi
    parse_key_signature) o 'scale_type' non e' uno tra SCALE_TYPES."""
    if scale_type not in SCALE_TYPES:
        raise ValueError(tr("Tipo di scala non valido: '{scale_type}' (validi: {0})", ', '.join(SCALE_TYPES), scale_type=scale_type))
    root_pc, minor = parse_key_signature(key)
    if scale_type == "blues":
        intervals = BLUES_INTERVALS
    elif scale_type == "pentatonica":
        intervals = MINOR_PENTATONIC_INTERVALS if minor else MAJOR_PENTATONIC_INTERVALS
    else:
        intervals = NATURAL_MINOR_SCALE_INTERVALS if minor else MAJOR_SCALE_INTERVALS
    return [(root_pc + iv) % 12 for iv in intervals]


def _letter_semitones(letter: str) -> int:
    """Semitoni della lettera nota (con alterazione) rispetto al Do della
    STESSA ottava scritta, senza riportarli in 0-11: 'cb' -> -1 (il Si
    dell'ottava sotto), 'b#' -> 12 (il Do dell'ottava sopra)."""
    semitones = PITCH_CLASS[letter[0].upper()]
    if len(letter) > 1:
        if letter[1] == "#":
            semitones += 1
        elif letter[1] in ("b", "♭", "-"):
            semitones -= 1
    return semitones


def note_name_to_pc(letter: str) -> int:
    """Converte una lettera nota (eventualmente con alterazione, es. 'c#', 'eb')
    nella classe di altezza 0-11."""
    return _letter_semitones(letter) % 12


def midi_note(pc: int, octave: int) -> int:
    """Converte classe di altezza + ottava (notazione /n) in nota MIDI.
    Convenzione: ottava 4 = C4 = MIDI 60 (standard 'scientific pitch')."""
    return (octave + 1) * 12 + pc


def pitch_to_midi(letter: str, octave: int) -> int:
    """Nota MIDI di una lettera nota (con alterazione) all'ottava scritta.
    A differenza di midi_note(note_name_to_pc(letter), octave), rispetta
    l'ottava delle alterazioni che scavalcano il Do: 'cb*4' e' il Si3 (59),
    non il Si4, e 'b#*4' e' il Do5 (72), non il Do4."""
    return (octave + 1) * 12 + _letter_semitones(letter)


_SHARP_NAMES = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]


def midi_to_pitch(midi: int):
    """Ritorna (lettera[+#], ottava) per una nota MIDI, usando diesis per le alterazioni.
    La grammatica non ammette ottave negative: le note MIDI 0-11 (ottava -1,
    sotto i 16 Hz, quasi inudibili) vengono portate un'ottava sopra, con la
    stessa classe di altezza."""
    if midi < 12:
        midi += 12
    pc = midi % 12
    octave = midi // 12 - 1
    return _SHARP_NAMES[pc], octave


def midi_to_token(midi: int) -> str:
    """Converte una nota MIDI nel token di notazione interna (es. 60 -> 'c*4', 61 -> 'c#*4')."""
    letter, octave = midi_to_pitch(midi)
    return f"{letter}*{octave}"


def transpose_pitch(letter: str, octave: int, semitones: int):
    """Trasla una nota (lettera[+alterazione], ottava) di N semitoni,
    ritornando la nuova coppia (lettera[+alterazione], ottava)."""
    return midi_to_pitch(pitch_to_midi(letter, octave) + semitones)


def pc_to_letter(pc: int) -> str:
    """Nome (minuscolo, con eventuale #) della classe di altezza 0-11."""
    return _SHARP_NAMES[pc % 12]


def transpose_chord_root(symbol: str, semitones: int) -> str:
    """Trasla il simbolo di un accordo (es. 'Cmaj7') di N semitoni, mantenendone la qualita'."""
    parsed = parse_chord_symbol(symbol)
    new_pc = (parsed.root_pc + semitones) % 12
    return pc_to_letter(new_pc).upper() + parsed.quality


def voice_chord(chord: ParsedChord, octave: int, instrument: InstrumentProfile,
                 voicing_override: str = None) -> List[int]:
    """
    Motore di voicing automatico (SoundText Engine): data l'intenzione
    astratta (accordo) genera le note concrete (numeri MIDI) adatte allo
    strumento, tenendo conto di registro/estensione/stile.

    Se voicing_override e' None (comportamento di sempre, invariato),
    lo stile e' quello di default dello strumento (instrument.voicing_style).
    Se voicing_override e' valorizzato (suffisso '.stile' sul token
    dell'accordo nella notazione, es. 'Cmaj7.drop2'), ha PRECEDENZA e forza
    l'algoritmo specifico, con fallback automatico su un equivalente
    generico se lo stile richiesto non ha senso per la famiglia dello
    strumento corrente (es. '.barre' su un Pianoforte diventa '.close').
    """
    base = midi_note(chord.root_pc, octave) + chord.octave_shift

    if voicing_override:
        style = _resolve_voicing_fallback(voicing_override, instrument)
        pattern = _lookup_guitar_pattern(chord.quality, style) if style in GUITAR_VOICINGS else None
        if pattern is not None:
            notes = [base + off for off in pattern]
        else:
            notes = _apply_named_voicing(style, base, chord.intervals)
    elif instrument.voicing_style == "monophonic":
        # Strumento monofonico: suona solo la fondamentale dell'accordo
        notes = [base]

    elif instrument.voicing_style == "root_fifth":
        # Basso: fondamentale (+ quinta se presente nell'accordo)
        notes = [base]
        if 7 in chord.intervals:
            notes.append(base + 7)

    elif instrument.voicing_style == "spread":
        # Piano/Chitarra: distribuisce le note dell'accordo, evitando che
        # cadano troppo vicine se lo strumento ha estensione ampia
        notes = [base + iv for iv in chord.intervals]

    else:
        notes = [base + iv for iv in chord.intervals]

    # Adatta ogni nota all'estensione (range) dello strumento, spostandola
    # di ottave finche' non rientra nel registro consentito
    adjusted = []
    for n in notes:
        while n < instrument.range_low:
            n += 12
        while n > instrument.range_high:
            n -= 12
        adjusted.append(n)
    return sorted(set(adjusted))


def apply_bass_note(notes: List[int], bass: str, base_octave: int) -> List[int]:
    """Applica il basso alternativo di un accordo 'slash' (es. 'C/E'): inserisce
    nella lista di note gia' voicate (da voice_chord) una nota aggiuntiva sulla
    classe di altezza 'bass', posizionata sotto tutte le altre (e' il punto
    dello slash chord: quella nota diventa la piu' grave suonata)."""
    bass_pc = note_name_to_pc(bass)
    lowest = min(notes) if notes else midi_note(bass_pc, base_octave)
    bass_midi = midi_note(bass_pc, base_octave - 1)
    while bass_midi >= lowest:
        bass_midi -= 12
    return sorted(set(notes) | {bass_midi})


# ---------------------------------------------------------------------------
# Voicing per suffisso esplicito (SoundText Language, sez. accordo compatto):
# Cmaj7.drop2, C7.cagEd, C.power, Am7.open, F.barre, ...
# ---------------------------------------------------------------------------

GENERAL_VOICINGS = {"noroot", "shell", "close", "open", "inv1", "inv2", "inv3"}
GUITAR_VOICINGS = {"barre", "Caged", "cAged", "caGed", "cagEd", "cageD",
                    "drop2", "drop3", "triad", "power",
                    "openpos", "hendrix", "top", "bottom"}
KEYBOARD_VOICINGS = {"left", "right", "spread"}
ALL_VOICINGS = GENERAL_VOICINGS | GUITAR_VOICINGS | KEYBOARD_VOICINGS

_GUITAR_FAMILIES = {"Chitarre"}
_KEYBOARD_FAMILIES = {"Pianoforti", "Organi", "Percussioni intonate"}

# Fallback quando uno stile specifico non ha senso per la famiglia corrente:
# viene sostituito con l'equivalente generico piu' vicino (mai un errore).
_GUITAR_FALLBACK = {
    "barre": "close", "Caged": "close", "cAged": "close", "caGed": "close",
    "cagEd": "close", "cageD": "close", "drop2": "open", "drop3": "open",
    "triad": "close", "power": "close",
    "openpos": "open", "hendrix": "close", "top": "close", "bottom": "close",
}
_KEYBOARD_FALLBACK = {"left": "open", "right": "close", "spread": "open"}

# ---------------------------------------------------------------------------
# Tabella di lookup per i voicing chitarra piu' comuni: offset semitonali
# reali (non un algoritmo generico) per garantire accuratezza fisica sulle
# combinazioni qualita'x stile piu' usate, senza dover simulare una
# tastiera/corde. Chiavi di qualita' canonicalizzate (vedi
# _canonical_quality): una combinazione qualita'/stile assente qui ricade
# sempre sull'algoritmo generico in _apply_named_voicing (nessun buco di
# copertura). NON sono diteggiature reali su corde/tasti: come per il resto
# del motore, sono approssimazioni musicalmente sensate su note MIDI astratte.
GUITAR_VOICING_PATTERNS: Dict[str, Dict[str, List[int]]] = {
    "maj": {
        "barre": [0, 7, 12, 16], "cagEd": [0, 7, 12, 16], "cAged": [0, 7, 12, 16],
        "triad": [0, 4, 7], "power": [0, 7, 12], "openpos": [0, 4, 7, 12, 16],
        "top": [12, 16, 19], "bottom": [0, 7, 12], "hendrix": [0, 12, 16, 19],
    },
    "m": {
        "barre": [0, 7, 12, 15], "cagEd": [0, 7, 12, 15], "cAged": [0, 7, 12, 15],
        "triad": [0, 3, 7], "power": [0, 7, 12], "openpos": [0, 3, 7, 12, 15],
        "top": [12, 15, 19], "bottom": [0, 7, 12], "hendrix": [0, 12, 15, 19],
    },
    "dim": {
        "barre": [0, 6, 12, 15], "triad": [0, 3, 6], "drop2": [3, 6, 12, 15],
        "openpos": [0, 3, 6, 12], "top": [12, 15, 18], "bottom": [0, 6, 12],
        "hendrix": [0, 6, 15, 18],
    },
    "aug": {
        "barre": [0, 8, 12, 16], "triad": [0, 4, 8], "openpos": [0, 4, 8, 12],
        "top": [12, 16, 20], "bottom": [0, 8, 12], "hendrix": [0, 8, 16, 20],
    },
    "maj7": {
        "barre": [0, 7, 11, 16], "cagEd": [0, 7, 11, 16], "cAged": [0, 7, 11, 16],
        "drop2": [4, 11, 12, 19], "drop3": [0, 11, 16, 19], "triad": [0, 4, 7],
        "power": [0, 7, 12], "openpos": [0, 4, 7, 11, 16], "top": [11, 12, 16, 19],
        "bottom": [0, 7, 11, 16], "hendrix": [0, 11, 16, 19],
    },
    "m7": {
        "barre": [0, 7, 10, 15], "cagEd": [0, 7, 10, 15], "cAged": [0, 7, 10, 15],
        "drop2": [3, 10, 12, 19], "drop3": [0, 10, 15, 19], "triad": [0, 3, 7],
        "power": [0, 7, 12], "openpos": [0, 3, 7, 10, 15], "top": [10, 12, 15, 19],
        "bottom": [0, 7, 10, 15], "hendrix": [0, 10, 15, 19],
    },
    "7": {
        "barre": [0, 7, 10, 16], "cagEd": [0, 7, 10, 16], "cAged": [0, 7, 10, 16],
        "drop2": [4, 10, 12, 19], "drop3": [0, 10, 16, 19], "triad": [0, 4, 7],
        "power": [0, 7, 12], "openpos": [0, 4, 7, 10, 16], "top": [10, 12, 16, 19],
        "bottom": [0, 7, 10, 16], "hendrix": [0, 10, 16, 19],
    },
    "mMaj7": {
        "barre": [0, 7, 11, 15], "drop2": [3, 11, 12, 19], "drop3": [0, 11, 15, 19],
        "openpos": [0, 3, 7, 11, 15], "top": [11, 12, 15, 19], "bottom": [0, 7, 11, 15],
        "hendrix": [0, 11, 15, 19],
    },
    "m7b5": {
        "barre": [0, 6, 10, 15], "drop2": [3, 10, 12, 18], "drop3": [0, 10, 15, 18],
        "openpos": [0, 3, 6, 10], "top": [10, 12, 15, 18], "bottom": [0, 6, 10, 15],
        "hendrix": [0, 10, 15, 18],
    },
    "dim7": {
        "barre": [0, 6, 9, 15], "drop2": [3, 9, 12, 18], "drop3": [0, 9, 15, 18],
        "openpos": [0, 3, 6, 9], "top": [9, 12, 15, 18], "bottom": [0, 6, 9, 15],
        "hendrix": [0, 9, 15, 18],
    },
    "sus2": {
        "barre": [0, 2, 7, 12], "triad": [0, 2, 7], "openpos": [0, 2, 7, 12, 14],
        "top": [12, 14, 19], "bottom": [0, 7, 12], "hendrix": [0, 12, 14, 19],
    },
    "sus4": {
        "barre": [0, 5, 7, 12], "triad": [0, 5, 7], "openpos": [0, 5, 7, 12, 17],
        "top": [12, 17, 19], "bottom": [0, 7, 12], "hendrix": [0, 12, 17, 19],
    },
    "7sus4": {
        "barre": [0, 5, 10, 12], "drop2": [5, 10, 12, 19], "openpos": [0, 5, 7, 10, 17],
        "top": [10, 12, 17, 19], "bottom": [0, 5, 10, 12], "hendrix": [0, 10, 17, 19],
    },
    "6": {
        "barre": [0, 4, 7, 9], "drop2": [4, 9, 12, 16], "openpos": [0, 4, 7, 9, 12],
        "top": [9, 12, 16, 19], "bottom": [0, 4, 7, 9], "hendrix": [0, 9, 16, 19],
    },
    "m6": {
        "barre": [0, 3, 7, 9], "drop2": [3, 9, 12, 15], "openpos": [0, 3, 7, 9, 12],
        "top": [9, 12, 15, 19], "bottom": [0, 3, 7, 9], "hendrix": [0, 9, 15, 19],
    },
    "add9": {
        "barre": [0, 4, 7, 14], "open": [0, 4, 7, 14], "openpos": [0, 4, 7, 14, 16],
        "top": [12, 14, 16, 19], "bottom": [0, 4, 7, 12], "hendrix": [0, 14, 16, 19],
    },
    "maj9": {
        "barre": [0, 11, 14, 16], "drop2": [4, 11, 14, 19], "openpos": [0, 4, 11, 14, 16],
        "top": [11, 14, 16, 19], "bottom": [0, 7, 11, 14], "hendrix": [0, 11, 14, 16],
    },
    "m9": {
        "barre": [0, 10, 14, 15], "drop2": [3, 10, 14, 19], "openpos": [0, 3, 10, 14, 15],
        "top": [10, 14, 15, 19], "bottom": [0, 7, 10, 14], "hendrix": [0, 10, 14, 15],
    },
    "9": {
        "barre": [0, 10, 14, 16], "drop2": [4, 10, 14, 19], "openpos": [0, 4, 10, 14, 16],
        "top": [10, 14, 16, 19], "bottom": [0, 7, 10, 14], "hendrix": [0, 10, 14, 16],
    },
    "7b9": {
        "barre": [0, 10, 13, 16], "drop2": [4, 10, 13, 19], "openpos": [0, 4, 10, 13, 16],
        "top": [10, 13, 16, 19], "bottom": [0, 7, 10, 13], "hendrix": [0, 10, 13, 16],
    },
    "7#9": {
        "barre": [0, 10, 15, 16], "drop2": [4, 10, 15, 19], "openpos": [0, 4, 10, 15, 16],
        "top": [10, 15, 16, 19], "bottom": [0, 7, 10, 15],
        "hendrix": [0, 10, 15, 16],  # la classica presa pollice/quinta corda
    },
}

# Alias di qualita' che condividono la stessa voce in tabella (stessi
# intervalli in CHORD_QUALITIES, un solo insieme di voicing curati).
_QUALITY_ALIASES = {"": "maj", "min": "m", "min7": "m7", "°": "dim", "°7": "dim7", "7alt": "7b9"}


def _canonical_quality(quality: str) -> str:
    return _QUALITY_ALIASES.get(quality, quality)


def _lookup_guitar_pattern(quality: str, style: str) -> Optional[List[int]]:
    return GUITAR_VOICING_PATTERNS.get(_canonical_quality(quality), {}).get(style)


def _instrument_family(instrument: InstrumentProfile) -> str:
    if instrument.is_percussion:
        return "Percussioni"
    from .instruments import gm_family_for_program
    return gm_family_for_program(instrument.gm_program)


def _resolve_voicing_fallback(style: str, instrument: InstrumentProfile) -> str:
    """Applica la logica di fallback: uno stile specifico per chitarra usato
    su uno strumento non-chitarristico (o viceversa per la tastiera) viene
    convertito nell'equivalente generico piu' vicino, invece di essere un
    errore o di venire semplicemente ignorato senza spiegazione."""
    if style in GENERAL_VOICINGS:
        return style  # sempre validi, su qualunque strumento

    family = _instrument_family(instrument)

    if style in GUITAR_VOICINGS:
        if family in _GUITAR_FAMILIES:
            return style
        return _GUITAR_FALLBACK.get(style, "close")

    if style in KEYBOARD_VOICINGS:
        if family in _KEYBOARD_FAMILIES:
            return style
        return _KEYBOARD_FALLBACK.get(style, "close")

    # Stile sconosciuto: fallback prudente, mai un crash del motore di voicing
    return "close"


def applicable_voicings(instrument: InstrumentProfile) -> List[str]:
    """Stili di voicing che, se scelti per questo strumento, verranno
    applicati esattamente come richiesto (nessuna sostituzione silenziosa
    da parte di _resolve_voicing_fallback). Usato dal menu di selezione
    voicing su doppio click (GUI): mostra solo le opzioni che avranno
    davvero l'effetto mostrato all'utente."""
    family = _instrument_family(instrument)
    styles = set(GENERAL_VOICINGS)
    if family in _GUITAR_FAMILIES:
        styles |= GUITAR_VOICINGS
    elif family in _KEYBOARD_FAMILIES:
        styles |= KEYBOARD_VOICINGS
    return sorted(styles)


def recognize_chord(midi_notes: List[int]) -> Optional[Tuple[int, str, int]]:
    """Cerca, tra le qualita' note (CHORD_QUALITIES), quella la cui
    struttura di classi di altezza e' interamente coperta dalle note MIDI
    fornite (usato per riconoscere un accordo gia' scritto in forma
    esplicita [...]). Ritorna (root_pc, quality, anchor_octave) o None se
    nessuna qualita' nota corrisponde (es. una semplice quinta, ambigua tra
    maggiore/minore, resta correttamente non riconosciuta).

    anchor_octave e' l'ottava della nota piu' grave, tra quelle fornite,
    che ha la classe di altezza scelta come fondamentale — per mantenere
    il registro originale del blocco quando si ricalcola il voicing."""
    if len(midi_notes) < 2:
        return None

    notes_by_pc: Dict[int, List[int]] = {}
    for n in midi_notes:
        notes_by_pc.setdefault(n % 12, []).append(n)
    observed = set(notes_by_pc.keys())

    best = None  # (score, root_pc, quality)
    for root_pc in observed:
        for quality, intervals in CHORD_QUALITIES.items():
            if quality == "":
                continue  # alias di 'maj', evita doppioni
            candidate = {(root_pc + iv) % 12 for iv in intervals}
            if candidate - observed:
                continue  # l'accordo candidato deve essere interamente coperto dalle note presenti
            score = (len(observed - candidate), len(intervals))
            if best is None or score < best[0]:
                best = (score, root_pc, quality)

    if best is None:
        return None
    _, root_pc, quality = best
    anchor_note = min(notes_by_pc[root_pc])
    anchor_octave = anchor_note // 12 - 1
    return root_pc, quality, anchor_octave


def _close_position_notes(base: int, intervals: List[int]) -> List[int]:
    """Impila le classi di altezza dell'accordo il piu' vicino possibile
    (entro una sola ottava dalla fondamentale), senza duplicati di classe."""
    seen_pcs = set()
    notes = []
    for iv in intervals:
        pc_offset = iv % 12
        if pc_offset in seen_pcs:
            continue
        seen_pcs.add(pc_offset)
        notes.append(base + pc_offset)
    return sorted(notes)


def _invert_chord(base: int, intervals: List[int], n: int) -> List[int]:
    """Inversione generica: la nota bersaglio (3a/5a/7a per n=1/2/3, in base
    all'ordine delle note in posizione stretta) scende di un'ottava per
    diventare il basso. Se l'accordo non ha abbastanza note per l'inversione
    richiesta, usa l'inversione piu' alta disponibile (mai un errore)."""
    notes = _close_position_notes(base, intervals)
    if len(notes) <= 1:
        return notes
    n = max(1, min(n, len(notes) - 1))
    target = notes[n]
    inverted = [x for x in notes if x != target] + [target - 12]
    return sorted(inverted)


def _apply_named_voicing(style: str, base: int, intervals: List[int]) -> List[int]:
    """Genera le note (prima dell'adattamento al registro dello strumento,
    fatto uniformemente da voice_chord) per lo stile di voicing richiesto.
    Le implementazioni per chitarra (barre/CAGED) sono approssimazioni
    musicalmente sensate, NON diteggiature su tastiera/corde reali: il
    motore lavora su note MIDI astratte e non modella corde/tasti/capotasto."""

    if style == "noroot":
        notes = [base + iv for iv in intervals if iv != 0]
        return notes or [base]

    if style == "shell":
        return [base + iv for iv in intervals if iv != 7]

    if style == "close":
        return _close_position_notes(base, intervals)

    if style == "open" or style == "openpos":
        # 'openpos' (chitarra, prima posizione con corde a vuoto) non ha un
        # equivalente algoritmico fedele senza un modello di corde/tasti:
        # approssimato come alias della forma aperta generica.
        close = _close_position_notes(base, intervals)
        return [n + (12 if i % 2 == 1 else 0) for i, n in enumerate(close)]

    if style in ("inv1", "inv2", "inv3"):
        return _invert_chord(base, intervals, int(style[-1]))

    if style == "top":  # chitarra: accordo un'ottava sopra, in posizione stretta
        return _close_position_notes(base + 12, intervals)

    if style == "bottom":  # chitarra: fondamentale + quinta + settima, senza la terza
        notes = [base]
        if 7 in intervals:
            notes.append(base + 7)
        for iv in (10, 11):
            if iv in intervals:
                notes.append(base + iv)
        return sorted(set(notes))

    if style == "hendrix":  # chitarra: fondamentale sola in basso (pollice) + resto un'ottava sopra
        notes = [base] + [base + 12 + iv for iv in intervals if iv != 0]
        return sorted(set(notes))

    if style == "triad":
        chosen = sorted(set(intervals))[:3]
        return [base + iv for iv in chosen]

    if style == "power":
        notes = [base]
        if 7 in intervals:
            notes.append(base + 7)
        return notes

    if style == "drop2":
        notes = _close_position_notes(base, intervals)
        if len(notes) >= 2:
            notes[-2] -= 12
        return sorted(notes)

    if style == "drop3":
        notes = _close_position_notes(base, intervals)
        if len(notes) >= 3:
            notes[-3] -= 12
        return sorted(notes)

    if style == "barre":
        # Accordo "a barre": impilamento pieno con fondamentale raddoppiata
        # sopra, per un suono corposo simile a un accordo a 6 corde.
        notes = [base] + [base + iv for iv in intervals] + [base + 12]
        return sorted(set(notes))

    if style == "Caged":  # forma C: fondamentale in basso, impilamento stretto
        return _close_position_notes(base, intervals)

    if style == "cAged":  # forma A: fondamentale + quinta raddoppiata in alto
        notes = _close_position_notes(base, intervals)
        if 7 in intervals:
            notes.append(base + 7 + 12)
        return sorted(set(notes))

    if style == "caGed":  # forma G: fondamentale raddoppiata su due ottave (tipico suono "pieno")
        notes = _close_position_notes(base, intervals) + [base + 12, base + 24]
        return sorted(set(notes))

    if style == "cagEd":  # forma E: accordo a 6 corde pieno, fondamentale e quinta raddoppiate
        notes = _close_position_notes(base, intervals) + [base + 12]
        if 7 in intervals:
            notes.append(base + 7 + 12)
        return sorted(set(notes))

    if style == "cageD":  # forma D: posizione piu' alta e compatta, senza raddoppi
        chosen = sorted(set(intervals))[:3]
        return sorted(base + 12 + iv for iv in chosen)

    if style == "left":  # tastiera: sinistra fondamentale/quinta grave, destra il resto
        notes = [base - 12]
        if 7 in intervals:
            notes.append(base - 12 + 7)
        notes += [base + iv for iv in intervals if iv != 0]
        return sorted(set(notes))

    if style == "right":  # tastiera: voicing compatto per sola mano destra, senza fondamentale
        notes = [base + 12 + iv for iv in intervals if iv != 0]
        return notes or [base + 12]

    if style == "spread":  # tastiera: voicing ampio a due mani
        notes = [base - 12, base]
        notes += [base + 12 + iv for iv in intervals if iv not in (0, 7)]
        return sorted(set(notes))

    # Stile non riconosciuto: fallback sicuro (non dovrebbe mai accadere,
    # _resolve_voicing_fallback normalizza sempre a uno stile valido prima)
    return [base + iv for iv in intervals]
