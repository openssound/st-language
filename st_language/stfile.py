"""
Il formato dei file di progetto .st (sezione "Formato dei file" della
specifica): le intestazioni (Tempo:, Metrica:, Tonalita:, Pattern %Nome:,
Traccia Nome [Strumento]:, Box..., Strumento Nome:, Mixer Nome:...) e la
lettura dei corpi dei blocchi. Usato dal lettore della libreria
(st_language.song) e da SoundText (core.project_io), che legge anche i
blocchi propri dell'applicazione (effetti, plugin, clip audio).
"""

import re
from typing import List, Optional, Tuple

from .instruments import InstrumentProfile


# Versione del linguaggio con cui e' scritto il file: "ST: 2.7" (riga
# facoltativa in cima; i lettori piu' vecchi la ignorano).
RE_ST_VERSION = re.compile(r"^ST:\s*(\d+)\.(\d+)$")
# La versione del linguaggio che questo lettore conosce (vedi la specifica).
LANGUAGE_VERSION = (2, 8)

# "Levare: 1" (o "Pickup:"): la battuta in levare, in quarti (anche "1.5" o
# "1/2"); la battuta 1 e' la prima intera.
RE_PICKUP = re.compile(r"^(?:Levare|Pickup):\s*(\d+(?:\.\d+)?(?:/\d+)?)$", re.IGNORECASE)


def parse_pickup(raw: str) -> float:
    """I quarti di 'Levare: raw' ("1", "1.5", "1/2")."""
    from fractions import Fraction
    return float(Fraction(raw))


def format_pickup(quarters: float) -> str:
    """'Levare:' come lo scrive il file: intero o decimale ("1", "1.5")."""
    return f"{round(quarters, 6):g}"

# Le parole chiave del file si scrivono in italiano o in inglese
# (Metrica/Meter, Tonalita/Key, Traccia/Track, Strumento/Instrument...);
# chi scrive il file usa sempre la forma italiana.
RE_TEMPO = re.compile(r"^Tempo:\s*(\d+)\s*BPM$", re.IGNORECASE)

RE_METRICA = re.compile(r"^(?:Metrica|Meter|Time):\s*(\d+/\d+)$", re.IGNORECASE)

# "Master: 80" persiste il volume master del progetto (100 = guadagno originale).
RE_MASTER = re.compile(r"^Master:\s*(\d+)$", re.IGNORECASE)

# "Tonalita: Am" persiste la tonalita' del brano (vedi core.chords.parse_key_signature).
RE_KEY = re.compile(r"^(?:Tonalita|Tonalità|Key):\s*(.+)$", re.IGNORECASE)
# 2.7: la tonalita' per battuta, come Tempo e Metrica: "Tonalita: 1: C, 17: G".
_KEY_VALUE = r"[A-G][#b♭]?m?"
RE_KEY_LIST_HDR = re.compile(rf"^(?:Tonalita|Tonalità|Key):\s*(\d+\s*:\s*{_KEY_VALUE}(?:\s*,\s*\d+\s*:\s*{_KEY_VALUE})*)$",
                             re.IGNORECASE)
RE_BAR_KEY = re.compile(rf"(\d+)\s*:\s*({_KEY_VALUE})")

# 2.7: titolo e autori del brano (testo libero fino a fine riga).
RE_TITLE = re.compile(r"^(?:Titolo|Title):\s*(.*)$", re.IGNORECASE)
RE_COMPOSER = re.compile(r"^(?:Autore|Composer):\s*(.*)$", re.IGNORECASE)
RE_LYRICIST = re.compile(r"^(?:Parole|Lyricist):\s*(.*)$", re.IGNORECASE)

# "Ambiente: sala" persiste l'ambiente del riverbero del synth (vedi core.effects).
RE_AMBIENTE = re.compile(r"^(?:Ambiente|Room):\s*(\w+)$", re.IGNORECASE)

# Forma estesa con cambi a partire da una certa battuta: "Tempo: 1: 120, 5: 140, 9: 100"
RE_TEMPO_LIST_HDR = re.compile(r"^Tempo:\s*(\d+\s*:\s*\d+(?:\s*,\s*\d+\s*:\s*\d+)*)$", re.IGNORECASE)

RE_METRICA_LIST_HDR = re.compile(r"^(?:Metrica|Meter|Time):\s*(\d+\s*:\s*\d+/\d+(?:\s*,\s*\d+\s*:\s*\d+/\d+)*)$", re.IGNORECASE)

RE_BAR_VALUE = re.compile(r"(\d+)\s*:\s*(\d+(?:/\d+)?)")

RE_PATTERN_HDR = re.compile(r"^Pattern\s+%(\w+):$")

# "Strumento Nome:" definisce uno strumento personalizzato (program=..., vedi
# _parse_instrument_body).
RE_INSTRUMENT_HDR = re.compile(r"^(?:Strumento|Instrument)\s+(\w+):$")

# "Mixer Nome:" persiste volume/pan/mute/solo della traccia "Nome".
RE_MIXER_HDR = re.compile(r"^Mixer\s+(.+?):$")

# "Effetti Nome:" persiste la catena di effetti della traccia "Nome" (vedi
# core.effects): una riga per effetto, "tipo: parametro=valore ...", con
# "spento" se l'effetto e' escluso e "preset=Nome" se parte da un preset.
RE_EFFECTS_HDR = re.compile(r"^(?:Effetti|Effects)\s+(.+?):$")

# "Catena master:" e' la catena di effetti sul mix finale (Project.master_effects);
# parola diversa da "Effetti" per non confondersi con una traccia chiamata "master".
RE_MASTER_CHAIN_HDR = re.compile(r"^(?=Catena\s+master:$|Master\s+chain:$)(\w+)", re.IGNORECASE)

RE_EFFECT_ITEM = re.compile(r"(\w+):((?:\s+(?:[\w.]+=(?:\"[^\"]*\"|[^\s]+)|spento|off))*)")

# "Plugin Nome:" e' lo strumento plugin della traccia "Nome" (Track.synth,
# vedi core.plugins): ref="vst3:..." o ref="lv2:...", i parametri come
# p.chiave=valore e, per i VST3, stato="base64".
RE_SYNTH_HDR = re.compile(r"^Plugin\s+(.+?):$")

# "Box TrackName "NomeBox" |beat:" persiste un box della vista Struttura
# brano (core.model.Clip) sulla traccia "TrackName", posizionato a "beat"
# (in beat/quarti) - vedi core.arrangement. Il separatore e' "|" (non "@",
# gia' usato per la velocity/dinamica nel corpo delle tracce, es. "100@" o
# "mf@": riusarlo qui per un significato del tutto diverso confonderebbe la
# lettura/scrittura a mano del file, anche se i due non si sovrappongono mai
# davvero nel parsing).
RE_BOX_HDR = re.compile(r'^Box\s+(.+?)\s+"(.*)"\s*\|(\d+(?:\.\d+)?)\s*:$')

# "Audio TrackName "NomeClip" |beat:" persiste una clip di una traccia audio
# (core.model.AudioClip), con nel corpo 'file="percorso"' (relativo alla
# cartella del file .st) ed eventualmente 'trim=inizio,fine' (secondi) e
# 'gain=dB'. Stessa forma dei Box.
RE_AUDIO_HDR = re.compile(r'^Audio\s+(.+?)\s+"(.*)"\s*\|(\d+(?:\.\d+)?)\s*:$')

RE_AUDIO_FILE = re.compile(r'file\s*=\s*"([^"]*)"')

RE_AUDIO_TRIM = re.compile(r'trim\s*=\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)')

RE_AUDIO_GAIN = re.compile(r'gain\s*=\s*(-?\d+(?:\.\d+)?)')

# Corpo di "Traccia Nome [Audio]:": come registrarla (vedi core.model.Track).
RE_AUDIO_INPUT = re.compile(r"(?:ingresso|input)\s*=\s*(\w+)")

RE_AUDIO_CHANNELS = re.compile(r"(?:canali|channels)\s*=\s*(\d+(?:\+\d+)*)")

# Forma corta "Strumento:" / "Strumento N:": il nome di uno strumento
# conosciuto (anche con cifre, come i GM "Lead8basslead" o "Pad8sweep"),
# indice facoltativo - vedi short_track_header.
RE_TRACK_HDR = re.compile(r"^([A-Za-z]\w*?)\s*(\d*)\s*:$")
_RE_TRACK_HDR_SPACED = re.compile(r"^([A-Za-z]\w*)(?:\s+(\d+))?\s*:$")


def short_track_header(line: str, instrument_names) -> Optional[Tuple[str, str]]:
    """(strumento, indice) di un'intestazione corta di traccia ("Piano:",
    "Piano 2:", "Lead8basslead 2:"), None se la riga non lo e' o se lo
    strumento non e' fra instrument_names. L'indice va dopo uno spazio:
    "Guitar2:" e' lo strumento "Guitar2", non Guitar con indice 2."""
    m = _RE_TRACK_HDR_SPACED.match(line)
    if m and m.group(1) in instrument_names:
        return m.group(1), m.group(2) or ""
    return None

# Formato esplicito con parentesi quadre, usato quando il nome della traccia
# non coincide con la convenzione "<Strumento> <indice>:" (es. dopo una
# rinomina) - vedi funzionalita' 2.
RE_TRACK_HDR_EXPLICIT = re.compile(r"^(?:Traccia|Track)\s+(.+?)\s*\[(\w+)\]\s*:$")

RE_KV_EQUALS = re.compile(r"(\w+)=([\w.-]+)")

RE_KV_COLON = re.compile(r"(\w+):\s*([\w.-]+)")

_TRACK_HDR_PATTERNS = (RE_ST_VERSION, RE_PICKUP, RE_TEMPO, RE_METRICA, RE_MASTER, RE_KEY, RE_PATTERN_HDR, RE_TRACK_HDR,
                        RE_TRACK_HDR_EXPLICIT, RE_MIXER_HDR, RE_BOX_HDR,
                        RE_AUDIO_HDR, RE_EFFECTS_HDR, RE_MASTER_CHAIN_HDR, RE_TITLE, RE_COMPOSER, RE_LYRICIST)

VOLUME_MAX = 200  # 100 = guadagno originale (unita'), fino a 200 = raddoppio percepito

def _parse_bar_value_list(raw: str, is_metrica: bool = False) -> List[tuple]:
    """Parsa 'N: v, N: v, ...' in [(bar:int, value), ...], ordinato per
    battuta. value e' str per la metrica (es. '3/4'), int per il tempo."""
    pairs = RE_BAR_VALUE.findall(raw)
    result = []
    for bar_s, value_s in pairs:
        bar = int(bar_s)
        value = value_s if is_metrica else int(value_s)
        result.append((bar, value))
    return sorted(result, key=lambda p: p[0])

def parse_key_list(raw: str) -> List[Tuple[int, str]]:
    """'1: C, 17: G' in [(battuta, tonalita')], ordinato per battuta."""
    return sorted(((int(bar), key) for bar, key in RE_BAR_KEY.findall(raw)), key=lambda p: p[0])


def _si(value: Optional[str], default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("si", "sì", "s", "true", "1", "yes", "y")

def _parse_kv_body(body: str) -> dict:
    """Estrae coppie chiave/valore da un corpo di blocco, accettando sia lo
    stile 'chiave=valore' sia lo stile 'chiave: valore' (una o piu' per riga,
    equivalenti dopo la concatenazione delle righe del blocco)."""
    kv = dict(RE_KV_COLON.findall(body))
    kv.update(RE_KV_EQUALS.findall(body))  # eventuali chiave=valore hanno priorita' se presenti entrambi
    return kv

def _convert_pan_to_0_127(raw: str) -> int:
    """Converte un valore di pan in scala -1.0..1.0 (convenzione audio
    comune, es. 'pan: 0.2') nella scala interna 0-127 (64 = centro).
    Accetta anche valori gia' espressi in scala -64..64 o 0..127."""
    v = float(raw)
    if -1.0 <= v <= 1.0:
        norm = v
    elif -64.0 <= v <= 64.0:
        norm = v / 64.0
    else:
        norm = (v - 64.0) / 64.0
    norm = max(-1.0, min(1.0, norm))
    return max(0, min(127, round(64 + norm * 63)))

def _pan_0_127_to_normalized(value: int) -> float:
    """Inversa di _convert_pan_to_0_127: da scala interna 0-127 a -1.0..1.0."""
    return round((value - 64) / 63.0, 2)

def _convert_volume(raw: str) -> int:
    """Volume/guadagno di traccia: 0-200, dove 100 = guadagno originale
    (unita'), valori maggiori aumentano la velocity delle note oltre
    l'originale, valori minori la riducono."""
    return max(0, min(VOLUME_MAX, round(float(raw))))

def _parse_instrument_body(name: str, body: str) -> InstrumentProfile:
    """Lo strumento di un blocco 'Strumento Nome:' (program=40 percussione=no
    ottava=3 range=36-96 poly=si voicing=spread)."""
    kv = dict(RE_KV_EQUALS.findall(body))
    range_low, range_high = 40, 88
    try:
        transposition = int(kv.get("trasposizione", kv.get("transposition", 0)))
    except ValueError:
        transposition = 0
    if "range" in kv and "-" in kv["range"]:
        lo, hi = kv["range"].split("-", 1)
        try:
            range_low, range_high = int(lo), int(hi)
        except ValueError:
            pass
    return InstrumentProfile(
        name=name,
        gm_program=int(kv.get("program", 0)),
        is_percussion=_si(kv.get("percussione", kv.get("percussion")), False),
        default_octave=int(kv.get("ottava", kv.get("octave", 4))),
        range_low=range_low,
        range_high=range_high,
        polyphonic=_si(kv.get("poly"), True),
        voicing_style=kv.get("voicing", "spread"),
        transposition=max(-48, min(48, transposition)),
    )

def _parse_mixer_body(body: str) -> dict:
    """Estrae {volume, pan, mute, solo} (solo le chiavi presenti) da un
    blocco 'Mixer Nome:'."""
    kv = _parse_kv_body(body)
    out = {}
    if "volume" in kv:
        out["volume"] = _convert_volume(kv["volume"])
    if "pan" in kv:
        out["pan"] = _convert_pan_to_0_127(kv["pan"])
    if "mute" in kv:
        out["mute"] = _si(kv["mute"], False)
    if "solo" in kv:
        out["solo"] = _si(kv["solo"], False)
    for key, field in (("riverbero", "reverb"), ("reverb", "reverb"), ("chorus", "chorus")):
        if key in kv:
            out[field] = max(0, min(100, round(float(kv[key]))))
    return out

def _notation_body_lines(text: str) -> List[str]:
    """Il testo di una traccia o di un box come righe del corpo del
    blocco, ognuna rientrata: le righe (e quindi i commenti '//') restano
    quelle scritte dall'utente. Le righe vuote si tolgono, perche' nel file
    una riga vuota chiude il blocco (il resto andrebbe perso)."""
    body = [line.strip() for line in text.splitlines() if line.strip()]
    return ["  " + line for line in body] or ["  "]


def _extract_named_blocks(lines: List[str], header_re) -> List[Tuple[str, str]]:
    """Pre-scansione generica: estrae tutti i blocchi che iniziano con
    header_re (es. 'Strumento Nome:' o 'Mixer Nome:'), indipendentemente
    dalla loro posizione rispetto alle tracce che li usano."""
    blocks = []
    current_name, buffer = None, []

    def flush():
        nonlocal current_name, buffer
        if current_name:
            blocks.append((current_name, " ".join(buffer).strip()))
        current_name, buffer = None, []

    for raw_line in lines:
        line = raw_line.strip()
        if line == "":
            flush()
            continue
        m = header_re.match(line)
        if m:
            flush()
            current_name = m.group(1)
            continue
        if current_name and not any(rx.match(line) for rx in _TRACK_HDR_PATTERNS):
            buffer.append(line)
        else:
            flush()
    flush()
    return blocks


def instrument_blocks(lines: List[str]) -> List[Tuple[str, str]]:
    """I blocchi 'Strumento Nome:' (o 'Instrument Nome:') con la loro
    definizione: (nome, corpo). Un blocco senza 'program=' non definisce
    nessuno strumento (era la vecchia forma con 'type:') e si salta."""
    return [(name, body) for name, body in _extract_named_blocks(lines, RE_INSTRUMENT_HDR)
            if "program" in RE_KV_EQUALS_KEYS.findall(body)]


RE_KV_EQUALS_KEYS = re.compile(r"(\w+)=")


def _extract_box_blocks(lines: List[str], header_re=RE_BOX_HDR) -> List[Tuple[str, str, float, str]]:
    """Pre-scansione dei blocchi 'Box TrackName "NomeBox" |beat:' (vedi
    RE_BOX_HDR; con header_re=RE_AUDIO_HDR le clip audio, stessa forma),
    indipendentemente dalla loro posizione rispetto alla traccia a cui
    appartengono. Ritorna (track_name, box_name, start_beat, body_text)."""
    blocks = []
    current, buffer = None, []

    def flush():
        nonlocal current, buffer
        if current:
            sep = "\n" if header_re is RE_BOX_HDR else " "     # come le tracce
            blocks.append((current[0], current[1], current[2], sep.join(buffer).strip()))
        current, buffer = None, []

    for raw_line in lines:
        line = raw_line.strip()
        if line == "":
            flush()
            continue
        m = header_re.match(line)
        if m:
            flush()
            current = (m.group(1).strip(), m.group(2), float(m.group(3)))
            continue
        if current and not any(rx.match(line) for rx in _TRACK_HDR_PATTERNS):
            buffer.append(line)
        else:
            flush()
    flush()
    return blocks
