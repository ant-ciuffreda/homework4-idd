import json

FILE_DUMP = "data/itwikinews_namespace_0_0.ndjson"

numero = 0
primo = None
with open(FILE_DUMP, encoding="utf-8") as f:
    for riga in f:
        numero += 1
        if primo is None:
            primo = json.loads(riga)

print("Numero di articoli (righe):", numero)
print("Campi del primo articolo:", list(primo.keys()))
print("Titolo:", primo.get("name"))
print("Data di modifica:", primo.get("date_modified"))
print("URL:", primo.get("url"))
print("Lunghezza dell'HTML (caratteri):", len(primo["article_body"]["html"]))