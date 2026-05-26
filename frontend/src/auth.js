// ─────────────────────────────────────────────────
// auth.js  — composable global de autenticación
// Uso en cualquier view:
//   import { useAuth, apiFetch } from '../auth.js'
//   const { usuario, cerrarSesion } = useAuth()
//   const data = await apiFetch('/api/tareas')
// ─────────────────────────────────────────────────

import { ref } from 'vue'

const BACKEND = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'

// Estado global reactivo (singleton)
const usuario = ref(null)   // { id, nombre, email, foto }
const token   = ref(null)

// Inicializar desde localStorage al cargar
function initAuth() {
  const t = localStorage.getItem('orbit-token')
  const u = localStorage.getItem('orbit-user')
  if (t && u) {
    token.value   = t
    usuario.value = JSON.parse(u)
  }
}

function guardarSesion(tok, user) {
  token.value   = tok
  usuario.value = user
  localStorage.setItem('orbit-token', tok)
  localStorage.setItem('orbit-user', JSON.stringify(user))
}

function cerrarSesion() {
  token.value   = null
  usuario.value = null
  localStorage.removeItem('orbit-token')
  localStorage.removeItem('orbit-user')
}

// fetch autenticado — reemplaza fetch() normal en todas las views
async function apiFetch(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }
  if (token.value) {
    headers['Authorization'] = `Bearer ${token.value}`
  }
  const res = await fetch(`${BACKEND}${path}`, { ...options, headers })

  // Token expirado → cerrar sesión
  if (res.status === 401) {
    cerrarSesion()
    window.location.reload()
    return null
  }
  return res
}

export function useAuth() {
  return { usuario, token, initAuth, guardarSesion, cerrarSesion }
}

export { apiFetch, BACKEND }