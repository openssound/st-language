"""
Rigenera cases.json, la suite di conformita' di ST-language, dagli input
qui sotto e dall'implementazione di riferimento (la libreria st_language).

    python3 docs/spec/conformance/make_cases.py

Va rilanciato solo quando il linguaggio cambia di proposito: i test
(tests/test_st_language.py) controllano che l'implementazione dia ancora
esattamente questi risultati. Formato dei casi: vedi README.md accanto.
"""

import json
import os
import sys
from dataclasses import asdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)

from st_language import Pattern, notation_warnings, parse_track_text, tokenize, validate_track_text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# (id, testo, opzioni) - opzioni: patterns {nome: corpo}, octave, time_sig, metrica_changes
CASES = [
    # --- altezze e durate
    ("notes-basic", "c d e f g a b", {}),
    ("notes-accidentals", "c# db d♭ d- eb b bb", {}),
    ("notes-octaves", "c*5 c/3 a*0 g*9 cb*4 b#*4", {}),
    ("notes-default-octave", "c e", {"octave": 2}),
    ("grid-and-multipliers", "8: c d 2e 16: f g 4: 3a r 2r", {}),
    ("grid-tuplets", "8T: c d e 16Q: c d e f g 8S: c d e f g a b 4: c", {}),
    ("note-values", "8: c'8. d'16 e'4 [c e g]'2 r'4 e'8T f'2.. g", {}),
    ("note-values-with-multiplier", "2c'8 3r'16 C'1", {}),
    ("articulations", "c! dx e_ C! Am7x Cmaj7_ C.drop2x C.hendrix C*3!", {}),
    # --- dinamiche, tempo, pedale
    ("velocity-and-dynamics", "100@ c 30@ d pp@ e mf@ f fff@ g", {}),
    ("velocity-ramp", "p@ >> c d e f ff@ g", {}),
    ("tempo-markers", "120§ c d 90§ e", {}),
    ("tempo-ramp", "100§ >> c d e 140§ f", {}),
    ("sustain", "SON c d SOFF e", {}),
    # --- accordi, blocchi, percussioni
    ("chords", "C Am7 G7 Cmaj7 F#m7b5 Bb Ebdim7 Dsus4 E5 C°", {}),
    ("chords-octave-voicing-bass", "C*3 Cmaj7.drop2 G7/B C/E*3 C7/3", {}),
    ("blocks", "[c e g] 2[c*3 g*3] [kick snare] [C e*5]", {}),
    ("percussion", "kick snare hihat hihat_open crash ride 2kick", {}),
    ("slides", "c*4>d*4 2c*4>d*4>c*4 c*4>2d*4 8: c*4>d*4", {}),
    # --- struttura
    ("repeat-groups", "2(c d) 3(e) 2(f 2(g))", {}),
    ("patterns", "%Riff 2%Riff c", {"patterns": {"Riff": "8: c d"}}),
    ("voices", "4: { 8: c d e f ; 2g*3 } a", {}),
    ("voices-state-is-local", "8: 100@ { c 4: 30@ d ; e } f", {}),
    ("voices-nested", "{ c ; { d ; e } ; f }", {}),
    ("lyrics", '4: c d e 2f "Ma- ri- a, sei" g a "_ la"', {}),
    ("lyrics-skip-and-attached", 'c r kick d"uno" e f "* due"', {}),
    ("lyrics-first-voice", '{ c d ; 2e } f "la la la"', {}),
    ("bar-checks-take-no-time", "c d|e | f", {}),
    ("comments", "c d // e f\ng // a\n// b", {}),
    # --- errori (nessun evento)
    ("error-unclosed-block", "c [d e", {}),
    ("error-unclosed-group", "2(c d", {}),
    ("error-unclosed-voices", "{ c ; d", {}),
    ("error-empty-voices", "{ ; }", {}),
    ("error-unclosed-lyric", 'c "la la', {}),
    ("error-unknown-token", "c H d", {}),
    ("error-unknown-percussion", "kick bonk", {}),
    ("error-unknown-chord-quality", "Cxyz", {}),
    ("error-unknown-voicing", "C.wide", {}),
    ("error-velocity-range", "128@ c", {}),
    ("error-note-out-of-range", "a*9", {}),
    ("error-bad-note-value", "c'3", {}),
    ("error-ramp-without-anchor", ">> c", {}),
    ("error-ramp-not-closed", "p@ >> c d", {}),
    ("error-ramp-mixed", "p@ >> c 120§ d", {}),
    ("error-undefined-pattern", "%Nope", {}),
    ("error-bar-check-in-block", "[c | e]", {}),
    ("error-semicolon-outside-voices", "c ; d", {}),
    # --- avvisi (il testo e' valido)
    ("warning-bar-missing", "4: c d e | f g a b |", {}),
    ("warning-bar-extra", "8: c d e f g a b c d | e", {}),
    ("warning-no-cascade", "4: c d e | f g a b | c d e f |", {}),
    ("warning-time-signature", "4: c d e f | g a b |", {"time_sig": "3/4"}),
    ("warning-meter-changes", "4: c d e f | g a b | c d e f g | a b c d |",
     {"metrica_changes": [[1, "4/4"], [2, "3/4"], [3, "5/4"]]}),
    ("warning-voices", "4: { c d e | f ; 2c 2d | } |", {}),
    ("warning-extra-syllables", 'c d "a b c"', {}),
]


def _round(value):
    if isinstance(value, float):
        return round(value, 9)
    if isinstance(value, list):
        return [_round(v) for v in value]
    if isinstance(value, tuple):
        return [_round(v) for v in value]
    if isinstance(value, dict):
        return {k: _round(v) for k, v in value.items()}
    return value


def event_json(ev) -> dict:
    """Un evento nella forma della suite: i campi non vuoti; voice solo se
    diversa da 1; items dei blocchi senza 'mult'."""
    out = {}
    for key, value in asdict(ev).items():
        if value is None or (key == "voice" and value == 1):
            continue
        if key == "items":
            value = [{k: v for k, v in item.items() if v is not None and k != "mult"} for item in value]
        out[key] = _round(value)
    return out


def run_case(text: str, options: dict) -> dict:
    patterns = {name: Pattern(name, tokenize(body)) for name, body in options.get("patterns", {}).items()}
    octave = options.get("octave", 4)
    ok, _message = validate_track_text(text, patterns, default_octave=octave)
    if not ok:
        return {"error": True}
    events = [event_json(e) for e in parse_track_text(text, patterns, default_octave=octave)]
    warnings = [{"start": w.char_start, "end": w.char_end, "bar": w.bar}
                for w in notation_warnings(text, patterns, options.get("time_sig", "4/4"),
                                           [tuple(c) for c in options.get("metrica_changes", [])],
                                           default_octave=octave)]
    result = {"events": events}
    if warnings:
        result["warnings"] = warnings
    return result


def main():
    cases = []
    for case_id, text, options in CASES:
        case = {"id": case_id, "input": text}
        case.update(options)
        case["expect"] = run_case(text, options)
        cases.append(case)
    with open(os.path.join(HERE, "cases.json"), "w", encoding="utf-8") as f:
        json.dump({"spec_version": "1.0", "cases": cases}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(cases)} casi")


if __name__ == "__main__":
    main()
