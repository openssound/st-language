"""
Comandi da terminale della libreria ST-language.

    st-language check brano.st          controlla la sintassi e gli avvisi
    st-language midi brano.st -o x.mid  esporta in MIDI
    st-language musicxml brano.st       esporta la partitura MusicXML
    st-language abc brano.st            esporta in notazione ABC
    st-language events brano.st         gli eventi (JSON), per verifiche

Un file senza tracce (solo notazione, anche '-' = standard input) e' un
brano di una traccia: --instrument ne sceglie lo strumento, --tempo e
--time il tempo e la metrica. Scorciatoie installate col pacchetto:
stcheck, st2mid, st2musicxml, st2abc.
"""

import argparse
import json
import os
import sys
from dataclasses import asdict
from typing import List, Optional

from . import __version__
from ._i18n import set_language, tr
from .notation import notation_warnings, validate_track_text
from .song import Song, load_song, text_to_song


def _read(source: str, instrument: str, tempo: Optional[int], time_sig: Optional[str]) -> Song:
    song = text_to_song(sys.stdin.read(), "stdin", instrument) if source == "-" else load_song(source, instrument)
    if tempo:
        song.tempo_bpm = tempo
        song.tempo_changes = []
    if time_sig:
        song.time_sig = time_sig
        song.metrica_changes = []
    return song


def _line_col(text: str, offset: int):
    line = text.count("\n", 0, offset) + 1
    col = offset - (text.rfind("\n", 0, offset) + 1) + 1
    return line, col


def check(song: Song) -> int:
    """Stampa errori e avvisi; ritorna il numero di errori."""
    errors = 0
    for part in song.tracks:
        if part.is_audio:
            continue
        ok, msg = validate_track_text(part.text, song.patterns, default_octave=part.instrument.default_octave)
        if not ok:
            errors += 1
            print(f"{part.name}: {tr('errore')}: {msg}")
            continue
        for w in notation_warnings(part.text, song.patterns, song.time_sig, song.metrica_changes,
                                   default_octave=part.instrument.default_octave):
            line, col = _line_col(part.text, w.char_start)
            print(f"{part.name}:{line}:{col}: {tr('avviso')}: {w.message}")
    if not errors:
        print(tr("{n} tracce, nessun errore", n=len([t for t in song.tracks if not t.is_audio])))
    return errors


def events_json(song: Song) -> List[dict]:
    out = []
    for part in song.tracks:
        if part.is_audio:
            continue
        events = []
        for ev in part.parsed_events(song.patterns):
            d = {k: v for k, v in asdict(ev).items() if v is not None and not (k == "voice" and v == 1)}
            events.append(d)
        out.append({"track": part.name, "instrument": part.instrument.name, "events": events})
    return out


def _output(source: str, out: Optional[str], ext: str) -> str:
    if out:
        return out
    base = "stdin" if source == "-" else os.path.splitext(source)[0]
    return base + ext


def main(argv: Optional[List[str]] = None, command: Optional[str] = None) -> int:
    set_language()
    parser = argparse.ArgumentParser(prog="st-language" if command is None else None,
                                     description="ST-language " + __version__)
    if command is None:
        parser.add_argument("command", choices=["check", "midi", "musicxml", "abc", "events"])
    parser.add_argument("files", nargs="+", help=tr("file .st o di sola notazione ('-' = standard input)"))
    parser.add_argument("-o", "--output", help=tr("file di uscita (con un solo file in ingresso)"))
    parser.add_argument("--instrument", default="Piano", help=tr("strumento per i file di sola notazione"))
    parser.add_argument("--tempo", type=int, help=tr("tempo in BPM (sostituisce quello del file)"))
    parser.add_argument("--time", dest="time_sig", help=tr("metrica, es. 3/4 (sostituisce quella del file)"))
    parser.add_argument("--lang", help=tr("lingua dei messaggi: it, en, fr, es"))
    parser.add_argument("--all-tracks", action="store_true", help=tr("esporta anche le tracce in Mute"))
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)
    command = command or args.command
    set_language(args.lang)
    if args.output and len(args.files) > 1:
        parser.error(tr("-o vale con un solo file"))
    status = 0
    for source in args.files:
        try:
            song = _read(source, args.instrument, args.tempo, args.time_sig)
        except OSError as e:
            print(f"{source}: {e}", file=sys.stderr)
            status = 2
            continue
        if command == "check":
            if len(args.files) > 1:
                print(f"== {source}")
            status = max(status, 1 if check(song) else 0)
        elif command == "events":
            json.dump(events_json(song), sys.stdout, ensure_ascii=False, indent=1)
            print()
        else:
            if check_quiet(song):
                print(tr("{source}: errori di sintassi, niente esportazione (vedi st-language check)",
                         source=source), file=sys.stderr)
                status = 1
                continue
            if command == "midi":
                from .midi import song_to_midi
                path = song_to_midi(song, _output(source, args.output, ".mid"), only_audible=not args.all_tracks)
            elif command == "abc":
                from .abc import export_project_to_abc
                path = export_project_to_abc(song, _output(source, args.output, ".abc"),
                                             only_audible=not args.all_tracks)
            else:
                from .musicxml import export_project_to_musicxml
                path = export_project_to_musicxml(song, _output(source, args.output, ".musicxml"),
                                                  only_audible=not args.all_tracks)
            print(path)
    return status


def check_quiet(song: Song) -> int:
    return sum(1 for part in song.tracks if not part.is_audio and not validate_track_text(
        part.text, song.patterns, default_octave=part.instrument.default_octave)[0])


def check_main(argv=None) -> int:
    return main(argv, command="check")


def midi_main(argv=None) -> int:
    return main(argv, command="midi")


def musicxml_main(argv=None) -> int:
    return main(argv, command="musicxml")


def abc_main(argv=None) -> int:
    return main(argv, command="abc")


if __name__ == "__main__":
    sys.exit(main())
