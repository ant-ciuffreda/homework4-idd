def cerca(testo, pagina=1, categoria=None, data_da=None, data_a=None):
    # Versione provvisoria: risultati finti, da sostituire con la ricerca vera
    risultati = [
        {
            "id": "1",
            "titolo": "Notizia di prova",
            "estratto": "Testo di esempio che contiene la parola " + testo,
            "data": "2025-01-01",
            "url": "https://it.wikinews.org",
            "score": 1.0,
        }
    ]
    return {"totale": len(risultati), "risultati": risultati}