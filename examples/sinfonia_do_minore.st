// Sinfonia n. 2 in Do minore, "Tempesta e quiete": una sinfonia lunga in quattro tempi.
//
// Musica originale, scritta per mostrare ST-language su larga scala: 288
// battute e 12 tracce, circa nove minuti. L'orchestra e' la stessa della
// "Sinfonia n. 1" (legni, corni e tromba, timpani, archi), ma qui le forme
// sono piu' ampie e il materiale tematico viene trasformato.
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
//   - le trasposizioni: lo stesso tema compare in altre tonalita' (il secondo
//     tema di Mi bemolle a Do, la fanfara-scherzo nella dominante) e nelle
//     sequenze dello sviluppo, ogni volta con le note ricalcolate;
//   - il fugato: un soggetto di due battute che entra otto volte, a battute
//     sfalsate e nell'ottava adatta a ciascun strumento;
//   - i cambi di tempo tra i movimenti e dentro (tempo=: Largo 60, Allegro 138,
//     Andante 66, Presto 160, Trio 132, Finale 126, Stretta 150) e il rallentando
//     finale con tempo=150 << ... tempo=54;
//   - le dinamiche: crescendo di volume nello sviluppo (vol=60 >> ... vol=100),
//     indicazioni di testo ($"Largo", $"Trio", $"Da capo", $"Stretta") e le corone;
//   - strumenti definiti nel file con il programma General MIDI;
//   - oltre trecento pattern per sezione: accordi tenuti, arpeggi, bassi, accordi
//     staccati, rulli e colpi di timpano.

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

Pattern %R1:
  4: 4r |

Pattern %I0M_Cm_0_0_70:
  key=Cm 8: 70@
  4c*5 2g*5 2e*5 |
  4a*5 2e*6 2c*6 |
  4f*5 2a*5 2c*6 |
  4d*6 2bn*5 2g*5 |
  4c*6 2g*5 2e*5 |
  4a*5 2c*6 2e*6 |
  2f*6 e*6 d*6 2c*6 2a*5 |
  4d*6 4r |

Pattern %I0M_Cm_0_m1_55:
  key=Cm 8: 55@
  4c*4 2g*4 2e*4 |
  4a*4 2e*5 2c*5 |
  4f*4 2a*4 2c*5 |
  4d*5 2bn*4 2g*4 |
  4c*5 2g*4 2e*4 |
  4a*4 2c*5 2e*5 |
  2f*5 e*5 d*5 2c*5 2a*4 |
  4d*5 4r |

Pattern %IAM_Cm_0_0_95:
  key=Cm 8: 95@
  2c*5 e*5 g*5 2c*6 2b*5 |
  a*5 g*5 f*5 e*5 4g*5 |
  2f*5 a*5 c*6 2f*6 2e*6 |
  d*6 c*6 bn*5 d*6 4g*5 |
  2c*5 e*5 g*5 2c*6 2e*6 |
  a*5 c*6 e*6 a*6 4g*6 |
  2f*6 d*6 bn*5 2d*6 2f*6 |
  4c*6 4r |

Pattern %IAM_Cm_0_0_90:
  key=Cm 8: 90@
  2c*5 e*5 g*5 2c*6 2b*5 |
  a*5 g*5 f*5 e*5 4g*5 |
  2f*5 a*5 c*6 2f*6 2e*6 |
  d*6 c*6 bn*5 d*6 4g*5 |
  2c*5 e*5 g*5 2c*6 2e*6 |
  a*5 c*6 e*6 a*6 4g*6 |
  2f*6 d*6 bn*5 2d*6 2f*6 |
  4c*6 4r |

Pattern %IAM_Cm_0_m1_90:
  key=Cm 8: 90@
  2c*4 e*4 g*4 2c*5 2b*4 |
  a*4 g*4 f*4 e*4 4g*4 |
  2f*4 a*4 c*5 2f*5 2e*5 |
  d*5 c*5 bn*4 d*5 4g*4 |
  2c*4 e*4 g*4 2c*5 2e*5 |
  a*4 c*5 e*5 a*5 4g*5 |
  2f*5 d*5 bn*4 2d*5 2f*5 |
  4c*5 4r |

Pattern %IAM2_Cm_0_0_100:
  key=Cm 8: 100@
  c*5 e*5 g*5 e*5 2c*6 2b*5 |
  a*5 g*5 f*5 e*5 2g*5 2c*5 |
  f*5 a*5 c*6 a*5 2f*6 2e*6 |
  d*6 c*6 bn*5 c*6 2d*6 2g*5 |
  c*5 e*5 g*5 e*5 2c*6 2e*6 |
  a*5 c*6 e*6 c*6 2a*6 2g*6 |
  f*6 e*6 d*6 bn*5 2d*6 2f*6 |
  6c*6 2r |

Pattern %IAM2_Cm_0_0_95:
  key=Cm 8: 95@
  c*5 e*5 g*5 e*5 2c*6 2b*5 |
  a*5 g*5 f*5 e*5 2g*5 2c*5 |
  f*5 a*5 c*6 a*5 2f*6 2e*6 |
  d*6 c*6 bn*5 c*6 2d*6 2g*5 |
  c*5 e*5 g*5 e*5 2c*6 2e*6 |
  a*5 c*6 e*6 c*6 2a*6 2g*6 |
  f*6 e*6 d*6 bn*5 2d*6 2f*6 |
  6c*6 2r |

Pattern %IAM2_Cm_0_m1_95:
  key=Cm 8: 95@
  c*4 e*4 g*4 e*4 2c*5 2b*4 |
  a*4 g*4 f*4 e*4 2g*4 2c*4 |
  f*4 a*4 c*5 a*4 2f*5 2e*5 |
  d*5 c*5 bn*4 c*5 2d*5 2g*4 |
  c*4 e*4 g*4 e*4 2c*5 2e*5 |
  a*4 c*5 e*5 c*5 2a*5 2g*5 |
  f*5 e*5 d*5 bn*4 2d*5 2f*5 |
  6c*5 2r |

Pattern %IPONTE_Cm_seq_0_90:
  key=Cm 8: 90@
  2g*5 c*6 e*6 2g*6 2f*6 |
  d*6 bn*5 g*5 d*6 4bn*5 |
  2c*5 f*5 a*5 2c*6 2b*5 |
  g*5 en*5 c*5 g*5 4en*5 |
  2f*5 b*5 db*6 2f*6 2e*6 |
  c*6 an*5 f*5 c*6 4an*5 |
  2b*5 e*6 gb*6 2b*6 2a*6 |
  f*6 d*6 b*5 f*6 4d*6 |

Pattern %IPONTE_Cm_seq_m1_80:
  key=Cm 8: 80@
  2g*4 c*5 e*5 2g*5 2f*5 |
  d*5 bn*4 g*4 d*5 4bn*4 |
  2c*4 f*4 a*4 2c*5 2b*4 |
  g*4 en*4 c*4 g*4 4en*4 |
  2f*4 b*4 db*5 2f*5 2e*5 |
  c*5 an*4 f*4 c*5 4an*4 |
  2b*4 e*5 gb*5 2b*5 2a*5 |
  f*5 d*5 b*4 f*5 4d*5 |

Pattern %IBM_Eb_0_m1_80:
  key=Eb 8: 80@
  2g*4 b*4 e*5 2d*5 2b*4 |
  2d*5 f*5 b*5 2g*5 2f*5 |
  2e*5 g*5 e*5 2c*5 2g*4 |
  2a*4 c*5 e*5 2a*5 2g*5 |
  2g*4 b*4 e*5 2g*5 2b*5 |
  2a*5 f*5 c*5 2a*4 2c*5 |
  d*5 f*5 a*5 f*5 2d*5 2b*4 |
  4e*5 4r |

Pattern %IBM_Eb_0_m1_75:
  key=Eb 8: 75@
  2g*4 b*4 e*5 2d*5 2b*4 |
  2d*5 f*5 b*5 2g*5 2f*5 |
  2e*5 g*5 e*5 2c*5 2g*4 |
  2a*4 c*5 e*5 2a*5 2g*5 |
  2g*4 b*4 e*5 2g*5 2b*5 |
  2a*5 f*5 c*5 2a*4 2c*5 |
  d*5 f*5 a*5 f*5 2d*5 2b*4 |
  4e*5 4r |

Pattern %IBM2_Eb_0_0_88:
  key=Eb 8: 88@
  g*5 b*5 e*6 g*6 2b*6 2g*6 |
  d*6 f*6 b*6 f*6 2d*6 2b*5 |
  e*6 g*6 e*6 c*6 2g*5 2e*5 |
  a*5 c*6 e*6 c*6 2a*5 2e*5 |
  g*5 b*5 e*6 b*5 2g*5 2e*6 |
  a*6 f*6 c*6 f*6 2a*5 2c*6 |
  d*6 f*6 a*6 f*6 2d*6 2f*6 |
  4e*6 2g*6 2b*6 |

Pattern %IBM2_Eb_0_0_80:
  key=Eb 8: 80@
  g*5 b*5 e*6 g*6 2b*6 2g*6 |
  d*6 f*6 b*6 f*6 2d*6 2b*5 |
  e*6 g*6 e*6 c*6 2g*5 2e*5 |
  a*5 c*6 e*6 c*6 2a*5 2e*5 |
  g*5 b*5 e*6 b*5 2g*5 2e*6 |
  a*6 f*6 c*6 f*6 2a*5 2c*6 |
  d*6 f*6 a*6 f*6 2d*6 2f*6 |
  4e*6 2g*6 2b*6 |

Pattern %ICOD_Eb_0_0_90:
  key=Eb 8: 90@
  b*6 a*6 g*6 f*6 e*6 d*6 2c*6 |
  b*5 c*6 d*6 e*6 2f*6 2d*6 |
  a*5 f*5 a*5 c*6 2f*6 2e*6 |
  d*6 f*6 a*6 f*6 4d*6 |
  2e*6 g*6 b*6 2g*6 2e*6 |
  2a*5 c*6 e*6 2a*6 2c*6 |
  d*6 c*6 b*5 a*5 2g*5 2f*5 |
  4e*5 4r |

Pattern %ICOD_Eb_0_0_85:
  key=Eb 8: 85@
  b*6 a*6 g*6 f*6 e*6 d*6 2c*6 |
  b*5 c*6 d*6 e*6 2f*6 2d*6 |
  a*5 f*5 a*5 c*6 2f*6 2e*6 |
  d*6 f*6 a*6 f*6 4d*6 |
  2e*6 g*6 b*6 2g*6 2e*6 |
  2a*5 c*6 e*6 2a*6 2c*6 |
  d*6 c*6 b*5 a*5 2g*5 2f*5 |
  4e*5 4r |

Pattern %ICOD_Eb_0_m1_85:
  key=Eb 8: 85@
  b*5 a*5 g*5 f*5 e*5 d*5 2c*5 |
  b*4 c*5 d*5 e*5 2f*5 2d*5 |
  a*4 f*4 a*4 c*5 2f*5 2e*5 |
  d*5 f*5 a*5 f*5 4d*5 |
  2e*5 g*5 b*5 2g*5 2e*5 |
  2a*4 c*5 e*5 2a*5 2c*5 |
  d*5 c*5 b*4 a*4 2g*4 2f*4 |
  4e*4 4r |

Pattern %IDEV1_Cm_seq_0_95:
  key=Cm 8: 95@
  2f*4 a*4 c*5 2f*5 2e*5 |
  db*5 c*5 b*4 a*4 4c*5 |
  2g*4 b*4 d*5 2g*5 2f*5 |
  e*5 d*5 c*5 b*4 4d*5 |
  2b*4 db*5 f*5 2b*5 2a*5 |
  gb*5 f*5 e*5 db*5 4f*5 |
  2c*5 e*5 g*5 2c*6 2b*5 |
  a*5 g*5 f*5 e*5 4g*5 |

Pattern %IDEV1_Cm_seq_m1_90:
  key=Cm 8: 90@
  2f*3 a*3 c*4 2f*4 2e*4 |
  db*4 c*4 b*3 a*3 4c*4 |
  2g*3 b*3 d*4 2g*4 2f*4 |
  e*4 d*4 c*4 b*3 4d*4 |
  2b*3 db*4 f*4 2b*4 2a*4 |
  gb*4 f*4 e*4 db*4 4f*4 |
  2c*4 e*4 g*4 2c*5 2b*4 |
  a*4 g*4 f*4 e*4 4g*4 |

Pattern %IDEV2_Cm_seq_0_92:
  key=Cm 8: 92@
  2g*5 b*5 e*6 2d*6 2b*5 |
  2d*6 f*6 b*6 2g*6 2f*6 |
  2f*5 a*5 db*6 2c*6 2a*5 |
  2c*6 e*6 a*6 2f*6 2e*6 |
  2d*5 f*5 b*5 2an*5 2f*5 |
  2an*5 c*6 f*6 2d*6 2c*6 |
  2c*5 e*5 a*5 2g*5 2e*5 |
  2g*5 b*5 e*6 2c*6 2b*5 |

Pattern %IDEV2_Cm_seq_m1_80:
  key=Cm 8: 80@
  2g*4 b*4 e*5 2d*5 2b*4 |
  2d*5 f*5 b*5 2g*5 2f*5 |
  2f*4 a*4 db*5 2c*5 2a*4 |
  2c*5 e*5 a*5 2f*5 2e*5 |
  2d*4 f*4 b*4 2an*4 2f*4 |
  2an*4 c*5 f*5 2d*5 2c*5 |
  2c*4 e*4 a*4 2g*4 2e*4 |
  2g*4 b*4 e*5 2c*5 2b*4 |

Pattern %IDEV2_Cm_seq_0_80:
  key=Cm 8: 80@
  2g*5 b*5 e*6 2d*6 2b*5 |
  2d*6 f*6 b*6 2g*6 2f*6 |
  2f*5 a*5 db*6 2c*6 2a*5 |
  2c*6 e*6 a*6 2f*6 2e*6 |
  2d*5 f*5 b*5 2an*5 2f*5 |
  2an*5 c*6 f*6 2d*6 2c*6 |
  2c*5 e*5 a*5 2g*5 2e*5 |
  2g*5 b*5 e*6 2c*6 2b*5 |

Pattern %IDEV3_Cm_0_0_100:
  key=Cm 8: 100@
  4a*5 4c*6 |
  4a*5 4f*5 |
  4d*6 4bn*5 |
  4g*5 4d*6 |
  d*6 bn*5 d*6 bn*5 d*6 bn*5 d*6 bn*5 |
  d*6 g*5 d*6 g*5 d*6 g*5 d*6 g*5 |
  2d*6 2f*6 2g*6 2bn*6 |
  4g*5 4r |

Pattern %IDEV3_Cm_0_m1_95:
  key=Cm 8: 95@
  4a*4 4c*5 |
  4a*4 4f*4 |
  4d*5 4bn*4 |
  4g*4 4d*5 |
  d*5 bn*4 d*5 bn*4 d*5 bn*4 d*5 bn*4 |
  d*5 g*4 d*5 g*4 d*5 g*4 d*5 g*4 |
  2d*5 2f*5 2g*5 2bn*5 |
  4g*4 4r |

Pattern %IAM_Cm_0_0_108:
  key=Cm 8: 108@
  2c*5 e*5 g*5 2c*6 2b*5 |
  a*5 g*5 f*5 e*5 4g*5 |
  2f*5 a*5 c*6 2f*6 2e*6 |
  d*6 c*6 bn*5 d*6 4g*5 |
  2c*5 e*5 g*5 2c*6 2e*6 |
  a*5 c*6 e*6 a*6 4g*6 |
  2f*6 d*6 bn*5 2d*6 2f*6 |
  4c*6 4r |

Pattern %IAM_Cm_0_0_100:
  key=Cm 8: 100@
  2c*5 e*5 g*5 2c*6 2b*5 |
  a*5 g*5 f*5 e*5 4g*5 |
  2f*5 a*5 c*6 2f*6 2e*6 |
  d*6 c*6 bn*5 d*6 4g*5 |
  2c*5 e*5 g*5 2c*6 2e*6 |
  a*5 c*6 e*6 a*6 4g*6 |
  2f*6 d*6 bn*5 2d*6 2f*6 |
  4c*6 4r |

Pattern %IAM_Cm_0_m1_100:
  key=Cm 8: 100@
  2c*4 e*4 g*4 2c*5 2b*4 |
  a*4 g*4 f*4 e*4 4g*4 |
  2f*4 a*4 c*5 2f*5 2e*5 |
  d*5 c*5 bn*4 d*5 4g*4 |
  2c*4 e*4 g*4 2c*5 2e*5 |
  a*4 c*5 e*5 a*5 4g*5 |
  2f*5 d*5 bn*4 2d*5 2f*5 |
  4c*5 4r |

Pattern %IAM_Cm_0_m1_105:
  key=Cm 8: 105@
  2c*4 e*4 g*4 2c*5 2b*4 |
  a*4 g*4 f*4 e*4 4g*4 |
  2f*4 a*4 c*5 2f*5 2e*5 |
  d*5 c*5 bn*4 d*5 4g*4 |
  2c*4 e*4 g*4 2c*5 2e*5 |
  a*4 c*5 e*5 a*5 4g*5 |
  2f*5 d*5 bn*4 2d*5 2f*5 |
  4c*5 4r |

Pattern %IPONTE2_Cm_seq_0_92:
  key=Cm 8: 92@
  2g*5 c*6 e*6 2g*6 2f*6 |
  d*6 bn*5 g*5 d*6 4bn*5 |
  2c*5 f*5 a*5 2c*6 2b*5 |
  g*5 en*5 c*5 g*5 4en*5 |
  2g*5 c*6 e*6 2g*6 2f*6 |
  d*6 bn*5 g*5 d*6 4bn*5 |
  2c*5 f*5 a*5 2c*6 2b*5 |
  g*5 en*5 c*5 g*5 4en*5 |

Pattern %IBMC_C_m3_m1_82:
  key=C 8: 82@
  2e*4 g*4 c*5 2b*4 2g*4 |
  2b*4 d*5 g*5 2e*5 2d*5 |
  2c*5 e*5 c*5 2a*4 2e*4 |
  2f*4 a*4 c*5 2f*5 2e*5 |
  2e*4 g*4 c*5 2e*5 2g*5 |
  2f*5 d*5 a*4 2f*4 2a*4 |
  b*4 d*5 f*5 d*5 2b*4 2g*4 |
  4c*5 4r |

Pattern %IBMC_C_m3_m1_75:
  key=C 8: 75@
  2e*4 g*4 c*5 2b*4 2g*4 |
  2b*4 d*5 g*5 2e*5 2d*5 |
  2c*5 e*5 c*5 2a*4 2e*4 |
  2f*4 a*4 c*5 2f*5 2e*5 |
  2e*4 g*4 c*5 2e*5 2g*5 |
  2f*5 d*5 a*4 2f*4 2a*4 |
  b*4 d*5 f*5 d*5 2b*4 2g*4 |
  4c*5 4r |

Pattern %IBM2C_C_m3_0_90:
  key=C 8: 90@
  e*5 g*5 c*6 e*6 2g*6 2e*6 |
  b*5 d*6 g*6 d*6 2b*5 2g*5 |
  c*6 e*6 c*6 a*5 2e*5 2c*5 |
  f*5 a*5 c*6 a*5 2f*5 2c*5 |
  e*5 g*5 c*6 g*5 2e*5 2c*6 |
  f*6 d*6 a*5 d*6 2f*5 2a*5 |
  b*5 d*6 f*6 d*6 2b*5 2d*6 |
  4c*6 2e*6 2g*6 |

Pattern %IBM2C_C_m3_0_85:
  key=C 8: 85@
  e*5 g*5 c*6 e*6 2g*6 2e*6 |
  b*5 d*6 g*6 d*6 2b*5 2g*5 |
  c*6 e*6 c*6 a*5 2e*5 2c*5 |
  f*5 a*5 c*6 a*5 2f*5 2c*5 |
  e*5 g*5 c*6 g*5 2e*5 2c*6 |
  f*6 d*6 a*5 d*6 2f*5 2a*5 |
  b*5 d*6 f*6 d*6 2b*5 2d*6 |
  4c*6 2e*6 2g*6 |

Pattern %ICODA_C_0_0_105:
  key=C 8: 105@
  2c*6 e*6 g*6 2g*6 2e*6 |
  2a*5 c*6 f*6 2a*6 2f*6 |
  2g*5 b*5 d*6 2g*6 2f*6 |
  4e*6 2g*6 2c*6 |
  2a*5 c*6 e*6 2a*6 2e*6 |
  2f*6 a*6 f*6 2c*6 2a*5 |
  g*5 b*5 d*6 f*6 2g*6 2d*6 |
  8c*6$fermata |

Pattern %ICODA_C_0_0_100:
  key=C 8: 100@
  2c*6 e*6 g*6 2g*6 2e*6 |
  2a*5 c*6 f*6 2a*6 2f*6 |
  2g*5 b*5 d*6 2g*6 2f*6 |
  4e*6 2g*6 2c*6 |
  2a*5 c*6 e*6 2a*6 2e*6 |
  2f*6 a*6 f*6 2c*6 2a*5 |
  g*5 b*5 d*6 f*6 2g*6 2d*6 |
  8c*6$fermata |

Pattern %ICODA_C_0_m1_100:
  key=C 8: 100@
  2c*5 e*5 g*5 2g*5 2e*5 |
  2a*4 c*5 f*5 2a*5 2f*5 |
  2g*4 b*4 d*5 2g*5 2f*5 |
  4e*5 2g*5 2c*5 |
  2a*4 c*5 e*5 2a*5 2e*5 |
  2f*5 a*5 f*5 2c*5 2a*4 |
  g*4 b*4 d*5 f*5 2g*5 2d*5 |
  8c*5$fermata |

Pattern %IIA_Ab_0_0_75:
  key=Ab 8: 75@
  4c*6 2e*6 2a*5 |
  4g*5 2b*5 2e*6 |
  4a*5 2c*6 2f*6 |
  4d*6 2f*6 2a*5 |
  4c*6 2e*6 2c*6 |
  4b*5 2d*6 2f*6 |
  4g*5 2b*5 2d*6 |
  4a*5 4r |

Pattern %IIA2_Ab_0_0_72:
  key=Ab 8: 72@
  c*6 d*6 e*6 c*6 2a*5 2e*6 |
  g*5 a*5 b*5 g*5 2e*6 2b*5 |
  a*5 b*5 c*6 a*5 2f*6 2c*6 |
  d*6 e*6 f*6 d*6 2a*5 2f*6 |
  c*6 e*6 a*6 g*6 2f*6 2e*6 |
  b*5 d*6 f*6 d*6 2b*5 2d*6 |
  g*5 b*5 d*6 b*5 2g*5 2b*5 |
  4a*5 4r |

Pattern %IIA_Ab_0_m1_70:
  key=Ab 8: 70@
  4c*5 2e*5 2a*4 |
  4g*4 2b*4 2e*5 |
  4a*4 2c*5 2f*5 |
  4d*5 2f*5 2a*4 |
  4c*5 2e*5 2c*5 |
  4b*4 2d*5 2f*5 |
  4g*4 2b*4 2d*5 |
  4a*4 4r |

Pattern %IIB_Fm_0_0_72:
  key=Fm 8: 72@
  4f*5 2a*5 2c*6 |
  4en*6 2g*6 2b*5 |
  2f*6 e*6 d*6 2c*6 2a*5 |
  4d*6 2f*6 2a*5 |
  4b*5 2d*6 2f*6 |
  2g*5 b*5 en*6 2g*6 2b*5 |
  4a*5 2c*6 2f*6 |
  4g*5 4r |

Pattern %IIB_Fm_0_0_65:
  key=Fm 8: 65@
  4f*5 2a*5 2c*6 |
  4en*6 2g*6 2b*5 |
  2f*6 e*6 d*6 2c*6 2a*5 |
  4d*6 2f*6 2a*5 |
  4b*5 2d*6 2f*6 |
  2g*5 b*5 en*6 2g*6 2b*5 |
  4a*5 2c*6 2f*6 |
  4g*5 4r |

Pattern %IIB_Fm_0_m1_65:
  key=Fm 8: 65@
  4f*4 2a*4 2c*5 |
  4en*5 2g*5 2b*4 |
  2f*5 e*5 d*5 2c*5 2a*4 |
  4d*5 2f*5 2a*4 |
  4b*4 2d*5 2f*5 |
  2g*4 b*4 en*5 2g*5 2b*4 |
  4a*4 2c*5 2f*5 |
  4g*4 4r |

Pattern %IIA_Ab_0_m2_78:
  key=Ab 8: 78@
  4c*4 2e*4 2a*3 |
  4g*3 2b*3 2e*4 |
  4a*3 2c*4 2f*4 |
  4d*4 2f*4 2a*3 |
  4c*4 2e*4 2c*4 |
  4b*3 2d*4 2f*4 |
  4g*3 2b*3 2d*4 |
  4a*3 4r |

Pattern %IIA2_Ab_0_0_75:
  key=Ab 8: 75@
  c*6 d*6 e*6 c*6 2a*5 2e*6 |
  g*5 a*5 b*5 g*5 2e*6 2b*5 |
  a*5 b*5 c*6 a*5 2f*6 2c*6 |
  d*6 e*6 f*6 d*6 2a*5 2f*6 |
  c*6 e*6 a*6 g*6 2f*6 2e*6 |
  b*5 d*6 f*6 d*6 2b*5 2d*6 |
  g*5 b*5 d*6 b*5 2g*5 2b*5 |
  4a*5 4r |

Pattern %IICOD_Ab_0_0_72:
  key=Ab 8: 72@
  4d*6 2f*6 2a*5 |
  4b*5 2d*6 2f*6 |
  4g*5 2b*5 2d*6 |
  4c*6 2e*6 2a*5 |
  4a*5 2c*6 2f*6 |
  4d*6 2f*6 2a*6 |
  2g*6 b*6 g*6 2d*6 2b*5 |
  8a*5$fermata |

Pattern %IICOD_Ab_0_0_70:
  key=Ab 8: 70@
  4d*6 2f*6 2a*5 |
  4b*5 2d*6 2f*6 |
  4g*5 2b*5 2d*6 |
  4c*6 2e*6 2a*5 |
  4a*5 2c*6 2f*6 |
  4d*6 2f*6 2a*6 |
  2g*6 b*6 g*6 2d*6 2b*5 |
  8a*5$fermata |

Pattern %IICOD_Ab_0_0_62:
  key=Ab 8: 62@
  4d*6 2f*6 2a*5 |
  4b*5 2d*6 2f*6 |
  4g*5 2b*5 2d*6 |
  4c*6 2e*6 2a*5 |
  4a*5 2c*6 2f*6 |
  4d*6 2f*6 2a*6 |
  2g*6 b*6 g*6 2d*6 2b*5 |
  8a*5$fermata |

Pattern %IIIS_Cm_0_0_88:
  key=Cm 8: 88@
  c*5 e*5 g*5 e*5 c*5 e*5 2g*5 |
  c*6 b*5 a*5 g*5 2f*5 2e*5 |
  d*5 f*5 g*5 f*5 d*5 f*5 2bn*5 |
  2c*6 2g*5 2e*5 2c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 2c*6 |
  e*5 g*5 c*6 g*5 e*5 g*5 2c*6 |
  d*6 c*6 bn*5 g*5 d*5 g*5 2bn*5 |
  4c*5 4r |

Pattern %IIIS_Cm_0_0_82:
  key=Cm 8: 82@
  c*5 e*5 g*5 e*5 c*5 e*5 2g*5 |
  c*6 b*5 a*5 g*5 2f*5 2e*5 |
  d*5 f*5 g*5 f*5 d*5 f*5 2bn*5 |
  2c*6 2g*5 2e*5 2c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 2c*6 |
  e*5 g*5 c*6 g*5 e*5 g*5 2c*6 |
  d*6 c*6 bn*5 g*5 d*5 g*5 2bn*5 |
  4c*5 4r |

Pattern %IIIS2_Gm_7_0_90:
  key=Gm 8: 90@
  g*5 b*5 d*6 b*5 g*5 b*5 2d*6 |
  g*6 f*6 e*6 d*6 2c*6 2b*5 |
  a*5 c*6 d*6 c*6 a*5 c*6 2gb*6 |
  2g*6 2d*6 2b*5 2g*5 |
  c*6 e*6 g*6 e*6 c*6 e*6 2g*6 |
  b*5 d*6 g*6 d*6 b*5 d*6 2g*6 |
  a*6 g*6 gb*6 d*6 a*5 d*6 2gb*6 |
  4g*5 4r |

Pattern %IIIS2_Gm_7_0_85:
  key=Gm 8: 85@
  g*5 b*5 d*6 b*5 g*5 b*5 2d*6 |
  g*6 f*6 e*6 d*6 2c*6 2b*5 |
  a*5 c*6 d*6 c*6 a*5 c*6 2gb*6 |
  2g*6 2d*6 2b*5 2g*5 |
  c*6 e*6 g*6 e*6 c*6 e*6 2g*6 |
  b*5 d*6 g*6 d*6 b*5 d*6 2g*6 |
  a*6 g*6 gb*6 d*6 a*5 d*6 2gb*6 |
  4g*5 4r |

Pattern %IIIS2_Gm_7_m1_80:
  key=Gm 8: 80@
  g*4 b*4 d*5 b*4 g*4 b*4 2d*5 |
  g*5 f*5 e*5 d*5 2c*5 2b*4 |
  a*4 c*5 d*5 c*5 a*4 c*5 2gb*5 |
  2g*5 2d*5 2b*4 2g*4 |
  c*5 e*5 g*5 e*5 c*5 e*5 2g*5 |
  b*4 d*5 g*5 d*5 b*4 d*5 2g*5 |
  a*5 g*5 gb*5 d*5 a*4 d*5 2gb*5 |
  4g*4 4r |

Pattern %IIITR_C_0_0_78:
  key=C 8: 78@
  2e*5 g*5 c*6 2e*6 2g*5 |
  2d*6 c*6 b*5 2c*6 2e*6 |
  2d*5 g*5 b*5 2d*6 2b*5 |
  4c*6 2g*5 2e*5 |
  2f*5 a*5 c*6 2f*6 2a*5 |
  2e*5 g*5 c*6 2e*6 2c*6 |
  2d*6 b*5 g*5 2f*5 2d*5 |
  4c*5 4r |

Pattern %IIITR_C_0_m1_70:
  key=C 8: 70@
  2e*4 g*4 c*5 2e*5 2g*4 |
  2d*5 c*5 b*4 2c*5 2e*5 |
  2d*4 g*4 b*4 2d*5 2b*4 |
  4c*5 2g*4 2e*4 |
  2f*4 a*4 c*5 2f*5 2a*4 |
  2e*4 g*4 c*5 2e*5 2c*5 |
  2d*5 b*4 g*4 2f*4 2d*4 |
  4c*4 4r |

Pattern %IIITR2_G_7_0_75:
  key=G 8: 75@
  2b*5 d*6 g*6 2b*6 2d*6 |
  2a*6 g*6 f*6 2g*6 2b*6 |
  2a*5 d*6 f*6 2a*6 2f*6 |
  4g*6 2d*6 2b*5 |
  2c*6 e*6 g*6 2c*7 2e*6 |
  2b*5 d*6 g*6 2b*6 2g*6 |
  2a*6 f*6 d*6 2c*6 2a*5 |
  4g*5 4r |

Pattern %IIITR2_G_7_0_72:
  key=G 8: 72@
  2b*5 d*6 g*6 2b*6 2d*6 |
  2a*6 g*6 f*6 2g*6 2b*6 |
  2a*5 d*6 f*6 2a*6 2f*6 |
  4g*6 2d*6 2b*5 |
  2c*6 e*6 g*6 2c*7 2e*6 |
  2b*5 d*6 g*6 2b*6 2g*6 |
  2a*6 f*6 d*6 2c*6 2a*5 |
  4g*5 4r |

Pattern %IIITR2_G_7_m1_70:
  key=G 8: 70@
  2b*4 d*5 g*5 2b*5 2d*5 |
  2a*5 g*5 f*5 2g*5 2b*5 |
  2a*4 d*5 f*5 2a*5 2f*5 |
  4g*5 2d*5 2b*4 |
  2c*5 e*5 g*5 2c*6 2e*5 |
  2b*4 d*5 g*5 2b*5 2g*5 |
  2a*5 f*5 d*5 2c*5 2a*4 |
  4g*4 4r |

Pattern %IIIS_Cm_0_0_92:
  key=Cm 8: 92@
  c*5 e*5 g*5 e*5 c*5 e*5 2g*5 |
  c*6 b*5 a*5 g*5 2f*5 2e*5 |
  d*5 f*5 g*5 f*5 d*5 f*5 2bn*5 |
  2c*6 2g*5 2e*5 2c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 2c*6 |
  e*5 g*5 c*6 g*5 e*5 g*5 2c*6 |
  d*6 c*6 bn*5 g*5 d*5 g*5 2bn*5 |
  4c*5 4r |

Pattern %IIIS_Cm_0_0_86:
  key=Cm 8: 86@
  c*5 e*5 g*5 e*5 c*5 e*5 2g*5 |
  c*6 b*5 a*5 g*5 2f*5 2e*5 |
  d*5 f*5 g*5 f*5 d*5 f*5 2bn*5 |
  2c*6 2g*5 2e*5 2c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 2c*6 |
  e*5 g*5 c*6 g*5 e*5 g*5 2c*6 |
  d*6 c*6 bn*5 g*5 d*5 g*5 2bn*5 |
  4c*5 4r |

Pattern %IIIS_Cm_0_m1_80:
  key=Cm 8: 80@
  c*4 e*4 g*4 e*4 c*4 e*4 2g*4 |
  c*5 b*4 a*4 g*4 2f*4 2e*4 |
  d*4 f*4 g*4 f*4 d*4 f*4 2bn*4 |
  2c*5 2g*4 2e*4 2c*4 |
  f*4 a*4 c*5 a*4 f*4 a*4 2c*5 |
  e*4 g*4 c*5 g*4 e*4 g*4 2c*5 |
  d*5 c*5 bn*4 g*4 d*4 g*4 2bn*4 |
  4c*4 4r |

Pattern %IIIS2_Gm_7_0_94:
  key=Gm 8: 94@
  g*5 b*5 d*6 b*5 g*5 b*5 2d*6 |
  g*6 f*6 e*6 d*6 2c*6 2b*5 |
  a*5 c*6 d*6 c*6 a*5 c*6 2gb*6 |
  2g*6 2d*6 2b*5 2g*5 |
  c*6 e*6 g*6 e*6 c*6 e*6 2g*6 |
  b*5 d*6 g*6 d*6 b*5 d*6 2g*6 |
  a*6 g*6 gb*6 d*6 a*5 d*6 2gb*6 |
  4g*5 4r |

Pattern %IIIS2_Gm_7_0_88:
  key=Gm 8: 88@
  g*5 b*5 d*6 b*5 g*5 b*5 2d*6 |
  g*6 f*6 e*6 d*6 2c*6 2b*5 |
  a*5 c*6 d*6 c*6 a*5 c*6 2gb*6 |
  2g*6 2d*6 2b*5 2g*5 |
  c*6 e*6 g*6 e*6 c*6 e*6 2g*6 |
  b*5 d*6 g*6 d*6 b*5 d*6 2g*6 |
  a*6 g*6 gb*6 d*6 a*5 d*6 2gb*6 |
  4g*5 4r |

Pattern %IIIS2_Gm_7_m1_84:
  key=Gm 8: 84@
  g*4 b*4 d*5 b*4 g*4 b*4 2d*5 |
  g*5 f*5 e*5 d*5 2c*5 2b*4 |
  a*4 c*5 d*5 c*5 a*4 c*5 2gb*5 |
  2g*5 2d*5 2b*4 2g*4 |
  c*5 e*5 g*5 e*5 c*5 e*5 2g*5 |
  b*4 d*5 g*5 d*5 b*4 d*5 2g*5 |
  a*5 g*5 gb*5 d*5 a*4 d*5 2gb*5 |
  4g*4 4r |

Pattern %IIIS2_Gm_7_m2_80:
  key=Gm 8: 80@
  g*3 b*3 d*4 b*3 g*3 b*3 2d*4 |
  g*4 f*4 e*4 d*4 2c*4 2b*3 |
  a*3 c*4 d*4 c*4 a*3 c*4 2gb*4 |
  2g*4 2d*4 2b*3 2g*3 |
  c*4 e*4 g*4 e*4 c*4 e*4 2g*4 |
  b*3 d*4 g*4 d*4 b*3 d*4 2g*4 |
  a*4 g*4 gb*4 d*4 a*3 d*4 2gb*4 |
  4g*3 4r |

Pattern %IVFAN_C_0_0_105:
  key=C 8: 105@
  c*5 e*5 g*5 c*6 2e*6 2g*5 |
  4c*6 4r |
  d*5 g*5 b*5 d*6 2g*6 2d*6 |
  4g*5 4r |
  e*5 a*5 c*6 e*6 2a*6 2e*6 |
  f*5 a*5 c*6 f*6 2a*6 2c*6 |
  d*6 b*5 g*5 f*5 2d*5 2g*5 |
  4g*5 4r |

Pattern %IVFAN_C_0_m1_105:
  key=C 8: 105@
  c*4 e*4 g*4 c*5 2e*5 2g*4 |
  4c*5 4r |
  d*4 g*4 b*4 d*5 2g*5 2d*5 |
  4g*4 4r |
  e*4 a*4 c*5 e*5 2a*5 2e*5 |
  f*4 a*4 c*5 f*5 2a*5 2c*5 |
  d*5 b*4 g*4 f*4 2d*4 2g*4 |
  4g*4 4r |

Pattern %IVFAN_C_0_0_95:
  key=C 8: 95@
  c*5 e*5 g*5 c*6 2e*6 2g*5 |
  4c*6 4r |
  d*5 g*5 b*5 d*6 2g*6 2d*6 |
  4g*5 4r |
  e*5 a*5 c*6 e*6 2a*6 2e*6 |
  f*5 a*5 c*6 f*6 2a*6 2c*6 |
  d*6 b*5 g*5 f*5 2d*5 2g*5 |
  4g*5 4r |

Pattern %IVT_C_0_0_98:
  key=C 8: 98@
  c*6 c*6 e*6 g*6 2c*6 2g*5 |
  d*6 d*6 g*6 b*5 2d*6 2g*5 |
  e*6 e*6 a*6 c*6 2e*6 2a*5 |
  g*5 b*5 e*6 g*6 2b*5 2e*6 |
  f*6 f*6 a*6 c*6 2f*6 2c*6 |
  e*6 g*6 c*6 e*6 2g*6 2e*6 |
  d*6 f*6 a*6 f*6 2d*6 2f*6 |
  g*5 b*5 d*6 f*6 4g*6 |

Pattern %IVT_C_0_0_92:
  key=C 8: 92@
  c*6 c*6 e*6 g*6 2c*6 2g*5 |
  d*6 d*6 g*6 b*5 2d*6 2g*5 |
  e*6 e*6 a*6 c*6 2e*6 2a*5 |
  g*5 b*5 e*6 g*6 2b*5 2e*6 |
  f*6 f*6 a*6 c*6 2f*6 2c*6 |
  e*6 g*6 c*6 e*6 2g*6 2e*6 |
  d*6 f*6 a*6 f*6 2d*6 2f*6 |
  g*5 b*5 d*6 f*6 4g*6 |

Pattern %IVT_C_0_m1_92:
  key=C 8: 92@
  c*5 c*5 e*5 g*5 2c*5 2g*4 |
  d*5 d*5 g*5 b*4 2d*5 2g*4 |
  e*5 e*5 a*5 c*5 2e*5 2a*4 |
  g*4 b*4 e*5 g*5 2b*4 2e*5 |
  f*5 f*5 a*5 c*5 2f*5 2c*5 |
  e*5 g*5 c*5 e*5 2g*5 2e*5 |
  d*5 f*5 a*5 f*5 2d*5 2f*5 |
  g*4 b*4 d*5 f*5 4g*5 |

Pattern %IVTG_G_7_0_102:
  key=G 8: 102@
  g*6 g*6 b*6 d*7 2g*6 2d*6 |
  a*6 a*6 d*7 f*6 2a*6 2d*6 |
  b*6 b*6 e*7 g*6 2b*6 2e*6 |
  d*6 f*6 b*6 d*7 2f*6 2b*6 |
  c*7 c*7 e*7 g*6 2c*7 2g*6 |
  b*6 d*7 g*6 b*6 2d*7 2b*6 |
  a*6 c*7 e*7 c*7 2a*6 2c*7 |
  d*6 f*6 a*6 c*7 4d*7 |

Pattern %IVTG_G_7_0_96:
  key=G 8: 96@
  g*6 g*6 b*6 d*7 2g*6 2d*6 |
  a*6 a*6 d*7 f*6 2a*6 2d*6 |
  b*6 b*6 e*7 g*6 2b*6 2e*6 |
  d*6 f*6 b*6 d*7 2f*6 2b*6 |
  c*7 c*7 e*7 g*6 2c*7 2g*6 |
  b*6 d*7 g*6 b*6 2d*7 2b*6 |
  a*6 c*7 e*7 c*7 2a*6 2c*7 |
  d*6 f*6 a*6 c*7 4d*7 |

Pattern %IVTG_G_7_m1_96:
  key=G 8: 96@
  g*5 g*5 b*5 d*6 2g*5 2d*5 |
  a*5 a*5 d*6 f*5 2a*5 2d*5 |
  b*5 b*5 e*6 g*5 2b*5 2e*5 |
  d*5 f*5 b*5 d*6 2f*5 2b*5 |
  c*6 c*6 e*6 g*5 2c*6 2g*5 |
  b*5 d*6 g*5 b*5 2d*6 2b*5 |
  a*5 c*6 e*6 c*6 2a*5 2c*6 |
  d*5 f*5 a*5 c*6 4d*6 |

Pattern %IVT_C_0_0_104:
  key=C 8: 104@
  c*6 c*6 e*6 g*6 2c*6 2g*5 |
  d*6 d*6 g*6 b*5 2d*6 2g*5 |
  e*6 e*6 a*6 c*6 2e*6 2a*5 |
  g*5 b*5 e*6 g*6 2b*5 2e*6 |
  f*6 f*6 a*6 c*6 2f*6 2c*6 |
  e*6 g*6 c*6 e*6 2g*6 2e*6 |
  d*6 f*6 a*6 f*6 2d*6 2f*6 |
  g*5 b*5 d*6 f*6 4g*6 |

Pattern %IVT_C_0_m2_96:
  key=C 8: 96@
  c*4 c*4 e*4 g*4 2c*4 2g*3 |
  d*4 d*4 g*4 b*3 2d*4 2g*3 |
  e*4 e*4 a*4 c*4 2e*4 2a*3 |
  g*3 b*3 e*4 g*4 2b*3 2e*4 |
  f*4 f*4 a*4 c*4 2f*4 2c*4 |
  e*4 g*4 c*4 e*4 2g*4 2e*4 |
  d*4 f*4 a*4 f*4 2d*4 2f*4 |
  g*3 b*3 d*4 f*4 4g*4 |

Pattern %IVT_C_0_0_96:
  key=C 8: 96@
  c*6 c*6 e*6 g*6 2c*6 2g*5 |
  d*6 d*6 g*6 b*5 2d*6 2g*5 |
  e*6 e*6 a*6 c*6 2e*6 2a*5 |
  g*5 b*5 e*6 g*6 2b*5 2e*6 |
  f*6 f*6 a*6 c*6 2f*6 2c*6 |
  e*6 g*6 c*6 e*6 2g*6 2e*6 |
  d*6 f*6 a*6 f*6 2d*6 2f*6 |
  g*5 b*5 d*6 f*6 4g*6 |

Pattern %IVT_C_0_m1_98:
  key=C 8: 98@
  c*5 c*5 e*5 g*5 2c*5 2g*4 |
  d*5 d*5 g*5 b*4 2d*5 2g*4 |
  e*5 e*5 a*5 c*5 2e*5 2a*4 |
  g*4 b*4 e*5 g*5 2b*4 2e*5 |
  f*5 f*5 a*5 c*5 2f*5 2c*5 |
  e*5 g*5 c*5 e*5 2g*5 2e*5 |
  d*5 f*5 a*5 f*5 2d*5 2f*5 |
  g*4 b*4 d*5 f*5 4g*5 |

Pattern %IVSTR_C_0_0_108:
  key=C 8: 108@
  c*5 d*5 e*5 f*5 g*5 a*5 b*5 c*6 |
  c*6 b*5 a*5 g*5 f*5 e*5 d*5 c*5 |
  f*5 a*5 c*6 f*6 c*6 a*5 f*5 a*5 |
  a*5 c*6 f*6 a*6 f*6 c*6 a*5 f*5 |
  g*5 b*5 d*6 g*6 d*6 b*5 g*5 b*5 |
  d*6 g*6 b*6 g*6 d*6 g*6 b*6 g*6 |
  c*6 e*6 g*6 e*6 c*6 e*6 g*6 e*6 |
  g*5 b*5 d*6 f*6 4g*6 |

Pattern %IVSTR_C_0_0_100:
  key=C 8: 100@
  c*5 d*5 e*5 f*5 g*5 a*5 b*5 c*6 |
  c*6 b*5 a*5 g*5 f*5 e*5 d*5 c*5 |
  f*5 a*5 c*6 f*6 c*6 a*5 f*5 a*5 |
  a*5 c*6 f*6 a*6 f*6 c*6 a*5 f*5 |
  g*5 b*5 d*6 g*6 d*6 b*5 g*5 b*5 |
  d*6 g*6 b*6 g*6 d*6 g*6 b*6 g*6 |
  c*6 e*6 g*6 e*6 c*6 e*6 g*6 e*6 |
  g*5 b*5 d*6 f*6 4g*6 |

Pattern %IVSTR_C_0_m1_100:
  key=C 8: 100@
  c*4 d*4 e*4 f*4 g*4 a*4 b*4 c*5 |
  c*5 b*4 a*4 g*4 f*4 e*4 d*4 c*4 |
  f*4 a*4 c*5 f*5 c*5 a*4 f*4 a*4 |
  a*4 c*5 f*5 a*5 f*5 c*5 a*4 f*4 |
  g*4 b*4 d*5 g*5 d*5 b*4 g*4 b*4 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*4 b*4 d*5 f*5 4g*5 |

Pattern %IVCOD_C_0_0_108:
  key=C 8: 108@
  2c*6 e*6 g*6 4c*6 |
  2a*5 c*6 f*6 4a*6 |
  2g*5 b*5 d*6 4g*6 |
  4e*6 4c*6 |
  2d*6 f*6 a*6 4f*6 |
  2d*6 b*5 g*5 4d*6 |
  4c*6 4e*6 |
  8c*6$fermata |

Pattern %IVCOD_C_0_0_100:
  key=C 8: 100@
  2c*6 e*6 g*6 4c*6 |
  2a*5 c*6 f*6 4a*6 |
  2g*5 b*5 d*6 4g*6 |
  4e*6 4c*6 |
  2d*6 f*6 a*6 4f*6 |
  2d*6 b*5 g*5 4d*6 |
  4c*6 4e*6 |
  8c*6$fermata |

Pattern %IVCOD_C_0_m1_100:
  key=C 8: 100@
  2c*5 e*5 g*5 4c*5 |
  2a*4 c*5 f*5 4a*5 |
  2g*4 b*4 d*5 4g*5 |
  4e*5 4c*5 |
  2d*5 f*5 a*5 4f*5 |
  2d*5 b*4 g*4 4d*5 |
  4c*5 4e*5 |
  8c*5$fermata |

Pattern %arp_I0_08_40:
  key=Cm 8: 40@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |

Pattern %arp_I4_08_45:
  key=Eb 8: 45@
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  b*4 d*5 f*5 a*5 f*5 d*5 f*5 d*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |

Pattern %arp_I12_08_45:
  key=C 8: 45@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %arp_II1_08_40:
  key=Ab 8: 40@
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  e*5 g*5 b*5 d*6 b*5 g*5 b*5 g*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |

Pattern %arp_II3_08_42:
  key=Fm 8: 42@
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |

Pattern %arp_III3_08_42:
  key=C 8: 42@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %IVSUBJ_C_7_0_90:
  key=C 8: 90@
  g*5 a*5 b*5 c*6 2d*6 2b*5 |
  e*6 d*6 c*6 b*5 2a*5 2g*5 |

Pattern %chords_IV5_816_60:
  key=C 4: 60@
  C'1 |
  Am'1 |
  Dm'1 |
  G7'1 |
  C'1 |
  F'1 |
  G7'1 |
  G7'1 |

Pattern %IVCHA_C_0_0_80:
  key=C 8: 80@
  4e*5 4g*5 |
  4g*5 4d*6 |
  4c*6 4e*6 |
  4d*6 4g*5 |
  4a*5 4c*6 |
  4g*5 4e*5 |
  4f*5 4a*5 |
  4g*5 4d*6 |

Pattern %IVCHB_C_0_0_80:
  key=C 8: 80@
  4e*6 4c*6 |
  4b*5 4g*5 |
  4a*5 4c*6 |
  4e*6 4g*6 |
  4f*6 4d*6 |
  4d*6 4bn*5 |
  4c*6 4e*6 |
  6g*5 2r |

Pattern %chords_I0_08_40:
  key=Cm 4: 40@
  Cm'1 |
  Ab'1 |
  Fm'1 |
  G7'1 |
  Cm'1 |
  Ab'1 |
  Fm'1 |
  G7'1 |

Pattern %arp_I1_08_75:
  key=Cm 8: 75@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %arp_I2_08_82:
  key=Cm 8: 82@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %arp_I3_08_60:
  key=Cm 8: 60@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |
  b*4 db*5 f*5 db*5 b*4 db*5 f*5 db*5 |
  f*5 an*5 c*6 e*6 c*6 an*5 c*6 an*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  b*4 d*5 f*5 a*5 f*5 d*5 f*5 d*5 |

Pattern %arp_I4_08_55:
  key=Eb 8: 55@
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  b*4 d*5 f*5 a*5 f*5 d*5 f*5 d*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |

Pattern %arp_I5_08_60:
  key=Eb 8: 60@
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  b*4 d*5 f*5 a*5 f*5 d*5 f*5 d*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |

Pattern %arp_I6_08_70:
  key=Eb 8: 70@
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  b*4 d*5 f*5 a*5 f*5 d*5 f*5 d*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  b*4 d*5 f*5 a*5 f*5 d*5 f*5 d*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |

Pattern %arp_I7_08_76:
  key=Cm 8: 76@
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  d*5 f#*5 an*5 c*6 an*5 f#*5 an*5 f#*5 |
  b*4 db*5 f*5 db*5 b*4 db*5 f*5 db*5 |
  f*5 an*5 c*6 e*6 c*6 an*5 c*6 an*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |

Pattern %arp_I8_08_63:
  key=Cm 8: 63@
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  db*5 f*5 a*5 f*5 db*5 f*5 a*5 f*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  f*5 an*5 c*6 an*5 f*5 an*5 c*6 an*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |

Pattern %arp_I9_08_82:
  key=Cm 8: 82@
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 bn*5 d*6 bn*5 g*5 bn*5 d*6 bn*5 |
  g*5 bn*5 d*6 bn*5 g*5 bn*5 d*6 bn*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |

Pattern %arp_I10_08_88:
  key=Cm 8: 88@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %arp_I11_08_63:
  key=Cm 8: 63@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |

Pattern %arp_I12_08_57:
  key=C 8: 57@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %arp_I13_08_63:
  key=C 8: 63@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %arp_I14_08_90:
  key=C 8: 90@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %chords_II1_08_35:
  key=Ab 4: 35@
  Ab'1 |
  Eb/G'1 |
  Fm'1 |
  Db'1 |
  Ab'1 |
  Bbm'1 |
  Eb7'1 |
  Ab'1 |

Pattern %chords_II2_08_40:
  key=Ab 4: 40@
  Ab'1 |
  Eb/G'1 |
  Fm'1 |
  Db'1 |
  Ab'1 |
  Bbm'1 |
  Eb7'1 |
  Ab'1 |

Pattern %arp_II3_08_43:
  key=Fm 8: 43@
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 en*5 g*5 b*5 g*5 en*5 g*5 en*5 |

Pattern %chords_II4_08_42:
  key=Ab 4: 42@
  Ab'1 |
  Eb/G'1 |
  Fm'1 |
  Db'1 |
  Ab'1 |
  Bbm'1 |
  Eb7'1 |
  Ab'1 |

Pattern %chords_II5_08_38:
  key=Ab 4: 38@
  Db'1 |
  Bbm'1 |
  Eb7'1 |
  Ab'1 |
  Fm'1 |
  Db'1 |
  Eb7'1 |
  Ab'1 |

Pattern %arp_III1_08_60:
  key=Cm 8: 60@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %arp_III2_08_63:
  key=Gm 8: 63@
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  d*5 f#*5 a*5 c*6 a*5 f#*5 a*5 f#*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  d*5 f#*5 a*5 c*6 a*5 f#*5 a*5 f#*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |

Pattern %chords_III3_08_45:
  key=C 4: 45@
  C'1 |
  C'1 |
  G'1 |
  C'1 |
  F'1 |
  C'1 |
  G7'1 |
  C'1 |

Pattern %chords_III4_08_49:
  key=G 4: 49@
  G'1 |
  G'1 |
  D'1 |
  G'1 |
  C'1 |
  G'1 |
  D7'1 |
  G'1 |

Pattern %arp_III5_08_65:
  key=Cm 8: 65@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 bn*5 d*6 f*6 d*6 bn*5 d*6 bn*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %arp_III6_08_67:
  key=Gm 8: 67@
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  d*5 f#*5 a*5 c*6 a*5 f#*5 a*5 f#*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  d*5 f#*5 a*5 c*6 a*5 f#*5 a*5 f#*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |

Pattern %arp_IV1_08_88:
  key=C 8: 88@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |

Pattern %arp_IV2_08_78:
  key=C 8: 78@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |

Pattern %arp_IV3_08_82:
  key=G 8: 82@
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  b*4 d*5 f*5 d*5 b*4 d*5 f*5 d*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  d*5 f*5 a*5 c*6 a*5 f*5 a*5 f*5 |

Pattern %arp_IV4_08_84:
  key=C 8: 84@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |

Pattern %IVSUBJ_C_0_0_86:
  key=C 8: 86@
  c*5 d*5 e*5 f*5 2g*5 2e*5 |
  a*5 g*5 f*5 e*5 2d*5 2c*5 |

Pattern %arp_IV5_616_60:
  key=C 8: 60@
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  a*4 c*5 e*5 c*5 a*4 c*5 e*5 c*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |

Pattern %chords_IV7_016_60:
  key=C 4: 60@
  C'1 |
  G/B'1 |
  Am'1 |
  C/G'1 |
  F'1 |
  C/E'1 |
  Dm'1 |
  G7'1 |
  Am'1 |
  Em'1 |
  F'1 |
  C'1 |
  Dm'1 |
  G7'1 |
  C'1 |
  G7'1 |

Pattern %arp_IV9_08_90:
  key=C 8: 90@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |

Pattern %arp_IV10_08_92:
  key=C 8: 92@
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 f*5 a*5 c*6 a*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  g*5 b*5 d*6 f*6 d*6 b*5 d*6 b*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |

Pattern %chords_I1_08_80:
  key=Cm 4: 80@
  Cm'1 |
  Cm'1 |
  Fm'1 |
  G7'1 |
  Cm'1 |
  Ab'1 |
  G7'1 |
  Cm'1 |

Pattern %chords_I2_08_87:
  key=Cm 4: 87@
  Cm'1 |
  Cm'1 |
  Fm'1 |
  G7'1 |
  Cm'1 |
  Ab'1 |
  G7'1 |
  Cm'1 |

Pattern %chords_I3_08_60:
  key=Cm 4: 60@
  Cm'1 |
  G7'1 |
  Fm'1 |
  C7'1 |
  Bbm'1 |
  F7'1 |
  Eb'1 |
  Bb7'1 |

Pattern %chords_I4_08_55:
  key=Eb 4: 55@
  Eb'1 |
  Bb/D'1 |
  Cm'1 |
  Ab'1 |
  Eb'1 |
  Fm'1 |
  Bb7'1 |
  Eb'1 |

Pattern %chords_I5_08_60:
  key=Eb 4: 60@
  Eb'1 |
  Bb/D'1 |
  Cm'1 |
  Ab'1 |
  Eb'1 |
  Fm'1 |
  Bb7'1 |
  Eb'1 |

Pattern %chords_I6_08_75:
  key=Eb 4: 75@
  Eb'1 |
  Ab'1 |
  Fm'1 |
  Bb7'1 |
  Eb'1 |
  Ab'1 |
  Bb7'1 |
  Eb'1 |

Pattern %chords_I7_08_81:
  key=Cm 4: 81@
  Fm'1 |
  C7'1 |
  Gm'1 |
  D7'1 |
  Bbm'1 |
  F7'1 |
  Cm'1 |
  G7'1 |

Pattern %chords_I8_08_63:
  key=Cm 4: 63@
  Eb'1 |
  Bb/D'1 |
  Db'1 |
  Ab/C'1 |
  Bb'1 |
  F/A'1 |
  Ab'1 |
  Eb/G'1 |

Pattern %chords_I9_08_87:
  key=Cm 4: 87@
  Ab'1 |
  Fm'1 |
  G'1 |
  G'1 |
  G7'1 |
  G7'1 |
  G7'1 |
  G7'1 |

Pattern %chords_I10_08_93:
  key=Cm 4: 93@
  Cm'1 |
  Cm'1 |
  Fm'1 |
  G7'1 |
  Cm'1 |
  Ab'1 |
  G7'1 |
  Cm'1 |

Pattern %chords_I11_08_63:
  key=Cm 4: 63@
  Cm'1 |
  G7'1 |
  Fm'1 |
  C7'1 |
  Cm'1 |
  G7'1 |
  Fm'1 |
  G7'1 |

Pattern %chords_I12_08_57:
  key=C 4: 57@
  C'1 |
  G/B'1 |
  Am'1 |
  F'1 |
  C'1 |
  Dm'1 |
  G7'1 |
  C'1 |

Pattern %chords_I13_08_63:
  key=C 4: 63@
  C'1 |
  G/B'1 |
  Am'1 |
  F'1 |
  C'1 |
  Dm'1 |
  G7'1 |
  C'1 |

Pattern %chords_I14_08_95:
  key=C 4: 95@
  C'1 |
  F'1 |
  G7'1 |
  C'1 |
  Am'1 |
  F'1 |
  G7'1 |
  C'1 |

Pattern %chords_II3_08_43:
  key=Fm 4: 43@
  Fm'1 |
  C7'1 |
  Fm'1 |
  Db'1 |
  Bbm'1 |
  C7'1 |
  Fm'1 |
  C7'1 |

Pattern %stab_III1_08_70:
  key=Cm 4: 70@
  r Cm! r Cm! |
  r Cm! r Cm! |
  r G7! r G7! |
  r Cm! r Cm! |
  r Fm! r Fm! |
  r Cm! r Cm! |
  r G7! r G7! |
  r Cm! r Cm! |

Pattern %stab_III2_08_73:
  key=Gm 4: 73@
  r Gm! r Gm! |
  r Gm! r Gm! |
  r D7! r D7! |
  r Gm! r Gm! |
  r Cm! r Cm! |
  r Gm! r Gm! |
  r D7! r D7! |
  r Gm! r Gm! |

Pattern %stab_III5_08_75:
  key=Cm 4: 75@
  r Cm! r Cm! |
  r Cm! r Cm! |
  r G7! r G7! |
  r Cm! r Cm! |
  r Fm! r Fm! |
  r Cm! r Cm! |
  r G7! r G7! |
  r Cm! r Cm! |

Pattern %stab_III6_08_77:
  key=Gm 4: 77@
  r Gm! r Gm! |
  r Gm! r Gm! |
  r D7! r D7! |
  r Gm! r Gm! |
  r Cm! r Cm! |
  r Gm! r Gm! |
  r D7! r D7! |
  r Gm! r Gm! |

Pattern %chords_IV1_08_93:
  key=C 4: 93@
  C'1 |
  C'1 |
  G'1 |
  G'1 |
  Am'1 |
  F'1 |
  G7'1 |
  G7'1 |

Pattern %chords_IV2_08_83:
  key=C 4: 83@
  C'1 |
  G/B'1 |
  Am'1 |
  Em'1 |
  F'1 |
  C/E'1 |
  Dm'1 |
  G7'1 |

Pattern %chords_IV3_08_87:
  key=G 4: 87@
  G'1 |
  D/F#'1 |
  Em'1 |
  Bm'1 |
  C'1 |
  G/B'1 |
  Am'1 |
  D7'1 |

Pattern %chords_IV4_08_89:
  key=C 4: 89@
  C'1 |
  G/B'1 |
  Am'1 |
  Em'1 |
  F'1 |
  C/E'1 |
  Dm'1 |
  G7'1 |

Pattern %IVSUBJ_C_7_m1_82:
  key=C 8: 82@
  g*4 a*4 b*4 c*5 2d*5 2b*4 |
  e*5 d*5 c*5 b*4 2a*4 2g*4 |

Pattern %chords_IV5_416_60:
  key=C 4: 60@
  C'1 |
  C'1 |
  G'1 |
  G'1 |
  C'1 |
  Am'1 |
  Dm'1 |
  G7'1 |
  C'1 |
  F'1 |
  G7'1 |
  G7'1 |

Pattern %chords_IV7_016_62:
  key=C 4: 62@
  C'1 |
  G/B'1 |
  Am'1 |
  C/G'1 |
  F'1 |
  C/E'1 |
  Dm'1 |
  G7'1 |
  Am'1 |
  Em'1 |
  F'1 |
  C'1 |
  Dm'1 |
  G7'1 |
  C'1 |
  G7'1 |

Pattern %chords_IV9_08_95:
  key=C 4: 95@
  C'1 |
  C'1 |
  F'1 |
  F'1 |
  G'1 |
  G'1 |
  C'1 |
  G7'1 |

Pattern %chords_IV10_08_97:
  key=C 4: 97@
  C'1 |
  F'1 |
  G7'1 |
  C'1 |
  Dm'1 |
  G7'1 |
  C'1 |
  C'1 |

Pattern %rootsW_I0_08_50:
  key=Cm 4: 50@
  c*2'1 |
  a*2'1 |
  f*2'1 |
  g*2'1 |
  c*2'1 |
  a*2'1 |
  f*2'1 |
  g*2'1 |

Pattern %rootsC_I1_08_87:
  key=Cm 4: 87@
  c*2 c*3 c*2 c*3 |
  c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  a*2 a*3 a*2 a*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |

Pattern %rootsC_I2_08_94:
  key=Cm 4: 94@
  c*2 c*3 c*2 c*3 |
  c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  a*2 a*3 a*2 a*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |

Pattern %rootsC_I3_08_70:
  key=Cm 4: 70@
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |
  f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 |
  b*2 b*3 b*2 b*3 |
  f*2 f*3 f*2 f*3 |
  e*2 e*3 e*2 e*3 |
  b*2 b*3 b*2 b*3 |

Pattern %rootsC_I4_08_65:
  key=Eb 4: 65@
  e*2 e*3 e*2 e*3 |
  d*2 d*3 d*2 d*3 |
  c*2 c*3 c*2 c*3 |
  a*2 a*3 a*2 a*3 |
  e*2 e*3 e*2 e*3 |
  f*2 f*3 f*2 f*3 |
  b*2 b*3 b*2 b*3 |
  e*2 e*3 e*2 e*3 |

Pattern %rootsC_I5_08_70:
  key=Eb 4: 70@
  e*2 e*3 e*2 e*3 |
  d*2 d*3 d*2 d*3 |
  c*2 c*3 c*2 c*3 |
  a*2 a*3 a*2 a*3 |
  e*2 e*3 e*2 e*3 |
  f*2 f*3 f*2 f*3 |
  b*2 b*3 b*2 b*3 |
  e*2 e*3 e*2 e*3 |

Pattern %rootsC_I6_08_82:
  key=Eb 4: 82@
  e*2 e*3 e*2 e*3 |
  a*2 a*3 a*2 a*3 |
  f*2 f*3 f*2 f*3 |
  b*2 b*3 b*2 b*3 |
  e*2 e*3 e*2 e*3 |
  a*2 a*3 a*2 a*3 |
  b*2 b*3 b*2 b*3 |
  e*2 e*3 e*2 e*3 |

Pattern %rootsC_I7_08_88:
  key=Cm 4: 88@
  f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |
  d*2 d*3 d*2 d*3 |
  b*2 b*3 b*2 b*3 |
  f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |

Pattern %rootsC_I8_08_73:
  key=Cm 4: 73@
  e*2 e*3 e*2 e*3 |
  d*2 d*3 d*2 d*3 |
  db*2 db*3 db*2 db*3 |
  c*2 c*3 c*2 c*3 |
  b*2 b*3 b*2 b*3 |
  an*2 an*3 an*2 an*3 |
  a*2 a*3 a*2 a*3 |
  g*2 g*3 g*2 g*3 |

Pattern %rootsC_I9_08_94:
  key=Cm 4: 94@
  a*2 a*3 a*2 a*3 |
  f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |

Pattern %rootsC_I10_08_100:
  key=Cm 4: 100@
  c*2 c*3 c*2 c*3 |
  c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  a*2 a*3 a*2 a*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |

Pattern %rootsC_I11_08_73:
  key=Cm 4: 73@
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |
  f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 |
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |
  f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 |

Pattern %rootsC_I12_08_67:
  key=C 4: 67@
  c*2 c*3 c*2 c*3 |
  b*2 b*3 b*2 b*3 |
  a*2 a*3 a*2 a*3 |
  f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 |
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |

Pattern %rootsC_I13_08_73:
  key=C 4: 73@
  c*2 c*3 c*2 c*3 |
  b*2 b*3 b*2 b*3 |
  a*2 a*3 a*2 a*3 |
  f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 |
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |

Pattern %rootsC_I14_08_102:
  key=C 4: 102@
  c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  a*2 a*3 a*2 a*3 |
  f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |

Pattern %rootsW_II1_08_45:
  key=Ab 4: 45@
  a*2'1 |
  g*2'1 |
  f*2'1 |
  d*2'1 |
  a*2'1 |
  b*2'1 |
  e*2'1 |
  a*2'1 |

Pattern %rootsW_II2_08_50:
  key=Ab 4: 50@
  a*2'1 |
  g*2'1 |
  f*2'1 |
  d*2'1 |
  a*2'1 |
  b*2'1 |
  e*2'1 |
  a*2'1 |

Pattern %rootsC_II3_08_53:
  key=Fm 4: 53@
  f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 |
  d*2 d*3 d*2 d*3 |
  b*2 b*3 b*2 b*3 |
  c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 |

Pattern %rootsW_II5_08_48:
  key=Ab 4: 48@
  d*2'1 |
  b*2'1 |
  e*2'1 |
  a*2'1 |
  f*2'1 |
  d*2'1 |
  e*2'1 |
  a*2'1 |

Pattern %rootsC_III1_08_80:
  key=Cm 4: 80@
  c*2 c*3 c*2 c*3 |
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |

Pattern %rootsC_III2_08_83:
  key=Gm 4: 83@
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |

Pattern %rootsW_III3_08_55:
  key=C 4: 55@
  c*2'1 |
  c*2'1 |
  g*2'1 |
  c*2'1 |
  f*2'1 |
  c*2'1 |
  g*2'1 |
  c*2'1 |

Pattern %rootsW_III4_08_59:
  key=G 4: 59@
  g*2'1 |
  g*2'1 |
  d*2'1 |
  g*2'1 |
  c*2'1 |
  g*2'1 |
  d*2'1 |
  g*2'1 |

Pattern %rootsC_III5_08_85:
  key=Cm 4: 85@
  c*2 c*3 c*2 c*3 |
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |

Pattern %rootsC_III6_08_87:
  key=Gm 4: 87@
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |

Pattern %rootsC_IV1_08_100:
  key=C 4: 100@
  c*2 c*3 c*2 c*3 |
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 |
  f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |

Pattern %rootsC_IV2_08_90:
  key=C 4: 90@
  c*2 c*3 c*2 c*3 |
  b*2 b*3 b*2 b*3 |
  a*2 a*3 a*2 a*3 |
  e*2 e*3 e*2 e*3 |
  f*2 f*3 f*2 f*3 |
  e*2 e*3 e*2 e*3 |
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |

Pattern %rootsC_IV3_08_94:
  key=G 4: 94@
  g*2 g*3 g*2 g*3 |
  f*2 f*3 f*2 f*3 |
  e*2 e*3 e*2 e*3 |
  b*2 b*3 b*2 b*3 |
  c*2 c*3 c*2 c*3 |
  b*2 b*3 b*2 b*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |

Pattern %IVSUBJ_C_0_m2_78:
  key=C 8: 78@
  c*3 d*3 e*3 f*3 2g*3 2e*3 |
  a*3 g*3 f*3 e*3 2d*3 2c*3 |

Pattern %rootsC_IV5_216_60:
  key=C 4: 60@
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |

Pattern %rootsW_IV7_016_66:
  key=C 4: 66@
  c*2'1 |
  b*2'1 |
  a*2'1 |
  g*2'1 |
  f*2'1 |
  e*2'1 |
  d*2'1 |
  g*2'1 |
  a*2'1 |
  e*2'1 |
  f*2'1 |
  c*2'1 |
  d*2'1 |
  g*2'1 |
  c*2'1 |
  g*2'1 |

Pattern %rootsC_IV9_08_102:
  key=C 4: 102@
  c*2 c*3 c*2 c*3 |
  c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 |
  f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  g*2 g*3 g*2 g*3 |

Pattern %rootsC_IV10_08_104:
  key=C 4: 104@
  c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  c*2 c*3 c*2 c*3 |

Pattern %rootsB_I0_08_48:
  key=Cm 4: 48@
  c*2'1 |
  a*1'1 |
  f*1'1 |
  g*1'1 |
  c*2'1 |
  a*1'1 |
  f*1'1 |
  g*1'1 |

Pattern %rootsB_I1_08_89:
  key=Cm 4: 89@
  c*2'1 |
  c*2'1 |
  f*1'1 |
  g*1'1 |
  c*2'1 |
  a*1'1 |
  g*1'1 |
  c*2'1 |

Pattern %rootsB_I2_08_96:
  key=Cm 4: 96@
  c*2'1 |
  c*2'1 |
  f*1'1 |
  g*1'1 |
  c*2'1 |
  a*1'1 |
  g*1'1 |
  c*2'1 |

Pattern %rootsB_I3_08_73:
  key=Cm 4: 73@
  c*2'1 |
  g*1'1 |
  f*1'1 |
  c*2'1 |
  b*1'1 |
  f*1'1 |
  e*2'1 |
  b*1'1 |

Pattern %rootsB_I4_08_68:
  key=Eb 4: 68@
  e*2'1 |
  d*2'1 |
  c*2'1 |
  a*1'1 |
  e*2'1 |
  f*1'1 |
  b*1'1 |
  e*2'1 |

Pattern %rootsB_I5_08_73:
  key=Eb 4: 73@
  e*2'1 |
  d*2'1 |
  c*2'1 |
  a*1'1 |
  e*2'1 |
  f*1'1 |
  b*1'1 |
  e*2'1 |

Pattern %rootsB_I6_08_84:
  key=Eb 4: 84@
  e*2'1 |
  a*1'1 |
  f*1'1 |
  b*1'1 |
  e*2'1 |
  a*1'1 |
  b*1'1 |
  e*2'1 |

Pattern %rootsB_I7_08_90:
  key=Cm 4: 90@
  f*1'1 |
  c*2'1 |
  g*1'1 |
  d*2'1 |
  b*1'1 |
  f*1'1 |
  c*2'1 |
  g*1'1 |

Pattern %rootsB_I8_08_76:
  key=Cm 4: 76@
  e*2'1 |
  d*2'1 |
  db*2'1 |
  c*2'1 |
  b*1'1 |
  an*1'1 |
  a*1'1 |
  g*1'1 |

Pattern %rootsB_I9_08_96:
  key=Cm 4: 96@
  a*1'1 |
  f*1'1 |
  g*1'1 |
  g*1'1 |
  g*1'1 |
  g*1'1 |
  g*1'1 |
  g*1'1 |

Pattern %rootsB_I10_08_102:
  key=Cm 4: 102@
  c*2'1 |
  c*2'1 |
  f*1'1 |
  g*1'1 |
  c*2'1 |
  a*1'1 |
  g*1'1 |
  c*2'1 |

Pattern %rootsB_I11_08_76:
  key=Cm 4: 76@
  c*2'1 |
  g*1'1 |
  f*1'1 |
  c*2'1 |
  c*2'1 |
  g*1'1 |
  f*1'1 |
  g*1'1 |

Pattern %rootsB_I12_08_70:
  key=C 4: 70@
  c*2'1 |
  b*1'1 |
  a*1'1 |
  f*1'1 |
  c*2'1 |
  d*2'1 |
  g*1'1 |
  c*2'1 |

Pattern %rootsB_I13_08_76:
  key=C 4: 76@
  c*2'1 |
  b*1'1 |
  a*1'1 |
  f*1'1 |
  c*2'1 |
  d*2'1 |
  g*1'1 |
  c*2'1 |

Pattern %rootsB_I14_08_104:
  key=C 4: 104@
  c*2'1 |
  f*1'1 |
  g*1'1 |
  c*2'1 |
  a*1'1 |
  f*1'1 |
  g*1'1 |
  c*2'1 |

Pattern %rootsB_II1_08_43:
  key=Ab 4: 43@
  a*1'1 |
  g*1'1 |
  f*1'1 |
  d*2'1 |
  a*1'1 |
  b*1'1 |
  e*2'1 |
  a*1'1 |

Pattern %rootsB_II2_08_48:
  key=Ab 4: 48@
  a*1'1 |
  g*1'1 |
  f*1'1 |
  d*2'1 |
  a*1'1 |
  b*1'1 |
  e*2'1 |
  a*1'1 |

Pattern %rootsB_II3_08_56:
  key=Fm 4: 56@
  f*1'1 |
  c*2'1 |
  f*1'1 |
  d*2'1 |
  b*1'1 |
  c*2'1 |
  f*1'1 |
  c*2'1 |

Pattern %rootsB_II4_08_50:
  key=Ab 4: 50@
  a*1'1 |
  g*1'1 |
  f*1'1 |
  d*2'1 |
  a*1'1 |
  b*1'1 |
  e*2'1 |
  a*1'1 |

Pattern %rootsB_II5_08_46:
  key=Ab 4: 46@
  d*2'1 |
  b*1'1 |
  e*2'1 |
  a*1'1 |
  f*1'1 |
  d*2'1 |
  e*2'1 |
  a*1'1 |

Pattern %rootsB_III1_08_80:
  key=Cm 4: 80@
  c*2'1 |
  c*2'1 |
  g*1'1 |
  c*2'1 |
  f*1'1 |
  c*2'1 |
  g*1'1 |
  c*2'1 |

Pattern %rootsB_III2_08_83:
  key=Gm 4: 83@
  g*1'1 |
  g*1'1 |
  d*2'1 |
  g*1'1 |
  c*2'1 |
  g*1'1 |
  d*2'1 |
  g*1'1 |

Pattern %rootsB_III3_08_55:
  key=C 4: 55@
  c*2'1 |
  c*2'1 |
  g*1'1 |
  c*2'1 |
  f*1'1 |
  c*2'1 |
  g*1'1 |
  c*2'1 |

Pattern %rootsB_III4_08_59:
  key=G 4: 59@
  g*1'1 |
  g*1'1 |
  d*2'1 |
  g*1'1 |
  c*2'1 |
  g*1'1 |
  d*2'1 |
  g*1'1 |

Pattern %rootsB_III5_08_85:
  key=Cm 4: 85@
  c*2'1 |
  c*2'1 |
  g*1'1 |
  c*2'1 |
  f*1'1 |
  c*2'1 |
  g*1'1 |
  c*2'1 |

Pattern %rootsB_III6_08_87:
  key=Gm 4: 87@
  g*1'1 |
  g*1'1 |
  d*2'1 |
  g*1'1 |
  c*2'1 |
  g*1'1 |
  d*2'1 |
  g*1'1 |

Pattern %rootsB_IV1_08_102:
  key=C 4: 102@
  c*2'1 |
  c*2'1 |
  g*1'1 |
  g*1'1 |
  a*1'1 |
  f*1'1 |
  g*1'1 |
  g*1'1 |

Pattern %rootsB_IV2_08_92:
  key=C 4: 92@
  c*2'1 |
  b*1'1 |
  a*1'1 |
  e*1'1 |
  f*1'1 |
  e*1'1 |
  d*2'1 |
  g*1'1 |

Pattern %rootsB_IV3_08_96:
  key=G 4: 96@
  g*1'1 |
  f*1'1 |
  e*1'1 |
  b*1'1 |
  c*2'1 |
  b*1'1 |
  a*1'1 |
  d*2'1 |

Pattern %rootsB_IV4_08_98:
  key=C 4: 98@
  c*2'1 |
  b*1'1 |
  a*1'1 |
  e*1'1 |
  f*1'1 |
  e*1'1 |
  d*2'1 |
  g*1'1 |

Pattern %rootsB_IV5_016_75:
  key=C 4: 75@
  c*2'1 |
  c*2'1 |
  g*1'1 |
  g*1'1 |
  c*2'1 |
  c*2'1 |
  g*1'1 |
  g*1'1 |
  c*2'1 |
  a*1'1 |
  d*2'1 |
  g*1'1 |
  c*2'1 |
  f*1'1 |
  g*1'1 |
  g*1'1 |

Pattern %rootsB_IV7_016_66:
  key=C 4: 66@
  c*2'1 |
  b*1'1 |
  a*1'1 |
  g*1'1 |
  f*1'1 |
  e*1'1 |
  d*2'1 |
  g*1'1 |
  a*1'1 |
  e*1'1 |
  f*1'1 |
  c*2'1 |
  d*2'1 |
  g*1'1 |
  c*2'1 |
  g*1'1 |

Pattern %rootsB_IV9_08_104:
  key=C 4: 104@
  c*2'1 |
  c*2'1 |
  f*1'1 |
  f*1'1 |
  g*1'1 |
  g*1'1 |
  c*2'1 |
  g*1'1 |

Pattern %rootsB_IV10_08_106:
  key=C 4: 106@
  c*2'1 |
  f*1'1 |
  g*1'1 |
  c*2'1 |
  d*2'1 |
  g*1'1 |
  c*2'1 |
  c*2'1 |

Pattern %IVSUBJ_C_7_0_98:
  key=C 8: 98@
  g*5 a*5 b*5 c*6 2d*6 2b*5 |
  e*6 d*6 c*6 b*5 2a*5 2g*5 |

Pattern %IVCHA_C_0_0_72:
  key=C 8: 72@
  4e*5 4g*5 |
  4g*5 4d*6 |
  4c*6 4e*6 |
  4d*6 4g*5 |
  4a*5 4c*6 |
  4g*5 4e*5 |
  4f*5 4a*5 |
  4g*5 4d*6 |

Pattern %IVCHB_C_0_0_72:
  key=C 8: 72@
  4e*6 4c*6 |
  4b*5 4g*5 |
  4a*5 4c*6 |
  4e*6 4g*6 |
  4f*6 4d*6 |
  4d*6 4bn*5 |
  4c*6 4e*6 |
  6g*5 2r |

Pattern %IVSUBJ_C_0_0_94:
  key=C 8: 94@
  c*5 d*5 e*5 f*5 2g*5 2e*5 |
  a*5 g*5 f*5 e*5 2d*5 2c*5 |

Pattern %IVCHA_C_0_m1_70:
  key=C 8: 70@
  4e*4 4g*4 |
  4g*4 4d*5 |
  4c*5 4e*5 |
  4d*5 4g*4 |
  4a*4 4c*5 |
  4g*4 4e*4 |
  4f*4 4a*4 |
  4g*4 4d*5 |

Pattern %IVCHB_C_0_m1_70:
  key=C 8: 70@
  4e*5 4c*5 |
  4b*4 4g*4 |
  4a*4 4c*5 |
  4e*5 4g*5 |
  4f*5 4d*5 |
  4d*5 4b*4 |
  4c*5 4e*5 |
  6g*4 2r |

Pattern %rootsF_I0_08_50:
  key=Cm 4: 50@
  c*2'1 |
  a*2'1 |
  f*2'1 |
  g*2'1 |
  c*2'1 |
  a*2'1 |
  f*2'1 |
  g*2'1 |

Pattern %rootsF_I1_08_85:
  key=Cm 4: 85@
  c*2'1 |
  c*2'1 |
  f*2'1 |
  g*2'1 |
  c*2'1 |
  a*2'1 |
  g*2'1 |
  c*2'1 |

Pattern %rootsF_I2_08_92:
  key=Cm 4: 92@
  c*2'1 |
  c*2'1 |
  f*2'1 |
  g*2'1 |
  c*2'1 |
  a*2'1 |
  g*2'1 |
  c*2'1 |

Pattern %rootsF_I3_08_75:
  key=Cm 4: 75@
  c*2'1 |
  g*2'1 |
  f*2'1 |
  c*2'1 |
  b*2'1 |
  f*2'1 |
  e*2'1 |
  b*2'1 |

Pattern %rootsF_I4_08_70:
  key=Eb 4: 70@
  e*2'1 |
  d*2'1 |
  c*2'1 |
  a*2'1 |
  e*2'1 |
  f*2'1 |
  b*2'1 |
  e*2'1 |

Pattern %rootsF_I5_08_75:
  key=Eb 4: 75@
  e*2'1 |
  d*2'1 |
  c*2'1 |
  a*2'1 |
  e*2'1 |
  f*2'1 |
  b*2'1 |
  e*2'1 |

Pattern %rootsF_I6_08_80:
  key=Eb 4: 80@
  e*2'1 |
  a*2'1 |
  f*2'1 |
  b*2'1 |
  e*2'1 |
  a*2'1 |
  b*2'1 |
  e*2'1 |

Pattern %rootsF_I7_08_86:
  key=Cm 4: 86@
  f*2'1 |
  c*2'1 |
  g*2'1 |
  d*2'1 |
  b*2'1 |
  f*2'1 |
  c*2'1 |
  g*2'1 |

Pattern %rootsF_I8_08_78:
  key=Cm 4: 78@
  e*2'1 |
  d*2'1 |
  db*2'1 |
  c*2'1 |
  b*2'1 |
  an*2'1 |
  a*2'1 |
  g*2'1 |

Pattern %rootsF_I9_08_92:
  key=Cm 4: 92@
  a*2'1 |
  f*2'1 |
  g*2'1 |
  g*2'1 |
  g*2'1 |
  g*2'1 |
  g*2'1 |
  g*2'1 |

Pattern %rootsF_I10_08_98:
  key=Cm 4: 98@
  c*2'1 |
  c*2'1 |
  f*2'1 |
  g*2'1 |
  c*2'1 |
  a*2'1 |
  g*2'1 |
  c*2'1 |

Pattern %rootsF_I11_08_78:
  key=Cm 4: 78@
  c*2'1 |
  g*2'1 |
  f*2'1 |
  c*2'1 |
  c*2'1 |
  g*2'1 |
  f*2'1 |
  g*2'1 |

Pattern %rootsF_I12_08_72:
  key=C 4: 72@
  c*2'1 |
  b*2'1 |
  a*2'1 |
  f*2'1 |
  c*2'1 |
  d*2'1 |
  g*2'1 |
  c*2'1 |

Pattern %rootsF_I13_08_78:
  key=C 4: 78@
  c*2'1 |
  b*2'1 |
  a*2'1 |
  f*2'1 |
  c*2'1 |
  d*2'1 |
  g*2'1 |
  c*2'1 |

Pattern %rootsF_I14_08_100:
  key=C 4: 100@
  c*2'1 |
  f*2'1 |
  g*2'1 |
  c*2'1 |
  a*2'1 |
  f*2'1 |
  g*2'1 |
  c*2'1 |

Pattern %rootsF_II1_08_45:
  key=Ab 4: 45@
  a*2'1 |
  g*2'1 |
  f*2'1 |
  d*2'1 |
  a*2'1 |
  b*2'1 |
  e*2'1 |
  a*2'1 |

Pattern %rootsF_II2_08_50:
  key=Ab 4: 50@
  a*2'1 |
  g*2'1 |
  f*2'1 |
  d*2'1 |
  a*2'1 |
  b*2'1 |
  e*2'1 |
  a*2'1 |

Pattern %rootsF_II3_08_58:
  key=Fm 4: 58@
  f*2'1 |
  c*2'1 |
  f*2'1 |
  d*2'1 |
  b*2'1 |
  c*2'1 |
  f*2'1 |
  c*2'1 |

Pattern %rootsF_II4_08_52:
  key=Ab 4: 52@
  a*2'1 |
  g*2'1 |
  f*2'1 |
  d*2'1 |
  a*2'1 |
  b*2'1 |
  e*2'1 |
  a*2'1 |

Pattern %rootsF_II5_08_48:
  key=Ab 4: 48@
  d*2'1 |
  b*2'1 |
  e*2'1 |
  a*2'1 |
  f*2'1 |
  d*2'1 |
  e*2'1 |
  a*2'1 |

Pattern %rootsF_III1_08_75:
  key=Cm 4: 75@
  c*2'1 |
  c*2'1 |
  g*2'1 |
  c*2'1 |
  f*2'1 |
  c*2'1 |
  g*2'1 |
  c*2'1 |

Pattern %rootsF_III2_08_78:
  key=Gm 4: 78@
  g*2'1 |
  g*2'1 |
  d*2'1 |
  g*2'1 |
  c*2'1 |
  g*2'1 |
  d*2'1 |
  g*2'1 |

Pattern %rootsF_III3_08_55:
  key=C 4: 55@
  c*2'1 |
  c*2'1 |
  g*2'1 |
  c*2'1 |
  f*2'1 |
  c*2'1 |
  g*2'1 |
  c*2'1 |

Pattern %rootsF_III4_08_59:
  key=G 4: 59@
  g*2'1 |
  g*2'1 |
  d*2'1 |
  g*2'1 |
  c*2'1 |
  g*2'1 |
  d*2'1 |
  g*2'1 |

Pattern %rootsF_III5_08_80:
  key=Cm 4: 80@
  c*2'1 |
  c*2'1 |
  g*2'1 |
  c*2'1 |
  f*2'1 |
  c*2'1 |
  g*2'1 |
  c*2'1 |

Pattern %rootsF_III6_08_82:
  key=Gm 4: 82@
  g*2'1 |
  g*2'1 |
  d*2'1 |
  g*2'1 |
  c*2'1 |
  g*2'1 |
  d*2'1 |
  g*2'1 |

Pattern %rootsF_IV1_08_98:
  key=C 4: 98@
  c*2'1 |
  c*2'1 |
  g*2'1 |
  g*2'1 |
  a*2'1 |
  f*2'1 |
  g*2'1 |
  g*2'1 |

Pattern %rootsF_IV2_08_88:
  key=C 4: 88@
  c*2'1 |
  b*2'1 |
  a*2'1 |
  e*2'1 |
  f*2'1 |
  e*2'1 |
  d*2'1 |
  g*2'1 |

Pattern %rootsF_IV3_08_92:
  key=G 4: 92@
  g*2'1 |
  f*2'1 |
  e*2'1 |
  b*2'1 |
  c*2'1 |
  b*2'1 |
  a*2'1 |
  d*2'1 |

Pattern %rootsF_IV4_08_94:
  key=C 4: 94@
  c*2'1 |
  b*2'1 |
  a*2'1 |
  e*2'1 |
  f*2'1 |
  e*2'1 |
  d*2'1 |
  g*2'1 |

Pattern %rootsF_IV5_016_70:
  key=C 4: 70@
  c*2'1 |
  c*2'1 |
  g*2'1 |
  g*2'1 |
  c*2'1 |
  c*2'1 |
  g*2'1 |
  g*2'1 |
  c*2'1 |
  a*2'1 |
  d*2'1 |
  g*2'1 |
  c*2'1 |
  f*2'1 |
  g*2'1 |
  g*2'1 |

Pattern %rootsF_IV7_016_70:
  key=C 4: 70@
  c*2'1 |
  b*2'1 |
  a*2'1 |
  g*2'1 |
  f*2'1 |
  e*2'1 |
  d*2'1 |
  g*2'1 |
  a*2'1 |
  e*2'1 |
  f*2'1 |
  c*2'1 |
  d*2'1 |
  g*2'1 |
  c*2'1 |
  g*2'1 |

Pattern %rootsF_IV9_08_100:
  key=C 4: 100@
  c*2'1 |
  c*2'1 |
  f*2'1 |
  f*2'1 |
  g*2'1 |
  g*2'1 |
  c*2'1 |
  g*2'1 |

Pattern %rootsF_IV10_08_102:
  key=C 4: 102@
  c*2'1 |
  f*2'1 |
  g*2'1 |
  c*2'1 |
  d*2'1 |
  g*2'1 |
  c*2'1 |
  c*2'1 |

Pattern %chords_I1_08_95:
  key=Cm 4: 95@
  Cm'1 |
  Cm'1 |
  Fm'1 |
  G7'1 |
  Cm'1 |
  Ab'1 |
  G7'1 |
  Cm'1 |

Pattern %chords_I2_08_102:
  key=Cm 4: 102@
  Cm'1 |
  Cm'1 |
  Fm'1 |
  G7'1 |
  Cm'1 |
  Ab'1 |
  G7'1 |
  Cm'1 |

Pattern %chords_I6_08_90:
  key=Eb 4: 90@
  Eb'1 |
  Ab'1 |
  Fm'1 |
  Bb7'1 |
  Eb'1 |
  Ab'1 |
  Bb7'1 |
  Eb'1 |

Pattern %chords_I7_08_96:
  key=Cm 4: 96@
  Fm'1 |
  C7'1 |
  Gm'1 |
  D7'1 |
  Bbm'1 |
  F7'1 |
  Cm'1 |
  G7'1 |

Pattern %chords_I9_08_102:
  key=Cm 4: 102@
  Ab'1 |
  Fm'1 |
  G'1 |
  G'1 |
  G7'1 |
  G7'1 |
  G7'1 |
  G7'1 |

Pattern %chords_I10_08_108:
  key=Cm 4: 108@
  Cm'1 |
  Cm'1 |
  Fm'1 |
  G7'1 |
  Cm'1 |
  Ab'1 |
  G7'1 |
  Cm'1 |

Pattern %chords_I14_08_110:
  key=C 4: 110@
  C'1 |
  F'1 |
  G7'1 |
  C'1 |
  Am'1 |
  F'1 |
  G7'1 |
  C'1 |

Pattern %chords_II1_08_45:
  key=Ab 4: 45@
  Ab'1 |
  Eb/G'1 |
  Fm'1 |
  Db'1 |
  Ab'1 |
  Bbm'1 |
  Eb7'1 |
  Ab'1 |

Pattern %chords_II2_08_48:
  key=Ab 4: 48@
  Ab'1 |
  Eb/G'1 |
  Fm'1 |
  Db'1 |
  Ab'1 |
  Bbm'1 |
  Eb7'1 |
  Ab'1 |

Pattern %chords_II4_08_50:
  key=Ab 4: 50@
  Ab'1 |
  Eb/G'1 |
  Fm'1 |
  Db'1 |
  Ab'1 |
  Bbm'1 |
  Eb7'1 |
  Ab'1 |

Pattern %chords_II5_08_50:
  key=Ab 4: 50@
  Db'1 |
  Bbm'1 |
  Eb7'1 |
  Ab'1 |
  Fm'1 |
  Db'1 |
  Eb7'1 |
  Ab'1 |

Pattern %chords_III3_08_40:
  key=C 4: 40@
  C'1 |
  C'1 |
  G'1 |
  C'1 |
  F'1 |
  C'1 |
  G7'1 |
  C'1 |

Pattern %chords_III4_08_44:
  key=G 4: 44@
  G'1 |
  G'1 |
  D'1 |
  G'1 |
  C'1 |
  G'1 |
  D7'1 |
  G'1 |

Pattern %chords_IV1_08_108:
  key=C 4: 108@
  C'1 |
  C'1 |
  G'1 |
  G'1 |
  Am'1 |
  F'1 |
  G7'1 |
  G7'1 |

Pattern %chords_IV2_08_98:
  key=C 4: 98@
  C'1 |
  G/B'1 |
  Am'1 |
  Em'1 |
  F'1 |
  C/E'1 |
  Dm'1 |
  G7'1 |

Pattern %chords_IV3_08_102:
  key=G 4: 102@
  G'1 |
  D/F#'1 |
  Em'1 |
  Bm'1 |
  C'1 |
  G/B'1 |
  Am'1 |
  D7'1 |

Pattern %chords_IV4_08_104:
  key=C 4: 104@
  C'1 |
  G/B'1 |
  Am'1 |
  Em'1 |
  F'1 |
  C/E'1 |
  Dm'1 |
  G7'1 |

Pattern %IVSUBJ_C_0_m1_102:
  key=C 8: 102@
  c*4 d*4 e*4 f*4 2g*4 2e*4 |
  a*4 g*4 f*4 e*4 2d*4 2c*4 |

Pattern %chords_IV5_1416_60:
  key=C 4: 60@
  G7'1 |
  G7'1 |

Pattern %chords_IV7_016_85:
  key=C 4: 85@
  C'1 |
  G/B'1 |
  Am'1 |
  C/G'1 |
  F'1 |
  C/E'1 |
  Dm'1 |
  G7'1 |
  Am'1 |
  Em'1 |
  F'1 |
  C'1 |
  Dm'1 |
  G7'1 |
  C'1 |
  G7'1 |

Pattern %chords_IV9_08_110:
  key=C 4: 110@
  C'1 |
  C'1 |
  F'1 |
  F'1 |
  G'1 |
  G'1 |
  C'1 |
  G7'1 |

Pattern %chords_IV10_08_112:
  key=C 4: 112@
  C'1 |
  F'1 |
  G7'1 |
  C'1 |
  Dm'1 |
  G7'1 |
  C'1 |
  C'1 |

Pattern %IVSUBJ_C_7_m1_106:
  key=C 8: 106@
  g*4 a*4 b*4 c*5 2d*5 2b*4 |
  e*5 d*5 c*5 b*4 2a*4 2g*4 |

Pattern %IVCHA_C_0_m1_90:
  key=C 8: 90@
  4e*4 4g*4 |
  4g*4 4d*5 |
  4c*5 4e*5 |
  4d*5 4g*4 |
  4a*4 4c*5 |
  4g*4 4e*4 |
  4f*4 4a*4 |
  4g*4 4d*5 |

Pattern %IVCHB_C_0_m1_90:
  key=C 8: 90@
  4e*5 4c*5 |
  4b*4 4g*4 |
  4a*4 4c*5 |
  4e*5 4g*5 |
  4f*5 4d*5 |
  4d*5 4b*4 |
  4c*5 4e*5 |
  6g*4 2r |

Pattern %hitS_I0_08_35:
  key=Cm 4: 35@
  c*2 r r r |
  a*1 r r r |
  f*1 r r r |
  g*1 r r r |
  c*2 r r r |
  a*1 r r r |
  f*1 r r r |
  g*1 r r r |

Pattern %hit_I1_08_95:
  key=Cm 4: 95@
  c*2 r c*2 r |
  c*2 r c*2 r |
  f*1 r f*1 r |
  g*1 r g*1 r |
  c*2 r c*2 r |
  a*1 r a*1 r |
  g*1 r g*1 r |
  c*2 r c*2 r |

Pattern %hit_I2_08_102:
  key=Cm 4: 102@
  c*2 r c*2 r |
  c*2 r c*2 r |
  f*1 r f*1 r |
  g*1 r g*1 r |
  c*2 r c*2 r |
  a*1 r a*1 r |
  g*1 r g*1 r |
  c*2 r c*2 r |

Pattern %hitS_I3_08_60:
  key=Cm 4: 60@
  c*2 r r r |
  g*1 r r r |
  f*1 r r r |
  c*2 r r r |
  b*1 r r r |
  f*1 r r r |
  e*2 r r r |
  b*1 r r r |

Pattern %hitS_I4_08_55:
  key=Eb 4: 55@
  e*2 r r r |
  d*2 r r r |
  c*2 r r r |
  a*1 r r r |
  e*2 r r r |
  f*1 r r r |
  b*1 r r r |
  e*2 r r r |

Pattern %hitS_I5_08_60:
  key=Eb 4: 60@
  e*2 r r r |
  d*2 r r r |
  c*2 r r r |
  a*1 r r r |
  e*2 r r r |
  f*1 r r r |
  b*1 r r r |
  e*2 r r r |

Pattern %hit_I6_08_90:
  key=Eb 4: 90@
  e*2 r e*2 r |
  a*1 r a*1 r |
  f*1 r f*1 r |
  b*1 r b*1 r |
  e*2 r e*2 r |
  a*1 r a*1 r |
  b*1 r b*1 r |
  e*2 r e*2 r |

Pattern %hit_I7_08_96:
  key=Cm 4: 96@
  f*1 r f*1 r |
  c*2 r c*2 r |
  g*1 r g*1 r |
  d*2 r d*2 r |
  b*1 r b*1 r |
  f*1 r f*1 r |
  c*2 r c*2 r |
  g*1 r g*1 r |

Pattern %hitS_I8_08_63:
  key=Cm 4: 63@
  e*2 r r r |
  d*2 r r r |
  db*2 r r r |
  c*2 r r r |
  b*1 r r r |
  an*1 r r r |
  a*1 r r r |
  g*1 r r r |

Pattern %roll_I9_08_85:
  key=Cm 16: 85@
  a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 |
  f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 f*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |

Pattern %hit_I10_08_108:
  key=Cm 4: 108@
  c*2 r c*2 r |
  c*2 r c*2 r |
  f*1 r f*1 r |
  g*1 r g*1 r |
  c*2 r c*2 r |
  a*1 r a*1 r |
  g*1 r g*1 r |
  c*2 r c*2 r |

Pattern %hitS_I11_08_63:
  key=Cm 4: 63@
  c*2 r r r |
  g*1 r r r |
  f*1 r r r |
  c*2 r r r |
  c*2 r r r |
  g*1 r r r |
  f*1 r r r |
  g*1 r r r |

Pattern %hitS_I12_08_57:
  key=C 4: 57@
  c*2 r r r |
  b*1 r r r |
  a*1 r r r |
  f*1 r r r |
  c*2 r r r |
  d*2 r r r |
  g*1 r r r |
  c*2 r r r |

Pattern %hitS_I13_08_63:
  key=C 4: 63@
  c*2 r r r |
  b*1 r r r |
  a*1 r r r |
  f*1 r r r |
  c*2 r r r |
  d*2 r r r |
  g*1 r r r |
  c*2 r r r |

Pattern %hit_I14_08_110:
  key=C 4: 110@
  c*2 r c*2 r |
  f*1 r f*1 r |
  g*1 r g*1 r |
  c*2 r c*2 r |
  a*1 r a*1 r |
  f*1 r f*1 r |
  g*1 r g*1 r |
  c*2 r c*2 r |

Pattern %hitS_II3_08_40:
  key=Fm 4: 40@
  f*1 r r r |
  c*2 r r r |
  f*1 r r r |
  d*2 r r r |
  b*1 r r r |
  c*2 r r r |
  f*1 r r r |
  c*2 r r r |

Pattern %hit_III1_08_85:
  key=Cm 4: 85@
  c*2 r c*2 r |
  c*2 r c*2 r |
  g*1 r g*1 r |
  c*2 r c*2 r |
  f*1 r f*1 r |
  c*2 r c*2 r |
  g*1 r g*1 r |
  c*2 r c*2 r |

Pattern %hit_III2_08_88:
  key=Gm 4: 88@
  g*1 r g*1 r |
  g*1 r g*1 r |
  d*2 r d*2 r |
  g*1 r g*1 r |
  c*2 r c*2 r |
  g*1 r g*1 r |
  d*2 r d*2 r |
  g*1 r g*1 r |

Pattern %hit_III5_08_90:
  key=Cm 4: 90@
  c*2 r c*2 r |
  c*2 r c*2 r |
  g*1 r g*1 r |
  c*2 r c*2 r |
  f*1 r f*1 r |
  c*2 r c*2 r |
  g*1 r g*1 r |
  c*2 r c*2 r |

Pattern %hit_III6_08_92:
  key=Gm 4: 92@
  g*1 r g*1 r |
  g*1 r g*1 r |
  d*2 r d*2 r |
  g*1 r g*1 r |
  c*2 r c*2 r |
  g*1 r g*1 r |
  d*2 r d*2 r |
  g*1 r g*1 r |

Pattern %hit_IV1_08_108:
  key=C 4: 108@
  c*2 r c*2 r |
  c*2 r c*2 r |
  g*1 r g*1 r |
  g*1 r g*1 r |
  a*1 r a*1 r |
  f*1 r f*1 r |
  g*1 r g*1 r |
  g*1 r g*1 r |

Pattern %hit_IV2_08_98:
  key=C 4: 98@
  c*2 r c*2 r |
  b*1 r b*1 r |
  a*1 r a*1 r |
  e*1 r e*1 r |
  f*1 r f*1 r |
  e*1 r e*1 r |
  d*2 r d*2 r |
  g*1 r g*1 r |

Pattern %hit_IV3_08_102:
  key=G 4: 102@
  g*1 r g*1 r |
  f*1 r f*1 r |
  e*1 r e*1 r |
  b*1 r b*1 r |
  c*2 r c*2 r |
  b*1 r b*1 r |
  a*1 r a*1 r |
  d*2 r d*2 r |

Pattern %hit_IV4_08_104:
  key=C 4: 104@
  c*2 r c*2 r |
  b*1 r b*1 r |
  a*1 r a*1 r |
  e*1 r e*1 r |
  f*1 r f*1 r |
  e*1 r e*1 r |
  d*2 r d*2 r |
  g*1 r g*1 r |

Pattern %roll_IV5_016_55:
  key=C 16: 55@
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

Pattern %hitS_IV7_016_55:
  key=C 4: 55@
  c*2 r r r |
  b*1 r r r |
  a*1 r r r |
  g*1 r r r |
  f*1 r r r |
  e*1 r r r |
  d*2 r r r |
  g*1 r r r |
  a*1 r r r |
  e*1 r r r |
  f*1 r r r |
  c*2 r r r |
  d*2 r r r |
  g*1 r r r |
  c*2 r r r |
  g*1 r r r |

Pattern %hit_IV9_08_110:
  key=C 4: 110@
  c*2 r c*2 r |
  c*2 r c*2 r |
  f*1 r f*1 r |
  f*1 r f*1 r |
  g*1 r g*1 r |
  g*1 r g*1 r |
  c*2 r c*2 r |
  g*1 r g*1 r |

Pattern %hit_IV10_04_108:
  key=C 4: 108@
  c*2 r c*2 r |
  f*1 r f*1 r |
  g*1 r g*1 r |
  c*2 r c*2 r |

Pattern %hit_IV10_47:
  key=C 4:
  d*2 r d*2 r |
  g*1 r g*1 r |
  c*2 r c*2 r |

// ================================================================ tracce

Violini1:
  $"Largo" %arp_I0_08_40 $"Allegro con fuoco" %IAM_Cm_0_0_95
  %IAM2_Cm_0_0_100 %IPONTE_Cm_seq_0_90 %arp_I4_08_45 %IBM2_Eb_0_0_88
  %ICOD_Eb_0_0_90 %IDEV1_Cm_seq_0_95 %IDEV2_Cm_seq_0_92 %IDEV3_Cm_0_0_100
  %IAM_Cm_0_0_108 %IPONTE2_Cm_seq_0_92 %arp_I12_08_45 %IBM2C_C_m3_0_90
  %ICODA_C_0_0_105 $"Andante" %arp_II1_08_40 %IIA2_Ab_0_0_72
  %arp_II3_08_42 %IIA2_Ab_0_0_75 %IICOD_Ab_0_0_70 $"Scherzo: Presto"
  %IIIS_Cm_0_0_88 %IIIS2_Gm_7_0_90 $"Trio" %arp_III3_08_42
  %IIITR2_G_7_0_72 $"Da capo" %IIIS_Cm_0_0_92 %IIIS2_Gm_7_0_94
  $"Finale: Allegro maestoso" %IVFAN_C_0_0_105 %IVT_C_0_0_98 %IVTG_G_7_0_102
  %IVT_C_0_0_104 6%R1 %IVSUBJ_C_7_0_90 %chords_IV5_816_60
  %IVCHA_C_0_0_80 %IVCHB_C_0_0_80 $"Stretta" %IVSTR_C_0_0_108
  %IVCOD_C_0_0_108

Violini2:
  %chords_I0_08_40 %arp_I1_08_75 %arp_I2_08_82 %arp_I3_08_60
  %arp_I4_08_55 %arp_I5_08_60 %arp_I6_08_70 vol=60 >>
  %arp_I7_08_76 %arp_I8_08_63 %arp_I9_08_82 vol=100
  %arp_I10_08_88 %arp_I11_08_63 %arp_I12_08_57 %arp_I13_08_63
  %arp_I14_08_90 %chords_II1_08_35 %chords_II2_08_40 %arp_II3_08_43
  %chords_II4_08_42 %chords_II5_08_38 %arp_III1_08_60 %arp_III2_08_63
  %chords_III3_08_45 %chords_III4_08_49 %arp_III5_08_65 %arp_III6_08_67
  %arp_IV1_08_88 %arp_IV2_08_78 %arp_IV3_08_82 %arp_IV4_08_84
  4%R1 %IVSUBJ_C_0_0_86 %arp_IV5_616_60 %chords_IV7_016_60
  %arp_IV9_08_90 %arp_IV10_08_92

Viole:
  %chords_I0_08_40 %chords_I1_08_80 %chords_I2_08_87 %chords_I3_08_60
  %chords_I4_08_55 %chords_I5_08_60 %chords_I6_08_75 vol=60 >>
  %chords_I7_08_81 %chords_I8_08_63 %chords_I9_08_87 vol=100
  %chords_I10_08_93 %chords_I11_08_63 %chords_I12_08_57 %chords_I13_08_63
  %chords_I14_08_95 %chords_II1_08_35 %chords_II2_08_40 %chords_II3_08_43
  %chords_II4_08_42 %chords_II5_08_38 %stab_III1_08_70 %stab_III2_08_73
  %chords_III3_08_45 %chords_III4_08_49 %stab_III5_08_75 %stab_III6_08_77
  %chords_IV1_08_93 %chords_IV2_08_83 %chords_IV3_08_87 %chords_IV4_08_89
  2%R1 %IVSUBJ_C_7_m1_82 %chords_IV5_416_60 %chords_IV7_016_62
  %chords_IV9_08_95 %chords_IV10_08_97

Violoncelli:
  %rootsW_I0_08_50 %rootsC_I1_08_87 %rootsC_I2_08_94 %rootsC_I3_08_70
  %rootsC_I4_08_65 %rootsC_I5_08_70 %rootsC_I6_08_82 %rootsC_I7_08_88
  %rootsC_I8_08_73 %rootsC_I9_08_94 %rootsC_I10_08_100 %rootsC_I11_08_73
  %rootsC_I12_08_67 %rootsC_I13_08_73 %rootsC_I14_08_102 %rootsW_II1_08_45
  %rootsW_II2_08_50 %rootsC_II3_08_53 %IIA_Ab_0_m2_78 %rootsW_II5_08_48
  %rootsC_III1_08_80 %rootsC_III2_08_83 %rootsW_III3_08_55 %rootsW_III4_08_59
  %rootsC_III5_08_85 %rootsC_III6_08_87 %rootsC_IV1_08_100 %rootsC_IV2_08_90
  %rootsC_IV3_08_94 %IVT_C_0_m2_96 %IVSUBJ_C_0_m2_78 %rootsC_IV5_216_60
  %rootsW_IV7_016_66 %rootsC_IV9_08_102 %rootsC_IV10_08_104

Contrabbassi:
  %rootsB_I0_08_48 %rootsB_I1_08_89 %rootsB_I2_08_96 %rootsB_I3_08_73
  %rootsB_I4_08_68 %rootsB_I5_08_73 %rootsB_I6_08_84 %rootsB_I7_08_90
  %rootsB_I8_08_76 %rootsB_I9_08_96 %rootsB_I10_08_102 %rootsB_I11_08_76
  %rootsB_I12_08_70 %rootsB_I13_08_76 %rootsB_I14_08_104 %rootsB_II1_08_43
  %rootsB_II2_08_48 %rootsB_II3_08_56 %rootsB_II4_08_50 %rootsB_II5_08_46
  %rootsB_III1_08_80 %rootsB_III2_08_83 %rootsB_III3_08_55 %rootsB_III4_08_59
  %rootsB_III5_08_85 %rootsB_III6_08_87 %rootsB_IV1_08_102 %rootsB_IV2_08_92
  %rootsB_IV3_08_96 %rootsB_IV4_08_98 %rootsB_IV5_016_75 %rootsB_IV7_016_66
  %rootsB_IV9_08_104 %rootsB_IV10_08_106

Flauto:
  8%R1 %IAM_Cm_0_0_90 %IAM2_Cm_0_0_95 %IPONTE_Cm_seq_0_90
  8%R1 %IBM2_Eb_0_0_80 %ICOD_Eb_0_0_85 8%R1
  %IDEV2_Cm_seq_0_80 %IDEV3_Cm_0_0_100 %IAM_Cm_0_0_100 %IPONTE2_Cm_seq_0_92
  8%R1 %IBM2C_C_m3_0_85 %ICODA_C_0_0_100 16%R1
  %IIB_Fm_0_0_65 8%R1 %IICOD_Ab_0_0_62 %IIIS_Cm_0_0_82
  %IIIS2_Gm_7_0_85 8%R1 %IIITR2_G_7_0_75 %IIIS_Cm_0_0_86
  %IIIS2_Gm_7_0_88 %IVFAN_C_0_0_95 %IVT_C_0_0_92 %IVTG_G_7_0_96
  %IVT_C_0_0_96 10%R1 %IVSUBJ_C_7_0_98 4%R1
  %IVCHA_C_0_0_72 %IVCHB_C_0_0_72 %IVSTR_C_0_0_100 %IVCOD_C_0_0_100

Oboe:
  %I0M_Cm_0_0_70 %IAM_Cm_0_m1_90 %IAM2_Cm_0_m1_95 8%R1
  %IBM_Eb_0_m1_80 %IBM_Eb_0_m1_80 %ICOD_Eb_0_m1_85 %IDEV1_Cm_seq_m1_90
  16%R1 %IAM_Cm_0_m1_100 8%R1 %IBMC_C_m3_m1_82
  %IBMC_C_m3_m1_82 %ICODA_C_0_m1_100 %IIA_Ab_0_0_75 8%R1
  %IIB_Fm_0_0_72 8%R1 %IICOD_Ab_0_0_72 8%R1
  %IIIS2_Gm_7_m1_80 %IIITR_C_0_0_78 %IIITR2_G_7_m1_70 8%R1
  %IIIS2_Gm_7_m1_84 8%R1 %IVT_C_0_m1_92 24%R1
  %IVSUBJ_C_0_0_94 6%R1 %IVCHA_C_0_m1_70 %IVCHB_C_0_m1_70
  %IVSTR_C_0_m1_100 %IVCOD_C_0_m1_100

Clarinetto:
  %I0M_Cm_0_m1_55 16%R1 %IPONTE_Cm_seq_m1_80 %IBM_Eb_0_m1_75
  24%R1 %IDEV2_Cm_seq_m1_80 24%R1 %IBMC_C_m3_m1_75
  24%R1 %IIA_Ab_0_m1_70 %IIB_Fm_0_m1_65 32%R1
  %IIITR_C_0_m1_70 104%R1

Fagotto:
  %rootsF_I0_08_50 %rootsF_I1_08_85 %rootsF_I2_08_92 %rootsF_I3_08_75
  %rootsF_I4_08_70 %rootsF_I5_08_75 %rootsF_I6_08_80 %rootsF_I7_08_86
  %rootsF_I8_08_78 %rootsF_I9_08_92 %rootsF_I10_08_98 %rootsF_I11_08_78
  %rootsF_I12_08_72 %rootsF_I13_08_78 %rootsF_I14_08_100 %rootsF_II1_08_45
  %rootsF_II2_08_50 %rootsF_II3_08_58 %rootsF_II4_08_52 %rootsF_II5_08_48
  %rootsF_III1_08_75 %rootsF_III2_08_78 %rootsF_III3_08_55 %rootsF_III4_08_59
  %rootsF_III5_08_80 %rootsF_III6_08_82 %rootsF_IV1_08_98 %rootsF_IV2_08_88
  %rootsF_IV3_08_92 %rootsF_IV4_08_94 %rootsF_IV5_016_70 %rootsF_IV7_016_70
  %rootsF_IV9_08_100 %rootsF_IV10_08_102

Corni:
  8%R1 %chords_I1_08_95 %chords_I2_08_102 %chords_I3_08_60
  %chords_I4_08_55 %chords_I5_08_60 %chords_I6_08_90 %chords_I7_08_96
  %chords_I8_08_63 %chords_I9_08_102 %chords_I10_08_108 %chords_I11_08_63
  %chords_I12_08_57 %chords_I13_08_63 %chords_I14_08_110 %chords_II1_08_45
  %chords_II2_08_48 %chords_II3_08_43 %chords_II4_08_50 %chords_II5_08_50
  %stab_III1_08_70 %stab_III2_08_73 %chords_III3_08_40 %chords_III4_08_44
  %stab_III5_08_75 %stab_III6_08_77 %chords_IV1_08_108 %chords_IV2_08_98
  %chords_IV3_08_102 %chords_IV4_08_104 12%R1 %IVSUBJ_C_0_m1_102
  %chords_IV5_1416_60 %chords_IV7_016_85 %chords_IV9_08_110 %chords_IV10_08_112

Trumpet:
  16%R1 %IAM2_Cm_0_m1_95 48%R1 %IDEV3_Cm_0_m1_95
  %IAM_Cm_0_m1_105 24%R1 %ICODA_C_0_m1_100 72%R1
  %IIIS_Cm_0_m1_80 %IIIS2_Gm_7_m2_80 %IVFAN_C_0_m1_105 8%R1
  %IVTG_G_7_m1_96 %IVT_C_0_m1_98 14%R1 %IVSUBJ_C_7_m1_106
  %IVCHA_C_0_m1_90 %IVCHB_C_0_m1_90 8%R1 %IVCOD_C_0_m1_100

Timpani:
  %hitS_I0_08_35 tempo=138
  %hit_I1_08_95 %hit_I2_08_102 %hitS_I3_08_60 %hitS_I4_08_55
  %hitS_I5_08_60 %hit_I6_08_90 %hit_I7_08_96 %hitS_I8_08_63
  %roll_I9_08_85 %hit_I10_08_108 %hitS_I11_08_63 %hitS_I12_08_57
  %hitS_I13_08_63 %hit_I14_08_110 tempo=66
  16%R1 %hitS_II3_08_40 16%R1 tempo=160
  %hit_III1_08_85 %hit_III2_08_88 tempo=132
  16%R1 tempo=160
  %hit_III5_08_90 %hit_III6_08_92 tempo=126
  %hit_IV1_08_108 %hit_IV2_08_98 %hit_IV3_08_102 %hit_IV4_08_104
  %roll_IV5_016_55 %hitS_IV7_016_55 tempo=150
  %hit_IV9_08_110 %hit_IV10_04_108 100@ tempo=150 <<
  %hit_IV10_47 key=C 4: c*2$fermata r r r | tempo=54

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
