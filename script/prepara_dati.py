import json
import re
from bs4 import BeautifulSoup
from config import FILE_DUMP, FILE_ARTICOLI

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
        "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
# Una data scritta in italiano, es. "12 ottobre 2012" o "1º marzo 2005"
DATA_ITALIANA = re.compile(r"(\d{1,2})º?\s+(" + "|".join(MESI) + r")\s+(\d{4})", re.IGNORECASE)
# Categorie che sono solo date ("12 ottobre 2012", "Ottobre 2012")
CATEGORIA_DATA = re.compile(r"^(\d{1,2} )?(" + "|".join(MESI) + r") \d{4}$", re.IGNORECASE)
# Categorie di servizio di Wikinews: non sono argomenti
PAROLE_DI_SERVIZIO = ["Pubblicati", "Articoli ", "Articolo ", "Notizie da prima pagina",
                      "Wikivoyage", "Richieste di cancellazione", "Da cancellare",
                      "Voci con interprogetto", "Sottotemplate", "Template "]


def converti_data(testo):
    """'venerdì 12 ottobre 2012' -> '2012-10-12' (None se non c'è una data)."""
    trovata = DATA_ITALIANA.search(testo)
    if trovata is None:
        return None
    giorno = int(trovata.group(1))
    mese = MESI.index(trovata.group(2).lower()) + 1
    anno = int(trovata.group(3))
    return f"{anno:04d}-{mese:02d}-{giorno:02d}"


def is_template_data(elemento):
    """Vero se l'elemento HTML è stato generato dal template Data o Luogodata."""
    try:
        info = json.loads(elemento.get("data-mw", ""))
        nome = info["parts"][0]["template"]["target"]["href"]
    except (ValueError, KeyError, IndexError, TypeError):
        return False
    return nome.lower() in ("./template:data", "./template:luogodata")


def estrai_testo_e_data(html):
    pagina = BeautifulSoup(html, "html.parser")
    corpo = pagina.body
    if corpo is None:
        corpo = pagina

    # Tolgo i riquadri di servizio: "Hai un'opinione?", "Condividi questa notizia",
    # avvisi di manutenzione e tabelle (es. "Vedi la pagina di discussione")
    for elemento in corpo.find_all(class_=["noprint", "messagebox", "plainlinks"]):
        elemento.decompose()
    for elemento in corpo.find_all(["table", "style", "script"]):
        elemento.decompose()

    # La riga con la data ("Livorno, mercoledì 5 dicembre 2007") è prodotta dal template
    # Data o Luogodata. La uso come data della notizia e la tolgo dal testo.
    data = None
    for elemento in corpo.find_all(attrs={"typeof": "mw:Transclusion"}):
        if not is_template_data(elemento):
            continue
        codice = elemento.get("about")
        pezzi = corpo.find_all(attrs={"about": codice}) if codice else [elemento]
        data = converti_data(" ".join(pezzo.get_text(" ") for pezzo in pezzi))
        for pezzo in pezzi:
            pezzo.decompose()
        break

    paragrafi = []
    for p in corpo.find_all("p"):
        testo_p = p.get_text(" ", strip=True)
        if testo_p:
            paragrafi.append(testo_p)

    testo = "\n".join(paragrafi)
    if testo == "":
        testo = corpo.get_text(" ", strip=True)
    return testo, data


def pulisci_categorie(articolo):
    categorie = []
    for categoria in articolo.get("categories") or []:
        nome = categoria["name"].replace("Categoria:", "")
        if CATEGORIA_DATA.match(nome):
            continue
        if any(parola in nome for parola in PAROLE_DI_SERVIZIO):
            continue
        categorie.append(nome)
    return categorie


# Primo passaggio: alcuni articoli compaiono due volte nel dump (stesso id, versioni diverse).
# Mi segno, per ogni id, la data dell'ultima modifica, per tenere solo la versione più recente.
ultima_modifica = {}
with open(FILE_DUMP, encoding="utf-8") as origine:
    for riga in origine:
        articolo = json.loads(riga)
        id_articolo = articolo["identifier"]
        modifica = articolo["date_modified"]
        if id_articolo not in ultima_modifica or modifica > ultima_modifica[id_articolo]:
            ultima_modifica[id_articolo] = modifica

scritti = 0
scartati_vuoti = 0
scartati_duplicati = 0
data_dal_testo = 0
data_dal_dump = 0
senza_data = 0
gia_scritti = set()

with open(FILE_DUMP, encoding="utf-8") as origine, open(FILE_ARTICOLI, "w", encoding="utf-8") as destinazione:
    for riga in origine:
        articolo = json.loads(riga)
        id_articolo = articolo["identifier"]
        if articolo["date_modified"] != ultima_modifica[id_articolo] or id_articolo in gia_scritti:
            scartati_duplicati += 1
            continue

        testo, data = estrai_testo_e_data(articolo["article_body"]["html"])
        if testo == "":
            scartati_vuoti += 1
            continue

        # Data della notizia: quella scritta nell'articolo; se manca, date_created del dump
        # (presente solo in pochi articoli); altrimenti nessuna data
        if data is not None:
            data_dal_testo += 1
        elif articolo.get("date_created"):
            data = articolo["date_created"][:10]
            data_dal_dump += 1
        else:
            senza_data += 1

        documento = {
            "id": str(id_articolo),
            "titolo": articolo["name"],
            "testo": testo,
            "categorie": pulisci_categorie(articolo),
            "data": data,
            "url": articolo["url"],
        }
        destinazione.write(json.dumps(documento, ensure_ascii=False) + "\n")
        gia_scritti.add(id_articolo)
        scritti += 1
        if scritti % 1000 == 0:
            print("Articoli preparati:", scritti)

print("Articoli scritti:", scritti)
print("Scartati perché duplicati:", scartati_duplicati)
print("Scartati perché senza testo:", scartati_vuoti)
print("Data presa dal testo dell'articolo:", data_dal_testo)
print("Data presa da date_created:", data_dal_dump)
print("Articoli senza data:", senza_data)
