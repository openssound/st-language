// Sinfonia dell'alba: un movimento sinfonico originale per orchestra.
//
// Archi, flauto, oboe, corni, trombe, timpani e arpa, in 40 battute (4/4).
// La forma ricorda quella di un primo movimento sinfonico in miniatura:
//   introduzione lenta  4 battute   Adagio, Re minore (tempo 56)
//   tema A              8           Allegro, Re minore: gli archi
//   tema B              8           Fa maggiore: oboe e flauto, con l'arpa
//   sviluppo            8           il motivo del tema A in sequenza, con
//                                   i corni, le trombe e un crescendo
//   ripresa             8           il tema A, ora con tutta l'orchestra
//   coda                4           il rallentando e la cadenza in Re
//                                   maggiore, con la corona
// Cosa c'e' dentro:
//   - strumenti definiti nel file (blocchi "Strumento"): ognuno ha il suo
//     programma, il registro e se suona note o accordi;
//   - i temi sono pattern, riusati da piu' strumenti: lo stesso %TemaA lo
//     suonano violini (introduzione e ripresa), flauto, oboe e trombe, e
//     ognuno lo porta nella propria ottava (ottave relative, rel:);
//   - i cambi di tempo con tempo=: Adagio, Allegro, il tema B piu' disteso,
//     lo sviluppo che spinge e il rallentando finale (tempo=126 << ... 70);
//   - le dinamiche con la velocity (50@ = piano, 110@ = fortissimo) e le
//     forcelle < sugli accordi e sulle note lunghe;
//   - la corona ($fermata) sull'ultimo accordo.

ST: 2.6
Tempo: 56 BPM
Metrica: 4/4
Tonalita: Dm

Strumento Violini1:
  program=40 percussione=no ottava=5 range=55-100 poly=no voicing=monophonic

Strumento Violini2:
  program=40 percussione=no ottava=4 range=55-100 poly=si voicing=spread

Strumento Viole:
  program=41 percussione=no ottava=3 range=48-91 poly=si voicing=spread

Strumento Violoncelli:
  program=42 percussione=no ottava=3 range=36-76 poly=no voicing=monophonic

Strumento Contrabbassi:
  program=43 percussione=no ottava=2 range=28-55 poly=no voicing=monophonic

Strumento Flauto:
  program=73 percussione=no ottava=5 range=60-96 poly=no voicing=monophonic

Strumento Oboe:
  program=68 percussione=no ottava=5 range=58-91 poly=no voicing=monophonic

Strumento Corni:
  program=60 percussione=no ottava=3 range=41-77 poly=si voicing=spread

Strumento Trombe:
  program=56 percussione=no ottava=4 range=55-82 poly=no voicing=monophonic

Strumento Timpani:
  program=47 percussione=no ottava=3 range=36-60 poly=no voicing=monophonic

Strumento Arpa:
  program=46 percussione=no ottava=4 range=24-103 poly=si voicing=spread

// ---------------------------------------------------------------- temi

Pattern %TemaA:
  rel: key=Dm 8:
  d f a 3d 2c |
  b a g f 2e 2d |
  e g a 3d 2c |
  b a g a 2b 2a |
  a 3d f 3e |
  2d c b a 2g f |
  g a b d 2c b a |
  a 7d |

Pattern %TemaB:
  rel: key=Dm 8:
  4a*4 2g 2f |
  2e 2g 2c 2a |
  4b 2a 2g |
  2b 2a 2g 2e |
  2f 2a 2c 2f |
  2d 2f 2b 2a |
  2g 2b 2g 2e |
  8f |

Pattern %Sviluppo1:
  key=Dm 8:
  g*5 b*5 d*6 3g*6 2f*6 |
  c*5 e*5 g*5 3c*6 2b*5 |
  f*5 a*5 c*6 3f*6 2e*6 |
  b*5 d*6 f*6 3b*6 2a*6 |
  g*5 a*5 b*5 d*6 2g*6 2f*6 |
  e*6 g*6 a*6 c#*6 2e*6 2a*5 |
  d*6 f*6 a*6 2f*6 e*6 2d*6 |
  2e*6 2g*6 4c#*6 |

Pattern %CodaVl1:
  key=Dm 8:
  2g*6 2f*6 2d*6 2b*5 |
  2e*6 2g*6 4a*6 |
  3d*6 f#*6 4a*6 |
  8d*6$fermata |

Pattern %IntroVl1:
  key=Dm 4:
  4a*5 | 4b*5 | 4d*6 | 4e*6 |

// ---------------------------------------------------------------- armonia

Pattern %AccIntro:
  Dm'1 | Bb'1 | Gm'1 | A7'1 |

Pattern %AccA:
  Dm'1 | Gm'2 A7'2 | C'2 F'2 | Gm'2 A7'2 | Dm'1 | Bb'2 Gm'2 | Gm'2 A7'2 | Dm'1 |

Pattern %AccB:
  F'1 | C'2 F'2 | Bb'1 | Gm'2 C7'2 | F'1 | Dm'2 Bb'2 | Gm'2 C7'2 | F'1 |

Pattern %AccSviluppo:
  Gm'1< | C7'1< | F'1< | Bb'1< | Gm'1< | A7'1< | Dm'1< | A7'1 |

Pattern %AccCoda:
  Gm'1 | A7'1 | D'1 | D'1$fermata |

// ---------------------------------------------------------------- bassi e violoncelli

Pattern %BassoA:
  key=Dm 4:
  2d*2 2a*1 | 2g*1 2a*1 | 2c*2 2f*1 | 2g*1 2a*1 | 2d*2 2a*1 | 2b*1 2g*1 | 2g*1 2a*1 | 4d*2 |

Pattern %CelloA:
  key=Dm 4:
  2d*3 2a*2 | 2g*2 2a*2 | 2c*3 2f*2 | 2g*2 2a*2 | 2d*3 2a*2 | 2b*2 2g*2 | 2g*2 2a*2 | 4d*3 |

Pattern %BassoB:
  key=Dm 4:
  4f*1 | 2c*2 2f*1 | 4b*1 | 2g*1 2c*2 | 4f*1 | 2d*2 2b*1 | 2g*1 2c*2 | 4f*1 |

Pattern %CelloB:
  key=Dm 4:
  4f*2 | 2c*3 2f*2 | 4b*2 | 2g*2 2c*3 | 4f*2 | 2d*3 2b*2 | 2g*2 2c*3 | 4f*2 |

Pattern %BassoSviluppo:
  key=Dm 4:
  4g*1< | 4c*2< | 4f*1< | 4b*1< | 4g*1< | 4a*1< | 4d*2< | 4a*1 |

Pattern %CelloSviluppo:
  key=Dm 4:
  4g*2< | 4c*3< | 4f*2< | 4b*2< | 4g*2< | 4a*2< | 4d*3< | 4a*2 |

Pattern %BassoCoda:
  key=Dm 4:
  4g*1 | 4a*1 | 4d*2 | 4d*2$fermata |

Pattern %CelloCoda:
  key=Dm 4:
  4g*2 | 4a*2 | 4d*3 | 4d*3$fermata |

// ---------------------------------------------------------------- trombe

Pattern %FanfaraTrombe:
  key=Dm 8:
  2g*4 2b*4 4d*5 |
  2a*4 2c#*5 4e*5 |
  2d*5 2f*5 4a*5 |
  2a*4 2e*5 4a*5 |

// ---------------------------------------------------------------- arpa

Pattern %ArpaB:
  key=Dm 8:
  f*3 a*3 c*4 f*4 a*4 f*4 c*4 a*3 |
  c*3 e*3 g*3 c*4 f*3 a*3 c*4 f*4 |
  b*2 d*3 f*3 b*3 d*4 b*3 f*3 d*3 |
  g*2 b*2 d*3 g*3 c*3 e*3 g*3 b*3 |
  f*3 a*3 c*4 f*4 a*4 f*4 c*4 a*3 |
  d*3 f*3 a*3 d*4 b*2 d*3 f*3 b*3 |
  g*2 b*2 d*3 g*3 c*3 e*3 g*3 b*3 |
  2f*3 2a*3 4c*4 |

Pattern %ArpaCoda:
  key=Dm 8:
  g*2 b*2 d*3 g*3 b*3 g*3 d*3 b*2 |
  a*2 c#*3 e*3 g*3 a*3 g*3 e*3 c#*3 |
  d*3 f#*3 a*3 d*4 f#*4 d*4 a*3 f#*3 |
  D'1$fermata |

// ---------------------------------------------------------------- timpani

Pattern %TimpIntro:
  key=Dm 4:
  d*3 d*3 d*3 d*3 | d*3 d*3 d*3 d*3 | g*2 g*2 g*2 g*2 | a*2 a*2 a*2 a*2 |

Pattern %TimpA:
  key=Dm 4:
  2d*3 2a*2 | 2g*2 2a*2 | 2c*3 2f*2 | 2g*2 2a*2 | 2d*3 2a*2 | 2b*2 2g*2 | 2g*2 2a*2 | 4d*3 |

Pattern %TimpB:
  key=Dm 4:
  4f*2 | 2c*3 2f*2 | 4b*2 | 2g*2 2c*3 | 4f*2 | 2d*3 2b*2 | 2g*2 2c*3 | 4f*2 |

Pattern %TimpSviluppo:
  key=Dm 4:
  g*2 g*2 g*2 g*2 | c*3 c*3 c*3 c*3 | f*2 f*2 f*2 f*2 | b*2 b*2 b*2 b*2 |
  g*2 g*2 g*2 g*2 | a*2 a*2 a*2 a*2 | d*3 d*3 d*3 d*3 | a*2 a*2 a*2 a*2 |

// ================================================================ tracce

Violini1:

Box Violini1 "Introduzione" |0:
  50@ %IntroVl1

Box Violini1 "Tema A" |16:
  $"con slancio"
  85@ %TemaA

Box Violini1 "Sviluppo" |80:
  80@ %Sviluppo1

Box Violini1 "Ripresa" |112:
  105@ %TemaA

Box Violini1 "Coda" |144:
  100@ %CodaVl1

Violini2:

Box Violini2 "Tema B" |48:
  $"dolce"
  55@ %AccB

Box Violini2 "Sviluppo" |80:
  70@ %AccSviluppo

Box Violini2 "Ripresa" |112:
  85@ %AccA
  90@ %AccCoda

Viole:

Box Viole "Introduzione" |0:
  45@ %AccIntro
  65@ %AccA
  55@ %AccB
  65@ %AccSviluppo
  80@ %AccA

Box Viole "Coda" |144:
  85@ %AccCoda

Violoncelli:

Box Violoncelli "Introduzione" |0:
  4: 45@ 4d*3 | 4b*2 | 4g*2 | 4a*2 |
  80@ %CelloA
  60@ %CelloB
  75@ %CelloSviluppo
  95@ %CelloA
  90@ %CelloCoda

Contrabbassi:

Box Contrabbassi "Introduzione" |0:
  4: 40@ 4d*2 | 4b*1 | 4g*1 | 4a*1 |
  80@ %BassoA
  60@ %BassoB
  75@ %BassoSviluppo
  95@ %BassoA
  90@ %BassoCoda

Flauto:

Box Flauto "Tema B" |48:
  $"cantabile"
  65@ %TemaB

Box Flauto "Ripresa" |112:
  95@ %TemaA

Oboe:

Box Oboe "Tema B" |48:
  $"espressivo"
  80@ %TemaB

Box Oboe "Ripresa" |112:
  95@ %TemaA

Corni:

Box Corni "Introduzione" |0:
  40@ %AccIntro

Box Corni "Sviluppo" |80:
  55@ %AccSviluppo
  95@ %AccA
  95@ %AccCoda

Trombe:

Box Trombe "Sviluppo" |96:
  // le trombe entrano nelle ultime quattro battute dello sviluppo
  90@ %FanfaraTrombe

Box Trombe "Ripresa" |112:
  // ripresa: il tema A all'ottava sotto i violini
  105@ %TemaA

Timpani:

Box Timpani "Introduzione" |0:
  // Adagio: il rullo sommesso
  35@ %TimpIntro
  // Allegro
  tempo=120
  85@ %TimpA
  // tema B, piu' disteso
  tempo=104
  50@ %TimpB
  // sviluppo: il tempo spinge e il crescendo cresce
  tempo=116
  60@ %TimpSviluppo
  // ripresa
  tempo=126
  95@ %TimpA

Box Timpani "Coda" |144:
  // coda: il rallentando
  100@ tempo=126 <<
  4: 4g*2 | 4a*2 | 4d*3 |
  4: 4d*3$fermata |
  tempo=70

Arpa:

Box Arpa "Tema B" |48:
  60@ %ArpaB

Box Arpa "Coda" |144:
  75@ %ArpaCoda

// ================================================================ mixer

Mixer Violini1:
  volume: 92 pan: -0.5 mute: no solo: no reverb: 35

Mixer Violini2:
  volume: 82 pan: -0.25 mute: no solo: no reverb: 35

Mixer Viole:
  volume: 80 pan: 0.15 mute: no solo: no reverb: 35

Mixer Violoncelli:
  volume: 84 pan: 0.4 mute: no solo: no reverb: 30

Mixer Contrabbassi:
  volume: 80 pan: 0.65 mute: no solo: no reverb: 25

Mixer Flauto:
  volume: 80 pan: -0.15 mute: no solo: no reverb: 40

Mixer Oboe:
  volume: 82 pan: 0.1 mute: no solo: no reverb: 40

Mixer Corni:
  volume: 78 pan: 0.3 mute: no solo: no reverb: 40

Mixer Trombe:
  volume: 80 pan: -0.3 mute: no solo: no reverb: 40

Mixer Timpani:
  volume: 86 pan: 0 mute: no solo: no reverb: 45

Mixer Arpa:
  volume: 76 pan: -0.6 mute: no solo: no reverb: 40
