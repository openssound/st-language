// Alba sul lago: un brano ambient in Re, 48 battute lente, tutto sulle automazioni.
//
// Un tappeto di sintetizzatore, pianoforte, glockenspiel con il suo eco,
// flauto, archi e un basso lunghissimo. Quasi nessun ritmo: il brano si muove
// perche' i parametri cambiano nel tempo. Cosa c'e' dentro:
//   - le rampe `>>` con la curva: `vol=0 >>exp` (dissolvenza in entrata
//     naturale), `>>log` (dissolvenza in uscita); le rampe di nomi diversi
//     (vol, cho, rev, cc74) si sovrappongono;
//   - il pan che attraversa il campo stereo da sinistra a destra nel ponte;
//   - il filtro (cc74=) che si apre lentamente;
//   - tempo=N con `>>` (accelerando) e `<<` (rallentando) senza batteria;
//   - l'accordatura che scivola (tune=, in cent) negli archi del ponte:
//     l'effetto del nastro che rallenta;
//   - il ritardo ("eco") ottenuto con una seconda traccia dello stesso
//     strumento, spostata nel tempo di 300 ms (shift=);
//   - le forcelle `<` sugli accordi e le legature `( )` e di valore `~` sul
//     pianoforte e sul flauto; una piccola scivolata (bend=) sul flauto;
//   - le ottave relative (rel:) e la tonalita' (key=D) nelle melodie;
//   - strumenti definiti nel file e la corona sull'ultimo accordo.
//
// Forma (12 sezioni da 4 battute, A e B sono due giri di accordi):
//   1 A  2 A  3 A  4 B  5 A  6 B  7 B  8 B  9 A  10 B  11 A  12 finale
//   A  Dmaj7 | Bm7 | Gmaj7 | Asus4          B  Gmaj7 | Em7 | Bm7 | A

ST: 2.6
Tempo: 60 BPM
Metrica: 4/4
Tonalita: D

Strumento Pad:
  program=89 percussione=no ottava=3 range=36-96 poly=si voicing=spread

Strumento Glock:
  program=9 percussione=no ottava=6 range=72-108 poly=si voicing=spread

Strumento Flauto:
  program=73 percussione=no ottava=5 range=72-100 poly=no voicing=monophonic

Strumento Archi:
  program=48 percussione=no ottava=3 range=36-96 poly=si voicing=spread

Pattern %Rest:
  4: 4r |

// ---------------------------------------------------------------- tappeto (pad)

Pattern %PadA:
  4: 56@ Dmaj7'1 | Bm7'1 | Gmaj7'1 | Asus4'1 |

Pattern %PadB:
  4: 56@ Gmaj7'1 | Em7'1 | Bm7'1 | A'1 |

// senza velocity: dentro i tratti con tempo= la velocity non si puo' cambiare
Pattern %PadAq:
  4: Dmaj7'1 | Bm7'1 | Gmaj7'1 | Asus4'1 |

Pattern %PadBq:
  4: Gmaj7'1 | Em7'1 | Bm7'1 | A'1 |

Pattern %PadEndq:
  4: Dmaj7'1 | Bm7'1 | Gmaj7'1 | Dmaj7'1$fermata |

// ---------------------------------------------------------------- pianoforte (arpeggi)

Pattern %PnA:
  key=D 8: 66@
  (d*4 a*4 c*5 f*5) c*5 a*4 f*4 a*4 |
  b*3 f*4 a*4 d*5 a*4 f*4 d*4 f*4 |
  g*3 d*4 f*4 b*4 f*4 d*4 b*3 d*4 |
  a*3 e*4 a*4 2d*5~ d*5 e*4 d*4 |

Pattern %PnB:
  key=D 8: 66@
  g*3 d*4 f*4 b*4 f*4 d*4 b*3 d*4 |
  (e*3 b*3 d*4 g*4) d*4 b*3 g*3 b*3 |
  b*3 f*4 a*4 d*5 a*4 f*4 d*4 f*4 |
  a*3 e*4 a*4 c*5 a*4 e*4 c*4 e*4 |

Pattern %PnEnd:
  key=D 8: 62@
  d*4 a*4 c*5 f*5 c*5 a*4 f*4 a*4 |
  b*3 f*4 a*4 d*5 a*4 f*4 d*4 f*4 |
  g*3 d*4 f*4 b*4 f*4 d*4 b*3 d*4 |
  1: [d*4 a*4 c*5 f*5]$fermata |

// ---------------------------------------------------------------- glockenspiel

Pattern %BellA:
  key=D 4: 70@
  f*6 r a*6 r |
  r r d*7 r |
  b*6 r r a*6 |
  2e*6 2r |

Pattern %BellB:
  key=D 4: 70@
  g*6 r b*6 r |
  r r e*6 r |
  d*7 r r b*6 |
  2a*6 2r |

Pattern %BellEnd:
  key=D 4: 66@
  d*6 r a*6 r |
  r r d*7 r |
  4r |
  1: d*6$fermata |

// ---------------------------------------------------------------- flauto

Pattern %FlP1:
  rel: key=D 4: 76@
  2a*5 f a |
  2d b a |
  2g f d |
  e f 2e |
  2g b a |
  2g e g |
  2d f d |
  4d |

Pattern %FlP2:
  rel: key=D 4: 80@
  (2a*5 f) a |
  2d b~ b |
  (2g f) d |
  e f 2e |
  2g (b a) |
  2g e g |
  2d f d |
  bend=0 >> 4d bend=1 bend=0 |

Pattern %FlP3:
  rel: key=D 4: 84@
  2a*6 f a |
  2d b a |
  2g f d |
  e f 2e |
  2g b a |
  2g e g |
  2d f d |
  4d |

// ---------------------------------------------------------------- archi e basso

Pattern %ArA:
  4: 64@ Dmaj7'1< | Bm7'1< | Gmaj7'1< | Asus4'1 |

Pattern %ArB:
  4: 64@ Gmaj7'1< | Em7'1< | Bm7'1< | A'1 |

Pattern %ArEnd:
  4: 60@ Dmaj7'1 | Bm7'1 | Gmaj7'1 | Dmaj7'1$fermata |

Pattern %BsA:
  key=D 4: 80@ d*2'1 | b*1'1 | g*1'1 | a*1'1 |

Pattern %BsB:
  key=D 4: 80@ g*1'1 | e*2'1 | b*1'1 | a*1'1 |

Pattern %BsEnd:
  key=D 4: 76@ d*2'1 | b*1'1 | g*1'1 | d*2'1$fermata |

// ================================================================ tracce

Pad:
  // le rampe di chorus, riverbero e filtro durano le prime sei sezioni
  cho=20 >>
  rev=40 >>
  cc74=25 >>
  // sezione 1: dissolvenza in entrata, con la curva "exp"
  vol=0 >>exp
  %PadA
  vol=85
  // sezioni 2-6
  %PadA %PadA %PadB %PadA %PadB
  cho=90
  rev=90
  cc74=110
  // sezioni 7-8, il ponte: il pan va da sinistra a destra e il tempo accelera
  pan=-0.9 >>
  tempo=60 >>
  %PadBq %PadBq
  pan=0.9
  tempo=84
  pan=0
  // sezioni 9-10
  %PadA %PadB
  // sezioni 11-12: rallentando e dissolvenza in uscita (curva "log")
  tempo=84 <<
  vol=85 >>log
  %PadAq %PadEndq
  vol=10
  tempo=50

Piano:

Box Piano "Inizio" |16:
  %PnA %PnA %PnB %PnA %PnB

Box Piano "Ponte" |96:
  // ponte
  %PnB %PnB
  %PnA %PnB %PnA
  %PnEnd

Traccia Glockenspiel [Glock]:

Box Glockenspiel "Inizio" |0:
  pan=-0.6
  4%Rest
  %BellA %BellA %BellB

Box Glockenspiel "Seconda parte" |128:
  // il glockenspiel tace nel mezzo del brano
  %BellA %BellB %BellA
  %BellEnd

Traccia Eco [Glock]:

Box Eco "Eco" |0:
  // la stessa traccia, 300 ms dopo, piu' piano e dall'altra parte
  pan=0.7
  shift=300
  vol=45
  4%Rest
  %BellA %BellA %BellB
  16%Rest
  %BellA %BellB %BellA
  %BellEnd

Flauto:

Box Flauto "Prima parte" |32:
  // le prime due sezioni e le ultime due sono senza flauto
  $"dolce" %FlP1
  %FlP2
  8%Rest

Box Flauto "Di nuovo" |128:
  // di nuovo, un'ottava sopra, quando il tempo e' piu' veloce
  %FlP3
  8%Rest

Archi:

Box Archi "Sezione 5" |64:
  // sezione 5: crescendo di volume
  vol=40 >>
  %ArA
  vol=90
  %ArB

Box Archi "Ponte" |96:
  // ponte: l'accordatura scende di 40 cent, come un nastro che rallenta
  tune=0 >>
  %ArB %ArB
  tune=-40
  tune=0
  8%Rest
  %ArA
  %ArEnd

Bass:

Box Bass "Inizio" |32:
  %BsA %BsB %BsA %BsB
  %BsB %BsB
  %BsA %BsB %BsA
  %BsEnd

// ================================================================ mixer

Mixer Pad:
  volume: 80 pan: 0 mute: no solo: no reverb: 40 chorus: 20

Mixer Piano:
  volume: 76 pan: -0.2 mute: no solo: no reverb: 35

Mixer Glockenspiel:
  volume: 64 pan: -0.6 mute: no solo: no reverb: 45

Mixer Eco:
  volume: 52 pan: 0.7 mute: no solo: no reverb: 55

Mixer Flauto:
  volume: 86 pan: 0.2 mute: no solo: no reverb: 40

Mixer Archi:
  volume: 70 pan: 0 mute: no solo: no reverb: 50

Mixer Bass:
  volume: 88 pan: 0 mute: no solo: no
