<template>
  <div class="app" :class="tema">

    <aside class="sidebar">

      <!-- Logo ORBIT -->
      <div class="logo">
        <div class="logo-mark">
          <span class="logo-ring"></span>
          <span class="logo-dot"></span>
        </div>
        <span class="logo-text">ORBIT</span>
      </div>

      <!-- Nav items -->
      <nav class="nav">
        <button
          v-for="item in navItems"
          :key="item.id"
          class="nav-item"
          :class="{ active: activeSection === item.id }"
          @click="activeSection = item.id"
        >
          <span class="nav-icon">
            <svg v-if="item.id==='dashboard'" viewBox="0 0 20 20" fill="currentColor"><path d="M3 4a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 8a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H4a1 1 0 01-1-1v-4zm8-8a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V4zm0 8a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/></svg>
            <svg v-else-if="item.id==='notas'" viewBox="0 0 20 20" fill="currentColor"><path d="M4 3a1 1 0 000 2h12a1 1 0 100-2H4zm0 4a1 1 0 000 2h12a1 1 0 100-2H4zm0 4a1 1 0 000 2h8a1 1 0 100-2H4z"/></svg>
            <svg v-else-if="item.id==='tareas'" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
            <svg v-else-if="item.id==='calendario'" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/></svg>
            <svg v-else-if="item.id==='pomodoro'" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/></svg>
            <svg v-else-if="item.id==='finanzas'" viewBox="0 0 20 20" fill="currentColor"><path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/></svg>
          </span>
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="activeSection === item.id" class="nav-active-pill"></span>
        </button>
      </nav>

      <!-- Footer: tema + usuario -->
      <div class="sidebar-footer">
        <div class="user-row">
          <div class="user-avatar">OR</div>
          <div class="user-info">
            <span class="user-name">Mi cuenta</span>
            <span class="user-role">ORBIT</span>
          </div>
          <!-- Toggle modo oscuro/claro -->
          <button class="theme-toggle" @click="toggleTema" :title="temaOscuro ? 'Modo claro' : 'Modo oscuro'">
            <svg v-if="temaOscuro" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"/>
            </svg>
            <svg v-else viewBox="0 0 20 20" fill="currentColor">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>
            </svg>
          </button>
        </div>
      </div>

    </aside>

    <main class="main-content">
      <Dashboard    v-if="activeSection === 'dashboard'" />
      <Notas        v-else-if="activeSection === 'notas'" />
      <Tareas       v-else-if="activeSection === 'tareas'" />
      <Calendario   v-else-if="activeSection === 'calendario'" />
      <Pomodoro     v-else-if="activeSection === 'pomodoro'" />
      <Finanzas     v-else-if="activeSection === 'finanzas'" />
    </main>

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Dashboard  from './views/Dashboard.vue'
import Notas      from './views/Notas.vue'
import Tareas     from './views/Tareas.vue'
import Calendario from './views/Calendario.vue'
import Pomodoro   from './views/Pomodoro.vue'
import Finanzas   from './views/Finanzas.vue'

const activeSection = ref('dashboard')
const temaOscuro    = ref(true)
const tema          = computed(() => temaOscuro.value ? 'dark' : 'light')

function toggleTema() {
  temaOscuro.value = !temaOscuro.value
  localStorage.setItem('orbit-tema', temaOscuro.value ? 'dark' : 'light')
}

// Restaurar tema guardado
const temaGuardado = localStorage.getItem('orbit-tema')
if (temaGuardado) temaOscuro.value = temaGuardado === 'dark'

const navItems = [
  { id: 'dashboard',  label: 'Dashboard' },
  { id: 'notas',      label: 'Notas' },
  { id: 'tareas',     label: 'Tareas' },
  { id: 'calendario', label: 'Calendario' },
  { id: 'pomodoro',   label: 'Pomodoro' },
  { id: 'finanzas',   label: 'Finanzas' },
]
</script>

<style>
/* ═══════════════════════════════════════════════
   FUENTES
═══════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,400&display=swap');

/* ═══════════════════════════════════════════════
   VARIABLES — MODO OSCURO (default)
═══════════════════════════════════════════════ */
.dark {
  --bg-app:        #0d0b1e;
  --bg-sidebar:    #110e26;
  --bg-card:       #17132e;
  --bg-card-hover: #1e1a38;
  --bg-input:      #1e1a38;
  --bg-active:     #2a1f5c;

  --border:        #2a2455;
  --border-focus:  #7c5cfc;

  --text-primary:  #eeeaff;
  --text-secondary:#9b94c9;
  --text-muted:    #524d7a;

  --accent:        #7c5cfc;
  --accent-light:  #a78bfa;
  --accent-soft:   #2a1f5c;

  --yellow:        #f5a623;
  --yellow-soft:   #2e2000;
  --green:         #22c55e;
  --green-soft:    #052e16;
  --red:           #f87171;
  --red-soft:      #3b0a0a;
  --blue:          #60a5fa;
  --blue-soft:     #0c1a3b;

  --shadow:        0 4px 24px rgba(0,0,0,0.4);
  --radius:        14px;
}

/* ═══════════════════════════════════════════════
   VARIABLES — MODO CLARO
═══════════════════════════════════════════════ */
.light {
  --bg-app:        #f0eeff;
  --bg-sidebar:    #ffffff;
  --bg-card:       #ffffff;
  --bg-card-hover: #f5f3ff;
  --bg-input:      #f5f3ff;
  --bg-active:     #ede9fe;

  --border:        #e0daf5;
  --border-focus:  #7c5cfc;

  --text-primary:  #1a1535;
  --text-secondary:#6b5fa0;
  --text-muted:    #b0a8d0;

  --accent:        #7c5cfc;
  --accent-light:  #a78bfa;
  --accent-soft:   #ede9fe;

  --yellow:        #d97706;
  --yellow-soft:   #fef3c7;
  --green:         #16a34a;
  --green-soft:    #dcfce7;
  --red:           #dc2626;
  --red-soft:      #fee2e2;
  --blue:          #2563eb;
  --blue-soft:     #dbeafe;

  --shadow:        0 4px 24px rgba(100,80,200,0.10);
  --radius:        14px;
}

/* ═══════════════════════════════════════════════
   RESET & BASE
═══════════════════════════════════════════════ */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'DM Sans', sans-serif;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-app);
  color: var(--text-primary);
  transition: background 0.3s, color 0.3s;
}

/* ═══════════════════════════════════════════════
   APP LAYOUT
═══════════════════════════════════════════════ */
.app {
  display: flex;
  height: 100vh;
  background: var(--bg-app);
  transition: background 0.3s;
}

/* ═══════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════ */
.sidebar {
  width: 230px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  flex-shrink: 0;
  transition: background 0.3s, border-color 0.3s;
  box-shadow: var(--shadow);
  z-index: 10;
}

/* ── Logo ── */
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 2rem;
  padding: 0.25rem 0.5rem;
}

.logo-mark {
  position: relative;
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.logo-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2.5px solid var(--accent);
  animation: orbit-spin 8s linear infinite;
}

.logo-ring::after {
  content: '';
  position: absolute;
  width: 7px;
  height: 7px;
  background: var(--yellow);
  border-radius: 50%;
  top: -3px;
  left: 50%;
  transform: translateX(-50%);
}

.logo-dot {
  position: absolute;
  width: 10px;
  height: 10px;
  background: var(--accent);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

@keyframes orbit-spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.logo-text {
  font-family: 'Syne', sans-serif;
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: 0.08em;
}

/* ── Nav ── */
.nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 0.65rem 0.85rem;
  border-radius: 12px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  width: 100%;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  overflow: hidden;
}

.nav-item:hover {
  background: var(--bg-card-hover);
  color: var(--text-secondary);
}

.nav-item.active {
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 500;
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon svg {
  width: 18px;
  height: 18px;
}

.nav-label { font-size: 0.88rem; }

.nav-active-pill {
  position: absolute;
  right: 10px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
}

/* ── Footer ── */
.sidebar-footer {
  border-top: 1px solid var(--border);
  padding-top: 1rem;
  margin-top: 0.5rem;
}

.user-row {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 0.5rem 0.5rem;
  border-radius: 10px;
  transition: background 0.2s;
}
.user-row:hover { background: var(--bg-card-hover); }

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--yellow));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 700;
  flex-shrink: 0;
}

.user-info { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.user-name { font-size: 0.82rem; color: var(--text-primary); font-weight: 500; }
.user-role { font-size: 0.7rem;  color: var(--text-muted); }

/* Toggle tema */
.theme-toggle {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-input);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}
.theme-toggle:hover { background: var(--accent-soft); color: var(--accent); border-color: var(--accent); }
.theme-toggle svg { width: 15px; height: 15px; }

/* ═══════════════════════════════════════════════
   MAIN CONTENT
═══════════════════════════════════════════════ */
.main-content {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-app);
  transition: background 0.3s;
}

/* ═══════════════════════════════════════════════
   SCROLLBAR GLOBAL
═══════════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-light); }
</style>