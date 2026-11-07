"""
Dagli eventi al testo, e dai richiami al testo per esteso.

events_to_text scrive in notazione ST una lista di eventi: rileggendo il
testo si riottengono gli stessi eventi. expand_to_text sostituisce i
richiami di un testo con il loro contenuto, senza cambiarne il suono: lo
controlla da sola, e se non ci riesce lo dice.
"""

from fractions import Fraction
from math import gcd
from typing import Dict, List, Optional, Tuple

from ._i18n import tr
from .chords import pitch_to_midi
from .notation import (BAR_CHECK, Event, NotationError, Pattern, PitchRewriter, RE_MIDI_REF, RE_NAVIGATION,
                       RE_PATTERN_REF, RE_RAMP_DOWN, RE_RAMP_UP, RE_REPEAT_GROUP, RE_TEMPO_SET, RE_TRANSPOSE,
                       RE_VOICES, RESET_TOKEN, _is_repeat_token, _is_rest, _is_stateless, _resolve_midi_ref,
                       _state_slot, _STATE_SLOTS, grid_value_beats, key_signature_alters, note_value_beats,
                       parse_track_text, rewrite_tokens, split_voices, tokenize, tokenize_spans)

_ARTICULATION_MARKS = {"staccato": "!", "mute": "x", "legato": "_"}
_GRACE_MARKS = {"acciaccatura": "'g", "appoggiatura": "'G"}
_SOUNDING = ("note", "chord", "block", "percussion", "slide", "rest")
_SKIPPED = ("repeat", "navigation")     # gli eventi sono gia' svolti: ripetizioni e salti non servono piu'


def _exact(value: float) -> Fraction:
    return Fraction(value).limit_denominator(10 ** 6)


def _grid_token(divisor: int) -> str:
    """Il comando di griglia di 4/divisor quarti: 8:, 12: si scrive 8T:."""
    if divisor % 3 == 0:
        straight = divisor * 2 // 3
        if straight & (straight - 1) == 0:
            return f"{straight}T:"
    return f"{divisor}:"


def _number(value: float) -> str:
    return f"{round(value, 6):g}"


class _Voice:
    """Scrive gli eventi di una voce, tenendo il filo dello stato."""

    def __init__(self, default_octave: int, alters: Dict[str, str], grid: Optional[Fraction],
                 velocity: Optional[int]):
        self.default_octave, self.alters = default_octave, alters
        self.grid, self.velocity = grid, velocity
        self.swing = self.shift = None
        self.tokens: List[str] = []
        self.unsung = False               # una nota senza sillaba aspetta il prossimo testo cantato

    def _note_name(self, name: str, octave: int) -> str:
        letter, accidental = name[0], name[1:]
        written = self.alters.get(letter, "")
        if accidental == written:
            accidental = ""
        elif not accidental:
            accidental = "n"
        return f"{letter}{accidental}*{octave}"

    def _chord(self, symbol: str, bass: Optional[str], octave: int, voicing: Optional[str]) -> str:
        return (symbol + (f".{voicing}" if voicing else "") + (f"/{bass}" if bass else "")
                + (f"*{octave}" if octave != self.default_octave else ""))

    def _atom(self, item: dict) -> str:
        if item["kind"] == "note":
            return self._note_name(item["letter"], item["octave"])
        if item["kind"] == "chord":
            return self._chord(item["symbol"], item.get("bass"), item["octave"], item.get("voicing"))
        return item["name"]

    def _fit(self, duration: Fraction) -> int:
        """Quante unita' di griglia dura l'evento, cambiando griglia se serve."""
        if self.grid and (duration / self.grid).denominator == 1:
            return int(duration / self.grid)
        self.grid = Fraction(1, duration.denominator)
        self.tokens.append(_grid_token(4 * duration.denominator))
        return duration.numerator

    def _state(self, ev: Event) -> None:
        if ev.velocity != self.velocity:
            self.velocity = ev.velocity
            self.tokens.append(f"{ev.velocity}@")
        if ev.swing != self.swing:
            self.swing = ev.swing
            if ev.swing:
                self.tokens.append(f"swing{'16' if ev.swing[0] == 0.5 else ''}={round(ev.swing[1] * 100)}")
            else:
                self.tokens.append("swing=50")
        if ev.shift != self.shift:
            self.shift = ev.shift
            self.tokens.append(f"shift={ev.shift or 0}")

    def _slide(self, ev: Event) -> str:
        durations = [_exact(d) for d in ev.slide_segment_durations]
        moving = [d for d in durations if d]
        if not (self.grid and all((d / self.grid).denominator == 1 for d in moving)):
            denominator = 1
            for d in moving:
                denominator = denominator * d.denominator // gcd(denominator, d.denominator)
            self.grid = Fraction(1, denominator)
            self.tokens.append(_grid_token(4 * denominator))
        points = [(ev.letter, ev.octave)] + list(ev.slide_points)
        parts = []
        for k, ((name, octave), duration) in enumerate(zip(points, durations)):
            count = int(duration / self.grid)
            last = k == len(points) - 1
            prefix = "" if (count == 0 and last) or (count == 1 and not last) else str(count)
            parts.append(prefix + self._note_name(name, octave))
        return ">".join(parts)

    def _lyrics(self, ev: Event) -> None:
        if ev.kind == "rest" or ev.grace or ev.kind == "percussion":
            return
        if ev.lyric is None:
            self.unsung = True
            return
        self.tokens.append(f'"{ev.lyric}"')
        for verse, syllable in sorted((ev.verses or {}).items()):
            self.tokens.append(f'"{verse}: {syllable}"')

    def sounding(self, ev: Event) -> None:
        if ev.kind == "rest":
            count = self._fit(_exact(ev.duration))
            self.tokens.append(f"{count if count > 1 else ''}r" + ("$fermata" if ev.decorations else ""))
            return
        if ev.lyric is not None and self.unsung:
            self.tokens.append('""')      # chiude le note senza sillaba: questa va alla sua nota
            self.unsung = False
        self._state(ev)
        duration = _exact(ev.duration)
        count = 1 if ev.grace else (self._fit(duration) if ev.kind != "slide" else 1)
        prefix = str(count) if count > 1 else ""
        if ev.kind == "note":
            body = prefix + self._note_name(ev.letter, ev.octave)
        elif ev.kind == "chord":
            body = prefix + self._chord(ev.symbol, ev.bass, ev.octave, ev.voicing)
        elif ev.kind == "block":
            body = prefix + "[" + " ".join(self._atom(i) for i in ev.items) + "]"
        elif ev.kind == "slide":
            body = self._slide(ev)
        else:
            body = prefix + ev.name
        body += _ARTICULATION_MARKS.get(ev.articulation, "")
        body += _GRACE_MARKS.get(ev.grace, "")
        body += "".join("$" + d for d in ev.decorations or ())
        body += {"start": "(", "stop": ")"}.get(ev.slur, "")
        self.tokens.append(body)
        self._lyrics(ev)

    def rest(self, duration: Fraction) -> None:
        count = self._fit(duration)
        self.tokens.append(f"{count if count > 1 else ''}r")


def _instant_text(ev: Event) -> str:
    """Un evento senza durata che non suona."""
    if ev.kind == "control":
        return f"{ev.name}={_number(ev.value)}"
    if ev.kind == "sustain":
        return "SON" if ev.name == "on" else "SOFF"
    if ev.kind == "tempo_marker":
        if ev.beat_unit:
            return f"tempo={_number(float(Fraction(ev.bpm) / note_value_beats(chr(39) + ev.beat_unit)))}'{ev.beat_unit}"
        return f"tempo={_number(ev.bpm)}"
    if ev.kind == "text":
        return f'$"{ev.name}"'
    if ev.kind == "harmony":
        return "$" + ev.symbol + (f"/{ev.bass}" if ev.bass else "")
    raise NotationError(tr("Evento che non si puo' scrivere in notazione: {kind}", kind=ev.kind), ev.kind)


def _lanes(events: List[Event]) -> List[List[Event]]:
    """Gli eventi che suonano divisi per voce; due eventi che si
    sovrappongono nella stessa voce vanno su due corsie."""
    lanes: List[list] = []                # [voce, fine, eventi]
    for ev in sorted((e for e in events if e.kind in _SOUNDING), key=lambda e: e.voice):
        start = _exact(ev.start)
        lane = next((lane for lane in lanes if lane[0] == ev.voice and lane[1] <= start), None)
        if lane is None:
            lane = [ev.voice, start, []]
            lanes.append(lane)
        lane[1] = start + _exact(ev.duration)
        lane[2].append(ev)
    return [lane[2] for lane in sorted(lanes, key=lambda lane: lane[0])]


def _sorted_events(events: List[Event]) -> List[Event]:
    return sorted(events, key=lambda e: _exact(e.start))


def events_to_text(events: List[Event], default_octave: int = 4, key: str = "", grid: Optional[float] = None,
                   velocity: Optional[int] = None) -> str:
    """Gli eventi come testo ST, dal quarto 0: rileggendolo si riottengono
    gli stessi eventi (le pause non conservano la velocity, che non suona).
    Piu' voci diventano un blocco { ; }. 'key' e' la tonalita' in vigore
    dove il testo verra' scritto (key= non si scrive: le alterazioni la
    seguono); 'grid' (in quarti) e 'velocity' quelle gia' in vigore, che non
    si riscrivono. Una durata che nessuna figura esprime si scrive come
    multiplo della griglia che la divide: non servono legature."""
    events = [ev for ev in events if ev.kind not in _SKIPPED]
    alters = key_signature_alters(key) if key else {}
    sorted_all = _sorted_events(events)
    lanes = [_sorted_events(lane) for lane in _lanes(sorted_all)] or [[]]
    boundaries = [{_exact(ev.start) for ev in lane} | {_exact(ev.start) + _exact(ev.duration) for ev in lane}
                  | {Fraction(0)} for lane in lanes]

    # gli eventi senza durata, e la fine delle rampe, vanno sulla prima
    # corsia che ha un confine in quel punto: non si puo' spezzare una nota
    instants: List[List[Tuple[Fraction, int, str]]] = [[] for _ in lanes]
    last_boundary = [max(found) for found in boundaries]
    all_lanes = list(range(len(lanes)))
    by_voice: Dict[int, List[int]] = {}
    for k, lane in enumerate(lanes):
        if lane:
            by_voice.setdefault(lane[0].voice, []).append(k)

    def place(moment: Fraction, order: int, text: str, voice: int) -> None:
        for k in by_voice.get(voice, []) + all_lanes:
            if moment in boundaries[k] or moment >= last_boundary[k]:
                instants[k].append((moment, order, text))
                return
        raise NotationError(tr("Evento che non si puo' scrivere in notazione: {kind}", kind=text), text)

    written = set()
    done = set()
    ramps = {(_exact(ev.start), ev.name): ev for ev in sorted_all if ev.kind == "control" and ev.duration}
    for order, ev in enumerate(sorted_all):
        if ev.kind in _SOUNDING:
            continue
        moment = _exact(ev.start)
        if id(ev) in done:
            continue                      # gia' scritta con il suo valore di partenza
        if ev.kind == "control" and ev.duration:
            curve = "" if ev.curve in (None, "lin") else ev.curve
            opening = f"{ev.name}={_number(ev.start_value)}"
            ramp = (">>" + curve) if (moment, opening) not in written else None
            place(moment, order, (f"{opening} {ramp}" if ramp else ">>" + curve), ev.voice)
            place(moment + _exact(ev.duration), order, f"{ev.name}={_number(ev.value)}", ev.voice)
            continue
        text = _instant_text(ev)
        following = ramps.get((moment, ev.name)) if ev.kind == "control" else None
        if following is not None and _number(following.start_value) == _number(ev.value):
            written.add((moment, text))
            curve = "" if following.curve in (None, "lin") else following.curve
            place(moment, order, f"{text} >>{curve}", ev.voice)
            place(moment + _exact(following.duration), order + 1, f"{ev.name}={_number(following.value)}", ev.voice)
            done.add(id(following))
            continue
        place(moment, order, text, ev.voice)

    texts = []
    for lane, moments in zip(lanes, instants):
        voice = _Voice(default_octave, alters, _exact(grid) if grid else None, velocity)
        cursor = Fraction(0)
        pending = sorted(moments, key=lambda item: (item[0], item[1]), reverse=True)
        for ev in lane:
            start = _exact(ev.start)
            while pending and pending[-1][0] <= start:
                moment, _order, text = pending.pop()
                if moment > cursor:
                    voice.rest(moment - cursor)
                    cursor = moment
                voice.tokens.append(text)
            if start > cursor:
                voice.rest(start - cursor)
            voice.sounding(ev)
            cursor = start + _exact(ev.duration)
        for moment, _order, text in reversed(pending):
            if moment > cursor:
                voice.rest(moment - cursor)
                cursor = moment
            voice.tokens.append(text)
        texts.append(" ".join(voice.tokens))
    return texts[0] if len(texts) == 1 else "{ " + " ; ".join(texts) + " }"


# ------------------------------------------------------------------ richiami per esteso

DEFAULT_STATE = {"grid": "4:", "velocity": "80@", "swing": "swing=50", "shift": "shift=0", "arp": "arp=off",
                 "transpose": "transpose=0"}
_KEY_MARK = "\x01"


class _Expander:
    def __init__(self, patterns: Dict[str, Pattern], default_octave: int, midi_dir: Optional[str], key: str):
        self.patterns, self.default_octave, self.midi_dir, self.key = patterns, default_octave, midi_dir, key

    def plain(self, text: str) -> str:
        """Il testo in ottave assolute e senza tonalita': rel: e key= finiscono
        cosi' dove devono. Un richiamo con funzioni ricorda la tonalita' del punto."""
        if not any(word in text for word in ("rel:", "key=")):
            return text
        rewriter = PitchRewriter(0, self.default_octave, to_relative=False, to_key="")
        rewriter.keep_reference_key = True
        return rewrite_tokens(text, rewriter)

    def _body(self, tokens: List[str], semitones: int) -> str:
        text = self.plain(" ".join(tokens))
        return rewrite_tokens(text, PitchRewriter(semitones, self.default_octave)) if semitones else text

    def transformed(self, tok: str, known: dict) -> str:
        from .transform import expand_reference
        tok, _, key = tok.partition(_KEY_MARK)
        prefix = " ".join(known[slot] for slot in _STATE_SLOTS)
        found = expand_reference(tok, self.patterns, self.default_octave, key=key or self.key, prefix=prefix)
        grid = grid_value_beats(known["grid"][:-1])
        velocity = None if known["velocity"][:-1].isalpha() else int(known["velocity"][:-1])
        return events_to_text(found.events, self.default_octave, grid=float(grid), velocity=velocity)

    def walk(self, text: str, known: dict, base: int = 0, nested: bool = False, close: bool = False,
             depth: int = 0) -> str:
        """Il testo con i richiami per esteso. 'known': il token in vigore per
        ogni stato; quello da rimettere dopo un pattern aspetta in 'pending'
        il primo token che lo usa. 'base': la trasposizione del richiamo."""
        out: List[str] = []
        pending: dict = {}
        pos = 0
        after_reference = False

        def flush(slots=tuple(DEFAULT_STATE)) -> None:
            ready = [slot for slot in DEFAULT_STATE if slot in slots and slot in pending]
            if ready:
                out.append(" ".join(pending[slot] for slot in ready) + " ")
            for slot in ready:
                known[slot] = pending.pop(slot)

        def inlined(body: str, entry: dict, inner_base: int) -> str:
            """Il corpo di una ripetizione: dopo, lo stato torna quello di 'entry'."""
            result = self.walk(body, known, inner_base, nested=True, depth=depth + 1)
            for slot, value in entry.items():
                if known[slot] != value:
                    pending[slot] = value
            return result

        for tok, start, end in tokenize_spans(text):
            out.append(text[pos:start])
            raw = new = text[start:end]
            pos = end
            slot = _state_slot(tok)
            ref = RE_PATTERN_REF.match(tok)
            midi = RE_MIDI_REF.match(tok)
            voices = RE_VOICES.match(raw)
            group = RE_REPEAT_GROUP.match(raw)
            transposed = RE_TRANSPOSE.match(tok)
            from .transform import is_transform_reference
            if slot:
                known[slot] = tok
                pending.pop(slot, None)
            elif transposed:
                new = known["transpose"] = f"transpose={base + int(transposed.group(1))}"
                pending.pop("transpose", None)
            elif tok == RESET_TOKEN:
                pending.clear()
                known.update(DEFAULT_STATE)
                if nested:      # dentro un pattern reset: non tocca la trasposizione che lo accompagna
                    known["transpose"] = f"transpose={base}"
                    new = " ".join(known[slot] for slot in DEFAULT_STATE)
            elif is_transform_reference(tok.partition(_KEY_MARK)[0]):
                flush()
                entry = dict(known)
                new = self.transformed(tok, known)
                self._follow(new, known)
                for slot_name, value in entry.items():
                    if known[slot_name] != value:
                        pending[slot_name] = value
            elif ref and ref.group(2) in self.patterns:
                flush()
                current = int(known["transpose"].partition("=")[2])
                semitones = int(ref.group(3) or 0)
                entry = dict(known)
                body = self._body(self.patterns[ref.group(2)].tokens, semitones)
                pieces = []
                for k in range(int(ref.group(1) or 1)):
                    if k:
                        for name in list(pending):
                            pieces.append(pending[name])
                            known[name] = pending.pop(name)
                    pieces.append(inlined(body, entry, current))
                new = " ".join(p for p in pieces if p)
            elif midi:
                flush()
                body = " ".join(_resolve_midi_ref(midi.group(2), self.midi_dir, tok))
                if midi.group(3):
                    body = rewrite_tokens(body, PitchRewriter(int(midi.group(3)), self.default_octave))
                pieces = [self.walk(body, known, base, nested, close=True, depth=depth + 1)
                          for _ in range(int(midi.group(1) or 1))]
                new = " ".join(pieces)
            elif voices:
                flush()
                new = "{" + ";".join(self.walk(voice, dict(known), base, nested, depth=depth + 1)
                                     for voice in split_voices(voices.group(1))) + "}"
            elif group:
                flush()
                new = self._group(group, known, base, nested, depth)
            elif _is_repeat_token(tok) or RE_NAVIGATION.match(tok):
                flush()
            elif RE_RAMP_UP.match(tok) or RE_RAMP_DOWN.match(tok):
                if after_reference:
                    flush(("velocity",))
            elif RE_TEMPO_SET.match(tok):
                flush(("velocity",))
            elif _is_rest(tok):
                flush(("grid",))
            elif not _is_stateless(tok):
                flush()
            out.append(new)
            after_reference = bool(ref)
        if close and pending:
            out.append(" " + " ".join(pending[slot] for slot in DEFAULT_STATE if slot in pending))
            for slot in list(pending):
                known[slot] = pending.pop(slot)
        out.append(text[pos:])
        return "".join(out)

    @staticmethod
    def _follow(text: str, known: dict) -> None:
        for tok in tokenize(text):
            slot = _state_slot(tok)
            if slot:
                known[slot] = tok

    def _group(self, group, known: dict, base: int, nested: bool, depth: int) -> str:
        """Un gruppo N( ): resta un gruppo se ogni ripetizione parte dallo
        stesso stato; altrimenti si scrive per esteso."""
        mult = int(group.group(1) or 1)
        trial = dict(known)
        inner = self.walk(group.group(2), trial, base, nested, close=True, depth=depth + 1)
        if mult < 2 or trial == known or "%" not in group.group(2):
            known.update(trial)
            return f"{group.group(1)}({inner})"
        pieces = []
        for _ in range(mult):
            pieces.append(self.walk(group.group(2), known, base, nested, close=True, depth=depth + 1))
        return " ".join(pieces)


def _sound(text: str, patterns: Dict[str, Pattern], default_octave: int, midi_dir: Optional[str]) -> list:
    """Quello che si sente: per ogni evento istante, durata, forza e altezze."""
    from .instruments import DEFAULT_INSTRUMENTS
    from .midi import _resolve_event_notes
    piano = DEFAULT_INSTRUMENTS["Piano"]
    sound = []
    events = parse_track_text(text, patterns, default_octave=default_octave, midi_dir=midi_dir)
    # il punto di partenza di una rampa e' la rampa stessa
    ramps = {(round(ev.start, 6), ev.name) for ev in events if ev.kind == "control" and ev.duration}
    for ev in events:
        moment = (round(ev.start, 6), round(ev.duration, 6))
        if ev.kind == "control" and not ev.duration and (moment[0], ev.name) in ramps:
            continue
        if ev.kind in ("note", "chord", "block", "percussion", "slide"):
            notes = tuple(_resolve_event_notes(ev, piano)[0])
            sound.append((moment, ev.kind, ev.velocity, notes, ev.swing, ev.shift, ev.articulation))
        elif ev.kind == "control" and (moment, ev.kind, ev.name, ev.value) not in sound:
            sound.append((moment, ev.kind, ev.name, ev.value))
        elif ev.kind == "tempo_marker":
            sound.append((moment, ev.kind, ev.bpm))
    return sorted(sound, key=repr)


def expand_to_text(text: str, patterns: Dict[str, Pattern], default_octave: int = 4, midi_dir: Optional[str] = None,
                   state: str = "", key: str = "") -> str:
    """Il testo con i richiami (%Nome, &"file", con o senza funzioni) scritti
    per esteso, senza segni interni, che suona come l'originale: dopo ogni
    pattern lo stato torna quello di prima, rel:, key= e transpose= finiscono
    con lui, e il testo diventa in ottave assolute se ne ha bisogno.

    'state': lo stato in vigore dove comincia il testo, come lo da'
    context_prefix_before; senza, quello iniziale (griglia di un quarto,
    velocity 80). 'key': la tonalita' del brano, per le funzioni sulla scala.
    Se il risultato non suonasse uguale solleva NotationError: il testo non
    cambia mai in silenzio."""
    parse_track_text(state + text, patterns, default_octave=default_octave, midi_dir=midi_dir)   # gli errori di sempre
    if "%" not in text and "&" not in text:
        return text
    expander = _Expander(patterns, default_octave, midi_dir, key)
    known = dict(DEFAULT_STATE)
    for tok in tokenize(state):
        slot = _state_slot(tok)
        if slot:
            known[slot] = tok
    result = expander.walk(expander.plain(text), known)
    if _sound(state + text, patterns, default_octave, midi_dir) != _sound(state + result, {}, default_octave, midi_dir):
        raise NotationError(tr("Questo testo non si puo' scrivere per esteso senza cambiarne il suono"), text[:40])
    return result.strip()
