import json
from config import FILE_DUMP

numero = 0
senza_testo = 0
senza_categorie = 0
primo = None

with open(FILE_DUMP, encoding="utf-8") as f:
    for riga in f:
        articolo = json.loads(riga)
        numero += 1
        if primo is None:
            primo = articolo
        if articolo.get("article_body", {}).get("html", "") == "":
            senza_testo += 1
        if not articolo.get("categories"):
            senza_categorie += 1

print("Numero di articoli:", numero)
print("Articoli senza HTML:", senza_testo)
print("Articoli senza categorie:", senza_categorie)
print("Titolo:", primo.get("name"))
print("Data di creazione:", primo.get("date_created"))
print("Data di modifica:", primo.get("date_modified"))
print("Categorie:", primo.get("categories"))
print("Inizio dell'HTML:", primo["article_body"]["html"][:800])