import json
import time
from elasticsearch import helpers
from config import crea_client, NOME_INDICE, FILE_ARTICOLI

# ---------------------------------------------------------------------------
# 1. Impostazioni dell'indice e analyzer italiano
# ---------------------------------------------------------------------------
IMPOSTAZIONI = {
    # Un solo nodo Elasticsearch: 1 shard e nessuna replica (con repliche l'indice resterebbe "yellow")
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
        "filter": {
            # Toglie gli articoli apostrofati: "dell'Italia" -> "Italia"
            "elisione_italiana": {
                "type": "elision",
                "articles_case": True,
                "articles": ["c", "l", "all", "dall", "dell", "nell", "sull", "coll", "pell",
                             "gl", "agl", "dagl", "degl", "negl", "sugl", "un", "m", "t", "s", "v", "d"],
            },
            # Toglie le parole troppo comuni (il, la, di, che, ...)
            "stopword_italiane": {"type": "stop", "stopwords": "_italian_"},
            # Riduce le parole alla radice: "elezioni", "elezione" -> "elezion"
            "radice_italiana": {"type": "stemmer", "language": "light_italian"},
        },
        "analyzer": {
            "italiano": {
                "type": "custom",
                "tokenizer": "standard",
                # asciifolding alla fine toglie gli accenti rimasti: "città" e "citta" diventano uguali
                "filter": ["elisione_italiana", "lowercase", "stopword_italiane", "radice_italiana",
                           "asciifolding"],
            }
        },
    },
}

MAPPING = {
    "properties": {
        "id": {"type": "keyword"},
        "titolo": {
            "type": "text",
            "analyzer": "italiano",
            # Sottocampo con l'analyzer standard: serve a confrontare i due analyzer nei test
            "fields": {"standard": {"type": "text", "analyzer": "standard"}},
        },
        "testo": {
            "type": "text",
            "analyzer": "italiano",
            "fields": {"standard": {"type": "text", "analyzer": "standard"}},
        },
        # keyword = valore intero, non diviso in parole: serve per filtri e conteggi
        "categorie": {"type": "keyword"},
        "data": {"type": "date", "format": "yyyy-MM-dd"},
        # L'url si mostra ma non si cerca: non serve indicizzarlo
        "url": {"type": "keyword", "index": False},
    }
}


# ---------------------------------------------------------------------------
# 2. Lettura degli articoli preparati
# ---------------------------------------------------------------------------
def leggi_articoli():
    """Restituisce gli articoli uno alla volta, nel formato richiesto da helpers.bulk."""
    with open(FILE_ARTICOLI, encoding="utf-8") as f:
        for riga in f:
            articolo = json.loads(riga)
            yield {
                "_index": NOME_INDICE,
                "_id": articolo["id"],
                "_source": articolo,
            }


# ---------------------------------------------------------------------------
# 3. Creazione dell'indice e caricamento
# ---------------------------------------------------------------------------
es = crea_client()

if es.indices.exists(index=NOME_INDICE):
    print("L'indice esiste già: lo cancello e lo ricreo")
    es.indices.delete(index=NOME_INDICE)

es.indices.create(index=NOME_INDICE, settings=IMPOSTAZIONI, mappings=MAPPING)
print("Indice creato:", NOME_INDICE)

# Durante il caricamento sospendo l'aggiornamento periodico dell'indice (refresh):
# Elasticsearch non deve rendere cercabili i documenti ogni secondo, e il caricamento è più veloce
es.indices.put_settings(index=NOME_INDICE, settings={"refresh_interval": "-1"})

inizio = time.time()
caricati = 0
errori = 0
for ok, risultato in helpers.streaming_bulk(es, leggi_articoli(), chunk_size=500, raise_on_error=False):
    if ok:
        caricati += 1
    else:
        errori += 1
        if errori <= 5:
            print("Errore:", risultato)
    if caricati % 2000 == 0 and ok:
        print("Articoli caricati:", caricati)
durata = time.time() - inizio

# Ripristino il refresh e rendo subito cercabili tutti i documenti
es.indices.put_settings(index=NOME_INDICE, settings={"refresh_interval": "1s"})
es.indices.refresh(index=NOME_INDICE)

totale = es.count(index=NOME_INDICE)["count"]
dimensione = es.indices.stats(index=NOME_INDICE)["_all"]["primaries"]["store"]["size_in_bytes"]

print("Articoli caricati:", caricati)
print("Errori:", errori)
print("Documenti nell'indice:", totale)
print(f"Tempo di indicizzazione: {durata:.1f} secondi ({caricati / durata:.0f} articoli al secondo)")
print(f"Dimensione dell'indice: {dimensione / 1024 / 1024:.1f} MB")
