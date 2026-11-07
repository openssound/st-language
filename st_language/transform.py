"""
Trasformazioni dei pattern (2.12): funzioni scritte dopo il richiamo di un
pattern, %Tema.invert(e*5).retro+5, che lavorano sugli eventi del pattern
svolto e ne restituiscono di nuovi. Il registro (TRANSFORMS) dice nomi,
argomenti e durata di ogni funzione: lo leggono il parser, il validatore e,
in SoundText, il completamento e la finestra Trasforma.
"""

import copy
import difflib
import re
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Callable, Dict, List, Optional, Tuple

from ._i18n import tr
from .chords import PITCH_CLASS, _canonical_quality, midi_to_pitch, pitch_to_midi
from .notation import (DYNAMICS_TO_VELOCITY, Event, NotationError, Pattern, TRANSPOSE_RANGE, _PitchState,
                       _parse_tokens_exact, _transpose_chord, _transpose_key_name, expand_patterns,
                       key_signature_alters, spell_midi)

SCALE_LETTERS = "cdefgab"
MIN_DURATION = Fraction(1, 32)        # '128, la figura piu' breve
_ACCIDENTALS = {"": 0, "#": 1, "b": -1, "♭": -1}

RE_TRANSFORM_REFERENCE = re.compile(r"^(\d*)%(\w+?)(?=[.+-])")
RE_NOTE_ARGUMENT = re.compile(r"^([a-g])([#b♭]?)(?:\*(\d+))?$")
RE_ROOT = re.compile(r"^([A-G])([#b♭]?)(.*)$")


@dataclass
class Step:
    """Un passo della catena: name e' il nome inglese della funzione, o
    'transpose' per +N; start e end la sua posizione nel token."""
    name: str
    args: tuple = ()
    start: int = 0
    end: int = 0


@dataclass
class Reference:
    """Un richiamo con la sua catena di passi."""
    pattern: str
    mult: int = 1
    steps: List[Step] = field(default_factory=list)


@dataclass
class Context:
    """Quello che le funzioni sanno del punto del richiamo."""
    key: Optional[str] = None             # la tonalita' di riferimento per le note senza un key= loro
    default_octave: int = 4
    token: str = ""
    semitones: int = 0                    # la trasposizione del richiamo: vale anche per il Do di ripiego
    warnings: List[str] = field(default_factory=list)


def _warn(ctx: Context, message: str) -> None:
    if message not in ctx.warnings:
        ctx.warnings.append(message)


def _exact(value: float) -> Fraction:
    return Fraction(value).limit_denominator(10 ** 6)


# ------------------------------------------------------------------ altezze

def _check_midi(midi: int, ctx: Context) -> int:
    if not 0 <= midi <= 127:
        raise NotationError(tr("La trasformazione porta una nota fuori dall'estensione MIDI"), ctx.token)
    return midi


def _map_pitches(ev: Event, note: Callable, chord: Callable) -> None:
    """Applica note(nome, ottava) e chord(simbolo, basso, ottava) a tutte le
    altezze dell'evento: la nota, le tappe di uno slide, gli elementi di un
    blocco. Le percussioni e le pause non ne hanno."""
    if ev.kind in ("note", "slide"):
        ev.letter, ev.octave = note(ev.letter, ev.octave)
        if ev.slide_points:
            ev.slide_points = [note(name, octave) for name, octave in ev.slide_points]
    elif ev.kind in ("chord", "harmony"):
        ev.symbol, ev.bass, octave = chord(ev.symbol, ev.bass, ev.octave if ev.octave is not None else 4)
        if ev.kind == "chord":
            ev.octave = octave
    elif ev.kind == "block":
        for item in ev.items or ():
            if item.get("kind") == "note":
                item["letter"], item["octave"] = note(item["letter"], item["octave"])
            elif item.get("kind") == "chord":
                item["symbol"], item["bass"], item["octave"] = chord(item["symbol"], item.get("bass"),
                                                                     item["octave"])


def _key_for(ev: Event, ctx: Context) -> str:
    """La tonalita' di riferimento di un evento (quella di un key= scritto
    nel pattern, poi quella del punto del richiamo); Do maggiore con un
    avviso se non ce n'e' nessuna."""
    key = ev.key or ctx.key
    if not key:
        _warn(ctx, tr("tonalita' non indicata: uso Do maggiore"))
    return key or _transpose_key_name("C", ctx.semitones)


def _spell(midi: int, key: str) -> Tuple[str, int]:
    """Come si scrive un'altezza: nella tonalita', e fuori scala coi bemolli
    nelle tonalita' con bemolli, coi diesis altrimenti."""
    alters = key_signature_alters(key) if key else {}
    name, octave = spell_midi(midi, alters, any(a == "b" for a in alters.values()))
    if name.endswith("n"):
        return name[:-1], octave
    return (name + alters[name] if name in alters else name), octave


def _step_note(name: str, octave: int, steps: int, key: str, ctx: Context) -> Tuple[str, int]:
    """La nota spostata di 'steps' gradi nella scala: una nota alterata e'
    il suo grado con l'alterazione, che si conserva."""
    alters = key_signature_alters(key)
    letter, accidental = name[0], name[1:]
    offset = _ACCIDENTALS[accidental] - _ACCIDENTALS[alters.get(letter, "")]
    index = SCALE_LETTERS.index(letter) + steps
    octave += index // 7
    letter = SCALE_LETTERS[index % 7]
    value = _ACCIDENTALS[alters.get(letter, "")] + offset
    midi = _check_midi((octave + 1) * 12 + PITCH_CLASS[letter.upper()] + value, ctx)
    if abs(value) > 1:                    # niente doppie alterazioni nella notazione
        return _spell(midi, key)
    return letter + {1: "#", -1: "b", 0: ""}[value], octave


_TRIADS = {(4, 7): "", (3, 7): "m", (3, 6): "dim", (4, 8): "aug"}
_SEVENTHS = {(4, 7, 11): "maj7", (4, 7, 10): "7", (3, 7, 10): "m7", (3, 6, 10): "m7b5"}


def _scale_chords(key: str, degree: int) -> Tuple[str, str]:
    """(triade, settima) sul grado della scala: le loro qualita'."""
    alters = key_signature_alters(key)
    tonic = SCALE_LETTERS.index(key[0].lower())

    def semitones(steps: int) -> int:
        letter = SCALE_LETTERS[(tonic + degree + steps) % 7]
        return PITCH_CLASS[letter.upper()] + _ACCIDENTALS[alters.get(letter, "")]

    root = semitones(0)
    third, fifth, seventh = ((semitones(n) - root) % 12 for n in (2, 4, 6))
    return _TRIADS.get((third, fifth), ""), _SEVENTHS.get((third, fifth, seventh), "")


def _step_chord(symbol: str, bass: Optional[str], octave: int, steps: int, key: str,
                ctx: Context) -> Tuple[str, Optional[str], int]:
    """L'accordo spostato di 'steps' gradi: la fondamentale sale nella
    scala e un accordo della scala prende la qualita' del nuovo grado (C ->
    Dm in Do); uno che non ne fa parte la conserva, con un avviso."""
    letter, accidental, quality = RE_ROOT.match(symbol).groups()
    root = letter.lower() + accidental
    new_root, new_octave = _step_note(root, octave, steps, key, ctx)
    tonic = SCALE_LETTERS.index(key[0].lower())
    degree = (SCALE_LETTERS.index(letter.lower()) - tonic) % 7
    in_scale = _ACCIDENTALS[accidental] == _ACCIDENTALS[key_signature_alters(key).get(letter.lower(), "")]
    written = _canonical_quality(quality)
    triad, seventh = _scale_chords(key, degree)
    new_triad, new_seventh = _scale_chords(key, degree + steps)
    if in_scale and written == _canonical_quality(triad):
        quality = new_triad
    elif in_scale and written and written == seventh:
        quality = new_seventh
    else:
        _warn(ctx, tr("l'accordo {symbol} non e' nella scala di {key}: conserva la sua qualita'",
                      symbol=symbol, key=key))
    if bass:
        bass = _step_note(bass[0].lower() + bass[1:], 4, steps, key, ctx)[0]
        bass = bass[0].upper() + bass[1:]
    return new_root[0].upper() + new_root[1:] + quality, bass, new_octave


_PITCHED_KINDS = ("note", "slide", "chord", "harmony", "block")


def _step_events(events: List[Event], steps: int, ctx: Context) -> None:
    for ev in events:
        if ev.kind not in _PITCHED_KINDS:
            continue
        key = _key_for(ev, ctx)
        _map_pitches(ev, lambda name, octave: _step_note(name, octave, steps, key, ctx),
                     lambda symbol, bass, octave: _step_chord(symbol, bass, octave, steps, key, ctx))


def _do_octave(events, end, ctx, n):
    def chord(symbol, bass, octave):
        return symbol, bass, octave + n

    def note(name, octave):
        _check_midi(pitch_to_midi(name, octave + n), ctx)
        return name, octave + n

    for ev in events:
        _map_pitches(ev, note, chord)
    return events, end


def _first_pitch(events: List[Event]) -> Optional[int]:
    """La prima altezza del pattern; per un blocco, la sua nota piu' bassa."""
    for ev in sorted(events, key=lambda e: e.start):
        if ev.kind in ("note", "slide"):
            return pitch_to_midi(ev.letter, ev.octave)
        if ev.kind == "block":
            notes = [pitch_to_midi(i["letter"], i["octave"]) for i in ev.items or () if i.get("kind") == "note"]
            if notes:
                return min(notes)
    return None


def _do_invert(events, end, ctx, axis=None):
    if any(ev.kind in ("chord", "harmony") or
           (ev.kind == "block" and any(i.get("kind") == "chord" for i in ev.items or ())) for ev in events):
        raise NotationError(tr("Un accordo scritto come simbolo non si puo' invertire: usa un blocco [...]"),
                            ctx.token)
    axis = _first_pitch(events) if axis is None else axis
    if axis is None:
        raise NotationError(tr("Nessuna nota nel pattern: indica l'asse dell'inversione"), ctx.token)
    for ev in events:
        key = ev.key or ctx.key or ""
        _map_pitches(ev, lambda name, octave: _spell(_check_midi(2 * axis - pitch_to_midi(name, octave), ctx), key),
                     None)
    return events, end


def _do_step(events, end, ctx, n):
    _step_events(events, n, ctx)
    return events, end


# ------------------------------------------------------------------ tempo e ordine

def _reject_tempo(events: List[Event], ctx: Context, name: str) -> None:
    if any(ev.kind == "tempo_marker" for ev in events):
        raise NotationError(tr("tempo= dentro il pattern: .{name} cambierebbe il tempo di tutto il brano",
                               name=name), ctx.token)


def _scale_time(events: List[Event], end: Fraction, factor: Fraction, ctx: Context, name: str):
    _reject_tempo(events, ctx, name)
    for ev in events:
        ev.start = float(_exact(ev.start) * factor)
        ev.duration = float(_exact(ev.duration) * factor)
        if ev.slide_segment_durations:
            ev.slide_segment_durations = [float(_exact(d) * factor) for d in ev.slide_segment_durations]
        if 0 < ev.duration < MIN_DURATION and ev.kind != "control":
            raise NotationError(tr(".{name}: una durata diventerebbe piu' breve di '128", name=name), ctx.token)
    return events, end * factor


def _do_augment(events, end, ctx, k):
    return _scale_time(events, end, k, ctx, "augment")


def _do_diminish(events, end, ctx, k):
    return _scale_time(events, end, 1 / k, ctx, "diminish")


def _attached(ev: Event) -> bool:
    """Se l'evento sta attaccato a quello che lo segue (abbellimenti,
    indicazioni, sigle): con .retro restano davanti alla loro nota."""
    return bool(ev.grace) or ev.kind in ("harmony", "text")


def _do_retro(events, end, ctx):
    _reject_tempo(events, ctx, "retro")
    if any(ev.kind == "slide" for ev in events):
        raise NotationError(tr("Uno slide non si puo' rovesciare con .retro"), ctx.token)
    if any(ev.kind in ("control", "sustain") for ev in events):
        raise NotationError(tr("Automazioni e pedale nel pattern non si possono rovesciare con .retro"), ctx.token)
    if any(ev.lyric for ev in events):
        _warn(ctx, tr("con .retro il testo cantato si legge al contrario"))
    units: List[List[Event]] = []
    waiting: List[Event] = []
    for ev in sorted(events, key=lambda e: (e.voice, e.start)):
        if _attached(ev):
            waiting.append(ev)
            continue
        same = [w for w in waiting if w.start == ev.start and w.voice == ev.voice]
        units.extend([w] for w in waiting if w not in same)
        units.append(same + [ev])
        waiting = []
    units.extend([w] for w in waiting)
    out: List[Event] = []
    for unit in reversed(units):
        main = unit[-1]
        start = float(end - _exact(main.start) - _exact(main.duration))
        for ev in unit:
            ev.start = start
            ev.slur = {"start": "stop", "stop": "start"}.get(ev.slur, ev.slur)
        out.extend(unit)
    return sorted(out, key=lambda e: e.start), end


def _do_sequence(events, end, ctx, n, passo):
    _reject_tempo(events, ctx, "sequence")
    if n < 1:
        raise NotationError(tr(".sequence: il numero di presentazioni va da 1 in su"), ctx.token)
    out: List[Event] = []
    for k in range(n):
        part = copy.deepcopy(events)
        if k * passo:
            _step_events(part, k * passo, ctx)
        for ev in part:
            ev.start = float(_exact(ev.start) + k * end)
        out.extend(part)
    return out, end * n


# ------------------------------------------------------------------ dinamica

_VELOCITY_KINDS = ("note", "chord", "block", "percussion", "slide")


def _do_vel(events, end, ctx, value):
    relative, number = value
    sounding = [ev for ev in events if ev.kind in _VELOCITY_KINDS]
    if not relative and len({ev.velocity for ev in sounding}) > 1:
        _warn(ctx, tr(".vel({value}) toglie le differenze di velocity scritte nel pattern", value=number))
    for ev in sounding:
        ev.velocity = max(1, min(127, ev.velocity + number)) if relative else number
    return events, end


def _transpose(events, end, ctx, semitones):
    """+N nella catena, come %Nome+N; la tonalita' di riferimento lo segue."""
    if not TRANSPOSE_RANGE[0] <= semitones <= TRANSPOSE_RANGE[1]:
        raise NotationError(tr("Trasposizione fuori range ({0}..{1} semitoni)", *TRANSPOSE_RANGE), ctx.token)
    for ev in events:
        pitch = _PitchState(ctx.default_octave)
        pitch.key_name = ev.key or ctx.key or ""
        _map_pitches(ev, lambda name, octave: pitch.spell_transposed(name, octave, semitones, ctx.token),
                     lambda symbol, bass, octave: _transpose_chord(symbol, bass, octave, semitones, pitch))
        if ev.key:
            ev.key = _transpose_key_name(ev.key, semitones)
    if ctx.key:
        ctx.key = _transpose_key_name(ctx.key, semitones)
    ctx.semitones += semitones
    return events, end


# ------------------------------------------------------------------ argomenti

def _integer(text: str, ctx_name: str, label: str) -> int:
    if not re.match(r"^[+-]?\d+$", text):
        raise NotationError(tr(".{name}: {label} deve essere un numero intero", name=ctx_name, label=label), text)
    return int(text)


def _factor(text: str, ctx_name: str, label: str) -> Fraction:
    if not re.match(r"^\d+(\.\d+)?$", text) or Fraction(text) <= 0:
        raise NotationError(tr(".{name}: {label} deve essere un numero maggiore di 0", name=ctx_name, label=label),
                            text)
    return Fraction(text)


def _note(text: str, ctx_name: str, label: str):
    """(nome, ottava o None): l'ottava mancante e' quella della traccia."""
    m = RE_NOTE_ARGUMENT.match(text)
    if not m:
        raise NotationError(tr(".{name}: {label} deve essere una nota", name=ctx_name, label=label), text)
    return m.group(1) + m.group(2), int(m.group(3)) if m.group(3) else None


def _velocity(text: str, ctx_name: str, label: str) -> Tuple[bool, int]:
    """(relativa, numero): +10 e -20 sono relative, 80 e mf assolute."""
    if text in DYNAMICS_TO_VELOCITY:
        return False, DYNAMICS_TO_VELOCITY[text]
    if re.match(r"^[+-]\d+$", text):
        return True, int(text)
    if text.isdigit() and 1 <= int(text) <= 127:
        return False, int(text)
    raise NotationError(tr(".{name}: {label} deve essere +N, -N, un valore da 1 a 127 o una dinamica",
                           name=ctx_name, label=label), text)


@dataclass
class Argument:
    name: str
    parse: Callable
    required: bool = True


@dataclass
class Transform:
    name: str                             # inglese, il nome canonico
    alias: str                            # italiano
    arguments: Tuple[Argument, ...]
    apply: Callable
    duration: Callable                    # (durata in ingresso, argomenti) -> durata
    help: str
    example: str = ""


def _same(duration, *_args):
    return duration


TRANSFORMS: Dict[str, Transform] = {t.name: t for t in (
    Transform("octave", "ottava", (Argument("n", _integer),), _do_octave, _same,
              "Sposta di n ottave", "%Tema.octave(-1)"),
    Transform("invert", "inverti", (Argument("asse", _note, required=False),), _do_invert, _same,
              "Inversione cromatica intorno a una nota", "%Tema.invert(e*4)"),
    Transform("step", "grado", (Argument("n", _integer),), _do_step, _same,
              "Trasposizione diatonica: n gradi nella scala", "%Tema.step(2)"),
    Transform("augment", "aumenta", (Argument("k", _factor),), _do_augment, lambda d, k: d * k,
              "Durate per k", "%Tema.augment(2)"),
    Transform("diminish", "diminuisci", (Argument("k", _factor),), _do_diminish, lambda d, k: d / k,
              "Durate diviso k", "%Tema.diminish(2)"),
    Transform("retro", "retrogrado", (), _do_retro, _same,
              "Dalla fine all'inizio", "%Tema.retro"),
    Transform("sequence", "progressione", (Argument("n", _integer), Argument("passo", _integer)), _do_sequence,
              lambda d, n, _passo: d * n, "Il motivo n volte, ogni volta spostato di passo gradi",
              "%Motivo.sequence(3,-1)"),
    Transform("vel", "vel", (Argument("x", _velocity),), _do_vel, _same,
              "Velocity relativa (+10) o assoluta (80, mf)", "%Tema.vel(-20)"),
)}
_BY_NAME = {alias: t for t in TRANSFORMS.values() for alias in (t.name, t.alias)}


def is_transform_name(name: str) -> bool:
    return name.lower() in _BY_NAME


def is_transform_reference(tok: str) -> bool:
    """Se il token e' un richiamo con almeno una funzione (%Tema.retro)."""
    m = RE_TRANSFORM_REFERENCE.match(tok)
    return bool(m) and "." in tok[m.end():]


def parse_reference(tok: str) -> Reference:
    """Il richiamo di pattern come pattern, ripetizioni e passi con
    argomenti e posizioni. Solleva NotationError con il problema preciso."""
    m = RE_TRANSFORM_REFERENCE.match(tok) or re.match(r"^(\d*)%(\w+)", tok)
    if not m:
        raise NotationError(tr("Token non riconosciuto dalla grammatica"), tok)
    if tok.count("(") > tok.count(")"):
        raise NotationError(tr("Niente spazi negli argomenti di una funzione: scrivi .sequence(3,-1)"), tok)
    reference = Reference(m.group(2), int(m.group(1) or 1))
    i = m.end()
    while i < len(tok):
        step = re.compile(r"[+-]\d+").match(tok, i)
        if step:
            reference.steps.append(Step("transpose", (int(step.group()),), i, step.end()))
            i = step.end()
            continue
        call = re.compile(r"\.(\w+)(?:\(([^()]*)\))?").match(tok, i)
        if not call:
            raise NotationError(tr("Token non riconosciuto dalla grammatica"), tok)
        reference.steps.append(_parse_step(call, tok))
        i = call.end()
    return reference


def _parse_step(call, tok: str) -> Step:
    written, raw = call.group(1), call.group(2)
    transform = _BY_NAME.get(written.lower())
    if transform is None:
        close = difflib.get_close_matches(written.lower(), list(_BY_NAME), n=1, cutoff=0.6)
        if close:
            raise NotationError(tr(".{name} non esiste: forse .{other}?", name=written, other=close[0]), tok)
        raise NotationError(tr(".{name} non esiste", name=written), tok)
    texts = [t for t in (raw or "").split(",")] if raw else []
    if len(texts) > len(transform.arguments):
        raise NotationError(tr(".{name}: troppi argomenti", name=transform.name), tok)
    args = []
    for k, argument in enumerate(transform.arguments):
        if k < len(texts):
            args.append(argument.parse(texts[k], transform.name, argument.name))
        elif argument.required:
            raise NotationError(tr(".{name}: manca {label}", name=transform.name, label=argument.name), tok)
    return Step(transform.name, tuple(args), call.start(), call.end())


def apply_steps(events: List[Event], end: Fraction, steps: List[Step], ctx: Context) -> Tuple[List[Event], Fraction]:
    """I passi applicati, da sinistra a destra, agli eventi di un pattern
    (che dura 'end'): eventi nuovi e nuova durata."""
    events = [ev for ev in copy.deepcopy(events) if ev.kind != "repeat"]
    for step in steps:
        if step.name == "transpose":
            events, end = _transpose(events, end, ctx, *step.args)
        elif step.name == "invert" and step.args:
            name, octave = step.args[0]
            axis = pitch_to_midi(name, ctx.default_octave if octave is None else octave)
            events, end = _do_invert(events, end, ctx, axis)
        else:
            events, end = TRANSFORMS[step.name].apply(events, end, ctx, *step.args)
    return events, end


def duration_after(step: Step, duration: Fraction) -> Fraction:
    """La durata di un pattern dopo un passo, senza svolgerlo."""
    if step.name == "transpose":
        return duration
    return TRANSFORMS[step.name].duration(duration, *step.args)


# ------------------------------------------------------------------ API per SoundText

def list_transforms() -> List[dict]:
    """Le funzioni: nome inglese, alias italiano, argomenti e aiuto breve
    tradotto, per il completamento e la finestra Trasforma."""
    return [{"name": t.name, "alias": t.alias, "help": tr(t.help),
             "arguments": [{"name": a.name, "required": a.required} for a in t.arguments]}
            for t in TRANSFORMS.values()]


def describe_transform(name: str) -> dict:
    """Una funzione, per il suggerimento e la guida: nome inglese o alias
    italiano in ingresso; nome, alias, firma, aiuto tradotto ed esempio."""
    transform = _BY_NAME.get(name.lower().lstrip("."))
    if transform is None:
        raise NotationError(tr(".{name} non esiste", name=name.lstrip(".")), name)
    arguments = ",".join(a.name for a in transform.arguments)
    return {"name": transform.name, "alias": transform.alias, "help": tr(transform.help),
            "signature": f".{transform.name}({arguments})" if arguments else f".{transform.name}",
            "example": transform.example}


@dataclass
class Expansion:
    """Quello che suona un richiamo: gli eventi (dall'inizio del richiamo,
    a 0) e la durata in quarti; 'stages' ha, dopo il pattern com'e', una
    coppia (passo, eventi) per ogni passo della catena. Se il richiamo si
    ripete (3%Tema.retro), stages vale per una presentazione sola."""
    events: List[Event]
    duration: float
    stages: List[tuple]
    warnings: List[str]


def expand_reference(tok: str, patterns: Dict[str, Pattern], default_octave: int = 4, meter=None,
                     position: float = 0.0, key: str = "", grid: float = 1.0, velocity: int = 80) -> Expansion:
    """Gli eventi di un richiamo, con o senza funzioni, e quelli dopo ogni
    passo, per l'anteprima delle note e la finestra Trasforma. 'grid'
    (in quarti) e 'velocity' sono quelli del punto del richiamo; la
    tonalita' di riferimento e' 'key' (il key= in vigore in quel punto) o,
    con 'meter', la Tonalita: del brano a 'position' (in quarti). Solleva
    NotationError come il parser."""
    reference = parse_reference(tok)
    if reference.pattern not in patterns:
        raise NotationError(tr("Pattern '%{name}' non definito", name=reference.pattern), tok)
    origin = _exact(position)
    tokens = expand_patterns(["%" + reference.pattern], patterns, default_octave=default_octave)
    events, end, _ = _parse_tokens_exact(tokens, default_octave, _exact(grid), initial_velocity=velocity,
                                         meter=meter, origin_beat=origin, record_keys=True)
    ctx = Context(key or (meter.key_at(origin) if meter is not None else "") or None, default_octave, tok)
    events = [ev for ev in events if ev.kind != "repeat"]
    stages = [(None, _without_keys(events))]
    for step in reference.steps:
        events, end = apply_steps(events, end, [step], ctx)
        stages.append((step, _without_keys(events)))
    result: List[Event] = []
    for k in range(reference.mult):
        for ev in stages[-1][1]:
            ev = copy.deepcopy(ev)
            ev.start = float(_exact(ev.start) + k * end)
            result.append(ev)
    return Expansion(result, float(end * reference.mult), stages, ctx.warnings)


def _without_keys(events: List[Event]) -> List[Event]:
    events = copy.deepcopy(events)
    for ev in events:
        ev.key = None
    return events


def _argument_text(value) -> str:
    if isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], bool):
        relative, number = value
        return f"{number:+d}" if relative else str(number)
    if isinstance(value, tuple):
        name, octave = value
        return name if octave is None else f"{name}*{octave}"
    return f"{float(value):g}" if isinstance(value, Fraction) else str(value)


def format_reference(reference: Reference, italian: bool = False) -> str:
    """Il testo del richiamo: nomi inglesi, o italiani con italian=True."""
    text = (str(reference.mult) if reference.mult > 1 else "") + "%" + reference.pattern
    for step in reference.steps:
        if step.name == "transpose":
            text += f"{step.args[0]:+d}"
            continue
        transform = TRANSFORMS[step.name]
        text += "." + (transform.alias if italian else transform.name)
        if step.args:
            text += "(" + ",".join(_argument_text(a) for a in step.args) + ")"
    return text
