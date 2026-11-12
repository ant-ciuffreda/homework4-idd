import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

NOME_INDICE = "wikinews-it"
FILE_DUMP = "data/itwikinews_namespace_0_0.ndjson"
FILE_CAMPIONE = "data/campione.ndjson"
FILE_ARTICOLI = "data/articoli.jsonl"
CAMPI = ["id", "titolo", "testo", "categorie", "data", "url"]


def crea_client():
    return Elasticsearch(
        os.getenv("ES_URL"),
        basic_auth=(os.getenv("ES_USER"), os.getenv("ES_PASSWORD")),
    )