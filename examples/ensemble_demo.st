// Strada di casa: una canzone pop-rock completa, musica e parole originali.
//
// Un piccolo giro d'orizzonte di ST-language: strofe e ritornelli con il
// testo cantato, un ponte strumentale, la coda con il rallentando e la
// corona. Cosa c'e' dentro:
//   - strumenti definiti nel file (blocchi "Strumento": voce e archi);
//   - melodie in ottave relative (rel:) e con la tonalita' (key=G): non si
//     scrivono le ottave ne' il diesis del fa; il salto d'ottava e' `*+`;
//   - le melodie sono pattern e il testo si attacca dopo: la strofa 1 e la
//     strofa 2 hanno la stessa musica e parole diverse;
//   - accordi (anche rovesciati, come D/F#) con valori di nota espliciti;
//   - automazioni: il volume e il pan che cambiano nel tempo (vol=, pan=),
//     forcelle sugli accordi degli archi, il rallentando con tempo=;
//   - indicazioni di testo ($"dolce", $"rit.") e la corona ($fermata).
//
// Forma (56 battute): introduzione 4, strofa 8, ritornello 8, strofa 8,
// ritornello 8, ponte 8, ritornello 8, coda 4.

ST: 2.6
Tempo: 112 BPM
Metrica: 4/4
Tonalita: G

Strumento Voce:
  program=53 percussione=no ottava=4 range=55-84 poly=no voicing=monophonic

Strumento Archi:
  program=48 percussione=no ottava=3 range=36-96 poly=si voicing=spread

// ---------------------------------------------------------------- melodia

Pattern %Rest:
  4: 4r |

Pattern %VerseMelody:
  rel: key=G 8: 90@
  r d g g a 2b a |
  b a g 2a g e d |
  e g b 2b a g e |
  2e 2d 2g 2r |
  r b b b a b 2d |
  d c b a 2g r e |
  e g a b 2a g r |
  2a 2f 2d 2r |

Pattern %ChorusMelody:
  rel: key=G 8: 100@
  2e g g 2a 2g |
  b b 2d b a 2g |
  c c b 2a c b a |
  2f 2d 4r |
  2d*+ b g 2b 2a |
  b b 2d d b 2g |
  c c b a 2b a g |
  4g 4r |

Pattern %OutroMelody:
  rel: key=G 8: 70@
  2e g g 2a 2g |
  8r |
  8r |
  8r |

// ---------------------------------------------------------------- armonia

Pattern %IntroChords:
  90@ G'1 | D/F#'1 | Em7'1 | Cmaj7'1 |

Pattern %VerseChords:
  80@ G'1 | D/F#'1 | Em7'1 | Cmaj7'1 | G/B'1 | Am7'1 | Cmaj7'1 | D'1 |

Pattern %ChorusChords:
  95@ Cmaj7'1$accent | G/B'1 | Am7'1 | D'1 | Cmaj7'1$accent | G/B'1 | Am7'2 D7'2 | G'1 |

Pattern %ChorusStrings:
  80@ Cmaj7'1< | G/B'1< | Am7'1< | D'1< | Cmaj7'1< | G/B'1< | Am7'2< D7'2< | G'1 |

Pattern %BridgeChords:
  85@ Em'1 | Em'1 | Cmaj7'1 | Cmaj7'1 | Am7'1 | Am7'1 | D7sus4'2 D7'2 | D7'1 |

Pattern %OutroChords:
  80@ Cmaj7'1 | G/B'1 | Am7'1 | G'1$fermata |

// ---------------------------------------------------------------- chitarra (arpeggi)

Pattern %ArpG:
  8: 78@ g*2 d*3 g*3 b*3 d*4 b*3 g*3 d*3 |

Pattern %ArpDF:
  8: 78@ f#*2 a*2 d*3 f#*3 a*3 f#*3 d*3 a*2 |

Pattern %ArpEm:
  8: 78@ e*2 b*2 e*3 g*3 b*3 g*3 e*3 b*2 |

Pattern %ArpC:
  8: 78@ c*3 g*3 b*3 e*4 b*3 g*3 e*3 g*3 |

Pattern %ArpGB:
  8: 78@ b*2 d*3 g*3 b*3 d*4 b*3 g*3 d*3 |

Pattern %ArpAm:
  8: 78@ a*2 e*3 g*3 c*4 e*4 c*4 g*3 e*3 |

Pattern %ArpD:
  8: 78@ d*3 a*3 c*4 f#*4 a*4 f#*4 c*4 a*3 |

Pattern %GtrIntro:
  %ArpG %ArpDF %ArpEm %ArpC

Pattern %GtrVerse:
  %ArpG %ArpDF %ArpEm %ArpC %ArpGB %ArpAm %ArpC %ArpD

Pattern %GtrChorus:
  %ArpC %ArpGB %ArpAm %ArpD %ArpC %ArpGB %ArpAm %ArpG

Pattern %GtrBridge:
  %ArpEm %ArpEm %ArpC %ArpC %ArpAm %ArpAm %ArpD %ArpD

// ---------------------------------------------------------------- basso

Pattern %BassVerse:
  4: 85@ 2g*1 2d*2 | 2f#*1 2a*1 | 2e*1 2b*1 | 2c*2 2g*1 | 2b*1 2d*2 | 2a*1 2e*2 | 2c*2 2g*1 | 2d*2 2a*1 |

Pattern %BassChorus:
  8: 98@ 4(c*2 c*3) | 4(b*1 b*2) | 4(a*1 a*2) | 4(d*2 d*3) | 4(c*2 c*3) | 4(b*1 b*2) | 2(a*1 a*2) 2(d*2 d*3) | 4(g*1 g*2) |

Pattern %BassBridge:
  88@ e*1'1 | e*1'1 | c*2'1 | c*2'1 | a*1'1 | a*1'1 | d*2'2 d*2'2 | d*2'1 |

// ---------------------------------------------------------------- tromba

Pattern %TrChorus:
  rel: key=G 8: 95@
  8r |
  8r |
  8r |
  4r 2f 2a |
  8r |
  8r |
  8r |
  4r 2b 2d |

Pattern %TrBridge:
  rel: key=G 8: 100@
  r e g 2b 2a g |
  2e 2g 4b |
  r c e 2g 3e |
  2d 2c 4r |
  r a c 2e 2d c |
  2b 2a 4e |
  2g 2a 2b 2d |
  8d |

// ---------------------------------------------------------------- batteria

Pattern %DrumsVerse:
  8: 78@ [kick hihat] 45@ hihat 70@ [snare hihat] 45@ hihat 78@ [kick hihat] 45@ [kick hihat] 70@ [snare hihat] 45@ hihat |

Pattern %DrumsChorus:
  8: 105@ [kick hihat_open] 70@ hihat 100@ [snare hihat] 70@ hihat 105@ [kick hihat] 70@ [kick hihat] 100@ [snare hihat] 70@ hihat |

Pattern %DrumsChorusCrash:
  8: 110@ [kick crash] 70@ hihat 100@ [snare hihat] 70@ hihat 105@ [kick hihat] 70@ [kick hihat] 100@ [snare hihat] 70@ hihat |

Pattern %DrumsFill:
  16: 95@ snare snare snare snare tom1 tom1 tom2 tom2 floor floor floor floor 110@ [kick snare] [kick snare] [kick snare] [kick snare] |

Pattern %DrumsBridge:
  4: 85@ [kick floor] r tom2 tom1 |

Pattern %DrumsVerse8:
  7%DrumsVerse %DrumsFill

Pattern %DrumsChorus8:
  %DrumsChorusCrash 7%DrumsChorus

// ================================================================ tracce

Voce:

Box Voce "Strofa 1" |16:
  // strofa 1
  $"dolce" %VerseMelody "Il so- le scen- de- va sul- la stra- da di ca- sa o- gni pas- so e- ra un ri- tor- no fi- ne- stre ac- ce- se il fu- mo dei cam- pi ma ven- go da mol- to len- ta- no"

Box Voce "Ritornello 1" |48:
  // ritornello 1
  %ChorusMelody "Stra- da di ca- sa por- ta- mi an- co- ra do- ve il cie- lo è a- ran- cio Stra- da di ca- sa se- ra do- po se- ra io sa- rò sem- pre a ca- sa"

Box Voce "Strofa 2" |80:
  // strofa 2: la stessa musica, parole nuove
  %VerseMelody "La por- ta a- per- ta il pro- fu- mo del pa- ne u- na vo- ce dal cor- ti- le chia- ma co- me se il tem- po non fos- se pas- sa- to fi- nal- men- te so- no a ca- sa"

Box Voce "Ritornello 2" |112:
  // ritornello 2
  %ChorusMelody "Stra- da di ca- sa por- ta- mi an- co- ra do- ve il cie- lo è a- ran- cio Stra- da di ca- sa se- ra do- po se- ra io sa- rò sem- pre a ca- sa"

Box Voce "Ritornello finale e coda" |176:
  // ritornello finale e coda
  %ChorusMelody "Stra- da di ca- sa por- ta- mi an- co- ra do- ve il cie- lo è a- ran- cio Stra- da di ca- sa se- ra do- po se- ra io sa- rò sem- pre a ca- sa"
  %OutroMelody "Stra- da di ca- sa"

Piano:

Box Piano "Inizio" |0:
  %IntroChords %VerseChords %ChorusChords
  %VerseChords %ChorusChords

Box Piano "Ponte" |144:
  // ponte
  %BridgeChords

Box Piano "Ritornello finale e coda" |176:
  // ritornello finale e coda, con l'indicazione di testo
  %ChorusChords
  $"rit." %OutroChords

Guitar 1:

Box Guitar 1 "Inizio" |0:
  vol=75 %GtrIntro
  %GtrVerse

Box Guitar 1 "Ritornello 1" |48:
  // nel ritornello la chitarra sale di volume
  vol=95 %GtrChorus
  vol=75 %GtrVerse
  vol=95 %GtrChorus

Box Guitar 1 "Ponte" |144:
  // ponte: gli arpeggi attraversano il campo stereo da sinistra a destra
  pan=-0.8 >>
  %GtrBridge
  pan=0.8
  pan=-0.4
  vol=100 %GtrChorus

Box Guitar 1 "Coda" |208:
  // coda
  vol=80 %ArpC %ArpGB %ArpAm
  8: [g*2 d*3 g*3 b*3 d*4]'1$fermata |

Bass:

Box Bass "Inizio" |8:
  4: 85@ 2e*1 2b*1 | 2c*2 2g*1 |
  %BassVerse %BassChorus %BassVerse %BassChorus
  %BassBridge
  %BassChorus

Box Bass "Coda" |208:
  // coda
  4: 98@ c*2'1 | b*1'1 | a*1'1 | g*1'1$fermata |

Archi:

Box Archi "Strofa 2" |80:
  // entrano alla seconda strofa (introduzione 4 + strofa 8 + ritornello 8)
  %VerseChords
  %ChorusStrings

Box Archi "Ponte" |144:
  // ponte: un crescendo che dura tutte e otto le battute
  vol=45 >>
  %BridgeChords
  vol=100
  %ChorusStrings
  %OutroChords

Trumpet:

Box Trumpet "Ritornello 2" |112:
  // tace fino al secondo ritornello
  %TrChorus
  %TrBridge
  %TrChorus
  4%Rest

Drums:

Box Drums "Introduzione" |8:
  // introduzione: due battute di pausa, poi il groove e il rullo
  %DrumsVerse %DrumsFill
  %DrumsVerse8 %DrumsChorus8
  %DrumsVerse8 %DrumsChorus8

Box Drums "Ponte" |144:
  // ponte: tamburi, e il rullo che porta al ritornello finale
  7%DrumsBridge %DrumsFill
  %DrumsChorus8

Box Drums "Coda" |208:
  // coda: due battute di groove, poi il rallentando
  %DrumsChorusCrash %DrumsChorus
  100@ tempo=112 <<
  8: [kick hihat] hihat [snare hihat] hihat [kick hihat] hihat [snare hihat] hihat |
  [kick crash] 7r |
  tempo=66

// ================================================================ mixer

Mixer Voce:
  volume: 100 pan: 0 mute: no solo: no reverb: 22

Mixer Piano:
  volume: 80 pan: -0.25 mute: no solo: no reverb: 15

Mixer Guitar 1:
  volume: 80 pan: -0.4 mute: no solo: no chorus: 25

Mixer Bass:
  volume: 96 pan: 0 mute: no solo: no

Mixer Archi:
  volume: 72 pan: 0.2 mute: no solo: no reverb: 35

Mixer Trumpet:
  volume: 86 pan: 0.35 mute: no solo: no reverb: 28

Mixer Drums:
  volume: 88 pan: 0 mute: no solo: no reverb: 12
