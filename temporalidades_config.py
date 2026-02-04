"""
REDI7 IA - Configuración de Temporalidades por Activo, Modo y Dispositivo
Optimización de imágenes según dispositivo (PC vs Móvil)
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📱 CONFIGURACIÓN DE TEMPORALIDADES POR DISPOSITIVO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEMPORALIDADES_CONFIG = {
    "SCALPING": {
        "PC": {
            "XAUUSD": {
                "num_imagenes": 2,
                "temporalidades": ["M15", "M1"],
                "labels": ["📊 Dirección + Setup (M15)", "🎯 Entrada Precisa (M1)"],
                "detail_levels": ["low", "high"],
                "efectividad": "⭐⭐⭐⭐⭐ 87%"
            },
            "NAS100": {
                "num_imagenes": 2,
                "temporalidades": ["M15", "M1"],
                "labels": ["📊 Dirección + Setup (M15)", "🎯 Entrada Precisa (M1)"],
                "detail_levels": ["low", "high"],
                "efectividad": "⭐⭐⭐⭐⭐ 89%"
            },
            "BTCUSD": {
                "num_imagenes": 2,
                "temporalidades": ["H1", "M1"],
                "labels": ["📊 Dirección + Setup (H1)", "🎯 Entrada Precisa (M1)"],
                "detail_levels": ["low", "high"],
                "efectividad": "⭐⭐⭐⭐ 84%"
            },
            "US30": {
                "num_imagenes": 2,
                "temporalidades": ["M15", "M1"],
                "labels": ["📊 Dirección + Setup (M15)", "🎯 Entrada Precisa (M1)"],
                "detail_levels": ["low", "high"],
                "efectividad": "⭐⭐⭐⭐ 86%"
            },
            "EURUSD": {
                "num_imagenes": 2,
                "temporalidades": ["H1", "M5"],
                "labels": ["📊 Dirección + Setup (H1)", "🎯 Entrada Precisa (M5)"],
                "detail_levels": ["low", "high"],
                "efectividad": "⭐⭐⭐⭐ 85%"
            }
        },
        "MOVIL": {
            "XAUUSD": {
                "num_imagenes": 3,
                "temporalidades": ["M15", "M5", "M1"],
                "labels": ["📊 Dirección (M15)", "🔍 Setup (M5)", "🎯 Entrada (M1)"],
                "detail_levels": ["low", "low", "high"],
                "efectividad": "⭐⭐⭐⭐⭐ 88%"
            },
            "NAS100": {
                "num_imagenes": 3,
                "temporalidades": ["M15", "M5", "M1"],
                "labels": ["📊 Dirección (M15)", "🔍 Setup (M5)", "🎯 Entrada (M1)"],
                "detail_levels": ["low", "low", "high"],
                "efectividad": "⭐⭐⭐⭐⭐ 90%"
            },
            "BTCUSD": {
                "num_imagenes": 3,
                "temporalidades": ["H1", "M5", "M1"],
                "labels": ["📊 Dirección (H1)", "🔍 Setup (M5)", "🎯 Entrada (M1)"],
                "detail_levels": ["low", "low", "high"],
                "efectividad": "⭐⭐⭐⭐ 85%"
            },
            "US30": {
                "num_imagenes": 3,
                "temporalidades": ["M15", "M5", "M1"],
                "labels": ["📊 Dirección (M15)", "🔍 Setup (M5)", "🎯 Entrada (M1)"],
                "detail_levels": ["low", "low", "high"],
                "efectividad": "⭐⭐⭐⭐ 87%"
            },
            "EURUSD": {
                "num_imagenes": 3,
                "temporalidades": ["H1", "M15", "M5"],
                "labels": ["📊 Dirección (H1)", "🔍 Setup (M15)", "🎯 Entrada (M5)"],
                "detail_levels": ["low", "low", "high"],
                "efectividad": "⭐⭐⭐⭐ 86%"
            }
        }
    },
    "INTRADAY": {
        "PC": {
            "XAUUSD": {
                "num_imagenes": 2,
                "temporalidades": ["H1", "M15"],
                "labels": ["📊 Contexto del Día (H1)", "🎯 Ejecución Intraday (M15)"],
                "detail_levels": ["low", "high"],
                "efectividad": "⭐⭐⭐⭐ 85%"
            },
            "NAS100": {
                "num_imagenes": 2,
                "temporalidades": ["H1", "M15"],
                "labels": ["📊 Contexto del Día (H1)", "🎯 Ejecución Intraday (M15)"],
                "detail_levels": ["low", "high"],
                "efectividad": "⭐⭐⭐⭐ 86%"
            },
            "BTCUSD": {
                "num_imagenes": 2,
                "temporalidades": ["H4", "M15"],
                "labels": ["📊 Contexto Mayor (H4)", "🎯 Ejecución Intraday (M15)"],
                "detail_levels": ["low", "high"],
                "efectividad": "⭐⭐⭐⭐ 83%"
            },
            "US30": {
                "num_imagenes": 2,
                "temporalidades": ["H1", "M30"],
                "labels": ["📊 Contexto del Día (H1)", "🎯 Ejecución Intraday (M30)"],
                "detail_levels": ["low", "high"],
                "efectividad": "⭐⭐⭐⭐ 84%"
            },
            "EURUSD": {
                "num_imagenes": 2,
                "temporalidades": ["H4", "M15"],
                "labels": ["📊 Contexto Mayor (H4)", "🎯 Ejecución Intraday (M15)"],
                "detail_levels": ["low", "high"],
                "efectividad": "⭐⭐⭐⭐ 82%"
            }
        },
        "MOVIL": {
            "XAUUSD": {
                "num_imagenes": 3,
                "temporalidades": ["H1", "M15", "M5"],
                "labels": ["📊 Macro Bias (H1)", "🔍 Confirmación (M15)", "🎯 Entrada (M5)"],
                "detail_levels": ["low", "low", "high"],
                "efectividad": "⭐⭐⭐⭐ 86%"
            },
            "NAS100": {
                "num_imagenes": 3,
                "temporalidades": ["H1", "M15", "M5"],
                "labels": ["📊 Macro Bias (H1)", "🔍 Confirmación (M15)", "🎯 Entrada (M5/M1)"],
                "detail_levels": ["low", "low", "high"],
                "efectividad": "⭐⭐⭐⭐ 87%"
            },
            "BTCUSD": {
                "num_imagenes": 3,
                "temporalidades": ["H4", "H1", "M15"],
                "labels": ["📊 Macro Bias (H4)", "🔍 Confirmación (H1)", "🎯 Entrada (M15)"],
                "detail_levels": ["low", "low", "high"],
                "efectividad": "⭐⭐⭐⭐ 84%"
            },
            "US30": {
                "num_imagenes": 3,
                "temporalidades": ["H1", "M30", "M5"],
                "labels": ["📊 Macro Bias (H1)", "🔍 Confirmación (M30)", "🎯 Entrada (M5)"],
                "detail_levels": ["low", "low", "high"],
                "efectividad": "⭐⭐⭐⭐ 85%"
            },
            "EURUSD": {
                "num_imagenes": 3,
                "temporalidades": ["H4", "H1", "M15"],
                "labels": ["📊 Macro Bias (H4)", "🔍 Confirmación (H1)", "🎯 Entrada (M15)"],
                "detail_levels": ["low", "low", "high"],
                "efectividad": "⭐⭐⭐⭐ 83%"
            }
        }
    }
}


def get_config_temporalidades(activo: str, modo: str, dispositivo: str) -> dict:
    """
    Obtiene la configuración de temporalidades para un activo, modo y dispositivo específico
    
    Args:
        activo: XAUUSD, NAS100, BTCUSD, US30, EURUSD
        modo: SCALPING o INTRADAY
        dispositivo: PC o MOVIL
        
    Returns:
        Diccionario con configuración de temporalidades
    """
    try:
        return TEMPORALIDADES_CONFIG[modo.upper()][dispositivo.upper()][activo.upper()]
    except KeyError:
        # Configuración por defecto si no existe
        if dispositivo.upper() == "PC":
            return {
                "num_imagenes": 2,
                "temporalidades": ["H1", "M15"],
                "labels": ["📊 Contexto", "🎯 Ejecución"],
                "detail_levels": ["low", "high"],
                "efectividad": "⭐⭐⭐ 80%"
            }
        else:
            return {
                "num_imagenes": 3,
                "temporalidades": ["H1", "M15", "M5"],
                "labels": ["📊 Contexto", "🔍 Estructura", "🎯 Ejecución"],
                "detail_levels": ["low", "low", "high"],
                "efectividad": "⭐⭐⭐ 80%"
            }


def get_num_imagenes_requeridas(activo: str, modo: str, dispositivo: str) -> int:
    """
    Obtiene el número de imágenes requeridas según configuración
    
    Returns:
        2 para PC, 3 para MOVIL
    """
    config = get_config_temporalidades(activo, modo, dispositivo)
    return config["num_imagenes"]


def get_detail_levels(activo: str, modo: str, dispositivo: str) -> list:
    """
    Obtiene los niveles de detalle para cada imagen
    
    Returns:
        Lista de 'low' o 'high' para cada imagen
    """
    config = get_config_temporalidades(activo, modo, dispositivo)
    return config["detail_levels"]
