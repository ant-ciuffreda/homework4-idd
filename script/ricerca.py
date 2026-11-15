from config import crea_client, NOME_INDICE
import html
client = crea_client()

def cerca(testo, pagina=1, categoria=None, data_da=None, data_a=None):
    
    if testo is None:
        return {"totale": 0, "risultati": []}

    testo = testo.strip()
    if testo == "":
        return {"totale": 0, "risultati": []}

    if testo.startswith('"') and testo.endswith('"'):
        frase = testo[1:-1].strip()
        if frase == "":
            return {"totale": 0, "risultati": []}
        ricerca_testo = {
            "bool": {
                "should": [
                    {"match_phrase": {"titolo": frase}},
                    {"match_phrase": {"testo": frase}}
                ],
                "minimum_should_match": 1
            }
        }
    else:
        ricerca_testo = {
            "multi_match": {"query": testo, "fields": ["titolo", "testo"]}
        }

    
    filtri = []
    if categoria:
        filtri.append({"term": {"categorie": categoria}})
    if data_da:
        filtri.append({"range": {"data": {"gte": data_da}}})
    if data_a:
        filtri.append({"range": {"data": {"lte": data_a}}})

    query = {
        "bool": {
            "must": [
                ricerca_testo
            ],
            "filter": filtri
        }
    }

    try:
        output = client.search(
            index=NOME_INDICE,
            query=query,
            from_=(pagina - 1) * 10,
            size=10,
            track_total_hits=True,
            highlight={
                "encoder": "html",
                "fields": {"testo": {"fragment_size": 150, "number_of_fragments": 1}}
            }
        )
    except Exception as e:
        print("Errore Elasticsearch:", e)
        return {"totale": 0, "risultati": []}


    risultati = []
    for hit in output["hits"]["hits"]:
        source = hit.get("_source", {})
        estratto = hit.get("highlight", {}).get("testo", [None])[0]
        if estratto is None:
            estratto = html.escape(source.get("testo", "")[:200]) + "..."

        risultati.append({
            "id": hit.get("_id"),
            "titolo": source.get("titolo", ""),
            "estratto": estratto,
            "data": source.get("data"),
            "url": source.get("url"),
            "score": hit.get("_score")
        })

    totale = output["hits"]["total"]
    if isinstance(totale, dict):
        totale = totale.get("value", 0)

    return {"totale": totale, "risultati": risultati}

if __name__ == "__main__":   #Controllo per verificare il funzionamento del codice
    while True:
        testo_ricerca = input("Inserisci il testo da cercare ('esci' per uscire): ")
        if testo_ricerca.lower() == "esci":
            break
        
        pagina_ricerca = int(input("Inserisci il numero di pagina (default 1): ") or 1)
        categoria_ricerca = input("Inserisci la categoria (opzionale): ") or None
        data_da_ricerca = input("Inserisci la data da (YYYY-MM-DD, opzionale): ") or None
        data_a_ricerca = input("Inserisci la data a (YYYY-MM-DD, opzionale): ") or None

        risultati_ricerca = cerca(testo_ricerca, pagina_ricerca, categoria_ricerca, data_da_ricerca, data_a_ricerca)
    
        print(f"Totale risultati: {risultati_ricerca['totale']}")
        for risultato in risultati_ricerca["risultati"]:
            print(f"{risultato['score']:.2f} | {risultato['data']} | {risultato['titolo']}")
            print(f"    {risultato['estratto']}")