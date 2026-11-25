"""
2.13: il simbolo '♯' accettato come '#' e la riscrittura delle alterazioni
('symbols' / 'ascii') senza cambiare il suono.
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pytest

import st_language as st
from st_language.notation import parse_track_text, tokenize

SONG = """ST: 2.12
Tonalita: Bb
Tempo: 100 BPM
Metrica: 4/4
// una nota eb in un commento, e un accordo Bb7
Pattern %Bb_Giro:
  4: Bb7 Eb7/Bb F#m7b5 C7#9 [c# eb g] 2(bb b) key=Eb c#*4>d#*4 $Bb7/D "la bb# do" |
Traccia Piano [Piano]:
  8: %Bb_Giro eb'4. Ab7.drop2 key=F# f# g# a# |
Mixer Piano:
  volume=80
"""


def _midi(song_text, tmp_path, name):
    """I byte del MIDI del brano: lo stesso suono, nota per nota."""
    path = tmp_path / name
    st.to_midi(st.read_song(song_text), str(path))
    return path.read_bytes()


def _events(text):
    return [(e.kind, e.start, e.duration, tuple(sorted(e.pitches)) if getattr(e, "pitches", None) else None,
             getattr(e, "symbol", None), getattr(e, "bass", None)) for e in parse_track_text(text, {})]


@pytest.mark.parametrize("ascii_text", [
    "4: e# f# c#*5 2g#",
    "2: F#m7 C/F# G#7 C#maj7.drop2 F#*3",
    "4: key=F# f g a",
    "4: [c# e# g#] 2[c#*4 g#*4]",
    "4: c#*4>d#*4>c#*4 e",
    "4: 2(c# d#) e",
])
def test_sharp_symbol_reads_as_the_hash(ascii_text):
    symbols = ascii_text.replace("#", "♯")
    assert _events(symbols) == _events(ascii_text)


def test_sharp_symbol_in_lyrics_and_extensions_is_left_alone():
    assert [e.kind for e in parse_track_text('c "la♯" d', {})] == ["note", "note"]
    assert st.normalize_accidentals(SONG, "symbols").count('"la bb# do"') == 1
    assert "C7#9" in st.normalize_accidentals(SONG, "symbols")
    assert "F♯m7b5" in st.normalize_accidentals(SONG, "symbols")


def test_normalize_to_symbols_and_back_keeps_text_and_sound(tmp_path):
    symbols = st.normalize_accidentals(SONG, "symbols")
    for expected in ("Tonalita: B♭", "B♭7 E♭7/B♭", "[c♯ e♭ g]", "2(b♭ b)", "key=E♭", "c♯*4>d♯*4", "$B♭7/D", "e♭'4.",
                     "A♭7.drop2", "key=F♯ f♯ g♯ a♯"):
        assert expected in symbols, expected
    assert "// una nota eb in un commento, e un accordo Bb7" in symbols      # commento
    assert "Pattern %Bb_Giro:" in symbols and "%Bb_Giro e♭" in symbols  # nome del pattern
    assert "Mixer Piano:\n  volume=80" in symbols
    assert st.normalize_accidentals(symbols, "ascii") == SONG
    assert _midi(symbols, tmp_path, "a.mid") == _midi(SONG, tmp_path, "b.mid")


def test_examples_round_trip_byte_for_byte_and_sound_the_same(tmp_path):
    for name in sorted(os.listdir(os.path.join(ROOT, "examples"))):
        text = open(os.path.join(ROOT, "examples", name), encoding="utf-8").read()
        symbols = st.normalize_accidentals(text, "symbols")
        assert symbols != text and "♯" in symbols or "♭" in symbols, name
        assert st.normalize_accidentals(symbols, "ascii") == text, name
        assert _midi(symbols, tmp_path, "a.mid") == _midi(text, tmp_path, "b.mid"), name


def test_style_option_of_the_writers():
    assert st.transpose_tokens(["c#", "Eb7", "d"], 0, 4, accidentals="symbols") == ["c♯", "E♭7", "d"]
    assert st.transpose_tokens(["c♯", "E♭7"], 0, 4, accidentals="ascii") == ["c#", "Eb7"]
    moved = st.transpose_tokens(["c", "e", "g"], 1, 4, accidentals="symbols")
    assert any("♯" in tok for tok in moved) and not any("#" in tok for tok in moved)
    events = parse_track_text("4: c# eb g", {})
    assert "♯" in st.events_to_text(events, accidentals="symbols") and "#" not in st.events_to_text(
        events, accidentals="symbols")
    assert "♯" not in st.events_to_text(events) and "♭" not in st.events_to_text(events)
    patterns = {"A": st.Pattern(name="A", tokens=tokenize("c# eb"))}
    assert "c♯" in st.expand_to_text("%A", patterns, accidentals="symbols")
    with pytest.raises(ValueError):
        st.transpose_tokens(["c"], 0, 4, accidentals="strano")


def test_language_version_and_declaration():
    assert st.language_version("4: c d e") is None
    assert st.language_version("4: c♯ d") == (2, 13)
    assert st.language_version("4: bd hh sn") == (2, 13)
    assert st.language_version("4: [bd hh] 2(sn)") == (2, 13)
    assert st.language_version("4: kick snare") is None
    assert st.language_version('4: c "bd" d') is None
    assert st.declare_language_version("ST: 2.12\nTraccia Piano [Piano]:\n  4: c♯ |\n").startswith("ST: 2.13\n")
    assert st.declare_language_version("Traccia Piano [Piano]:\n  4: c♯ |\n").startswith("ST: 2.13\n")
    plain = "ST: 2.12\nTraccia Piano [Piano]:\n  4: c# |\n"
    assert st.declare_language_version(plain) == plain


def test_command_line(tmp_path):
    src = tmp_path / "brano.st"
    src.write_text(SONG, encoding="utf-8")
    out = tmp_path / "simboli.st"
    run = lambda *args: subprocess.run([sys.executable, "-m", "st_language", *args], cwd=ROOT, check=True,
                                       capture_output=True, text=True)
    run("accidentals", str(src), "-o", str(out))
    written = out.read_text(encoding="utf-8")
    assert written.startswith("ST: 2.13\n") and "E♭7/B♭" in written
    back = tmp_path / "ascii.st"
    run("accidentals", "--style", "ascii", str(out), "-o", str(back))
    assert back.read_text(encoding="utf-8").split("\n", 1)[1] == SONG.split("\n", 1)[1]
