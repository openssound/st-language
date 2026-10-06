// Sabato a Lisbona: una bossa nova in La minore, in 64 battute.
//
// Flauto, chitarra nylon, pianoforte, basso e due strumenti a percussione
// (batteria e shaker). La forma e' A A' B A: otto battute ciascuna.
//   introduzione 4 + tema 32 + assolo di pianoforte su B e A (16)
//   + tema (A) 8 + coda con il rallentando 4.
// Cosa c'e' dentro:
//   - strumenti definiti nel file (flauto, chitarra nylon);
//   - il ritmo "3-3-2" della bossa (accordi sul 1, sul 2 e e sul 4) scritto con
//     le pause: `Am7 r r Am7 r r Am7 r`;
//   - il basso alla brasiliana (fondamentale e quinta), la batteria con il
//     rim-click sul ritmo della clave, lo shaker a sedicesimi con il volume
//     che cambia (accenti), una traccia in piu' dedicata a quello;
//   - la tonalita' (key=Am): il sol# di E7 e' scritto, il resto no;
//   - le automazioni: pan che attraversa il campo stereo durante l'assolo,
//     forcelle sugli accordi, il rallentando con tempo=;
//   - la corona sull'ultimo accordo.
//   A    Am7 | Dm7 | G7 | Cmaj7 | Fmaj7 | Bm7b5 E7 | Am7 | Am7 (A7 nella ripetizione)
//   B    Dm7 | G7 | Cmaj7 | Fmaj7 | Bm7b5 | E7 | Am7 | E7

ST: 2.6
Tempo: 126 BPM
Metrica: 4/4
Tonalita: Am

Strumento Flauto:
  program=73 percussione=no ottava=5 range=72-100 poly=no voicing=monophonic

Strumento Nylon:
  program=24 percussione=no ottava=3 range=40-88 poly=si voicing=spread

Pattern %Rest:
  4: 4r |

// ---------------------------------------------------------------- melodia (flauto)

Pattern %HeadA:
  key=Am 8: 84@
  r e*5 a*5 c*6 2b*5 a*5 e*5 |
  f*5 a*5 d*6 2c*6 a*5 f*5 d*5 |
  g*5 b*5 d*6 f*6 2e*6 d*6 b*5 |
  4c*6 2g*5 2e*5 |
  a*5 c*6 f*6 2e*6 c*6 a*5 f*5 |
  r d*6 f*6 b*5 2g#*5 b*5 e*6 |
  4a*5 2e*5 2c*5 |

Pattern %HeadEnd1:
  key=Am 8: 84@ 3a*5 r 4r |

Pattern %HeadEnd2:
  key=Am 8: 84@ 3a*5 r r g#*5 b*5 d*6 |

Pattern %HeadEnd3:
  key=Am 8: 84@ 6a*5 2r |

Pattern %HeadB:
  key=Am 8: 90@
  d*6 f*6 a*6 2g*6 f*6 d*6 a*5 |
  b*5 d*6 g*6 2f*6 d*6 b*5 g*5 |
  e*6 g*6 e*6 2c*6 b*5 g*5 e*5 |
  f*5 a*5 c*6 e*6 2a*6 2r |
  d*6 f*6 b*6 2a*6 f*6 d*6 b*5 |
  g#*5 b*5 e*6 d*6 b*5 g#*5 2e*5 |
  a*5 c*6 e*6 2a*6 g*6 e*6 c*6 |
  2b*5 g#*5 e*5 4r |

// ---------------------------------------------------------------- assolo (pianoforte)

Pattern %SoloB:
  key=Am 8: 92@
  d*5 f*5 a*5 d*6 c*6 a*5 f*5 e*5 |
  d*5 g*5 b*5 d*6 f*6 d*6 b*5 g*5 |
  e*5 g*5 c*6 e*6 d*6 b*5 g*5 e*5 |
  f*5 a*5 c*6 a*5 g*5 f*5 e*5 c*5 |
  b*4 d*5 f*5 b*5 a*5 f*5 d*5 b*4 |
  g#*4 b*4 e*5 g#*5 b*5 g#*5 e*5 b*4 |
  a*4 c*5 e*5 a*5 g*5 e*5 c*5 a*4 |
  g#*4 b*4 d*5 e*5 g#*5 e*5 d*5 b*4 |

Pattern %SoloA:
  key=Am 8: 96@
  2a*5 c*6 e*6 2d*6 c*6 a*5 |
  r d*5 f*5 a*5 d*6 c*6 a*5 f*5 |
  g*5 b*5 d*6 f*6 e*6 d*6 b*5 g*5 |
  2e*6 c*6 g*5 e*5 g*5 c*6 e*6 |
  f*6 e*6 c*6 a*5 c*6 a*5 f*5 a*5 |
  d*6 f*6 b*5 d*6 g#*5 b*5 e*6 d*6 |
  c*6 a*5 e*5 a*5 c*6 e*6 a*6 e*6 |
  4a*5 4r |

// ---------------------------------------------------------------- chitarra nylon (3-3-2)

Pattern %GtrIntro:
  key=Am 8: 66@
  Am7 r r Am7 r r Am7 r |
  Dm7 r r Dm7 r r Dm7 r |
  Bm7b5 r r Bm7b5 r r E7 r |
  E7 r r E7 r r E7 r |

Pattern %GtrA7:
  key=Am 8: 70@
  Am7 r r Am7 r r Am7 r |
  Dm7 r r Dm7 r r Dm7 r |
  G7 r r G7 r r G7 r |
  Cmaj7 r r Cmaj7 r r Cmaj7 r |
  Fmaj7 r r Fmaj7 r r Fmaj7 r |
  Bm7b5 r r Bm7b5 r r E7 r |
  Am7 r r Am7 r r Am7 r |

Pattern %GtrA8:
  key=Am 8: 70@ Am7 r r Am7 r r A7 r |

Pattern %GtrA8End:
  key=Am 8: 70@ Am7 r r Am7 r r Am7 r |

Pattern %GtrB:
  key=Am 8: 74@
  Dm7 r r Dm7 r r Dm7 r |
  G7 r r G7 r r G7 r |
  Cmaj7 r r Cmaj7 r r Cmaj7 r |
  Fmaj7 r r Fmaj7 r r Fmaj7 r |
  Bm7b5 r r Bm7b5 r r Bm7b5 r |
  E7 r r E7 r r E7 r |
  Am7 r r Am7 r r Am7 r |
  E7 r r E7 r r E7 r |

// ---------------------------------------------------------------- pianoforte (accordi lunghi sotto il tema)

Pattern %PnA7:
  key=Am 4: 58@
  Am7.drop2'1< |
  Dm7.drop2'1< |
  G7.drop2'1< |
  Cmaj7.drop2'1< |
  Fmaj7.drop2'1< |
  Bm7b5.drop2'2 E7.drop2'2 |
  Am7.drop2'1 |

Pattern %PnA8:
  key=Am 4: 58@ Am7.drop2'2 A7.drop2'2 |

Pattern %PnA8End:
  key=Am 4: 58@ Am7.drop2'1 |

Pattern %PnB:
  key=Am 4: 62@
  Dm7.drop2'1< |
  G7.drop2'1< |
  Cmaj7.drop2'1< |
  Fmaj7.drop2'1< |
  Bm7b5.drop2'1 |
  E7.drop2'1 |
  Am7.drop2'1 |
  E7.drop2'1 |

// ---------------------------------------------------------------- basso (fondamentale e quinta)

Pattern %BsAm:
  8: 86@ 3a*1 3e*2 2a*1 |

Pattern %BsDm:
  8: 86@ 3d*2 3a*1 2d*2 |

Pattern %BsG:
  8: 86@ 3g*1 3d*2 2g*1 |

Pattern %BsC:
  8: 86@ 3c*2 3g*1 2c*2 |

Pattern %BsF:
  8: 86@ 3f*1 3c*2 2f*1 |

Pattern %BsBE:
  8: 86@ 3b*1 3f*2 2e*2 |

Pattern %BsBm:
  8: 86@ 3b*1 3f*2 2b*1 |

Pattern %BsE:
  8: 86@ 3e*2 3b*1 2e*2 |

Pattern %BsA7:
  8: 86@ 3a*1 3e*2 2a*1 |

Pattern %BassIntro:
  %BsBE %BsE

Pattern %BassA7:
  %BsAm %BsDm %BsG %BsC %BsF %BsBE %BsAm

Pattern %BassB:
  %BsDm %BsG %BsC %BsF %BsBm %BsE %BsAm %BsE

// ---------------------------------------------------------------- batteria

Pattern %BossaA:
  8: 78@ [kick hihat] 45@ hihat hihat 66@ [rimshot hihat] 78@ [kick hihat] 45@ hihat 66@ [rimshot hihat] 45@ hihat |

Pattern %BossaB:
  8: 78@ [kick hihat] 45@ hihat 66@ [rimshot hihat] 45@ hihat 78@ [kick hihat] 45@ hihat 66@ [rimshot hihat] 45@ hihat |

Pattern %BossaRideA:
  8: 78@ [kick ride] 45@ ride ride 66@ [rimshot ride] 78@ [kick ride] 45@ ride 66@ [rimshot ride] 45@ ride |

Pattern %BossaRideB:
  8: 78@ [kick ride] 45@ ride 66@ [rimshot ride] 45@ ride 78@ [kick ride] 45@ ride 66@ [rimshot ride] 45@ ride |

Pattern %BossaFill:
  16: 75@ rimshot r rimshot r rimshot rimshot rimshot rimshot 90@ tom1 tom1 tom2 tom2 100@ [kick crash] r r r |

Pattern %BossaA3:
  %BossaA %BossaB

Pattern %BossaRide2:
  %BossaRideA %BossaRideB

Pattern %Drums8:
  3%BossaA3 %BossaA %BossaFill

Pattern %Drums8Ride:
  3%BossaRide2 %BossaRideA %BossaFill

// ---------------------------------------------------------------- shaker

Pattern %Shaker:
  16: 56@ maracas 34@ maracas 46@ maracas 34@ maracas 56@ maracas 34@ maracas 46@ maracas 34@ maracas 56@ maracas 34@ maracas 46@ maracas 34@ maracas 56@ maracas 34@ maracas 46@ maracas 34@ maracas |

// ================================================================ tracce

Flauto:

Box Flauto "Tema" |16:
  // tema: A, A', B, A
  $"dolce" %HeadA %HeadEnd1
  %HeadA %HeadEnd2
  %HeadB
  %HeadA %HeadEnd1

Box Flauto "Tema di nuovo (A) e coda" |208:
  // tema di nuovo (A) e coda
  vol=100 %HeadA %HeadEnd3
  key=Am 8: 80@
  r e*5 a*5 c*6 2b*5 a*5 e*5 |
  4a*5 4r |
  2%Rest

Nylon:

Box Nylon "Inizio" |0:
  vol=80 %GtrIntro

Box Nylon "Tema" |16:
  // tema: la chitarra con il ritmo 3-3-2
  %GtrA7 %GtrA8
  %GtrA7 %GtrA8
  %GtrB
  %GtrA7 %GtrA8End

Box Nylon "Assolo" |144:
  // assolo: la chitarra accompagna
  vol=95 %GtrB
  %GtrA7 %GtrA8End

Box Nylon "Tema e coda" |208:
  // tema e coda
  vol=80 %GtrA7 %GtrA8End
  key=Am 8: 66@
  Dm7 r r Dm7 r r Dm7 r |
  Bm7b5 r r Bm7b5 r r E7 r |
  Am7 r r Am7 r r Am7 r |
  1: Am7$fermata |

Piano:

Box Piano "Tema" |16:
  // tema: accordi lunghi e morbidi
  $"dolce" %PnA7 %PnA8
  %PnA7 %PnA8
  %PnB
  %PnA7 %PnA8End

Box Piano "Assolo" |144:
  // assolo: la mano destra, il pan si sposta da sinistra a destra
  pan=-0.5 >>
  $"assolo" %SoloB
  pan=0.5
  %SoloA
  pan=0

Box Piano "Tema e coda" |208:
  // tema e coda
  %PnA7 %PnA8End
  key=Am 4: 55@ Dm7.drop2'1 |
  Bm7b5.drop2'2 E7.drop2'2 |
  Am7.drop2'1 |
  Am7.drop2'1$fermata |

Bass:

Box Bass "Inizio" |8:
  %BassIntro

Box Bass "Tema" |16:
  // tema
  %BassA7 %BsA7
  %BassA7 %BsA7
  %BassB
  %BassA7 %BsAm

Box Bass "Assolo" |144:
  // assolo
  %BassB
  %BassA7 %BsAm

Box Bass "Tema e coda" |208:
  // tema e coda
  %BassA7 %BsAm
  %BsDm %BsBE %BsAm
  1: 80@ a*1$fermata |

Drums:

Box Drums "Introduzione" |8:
  // introduzione: due battute di pausa, poi il groove
  %BossaA %BossaB

Box Drums "Tema" |16:
  // tema: sul cerchio (hihat) e sul ride per il ponte
  %Drums8 %Drums8
  %Drums8Ride
  %Drums8

Box Drums "Assolo" |144:
  // assolo
  %Drums8Ride
  %Drums8

Box Drums "Tema" |208:
  // tema
  %Drums8

Box Drums "Coda" |240:
  // coda: il rallentando comincia sulla prima battuta
  100@ tempo=126 <<
  8: [kick hihat] hihat hihat [rimshot hihat] [kick hihat] hihat [rimshot hihat] hihat |
  8: [kick hihat] hihat hihat [rimshot hihat] [kick hihat] hihat [rimshot hihat] hihat |
  8: [kick hihat] hihat hihat [rimshot hihat] [kick hihat] hihat [rimshot hihat] hihat |
  8: [kick crash] 7r |
  tempo=70

Traccia Shaker [Drums]:

Box Shaker "Tema" |16:
  // tema: A e A'
  vol=70 16%Shaker

Box Shaker "Ponte" |80:
  // ponte: il volume cresce per tutte e otto le battute
  vol=60 >>
  8%Shaker
  vol=95

Box Shaker "Ultima A del tema" |112:
  // ultima A del tema
  vol=70 8%Shaker

Box Shaker "Assolo di pianoforte" |144:
  // assolo di pianoforte
  vol=90 16%Shaker

Box Shaker "Tema finale e coda" |208:
  // tema finale e coda
  vol=70 12%Shaker

// ================================================================ mixer

Mixer Flauto:
  volume: 92 pan: 0.2 mute: no solo: no reverb: 28

Mixer Nylon:
  volume: 80 pan: -0.4 mute: no solo: no reverb: 12

Mixer Piano:
  volume: 80 pan: 0.2 mute: no solo: no reverb: 20

Mixer Bass:
  volume: 96 pan: 0 mute: no solo: no

Mixer Drums:
  volume: 78 pan: 0 mute: no solo: no reverb: 15

Mixer Shaker:
  volume: 70 pan: 0.5 mute: no solo: no
