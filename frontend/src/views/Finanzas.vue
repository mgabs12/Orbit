<template>
  <div class="fin-page">

    <div class="fin-header">
      <div>
        <h1>Finanzas</h1>
        <p class="sub">Control de gastos personales</p>
      </div>
      <button class="btn-nueva" @click="mostrarForm = !mostrarForm">+ Registrar</button>
    </div>

    <!-- Resumen -->
    <div class="resumen-grid">
      <div class="resumen-card ingresos">
        <span class="rc-label">Ingresos</span>
        <span class="rc-valor">Q {{ formatNum(totalIngresos) }}</span>
      </div>
      <div class="resumen-card gastos">
        <span class="rc-label">Gastos</span>
        <span class="rc-valor">Q {{ formatNum(totalGastos) }}</span>
      </div>
      <div class="resumen-card" :class="balance >= 0 ? 'balance-pos' : 'balance-neg'">
        <span class="rc-label">Balance</span>
        <span class="rc-valor">Q {{ formatNum(balance) }}</span>
      </div>
    </div>

    <!-- Barra visual ingresos vs gastos -->
    <div class="bar-comparativa" v-if="totalIngresos + totalGastos > 0">
      <div
        class="bar-seg ingresos"
        :style="{ width: pctIngresos + '%' }"
        :title="`Ingresos: Q${formatNum(totalIngresos)}`"
      ></div>
      <div
        class="bar-seg gastos"
        :style="{ width: pctGastos + '%' }"
        :title="`Gastos: Q${formatNum(totalGastos)}`"
      ></div>
    </div>

    <!-- Formulario -->
    <transition name="slide">
      <div v-if="mostrarForm" class="fin-form">
        <div class="tipo-toggle">
          <button :class="{ active: form.tipo === 'ingreso' }" @click="form.tipo = 'ingreso'">Ingreso</button>
          <button :class="{ active: form.tipo === 'gasto' }"   @click="form.tipo = 'gasto'">Gasto</button>
        </div>
        <div class="form-row">
          <input v-model="form.descripcion" class="input" placeholder="Descripción *" />
          <input v-model.number="form.monto" class="input" type="number" placeholder="Monto (Q) *" min="0" step="0.01" />
        </div>
        <div class="form-row">
          <select v-model="form.categoria" class="input select">
            <option v-for="cat in categorias[form.tipo]" :key="cat" :value="cat">{{ cat }}</option>
          </select>
          <input v-model="form.fecha" class="input" type="date" />
        </div>
        <div class="form-actions">
          <button class="btn-cancel" @click="mostrarForm = false; resetForm()">Cancelar</button>
          <button class="btn-guardar" @click="guardarMovimiento">Guardar</button>
        </div>
      </div>
    </transition>

    <!-- Filtros -->
    <div class="filtros">
      <button
        v-for="f in ['todos','ingreso','gasto']"
        :key="f"
        class="filtro-btn"
        :class="{ active: filtro === f }"
        @click="filtro = f"
      >{{ f === 'todos' ? 'Todos' : f === 'ingreso' ? 'Ingresos' : 'Gastos' }}</button>
    </div>

    <!-- Lista de movimientos -->
    <div class="movimientos-lista" v-if="!cargando">
      <div
        v-for="m in movimientosFiltrados"
        :key="m._id"
        class="mov-item"
        :class="m.tipo"
      >
        <div class="mov-icono" :class="m.tipo">
          {{ m.tipo === 'ingreso' ? '↑' : '↓' }}
        </div>
        <div class="mov-info">
          <span class="mov-desc">{{ m.descripcion }}</span>
          <div class="mov-meta">
            <span class="mov-cat">{{ m.categoria }}</span>
            <span class="mov-fecha">{{ formatFecha(m.fecha) }}</span>
          </div>
        </div>
        <span class="mov-monto" :class="m.tipo">
          {{ m.tipo === 'ingreso' ? '+' : '-' }} Q {{ formatNum(m.monto) }}
        </span>
        <button class="btn-del" @click="eliminarMovimiento(m._id)">✕</button>
      </div>

      <div v-if="movimientosFiltrados.length === 0" class="empty-state">
        <span>₿</span>
        <p>No hay movimientos registrados</p>
      </div>
    </div>

    <div v-else class="cargando">Cargando movimientos...</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const BACKEND = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'

const movimientos = ref([])
const cargando    = ref(true)
const mostrarForm = ref(false)
const filtro      = ref('todos')

const form = ref({ tipo: 'gasto', descripcion: '', monto: '', categoria: 'Alimentación', fecha: new Date().toISOString().slice(0, 10) })

const categorias = {
  ingreso: ['Salario', 'Beca', 'Freelance', 'Regalo', 'Otro ingreso'],
  gasto:   ['Alimentación', 'Transporte', 'Educación', 'Entretenimiento', 'Salud', 'Servicios', 'Otro gasto']
}

const totalIngresos = computed(() =>
  movimientos.value.filter(m => m.tipo === 'ingreso').reduce((a, m) => a + m.monto, 0)
)
const totalGastos = computed(() =>
  movimientos.value.filter(m => m.tipo === 'gasto').reduce((a, m) => a + m.monto, 0)
)
const balance = computed(() => totalIngresos.value - totalGastos.value)

const total = computed(() => totalIngresos.value + totalGastos.value)
const pctIngresos = computed(() => total.value ? (totalIngresos.value / total.value) * 100 : 0)
const pctGastos   = computed(() => total.value ? (totalGastos.value   / total.value) * 100 : 0)

const movimientosFiltrados = computed(() => {
  if (filtro.value === 'todos') return movimientos.value
  return movimientos.value.filter(m => m.tipo === filtro.value)
})

function formatNum(n) {
  return Number(n).toLocaleString('es-GT', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatFecha(f) {
  if (!f) return ''
  return new Date(f + 'T12:00:00').toLocaleDateString('es-GT', { day: 'numeric', month: 'short', year: 'numeric' })
}

function resetForm() {
  form.value = { tipo: 'gasto', descripcion: '', monto: '', categoria: 'Alimentación', fecha: new Date().toISOString().slice(0, 10) }
}

async function cargarMovimientos() {
  try {
    const res = await fetch(`${BACKEND}/api/finanzas`)
    movimientos.value = await res.json()
  } catch {} finally {
    cargando.value = false
  }
}

async function guardarMovimiento() {
  if (!form.value.descripcion.trim() || !form.value.monto) return
  try {
    await fetch(`${BACKEND}/api/finanzas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form.value, monto: Number(form.value.monto) })
    })
    resetForm()
    mostrarForm.value = false
    await cargarMovimientos()
  } catch {}
}

async function eliminarMovimiento(id) {
  try {
    await fetch(`${BACKEND}/api/finanzas/${id}`, { method: 'DELETE' })
    await cargarMovimientos()
  } catch {}
}

onMounted(cargarMovimientos)
</script>

<style scoped>
.fin-page { padding: 2rem; max-width: 860px; }

.fin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.fin-header h1 {
  font-family: 'Syne', sans-serif;
  font-size: 1.8rem;
  color: var(--text-primary);
}

.sub { font-size: 0.85rem; color: var(--text-muted); margin-top: 4px; }

.btn-nueva {
  background: var(--accent); color: var(--text-primary); border: none;
  padding: 0.55rem 1.2rem; border-radius: 9px;
  cursor: pointer; font-size: 0.88rem; transition: background 0.2s;
}
.btn-nueva:hover { background: var(--accent); }

/* ── Resumen ── */
.resumen-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.resumen-card {
  border-radius: 14px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.resumen-card.ingresos   { background: var(--green-soft); }
.resumen-card.gastos     { background: var(--red-soft); }
.resumen-card.balance-pos { background: var(--blue-soft); }
.resumen-card.balance-neg { background: #2a0a0a; }

.rc-label { font-size: 0.78rem; color: var(--text-muted); }
.rc-valor {
  font-family: 'Syne', sans-serif;
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--text-primary);
}

/* ── Barra ── */
.bar-comparativa {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}
.bar-seg { height: 100%; transition: width 0.5s ease; }
.bar-seg.ingresos { background: var(--green); }
.bar-seg.gastos   { background: var(--red); }

/* ── Form ── */
.fin-form {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.tipo-toggle {
  display: flex;
  gap: 8px;
  background: var(--bg-input);
  padding: 4px;
  border-radius: 10px;
  align-self: flex-start;
}

.tipo-toggle button {
  padding: 0.4rem 1.2rem;
  border-radius: 7px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.tipo-toggle button.active {
  background: var(--accent-soft);
  color: var(--accent-light);
  font-weight: 500;
}

.input {
  background: var(--bg-input); border: 1px solid var(--border);
  border-radius: 8px; padding: 0.6rem 0.75rem;
  color: var(--text-primary); font-size: 0.88rem; width: 100%; outline: none;
}
.input:focus { border-color: var(--accent); }
.select      { cursor: pointer; }
.form-row    { display: flex; gap: 0.75rem; }
.form-row .input { flex: 1; }
.form-actions { display: flex; justify-content: flex-end; gap: 0.5rem; }

.btn-cancel {
  background: transparent; border: 1px solid var(--border);
  color: var(--text-secondary); padding: 0.45rem 1rem; border-radius: 8px; cursor: pointer; font-size: 0.82rem;
}
.btn-guardar {
  background: var(--accent); border: none; color: white;
  padding: 0.45rem 1.2rem; border-radius: 8px; cursor: pointer; font-size: 0.82rem;
}

/* ── Filtros ── */
.filtros {
  display: flex;
  gap: 8px;
  margin-bottom: 1rem;
}

.filtro-btn {
  padding: 0.35rem 1rem; border-radius: 20px;
  border: 1px solid var(--border); background: transparent;
  color: var(--text-secondary); cursor: pointer; font-size: 0.82rem; transition: all 0.2s;
}
.filtro-btn:hover  { border-color: var(--accent); color: var(--accent-light); }
.filtro-btn.active { background: var(--accent-soft); border-color: var(--accent); color: var(--accent-light); }

/* ── Movimientos ── */
.movimientos-lista { display: flex; flex-direction: column; gap: 0.5rem; }

.mov-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.85rem 1rem;
  transition: border-color 0.2s;
}
.mov-item:hover { border-color: var(--accent); }

.mov-icono {
  width: 36px; height: 36px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1rem;
  flex-shrink: 0;
}
.mov-icono.ingreso { background: var(--green-soft); color: var(--green); }
.mov-icono.gasto   { background: var(--red-soft); color: var(--red); }

.mov-info { flex: 1; min-width: 0; }
.mov-desc { font-size: 0.9rem; color: var(--text-primary); display: block; }
.mov-meta { display: flex; gap: 0.75rem; margin-top: 2px; }
.mov-cat  { font-size: 0.72rem; color: var(--text-muted); }
.mov-fecha{ font-size: 0.72rem; color: var(--text-muted); }

.mov-monto {
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  white-space: nowrap;
}
.mov-monto.ingreso { color: var(--green); }
.mov-monto.gasto   { color: var(--red); }

.btn-del {
  background: transparent; border: none;
  color: var(--text-muted); cursor: pointer; font-size: 0.8rem;
  transition: color 0.2s; padding: 4px;
}
.btn-del:hover { color: var(--red); }

.empty-state {
  text-align: center;
  padding: 4rem; color: var(--text-muted); font-size: 2.5rem;
}
.empty-state p { font-size: 0.9rem; color: var(--text-muted); margin-top: 0.5rem; }

.cargando { padding: 2rem; text-align: center; color: var(--text-muted); }

/* ── Transition ── */
.slide-enter-active, .slide-leave-active { transition: all 0.25s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-10px); }
</style>