<template>
  <div class="tareas-page">

    <div class="tareas-header">
      <div>
        <h1>Tareas</h1>
        <p class="sub">{{ pendientes }} pendientes · {{ completadas }} completadas</p>
      </div>
      <button class="btn-nueva" @click="mostrarForm = !mostrarForm">+ Nueva tarea</button>
    </div>

    <!-- Filtros -->
    <div class="filtros">
      <button
        v-for="f in filtros"
        :key="f.id"
        class="filtro-btn"
        :class="{ active: filtroActivo === f.id }"
        @click="filtroActivo = f.id"
      >{{ f.label }}</button>
    </div>

    <!-- Formulario nueva tarea -->
    <transition name="slide">
      <div v-if="mostrarForm" class="tarea-form">
        <input v-model="form.titulo"    class="input" placeholder="Título de la tarea *" />
        <textarea v-model="form.descripcion" class="input textarea" placeholder="Descripción (opcional)" rows="2"></textarea>
        <div class="form-row">
          <select v-model="form.prioridad" class="input select">
            <option value="alta">🔴 Alta prioridad</option>
            <option value="media">🟡 Media prioridad</option>
            <option value="baja">🟢 Baja prioridad</option>
          </select>
          <select v-model="form.categoria" class="input select">
            <option value="general">📌 General</option>
            <option value="estudio">📚 Estudio</option>
            <option value="personal">👤 Personal</option>
            <option value="trabajo">💼 Trabajo</option>
          </select>
          <input v-model="form.fecha" type="date" class="input" />
        </div>
        <div class="form-actions">
          <button class="btn-cancel" @click="mostrarForm = false; resetForm()">Cancelar</button>
          <button class="btn-guardar" @click="guardarTarea">Guardar tarea</button>
        </div>
      </div>
    </transition>

    <!-- Lista de tareas -->
    <div class="tareas-lista" v-if="!cargando">
      <div
        v-for="tarea in tareasVisibles"
        :key="tarea._id"
        class="tarea-card"
        :class="{ completada: tarea.completada }"
      >
        <button class="check" :class="{ done: tarea.completada }" @click="toggleTarea(tarea)">
          <span v-if="tarea.completada">✓</span>
        </button>

        <div class="tarea-body">
          <div class="tarea-top">
            <span class="tarea-titulo">{{ tarea.titulo }}</span>
            <div class="tarea-badges">
              <span class="badge-cat" :class="tarea.categoria">{{ tarea.categoria }}</span>
              <span class="badge-pri" :class="tarea.prioridad">{{ tarea.prioridad }}</span>
            </div>
          </div>
          <p class="tarea-desc" v-if="tarea.descripcion">{{ tarea.descripcion }}</p>
          <div class="tarea-meta">
            <span v-if="tarea.fecha" :class="{ vencida: estaVencida(tarea) }">
              📅 {{ tarea.fecha }}
            </span>
          </div>
        </div>

        <button class="btn-del" @click="eliminarTarea(tarea._id)">✕</button>
      </div>

      <div v-if="tareasVisibles.length === 0" class="empty-state">
        <span>✓</span>
        <p>No hay tareas en esta categoría</p>
      </div>
    </div>

    <div v-else class="cargando">Cargando tareas...</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const BACKEND = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'

const tareas       = ref([])
const cargando     = ref(true)
const mostrarForm  = ref(false)
const filtroActivo = ref('todas')

const form = ref({ titulo: '', descripcion: '', prioridad: 'media', categoria: 'general', fecha: '' })

const filtros = [
  { id: 'todas',      label: 'Todas' },
  { id: 'hoy',        label: 'Hoy' },
  { id: 'pendientes', label: 'Pendientes' },
  { id: 'alta',       label: '🔴 Alta' },
  { id: 'media',      label: '🟡 Media' },
  { id: 'baja',       label: '🟢 Baja' },
]

const hoy = new Date().toISOString().slice(0, 10)

const pendientes  = computed(() => tareas.value.filter(t => !t.completada).length)
const completadas = computed(() => tareas.value.filter(t => t.completada).length)

const tareasVisibles = computed(() => {
  switch (filtroActivo.value) {
    case 'hoy':        return tareas.value.filter(t => t.fecha === hoy)
    case 'pendientes': return tareas.value.filter(t => !t.completada)
    case 'alta':       return tareas.value.filter(t => t.prioridad === 'alta')
    case 'media':      return tareas.value.filter(t => t.prioridad === 'media')
    case 'baja':       return tareas.value.filter(t => t.prioridad === 'baja')
    default:           return tareas.value
  }
})

function estaVencida(t) {
  return !t.completada && t.fecha && t.fecha < hoy
}

function resetForm() {
  form.value = { titulo: '', descripcion: '', prioridad: 'media', categoria: 'general', fecha: '' }
}

async function cargarTareas() {
  try {
    const res = await fetch(`${BACKEND}/api/tareas`)
    tareas.value = await res.json()
  } catch {} finally {
    cargando.value = false
  }
}

async function guardarTarea() {
  if (!form.value.titulo.trim()) return
  try {
    await fetch(`${BACKEND}/api/tareas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form.value, completada: false })
    })
    resetForm()
    mostrarForm.value = false
    await cargarTareas()
  } catch {}
}

async function toggleTarea(t) {
  try {
    await fetch(`${BACKEND}/api/tareas/${t._id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completada: !t.completada })
    })
    await cargarTareas()
  } catch {}
}

async function eliminarTarea(id) {
  try {
    await fetch(`${BACKEND}/api/tareas/${id}`, { method: 'DELETE' })
    await cargarTareas()
  } catch {}
}

onMounted(cargarTareas)
</script>

<style scoped>
.tareas-page { padding: 2rem; max-width: 860px; }

.tareas-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.tareas-header h1 {
  font-family: 'Syne', sans-serif;
  font-size: 1.8rem;
  color: var(--text-primary);
}

.sub { font-size: 0.85rem; color: var(--text-muted); margin-top: 4px; }

.btn-nueva {
  background: var(--accent);
  color: var(--text-primary);
  border: none;
  padding: 0.55rem 1.2rem;
  border-radius: 9px;
  cursor: pointer;
  font-size: 0.88rem;
  transition: background 0.2s;
  white-space: nowrap;
}
.btn-nueva:hover { background: var(--accent); }

/* ── Filtros ── */
.filtros {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.filtro-btn {
  padding: 0.35rem 1rem;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.82rem;
  transition: all 0.2s;
}
.filtro-btn:hover  { border-color: var(--accent); color: var(--accent-light); }
.filtro-btn.active { background: var(--accent-soft); border-color: var(--accent); color: var(--accent-light); }

/* ── Form ── */
.tarea-form {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
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
  font-size: 0.88rem;
  width: 100%;
  outline: none;
}
.input:focus  { border-color: var(--accent); }
.textarea     { resize: vertical; min-height: 60px; }
.select       { cursor: pointer; }
.form-row     { display: flex; gap: 0.75rem; }
.form-row .input { flex: 1; }
.form-actions { display: flex; justify-content: flex-end; gap: 0.5rem; }

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 0.45rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.82rem;
}

.btn-guardar {
  background: var(--accent);
  border: none;
  color: white;
  padding: 0.45rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.82rem;
}

/* ── Tarjetas ── */
.tareas-lista { display: flex; flex-direction: column; gap: 0.6rem; }

.tarea-card {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem;
  transition: border-color 0.2s;
}
.tarea-card:hover     { border-color: var(--accent); }
.tarea-card.completada { opacity: 0.5; }
.tarea-card.completada .tarea-titulo { text-decoration: line-through; }

.check {
  width: 24px; height: 24px;
  border-radius: 50%;
  border: 2px solid var(--accent);
  background: transparent;
  cursor: pointer;
  color: var(--accent-light);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem;
  flex-shrink: 0;
  margin-top: 2px;
  transition: background 0.2s;
}
.check:hover { background: var(--accent-soft); }
.check.done  { background: var(--accent-soft); border-color: var(--accent); }

.tarea-body { flex: 1; min-width: 0; }

.tarea-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 4px;
}

.tarea-titulo { font-size: 0.9rem; color: var(--text-primary); }

.tarea-badges { display: flex; gap: 5px; flex-shrink: 0; }

.badge-cat, .badge-pri {
  font-size: 0.68rem;
  padding: 2px 8px;
  border-radius: 20px;
  font-weight: 500;
  white-space: nowrap;
}

.badge-cat.estudio  { background: var(--blue-soft); color: var(--blue); }
.badge-cat.personal { background: #1a0c3b; color: #c084fc; }
.badge-cat.trabajo  { background: #0c2a1a; color: #34d399; }
.badge-cat.general  { background: var(--bg-input); color: var(--accent-light); }

.badge-pri.alta  { background: var(--red-soft); color: var(--red); }
.badge-pri.media { background: var(--yellow-soft); color: var(--yellow); }
.badge-pri.baja  { background: var(--green-soft); color: var(--green); }

.tarea-desc { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 6px; }

.tarea-meta { font-size: 0.75rem; color: var(--text-muted); }
.vencida    { color: var(--red); }

.btn-del {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.8rem;
  padding: 4px;
  transition: color 0.2s;
  flex-shrink: 0;
}
.btn-del:hover { color: var(--red); }

.empty-state {
  text-align: center;
  padding: 4rem;
  color: var(--text-muted);
  font-size: 2.5rem;
}
.empty-state p { font-size: 0.9rem; color: var(--text-muted); margin-top: 0.5rem; }

.cargando { padding: 2rem; text-align: center; color: var(--text-muted); }

/* ── Transition ── */
.slide-enter-active, .slide-leave-active { transition: all 0.25s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-10px); }
</style>