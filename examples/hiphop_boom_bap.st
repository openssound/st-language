// Boom bap di mezzanotte: un beat hip hop in La minore, 56 battute a 90 BPM.
//
// Batteria, percussioni, basso sintetico, piano elettrico, vibrafono e archi:
// il suono "boom bap" da strumentale, con il cassa che arriva un po' in
// ritardo e i rullanti sul secondo e quarto movimento. Forma:
//   introduzione 4 + strofa 16 + ritornello 8 + strofa 16
//   + ritornello 8 + coda 4
//   Strofa      Am9 | Fmaj7 | Dm7 | E7
//   Ritornello  Fmaj7 | G7 | Am9 | Am9
// Cosa c'e' dentro:
//   - lo swing delle semicrome (swing16=58), scritto sempre sulla griglia 16:
//     la cassa e il rullante "fantasma" cadono sulle semicrome dispari e
//     pari e danno il dondolio tipico del genere;
//   - rullante e battito di mani insieme, [snare clap hihat], e i colpi
//     fantasma a velocity bassa;
//   - il basso con le note lunghe (`7a*1` dura sette semicrome), che segue
//     la cassa e lascia respirare il groove;
//   - il piano elettrico a colpi sincopati: gli accordi hanno la durata
//     davanti (`3Am9`) e la `!` per il colpo corto;
//   - un fill di batteria (rullante, tom, cassa e piatto) in fondo a ogni
//     strofa e a ogni ritornello;
//   - il tema del vibrafono in ottave relative (rel:), le percussioni
//     (maracas, tamburello, conga) e gli archi lenti nel ritornello;
//   - la coda con la corona ($fermata) su tutti gli strumenti;
//   - strumenti definiti nel file (basso sintetico, piano elettrico,
//     vibrafono, archi).

ST: 2.6
Tempo: 90 BPM
Metrica: 4/4
Tonalita: Am

Strumento Rhodes:
  program=4 percussione=no ottava=4 range=48-84 poly=si voicing=spread

Strumento Synbass:
  program=38 percussione=no ottava=2 range=28-60 poly=no voicing=monophonic

Strumento Vibrafono:
  program=11 percussione=no ottava=5 range=53-96 poly=no voicing=monophonic

Strumento Archi:
  program=49 percussione=no ottava=4 range=36-96 poly=si voicing=spread

// ---------------------------------------------------------------- batteria

Pattern %DrHats:
  16: 60@ hihat 28@ hihat 45@ hihat 28@ hihat 60@ hihat 28@ hihat 45@ hihat 28@ hihat 60@ hihat 28@ hihat 45@ hihat 28@ hihat 60@ hihat 28@ hihat 45@ hihat 35@ hihat_open |

Pattern %DrBoom:
  16: 105@ [kick hihat] r 50@ hihat 28@ hihat 100@ [snare clap hihat] r 50@ hihat 80@ kick 60@ hihat r 100@ [kick hihat] 28@ hihat 100@ [snare clap hihat] r 50@ hihat 35@ snare |

Pattern %DrBoom2:
  16: 105@ [kick hihat] r 50@ hihat 28@ hihat 100@ [snare clap hihat] r 50@ hihat r 100@ [kick hihat] 75@ kick 50@ hihat 28@ hihat 100@ [snare clap hihat] r 50@ hihat_open r |

Pattern %DrFill:
  16: 105@ [kick hihat] r 50@ hihat r 100@ [snare clap] r 60@ snare 70@ snare 85@ snare 90@ tom2 95@ tom1 100@ floor 105@ [kick snare] 90@ snare 105@ [kick snare] 110@ [kick crash] |

Pattern %DrVerse4:
  %DrBoom %DrBoom2 %DrBoom %DrBoom2

Pattern %DrVerse4Fill:
  %DrBoom %DrBoom2 %DrBoom %DrFill

// ---------------------------------------------------------------- percussioni

Pattern %PercHook:
  16: 40@ maracas r 55@ maracas r 90@ tambourine r 55@ maracas r 40@ maracas r 55@ maracas r 90@ tambourine r 55@ maracas r |

Pattern %PercVerse:
  16: r r r r r r r 70@ conga_open r r r r r r 60@ conga_low r |

// ---------------------------------------------------------------- basso

Pattern %BsAm9:
  key=Am 16: 7a*1 3a*1 6g*1 |

Pattern %BsF:
  key=Am 16: 7f*1 3f*1 6c*2 |

Pattern %BsDm:
  key=Am 16: 7d*2 3d*2 6c*2 |

Pattern %BsE:
  key=Am 16: 7e*2 3e*2 6b*1 |

Pattern %BsG:
  key=Am 16: 7g*1 3g*1 6d*2 |

Pattern %BsAmHook:
  key=Am 16: 7a*1 3a*1 6e*2 |

Pattern %BsAmHook2:
  key=Am 16: 7a*1 2r 3a*1 4g*1 |

Pattern %BsVerse4:
  %BsAm9 %BsF %BsDm %BsE

Pattern %BsHook4:
  %BsF %BsG %BsAmHook %BsAmHook2

// ---------------------------------------------------------------- piano elettrico

Pattern %RhAm9:
  16: 72@ 3Am9 r 56@ 2Am9 r 66@ 3Am9 r 50@ Am9! r 60@ 2Am9 r |

Pattern %RhF:
  16: 72@ 3Fmaj7 r 56@ 2Fmaj7 r 66@ 3Fmaj7 r 50@ Fmaj7! r 60@ 2Fmaj7 r |

Pattern %RhDm:
  16: 72@ 3Dm7 r 56@ 2Dm7 r 66@ 3Dm7 r 50@ Dm7! r 60@ 2Dm7 r |

Pattern %RhE:
  16: 72@ 3E7 r 56@ 2E7 r 66@ 3E7 r 50@ E7! r 60@ 2E7 r |

Pattern %RhG:
  16: 72@ 3G7 r 56@ 2G7 r 66@ 3G7 r 50@ G7! r 60@ 2G7 r |

Pattern %RhVerse4:
  %RhAm9 %RhF %RhDm %RhE

Pattern %RhHook4:
  %RhF %RhG %RhAm9 %RhAm9

// ---------------------------------------------------------------- vibrafono

Pattern %LeadHook:
  rel: key=Am 16:
  2r 2e 2g 4a 2g 2e 2r |
  2r 2d 2g 4b 2a 2g 2r |
  2r 2e 2a 4c 2b 2a 2g |
  6a 2g 4e 4r |

Pattern %LeadOutro:
  rel: key=Am 16:
  2r 2e 2a 4c 2b 2a 2g |
  2r 2c 2e 4a 2g 2e 2r |
  2r 2d 2f 4a 2g 2f 2e |
  16a$fermata |

// ---------------------------------------------------------------- archi

Pattern %PadHook:
  Fmaj7'1 | G7'1 | Am9'1< | Am9'1 |

Pattern %PadOutro:
  Am9'1 | Fmaj7'1 | Dm7'1 | Am9'1$fermata |

// ================================================================ tracce

Drums:

Box Drums "Introduzione" |0:
  // introduzione: soltanto i charleston
  swing16=58 4%DrHats

Box Drums "Strofa 1" |16:
  // strofa 1: tre giri di groove e il fill in fondo
  swing16=58 3%DrVerse4 %DrVerse4Fill

Box Drums "Ritornello 1" |80:
  // ritornello 1
  swing16=58 %DrVerse4 %DrVerse4Fill

Box Drums "Strofa 2" |112:
  // strofa 2
  swing16=58 3%DrVerse4 %DrVerse4Fill

Box Drums "Ritornello 2" |176:
  // ritornello 2
  swing16=58 %DrVerse4 %DrVerse4Fill

Box Drums "Coda" |208:
  // coda: il groove si ferma sull'ultimo colpo
  swing16=58 %DrBoom %DrBoom2 %DrBoom
  16: 100@ [kick crash] 15r |

Traccia Percussioni [Drums]:

Box Percussioni "Ritornello 1" |80:
  // ritornello 1: maracas e tamburello
  swing16=58 8%PercHook

Box Percussioni "Strofa 2" |112:
  // strofa 2: le conga
  swing16=58 16%PercVerse

Box Percussioni "Ritornello 2" |176:
  // ritornello 2
  swing16=58 8%PercHook

Synbass:

Box Synbass "Strofa 1" |16:
  // strofa 1: il basso entra con la strofa
  swing16=58 shift=-6 100@ 4%BsVerse4

Box Synbass "Ritornello 1" |80:
  // ritornello 1
  swing16=58 shift=-6 105@ 2%BsHook4

Box Synbass "Strofa 2" |112:
  // strofa 2
  swing16=58 shift=-6 100@ 4%BsVerse4

Box Synbass "Ritornello 2" |176:
  // ritornello 2
  swing16=58 shift=-6 105@ 2%BsHook4

Box Synbass "Coda" |208:
  // coda
  swing16=58 shift=-6 100@ %BsAm9 %BsF %BsDm
  16: 90@ 16a*1$fermata |

Rhodes:

Box Rhodes "Introduzione" |0:
  // introduzione: il piano da solo
  swing16=58 vol=70 %RhVerse4

Box Rhodes "Strofa 1" |16:
  // strofa 1
  swing16=58 vol=85 4%RhVerse4

Box Rhodes "Ritornello 1" |80:
  // ritornello 1
  swing16=58 vol=95 2%RhHook4

Box Rhodes "Strofa 2" |112:
  // strofa 2
  swing16=58 vol=85 4%RhVerse4

Box Rhodes "Ritornello 2" |176:
  // ritornello 2
  swing16=58 vol=95 2%RhHook4

Box Rhodes "Coda" |208:
  // coda: il riverbero cresce mentre il beat si spegne
  swing16=58 rev=20 >>
  %RhAm9 %RhF %RhDm
  Am9'1$fermata |
  rev=70

Vibrafono:

Box Vibrafono "Ritornello 1" |80:
  // ritornello 1: il tema, due volte
  swing16=58 90@ 2%LeadHook

Box Vibrafono "Ritornello 2" |176:
  // ritornello 2
  swing16=58 100@ 2%LeadHook

Box Vibrafono "Coda" |208:
  // coda
  swing16=58 85@ %LeadOutro

Archi:

Box Archi "Ritornello 1" |80:
  // ritornello 1: gli archi lenti
  60@ %PadHook %PadHook

Box Archi "Ritornello 2" |176:
  // ritornello 2
  70@ %PadHook %PadHook

Box Archi "Coda" |208:
  // coda
  55@ %PadOutro

// ================================================================ mixer

Mixer Drums:
  volume: 92 pan: 0 mute: no solo: no reverb: 10

Mixer Percussioni:
  volume: 62 pan: 0.35 mute: no solo: no reverb: 18

Mixer Synbass:
  volume: 98 pan: 0 mute: no solo: no

Mixer Rhodes:
  volume: 82 pan: -0.25 mute: no solo: no reverb: 28 chorus: 25

Mixer Vibrafono:
  volume: 72 pan: 0.3 mute: no solo: no reverb: 35

Mixer Archi:
  volume: 66 pan: 0 mute: no solo: no reverb: 40
