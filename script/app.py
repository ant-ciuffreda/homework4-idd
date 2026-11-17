"""Interfaccia web del motore di ricerca su Wikinews (parte C).

Avvio dalla cartella principale:  python script/app.py
poi aprire http://127.0.0.1:5000

Il sito non interroga Elasticsearch per la ricerca: chiama solo cerca() di
ricerca.py (contratto del gruppo). L'unico accesso diretto all'indice serve a
leggere l'elenco delle categorie suggerite nel filtro.
"""

import math
import re
from datetime import date

from flask import Flask, render_template, request

from config import NOME_INDICE, crea_client
from ricerca import cerca

# True solo durante lo sviluppo; per la demo deve restare False
DEBUG = False

RISULTATI_PER_PAGINA = 10
# Elasticsearch non restituisce risultati oltre il 10.000esimo (from + size),
# quindi non ha senso offrire pagine oltre la 1000
MAX_PAGINE = 10000 // RISULTATI_PER_PAGINA

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]
# Formato delle date: il calendario del browser invia sempre AAAA-MM-GG
FORMATO_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")

app = Flask(__name__)
_categorie_in_cache = None


def elenco_categorie():
    """Nomi delle categorie presenti nell'indice, dalla più usata alla meno usata.

    Si leggono una volta sola con un'aggregazione terms sul campo keyword
    'categorie' e si tengono in memoria. Se Elasticsearch non risponde si
    restituisce una lista vuota: la casella resta, ma senza suggerimenti.
    """
    global _categorie_in_cache
    if _categorie_in_cache is not None:
        return _categorie_in_cache
    try:
        es = crea_client()
        risposta = es.search(
            index=NOME_INDICE,
            size=0,
            aggs={"categorie": {"terms": {"field": "categorie", "size": 5000}}},
        )
        # bucket già ordinati per n. di articoli: in cima le più usate (Chrome ne mostra 512)
        _categorie_in_cache = [b["key"] for b in risposta["aggregations"]["categorie"]["buckets"]]
    except Exception as errore:  # indice assente, Docker spento, credenziali errate
        app.logger.warning("Categorie non disponibili: %s", errore)
        return []
    return _categorie_in_cache


def leggi_data(valore):
    """Restituisce la data AAAA-MM-GG se è valida, altrimenti None.

    Il calendario invia sempre AAAA-MM-GG; il controllo serve se l'indirizzo
    viene modificato a mano (testo qualsiasi o date impossibili come 2007-04-31).
    """
    valore = (valore or "").strip()
    if not FORMATO_DATA.match(valore):
        return None
    try:
        date.fromisoformat(valore)
    except ValueError:
        return None
    return valore


def leggi_categoria(valore, categorie):
    """Trova la categoria scritta a mano, senza badare a maiuscole e minuscole.

    Il filtro term di cerca() vuole il nome esatto ("Sport", non "sport").
    Restituisce (nome esatto o None, True se il nome non esiste).
    """
    valore = (valore or "").strip()
    if not valore:
        return None, False
    if not categorie:  # elenco non disponibile: si passa il testo così com'è
        return valore, False
    for nome in categorie:
        if nome.casefold() == valore.casefold():
            return nome, False
    return None, True


def leggi_pagina(valore):
    try:
        pagina = int(valore)
    except (TypeError, ValueError):
        return 1
    return min(max(pagina, 1), MAX_PAGINE)


@app.template_filter("data_italiana")
def data_italiana(valore):
    """'2007-12-05' -> '5 dicembre 2007'; None -> testo di ripiego."""
    if not valore:
        return "Data non disponibile"
    try:
        d = date.fromisoformat(str(valore)[:10])
    except ValueError:
        return str(valore)
    return f"{d.day} {MESI[d.month - 1]} {d.year}"


@app.route("/")
def home():
    testo = request.args.get("q", "").strip()
    categorie = elenco_categorie()
    categoria_grezza = request.args.get("categoria", "").strip()
    categoria, categoria_sconosciuta = leggi_categoria(categoria_grezza, categorie)
    data_da_grezza = request.args.get("data_da", "").strip()
    data_a_grezza = request.args.get("data_a", "").strip()
    pagina = leggi_pagina(request.args.get("pagina", 1))

    data_da = leggi_data(data_da_grezza)
    data_a = leggi_data(data_a_grezza)

    avvisi = []
    if categoria_sconosciuta:
        avvisi.append(f"La categoria «{categoria_grezza}» non esiste ed è stata ignorata.")
    if data_da_grezza and not data_da:
        avvisi.append(f"La data iniziale «{data_da_grezza}» non è valida ed è stata ignorata.")
    if data_a_grezza and not data_a:
        avvisi.append(f"La data finale «{data_a_grezza}» non è valida ed è stata ignorata.")
    if data_da and data_a and data_da > data_a:
        # le stringhe AAAA-MM-GG si confrontano correttamente come testo
        data_da, data_a = data_a, data_da
        avvisi.append("Le date erano invertite: l'intervallo è stato corretto.")

    filtri = {"categoria": categoria, "data_da": data_da, "data_a": data_a}
    contesto = {
        "testo": testo,
        "filtri": filtri,
        "categorie": categorie,
        "avvisi": avvisi,
        "risposta": None,
        "errore": None,
        "messaggio": None,
        "pagina": pagina,
        "pagine_totali": 0,
        # parametri già ripuliti, riusati nei link di impaginazione
        "parametri": {k: v for k, v in {"q": testo, **filtri}.items() if v},
    }

    if not testo:
        if request.args:  # il modulo è stato inviato senza testo
            contesto["messaggio"] = "Scrivi almeno una parola da cercare."
        return render_template("index.html", **contesto)

    try:
        risposta = cerca(testo, pagina=pagina, **filtri)
    except Exception as errore:
        app.logger.exception("Errore durante la ricerca")
        contesto["errore"] = (
            "La ricerca non è disponibile in questo momento. "
            "Controlla che Elasticsearch sia avviato (docker start elasticsearch)."
        )
        if DEBUG:
            contesto["errore"] += f" Dettaglio: {errore}"
        return render_template("index.html", **contesto)

    totale = risposta.get("totale", 0)
    pagine_totali = min(math.ceil(totale / RISULTATI_PER_PAGINA), MAX_PAGINE)
    contesto["risposta"] = risposta
    contesto["pagine_totali"] = pagine_totali

    if totale == 0:
        contesto["messaggio"] = f"Nessun risultato per «{testo}»."
        if any(filtri.values()):
            contesto["messaggio"] += " Prova a togliere o allargare i filtri."
    elif pagina > pagine_totali:
        contesto["messaggio"] = (
            f"La pagina {pagina} non esiste: i risultati occupano "
            f"{pagine_totali} pagin{'a' if pagine_totali == 1 else 'e'}."
        )

    return render_template("index.html", **contesto)


if __name__ == "__main__":
    app.run(debug=DEBUG)