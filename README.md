# Motore di ricerca per le notizie di Wikinews

Homework 4 · Ingegneria dei dati 2026/2027 · prof. Paolo Merialdo

Gruppo: Antonio Ciuffreda (605734), Elena Pelicella (604853), Matteo Marchegiani (605427)

Motore di ricerca con interfaccia web sulle notizie in italiano di it.wikinews.org. Il sistema pulisce il dump Wikimedia Enterprise HTML del 20 marzo 2025, indicizza 12.147 articoli in Elasticsearch con un analyzer per l'italiano e li rende cercabili da un sito Flask, con ricerca per parole, frase esatta tra virgolette, filtri per categoria e per data.

## Contenuto della repository

| Percorso | Contenuto |
|---|---|
| `data/itwikinews-NS0-20250320-ENTERPRISE-HTML.json.tar.gz` | Dump compresso (69,5 MB), da estrarre |
| `script/config.py` | Nomi condivisi (indice, file) e collegamento a Elasticsearch |
| `script/prepara_dati.py` | Pulizia del dump: testo, data, categorie, duplicati → `data/articoli.jsonl` |
| `script/indicizza.py` | Crea l'indice `wikinews-it` con l'analyzer `italiano` e carica gli articoli |
| `script/ricerca.py` | Funzione `cerca()` usata dal sito (provabile anche da console) |
| `script/app.py`, `script/templates/` | Sito web (Flask) |
| `script/esplora_dump.py`, `script/conta_categorie.py`, `script/esempio_pulizia.py` | Statistiche sul dump ed esempio di un articolo prima e dopo la pulizia |
| `script/prep_giudizi.py`, `script/calcola_metriche.py` | Valutazione della qualità della ricerca |
| `script/misura_query.py` | Tempi di risposta delle query |
| `test/` | Criteri di rilevanza e query di valutazione |
| `risultati/` | Risultati dei test usati nella presentazione |

## Requisiti

- Python 3.10 o successivo
- Docker (Docker Desktop su Windows e Mac), con almeno 4 GB di memoria assegnati
- Circa 1 GB di spazio libero (il dump estratto occupa 563 MB)
- Non serve una connessione a internet dopo l'installazione: il sito gira in locale

## Installazione

I comandi vanno lanciati dalla cartella principale della repository.

**1. Scaricare il codice e creare l'ambiente Python**

```
git clone https://github.com/ant-ciuffreda/homework4-idd.git
cd homework4-idd
python -m venv .venv
```

Attivare l'ambiente:
- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- macOS / Linux: `source .venv/bin/activate` (su Mac usare `python3` al posto di `python`)

```
pip install -r requirements.txt
```

**2. Avviare Elasticsearch 9.5.6 con Docker** (sostituire `scegli_una_password`)

```
docker run -d --name elasticsearch -p 127.0.0.1:9200:9200 -e "discovery.type=single-node" -e "xpack.security.http.ssl.enabled=false" -e "ELASTIC_PASSWORD=scegli_una_password" docker.elastic.co/elasticsearch/elasticsearch:9.5.6
```

Attendere circa 30 secondi. Aprendo `http://localhost:9200` nel browser deve comparire la richiesta di utente e password. Dopo un riavvio del computer basta `docker start elasticsearch`.

**3. Creare il file `.env`** nella cartella principale, con la password scelta al punto 2:

```
ES_URL=http://localhost:9200
ES_USER=elastic
ES_PASSWORD=scegli_una_password
```

Senza questo file né gli script né il sito partono.

**4. Estrarre il dump**

```
tar -xzf data/itwikinews-NS0-20250320-ENTERPRISE-HTML.json.tar.gz -C data
```

Si ottiene `data/itwikinews_namespace_0_0.ndjson`.

**5. Preparare i dati e creare l'indice**

```
python script/prepara_dati.py
python script/indicizza.py
```

`prepara_dati.py` richiede circa 2 minuti e stampa i conteggi della pulizia (12.147 articoli scritti, 48 duplicati e 66 articoli senza testo scartati). `indicizza.py` richiede pochi secondi e deve terminare con `Documenti nell'indice: 12147` ed `Errori: 0`. Rilanciarlo cancella e ricrea l'indice.

## Uso

**Sito web**

```
python script/app.py
```

Aprire `http://127.0.0.1:5000`. Elasticsearch deve essere già avviato: all'avvio il sito legge l'elenco delle categorie.

- Parole libere (es. `elezioni`): cerca su titolo e testo; basta una delle parole.
- Testo tra virgolette (es. `"Giro d'Italia"`): cerca la frase esatta.
- Categoria: si scrive il nome (sono suggerite le categorie esistenti, maiuscole indifferenti).
- Dal / Al: intervallo di date. Gli articoli senza data (452, soprattutto pagine "Speciale") vengono esclusi quando si usa un filtro sulle date.
- 10 risultati per pagina, con link alla pagina precedente e successiva.

**Ricerca da console**

```
python script/ricerca.py
```

Chiede testo, pagina, categoria e date, e stampa score, data e titolo dei risultati.

## Scelte principali

- **Pulizia:** del campo HTML si leggono solo i paragrafi del corpo della pagina; si eliminano riquadri di servizio, tabelle, stili e script.
- **Data:** viene letta dalla prima riga del testo (template Data/Luogodata, es. «Bruxelles, mercoledì 20 maggio 2020»), perché `date_created` è compilato solo in 14 articoli e `date_modified` è la data dell'ultima modifica.
- **Categorie:** si tolgono il prefisso «Categoria:», le categorie che sono date e quelle di servizio; ne restano 1.743.
- **Duplicati:** per ogni articolo si tiene la versione modificata più di recente.
- **Analyzer `italiano`:** tokenizer standard, elisione (`dell'Italia` → `italia`), minuscole, stopword italiane, stemmer `light_italian`, rimozione degli accenti (`città` = `citta`). I campi `titolo.standard` e `testo.standard` (analyzer standard) servono solo per il confronto.
- **Ricerca:** `multi_match` su titolo e testo; frase esatta con `match_phrase` su entrambi i campi; filtri `term` (categoria) e `range` (data) in `filter`, così non cambiano il punteggio; estratto con i termini evidenziati.

## Test e risultati

La strategia di test ha tre livelli. Tutti i risultati sono in `risultati/`.

**1. Test funzionali** (eseguiti dal sito, 9 casi su 9 superati)

| Caso | Risultato atteso |
|---|---|
| `calcio` | 2.790 risultati, termine evidenziato |
| `calcio` + categoria Sport | 2.157 |
| + date dal 01/01/2010 al 31/12/2010 | 95 |
| Pagina successiva | «pagina 2 di 10», filtri mantenuti |
| `"Giro d'Italia"` | 117, frase intera evidenziata |
| `xqzwk` | messaggio «Nessun risultato» |
| Query vuota | messaggio «Scrivi almeno una parola da cercare» |
| `città` / `citta` | stesso numero di risultati (876) |
| `dell'Italia` / `Italia` | stesso numero di risultati (3.318) |

Con Elasticsearch spento (`docker stop elasticsearch` dopo aver avviato il sito) il sito mostra un messaggio che invita a controllare che Elasticsearch sia attivo.

**2. Qualità della ricerca**

- Criteri di rilevanza in `test/criteri_rilevanza.md`, scritti prima dei test; 16 query in `test/query_test.txt` (4 argomenti: politica, sport, informatica, economia).
- 4 configurazioni: analyzer italiano (quella del sito), analyzer standard, e le stesse due con peso doppio sul titolo.
- I 208 articoli comparsi nei primi 10 di almeno una configurazione sono stati giudicati una volta sola da due persone, senza sapere da quale configurazione venissero (`risultati/qualita_giudizi.csv`).
- Per ricalcolare le metriche dai giudizi salvati:

  ```
  python script/calcola_metriche.py
  ```

  Scrive `risultati/qualita_metriche_per_query.csv` e `risultati/confronto_configurazioni.csv`.
- **Attenzione:** `script/prep_giudizi.py` rigenera l'insieme degli articoli da giudicare e **sovrascrive** `risultati/qualita_giudizi.csv` con la colonna dei giudizi vuota. Va lanciato solo su una copia della repository.

| Configurazione | Precisione a 5 | Precisione a 10 | Primo rilevante (media) | Query senza rilevanti |
|---|---|---|---|---|
| Analyzer italiano (sito) | 0,45 | 0,36 | 1,09 | 5 su 16 |
| Analyzer standard | 0,39 | 0,33 | 1,60 | 6 su 16 |
| Italiano, titolo con peso doppio | 0,42 | 0,34 | 2,58 | 4 su 16 |
| Standard, titolo con peso doppio | 0,40 | 0,32 | 1,89 | 7 su 16 |

La media del primo rilevante è calcolata solo sulle query che hanno almeno un risultato rilevante.

**3. Prestazioni** (dettagli in `risultati/prestazioni.md`)

- Indicizzazione, 10 esecuzioni di `indicizza.py`: 1,8 ± 0,1 s, 6.761 ± 405 articoli al secondo, indice di 21,7 MB, 0 errori.
- Risposta delle query: `python script/misura_query.py` (80 ricerche) dà in media 9,0 ± 1,8 ms.
- PC di riferimento: Intel Core Ultra 5 226V, 16 GB di RAM, SSD, Windows, Docker con 8 CPU e 7,6 GB. Su un MacBook Air: 1,3 s e 21,5 MB.

## Limiti noti

- 16 query e due giudici: le differenze tra configurazioni sono indicative; il richiamo non è misurato.
- `"Scuderia Ferrari"` e `AGCOM` con filtro Economia non restituiscono risultati.
- Pagine "Speciale" e quasi duplicati (calendari della Serie B) influenzano la precisione; alcune categorie non sono uniformi.
- Alcuni testi conservano residui di tabelle e riquadri (es. la parola «Wikipedia» in fondo).

## Problemi frequenti

| Problema | Soluzione |
|---|---|
| Il sito mostra «controlla che Elasticsearch sia attivo» | `docker start elasticsearch`, attendere 30 secondi, riavviare `app.py` |
| Errore di autenticazione | La password nel `.env` deve coincidere con quella del comando `docker run` |
| `Documenti nell'indice` diverso da 12147 | Rilanciare `prepara_dati.py` e poi `indicizza.py` |
| Porta 5000 occupata su Mac | Disattivare il Ricevitore AirPlay (Impostazioni di Sistema → Generali → AirDrop e Handoff) |
| Il sito non riflette una modifica al template | Riavviare `app.py` (il ricaricamento automatico è disattivato) |
