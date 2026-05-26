<template>
  <div class="cal-page">

    <div class="cal-header">
      <div>
        <h1>Calendario</h1>
        <p class="sub">{{ mesLabel }} {{ anio }}</p>
      </div>
      <div class="cal-nav">
        <button class="nav-btn" @click="cambiarMes(-1)">‹</button>
        <button class="nav-btn hoy-btn" @click="irAHoy">Hoy</button>
        <button class="nav-btn" @click="cambiarMes(1)">›</button>
      </div>
    </div>

    <div class="cal-layout">
      <!-- Grid del calendario -->
      <div class="cal-grid-wrap">
        <!-- Días de la semana -->
        <div class="weekdays">
          <div v-for="d in diasSemana" :key="d" class="weekday">{{ d }}</div>
        </div>

        <!-- Celdas -->
        <div class="cal-grid">
          <div
            v-for="(celda, i) in celdas"
            :key="i"
            class="cal-cell"
            :class="{
              'otro-mes': !celda.esMes,
              'es-hoy':    celda.esHoy,
              'seleccionado': diaSeleccionado === celda.fecha
            }"
            @click="seleccionarDia(celda)"
          >
            <span class="cal-num">{{ celda.dia }}</span>
            <div class="cel-eventos">
              <div
                v-for="ev in eventosDelDia(celda.fecha)"
                :key="ev._id"
                class="cel-evento-dot"
                :class="ev.tipo"
                :title="ev.titulo"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Panel lateral: eventos del día seleccionado -->
      <aside class="events-panel">
        <div class="events-header">
          <h3>{{ diaSeleccionado ? formatFechaLarga(diaSeleccionado) : 'Selecciona un día' }}</h3>
          <button v-if="diaSeleccionado" class="btn-add-ev" @click="mostrarFormEvento = !mostrarFormEvento">+</button>
        </div>

        <!-- Form nuevo evento -->
        <div v-if="mostrarFormEvento" class="ev-form">
          <input v-model="formEvento.titulo" class="input" placeholder="Título del evento *" />
          <input v-model="formEvento.hora"   class="input" type="time" />
          <select v-model="formEvento.tipo"  class="input select">
            <option value="clase">📘 Clase</option>
            <option value="examen">📝 Examen</option>
            <option value="entrega">📌 Entrega</option>
            <option value="personal">👤 Personal</option>
          </select>
          <div class="form-actions">
            <button class="btn-cancel" @click="mostrarFormEvento = false">Cancelar</button>
            <button class="btn-guardar" @click="guardarEvento">Guardar</button>
          </div>
        </div>

        <!-- Lista de eventos del día -->
        <div class="events-list">
          <div
            v-for="ev in eventosDelDia(diaSeleccionado)"
            :key="ev._id"
            class="event-item"
            :class="ev.tipo"
          >
            <div class="ev-line" :class="ev.tipo"></div>
            <div class="ev-info">
              <span class="ev-titulo">{{ ev.titulo }}</span>
              <span class="ev-hora" v-if="ev.hora">{{ ev.hora }}</span>
            </div>
            <button class="btn-del-ev" @click="eliminarEvento(ev._id)">✕</button>
          </div>
          <div v-if="eventosDelDia(diaSeleccionado).length === 0 && diaSeleccionado" class="empty-ev">
            Sin eventos este día
          </div>
        </div>

        <!-- Tareas del día -->
        <div class="events-header" style="margin-top:1.5rem">
          <h3>Tareas de hoy</h3>
        </div>
        <div class="events-list">
          <div v-for="t in tareasDelDia" :key="t._id" class="event-item tarea-ev">
            <div class="ev-line entrega"></div>
            <div class="ev-info">
              <span class="ev-titulo">{{ t.titulo }}</span>
              <span class="badge-pri" :class="t.prioridad">{{ t.prioridad }}</span>
            </div>
          </div>
          <div v-if="tareasDelDia.length === 0 && diaSeleccionado" class="empty-ev">Sin tareas</div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const BACKEND = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'

const hoyDate   = new Date()
const mesActual = ref(hoyDate.getMonth())
const anio      = ref(hoyDate.getFullYear())
const eventos   = ref([])
const tareas    = ref([])
const diaSeleccionado  = ref(null)
const mostrarFormEvento = ref(false)

const formEvento = ref({ titulo: '', hora: '', tipo: 'clase' })

const diasSemana = ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb']

const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
               'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

const mesLabel = computed(() => meses[mesActual.value])

const celdas = computed(() => {
  const primero = new Date(anio.value, mesActual.value, 1)
  const ultimo  = new Date(anio.value, mesActual.value + 1, 0)
  const cells   = []

  // Días del mes anterior para completar la primera semana
  for (let i = 0; i < primero.getDay(); i++) {
    const d = new Date(anio.value, mesActual.value, -i)
    cells.unshift({ dia: d.getDate(), fecha: fmtDate(d), esMes: false, esHoy: false })
  }

  // Días del mes
  for (let d = 1; d <= ultimo.getDate(); d++) {
    const date = new Date(anio.value, mesActual.value, d)
    const fechaStr = fmtDate(date)
    cells.push({
      dia:   d,
      fecha: fechaStr,
      esMes: true,
      esHoy: fechaStr === fmtDate(hoyDate)
    })
  }

  // Rellenar hasta múltiplo de 7
  let extra = 1
  while (cells.length % 7 !== 0) {
    const d = new Date(anio.value, mesActual.value + 1, extra++)
    cells.push({ dia: d.getDate(), fecha: fmtDate(d), esMes: false, esHoy: false })
  }

  return cells
})

const tareasDelDia = computed(() => {
  if (!diaSeleccionado.value) return []
  return tareas.value.filter(t => t.fecha === diaSeleccionado.value && !t.completada)
})

function fmtDate(d) {
  return d.toISOString().slice(0, 10)
}

function formatFechaLarga(f) {
  return new Date(f + 'T12:00:00').toLocaleDateString('es-GT', {
    weekday: 'long', day: 'numeric', month: 'long'
  })
}

function cambiarMes(delta) {
  let m = mesActual.value + delta
  let a = anio.value
  if (m < 0) { m = 11; a-- }
  if (m > 11) { m = 0; a++ }
  mesActual.value = m
  anio.value = a
}

function irAHoy() {
  mesActual.value = hoyDate.getMonth()
  anio.value = hoyDate.getFullYear()
  diaSeleccionado.value = fmtDate(hoyDate)
}

function seleccionarDia(celda) {
  diaSeleccionado.value = celda.fecha
  mostrarFormEvento.value = false
}

function eventosDelDia(fecha) {
  if (!fecha) return []
  return eventos.value.filter(e => e.fecha === fecha)
}

// ── API ──
async function cargarEventos() {
  try {
    const res = await fetch(`${BACKEND}/api/eventos`)
    eventos.value = await res.json()
  } catch {}
}

async function cargarTareas() {
  try {
    const res = await fetch(`${BACKEND}/api/tareas`)
    tareas.value = await res.json()
  } catch {}
}

async function guardarEvento() {
  if (!formEvento.value.titulo.trim() || !diaSeleccionado.value) return
  try {
    await fetch(`${BACKEND}/api/eventos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...formEvento.value, fecha: diaSeleccionado.value })
    })
    formEvento.value = { titulo: '', hora: '', tipo: 'clase' }
    mostrarFormEvento.value = false
    await cargarEventos()
  } catch {}
}

async function eliminarEvento(id) {
  try {
    await fetch(`${BACKEND}/api/eventos/${id}`, { method: 'DELETE' })
    await cargarEventos()
  } catch {}
}

onMounted(() => {
  diaSeleccionado.value = fmtDate(hoyDate)
  cargarEventos()
  cargarTareas()
})
</script>

<style scoped>
.cal-page { padding: 2rem; height: 100%; display: flex; flex-direction: column; }

.cal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.cal-header h1 {
  font-family: 'Syne', sans-serif;
  font-size: 1.8rem;
  color: var(--text-primary);
}

.sub { font-size: 0.85rem; color: var(--text-muted); margin-top: 4px; }

.cal-nav { display: flex; gap: 8px; align-items: center; }

.nav-btn {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--accent-light);
  width: 34px; height: 34px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}
.nav-btn:hover { background: var(--accent-soft); }

.hoy-btn { width: auto; padding: 0 0.9rem; font-size: 0.82rem; }

/* ── Layout ── */
.cal-layout {
  display: flex;
  gap: 1.5rem;
  flex: 1;
  overflow: hidden;
}

.cal-grid-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* ── Grid ── */
.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 6px;
}

.weekday {
  text-align: center;
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 600;
  padding: 4px;
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  flex: 1;
}

.cal-cell {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  min-height: 70px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.cal-cell:hover    { border-color: var(--accent); }
.cal-cell.otro-mes { opacity: 0.3; }
.cal-cell.es-hoy   { border-color: var(--accent); background: #1a1040; }
.cal-cell.seleccionado { border-color: var(--accent-light); background: var(--accent-soft); }

.cal-num {
  font-size: 0.82rem;
  color: var(--accent-light);
  font-weight: 500;
}

.cal-cell.es-hoy .cal-num {
  color: var(--accent-light);
  font-weight: 700;
}

.cel-eventos { display: flex; flex-wrap: wrap; gap: 3px; }

.cel-evento-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
}
.cel-evento-dot.clase    { background: var(--blue); }
.cel-evento-dot.examen   { background: var(--red); }
.cel-evento-dot.entrega  { background: var(--yellow); }
.cel-evento-dot.personal { background: var(--accent-light); }

/* ── Panel lateral ── */
.events-panel {
  width: 260px;
  flex-shrink: 0;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.events-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.events-header h3 {
  font-family: 'Syne', sans-serif;
  font-size: 0.88rem;
  color: var(--accent-light);
}

.btn-add-ev {
  width: 24px; height: 24px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--accent-light);
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}
.btn-add-ev:hover { background: var(--accent-soft); }

.ev-form {
  background: var(--bg-input);
  border-radius: 10px;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 0.5rem 0.65rem;
  color: var(--text-primary);
  font-size: 0.82rem;
  width: 100%;
  outline: none;
}
.input:focus { border-color: var(--accent); }
.select { cursor: pointer; }

.form-actions { display: flex; justify-content: flex-end; gap: 0.5rem; }

.btn-cancel {
  background: transparent; border: 1px solid var(--border);
  color: var(--text-secondary); padding: 0.35rem 0.75rem;
  border-radius: 6px; cursor: pointer; font-size: 0.78rem;
}

.btn-guardar {
  background: var(--accent); border: none; color: white;
  padding: 0.35rem 0.9rem; border-radius: 6px;
  cursor: pointer; font-size: 0.78rem;
}

/* ── Events list ── */
.events-list { display: flex; flex-direction: column; gap: 6px; }

.event-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-input);
  border-radius: 8px;
  padding: 0.6rem 0.75rem;
}

.ev-line {
  width: 3px; height: 28px;
  border-radius: 2px;
  flex-shrink: 0;
}
.ev-line.clase    { background: var(--blue); }
.ev-line.examen   { background: var(--red); }
.ev-line.entrega  { background: var(--yellow); }
.ev-line.personal { background: var(--accent-light); }

.ev-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.ev-titulo { font-size: 0.82rem; color: var(--text-primary); }
.ev-hora   { font-size: 0.72rem; color: var(--text-muted); }

.badge-pri {
  font-size: 0.65rem;
  padding: 1px 6px;
  border-radius: 10px;
}
.badge-pri.alta  { background: var(--red-soft); color: var(--red); }
.badge-pri.media { background: var(--yellow-soft); color: var(--yellow); }
.badge-pri.baja  { background: var(--green-soft); color: var(--green); }

.btn-del-ev {
  background: transparent; border: none;
  color: var(--text-muted); cursor: pointer; font-size: 0.75rem;
  transition: color 0.2s;
}
.btn-del-ev:hover { color: var(--red); }

.empty-ev { font-size: 0.8rem; color: var(--text-muted); text-align: center; padding: 0.5rem; }
</style>