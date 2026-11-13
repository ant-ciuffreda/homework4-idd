# Guida del gruppo: Homework 4 (Wikinews)

Scadenza: invio della presentazione entro le 18:00 del 19 novembre 2026.

## Preparazione (una sola volta, ognuno sul proprio PC)
1. `git clone <URL della repository>` e aprire la cartella in VS Code.
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

## Regole con Git
- Prima di iniziare: `git pull`.
- A fine lavoro: `git add <i propri file>`, `git commit -m "messaggio"`, `git push`.
- Se il push viene rifiutato: `git pull`, poi di nuovo `git push`.
- Ognuno modifica solo i propri file. Per `script/config.py` avvisare il gruppo.
- Non caricare mai `.env`, il file `.ndjson`, `data/articoli.jsonl` o la cartella `.venv`.
- Tutti i comandi si eseguono dalla cartella principale (`python script/nome.py`).

## Pacchetti Python
- `requirements.txt` lo modifica solo Antonio. Per un pacchetto nuovo, chiedere a lui.
- Dopo ogni `git pull` che cambia `requirements.txt`: `pip install -r requirements.txt`.
- Non usare `pip freeze > requirements.txt`.

## Il "contratto" tra gli script (non cambiarlo senza avvisare)
- Indice Elasticsearch: `wikinews-it`
- Campi di ogni articolo: `id`, `titolo`, `testo`, `categorie`, `data`, `url`
  (`data` = data di creazione dell'articolo, campo `date_created` del dump)
- File intermedio: `data/articoli.jsonl`, un articolo pulito per riga
- Funzione di ricerca, in `script/ricerca.py`:
  `cerca(testo, pagina=1, categoria=None, data_da=None, data_a=None)`
  restituisce `{"totale": N, "risultati": [{"id", "titolo", "estratto", "data", "url", "score"}]}`

## Ordine di esecuzione
1. `python script/prepara_dati.py` (crea `data/articoli.jsonl`)
2. `python script/indicizza.py` (crea l'indice in Elasticsearch)
3. `python script/app.py`, poi aprire `http://127.0.0.1:5000`

## Ruoli
| Persona | Compiti | File |
|---|---|---|
| Antonio | Dati, indicizzazione, test di prestazioni, requirements | `prepara_dati.py`, `indicizza.py`, `requirements.txt` |
| (nome) | Ricerca, analyzer, valutazione della qualità | `ricerca.py`, cartella `test/` |
| (nome) | Interfaccia web, test funzionali | `app.py`, `templates/` |
Tutti: presentazione, README e prove della demo.