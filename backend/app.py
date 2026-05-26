from flask import Flask, jsonify, request
from flask_cors import CORS
import pymongo
from bson import ObjectId
import os
from datetime import datetime
from google import genai
from google.genai import types
import json

app = Flask(__name__)
CORS(app)

MONGO_URI = (
    f"mongodb://{os.getenv('MONGO_INITDB_ROOT_USERNAME')}:"
    f"{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@mongo:27017/"
)
client = pymongo.MongoClient(MONGO_URI)
db = client[os.getenv('MONGO_DB_NAME', 'proyectoV')]

def oid(id_str):
    return ObjectId(id_str)

def serialize(doc):
    doc['_id'] = str(doc['_id'])
    return doc

# ─────────────────────────────────────────
# PING
# ─────────────────────────────────────────
@app.route('/api/ping')
def ping():
    return jsonify({"mensaje": "Backend ORBIT funcionando ✔"})


# ─────────────────────────────────────────
# TAREAS
# ─────────────────────────────────────────
@app.route('/api/tareas', methods=['GET'])
def get_tareas():
    tareas = list(db.tareas.find().sort('fecha', pymongo.ASCENDING))
    return jsonify([serialize(t) for t in tareas])

@app.route('/api/tareas', methods=['POST'])
def crear_tarea():
    data = request.json
    tarea = {
        'titulo':      data.get('titulo', ''),
        'descripcion': data.get('descripcion', ''),
        'prioridad':   data.get('prioridad', 'media'),
        'categoria':   data.get('categoria', 'general'),
        'fecha':       data.get('fecha', ''),
        'completada':  data.get('completada', False),
        'creada_en':   datetime.utcnow().isoformat()
    }
    result = db.tareas.insert_one(tarea)
    tarea['_id'] = str(result.inserted_id)
    return jsonify(tarea), 201

@app.route('/api/tareas/<id>', methods=['PUT'])
def actualizar_tarea(id):
    data = request.json
    db.tareas.update_one({'_id': oid(id)}, {'$set': data})
    return jsonify({'ok': True})

@app.route('/api/tareas/<id>', methods=['DELETE'])
def eliminar_tarea(id):
    db.tareas.delete_one({'_id': oid(id)})
    return jsonify({'ok': True})


# ─────────────────────────────────────────
# CUADERNOS
# ─────────────────────────────────────────
@app.route('/api/cuadernos', methods=['GET'])
def get_cuadernos():
    cuadernos = list(db.cuadernos.find())
    return jsonify([serialize(c) for c in cuadernos])

@app.route('/api/cuadernos', methods=['POST'])
def crear_cuaderno():
    data = request.json
    cuaderno = {
        'nombre':    data.get('nombre', 'Nuevo cuaderno'),
        'creado_en': datetime.utcnow().isoformat()
    }
    result = db.cuadernos.insert_one(cuaderno)
    cuaderno['_id'] = str(result.inserted_id)
    return jsonify(cuaderno), 201

@app.route('/api/cuadernos/<id>', methods=['DELETE'])
def eliminar_cuaderno(id):
    db.cuadernos.delete_one({'_id': oid(id)})
    db.notas.delete_many({'cuaderno_id': id})
    return jsonify({'ok': True})


# ─────────────────────────────────────────
# NOTAS
# ─────────────────────────────────────────
@app.route('/api/notas', methods=['GET'])
def get_notas():
    notas = list(db.notas.find().sort('fecha', pymongo.DESCENDING))
    return jsonify([serialize(n) for n in notas])

@app.route('/api/notas', methods=['POST'])
def crear_nota():
    data = request.json
    nota = {
        'titulo':      data.get('titulo', 'Sin título'),
        'contenido':   data.get('contenido', ''),
        'cuaderno_id': data.get('cuaderno_id', ''),
        'imagenes':    data.get('imagenes', []),
        'fecha':       datetime.utcnow().isoformat()
    }
    result = db.notas.insert_one(nota)
    nota['_id'] = str(result.inserted_id)
    return jsonify(nota), 201

@app.route('/api/notas/<id>', methods=['PUT'])
def actualizar_nota(id):
    data = request.json
    data['fecha'] = datetime.utcnow().isoformat()
    db.notas.update_one({'_id': oid(id)}, {'$set': data})
    return jsonify({'ok': True})

@app.route('/api/notas/<id>', methods=['DELETE'])
def eliminar_nota(id):
    db.notas.delete_one({'_id': oid(id)})
    return jsonify({'ok': True})


# ─────────────────────────────────────────
# EVENTOS (Calendario)
# ─────────────────────────────────────────
@app.route('/api/eventos', methods=['GET'])
def get_eventos():
    eventos = list(db.eventos.find().sort('fecha', pymongo.ASCENDING))
    return jsonify([serialize(e) for e in eventos])

@app.route('/api/eventos', methods=['POST'])
def crear_evento():
    data = request.json
    evento = {
        'titulo': data.get('titulo', ''),
        'fecha':  data.get('fecha', ''),
        'hora':   data.get('hora', ''),
        'tipo':   data.get('tipo', 'clase'),
    }
    result = db.eventos.insert_one(evento)
    evento['_id'] = str(result.inserted_id)
    return jsonify(evento), 201

@app.route('/api/eventos/<id>', methods=['DELETE'])
def eliminar_evento(id):
    db.eventos.delete_one({'_id': oid(id)})
    return jsonify({'ok': True})


# ─────────────────────────────────────────
# POMODOROS
# ─────────────────────────────────────────
@app.route('/api/pomodoros', methods=['GET'])
def get_pomodoros():
    pomodoros = list(db.pomodoros.find().sort('fecha', pymongo.DESCENDING).limit(50))
    return jsonify([serialize(p) for p in pomodoros])

@app.route('/api/pomodoros', methods=['POST'])
def crear_pomodoro():
    data = request.json
    pomo = {
        'fecha':    data.get('fecha', datetime.utcnow().isoformat()[:10]),
        'minutos':  data.get('minutos', 25),
        'creado_en': datetime.utcnow().isoformat()
    }
    result = db.pomodoros.insert_one(pomo)
    pomo['_id'] = str(result.inserted_id)
    return jsonify(pomo), 201


# ─────────────────────────────────────────
# FINANZAS
# ─────────────────────────────────────────
@app.route('/api/finanzas', methods=['GET'])
def get_finanzas():
    movs = list(db.finanzas.find().sort('fecha', pymongo.DESCENDING))
    return jsonify([serialize(m) for m in movs])

@app.route('/api/finanzas', methods=['POST'])
def crear_movimiento():
    data = request.json
    mov = {
        'descripcion': data.get('descripcion', ''),
        'monto':       float(data.get('monto', 0)),
        'tipo':        data.get('tipo', 'gasto'),
        'categoria':   data.get('categoria', 'Otro'),
        'fecha':       data.get('fecha', datetime.utcnow().isoformat()[:10]),
        'creado_en':   datetime.utcnow().isoformat()
    }
    result = db.finanzas.insert_one(mov)
    mov['_id'] = str(result.inserted_id)
    return jsonify(mov), 201

@app.route('/api/finanzas/<id>', methods=['DELETE'])
def eliminar_movimiento(id):
    db.finanzas.delete_one({'_id': oid(id)})
    return jsonify({'ok': True})


# ─────────────────────────────────────────
# AI STUDIO (Gemini)
# ─────────────────────────────────────────
def llamar_gemini(system_prompt, user_content, max_tokens=1500):
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None, "GEMINI_API_KEY no configurada en .env"
    try:
        gemini_client = genai.Client(api_key=api_key)
        prompt = f"{system_prompt}\n\n{user_content}"
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.4,
            )
        )
        return response.text, None
    except Exception as e:
        return None, str(e)


@app.route('/api/ai/resumen', methods=['POST'])
def ai_resumen():
    data  = request.json
    texto = data.get('texto', '').strip()
    if not texto:
        return jsonify({'error': 'No hay texto para resumir'}), 400
    system = "Eres un asistente de estudio. Haz resúmenes claros y concisos en español con bullets."
    resultado, error = llamar_gemini(system, f"Resume este texto:\n\n{texto}", 800)
    if error:
        return jsonify({'error': error}), 500
    return jsonify({'resultado': resultado, 'tipo': 'resumen'})


@app.route('/api/ai/flashcards', methods=['POST'])
def ai_flashcards():
    data     = request.json
    texto    = data.get('texto', '').strip()
    cantidad = data.get('cantidad', 6)
    if not texto:
        return jsonify({'error': 'No hay texto'}), 400
    system = ('Genera flashcards en español. Responde ÚNICAMENTE con JSON válido sin markdown. '
              'Formato: [{"pregunta": "...", "respuesta": "..."}]')
    resultado, error = llamar_gemini(system, f"Genera {cantidad} flashcards de:\n\n{texto}", 1200)
    if error:
        return jsonify({'error': error}), 500
    try:
        clean = resultado.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
        return jsonify({'resultado': json.loads(clean), 'tipo': 'flashcards'})
    except Exception:
        return jsonify({'resultado': resultado, 'tipo': 'flashcards_raw'})


@app.route('/api/ai/cuestionario', methods=['POST'])
def ai_cuestionario():
    data     = request.json
    texto    = data.get('texto', '').strip()
    cantidad = data.get('cantidad', 4)
    if not texto:
        return jsonify({'error': 'No hay texto'}), 400
    system = ('Genera preguntas de opción múltiple en español. Solo JSON sin markdown. '
              'Formato: [{"pregunta":"...","opciones":["A)...","B)...","C)...","D)..."],"correcta":0}]')
    resultado, error = llamar_gemini(system, f"Genera {cantidad} preguntas de:\n\n{texto}", 1500)
    if error:
        return jsonify({'error': error}), 500
    try:
        clean = resultado.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
        return jsonify({'resultado': json.loads(clean), 'tipo': 'cuestionario'})
    except Exception:
        return jsonify({'resultado': resultado, 'tipo': 'cuestionario_raw'})


@app.route('/api/ai/puntos-clave', methods=['POST'])
def ai_puntos_clave():
    data  = request.json
    texto = data.get('texto', '').strip()
    if not texto:
        return jsonify({'error': 'No hay texto'}), 400
    system = 'Extrae puntos clave en español. Solo JSON: ["punto 1", "punto 2", ...]'
    resultado, error = llamar_gemini(system, f"Extrae 6-8 puntos de:\n\n{texto}", 600)
    if error:
        return jsonify({'error': error}), 500
    try:
        clean = resultado.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
        return jsonify({'resultado': json.loads(clean), 'tipo': 'puntos_clave'})
    except Exception:
        return jsonify({'resultado': resultado, 'tipo': 'puntos_raw'})


@app.route('/api/ai/mapa-mental', methods=['POST'])
def ai_mapa_mental():
    data  = request.json
    texto = data.get('texto', '').strip()
    if not texto:
        return jsonify({'error': 'No hay texto'}), 400
    system = ('Genera mapa mental en español. Solo JSON sin markdown. '
              'Formato: {"tema_central":"...","ramas":[{"titulo":"...","subtemas":["...","..."]}]}')
    resultado, error = llamar_gemini(system, f"Mapa mental de:\n\n{texto}", 1000)
    if error:
        return jsonify({'error': error}), 500
    try:
        clean = resultado.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
        return jsonify({'resultado': json.loads(clean), 'tipo': 'mapa_mental'})
    except Exception:
        return jsonify({'resultado': resultado, 'tipo': 'mapa_raw'})


@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    key = os.getenv('GEMINI_API_KEY')
    return jsonify({'disponible': bool(key and len(key) > 10)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)