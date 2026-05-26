# ── Etapa 1: Build con Node ──────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Recibir la URL del backend como argumento de build
# Vite necesita esto en tiempo de compilación, no en runtime
ARG VITE_BACKEND_URL=http://localhost:5000
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL

ARG VITE_GOOGLE_CLIENT_ID
ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID

# Copiar dependencias primero (aprovecha cache de Docker)
COPY package*.json ./
RUN npm install

# Copiar el resto del código fuente
COPY . .

# Construir para producción
RUN npm run build

# ── Etapa 2: Servir con Nginx ─────────────────────────────
FROM nginx:alpine

# Copiar el build de Vite al directorio de Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuración de Nginx para Vue SPA
RUN printf 'server {\n    listen 80;\n    root /usr/share/nginx/html;\n    index index.html;\n    location / {\n        try_files $uri $uri/ /index.html;\n    }\n}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]