"""
La libreria st_language da sola: suite di conformita' della specifica,
indipendenza da SoundText e da pacchetti esterni, lettore dei file .st,
comandi da terminale, pacchetto per PyPI, messaggi tradotti.
(I test che confrontano la libreria con SoundText stanno nel repository
di SoundText.)
"""

import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pytest

import st_language as st

SPEC = os.path.join(ROOT, "docs", "spec")


# ------------------------------------------------------------------ conformita'

def _cases():
    with open(os.path.join(SPEC, "conformance", "cases.json"), encoding="utf-8") as f:
        return json.load(f)["cases"]


def _run_case():
    sys.path.insert(0, os.path.join(SPEC, "conformance"))
    from make_cases import run_case
    return run_case


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c["id"])
def test_conformance_suite(case):
    options = {k: v for k, v in case.items() if k not in ("id", "input", "expect")}
    assert _run_case()(case["input"], options) == case["expect"]


def test_suite_covers_every_part_of_the_language():
    ids = {c["id"] for c in _cases()}
    for prefix in ("notes", "grid", "note-values", "velocity", "tempo", "chords", "blocks", "slides",
                   "repeat-groups", "patterns", "voices", "lyrics", "bar-checks", "comments",
                   "automations", "ramp-curves", "hairpins", "ties", "slurs", "swing", "repeats", "marks",
                   "text-indications", "relative-", "key-", "shift-", "tune-", "anchor-", "transpose-",
                   "error-", "warning-"):
        assert any(i.startswith(prefix) for i in ids), prefix


def test_spec_documents_exist_in_both_languages():
    for name in ("ST-language.md", "ST-language.it.md"):
        text = open(os.path.join(SPEC, name), encoding="utf-8").read()
        assert "CC BY 4.0" in text and "conformance/cases.json" in text


# ------------------------------------------------------------------ indipendenza

def _isolated_copy(tmp_path):
    """Solo la cartella st_language, lontano dal repository."""
    dest = tmp_path / "solo"
    shutil.copytree(os.path.join(ROOT, "st_language"), dest / "st_language",
                    ignore=shutil.ignore_patterns("__pycache__"))
    return dest


def _run(args, cwd, stdin=None):
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "SOUNDTEXT_LANGUAGE")}
    env["ST_LANGUAGE"] = "en"
    return subprocess.run([sys.executable, *args], cwd=cwd, input=stdin, capture_output=True,
                          text=True, env=env, timeout=120)


def test_library_works_without_soundtext_and_without_dependencies(tmp_path):
    cwd = _isolated_copy(tmp_path)
    script = (
        "import sys, st_language as st\n"
        "ev = st.parse('4: { c d ; 2e } C7\\'2 \"la la\"')\n"
        "song = st.Song(name='x'); song.add_track('Basso', 'Bass', '4: c*2 g*1')\n"
        "st.to_midi(song, 'x.mid'); st.to_musicxml(song, 'x.musicxml')\n"
        "bad = [m for m in sys.modules if m.split('.')[0] in ('core', 'gui', 'PySide6', 'mido', 'numpy')]\n"
        "print(len(ev), bad, st.validate('c [d')[1])\n")
    out = _run(["-c", script], cwd)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "4 [] Block '[' not closed (token: '[d')"
    assert (cwd / "x.mid").read_bytes()[:4] == b"MThd"


def test_cli_in_isolation(tmp_path):
    cwd = _isolated_copy(tmp_path)
    (cwd / "melodia.txt").write_text('4: c d e | f g a b |\n"la la la la"\n', encoding="utf-8")
    out = _run(["-m", "st_language", "check", "melodia.txt"], cwd)
    assert out.returncode == 0
    assert "Piano:1:10: warning: bar 1: 1 quarter note missing" in out.stdout
    out = _run(["-m", "st_language", "check", "-", "--lang", "it"], cwd, stdin="c [d")
    assert out.returncode == 1 and "errore" in out.stdout
    out = _run(["-m", "st_language", "midi", "melodia.txt", "--instrument", "Trumpet", "-o", "m.mid"], cwd)
    assert out.returncode == 0 and (cwd / "m.mid").exists()
    out = _run(["-m", "st_language", "events", "-"], cwd, stdin="4: c d")
    assert [e["letter"] for e in json.loads(out.stdout)[0]["events"]] == ["c", "d"]
    out = _run(["-m", "st_language", "abc", "melodia.txt"], cwd)
    assert out.returncode == 0 and (cwd / "melodia.abc").read_text(encoding="utf-8").startswith("X:1\n")
    out = _run(["-m", "st_language", "midi", "-", "-o", "bad.mid"], cwd, stdin="c [d")
    assert out.returncode == 1 and not (cwd / "bad.mid").exists()


def test_song_from_code_and_boxes():
    song = st.read_song('Tempo: 90 BPM\n\nTraccia Voce [Trumpet]:\n  4: c d\n\n'
                        'Box Voce "A" |4:\n  4: e f // fine\n\nMixer Voce:\n  mute: si\n')
    voce = song.get_track("Voce")
    assert voce.mute and song.audible_tracks() == []
    assert [e.start for e in voce.parsed_events(song.patterns) if e.kind == "note"] == [4.0, 5.0]


def test_box_after_a_tuplet_box_starts_exactly_where_it_is():
    """2.8: il vuoto prima di un box si riempie con una pausa esatta quando
    non e' un multiplo di un sedicesimo. Con l'arrotondamento ai sedicesimi
    il box dopo un box in terzina slittava di 1/12 di quarto (1/10 dopo
    una quintina), e lo scarto si sommava box dopo box."""
    from st_language.song import flatten_clips_to_text
    for first in ("8T: c d e f", "8T: c d e f g", "16Q: c d e"):
        clips = [st.Clip("A", first, 0.0), st.Clip("B", "4: g*6", 4.0), st.Clip("C", first, 8.0),
                 st.Clip("D", "4: a*6", 12.0)]
        text = flatten_clips_to_text(clips, {}, 4)
        starts = {e.letter: e.start for e in st.parse(text) if e.kind == "note" and e.octave == 6}
        assert starts == {"g": pytest.approx(4.0), "a": pytest.approx(12.0)}
    # un vuoto multiplo di un sedicesimo resta scritto come prima
    text = flatten_clips_to_text([st.Clip("A", "c", 2.5)], {}, 4)
    assert text == "16: 10r reset: c"


def test_tempo_header_with_decimals():
    """2.9: 'Tempo:' coi decimali, anche per battuta; un valore intero resta int."""
    from st_language.timing import build_tempo_beat_map, seconds_for_beats
    song = st.read_song("ST: 2.9\nTempo: 101.4 BPM\n\nPiano:\n  c\n")
    assert song.tempo_bpm == 101.4
    song = st.read_song("Tempo: 1: 96.5, 3: 98\n\nPiano:\n  c\n")
    assert song.tempo_changes == [(1, 96.5), (3, 98)] and song.tempo_bpm == 96.5
    assert type(song.tempo_changes[1][1]) is int
    assert type(st.read_song("Tempo: 96.0 BPM\n").tempo_bpm) is int
    # 4 battute a 101,4 BPM
    song = st.read_song("Tempo: 101.4 BPM\n\nPiano:\n  1: c c c c\n")
    beat_map = build_tempo_beat_map(song)
    assert beat_map == [(0.0, 101.4)]
    assert seconds_for_beats(beat_map, 16) == pytest.approx(9.467, abs=1e-3)
    # un file 2.8 si legge come prima
    song = st.read_song("ST: 2.8\nTempo: 1: 120, 5: 140\n\nPiano:\n  c\n")
    assert song.tempo_changes == [(1, 120), (5, 140)] and type(song.tempo_bpm) is int


def test_decimal_tempo_survives_fermatas_in_midi(tmp_path):
    from st_language.timing import with_fermatas
    assert with_fermatas([(0.0, 101.4)], [(4.0, 6.0)]) == [(0.0, 101.4), (4.0, 50.7), (6.0, 101.4)]
    assert with_fermatas([(0.0, 101)], [(4.0, 6.0)]) == [(0.0, 101), (4.0, 50), (6.0, 101)]
    song = st.read_song("Tempo: 101.4 BPM\n\nPiano:\n  4: c d$fermata e f\n")
    assert os.path.exists(st.to_midi(song, str(tmp_path / "t.mid")))


def test_bar_starts_and_bar_at_beat():
    from st_language.timing import bar_at_beat, bar_starts, compute_bar_beat_offsets
    song = st.Song()
    assert bar_starts(song, 10)[:4] == [0, 4, 8, 12] and bar_starts(song, 10)[-1] > 10
    song = st.Song(metrica_changes=[(1, "4/4"), (3, "3/4")])
    assert bar_starts(song, 12)[:5] == [0, 4, 8, 11, 14]
    song = st.Song(pickup=1.0)
    assert bar_starts(song, 6)[:3] == [1, 5, 9]
    assert bar_at_beat(song, 0.5) == 0 and bar_at_beat(song, 1) == 1 and bar_at_beat(song, 4.99) == 1

    song = st.Song(metrica_changes=[(1, "4/4"), (3, "3/4"), (7, "6/8"), (11, "5/4")])
    starts = bar_starts(song, 1000)
    assert bar_at_beat(song, 8.0, starts) == 3          # inizio di battuta
    assert bar_at_beat(song, 9.5, starts) == 3          # a meta'
    assert bar_at_beat(song, 10.999, starts) == 3       # appena prima della successiva
    assert bar_at_beat(song, 10.9, starts, nearest=True) == 4
    assert bar_at_beat(song, 9.5, starts, nearest=True) == 3      # a pari distanza quella prima
    assert bar_at_beat(song, 2000) == bar_at_beat(song, 2000, starts)   # starts troppo corto: si ricalcola
    for pickup in (0.0, 1.5):
        song.pickup = pickup
        starts = bar_starts(song, 1000)
        offsets = compute_bar_beat_offsets([(200, 120)], song.metrica_changes, song.time_sig, pickup)
        assert all(starts[bar - 1] == pytest.approx(offsets[bar]) for bar in range(2, 201))
        assert all(bar_at_beat(song, starts[k] + 0.01, starts) == k + 1 for k in range(200))


_CONVERSION_BLOCK = 'Conversione Voce (note):\n  da="Voce" modo=melodia griglia=8 forza=80 finestra=100 swing=66'
_CONVERSION_SONG = f'''ST: 2.10
Tempo: 96 BPM

Traccia Voce [Audio]:
  ingresso=voce

Traccia Voce (note) [Trumpet]:

{_CONVERSION_BLOCK}

Audio Voce "Strofa" |8:
  file="audio/voce-1.wav"

Box Voce (note) "Strofa" |8:
  16: e g a b
'''


def test_conversion_block_is_read():
    """2.10: 'Conversione Nome:' ricorda da quale traccia audio viene una traccia di note."""
    song = st.read_song(_CONVERSION_SONG)
    note = song.get_track("Voce (note)")
    assert note.conversion["from"] == "Voce" and note.conversion["grid"] == 8
    assert note.conversion["strength"] == pytest.approx(0.8) and note.conversion["swing"] == pytest.approx(0.66)
    assert note.conversion["mode"] == "melody" and note.conversion["triplets"] is False
    assert song.get_track("Voce").conversion is None and song.file_warnings == []
    assert [e.letter for e in note.parsed_events(song.patterns) if e.kind == "note"] == ["e", "g", "a", "b"]
    # senza il blocco il resto del brano e' lo stesso
    without = st.read_song(_CONVERSION_SONG.replace(_CONVERSION_BLOCK + "\n\n", ""))
    assert without.get_track("Voce (note)").conversion is None
    assert [(t.name, t.text) for t in without.tracks] == [(t.name, t.text) for t in song.tracks]


def test_conversion_body_round_trip_and_aliases():
    from st_language.stfile import CONVERSION_DEFAULTS, conversion_body_text, parse_conversion_body
    conversion, problems = parse_conversion_body('from="Voce 2" mode=chords grid=16 triplets strength=75 '
                                                 'window=40 swing=60 min_note=30 merge=12.5 sevenths voice futuro=3')
    assert problems == []
    assert conversion == {"from": "Voce 2", "mode": "chords", "grid": 16, "triplets": True, "strength": 0.75,
                          "window": 0.4, "swing": 0.6, "min_note_sec": 0.03, "merge_gap_sec": 0.0125,
                          "sevenths": True, "voice": True}
    text = conversion_body_text(conversion)
    assert text == ('da="Voce 2" modo=accordi terzine forza=75 finestra=40 swing=60 nota_minima=30 '
                    'unisci=12.5 settime voce')
    assert parse_conversion_body(text) == (conversion, [])
    # solo da= quando tutto e' predefinito
    assert conversion_body_text(dict(CONVERSION_DEFAULTS, **{"from": "Voce"})) == 'da="Voce"'
    assert parse_conversion_body('da="Voce"')[0] == dict(CONVERSION_DEFAULTS, **{"from": "Voce"})


def test_conversion_invalid_values_warn_and_use_the_default():
    from st_language.stfile import parse_conversion_body
    conversion, problems = parse_conversion_body('da="Voce" griglia=12 modo=jazz forza=120 swing=40 '
                                                 'nota_minima=-5 terzine=si')
    assert conversion["grid"] == 16 and conversion["mode"] == "melody" and conversion["strength"] == 1.0
    assert conversion["swing"] == 0.5 and conversion["min_note_sec"] == 0.0 and conversion["triplets"] is True
    assert len(problems) == 5 and "griglia=12" in problems[0]
    conversion, problems = parse_conversion_body('da="Voce" griglia=32 terzine')
    assert conversion["triplets"] is False and len(problems) == 1

    song = st.read_song(_CONVERSION_SONG.replace("griglia=8", "griglia=12"))
    assert song.get_track("Voce (note)").conversion["grid"] == 16
    assert [line for line, _ in song.file_warnings] == [9]


@pytest.mark.parametrize("block", [
    'Conversione Nessuna:\n  da="Voce"',                   # la traccia non esiste
    'Conversione Voce:\n  da="Voce"',                      # e' una traccia audio
    'Conversione Voce (note):\n  modo=accordi',            # manca da
    'Conversione Voce (note):\n  da="Altra"',              # da non esiste
    'Conversione Voce (note):\n  da="Voce (note)"',        # da non e' audio
])
def test_conversion_block_that_cannot_be_used_is_ignored_with_a_warning(block):
    text = _CONVERSION_SONG.replace(_CONVERSION_BLOCK, block)
    song = st.read_song(text)
    assert song.get_track("Voce (note)").conversion is None
    assert [line for line, _ in song.file_warnings] == [9]


def test_conversion_second_block_and_check_command(tmp_path):
    text = _CONVERSION_SONG + '\nConversion Voce (note):\n  from="Voce" mode=drums\n'
    song = st.read_song(text)
    assert song.get_track("Voce (note)").conversion["mode"] == "melody"
    assert [line for line, _ in song.file_warnings] == [18]
    cwd = _isolated_copy(tmp_path)
    (cwd / "brano.st").write_text(text.replace("griglia=8", "griglia=12"), encoding="utf-8")
    out = _run(["-m", "st_language", "check", "brano.st", "--lang", "it"], cwd)
    assert out.returncode == 0
    assert "brano.st:9: avviso: Conversione Voce (note): griglia=12 non valido" in out.stdout
    assert "brano.st:18: avviso:" in out.stdout and "nessun errore" in out.stdout


def test_conversion_header_is_unknown_to_older_readers():
    """Un lettore 2.9 non riconosce l'intestazione: e' una riga fuori da ogni
    blocco, e il corpo che segue una riga vuota si ignora."""
    from st_language import stfile
    line = "Conversione Voce (note):"
    assert [rx for rx in stfile._TRACK_HDR_PATTERNS if rx.match(line)] == [stfile.RE_CONVERSION_HDR]
    assert stfile.LANGUAGE_VERSION >= (2, 10)


@pytest.mark.parametrize("name, program", [
    ("Flauto", 73), ("Violoncello", 42), ("Flûte", 73), ("Chitarra", 25), ("Basso", 33), ("Contrebasse", 43),
    ("Violonchelo", 42), ("Trompeta", 56), ("Chœur", 52), ("Orgue d'église", 19), ("Flûte à bec", 74),
    ("Sassofono", 65), ("Cor", 60),
    # 2.11.1
    ("Clavicembalo", 6), ("Clavecín", 6), ("Cembalo", 6), ("Pianoforte_elettrico", 4), ("Carillon", 10),
    ("Campane_tubolari", 14), ("Hammond", 16), ("Bandoneón", 23), ("Basso_fretless", 35), ("Pizzicato", 45),
    ("Sax_soprano", 64), ("Sax_baritono", 67), ("Corno_inglese", 69), ("Cor_anglais", 69),
    ("Tromba_con_sordina", 59), ("Flauto_di_Pan", 75), ("Flûte_de_Pan", 75), ("Cornamusa", 109), ("Gaita", 109),
])
def test_instrument_names_in_italian_french_and_spanish(name, program):
    """2.11: i nomi degli strumenti in italiano, francese e spagnolo, anche con gli accenti."""
    from st_language.instruments import instrument_for
    profile = instrument_for(name)
    assert profile.gm_program == program and profile.resolved and not profile.is_percussion


def test_drum_names_and_english_names_as_before():
    from st_language.instruments import instrument_for
    for name in ("Batteria", "Batería", "Percussions", "drum_kit"):
        assert instrument_for(name).is_percussion
    # i nomi inglesi danno lo stesso programma di prima ('Alto' resta il sax contralto)
    before = {"Alto": 65, "sax": 65, "violin": 40, "muted": 28, "steel": 25, "String": 44, "strings": 48,
              "Horn": 60, "Synth": 38, "Marimba": 12, "Piccolo": 72, "Choir": 52, "Alto Sax": 65}
    assert {name: instrument_for(name).gm_program for name in before} == before
    # i nomi General MIDI con le parentesi ora si riconoscono
    assert instrument_for("Acoustic Guitar (nylon)").gm_program == 24


def test_unknown_instrument_warns_with_a_suggestion(tmp_path):
    from st_language.instruments import instrument_for, suggest_instrument
    for name in ("Xyzzy", "Pan", "Tom"):              # niente corrispondenze parziali sotto i 4 caratteri
        profile = instrument_for(name)
        assert profile.gm_program == 0 and profile.resolved is False
    assert instrument_for("Piano").resolved and suggest_instrument("Flautoo") == "flauto"
    assert suggest_instrument("Xyzzy") is None
    from st_language.instruments import unknown_instrument_message
    assert unknown_instrument_message("Flautoo").endswith("«flauto»?")
    text = "Traccia Melodia [Flautoo]:\n  c d e\n\nTraccia Voci [Coro]:\n  c\n\nTraccia X [Xyzzy]:\n  c\n"
    song = st.read_song(text)
    assert [line for line, _ in song.file_warnings] == [1, 7]
    assert "«flauto»" in song.file_warnings[0][1] and "«" not in song.file_warnings[1][1].split(":", 1)[1]
    cwd = _isolated_copy(tmp_path)
    (cwd / "brano.st").write_text(text, encoding="utf-8")
    out = _run(["-m", "st_language", "check", "brano.st", "--lang", "it"], cwd)
    assert out.returncode == 0
    assert ("brano.st:1: avviso: «Flautoo» non e' uno strumento noto: suona come pianoforte. "
            "Forse intendevi «flauto»?") in out.stdout


def test_examples_have_known_instruments():
    for name in os.listdir(os.path.join(ROOT, "examples")):
        song = st.load_song(os.path.join(ROOT, "examples", name))
        assert song.file_warnings == [] and all(t.instrument.resolved for t in song.tracks)


def _notes(text, patterns):
    song = st.Song()
    for name, body in patterns.items():
        song.add_pattern(name, body)
    return [(e.letter, e.start, e.duration, e.velocity, bool(e.swing), e.shift)
            for e in st.parse(text, song.patterns) if e.kind == "note"]


def test_what_a_pattern_writes_ends_with_it():
    """2.12: griglia, velocity, swing e spostamento di un pattern finiscono con lui."""
    assert _notes("60@ %A c", {"A": "8: 100@ swing=66 shift=5 e"}) == [
        ("e", 0.0, 0.5, 100, True, 5), ("c", 0.5, 1.0, 60, False, None)]
    # a ogni ripetizione, e il pattern eredita lo stato del punto in cui e' richiamato
    assert [n[2] for n in _notes("3%A", {"A": "c 8: d"})] == [1.0, 0.5] * 3
    assert _notes("8: 100@ %A", {"A": "c"}) == [("c", 0.0, 0.5, 100, False, None)]
    # un pattern dentro un pattern
    assert [n[2] for n in _notes("%A c", {"A": "%B d", "B": "8: e"})] == [0.5, 1.0, 1.0]


def _as_before(body, patterns):
    """Il brano di una traccia e questi pattern, in un file senza versione."""
    blocks = "".join(f"Pattern %{name}:\n  {text}\n\n" for name, text in patterns.items())
    song = st.read_song(f"{blocks}Traccia T [Piano]:\n  {body}\n")
    track = song.get_track("T")
    return track.text, [(e.letter, e.start, e.duration, e.velocity) for e in track.parsed_events(song.patterns)
                        if e.kind == "note"]


@pytest.mark.parametrize("body, patterns, text, durations", [
    ("%A c", {"A": "8: 100@ d"}, "%A 8: 100@ c", [0.5, 0.5]),
    ("%A | c", {"A": "8: d"}, "%A | 8: c", [0.5, 0.5]),
    ("8: %A c", {"A": "8: d"}, "8: %A c", [0.5, 0.5]),                 # lo stato era gia' quello
    ("%A %A", {"A": "8: d"}, "%A %A", [0.5, 0.5]),                     # il pattern lo riscrive da se'
    ("%A", {"A": "8: d"}, "%A", [0.5]),                                # il testo finisce
    ("3%A", {"A": "c 8: d"}, "%A 8: 2%A", [1.0, 0.5, 0.5, 0.5, 0.5, 0.5]),
    ("2%A+2", {"A": "c 8: d"}, "%A+2 8: %A+2", [1.0, 0.5, 0.5, 0.5]),
    ("%A c // fine", {"A": "8: d"}, "%A 8: c // fine", [0.5, 0.5]),
    ("2( %A c )", {"A": "8: d"}, "2( %A 8: c )", [0.5, 0.5, 0.5, 0.5]),
    ("|: %A :| c", {"A": "8: d"}, "|: %A 8: :| c", [0.5, 0.5, 0.5]),
    ("{ %A c ; e }", {"A": "8: d"}, "{ %A 8: c ; e }", [0.5, 0.5, 1.0]),
    ("%A { c ; e }", {"A": "8: d"}, "%A 8: { c ; e }", [0.5, 0.5, 0.5]),
    ("%A >> c 100@ d", {"A": "60@ e"}, "%A 60@ >> c 100@ d", [1.0, 1.0, 1.0]),
    ("%A tempo=60 >> c tempo=80 d", {"A": "60@ e"}, "%A 60@ tempo=60 >> c tempo=80 d", [1.0, 1.0, 1.0]),
    ("%A 2r c", {"A": "8: 60@ d"}, "%A 8: 2r 60@ c", [0.5, 0.5]),      # una pausa usa solo la griglia
    ("%S c", {"S": "swing=66 8:"}, "%S 8: swing=66 c", [0.5]),         # un pattern di sole impostazioni
    ("%A c", {"A": "reset: d", "B": "c"}, "%A 4: 80@ swing=50 shift=0 c", [1.0, 1.0]),
])
def test_a_file_before_2_12_keeps_its_sound(body, patterns, text, durations):
    written, notes = _as_before(body, patterns)
    assert written == text and [n[2] for n in notes] == durations


def test_upgrade_pattern_state_for_a_new_pattern():
    """Trasforma in pattern: il pezzo spostato portava via anche arp=, e
    va riscritto solo il richiamo del pattern nuovo."""
    from st_language.notation import upgrade_pattern_state
    new = {"N": st.Pattern("N", st.tokenize("8: 100@ arp=up c"))}
    assert upgrade_pattern_state("%Altro %N C", new) == "%Altro %N 8: 100@ arp=up C"
    assert upgrade_pattern_state("%N", new) == "%N"


def test_nested_patterns_are_upgraded_too():
    assert [n[2] for n in _as_before("%A", {"A": "%B c", "B": "8: d"})[1]] == [0.5, 0.5]
    assert [n[2] for n in _as_before("%A c", {"A": "%B", "B": "8: d"})[1]] == [0.5, 0.5]


def test_upgrade_song_text():
    old = 'ST: 2.7\n\nPattern %A:\n  8: 100@ d\n\nTraccia T [Piano]:\n\nTraccia U [Piano]:\n  %A c // resta\n'
    new = st.upgrade_song_text(old)
    assert new == old.replace("ST: 2.7", "ST: 2.12").replace("%A c", "%A 8: 100@ c")
    assert st.upgrade_song_text(new) == new
    assert st.read_song(new).st_version == (2, 12)
    # un file che dichiara la 2.12 segue gia' la regola nuova
    assert st.read_song("ST: 2.12\n\nPattern %A:\n  8: d\n\nPiano:\n  %A c\n").tracks[0].text == "%A c"
    assert st.upgrade_song_text("Piano:\n  c\n") == "ST: 2.12\nPiano:\n  c\n"
    # il testo gia' riscritto, letto come vecchio, non cambia piu'
    assert st.read_song(new.replace("ST: 2.12", "ST: 2.11")).get_track("U").text == "%A 8: 100@ c // resta"


def test_upgrade_keeps_blocks_and_warnings_lines():
    text = ('Traccia Vuota [Flautoo]:\n\nBox Vuota "B" |0:\n  %A c\n\n'
            'Pattern %A:\n  8: d\n\nTraccia Audio1 [Audio]:\n  ingresso=voce\n\nTraccia X [Xyzzy]:\n  %A\n')
    song = st.read_song(text)
    assert [line for line, _ in song.file_warnings] == [1, 12]
    assert song.get_track("Vuota").clips[0].text == "%A 8: c"


def test_upgrade_command(tmp_path):
    cwd = _isolated_copy(tmp_path)
    old = "Pattern %A:\n  8: d\n\nTraccia T [Piano]:\n  %A c\n"
    (cwd / "brano.st").write_text(old, encoding="utf-8")
    out = _run(["-m", "st_language", "upgrade", "brano.st"], cwd)
    assert out.returncode == 0 and "brano.st" in out.stdout
    assert (cwd / "brano.st.bak").read_text(encoding="utf-8") == old
    assert (cwd / "brano.st").read_text(encoding="utf-8").startswith("ST: 2.12\n")
    assert "%A 8: c" in (cwd / "brano.st").read_text(encoding="utf-8")
    out = _run(["-m", "st_language", "upgrade", "brano.st"], cwd)
    assert out.returncode == 0 and "already up to date" in out.stdout


_TRANSFORM_PATTERNS = {
    "Tema": "4: c*4 e*4 g*4", "Scala": "key=C 4: c*4 e*4 g*4 c*5", "Ritmo": "c*4'8 d*4'8 e*4'4 g*4'2",
    "Motivo": "key=C 8: c*5 d*5 e*5 c*5", "Giro": "key=C 4: 2C 2G", "Forte": "100@ 4: c*4 d*4 e*4 c*4",
    "Fuori": "key=C c#*4 f*4", "Sol": "key=G f*4 g*4", "Accordi": "key=C Cmaj7 G7 C/E", "Alieno": "key=Am E7",
    "Blocco": "key=C [c*4 e*4] d*4", "Vuoto": "r", "Slide": "c*4>d*4", "Vol": "vol=40 c", "Tempo": "tempo=90 c",
    "Bar": "bar=2 c", "Dc": "c $dc", "Mista": "4: c*4 kick r e*4",
}


def _song_with(patterns=_TRANSFORM_PATTERNS):
    song = st.Song()
    for name, body in patterns.items():
        song.add_pattern(name, body)
    return song


def _pitched(text, song=None):
    song = song or _song_with()
    out = []
    for ev in st.parse(text, song.patterns):
        if ev.kind == "note":
            out.append(f"{ev.letter}*{ev.octave}")
        elif ev.kind == "chord":
            out.append(ev.symbol + (f"/{ev.bass}" if ev.bass else ""))
    return " ".join(out)


@pytest.mark.parametrize("text, expected", [
    ("%Tema.octave(-1)", "c*3 e*3 g*3"),
    ("%Tema.ottava(1)", "c*5 e*5 g*5"),
    ("%Tema.OCTAVE(1)", "c*5 e*5 g*5"),
    ("%Tema.invert", "c*4 g#*3 f*3"),
    ("%Tema.invert(e*4)", "g#*4 e*4 c#*4"),
    ("%Tema.inverti(e)", "g#*4 e*4 c#*4"),
    ("%Tema.invert.invert", "c*4 e*4 g*4"),
    ("%Scala.step(2)", "e*4 g*4 b*4 e*5"),
    ("%Scala.grado(-1)", "b*3 d*4 f*4 b*4"),
    ("%Scala.step(7)", "c*5 e*5 g*5 c*6"),
    ("%Fuori.step(1)", "d#*4 g*4"),
    ("%Sol.step(1)", "g*4 a*4"),
    ("%Giro.step(1)", "Dm Am"),
    ("%Accordi.step(1)", "Dm7 Am7 Dm/F"),
    ("%Alieno.step(1)", "F7"),
    ("%Blocco.step(1)", "e*4"),
    ("%Motivo.sequence(3,-1)", "c*5 d*5 e*5 c*5 b*4 c*5 d*5 b*4 a*4 b*4 c*5 a*4"),
    ("%Motivo.progressione(1,5)", "c*5 d*5 e*5 c*5"),
    ("%Giro.sequence(2,1)", "C G Dm Am"),
    ("%Ritmo.retro", "g*4 e*4 d*4 c*4"),
    ("%Ritmo.retrogrado.retro", "c*4 d*4 e*4 g*4"),
    ("%Tema.octave(1)+2", "d*5 f#*5 a*5"),
    ("%Tema+2.octave(1)", "d*5 f#*5 a*5"),
    ("2%Tema.retro", "g*4 e*4 c*4 g*4 e*4 c*4"),
])
def test_transforms_change_the_pitches_as_specified(text, expected):
    assert _pitched(text) == expected


def test_transforms_durations_and_state():
    song = _song_with()

    def durations(text):
        return [e.duration for e in st.parse(text, song.patterns) if e.kind == "note"]

    assert durations("%Ritmo.augment(2)") == [1, 1, 2, 4]
    assert durations("%Ritmo.aumenta(1.5)") == [0.75, 0.75, 1.5, 3]
    assert durations("%Ritmo.diminish(2)") == [0.25, 0.25, 0.5, 1]
    assert durations("%Ritmo.augment(2).diminuisci(2)") == durations("%Ritmo")
    assert durations("%Ritmo.retro") == [2, 1, 0.5, 0.5]
    # il cursore segue la durata del risultato, e lo stato resta quello di prima
    ev = [e for e in st.parse("60@ 8: %Ritmo.augment(2) %Tema.retro c", song.patterns) if e.kind == "note"]
    assert ev[4].start == 8 and ev[-1].start == 11 and ev[-1].duration == 0.5 and ev[-1].velocity == 60
    assert [(e.kind, e.start) for e in st.parse("%Mista.retro", song.patterns)] == [
        ("note", 0.0), ("rest", 1.0), ("percussion", 2.0), ("note", 3.0)]
    assert {e.velocity for e in st.parse("%Forte.vel(-30)", song.patterns)} == {70}
    assert {e.velocity for e in st.parse("%Forte.vel(p)", song.patterns)} == {49}
    assert {e.velocity for e in st.parse("%Forte.vel(+40)", song.patterns)} == {127}
    assert {e.velocity for e in st.parse("%Forte.vel(90)", song.patterns)} == {90}


def test_retro_keeps_slurs_and_grace_notes():
    song = _song_with({"L": "c( d e) f", "G": "d'g c e"})
    assert [(e.letter, e.slur) for e in st.parse("%L.retro", song.patterns)] == [
        ("f", None), ("e", "start"), ("d", "continue"), ("c", "stop")]
    assert [(e.letter, e.grace, e.start) for e in st.parse("%G.retro", song.patterns)] == [
        ("e", None, 0.0), ("d", "acciaccatura", 1.0), ("c", None, 1.0)]


def test_transforms_use_the_key_of_the_song():
    def notes(text):
        song = st.read_song(f"ST: 2.12\n{text}\n\nPattern %M:\n  c d\n\nTraccia T [Piano]:\n  %M.step(1) %M.step(1)\n")
        return [e.letter for e in song.tracks[0].parsed_events(song.patterns, meter=song.meter())
                if e.kind == "note"]

    assert notes("Tonalita: G") == ["d", "e", "d", "e"]
    assert notes("Tonalita: D") == ["db", "e", "db", "e"]       # c e' fuori scala: resta alterata
    assert notes("Tonalita: Eb") == ["d", "eb", "d", "eb"]
    # il key= del punto del richiamo viene prima della tonalita' del brano
    assert _pitched("key=A %M.step(1)", _song_with({"M": "c# d"})) == "d*4 e*4"
    assert _pitched("key=Bb %M.step(2)", _song_with({"M": "c d"})) == "eb*4 f*4"
    # la trasposizione nella catena sposta anche la scala: si resta nella tonalita'
    assert _pitched("key=C %M+2.step(1)", _song_with({"M": "c e"})) == "e*4 g*4"
    assert _pitched("%M+2.step(1)", _song_with({"M": "c e"})) == "e*4 g*4"


@pytest.mark.parametrize("text, message", [
    ("%Tema.invertt", ".invertt non esiste: forse .invert?"),
    ("%Tema.xyzzyq", ".xyzzyq non esiste"),
    ("%Nessuno.retro", "non definito"),
    ("%Tema.sequence(3, -1)", "Niente spazi"),
    ("%Tema.octave", ".octave: manca n"),
    ("%Tema.octave(1,2)", "troppi argomenti"),
    ("%Tema.octave(1.5)", "numero intero"),
    ("%Tema.augment(0)", "maggiore di 0"),
    ("%Tema.invert(h)", "deve essere una nota"),
    ("%Tema.vel(200)", "dinamica"),
    ("%Tema.sequence(0,1)", "da 1 in su"),
    ("%Tema.octave(9)", "estensione MIDI"),
    ("%Giro.invert", "non si puo' invertire"),
    ("%Vuoto.invert", "indica l'asse"),
    ("%Ritmo.diminish(32)", "'128"),
    ("%Slide.retro", "slide"),
    ("%Vol.retro", "Automazioni"),
    ("%Tempo.retro", "tempo="),
    ("%Tempo.augment(2)", "tempo="),
    ("%Bar.octave(1)", "bar=N"),
    ("%Dc.octave(1)", "navigazione"),
    ("C.retro", "solo sui pattern"),
    ("c~ %Tema.retro", "legatura"),
])
def test_transform_errors(text, message):
    st.set_language("it")
    try:
        ok, error = st.validate(text, _song_with().patterns)
    finally:
        st.set_language(None)
    assert not ok and message in error


def test_transforms_warnings():
    st.set_language("it")
    try:
        song = _song_with({"M": "c d", "V": "100@ c 60@ d", "L": 'c "la"', "A": "key=Am E7"})
        messages = {t: [w.message for w in st.check(t, song.patterns)]
                    for t in ("%M.step(1)", "%V.vel(80)", "%L.retro", "%A.step(1)", "%M.retro")}
    finally:
        st.set_language(None)
    assert "Do maggiore" in messages["%M.step(1)"][0]
    assert "velocity" in messages["%V.vel(80)"][0]
    assert "al contrario" in messages["%L.retro"][0]
    assert "E7" in messages["%A.step(1)"][0]
    assert messages["%M.retro"] == []
    assert st.check("%M.step(1)", song.patterns) and not [
        w for w in st.check("key=C %M.step(1)", song.patterns)]


def test_transforms_properties():
    import random
    from fractions import Fraction
    from st_language.chords import pitch_to_midi
    from st_language.transform import TRANSFORMS, duration_after, parse_reference
    rng = random.Random(12)

    def sound(text, song):
        return sorted((e.start, e.duration, pitch_to_midi(e.letter, e.octave) if e.letter else 0, e.velocity, e.kind)
                      for e in st.parse(text, song.patterns) if e.kind in ("note", "rest"))

    for _ in range(60):
        notes = [rng.choice("cdefgab") + rng.choice(["", "#"] if _ % 2 else [""]) + f"*{rng.randint(3, 6)}"
                 + rng.choice(["'8", "'4", "'4.", "'2", "'8T"]) for _ in range(rng.randint(1, 8))]
        body = "key=C " + " ".join(notes)
        song = _song_with({"P": body, "Q": f"key=C {rng.choice(['8:', '4:'])} 90@ {body}"})
        same = sound("%P", song)
        assert sound("%P.retro.retro", song) == same
        assert sound("%P.invert(c*4).invert(c*4)", song) == same
        assert sound("%P.augment(2).diminish(2)", song) == same
        assert sound("%P.augment(1.5).diminish(1.5)", song) == same
        assert sound("%P.octave(1)", song) == sound("%P+12", song)
        assert sound("%P.sequence(1,3)", song) == same
        assert sound("%P.sequence(3,0)", song) == sound("3%P", song)
        assert sound("%P.step(2).step(-2)", song) == same
        assert sound("%P.step(7)", song) == sound("%P.octave(1)", song)
        assert sound("%P.sequence(2,1)", song) == sound("%P %P.step(1)", song)
        assert sound("%Q.vel(+7).vel(-7)", song) == sound("%Q", song)
        # la durata dichiarata dal registro e' quella del risultato
        for chain in ("%P.augment(1.5)", "%P.diminish(2)", "%P.sequence(3,1)", "%P.retro", "%P.vel(10)"):
            step = parse_reference(chain).steps[0]
            events = st.parse("%P", song.patterns)
            length = Fraction(max(e.start + e.duration for e in events)).limit_denominator(10 ** 6)
            after = st.parse(chain, song.patterns)
            assert float(duration_after(step, length)) == pytest.approx(max(e.start + e.duration for e in after))
    assert set(TRANSFORMS) == {"octave", "invert", "step", "augment", "diminish", "retro", "sequence", "vel",
                               "canon", "thirds", "arpeggio"}


def test_transforms_syntax_next_to_other_tokens():
    song = _song_with()
    assert _pitched("%Tema+5", song) == "f*4 a*4 c*5"
    assert _pitched("c( d e) 2( %Tema.octave(1) ) { %Tema.retro ; c } e", song).startswith("c*4 d*4 e*4 c*5")
    assert _pitched("Cmaj7.drop2", song) == "Cmaj7"
    # un richiamo dentro un pattern, e una trasformazione del risultato
    nested = _song_with({"A": "c*4 d*4", "B": "%A.octave(1) e*4"})
    assert _pitched("%B.retro", nested) == "e*4 d*5 c*5"
    # niente tracce della tonalita' negli eventi
    assert all(e.key is None for e in st.parse("%Scala.step(1)", song.patterns))
    # la trasposizione del testo va in fondo alla catena
    assert st.transpose_tokens(["%Tema.invert(e*5)"], 2, 4) == ["%Tema.invert(e*5)+2"]
    assert st.transpose_tokens(["3%Tema.retro+2"], -2, 4) == ["3%Tema.retro"]


def test_transforms_reach_the_exports(tmp_path):
    song = st.read_song("ST: 2.12\nTonalita: C\n\nPattern %T:\n  c e g\n\nTraccia A [Piano]:\n  %T.step(1).retro\n")
    assert os.path.exists(st.to_midi(song, str(tmp_path / "t.mid")))
    assert os.path.exists(st.to_musicxml(song, str(tmp_path / "t.musicxml")))
    assert os.path.exists(st.to_abc(song, str(tmp_path / "t.abc")))
    assert "a" in (tmp_path / "t.abc").read_text(encoding="utf-8").lower()


def test_transforms_api_for_soundtext():
    from st_language.transform import format_reference, list_transforms, parse_reference
    reference = parse_reference("3%Tema.inverti(e*5).RETRO+5.vel(+10)")
    assert (reference.pattern, reference.mult) == ("Tema", 3)
    assert [s.name for s in reference.steps] == ["invert", "retro", "transpose", "vel"]
    assert reference.steps[0].start == len("3%Tema") and reference.steps[0].end == len("3%Tema.inverti(e*5)")
    assert format_reference(reference) == "3%Tema.invert(e*5).retro+5.vel(+10)"
    assert format_reference(reference, italian=True) == "3%Tema.inverti(e*5).retrogrado+5.vel(+10)"
    assert format_reference(parse_reference("%T.augment(1.5)")) == "%T.augment(1.5)"
    names = {t["name"]: t for t in list_transforms()}
    assert names["sequence"]["alias"] == "progressione" and names["invert"]["arguments"][0]["required"] is False


def test_expand_reference_for_the_preview():
    from st_language.transform import describe_transform, expand_reference
    song = _song_with()

    def letters(events):
        return [e.letter for e in events if e.kind == "note"]

    found = expand_reference("%Tema.invert(e*4).retro+2", song.patterns)
    assert letters(found.events) == [e.letter for e in st.parse("%Tema.invert(e*4).retro+2", song.patterns)]
    assert found.duration == 3 and found.warnings == []
    assert [step.name if step else None for step, _ in found.stages] == [None, "invert", "retro", "transpose"]
    assert letters(found.stages[0][1]) == ["c", "e", "g"]
    assert letters(found.stages[1][1]) == ["g#", "e", "c#"]
    assert letters(found.stages[2][1]) == ["c#", "e", "g#"]
    # le ripetizioni, un richiamo senza funzioni, la griglia del punto del richiamo
    repeated = expand_reference("2%Tema.retro", song.patterns)
    assert [e.start for e in repeated.events] == [0, 1, 2, 3, 4, 5] and repeated.duration == 6
    assert expand_reference("%Tema", song.patterns).stages[0][0] is None
    plain = _song_with({"M": "c d"})
    assert expand_reference("%M", plain.patterns, grid=0.5, velocity=100).events[1].start == 0.5
    assert expand_reference("%M", plain.patterns, velocity=100).events[0].velocity == 100
    # la tonalita': quella del punto, poi quella del brano, poi l'avviso
    assert letters(expand_reference("%M.step(1)", plain.patterns, key="Eb").events) == ["d", "eb"]
    meter = st.Meter(key="Eb", key_changes=[(1, "Eb"), (3, "G")])
    assert letters(expand_reference("%M.step(1)", plain.patterns, meter=meter).events) == ["d", "eb"]
    assert letters(expand_reference("%M.step(1)", plain.patterns, meter=meter, position=8).events) == ["d", "e"]
    assert expand_reference("%M.step(1)", plain.patterns).warnings
    assert all(e.key is None for _, stage in found.stages for e in stage) and all(e.key is None for e in found.events)
    with pytest.raises(st.NotationError):
        expand_reference("%Nessuno.retro", song.patterns)
    info = describe_transform(".progressione")
    assert info["name"] == "sequence" and info["signature"] == ".sequence(n,passo)" and info["example"]
    assert describe_transform("retro")["signature"] == ".retro"
    with pytest.raises(st.NotationError):
        describe_transform("xyzzy")


def _voices_of(text, song):
    by_voice = {}
    for ev in st.parse(text, song.patterns):
        name = ({"rest": "r"}.get(ev.kind) or (f"{ev.letter}*{ev.octave}" if ev.letter else ev.symbol or ev.name))
        by_voice.setdefault(ev.voice, []).append((name, ev.start, ev.duration))
    return by_voice


def test_canon():
    song = _song_with({"T": "4: c*4 d*4 e*4 c*4", "K": "4: kick snare", "C": "4: C G"})
    voices = _voices_of("%T.canon('2,12)", song)
    assert [n for n, _s, _d in voices[1]] == ["c*4", "d*4", "e*4", "c*4"]
    assert voices[2] == [("r", 0.0, 2.0), ("c*5", 2.0, 1.0), ("d*5", 3.0, 1.0), ("e*5", 4.0, 1.0), ("c*5", 5.0, 1.0)]
    voices = _voices_of("%T.canone('4,7,3)", song)
    assert [n for n, _s, _d in voices[2]] == ["r", "g*4", "a*4", "b*4", "g*4"]
    assert [n for n, _s, _d in voices[3]] == ["r", "d*5", "e*5", "f#*5", "d*5"]
    assert voices[3][0] == ("r", 0.0, 2.0)
    assert [n for n, _s, _d in _voices_of("%T.canon('1)", song)[2]][1:] == ["c*4", "d*4", "e*4", "c*4"]
    # il cursore va avanti della durata del canone, e le durate con il punto e le terzine valgono
    assert st.parse("%T.canon('2,12) f", song.patterns)[-1].start == 6
    assert st.parse("%T.canon('4.) f", song.patterns)[-1].start == 5.5
    assert st.parse("%T.canon('8T) f", song.patterns)[-1].start == pytest.approx(4 + 1 / 3)
    # percussioni solo all'unisono, accordi trasposti come con +N
    assert [n for n, _s, _d in _voices_of("%K.canon('4)", song)[2]] == ["r", "kick", "snare"]
    assert [n for n, _s, _d in _voices_of("%C.canon('4,2)", song)[2]] == ["r", "D", "A"]
    # la velocity si puo' cambiare dopo, su tutte le voci
    assert {e.velocity for e in st.parse("%T.canon('2,12).vel(-10)", song.patterns) if e.kind == "note"} == {70}


def test_thirds():
    song = _song_with({"M": "key=C 4: e*5 f*5 g*5 e*5", "G": "key=G 4: b*4 c*5 d*5 b*4", "F": "key=C c#*5 r",
                       "S": "key=C e*5>g*5", "L": 'key=C e*5 "la"'})
    voices = _voices_of("%M.thirds", song)
    assert [n for n, _s, _d in voices[1]] == ["e*5", "f*5", "g*5", "e*5"]
    assert [n for n, _s, _d in voices[2]] == ["c*5", "d*5", "e*5", "c*5"]
    assert [n for n, _s, _d in _voices_of("%G.terze", song)[2]] == ["g*4", "a*4", "b*4", "g*4"]
    assert [n for n, _s, _d in _voices_of("%F.thirds", song)[2]] == ["a#*4", "r"]
    second = [e for e in st.parse("%S.thirds", song.patterns) if e.voice == 2][0]
    assert (second.letter, second.slide_points) == ("c", [("e", 5)])
    assert [e.lyric for e in st.parse("%L.thirds", song.patterns) if e.kind == "note"] == ["la", None]


def test_functions_after_a_result_with_more_voices():
    song = _song_with({"T": "key=C 4: c*4 d*4 e*4 c*4"})

    def notes(text, voice):
        return [n for n, _s, _d in _voices_of(text, song)[voice] if n != "r"]

    assert notes("%T.canon('2,12).octave(-1)", 2) == ["c*4", "d*4", "e*4", "c*4"]
    assert notes("%T.thirds.step(1)", 2) == ["b*3", "c*4", "d*4", "b*3"]
    assert notes("%T.thirds+2", 2) == ["b*3", "c#*4", "d*4", "b*3"]
    # senza asse ogni voce si inverte intorno alla sua prima nota
    assert notes("%T.thirds.invert", 2) == ["a*3", "g*3", "f#*3", "a*3"]
    # .retro rovescia il blocco intero: la voce che entrava dopo finisce prima
    voices = _voices_of("%T.canon('2).retro", song)
    assert voices[1][0] == ("r", 0.0, 2.0) and voices[1][1][0] == "c*4"
    assert voices[2][0][:2] == ("c*4", 0.0) and voices[2][-1][0] == "r"
    assert [e.start for e in st.parse("%T.canon('2).augment(2)", song.patterns)
            if e.voice == 2 and e.kind == "note"] == [4, 6, 8, 10]
    assert st.parse("%T.canon('2).sequence(2,1) f", song.patterns)[-1].start == 12
    for text in ("%T.canon('2).canon('2)", "%T.thirds.thirds", "%T.canon('2).thirds", "%T.thirds.canon('2)"):
        ok, error = st.validate(text, song.patterns)
        assert not ok and "voice" in error or "voce" in error


@pytest.mark.parametrize("text, message", [
    ("%T.canon", "manca ritardo"),
    ("%T.canon(2)", "durata"),
    ("%T.canon('3)", "Valore di nota"),
    ("%T.canon('2,x)", "numero intero"),
    ("%T.canon('2,12,5)", "da 2 a 4"),
    ("%T.canon('2,12,1)", "da 2 a 4"),
    ("%T.canon('2,0,2,1)", "troppi argomenti"),
    ("%K.canon('2,12)", "percussioni"),
    ("%V.canon('2)", "una voce sola"),
    ("%V.thirds", "una voce sola"),
    ("%C.thirds", "melodie"),
    ("%B.thirds", "melodie"),
    ("%K.thirds", "melodie"),
    ("%Tempo.canon('2)", "tempo="),
    ("%T.canon('2,120,2)", "fuori range"),
    ("%A.canon('2,60)", "estensione MIDI"),
    ("C.canon('2)", "solo sui pattern"),
    ("c.octave(1)", "solo sui pattern"),
])
def test_canon_and_thirds_errors(text, message):
    song = _song_with({"T": "c*4 d*4", "K": "kick", "V": "{ c ; e }", "C": "C", "B": "[c e]", "Tempo": "tempo=90 c",
                       "A": "c*6"})
    st.set_language("it")
    try:
        ok, error = st.validate(text, song.patterns)
    finally:
        st.set_language(None)
    assert not ok and message.lower() in error.lower()


def test_canon_and_thirds_properties():
    import random
    from st_language.chords import pitch_to_midi
    from st_language.notation import key_signature_alters
    from st_language.transform import parse_reference
    rng = random.Random(21)
    for _ in range(60):
        key = rng.choice(["C", "G", "F", "D", "Bb", "Am", "Em"])
        alters = key_signature_alters(key)
        letters = [c + alters.get(c, "") for c in "cdefgab"]
        notes = [rng.choice(letters) + f"*{rng.randint(4, 6)}" + rng.choice(["'8", "'4", "'4.", "'2"])
                 for _ in range(rng.randint(1, 8))]
        song = _song_with({"P": f"key={key} " + " ".join(notes)})
        interval, delay = rng.randint(-12, 12), rng.choice(["'1", "'2", "'4", "'4."])

        def pitched(text, voice=1):
            return [(e.start, e.duration, pitch_to_midi(e.letter, e.octave))
                    for e in st.parse(text, song.patterns) if e.kind == "note" and e.voice == voice]

        shift = float(parse_reference(f"%P.canon({delay})").steps[0].args[0].beats)
        canon = pitched(f"%P.canon({delay},{interval})", 2)
        assert canon == [(s + shift, d, m + interval) for s, d, m in pitched("%P")]
        assert pitched(f"%P.canon({delay},{interval})") == pitched("%P")
        pairs = list(zip(pitched("%P.thirds"), pitched("%P.thirds", 2)))
        assert pairs and all(a[:2] == b[:2] and a[2] - b[2] in (3, 4) for a, b in pairs)
        assert sum(1 for e in st.parse("%P.thirds", song.patterns) if e.voice == 2) == len(notes)


def test_canon_and_thirds_reach_the_exports(tmp_path):
    song = st.read_song("ST: 2.12\nTonalita: C\n\nPattern %T:\n  c e g c\n\nTraccia A [Piano]:\n"
                        "  %T.canon('2,12) | %T.thirds |\n")
    midi = st.to_midi(song, str(tmp_path / "t.mid"))
    xml = st.to_musicxml(song, str(tmp_path / "t.musicxml"))
    assert os.path.getsize(midi) > 0 and "<voice>2</voice>" in open(xml, encoding="utf-8").read()
    assert os.path.exists(st.to_abc(song, str(tmp_path / "t.abc")))


def _arp(text, patterns=None, **options):
    song = _song_with(patterns or {})
    return [(e.letter, e.duration) for e in st.parse_track_text(text, song.patterns, **options) if e.kind == "note"]


@pytest.mark.parametrize("kind, letters", [
    ("up", "c e g c e g c e"), ("su", "c e g c e g c e"),
    ("down", "g e c g e c g e"), ("giu", "g e c g e c g e"), ("giù", "g e c g e c g e"),
    ("updown", "c e g e c e g e"), ("sugiu", "c e g e c e g e"),
    ("alberti", "c g e g c g e g"),
])
def test_arpeggio_types(kind, letters):
    patterns = {"T": "[c*4 e*4 g*4]'1"}
    assert [n for n, _d in _arp(f"%T.arpeggio({kind},8)", patterns)] == letters.split()
    assert [n for n, _d in _arp(f"[c*4 e*4 g*4]'1.arpeggio({kind},8)")] == letters.split()
    assert [n for n, _d in _arp(f"arp={kind},8 [c*4 e*4 g*4]'1")] == letters.split()


def test_arpeggio_details():
    # due note, una nota, l'ultima che si accorcia, la griglia in vigore
    assert [n for n, _d in _arp("[c e]'2.arpeggio(alberti,8)")] == ["c", "e", "c", "e"]
    assert [n for n, _d in _arp("[e]'4.arpeggio(updown,8)")] == ["e", "e"]
    assert _arp("[c e]'4..arpeggio(up,4)") == [("c", 1.0), ("e", 0.5)]
    assert [d for _n, d in _arp("16: 8[c e].arpeggio")] == [0.25] * 8
    assert [d for _n, d in _arp("arp=up 8: [c e]'4 16: [c e]'8")] == [0.5, 0.5, 0.25, 0.25]
    assert [d for _n, d in _arp("%T.arpeggio c", {"T": "[c e]'2"})] == [1, 1, 1]
    assert [d for _n, d in _arp("8: %T.arpeggio", {"T": "[c e]'2"})] == [0.5] * 4
    assert [round(d, 3) for _n, d in _arp("[c e]'4.arpeggio(up,8T)")] == [0.333, 0.333, 0.333]
    # il tempo non cambia: la nota dopo e' dove sarebbe stata
    assert st.parse("[c e]'2.arpeggio(up,8) f")[-1].start == 2
    # legato: un accordo solo, l'arpeggio continua oltre la stanghetta
    assert [n for n, _d in _arp("4: [c e].arpeggio(up,4)~ | [c e] | ")] == ["c", "e"]
    assert [n for n, _d in _arp("4: 2[c e].arpeggio(up,4)~ | 2[c e] |")] == ["c", "e", "c", "e"]


def test_arpeggio_notes_come_from_the_voicing_of_the_instrument():
    from st_language.chords import parse_chord_symbol, pitch_to_midi, voice_chord
    from st_language.instruments import instrument_for
    for name in ("Piano", "Guitar", "Bass"):
        instrument = instrument_for(name)
        notes = voice_chord(parse_chord_symbol("Am7"), 3, instrument)
        events = st.parse_track_text("8: 16Am7*3.arpeggio(up)", {}, instrument=instrument)
        played = [pitch_to_midi(e.letter, e.octave) for e in events if e.kind == "note"]
        assert sorted(set(played)) == sorted(set(notes)) and played[:len(notes)] == sorted(notes)
    # il basso e' la nota piu' bassa, lo stile sceglie le note, la tonalita' la grafia
    assert _arp("C/E.arpeggio(up,4)")[0][0] == "e"
    close = [n for n, _d in _arp("4Cmaj7.close.arpeggio(up,4)")]
    assert close == ["c", "e", "g", "b"]
    assert [n for n, _d in _arp("key=Eb 4Cm.close.arpeggio(up,4)")][:2] == ["c", "eb"]
    # un brano usa lo strumento della traccia
    song = st.read_song("ST: 2.12\n\nTraccia B [Bass]:\n  8: 8C.arpeggio(up)\n")
    part = song.tracks[0]
    played = {(e.letter, e.octave) for e in part.parsed_events(song.patterns, meter=song.meter()) if e.kind == "note"}
    assert played == {(e.letter, e.octave) for e in st.parse_track_text("8: 8C.arpeggio(up)", {}, instrument=part.instrument,
                                                                        default_octave=part.instrument.default_octave)
                      if e.kind == "note"}


def test_arpeggio_keeps_marks_velocity_and_state():
    events = [e for e in st.parse('100@ swing=66 shift=5 [c e]\'2.arpeggio(up,8)$fermata$accent "la"') if e.kind == "note"]
    assert {e.velocity for e in events} == {100} and all(e.swing and e.shift == 5 for e in events)
    assert events[0].decorations == ["accent"] and events[-1].decorations == ["fermata"]
    assert events[0].lyric == "la" and events[1].lyric is None
    slur = [(e.letter, e.slur) for e in st.parse("c( [d e]'4.arpeggio(up,8) f)") if e.kind == "note"]
    assert slur == [("c", "start"), ("d", "continue"), ("e", "continue"), ("f", "stop")]
    # arp= finisce con il pattern, con reset:, con arp=off; una voce lo eredita ma non lo cambia fuori
    assert [n for n, _d in _arp("%T [c e]'4", {"T": "arp=up,8 [c e]'4"})] == ["c", "e"]
    assert [n for n, _d in _arp("arp=up,8 reset: [c e]'4")] == []
    assert [n for n, _d in _arp("arp=up,8 { [c e]'4 ; arp=off [c e]'4 } [c e]'4")] == ["c", "e", "c", "e"]
    # il pattern eredita arp= dal punto del richiamo
    assert [n for n, _d in _arp("arp=up,8 %T", {"T": "[c e]'4"})] == ["c", "e"]
    # quello scritto sull'accordo vale piu' di arp=
    assert [n for n, _d in _arp("arp=up,8 [c e]'4.arpeggio(off)")] == []
    assert [n for n, _d in _arp("arp=up,8 [c e]'4.arpeggio(down,8)")] == ["e", "c"]
    # $arp sotto arp= resta rullato; un pattern gia' arpeggiato resta com'e'
    assert [e.kind for e in st.parse("arp=up,8 C$arp") if e.kind in ("chord", "note")] == ["chord"]
    assert [n for n, _d in _arp("%T.arpeggio(down,8)", {"T": "arp=up,8 [c e]'4 [d f]'4"})] == ["c", "e", "d", "f"]
    # note, pause e percussioni in un pattern misto non cambiano
    assert [e.kind for e in st.parse("%T.arpeggio(up,8)", _song_with({"T": "c [d e]'4 r"}).patterns)] == [
        "note", "note", "note", "rest"]
    # dopo .arpeggio le altre funzioni lavorano sulle note
    assert [n for n, _d in _arp("%T.arpeggio(up,8).retro", {"T": "[c*4 e*4]'4"})] == ["e", "c"]
    assert [n for n, _d in _arp("%T.arpeggio(up,8).step(1)", {"T": "key=C [c*4 e*4]'4"})] == ["d", "f"]


@pytest.mark.parametrize("text, message", [
    ("c.arpeggio", "accordo o su un blocco"),
    ("kick.arpeggio", "accordo o su un blocco"),
    ("[c kick].arpeggio", "accordo o su un blocco"),
    ("C$arp.arpeggio", "accordo rullato"),
    ("C.arpeggio(boh)", "sconosciuto"),
    ("C.arpeggio(up,x)", "Griglia"),
    ("C.arpeggio(up, 8)", "Niente spazi"),
    ("arp=boh C", "sconosciuto"),
    ("%A.arpeggio(off)", "vale solo su un accordo"),
    ("%A.arpeggio(boh)", "sconosciuto"),
    ("%A.arpeggio(up,8,3)", "troppi argomenti"),
    ("%K.arpeggio", "accordo o su un blocco"),
    ("%V.arpeggio", "una voce sola"),
    ("%A.canon('2).arpeggio", "una voce sola"),
    ("%R.arpeggio", "accordo rullato"),
])
def test_arpeggio_errors(text, message):
    song = _song_with({"A": "C", "K": "kick", "V": "{ C ; e }", "R": "C$arp"})
    st.set_language("it")
    try:
        ok, error = st.validate(text, song.patterns)
    finally:
        st.set_language(None)
    assert not ok and message in error


def test_arpeggio_with_the_rest_of_the_library(tmp_path):
    from st_language.notation import compute_token_spans
    from st_language.transform import expand_reference, format_reference, parse_reference
    song = _song_with({"G": "2C 2Am", "D": "arp=up kick"})
    # la durata e' quella degli accordi, in tutte le forme
    assert compute_token_spans("%G.arpeggio(up,8) c", song.patterns)[1][2] == 4
    assert compute_token_spans("2C.arpeggio(up,8) c", {})[1][2] == 2
    assert [w.message for w in st.check("4: 2C.arpeggio(up,8) 2C | c", {})] == []
    assert any("arp=" in w.message for w in st.check("arp=up kick", {}))
    # l'anteprima usa lo strumento e la griglia del punto
    found = expand_reference("%G.arpeggio(up)", song.patterns, grid=0.5)
    assert found.duration == 2 and {e.duration for e in found.events} == {0.5}
    assert [s.name if s else None for s, _ in found.stages] == [None, "arpeggio"]
    assert all(e.arp is None for e in found.events)
    assert format_reference(parse_reference("%G.arpeggio(updown,8)"), italian=True) == "%G.arpeggio(sugiu,8)"
    assert format_reference(parse_reference("%G.arpeggio(alberti)")) == "%G.arpeggio(alberti)"
    # la trasposizione del testo non tocca il suffisso, e arp= passa
    assert st.transpose_tokens(["Cmaj7.arpeggio(up,8)$fermata", "[c e].arpeggio(down)", "arp=up", "%G.arpeggio"], 2, 4) == [
        "Dmaj7.arpeggio(up,8)$fermata", "[d*4 f#*4].arpeggio(down)", "arp=up", "%G.arpeggio+2"]
    assert all(e.arp is None for e in st.parse("arp=up,8 C"))
    full = st.read_song("ST: 2.12\n\nPattern %G:\n  4: 2C 2Am\n\nTraccia A [Piano]:\n  %G.arpeggio(alberti,8) arp=up,16 2F arp=off G\n")
    assert os.path.getsize(st.to_midi(full, str(tmp_path / "a.mid"))) > 0
    assert os.path.exists(st.to_musicxml(full, str(tmp_path / "a.musicxml")))
    assert os.path.exists(st.to_abc(full, str(tmp_path / "a.abc")))


def test_arpeggio_state_and_pattern_give_the_same_midi(tmp_path):
    """arp= e .arpeggio sugli stessi accordi: stesso MIDI."""
    head = "ST: 2.12\n\nPattern %Giro:\n  4: 4Cmaj7 | 4Am7 |\n\nTraccia A [Piano]:\n"
    state = st.read_song(head.replace("%Giro:\n  4: 4Cmaj7 | 4Am7 |", "%Vuoto:\n  c") + "  8: arp=alberti 8Cmaj7 | 8Am7 | arp=off 2C |\n")
    pattern = st.read_song(head + "  8: %Giro.arpeggio(alberti,8) 2C |\n")
    a, b = tmp_path / "a.mid", tmp_path / "b.mid"
    st.to_midi(state, str(a))
    st.to_midi(pattern, str(b))
    assert a.read_bytes() == b.read_bytes()


_TEXT_PATTERNS = {"A": "8: 100@ d e", "S": "swing=66 shift=5 arp=up,8 c", "R": "rel: c e g key=G f",
                  "T": "transpose=2 c", "Z": "reset: c", "B": "c 8: d", "N": "%A f", "M": "key=C c e"}


@pytest.mark.parametrize("text", [
    "%A c", "2%A c", "%S [c e]'4", "%R c", "%T c", "%Z c", "rel: c %A g", "key=G %A f", "key=G %R f",
    "transpose=3 %A c", "transpose=3 %Z c", "transpose=3 %T c", "2%B c", "3%B c", "%N c", "%A+2 c", "%R+3 c",
    "2( %A c )", "2( %A c 16: d )", "{ %A c ; %A }", "|: %A c :| d", "%A >> c 120@ d", "%M.step(1) c",
    "key=G %M.retro c", "2%A.retro c", "%A.canon('2,12) c", "%A | c |", "rel: c %A.octave(1) g", "c // commento\n%A d",
    "arp=up,8 %M.retro [c e]'4", "%S.octave(1) [c e]'4",
])
def test_expand_to_text_keeps_the_sound(text):
    from st_language.totext import _sound
    song = _song_with(_TEXT_PATTERNS)
    result = st.expand_to_text(text, song.patterns)
    assert "%" not in result and "\x00" not in result
    assert _sound(result, {}, 4, None) == _sound(text, song.patterns, 4, None)
    assert st.expand_to_text(result, {}) == result


def test_expand_to_text_details():
    song = _song_with(_TEXT_PATTERNS)
    assert st.expand_to_text("%A c", song.patterns) == "8: 100@ d e 4: 80@ c"
    assert st.expand_to_text("c // resta\n%A", song.patterns) == "c // resta\n8: 100@ d e"
    # lo stato del punto in cui comincia il testo
    assert st.expand_to_text("%A c", song.patterns, state="16: 60@ ") == "8: 100@ d e 16: 60@ c"
    assert st.expand_to_text("c d", {}) == "c d"
    with pytest.raises(st.NotationError):
        st.expand_to_text("%Nessuno", {})


def test_events_to_text_round_trip():
    from st_language.totext import _sound
    texts = ["4: c d 8: e f 2g", "100@ c 60@ d", "8T: c d e 4: f", "swing=66 8: c d swing=50 e", "shift=-10 c shift=0 d",
             "c! dx e_", "C Am7.drop2 F/A G*5", "[c e g] 2[d f]", "kick snare 2hihat", "c>d 2e>3f c>d>c", "c r 3r d",
             "c( d e) f", "d'g c e'G f", "c$accent d$fermata", "vol=40 >> c d vol=100 e", "vol=0 >>exp c cho=20 d vol=90",
             "SON c SOFF d", "tempo=90 c tempo=60'4. d", "$\"rit.\" c $C/E d", "c<  d>", "{ c d ; e f g }",
             "{ 8: c d ; r e ; 2g }", "100@ >> c d 40@ e", "c'4. d'8", "c~ c d", "5c 7d"]
    for text in texts:
        written = st.events_to_text(st.parse(text))
        assert _sound(written, {}, 4, None) == _sound(text, {}, 4, None), (text, written)
    # una nota senza sillaba prima di una che ce l'ha (dopo .retro): ognuna resta la sua
    reversed_lyrics = st.parse("%L.retro", _song_with({"L": 'c "la" d'}).patterns)
    lyrics = [(e.letter, e.lyric) for e in st.parse(st.events_to_text(reversed_lyrics)) if e.kind == "note"]
    assert lyrics == [("d", None), ("c", "la")]
    assert [e.decorations for e in st.parse(st.events_to_text(st.parse("c$accent$tenuto"))) if e.kind == "note"] == [
        ["accent", "tenuto"]]


def test_events_to_text_after_the_functions():
    from st_language.totext import _sound
    song = _song_with({"T": "key=C 4: c*4 d*4 e*4 c*4", "G": "key=C 2C 2G", "D": "c'4. d'8 e'2"})
    for text in ("%T.canon('2,12)", "%T.thirds", "%D.augment(1.5)", "%D.augment(1.3)", "%D.diminish(3)", "%G.step(1)",
                 "%G.arpeggio(alberti,8)", "%T.canon('4.,7,3).retro", "%T.sequence(3,-1)"):
        written = st.events_to_text(st.parse(text, song.patterns))
        assert _sound(written, {}, 4, None) == _sound(text, song.patterns, 4, None), (text, written)
    assert st.events_to_text(st.parse("%T.thirds", song.patterns)).startswith("{ ")
    # le alterazioni seguono la tonalita' in vigore; griglia e velocity gia' in vigore non si riscrivono
    assert st.events_to_text(st.parse("key=G f g fn"), key="G") == "80@ 4: f*4 g*4 fn*4"
    assert st.events_to_text(st.parse("c d"), grid=1, velocity=80) == "c*4 d*4"
    assert st.events_to_text(st.parse("8: c d"), grid=0.5, velocity=80) == "c*4 d*4"


def test_find_references():
    text = 'c %A+2.retro 2( %B ) { d ; &"x"+1 } C.arpeggio(up)$fermata "%no" // %commento\n%Tema.seq'
    found = st.find_references(text)
    assert [(r.kind, r.token) for r in found] == [("pattern", "%A+2.retro"), ("pattern", "%B"), ("midi", '&"x"+1'),
                                                  ("arpeggio", ".arpeggio(up)"), ("pattern", "%Tema.seq")]
    assert all(text[r.start:r.end] == r.token for r in found)
    # un testo che si sta scrivendo
    assert [r.token for r in st.find_references("2( %A %B.")] == ["%A", "%B."]
    assert [r.token for r in st.find_references("%T.sequence(3,")] == ["%T.sequence(3,"]


def test_list_transforms_arguments():
    from st_language.transform import list_transforms
    names = {t["name"]: t for t in list_transforms()}
    voices = names["canon"]["arguments"][2]
    assert (voices["min"], voices["max"], voices["default"], voices["type"]) == (2, 4, 2, "integer")
    assert names["canon"]["arguments"][0]["type"] == "note_value" and names["canon"]["group"] == "voices"
    assert names["arpeggio"]["arguments"][0]["choices"] == ["up", "down", "updown", "alberti"]
    assert {t["group"] for t in names.values()} == {"pitch", "rhythm", "order", "voices", "chords"}
    assert all(t["group_label"] for t in names.values())


def test_state_at_the_point_of_a_reference():
    from st_language.notation import context_prefix_before
    from st_language.transform import expand_reference
    text = "8: 100@ swing=66 shift=5 arp=up reset: 16: arp=alberti,8 swing16=60 c %T"
    prefix = context_prefix_before(text, text.index("%T"))
    assert prefix == "16: swing16=60 arp=alberti,8 "
    song = _song_with({"T": "[c e g]'1 d"})
    found = expand_reference("%T.octave(1)", song.patterns, prefix=prefix)
    assert [e.letter for e in found.events[:4]] == ["c", "g", "e", "g"] and found.events[0].swing
    assert found.events[-1].duration == 0.25


def test_public_names_for_soundtext():
    from st_language.midi import resolve_event_notes
    from st_language.notation import pattern_state_effect, pattern_writes_state, resolve_midi_ref
    patterns = _song_with({"A": "8: c", "B": "c"}).patterns
    assert pattern_writes_state(patterns["A"].tokens, patterns) and not pattern_writes_state(patterns["B"].tokens, patterns)
    assert pattern_state_effect(patterns["A"].tokens, patterns) == ({"velocity", "swing", "shift", "arp"}, {"grid": "8:"})
    assert resolve_event_notes(st.parse("c")[0], st.Song().instrument("Piano")) == ([60], 80)
    assert callable(resolve_midi_ref)


def test_translator_falls_back_on_the_catalogs():
    from st_language._i18n import set_translator, tr
    st.set_language("en")
    try:
        set_translator(lambda text, *a, **k: "mio" if text == "errore" else text.format(*a, **k))
        assert tr("errore") == "mio"
        assert tr("avviso") == "warning"
        assert tr("{n} tracce, nessun errore", n=2) == "2 tracks, no errors"
    finally:
        set_translator(None)
        st.set_language(None)


def test_plain_notation_file_is_a_one_track_song(tmp_path):
    path = tmp_path / "solo.txt"
    path.write_text("8: c d e f", encoding="utf-8")
    song = st.load_song(str(path), instrument="Guitar")
    assert [(t.name, t.instrument_name) for t in song.tracks] == [("Guitar", "Guitar")]


# ------------------------------------------------------------------ installazione e lingue

def test_pyproject_entry_points_exist():
    tomllib = pytest.importorskip("tomllib")
    with open(os.path.join(ROOT, "pyproject.toml"), "rb") as f:
        project = tomllib.load(f)["project"]
    assert project["name"] == "st-language" and project["dependencies"] == []
    assert project["version"] == st.__version__
    from st_language import cli
    for target in project["scripts"].values():
        module, func = target.split(":")
        assert module == "st_language.cli" and callable(getattr(cli, func))


@pytest.mark.parametrize("code", ["en", "fr", "es"])
def test_library_catalogs_translate_every_library_message(code):
    from _strings import library_strings
    with open(os.path.join(ROOT, "st_language", "locales", f"{code}.json"), encoding="utf-8") as f:
        catalog = json.load(f)
    missing = [s for s in library_strings() if not catalog.get(s)]
    assert not missing, missing[:5]


# ------------------------------------------------------------------ pacchetto (PyPI)

def _pyproject():
    with open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8") as f:
        return f.read()


def test_package_versions_agree():
    """La versione di pyproject.toml, quella di st_language e quella della
    suite di conformita' dicono lo stesso (il workflow di pubblicazione ne
    controlla il tag)."""
    import re
    version = re.search(r'^version = "([^"]+)"', _pyproject(), re.M).group(1)
    assert version == st.__version__
    spec = open(os.path.join(SPEC, "ST-language.md"), encoding="utf-8").read()
    assert f"**Version {'.'.join(version.split('.')[:2])}**" in spec
    with open(os.path.join(SPEC, "conformance", "cases.json"), encoding="utf-8") as f:
        assert json.load(f)["spec_version"] == ".".join(version.split(".")[:2])


def test_package_metadata_is_ready_for_pypi():
    text = _pyproject()
    assert 'license = "GPL-3.0-or-later"' in text and 'license-files = ["LICENSE"]' in text
    assert "License ::" not in text                      # le classificatori di licenza sono deprecate
    for script in ("st-language", "stcheck", "st2mid", "st2musicxml", "st2abc", "st2mtxt"):
        assert f"{script} = " in text
    manifest = open(os.path.join(ROOT, "MANIFEST.in"), encoding="utf-8").read()
    assert "prune tests" in manifest and "include LICENSE" in manifest
    publish = open(os.path.join(ROOT, ".github", "workflows", "publish-pypi.yml"), encoding="utf-8").read()
    assert "id-token: write" in publish and "pypa/gh-action-pypi-publish" in publish
    assert "secrets." not in publish                        # trusted publishing: nessun segreto nel repository
    # lo sdist ha la specifica e la suite di conformita', non l'applicazione
    assert "include docs/spec/ST-language.md" in manifest and "include docs/spec/conformance/cases.json" in manifest
    assert "prune core" in manifest and "prune gui" in manifest
    # solo il job che allega i file alla release puo' scrivere nel repository
    import re
    writers = []
    for block in re.split(r"\n  (?=[a-z][a-z0-9-]*:\n)", publish.split("\njobs:\n", 1)[1]):
        if "contents: write" in block:
            writers.append(block.split(":", 1)[0].strip())
    assert writers == ["github-release"]


# ------------------------------------------------------------------ 2.7 nelle esportazioni

SONG_27 = """ST: 2.7
Titolo: Prova
Autore: A. Autore
Parole: P. Paroliere
Tempo: 100 BPM
Tonalita: 1: C, 3: G

Strumento TrombaSib:
  program=56 percussione=no ottava=4 range=54-82 poly=no voicing=monophonic trasposizione=-2

Traccia Tromba [TrombaSib]:
  4: $segno $C7 d'g c e f g | a b c*5 d*5 $tocoda | f# g a b $ds $coda | c*5 C$arp 2r |
  "la la la la" "2: lo lo lo lo"

Piano:
  4: C$arp [c e g]'g C c$trem d$staccatissimo
"""


def test_musicxml_has_the_27_features():
    from st_language.musicxml import project_to_musicxml
    xml = project_to_musicxml(st.read_song(SONG_27))
    for needed in ("<work-title>Prova</work-title>", '<creator type="composer">A. Autore</creator>',
                   '<creator type="lyricist">P. Paroliere</creator>', '<grace slash="yes"/>', "<arpeggiate/>",
                   "<chromatic>-2</chromatic>", "<segno/>", "<coda/>", "D.S. al Coda", '<lyric number="2">',
                   '<tremolo type="single">3</tremolo>', "<staccatissimo/>"):
        assert needed in xml, needed
    # tromba in Si bemolle: Do maggiore si scrive in Re (2 diesis), poi Sol diventa La (3)
    assert "<key><fifths>2</fifths>" in xml and "<key><fifths>3</fifths>" in xml
    # la sigla senza suono $C7 si scrive trasposta (D7) nella parte della tromba
    assert "<root-step>D</root-step>" in xml


def test_abc_has_title_verses_and_key_change():
    from st_language.abc import project_to_abc
    abc = project_to_abc(st.read_song(SONG_27))
    assert "T:Prova" in abc and "C:A. Autore" in abc and "[K:G]" in abc and "{/" in abc
    assert sum(line.startswith("w:") for line in abc.splitlines()) >= 2


def test_midi_grace_note_sounds_before_the_note():
    from st_language.midi import song_midi_tracks
    song = st.read_song("Tempo: 120 BPM\n\nPiano:\n  d'g c\n")
    ons = [(t, m[1]) for t, _o, m in sorted(song_midi_tracks(song)[0][1]) if m[0] & 0xF0 == 0x90]
    assert ons == [(0, 62), (60, 60)]


# ------------------------------------------------------------------ voicing spread

def _spread(symbol):
    from st_language.chords import _apply_named_voicing, parse_chord_symbol
    return _apply_named_voicing("spread", 60, parse_chord_symbol(symbol).intervals)


@pytest.mark.parametrize("symbol, fifth", [("C", 79), ("Cm", 79), ("Cdim", 78)])
def test_spread_triad_keeps_the_fifth(symbol, fifth):
    notes = _spread(symbol)
    assert fifth in notes
    assert len(notes) == len(set(notes))


@pytest.mark.parametrize("symbol, expected", [
    ("C7", [48, 60, 76, 82]),
    ("Cmaj7", [48, 60, 76, 83]),
    ("Cm9", [48, 60, 75, 82, 86]),
])
def test_spread_four_note_chords_drop_the_fifth(symbol, expected):
    assert _spread(symbol) == expected


# ------------------------------------------------------------------ controlli di battuta nei blocchi di voci

@pytest.mark.parametrize("voices", [
    "c d e f | g a b c ; 4C | 4G",
    "c d e f | g a b c | c d e f ; 4C | 4G | 4C",
    "c d e f | g a b c | c d e f | g a b c ; 4C | 4G | 4C | 4G",
])
def test_voice_block_with_right_bars_gives_no_warning(voices):
    assert st.check("4: c d e f | { " + voices + " } | 4C |") == []


def test_voice_block_still_reports_a_short_bar_in_the_second_voice():
    issues = st.check("4: c d e f | { c d e f | g a b c | c d e f ; 4C | 2G | 4C } | 4C |")
    assert [i.bar for i in issues] == [2]       # prima della correzione: battuta 3


def test_voice_block_reports_lyrics_and_anchors_inside_a_voice():
    assert [i.kind for i in st.check('4: { c d "la la la" ; e f }')] == ["lyric"]
    assert [(i.kind, i.bar) for i in st.check("4: c d e f | { c d bar=1 ; e f }")] == [("anchor", 1)]


# ------------------------------------------------------------------ file .st: box, strumenti, mixer, metrica

@pytest.mark.parametrize("command", ["rel:", "abs:", "reset:"])
def test_box_keeps_a_line_with_only_a_notation_command(command):
    song = st.read_song(f'Piano:\n  4: c\n\nBox Piano "A" |0:\n  {command}\n  4: c d e f\n')
    assert song.tracks[0].clips[0].text == f"{command}\n4: c d e f"


def test_invalid_numbers_in_instrument_and_mixer_blocks_use_the_default():
    song = st.read_song("Strumento Mio:\n  program=abc ottava=x\n\nTraccia A [Mio]:\n  4: c\n\n"
                        "Mixer A:\n  volume: alto pan=0.5\n")
    part = song.tracks[0]
    assert (part.instrument.gm_program, part.instrument.default_octave) == (0, 4)
    assert (part.volume, part.pan) == (100, 96)


def test_meter_with_a_zero_counts_bars_in_four_four(tmp_path):
    song = st.read_song("Metrica: 4/0\nTempo: 1: 120, 3: 100\n\nPiano:\n  4: c d e f c d e f c\n")
    from st_language.timing import build_tempo_beat_map
    assert build_tempo_beat_map(song) == [(0.0, 120), (8.0, 100)]
    for export, ext in ((st.to_midi, "mid"), (st.to_musicxml, "xml"), (st.to_abc, "abc"), (st.to_mtxt, "mtxt")):
        export(song, str(tmp_path / f"brano.{ext}"))


# ------------------------------------------------------------------ MIDI: note della stessa altezza

def _note_messages(body):
    from st_language.midi import song_midi_tracks
    song = st.read_song("Piano:\n  " + body + "\n")
    return [(t, m[0] & 0xF0, m[1]) for t, _o, m in sorted(song_midi_tracks(song)[0][1], key=lambda e: (e[0], e[1]))
            if m[0] & 0xF0 in (0x80, 0x90)]


@pytest.mark.parametrize("body", ["4: c_ c", "4: c( c d)"])
def test_legato_note_ends_where_the_same_pitch_starts_again(body):
    assert _note_messages(body)[:3] == [(0, 0x90, 60), (480, 0x80, 60), (480, 0x90, 60)]


def test_unison_voices_sound_the_longer_note_once():
    assert _note_messages("4: { 2c ; c }") == [(0, 0x90, 60), (960, 0x80, 60)]


# ------------------------------------------------------------------ trasposizione del testo: accordi e sigle

def _chord_roots(text):
    from st_language.chords import parse_chord_symbol, voice_chord
    piano = st.read_song("Piano:\n  4: c\n").tracks[0].instrument
    return [voice_chord(parse_chord_symbol(e.symbol), e.octave, piano)[0]
            for e in st.parse(text) if e.kind == "chord"]


@pytest.mark.parametrize("semitones", [1, -1, 2, 12, -7])
def test_transposed_chords_sound_the_same_interval_higher(semitones):
    from st_language.notation import tokenize, transpose_tokens
    text = "4: B*3 C*4 Cb B# Bb7 G/B Cmaj7.drop2 F#m*5"
    moved = " ".join(transpose_tokens(tokenize(text), semitones, 4))
    assert _chord_roots(moved) == [n + semitones for n in _chord_roots(text)]


def test_transposed_text_moves_the_chord_symbols_too():
    from st_language.notation import tokenize, transpose_tokens
    assert transpose_tokens(tokenize("$C7 $G/B c"), 2, 4) == ["$D7", "$A/C#", "d*4"]


def test_default_instrument_changed_in_one_song_stays_in_that_song():
    song = st.read_song("Piano:\n  4: c\n")
    song.tracks[0].instrument.default_octave = 2
    assert st.read_song("Piano:\n  4: c\n").tracks[0].instrument.default_octave == 4


# ------------------------------------------------------------------ comandi da terminale: casi d'errore

def test_cli_events_reports_a_syntax_error(tmp_path, capsys):
    from st_language.cli import main
    path = tmp_path / "brano.st"
    path.write_text("Piano:\n  4: c d xyz f\n", encoding="utf-8")
    assert main(["events", str(path)]) == 1
    assert "xyz" in capsys.readouterr().err


def test_cli_tempo_accepts_decimals(tmp_path):
    from st_language.cli import main
    path = tmp_path / "brano.st"
    path.write_text("Piano:\n  4: c d\n", encoding="utf-8")
    assert main(["midi", "--tempo", "72.5", str(path), "-o", str(tmp_path / "x.mid")]) == 0


def test_cli_file_that_is_not_utf8_is_an_error_not_a_crash(tmp_path):
    from st_language.cli import main
    path = tmp_path / "brano.st"
    path.write_bytes(b"\xff\xfe\x00bin")
    assert main(["check", str(path)]) == 2


@pytest.mark.parametrize("meter, written", [
    ((4, 4), "4/4"), ((6, 8), "6/8"), ((3, 3), "4/4"), ((6, 12), "8/16"), ((4, 6), "5/8"), ((4, 0), None),
])
def test_midi_time_signature_keeps_the_bar_length_when_it_can(meter, written):
    from st_language.midi import midi_time_signature
    result = midi_time_signature(*meter)
    assert (f"{result[0]}/{2 ** result[1]}" if result else None) == written


# Intestazione corta con un nome General MIDI o un alias: e' una traccia,
# come nella forma esplicita "Traccia Nome [Flute]:".
@pytest.mark.parametrize("header, program", [("Flute:", 73), ("Violin:", 40), ("Organ:", 16), ("Flauto:", 73)])
def test_short_header_takes_general_midi_names(header, program):
    song = st.read_song(f"Tempo: 96 BPM\n\nBass:\n  4: c |\n\n{header}\n  4: c d e f |\n")
    assert [p.name for p in song.tracks] == ["Bass", header[:-1]]
    assert song.tracks[1].instrument.gm_program == program
    assert song.file_warnings == []


def test_short_header_with_index_and_general_midi_name():
    song = st.read_song("Violin 2:\n  4: c |\n")
    assert song.get_track("Violin 2").instrument.gm_program == 40


def test_unknown_short_header_is_ignored_with_a_warning():
    song = st.read_song("Bass:\n  4: c |\n\nPianoo:\n  4: c d e f |\n")
    assert [p.name for p in song.tracks] == ["Bass"]
    assert [line for line, _ in song.file_warnings] == [4]
    assert "Pianoo" in song.file_warnings[0][1]


def test_unknown_short_header_without_body_gives_no_warning():
    song = st.read_song("Foo:\n\nPiano:\n  4: c |\n")
    assert song.file_warnings == []


def test_notation_commands_are_not_track_headers():
    song = st.read_song("Flute:\n  rel:\n  4: c d e f |\n")
    assert [p.name for p in song.tracks] == ["Flute"]
    assert song.tracks[0].text.startswith("rel:")
