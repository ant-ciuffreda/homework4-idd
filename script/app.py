from flask import Flask, render_template, request
from ricerca import cerca

app = Flask(__name__)


@app.route("/")
def home():
    testo = request.args.get("q", "").strip()
    risposta = None
    if testo:
        risposta = cerca(testo)
    return render_template("index.html", testo=testo, risposta=risposta)


if __name__ == "__main__":
    app.run(debug=True)