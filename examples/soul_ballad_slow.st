// Resta ancora: una ballata soul lenta in Mi bemolle, musica e parole originali.
//
// Voce, pianoforte elettrico, archi, chitarra, basso e batteria: 56 battute
// con la forma classica strofa - ritornello - strofa - ritornello - ponte -
// ritornello - coda. Cosa c'e' dentro:
//   - il testo cantato (virgolette) agganciato alle melodie, che sono pattern:
//     una sillaba per nota, il trattino "-" dice che la parola continua;
//   - la tonalita' (key=Eb): mi, la e si bemolle senza scrivere il bemolle;
//   - il "groove" rilassato: swing=60 sulla batteria, il micro-tempo (shift=)
//     che fa suonare il rullante e il basso un filo dietro il tempo, la
//     piccola accordatura (tune=) del pianoforte elettrico;
//   - la scivolata di intonazione (bend=) sulla nota lunga del ponte;
//   - le automazioni: forcelle sugli accordi degli archi, il volume del
//     ponte che cresce (vol=), il rallentando finale con tempo=;
//   - strumenti definiti nel file (voce, pianoforte elettrico, archi);
//   - la corona sull'ultimo accordo.
//
//   Strofa      Ebmaj7 | Cm7 | Abmaj7 | Bb7sus4 Bb7 | Gm7 | Cm7 | Abmaj7 Fm7 | Bb7
//   Ritornello  Abmaj7 | Bb7 | Gm7 Cm7 | Fm7 Bb7 | Abmaj7 | Bb/D Ebmaj7 | Cm7 Fm7 | Bb7sus4 Bb7
//   Ponte       Cm7 | Fm7 | Dm7b5 G7 | Cm7 | Abmaj7 | Bb7sus4 | Gm7 Cm7 | Fm7 Bb7

ST: 2.6
Tempo: 66 BPM
Metrica: 4/4
Tonalita: Eb

Strumento Voce:
  program=53 percussione=no ottava=4 range=55-84 poly=no voicing=monophonic

Strumento Rhodes:
  program=4 percussione=no ottava=4 range=40-88 poly=si voicing=spread

Strumento Archi:
  program=48 percussione=no ottava=3 range=36-96 poly=si voicing=spread

Pattern %Rest:
  4: 4r |

// ---------------------------------------------------------------- melodie (voce)

Pattern %VerseM:
  key=Eb 8: 84@
  r r g*4 b*4 2c*5 b*4 g*4 |
  2g*4 e*4 f*4 3g*4 r |
  r c*5 c*5 b*4 2a*4 g*4 f*4 |
  4f*4 2d*4 2r |
  r g*4 g*4 b*4 2d*5 c*5 b*4 |
  2c*5 b*4 g*4 2e*4 2r |
  r a*4 c*5 e*5 2d*5 c*5 b*4 |
  3b*4 3r 2g*4 |

Pattern %ChorusM:
  key=Eb 8: 96@
  r c*5 c*5 e*5 2d*5 c*5 b*4 |
  2b*4 d*5 3c*5 2r |
  r g*4 b*4 d*5 2e*5 d*5 c*5 |
  r a*4 c*5 2e*5 d*5 c*5 b*4 |
  2c*5 c*5 e*5 2f*5 e*5 d*5 |
  2d*5 b*4 g*4 2e*4 2r |
  r c*5 e*5 g*5 2f*5 e*5 d*5 |
  4b*4 3d*5 r |

Pattern %BridgeM:
  key=Eb 8: 90@
  2g*4 c*5 e*5 3d*5 r |
  2c*5 a*4 c*5 3f*4 r |
  r d*5 f*5 g*5 2f*5 d*5 c*5 |
  4e*5 4d*5 |
  2c*5 e*5 f*5 2g*5 e*5 c*5 |
  bend=0 >> 6f*5 bend=1 bend=0 2r |
  2g*4 b*4 d*5 2c*5 b*4 g*4 |
  3a*4 c*5 2d*5 2b*4 |

Pattern %OutroM:
  key=Eb 8: 80@
  r c*5 c*5 e*5 2d*5 c*5 b*4 |
  2b*4 d*5 3c*5 2r |
  8r |
  1: g*4$fermata |

// ---------------------------------------------------------------- pianoforte elettrico

Pattern %RhIntro:
  4: 60@ Ebmaj7'1 | Cm7'1 | Abmaj7'1 | Bb7sus4'2 Bb7'2 |

Pattern %RhVerse:
  4: 60@ Ebmaj7'1 | Cm7'1 | Abmaj7'1 | Bb7sus4'2 Bb7'2 | Gm7'1 | Cm7'1 | Abmaj7'2 Fm7'2 | Bb7'1 |

Pattern %RhChorus:
  8: 72@
  3Abmaj7 Abmaj7 4r |
  3Bb7 Bb7 4r |
  3Gm7 r 3Cm7 r |
  3Fm7 r 3Bb7 r |
  3Abmaj7 Abmaj7 4r |
  3Bb/D r 3Ebmaj7 r |
  3Cm7 r 3Fm7 r |
  3Bb7sus4 r 3Bb7 r |

Pattern %RhBridge:
  4: 64@ Cm7'1 | Fm7'1 | Dm7b5'2 G7'2 | Cm7'1 | Abmaj7'1 | Bb7sus4'1 | Gm7'2 Cm7'2 | Fm7'2 Bb7'2 |

Pattern %RhOutro:
  4: 60@ Abmaj7'1 | Bb7'1 | Ebmaj7'1 | Ebmaj7'1$fermata |

// ---------------------------------------------------------------- archi

Pattern %ArChorus:
  4: 66@ Abmaj7'1< | Bb7'1< | Gm7'2< Cm7'2< | Fm7'2< Bb7'2< | Abmaj7'1< | Bb/D'2< Ebmaj7'2< | Cm7'2< Fm7'2< | Bb7sus4'2 Bb7'2 |

Pattern %ArBridge:
  4: 66@ Cm7'1< | Fm7'1< | Dm7b5'2< G7'2< | Cm7'1< | Abmaj7'1< | Bb7sus4'1< | Gm7'2 Cm7'2 | Fm7'2 Bb7'2 |

Pattern %ArOutro:
  4: 66@ Abmaj7'1 | Bb7'1 | Ebmaj7'1 | Ebmaj7'1$fermata |

// ---------------------------------------------------------------- chitarra (arpeggi)

Pattern %GaE:
  key=Eb 8: 58@ e*3 g*3 b*3 d*4 b*3 g*3 d*4 g*3 |

Pattern %GaC:
  key=Eb 8: 58@ c*3 e*3 g*3 b*3 e*4 b*3 g*3 e*3 |

Pattern %GaA:
  key=Eb 8: 58@ a*2 e*3 g*3 c*4 e*4 c*4 g*3 e*3 |

Pattern %GaB:
  key=Eb 8: 58@ b*2 f*3 a*3 d*4 f*4 d*4 a*3 f*3 |

Pattern %GaG:
  key=Eb 8: 58@ g*2 d*3 f*3 b*3 d*4 b*3 f*3 d*3 |

Pattern %GaF:
  key=Eb 8: 58@ f*2 c*3 e*3 a*3 c*4 a*3 e*3 c*3 |

Pattern %GtVerse:
  %GaE %GaC %GaA %GaB %GaG %GaC %GaA %GaB

Pattern %GtChorus:
  %GaA %GaB %GaG %GaF %GaA %GaE %GaC %GaB

// ---------------------------------------------------------------- basso

Pattern %BsVerse:
  key=Eb 4: 88@
  2e*2 e*2 b*1 |
  2c*2 c*2 g*1 |
  2a*1 a*1 e*2 |
  2b*1 b*1 d*2 |
  2g*1 g*1 d*2 |
  2c*2 c*2 g*1 |
  2a*1 2f*1 |
  2b*1 b*1 a*1 |

Pattern %BsChorus:
  key=Eb 4: 92@
  2a*1 a*1 e*2 |
  2b*1 b*1 d*2 |
  2g*1 2c*2 |
  2f*1 2b*1 |
  2a*1 a*1 e*2 |
  2d*2 2e*2 |
  2c*2 2f*1 |
  2b*1 2b*1 |

Pattern %BsBridge:
  key=Eb 4: 88@
  2c*2 c*2 g*1 |
  2f*1 f*1 c*2 |
  2d*2 2g*1 |
  2c*2 c*2 g*1 |
  2a*1 a*1 e*2 |
  2b*1 b*1 f*1 |
  2g*1 2c*2 |
  2f*1 2b*1 |

Pattern %BsOutro:
  key=Eb 4: 86@ 2a*1 a*1 e*2 | 2b*1 b*1 d*2 | 2e*2 2b*1 | 1: e*2$fermata |

// ---------------------------------------------------------------- batteria

Pattern %DrVerseA:
  8: 74@ [kick hihat] 42@ hihat 80@ [rimshot hihat] 42@ hihat 74@ [kick hihat] 42@ hihat 80@ [rimshot hihat] 42@ hihat |

Pattern %DrVerseB:
  8: 74@ [kick hihat] 42@ hihat 80@ [rimshot hihat] 42@ hihat 42@ hihat 74@ [kick hihat] 80@ [rimshot hihat] 42@ hihat |

Pattern %DrFill:
  8: 80@ [kick hihat] 42@ hihat 80@ [snare hihat] 42@ hihat 85@ snare tom1 tom2 90@ floor |

Pattern %DrCrash:
  8: 100@ [kick crash] 45@ hihat 90@ [snare hihat] 45@ hihat 85@ [kick hihat] 45@ [kick hihat] 92@ [snare hihat] 45@ hihat |

Pattern %DrChorus:
  8: 88@ [kick hihat] 45@ hihat 90@ [snare hihat] 45@ hihat 85@ [kick hihat] 45@ [kick hihat] 92@ [snare hihat_open] 45@ hihat |

Pattern %DrBridge:
  8: 70@ [kick ride] 40@ ride 75@ [rimshot ride] 40@ ride 70@ [kick ride] 40@ ride 75@ [rimshot ride] 40@ ride |

Pattern %DrIntro:
  8: 48@ hihat 34@ hihat 44@ hihat 34@ hihat 48@ hihat 34@ hihat 44@ hihat 34@ hihat |

Pattern %DrVerse2:
  %DrVerseA %DrVerseB

Pattern %DrumsVerse:
  3%DrVerse2 %DrVerseA %DrFill

Pattern %DrumsChorus:
  %DrCrash 6%DrChorus %DrFill

Pattern %DrumsBridge:
  7%DrBridge %DrFill

// ================================================================ tracce

Voce:

Box Voce "Strofa 1" |16:
  // strofa 1
  $"sottovoce" %VerseM "La not- te scen- de sul- le stra- de e tu mi guar- di qui sem- pre non ser- ve dir- ci più il cuo- re sa la se- ra è no- stra o- ra"

Box Voce "Ritornello 1" |48:
  // ritornello 1
  %ChorusM "Re- sta an- co- ra un po' con me la not- te è lun- ga e ti vo- glio an- cor non c'è fret- ta que- sta se- ra re- sta con me fi- no al mat- ti- no"

Box Voce "Strofa 2" |80:
  // strofa 2: la stessa musica, parole nuove
  %VerseM "Il tuo pro- fu- mo ri- ma- ne qui co- me un pen- sie- ro lie- ve il tem- po si fer- ma nei tuoi oc- chi ri- tro- vo la pa- ce con te"

Box Voce "Ritornello 2" |112:
  // ritornello 2
  %ChorusM "Re- sta an- co- ra un po' con me la not- te è lun- ga e ti vo- glio an- cor non c'è fret- ta que- sta se- ra re- sta con me fi- no al mat- ti- no"

Box Voce "Ponte" |144:
  // ponte: la nota lunga e' una scivolata di intonazione
  $"con anima" %BridgeM "Quan- te vol- te ti cer- ca- vo in mez- zo al ven- to ec- co il mon- do ta- ce qui sì ti pre- go non par- ti re- sta re- sta"

Box Voce "Ritornello finale" |176:
  // ritornello finale, piu' forte
  vol=100 %ChorusM "Re- sta an- co- ra un po' con me la not- te è lun- ga e ti vo- glio an- cor non c'è fret- ta que- sta se- ra re- sta con me fi- no al mat- ti- no"

Box Voce "Coda" |208:
  // coda
  %OutroM "Re- sta an- co- ra un po' con me sì"

Rhodes:

Box Rhodes "Inizio" |0:
  tune=-8
  %RhIntro %RhVerse %RhChorus %RhVerse %RhChorus

Box Rhodes "Ponte" |144:
  // ponte
  %RhBridge
  %RhChorus
  %RhOutro

Archi:

Box Archi "Ritornello 1" |48:
  // entrano al primo ritornello
  %ArChorus
  8%Rest
  %ArChorus

Box Archi "Ponte" |144:
  // ponte: il volume cresce per tutte le otto battute
  vol=45 >>
  %ArBridge
  vol=100
  %ArChorus
  %ArOutro

Guitar 1:

Box Guitar 1 "Strofa 2" |80:
  // la chitarra entra alla seconda strofa
  vol=80 %GtVerse
  %GtChorus
  8%Rest
  vol=100 %GtChorus

Box Guitar 1 "Coda" |208:
  // coda
  %GaA %GaB %GaE
  key=Eb 1: [e*3 g*3 b*3 d*4]$fermata |

Bass:

Box Bass "Groove" |0:
  // il basso suona un poco dopo il tempo
  shift=12
  2%Rest

Box Bass "Introduzione" |8:
  // introduzione (ultime due battute)
  shift=12 key=Eb 4: 88@ 2a*1 a*1 e*2 | 2b*1 b*1 d*2 |
  %BsVerse %BsChorus %BsVerse %BsChorus
  %BsBridge
  %BsChorus
  %BsOutro

Drums:

Box Drums "Groove" |0:
  // il rullante e' un po' indietro, come nelle ballate soul
  swing=60 shift=14
  2%Rest 2%DrIntro
  %DrumsVerse %DrumsChorus %DrumsVerse %DrumsChorus
  %DrumsBridge
  %DrumsChorus

Box Drums "Coda" |208:
  // coda: il rallentando comincia sulla prima battuta
  swing=60 shift=14 100@ tempo=66 <<
  8: [kick hihat] hihat [rimshot hihat] hihat [kick hihat] hihat [rimshot hihat] hihat |
  8: [kick hihat] hihat [rimshot hihat] hihat [kick hihat] hihat [rimshot hihat] hihat |
  8: [kick hihat] hihat [snare hihat] hihat [snare hihat] snare [snare hihat] hihat |
  8: [kick crash] 7r |
  tempo=48

// ================================================================ mixer

Mixer Voce:
  volume: 100 pan: 0 mute: no solo: no reverb: 30

Mixer Rhodes:
  volume: 78 pan: -0.3 mute: no solo: no reverb: 20 chorus: 30

Mixer Archi:
  volume: 68 pan: 0.2 mute: no solo: no reverb: 40

Mixer Guitar 1:
  volume: 66 pan: 0.45 mute: no solo: no reverb: 25

Mixer Bass:
  volume: 94 pan: -0.05 mute: no solo: no

Mixer Drums:
  volume: 82 pan: 0 mute: no solo: no reverb: 15
