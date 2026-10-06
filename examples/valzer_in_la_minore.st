// Il valzer della nebbia: un valzer in La minore, in 48 battute (tre quarti).
//
// Violino, fisarmonica, chitarra, basso e percussioni. Forma:
//   introduzione 4 + A (ripetuta, 16) + B in Do maggiore (ripetuta, 16)
//   + A (8) + coda con il rallentando (4).
// Cosa c'e' dentro:
//   - metrica in 3/4 e griglia di crome (8:), con le pause che scandiscono
//     il "pam-pa-pa" del valzer;
//   - i ritornelli con le caselle: `|:  ...  |1.  ...  :|  |2.  ...  ||` sulle
//     due parti del brano (la seconda volta cambia la battuta finale);
//   - le voci `{ a ; b }` della fisarmonica: arpeggio sopra, basso tenuto sotto;
//   - gli abbellimenti $tr (trillo), $mordent, l'accento e la corona;
//   - le ottave relative (rel:) nella seconda parte del violino: le note
//     vanno vicino alla precedente e il salto d'ottava e' `*+` / `*-`;
//   - le automazioni: il riverbero che aumenta nella coda (rev=), il volume
//     del ponte che cresce (vol=), il rallentando con tempo=;
//   - strumenti definiti nel file (violino, fisarmonica).
//   A    Am | E7 | Am | Dm | Am | Dm | E7 | (1) E7  (2) Am
//   B    C | G7 | C | F | Dm | Am | Dm G7 | (1) G7  (2) E7

ST: 2.6
Tempo: 144 BPM
Metrica: 3/4
Tonalita: Am

Strumento Violino:
  program=40 percussione=no ottava=5 range=55-100 poly=no voicing=monophonic

Strumento Fisarmonica:
  program=21 percussione=no ottava=4 range=48-84 poly=si voicing=spread

Pattern %Rest:
  4: 3r |

// ---------------------------------------------------------------- violino

Pattern %MelA:
  key=Am 8: 88@
  2a*5 c*6 e*6 2c*6 |
  2b*5 g#*5 b*5 2e*6 |
  a*5 c*6 e*6 a*6 2e*6 |
  2f*6 d*6 a*5 2d*6 |
  c*6 e*6 a*6 2g*6 e*6 |
  f*6 e*6 d*6 c*6 2a*5 |
  g#*5 b*5 d*6 b*5 2g#*5 |

Pattern %MelAend1:
  key=Am 8: 88@ b*5 g#*5 e*5 3b*5 |

Pattern %MelAend2:
  key=Am 8: 88@ a*5 c*6 e*6 3a*5 |

Pattern %MelB:
  rel: key=Am 8: 80@
  e g c 2b g |
  2d*+ b g 2f |
  e g c e 2c |
  2a f c*+ 2a |
  d f a 2g f |
  e c a 2e c |
  f a d g*- b d |

Pattern %MelBend1:
  key=Am 8: 80@ b*5 d*6 g*6 3f*6 |

Pattern %MelBend2:
  key=Am 8: 80@ 2b*5 g#*5 3e*5 |

// ---------------------------------------------------------------- fisarmonica

Pattern %PadA:
  4: 60@
  Am'2. |
  E7'2. |
  Am'2. |
  Dm'2. |
  Am'2. |
  Dm'2. |
  E7'2. |

Pattern %PadAend1:
  4: 60@ E7'2. |

Pattern %PadAend2:
  4: 60@ Am'2. |

Pattern %ArpB:
  key=Am 8: 66@
  { c*5 e*5 g*5 e*5 g*5 e*5 ; c*3'2. } |
  { d*5 g*5 b*5 g*5 f*5 d*5 ; g*2'2. } |
  { c*5 e*5 g*5 e*5 g*5 e*5 ; c*3'2. } |
  { c*5 f*5 a*5 f*5 a*5 f*5 ; f*2'2. } |
  { d*5 f*5 a*5 f*5 a*5 f*5 ; d*3'2. } |
  { c*5 e*5 a*5 e*5 a*5 e*5 ; a*2'2. } |
  { d*5 f*5 a*5 ; d*3'4. } { d*5 g*5 b*5 ; g*2'4. } |

Pattern %ArpBend1:
  key=Am 8: 66@ { d*5 g*5 b*5 g*5 f*5 d*5 ; g*2'2. } |

Pattern %ArpBend2:
  key=Am 8: 66@ { b*4 e*5 g#*5 e*5 g#*5 e*5 ; e*3'2. } |

// ---------------------------------------------------------------- chitarra (pam-pa-pa)

Pattern %GtA:
  4: 70@
  r Am! Am! |
  r E7! E7! |
  r Am! Am! |
  r Dm! Dm! |
  r Am! Am! |
  r Dm! Dm! |
  r E7! E7! |

Pattern %GtAend1:
  4: 70@ r E7! E7! |

Pattern %GtAend2:
  4: 70@ r Am! Am! |

Pattern %GtB:
  4: 68@
  r C! C! |
  r G7! G7! |
  r C! C! |
  r F! F! |
  r Dm! Dm! |
  r Am! Am! |
  r Dm! G7! |

Pattern %GtBend1:
  4: 68@ r G7! G7! |

Pattern %GtBend2:
  4: 68@ r E7! E7! |

// ---------------------------------------------------------------- basso e percussioni

Pattern %BsA:
  4: 84@
  a*1 r e*2 |
  e*2 r b*1 |
  a*1 r e*2 |
  d*2 r a*1 |
  a*1 r e*2 |
  d*2 r a*1 |
  e*2 r b*1 |

Pattern %BsAend1:
  4: 84@ e*2 r b*1 |

Pattern %BsAend2:
  4: 84@ a*1 r e*2 |

Pattern %BsB:
  4: 84@
  c*2 r g*1 |
  g*1 r d*2 |
  c*2 r g*1 |
  f*1 r c*2 |
  d*2 r a*1 |
  a*1 r e*2 |
  d*2 r g*1 |

Pattern %BsBend1:
  4: 84@ g*1 r d*2 |

Pattern %BsBend2:
  4: 84@ e*2 r b*1 |

Pattern %Perc:
  4: 80@ kick 55@ tambourine tambourine |

// ================================================================ tracce

Violino:

Box Violino "Inizio" |0:
  pan=0.2

Box Violino "Prima parte" |12:
  // prima parte, con il ritornello e le due caselle
  $"con grazia"
  |: %MelA
  |1. %MelAend1 :|
  |2. %MelAend2 ||

Box Violino "Seconda parte" |60:
  // seconda parte: ottave relative
  vol=100
  |: %MelB
  |1. %MelBend1 :|
  |2. %MelBend2 ||

Box Violino "Ultima volta" |108:
  // ultima volta, con il mordente sulla prima nota e il trillo sul finale
  vol=110
  %MelA
  8: 88@ a*5$mordent c*6 e*6 3a*5$tr |

Box Violino "Coda" |132:
  // coda: il riverbero aumenta mentre il valzer rallenta
  8: 88@ rev=30 >>
  8: 80@ f*6 e*6 d*6 c*6 2a*5 |
  g#*5 b*5 d*6 b*5 2g#*5 |
  a*5 c*6 e*6 3a*5 |
  rev=100
  4: 3a*5$fermata |

Fisarmonica:

Box Fisarmonica "Introduzione" |0:
  // introduzione: la fisarmonica sola
  4: 66@ Am'2. | E7'2. | Am'2. | E7'2. |

Box Fisarmonica "Prima parte" |12:
  // prima parte: accordi tenuti
  4: 66@ |: %PadA
  |1. %PadAend1 :|
  |2. %PadAend2 ||

Box Fisarmonica "Seconda parte" |60:
  // seconda parte: arpeggio e basso tenuto, in due voci
  4: 66@ |: %ArpB
  |1. %ArpBend1 :|
  |2. %ArpBend2 ||

Box Fisarmonica "Ultima volta e coda" |108:
  // ultima volta e coda
  4: 66@ %PadA %PadAend2
  4: 56@ Dm'2. | E7'2. | Am'2. | Am'2.$fermata |

Guitar 1:

Box Guitar 1 "Introduzione" |12:
  // introduzione
  pan=-0.4
  |: %GtA
  |1. %GtAend1 :|
  |2. %GtAend2 ||
  |: %GtB
  |1. %GtBend1 :|
  |2. %GtBend2 ||
  %GtA %GtAend2
  4: 60@ r Dm! Dm! |
  r E7! E7! |
  r Am! Am! |
  4: Am'2.$fermata |

Bass:

Box Bass "Inizio" |0:
  4: 80@ a*1 r e*2 | e*2 r b*1 | a*1 r e*2 | e*2 r b*1 |
  |: %BsA
  |1. %BsAend1 :|
  |2. %BsAend2 ||
  |: %BsB
  |1. %BsBend1 :|
  |2. %BsBend2 ||
  %BsA %BsAend2
  4: 70@ d*2 r a*1 | e*2 r b*1 | a*1 r e*2 |
  4: a*1'2.$fermata |

Traccia Percussioni [Drums]:

Box Percussioni "Introduzione" |12:
  // introduzione: soltanto un colpo ogni battuta
  vol=80
  |: 7%Perc
  |1. %Perc :|
  |2. %Perc ||
  vol=75 >>
  |: 7%Perc
  |1. %Perc :|
  |2. %Perc ||
  vol=100
  8%Perc

Box Percussioni "Coda" |132:
  // coda: il rallentando
  100@ tempo=144 <<
  4: [kick tambourine] tambourine tambourine |
  4: [kick tambourine] tambourine tambourine |
  4: [kick tambourine] tambourine tambourine |
  4: [kick crash] 2r |
  tempo=84

// ================================================================ mixer

Mixer Violino:
  volume: 96 pan: 0.2 mute: no solo: no reverb: 30

Mixer Fisarmonica:
  volume: 78 pan: 0.4 mute: no solo: no reverb: 22

Mixer Guitar 1:
  volume: 72 pan: -0.4 mute: no solo: no

Mixer Bass:
  volume: 90 pan: -0.1 mute: no solo: no

Mixer Percussioni:
  volume: 70 pan: 0.1 mute: no solo: no reverb: 10
