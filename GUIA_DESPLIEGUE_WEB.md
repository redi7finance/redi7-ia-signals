# Guía de Despliegue - REDI7 IA en la Web

## 🚀 GUÍA PASO A PASO PARA PRINCIPIANTES

### FASE 1: Preparación (5 minutos)

#### 1. Crear cuenta en GitHub (si no tienes)
- Ve a https://github.com
- Click en "Sign up"
- Usa tu email y crea contraseña
- Verifica tu email

#### 2. Crear cuenta en Streamlit Cloud
- Ve a https://share.streamlit.io
- Click en "Sign up with GitHub"
- Autoriza la conexión

---

### FASE 2: Subir tu código a GitHub (10 minutos)

#### 1. Instalar GitHub Desktop (la forma más fácil)
- Descarga: https://desktop.github.com
- Instala y abre la aplicación
- Inicia sesión con tu cuenta de GitHub

#### 2. Crear un nuevo repositorio
En GitHub Desktop:
- File > New Repository
- Name: `redi7-ia-signals`
- Description: `Sistema Profesional de Análisis de Trading`
- Local Path: Selecciona la carpeta de tu proyecto
- ✅ Initialize with README
- Click "Create Repository"

#### 3. Publicar a GitHub
- Click en "Publish repository"
- ✅ Marca como Private (para mantener tu código seguro)
- Click "Publish repository"

---

### FASE 3: Configurar Secretos (IMPORTANTE - 5 minutos)

Antes de desplegar, necesitas configurar las credenciales de forma segura.

#### Crear archivo de configuración para la web:

**Archivo: `secrets.toml`** (crear en la carpeta `.streamlit/`)

```toml
# API Keys
OPENAI_API_KEY = "tu-api-key-de-openai"

# Email Configuration
EMAIL_SENDER = "redi7soporte@gmail.com"
EMAIL_PASSWORD = "mnkuigggxljattdo"
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587

# Telegram (opcional)
TELEGRAM_BOT_TOKEN = "tu-bot-token"
TELEGRAM_CHAT_ID = "tu-chat-id"
```

---

### FASE 4: Desplegar en Streamlit Cloud (5 minutos)

#### 1. Ir a Streamlit Cloud
- Ve a https://share.streamlit.io
- Click en "New app"

#### 2. Configurar el despliegue
- Repository: Selecciona `redi7-ia-signals`
- Branch: `main`
- Main file path: `app_redi7.py`
- Click "Deploy!"

#### 3. Configurar Secretos
En Streamlit Cloud:
- Click en ⚙️ (Settings)
- Click en "Secrets"
- Pega el contenido del archivo `secrets.toml`
- Click "Save"

**¡Tu aplicación estará online en 2-3 minutos!**
La URL será: `https://tu-usuario-redi7-ia-signals.streamlit.app`

---

### FASE 5: Conectar tu Dominio de Hostinger (10 minutos)

#### 1. En Streamlit Cloud
- Copia la URL de tu app: `tu-app.streamlit.app`

#### 2. En Hostinger (Panel de Control)
- Ve a "Dominios"
- Click en tu dominio
- Ve a "DNS / Name Servers"

#### 3. Agregar registro CNAME
- Type: `CNAME`
- Name: `@` (o `www`)
- Points to: `tu-app.streamlit.app`
- TTL: `14400`
- Click "Add Record"

#### 4. Configurar en Streamlit
- En Settings de tu app en Streamlit Cloud
- Ve a "Custom domain"
- Ingresa tu dominio: `tudominio.com`
- Click "Add domain"

**Espera 24-48 horas para que el DNS se propague**

---

### ✅ CHECKLIST DE VERIFICACIÓN

Antes de desplegar, asegúrate de:
- [ ] Tener cuenta en GitHub
- [ ] Tener cuenta en Streamlit Cloud
- [ ] Código subido a GitHub (privado)
- [ ] Archivo secrets.toml configurado
- [ ] App desplegada en Streamlit Cloud
- [ ] Dominio configurado en Hostinger

---

### 🆘 SOLUCIÓN DE PROBLEMAS COMUNES

**Error: "No module named 'X'"**
- Solución: Verifica que todos los paquetes estén en `requirements.txt`

**Error: Base de datos no se crea**
- Solución: Streamlit Cloud usa almacenamiento temporal, la BD se creará automáticamente

**Dominio no funciona**
- Solución: Espera 24-48 horas para propagación DNS

---

### 📞 SOPORTE

Si necesitas ayuda:
1. Revisa logs en Streamlit Cloud (botón "Manage app" > "Logs")
2. Verifica que todos los secretos estén configurados
3. Confirma que requirements.txt tenga todos los paquetes

---

## 🎉 ¡FELICIDADES!

Tu aplicación REDI7 IA estará online y accesible desde cualquier parte del mundo.

**URLs:**
- Streamlit: `https://tu-app.streamlit.app`
- Tu dominio: `https://tudominio.com` (después de 24-48h)

---

**Fecha:** 4 de febrero de 2026
**Sistema:** REDI7 IA - Análisis de Trading Institucional
