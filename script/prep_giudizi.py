import csv
from config import crea_client, NOME_INDICE

client = crea_client()

def leggi_query_test(query_test):
    query_lista = []
    with open(query_test, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            campi = [campo.strip() or None for campo in line.split("|")]
            campi = campi + [None] * (4 - len(campi))
            dizionario_campi = {
                "testo": campi[0],
                "categoria": campi[1],
                "data_da": campi[2],
                "data_a": campi[3]
            }
            query_lista.append(dizionario_campi)
    return query_lista

def cerca_query_test (testo, campi, categoria=None, data_da=None, data_a=None):
    if testo is None:
        return []
    
    testo = testo.strip()
    if testo == "":
        return []
    
    if testo.startswith('"') and testo.endswith('"'):
        frase = testo[1:-1].strip()
        if frase == "":
            return []
        ricerca_testo = {
                "bool": {
                    "should": [
                       {"match_phrase": {campo.split('^')[0]: frase}} for campo in campi 
                    ],
                    "minimum_should_match": 1
                }
            }
    else:
        ricerca_testo = {
            "multi_match": {"query": testo, "fields": campi}
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
    
    output = client.search(
        index=NOME_INDICE,
        query=query,
        size=10,
            )
        
    risultati = []
    for hit in output["hits"]["hits"]:
        source = hit.get("_source", {})
        estratto = source.get("testo", "")[:200] + "..."
    
        risultati.append({
            "id": hit.get("_id"),
            "titolo": source.get("titolo", ""),
            "estratto": estratto
        })

    return risultati

if __name__ == "__main__":
    configurazioni = [
        {"nome": "italiano", "campi": ["titolo", "testo"]},
        {"nome": "standard", "campi": ["titolo.standard", "testo.standard"]},
        {"nome": "italiano_titolo2", "campi": ["titolo^2", "testo"]},
        {"nome": "standard_titolo2", "campi": ["titolo.standard^2", "testo.standard"]},
    ]

    query_lista = leggi_query_test("test/query_test.txt")
    righe_posizioni = []
    art_unici = {}
    
    for q in query_lista:
        for c in configurazioni:
            risultati = cerca_query_test(
                testo=q["testo"],
                campi=c["campi"],
                categoria=q["categoria"],
                data_da=q["data_da"],
                data_a=q["data_a"],
            )
            for pos, r in enumerate(risultati, start = 1):
                righe_posizioni.append([q["testo"], c["nome"], pos, r["id"]])
                art_unici[(q["testo"], r["id"] )] = r

    save_path = "risultati/qualita_posizioni.csv"
    with open(save_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile, delimiter = ",")
        writer.writerow(["query", "configurazione", "posizione", "id_articolo"])
        writer.writerows(righe_posizioni)

    save_path_2 = "risultati/qualita_giudizi.csv"
    with open(save_path_2, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile, delimiter = ",")
        writer.writerow(["query", "id_articolo", "titolo", "estratto", "rilevante"])
        ordinati = sorted(art_unici.items(), key=lambda x: (x[0][0], x [1]["titolo"]))
        for (query, id_articolo), r in ordinati:
            writer.writerow([query, id_articolo, r["titolo"], r["estratto"].replace("\n", " "), ""])

    print("Righe posizioni:", len(righe_posizioni))
    print("Articoli da giudicare:", len(art_unici))