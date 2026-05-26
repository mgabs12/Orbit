<template>
  <div class="notas-page">

    <!-- ══════════════════════════════════════════
         PANEL 1: CUADERNOS
    ══════════════════════════════════════════ -->
    <aside class="notebooks-panel">

      <div class="panel-title">
        <span>📚 Cuadernos</span>
      </div>

      <!-- Botón crear cuaderno — siempre visible -->
      <button class="btn-nuevo-cuaderno" @click="mostrarFormCuaderno = !mostrarFormCuaderno">
        <span class="btn-nc-icon">+</span>
        <span>Nuevo cuaderno</span>
      </button>

      <!-- Formulario inline -->
      <transition name="slide">
        <div v-if="mostrarFormCuaderno" class="form-cuaderno">
          <input
            ref="inputCuaderno"
            v-model="nuevoCuaderno"
            class="input-cuaderno"
            placeholder="Nombre del cuaderno..."
            @keyup.enter="crearCuaderno"
            @keyup.esc="cancelarFormCuaderno"
            maxlength="40"
          />
          <div class="form-cuaderno-acciones">
            <button class="btn-cancelar-c" @click="cancelarFormCuaderno">Cancelar</button>
            <button class="btn-crear-c"    @click="crearCuaderno" :disabled="!nuevoCuaderno.trim()">Crear</button>
          </div>
        </div>
      </transition>

      <!-- Separador -->
      <div class="separator" v-if="cuadernos.length > 0"></div>

      <!-- Lista de cuadernos -->
      <div class="notebooks-list">
        <div
          v-for="c in cuadernos"
          :key="c._id"
          class="notebook-item"
          :class="{ active: cuadernoActivo?._id === c._id }"
          @click="seleccionarCuaderno(c)"
        >
          <span class="nb-emoji">📓</span>
          <div class="nb-info">
            <span class="nb-nombre">{{ c.nombre }}</span>
            <span class="nb-count">{{ notasDeCuaderno(c._id).length }} notas</span>
          </div>
          <button
            class="nb-delete"
            title="Eliminar cuaderno"
            @click.stop="confirmarEliminarCuaderno(c)"
          >✕</button>
        </div>

        <!-- Estado vacío -->
        <div v-if="cuadernos.length === 0 && !mostrarFormCuaderno" class="empty-cuadernos">
          <div class="empty-icon">📓</div>
          <p>No tenés cuadernos todavía</p>
          <span>Usá el botón de arriba para crear uno</span>
        </div>
      </div>
    </aside>

    <!-- ══════════════════════════════════════════
         PANEL 2: NOTAS DEL CUADERNO
    ══════════════════════════════════════════ -->
    <aside class="notes-panel">

      <!-- Header del panel -->
      <div class="notes-panel-header">
        <div class="notes-panel-title">
          <span class="notes-cuaderno-nombre">
            {{ cuadernoActivo ? cuadernoActivo.nombre : 'Notas' }}
          </span>
          <span class="notes-count" v-if="cuadernoActivo">
            {{ notasActuales.length }} notas
          </span>
        </div>
        <button
          class="btn-nueva-nota"
          :disabled="!cuadernoActivo"
          @click="nuevaNota"
          title="Nueva nota en este cuaderno"
        >
          + Nueva nota
        </button>
      </div>

      <!-- Lista de notas -->
      <div class="notes-list">
        <div
          v-for="n in notasActuales"
          :key="n._id"
          class="note-thumb"
          :class="{ active: notaActiva?._id === n._id }"
          @click="seleccionarNota(n)"
        >
          <div class="nt-title">{{ n.titulo || 'Sin título' }}</div>
          <div class="nt-preview">{{ limpiarMarkdown(n.contenido) }}</div>
          <div class="nt-date">{{ formatFecha(n.fecha) }}</div>
        </div>

        <!-- Estado vacío con cuaderno seleccionado -->
        <div v-if="cuadernoActivo && notasActuales.length === 0" class="empty-notas">
          <div class="empty-icon">✏️</div>
          <p>Este cuaderno está vacío</p>
          <button class="btn-primera-nota" @click="nuevaNota">+ Crear primera nota</button>
        </div>

        <!-- Sin cuaderno seleccionado -->
        <div v-if="!cuadernoActivo" class="empty-notas">
          <div class="empty-icon">👈</div>
          <p>Seleccioná un cuaderno</p>
        </div>
      </div>
    </aside>

    <!-- ══════════════════════════════════════════
         PANEL 3: EDITOR
    ══════════════════════════════════════════ -->
    <main class="editor-panel">
      <template v-if="notaActiva">

        <!-- Header del editor -->
        <div class="editor-header">
          <input
            v-model="notaActiva.titulo"
            class="editor-title-input"
            placeholder="Título de la nota"
            @input="marcarCambio"
          />
          <div class="editor-acciones">
            <span class="save-badge" :class="{ guardado: !pendiente }">
              {{ pendiente ? '● Sin guardar' : '✓ Guardado' }}
            </span>
            <button class="btn-guardar" @click="guardarNota">Guardar</button>
            <button class="btn-eliminar" @click="eliminarNota">Eliminar</button>
          </div>
        </div>

        <!-- Toolbar Markdown -->
        <div class="toolbar">
          <span class="toolbar-label">Formato:</span>
          <button @click="wrap('**','**')" title="Negrita"><b>B</b></button>
          <button @click="wrap('*','*')"   title="Cursiva"><i>I</i></button>
          <button @click="wrap('`','`')"   title="Código">{ }</button>
          <div class="toolbar-sep"></div>
          <button @click="insertLine('## ')"  title="Encabezado">H2</button>
          <button @click="insertLine('### ')" title="Subencabezado">H3</button>
          <button @click="insertLine('- ')"   title="Lista">≡</button>
          <button @click="insertLine('- [ ] ')" title="Checklist">☐</button>
          <button @click="insertLine('> ')"   title="Cita">❝</button>
          <button @click="insertLine('---\n')" title="Separador">—</button>
        </div>

        <!-- Área de texto -->
        <textarea
          ref="editorRef"
          v-model="notaActiva.contenido"
          class="editor-area"
          placeholder="Empezá a escribir tu nota aquí...

Soporta Markdown:
## Encabezados
**negrita**, *cursiva*
- listas
- [ ] checklists
> citas"
          @input="marcarCambio"
          @keydown.tab.prevent="insertarTab"
        ></textarea>

        <!-- Footer: adjuntar imagen + AI -->
        <div class="editor-footer">
          <label class="btn-adjuntar">
            📎 Adjuntar imagen
            <input type="file" accept="image/*" @change="adjuntarImagen" style="display:none" />
          </label>
          <div class="imagenes-adjuntas">
            <span
              v-for="(img, i) in notaActiva.imagenes"
              :key="i"
              class="img-tag"
            >🖼 {{ img.length > 18 ? img.slice(0,18)+'…' : img }}</span>
          </div>
          <button class="btn-ai-toggle" @click="mostrarAI = !mostrarAI" :class="{ active: mostrarAI }">
            ✦ AI Studio
          </button>
        </div>

      </template>

      <!-- Estado vacío del editor -->
      <div v-else class="editor-empty">
        <div class="editor-empty-icon">◻</div>
        <p v-if="!cuadernoActivo">Seleccioná un cuaderno para empezar</p>
        <p v-else>Seleccioná o creá una nota</p>
      </div>
    </main>

    <!-- ══════════════════════════════════════
         PANEL 4: AI STUDIO
    ══════════════════════════════════════ -->
    <transition name="ai-slide">
      <aside class="ai-panel" v-if="mostrarAI && notaActiva">
        <div class="ai-header">
          <div class="ai-title"><span class="ai-icon">✦</span><span>AI Studio</span></div>
          <button class="ai-close" @click="mostrarAI = false">✕</button>
        </div>
        <div class="ai-no-key" v-if="!aiDisponible">
          <span>⚠️</span>
          <p>Agregá <code>ANTHROPIC_API_KEY=tu_key</code> al <code>.env</code> para usar AI Studio.</p>
          <a href="https://console.anthropic.com" target="_blank" class="ai-link">Obtener API key →</a>
        </div>
        <div class="ai-tools" v-else>
          <button v-for="tool in aiTools" :key="tool.id"
            class="ai-tool-btn"
            :class="{ active: aiToolActiva === tool.id, loading: aiCargando && aiToolActiva === tool.id }"
            @click="ejecutarAI(tool)" :disabled="aiCargando">
            <span class="tool-icon">{{ tool.icon }}</span>
            <div class="tool-info">
              <span class="tool-name">{{ tool.nombre }}</span>
              <span class="tool-desc">{{ tool.desc }}</span>
            </div>
            <span class="tool-arrow" v-if="!aiCargando || aiToolActiva !== tool.id">›</span>
            <span class="tool-spinner" v-else>⟳</span>
          </button>
        </div>
        <transition name="fade">
          <div class="ai-resultado" v-if="aiResultado">
            <div class="ai-res-header">
              <span class="ai-res-tipo">{{ aiResultadoTipo }}</span>
              <button class="ai-res-copy" @click="copiarResultado">{{ copiado ? "✓ Copiado" : "⎘ Copiar" }}</button>
              <button class="ai-res-close" @click="aiResultado = null">✕</button>
            </div>
            <div v-if="tipoResultado === 'texto'" class="ai-res-texto">{{ aiResultado }}</div>
            <div v-else-if="tipoResultado === 'flashcards'" class="ai-flashcards">
              <div v-for="(card, i) in aiResultado" :key="i"
                class="flashcard" :class="{ flipped: cardFlipped[i] }" @click="flipCard(i)">
                <div class="fc-front"><span class="fc-num">{{ i + 1 }}</span><p>{{ card.pregunta }}</p><span class="fc-hint">Toca para ver respuesta</span></div>
                <div class="fc-back"><p>{{ card.respuesta }}</p></div>
              </div>
            </div>
            <div v-else-if="tipoResultado === 'cuestionario'" class="ai-quiz">
              <div v-for="(q, qi) in aiResultado" :key="qi" class="quiz-item">
                <p class="quiz-pregunta">{{ qi + 1 }}. {{ q.pregunta }}</p>
                <div class="quiz-opciones">
                  <button v-for="(op, oi) in q.opciones" :key="oi" class="quiz-opcion"
                    :class="{ correcta: quizRespuestas[qi] !== undefined && oi === q.correcta, incorrecta: quizRespuestas[qi] !== undefined && quizRespuestas[qi] === oi && oi !== q.correcta }"
                    @click="responderQuiz(qi, oi)" :disabled="quizRespuestas[qi] !== undefined">{{ op }}</button>
                </div>
              </div>
            </div>
            <div v-else-if="tipoResultado === 'puntos'" class="ai-puntos">
              <div v-for="(p, i) in aiResultado" :key="i" class="punto-item">
                <span class="punto-dot">◆</span><span>{{ p }}</span>
              </div>
            </div>
            <div v-else-if="tipoResultado === 'mapa'" class="ai-mapa">
              <div class="mapa-central">{{ aiResultado.tema_central }}</div>
              <div class="mapa-ramas">
                <div v-for="(rama, i) in aiResultado.ramas" :key="i" class="mapa-rama">
                  <div class="rama-titulo">{{ rama.titulo }}</div>
                  <div class="rama-subtemas">
                    <span v-for="(sub, j) in rama.subtemas" :key="j" class="subtema">{{ sub }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <div class="ai-error" v-if="aiError">⚠️ {{ aiError }}</div>
      </aside>
    </transition>

    <!-- Modal confirmar eliminar cuaderno -->
    <div v-if="cuadernoAEliminar" class="modal-overlay" @click.self="cuadernoAEliminar = null">
      <div class="modal">
        <h3>¿Eliminar cuaderno?</h3>
        <p>Se eliminará <strong>{{ cuadernoAEliminar.nombre }}</strong> y todas sus notas. Esta acción no se puede deshacer.</p>
        <div class="modal-actions">
          <button class="btn-cancelar-c" @click="cuadernoAEliminar = null">Cancelar</button>
          <button class="btn-eliminar-confirm" @click="eliminarCuaderno">Sí, eliminar</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { apiFetch } from '../auth.js'
import { ref, computed, onMounted, nextTick } from 'vue'


// ── Estado ──────────────────────────────────────────────────
const cuadernos          = ref([])
const notas              = ref([])
const cuadernoActivo     = ref(null)
const notaActiva         = ref(null)
const mostrarFormCuaderno = ref(false)
const nuevoCuaderno      = ref('')
const pendiente          = ref(false)
const cuadernoAEliminar  = ref(null)
const editorRef          = ref(null)
const inputCuaderno      = ref(null)

// ── Computed ─────────────────────────────────────────────────
const notasActuales = computed(() =>
  cuadernoActivo.value
    ? notas.value.filter(n => n.cuaderno_id === cuadernoActivo.value._id)
    : []
)

function notasDeCuaderno(id) {
  return notas.value.filter(n => n.cuaderno_id === id)
}

// ── Helpers ──────────────────────────────────────────────────
function formatFecha(f) {
  if (!f) return ''
  return new Date(f).toLocaleDateString('es-GT', { day: 'numeric', month: 'short', year: 'numeric' })
}

function limpiarMarkdown(texto) {
  if (!texto) return 'Nota vacía...'
  return texto
    .replace(/#{1,6}\s/g, '')
    .replace(/\*\*/g, '')
    .replace(/\*/g, '')
    .replace(/`/g, '')
    .replace(/>/g, '')
    .replace(/- \[ \] /g, '')
    .replace(/---/g, '')
    .slice(0, 80)
}

function marcarCambio() { pendiente.value = true }

function cancelarFormCuaderno() {
  mostrarFormCuaderno.value = false
  nuevoCuaderno.value = ''
}

// ── CUADERNOS ────────────────────────────────────────────────
async function cargarCuadernos() {
  try {
    const res = await apiFetch(`/api/cuadernos`)
    cuadernos.value = await res.json()
  } catch (e) { console.error('Error cargando cuadernos:', e) }
}

async function crearCuaderno() {
  if (!nuevoCuaderno.value.trim()) return
  try {
    await apiFetch(`/api/cuadernos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre: nuevoCuaderno.value.trim() })
    })
    nuevoCuaderno.value = ''
    mostrarFormCuaderno.value = false
    await cargarCuadernos()
  } catch (e) { console.error('Error creando cuaderno:', e) }
}

function seleccionarCuaderno(c) {
  cuadernoActivo.value = c
  notaActiva.value = null
  pendiente.value = false
}

function confirmarEliminarCuaderno(c) {
  cuadernoAEliminar.value = c
}

async function eliminarCuaderno() {
  if (!cuadernoAEliminar.value) return
  try {
    await apiFetch(`/api/cuadernos/${cuadernoAEliminar.value._id}`, { method: 'DELETE' })
    if (cuadernoActivo.value?._id === cuadernoAEliminar.value._id) {
      cuadernoActivo.value = null
      notaActiva.value = null
    }
    cuadernoAEliminar.value = null
    await cargarCuadernos()
    await cargarNotas()
  } catch (e) { console.error('Error eliminando cuaderno:', e) }
}

// ── NOTAS ────────────────────────────────────────────────────
async function cargarNotas() {
  try {
    const res = await apiFetch(`/api/notas`)
    notas.value = await res.json()
  } catch (e) { console.error('Error cargando notas:', e) }
}

async function nuevaNota() {
  if (!cuadernoActivo.value) return
  try {
    const res = await apiFetch(`/api/notas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        titulo: 'Nueva nota',
        contenido: '',
        cuaderno_id: cuadernoActivo.value._id,
        imagenes: []
      })
    })
    const creada = await res.json()
    await cargarNotas()
    // Seleccionar la nota recién creada
    const encontrada = notas.value.find(n => n._id === creada._id)
    notaActiva.value = encontrada ? { ...encontrada } : { ...creada }
    pendiente.value = false
  } catch (e) { console.error('Error creando nota:', e) }
}

function seleccionarNota(n) {
  notaActiva.value = { ...n }
  pendiente.value = false
}

async function guardarNota() {
  if (!notaActiva.value) return
  try {
    await apiFetch(`/api/notas/${notaActiva.value._id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        titulo:    notaActiva.value.titulo,
        contenido: notaActiva.value.contenido,
        imagenes:  notaActiva.value.imagenes || []
      })
    })
    pendiente.value = false
    await cargarNotas()
  } catch (e) { console.error('Error guardando nota:', e) }
}

async function eliminarNota() {
  if (!notaActiva.value) return
  try {
    await apiFetch(`/api/notas/${notaActiva.value._id}`, { method: 'DELETE' })
    notaActiva.value = null
    await cargarNotas()
  } catch (e) { console.error('Error eliminando nota:', e) }
}

// ── Editor helpers ───────────────────────────────────────────
function wrap(pre, post) {
  const ta = editorRef.value
  if (!ta || !notaActiva.value) return
  const start = ta.selectionStart
  const end   = ta.selectionEnd
  const sel   = notaActiva.value.contenido.slice(start, end)
  notaActiva.value.contenido =
    notaActiva.value.contenido.slice(0, start) + pre + sel + post +
    notaActiva.value.contenido.slice(end)
  marcarCambio()
  nextTick(() => { ta.focus(); ta.setSelectionRange(start + pre.length, end + pre.length) })
}

function insertLine(prefix) {
  const ta = editorRef.value
  if (!ta || !notaActiva.value) return
  const pos    = ta.selectionStart
  const before = notaActiva.value.contenido.slice(0, pos)
  const after  = notaActiva.value.contenido.slice(pos)
  notaActiva.value.contenido = before + '\n' + prefix + after
  marcarCambio()
  nextTick(() => { ta.focus(); ta.setSelectionRange(pos + prefix.length + 1, pos + prefix.length + 1) })
}

function insertarTab() {
  const ta = editorRef.value
  if (!ta || !notaActiva.value) return
  const pos = ta.selectionStart
  notaActiva.value.contenido =
    notaActiva.value.contenido.slice(0, pos) + '  ' + notaActiva.value.contenido.slice(pos)
  marcarCambio()
  nextTick(() => ta.setSelectionRange(pos + 2, pos + 2))
}

function adjuntarImagen(e) {
  const file = e.target.files[0]
  if (!file || !notaActiva.value) return
  const reader = new FileReader()
  reader.onload = () => {
    notaActiva.value.imagenes = notaActiva.value.imagenes || []
    notaActiva.value.imagenes.push(file.name)
    notaActiva.value.contenido += `\n\n![${file.name}](${reader.result})\n`
    marcarCambio()
  }
  reader.readAsDataURL(file)
  e.target.value = ''
}

// ── Mostrar form y enfocar input ─────────────────────────────
async function abrirFormCuaderno() {
  mostrarFormCuaderno.value = true
  await nextTick()
  inputCuaderno.value?.focus()
}

// Watcher: cuando se abre el form, enfocar el input
import { watch } from 'vue'
watch(mostrarFormCuaderno, async (val) => {
  if (val) {
    await nextTick()
    inputCuaderno.value?.focus()
  }
})

onMounted(async () => {
  await cargarCuadernos()
  await cargarNotas()
  verificarAI()
})

// ── AI STUDIO ───────────────────────────────────────────────
const mostrarAI      = ref(false)
const aiDisponible   = ref(false)
const aiCargando     = ref(false)
const aiToolActiva   = ref(null)
const aiResultado    = ref(null)
const aiResultadoTipo = ref('')
const tipoResultado  = ref('')
const aiError        = ref(null)
const copiado        = ref(false)
const cardFlipped    = ref([])
const quizRespuestas = ref({})

const aiTools = [
  { id: 'resumen',      icon: '📄', nombre: 'Resumen',      desc: 'Resume el contenido de la nota',      endpoint: '/api/ai/resumen',      tipo: 'texto',      label: 'Resumen' },
  { id: 'puntos-clave', icon: '◆',  nombre: 'Puntos clave', desc: 'Extrae los conceptos importantes',    endpoint: '/api/ai/puntos-clave', tipo: 'puntos',     label: 'Puntos clave' },
  { id: 'flashcards',   icon: '🃏', nombre: 'Flashcards',   desc: 'Tarjetas de memorización',            endpoint: '/api/ai/flashcards',   tipo: 'flashcards', label: 'Flashcards' },
  { id: 'cuestionario', icon: '❓', nombre: 'Cuestionario', desc: 'Preguntas de opción múltiple',        endpoint: '/api/ai/cuestionario', tipo: 'cuestionario', label: 'Cuestionario' },
  { id: 'mapa-mental',  icon: '🗺', nombre: 'Mapa mental',  desc: 'Estructura jerárquica del contenido', endpoint: '/api/ai/mapa-mental',  tipo: 'mapa',       label: 'Mapa mental' },
]

async function verificarAI() {
  try {
    const res = await apiFetch(`/api/ai/status`)
    const data = await res.json()
    aiDisponible.value = data.disponible
  } catch { aiDisponible.value = false }
}

async function ejecutarAI(tool) {
  const texto = notaActiva.value?.contenido?.trim()
  if (!texto) { aiError.value = 'La nota está vacía. Escribí algo primero.'; return }
  if (texto.length < 30) { aiError.value = 'El texto es muy corto. Necesita más contenido.'; return }

  aiCargando.value  = true
  aiToolActiva.value = tool.id
  aiResultado.value = null
  aiError.value     = null
  cardFlipped.value = []
  quizRespuestas.value = {}

  try {
    const res  = await fetch(`${BACKEND}${tool.endpoint}`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ texto, cantidad: 6 })
    })
    const data = await res.json()
    if (data.error) { aiError.value = data.error; return }

    aiResultado.value   = data.resultado
    aiResultadoTipo.value = tool.label
    tipoResultado.value = tool.tipo

    if (tool.tipo === 'flashcards' && Array.isArray(data.resultado)) {
      cardFlipped.value = new Array(data.resultado.length).fill(false)
    }
  } catch(e) {
    aiError.value = 'Error conectando con el servidor'
  } finally {
    aiCargando.value = false
  }
}

function flipCard(i) {
  const arr = [...cardFlipped.value]
  arr[i] = !arr[i]
  cardFlipped.value = arr
}

function responderQuiz(qi, oi) {
  if (quizRespuestas.value[qi] !== undefined) return
  quizRespuestas.value = { ...quizRespuestas.value, [qi]: oi }
}

async function copiarResultado() {
  try {
    let texto = ''
    if (typeof aiResultado.value === 'string') {
      texto = aiResultado.value
    } else if (Array.isArray(aiResultado.value)) {
      if (tipoResultado.value === 'flashcards') {
        texto = aiResultado.value.map((c,i) => `${i+1}. P: ${c.pregunta}\nR: ${c.respuesta}`).join('\n\n')
      } else if (tipoResultado.value === 'puntos') {
        texto = aiResultado.value.map(p => `• ${p}`).join('\n')
      }
    } else if (tipoResultado.value === 'mapa') {
      texto = aiResultado.value.tema_central + '\n' + aiResultado.value.ramas.map(r => `  ${r.titulo}: ${r.subtemas.join(', ')}`).join('\n')
    }
    await navigator.clipboard.writeText(texto)
    copiado.value = true
    setTimeout(() => copiado.value = false, 2000)
  } catch {}
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════
   LAYOUT GENERAL
═══════════════════════════════════════════════ */
.notas-page {
  display: flex;
  height: 100vh;
  overflow: hidden;
  position: relative;
}

/* ═══════════════════════════════════════════════
   PANEL 1 — CUADERNOS
═══════════════════════════════════════════════ */
.notebooks-panel {
  width: 220px;
  flex-shrink: 0;
  background: var(--bg-card);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-title {
  padding: 1.2rem 1rem 0.75rem;
  font-family: 'Syne', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* Botón principal de crear cuaderno */
.btn-nuevo-cuaderno {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0.75rem 0.75rem;
  padding: 0.6rem 0.85rem;
  background: var(--accent-soft);
  border: 1px dashed var(--accent);
  border-radius: 10px;
  color: var(--accent-light);
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
  width: calc(100% - 1.5rem);
}
.btn-nuevo-cuaderno:hover {
  background: var(--accent-soft);
  border-color: var(--accent-light);
  color: var(--text-primary);
}

.btn-nc-icon {
  font-size: 1.2rem;
  font-weight: 300;
  color: var(--accent-light);
  line-height: 1;
}

/* Formulario crear cuaderno */
.form-cuaderno {
  margin: 0 0.75rem 0.75rem;
  background: var(--bg-input);
  border: 1px solid var(--accent);
  border-radius: 10px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.input-cuaderno {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 0.55rem 0.7rem;
  color: var(--text-primary);
  font-size: 0.88rem;
  outline: none;
  width: 100%;
  font-family: 'DM Sans', sans-serif;
}
.input-cuaderno:focus { border-color: var(--accent); }

.form-cuaderno-acciones {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}

.btn-cancelar-c {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.78rem;
  transition: all 0.15s;
}
.btn-cancelar-c:hover { border-color: var(--text-muted); color: var(--accent-light); }

.btn-crear-c {
  background: var(--accent);
  border: none;
  color: var(--text-primary);
  padding: 0.35rem 0.9rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.78rem;
  font-weight: 500;
  transition: background 0.15s;
}
.btn-crear-c:hover:not(:disabled) { background: var(--accent); }
.btn-crear-c:disabled { opacity: 0.4; cursor: not-allowed; }

.separator {
  height: 1px;
  background: var(--border);
  margin: 0 0.75rem 0.5rem;
}

/* Lista de cuadernos */
.notebooks-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.25rem 0.5rem 1rem;
}

.notebook-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.65rem 0.75rem;
  border-radius: 9px;
  cursor: pointer;
  transition: background 0.15s;
  border: 1px solid transparent;
  margin-bottom: 3px;
}
.notebook-item:hover  { background: var(--bg-input); }
.notebook-item.active { background: var(--accent-soft); border-color: var(--accent); }

.nb-emoji { font-size: 1rem; flex-shrink: 0; }

.nb-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.nb-nombre {
  font-size: 0.85rem;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nb-count { font-size: 0.7rem; color: var(--text-muted); margin-top: 1px; }

.nb-delete {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.7rem;
  padding: 3px 5px;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.15s;
  flex-shrink: 0;
}
.notebook-item:hover .nb-delete { opacity: 1; }
.nb-delete:hover { color: var(--red); background: var(--red-soft)22; }

/* Estado vacío cuadernos */
.empty-cuadernos {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--text-muted);
}
.empty-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.empty-cuadernos p { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.3rem; }
.empty-cuadernos span { font-size: 0.75rem; color: var(--text-muted); }

/* ═══════════════════════════════════════════════
   PANEL 2 — NOTAS
═══════════════════════════════════════════════ */
.notes-panel {
  width: 260px;
  flex-shrink: 0;
  background: var(--bg-app);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.notes-panel-header {
  padding: 1rem 0.85rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.notes-panel-title {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}

.notes-cuaderno-nombre {
  font-family: 'Syne', sans-serif;
  font-size: 0.9rem;
  color: var(--accent-light);
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notes-count {
  font-size: 0.72rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.btn-nueva-nota {
  width: 100%;
  padding: 0.5rem;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--accent-light);
  cursor: pointer;
  font-size: 0.82rem;
  transition: all 0.2s;
  text-align: center;
}
.btn-nueva-nota:hover:not(:disabled) {
  background: var(--accent-soft);
  border-color: var(--accent);
  color: var(--text-primary);
}
.btn-nueva-nota:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* Lista notas */
.notes-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.note-thumb {
  padding: 0.75rem;
  border-radius: 9px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s;
  margin-bottom: 4px;
}
.note-thumb:hover  { background: var(--bg-card-hover); border-color: var(--border); }
.note-thumb.active { background: var(--bg-input); border-color: var(--accent); }

.nt-title {
  font-size: 0.87rem;
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nt-preview {
  font-size: 0.76rem;
  color: var(--text-muted);
  line-height: 1.4;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.nt-date { font-size: 0.7rem; color: var(--text-muted); }

/* Estado vacío notas */
.empty-notas {
  text-align: center;
  padding: 2.5rem 1rem;
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.empty-notas p { font-size: 0.85rem; color: var(--text-muted); }

.btn-primera-nota {
  margin-top: 0.5rem;
  background: var(--accent-soft);
  border: 1px solid var(--accent);
  color: var(--accent-light);
  padding: 0.45rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.82rem;
  transition: all 0.2s;
}
.btn-primera-nota:hover { background: var(--accent-soft); }

/* ═══════════════════════════════════════════════
   PANEL 3 — EDITOR
═══════════════════════════════════════════════ */
.editor-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-app);
}

.editor-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.editor-title-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-family: 'Syne', sans-serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
  min-width: 0;
}

.editor-acciones {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
}

.save-badge {
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
  transition: color 0.3s;
}
.save-badge.guardado { color: var(--green); }

.btn-guardar {
  background: var(--accent);
  border: none;
  color: var(--text-primary);
  padding: 0.4rem 0.9rem;
  border-radius: 7px;
  cursor: pointer;
  font-size: 0.82rem;
  transition: background 0.2s;
}
.btn-guardar:hover { background: var(--accent); }

.btn-eliminar {
  background: transparent;
  border: 1px solid var(--red-soft);
  color: var(--red);
  padding: 0.4rem 0.7rem;
  border-radius: 7px;
  cursor: pointer;
  font-size: 0.82rem;
  transition: background 0.2s;
}
.btn-eliminar:hover { background: var(--red-soft); }

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 0.45rem 1.5rem;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  flex-wrap: wrap;
}

.toolbar-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-right: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.toolbar-sep {
  width: 1px;
  height: 18px;
  background: var(--border);
  margin: 0 4px;
}

.toolbar button {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  min-width: 30px;
  height: 26px;
  padding: 0 6px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.78rem;
  transition: all 0.15s;
}
.toolbar button:hover {
  background: var(--accent-soft);
  color: var(--accent-light);
  border-color: var(--accent);
}

/* Área de texto */
.editor-area {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  padding: 1.5rem;
  color: var(--text-primary);
  font-family: 'DM Mono', 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.8;
}

/* Footer */
.editor-footer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 1.5rem;
  border-top: 1px solid var(--border);
  flex-shrink: 0;
  flex-wrap: wrap;
}

.btn-adjuntar {
  font-size: 0.78rem;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.3rem 0.7rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  transition: all 0.2s;
  white-space: nowrap;
}
.btn-adjuntar:hover { border-color: var(--accent); color: var(--accent-light); }

.imagenes-adjuntas { display: flex; gap: 6px; flex-wrap: wrap; }

.img-tag {
  font-size: 0.72rem;
  color: var(--text-muted);
  background: var(--bg-input);
  padding: 2px 8px;
  border-radius: 10px;
}

/* Estado vacío editor */
.editor-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}
.editor-empty-icon { font-size: 3rem; color: var(--border); }
.editor-empty p    { font-size: 0.9rem; color: var(--text-muted); }

/* ═══════════════════════════════════════════════
   MODAL CONFIRMAR ELIMINAR
═══════════════════════════════════════════════ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(5, 3, 15, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: var(--bg-card-hover);
  border: 1px solid var(--accent);
  border-radius: 14px;
  padding: 1.75rem;
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.modal h3 {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.modal p {
  font-size: 0.88rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.modal strong { color: var(--accent-light); }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 0.5rem;
}

.btn-eliminar-confirm {
  background: var(--red-soft);
  border: none;
  color: var(--red);
  padding: 0.45rem 1rem;
  border-radius: 7px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
}
.btn-eliminar-confirm:hover { background: var(--red-soft); }

/* ═══════════════════════════════════════════════
   TRANSICIONES
═══════════════════════════════════════════════ */
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-8px); }


/* ═══════════════════════════════════════════════
   BOTON AI STUDIO (en footer del editor)
═══════════════════════════════════════════════ */
.btn-ai-toggle {
  margin-left: auto;
  padding: 0.3rem 0.85rem;
  border-radius: 20px;
  border: 1px solid var(--accent);
  background: transparent;
  color: var(--accent);
  cursor: pointer;
  font-size: 0.78rem;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
  letter-spacing: 0.03em;
}
.btn-ai-toggle:hover, .btn-ai-toggle.active {
  background: var(--accent);
  color: #fff;
}

/* ═══════════════════════════════════════════════
   AI PANEL
═══════════════════════════════════════════════ */
.ai-panel {
  width: 320px;
  flex-shrink: 0;
  background: var(--bg-card);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
}

.ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1rem 0.75rem;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.ai-title {
  display: flex;
  align-items: center;
  gap: 7px;
  font-family: 'Syne', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
}

.ai-icon {
  color: var(--accent);
  font-size: 1rem;
}

.ai-close {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.8rem;
  padding: 4px 6px;
  border-radius: 5px;
  transition: all 0.15s;
}
.ai-close:hover { background: var(--red-soft); color: var(--red); }

/* Sin key */
.ai-no-key {
  margin: 1rem;
  padding: 1rem;
  background: var(--bg-input);
  border: 1px dashed var(--border);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.ai-no-key code {
  background: var(--bg-app);
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 0.75rem;
  color: var(--accent-light);
}

.ai-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.8rem;
}
.ai-link:hover { text-decoration: underline; }

/* Tools */
.ai-tools {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0.75rem;
}

.ai-tool-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0.75rem;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--bg-input);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  width: 100%;
}
.ai-tool-btn:hover:not(:disabled) {
  border-color: var(--accent);
  background: var(--accent-soft);
}
.ai-tool-btn.active { border-color: var(--accent); background: var(--accent-soft); }
.ai-tool-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.tool-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
  width: 26px;
  text-align: center;
}

.tool-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.tool-name { font-size: 0.85rem; color: var(--text-primary); font-weight: 500; }
.tool-desc { font-size: 0.72rem; color: var(--text-muted); }

.tool-arrow { color: var(--text-muted); font-size: 1rem; }
.tool-spinner { color: var(--accent); font-size: 0.9rem; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Resultado */
.ai-resultado {
  margin: 0.75rem;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}

.ai-res-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid var(--border);
  background: var(--bg-app);
}

.ai-res-tipo {
  flex: 1;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--accent-light);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.ai-res-copy {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 2px 8px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.72rem;
  transition: all 0.15s;
}
.ai-res-copy:hover { border-color: var(--accent); color: var(--accent); }

.ai-res-close {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.75rem;
  padding: 2px 4px;
}

/* Texto */
.ai-res-texto {
  padding: 0.85rem;
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.65;
  white-space: pre-wrap;
}

/* Flashcards */
.ai-flashcards {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.flashcard {
  position: relative;
  min-height: 90px;
  cursor: pointer;
  perspective: 600px;
}

.fc-front, .fc-back {
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.82rem;
  line-height: 1.5;
  transition: opacity 0.25s;
}

.fc-front {
  background: var(--accent-soft);
  border: 1px solid var(--accent);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.fc-back {
  background: var(--green-soft);
  border: 1px solid var(--green);
  color: var(--text-primary);
  display: none;
}

.flashcard.flipped .fc-front { display: none; }
.flashcard.flipped .fc-back  { display: block; }

.fc-num {
  font-size: 0.65rem;
  color: var(--accent-light);
  font-weight: 700;
}

.fc-hint {
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-top: 4px;
}

/* Quiz */
.ai-quiz {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.quiz-item {}

.quiz-pregunta {
  font-size: 0.82rem;
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.quiz-opciones {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.quiz-opcion {
  text-align: left;
  padding: 0.45rem 0.65rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg-app);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.78rem;
  transition: all 0.15s;
}
.quiz-opcion:hover:not(:disabled) { border-color: var(--accent); color: var(--text-primary); }
.quiz-opcion:disabled { cursor: default; }
.quiz-opcion.correcta  { background: var(--green-soft); border-color: var(--green); color: var(--green); }
.quiz-opcion.incorrecta { background: var(--red-soft); border-color: var(--red); color: var(--red); }

/* Puntos clave */
.ai-puntos {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.punto-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.punto-dot { color: var(--accent); flex-shrink: 0; font-size: 0.6rem; margin-top: 5px; }

/* Mapa mental */
.ai-mapa { padding: 0.75rem; }

.mapa-central {
  text-align: center;
  background: var(--accent);
  color: #fff;
  padding: 0.6rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.85rem;
  margin-bottom: 0.75rem;
}

.mapa-ramas { display: flex; flex-direction: column; gap: 6px; }

.mapa-rama {
  background: var(--bg-app);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.6rem;
}

.rama-titulo {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent-light);
  margin-bottom: 5px;
}

.rama-subtemas { display: flex; flex-wrap: wrap; gap: 4px; }

.subtema {
  font-size: 0.72rem;
  background: var(--accent-soft);
  color: var(--text-secondary);
  padding: 2px 8px;
  border-radius: 10px;
}

/* Error */
.ai-error {
  margin: 0.75rem;
  padding: 0.75rem;
  background: var(--red-soft);
  border: 1px solid var(--red);
  border-radius: 8px;
  font-size: 0.8rem;
  color: var(--red);
}

/* Transiciones */
.ai-slide-enter-active, .ai-slide-leave-active { transition: all 0.25s ease; }
.ai-slide-enter-from, .ai-slide-leave-to { opacity: 0; transform: translateX(20px); width: 0; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

</style>