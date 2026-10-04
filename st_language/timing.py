"""
Mappa di tempo (BPM) e metrica in funzione del beat assoluto (quarti) del
progetto, unificando le due sorgenti di cambi possibili:
  1) l'elenco Tempo:/Metrica: per battuta dell'intestazione del progetto
     (project.tempo_changes / project.metrica_changes);
  2) i marcatori di tempo inline (tempo=120) presenti nelle tracce (solo tempo,
     non esiste un equivalente inline per la metrica).

Usata sia dall'esportazione MIDI (core.midi_export, che lavora in tick) sia
dalla GUI durante la riproduzione (barra di avanzamento, campi Tempo/Metrica
e metronomo, che lavorano in beat/secondi) cosi' che i cambi dichiarati nel
progetto abbiano sempre lo stesso effetto in entrambi i percorsi.
"""

import re
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:          # solo per le annotazioni (nessun import circolare)
    from .song import Part, Song  # noqa: F401


RE_METRICA_VALUE = re.compile(r"^\s*(\d+)\s*/\s*(\d+)\s*$")


def compute_bar_beat_offsets(tempo_changes, metrica_changes, base_time_sig: str = "4/4") -> Dict[int, float]:
    """Calcola, per ogni numero di battuta dichiarato in tempo_changes o
    metrica_changes, il beat (quarti) assoluto in cui quella battuta inizia,
    simulando l'accumulo delle durate di battuta (dipendenti dalla metrica
    attiva in quel momento) dalla battuta 1 in poi. La battuta 1 e' sempre
    beat 0.0. base_time_sig e' la metrica in vigore fino al primo cambio
    dichiarato (project.time_sig), usata solo se metrica_changes e' vuota:
    con una metrica singola ('Metrica: 3/4') le battute verrebbero
    altrimenti contate in 4/4."""
    declared_bars = sorted({b for b, _ in tempo_changes} | {b for b, _ in metrica_changes} | {1})
    if not declared_bars:
        return {1: 0.0}

    metrica_map = dict(metrica_changes)
    max_bar = max(declared_bars)

    offsets = {1: 0.0}
    # Con una lista di cambi che non parte dalla battuta 1, project.time_sig
    # vale il primo cambio (vedi parse_project_text), non la metrica delle
    # battute precedenti: li' resta il 4/4 di default, come nell'export MIDI.
    current_sig = metrica_map.get(1, "4/4" if metrica_changes else (base_time_sig or "4/4"))
    beat_acc = 0.0
    bar = 1
    while bar < max_bar:
        if bar in metrica_map:
            current_sig = metrica_map[bar]
        num, den = current_sig.split("/")
        bar_length_beats = int(num) * 4.0 / int(den)
        beat_acc += bar_length_beats
        bar += 1
        offsets[bar] = beat_acc
    return offsets


def build_tempo_beat_map(project: "Song", tracks=None, midi_dir: Optional[str] = None,
                          events_by_track=None) -> List[Tuple[float, int]]:
    """Elenco ordinato (beat, bpm) di ogni punto in cui il tempo cambia,
    combinando i cambi per battuta e i marcatori inline di tutte le tracce
    considerate (di default le tracce udibili del progetto).

    events_by_track permette di riusare eventi gia' parsati dal chiamante
    (core.midi_export, che ne ha comunque bisogno per il resto dell'export)
    invece di riparsarli qui."""
    if tracks is None:
        tracks = project.audible_tracks()

    points = {}
    bar_offsets = compute_bar_beat_offsets(project.tempo_changes, project.metrica_changes,
                                           project.time_sig)
    for bar, bpm in project.tempo_changes:
        points[bar_offsets.get(bar, 0.0)] = bpm
    if not project.tempo_changes:
        points[0.0] = project.tempo_bpm

    for track in tracks:
        events = (events_by_track.get(track.name, []) if events_by_track is not None
                  else track.parsed_events(project.patterns, midi_dir=midi_dir))
        for ev in events:
            if ev.kind == "tempo_marker" and ev.bpm:
                points[ev.start] = ev.bpm

    return sorted(points.items())


def build_metrica_beat_map(project: "Song") -> List[Tuple[float, str]]:
    """Elenco ordinato (beat, "N/D") di ogni punto in cui la metrica cambia,
    a partire dai cambi per battuta dichiarati nell'intestazione del
    progetto (nessun marcatore inline esiste per la metrica)."""
    bar_offsets = compute_bar_beat_offsets(project.tempo_changes, project.metrica_changes,
                                           project.time_sig)
    points = {}
    for bar, sig in project.metrica_changes:
        points[bar_offsets.get(bar, 0.0)] = sig
    if not project.metrica_changes:
        points[0.0] = project.time_sig
    return sorted(points.items())


def value_at_beat(beat_map: List[Tuple[float, object]], beat: float):
    """Ultimo valore di beat_map (lista ordinata (beat, valore)) dichiarato
    a un beat <= beat; il primo valore se beat precede il primo punto. None
    se beat_map e' vuota."""
    if not beat_map:
        return None
    result = beat_map[0][1]
    for b, v in beat_map:
        if b <= beat:
            result = v
        else:
            break
    return result


def beat_at_elapsed_seconds(tempo_beat_map: List[Tuple[float, int]], start_beat: float,
                             elapsed_seconds: float) -> float:
    """Beat assoluto raggiunto dopo elapsed_seconds di riproduzione reale a
    partire da start_beat, integrando i cambi di tempo dichiarati in
    tempo_beat_map: necessario perche' la conversione beat<->secondi non e'
    piu' lineare quando il tempo cambia durante l'esecuzione (senza questo,
    barra di avanzamento, evidenziazione ed eventuale metronomo andrebbero
    fuori sincrono ad ogni cambio di tempo)."""
    if not tempo_beat_map or elapsed_seconds <= 0:
        return start_beat

    idx = 0
    for i, (b, _bpm) in enumerate(tempo_beat_map):
        if b <= start_beat:
            idx = i
        else:
            break

    current_beat = start_beat
    remaining = elapsed_seconds
    while idx < len(tempo_beat_map):
        bpm = max(1, tempo_beat_map[idx][1])
        next_change_beat = tempo_beat_map[idx + 1][0] if idx + 1 < len(tempo_beat_map) else None
        if next_change_beat is None:
            return current_beat + remaining * bpm / 60.0
        beats_available = next_change_beat - current_beat
        if beats_available <= 0:
            idx += 1
            continue
        seconds_available = beats_available * 60.0 / bpm
        if remaining <= seconds_available:
            return current_beat + remaining * bpm / 60.0
        remaining -= seconds_available
        current_beat = next_change_beat
        idx += 1
    return current_beat


def seconds_for_beats(tempo_beat_map: List[Tuple[float, int]], total_beats: float) -> float:
    """Durata in secondi dei primi total_beats beat del brano, integrando i
    cambi di tempo dichiarati in tempo_beat_map (inverso di
    beat_at_elapsed_seconds, usato per formattare barra/etichette mm:ss)."""
    if not tempo_beat_map or total_beats <= 0:
        return 0.0
    total_seconds = 0.0
    for i, (b, bpm) in enumerate(tempo_beat_map):
        if b >= total_beats:
            break
        next_change_beat = tempo_beat_map[i + 1][0] if i + 1 < len(tempo_beat_map) else total_beats
        seg_end = min(next_change_beat, total_beats)
        total_seconds += max(0.0, seg_end - b) * 60.0 / max(1, bpm)
    return total_seconds


def click_grid_position(metrica_beat_map: List[Tuple[float, str]], beat: float) -> Tuple[float, bool]:
    """Ritorna (beat_del_prossimo_click, accento) per il metronomo: il primo
    click della griglia a partire da (e incluso) `beat`. La griglia e'
    allineata alla battuta che inizia a ciascun cambio di metrica dichiarato
    (o all'origine, beat 0.0): un click per ogni unita' del denominatore
    (es. 4/4 -> 4 click di un quarto, 6/8 -> 6 click di un ottavo), il primo
    di ogni battuta accentato."""
    seg_start, sig = metrica_beat_map[0] if metrica_beat_map else (0.0, "4/4")
    for b, s in metrica_beat_map:
        if b <= beat:
            seg_start, sig = b, s
        else:
            break

    m = RE_METRICA_VALUE.match(sig) if sig else None
    num, den = (int(m.group(1)), int(m.group(2))) if m else (4, 4)
    num = max(1, num)
    den = max(1, den)
    click_len = 4.0 / den

    k = max(0, round((beat - seg_start) / click_len))
    next_click_beat = seg_start + k * click_len
    while next_click_beat < beat - 1e-9:
        k += 1
        next_click_beat = seg_start + k * click_len

    accent = (k % num) == 0
    return next_click_beat, accent
