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
