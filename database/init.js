// ==========================================================
// StudyHub - Script de inicialización de MongoDB
// Se ejecuta automáticamente al crear el contenedor por
// primera vez, gracias al volumen /docker-entrypoint-initdb.d/
// ==========================================================

// Cambiar a la base de datos del proyecto
// (la variable viene del entorno, pero en init.js usamos el nombre directo)
db = db.getSiblingDB(process.env.MONGO_DB_NAME || 'proyectoV');

// ── Crear colecciones con validación básica ────────────────

db.createCollection('tareas');
db.createCollection('cuadernos');
db.createCollection('notas');
db.createCollection('eventos');
db.createCollection('pomodoros');
db.createCollection('finanzas');

// ── Índices para búsquedas rápidas ────────────────────────

db.tareas.createIndex({ fecha: 1 });
db.tareas.createIndex({ prioridad: 1 });
db.tareas.createIndex({ completada: 1 });

db.notas.createIndex({ cuaderno_id: 1 });
db.notas.createIndex({ fecha: -1 });

db.eventos.createIndex({ fecha: 1 });

db.finanzas.createIndex({ fecha: -1 });
db.finanzas.createIndex({ tipo: 1 });

db.pomodoros.createIndex({ fecha: -1 });

// ── Datos iniciales de ejemplo ─────────────────────────────

// Tareas de ejemplo
db.tareas.insertMany([
  {
    titulo: '📖 Leer capítulo 3 de Virtualización',
    descripcion: 'Enfocarse en la sección de contenedores Docker',
    prioridad: 'alta',
    categoria: 'estudio',
    fecha: new Date().toISOString().slice(0, 10),
    completada: false,
    creada_en: new Date().toISOString()
  },
  {
    titulo: '✅ Completar proyecto final Fase I',
    descripcion: 'Entregar antes del viernes',
    prioridad: 'alta',
    categoria: 'estudio',
    fecha: new Date().toISOString().slice(0, 10),
    completada: false,
    creada_en: new Date().toISOString()
  },
  {
    titulo: '🛒 Comprar cuaderno nuevo',
    descripcion: '',
    prioridad: 'baja',
    categoria: 'personal',
    fecha: '',
    completada: false,
    creada_en: new Date().toISOString()
  }
]);

// Cuaderno de ejemplo
const cuadernoId = new ObjectId();
db.cuadernos.insertOne({
  _id: cuadernoId,
  nombre: '📚 Virtualización 2026',
  creado_en: new Date().toISOString()
});

// Nota de ejemplo dentro del cuaderno
db.notas.insertOne({
  titulo: 'Bienvenido a StudyHub',
  contenido: '## StudyHub\n\nEsta es tu primera nota. Puedes usar **Markdown** para formatear.\n\n- Crea cuadernos\n- Organiza tus notas\n- Adjunta imágenes\n\n> Tip: usa los botones de la barra de herramientas para dar formato rápido.',
  cuaderno_id: cuadernoId.toString(),
  imagenes: [],
  fecha: new Date().toISOString()
});

// Evento de ejemplo en el calendario
db.eventos.insertOne({
  titulo: '🎓 Entrega Proyecto Final',
  fecha: new Date().toISOString().slice(0, 10),
  hora: '23:59',
  tipo: 'entrega'
});

// Movimiento de finanzas de ejemplo
db.finanzas.insertOne({
  descripcion: 'Beca semestral',
  monto: 500.00,
  tipo: 'ingreso',
  categoria: 'Beca',
  fecha: new Date().toISOString().slice(0, 10),
  creado_en: new Date().toISOString()
});

print('✅ StudyHub - Base de datos inicializada correctamente');
print('   Colecciones creadas: tareas, cuadernos, notas, eventos, pomodoros, finanzas');