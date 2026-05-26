from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import wraps
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
db = client[os.getenv('MONGO_DB_NAME', 'proyectodb')]

def oid(id_str):
    return ObjectId(id_str)

def serialize(doc):
    doc['_id'] = str(doc['_id'])
    return doc

JWT_SECRET = os.getenv('JWT_SECRET', 'orbit-secret-change-in-prod')

# ─────────────────────────────────────────
# MIDDLEWARE JWT
# ─────────────────────────────────────────
def token_requerido(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Token requerido'}), 401
        token = auth.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            request.user_id = payload['user_id']
            request.user_email = payload['email']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────
# AUTH — Google OAuth
# ─────────────────────────────────────────
@app.route('/api/auth/google', methods=['POST'])
def auth_google():
    data         = request.json
    code         = data.get('code')
    redirect_uri = data.get('redirect_uri')

    if not code:
        return jsonify({'error': 'Código de autorización requerido'}), 400

    client_id     = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    # Intercambiar código por tokens
    token_res = http_requests.post('https://oauth2.googleapis.com/token', data={
        'code':          code,
        'client_id':     client_id,
        'client_secret': client_secret,
        'redirect_uri':  redirect_uri,
        'grant_type':    'authorization_code',
    })
    token_data = token_res.json()

    if 'error' in token_data:
        return jsonify({'error': token_data.get('error_description', token_data['error'])}), 400

    # Obtener info del usuario
    userinfo_res = http_requests.get('https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f"Bearer {token_data['access_token']}"})
    userinfo = userinfo_res.json()

    google_id = userinfo.get('sub')
    email     = userinfo.get('email')
    nombre    = userinfo.get('name', email)
    foto      = userinfo.get('picture', '')

    # Upsert usuario en MongoDB
    user_doc = db.usuarios.find_one_and_update(
        {'google_id': google_id},
        {'$set': {
            'google_id': google_id,
            'email':     email,
            'nombre':    nombre,
            'foto':      foto,
            'ultimo_login': datetime.utcnow().isoformat()
        }},
        upsert=True,
        return_document=True
    )
    user_id = str(user_doc['_id'])

    # Generar JWT (expira en 7 días)
    payload = {
        'user_id': user_id,
        'email':   email,
        'nombre':  nombre,
        'exp':     datetime.utcnow() + timedelta(days=7)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')

    return jsonify({
        'token':   token,
        'usuario': {'id': user_id, 'email': email, 'nombre': nombre, 'foto': foto}
    })


@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    user = db.usuarios.find_one({'_id': ObjectId(request.user_id)})
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({
        'id':     str(user['_id']),
        'email':  user.get('email'),
        'nombre': user.get('nombre'),
        'foto':   user.get('foto', '')
    })


# ─────────────────────────────────────────
# PING
# ─────────────────────────────────────────
@app.route('/api/ping')
def ping():
    return jsonify({"mensaje": "Backend funcionando ✔"})


# ─────────────────────────────────────────
# TAREAS
# ─────────────────────────────────────────
@app.route('/api/tareas', methods=['GET'])
def get_tareas():
    tareas = list(db.tareas.find({'user_id': request.user_id}).sort('fecha', pymongo.ASCENDING))
    return jsonify([serialize(t) for t in tareas])

@app.route('/api/tareas', methods=['POST'])
def crear_tarea():
    data = request.json
    tarea = {
        'user_id':     request.user_id,
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
    cuadernos = list(db.cuadernos.find({'user_id': request.user_id}))
    return jsonify([serialize(c) for c in cuadernos])

@app.route('/api/cuadernos', methods=['POST'])
def crear_cuaderno():
    data = request.json
    cuaderno = {
        'user_id':   request.user_id,
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
    notas = list(db.notas.find({'user_id': request.user_id}).sort('fecha', pymongo.DESCENDING))
    return jsonify([serialize(n) for n in notas])

@app.route('/api/notas', methods=['POST'])
def crear_nota():
    data = request.json
    nota = {
        'user_id':     request.user_id,
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
    eventos = list(db.eventos.find({'user_id': request.user_id}).sort('fecha', pymongo.ASCENDING))
    return jsonify([serialize(e) for e in eventos])

@app.route('/api/eventos', methods=['POST'])
def crear_evento():
    data = request.json
    evento = {
        'user_id': request.user_id,
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
    pomodoros = list(db.pomodoros.find({'user_id': request.user_id}).sort('fecha', pymongo.DESCENDING).limit(50))
    return jsonify([serialize(p) for p in pomodoros])

@app.route('/api/pomodoros', methods=['POST'])
def crear_pomodoro():
    data = request.json
    pomo = {
        'user_id':  request.user_id,
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
    movs = list(db.finanzas.find({'user_id': request.user_id}).sort('fecha', pymongo.DESCENDING))
    return jsonify([serialize(m) for m in movs])

@app.route('/api/finanzas', methods=['POST'])
def crear_movimiento():
    data = request.json
    mov = {
        'user_id':     request.user_id,
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
# AI STUDIO (Claude API)
# ─────────────────────────────────────────

def llamar_gemini(system_prompt, user_content, max_tokens=1500):
    """Helper genérico para llamar a Gemini 2.0 Flash (gratuito)"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None, "GEMINI_API_KEY no configurada en .env"
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"{system_prompt}\n\n{user_content}"
        response = client.models.generate_content(
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
    """Genera un resumen de la nota"""
    data = request.json
    texto = data.get('texto', '').strip()
    if not texto:
        return jsonify({'error': 'No hay texto para resumir'}), 400

    system = (
        "Eres un asistente de estudio. Tu tarea es hacer resúmenes claros y concisos en español. "
        "Usa bullets para los puntos clave. Sé directo y útil para un estudiante."
    )
    user = f"Resume el siguiente texto de forma clara y estructurada:\n\n{texto}"

    resultado, error = llamar_gemini(system, user, max_tokens=800)
    if error:
        return jsonify({'error': error}), 500
    return jsonify({'resultado': resultado, 'tipo': 'resumen'})


@app.route('/api/ai/flashcards', methods=['POST'])
def ai_flashcards():
    """Genera flashcards (pregunta/respuesta) desde el texto"""
    data = request.json
    texto = data.get('texto', '').strip()
    cantidad = data.get('cantidad', 6)
    if not texto:
        return jsonify({'error': 'No hay texto para generar flashcards'}), 400

    system = (
        "Eres un asistente de estudio. Genera flashcards en español para memorización. "
        "Responde ÚNICAMENTE con un array JSON válido, sin texto extra, sin markdown, sin explicaciones. "
        "Formato exacto: [{\"pregunta\": \"...\", \"respuesta\": \"...\"}]"
    )
    user = f"Genera exactamente {cantidad} flashcards de estudio basadas en este texto:\n\n{texto}"

    resultado, error = llamar_gemini(system, user, max_tokens=1200)
    if error:
        return jsonify({'error': error}), 500

    try:
        # Limpiar posibles backticks de markdown
        clean = resultado.strip()
        if clean.startswith('```'):
            clean = clean.split('```')[1]
            if clean.startswith('json'):
                clean = clean[4:]
        cards = json.loads(clean.strip())
        return jsonify({'resultado': cards, 'tipo': 'flashcards'})
    except Exception:
        return jsonify({'resultado': resultado, 'tipo': 'flashcards_raw'})


@app.route('/api/ai/cuestionario', methods=['POST'])
def ai_cuestionario():
    """Genera preguntas de opción múltiple"""
    data = request.json
    texto = data.get('texto', '').strip()
    cantidad = data.get('cantidad', 4)
    if not texto:
        return jsonify({'error': 'No hay texto para generar cuestionario'}), 400

    system = (
        "Eres un profesor. Genera preguntas de opción múltiple en español. "
        "Responde ÚNICAMENTE con un array JSON válido, sin texto extra ni markdown. "
        "Formato: [{\"pregunta\": \"...\", \"opciones\": [\"A) ...\",\"B) ...\",\"C) ...\",\"D) ...\"], \"correcta\": 0}] "
        "donde 'correcta' es el índice (0-3) de la opción correcta."
    )
    user = f"Genera exactamente {cantidad} preguntas de opción múltiple sobre este texto:\n\n{texto}"

    resultado, error = llamar_gemini(system, user, max_tokens=1500)
    if error:
        return jsonify({'error': error}), 500

    try:
        clean = resultado.strip()
        if clean.startswith('```'):
            clean = clean.split('```')[1]
            if clean.startswith('json'):
                clean = clean[4:]
        preguntas = json.loads(clean.strip())
        return jsonify({'resultado': preguntas, 'tipo': 'cuestionario'})
    except Exception:
        return jsonify({'resultado': resultado, 'tipo': 'cuestionario_raw'})


@app.route('/api/ai/puntos-clave', methods=['POST'])
def ai_puntos_clave():
    """Extrae los conceptos y puntos más importantes"""
    data = request.json
    texto = data.get('texto', '').strip()
    if not texto:
        return jsonify({'error': 'No hay texto'}), 400

    system = (
        "Eres un asistente de estudio. Extrae los puntos clave y conceptos importantes en español. "
        "Responde ÚNICAMENTE con un array JSON de strings, sin texto extra. "
        "Formato: [\"punto 1\", \"punto 2\", ...]"
    )
    user = f"Extrae los 6-8 puntos más importantes de este texto:\n\n{texto}"

    resultado, error = llamar_gemini(system, user, max_tokens=600)
    if error:
        return jsonify({'error': error}), 500

    try:
        clean = resultado.strip()
        if clean.startswith('```'):
            clean = clean.split('```')[1]
            if clean.startswith('json'):
                clean = clean[4:]
        puntos = json.loads(clean.strip())
        return jsonify({'resultado': puntos, 'tipo': 'puntos_clave'})
    except Exception:
        return jsonify({'resultado': resultado, 'tipo': 'puntos_raw'})


@app.route('/api/ai/mapa-mental', methods=['POST'])
def ai_mapa_mental():
    """Genera estructura de mapa mental"""
    data = request.json
    texto = data.get('texto', '').strip()
    if not texto:
        return jsonify({'error': 'No hay texto'}), 400

    system = (
        "Eres un asistente de estudio. Genera un mapa mental estructurado en español. "
        "Responde ÚNICAMENTE con JSON válido, sin texto extra ni markdown. "
        "Formato: {\"tema_central\": \"...\", \"ramas\": [{\"titulo\": \"...\", \"subtemas\": [\"...\",\"...\"]}]}"
    )
    user = f"Crea un mapa mental del siguiente texto:\n\n{texto}"

    resultado, error = llamar_gemini(system, user, max_tokens=1000)
    if error:
        return jsonify({'error': error}), 500

    try:
        clean = resultado.strip()
        if clean.startswith('```'):
            clean = clean.split('```')[1]
            if clean.startswith('json'):
                clean = clean[4:]
        mapa = json.loads(clean.strip())
        return jsonify({'resultado': mapa, 'tipo': 'mapa_mental'})
    except Exception:
        return jsonify({'resultado': resultado, 'tipo': 'mapa_raw'})


@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """Verifica si la API key está configurada"""
    key = os.getenv('GEMINI_API_KEY')
    return jsonify({'disponible': bool(key and len(key) > 10)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)