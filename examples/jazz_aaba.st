// Luci sul Naviglio: un brano jazz nella forma classica AABA (32 battute).
//
// Un quartetto (tromba, pianoforte, chitarra, contrabbasso e batteria) che
// suona un "chorus" dopo l'altro, come in un vero club:
//   introduzione di 4 battute, tema alla tromba, assolo di pianoforte,
//   tema ripreso con la sezione ritmica piu' vivace, e una breve coda.
// Cosa c'e' dentro:
//   - lo swing (swing=66): le crome scritte dritte suonano "terzinate";
//   - la tonalita' (key=F): il si e' bemolle senza scriverlo;
//   - il basso "camminato" (walking bass): quattro note a battuta, sempre
//     in movimento verso l'accordo seguente;
//   - il pianoforte che accompagna con il ritmo "Charleston" e gli accordi
//     a voicing drop-2 (.drop2); la chitarra con i quarti alla Freddie Green;
//   - la batteria con il ride swing, il pedale del charleston sul 2 e sul 4,
//     la "piumata" della cassa nell'ultimo chorus;
//   - le sezioni A e B come pattern: A, A, B, A per tre chorus;
//   - le forcelle di dinamica sul ponte e la corona finale.
//
// Forma: introduzione 4 + tema 32 + assolo 32 + tema 32 + coda 4 = 104 battute.
//   A  Fmaj7 | D7 | Gm7 | C7 | Am7 D7 | Gm7 C7 | Fmaj7 Dm7 | Gm7 C7
//   B  Em7 A7 | Dmaj7 | Dm7 G7 | Cmaj7 | Cm7 F7 | Bbmaj7 | Gm7 C7 | C7

ST: 2.6
Tempo: 132 BPM
Metrica: 4/4
Tonalita: F

// ---------------------------------------------------------------- generale

Pattern %Rest:
  4: 4r |

// ---------------------------------------------------------------- tema (tromba)

Pattern %HeadA1:
  key=F 8: 92@
  r a*4 c*5 f*5 2e*5 c*5 a*4 |
  2f#*4 a*4 d*5 3c*5 r |
  r b*4 d*5 g*5 2f*5 d*5 b*4 |
  3e*5 c*5 4r |
  r c*5 e*5 a*5 2g*5 f#*5 d*5 |
  b*4 d*5 f*5 e*5 2c*5 b*4 g*4 |
  2a*4 c*5 f*5 3d*5 r |
  r g*4 b*4 d*5 2c*5 e*5 g*5 |

Pattern %HeadA3:
  key=F 8: 92@
  r a*4 c*5 f*5 2e*5 c*5 a*4 |
  2f#*4 a*4 d*5 3c*5 r |
  r b*4 d*5 g*5 2f*5 d*5 b*4 |
  3e*5 c*5 4r |
  r c*5 e*5 a*5 2g*5 f#*5 d*5 |
  b*4 d*5 f*5 e*5 2c*5 b*4 g*4 |
  r b*4 d*5 f*5 e*5 c*5 b*4 g*4 |
  6f*4 2r |

Pattern %HeadB:
  key=F 8: 96@
  r g*4 e*5 g*5 2f#*5 e*5 c#*5 |
  2a*5 f#*5 d*5 4a*4 |
  r a*4 d*5 f*5 2g*5 f*5 d*5 |
  2e*5 g*5 e*5 4c*5 |
  r g*4 c*5 eb*5 2d*5 c*5 a*4 |
  2b*4 d*5 f*5 4a*5 |
  r g*4 b*4 d*5 2f*5 e*5 c*5 |
  2g*4 b*4 c*5 3e*5 r |

Pattern %Head:
  %HeadA1 %HeadA1 %HeadB %HeadA3

// ---------------------------------------------------------------- assolo (pianoforte)

Pattern %SoloA1:
  key=F 8: 88@
  r f*4 a*4 c*5 e*5 d*5 c*5 a*4 |
  f#*4 a*4 d*5 c*5 a*4 f#*4 d*4 r |
  g*4 b*4 d*5 f*5 d*5 b*4 a*4 g*4 |
  e*4 g*4 b*4 c*5 b*4 g*4 e*4 c*4 |
  c*5 e*5 a*5 g*5 f#*5 d*5 c*5 a*4 |
  b*4 d*5 g*5 f*5 e*5 c*5 b*4 g*4 |
  a*4 c*5 f*5 e*5 d*5 f*5 a*5 f*5 |
  g*5 f*5 d*5 b*4 g*4 b*4 c*5 e*5 |

Pattern %SoloA2:
  key=F 8: 94@
  2a*5 g*5 f*5 e*5 c*5 2a*4 |
  d*5 c*5 a*4 f#*4 2d*4 2r |
  r b*4 d*5 g*5 2a*5 g*5 f*5 |
  e*5 d*5 c*5 b*4 4g*4 |
  2a*4 c*5 e*5 2f#*5 d*5 c*5 |
  b*4 g*4 d*5 g*5 2f*5 e*5 g*5 |
  f*5 a*5 c*6 a*5 f*5 d*5 f*5 a*5 |
  g*5 f*5 d*5 b*4 2c*5 r r |

Pattern %SoloB:
  key=F 8: 100@
  e*5 g*5 e*5 d*5 c#*5 e*5 a*4 c#*5 |
  d*5 f#*5 a*5 f#*5 d*5 c#*5 a*4 f#*4 |
  d*5 f*5 a*5 g*5 f*5 d*5 a*4 g*4 |
  e*5 g*5 c*6 g*5 e*5 c*5 g*4 e*4 |
  c*5 eb*5 g*5 f*5 e*5 c*5 a*4 f*4 |
  b*4 d*5 f*5 a*5 f*5 d*5 b*4 f*4 |
  g*4 b*4 d*5 f*5 e*5 c*5 b*4 g*4 |
  e*4 g*4 b*4 c*5 2e*5 2r |

Pattern %SoloA3:
  key=F 8: 96@
  r f*5 a*5 c*6 2a*5 f*5 c*5 |
  a*5 f#*5 d*5 f#*5 a*5 d*6 c*6 a*5 |
  g*5 b*5 d*6 c*6 b*5 g*5 f*5 d*5 |
  e*5 g*5 e*5 c*5 e*5 g*5 b*5 g*5 |
  a*5 c*6 e*6 d*6 c*6 a*5 f#*5 d*5 |
  b*4 d*5 g*5 b*5 2a*5 g*5 f*5 |
  r g*5 b*5 d*6 c*6 b*5 g*5 e*5 |
  2f*5 c*5 a*4 4f*4 |

Pattern %Solo:
  %SoloA1 %SoloA2 %SoloB %SoloA3

// ---------------------------------------------------------------- contrabbasso (walking)

Pattern %BF:
  key=F 4: 90@ f*1 a*1 c*2 e*2 |

Pattern %BD7:
  key=F 4: 86@ d*2 c*2 a*1 f#*1 |

Pattern %BGm:
  key=F 4: 90@ g*1 b*1 d*2 f*2 |

Pattern %BC7:
  key=F 4: 86@ c*2 b*1 g*1 g#*1 |

Pattern %BAmD:
  key=F 4: 90@ a*1 c*2 d*2 f#*2 |

Pattern %BGmC:
  key=F 4: 88@ g*1 b*1 c*2 e*2 |

Pattern %BFDm:
  key=F 4: 90@ f*1 a*1 d*2 c*2 |

Pattern %BFend:
  key=F 4: 90@ f*1 c*2 a*1 f*1 |

Pattern %BassA:
  %BF %BD7 %BGm %BC7 %BAmD %BGmC %BFDm %BGmC

Pattern %BassAEnd:
  %BF %BD7 %BGm %BC7 %BAmD %BGmC %BGmC %BFend

Pattern %BassB:
  key=F 4: 90@
  e*2 b*1 a*1 c#*2 |
  d*2 f#*2 a*2 f#*2 |
  d*2 a*1 g*1 d*2 |
  c*2 e*2 g*1 e*2 |
  c*2 g*1 f*1 a*1 |
  b*1 d*2 f*2 d*2 |
  g*1 d*2 c*2 e*2 |
  c*2 b*1 a*1 g*1 |

Pattern %BassChorus:
  %BassA %BassA %BassB %BassAEnd

// ---------------------------------------------------------------- pianoforte (comping)

Pattern %CF:
  8: 74@ 3Fmaj7.drop2! Fmaj7.drop2! 4r |

Pattern %CD7:
  8: 74@ r 2D7.drop2! 2r 3r |

Pattern %CGm:
  8: 74@ 3Gm7.drop2! Gm7.drop2! 4r |

Pattern %CC7:
  8: 74@ r 2C7.drop2! 2r 3r |

Pattern %CAmD:
  8: 74@ 3Am7.drop2! r 2D7.drop2! 2r |

Pattern %CGmC:
  8: 74@ 3Gm7.drop2! r 2C7.drop2! 2r |

Pattern %CFDm:
  8: 74@ 3Fmaj7.drop2! r 2Dm7.drop2! 2r |

Pattern %CFend:
  8: 70@ 3Fmaj7.drop2! Fmaj7.drop2! 4r |

Pattern %CompB:
  8: 76@
  3Em7.drop2! r 2A7.drop2! 2r |
  3Dmaj7.drop2! Dmaj7.drop2! 4r |
  3Dm7.drop2! r 2G7.drop2! 2r |
  r 2Cmaj7.drop2! 2r 3r |
  3Cm7.drop2! r 2F7.drop2! 2r |
  3Bbmaj7.drop2! Bbmaj7.drop2! 4r |
  3Gm7.drop2! r 2C7.drop2! 2r |
  r 2C7.drop2! 2r 3r |

Pattern %CompA:
  %CF %CD7 %CGm %CC7 %CAmD %CGmC %CFDm %CGmC

Pattern %CompAEnd:
  %CF %CD7 %CGm %CC7 %CAmD %CGmC %CGmC %CFend

Pattern %CompChorus:
  %CompA %CompA %CompB %CompAEnd

// ---------------------------------------------------------------- chitarra (quarti alla Freddie Green)

Pattern %GtrA:
  4: 62@
  Fmaj7! Fmaj7! Fmaj7! Fmaj7! |
  D7! D7! D7! D7! |
  Gm7! Gm7! Gm7! Gm7! |
  C7! C7! C7! C7! |
  Am7! Am7! D7! D7! |
  Gm7! Gm7! C7! C7! |
  Fmaj7! Fmaj7! Dm7! Dm7! |
  Gm7! Gm7! C7! C7! |

Pattern %GtrAEnd:
  4: 62@
  Fmaj7! Fmaj7! Fmaj7! Fmaj7! |
  D7! D7! D7! D7! |
  Gm7! Gm7! Gm7! Gm7! |
  C7! C7! C7! C7! |
  Am7! Am7! D7! D7! |
  Gm7! Gm7! C7! C7! |
  Gm7! Gm7! C7! C7! |
  Fmaj7! Fmaj7! Fmaj7! Fmaj7! |

Pattern %GtrB:
  4: 66@
  Em7! Em7! A7! A7! |
  Dmaj7! Dmaj7! Dmaj7! Dmaj7! |
  Dm7! Dm7! G7! G7! |
  Cmaj7! Cmaj7! Cmaj7! Cmaj7! |
  Cm7! Cm7! F7! F7! |
  Bbmaj7! Bbmaj7! Bbmaj7! Bbmaj7! |
  Gm7! Gm7! C7! C7! |
  C7! C7! C7! C7! |

Pattern %GtrChorus:
  %GtrA %GtrA %GtrB %GtrAEnd

// ---------------------------------------------------------------- batteria

Pattern %Ride:
  8: 72@ ride r [ride hihat_pedal] 52@ ride 72@ ride r [ride hihat_pedal] 52@ ride |

Pattern %RideK:
  8: 72@ [ride kick] r [ride hihat_pedal] 52@ ride 72@ [ride kick] r [ride hihat_pedal] 52@ ride |

Pattern %RideFill:
  8: 72@ ride r [ride hihat_pedal] 52@ ride 80@ snare snare 85@ snare 90@ [snare crash] |

Pattern %RideFillTom:
  8: 72@ ride r [ride hihat_pedal] 52@ ride 82@ snare tom1 tom2 90@ [floor crash] |

Pattern %RideBridge:
  8: 78@ ride r [ride hihat_pedal] 56@ ride 78@ ride r [ride hihat_pedal] 56@ ride |

Pattern %Brush:
  8: 60@ [snare hihat_pedal] r r snare 60@ [snare hihat_pedal] r r snare |

Pattern %DrumsA:
  7%Ride %RideFill

Pattern %DrumsAK:
  7%RideK %RideFillTom

Pattern %DrumsB:
  7%RideBridge %RideFillTom

Pattern %DrumsChorus1:
  %DrumsA %DrumsA %DrumsB %DrumsA

Pattern %DrumsChorus2:
  %DrumsA %DrumsA %DrumsB %DrumsA

Pattern %DrumsChorus3:
  %DrumsAK %DrumsAK %DrumsB %DrumsAK

// ================================================================ tracce

Trumpet:

Box Trumpet "Chorus 1" |16:
  // chorus 1: il tema
  swing=66 $"tema" %Head

Box Trumpet "Chorus 3" |272:
  // chorus 3: il tema ripreso, con piu' forza
  swing=66 100@ %Head

Box Trumpet "Coda" |400:
  // coda
  swing=66 100@ key=F 8: 90@
  r g*4 b*4 d*5 2f*5 e*5 c*5 |
  2a*4 c*5 f*5 3d*5 r |
  r g*4 b*4 d*5 2c*5 e*5 c*5 |
  8f*4$fermata |

Piano:

Box Piano "Introduzione" |0:
  // introduzione: una breve frase a mano sola sul giro ii-V
  swing=66 key=F 8: 82@
  r c*5 e*5 a*5 g*5 f#*5 a*5 d*5 |
  c*5 b*4 g*4 b*4 d*5 c*5 e*4 g*4 |
  r c*5 e*5 a*5 g*5 f#*5 a*5 d*5 |
  b*4 d*5 g*5 f*5 2e*5 c*5 e*5 |

Box Piano "Chorus 1" |16:
  // chorus 1: accompagnamento Charleston sotto il tema
  swing=66 key=F 8: 82@ %CompChorus

Box Piano "Chorus 2" |144:
  // chorus 2: l'assolo
  swing=66 key=F 8: 82@ $"assolo" %Solo

Box Piano "Chorus 3" |272:
  // chorus 3: di nuovo il compagnamento
  swing=66 key=F 8: 82@ 100@ %CompChorus

Box Piano "Coda" |400:
  // coda
  swing=66 key=F 8: 100@ 8: 76@ 3Gm7.drop2! r 2C7.drop2! 2r |
  3Am7.drop2! r 2D7.drop2! 2r |
  3Gm7.drop2! r 2C7.drop2! 2r |
  1: Fmaj7.drop2$fermata |

Guitar 1:

Box Guitar 1 "Chorus 2" |144:
  // la chitarra entra con l'assolo di pianoforte
  swing=66 vol=100 %GtrChorus

Box Guitar 1 "Chorus 3" |272:
  // chorus 3: di nuovo in sottofondo
  swing=66 vol=80 %GtrChorus

Box Guitar 1 "Coda" |400:
  // coda
  swing=66 4: 62@ Gm7! Gm7! C7! C7! |
  Am7! Am7! D7! D7! |
  Gm7! Gm7! C7! C7! |
  1: Fmaj7$fermata |

Bass:

Box Bass "Introduzione" |8:
  // introduzione: il basso entra alla terza battuta
  swing=66 %BAmD %BGmC

Box Bass "Tre chorus" |16:
  // tre chorus
  swing=66 3%BassChorus

Box Bass "Coda" |400:
  // coda
  swing=66 %BGmC %BAmD %BGmC
  1: 90@ f*1$fermata |

Drums:

Box Drums "Introduzione" |8:
  // introduzione: due battute di pausa, poi il ride e il rullo di entrata
  swing=66 %Ride %RideFill

Box Drums "Chorus 1 e 2" |16:
  // chorus 1 e 2: ride swing
  swing=66 %DrumsChorus1 %DrumsChorus2

Box Drums "Chorus 3" |272:
  // chorus 3: la cassa "piumata" e piu' energia
  swing=66 %DrumsChorus3

Box Drums "Coda" |400:
  // coda
  swing=66 %Ride %Ride %RideFill 8: [kick crash] 7r |

// ================================================================ mixer

Mixer Trumpet:
  volume: 92 pan: 0.3 mute: no solo: no reverb: 30

Mixer Piano:
  volume: 86 pan: -0.3 mute: no solo: no reverb: 18

Mixer Guitar 1:
  volume: 72 pan: -0.55 mute: no solo: no reverb: 10

Mixer Bass:
  volume: 100 pan: 0.1 mute: no solo: no

Mixer Drums:
  volume: 84 pan: 0 mute: no solo: no reverb: 15
