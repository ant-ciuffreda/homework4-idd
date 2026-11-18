# Criteri di rilevanza – valutazione della qualità della ricerca

I seguenti criteri di rilevanza sono stati decisi prima di eseguire i test.
Servono per giudicare coerentemente la rilevanza di un risultato.

## Regola generale

Un articolo è **rilevante** se un utente che ha scritto quella query restituisse il risultato atteso:
l'articolo **tratta principalmente** l'argomento cercato.

Un articolo è **non rilevante** se contrariamente:
- cita l'argomento solo di passaggio (una riga in un articolo che parla d'altro);
- contiene le parole cercate con un altro significato (es. "calcio" come minerale);
- parla di un argomento simile ma diverso da quello chiesto (es. elezioni regionali per una query sulle elezioni politiche).

Il giudizio è binario: sì / no. Nessun "parzialmente".

## Casi particolari

| Caso | Decisione |
|---|---|
| Pagine "Speciale" (raccolte di articoli, spesso senza data) | **Rilevante** se il suo argomento coincide con la query |
| Quasi duplicati (es. calendari della Serie B quasi identici) | Ognuno giudicato **da solo**, con la regola generale |
| Query tra virgolette (frase esatta) | Rilevante se l'articolo parla del soggetto indicato dalla frase, non basta che la frase compaia |
| Query con filtro (categoria o date) | Il filtro si dà per corretto (lo verificano i test funzionali); si giudica solo l'argomento |
| Articoli senza data | Giudicati normalmente |
| Articolo con testo sporco (menu, tabelle) ma sull'argomento giusto | Rilevante |
| Dubbio che resta dopo aver letto titolo e inizio del testo | **Non rilevante** |

## Procedura di giudizio

1. Per ogni query si leggono **titolo ed estratto**; se non bastano, si apre l'articolo.
2. Si giudicano i **primi 10 risultati** (pagina 1).
3. Per i confronti tra configurazioni (analyzer italiano / standard; con / senza peso sul titolo) si giudica **una volta sola l'insieme** di tutti gli articoli comparsi nei primi 10 di almeno una configurazione, **senza sapere da quale configurazione vengono**. Poi si calcolano le metriche di ogni configurazione usando quei giudizi.
   Così lo stesso articolo ha sempre lo stesso giudizio e chi giudica non favorisce, anche senza volerlo, una configurazione.
4. I giudizi si salvano in `risultati/qualita_giudizi.csv` (query, id articolo, titolo, rilevante sì/no).

## Metriche

- **P@5** = rilevanti nei primi 5 / 5
- **P@10** = rilevanti nei primi 10 / 10
- **Posizione del primo rilevante** (1 = primo risultato; se nessuno nei primi 10: "nessuno")
- **Meno di 10 risultati:** i posti mancanti contano come non rilevanti (es. 4 risultati tutti rilevanti → P@5 = 0,8, P@10 = 0,4). Le query non vengono provate né cambiate prima dei giudizi: se una restituisce pochi risultati, è un comportamento del sistema.
- Per ogni metrica: valore per query e media su tutte le query.

## Limiti dichiarati

- Giudizi di una sola persona: possono essere soggettivi.
- 16 query, 4 per argomento (politica, sport, informatica, economia): per ogni argomento 2 query normali senza filtri, 1 frase tra virgolette e 1 query normale con un filtro (categoria o data). Con 16 query le differenze tra configurazioni sono indicative, non statisticamente solide.
- Si valutano solo i primi 10 risultati: non si misura quanti articoli rilevanti il sistema non trova.
