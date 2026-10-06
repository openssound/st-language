"""
Motore di parsing della notazione testuale semplificata descritta nelle
Specifiche di Progetto (sezioni 3, 4, 5, 6).

Pipeline:
    testo grezzo -> tokenizzazione -> espansione pattern (%Nome)
    -> scansione sequenziale con Stato Corrente (griglia + velocity)
    -> lista di Event con tempi assoluti in beat (quarti)

Il parser produce eventi "astratti" (nota/accordo/percussione): la
risoluzione in note MIDI concrete (voicing) e' demandata a chords.py e
avviene al momento dell'export/playback, perche' dipende dallo strumento
della traccia (vedi Visione del prodotto, livelli 1/2/3).
"""

import re
from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Dict, Optional, Tuple

from .instruments import PERCUSSION_MAP
from ._i18n import tr


class NotationError(Exception):
    def __init__(self, message: str, token: str = ""):
        self.token = token
        super().__init__(f"{message}" + (f" (token: '{token}')" if token else ""))


# ---------------------------------------------------------------------------
# Tokenizzazione
# ---------------------------------------------------------------------------

COMMENT_MARK = "//"
BAR_CHECK = "|"
# Ritornelli: |: ... :| (con le caselle |1. ... :| |2. ... ||) e la doppia
# stanghetta ||; valgono anche come controlli di battuta (vedi expand_repeats).
REPEAT_START, REPEAT_END, DOUBLE_BAR = "|:", ":|", "||"
RE_ENDING = re.compile(r"^\|([1-9])\.$")
RE_REPEAT_END_ENDING = re.compile(r"^:\|([1-9])\.$")
# Segnaposto interni (non scrivibili: contengono un carattere di controllo)
# che expand_repeats e i gruppi N(...) lasciano nel testo espanso, perche'
# il parser ne faccia gli eventi 'repeat' (vedi Event).
_MARK = "\x00"
LYRIC_QUOTE = '"'


def comment_spans(text: str) -> List[Tuple[int, int]]:
    """Intervalli (inizio, fine) dei commenti '//' del testo: da '//' alla
    fine della riga, esclusa. Un '//' dentro un testo cantato "..." non
    apre un commento. Il parser li ignora; l'evidenziatore li colora a
    parte."""
    if COMMENT_MARK not in text:
        return []
    spans = []
    i, n = 0, len(text)
    in_quote = False
    while i < n:
        ch = text[i]
        if ch == "\n":
            in_quote = False
        elif ch == LYRIC_QUOTE:
            in_quote = not in_quote
        elif not in_quote and text.startswith(COMMENT_MARK, i):
            j = text.find("\n", i)
            if j == -1:
                j = n
            spans.append((i, j))
            i = j
            continue
        i += 1
    return spans


def strip_comments(text: str) -> str:
    """Il testo con ogni commento '//' sostituito da altrettanti spazi:
    stesse posizioni carattere dell'originale (cosi' gli span dei token
    restano validi sul testo vero), nessun commento rimasto."""
    spans = comment_spans(text)
    if not spans:
        return text
    chars = list(text)
    for i, j in spans:
        chars[i:j] = " " * (j - i)
    return "".join(chars)


# Caratteri che chiudono un token semplice anche senza spazio: la
# stanghetta ('d*4|' sono due token) e l'inizio di un testo cantato
# ('c*4"Ma-"': la nota e la sua sillaba).
_PLAIN_STOP = (BAR_CHECK, LYRIC_QUOTE)


def tokenize_spans(text: str) -> List[Tuple[str, int, int]]:
    """Come tokenize, ma con la posizione di ogni token nel testo:
    lista di (token, inizio, fine)."""
    text = strip_comments(text)
    tokens = []
    i, n = 0, len(text)

    def _quote_end(start: int) -> int:
        """Indice della virgolette che chiude il testo cantato aperto in
        text[start]."""
        k = text.find(LYRIC_QUOTE, start + 1)
        if k == -1:
            raise NotationError(tr("Testo cantato '\"' non chiuso"), text[start:start + 20])
        return k

    def _capture_balanced(start: int, open_ch: str, close_ch: str) -> int:
        """Ritorna l'indice del carattere di chiusura bilanciato, a partire
        da text[start] == open_ch (le parentesi dentro un testo cantato
        "..." non contano)."""
        depth = 0
        k = start
        while k < n:
            c = text[k]
            if c == LYRIC_QUOTE:
                k = _quote_end(k)
            elif c == open_ch:
                depth += 1
            elif c == close_ch:
                depth -= 1
                if depth == 0:
                    return k
            k += 1
        return -1

    def _plain_end(k: int) -> int:
        """Fine di un token semplice: allo spazio, alla stanghetta, a un
        testo cantato, a ':|' (che resta alla griglia: '4:|') e a '$"'."""
        start = k
        while k < n and not text[k].isspace() and text[k] not in _PLAIN_STOP:
            if text[k] == ":" and k + 1 < n and text[k + 1] == BAR_CHECK:
                if RE_GRID.match(text[start:k + 1]):
                    k += 1
                break
            if text[k] == "$" and k + 1 < n and text[k + 1] == LYRIC_QUOTE:
                break
            k += 1
        return k

    def _with_value(k: int) -> int:
        """Fine di un blocco [...] col suo eventuale valore di nota
        attaccato ('[c e g]'2), i segni ('[c e g]$accent'), la forcella
        ('[c e g]<'), la legatura di valore ('[c e g]~') e quella di
        portamento ('[c e g](')."""
        if k < n and text[k] in "'$":
            return _plain_end(k)
        if k < n and text[k] in "<>" and (k + 1 >= n or text[k + 1] not in "<>"):
            k += 1
        if k < n and text[k] == "~":
            k += 1
        if k < n and text[k] in "()":
            k += 1
        return k

    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch == BAR_CHECK:
            # | da sola, |: (inizio ritornello), || (doppia stanghetta), |1. (casella)
            m = re.match(r"\|(?::|\||[1-9]\.)?", text[i:])
            tokens.append((m.group(), i, i + len(m.group())))
            i += len(m.group())
            continue
        if ch == ":" and i + 1 < n and text[i + 1] == BAR_CHECK:
            m = re.match(r":\|(?:[1-9]\.)?", text[i:])       # :| (fine ritornello), :|2.
            tokens.append((m.group(), i, i + len(m.group())))
            i += len(m.group())
            continue
        if ch == "$" and i + 1 < n and text[i + 1] == LYRIC_QUOTE:
            k = _quote_end(i + 1)                                # $"rit." (indicazione di testo)
            tokens.append((text[i:k + 1], i, k + 1))
            i = k + 1
            continue
        if ch == LYRIC_QUOTE:
            k = _quote_end(i)
            tokens.append((text[i:k + 1], i, k + 1))
            i = k + 1
            continue
        j = i
        while j < n and text[j].isdigit():
            j += 1
        if j < n and text[j] == "[":
            if "]" not in text[j:]:
                raise NotationError(tr("Blocco '[' non chiuso"), text[i:j + 20])
            k = _with_value(text.index("]", j) + 1)
            tokens.append((text[i:k], i, k))
            i = k
            continue
        if j < n and text[j] == "(":
            k = _capture_balanced(j, "(", ")")
            if k == -1:
                raise NotationError(tr("Gruppo '(' non chiuso"), text[i:j + 20])
            tokens.append((text[i:k + 1], i, k + 1))
            i = k + 1
            continue
        if ch == "{":
            k = _capture_balanced(i, "{", "}")
            if k == -1:
                raise NotationError(tr("Blocco di voci '{0}' non chiuso", "{"), text[i:i + 20])
            tokens.append((text[i:k + 1], i, k + 1))
            i = k + 1
            continue
        k = _plain_end(i)
        tokens.append((text[i:k], i, k))
        i = k
    return tokens


def split_voices(inner: str) -> List[str]:
    """Il contenuto di un blocco di voci { ... ; ... } diviso nelle sue
    voci, ai ';' che non stanno dentro un gruppo, un blocco, un altro
    blocco di voci o un testo cantato."""
    voices, depth, start, in_quote = [], 0, 0, False
    for k, c in enumerate(inner):
        if c == LYRIC_QUOTE:
            in_quote = not in_quote
        elif in_quote:
            continue
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == ";" and depth == 0:
            voices.append(inner[start:k])
            start = k + 1
    voices.append(inner[start:])
    return voices


def rewrite_tokens(text: str, rewrite) -> str:
    """Il testo con ogni token di primo livello sostituito da
    rewrite(token), lasciando com'e' tutto il resto (spazi, a capo,
    commenti): per le operazioni che cambiano le note (trasposizione,
    congelamento degli accordi) senza buttare via l'impaginazione."""
    out = []
    pos = 0
    for tok, start, end in tokenize_spans(text):
        out.append(text[pos:start])
        new = rewrite(tok)
        out.append(text[start:end] if new == tok else new)
        pos = end
    out.append(text[pos:])
    return "".join(out)


def tokenize(text: str) -> List[str]:
    """Divide una stringa di notazione in token, trattando i blocchi [...]
    (eventi simultanei) e i gruppi (...)  (sequenze ripetute, con eventuale
    moltiplicatore numerico anteposto, es. '4(2C7 2e c d 2A7)') come un
    unico token ciascuno, anche con spazi interni. I gruppi possono essere
    annidati (le parentesi tonde sono bilanciate correttamente). I commenti
    '//' (fino a fine riga) sono ignorati; la stanghetta '|' (controllo di
    battuta) e' sempre un token a se', anche se attaccata a una nota."""
    return [tok for tok, _, _ in tokenize_spans(text)]


# ---------------------------------------------------------------------------
# Regex di classificazione (vedi tabella sintattica 3.2)
# ---------------------------------------------------------------------------

# %Nome puo' essere preceduto da un moltiplicatore di ripetizione (es. 3%Riff)
# e seguito dalla trasposizione in semitoni (es. %Tema+7, 2%Tema-3).
RE_PATTERN_REF = re.compile(r"^(\d*)%(\w+?)([+-]\d+)?$")
# &Nome richiama un file MIDI dalla libreria (ricerca ricorsiva nelle sottocartelle,
# funzionalita' 5), con lo stesso moltiplicatore di ripetizione di %Nome. Il nome
# puo' anche essere un percorso qualificato con sottocartella (es. &Blues/bass_line).
RE_MIDI_REF = re.compile(r"^(\d*)&([\w/-]+)$")
# N(...) ripete N volte la sequenza di token racchiusa tra parentesi tonde
# (a differenza di [...], che e' simultaneita', non sequenza ripetuta).
RE_REPEAT_GROUP = re.compile(r"^(\d*)\((.*)\)$", re.DOTALL)
# Lettera di tuplet opzionale dopo il numero della griglia: quanti spazi
# "normali" (potenza di due) occupano le sue note - es. 8T: (terzine di
# ottavi: 3 note nello spazio di 2), 16Q: (quintine di sedicesimi: 5 note
# nello spazio di 4), 8S: (settimine di ottavi: 7 note nello spazio di 4).
# Rapporto standard per ciascuna: la stessa convenzione con cui la terzina
# esisteva gia' (3:2), generalizzata alle tuplet dispari piu' comuni oltre
# la terzina, che si appoggiano tutte allo spazio della potenza di due
# immediatamente inferiore (4, non 8) tranne la terzina stessa (2).
# Frazioni esatte, non float: il parser somma le durate una dopo l'altra per
# calcolare gli attacchi, e con 1/3 in virgola mobile l'errore si accumula
# (dopo qualche terzina un attacco sul beat 8 risultava 7.999999999999999,
# finendo nella battuta precedente per chi calcola floor(start / 4)).
TUPLET_SCALE = {
    "T": Fraction(2, 3),
    "Q": Fraction(4, 5),
    "S": Fraction(4, 7),
}
RE_GRID = re.compile(r"^(\d+)([TQS])?:$")
# Valore di nota esplicito, in alternativa alla griglia: c*4'8. (croma
# puntata), d'16 (semicroma), [c e g]'2 (minima), r'4 (pausa di
# semiminima), e'8T (croma di terzina). Il numero e' la figura (1 =
# semibreve ... 64), la lettera opzionale la tuplet come per la griglia
# (8T: ecc.), i punti allungano di meta' (uno) o di tre quarti (due). Vale
# solo per quel token: la griglia corrente non cambia. Va in fondo al
# token, prima o dopo l'eventuale articolazione (c'8! = c!'8).
RE_NOTE_VALUE = re.compile(r"^(.+?)'(\d+)([TQS]?)(\.{0,2})([!x_]?)$")
NOTE_VALUES = (1, 2, 4, 8, 16, 32, 64)
_DOT_SCALE = {0: Fraction(1), 1: Fraction(3, 2), 2: Fraction(7, 4)}
# Blocco di voci { voce1 ; voce2 ... }: sequenze che partono insieme.
RE_VOICES = re.compile(r"^\{(.*)\}$", re.DOTALL)
# Velocity: numero esplicito oppure dinamica classica (pppp/ppp/pp/p/mp/mf/f/ff/fff/ffff)
DYNAMICS_TO_VELOCITY = {
    "pppp": 10, "ppp": 23, "pp": 36, "p": 49, "mp": 62,
    "mf": 75, "f": 88, "ff": 101, "fff": 114, "ffff": 127,
}
RE_VELOCITY = re.compile(r"^(pppp|ppp|pp|p|mp|mf|ffff|fff|ff|f|\d+)@$")
RE_REST = re.compile(r"^(\d*)r$")
# Nota melodica, con modificatore opzionale finale: '!' staccato, 'x' mute, '_' legato.
# Alterazione: '#' diesis; 'b' o '♭' bemolle (equivalenti, vedi core.chords.
# note_name_to_pc). Il '-' NON e' un bemolle nel linguaggio: e' solo una scorciatoia
# di digitazione dell'editor, che lo sostituisce con '♭' quando viene battuto subito
# dopo una lettera nota (per evitare l'ambiguita' con la lettera nota 'b').
# Ottava: '*n' (es. c*5); senza, quella di default dello strumento.
# Alterazione: anche 'n' (o '♮', bequadro) per togliere quella della
# tonalita' (key=, vedi _PitchState). Ottava: '*n' esplicita, oppure nel
# modo relativo (rel:) '*+' e '*-' per salire o scendere di un'ottava.
RE_NOTE = re.compile(r"^(\d*)([a-g])([#b♭n♮]?)(\*\d+|\*\++|\*-+)?([!x_])?$")
# Suffisso opzionale '.stile' (es. Cmaj7.drop2) per forzare il voicing:
# vedi core.chords.ALL_VOICINGS per l'elenco degli stili validi. La classe
# di caratteri della qualita' include '#' per accordi come '7#9' e '°' per
# l'alias di 'dim'/'dim7' ('C°', 'C°7').
# Dopo l'eventuale '.stile', '/' introduce il basso alternativo (lettera
# nota maiuscola, es. 'C/E' = Do col basso Mi); l'ottava si scrive con
# '*n', anche insieme al basso (es. 'C/E*4').
# Modificatore opzionale finale (dopo l'eventuale ottava): '!' staccato,
# 'x' mute, '_' legato, stesso schema delle note (vedi Event.articulation).
# La qualita' e' la piu' corta che fa tornare il resto del token: cosi'
# una 'x' finale e' il modificatore (Cmaj7x = Cmaj7 stoppato), non parte
# della qualita' (nessuna qualita' finisce con 'x').
RE_CHORD = re.compile(
    r"^(\d*)([A-G])([#b♭]?)([A-Za-z0-9#°]*?)(?:\.([A-Za-z0-9]+))?"
    r"(?:/([A-G][#b♭]?))?(?:\*(\d+))?([!x_])?$"
)
RE_PERC = re.compile(r"^(\d*)([a-z][a-z_0-9]*)$")
# Portamento/slide tra due o piu' note: c*4>d*4,
# oppure una catena c*4>d*4>c*4 (bend-and-release: sale e poi rilascia).
# Ogni tappa puo' avere un proprio
# moltiplicatore di durata (es. 2c*4>3d*4, vedi _slide_segment_durations
# per la semantica): il gruppo catturato e' l'intera catena grezza, da
# ripassare a RE_SLIDE_POINT tappa per tappa dopo lo split su '>'.
_SLIDE_POINT_PATTERN = r"\d*[a-g][#b♭n♮]?(?:\*\d+|\*\++|\*-+)?"
RE_SLIDE = re.compile(rf"^({_SLIDE_POINT_PATTERN}(?:>{_SLIDE_POINT_PATTERN})+)$")
RE_SLIDE_POINT = re.compile(r"^(\d*)([a-g])([#b♭n♮]?)(\*\d+|\*\++|\*-+)?$")


def _check_pitch_range(letter: str, octave: int, tok: str) -> None:
    """Solleva NotationError se la nota esce dal range MIDI 0-127 (es.
    'a*9'): altrimenti la validazione la accetterebbe e l'export MIDI
    fallirebbe dopo, con un errore incomprensibile per l'utente."""
    from .chords import pitch_to_midi  # import locale: evita dipendenza circolare
    if not 0 <= pitch_to_midi(letter, octave) <= 127:
        raise NotationError(tr("Nota fuori dall'estensione MIDI (la piu' acuta e' g*9)"), tok)


LETTERS = "cdefgab"
# Modo delle ottave: 'rel:' (relative, come in LilyPond) e 'abs:' (assolute,
# il default); tonalita' delle note: 'key=G', 'key=Dm', 'key=off'.
RE_PITCH_MODE = re.compile(r"^(rel|abs):$")
RE_KEY_MODE = re.compile(r"^key=(?:([A-G][#b♭]?m?)|off)$")
_LETTER_FIFTHS = {"f": -1, "c": 0, "g": 1, "d": 2, "a": 3, "e": 4, "b": 5}


def key_signature_alters(name: str) -> Dict[str, str]:
    """Le alterazioni della tonalita' (es. 'G' -> {'f': '#'}, 'Dm' ->
    {'b': 'b'}): lettera nota -> '#' o 'b'."""
    m = re.match(r"^([A-G])([#b♭]?)(m?)$", name)
    if not m:
        raise NotationError(tr("Tonalita' non valida: '{key}'", key=name))
    letter, accidental, minor = m.groups()
    fifths = _LETTER_FIFTHS[letter.lower()] + (7 if accidental == "#" else -7 if accidental else 0)
    fifths -= 3 if minor else 0
    if not -7 <= fifths <= 7:
        raise NotationError(tr("Tonalita' con troppe alterazioni: '{key}' (usa quella enarmonica)", key=name))
    if fifths >= 0:
        return {letter: "#" for letter in "fcgdaeb"[:fifths]}
    return {letter: "b" for letter in "beadgcf"[:-fifths]}


class _PitchState:
    """Come si leggono le altezze delle note: ottave assolute o relative
    (rel:, ogni nota senza '*n' va all'ottava piu' vicina alla precedente,
    contando le lettere: al piu' una quarta sopra o sotto; '*+' e '*-' la
    spostano di un'ottava), e le alterazioni della tonalita' (key=)."""

    def __init__(self, default_octave: int):
        self.default_octave = default_octave
        self.relative = False
        self.ref: Tuple[str, int] = ("c", default_octave)   # lettera e ottava dell'ultima nota
        self.alters: Dict[str, str] = {}
        self.key_name = ""                                   # la tonalita' scritta (key=G), se c'e'
        self.stack: List[Tuple[str, int]] = []               # riferimento all'inizio dei ritornelli
        # Trasposizione in semitoni: 'outer' viene dai pattern richiamati
        # con %Nome+N (e da quelli che li contengono), 'local' da transpose=.
        self.outer = 0
        self.local = 0

    @property
    def semitones(self) -> int:
        return self.outer + self.local

    def copy(self) -> "_PitchState":
        other = _PitchState(self.default_octave)
        other.relative, other.ref, other.alters = self.relative, self.ref, dict(self.alters)
        other.key_name, other.outer, other.local = self.key_name, self.outer, self.local
        return other

    def spell_transposed(self, name: str, octave: int, semitones: int, tok: str) -> Tuple[str, int]:
        """(lettera con alterazione, ottava) di una nota scritta come
        'name' all'ottava 'octave', trasposta di 'semitones'. Se c'e' una
        tonalita' si scrive nella tonalita' trasposta, altrimenti coi
        bemolli se la nota scritta ne aveva uno, con i diesis negli altri
        casi."""
        from .chords import pitch_to_midi
        midi = pitch_to_midi(name, octave) + semitones
        if not 0 <= midi <= 127:
            raise NotationError(tr("La trasposizione porta la nota fuori dall'estensione MIDI"), tok)
        alters = (key_signature_alters(_transpose_key_name(self.key_name, semitones))
                  if self.key_name else {})
        flats = (any(a == "b" for a in alters.values()) if self.key_name
                 else len(name) > 1 and name[1] in "b♭")
        spelled, octave = spell_midi(midi, alters, flats)
        # spell_midi dice come si scrive nel testo (la lettera da sola prende
        # l'alterazione della tonalita'); l'evento porta il nome esplicito
        if spelled.endswith("n"):
            spelled = spelled[:-1]
        elif spelled in alters:
            spelled += alters[spelled]
        return spelled, octave

    def set_relative(self, relative: bool) -> None:
        self.relative = relative
        self.ref = ("c", self.default_octave)

    def nearest_octave(self, letter: str) -> int:
        """L'ottava di 'letter' piu' vicina alla nota precedente (rel:)."""
        ref_letter, ref_octave = self.ref
        base = ref_octave * 7 + LETTERS.index(ref_letter)
        step = (LETTERS.index(letter) - LETTERS.index(ref_letter)) % 7
        return (base + step if step <= 3 else base + step - 7) // 7

    def resolve(self, letter: str, accidental: str, mark: Optional[str], tok: str) -> Tuple[str, int]:
        """(lettera con alterazione, ottava) di una nota scritta."""
        if accidental in ("n", "♮"):
            accidental = ""
        elif not accidental:
            accidental = self.alters.get(letter, "")
        if mark and mark[1:].isdigit():
            octave = int(mark[1:])
        elif self.relative:
            octave = self.nearest_octave(letter) + (mark.count("+") - mark.count("-") if mark else 0)
        elif mark:
            raise NotationError(tr("'*+' e '*-' cambiano l'ottava solo nel modo relativo (rel:)"), tok)
        else:
            octave = self.default_octave
        _check_pitch_range(letter + accidental, octave, tok)
        self.ref = (letter, octave)
        if self.semitones:
            return self.spell_transposed(letter + accidental, octave, self.semitones, tok)
        return letter + accidental, octave


def _parse_slide_points(chain: str, default_octave: int, pitch: Optional["_PitchState"] = None
                        ) -> List[Tuple[Optional[int], str, int]]:
    """Scompone la catena grezza catturata da RE_SLIDE (gia' validata nella
    sua interezza dal match esterno) in [(moltiplicatore_esplicito_o_None,
    lettera[+alterazione], ottava), ...], una tappa per ogni punto del
    bending, nell'ordine in cui compaiono. Il moltiplicatore e' None se
    quella tappa non ne aveva uno scritto (vedi _slide_segment_durations)."""
    pitch = pitch or _PitchState(default_octave)
    points = []
    for point_str in chain.split(">"):
        pm = RE_SLIDE_POINT.match(point_str)
        mult_s, letter, acc, mark = pm.groups()
        mult = int(mult_s) if mult_s else None
        name, octave = pitch.resolve(letter, acc, mark, chain)
        points.append((mult, name, octave))
    return points


def _slide_segment_durations(points: List[Tuple[Optional[int], str, int]],
                              grid_beats: Fraction) -> List[Fraction]:
    """Durata (in beat) di ciascun segmento di uno slide, una per tappa:
    per le tappe 1..N-1 e' la rampa che PARTE da quella tappa verso la
    successiva e vale il suo moltiplicatore (1 se manca) per l'unita'; per
    l'ultima e' quanto la nota resta ferma sull'altezza d'arrivo e vale il
    suo moltiplicatore (0 se manca: lo slide finisce arrivando).

    c*4>d*4 dura cosi' un'unita' come una nota; 2c*4>3d*4 sale in 2 e resta
    ferma per 3; c*4>d*4>c*4 (bend-and-release) sale in 1 e scende in 1."""
    durations = [(mult if mult is not None else 1) * grid_beats for mult, _, _ in points[:-1]]
    last_mult = points[-1][0]
    durations.append((last_mult or 0) * grid_beats)
    return durations


def split_note_value(tok: str) -> Tuple[str, str]:
    """(token senza valore di nota, valore come scritto: "'8." o "").
    c*4'8. -> ('c*4', "'8."); c'8! -> ('c!', "'8"); c'2< -> ('c', "'2<");
    2c< -> ('2c', "<"); c'2~( -> ('c', "'2~(").

    In fondo al valore restano, in quest'ordine, la forcella (< o >), la
    legatura di valore (~) e quella di portamento (( o )): fanno parte del
    "valore" restituito, cosi' chi ricompone il token (trasposizione,
    congelamento) li conserva; vedi split_marks."""
    if tok.startswith(LYRIC_QUOTE) or tok.startswith("{"):
        return tok, ""
    tail = ""
    if len(tok) > 1 and tok[-1] in "()":
        tok, tail = tok[:-1], tok[-1]
    if len(tok) > 1 and tok[-1] == "~":
        tok, tail = tok[:-1], "~" + tail
    if len(tok) > 1 and tok[-1] in "<>" and tok[-2] not in "<>":
        tok, tail = tok[:-1], tok[-1] + tail
    m = RE_DECORATIONS.search(tok)
    if m and m.start() > 0:
        tok, tail = tok[:m.start()], m.group(1) + tail
    m = RE_NOTE_VALUE.match(tok)
    if not m:
        return tok, tail
    base, number, tuplet, dots, articulation = m.groups()
    return base + articulation, f"'{number}{tuplet}{dots}{tail}"


def split_marks(value: str) -> Tuple[str, str, bool, str, List[str]]:
    """Il valore restituito da split_note_value scomposto in (valore di
    nota, forcella, legatura di valore, legatura di portamento, segni)."""
    slur = value[-1] if value[-1:] in ("(", ")") else ""
    value = value[:len(value) - len(slur)]
    tie = value.endswith("~")
    value = value[:-1] if tie else value
    hairpin = value[-1] if value[-1:] in ("<", ">") else ""
    value = value[:len(value) - len(hairpin)]
    decorations: List[str] = []
    m = RE_DECORATIONS.search(value)
    if m:
        decorations = m.group(1).split("$")[1:]
        value = value[:m.start()]
    return value, hairpin, tie, slur, decorations


def note_value_beats(value: str) -> Fraction:
    """Durata in quarti di un valore di nota come "'8." (vedi RE_NOTE_VALUE)."""
    m = re.match(r"^'(\d+)([TQS]?)(\.{0,2})$", value)
    if not m or int(m.group(1)) not in NOTE_VALUES:
        raise NotationError(tr("Valore di nota non valido: dopo l'apostrofo va 1, 2, 4, 8, 16, 32 o 64 "
                               "(es. c'8 croma, c'4. semiminima puntata, c'8T croma di terzina)"), value)
    number, tuplet, dots = m.groups()
    beats = Fraction(4, int(number)) * _DOT_SCALE[len(dots)]
    if tuplet:
        beats *= TUPLET_SCALE[tuplet]
    return beats


def is_lyric(tok: str) -> bool:
    return len(tok) >= 2 and tok[0] == LYRIC_QUOTE and tok[-1] == LYRIC_QUOTE


# Tempo inline in una traccia (BPM, da qui in poi per tutto il brano): tempo=120
RE_TEMPO_SET = re.compile(r"^tempo=(\d+)$")
# Rampe: '>>' o '<<' (equivalenti), con la forma della curva facoltativa:
# lin (di default), exp (parte piano e accelera: i fade dei volumi), log
# (parte veloce e rallenta), s (morbida a inizio e fine).
RE_RAMP_UP = re.compile(r"^>>(lin|exp|log|s)?$")
RE_RAMP_DOWN = re.compile(r"^<<(lin|exp|log|s)?$")
RAMP_CURVES = {
    "lin": lambda x: x,
    "exp": lambda x: x * x,
    "log": lambda x: 1 - (1 - x) * (1 - x),
    "s": lambda x: x * x * (3 - 2 * x),
}

# Automazioni continue della traccia (controlli MIDI del canale): volume
# (CC7), espressione (CC11, la dinamica dentro le note tenute), pan (CC10,
# da -1 sinistra a 1 destra), modulazione (CC1, vibrato), mandate a
# riverbero (CC91) e chorus (CC93). 'vol=60' imposta il valore da li' in
# poi; 'vol=40 >> ... vol=100' va da 40 a 100 nel tempo fra i due comandi.
# Oltre ai nomi, 'ccN=' (N = 0-119) scrive un controller MIDI qualsiasi
# (cc74 = brillantezza su molti synth) e 'bend=' il pitch bend in semitoni
# (-24..24, l'ampiezza impostata dall'esportazione).
RE_CONTROL = re.compile(r"^(vol|expr|pan|mod|rev|cho|bend|tune|cc\d{1,3})=(-?\d+(?:\.\d+)?)$")
# tune=N: accordatura dello strumento in cent (RPN 1 Channel Fine Tuning).
CONTROL_RANGES = {"vol": (0, 127), "expr": (0, 127), "pan": (-1, 1), "mod": (0, 127),
                  "rev": (0, 127), "cho": (0, 127), "bend": (-24, 24), "tune": (-100, 100)}
CONTROL_DEFAULTS = {"vol": 100, "expr": 127, "pan": 0, "mod": 0, "rev": 0, "cho": 0, "bend": 0, "tune": 0}
# Controlli che tengono i decimali (gli altri sono arrotondati all'intero).
CONTROL_DECIMAL = ("pan", "bend")
# Ultimo numero di controller ammesso da 'ccN=' (120-127 sono messaggi di modo del canale).
CC_MAX = 119

# Segni sulle note, in fondo al token prima della forcella e delle legature:
# c$tr, C$fermata, [c e g]$accent$tenuto (vedi split_note_value).
DECORATIONS = ("accent", "marcato", "tenuto", "fermata", "tr", "mordent", "turn")
RE_DECORATIONS = re.compile(r"((?:\$[a-z]+)+)$")
# Indicazione di testo sopra il pentagramma: $"rit.", $"dolce".
RE_TEXT = re.compile(r'^\$"(.*)"$', re.DOTALL)

# Swing: 'swing=N' sposta la seconda croma di ogni coppia, 'swing16=N' la
# seconda semicroma; N e' la percentuale della coppia data alla prima nota
# (50 = diritto, 66 = terzinato, fino a 80).
RE_SWING = re.compile(r"^swing(16)?=(\d+)$")
SWING_RANGE = (50, 80)

# Micro-timing: 'shift=N' anticipa (N < 0) o ritarda (N > 0) di N
# millisecondi le note che seguono, senza cambiare il ritmo scritto;
# 'shift=0' torna a tempo.
RE_SHIFT = re.compile(r"^shift=(-?\d+)$")
SHIFT_RANGE = (-500, 500)

# Ancora di battuta: 'bar=N' porta il cursore all'inizio della battuta N
# (con i silenzi che servono); se la traccia e' gia' oltre, resta dov'e' e
# l'editor segnala l'avviso (vedi notation_warnings).
RE_BAR_ANCHOR = re.compile(r"^bar=(\d+)$")

# Trasposizione: 'transpose=N' sposta di N semitoni le note, gli accordi e
# gli slide che seguono (0 per tornare all'altezza scritta); '%Nome+N' fa
# suonare un pattern N semitoni sopra (o sotto, con '-') e poi torna
# com'era.
RE_TRANSPOSE = re.compile(r"^transpose=(-?\d+)$")
TRANSPOSE_RANGE = (-60, 60)
BAR_ANCHOR_MAX = 99999


# ---------------------------------------------------------------------------
# Eventi
# ---------------------------------------------------------------------------

@dataclass
class Event:
    start: float          # in beat (quarti di nota)
    duration: float        # in beat
    kind: str               # note|chord|percussion|rest|block|sustain|tempo_marker|slide
    velocity: int = 80
    letter: Optional[str] = None       # per note (e per l'estremo di partenza di uno slide)
    symbol: Optional[str] = None       # per chord
    voicing: Optional[str] = None      # per chord: suffisso '.stile' opzionale (vedi core.chords.ALL_VOICINGS)
    bass: Optional[str] = None         # per chord: basso alternativo opzionale (es. 'C/E' -> bass='E')
    name: Optional[str] = None         # per percussion; per sustain: "on"/"off"
    octave: Optional[int] = None
    items: Optional[List[dict]] = None  # per block: [{kind, letter/symbol/name, octave}, ...]
    articulation: Optional[str] = None  # staccato|mute|legato (note e accordi)
    # per kind='slide': tappe successive alla partenza (letter/octave sopra),
    # nell'ordine in cui il bending le attraversa - [(lettera, ottava), ...],
    # un solo elemento per il classico slide a due punti (c*4>d*4), due o
    # piu' per una catena (c*4>d*4>c*4, bend-and-release).
    slide_points: Optional[List[Tuple[str, int]]] = None
    # per kind='slide': durata (in beat) di ciascun segmento della catena,
    # vedi _slide_segment_durations - N valori per N tappe totali (partenza
    # inclusa): le prime N-1 sono le rampe tra tappe consecutive, l'ultima
    # e' l'attesa sull'altezza finale. La somma coincide sempre con
    # 'duration' sopra.
    slide_segment_durations: Optional[List[float]] = None
    bpm: Optional[int] = None               # per kind='tempo_marker'
    # Voce dentro la traccia: 1 fuori dai blocchi { ; }, poi 1, 2... per le
    # voci di un blocco (la partitura le scrive come voci separate).
    voice: int = 1
    # Sillaba del testo cantato ("Ma-": la parola continua; "_": la nota
    # prolunga la sillaba precedente), vedi la sezione testo cantato.
    lyric: Optional[str] = None
    # per kind='control' (automazioni, vedi RE_CONTROL): name e' il
    # parametro (vol, expr, pan, mod, rev, cho), value il valore (di arrivo,
    # per una rampa); una rampa ha duration > 0, start_value e la curva.
    value: Optional[float] = None
    start_value: Optional[float] = None
    curve: Optional[str] = None
    # Legatura di portamento (c( d e f)): "start" sulla prima nota, "continue"
    # su quelle in mezzo, "stop" sull'ultima; suonano legate (vedi midi).
    slur: Optional[str] = None
    # Swing attivo (vedi RE_SWING e swing_time): (durata della coppia in
    # quarti, frazione data alla prima nota), es. (1.0, 0.66) per le crome.
    swing: Optional[Tuple[float, float]] = None
    # Segni sulla nota (DECORATIONS): accent, fermata, tr...
    decorations: Optional[List[str]] = None
    # Micro-timing (vedi RE_SHIFT): millisecondi di anticipo (< 0) o
    # ritardo (> 0) con cui la nota suona rispetto a dove e' scritta.
    shift: Optional[int] = None


@dataclass
class Pattern:
    name: str
    tokens: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Trasposizione di una sequenza di token gia' espansa (note/accordi, incluso
# l'eventuale basso alternativo; le percussioni e i comandi di stato passano
# invariati). Non piu' collegata alla sintassi %Nome/N o &Nome/N (rimossa su
# richiesta: la trasposizione inline sui riferimenti a pattern/file MIDI non
# esiste piu' nella grammatica), resta una utility generica di supporto.
# ---------------------------------------------------------------------------

_MAJOR_KEY_NAMES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
_MINOR_KEY_NAMES = ["Cm", "C#m", "Dm", "Ebm", "Em", "Fm", "F#m", "Gm", "G#m", "Am", "Bbm", "Bm"]


_FLAT_NAMES = ["c", "db", "d", "eb", "e", "f", "gb", "g", "ab", "a", "bb", "b"]


def spell_midi(midi: int, alters: Dict[str, str], prefer_flat: bool = False) -> Tuple[str, int]:
    """Come scrivere l'altezza midi in una tonalita' (le sue alterazioni,
    lettera -> '#' o 'b'): una nota della scala senza alterazioni scritte,
    le altre con un diesis o un bemolle (a scelta di prefer_flat)."""
    from .chords import midi_to_pitch, note_name_to_pc
    for letter in LETTERS:
        accidental = alters.get(letter, "")
        pc = note_name_to_pc(letter + accidental)
        if pc == midi % 12:
            octave = (midi - pc) // 12 - 1
            if letter == "c" and accidental == "b":
                octave += 1          # do bemolle: l'ottava della lettera e' quella sopra
            elif letter == "b" and accidental == "#":
                octave -= 1
            return letter, octave
    name, octave = midi_to_pitch(midi)
    if prefer_flat and len(name) == 2:
        name = _FLAT_NAMES[midi % 12]
    if len(name) == 1 and name in alters:
        name += "n"                  # la tonalita' la altererebbe: bequadro
    return name, octave


def _transpose_key_name(name: str, semitones: int) -> str:
    """La tonalita' trasposta, scritta con meno alterazioni possibili."""
    from .chords import note_name_to_pc
    minor = name.endswith("m")
    pc = (note_name_to_pc(name[:-1] if minor else name) + semitones) % 12
    return (_MINOR_KEY_NAMES if minor else _MAJOR_KEY_NAMES)[pc]


class PitchRewriter:
    """Riscrive le note di un testo token per token, nell'ordine, tenendo il
    filo del modo relativo e della tonalita': trasposizione (semitones) e/o
    conversione al modo relativo (to_relative=True) e a una tonalita'
    (to_key='G', '' per nessuna). Si usa come funzione da passare a
    rewrite_tokens (un oggetto per testo, perche' ricorda lo stato)."""

    def __init__(self, semitones: int, default_octave: int, to_relative: Optional[bool] = None,
                 to_key: Optional[str] = None):
        self.semitones = semitones
        self.src = _PitchState(default_octave)
        self.dst = _PitchState(default_octave)
        self.to_relative, self.to_key = to_relative, to_key
        if to_relative is not None:
            self.dst.set_relative(to_relative)
        if to_key is not None:
            self.dst.alters = key_signature_alters(to_key) if to_key else {}
        self._body_end: List[Tuple[Tuple[str, int], Tuple[str, int]]] = []

    def __call__(self, tok: str) -> str:
        m = RE_VOICES.match(tok)
        if m:
            src, dst = self.src, self.dst
            voices = []
            for voice in split_voices(m.group(1)):
                self.src, self.dst = src.copy(), dst.copy()
                voices.append(" ".join(t for t in (self(t) for t in tokenize(voice)) if t))
            self.src, self.dst = src, dst
            return "{ " + " ; ".join(voices) + " }"
        m = RE_REPEAT_GROUP.match(tok)
        if m:
            mult_s, inner = m.groups()
            return f"{mult_s}(" + " ".join(t for t in (self(t) for t in tokenize(inner)) if t) + ")"
        m = RE_PITCH_MODE.match(tok)
        if m:
            self.src.set_relative(m.group(1) == "rel")
            if self.to_relative is not None:
                return ""
            self.dst.set_relative(m.group(1) == "rel")
            return tok
        m = RE_KEY_MODE.match(tok)
        if m:
            self.src.alters = key_signature_alters(m.group(1)) if m.group(1) else {}
            if self.to_key is not None:
                return ""
            name = _transpose_key_name(m.group(1), self.semitones) if m.group(1) else None
            self.dst.alters = key_signature_alters(name) if name else {}
            return f"key={name}" if name else tok
        if RE_ENDING.match(tok) or RE_REPEAT_END_ENDING.match(tok):
            # nel testo espanso ogni casella segue il corpo del ritornello
            number = int(re.search(r"(\d)\.$", tok).group(1))
            if number == 1:
                self._body_end.append((self.src.ref, self.dst.ref))
            elif self._body_end:
                self.src.ref, self.dst.ref = self._body_end[-1]
            return tok
        if tok.startswith(LYRIC_QUOTE) or tok.startswith("$") or tok in (BAR_CHECK, REPEAT_START, REPEAT_END,
                                                                            DOUBLE_BAR):
            return tok
        base, value = split_note_value(tok)
        mm = re.match(r"^(\d*)\[(.*)\]$", base)
        if mm:
            mult_s, inner = mm.groups()
            self._block_refs = []
            atoms = [self._atom(t) for t in inner.split()]
            first = [k for k, t in enumerate(inner.split()) if RE_NOTE.match(t)]
            if first:
                self.src.ref, self.dst.ref = self._block_refs[first[0]]
            return f"{mult_s}[{' '.join(atoms)}]{value}"
        m = RE_SLIDE.match(base)
        if m:
            mult_s = re.match(r"^\d*", base).group()
            points = []
            for point in m.group(1).split(">"):
                pm = RE_SLIDE_POINT.match(point)
                points.append(self._note(pm.group(1), pm.group(2), pm.group(3), pm.group(4), "", point))
            return ">".join(points) + value
        return self._atom(base) + value

    _block_refs: List[tuple] = []

    def _atom(self, tok: str) -> str:
        m = RE_NOTE.match(tok)
        if m:
            mult, letter, accidental, mark, modifier = m.groups()
            out = self._note(mult, letter, accidental, mark, modifier, tok)
            self._block_refs = self._block_refs + [(self.src.ref, self.dst.ref)]
            return out
        self._block_refs = self._block_refs + [None]
        m = RE_CHORD.match(tok)
        if m and self.semitones:
            from .chords import transpose_chord_root, transpose_pitch
            mult, letter, accidental, suffix, voicing, bass, octv, modifier = m.groups()
            try:
                new_symbol = transpose_chord_root(letter + accidental + suffix, self.semitones)
            except ValueError:
                return tok
            bass_part = f"/{transpose_pitch(bass, 4, self.semitones)[0].upper()}" if bass else ""
            return (f"{mult or ''}{new_symbol}{'.' + voicing if voicing else ''}{bass_part}"
                    f"{'*' + octv if octv else ''}{modifier or ''}")
        return tok

    def _note(self, mult, letter, accidental, mark, modifier, tok) -> str:
        from .chords import pitch_to_midi
        name, octave = self.src.resolve(letter, accidental or "", mark, tok)
        midi = pitch_to_midi(name, octave) + self.semitones
        if self.semitones == 0 and not self.dst.alters and not self.src.alters:
            new_name, new_octave = (letter + (accidental or "") if accidental not in ("n", "♮") else letter), octave
        else:
            new_name, new_octave = self._spell(midi)
        base = new_name[0]
        keep_explicit = (mark or "")[1:].isdigit() and self.to_relative is None
        if self.dst.relative and not keep_explicit:
            shift = new_octave - self.dst.nearest_octave(base)
            octave_part = ("*" + "+" * shift if shift > 0 else "*" + "-" * -shift) if shift else ""
        else:
            octave_part = f"*{new_octave}"
        self.dst.ref = (base, new_octave)
        return f"{mult or ''}{new_name}{octave_part}{modifier or ''}"

    def _spell(self, midi: int) -> Tuple[str, int]:
        """Come scrivere l'altezza midi nella tonalita' di destinazione."""
        return spell_midi(midi, self.dst.alters)


def transpose_tokens(tokens: List[str], semitones: int, default_octave: int) -> List[str]:
    """I token trasposti di 'semitones' (vedi PitchRewriter)."""
    if semitones == 0:
        return tokens
    rewriter = PitchRewriter(semitones, default_octave)
    return [rewriter(tok) for tok in tokens]


def relative_text(text: str, default_octave: int, key: Optional[str] = None) -> str:
    """Il testo riscritto con le ottave relative (rel:) e, se data, la
    tonalita' (key=): stesse note, impaginazione e commenti come prima."""
    rewriter = PitchRewriter(0, default_octave, to_relative=True, to_key=key or "")
    body = rewrite_tokens(text, rewriter)
    header = "rel:" + (f" key={key}" if key else "")
    return header + " " + body.lstrip()


def map_nested_tokens(tok: str, fn) -> str:
    """fn applicata al token e, dentro i gruppi N(...) e i blocchi di voci
    { ; }, a ciascun token interno (ricostruendo il gruppo o il blocco)."""
    m = RE_VOICES.match(tok)
    if m:
        voices = [" ".join(map_nested_tokens(t, fn) for t in tokenize(v)) for v in split_voices(m.group(1))]
        return "{ " + " ; ".join(voices) + " }"
    m = RE_REPEAT_GROUP.match(tok)
    if m:
        mult_s, inner = m.groups()
        return f"{mult_s}(" + " ".join(map_nested_tokens(t, fn) for t in tokenize(inner)) + ")"
    return fn(tok)


# ---------------------------------------------------------------------------
# Espansione dei pattern (%Nome) e dei riferimenti MIDI (&Nome) - sostituzione
# ricorsiva, con supporto a ripetizione (moltiplicatore)
# ---------------------------------------------------------------------------

# Chi risolve i riferimenti &Nome a file MIDI: (nome, cartella) -> token,
# FileNotFoundError se non c'e'. La libreria da sola non ne ha (SoundText
# registra la sua libreria midi/, vedi set_midi_ref_resolver).
_midi_ref_resolver = None


def set_midi_ref_resolver(fn) -> None:
    global _midi_ref_resolver
    _midi_ref_resolver = fn


def expand_patterns(tokens: List[str], patterns: Dict[str, Pattern],
                     midi_dir: Optional[str] = None, default_octave: int = 4,
                     _depth: int = 0) -> List[str]:
    if _depth > 32:
        raise NotationError(tr("Riferimento a pattern o file MIDI troppo profondo o ciclico"))
    out = []
    for t in tokens:
        m = RE_PATTERN_REF.match(t)
        if m:
            mult_s, name, offset = m.groups()
            mult = int(mult_s) if mult_s else 1
            if name not in patterns:
                raise NotationError(tr("Pattern '%{name}' non definito", name=name), t)
            semitones = int(offset) if offset else 0
            if not TRANSPOSE_RANGE[0] <= semitones <= TRANSPOSE_RANGE[1]:
                raise NotationError(tr("Trasposizione fuori range ({0}..{1} semitoni)", *TRANSPOSE_RANGE), t)
            body = expand_patterns(patterns[name].tokens, patterns, midi_dir, default_octave, _depth + 1)
            # un pattern si legge per conto suo (ottave assolute, nessuna
            # tonalita'), qualunque sia il modo della traccia che lo usa; la
            # trasposizione in vigore, invece, lo accompagna (piu' la sua)
            push = f"{_MARK}push:{semitones}" if semitones else f"{_MARK}push"
            out.extend([push] + body * mult + [f"{_MARK}pop"])
            continue

        m = RE_MIDI_REF.match(t)
        if m:
            mult_s, name_path = m.groups()
            mult = int(mult_s) if mult_s else 1
            if _midi_ref_resolver is None:
                raise NotationError(tr("I riferimenti a file MIDI (&Nome) non sono disponibili qui"), t)
            try:
                body = _midi_ref_resolver(name_path, midi_dir)
            except FileNotFoundError:
                raise NotationError(
                    tr("File MIDI '&{name_path}' non trovato nella libreria MIDI", name_path=name_path), t
                )
            except NotationError:
                raise
            except Exception as e:      # es. riferimento ambiguo
                raise NotationError(str(e), t)
            out.extend(body * mult)
            continue

        m = RE_VOICES.match(t)
        if m:
            # Le voci restano un blocco solo; si espandono i riferimenti
            # dentro ciascuna.
            parts = [" ".join(expand_patterns(tokenize(v), patterns, midi_dir, default_octave, _depth + 1))
                     for v in split_voices(m.group(1))]
            out.append("{" + " ; ".join(parts) + "}")
            continue

        m = RE_REPEAT_GROUP.match(t)
        if m:
            mult_s, inner = m.groups()
            mult = int(mult_s) if mult_s else 1
            inner_tokens = tokenize(inner)
            body = expand_patterns(inner_tokens, patterns, midi_dir, default_octave, _depth + 1)
            if mult < 2:
                out.extend(body * mult)
                continue
            # Le ripetizioni restano segnate (eventi 'repeat'): la partitura
            # puo' scriverle come ritornello invece che per esteso.
            for k in range(mult):
                out.append(f"{_MARK}start" if k == 0 else f"{_MARK}again:{k + 1}")
                out.extend(body)
            out.append(f"{_MARK}end")
            continue

        out.append(t)
    return out


def _is_repeat_token(tok: str) -> bool:
    return tok in (REPEAT_START, REPEAT_END, DOUBLE_BAR) or bool(RE_ENDING.match(tok)) \
        or bool(RE_REPEAT_END_ENDING.match(tok))


def expand_repeats(tokens: List[str], origins: Optional[List[int]] = None,
                   lenient: bool = False) -> Tuple[List[str], List[int]]:
    """Ritornelli scritti per esteso, come li suona un musicista:

        |: corpo :|                          corpo due volte
        |: corpo |1. fine1 :| |2. fine2 ||   corpo fine1 corpo fine2

    Senza '|:' il ritornello parte dall'inizio (o dalla fine del ritornello
    precedente); le caselle sono 1., 2., 3. ... (tante ripetizioni quante
    caselle), ognuna chiusa da ':|' tranne l'ultima, che finisce a '||' o
    alla fine del testo. '|:', ':|', '|N.' e '||' valgono anche come
    controlli di battuta ('|'). Ritorna (token, origini): origins dice da
    quale token di partenza viene ciascun token (vedi _expanded_ranges).
    Con lenient i ritornelli malformati restano semplici controlli di
    battuta invece di sollevare NotationError."""
    if origins is None:
        origins = list(range(len(tokens)))
    if not any(_is_repeat_token(t) for t in tokens):
        return list(tokens), list(origins)
    toks: List[str] = []
    orig: List[int] = []
    for t, o in zip(tokens, origins):
        m = RE_REPEAT_END_ENDING.match(t)
        if m:
            toks += [REPEAT_END, f"|{m.group(1)}."]
            orig += [o, o]
        else:
            toks.append(t)
            orig.append(o)
    try:
        return _expand_repeats(toks, orig)
    except NotationError:
        if not lenient:
            raise
        return [BAR_CHECK if _is_repeat_token(t) else t for t in toks], orig


def _expand_repeats(toks: List[str], orig: List[int]) -> Tuple[List[str], List[int]]:
    out: List[str] = []
    out_o: List[int] = []

    def emit(tok: str, origin: int) -> None:
        out.append(tok)
        out_o.append(origin)

    def emit_plain(a: int, b: int) -> None:
        for k in range(a, b):
            t = toks[k]
            if t == DOUBLE_BAR:
                t = BAR_CHECK
            elif _is_repeat_token(t):
                raise NotationError(tr("Ritornello dentro un altro ritornello: i ritornelli non si annidano"), t)
            emit(t, orig[k])

    n = len(toks)
    pos = 0                  # primo token non ancora scritto
    body_start = None        # dopo il '|:' aperto
    i = 0
    while i < n:
        t = toks[i]
        if t == REPEAT_START:
            if body_start is not None:
                raise NotationError(tr("Ritornello '|:' gia' aperto: chiudilo con ':|' prima di aprirne un altro"), t)
            emit_plain(pos, i)
            emit(BAR_CHECK, orig[i])
            body_start = pos = i + 1
            i += 1
            continue
        m = RE_ENDING.match(t)
        if t == REPEAT_END or m:
            start = body_start if body_start is not None else pos
            opener = orig[start - 1] if body_start is not None else orig[i]
            endings: List[Tuple[int, int, int]] = []     # (inizio, fine, origine di chi la chiude)
            after = i + 1
            if m:
                if m.group(1) != "1":
                    raise NotationError(tr("Le caselle del ritornello vanno numerate da 1. in poi"), t)
                j, number = i, 1
                while True:
                    k = j + 1
                    while k < n and toks[k] not in (REPEAT_END, DOUBLE_BAR, REPEAT_START) \
                            and not RE_ENDING.match(toks[k]):
                        k += 1
                    if k < n and toks[k] == REPEAT_END:
                        endings.append((j + 1, k, orig[k]))
                        number += 1
                        if k + 1 < n and toks[k + 1] == f"|{number}.":
                            j = k + 1
                            continue
                        raise NotationError(tr("Dopo ':|' ci vuole la casella successiva ('|{number}.')",
                                               number=number), toks[k])
                    if k < n and toks[k] in (REPEAT_START,) or (k < n and RE_ENDING.match(toks[k])):
                        raise NotationError(tr("Casella del ritornello non chiusa: chiudila con ':|' o '||'"),
                                            toks[k])
                    endings.append((j + 1, k, orig[k] if k < n else -1))    # l'ultima: fino a || o alla fine
                    after = k + 1 if k < n else n
                    break
                if len(endings) < 2:
                    raise NotationError(tr("Un ritornello con le caselle ne vuole almeno due (|1. e |2.)"), t)
            passes = len(endings) or 2
            for p in range(passes):
                emit(f"{_MARK}start" if p == 0 else f"{_MARK}again:{p + 1}", opener)
                emit_plain(start, i)
                if endings:
                    a, b, closer = endings[p]
                    emit(BAR_CHECK, orig[a - 1])
                    emit(f"{_MARK}ending:{p + 1}", orig[a - 1])
                    emit_plain(a, b)
                    if closer >= 0:
                        emit(BAR_CHECK, closer)
                else:
                    emit(BAR_CHECK, orig[i])
            emit(f"{_MARK}end", opener)
            body_start = None
            pos = i = after
            continue
        i += 1
    if body_start is not None:
        raise NotationError(tr("Ritornello '|:' aperto ma mai chiuso con ':|'"))
    emit_plain(pos, n)
    return out, out_o


# ---------------------------------------------------------------------------
# Parsing di un singolo sotto-elemento (usato sia a livello top che dentro [...])
# ---------------------------------------------------------------------------

def _split_voicing_modifier(voicing: Optional[str], modifier: Optional[str]):
    """'C.drop2x': la 'x' finale dello stile e' il modificatore (stoppato)
    se senza di essa lo stile esiste (ma 'C.hendrix' resta lo stile)."""
    if voicing and not modifier and voicing.endswith("x"):
        from .chords import ALL_VOICINGS
        if voicing not in ALL_VOICINGS and voicing[:-1] in ALL_VOICINGS:
            return voicing[:-1], "x"
    return voicing, modifier


def _transpose_chord(symbol: str, bass: Optional[str], octave: int, semitones: int,
                     pitch: "_PitchState") -> Tuple[str, Optional[str], int]:
    """L'accordo (simbolo, basso alternativo, ottava) trasposto: la
    fondamentale e il basso cambiano nome (coi bemolli se la tonalita' li ha
    o se la fondamentale scritta ne aveva uno), l'ottava segue quando la
    fondamentale scavalca il Do."""
    from .chords import parse_chord_symbol, note_name_to_pc
    parsed = parse_chord_symbol(symbol)
    flats = (any(a == "b" for a in key_signature_alters(_transpose_key_name(pitch.key_name, semitones)).values())
             if pitch.key_name else (len(symbol) > 1 and symbol[1] in "b♭") or (bool(bass) and len(bass) > 1))
    names = [n[0].upper() + n[1:] for n in (_FLAT_NAMES if flats else _SHARP_PC_NAMES)]
    new_total = parsed.root_pc + semitones
    new_symbol = names[new_total % 12] + parsed.quality
    new_bass = None
    if bass:
        new_bass = names[(note_name_to_pc(bass) + semitones) % 12]
    return new_symbol, new_bass, octave + new_total // 12


_SHARP_PC_NAMES = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]


def _parse_atom(tok: str, default_octave: int, pitch: Optional[_PitchState] = None):
    """Ritorna un dict {kind, letter/symbol/name, octave, mult} per nota/accordo/percussione."""
    m = RE_NOTE.match(tok)
    if m:
        mult, letter, accidental, mark, modifier = m.groups()
        articulation = {"!": "staccato", "x": "mute", "_": "legato"}.get(modifier)
        name, octave = (pitch or _PitchState(default_octave)).resolve(letter, accidental, mark, tok)
        return {
            "kind": "note", "letter": name,
            "octave": octave,
            "mult": int(mult) if mult else 1,
            "articulation": articulation,
        }
    m = RE_CHORD.match(tok)
    if m:
        mult, letter, accidental, suffix, voicing, bass, octv, modifier = m.groups()
        voicing, modifier = _split_voicing_modifier(voicing, modifier)
        symbol = letter + accidental + suffix
        # Import locale per evitare dipendenza circolare
        from .chords import parse_chord_symbol, ALL_VOICINGS
        parse_chord_symbol(symbol)  # valida la qualita' (solleva NotationError-compatibile)
        if voicing and voicing not in ALL_VOICINGS:
            raise NotationError(
                tr("Stile di voicing sconosciuto: '{voicing}'. Ammessi: {0}", ', '.join(sorted(ALL_VOICINGS)), voicing=voicing),
                tok,
            )
        articulation = {"!": "staccato", "x": "mute", "_": "legato"}.get(modifier)
        octave = int(octv) if octv else default_octave
        semitones = pitch.semitones if pitch is not None else 0
        if semitones:
            symbol, bass, octave = _transpose_chord(symbol, bass, octave, semitones, pitch)
        return {
            "kind": "chord", "symbol": symbol, "voicing": voicing, "bass": bass,
            "octave": octave,
            "mult": int(mult) if mult else 1,
            "articulation": articulation,
        }
    m = RE_PERC.match(tok)
    if m:
        mult, name = m.groups()
        if name not in PERCUSSION_MAP:
            raise NotationError(
                tr("Evento percussivo sconosciuto: '{name}'. Ammessi: {0}", ', '.join(PERCUSSION_MAP), name=name),
                tok,
            )
        return {"kind": "percussion", "name": name, "mult": int(mult) if mult else 1}
    raise NotationError(tr("Token non riconosciuto dalla grammatica"), tok)


# ---------------------------------------------------------------------------
# Parser principale: scansione sequenziale con Stato Corrente
# ---------------------------------------------------------------------------

def _sings(ev: Event) -> bool:
    """Se l'evento riceve una sillaba del testo cantato (note e accordi,
    non pause ne' percussioni)."""
    return ev.kind in ("note", "chord", "slide") or (
        ev.kind == "block" and any(it["kind"] != "percussion" for it in ev.items))


def _assign_lyrics(syllables: List[str], targets: List[Event]) -> int:
    """Una sillaba per nota, nell'ordine; '_' fa durare la sillaba
    precedente anche su questa nota, '*' la lascia senza sillaba. Ritorna
    quante sillabe avanzano (piu' sillabe che note)."""
    for n, syllable in enumerate(syllables):
        if n >= len(targets):
            return len(syllables) - n
        if syllable != "*":
            targets[n].lyric = syllable
    return 0


def _pitch_key(ev: Event):
    """Cio' che una legatura di valore confronta: la stessa nota (anche
    scritta con un'altra alterazione), lo stesso accordo, lo stesso blocco."""
    from .chords import pitch_to_midi
    if ev.kind == "note":
        return ("note", pitch_to_midi(ev.letter, ev.octave))
    if ev.kind == "chord":
        return ("chord", ev.symbol, ev.octave, ev.voicing, ev.bass)
    if ev.kind == "block":
        return ("block", tuple(sorted(
            (it["kind"], pitch_to_midi(it["letter"], it["octave"]) if it["kind"] == "note"
             else (it.get("symbol"), it.get("octave"), it.get("voicing"), it.get("bass"), it.get("name")))
            for it in ev.items)))
    return (ev.kind, id(ev))


def swing_time(beat: float, swing: Optional[Tuple[float, float]]) -> float:
    """La posizione (in quarti) di un istante con lo swing: dentro ogni
    coppia di note lunga 'pair' quarti la prima meta' si allunga fino alla
    frazione 'ratio' e la seconda si accorcia di conseguenza; gli inizi
    delle coppie (i battiti, per le crome) non si spostano."""
    if not swing:
        return beat
    pair, ratio = swing
    k = beat // pair
    x = (beat - k * pair) / pair
    warped = x * 2 * ratio if x <= 0.5 else ratio + (x - 0.5) * 2 * (1 - ratio)
    return (k + warped) * pair


def parse_tokens(tokens: List[str], default_octave: int = 4, meter: Optional["Meter"] = None) -> List[Event]:
    return _parse_tokens_exact(tokens, default_octave, meter=meter)[0]


def _parse_tokens_exact(tokens: List[str], default_octave: int = 4,
                         initial_grid: Fraction = Fraction(1), lenient: bool = False,
                         ranges: Optional[List[Tuple[Fraction, Fraction]]] = None,
                         initial_velocity: int = 80, voice: int = 1,
                         extras: Optional[dict] = None,
                         pending_lyrics: Optional[List["Event"]] = None,
                         initial_controls: Optional[Dict[str, float]] = None,
                         initial_swing: Optional[Tuple[float, float]] = None,
                         initial_pitch: Optional["_PitchState"] = None,
                         initial_shift: Optional[int] = None,
                         meter: Optional["Meter"] = None,
                         origin_beat: Fraction = Fraction(0)
                         ) -> Tuple[List[Event], Fraction, Fraction]:
    """Come parse_tokens, ma ritorna anche la posizione finale esatta (in
    beat, Fraction) e la griglia attiva alla fine. Griglia e posizione sono
    tenute come frazioni esatte (vedi TUPLET_SCALE) e convertite in float
    solo nei campi degli Event. initial_grid permette di interpretare un
    frammento con la griglia che eredita nel punto in cui compare.

    Se 'ranges' e' una lista, vi si aggiunge per ogni token l'intervallo
    (inizio, fine) in beat che occupa (vuoto per i comandi di stato): e' da
    qui che compute_token_spans ricava le posizioni da evidenziare, cosi'
    che siano per costruzione le stesse della riproduzione. 'lenient' salta
    i token non validi invece di sollevare NotationError (l'evidenziazione
    non deve sparire per un errore di battitura altrove nel testo).

    Un blocco di voci { ; } interpreta ogni voce con lo stato del punto in
    cui si apre (initial_grid/initial_velocity) e la numera da 'voice' in
    su; i cambi di stato dentro una voce restano li'. Se 'extras' e' un
    dict vi si raccolgono, per indice di token, i controlli di battuta
    dentro le voci ("voice_bars": {i: (inizio, [[posizioni], ...])}) e gli
    avvisi sul testo cantato ("lyric_issues": {i: messaggio}), vedi
    notation_warnings.

    'meter' (vedi Meter) dice dove cominciano le battute, per 'bar=N'; senza,
    si usa il 4/4. 'origin_beat' e' dove il frammento comincia nel brano
    (un blocco di voci o un box): la battuta N va cercata nel brano, non nel
    frammento."""
    tokens, _origins = expand_repeats(tokens, lenient=lenient)
    grid_beats = initial_grid  # unita' di durata corrente, in beat (quarti). Default: 1/4 (nera)
    velocity = initial_velocity  # velocity corrente
    tempo = None             # tempo corrente inline (solo se la traccia usa tempo=N)
    cursor = Fraction(0)     # posizione nella timeline, in beat
    events: List[Event] = []

    # Stato per le rampe (Crescendo/diminuendo di velocity, accelerando/
    # rallentando di tempo) introdotte da >> o << subito dopo un comando N@
    # (o dinamica) / tempo=N, e chiuse dal successivo comando dello stesso tipo.
    last_state_kind = None   # 'grid' | 'velocity' | 'tempo' (ultimo comando di stato incontrato)
    pending_ramp = None      # {'kind': 'velocity'|'tempo', 'start_value': float, 'start_index': int}
    # Note che aspettano la sillaba del prossimo testo cantato "...": la
    # lista e' quella del chiamante per la prima voce di un blocco { ; }
    # (le note prima del blocco aspettano lo stesso testo).
    lyric_targets: List[Event] = pending_lyrics if pending_lyrics is not None else []
    # Legature: l'evento che continua nel prossimo token (c~ c), e quella di
    # portamento aperta con le note che ne fanno parte.
    pending_tie: Optional[Event] = None
    slur_notes: Optional[List[Event]] = None
    swing = initial_swing
    shift = initial_shift
    pitch = initial_pitch.copy() if initial_pitch is not None else _PitchState(default_octave)
    saved_pitch: List[_PitchState] = []      # modo delle altezze fuori dai pattern
    # Automazioni: valore corrente di ogni controllo e rampe aperte
    # ({nome: (inizio, valore di partenza, curva)}), indipendenti fra loro.
    controls: Dict[str, float] = dict(initial_controls or CONTROL_DEFAULTS)
    pending_controls: Dict[str, tuple] = {}

    def _control(start: Fraction, name: str, value, duration: Fraction = Fraction(0),
                 start_value=None, curve=None) -> None:
        events.append(Event(start=float(start), duration=float(duration), kind="control", name=name,
                            value=value, start_value=start_value, curve=curve, voice=voice))

    def _hairpin(sign: str, start: Fraction, duration: Fraction, tok: str) -> None:
        """Forcella su una nota: l'espressione sale (<) dalla meta' al valore
        corrente, o scende (>) alla meta', durante la nota; dopo torna quella."""
        if "expr" in pending_controls:
            raise NotationError(tr("Forcella ('<' o '>') dentro una rampa di espressione (expr=): "
                                   "chiudi prima la rampa"), tok)
        full = controls["expr"]
        half = round(full / 2)
        a, b = (half, full) if sign == "<" else (full, half)
        _control(start, "expr", b, duration, a, "lin")
        _control(start + duration, "expr", full)

    def _finalize_ramp(end_value):
        nonlocal pending_ramp
        start_value = pending_ramp["start_value"]
        start_index = pending_ramp["start_index"]
        # le automazioni (vol=, forcelle...) scritte dentro la rampa non contano
        affected = [ev for ev in events[start_index:] if ev.kind not in ("control", "repeat", "text")]
        n = len(affected)
        if n == 0 and pending_ramp["kind"] == "tempo":
            # Nessun evento dentro la rampa ('tempo=120 >> tempo=140 c'): non c'e'
            # niente su cui distribuirla, ma il valore di arrivo va comunque
            # applicato da qui in poi, come un tempo=N senza rampa.
            events.append(Event(start=float(cursor), duration=0.0, kind="tempo_marker", bpm=end_value))
        # frac va da 0 (primo evento della rampa, coincide col valore di
        # partenza) a 1 (ultimo evento, coincide col valore di arrivo): con
        # (i+1)/n il primo evento otterrebbe gia' un valore intermedio, che
        # in caso di rampa di tempo posizionata esattamente sulla stessa
        # battuta del marcatore di apertura ne sovrascriverebbe il valore
        # (stesso tick, valore diverso) nella mappa di tempo globale.
        shape = RAMP_CURVES[pending_ramp.get("curve") or "lin"]
        for i, ev in enumerate(affected):
            frac = shape(i / (n - 1) if n > 1 else 1.0)
            if pending_ramp["kind"] == "velocity":
                interp = round(start_value + (end_value - start_value) * frac)
                ev.velocity = max(1, min(127, interp))
            else:  # tempo
                interp = round(start_value + (end_value - start_value) * frac)
                events.append(Event(start=ev.start, duration=0.0, kind="tempo_marker", bpm=interp))
        pending_ramp = None

    def _add(ev: Event) -> Event:
        ev.voice = voice
        events.append(ev)
        if _sings(ev):
            lyric_targets.append(ev)
        return ev

    def _sounding(ev: Event, dur: Fraction, hairpin: str, tie: bool, slur: str,
                  start: Fraction, tok: str, decorations: Optional[List[str]] = None) -> None:
        """Aggiunge un evento che suona, con legature, forcella e swing: se
        la nota precedente finiva con '~' questo token la allunga invece di
        crearne una nuova (deve avere la stessa altezza)."""
        nonlocal pending_tie, slur_notes
        if pending_tie is not None:
            if _pitch_key(pending_tie) != _pitch_key(ev):
                raise NotationError(tr("La legatura di valore (~) collega due note diverse: "
                                       "deve arrivare alla stessa nota, accordo o blocco"), tok)
            target = pending_tie
            target.duration = float(Fraction(target.duration).limit_denominator(10 ** 6) + dur)
            if ev.articulation:
                target.articulation = ev.articulation
            for deco in decorations or ():
                if deco not in (target.decorations or []):
                    target.decorations = (target.decorations or []) + [deco]
        else:
            ev.swing = swing
            ev.shift = shift
            ev.decorations = list(decorations) if decorations else None
            target = _add(ev)
        if hairpin:
            _hairpin(hairpin, start, dur, tok)
        pending_tie = target if tie else None
        if ev.kind == "percussion":
            if slur:
                raise NotationError(tr("Una legatura di portamento va su note, accordi, blocchi o slide"), tok)
            return
        if slur == "(":
            if slur_notes is not None:
                raise NotationError(tr("Legatura di portamento gia' aperta: chiudila con ')' prima di aprirne "
                                       "un'altra"), tok)
            slur_notes = [target]
            return
        if slur_notes is not None and (not slur_notes or slur_notes[-1] is not target):
            slur_notes.append(target)
        if slur == ")":
            if slur_notes is None:
                raise NotationError(tr("')' chiude una legatura di portamento mai aperta"), tok)
            if len(slur_notes) < 2:
                raise NotationError(tr("Una legatura di portamento collega almeno due note"), tok)
            for n, note in enumerate(slur_notes):
                note.slur = "start" if n == 0 else ("stop" if n == len(slur_notes) - 1 else "continue")
            slur_notes = None

    for index, tok in enumerate(tokens):
        before = cursor
        try:
            if tok == BAR_CHECK:
                # Controllo di battuta: non suona e non sposta il cursore;
                # se cade davvero su una stanghetta lo verifica
                # check_bar_lines (avviso, non errore).
                continue

            if tok == f"{_MARK}push" or tok.startswith(f"{_MARK}push:"):
                saved_pitch.append(pitch)
                fresh = _PitchState(default_octave)
                fresh.outer = pitch.semitones + int(tok.partition(":")[2] or 0)
                pitch = fresh
                continue
            if tok == f"{_MARK}pop":
                if saved_pitch:
                    pitch = saved_pitch.pop()
                continue

            if tok.startswith(_MARK):
                # inizio, ripetizione, casella o fine di un ritornello (vedi expand_repeats)
                name, _, number = tok[1:].partition(":")
                events.append(Event(start=float(cursor), duration=0.0, kind="repeat", name=name,
                                    value=int(number) if number else None, voice=voice))
                # nel modo relativo ogni passaggio riparte dalla stessa nota
                if name == "start":
                    pitch.stack.append(pitch.ref)
                elif name == "again" and pitch.stack:
                    pitch.ref = pitch.stack[-1]
                elif name == "end" and pitch.stack:
                    pitch.stack.pop()
                continue

            m = RE_PITCH_MODE.match(tok)
            if m:
                pitch.set_relative(m.group(1) == "rel")
                continue

            m = RE_KEY_MODE.match(tok)
            if m:
                pitch.alters = key_signature_alters(m.group(1)) if m.group(1) else {}
                pitch.key_name = m.group(1) or ""
                continue

            m = RE_TRANSPOSE.match(tok)
            if m:
                semitones = int(m.group(1))
                if not TRANSPOSE_RANGE[0] <= semitones <= TRANSPOSE_RANGE[1]:
                    raise NotationError(tr("Trasposizione fuori range ({0}..{1} semitoni)", *TRANSPOSE_RANGE), tok)
                pitch.local = semitones
                continue

            m = RE_TEXT.match(tok)
            if m:
                events.append(Event(start=float(cursor), duration=0.0, kind="text", name=m.group(1),
                                    voice=voice))
                continue

            if is_lyric(tok):
                extra = _assign_lyrics(tok[1:-1].split(), lyric_targets)
                lyric_targets.clear()
                if extra and extras is not None:
                    extras.setdefault("lyric_issues", {})[index] = (
                        tr("testo cantato: 1 sillaba in piu' delle note") if extra == 1 else
                        tr("testo cantato: {n} sillabe in piu' delle note", n=extra))
                continue

            m = RE_VOICES.match(tok)
            if m:
                if pending_tie is not None or slur_notes is not None:
                    raise NotationError(tr("Una legatura (~ o parentesi) non puo' attraversare un blocco di voci: "
                                           "chiudila prima"), tok)
                voices = split_voices(m.group(1))
                if not any(v.strip() for v in voices):
                    raise NotationError(tr("Blocco di voci vuoto"), tok)
                longest = Fraction(0)
                checks = []
                # Le automazioni valgono per tutto lo strumento (un canale
                # MIDI): dopo il blocco resta l'ultimo valore scritto in una voce.
                control_ends: List[tuple] = []
                for k, voice_text in enumerate(voices):
                    voice_tokens = expand_repeats(tokenize(voice_text), lenient=lenient)[0]
                    voice_ranges: List[Tuple[Fraction, Fraction]] = []
                    # La prima voce continua il testo cantato della traccia:
                    # un testo dentro di essa prende anche le note prima del
                    # blocco, uno dopo il blocco anche le sue note.
                    sub_events, sub_end, _ = _parse_tokens_exact(
                        voice_tokens, default_octave, grid_beats, lenient, voice_ranges,
                        initial_velocity=velocity, voice=voice + k, extras=None,
                        pending_lyrics=lyric_targets if k == 0 else None,
                        initial_controls=controls, initial_swing=swing, initial_pitch=pitch,
                        initial_shift=shift, meter=meter, origin_beat=origin_beat + cursor)
                    for ev in sub_events:
                        ev.start += float(cursor)
                        if ev.kind == "control":
                            control_ends.append((ev.start + ev.duration, ev.name, ev.value))
                    events.extend(sub_events)
                    longest = max(longest, sub_end)
                    checks.append([a for t, (a, _) in zip(voice_tokens, voice_ranges) if t == BAR_CHECK])
                if extras is not None and any(checks):
                    extras.setdefault("voice_bars", {})[index] = (cursor, checks)
                for _end, name, value in sorted(control_ends, key=lambda c: c[0]):
                    controls[name] = value
                cursor += longest
                continue

            m = RE_GRID.match(tok)
            if m:
                n, tuplet = m.groups()
                n = int(n)
                if n <= 0:
                    raise NotationError(tr("Divisore di griglia non valido"), tok)
                beats = Fraction(4, n)
                if tuplet:
                    beats *= TUPLET_SCALE[tuplet]
                grid_beats = beats
                last_state_kind = "grid"
                continue

            m = RE_TEMPO_SET.match(tok)
            if m:
                new_tempo = int(m.group(1))
                if not 1 <= new_tempo <= 999:
                    raise NotationError(tr("Tempo fuori range (1-999 BPM)"), tok)
                if pending_ramp and pending_ramp["kind"] == "tempo":
                    _finalize_ramp(new_tempo)
                elif pending_ramp:
                    # kind == "velocity": senza questo controllo la rampa di
                    # velocity resterebbe "orfana" in silenzio (mai richiusa,
                    # nessun crescendo/diminuendo applicato, nessun errore) -
                    # meglio segnalarlo subito che lasciare un bug silenzioso.
                    raise NotationError(
                        tr("Rampa di velocity ('>>'/'<<' dopo N@ o una dinamica) aperta ma mai "
                        "richiusa da un altro N@/dinamica prima di questo cambio di tempo (tempo=N): "
                        "chiudila con un altro N@ prima, oppure sposta tempo=N dopo la chiusura"), tok
                    )
                else:
                    events.append(Event(start=float(cursor), duration=0.0, kind="tempo_marker", bpm=new_tempo))
                tempo = new_tempo
                last_state_kind = "tempo"
                continue

            m = RE_RAMP_UP.match(tok) or RE_RAMP_DOWN.match(tok)
            if m:
                curve = m.group(1) or "lin"
                if last_state_kind and last_state_kind.startswith("control:"):
                    name = last_state_kind.split(":", 1)[1]
                    pending_controls[name] = (cursor, controls.get(name, 0), curve)
                    continue
                if last_state_kind not in ("velocity", "tempo"):
                    raise NotationError(
                        tr("'>>' / '<<' deve seguire un comando di velocity (N@), di tempo (tempo=N) "
                           "o un'automazione (vol=, expr=, pan=, mod=, rev=, cho=)"), tok
                    )
                start_value = tempo if last_state_kind == "tempo" else velocity
                pending_ramp = {"kind": last_state_kind, "start_value": start_value, "start_index": len(events),
                                "curve": curve}
                continue

            m = RE_CONTROL.match(tok)
            if m:
                name, number = m.group(1), float(m.group(2))
                if name.startswith("cc") and int(name[2:]) > CC_MAX:
                    raise NotationError(tr("Controller MIDI non valido: 'ccN=' va da cc0 a cc{0}", CC_MAX), tok)
                low, high = CONTROL_RANGES.get(name, (0, 127))
                if not low <= number <= high:
                    raise NotationError(tr("Valore di '{name}' fuori dall'intervallo {low}..{high}",
                                           name=name, low=low, high=high), tok)
                value = number if name in CONTROL_DECIMAL else round(number)
                if name in pending_controls:
                    start, start_value, curve = pending_controls.pop(name)
                    if cursor > start:
                        _control(start, name, value, cursor - start, start_value, curve)
                    else:
                        _control(cursor, name, value)
                else:
                    _control(cursor, name, value)
                controls[name] = value
                last_state_kind = "control:" + name
                continue

            m = RE_SWING.match(tok)
            if m:
                percent = int(m.group(2))
                if not SWING_RANGE[0] <= percent <= SWING_RANGE[1]:
                    raise NotationError(tr("Swing fuori range ({0}-{1})", *SWING_RANGE), tok)
                swing = None if percent == 50 else (0.5 if m.group(1) else 1.0, percent / 100)
                continue

            m = RE_SHIFT.match(tok)
            if m:
                ms = int(m.group(1))
                if not SHIFT_RANGE[0] <= ms <= SHIFT_RANGE[1]:
                    raise NotationError(tr("Spostamento fuori range ({0}..{1} ms)", *SHIFT_RANGE), tok)
                shift = ms or None
                continue

            m = RE_BAR_ANCHOR.match(tok)
            if m:
                bar = int(m.group(1))
                if not 1 <= bar <= BAR_ANCHOR_MAX:
                    raise NotationError(tr("Battuta fuori range (1-{0})", BAR_ANCHOR_MAX), tok)
                target = (meter or default_meter()).start_of(bar) - origin_beat
                if target > cursor:
                    if pending_tie is not None:
                        raise NotationError(tr("La legatura di valore (~) deve arrivare a una nota uguale, "
                                               "non a un'ancora di battuta"), tok)
                    _add(Event(start=float(cursor), duration=float(target - cursor), kind="rest",
                               velocity=velocity))
                    cursor = target
                elif target < cursor and extras is not None:
                    extras.setdefault("anchor_issues", {})[index] = (bar, cursor - target)
                continue

            if tok in ("SON", "SOFF"):
                events.append(Event(start=float(cursor), duration=0.0, kind="sustain",
                                     name="on" if tok == "SON" else "off"))
                continue

            m = RE_VELOCITY.match(tok)
            if m:
                raw = m.group(1)
                v = DYNAMICS_TO_VELOCITY[raw] if raw in DYNAMICS_TO_VELOCITY else int(raw)
                if not (1 <= v <= 127):
                    raise NotationError(tr("Velocity fuori range (1-127)"), tok)
                if pending_ramp and pending_ramp["kind"] == "velocity":
                    _finalize_ramp(v)
                elif pending_ramp:
                    # kind == "tempo": stesso problema del ramo tempo=N sopra, speculare.
                    raise NotationError(
                        tr("Rampa di tempo ('>>'/'<<' dopo tempo=N) aperta ma mai richiusa da un altro "
                        "tempo=N prima di questo comando di velocity (N@/dinamica): chiudila con un "
                        "altro tempo=N prima, oppure sposta il comando di velocity dopo la chiusura"), tok
                    )
                velocity = v
                last_state_kind = "velocity"
                continue

            # Da qui solo token che occupano tempo: col valore di nota
            # esplicito (c'8.) durano quello invece dell'unita' di griglia.
            tok, value = split_note_value(tok)
            value, hairpin, tie, slur, decorations = split_marks(value)
            for deco in decorations:
                if deco not in DECORATIONS:
                    raise NotationError(tr("Segno sconosciuto: '${deco}'. Ammessi: {0}",
                                           ", ".join("$" + d for d in DECORATIONS), deco=deco), tokens[index])
            unit = note_value_beats(value) if value else grid_beats
            note_start = cursor

            m = RE_REST.match(tok)
            if m:
                if hairpin:
                    raise NotationError(tr("Una pausa non puo' avere una forcella ('<' o '>')"), tokens[index])
                if tie or slur:
                    raise NotationError(tr("Una pausa non puo' avere una legatura"), tokens[index])
                if any(d != "fermata" for d in decorations):
                    raise NotationError(tr("Su una pausa va solo la corona ($fermata)"), tokens[index])
                if pending_tie is not None:
                    raise NotationError(tr("La legatura di valore (~) deve arrivare a una nota uguale, "
                                           "non a una pausa"), tokens[index])
                mult = int(m.group(1)) if m.group(1) else 1
                dur = unit * mult
                _add(Event(start=float(cursor), duration=float(dur), kind="rest", velocity=velocity,
                           decorations=decorations or None))
                cursor += dur
                continue

            m = RE_SLIDE.match(tok)
            if m:
                points = _parse_slide_points(m.group(1), default_octave, pitch)
                segment_durations = _slide_segment_durations(points, unit)
                dur = sum(segment_durations)
                if dur <= 0:
                    raise NotationError(tr("Slide di durata nulla"), tok)
                _, first_letter, first_octave = points[0]
                if tie or pending_tie is not None:
                    raise NotationError(tr("Uno slide non puo' avere una legatura di valore (~)"), tokens[index])
                _sounding(Event(
                    start=float(cursor), duration=float(dur), kind="slide", velocity=velocity,
                    letter=first_letter, octave=first_octave,
                    slide_points=[(letter, octave) for _, letter, octave in points[1:]],
                    slide_segment_durations=[float(d) for d in segment_durations],
                ), dur, hairpin, tie, slur, note_start, tokens[index], decorations)
                cursor += dur
                continue

            if tok.startswith("[") or re.match(r"^\d+\[", tok):
                mm = re.match(r"^(\d*)\[(.*)\]$", tok)
                if not mm:
                    raise NotationError(tr("Blocco simultaneo malformato"), tok)
                mult_s, inner = mm.groups()
                mult = int(mult_s) if mult_s else 1
                sub_toks = inner.split()
                if not sub_toks:
                    raise NotationError(tr("Blocco simultaneo vuoto"), tok)
                items = [_parse_atom(st, default_octave, pitch) for st in sub_toks]
                first_note = next((it for it in items if it["kind"] == "note"), None)
                if first_note is not None:       # rel: dopo il blocco si riparte dalla sua prima nota
                    pitch.ref = (first_note["letter"][0], first_note["octave"])
                dur = unit * mult
                _sounding(Event(start=float(cursor), duration=float(dur), kind="block",
                                velocity=velocity, items=items), dur, hairpin, tie, slur, note_start, tokens[index],
                          decorations)
                cursor += dur
                continue

            # nota / accordo / percussione singoli
            atom = _parse_atom(tok, default_octave, pitch)
            dur = unit * atom["mult"]
            start, duration = float(cursor), float(dur)
            if atom["kind"] == "note":
                ev = Event(start=start, duration=duration, kind="note", velocity=velocity,
                           letter=atom["letter"], octave=atom["octave"],
                           articulation=atom.get("articulation"))
            elif atom["kind"] == "chord":
                ev = Event(start=start, duration=duration, kind="chord", velocity=velocity,
                           symbol=atom["symbol"], octave=atom["octave"], voicing=atom.get("voicing"),
                           articulation=atom.get("articulation"), bass=atom.get("bass"))
            else:  # percussion
                if tie or pending_tie is not None:
                    raise NotationError(tr("Una percussione non puo' avere una legatura di valore (~)"),
                                        tokens[index])
                ev = Event(start=start, duration=duration, kind="percussion", velocity=velocity,
                           name=atom["name"])
            _sounding(ev, dur, hairpin, tie, slur, note_start, tokens[index], decorations)
            cursor += dur
        except (NotationError, ValueError):
            if not lenient:
                raise
            # modalita' tollerante (vedi compute_token_spans): il token
            # non valido non occupa tempo e lo stato resta com'era.
        finally:
            if ranges is not None:
                ranges.append((before, cursor))

    if pending_tie is not None and not lenient:
        raise NotationError(tr("Legatura di valore (~) senza la nota che la continua"))
    if slur_notes is not None and not lenient:
        raise NotationError(tr("Legatura di portamento aperta ma mai chiusa con ')'"))
    if pending_controls and not lenient:
        raise NotationError(tr("Rampa di '{name}' aperta ma mai chiusa da un valore finale ({name}=N)",
                               name=next(iter(pending_controls))))
    if pending_ramp and not lenient:
        anchor = "tempo=N" if pending_ramp["kind"] == "tempo" else "N@"
        raise NotationError(tr("Rampa '>>' o '<<' aperta ma mai chiusa da un valore finale ({anchor})", anchor=anchor))

    return events, cursor, grid_beats


def parse_track_text(text: str, patterns: Dict[str, Pattern], default_octave: int = 4,
                      midi_dir: Optional[str] = None, meter: Optional["Meter"] = None) -> List[Event]:
    """Punto di ingresso completo: tokenizza, espande pattern (%) e riferimenti
    MIDI (&), quindi interpreta lo Stato Corrente. 'meter' (vedi Meter) serve
    alle ancore di battuta 'bar=N'."""
    raw_tokens = tokenize(text)
    expanded = expand_patterns(raw_tokens, patterns, midi_dir=midi_dir, default_octave=default_octave)
    return parse_tokens(expanded, default_octave=default_octave, meter=meter)


def validate_track_text(text: str, patterns: Dict[str, Pattern], default_octave: int = 4,
                         midi_dir: Optional[str] = None, meter: Optional["Meter"] = None):
    """Usata dall'editor per la validazione sintattica live. Ritorna (ok, messaggio_errore)."""
    try:
        parse_track_text(text, patterns, default_octave=default_octave, midi_dir=midi_dir, meter=meter)
        return True, ""
    except (NotationError, ValueError) as e:
        return False, str(e)


def _expanded_ranges(text: str, patterns: Dict[str, Pattern], midi_dir: Optional[str],
                     default_octave: int, extras: Optional[dict] = None,
                     meter: Optional["Meter"] = None, origin_beat: Fraction = Fraction(0)):
    """Espande separatamente ogni token di primo livello e interpreta il
    risultato in modalita' tollerante. Ritorna (token grezzi con posizione,
    token espansi, indice del token grezzo da cui viene ciascun espanso,
    intervallo in beat di ciascun espanso)."""
    raw = tokenize_spans(text)
    expanded: List[str] = []
    origins: List[int] = []
    for i, (tok, _, _) in enumerate(raw):
        try:
            body = expand_patterns([tok], patterns, midi_dir=midi_dir, default_octave=default_octave)
        except (NotationError, ValueError):
            body = []
        expanded.extend(body)
        origins.extend([i] * len(body))
    expanded, origins = expand_repeats(expanded, origins, lenient=True)
    ranges: List[Tuple[Fraction, Fraction]] = []
    _parse_tokens_exact(expanded, default_octave=default_octave, lenient=True, ranges=ranges,
                        extras=extras, meter=meter, origin_beat=origin_beat)
    return raw, expanded, origins, ranges


def compute_token_spans(text: str, patterns: Dict[str, Pattern], midi_dir: Optional[str] = None,
                          default_octave: int = 4, meter: Optional["Meter"] = None) -> List[tuple]:
    """Calcola, per ogni token di 'primo livello' del testo GREZZO (prima
    dell'espansione di %pattern/&midi), la sua posizione carattere e il suo
    intervallo temporale in beat. Un riferimento %Nome o &Nome, o un gruppo
    N(...), viene trattato come un unico span che copre tutto il suo
    contenuto espanso (non si entra dentro): e' quanto serve per evidenziare
    nell'editor il token in esecuzione durante la riproduzione.

    I tempi vengono dal parser stesso (_parse_tokens_exact, con 'ranges'),
    sul testo espanso come per la riproduzione: nessuna logica di durata
    duplicata qui, quindi griglia ereditata dai pattern, tuplet, slide e
    ogni sintassi futura restano per costruzione allineati a cio' che si
    sente. Un token non valido (o un riferimento irrisolvibile) non produce
    uno span e non blocca gli altri.

    Ritorna una lista di tuple (char_start, char_end, beat_start, beat_duration),
    ordinata per beat_start crescente. I comandi di stato (N:, NT:, N@, tempo=N,
    rampe, SON/SOFF) non producono uno span (non hanno una durata propria)."""
    raw, expanded, origins, ranges = _expanded_ranges(text, patterns, midi_dir, default_octave,
                                                      meter=meter)
    raw_positions = [(cs, ce) for _, cs, ce in raw]

    # Uno span per ogni tratto consecutivo dello stesso token grezzo: un
    # gruppo o un pattern e' un tratto solo, un token ripetuto da un
    # ritornello ne ha uno per passaggio.
    runs: List[list] = []
    previous = None
    for origin, (start, end) in zip(origins, ranges):
        if origin != previous:
            runs.append([origin, None, None])
            previous = origin
        if end <= start:
            continue  # comando di stato o token non valido: nessuna durata
        run = runs[-1]
        run[1] = start if run[1] is None else min(run[1], start)
        run[2] = end if run[2] is None else max(run[2], end)

    spans = []
    for origin, start, end in runs:
        if start is None:
            continue
        cs, ce = raw_positions[origin]
        spans.append((cs, ce, float(start), float(end - start)))
    return sorted(spans, key=lambda span: (span[2], span[0]))


def find_span_at_beat(spans: List[tuple], beat: float) -> Optional[tuple]:
    """Ritorna lo span (char_start, char_end, beat_start, beat_duration) che
    contiene 'beat', oppure None se nessuno lo contiene (es. durante una
    pausa gestita da un token successivo, o dopo la fine della traccia)."""
    for span in spans:
        _, _, beat_start, beat_duration = span
        if beat_duration <= 0:
            continue
        if beat_start <= beat < beat_start + beat_duration:
            return span
    return None


def all_token_spans(text: str) -> List[Tuple[int, int]]:
    """Posizione carattere di OGNI token di primo livello, inclusi i comandi
    di stato N:/N@ (che compute_token_spans esclude perche' privi di durata
    propria): serve per agganciare un punto del testo a un confine di token
    intero (es. una selezione dell'utente, vedi gui.selection_actions) o per
    ricostruire lo stato attivo in un dato punto (vedi
    context_prefix_before)."""
    return [(start, end) for _, start, end in tokenize_spans(text)]


def context_prefix_before(text: str, char_start: int) -> str:
    """Ricostruisce l'ultimo comando di griglia e di velocity attivi prima
    di char_start, cosi' un frammento di testo estratto da quel punto (per
    esempio l'anteprima 'Play' di una selezione, vedi
    gui.selection_actions._play_selection, o un box ottenuto dividendo una
    traccia, vedi core.arrangement.split_text_into_box_segments) suona/si
    interpreta con lo stesso Stato Corrente che avrebbe nel punto originale,
    invece di ripartire sempre da 1/4 e velocity di default."""
    last_grid = last_vel = None
    for cs, ce in all_token_spans(text):
        if cs >= char_start:
            break
        tok = text[cs:ce]
        if RE_GRID.match(tok):
            last_grid = tok
        elif RE_VELOCITY.match(tok):
            last_vel = tok
    parts = [t for t in (last_grid, last_vel) if t]
    return (" ".join(parts) + " ") if parts else ""


# ---------------------------------------------------------------------------
# Controlli di battuta: '|' dichiara "qui finisce una battuta"
# ---------------------------------------------------------------------------

# Figure con cui si esprime quanto manca o avanza in una battuta, dalla piu'
# lunga alla piu' corta: si usa la piu' lunga che divide esattamente la
# quantita' ("3 crome", non "1 semiminima e mezza").
_NOTE_VALUES = [
    (Fraction(4), "semibreve", "semibrevi"),
    (Fraction(2), "minima", "minime"),
    (Fraction(1), "semiminima", "semiminime"),
    (Fraction(2, 3), "semiminima di terzina", "semiminime di terzina"),
    (Fraction(1, 2), "croma", "crome"),
    (Fraction(1, 3), "croma di terzina", "crome di terzina"),
    (Fraction(1, 4), "semicroma", "semicrome"),
    (Fraction(1, 6), "semicroma di terzina", "semicrome di terzina"),
    (Fraction(1, 8), "biscroma", "biscrome"),
    (Fraction(1, 16), "semibiscroma", "semibiscrome"),
]


def describe_duration(beats: Fraction) -> Tuple[int, str]:
    """(quante, 'figura') per una durata in quarti: (3, '3 crome').
    Il numero serve a chi deve accordare il verbo (manca/mancano)."""
    for unit, singular, plural in _NOTE_VALUES:
        count = beats / unit
        if count.denominator == 1:
            n = int(count)
            return n, f"{n} {tr(singular) if n == 1 else tr(plural)}"
    value = f"{float(beats):.3f}".rstrip("0").rstrip(".")
    return 2, tr("{value} quarti", value=value)


def bar_starts(time_sig: str = "4/4", metrica_changes=()):
    """Generatore infinito dell'inizio (in quarti, Fraction) di ogni
    battuta: 0, poi via via sommando la durata della battuta secondo la
    metrica in vigore. Stessa regola di project_io.compute_bar_beat_offsets
    (con dei cambi di metrica che non partono dalla battuta 1, prima vale
    il 4/4)."""
    metrica_map = dict(metrica_changes)
    sig = metrica_map.get(1, "4/4" if metrica_changes else (time_sig or "4/4"))
    start = Fraction(0)
    bar = 1
    while True:
        yield start
        if bar in metrica_map:
            sig = metrica_map[bar]
        try:
            num, den = (int(x) for x in sig.split("/"))
            length = Fraction(num * 4, den)
        except (ValueError, ZeroDivisionError):
            length = Fraction(4)
        start += length if length > 0 else Fraction(4)
        bar += 1


class Meter:
    """Dove cominciano le battute del brano (in quarti): serve alle ancore
    'bar=N'. Si costruisce con la metrica del brano e gli eventuali suoi
    cambi (vedi bar_starts); senza, vale il 4/4."""

    def __init__(self, time_sig: str = "4/4", metrica_changes=()):
        self._gen = bar_starts(time_sig, metrica_changes)
        self._starts: List[Fraction] = []

    def start_of(self, bar: int) -> Fraction:
        """L'inizio della battuta 'bar' (la prima e' la 1, a 0)."""
        while len(self._starts) < bar:
            self._starts.append(next(self._gen))
        return self._starts[bar - 1]


_DEFAULT_METER: Optional[Meter] = None


def default_meter() -> Meter:
    global _DEFAULT_METER
    if _DEFAULT_METER is None:
        _DEFAULT_METER = Meter()
    return _DEFAULT_METER


@dataclass
class BarIssue:
    char_start: int     # posizione della '|' nel testo
    char_end: int
    bar: int            # battuta che non torna
    message: str


class _BarGrid:
    """Le stanghette del brano, calcolate man mano che servono."""

    def __init__(self, time_sig: str, metrica_changes):
        self._gen = bar_starts(time_sig, metrica_changes)
        self._starts = [next(self._gen), next(self._gen)]

    def nearest(self, position: Fraction) -> Tuple[int, Fraction]:
        """(k, inizio della battuta k) per la stanghetta piu' vicina a
        'position', mai la 1 (l'inizio del brano non chiude nessuna
        battuta); a pari distanza vince quella prima."""
        while self._starts[-1] <= position:
            self._starts.append(next(self._gen))
        k = len(self._starts) - 1          # prima stanghetta oltre position (indice 0 = battuta 1)
        before, after = self._starts[k - 1], self._starts[k]
        if k - 1 >= 1 and position - before <= after - position:
            return k, before                # battuta k (1-based) inizia in 'before'
        return k + 1, after


def bar_check_message(bar: int, delta: Fraction) -> str:
    """Messaggio per la battuta 'bar' che ha 'delta' quarti in piu'
    (positivo) o in meno (negativo) del dovuto."""
    count, amount = describe_duration(abs(delta))
    if delta > 0:
        return tr("battuta {bar}: {amount} di troppo", bar=bar, amount=amount)
    if count == 1:
        return tr("battuta {bar}: manca {amount}", bar=bar, amount=amount)
    return tr("battuta {bar}: mancano {amount}", bar=bar, amount=amount)


def anchor_message(bar: int, over: Fraction) -> str:
    """Avviso per 'bar=N' quando la traccia e' gia' oltre l'inizio della
    battuta N di 'over' quarti."""
    _, amount = describe_duration(over)
    return tr("battuta {bar}: la traccia e' gia' {amount} oltre l'inizio", bar=bar, amount=amount)


def check_bar_lines(text: str, patterns: Dict[str, Pattern], time_sig: str = "4/4",
                    metrica_changes=(), start_beat: float = 0.0, default_octave: int = 4,
                    midi_dir: Optional[str] = None) -> List[BarIssue]:
    """I controlli di battuta '|' del testo che non cadono su una
    stanghetta, secondo la metrica del progetto (e i suoi cambi).
    'start_beat' e' dove il testo comincia nel brano (l'inizio del box).
    Non e' un errore di sintassi: il brano suona lo stesso, l'editor lo
    segnala come avviso.

    Ogni '|' viene attribuita alla stanghetta piu' vicina. Una nota
    mancante sposta tutto quel che segue: le '|' successive non vengono
    segnalate di nuovo per lo stesso sfasamento (si misurano tenendone
    conto), solo dove ci sono altri errori, con quanto manca o avanza in
    quella battuta. Una '|' dentro un pattern o un gruppo N(...) viene
    controllata a ogni ripetizione e segnalata sul riferimento; dentro un
    blocco di voci { ; } ogni voce si controlla per conto suo."""
    return [w for w in notation_warnings(text, patterns, time_sig, metrica_changes, start_beat,
                                         default_octave, midi_dir) if w.bar]


def notation_warnings(text: str, patterns: Dict[str, Pattern], time_sig: str = "4/4",
                      metrica_changes=(), start_beat: float = 0.0, default_octave: int = 4,
                      midi_dir: Optional[str] = None) -> List[BarIssue]:
    """Gli avvisi che non impediscono di suonare il testo, in ordine di
    posizione: controlli di battuta '|' che non tornano (vedi
    check_bar_lines, bar > 0) e testi cantati con piu' sillabe che note
    (bar == 0)."""
    extras: dict = {}
    offset = Fraction(start_beat).limit_denominator(1 << 16)
    try:
        raw, expanded, origins, ranges = _expanded_ranges(text, patterns, midi_dir, default_octave, extras,
                                                          Meter(time_sig, metrica_changes), offset)
    except NotationError:
        return []
    grid = _BarGrid(time_sig, metrica_changes)
    issues: List[BarIssue] = []
    reported = set()

    def check(position: Fraction, shift: Fraction, origin: int) -> Fraction:
        """Controlla una '|' (sfasamento gia' accumulato: shift); ritorna
        lo sfasamento aggiornato."""
        # Dove cadrebbe senza gli errori gia' segnalati prima.
        expected = offset + position - shift
        if expected == 0:
            return shift            # una '|' all'inizio del brano (o un '|:') e' sempre giusta
        k, line = grid.nearest(expected)
        delta = expected - line
        if delta and origin not in reported:
            reported.add(origin)    # un solo avviso per token, anche se ripetuto
            _, cs, ce = raw[origin]
            issues.append(BarIssue(cs, ce, k - 1, bar_check_message(k - 1, delta)))
        return shift + delta

    shift = Fraction(0)          # sfasamento rispetto alle stanghette vere
    voice_bars = extras.get("voice_bars", {})
    for index, (tok, origin, (pos, _)) in enumerate(zip(expanded, origins, ranges)):
        if tok == BAR_CHECK:
            shift = check(pos, shift, origin)
        elif index in voice_bars:
            block_start, voices = voice_bars[index]
            for positions in voices:
                voice_shift = shift
                for p in positions:
                    voice_shift = check(block_start + p, voice_shift, origin)
    for index, message in extras.get("lyric_issues", {}).items():
        _, cs, ce = raw[origins[index]]
        issues.append(BarIssue(cs, ce, 0, message))
    for index, (bar, over) in extras.get("anchor_issues", {}).items():
        _, cs, ce = raw[origins[index]]
        issues.append(BarIssue(cs, ce, bar, anchor_message(bar, over)))
    issues.sort(key=lambda i: i.char_start)
    return issues


def bar_issues_summary(issues: List[BarIssue]) -> str:
    """Una riga per la barra di stato dell'editor: il primo avviso e
    quanti altri ce ne sono (l'elenco completo va nel suggerimento)."""
    if len(issues) == 1:
        return tr("⚠  Avviso: {msg}", msg=issues[0].message)
    return tr("⚠  Avviso: {msg} (e altri {n})", msg=issues[0].message, n=len(issues) - 1)
