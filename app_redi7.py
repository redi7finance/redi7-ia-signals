"""
REDI7 IA - Interfaz Gráfica Profesional
Dashboard para análisis de trading institucional con sistema multiusuario
"""

import streamlit as st
import os
from datetime import datetime
from redi7_ai import REDI7AI
from config import ACTIVOS_PERMITIDOS
from auth import AuthSystem
from admin_panel import show_admin_panel
from telegram_sender import TelegramSender
from PIL import Image
import io
import base64
import sqlite3
from temporalidades_config import get_config_temporalidades, get_num_imagenes_requeridas, get_detail_levels

# Configuración de la página
st.set_page_config(
    page_title="REDI7 AI - Análisis Institucional",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# CSS personalizado para estilo profesional
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1e3c72;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #2a5298;
        transform: scale(1.02);
    }
    .resultado-box {
        background-color: #0e1117;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1e3c72;
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .stFileUploader button[kind="primary"] {
        background-color: #1e3c72 !important;
        color: transparent !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 8px 16px !important;
        font-size: 0 !important;
        width: auto !important;
        min-width: 140px !important;
        position: relative !important;
    }
    .stFileUploader button[kind="primary"]::after {
        content: "Subir archivo" !important;
        color: #ffffff !important;
        font-size: 14px !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
    }
    .stFileUploader button[kind="primary"]:hover {
        background-color: #2a5298 !important;
    }
    .stFileUploader:has(button[kind="secondary"]) button[kind="primary"] {
        display: none !important;
    }
    .stFileUploader section {
        padding: 0 !important;
    }
    .stFileUploader div[data-testid="stFileDropzone"] {
        display: none !important;
    }
    .stFileUploader {
        padding: 0 !important;
    }
    .stFileUploader div[data-testid="stFileDropzone"] p {
        display: none !important;
    }
    .logo-circle {
        width: 96px;
        height: 96px;
        border-radius: 50%;
        object-fit: cover;
        display: block;
        margin: 0 auto 0.5rem auto;
        border: 2px solid #2a5298;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar sistema de autenticación
if 'auth' not in st.session_state:
    st.session_state.auth = AuthSystem()

# Inicializar estado de sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'mostrar_recuperacion' not in st.session_state:
    st.session_state.mostrar_recuperacion = False
if 'recuperacion_email' not in st.session_state:
    st.session_state.recuperacion_email = ""
if 'recuperacion_codigo' not in st.session_state:
    st.session_state.recuperacion_codigo = ""
if 'recuperacion_paso' not in st.session_state:
    st.session_state.recuperacion_paso = 1


def mostrar_recuperacion():
    """Pantalla de recuperación de contraseña"""
    st.markdown("""
    <div class="main-header">
        <h1>🔑 Recuperar Contraseña</h1>
        <p>Ingresa tu email para recibir un código de recuperación</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.session_state.recuperacion_paso == 1:
            # Paso 1: Solicitar código
            st.markdown("### Paso 1: Verificar tu cuenta")
            with st.form("solicitar_codigo_form"):
                email_recuperacion = st.text_input("Email registrado", placeholder="email@ejemplo.com")
                submit = st.form_submit_button("📧 Enviar código", use_container_width=True)
                
                if submit:
                    if email_recuperacion:
                        resultado = st.session_state.auth.solicitar_recuperacion(email_recuperacion)
                        if resultado["success"]:
                            st.session_state.recuperacion_email = email_recuperacion
                            # Solo guardar código si se muestra en pantalla (fallback)
                            st.session_state.recuperacion_codigo = resultado.get("codigo", "")
                            st.session_state.recuperacion_paso = 2
                            st.success(resultado["mensaje"])
                            # Solo mostrar el código si está en el resultado (fallback)
                            if "codigo" in resultado:
                                st.warning("⚠️ Usa este código (no se pudo enviar por email)")
                            else:
                                st.info("📧 Revisa tu bandeja de entrada (y spam) para ver el código")
                            st.rerun()
                        else:
                            st.error(resultado["mensaje"])
                    else:
                        st.warning("⚠️ Ingresa tu email")
        
        elif st.session_state.recuperacion_paso == 2:
            # Paso 2: Ingresar código y nueva contraseña
            st.markdown("### Paso 2: Nueva contraseña")
            st.info(f"📧 Código enviado a: **{st.session_state.recuperacion_email}**")
            
            with st.form("restablecer_password_form"):
                codigo_ingresado = st.text_input("Código de 6 dígitos", placeholder="123456", max_chars=6)
                nueva_password = st.text_input("Nueva contraseña", type="password", placeholder="••••••••")
                confirmar_password = st.text_input("Confirmar contraseña", type="password", placeholder="••••••••")
                submit = st.form_submit_button("✅ Restablecer contraseña", use_container_width=True)
                
                if submit:
                    if not codigo_ingresado or not nueva_password or not confirmar_password:
                        st.warning("⚠️ Completa todos los campos")
                    elif nueva_password != confirmar_password:
                        st.error("❌ Las contraseñas no coinciden")
                    elif len(nueva_password) < 6:
                        st.warning("⚠️ La contraseña debe tener al menos 6 caracteres")
                    else:
                        resultado = st.session_state.auth.restablecer_contrasena(
                            st.session_state.recuperacion_email,
                            codigo_ingresado,
                            nueva_password
                        )
                        if resultado["success"]:
                            st.session_state.password_cambiada = True
                        else:
                            st.error(resultado["mensaje"])
            
            # Mostrar éxito y botón fuera del formulario
            if st.session_state.get('password_cambiada', False):
                st.success("✅ Contraseña actualizada correctamente")
                st.info("👉 Ahora puedes iniciar sesión con tu nueva contraseña")
                if st.button("🚀 Ir a Iniciar Sesión", type="primary", use_container_width=True, key="btn_login_recovery"):
                    # Resetear estado
                    st.session_state.mostrar_recuperacion = False
                    st.session_state.recuperacion_paso = 1
                    st.session_state.recuperacion_email = ""
                    st.session_state.recuperacion_codigo = ""
                    st.session_state.password_cambiada = False
                    st.rerun()
                st.balloons()
        
        st.markdown("---")
        if st.button("⬅️ Volver al inicio de sesión", use_container_width=True):
            st.session_state.mostrar_recuperacion = False
            st.session_state.recuperacion_paso = 1
            st.session_state.recuperacion_email = ""
            st.session_state.recuperacion_codigo = ""
            st.rerun()


def mostrar_login():
    """Pantalla de login/registro"""
    try:
        ref_code_param = st.query_params.get("ref", "")
    except Exception:
        ref_code_param = ""

    st.markdown("""
    <div class="main-header">
        <h1>🧠 REDI7 IA</h1>
        <p>Sistema Profesional de Análisis de Trading Institucional</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab1, tab2 = st.tabs(["🔐 Iniciar Sesión", "📝 Registrarse"])

        with tab1:
            st.markdown("### Accede a tu cuenta")
            with st.form("login_form"):
                username = st.text_input("Usuario", placeholder="tu_usuario")
                password = st.text_input("Contraseña", type="password", placeholder="••••••••")
                submit = st.form_submit_button("🚀 Entrar", type="primary", use_container_width=True)

                if submit:
                    if username and password:
                        resultado = st.session_state.auth.login(username, password)

                        if resultado["success"]:
                            st.session_state.logged_in = True
                            st.session_state.user_data = resultado["user_data"]
                            st.success(resultado["mensaje"])
                            st.rerun()
                        else:
                            st.error(resultado["mensaje"])
                    else:
                        st.warning("⚠️ Completa todos los campos")
            
            # Enlace de recuperación de contraseña como texto
            st.markdown("<div style='text-align: center; margin-top: 10px;'>", unsafe_allow_html=True)
            if st.button("¿Olvidaste tu contraseña?", key="forgot_pass", help="Recuperar acceso a tu cuenta"):
                st.session_state.mostrar_recuperacion = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("### Crea tu cuenta gratuita")
            with st.form("register_form"):
                new_username = st.text_input("Usuario *", placeholder="usuario_nuevo")
                new_email = st.text_input("Email *", placeholder="email@ejemplo.com")
                new_nombre = st.text_input("Nombre Completo *", placeholder="Tu nombre completo")
                new_whatsapp = st.text_input("Teléfono + código de país (+51, +52, etc.) *", placeholder="+52 1234567890")
                
                ref_code_input = st.text_input(
                    "Código de referido (opcional)",
                    value=ref_code_param,
                    placeholder="Ej: ABC123"
                )
                new_password = st.text_input("Contraseña *", type="password", placeholder="••••••••")
                new_password2 = st.text_input("Confirmar Contraseña *", type="password", placeholder="••••••••")

                submit_reg = st.form_submit_button("✨ Crear Cuenta", width='stretch')

                if submit_reg:
                    if new_password != new_password2:
                        st.error("❌ Las contraseñas no coinciden")
                    elif not new_username or not new_email or not new_password or not new_nombre or not new_whatsapp:
                        st.warning("⚠️ Completa todos los campos obligatorios (*)")
                    else:
                        resultado = st.session_state.auth.registrar_usuario(
                            new_username, new_email, new_password, new_nombre, ref_code_input, new_whatsapp
                        )

                        if resultado["success"]:
                            st.session_state.registro_exitoso = True
                        else:
                            st.error(resultado["mensaje"])
            
            # Mostrar éxito y botón fuera del formulario
            if st.session_state.get('registro_exitoso', False):
                st.success("✅ Cuenta creada exitosamente")
                st.info("👉 Ahora puedes iniciar sesión")
                if st.button("🚀 Ir a Iniciar Sesión", type="primary", use_container_width=True, key="btn_login_registro"):
                    st.session_state.registro_exitoso = False
                    st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #888;'>
            <p>🔒 Tus datos están seguros con encriptación SHA-256</p>
            <p>🚀 Impulsa tu trading con análisis institucionales ilimitados y decisiones respaldadas por IA</p>
        </div>
        """, unsafe_allow_html=True)


def mostrar_panel_usuario():
    """Panel lateral con info del usuario"""
    with st.sidebar:
        try:
            with open("logo/redi7ia.png", "rb") as logo_file:
                logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
            st.markdown(
                f"<img class='logo-circle' src='data:image/png;base64,{logo_b64}' />",
                unsafe_allow_html=True
            )
        except:
            pass
        # Obtener estadísticas de uso
        usage_stats = st.session_state.auth.can_analyze(
            st.session_state.user_data['id'],
            st.session_state.user_data['plan']
        )
        
        # Determinar color según uso
        porcentaje_uso = (usage_stats['used'] / usage_stats['limit']) * 100
        if porcentaje_uso < 50:
            color_uso = "🟢"
        elif porcentaje_uso < 80:
            color_uso = "🟡"
        else:
            color_uso = "🔴"
        
        st.markdown(f"""
        <div class="user-info">
            <h3>👤 {st.session_state.user_data['username']}</h3>
            <p>📧 {st.session_state.user_data['email']}</p>
            <p>🎯 Plan: <b>{st.session_state.user_data['plan'].upper()}</b></p>
            <p>{color_uso} Análisis hoy: <b>{usage_stats['used']}/{usage_stats['limit']}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar advertencia si está cerca del límite
        if usage_stats['remaining'] <= 1 and usage_stats['remaining'] > 0:
            st.warning(f"⚠️ Te queda {usage_stats['remaining']} análisis hoy")
        elif usage_stats['remaining'] == 0:
            st.error("🔴 Límite alcanzado")
            if st.button("💎 Actualizar Plan", type="primary", width='stretch', key="upgrade_sidebar"):
                mostrar_modal_upgrade()

        # Enlace de referido oculto para usuarios normales
        # Solo visible en el panel de administrador
        
        try:
            conn = sqlite3.connect("redi7_users.db")
            cursor = conn.cursor()
            cursor.execute("SELECT is_admin FROM usuarios WHERE id = ?", (st.session_state.user_data['id'],))
            result = cursor.fetchone()
            conn.close()

            if result and result[0] == 1:
                st.markdown("---")
                if st.button("👑 Panel Administrador", width='stretch', type="primary", key="btn_admin_access"):
                    st.session_state['show_admin_panel'] = True
                    st.rerun()
        except Exception as e:
            pass  # Si no existe la columna is_admin, ignorar

# Componente de paste eliminado - causaba parpadeo


def mostrar_modal_upgrade():
    """Modal para actualización de plan cuando se alcanza el límite"""
    st.info("💎 Actualiza tu Plan REDI7 AI")
    st.markdown("""
### 🚀 ¡Has alcanzado el límite de análisis diarios!

Para seguir disfrutando de análisis ilimitados y más beneficios, actualiza tu plan:

#### 📊 Planes Disponibles:

**🆓 FREE** (Plan Actual)
- ✅ 3 análisis diarios
- ✅ Análisis básico

**⭐ PRO**
- ✅ 10 análisis diarios
- ✅ Análisis avanzado
- ✅ Soporte prioritario
- 💰 Precio: Consultar

**👑 ELITE**
- ✅ 25 análisis diarios
- ✅ Análisis institucional completo
- ✅ Soporte VIP 24/7
- ✅ Señales exclusivas
- 💰 Precio: Consultar

---

### 📞 Contáctanos para Actualizar

Chatea con nosotros en WhatsApp para más información y actualizar tu plan:
""", unsafe_allow_html=True)
    
    whatsapp_url = "https://wa.me/51960239007?text=Hola,%20quiero%20actualizar%20mi%20plan%20REDI7%20AI"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.link_button(
            "💬 Contactar por WhatsApp",
            whatsapp_url,
            type="primary",
            width='stretch'
        )
    
    st.markdown("---")
    st.caption("📱 +51 960 239 007 | Soporte REDI7 AI")


def detectar_dispositivo():
    """Detecta si el usuario está en PC o dispositivo móvil con toggle permanente"""
    # Inicializar con valor por defecto
    if 'dispositivo' not in st.session_state:
        st.session_state.dispositivo = "PC"

    # Toggle switch para cambiar entre PC y MÓVIL
    es_movil = st.toggle(
        "📱 Modo Móvil",
        value=(st.session_state.dispositivo == "MOVIL"),
        help="Activa para análisis desde móvil (3 capturas). Desactiva para PC (2 capturas)",
        key="toggle_dispositivo"
    )

    # Actualizar dispositivo basado en el toggle
    nuevo_dispositivo = "MOVIL" if es_movil else "PC"
    if nuevo_dispositivo != st.session_state.dispositivo:
        st.session_state.dispositivo = nuevo_dispositivo
        st.rerun()

    # Mostrar estado actual con iconos
    if st.session_state.dispositivo == "PC":
        st.success("💻 Modo PC (2 capturas)")
    else:
        st.info("📱 Modo Móvil (3 capturas)")
    
    return st.session_state.dispositivo


def main():
    """Función principal con sistema de usuarios"""
    
    # Verificar si está en modo recuperación
    if st.session_state.mostrar_recuperacion:
        mostrar_recuperacion()
        return
    
    # Verificar si está logueado
    if not st.session_state.logged_in:
        mostrar_login()
        return
    
    # Mostrar header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 REDI7 IA</h1>
        <p>Sistema Profesional de Análisis de Trading Institucional</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar panel de usuario
    mostrar_panel_usuario()

    # Verificar si debe mostrar panel admin
    if st.session_state.get("show_admin_panel", False):
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⬅️ Volver al Dashboard", width='stretch', key="btn_back_dashboard"):
                st.session_state['show_admin_panel'] = False
                st.rerun()
        st.markdown("---")
        try:
            show_admin_panel()
        except Exception as e:
            st.error(f"Error al cargar panel admin: {str(e)}")
            st.session_state['show_admin_panel'] = False
            if st.button("🔄 Reintentar"):
                st.rerun()
        return
    
    # Sidebar - Configuración (fuera de tabs)
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📱 Tipo de Dispositivo")
        dispositivo = detectar_dispositivo()

        # Guía de inicio movida aquí
        st.markdown("---")
        st.markdown("### 📘 Guía de Uso")
        
        with st.expander("📘 Ver Guía Completa", expanded=False):
            st.markdown("""
**7 PASOS PARA UN ANÁLISIS PROFESIONAL**

1. **Selecciona el activo correcto**: asegúrate de que el símbolo coincide con tu gráfico (XAUUSD, NAS100, US30, BTCUSD, EURUSD).
2. **Configura el gráfico con estándar institucional**:
    - Fondo limpio y sin cuadrículas (si es posible).
    - Velas **verdes/rojas** con buen contraste.
    - Solo precio + volumen (si aplica). Evita indicadores extra.
    - Mantén visible el **precio actual** y la **temporalidad**.
3. **Calidad de captura (PC/Móvil)**:
    - Sin cortes ni zoom excesivo.
    - Buena resolución y texto legible.
    - Una captura por temporalidad solicitada.
4. **Horarios de mayor efectividad (EST)**:
    - **XAUUSD / NAS100 / US30**: Londres–NY (08:00–11:30).
    - **EURUSD**: solape Londres–NY (08:00–10:30).
    - **BTCUSD**: picos 07:00–10:30 y 19:00–22:00.
5. **Noticias económicas**:
    - Evita operar **15–30 min antes** y **15–30 min después** de noticias de alto impacto.
    - Revisa **forexfactory.com** (calendario económico).
6. **Gestión de riesgo disciplinada**:
    - Respeta tu límite diario por plan.
    - Mantén riesgo fijo por operación.
7. **Coherencia multi‑temporalidad**:
    - Si el contexto y la entrada no alinean, **no operes**.
    - Espera confirmación antes de ejecutar.
""")

        # Configuración de Telegram al final
        st.markdown("---")
        st.markdown("### 📱 Configuración Telegram")
        
        with st.expander("⚙️ Configurar Bot", expanded=False):
            st.markdown("Configura tu bot personal para recibir señales")
            
            # Obtener configuración actual
            telegram_config = st.session_state.auth.obtener_telegram_config(
                st.session_state.user_data['id']
            )
            
            with st.form("telegram_config_form"):
                bot_token_input = st.text_input(
                    "🤖 Token del Bot",
                    value=telegram_config['bot_token'],
                    type="password",
                    help="Token proporcionado por @BotFather"
                )
                
                chat_id_input = st.text_input(
                    "💬 Chat ID",
                    value=telegram_config['chat_id'],
                    help="Tu ID personal o del grupo"
                )
                
                col_save, col_help = st.columns(2)
                
                with col_save:
                    guardar_telegram = st.form_submit_button(
                        "💾 Guardar",
                        width='stretch'
                    )
                
                with col_help:
                    if st.form_submit_button("❓ Ayuda", width='stretch'):
                        st.session_state['show_telegram_help'] = True
                
                if guardar_telegram:
                    if bot_token_input and chat_id_input:
                        resultado = st.session_state.auth.guardar_telegram_config(
                            st.session_state.user_data['id'],
                            bot_token_input,
                            chat_id_input
                        )
                        if resultado['success']:
                            st.success(resultado['mensaje'])
                            st.rerun()
                        else:
                            st.error(resultado['mensaje'])
                    else:
                        st.warning("⚠️ Completa ambos campos")
            
            # Mostrar estado
            if telegram_config['configurado']:
                st.success("✅ Telegram configurado")
                
                # SWITCH PARA ENVÍO AUTOMÁTICO
                st.markdown("---")
                enviar_auto = st.toggle(
                    "📤 Enviar alertas automáticamente",
                    value=st.session_state.get('telegram_auto_envio', False),
                    help="Cuando está activado, las señales se envían automáticamente a Telegram después del análisis"
                )
                st.session_state['telegram_auto_envio'] = enviar_auto
                
                if enviar_auto:
                    st.info("🟢 Envío automático ACTIVO")
                else:
                    st.warning("🔴 Envío automático DESACTIVADO")
            else:
                st.info("⚠️ Sin configurar")
        
        # Ayuda de Telegram inline
        if st.session_state.get('show_telegram_help', False):
            st.info("📖 Cómo configurar Telegram")
            st.markdown("""
**Pasos rápidos:**

1. **Crear Bot:**
   - Busca `@BotFather` en Telegram
   - Envía `/newbot`
   - Guarda el **token**

2. **Obtener Chat ID:**
   - Busca `@userinfobot`
   - Envía `/start`
   - Copia tu **ID**

3. **Guardar aquí** y ¡listo!

📄 [Guía completa](TELEGRAM_SETUP.md)
""")
            
            if st.button("Cerrar", key="close_telegram_help"):
                st.session_state['show_telegram_help'] = False
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Salir", width='stretch'):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.rerun()
    
    # Tabs principales: Análisis y Historial
    tab_analisis, tab_historial = st.tabs(["🔍 Nuevo Análisis", "📚 Mi Historial"])
    
    with tab_historial:
        st.markdown("### 📚 Historial de Análisis")
        
        historial = st.session_state.auth.obtener_historial(
            st.session_state.user_data['id'], 
            limit=20
        )
        
        if historial:
            for idx, (activo, modo, temporalidad, fecha, resultado) in enumerate(historial):
                with st.expander(f"📊 {activo} - {modo} - {fecha}", expanded=False):
                    st.markdown(f"**Temporalidad:** {temporalidad}")
                    st.markdown(f"**Fecha:** {fecha}")
                    st.markdown("**Análisis:**")
                    st.text(resultado)
        else:
            st.info("📭 No tienes análisis previos. Realiza tu primer análisis en la pestaña 'Nuevo Análisis'.")
    
    with tab_analisis:
        st.markdown("### ⚙️ Selección del Análisis")

        col_activo, col_modo, col_riesgo = st.columns([1, 1, 1])
        
        with col_activo:
            activo = st.selectbox(
                "📊 Selecciona el Activo",
                options=ACTIVOS_PERMITIDOS,
                help="Activo financiero a analizar",
                key="activo_select"
            )

        with col_modo:
            modo_operacion = st.radio(
                "⚡ Modo de Operación",
                options=["SCALPING", "INTRADAY"],
                help="Tipo de estrategia a aplicar",
                horizontal=True,
                key="modo_operacion"
            )
        
        with col_riesgo:
            gestionar_riesgo = st.checkbox(
                "💰 Gestión de Riesgo",
                value=True,
                help="Activa para incluir cálculos de capital y riesgo",
                key="gestionar_riesgo_check"
            )
            
            capital = None
            riesgo_porcentaje = None
            
            if gestionar_riesgo:
                # Capital y Riesgo en la misma fila
                col_cap, col_risk = st.columns(2)
                
                with col_cap:
                    capital = st.number_input(
                        "Capital ($)",
                        min_value=100.0,
                        max_value=1000000.0,
                        value=10000.0,
                        step=100.0,
                        help="Capital disponible",
                        label_visibility="visible"
                    )
                
                with col_risk:
                    riesgo_porcentaje = st.number_input(
                        "Riesgo (%)",
                        min_value=0.1,
                        max_value=20.0,
                        value=2.0,
                        step=0.1,
                        help="% de capital",
                        label_visibility="visible"
                    )

        activo_icons = {
            "XAUUSD": "🥇",
            "BTCUSD": "₿",
            "NAS100": "📈",
            "US30": "📊",
            "EURUSD": "💶"
        }
        st.markdown(f"### {activo_icons.get(activo, '📊')} {activo}")
        st.markdown("---")

        # Obtener configuración de temporalidades según activo, modo y dispositivo
        config = get_config_temporalidades(activo, modo_operacion, dispositivo)
        num_imagenes = config["num_imagenes"]
        tf_labels = config["labels"]
        temporalidades = config["temporalidades"]
        efectividad = config["efectividad"]

        # Main Area
        st.markdown("### 📸 Capturas de Gráficos MT5")

        if num_imagenes == 2:
            cols = st.columns(2)
        else:
            cols = st.columns(3)
        
        # Inicializar variables de imágenes
        imagenes_cargadas = []
        uploaded_files = []
        
        # Generar columnas dinámicamente según número de imágenes
        for i, (col, label, temp) in enumerate(zip(cols, tf_labels, temporalidades)):
            with col:
                label_text = label if f"({temp})" in label else f"{label} ({temp})"
                st.markdown(
                    f"**🕒 Temporalidad:** <span style='color:#4CAF50; font-weight:700;'>{label_text}</span>",
                    unsafe_allow_html=True
                )
                uploaded_file = st.file_uploader(
                    "Subir aquí los archivos",
                    type=['png', 'jpg', 'jpeg'],
                    key=f"upload_imagen_{i+1}",
                    help="Sube la captura si no usas el pegado directo",
                    label_visibility="visible"
                )
                if uploaded_file:
                    st.image(uploaded_file, caption=f"{label_text}", width='stretch')
                    uploaded_files.append(uploaded_file)
                    imagenes_cargadas.append(True)
                else:
                    imagenes_cargadas.append(False)
        
        # Indicador de imágenes cargadas
        num_cargadas = sum(imagenes_cargadas)
        st.markdown("---")
        
        if num_cargadas == num_imagenes:
            st.success(f"✅ {num_cargadas}/{num_imagenes} capturas cargadas correctamente")
        else:
            st.warning(f"⚠️ {num_cargadas}/{num_imagenes} capturas cargadas. Sube las {num_imagenes} capturas para analizar.")
    
        # Variables de contexto (valores por defecto ya que se removió la sección de UI)
        horario_actual = datetime.now().strftime("%H:%M EST")
        contexto_adicional = ""
        evento_macro = False
        descripcion_evento = ""
    
        # Botón de Análisis
        st.markdown("---")
    
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
        with col_btn2:
            analizar = st.button("🚀 GENERAR ANÁLISIS INSTITUCIONAL", width='stretch', key="btn_generar_analisis")
        
        # Procesamiento del análisis
        if analizar:
            # Validaciones simples
            if num_cargadas != num_imagenes:
                st.error(f"❌ Por favor sube las {num_imagenes} capturas de gráficos antes de analizar")
                return

            # Verificar límite de consultas ANTES de procesar
            plan = st.session_state.user_data.get("plan", "free")
            usage = st.session_state.auth.can_analyze(st.session_state.user_data['id'], plan)
            
            if not usage["allowed"]:
                st.error(
                    f"❌ Límite diario alcanzado ({usage['used']}/{usage['limit']} análisis). "
                    f"Plan actual: **{plan.upper()}**"
                )
                st.info("💡 Actualiza tu plan para obtener más análisis diarios")
                
                # Mostrar el modal de upgrade
                mostrar_modal_upgrade()
                return
        
            if gestionar_riesgo and (not capital or not riesgo_porcentaje):
                st.error("❌ Completa los datos de capital y riesgo")
                return
        
            # Mostrar spinner mientras procesa
            with st.spinner('🧠 REDI7 IA analizando el mercado con Inteligencia Artificial...'):
                try:
                    # Inicializar REDI7 AI - Obtener API key de variable de entorno
                    api_key = os.getenv("OPENAI_API_KEY")
                    
                    if not api_key:
                        st.error("❌ API Key de OpenAI no configurada. Configura la variable de entorno OPENAI_API_KEY")
                        return
                
                    redi7 = REDI7AI(api_key=api_key)
                
                    # Preparar imágenes en base64
                    imagenes_base64 = []
                
                    # Función helper para convertir imagen a base64
                    def imagen_to_base64(img):
                        # Es UploadedFile de Streamlit
                        return base64.b64encode(img.getvalue()).decode('utf-8')
                
                    # Convertir todas las imágenes (2 o 3 según dispositivo)
                    for uploaded_file in uploaded_files:
                        imagenes_base64.append(imagen_to_base64(uploaded_file))
                    
                    # Obtener los niveles de detalle para cada imagen
                    detail_levels = get_detail_levels(activo, modo_operacion, dispositivo)
                
                    # Parámetros del análisis
                    params = {
                        "activo": activo,
                        "modo": modo_operacion,
                        "horario_actual": horario_actual,
                        "imagenes_base64": imagenes_base64,
                        "detail_levels": detail_levels,
                        "dispositivo": dispositivo,
                        "temporalidades": temporalidades,
                        "evento_macro": evento_macro,
                        "descripcion_evento": descripcion_evento if evento_macro else "",
                        "contexto_adicional": contexto_adicional,
                        "gestionar_riesgo": gestionar_riesgo
                    }
                
                    # Si la gestión de riesgo está activa, agregar parámetros
                    if gestionar_riesgo:
                        params["capital"] = capital
                        params["riesgo_porcentaje"] = riesgo_porcentaje
                    else:
                        # Valores por defecto cuando no hay gestión de riesgo
                        params["capital"] = 10000.0
                        params["riesgo_porcentaje"] = 2.0
                
                    # Realizar análisis CON IMÁGENES
                    resultado = redi7.analizar_con_imagenes(**params)

                    # Mostrar resultados
                    if resultado["error"]:
                        st.error(f"❌ {resultado['mensaje']}")
                    else:
                        # Guardar en historial
                        try:
                            conn = sqlite3.connect("redi7_users.db")
                            cursor = conn.cursor()
                            cursor.execute("""
                                INSERT INTO historial_analisis (user_id, activo, modo, temporalidad, resultado)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                st.session_state.user_data['id'],
                                activo,
                                modo_operacion,
                                ', '.join(temporalidades) if isinstance(temporalidades, list) else str(temporalidades),
                                resultado['analisis'][:1000]  # Guardar primeros 1000 caracteres
                            ))
                            conn.commit()
                            conn.close()
                        except Exception as e:
                            print(f"Error guardando análisis: {e}")
                        
                        # GUARDAR TODO EN SESSION STATE PARA QUE NO DESAPAREZCA
                        st.session_state['resultado_actual'] = {
                            'activo': resultado['activo'],
                            'modo': resultado['modo'],
                            'horario': resultado['horario'],
                            'tokens': resultado['tokens_usados'],
                            'analisis_completo': resultado['analisis'],
                            'timestamp': resultado['timestamp'],
                            'gestionar_riesgo': gestionar_riesgo
                        }
                        
                        # ENVÍO AUTOMÁTICO A TELEGRAM SI ESTÁ ACTIVADO
                        if st.session_state.get('telegram_auto_envio', False):
                            telegram_config = st.session_state.auth.obtener_telegram_config(
                                st.session_state.user_data['id']
                            )
                            
                            if telegram_config['configurado']:
                                try:
                                    from telegram_sender import TelegramSender
                                    
                                    # Extraer análisis principal
                                    analisis_text = resultado['analisis']
                                    if "📉GESTIÓN DE RIESGO REDI7📉" in analisis_text:
                                        analisis_principal = analisis_text.split("📉GESTIÓN DE RIESGO REDI7📉")[0].strip()
                                    else:
                                        analisis_principal = analisis_text
                                    
                                    # Crear sender y enviar
                                    sender = TelegramSender(
                                        bot_token=telegram_config['bot_token'],
                                        chat_id=telegram_config['chat_id']
                                    )
                                    
                                    mensaje = f"🚀 SEÑAL REDI7 AI\n\n📊 Activo: {resultado['activo']}\n⚡ Modo: {resultado['modo']}\n\n{analisis_principal}"
                                    resultado_tg = sender.enviar_mensaje(mensaje, parse_mode=None)
                                    
                                    if resultado_tg["exito"]:
                                        st.success("📱 ✅ Señal enviada automáticamente a Telegram")
                                        st.balloons()
                                    else:
                                        st.warning(f"⚠️ No se pudo enviar a Telegram: {resultado_tg.get('mensaje', 'Error')}")
                                
                                except Exception as e:
                                    st.warning(f"⚠️ Error al enviar a Telegram: {str(e)}")
                        
                        # Header del resultado
                        st.success("✅ **Análisis completado exitosamente**")

                        # Métricas superiores
                        # Verificar si es admin para mostrar tokens
                        try:
                            conn = sqlite3.connect("redi7_users.db")
                            cursor = conn.cursor()
                            cursor.execute("SELECT is_admin FROM usuarios WHERE id = ?", (st.session_state.user_data['id'],))
                            result = cursor.fetchone()
                            conn.close()
                            es_admin = result and result[0] == 1
                        except:
                            es_admin = False
                        
                        if es_admin:
                            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        else:
                            col_m1, col_m2, col_m3 = st.columns(3)

                        with col_m1:
                            st.metric("📊 Activo", resultado['activo'])

                        with col_m2:
                            st.metric("⚡ Modo", resultado['modo'])

                        with col_m3:
                            st.metric("⏰ Hora", resultado['horario'])

                        if es_admin:
                            with col_m4:
                                st.metric("🔢 Tokens", f"{resultado['tokens_usados']}")

                        # Resultado del análisis
                        st.markdown("---")
                        st.markdown("### 📋 Análisis Institucional REDI7 AI")

                        analisis_text = resultado['analisis']
                        
                        # Separar análisis de gestión de riesgo si existe
                        if "📉GESTIÓN DE RIESGO REDI7📉" in analisis_text:
                            partes = analisis_text.split("📉GESTIÓN DE RIESGO REDI7📉")
                            analisis_principal = partes[0].strip()
                            gestion_riesgo_texto = partes[1].strip() if len(partes) > 1 else ""
                        else:
                            analisis_principal = analisis_text
                            gestion_riesgo_texto = ""

                        # Mostrar el análisis principal en un contenedor con estilo
                        st.markdown('<div class="resultado-box">', unsafe_allow_html=True)
                        analisis_formatted = analisis_principal.replace('\n', '  \n')
                        st.markdown(analisis_formatted)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Si hay gestión de riesgo, mostrarla en formato profesional
                        if gestion_riesgo_texto and gestionar_riesgo:
                            st.markdown("---")
                            st.markdown("### 💰 Gestión de Riesgo")
                            
                            # Extraer valores con regex
                            import re
                            capital_match = re.search(r'Capital: \$([0-9,]+\.\d{2})', gestion_riesgo_texto)
                            riesgo_pct_match = re.search(r'Riesgo: ([\d.]+)%', gestion_riesgo_texto)
                            dinero_riesgo_match = re.search(r'Dinero en riesgo: \$([0-9,]+\.\d{2})', gestion_riesgo_texto)
                            lotaje_match = re.search(r'Tamaño posición: ([\d.]+) lotes', gestion_riesgo_texto)
                            tp1_match = re.search(r'TP1: \$([0-9,]+\.\d{2}) \(R:R ([\d.]+)\)', gestion_riesgo_texto)
                            tp2_match = re.search(r'TP2: \$([0-9,]+\.\d{2}) \(R:R ([\d.]+)\)', gestion_riesgo_texto)
                            tp3_match = re.search(r'TP3: \$([0-9,]+\.\d{2}) \(R:R ([\d.]+)\)', gestion_riesgo_texto)
                            rr_prom_match = re.search(r'Ratio Riesgo/Beneficio promedio: ([\d.]+)', gestion_riesgo_texto)
                            
                            # Primera fila: Capital y Riesgo
                            col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                            
                            with col_r1:
                                if capital_match:
                                    st.metric("💰 Capital Total", f"${capital_match.group(1)}")
                            
                            with col_r2:
                                if riesgo_pct_match:
                                    st.metric("⚠️ Riesgo", f"{riesgo_pct_match.group(1)}%")
                            
                            with col_r3:
                                if dinero_riesgo_match:
                                    st.metric("💵 En Riesgo", f"${dinero_riesgo_match.group(1)}")
                            
                            with col_r4:
                                if lotaje_match:
                                    st.metric("📊 Lotaje", f"{lotaje_match.group(1)} lotes")
                            
                            # Segunda fila: TPs y Ratios
                            st.markdown("**💎 Ganancias Potenciales:**")
                            col_tp1, col_tp2, col_tp3, col_rr = st.columns(4)
                            
                            with col_tp1:
                                if tp1_match:
                                    st.metric("🎯 TP1", f"${tp1_match.group(1)}", delta=f"R:R {tp1_match.group(2)}")
                            
                            with col_tp2:
                                if tp2_match:
                                    st.metric("🎯 TP2", f"${tp2_match.group(1)}", delta=f"R:R {tp2_match.group(2)}")
                            
                            with col_tp3:
                                if tp3_match:
                                    st.metric("🎯 TP3", f"${tp3_match.group(1)}", delta=f"R:R {tp3_match.group(2)}")
                            
                            with col_rr:
                                if rr_prom_match:
                                    st.metric("📈 R:R Promedio", rr_prom_match.group(1))

                        # Guardar análisis en session_state para Telegram
                        st.session_state['ultimo_analisis'] = {
                            'activo': activo,
                            'modo': modo_operacion,
                            'analisis_principal': analisis_principal,
                            'timestamp': resultado['timestamp']
                        }

                        # Timestamp
                        st.caption(f"🕐 Generado: {resultado['timestamp']}")

                        # Botones de acción
                        st.markdown("---")
                        col_btn_nuevo, col_btn_tg = st.columns(2)
                        
                        with col_btn_nuevo:
                            # Botón para analizar de nuevo
                            if st.button("🔄 Analizar de Nuevo", width='stretch', key="btn_nuevo_analisis", use_container_width=True):
                                st.rerun()
                        
                        with col_btn_tg:
                            # Botón para enviar a Telegram con callback
                            if st.button("📱 Enviar a Telegram", type="primary", width='stretch', key="btn_telegram", use_container_width=True):
                                # Obtener datos del último análisis
                                if 'ultimo_analisis' in st.session_state:
                                    datos = st.session_state['ultimo_analisis']
                                    
                                    # Obtener configuración de Telegram
                                    telegram_config = st.session_state.auth.obtener_telegram_config(
                                        st.session_state.user_data['id']
                                    )
                                    
                                    if not telegram_config['configurado']:
                                        st.error("⚠️ Configura tu bot de Telegram en el menú lateral primero")
                                    else:
                                        try:
                                            from telegram_sender import TelegramSender
                                            
                                            # Crear sender
                                            telegram_sender = TelegramSender(
                                                bot_token=telegram_config['bot_token'],
                                                chat_id=telegram_config['chat_id']
                                            )
                                            
                                            # Preparar mensaje desde session_state
                                            mensaje = f"🚀 SEÑAL REDI7 AI\n\n📊 Activo: {datos['activo']}\n⚡ Modo: {datos['modo']}\n\n{datos['analisis_principal']}"
                                            
                                            # Enviar
                                            resultado_tg = telegram_sender.enviar_mensaje(mensaje, parse_mode=None)
                                            
                                            if resultado_tg["exito"]:
                                                st.success("✅ Señal enviada a Telegram exitosamente")
                                                st.balloons()
                                            else:
                                                st.error(f"❌ Error: {resultado_tg.get('mensaje', 'Error desconocido')}")
                                        
                                        except Exception as e:
                                            st.error(f"❌ Error al enviar: {str(e)}")
                                else:
                                    st.error("❌ No hay análisis para enviar")
                    
                except Exception as e:
                    st.error(f"❌ Error durante el análisis: {str(e)}")
                    st.exception(e)
        
        # MOSTRAR RESULTADO SIEMPRE SI EXISTE EN SESSION STATE (FUERA del bloque if analizar)
        # Esto mantiene el análisis visible incluso después de presionar otros botones
        if 'resultado_actual' in st.session_state:
            res = st.session_state['resultado_actual']
            
            # Header del resultado
            st.success("✅ **Análisis completado exitosamente**")

            # Verificar si es admin para mostrar tokens
            try:
                conn = sqlite3.connect("redi7_users.db")
                cursor = conn.cursor()
                cursor.execute("SELECT is_admin FROM usuarios WHERE id = ?", (st.session_state.user_data['id'],))
                result = cursor.fetchone()
                conn.close()
                es_admin = result and result[0] == 1
            except:
                es_admin = False
            
            # Métricas superiores
            if es_admin:
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            else:
                col_m1, col_m2, col_m3 = st.columns(3)
            
            with col_m1:
                st.metric("📊 Activo", res['activo'])
            with col_m2:
                st.metric("⚡ Modo", res['modo'])
            with col_m3:
                st.metric("⏰ Hora", res['horario'])
            if es_admin:
                with col_m4:
                    st.metric("🔢 Tokens", f"{res['tokens']}")

            # Resultado del análisis
            st.markdown("---")
            st.markdown("### 📋 Análisis Institucional REDI7 AI")

            analisis_text = res['analisis_completo']
            
            # Separar análisis de gestión de riesgo si existe
            if "📉GESTIÓN DE RIESGO REDI7📉" in analisis_text:
                partes = analisis_text.split("📉GESTIÓN DE RIESGO REDI7📉")
                analisis_principal = partes[0].strip()
            else:
                analisis_principal = analisis_text

            # Mostrar el análisis principal
            st.markdown('<div class="resultado-box">', unsafe_allow_html=True)
            analisis_formatted = analisis_principal.replace('\n', '  \n')
            st.markdown(analisis_formatted)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Timestamp
            st.caption(f"🕐 Generado: {res['timestamp']}")

            # Botón de acción - Solo "Analizar de Nuevo"
            st.markdown("---")
            if st.button("🔄 Analizar de Nuevo", width='stretch', key="btn_nuevo_analisis_final", use_container_width=True):
                del st.session_state['resultado_actual']
                st.rerun()
    
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>🧠 <strong>REDI7 IA</strong> - Sistema Profesional de Análisis Institucional</p>
            <p>⚠️ Disclaimer: Esta herramienta es educacional. El trading conlleva riesgo de pérdida.</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
