"""
Configuración de REDI7 AI v1.0
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

# ━━━━━━━━━━━━━━━━━━━━━━
# 🔑 API CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━

# OpenAI API Key (recomendado usar variable de entorno)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Modelo a utilizar
# Opciones: "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"
MODELO = "gpt-4"

# ━━━━━━━━━━━━━━━━━━━━━━
# � TELEGRAM CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━

# Token del bot de Telegram (obtener de @BotFather)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ID del chat o grupo donde enviar señales
# Para obtenerlo: envía /start a @userinfobot en Telegram
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Activar envío automático a Telegram (True/False)
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# ━━━━━━━━━━━━━━━━━━━━━━
# �📊 TRADING CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━

# Activos permitidos
ACTIVOS_PERMITIDOS = [
    "XAUUSD",   # Oro
    "BTCUSD",   # Bitcoin
    "NAS100",   # Nasdaq 100
    "US30",     # Dow Jones 30
    "EURUSD"    # Euro Dólar
]

# Modos de operativa
MODOS = {
    "SCALPING": {
        "descripcion": "Corto plazo, alta precisión",
        "tf_contexto": ["D1", "H4"],
        "tf_estructura": ["H1", "M30"],
        "tf_entrada": ["M15", "M5", "M1"]
    },
    "INTRADAY": {
        "descripcion": "Movimientos estructurales de sesión",
        "tf_contexto": ["W1", "D1"],
        "tf_estructura": ["H4", "H1"],
        "tf_entrada": ["M30", "M15"]
    }
}

# ━━━━━━━━━━━━━━━━━━━━━━
# ⚠️ RISK MANAGEMENT
# ━━━━━━━━━━━━━━━━━━━━━━

# Riesgo mínimo y máximo por operación
RIESGO_MIN = 1.0  # 1%
RIESGO_MAX = 5.0  # 5%

# Capital por defecto para pruebas
CAPITAL_DEFAULT = 10000.0

# ━━━━━━━━━━━━━━━━━━━━━━
# 🕐 HORARIOS INSTITUCIONALES
# ━━━━━━━━━━━━━━━━━━━━━━

SESIONES = {
    "TOKYO": {"inicio": "00:00", "fin": "09:00", "timezone": "UTC"},
    "LONDON": {"inicio": "08:00", "fin": "16:00", "timezone": "UTC"},
    "NY": {"inicio": "13:00", "fin": "22:00", "timezone": "UTC"}
}

# ━━━━━━━━━━━━━━━━━━━━━━
# 🎨 UI CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━

# Colores para contexto
COLORES_CONTEXTO = {
    "optimo": "🟢",
    "precaucion": "🟡",
    "alto_riesgo": "🔴"
}

# ━━━━━━━━━━━━━━━━━━━━━━
# 📁 PATHS
# ━━━━━━━━━━━━━━━━━━━━━━

# Directorio para guardar análisis
DIR_ANALISIS = "analisis_guardados"

# Directorio para capturas MT5
DIR_CAPTURAS = "capturas_mt5"

# ━━━━━━━━━━━━━━━━━━━━━━
# 🔧 ADVANCED SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━

# Temperatura de la API (0.0 - 1.0)
# Menor = Más determinista, Mayor = Más creativo
TEMPERATURE = 0.7

# Máximo de tokens en la respuesta
MAX_TOKENS = 2000

# Timeout para llamadas API (segundos)
API_TIMEOUT = 30

# ━━━━━━━━━━━━━━━━━━━━━━
# 📝 LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━

# Nivel de logging
# Opciones: "DEBUG", "INFO", "WARNING", "ERROR"
LOG_LEVEL = "INFO"

# Archivo de log
LOG_FILE = "redi7_ai.log"


def validar_configuracion() -> Dict[str, Any]:
    """
    Valida que la configuración sea correcta
    
    Returns:
        Diccionario con el resultado de la validación
    """
    errores = []
    
    # Validar API Key
    if not OPENAI_API_KEY or OPENAI_API_KEY == "":
        errores.append("⚠️  OPENAI_API_KEY no configurada")
    
    # Validar modelo
    modelos_validos = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"]
    if MODELO not in modelos_validos:
        errores.append(f"⚠️  Modelo '{MODELO}' no válido. Usa: {', '.join(modelos_validos)}")
    
    # Validar riesgo
    if not (0 < RIESGO_MIN < RIESGO_MAX <= 10):
        errores.append(f"⚠️  Rangos de riesgo incorrectos: {RIESGO_MIN}% - {RIESGO_MAX}%")
    
    if errores:
        return {
            "valido": False,
            "errores": errores
        }
    
    return {
        "valido": True,
        "mensaje": "✅ Configuración válida"
    }


if __name__ == "__main__":
    # Test de configuración
    print("🔧 REDI7 IA - Validación de Configuración")
    print("=" * 60)
    
    resultado = validar_configuracion()
    
    if resultado["valido"]:
        print(resultado["mensaje"])
        print("\n📊 Activos permitidos:", ", ".join(ACTIVOS_PERMITIDOS))
        print(f"🤖 Modelo configurado: {MODELO}")
        print(f"💰 Capital por defecto: ${CAPITAL_DEFAULT:,.2f}")
        print(f"⚠️  Riesgo permitido: {RIESGO_MIN}% - {RIESGO_MAX}%")
    else:
        print("❌ Errores en la configuración:\n")
        for error in resultado["errores"]:
            print(f"   {error}")
        print("\n💡 Corrígelos en config.py antes de continuar")
