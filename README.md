# Guida del gruppo: Homework 4 (Wikinews)

Scadenza: invio della presentazione entro le 18:00 del 19 novembre 2026.

## Preparazione (una sola volta, ognuno sul proprio PC)
1. `git clone https://github.com/ant-ciuffreda/homework4-idd.git` e aprire la cartella in VS Code.
2. Ambiente Python, dalla cartella principale:
   `python -m venv .venv`, poi `.venv\Scripts\Activate.ps1`, poi `pip install -r requirements.txt`.
3. Avviare Elasticsearch con Docker (scegliendo una password):
   `docker run -d --name elasticsearch -p 127.0.0.1:9200:9200 -e "discovery.type=single-node" -e "xpack.security.http.ssl.enabled=false" -e "ELASTIC_PASSWORD=scegli_una_password" docker.elastic.co/elasticsearch/elasticsearch:9.5.6`
   Dopo un riavvio del PC: `docker start elasticsearch`.
4. Creare il file `.env` nella cartella principale (non va su GitHub):
   ES_URL=http://localhost:9200
   ES_USER=elastic
   ES_PASSWORD=la_password_scelta
5. Estrarre il dump (il file compresso è già nella repository):
   `tar -xzf data/itwikinews-NS0-20250320-ENTERPRISE-HTML.json.tar.gz -C data`
   Si ottiene `data/itwikinews_namespace_0_0.ndjson` (563 MB, non va su GitHub).
6. Creare i dati e l'indice sul proprio PC (ognuno ha il suo Elasticsearch):
   `python script/prepara_dati.py` (circa 2 minuti), poi `python script/indicizza.py` (circa 10 secondi).
   Alla fine deve stampare `Documenti nell'indice: 12147` e `Errori: 0`.

## Regole con Git
- Prima di iniziare: `git pull`.
- A fine lavoro: `git add <i propri file>`, `git commit -m "messaggio"`, `git push`.
- Se il push viene rifiutato: `git pull`, poi di nuovo `git push`.
- Ognuno modifica solo i propri file. Per `script/config.py` avvisare il gruppo.
- Non caricare mai `.env`, il file `.ndjson`, `data/articoli.jsonl` o la cartella `.venv`.
- Tutti i comandi si eseguono dalla cartella principale (`python script/nome.py`).
- I file di testo vanno salvati in UTF-8 (VS Code lo fa da solo). Non crearli con `>` in
  PowerShell: li salva in UTF-16 e su GitHub diventano illeggibili.

## Pacchetti Python
- `requirements.txt` lo modifica solo Antonio. Per un pacchetto nuovo, chiedere a lui.
- Dopo ogni `git pull` che cambia `requirements.txt`: `pip install -r requirements.txt`.
- Non usare `pip freeze > requirements.txt`.

## Il "contratto" tra gli script (non cambiarlo senza avvisare)
- Indice Elasticsearch: `wikinews-it` (costante `NOME_INDICE` in `config.py`).
  Per collegarsi: `from config import crea_client, NOME_INDICE`, poi `es = crea_client()`.
- File intermedio: `data/articoli.jsonl`, un articolo pulito per riga (12.147 articoli).
- Campi di ogni articolo e come sono indicizzati:

| Campo | Contenuto | Tipo in Elasticsearch | Come si usa nelle query |
|---|---|---|---|
| `id` | id Wikinews, come stringa (es. `"48882"`) | `keyword` | è anche l'`_id` del documento |
| `titolo` | titolo della notizia | `text`, analyzer `italiano` | `match` / `multi_match` |
| `titolo.standard` | stesso titolo | `text`, analyzer `standard` | solo per confrontare gli analyzer |
| `testo` | paragrafi della notizia, separati da `\n` | `text`, analyzer `italiano` | `match` / `multi_match`, highlight per l'estratto |
| `testo.standard` | stesso testo | `text`, analyzer `standard` | solo per confrontare gli analyzer |
| `categorie` | lista di argomenti (es. `["Europa", "Italia", "Sport"]`) | `keyword` | filtro `term`, aggregazione `terms` (nome esatto, maiuscole comprese) |
| `data` | data della notizia `AAAA-MM-GG`, oppure `null` (452 articoli) | `date` | filtro `range` con `gte` / `lte` |
| `url` | link alla pagina su it.wikinews.org | `keyword`, non indicizzato | solo da mostrare |

- `data` è la data scritta nell'articolo (template Data/Luogodata), non la data di modifica.
  Gli articoli senza data (pagine "Speciale", calendari) escono dai filtri per data.
- Dalle categorie sono già state tolte le date ("12 ottobre 2012") e quelle di servizio
  ("Pubblicati", "Articoli archiviati", ...). Restano 1.743 categorie.
- Analyzer `italiano` (definito in `indicizza.py`): tokenizer standard, toglie gli articoli
  apostrofati (`dell'Italia` → `italia`), minuscole, stopword italiane, radice (`light_italian`),
  accenti (`città` = `citta`). Per vedere cosa produce:
  `es.indices.analyze(index=NOME_INDICE, analyzer="italiano", text="...")`.
- Funzione di ricerca, in `script/ricerca.py`:
  `cerca(testo, pagina=1, categoria=None, data_da=None, data_a=None)`
  restituisce `{"totale": N, "risultati": [{"id", "titolo", "estratto", "data", "url", "score"}]}`
  (`data_da` e `data_a` sono stringhe `AAAA-MM-GG`; `categoria` è un nome esatto o `None`).
- Template HTML di Flask: cartella `script/templates/` (al plurale, altrimenti Flask non li trova).

## Ordine di esecuzione
1. `python script/prepara_dati.py` (crea `data/articoli.jsonl`)
2. `python script/indicizza.py` (cancella e ricrea l'indice in Elasticsearch)
3. `python script/app.py`, poi aprire `http://127.0.0.1:5000`

Script di supporto (non servono per la demo): `esplora_dump.py` e `conta_categorie.py`
(statistiche sul dump, utili per la presentazione).

## Numeri per la presentazione
- Dump: 12.261 righe; 48 duplicati (stesso articolo in più versioni) e 66 senza testo scartati
  → 12.147 articoli indicizzati.
- Date: 11.681 dal testo, 14 da `date_created`, 452 senza data; dal 2004 al 2025.
- Indicizzazione: circa 7-10 secondi (1.100-1.700 articoli al secondo), indice di circa 22 MB.

## Ruoli
| Persona | Compiti | File |
|---|---|---|
| Antonio | Dati, indicizzazione, analyzer, test di prestazioni, requirements | `prepara_dati.py`, `indicizza.py`, `conta_categorie.py`, `requirements.txt` |
| (nome) | Ricerca, valutazione della qualità (anche confronto tra analyzer) | `ricerca.py`, cartella `test/` |
| (nome) | Interfaccia web, test funzionali | `app.py`, `templates/` |

Per cambiare l'analyzer o il mapping, chiedere ad Antonio: cambiano `indicizza.py` e tutti
devono rilanciarlo.

Tutti: presentazione, README e prove della demo.
