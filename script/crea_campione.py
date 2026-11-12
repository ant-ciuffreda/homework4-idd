FILE_DUMP = "data/itwikinews_namespace_0_0.ndjson"
FILE_CAMPIONE = "data/campione.ndjson"
QUANTITÀ = 2390

with open(FILE_DUMP, encoding="utf-8") as origine, open(FILE_CAMPIONE, "w", encoding="utf-8") as campione:
    for numero, riga in enumerate(origine):
        if numero >= QUANTITÀ:
            break
        campione.write(riga)