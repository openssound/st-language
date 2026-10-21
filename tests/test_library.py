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
    assert stfile.LANGUAGE_VERSION == (2, 10)


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
