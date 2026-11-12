"""
Strumenti per la notazione: la mappa delle percussioni (nomi -> note
General MIDI), i 128 suoni General MIDI per famiglia e i profili che
dicono al motore di voicing come scrivere un accordo per uno strumento
(ottava di partenza, estensione, stile).

Gli strumenti predefiniti sono Piano, Guitar, Bass, Trumpet e Drums; ogni
altro nome si risolve con instrument_for() (alias come 'electric_bass',
'violin', 'drum_kit', anche in italiano, francese e spagnolo come 'flauto',
'violoncelle', 'batería', o un nome General MIDI come 'Alto Sax').
"""

import difflib
import re
import unicodedata
from dataclasses import dataclass, replace
from typing import Dict, Optional

from ._i18n import tr

# Mappa percussioni -> nota MIDI standard (General MIDI Drum Map, canale 10).
# Ordine = ordine di assegnazione ai tasti in "Suona con la tastiera" (vedi
# gui.keyboard_play_dialog/gui.keyboard_note_map.PERCUSSION_KEYS): i primi 9
# (kick...ride) sono il set originale sulla riga numerica 1-9, invariati per
# non spostare la disposizione gia' imparata; il resto riempie prima il resto
# della riga numerica (0 ' ì), poi la riga Q (12 tasti), poi la riga A (12
# tasti) - set GM standard piu' ampio (batteria elettronica/rullante
# alternativi, piatti aggiuntivi, percussioni latine), scelto per restare
# entro i 3x12 = 36 tasti disponibili su questo schema.
PERCUSSION_MAP = {
    "kick": 36,
    "snare": 38,
    "hihat": 42,
    "hihat_open": 46,
    "tom1": 48,
    "tom2": 45,
    "floor": 41,
    "crash": 49,
    "ride": 51,
    # resto della riga numerica (0 ' ì)
    "kick2": 35,          # Acoustic Bass Drum
    "rimshot": 37,        # Side Stick
    "clap": 39,           # Hand Clap
    # riga Q (Q W E R T Y U I O P È +)
    "snare2": 40,         # Electric Snare
    "hihat_pedal": 44,    # Pedal Hi-Hat
    "tom_lowmid": 47,     # Low-Mid Tom
    "tom_hi": 50,         # High Tom
    "tom_highfloor": 43,  # High Floor Tom
    "china": 52,          # Chinese Cymbal
    "ride_bell": 53,      # Ride Bell
    "tambourine": 54,
    "splash": 55,         # Splash Cymbal
    "cowbell": 56,
    "crash2": 57,         # Crash Cymbal 2
    "ride2": 59,          # Ride Cymbal 2
    # riga A (A S D F G H J K L Ò À Ù) - percussioni latine
    "bongo_hi": 60,
    "bongo_low": 61,
    "conga_mute": 62,     # Mute Hi Conga
    "conga_open": 63,     # Open Hi Conga
    "conga_low": 64,
    "timbale_hi": 65,
    "timbale_low": 66,
    "cabasa": 69,
    "maracas": 70,
    "claves": 75,
    "woodblock_hi": 76,
    "woodblock_low": 77,
    # 2.7: il resto del set General MIDI (35-81). Vanno in fondo: i primi 36
    # nomi sono i tasti della tastiera di SoundText.
    "side_stick": 37,     # alias di rimshot, il nome General MIDI
    "vibraslap": 58,
    "agogo_hi": 67,
    "agogo_low": 68,
    "whistle_short": 71,
    "whistle_long": 72,
    "guiro_short": 73,
    "guiro_long": 74,
    "cuica_mute": 78,
    "cuica_open": 79,
    "triangle_mute": 80,
    "triangle": 81,       # Open Triangle
}

DRUM_MIDI_CHANNEL = 9  # canale 10 (0-indexed) riservato alle percussioni GM


# Elenco standard General MIDI Level 1 (128 suoni, raggruppati per famiglia),
# usato per far scegliere lo strumento per NOME invece che per numero (0-127).
GM_FAMILIES = [
    ("Pianoforti", 0, [
        "Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano",
        "Honky-tonk Piano", "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavinet",
    ]),
    ("Percussioni intonate", 8, [
        "Celesta", "Glockenspiel", "Music Box", "Vibraphone",
        "Marimba", "Xylophone", "Tubular Bells", "Dulcimer",
    ]),
    ("Organi", 16, [
        "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ",
        "Reed Organ", "Accordion", "Harmonica", "Tango Accordion",
    ]),
    ("Chitarre", 24, [
        "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)",
        "Electric Guitar (clean)", "Electric Guitar (muted)", "Overdriven Guitar",
        "Distortion Guitar", "Guitar Harmonics",
    ]),
    ("Bassi", 32, [
        "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass",
        "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2",
    ]),
    ("Archi", 40, [
        "Violin", "Viola", "Cello", "Contrabass",
        "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani",
    ]),
    ("Ensemble/Voci", 48, [
        "String Ensemble 1", "String Ensemble 2", "Synth Strings 1", "Synth Strings 2",
        "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit",
    ]),
    ("Ottoni", 56, [
        "Trumpet", "Trombone", "Tuba", "Muted Trumpet",
        "French Horn", "Brass Section", "Synth Brass 1", "Synth Brass 2",
    ]),
    ("Ance", 64, [
        "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax",
        "Oboe", "English Horn", "Bassoon", "Clarinet",
    ]),
    ("Fiati", 72, [
        "Piccolo", "Flute", "Recorder", "Pan Flute",
        "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina",
    ]),
    ("Synth Lead", 80, [
        "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiff)",
        "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)",
    ]),
    ("Synth Pad", 88, [
        "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)",
        "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)",
    ]),
    ("Synth FX", 96, [
        "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)",
        "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)",
    ]),
    ("Etnici", 104, [
        "Sitar", "Banjo", "Shamisen", "Koto",
        "Kalimba", "Bag pipe", "Fiddle", "Shanai",
    ]),
    ("Percussivi", 112, [
        "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock",
        "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal",
    ]),
    ("Effetti sonori", 120, [
        "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet",
        "Telephone Ring", "Helicopter", "Applause", "Gunshot",
    ]),
]

# Suggerimenti automatici (ottava/estensione/voicing) in base alla famiglia GM,
# per rendere piu' intuitiva la creazione di un nuovo strumento personalizzato.
GM_FAMILY_DEFAULTS = {
    "Pianoforti":            dict(default_octave=4, range_low=21, range_high=108, polyphonic=True, voicing_style="spread"),
    "Percussioni intonate":  dict(default_octave=5, range_low=48, range_high=96, polyphonic=True, voicing_style="spread"),
    "Organi":                dict(default_octave=4, range_low=36, range_high=96, polyphonic=True, voicing_style="spread"),
    "Chitarre":              dict(default_octave=3, range_low=40, range_high=88, polyphonic=True, voicing_style="spread"),
    "Bassi":                 dict(default_octave=2, range_low=28, range_high=60, polyphonic=False, voicing_style="root_fifth"),
    "Archi":                 dict(default_octave=3, range_low=36, range_high=96, polyphonic=False, voicing_style="monophonic"),
    "Ensemble/Voci":         dict(default_octave=4, range_low=36, range_high=96, polyphonic=True, voicing_style="spread"),
    "Ottoni":                dict(default_octave=4, range_low=52, range_high=82, polyphonic=False, voicing_style="monophonic"),
    "Ance":                  dict(default_octave=4, range_low=49, range_high=82, polyphonic=False, voicing_style="monophonic"),
    "Fiati":                 dict(default_octave=5, range_low=60, range_high=96, polyphonic=False, voicing_style="monophonic"),
    "Synth Lead":            dict(default_octave=4, range_low=48, range_high=96, polyphonic=False, voicing_style="monophonic"),
    "Synth Pad":             dict(default_octave=3, range_low=36, range_high=96, polyphonic=True, voicing_style="spread"),
    "Synth FX":              dict(default_octave=4, range_low=36, range_high=96, polyphonic=True, voicing_style="spread"),
    "Etnici":                dict(default_octave=4, range_low=40, range_high=84, polyphonic=True, voicing_style="spread"),
    "Percussivi":            dict(default_octave=4, range_low=40, range_high=84, polyphonic=True, voicing_style="spread"),
    "Effetti sonori":        dict(default_octave=4, range_low=36, range_high=96, polyphonic=True, voicing_style="spread"),
}


# Drum kit General MIDI 2 selezionabili sul canale percussioni tramite Bank
# Select (CC0=120) + Program Change (vedi core/midi_export.py). Valori
# verificati contro la specifica MIDI Association GM2 (Program # 1-based
# nella spec ufficiale: Standard Kit #1, Room Kit #9, Power Kit #17,
# Electronic Kit #25, TR-808 Kit #26, Jazz Kit #33, Brush Kit #41,
# Orchestra Kit #49, SFX Kit #57 -> Program Change 0-based = # - 1).
GM_DRUM_KITS = {
    0: "Standard Kit",
    8: "Room Kit",
    16: "Power Kit",
    24: "Electronic Kit",
    25: "TR-808 Kit",
    32: "Jazz Kit",
    40: "Brush Kit",
    48: "Orchestra Kit",
    56: "SFX Kit",
}


def gm_instrument_catalog():
    """Ritorna [(program, nome, famiglia), ...] per i 128 suoni General MIDI,
    usato dalla GUI per popolare la selezione a tendina per nome."""
    out = []
    for family, start, names in GM_FAMILIES:
        for i, name in enumerate(names):
            out.append((start + i, name, family))
    return out


def gm_family_for_program(program: int) -> str:
    for family, start, names in GM_FAMILIES:
        if start <= program < start + len(names):
            return family
    return "Altro"


@dataclass
class InstrumentProfile:
    name: str
    gm_program: int            # Program Change General MIDI (0-127)
    is_percussion: bool = False
    default_octave: int = 4
    range_low: int = 40        # nota MIDI più bassa suonabile
    range_high: int = 84       # nota MIDI più alta suonabile
    polyphonic: bool = True    # False = strumento monofonico (es. Tromba)
    voicing_style: str = "spread"  # "spread" | "root_only" | "root_fifth" | "monophonic"
    # Strumento traspositore (2.7): semitoni fra il suono e la parte scritta
    # (tromba in Si bemolle -2: suona un tono sotto lo scritto). Vale solo
    # per la partitura; il testo si scrive in suoni reali.
    transposition: int = 0
    # 2.11: False se il nome non e' uno strumento noto (suona come
    # pianoforte, e chi legge il brano lo segnala: vedi suggest_instrument)
    resolved: bool = True


# Strumenti iniziali richiesti dall'MVP (sezione 8 delle specifiche)
DEFAULT_INSTRUMENTS = {
    "Piano": InstrumentProfile(
        name="Piano", gm_program=0, default_octave=4,
        range_low=21, range_high=108, voicing_style="spread",
    ),
    "Guitar": InstrumentProfile(
        name="Guitar", gm_program=25, default_octave=3,
        range_low=40, range_high=88, voicing_style="spread",
    ),
    "Bass": InstrumentProfile(
        name="Bass", gm_program=33, default_octave=2,
        range_low=28, range_high=60, polyphonic=False,
        voicing_style="root_fifth",
    ),
    "Trumpet": InstrumentProfile(
        name="Trumpet", gm_program=56, default_octave=4,
        range_low=54, range_high=82, polyphonic=False,
        voicing_style="monophonic",
    ),
    "Drums": InstrumentProfile(
        name="Drums", gm_program=0, default_octave=4,
        is_percussion=True, polyphonic=True, voicing_style="none",
    ),
}


# Alias testuali comuni ("type: electric_bass") -> numero di programma GM.
# Usati per interpretare blocchi "Instrument Nome: type: ..." nel formato
# progetto testuale, come alternativa piu' leggibile alla selezione per nome.
INSTRUMENT_TYPE_ALIASES = {
    "piano": 0, "acoustic_piano": 0, "acoustic_grand_piano": 0, "grand_piano": 0,
    "electric_piano": 4, "honky_tonk_piano": 3, "harpsichord": 6,
    "acoustic_guitar": 25, "guitar": 25, "acoustic_guitar_nylon": 24, "nylon_guitar": 24,
    "acoustic_guitar_steel": 25, "steel_guitar": 25,
    "electric_guitar": 27, "electric_guitar_clean": 27, "clean_guitar": 27,
    "electric_guitar_jazz": 26, "jazz_guitar": 26,
    "distortion_guitar": 30, "overdriven_guitar": 29,
    "acoustic_bass": 32, "bass": 33, "electric_bass": 33, "electric_bass_finger": 33,
    "electric_bass_pick": 34, "fretless_bass": 35, "slap_bass": 36, "synth_bass": 38,
    "violin": 40, "viola": 41, "cello": 42, "contrabass": 43, "double_bass": 43,
    "harp": 46, "timpani": 47,
    "trumpet": 56, "trombone": 57, "tuba": 58, "muted_trumpet": 59,
    "french_horn": 60, "brass_section": 61, "brass": 61, "synth_brass": 62,
    "sax": 65, "alto_sax": 65, "tenor_sax": 66, "soprano_sax": 64, "baritone_sax": 67,
    "oboe": 68, "bassoon": 70, "clarinet": 71,
    "piccolo": 72, "flute": 73, "recorder": 74, "pan_flute": 75, "ocarina": 79,
    "synth_lead": 80, "synth_pad": 88, "pad": 88, "lead": 80,
    "organ": 16, "drawbar_organ": 16, "church_organ": 19, "reed_organ": 20,
    "accordion": 21, "harmonica": 22,
    "strings": 48, "string_ensemble": 48, "choir": 52, "voice": 53,
    "sitar": 104, "banjo": 105, "steel_drums": 114,
}

# 2.11: i nomi in italiano, francese e spagnolo, senza accenti (vedi
# normalize_instrument_name), con i plurali e le varianti comuni. 'alto'
# (la viola in francese) manca apposta: resta il sax contralto di prima.
INSTRUMENT_TYPE_ALIASES.update({
    # italiano
    "pianoforte": 0, "chitarra_classica": 24, "chitarra": 25, "chitarra_acustica": 25,
    "chitarra_elettrica": 27, "basso": 33, "basso_elettrico": 33, "basso_acustico": 32,
    "violino": 40, "violini": 40, "viole": 41, "violoncello": 42, "violoncelli": 42,
    "contrabbasso": 43, "archi": 48, "arpa": 46, "timpano": 47, "tromba": 56, "trombe": 56,
    "tromboni": 57, "corno": 60, "corni": 60, "ottoni": 61, "sax_contralto": 65,
    "sassofono": 65, "sax_tenore": 66, "fagotto": 70, "clarinetto": 71, "ottavino": 72,
    "flauto": 73, "flauti": 73, "flauto_dolce": 74, "organo": 16, "organo_da_chiesa": 19,
    "fisarmonica": 21, "armonica": 22, "vibrafono": 11, "xilofono": 13, "campanelli": 9,
    "coro": 52, "voce": 53, "tappeto": 88,
    # francese
    "guitare_classique": 24, "guitare": 25, "guitare_acoustique": 25, "guitare_electrique": 27,
    "basse": 33, "basse_electrique": 33, "basse_acoustique": 32, "violon": 40, "violons": 40,
    "violoncelle": 42, "contrebasse": 43, "cordes": 48, "harpe": 46, "timbales": 47,
    "trompette": 56, "cor": 60, "cuivres": 61, "saxophone_alto": 65, "saxophone_tenor": 66,
    "hautbois": 68, "basson": 70, "clarinette": 71, "flute_a_bec": 74, "orgue": 16,
    "orgue_d_eglise": 19, "accordeon": 21, "vibraphone": 11, "xylophone": 13, "choeur": 52,
    "voix": 53, "nappe": 88,
    # spagnolo
    "guitarra_clasica": 24, "guitarra": 25, "guitarra_acustica": 25, "guitarra_electrica": 27,
    "bajo": 33, "bajo_electrico": 33, "bajo_acustico": 32, "violines": 40, "violonchelo": 42,
    "chelo": 42, "contrabajo": 43, "cuerdas": 48, "trompeta": 56, "trombon": 57, "trompa": 60,
    "metales": 61, "saxo_alto": 65, "saxo_tenor": 66, "fagot": 70, "clarinete": 71,
    "flautin": 72, "flauta": 73, "flauta_dulce": 74, "organo_de_iglesia": 19, "acordeon": 21,
    "voz": 53, "colchon": 88,
})

# 2.11.1: altri nomi comuni che finivano nel pianoforte (clavicembalo e
# gli strumenti General MIDI che mancavano nelle tre lingue). Non hanno un
# programma General MIDI, e restano sconosciuti, mandolino, ukulele e il
# generico sintetizzatore.
INSTRUMENT_TYPE_ALIASES.update({
    # clavicembalo
    "clavicembalo": 6, "cembalo": 6, "clavecin": 6, "clave": 6,
    # pianoforte elettrico
    "pianoforte_elettrico": 4, "piano_elettrico": 4, "piano_electrique": 4, "piano_electrico": 4,
    # carillon, campane tubolari
    "carillon": 10, "boite_a_musique": 10, "caja_de_musica": 10,
    "campane_tubolari": 14, "campane": 14, "cloches_tubulaires": 14, "campanas_tubulares": 14, "campanas": 14,
    # organo Hammond, bandoneon
    "hammond": 16, "organo_hammond": 16, "orgue_hammond": 16, "organo_hammond_b3": 16,
    "bandoneon": 23,
    # chitarre
    "chitarra_jazz": 26, "guitare_jazz": 26, "guitarra_jazz": 26,
    "chitarra_distorta": 30, "guitare_saturee": 30, "guitarra_distorsionada": 30,
    # bassi
    "basso_fretless": 35, "basse_fretless": 35, "bajo_fretless": 35,
    "basso_synth": 38, "basse_synthe": 38, "bajo_sintetizado": 38,
    # archi
    "archi_tremolo": 44, "cordes_tremolo": 44, "cuerdas_tremolo": 44,
    "pizzicato": 45, "archi_pizzicato": 45, "cordes_pizzicato": 45, "cuerdas_pizzicato": 45,
    "arpa_celtica": 46, "harpe_celtique": 46,
    # ottoni
    "tromba_con_sordina": 59, "tromba_sordina": 59, "trompette_bouchee": 59, "trompeta_con_sordina": 59,
    # sassofoni
    "sax_soprano": 64, "saxophone_soprano": 64, "saxo_soprano": 64,
    "sax_alto": 65, "sax_tenor": 66,
    "sax_baritono": 67, "saxophone_baryton": 67, "saxo_baritono": 67,
    # ance
    "corno_inglese": 69, "cor_anglais": 69, "corno_ingles": 69,
    # fiati
    "flauto_di_pan": 75, "flute_de_pan": 75, "flauta_de_pan": 75,
    "fischio": 78, "sifflet": 78, "silbido": 78,
    "cornamusa": 109, "zampogna": 109, "cornemuse": 109, "gaita": 109,
})

PERCUSSION_TYPE_ALIASES = {"drum_kit", "drums", "percussion", "drumkit",
                           "batteria", "percussioni", "batterie", "percussions", "bateria", "percusion"}

# Le corrispondenze parziali con i nomi General MIDI ('alto' -> 'Alto Sax')
# valgono solo da questa lunghezza: un nome corto ne trova di sbagliate
# ('pan' e' dentro 'timpani', 'cor' dentro 'accordion').
MIN_PARTIAL_MATCH = 4


def normalize_instrument_name(text: str) -> str:
    """Il nome di uno strumento come chiave degli alias: minuscole, senza
    accenti (anche le legature: 'chœur' -> 'choeur'), ogni carattere che non
    e' una lettera o una cifra diventa '_' ('Flûte à bec' -> 'flute_a_bec')."""
    text = text.strip().lower().replace("œ", "oe").replace("æ", "ae")
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def _gm_keys():
    return [(p, normalize_instrument_name(gm_name)) for p, gm_name, _family in gm_instrument_catalog()]


def _gm_program_for(key: str) -> Optional[int]:
    """Il programma General MIDI del nome: prima il nome esatto, poi il
    primo che lo contiene, nell'ordine dei programmi (solo per le chiavi di
    almeno MIN_PARTIAL_MATCH caratteri)."""
    gm = _gm_keys()
    for p, norm in gm:
        if norm == key:
            return p
    if len(key) >= MIN_PARTIAL_MATCH:
        for p, norm in gm:
            if key in norm:
                return p
    return None


def suggest_instrument(name: str) -> Optional[str]:
    """Il nome noto piu' simile a name (alias, predefiniti, nomi General
    MIDI), per l'avviso su uno strumento sconosciuto; None se non ce n'e'
    uno abbastanza vicino."""
    candidates = {normalize_instrument_name(n): n for n in DEFAULT_INSTRUMENTS}
    candidates.update({k: k for k in INSTRUMENT_TYPE_ALIASES})
    candidates.update({k: k for k in PERCUSSION_TYPE_ALIASES})
    candidates.update({normalize_instrument_name(n): n for _p, n, _f in gm_instrument_catalog()})
    found = difflib.get_close_matches(normalize_instrument_name(name), list(candidates), n=1, cutoff=0.75)
    return candidates[found[0]] if found else None


def unknown_instrument_message(name: str) -> str:
    """L'avviso per uno strumento che non si conosce (InstrumentProfile.resolved
    falso), tradotto, con il nome noto piu' simile se ce n'e' uno: lo usano
    il lettore dei file (Song.file_warnings) e l'editor di SoundText."""
    message = tr("«{name}» non e' uno strumento noto: suona come pianoforte", name=name)
    suggestion = suggest_instrument(name)
    if suggestion:
        message += ". " + tr("Forse intendevi «{suggestion}»?", suggestion=suggestion)
    return message


def unrecognized_header_message(name: str) -> str:
    """L'avviso per un'intestazione corta ("Pianoo:") con un corpo sotto
    che non nomina uno strumento noto: la traccia non si legge."""
    message = tr("«{name}:» non e' uno strumento noto: la traccia si ignora", name=name)
    suggestion = suggest_instrument(name)
    if suggestion:
        message += ". " + tr("Forse intendevi «{suggestion}»?", suggestion=suggestion)
    return message


def resolve_instrument_type(type_name: str, name: str) -> InstrumentProfile:
    """Costruisce un InstrumentProfile a partire da un identificatore di tipo
    testuale (es. 'electric_bass', 'drum_kit', 'trumpet'), usato dal formato
    progetto per i blocchi 'Instrument Nome: type: ...'. Applica gli stessi
    valori suggeriti per famiglia usati dalla GUI (ottava/estensione/voicing)."""
    key = normalize_instrument_name(type_name)

    if key in PERCUSSION_TYPE_ALIASES:
        return InstrumentProfile(name=name, gm_program=0, is_percussion=True,
                                  default_octave=4, range_low=0, range_high=127,
                                  polyphonic=True, voicing_style="none")

    program = INSTRUMENT_TYPE_ALIASES.get(key)
    if program is None:
        program = _gm_program_for(key)
    resolved = program is not None
    if not resolved:
        program = 0  # fallback finale: pianoforte (chi legge il brano lo segnala)

    family = gm_family_for_program(program)
    defaults = GM_FAMILY_DEFAULTS.get(family, {})
    return InstrumentProfile(
        name=name,
        gm_program=program,
        is_percussion=False,
        default_octave=defaults.get("default_octave", 4),
        range_low=defaults.get("range_low", 40),
        range_high=defaults.get("range_high", 88),
        polyphonic=defaults.get("polyphonic", True),
        voicing_style=defaults.get("voicing_style", "spread"),
        resolved=resolved,
    )


def instrument_for(name: str, type_name: Optional[str] = None,
                   known: Optional[Dict[str, InstrumentProfile]] = None) -> InstrumentProfile:
    """Il profilo di uno strumento per nome: quelli in known (o i
    predefiniti), altrimenti dedotto dal tipo o dal nome stesso (vedi
    resolve_instrument_type). Un predefinito si da' come copia: chi cambia
    lo strumento di una traccia non cambia quello di tutti i brani."""
    table = known if known is not None else DEFAULT_INSTRUMENTS
    if type_name is None and name in table:
        profile = table[name]
        return replace(profile) if profile is DEFAULT_INSTRUMENTS.get(name) else profile
    return resolve_instrument_type(type_name or name, name)
