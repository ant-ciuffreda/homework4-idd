# Guida del gruppo: Homework 4 (Wikinews)

Scadenza: invio della presentazione entro le 18:00 del 19 novembre 2026.

## Preparazione (una sola volta, ognuno sul proprio PC)
1. `git clone https://github.com/ant-ciuffreda/homework4-idd.git` e aprire la cartella in VS Code.
2. Ambiente Python:
   `python -m venv .venv`, poi `.venv\Scripts\Activate.ps1`, poi `pip install -r requirements.txt`.
3. Avviare Elasticsearch con Docker (scegliendo una password):
   `docker run -d --name elasticsearch -p 127.0.0.1:9200:9200 -e "discovery.type=single-node" -e "xpack.security.http.ssl.enabled=false" -e "ELASTIC_PASSWORD=scegli_una_password" docker.elastic.co/elasticsearch/elasticsearch:9.5.6`
   Dopo un riavvio: `docker start elasticsearch`.
4. Creare il file `.env` nella radice (non va su GitHub):
   ES_URL=http://localhost:9200
   ES_USER=elastic
   ES_PASSWORD=la_password_scelta
5. Dump dei dati (non è nella repository): scaricare il file da
   https://dumps.wikimedia.org/other/enterprise_html/runs/20250320/itwikinews-NS0-20250320-ENTERPRISE-HTML.json.tar.gz
   metterlo in `data/`, decomprimerlo con
   `tar -xzf itwikinews-NS0-20250320-ENTERPRISE-HTML.json.tar.gz -C data`
   e rinominare il file ottenuto in `data/itwikinews.ndjson`.
   (Per iniziare subito si può usare `data/campione.ndjson`, già nella repository.)

## Regole con Git
- Prima di iniziare a lavorare: `git pull`.
- A fine lavoro: `git add <i propri file>`, `git commit -m "messaggio"`, `git push`.
- Se il push viene rifiutato: `git pull`, poi di nuovo `git push`.
- Ognuno modifica solo i propri file. Per `script/config.py` avvisare gli altri.
- Non caricare mai `.env`, il dump o la cartella `.venv`.
- Tutti i comandi si eseguono dalla cartella principale (`python script/nome.py`).

## Il "contratto" tra gli script
- Indice Elasticsearch: `wikinews-it`
- Campi di ogni articolo: `id`, `titolo`, `testo`, `categorie`, `data`, `url`
- File intermedio: `data/articoli.jsonl`, un articolo pulito per riga
- La funzione di ricerca, in `script/ricerca.py`:
  `cerca(testo, pagina=1, categoria=None, data_da=None, data_a=None)`
  restituisce `{"totale": N, "risultati": [{"id", "titolo", "estratto", "data", "url", "score"}]}`

## Ruoli
| Persona | Compiti | File |
|---|---|---|
| (nome1) | Dati e indicizzazione, test di prestazioni | `prepara_dati.py`, `indicizza.py` |
| (nome2) | Ricerca, analyzer, valutazione della qualità | `ricerca.py`, cartella `test/` |
| (nome3) | Interfaccia web, test funzionali | `app.py`, `templates/` |
Tutti | presentazione, README e prove della demo.
