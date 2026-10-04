# ST-language conformance suite

`cases.json` lists test cases for the [ST-language specification](../ST-language.md).
A parser conforms to version 2.0 if it gives, for every case, the result
under `expect`.

```json
{"spec_version": "2.0", "cases": [
  {"id": "notes-basic", "input": "c d e f g a b",
   "expect": {"events": [{"start": 0.0, "duration": 1.0, "kind": "note",
                          "velocity": 80, "letter": "c", "octave": 4}, ...]}},
  {"id": "error-unclosed-block", "input": "c [d e", "expect": {"error": true}},
  {"id": "warning-bar-missing", "input": "4: c d e | f g a b |",
   "expect": {"events": [...], "warnings": [{"start": 9, "end": 10, "bar": 1}]}}
]}
```

Each case has:

- `input`: a track text (section 2 of the specification);
- optional `patterns` (`{"Name": "tokens"}`), `octave` (default octave,
  4 if absent), `time_sig` (meter, `"4/4"` if absent) and
  `metrica_changes` (`[[bar, "N/D"], ...]`);
- `expect`: either `{"error": true}` (the text is invalid, section 10.1)
  or `{"events": [...]}` with the events of section 11 in interpretation
  order, plus `"warnings"` when there are any (section 10.2).

Event fields: those of section 11 that are not empty; `voice` only when
it is not 1; block atoms (`items`) without their `mult`; numbers rounded
to 9 decimals (compare with a tolerance of 10⁻⁹). Warnings give the
character range of the token they refer to (`start`, `end`, in the
original text, comments included) and the bar number (0 for lyrics).
Message texts are not part of the suite.

`make_cases.py` regenerates `cases.json` from the reference
implementation; it is run only when the language changes on purpose, and
the test `tests/test_st_language.py` checks that the implementation still
gives exactly these results.

---

La suite di conformita' di ST-language: per ogni caso, il risultato che un
parser conforme alla versione 2.0 deve dare (vedi la [specifica in
italiano](../ST-language.it.md), sezione 14). Formato dei casi descritto
sopra, in inglese.
