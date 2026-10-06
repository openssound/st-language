// Sinfonia n. 2 in Do minore, "Tempesta e quiete": una sinfonia lunga in quattro tempi.
//
// Musica originale, scritta per mostrare ST-language su larga scala: 288
// battute e 12 tracce, circa dieci minuti. L'orchestra e' la stessa della
// "Sinfonia n. 1" (legni, corni e tromba, timpani, archi), ma qui le forme
// sono piu' ampie e il materiale tematico viene trasformato. Ogni tema e'
// scritto una volta sola: le riprese in altre tonalita' e in altre ottave sono
// la stessa riga con la trasposizione (`%Tema-3`, `%Tema-12`), e le entrate
// delle parti sono ancore di battuta (`bar=41`).
//
//   I    Largo - Allegro con fuoco   Do minore  (120 battute)
//        introduzione lenta; esposizione con due temi (il secondo in Mi bemolle
//        maggiore) e codetta; sviluppo di tre sezioni (sequenze, il secondo
//        tema che scende, la lunga attesa sulla dominante); ripresa, con il
//        secondo tema ora in Do maggiore, e coda trionfale
//   II   Andante                      La bemolle maggiore (40 battute)
//        canto dell'oboe, variazione ornamentata dei violini, episodio in
//        Fa minore, il tema ai violoncelli, coda con la corona
//   III  Scherzo: Presto - Trio - Da capo   Do minore / Do maggiore (48 battute)
//        scherzo staccato con la seconda parte nella dominante, trio pastorale,
//        ripresa dello scherzo
//   IV   Finale: Allegro maestoso     Do maggiore (80 battute)
//        fanfara, tema in Do e in Sol, fugato a otto entrate (violoncelli,
//        viole, violini secondi e primi, oboe, flauto, corni, tromba), corale
//        degli ottoni, stretta con accelerando e coda con il rallentando
//
// Cosa c'e' dentro:
//   - le tonalita' che cambiano da un tempo all'altro e dentro un tempo
//     (Do minore, Mi bemolle, La bemolle, Fa minore, Sol minore, Do, Sol): ogni
//     pattern ha il suo key=, e le alterazioni si scrivono solo quando servono;
//   - la trasposizione: `%Nome+N` suona un pattern N semitoni sopra o sotto
//     (il secondo tema scritto in Mi bemolle torna in Do con `%TemaB-3`, un
//     tema all'ottava con `+12` / `-12`, la seconda parte dello scherzo e il
//     tema del finale in Sol con `+7`); le alterazioni seguono la tonalita'
//     del pattern (`key=`) trasportata;
//   - le ancore di battuta: ogni parte che entra dopo una pausa lo dice con
//     `bar=N` invece di contare le battute di silenzio;
//   - le sequenze dello sviluppo: un motivo di due battute richiamato a
//     tonalita' diverse (`%Motivo %Motivo-7 %Motivo-2 %Motivo+3`);
//   - il fugato: un soggetto di due battute che entra otto volte, a battute
//     sfalsate e nell'ottava adatta a ciascun strumento;
//   - i cambi di tempo tra i movimenti e dentro (tempo=: Largo 60, Allegro 138,
//     Andante 66, Presto 160, Trio 132, Finale 126, Stretta 150) e il rallentando
//     finale con tempo=150 << ... tempo=54;
//   - le dinamiche: crescendo di volume nello sviluppo (vol=60 >> ... vol=100),
//     indicazioni di testo ($"Largo", $"Trio", $"Da capo", $"Stretta") e le corone;
//   - strumenti definiti nel file con il programma General MIDI;
//   - i pattern degli accompagnamenti (accordi tenuti, arpeggi, bassi, accordi
//     staccati, rulli e colpi di timpano) senza velocity: la dinamica la
//     decide la traccia (`90@ %Arp_IA`), cosi' lo stesso pattern serve piu' volte.

ST: 2.6
Tempo: 60 BPM
Metrica: 4/4
Tonalita: Cm

Strumento Flauto:
  program=73 percussione=no ottava=5 range=72-100 poly=no voicing=monophonic

Strumento Oboe:
  program=68 percussione=no ottava=5 range=52-96 poly=no voicing=monophonic

Strumento Clarinetto:
  program=71 percussione=no ottava=4 range=50-94 poly=no voicing=monophonic

Strumento Fagotto:
  program=70 percussione=no ottava=3 range=34-72 poly=no voicing=monophonic

Strumento Corni:
  program=60 percussione=no ottava=4 range=41-77 poly=si voicing=spread

Strumento Timpani:
  program=47 percussione=no ottava=2 range=28-60 poly=no voicing=monophonic

Strumento Violini1:
  program=48 percussione=no ottava=5 range=55-103 poly=no voicing=monophonic

Strumento Violini2:
  program=48 percussione=no ottava=5 range=55-103 poly=no voicing=monophonic

Strumento Viole:
  program=48 percussione=no ottava=4 range=48-91 poly=si voicing=spread

Strumento Violoncelli:
  program=42 percussione=no ottava=3 range=36-76 poly=no voicing=monophonic

Strumento Contrabbassi:
  program=43 percussione=no ottava=2 range=28-60 poly=no voicing=monophonic


// ================================================================ temi

Pattern %I_Largo:
  key=Cm 8:
  4c*5 2g*5 2e*5 |
  4a*5 2e*6 2c*6 |
  4f*5 2a*5 2c*6 |
  4d*6 2bn*5 2g*5 |
  4c*6 2g*5 2e*5 |
  4a*5 2c*6 2e*6 |
  2f*6 e*6 d*6 2c*6 2a*5 |
  4d*6 4r |

Pattern %I_TemaA:
  key=Cm 8:
  2c*5 e*5 g*5 2c*6 2b*5 |
  a*5 g*5 f*5 e*5 4g*5 |
  2f*5 a*5 c*6 2f*6 2e*6 |
  d*6 c*6 bn*5 d*6 4g*5 |
  2c*5 e*5 g*5 2c*6 2e*6 |
  a*5 c*6 e*6 a*6 4g*6 |
  2f*6 d*6 bn*5 2d*6 2f*6 |
  4c*6 4r |

Pattern %I_TemaA2:
  key=Cm 8:
  c*5 e*5 g*5 e*5 2c*6 2b*5 |
  a*5 g*5 f*5 e*5 2g*5 2c*5 |
  f*5 a*5 c*6 a*5 2f*6 2e*6 |
  d*6 c*6 bn*5 c*6 2d*6 2g*5 |
  c*5 e*5 g*5 e*5 2c*6 2e*6 |
  a*5 c*6 e*6 c*6 2a*6 2g*6 |
  f*6 e*6 d*6 bn*5 2d*6 2f*6 |
  6c*6 2r |

Pattern %I_PonteMotivo:
  key=Cm 8:
  2g*5 c*6 e*6 2g*6 2f*6 |
  d*6 bn*5 g*5 d*6 4bn*5 |

Pattern %I_TemaB:
  key=Eb 8:
  2g*5 b*5 e*6 2d*6 2b*5 |
  2d*6 f*6 b*6 2g*6 2f*6 |
  2e*6 g*6 e*6 2c*6 2g*5 |
  2a*5 c*6 e*6 2a*6 2g*6 |
  2g*5 b*5 e*6 2g*6 2b*6 |
  2a*6 f*6 c*6 2a*5 2c*6 |
  d*6 f*6 a*6 f*6 2d*6 2b*5 |
  4e*6 4r |

Pattern %I_TemaB2:
  key=Eb 8:
  g*5 b*5 e*6 g*6 2b*6 2g*6 |
  d*6 f*6 b*6 f*6 2d*6 2b*5 |
  e*6 g*6 e*6 c*6 2g*5 2e*5 |
  a*5 c*6 e*6 c*6 2a*5 2e*5 |
  g*5 b*5 e*6 b*5 2g*5 2e*6 |
  a*6 f*6 c*6 f*6 2a*5 2c*6 |
  d*6 f*6 a*6 f*6 2d*6 2f*6 |
  4e*6 2g*6 2b*6 |

Pattern %I_Codetta:
  key=Eb 8:
  b*6 a*6 g*6 f*6 e*6 d*6 2c*6 |
  b*5 c*6 d*6 e*6 2f*6 2d*6 |
  a*5 f*5 a*5 c*6 2f*6 2e*6 |
  d*6 f*6 a*6 f*6 4d*6 |
  2e*6 g*6 b*6 2g*6 2e*6 |
  2a*5 c*6 e*6 2a*6 2c*6 |
  d*6 c*6 b*5 a*5 2g*5 2f*5 |
  4e*5 4r |

Pattern %I_SvilMotivoA:
  key=Cm 8:
  2c*5 e*5 g*5 2c*6 2b*5 |
  a*5 g*5 f*5 e*5 4g*5 |

Pattern %I_SvilMotivoB:
  key=Eb 8:
  2g*5 b*5 e*6 2d*6 2b*5 |
  2d*6 f*6 b*6 2g*6 2f*6 |

Pattern %I_Attesa:
  key=Cm 8:
  4a*5 4c*6 |
  4a*5 4f*5 |
  4d*6 4bn*5 |
  4g*5 4d*6 |
  d*6 bn*5 d*6 bn*5 d*6 bn*5 d*6 bn*5 |
  d*6 g*5 d*6 g*5 d*6 g*5 d*6 g*5 |
  2d*6 2f*6 2g*6 2bn*6 |
  4g*5 4r |

Pattern %I_Coda:
  key=C 8:
  2c*6 e*6 g*6 2g*6 2e*6 |
  2a*5 c*6 f*6 2a*6 2f*6 |
  2g*5 b*5 d*6 2g*6 2f*6 |
  4e*6 2g*6 2c*6 |
  2a*5 c*6 e*6 2a*6 2e*6 |
  2f*6 a*6 f*6 2c*6 2a*5 |
  g*5 b*5 d*6 f*6 2g*6 2d*6 |
  8c*6$fermata |

Pattern %II_Canto:
  key=Ab 8:
  4c*6 2e*6 2a*5 |
  4g*5 2b*5 2e*6 |
  4a*5 2c*6 2f*6 |
  4d*6 2f*6 2a*5 |
  4c*6 2e*6 2c*6 |
  4b*5 2d*6 2f*6 |
  4g*5 2b*5 2d*6 |
  4a*5 4r |

Pattern %II_Variazione:
  key=Ab 8:
  c*6 d*6 e*6 c*6 2a*5 2e*6 |
  g*5 a*5 b*5 g*5 2e*6 2b*5 |
  a*5 b*5 c*6 a*5 2f*6 2c*6 |
  d*6 e*6 f*6 d*6 2a*5 2f*6 |
  c*6 e*6 a*6 g*6 2f*6 2e*6 |
  b*5 d*6 f*6 d*6 2b*5 2d*6 |
  g*5 b*5 d*6 b*5 2g*5 2b*5 |
  4a*5 4r |

Pattern %II_Episodio:
  key=Fm 8:
  4f*5 2a*5 2c*6 |
  4en*6 2g*6 2b*5 |
  2f*6 e*6 d*6 2c*6 2a*5 |
  4d*6 2f*6 2a*5 |
  4b*5 2d*6 2f*6 |
  2g*5 b*5 en*6 2g*6 2b*5 |
  4a*5 2c*6 2f*6 |
  4g*5 4r |

Pattern %II_Coda:
  key=Ab 8:
  4d*6 2f*6 2a*5 |
  4b*5 2d*6 2f*6 |
  4g*5 2b*5 2d*6 |
  4c*6 2e*6 2a*5 |
  4a*5 2c*6 2f*6 |
  4d*6 2f*6 2a*6 |
  2g*6 b*6 g*6 2d*6 2b*5 |
  8a*5$fermata |

Pattern %III_Scherzo:
  key=Cm 8:
  c*5 e*5 g*5 e*5 c*5 e*5 2g*5 |
  c*6 b*5 a*5 g*5 2f*5 2e*5 |
  d*5 f*5 g*5 f*5 d*5 f*5 2bn*5 |
  2c*6 2g*5 2e*5 2c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 2c*6 |
  e*5 g*5 c*6 g*5 e*5 g*5 2c*6 |
  d*6 c*6 bn*5 g*5 d*5 g*5 2bn*5 |
  4c*5 4r |

Pattern %III_Trio:
  key=C 8:
  2e*5 g*5 c*6 2e*6 2g*5 |
  2d*6 c*6 b*5 2c*6 2e*6 |
  2d*5 g*5 b*5 2d*6 2b*5 |
  4c*6 2g*5 2e*5 |
  2f*5 a*5 c*6 2f*6 2a*5 |
  2e*5 g*5 c*6 2e*6 2c*6 |
  2d*6 b*5 g*5 2f*5 2d*5 |
  4c*5 4r |

Pattern %IV_Fanfara:
  key=C 8:
  c*5 e*5 g*5 c*6 2e*6 2g*5 |
  4c*6 4r |
  d*5 g*5 b*5 d*6 2g*6 2d*6 |
  4g*5 4r |
  e*5 a*5 c*6 e*6 2a*6 2e*6 |
  f*5 a*5 c*6 f*6 2a*6 2c*6 |
  d*6 b*5 g*5 f*5 2d*5 2g*5 |
  4g*5 4r |

Pattern %IV_Tema:
  key=C 8:
  c*6 c*6 e*6 g*6 2c*6 2g*5 |
  d*6 d*6 g*6 b*5 2d*6 2g*5 |
  e*6 e*6 a*6 c*6 2e*6 2a*5 |
  g*5 b*5 e*6 g*6 2b*5 2e*6 |
  f*6 f*6 a*6 c*6 2f*6 2c*6 |
  e*6 g*6 c*6 e*6 2g*6 2e*6 |
  d*6 f*6 a*6 f*6 2d*6 2f*6 |
  g*5 b*5 d*6 f*6 4g*6 |

Pattern %IV_Stretta:
  key=C 8:
  c*5 d*5 e*5 f*5 g*5 a*5 b*5 c*6 |
  c*6 b*5 a*5 g*5 f*5 e*5 d*5 c*5 |
  f*5 a*5 c*6 f*6 c*6 a*5 f*5 a*5 |
  a*5 c*6 f*6 a*6 f*6 c*6 a*5 f*5 |
  g*5 b*5 d*6 g*6 d*6 b*5 g*5 b*5 |
  d*6 g*6 b*6 g*6 d*6 g*6 b*6 g*6 |
  c*6 e*6 g*6 e*6 c*6 e*6 g*6 e*6 |
  g*5 b*5 d*6 f*6 4g*6 |

Pattern %IV_Coda:
  key=C 8:
  2c*6 e*6 g*6 4c*6 |
  2a*5 c*6 f*6 4a*6 |
  2g*5 b*5 d*6 4g*6 |
  4e*6 4c*6 |
  2d*6 f*6 a*6 4f*6 |
  2d*6 b*5 g*5 4d*6 |
  4c*6 4e*6 |
  8c*6$fermata |

Pattern %IV_Soggetto:
  key=C 8:
  c*5 d*5 e*5 f*5 2g*5 2e*5 |
  a*5 g*5 f*5 e*5 2d*5 2c*5 |

Pattern %IV_CoraleA:
  key=C 8:
  4e*5 4g*5 |
  4g*5 4d*6 |
  4c*6 4e*6 |
  4d*6 4g*5 |
  4a*5 4c*6 |
  4g*5 4e*5 |
  4f*5 4a*5 |
  4g*5 4d*6 |

Pattern %IV_CoraleB:
  key=C 8:
  4e*6 4c*6 |
  4b*5 4g*5 |
  4a*5 4c*6 |
  4e*6 4g*6 |
  4f*6 4d*6 |
  4d*6 4bn*5 |
  4c*6 4e*6 |
  6g*5 2r |

// ================================================================ accompagnamenti

Pattern %Arp_I0:
  key=Cm 8:
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |

Pattern %Arp_IB:
  key=Eb 8:
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 | b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 | f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  b*4 d*5 f*5 a*5 f*5 d*5 f*5 d*5 | e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |

Pattern %Arp_IB_C:
  key=C 8:
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 | f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %Arp_IIA:
  key=Ab 8:
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 | e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 | b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  e*5 g*5 b*5 d*6 b*5 g*5 b*5 g*5 | a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |

Pattern %Arp_IIB:
  key=Fm 8:
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 | c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |

Pattern %Arp_IITR:
  key=C 8:
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %Acc_IVFUG_8_16:
  key=C 4:
  C'1 | Am'1 |
  Dm'1 | G7'1 |
  C'1 | F'1 |
  G7'1 | G7'1 |

Pattern %Acc_I0:
  key=Cm 4:
  Cm'1 | Ab'1 |
  Fm'1 | G7'1 |
  Cm'1 | Ab'1 |
  Fm'1 | G7'1 |

Pattern %Arp_IA:
  key=Cm 8:
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %Arp_I3:
  key=Cm 8:
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |
  b*4 db*5 f*5 db*5 b*4 db*5 f*5 db*5 | f*5 an*5 c*6 e*6 c*6 an*5 c*6 an*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 | b*4 d*5 f*5 a*5 f*5 d*5 f*5 d*5 |

Pattern %Arp_ICOD:
  key=Eb 8:
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 | a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | b*4 d*5 f*5 a*5 f*5 d*5 f*5 d*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 | a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  b*4 d*5 f*5 a*5 f*5 d*5 f*5 d*5 | e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |

Pattern %Arp_IDEV1:
  key=Cm 8:
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 | d*5 f#*5 an*5 c*6 an*5 f#*5 an*5 f#*5 |
  b*4 db*5 f*5 db*5 b*4 db*5 f*5 db*5 | f*5 an*5 c*6 e*6 c*6 an*5 c*6 an*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |

Pattern %Arp_IDEV2:
  key=Cm 8:
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 | b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  db*5 f*5 a*5 f*5 db*5 f*5 a*5 f*5 | a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 | f*5 an*5 c*6 an*5 f*5 an*5 c*6 an*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 | e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |

Pattern %Arp_IDEV3:
  key=Cm 8:
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 | f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 bn*5 d*6 bn*5 g*5 bn*5 d*6 bn*5 | g*5 bn*5 d*6 bn*5 g*5 bn*5 d*6 bn*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 | g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 | g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |

Pattern %Arp_I11:
  key=Cm 8:
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |

Pattern %Arp_ICODA:
  key=C 8:
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 | f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %Acc_IIA:
  key=Ab 4:
  Ab'1 | Eb/G'1 |
  Fm'1 | Db'1 |
  Ab'1 | Bbm'1 |
  Eb7'1 | Ab'1 |

Pattern %Acc_IICOD:
  key=Ab 4:
  Db'1 | Bbm'1 |
  Eb7'1 | Ab'1 |
  Fm'1 | Db'1 |
  Eb7'1 | Ab'1 |

Pattern %Arp_IIIS:
  key=Cm 8:
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %Arp_IIIS_G:
  key=Gm 8:
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 | g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  d*5 f#*5 a*5 c*6 a*5 f#*5 a*5 f#*5 | g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  d*5 f#*5 a*5 c*6 a*5 f#*5 a*5 f#*5 | g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |

Pattern %Acc_IITR:
  key=C 4:
  C'1 | C'1 |
  G'1 | C'1 |
  F'1 | C'1 |
  G7'1 | C'1 |

Pattern %Acc_IITR_G:
  key=G 4:
  G'1 | G'1 |
  D'1 | G'1 |
  C'1 | G'1 |
  D7'1 | G'1 |

Pattern %Arp_IVFAN:
  key=C 8:
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 | g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 | f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 | g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |

Pattern %Arp_IVT:
  key=C 8:
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 | e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 | g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |

Pattern %Arp_IVT_G:
  key=G 8:
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 | d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 | b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 | d*5 f*5 a*5 c*6 a*5 f*5 a*5 f*5 |

Pattern %Arp_IVFUG_6_16:
  key=C 8:
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 | g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 | g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 | g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |

Pattern %Acc_IVCH:
  key=C 4:
  C'1 | G/B'1 |
  Am'1 | C/G'1 |
  F'1 | C/E'1 |
  Dm'1 | G7'1 |
  Am'1 | Em'1 |
  F'1 | C'1 |
  Dm'1 | G7'1 |
  C'1 | G7'1 |

Pattern %Arp_IVSTR:
  key=C 8:
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 | f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 | g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |

Pattern %Arp_IVCOD:
  key=C 8:
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 | g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 | c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %Acc_IA:
  key=Cm 4:
  Cm'1 | Cm'1 |
  Fm'1 | G7'1 |
  Cm'1 | Ab'1 |
  G7'1 | Cm'1 |

Pattern %Acc_I3:
  key=Cm 4:
  Cm'1 | G7'1 |
  Fm'1 | C7'1 |
  Bbm'1 | F7'1 |
  Eb'1 | Bb7'1 |

Pattern %Acc_IB:
  key=Eb 4:
  Eb'1 | Bb/D'1 |
  Cm'1 | Ab'1 |
  Eb'1 | Fm'1 |
  Bb7'1 | Eb'1 |

Pattern %Acc_ICOD:
  key=Eb 4:
  Eb'1 | Ab'1 |
  Fm'1 | Bb7'1 |
  Eb'1 | Ab'1 |
  Bb7'1 | Eb'1 |

Pattern %Acc_IDEV1:
  key=Cm 4:
  Fm'1 | C7'1 |
  Gm'1 | D7'1 |
  Bbm'1 | F7'1 |
  Cm'1 | G7'1 |

Pattern %Acc_IDEV2:
  key=Cm 4:
  Eb'1 | Bb/D'1 |
  Db'1 | Ab/C'1 |
  Bb'1 | F/A'1 |
  Ab'1 | Eb/G'1 |

Pattern %Acc_IDEV3:
  key=Cm 4:
  Ab'1 | Fm'1 |
  G'1 | G'1 |
  G7'1 | G7'1 |
  G7'1 | G7'1 |

Pattern %Acc_I11:
  key=Cm 4:
  Cm'1 | G7'1 |
  Fm'1 | C7'1 |
  Cm'1 | G7'1 |
  Fm'1 | G7'1 |

Pattern %Acc_IB_C:
  key=C 4:
  C'1 | G/B'1 |
  Am'1 | F'1 |
  C'1 | Dm'1 |
  G7'1 | C'1 |

Pattern %Acc_ICODA:
  key=C 4:
  C'1 | F'1 |
  G7'1 | C'1 |
  Am'1 | F'1 |
  G7'1 | C'1 |

Pattern %Acc_IIB:
  key=Fm 4:
  Fm'1 | C7'1 |
  Fm'1 | Db'1 |
  Bbm'1 | C7'1 |
  Fm'1 | C7'1 |

Pattern %Stacco_IIIS:
  key=Cm 4:
  r Cm! r Cm! | r Cm! r Cm! |
  r G7! r G7! | r Cm! r Cm! |
  r Fm! r Fm! | r Cm! r Cm! |
  r G7! r G7! | r Cm! r Cm! |

Pattern %Stacco_IIIS_G:
  key=Gm 4:
  r Gm! r Gm! | r Gm! r Gm! |
  r D7! r D7! | r Gm! r Gm! |
  r Cm! r Cm! | r Gm! r Gm! |
  r D7! r D7! | r Gm! r Gm! |

Pattern %Acc_IVFAN:
  key=C 4:
  C'1 | C'1 |
  G'1 | G'1 |
  Am'1 | F'1 |
  G7'1 | G7'1 |

Pattern %Acc_IVT:
  key=C 4:
  C'1 | G/B'1 |
  Am'1 | Em'1 |
  F'1 | C/E'1 |
  Dm'1 | G7'1 |

Pattern %Acc_IVT_G:
  key=G 4:
  G'1 | D/F#'1 |
  Em'1 | Bm'1 |
  C'1 | G/B'1 |
  Am'1 | D7'1 |

Pattern %Acc_IVFUG_4_16:
  key=C 4:
  C'1 | C'1 |
  G'1 | G'1 |
  C'1 | Am'1 |
  Dm'1 | G7'1 |
  C'1 | F'1 |
  G7'1 | G7'1 |

Pattern %Acc_IVSTR:
  key=C 4:
  C'1 | C'1 |
  F'1 | F'1 |
  G'1 | G'1 |
  C'1 | G7'1 |

Pattern %Acc_IVCOD:
  key=C 4:
  C'1 | F'1 |
  G7'1 | C'1 |
  Dm'1 | G7'1 |
  C'1 | C'1 |

Pattern %Radici_I0:
  key=Cm 4:
  c*2'1 | a*2'1 |
  f*2'1 | g*2'1 |
  c*2'1 | a*2'1 |
  f*2'1 | g*2'1 |

Pattern %Celli_IA:
  key=Cm 4:
  c*2 c*3 c*2 c*3 | c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 | g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 | a*2 a*3 a*2 a*3 |
  g*2 g*3 g*2 g*3 | c*2 c*3 c*2 c*3 |

Pattern %Celli_I3:
  key=Cm 4:
  c*2 c*3 c*2 c*3 | g*2 g*3 g*2 g*3 |
  f*2 f*3 f*2 f*3 | c*2 c*3 c*2 c*3 |
  b*2 b*3 b*2 b*3 | f*2 f*3 f*2 f*3 |
  e*2 e*3 e*2 e*3 | b*2 b*3 b*2 b*3 |

Pattern %Celli_IB:
  key=Eb 4:
  e*2 e*3 e*2 e*3 | d*2 d*3 d*2 d*3 |
  c*2 c*3 c*2 c*3 | a*2 a*3 a*2 a*3 |
  e*2 e*3 e*2 e*3 | f*2 f*3 f*2 f*3 |
  b*2 b*3 b*2 b*3 | e*2 e*3 e*2 e*3 |

Pattern %Celli_ICOD:
  key=Eb 4:
  e*2 e*3 e*2 e*3 | a*2 a*3 a*2 a*3 |
  f*2 f*3 f*2 f*3 | b*2 b*3 b*2 b*3 |
  e*2 e*3 e*2 e*3 | a*2 a*3 a*2 a*3 |
  b*2 b*3 b*2 b*3 | e*2 e*3 e*2 e*3 |

Pattern %Celli_IDEV1:
  key=Cm 4:
  f*2 f*3 f*2 f*3 | c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 | d*2 d*3 d*2 d*3 |
  b*2 b*3 b*2 b*3 | f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 | g*2 g*3 g*2 g*3 |

Pattern %Celli_IDEV2:
  key=Cm 4:
  e*2 e*3 e*2 e*3 | d*2 d*3 d*2 d*3 |
  db*2 db*3 db*2 db*3 | c*2 c*3 c*2 c*3 |
  b*2 b*3 b*2 b*3 | an*2 an*3 an*2 an*3 |
  a*2 a*3 a*2 a*3 | g*2 g*3 g*2 g*3 |

Pattern %Celli_IDEV3:
  key=Cm 4:
  a*2 a*3 a*2 a*3 | f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 | g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 | g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 | g*2 g*3 g*2 g*3 |

Pattern %Celli_I11:
  key=Cm 4:
  c*2 c*3 c*2 c*3 | g*2 g*3 g*2 g*3 |
  f*2 f*3 f*2 f*3 | c*2 c*3 c*2 c*3 |
  c*2 c*3 c*2 c*3 | g*2 g*3 g*2 g*3 |
  f*2 f*3 f*2 f*3 | g*2 g*3 g*2 g*3 |

Pattern %Celli_IB_C:
  key=C 4:
  c*2 c*3 c*2 c*3 | b*2 b*3 b*2 b*3 |
  a*2 a*3 a*2 a*3 | f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 | d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 | c*2 c*3 c*2 c*3 |

Pattern %Celli_ICODA:
  key=C 4:
  c*2 c*3 c*2 c*3 | f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 | c*2 c*3 c*2 c*3 |
  a*2 a*3 a*2 a*3 | f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 | c*2 c*3 c*2 c*3 |

Pattern %Radici_IIA:
  key=Ab 4:
  a*2'1 | g*2'1 |
  f*2'1 | d*2'1 |
  a*2'1 | b*2'1 |
  e*2'1 | a*2'1 |

Pattern %Celli_IIB:
  key=Fm 4:
  f*2 f*3 f*2 f*3 | c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 | d*2 d*3 d*2 d*3 |
  b*2 b*3 b*2 b*3 | c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 | c*2 c*3 c*2 c*3 |

Pattern %Radici_IICOD:
  key=Ab 4:
  d*2'1 | b*2'1 |
  e*2'1 | a*2'1 |
  f*2'1 | d*2'1 |
  e*2'1 | a*2'1 |

Pattern %Celli_IIIS:
  key=Cm 4:
  c*2 c*3 c*2 c*3 | c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 | c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 | c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 | c*2 c*3 c*2 c*3 |

Pattern %Celli_IIIS_G:
  key=Gm 4:
  g*2 g*3 g*2 g*3 | g*2 g*3 g*2 g*3 |
  d*2 d*3 d*2 d*3 | g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 | g*2 g*3 g*2 g*3 |
  d*2 d*3 d*2 d*3 | g*2 g*3 g*2 g*3 |

Pattern %Radici_IITR:
  key=C 4:
  c*2'1 | c*2'1 |
  g*2'1 | c*2'1 |
  f*2'1 | c*2'1 |
  g*2'1 | c*2'1 |

Pattern %Radici_IITR_G:
  key=G 4:
  g*2'1 | g*2'1 |
  d*2'1 | g*2'1 |
  c*2'1 | g*2'1 |
  d*2'1 | g*2'1 |

Pattern %Celli_IVFAN:
  key=C 4:
  c*2 c*3 c*2 c*3 | c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 | g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 | f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 | g*2 g*3 g*2 g*3 |

Pattern %Celli_IVT:
  key=C 4:
  c*2 c*3 c*2 c*3 | b*2 b*3 b*2 b*3 |
  a*2 a*3 a*2 a*3 | e*2 e*3 e*2 e*3 |
  f*2 f*3 f*2 f*3 | e*2 e*3 e*2 e*3 |
  d*2 d*3 d*2 d*3 | g*2 g*3 g*2 g*3 |

Pattern %Celli_IVT_G:
  key=G 4:
  g*2 g*3 g*2 g*3 | f*2 f*3 f*2 f*3 |
  e*2 e*3 e*2 e*3 | b*2 b*3 b*2 b*3 |
  c*2 c*3 c*2 c*3 | b*2 b*3 b*2 b*3 |
  a*2 a*3 a*2 a*3 | d*2 d*3 d*2 d*3 |

Pattern %Celli_IVFUG_2_16:
  key=C 4:
  g*2 g*3 g*2 g*3 | g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 | c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 | g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 | a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 | g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 | f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 | g*2 g*3 g*2 g*3 |

Pattern %Radici_IVCH:
  key=C 4:
  c*2'1 | b*2'1 |
  a*2'1 | g*2'1 |
  f*2'1 | e*2'1 |
  d*2'1 | g*2'1 |
  a*2'1 | e*2'1 |
  f*2'1 | c*2'1 |
  d*2'1 | g*2'1 |
  c*2'1 | g*2'1 |

Pattern %Celli_IVSTR:
  key=C 4:
  c*2 c*3 c*2 c*3 | c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 | f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 | g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 | g*2 g*3 g*2 g*3 |

Pattern %Celli_IVCOD:
  key=C 4:
  c*2 c*3 c*2 c*3 | f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 | c*2 c*3 c*2 c*3 |
  d*2 d*3 d*2 d*3 | g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 | c*2 c*3 c*2 c*3 |

Pattern %Bassi_I0:
  key=Cm 4:
  c*2'1 | a*1'1 |
  f*1'1 | g*1'1 |
  c*2'1 | a*1'1 |
  f*1'1 | g*1'1 |

Pattern %Bassi_IA:
  key=Cm 4:
  c*2'1 | c*2'1 |
  f*1'1 | g*1'1 |
  c*2'1 | a*1'1 |
  g*1'1 | c*2'1 |

Pattern %Bassi_I3:
  key=Cm 4:
  c*2'1 | g*1'1 |
  f*1'1 | c*2'1 |
  b*1'1 | f*1'1 |
  e*2'1 | b*1'1 |

Pattern %Bassi_IB:
  key=Eb 4:
  e*2'1 | d*2'1 |
  c*2'1 | a*1'1 |
  e*2'1 | f*1'1 |
  b*1'1 | e*2'1 |

Pattern %Bassi_ICOD:
  key=Eb 4:
  e*2'1 | a*1'1 |
  f*1'1 | b*1'1 |
  e*2'1 | a*1'1 |
  b*1'1 | e*2'1 |

Pattern %Bassi_IDEV1:
  key=Cm 4:
  f*1'1 | c*2'1 |
  g*1'1 | d*2'1 |
  b*1'1 | f*1'1 |
  c*2'1 | g*1'1 |

Pattern %Bassi_IDEV2:
  key=Cm 4:
  e*2'1 | d*2'1 |
  db*2'1 | c*2'1 |
  b*1'1 | an*1'1 |
  a*1'1 | g*1'1 |

Pattern %Bassi_IDEV3:
  key=Cm 4:
  a*1'1 | f*1'1 |
  g*1'1 | g*1'1 |
  g*1'1 | g*1'1 |
  g*1'1 | g*1'1 |

Pattern %Bassi_I11:
  key=Cm 4:
  c*2'1 | g*1'1 |
  f*1'1 | c*2'1 |
  c*2'1 | g*1'1 |
  f*1'1 | g*1'1 |

Pattern %Bassi_IB_C:
  key=C 4:
  c*2'1 | b*1'1 |
  a*1'1 | f*1'1 |
  c*2'1 | d*2'1 |
  g*1'1 | c*2'1 |

Pattern %Bassi_ICODA:
  key=C 4:
  c*2'1 | f*1'1 |
  g*1'1 | c*2'1 |
  a*1'1 | f*1'1 |
  g*1'1 | c*2'1 |

Pattern %Bassi_IIA:
  key=Ab 4:
  a*1'1 | g*1'1 |
  f*1'1 | d*2'1 |
  a*1'1 | b*1'1 |
  e*2'1 | a*1'1 |

Pattern %Bassi_IIB:
  key=Fm 4:
  f*1'1 | c*2'1 |
  f*1'1 | d*2'1 |
  b*1'1 | c*2'1 |
  f*1'1 | c*2'1 |

Pattern %Bassi_IICOD:
  key=Ab 4:
  d*2'1 | b*1'1 |
  e*2'1 | a*1'1 |
  f*1'1 | d*2'1 |
  e*2'1 | a*1'1 |

Pattern %Bassi_IIIS:
  key=Cm 4:
  c*2'1 | c*2'1 |
  g*1'1 | c*2'1 |
  f*1'1 | c*2'1 |
  g*1'1 | c*2'1 |

Pattern %Bassi_IIIS_G:
  key=Gm 4:
  g*1'1 | g*1'1 |
  d*2'1 | g*1'1 |
  c*2'1 | g*1'1 |
  d*2'1 | g*1'1 |

Pattern %Bassi_IITR:
  key=C 4:
  c*2'1 | c*2'1 |
  g*1'1 | c*2'1 |
  f*1'1 | c*2'1 |
  g*1'1 | c*2'1 |

Pattern %Bassi_IITR_G:
  key=G 4:
  g*1'1 | g*1'1 |
  d*2'1 | g*1'1 |
  c*2'1 | g*1'1 |
  d*2'1 | g*1'1 |

Pattern %Bassi_IVFAN:
  key=C 4:
  c*2'1 | c*2'1 |
  g*1'1 | g*1'1 |
  a*1'1 | f*1'1 |
  g*1'1 | g*1'1 |

Pattern %Bassi_IVT:
  key=C 4:
  c*2'1 | b*1'1 |
  a*1'1 | e*1'1 |
  f*1'1 | e*1'1 |
  d*2'1 | g*1'1 |

Pattern %Bassi_IVT_G:
  key=G 4:
  g*1'1 | f*1'1 |
  e*1'1 | b*1'1 |
  c*2'1 | b*1'1 |
  a*1'1 | d*2'1 |

Pattern %Bassi_IVFUG:
  key=C 4:
  c*2'1 | c*2'1 |
  g*1'1 | g*1'1 |
  c*2'1 | c*2'1 |
  g*1'1 | g*1'1 |
  c*2'1 | a*1'1 |
  d*2'1 | g*1'1 |
  c*2'1 | f*1'1 |
  g*1'1 | g*1'1 |

Pattern %Bassi_IVCH:
  key=C 4:
  c*2'1 | b*1'1 |
  a*1'1 | g*1'1 |
  f*1'1 | e*1'1 |
  d*2'1 | g*1'1 |
  a*1'1 | e*1'1 |
  f*1'1 | c*2'1 |
  d*2'1 | g*1'1 |
  c*2'1 | g*1'1 |

Pattern %Bassi_IVSTR:
  key=C 4:
  c*2'1 | c*2'1 |
  f*1'1 | f*1'1 |
  g*1'1 | g*1'1 |
  c*2'1 | g*1'1 |

Pattern %Bassi_IVCOD:
  key=C 4:
  c*2'1 | f*1'1 |
  g*1'1 | c*2'1 |
  d*2'1 | g*1'1 |
  c*2'1 | c*2'1 |

Pattern %Radici_IA:
  key=Cm 4:
  c*2'1 | c*2'1 |
  f*2'1 | g*2'1 |
  c*2'1 | a*2'1 |
  g*2'1 | c*2'1 |

Pattern %Radici_I3:
  key=Cm 4:
  c*2'1 | g*2'1 |
  f*2'1 | c*2'1 |
  b*2'1 | f*2'1 |
  e*2'1 | b*2'1 |

Pattern %Radici_IB:
  key=Eb 4:
  e*2'1 | d*2'1 |
  c*2'1 | a*2'1 |
  e*2'1 | f*2'1 |
  b*2'1 | e*2'1 |

Pattern %Radici_ICOD:
  key=Eb 4:
  e*2'1 | a*2'1 |
  f*2'1 | b*2'1 |
  e*2'1 | a*2'1 |
  b*2'1 | e*2'1 |

Pattern %Radici_IDEV1:
  key=Cm 4:
  f*2'1 | c*2'1 |
  g*2'1 | d*2'1 |
  b*2'1 | f*2'1 |
  c*2'1 | g*2'1 |

Pattern %Radici_IDEV2:
  key=Cm 4:
  e*2'1 | d*2'1 |
  db*2'1 | c*2'1 |
  b*2'1 | an*2'1 |
  a*2'1 | g*2'1 |

Pattern %Radici_IDEV3:
  key=Cm 4:
  a*2'1 | f*2'1 |
  g*2'1 | g*2'1 |
  g*2'1 | g*2'1 |
  g*2'1 | g*2'1 |

Pattern %Radici_I11:
  key=Cm 4:
  c*2'1 | g*2'1 |
  f*2'1 | c*2'1 |
  c*2'1 | g*2'1 |
  f*2'1 | g*2'1 |

Pattern %Radici_IB_C:
  key=C 4:
  c*2'1 | b*2'1 |
  a*2'1 | f*2'1 |
  c*2'1 | d*2'1 |
  g*2'1 | c*2'1 |

Pattern %Radici_ICODA:
  key=C 4:
  c*2'1 | f*2'1 |
  g*2'1 | c*2'1 |
  a*2'1 | f*2'1 |
  g*2'1 | c*2'1 |

Pattern %Radici_IIB:
  key=Fm 4:
  f*2'1 | c*2'1 |
  f*2'1 | d*2'1 |
  b*2'1 | c*2'1 |
  f*2'1 | c*2'1 |

Pattern %Radici_IIIS:
  key=Cm 4:
  c*2'1 | c*2'1 |
  g*2'1 | c*2'1 |
  f*2'1 | c*2'1 |
  g*2'1 | c*2'1 |

Pattern %Radici_IIIS_G:
  key=Gm 4:
  g*2'1 | g*2'1 |
  d*2'1 | g*2'1 |
  c*2'1 | g*2'1 |
  d*2'1 | g*2'1 |

Pattern %Radici_IVFAN:
  key=C 4:
  c*2'1 | c*2'1 |
  g*2'1 | g*2'1 |
  a*2'1 | f*2'1 |
  g*2'1 | g*2'1 |

Pattern %Radici_IVT:
  key=C 4:
  c*2'1 | b*2'1 |
  a*2'1 | e*2'1 |
  f*2'1 | e*2'1 |
  d*2'1 | g*2'1 |

Pattern %Radici_IVT_G:
  key=G 4:
  g*2'1 | f*2'1 |
  e*2'1 | b*2'1 |
  c*2'1 | b*2'1 |
  a*2'1 | d*2'1 |

Pattern %Radici_IVFUG:
  key=C 4:
  c*2'1 | c*2'1 |
  g*2'1 | g*2'1 |
  c*2'1 | c*2'1 |
  g*2'1 | g*2'1 |
  c*2'1 | a*2'1 |
  d*2'1 | g*2'1 |
  c*2'1 | f*2'1 |
  g*2'1 | g*2'1 |

Pattern %Radici_IVSTR:
  key=C 4:
  c*2'1 | c*2'1 |
  f*2'1 | f*2'1 |
  g*2'1 | g*2'1 |
  c*2'1 | g*2'1 |

Pattern %Radici_IVCOD:
  key=C 4:
  c*2'1 | f*2'1 |
  g*2'1 | c*2'1 |
  d*2'1 | g*2'1 |
  c*2'1 | c*2'1 |

Pattern %Acc_IVFUG_14_16:
  key=C 4:
  G7'1 | G7'1 |

Pattern %TimpDolce_I0:
  key=Cm 4:
  c*2 r r r | a*1 r r r |
  f*1 r r r | g*1 r r r |
  c*2 r r r | a*1 r r r |
  f*1 r r r | g*1 r r r |

Pattern %Timp_IA:
  key=Cm 4:
  c*2 r c*2 r | c*2 r c*2 r |
  f*1 r f*1 r | g*1 r g*1 r |
  c*2 r c*2 r | a*1 r a*1 r |
  g*1 r g*1 r | c*2 r c*2 r |

Pattern %TimpDolce_I3:
  key=Cm 4:
  c*2 r r r | g*1 r r r |
  f*1 r r r | c*2 r r r |
  b*1 r r r | f*1 r r r |
  e*2 r r r | b*1 r r r |

Pattern %TimpDolce_IB:
  key=Eb 4:
  e*2 r r r | d*2 r r r |
  c*2 r r r | a*1 r r r |
  e*2 r r r | f*1 r r r |
  b*1 r r r | e*2 r r r |

Pattern %Timp_ICOD:
  key=Eb 4:
  e*2 r e*2 r | a*1 r a*1 r |
  f*1 r f*1 r | b*1 r b*1 r |
  e*2 r e*2 r | a*1 r a*1 r |
  b*1 r b*1 r | e*2 r e*2 r |

Pattern %Timp_IDEV1:
  key=Cm 4:
  f*1 r f*1 r | c*2 r c*2 r |
  g*1 r g*1 r | d*2 r d*2 r |
  b*1 r b*1 r | f*1 r f*1 r |
  c*2 r c*2 r | g*1 r g*1 r |

Pattern %TimpDolce_IDEV2:
  key=Cm 4:
  e*2 r r r | d*2 r r r |
  db*2 r r r | c*2 r r r |
  b*1 r r r | an*1 r r r |
  a*1 r r r | g*1 r r r |

Pattern %TimpRullo_IDEV3:
  key=Cm 16:
  a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 |
  f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |

Pattern %TimpDolce_I11:
  key=Cm 4:
  c*2 r r r | g*1 r r r |
  f*1 r r r | c*2 r r r |
  c*2 r r r | g*1 r r r |
  f*1 r r r | g*1 r r r |

Pattern %TimpDolce_IB_C:
  key=C 4:
  c*2 r r r | b*1 r r r |
  a*1 r r r | f*1 r r r |
  c*2 r r r | d*2 r r r |
  g*1 r r r | c*2 r r r |

Pattern %Timp_ICODA:
  key=C 4:
  c*2 r c*2 r | f*1 r f*1 r |
  g*1 r g*1 r | c*2 r c*2 r |
  a*1 r a*1 r | f*1 r f*1 r |
  g*1 r g*1 r | c*2 r c*2 r |

Pattern %TimpDolce_IIB:
  key=Fm 4:
  f*1 r r r | c*2 r r r |
  f*1 r r r | d*2 r r r |
  b*1 r r r | c*2 r r r |
  f*1 r r r | c*2 r r r |

Pattern %Timp_IIIS:
  key=Cm 4:
  c*2 r c*2 r | c*2 r c*2 r |
  g*1 r g*1 r | c*2 r c*2 r |
  f*1 r f*1 r | c*2 r c*2 r |
  g*1 r g*1 r | c*2 r c*2 r |

Pattern %Timp_IIIS_G:
  key=Gm 4:
  g*1 r g*1 r | g*1 r g*1 r |
  d*2 r d*2 r | g*1 r g*1 r |
  c*2 r c*2 r | g*1 r g*1 r |
  d*2 r d*2 r | g*1 r g*1 r |

Pattern %Timp_IVFAN:
  key=C 4:
  c*2 r c*2 r | c*2 r c*2 r |
  g*1 r g*1 r | g*1 r g*1 r |
  a*1 r a*1 r | f*1 r f*1 r |
  g*1 r g*1 r | g*1 r g*1 r |

Pattern %Timp_IVT:
  key=C 4:
  c*2 r c*2 r | b*1 r b*1 r |
  a*1 r a*1 r | e*1 r e*1 r |
  f*1 r f*1 r | e*1 r e*1 r |
  d*2 r d*2 r | g*1 r g*1 r |

Pattern %Timp_IVT_G:
  key=G 4:
  g*1 r g*1 r | f*1 r f*1 r |
  e*1 r e*1 r | b*1 r b*1 r |
  c*2 r c*2 r | b*1 r b*1 r |
  a*1 r a*1 r | d*2 r d*2 r |

Pattern %TimpRullo_IVFUG:
  key=C 16:
  c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 |
  c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 |
  c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 |
  a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 |
  d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 c*2 |
  f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |

Pattern %TimpDolce_IVCH:
  key=C 4:
  c*2 r r r | b*1 r r r |
  a*1 r r r | g*1 r r r |
  f*1 r r r | e*1 r r r |
  d*2 r r r | g*1 r r r |
  a*1 r r r | e*1 r r r |
  f*1 r r r | c*2 r r r |
  d*2 r r r | g*1 r r r |
  c*2 r r r | g*1 r r r |

Pattern %Timp_IVSTR:
  key=C 4:
  c*2 r c*2 r | c*2 r c*2 r |
  f*1 r f*1 r | f*1 r f*1 r |
  g*1 r g*1 r | g*1 r g*1 r |
  c*2 r c*2 r | g*1 r g*1 r |

Pattern %Timp_IVCOD_0_4:
  key=C 4:
  c*2 r c*2 r | f*1 r f*1 r |
  g*1 r g*1 r | c*2 r c*2 r |

Pattern %Timp_IVCOD_4_7:
  key=C 4:
  d*2 r d*2 r | g*1 r g*1 r |
  c*2 r c*2 r |

// ================================================================ tracce

Violini1:
  // battute 1-8: Largo: introduzione
  $"Largo" 40@ %Arp_I0
  // battute 9-16: Allegro con fuoco: primo tema
  $"Allegro con fuoco" 95@ %I_TemaA
  // battute 17-24: primo tema, tutti
  100@ %I_TemaA2
  // battute 25-32: ponte: il motivo sale di tonalita'
  90@ %I_PonteMotivo %I_PonteMotivo-7 %I_PonteMotivo-2 %I_PonteMotivo+3
  // battute 33-40: secondo tema in Mi bemolle
  45@ %Arp_IB
  // battute 41-48: secondo tema, variato
  88@ %I_TemaB2
  // battute 49-56: codetta
  90@ %I_Codetta
  // battute 57-64: sviluppo 1: il primo tema in sequenza
  95@ %I_SvilMotivoA-7 %I_SvilMotivoA-5 %I_SvilMotivoA-2 %I_SvilMotivoA
  // battute 65-72: sviluppo 2: il secondo tema scende
  92@ %I_SvilMotivoB %I_SvilMotivoB-2 %I_SvilMotivoB-5 %I_SvilMotivoB-7
  // battute 73-80: sviluppo 3: l'attesa sulla dominante
  100@ %I_Attesa
  // battute 81-88: ripresa: primo tema
  108@ %I_TemaA
  // battute 89-96: ponte della ripresa
  92@ %I_PonteMotivo %I_PonteMotivo-7 %I_PonteMotivo %I_PonteMotivo-7
  // battute 97-104: secondo tema in Do maggiore
  45@ %Arp_IB_C
  // battute 105-112: secondo tema, variato
  90@ %I_TemaB2-3
  // battute 113-120: coda trionfale
  105@ %I_Coda
  // battute 121-128: Andante: il canto dell'oboe
  $"Andante" 40@ %Arp_IIA
  // battute 129-136: variazione dei violini
  72@ %II_Variazione
  // battute 137-144: episodio in Fa minore
  42@ %Arp_IIB
  // battute 145-152: il canto ai violoncelli
  75@ %II_Variazione
  // battute 153-160: coda
  70@ %II_Coda
  // battute 161-168: Scherzo: Presto
  $"Scherzo: Presto" 88@ %III_Scherzo
  // battute 169-176: seconda parte, in Sol minore
  90@ %III_Scherzo+7
  // battute 177-184: Trio
  $"Trio" 42@ %Arp_IITR
  // battute 185-192: il trio in Sol maggiore
  72@ %III_Trio+7
  // battute 193-200: Scherzo da capo
  $"Da capo" 92@ %III_Scherzo
  // battute 201-208: seconda parte
  94@ %III_Scherzo+7
  // battute 209-216: Finale: Allegro maestoso, la fanfara
  $"Finale: Allegro maestoso" 105@ %IV_Fanfara
  // battute 217-224: il tema
  98@ %IV_Tema
  // battute 225-232: il tema in Sol maggiore
  102@ %IV_Tema+7
  // battute 233-240: il tema, con i violoncelli
  104@ %IV_Tema
  // battute 241-256: fugato: otto entrate del soggetto
  bar=247 90@ %IV_Soggetto+7 60@ %Acc_IVFUG_8_16
  // battute 257-272: corale degli ottoni
  80@ %IV_CoraleA %IV_CoraleB
  // battute 273-280: Stretta: accelerando
  $"Stretta" 108@ %IV_Stretta
  // battute 281-288: coda con il rallentando
  %IV_Coda

Violini2:
  40@ %Acc_I0
  75@ %Arp_IA
  82@ %Arp_IA
  60@ %Arp_I3
  55@ %Arp_IB
  60@ %Arp_IB
  70@ %Arp_ICOD
  vol=60 >> 76@ %Arp_IDEV1
  63@ %Arp_IDEV2
  82@ %Arp_IDEV3 vol=100
  88@ %Arp_IA
  63@ %Arp_I11
  57@ %Arp_IB_C
  63@ %Arp_IB_C
  90@ %Arp_ICODA
  35@ %Acc_IIA
  40@ %Acc_IIA
  43@ %Arp_IIB
  42@ %Acc_IIA
  38@ %Acc_IICOD
  60@ %Arp_IIIS
  63@ %Arp_IIIS_G
  45@ %Acc_IITR
  49@ %Acc_IITR_G
  65@ %Arp_IIIS
  67@ %Arp_IIIS_G
  88@ %Arp_IVFAN
  78@ %Arp_IVT
  82@ %Arp_IVT_G
  84@ %Arp_IVT
  bar=245 86@ %IV_Soggetto 60@ %Arp_IVFUG_6_16
  %Acc_IVCH
  90@ %Arp_IVSTR
  92@ %Arp_IVCOD

Viole:
  40@ %Acc_I0
  80@ %Acc_IA
  87@ %Acc_IA
  60@ %Acc_I3
  55@ %Acc_IB
  60@ %Acc_IB
  75@ %Acc_ICOD
  vol=60 >> 81@ %Acc_IDEV1
  63@ %Acc_IDEV2
  87@ %Acc_IDEV3 vol=100
  93@ %Acc_IA
  63@ %Acc_I11
  57@ %Acc_IB_C
  63@ %Acc_IB_C
  95@ %Acc_ICODA
  35@ %Acc_IIA
  40@ %Acc_IIA
  43@ %Acc_IIB
  42@ %Acc_IIA
  38@ %Acc_IICOD
  70@ %Stacco_IIIS
  73@ %Stacco_IIIS_G
  45@ %Acc_IITR
  49@ %Acc_IITR_G
  75@ %Stacco_IIIS
  77@ %Stacco_IIIS_G
  93@ %Acc_IVFAN
  83@ %Acc_IVT
  87@ %Acc_IVT_G
  89@ %Acc_IVT
  bar=243 82@ %IV_Soggetto-5 60@ %Acc_IVFUG_4_16
  62@ %Acc_IVCH
  95@ %Acc_IVSTR
  97@ %Acc_IVCOD

Violoncelli:
  50@ %Radici_I0
  87@ %Celli_IA
  94@ %Celli_IA
  70@ %Celli_I3
  65@ %Celli_IB
  70@ %Celli_IB
  82@ %Celli_ICOD
  88@ %Celli_IDEV1
  73@ %Celli_IDEV2
  94@ %Celli_IDEV3
  100@ %Celli_IA
  73@ %Celli_I11
  67@ %Celli_IB_C
  73@ %Celli_IB_C
  102@ %Celli_ICODA
  45@ %Radici_IIA
  50@ %Radici_IIA
  53@ %Celli_IIB
  78@ %II_Canto-24
  48@ %Radici_IICOD
  80@ %Celli_IIIS
  83@ %Celli_IIIS_G
  55@ %Radici_IITR
  59@ %Radici_IITR_G
  85@ %Celli_IIIS
  87@ %Celli_IIIS_G
  100@ %Celli_IVFAN
  90@ %Celli_IVT
  94@ %Celli_IVT_G
  96@ %IV_Tema-24
  78@ %IV_Soggetto-24 60@ %Celli_IVFUG_2_16
  66@ %Radici_IVCH
  102@ %Celli_IVSTR
  104@ %Celli_IVCOD

Contrabbassi:
  48@ %Bassi_I0
  89@ %Bassi_IA
  96@ %Bassi_IA
  73@ %Bassi_I3
  68@ %Bassi_IB
  73@ %Bassi_IB
  84@ %Bassi_ICOD
  90@ %Bassi_IDEV1
  76@ %Bassi_IDEV2
  96@ %Bassi_IDEV3
  102@ %Bassi_IA
  76@ %Bassi_I11
  70@ %Bassi_IB_C
  76@ %Bassi_IB_C
  104@ %Bassi_ICODA
  43@ %Bassi_IIA
  48@ %Bassi_IIA
  56@ %Bassi_IIB
  50@ %Bassi_IIA
  46@ %Bassi_IICOD
  80@ %Bassi_IIIS
  83@ %Bassi_IIIS_G
  55@ %Bassi_IITR
  59@ %Bassi_IITR_G
  85@ %Bassi_IIIS
  87@ %Bassi_IIIS_G
  102@ %Bassi_IVFAN
  92@ %Bassi_IVT
  96@ %Bassi_IVT_G
  98@ %Bassi_IVT
  75@ %Bassi_IVFUG
  66@ %Bassi_IVCH
  104@ %Bassi_IVSTR
  106@ %Bassi_IVCOD

Flauto:
  bar=9 90@ %I_TemaA
  95@ %I_TemaA2
  90@ %I_PonteMotivo %I_PonteMotivo-7 %I_PonteMotivo-2 %I_PonteMotivo+3
  bar=41 80@ %I_TemaB2
  85@ %I_Codetta
  bar=65 80@ %I_SvilMotivoB %I_SvilMotivoB-2 %I_SvilMotivoB-5 %I_SvilMotivoB-7
  100@ %I_Attesa
  %I_TemaA
  92@ %I_PonteMotivo %I_PonteMotivo-7 %I_PonteMotivo %I_PonteMotivo-7
  bar=105 85@ %I_TemaB2-3
  100@ %I_Coda
  bar=137 65@ %II_Episodio
  bar=153 62@ %II_Coda
  82@ %III_Scherzo
  85@ %III_Scherzo+7
  bar=185 75@ %III_Trio+7
  86@ %III_Scherzo
  88@ %III_Scherzo+7
  95@ %IV_Fanfara
  92@ %IV_Tema
  96@ %IV_Tema+7
  %IV_Tema
  bar=251 98@ %IV_Soggetto+7
  bar=257 72@ %IV_CoraleA %IV_CoraleB
  100@ %IV_Stretta
  %IV_Coda

Oboe:
  70@ %I_Largo
  90@ %I_TemaA-12
  95@ %I_TemaA2-12
  bar=33 80@ %I_TemaB-12
  %I_TemaB-12
  85@ %I_Codetta-12
  90@ %I_SvilMotivoA-19 %I_SvilMotivoA-17 %I_SvilMotivoA-14 %I_SvilMotivoA-12
  bar=81 100@ %I_TemaA-12
  bar=97 82@ %I_TemaB-15
  %I_TemaB-15
  100@ %I_Coda-12
  75@ %II_Canto
  bar=137 72@ %II_Episodio
  bar=153 %II_Coda
  bar=169 80@ %III_Scherzo-5
  78@ %III_Trio
  70@ %III_Trio-5
  bar=201 84@ %III_Scherzo-5
  bar=217 92@ %IV_Tema-12
  bar=249 94@ %IV_Soggetto
  bar=257 70@ %IV_CoraleA-12 %IV_CoraleB-12
  100@ %IV_Stretta-12
  %IV_Coda-12

Clarinetto:
  55@ %I_Largo-12
  bar=25 80@ %I_PonteMotivo-12 %I_PonteMotivo-19 %I_PonteMotivo-14 %I_PonteMotivo-9
  75@ %I_TemaB-12
  bar=65 80@ %I_SvilMotivoB-12 %I_SvilMotivoB-14 %I_SvilMotivoB-17 %I_SvilMotivoB-19
  bar=97 75@ %I_TemaB-15
  bar=129 70@ %II_Canto-12
  65@ %II_Episodio-12
  bar=177 70@ %III_Trio-12
  bar=289

Fagotto:
  50@ %Radici_I0
  85@ %Radici_IA
  92@ %Radici_IA
  75@ %Radici_I3
  70@ %Radici_IB
  75@ %Radici_IB
  80@ %Radici_ICOD
  86@ %Radici_IDEV1
  78@ %Radici_IDEV2
  92@ %Radici_IDEV3
  98@ %Radici_IA
  78@ %Radici_I11
  72@ %Radici_IB_C
  78@ %Radici_IB_C
  100@ %Radici_ICODA
  45@ %Radici_IIA
  50@ %Radici_IIA
  58@ %Radici_IIB
  52@ %Radici_IIA
  48@ %Radici_IICOD
  75@ %Radici_IIIS
  78@ %Radici_IIIS_G
  55@ %Radici_IITR
  59@ %Radici_IITR_G
  80@ %Radici_IIIS
  82@ %Radici_IIIS_G
  98@ %Radici_IVFAN
  88@ %Radici_IVT
  92@ %Radici_IVT_G
  94@ %Radici_IVT
  70@ %Radici_IVFUG
  %Radici_IVCH
  100@ %Radici_IVSTR
  102@ %Radici_IVCOD

Corni:
  bar=9 95@ %Acc_IA
  102@ %Acc_IA
  60@ %Acc_I3
  55@ %Acc_IB
  60@ %Acc_IB
  90@ %Acc_ICOD
  96@ %Acc_IDEV1
  63@ %Acc_IDEV2
  102@ %Acc_IDEV3
  108@ %Acc_IA
  63@ %Acc_I11
  57@ %Acc_IB_C
  63@ %Acc_IB_C
  110@ %Acc_ICODA
  45@ %Acc_IIA
  48@ %Acc_IIA
  43@ %Acc_IIB
  50@ %Acc_IIA
  %Acc_IICOD
  70@ %Stacco_IIIS
  73@ %Stacco_IIIS_G
  40@ %Acc_IITR
  44@ %Acc_IITR_G
  75@ %Stacco_IIIS
  77@ %Stacco_IIIS_G
  108@ %Acc_IVFAN
  98@ %Acc_IVT
  102@ %Acc_IVT_G
  104@ %Acc_IVT
  bar=253 102@ %IV_Soggetto-12 60@ %Acc_IVFUG_14_16
  85@ %Acc_IVCH
  110@ %Acc_IVSTR
  112@ %Acc_IVCOD

Trumpet:
  bar=17 95@ %I_TemaA2-12
  bar=73 %I_Attesa-12
  105@ %I_TemaA-12
  bar=113 100@ %I_Coda-12
  bar=193 80@ %III_Scherzo-12
  %III_Scherzo-17
  105@ %IV_Fanfara-12
  bar=225 96@ %IV_Tema-5
  98@ %IV_Tema-12
  bar=255 106@ %IV_Soggetto-5
  90@ %IV_CoraleA-12 %IV_CoraleB-12
  bar=281 100@ %IV_Coda-12

Timpani:
  35@ %TimpDolce_I0
  tempo=138 95@ %Timp_IA
  102@ %Timp_IA
  60@ %TimpDolce_I3
  55@ %TimpDolce_IB
  60@ %TimpDolce_IB
  90@ %Timp_ICOD
  96@ %Timp_IDEV1
  63@ %TimpDolce_IDEV2
  85@ %TimpRullo_IDEV3
  108@ %Timp_IA
  63@ %TimpDolce_I11
  57@ %TimpDolce_IB_C
  63@ %TimpDolce_IB_C
  110@ %Timp_ICODA
  tempo=66
  bar=137 40@ %TimpDolce_IIB
  bar=161 tempo=160 85@ %Timp_IIIS
  88@ %Timp_IIIS_G
  tempo=132
  bar=193 tempo=160 90@ %Timp_IIIS
  92@ %Timp_IIIS_G
  tempo=126 108@ %Timp_IVFAN
  98@ %Timp_IVT
  102@ %Timp_IVT_G
  104@ %Timp_IVT
  55@ %TimpRullo_IVFUG
  %TimpDolce_IVCH
  tempo=150 110@ %Timp_IVSTR
  108@ %Timp_IVCOD_0_4 100@ tempo=150 << %Timp_IVCOD_4_7 key=C 4: c*2$fermata r r r | tempo=54

// ================================================================ mixer

Mixer Flauto:
  volume: 67 pan: 0.25 mute: no solo: no reverb: 25

Mixer Oboe:
  volume: 64 pan: -0.2 mute: no solo: no reverb: 25

Mixer Clarinetto:
  volume: 62 pan: 0.15 mute: no solo: no reverb: 25

Mixer Fagotto:
  volume: 62 pan: -0.3 mute: no solo: no reverb: 20

Mixer Corni:
  volume: 65 pan: 0.3 mute: no solo: no reverb: 28

Mixer Trumpet:
  volume: 64 pan: 0.4 mute: no solo: no reverb: 28

Mixer Timpani:
  volume: 68 pan: 0.0 mute: no solo: no reverb: 30

Mixer Violini1:
  volume: 71 pan: -0.5 mute: no solo: no reverb: 22

Mixer Violini2:
  volume: 67 pan: -0.3 mute: no solo: no reverb: 22

Mixer Viole:
  volume: 64 pan: 0.2 mute: no solo: no reverb: 22

Mixer Violoncelli:
  volume: 68 pan: 0.45 mute: no solo: no reverb: 20

Mixer Contrabbassi:
  volume: 67 pan: 0.6 mute: no solo: no reverb: 15
