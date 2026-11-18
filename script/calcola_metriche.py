import csv
#Restituisce la quota di risultati rilevanti (1) nei primi k di una classifica.
#P@5 con k=5, P@10 con k=10.""
def precisione (lista_giudizi, k):
    lista = lista_giudizi[:k]
    somma = sum(lista)
    return somma/k

#Restituisce la posizione (contando da 1) del primo risultato rilevante. 
#Restituisce None se nella classifica non c'è nessun risultato rilevante.
def primo_rilevante (lista_giudizi):
    for posizione, g in enumerate(lista_giudizi, start=1):
        if g == 1:
            return posizione
    return None
        
## Legge i giudizi dati a mano: per ogni coppia (query, id articolo) il giudizio 1 o 0
with open('risultati/qualita_giudizi.csv', 'r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file, delimiter=';')
    giudizi = {}
    for row in reader:
        giudizi[(row['query'], row['id_articolo'])] = int(row['rilevante'])

print(len(giudizi))

# Legge le posizioni prodotte da prep_giudizi.py: per ogni coppia (query, configurazione)
# costruisce la lista degli id degli articoli nell'ordine in cui il motore li ha restituiti
with open('risultati/qualita_posizioni.csv', 'r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file, delimiter=',')
    classifiche = {}
    for row in reader:
        classifiche.setdefault((row['query'], row['configurazione']), []).append(row['id_articolo'])

configurazioni = ["italiano", "standard", "italiano_titolo2", "standard_titolo2"]
# Legge le 16 query dal file (solo il testo prima del "|", senza i filtri) e non da classifiche:
# così contano anche le query senza nessun risultato (Ferrari, AGCOM), con precisione 0
query_lista = []
with open("test/query_test.txt", "r", encoding="utf-8") as file:
    for riga in file:
        riga = riga.strip()
        if not riga:
            continue
        query_lista.append(riga.split("|")[0].strip())

# Per ogni query e configurazione: trasforma gli id in giudizi (1/0), completa a 10 con zeri
# (i posti mancanti contano come non rilevanti, come nei criteri) e calcola P@5, P@10 e primo rilevante
righe_per_query = []  

for q in query_lista:
    for c in configurazioni:
        ids = classifiche.get((q, c), [])
        lista_giudizi = [giudizi[q, id_articolo] for id_articolo in ids]
        n_risultati = len(lista_giudizi)
        lista_giudizi = lista_giudizi + [0] * (10-len(lista_giudizi))

        p5 = precisione(lista_giudizi, 5)
        p10 = precisione (lista_giudizi, 10)
        primo = primo_rilevante(lista_giudizi)
        righe_per_query.append([q, c, n_risultati, p5, p10, primo])

# Per ogni configurazione: media di P@5 e P@10 sulle 16 query, media della posizione del primo
# rilevante (solo sulle query che ne hanno uno: una posizione che non esiste non si può mediare)
# e numero di query senza nessun risultato rilevante nei primi 10
confronto = []
for c in configurazioni:
    righe_config = [t_r for t_r in righe_per_query if t_r[1] == c]
    p5_righe = [r[3] for r in righe_config]
    media_p5_righe = round(sum(p5_righe) /len(righe_config), 2)
    
    p10_righe = [r[4] for r in righe_config]
    media_p10_righe = round(sum(p10_righe)/len(righe_config), 2)
    
    primi_righe = [r[5] for r in righe_config if r[5] is not None]
    if primi_righe:
        primi_media = round(sum(primi_righe) / len(primi_righe), 2)
    else:
        primi_media = None 

    senza_ril = len(righe_config)-len(primi_righe)
    confronto.append([c, media_p5_righe, media_p10_righe, primi_media, senza_ril])

#creiamo due nuovi csv uno per le statistiche sulle metriche e uno per il confronto degli analyzer
with open ("risultati/qualita_metriche_per_query.csv", "w", newline = "", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["query", "configurazione", "n_risultati", "p5", "p10", "primo_rilevante"])
    writer.writerows(righe_per_query)
    
with open("risultati/confronto_configurazioni.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["configurazione", "media_p5", "media_p10", "media_primo_rilevante", "query_senza_rilevanti"])
    writer.writerows(confronto)

for riga in confronto:
    print(riga)