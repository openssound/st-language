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
        while k < n and not text[k].isspace() and text[k] not in _PLAIN_STOP:
            k += 1
        return k

    def _with_value(k: int) -> int:
        """Fine di un blocco [...] col suo eventuale valore di nota
        attaccato ('[c e g]'2) o della forcella ('[c e g]<')."""
        if k < n and text[k] == "'":
            return _plain_end(k)
        if k < n and text[k] in "<>" and (k + 1 >= n or text[k + 1] not in "<>"):
            return k + 1
        return k

    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch == BAR_CHECK:
            tokens.append((ch, i, i + 1))
            i += 1
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
RE_PATTERN_REF = re.compile(r"^(\d*)%(\w+)$")
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
# Velocity: numero esplicito oppure dinamica classica (ppp/pp/p/mp/mf/f/ff/fff)
DYNAMICS_TO_VELOCITY = {
    "ppp": 20, "pp": 40, "p": 60, "mp": 75, "mf": 90, "f": 105, "ff": 120, "fff": 127,
}
RE_VELOCITY = re.compile(r"^(ppp|pp|p|mp|mf|fff|ff|f|\d+)@$")
RE_REST = re.compile(r"^(\d*)r$")
# Nota melodica, con modificatore opzionale finale: '!' staccato, 'x' mute, '_' legato.
# Alterazione: '#' diesis; 'b', '♭' o '-' bemolle (equivalenti, vedi core.chords.
# note_name_to_pc). '-' e' una scorciatoia di digitazione: l'editor la sostituisce
# automaticamente con '♭' quando viene battuta subito dopo una lettera nota, per
# evitare l'ambiguita' visiva tra la 'b' di alterazione e la lettera nota 'b' (Si).
# Ottava: '*n' (sintassi preferita) oppure, per compatibilita' con i progetti
# gia' scritti, '/n' (equivalente, mai deprecato: nessun motivo di rompere
# file esistenti solo per uniformare la sintassi).
RE_NOTE = re.compile(r"^(\d*)([a-g])([#b♭-]?)(?:[/*](\d+))?([!x_])?$")
# Suffisso opzionale '.stile' (es. Cmaj7.drop2) per forzare il voicing:
# vedi core.chords.ALL_VOICINGS per l'elenco degli stili validi. La classe
# di caratteri della qualita' include '#' per accordi come '7#9' e '°' per
# l'alias di 'dim'/'dim7' ('C°', 'C°7').
# Dopo l'eventuale '.stile' un unico gruppo opzionale introdotto da '/' e'
# o il basso alternativo (lettera nota maiuscola, es. 'C/E' = Do col basso
# Mi) o, per compatibilita' con la vecchia sintassi, l'ottava in cifre
# (es. 'C7/3'): i due usi non sono ambigui per il parser, si distinguono
# dal tipo di carattere che segue '/' (lettera vs cifra) - vedi
# split_chord_slash(). L'ottava nella sintassi preferita si scrive invece
# con '*n', indipendentemente dal basso alternativo (es. 'C/E*4').
# Modificatore opzionale finale (dopo l'eventuale ottava): '!' staccato,
# 'x' mute, '_' legato, stesso schema delle note (vedi Event.articulation).
# La qualita' e' la piu' corta che fa tornare il resto del token: cosi'
# una 'x' finale e' il modificatore (Cmaj7x = Cmaj7 stoppato), non parte
# della qualita' (nessuna qualita' finisce con 'x').
RE_CHORD = re.compile(
    r"^(\d*)([A-G])([#b♭-]?)([A-Za-z0-9#°]*?)(?:\.([A-Za-z0-9]+))?"
    r"(?:/([A-G][#b♭-]?|\d+))?(?:\*(\d+))?([!x_])?$"
)
RE_PERC = re.compile(r"^(\d*)([a-z][a-z_0-9]*)$")
# Portamento/slide tra due o piu' note: c/4>d/4 (o c*4>d*4, vedi RE_NOTE),
# oppure una catena c*4>d*4>c*4 (bend-and-release: sale e poi rilascia,
# tutto entro la stessa unita' di griglia). Ogni tappa puo' avere un proprio
# moltiplicatore di durata (es. 2c*4>3d*4, vedi _slide_segment_durations
# per la semantica): il gruppo catturato e' l'intera catena grezza, da
# ripassare a RE_SLIDE_POINT tappa per tappa dopo lo split su '>'.
_SLIDE_POINT_PATTERN = r"\d*[a-g][#b♭-]?(?:[/*]\d+)?"
RE_SLIDE = re.compile(rf"^({_SLIDE_POINT_PATTERN}(?:>{_SLIDE_POINT_PATTERN})+)$")
RE_SLIDE_POINT = re.compile(r"^(\d*)([a-g])([#b♭-]?)(?:[/*](\d+))?$")


def _check_pitch_range(letter: str, octave: int, tok: str) -> None:
    """Solleva NotationError se la nota esce dal range MIDI 0-127 (es.
    'a*9'): altrimenti la validazione la accetterebbe e l'export MIDI
    fallirebbe dopo, con un errore incomprensibile per l'utente."""
    from .chords import pitch_to_midi  # import locale: evita dipendenza circolare
    if not 0 <= pitch_to_midi(letter, octave) <= 127:
        raise NotationError(tr("Nota fuori dall'estensione MIDI (la piu' acuta e' g*9)"), tok)


def _parse_slide_points(chain: str, default_octave: int) -> List[Tuple[Optional[int], str, int]]:
    """Scompone la catena grezza catturata da RE_SLIDE (gia' validata nella
    sua interezza dal match esterno) in [(moltiplicatore_esplicito_o_None,
    lettera[+alterazione], ottava), ...], una tappa per ogni punto del
    bending, nell'ordine in cui compaiono. Il moltiplicatore e' None se
    quella tappa non ne aveva uno scritto esplicitamente (per distinguere
    la modalita' legacy da quella con durate per tappa, vedi
    _slide_segment_durations)."""
    points = []
    for point_str in chain.split(">"):
        pm = RE_SLIDE_POINT.match(point_str)
        mult_s, letter, acc, octv = pm.groups()
        mult = int(mult_s) if mult_s else None
        octave = int(octv) if octv else default_octave
        _check_pitch_range(letter + acc, octave, chain)
        points.append((mult, letter + acc, octave))
    return points


def _slide_segment_durations(points: List[Tuple[Optional[int], str, int]],
                              grid_beats: Fraction) -> List[Fraction]:
    """Ritorna la durata (in beat) di ciascun segmento di uno slide a
    catena: per le tappe 1..N-1 e' la durata della rampa che PARTE da quella
    tappa verso la successiva; per l'ultima e' quanto la nota resta ferma
    sull'altezza d'arrivo dopo la rampa finale (un'attesa, non avendo una
    tappa successiva verso cui rampare) - lista di N valori totali (N-1
    rampe + 1 attesa), la cui somma e' la durata complessiva dell'evento.

    Se nessuna tappa OLTRE la prima ha un proprio moltiplicatore esplicito
    (caso comune: 'c*4>d*4' o '5c*4>d*4>c*4'), si resta in modalita' LEGACY
    per compatibilita' con tutti i progetti gia' scritti: un solo
    moltiplicatore prima dell'intera catena (sulla prima tappa, o 1 se
    omesso) fissa la durata TOTALE, suddivisa in parti uguali tra le sole
    rampe (nessuna attesa finale) - esattamente il comportamento del
    progetto prima di poter dare una durata propria a ogni tappa. Basta un
    moltiplicatore esplicito su una qualunque tappa successiva alla prima
    per attivare invece la modalita' per-tappa (una tappa senza il proprio
    moltiplicatore vale implicitamente 1, come una nota bare)."""
    explicit_beyond_first = any(mult is not None for mult, _, _ in points[1:])
    num_ramps = len(points) - 1
    if not explicit_beyond_first:
        total_mult = points[0][0] if points[0][0] is not None else 1
        seg_duration = (total_mult * grid_beats) / num_ramps
        return [seg_duration] * num_ramps + [Fraction(0)]
    return [(mult if mult is not None else 1) * grid_beats for mult, _, _ in points]


def split_chord_slash(slash_val: Optional[str]):
    """Scompone il gruppo unificato dopo '/' di RE_CHORD in (basso,
    ottava_legacy): una lettera nota (es. 'E') e' basso alternativo, una
    stringa di sole cifre (es. '3') e' l'ottava nella vecchia sintassi.
    Ritorna (None, None) se il gruppo non era presente nel token."""
    if slash_val is None:
        return None, None
    if slash_val[0].isdigit():
        return None, slash_val
    return slash_val, None


def split_note_value(tok: str) -> Tuple[str, str]:
    """(token senza valore di nota, valore come scritto: "'8." o "").
    c*4'8. -> ('c*4', "'8."); c'8! -> ('c!', "'8"); c'2< -> ('c', "'2<");
    2c< -> ('2c', "<")."""
    if tok.startswith(LYRIC_QUOTE):
        return tok, ""
    # Forcella in fondo (c'2<, 2c*4>): fa parte del "valore" restituito,
    # cosi' chi ricompone il token (trasposizione, congelamento) la conserva.
    hairpin = ""
    if len(tok) > 1 and tok[-1] in "<>" and tok[-2] not in "<>":
        tok, hairpin = tok[:-1], tok[-1]
    m = RE_NOTE_VALUE.match(tok)
    if not m:
        return tok, hairpin
    base, number, tuplet, dots, articulation = m.groups()
    return base + articulation, f"'{number}{tuplet}{dots}{hairpin}"


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


# Tempo istantaneo inline in una traccia: 120§
RE_TEMPO_SET = re.compile(r"^(\d+)§$")
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
RE_CONTROL = re.compile(r"^(vol|expr|pan|mod|rev|cho)=(-?\d+(?:\.\d+)?)$")
CONTROL_RANGES = {"vol": (0, 127), "expr": (0, 127), "pan": (-1, 1), "mod": (0, 127),
                  "rev": (0, 127), "cho": (0, 127)}
CONTROL_DEFAULTS = {"vol": 100, "expr": 127, "pan": 0, "mod": 0, "rev": 0, "cho": 0}


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

def transpose_tokens(tokens: List[str], semitones: int, default_octave: int) -> List[str]:
    if semitones == 0:
        return tokens
    from .chords import transpose_pitch, transpose_chord_root

    def transpose_one(tok: str) -> str:
        m = RE_NOTE.match(tok)
        if m:
            mult, letter, accidental, octv, modifier = m.groups()
            octave = int(octv) if octv else default_octave
            new_letter, new_octave = transpose_pitch(letter + accidental, octave, semitones)
            return f"{mult or ''}{new_letter}*{new_octave}{modifier or ''}"
        m = RE_CHORD.match(tok)
        if m:
            mult, letter, accidental, suffix, voicing, slash_val, star_octv, modifier = m.groups()
            bass, legacy_octv = split_chord_slash(slash_val)
            octv = star_octv or legacy_octv
            symbol = letter + accidental + suffix
            try:
                new_symbol = transpose_chord_root(symbol, semitones)
            except ValueError:
                return tok
            voicing_part = f".{voicing}" if voicing else ""
            bass_part = ""
            if bass:
                new_bass_letter, _ = transpose_pitch(bass, 4, semitones)
                bass_part = f"/{new_bass_letter.upper()}"
            octv_part = f"*{octv}" if octv else ""
            return f"{mult or ''}{new_symbol}{voicing_part}{bass_part}{octv_part}{modifier or ''}"
        return tok  # percussioni, pause, comandi di stato: invariati

    def transpose_token(tok: str) -> str:
        base, value = split_note_value(tok)
        mm = re.match(r"^(\d*)\[(.*)\]$", base)
        if mm:
            mult_s, inner = mm.groups()
            sub = [transpose_one(st) for st in inner.split()]
            return f"{mult_s}[{' '.join(sub)}]{value}"
        return transpose_one(base) + value if value else transpose_one(tok)

    return [map_nested_tokens(tok, transpose_token) for tok in tokens]


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
            mult_s, name = m.groups()
            mult = int(mult_s) if mult_s else 1
            if name not in patterns:
                raise NotationError(tr("Pattern '%{name}' non definito", name=name), t)
            body = expand_patterns(patterns[name].tokens, patterns, midi_dir, default_octave, _depth + 1)
            out.extend(body * mult)
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
            out.extend(body * mult)
            continue

        out.append(t)
    return out


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


def _parse_atom(tok: str, default_octave: int):
    """Ritorna un dict {kind, letter/symbol/name, octave, mult} per nota/accordo/percussione."""
    m = RE_NOTE.match(tok)
    if m:
        mult, letter, accidental, octv, modifier = m.groups()
        articulation = {"!": "staccato", "x": "mute", "_": "legato"}.get(modifier)
        octave = int(octv) if octv else default_octave
        _check_pitch_range(letter + accidental, octave, tok)
        return {
            "kind": "note", "letter": letter + accidental,
            "octave": octave,
            "mult": int(mult) if mult else 1,
            "articulation": articulation,
        }
    m = RE_CHORD.match(tok)
    if m:
        mult, letter, accidental, suffix, voicing, slash_val, star_octv, modifier = m.groups()
        voicing, modifier = _split_voicing_modifier(voicing, modifier)
        bass, legacy_octv = split_chord_slash(slash_val)
        octv = star_octv or legacy_octv
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
        return {
            "kind": "chord", "symbol": symbol, "voicing": voicing, "bass": bass,
            "octave": int(octv) if octv else default_octave,
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


def parse_tokens(tokens: List[str], default_octave: int = 4) -> List[Event]:
    return _parse_tokens_exact(tokens, default_octave)[0]


def _parse_tokens_exact(tokens: List[str], default_octave: int = 4,
                         initial_grid: Fraction = Fraction(1), lenient: bool = False,
                         ranges: Optional[List[Tuple[Fraction, Fraction]]] = None,
                         initial_velocity: int = 80, voice: int = 1,
                         extras: Optional[dict] = None,
                         pending_lyrics: Optional[List["Event"]] = None,
                         initial_controls: Optional[Dict[str, float]] = None
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
    notation_warnings."""
    grid_beats = initial_grid  # unita' di durata corrente, in beat (quarti). Default: 1/4 (nera)
    velocity = initial_velocity  # velocity corrente
    tempo = None             # tempo corrente inline (solo se la traccia usa N§)
    cursor = Fraction(0)     # posizione nella timeline, in beat
    events: List[Event] = []

    # Stato per le rampe (Crescendo/diminuendo di velocity, accelerando/
    # rallentando di tempo) introdotte da >> o << subito dopo un comando N@
    # (o dinamica) / N§, e chiuse dal successivo comando dello stesso tipo.
    last_state_kind = None   # 'grid' | 'velocity' | 'tempo' (ultimo comando di stato incontrato)
    pending_ramp = None      # {'kind': 'velocity'|'tempo', 'start_value': float, 'start_index': int}
    # Note che aspettano la sillaba del prossimo testo cantato "...": la
    # lista e' quella del chiamante per la prima voce di un blocco { ; }
    # (le note prima del blocco aspettano lo stesso testo).
    lyric_targets: List[Event] = pending_lyrics if pending_lyrics is not None else []
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
        affected = [ev for ev in events[start_index:] if ev.kind != "control"]
        n = len(affected)
        if n == 0 and pending_ramp["kind"] == "tempo":
            # Nessun evento dentro la rampa ('120§ >> 140§ c'): non c'e'
            # niente su cui distribuirla, ma il valore di arrivo va comunque
            # applicato da qui in poi, come un N§ senza rampa.
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

    for index, tok in enumerate(tokens):
        before = cursor
        try:
            if tok == BAR_CHECK:
                # Controllo di battuta: non suona e non sposta il cursore;
                # se cade davvero su una stanghetta lo verifica
                # check_bar_lines (avviso, non errore).
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
                voices = split_voices(m.group(1))
                if not any(v.strip() for v in voices):
                    raise NotationError(tr("Blocco di voci vuoto"), tok)
                longest = Fraction(0)
                checks = []
                # Le automazioni valgono per tutto lo strumento (un canale
                # MIDI): dopo il blocco resta l'ultimo valore scritto in una voce.
                control_ends: List[tuple] = []
                for k, voice_text in enumerate(voices):
                    voice_tokens = tokenize(voice_text)
                    voice_ranges: List[Tuple[Fraction, Fraction]] = []
                    # La prima voce continua il testo cantato della traccia:
                    # un testo dentro di essa prende anche le note prima del
                    # blocco, uno dopo il blocco anche le sue note.
                    sub_events, sub_end, _ = _parse_tokens_exact(
                        voice_tokens, default_octave, grid_beats, lenient, voice_ranges,
                        initial_velocity=velocity, voice=voice + k, extras=None,
                        pending_lyrics=lyric_targets if k == 0 else None,
                        initial_controls=controls)
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
                if pending_ramp and pending_ramp["kind"] == "tempo":
                    _finalize_ramp(new_tempo)
                elif pending_ramp:
                    # kind == "velocity": senza questo controllo la rampa di
                    # velocity resterebbe "orfana" in silenzio (mai richiusa,
                    # nessun crescendo/diminuendo applicato, nessun errore) -
                    # meglio segnalarlo subito che lasciare un bug silenzioso.
                    raise NotationError(
                        tr("Rampa di velocity ('>>'/'<<' dopo N@ o una dinamica) aperta ma mai "
                        "richiusa da un altro N@/dinamica prima di questo cambio di tempo (N§): "
                        "chiudila con un altro N@ prima, oppure sposta N§ dopo la chiusura"), tok
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
                    pending_controls[name] = (cursor, controls[name], curve)
                    continue
                if last_state_kind not in ("velocity", "tempo"):
                    raise NotationError(
                        tr("'>>' / '<<' deve seguire un comando di velocity (N@), di tempo (N§) "
                           "o un'automazione (vol=, expr=, pan=, mod=, rev=, cho=)"), tok
                    )
                start_value = tempo if last_state_kind == "tempo" else velocity
                pending_ramp = {"kind": last_state_kind, "start_value": start_value, "start_index": len(events),
                                "curve": curve}
                continue

            m = RE_CONTROL.match(tok)
            if m:
                name, number = m.group(1), float(m.group(2))
                low, high = CONTROL_RANGES[name]
                if not low <= number <= high:
                    raise NotationError(tr("Valore di '{name}' fuori dall'intervallo {low}..{high}",
                                           name=name, low=low, high=high), tok)
                value = number if name == "pan" else round(number)
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
                    # kind == "tempo": stesso problema del ramo N§ sopra, speculare.
                    raise NotationError(
                        tr("Rampa di tempo ('>>'/'<<' dopo N§) aperta ma mai richiusa da un altro "
                        "N§ prima di questo comando di velocity (N@/dinamica): chiudila con un "
                        "altro N§ prima, oppure sposta il comando di velocity dopo la chiusura"), tok
                    )
                velocity = v
                last_state_kind = "velocity"
                continue

            # Da qui solo token che occupano tempo: col valore di nota
            # esplicito (c'8.) durano quello invece dell'unita' di griglia.
            tok, value = split_note_value(tok)
            hairpin = value[-1] if value[-1:] in ("<", ">") else ""
            if hairpin:
                value = value[:-1]
            unit = note_value_beats(value) if value else grid_beats
            note_start = cursor

            m = RE_REST.match(tok)
            if m:
                if hairpin:
                    raise NotationError(tr("Una pausa non puo' avere una forcella ('<' o '>')"), tok + hairpin)
                mult = int(m.group(1)) if m.group(1) else 1
                dur = unit * mult
                _add(Event(start=float(cursor), duration=float(dur), kind="rest", velocity=velocity))
                cursor += dur
                continue

            m = RE_SLIDE.match(tok)
            if m:
                points = _parse_slide_points(m.group(1), default_octave)
                segment_durations = _slide_segment_durations(points, unit)
                dur = sum(segment_durations)
                _, first_letter, first_octave = points[0]
                _add(Event(
                    start=float(cursor), duration=float(dur), kind="slide", velocity=velocity,
                    letter=first_letter, octave=first_octave,
                    slide_points=[(letter, octave) for _, letter, octave in points[1:]],
                    slide_segment_durations=[float(d) for d in segment_durations],
                ))
                cursor += dur
                if hairpin:
                    _hairpin(hairpin, note_start, dur, tokens[index])
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
                items = [_parse_atom(st, default_octave) for st in sub_toks]
                dur = unit * mult
                _add(Event(start=float(cursor), duration=float(dur), kind="block",
                     velocity=velocity, items=items))
                cursor += dur
                if hairpin:
                    _hairpin(hairpin, note_start, dur, tokens[index])
                continue

            # nota / accordo / percussione singoli
            atom = _parse_atom(tok, default_octave)
            dur = unit * atom["mult"]
            start, duration = float(cursor), float(dur)
            if atom["kind"] == "note":
                _add(Event(start=start, duration=duration, kind="note", velocity=velocity,
                     letter=atom["letter"], octave=atom["octave"],
                     articulation=atom.get("articulation")))
            elif atom["kind"] == "chord":
                _add(Event(start=start, duration=duration, kind="chord", velocity=velocity,
                     symbol=atom["symbol"], octave=atom["octave"], voicing=atom.get("voicing"),
                     articulation=atom.get("articulation"), bass=atom.get("bass")))
            else:  # percussion
                _add(Event(start=start, duration=duration, kind="percussion", velocity=velocity,
                     name=atom["name"]))
            cursor += dur
            if hairpin:
                _hairpin(hairpin, note_start, dur, tokens[index])
        except (NotationError, ValueError):
            if not lenient:
                raise
            # modalita' tollerante (vedi compute_token_spans): il token
            # non valido non occupa tempo e lo stato resta com'era.
        finally:
            if ranges is not None:
                ranges.append((before, cursor))

    if pending_controls and not lenient:
        raise NotationError(tr("Rampa di '{name}' aperta ma mai chiusa da un valore finale ({name}=N)",
                               name=next(iter(pending_controls))))
    if pending_ramp and not lenient:
        anchor = "N§" if pending_ramp["kind"] == "tempo" else "N@"
        raise NotationError(tr("Rampa '>>' o '<<' aperta ma mai chiusa da un valore finale ({anchor})", anchor=anchor))

    return events, cursor, grid_beats


def parse_track_text(text: str, patterns: Dict[str, Pattern], default_octave: int = 4,
                      midi_dir: Optional[str] = None) -> List[Event]:
    """Punto di ingresso completo: tokenizza, espande pattern (%) e riferimenti
    MIDI (&), quindi interpreta lo Stato Corrente."""
    raw_tokens = tokenize(text)
    expanded = expand_patterns(raw_tokens, patterns, midi_dir=midi_dir, default_octave=default_octave)
    return parse_tokens(expanded, default_octave=default_octave)


def validate_track_text(text: str, patterns: Dict[str, Pattern], default_octave: int = 4,
                         midi_dir: Optional[str] = None):
    """Usata dall'editor per la validazione sintattica live. Ritorna (ok, messaggio_errore)."""
    try:
        parse_track_text(text, patterns, default_octave=default_octave, midi_dir=midi_dir)
        return True, ""
    except (NotationError, ValueError) as e:
        return False, str(e)


def _expanded_ranges(text: str, patterns: Dict[str, Pattern], midi_dir: Optional[str],
                     default_octave: int, extras: Optional[dict] = None):
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
    ranges: List[Tuple[Fraction, Fraction]] = []
    _parse_tokens_exact(expanded, default_octave=default_octave, lenient=True, ranges=ranges,
                        extras=extras)
    return raw, expanded, origins, ranges


def compute_token_spans(text: str, patterns: Dict[str, Pattern], midi_dir: Optional[str] = None,
                          default_octave: int = 4) -> List[tuple]:
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
    ordinata per beat_start crescente. I comandi di stato (N:, NT:, N@, N§,
    rampe, SON/SOFF) non producono uno span (non hanno una durata propria)."""
    raw, expanded, origins, ranges = _expanded_ranges(text, patterns, midi_dir, default_octave)
    raw_positions = [(cs, ce) for _, cs, ce in raw]

    covered: Dict[int, Tuple[Fraction, Fraction]] = {}
    for origin, (start, end) in zip(origins, ranges):
        if end <= start:
            continue  # comando di stato o token non valido: nessuna durata
        if origin in covered:
            first, last = covered[origin]
            covered[origin] = (min(first, start), max(last, end))
        else:
            covered[origin] = (start, end)

    spans = []
    for origin in sorted(covered):
        cs, ce = raw_positions[origin]
        start, end = covered[origin]
        spans.append((cs, ce, float(start), float(end - start)))
    return spans


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
    try:
        raw, expanded, origins, ranges = _expanded_ranges(text, patterns, midi_dir, default_octave, extras)
    except NotationError:
        return []
    offset = Fraction(start_beat).limit_denominator(1 << 16)
    grid = _BarGrid(time_sig, metrica_changes)
    issues: List[BarIssue] = []
    reported = set()

    def check(position: Fraction, shift: Fraction, origin: int) -> Fraction:
        """Controlla una '|' (sfasamento gia' accumulato: shift); ritorna
        lo sfasamento aggiornato."""
        # Dove cadrebbe senza gli errori gia' segnalati prima.
        expected = offset + position - shift
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
    issues.sort(key=lambda i: i.char_start)
    return issues


def bar_issues_summary(issues: List[BarIssue]) -> str:
    """Una riga per la barra di stato dell'editor: il primo avviso e
    quanti altri ce ne sono (l'elenco completo va nel suggerimento)."""
    if len(issues) == 1:
        return tr("⚠  Avviso: {msg}", msg=issues[0].message)
    return tr("⚠  Avviso: {msg} (e altri {n})", msg=issues[0].message, n=len(issues) - 1)
