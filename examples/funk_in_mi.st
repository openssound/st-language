// Funk in Mi: un groove funk in Mi minore, 50 battute di sedicesimi.
//
// Clavinet, chitarra "chicken scratch", basso, sezione di fiati, tromba
// solista e batteria. Un unico giro di quattro battute che torna sempre,
// con un ritornello di accordi di nona. Cosa c'e' dentro:
//   - lo swing delle semicrome (swing16=58): il groove "sporco" del funk,
//     scritto sempre con la griglia 16: (sedici colpi a battuta);
//   - note fantasma (rullante a velocity bassa) e pause che fanno il ritmo;
//   - accordi spezzettati a staccato (`Em7!`) per il "gratto" della chitarra,
//     con il wah-wah automatico (cc74=): il filtro si apre e si chiude;
//   - le entrate dei fiati con l'accento ($accent) e le pause di durata
//     multipla (`2r`, `9r`);
//   - il basso che anticipa il tempo (shift=-8, in millisecondi);
//   - uno stop di due battute con tutti gli strumenti, poi l'assolo di tromba;
//   - strumenti definiti nel file (clavinet, fiati).
//
// Forma: introduzione 4, strofa 8, ritornello 8, strofa 8, stop 2,
// assolo 8, ritornello 8, coda 4.
//   Giro    Em7 | Em7 | A9 | Em7
//   Ritorn. C9 | B7#9 | Em7 | Em7

ST: 2.6
Tempo: 104 BPM
Metrica: 4/4
Tonalita: Em

Strumento Clavinet:
  program=7 percussione=no ottava=4 range=48-88 poly=si voicing=spread

Strumento Fiati:
  program=61 percussione=no ottava=4 range=55-88 poly=si voicing=spread

Pattern %Rest:
  4: 4r |

// ---------------------------------------------------------------- batteria

Pattern %DrFunk1:
  16: 100@ [kick hihat] 45@ hihat 65@ hihat 45@ hihat 105@ [snare hihat] 45@ hihat 65@ hihat 95@ [kick hihat] 45@ hihat 38@ [snare hihat] 95@ [kick hihat] 45@ hihat 105@ [snare hihat] 45@ hihat 65@ hihat 38@ [snare hihat] |

Pattern %DrFunk2:
  16: 100@ [kick hihat] 45@ hihat 65@ hihat 45@ hihat 105@ [snare hihat] 45@ hihat 65@ hihat 95@ [kick hihat_open] 45@ hihat 38@ [snare hihat] 45@ hihat 95@ [kick hihat] 105@ [snare hihat] 45@ hihat 65@ hihat 38@ [snare hihat] |

Pattern %DrRide:
  16: 105@ [kick ride] 50@ ride 70@ ride 50@ ride 105@ [snare ride] 50@ ride 70@ ride 95@ [kick ride] 50@ ride 38@ [snare ride] 95@ [kick ride] 50@ ride 105@ [snare ride] 50@ ride 70@ ride 38@ [snare ride] |

Pattern %DrFill:
  16: 100@ [kick hihat] r snare snare tom1 tom1 tom2 tom2 floor floor 110@ [kick snare] [kick snare] [kick crash] r r r |

Pattern %DrFunk4:
  3%DrFunk1 %DrFunk2

Pattern %DrFunk4F:
  %DrFunk1 %DrFunk2 %DrFunk1 %DrFill

Pattern %DrChorus4:
  3%DrRide %DrFill

// ---------------------------------------------------------------- basso

Pattern %BsE1:
  key=Em 16: 96@ e*2 r r e*2 r r e*3 r e*2 r g*2 r a*2 r b*2 e*3 |

Pattern %BsE2:
  key=Em 16: 96@ e*2 r e*2 r r e*3 d*3 r e*2 r r e*2 g*2 a*2 b*2 d*3 |

Pattern %BsA9:
  key=Em 16: 96@ a*1 r r a*1 r r a*2 r a*1 r c#*2 r e*2 r g*2 a*2 |

Pattern %BsC9:
  key=Em 16: 96@ c*2 r r c*2 r r c*3 r c*2 r e*2 r g*2 r bb*2 c*3 |

Pattern %BsB7:
  key=Em 16: 96@ b*1 r r b*1 r r b*2 r b*1 r d#*2 r f#*2 r a*2 b*2 |

Pattern %BsVerse4:
  %BsE1 %BsE2 %BsA9 %BsE1

Pattern %BsChorus4:
  %BsC9 %BsB7 %BsE1 %BsE2

// ---------------------------------------------------------------- chitarra (gratto)

Pattern %GtEm:
  16: 78@ Em7! r Em7! Em7! r Em7! r Em7! Em7! r Em7! Em7! r Em7! r Em7! |

Pattern %GtA9:
  16: 78@ A9! r A9! A9! r A9! r A9! A9! r A9! A9! r A9! r A9! |

Pattern %GtC9:
  16: 78@ C9! r C9! C9! r C9! r C9! C9! r C9! C9! r C9! r C9! |

Pattern %GtB7:
  16: 78@ B7#9! r B7#9! B7#9! r B7#9! r B7#9! B7#9! r B7#9! B7#9! r B7#9! r B7#9! |

Pattern %GtVerse4:
  %GtEm %GtEm %GtA9 %GtEm

Pattern %GtChorus4:
  %GtC9 %GtB7 %GtEm %GtEm

// ---------------------------------------------------------------- clavinet (il riff)

Pattern %ClE1:
  key=Em 16: 92@ e*4 r g*4 a*4 r b*4 a*4 r g*4 r e*4 r d*4 r e*4 r |

Pattern %ClE2:
  key=Em 16: 92@ e*4 r e*4 g*4 r b*4 g*4 r e*4 r d*4 r e*4 g*4 a*4 b*4 |

Pattern %ClA9:
  key=Em 16: 92@ a*4 r c#*5 e*5 r c#*5 a*4 r g*4 r a*4 r e*4 r a*4 r |

Pattern %ClC9:
  key=Em 16: 92@ c*5 r e*5 g*5 r e*5 c*5 r bb*4 r c*5 r g*4 r c*5 r |

Pattern %ClB7:
  key=Em 16: 92@ b*4 r d#*5 f#*5 r d*5 b*4 r a*4 r b*4 r f#*4 r b*4 r |

Pattern %ClVerse4:
  %ClE1 %ClE2 %ClA9 %ClE1

Pattern %ClChorus4:
  %ClC9 %ClB7 %ClE1 %ClE2

// ---------------------------------------------------------------- fiati (stacchi) e tromba (assolo)

Pattern %HnChorus:
  16: 105@
  C9!$accent 2r C9! 2r C9! 9r |
  B7#9!$accent 2r B7#9! 2r B7#9! 9r |
  Em7!$accent 2r Em7! 2r Em7! 3r Em7! r Em7! 3r |
  16r |

Pattern %Solo:
  key=Em 16: 100@
  r r e*5 g*5 r b*5 r g*5 4a*5 r e*5 2r |
  4b*5 a*5 g*5 r e*5 4g*5 r d*5 e*5 r |
  r a*5 c#*6 r e*6 r c#*6 a*5 4g*5 2r e*5 r |
  4e*5 r g*5 b*5 r e*6 r d*6 b*5 r 2a*5 r |
  r c*6 bb*5 g*5 r e*5 g*5 r 4c*6 r bb*5 2r |
  4d#*6 f#*6 r d#*6 b*5 r 4a*5 r f#*5 r |
  r e*5 g*5 b*5 e*6 r d*6 b*5 4g*5 r e*5 g*5 r |
  6e*6$fermata 10r |

// ================================================================ tracce

Clavinet:

Box Clavinet "Strofa 1" |16:
  // strofa 1
  swing16=58 2%ClVerse4

Box Clavinet "Ritornello 1" |48:
  // ritornello 1: il clavinet scende di volume sotto i fiati
  swing16=58 vol=70 2%ClChorus4

Box Clavinet "Strofa 2" |80:
  // strofa 2
  swing16=58 vol=100 2%ClVerse4

Box Clavinet "Assolo" |120:
  // assolo: il clavinet accompagna piano
  swing16=58 vol=60 %ClVerse4 %ClChorus4

Box Clavinet "Ritornello 2" |152:
  // ritornello 2
  swing16=58 vol=100 2%ClChorus4

Box Clavinet "Coda" |184:
  // coda
  swing16=58 %ClE1 %ClE2 %ClE1
  16: 105@ [e*4 g*4 b*4 e*5]$accent 15r |

Guitar 1:

Box Guitar 1 "Introduzione" |8:
  // introduzione: la chitarra entra alla terza battuta
  swing16=58 shift=5 %GtEm %GtEm

Box Guitar 1 "Strofa 1" |16:
  // strofa 1: il wah si apre e si chiude
  swing16=58 shift=5 cc74=30 >>
  %GtVerse4
  cc74=110 >>
  %GtVerse4
  cc74=30

Box Guitar 1 "Ritornello 1" |48:
  // ritornello 1
  swing16=58 shift=5 2%GtChorus4

Box Guitar 1 "Strofa 2" |80:
  // strofa 2
  swing16=58 shift=5 cc74=30 >>
  %GtVerse4
  cc74=110 >>
  %GtVerse4
  cc74=70

Box Guitar 1 "Assolo" |120:
  // assolo
  swing16=58 shift=5 %GtVerse4 %GtChorus4

Box Guitar 1 "Ritornello 2 e coda" |152:
  // ritornello 2 e coda
  swing16=58 shift=5 2%GtChorus4
  %GtEm %GtEm %GtEm
  16: 105@ Em7!$accent 15r |

Bass:

Box Bass "Groove" |0:
  // il basso suona un po' prima del tempo
  swing16=58 shift=-8
  %BsVerse4
  2%BsVerse4
  2%BsChorus4
  2%BsVerse4

Box Bass "Stop" |112:
  // stop
  swing16=58 shift=-8 16: 110@ e*2 15r |
  16: 100@ e*2 7r e*2 r e*2 r e*2 g*2 a*2 b*2 |

Box Bass "Assolo" |120:
  // assolo
  swing16=58 shift=-8 16: 100@ %BsE1 %BsE2 %BsA9 %BsE1 %BsC9 %BsB7 %BsE1 %BsE2
  2%BsChorus4

Box Bass "Coda" |184:
  // coda
  swing16=58 shift=-8 16: 100@ %BsE1 %BsE2 %BsE1
  16: 110@ e*2 15r |

Fiati:

Box Fiati "Ritornello 1" |48:
  // ritornello 1
  swing16=58 2%HnChorus

Box Fiati "Stop" |112:
  // stop: tutti insieme
  swing16=58 16: 110@ Em7!$accent 15r |
  16: 105@ Em7!$accent 7r Em7! r Em7! 5r |

Box Fiati "Ritornello 2" |152:
  // ritornello 2
  swing16=58 16: 105@ 2%HnChorus

Box Fiati "Coda" |184:
  // coda
  swing16=58 16: 105@ 16: 105@ Em7!$accent 2r Em7! 2r Em7! 9r |
  16: 105@ Em7!$accent 2r Em7! 2r Em7! 9r |
  16r |
  16: 110@ Em7!$accent 15r |

Trumpet:

Box Trumpet "Fino all'assolo" |120:
  // fino all'assolo
  swing16=58 $"assolo" %Solo

Box Trumpet "Ritornello 2" |152:
  // ritornello 2: note lunghe sopra i fiati
  swing16=58 1: 92@ bb*5 | a*5 | g*5 | g*5 | bb*5 | a*5 | b*5 | e*6 |

Drums:

Box Drums "Introduzione" |0:
  // introduzione
  swing16=58 %DrFunk4

Box Drums "Strofa 1" |16:
  // strofa 1, ritornello 1, strofa 2
  swing16=58 %DrFunk4 %DrFunk4F
  2%DrChorus4
  %DrFunk4 %DrFunk4F

Box Drums "Stop" |112:
  // stop: i colpi in battere e il rullo
  swing16=58 16: 110@ [kick crash] 3r 100@ snare 3r 100@ kick 3r 105@ snare 3r |
  16: 100@ kick r r r snare r r r kick r snare r tom1 tom2 floor [kick crash] |

Box Drums "Assolo" |120:
  // assolo
  swing16=58 16: 100@ %DrFunk4 %DrFunk4F

Box Drums "Ritornello 2" |152:
  // ritornello 2
  swing16=58 16: 100@ 2%DrChorus4

Box Drums "Coda" |184:
  // coda
  swing16=58 16: 100@ %DrFunk1 %DrFunk2 %DrFill
  16: 110@ [kick crash] 15r |

// ================================================================ mixer

Mixer Clavinet:
  volume: 80 pan: -0.3 mute: no solo: no reverb: 8

Mixer Guitar 1:
  volume: 72 pan: 0.45 mute: no solo: no

Mixer Bass:
  volume: 100 pan: 0 mute: no solo: no

Mixer Fiati:
  volume: 80 pan: 0.15 mute: no solo: no reverb: 18

Mixer Trumpet:
  volume: 88 pan: 0.3 mute: no solo: no reverb: 22

Mixer Drums:
  volume: 88 pan: 0 mute: no solo: no reverb: 10
