<template>
  <div class="pomo-page">

    <div class="pomo-header">
      <h1>Pomodoro</h1>
      <p class="sub">Sesión {{ sesion }} · {{ pomosHoy }} pomodoros hoy</p>
    </div>

    <!-- Modo selector -->
    <div class="modo-tabs">
      <button
        v-for="m in modos"
        :key="m.id"
        class="modo-tab"
        :class="{ active: modoActivo === m.id }"
        @click="cambiarModo(m)"
      >{{ m.label }}</button>
    </div>

    <!-- Timer central -->
    <div class="timer-wrap">
      <svg class="timer-ring" viewBox="0 0 200 200">
        <circle cx="100" cy="100" r="88" class="ring-bg" />
        <circle
          cx="100" cy="100" r="88"
          class="ring-fill"
          :class="modoActivo"
          :stroke-dasharray="circunferencia"
          :stroke-dashoffset="dashOffset"
        />
      </svg>

      <div class="timer-inner">
        <span class="timer-display">{{ tiempoDisplay }}</span>
        <span class="timer-modo">{{ modos.find(m => m.id === modoActivo)?.label }}</span>
      </div>
    </div>

    <!-- Controles -->
    <div class="timer-controls">
      <button class="ctrl-btn secondary" @click="resetear">↺</button>
      <button class="ctrl-btn primary" @click="toggleTimer">
        {{ corriendo ? '⏸' : '▶' }}
      </button>
      <button class="ctrl-btn secondary" @click="saltar">⏭</button>
    </div>

    <!-- Config tiempos -->
    <div class="config-section">
      <h3>Configuración</h3>
      <div class="config-grid">
        <div class="config-item" v-for="c in config" :key="c.id">
          <label>{{ c.label }}</label>
          <div class="num-input">
            <button @click="c.valor > 1 && c.valor--; if (c.id === modoActivo) reiniciarTiempo()">−</button>
            <span>{{ c.valor }} min</span>
            <button @click="c.valor < 60 && c.valor++; if (c.id === modoActivo) reiniciarTiempo()">+</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Historial de sesiones -->
    <div class="historial-section">
      <h3>Sesiones de hoy</h3>
      <div class="pomo-dots">
        <div
          v-for="n in pomosHoy"
          :key="n"
          class="pomo-dot completado"
        ></div>
        <div
          v-for="n in Math.max(0, 8 - pomosHoy)"
          :key="'p-' + n"
          class="pomo-dot pendiente"
        ></div>
      </div>
      <p class="historial-nota">Meta diaria: 8 pomodoros (4 horas de enfoque)</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'

const BACKEND = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'

const modos = [
  { id: 'pomodoro',   label: 'Pomodoro',      minutos: 25 },
  { id: 'descanso',   label: 'Descanso corto', minutos: 5  },
  { id: 'largo',      label: 'Descanso largo', minutos: 15 },
]

const config = ref([
  { id: 'pomodoro', label: 'Pomodoro',       valor: 25 },
  { id: 'descanso', label: 'Descanso corto', valor: 5  },
  { id: 'largo',    label: 'Descanso largo', valor: 15 },
])

const modoActivo = ref('pomodoro')
const corriendo  = ref(false)
const segundos   = ref(25 * 60)
const sesion     = ref(1)
const pomosHoy   = ref(0)
let intervalo    = null

const circunferencia = 2 * Math.PI * 88  // ≈ 553

const totalSegundos = computed(() => {
  const c = config.value.find(c => c.id === modoActivo.value)
  return (c?.valor ?? 25) * 60
})

const dashOffset = computed(() => {
  const pct = segundos.value / totalSegundos.value
  return circunferencia * (1 - pct)
})

const tiempoDisplay = computed(() => {
  const m = Math.floor(segundos.value / 60).toString().padStart(2, '0')
  const s = (segundos.value % 60).toString().padStart(2, '0')
  return `${m}:${s}`
})

function toggleTimer() {
  if (corriendo.value) {
    clearInterval(intervalo)
    corriendo.value = false
  } else {
    corriendo.value = true
    intervalo = setInterval(() => {
      if (segundos.value > 0) {
        segundos.value--
      } else {
        finalizarSesion()
      }
    }, 1000)
  }
}

function finalizarSesion() {
  clearInterval(intervalo)
  corriendo.value = false
  if (modoActivo.value === 'pomodoro') {
    pomosHoy.value++
    sesion.value++
    guardarSesion()
  }
  // Auto-pasar al descanso
  if (modoActivo.value === 'pomodoro') {
    cambiarModo(modos.find(m => m.id === (sesion.value % 4 === 0 ? 'largo' : 'descanso')))
  } else {
    cambiarModo(modos.find(m => m.id === 'pomodoro'))
  }
}

function cambiarModo(m) {
  clearInterval(intervalo)
  corriendo.value  = false
  modoActivo.value = m.id
  reiniciarTiempo()
}

function reiniciarTiempo() {
  const c = config.value.find(c => c.id === modoActivo.value)
  segundos.value = (c?.valor ?? 25) * 60
}

function resetear() {
  clearInterval(intervalo)
  corriendo.value = false
  reiniciarTiempo()
}

function saltar() {
  clearInterval(intervalo)
  corriendo.value = false
  const idx = modos.findIndex(m => m.id === modoActivo.value)
  cambiarModo(modos[(idx + 1) % modos.length])
}

async function guardarSesion() {
  try {
    await fetch(`${BACKEND}/api/pomodoros`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fecha: new Date().toISOString().slice(0, 10),
        minutos: config.value.find(c => c.id === 'pomodoro')?.valor ?? 25
      })
    })
  } catch {}
}

onUnmounted(() => clearInterval(intervalo))
</script>

<style scoped>
.pomo-page {
  padding: 2rem;
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.pomo-header { text-align: center; }

.pomo-header h1 {
  font-family: 'Syne', sans-serif;
  font-size: 1.8rem;
  color: var(--text-primary);
}

.sub { font-size: 0.85rem; color: var(--text-muted); margin-top: 4px; }

/* ── Modo tabs ── */
.modo-tabs { display: flex; gap: 8px; }

.modo-tab {
  padding: 0.4rem 1.1rem;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.82rem;
  transition: all 0.2s;
}
.modo-tab:hover  { border-color: var(--accent); color: var(--accent-light); }
.modo-tab.active { background: var(--accent-soft); border-color: var(--accent); color: var(--accent-light); }

/* ── Timer ── */
.timer-wrap {
  position: relative;
  width: 220px; height: 220px;
}

.timer-ring {
  width: 100%; height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: var(--bg-input);
  stroke-width: 10;
}

.ring-fill {
  fill: none;
  stroke-width: 10;
  stroke-linecap: round;
  transition: stroke-dashoffset 1s linear;
}
.ring-fill.pomodoro { stroke: var(--accent-light); }
.ring-fill.descanso { stroke: var(--green); }
.ring-fill.largo    { stroke: var(--blue); }

.timer-inner {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.timer-display {
  font-family: 'Syne', sans-serif;
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 2px;
}

.timer-modo {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 4px;
}

/* ── Controles ── */
.timer-controls { display: flex; gap: 1rem; align-items: center; }

.ctrl-btn {
  border: none;
  cursor: pointer;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
  font-size: 1rem;
}

.ctrl-btn.primary {
  width: 60px; height: 60px;
  background: var(--accent);
  color: var(--text-primary);
  font-size: 1.3rem;
}
.ctrl-btn.primary:hover { background: var(--accent); }

.ctrl-btn.secondary {
  width: 44px; height: 44px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-secondary);
}
.ctrl-btn.secondary:hover { background: var(--bg-input); color: var(--accent-light); }

/* ── Config ── */
.config-section {
  width: 100%;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.25rem;
}

.config-section h3,
.historial-section h3 {
  font-family: 'Syne', sans-serif;
  font-size: 0.9rem;
  color: var(--accent-light);
  margin-bottom: 1rem;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
}

.config-item label { font-size: 0.75rem; color: var(--text-muted); text-align: center; }

.num-input {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.35rem 0.6rem;
}

.num-input button {
  background: transparent;
  border: none;
  color: var(--accent-light);
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  transition: color 0.2s;
}
.num-input button:hover { color: var(--text-primary); }
.num-input span { font-size: 0.82rem; color: var(--text-primary); min-width: 48px; text-align: center; }

/* ── Historial ── */
.historial-section { width: 100%; }

.pomo-dots {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.pomo-dot {
  width: 28px; height: 28px;
  border-radius: 50%;
}
.pomo-dot.completado { background: var(--accent); }
.pomo-dot.pendiente  { background: var(--bg-input); border: 1px solid var(--border); }

.historial-nota { font-size: 0.78rem; color: var(--text-muted); }
</style>