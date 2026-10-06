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
# Con ST_LANGUAGE_INSTALLED=1 si usa la libreria installata (pip install
# st-language) e non quella della cartella del repository: serve a
# run_installed.py per provare il pacchetto pubblicato.
if not os.environ.get("ST_LANGUAGE_INSTALLED"):
    sys.path.insert(0, ROOT)

from st_language import Pattern, notation_warnings, parse_track_text, tokenize, validate_track_text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# (id, testo, opzioni) - opzioni: patterns {nome: corpo}, octave, time_sig, metrica_changes, pickup
CASES = [
    # --- altezze e durate
    ("notes-basic", "c d e f g a b", {}),
    ("notes-accidentals", "c# db d♭ d- eb b bb", {}),
    ("notes-octaves", "c*5 c*3 a*0 g*9 cb*4 b#*4", {}),
    ("notes-default-octave", "c e", {"octave": 2}),
    ("grid-and-multipliers", "8: c d 2e 16: f g 4: 3a r 2r", {}),
    ("grid-tuplets", "8T: c d e 16Q: c d e f g 8S: c d e f g a b 4: c", {}),
    ("note-values", "8: c'8. d'16 e'4 [c e g]'2 r'4 e'8T f'2.. g", {}),
    ("note-values-with-multiplier", "2c'8 3r'16 C'1", {}),
    ("articulations", "c! dx e_ C! Am7x Cmaj7_ C.drop2x C.hendrix C*3!", {}),
    # --- dinamiche, tempo, pedale
    ("velocity-and-dynamics", "100@ c 30@ d pp@ e mf@ f fff@ g", {}),
    ("velocity-ramp", "p@ >> c d e f ff@ g", {}),
    ("tempo-markers", "tempo=120 c d tempo=90 e", {}),
    ("tempo-ramp", "tempo=100 >> c d e tempo=140 f", {}),
    ("sustain", "SON c d SOFF e", {}),
    # --- automazioni, curve delle rampe, forcelle (1.1)
    ("automations-set", "vol=90 c expr=64 d pan=-0.5 mod=30 rev=40.4 cho=20 e", {}),
    ("automations-ramp", "vol=40 >> c d e vol=100 f", {}),
    ("automations-ramp-curve", "expr=20 >>exp 4c expr=127 pan=-1 <<s 2c pan=1", {}),
    ("automations-overlapping-ramps", "vol=50 >> pan=0 >> c d pan=1 e vol=120", {}),
    ("automations-ramp-same-position", "mod=10 >> mod=90 c", {}),
    ("automations-in-voices", "{ c vol=30 ; d d } expr=100 e<", {}),
    ("ramp-curves-velocity", "20@ >>exp c d e f 100@ tempo=60 >>log g a b tempo=120 c", {}),
    ("hairpins", "2c< d> e'2< [c e g]> 4: C7!< c>e<", {}),
    # --- legature, swing, ccN e bend (2.1)
    ("ties", "4: 2c 2d~ | 2d 2e | c#~ db C7~ C7 [c e]~ | [e c] c~ 100@ c~ c", {}),
    ("ties-with-values", "c'2~ c'8 r'8 e'4.~ e'8", {}),
    ("slurs", "c( d r e f) [c e]( d~ d) C( G7)", {}),
    ("slurs-in-groups", "2(c( d) e)", {}),
    ("swing", "swing=66 8: c d e f swing16=60 16: g a b c swing=50 8: d e", {}),
    ("swing-in-voices", "swing=62 { 8: c d ; 4e } f", {}),
    # --- ottave relative e tonalita' (2.3)
    ("relative-octaves", "rel: c d e f g a b c c*- g c*+ b*-- d*6 e", {}),
    ("relative-blocks-slides-chords", "rel: [e g c] d c>e>g c C7 a", {}),
    ("relative-voices-and-repeats", "rel: e { g a ; c b*- } f |: g a b c :| d 2(c*- d) e", {}),
    ("relative-default-octave", "rel: g b d", {"octave": 3}),
    ("relative-patterns-are-absolute", "rel: g*- %R a", {"patterns": {"R": "c e"}}),
    ("key-accidentals", "key=G f g f# fn f♮ C key=Bb b e a key=Ebm a key=off b", {}),
    ("key-with-relative", "key=D rel: d e f g a b c d", {}),
    ("key-in-blocks-and-slides", "key=F [b d f] b>c", {}),
    # --- micro-tempo e accordatura (2.4)
    ("shift-moves-the-following-notes", "c shift=-20 d kick [c e] shift=15 e shift=0 f", {}),
    ("shift-in-voices-and-ties", "shift=10 { c~ c ; 2e } shift=-5 C7", {}),
    ("tune-automation-and-ramp", "tune=-30 c tune=-30 >>exp 2d tune=50 e", {}),
    # --- ritornelli, segni, indicazioni di testo (2.2)
    ("repeats", "4: |: c d e f :| g a b c |", {}),
    ("repeats-from-start", "4: c d e f :| g", {}),
    ("repeats-endings", "4: |: c d e f |1. g a b c :| |2. 4g || 4c", {}),
    ("repeats-three-endings", "4: |: 4c |1. 4d :|2. 4e :|3. 4f", {}),
    ("repeats-in-voices", "{ 4: |: c d e f :| ; 8e }", {}),
    ("marks", "c$accent d$marcato$tenuto e$fermata f$tr g$mordent a$turn r$fermata [c e]$accent C7$tr", {}),
    ("marks-with-tie-and-value", "c'2$accent~ c'4$fermata", {}),
    ("text-indications", '$"dolce" c d $"rit." e f', {}),
    ("bar-checks-at-start", "4: | c d e f | |: g a b c :|", {}),
    ("automations-cc-and-bend", "cc74=20 >>exp 2c cc74=100 bend=-2 c bend=0.5 >> d bend=0", {}),
    ("hairpins-follow-expression", "expr=100 2c< vol=60 >> d< e vol=90", {}),
    # --- accordi, blocchi, percussioni
    ("chords", "C Am7 G7 Cmaj7 F#m7b5 Bb Ebdim7 Dsus4 E5 C°", {}),
    ("chords-octave-voicing-bass", "C*3 Cmaj7.drop2 G7/B C/E*3 C7*3", {}),
    ("blocks", "[c e g] 2[c*3 g*3] [kick snare] [C e*5]", {}),
    ("percussion", "kick snare hihat hihat_open crash ride 2kick", {}),
    ("slides", "c*4>d*4 2c*4>d*4>c*4 c*4>2d*4 8: c*4>d*4", {}),
    ("slides-hold-and-chains", "2c*4>3d*4 c*4>d*4>c*4 2c*4>2d*4>3c*4 c*4>0d*4", {}),
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
    ("error-ramp-mixed", "p@ >> c tempo=120 d", {}),
    ("error-undefined-pattern", "%Nope", {}),
    ("error-bar-check-in-block", "[c | e]", {}),
    ("error-semicolon-outside-voices", "c ; d", {}),
    ("error-automation-range", "vol=128 c", {}),
    ("error-pan-range", "pan=-1.5 c", {}),
    ("error-automation-ramp-not-closed", "vol=40 >> c d", {}),
    ("error-automation-ramp-in-voice-not-closed", "{ vol=40 >> c ; d } vol=90", {}),
    ("error-hairpin-on-rest", "c r<", {}),
    ("error-hairpin-in-expression-ramp", "expr=40 >> c< expr=120", {}),
    ("error-unknown-curve", "p@ >>quad c f@", {}),
    ("error-old-slash-octave", "c/4 d", {}),
    ("error-old-chord-octave", "C7/3", {}),
    ("error-old-tempo", "120§ c", {}),
    ("error-tempo-range", "tempo=0 c", {}),
    ("error-slide-zero-duration", "0c*4>d*4", {}),
    ("error-tie-different-note", "c~ d", {}),
    ("error-tie-to-rest", "c~ r", {}),
    ("error-tie-not-continued", "c d~", {}),
    ("error-tie-on-percussion", "kick~ kick", {}),
    ("error-tie-across-voices", "c~ { c ; e }", {}),
    ("error-slur-not-closed", "c( d e", {}),
    ("error-slur-not-opened", "c d)", {}),
    ("error-slur-nested", "c( d( e) f)", {}),
    ("error-slur-single-note", "c() d", {}),
    ("error-slur-on-rest", "r( c d)", {}),
    ("error-swing-range", "swing=90 c", {}),
    ("error-transpose-range", "transpose=61 c", {}),
    ("error-transpose-decimals", "transpose=1.5 c", {}),
    ("error-transpose-pattern-range", "%A+99", {"patterns": {"A": "c"}}),
    ("error-transpose-out-of-midi", "c*9 transpose=12 c*5 transpose=60 c*8", {}),
    ("error-pattern-slash-suffix", "%A/3", {"patterns": {"A": "c"}}),
    ("error-anchor-zero", "bar=0 c", {}),
    ("error-anchor-decimals", "bar=1.5 c", {}),
    ("error-anchor-too-large", "bar=100000 c", {}),
    ("error-anchor-after-tie", "c~ bar=2 c", {}),
    ("error-shift-range", "shift=600 c", {}),
    ("error-shift-decimals", "shift=1.5 c", {}),
    ("error-tune-range", "tune=-101 c", {}),
    ("error-cc-number", "cc121=10 c", {}),
    ("error-bend-range", "bend=30 c", {}),
    ("error-repeat-not-closed", "|: c d", {}),
    ("error-repeat-nested", "|: c |: d :| :|", {}),
    ("error-repeat-ending-number", "c |2. d", {}),
    ("error-repeat-single-ending", "|: c |1. d ||", {}),
    ("error-repeat-ending-sequence", "|: c |1. d :| e", {}),
    ("error-unknown-mark", "c$wobble", {}),
    ("error-octave-mark-not-relative", "c*+ d", {}),
    ("error-key-invalid", "key=H c", {}),
    ("error-key-too-many-accidentals", "key=G# c", {}),
    ("error-relative-out-of-range", "rel: c*9 a*+", {}),
    ("error-mark-on-rest", "r$accent", {}),
    # --- ancore di battuta (2.5)
    ("anchor-pads-with-silence", "4: c d e f bar=3 g", {}),
    ("anchor-on-the-spot", "4: c d e f bar=2 g", {}),
    ("anchor-at-the-start", "bar=3 4: c", {}),
    ("anchor-time-signature", "4: bar=3 c", {"time_sig": "3/4"}),
    ("anchor-meter-changes", "4: bar=4 c",
     {"metrica_changes": [[1, "4/4"], [3, "3/4"]]}),
    ("anchor-in-patterns", "%A bar=3 %A", {"patterns": {"A": "4: c d"}}),
    ("anchor-in-voices", "4: c { d e ; bar=2 f }", {}),
    ("anchor-keeps-velocity-and-grid", "8: 90@ c bar=2 d", {}),
    # --- trasposizione (2.5)
    ("transpose-notes", "c d transpose=2 c d transpose=0 c transpose=-1 c e", {}),
    ("transpose-octaves", "transpose=12 c*4 transpose=-12 c*4 e", {}),
    ("transpose-chords", "C7 transpose=5 C7/E transpose=12 Cm/Eb*3 transpose=-7 Cm7/Bb Db/F", {}),
    ("transpose-chord-across-c", "B transpose=1 B", {}),
    ("transpose-key-sharps", "key=G f g transpose=2 f g", {}),
    ("transpose-key-flats", "key=Eb e a transpose=2 e a b", {}),
    ("transpose-key-minor", "key=Dm b a transpose=-3 b a", {}),
    ("transpose-without-key", "eb db*5 transpose=2 eb db*5 transpose=1 c", {}),
    ("transpose-relative", "rel: g a b transpose=2 g a b", {}),
    ("transpose-slides-and-blocks", "transpose=3 c>e*5 [c e g]'2 { c ; e }", {}),
    ("transpose-percussion-untouched", "transpose=5 kick r snare c", {}),
    ("transpose-pattern-suffix", "%T %T+7 %T-5 2%T+2", {"patterns": {"T": "4: c e g"}}),
    ("transpose-pattern-inherits", "transpose=3 %T %T+4", {"patterns": {"T": "4: c e g"}}),
    ("transpose-pattern-nested", "%U+1", {"patterns": {"T": "4: c e g", "U": "%T+2 c"}}),
    ("transpose-set-inside-pattern", "%A %B %A+2", {"patterns": {"A": "transpose=5 c d", "B": "c"}}),
    # --- reset: (2.6)
    ("reset-restores-state", "8: 100@ rel: key=G transpose=2 swing=60 shift=20 c f reset: c f", {}),
    ("reset-keeps-automations", "vol=40 pan=0.5 c reset: d", {}),
    ("reset-keeps-call-transposition", "%P+2", {"patterns": {"P": "transpose=5 c reset: c"}}),
    ("reset-in-voices", "8: 90@ { c reset: c ; d } e", {}),
    ("error-reset-in-ramp", "60@ >> c reset: d 90@", {}),
    ("error-ramp-after-reset", "reset: >> c", {}),
    # --- riferimenti MIDI fra virgolette (2.6): senza libreria sono errori
    ("error-midi-ref-without-quotes", "c &Riff d", {}),
    ("error-midi-ref-unclosed-quote", 'c &"Riff d', {}),
    # --- battuta in levare (2.6)
    ("pickup-bar-checks", "4: g | c e g | c 2r |", {"time_sig": "3/4", "pickup": 1}),
    ("pickup-anchor", "4: g bar=2 c", {"time_sig": "3/4", "pickup": 1}),
    ("pickup-meter-changes", "8: g a | 4: c d e | c d | bar=4 e",
     {"metrica_changes": [[1, "3/4"], [2, "2/4"]], "pickup": 1}),
    ("warning-pickup-bar", "4: g a | c e g |", {"time_sig": "3/4", "pickup": 1}),
    # --- avvisi (il testo e' valido)
    ("warning-bar-missing", "4: c d e | f g a b |", {}),
    ("warning-bar-extra", "8: c d e f g a b c d | e", {}),
    ("warning-no-cascade", "4: c d e | f g a b | c d e f |", {}),
    ("warning-time-signature", "4: c d e f | g a b |", {"time_sig": "3/4"}),
    ("warning-meter-changes", "4: c d e f | g a b | c d e f g | a b c d |",
     {"metrica_changes": [[1, "4/4"], [2, "3/4"], [3, "5/4"]]}),
    ("warning-voices", "4: { c d e | f ; 2c 2d | } |", {}),
    ("warning-extra-syllables", 'c d "a b c"', {}),
    ("warning-anchor-past", "4: c d e f g a b c bar=2 d", {}),
    ("warning-anchor-past-in-pattern", "%B %B", {"patterns": {"B": "4: c d e f bar=2 g"}}),
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
    from st_language import Meter
    pickup = options.get("pickup", 0)
    meter = Meter(options.get("time_sig", "4/4"), [tuple(c) for c in options.get("metrica_changes", [])], pickup)
    ok, _message = validate_track_text(text, patterns, default_octave=octave, meter=meter)
    if not ok:
        return {"error": True}
    events = [event_json(e) for e in parse_track_text(text, patterns, default_octave=octave, meter=meter)]
    warnings = [{"start": w.char_start, "end": w.char_end, "bar": w.bar}
                for w in notation_warnings(text, patterns, options.get("time_sig", "4/4"),
                                           [tuple(c) for c in options.get("metrica_changes", [])],
                                           default_octave=octave, pickup=pickup)]
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
        json.dump({"spec_version": "2.6", "cases": cases}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(cases)} casi")


if __name__ == "__main__":
    main()
