"""
Prova la libreria st_language INSTALLATA (pip install st-language, una
wheel, uno sdist): i casi della suite di conformita' e i comandi da
terminale. Non usa il codice della cartella del repository.

    pip install dist/st_language-2.5.0-py3-none-any.whl
    python docs/spec/conformance/run_installed.py

Esce con 0 se tutto e' uguale all'atteso, con 1 altrimenti.
"""

import json
import os
import shutil
import subprocess
import sys
import sysconfig
import tempfile

os.environ["ST_LANGUAGE_INSTALLED"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
# la cartella del repository non deve essere in sys.path: altrimenti si
# proverebbe il sorgente e non il pacchetto installato
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path[:] = [p for p in sys.path if os.path.abspath(p or os.getcwd()) not in (REPO, HERE)]
sys.path.append(HERE)

import st_language as st  # noqa: E402
from make_cases import run_case  # noqa: E402

SONG = """Tempo: 100 BPM
Tonalita: Am

Traccia Piano [Piano]:
  4: Am F | C G | rel: c d e f | 2g 2g |

Traccia Batteria [Drums]:
  4: kick snare kick snare | kick snare kick snare |
"""


def main() -> int:
    where = os.path.abspath(st.__file__)
    if os.path.abspath(REPO) in where and "site-packages" not in where:
        print(f"ERRORE: st_language viene dal repository ({where}), non da un'installazione")
        return 1
    print(f"st_language {st.__version__} da {where}")
    failures = 0

    with open(os.path.join(HERE, "cases.json"), encoding="utf-8") as f:
        suite = json.load(f)
    for case in suite["cases"]:
        options = {k: v for k, v in case.items() if k not in ("id", "input", "expect")}
        if run_case(case["input"], options) != case["expect"]:
            failures += 1
            print("CASO DIVERSO:", case["id"])
    print(f"conformita' (specifica {suite['spec_version']}): {len(suite['cases']) - failures}/{len(suite['cases'])} casi")

    tmp = tempfile.mkdtemp()
    try:
        song = os.path.join(tmp, "prova.st")
        with open(song, "w", encoding="utf-8") as f:
            f.write(SONG)
        commands = [
            ("st-language", ["check", song]),
            ("stcheck", [song]),
            ("st2mid", [song, "-o", os.path.join(tmp, "a.mid")]),
            ("st2musicxml", [song, "-o", os.path.join(tmp, "a.musicxml")]),
            ("st2abc", [song, "-o", os.path.join(tmp, "a.abc")]),
            ("st2mtxt", [song, "-o", os.path.join(tmp, "a.mtxt")]),
            ("st-language", ["mtxt", os.path.join(tmp, "a.mtxt"), "-o", os.path.join(tmp, "b.mid")]),
            ("st-language", ["events", song]),
        ]
        # i comandi stanno nella cartella degli script dell'installazione
        # (su Windows e' Scripts, accanto a python.exe solo nei venv)
        scripts = os.pathsep.join([sysconfig.get_path("scripts"), os.path.dirname(sys.executable)])
        for command, args in commands:
            exe = shutil.which(command, path=scripts + os.pathsep + os.environ.get("PATH", ""))
            if not exe:
                failures += 1
                print("COMANDO NON INSTALLATO:", command)
                continue
            out = subprocess.run([exe] + args, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=tmp)
            if out.returncode != 0:
                failures += 1
                print(f"COMANDO FALLITO: {command} {' '.join(args[:1])}\n{out.stdout}{out.stderr}")
        for name, magic in (("a.mid", b"MThd"), ("b.mid", b"MThd")):
            path = os.path.join(tmp, name)
            if not os.path.exists(path) or open(path, "rb").read(4) != magic:
                failures += 1
                print("FILE NON VALIDO:", name)
        for name, start in (("a.musicxml", "<?xml"), ("a.abc", "X:1"), ("a.mtxt", "mtxt 1.0")):
            path = os.path.join(tmp, name)
            if not os.path.exists(path) or not open(path, encoding="utf-8").read().startswith(start):
                failures += 1
                print("FILE NON VALIDO:", name)
        print(f"comandi da terminale: {len(commands)} provati")

        # in italiano, come per il resto: i messaggi si traducono
        out = subprocess.run([sys.executable, "-m", "st_language", "check", "-", "--lang", "it"],
                             input="c [d", capture_output=True, text=True, encoding="utf-8", errors="replace",
                             cwd=tmp)
        if out.returncode != 1 or "errore" not in out.stdout:
            failures += 1
            print("MESSAGGI TRADOTTI NON TROVATI (locales mancanti nel pacchetto?)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("OK" if not failures else f"{failures} problemi")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
