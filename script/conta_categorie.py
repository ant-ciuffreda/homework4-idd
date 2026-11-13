import json
import re
from collections import Counter
from config import FILE_DUMP

MESI = "gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre"
CATEGORIA_DATA = re.compile(r"^(\d{1,2} )?(" + MESI + r") \d{4}$", re.IGNORECASE)

conteggio = Counter()
categorie_data = Counter()

with open(FILE_DUMP, encoding="utf-8") as f:
    for riga in f:
        articolo = json.loads(riga)
        for categoria in articolo.get("categories") or []:
            nome = categoria["name"].replace("Categoria:", "")
            if CATEGORIA_DATA.match(nome):
                categorie_data[nome] += 1
            else:
                conteggio[nome] += 1

print("Categorie diverse (escluse le date):", len(conteggio))
print("Categorie che sono date (es. '12 ottobre 2012'):", len(categorie_data))
for nome, quante in conteggio.most_common(60):
    print(quante, nome)
