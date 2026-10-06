// Blues in La: introduzione, quattro cori da 12 battute e coda.
//
// Un brano intero costruito con i pattern: ogni "coro" (le 12 battute del
// blues) e' un pattern fatto di pattern di una battuta, e le tracce lo
// richiamano. Ogni coro cambia carattere:
//   1. il tema, alla tromba;      2. l'assolo di pianoforte;
//   3. l'assolo di chitarra, con scivolate e bending;      4. il tema, di nuovo,
// poi la coda con il rallentando e la corona sull'ultimo accordo.
// Lo swing (swing=66) da' il "terzinato" del blues alle crome scritte dritte.

ST: 2.6
Tempo: 96 BPM
Metrica: 4/4
Tonalita: A

// ---------------------------------------------------------------- batteria

Pattern %Click:
  4: 70@ rimshot r rimshot hihat_pedal |

Pattern %Shuffle:
  8: 100@ [kick hihat] 60@ hihat 100@ [snare hihat] 60@ hihat 100@ [kick hihat] 60@ hihat 100@ [snare hihat] 60@ [kick hihat] |

Pattern %ShuffleCrash:
  8: 110@ [kick crash] 60@ hihat 100@ [snare hihat] 60@ hihat 100@ [kick hihat] 60@ hihat 100@ [snare hihat] 60@ [kick hihat] |

Pattern %ShuffleSoft:
  8: 75@ [kick ride] 45@ ride 70@ [rimshot ride] 45@ ride 75@ [kick ride] 45@ ride 70@ [rimshot ride] 45@ ride |

Pattern %FillA:
  8: 100@ [kick hihat] 60@ hihat 100@ [snare hihat] 60@ hihat 95@ snare snare 105@ tom1 floor |

Pattern %FillB:
  8: 100@ [kick hihat] 100@ snare 105@ snare 100@ tom1 tom2 floor 110@ [kick floor] 90@ snare |

Pattern %DrumsChorus:
  %ShuffleCrash %Shuffle %Shuffle %Shuffle %Shuffle %Shuffle %Shuffle %FillA %Shuffle %Shuffle %Shuffle %FillB

Pattern %DrumsChorusSoft:
  %ShuffleSoft %ShuffleSoft %ShuffleSoft %ShuffleSoft %ShuffleSoft %ShuffleSoft %ShuffleSoft %FillA %ShuffleSoft %ShuffleSoft %ShuffleSoft %FillB

// ---------------------------------------------------------------- basso (camminato)

Pattern %BassA1:
  4: 92@ a*1 c#*2 e*2 f#*2 |

Pattern %BassA2:
  4: 88@ a*1 e*2 g*2 e*2 |

Pattern %BassD1:
  4: 92@ d*2 f#*2 a*2 b*2 |

Pattern %BassD2:
  4: 88@ d*2 a*2 c*3 a*2 |

Pattern %BassE1:
  4: 92@ e*2 g#*2 b*2 c#*3 |

Pattern %BassTurn:
  4: 95@ e*2 d*2 c#*2 b*1 |

Pattern %BassChorus:
  %BassA1 %BassD1 %BassA2 %BassA1 %BassD2 %BassD1 %BassA2 %BassA1 %BassE1 %BassD2 %BassA1 %BassTurn

// ---------------------------------------------------------------- chitarra ritmica (shuffle 1-5, 1-6, 1-b7)

Pattern %GA:
  8: 88@ [a*2 e*3] [a*2 e*3] [a*2 f#*3] [a*2 f#*3] [a*2 g*3] [a*2 g*3] [a*2 f#*3] [a*2 f#*3] |

Pattern %GD:
  8: 88@ [d*3 a*3] [d*3 a*3] [d*3 b*3] [d*3 b*3] [d*3 c*4] [d*3 c*4] [d*3 b*3] [d*3 b*3] |

Pattern %GE:
  8: 88@ [e*3 b*3] [e*3 b*3] [e*3 c#*4] [e*3 c#*4] [e*3 d*4] [e*3 d*4] [e*3 c#*4] [e*3 c#*4] |

Pattern %GChorus:
  %GA %GD %GA %GA %GD %GD %GA %GA %GE %GD %GA %GE

// ---------------------------------------------------------------- pianoforte (accordi sul 2 e sul 4)

Pattern %CompA:
  4: 78@ r A7! r A7! |

Pattern %CompD:
  4: 78@ r D7! r D7! |

Pattern %CompE:
  4: 78@ r E7! r E7! |

Pattern %CompChorus:
  %CompA %CompD %CompA %CompA %CompD %CompD %CompA %CompA %CompE %CompD %CompA %CompE

// ---------------------------------------------------------------- tromba: il tema (dialogo con la chitarra)

Pattern %Rest:
  4: 4r |

Pattern %Head:
  8: 96@ r e*4 g*4 a*4 4a*4 | g*4 a*4 2c*5 c*5 a*4 2g*4 |
  8r |
  8r |
  r a*4 c*5 d*5 4d*5 | c*5 d*5 2f*5 f*5 d*5 2c*5 |
  r a*4 c*5 e*5 4e*5 |
  8r |
  b*4 d*5 2e*5 d*5 b*4 2g#*4 | a*4 c*5 2d*5 c*5 a*4 2f#*4 |
  e*4 g*4 a*4 c*5 4a*4 |
  4r b*4 g#*4 e*4 d*4 |

// ================================================================ tracce

Drums:

Box Drums "Introduzione" |0:
  // introduzione: il click, poi il groove entra con il rullo
  swing=66 2%Click %Shuffle %FillA

Box Drums "Coro 1" |16:
  // coro 1: il tema
  swing=66 %DrumsChorus

Box Drums "Coro 2" |64:
  // coro 2: assolo di pianoforte, la batteria suona piano sul ride
  swing=66 %DrumsChorusSoft

Box Drums "Coro 3" |112:
  // coro 3: assolo di chitarra, tutta la forza
  swing=66 %DrumsChorus

Box Drums "Coro 4" |160:
  // coro 4: il tema, e la coda con il rallentando
  swing=66 %DrumsChorus

Box Drums "Coda" |208:
  // il rallentando va chiuso prima di un nuovo cambio di velocity: qui non ce ne sono
  swing=66 100@ tempo=96 <<
  8: [kick hihat] hihat [snare hihat] hihat [kick hihat] hihat [snare hihat] [kick hihat] |
  [kick crash] 7r |
  tempo=62

Bass:

Box Bass "Inizio" |8:
  %BassA1 %BassE1
  4%BassChorus

Box Bass "Coda" |208:
  // coda
  4: 92@ a*1 c#*2 e*2 f#*2 | 4: 2a*1 2r |

Guitar 1:

Box Guitar 1 "Inizio" |0:
  swing=66
  2%Rest %GA %GE

Box Guitar 1 "Coro 1" |16:
  // coro 1: ritmica piena
  swing=66 %GChorus

Box Guitar 1 "Coro 2" |64:
  // coro 2: sotto l'assolo di pianoforte, il volume scende
  swing=66 vol=62 %GChorus

Box Guitar 1 "Coro 3" |112:
  // coro 3: torna a pieno volume per l'assolo
  swing=66 vol=100 %GChorus

Box Guitar 1 "Coro 4" |160:
  // coro 4
  swing=66 %GChorus

Box Guitar 1 "Coda" |208:
  // coda
  swing=66 %GA 8: [a*2 e*3 a*3]'1 |

Piano:

Box Piano "Introduzione" |0:
  // introduzione: I - IV - I - V
  swing=66 %CompA %CompD %CompA %CompE

Box Piano "Coro 1" |16:
  // coro 1: accordi sul 2 e sul 4
  swing=66 %CompChorus

Box Piano "Coro 2" |64:
  // coro 2: assolo (la mano destra, sul giro del blues)
  swing=66 8: 100@
  e*5 2g*5 e*5 c*5 2a*4 r |
  d*5 f*5 2a*5 f*5 d*5 2c*5 |
  a*4 c*5 d*5 d#*5 2e*5 e*5 r |
  4e*5 g*5 e*5 2c*5 |
  a*5 2f*5 d*5 2c*5 a*4 r |
  d*5 f*5 a*5 c*6 2a*5 f*5 r |
  e*5 e*5 g*5 a*5 2c*6 a*5 e*5 |
  4a*5 2e*5 c*5 a*4 |
  b*5 d*6 2e*6 d*6 b*5 2g#*5 |
  a*5 c*6 2d*6 c*6 a*5 2f#*5 |
  e*5 g*5 a*5 c*6 4e*6 |
  2b*5 g#*5 e*5 d*5 b*4 2e*4 |

Box Piano "Coro 3" |112:
  // coro 3: di nuovo il compagnamento
  swing=66 8: 100@ %CompChorus

Box Piano "Coro 4" |160:
  // coro 4
  swing=66 8: 100@ %CompChorus

Box Piano "Coda" |208:
  // coda: gli ultimi due accordi, il secondo con la corona
  swing=66 8: 100@ 4: 80@ r A7! r A7! |
  1: 90@ A7$fermata |

Trumpet:

Box Trumpet "Inizio" |0:
  swing=66
  4%Rest

Box Trumpet "Coro 1" |16:
  // coro 1: il tema
  swing=66 %Head

Box Trumpet "Coro 4" |160:
  // coro 4: il tema, con piu' forza
  swing=66 100@ %Head

Box Trumpet "Coda" |208:
  // coda
  swing=66 100@ 4: 4r | 4: 4r |

Guitar 2:

Box Guitar 2 "Coro 3" |112:
  // coro 3: assolo, con scivolate (nota>nota) e bending (bend=)
  swing=66 8: 100@
  2a*4>c*5 c*5 e*5 2e*5 2r |
  d*5 f*5 a*5 f*5 2d*5 2c*5 |
  a*4 c*5 e*5 g*5 bend=0 >> 4a*5 bend=1 bend=0 |
  2e*5>g*5 e*5 c*5 2a*4 2r |
  4d*5 f*5 a*5 2c*6 |
  a*5 f*5 d*5 f*5 2a*5 2r |
  e*5 a*5 c*6 a*5 2e*5 2c*5 |
  4a*5 2g*5 2e*5 |
  b*4 d*5 e*5 g#*5 bend=0 >> 4b*5 bend=1 bend=0 |
  a*5 f#*5 d*5 f#*5 2a*5 2f#*5 |
  e*5 g*5 a*5 c*6 2a*5 2e*5 |
  2b*4 g#*4 e*4 4e*4 |
  12%Rest
  4: 4r | 4: 4r |

// ================================================================ mixer

Mixer Piano:
  volume: 88 pan: -0.3 mute: no solo: no reverb: 18

Mixer Guitar 1:
  volume: 80 pan: -0.5 mute: no solo: no

Mixer Guitar 2:
  volume: 92 pan: 0.45 mute: no solo: no reverb: 30

Mixer Bass:
  volume: 100 pan: 0 mute: no solo: no

Mixer Trumpet:
  volume: 92 pan: 0.25 mute: no solo: no reverb: 25

Mixer Drums:
  volume: 90 pan: 0 mute: no solo: no reverb: 12
