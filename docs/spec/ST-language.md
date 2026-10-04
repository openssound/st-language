# ST-language Specification

**Version 2.0** · Reference implementation: the `st_language` Python
library (this repository) · Italian version: [ST-language.it.md](ST-language.it.md)

© 2026 Sergio Scolaro. This specification is licensed under the
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
license (CC BY 4.0): you may copy, translate and adapt it, also
commercially, as long as you credit the source. The reference
implementation is free software under the GPL-3.0-or-later.

---

## 1. Introduction

ST-language (SoundText Language) is a plain-text notation for music:
melodies, abstract chords, drums, dynamics, tempo changes, several voices
and lyrics, written as a sequence of short tokens.

```
// Verse
4: Am | F | C | G |            // one chord per bar
8: e*5 d*5 c*5 d*5 2e*5 2e*5 |
"Ma- ry had a lit- tle lamb"
```

This document defines:

- the **notation** of a single part (a *track text*): how text becomes a
  list of timed musical events (sections 2-11);
- the **song file** format `.st`, which puts several tracks, patterns,
  tempo and meter together (section 12);
- how events map to **MIDI** (section 13, informative);
- the **conformance suite** (section 14).

### 1.1 Conformance

The key words MUST, MUST NOT, SHOULD and MAY are to be interpreted as in
RFC 2119. A conforming **parser** turns every valid track text into the
events of section 11 (the same kinds, times, durations, pitches and
velocities as the reference implementation, compared with a tolerance of
10⁻⁹ beats) and rejects every invalid one (section 10). A conforming
**song reader** also reads the `.st` format of section 12. Error message
texts are not normative.

### 1.2 Units

Time is measured in **beats**: one beat is a quarter note. A conforming
parser MUST compute positions with **exact rational arithmetic** (or
equivalent): triplets accumulate thirds of a beat, and floating-point
error would move later events across bar lines.

---

## 2. Lexical structure

A track text is a Unicode string. Line breaks are whitespace, with one
exception: they end comments.

### 2.1 Comments

`//` starts a **comment** that extends to the end of the line (excluding
the line break). A `//` inside a lyric string (`"..."`, section 8.5) on
the same line does not start a comment. Comments are removed before
tokenization; implementations SHOULD replace them with spaces so that
character positions stay the same as in the original text.

### 2.2 Tokens

After comments are removed, the text is split into **tokens** from left
to right; whitespace separates tokens and is otherwise ignored. At each
position, the first matching rule applies:

1. `|` is a token by itself (bar check, section 8.6).
2. `"` starts a **lyric** token that ends at the next `"`. A lyric with
   no closing quote is an error.
3. Optional digits followed by `[` start a **block** token that ends at
   the first following `]` (blocks do not nest); a `'` immediately after
   the `]` extends the token with a note value (`[c e g]'2`), and a
   single `<` or `>` immediately after the `]` extends it with a hairpin
   (`[c e g]<`). No `]` is an error.
4. Optional digits followed by `(` start a **group** token that ends at
   the matching `)`; parentheses nest, and parentheses inside lyric
   strings do not count. No matching `)` is an error.
5. `{` starts a **voice block** token that ends at the matching `}`
   (same rules as groups). No matching `}` is an error.
6. Otherwise a **plain** token runs until whitespace, `|` or `"`. So
   `d*4|` is two tokens (`d*4`, `|`) and `c"la"` is two tokens (`c`,
   `"la"`).

Group and voice-block tokens keep their content as text; it is tokenized
again, with the same rules, when the group or block is interpreted.

---

## 3. Grammar

The grammar of each kind of token (EBNF; `digit` is 0-9, `letter` is
A-Z or a-z, `word` is one or more letters, digits or `_`):

```ebnf
token        = grid | velocity | tempo | ramp | control | sustain | bar-check
             | lyric | pattern-ref | midi-ref | group | voices | sounding ;

grid         = number [ "T" | "Q" | "S" ] ":" ;                 (* 4:  8T: *)
velocity     = ( number | dynamic ) "@" ;                       (* 100@  mf@ *)
dynamic      = "ppp" | "pp" | "p" | "mp" | "mf" | "f" | "ff" | "fff" ;
tempo        = "tempo=" number ;                               (* tempo=120 *)
ramp         = ( ">>" | "<<" ) [ curve ] ;                       (* >>  >>exp *)
curve        = "lin" | "exp" | "log" | "s" ;
control      = control-name "=" [ "-" ] number [ "." digit { digit } ] ;
control-name = "vol" | "expr" | "pan" | "mod" | "rev" | "cho" ;   (* vol=80  pan=-0.5 *)
sustain      = "SON" | "SOFF" ;
bar-check    = "|" ;
lyric        = '"' { any character except '"' } '"' ;
pattern-ref  = [ number ] "%" word ;                            (* %Riff  3%Riff *)
midi-ref     = [ number ] "&" ( word | "/" | "-" ) { word | "/" | "-" } ;
group        = [ number ] "(" { token } ")" ;                   (* 4(c d) *)
voices       = "{" voice { ";" voice } "}" ;                    (* { c d ; 2e } *)
voice        = { token } ;

sounding     = ( note | chord | percussion | rest | block | slide ) [ value ]
               [ hairpin ] ;
hairpin      = "<" | ">" ;                                      (* 2c<  c'2> *)
note         = [ number ] pitch [ octave ] [ modifier ] ;
pitch        = "a" | "b" | "c" | "d" | "e" | "f" | "g" , [ accidental ] ;
accidental   = "#" | "b" | "♭" | "-" ;
octave       = "*" number ;
modifier     = "!" | "x" | "_" ;
chord        = [ number ] root quality [ "." style ] [ "/" bass ]
               [ "*" number ] [ modifier ] ;
root         = "A" | "B" | "C" | "D" | "E" | "F" | "G" , [ accidental ] ;
bass         = root ;
quality      = (* one of the qualities of section 9.1 *) ;
style        = (* one of the voicing styles of section 9.3 *) ;
percussion   = [ number ] drum-name ;                           (* section 9.5 *)
rest         = [ number ] "r" ;
block        = [ number ] "[" atom { atom } "]" ;
atom         = note | chord | percussion ;
slide        = slide-point ">" slide-point { ">" slide-point } ;
slide-point  = [ number ] pitch [ octave ] ;
value        = "'" ( "1" | "2" | "4" | "8" | "16" | "32" | "64" )
               [ "T" | "Q" | "S" ] [ "." [ "." ] ] [ modifier ] ;
number       = digit { digit } ;
```

Notes on the grammar:

- The **value** may come before or after the modifier: `c'8!` and `c!'8`
  are the same token meaning. It cannot follow a grid, velocity or other
  state command.
- The **hairpin** is always the last character (`c'2!<`, `2c*4>`); a rest
  with a hairpin is an error. A token ending in `<<` or `>>` is never a
  hairpin.
- In a **chord**, the quality is the *shortest* string that lets the
  rest of the token match, so a final `x` is the mute modifier
  (`Cmaj7x`). After a voicing style, a final `x` is the modifier if the
  style without it exists and the style with it does not (`C.drop2x`
  is `drop2` muted, `C.hendrix` is the `hendrix` style).
- After `/` comes an alternate **bass** (`C/E`); the octave is always
  written with `*` (`C7*3`, `C/E*3`).
- Lowercase letters a-g are notes; a lowercase word that is not a note,
  a rest or a command is a **percussion** name and MUST be one of the
  names of section 9.5.
- Inside a block, atoms are separated by whitespace and MUST NOT
  contain `|`, values or nested blocks.
- A `;` outside a voice block is not part of any token rule and makes
  the token invalid.

---

## 4. Time and state

A track is interpreted **left to right** with a *cursor* (the current
time, starting at 0) and a **current state**:

| State | Initial value | Changed by |
| --- | --- | --- |
| grid unit | 1 beat (as after `4:`) | grid tokens |
| velocity | 80 | velocity tokens |
| automation values | `vol` 100, `expr` 127, `pan` 0, `mod` 0, `rev` 0, `cho` 0 | control tokens (section 7.5) |
| default octave | given by the instrument (4 if none) | — |

**Grid.** `N:` sets the unit to 4/N beats: `4:` quarter note, `8:`
eighth, `16:` sixteenth, `2:` half, `1:` whole; any positive N is
allowed (`12:` is a triplet eighth). A letter after N makes a **tuplet**
grid: `T` multiplies the unit by 2/3 (triplets), `Q` by 4/5
(quintuplets), `S` by 4/7 (septuplets). `N` MUST be positive.

**Duration.** A sounding token lasts `multiplier × unit`, where the
multiplier is the leading number (1 if absent) and the unit is the grid
unit, or the **note value** if the token has one (section 6.6). The
cursor then advances by the duration. State commands, bar checks and
lyrics take no time.

---

## 5. Pitch

A note is a letter `a`-`g` with an optional accidental: `#` (sharp),
`b`, `♭` or `-` (flat; `-` is a typing shortcut). `b` alone is the note
B; `bb` is B-flat.

The **octave** follows `*`: `c*4` is middle C. When
absent, the instrument's default octave is used. The MIDI note number is

```
midi = (octave + 1) × 12 + pc(letter) + alteration
pc: c=0 d=2 e=4 f=5 g=7 a=9 b=11      alteration: # = +1, flat = -1
```

without wrapping: `cb*4` is B3 (59) and `b#*4` is C5 (72). A note whose
MIDI number falls outside 0-127 is an error (the highest note is `g*9`).

---

## 6. Sounding tokens

Every sounding token produces one **event** at the cursor, with the
current velocity, and advances the cursor by its duration.

### 6.1 Notes

`c`, `f#*5`, `2eb`: a single pitch (event kind `note`).

### 6.2 Chords

`C`, `Am7`, `G7/B*3`, `Cmaj7.drop2`: an abstract chord (kind `chord`)
with its symbol (root + quality), optional voicing style, optional bass
and octave. How the chord becomes notes is described in section 9.

### 6.3 Percussion

`kick`, `2snare`: a drum sound (kind `percussion`) from the table of
section 9.5.

### 6.4 Rests

`r`, `3r`: silence (kind `rest`).

### 6.5 Blocks

`[c*4 e*4 g*4]`, `2[kick hihat]`, `[C e*5]`: notes, chords and drums
that start and end together (kind `block`). The duration is given by
the block's multiplier (and value), not by the atoms; multipliers inside
atoms are ignored.

### 6.6 Note values

A value after `'` gives the duration directly instead of the grid unit:
the number is the note (1 whole = 4 beats, 2 half, 4 quarter, 8 eighth,
16, 32, 64), a tuplet letter scales it like a tuplet grid, and one or two
dots multiply it by 3/2 or 7/4:

| Token | Beats |
| --- | --- |
| `c'4` | 1 |
| `c'8.` | 3/4 |
| `c'2..` | 7/2 |
| `c'8T` | 1/3 |
| `2c'8` | 1 |

The value applies **only to that token**: the grid does not change. It
works with notes, chords, blocks, rests, percussion and slides.

### 6.7 Articulation

A final `!` (staccato), `x` (mute) or `_` (legato) on a note or chord
sets the event's articulation. It does not change the duration of the
event (the time it occupies); see section 13 for how it sounds.

### 6.8 Slides

`c*4>d*4` (kind `slide`): a continuous glide through two or more pitches
(*taps*). Let the taps be p₁…pₙ with optional multipliers m₁…mₙ. There
are n segments:

- for i < n, segment i is the glide from tap i to tap i+1 and lasts
  `(mᵢ or 1) × unit`;
- segment n is the hold on the final pitch and lasts `(mₙ or 0) × unit`.

So `c*4>d*4` lasts one unit like a note, `c*4>d*4>c*4` (bend and release)
two, `2c*4>3d*4` glides for 2 units and holds for 3. A slide whose total
duration is 0 is an error.

The event carries the first pitch, the following taps and the segment
durations.

---

## 7. State commands

### 7.1 Velocity and dynamics

`N@` sets the velocity (1-127; outside is an error). Classical dynamics
are fixed velocities:

| ppp | pp | p | mp | mf | f | ff | fff |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | 40 | 60 | 75 | 90 | 105 | 120 | 127 |

### 7.2 Tempo

`tempo=N` sets the tempo (beats per minute, 1-999; outside is an error)
from the cursor on. It produces
an event of kind `tempo_marker` with `bpm` = N. Tempo is global: a
marker in any track changes the tempo of the whole song.

### 7.3 Ramps

`>>` or `<<` (both mean the same; the direction comes from the values)
opens a **ramp**. The last state command before it MUST be a velocity,
a tempo or a control command (sounding tokens may stand in between, a
grid command may not), otherwise it is an error. A velocity or tempo
ramp closes at the next command **of the same kind** (grid commands
inside the ramp do not close it), and MUST be closed before a velocity
or tempo command of the other kind and before the end of the track.
Control ramps are described in section 7.5.

An optional **curve** after the arrows gives the shape f(x) of the
ramp, for x from 0 (start) to 1 (end):

| Curve | f(x) | Use |
| --- | --- | --- |
| `lin` (default) | x | even change |
| `exp` | x² | starts slowly, then speeds up (volume fades) |
| `log` | 1 − (1 − x)² | starts fast, then slows down |
| `s` | x² (3 − 2x) | smooth at both ends |

- **Velocity ramp** (crescendo/diminuendo): let the events produced
  between opening and closing, except `control` events, be e₀…eₖ₋₁ (k
  events). Event i gets `round(v₀ + (v₁ - v₀) × f(i / (k-1)))` (with
  k = 1: the end value), where v₀ is the velocity at the opening and v₁
  the closing value, clamped to 1-127.
- **Tempo ramp** (accelerando/rallentando): for each of those events, a
  `tempo_marker` at its start with the interpolated tempo (same
  formula). With no events in between, a single marker with the end
  value is placed at the cursor.

### 7.4 Sustain pedal

`SON` and `SOFF` produce events of kind `sustain` (name `on`/`off`) at
the cursor.

### 7.5 Automations

`name=N` sets an **automation value** of the track from the cursor on.
Automations act on the whole instrument (in MIDI, its channel), not on
single notes, and change continuously even during a held note:

| Name | Meaning | Range | Initial |
| --- | --- | --- | --- |
| `vol` | volume | 0-127 | 100 |
| `expr` | expression (volume inside the dynamic) | 0-127 | 127 |
| `pan` | stereo position, −1 left, 0 centre, 1 right | −1..1 | 0 |
| `mod` | modulation (vibrato) | 0-127 | 0 |
| `rev` | reverb send | 0-127 | 0 |
| `cho` | chorus send | 0-127 | 0 |

A value outside the range is an error. `pan` keeps its decimals; the
other values are rounded to the nearest integer (`vol=80.6` is 81).

Without a ramp, `name=N` produces a `control` event at the cursor with
`name`, `value` = N and duration 0. A ramp (section 7.3) right after it
opens a **control ramp**: it is closed by the next command with the
**same name**, which produces instead one `control` event from the
opening position to the cursor (duration = the difference), with
`start_value` = the value at the opening, `value` = N and `curve` (the
default is `lin`). If the cursor has not moved, it is a plain value
change (duration 0, no `start_value`). Ramps of different names are
independent and may overlap; velocity and tempo commands do not close
them. A control ramp still open at the end of the track (or of a voice)
is an error.

**Hairpins.** A final `<` on a sounding token is a crescendo on that
event, `>` a diminuendo, made with the expression. Let E be the current
`expr` value, H = round(E / 2), s and d the start and duration of the
event. A hairpin produces, after the event:

1. a `control` event `expr` at s, duration d, `start_value` H and
   `value` E for `<` (E then H for `>`), curve `lin`;
2. a `control` event `expr` at s + d, duration 0, `value` E (the
   expression returns to its value).

A hairpin inside an open `expr` ramp is an error.

---

## 8. Structure

### 8.1 Repeat groups

`N(tokens)` repeats its content N times (1 if no number), as if the
tokens had been written out. Groups can be nested. Groups are expanded
before interpretation, so state set inside a group carries on after it.

### 8.2 Patterns

`%Name` inserts the tokens of the pattern `Name` (defined in the song,
section 12); `N%Name` inserts them N times. Patterns may reference other
patterns; a reference chain deeper than 32 levels (or a cycle) is an
error, as is an undefined pattern.

### 8.3 MIDI references

`&Name` (and `N&Name`) inserts tokens converted from a MIDI file of a
library. This is an **optional** feature of the host application: a
parser without a library MUST report such a reference as an error.

### 8.4 Voice blocks

`{ v₁ ; v₂ ; … }` contains **voices** that start together at the cursor.
Each voice is a token sequence interpreted on its own:

- it starts with the current grid unit, velocity and automation values
  (and the default octave); state changes inside a voice stay inside it,
  except automation values (section 7.5), which belong to the whole
  track;
- its events start at the block's position; voice k (counting from 1)
  of a block reached in voice v has voice number v + k - 1 (the top level
  is voice 1);
- the block lasts as long as its longest voice; the cursor then advances
  by that amount, and the state after the block is the state before it,
  except that each automation value is the one of the control event,
  in any voice, that ends last (the first voice wins a tie);
- a block with only empty voices is an error.

Voices may contain groups, pattern references, bar checks, lyrics and
other voice blocks. Patterns are expanded inside each voice.

### 8.5 Lyrics

A lyric token `"…"` holds syllables separated by whitespace. They are
assigned, in order, to the **sung events** that precede the token since
the previous lyric token (or the start): notes, chords, slides and blocks
containing at least one note or chord — not rests, not percussion.

- `*` gives no syllable to its event.
- `_` marks the event as a continuation of the previous syllable
  (melisma); the event's `lyric` is `_`.
- A syllable ending with `-` continues the word in the next syllable.
- A lyric token directly attached to a note (`c"la"`) is simply the next
  token: it gets the notes pending since the previous lyric.
- Lyrics inside a group repeat with it.
- The first voice of a voice block shares the pending events with the
  surrounding text: a lyric after the block also covers the first
  voice's events, and a lyric inside the first voice also covers the
  events pending before the block.
- More syllables than pending events is a **warning** (section 10.2);
  the extra syllables are ignored.

Syllables are stored in the event's `lyric` field.

### 8.6 Bar checks

`|` asserts that a bar ends at the cursor. It takes no time and is not
an error when it is wrong: it produces a **warning** (section 10.2).
Inside a block `[...]` it is an error.

---

## 9. Chords and drums

### 9.1 Chord qualities

A chord symbol is a root (A-G with optional accidental) plus a quality.
Intervals are semitones above the root:

| Quality | Intervals | | Quality | Intervals |
| --- | --- | --- | --- | --- |
| (none), `maj` | 0 4 7 | | `m6` | 0 3 7 9 |
| `m`, `min` | 0 3 7 | | `9` | 0 4 7 10 14 |
| `7` | 0 4 7 10 | | `maj9` | 0 4 7 11 14 |
| `maj7` | 0 4 7 11 | | `m9` | 0 3 7 10 14 |
| `m7`, `min7` | 0 3 7 10 | | `mMaj7` | 0 3 7 11 |
| `dim`, `°` | 0 3 6 | | `m7b5` | 0 3 6 10 |
| `dim7`, `°7` | 0 3 6 9 | | `add9` | 0 4 7 14 |
| `aug` | 0 4 8 | | `7sus4` | 0 5 7 10 |
| `sus2` | 0 2 7 | | `7b9`, `7alt` | 0 4 7 10 13 |
| `sus4` | 0 5 7 | | `7#9` | 0 4 7 10 15 |
| `6` | 0 4 7 9 | | `5` | 0 7 |
| `11` | 0 4 7 10 14 17 | | `13` | 0 4 7 10 14 21 |
| `maj13` | 0 4 7 11 14 21 | | | |

An unknown quality is an error.

### 9.2 Realization

The **pitch-class content** of a chord is normative: the root plus the
intervals above, and the bass if any. The exact voicing (which octaves,
which notes are doubled or omitted) is **implementation-defined** and
depends on the instrument; the reference algorithm is:

- base = MIDI(root, octave) (section 5, octave from the token or the
  instrument);
- instrument style `monophonic`: the root only; `root_fifth`: root and
  fifth (if the quality has one); otherwise (`spread`) every interval;
- each note is moved by octaves into the instrument's range;
- with a bass `/X`: a note of pitch class X is added below all the
  others.

### 9.3 Voicing styles

`.style` after the chord requests a voicing: general styles `close`,
`open`, `inv1`, `inv2`, `inv3`, `shell`, `noroot`; keyboard styles
`left`, `right`, `spread`; guitar styles `barre`, `Caged`, `cAged`,
`caGed`, `cagEd`, `cageD`, `drop2`, `drop3`, `triad`, `power`,
`openpos`, `hendrix`, `top`, `bottom`. An unknown style is an error.
Styles of another instrument family fall back to the nearest general one
(implementation-defined).

### 9.4 Instruments

A track's instrument gives the default octave, the range and the chord
style, and its General MIDI program. The built-in instruments are:

| Name | GM program | Default octave | Range (MIDI) | Chord style |
| --- | --- | --- | --- | --- |
| Piano | 0 | 4 | 21-108 | spread |
| Guitar | 25 | 3 | 40-88 | spread |
| Bass | 33 | 2 | 28-60 | root_fifth |
| Trumpet | 56 | 4 | 54-82 | monophonic |
| Drums | — (channel 10) | 4 | — | — |

Other names are resolved by an implementation-defined table of aliases
(e.g. `violin`, `electric_bass`, `drum_kit`) and General MIDI names.

### 9.5 Drum names

| Name | GM note | Name | GM note | Name | GM note |
| --- | --- | --- | --- | --- | --- |
| kick | 36 | kick2 | 35 | snare | 38 |
| snare2 | 40 | rimshot | 37 | clap | 39 |
| hihat | 42 | hihat_open | 46 | hihat_pedal | 44 |
| tom1 | 48 | tom2 | 45 | floor | 41 |
| tom_hi | 50 | tom_lowmid | 47 | tom_highfloor | 43 |
| crash | 49 | crash2 | 57 | ride | 51 |
| ride2 | 59 | ride_bell | 53 | china | 52 |
| splash | 55 | tambourine | 54 | cowbell | 56 |
| bongo_hi | 60 | bongo_low | 61 | conga_mute | 62 |
| conga_open | 63 | conga_low | 64 | timbale_hi | 65 |
| timbale_low | 66 | cabasa | 69 | maracas | 70 |
| claves | 75 | woodblock_hi | 76 | woodblock_low | 77 |

---

## 10. Errors and warnings

### 10.1 Errors

A track text with an error is **invalid** and produces no events. A
conforming parser MUST report at least these errors:

- unclosed block, group, voice block or lyric;
- a token matching no rule of section 3 (including `;` outside a voice
  block and `|` inside a block);
- unknown percussion name, chord quality or voicing style;
- velocity outside 1-127; grid with N = 0; note value other than 1, 2,
  4, 8, 16, 32, 64;
- a note outside MIDI 0-127;
- a ramp not after a velocity, tempo or control command, or not closed
  as required by sections 7.3 and 7.5;
- an automation value outside its range; a hairpin on a rest or inside
  an open `expr` ramp;
- an undefined pattern, a too-deep or cyclic reference, an unresolvable
  MIDI reference;
- an empty block `[]` or an empty voice block.

### 10.2 Warnings

Warnings do not make the text invalid.

**Bar checks.** Bar lines come from the song's meter: bar 1 starts at
beat 0 and each bar lasts `4 × num / den` beats of the meter in force
(section 12.3). A track that starts later in the song (a box, section
12.4) is checked at its absolute position. The checks are processed in
time order with a running **shift** (initially 0):

1. expected = position − shift;
2. find the bar line nearest to *expected*, never the one at beat 0; on
   a tie, the earlier one; let it start bar k;
3. delta = expected − that line. If delta ≠ 0, report "bar k−1 has
   |delta| beats too many (delta > 0) / too few (delta < 0)" at the `|`;
4. shift = shift + delta.

So a missing note is reported once, not at every following check. A `|`
repeated by a group or a pattern is reported at most once (at the group
or reference). Each voice of a voice block is checked on its own,
starting from the shift at the block; the shift after the block is the
one before it.

**Lyrics.** More syllables than pending events (section 8.5): reported
at the lyric token.

---

## 11. The event model

Interpreting a track produces a list of events. Each event has:

| Field | Type | Meaning |
| --- | --- | --- |
| `kind` | string | `note`, `chord`, `percussion`, `rest`, `block`, `slide`, `sustain`, `tempo_marker`, `control` |
| `start` | number | start, in beats from the beginning of the track |
| `duration` | number | duration in beats (0 for `sustain` and `tempo_marker`, and for `control` without a ramp) |
| `velocity` | 1-127 | current velocity (default 80) |
| `letter`, `octave` | | note pitch (`note`, first tap of `slide`) |
| `symbol`, `voicing`, `bass`, `octave` | | chord (`chord`) |
| `name` | string | drum name (`percussion`); `on`/`off` (`sustain`); automation name (`control`) |
| `items` | list | atoms of a `block`: each with `kind` and its fields |
| `articulation` | string | `staccato`, `mute`, `legato` |
| `slide_points` | list | taps after the first (`slide`), as [letter, octave] |
| `slide_segment_durations` | list | segment durations (`slide`) |
| `bpm` | integer | tempo (`tempo_marker`) |
| `value` | number | automation value (`control`; at the end of a ramp) |
| `start_value` | number | value at the start of a ramp (`control`) |
| `curve` | string | ramp curve: `lin`, `exp`, `log`, `s` (`control` ramps) |
| `voice` | integer | voice number (1 outside voice blocks) |
| `lyric` | string | syllable (sung events) |

Events appear in interpretation order (all events of the first voice of
a block, then the second voice, …), which is not necessarily sorted by
`start`. The note letter keeps the accidental as written (`eb`, `e♭`,
`e-` are all `e` with a flat for pitch purposes).

---

## 12. The song file (`.st`)

A song file is UTF-8 text made of **lines** grouped into **blocks**. A
block starts with a header line and continues with body lines until an
empty line or the next header. Lines are compared after removing leading
and trailing whitespace. Lines outside any block that match no header are
ignored (free text).

### 12.1 Song headers

| Line | Meaning |
| --- | --- |
| `Tempo: 120 BPM` | tempo |
| `Tempo: 1: 120, 5: 140` | tempo per bar (bar: bpm, …) |
| `Metrica: 3/4` | meter |
| `Metrica: 1: 4/4, 5: 3/4` | meter per bar |
| `Tonalita: Am` | key (A-G, optional accidental, optional `m`) |

With a per-bar list, the song tempo/meter is the bar-1 value, or the
first value if bar 1 is not listed. `Tempo`, `Metrica` and `Tonalita`
are case-insensitive; the other headers are written as shown.

### 12.2 Blocks

| Header | Body |
| --- | --- |
| `Pattern %Name:` | the pattern's tokens |
| `Traccia Name [Instrument]:` | track text |
| `Piano:`, `Piano 2:` (a known instrument name, optional index) | text of the track `Piano` / `Piano 2` |
| `Box Track "Name" \|beat:` | a box of the track `Track` starting at `beat` |
| `Strumento Name:` | instrument definition (`program=40 percussione=no ottava=3 range=36-96 poly=si voicing=spread`) |
| `Mixer Track:` | `volume` (0-200), `pan` (-1…1), `mute`, `solo` (`si`/`no`) of a track |

Track and box bodies keep their **line breaks** (comments end at line
ends); pattern bodies are tokenized. Instrument and mixer blocks are
read before the tracks, wherever they are in the file. Applications MAY
add other block types (SoundText uses `Effetti`, `Plugin`, `Catena
master`, `Audio`, `Master:` and `Ambiente:`); readers MUST skip blocks
they do not know. A track whose instrument is `Audio` has no notation.

### 12.3 Bar positions

Bar starts are computed from the meter list: bar 1 starts at beat 0;
the meter in force at bar 1 is the listed bar-1 meter, or 4/4 if the
list does not start at bar 1, or the `Metrica:` value if there is no
list; it changes at each listed bar; each bar lasts `4 × num / den`
beats. Per-bar tempo changes take effect at those positions.

### 12.4 Boxes

When a track has boxes, its text is built from them, in order of start
beat:

- the gap before each box (from the end of the previous box, or 0) is
  filled with rests on a sixteenth grid: `16: Nr` with N = round(gap /
  0.25);
- each box contributes `4: 80@ ` followed by its text (so a box always
  starts from the default state); a box whose text contains `//` is
  followed by a line break;
- the parts are joined with spaces; a box's end is its start plus the
  end of its last event.

The body of a track that has boxes is ignored, so writers leave it empty:
the header alone gives the track's name and instrument.

### 12.5 Solo and mute

The audible tracks are the tracks not in mute; if at least one track is
in solo, only the tracks in solo (and not in mute).

---

## 13. Mapping to MIDI (informative)

The reference exporter writes a Standard MIDI File (format 1, 480 ticks
per beat): a conductor track with tempo and meter, then one track per
audible track:

- channels in order, skipping channel 10, which is reserved for drums;
- program change = instrument GM program (drums: bank 120);
- notes: `note` → its pitch; `chord` → its realization (section 9.2);
  `block` → all atoms; `percussion` → the drum note of section 9.5;
- velocity = event velocity × track volume / 100;
- articulation changes the **sounding** length only: staccato 50 %,
  mute 15 %, legato 115 %;
- `slide` → the first pitch with pitch-bend ramps (bend range set to 24
  semitones via RPN 0);
- `sustain` → CC 64; tempo markers and per-bar changes → set-tempo;
- `control` → control change: `vol` CC 7 (× track volume / 100), `expr`
  CC 11, `pan` CC 10 (`round(64 + 63 × value)`), `mod` CC 1, `rev` CC 91,
  `cho` CC 93; a ramp is written as a series of values along its curve
  (at most 128 points, at least 10 ticks apart, equal consecutive values
  omitted). The score export draws ramps of `vol` and `expr` (hairpins
  included) as crescendo/diminuendo wedges;
- lyrics → *lyrics* meta events (syllables continuing a word without a
  trailing space, word ends with one; `_` not written).

---

## 14. Conformance suite

[`conformance/cases.json`](conformance/cases.json) contains test cases
(see [`conformance/README.md`](conformance/README.md)): for each input,
either `"error": true` or the expected events (section 11 fields,
numbers rounded to 9 decimals, `voice` omitted when 1, block atoms
without their multiplier) and the expected warnings (character range of
the token and bar number; 0 for lyrics). A parser conforms to this
version if it gives the same result for every case.

---

## Appendix A: changes

**2.0** — removed the duplicate forms, so that each thing has one
spelling: the octave is only `*n` (`c/4` and the chord octave `C7/3`
are no longer valid; `/` is only the alternate bass), the tempo command
is `tempo=N` instead of `N§`. In the song file a short track header needs
a space before the index (`Guitar 2:`; `Guitar2:` is the instrument
`Guitar2`). Texts using the removed forms are invalid.
Slides have a single rule (section 6.8): the old "legacy" form, where a
chain without multipliers after the first tap divided one unit among its
glides, is gone. The song file no longer accepts the alternative
`Instrument Name:` blocks (with `type:`, `volume`, `pan`) and the
`Name — Instrument:` track headers.

**1.1** — automations (`vol=`, `expr=`, `pan=`, `mod=`, `rev=`,
`cho=`, section 7.5) with their ramps, ramp curves (`>>exp`, `>>log`,
`>>s`, section 7.3), hairpins on sounding tokens (`c<`, `c>`), the
`control` event. Every valid 1.0 text is valid 1.1 text with the same
events.

**1.0** — first published version: notation, voices, note values,
lyrics, bar checks, comments, song file format, conformance suite.
