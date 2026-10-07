# ST-language

**ST-language** is a plain-text music notation — notes, abstract chords,
drums, dynamics, tempo changes, automations (volume, expression, pan,
modulation, effect sends, with curved ramps and hairpins), several
voices and lyrics — and this is
its reference implementation: a pure-Python library (no dependencies)
with command-line tools to check songs and export them to **MIDI**,
**MusicXML**, **ABC** and **MTXT**. It is the notation engine of
[SoundText](https://github.com/openssound/soundtext), usable on its own.

```
// a blues riff
Tempo: 96 BPM

Bass:
  8: 2c*2 2e*2 2g*2 2a*2 | 2a#*2 2a*2 2g*2 2e*2 |

Piano:
  4: 4C7 | 4F7 |
```

## Install

```bash
pip install st-language
```

Python 3.9 or later, no other packages needed. To work on the library
itself: `pip install .` from the
[SoundText repository](https://github.com/openssound/soundtext).

## Command line

```bash
st-language check song.st          # syntax errors and warnings (bar checks, lyrics)
st-language midi song.st -o song.mid
st-language musicxml song.st       # -> song.musicxml
st-language abc song.st            # -> song.abc (ABC 2.1)
st-language mtxt song.st           # -> song.mtxt (MTXT 1.0, one event per line)
st-language mtxt take.mtxt         # MTXT -> take.mid
st-language events song.st         # the events as JSON
echo "4: c d e f | 2g 2g" | st2mid - -o melody.mid --instrument Trumpet
```

`stcheck`, `st2mid`, `st2musicxml`, `st2abc` and `st2mtxt` are shortcuts. A file without track
headers is a one-track song (choose the instrument with `--instrument`).
Messages are in English, Italian, French or Spanish (`--lang`, or the
`ST_LANGUAGE`/`LANG` environment variables).

## Python

```python
import st_language as st

events = st.parse("4: c d e f | 2g 2g")           # timed events (beats)
ok, error = st.validate("4: C Am | F G")
warnings = st.check("4: c d e | f g a b |")      # bar 1: 1 quarter note missing

song = st.load_song("song.st")                   # or st.read_song(text)
song = st.Song(name="Demo", tempo_bpm=100)
song.add_track("Bass", "Bass", "4: c*2 g*1 2c*2")
song.add_pattern("Riff", "8: c d e g")
st.to_midi(song, "demo.mid")
st.to_musicxml(song, "demo.musicxml")
st.to_abc(song, "demo.abc")
```

## Specification

The language and the `.st` song format are defined in the
[ST-language specification](https://github.com/openssound/st-language/blob/main/docs/spec/ST-language.md)
(CC BY 4.0, also [in Italian](https://github.com/openssound/st-language/blob/main/docs/spec/ST-language.it.md)),
with a [conformance suite](https://github.com/openssound/st-language/tree/main/docs/spec/conformance)
for other implementations.

## License

GPL-3.0-or-later, © 2026 Sergio Scolaro. The MTXT-derived voice-name table is MIT
(see `THIRD_PARTY_NOTICES.md`).

---

*In italiano:* ST-language e' la notazione musicale testuale di
SoundText come libreria Python autonoma, senza dipendenze, con i comandi
`st-language check | midi | musicxml | abc | mtxt | events` (e le scorciatoie
`stcheck`, `st2mid`, `st2musicxml`, `st2abc`, `st2mtxt`). La specifica, anche in italiano, e'
in `docs/spec/` del repository.
