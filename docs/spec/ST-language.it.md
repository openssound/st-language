# Specifica di ST-language

**Versione 2.7** · Implementazione di riferimento: la libreria Python
`st_language` (questo repository) · Versione inglese, di riferimento in
caso di differenze: [ST-language.md](ST-language.md)

© 2026 Sergio Scolaro. Questa specifica e' distribuita con licenza
[Creative Commons Attribuzione 4.0 Internazionale](https://creativecommons.org/licenses/by/4.0/deed.it)
(CC BY 4.0): si puo' copiare, tradurre e adattare, anche a fini
commerciali, citando la fonte. L'implementazione di riferimento e'
software libero con licenza GPL-3.0 o successiva.

---

## 1. Introduzione

ST-language (SoundText Language) e' una notazione musicale in testo
semplice: melodie, accordi astratti, batteria, dinamiche, cambi di tempo,
piu' voci e testo cantato, scritti come una sequenza di brevi token.

```
// Strofa
4: Am | F | C | G |            // un accordo per battuta
8: e*5 d*5 c*5 d*5 2e*5 2e*5 |
"Ma- ri- a, sei qui"
```

Questo documento definisce:

- la **notazione** di una singola parte (il *testo di una traccia*): come
  il testo diventa un elenco di eventi musicali nel tempo (sezioni 2-11);
- il formato dei **file di brano** `.st`, che mette insieme piu' tracce,
  pattern, tempo e metrica (sezione 12);
- come gli eventi diventano **MIDI** (sezione 13, informativa);
- la **suite di conformita'** (sezione 14).

### 1.1 Conformita'

Le parole DEVE, NON DEVE, DOVREBBE e PUO' (MUST, MUST NOT, SHOULD, MAY)
hanno il significato della RFC 2119. Un **parser** conforme trasforma ogni
testo di traccia valido negli eventi della sezione 11 (stessi tipi, tempi,
durate, altezze e velocity dell'implementazione di riferimento,
confrontati con una tolleranza di 10⁻⁹ quarti) e rifiuta ogni testo non
valido (sezione 10). Un **lettore di brani** conforme legge anche il
formato `.st` della sezione 12. Il testo dei messaggi d'errore non e'
normativo.

### 1.2 Unita'

Il tempo si misura in **quarti** (beat): un quarto e' una semiminima. Un
parser conforme DEVE calcolare le posizioni con **aritmetica razionale
esatta** (o equivalente): le terzine sommano terzi di quarto, e l'errore
della virgola mobile sposterebbe gli eventi successivi oltre le
stanghette.

---

## 2. Struttura lessicale

Il testo di una traccia e' una stringa Unicode. Gli a capo sono spazi,
con un'eccezione: chiudono i commenti.

### 2.1 Commenti

`//` apre un **commento** fino alla fine della riga (a capo escluso). Un
`//` dentro un testo cantato (`"..."`, sezione 8.5) sulla stessa riga non
apre un commento. I commenti si tolgono prima della suddivisione in
token; le implementazioni DOVREBBERO sostituirli con spazi, cosi' le
posizioni dei caratteri restano quelle del testo originale.

### 2.2 Token

Tolti i commenti, il testo si divide in **token** da sinistra a destra;
gli spazi separano i token e per il resto si ignorano. In ogni punto vale
la prima regola che si applica:

1. `|` e' un token a se' (controllo di battuta, sezione 8.6), insieme a
   cio' che lo segue subito in `|:` (inizio ritornello), `||` (doppia
   stanghetta) e `|N.` con N una cifra 1-9 (casella, sezione 8.7). Un
   `:` subito prima di `|` apre un token `:|` (fine ritornello), che con
   il numero di una casella diventa `:|N.`; un token semplice non
   contiene mai `:|`. `$"` apre un token di **indicazione di testo** che
   finisce alla `"` successiva (sezione 8.8).
2. `"` apre un token di **testo cantato** che finisce alla `"`
   successiva. Senza la virgoletta di chiusura e' un errore.
3. Delle cifre facoltative seguite da `[` aprono un **blocco** che finisce
   alla prima `]` successiva (i blocchi non si annidano); un `'` subito
   dopo la `]` aggiunge al token un valore di nota (`[c e g]'2`), e un
   solo `<` o `>` subito dopo la `]` una forcella (`[c e g]<`), poi un `~`
   una legatura di valore e un `(` o `)` una legatura di portamento
   (`[c e g]~`, `[c e g](`). Senza `]` e' un errore.
4. Delle cifre facoltative seguite da `&"` aprono un **riferimento MIDI**:
   il nome del file arriva fino alla `"` successiva (puo' contenere
   spazi), e un `+` o un `-` seguito da cifre subito dopo la virgoletta
   di chiusura allunga il token con una trasposizione
   (`&"Blues/bass line"-2`). Senza la virgoletta di chiusura e' un errore.
5. Delle cifre facoltative seguite da `(` aprono un **gruppo** che finisce
   alla `)` corrispondente; le parentesi si annidano, e quelle dentro un
   testo cantato non contano. Senza la `)` corrispondente e' un errore.
6. `{` apre un **blocco di voci** che finisce alla `}` corrispondente
   (stesse regole dei gruppi). Senza la `}` corrispondente e' un errore.
7. Altrimenti un token **semplice** arriva fino a uno spazio, a `|` o a
   `"`. Cosi' `d*4|` sono due token (`d*4`, `|`) e `c"la"` sono due token
   (`c`, `"la"`).

Gruppi e blocchi di voci conservano il loro contenuto come testo, che
viene diviso di nuovo in token, con le stesse regole, quando il gruppo o
il blocco viene interpretato.

---

## 3. Grammatica

La grammatica di ogni tipo di token (EBNF; `digit` e' 0-9, `letter` e'
A-Z o a-z, `word` sono una o piu' lettere, cifre o `_`):

```ebnf
token        = grid | velocity | tempo | ramp | control | swing | shift | anchor
             | transpose | reset
             | pitch-mode | key-mode | sustain
             | bar-check | repeat | text | harmony | navigation | lyric
             | pattern-ref | midi-ref | group | voices | sounding ;

grid         = number [ tuplet ] ":" ;                          (* 4:  8T:  8D: *)
tuplet       = "T" | "Q" | "S" | "D" ;
velocity     = ( number | dynamic ) "@" ;                       (* 100@  mf@ *)
dynamic      = "pppp" | "ppp" | "pp" | "p" | "mp" | "mf" | "f" | "ff" | "fff" | "ffff" ;
tempo        = "tempo=" number [ "." digit { digit } ]
               [ "'" note-number [ "." [ "." ] ] ] ;           (* tempo=120  tempo=72.5  tempo=60'4. *)
ramp         = ( ">>" | "<<" ) [ curve ] ;                       (* >>  >>exp *)
curve        = "lin" | "exp" | "log" | "s" ;
control      = control-name "=" [ "-" ] number [ "." digit { digit } ] ;
control-name = "vol" | "expr" | "pan" | "mod" | "rev" | "cho" | "bend"
             | "tune" | "cc" number ;                         (* vol=80  cc74=30 *)
swing        = "swing" [ "16" ] "=" number ;                    (* swing=66 *)
shift        = "shift=" [ "-" ] number ;                        (* shift=-15 *)
anchor       = "bar=" number ;                                  (* bar=29 *)
transpose    = "transpose=" [ "-" ] number ;                    (* transpose=-3 *)
reset        = "reset:" ;
pitch-mode   = "rel:" | "abs:" ;
key-mode     = "key=" ( root [ "m" ] | "off" ) ;                (* key=G  key=Dm *)
sustain      = "SON" | "SOFF" ;
bar-check    = "|" ;
repeat       = "|:" | ":|" | "||" | "|" digit "." | ":|" digit "." ;   (* |: :| |1. *)
text         = '$"' { any character except '"' } '"' ;          (* $"rit." *)
harmony      = "$" root quality [ "/" bass ] ;                  (* $Am7  $G7/B *)
navigation   = "$segno" | "$coda" | "$tocoda" | "$fine" | "$dc" | "$ds" ;
lyric        = '"' [ verse ":" ] { qualunque carattere tranne '"' } '"' ;   (* "la la"  "2: lo lo" *)
verse        = "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
pattern-ref  = [ number ] "%" word [ ( "+" | "-" ) number ] ;      (* %Riff  3%Riff  %Riff+7 *)
midi-ref     = [ number ] "&" '"' file-name '"' [ ( "+" | "-" ) number ] ;
                                                  (* &"Riff"  2&"Blues/bass line"-12 *)
file-name    = any character except '"' , { any character except '"' } ;
group        = [ number ] "(" { token } ")" ;                   (* 4(c d) *)
voices       = "{" voice { ";" voice } "}" ;                    (* { c d ; 2e } *)
voice        = { token } ;

sounding     = ( note | chord | percussion | rest | block | slide ) [ value ]
               { mark } [ hairpin ] [ "~" ] [ "(" | ")" ] ;
mark         = "$" ( "accent" | "marcato" | "tenuto" | "fermata" | "tr"
                     | "mordent" | "turn" | "arp" | "staccatissimo"
                     | "sfz" | "fp" | "trem" | "harmonic" ) ;      (* c$tr *)
hairpin      = "<" | ">" ;                                      (* 2c<  c'2> *)
note         = [ number ] pitch [ octave ] [ modifier ] ;
pitch        = "a" | "b" | "c" | "d" | "e" | "f" | "g" , [ accidental ] ;
accidental   = "#" | "b" | "♭" | "n" | "♮" ;
octave       = "*" number | "*" "+" { "+" } | "*" "-" { "-" } ;
modifier     = "!" | "x" | "_" ;
chord        = [ number ] root quality [ "." style ] [ "/" bass ]
               [ "*" number ] [ modifier ] ;
root         = "A" | "B" | "C" | "D" | "E" | "F" | "G" , [ accidental ] ;
bass         = root ;
quality      = (* una delle qualita' della sezione 9.1 *) ;
style        = (* uno degli stili di voicing della sezione 9.3 *) ;
percussion   = [ number ] drum-name ;                           (* sezione 9.5 *)
rest         = [ number ] "r" ;
block        = [ number ] "[" atom { atom } "]" ;
atom         = note | chord | percussion ;
slide        = slide-point ">" slide-point { ">" slide-point } ;
slide-point  = [ number ] pitch [ octave ] ;
value        = "'" ( note-number [ tuplet ] [ "." [ "." ] ] | "g" | "G" )
               [ modifier ] ;                                   (* c'8.  c'8T  d'g *)
note-number  = "1" | "2" | "4" | "8" | "16" | "32" | "64" | "128" ;
number       = digit { digit } ;
```

Note sulla grammatica:

- Il **valore di nota** puo' stare prima o dopo il modificatore: `c'8!` e
  `c!'8` significano la stessa cosa. Non puo' seguire una griglia, una
  velocity o un altro comando di stato.
- In fondo a un token che suona vengono, in quest'ordine, i **segni**
  (sezione 6.11), la **forcella** (`c'2!<`, `2c*4>`), la **legatura di
  valore** `~` (sezione 6.9) e il segno della **legatura di portamento**
  `(` o `)` (sezione 6.10): `c'2$accent<~(`. Un token che finisce con `<<` o `>>` non e' mai una
  forcella. Un `(` in fondo a un token che suona non e' un gruppo: i
  gruppi cominciano con `(` o con delle cifre seguite da `(`.
- In un **accordo** la qualita' e' la stringa *piu' corta* che fa tornare
  il resto del token, quindi una `x` finale e' il modificatore di
  stoppato (`Cmaj7x`). Dopo uno stile di voicing, una `x` finale e' il
  modificatore se lo stile senza di essa esiste e quello con la `x` no
  (`C.drop2x` e' `drop2` stoppato, `C.hendrix` e' lo stile `hendrix`).
- Dopo `/` viene il **basso** alternativo (`C/E`); l'ottava si scrive
  sempre con `*` (`C7*3`, `C/E*3`).
- Le lettere minuscole a-g sono note; una parola minuscola che non e' una
  nota, una pausa o un comando e' il nome di una **percussione** e DEVE
  essere uno dei nomi della sezione 9.5.
- In un blocco gli atomi sono separati da spazi e NON DEVONO contenere
  `|`, valori di nota o altri blocchi.
- Un `;` fuori da un blocco di voci non appartiene a nessuna regola e
  rende il token non valido.
- Un token `$` seguito da un nome minuscolo e' un segno di navigazione
  (sezione 8.11) quando sta da solo, un segno sulla nota (sezione 6.11) in
  fondo a un token che suona; `$` seguito da una lettera maiuscola A-G e'
  una sigla d'accordo (sezione 8.10).

---

## 4. Tempo e stato

Una traccia si interpreta **da sinistra a destra** con un *cursore* (il
tempo corrente, che parte da 0) e uno **stato corrente**:

| Stato | Valore iniziale | Cambiato da |
| --- | --- | --- |
| unita' di griglia | 1 quarto (come dopo `4:`) | comandi di griglia |
| velocity | 80 | comandi di velocity |
| valori delle automazioni | `vol` 100, `expr` 127, `pan` 0, `mod` 0, `rev` 0, `cho` 0, `bend` 0, `tune` 0, `ccN` 0 | comandi di automazione (sezione 7.5) |
| swing | spento | comandi di swing (sezione 7.6) |
| spostamento | 0 ms | `shift=` (sezione 7.7) |
| trasposizione | 0 semitoni | `transpose=`, `%Nome+N` (sezione 7.8) |
| modo delle altezze | `abs:` | `rel:` / `abs:` (sezione 5) |
| tonalita' | nessuna (`key=off`) | `key=` (sezione 5) |
| ottava di default | quella dello strumento (4 se manca) | — |

**Griglia.** `N:` imposta l'unita' a 4/N quarti: `4:` semiminima, `8:`
croma, `16:` semicroma, `2:` minima, `1:` semibreve; vale qualunque N
positivo (`12:` e' una croma di terzina). Una lettera dopo N fa una
griglia a **tuplet**: `T` moltiplica l'unita' per 2/3 (terzine), `Q` per
4/5 (quintine), `S` per 4/7 (settimine), `D` per 3/2 (duine: due note
nel tempo di tre, come in 6/8). `N` DEVE essere positivo.

**Durata.** Un token che suona dura `moltiplicatore × unita'`, dove il
moltiplicatore e' il numero iniziale (1 se manca) e l'unita' e' quella di
griglia, o il **valore di nota** se il token ne ha uno (sezione 6.6). Poi
il cursore avanza della durata. Comandi di stato, controlli di battuta e
testi cantati non occupano tempo.

**Eredita'.** Con quale stato comincia ogni parte del testo, e dove
finiscono i cambi fatti dentro:

| Contesto | Comincia con | I cambi fatti dentro |
| --- | --- | --- |
| gruppo di ripetizione `N(...)` | lo stato corrente | continuano dopo (il gruppo e' scritto per esteso) |
| pattern `%Nome`, riferimento MIDI `&"Nome"` | lo stato corrente, tranne: modo `abs:`, nessuna tonalita', nota precedente azzerata (sezione 8.2); trasposizione = quella corrente piu' il `+N`/`-N` del riferimento | modo, tonalita', nota precedente e `transpose=` finiscono col riferimento; griglia, velocity, automazioni, swing e spostamento continuano dopo |
| blocco di voci `{ ; }` | ogni voce: lo stato corrente | restano nella voce; dopo il blocco lo stato e' quello di prima |
| box (file di brano, sezione 12.4) | lo stato iniziale, con `reset:`; i valori delle automazioni continuano dal box prima | finiscono col box |
| `reset:` | — | griglia, velocity, swing, spostamento, trasposizione (`transpose=`), modo, tonalita' e nota precedente tornano ai valori iniziali (sezione 7.9) |

---

## 5. Altezze

Una nota e' una lettera `a`-`g` con un'alterazione facoltativa: `#`
(diesis), `b` o `♭` (bemolle),
`n` o `♮` (bequadro). `b` da sola e' la nota Si; `bb` e' Si bemolle.

**Tonalita'.** `key=K` (K una tonalita' come in `key=G`, `key=Bb`,
`key=F#m`) da' a ogni nota successiva **senza** alterazione
l'alterazione di K: con `key=G`, `f` e' Fa diesis; con `key=Dm`, `b` e'
Si bemolle. Un'alterazione scritta vale solo per la sua nota (non si
trascina fino alla fine della battuta); `n` o `♮` toglie quella della
tonalita' (`fn` e' Fa con `key=G`). `key=off` (lo stato iniziale) non da'
alterazioni. L'armatura di K e' un numero n: per la lettera F −1, C 0,
G 1, D 2, A 3, E 4, B 5, piu' 7 per `#`, meno 7 per un bemolle, meno 3
per `m`. Con n > 0 sono diesis le prime n lettere di F C G D A E B, con
n < 0 sono bemolli le prime −n di B E A D G C F; |n| > 7 e' un errore.
La tonalita' non vale per gli accordi, le cui sigle sono assolute.

**Ottava.** `*n` da' l'ottava esplicita: `c*4` e' il Do centrale. Senza,
l'ottava dipende dal **modo delle altezze**:

- `abs:` (assoluto, lo stato iniziale): l'ottava di default dello
  strumento. `*+` e `*-` sono errori.
- `rel:` (relativo): l'ottava che mette la nota **piu' vicina** alla
  precedente contando le lettere, cioe' al piu' una quarta sopra o sotto
  (dopo `b`, `c` sale; dopo `c`, `g` scende); poi ogni `+` di `*+`, `*++`... la alza di
  un'ottava e ogni `-` di `*-`, `*--`... la abbassa. La nota precedente e' l'ultima nota o
  tappa di slide letta, ottave esplicite comprese; dopo un blocco `[...]`
  e' la prima nota del blocco; accordi e percussioni non contano. `rel:`
  parte dal Do dell'ottava di default (quindi la prima nota e' quella
  piu' vicina a lui).

`rel:` e `abs:` possono stare ovunque; ogni `rel:` riparte dal Do
dell'ottava di default. Il numero di nota MIDI e'

```
midi = (ottava + 1) × 12 + pc(lettera) + alterazione
pc: c=0 d=2 e=4 f=5 g=7 a=9 b=11      alterazione: # = +1, bemolle = -1
```

senza riportarlo nell'ottava: `cb*4` e' il Si3 (59) e `b#*4` il Do5 (72).
Una nota fuori dall'intervallo MIDI 0-127 e' un errore (la piu' acuta e'
`g*9`).

---

## 6. Token che suonano

Ogni token che suona produce un **evento** nel punto del cursore, con la
velocity corrente, e fa avanzare il cursore della sua durata.

### 6.1 Note

`c`, `f#*5`, `2eb`: una sola altezza (evento di tipo `note`).

### 6.2 Accordi

`C`, `Am7`, `G7/B*3`, `Cmaj7.drop2`: un accordo astratto (tipo `chord`)
con la sigla (fondamentale + qualita'), lo stile di voicing, il basso e
l'ottava facoltativi. Come l'accordo diventa note e' descritto nella
sezione 9.

### 6.3 Percussioni

`kick`, `2snare`: un suono di batteria (tipo `percussion`) dalla tabella
della sezione 9.5.

### 6.4 Pause

`r`, `3r`: silenzio (tipo `rest`).

### 6.5 Blocchi

`[c*4 e*4 g*4]`, `2[kick hihat]`, `[C e*5]`: note, accordi e percussioni
che iniziano e finiscono insieme (tipo `block`). La durata e' data dal
moltiplicatore (e dal valore) del blocco, non dagli atomi; i
moltiplicatori dentro gli atomi si ignorano.

### 6.6 Valori di nota

Un valore dopo `'` da' direttamente la durata, al posto dell'unita' di
griglia: il numero e' la figura (1 semibreve = 4 quarti, 2 minima, 4
semiminima, 8 croma, 16, 32, 64, 128), una lettera di tuplet la scala come
una griglia a tuplet, e uno o due punti la moltiplicano per 3/2 o 7/4:

| Token | Quarti |
| --- | --- |
| `c'4` | 1 |
| `c'8.` | 3/4 |
| `c'2..` | 7/2 |
| `c'8T` | 1/3 |
| `c'8D` | 3/4 |
| `2c'8` | 1 |

Il valore vale **solo per quel token**: la griglia non cambia. Vale per
note, accordi, blocchi, pause, percussioni e slide. I valori `'g` e `'G`
sono note di abbellimento (sezione 6.12).

### 6.7 Articolazione

Un `!` (staccato), una `x` (stoppato) o un `_` (legato) finale su una nota
o un accordo ne imposta l'articolazione. Non cambia la durata
dell'evento (il tempo che occupa); per come suona vedi la sezione 13.

### 6.8 Slide

`c*4>d*4` (tipo `slide`): un portamento continuo attraverso due o piu'
altezze (*tappe*). Siano le tappe p₁…pₙ con moltiplicatori facoltativi
m₁…mₙ. I segmenti sono n:

- per i < n, il segmento i e' la rampa dalla tappa i alla i+1 e dura
  `(mᵢ o 1) × unita'`;
- il segmento n e' la tenuta sull'altezza finale e dura `(mₙ o 0) × unita'`.

Cosi' `c*4>d*4` dura un'unita' come una nota, `c*4>d*4>c*4` (sale e
rilascia) due, `2c*4>3d*4` sale in 2 unita' e resta ferma per 3. Uno
slide di durata totale 0 e' un errore.

L'evento porta la prima altezza, le tappe successive e le durate dei
segmenti.

### 6.9 Legature di valore

Un `~` in fondo a una nota, un accordo o un blocco lo **lega** al
successivo token che suona, che DEVE essere la stessa nota (la stessa
altezza MIDI: `c#~ db` va bene), lo stesso accordo (sigla, ottava, stile,
basso) o lo stesso blocco (gli stessi atomi, in qualunque ordine). I due
fanno **un solo** evento: l'inizio del primo, la somma delle durate,
l'articolazione dell'ultima parte se ne ha una. In mezzo possono esserci
controlli di battuta, commenti, testo cantato e comandi di stato (valgono
come sempre, ma l'evento legato tiene la sua velocity); `c~ | c` e' il
modo normale di tenere una nota oltre la stanghetta. Una catena
`c~ c~ c` lega tre parti.

E' un errore legare una pausa, una percussione o uno slide, legare a una
nota diversa o a una pausa, lasciare una legatura senza la nota che la
continua, o avere un blocco di voci fra le due parti.

### 6.10 Legature di portamento

Un `(` in fondo a un token che suona apre una **legatura di portamento**,
un `)` in fondo a uno successivo la chiude: `c( d e f)`. Ogni nota,
accordo, blocco o slide dall'apertura alla chiusura riceve il campo
`slur`: `start` il primo, `stop` l'ultimo, `continue` gli altri (pause e
percussioni in mezzo non ne fanno parte; un evento legato conta una
volta). Una legatura DEVE contenere almeno due eventi, le legature non si
annidano, e una legatura DEVE chiudersi nello stesso testo di traccia o
nella stessa voce in cui si apre, senza blocchi di voci in mezzo. Gli
eventi sotto la legatura senza un'articolazione propria suonano legati
(sezione 13), tranne l'ultimo.

Dentro un gruppo le parentesi delle legature fanno parte del conteggio
delle parentesi del gruppo: `2(c( d) e)` ripete una coppia legata.

### 6.11 Segni

Un `$nome` in fondo a un token che suona (dopo il valore) aggiunge un
**segno**; piu' segni si possono mettere di seguito (`c$accent$tenuto`).
L'evento riceve il campo `decorations` con i nomi nell'ordine in cui
sono scritti (un evento legato raccoglie i segni di tutte le sue parti,
una volta ciascuno):

| Segno | Significato | Suono (sezione 13) |
| --- | --- | --- |
| `$accent` | accento | piu' forte |
| `$marcato` | accento forte | ancora piu' forte |
| `$tenuto` | tenuto | come scritto |
| `$fermata` | corona (anche su una pausa) | tutto il brano aspetta: durata doppia |
| `$tr` | trillo | alterna la nota e quella sopra nella tonalita' |
| `$mordent` | mordente | nota, quella sotto nella tonalita', nota |
| `$turn` | gruppetto | sopra, nota, sotto, nota |
| `$arp` | arpeggio (accordo arpeggiato) | le note di un accordo o di un blocco entrano una dopo l'altra, dalla piu' grave |
| `$staccatissimo` | staccatissimo | molto breve (un quarto della durata) |
| `$sfz` | sforzando | piu' forte di `$marcato` |
| `$fp` | forte-piano | attacco piu' forte, come `$accent` |
| `$trem` | tremolo (sulla batteria: rullata) | la nota ribattuta a biscrome |
| `$harmonic` | armonico | come scritto |

Un nome sconosciuto e' un errore; su una pausa va solo `$fermata`. I
segni non cambiano `start`, `duration` e `velocity` dell'evento.

### 6.12 Note di abbellimento

Una nota, un accordo, un blocco o una percussione con il valore `'g` e'
un'**acciaccatura**, con `'G` un'**appoggiatura**: `d'g c`, `[c e]'G C`,
`snare'g snare` (un flam). Un abbellimento **non occupa tempo scritto**:
il suo evento ha `duration` 0, comincia nel punto del cursore e ha il
campo `grace` (`acciaccatura` o `appoggiatura`); il cursore non si
sposta. Piu' abbellimenti possono precedere la stessa nota (`c'g d'g e`).
Si suona subito prima della nota che segue (sezione 13).

Un abbellimento DEVE essere seguito dalla nota, dall'accordo, dal blocco
o dalla percussione che abbellisce: prima di una pausa, di un blocco di
voci o della fine del testo e' un errore, come lo sono una legatura di
valore o una forcella su di esso, una legatura di valore che vi arriva e
un valore di abbellimento su una pausa o su uno slide. Una legatura di
portamento puo' cominciare su un abbellimento (`d'g( c)`). Gli
abbellimenti non prendono sillabe (sezione 8.5) e una rampa di velocity
(sezione 7.3) non li conta.

---

## 7. Comandi di stato

### 7.1 Velocity e dinamiche

`N@` imposta la velocity (1-127; fuori e' un errore). Le dinamiche
classiche sono velocity fisse:

| pppp | ppp | pp | p | mp | mf | f | ff | fff | ffff |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 23 | 36 | 49 | 62 | 75 | 88 | 101 | 114 | 127 |

### 7.2 Tempo

`tempo=N` imposta il tempo (battiti al minuto, 1-999; fuori e' un errore)
dal cursore in poi. Produce un
evento di tipo `tempo_marker` con `bpm` = N. Il tempo e' globale: un
marcatore in una traccia qualsiasi cambia il tempo di tutto il brano.

N puo' avere decimali (`tempo=72.5`). Un valore di nota dopo N dice la
figura che si conta: `tempo=60'4.` sono 60 semiminime puntate al minuto,
`tempo=40'2` 40 minime (il valore e' una figura con punti facoltativi,
senza lettera di tuplet). `bpm` e' sempre in quarti al minuto
(`tempo=60'4.` da' 90) e DEVE stare in 1-999; l'evento riceve anche il
campo `beat_unit` con il valore come scritto (`4.`), per la partitura.
`bpm` e' un intero quando lo e'.

### 7.3 Rampe

`>>` o `<<` (equivalenti: la direzione viene dai valori) apre una
**rampa**. L'ultimo comando di stato prima di essa DEVE essere una
velocity, un tempo o un'automazione (possono esserci in mezzo token che
suonano, non un comando di griglia), altrimenti e' un errore. Una rampa
di velocity o di tempo si chiude al successivo comando **dello stesso
tipo** (i comandi di griglia dentro la rampa non la chiudono), e DEVE
essere chiusa prima di un comando di velocity o di tempo dell'altro tipo
e prima della fine della traccia. Le rampe delle automazioni sono
descritte nella sezione 7.5.

Una **curva** facoltativa dopo le frecce da' la forma f(x) della rampa,
per x da 0 (inizio) a 1 (fine):

| Curva | f(x) | Uso |
| --- | --- | --- |
| `lin` (default) | x | cambio regolare |
| `exp` | x² | parte piano, poi accelera (i fade dei volumi) |
| `log` | 1 − (1 − x)² | parte veloce, poi rallenta |
| `s` | x² (3 − 2x) | morbida all'inizio e alla fine |

- **Rampa di velocity** (crescendo/diminuendo): siano e₀…eₖ₋₁ (k eventi)
  gli eventi prodotti fra apertura e chiusura, esclusi gli eventi
  `control`, `repeat`, `text` e `harmony` e le note di abbellimento. L'evento i riceve `round(v₀ + (v₁ - v₀) × f(i / (k-1)))`
  (con k = 1: il valore finale), dove v₀ e' la velocity all'apertura e
  v₁ il valore di chiusura, limitato a 1-127.
- **Rampa di tempo** (accelerando/rallentando): per ciascuno di quegli
  eventi, un `tempo_marker` al suo inizio con il tempo interpolato (stessa
  formula; se il valore iniziale o quello finale ha decimali, il risultato
  si arrotonda a 2 decimali invece che all'intero). Senza eventi in mezzo,
  un solo marcatore con il valore finale nel punto del cursore.

### 7.4 Pedale del sustain

`SON` e `SOFF` producono eventi di tipo `sustain` (nome `on`/`off`) nel
punto del cursore.

### 7.5 Automazioni

`nome=N` imposta un **valore di automazione** della traccia dal cursore
in poi. Le automazioni agiscono su tutto lo strumento (nel MIDI, sul suo
canale), non sulle singole note, e cambiano con continuita' anche
durante una nota tenuta:

| Nome | Significato | Intervallo | Iniziale |
| --- | --- | --- | --- |
| `vol` | volume | 0-127 | 100 |
| `expr` | espressione (il volume dentro la dinamica) | 0-127 | 127 |
| `pan` | posizione stereo, −1 sinistra, 0 centro, 1 destra | −1..1 | 0 |
| `mod` | modulazione (vibrato) | 0-127 | 0 |
| `rev` | mandata al riverbero | 0-127 | 0 |
| `cho` | mandata al chorus | 0-127 | 0 |
| `bend` | pitch bend, in semitoni | −24..24 | 0 |
| `tune` | accordatura dello strumento, in cent | −100..100 | 0 |
| `ccN` | controller MIDI N (0-119), es. `cc74` | 0-127 | 0 |

Un valore fuori dall'intervallo, o `ccN` con N > 119, e' un errore. `pan`
e `bend` tengono i decimali, gli altri valori sono arrotondati all'intero
piu' vicino (`vol=80.6` e' 81).

Senza rampa, `nome=N` produce un evento `control` nel punto del cursore
con `name`, `value` = N e durata 0. Una rampa (sezione 7.3) subito dopo
apre una **rampa di automazione**: la chiude il successivo comando con
lo **stesso nome**, che produce invece un solo evento `control` dalla
posizione di apertura al cursore (durata = la differenza), con
`start_value` = il valore all'apertura, `value` = N e `curve` (di
default `lin`). Se il cursore non si e' mosso, e' un semplice cambio di
valore (durata 0, senza `start_value`). Le rampe di nomi diversi sono
indipendenti e possono sovrapporsi; i comandi di velocity e di tempo non
le chiudono. Una rampa di automazione ancora aperta alla fine della
traccia (o di una voce) e' un errore.

**Forcelle.** Un `<` finale su un token che suona e' un crescendo su
quell'evento, `>` un diminuendo, fatti con l'espressione. Siano E il
valore corrente di `expr`, H = round(E / 2), s e d inizio e durata
dell'evento. Una forcella produce, dopo l'evento:

1. un evento `control` `expr` in s, durata d, `start_value` H e `value`
   E per `<` (E poi H per `>`), curva `lin`;
2. un evento `control` `expr` in s + d, durata 0, `value` E
   (l'espressione torna al suo valore).

Una forcella dentro una rampa di `expr` aperta e' un errore.

### 7.6 Swing

`swing=N` (N da 50 a 80) fa lo swing delle crome dal cursore in poi:
dentro ogni battito la prima meta' si allunga fino a N % del battito e la
seconda si accorcia di conseguenza. `swing16=N` fa lo stesso con le
semicrome dentro ogni mezzo battito. `swing=50` (o `swing16=50`) toglie
lo swing. Fuori da 50-80 e' un errore.

Lo swing non cambia `start` e `duration` degli eventi (i controlli di
battuta e la partitura restano diritti): ogni evento che suona prodotto
con lo swing attivo riceve il campo `swing` = [coppia, rapporto], dove
*coppia* e' 1 (crome) o 0,5 (semicrome) e *rapporto* e' N / 100. Il
tempo in cui suona un istante t e' poi, con k = ⌊t / coppia⌋ e
x = t / coppia − k:

    k + 2·rapporto·x                          se x ≤ 1/2
    k + rapporto + 2·(1 − rapporto)·(x − 1/2) altrimenti

il tutto moltiplicato per *coppia*; si applica all'inizio e alla fine di
ogni evento (sezione 13). Un blocco di voci eredita lo swing in vigore.

### 7.7 Micro-tempo

`shift=N` (N da −500 a 500, intero) fa suonare gli eventi sonori che
seguono N **millisecondi** dopo (N > 0) o prima (N < 0) di dove sono
scritti, senza cambiare il ritmo scritto; `shift=0` li riporta a tempo.
Fuori da −500..500, o un numero con decimali, e' un errore.

Come lo swing, lo spostamento non cambia `start` e `duration` (i
controlli di battuta e la partitura tengono il ritmo scritto): ogni
evento sonoro prodotto mentre lo spostamento non e' 0 ha il campo
`shift` = N. Chi suona sposta l'intero evento (inizio e fine) di N ms,
convertiti in quarti con il tempo in vigore all'inizio sonoro
dell'evento (dopo lo swing), e mai prima dell'inizio del brano. Un blocco
di voci eredita lo spostamento in vigore.

`shift=` serve per il feeling (un rullante un po' dietro il tempo, un
basso che spinge in avanti) e per allineare una parte a una
registrazione; per i ritmi scritti si usano valori di nota, gruppi
irregolari e swing.

### 7.8 Trasposizione

`transpose=N` (N intero da −60 a 60) fa suonare **note, accordi, slide e
blocchi** che seguono N semitoni sopra (N > 0) o sotto (N < 0) rispetto a
come sono scritti; `transpose=0` torna all'altezza scritta. Gli eventi
portano l'altezza trasposta: `letter` e `octave` di una nota, la
fondamentale (`symbol`), `bass` e `octave` di un accordo, i punti di uno
slide e gli elementi di un blocco. Le percussioni, le pause e tutto cio'
che non e' un'altezza non cambiano. Le ottave relative (`rel:`, sezione 5)
si leggono sulle note scritte e la trasposizione si applica dopo; un
blocco di voci eredita la trasposizione in vigore.

**Scrittura.** Se c'e' una tonalita' (`key=K`), le note trasposte si
scrivono nella tonalita' trasposta: `key=G` e `transpose=2` danno La
maggiore, quindi un fa diesis scritto diventa sol diesis e un sol diventa
la; una tonalita' con i bemolli da' bemolli. Senza tonalita', una nota
trasposta prende un bemolle se la nota scritta lo aveva e un diesis negli
altri casi. Fondamentale e basso di un accordo seguono la stessa regola.
Un accordo la cui fondamentale scavalca il Do cambia ottava (`B` +1 e' `C`
un'ottava sopra): una trasposizione di 12 alza quindi ogni accordo di
un'ottava.

Una nota o un accordo che la trasposizione porta fuori da MIDI 0-127, o un
N fuori da −60..60, e' un errore.

**Pattern.** `%Nome+N` e `%Nome-N` (e `K%Nome+N`) leggono il pattern
trasposto di N semitoni **in aggiunta** alla trasposizione in vigore
(sezione 8.2); il numero segue il nome senza spazi. Lo stesso vale per i
riferimenti MIDI della sezione 8.3 (`&"Nome"+7`).

### 7.9 Reset

`reset:` rimette lo **stato iniziale** della sezione 4: unita' di griglia
1 quarto, velocity 80, swing spento, spostamento 0, trasposizione di
`transpose=` 0, modo `abs:`, nessuna tonalita', nota precedente
azzerata. Non occupa tempo e non produce eventi. **Non** cambia:

- i valori delle automazioni (sezione 7.5): agiscono su tutto il canale,
  e riportarli indietro produrrebbe degli eventi;
- la trasposizione che viene dal riferimento del pattern che lo contiene
  (`%Nome+N`): dentro quel pattern la trasposizione torna a N.

`reset:` con una rampa di velocity o di tempo aperta e' un errore, e una
rampa non puo' seguirlo direttamente (sezione 7.3). E' cio' con cui
comincia un box (sezione 12.4), ed e' il modo per rendere un testo
indipendente da quello che c'e' prima.

---

## 8. Struttura

### 8.1 Gruppi di ripetizione

`N(token)` ripete il contenuto N volte (1 se manca il numero), come se i
token fossero scritti per esteso. I gruppi si annidano. Si espandono
prima dell'interpretazione, quindi lo stato impostato in un gruppo resta
anche dopo. Con N ≥ 2 le ripetizioni sono segnate da eventi `repeat`
come nella sezione 8.7 (`start` prima della prima, `again` con il numero
del passaggio prima delle altre, `end` dopo l'ultima), perche' una
partitura possa scriverle come ritornello.

### 8.2 Pattern

`%Nome` inserisce i token del pattern `Nome` (definito nel brano, sezione
12); `N%Nome` li inserisce N volte. Un pattern puo' richiamarne altri;
una catena di riferimenti piu' profonda di 32 livelli (o un ciclo) e' un
errore, come un pattern non definito. Le note di un pattern si leggono
nello stato iniziale delle altezze (`abs:`, nessuna tonalita') qualunque
sia il modo della traccia, e dopo il riferimento modo, tonalita' e nota
precedente della traccia sono quelli di prima: un pattern suona uguale
in ogni traccia.

Fa eccezione la **trasposizione** (sezione 7.8): un pattern si legge alla
trasposizione in vigore nel punto del riferimento, piu' il numero scritto
dopo il nome (`%Riff+7`, `3%Riff-12`). Un `transpose=` dentro il pattern
vale rispetto a quel riferimento e finisce con esso.

### 8.3 Riferimenti MIDI

`&"Nome"` (e `N&"Nome"`) inserisce i token convertiti da un file MIDI di
una libreria. Il nome del file si scrive sempre **fra virgolette**: puo'
contenere sottocartelle, trattini e spazi (`&"Blues/bass-line"`,
`&"intro take 2"`), e niente di quello che sta fuori dalle virgolette ne
fa parte. E' una funzione **facoltativa** dell'applicazione che ospita il
parser: un parser senza libreria DEVE segnalare questi riferimenti come
errore.

Un riferimento MIDI si trasporta come un pattern: `&"Nome"+N` legge il
file N semitoni sopra, in aggiunta alla trasposizione in vigore (sezione
7.8), e `&"Nome"-N` sotto. I token del file si leggono nello stato
iniziale delle altezze, come quelli di un pattern, e la trasposizione
finisce col riferimento.

Un riferimento senza virgolette (`&Nome`, la forma delle versioni prima
della 2.6) e' un errore. Un lettore dei file di brano DOVREBBE convertirlo
quando legge un file (sezione 12): `&Nome` e `&Nome+N` diventano `&"Nome"`
e `&"Nome"+N`; per un `-N` finale senza `+` vale la regola della 2.5 (il
nome per intero se la libreria ha un file che si chiama cosi', altrimenti
il nome senza `-N` trasposto di N semitoni sotto). Siccome la forma senza
virgolette non e' mai un testo valido, la conversione non cambia mai il
significato di un testo valido.

### 8.4 Blocchi di voci

`{ v₁ ; v₂ ; … }` contiene **voci** che partono insieme nel punto del
cursore. Ogni voce e' una sequenza di token interpretata per conto suo:

- parte con l'unita' di griglia, la velocity, lo swing, lo spostamento,
  i valori delle automazioni, il modo delle altezze, la tonalita' e la nota precedente
  correnti (e l'ottava di default); i cambi di stato dentro
  una voce restano li', tranne i valori delle automazioni (sezione 7.5),
  che sono di tutta la traccia;
- i suoi eventi partono dalla posizione del blocco; la voce k (contando
  da 1) di un blocco che si trova nella voce v ha numero v + k - 1 (il
  livello principale e' la voce 1);
- il blocco dura quanto la voce piu' lunga; poi il cursore avanza di
  tanto e lo stato dopo il blocco e' quello di prima, tranne che ogni
  valore di automazione e' quello dell'evento `control`, in una voce
  qualsiasi, che finisce per ultimo (a pari fine vince la voce prima);
- un blocco con sole voci vuote e' un errore.

Le voci possono contenere gruppi, riferimenti a pattern, controlli di
battuta, testi cantati e altri blocchi di voci. I pattern si espandono
dentro ciascuna voce.

### 8.5 Testo cantato

Un token di testo `"…"` contiene sillabe separate da spazi, assegnate in
ordine agli **eventi cantati** che lo precedono dopo il testo precedente
(o dall'inizio): note, accordi, slide e blocchi con almeno una nota o un
accordo — non pause, non percussioni.

- `*` lascia il suo evento senza sillaba.
- `_` segna l'evento come prolungamento della sillaba precedente
  (melisma); il campo `lyric` dell'evento vale `_`.
- Una sillaba che finisce con `-` continua la parola nella sillaba dopo.
- Un testo attaccato a una nota (`c"la"`) e' semplicemente il token
  successivo: prende le note in attesa dal testo precedente.
- Un testo dentro un gruppo si ripete con il gruppo.
- La prima voce di un blocco di voci condivide gli eventi in attesa con
  il testo intorno: un testo dopo il blocco copre anche gli eventi della
  prima voce, e un testo dentro la prima voce copre anche gli eventi in
  attesa prima del blocco.
- Piu' sillabe che eventi in attesa e' un **avviso** (sezione 10.2); le
  sillabe in piu' si ignorano.

Le sillabe vanno nel campo `lyric` dell'evento.

**Strofe.** Un testo che comincia con una cifra 1-9, i due punti e uno
spazio appartiene a quella strofa: `"2: Ev- ry where that Ma- ry went"`;
senza numero (o con `1:`) e' la strofa 1, come sopra. Ogni strofa ha i
suoi eventi in attesa: un testo della strofa N prende gli eventi cantati
dal testo precedente della strofa N (o dall'inizio), cosi' le strofe si
possono scrivere una dopo l'altra sotto la stessa musica. La prima voce di
un blocco di voci li condivide con il testo intorno, come per la strofa
1. Le sillabe dalla strofa 2 in poi vanno nel campo `verses` dell'evento,
un oggetto dal numero della strofa alla sillaba (`{"2": "lo"}` nella
suite di conformita'); le regole per `*`, `_` e `-` sono le stesse.

### 8.6 Controlli di battuta

`|` dichiara che nel punto del cursore finisce una battuta. Non occupa
tempo e, se non torna, non e' un errore ma un **avviso** (sezione 10.2).
Dentro un blocco `[...]` e' un errore. Anche i token dei ritornelli della
sezione 8.7 sono controlli di battuta.

### 8.7 Ritornelli

I ritornelli si scrivono come in partitura e si espandono prima
dell'interpretazione, dopo pattern e gruppi:

    |: corpo :|                           corpo due volte
    |: corpo |1. fine1 :| |2. fine2 ||    corpo fine1 corpo fine2

- `|:` apre la parte da ripetere; se manca, la parte comincia
  dall'inizio del testo (o della voce), o dopo il ritornello precedente.
- Senza caselle, `:|` chiude la parte, che si suona due volte.
- Con le caselle, il corpo e' seguito da `|1.`; la casella k si chiude con
  `:|` e DEVE essere seguita da `|k+1.` (`:|2.` equivale a `:| |2.`);
  l'ultima casella si chiude con `||` o con la fine del testo. I
  passaggi sono tanti quante le caselle, almeno due.
- I ritornelli non si annidano. `|:`, `:|`, `|N.` e `||` sono controlli di
  battuta.
- Nel modo relativo ogni passaggio riparte dalla nota precedente che il
  ritornello aveva all'inizio (cosi' ogni passaggio ha le stesse altezze),
  e ogni casella riparte dalla nota che chiude il corpo; lo stesso vale per
  i passaggi di un gruppo `N(...)`.

L'espansione inserisce nel punto del cursore eventi di tipo `repeat`
lunghi zero: `start` prima del primo passaggio, `again` (con `value` = il
numero del passaggio) prima di ciascuno dei successivi, `ending` (con
`value` = il suo numero) prima di ogni casella, `end` dopo l'ultimo
passaggio. Un `||` fuori da un ritornello e' solo un controllo di
battuta. Un ritornello aperto, chiuso due volte, numerato male o con una
sola casella e' un errore.

### 8.8 Indicazioni di testo

`$"testo"` mette un'**indicazione di testo** (rit., dolce, a tempo…) nel
punto del cursore: un evento di tipo `text` con `name` = il testo e
durata 0. Non cambia il suono: tempo e dinamica cambiano con i loro
comandi.

### 8.9 Ancore di battuta

`bar=N` (N intero da 1 a 99999) porta il cursore all'**inizio della
battuta N** del brano, con le stesse posizioni delle battute dei controlli
di battuta (sezione 12.3: la battuta 1 comincia al quarto 0, o dopo la
battuta in levare se il brano ne ha una; ogni battuta dura
`4 × num / den` quarti della metrica in vigore).

- Se il cursore e' **prima** di quel punto, il vuoto si riempie di
  silenzio: un evento di tipo `rest` dal cursore all'inizio della battuta
  N, con la velocity in vigore, e il cursore si sposta sull'ancora. Una
  legatura (`~`) non puo' arrivare a un'ancora che richiede un silenzio
  (errore).
- Se il cursore e' **esattamente** li', non succede nulla.
- Se il cursore e' **gia' oltre**, il testo resta valido e il cursore resta
  dov'e' (un'ancora non torna mai indietro); si segnala con un avviso
  (sezione 10.2).

L'ancora serve a dire dove entra una parte (`bar=29`) senza contare a mano
le pause, e a scoprire una parte che si e' spostata rispetto alle battute
su cui era pensata. Non ha una durata propria: non cambia alcuno stato ne'
la griglia. Dentro un pattern o un gruppo ripetuto si valuta a ogni
ripetizione, nella posizione assoluta del brano; in un blocco di voci ogni
voce raggiunge la battuta partendo dall'inizio del blocco.

### 8.10 Sigle d'accordo

`$Am7`, `$G7/B`: una **sigla d'accordo** scritta sopra il pentagramma,
che non suona (l'armonia di un lead sheet sopra una melodia). E' un
evento di tipo `harmony` nel punto del cursore, con `symbol` e `bass` e
durata 0. La qualita' DEVE essere una della sezione 9.1. Una
trasposizione in vigore (sezione 7.8) la traspone come un accordo.

### 8.11 Navigazione: D.C., D.S., Coda, Fine

I segni di una partitura che fanno tornare indietro si scrivono come
token:

| Token | Segno |
| --- | --- |
| `$segno` | 𝄋 segno |
| `$coda` | 𝄌 coda (dove comincia la coda) |
| `$tocoda` | "alla Coda": nella ripresa, da qui si salta a `$coda` |
| `$fine` | Fine: nella ripresa ci si ferma qui |
| `$dc` | D.C. (da capo): si torna all'inizio |
| `$ds` | D.S. (dal segno): si torna a `$segno` |

Come i ritornelli, si espandono prima dell'interpretazione (dopo aver
letto pattern, gruppi e ritornelli):

    A $fine B $dc                       A B A
    $segno A $tocoda B $ds $coda C      A B A C

- Il testo si suona fino a `$dc` o `$ds`; poi dall'inizio (`$dc`) o da
  `$segno` (`$ds`) fino a `$fine`, oppure fino a `$tocoda` e poi da
  `$coda` alla fine, oppure, senza nessuno dei due, di nuovo fino al
  salto.
- Nella ripresa i ritornelli si suonano una volta, con l'ultima casella
  (sezione 8.7), come si usa; i passaggi dei gruppi `N(...)` si suonano
  come sono scritti.
- Nel modo relativo la ripresa riparte dalla nota precedente che il testo
  aveva nel punto a cui si torna, e la coda da quella prima del salto.
- Un testo ha al piu' un `$dc` o `$ds`. E' un errore scrivere un `$ds`
  senza un `$segno` prima, sia `$fine` sia `$tocoda`, un `$fine` o un
  `$tocoda` che non sta fra il punto a cui si torna e il salto, un
  `$tocoda` senza un `$coda` dopo il salto, un `$coda` dopo il salto senza
  un `$tocoda`, e musica dopo il salto fuori dalla coda (possono seguirlo
  solo controlli di battuta).
- Senza `$dc` o `$ds` i segni marcano soltanto la partitura.

L'espansione inserisce eventi di durata nulla di tipo `navigation` con
`name` = il segno, nell'ordine in cui si suonano: `segno`, `coda`,
`tocoda`, `fine` dove si incontrano la prima volta; il salto come `dc` o
`ds`, seguito da `_fine` o `_coda` quando la ripresa finisce a `$fine` o
alla coda (`ds_coda`: "D.S. al Coda"); nella ripresa solo il `fine`
finale, oppure il `tocoda` e il `coda` dove comincia la coda.

---

## 9. Accordi e percussioni

### 9.1 Qualita' degli accordi

Una sigla e' una fondamentale (A-G con alterazione facoltativa) piu' una
qualita'. Gli intervalli sono semitoni sopra la fondamentale:

| Qualita' | Intervalli | | Qualita' | Intervalli |
| --- | --- | --- | --- | --- |
| (nessuna), `maj` | 0 4 7 | | `m6` | 0 3 7 9 |
| `m`, `min` | 0 3 7 | | `9` | 0 4 7 10 14 |
| `7` | 0 4 7 10 | | `maj9` | 0 4 7 11 14 |
| `maj7` | 0 4 7 11 | | `m9` | 0 3 7 10 14 |
| `m7`, `min7` | 0 3 7 10 | | `mMaj7` | 0 3 7 11 |
| `dim`, `°` | 0 3 6 | | `m7b5` | 0 3 6 10 |
| `dim7`, `°7` | 0 3 6 9 | | `add9` | 0 4 7 14 |
| `aug` | 0 4 8 | | `7sus4` | 0 5 7 10 |
| `sus2` | 0 2 7 | | `7b9`, `7alt` | 0 4 7 10 13 |
| `sus4` | 0 5 7 | | `7#9` | 0 4 7 10 15 |
| `6` | 0 4 7 9 | | `5` | 0 7 |
| `11` | 0 4 7 10 14 17 | | `13` | 0 4 7 10 14 21 |
| `maj13` | 0 4 7 11 14 21 | | `7#5`, `aug7` | 0 4 8 10 |
| `7b5` | 0 4 6 10 | | `m11` | 0 3 7 10 14 17 |
| `m13` | 0 3 7 10 14 21 | | `69` | 0 4 7 9 14 |
| `maj7#11` | 0 4 7 11 18 | | `7#11` | 0 4 7 10 18 |
| `9sus4` | 0 5 7 10 14 | | `7b13` | 0 4 7 10 20 |
| `add11` | 0 4 7 17 | | `madd9` | 0 3 7 14 |
| `7sus2` | 0 2 7 10 | | `sus` | 0 5 7 |
| `13b9` | 0 4 7 10 13 21 | | | |

L'accordo di sesta e nona si scrive `69` (`C69`): in `C6/9` la barra
sarebbe il basso alternativo.

Una qualita' sconosciuta e' un errore.

### 9.2 Realizzazione

E' normativo il **contenuto in classi di altezza** dell'accordo: la
fondamentale piu' gli intervalli sopra, e il basso se c'e'. Il voicing
esatto (quali ottave, quali note raddoppiate o omesse) e' **a scelta
dell'implementazione** e dipende dallo strumento; l'algoritmo di
riferimento e':

- base = MIDI(fondamentale, ottava) (sezione 5, ottava dal token o dallo
  strumento);
- stile dello strumento `monophonic`: solo la fondamentale; `root_fifth`:
  fondamentale e quinta (se la qualita' ce l'ha); altrimenti (`spread`)
  tutti gli intervalli;
- ogni nota si sposta di ottave finche' rientra nell'estensione dello
  strumento;
- con un basso `/X`: si aggiunge, sotto tutte le altre, una nota di classe
  X.

### 9.3 Stili di voicing

`.stile` dopo l'accordo chiede un voicing: stili generali `close`,
`open`, `inv1`, `inv2`, `inv3`, `shell`, `noroot`; da tastiera `left`,
`right`, `spread`; da chitarra `barre`, `Caged`, `cAged`, `caGed`,
`cagEd`, `cageD`, `drop2`, `drop3`, `triad`, `power`, `openpos`,
`hendrix`, `top`, `bottom`. Uno stile sconosciuto e' un errore. Gli stili
di un'altra famiglia di strumenti ripiegano sul generale piu' vicino (a
scelta dell'implementazione).

### 9.4 Strumenti

Lo strumento di una traccia ne da' l'ottava di default, l'estensione, lo
stile degli accordi e il programma General MIDI. Gli strumenti di base
sono:

| Nome | Programma GM | Ottava di default | Estensione (MIDI) | Stile accordi |
| --- | --- | --- | --- | --- |
| Piano | 0 | 4 | 21-108 | spread |
| Guitar | 25 | 3 | 40-88 | spread |
| Bass | 33 | 2 | 28-60 | root_fifth |
| Trumpet | 56 | 4 | 54-82 | monophonic |
| Drums | — (canale 10) | 4 | — | — |

Gli altri nomi si risolvono con una tabella di alias a scelta
dell'implementazione (es. `violin`, `electric_bass`, `drum_kit`) e con i
nomi General MIDI.

Uno strumento puo' essere **traspositore** (sezione 12.2,
`trasposizione=N`): N e' il numero di semitoni fra quello che suona e
quello che e' scritto nella sua parte (una tromba in Si♭ e' −2). Il testo
si scrive sempre in suoni reali; la trasposizione cambia solo la parte
scritta della partitura.

### 9.5 Nomi delle percussioni

| Nome | Nota GM | Nome | Nota GM | Nome | Nota GM |
| --- | --- | --- | --- | --- | --- |
| kick | 36 | kick2 | 35 | snare | 38 |
| snare2 | 40 | rimshot | 37 | clap | 39 |
| hihat | 42 | hihat_open | 46 | hihat_pedal | 44 |
| tom1 | 48 | tom2 | 45 | floor | 41 |
| tom_hi | 50 | tom_lowmid | 47 | tom_highfloor | 43 |
| crash | 49 | crash2 | 57 | ride | 51 |
| ride2 | 59 | ride_bell | 53 | china | 52 |
| splash | 55 | tambourine | 54 | cowbell | 56 |
| bongo_hi | 60 | bongo_low | 61 | conga_mute | 62 |
| conga_open | 63 | conga_low | 64 | timbale_hi | 65 |
| timbale_low | 66 | cabasa | 69 | maracas | 70 |
| claves | 75 | woodblock_hi | 76 | woodblock_low | 77 |
| side_stick | 37 | vibraslap | 58 | agogo_hi | 67 |
| agogo_low | 68 | whistle_short | 71 | whistle_long | 72 |
| guiro_short | 73 | guiro_long | 74 | cuica_mute | 78 |
| cuica_open | 79 | triangle_mute | 80 | triangle | 81 |

---

## 10. Errori e avvisi

### 10.1 Errori

Un testo con un errore **non e' valido** e non produce eventi. Un parser
conforme DEVE segnalare almeno questi errori:

- blocco, gruppo, blocco di voci o testo cantato non chiuso;
- un token che non corrisponde a nessuna regola della sezione 3 (compresi
  `;` fuori da un blocco di voci e `|` dentro un blocco);
- nome di percussione, qualita' di accordo o stile di voicing sconosciuti;
- velocity fuori da 1-127; griglia con N = 0; valore di nota diverso da
  1, 2, 4, 8, 16, 32, 64, 128 (o `g`, `G`); un tempo fuori da 1-999 o con
  un valore di nota che non e' uno di questi;
- una nota fuori dall'intervallo MIDI 0-127;
- `*+` o `*-` fuori dal modo relativo; una tonalita' non valida o con piu' di
  7 alterazioni;
- una rampa che non segue un comando di velocity, di tempo o di
  automazione, o non chiusa come richiesto dalle sezioni 7.3 e 7.5;
- un valore di automazione fuori dal suo intervallo; una forcella su una
  pausa o dentro una rampa di `expr` aperta;
- un segno sconosciuto, o un segno diverso da `$fermata` su una pausa; un
  ritornello scritto diversamente da come dice la sezione 8.7;
- una legatura usata diversamente da come dicono le sezioni 6.9 e 6.10;
  uno swing fuori da 50-80; uno spostamento fuori da −500..500 ms; un'ancora
  di battuta che non e' un intero da 1 a 99999, o che richiede un
  silenzio con una legatura aperta; una trasposizione fuori da −60..60
  (`transpose=` o `%Nome+N`) o che porta una nota fuori da MIDI 0-127;
  `reset:` con una rampa di velocity o di tempo aperta;
- un pattern non definito, un riferimento troppo profondo o ciclico, un
  riferimento MIDI che non si risolve, senza virgolette o con la
  virgoletta non chiusa;
- un blocco vuoto `[]` o un blocco di voci vuoto;
- una nota di abbellimento usata diversamente dalla sezione 6.12; una
  sigla d'accordo con una qualita' sconosciuta; segni di navigazione
  scritti diversamente dalla sezione 8.11.

### 10.2 Avvisi

Gli avvisi non rendono il testo non valido.

**Controlli di battuta.** Le stanghette vengono dalla metrica del brano
(sezione 12.3): la battuta 1 comincia al quarto 0 e ogni battuta dura
`4 × num / den` quarti della metrica in vigore; con un levare di P quarti
la prima stanghetta e' a P e chiude la battuta 0 (il levare), e li'
comincia la battuta 1. Una traccia che comincia
piu' avanti nel brano (un box, sezione 12.4) si controlla nella sua
posizione assoluta. I controlli si esaminano in ordine di tempo con uno
**sfasamento** corrente (all'inizio 0):

1. atteso = posizione − sfasamento; se atteso e' 0 (l'inizio del brano)
   il controllo e' giusto e non cambia nulla;
2. si trova la stanghetta piu' vicina ad *atteso*, mai quella al quarto
   0; a pari distanza, la precedente; sia l'inizio della battuta k;
3. delta = atteso − quella stanghetta. Se delta ≠ 0, si segnala sulla `|`
   "nella battuta k−1 ci sono |delta| quarti in piu' (delta > 0) / in meno
   (delta < 0)";
4. sfasamento = sfasamento + delta.

Cosi' una nota mancante si segnala una volta sola, non a ogni controllo
successivo. Una `|` ripetuta da un gruppo o da un pattern si segnala al
massimo una volta (sul gruppo o sul riferimento). Ogni voce di un blocco
di voci si controlla per conto suo, partendo dallo sfasamento al blocco;
dopo il blocco lo sfasamento e' quello di prima.

**Ancore di battuta.** Un `bar=N` raggiunto da un cursore che e' gia' oltre
l'inizio della battuta N (sezione 8.9): si segnala sull'ancora, con il
numero di battuta N, una volta per token anche se ripetuto.

**Testo cantato.** Piu' sillabe che eventi in attesa (sezione 8.5): si
segnala sul token del testo.

---

## 11. Il modello degli eventi

L'interpretazione di una traccia produce un elenco di eventi. Ogni evento
ha:

| Campo | Tipo | Significato |
| --- | --- | --- |
| `kind` | stringa | `note`, `chord`, `percussion`, `rest`, `block`, `slide`, `sustain`, `tempo_marker`, `control`, `repeat`, `text`, `harmony`, `navigation` |
| `start` | numero | inizio, in quarti dall'inizio della traccia |
| `duration` | numero | durata in quarti (0 per `sustain` e `tempo_marker`, e per `control` senza rampa) |
| `velocity` | 1-127 | velocity corrente (di default 80) |
| `letter`, `octave` | | altezza della nota (`note`, prima tappa di `slide`), con l'alterazione che suona: compresa quella della tonalita', nessuna per un bequadro, l'ottava risolta |
| `symbol`, `voicing`, `bass`, `octave` | | accordo (`chord`); `symbol` e `bass` anche per `harmony` |
| `name` | stringa | nome della percussione (`percussion`); `on`/`off` (`sustain`); nome dell'automazione (`control`); segno (`navigation`) |
| `items` | elenco | atomi di un `block`: ciascuno con `kind` e i suoi campi |
| `articulation` | stringa | `staccato`, `mute`, `legato` |
| `slide_points` | elenco | tappe dopo la prima (`slide`), come [lettera, ottava] |
| `slide_segment_durations` | elenco | durate dei segmenti (`slide`) |
| `bpm` | numero | tempo in quarti al minuto (`tempo_marker`) |
| `beat_unit` | stringa | la figura contata dal tempo, come scritta (`4.`), se c'e' (`tempo_marker`) |
| `value` | numero | valore dell'automazione (`control`; alla fine di una rampa) |
| `start_value` | numero | valore all'inizio di una rampa (`control`) |
| `curve` | stringa | curva della rampa: `lin`, `exp`, `log`, `s` (rampe `control`) |
| `slur` | stringa | `start`, `continue`, `stop` (eventi sotto una legatura, sezione 6.10) |
| `swing` | elenco | [coppia, rapporto] con lo swing attivo (sezione 7.6) |
| `shift` | intero | millisecondi di micro-tempo, quando non e' 0 (sezione 7.7) |
| `decorations` | elenco | segni dell'evento (sezione 6.11) |
| `voice` | intero | numero di voce (1 fuori dai blocchi di voci) |
| `lyric` | stringa | sillaba (eventi cantati) |
| `verses` | oggetto | sillabe delle strofe dalla 2 in poi: numero della strofa → sillaba |
| `grace` | stringa | `acciaccatura` o `appoggiatura` (note di abbellimento, sezione 6.12) |

Gli eventi compaiono nell'ordine di interpretazione (tutti gli eventi
della prima voce di un blocco, poi della seconda, …), non per forza in
ordine di `start`. La lettera della nota conserva l'alterazione come
scritta (`eb` ed `e♭` sono un Mi bemolle per l'altezza).

---

## 12. Il file di brano (`.st`)

Un file di brano e' testo UTF-8 fatto di **righe** raccolte in
**blocchi**. Un blocco comincia con una riga di intestazione e prosegue
con righe di corpo fino a una riga vuota o all'intestazione successiva.
Le righe si confrontano dopo aver tolto gli spazi iniziali e finali. Le
righe fuori dai blocchi che non sono intestazioni si ignorano (testo
libero).

### 12.1 Intestazioni del brano

| Riga | Significato |
| --- | --- |
| `ST: 2.7` | versione del linguaggio in cui e' scritto il file |
| `Tempo: 120 BPM` | tempo |
| `Tempo: 1: 120, 5: 140` | tempo per battuta (battuta: bpm, …) |
| `Metrica: 3/4` | metrica |
| `Metrica: 1: 4/4, 5: 3/4` | metrica per battuta |
| `Levare: 1` | battuta in levare, in quarti (`1`, `1.5`, `1/2`; sezione 12.3) |
| `Tonalita: Am` | tonalita' (A-G, alterazione e `m` facoltative) |
| `Tonalita: 1: C, 17: G` | tonalita' per battuta (battuta: tonalita', …) |
| `Titolo: Blue Moon` | titolo |
| `Autore: R. Rodgers` | autore della musica |
| `Parole: L. Hart` | autore del testo |

Con un elenco per battuta, il tempo/la metrica/la tonalita' del brano
sono quelli della battuta 1, o il primo valore se la battuta 1 non c'e'.
`Tempo`, `Metrica`, `Levare`, `Tonalita`, `Titolo`, `Autore` e `Parole`
non distinguono maiuscole e minuscole; le altre intestazioni si scrivono
come indicato. Titolo e autori arrivano fino a fine riga; senza titolo,
una partitura usa il nome del file.

**Versione.** `ST: M.m` e' facoltativa e va prima degli altri blocchi. Un
lettore che trova una versione piu' recente di quella che conosce
DOVREBBE avvisare che parti del file potrebbero non essere lette; chi
scrive il file DOVREBBE metterla. I lettori delle versioni prima della 2.6
la ignorano (e' una riga fuori da ogni blocco).

**Parole chiave.** Le parole chiave del file si possono scrivere in
italiano o in inglese: `Metrica`/`Meter`, `Tonalita`/`Key`,
`Levare`/`Pickup`, `Traccia`/`Track`, `Strumento`/`Instrument`,
`Titolo`/`Title`, `Autore`/`Composer`, `Parole`/`Lyricist`; nel corpo di
uno strumento `percussione`/`percussion`, `ottava`/`octave` e
`trasposizione`/`transposition`; i valori
si'/no come `si`/`yes`/`no`. Chi scrive il file DOVREBBE usare le forme
italiane, che ogni versione legge.

### 12.2 Blocchi

| Intestazione | Corpo |
| --- | --- |
| `Pattern %Nome:` | i token del pattern |
| `Traccia Nome [Strumento]:` | testo della traccia |
| `Piano:`, `Piano 2:` (il nome di uno strumento conosciuto, indice facoltativo) | testo della traccia `Piano` / `Piano 2` |
| `Box Traccia "Nome" \|quarto:` | un box della traccia `Traccia` che comincia a `quarto` |
| `Strumento Nome:` | definizione di strumento (`program=40 percussione=no ottava=3 range=36-96 poly=si voicing=spread`, facoltativo `trasposizione=-2`, sezione 9.4); un blocco senza `program=` non definisce nulla |
| `Mixer Traccia:` | `volume` (0-200), `pan` (-1…1), `mute`, `solo` (`si`/`no`) di una traccia; i lettori ignorano le chiavi che non conoscono |

I corpi di tracce e box conservano gli **a capo** (i commenti finiscono a
fine riga); i corpi dei pattern si dividono in token. I blocchi Strumento
e Mixer si leggono prima delle tracce, ovunque siano nel file. Le
applicazioni POSSONO aggiungere altri tipi di blocco (SoundText usa
`Effetti`, `Plugin`, `Catena master`, `Audio`, `Master:` e `Ambiente:`);
i lettori DEVONO saltare i blocchi che non conoscono. Una traccia con
strumento `Audio` non ha notazione.

### 12.3 Posizione delle battute

L'inizio delle battute si calcola dall'elenco delle metriche: la battuta
1 comincia al quarto 0; la metrica in vigore alla battuta 1 e' quella
dell'elenco per la battuta 1, oppure 4/4 se l'elenco non parte dalla
battuta 1, oppure il valore di `Metrica:` se non c'e' un elenco; cambia a
ogni battuta elencata; ogni battuta dura `4 × num / den` quarti. I cambi
di tempo per battuta valgono da quelle posizioni.

Con `Levare: P` (0 < P, meno di una battuta intera) il brano comincia con
una **battuta in levare** incompleta di P quarti, numerata 0: la battuta
1 e' la prima intera e comincia al quarto P, e tutte le successive si
spostano di P. Quello che e' dichiarato per la battuta 1 (tempo, metrica)
vale dall'inizio del brano, levare compreso. Una partitura stampa il
levare come prima misura incompleta; un metronomo lo conta come gli
ultimi tempi di una battuta.

### 12.4 Box

Se una traccia ha dei box, il suo testo si costruisce da questi, in
ordine di inizio:

- il vuoto prima di ogni box (dalla fine del box precedente, o da 0) si
  riempie di pause su una griglia di sedicesimi: `16: Nr` con N =
  round(vuoto / 0,25);
- ogni box porta `reset: ` seguito dal suo testo, cosi' parte sempre
  dallo stato iniziale (sezione 7.9); un box il cui testo contiene `//` e'
  seguito da un a capo;
- le parti si uniscono con spazi. Un box comincia dove finisce il testo
  costruito fin li' (il suo quarto d'inizio, salvo box sovrapposti) e la
  sua fine e' quella posizione piu' la fine del suo ultimo evento, con il
  testo interpretato in quel punto del brano (cosi' un `bar=N` al suo
  interno arriva alla battuta N del brano). Un box il cui testo non e'
  valido dura 0: la traccia non e' valida, il brano si legge lo stesso.

Il corpo di una traccia che ha dei box si ignora, quindi chi scrive il
file lo lascia vuoto: basta l'intestazione, con il nome e lo strumento.

### 12.5 Solo e mute

Le tracce udibili sono quelle non in mute; se almeno una traccia e' in
solo, solo quelle in solo (e non in mute).

---

## 13. Corrispondenza con il MIDI (informativa)

L'esportazione di riferimento scrive uno Standard MIDI File (formato 1,
480 tick per quarto): una traccia di direzione con tempo e metrica, poi
una traccia per ogni traccia udibile:

- canali in ordine, saltando il canale 10, riservato alla batteria;
  ogni traccia ha il suo canale: dalla sedicesima traccia melodica le
  tracce passano alla **porta** successiva (un meta evento *MIDI port*,
  FF 21, in testa a ogni traccia quando si usa piu' di una porta), 15
  tracce melodiche per porta; le tracce di batteria condividono il canale
  10 della porta 0;
- program change = programma GM dello strumento (batteria: banco 120);
- note: `note` → la sua altezza; `chord` → la sua realizzazione (sezione
  9.2); `block` → tutti gli atomi; `percussion` → la nota della sezione
  9.5;
- velocity = velocity dell'evento × volume della traccia / 100;
- l'articolazione cambia solo la durata **udibile**: staccato 50 %,
  stoppato 15 %, legato 115 %;
- `slide` → la prima altezza con rampe di pitch bend (ampiezza 24
  semitoni impostata con l'RPN 0);
- `sustain` → CC 64; marcatori di tempo e cambi per battuta → set-tempo;
- segni: `$accent` × 1,25 e `$marcato` × 1,4 sulla velocity (al piu' 127);
  `$tr` alterna la nota e l'altezza successiva sopra nella tonalita' del
  brano (C se manca) a passi di 1/8 di quarto, cominciando e finendo
  sulla nota; `$mordent` suona nota, altezza sotto, nota e `$turn` sopra,
  nota, sotto, nota, ogni nota dell'abbellimento lunga 1/8 di quarto
  tranne l'ultima; `$fermata` dimezza il tempo di tutto il brano durante
  l'evento; `$sfz` × 1,5 e `$fp` × 1,25 sulla velocity; `$staccatissimo`
  suona il 25 % della durata; `$trem` ribatte la nota a colpi di 1/8 di
  quarto; `$arp` ritarda ogni nota di un accordo o di un blocco di 1/16 di
  quarto, dalla piu' grave; `$harmonic` suona come scritto;
- note di abbellimento: gli abbellimenti prima di una nota suonano uno
  dopo l'altro dall'inizio della nota, ciascuno lungo 1/8 di quarto (al
  piu' una parte uguale della nota), e la nota comincia dopo di loro,
  accorciata di altrettanto;
- gli eventi `harmony` e `navigation` non suonano;
- i ritornelli si suonano espansi; l'esportazione in partitura scrive un
  ritornello (con le sue caselle) invece della musica per esteso quando
  comincia e finisce sulle stanghette, nessuna nota ne attraversa i
  confini e ogni passaggio e' uguale al primo in tutte le tracce; gli
  eventi `text` diventano parole sopra il pentagramma;
- tempi delle note con lo swing → i tempi della sezione 7.6; con uno
  spostamento, spostati dei suoi millisecondi al tempo in vigore
  (sezione 7.7);
- eventi sotto una legatura (tranne l'ultimo) senza articolazione → legato;
- `control` → control change: `vol` CC 7 (× volume della traccia / 100),
  `expr` CC 11, `pan` CC 10 (`round(64 + 63 × valore)`), `mod` CC 1,
  `rev` CC 91, `cho` CC 93, `ccN` CC N; `bend` → pitch bend `8192 +
  round(valore / 24 × 8192)` (sul canale si imposta l'ampiezza di 24
  semitoni, come per gli slide, che usano lo stesso pitch bend); `tune` →
  RPN 1 (accordatura fine del canale): CC 101 = 0, CC 100 = 1, CC 6 e
  CC 38 con il valore a 14 bit `8192 + round(valore / 100 × 8192)` (al
  piu' 16383), poi CC 101 = CC 100 = 127; una rampa si scrive come una serie di valori
  lungo la sua curva (al piu' 128 punti, distanti almeno 10 tick, senza
  ripetere valori uguali consecutivi). L'esportazione in partitura
  disegna le rampe di `vol` e di `expr` (forcelle comprese) come forcelle
  di crescendo/diminuendo;
- testo cantato → eventi meta *lyrics* (le sillabe che continuano una
  parola senza spazio dopo, le fini di parola con uno spazio; `_` non si
  scrive); solo la strofa 1.

L'esportazione in partitura (informativa) scrive titolo e autori del
brano, un cambio di armatura dove l'elenco per battuta cambia la
tonalita', la parte scritta di uno strumento traspositore (trasposta e con
l'elemento `transpose` di MusicXML), le sigle d'accordo, le note di
abbellimento, i nuovi segni, i segni di navigazione sopra la musica
scritta per esteso, e una riga di testo per strofa.

**MTXT.** L'implementazione di riferimento scrive lo stesso MIDI anche
come testo [MTXT 1.0](https://github.com/Daninet/mtxt) (un evento per
riga, tempi in quarti): ogni traccia e' un canale MTXT numerato porta ×
16 + canale, con `meta name`, `voice` (nome MTXT e General MIDI) e gli
alias della batteria con i nomi della sezione 9.5; `bend` e `tune`
insieme diventano `cc pitch` in semitoni. Legge anche MTXT, scrivendolo
come MIDI.

---

## 14. Suite di conformita'

[`conformance/cases.json`](conformance/cases.json) contiene i casi di
prova (vedi [`conformance/README.md`](conformance/README.md)): per ogni
input, `"error": true` oppure gli eventi attesi (campi della sezione 11,
numeri arrotondati a 9 decimali, `voice` omesso quando vale 1, atomi dei
blocchi senza il moltiplicatore) e gli avvisi attesi (intervallo di
caratteri del token e numero di battuta; 0 per il testo cantato e per la
battuta in levare; un caso puo' dare il levare in quarti come `pickup`;
nel campo `verses` i numeri delle strofe sono chiavi di un oggetto JSON,
quindi stringhe). Un
parser e' conforme a questa versione se da' lo stesso risultato per ogni
caso.

---

## Appendice A: modifiche

**2.7** — completamenti: le qualita' di accordo `7#5` (`aug7`), `7b5`,
`m11`, `m13`, `69`, `maj7#11`, `7#11`, `9sus4`, `7b13`, `add11`, `madd9`,
`7sus2`, `sus`, `13b9` (sezione 9.1); il resto della batteria General
MIDI (sezione 9.5); il valore `'128` e la lettera di duina `D` (sezioni 4,
6.6); il tempo con i decimali e con la figura contata `tempo=60'4.`
(sezione 7.2); le note di abbellimento `'g` e `'G` (sezione 6.12); i
segni `$arp`, `$staccatissimo`, `$sfz`, `$fp`, `$trem`, `$harmonic`
(sezione 6.11); le sigle d'accordo `$Am7` (sezione 8.10); D.C., D.S., Coda
e Fine (sezione 8.11); le strofe del testo `"2: ..."` (sezione 8.5); nel
file del brano titolo e autori, la tonalita' per battuta e gli strumenti
traspositori (sezioni 9.4, 12.1, 12.2). Ogni testo 2.6 valido e' un testo
2.7 valido con gli stessi eventi.

**2.6** — consolidamento: `reset:` (sezione 7.9), usato come prefisso dei
box (sezione 12.4); la tabella dell'eredita' dello stato (sezione 4);
i nomi dei file MIDI fra virgolette, `&"Nome"+N` / `&"Nome"-N` (sezioni
2.2, 3, 8.3), con la conversione della forma vecchia quando si leggono i
file; l'intestazione di versione `ST:`, la battuta in levare `Levare:`
(sezioni 12.1, 12.3) e le parole chiave inglesi nel file di brano; un
blocco strumento vuole `program=`. Ogni testo di traccia valido 2.5 senza
riferimenti MIDI e' valido anche in 2.6, con gli stessi eventi; uno con
riferimenti MIDI lo e' dopo la conversione della sezione 8.3.

**2.5** — ancore di battuta `bar=N` (sezione 8.9) e l'avviso per una
traccia che e' gia' oltre la battuta; trasposizione `transpose=N` e
`%Nome+N` (sezione 7.8). Ogni testo valido 2.4 e' valido anche in 2.5, con
gli stessi eventi.

**2.4** — micro-tempo `shift=N` in millisecondi (sezione 7.7) con il
campo `shift` degli eventi; l'automazione `tune=` in cent (sezione 7.5);
nel MIDI, oltre 15 tracce melodiche usano piu' porte invece di
condividere i canali (sezione 13). Ogni testo valido 2.3 e' valido anche
in 2.4, con gli stessi eventi.

**2.3** — ottave relative `rel:` / `abs:` con `*+` e `*-`, la tonalita'
`key=K` con il bequadro `n` / `♮` (sezione 5); pattern letti nello stato
iniziale delle altezze. Ogni testo valido 2.2 e' valido anche in 2.3, con
gli stessi eventi.

**2.2** — ritornelli `|: :|` con le caselle `|1.` `|2.` e `||` (sezione
8.7), segni `$accent`, `$marcato`, `$tenuto`, `$fermata`, `$tr`,
`$mordent`, `$turn` (sezione 6.11), indicazioni di testo `$"…"`
(sezione 8.8); eventi `repeat` anche per i gruppi `N(…)` con N ≥ 2; un
controllo di battuta all'inizio del brano e' sempre giusto. Gli eventi
di un testo 2.1 sono gli stessi, piu' gli eventi `repeat` dei suoi
gruppi.

**2.1** — legature di valore `~` (sezione 6.9), legature di portamento
`( )` (sezione 6.10), swing `swing=N` / `swing16=N` (sezione 7.6), le
automazioni `ccN=` e `bend=` (sezione 7.5); i campi `slur` e `swing`
degli eventi. Ogni testo valido 2.0 e' valido anche in 2.1, con gli
stessi eventi.

**2.0** — tolte le forme doppie, perche' ogni cosa abbia una sola
scrittura: l'ottava e' solo `*n` (`c/4` e l'ottava degli accordi `C7/3`
non sono piu' validi; `/` e' solo il basso alternativo), il comando di
tempo e' `tempo=N` al posto di `N§`. Nel file di brano un'intestazione
corta di traccia vuole uno spazio prima dell'indice (`Guitar 2:`;
`Guitar2:` e' lo strumento `Guitar2`). I testi con le forme tolte non
sono validi. Gli slide hanno una regola sola (sezione 6.8): non c'e' piu'
la vecchia forma in cui una catena senza moltiplicatori dopo la prima
tappa divideva un'unita' fra le sue rampe. Il file di brano non accetta
piu' i blocchi alternativi `Instrument Nome:` (con `type:`, `volume`,
`pan`) ne' le intestazioni di traccia `Nome — Strumento:`.

**1.1** — automazioni (`vol=`, `expr=`, `pan=`, `mod=`, `rev=`,
`cho=`, sezione 7.5) con le loro rampe, curve delle rampe (`>>exp`,
`>>log`, `>>s`, sezione 7.3), forcelle sui token che suonano (`c<`,
`c>`), l'evento `control`. Ogni testo valido 1.0 e' valido anche in 1.1,
con gli stessi eventi.

**1.0** — prima versione pubblicata: notazione, voci, valori di nota,
testo cantato, controlli di battuta, commenti, formato dei file di
brano, suite di conformita'.
