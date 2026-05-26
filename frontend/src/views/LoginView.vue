<template>
  <div class="login-page" :class="tema">

    <!-- Fondo animado -->
    <div class="login-bg">
      <div class="bg-orb orb-1"></div>
      <div class="bg-orb orb-2"></div>
      <div class="bg-orb orb-3"></div>
    </div>

    <div class="login-card">

      <!-- Logo -->
      <div class="login-logo">
        <div class="logo-mark">
          <span class="logo-ring"></span>
          <span class="logo-dot"></span>
        </div>
        <span class="logo-text">ORBIT</span>
      </div>

      <h1 class="login-title">Bienvenido de vuelta</h1>
      <p class="login-sub">Tu espacio de estudio inteligente</p>

      <!-- Botón Google -->
      <button
        class="btn-google"
        @click="loginConGoogle"
        :disabled="cargando"
      >
        <span v-if="cargando" class="btn-spinner"></span>
        <svg v-else viewBox="0 0 48 48" width="20" height="20">
          <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
          <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
          <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
          <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.35-8.16 2.35-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
        </svg>
        {{ cargando ? 'Conectando...' : 'Continuar con Google' }}
      </button>

      <!-- Error -->
      <div class="login-error" v-if="error">
        <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
        </svg>
        {{ error }}
      </div>

      <p class="login-footer">
        Al continuar aceptas usar esta app con tu cuenta de Google.<br>
        No almacenamos tu contraseña.
      </p>

    </div>

    <!-- Toggle tema -->
    <button class="login-theme-btn" @click="toggleTema">
      <svg v-if="temaOscuro" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
        <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"/>
      </svg>
      <svg v-else viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
        <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>
      </svg>
    </button>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuth } from '../auth.js'

const BACKEND = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

const { guardarSesion } = useAuth()
const emit = defineEmits(['autenticado'])

const cargando   = ref(false)
const error      = ref('')
const temaOscuro = ref(localStorage.getItem('orbit-tema') !== 'light')
const tema       = computed(() => temaOscuro.value ? 'dark' : 'light')

function toggleTema() {
  temaOscuro.value = !temaOscuro.value
  localStorage.setItem('orbit-tema', temaOscuro.value ? 'dark' : 'light')
}

function loginConGoogle() {
  if (!GOOGLE_CLIENT_ID) {
    error.value = 'VITE_GOOGLE_CLIENT_ID no configurado en .env'
    return
  }
  cargando.value = true
  error.value = ''

  // Abrir popup de Google OAuth
  const redirectUri = `${window.location.origin}/auth/callback`
  const scope = 'openid email profile'
  const url = `https://accounts.google.com/o/oauth2/v2/auth?` +
    `client_id=${GOOGLE_CLIENT_ID}` +
    `&redirect_uri=${encodeURIComponent(redirectUri)}` +
    `&response_type=code` +
    `&scope=${encodeURIComponent(scope)}` +
    `&access_type=offline` +
    `&prompt=select_account`

  const popup = window.open(url, 'google-login', 'width=500,height=600,scrollbars=yes')

  // Escuchar mensaje del callback
  const handler = async (event) => {
    if (event.origin !== window.location.origin) return
    if (!event.data?.code) return

    window.removeEventListener('message', handler)
    popup?.close()

    try {
      const res  = await fetch(`${BACKEND}/api/auth/google`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ code: event.data.code, redirect_uri: redirectUri })
      })
      const data = await res.json()
      if (data.error) { error.value = data.error; return }

      guardarSesion(data.token, data.usuario)
      emit('autenticado', data.usuario)
    } catch (e) {
      error.value = 'Error al conectar con el servidor'
    } finally {
      cargando.value = false
    }
  }

  window.addEventListener('message', handler)

  // Detectar si el popup fue cerrado sin completar
  const poll = setInterval(() => {
    if (popup?.closed) {
      clearInterval(poll)
      cargando.value = false
      window.removeEventListener('message', handler)
    }
  }, 500)
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: var(--bg-app);
}

/* Fondo orbes */
.login-bg { position: absolute; inset: 0; z-index: 0; pointer-events: none; }
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.25;
}
.orb-1 { width: 500px; height: 500px; background: var(--accent); top: -150px; left: -150px; animation: float1 12s ease-in-out infinite; }
.orb-2 { width: 400px; height: 400px; background: var(--yellow); bottom: -100px; right: -100px; animation: float2 15s ease-in-out infinite; }
.orb-3 { width: 300px; height: 300px; background: var(--accent-light); top: 40%; left: 60%; animation: float1 10s ease-in-out infinite reverse; }
@keyframes float1 { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-30px); } }
@keyframes float2 { 0%,100% { transform: translateY(0); } 50% { transform: translateY(20px); } }

/* Card */
.login-card {
  position: relative;
  z-index: 1;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 2.5rem 2rem;
  width: 100%;
  max-width: 380px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--shadow), 0 0 60px rgba(124,92,252,0.08);
}

/* Logo */
.login-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0.5rem;
}
.logo-mark {
  position: relative;
  width: 36px; height: 36px;
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
  width: 8px; height: 8px;
  background: var(--yellow);
  border-radius: 50%;
  top: -4px; left: 50%;
  transform: translateX(-50%);
}
.logo-dot {
  position: absolute;
  width: 11px; height: 11px;
  background: var(--accent);
  border-radius: 50%;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
}
@keyframes orbit-spin { to { transform: rotate(360deg); } }
.logo-text {
  font-family: 'Syne', sans-serif;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: 0.08em;
}

/* Textos */
.login-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
}
.login-sub {
  font-size: 0.87rem;
  color: var(--text-muted);
  text-align: center;
  margin-top: -0.5rem;
}

/* Botón Google */
.btn-google {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.85rem 1.25rem;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--bg-input);
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  justify-content: center;
  margin-top: 0.5rem;
}
.btn-google:hover:not(:disabled) {
  border-color: var(--accent);
  background: var(--accent-soft);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(124,92,252,0.2);
}
.btn-google:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-spinner {
  width: 18px; height: 18px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Error */
.login-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.65rem 0.85rem;
  background: var(--red-soft);
  border: 1px solid var(--red);
  border-radius: 10px;
  color: var(--red);
  font-size: 0.82rem;
}

/* Footer */
.login-footer {
  font-size: 0.73rem;
  color: var(--text-muted);
  text-align: center;
  line-height: 1.6;
  margin-top: 0.25rem;
}

/* Tema toggle */
.login-theme-btn {
  position: fixed;
  top: 1.25rem;
  right: 1.25rem;
  width: 36px; height: 36px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
}
.login-theme-btn:hover { background: var(--accent-soft); color: var(--accent); border-color: var(--accent); }
</style>