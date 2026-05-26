<template>
  <div class="dashboard">
    <header class="dash-header">
      <div>
        <h1>Buenos días 👋</h1>
        <p class="date">{{ fechaHoy }}</p>
      </div>

    </header>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card purple">
        <span class="stat-value">{{ tareas.length }}</span>
        <span class="stat-label">Tareas totales</span>
      </div>
      <div class="stat-card yellow">
        <span class="stat-value">{{ tareasPendientes }}</span>
        <span class="stat-label">Pendientes</span>
      </div>
      <div class="stat-card green">
        <span class="stat-value">{{ tareasCompletadas }}</span>
        <span class="stat-label">Completadas</span>
      </div>
      <div class="stat-card blue">
        <span class="stat-value">{{ progreso }}%</span>
        <span class="stat-label">Progreso</span>
      </div>
    </div>

    <!-- Barra de progreso -->
    <div class="progress-section">
      <div class="progress-bar-bg">
        <div class="progress-bar-fill" :style="{ width: progreso + '%' }"></div>
      </div>
      <span class="progress-label">{{ progreso }}% completado hoy</span>
    </div>

    <!-- Tareas -->
    <div class="section">
      <div class="section-header">
        <h2>Tareas</h2>
        <button class="btn-add" @click="mostrarForm = !mostrarForm">+ Nueva tarea</button>
      </div>

      <div v-if="mostrarForm" class="task-form">
        <input v-model="nuevaTarea.titulo" placeholder="Título de la tarea" class="input" />
        <div class="form-row">
          <select v-model="nuevaTarea.prioridad" class="input select">
            <option value="alta">🔴 Alta</option>
            <option value="media">🟡 Media</option>
            <option value="baja">🟢 Baja</option>
          </select>
          <input v-model="nuevaTarea.fecha" type="date" class="input" />
        </div>
        <div class="form-actions">
          <button class="btn-cancel" @click="mostrarForm = false">Cancelar</button>
          <button class="btn-save"   @click="guardarTarea">Guardar</button>
        </div>
      </div>

      <div v-if="cargando" class="loading">Cargando tareas...</div>
      <div v-else class="task-list">
        <div
          v-for="tarea in tareas"
          :key="tarea._id"
          class="task-item"
          :class="{ completada: tarea.completada }"
        >
          <button class="check-btn" @click="toggleTarea(tarea)">
            <span v-if="tarea.completada">✓</span>
          </button>
          <div class="task-info">
            <span class="task-titulo">{{ tarea.titulo }}</span>
            <span class="task-fecha" v-if="tarea.fecha">📅 {{ tarea.fecha }}</span>
          </div>
          <span class="prioridad-badge" :class="tarea.prioridad">{{ tarea.prioridad }}</span>
          <button class="delete-btn" @click="eliminarTarea(tarea._id)">✕</button>
        </div>
        <div v-if="tareas.length === 0 && !cargando" class="empty-state">
          No hay tareas aún. ¡Creá una!
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const BACKEND = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'

const tareas      = ref([])
const cargando    = ref(true)
const mostrarForm = ref(false)
const nuevaTarea  = ref({ titulo: '', prioridad: 'media', fecha: '' })

const fechaHoy = new Date().toLocaleDateString('es-GT', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
})

const tareasPendientes  = computed(() => tareas.value.filter(t => !t.completada).length)
const tareasCompletadas = computed(() => tareas.value.filter(t =>  t.completada).length)
const progreso = computed(() => {
  if (!tareas.value.length) return 0
  return Math.round((tareasCompletadas.value / tareas.value.length) * 100)
})

async function cargarTareas() {
  try {
    const res = await fetch(`${BACKEND}/api/tareas`)
    tareas.value = await res.json()
  } catch { }
  finally  { cargando.value = false }
}

async function guardarTarea() {
  if (!nuevaTarea.value.titulo.trim()) return
  try {
    await fetch(`${BACKEND}/api/tareas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(nuevaTarea.value)
    })
    nuevaTarea.value = { titulo: '', prioridad: 'media', fecha: '' }
    mostrarForm.value = false
    await cargarTareas()
  } catch(e) { console.error(e) }
}

async function toggleTarea(tarea) {
  try {
    await fetch(`${BACKEND}/api/tareas/${tarea._id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completada: !tarea.completada })
    })
    await cargarTareas()
  } catch(e) { console.error(e) }
}

async function eliminarTarea(id) {
  try {
    await fetch(`${BACKEND}/api/tareas/${id}`, { method: 'DELETE' })
    await cargarTareas()
  } catch(e) { console.error(e) }
}

onMounted(cargarTareas)
</script>

<style scoped>
.dashboard { padding: 2rem; max-width: 900px; }

/* Header */
.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.dash-header h1 {
  font-family: 'Syne', sans-serif;
  font-size: 1.8rem;
  color: var(--text-primary);
}

.date { color: var(--text-muted); font-size: 0.9rem; margin-top: 4px; }

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-card);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  border: 1px solid var(--border);
}


/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  border-radius: var(--radius);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border: 1px solid var(--border);
  transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: var(--shadow); }

.stat-card.purple { background: var(--accent-soft); }
.stat-card.yellow { background: var(--yellow-soft); }
.stat-card.green  { background: var(--green-soft); }
.stat-card.blue   { background: var(--blue-soft); }

.stat-value {
  font-family: 'Syne', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}
.stat-label { font-size: 0.8rem; color: var(--text-secondary); }

/* Progress */
.progress-section {
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-bar-bg {
  flex: 1;
  height: 8px;
  background: var(--bg-card);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--border);
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent-light));
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-label { font-size: 0.8rem; color: var(--text-muted); white-space: nowrap; }

/* Section */
.section { margin-bottom: 2rem; }

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h2 {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.btn-add {
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 0.45rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: opacity 0.2s;
}
.btn-add:hover { opacity: 0.85; }

/* Form */
.task-form {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.input {
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.6rem 0.75rem;
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  width: 100%;
  outline: none;
  transition: border-color 0.2s;
}
.input:focus { border-color: var(--border-focus); }
.select { cursor: pointer; }

.form-row { display: flex; gap: 0.75rem; }
.form-row .input { flex: 1; }
.form-actions { display: flex; justify-content: flex-end; gap: 0.5rem; }

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 0.45rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-save {
  background: var(--accent);
  border: none;
  color: white;
  padding: 0.45rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
}

/* Task list */
.task-list { display: flex; flex-direction: column; gap: 0.5rem; }

.task-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.75rem 1rem;
  transition: border-color 0.2s, transform 0.15s;
}
.task-item:hover { border-color: var(--accent); transform: translateX(2px); }
.task-item.completada { opacity: 0.5; }
.task-item.completada .task-titulo { text-decoration: line-through; }

.check-btn {
  width: 22px; height: 22px;
  border-radius: 50%;
  border: 2px solid var(--accent);
  background: transparent;
  cursor: pointer;
  color: var(--accent);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem;
  flex-shrink: 0;
  transition: background 0.2s;
}
.check-btn:hover { background: var(--accent-soft); }

.task-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.task-titulo { font-size: 0.9rem; color: var(--text-primary); }
.task-fecha  { font-size: 0.75rem; color: var(--text-muted); }

.prioridad-badge {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 20px;
  font-weight: 500;
}
.prioridad-badge.alta  { background: var(--red-soft);    color: var(--red); }
.prioridad-badge.media { background: var(--yellow-soft); color: var(--yellow); }
.prioridad-badge.baja  { background: var(--green-soft);  color: var(--green); }

.delete-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.8rem;
  transition: color 0.2s;
  padding: 4px;
}
.delete-btn:hover { color: var(--red); }

.loading, .empty-state {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem;
  font-size: 0.9rem;
}
</style>