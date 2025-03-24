from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

eventos = []
peregrinaciones = {}

@app.route("/")
def home():
    return render_template_string("""
    <h1>TORREMAL - Plataforma Dinámica</h1>
    <h2>Eventos:</h2>
    <ul>
    {% for evento in eventos %}
      <li>{{ evento['titulo'] }} - {{ evento['fecha'] }}</li>
    {% endfor %}
    </ul>

    <h2>Peregrinaciones:</h2>
    {% for anio, meses in peregrinaciones.items() %}
      <h3>{{ anio }}</h3>
      {% for mes, peregrinas in meses.items() %}
        <h4>{{ mes }}</h4>
        <ul>
          {% for p in peregrinas %}
            <li>{{ p['nombre'] }} - {{ p['descripcion'] }}</li>
          {% endfor %}
        </ul>
      {% endfor %}
    {% endfor %}
    """, eventos=eventos, peregrinaciones=peregrinaciones)

@app.route("/crear_evento", methods=["POST"])
def crear_evento():
    data = request.json
    eventos.append({
        "titulo": data.get("titulo"),
        "fecha": data.get("fecha"),
        "descripcion": data.get("descripcion", "")
    })
    return jsonify({"ok": True})

@app.route("/crear_peregrinacion", methods=["POST"])
def crear_peregrinacion():
    data = request.json
    anio = data.get("anio")
    mes = data.get("mes")
    if anio not in peregrinaciones:
        peregrinaciones[anio] = {}
    if mes not in peregrinaciones[anio]:
        peregrinaciones[anio][mes] = []
    peregrinaciones[anio][mes].append({
        "nombre": data.get("nombre"),
        "descripcion": data.get("descripcion"),
        "imagen": data.get("imagen", ""),
        "video": data.get("video", "")
    })
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")