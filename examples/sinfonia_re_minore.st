// Sinfonia n. 1 in Re minore, "Dal buio alla luce": una sinfonia di esempio in quattro tempi.
//
// Musica originale, scritta per mostrare ST-language con un'orchestra intera:
// legni (flauto, oboe, clarinetto, fagotto), corni e tromba, timpani e gli
// archi (violini primi e secondi, viole, violoncelli, contrabbassi).
//
//   I    Allegro con fuoco   Re minore  (32 battute)  esposizione di due temi
//                                         (il secondo in Fa maggiore), sviluppo
//                                         sulla dominante, ripresa e finale in Re maggiore
//   II   Adagio              Si bemolle (16 battute)  il canto dell'oboe, poi dei violini
//   III  Scherzo: Presto     Re minore  (16 battute)  tema staccato, passato dai flauti ai violini
//   IV   Finale: Allegro con brio  Re maggiore (32 battute)  fanfara, fugato (violoncelli,
//                                         viole, violini secondi, violini primi), corale,
//                                         coda con il rallentando e la corona
//
// Cosa c'e' dentro:
//   - le tonalita' che cambiano da un tempo all'altro (key=Dm, F, Bb, D): ogni
//     pattern dice la sua, e le alterazioni non si scrivono;
//   - i cambi di tempo tra un movimento e l'altro (tempo=) sulla traccia dei
//     timpani, e il rallentando finale (tempo=126 << ... tempo=56);
//   - il fugato: lo stesso soggetto che entra a battute sfalsate, nello
//     strumento e nell'ottava giusti;
//   - le dinamiche: crescendo di volume nello sviluppo (vol=60 >> ... vol=100),
//     forcelle, indicazioni di testo ($"Adagio") e la corona ($fermata);
//   - strumenti definiti nel file con il programma General MIDI (flauto,
//     oboe, clarinetto, fagotto, corno, timpani, archi);
//   - i pattern generati per sezione: accordi tenuti, arpeggi, bassi, rulli di
//     timpano, accordi staccati.
// Il pannello Mixer ha un blocco per ogni sezione dell'orchestra.

ST: 2.6
Tempo: 132 BPM
Metrica: 4/4
Tonalita: Dm

Strumento Flauto:
  program=73 percussione=no ottava=5 range=72-100 poly=no voicing=monophonic

Strumento Oboe:
  program=68 percussione=no ottava=5 range=58-93 poly=no voicing=monophonic

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

Pattern %I_ThA:
  key=Dm 8: 100@
  2d*5 f*5 a*5 2d*6 2c*6 |
  b*5 a*5 g*5 f*5 2e*5 2d*5 |
  2e*5 g*5 a*5 2c#*6 2a*5 |
  4d*6 3a*5 r |
  2b*5 d*6 f*6 2b*6 2a*6 |
  g*6 f*6 e*6 d*6 2c*6 b*5 a*5 |
  2g*5 a*5 c#*6 2e*6 2a*5 |
  6d*6 2r |

Pattern %I_ThA_giu:
  key=Dm 8: 100@
  2d*4 f*4 a*4 2d*5 2c*5 |
  b*4 a*4 g*4 f*4 2e*4 2d*4 |
  2e*4 g*4 a*4 2c#*5 2a*4 |
  4d*5 3a*4 r |
  2b*4 d*5 f*5 2b*5 2a*5 |
  g*5 f*5 e*5 d*5 2c*5 b*4 a*4 |
  2g*4 a*4 c#*5 2e*5 2a*4 |
  6d*5 2r |

Pattern %I_ThAr:
  key=Dm 8: 100@
  2d*5 f*5 a*5 2d*6 2c*6 |
  b*5 a*5 g*5 f*5 2e*5 2d*5 |
  2e*5 g*5 a*5 2c#*6 2a*5 |
  4d*6 3a*5 r |
  2b*5 d*6 f*6 2b*6 2a*6 |
  g*6 f*6 e*6 d*6 2c*6 b*5 a*5 |
  2g*5 a*5 c#*6 2e*6 2a*5 |
  8d*6$fermata |

Pattern %I_ThAr_giu:
  key=Dm 8: 100@
  2d*4 f*4 a*4 2d*5 2c*5 |
  b*4 a*4 g*4 f*4 2e*4 2d*4 |
  2e*4 g*4 a*4 2c#*5 2a*4 |
  4d*5 3a*4 r |
  2b*4 d*5 f*5 2b*5 2a*5 |
  g*5 f*5 e*5 d*5 2c*5 b*4 a*4 |
  2g*4 a*4 c#*5 2e*5 2a*4 |
  8d*5$fermata |

Pattern %I_ThB1_giu:
  key=F 8: 80@
  2a*4 c*5 f*5 2e*5 2d*5 |
  2c*5 e*5 g*5 2e*5 2c*5 |
  2d*5 f*5 a*5 2g*5 2f*5 |
  2b*4 d*5 f*5 4d*5 |

Pattern %I_ThB2_giu:
  key=F 8: 80@
  2a*4 c*5 f*5 2e*5 2c*5 |
  2b*4 d*5 g*5 2f*5 2d*5 |
  2c*5 e*5 g*5 2b*5 2g*5 |
  6f*5 2r |

Pattern %I_ThB2:
  key=F 8: 75@
  2a*5 c*6 f*6 2e*6 2c*6 |
  2b*5 d*6 g*6 2f*6 2d*6 |
  2c*6 e*6 g*6 2b*6 2g*6 |
  6f*6 2r |

Pattern %I_Dev:
  key=Dm 8: 95@
  2g*5 b*5 d*6 2g*6 2f*6 |
  2g*5 b*5 d*6 2f*6 2e*6 |
  2a*5 c#*6 e*6 2a*6 2g*6 |
  g*6 f*6 e*6 d*6 2c#*6 2a*5 |
  2b*5 d*6 f*6 2b*6 2a*6 |
  g*6 f*6 e*6 d*6 2c*6 b*5 a*5 |
  2a*5 d*6 e*6 2a*6 2d*7 |
  6c#*6 2r |

Pattern %rootsF_IA_08_90:
  key=Dm 4: 90@
  d*2'1 |
  g*2'1 |
  a*2'1 |
  d*2'1 |
  b*2'1 |
  g*2'1 |
  a*2'1 |
  d*2'1 |

Pattern %rootsF_IB_08_55:
  key=F 4: 55@
  f*2'1 |
  c*2'1 |
  d*2'1 |
  b*2'1 |
  f*2'1 |
  g*2'1 |
  c*2'1 |
  f*2'1 |

Pattern %rootsF_ID_08_70:
  key=Dm 4: 70@
  g*2'1 |
  e*2'1 |
  a*2'1 |
  a*2'1 |
  b*2'1 |
  g*2'1 |
  a*2'1 |
  a*2'1 |

Pattern %rootsF_IR_08_95:
  key=Dm 4: 95@
  d*2'1 |
  g*2'1 |
  a*2'1 |
  d*2'1 |
  b*2'1 |
  g*2'1 |
  a*2'1 |
  d*2'1 |

Pattern %chords_IA_08_100:
  key=Dm 4: 100@
  Dm'1 |
  Gm'1 |
  A7'1 |
  Dm'1 |
  Bb'1 |
  Gm'1 |
  A7'1 |
  Dm'1 |

Pattern %chords_IB_08_55:
  key=F 4: 55@
  F'1 |
  C'1 |
  Dm'1 |
  Bb'1 |
  F'1 |
  Gm'1 |
  C7'1 |
  F'1 |

Pattern %chords_ID_08_80:
  key=Dm 4: 80@
  Gm'1 |
  Em7b5'1 |
  A7'1 |
  A7'1 |
  Bb'1 |
  Gm'1 |
  Asus4'1 |
  A7'1 |

Pattern %chords_IR_08_105:
  key=Dm 4: 105@
  Dm'1 |
  Gm'1 |
  A7'1 |
  Dm'1 |
  Bb'1 |
  Gm'1 |
  A7'1 |
  D'1 |

Pattern %hit_IA_08_100:
  key=Dm 4: 100@
  d*2 r d*2 r |
  g*1 r g*1 r |
  a*1 r a*1 r |
  d*2 r d*2 r |
  b*1 r b*1 r |
  g*1 r g*1 r |
  a*1 r a*1 r |
  d*2 r d*2 r |

Pattern %hitS_IB_08_45:
  key=F 4: 45@
  f*1 r r r |
  c*2 r r r |
  d*2 r r r |
  b*1 r r r |
  f*1 r r r |
  g*1 r r r |
  c*2 r r r |
  f*1 r r r |

Pattern %roll_ID_08_70:
  key=Dm 16: 70@
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  e*1 e*1 e*1 e*1 e*1 e*1 e*1 e*1 e*1 e*1 e*1 e*1 e*1 e*1 e*1 e*1 |
  a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 |
  a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 |
  b*1 b*1 b*1 b*1 b*1 b*1 b*1 b*1 b*1 b*1 b*1 b*1 b*1 b*1 b*1 b*1 |
  g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 g*1 |
  a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 |
  a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 |

Pattern %hit_IR_08_105:
  key=Dm 4: 105@
  d*2 r d*2 r |
  g*1 r g*1 r |
  a*1 r a*1 r |
  d*2 r d*2 r |
  b*1 r b*1 r |
  g*1 r g*1 r |
  a*1 r a*1 r |
  d*2 r d*2 r |

Pattern %arp_IA_08_70:
  key=Dm 8: 70@
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  a*4 c#*5 e*5 g*5 e*5 c#*5 e*5 c#*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  a*4 c#*5 e*5 g*5 e*5 c#*5 e*5 c#*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |

Pattern %arp_IB_08_55:
  key=F 8: 55@
  c*5 f*5 a*5 f*5 c*5 f*5 a*5 f*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |
  c*5 f*5 a*5 f*5 c*5 f*5 a*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  c*5 e*5 g*5 b*5 g*5 e*5 g*5 e*5 |
  c*5 f*5 a*5 f*5 c*5 f*5 a*5 f*5 |

Pattern %arp_ID_08_80:
  key=Dm 8: 80@
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  e*5 g*5 b*5 d*6 b*5 g*5 b*5 g*5 |
  a*4 c#*5 e*5 g*5 e*5 c#*5 e*5 c#*5 |
  a*4 c#*5 e*5 g*5 e*5 c#*5 e*5 c#*5 |
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  a*4 d*5 e*5 d*5 a*4 d*5 e*5 d*5 |
  a*4 c#*5 e*5 g*5 e*5 c#*5 e*5 c#*5 |

Pattern %arp_IR_08_85:
  key=Dm 8: 85@
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  a*4 c#*5 e*5 g*5 e*5 c#*5 e*5 c#*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  a*4 c#*5 e*5 g*5 e*5 c#*5 e*5 c#*5 |
  d*5 f#*5 a*5 f#*5 d*5 f#*5 a*5 f#*5 |

Pattern %chords_IA_08_78:
  key=Dm 4: 78@
  Dm'1 |
  Gm'1 |
  A7'1 |
  Dm'1 |
  Bb'1 |
  Gm'1 |
  A7'1 |
  Dm'1 |

Pattern %chords_IB_08_50:
  key=F 4: 50@
  F'1 |
  C'1 |
  Dm'1 |
  Bb'1 |
  F'1 |
  Gm'1 |
  C7'1 |
  F'1 |

Pattern %chords_ID_08_75:
  key=Dm 4: 75@
  Gm'1 |
  Em7b5'1 |
  A7'1 |
  A7'1 |
  Bb'1 |
  Gm'1 |
  Asus4'1 |
  A7'1 |

Pattern %chords_IR_08_85:
  key=Dm 4: 85@
  Dm'1 |
  Gm'1 |
  A7'1 |
  Dm'1 |
  Bb'1 |
  Gm'1 |
  A7'1 |
  D'1 |

Pattern %rootsC_IA_08_90:
  key=Dm 4: 90@
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |
  b*2 b*3 b*2 b*3 |
  g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |

Pattern %rootsC_IB_08_60:
  key=F 4: 60@
  f*2 f*3 f*2 f*3 |
  c*2 c*3 c*2 c*3 |
  d*2 d*3 d*2 d*3 |
  b*2 b*3 b*2 b*3 |
  f*2 f*3 f*2 f*3 |
  g*2 g*3 g*2 g*3 |
  c*2 c*3 c*2 c*3 |
  f*2 f*3 f*2 f*3 |

Pattern %rootsC_ID_08_85:
  key=Dm 4: 85@
  g*2 g*3 g*2 g*3 |
  e*2 e*3 e*2 e*3 |
  a*2 a*3 a*2 a*3 |
  a*2 a*3 a*2 a*3 |
  b*2 b*3 b*2 b*3 |
  g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 |
  a*2 a*3 a*2 a*3 |

Pattern %rootsC_IR_08_95:
  key=Dm 4: 95@
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |
  b*2 b*3 b*2 b*3 |
  g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |

Pattern %rootsB_IA_08_92:
  key=Dm 4: 92@
  d*2'1 |
  g*1'1 |
  a*1'1 |
  d*2'1 |
  b*1'1 |
  g*1'1 |
  a*1'1 |
  d*2'1 |

Pattern %rootsB_IB_08_60:
  key=F 4: 60@
  f*1'1 |
  c*2'1 |
  d*2'1 |
  b*1'1 |
  f*1'1 |
  g*1'1 |
  c*2'1 |
  f*1'1 |

Pattern %rootsB_ID_08_85:
  key=Dm 4: 85@
  g*1'1 |
  e*1'1 |
  a*1'1 |
  a*1'1 |
  b*1'1 |
  g*1'1 |
  a*1'1 |
  a*1'1 |

Pattern %rootsB_IR_08_98:
  key=Dm 4: 98@
  d*2'1 |
  g*1'1 |
  a*1'1 |
  d*2'1 |
  b*1'1 |
  g*1'1 |
  a*1'1 |
  d*2'1 |

Pattern %II_Oboe:
  key=Bb 8: 80@
  4f*5 2d*5 2c*5 |
  2b*4 d*5 g*5 4f*5 |
  4e*5 2g*5 2b*5 |
  4a*5 2c*6 2e*6 |
  4d*6 2b*5 2f*5 |
  2g*5 b*5 d*6 4c*6 |
  2e*6 2d*6 2c*6 2a*5 |
  6b*5 2r |

Pattern %II_Violino:
  key=Bb 8: 78@
  4g*5 2e*5 2g*5 |
  4f*5 2d*5 2f*5 |
  4e*5 2g*5 2c*6 |
  2a*5 2c*6 4e*6 |
  4d*6 2f*6 2a*5 |
  4b*5 2g*5 2d*5 |
  2c*6 2e*6 2d*6 2c*6 |
  8b*5$fermata |

Pattern %II_Violino_giu:
  key=Bb 8: 70@
  4g*4 2e*4 2g*4 |
  4f*4 2d*4 2f*4 |
  4e*4 2g*4 2c*5 |
  2a*4 2c*5 4e*5 |
  4d*5 2f*5 2a*4 |
  4b*4 2g*4 2d*4 |
  2c*5 2e*5 2d*5 2c*5 |
  8b*4$fermata |

Pattern %rootsF_II1_08_55:
  key=Bb 4: 55@
  b*2'1 |
  g*2'1 |
  e*2'1 |
  f*2'1 |
  b*2'1 |
  g*2'1 |
  c*2'2 f*2'2 |
  b*2'1 |

Pattern %rootsF_II2_08_58:
  key=Bb 4: 58@
  e*2'1 |
  d*2'1 |
  c*2'1 |
  f*2'1 |
  d*2'1 |
  g*2'1 |
  c*2'2 f*2'2 |
  b*2'1 |

Pattern %chords_II1_08_50:
  key=Bb 4: 50@
  Bb'1 |
  Gm'1 |
  Eb'1 |
  F7'1 |
  Bb'1 |
  Gm'1 |
  Cm7'2 F7'2 |
  Bb'1 |

Pattern %chords_II2_08_55:
  key=Bb 4: 55@
  Eb'1 |
  Bb/D'1 |
  Cm'1 |
  F7'1 |
  Dm'1 |
  Gm'1 |
  Cm7'2 F7'2 |
  Bb'1 |

Pattern %arp_II1_08_48:
  key=Bb 8: 48@
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  a*4 c*5 e*5 f*5 e*5 c*5 e*5 c*5 |
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  c*5 e*5 g*5 b*5 a*4 c*5 e*5 f*5 |
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |

Pattern %chords_II1_08_45:
  key=Bb 4: 45@
  Bb'1 |
  Gm'1 |
  Eb'1 |
  F7'1 |
  Bb'1 |
  Gm'1 |
  Cm7'2 F7'2 |
  Bb'1 |

Pattern %arp_II2_08_50:
  key=Bb 8: 50@
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |
  c*5 e*5 g*5 e*5 c*5 e*5 g*5 e*5 |
  a*4 c*5 e*5 f*5 e*5 c*5 e*5 c*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  c*5 e*5 g*5 b*5 a*4 c*5 e*5 f*5 |
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |

Pattern %rootsW_II1_08_70:
  key=Bb 4: 70@
  b*2'1 |
  g*2'1 |
  e*2'1 |
  f*2'1 |
  b*2'1 |
  g*2'1 |
  c*2'2 f*2'2 |
  b*2'1 |

Pattern %rootsW_II2_08_72:
  key=Bb 4: 72@
  e*2'1 |
  d*2'1 |
  c*2'1 |
  f*2'1 |
  d*2'1 |
  g*2'1 |
  c*2'2 f*2'2 |
  b*2'1 |

Pattern %rootsB_II1_08_60:
  key=Bb 4: 60@
  b*1'1 |
  g*1'1 |
  e*1'1 |
  f*1'1 |
  b*1'1 |
  g*1'1 |
  c*2'2 f*1'2 |
  b*1'1 |

Pattern %rootsB_II2_08_62:
  key=Bb 4: 62@
  e*1'1 |
  d*2'1 |
  c*2'1 |
  f*1'1 |
  d*2'1 |
  g*1'1 |
  c*2'2 f*1'2 |
  b*1'1 |

Pattern %III_S1:
  key=Dm 8: 95@
  d*5 f*5 a*5 f*5 d*5 f*5 2a*5 |
  d*6 c*6 b*5 a*5 2g*5 2f*5 |
  e*5 g*5 a*5 g*5 e*5 g*5 2c#*6 |
  2d*6 2a*5 2f*5 2d*5 |
  g*5 b*5 d*6 b*5 g*5 b*5 2d*6 |
  f*5 a*5 d*6 a*5 f*5 a*5 2d*6 |
  e*5 g*5 c#*6 e*6 2a*6 2g*6 |
  4d*6 4r |

Pattern %III_S2:
  key=Dm 8: 100@
  b*5 d*6 f*6 d*6 b*5 d*6 2f*6 |
  g*5 b*5 d*6 b*5 g*5 b*5 2d*6 |
  f*6 d*6 b*5 d*6 f*6 d*6 2b*5 |
  e*6 g*6 e*6 c#*6 2a*5 2e*5 |
  d*6 f*6 a*6 f*6 d*6 f*6 2a*6 |
  g*6 b*6 d*7 b*6 g*6 b*6 2d*7 |
  a*6 g*6 e*6 c#*6 a*5 g*5 2e*5 |
  4d*5 4r |

Pattern %stab_III2_08_75:
  key=Dm 4: 75@
  r Bb! r Bb! |
  r Gm! r Gm! |
  r Bb! r Bb! |
  r A7! r A7! |
  r Dm! r Dm! |
  r Gm! r Gm! |
  r A7! r A7! |
  r Dm! r Dm! |

Pattern %rootsF_III1_08_75:
  key=Dm 4: 75@
  d*2'1 |
  d*2'1 |
  a*2'1 |
  d*2'1 |
  g*2'1 |
  d*2'1 |
  a*2'1 |
  d*2'1 |

Pattern %rootsF_III2_08_80:
  key=Dm 4: 80@
  b*2'1 |
  g*2'1 |
  b*2'1 |
  a*2'1 |
  d*2'1 |
  g*2'1 |
  a*2'1 |
  d*2'1 |

Pattern %stab_III1_08_70:
  key=Dm 4: 70@
  r Dm! r Dm! |
  r Dm! r Dm! |
  r A7! r A7! |
  r Dm! r Dm! |
  r Gm! r Gm! |
  r Dm! r Dm! |
  r A7! r A7! |
  r Dm! r Dm! |

Pattern %stab_III2_08_90:
  key=Dm 4: 90@
  r Bb! r Bb! |
  r Gm! r Gm! |
  r Bb! r Bb! |
  r A7! r A7! |
  r Dm! r Dm! |
  r Gm! r Gm! |
  r A7! r A7! |
  r Dm! r Dm! |

Pattern %hit_III1_08_90:
  key=Dm 4: 90@
  d*2 r d*2 r |
  d*2 r d*2 r |
  a*1 r a*1 r |
  d*2 r d*2 r |
  g*1 r g*1 r |
  d*2 r d*2 r |
  a*1 r a*1 r |
  d*2 r d*2 r |

Pattern %hit_III2_08_95:
  key=Dm 4: 95@
  b*1 r b*1 r |
  g*1 r g*1 r |
  b*1 r b*1 r |
  a*1 r a*1 r |
  d*2 r d*2 r |
  g*1 r g*1 r |
  a*1 r a*1 r |
  d*2 r d*2 r |

Pattern %arp_III1_08_65:
  key=Dm 8: 65@
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  a*4 c#*5 e*5 g*5 e*5 c#*5 e*5 c#*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  a*4 c#*5 e*5 g*5 e*5 c#*5 e*5 c#*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |

Pattern %arp_III2_08_72:
  key=Dm 8: 72@
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |
  a*4 c#*5 e*5 g*5 e*5 c#*5 e*5 c#*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  a*4 c#*5 e*5 g*5 e*5 c#*5 e*5 c#*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |

Pattern %stab_III2_08_78:
  key=Dm 4: 78@
  r Bb! r Bb! |
  r Gm! r Gm! |
  r Bb! r Bb! |
  r A7! r A7! |
  r Dm! r Dm! |
  r Gm! r Gm! |
  r A7! r A7! |
  r Dm! r Dm! |

Pattern %rootsC_III1_08_85:
  key=Dm 4: 85@
  d*2 d*3 d*2 d*3 |
  d*2 d*3 d*2 d*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |
  d*2 d*3 d*2 d*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |

Pattern %rootsC_III2_08_90:
  key=Dm 4: 90@
  b*2 b*3 b*2 b*3 |
  g*2 g*3 g*2 g*3 |
  b*2 b*3 b*2 b*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |

Pattern %rootsB_III1_08_85:
  key=Dm 4: 85@
  d*2'1 |
  d*2'1 |
  a*1'1 |
  d*2'1 |
  g*1'1 |
  d*2'1 |
  a*1'1 |
  d*2'1 |

Pattern %rootsB_III2_08_88:
  key=Dm 4: 88@
  b*1'1 |
  g*1'1 |
  b*1'1 |
  a*1'1 |
  d*2'1 |
  g*1'1 |
  a*1'1 |
  d*2'1 |

Pattern %IV_Tema:
  key=D 8: 100@
  d*5 f*5 a*5 d*6 2f*6 2a*6 |
  g*6 f*6 e*6 d*6 2b*5 2g*5 |
  2c*6 e*6 g*6 2a*6 2e*6 |
  4d*6 2a*5 2f*5 |
  2b*5 d*6 f*6 2b*6 2a*6 |
  2g*6 b*6 a*6 2g*6 2f*6 |
  2a*5 c*6 e*6 2g*6 2e*6 |
  4d*6 4r |

Pattern %IV_Tema_giu:
  key=D 8: 100@
  d*4 f*4 a*4 d*5 2f*5 2a*5 |
  g*5 f*5 e*5 d*5 2b*4 2g*4 |
  2c*5 e*5 g*5 2a*5 2e*5 |
  4d*5 2a*4 2f*4 |
  2b*4 d*5 f*5 2b*5 2a*5 |
  2g*5 b*5 a*5 2g*5 2f*5 |
  2a*4 c*5 e*5 2g*5 2e*5 |
  4d*5 4r |

Pattern %IV_Corale:
  key=D 8: 90@
  2g*5 b*5 d*6 2g*6 2f*6 |
  2a*5 d*6 f*6 4a*6 |
  2g*5 b*5 e*6 2d*6 2b*5 |
  2c*6 e*6 g*6 4a*6 |
  2d*6 f*6 b*6 2a*6 2f*6 |
  2g*5 b*5 d*6 2g*6 2b*6 |
  2e*6 g*6 a*6 2c*7 2a*6 |
  6d*6 2r |

Pattern %IV_Corale_giu:
  key=D 8: 85@
  2g*4 b*4 d*5 2g*5 2f*5 |
  2a*4 d*5 f*5 4a*5 |
  2g*4 b*4 e*5 2d*5 2b*4 |
  2c*5 e*5 g*5 4a*5 |
  2d*5 f*5 b*5 2a*5 2f*5 |
  2g*4 b*4 d*5 2g*5 2b*5 |
  2e*5 g*5 a*5 2c*6 2a*5 |
  6d*5 2r |

Pattern %IV_SoggCelli:
  key=D 8: 85@
  d*3 e*3 f*3 g*3 2a*3 2f*3 |
  b*3 a*3 g*3 f*3 2e*3 2d*3 |

Pattern %IV_RispVle:
  key=D 8: 85@
  a*3 b*3 c*4 d*4 2e*4 2c*4 |
  f*4 e*4 d*4 c*4 2b*3 2a*3 |

Pattern %IV_SoggV2:
  key=D 8: 88@
  d*5 e*5 f*5 g*5 2a*5 2f*5 |
  b*5 a*5 g*5 f*5 2e*5 2d*5 |

Pattern %IV_RispV1:
  key=D 8: 90@
  a*5 b*5 c*6 d*6 2e*6 2c*6 |
  f*6 e*6 d*6 c*6 2b*5 2a*5 |

Pattern %rootsF_IVM_08_90:
  key=D 4: 90@
  d*2'1 |
  g*2'1 |
  a*2'1 |
  d*2'1 |
  b*2'1 |
  g*2'1 |
  a*2'1 |
  d*2'1 |

Pattern %rootsF_IVF_08_70:
  key=D 4: 70@
  d*2'1 |
  d*2'1 |
  a*2'1 |
  a*2'1 |
  d*2'1 |
  d*2'1 |
  a*2'1 |
  a*2'1 |

Pattern %rootsF_IVC_08_80:
  key=D 4: 80@
  g*2'1 |
  f*2'1 |
  e*2'1 |
  a*2'1 |
  b*2'1 |
  g*2'1 |
  a*2'1 |
  d*2'1 |

Pattern %rootsF_IVK_08_95:
  key=D 4: 95@
  d*2'1 |
  g*2'1 |
  a*2'1 |
  d*2'1 |
  b*2'1 |
  g*2'1 |
  a*2'1 |
  d*2'1 |

Pattern %chords_IVM_08_100:
  key=D 4: 100@
  D'1 |
  G'1 |
  A7'1 |
  D'1 |
  Bm'1 |
  G'1 |
  A7'1 |
  D'1 |

Pattern %chords_IVF_08_65:
  key=D 4: 65@
  D'1 |
  D'1 |
  A'1 |
  A'1 |
  D'1 |
  D'1 |
  A'1 |
  A7'1 |

Pattern %chords_IVC_08_80:
  key=D 4: 80@
  G'1 |
  D/F#'1 |
  Em'1 |
  A7'1 |
  Bm'1 |
  G'1 |
  A7'1 |
  D'1 |

Pattern %chords_IVK_08_105:
  key=D 4: 105@
  D'1 |
  G'1 |
  A7'1 |
  D'1 |
  Bm'1 |
  G'1 |
  A7'1 |
  D'1 |

Pattern %hit_IVM_08_100:
  key=D 4: 100@
  d*2 r d*2 r |
  g*1 r g*1 r |
  a*1 r a*1 r |
  d*2 r d*2 r |
  b*1 r b*1 r |
  g*1 r g*1 r |
  a*1 r a*1 r |
  d*2 r d*2 r |

Pattern %roll_IVF_08_60:
  key=D 16: 60@
  d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 |
  d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 |
  a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 |
  a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 |
  d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 |
  d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 d*2 |
  a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 |
  a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 a*1 |

Pattern %hitS_IVC_08_60:
  key=D 4: 60@
  g*1 r r r |
  f*1 r r r |
  e*1 r r r |
  a*1 r r r |
  b*1 r r r |
  g*1 r r r |
  a*1 r r r |
  d*2 r r r |

Pattern %hit_IVK_04_105:
  key=D 4: 105@
  d*2 r d*2 r |
  g*1 r g*1 r |
  a*1 r a*1 r |
  d*2 r d*2 r |

Pattern %hit_IVK_47:
  key=D 4:
  b*1 r b*1 r |
  g*1 r g*1 r |
  a*1 r a*1 r |

Pattern %arp_IVM_08_75:
  key=D 8: 75@
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  e*5 g*5 a*5 c*6 a*5 g*5 a*5 g*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  e*5 g*5 a*5 c*6 a*5 g*5 a*5 g*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |

Pattern %chords_IVF_68_55:
  key=D 4: 55@
  A'1 |
  A7'1 |

Pattern %arp_IVC_08_70:
  key=D 8: 70@
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  e*5 g*5 b*5 g*5 e*5 g*5 b*5 g*5 |
  e*5 g*5 a*5 c*6 a*5 g*5 a*5 g*5 |
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  e*5 g*5 a*5 c*6 a*5 g*5 a*5 g*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |

Pattern %arp_IVK_08_85:
  key=D 8: 85@
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  e*5 g*5 a*5 c*6 a*5 g*5 a*5 g*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |
  d*5 f*5 b*5 f*5 d*5 f*5 b*5 f*5 |
  d*5 g*5 b*5 g*5 d*5 g*5 b*5 g*5 |
  e*5 g*5 a*5 c*6 a*5 g*5 a*5 g*5 |
  d*5 f*5 a*5 f*5 d*5 f*5 a*5 f*5 |

Pattern %chords_IVM_08_80:
  key=D 4: 80@
  D'1 |
  G'1 |
  A7'1 |
  D'1 |
  Bm'1 |
  G'1 |
  A7'1 |
  D'1 |

Pattern %chords_IVF_48_60:
  key=D 4: 60@
  D'1 |
  D'1 |
  A'1 |
  A7'1 |

Pattern %chords_IVC_08_70:
  key=D 4: 70@
  G'1 |
  D/F#'1 |
  Em'1 |
  A7'1 |
  Bm'1 |
  G'1 |
  A7'1 |
  D'1 |

Pattern %chords_IVK_08_88:
  key=D 4: 88@
  D'1 |
  G'1 |
  A7'1 |
  D'1 |
  Bm'1 |
  G'1 |
  A7'1 |
  D'1 |

Pattern %rootsC_IVM_08_90:
  key=D 4: 90@
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |
  b*2 b*3 b*2 b*3 |
  g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |

Pattern %rootsC_IVF_28_70:
  key=D 4: 70@
  a*2 a*3 a*2 a*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |
  d*2 d*3 d*2 d*3 |
  a*2 a*3 a*2 a*3 |
  a*2 a*3 a*2 a*3 |

Pattern %rootsC_IVC_08_80:
  key=D 4: 80@
  g*2 g*3 g*2 g*3 |
  f*2 f*3 f*2 f*3 |
  e*2 e*3 e*2 e*3 |
  a*2 a*3 a*2 a*3 |
  b*2 b*3 b*2 b*3 |
  g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |

Pattern %rootsC_IVK_08_95:
  key=D 4: 95@
  d*2 d*3 d*2 d*3 |
  g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |
  b*2 b*3 b*2 b*3 |
  g*2 g*3 g*2 g*3 |
  a*2 a*3 a*2 a*3 |
  d*2 d*3 d*2 d*3 |

Pattern %rootsB_IVM_08_92:
  key=D 4: 92@
  d*2'1 |
  g*1'1 |
  a*1'1 |
  d*2'1 |
  b*1'1 |
  g*1'1 |
  a*1'1 |
  d*2'1 |

Pattern %rootsB_IVF_08_70:
  key=D 4: 70@
  d*2'1 |
  d*2'1 |
  a*1'1 |
  a*1'1 |
  d*2'1 |
  d*2'1 |
  a*1'1 |
  a*1'1 |

Pattern %rootsB_IVC_08_82:
  key=D 4: 82@
  g*1'1 |
  f*1'1 |
  e*1'1 |
  a*1'1 |
  b*1'1 |
  g*1'1 |
  a*1'1 |
  d*2'1 |

Pattern %rootsB_IVK_08_98:
  key=D 4: 98@
  d*2'1 |
  g*1'1 |
  a*1'1 |
  d*2'1 |
  b*1'1 |
  g*1'1 |
  a*1'1 |
  d*2'1 |

// ================================================================ tracce

Violini1:
  $"Allegro con fuoco" %I_ThA
  4%R1 %I_ThB2
  %I_Dev
  %I_ThAr
  $"Adagio"
  %arp_II1_08_48
  %II_Violino
  $"Scherzo: Presto" %III_S1
  %III_S2
  $"Finale: Allegro con brio" %IV_Tema
  6%R1 %IV_RispV1
  %IV_Corale
  %IV_Tema

Violini2:
  %arp_IA_08_70
  %arp_IB_08_55
  vol=60 >>
  %arp_ID_08_80
  vol=100
  %arp_IR_08_85
  %chords_II1_08_45
  %arp_II2_08_50
  %arp_III1_08_65
  %arp_III2_08_72
  %arp_IVM_08_75
  4%R1 %IV_SoggV2 %chords_IVF_68_55
  %arp_IVC_08_70
  %arp_IVK_08_85

Viole:
  %chords_IA_08_78
  %chords_IB_08_50
  vol=60 >>
  %chords_ID_08_75
  vol=100
  %chords_IR_08_85
  %chords_II1_08_50
  %chords_II2_08_55
  %stab_III1_08_70
  %stab_III2_08_78
  %chords_IVM_08_80
  2%R1 %IV_RispVle %chords_IVF_48_60
  %chords_IVC_08_70
  %chords_IVK_08_88

Violoncelli:
  %rootsC_IA_08_90
  %rootsC_IB_08_60
  %rootsC_ID_08_85
  %rootsC_IR_08_95
  %rootsW_II1_08_70
  %rootsW_II2_08_72
  %rootsC_III1_08_85
  %rootsC_III2_08_90
  %rootsC_IVM_08_90
  %IV_SoggCelli %rootsC_IVF_28_70
  %rootsC_IVC_08_80
  %rootsC_IVK_08_95

Contrabbassi:
  %rootsB_IA_08_92
  %rootsB_IB_08_60
  %rootsB_ID_08_85
  %rootsB_IR_08_98
  %rootsB_II1_08_60
  %rootsB_II2_08_62
  %rootsB_III1_08_85
  %rootsB_III2_08_88
  %rootsB_IVM_08_92
  %rootsB_IVF_08_70
  %rootsB_IVC_08_82
  %rootsB_IVK_08_98

Flauto:
  %I_ThA
  8%R1
  8%R1
  %I_ThAr
  16%R1
  %III_S1
  %III_S2
  %IV_Tema
  8%R1
  %IV_Corale
  %IV_Tema

Oboe:
  %I_ThA_giu
  4%R1 %I_ThB2_giu
  8%R1
  %I_ThAr_giu
  %II_Oboe
  8%R1
  8%R1
  8%R1
  %IV_Tema_giu
  8%R1
  %IV_Corale_giu
  %IV_Tema_giu

Clarinetto:
  8%R1
  %I_ThB1_giu 4%R1
  4%R1 4: 80@ a*4'1 | a*4'1 | a*4'1 | a*4'1 |
  8%R1
  8%R1
  %II_Violino_giu
  8%R1
  %stab_III2_08_75
  8%R1
  8%R1
  8%R1
  8%R1

Fagotto:
  %rootsF_IA_08_90
  %rootsF_IB_08_55
  %rootsF_ID_08_70
  %rootsF_IR_08_95
  %rootsF_II1_08_55
  %rootsF_II2_08_58
  %rootsF_III1_08_75
  %rootsF_III2_08_80
  %rootsF_IVM_08_90
  %rootsF_IVF_08_70
  %rootsF_IVC_08_80
  %rootsF_IVK_08_95

Corni:
  %chords_IA_08_100
  %chords_IB_08_55
  %chords_ID_08_80
  %chords_IR_08_105
  %chords_II1_08_50
  %chords_II2_08_55
  %stab_III1_08_70
  %stab_III2_08_90
  %chords_IVM_08_100
  %chords_IVF_08_65
  %chords_IVC_08_80
  %chords_IVK_08_105

Trumpet:
  8%R1
  8%R1
  8%R1
  %I_ThAr_giu
  16%R1
  8%R1
  8%R1
  %IV_Tema_giu
  8%R1
  %IV_Corale_giu
  %IV_Tema_giu

Timpani:
  %hit_IA_08_100
  %hitS_IB_08_45
  %roll_ID_08_70
  %hit_IR_08_105
  tempo=58
  16%R1
  tempo=152
  %hit_III1_08_90
  %hit_III2_08_95
  tempo=126
  %hit_IVM_08_100
  %roll_IVF_08_60
  %hitS_IVC_08_60
  %hit_IVK_04_105
  100@ tempo=126 <<
  %hit_IVK_47
  key=D 4: d*2$fermata r r r |
  tempo=56

// ================================================================ mixer

Mixer Flauto:
  volume: 70 pan: 0.25 mute: no solo: no reverb: 25

Mixer Oboe:
  volume: 67 pan: -0.2 mute: no solo: no reverb: 25

Mixer Clarinetto:
  volume: 66 pan: 0.15 mute: no solo: no reverb: 25

Mixer Fagotto:
  volume: 66 pan: -0.3 mute: no solo: no reverb: 20

Mixer Corni:
  volume: 69 pan: 0.3 mute: no solo: no reverb: 28

Mixer Trumpet:
  volume: 67 pan: 0.4 mute: no solo: no reverb: 28

Mixer Timpani:
  volume: 72 pan: 0.0 mute: no solo: no reverb: 30

Mixer Violini1:
  volume: 75 pan: -0.5 mute: no solo: no reverb: 22

Mixer Violini2:
  volume: 70 pan: -0.3 mute: no solo: no reverb: 22

Mixer Viole:
  volume: 67 pan: 0.2 mute: no solo: no reverb: 22

Mixer Violoncelli:
  volume: 72 pan: 0.45 mute: no solo: no reverb: 20

Mixer Contrabbassi:
  volume: 70 pan: 0.6 mute: no solo: no reverb: 15
