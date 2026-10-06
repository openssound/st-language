// Rock distorto: un brano rock in Mi minore, 32 battute a 124 BPM.
//
// Chitarra solista con molta distorsione, batteria e basso in primo piano
// (volumi alti nel mixer), con una chitarra ritmica di accompagnamento piu'
// bassa e dietro. Forma:
//   introduzione 4 + strofa 8 + ritornello 8 + assolo 8 + coda 4
//   Strofa e assolo  Em | C | G | D  (due volte)
//   Ritornello       C | G | D | Em  (due volte)
// Cosa c'e' dentro:
//   - la chitarra solista con il programma "Distortion Guitar" e velocity
//     alte: il riff in pentatonica minore, il tema del ritornello a note
//     lunghe e l'assolo con semicrome veloci e scivolate (nota>nota);
//   - il basso a ottavi che "martella" la fondamentale, con la cassa;
//   - la batteria rock: cassa e rullante sul 1-3 e 2-4, charleston sugli
//     ottavi, il piatto crash sul primo colpo del ritornello e un fill in
//     fondo a ogni sezione;
//   - la chitarra ritmica doppiata a destra e a sinistra: power chord con il
//     palm mute (ottavi staccati `!` a velocity bassa), colpi aperti accentati
//     e galoppo di semicrome; nel ritornello power chord aperti;
//   - la corona ($fermata) sull'ultimo accordo;
//   - strumenti definiti nel file (chitarra distorta, basso a plettro).

Tempo: 124 BPM
Metrica: 4/4
Tonalita: Em

Strumento Distorta:
  program=30 percussione=no ottava=4 range=40-88 poly=no voicing=monophonic

Strumento Ritmica:
  program=29 percussione=no ottava=2 range=36-76 poly=si voicing=power

Strumento Basso:
  program=34 percussione=no ottava=2 range=28-60 poly=no voicing=monophonic

Pattern %Rest:
  4: 4r |

// ---------------------------------------------------------------- batteria

Pattern %DrRock:
  16: 110@ [kick hihat] r 75@ hihat r 112@ [snare hihat] r 75@ hihat r 110@ [kick hihat] r 105@ [kick hihat] r 112@ [snare hihat] r 75@ hihat r |

Pattern %DrChorus:
  16: 115@ [kick crash] r 80@ hihat_open r 115@ [snare hihat] r 80@ hihat r 112@ [kick hihat] r 105@ [kick hihat] r 115@ [snare hihat] r 80@ hihat_open r |

Pattern %DrFill:
  16: 110@ [kick hihat] r 75@ hihat r 112@ [snare hihat] r 100@ snare 105@ snare 100@ tom1 100@ tom1 105@ tom2 105@ tom2 110@ floor 110@ floor 115@ [kick snare] 115@ [kick snare] |

Pattern %DrVerse4:
  3%DrRock %DrFill

Pattern %DrChorus4:
  3%DrChorus %DrFill

// ---------------------------------------------------------------- basso

Pattern %BsEm:
  key=Em 16: 110@ 2e*2 2e*2 2e*2 2e*2 2e*2 2e*2 2e*2 2g*2 |

Pattern %BsC:
  key=Em 16: 110@ 2c*2 2c*2 2c*2 2c*2 2c*2 2c*2 2c*2 2e*2 |

Pattern %BsG:
  key=Em 16: 110@ 2g*1 2g*1 2g*1 2g*1 2g*1 2g*1 2g*1 2b*1 |

Pattern %BsD:
  key=Em 16: 110@ 2d*2 2d*2 2d*2 2d*2 2d*2 2d*2 2d*2 2f#*2 |

Pattern %BsVerse4:
  %BsEm %BsC %BsG %BsD

Pattern %BsChorus4:
  %BsC %BsG %BsD %BsEm

// ---------------------------------------------------------------- chitarra ritmica
// Palm mute: ottavi staccati (`!`) a velocity bassa sulla fondamentale, poi i
// colpi aperti e accentati che fanno respirare il riff. A: sei ottavi muti e
// due colpi pieni; B: un galoppo di semicrome al posto dei primi due ottavi;
// R: il ritornello, power chord aperti e accentati.

Pattern %RtEmA:
  16: 72@ 2E.power! 2E.power! 2E.power! 2E.power! 2E.power! 2E.power! 112@ 2E.power 118@ 2E.power |

Pattern %RtEmB:
  16: 72@ E.power! E.power! E.power! E.power! 2E.power! 2E.power! 2E.power! 2E.power! 112@ 2E.power 118@ 2E.power |

Pattern %RtEmR:
  16: 112@ 4E.power 100@ 2E.power 2E.power! 112@ 4E.power 100@ 2E.power 118@ 2E.power |

Pattern %RtCA:
  16: 72@ 2C.power! 2C.power! 2C.power! 2C.power! 2C.power! 2C.power! 112@ 2C.power 118@ 2C.power |

Pattern %RtCB:
  16: 72@ C.power! C.power! C.power! C.power! 2C.power! 2C.power! 2C.power! 2C.power! 112@ 2C.power 118@ 2C.power |

Pattern %RtCR:
  16: 112@ 4C.power 100@ 2C.power 2C.power! 112@ 4C.power 100@ 2C.power 118@ 2C.power |

Pattern %RtGA:
  16: 72@ 2G.power! 2G.power! 2G.power! 2G.power! 2G.power! 2G.power! 112@ 2G.power 118@ 2G.power |

Pattern %RtGB:
  16: 72@ G.power! G.power! G.power! G.power! 2G.power! 2G.power! 2G.power! 2G.power! 112@ 2G.power 118@ 2G.power |

Pattern %RtGR:
  16: 112@ 4G.power 100@ 2G.power 2G.power! 112@ 4G.power 100@ 2G.power 118@ 2G.power |

Pattern %RtDA:
  16: 72@ 2D.power! 2D.power! 2D.power! 2D.power! 2D.power! 2D.power! 112@ 2D.power 118@ 2D.power |

Pattern %RtDB:
  16: 72@ D.power! D.power! D.power! D.power! 2D.power! 2D.power! 2D.power! 2D.power! 112@ 2D.power 118@ 2D.power |

Pattern %RtDR:
  16: 112@ 4D.power 100@ 2D.power 2D.power! 112@ 4D.power 100@ 2D.power 118@ 2D.power |

Pattern %RtVerse4:
  %RtEmA %RtCB %RtGA %RtDB

Pattern %RtChorus4:
  %RtCR %RtGR %RtDR %RtEmR

// ---------------------------------------------------------------- chitarra solista

Pattern %RiffEm:
  key=Em 16: 4e*4 2g*4 2a*4 4b*4 2a*4 2g*4 |

Pattern %RiffC:
  key=Em 16: 4c*5 2b*4 2g*4 4e*4 2g*4 2e*4 |

Pattern %RiffG:
  key=Em 16: 4d*5 2b*4 2a*4 4g*4 2a*4 2b*4 |

Pattern %RiffD:
  key=Em 16: 4a*4 2f#*4 2a*4 4d*5 2c*5 2a*4 |

Pattern %RiffVerse4:
  %RiffEm %RiffC %RiffG %RiffD

Pattern %ThemeC:
  key=Em 16: 6g*5 2e*5 8c*5 |

Pattern %ThemeG:
  key=Em 16: 6d*5 2g*5 8b*5 |

Pattern %ThemeD:
  key=Em 16: 6a*5 2f#*5 8d*5 |

Pattern %ThemeEm:
  key=Em 16: 8e*5 8b*4 |

Pattern %ThemeChorus4:
  %ThemeC %ThemeG %ThemeD %ThemeEm

Pattern %SoloEm1:
  key=Em 16: 2b*4 2e*5 2g*5 2b*5 4a*5>b*5 4g*5 |

Pattern %SoloC1:
  key=Em 16: 2g*5 2e*5 2c*5 2e*5 2g*5 2e*5 4c*5>e*5 |

Pattern %SoloG1:
  key=Em 16: 2d*5 2g*5 2b*5 2d*6 2b*5 2g*5 4d*5 |

Pattern %SoloD1:
  key=Em 16: 2a*5 2f#*5 2d*5 2f#*5 8a*5>d*6 |

Pattern %SoloEm2:
  key=Em 16: b*5 e*6 b*5 g*5 e*5 g*5 b*5 g*5 4e*6 4b*5 |

Pattern %SoloC2:
  key=Em 16: g*5 c*6 g*5 e*5 c*5 e*5 g*5 e*5 8c*6 |

Pattern %SoloG2:
  key=Em 16: d*6 b*5 g*5 b*5 d*6 b*5 g*5 d*5 4g*5 4b*5 |

Pattern %SoloD2:
  key=Em 16: 2a*5 2f#*5 2d*5 2a*5 8d*6 |

Pattern %SoloAll:
  %SoloEm1 %SoloC1 %SoloG1 %SoloD1 %SoloEm2 %SoloC2 %SoloG2 %SoloD2

// ================================================================ tracce

Drums:

Box Drums "Introduzione" |0:
  3%DrRock %DrFill

Box Drums "Strofa" |16:
  2%DrVerse4

Box Drums "Ritornello" |48:
  2%DrChorus4

Box Drums "Assolo" |80:
  2%DrVerse4

Box Drums "Coda" |112:
  %DrRock %DrRock %DrRock
  16: 118@ [kick crash] 15r |

Basso:

Box Basso "Introduzione" |0:
  4%BsEm

Box Basso "Strofa" |16:
  2%BsVerse4

Box Basso "Ritornello" |48:
  2%BsChorus4

Box Basso "Assolo" |80:
  2%BsVerse4

Box Basso "Coda" |112:
  %BsEm %BsC %BsD
  16: 100@ 16e*2$fermata |

Ritmica:

Box Ritmica "Introduzione" |8:
  2%RtEmA

Box Ritmica "Strofa" |16:
  2%RtVerse4

Box Ritmica "Ritornello" |48:
  2%RtChorus4

Box Ritmica "Assolo" |80:
  2%RtVerse4

Box Ritmica "Coda" |112:
  %RtEmA %RtCB %RtDA
  16: 80@ 16E.power$fermata |

Ritmica 2:

Box Ritmica 2 "Introduzione" |8:
  2%RtEmA

Box Ritmica 2 "Strofa" |16:
  2%RtVerse4

Box Ritmica 2 "Ritornello" |48:
  2%RtChorus4

Box Ritmica 2 "Assolo" |80:
  2%RtVerse4

Box Ritmica 2 "Coda" |112:
  %RtEmA %RtCB %RtDA
  16: 80@ 16E.power$fermata |

Distorta:

Box Distorta "Introduzione" |0:
  // due battute di silenzio, poi il riff
  2%Rest 115@ %RiffEm %RiffEm

Box Distorta "Strofa" |16:
  // il riff sotto la strofa, un po' piu' piano
  105@ 2%RiffVerse4

Box Distorta "Ritornello" |48:
  // il tema a note lunghe, con piu' forza
  124@ 2%ThemeChorus4

Box Distorta "Assolo" |80:
  // l'assolo: semicrome veloci e scivolate
  127@ %SoloAll

Box Distorta "Coda" |112:
  115@ %RiffEm %RiffC %RiffD
  16: 127@ 16e*5$fermata |

// ================================================================ mixer

Mixer Drums:
  volume: 120 pan: 0 mute: no solo: no reverb: 12

Mixer Basso:
  volume: 125 pan: 0 mute: no solo: no

Mixer Distorta:
  volume: 140 pan: 0.1 mute: no solo: no reverb: 22

Mixer Ritmica:
  volume: 80 pan: -0.7 mute: no solo: no reverb: 10

Mixer Ritmica 2:
  volume: 80 pan: 0.7 mute: no solo: no reverb: 10

// ================================================================ effetti
// (blocchi dell'app SoundText: gli altri lettori li saltano e suonano la
// chitarra col solo programma "Distortion Guitar")

Effetti Distorta:
  distorsione: spinta=34 tono=65 livello=-10 mix=100
  amplificatore: modello=high_gain cassa=4x12 guadagno=40 bassi=6 medi=6 alti=7 presenza=8 potenza=60 livello=-12
  delay: suddivisione=1/8p ripetizioni=22 mix=14

Effetti Ritmica:
  amplificatore: modello=british cassa=4x12 guadagno=28 bassi=7 medi=6 alti=6 presenza=6 potenza=45 livello=-12

Effetti Ritmica 2:
  amplificatore: modello=british cassa=4x12 guadagno=28 bassi=7 medi=6 alti=6 presenza=6 potenza=45 livello=-12
