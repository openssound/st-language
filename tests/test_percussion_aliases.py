"""
2.13: le abbreviazioni delle percussioni ('bd', 'hh', 'sn'...). Valgono
dove vale il nome lungo e non possono coincidere con altro: lettera sola,
nota o accordo, nome esistente.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pytest

import st_language as st
from st_language.instruments import (
    PERCUSSION_ALIASES, PERCUSSION_MAP, percussion_name, percussion_short_name,
)
from st_language.notation import RE_NOTE, RE_PERC, parse_track_text


def _events(text):
    return parse_track_text(text, {})


def test_every_alias_stands_for_a_long_name_and_every_name_has_one():
    assert len(PERCUSSION_ALIASES) == 53
    assert all(long in PERCUSSION_MAP for long in PERCUSSION_ALIASES.values())
    assert set(PERCUSSION_ALIASES.values()) == set(PERCUSSION_MAP)


@pytest.mark.parametrize("short, long", sorted(PERCUSSION_ALIASES.items()))
def test_alias_gives_the_same_general_midi_note_as_the_long_name(short, long):
    short_ev, long_ev = _events(f"4: {short}")[0], _events(f"4: {long}")[0]
    assert short_ev.kind == long_ev.kind == "percussion"
    assert short_ev.name == long_ev.name == long
    assert PERCUSSION_MAP[short_ev.name] == PERCUSSION_MAP[long]


@pytest.mark.parametrize("alias", sorted(PERCUSSION_ALIASES))
def test_alias_is_never_a_single_letter_a_note_or_an_existing_name(alias):
    assert len(alias) > 1
    assert not RE_NOTE.match(alias), alias
    assert alias not in PERCUSSION_MAP
    assert RE_PERC.match(alias)
    # in una traccia melodica non da' mai una nota
    assert _events(f"4: {alias}")[0].kind == "percussion"


def test_flats_stay_flats():
    for note in ("ab", "bb", "cb", "db", "eb", "fb", "gb"):
        assert _events(f"4: {note}")[0].kind == "note"
        assert note not in PERCUSSION_ALIASES


def test_aliases_work_in_groups_blocks_and_with_a_multiplier():
    long = _events("8: kick hihat snare hihat kick kick snare hihat")
    short = _events("8: bd hh sn hh bd bd sn hh")
    assert [(e.kind, e.name, e.start, e.duration) for e in short] == \
           [(e.kind, e.name, e.start, e.duration) for e in long]
    block = _events("4: [bd hh]")[0]
    assert [item["name"] for item in block.items] == ["kick", "hihat"]
    assert [e.name for e in _events("4: 2(bd) sn") if e.kind == "percussion"] == ["kick", "kick", "snare"]


def test_helpers():
    assert percussion_name("bd") == "kick"
    assert percussion_name("kick") == "kick"
    assert percussion_name("xyz") == "xyz"
    assert percussion_short_name("kick") == "bd"
    assert percussion_short_name("snare") == "sn"
    assert percussion_short_name("nonesiste") == "nonesiste"


def test_unknown_names_are_still_rejected_and_listed_with_long_names():
    with pytest.raises(st.NotationError):
        _events("4: bdd")
