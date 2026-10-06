# Messaggi della libreria in inglese nei test, qualunque sia la lingua del sistema.
import os
import sys

os.environ["ST_LANGUAGE"] = "en"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
