"""
REDI7 IA v1.0 - Sistema Profesional de Análisis de Trading Institucional
Autor: Geiser
Fecha: Febrero 2026
"""

import openai
import os
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()


class REDI7AI:
    """Sistema de análisis de trading institucional basado en Smart Money Concept"""
    
    # Configuración del sistema
    ACTIVOS_PERMITIDOS = ["XAUUSD", "BTCUSD", "NAS100", "US30", "EURUSD"]
    MODOS_OPERATIVA = ["SCALPING", "INTRADAY"]
    
    # Valor del punto por lote estándar (1.0) para cada activo
    VALOR_PUNTO = {
        "XAUUSD": 100.0,     # Oro: distancia × 10, luego × $10 = $100 por punto por lote
        "BTCUSD": 10.0,      # $10 por punto por lote en Bitcoin
        "NAS100": 10.0,      # $10 por punto por lote en Nasdaq (verificado en MT5)
        "US30": 10.0,        # $10 por punto por lote en Dow Jones
        "EURUSD": 10.0       # $10 por pip por lote en EUR/USD
    }
    
    # Rangos de precios lógicos para 2024-2026 (validación de coherencia)
    RANGOS_PRECIO_VALIDOS = {
        "XAUUSD": {"min": 1800, "max": 3000, "descripcion": "Oro entre $1800-$3000"},
        "BTCUSD": {"min": 15000, "max": 150000, "descripcion": "Bitcoin entre $15k-$150k"},
        "NAS100": {"min": 12000, "max": 25000, "descripcion": "Nasdaq entre 12k-25k"},
        "US30": {"min": 28000, "max": 50000, "descripcion": "Dow Jones entre 28k-50k"},
        "EURUSD": {"min": 0.95, "max": 1.25, "descripcion": "EUR/USD entre 0.95-1.25"}
    }
    
    PROMPT_MAESTRO = """Eres REDI7 IA, analista profesional de mercados institucionales especializado en Smart Money Concept.

TU MISIÓN:
Analizar gráficos de trading con precisión profesional, identificando movimientos institucionales y proporcionando niveles exactos basados ÚNICAMENTE en lo visible en las imágenes.

METODOLOGÍA DE ANÁLISIS:
1. Identificar precio actual y rango temporal visible
2. Analizar estructura de mercado (Higher Highs, Higher Lows, Lower Highs, Lower Lows)
3. Detectar Break of Structure (BOS) y Change of Character (CHoCH)
4. Localizar zonas de liquidez institucional
5. Identificar Order Blocks de alta probabilidad
6. Ubicar Fair Value Gaps (imbalances)
7. Determinar confluencias para niveles óptimos de entrada/salida

LECTURA DE PRECIOS:
- Lee los precios EXACTOS del eje derecho del gráfico
- Observa las fechas y horas en el eje inferior
- Si un nivel no es claro, indícalo como aproximado
- Todos los niveles deben ser coherentes con el precio actual visible

FORMATO DE RESPUESTA (CADA LÍNEA SEPARADA):

🚨REDI7 IA🚨
🚨Señal: [BUY/SELL] en [ACTIVO]🚨
💰Entrada: [Precio]
🚫SL: [Precio]
🎯TP1: [Precio]
🎯TP2: [Precio]
🎯TP3: [Precio]
✅Probabilidad: [50-95]%
📊Contexto: [Resumen de UNA línea destacando lo MÁS importante del análisis]

CRÍTICO: Respeta EXACTAMENTE este formato con cada emoji y dato en su propia línea.

IMPORTANTE:
- NO calcules gestión de riesgo, lotaje ni ganancias en USD
- Solo proporciona niveles de precio basados en análisis técnico
- Enfócate en la calidad del análisis institucional
"""

    def __init__(self, api_key: str):
        """
        Inicializa el sistema REDI7 IA
        
        Args:
            api_key: Clave API de OpenAI
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.modelo = "gpt-4o"  # Modelo con capacidad de visión
        
    def validar_activo(self, activo: str) -> bool:
        """Valida si el activo está en la lista permitida"""
        return activo.upper() in self.ACTIVOS_PERMITIDOS
    
    def validar_modo(self, modo: str) -> bool:
        """Valida si el modo de operativa es correcto"""
        return modo.upper() in self.MODOS_OPERATIVA
    
    def calcular_gestion_riesgo(
        self,
        activo: str,
        entrada: float,
        stop_loss: float,
        tp1: float,
        tp2: float,
        tp3: float,
        capital: float,
        riesgo_porcentaje: float,
        direccion: str = "BUY"
    ) -> Dict[str, any]:
        """
        Calcula la gestión de riesgo con valores precisos
        
        Args:
            activo: Símbolo del activo
            entrada: Precio de entrada
            stop_loss: Precio del stop loss
            tp1, tp2, tp3: Precios de los take profits
            capital: Capital total
            riesgo_porcentaje: Porcentaje de riesgo (1-5%)
            direccion: BUY o SELL
            
        Returns:
            Diccionario con cálculos de riesgo
        """
        activo_upper = activo.upper()
        valor_punto = self.VALOR_PUNTO.get(activo_upper, 10.0)
        
        # Calcular distancia al SL en puntos
        if direccion.upper() == "BUY":
            distancia_sl = abs(entrada - stop_loss)
            ganancia_tp1 = abs(tp1 - entrada)
            ganancia_tp2 = abs(tp2 - entrada)
            ganancia_tp3 = abs(tp3 - entrada)
        else:  # SELL
            distancia_sl = abs(stop_loss - entrada)
            ganancia_tp1 = abs(entrada - tp1)
            ganancia_tp2 = abs(entrada - tp2)
            ganancia_tp3 = abs(entrada - tp3)
        
        # Calcular riesgo en USD
        riesgo_usd = capital * (riesgo_porcentaje / 100)
        
        # Calcular lotaje: Riesgo_USD / (Distancia_SL × Valor_Punto)
        lotaje = riesgo_usd / (distancia_sl * valor_punto)
        lotaje = round(lotaje, 2)  # Redondear a 2 decimales
        
        # Calcular ganancias potenciales
        ganancia_usd_tp1 = ganancia_tp1 * valor_punto * lotaje
        ganancia_usd_tp2 = ganancia_tp2 * valor_punto * lotaje
        ganancia_usd_tp3 = ganancia_tp3 * valor_punto * lotaje
        
        # Calcular R:R (Risk-Reward Ratio)
        rr_tp1 = ganancia_usd_tp1 / riesgo_usd if riesgo_usd > 0 else 0
        rr_tp2 = ganancia_usd_tp2 / riesgo_usd if riesgo_usd > 0 else 0
        rr_tp3 = ganancia_usd_tp3 / riesgo_usd if riesgo_usd > 0 else 0
        
        return {
            "lotaje": lotaje,
            "riesgo_usd": round(riesgo_usd, 2),
            "distancia_sl_puntos": round(distancia_sl, 1),
            "valor_punto": valor_punto,
            "ganancia_tp1": round(ganancia_usd_tp1, 2),
            "ganancia_tp2": round(ganancia_usd_tp2, 2),
            "ganancia_tp3": round(ganancia_usd_tp3, 2),
            "rr_tp1": round(rr_tp1, 2),
            "rr_tp2": round(rr_tp2, 2),
            "rr_tp3": round(rr_tp3, 2)
        }
    
    def analizar_mercado(
        self,
        activo: str,
        modo: str,
        capital: float,
        riesgo_porcentaje: float,
        horario_actual: str,
        evento_macro: bool = False,
        descripcion_evento: str = "",
        contexto_adicional: str = ""
    ) -> Dict[str, any]:
        """
        Realiza análisis de mercado completo usando REDI7 IA
        
        Args:
            activo: Símbolo del activo (XAUUSD, BTCUSD, etc.)
            modo: Modo de operativa (SCALPING o INTRADAY)
            capital: Capital total disponible
            riesgo_porcentaje: Porcentaje de riesgo por operación (1-5%)
            horario_actual: Horario actual del análisis
            evento_macro: Si hay evento macroeconómico relevante
            descripcion_evento: Descripción del evento si existe
            contexto_adicional: Información adicional de mercado
            
        Returns:
            Diccionario con el análisis completo
        """
        
        # Validaciones
        if not self.validar_activo(activo):
            return {
                "error": True,
                "mensaje": f"❌ Activo '{activo}' no permitido. Activos válidos: {', '.join(self.ACTIVOS_PERMITIDOS)}"
            }
        
        if not self.validar_modo(modo):
            return {
                "error": True,
                "mensaje": f"❌ Modo '{modo}' no válido. Modos válidos: {', '.join(self.MODOS_OPERATIVA)}"
            }
        
        if not (1 <= riesgo_porcentaje <= 5):
            return {
                "error": True,
                "mensaje": "❌ El riesgo debe estar entre 1% y 5%"
            }
        
        # Construir mensaje del usuario
        mensaje_usuario = f"""
ANÁLISIS SOLICITADO:

Activo: {activo.upper()}
Modo: {modo.upper()}
Horario actual: {horario_actual}
Evento macro: {'SÍ - ' + descripcion_evento if evento_macro else 'NO'}

GESTIÓN DE RIESGO:
Capital total: ${capital:,.2f}
Riesgo por operación: {riesgo_porcentaje}%

{f'CONTEXTO ADICIONAL:{chr(10)}{contexto_adicional}' if contexto_adicional else ''}

Por favor, realiza el análisis completo siguiendo tu protocolo institucional.
"""
        
        try:
            # Llamada a la API
            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": self.PROMPT_MAESTRO},
                    {"role": "user", "content": mensaje_usuario}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            analisis = response.choices[0].message.content
            
            return {
                "error": False,
                "activo": activo.upper(),
                "modo": modo.upper(),
                "capital": capital,
                "riesgo_porcentaje": riesgo_porcentaje,
                "horario": horario_actual,
                "evento_macro": evento_macro,
                "analisis": analisis,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tokens_usados": response.usage.total_tokens
            }
            
        except Exception as e:
            return {
                "error": True,
                "mensaje": f"❌ Error en la API: {str(e)}"
            }
    
    def analizar_con_imagenes(
        self,
        activo: str,
        modo: str,
        capital: float,
        riesgo_porcentaje: float,
        horario_actual: str,
        imagenes_base64: List[str],
        detail_levels: List[str],
        dispositivo: str,
        temporalidades: List[str],
        evento_macro: bool = False,
        descripcion_evento: str = "",
        contexto_adicional: str = "",
        gestionar_riesgo: bool = True
    ) -> Dict[str, any]:
        """
        Realiza análisis con capturas de pantalla de MT5 usando GPT-4 Vision
        
        Args:
            activo: Símbolo del activo
            modo: Modo de operativa
            capital: Capital disponible
            riesgo_porcentaje: Porcentaje de riesgo
            horario_actual: Horario del análisis
            imagenes_base64: Lista de imágenes en formato base64 (2 o 3)
            detail_levels: Niveles de detalle para cada imagen ('low' o 'high')
            dispositivo: Tipo de dispositivo ('PC' o 'MOVIL')
            temporalidades: Lista de temporalidades de cada imagen
            evento_macro: Si hay evento macroeconómico
            descripcion_evento: Descripción del evento
            contexto_adicional: Información adicional
            gestionar_riesgo: Si se debe incluir gestión de riesgo en el análisis
            
        Returns:
            Diccionario con el análisis completo
        """
        
        # Validaciones
        if not self.validar_activo(activo):
            return {
                "error": True,
                "mensaje": f"❌ Activo '{activo}' no permitido. Activos válidos: {', '.join(self.ACTIVOS_PERMITIDOS)}"
            }
        
        if not self.validar_modo(modo):
            return {
                "error": True,
                "mensaje": f"❌ Modo '{modo}' no válido. Modos válidos: {', '.join(self.MODOS_OPERATIVA)}"
            }
        
        if not (1 <= riesgo_porcentaje <= 5):
            return {
                "error": True,
                "mensaje": "❌ El riesgo debe estar entre 1% y 5%"
            }
        
        num_imagenes = len(imagenes_base64)
        if num_imagenes not in [2, 3]:
            return {
                "error": True,
                "mensaje": f"❌ Se requieren 2 o 3 capturas de gráficos según el dispositivo (recibidas: {num_imagenes})"
            }
        
        # Construir mensaje del usuario con contexto
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        # Mensaje base SIEMPRE SIN gestión de riesgo (eso se calcula localmente)
        mensaje_texto = f"""Analiza profesionalmente los gráficos de {activo.upper()} en {modo.upper()} capturados desde {dispositivo}.

CONTEXTO:
Fecha: {fecha_actual} | Hora: {horario_actual}
Temporalidades: {', '.join(temporalidades)} ({num_imagenes} imágenes)

{f'Información adicional: {contexto_adicional}' if contexto_adicional else ''}

INSTRUCCIONES:
1. Identifica el precio actual visible en el gráfico más cercano (última vela)
2. Analiza la estructura de mercado usando Smart Money Concept
3. Localiza zonas de liquidez, order blocks y fair value gaps
4. Determina niveles precisos de entrada, stop loss y take profits
5. Proporciona análisis institucional del movimiento esperado

Lee los precios EXACTOS de los gráficos y proporciona niveles basados en confluencias técnicas.

IMPORTANTE: NO calcules lotaje ni gestión de riesgo. Solo proporciona niveles de precio (Entrada, SL, TP1, TP2, TP3)."""
        
        # Construir contenido del mensaje con imágenes
        content = [
            {
                "type": "text",
                "text": mensaje_texto
            }
        ]
        
        # Agregar las imágenes al contenido con sus niveles de detalle
        for i, (img_base64, detail) in enumerate(zip(imagenes_base64, detail_levels), 1):
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_base64}",
                    "detail": detail  # 'low' o 'high' según configuración
                }
            })
        
        try:
            # Llamada a la API con GPT-4 Vision
            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": self.PROMPT_MAESTRO},
                    {"role": "user", "content": content}
                ],
                temperature=0.7,
                max_tokens=3000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            analisis = response.choices[0].message.content
            
            # Si gestionar_riesgo está activado, calcular localmente
            gestion_riesgo_texto = ""
            if gestionar_riesgo:
                try:
                    # Extraer valores del análisis usando regex
                    import re
                    
                    # Buscar señal (BUY o SELL)
                    match_senal = re.search(r'🚨Señal:\s*(BUY|SELL)', analisis, re.IGNORECASE)
                    direccion = match_senal.group(1).upper() if match_senal else "BUY"
                    
                    # Buscar precios
                    match_entrada = re.search(r'💰Entrada:\s*([\d.,]+)', analisis)
                    match_sl = re.search(r'🚫SL:\s*([\d.,]+)', analisis)
                    match_tp1 = re.search(r'🎯TP1:\s*([\d.,]+)', analisis)
                    match_tp2 = re.search(r'🎯TP2:\s*([\d.,]+)', analisis)
                    match_tp3 = re.search(r'🎯TP3:\s*([\d.,]+)', analisis)
                    
                    if all([match_entrada, match_sl, match_tp1, match_tp2, match_tp3]):
                        entrada = float(match_entrada.group(1).replace(',', ''))
                        stop_loss = float(match_sl.group(1).replace(',', ''))
                        tp1 = float(match_tp1.group(1).replace(',', ''))
                        tp2 = float(match_tp2.group(1).replace(',', ''))
                        tp3 = float(match_tp3.group(1).replace(',', ''))
                        
                        # Calcular gestión de riesgo usando la función local
                        gestion = self.calcular_gestion_riesgo(
                            activo=activo,
                            entrada=entrada,
                            stop_loss=stop_loss,
                            tp1=tp1,
                            tp2=tp2,
                            tp3=tp3,
                            capital=capital,
                            riesgo_porcentaje=riesgo_porcentaje,
                            direccion=direccion
                        )
                        
                        # Construir texto de gestión de riesgo
                        gestion_riesgo_texto = f"""

📉GESTIÓN DE RIESGO REDI7📉
💰 Capital: ${capital:,.2f}
⚠️ Riesgo: {riesgo_porcentaje}%
💵 Dinero en riesgo: ${gestion['riesgo_usd']:,.2f}
📊 Tamaño posición: {gestion['lotaje']} lotes
💎 Ganancia potencial TP1: ${gestion['ganancia_tp1']:,.2f} (R:R {gestion['rr_tp1']})
💎 Ganancia potencial TP2: ${gestion['ganancia_tp2']:,.2f} (R:R {gestion['rr_tp2']})
💎 Ganancia potencial TP3: ${gestion['ganancia_tp3']:,.2f} (R:R {gestion['rr_tp3']})
📈 Ratio Riesgo/Beneficio promedio: {((gestion['rr_tp1'] + gestion['rr_tp2'] + gestion['rr_tp3']) / 3):.2f}

ℹ️ Valor del punto: ${gestion['valor_punto']} | Distancia SL: {gestion['distancia_sl_puntos']} puntos"""
                        
                        # Agregar al análisis
                        analisis += gestion_riesgo_texto
                        
                except Exception as e:
                    print(f"Error calculando gestión de riesgo: {e}")
                    # Si falla, continuar sin gestión de riesgo
            
            return {
                "error": False,
                "activo": activo.upper(),
                "modo": modo.upper(),
                "capital": capital,
                "riesgo_porcentaje": riesgo_porcentaje,
                "horario": horario_actual,
                "evento_macro": evento_macro,
                "analisis": analisis,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tokens_usados": response.usage.total_tokens,
                "con_imagenes": True
            }
            
        except Exception as e:
            return {
                "error": True,
                "mensaje": f"❌ Error en la API: {str(e)}"
            }


def main():
    """Función principal para pruebas"""
    
    print("=" * 60)
    print("🧠 REDI7 IA v1.0 - Sistema de Análisis Institucional")
    print("=" * 60)
    print()
    
    # Configuración
    API_KEY = os.getenv("OPENAI_API_KEY", "tu-api-key-aqui")
    
    if API_KEY == "tu-api-key-aqui":
        print("⚠️  IMPORTANTE: Configura tu OPENAI_API_KEY en las variables de entorno")
        print("   o edita el archivo config.py")
        print()
        print("   Instrucciones:")
        print("   1. Obtén tu API Key en: https://platform.openai.com/api-keys")
        print("   2. Windows: set OPENAI_API_KEY=tu-clave-aqui")
        print("   3. Linux/Mac: export OPENAI_API_KEY=tu-clave-aqui")
        print()
        return
    
    # Inicializar sistema
    redi7 = REDI7AI(api_key=API_KEY)
    
    # Ejemplo de uso
    print("📊 EJEMPLO DE ANÁLISIS:")
    print("-" * 60)
    
    resultado = redi7.analizar_mercado(
        activo="XAUUSD",
        modo="SCALPING",
        capital=10000.0,
        riesgo_porcentaje=2.0,
        horario_actual="14:30 EST (Sesión NY Activa)",
        evento_macro=False,
        contexto_adicional="Mercado en rango, última vela muestra rechazo en zona de resistencia"
    )
    
    if resultado["error"]:
        print(f"\n❌ {resultado['mensaje']}\n")
    else:
        print(f"\n✅ Análisis completado - {resultado['timestamp']}")
        print(f"📈 Activo: {resultado['activo']} | Modo: {resultado['modo']}")
        print(f"💰 Capital: ${resultado['capital']:,.2f} | Riesgo: {resultado['riesgo_porcentaje']}%")
        print(f"🔢 Tokens usados: {resultado['tokens_usados']}")
        print("\n" + "=" * 60)
        print(resultado['analisis'])
        print("=" * 60)


if __name__ == "__main__":
    main()
